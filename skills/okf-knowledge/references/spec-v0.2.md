# OKF v0.2 — Pinned Spec Reference

Authoritative source: `GoogleCloudPlatform/open-knowledge-format/SPEC.md` (v0.2, last revised 2026-08-21, Apache 2.0). The older copy under `GoogleCloudPlatform/knowledge-catalog/okf/` is a frozen snapshot — do not use it. This is a condensed, faithful pin. If the user reports a newer version, fetch the live SPEC.md and diff against this file.

## Conformance (the only hard rules)

A bundle is conformant with OKF v0.2 if:

1. Every non-reserved `.md` file contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows its defined structure when present.

When the trust, lifecycle, provenance, or computation families are present, producers SHOULD follow them as specified, and consumers:

- MUST treat a bare `verified` mapping as a one-element list.
- MUST NOT reject a concept for missing any optional family.
- SHOULD derive trust tiers and staleness only from the fields specified here, and SHOULD surface, not silently drop, a failing attestation.

Consumers MUST NOT reject a bundle for: missing optional fields, unknown `type` values, unknown additional keys, broken cross-links, or missing `index.md` files.

## Terminology

- **Knowledge Bundle** — self-contained hierarchical collection of concept docs; the unit of distribution.
- **Concept** — one unit of knowledge = one markdown file.
- **Concept ID** — file path minus `.md`. `tables/users.md` → `tables/users`.
- **Source** — a material a concept derives from, recorded in `sources`. **Provenance** = the set of sources.
- **Credibility signal** — objective per-source fact (`author`, `usage_count`, `last_modified`). OKF records signals, never a score.
- **Actor** — who/what performed an action: `<producer>/<version>`, `human:<id>`, or `process:<id>`.
- **Trust tier** — derived from `verified`: unverified, machine-confirmed, human-reviewed.
- **Attested Computation** — a concept carrying a sanctioned way to compute a value.
- **Executor** / **Receipt** / **Attester** — run instructions that return a receipt; the runtime evidence (never stored in the bundle); deterministic no-LLM code that turns a receipt into a verdict.

## Bundle structure

```
bundle/
├── index.md          # optional, progressive disclosure
├── log.md            # optional, change history
├── <concept>.md
└── <subdir>/
    ├── index.md
    └── <concept>.md
```

Distributable as: git repo (recommended), tarball/zip, or subdirectory of a larger repo.

Reserved filenames at any level (MUST NOT be used for concepts): `index.md`, `log.md`. All other `.md` files are concepts. There is no tag-index file; consumers synthesize tag views from `tags`.

## Frontmatter fields

**Required:** `type` — short descriptive string. Not centrally registered; consumers tolerate unknown types.

**Recommended:** `title`, `description`, `resource`, `tags` (YAML list).

**Optional families** (§5 and §10 of the spec) — see below.

**Extensions:** any additional keys allowed; consumers preserve them and must not reject on unknown keys.

**Timestamps:** every timestamp-valued key is an ISO 8601 datetime with an explicit UTC offset, e.g. `2026-06-30T14:00:00Z`. Bare dates and offset-less datetimes are non-conforming values.

## Provenance: `sources`

```yaml
sources:
  - id: ga4-schema                       # optional; SHOULD be present when the body cites it
    resource: https://developers.google.com/analytics/bigquery/export-schema   # REQUIRED in each entry
    title: GA4 BigQuery Export schema    # optional
    author: team:ga4-docs                # optional credibility signal (actor convention)
    usage_count: 5000                    # optional; exercises over usage_window
    last_modified: 2026-05-30T00:00:00Z  # optional; when the SOURCE last changed
usage_window: { from: 2026-06-01T00:00:00Z, to: 2026-06-30T00:00:00Z }   # sibling of sources
```

- `resource` may be an absolute URL, a bundle-relative path, a path into `references/`, or a scope descriptor (e.g. `all queries in BigQuery project X`).
- A single entry MAY carry its own `usage_window` to override the shared one.
- `usage_count` is a coarse liveness/trend signal, not a ranking.
- Lineage is expressed through links: when a source `resource` is another OKF concept, consumers may recurse into its `sources`. No `derived_from` field in v0.2.

**Per-claim attribution** uses markdown footnotes whose label is a `sources[].id`:

```markdown
The `events_` table is sharded daily.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

The label is the join key; keyed (not positional) so it survives agents reordering the list.

## Trust: `generated` and `verified`

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `generated.by` REQUIRED within `generated` (an actor). `generated.at` = last meaningful content change.
- `verified` = list of `{ by, at }` confirmation events. A single bare `{ by, at }` mapping is allowed and treated as a one-element list.
- `verified` is independent of `generated.at` — content can change without re-confirmation, and vice versa.

**Trust tiers** (advisory, not access control):

- No `verified` ⇒ **unverified**
- `verified` by non-`human:` actors only ⇒ **machine-confirmed**
- `verified` by any `human:<id>` ⇒ **human-reviewed**

## Lifecycle: `status`, `stale_after`

```yaml
status: stable                       # draft | stable | deprecated; absent ⇒ stable
stale_after: 2026-09-23T00:00:00Z    # stale when now >= stale_after (absolute instant, not a TTL)
```

## Actor convention

Used by `generated.by`, `verified[].by`, and `sources[].author`:

- `<producer>/<version>` — agents and tools (`reference_agent/gemini-2.5-pro`)
- `human:<id>` — a person. Producers MUST use it for hand-authored or human-confirmed content.
- `process:<id>` — an automated process (`process:finance-nightly`)

## Body conventions

Favor structural markdown. No required sections. Conventional headings:

| Heading | Purpose |
|---|---|
| `# Schema` | Columns/fields of an asset |
| `# Examples` | Concrete usage, often fenced code |
| `# Computation` | The sanctioned computation of an Attested Computation |

## Cross-linking and paths

- **Absolute (bundle-relative):** begins with `/`. **Recommended** — stable under moves.
- **Relative:** standard `./path.md`, `../dir/x.md`.
- No `links:` frontmatter field. Link A→B is an untyped relationship; prose conveys its kind.
- Broken links are tolerated.
- Path-valued fields (`resource`, `sources[].resource`, `computation`, `executor.resource`, `attester.resource`) accept an absolute URL, a `/`-bundle-relative path, or a relative path.
- `references/` subdirectory conventionally mirrors external material, run instructions, and attester code as first-class content. Convention, not requirement.

## index.md

No frontmatter, except a bundle-root `index.md` MAY carry `okf_version`. Grouped link lists:

```markdown
# Group Heading

* [Title](relative-url) - description from frontmatter
* [Subdirectory](subdir/) - short description
```

Producers may auto-generate; consumers may synthesize on the fly.

## log.md

Date-grouped, newest first. Date headings MUST be ISO `YYYY-MM-DD`:

```markdown
# Update Log

## 2026-05-22
* **Update**: Added [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established [Dataplex Playbook](/playbooks/dataplex.md).
```

Leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`) is convention.

## Attested Computation

A standalone concept (`type: Attested Computation`) holding the sanctioned way to compute one value. Concepts that use the value (a `Metric`, a table) link to it. One computation per value — revenue, profit, and margin are three concepts, each verifying, staling, and attesting independently.

Contract fields (top-level frontmatter, in addition to the families above):

- `runtime` — REQUIRED for this type. How to run it (`bigquery`, `postgres`, `dbt`, `python`, `Looker`); defines what `parameters` mean.
- `parameters` — list of `{ name, type, required }`; the only holes an agent may fill.
- `computation` — optional path to a file holding the computation. Absent ⇒ the single fenced block under `# Computation` in the body is the computation.
- `executor` — `{ resource, receipt }`: run instructions/code, and the fields a run must return (e.g. `[job_id, executed_sql, result]`).
- `attester` — `{ resource }`: deterministic (no-LLM) code that checks a receipt, run consumer-side.

```markdown
---
type: Attested Computation
title: Revenue for fiscal year
description: Recognized revenue for a fiscal year, per Finance's definition.
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/revenue.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-09-23T00:00:00Z
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
---

# Computation

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = @year

Binds only the declared `parameters`, per the recognition policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

Rules: the agent MAY only supply parameter values; it MUST NOT author or edit the computation. The consumer binds the computation; the attester re-derives the binding and compares it to the expanded artifact in the receipt (`executed_sql`, `compiled_sql`).

Consumer flow (informative): discover → load contract → parameterize → execute (receipt) → attest → gate (refuse on failing attestation; warn or refuse when `now >= stale_after`; surface the verdict on success). Receipts and verdicts are runtime artifacts, never stored in the bundle.

`verified` confirms the *definition* still matches policy (doc-level, slow, stored). Attestation confirms a single *run* (per-call, runtime, not stored). Both are needed.

## Versioning

`<major>.<minor>`. Minor = backward-compatible additions. Major = possible breaking changes. Declare with `okf_version: "0.2"` in bundle-root `index.md` frontmatter (the only place frontmatter is permitted in an index). Consumers that don't understand a declared version SHOULD attempt best-effort consumption.

Deferred to a future revision: receipt/verdict wire formats, attester ABI and sandboxing, attestation caching, semantic-layer (Looker/dbt) attestation templates.

## Changes from v0.1

**Breaking (with consumer fallbacks):**

- `timestamp` → superseded by `generated: { by, at }`. Consumers MAY fall back to legacy `timestamp`.
- Body `# Citations` list → superseded by frontmatter `sources` + keyed footnotes. Consumers MAY still parse legacy `# Citations`.

**Additive:** `sources` + credibility signals + `usage_window`; `generated`, `verified`; `status`, `stale_after`; the actor convention; `Attested Computation` with `runtime`, `parameters`, `computation`, `executor`, `attester`; `# Computation` heading.

Unchanged: bundle structure, reserved filenames, required `type`, recommended `title`/`description`/`resource`/`tags`, cross-linking, index and log files, permissive conformance.

### Migrating a v0.1 concept

| v0.1 | v0.2 |
|---|---|
| `timestamp: 2026-05-28T22:53:05+00:00` | `generated: { by: <actor>, at: 2026-05-28T22:53:05Z }` |
| `# Citations` numbered list in body | `sources:` entries with `id`, and `[^id]` footnotes on the claims they back |
| producer `status:` with custom values | `status: draft \| stable \| deprecated`; move custom values to another key |
| SQL/formula in prose | optional: split into an `Attested Computation` concept and link to it |
| root `index.md` `okf_version: "0.1"` | `okf_version: "0.2"` |

## Non-goals (do not attempt)

- Defining a fixed taxonomy of types.
- Prescribing storage/serving/query infrastructure.
- Replacing domain schemas (Avro, Protobuf, OpenAPI) — OKF references them.
- Specifying packaging/invocation of executor or attester code — OKF fixes the interface only.
