---
name: e2e-test
description: Comprehensive end-to-end testing command. Launches parallel sub-agents to research the codebase (structure, database schema, potential bugs), then uses the agent-browser CLI to test every user journey — taking screenshots, validating UI/UX, and querying the database to verify records. Run after implementation to validate everything before code review.
---

# End-to-End Application Testing

## Pre-flight Check

Before starting, run these gates **in this order**. If any fails, stop and report — do not proceed to Phase 1.

```bash
# Gate 1: TypeScript must compile. No point running browser tests if types are broken.
npx tsc --noEmit
# (or: pnpm tsc --noEmit / bun tsc --noEmit)

# Gate 2: Detect dev-server port (try common ports in order)
for port in 3000 3001 5173 8000; do
  if lsof -i :$port -sTCP:LISTEN >/dev/null 2>&1; then
    DEV_PORT=$port; break
  fi
done

# Gate 3: Start the dev server if nothing is listening
if [ -z "$DEV_PORT" ]; then
  npm run dev > /tmp/devserver.log 2>&1 &
  DEV_PORT=3000
fi

# Gate 4: Wait for server with a hard timeout (60s) — fail loudly if it never comes up
DEADLINE=$((SECONDS+60))
until curl -sf "http://localhost:$DEV_PORT" > /dev/null; do
  if [ $SECONDS -ge $DEADLINE ]; then
    echo "Server failed to start within 60s. Check /tmp/devserver.log" >&2
    exit 1
  fi
  sleep 2
done
echo "Server ready on http://localhost:$DEV_PORT"
```

Record `DEV_PORT` — every Phase 2 command uses it.

---

## Phase 1 — Research

### Step 1: Run A and B in parallel (single message, two `Agent` calls)

**Sub-Agent A — Codebase Explorer** (`subagent_type: Explore`)

```
Map this codebase for end-to-end testing. Return a structured report covering:

1. ROUTES — every page route and its file path. Note which require auth.
2. API ENDPOINTS — every route handler, grouped by method (GET / POST / PATCH / DELETE).
   For each: path, file location, what it does in one line, whether it writes to the DB.
3. DATABASE TABLES — list every table, its primary columns, and foreign-key relationships.
   Note RLS-protected tables.
4. AUTH FLOW — describe how login/logout works: which routes, which session mechanism
   (Supabase, NextAuth, custom JWT), where test credentials would come from
   (look for .env.local, seed scripts, README).
5. FEATURE UNDER TEST — based on the most recent commits and uncommitted changes,
   identify which feature should be the primary focus of E2E testing.

Be exhaustive on routes and endpoints. Report under 600 words.
```

**Sub-Agent B — Bug Spotter** (`subagent_type: general-purpose`)

```
Scan this codebase for likely runtime bugs that E2E tests should catch. Look for:

- Components with conditional rendering that lack null/undefined guards
  (e.g. `data.map(...)` without checking data exists)
- API route handlers that don't validate request body with Zod (or equivalent)
- DB queries that could return null where the caller assumes a row exists
- Missing error boundaries around async data
- Form submissions without loading/disabled states (double-submit risk)

For each finding: file:line, the risk in one sentence, and the user-facing symptom
that an E2E test would observe. Report under 400 words, top 10 findings only.
```

### Step 2: Run C after A returns (it depends on A's output)

**Sub-Agent C — Test Planner** (`subagent_type: general-purpose`)

```
Using this codebase map [PASTE SUB-AGENT A OUTPUT HERE], produce a concrete E2E test plan:

1. USER JOURNEYS — list every journey to test, ordered by criticality. For each:
   - Name
   - Step-by-step actions (URLs, clicks, form fields)
   - Expected UI outcome
   - Expected DB state change (table, columns, conditions)
2. EDGE CASES — per journey, list validation/error states to exercise.
3. SCREENSHOTS — list the exact moments to capture (file naming: NN-description.png).
4. TEST CREDENTIALS — specify which credentials each journey needs and where to source them.

Focus on the FEATURE UNDER TEST from A's report. Report under 500 words.
```

---

## Phase 2 — Browser Testing

Drive the browser via the `agent-browser` skill — load it for the exact CLI surface and element-ref syntax. **Do not hardcode the journey here** — execute the journeys produced by Sub-Agent C, against `http://localhost:$DEV_PORT`.

Before running any browser commands, set the screenshot output directory so all screenshots land directly in the project folder — nothing goes to `~/.agent-browser/tmp/`:

```bash
E2E_DATE=$(date +%Y-%m-%d)
mkdir -p ./e2e-screenshots/$E2E_DATE
export AGENT_BROWSER_SCREENSHOT_DIR=./e2e-screenshots/$E2E_DATE
```

### Per-journey loop

For each journey from C's plan:

1. Open the starting URL.
2. Take a "before" screenshot: `agent-browser screenshot NN-<journey>-before.png`
3. Execute the steps (open → snapshot → fill → click → wait).
4. Take an "after" screenshot: `agent-browser screenshot NN-<journey>-after.png`
5. **Capture console messages** — read browser console for errors/warnings produced during the journey.
6. **Capture network errors** — read network log for any 4xx/5xx responses.
7. If the journey writes data, hand off to Phase 3 (DB verification) before moving on.

### Always-capture checklist

For every test session, regardless of journey:

| Moment | Capture |
|---|---|
| Initial page load | Screenshot + console snapshot (catches hydration errors) |
| Unauthenticated access to a protected route | Screenshot (confirms redirect) |
| After login | Screenshot + network log (confirms auth requests succeed) |
| After every form submission | Screenshot + console + network (catches silent 500s) |
| After validation failure | Screenshot (confirms error messages render) |
| After delete/remove | Screenshot (confirms removal) |
| After logout | Screenshot (confirms session cleared) |
| Any unexpected error UI | Screenshot + console — stop and record before retrying |

### Where screenshots go

`AGENT_BROWSER_SCREENSHOT_DIR` is set at Phase 2 start to `./e2e-screenshots/<YYYY-MM-DD>/`. All `agent-browser screenshot` calls write there directly — nothing accumulates in `~/.agent-browser/tmp/`. Use filenames like `NN-<journey>-<state>.png` and reference these paths in the Phase 4 report.

---

## Phase 3 — Database Verification

After any browser action that writes data, verify the DB state. **Prefer MCP tools** — they work the same against local and remote Supabase, with no shell setup.

### Path A — Supabase MCP (preferred when available)

```
mcp__supabase__execute_sql with query:
  SELECT * FROM <table> WHERE <condition> ORDER BY created_at DESC LIMIT 5;
```

Useful companions:
- `mcp__supabase__list_tables` — confirm table exists / inspect schema
- `mcp__supabase__get_advisors` — surface RLS/security warnings introduced by the change
- `mcp__supabase__get_logs` — pull recent Postgres / API logs if a write silently failed

### Path B — Local Supabase via shell (fallback when MCP unavailable)

```bash
psql postgresql://postgres:postgres@localhost:54322/postgres \
  -c "SELECT * FROM <table> ORDER BY created_at DESC LIMIT 5;"
```

### Path C — Non-Supabase stacks

Use the project's own DB client (Prisma Studio, drizzle-kit, raw psql/mysql) per the project's conventions — discover from Sub-Agent A's report.

### What to verify on every write

- Row exists with the expected column values
- `user_id` (or tenant key) matches the authenticated user
- `created_at` / `updated_at` populated
- Soft-delete columns (`deleted_at`) set correctly on delete operations
- RLS didn't silently drop the insert (no missing row when one was expected)
- No duplicate rows from accidental double-submit

---

## Phase 4 — Report & Follow-through

### 4a. Write the report to `E2E_TEST.md` in the project root

Overwrite any previous run.

```markdown
# E2E Test Report — <Feature Name>
Date: YYYY-MM-DD
Branch: <branch>
Commit: <short-sha>

## Test Environment
- App: http://localhost:<DEV_PORT>
- DB: local Supabase / remote Supabase / other (specify)

## User Journeys Tested

| Journey | Result | Console clean? | Network clean? | DB verified? | Notes |
|---|---|---|---|---|---|
| Unauthenticated redirect | PASS | yes | yes | n/a | Redirects to /login |
| Login — valid creds | PASS | yes | yes | n/a | Session cookie set |
| Create <resource> — happy | PASS | yes | yes | yes | Row in <table> |
| Create <resource> — validation | PASS | yes | yes | n/a | Field errors shown |
| Delete <resource> | PASS | yes | yes | yes | deleted_at populated |
| Logout | PASS | yes | yes | n/a | Session cleared |

## Screenshots
- `e2e-screenshots/2026-05-24/01-initial.png`
- `e2e-screenshots/2026-05-24/02-login-before.png`
- ...

## Issues Found

| Severity | Type | Description | Reproduction | Evidence |
|---|---|---|---|---|
| HIGH | BUG | <description> | <steps> | screenshot path / console line |
| MED | UI | <description> | <steps> | screenshot path |
| LOW | PERF | <description> | <steps> | network log line |

## Overall Result: GO / NO-GO

GO requires: all critical journeys PASS, no HIGH severity issues, console clean on every journey.
NO-GO if any of the above fail — list the blockers explicitly.
```

### 4b. Append remediation tasks to `TODO.md`

For every issue in the report, append an entry under a `## E2E Test Remediation` section in `TODO.md` (create the section if it doesn't exist). Format:

```markdown
- [ ] [HIGH] [BUG] <description> — see E2E_TEST.md for repro
```

Do not silently swallow findings. If `TODO.md` doesn't exist in the project, create it.

### 4c. State the GO / NO-GO verdict in chat

End the session with an explicit one-line verdict so the user doesn't have to open the report to know the result.

### 4d. Clean up tmp

After the verdict, purge the agent-browser scratch directory:

```bash
rm -f ~/.agent-browser/tmp/screenshot-*.png
```

Screenshots are already saved to `./e2e-screenshots/<date>/` via `AGENT_BROWSER_SCREENSHOT_DIR` — anything left in tmp is a stale artefact.

---

## Rules

- Never test against production unless the user explicitly asks
- Pre-flight gates are hard gates — TS errors or a server that won't start mean stop, not "try anyway"
- Take screenshots before and after every significant interaction
- Capture console + network on every journey — UI-only verification misses silent 500s
- If a test step fails, capture screenshot + console + network state, then stop the journey (don't barrel through)
- Verify DB state after any write — never trust the UI alone
- All findings land in both `E2E_TEST.md` (report) and `TODO.md` (remediation)
- End with a one-line GO / NO-GO verdict
