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
| `Runbook` / `Playbook` | An operational procedure |
| `Decision` / `ADR` | An architecture decision record |
| `Config` | A configuration surface |

## Directory skeleton

```
okf/
├── index.md                 # root listing (may carry okf_version: "0.1")
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
timestamp: <ISO 8601 now>
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
timestamp: <ISO 8601 now>
---

# Schema
| Column | Type | Description |
|---|---|---|
| `id` | uuid | Primary key. |
| `document_id` | uuid | FK to [documents](/tables/documents.md). |
| `embedding` | vector | Dense vector; HNSW index. |

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
timestamp: <ISO 8601 now>
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

## Tips

- Mirror the code's mental model in the directory layout, not the file system literally.
- Link aggressively: a module → the tables it reads, the endpoints it serves, the runbooks that operate it. The link graph is the value.
- Point `CLAUDE.md` / `AGENTS.md` at `okf/index.md` and instruct the agent to read relevant concepts before code tasks — this is workflow step 7 in `skill.md`, not optional polish. A bundle that isn't linked from `CLAUDE.md` is invisible to every agent that reads that file at task start (`/feature-dev`, `database-architect`, `integration-test-engineer` all do).
