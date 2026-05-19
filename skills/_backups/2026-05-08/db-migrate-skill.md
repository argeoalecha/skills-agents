---
name: db-migrate
description: Safe database migration workflow for Supabase PostgreSQL databases. Use this skill when creating, reviewing, or applying database migrations. Triggers on requests like "create a migration", "add a table", "modify the database schema", "migrate the database", or any database structure changes. Combines multiple specialized agents (database-architect, security-code-reviewer, Explore) to ensure migrations are safe, secure, and follow established patterns.
---

# Database Migration Workflow

## Overview

Safe, reversible migration workflow for Supabase PostgreSQL. Every migration is reviewed for security (RLS, injection risks), tested locally before applying to production, and documented.

---

## Step 1 — Plan the Migration

Identify what schema change is needed:
- New table
- Add/remove/modify columns
- Add/remove indexes
- Add/remove RLS policies
- Add foreign key constraints
- Drop table (rare — prefer soft deletes)

Spawn the **database-architect** agent to design the schema and RLS policies before writing any SQL:
- What columns does the table need?
- What are the data types and constraints?
- What RLS policies enforce multi-tenant isolation?
- Does this change require a backfill for existing rows?
- Is the migration reversible without data loss?

---

## Step 2 — Create the Migration File

```bash
# Generate timestamp
TIMESTAMP=$(date -u +"%Y%m%d%H%M%S")

# Create migration file
touch supabase/migrations/${TIMESTAMP}_<description>.sql
```

Naming convention: `YYYYMMDDHHMMSS_verb_noun.sql`
- `20260507120000_create_bookings_table.sql`
- `20260507120001_add_status_to_trips.sql`
- `20260507120002_add_idx_bookings_user_id.sql`

---

## Step 3 — Write the Migration SQL

### New table template

```sql
-- supabase/migrations/YYYYMMDDHHMMSS_create_<table>.sql

-- Create table
CREATE TABLE public.<table_name> (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  -- business columns
  name        TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
  metadata    JSONB,
  -- audit trail (always include)
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at  TIMESTAMPTZ
);

-- Index on user_id (RLS will use this)
CREATE INDEX idx_<table_name>_user_id ON public.<table_name>(user_id);

-- Index on common query patterns
CREATE INDEX idx_<table_name>_created_at ON public.<table_name>(created_at DESC);
CREATE INDEX idx_<table_name>_status ON public.<table_name>(status) WHERE deleted_at IS NULL;

-- Enable Row Level Security (mandatory)
ALTER TABLE public.<table_name> ENABLE ROW LEVEL SECURITY;

-- RLS: users see only their own rows
CREATE POLICY "<table_name>_select_own"
  ON public.<table_name> FOR SELECT
  USING (auth.uid() = user_id AND deleted_at IS NULL);

CREATE POLICY "<table_name>_insert_own"
  ON public.<table_name> FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "<table_name>_update_own"
  ON public.<table_name> FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "<table_name>_delete_own"
  ON public.<table_name> FOR DELETE
  USING (auth.uid() = user_id);

-- updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON public.<table_name>
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Add column template

```sql
-- supabase/migrations/YYYYMMDDHHMMSS_add_<column>_to_<table>.sql

ALTER TABLE public.<table_name>
  ADD COLUMN <column_name> <type> [NOT NULL] [DEFAULT <value>];

-- Add index if this column will be filtered/sorted frequently
CREATE INDEX idx_<table_name>_<column_name> ON public.<table_name>(<column_name>);
```

### Rollback comment

Every migration must include a rollback comment at the bottom:

```sql
-- ROLLBACK (run manually if needed):
-- DROP TABLE public.<table_name> CASCADE;
-- or: ALTER TABLE public.<table_name> DROP COLUMN <column_name>;
```

---

## Step 4 — Security Review

Spawn a **security-code-reviewer** sub-agent to check the migration SQL for:
- Missing `ENABLE ROW LEVEL SECURITY` on any new table
- RLS policies that might allow cross-tenant data access
- Missing `auth.uid()` checks in policies
- Overly permissive policies (`USING (true)` on sensitive tables)
- Indexes on sensitive PII columns that could be exploited
- Missing cascade behavior on foreign keys

Fix any findings before proceeding.

---

## Step 5 — Test Locally

```bash
# Start Supabase local dev
supabase start

# Apply the migration
supabase db reset   # clean slate, applies all migrations from scratch
# or: supabase migration up  # apply only pending migrations

# Verify the table/column exists
supabase db diff

# Run any DB-dependent tests
npx vitest run --reporter=verbose
```

---

## Step 6 — Apply to Production

Only after local tests pass:

```bash
# Link to the production project (first time only)
supabase link --project-ref <project-ref>

# Push migration to production
supabase db push

# Verify in Supabase dashboard
# Table Editor → confirm table and policies exist
```

---

## Rules

- Never use the Supabase dashboard to make schema changes — always use migration files so the change is versioned
- Every table must have RLS enabled — no exceptions
- Soft deletes (`deleted_at`) preferred over hard deletes for user-facing tables
- Always include `created_at`, `updated_at`, `user_id` on business tables
- Test migrations with `supabase db reset` locally before pushing to production
- Never edit an existing migration that has been applied to production — create a new one
- Destructive migrations (DROP TABLE, DROP COLUMN) require explicit user confirmation before proceeding
