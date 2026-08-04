# Digital Twin / Dashboard Mimic Spec — Topology Bindings, Tag Schema, RLS
## QC 3-Storey Mixed-Use, 4-Tenant Submetering — SYNTHETIC SMOKE TEST

**Status:** Draft, topology/tag-schema layer only. No code has been built for this smoke
test beyond the illustrative Zod/RLS fragments below, per the smoke-test instruction.
**Not for construction/deployment** until load-calc unblocks (see §5) and this spec is
re-reviewed against real numeric thresholds.

**Node ID source of truth:** `topology.json` in this folder (as-built-agent output,
version 0.1-synthetic, unsurveyed). Every panel/feeder ID below is copied verbatim from
that file. Do not rename.

---

## 1. Scope boundary — restated before anything else

This document defines **structure**: which physical node maps to which tag, what data
type and unit each tag carries, and where thresholds *will* attach once they exist. It
does **not** define any numeric alarm setpoint, breaker %-loading band, or over-current
threshold. `load-calc-gap-report.md` confirms zero threshold figures exist yet — see
`load-calc-gap-report.md` §"Downstream impact of this refusal": *"digital-twin-agent: no
breaker ratings or 80%-continuous flags exist yet to derive alarm/warning thresholds
from."* Every threshold field below is explicitly `TBD-pending-load-calc`, not a stub
value, not a placeholder number, not rounded from anything. Do not let a build step fill
these with a guess to "unblock the UI" — that is the exact failure mode this pipeline
exists to prevent.

---

## 2. Monitoring topology — panel/tenant → tag binding

Source nodes are from `topology.json`. Only nodes with a confirmed instrumentation path
(per `instrumentation-procurement.md` §3: Modbus RTU RS-485, 4 tenant submeters →
RTU→TCP gateway at MP-1) get live monitoring points. Nodes without a metering plan get
no tag — see §2.4 for what is explicitly excluded and why.

### 2.1 Main panel (MP-1) — no submeter, utility-metered only

`MP-1` is Meralco-metered on the utility side (as-built: `"metering": "Utility-metered
(main only)"`) — that revenue meter is Meralco's asset, out of scope per baseline §5.1,
and is **not** on the Modbus RS-485 bus described in the instrumentation doc. No
`instrumentation-procurement.md` section proposes a main-panel submeter or gateway tag
for MP-1 itself.

**Consequence for the dashboard:** there is no live main-bus tag to bind to. Any
"aggregate load" figure the mimic shows for MP-1 must be computed as the arithmetic sum
of the 4 tenant tags (§2.2) client-side/server-side, labeled explicitly as **calculated,
not metered**, and must not be presented as though it came from a device at MP-1. If a
main-bus submeter is added later, this is a real gap to flag to
instrumentation-procurement-agent now rather than silently synthesizing a phantom tag.

- `node_id`: `MP-1`
- `tag_type`: none (no device) — `derived_aggregate` only, computed from §2.2 tags
- `main_breaker_rating_amps`: **TBD-pending-load-calc** (as-built: `main_breaker_rating`
  status = UNKNOWN, not field-surveyed; also not a load-calc output until the
  replacement design runs)
- `existing_service_rating_amps`: 100 (topology.json `MP-1.attributes.rating_amps`,
  status ASSUMED per as-built — display as existing/legacy reference figure only, not a
  design threshold; do not treat 100 A as the alarm ceiling)

### 2.2 Tenant subpanels — 4 live-metered points

Each of the 4 tenant subpanel nodes gets one Modbus-polled submeter per
`instrumentation-procurement.md` §3 (protocol) and §0/§5 (meter class shortlist, CT
ratio still blocked).

| `node_id` (topology.json) | Tenant / floor | Meter class (per instrumentation doc, TBD final SKU) | Poll path |
|---|---|---|---|
| `SP-RETAIL1` | Retail-1, Ground | IEC 62053-22 or -21, tier TBD by spec-writer (§1 instrumentation doc — 0.5S vs Class 1 cost decision not yet made) | RS-485 slave → gateway → Modbus TCP |
| `SP-RETAIL2` | Retail-2, Ground | same | RS-485 slave → gateway → Modbus TCP |
| `SP-OFFICE1` | Office-1, 2nd floor | same | RS-485 slave → gateway → Modbus TCP |
| `SP-OFFICE2` | Office-2, 3rd floor | same | RS-485 slave → gateway → Modbus TCP |

Panel/feeder OCPD sizes for these 4 nodes are UNKNOWN in the as-built (not field
surveyed) and not yet computed by load-calc — so no per-tenant breaker-rating threshold
can be attached either, independent of the CT-ratio blocker.

### 2.3 Grounding electrode system (`GES-1`)

Not a metering point. No tag. Condition is UNKNOWN per as-built and requires physical
inspection, not a Modbus register. Excluded from the mimic's live-data layer entirely;
may appear as a static annotation ("condition unknown, pending field survey") on the SLD
view if the mimic renders the full topology for cross-reference purposes, but carries no
tag, no threshold, no alarm state.

### 2.4 House loads (`HOUSE-LOADS`) — explicitly excluded

Existence is **unconfirmed** per as-built (`field_verification_status`: "EXISTENCE
UNCONFIRMED"). No tag is defined for this node. If the mimic renders the full topology
for SLD cross-reference, this node must be visually marked as unconfirmed/speculative
(e.g., dashed outline, "not confirmed to exist" label) — never rendered with the same
visual weight as a confirmed, metered node. Do not silently drop it from the drawing
either; the as-built explicitly wants this open question carried forward, not erased.

### 2.5 Cross-tenant branch circuit (SP-RETAIL1 ↔ SP-RETAIL2, speculative)

Not a metering point, not a tag. This edge in `topology.json` is a flagged **risk**, not
an as-observed condition (as-built §3, risk #2 — "highest-value finding" per baseline).
It must not be drawn on the mimic as a live/solid connection. If field circuit-tracing
confirms it, that changes the topology itself (as-built revision), which flows through
this spec's §2.2 bindings before it flows into the mimic — not the other way around.

---

## 3. Tag schema

One row per Modbus-sourced measurement, per tenant node. All 4 tenant nodes (§2.2) get
an identical schema instance; only `source_node` and `tenant_id` vary.

| Field | Type | Notes |
|---|---|---|
| `tag_id` | `string` (e.g. `SP-RETAIL1.kw`) | `${source_node}.${measurement}`, stable, matches SLD node ID |
| `source_node` | `string`, one of `SP-RETAIL1`\|`SP-RETAIL2`\|`SP-OFFICE1`\|`SP-OFFICE2` | Must equal a `topology.json` node id exactly — no dashboard-local renaming |
| `tenant_id` | `uuid` (Supabase FK) | Maps node → tenant account for RLS (§6) |
| `measurement` | enum: `kwh_import` \| `kw_demand` \| `voltage` \| `current` \| `power_factor` | Per instrumentation doc §4: raw usage registers only — no `billing_amount`, no `rate_applied`, no `markup` field anywhere in this schema (§4 of this doc) |
| `unit` | enum: `kWh` \| `kW` \| `V` \| `A` \| `PF` (dimensionless 0–1) | |
| `data_type` | `number` (Zod `z.number().finite()`) | Reject NaN/Infinity at ingest boundary |
| `sample_interval_s` | `number`, e.g. 15–300 | Per instrumentation doc §3 reachability note: 15 s–5 min polling is the stated comfortable range for 4 RS-485 devices; exact interval TBD at gateway commissioning, not invented here |
| `warn_threshold` | `number \| null` | **TBD-pending-load-calc.** Must be `null` in schema/DB until load-calc publishes 80%-continuous figures per breaker. A `null` here must render as "threshold pending" on the mimic, never as "0" or "OK." |
| `alarm_threshold` | `number \| null` | **TBD-pending-load-calc.** Same rule as above — over-current alarm band, sourced only from load-calc's breaker/conductor ratings. |
| `threshold_source_ref` | `string \| null` | Once populated: citation back to the specific load-calc panel-schedule line item (e.g. `load-calc-output.md#SP-RETAIL1-branch`). Required non-null before any threshold is non-null — enforced by a check constraint, not convention. |
| `data_quality` | enum: `live` \| `stale` \| `simulated` \| `no_data` | See §4 (status semantics). `simulated` required on-screen label per project brief, not just code comment. |
| `last_read_at` | `timestamptz` | Used to derive `stale` (no update within N × `sample_interval_s`) vs `live` |

**Zod boundary sketch (illustrative only, not a build artifact for this smoke test):**

```ts
const TagReadingSchema = z.object({
  tag_id: z.string(),
  source_node: z.enum(["SP-RETAIL1", "SP-RETAIL2", "SP-OFFICE1", "SP-OFFICE2"]),
  tenant_id: z.string().uuid(),
  measurement: z.enum(["kwh_import", "kw_demand", "voltage", "current", "power_factor"]),
  unit: z.enum(["kWh", "kW", "V", "A", "PF"]),
  value: z.number().finite(),
  sample_interval_s: z.number().positive(),
  warn_threshold: z.number().nullable(),
  alarm_threshold: z.number().nullable(),
  threshold_source_ref: z.string().nullable(),
  data_quality: z.enum(["live", "stale", "simulated", "no_data"]),
  last_read_at: z.string().datetime(),
}).refine(
  (t) => (t.warn_threshold === null && t.alarm_threshold === null) || t.threshold_source_ref !== null,
  { message: "A non-null threshold must carry a load-calc citation." }
);
```

This constraint is the mechanism that stops a "reasonable-looking" threshold from
surviving a code review by accident — it is a structural guard, not a style preference.

---

## 4. Alarm/status semantics (operator-safety rule, carried from /electrical-engineer)

- Status is never color-alone: every tag rendering pairs a status dot with a text label
  (`Nominal`, `Warning — pending threshold`, `Alarm — pending threshold`, `Stale`, `No
  data`, `Simulated`).
- Until §3's `warn_threshold`/`alarm_threshold` are populated, the mimic must show a
  neutral **"Threshold pending — load-calc"** state for every tenant tag, distinct from
  both "Nominal" and "Alarm." Do not default an unset threshold to "OK."
- `no_data` and `reading 0` are visually and label-distinct (per hayah-console
  variant, dot + label required, no color-only differentiation) — a submeter reporting
  0 A during a valid off-hours period must not look like a communications failure, and a
  gateway/RS-485 dropout must not look like "load is zero."
- Simulated feed (if used before real Modbus wiring is commissioned) must carry an
  on-screen `Simulated` label at all times the feed is simulated — not only a code
  comment or a dev-only banner.

---

## 5. Direct answer — is this genuinely independent of load-calc's numeric output?

**Structurally independent, but with one real, load-bearing dependency for the part of
this deliverable that actually protects an operator — the threshold values themselves.**

What *is* independent (all defined above without touching load-calc):
- Node/tag topology bindings (§2) — these come from `topology.json` (as-built) and
  `instrumentation-procurement.md` (protocol/metering plan), neither of which needed
  load-calc, matching both agents' own routing findings.
- Tag schema shape, data types, units, Zod validation boundary (§3).
- RLS/tenant-isolation design (§6) — this is an access-control question about tenant
  accounts, not a function of any electrical rating.
- Status/alarm *semantics and rendering rules* (§4) — the rule "no color-alone,"
  "stale ≠ zero," "simulated must be labeled" holds regardless of what the numbers turn
  out to be.

What is **not** independent, and where I hit the same wall load-calc's own gap report
predicted: the `warn_threshold` / `alarm_threshold` **values** in §3 cannot exist without
load-calc's breaker/conductor ratings — not because I lack the topology, but because a
threshold is, by definition, a number derived from a demand calculation load-calc has not
run. I did not invent one. This is the one field in the whole spec that is a hard,
non-negotiable dependency rather than a shared-input soft edge (contrast: as-built and
instrumentation-procurement both reported soft edges they worked around; this one does
not resolve without load-calc's actual output).

**Practical routing implication:** this topology/tag-schema layer can proceed to
`/db-migrate` now (tag tables, RLS, ingest schema) without waiting on load-calc. The
`warn_threshold`/`alarm_threshold` columns can be created now as nullable — but must
remain `null` in every environment, including any demo/staging seed data, until
load-calc publishes real figures. Do not let a QA/demo seed script populate a "looks
right" number into those columns; that number will look identical to a real one to
anyone reading the screen later.

---

## 6. RLS / tenant data isolation — requirement for `/db-migrate`

Real constraint for the downstream build, not illustrative: **4 independent tenants
(Retail-1, Retail-2, Office-1, Office-2) must not be able to query, subscribe to, or
infer each other's tag data.** This is a hard multi-tenant isolation requirement, not a
UI-layer filter.

- Every tag/reading table carries a non-nullable `tenant_id uuid references tenants(id)`.
- RLS policy per table: `USING (tenant_id = (select tenant_id from tenant_users where
  user_id = auth.uid()))` — no table ships without this policy; no `service_role` key on
  the client per CLAUDE.md.
- An **operator/facility-manager role** needs cross-tenant visibility (the main mimic
  screen showing all 4 panels at once) — model this as a separate `role` claim
  (`operator` | `tenant`) checked in the same RLS policy, e.g. `USING (role() =
  'operator' OR tenant_id = current_tenant_id())`, not as a service-role bypass.
- Realtime (Supabase subscriptions) must respect the same RLS — verify Realtime is
  configured to enforce RLS per-channel per table, not just on initial REST reads; a
  live-tag websocket that leaks cross-tenant rows on subscribe is the same defect as a
  leaky `SELECT`.
- Historian/trend tables (if added at `/db-migrate` time for load-profile charts per
  `/dataviz`) inherit the identical `tenant_id` + RLS pattern — do not create a
  "read-only, so isolation doesn't matter" exception for historical data; tenant billing
  disputes are exactly the scenario where historical cross-tenant visibility would be
  most damaging.
- This isolation requirement is independent of load-calc too — it is a consequence of
  there being 4 separate tenant accounts on one physical service, which was already true
  in the as-built before any calc ran.

---

## 7. ERC/EPIRA billing-layer constraint — explicit, forwarded, and binding on this dashboard's design

Restating `instrumentation-procurement.md` §4 and `standards-baseline.md` §5.3 here
because this is exactly the layer where the constraint is enforced or silently violated:

- The 4 candidate submeters expose **raw interval data only** — kWh import, kW demand,
  V, A, PF — with no tariff/billing engine in firmware. Confirmed in §3 above: this
  dashboard's tag schema mirrors that same raw-usage set. There is no `billing_amount`,
  `rate_applied`, `markup_pct`, or any derived-currency field anywhere in §3.
- **This dashboard must not compute, store, or display a per-tenant bill, a markup
  percentage, or any rate-application logic.** Under EPIRA/ERC rules, resale of
  electricity at a profit is generally prohibited absent authorization, and submetered
  billings must not exceed the aggregate Meralco bill — the compliance boundary for that
  constraint lives entirely in this software layer, not in the meters. That is
  transparent usage reporting (kWh/kW/V/A/PF per tenant), full stop.
- If a future ticket asks for "tenant billing" or "cost allocation" screens, that is a
  **new, separate deliverable** requiring its own ERC/EPIRA compliance review (baseline
  §8 item 7: "ERC resale applicability — client's counsel") — it must not be added to
  this mimic as an incremental feature without that review, and it must not reuse this
  schema's tag tables to back a rate calculation without a new, explicit design pass.
- State this on-screen too, not only in this spec: any usage summary view should be
  labeled descriptively (e.g., "Usage — kWh/kW, informational only") to avoid an operator
  or tenant mistaking a usage display for a bill.

---

## 8. Drift / staleness notice for this spec itself

This spec is built on:
- `topology.json` v0.1-synthetic — **unsurveyed**, all node data ASSUMED or UNKNOWN, no
  survey date. If a real site survey changes panel IDs, feeder existence (esp.
  `HOUSE-LOADS`, the SP-RETAIL1↔SP-RETAIL2 cross-tenant edge), or panel ratings, §2 of
  this document is stale and must be re-issued before `/db-migrate` runs against it.
- `instrumentation-procurement.md` — CT ratios and final meter SKU are still blocked on
  load-calc; §2.2/§3 meter-class references are provisional shortlist entries, not final
  hardware. Any gateway model change affecting the 4-device Modbus RS-485 addressing
  scheme also requires re-issuing §2.2.
- `load-calc-gap-report.md` — a hard, not soft, blocker for §3's threshold columns (see
  §5). **No deployed dashboard build should read this spec's threshold fields as final
  until a load-calc output file exists and this spec is explicitly re-issued against it.**
  If a future build step ships with those thresholds still null-and-unlabeled (rather
  than visibly "pending"), that is itself a drift defect on the software side, not an
  engineering-layer one, and falls under `/audit`'s authority to catch.

**Affected screens if any of the above changes:** the full mimic view (all 4 tenant
panels + MP-1 aggregate), and any load-profile/trend chart built at `/db-migrate` +
build time against these tag definitions.
