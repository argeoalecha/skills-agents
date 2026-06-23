---
name: learning-guide
description: >
  Generates a comprehensive, interactive HTML learning guide for any subject or topic.
  Triggers on /learning-guide, "generate a learning guide for", "create a learning guide",
  "build a study guide for", "make a learning path for", "create a course outline for".
  Asks clarifying questions if subject, level, or audience is ambiguous.
user-invocable: true
---

# Learning Guide Skill

Generates a self-paced, non-linear, interactive HTML learning guide for any subject. Output matches the style and interactivity of the hayah-ai Data Analyst Learning Guide: sidebar navigation, progress tracking, mobile-responsive, scrollspy, code blocks with language labels.

**Shell template:** `~/.claude/skills/learning-guide/assets/guide_shell.html`
**Output location:** `/Volumes/1TB_SSD/projects-mvp-ext/learning-guides/<subject-slug>/<subject-slug>_learning_guide.html`

---

## Phase 1 — Invocation

Accepts any of these forms:
```
/learning-guide <subject>
/learning-guide "machine learning for beginners"
/learning-guide react --level intermediate
/learning-guide                          ← triggers clarification
```

**Argument parsing:**
- Positional arg 1: the subject (bare word or phrase)
- Inline descriptors (e.g., "for beginners", "advanced", "from scratch") refine the level
- If no subject is given: go directly to Phase 2

---

## Phase 2 — Clarification

Ask ONLY what is genuinely unclear. Batch all questions into a single `AskUserQuestion` call or a single message. Skip entirely when: the subject is a well-defined technical discipline and the prompt clearly implies a full self-study path.

Questions to ask only if unanswered:
1. **Scope** — Full beginner-to-intermediate path, or a targeted deep-dive on a specific subtopic?
2. **Audience level** — What prior knowledge should the learner already have?
3. **Tool/sub-domain focus** — Which specific tools, frameworks, or sub-domains to cover?
4. **Primary use-case** — Self-study, job prep, certification target, career switch, hobbyist?

---

## Phase 3 — Internal Planning (reason first, no output yet)

Before writing any HTML, determine and record internally:

- **Subject type → presentation mode** (decide this FIRST — it shapes wording and block styles throughout):
  - **Technical** (programming, data, engineering, IT): code-centric. Example artifacts are runnable code; the running example is a **dataset**; exercises say "write / run / build"; the third Resources table is "Datasets & Tools".
  - **Business / Non-technical** (sales, marketing, management, design, writing, finance, soft skills): artifact-centric. Example artifacts are **scripts / frameworks / templates / worksheets** in `.artifact` cards (see Phase 4.0); the running example is a **scenario / case**; exercises say "draft / produce / role-play / map"; the third Resources table is "Tools & Templates".
  - Block type still follows **content**, not just mode: genuine code uses a code block even inside a business guide (e.g., a landing-page HTML snippet), and a technical guide may use an `.artifact` card for a checklist. Mode just sets the default and the wording.
- **Subject slug**: lowercase, hyphens only, no special chars. ("Machine Learning" → `machine-learning`)
- **Page title**: `<Subject> Learning Guide — <Level Descriptor>` (e.g., "Machine Learning Learning Guide — Beginner to Intermediate")
- **Brand fields**:
  - `BRAND_KICKER`: e.g., `Self-Paced · Non-Linear`
  - `BRAND_TITLE`: e.g., `Machine Learning<br>Learning Guide`
  - `BRAND_SUB`: comma-separated tools, e.g., `Python · scikit-learn · Pandas · SQL`
- **Canonical tool list**: 3–8 primary tools/frameworks the subject uses
- **Track structure**: independent parallel tracks (like Excel/Python/SQL) vs. linear progression
- **Phase count**: 3 for linear subjects, 4–5 for multi-track subjects
- **Module count**: 8–18 total (2–6 per phase)
- **Benchmark example**: ONE realistic, domain-authentic running example used in ALL exercises and capstones — a **dataset** for technical subjects ("Superstore Sales") or a **scenario / case** for business subjects ("FitForge, a $3,000 fitness offer"). One running example, every exercise.

---

## Phase 4 — Content Generation

Generate all HTML content sections in order. Every section listed below is REQUIRED.

### 4.0 Artifact Blocks — code vs. card (choose by content)

Every module needs at least one concrete, substantive artifact block. Pick the style by what the block contains:

- **Real code** → dark code terminal: `<pre><code class="language-X">…</code></pre>`. Gets a language label. Use for any actual code, in technical OR business guides (e.g. a landing-page HTML snippet).
- **Script / framework / template / worksheet** (non-code) → light artifact card:
  ```html
  <pre class="artifact" data-kind="SCRIPT"><code>CLOSER call opener
  "What made you book this call today, specifically?"
  ...</code></pre>
  ```
  `data-kind` is shown as the corner label — use `SCRIPT`, `FRAMEWORK`, `TEMPLATE`, `WORKSHEET`, or `CHECKLIST`. No `language-` class on the `<code>`.

Both must contain real, complete content — never pseudocode, `...` ellipsis, or `# TODO` (Quality Rule 4). Technical guides lean on code blocks; business guides lean on artifact cards. The same HTML-escaping rules (Phase 5.0) apply inside both.

### 4.1 Hero Header (with subject mark)

The hero is wrapped in `<div class="hero">`: a `.hero-text` block (h1/h2/h3, kept adjacent so the heading-adjacency CSS works) and a `.hero-mark` block holding an inline SVG that signifies the subject. The shell CSS sizes and positions it (borderless, right-aligned, 84px desktop / 48px mobile).

```html
<div class="hero">
<div class="hero-text">
<h1 id="<subject-slug>-learning-guide"><Subject Name> Learning Guide</h1>
<h2 id="<level-slug>"><Level Descriptor> Track</h2>
<h3><Tool 1> · <Tool 2> · <Tool 3></h3>
</div>
<div class="hero-mark">
<svg viewBox="0 0 256 256" role="img" aria-label="<Subject>" xmlns="http://www.w3.org/2000/svg">
  <!-- inline SVG paths for the subject mark — see rules below -->
</svg>
</div>
</div>
<blockquote class="callout">
<p><strong>How to use this guide — you do NOT have to start at Module 1.1</strong><br>
This guide is built to be <strong>non-linear</strong>. Each module is self-contained with its own prerequisites, skip-check, and outcomes. Use the <strong>Placement Quiz</strong> below to find your entry point, or jump straight to any module using the <strong>Module Index</strong>. Every exercise and capstone uses the same realistic <strong>[Benchmark Dataset]</strong> scenario.</p>
</blockquote>
```

**Choosing the subject mark (always teal-toned):**
1. **Recognizable tech/brand logo silhouette** when the subject has one (Python, React, SQL/database, Docker, etc.) — use the real logo's shape, but recolor it to the brand teal. Do NOT use official brand colors; they clash with the palette.
2. **A clean themed glyph** (Lucide-style line/solid icon) in teal when there's no canonical logo (e.g. "Project Management" → a kanban/board glyph; "Creative Writing" → a pen-nib glyph).

**Mark color rules:**
- Tone everything in the brand teal. For a single-shape glyph use `fill="#075249"` (or `stroke="#075249"` for line icons).
- For a mark with two overlapping/interlocking shapes (like the Python snakes), use TWO teal shades — `#075249` (teal-deep) and `#0d7a6e` (teal) — so the shapes stay legible instead of merging.
- Keep the SVG self-contained (inline paths, a `viewBox`, `role="img"`, and an `aria-label`). No external image references, no `<img>`.

### 4.2 Quick Start

```html
<h2 id="quick-start">Quick Start: Three Ways to Use This Guide</h2>
<ol>
<li><strong>Complete beginner</strong> → Start at Module 1.1 and go sequentially.</li>
<li><strong>Some experience</strong> → Take the <strong>Placement Quiz</strong> (next section) to find your entry point.</li>
<li><strong>Targeting a specific skill</strong> → Jump via the <strong>Module Index</strong> or <strong>Learning Tracks</strong>.</li>
</ol>
```

### 4.3 Placement Quiz

Open with the section heading (use this exact id), then add one quiz section per major track/domain (2–5 sections):

```html
<h2 id="placement-quiz">Placement Quiz — Find Your Starting Point</h2>
<p>Answer honestly. Score 1 point per "yes." Your <strong>lowest-scoring</strong> area is where you should start.</p>
```

Each quiz section:
- 4 yes/no checkbox items: `<li>[ ] I can...</li>` (the JS converts these to real checkboxes)
- Items progress from beginner to intermediate skills
- Scoring key immediately after: `<p><strong>0–1 yes</strong> → Start <strong>Module X.X</strong> | <strong>2–3 yes</strong> → Start <strong>Module Y.Y</strong> | <strong>4 yes</strong> → Skip to <strong>Phase Z</strong></p>`

End the quiz with:
```html
<blockquote class="callout"><p><strong>Rule of thumb:</strong> If you can complete a module's exercise without studying it, skip the module. The exercise <em>is</em> the test-out.</p></blockquote>
```

### 4.4 Module Index (INTERACTIVE — clickable rows)

The table MUST use `class="module-index-table"`, a `<thead>`/`<tbody>` split, and a `data-href="#module-id"` on every `<tbody>` row. The shell JS makes each row clickable and scrolls to that module; the CSS gives rows a pointer cursor, hover highlight, and underlined module number. Each `data-href` must match a real module `id=` in the content (verified in Phase 6.3).

```html
<h2 id="module-index">Module Index (Jump Anywhere)</h2>
<p style="font-size:.82rem;color:var(--ink-soft);margin:.2rem 0 .9rem">Click any row to jump to that module.</p>
<table class="module-index-table">
<thead>
<tr><th>Module</th><th>Topic</th><th>Level</th><th>Prereqs</th><th>Time</th></tr>
</thead>
<tbody>
<tr data-href="#module-11-<slug>"><td>1.1</td><td>[Topic]</td><td>Beginner</td><td>None</td><td>3h</td></tr>
<!-- one <tr data-href="#module-NM-slug"> per module -->
</tbody>
</table>
<blockquote class="callout"><p><strong>Note:</strong> [explain any parallel/independent tracks]</p></blockquote>
```

### 4.5 Learning Tracks

```html
<h2 id="learning-tracks">Learning Tracks (Curated Paths)</h2>
<p>Pick a track based on your goal. Each is a valid subset.</p>
<h3 id="track-1-<slug>">Track 1 — <Name> (<tagline>)</h3>
<p><code>1.1 → 2.1 → 3.2 → Capstone</code><br>
Target cert/outcome: <strong>[Certification or role]</strong></p>
<!-- repeat for 3–5 tracks -->
```

### 4.6 Roadmap Overview

```html
<h2 id="roadmap-overview">Roadmap Overview</h2>
<pre><code>Phase 1 — Foundations      (Weeks 1–N)
Phase 2 — ...              (Weeks N–N)
...
Capstone Projects          (Ongoing)</code></pre>
<p><strong>Dependency map:</strong></p>
<pre><code>1.1 ─┬─ 2.1 ── 2.2 ─┐
     ├─ 3.1 ── 3.2  ├─ Final Capstone
     └─ 4.1 ── 4.2 ─┘</code></pre>
```

### 4.7 Phases and Modules

Each phase opens with:
```html
<h2 id="phase-N-<slug>">Phase N: <Name></h2>
<h3 id="weeks-N-N">Weeks X–Y | Goal: <one-line goal></h3>
<hr />
```

Each module follows this EXACT structure:
```html
<h3 id="module-NM-<slug>">Module N.M — <Title></h3>
<blockquote class="module-meta">
<p><strong>Level:</strong> [Beginner | Beginner–Intermediate | Intermediate | Advanced] · <strong>Prereqs:</strong> [list or None] · <strong>Time:</strong> ~Xh<br>
<strong>Skip-check (test-out):</strong> [one concrete verifiable task]<br>
<strong>Skip if:</strong> [condition describing existing knowledge]<br>
<strong>Unlocks:</strong> [subsequent module numbers or phases]</p>
</blockquote>
```

Then: 2–4 `<h4>` subsections with substantive content. At minimum one artifact block per module (Phase 4.0) — a `language-X` code block for technical content, or a `.artifact` card (`SCRIPT`/`FRAMEWORK`/`TEMPLATE`/`WORKSHEET`) for business content — with REAL, complete content (no pseudocode, no `...`, no `# TODO`).

**Subsection prose should ground knowledge in WHY, not just HOW.** When a subsection states a rule or a how-to step, add one sentence on the consequence of getting it wrong or the reason it matters ("Without RLS, a single missing filter in app code exposes every tenant's data"). Motivation is what makes knowledge stick; a bare instruction is forgotten. Do this in the existing prose — it adds no new blocks.

**Optional learning callouts (use sparingly — a toolkit, not a quota).** Across the WHOLE guide, place roughly **2–4 retrieval prompts** and **1–2 misconception callouts** total — only where the trap or the recall opportunity is genuinely real. Forcing one into every module turns them into noise the learner skims past. Patterns:

- **Retrieval prompt** (drives recall before lookup — builds long-term retention): an `<em>`-wrapped line inside an exercise, or a `callout` before a decision framework. Example: `<p><em>Retrieval practice: attempt step 1 from memory before referring back to the template above. Draft first, then compare — the gaps reveal what you have not yet internalized.</em></p>`
- **Misconception callout** (corrects a predictable wrong belief): `<blockquote class="callout"><p><strong>Common mistake:</strong> …</p></blockquote>` or `<strong>Disambiguation:</strong>` when an acronym/term collides with another common meaning.

Each module ends with:
```html
<p><strong>Exercise N.M — <Title></strong></p>
<p>Dataset: [the benchmark dataset established in Phase 3]</p>
<!-- OPTIONAL: a retrieval-practice line on 1–2 exercises where recall-before-lookup adds value -->
<ol>
<li>[Task 1]</li>
<!-- 4–8 concrete tasks -->
</ol>
<hr />
```

Each phase ends with a capstone:
```html
<h3 id="phase-N-capstone-<slug>">Phase N Capstone: <Title></h3>
<p><strong>Project: <Name></strong></p>
<!-- OPTIONAL self-check (good on 1–2 capstones): gates progress on recall, not completion -->
<blockquote class="callout"><p><strong>Self-check before starting:</strong> Without looking back, can you explain [2–3 core concepts from this phase]? If any draws a blank, re-read that module before attempting the deliverables.</p></blockquote>
<p><strong>Dataset:</strong> [benchmark dataset]</p>
<p><strong>Deliverables:</strong></p>
<ol><!-- 5–8 numbered deliverables --></ol>
<hr />
```

### 4.8 Final Capstone

```html
<h2 id="final-capstone-<slug>">Final Capstone: <Title></h2>
<p><strong>Project: <Name></strong></p>
<p>Integrates all tracks. Uses the benchmark dataset from all phases.</p>
<p><strong>Deliverables:</strong></p>
<ol><!-- 6–10 deliverables --></ol>
<hr />
```

### 4.9 Quick Reference

```html
<h2 id="quick-reference">Quick Reference: <Subject> Tool-Task Matrix</h2>
<table>
<tr><th>Task</th><th>Tool / Function</th><th>Notes</th></tr>
<!-- 8–15 rows mapping common tasks to tools -->
</table>
```

### 4.9.5 Glossary (canonical language — optional but recommended)

For any subject with its own nomenclature, add a glossary between Quick Reference and Resources. It is a printable reference layer: tight, opinionated term definitions that the rest of the guide adheres to. Skip it only for subjects with little specialized vocabulary.

Format each entry as: **term name** (`<dt>`), a 1–2 sentence definition stating what the term *is* — not how to use it (`<dd>`), and an **Avoid** line listing synonyms or near-misses that cause confusion (`<dd class="avoid">`). Cluster terms by phase/domain under `<h3>` subheadings (8–12 terms per cluster is comfortable). Definitions stay 1–2 sentences; be opinionated — when several words mean the same thing, pick one and list the rest as "Avoid". The `dl.glossary` CSS is already in the shell.

```html
<h2 id="glossary">Glossary</h2>
<p>Canonical terms for this guide. Definitions state what a term <em>is</em>, not how to use it. Each <strong style="color:var(--coral)">Avoid</strong> line lists synonyms that cause confusion.</p>
<h3 id="glossary-<cluster-slug>"><Cluster Name></h3>
<dl class="glossary">
<dt><Term></dt>
<dd>[1–2 sentence definition of what it IS.]</dd>
<dd class="avoid"><strong>Avoid:</strong> [synonym], [near-miss] — [why they confuse].</dd>
<!-- 8–12 terms per cluster; one <dl> per cluster -->
</dl>
```

Note for self-paced guides: unlike a teacher-led glossary that grows as a learner demonstrates understanding, this one is pre-populated — that is intentional for a static, printable artifact.

### 4.10 Resources

```html
<h2 id="resources">Learning Resources &amp; Communities</h2>
<h3 id="books">Books</h3>
<table><tr><th>Title</th><th>Focus</th></tr><!-- 4–6 rows --></table>
<h3 id="online-resources">Online Resources</h3>
<table><tr><th>Resource</th><th>Topic</th><th>Notes</th></tr><!-- 6–10 rows --></table>
<h3 id="datasets-and-tools">Datasets &amp; Tools</h3>   <!-- business mode: "Tools &amp; Templates" (id: tools-and-templates) -->
<table><tr><th>Item</th><th>Primary Use</th></tr><!-- 4–6 rows --></table>
<h3 id="communities">Communities</h3>   <!-- the "Wisdom" layer: where the learner tests skills against real practitioners -->
<table><tr><th>Community</th><th>Platform</th><th>Best for</th></tr><!-- 4–6 high-reputation forums/Discords/subreddits, each annotated --></table>
```

The **Communities** group is the Wisdom layer — high-reputation forums, Discords, or subreddits where the learner tests skills against real practitioners. Annotate each with what it is best for. Resources sub-headings are not in the nav, so their ids can follow whichever heading text the mode uses; the `<h2 id="resources">` heading text changes to "Learning Resources &amp; Communities" when a Communities group is present.

### 4.11 Progress Tracker

**Critical:** The Progress Tracker must use real `<ul><li>[ ]</li></ul>` lists — NOT `<pre><code>` blocks. The JS converts these `<li>[ ]` items into checkboxes, and the sidebar "Module progress" meter counts ONLY the checkboxes that appear after the `#progress-tracker` heading. (Placement-quiz `<li>[ ]` items stay interactive but are excluded from the meter.) Putting the tracker in a `<pre>` block makes it inert and leaves the meter empty.

```html
<h2 id="progress-tracker">Progress Tracker</h2>
<blockquote class="module-meta"><p>Check items off as you finish them — this checklist drives the <strong>Module progress</strong> meter in the sidebar. Progress is session-only and resets on reload.</p></blockquote>
<h4>Phase 1 — [NAME]</h4>
<ul>
<li>[ ] Module 1.1 — [Title]</li>
<li>[ ] Exercise 1.1 — [brief label]</li>
<li>[ ] Module 1.2 — [Title]</li>
<li>[ ] Exercise 1.2 — [brief label]</li>
<li>[ ] Capstone 1 — [Title]</li>
</ul>
<!-- one <h4> + <ul> block per phase -->
<h4>Certifications / Outcomes</h4>
<ul>
<li>[ ] [Cert 1]</li>
<li>[ ] [Cert 2]</li>
<li>[ ] [Final Capstone project complete]</li>
</ul>
```

### 4.12 Footer

```html
<p><em>Guide Version 1.0 — <Subject> Track: <Level></em><br>
<em>Non-linear modular design · Placement quiz · [N] modules · ~[X] weeks part-time · hayah-ai</em></p>
```

---

## Phase 5 — HTML Rendering

### 5.0 HTML Escaping (apply to ALL generated text)

This is raw HTML, not Markdown — there is no escaping layer. In every piece of generated text (code blocks, nav labels, table cells, prose), escape these characters or the page renders broken or silently eats content:

- `&` → `&amp;`  (escape this FIRST, before the others)
- `<` → `&lt;`
- `>` → `&gt;`

This matters most inside `<pre><code>` blocks. Examples that WILL break if unescaped: C++/TypeScript generics (`List<T>` → `List&lt;T&gt;`), shell pipes/redirects (`a && b`, `cmd > out` → `a &amp;&amp; b`, `cmd &gt; out`), JSX/HTML samples, and comparison operators (`if x < 5` → `if x &lt; 5`). Nav labels and headings with ampersands: `Tables & Data` → `Tables &amp; Data`.

### 5.1 ID Slug Formula

IDs are generated from heading text:
1. Lowercase all characters
2. Replace spaces and any non-alphanumeric character with `-`
3. Collapse multiple consecutive `-` into one
4. Strip leading and trailing `-`

Examples:
- "Module 1.1 — Data Fundamentals" → `module-11-data-fundamentals`
- "Phase 2: Core Tools" → `phase-2-core-tools`
- "Python & SQL Integration" → `python-sql-integration`
- "EDA: Exploratory Data Analysis" → `eda-exploratory-data-analysis`

**Fixed sections** (Quick Start, Placement Quiz, Module Index, Learning Tracks, Roadmap Overview, Final Capstone, Quick Reference, Glossary, Resources, Progress Tracker) use the short explicit ids shown in their Phase 4 templates (e.g. `quick-start`, `placement-quiz`, `glossary`) — do NOT slug their full heading text. Apply this formula only to derive the `<slug>` portion of **variable** headings: modules, phases, tracks, and capstones.

### 5.2 Nav Tree Construction

Build in strict parallel with the content. Every heading with an `id=` must have a matching `<a href="#id">` in the nav. Use this exact HTML structure:

```html
<!-- Standalone top-level items (not in a group) -->
<a href="#<id>" class="nav-top"><Display Name></a>

<!-- Phase groups -->
<div class="nav-group">
<a href="#phase-N-<slug>" class="nav-top nav-phase">Phase N: <Name></a>
<div class="nav-children">
<a href="#module-N1-<slug>" class="nav-child">Module N.1 — <Title></a>
<a href="#module-N2-<slug>" class="nav-child">Module N.2 — <Title></a>
<a href="#phase-N-capstone-<slug>" class="nav-child">Phase N Capstone: <Title></a>
</div></div>
```

Standalone top-level nav items (in order):
1. The `<h2>` level descriptor (first one after `<h1>`)
2. Quick Start
3. Placement Quiz
4. Module Index
5. Learning Tracks
6. Roadmap Overview
7. [Phase groups for each phase]
8. Final Capstone
9. Quick Reference
10. Glossary (only if the 4.9.5 Glossary section is present)
11. Resources (label as "Resources &amp; Communities" when a Communities group is present)
12. Progress Tracker

### 5.3 Template Substitution (copy-then-Edit — do NOT re-emit the shell)

Do NOT read the whole shell and re-type it into a new Write — that risks corrupting the verbatim CSS/JS and forces one fragile 2000+ line write. Instead:

1. `cp` the shell to the output path (see Phase 6.1):
   ```bash
   cp ~/.claude/skills/learning-guide/assets/guide_shell.html "<output-path>"
   ```
2. Use the **Edit** tool to replace each placeholder in the copied file, one at a time:

| Placeholder | Replace with |
|---|---|
| `{{TITLE}}` | Full page title, e.g., `Machine Learning Learning Guide — Beginner to Intermediate` |
| `{{BRAND_KICKER}}` | e.g., `Self-Paced · Non-Linear` |
| `{{BRAND_TITLE}}` | e.g., `Machine Learning<br>Learning Guide` |
| `{{BRAND_SUB}}` | e.g., `Python · scikit-learn · Pandas · SQL` |
| `{{NAV_TREE}}` | Complete nav HTML built in 5.2 |
| `{{MAIN_CONTENT}}` | All content HTML built in Phase 4 (this is the one large Edit) |

This keeps the chrome (CSS, JS, logo) byte-identical and isolates your generated content to two Edits (`{{NAV_TREE}}`, `{{MAIN_CONTENT}}`) plus four short ones.

For languages not already in the JS map (py, js, ts, sql, dax, m, excel, bash, md, r, css, html, json, yaml): add `<slug>:"<label>"` entries with an Edit at the `/* EXTEND_LANG_MAP */` comment location.

---

## Phase 6 — File Output

### 6.1 Path Formula

```
/Volumes/1TB_SSD/projects-mvp-ext/learning-guides/<subject-slug>/<subject-slug>_learning_guide.html
```

Create the directory with `mkdir -p` before writing. If a file already exists at that path, ask the user: "A guide already exists at `<path>`. Overwrite, or save as `-v2`?"

### 6.2 Write Order

1. Complete all content sections in memory (Phase 4)
2. Build the nav tree (Phase 5.2)
3. `cp` the shell template to the output path
4. Edit each of the 6 placeholders in the copied file (Phase 5.3)
5. Add any new language-map entries at `/* EXTEND_LANG_MAP */`

### 6.3 Verification Checks

Run these immediately after writing:

```bash
# File created and not truncated (this is a truncation guard, NOT a verbosity target)
wc -l <file>
# The shell alone is ~440 lines. A complete guide adds roughly 70–110 lines per
# module plus the supporting sections. Floor: ≥ 1000. A concise, fully-complete
# guide landing anywhere in ~1000–1800 lines is fine — do not pad to hit a number.
# Only a result far below 1000 *with sections missing* signals a truncated Edit
# worth investigating; rely on the module-count and cross-link checks below, not line count, as the real completeness signal.

# No unreplaced placeholders
grep -c "{{" <file>
# Must return 0

# Minimum module count
grep -c 'class="module-meta"' <file>
# Must return ≥ 8

# Progress tracker present
grep -c 'id="progress-tracker"' <file>
# Must return 1

# JavaScript intact (scrollspy)
grep -c 'IntersectionObserver' <file>
# Must return ≥ 1

# Every nav anchor AND module-index row link resolves to a real content id
# (catches broken navigation and dead module-index rows)
{ grep -oE 'href="#[^"]*"' <file> | sed 's/href="#//;s/"//';
  grep -oE 'data-href="#[^"]*"' <file> | sed 's/data-href="#//;s/"//'; } | sort -u > /tmp/lg_link_ids.txt
grep -oE 'id="[^"]*"' <file> | sed 's/id="//;s/"//' | sort -u > /tmp/lg_content_ids.txt
comm -23 /tmp/lg_link_ids.txt /tmp/lg_content_ids.txt
# Must output NOTHING — any line printed is a nav link or module-index row pointing at a missing id

# Module index is the interactive version (clickable rows)
grep -c 'class="module-index-table"' <file>   # must return 1
grep -c 'data-href="#module'         <file>   # must equal the module count

# Hero subject mark is present (inline SVG, teal-toned)
grep -c 'class="hero-mark"' <file>   # must return 1
grep -c '<svg'              <file>   # must return >= 2 (sidebar hayah logo + the subject mark)
grep -c '#075249'           <file>   # must return >= 1 (mark is teal-toned, not brand colors)
```

### 6.4 Summary Output to User

After verification, report:

```
Guide generated: /Volumes/1TB_SSD/projects-mvp-ext/learning-guides/<slug>/<slug>_learning_guide.html

  Lines       : XXXX
  Modules     : XX
  Phases      : X
  Tracks      : X
  Total hours : ~XXXh estimated study time
  Placeholders: 0 unreplaced

Open with:
  open /Volumes/1TB_SSD/projects-mvp-ext/learning-guides/<slug>/<slug>_learning_guide.html
```

---

## Quality Rules (Self-Check Before Writing)

Before calling Write, verify ALL of the following:

1. Every nav `href="#id"` has a corresponding `id=` in the content — no broken anchors
2. Every module listed in the Module Index table appears as an actual `<h3>` in the content
3. Every exercise and capstone uses the SAME benchmark dataset established in Phase 3
4. No artifact block (code block OR `.artifact` card) contains pseudocode, `...` ellipsis, or `# TODO` — every block is real, complete content
5. Every `<blockquote class="module-meta">` has all 5 fields: Level, Prereqs, Time, Skip-check (or Skip if), Unlocks
6. The Progress Tracker uses real `<ul><li>[ ]</li></ul>` lists (NOT `<pre>`) and lists every module, every exercise, and every capstone in the guide
7. All 6 `{{...}}` placeholders (`TITLE`, `BRAND_KICKER`, `BRAND_TITLE`, `BRAND_SUB`, `NAV_TREE`, `MAIN_CONTENT`) are replaced
8. File path matches exactly: `/Volumes/1TB_SSD/projects-mvp-ext/learning-guides/<slug>/<slug>_learning_guide.html`
9. Level badges are only: `Beginner`, `Beginner–Intermediate`, `Intermediate`, or `Advanced`
10. The output file is not truncated — `wc -l` is comfortably above the shell's ~440 lines (typically 1000+, scaling with module count). Completeness of the required sections is the real bar; never pad to hit a line number
11. All `&`, `<`, `>` in generated text are HTML-escaped (`&amp;`, `&lt;`, `&gt;`) — especially inside `<pre><code>` blocks and nav labels (Phase 5.0)
12. The nav/id cross-check (Phase 6.3) prints nothing — no broken anchors or dead module-index rows
13. The Module Index uses `class="module-index-table"` with a `data-href="#module-id"` on every `<tbody>` row (interactive — Phase 4.4)
14. The hero has a `.hero-mark` with an inline, teal-toned SVG that signifies the subject (Phase 4.1) — no `<img>`, no official brand colors
15. Presentation mode is consistent (Phase 3): a business/non-technical guide uses `.artifact` cards (not dark code terminals) for scripts/frameworks/templates, says "scenario/case" not "dataset", and uses produce/draft/role-play exercise verbs — and vice-versa for technical
16. If a Glossary (4.9.5) is present: it uses `<dl class="glossary">` with the `<dt>` / `<dd>` / `<dd class="avoid">` triplet per term, has a matching `glossary` nav entry, and definitions state what each term IS in 1–2 sentences
17. Optional learning callouts are within budget (Phase 4.7): roughly 2–4 retrieval prompts and 1–2 misconception callouts across the WHOLE guide — not one per module. If a Communities group is present, the Resources `<h2>` and its nav label both read "… &amp; Communities"
