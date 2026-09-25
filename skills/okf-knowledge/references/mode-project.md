# Mode: project — document a codebase / repo

Capture the knowledge an agent (or new engineer) needs to work in a codebase: what modules do, how data is shaped, what APIs exist, how to operate the system. This is the layer a coding agent reads before editing code, and what you point `CLAUDE.md` / `AGENTS.md` at.

## Where it lives

Typically a subdirectory of the repo: `<repo>/okf/`. Commit it next to the code it describes so it diffs and reviews through normal PRs ("metadata as code").

## Suggested type vocabulary

Producer-chosen, but consistent types help filtering and graph views. Common ones:

| type | Describes |
|---|---|
| `Module` / `Service` | A code module, package, or service |
| `API Endpoint` | A single HTTP/RPC endpoint |
| `Table` / `Schema` | A database table or schema |
| `Function` | A key function or entry point |
| `Metric` | A computed metric and its definition |
| `Attested Computation` | The one sanctioned query/code that computes a metric (spec-defined type, see below) |
| `Runbook` / `Playbook` | An operational procedure |
| `Decision` / `ADR` | An architecture decision record |
| `Config` | A configuration surface |

## Directory skeleton

```
okf/
├── index.md                 # root listing (may carry okf_version: "0.2")
├── log.md
├── services/
│   ├── index.md
│   └── search.md
├── apis/
│   ├── index.md
│   └── search-endpoint.md
├── tables/
│   ├── index.md
│   ├── chunks.md
│   └── documents.md
├── metrics/
│   └── recall-at-k.md
├── computations/            # only if metrics need attested computation
│   └── recall-at-k.md
├── references/              # executor run instructions, attester code
│   └── attesters/
└── runbooks/
    └── reindex.md
```

## Concept template — module/service

```markdown
---
type: Module
title: Search Pipeline
description: Hybrid dense + full-text retrieval over the chunk store.
resource: https://github.com/<owner>/<repo>/blob/main/src/search.py
tags: [retrieval, search]
generated: { by: claude-code/<model-id>, at: <ISO 8601 now, e.g. 2026-09-25T10:30:00Z> }
---

# Purpose
What this module is responsible for, in two or three sentences.

# Key entry points
| Symbol | Description |
|---|---|
| `hybrid_search(query, k)` | Runs dense + lexical, merges via RRF. |
| `rerank(chunks, query)` | Reranker pass over candidates. |

# Dependencies
- [chunks table](/tables/chunks.md)
- [search endpoint](/apis/search-endpoint.md)

# Caveats
- Operational gotchas, tuning constants, known limits.
```

## Concept template — table/schema

```markdown
---
type: Table
title: chunks
description: Embedded document chunks with vector + lexical indexes.
resource: <db console or migration file URL>
tags: [storage, pgvector]
generated: { by: claude-code/<model-id>, at: <ISO 8601 now, e.g. 2026-09-25T10:30:00Z> }
sources:
  - id: migration
    resource: <path or URL of the migration that defines the table>
    title: <migration name>
    last_modified: <migration file's last commit time, with offset>
---

# Schema
| Column | Type | Description |
|---|---|---|
| `id` | uuid | Primary key. |
| `document_id` | uuid | FK to [documents](/tables/documents.md). |
| `embedding` | vector | Dense vector; HNSW index.[^migration] |

[^migration]: <migration name>

# Joins
Joined with [documents](/tables/documents.md) on `document_id`.

# Caveats
- Index/maintenance notes.
```

## Concept template — API endpoint

```markdown
---
type: API Endpoint
title: POST /search
description: Hybrid search endpoint returning ranked chunks.
resource: https://api.example.com/search
tags: [api, retrieval]
generated: { by: claude-code/<model-id>, at: <ISO 8601 now, e.g. 2026-09-25T10:30:00Z> }
---

# Request
| Field | Type | Description |
|---|---|---|
| `query` | string | Natural-language query. |
| `top_k` | int | Max results (default 10). |

# Response
Ranked array of chunk objects. See [chunks](/tables/chunks.md).

# Examples
```bash
curl -X POST /search -d '{"query":"...","top_k":5}'
```
```

## Concept template — attested computation

Use only when a metric has one sanctioned computation that agents must run verbatim, and the project has (or is building) a runner and a deterministic attester. The `Metric` concept keeps the definition and links here; this concept holds the contract.

```markdown
---
type: Attested Computation
title: Recall@k for evaluation set
description: Fraction of gold chunks retrieved in the top k, per the eval protocol.
tags: [retrieval, eval]
status: draft
runtime: postgres
parameters:
  - { name: k, type: integer, required: true }
  - { name: eval_set, type: string, required: true }
executor:
  resource: /references/run-on-postgres.md
  receipt: [executed_sql, result]
attester:
  resource: /references/attesters/sql-equality.py
generated: { by: claude-code/<model-id>, at: <ISO 8601 now, e.g. 2026-09-25T10:30:00Z> }
stale_after: <when the eval protocol is next reviewed, with offset>
sources:
  - id: eval-protocol
    resource: /decisions/eval-protocol.md
    title: Evaluation protocol
---

# Computation

    SELECT AVG(hit::int) AS recall_at_k
    FROM eval_results
    WHERE eval_set = $eval_set AND rank <= $k

Binds only `k` and `eval_set`, per the evaluation protocol.[^eval-protocol]

[^eval-protocol]: Evaluation protocol
```

Exactly one fenced/indented code block under `# Computation`. For a long or shared query, set `computation: /references/computations/recall.sql` and omit the body block. If no attester exists yet, say so to the user rather than pointing `attester.resource` at a file that doesn't exist — a broken attester link is conformant but misleading.

## Tips

- Every concept you derive from code should list the code as a `sources` entry (file path or permalink) with its `last_modified` from `git log -1 --format=%cI -- <file>`. When that date is newer than the concept's `generated.at`, the concept may be stale — that comparison is how you find concepts to refresh.
- Mirror the code's mental model in the directory layout, not the file system literally.
- Link aggressively: a module → the tables it reads, the endpoints it serves, the runbooks that operate it. The link graph is the value.
- Point `CLAUDE.md` / `AGENTS.md` at `okf/index.md` and instruct the agent to read relevant concepts before code tasks — this is workflow step 7 in `skill.md`, not optional polish. A bundle that isn't linked from `CLAUDE.md` is invisible to every agent that reads that file at task start (`/feature-dev`, `database-architect`, `integration-test-engineer` all do).
