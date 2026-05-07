---
name: prd-tdd-writer
description: Create Product Requirements Documents (PRDs) and Technical Design Documents (TDDs) for software and AI/automation projects. Use this skill whenever the user wants to spec out a product, plan a feature, document architecture, or define system behavior. Trigger on phrases like "write a PRD", "create a TDD", "spec this out", "document this feature", "let's plan the system", "design doc", "spec doc", "system design", or when the user describes an app or agent they want to build and needs formal documentation.
---

# PRD & TDD Writer — Hayah-AI Services

A skill for producing lean, professional PRDs and TDDs for web apps, AI agents, automation systems, and data products.

---

## Workflow

1. **Identify doc type**: PRD (what + why) or TDD (how). Often both are needed.
2. **Extract context** from the conversation — don't ask for things already described.
3. **Fill gaps** by asking only what's missing (1–3 targeted questions max). Ask all missing questions in a **single block** before drafting. Never ask follow-ups mid-draft.
4. **Draft document** using the templates below.
5. **Offer follow-up**: companion doc, architecture diagram, task breakdown (`/plan-todo`).
6. **Output**: Render the document as clean Markdown. Offer to save as a `.md` file if the user is in a project context.

---

## PRD Template

```markdown
# Product Requirements Document
**Product:** <name>
**Author:** <name>
**Date:** YYYY-MM-DD
**Status:** Draft | Review | Approved

---

## 1. Problem Statement
<2–3 sentences on the problem being solved and who it affects>

## 2. Goals
- <measurable goal 1>
- <measurable goal 2>

## 3. Non-Goals (out of scope)
- <explicit exclusion 1>
- <explicit exclusion 2>

## 4. User Personas
| Persona | Description | Primary Need |
|---|---|---|
| <name> | <who they are> | <what they need from this product> |

## 5. User Stories / Requirements

### Must Have (MVP)
- [ ] As a <persona>, I can <action> so that <benefit>
- [ ] ...

### Should Have (V1+)
- [ ] ...

### Nice to Have (future)
- [ ] ...

## 6. Success Metrics
| Metric | Target | How Measured |
|---|---|---|
| <metric> | <value> | <method> |

## 7. Constraints
- **Budget:** <if relevant>
- **Timeline:** <if relevant>
- **Technical:** <limitations>
- **Regulatory:** Philippines DPA compliance required / not required

## 8. Open Questions
- <question that needs an answer before building>
```

---

## TDD Template

```markdown
# Technical Design Document
**Feature/System:** <name>
**Author:** <name>
**Date:** YYYY-MM-DD
**Status:** Draft | Review | Approved
**Related PRD:** [link or "see PRD above"]

---

## 1. Overview
<2–3 sentence technical summary of what this builds and how>

## 2. Architecture

### System Diagram
<ASCII diagram or description of how components interact>

### Tech Stack
| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 14 App Router + TypeScript | <reason> |
| Styling | Tailwind CSS + shadcn/ui | <reason> |
| Backend | Next.js API Routes | <reason> |
| Database | Supabase (PostgreSQL) | <reason> |
| Auth | Supabase Auth | <reason> |
| AI | Claude API (claude-sonnet-4-6) | <reason> |
| Deployment | Vercel | <reason> |

## 3. Database Schema

### Tables

#### `<table_name>`
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | |
| user_id | UUID | NOT NULL REFERENCES auth.users(id) | |
| <column> | <type> | <constraints> | <description> |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | | Soft delete |

### RLS Policies
```sql
-- <table>: users see only their own rows
CREATE POLICY "<table>_own" ON <table>
  USING (auth.uid() = user_id);
```

## 4. API Design

### Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/<resource> | Required | List user's resources |
| POST | /api/<resource> | Required | Create resource |
| GET | /api/<resource>/[id] | Required | Get single resource |
| PATCH | /api/<resource>/[id] | Required | Update resource |
| DELETE | /api/<resource>/[id] | Required | Soft delete resource |

### Request/Response Shapes

#### POST /api/<resource>
```typescript
// Request body
interface CreateRequest {
  name: string
  // ...
}

// Success response (201)
interface ResourceResponse {
  id: string
  name: string
  created_at: string
}

// Error response (4xx/5xx)
interface ErrorResponse {
  error: string
  code: string
  details?: unknown
}
```

## 5. Frontend Structure

```
app/
├── (auth)/
│   ├── login/page.tsx
│   └── signup/page.tsx
├── dashboard/
│   ├── layout.tsx          # Protected layout
│   └── page.tsx
└── api/
    └── <resource>/
        └── route.ts
components/
├── <feature>/
│   ├── <Component>.tsx
│   └── index.ts
lib/
├── supabase/
│   ├── client.ts
│   └── server.ts
└── validations/
    └── <resource>.ts
```

## 6. Key Technical Decisions

| Decision | Choice | Rationale | Trade-off |
|---|---|---|---|
| <decision> | <what was chosen> | <why> | <what was given up> |

## 7. Security Considerations
- Auth: <how auth is enforced>
- RLS: <which tables have RLS and the policy logic>
- Input validation: <Zod schemas on all inputs>
- PII: <what personal data is handled and how>
- Philippines DPA: <consent mechanism, data rights endpoints>

## 8. Performance Considerations
- Caching: <what is cached and for how long>
- Pagination: <how list endpoints paginate>
- N+1 queries: <how joins are structured to avoid N+1>

## 9. Testing Strategy
- Unit tests: <what is unit tested>
- Integration tests: <what is integration tested>
- E2E tests: <critical user journeys covered by Playwright>

## 10. Deployment
- Environment: Vercel (preview + production)
- Migrations: `supabase db push` before app deploy
- Env vars: <list of required vars without values>

## 11. Open Questions
- <technical question that needs resolution>
```

---

## Philippines Market Notes

When the project targets the Philippines market, add to PRD constraints and TDD:
- Currency: Philippine Peso (₱), format as `₱1,234.00`
- Address structure: Barangay → Municipality → Province → Region
- Primary payment: COD, GCash, Maya, bank transfer
- DPA compliance required (RA 10173) — add consent mechanism and data rights endpoints
- Optimize for mobile-first, slower connections (target Core Web Vitals on 4G)
