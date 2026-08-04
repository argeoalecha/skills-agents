# Instrumentation & Metering Procurement — Tenant Submetering
## QC 3-Storey Mixed-Use, 4 Tenants — SYNTHETIC SMOKE TEST

**Draft, budgetary, indicative. Not a spec, not a BOQ. Research date: 2026-08-04.**
Feeds `spec-writer-agent` (spec language) and `digital-twin-agent` (protocol/polling
reachability). This document does not select CT ratios or meter current ranges — see
§0 Scope Limit.

---

## 0. Scope limit — what could NOT be done this run, and why

`/ee-load-calc` refused to run (`load-calc-gap-report.md`) — no demand-load figures
exist for any of the 4 tenants (retail x2, office x2) or the aggregate service.
Per the task boundary and per this pipeline's own rule (CT ratios/meter ranges must be
sized against actual demand loads, not nameplate), **no CT ratio and no meter current
rating are selected in this document.** Doing so would require inventing a tenant
amperage figure, which is exactly the failure mode the upstream refusal exists to
prevent.

What follows is standard/accuracy-class selection, protocol selection, and a
**class-of-product** shortlist (types and accuracy tiers suitable for a 4-tenant, ~100 A
aggregate installation) — not tenant-specific model/CT selections. Once load-calc
produces per-tenant demand amps, re-run this research to pick actual CT ratios (rule of
thumb to re-apply then, not applied now: CT primary ≈ 1.0–1.25× tenant demand amps, not
the tenant subpanel's breaker rating).

---

## 1. Metering accuracy standard — decision

**Selected: IEC 62053-22, Class 0.5S** (active energy, static meters). Not ANSI C12.20.

**Rationale:**
- Baseline §5.1 authorized picking either ANSI C12.20 or IEC 62053-22 — both are valid,
  don't cite both.
- The PH commercial electrical distributor market (Schneider Electric Philippines,
  RS Components PH, and the general panel-builder supply chain) stocks IEC-compliant
  DIN-rail meters and CTs as the default catalog line. ANSI C12.20 meters are
  predominantly a US utility-revenue-metering product segment with materially thinner
  PH distributor presence — none of the three vendors researched below (Schneider,
  SATEC, Selec) markets a C12.20-primary product to this region; Schneider and Selec
  datasheets cite IEC 62053-21/22 as primary, ANSI C12.20 only as a secondary
  cross-reference on some models ([Schneider iEM3155 datasheet](https://iportal2.schneider-electric.com/Contents/docs/SQD-A9MEM3155_DATASHEET.PDF); [SATEC PM130 PLUS datasheet](https://www.satec-global.com/wp-content/uploads/2022/11/PM130_PLUS_DATASHEET.pdf)).
- This matches PEC 2017's own posture (§0 of baseline): PEC is NEC-derived for wiring
  methods, but the PH electrical equipment supply chain is IEC-standard for
  instrumentation — there is no requirement to force an ANSI metering standard onto a
  PEC-governed installation.

**Flag for spec-writer — datasheet disagreement with baseline's assumed class.**
Baseline §5.1 states "ANSI C12.20 (class 0.2/0.5) *or* IEC 62053-22 (class 0.2S/0.5S)."
That's correct as a citation, but **not every commercially available submeter in this
price/size class actually meets 0.5S**. Verified this run:
- Schneider iEM3155/iEM3000 series: energy accuracy is **Class 1 per IEC 62053-21**
  (the *lower*-accuracy standard for static meters), with one datasheet variant citing
  "IEC 62053-21/22 Class 1 and Class 0.5S" ambiguously across model variants —
  confirm the exact SKU before spec commitment ([datasheet](https://iportal2.schneider-electric.com/Contents/docs/SQD-A9MEM3155_DATASHEET.PDF)).
- Eastron SDM630: energy accuracy is **Class 1 per IEC 62053-21 / Class B per
  EN 50470-1/3** — does **not** meet 62053-22 Class 0.5S ([datasheet/manual](https://enertik.com/wp-content/uploads/sites/2/documentos/manuales/manual-12-420002-01g.pdf)).
- SATEC PM130 PLUS (PM130E/PM130EH variants): **Class 0.5S per IEC 62053-22**, confirmed
  ([datasheet](https://www.satec-global.com/wp-content/uploads/2022/11/PM130_PLUS_DATASHEET.pdf)).
- Selec MFM384: voltage/current at ±0.5%, but **active/reactive/apparent energy is
  Class 1**, not 0.5S ([datasheet](https://www.selec.com/us/en/viewdocument/2387337ba1e0b0249ba90f55b2ba2521)).

**Implication:** if the client/spec-writer holds the line at 0.5S (justified by the
ERC/EPIRA transparency requirement, §4 below — tighter accuracy reduces billing-dispute
exposure), the shortlist narrows to SATEC-tier instruments and pulls the budget up
materially versus the Schneider/Eastron/Selec DIN-rail commodity tier, which is Class 1.
This is a real cost-vs-accuracy decision for spec-writer to make explicitly, not a
detail to silently resolve here. **Class 1 (IEC 62053-21) is the realistic accuracy
tier for a commodity 4-tenant submetering retrofit at this building scale**; Class 0.5S
is achievable but is a step up in both cost and sourcing difficulty. Recommend
spec-writer present both tiers to the client rather than pick one unilaterally.

---

## 2. Metering CT standard — decision

**Selected: IEC 61869-2** (supersedes IEC 60044-1), not IEEE C57.13.

**Rationale:** same PH-market IEC-default logic as §1; consistent standard family
alongside the IEC 62053-22 meter selection avoids mixing ANSI/IEC accuracy-class
terminology in the same spec package. Split-core CT product lines carrying IEC 61869-2
Class 0.5(S) compliance are available from RS Components Philippines and international
manufacturers (Accuenergy, GFUVE, FLEX-CORE) that ship to PH — see §3 for import
implications ([RS PH current transformers](https://ph.rs-online.com/web/c/automation-control-gear/process-control/current-transformers/?pn=2); [Accuenergy AcuCT split-core](https://www.accuenergy.com/products/acuct-5a-split-core-current-transformers/)).

**Blocked, not decided:** CT primary current ratio. Cannot be sized until load-calc
produces per-tenant demand amps (§0).

---

## 3. Communication protocol for remote read — decision

**Selected: Modbus RTU over RS-485, daisy-chained from the 4 tenant meters to a single
Modbus RTU→TCP gateway at the main panel; gateway exposes Modbus TCP to the digital-twin
dashboard's data layer.**

**Rationale:**
- Every candidate meter researched (Schneider iEM3000/3100/3155, Eastron SDM630,
  Selec MFM384, SATEC PM130 PLUS) natively supports Modbus RTU over RS-485 as its
  standard/base communication option — this is the single protocol common to all
  candidates across all three accuracy/price tiers, which keeps the vendor shortlist
  genuinely comparable (rule requirement: ≥2 comparable options per class) rather than
  protocol-locking to one vendor's proprietary option.
- RS-485 multidrop is well suited to 4 meters at one building — one twisted-pair run
  daisy-chained panel-to-panel to MP-1, terminated at a gateway, is standard commercial
  submetering topology and avoids running 4 separate long cable pulls.
- BACnet (IEC 61850 does not apply — that's a substation/utility protection-relay
  protocol, not appropriate for commercial tenant submetering at this scale) was
  evaluated and **not selected** as the primary field protocol. No BACnet BMS exists at
  this site per the as-built (no BMS is mentioned anywhere in the existing-conditions
  survey) — introducing BACnet would add a gateway/translation layer with no consuming
  system on the other end. If a future BMS integration is required, a Modbus→BACnet
  gateway (e.g., Chipkin, Intesis) can be added downstream of the RS-485 bus without
  re-wiring the meters — this preserves the option without over-building it into the
  submetering scope now.
- **Reachability check for digital-twin-agent:** confirm the intended gateway model
  supports Modbus RTU master polling of 4 slave addresses on one RS-485 segment at a
  polling interval the dashboard actually needs (typical commercial submetering:
  15-second to 5-minute polling is comfortably within Modbus RTU RS-485 throughput at
  9600–38400 baud for 4 devices; sub-second polling is not needed for tenant billing
  visibility and should not be spec'd). This is a check digital-twin-agent must perform
  against its actual gateway hardware — not assumed here.

---

## 4. ERC/EPIRA constraint — forwarded requirement, not a spec

Standards baseline §5.3 (VERIFIED existence, OPEN as to application; not legal counsel):
resale of electricity at a profit is generally prohibited under EPIRA/ERC rules absent
authorization; submetered billings must reflect the actual DU rate and must not exceed
the aggregate Meralco bill; **the dashboard must not ship a billing feature implying
markup capability.**

**Instrumentation-layer consequence, flagged forward for digital-twin-agent and
spec-writer-agent:** all four candidate meter families (Schneider, Eastron, Selec,
SATEC) expose raw interval data over Modbus registers — kWh (import/export), kW demand,
V, A, PF — with **no built-in tariff/billing-calculation engine in the meter firmware
itself**; rate application and bill calculation happen entirely in whatever software
layer reads the Modbus data. This means the instrumentation choice is compatible with
the constraint by default (the meter reports usage transparently; it does not compute a
bill), but it also means **the constraint's actual compliance boundary lives entirely in
the dashboard/software layer**, not in the meter selection. Spec-writer should not treat
meter procurement as having satisfied this requirement — it hasn't; it's a necessary but
not sufficient condition. Digital-twin-agent's dashboard design is where this
requirement actually gets enforced or violated.

---

## 5. Comparison table — candidate submeters (class of product, not tenant-sized)

| Requirement | Candidate models | Key specs | Est. cost/lead time | Source |
|---|---|---|---|---|
| Tenant submeter, commodity tier (Class 1, IEC 62053-21/-22 mixed per SKU) | Schneider Electric iEM3155 (A9MEM3155) | 3-phase, direct-connect up to 63 A (no CT for this tier — verify vs. actual tenant amps once load-calc unblocks), Modbus RTU RS-485, active energy Class 1 IEC 62053-21 (some SKU variants cite Class 0.5S per 62053-22 — confirm exact part number), MID certified | Budgetary, PH list ~US$150–250 equiv./unit range typical for this DIN-rail class; **local stock via Schneider Electric Philippines partner network** — no import wait if in-country stock; indicative only, not a formal quote, priced 2026-08-04 | [Schneider iEM3155 datasheet](https://iportal2.schneider-electric.com/Contents/docs/SQD-A9MEM3155_DATASHEET.PDF); [Schneider PH product page](https://www.se.com/ph/en/product/A9MEM3100/iem3000-energy-meter-63-a/); [Schneider PH distributor locator](https://www.se.com/ph/en/partners/distributors/) |
| Tenant submeter, commodity tier (Class 1, IEC 62053-21) | Eastron SDM630-Modbus V2 | 3-phase via CT (CT ratio TBD post-load-calc), Modbus RTU RS-485, active energy Class 1 IEC 62053-21 / Class B EN 50470-1/3, does not meet 62053-22 0.5S | Budgetary, low-cost tier (~US$40–90 equiv./unit typical for this brand class) — **but PH availability found only via Lazada/Ubuy marketplace resale, not a formal Eastron PH distributor or local rep.** This is an import-adjacent channel: no confirmed local warranty support, unclear duty/lead-time handling on marketplace orders, and grey-market risk on a commercial procurement. Flag explicitly to spec-writer/client before use. Priced 2026-08-04, indicative | [Eastron SDM630 V2 manual](https://enertik.com/wp-content/uploads/sites/2/documentos/manuales/manual-12-420002-01g.pdf); [PH marketplace listing example](https://www.lazada.com.ph/tag/eastron-meter-sdm120/) |
| Tenant submeter, commodity tier (Class 1 energy / 0.5% V-I) | Selec MFM384 | 3-phase, CT-input (5A secondary, ratio TBD post-load-calc), Modbus RTU RS-485, V/I accuracy ±0.5%, active/reactive/apparent energy Class 1, CE/RoHS/UL/MID certified | Budgetary, mid-low tier; **no confirmed Philippines-specific distributor or local rep found this run** — Selec's dealer network located this run is India-centric; treat as import unless a PH rep is confirmed directly with Selec. Indicative, priced 2026-08-04 | [Selec MFM384 datasheet](https://www.selec.com/us/en/viewdocument/2387337ba1e0b0249ba90f55b2ba2521) |
| Tenant submeter, revenue-grade tier (Class 0.5S, IEC 62053-22 — confirmed) | SATEC PM130 PLUS (PM130E / PM130EH) | 3-phase, CT-input, active energy **Class 0.5S per IEC 62053-22 (confirmed, not ambiguous)**, also cites ANSI C12.20-1998 class 0.5 cross-reference, RS-485 standard + optional Ethernet/Modbus TCP second port, operating temp -30°C to 60°C, TOU + daily profile logging | Budgetary, premium tier — meaningfully higher unit cost than the three commodity candidates above (SATEC is positioned as a utility/revenue-grade instrument, not a DIN-rail commodity meter); **no PH-specific distributor identified this run — likely import via SATEC's regional (APAC) channel**, implying longer lead time and support routed through a regional rep rather than a walk-in PH stockist. Indicative, priced 2026-08-04 | [SATEC PM130 PLUS datasheet](https://www.satec-global.com/wp-content/uploads/2022/11/PM130_PLUS_DATASHEET.pdf); [SATEC PM130 PLUS product page](https://www.satec-global.com/products/pm130-plus/) |
| Metering CT (class per §2, ratio blocked) | RS PRO / Siemens / Murata split-core CTs via RS Components Philippines | IEC 61869-2, Class 0.5(S) split-core options, multiple window sizes, 1A/5A secondary outputs — **primary ratio NOT selected, blocked on load-calc (§0)** | RS Components PH has local e-commerce/logistics presence — not a grey-market import, but confirm individual CT model stock vs. made-to-order lead time at ratio-selection stage | [RS PH current transformers](https://ph.rs-online.com/web/c/automation-control-gear/process-control/current-transformers/?pn=2) |
| Metering CT (class per §2, ratio blocked) | Accuenergy AcuCT split-core, GFUVE split-core | IEC 61869-2 / IEC 60044-1 (superseded, but GFUVE still cross-references it) compliant, Class 0.5(S) split-core options | Both are import from manufacturer (Accuenergy — Canada/China; GFUVE — China); no PH distributor confirmed this run — treat as import, factor duties + freight lead time into any BOQ | [Accuenergy AcuCT](https://www.accuenergy.com/products/acuct-5a-split-core-current-transformers/); [GFUVE split-core CT](https://www.gfuve.com/split-core-current-transformer/) |

**Single-vendor flag:** none of the rows above is sole-source — every requirement row
has ≥2 candidates. The Class 0.5S-confirmed row (SATEC) currently has only one
confirmed-compliant model identified this run; a second 0.5S-confirmed candidate
(e.g., Circutor, Accuenergy Acuvim, or a Schneider revenue-grade line such as
PowerLogic PM5xxx) should be researched in a follow-up pass before spec-writer treats
0.5S as a two-vendor-comparable tier — **flagging this as a single-candidate gap in the
0.5S tier specifically**, not a general single-vendor recommendation for the whole
submetering scope.

---

## 6. Direct answer to the routing question

**Is protocol/standard selection genuinely independent of load-calc's output, or did
you hit a real dependency partway through?**

**Genuinely independent — confirmed, not just assumed, and no soft edge was hit this
time (contrast with as-built-agent, which flagged one shared-input soft edge).**

- The accuracy standard (§1), CT standard (§2), and communication protocol (§3) are all
  properties of *which instrument class exists in the market and what it natively
  speaks* — none of that changes based on how many amps a tenant draws. A Class 0.5S
  meter is Class 0.5S whether it reads 5 A or 80 A; Modbus RTU RS-485 is Modbus RTU
  RS-485 regardless of tenant load magnitude.
- The one place load magnitude *would* matter — CT ratio and meter current-range model
  selection — was correctly excluded from this document (§0) rather than guessed at.
  That's the same boundary load-calc's refusal already drew; this document didn't need
  to cross it to do everything else asked.
- **Routing implication for orchestrator-scope:** instrumentation-procurement's
  standard/protocol/vendor-shortlist work does **not** need to wait in the queue behind
  load-calc the way CT/meter sizing does. If the pipeline is currently gating this
  entire agent behind load-calc's output, that's stricter than necessary — same finding
  pattern as as-built-agent reported for existing-conditions documentation. The
  CT-ratio/meter-range half of this agent's scope remains correctly blocked; the
  standard-selection half was never blocked and should be allowed to run in parallel
  with load-calc, not serialized after it.

---

## 7. Outstanding blockers, restated for this document

1. Tenant demand amps (all 4 tenants) — blocks CT ratio and meter current-range
   selection specifically. Everything else in this document is unblocked and complete.
2. Class 0.5S tier has only one confirmed-compliant candidate (SATEC) this run — needs
   a second comparable candidate before spec-writer relies on it as a genuinely
   compared tier.
3. Eastron and Selec PH distribution channels not confirmed as formal local reps this
   run — treat both as import-risk until a direct vendor confirmation exists.
4. BACnet/BMS integration was evaluated and deliberately not selected as primary — if
   a BMS surfaces later in the project that wasn't visible in the as-built, revisit §3.
