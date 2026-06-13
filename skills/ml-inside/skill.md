---
name: ml-inside
description: Writes a comprehensive ML Algorithm & Calculation Specification document for any project that ALREADY CONTAINS a built machine learning or AI pipeline. Covers system architecture, input features, every calculation step (with formulas, parameter tables, and interpretation), algorithm selection rationale with comparative analysis, accuracy assurances, known limitations, and a scheduled training/testing plan. Produces both Markdown and optionally HTML output. Triggers on "document the ML", "write the algorithm spec", "document the model calculations", "write the ml-algorithms doc", "explain how the model works", "write the calculation spec", "spec out the ML pipeline", "document the AI pipeline", or any request to produce technical documentation for an existing ML/AI pipeline. NOT for building, selecting, validating, or tuning a model — use /ml-ops for that.
---

# ML Algorithm & Calculation Specification — Document Writer

Produces a structured, audience-ready specification document covering every calculation step from raw input to final output score or prediction. Modelled after the RotaBrain `docs/ml-algorithms.md` template — that document is the canonical style reference for depth, tone, and structure.

**Companion skill — `/ml-ops`:** builds, validates, and maintains the model. `/ml-ops` produces `MODEL_REPORT.md` (algorithm decision record, validation results, accuracy gates, fairness audit, drift schedule) and a `models/manifest.json`. **If those artifacts exist, lift content from them — do not re-derive.** This skill is the human-readable spec; `/ml-ops` is the operational runbook.

**Hand-off rule:** If the pipeline does not yet exist (no trained model, no `MODEL_REPORT.md`, no scoring code), stop and recommend `/ml-ops` instead. `/ml-inside` documents what is; it does not design what should be.

---

## What This Skill Produces

A single Markdown file (default: `docs/ml-algorithms.md`) with five sections:

```
Section 1 — System Architecture Overview    (ASCII data-flow diagram + narrative)
Section 2 — Input Features / Data           (table: name, unit, source, schema column, typical range)
Section 3 — Step-by-Step Calculation Pipeline
  Step N-1 — Preprocessing / Data Fetch
  Step N   — Each algorithm or transformation (formula + params + outputs)
    Step Na — Algorithm Selection (comparative analysis, rejections, roadmap)
  Step N+1 — Post-processing / Score derivation
  Step N+2 — Derived statistics / aggregations
  Step N+3 — AI/LLM layer (if present)
Section 4 — Accuracy Assurances             (calibration, limitations table, guardrails)
Section 5 — Scheduled Training & Testing    (schedule, benchmark procedure, acceptance criteria, test matrix)
```

---

## Phase 1 — Codebase Survey

Before writing a single line of the document, read the project. The document must reflect the actual code, not general ML knowledge.

### 1pre. Check for `/ml-ops` artifacts first

These files, if present, are authoritative and should be lifted into the spec rather than re-derived:

```bash
# Operational runbook from /ml-ops
test -f MODEL_REPORT.md && echo "FOUND: MODEL_REPORT.md (use for Constraint Summary, Algorithm Decision Record, Accuracy Results, Fairness, Maintenance Schedule)"
test -f ML_REPORT.md    && echo "FOUND: ML_REPORT.md (legacy name — same role as MODEL_REPORT.md)"

# Model manifest (single source of truth for version, seed, data snapshot, latency)
test -f models/manifest.json && cat models/manifest.json

# Outstanding remediation items (failed gates from /ml-ops)
grep -A 20 "## ML Model Remediation" TODO.md 2>/dev/null
```

If `MODEL_REPORT.md` exists:
- Section 1 narrative cites the architecture from it
- Section 3a (Algorithm Selection) lifts the Algorithm Decision Record verbatim — do not re-invent rejection reasons
- Section 4 (Accuracy Assurances) lifts validation design, acceptance gates, calibration, fairness audit (if present)
- Section 5 (Scheduled Training & Testing) lifts the Maintenance Schedule
- Any FAIL gates in MODEL_REPORT.md become entries in Section 4's Known Limitations table with "tracked in TODO.md"

If no `MODEL_REPORT.md` exists, proceed with the full codebase survey below — but flag this in the Output as a recommendation to run `/ml-ops` to produce one.

### 1a. Locate the ML Pipeline

```bash
# Find ML scripts (Python, R, notebooks)
find . -name "*.py" | grep -v __pycache__ | grep -v .venv | head -30
find . -name "*.ipynb" | head -10
find . -name "*.R" | head -10

# Find model or scoring utilities
grep -rl "fit\|predict\|transform\|score_samples\|anomaly\|health_score\|forecast\|classify" \
  --include="*.py" --include="*.ts" --include="*.js" . | grep -v node_modules | grep -v .next

# Find API routes that serve ML output
find . -path "*/api/*" -name "*.ts" | grep -v node_modules | head -20
find . -path "*/routes/*" -name "*.py" | head -10

# Find schema files
find . -name "schema.sql" -o -name "*.prisma" -o -name "*.sql" | grep -v node_modules | head -10
find . -name "models.py" | grep -v node_modules | head -5
```

### 1b. Read Every ML File End-to-End

Read each ML script identified above completely. Extract:

**From each script/module, capture:**
- **Inputs**: column names, table names, API params, data types
- **Preprocessing steps**: imputation method, scaling, encoding, feature derivation, temporal sorting
- **Each algorithm used**: library, class name, parameters and their values
- **Formulas**: every formula written in code — extract it symbolically (not just as code)
- **Outputs**: column names, value ranges, what they represent
- **Thresholds**: every numeric cutoff used for classification, severity, status
- **Randomness controls**: random seeds, determinism mechanisms

**From API routes:**
- What inputs are accepted (query params, request body)
- What data is fetched and from where
- What is computed vs pre-computed
- What is returned and its schema

**From schema files:**
- Table structures relevant to ML
- Column types, nullability, constraints
- Views that derive computed values

**From config / environment:**
- Model parameters passed via environment or CLI flags
- API keys for LLM services

### 1c. Identify AI/LLM Layers

```bash
# Check for Claude / OpenAI / LLM usage
grep -rl "anthropic\|openai\|claude\|gpt\|llm\|chat.completions\|messages.create" \
  --include="*.py" --include="*.ts" --include="*.js" . | grep -v node_modules
```

If found, read the prompt construction code. Extract:
- Model ID and version
- max_tokens, temperature, streaming mode
- System prompt persona (summarise in one sentence)
- Required output structure enforced by the prompt
- Any guardrails (forbidden phrases, bounded length, required fields)

### 1d. Identify Algorithm Selection History

If there is no explicit comparison document, reconstruct from context:
- What algorithms are imported but not used (commented out, tried and removed)?
- Are there any comments, docstrings, or commit messages explaining a choice?
- What libraries are in `requirements.txt`, `pyproject.toml`, or `package.json`?

```bash
grep -r "sklearn\|xgboost\|lightgbm\|catboost\|river\|statsmodels\|scipy\|torch\|tensorflow" \
  requirements.txt pyproject.toml setup.py 2>/dev/null

git log --all --oneline | grep -i "model\|algorithm\|detect\|anomaly\|score\|pipeline" | head -20
```

---

## Phase 2 — Clarify Gaps

**First check `MODEL_REPORT.md` (Phase 1pre).** If it exists, items 3–6 below are already answered there — lift them. Only ask the user for items not covered by the report (typically audience and domain context).

If any of the following still cannot be determined, ask the user before writing:

1. **Audience** — who reads this document? (engineers, QA, technical sales, regulators?) This sets tone and assumed background knowledge.
2. **Domain context** — what is the subject-matter domain? (O&G, finance, healthcare, logistics, e-commerce?) This determines what "normal range" and "anomaly" mean.
3. **Algorithm selection history** — which alternatives were considered and why was this one chosen? *Lifted from `MODEL_REPORT.md` → Algorithm Decision Record if present.* If code gives no signal and no report, ask.
4. **Benchmark dataset** — what labelled or reference dataset (if any) validates the model? *Lifted from `MODEL_REPORT.md` → Validation Design if present.*
5. **Acceptance criteria** — what threshold must be met before production? *Lifted from `MODEL_REPORT.md` → Accuracy Results if present.*
6. **Scheduled retraining** — persisted vs ephemeral, cadence. *Lifted from `MODEL_REPORT.md` → Maintenance Schedule if present.*
7. **Fairness requirements** (regulated decisions) — *lifted from `MODEL_REPORT.md` § 6e if present.*

Do **not** invent answers. Mark unknown items as `[TBD — confirm with engineering]` in the draft and surface them to the user after generating.

---

## Phase 3 — Write the Document

Write to `docs/ml-algorithms.md` (create `docs/` if it does not exist). Follow the structure below exactly. Use the RotaBrain document as the style and depth reference.

---

### Document Header

```markdown
# {Project Name} — ML Algorithms & Calculation Reference

> Audience: {audience}. Covers every calculation step from raw {input type} to {final output} and {secondary output if any}.

---
```

---

### Section 1 — System Architecture Overview

Draw an ASCII data-flow diagram. Every component in the pipeline must appear:

```
{Raw data source / external system}
        │
        ▼
{Input table / data store}  ({technology})
        │
        ▼  {script or service name}  ({language} — {run mode: scheduled / on-demand / real-time})
        │  ├── {Algorithm 1}
        │  └── {Algorithm 2}
        │
        ▼
{Output table / data store}  ({technology})
        │
        ├──▶  {Consumer 1}  ({technology})
        │         └── {What it does with the output}
        │
        └──▶  {Consumer 2}  ({technology})
                  └── {What it does with the output}
```

Follow the diagram with a 2–3 sentence narrative explaining the separation of concerns: which layer does ML inference vs. which layer reads pre-computed results. Be explicit about where computation happens and where it does not.

---

### Section 2 — Input Features / Data

Table format:

```markdown
| Feature / Tag | Unit | Schema Column | Source | Typical Range / Domain |
|---|---|---|---|---|
| {name} | {unit or "dimensionless"} | `{column_name}` | {table or API field} | {range or enum values} |
```

After the table, state: which columns are nullable, how nulls are handled downstream, and whether any feature is derived vs. raw.

---

### Section 3 — Step-by-Step Calculation Pipeline

Number each step sequentially. Every step gets this structure:

```markdown
### Step {N} — {Step Name}

**What it is:** One to three sentences explaining the purpose of this step in non-specialist language. What problem does it solve and why is it in the pipeline?

**Formula:**

{Mathematical notation — symbolic, not code. Use the format:}

  output = f(input_1, input_2, ...)

  where:
    variable_1 = definition
    variable_2 = definition

**Implementation details (`{file}:{line range}`):**

| Parameter | Value | Rationale |
|---|---|---|
| {param_name} | {exact value} | {one-sentence reason this value was chosen} |

**Interpretation:**

| {Output range or tier} | Meaning |
|---|---|
| {value or range} | {what this means to a practitioner} |

**Output columns / fields stored:**
- `{column_name}` — {description, value range, polarity}

{Optional closing sentence: the key property of this output that makes it important to the next step.}
```

#### Step for the Primary Algorithm — Include Section Na

When documenting the main ML algorithm, insert a sub-section `Step {N}a — Algorithm Selection` immediately after the step header, before the configuration table. This sub-section must contain:

**Na.1 — Evaluation Criteria**

A table of the project-specific constraints that governed algorithm selection:

```markdown
| Constraint | Why it matters |
|---|---|
| {constraint specific to this project's data and deployment} | {domain-specific consequence} |
```

Include only constraints that are real and specific to this project. Generic constraints (e.g. "must be accurate") are not constraints.

**Na.2 — Candidate Algorithm Comparison**

A table of every algorithm that was seriously considered (minimum 4, ideally 6–9):

```markdown
| Algorithm | Training Complexity | Score Type | Distribution Assumption | Key Parameters | Cold-Start | Verdict |
|---|---|---|---|---|---|---|
| **{Selected}** | O(...) | {continuous/binary} | {none/Gaussian/etc} | {params} | {good/poor} | **Selected** |
| {Retained} | ... | ... | ... | ... | ... | Retained as complementary layer |
| {Rejected A} | ... | ... | ... | ... | ... | Rejected |
| {Deferred B} | ... | ... | ... | ... | ... | Deferred to Phase {N} |
```

Verdict values: **Selected**, Retained, Rejected, Deferred.

**Na.3 — Why Each Was Rejected or Deferred**

One to four paragraphs per non-selected candidate. Each paragraph must:
- Name the candidate's genuine strength (not straw-man it)
- State the specific, domain-grounded reason it was disqualified
- Be honest if it is "better in theory but impractical for this project's constraints"

Use this structure:

```markdown
**{Algorithm Name}**
{Strength}: ... {Disqualifying factor specific to this project}: ...
{Optional}: if conditions change in Phase N, this algorithm becomes viable again because ...
```

**Na.4 — Why the Selected Algorithm Wins**

A table showing the selected algorithm against every hard constraint from Na.1:

```markdown
| Criterion | {Selected Algorithm} |
|---|---|
| {Constraint from Na.1} | {How the algorithm satisfies it} |
```

End with a paragraph explaining the combination of methods if multiple algorithms are used together (e.g. univariate + multivariate, or heuristic + statistical). Explain what failure pattern each catches that the other misses.

**Na.5 — Known Weaknesses and Mitigations**

```markdown
| Weakness | Detail | Mitigation in {Project Name} |
|---|---|---|
| {known algorithmic limitation} | {specific scenario where it fails} | {what the project does to reduce impact} |
```

**Na.6 — Planned Algorithm Improvements (Roadmap)**

For each planned upgrade:

```markdown
**{Phase N} ({near-term / medium-term / long-term}): {Upgrade Name}**
{What it improves, why, and the condition that must be met before it can be adopted.}
{If a code snippet illustrates the upgrade, include it.}
```

---

### Section 4 — Accuracy Assurances

Write one sub-section per accuracy mechanism actually implemented in the code. Do not invent mechanisms that do not exist. Common sub-sections, adapted to the project:

**Parameter Calibration**
How the most sensitive parameter(s) are chosen. What happens if they are too high or too low. Whether per-entity overrides are supported.

**Baseline Adaptation**
How the model or statistical baseline adapts to changing operating conditions over time. What it absorbs and what it cannot absorb.

**Complementary Method Advantage**
If multiple methods are used in combination, explain explicitly what the combination catches that neither method alone would catch.

**Determinism / Reproducibility**
Whether re-running on the same data produces identical results. Why this matters for auditability.

**Score Conservatism / Formula Design**
For derived scores (health scores, risk scores), explain the weight choices and why they prevent double-penalisation, floor/ceiling logic, and proportional vs. catastrophic scaling.

**AI/LLM Guardrails** (if an LLM layer exists)
The specific prompt-level rules that prevent common failure modes:
- What vague language is forbidden
- What the output must commit to
- Tone rules (e.g. tone shift at health score threshold)
- Word/token budget and why it exists

**Fairness Audit** (regulated decisions only — lending, credit, hiring, insurance, healthcare triage)

If the pipeline influences a regulated decision, document the audit results — lift from `MODEL_REPORT.md` § 6e if `/ml-ops` has produced one. For PH-targeted projects, cross-reference RA 10173 automated-decision rights (`/ph-dpa-compliance`).

```markdown
| Protected Attribute | Disparate Impact Ratio | Equalised Odds Gap | Verdict |
|---|---|---|---|
| {attribute} | {ratio} (≥ 0.80 = 4/5 rule pass) | {gap} | PASS / FAIL |
```

State explicitly whether the attribute is in the feature set or only used for held-back audit (proxies like zip/education/name can still leak protected information).

**Reproducibility**

Document the inputs required to exactly reproduce a given model version — lift from `models/manifest.json` if present:

| Field | Value |
|---|---|
| Model version | `v{N}` |
| RNG seed | `{int}` |
| Data snapshot | `{hash or query timestamp}` |
| Environment pin | `{requirements.txt hash / lockfile commit}` |
| Trained at | `{ISO timestamp}` |

**Known Limitations**

```markdown
| Limitation | Impact | Mitigation |
|---|---|---|
| {what the model cannot do} | {what this means in practice} | {the specific counter-measure or acceptance of the gap} |
```

Be honest. Limitations that have no mitigation should say "accepted at MVP — revisit in Phase {N}." Do not omit real limitations.

---

### Section 5 — Scheduled Training & Testing

> Operational depth (drift detection thresholds, retraining checklist, model registry schema) is `/ml-ops`'s territory — Phase 8 of that skill. This section summarises the cadence and acceptance criteria for the spec audience; for the full runbook, link to `MODEL_REPORT.md`.

#### Current State

State whether models are:
- **Persisted**: trained once, serialised to a file, loaded at inference time
- **Ephemeral**: re-trained on every pipeline run from raw data (fit-and-discard)
- **Online/incremental**: updated with each new batch without a full refit

Explain the design choice and its trade-offs.

#### Recommended Schedule (Production)

```markdown
| Cadence | Action | Command or trigger |
|---|---|---|
| {Daily / Hourly / Real-time} | {What runs} | `{command or API call}` |
| {Weekly} | {What runs} | `{command}` |
| {Monthly} | {What runs} | Manual review or script |
| {Quarterly} | {What runs} | Compare against ground truth |
```

#### Automated Scheduling (if applicable)

If the project uses a scheduler (cron, Vercel cron, Celery, Airflow, etc.), show the configuration snippet:

```ts / python / yaml
// {scheduler config — planned or implemented}
// mark as "planned — not yet implemented" if not in code
```

State what the scheduled endpoint must do and that it must be protected from anonymous access.

#### Benchmarking / Validation Procedure

If a reference dataset or benchmark exists, document the procedure step-by-step:

```markdown
**{Benchmark dataset name}** — {one-sentence description, source URL}

**Validation procedure:**
1. Download: {command or URL}
2. Load: {command}
3. Run: {command}
4. Compare: {what to compare against what}
5. Compute: {metric at threshold values}
6. Select: {what decision the result drives}

**Acceptance criteria for {Phase N} sign-off:**
- {Metric} ≥ {threshold} — {plain-language meaning}
- {Metric} ≥ {threshold} — {plain-language meaning}
- {Metric} ≥ {threshold} — {plain-language meaning}
```

If no benchmark exists yet, document the planned validation approach and state when it will be executed.

#### Testing Requirements

```markdown
| Test | Type | Target file | Scope |
|---|---|---|---|
| {function} — {scenario} | Unit | `{file}` | {what is verified} |
| {formula parity test} | Unit | `{file}` | {parity between two implementations} |
| {API contract test} | Integration | {tool} | {what contract is verified} |
| {E2E happy path} | E2E | {tool} | {full pipeline} |
```

Always include a **Critical Invariant** block at the bottom of the test table — any formula, threshold, or business rule that must remain identical across multiple implementations (e.g. Python vs TypeScript) and that would cause a silent data inconsistency if they diverged. State exactly what would break and how a test prevents it.

---

## Phase 4 — Post-Write Checklist

Before delivering the document, verify:

```
Content completeness
  Every algorithm in the codebase appears in the document                PASS / FAIL
  Every parameter in the code appears in a parameter table               PASS / FAIL
  Every threshold in the code appears with a rationale                   PASS / FAIL
  Every output column is named and described                             PASS / FAIL
  Algorithm selection section has ≥ 4 candidates                        PASS / FAIL
  Every rejected candidate has a domain-grounded reason                  PASS / FAIL
  Known limitations table is non-empty                                   PASS / FAIL
  Reproducibility block populated (seed, data snapshot, env pin)         PASS / FAIL
  Fairness audit included if model is regulated (or marked N/A)          PASS / FAIL

Formula accuracy
  All formulas verified against actual code — no approximations         PASS / FAIL
  Parameter values match code exactly — no paraphrasing                 PASS / FAIL
  All symbolic variables are defined below each formula                  PASS / FAIL

Source consistency
  If MODEL_REPORT.md exists, the spec matches it (no contradictions)    PASS / FAIL
  Failed gates from MODEL_REPORT.md appear in Known Limitations         PASS / FAIL

Gaps flagged
  Any item marked [TBD] is listed explicitly to the user after output   PASS / FAIL
```

---

## Phase 5 — HTML Version (Optional)

If the user requests an HTML version (explicitly or if they mention "styled doc", "HTML", "share with client", "send to sales"):

1. Use the Hayah Midnight design system (if this is a Hayah-AI project) or the project's own design system
2. The HTML must be a single self-contained file (inline CSS, no external dependencies)
3. Include a sticky sidebar table of contents with IntersectionObserver active-link tracking
4. Use the same five-section structure
5. Write to `docs/ml-algorithms.html` and add it to `.gitignore` under "Internal docs"
6. Deliver via SendUserFile after writing

For the HTML version, preserve the exact content of the Markdown version — do not abbreviate, paraphrase, or omit any section.

---

## Output

After writing the file:
1. State the file path and approximate line count
2. List all `[TBD]` items that need the user's input to complete
3. State what the document covers and what it intentionally leaves to `/ml-ops` (validation design, hyperparameter tuning, drift detection thresholds, retraining checklist, fairness audit methodology — those belong in the operational runbook, not the algorithm spec)
4. If no `MODEL_REPORT.md` exists, recommend running `/ml-ops` to produce one — the spec is more complete and trustworthy when paired with the operational runbook
5. If the user asked for HTML, deliver the file via SendUserFile

---

## Rules

### Hand-off
- If no built pipeline exists (no model file, no scoring code, no `MODEL_REPORT.md`), stop and recommend `/ml-ops` — this skill documents what is, not what should be
- If `MODEL_REPORT.md` or `models/manifest.json` exists, treat them as authoritative and lift content; do not re-derive

### Fidelity
- Never write a formula without verifying it against the actual code
- Never invent algorithm selection history — reconstruct from code signals, lift from `MODEL_REPORT.md`, or ask
- Every parameter table must contain the exact value from the code, not a generic default
- Never summarise a limitation with "this may be addressed in a future version" — give it a phase and a concrete condition
- The algorithm selection section must name real competitors, not strawmen; acknowledge their genuine strengths before explaining the rejection

### Completeness
- If a calculation appears in more than one implementation (e.g. Python + TypeScript), document both and call out the critical invariant requirement
- The Reproducibility block (seed, data snapshot, env pin) is non-negotiable — pull from `models/manifest.json` or mark `[TBD]`
- Fairness audit is required for regulated decisions; if absent in `MODEL_REPORT.md`, flag `[TBD — run /ml-ops § 6e]` and continue

### Audience
- The document is a living spec, not a one-time artifact — write it so that a new engineer can read it and fully understand the pipeline without looking at the code
