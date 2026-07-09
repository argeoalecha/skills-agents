---
name: plan-todo
description: Generate or refresh a codebase-aware TODO list from the project's PRD and TDD. Works at any stage — first run (no TODO.md yet), mid-development refresh, or in-session progress check. Adapts phase structure based on project type (web app vs. AI agent/automation). Use when the user says "plan my todos", "what should I work on next", "generate a task list from the PRD", "refresh my TODO", "check my progress", "how am I doing vs the PRD", "what's left to build", or "show me what's done". Does NOT create PRDs or TDDs — use /prd-tdd-writer for that. Does NOT implement code — use /feature-dev for that.
---

# Plan → TODO Skill

Reads the project's PRD and TDD, cross-references the current codebase and any existing TODO.md, and produces an ordered, phase-grouped TODO list. Works at every stage of development — first planning session, mid-implementation refresh, or in-session progress review.

---

## Where This Skill Fits

| Skill / Agent | What It Does | When to Use |
|---|---|---|
| `/brainstorm-ideas` | Diverge/converge ideation; ranks options (ICE/RICE/2×2) | Before docs exist, or to re-rank backlog scope |
| `product-planner` (built-in agent) | Creates a plan and PRD from a vague idea | Before docs exist |
| `/prd-tdd-writer` | Writes or reviews formal PRD and TDD documents | To spec or critique |
| **`/plan-todo`** | **Reads PRD + TDD → ordered, refreshable TODO list** | **Any stage of development** |
| `/ui-builder` | Locks theme, logo + tagline, component conventions | Phase 1 Foundation — web app projects only |
| `/feature-dev` | Executes the full build lifecycle for a feature | Implementing a specific feature |
| `/checkpoint` | Saves session state for resuming | End of session |

---

## Step 1 — Locate Source Documents

```bash
# Check docs/ directory first (prd-tdd-writer default save location)
find . -path "*/docs/*.md" | sort 2>/dev/null | head -10

# Then check project root and common names
find . -maxdepth 2 \( \
  -name "PRD.md" -o -name "TDD.md" -o \
  -name "prd.md" -o -name "tdd.md" -o \
  -name "*requirements*.md" -o -name "*technical-design*.md" \
\) 2>/dev/null | head -10

# Check for existing TODO
ls TODO.md 2>/dev/null && echo "TODO.md found" || echo "No TODO.md yet"
```

**If PRD or TDD are missing:**
- PRD only, no TDD: proceed — generate TODO from PRD with a note that TDD is pending. Mark all technical implementation tasks as needing TDD review before execution.
- TDD only, no PRD: proceed — generate TODO from TDD. Warn that task prioritization may be off without PRD goals and personas.
- Neither: tell the user to run `/prd-tdd-writer` first. Do not attempt to generate a TODO from memory or conversation alone.

**Read PRD Status field** (from header: `**Status:** Draft | Review | Approved`). Surface this in the TODO header — tasks generated from a Draft PRD should carry a warning that scope may change.

---

## Step 2 — Detect Project Type

Read the TDD (or PRD if no TDD) and determine:

- **Web App**: TDD has Database Schema, API endpoints, frontend routes, Supabase/Vercel
- **AI / Agent / Automation**: TDD has Agent Flow, Prompt Design, Tool Definitions, Token Cost, Evals
- **Hybrid**: has both (e.g. a Next.js app with an embedded Claude agent)

Project type determines which phase template is used in Step 4.

---

## Step 3 — Read Project State

In parallel, read:

1. PRD — extract goals, personas, user stories (MVP vs. later), success metrics
2. TDD — extract components, decisions, open questions
3. Codebase structure — what files and folders exist
4. Existing TODO.md — what's already marked done or in progress
5. Git log — `git log --oneline -20` to see what was recently committed

**Codebase scan by project type:**

```bash
# Web App
find src app -type f \( -name "*.ts" -o -name "*.tsx" \) 2>/dev/null | sort
ls supabase/migrations/ 2>/dev/null | sort

# AI / Agent
find . -maxdepth 3 -type f \( -name "*.ts" -o -name "*.py" \) \
  -not -path "*/node_modules/*" 2>/dev/null | sort
find . -maxdepth 3 -name "*.prompt" -o -name "*agent*.ts" -o -name "*agent*.py" 2>/dev/null
```

---

## Step 4 — Determine Status of Each PRD Item

For each feature or requirement in the PRD:

- **DONE** — code exists and the feature is complete (see criteria by type below)
- **IN PROGRESS** — code exists but is incomplete, untested, or partially wired
- **TODO** — no corresponding code found
- **BLOCKED** — depends on an incomplete item; name the blocker

Never mark something DONE without finding the code. Existing file ≠ working feature.

**DONE criteria — Web App:**
- Route file exists AND implements required HTTP methods with auth and Zod validation
- Migration file exists AND RLS policy is defined
- Component renders AND is reachable via a real route
- Tests exist and pass

**DONE criteria — AI / Agent:**
- Agent file/function exists AND runs end-to-end without error
- System prompt and user prompt template are implemented (not placeholders)
- All tool definitions are implemented with correct schemas
- At least one eval / test case is defined and passes
- Error and fallback handling is implemented

---

## Step 5 — Generate TODO.md

If `TODO.md` already exists:
- Preserve all `- [x]` checked items (do not uncheck completed work)
- Preserve any lines that start with `>` or contain inline notes added by the user
- Add net-new items from the PRD that aren't already in the list
- Update status of items where the codebase state has changed
- Do NOT reorder sections the user has reorganized manually

If `TODO.md` does not exist, write it fresh at the project root.

---

### Template — Web App

```markdown
# TODO — <Project Name>
Generated: YYYY-MM-DD
Based on: PRD (<Status field value>), TDD (<Status field value>)
⚠️ PRD is in Draft status — scope may change  ← include only if Draft

## Progress: N/M tasks complete (X%)

---

## Phase 1: Foundation
- [x] Initialize project with TypeScript strict
- [x] Set up Supabase project and local dev
- [ ] Run /ui-builder — lock theme, logo + tagline, component conventions (produces BRAND.md and/or tailwind.config.js with theme tokens)
- [ ] Configure error monitoring (Sentry)

## Phase 2: Database & Auth
- [x] <table> migration with RLS policy
- [ ] <table> migration — needed for <feature>

## Phase 3: API Layer
- [x] GET /api/<resource>
- [ ] POST /api/<resource> — Zod validation needed
- [ ] PATCH /api/<resource>/[id]

## Phase 4: Frontend
- [x] Auth pages (login, signup)
- [ ] <Feature> form — validation missing
- [ ] <Feature> detail page

## Phase 5: Testing
- [ ] Unit tests: <what>
- [ ] E2E tests: <critical flows>

## Phase 6: Deployment
- [ ] Configure Vercel project + env vars
- [ ] Deploy to production

---

## Blocked
- <item> — waiting on <dependency>

## Open Questions (from PRD/TDD)
- <unresolved question>

## Next Action
<single most important thing to do right now>
Skill: /feature-dev | /db-migrate | /api-new
```

---

### Template — AI / Agent

```markdown
# TODO — <Agent / System Name>
Generated: YYYY-MM-DD
Based on: PRD (<Status>), TDD (<Status>)
⚠️ PRD is in Draft status — scope may change  ← include only if Draft

## Progress: N/M tasks complete (X%)

---

## Phase 1: Agent Design
- [ ] Finalize agent flow diagram (trigger → decision → output)
- [ ] Define all tool schemas
- [ ] Write and lock system prompt

## Phase 2: Tool Implementation
- [ ] Implement <tool_name> — schema: <input/output>
- [ ] Unit test each tool with mocked responses

## Phase 3: Prompt Engineering
- [ ] Draft user prompt template with {{variables}}
- [ ] Define output format (JSON schema / structured text)
- [ ] Test prompt against edge cases

## Phase 4: Orchestration
- [ ] Wire trigger (HTTP / cron / event)
- [ ] Implement error + fallback handling
- [ ] Add token usage logging

## Phase 5: Evaluation
- [ ] Define golden eval set (N input/output pairs)
- [ ] Run evals against live Claude API
- [ ] Verify cost estimate matches TDD projection

## Phase 6: Deployment
- [ ] Deploy to <runtime: Vercel fn / cron / Edge Function>
- [ ] Set env vars: ANTHROPIC_API_KEY, <others>
- [ ] Enable monitoring (error rate, latency, token cost)

---

## Blocked
- <item> — waiting on <dependency>

## Open Questions (from PRD/TDD)
- <unresolved question>

## Next Action
<single most important thing to do right now>
Skill: /feature-dev | /claude-api | /api-new | /e2e-test
```

---

## Step 6 — Recommend Next Action

After generating the TODO list, output:

```
Next action: <specific task from the TODO list — not a category, a concrete item>
Why: <one sentence on why this unblocks the most work>
Skill: /feature-dev | /db-migrate | /api-new | /claude-api | /audit | ...
```

If the project is first-run (no TODO.md existed and <25% of PRD items have code), offer to run `/feature-dev` on Phase 1 immediately.

---

## Rules

- Never mark something DONE without finding the corresponding code
- Phase order matters — flag any out-of-order work (e.g. frontend built before the API exists)
- If TODO.md already exists, merge — never wholesale replace it
- The "Next Action" must name a single concrete item, not a direction
- If TDD has open questions, surface them in the TODO's "Open Questions" section so they don't get buried
- If the PRD Status is Draft, add a visible warning — tasks from a draft spec carry scope risk
