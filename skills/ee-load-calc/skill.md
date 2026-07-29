---
name: ee-load-calc
description: Performs electrical load list aggregation, demand factor application, breaker/conductor sizing, voltage drop, and fault current calculations per PEC 2017. Use for any panel schedule, protection coordination, load study, or sizing task in an electrical consulting engagement. Triggers on /ee-load-calc, "load calculation", "size the breaker", "panel schedule", "voltage drop", "fault current", "conductor sizing", "demand load".
---

# Electrical Load Calculation

Deterministic calc procedure. Never estimate breaker size, fault current, ampacity, or
voltage drop by reasoning in text — always run `scripts/pec_calc_lib.py` and report its
numeric output. A number that did not come out of the library or off a cited code table
does not go into a deliverable.

## Procedure

1. Build the load list: each load's connected VA/kW, phase, voltage, continuous vs.
   non-continuous classification.
2. Apply demand factors per `reference/demand_factors.md` (populate from your physical
   PEC 2017 Table 2.20 / 2.0-A — table values are copyrighted and not reproduced here).
3. Run `scripts/pec_calc_lib.py` for: demand load, minimum conductor ampacity (125%
   continuous per PEC Art. 2.15 / NEC-equivalent), breaker size (next standard rating
   up, from `reference/standard_breaker_ratings.md`), voltage drop %, and fault current
   (point-to-point method).
4. Cite the PEC article/table used for every demand factor and derating applied.
5. Flag anything loaded beyond 80% continuous breaker rating.
6. Output a structured panel schedule: load ID, connected load, demand factor, demand
   load, conductor size, breaker size, voltage drop %.

## Inputs the library does not supply

`pec_calc_lib.py` implements public-domain formulas only. These must be supplied as
arguments from a cited source, never guessed:

- Demand factors → PEC 2017 tables (`reference/demand_factors.md`)
- Conductor R and X per km → cable manufacturer datasheet or PEC conductor tables
- Transformer impedance % → transformer nameplate or datasheet
- Ampacity tables → physical PEC 2017 copy

If any of these is unavailable, state the gap and stop. Do not substitute a typical value
silently — a plausible-looking assumed impedance is how a coordination study goes wrong.

## When standards are unclear

If `standards-compliance-agent` output isn't available for this engagement, request it
before proceeding. Don't assume code edition or local amendments — an LGU electrical
ordinance may override national PEC minimums.

## Downstream consumers

These outputs are contract inputs elsewhere; revising a result here invalidates work
already done downstream:

- `as-built-agent` copies panel/breaker/conductor data **verbatim** into panel schedules.
- `digital-twin-agent` derives alarm and warning thresholds from breaker ratings and the
  80% continuous flag.
- `/ee-spec-writer` traces every numeric spec requirement back to these results.

If a calc changes after those ran, say so explicitly so the affected deliverables get
re-issued. `/ee-audit` checks for exactly this drift.

## Files

- `scripts/pec_calc_lib.py` — calc engine (demand load, ampacity, voltage drop, fault
  current, breaker selection, continuous derating check)
- `reference/demand_factors.md` — your PEC 2017 demand factor values (populate manually;
  table data is copyrighted)
- `reference/standard_breaker_ratings.md` — standard breaker ampere ratings for sizing

## Licensure boundary

Output is **draft for PEE review**, not a stamped deliverable. Under RA 7920, electrical
studies require the seal of a licensed Professional Electrical Engineer. Verify every
result against the current physical code edition before sealing.
