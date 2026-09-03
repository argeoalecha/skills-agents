---
name: ee-arc-flash-calc
description: Arc-flash workplace-safety workflow — electrode-configuration risk flagging, governing-case selection (average vs. minimum arcing current per IEEE 1584-2018 Sec. 6.4), NFPA 70E (2024) PPE category banding, and the 40 cal/cm2 control-required flag. Requires bolted fault current from /ee-short-circuit and incident-energy figures computed externally (commercial tool or your own IEEE 1584-2018 copy) — does NOT implement the IEEE 1584 arcing-current/incident-energy equations itself. Use once electrode configuration, enclosure data, and both arcing-current cases' incident energy are available per bus. Triggers on "arc flash study", "incident energy", "PPE category", "IEEE 1584", "arc flash boundary", "40 cal", "electrode configuration".
---

# Arc Flash / Incident Energy — Safety Workflow Layer

Deterministic workflow procedure. This skill governs the arc-flash assessment
*process* — governing-case selection, PPE banding, boundary and control flagging — and
does **not** perform the IEEE 1584-2018 arcing-current or incident-energy calculation
itself. See "What this skill does not do" below before assuming otherwise.

## Hard prerequisites — do not start without these

1. **Bolted fault current and X/R at every bus, from `ee-short-circuit`.** Never assumed
   or estimated. If that study isn't finalized, stop and run it first — running this
   assessment against a provisional fault-current model produces a report that has to be
   redone, not just revised.
2. **Protective device time-current curves**, so clearing time can be read **at the
   arcing current specifically**, not at bolted fault current — these differ materially,
   and a lower fault current can fall below a breaker's instantaneous pickup and time
   out on the long-time element instead, producing a *longer* clearing time and
   therefore *higher* incident energy than the bolted-fault-current case would suggest.
3. **Electrode configuration per piece of equipment** (VCB, VCBB, HCB, VOA, or HOA) —
   from a manufacturer general-arrangement drawing, or a field-confirmed survey, or (only
   where neither is available) the conservative default for that equipment class,
   explicitly flagged as an assumption. This single input carries more consequence than
   any fault-current or clearing-time input: for identical fault current, voltage, and
   gap, an enclosed configuration can produce incident energy 2-3x an open-air one.
   Never default to whichever configuration is easiest to model.
4. **Incident energy (cal/cm²) computed for BOTH the average-arcing-current case and the
   minimum-arcing-current case, per bus** — from a licensed commercial tool (ETAP, SKM
   PowerTools, EasyPower, DIgSILENT PowerFactory) or your own from-standard
   implementation. See "What this skill does not do."

## What this skill does not do

**It does not calculate arcing current or incident energy from bolted fault current.**
IEEE 1584-2018 replaced the 2002 edition's model entirely — different equations,
different electrode-configuration framework, different validated input ranges — and in
some configurations produces incident energy results nearly double the 2002 figures for
the same equipment. Its coefficients are numerous, per-voltage-class, and not something
to trust from an LLM's recall for a safety deliverable that determines what protective
equipment a worker relies on. Get the actual incident-energy number from:

- a licensed commercial tool already validated against IEEE 1584-2018 (ETAP, SKM
  PowerTools, EasyPower, DIgSILENT PowerFactory), or
- a documented independent implementation built directly against your own copy of IEEE
  1584-2018 Section 4's equations and coefficient tables.

Once you have incident energy (cal/cm²) for both cases at each bus, this skill's
`scripts/arc_flash_lib.py` handles everything downstream of that number.

## Procedure

1. **Build one `BusAssessment` per bus**: bolted fault current (from `ee-short-circuit`,
   required), electrode configuration and its source, and both `ArcFlashCase` entries
   (`"average"` and `"minimum"`) with arcing current, clearing time, incident energy, and
   working distance for each.
2. **Run `assess_bus()`** — this selects the governing case (the higher of the two
   incident energies, per IEEE 1584-2018 Sec. 6.4; it raises if only one case was
   supplied, because silently defaulting to the average case is the exact mistake this
   step exists to catch), bands the result into a PPE category via
   `ppe_category()` (NFPA 70E (2024) Article 130.5 bands), and flags anything above 40
   cal/cm² as **control-required** rather than banding it — above that threshold arc
   blast is a pressure/shrapnel hazard independent of the thermal one, and the only
   correct answer is de-energizing or engineering the energy down, not a heavier suit.
3. **Confirm or correct any standing hypothesis about the worst-case bus** if one exists
   from an earlier design review (e.g. "the transformer secondary main is probably
   worst-case") — state explicitly whether the calculation confirmed or corrected it,
   don't let an unverified hypothesis stand as if it were a finding.
4. **Run `assessment_report()`** for the summary table, and flag every bus with
   `control_required=True` individually with a recommended control other than PPE.
5. **Record electrode-configuration source per bus** (drawing / field-confirmed /
   conservative-default) — a result sourced from a conservative default is weaker
   evidence than a field-confirmed one, and the report should say which is which.
6. **Field labels** (ANSI Z535): nominal voltage, arc flash boundary, incident energy at
   the stated working distance, and PPE category, matching the sealed report exactly. A
   label reprinted after a settings change without updating the underlying study is a
   compliance gap, not a paperwork detail.

## Review interval

Per NFPA 70E Article 130.5: reviewed for accuracy at intervals not exceeding five years,
and updated immediately upon any modification to the electrical distribution system — a
transformer change, a protective device replacement or resetting, or a material load
addition all trigger an update regardless of where the facility sits in the cycle.

## Files

- `scripts/arc_flash_lib.py` — `BusAssessment`/`ArcFlashCase` data structures,
  `governing_case()`, `ppe_category()`, `electrode_config_risk_note()`, `assess_bus()`,
  `assessment_report()`. PPE bands, the arc-flash-boundary threshold, valid conductor-gap
  ranges, and working-distance conventions are cited directly from NFPA 70E (2024)
  Article 130.5 / IEEE 1584-2018 as retrieved from a governing procedure document for a
  prior campus engagement — not recalled from training data. The arcing-current/
  incident-energy arithmetic itself is deliberately not implemented here; see above.

## Governing standards

| Standard | Governs |
|---|---|
| IEEE 1584-2018 | The calculation method itself (not implemented here — see above) |
| NFPA 70E (2024), Article 130.5 | Requires the assessment; review interval; PPE category bands |
| ANSI Z535 | Physical format of the arc-flash label |
| DOLE OSHS Rule 1210 | Philippine enforceable local anchor |

## Roles and scope boundary — the single most consequence-bearing deliverable in this pipeline

Electrode-configuration selection, incident-energy calculation, and PPE-category
determination are safety-critical engineering judgments, not measurements against a
published table. Interpretation of results and the PPE category determination are the
retained PEE's call, not a finding to leave to a draft-and-review workflow. Hold the
review discipline here at least as strictly as anywhere else in this pipeline — an
underestimated incident energy translates directly into undersized PPE for whoever is
standing in front of that panel next.

## Licensure boundary

Output is **draft for PEE review**, not a sealed deliverable. Under RA 7920, this
assessment and the labels it drives require the seal of a licensed Professional
Electrical Engineer. Producing this analysis is not the same as being entitled to
certify it.
