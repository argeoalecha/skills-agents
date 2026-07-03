# OKF v0.1 — Pinned Spec Reference

Authoritative source: `GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md` (v0.1 Draft, published 2026-06-12, Apache 2.0). This is a condensed, faithful pin. If the user reports a newer version, fetch the live SPEC.md and diff against this file.

## Conformance (the only hard rules)

A bundle is conformant with OKF v0.1 if:

1. Every non-reserved `.md` file contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows its defined structure when present.

Consumers MUST NOT reject a bundle for: missing optional fields, unknown `type` values, unknown additional keys, broken cross-links, or missing `index.md` files. This permissive model is intentional.

## Terminology

- **Knowledge Bundle** — self-contained hierarchical collection of concept docs; the unit of distribution.
- **Concept** — one unit of knowledge = one markdown file. May describe a tangible asset (table, API) or abstract idea (metric, process).
- **Concept ID** — file path minus `.md`. `tables/users.md` → `tables/users`.
- **Frontmatter** — YAML block delimited by `---` at file top.
- **Body** — everything after frontmatter.
- **Link** — markdown link expressing a relationship beyond parent/child.
- **Citation** — link to an external source backing a body claim.

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

### Reserved filenames

| Filename | Purpose |
|---|---|
| `index.md` | Directory listing (§6) |
| `log.md` | Update history (§7) |

All other `.md` files are concepts.

## Frontmatter fields

**Required:** `type` — short descriptive string. Not centrally registered; consumers tolerate unknown types as generic concepts.

**Recommended (priority order):** `title`, `description`, `resource`, `tags`, `timestamp` (ISO 8601).

**Extensions:** any additional keys allowed; consumers preserve them and must not reject on unknown keys.

## Body conventions

Favor structural markdown (headings, lists, tables, fenced code) over prose. No required sections. Conventional headings:

| Heading | Purpose |
|---|---|
| `# Schema` | Columns/fields of an asset |
| `# Examples` | Concrete usage, often fenced code |
| `# Citations` | External sources (§8) |

## Cross-linking

- **Absolute (bundle-relative):** begins with `/`, relative to bundle root. **Recommended** — stable under moves.
- **Relative:** standard `./path.md`.
- No `links:` frontmatter field exists.
- Link A→B asserts an untyped relationship; kind is conveyed by prose.
- Broken links are tolerated (may be not-yet-written knowledge).

## index.md

No frontmatter (except bundle-root may carry `okf_version`). Grouped link lists:

```markdown
# Group Heading

* [Title](/path/to/concept.md) - description from frontmatter
```

Producers may auto-generate; consumers may synthesize on the fly.

## log.md

Date-grouped, newest first, ISO `YYYY-MM-DD` headings:

```markdown
# Update Log

## 2026-05-22
* **Update**: Added [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established [Dataplex Playbook](/playbooks/dataplex.md).
```

Leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`) is convention, not requirement.

## Citations

List under `# Citations` at document bottom, numbered. Links may be absolute URLs, bundle-relative paths, or paths into a `references/` subdir mirroring external material as first-class concepts.

## Versioning

`<major>.<minor>`. Minor = backward-compatible additions. Major = possible breaking changes (renamed required fields, changed reserved filenames). Bundles MAY declare version via `okf_version: "0.1"` in bundle-root `index.md` frontmatter (the only place frontmatter is permitted in an index). Consumers that don't understand a declared version SHOULD attempt best-effort consumption, not refuse.

## Non-goals (do not attempt)

- Defining a fixed taxonomy of types.
- Prescribing storage/serving/query infrastructure.
- Replacing domain schemas (Avro, Protobuf, OpenAPI) — OKF references them.
