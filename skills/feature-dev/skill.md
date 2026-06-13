---
name: feature-dev
description: Guided workflow for full-stack feature development across any project in the workspace. Use this skill when building new features (seller dashboard, contact system, CRM module, AI agent, etc.), implementing full-stack functionality, or making infrastructure/DevOps changes. Triggers on requests like "build a feature for", "implement", "add a module", "develop new feature", or "create full-stack feature". Provides structured guidance through requirements, architecture, implementation, testing, code review, and deployment with approval checkpoints.
---

# Feature Development Workflow

Guided workflow for developing production-ready features from concept to deployment.

## Workflow Overview

This skill guides you through 7 phases:

1. **Requirements Gathering** — Understand what to build
2. **Architecture Design** — Plan the technical approach
3. **Implementation** — Write the code
4. **Testing** — Ensure quality and correctness
5. **Code Review** — Self-review against quality gates
6. **Documentation** — Document significant decisions
7. **Deployment** — Ship to production

---

## Phase 1 — Requirements Gathering

Before writing any code:

**Read context first:**
- Read the project-level `CLAUDE.md` for conventions, stack decisions, and patterns
- Read `references/architecture-workflow.md` for workspace-wide patterns
- If a `TODO.md` or `PRD.md` exists, read it to understand the feature's place in the roadmap

**Clarify functional requirements:**
- What user action triggers this feature?
- What does the feature do? What is the output or outcome?
- What are the edge cases and failure modes?
- Who uses this? (authenticated user, admin, public)
- What is the acceptance criterion — how do we know it is done?

**Clarify non-functional requirements:**
- Performance: how fast must it respond?
- Scale: how many concurrent users / records?
- Security: what data does it handle? (PII, payments?)
- Compliance: Philippines DPA relevant? Payment regulations?

For complex features where scope needs formal alignment, use `/prd-tdd-writer` to produce a spec before proceeding.

---

## Phase 2 — Architecture Design

Use the **Plan** sub-agent to design before implementing.

Produce an Architecture Decision Record (ADR) using `assets/adr-template.md` for any decision that:
- Affects multiple layers (DB + API + frontend)
- Introduces a new dependency or external service
- Changes the data model significantly
- Establishes a pattern others will follow

**Database:**
- New tables? Use `/db-migrate` skill
- New columns? Add migration with rollback SQL
- RLS policies? Define them before implementing routes

**API:**
- New endpoints? Use `/api-new` skill
- HTTP methods, request/response shape (Zod schema)
- Auth requirements, rate limiting

**Frontend:**
- New pages or components?
- Server Component vs Client Component?
- State management: Zustand store or TanStack Query?
- Form: React Hook Form + Zod?

**Reference patterns:** `references/fullstack-patterns.md`

**Checkpoint:** Present the architecture plan to the user and get explicit approval before writing any code.

---

## Phase 3 — Implementation

Follow this order — database before API, API before frontend.

### 3a. Read before writing

Before touching any file, read the relevant existing code:
- Existing API routes in the same domain
- Existing components for similar UI patterns
- Existing DB schema for related tables

This prevents diverging from established patterns.

### 3b. Database migrations

Use `/db-migrate` skill to create and apply the migration. Verify RLS policies are in place before proceeding.

### 3c. API routes

Use `/api-new` skill to scaffold routes. Every route must:
- Validate the request body with Zod before any processing
- Check auth before touching data
- Return `{ error: string, code?: string }` on failure
- Return consistent HTTP status codes

### 3d. Frontend components and pages

- Server Components for data fetching (avoid unnecessary client boundaries)
- `'use client'` only when interactivity, hooks, or browser APIs are required
- React Hook Form + Zod for all forms
- TanStack Query for client-side data fetching and cache invalidation
- Lucide React for icons

### 3e. Apply design system

Use the Hayah-AI Ocean-Teal theme tokens from the project's Tailwind config. Run `/theme-hayahai` if you need to set up or verify the theme. No hardcoded colors.

**Reference patterns:** `references/fullstack-patterns.md`, `references/cicd-pipeline.md`

### 3f. Simplify

After implementation is complete, run `/simplify` to catch reuse opportunities, dead code, and quality issues before testing.

---

## Phase 4 — Testing

**Unit/component tests (Vitest + RTL):**
- Test each new API route handler
- Test form validation logic
- Test component rendering for key states: loading, error, empty, populated

**Integration tests:**
- Test the full request → database → response cycle for critical paths
- Validate RLS policies enforce access correctly

**E2E — two tools, two purposes:**

| Tool | When to use | What it produces |
|---|---|---|
| `/e2e-playwright` | Write regression tests for the feature — committed to the repo, run in CI | `e2e/*.spec.ts` files |
| `/e2e-test` | Interactive exploratory pass before code review — one-time validation | `E2E_TEST.md` report + screenshots |

For every user-facing feature, do both:
1. Run `/e2e-playwright` to write the Playwright spec covering the feature's critical journeys. Every feature must have at least one tier-2 (feature-level) test — not just a smoke test.
2. Run `/e2e-test` for the interactive browser pass to catch UX issues that code alone misses.

**Run the quality gates before review:**
```bash
pnpm build                    # Must pass — catches type errors and import issues
pnpm typecheck                # npx tsc --noEmit if no typecheck script
pnpm lint                     # ESLint
pnpm test                     # Vitest unit tests
npx playwright test           # Playwright E2E suite
```

Reference: `references/testing-strategy.md`, `/e2e-playwright` skill

---

## Phase 5 — Code Review

Self-review checklist before presenting to user:

**Security:**
- [ ] All inputs validated with Zod at the API boundary
- [ ] Auth check present on all protected routes
- [ ] No secrets in code
- [ ] RLS policies cover SELECT, INSERT, UPDATE, DELETE
- [ ] No `any` TypeScript types

**Reliability:**
- [ ] All promises awaited or handled
- [ ] Error states rendered in UI
- [ ] Database errors caught and returned as standardized error response

**Code quality:**
- [ ] No unused imports or dead code
- [ ] File structure matches project conventions from CLAUDE.md
- [ ] No unnecessary comments

Reference: `references/code-review-checklist.md`

For a deeper review, use the `/security-review` skill or `/code-review:code-review` skill.

**Checkpoint:** Present the implementation to the user for review and approval before documenting or deploying.

---

## Phase 6 — Documentation

- Update `README.md` if this feature changes the project setup or API surface
- If a significant architectural decision was made, save the ADR to `docs/decisions/`
- Update `CLAUDE.md` (project-level) if the feature establishes a new pattern other features should follow
- Update API docs if the project has an OpenAPI spec

Use `assets/pr-template.md` when creating a PR.

---

## Phase 7 — Deployment

**Pre-deployment audit:**
```bash
/audit
```

The audit skill runs build validation, static analysis, and a production-readiness gate. It must pass (or all blockers resolved) before deploying.

**Deployment validation:**
```bash
bash scripts/check_deployment.sh    # Env vars, secrets, git state
bash scripts/validate_migration.sh  # Migrations applied
```

**Commit and push:**
```bash
/commit-push
```

**Deploy:**
```bash
/vercel:deploy      # Vercel deployment
/netlify-deploy     # Netlify deployment
```

Reference: `references/cicd-pipeline.md`

**Post-deploy verification:**
- Manually verify the feature works in the deployed environment
- Monitor Sentry for new errors in the first 10 minutes
- Confirm database migrations applied correctly in production

---

## Feature Spec Template

Before implementing complex features, fill out `assets/feature-spec-template.md` and confirm with the user. This prevents scope creep and misunderstandings.
