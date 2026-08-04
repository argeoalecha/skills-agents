# Technical Specification — Main Panel Replacement and Tenant Submetering
## QC 3-Storey Mixed-Use Building — SYNTHETIC SMOKE TEST

**DRAFT FOR PEE REVIEW — NOT ISSUED FOR CONSTRUCTION, NOT ISSUED FOR BID.** Nothing in
this document may be represented as a bid-ready or IFC deliverable until a Professional
Electrical Engineer applies sign and seal per RA 7920 and QC DBO requirements. Every
requirement below is the sealing engineer's to adopt, modify, or reject.

**Status legend (carried from `standards-baseline.md`):** VERIFIED = confirmed against a
published source. CHECK-BOOK = article-level citation is high confidence; the exact
sub-article/table designator must be confirmed against the physical PEC 2017 Part 1
before issue. TBD-pending-load-calc = cannot be specified until `/ee-load-calc` produces
a sealed demand calculation; no number has been substituted. TBD-pending-[X] = a
different named blocker, same discipline.

**Source documents (this run):**
- `standards-baseline.md` — codes/standards citations
- `asbuilt-existing-conditions.md` — existing-conditions survey (unsurveyed, v0.1-synthetic)
- `load-calc-gap-report.md` — load-calc REFUSED; no sizing figures exist
- `instrumentation-procurement.md` — submeter/CT standard and protocol selection
- `digital-twin-spec.md` — tag schema and threshold-binding rules for the dashboard

No numeric value in Part 2 or Part 3 below was invented to fill a gap. Where a document
listed above did not supply a traceable figure, this spec states `TBD-pending-[blocker]`
explicitly rather than a plausible-looking placeholder.

---

## PART 1 — GENERAL

### 1.1 Scope of Work

1.1.1 Replacement of the existing 100 A, 230 V, single-phase main service panel (`MP-1`,
existing, ~15 years old) and associated service equipment, subject to the sizing
determination in Section 1.1.3.

1.1.2 Installation of four (4) tenant submeters (retail x2, office x2) with associated
current transformers, communications wiring, and a Modbus gateway, per the metering and
protocol selections in `instrumentation-procurement.md`.

1.1.3 **This scope explicitly excludes a predetermined outcome on service capacity.**
Per `standards-baseline.md` §1: "If the Art. 2.20 calculated demand exceeds 100 A,
'like-for-like, not capacity expansion' is not an available option." The replacement
panel's bus rating, main breaker size, and whether the existing 100 A Meralco service
remains adequate are **not yet determined** — see Part 2, Section 2.1.

1.1.4 Circuit segregation, grounding electrode system condition, and disconnect-count
compliance are field-verification items per Section 3.2, not assumptions carried into
this spec from the as-built (which surveyed nothing physically — see
`asbuilt-existing-conditions.md` §3).

1.1.5 Digital-twin/dashboard software integration (tag schema, RLS, billing-boundary
compliance) is governed by `digital-twin-spec.md` and is **not** electrical construction
scope under RA 7920 sealing — it is referenced here only where it constrains submeter
commissioning acceptance criteria (Section 3.5).

### 1.2 Related Documents

- As-built existing-conditions survey (`asbuilt-existing-conditions.md`) — governs
  existing topology, tagged ASSUMED/UNKNOWN throughout; not a verified field survey.
- Load-calculation gap report (`load-calc-gap-report.md`) — no sizing output exists.
  This spec's Products section carries the resulting gaps forward explicitly rather
  than resolving them.
- Instrumentation/metering procurement comparison (`instrumentation-procurement.md`).

### 1.3 Applicable Codes and Standards

All citations below are reproduced from `standards-baseline.md` at article level only.
**No sub-article or table designator is asserted as verified** — CHECK-BOOK items must
be confirmed against the physical PEC 2017 Part 1 before this spec is sealed or issued.

| Subject | Citation | Status |
|---|---|---|
| Governing code edition | PEC Part 1, 2017 Edition (Philippine modification of NEC 2017; NEC 2020/2023 changes not in force) | VERIFIED |
| Feeder/service demand calculation | PEC 2017 Art. 2.20 (= NEC 220) | CHECK-BOOK |
| Branch circuits, multi-occupancy | PEC 2017 Art. 2.10 (= NEC 210) | CHECK-BOOK |
| Feeder sizing, 125% continuous | PEC 2017 Art. 2.15 (= NEC 215) | CHECK-BOOK |
| Conductor ampacity + derating | PEC 2017 Art. 3.10 (= NEC 310) | CHECK-BOOK |
| Panelboard rating/construction | PEC 2017 Art. 4.8 (= NEC 408) | CHECK-BOOK |
| Service conductors/equipment | PEC 2017 Art. 2.30 (= NEC 230) | CHECK-BOOK |
| Working space / dedicated space | PEC Ch.1 general article (= NEC 110.26) | CHECK-BOOK |
| Interrupting rating ≥ available fault current | = NEC 110.9/110.10 equivalent | CHECK-BOOK |
| Available-fault-current marking | = NEC 110.24 equivalent | CHECK-BOOK |
| Ready access to OCPD (tenant) | PEC Art. 2.40 (= NEC 240.24(B)) | CHECK-BOOK |
| Branch circuits serve only the tenant supplied | PEC Art. 2.10 (= NEC 210.25(A)) | CHECK-BOOK |
| House loads not fed from a tenant panel | = NEC 210.25(B) | CHECK-BOOK |
| Neutral–EGC bonding, downstream of service disconnect | PEC Art. 2.50 (= NEC 250.24(A)(5) / 250.142) | CHECK-BOOK |
| Six-disconnect rule (2017 text; 4 tenant + 1 house = 5) | PEC Art. 2.30 (= NEC 230.71, 2017 text) | CHECK-BOOK |
| Grounding electrode system, GEC/EGC sizing, main bonding jumper | PEC 2017 Art. 2.50 (= NEC 250) | CHECK-BOOK |
| Overcurrent protection, standard breaker ratings | PEC Art. 2.40 (= NEC 240; standard ratings = NEC 240.6) | CHECK-BOOK |
| Commercial GFCI | PEC Art. 2.40 (= NEC 210.8(B), 2017 text) | CHECK-BOOK |
| Arc-flash hazard calculation methodology | IEEE 1584-2018 | VERIFIED |
| Coordination/protection-study reference series | IEEE 3002 series (supersedes IEEE 141); IEEE 3004 series (supersedes IEEE 242) | Cite 3000-series only — confirm current status before issue |
| Occupational safety, LOTO, energized-work basis (mandatory) | RA 11058 + DOLE D.O. 198-18 | VERIFIED — Philippine law, mandatory |
| Arc-flash PPE category tables (contractual, not statutory) | NFPA 70E (2024) | Not Philippine law — binding only if contractually adopted; cite as such |
| Tenant submeter accuracy class | IEC 62053-22 (baseline authorized IEC 62053-22 *or* ANSI C12.20 — IEC selected per `instrumentation-procurement.md` §1; do not cite both) | VERIFIED selection basis |
| Metering CT standard | IEC 61869-2 (supersedes IEC 60044-1) | VERIFIED selection basis |
| Sealing/licensure | RA 7920; QC DBO PEE-seal + Licensed Electrical Practitioner requirement for wiring permit | VERIFIED |
| Local permit/inspection | QC Electrical Permit + Certificate of Final Electrical Inspection (CFEI); PD 1096 + IRR | VERIFIED (statute); QC Local Building Code electrical amendments not yet obtained — OPEN |
| Fire code applicability | RA 9514 (Fire Code 2008) + IRR | Statute VERIFIED; applicability to this building OPEN |

**Not cited because not traceable this run:** UL 67 (panelboard listing standard) and
any specific enclosure IP/NEMA rating. Neither appears in `standards-baseline.md`.
Flagged in Section 2.6 rather than asserted.

### 1.4 Submittal Requirements

1.4.1 Formal load calculation (PEC Art. 2.20 basis), PEE-sealed, submitted and approved
before any panel schedule, breaker schedule, or conductor schedule is finalized. This
spec's Part 2 gaps do not close until this submittal exists.

1.4.2 Shop drawings: panelboard construction details, breaker schedule, conductor
schedule, grounding system layout, submeter/CT wiring diagram, Modbus network topology
(RS-485 segment, gateway, addressing).

1.4.3 Product data sheets for: panelboard, overcurrent devices, submeters, CTs, gateway —
each cross-referenced to the performance requirement it satisfies (Section 2), not
submitted as a substitute for that requirement.

1.4.4 Available fault current at the service point, obtained from Meralco in writing
(baseline §5.2) — submitted before breaker AIC selection is finalized. This is a
**separate blocker from load-calc** and must not be assumed resolved when load-calc
unblocks.

1.4.5 As-built revision package reconciling this installation against
`asbuilt-existing-conditions.md` / `topology.json`, including resolution of the five
open survey risks in that document's §3 (OCPD access, circuit segregation, house-load
classification, neutral–EGC bonding, disconnect count).

1.4.6 O&M manuals, warranty documentation, PEE-sealed as-built SLD and panel schedule,
per baseline §6.

### 1.5 Quality Assurance

1.5.1 Electrical plans bear the sign and seal of a Professional Electrical Engineer
(RA 7920). Wiring permit sealed by a Licensed Electrical Practitioner holding a current
PRC license, PTR, and three specimen signatures on file with QC DBO.

1.5.2 Arc-flash PPE, LOTO, and energized-work procedures follow RA 11058 / DOLE
D.O. 198-18 as the mandatory basis; NFPA 70E (2024) may be contractually adopted for
category-table detail but is not itself a legal requirement in this jurisdiction — state
this distinction in the executed contract, not just in this spec.

1.5.3 Installer qualification: Licensed Electrical Practitioner or equivalent, per QC
DBO wiring permit requirements.

### 1.6 Site Conditions

Existing conditions per `asbuilt-existing-conditions.md` are **unsurveyed** (no physical
site visit performed this run; every figure tagged ASSUMED or UNKNOWN, none VERIFIED).
The contractor's own field verification at mobilization supersedes this document's
existing-conditions assumptions and must be reconciled against `topology.json` before
demolition of any existing panel or feeder.

---

## PART 2 — PRODUCTS

### 2.1 Main Service Panel (Replacement of `MP-1`)

**HARD BLOCKED — do not fill with an assumed or "likely" value:**

| Parameter | Value | Basis / blocker |
|---|---|---|
| Main bus rating (A) | **TBD-pending-load-calc** | Requires PEC Art. 2.20 demand calculation; existing 100 A rating must not be carried forward as the design value (baseline §1: "Do not size the replacement to 100 A merely because the existing service is 100 A.") |
| Main breaker/service disconnect rating (A) | **TBD-pending-load-calc** | Same |
| Main breaker interrupting rating (AIC) | **TBD-pending-Meralco-fault-current** | Requires available fault current in writing from Meralco (baseline §5.2); this is a distinct blocker from load-calc and will not resolve merely because load-calc unblocks |
| Branch breaker sizes, all circuits (retail x2, office x2, house load if confirmed) | **TBD-pending-load-calc** | Per-tenant demand amps not yet computed |
| Number of service disconnects | **TBD-pending-field-survey** | Baseline six-disconnect rule (Art. 2.30 = NEC 230.71, 2017 text): 4 tenant + 1 house = 5 disconnects, assuming a house load exists (unconfirmed per as-built §2.4/`HOUSE-LOADS` node) |

**Specifiable now — performance requirements, not brand names:**

2.1.1 Panelboard construction and rating shall conform to PEC 2017 Art. 4.8
(= NEC 408 equivalent) [CHECK-BOOK]. Bus material, insulation, and bracing requirements
per the same article once the physical PEC 2017 designator is confirmed.

2.1.2 Working space and dedicated equipment space shall conform to the PEC Ch.1 general
article (= NEC 110.26 equivalent) [CHECK-BOOK]. **Specific clearance dimensions
(depth/width/height by condition) are not reproduced in this spec** — the baseline
explicitly declined to invent PEC table values (baseline §9: "table values are
copyrighted and deliberately not reproduced"). The installing contractor and reviewing
PEE shall confirm the applicable clearance table against the physical PEC 2017 before
rough-in layout is finalized. This is flagged, not filled.

2.1.3 Panelboard shall bear a field-applied available-fault-current marking per the
NEC 110.24 equivalent [CHECK-BOOK] once the fault-current value is obtained (Section
1.4.4).

2.1.4 **Untraceable, flagged rather than specified:** enclosure type/NEMA or IP rating,
UL 67 listing. Neither is sourced from `standards-baseline.md`. Recommend a follow-up
pass to `standards-compliance-agent` to confirm indoor commercial enclosure
classification before this subsection is finalized.

### 2.2 Conductors

2.2.1 **Type/material — specifiable now, does not require load-calc's numeric output.**
Copper conductors, insulation rated per PEC 2017 Art. 3.10 (= NEC 310 equivalent)
[CHECK-BOOK], minimum 90°C insulation rating for ampacity table lookup purposes (THHN/
THWN-2 or PEC-equivalent designation), with ampacity derated for conduit fill and
ambient temperature per the same article.

2.2.2 **Size — HARD BLOCKED.** Conductor size (AWG/mm²) for every feeder and branch
circuit: **TBD-pending-load-calc.** Requires `pec_calc_lib.py` output (`min_conductor_
ampacity()`), which requires a demand load that does not yet exist (`load-calc-gap-
report.md`).

2.2.3 **Voltage drop — HARD BLOCKED**, secondary dependency. Even after conductor size
is determined, voltage-drop percentage calculation requires conductor R/X per km data
not yet gathered (`load-calc-gap-report.md` item C.9). Flag as a second-order gap, not
resolved merely by unblocking sizing.

### 2.3 Overcurrent Protective Devices

2.3.1 Standard ampere ratings shall be selected from the PEC 2017 standard breaker step
list (= NEC 240.6 equivalent) [CHECK-BOOK] — confirmed populated and usable in
`reference/standard_breaker_ratings.md`; not itself a blocker.

2.3.2 Actual breaker ampere ratings (main and branch): **TBD-pending-load-calc**, per
Section 2.1.

2.3.3 Interrupting rating (AIC): **TBD-pending-Meralco-fault-current**, per Section 2.1.

2.3.4 GFCI protection shall be provided on circuits where required by PEC Art. 2.40
(= NEC 210.8(B), 2017 text) [CHECK-BOOK]. Specific circuits requiring GFCI protection
depend on load classification/use, which is a field-survey and load-calc joint output —
not determined in this document.

### 2.4 Grounding and Bonding

2.4.1 Grounding electrode system (GES) replacement is treated as in-scope per baseline
§3 judgment ("grounding upgrades are generally not grandfathered when service equipment
is replaced... treat GES replacement as in-scope until proven otherwise"), pending field
confirmation of existing GES condition (`GES-1`, status UNKNOWN per as-built).

2.4.2 Grounding electrode system, GEC sizing (= NEC Table 250.66 equivalent), EGC sizing
(= NEC Table 250.122 equivalent), and main bonding jumper sizing (= NEC 250.24/.28
equivalent) — all PEC 2017 Art. 2.50 [CHECK-BOOK]: **TBD-pending-load-calc**, since EGC
sizing is a function of the associated overcurrent device rating, which is itself
blocked.

2.4.3 Neutral-to-EGC bonding shall occur only at the service disconnect per PEC Art.
2.50 (= NEC 250.24(A)(5) / 250.142) [CHECK-BOOK] — no downstream re-bonding. Field
verification requirement, see Section 3.2.

### 2.5 Tenant Submetering — Specifiable in Full

2.5.1 **Metering standard.** IEC 62053-22, active energy static meters. Selected over
ANSI C12.20 per `instrumentation-procurement.md` §1 (PH distributor-market fit;
baseline §5.1 authorized either, do not cite both).

2.5.2 **Accuracy class — two-tier decision, present both to client, do not
unilaterally resolve here** (per `instrumentation-procurement.md` §1 and this spec's own
rule against silently picking a cost-bearing option):

| Tier | Accuracy class | Basis of design candidates (≥2 comparable, "or approved equal") | Note |
|---|---|---|---|
| Revenue-grade | Class 0.5S per IEC 62053-22, confirmed | SATEC PM130 PLUS (PM130E/PM130EH) | **Only one confirmed-compliant candidate identified this run** (`instrumentation-procurement.md` §5) — do not present this tier as genuinely multi-vendor-comparable until a second 0.5S-confirmed candidate (e.g., Circutor, Accuenergy Acuvim, Schneider PowerLogic PM5xxx) is researched and confirmed |
| Commodity | Class 1 per IEC 62053-21 | Schneider iEM3155 (confirm exact SKU — some variants ambiguously cite Class 0.5S), Selec MFM384 (V/I ±0.5%, but energy is Class 1) | Eastron SDM630 excluded from "or approved equal" list — PH channel is marketplace resale only, no confirmed local distributor/warranty; flag to client as import-risk if considered |

ERC/EPIRA transparency exposure (baseline §5.3) favors the tighter-accuracy tier; final
selection is a client cost-vs-accuracy decision, not an engineering default.

2.5.3 **Metering CT standard.** IEC 61869-2 (supersedes IEC 60044-1), Class 0.5(S)
split-core, consistent accuracy-class family with the meter selection.
Basis-of-design-eligible candidates (≥2): RS PRO/Siemens/Murata via RS Components
Philippines (local stock/logistics presence); Accuenergy AcuCT or GFUVE split-core
(import, factor duty/freight lead time). **CT primary ratio: TBD-pending-load-calc**
(requires per-tenant demand amps; rule of thumb from procurement doc, not to be applied
before real data exists: CT primary ≈ 1.0–1.25× tenant demand amps, not the tenant
subpanel breaker rating).

2.5.4 **Communication protocol.** Modbus RTU over RS-485, 4 tenant meters daisy-chained
to a single Modbus RTU→TCP gateway at `MP-1`; gateway exposes Modbus TCP to the
dashboard data layer. Selected as the protocol common to all candidate meter families
across both accuracy tiers (`instrumentation-procurement.md` §3). BACnet/IEC 61850 not
selected as primary — no BMS exists at this site per the as-built; a Modbus→BACnet
gateway may be added downstream without re-wiring the meters if a future BMS
integration is required.

2.5.5 Polling interval: 15 seconds to 5 minutes, comfortably within Modbus RTU RS-485
throughput at 9600–38400 baud for 4 devices per `instrumentation-procurement.md` §3.
Sub-second polling shall not be specified — not needed for tenant billing visibility.

2.5.6 Raw usage registers only (kWh import, kW demand, V, A, PF). No meter, gateway, or
downstream schema element shall implement or expose a billing-amount, rate-applied, or
markup field — required for consistency with the ERC/EPIRA constraint carried in
`digital-twin-spec.md` §7 (software-layer compliance boundary; meter selection alone
does not satisfy this constraint).

### 2.6 Enclosures / Environmental Rating

**Flagged, not specified.** No enclosure IP or NEMA rating, and no ambient-temperature/
environmental service condition for the submeter/gateway enclosure, is cited in any
source document for this run. Recommend confirming with `standards-compliance-agent`
(indoor commercial panel room assumed, but not stated in the as-built) before this
subsection is finalized. Do not read "indoor" as verified — the as-built does not state
whether `MP-1` sits in a dedicated electrical room, a corridor, or an exterior-adjacent
space.

---

## PART 3 — EXECUTION

### 3.1 Installation — General

3.1.1 Installation by a Licensed Electrical Practitioner per QC DBO wiring permit
requirements (Section 1.5.1).

3.1.2 Working space and dedicated equipment space per Section 2.1.2 — contractor to
confirm actual clearance dimensions against the physical PEC 2017 before rough-in;
this spec does not supply those dimensions.

3.1.3 No conductor, breaker, or panel bus installed under this contract shall be sized
by field judgment where Part 2 states TBD-pending-load-calc. Installation of those
components shall not proceed until the PEE-sealed load calculation and resulting panel
schedule (Section 1.4.1) exist and this spec section is reissued against them (see
Section 3.9).

### 3.2 Field Verification of Survey Risks (Testable, Pre-Demolition)

Each item below is a baseline-flagged risk that `asbuilt-existing-conditions.md`
could not confirm without a physical site visit (that document's §3). These become
mandatory, testable field-verification steps under this contract, performed before
existing panels/feeders are demolished:

| # | Verification | Test method | Acceptance criterion |
|---|---|---|---|
| 1 | Each tenant has ready access to their own OCPD | Physical walk of each tenant space; locate subpanel relative to leased area | Subpanel accessible from within tenant's leased space or designated common corridor per PEC Art. 2.40 (= NEC 240.24(B)) — pass/fail, documented with photo per panel |
| 2 | Tenant branch circuits supply only that tenant | Breaker-off test at each subpanel; confirm which downstream devices de-energize | Zero cross-tenant de-energization observed at any breaker-off test — pass/fail per circuit, logged in a circuit-trace record |
| 3 | House loads not supplied from a tenant panel | Trace common-area/signage/fire-life-safety loads (if any exist) to their supply point | Any confirmed house load traces to a dedicated house disconnect, not a tenant subpanel — pass/fail; if no house load is confirmed to exist, record that finding explicitly (do not leave silent) |
| 4 | Neutral not re-bonded downstream of service disconnect | Open each subpanel; inspect neutral bus isolation from ground/EGC | Neutral bus isolated from EGC/ground at every point downstream of the service disconnect — pass/fail per panel |
| 5 | Disconnect count (six-disconnect rule) | Count actual service disconnecting means at `MP-1` | Disconnect count consistent with PEC Art. 2.30 (= NEC 230.71, 2017 text) once house-load existence (item 3) is resolved |

Findings from this section supersede `asbuilt-existing-conditions.md` §3 and require an
as-built revision (Section 1.4.5) before substantial completion.

### 3.3 Grounding System

3.3.1 Grounding electrode system condition assessment (excavation/inspection or, at
minimum, visual GEC trace from `MP-1`) — required before design finalization of GES
replacement scope (Section 2.4.1).

3.3.2 Ground resistance test, performed and recorded after GES installation/
verification. **Acceptance threshold: TBD-pending-PEE-design.** No numeric maximum
resistance value is cited in `standards-baseline.md` for this installation; a commonly
cited NEC single-rod-electrode figure (25 Ω, NEC 250.53(A)(2)) exists but is not
confirmed as the applicable PEC 2017 value for this site's electrode configuration, and
is therefore not asserted here. The sealing PEE shall establish the acceptance value at
design stage based on the final GES configuration and any available soil-resistivity
data.

### 3.4 Overcurrent Devices and Conductors — Commissioning

3.4.1 Insulation resistance and continuity testing on all conductors before
energization. **Test voltage and pass/fail threshold: TBD-pending-PEE-design** — not
specified here; no source document supplies a verified figure for this installation's
voltage class.

3.4.2 Breaker/panel commissioning (torque verification, bus connection inspection,
labeling) proceeds only after Section 2.1/2.2/2.3 TBD items are resolved by the
PEE-sealed panel schedule.

### 3.5 Tenant Submetering — Commissioning (Fully Testable Now)

This subsection is not blocked by load-calc — it tests the metering/communications
layer selected in Section 2.5, independent of any breaker or conductor sizing.

| Step | Test method | Acceptance criterion |
|---|---|---|
| Modbus addressing | Query each of the 4 meters at its configured RTU slave address via the gateway | All 4 addresses respond uniquely; no duplicate slave IDs on the RS-485 segment |
| RS-485 physical layer | Verify termination and bias resistor configuration at bus ends | Bus terminated per gateway/meter manufacturer instructions; no communication errors over a sustained 30-minute poll cycle |
| Gateway protocol translation | Poll all 4 meters via Modbus TCP from the dashboard data layer | Live readings (kWh, kW, V, A, PF) received from all 4 tenant nodes at the configured poll interval (15 s–5 min, Section 2.5.5), matching `topology.json` node IDs (`SP-RETAIL1`, `SP-RETAIL2`, `SP-OFFICE1`, `SP-OFFICE2`) exactly |
| Reading accuracy spot-check | Independent clamp-meter measurement at each tenant subpanel, compared against the corresponding submeter's live reading | Deviation within the stated accuracy class tolerance of the installed meter tier (0.5S or Class 1 per Section 2.5.2) — record both readings, not just pass/fail |
| Tag/node binding verification | Confirm each submeter's physical panel label matches its `tenant_id` and `source_node` binding in the dashboard schema | 1:1 match, no cross-wired tenant, verified against `digital-twin-spec.md` §3 schema and physical panel labeling |
| ERC/EPIRA compliance check | Inspect dashboard usage screens and underlying schema | No billing-amount, rate-applied, or markup field present or populated anywhere in the commissioned system, per `digital-twin-spec.md` §7 |
| Threshold-field state | Inspect `warn_threshold`/`alarm_threshold` fields in the commissioned system | Both fields `null` with a "Threshold pending — load-calc" state rendered on the dashboard for all 4 tenant tags — a populated (non-null) value at commissioning without a `threshold_source_ref` citation is a commissioning FAILURE, not an acceptable default |

### 3.6 Arc-Flash and Electrical Safety

3.6.1 Arc-flash hazard calculation methodology, if performed, shall follow IEEE
1584-2018 [VERIFIED].

3.6.2 Per baseline judgment (not code): at the scale of this installation
(~23 kVA single-phase existing service; exact figure pending load-calc), a formal
protection-coordination (TCC) study is likely unwarranted — the relevant question is
series-rating/interrupting-rating adequacy, not time-current coordination. **This
determination is provisional** and shall be reconfirmed once the actual demand load and
Meralco fault-current figure are known (Sections 2.1, 1.4.4) — do not treat "study not
required" as final until those figures exist.

3.6.3 PPE, LOTO, and energized-work procedures per RA 11058 / DOLE D.O. 198-18
(mandatory) [VERIFIED]; NFPA 70E (2024) category tables applied only if contractually
adopted — state this in the contract, not assumed from this spec alone.

### 3.7 Acceptance Criteria — Summary (Testable, Not Aspirational)

The installation shall not be presented for substantial completion or CFEI application
until:

1. PEE-sealed load calculation and panel schedule exist, and all Part 2 TBD items in
   Sections 2.1–2.4 are resolved against that sealed output (no field-substituted
   values).
2. All five field-verification items in Section 3.2 are documented pass/fail, with
   findings folded into an as-built revision.
3. Ground resistance test recorded against a PEE-established threshold (Section 3.3.2).
4. All six submetering commissioning checks in Section 3.5 pass, including the
   threshold-field-null check.
5. Available fault current obtained from Meralco in writing and breaker AIC selection
   confirmed against it (Section 1.4.4, Section 2.1).
6. QC DBO Certificate of Final Electrical Inspection issued.

"Shall be suitable for the intended application" does not appear anywhere in this
document as an acceptance criterion — every item above is pass/fail or a recorded
measured value.

### 3.8 Documentation Handoff

Final as-built SLD, panel schedule, load calculation/basis of design, and this spec
package — each PEE-sealed — per baseline §6, before the project is presented as
IFC-equivalent to any party.

### 3.9 Sections Requiring Revision When Load-Calc / Procurement Outputs Change

Per this pipeline's drift-prevention rule, the following sections are explicitly named
as **stale on arrival of new sizing data** and must be revised before reuse, not
silently left as-is:

- **Section 2.1** (main bus rating, main breaker, branch breaker sizes, disconnect
  count) — revise on `/ee-load-calc` output.
- **Section 2.1** (AIC/interrupting rating) and **Section 2.3.3** — revise on receipt of
  Meralco's written fault-current figure (separate trigger from load-calc).
- **Section 2.2** (conductor sizes, voltage drop) — revise on `/ee-load-calc` output.
- **Section 2.4.2** (GEC/EGC/bonding jumper sizing) — revise on `/ee-load-calc` output
  (EGC size is a function of the associated OCPD rating).
- **Section 2.5.3** (CT primary ratio) — revise on `/ee-load-calc` per-tenant demand
  amps.
- **Section 2.5.2** (accuracy-class tier decision) — revise if the client selects a
  tier, or if a second 0.5S-confirmed candidate is added to the procurement comparison.
- **Section 3.2** — revise if field verification finds a cross-tenant circuit
  crossing, a confirmed house load, or a neutral-bonding defect; any of these change
  `topology.json` and cascade to `digital-twin-spec.md` §2.
- **Section 3.3.2 / 3.4.1** — revise once the PEE establishes numeric test thresholds
  at design stage; currently unspecified by design, not by omission.

`/ee-audit` should treat any of the above sections as a drift flag if a newer
load-calc, procurement, or fault-current document exists in this project folder without
a corresponding spec-package revision.

---

## Traceability Note — Values This Document Could Not Trace

Per this agent's own operating rule ("every numeric requirement must trace back to
load-calc output or a standards-compliance-agent citation... flag any spec value you
can't trace"), the following are explicitly **not specified** rather than filled in:

1. Main bus rating, main/branch breaker sizes, conductor sizes, voltage drop, GEC/EGC/
   bonding jumper sizes, CT ratio — all trace to the load-calc gap, not fabricated.
2. Breaker AIC / interrupting rating — traces to the separate, still-open Meralco
   fault-current request, not load-calc.
3. Working-space clearance dimensions (Section 2.1.2) — the baseline article citation
   is CHECK-BOOK but no numeric table value was supplied by any upstream document;
   this spec does not invent NEC's typical 900 mm/1000 mm/1200 mm figures as PEC
   values without confirmation.
4. Enclosure IP/NEMA rating, UL 67 listing (Section 2.6) — no source document in this
   run cites either; flagged as a genuine research gap, not assumed "standard practice."
5. Insulation-resistance test voltage/threshold, ground-resistance acceptance value
   (Sections 3.3.2, 3.4.1) — no verified figure exists in the source set for this
   site's configuration; left to PEE design-stage determination.
6. GFCI-required circuit list (Section 2.3.4) — the article citation is traceable; the
   specific circuits requiring it are not, pending load classification.

---

## Direct Answer — Did Products Hit the Predicted Hard Wall?

**Yes on the core numeric triad, but the wall has more structure than a single blanket
"Products is blocked" finding would suggest — more was draftable than the minimum
expected, and the blocked items split into two distinct blockers, not one.**

- **Confirmed hard-blocked, exactly as expected:** main bus rating, main/branch breaker
  ampere sizes, and conductor sizes (Sections 2.1, 2.2.2) — none of these could be
  specified without `/ee-load-calc`'s demand-calculation output. This matches every
  upstream agent's own finding pattern for the parts of their scope that touch actual
  sizing numbers.
- **A second, independent blocker was found within "Products," not collapsed into
  load-calc:** breaker interrupting rating (AIC) does not depend on load-calc at all —
  it depends on Meralco's written fault-current figure (baseline §5.2), a separate open
  item. Treating "load-calc unblocks Products" as sufficient would be wrong; AIC stays
  blocked even after load-calc runs, until Meralco responds. This is flagged explicitly
  in Sections 2.1, 2.3.3, and 3.9 so it isn't silently conflated with the load-calc gap.
- **More was draftable than the framing anticipated:** conductor *type/material*
  (copper, 90°C-rated insulation per Art. 3.10) is fully specifiable without load-calc —
  only conductor *size* is blocked. Panelboard construction standard (Art. 4.8),
  available-fault-current marking requirement (procedural, not the value itself), GFCI
  applicability citation, and grounding-in-scope judgment (Section 2.4.1) were also
  draftable as performance requirements even though their associated numeric values are
  not.
- **The submetering/CT half of Products (Section 2.5) drafted in full**, exactly as the
  instrumentation-procurement document predicted for itself — standard, accuracy-tier
  options, protocol, and CT standard are all specified; only the CT ratio is
  load-calc-blocked, consistent with that document's own finding.
- **One item flagged as untraceable that wasn't anticipated by the task framing at
  all:** enclosure IP/NEMA rating and UL 67 listing (Section 2.6) — genuinely absent
  from every upstream document, not a load-calc dependency, a plain research gap.

Net: Products did hit a real, hard, load-calc-specific wall on bus rating, breaker
sizing, and conductor sizing — that part of the expectation held. But calling the whole
section "blocked" would have been an overstatement; roughly half of Part 2 by line
count was draftable, and the blocked half turned out to be two distinct blockers
(load-calc and Meralco fault current) that this document keeps visibly separate so a
future reviewer doesn't assume both resolve on the same trigger.
