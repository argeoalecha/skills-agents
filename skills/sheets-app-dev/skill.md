---
name: sheets-app-dev
description: Dev process for Sheets-backed dashboard apps — a single-file .html/.jsx React UI with Google Sheets as the database and a Google Apps Script Web App as the API layer (the pattern proven on the SILAGO/FiberLine ISP Billing console). Use when building, extending, or debugging any app where the data store is a Google Sheet and the backend is Code.gs deployed as a Web App. Triggers on /sheets-app-dev, "sheets-backed app", "Apps Script backend", "Google Sheets as database", "build an app like the ISP billing one", "single-file dashboard with Sheets", "Code.gs web app", or "spreadsheet-backed CRUD app".
user-invocable: true
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

This skill is the **pattern and template layer** for the stack — scaffolds,
platform facts, and phase process. The **canonical reference implementation**
is `~/projects-mvp/isp-billing/sheets-version/` (live in production): its
`Code.gs`, `.jsx`/`.html` pair, `SETUP.md`, and OKF bundle (`okf/`) are the
ground truth every template here was extracted from. When a pattern question
isn't answered in `references/`, read the reference implementation.

---

## Skill Root

All paths relative to `~/.claude/skills/sheets-app-dev/`.

| Path | What it is |
|---|---|
| `references/apps-script-backend.md` | **Code.gs deep reference** — entry-point shape, auth, validation, sanitizeCell, date traps, helpers, idempotency patterns, platform facts |
| `references/frontend-spa.md` | **SPA deep reference** — two build forms, CDN shim, API client, required states, data flow, console styling, print surfaces |
| `references/sheet-schema.md` | Schema conventions — headers-as-schema, id/FK rules, deliberate gaps, humans-edit-the-db, scale ceiling |
| `references/deploy-runbook.md` | First deploy, the redeploy-new-version gotcha, API_TOKEN procedure, post-deploy verification |
| `assets/Code.gs.template` | Generic backend scaffold — copy, rename tabs/actions, keep every helper |
| `assets/app-template.html` | Zero-build frontend skeleton, styled per **hayah-console** — shell, table, metric cards, badges, toast, arc loader, Setup/Loading/Error screens |

External anchors:

| Path | What it is |
|---|---|
| `~/projects-mvp/isp-billing/sheets-version/` | Reference implementation — production Code.gs (9 write actions + `getAll`), SPA pair, OKF bundle |
| `~/.claude/skills/theme-hayahai/hayahai-design/project/themes/hayah-console.json` | Console theme tokens the app template implements |

---

## Relationship with sibling skills

| If the task is… | Skill that owns it |
|---|---|
| Building/extending/debugging a Sheets-backed app | **This skill** — templates + references here |
| Project bootstrap (skeleton, PRD/TDD, TODO) | `/init` → `/prd-tdd-writer` → `/plan-todo` |
| Theme tokens, logo, component specs | `/theme-hayahai` (**hayah-console** for app screens) or `/theme-client` for client brands |
| Composing a new dashboard layout from scratch | `/ui-builder` (calls into theme skills) |
| Static hosting of the .html | `/netlify-deploy` or `/vercel-deploy` |
| Verification / E2E | `/verify`, `/agent-browser`, `/e2e-playwright` |
| Ship gate / PII | `/audit`; `/ph-dpa-compliance` the moment real customer PII enters the Sheet |
| Knowledge base once it works | `/okf-knowledge` (project mode) |
| Session continuity | `/checkpoint`, `/resume`; `/commit-push` |

## When this pattern fits (and when it doesn't)

**Fits:** solo/few-operator internal tools, $0 budget, "usable within days"
timelines, low tens-to-hundreds of rows per tab, human-editable data a bonus,
workflow validation before committing to a bigger build.

**Doesn't fit — recommend Supabase/Next.js instead (workspace default):**
multi-user with real auth/roles, real customer PII at scale (PH DPA
obligations), >~1k rows per tab or high write concurrency, relational
integrity needs, sub-second latency (Apps Script cold starts are seconds). If
the app may graduate later, keep this track's docs separate from the future
track's from day one (the `isp-billing/` two-folder precedent).

---

## When Invoked

1. **New app:** Phase 0 bootstrap, then copy both `assets/` templates and
   rename tabs/actions/entities to the domain. Do not regenerate the scaffolds
   from memory — the templates encode non-obvious platform fixes
   (`sanitizeCell`, the lucide shim, `text/plain`, date parsing).
2. **Extending/debugging an existing app:** read the relevant
   `references/*.md` first; the top failure causes are, in order — stale
   deployment version, header-row typo, missing `sanitizeCell`, config const
   updated in only one of the two frontend files.
3. Styling questions route to `hayah-console.json` via `/theme-hayahai` —
   app screens always get Console unless the client mandates their own brand
   (the structure survives a palette swap; the ISP console itself is
   client-branded).

## Phases

### Phase 0 — Bootstrap (delegate, don't reinvent)
New project: `/init` (skeleton + git) → auto-chains `/prd-tdd-writer` →
`/plan-todo`; record the Sheets-over-Supabase decision in the TDD with
trade-offs (no RLS, no FK enforcement, quotas) and the graduation trigger.
Existing prototype folder: just add `CLAUDE.md` + `.gitignore` + `git init`.

### Phase 1 — Design the Sheet schema
Follow `references/sheet-schema.md`. One tab per entity; **row 1 = headers,
exact, case-sensitive**; `id` first; FK columns `<entity>Id` validated
server-side; no derived values in cells. Document per-tab schema in TDD §3.

### Phase 2 — Write Code.gs
Start from `assets/Code.gs.template`; patterns and platform facts in
`references/apps-script-backend.md`. Keep the header comment (the schema doc)
current. All writes: validated → sanitized → inside the script lock.

### Phase 3 — Wire the frontend
Start from `assets/app-template.html`; patterns in
`references/frontend-spa.md`. Zero-build .html is the default deploy artifact;
add the .jsx source only if a bundled deploy is actually planned — and then
keep the pair in sync on every edit.

### Phase 4 — Deploy
Follow `references/deploy-runbook.md`. The OAuth consent click is a hard
human-in-the-loop step; every Code.gs change afterwards needs **Manage
deployments → Edit → New version**. Set `API_TOKEN` before the URL leaves
your machine.

### Phase 5 — Verify
`/verify` mindset after every redeploy: curl `getAll` → one curl write → real
flows through the UI (`/agent-browser` / `/e2e-playwright`). Idempotent bulk
writes run twice must create 0 rows the second time. Formal unit tests are
usually skipped on this track (per-TDD decision) — the substitute is a
documented manual walkthrough of every write path after each backend change,
tracked in TODO.md. Dev = prod Sheet: clean up test rows explicitly.

### Phase 6 — Document and maintain
`SETUP.md` (tab/header spec, deploy steps, redeploy warning, token
procedure). Once working end-to-end: `/okf-knowledge` for the `okf/` bundle
(service, per-action APIs, per-tab schemas, runbooks, decision records).
`/checkpoint` must record live external state git can't reconstruct: Sheet
URL/id, `/exec` URL, verified-vs-unverified write paths, test rows pending
cleanup. `/audit` before anything user-facing ships.

---

## Non-negotiables

1. Header row is the schema — exact, case-sensitive, documented in three
   agreeing places (Sheet, Code.gs header comment, TDD/okf).
2. Every write validates inputs and FK existence before touching the Sheet.
3. All writes serialized via `LockService` with `releaseLock()` in `finally`.
4. Every written row maps through `sanitizeCell` — formula injection and
   `+63…` phone numbers are both real failures without it.
5. Clients check `data.error`, never HTTP status (always 200).
6. POST as `text/plain` — never `application/json` (no CORS preflight).
7. Code.gs change ⇒ new deployment **version**, always.
8. `API_TOKEN` in Script Properties, never in committed code — and never
   commit a real token/URL pair to a public repo.
9. Bulk writes idempotent via skip-lists; must-not-duplicate writes idempotent
   via client-generated ids.
10. Dates: `YYYY-MM-DD` strings end-to-end; format Dates on read, split-parse
    on write — never `new Date("YYYY-MM-DD")`.
11. Dev = prod Sheet: track and clean test rows explicitly.
