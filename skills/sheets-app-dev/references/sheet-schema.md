# Sheet Schema — Conventions

The Sheet is the database; the header row is the schema. Reference example:
the 4-tab ISP billing Sheet documented in
`~/projects-mvp/isp-billing/sheets-version/okf/tables/`.

## Tabs

- One tab per entity. Reference/catalog tabs (e.g. `Plans`) are seeded by hand
  and read-only to the app; transactional tabs (e.g. `Customers`, `Invoices`,
  `Payments`) start empty and are app-written only.
- **Row 1 = headers — exact spelling, case-sensitive.** `sheetToObjects` keys
  objects off this row; a typo silently produces `undefined` fields, not an
  error. The header spec lives in three places that must agree: the Sheet
  itself, the `Code.gs` header comment, and the TDD §3 (later `okf/tables/`).

## Columns

- `id` first. Generated string ids: `<PREFIX><Date.now()>` (`C1720...`,
  `PAY1720...`). Human-meaningful ids where the domain has them
  (`INV-{acct}-NNN` — derived from a stable anchor, never from row count, so a
  deleted mid-series row regenerates with the same id instead of colliding).
- FK columns named `<entity>Id` (`planId`, `customerId`, `invoiceId`) —
  convention only; Sheets enforces nothing. Validate existence server-side at
  write time; changing a referenced id requires a migration action that
  rewrites the referencing tabs too (see `migrateInvoiceIds` in the reference
  impl).
- Dates stored as `YYYY-MM-DD` strings. Enums as lowercase strings validated
  against a `const` array in Code.gs.
- Denormalized convenience columns (e.g. `Payments.subscriber` = "name · acct")
  are allowed **for human readability of the Sheet only** — the API must never
  derive logic from them.

## What this schema deliberately lacks

- No soft deletes, no `createdAt`/`updatedAt`/`createdBy` audit columns at
  prototype stage — accept and document the gap in the TDD rather than
  half-implementing it. (This is a sanctioned deviation from the workspace
  database conventions; record it in the Sheets-over-Supabase decision.)
- No derived/computed columns — balances, credit, status rollups are
  recomputed from the ledger tabs in code every time. A stored derivation goes
  stale the moment a human edits a row.
- No formulas in app-written ranges — and app writes must neutralize
  formula-leading input (`sanitizeCell`, see the backend reference).

## Humans edit this database

That's a feature (hand-seed catalogs, fix typos in place) and a hazard:
- The app must tolerate hand-edited rows — hence empty-first-cell row
  skipping, `Number()` coercion, and date re-formatting on read.
- Dev = prod. Test rows land in the live Sheet; track them and clean them up
  as an explicit TODO item before real use.

## Scale ceiling

Low tens-to-hundreds of rows per tab. Past ~1k rows per tab, high write
concurrency, real relational integrity needs, or real customer PII at scale
(PH DPA obligations) — graduate to the Supabase/Next.js track. Keep the two
tracks' docs separate from day one (the `isp-billing/` two-folder precedent).
