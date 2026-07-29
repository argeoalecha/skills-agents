# Apps Script Backend (Code.gs) — Pattern Reference

Extracted from the proven implementation at
`~/projects-mvp/isp-billing/sheets-version/Code.gs` (9 write actions + `getAll`,
live in production for the SILAGO ISP billing console). The generic scaffold is
`assets/Code.gs.template` — start there; consult the reference impl for the
concrete versions of every pattern below.

## Shape

One file, four layers, in this order:

1. **Header comment** — the tab/header spec (row 1, exact spelling,
   case-sensitive), business rules, and the API_TOKEN note. This comment is the
   backend's schema documentation; keep it current.
2. **Entry points** — `doGet(e)` / `doPost(e)`.
3. **Action handlers** — one function per action, each returning a plain object
   (`{ ok: true, ... }` or `{ error: string }`), never a `ContentService` value.
4. **Helpers** — `sheetToObjects`, `setFieldByMatch`, date utils, `sanitizeCell`,
   `respond`.

## Entry points

- `doGet(e)` → auth check, then dispatch on `e.parameter.action`. A single
  `getAll` returning every tab via `sheetToObjects` is usually the only GET —
  no pagination until row counts demand it.
- `doPost(e)` → `JSON.parse(e.postData.contents)` in a try/catch (bad body →
  `{ error: "Invalid request body" }`), auth check, then the **entire switch
  wrapped in `LockService.getScriptLock()` with `waitLock(10000)`**, handlers
  inside `try`, catch-all returning `{ error: err.message }`, and
  `lock.releaseLock()` in `finally`. This serializes writes so concurrent
  `appendRow` calls don't race. Correct for solo/few-operator volume; does not
  scale to many concurrent writers — that's a graduation signal.

## Auth

```js
function checkAuth(token) {
  const required = PropertiesService.getScriptProperties().getProperty("API_TOKEN");
  if (!required) return true; // not configured — auth disabled
  return token === required;
}
```

Opt-in by design — an unset property disables auth so you can't lock yourself
out mid-setup. GET reads the token from `e.parameter.token`; POST from
`body.token`. It's a shared secret, not real auth — internal tools only. Never
hardcode it in committed code.

## Validation at the boundary

Every handler validates before any `appendRow`/`setValue`:

- Required strings: `String(body.x || "").trim()` then reject empty.
- Numbers: `Number(body.x)` then `Number.isFinite` / `Number.isInteger` +
  range check (`!(amount > 0)` also rejects NaN).
- Enums: index-of against a top-level `const` array
  (`VALID_STATUSES = [...]`).
- Dates: accept only `YYYY-MM-DD` strings — `isValidDateStr` regex.
- FK existence: scan the referenced tab with `sheetToObjects` and reject a
  `planId`-style value that matches no row. Sheets enforces nothing; this scan
  is the only referential integrity you get.
- Uniqueness: scan the target tab for an existing `id`/`acct` before append.

Error messages state what to fix ("billingDay must be a whole number between
1 and 28"), matching the workspace `{ error: string }` shape.

## Cell sanitization — non-negotiable

Sheets treats a leading `=` `+` `-` `@` as a formula (or arithmetic coercion)
even when written via `appendRow`/`setValue` — a name like `=IMPORTXML(...)`
would execute; a contact like `+639...` would break. Map **every** written row
through:

```js
function sanitizeCell(v) {
  return typeof v === "string" && /^[=+\-@]/.test(v) ? "'" + v : v;
}
// sheet.appendRow([...].map(sanitizeCell));
```

The apostrophe is Sheets' literal-text marker — not stored, not seen on
readback.

## Date handling — two traps

1. **Read-back coercion:** Sheets auto-converts date-looking strings into
   `Date` objects. `sheetToObjects` must format any `Date` cell back to
   `yyyy-MM-dd` via `Utilities.formatDate(v, Session.getScriptTimeZone(), ...)`
   or clients receive ISO timestamps that break string comparisons.
2. **Parse timezone shift:** never `new Date("YYYY-MM-DD")` — it parses as UTC
   and can shift the calendar day in a non-UTC timezone. Use a manual
   split-parse (`parseDateStr` in the template) producing a local-midnight Date.

## Core helpers

- `sheetToObjects(sheet)` — rows → objects keyed by the header row; skips rows
  with an empty first cell; formats Date cells (above). A header typo silently
  yields `undefined` fields, not an error — which is why headers are treated as
  schema.
- `setFieldByMatch(sheet, idField, idValue, fieldName, fieldValue)` — find row
  by id, `setValue` one cell in place; returns found/not-found.
- Multi-field update: read `getDataRange().getValues()` once, locate the row by
  id column, then `setValue` per changed field via `headers.indexOf(field)`
  (see `updateCustomer` in the reference impl).
- `respond(obj)` — `ContentService.createTextOutput(JSON.stringify(obj))
  .setMimeType(ContentService.MimeType.JSON)`. The only place ContentService
  appears.

## Idempotency patterns (both proven in production)

- **Bulk generation skip-list:** before appending, build a key-map from
  existing rows (e.g. `customerId|YYYY-MM` per invoice) and skip keys already
  present. Re-running the same period must create 0 rows. Verify by running
  twice.
- **Client-generated write id:** Apps Script executes a POST even when the
  client loses the response (the 302 redirect can fail to follow). For
  must-not-duplicate writes (payments), accept an optional client id
  (validated by regex, e.g. `^PAY[A-Za-z0-9]{6,40}$`); if it's already in the
  ledger, return `{ ok: true, duplicate: true }` instead of appending. The
  frontend resends the same id on retry.
- **Editor-runnable migrations:** wrap any one-time migration action in a
  zero-arg function (`runMigrateX()`) that calls it with
  `SpreadsheetApp.getActive()` and `Logger.log`s the result, so it can be run
  from the editor's function dropdown without a token. Make the migration
  re-derive its targets each run so a repeat run is a no-op.

## Derived values live in code, not cells

Balances, credit, KPIs are recomputed from the ledger tabs on every request
(or client-side) — never stored in the Sheet. Stored derivations go stale the
moment a human edits a row.

## Platform facts to design around

- Web Apps **always return HTTP 200** — the body carries `{ error }`; clients
  must check that, never status codes.
- **No CORS preflight support** — clients POST `Content-Type: text/plain`
  (a "simple request"); the server JSON-parses `e.postData.contents`
  regardless. Never `application/json`.
- Quotas: ~6 min/execution, daily totals — fine at this scale; note in TDD.
- No RLS, no schema enforcement — access control is whatever `checkAuth`
  provides; schema is the header row plus your validation.
- Any `Code.gs` change requires a **new deployment version** — see
  `references/deploy-runbook.md`.
