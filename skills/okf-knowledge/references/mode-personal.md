# Mode: personal — personal knowledge base / second brain

Capture an individual's curated knowledge — research notes, ideas, reading notes, references, learnings — as an OKF bundle a personal AI agent can read. Think Obsidian vault, but conformant and agent-portable.

## Where it lives

A standalone folder on local disk, synced drive, or a private repo (e.g. `~/knowledge/`, `~/second-brain/`). No project coupling. Fully portable: it's just files.

## Suggested type vocabulary

| type | Describes |
|---|---|
| `Note` | A general note or thought |
| `Research` | Findings on a topic |
| `Reading` | Notes on a book/paper/article |
| `Idea` | A captured idea or hypothesis |
| `Reference` | Lookup material, cheat sheet |
| `Person` | Notes about a person/contact |
| `Project` | A personal project's context |
| `Learning` | Something learned, a skill log |

## Directory skeleton

Organize by how *you* think — by topic, by area, by PARA, whatever fits. The spec is layout-agnostic.

```
knowledge/
├── index.md                 # may carry okf_version: "0.1"
├── log.md
├── research/
│   ├── index.md
│   └── okf-format.md
├── reading/
│   └── thinking-fast-slow.md
├── ideas/
│   └── productized-consulting.md
└── reference/
    └── sql-window-functions.md
```

## Concept template — research note

```markdown
---
type: Research
title: Open Knowledge Format
description: How OKF works and where it fits vs RAG and MCP.
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog
tags: [ai, knowledge, agents]
timestamp: <ISO 8601 now>
source: <where you learned this>
---

# Summary
The core insight in a few sentences.

# Details
Structured findings — headings, lists, tables.

# Related
- [MCP notes](/research/mcp.md)
- [RAG patterns](/research/rag.md)

# Citations
[1] [OKF spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
```

## Concept template — reading note

```markdown
---
type: Reading
title: Thinking, Fast and Slow
description: Key takeaways on System 1 / System 2 cognition.
tags: [psychology, decision-making]
timestamp: <ISO 8601 now>
author: Daniel Kahneman
---

# Key ideas
- Idea one.
- Idea two.

# Quotes
Keep any quoted material short and attributed.

# My takeaways
How this connects to your own work or other [notes](/research/decision-making.md).
```

## Concept template — reference / cheat sheet

```markdown
---
type: Reference
title: SQL Window Functions
description: Syntax and patterns for window functions.
tags: [sql, cheatsheet]
timestamp: <ISO 8601 now>
---

# Patterns
| Need | Pattern |
|---|---|
| Running total | `SUM(x) OVER (ORDER BY d)` |
| Rank within group | `RANK() OVER (PARTITION BY g ORDER BY x)` |

# Examples
```sql
SELECT id, RANK() OVER (PARTITION BY dept ORDER BY salary DESC) FROM emp;
```
```

## Tips

- Lower the bar to capture: a `Note` with just `type` and a body is conformant. Enrich later.
- Link notes to each other to build a personal knowledge graph the agent can traverse.
- Coming from Obsidian: vault ≈ bundle, note ≈ concept, frontmatter ≈ frontmatter, wikilink ≈ markdown link. The only required change is a non-empty `type` per note and `/`-absolute links for stability.
- Copyright: when capturing reading notes, keep quoted passages short and attributed; summarize in your own words.
