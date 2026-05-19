---
name: resume
description: Session startup skill. Produces a structured briefing so you can continue an ongoing project without losing context. Invoke at the start of any new session. Triggers on /resume, "resume project", "continue where we left off", "what were we working on", "session start", "catch me up", or "what's the status".
---

# Session Resume

Produces a structured **Session Briefing** for the current project so work can continue without losing context.

---

## What This Skill Does

1. Checks for a checkpoint file and assesses how fresh it is
2. Supplements or replaces stale/missing checkpoint with git history and project files
3. Checks for open work (tasks, todos, in-progress items)
4. Outputs a single, structured briefing with a clear recommended next action

---

## Step 1 — Find the Checkpoint

```bash
# Look for checkpoint in current directory and common project roots
ls SESSION_CHECKPOINT.md 2>/dev/null && cat SESSION_CHECKPOINT.md || echo "No checkpoint found"

# Check how old it is
stat -f "%Sm" SESSION_CHECKPOINT.md 2>/dev/null || stat -c "%y" SESSION_CHECKPOINT.md 2>/dev/null
```

**Freshness:**
- < 4 hours: recent — use as primary source
- 4–24 hours: stale — supplement with git log
- > 24 hours: very stale — reconstruct primarily from git + codebase
- Missing: reconstruct fully from git + codebase

---

## Step 2 — Reconstruct from Git (if checkpoint missing or stale)

```bash
# Recent commits
git log --oneline -20

# What changed in the last session
git diff HEAD~5 --name-only

# Current branch and status
git branch --show-current && git status --short

# Uncommitted changes
git diff --stat
```

---

## Step 3 — Check Open Work

```bash
# TODO list
cat TODO.md 2>/dev/null | head -60

# Any in-progress items flagged
grep -n "IN PROGRESS\|in-progress\|WIP\|TODO\|FIXME" TODO.md 2>/dev/null

# TypeScript errors
npx tsc --noEmit 2>&1 | head -20
```

---

## Step 4 — Scan Project State

```bash
# Project structure snapshot (fast)
ls -la

# Key config files
cat package.json | grep -E '"name"|"version"|"scripts"' 2>/dev/null | head -10

# Current branch
git log --oneline -5
```

---

## Step 5 — Produce the Briefing

Output a structured briefing:

```
## Session Briefing — <Project Name>
Resumed: <timestamp PHT>
Checkpoint: <fresh/stale/reconstructed>

### What Was In Progress
<precise description of the last thing being worked on — file, feature, or task>

### What's Done (this sprint)
- <recently committed item>
- <recently committed item>

### Open Tasks (in priority order)
1. <most important next thing>
2. <second thing>
3. <third thing>

### Current State
- Branch: <branch name>
- Uncommitted changes: <yes/no — list files if yes>
- TypeScript errors: <none / N errors>
- Tests: <passing / failing / unknown>

### Blockers or Known Issues
<any blockers from checkpoint or visible in code>

### Recommended Next Action
<single, specific, immediately actionable step>
Skill to use: /feature-dev | /db-migrate | /api-new | /audit | ...
```

---

## Rules

- Never invent context — if you can't determine something, say "unknown"
- The recommended next action must be a single concrete step, not a direction
- If there are uncommitted changes, flag them prominently — they may represent in-progress work
- If TypeScript has errors, surface them in the briefing regardless of whether the checkpoint mentions them
- If the checkpoint is missing and git history is thin, ask the user to describe what they were working on before reconstructing
