---
name: brainstorm
description: >
  Structured ideation and solution generation for business or technical problems,
  grounded in proven methodologies from McKinsey, IDEO, de Bono, Christensen, and others.
  Use this skill whenever the user is stuck, exploring options, or needs to generate
  and evaluate ideas — including architecture decisions, go-to-market strategy, product
  features, debugging approaches, pricing models, root cause analysis, or any open-ended
  problem. Trigger on: "brainstorm", "ideate", "what are my options", "how should I
  approach", "I'm stuck on", "what's the best way to", "give me ideas for", "help me
  think through", "what would you recommend", "how do I solve", "explore options".
  Also trigger proactively when the user describes a problem without a clear solution path,
  even if they don't explicitly ask for brainstorming.
---

# Brainstorm Skill

Structured, methodology-grounded ideation for business and technical problems.
Always: **diverge first** (wide exploration) → **converge** (filter, rank, recommend).
Always name the methodology used so the output is traceable and defensible.

---

## Step 1 — Classify the Problem

Determine the primary problem type to select the right methodology set:

| Type | Signals | Primary References |
|---|---|---|
| **Business strategy / GTM** | market entry, pricing, positioning, revenue model | `references/business.md` + `references/convergence.md` |
| **Product / feature decision** | what to build, prioritization, roadmap | `references/business.md` + `references/convergence.md` |
| **Technical architecture** | stack choice, system design, agent design, infra | `references/technical.md` + `references/convergence.md` |
| **Root cause / debugging** | something broke, performance issue, why X is failing | `references/framing.md` + `references/technical.md` |
| **Creative / open-ended** | stuck, no clear direction, exploring possibilities | `references/ideation.md` + `references/convergence.md` |
| **Prioritization only** | have ideas, need to rank/decide | `references/convergence.md` |

Load the relevant reference file(s) before proceeding. For hybrid problems, load multiple.

---

## Step 2 — Frame the Problem

Before generating ideas, apply structured framing from `references/framing.md`.

Do this inline (no need to present the framing as a separate section unless it adds clarity):

1. **Restate** the problem in one crisp sentence — not the symptom, the actual problem.
2. **Surface assumptions** — what is the user taking for granted that may not be true?
3. **Define the constraint boundary** — what is fixed vs. flexible?
4. **Apply the HMW reframe** — convert the problem into a "How Might We..." statement.

> If the problem is too vague to generate useful ideas, ask **one** clarifying question before proceeding. Do not ask multiple questions.

---

## Step 3 — Select Methodology Set

Based on problem type, select **1–2 primary methodologies** and **1 convergence method**.
Load the appropriate reference files and apply the methodology steps as documented.

**Routing guide:**

```
Business strategy / GTM       → JTBD + Porter's Five Forces → ICE Scoring
Product / feature decision    → Double Diamond + Value Proposition Canvas → RICE
Technical architecture        → First Principles + Constraint Analysis → 2×2 Matrix
Root cause / debugging        → 5 Whys + MECE Issue Tree → Kepner-Tregoe
Creative / open-ended stuck   → Six Thinking Hats + SCAMPER → 2×2 Matrix
Prioritization only           → Kepner-Tregoe Decision Analysis
```

---

## Step 4 — Generate Ideas (Divergent Phase)

Apply the selected methodology to produce **5–10 ideas**.
Group them by lens — not all lenses apply every time, use judgment:

- **Quick Win** — low effort, fast to implement, partial or full solution
- **Strategic** — higher effort, compounding returns, longer horizon
- **Unconventional** — challenges assumptions, potentially disruptive
- **Safe Default** — proven, low-risk, industry-standard approach
- **First Principles** — strips assumptions, rebuilds from atomic truths

Prefer **quality and diversity** over quantity. Avoid listing variations of the same idea.

---

## Step 5 — Evaluate (Convergent Phase)

Apply the selected convergence method from `references/convergence.md`.

Default scoring when no specific method is mandated — **ICE Score**:

| Idea | Impact (1–5) | Confidence (1–5) | Ease (1–5) | ICE Score |
|---|---|---|---|---|
| [Idea] | | | | `(I+C+E)/3` |

For product/feature decisions → use **RICE** (from `references/convergence.md`).
For complex multi-criteria decisions → use **Kepner-Tregoe**.

---

## Step 6 — Recommend

- Recommend **top 1–3 ideas** with 2–3 sentence rationale each.
- Be opinionated. State clearly which is the top pick and why.
- If one idea is clearly dominant, say so directly — don't hedge.
- Flag any idea that scores lower but has strategic upside worth monitoring.

---

## Output Format

```
## Problem
[One-sentence crisp restatement]

**HMW Statement:** How might we [reframe as opportunity]?

## Constraints & Assumptions
- [Fixed constraint]
- [Flexible constraint]
- [Assumption surfaced]

## Methodology Applied
- Framing: [e.g., 5 Whys + HMW — IDEO/Stanford d.school]
- Ideation: [e.g., Six Thinking Hats — Edward de Bono, 1985]
- Convergence: [e.g., ICE Scoring — Sean Ellis, GrowthHackers]

## Ideas

### Quick Wins
- **[Idea name]** — [one-line description]

### Strategic
- **[Idea name]** — [one-line description]

### Unconventional
- **[Idea name]** — [one-line description]

### Safe Default
- **[Idea name]** — [one-line description]

## Evaluation

| Idea | Impact | Confidence | Ease | ICE Score |
|------|--------|------------|------|-----------|
| ...  |        |            |      |           |

## Recommendation

**Top pick: [Idea name]**
[2–3 sentence rationale. Be direct.]

**Also consider: [Idea name]** *(if applicable)*
[1–2 sentence rationale.]
```

---

## Reference Files

| File | Contents | Load When |
|---|---|---|
| `references/framing.md` | MECE, 5 Whys, HMW | Always for root cause or vague problems |
| `references/ideation.md` | SCAMPER, Six Hats, TRIZ, Lateral Thinking | Creative / open-ended problems |
| `references/business.md` | JTBD, Value Proposition Canvas, Porter's Five Forces, Double Diamond | Business, GTM, product problems |
| `references/technical.md` | First Principles, Constraint Analysis, TRIZ (technical) | Architecture, stack, debugging |
| `references/convergence.md` | ICE, RICE, Kepner-Tregoe, 2×2 Matrix | Convergence phase — always load at least one |
