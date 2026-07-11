---
name: sheets-app-dev
description: Dev process for Sheets-backed dashboard apps — a single-file .html/.jsx React UI with Google Sheets as the database and a Google Apps Script Web App as the API layer (the pattern proven on the FiberLine ISP Billing console). Use when building, extending, or debugging any app where the data store is a Google Sheet and the backend is Code.gs deployed as a Web App. Triggers on /sheets-app-dev, "sheets-backed app", "Apps Script backend", "Google Sheets as database", "build an app like the ISP billing one", "single-file dashboard with Sheets", "Code.gs web app", or "spreadsheet-backed CRUD app".
---

# Sheets-Backed App Dev Process

Build and operate small internal dashboard apps on a deliberately minimal stack:

```
Browser (single-file React SPA — .jsx source + zero-build .html wrapper)
        │  fetch (GET query string / POST text/plain JSON)
        ▼
Apps Script Web App (Code.gs) — doGet / doPost, LockService, optional API_TOKEN
        │  SpreadsheetApp API
        ▼
Google Sheet — one tab per "table", header row = schema
```

## When this pattern fits (and when it doesn't)

**Fits:** solo/few-operator internal tools, $0 budget, "usable within days" timelines, low tens-to-hundreds of rows per tab, human-editable data a bonus, workflow validation before committing to a bigger build.

**Doesn't fit — recommend Supabase/Next.js instead (workspace default):** multi-user with real auth/roles, real customer PII at scale (PH DPA obligations), >~1k rows per tab or high write concurrency, need for relational integrity, sub-second latency requirements (Apps Script cold starts are seconds). If the app may graduate later, keep this track's docs separate from the future track's from day one (see the ISP Billing two-track precedent at `~/projects-mvp/isp-billing/`).

---

## Phase 0 — Bootstrap (delegate, don't reinvent)

1. New project: run `/init` (skeleton + git) → auto-chains `/prd-tdd-writer` → `/plan-todo`. In the TDD, record the Sheets-over-Supabase decision explicitly with trade-offs (no RLS, no FK enforcement, quotas) and the graduation trigger as an open question.
2. Existing prototype folder: skip the doc-writer chain if PRD/TDD/TODO already exist — just add `CLAUDE.md` + `.gitignore` + `git init`.
3. Theme: `/theme-hayahai` (or `/theme-client` for client work) for the palette; `/ui-builder` if composing a new dashboard layout from scratch.

## Phase 1 — Design the Sheet schema

- One tab per entity. **Row 1 = headers, exact spelling, case-sensitive** — `sheetToObjects` keys objects off the header row, so a typo silently produces `undefined` fields, not an error.
- Column conventions: `id` first (string, `<PREFIX><Date.now()>`), FK columns named `<entity>Id` (convention only — Sheets enforces nothing; validate existence server-side at write time).
- No soft deletes / audit columns at prototype stage — accept and document the gap in the TDD rather than half-implementing it.
- Reference/catalog tabs (e.g. Plans) are seeded by hand and read-only to the app; transactional tabs (Customers, Invoices, Payments) start empty and are app-written only.
- Document the schema per tab in the TDD §3 (and later in `okf/tables/` — Phase 6).

## Phase 2 — Write Code.gs (the backend)

Skeleton every Code.gs should follow (proven shape — see `~/projects-mvp/isp-billing/sheets-version/Code.gs` as the reference implementation):

- `doGet(e)` → dispatch on `e.parameter.action`; a single `getAll` action returning every tab as JSON is usually enough — no pagination until row counts demand it.
- `doPost(e)` → `JSON.parse(e.postData.contents)`, dispatch on `body.action`, **entire switch wrapped in `LockService.getScriptLock()` with `waitLock(10000)` and `releaseLock()` in `finally`** — serializes writes so concurrent `appendRow` calls don't race.
- `checkAuth(token)` → compare against an `API_TOKEN` Script Property (`PropertiesService`); **return true if the property is unset** so auth is opt-in and can't lock you out mid-setup. Never hardcode the token in committed code.
- Validate at the boundary before any `appendRow`/`setValue`: required fields non-empty after trim, numerics via `Number()` + range checks, enums against a `const` array, FK existence by scanning the referenced tab.
- Helpers: `sheetToObjects(sheet)` (rows → objects keyed by headers; format `Date` cells to `yyyy-MM-dd` — Sheets auto-coerces date-looking strings into Date objects on read-back), `setFieldByMatch(...)` for in-place single-field updates, `respond(obj)` returning `ContentService` JSON.
- Idempotency for bulk writes: build a skip-list from existing rows before appending (the duplicate-invoice-guard pattern — re-running a bulk generation for the same period must be safe).

**Apps Script platform facts to design around:**
- Web Apps **always return HTTP 200**, even for errors — the response body carries `{ error: string }` and clients must check that, not status codes.
- **No CORS preflight support** — POST with `Content-Type: text/plain` (a "simple request") and JSON-parse the body server-side. Do not use `application/json`.
- Quotas: ~6 min/execution, daily totals — fine at this scale, note in TDD.
- Error shape matches the workspace convention: `{ error: string }`.

## Phase 3 — Wire the frontend

- Single-file React SPA (function components + hooks, Tailwind, Recharts for charts, lucide-react for icons). No component splitting until scope demands it.
- Two build forms of the same app:
  - `<app>.jsx` — the source; deployable later via a bundler if ever needed.
  - `<app>.html` — **zero-build standalone wrapper**: CDN React + ReactDOM + Recharts + lucide-react UMD + in-browser Babel, app code inline in a `<script type="text/babel">`. This is the default deploy artifact — no Node/npm, opens directly in a browser, matches "usable within days".
- **Known CDN bug:** lucide-react's UMD bundle reads `window.react` (lowercase) but React's UMD only sets `window.React`. Add `<script>window.react = window.React</script>` (and same for ReactDOM if needed) *before* the lucide script tag.
- API client: `apiGet(action, params)` builds a query string onto `APPS_SCRIPT_URL`; `apiPost(action, payload)` sends text/plain JSON. Both append `token: API_TOKEN` and both throw on `data.error`.
- Config consts at the top of the file: `APPS_SCRIPT_URL` (the `/exec` URL) and `API_TOKEN` (blank = auth off). **These must be updated in both the .jsx and the .html** — easy to change one and forget the other.
- Required UI states: `SetupScreen` (URL not configured), `LoadingScreen`, `ErrorScreen` (with retry), plus a toast for write feedback.
- Data flow: full `getAll` on mount, full re-fetch (`refresh()`) after every successful write. Derive computed views (balances, overdue, KPIs) client-side with `useMemo` — do not store derived values in the Sheet.

## Phase 4 — Deploy

**Sheet:** create manually or via the Google Drive MCP tools. If uploading an .xlsx via MCP `create_file`, keep it minimal — large base64 blobs (>~5KB) passed as literal tool-call params are unreliable (transcription corruption); verify post-upload with `read_file_content`.

**Backend (first deploy):** Sheet → Extensions → Apps Script → paste Code.gs → Deploy → New deployment → type Web app → Execute as **Me** → access **Anyone** (or "Anyone within org" on Workspace — tighter, prefer when available). **The OAuth consent click is a hard human-in-the-loop step** ("Advanced → Go to project (unsafe) → Allow") — it cannot be automated; hand it to the user and wait for the `/exec` URL back.

**Backend (every subsequent change):** **Deploy → Manage deployments → Edit (pencil) → New version.** Editing the script alone does NOT update the live endpoint — this is the #1 source of "my change did nothing" confusion in this pattern. Editing the existing deployment keeps the URL stable; creating a *new* deployment mints a new URL and forces a frontend config update.

**Frontend:** the standalone .html deploys anywhere static — `/netlify-deploy` or `/vercel-deploy` (free tier), or just open the file locally for solo use.

**Auth (recommended before the URL leaves your machine):** set Script Property `API_TOKEN` (e.g. `openssl rand -hex 16`), redeploy a new version, set the matching const in the frontend. It's a shared secret, not real auth — acceptable only for internal tools.

## Phase 5 — Verify and test

- After every Code.gs redeploy, exercise the live endpoint — `/verify` mindset: drive the real flow, don't assume the deploy took.
- Smoke-test order: raw `curl` GET `?action=getAll` first (proves deploy + auth), then one write via curl (proves lock + validation), then the full flows through the actual UI via `/agent-browser` or `/e2e-playwright` against the standalone .html.
- Test idempotent bulk writes by running them twice and asserting the second run creates 0 rows.
- Formal unit tests are usually skipped on this track (per-TDD decision) — the substitute is a documented manual walkthrough of every write path after each backend change. Keep the list of exercised-vs-unexercised paths current in TODO.md.
- Clean up test rows from the live Sheet before real use — dev and prod are the same Sheet in this pattern; track cleanup as an explicit TODO item.

## Phase 6 — Document and maintain

- Write a `SETUP.md` in the project: Sheet tab/header spec, deploy steps, the redeploy-new-version warning, and the API_TOKEN procedure.
- Once the app works end-to-end, run `/okf-knowledge` (project mode) to build `okf/` — concepts for the backend service, each API action, each Sheet tab (schema + FK/PII notes), the deploy/redeploy runbooks, and the Sheets-over-alternative decision record. Wire `CLAUDE.md` at the bundle per that skill.
- `/checkpoint` at session end, `/resume` at session start — this pattern involves live external state (the Sheet, the deployment URL, test rows) that git can't reconstruct, so checkpoints must record: live Sheet URL/id, `/exec` URL, which write paths are verified, and any test data pending cleanup.
- `/commit-push` for git hygiene; `/audit` before anything user-facing ships; `/ph-dpa-compliance` becomes mandatory the moment real subscriber/customer PII enters the Sheet.

---

## Skill wiring map

| Stage | Skill |
|---|---|
| Bootstrap | `/init` → `/prd-tdd-writer` → `/plan-todo` |
| Theme/UI | `/theme-hayahai` or `/theme-client`, `/ui-builder` |
| Build | this skill (Phases 1–4) |
| Verify | `/verify`, `/agent-browser`, `/e2e-playwright` |
| Deploy frontend | `/netlify-deploy` or `/vercel-deploy` |
| Ship gate | `/audit`; `/ph-dpa-compliance` if real PII |
| Docs | `/okf-knowledge` |
| Session | `/checkpoint`, `/resume`; `/commit-push` |

## Non-negotiables (recap)

1. Header row is the schema — exact, case-sensitive, documented.
2. Every write validates inputs and FK existence before touching the Sheet.
3. All writes serialized via `LockService` with `releaseLock()` in `finally`.
4. Clients check `data.error`, never HTTP status.
5. POST as `text/plain` — never `application/json`.
6. Code.gs change ⇒ new deployment **version**, always.
7. `API_TOKEN` in Script Properties, never in committed code.
8. Bulk writes idempotent via skip-lists.
9. Dev = prod Sheet: track and clean test rows explicitly.

## Reference implementation

`~/projects-mvp/isp-billing/sheets-version/` — Code.gs, the .jsx/.html pair, SETUP.md, and an OKF bundle (`okf/`) documenting every piece of this pattern in the concrete.
