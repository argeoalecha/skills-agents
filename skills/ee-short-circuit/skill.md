---
name: ee-short-circuit
description: Multi-bus short-circuit fault-current study — per-unit symmetrical components, Zbus method, ANSI/IEEE C37.010 asymmetrical duty, and C37.13 low-voltage X/R device-rating checks. Use for protective-device coordination, bus-bracing/momentary-withstand checks, or as the required fault-current input to an arc-flash incident-energy study. Distinct from /ee-load-calc's single-point fault_current_point_to_point() estimate — use this skill when more than one bus, more than one source, or a device duty check against ANSI/IEEE ratings is needed. Triggers on "short circuit study", "fault current study", "Zbus", "symmetrical components", "coordination study", "bus bracing", "device duty check", "interrupting rating check".
---

# Multi-Bus Short-Circuit Study

Deterministic calc procedure. Never estimate multi-bus fault duty, X/R, or device duty by
reasoning in text — always run `scripts/short_circuit_lib.py` and report its numeric
output. A number that did not come out of the engine or off a cited code table does not go
into a deliverable.

## Relationship to `/ee-load-calc`

`/ee-load-calc`'s `fault_current_point_to_point()` is a single-point transformer-secondary
estimate, adequate for a basic panel-schedule breaker AIC sanity check on one bus. This
skill is the full multi-bus engine: build every bus and source once, solve the whole
network in one pass, and get three-phase/SLG/L-L/LLG duty, ANSI C37.010 asymmetrical duty,
and a C37.13 device-rating check at *every* bus simultaneously. Use `/ee-load-calc` for a
quick single-bus estimate during load-calc work; use this skill for an actual coordination
study, a bus-bracing check, or anything an arc-flash study will consume.

## Procedure

1. **Build the `System`**: `System(base_mva=..., prefault_pu=1.0)`, then declare every bus
   (`.bus(name, kv)`), source (`.utility()` / `.generator()`), motor contribution
   (`.motor_group()`), transformer (`.transformer()`), and cable/impedance branch
   (`.cable()` / `.impedance()`), and every protective device to be checked (`.device()`).
2. **Supply cable and transformer data from a cited source** — never guessed. See "Inputs
   the library does not supply" below.
3. **Run `.solve()`** — one call returns three-phase, SLG, L-L, and LLG bolted-fault duty,
   ANSI C37.010 asymmetrical (peak/rms) duty, and the interrupting-network duty at every
   bus, in one pass.
4. **Run `device_duty_check()`** on the result for every bus with a device attached — this
   is the pass/marginal/fail verdict against each device's interrupting rating, C37.13 LV
   X/R-adjusted.
5. **State the maximum-fault case and, if protection pickup settings are in scope, the
   minimum-fault case too** (e.g. utility-fed vs. standby-generator-fed) — a study that
   only reports the maximum case cannot validate protection pickup on a weaker source.
6. **Flag whichever bus has SLG duty exceeding three-phase duty** (`islg > i3p`) — this
   happens wherever Z0 < Z1, typically just downstream of a solidly grounded delta-wye
   transformer, and it governs device selection over the three-phase figure (IEEE 242).
   The governing device also needs its single-pole/ground-fault rating confirmed
   separately from the three-pole symmetrical rating.
7. **Cite the standard behind every judgment call** — transformer tolerance sign (`tol`),
   motor class multiplier, X/R assumption, device test X/R — per the docstrings in
   `scripts/short_circuit_lib.py`.

## Inputs the library does not supply

`short_circuit_lib.py` implements public-domain per-unit/symmetrical-components formulas
only. These must be supplied as arguments from a cited source, never guessed:

- Utility fault MVA (and X/R) at the service point → utility's own fault study (e.g.
  Meralco), in writing. **Never assumed** for an issued study — an assumed utility source
  is acceptable only for a preliminary/estimated-basis draft, clearly labeled as such.
- Cable R and X per km → cable manufacturer datasheet or your own copy of NEC (NFPA 70)
  Ch.9 Table 9 / PEC conductor tables — copyrighted table data, not reproduced here, same
  convention as `pec_calc_lib.py`. Build the impedance with `cable_z(length_m,
  r_ohm_per_km, x_ohm_per_km, sets, ...)`.
- Transformer %Z, X/R, and winding connection → transformer nameplate or certified test
  report (not the estimated/nameplate-typical value, for an issued study).
- Motor group kVA and X/R → motor schedule / nameplate data, or the customary LV
  lumped-group assumption (`mtr_class="lv_group"`, ~4x FLA) only for a preliminary study.
- Device interrupting ratings and types → protective device nameplate/datasheet.

If any of these is unavailable, state the gap and stop, or clearly label the study as
preliminary/estimated-basis with each assumed input named. Do not substitute a
plausible-looking assumed value silently — that is how a coordination study goes wrong in
a way that survives review.

## What this engine does not do

- **No arc-flash incident-energy (IEEE 1584) calculation.** That is a separate, downstream
  calculation — see `ee-arc-flash-calc` — which consumes this engine's bolted three-phase
  and/or SLG duty as its required input. Do not let an arc-flash study assume or estimate a
  fault current instead of running this engine first.
- **No 30-cycle time-delayed network**, and no NACD (local/remote apportionment) or
  contact-parting-time interpolation — both matter only for MV breakers rated on a
  symmetrical-current basis, which most personal-scale LV studies won't include. If one is
  in scope, extend `System._zbus()`'s `network` parameter rather than approximating inline.
- **Peak and asymmetrical-rms duty are three-phase-only.** At any bus where SLG duty
  governs (`islg > i3p`), the true momentary duty is understated — for a conservative
  estimate, scale `ipeak`/`irms_asym` by `islg / i3p` at that bus, or report both duties
  explicitly if the study will be issued.

## Downstream consumers

- `ee-arc-flash-calc` — consumes bolted three-phase and/or SLG duty (and bus X/R, for the
  arcing-current correction) as its required, non-optional input.
- `/ee-audit` — should check that any arc-flash study's fault-current basis actually traces
  to an `ee-short-circuit` solve, not an assumed value.

## Files

- `scripts/short_circuit_lib.py` — the engine: `System` class (bus/utility/generator/
  motor_group/transformer/cable/impedance/device/solve), `device_duty_check()`, `to_rows()`
  for CSV/tabular export, plus the per-unit/DC-offset/C37.13 helper functions.
- `scripts/validate.py` — 4 parity checks against known closed-form and hand-calculated
  results (transformer-on-infinite-bus, series-source vector-vs-scalar sum, separate-R/X-
  network X/R divergence, DC-offset-factor limits). Run `python3 validate.py` after any
  change to `short_circuit_lib.py` — all 4 must pass before the engine is trusted for a
  deliverable.

## Provenance

The engine (per-unit system, Zbus network solve, ANSI C37.010 duty networks, C37.13 LV X/R
adjustment) is ported from a validated R implementation built for a prior campus
power-system short-circuit study — engine only, no case-specific equipment data. It was
checked against that study's own published results as an additional integrity check before
being trusted here: every published figure (bus fault duties, X/R values) reproduced
exactly. The formulas themselves are standard public-domain IEEE/ANSI methodology (see the
citations in `short_circuit_lib.py`'s module docstring), not anything project-proprietary.

## Licensure boundary

Output is **draft for PEE review**, not a stamped deliverable. Under RA 7920, electrical
studies require the seal of a licensed Professional Electrical Engineer. Verify every
result against the current physical code edition, a certified transformer test report, and
the actual utility fault study before sealing.
