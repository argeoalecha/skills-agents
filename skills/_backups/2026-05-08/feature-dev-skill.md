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
5. **Code Review** — Get feedback and approval
6. **Documentation** — Document the feature
7. **Deployment** — Ship to production

---

## Phase 1 — Requirements Gathering

Before writing any code, clarify:

**Functional requirements:**
- What user action triggers this feature?
- What does the feature do? What's the output or outcome?
- What are the edge cases and failure modes?
- Who uses this? (authenticated user, admin, public)
- What is the acceptance criterion? (how do we know it's done?)

**Non-functional requirements:**
- Performance: how fast must it respond?
- Scale: how many concurrent users / records?
- Security: what data does it handle? (PII, payments?)
- Compliance: Philippines DPA relevant? Payment regulations?

**Resources:** Read `references/architecture-workflow.md` for workspace-wide patterns.

---

## Phase 2 — Architecture Design

Use the **Plan** sub-agent to design before implementing.

Produce an Architecture Decision Record (ADR) using `assets/adr-template.md`. Cover:

**Database:**
- New tables? Use `/db-migrate` skill
- New columns? Add migration
- RLS policies? Define them before implementing routes

**API:**
- New endpoints? Use `/api-new` skill
- Which HTTP methods?
- Request/response shape (Zod schema)
- Auth requirements
- Rate limiting needed?

**Frontend:**
- New pages or components?
- Server Component vs Client Component?
- State management: Zustand store or TanStack Query?
- Form: React Hook Form + Zod?

**Reference patterns:** `references/fullstack-patterns.md`

**Checkpoint:** Present the plan to the user and get approval before implementing.

---

## Phase 3 — Implementation

Follow this order — back-end before front-end:

### 3a. Database migrations
```bash
# Create and apply migration first
# Reference: /db-migrate skill
```

### 3b. API routes
```bash
# Scaffold and implement routes
# Reference: /api-new skill
```

### 3c. Frontend components and pages
- Server Components for data fetching (avoid unnecessary client boundaries)
- Client Components only when interactivity is required (`'use client'`)
- React Hook Form + Zod for all forms
- TanStack Query for client-side data fetching and cache invalidation

### 3d. Apply Hayah-AI theme
- Use the project's established design tokens
- Reference: `/theme-hayahai` skill for design system
- Lucide React for icons
- No custom icons, no emoji in UI

**Reference patterns:** `references/fullstack-patterns.md`, `references/cicd-pipeline.md`

---

## Phase 4 — Testing

**Unit/component tests (Vitest + RTL):**
- Test each new API route handler
- Test form validation logic
- Test component rendering for key states (loading, error, empty, populated)

**Integration tests:**
- Test the full request → database → response cycle for critical paths
- Validate RLS policies work as expected

**E2E (optional but recommended for complex features):**
```bash
/e2e-test
```

**Run tests before moving to review:**
```bash
npx vitest run
npx tsc --noEmit
npx eslint . --ext .ts,.tsx
```

Reference: `references/testing-strategy.md`

---

## Phase 5 — Code Review

Self-review checklist before presenting to user:

**Security:**
- [ ] All inputs validated with Zod at the API boundary
- [ ] Auth check present on all protected routes
- [ ] No secrets in code
- [ ] RLS policies cover all operations (SELECT, INSERT, UPDATE, DELETE)
- [ ] No `any` TypeScript types

**Reliability:**
- [ ] All promises awaited or handled
- [ ] Error states rendered in UI
- [ ] Database errors caught and returned as standardized error response

**Code quality:**
- [ ] No unused imports or dead code
- [ ] File structure matches project conventions
- [ ] No unnecessary comments

Reference: `references/code-review-checklist.md`

For a deeper review, spawn the `security-code-reviewer` sub-agent.

**Checkpoint:** Present the implementation to the user for review and approval before documenting or deploying.

---

## Phase 6 — Documentation

- Update `README.md` if this feature changes the project setup or API surface
- If a significant architectural decision was made, save the ADR to `docs/decisions/`
- Update API docs if the project has an OpenAPI spec

Use `assets/pr-template.md` when creating a PR.

---

## Phase 7 — Deployment

```bash
# Run the deployment check script
bash scripts/check_deployment.sh

# Validate migrations are applied
bash scripts/validate_migration.sh

# Deploy
/vercel:deploy       # Vercel deployment
/netlify-deploy      # Netlify deployment
```

Reference: `references/cicd-pipeline.md`

**Post-deploy verification:**
- Check that the feature works in the deployed environment
- Monitor Sentry for any new errors in the first 10 minutes
- Confirm database migrations applied correctly in production

---

## Feature Spec Template

Before implementing complex features, fill out `assets/feature-spec-template.md` and confirm with the user. This prevents scope creep and misunderstandings.
