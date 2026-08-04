# Topology Examples by Domain

Worked examples showing how the pattern table (Step 3 of SKILL.md) applies across
different kinds of projects. Use these for calibration, not as templates to copy verbatim
— match the *shape* of your project to the *shape* of the example, not the specifics.

## Engineering / Consulting Deliverable (dependency-heavy, gated)

Example: a multi-study electrical engineering package (load analysis → short-circuit →
grounding → arc flash → risk assessment) across several sites feeding one aggregated view.

- **Topology:** Chaining is the backbone — arc flash literally cannot run without
  short-circuit results, short-circuit cannot run without load data. Resist parallelizing
  a real dependency chain just because the nodes *could* run at once.
- **Parallelization (Sectioning):** If multiple independent sites each need the same study
  sequence, the per-site studies are independent of each other — run those as sectioned
  parallel branches, then fan in to the aggregation node.
- **Gates:** Every transition where the deliverable eventually carries a professional
  stamp gets a human gate — not just the final output. A bad load analysis silently
  corrupts everything downstream, so gate right after Node 1, not only at the end.
- **Reducer note:** A multi-site fan-in usually isn't a vote or an overwrite — it's a
  structured merge (each site's data becomes one row/section in the aggregate), so the
  reducer is closer to "concatenate with schema" than "pick one."

## Multi-Agent Consulting Tooling (routing-heavy)

Example: a plugin with several specialized subagents (e.g., load-calc, spec-writer, audit)
invoked ad hoc from one session.

- **Symptom this framework catches:** subagents with no explicit edges between them aren't
  a graph — they're a toolbox. If "audit" depends on "spec-writer" output but that
  dependency isn't encoded anywhere, you have nodes without a topology.
- **This case is already solved locally.** `/electrical-engineer` is the router and
  `orchestrator-scope` the decomposer for exactly this shape — a fixed
  standards → load-calc → as-built/instrumentation → spec → digital-twin → audit chain.
  Treat it as a worked reference, not as work to redo: a pre-solved pipeline should be
  invoked, never re-derived. Reach for this skill only when the deliverable shape is
  genuinely new.
- **Topology:** Routing at the front (an intake node classifies "load calc / spec doc /
  audit request") + Chaining once a request enters the spec→audit path.
- **Gate:** Before an audit finding gets silently applied back to the spec — decide
  explicitly whether audit output overwrites, appends as review comments, or blocks
  pending manual resolution. This is a Step 4 reducer decision, not a runtime afterthought.

## Content / Recurring Pipeline (loop-heavy, low stakes per cycle)

Example: draft → critique → revise → publish, run on a recurring cadence.

- **Topology:** Evaluator-Optimizer, capped at 2–3 iterations. Uncapped loops on marginal
  polish are the most common way this pattern burns tokens for no real quality gain.
- **Gate:** One gate, right before publish — not one per revision cycle. Low per-cycle
  stakes mean over-gating here just adds friction to a recurring task without buying
  meaningful safety.

## Event-Driven / Always-On System (not request-response)

Example: a monitoring or predictive-maintenance pipeline reacting to new sensor data or a
refreshed dataset, rather than a single user prompt starting a traversal.

- **Different concern than the other examples:** the graph is triggered by data arrival,
  not by a request entering at Node 1. Idempotency (can a node safely re-run if triggered
  twice on the same data?) and state persistence across restarts matter more here than the
  routing logic itself.
- **Topology:** Usually still Chaining or Routing per event, but each node needs to be
  safe to re-invoke — capture this as a Step 1 node property ("idempotent: yes/no"), since
  it isn't covered by the pattern table itself.

## Business / Strategy Work (mostly gates, thin topology)

Example: a pricing decision, a market-entry plan, a go/no-go call.

- **Reality check:** these are often *not* graph-shaped at all — a single
  Evaluator-Optimizer loop, or even a plain `brainstorm-ideas` pass, covers it. If Step 3
  produces one cluster with one pattern and zero parallel or routing structure, that's a
  sign the project didn't need this skill in the first place — a well-scoped loop would've
  been faster to design and cheaper to run than a graph.
