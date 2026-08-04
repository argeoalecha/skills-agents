# Standards Baseline — QC 3-Storey Mixed-Use, Panel Replacement + Tenant Submetering

**SYNTHETIC / smoke test. Draft for PEE review — nothing here is sealed.**

**Status legend:** VERIFIED = confirmed against a published source this run. CHECK-BOOK = the requirement is real and correctly attributed to the article's subject matter, but the exact PEC designator must be confirmed against the physical PEC 2017 Part 1. OPEN = unresolved scope, missing data, or outside my authority.

**Scope resolution (client-confirmed, post-baseline):** Submetering scope is **(A) — private submeters behind one Meralco account**, client re-bills tenants. ERC/EPIRA resale-rate constraints apply to the dashboard billing logic (§5.3). Meralco is out of scope except at the service entrance (§5.2).

## 0. Code edition — settled

PEC Part 1, **2017 Edition** (IIEE / Board of Electrical Engineering). No successor edition found adopted as of this run — VERIFIED, re-confirm with IIEE before permit filing. Edition is fixed by **permit application date**, not design date.

PEC 2017 is a Philippine modification of **NEC 2017**. Downstream consequence: NEC 2020/2023 changes are **not** in force. Do not apply NEC 2020 230.67 (surge protection) or the NEC 2020 single-service-disconnect rule.

## 1. Panel replacement and sizing

| Requirement | Standard/Article | Deliverable | Status |
|---|---|---|---|
| Feeder/service demand calculation | PEC 2017 **Art. 2.20** (= NEC 220) | load-calc | CHECK-BOOK |
| Demand factors by load class | PEC 2017 Art. 2.20 tables | load-calc | CHECK-BOOK |
| Branch circuits, multi-occupancy | PEC 2017 **Art. 2.10** (= NEC 210) | load-calc, as-built | CHECK-BOOK |
| Feeder sizing, 125% continuous | PEC 2017 **Art. 2.15** (= NEC 215) | load-calc | CHECK-BOOK |
| Conductor ampacity + derating | PEC 2017 **Art. 3.10** (= NEC 310; ampacity = NEC Table 310.16 equiv.) | load-calc, spec | CHECK-BOOK |
| Panelboard rating/construction | PEC 2017 **Art. 4.8** (= NEC 408) | spec, as-built | CHECK-BOOK |
| Service conductors/equipment | PEC 2017 **Art. 2.30** (= NEC 230) | as-built, spec | CHECK-BOOK |
| Working space / dedicated space | PEC Ch.1 general art. (= NEC 110.26) | as-built, spec, survey | CHECK-BOOK |
| Interrupting rating ≥ available fault current | = NEC 110.9 / 110.10 equiv. | load-calc, spec | CHECK-BOOK |
| Available-fault-current marking | = NEC 110.24 equiv. | as-built, spec | CHECK-BOOK |

**Blocking risk:** 100 A @ 230 V 1-phase ≈ **23 kVA** for 4 tenants plus house loads. If the Art. 2.20 calculated demand exceeds 100 A, **"like-for-like, not capacity expansion" is not an available option** — the code minimum forces a service upgrade, implicating Meralco service capacity and possibly 1-phase → 3-phase conversion. `/ee-load-calc` must resolve this before as-built or spec proceed. Do not size the replacement to 100 A merely because the existing service is 100 A.

## 2. Multi-occupancy defects to survey for

Existing condition (4 tenants, unmetered subpanels, one 100 A main, 15 years old, no as-builts) creates specific exposures. Survey items, not assumptions.

| Requirement | Standard/Article | Status |
|---|---|---|
| Each occupant has **ready access** to their overcurrent devices | PEC **Art. 2.40** (= NEC 240.24(B)) | CHECK-BOOK — survey |
| Tenant branch circuits supply **only that tenant** | PEC **Art. 2.10** (= NEC 210.25(A)) | CHECK-BOOK — survey |
| House loads not supplied from a tenant panel | = NEC 210.25(B) | CHECK-BOOK — survey |
| Neutral **not** re-bonded to EGC downstream of service disconnect | PEC **Art. 2.50** (= NEC 250.24(A)(5) / 250.142) | CHECK-BOOK — common defect at this age |
| Six-disconnect rule (NEC 2017 basis); 4 tenant + 1 house = 5 | PEC **Art. 2.30** (= NEC 230.71, 2017 text) | CHECK-BOOK |

**Highest-value finding:** if existing branch circuits cross tenant boundaries, the submetering deliverable cannot produce accurate cost allocation regardless of meter quality — circuits must be re-segregated first. That is scope the client has not asked for and should be told about.

## 3. Grounding and bonding

PEC 2017 **Art. 2.50** (= NEC 250) governs. Grounding electrode system (= NEC 250.50/.52/.53), GEC sizing (= NEC Table 250.66 equiv.), EGC sizing (= NEC Table 250.122 equiv.), main bonding jumper (= NEC 250.24/.28). All CHECK-BOOK — deliberately not inventing PEC table designators for these.

A 15-year-old service was built to PEC 2000 or 2009. Grounding electrode system is the most likely non-compliance, and grounding upgrades are generally **not** grandfathered when service equipment is replaced. Treat GES replacement as in-scope until proven otherwise.

## 4. Overcurrent protection and coordination

PEC **Art. 2.40** (= NEC 240); standard breaker ratings (= NEC 240.6 equiv.); commercial GFCI (= NEC 210.8(B), 2017 text) — all CHECK-BOOK. Arc-flash calculation: **IEEE 1584-2018** — VERIFIED.

**Caution on the canonical IEEE citations.** **IEEE 141** (Red Book, 1993) is withdrawn/inactive, superseded by the IEEE **3002** series. **IEEE 242** (Buff Book, 2001) is superseded in practice by the IEEE **3004** series. Citing IEEE 141 as a current normative reference in a bid spec is a defect a contractor can challenge. Spec-writer should cite the 3000-series as normative; confirm current status before issue.

**Judgment, not code:** at ~23 kVA single-phase LV, a formal coordination study is almost certainly unwarranted — this is a series-rating and interrupting-rating question, not a TCC study. Do not let the spec require an IEEE 242/3004 study by reflex.

## 5. Utility submetering — resolved

**5.1 — Meralco standards are mostly OUT of scope for item (2).** Per Meralco's published guidance, **sub-meters are private equipment: Meralco does not provide, install, or maintain them.** They sit on the load side of the revenue meter. The 4 submeters are governed by PEC 2017 plus procurement/accuracy standards, not Meralco connection standards. Applicable: **ANSI C12.20** (class 0.2/0.5) *or* **IEC 62053-22** (class 0.2S/0.5S) — pick one, don't cite both; **IEEE C57.13** or **IEC 61869-2** for metering CTs (61869 supersedes IEC 60044-1); **IEEE 519** informative for harmonics/true-RMS.

**5.2 — Meralco standards ARE in scope, narrowly, for the service entrance.** Replacing the main panel means replacing service equipment. Meralco's distribution services and connection manual governs service entrance and metering enclosure arrangement — no document number, clause, or revision verified this run. OPEN. Also OPEN and **blocking**: available fault current at the service point (transformer kVA and %Z) must be obtained **in writing** from Meralco. `pec_calc_lib.py` requires impedance as a cited input; per the load-calc skill's own rule, state the gap and stop rather than assume.

**5.3 — ERC/EPIRA governs the re-billing itself.** Under **EPIRA (RA 9136)** and ERC rules, resale of electricity at a profit is generally prohibited absent authorization; submetered charges must reflect the actual distribution utility rate, and the sum of submetered billings must not exceed the main Meralco bill. Reasonable, transparent, contractually-agreed administrative fees are treated separately. Exposure is administrative (ERC) and civil (tenant claims) — a codes agent is not counsel; VERIFIED that the constraint exists, OPEN as to application. Practical consequence: it drives the meter accuracy class the client should buy, and **the dashboard must not ship a billing feature implying markup capability.**

## 6. RA 7920 and sealing

**RA 7920** (1995) governs practice and the PEE/REE/RME categories — VERIFIED. **QC DBO requires electrical plans bearing the sign and seal of a Professional Electrical Engineer**, plus a wiring permit sealed by an authorized Licensed Electrical Practitioner with PRC license, current PTR, and three specimen signatures — VERIFIED.

No verified RA 7920 REE-vs-PEE kVA/voltage threshold — moot here since QC DBO requires a PEE seal regardless.

Seal required: **as-built SLD, panel schedule, load calculation/basis of design, and the spec package** where issued as permit/bid documents. **Not required: the digital-twin dashboard software** — but every threshold, setpoint, and rating it displays derives from sealed engineering and must not be edited in the software layer.

## 7. Quezon City and statutory layer

Electrical Permit + **Certificate of Final Electrical Inspection (CFEI)** from QC DBO — VERIFIED. **PD 1096** (National Building Code) + IRR. **RA 9514** (Fire Code 2008) + IRR — statute VERIFIED, applicability to this building OPEN. **RA 11285** / Philippine Green Building Code metering provisions — likely below floor-area threshold for 3 storeys, confirm with QC DBO. OPEN.

**Mandatory vs. best practice.** **RA 11058 + DOLE D.O. 198-18** is Philippine law and is the mandatory occupational safety basis. **NFPA 70E (2024) is not Philippine law** — binding only if contractually adopted. Right source for arc-flash PPE, LOTO, energized-work rules; cite as a **contractually-adopted standard, not a legal obligation.**

**QC DBO implements the National Building Code *and the Local Building Code of Quezon City*.** That local layer is the most likely place for a requirement to override or add to PEC minimums, and has not been obtained. Until pulled from QC DBO, this baseline is national-code-only.

## 8. Blocking items before downstream agents run

1. ~~Scope ambiguity §5.4 — private submeters vs. individual Meralco services.~~ **RESOLVED: (A) confirmed.**
2. Calculated demand vs. 100 A — "like-for-like" may be code-impossible.
3. Available fault current from Meralco, in writing. Do not assume.
4. QC Local Building Code electrical amendments — not obtained.
5. All CHECK-BOOK designators — verify against the physical PEC 2017.
6. IEEE 141/242 current status — confirm before citing as normative.
7. ERC resale applicability — client's counsel.

## 9. Citation confidence

PEC 2017 renumbers NEC articles into a dotted scheme. The **article-level** mapping (NEC 220→2.20, 250→2.50, 240→2.40, 310→3.10, 408→4.8) is high confidence and is what's cited. **Sub-section and table designators are not, and were not invented** — where a specific table matters, the NEC-equivalent designator and subject matter are given so the engineer can locate it and record the true PEC designator. A wrong-but-plausible table number is worse than an admitted gap because it survives review. No downstream agent should promote a CHECK-BOOK citation to VERIFIED without the book in hand. Table values are copyrighted and deliberately not reproduced; read them into `~/.claude/skills/ee-load-calc/reference/demand_factors.md` and `standard_breaker_ratings.md` (both currently unpopulated stubs — load-calc will stall without them).

Sources: Meralco Biz — Start or Modify Service; Requirements for Installing a Separate Sub-meter (respicio.ph); ERC Rules on Submetered Electricity Billing in Condominiums (respicio.ph); QC Electrical Permit / CFEI Application; QC Department of the Building Official; IIEE — Philippine Electrical Code Part 1.
