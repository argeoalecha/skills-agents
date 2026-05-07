---
name: plan-todo
description: Generate or refresh a codebase-aware TODO list from the project's PRD and TDD. Works at any stage — first run (no TODO.md yet), mid-development refresh, or in-session progress check. Use when the user says "plan my todos", "what should I work on next", "generate a task list from the PRD", "refresh my TODO", "check my progress", "how am I doing vs the PRD", "what's left to build", or "show me what's done". Does NOT create PRDs or TDDs — use /prd-tdd-writer for that. Does NOT implement code — use /feature-dev for that.
---

# Plan → TODO Skill

Reads the project's PRD and TDD, cross-references the current codebase and any existing TODO.md, and produces an ordered, phase-grouped TODO list. Works at every stage of development — first planning session, mid-implementation refresh, or in-session progress review.

---

## Where This Skill Fits

| Skill / Agent | What It Does | When to Use |
|---|---|---|
| `product-planner` agent | Creates a plan and PRD from a vague idea | Before docs exist |
| `/prd-tdd-writer` | Writes formal PRD and TDD documents | To spec something out |
| **`/plan-todo`** | **Reads PRD + TDD → ordered, refreshable TODO list** | **Any stage of development** |
| `/feature-dev` | Executes the full build lifecycle | Implementing a specific feature |
| `/checkpoint` | Saves session state for resuming | End of session |

---

## Step 1 — Locate Source Documents

```bash
# Look for PRD and TDD in common locations
find . -name "PRD.md" -o -name "TDD.md" -o -name "prd.md" -o -name "tdd.md" \
  -o -name "*requirements*.md" -o -name "*technical-design*.md" 2>/dev/null | head -10

# Check for existing TODO
ls TODO.md 2>/dev/null && echo "TODO.md found" || echo "No TODO.md yet"

# Check for checkpoint
ls SESSION_CHECKPOINT.md 2>/dev/null && echo "Checkpoint found"
```

If PRD or TDD don't exist, tell the user to run `/prd-tdd-writer` first.

---

## Step 2 — Read Project State

In parallel, read:
1. PRD — extract phases, features, acceptance criteria
2. TDD — extract components, API routes, database schema, technical decisions
3. Codebase structure — what files and folders exist
4. Existing TODO.md — what's already marked done or in progress
5. Git log — `git log --oneline -20` to see what was recently committed

```bash
# Quick codebase scan
find src -type f -name "*.ts" -o -name "*.tsx" | sort
find app -type f -name "*.ts" -o -name "*.tsx" | sort 2>/dev/null
ls supabase/migrations/ 2>/dev/null | sort
```

---

## Step 3 — Determine Status of Each PRD Item

For each feature or requirement in the PRD:
- **DONE** if: file exists, component renders, API route works, migration applied
- **IN PROGRESS** if: file exists but incomplete, tests missing, or partially wired up
- **TODO** if: no corresponding code found in the codebase
- **BLOCKED** if: depends on an incomplete item

Be specific — checking `app/api/trips/route.ts` exists is not enough. Check that the required endpoints (GET, POST) are implemented with proper auth and validation.

---

## Step 4 — Generate TODO.md

Write `TODO.md` at the project root:

```markdown
# TODO — <Project Name>
Generated: YYYY-MM-DD | Based on: PRD v<x>, TDD v<x>

## Progress: N/M tasks complete (X%)

---

## Phase 1: Foundation
- [x] Initialize Next.js project with TypeScript strict
- [x] Set up Supabase project and local dev
- [x] Configure Tailwind CSS + shadcn/ui
- [ ] Configure Sentry (client + server)

## Phase 2: Database Schema
- [x] Create users/profiles migration
- [x] Create trips table with RLS
- [ ] Add bookings table — migration needed
- [ ] Add indexes for common query patterns

## Phase 3: API Layer
- [x] GET /api/trips — list user's trips
- [x] POST /api/trips — create trip
- [ ] PATCH /api/trips/[id] — update trip
- [ ] DELETE /api/trips/[id] — soft delete

## Phase 4: Frontend
- [x] Login page
- [x] Dashboard layout
- [ ] Trip creation form — validation needed
- [ ] Trip detail page

## Phase 5: Testing
- [ ] Unit tests for API routes
- [ ] E2E tests for trip creation flow

## Phase 6: Deployment
- [ ] Configure Vercel project
- [ ] Set production environment variables
- [ ] Deploy to production

---

## Blocked
- Bookings table (Phase 2) — waiting on trips table to be finalized

## Next Action
<single most important thing to do right now>
```

---

## Step 5 — Recommend Next Action

After generating the TODO list, state clearly:

```
Next action: <specific task from the TODO list>
Why: <one sentence on why this is the priority>
Skill to use: /feature-dev | /db-migrate | /api-new | /audit | ...
```

---

## Rules

- Never mark something DONE without finding the corresponding code
- Phase order matters — flag any out-of-order work (e.g. frontend built before the API)
- If TODO.md already exists, diff it against the PRD rather than replacing it wholesale — preserve any manual notes the user added
- The "Next Action" must be a single actionable item, not a vague direction
- If more than 50% of the PRD is unimplemented, offer to run `/feature-dev` on the highest-priority incomplete phase
