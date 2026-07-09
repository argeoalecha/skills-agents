---
name: init
description: Bootstrap a new Hayah-AI project from a concept. Reads the concept doc in the pre-created project folder, writes the universal skeleton (CLAUDE.md, .gitignore, docs/concept.md), git-inits, then auto-runs /prd-tdd-writer to produce the PRD/TDD/TODO. Stack, theme, and deploy target are decided in the TDD — not here. Use when the user says "init", "bootstrap this project", "start a new project", "scaffold a new project", or invokes /init.
user-invocable: true
---

# /init — Project Bootstrapper

Entry point of the project pipeline. Turns a concept doc sitting in a freshly-created folder into a git-tracked skeleton, then hands straight off to `/prd-tdd-writer`.

```
concept doc in folder
   │
   ▼
/init  ── skeleton + git ──►  (auto, no stop)  ──►  /prd-tdd-writer  ──►  PRD / TDD / TODO
```

`/init` does **not** choose a stack, write framework files, pick a theme, or configure a deploy target. The TDD decides the stack; framework files come later from `/company-site` (marketing site) or `/feature-dev` (app), driven by the TODO. Keep this skill thin — its only job is skeleton + handoff.

---

## Phase 0 — Locate the concept

The current working directory is the pre-created project folder. Confirm it, then find the concept:

1. **Project name** = the folder's own name (kebab-case). Do not ask.
2. **Concept doc** — look for a concept file in the folder: any `.md`, or a single source/code file the user dropped in as the seed idea. Common names: `concept.md`, `idea.md`, `README.md`, `notes.md`, or a lone `.txt`/`.py`/`.ts`/`.jsx`.
   - **If a concept doc is found:** read it. That is the input — no interview. (A `/brainstorm-ideas` Recommendation block saved as a file counts as a concept doc.)
   - **If none is found:** ask the user one question — "What's the concept? One or two lines is enough." — then write their answer to `docs/concept.md` yourself and proceed. This is the only prompt `/init` ever issues.

Do not ask for project type, theme variant, or deploy target. Those are decided downstream.

---

## Phase 1 — Read the concept

Read the concept doc fully. Extract:
- **What the project is** — a one-line description (for `CLAUDE.md` and the commit message).
- Any explicit signals worth carrying forward (target market, must-have features, named tools) — but do not act on them or lock in a stack. They are notes for `/prd-tdd-writer`, not decisions for `/init`.

---

## Phase 2 — Write the skeleton

Write only these files. No framework files, no `package.json`, no theme, no deploy config.

### `.gitignore`
```
node_modules
dist
build
.next
.env
.env.*
.env.local
.DS_Store
.netlify
.vercel
*.log
```

### `CLAUDE.md`
```markdown
# <name> — Project Instructions

## What This Project Is

<one-line description from the concept>

## Stack

Stack: TBD — decided in the TDD (run /prd-tdd-writer). Do not assume a framework
before the TDD exists.

## Key Conventions

- Follow workspace-level conventions in ~/projects-mvp/CLAUDE.md
- No secrets in code — env vars in .env.local (gitignored), documented in .env.example
- Validate all external data at the boundary

## What Not To Do

- Do not add features beyond what is asked
- Do not refactor surrounding code when fixing a bug
- Do not add error handling for scenarios that cannot happen
```

### `docs/concept.md`
- If the user provided the concept inline (Phase 0, no doc found), write it here.
- If a concept doc already existed under a different name, normalize it: ensure a copy lives at `docs/concept.md`. Leave the original in place if it was `README.md`.

Do **not** create a public `README.md` — `CLAUDE.md` serves that purpose internally.

---

## Phase 3 — Git init

```bash
git init
git add .
git commit -m "chore: bootstrap <name> skeleton"
```

Do not add a remote and do not push. The user adds the remote when ready.

---

## Phase 4 — Hand off to /prd-tdd-writer

Immediately invoke the `prd-tdd-writer` skill via the Skill tool — **do not stop, do not wait for confirmation.** Pass the concept along (point it at `docs/concept.md`). The TDD it produces is where stack, theme, and deploy target get decided.

After `/prd-tdd-writer` returns, tell the user:
1. Skeleton created and committed at the project folder.
2. `/prd-tdd-writer` has run — PRD / TDD / TODO are written.
3. Next: build from the TODO — `/company-site` for a marketing site, `/feature-dev` for an app, stepped through the TODO. Run `/audit` before the first production deploy.
4. Optional, as the codebase grows: `/okf-knowledge` to build an agent-readable docs bundle (`okf/`) that `/feature-dev` and the local agents (full-stack-developer, database-architect, integration-test-engineer) read before touching code. Not needed for a fresh skeleton — worth it once there's real architecture to document.

---

## Rules

- Never choose a stack, framework, theme, or deploy target — the TDD owns those.
- Never write framework files (`package.json`, `next.config`, `tailwind.config`, `vite.config`, etc.). `/company-site` and `/feature-dev` are the only authors of those.
- The only prompt allowed is the single concept question in Phase 0, and only when no concept doc exists.
- Always create `CLAUDE.md` and always `git init` — non-negotiable regardless of project size.
- Always auto-run `/prd-tdd-writer` at the end — `/init` never terminates the chain on its own.
