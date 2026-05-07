---
name: e2e-test
description: Comprehensive end-to-end testing command. Launches parallel sub-agents to research the codebase (structure, database schema, potential bugs), then uses the agent-browser CLI to test every user journey — taking screenshots, validating UI/UX, and querying the database to verify records. Run after implementation to validate everything before code review.
---

# End-to-End Application Testing

## Pre-flight Check

Before starting, confirm:

```bash
# Check if dev server is already running
lsof -i :3000 | head -3
# or check for other common ports: 3001, 5173, 8000

# If not running, start it (background)
npm run dev &
# or: pnpm dev & / bun dev &

# Wait for it to be ready
until curl -s http://localhost:3000 > /dev/null; do sleep 1; done
echo "Server ready"
```

---

## Phase 1 — Parallel Research (3 sub-agents)

Spawn these three sub-agents simultaneously before starting any browser tests:

### Sub-Agent A: Codebase Explorer
Using the `Explore` agent, map:
- All routes/pages in the app
- API endpoints (list GET endpoints, mutation POST/PATCH/DELETE endpoints)
- Database tables and their relationships
- Auth flow (how login/logout works)
- Key user flows the feature supports

### Sub-Agent B: Bug Spotter
Using the `general-purpose` agent, scan for:
- Any TypeScript errors (`npx tsc --noEmit`)
- Components that might have rendering issues (conditional rendering, missing null checks)
- API routes that don't validate input
- Database queries that could return unexpected results

### Sub-Agent C: Test Planner
Based on the feature that was implemented, generate:
- List of user journeys to test (happy path + edge cases)
- Expected database state after each write operation
- Screenshots to take at each step

---

## Phase 2 — Browser Testing

After research completes, run browser tests using `agent-browser`. Follow `/agent-browser` skill conventions.

### Standard test sequence for any feature

```bash
# 1. Start at the app entry point
agent-browser open http://localhost:3000
agent-browser screenshot   # document initial state

# 2. Test unauthenticated access (should redirect to login)
agent-browser open http://localhost:3000/dashboard
agent-browser screenshot   # should see login page, not dashboard

# 3. Log in with test credentials
agent-browser open http://localhost:3000/login
agent-browser snapshot -i
agent-browser fill @e1 "test@example.com"
agent-browser fill @e2 "testpassword"
agent-browser click @e3
agent-browser wait --url "/dashboard"
agent-browser screenshot   # logged in dashboard state

# 4. Test the feature's happy path
# (varies by feature — follow the test plan from Phase 1)

# 5. Test edge cases / error states
# - Empty form submission
# - Invalid input
# - Missing required fields

# 6. Test navigation and back-button behavior

# 7. Log out and verify session cleared
```

### Screenshots to always capture

| Moment | Why |
|---|---|
| Initial page load | Confirm no visual regressions |
| After login | Confirm auth works |
| After successful form submission | Confirm success state |
| After failed validation | Confirm error messages appear |
| After delete/remove | Confirm item is gone |
| After logout | Confirm redirect to login |

---

## Phase 3 — Database Verification

After browser actions that write data, verify the database was updated correctly:

```bash
# Check Supabase local dev (if running)
supabase db dump --local | grep -A5 "table_name"

# Or use psql directly
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "SELECT * FROM <table_name> ORDER BY created_at DESC LIMIT 5;"

# Or run a test query via Supabase client in a script
```

Verify:
- Record was created with correct data
- `user_id` is set to the authenticated user's ID
- `created_at` and `updated_at` are populated
- RLS didn't block the insert (no null result when one is expected)

---

## Phase 4 — Report

Produce a structured test report:

```markdown
## E2E Test Report — <Feature Name>
Date: YYYY-MM-DD
Branch: <branch>

### Test Environment
- App: http://localhost:3000
- DB: local Supabase / production (specify)

### User Journeys Tested

| Journey | Result | Notes |
|---|---|---|
| Unauthenticated redirect | PASS | Redirects to /login correctly |
| Login with valid credentials | PASS | Redirects to /dashboard |
| Create <resource> — happy path | PASS | Record visible in DB |
| Create <resource> — validation | PASS | Errors shown for empty fields |
| Delete <resource> | PASS | Soft-deleted (deleted_at set) |
| Logout | PASS | Session cleared, /login redirect |

### Screenshots Taken
- `screenshots/01-initial.png`
- `screenshots/02-login.png`
- ...

### Issues Found
- [BUG] <description> — <reproduction steps>
- [UI] <description> — <screenshot reference>

### Overall Result: PASS / FAIL
```

---

## Rules

- Never test against production unless the user explicitly asks
- Take screenshots before and after every significant interaction
- If a test step fails, take a screenshot of the failure state before stopping
- Verify database state after any write operation — don't trust the UI alone
- If the dev server isn't running, start it before testing (never skip this)
