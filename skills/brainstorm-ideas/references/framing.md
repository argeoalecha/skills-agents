# Framing Methodologies

Use these before ideation. Framing the right problem is more valuable than generating solutions to the wrong one.

---

## 1. MECE Issue Tree
**Source:** McKinsey & Company — core consulting framework, widely documented in *The McKinsey Way* (Ethan Rasiel, 1999)
**Answers:** What are all the dimensions of this problem, with no overlap and no gaps?

### Application
1. State the top-level problem as a question (e.g., "Why is revenue declining?")
2. Break it into **mutually exclusive** branches (each branch covers a distinct cause/dimension)
3. Ensure branches are **collectively exhaustive** (together they cover all possibilities)
4. Drill down 2–3 levels until you reach actionable, testable hypotheses
5. Use the leaf nodes as your problem-solving agenda

### Structure
```
Problem
├── Branch A (mutually exclusive from B, C)
│   ├── Sub-branch A1
│   └── Sub-branch A2
├── Branch B
│   ├── Sub-branch B1
│   └── Sub-branch B2
└── Branch C
```

### Example
Problem: "Our SaaS churn rate is too high"
```
Churn
├── Product issues
│   ├── Missing features
│   └── UX/usability problems
├── Customer success failure
│   ├── Onboarding gaps
│   └── Lack of ongoing engagement
└── Value-price mismatch
    ├── Pricing too high for perceived value
    └── Competitive alternatives are better
```

---

## 2. Five Whys
**Source:** Toyota Production System — developed by Sakichi Toyoda, formalized by Taiichi Ohno in *Toyota Production System* (1978)
**Answers:** What is the root cause beneath the surface symptom?

### Application
1. State the observable problem (the symptom)
2. Ask "Why did this happen?" — record the answer
3. Ask "Why?" to that answer
4. Repeat until you reach a root cause (usually 3–6 iterations — 5 is a guideline, not a rule)
5. The root cause is typically a system, process, or structural failure — not a person

### Rules
- Each "Why" must be answered with a **specific, factual statement** — not a guess
- Stop when you reach something you can actually fix
- If the answer is "we don't know," that's a valid finding — it means you need data first

### Example
Symptom: "The client didn't renew their contract."
- Why? → They said the reports weren't useful.
- Why? → Reports only showed raw data, no interpretation.
- Why? → The dashboard was built for volume, not insight.
- Why? → Requirements were gathered from the IT team, not the end user.
- **Root cause:** Discovery process bypassed the actual decision-maker.

---

## 3. How Might We (HMW)
**Source:** IDEO and Stanford d.school Design Thinking methodology — documented in *Change By Design* (Tim Brown, 2009) and IDEO.org design kit
**Answers:** How do we convert a constraint or problem into an actionable opportunity statement?

### Application
1. Take the problem or root cause identified
2. Reframe it using the structure: **"How might we [desired outcome] so that [benefit]?"**
3. The statement should be:
   - Broad enough to allow multiple solutions
   - Narrow enough to be actionable
   - Framed as an opportunity, not a constraint
4. Generate 2–3 HMW variants at different levels of abstraction
5. Select the one that best opens up useful solution space

### Abstraction levels
- **Too narrow:** "How might we add a PDF export button?" (prescribes solution)
- **Too broad:** "How might we make clients happy?" (no useful constraint)
- **Just right:** "How might we give clients instant clarity on their KPIs without requiring a call?"

### Example
Problem: Clients are not renewing because reports feel useless.
- HMW make reports feel like insights, not data dumps?
- HMW reduce the time between data and decision for the client?
- HMW make every report feel personally relevant to the client's specific goals?
