---
name: okf-knowledge
description: Author Open Knowledge Format (OKF) v0.1 concept files — markdown docs with YAML frontmatter that AI agents read as a curated knowledge base. Use this skill whenever the user wants to document a codebase, build a technical wiki, capture a personal knowledge base, write OKF concepts, create an agent-readable knowledge bundle, convert docs/Notion/Obsidian content to OKF, or maintain an LLM wiki. Trigger on mentions of "OKF", "knowledge bundle", "concept file", "agent-readable docs", "knowledge base for agents", "LLM wiki", or requests to turn a project directory, documentation set, or notes into structured markdown an agent can navigate. Covers three modes (project / wiki / personal), validation, index and log generation, and cross-linking.
---

# OKF Knowledge Builder

Author and maintain **Open Knowledge Format (OKF) v0.1** bundles: directories of markdown files with YAML frontmatter that both humans and AI agents read directly. OKF is a *format, not a platform* — no SDK, no runtime, no install. A bundle is just files in a directory, shippable via git, tarball, or any filesystem.

This skill produces bundles that are **conformant** with the canonical Google Cloud spec (`GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md`) and **forward-compatible** with future versions. When in doubt about any rule, consult `references/spec-v0.1.md` — it is the pinned, authoritative copy.

## When OKF is the right tool

OKF is for **stable, curated, human-maintained knowledge** that an agent should treat as authoritative baseline truth: schemas, metric definitions, API specs, runbooks, domain ontologies, decision records, reference notes. It is the layer agents read *before* they touch live data.

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
type: <Type name>                # REQUIRED — non-empty short string
title: <Display name>            # recommended
description: <One-line summary>   # recommended
resource: <Canonical URI>         # recommended when a real asset exists; omit for abstract concepts
tags: [<tag>, <tag>]              # recommended
timestamp: <ISO 8601 datetime>    # recommended — last meaningful change
# any producer-defined keys are allowed and must be preserved
---
```

Recommended fields in priority order: `title`, `description`, `resource`, `tags`, `timestamp`. Add extra keys freely (e.g. `owner`, `status`, `source`) — consumers must tolerate them. Use the current real datetime for `timestamp`; do not invent one. If you don't know the current date, fetch it rather than guessing.

## Cross-linking

Concepts relate to each other via **standard markdown links**. There is NO `links:` frontmatter field — never invent one.

- **Preferred:** bundle-relative absolute paths beginning with `/`, e.g. `[customers](/tables/customers.md)`. These survive file moves within a subdirectory.
- Relative paths (`./other.md`) are allowed but less stable.

The relationship type (depends-on, joins-with, parent-of) is conveyed by surrounding prose, not the link. Broken links are valid — they may point at not-yet-written knowledge.

## Concept ID

A concept's identity is its file path minus `.md`. `tables/orders.md` → concept ID `tables/orders`. Path = identity, so choose paths deliberately and keep them stable.

## Modes

Pick the mode from context; if genuinely ambiguous, ask once. The authoring mechanics are identical across modes — only the conventional `type` vocabulary, directory layout, and body sections differ. Read the matching reference file for templates and type vocabularies:

| Mode | User signal | Reference |
|---|---|---|
| **project** | "document my codebase / repo / API / this project dir" | `references/mode-project.md` |
| **wiki** | "technical wiki / team docs / Notion-style / how-tos / runbooks" | `references/mode-wiki.md` |
| **personal** | "personal knowledge base / my notes / research / second brain" | `references/mode-personal.md` |

Load only the relevant reference file. Each defines suggested `type` values, a directory skeleton, and body section conventions. These are conventions, not constraints — adapt to the user's actual material.

## Workflow

1. **Determine mode** and where the bundle lives (a project subdir like `<repo>/okf/`, a standalone folder like `~/knowledge/`, or cloud storage). OKF doesn't care — it's just files. Confirm the root path.
2. **Read the matching mode reference** for type vocabulary and templates.
3. **Author concepts.** One file per concept. Group related concepts in subdirectories. Write structural markdown (headings, tables, fenced code) over prose — structure aids both human reading and agent retrieval.
4. **Cross-link** related concepts with `/`-absolute markdown links.
5. **Generate `index.md`** per directory for progressive disclosure (see below). Optional but strongly recommended for any bundle an agent will navigate.
6. **Maintain `log.md`** at the root (or per scope) for chronological history when updating an existing bundle.
7. **Wire it into `CLAUDE.md` (project mode only).** A bundle nobody points at doesn't get read. If a project-level `CLAUDE.md` exists at (or above) the bundle root, offer to add or update a short section pointing at it, e.g.:

   ```markdown
   ## Knowledge Base
   This project has an OKF knowledge bundle at `okf/`. Read `okf/index.md` before
   starting any code task — it is the curated source of truth for architecture,
   schema, and API decisions. Keep it in sync when those change (see /okf-knowledge).
   ```

   Insert near the top of `CLAUDE.md`, not buried after unrelated sections — an agent skimming for context should hit it early. If no `CLAUDE.md` exists yet, mention to the user that one should point at the bundle once created (don't create a bare `CLAUDE.md` yourself — that's `/init`'s job). This step is what makes the bundle load-bearing rather than orphaned documentation; skipping it is the most common way an OKF bundle goes stale unread.
8. **Validate** with `scripts/validate.py <bundle-root>` before declaring done.

## index.md (progressive disclosure)

Lets an agent see what's available before opening files. Contains **no frontmatter** (the sole exception: the bundle-root `index.md` MAY carry `okf_version: "0.1"` — see version stability below). Body is grouped link lists:

```markdown
# Tables

* [Orders](/tables/orders.md) - one row per completed order
* [Customers](/tables/customers.md) - customer master record

# Metrics

* [Weekly Active Users](/metrics/wau.md) - distinct users in a 7-day window
```

Entries should reuse each concept's `description`. Generate with `scripts/gen_index.py <directory>`.

## log.md (optional history)

Date-grouped, newest first. ISO `YYYY-MM-DD` headings. Leading bold word is convention:

```markdown
# Update Log

## 2026-06-28
* **Update**: Revised [WAU metric](/metrics/wau.md) to exclude bot traffic.
* **Creation**: Added [cold-start runbook](/runbooks/cold-start.md).
```

## Version stability (forward-compatibility)

OKF versions as `<major>.<minor>`. Minor bumps add backward-compatible fields/headings; major bumps may rename required fields or reserved filenames. To keep bundles durable:

- **Declare the target version.** Put `okf_version: "0.1"` in the bundle-root `index.md` frontmatter — the one place frontmatter is allowed in an index file. This lets future consumers do version-aware best-effort parsing.
- **Depend only on the hard rule** (`type` present). Treat every other field as optional, so a future spec revision can't break your bundle.
- **Never hardcode a central type registry.** Types are producer-chosen by design; a future taxonomy won't invalidate descriptive types.
- **Use `/`-absolute links** so refactors don't break the graph.
- **Keep the pinned spec** in `references/spec-v0.1.md`. If the user reports a newer OKF version, fetch the updated `SPEC.md` from the canonical repo, diff it against the pinned copy, and adjust only what changed — the permissive consumption model means old bundles stay valid.

Following the hard rule plus version declaration is what makes a bundle survive spec evolution: consumers that don't understand a declared version must attempt best-effort consumption rather than refusing the bundle.

## Validation is mandatory before finishing

Always run `scripts/validate.py <bundle-root>` and report the result. It enforces exactly the three conformance rules and flags soft issues (missing recommended fields, broken links) as warnings, not errors — matching the spec's permissive model.
