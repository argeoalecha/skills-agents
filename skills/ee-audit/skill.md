---
name: ee-audit
description: Cross-checks electrical engagement deliverables — panel schedules, specs, as-built drawings, dashboard thresholds, and standards citations — against each other for internal consistency before client delivery. This is a deliverable-consistency audit for the electrical discipline, NOT the web/security code audit (/audit) and not a substitute for it. Use as a final pass once as-built, load-calc, spec-writer, and digital-twin outputs exist. Triggers on /ee-audit, "check the deliverables", "cross-check the panel schedule", "consistency check before issue", "are the specs and calcs aligned".
---

# Deliverable Consistency Audit

Compare only. Do not calculate, draft, or silently fix mismatches — this skill runs
inline in the main conversation (no `context: fork`) because it needs full visibility
into everything already produced this session. Forking it would blind it to that
context and defeat the point.

Not to be confused with `/audit`, which gates web application code for security and
production readiness. If the engagement includes a digital-twin dashboard, both run:
this one on the engineering deliverables, `/audit` on the dashboard software.

## Checklist

1. Do as-built panel schedule breaker/conductor sizes match `/ee-load-calc` output
   exactly? Any re-derivation in the as-built is a finding, even if it agrees.
2. Does every numeric requirement in the spec trace to a load-calc result or a
   standards-compliance citation?
3. Do digital-twin alarm/threshold values match load-calc's derating values
   (e.g. the 80% continuous flag)? A threshold that drifted from its breaker rating
   is the highest-consequence mismatch in this list — it misinforms an operator.
4. Is every standards citation (PEC article, IEEE clause, RA 7920 reference) present
   and traceable — none asserted without a source? Include **within-document** checks,
   not just cross-document ones: a summary citation table can assert a clean single
   standard (e.g. "meets Class 0.5S") while the same document's body text discloses a
   caveat (e.g. only one of several shortlisted candidates actually meets that tier).
   That's a discrepancy even though both halves are in the same file — a reader who
   extracts only the table gets a wrong impression.
5. Are as-built "field-verified" vs. "assumed" labels still correctly applied after
   any later edits?
6. Did any load-calc result change after downstream deliverables were produced? If so,
   which as-built sheets, spec sections, and dashboard thresholds are now stale?
7. Are panel/feeder IDs identical across as-built, panel schedule, spec, and the
   dashboard mimic? Divergent IDs break operator cross-reference between the drawing
   and the screen.
8. Does any deliverable read as issued-for-construction rather than draft-for-PEE-review?
9. If an arc-flash / incident-energy assessment (`elektra-arc-flash`) exists, does its
   fault-current basis actually trace to an `ee-short-circuit` solve — not an assumed or
   inline-estimated value? And does every bus report both the average- and minimum-
   arcing-current cases, with the higher (governing) incident energy carried forward —
   not the average case alone?

## Output format

Discrepancy list only:

`[Deliverable A] vs [Deliverable B] → [Mismatch] → [Which one appears authoritative — flag for human confirmation, don't auto-resolve]`

If no discrepancies are found, state that explicitly. Don't pad the output with things
that already check out.

Resolution is the engineer's call, not this skill's. Where one source looks
authoritative, say why — don't rewrite the other to match.
