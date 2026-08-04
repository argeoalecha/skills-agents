# As-Built — Existing Conditions Only
## QC 3-Storey Mixed-Use Building — SYNTHETIC SMOKE TEST

**DRAFT FOR PEE REVIEW. Not issued for construction. Not sealed.** Nothing in this
document may be represented as IFC or code-compliant documentation until a PEE applies
sign and seal per RA 7920 / QC DBO requirements (standards-baseline.md Sec.6).

**Document status:** first-ever as-built for this installation (no prior as-built exists
per stated site data).

**Version:** 0.1-synthetic
**Document generation date:** 2026-08-04
**Site survey date:** NONE — no physical site survey was performed for this run.

> This drawing set is **not properly versioned against a survey date**, because no survey
> occurred. It is versioned only against the date this synthetic dataset was drafted. Per
> the as-built documentation standard this pipeline holds itself to, an as-built without a
> survey date is undated evidence about a system that changes — treat this entire document
> as provisional pending a real survey, not as a substitute for one. Every downstream
> consumer (digital-twin-agent, spec-writer-agent) must carry this caveat forward.

All data below originates from a synthetic scenario description provided for this smoke
test, not from field measurement. Every figure is tagged **[ASSUMED]** (stated as given
site data, not observed) or **[UNKNOWN]** (a field survey would be required to determine
it, and none has been performed). No figure in this document is tagged VERIFIED — that
tag is reserved for data a field engineer actually confirmed on site, and none exists yet.

---

## 1. Single-line diagram — structural description

No image tooling was used; this is the node/connection structure a drafter would render
as the SLD. See `topology.json` in this same folder for the machine-readable version —
IDs here are stable and match that file and should be reused verbatim by
`digital-twin-agent`.

```
UTIL-SVC (Meralco service point, 230V 1-phase)
   │  [service conductors — size/type ASSUMED not stated, routing UNKNOWN]
   ▼
MP-1 (existing main panel, 100A 230V 1-phase, ~15 yrs old) [ASSUMED rating/age]
   │
   ├──(GEC, size/routing UNKNOWN)──► GES-1 (grounding electrode system) [UNKNOWN condition]
   │
   ├──(feeder, size/OCPD UNKNOWN)──► SP-RETAIL1  (Ground floor, ~80 sqm, unmetered)
   ├──(feeder, size/OCPD UNKNOWN)──► SP-RETAIL2  (Ground floor, ~80 sqm, unmetered)
   ├──(feeder, size/OCPD UNKNOWN)──► SP-OFFICE1  (2nd floor, ~100 sqm, unmetered)
   ├──(feeder, size/OCPD UNKNOWN)──► SP-OFFICE2  (3rd floor, ~100 sqm, unmetered)
   └──(existence UNCONFIRMED)──────► HOUSE-LOADS (possible common-area/house load,
                                       not confirmed to exist — see Sec.3)
```

Dashed/speculative element in the machine-readable topology only (not drawn as a solid
line on any rendered SLD until confirmed): a possible cross-tenant branch circuit between
SP-RETAIL1 and SP-RETAIL2, included solely to flag that circuit segregation has not been
traced in the field. Do not render this as an observed condition.

**Node ID stability notice for digital-twin-agent:** `MP-1`, `SP-RETAIL1`, `SP-RETAIL2`,
`SP-OFFICE1`, `SP-OFFICE2`, `UTIL-SVC`, `GES-1` are the panel/feeder IDs to reuse verbatim
in the dashboard mimic. Do not rename after this point.

---

## 2. Panel schedule — existing conditions

**This is not a replacement panel schedule.** It contains no breaker sizes, conductor
sizes, or demand loads, because those are load-calc outputs and `/ee-load-calc` refused
to run (see `load-calc-gap-report.md` — `demand_factors.md` is an unpopulated stub).
Per the operating rule for this pipeline, panel schedules must match load-calc's output
exactly and must never be re-derived here — since load-calc produced no output, no such
figures appear below. This is a **documentation-of-what-exists** table, not a design
table.

| Panel ID | Description | Floor | Area (sqm) | Rating (A) | Age | Metering | Main breaker | Branch inventory | Circuit directory |
|---|---|---|---|---|---|---|---|---|---|
| MP-1 | Existing main panel | — | — | 100 [ASSUMED] | ~15 yrs [ASSUMED] | Utility-metered (main only) [ASSUMED] | UNKNOWN | UNKNOWN | UNKNOWN |
| SP-RETAIL1 | Retail-1 subpanel | Ground | 80 [ASSUMED] | UNKNOWN | UNKNOWN | Unmetered [ASSUMED] | UNKNOWN | UNKNOWN | UNKNOWN |
| SP-RETAIL2 | Retail-2 subpanel | Ground | 80 [ASSUMED] | UNKNOWN | UNKNOWN | Unmetered [ASSUMED] | UNKNOWN | UNKNOWN | UNKNOWN |
| SP-OFFICE1 | Office-1 subpanel | 2nd | 100 [ASSUMED] | UNKNOWN | UNKNOWN | Unmetered [ASSUMED] | UNKNOWN | UNKNOWN | UNKNOWN |
| SP-OFFICE2 | Office-2 subpanel | 3rd | 100 [ASSUMED] | UNKNOWN | UNKNOWN | Unmetered [ASSUMED] | UNKNOWN | UNKNOWN | UNKNOWN |

"UNKNOWN" in every case means: a field survey (nameplate reading, breaker-by-breaker
inventory, circuit tracing) has not been performed and no value has been substituted.

---

## 3. Standards-baseline survey risks — status per item

Per the standards baseline (§2, §3) and per this run having **no physical site visit**,
here is each flagged risk and whether it can be confirmed from the data available to
this run.

| # | Risk (baseline citation) | Can this run confirm it? | Status |
|---|---|---|---|
| 1 | Each occupant has ready access to their own OCPD — PEC Art. 2.40 (= NEC 240.24(B)) | No | **CANNOT BE CONFIRMED WITHOUT PHYSICAL SITE VISIT.** Requires walking each tenant space and locating the subpanel relative to leased area / common corridor. |
| 2 | Tenant branch circuits supply only that tenant — PEC Art. 2.10 (= NEC 210.25(A)) | No | **CANNOT BE CONFIRMED WITHOUT PHYSICAL SITE VISIT.** Requires circuit tracing (breaker-off test at each subpanel, confirm which downstream devices de-energize). This is the single highest-value unresolved item for the submetering deliverable specifically — if crossings exist, submetering accuracy is compromised regardless of meter quality (baseline §2 "highest-value finding"). |
| 3 | House loads not supplied from a tenant panel — (= NEC 210.25(B)) | No | **CANNOT BE CONFIRMED WITHOUT PHYSICAL SITE VISIT.** Existence of any house/common-area load at all is unconfirmed, let alone its supply point. Represented in `topology.json` as a speculative placeholder node only. |
| 4 | Neutral not re-bonded to EGC downstream of the service disconnect — PEC Art. 2.50 (= NEC 250.24(A)(5) / 250.142) | No | **CANNOT BE CONFIRMED WITHOUT PHYSICAL SITE VISIT.** Requires opening each subpanel and inspecting the neutral bus bonding/isolation. Baseline flags this as a common defect at this building age — treat as a survey priority, not as confirmed present or absent. |
| 5 | Six-disconnect rule, 4 tenant + 1 house = 5 — PEC Art. 2.30 (= NEC 230.71, 2017 text) | No | **CANNOT BE CONFIRMED WITHOUT PHYSICAL SITE VISIT.** Requires counting actual service disconnecting means at MP-1 and confirming whether a house disconnect exists as a 5th (or 6th, if house load is split). |
| 6 | Grounding electrode system condition — PEC Art. 2.50 (= NEC 250.50/.52/.53) | No | **CANNOT BE CONFIRMED WITHOUT PHYSICAL SITE VISIT.** Electrode type, count, and connection integrity require excavation/inspection or, at minimum, visual trace of the GEC from MP-1. Baseline treats GES replacement as in-scope for the eventual replacement design until proven otherwise — that presumption is unaffected by this as-built, which only records that the condition is unknown, not that replacement is or isn't needed. |

**Net result: all five baseline survey risks are unresolved by this run.** None can be
marked compliant or non-compliant. This as-built's contribution is limited to correctly
recording *that* these are open field questions, with stable node IDs so a future field
visit has a place to attach its findings (e.g., updating `GES-1.field_verification_status`
in `topology.json` from `UNKNOWN` to a real reading).

---

## 4. Direct answer — does this deliverable depend on load-calc's output?

**No — confirmed, not just assumed.** Everything in this as-built (topology, panel
identities, floor areas, tenant count, service voltage/phase, the survey-risk flags
above) came from the stated existing-conditions scenario data and from the standards
baseline's list of things to check for. None of it required a demand load, a conductor
size, or a breaker size — those only enter the picture once someone is *designing* the
replacement panel, which is exactly the part load-calc's refusal blocked.

I did hit one soft edge, not a hard dependency: the "six-disconnect rule" and "house
loads not supplied from a tenant panel" risk items reference concepts (disconnect count,
house-load classification) that *load-calc's own reference work* also touches on (its
gap report's item A.7 flags house-load classification as needed for the demand
calculation). But that's a shared input both deliverables independently need from a site
survey — load-calc needs it to size a feeder, this as-built needs it to know what to draw
— not a real dependency of this as-built ON load-calc's output. Neither deliverable can
get that fact from the other; both need the same missing field visit.

**Routing implication for the pipeline:** as-built documentation of existing conditions
and load-calc's replacement-design output are separable work items with a shared
prerequisite (a physical site survey), not a sequential dependency of as-built on
load-calc. The current pipeline ordering (load-calc blocks as-built) is stricter than
necessary for the existing-conditions half of the as-built scope. It remains correct that
as-built cannot produce a *replacement* panel schedule until load-calc unblocks — that
part of the original scope limit stands.

---

## 5. Outstanding blockers, restated for this document specifically

1. No physical site survey performed — every item in Section 3 is open.
2. `demand_factors.md` stub blocks load-calc, which blocks the *replacement* panel
   schedule and any DXF/SLD content showing new breaker/conductor sizes. This document
   does not attempt that content.
3. Meralco fault-current data (baseline §5.2) is not needed for this document and remains
   open only for the eventual replacement design.
4. No prior as-built exists to cross-check this one against — this is the baseline
   record going forward, contingent on a real survey superseding it.
