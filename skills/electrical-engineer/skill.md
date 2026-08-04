---
name: electrical-engineer
description: Entry point for electrical engineering consulting work — power system studies, load calculations, as-built documentation, technical specifications, instrumentation procurement, standards compliance, and digital-twin/SCADA mimic dashboards. Routes to the electrical-agency subagents and the /ee-* skills, and hands the software layer off to the web stack (/theme-hayahai, /db-migrate, /audit, /vercel-deploy). Philippines-first — PEC 2017, RA 7920, PEE stamping. Use when the user mentions an electrical engagement, SOW, RFP, panel schedule, single-line diagram, load study, breaker/conductor sizing, voltage drop, fault current, arc flash, protection coordination, CT/PT/power meter selection, as-built drawings, a mimic or digital twin of a power system, or asks "what do I run for this electrical job". Triggers on /electrical-engineer, "electrical project", "EE work", "power system study".
---

# Electrical Engineering — Engagement Router

The front door for electrical discipline work. This skill decides *what runs in what
order*; it does not calculate, draft, or design. Each specialist below owns its own
rules — do not restate or override them here.

## Decision: which entry point

| Situation | Route to |
|---|---|
| New SOW / RFP / client brief, scope not yet decomposed | `orchestrator-scope` agent |
| Need to know which codes govern before anything else | `standards-compliance-agent` |
| Panel schedule, breaker/conductor sizing, VD, fault current | `/ee-load-calc` |
| Site survey → SLD, panel schedules, riser diagrams | `as-built-agent` |
| Selecting CTs, PTs, meters, sensors, gateways | `instrumentation-procurement-agent` |
| Formal spec sections (General/Products/Execution) | `/ee-spec-writer` |
| Mimic / digital-twin dashboard of the power system | `digital-twin-agent` |
| Final cross-check before client delivery | `/ee-audit` |
| Pricing and commercial packaging of the engagement | `/proposal-tech` + `/proposal-comm` |

The dependency order below is **already solved** for this pipeline. Do not run
`/graph-topology-planner` to re-derive it — that skill designs topologies for novel
projects, and this one is a fixed instance whose order is fixed by engineering
dependency, not by preference. Use it only for work that falls outside this pipeline
(a new service line, a client engagement with an unfamiliar deliverable shape).

## Canonical dependency order

Never run a downstream step on missing upstream inputs — flag the gap instead.
Validated against a live smoke-test engagement (see `references/example-panel-upgrade-
synthetic/` for the full worked run). The order is **not** a strict chain — several
steps split into a structural/scoping half that only needs standards-compliance, and a
numeric-sizing half that needs `/ee-load-calc`'s output. Route the independent halves
in parallel.

```
standards-compliance ──┬─→ /ee-load-calc ──┬─→ as-built (replacement schedule)
        │              │                   ├─→ instrumentation (CT/meter sizing)
        │              │                   ├─→ /ee-spec-writer (Products: sizing)
        │              │                   └─→ digital-twin (threshold values)
        │              │
        ├─→ field survey (external owner — no agent performs this)
        │      │
        │      └─→ as-built (existing-conditions doc) ─┐
        │                                               ├─→ digital-twin (topology/schema)
        ├─→ instrumentation (standard/protocol) ────────┘
        │
        └─→ /ee-spec-writer (General + most of Execution)

  all outputs ──→ /ee-audit ─→ deliver
```

**Field site survey has no agent owner.** If the engagement involves documenting an
existing installation, someone has to physically visit the site before as-built or
load-calc can use real (not stated/assumed) data. Flag this as a client/field-engineer
deliverable in the task queue, not a silent gap.

**Breaker interrupting rating (AIC) is a separate blocker from `/ee-load-calc`.** It
depends on the utility's available fault current at the service point (e.g. Meralco,
in writing) — track it as its own queue item with an external owner. Unblocking
load-calc does not unblock AIC.

## The two layers — keep them separate

An electrical engagement has an **engineering layer** and a **software layer**. They
use different toolchains and different standards of proof. Routing errors between
them are the most expensive mistake in this pipeline.

**Engineering layer** — load calcs, sizing, standards citations, as-builts, specs.
Governed by PEC 2017 / IEEE / RA 7920. Numbers come from `pec_calc_lib.py` or a
cited code table, never from prose reasoning. Web tooling has no authority here:
never let `/audit`, `/simplify`, or any code-quality skill "improve" a calc result,
a breaker size, or a code citation.

**Software layer** — the digital-twin dashboard, tag database, client portal, any
Next.js/Supabase deliverable. This is ordinary web work and uses the full web stack.
It consumes engineering-layer outputs as fixed inputs.

## Handoff into the web stack

Once `digital-twin-agent` has produced topology bindings and threshold values, the
build is a normal web project:

- `/theme-hayahai` → **hayah-console** variant. The only variant with semantic status
  colors and a data-viz palette — built for exactly this. Live tags use the coral
  pulse dot. Status is never color alone: always dot + label (operators may be
  colour-blind, and a mimic misread is a safety event).
- `/dataviz` → trend charts, load profiles, KPI tiles. Read before writing chart code.
- `/db-migrate` → tag schema, historian tables. RLS on every table, per global standards.
- `/audit` → pre-production gate on the dashboard **software only**.
- `/ux-review` → operator-facing usability. Weight legibility and alarm clarity over
  conversion heuristics; this is a control-room screen, not a marketing page.
- `/vercel-deploy` or `/netlify-deploy` → ship it.
- `/e2e-test` → verify alarm states render correctly against seeded tag data.

## Document deliverables

- Spec sections and basis-of-design → `document-skills:docx` for client-facing format.
- Instrument comparison tables, BOQ, load lists → `document-skills:xlsx`.
- Proposals → `/proposal-tech` and `/proposal-comm` (Philippines variant).

## Worked example

`references/example-panel-upgrade-synthetic/` — a full synthetic engagement run
through every agent and skill in this pipeline, kept as a reference for what each
step's output should look like and how gaps get carried forward without fabrication.
Not real data; see that folder's `README.md` before treating anything in it as a
template to copy verbatim.

## Non-negotiable: licensure boundary

Nothing produced by this pipeline is a stamped deliverable. Under RA 7920, electrical
plans and studies require the seal and signature of a licensed Professional Electrical
Engineer. Every calc, spec, and drawing that leaves this pipeline is **draft for PEE
review** — label it as such. Verify against the physical PEC 2017 code book before
sealing. Never present an AI-generated code article number as verified.
