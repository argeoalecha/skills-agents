---
name: init
description: Bootstrap a new Hayah-AI project from a concept. Reads the concept doc in the pre-created project folder (an /interrogate-me Concept Brief is the preferred input), checks it is concrete enough to spec, writes the universal skeleton (CLAUDE.md with Project Profile and Definition of Done, .gitignore, docs/concept.md), git-inits on main, registers the project in the workspace map, then auto-runs /prd-tdd-writer (PRD/TDD) followed by /plan-todo (TODO.md) and commits the result. Stack, theme, and deploy target are decided in the TDD — not here. Use when the user says "init", "bootstrap this project", "start a new project", "scaffold a new project", or invokes /init.
user-invocable: true
---

# /init — Project Bootstrapper

Entry point of the project pipeline. Turns a concept doc sitting in a freshly-created folder into a git-tracked foundation, then hands straight off to `/prd-tdd-writer` and `/plan-todo`.

```
/interrogate-me ── Concept Brief ──► docs/concept.md
                                          │
                                          ▼
/init ── guard ─► concept check ─► skeleton + git ─► /prd-tdd-writer ─► close the loop ─► /plan-todo ─► commit
```

`/init` does **not** choose a stack, write framework files, pick a theme, or configure a deploy target. The TDD decides the stack; framework files come later from `/company-site` (marketing site) or `/feature-dev` (app), driven by the TODO. Keep this skill thin — its job is a foundation every later skill can trust: a concept that is concrete, a profile `/audit` can read, docs that agree with each other, and a clean git history.

---

## Phase 0 — Guard and locate the concept

### Guard the folder

The current working directory must be a fresh project folder. Check before writing anything:

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null
ls -A
```

- **Stop** if cwd is `$HOME`, `~/projects-mvp`, `/Volumes/1TB_SSD/projects-mvp-ext`, or `~/.claude`. Running here would put a whole workspace under one repo. Tell the user to create the project folder and `cd` into it.
- **Stop** if cwd is already inside a git repository. If the repo's top level is cwd and it has commits, this isn't a new project: point to `/prd-tdd-writer` (review mode) or `/audit gap`. If the top level is a parent folder, ask whether the project should really be nested there.

### Name

**Project name** = the folder's own name. Do not ask. If it isn't kebab-case, use the kebab-case form in `CLAUDE.md` and the commit message; never rename the folder.

### Find the concept doc, in this order

1. `docs/concept.md` — where `/interrogate-me` writes its Concept Brief.
2. `concept.md`, `idea.md`, `brief.md`, `notes.md` at the root.
3. `README.md`.
4. Any other lone `.md`/`.txt`, or a single source file (`.py`/`.ts`/`.jsx`, etc.) the user dropped in as the seed idea.

Take the first level that has a match. If one level has several candidates, ask which one is the concept. A `/brainstorm-ideas` Recommendation block or an `/interrogate-me` Concept Brief saved as a file counts as a concept doc.

If nothing is found, ask one question: "What's the concept? One or two lines is enough." Write the answer to `docs/concept.md`, then continue to Phase 1, where a one-liner will normally fail the concept check.

Do not ask for project type, theme variant, or deploy target. Those are decided downstream.

---

## Phase 1 — Check the concept

Read the concept doc fully. Extract:
- **What the project is**: a one-line description for `CLAUDE.md` and the commit message.
- **Foundation facts**: engagement (internal or client), tier, AI features and their class (A1–A4), personal data, market, scale. An `/interrogate-me` brief has these in its Foundation facts table. For any other doc, take only what it states explicitly and mark the rest `UNRESOLVED`.
- Other explicit signals (must-have features, named tools). These are notes for `/prd-tdd-writer`, not decisions for `/init`.

**Concept check.** A concept is concrete enough to spec when it states all three of these:
- **Problem**: a specific pain for a specific person.
- **User**: who, beyond "everyone".
- **v1 scope**: at least what's in, ideally what's out.

An `/interrogate-me` brief with `Status: Ready for /init` passes without further checking. A brief marked `Not ready`, or any doc missing one of the three, fails. On a failure, ask one question that names the gaps: "This concept doesn't settle <gaps>. Run /interrogate-me first (recommended), or proceed and let /prd-tdd-writer fill the gaps?"
- **Interrogate**: invoke the `interrogate-me` skill. When it has written `docs/concept.md`, restart Phase 1 with that brief.
- **Proceed**: continue, and pass the gaps to `/prd-tdd-writer` in Phase 4 as the things it must ask about.

A PRD built on a one-line concept is the most expensive rework in the pipeline. That's why this is the one question worth asking.

---

## Phase 2 — Write the skeleton

Write only these files. No framework files, no `package.json`, no theme, no deploy config, no `README.md`. There is no setup to document yet; `/plan-todo` puts the README in Phase 1 Foundation (audit G0-08).

### `.gitignore`
```
node_modules
dist
build
out
.next
coverage
*.tsbuildinfo
.env
.env.*
!.env.example
.DS_Store
.netlify
.vercel
supabase/.temp
__pycache__
.venv
*.log
SESSION_CHECKPOINT.md
.claude/settings.local.json
```

`!.env.example` matters. Without it, `.env.*` also ignores the placeholder file that the conventions and audit G0-06 require to be committed.

### `CLAUDE.md`
```markdown
# <name> — Project Instructions

## What This Project Is

<one-line description from the concept>

## Project Profile

| Fact | Value |
|---|---|
| Engagement | <internal / client: name> |
| Tier | <T1 / T2 / T3 — one-line rationale> |
| AI features | <none / feature: A1–A4, one per feature> |
| Personal data | <none / fields — RA 10173 applies> |
| Market | <Philippines / other> |
| Storage | <mac / ext> |

This table is the tier and AI-class record (audit G1-01). Change it deliberately:
raising the tier or changing an AI feature's class means a re-audit.

## Stack

Stack: TBD — decided in the TDD (run /prd-tdd-writer). Do not assume a framework
before the TDD exists.

## Source of Truth

| Doc | Path |
|---|---|
| Concept | docs/concept.md |
| PRD | TBD — written by /prd-tdd-writer |
| TDD | TBD — written by /prd-tdd-writer |
| Tasks | TODO.md |

When these disagree, the TDD wins on how and the PRD wins on what. Fix the drift
instead of working around it.

## Definition of Done

A change is done when:
- typecheck, lint, tests and build pass
- every Must-Have story it touches has a feature-tier E2E test
- no secrets in code; every new env var is listed in .env.example
- /audit gate G3 is GO before merging to main; /audit gate G5 is GO before production

## Key Conventions

- Follow workspace-level conventions in ~/projects-mvp/CLAUDE.md
- No secrets in code — env vars in .env.local (gitignored), documented in .env.example
- Validate all external data at the boundary

## What Not To Do

- Do not add features beyond what is asked
- Do not refactor surrounding code when fixing a bug
- Do not add error handling for scenarios that cannot happen
```

Fill the Project Profile from the Phase 1 facts and write `UNRESOLVED` for anything unknown. Never guess a tier. Storage is `mac` under `~/projects-mvp/` and `ext` under `/Volumes/1TB_SSD/projects-mvp-ext/`.

### `docs/concept.md`
`docs/concept.md` is the single concept file from here on.
- If the concept came inline (Phase 0), it's already there.
- If it came from a root `.md`/`.txt` other than `README.md`, move it to `docs/concept.md`. Don't keep a copy that will drift.
- If it came from `README.md` or a seed source file, leave the original in place and write `docs/concept.md` from its content, with a line naming the original file.

---

## Phase 3 — Git init and register

Commit the skeleton:

```bash
git init -b main
git add .
git status --short
```

Before committing, read the staged list. If anything looks like a credential (`*.pem`, `*.key`, `id_rsa*`, `*credentials*.json`, `service-account*.json`, any file containing `-----BEGIN`), or a file is larger than 5 MB, unstage it and ask the user what to do with it. If `gitleaks` is installed, also run `gitleaks dir --redact .`. Then:

```bash
git commit -m "chore: bootstrap <name> skeleton"
```

Do not add a remote and do not push. The user adds the remote when ready.

**Register the project.** Add a row to the Project Map table in `~/projects-mvp/CLAUDE.md`: `| <name> | <one-line description> | TBD | Active | <mac/ext> |`. Skip this if a row for the name already exists. Don't edit `~/projects-mvp/okf/` yourself; mention in the final report that `/okf-knowledge` should add the project to the catalog.

---

## Phase 4 — Hand off to /prd-tdd-writer

Immediately invoke the `prd-tdd-writer` skill via the Skill tool. **Do not stop or wait for confirmation.** Point it at `docs/concept.md` and `CLAUDE.md`'s Project Profile, and pass:
- any concept-check gaps the user chose to proceed with (Phase 1), and
- every Project Profile field marked `UNRESOLVED`, as things the PRD must settle.

Have it save the PRD and TDD in `docs/`. The TDD it produces is where stack, theme, and deploy target get decided.

---

## Phase 5 — Close the loop, plan, commit

When `/prd-tdd-writer` returns:

1. **Update `CLAUDE.md`** so it agrees with the new docs:
   - Replace the `Stack: TBD` text with the TDD's choices: one line each for stack, theme variant (web), and deploy target, plus "Full rationale: <TDD path>".
   - Fill in any Project Profile fields the PRD settled. Anything still open stays `UNRESOLVED`.
   - Fill in the PRD and TDD paths under Source of Truth.
2. **Invoke `plan-todo`** (same rule: no stop) to generate `TODO.md` from the PRD and TDD. `/prd-tdd-writer` does not write the TODO.
3. **Commit:**
   ```bash
   git add docs/ CLAUDE.md TODO.md
   git commit -m "docs: add PRD, TDD and TODO for <name>"
   ```

Then report to the user:
1. **Foundation committed** at the project folder, on `main`, in two commits (skeleton, then docs). The project is in the workspace map.
2. **Decisions locked**: stack, theme, deploy target, tier, and AI class per feature. These come from the TDD and the profile.
3. **Still open**: every `UNRESOLVED` profile field and every TDD Open Question that blocks Phase 1. Name them; don't summarize them away.
4. **Next**: build from the TODO. Use `/company-site` for a marketing site, or `/feature-dev` for an app, working through the TODO in order. `/audit gate G3` before merging to main, `/audit gate G5` before the first production deploy.
5. **Optional, as the codebase grows**: `/okf-knowledge`, to add the project to the workspace catalog now and later build an agent-readable bundle (`okf/`) that `/feature-dev` and the local agents (database-architect, integration-test-engineer) read before touching code.

---

## Rules

- Never choose a stack, framework, theme, or deploy target — the TDD owns those. `/init` only copies the TDD's choices into `CLAUDE.md` in Phase 5.
- Never write framework files (`package.json`, `next.config`, `tailwind.config`, `vite.config`, etc.). `/company-site` and `/feature-dev` are the only authors of those.
- Never run in a workspace root, `$HOME`, `~/.claude`, or inside an existing repo (Phase 0 guard).
- Never guess a Project Profile value. Unknown is `UNRESOLVED` until the user or the PRD settles it.
- `/init` asks at most two questions: which file or what concept (Phase 0, only when needed), and interrogate-or-proceed (Phase 1, only when the concept fails the check).
- Always create `CLAUDE.md` and always `git init -b main`, whatever the project's size.
- Always auto-run `/prd-tdd-writer`, then `/plan-todo`, then the docs commit. `/init` never ends the chain early, and the TODO comes from `/plan-todo`, not `/prd-tdd-writer`.
