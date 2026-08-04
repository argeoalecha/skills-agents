# Worked Example — QC Panel Upgrade + Tenant Submetering (SYNTHETIC)

First live end-to-end run of the electrical-agency pipeline (2026-08-04). No real
client — a synthetic scope was used deliberately to smoke-test the pipeline's routing,
dependency ordering, and refuse-rather-than-guess discipline before running it against
real engagement data. **Every file here is SYNTHETIC and unsealed — none of it is
usable as real engineering data for an actual client.** Its value is as a worked
example of pipeline mechanics: what each agent produces, how gaps get carried forward
without fabrication, and where the canonical dependency order (see this skill's
`skill.md`) actually held up under a real run vs. where it turned out to be stricter
than necessary.

## Scenario

3-storey mixed-use commercial building, Quezon City. Ground floor: 2 retail tenants.
2nd/3rd floor: 1 office tenant each. Existing service: 100A, 230V single-phase main
panel, ~15 years old, feeding 4 unmetered tenant subpanels, no prior as-built
documentation. Scope: replace the main panel per current PEC 2017, add per-tenant
submetering for cost allocation, produce as-built documentation, add a basic
digital-twin dashboard, and produce a formal spec package for contractor bidding.

## Files, in pipeline order

| File | Produced by | What it demonstrates |
|---|---|---|
| `standards-baseline.md` | `standards-compliance-agent` | Full codes/standards baseline, including the correct handling of a genuinely ambiguous scope item (submetering: private submeters vs. separate utility services) by stating both readings and flagging the ambiguity for client confirmation rather than guessing. |
| `load-calc-gap-report.md` | `load-calc-agent` | **The core discipline this pipeline exists to enforce**: refusing to fabricate a demand calculation when the reference table (`ee-load-calc/reference/demand_factors.md`) is an unpopulated stub, and instead producing a precise, prioritized, itemized list of exactly which PEC table entries are missing. |
| `asbuilt-existing-conditions.md` + `topology.json` | `as-built-agent` | Documenting existing conditions from stated (not surveyed) data, with every figure explicitly tagged ASSUMED or UNKNOWN — never VERIFIED. Also the discovery that existing-conditions documentation does *not* actually depend on load-calc's output, only a *replacement* panel schedule does. |
| `instrumentation-procurement.md` | `instrumentation-procurement-agent` | Splitting standard/protocol selection (independent of load-calc) from CT/meter sizing (dependent on it), and correctly identifying that the ERC/EPIRA "no billing markup" constraint is enforced at the software layer, not the meter layer. |
| `digital-twin-spec.md` | `digital-twin-agent` | Tag schema and RLS design proceeding fully while threshold *values* stay explicitly null/TBD, enforced with a structural Zod guard (a threshold can't be non-null without a citation) rather than a convention. |
| `spec-package.md` | `spec-writer-agent` | The most numeric-heavy consumer in the pipeline still drafting ~half its content (General + most of Execution) while Products correctly splits into *two* distinct blockers (load-calc's sizing triad vs. a separate utility fault-current request) rather than one undifferentiated gap. |

## What this run changed in the pipeline itself

Findings from this run were applied directly to the agent/skill definitions (not just
recorded here):

- `standards-compliance-agent` was missing `Write` access despite the pipeline's
  file-handoff contract requiring it — fixed.
- The canonical dependency order in this skill's `skill.md` and in
  `orchestrator-scope.md` was stricter than necessary — three separate agents
  independently found their structural/scoping work doesn't need `load-calc-agent`,
  only their numeric sizing sub-tasks do. The canonical order now reflects the split.
- No agent owns field site survey — now flagged explicitly as an external-owner queue
  item rather than a silent gap.
- Breaker interrupting rating (AIC) was being implicitly treated as part of the
  load-calc gap; it's a separate blocker (utility fault-current data) and is now
  tracked as one.
- `/ee-audit`'s checklist only looked for cross-document mismatches; this run found a
  same-document mismatch (a citation table vs. the same file's body text) that the
  checklist now explicitly covers.

## Still open (not fixed by this run)

`skills/ee-load-calc/reference/demand_factors.md` remains an unpopulated stub — this
pipeline still cannot complete a real load calculation until someone transcribes the
relevant PEC 2017 Table 2.20 series demand factors from a physical code copy. This
example's `load-calc-gap-report.md` states exactly which entries are needed.
