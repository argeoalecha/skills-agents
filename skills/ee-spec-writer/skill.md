---
name: ee-spec-writer
description: Drafts formal technical specification sections (3-part General/Products/Execution format) from load-calc, standards-compliance, and instrumentation-procurement outputs. Use once a technical basis exists for a system or equipment class. Triggers on /ee-spec-writer, "write a spec section", "technical specification", "basis of design", "spec sheet", "SOW technical section", "equipment specification".
context: fork
agent: spec-writer-agent
background: false
---

Draft a technical specification section for: $ARGUMENTS

IMPORTANT: this skill runs in a forked subagent with no access to the main
conversation's history. The invoking prompt MUST supply file paths to the
relevant load-calc output, standards-compliance citations, and procurement
comparison table (e.g. project docs saved to `deliverables/`). Do not assume
any of that is already visible — read it from the referenced files first.

If a required input file was not supplied, say which one is missing and stop.
Drafting a spec section on an unstated technical basis produces language that
looks authoritative and traces to nothing.

## Structure (3-part format)

**Part 1 — General:** scope, applicable standards, submittal requirements. Cite
article/clause from the standards-compliance file provided — never restate a
requirement without a traceable citation.

**Part 2 — Products:** performance requirements stated as measurable criteria
(range, accuracy class, comms protocol, environmental/IP rating) — not brand
names, unless the procurement comparison table shows a genuine sole-source case.

**Part 3 — Execution:** installation, testing/commissioning, acceptance criteria.

## Rules

- Never let a single vendor's datasheet language become the spec requirement
  verbatim — that inadvertently single-sources the bid. Write performance-based
  requirements the vendor's product happens to meet.
- Where more than one compliant option exists in the procurement comparison,
  write "basis of design, or approved equal."
- Every numeric requirement must trace to the load-calc file or a standards
  citation — flag anything you can't trace back to a source file.
- Output clean markdown, section-numbered.

## Handoff

- Client-facing formatting → `document-skills:docx`. Keep the markdown source as
  the editable master; the .docx is a render, not the source of truth.
- Instrument schedules and BOQ tables → `document-skills:xlsx`.
- Cross-check against sibling deliverables before issue → `/ee-audit`.

## Revision drift

If load-calc or procurement outputs are updated after a section is drafted, the
affected sections are stale. Name them explicitly for re-issue rather than
letting a spec quietly diverge from its calc basis.

## Licensure boundary

Output is **draft for PEE review**, not an issued-for-construction document.
Under RA 7920 the sealing engineer owns every number in it.

## Note on routing

`context: fork` + named `agent:` has had version-dependent bugs in Claude Code
(some releases run the skill inline instead of dispatching to the named
subagent). If invoking `/ee-spec-writer` doesn't visibly hand off to
`spec-writer-agent`, invoke that subagent directly — its system prompt covers
the same ground.
