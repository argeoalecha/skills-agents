---
name: okf-knowledge
description: Author Open Knowledge Format (OKF) v0.2 concept files — markdown docs with YAML frontmatter that AI agents read as a curated, trust-annotated knowledge base. Use this skill whenever the user wants to document a codebase, build a technical wiki, capture a personal knowledge base, write OKF concepts, create an agent-readable knowledge bundle, convert docs/Notion/Obsidian content to OKF, migrate an OKF v0.1 bundle to v0.2, or maintain an LLM wiki. Trigger on mentions of "OKF", "knowledge bundle", "concept file", "agent-readable docs", "knowledge base for agents", "LLM wiki", "attested computation", or requests to turn a project directory, documentation set, or notes into structured markdown an agent can navigate. Covers three modes (project / wiki / personal), provenance/trust/lifecycle frontmatter, v0.1→v0.2 migration, validation, index and log generation, and cross-linking.
---

# OKF Knowledge Builder

Author and maintain **Open Knowledge Format (OKF) v0.2** bundles: directories of markdown files with YAML frontmatter that both humans and AI agents read directly. OKF is a *format, not a platform* — no SDK, no runtime, no install. A bundle is just files in a directory, shippable via git, tarball, or any filesystem.

This skill produces bundles that are **conformant** with the canonical spec (`GoogleCloudPlatform/open-knowledge-format/SPEC.md` — the copy under `knowledge-catalog/okf/` is a frozen snapshot, don't use it) and **forward-compatible** with future versions. When in doubt about any rule, consult `references/spec-v0.2.md` — it is the pinned, authoritative copy.

## When OKF is the right tool

OKF is for **stable, curated knowledge** that an agent should treat as authoritative baseline truth: schemas, metric definitions, API specs, runbooks, domain ontologies, decision records, reference notes. It is the layer agents read *before* they touch live data. v0.2 assumes much of that corpus is agent-written and agent-maintained, so it adds frontmatter that tells a consumer where each concept came from, whether anyone checked it, and whether it is still current.

It is NOT a replacement for RAG (which retrieves chunks from large, changing corpora at query time) or MCP (which connects agents to live tools at runtime). OKF complements both: OKF supplies curated definitions; RAG supplies supporting evidence; MCP serves the bundle to deployed agents. If the user's knowledge is large, noisy, and frequently changing, recommend RAG instead. If it is curated and stable, OKF fits.

## The one hard rule (conformance)

A bundle is conformant if and only if:

1. Every non-reserved `.md` file has a parseable YAML frontmatter block delimited by `---` lines.
2. Every frontmatter block has a non-empty `type` field.
3. Reserved files (`index.md`, `log.md`) follow their defined structure when present.

Everything else is soft guidance. Never reject or refuse to produce a bundle over missing optional fields, unknown types, broken links, or missing index files — the spec mandates permissive consumption. The only thing you must never omit is a non-empty `type` on every concept.

## Frontmatter (apply to every concept)

```yaml
---
type: <Type name>                 # REQUIRED — non-empty short string
title: <Display name>             # recommended
description: <One-line summary>   # recommended
resource: <Canonical URI>         # recommended when a real asset exists; omit for abstract concepts
tags: [<tag>, <tag>]              # recommended — a YAML list
generated: { by: <actor>, at: <ISO 8601 datetime with offset> }   # write on every concept you create or change
sources:                          # when the concept derives from identifiable material
  - id: <stable-key>
    resource: <URL | /bundle/path.md | scope descriptor>
    title: <label>
status: stable                    # draft | stable | deprecated — only these values
# verified, stale_after, and any producer-defined keys as needed
---
```

Rules that trip people up:

- **No `timestamp`.** v0.1's `timestamp` is superseded by `generated.at`. Never write `timestamp` in a new or updated concept.
- **Every timestamp has an explicit offset.** `2026-09-25T10:30:00Z` or `2026-09-25T18:30:00+08:00` — never a bare date or an offset-less datetime. Use the real current time (`date -u +%Y-%m-%dT%H:%M:%SZ`); never invent one.
- **`status` is a lifecycle field** with exactly three values. Put domain states (ADR `accepted`, project `active`) in a different key, e.g. `decision_status`.
- **Extra keys are allowed** (`owner`, `decision_status`, …) and consumers must preserve them.

## Provenance, trust, and lifecycle

These families are optional, but their presence is what makes an agent-maintained bundle trustable. Apply them honestly:

**Actors** (`generated.by`, `verified[].by`, `sources[].author`):

| Who | Actor string |
|---|---|
| You (Claude Code) writing a concept | `claude-code/<model-id>`, e.g. `claude-code/claude-opus-5-5` |
| The user writing or dictating it by hand | `human:<id>` (their git username) |
| A script or scheduled job | `process:<id>` |

**`generated`** — who produced the current content and when. When you write or substantively rewrite a concept, set `generated.by` to your own actor and `generated.at` to now. When the user hand-authors it, use their `human:` actor.

**`verified`** — who confirmed the content against its sources. **Never add a `verified` entry on your own authority.** Add `{ by: human:<id>, at: <now> }` only when the user explicitly says they reviewed that concept, and `process:<id>` only when a real automated check actually ran. Absent `verified` = unverified, which is the honest default for anything you draft. Trust tiers derive from it: no `verified` → unverified; non-human only → machine-confirmed; any `human:` → human-reviewed.

**`sources` + footnotes** — replace v0.1's body `# Citations` list. Each entry needs a `resource`; give it an `id` when the body cites it, and attribute specific claims with a footnote whose label is that id:

```markdown
The chunks table uses an HNSW index.[^migration-012]

[^migration-012]: Migration 012 — vector index
```

Optional credibility signals per source: `author` (actor), `last_modified` (when the source changed), `usage_count` (framed by a sibling `usage_window: { from, to }`). Record only signals you actually observed — never estimate a `usage_count`.

**`status` / `stale_after`** — `draft` for incomplete or speculative concepts, `deprecated` for superseded ones kept for links and history. Set `stale_after` (absolute instant) when the knowledge has a known shelf life — pricing, fee schedules, quarterly figures, time-boxed policies.

## Cross-linking

Concepts relate to each other via **standard markdown links**. There is NO `links:` frontmatter field — never invent one.

- **Preferred:** bundle-relative absolute paths beginning with `/`, e.g. `[customers](/tables/customers.md)`. These survive file moves within a subdirectory.
- Relative paths (`./other.md`, `../tables/x.md`) are allowed. Use them when the bundle must render with working links on GitHub, which resolves `/` against the repo root rather than the bundle root.

The relationship type (depends-on, joins-with, parent-of) is conveyed by surrounding prose, not the link. Broken links are valid — they may point at not-yet-written knowledge. Linking to another concept from `sources[].resource` expresses lineage.

## Concept ID

A concept's identity is its file path minus `.md`. `tables/orders.md` → concept ID `tables/orders`. Path = identity, so choose paths deliberately and keep them stable.

## Attested Computation (when a number must be computed the sanctioned way)

When a metric, KPI, or figure has one blessed computation that agents must run rather than improvise, put it in its own concept of `type: Attested Computation` and have the `Metric` concept link to it. One computation per value. Contract fields: `runtime` (required), `parameters` (`{ name, type, required }`), the query in a single fenced block under `# Computation` (or a `computation:` file path), `executor: { resource, receipt }`, and `attester: { resource }` pointing at deterministic no-LLM check code, usually under `references/`. Agents only supply parameter values — they never edit the computation.

Use it only when the user has a real runner and attester, or asks to design them. For a metric that is just a definition, a plain `Metric` concept with the SQL in `# Definition` is enough. Full contract and example: `references/spec-v0.2.md` → Attested Computation; project-mode template in `references/mode-project.md`.

## Modes

Pick the mode from context; if genuinely ambiguous, ask once. The authoring mechanics are identical across modes — only the conventional `type` vocabulary, directory layout, and body sections differ. Read the matching reference file for templates and type vocabularies:

| Mode | User signal | Reference |
|---|---|---|
| **project** | "document my codebase / repo / API / this project dir" | `references/mode-project.md` |
| **wiki** | "technical wiki / team docs / Notion-style / how-tos / runbooks" | `references/mode-wiki.md` |
| **personal** | "personal knowledge base / my notes / research / second brain" | `references/mode-personal.md` |

Load only the relevant reference file. Each defines suggested `type` values, a directory skeleton, and body section conventions. These are conventions, not constraints — adapt to the user's actual material.

## Workflow

1. **Determine mode** and where the bundle lives (a project subdir like `<repo>/okf/`, a standalone folder like `~/knowledge/`, or cloud storage). OKF doesn't care — it's just files. Confirm the root path. If a bundle already exists there, check its root `okf_version` — if it is `0.1` or absent and concepts carry `timestamp`, offer the migration below before adding to it.
2. **Read the matching mode reference** for type vocabulary and templates.
3. **Author concepts.** One file per concept. Group related concepts in subdirectories. Write structural markdown (headings, tables, fenced code) over prose — structure aids both human reading and agent retrieval. Set `generated` on every concept you write; record `sources` for anything derived from identifiable material.
4. **Cross-link** related concepts with `/`-absolute markdown links.
5. **Generate `index.md`** per directory for progressive disclosure (see below). Optional but strongly recommended for any bundle an agent will navigate.
6. **Maintain `log.md`** at the root (or per scope) for chronological history when updating an existing bundle.
7. **Wire it into `CLAUDE.md` (project mode only).** A bundle nobody points at doesn't get read. If a project-level `CLAUDE.md` exists at (or above) the bundle root, offer to add or update a short section pointing at it, e.g.:

   ```markdown
   ## Knowledge Base
   This project has an OKF knowledge bundle at `okf/`. Read `okf/index.md` before
   starting any code task — it is the curated source of truth for architecture,
   schema, and API decisions. Prefer human-reviewed concepts (`verified` by a
   `human:` actor); treat `status: draft` and past-`stale_after` concepts as
   leads to confirm, not facts. Keep it in sync when those change (see /okf-knowledge).
   ```

   Insert near the top of `CLAUDE.md`, not buried after unrelated sections — an agent skimming for context should hit it early. If no `CLAUDE.md` exists yet, mention to the user that one should point at the bundle once created (don't create a bare `CLAUDE.md` yourself — that's `/init`'s job). This step is what makes the bundle load-bearing rather than orphaned documentation; skipping it is the most common way an OKF bundle goes stale unread.
8. **Validate** with `uv run scripts/validate.py <bundle-root>` before declaring done.
9. **Report trust state.** Tell the user which concepts are unverified drafts you wrote, and that they can ask you to mark specific concepts `verified` by them once reviewed.

## Migrating a v0.1 bundle

v0.2 consumers still read v0.1 bundles (legacy `timestamp` and `# Citations` fall back gracefully), so migration is an upgrade, not a repair. Do it when the user asks, or offer it when you are about to edit a v0.1 bundle. Per concept:

1. `timestamp: X` → `generated: { by: <actor>, at: X }`. The original author is usually unknown — use `human:<id>` only if the user confirms they wrote it by hand, otherwise ask; if the user does not know, use `process:okf-v01-import`. Normalize `X` to carry an explicit offset.
2. `# Citations` list → `sources:` entries (give each an `id`), and add `[^id]` footnotes on the claims they back where that mapping is clear. Remove the `# Citations` section.
3. Any producer `status:` value outside `draft | stable | deprecated` → move to another key (e.g. `decision_status`) and set `status` from it (`superseded` → `deprecated`, `proposed` → `draft`, otherwise omit).
4. Root `index.md` → `okf_version: "0.2"`.
5. Add a `log.md` entry: `* **Update**: Migrated bundle to OKF v0.2.`

Do not add `verified` during migration — nobody has re-confirmed the content. Run `uv run scripts/validate.py`; its v0.1-legacy warnings list anything missed.

## index.md (progressive disclosure)

Lets an agent see what's available before opening files. Contains **no frontmatter** (the sole exception: the bundle-root `index.md` MAY carry `okf_version: "0.2"`). Body is grouped link lists:

```markdown
# Tables

* [Orders](/tables/orders.md) - one row per completed order
* [Customers](/tables/customers.md) - customer master record

# Metrics

* [Weekly Active Users](/metrics/wau.md) - distinct users in a 7-day window
```

Entries should reuse each concept's `description`. Generate with `scripts/gen_index.py <directory>` (add `--root` at the bundle root to write the `okf_version` declaration).

## log.md (optional history)

Date-grouped, newest first. Date headings MUST be ISO `YYYY-MM-DD`. Leading bold word is convention:

```markdown
# Update Log

## 2026-09-25
* **Update**: Revised [WAU metric](/metrics/wau.md) to exclude bot traffic.
* **Creation**: Added [cold-start runbook](/runbooks/cold-start.md).
* **Deprecation**: Marked [legacy ETL](/runbooks/legacy-etl.md) `status: deprecated`.
```

## Version stability (forward-compatibility)

OKF versions as `<major>.<minor>`. Minor bumps add backward-compatible fields/headings; major bumps may rename required fields or reserved filenames. To keep bundles durable:

- **Declare the target version.** Put `okf_version: "0.2"` in the bundle-root `index.md` frontmatter — the one place frontmatter is allowed in an index file.
- **Depend only on the hard rule** (`type` present). Treat every other field as optional, so a future spec revision can't break your bundle.
- **Never hardcode a central type registry.** Types are producer-chosen by design.
- **Use `/`-absolute links** so refactors don't break the graph.
- **Keep the pinned spec** in `references/spec-v0.2.md`. If the user reports a newer OKF version, fetch `SPEC.md` from `GoogleCloudPlatform/open-knowledge-format`, diff it against the pinned copy, and adjust only what changed — the permissive consumption model means old bundles stay valid.

## Validation is mandatory before finishing

Always run `uv run scripts/validate.py <bundle-root>` and report the result. It fails (exit 1) only on the three conformance rules — unparseable frontmatter, missing `type`, malformed `index.md`/`log.md`. Everything else — missing recommended fields, v0.1 legacy fields, timestamps without offsets, invalid `status` values, malformed `generated`/`verified`/`sources`, footnotes with no matching source, Attested Computations missing `runtime`, broken links — is reported as a warning, matching the spec's permissive model. Fix warnings in concepts you wrote; mention them for concepts you didn't. `uv run` pulls in PyYAML from the script's inline metadata; plain `python3 scripts/validate.py` also works but skips the nested-field checks (`generated`, `verified`, `sources`) and can miss malformed YAML.
