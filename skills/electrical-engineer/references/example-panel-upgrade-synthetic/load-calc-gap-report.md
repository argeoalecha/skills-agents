# Load Calculation — BLOCKED (gap report, not a panel schedule)

**Engagement:** QC 3-storey mixed-use, panel replacement feasibility (SYNTHETIC smoke test)
**Status:** REFUSED TO CALCULATE — reference data required by the skill procedure is absent.
Draft-for-PEE-review process, RA 7920 sealing boundary applies as always.

## Why this run stops here

`/ee-load-calc` step 2 requires demand factors from `reference/demand_factors.md` and step 3
requires breaker steps from `reference/standard_breaker_ratings.md` before
`pec_calc_lib.py` can be run. I read both files:

- `reference/demand_factors.md` — table is a header row only, all Demand Factor / Article
  cells empty except a placeholder row citing "Art. 2.20, Table 2.20-A" with no numeric
  value filled in.
- `reference/standard_breaker_ratings.md` — this one IS populated (15–2000 A standard step
  list, matches `STANDARD_BREAKER_RATINGS_A` in the script) and is usable once a demand
  amperage exists to round up from. It is not the blocker by itself.

The standards baseline for this engagement (`standards-baseline.md`, §8 items 2 and 5)
independently flags the same gap and instructs: "All CHECK-BOOK designators — verify
against the physical PEC 2017" and "load-calc will stall without them." That is exactly
what happened.

Per the skill's own rule and my operating rules: a demand factor, ampacity, or breaker
size that did not come out of `pec_calc_lib.py` fed by a cited table value does not go
into a deliverable. No connected-load estimate, no per-sqm VA/sqm guess, and no assumed
demand factor was applied anywhere below, including informally in prose.

## What was NOT done (and why, explicitly)

- Did not assign a VA/sqm figure to the retail (80 sqm x2) or office (100 sqm x2) areas.
  PEC Table 220.12/2.20-equivalent unit-load-per-area values were not supplied and are
  not general engineering knowledge I'm permitted to substitute.
- Did not apply any demand factor curve (e.g., first-X-VA at 100%, remainder at Y%) to
  the retail/office connected loads, because none is in `demand_factors.md`.
  general commercial/retail lighting demand factor
- Did not aggregate tenant loads into a feeder/service demand per Art. 2.20 multi-
  occupancy rules, because that table is also unpopulated.
- Did not run `pec_calc_lib.py` at all — there is no demand VA to feed into
  `min_conductor_ampacity()` or `select_breaker()`. Running the script on invented
  inputs would produce a numerically precise but factually fabricated output, which is
  the specific failure mode this rule set exists to prevent.
- Did not state an opinion on whether 100 A remains adequate. That is the blocking
  question and it is unanswered — not "probably yes" or "probably no."

## Itemized gap list — exactly what unblocks this calc

### A. Demand factor entries needed in `reference/demand_factors.md`

1. **Retail/store lighting — general lighting load, VA per unit area.**
   PEC 2017 Table 2.20-A (= NEC Table 220.12) "Store" occupancy unit load, VA/m².
   Needed to convert 80 sqm x2 retail floor area into a connected lighting VA figure
   before any demand factor can even be applied.
2. **Office lighting — general lighting load, VA per unit area.**
   Same table, "Office" occupancy row. Needed for the 100 sqm x2 office floor areas.
3. **General lighting demand factor curve — commercial/office occupancy.**
   PEC 2017 Table 2.20-B / Table 220.42-equivalent: the first-N-VA-at-100%,
   remainder-at-X% demand factor tiers for office and store occupancies (these
   differ by occupancy class — dwelling-unit tiers do not apply here).
4. **Receptacle load demand factor — commercial/office, non-dwelling.**
   PEC 2017 Art. 2.20 receptacle demand factor table (= NEC 220.44) for banks/office
   and store occupancies specifically (unit load + demand tiers differ from the
   general "other loads" table).
5. **HVAC/motor load demand and largest-motor factor**, if any HVAC equipment exists
   per floor — connected load and demand basis, since motor loads are calculated at
   100% of the largest motor plus other motors, not blanket-derated (PEC Art. 4.30 /
   NEC 430 territory, cross-referenced from Art. 2.20 feeder calc).
6. **Feeder/service demand factor for multi-occupancy (4-tenant) aggregation.**
   PEC 2017 Art. 2.20 optional or standard calculation method for multi-family/
   multi-occupancy commercial buildings (NEC 220.84/220.87-equivalent) — this is the
   specific table that determines whether the 4 tenant loads sum at 100% or get a
   diversity/coincidence factor applied at the service. This is the single highest-
   leverage missing entry: it directly decides the "is 100 A enough" answer.
7. **House/common-area load classification and demand factor**, if there is any
   common-area lighting, signage, or fire/life-safety load fed from the main panel
   ahead of the 4 tenant subpanels (implicated by baseline §2 "house loads not
   supplied from a tenant panel" finding — if such loads exist they need their own
   line item and demand basis).

None of these six/seven values may be filled in from general NEC familiarity, because
PEC 2017 is confirmed (baseline §0) to diverge from NEC 2017 at the sub-article/table
level in ways not yet verified, and table values are copyrighted — they must come from
the physical PEC 2017 Part 1, Table 2.20 series.

### B. Breaker rating entries — status

`reference/standard_breaker_ratings.md` is already populated with the standard ampere
step list (15...2000 A) and matches the script's built-in table. This is NOT a blocker.
Once a demand ampacity is computed, `select_breaker()` can run immediately. The relevant
steps near this building's likely range (100-225 A class, given a ~23 kVA existing
service and probable growth from a 4-tenant aggregate) are already present: 100, 110,
125, 150, 175, 200, 225 A. No action needed here unless the calculated demand exceeds
225 A, in which case the existing list still covers it (up to 2000 A) — still not a gap.

### C. Also outstanding (carried from standards baseline, not this skill's table gap
but blocking the same downstream question)

8. **Available fault current at the service point** (transformer kVA and %Z from
   Meralco, in writing) — required by `pec_calc_lib.py`'s
   `fault_current_point_to_point()` before any interrupting-rating or breaker AIC
   selection can be finalized. Baseline §5.2, OPEN and blocking.
9. **Conductor R/X per km** for whatever conductor size ends up selected — needed for
   `voltage_drop_pct()`. Not yet relevant until (A) is resolved and a conductor size
   is on the table, but flagging so it isn't missed at the next pass.

## Answer to the two questions this smoke test asked

1. **Did the agent correctly detect the gap and refuse rather than guess?** Yes. No
   demand factor, VA/sqm figure, aggregated demand load, conductor size, breaker size,
   or voltage-drop percentage was produced. `pec_calc_lib.py` was not invoked, because
   it had no legitimately-sourced input to run on.
2. **Itemized missing-data list** — see sections A (7 items) and C (2 items) above.
   Section B (breaker ratings) is confirmed NOT missing.

## Next action required before this calc can proceed

Populate `~/.claude/skills/ee-load-calc/reference/demand_factors.md` items A.1-A.7 from
a physical PEC 2017 Part 1 copy (Table 2.20-A, 2.20-B, and Art. 4.30 motor provisions),
and obtain item C.8 (fault current basis) from Meralco in writing. Once both exist, this
same procedure can be re-run and will produce an itemized panel schedule (load ID,
connected load, demand factor, demand load, conductor size, breaker size, voltage drop %)
per the skill's required output format.

## Downstream impact of this refusal

- `as-built-agent`: nothing to copy — no panel schedule exists yet. Do not proceed on
  panel/breaker/conductor data for this feeder calc.
- `digital-twin-agent`: no breaker ratings or 80%-continuous flags exist yet to derive
  alarm/warning thresholds from.
- `spec-writer-agent` / `/ee-spec-writer`: no numeric spec requirements to trace back to
  from this calc yet.
- This gap report, not a panel schedule, is the correct input for those agents to wait on.
