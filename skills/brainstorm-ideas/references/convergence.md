# Convergence & Prioritization Methodologies

Use in the convergent phase to filter, score, and rank ideas generated during ideation.
Select the method that best matches the decision context.

---

## Method Selection Guide

| Situation | Recommended Method |
|---|---|
| Fast prioritization, early-stage ideas, solo decisions | **ICE Scoring** |
| Product features, roadmap, stakeholder-facing decisions | **RICE Framework** |
| High-stakes decisions with multiple must-have criteria | **Kepner-Tregoe Decision Analysis** |
| Visual mapping of effort vs. impact, quick team alignment | **2×2 Prioritization Matrix** |
| Root-cause hypothesis triage (which cause to investigate first) | **2×2 Matrix** — Likelihood × Ease of verification |
| Distinguishing table-stakes from delighters; new-product/UX opportunities | **Kano Model** |
| Fixed-deadline release scope; fast stakeholder alignment on in/out | **MoSCoW** |
| Portfolio-level sequencing across teams; many competing time-critical items | **WSJF** |
| Early concept screening on desirability, feasibility, and viability together | **DFV (IDEO)** |

### On layering, not just picking

Modern practice (2025) treats these as a stack, not a single choice — prioritization is less about the score and more about a consistent, defensible decision. A common layering: **WSJF** for cross-team sequencing → **RICE** for backlog management → **MoSCoW** for release/sprint scope → **ICE** for experiment triage. Or upstream-to-downstream: **Kano** to identify high-excitement features → **RICE** to score them → **MoSCoW** to bound scope → **WSJF** to order execution. Use one method when the decision is contained; layer when the decision spans stages or audiences.

---

## 1. ICE Scoring
**Source:** Sean Ellis, GrowthHackers — developed as part of the Growth Hacking methodology (~2010), widely adopted in lean startup and product growth contexts
**Answers:** Which ideas give the most output for the least input, with the most certainty?
**Best for:** Early-stage prioritization; marketing experiments; feature ideas; any situation needing fast, defensible ranking

### Formula
```
ICE Score = (Impact + Confidence + Ease) / 3
```

### Scoring Dimensions

| Dimension | Definition | Scoring Guide |
|---|---|---|
| **Impact** (1–10) | How much will this move the target metric if it works? | 10 = transformational, 5 = meaningful, 1 = negligible |
| **Confidence** (1–10) | How certain are you that it will work? Based on data, precedent, or experience | 10 = proven/tested, 5 = educated guess, 1 = pure hypothesis |
| **Ease** (1–10) | How easy is this to implement? Inverse of effort | 10 = hours, 5 = days to weeks, 1 = months or requires new capabilities |

### Application
1. List all candidate ideas
2. Score each on Impact, Confidence, and Ease independently — don't let one dimension anchor the others
3. Calculate ICE Score = average of the three
4. Rank descending by ICE Score
5. Top-ranked items = highest priority; bottom-ranked = deprioritize or kill

### Scoring Table Template

| Idea | Impact | Confidence | Ease | ICE Score |
|---|---|---|---|---|
| [Idea A] | 8 | 7 | 6 | 7.0 |
| [Idea B] | 9 | 4 | 3 | 5.3 |
| [Idea C] | 5 | 8 | 9 | 7.3 |

### Limitation
ICE treats all three dimensions equally. If one dimension matters significantly more in context (e.g., confidence is critical because resources are very limited), use Kepner-Tregoe instead.

---

## 2. RICE Framework
**Source:** Sean McBride, Intercom — published in "RICE: Simple prioritization for product managers" (Intercom Blog, 2016)
**Answers:** Which features or initiatives will deliver the most value given team capacity?
**Best for:** Product roadmap prioritization; feature decisions; initiatives with measurable reach

### Formula
```
RICE Score = (Reach × Impact × Confidence) / Effort
```

### Scoring Dimensions

| Dimension | Definition | Unit |
|---|---|---|
| **Reach** | How many users/customers will this affect in a given period? | Number of people per quarter |
| **Impact** | How much will this move the target metric per person reached? | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| **Confidence** (%) | How confident are you in your Reach and Impact estimates? | 100%=high, 80%=medium, 50%=low |
| **Effort** | How many person-months will this take to build and ship? | Person-months |

### Application
1. Define the time horizon (typically 1 quarter)
2. Estimate Reach based on user data or segment size
3. Rate Impact using the standard scale
4. Set Confidence % based on quality of evidence
5. Estimate Effort honestly — bias toward over-estimation
6. Calculate RICE Score and rank descending
7. Validate top items with stakeholders before committing

### Example

| Feature | Reach | Impact | Confidence | Effort | RICE |
|---|---|---|---|---|---|
| Automated report emails | 200 users | 2 | 80% | 0.5 months | (200×2×0.8)/0.5 = **640** |
| AI chat interface | 200 users | 3 | 50% | 3 months | (200×3×0.5)/3 = **100** |
| CSV export | 80 users | 1 | 100% | 0.25 months | (80×1×1.0)/0.25 = **320** |

**Priority order:** Automated report emails → CSV export → AI chat interface

---

## 3. Kepner-Tregoe Decision Analysis
**Source:** Charles H. Kepner and Benjamin B. Tregoe, *The Rational Manager* (1965), McGraw-Hill; updated in *The New Rational Manager* (1981)
**Answers:** Which option best satisfies our must-have requirements while maximizing want-to-have criteria?
**Best for:** High-stakes decisions; vendor or technology selection; decisions with clear non-negotiables; situations where gut feel needs to be structured

### Core Concept
Decisions have two types of criteria:
- **MUSTs (Musts):** Non-negotiable requirements. Any option that fails a MUST is eliminated immediately.
- **WANTs (Wants):** Desirable criteria. Weighted by importance; used to differentiate remaining options.

### Application

**Step 1 — Define MUSTs**
List binary, non-negotiable requirements. Each is pass/fail.
Example: "Must integrate with Supabase" / "Must cost under $500/month" / "Must be deployable on Netlify"

**Step 2 — Eliminate options that fail any MUST**
Any option that fails even one MUST is out. Do not score it further.

**Step 3 — Define and weight WANTs**
List desirable criteria. Assign a weight 1–10 to each based on relative importance.

**Step 4 — Score remaining options on WANTs**
Score each option on each WANT criterion (1–10).
Calculate Weighted Score = Weight × Score.

**Step 5 — Sum weighted scores and rank**
Highest total = best fit for the wants criteria.

**Step 6 — Assess adverse consequences**
For the top-scoring option(s), identify potential downsides and risks.
Ask: "Is the risk acceptable, or does it change the decision?"

### Scoring Template

| Criterion | Weight | Option A Score | Option A Weighted | Option B Score | Option B Weighted |
|---|---|---|---|---|---|
| [Want 1] | 8 | 7 | 56 | 9 | 72 |
| [Want 2] | 6 | 8 | 48 | 5 | 30 |
| [Want 3] | 9 | 6 | 54 | 8 | 72 |
| **TOTAL** | | | **158** | | **174** |

### Example — LangGraph vs n8n for a lead generation agent
**MUSTs:** Must support conditional branching; must integrate with Supabase; must be maintainable by a solo Python developer

| Want Criterion | Weight | LangGraph | n8n |
|---|---|---|---|
| Python-native | 9 | 9 (81) | 4 (36) |
| Community/docs quality | 7 | 6 (42) | 9 (63) |
| Debugging visibility | 8 | 7 (56) | 8 (64) |
| Scalability to complex workflows | 8 | 9 (72) | 6 (48) |
| Setup speed | 5 | 5 (25) | 9 (45) |
| **Total** | | **276** | **256** |

**Decision:** LangGraph — primarily driven by Python-native and complex workflow scalability weight.

---

## 4. 2×2 Prioritization Matrix
**Source:** Boston Consulting Group — BCG Growth-Share Matrix (1970) established the 2×2 framework pattern; the effort/impact variant is widely attributed to general management consulting practice and is documented in numerous McKinsey and BCG publications
**Answers:** How do we visually categorize options by two competing dimensions to make trade-offs obvious?
**Best for:** Team alignment, quick visual prioritization, workshop facilitation, stakeholder communication

### Standard Effort vs. Impact Matrix

```
         LOW EFFORT          HIGH EFFORT
         ─────────────────────────────────
HIGH  │  QUICK WINS        │  MAJOR PROJECTS  │
      │  Do first          │  Plan carefully  │
      ├────────────────────┼──────────────────┤
LOW   │  FILL-INS          │  THANKLESS TASKS │
      │  Do if time allows │  Avoid or kill   │
      ─────────────────────────────────────────
```

### Application
1. Define the two axes relevant to the decision (Effort/Impact is default; alternatives: Risk/Return, Speed/Quality, Cost/Value)
2. Plot each idea on the matrix based on relative position — not precise scores
3. Cluster ideas that land in the same quadrant
4. Quick Wins → prioritize immediately
5. Major Projects → evaluate with RICE or Kepner-Tregoe before committing
6. Fill-ins → do opportunistically, don't plan around them
7. Thankless Tasks → strong default is to eliminate; challenge why they exist

### Alternative Axis Pairs

| Axis 1 | Axis 2 | Use Case |
|---|---|---|
| Impact | Effort | General prioritization |
| Revenue potential | Implementation risk | Business investment decisions |
| Strategic fit | Time to value | Roadmap planning |
| Confidence | Impact | Experiment prioritization |
| Urgency | Importance | Task management (Eisenhower Matrix variant) |
| Likelihood | Ease of verification | Root-cause hypothesis triage — test high-likelihood, cheap-to-verify causes first |

---

## 5. Kano Model
**Source:** Noriaki Kano, Tokyo University of Science — "Attractive Quality and Must-Be Quality" (1984), *Journal of the Japanese Society for Quality Control*
**Answers:** Which features are table-stakes, which drive satisfaction linearly, and which delight — so we don't over-invest in the wrong tier?
**Best for:** New-product and UX decisions; distinguishing must-haves from differentiators; feeding a customer-centric lens into RICE/MoSCoW backlog work

### Core Concept
Not all features affect satisfaction the same way. Kano classifies each feature by how customer satisfaction responds to its presence or absence:

| Category | Behavior | Investment implication |
|---|---|---|
| **Must-be (Basic)** | Absence causes strong dissatisfaction; presence is merely expected | Non-negotiable floor — fund enough to not fail, no more |
| **Performance (Linear)** | Satisfaction scales with how much you deliver | Invest proportionally to competitive position |
| **Attractive (Delighter)** | Absence is fine; presence delights disproportionately | Cheap delighters are the best ROI; a few can differentiate |
| **Indifferent** | Customers don't care either way | Cut — pure waste |
| **Reverse** | Presence actively dissatisfies some segments | Make optional or remove |

### Application
1. List candidate features
2. For each, ask the Kano question pair: "How do you feel if this feature is present?" and "How do you feel if it is absent?" (functional + dysfunctional)
3. Classify each feature into a category from the answer combination
4. Fund all Must-bes first, invest in Performance features by competitive need, sprinkle a few cheap Attractive features, cut Indifferent ones
5. Re-run periodically — delighters decay into expectations over time (today's delighter is tomorrow's must-be)

### Limitation
Requires real customer input to classify honestly; internal guesses drift toward wishful "everything is a delighter." Pair with RICE to size the winners.

---

## 6. MoSCoW
**Source:** Dai Clegg, Oracle (1994); formalized in the DSDM Agile framework
**Answers:** Given a fixed deadline or budget, what is in and what is out — and can we align stakeholders fast?
**Best for:** Scoping a fixed-deadline release; sprint/scope negotiation; situations where the constraint is time, not idea quality

### The Four Buckets

| Bucket | Meaning | Rule of thumb |
|---|---|---|
| **Must have** | Non-negotiable for this release; without it, the release fails or has no value | Keep Musts ≤ ~60% of effort — if everything is a Must, nothing is |
| **Should have** | Important but not vital; painful to omit but the release survives | Next in line if capacity allows |
| **Could have** | Desirable, low impact if dropped; the first things cut under pressure | Deliver only with spare capacity |
| **Won't have (this time)** | Explicitly out of scope now — recorded, not forgotten | Prevents scope creep by naming the "no" |

### Application
1. Fix the timebox or budget first — MoSCoW only works against a hard constraint
2. Sort every item into one bucket with stakeholders in the room
3. Enforce the effort cap on Musts so there's slack for risk
4. Make "Won't have this time" explicit — the recorded no is what keeps scope honest
5. Revisit each release; buckets are per-timebox, not permanent labels

### Limitation
MoSCoW decides in/out, not order or ROI — it's weak on trade-offs between two Musts. Layer WSJF or RICE for sequencing within the Must/Should tiers.

---

## 7. WSJF (Weighted Shortest Job First)
**Source:** Don Reinertsen, *The Principles of Product Development Flow* (2009); adopted as the prioritization core of SAFe (Scaled Agile Framework)
**Answers:** In what order do we sequence a backlog to maximize economic value delivered per unit of time?
**Best for:** Portfolio- and program-level sequencing; large teams with many competing, time-sensitive items; when 50+ stakeholders need one defensible ordering

### Formula
```
WSJF = Cost of Delay / Job Size (Duration)

Cost of Delay = User/Business Value + Time Criticality + Risk Reduction/Opportunity Enablement
```

### Scoring Dimensions

| Component | Question | Scale |
|---|---|---|
| **User/Business Value** | How much value if delivered? | Relative, e.g. Fibonacci 1–2–3–5–8–13 |
| **Time Criticality** | Does value decay if delayed? Deadlines, competitive windows? | Same relative scale |
| **Risk Reduction / Opportunity Enablement** | Does it de-risk or unlock future work? | Same relative scale |
| **Job Size** | Relative effort/duration to deliver | Same relative scale |

### Application
1. Score the three Cost-of-Delay components for each item on a shared relative scale (estimate as a team to calibrate)
2. Sum them for total Cost of Delay
3. Estimate Job Size on the same scale
4. Compute WSJF = Cost of Delay / Job Size; sequence descending
5. The math favors short, high-value, time-critical jobs — deliberately biasing toward fast economic wins first

### Limitation
Relative estimates invite gaming when incentives differ across teams; the calibration conversation matters more than the number. Overkill for a small solo backlog — use ICE there.

---

## 8. DFV — Desirability, Feasibility, Viability
**Source:** IDEO / Tim Brown, human-centered design; popularized via *Change by Design* (2009). The three-lens screen dates to IDEO practice in the early 2000s.
**Answers:** Before we commit, does this idea clear all three innovation lenses — do people want it, can we build it, and does the business work?
**Best for:** Early concept screening; go/no-go on a new product or venture; catching ideas that are strong on one lens but fatal on another

### The Three Lenses

| Lens | Question | Fatal-flaw signal |
|---|---|---|
| **Desirability** | Do real users want this? Does it solve a job they care about? | "We'd love it" but no evidence anyone else does |
| **Feasibility** | Can we actually build and operate it with what we have (tech, team, ops)? | Depends on capability or infrastructure we don't have |
| **Viability** | Does the business model work — sustainable revenue, cost, margin? | Users want it but won't pay enough to sustain it |

### Application
1. Score each lens 1–10 (or simple pass/concern/fail) for every candidate concept
2. Treat a very low score on **any** lens as a red flag, not something averaging can wash out — DFV is about the weakest link, not the sum
3. Sweet-spot innovation sits where all three overlap; ideas strong on two lenses but weak on the third are the ones to reshape, not fund as-is
4. Use as an upstream gate before RICE/WSJF sizing — no point scoring reach on something that fails viability
5. For each weak lens, generate a targeted fix (cheaper build for feasibility, new revenue model for viability) rather than killing outright

### Relationship to ICE/RICE
DFV screens *whether* an idea is worth pursuing across three qualitative dimensions; ICE/RICE rank *how much* among ideas already deemed worth pursuing. Run DFV first as a gate, then score survivors.
