# Mode: wiki — technical wiki / team docs (Notion-style)

Replace a stale Notion/Confluence/Obsidian space with versioned markdown an agent keeps current. This is for human-and-agent documentation: how-tos, processes, guides, decision logs, onboarding, glossaries.

## Where it lives

A standalone repo or folder (e.g. `team-wiki/` or `~/wiki/`). Git-backed so curation becomes a normal review workflow. Non-technical contributors can keep using Notion as a frontend; the OKF bundle is the agent-readable backend engineers maintain in parallel.

## Suggested type vocabulary

| type | Describes |
|---|---|
| `Guide` / `How-To` | Step-by-step instructions |
| `Process` | A recurring business/team process |
| `Runbook` / `Playbook` | Operational/incident procedure |
| `Reference` | Lookup material, glossary, FAQ |
| `Decision` / `ADR` | A recorded decision and rationale |
| `Onboarding` | Getting-started material |
| `Policy` | A rule or standard the team follows |

## Directory skeleton

```
wiki/
├── index.md                 # may carry okf_version: "0.1"
├── log.md
├── guides/
│   ├── index.md
│   └── deploy-to-prod.md
├── processes/
│   ├── index.md
│   └── sprint-planning.md
├── runbooks/
│   └── incident-response.md
├── decisions/
│   └── 0001-postgres-over-mongo.md
└── reference/
    └── glossary.md
```

## Concept template — how-to / guide

```markdown
---
type: How-To
title: Deploy to Production
description: Step-by-step production deploy with rollback.
tags: [deploy, ops]
timestamp: <ISO 8601 now>
owner: <team or person>
status: current
---

# Prerequisites
- Access, tools, approvals needed.

# Steps
1. First action.
2. Second action — see [incident response](/runbooks/incident-response.md) if it fails.
3. Verify.

# Rollback
How to undo safely.

# Citations
[1] [Internal deploy dashboard](https://...)
```

## Concept template — decision record (ADR)

```markdown
---
type: Decision
title: Postgres over Mongo for primary store
description: Why we chose relational for the core data model.
tags: [architecture, database]
timestamp: <ISO 8601 now>
status: accepted
---

# Context
The situation and forces at play.

# Decision
What was decided.

# Consequences
Trade-offs accepted; what this constrains going forward.

# Alternatives considered
- Option B and why it lost.
```

## Concept template — reference / glossary

```markdown
---
type: Reference
title: Glossary
description: Canonical definitions of internal terms.
tags: [reference]
timestamp: <ISO 8601 now>
---

# Terms
- **ARR** — annual recurring revenue; see [ARR metric](/metrics/arr.md).
- **WAU** — weekly active users.
```

## Migrating from Notion / Obsidian

- Notion pages and Obsidian notes already use markdown + frontmatter, so the shape transfers directly. The work is adding a non-empty `type` to each file and converting wikilinks to `/`-absolute markdown links.
- One Notion page = one concept file. Use the page's database property (category/type) as the OKF `type`.
- Preserve existing properties as extra frontmatter keys — consumers must keep them.

## Tips

- A wiki's value is the cross-link graph: link guides to the processes they support, runbooks to the systems they touch, decisions to the components they shaped.
- Keep one canonical definition per concept. Duplication is what OKF exists to eliminate.
