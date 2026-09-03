---
name: ph-legal-citation-format
description: Philippine legal citation conventions — G.R. No. / R.A. / P.D. / B.P. Blg. / A.M. No. formats, statutory pinpoint cites, and the retrieval-verification checklist that gates every citation before it ships. Used by the atty-sia subagents (atty-sia-compliance, atty-sia-redline, atty-sia-crossborder), not invoked directly by the user. Triggers on "cite this case", "format this citation", "G.R. No.", "R.A. No.", "verify this citation".
---

# Philippine Legal Citation Format

Stateless reference: how to format a citation correctly, and how to gate one before it
ships. Any atty-sia subagent calls this before finalizing output.

---

## Citation formats

| Instrument | Format | Example |
|---|---|---|
| Republic Act | `R.A. No. [number], "[Short Title]" (Approved [date])` | `R.A. No. 11232, "Revised Corporation Code of the Philippines" (Approved Feb. 20, 2019)` |
| Presidential Decree | `P.D. No. [number] (Signed [date])` | `P.D. No. 1445 (Government Auditing Code, Signed June 11, 1978)` |
| Batas Pambansa | `B.P. Blg. [number]` | `B.P. Blg. 68 (Corporation Code, superseded by R.A. 11232)` |
| Supreme Court decision | `[Case Name], G.R. No. [number], [Date Decided]` | `Heirs of Malate v. Gamboa, G.R. No. 170338, Dec. 13, 2007` |
| Administrative Matter | `A.M. No. [number]` | `A.M. No. 25-11-28-SC (AI Governance Framework)` |
| Executive Order | `E.O. No. [number], s. [year]` | `E.O. No. 226, s. 1987 (Omnibus Investments Code)` |
| Statutory pinpoint | `[Instrument], [Art./Sec./Rule] [number]` | `Civil Code, Art. 1191` |
| Agency issuance | `[Agency] [Type] No. [number] ([Date])` | `BIR RMC No. 45-2026 (June 2, 2026)` |
| Case law pinpoint | append the reporter pin cite when quoting a passage | `G.R. No. 170338, at 12` |

Always resolve amendment chains explicitly — cite the current governing text and name
what it amended: `R.A. No. 11976 (Ease of Paying Taxes Act), amending R.A. No. 8424
(NIRC)`. Never cite a superseded provision as if it were current law without flagging
the supersession.

---

## Verification gate — run before every response ships

This is the control for the SC's 2026 AI Governance Framework's named failure mode
(fabricated citations). Every subagent using this skill runs this checklist on its own
draft output before returning it:

1. **List every citation in the draft** — every G.R./R.A./P.D./B.P./A.M./E.O./agency
   issuance, and every statutory pinpoint cite.
2. **For each one, confirm it came from a retrieval this turn** — corpus lookup, web
   fetch, or file read actually performed in this session. Recall from training data
   does not count, even if you're confident it's right.
3. **If a citation cannot be traced to a retrieval this turn**, do not silently drop
   it and do not silently keep it. Mark it inline: `[UNVERIFIED — not retrieved this
   session; confirm before relying on this]`. Say so in the response, don't bury it in
   a footnote.
4. **If retrieval returned nothing on point for a claim the user needs**, say that
   explicitly — "no corpus/web result found for X" — rather than filling the gap from
   training-data recall dressed up as a citation.
5. **Check amendment currency** — for any statute cited, confirm (via retrieval, not
   recall) that the cited provision hasn't been superseded or renumbered since.

A response with zero citations is safer than a response with one fabricated citation
that reads as confident. When in doubt, under-cite and flag the gap.
