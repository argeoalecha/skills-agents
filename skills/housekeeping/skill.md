---
name: housekeeping
description: Weekly ~/.claude/ directory cleanup agent. Scans for redundant, superseded, stale, and non-essential files across skills, agents, plans, debug logs, backups, cache, and telemetry. Produces a categorized report with size and deletion rationale, then waits for user confirmation before removing anything. Triggers on /housekeeping, "run housekeeping", "clean up claude folder", "weekly cleanup", "clear old files", or "regain disk space".
---

# Housekeeping Agent

Performs a systematic audit of `~/.claude/` to identify files that are safe to delete — redundant, superseded, stale, or auto-generated junk. Nothing is deleted without explicit user approval.

---

## When to Run

- Weekly, on a fixed day (e.g., every Monday morning before starting work)
- After any major skill refactor or theme/agent overhaul
- When disk space feels tight
- Before a `/checkpoint` at end of a big session

---

## What This Covers (Learned from Real Cleanup Sessions)

Real examples of what has been cleaned in this workspace:

| File Removed | Why |
|---|---|
| `assets/themes/hayah-ai.json` | Single-theme JSON superseded by 5 variant JSONs |
| `assets/hayah-ai-theme-showcase.pdf` | Static PDF replaced by live `showcase.html` |

These are the patterns this skill looks for at scale.

---

## Scan Workflow

### Step 1 — Run the Directory Audit

Execute all scans silently before presenting anything to the user.

```bash
# Full file listing with sizes
find ~/.claude -not -path '*/.git/*' -type f -exec du -sh {} + 2>/dev/null | sort -rh

# .DS_Store files (always safe to delete)
find ~/.claude -name ".DS_Store" -type f

# Debug logs
find ~/.claude/debug -type f 2>/dev/null

# Stale IDE lock files
find ~/.claude/ide -name "*.lock" -type f 2>/dev/null

# Telemetry failed events
find ~/.claude/telemetry -type f 2>/dev/null

# Statsig cache files
find ~/.claude/statsig -type f 2>/dev/null

# Backup files older than 14 days
find ~/.claude/backups -type f -mtime +14 2>/dev/null

# file-history session folders older than 7 days
find ~/.claude/file-history -maxdepth 1 -mindepth 1 -type d -mtime +6 2>/dev/null

# Stale plan files (check if referenced in any active project)
find ~/.claude/plans -type f 2>/dev/null

# Shell snapshots
find ~/.claude/shell-snapshots -type f 2>/dev/null

# Orphaned todos (no matching active session)
find ~/.claude/todos -type f 2>/dev/null

# Skill asset files — PDFs, old JSONs, images possibly superseded
find ~/.claude/skills -type f \( -name "*.pdf" -o -name "*.png" -o -name "*.jpg" \) 2>/dev/null

# Skills with no SKILL.md (orphaned skill fragments)
find ~/.claude/skills -maxdepth 1 -name "*.md" -not -path "*/*/SKILL.md" 2>/dev/null

# Skill backup folders older than 14 days (auto-safe — live skill.md files are the source of truth)
find ~/.claude/skills/_backups -maxdepth 1 -mindepth 1 -type d -mtime +13 2>/dev/null
```

### Step 2 — Cross-Check Skills for Internal Redundancy

For each skill directory under `~/.claude/skills/`, read its `SKILL.md` and check:

- Do any `references/` files go unmentioned in the SKILL.md?
- Do any `assets/` files go unmentioned in the SKILL.md?
- Are there multiple versions of the same file type (e.g., two showcase files, old + new JSON configs)?
- Are there scripts in `scripts/` that aren't invoked anywhere?

Flag anything that fails these checks as **potentially orphaned**.

### Step 3 — Check agents/ for Staleness

Read each file in `~/.claude/agents/`. Flag an agent as stale if:
- Its role is fully covered by a built-in Claude Code agent type
- It hasn't been referenced in any recent skill or CLAUDE.md
- It duplicates another agent file's purpose

Do not delete agents automatically — just flag for review.

### Step 4 — Categorize All Findings

Group every finding into one of these categories:

**AUTO-SAFE** — Safe to delete without hesitation. Always accumulate silently and offer as a batch:
- `.DS_Store` files
- `debug/` log files
- `telemetry/` failed event files
- `statsig/` cache and session files
- `ide/` stale `.lock` files
- `shell-snapshots/` files
- `todos/` JSON files for closed sessions
- `file-history/` session folders older than 7 days (undo snapshots for sessions too old to revert)
- `skills/_backups/` dated subfolders older than 14 days (live skill.md files are the source of truth; old backups are not needed)

**SUPERSEDED** — Confirmed replaced by a newer file (e.g., PDF replaced by HTML, single JSON replaced by variant JSONs). Require explicit confirmation per item or as a group.

**STALE** — Files older than 30 days with no clear active use. Show with age and size. Require confirmation.

**ORPHANED** — Files in skill `assets/` or `references/` not mentioned in the skill's `SKILL.md`. Flag individually — some may be intentionally unlisted.

**REVIEW NEEDED** — Agents, plans, or config files that may be outdated but require human judgment. Do not offer to delete — only surface for awareness.

---

## Step 5 — Present the Report

Format the report clearly. Do not delete anything yet.

```
## ~/.claude/ Housekeeping Report
Date: [today's date PHT]

### AUTO-SAFE (safe to batch-delete)
[count] files · [total size]

  debug/          [n files] · [size]
  telemetry/      [n files] · [size]
  statsig/        [n files] · [size]
  .DS_Store       [n files] · [size]
  ide/ locks      [n files] · [size]
  shell-snapshots [n files] · [size]
  todos/          [n files] · [size]
  file-history/   [n session folders, 7+ days old] · [size]
  _backups/       [n dated folders, 14+ days old] · [size]

→ Delete all AUTO-SAFE files? [yes/no]

---

### SUPERSEDED
Files confirmed replaced by newer equivalents:

  [file path] ([size]) — replaced by [newer file]
  ...

→ Delete all SUPERSEDED? Or review individually?

---

### STALE (30+ days, no active reference)
  [file path] ([size]) — last modified [date]
  ...

→ Review each before deciding.

---

### ORPHANED SKILL ASSETS
Assets not referenced in their skill's SKILL.md:

  [skill name]/[file] ([size]) — not mentioned in SKILL.md
  ...

→ Review each. May be safe to delete or may need SKILL.md update.

---

### REVIEW NEEDED (no deletion offered)
  [file path] — reason for flagging
  ...

---

### Summary
Total recoverable if all confirmed: [X MB]
```

---

## Step 6 — Execute Deletions

Only after explicit user confirmation per category or per file.

- Batch-delete AUTO-SAFE in one `rm` command
- Delete SUPERSEDED and STALE files one group at a time
- Never delete REVIEW NEEDED files — surface them only
- After deletion, run a final `du -sh ~/.claude/` to show space reclaimed

---

## What This Skill Never Touches

These are off-limits regardless of age or apparent redundancy:

- `CLAUDE.md` (global config)
- `settings.json` / `settings.local.json`
- `.credentials.json`
- `history.jsonl`
- `stats-cache.json`
- `skills/*/SKILL.md` files
- `agents/*.md` files (flag only, never delete)
- `plugins/` directory
- `cache/changelog.md`
- Any file actively referenced in a current project's `CLAUDE.md`

---

## Disk Space Context

After each housekeeping run, log the result here for trend tracking:

| Date | Before | After | Reclaimed |
|---|---|---|---|
| 2026-02-24 | — | — | hayah-ai.json + showcase.pdf (first manual cleanup) |
| 2026-02-24 | 105 MB | 104 MB | ~1.77 MB — 33 AUTO-SAFE files (debug, statsig, telemetry, .DS_Store, ide locks, shell snapshots, todos, plans). Also migrated prd-tdd-writer.md → proper skill folder. |
| 2026-02-25 | 128 MB | 124 MB | ~4.28 MB — 29 files: 15 debug logs, 2 ide locks, 1 shell snapshot, 9 todos, 2 stale plans (CDA pipeline + data-analyst PRD/TDD). Skills clean, no orphans. |
| 2026-03-08 | 198 MB | 174 MB | ~24 MB — 65 files: 41 debug logs, 4 telemetry, 9 todos, 1 ide lock, 1 shell snapshot, 5 stale plans, 4 orphaned tool-result files (data-analyst). Skills clean. |
| 2026-05-06 | 180 MB | 174 MB | ~6 MB — 22 items: 15 .DS_Store, 1 telemetry, 1 ide lock, 1 shell snapshot, 19 file-history folders (Apr 6–Apr 29). 5 stale plans + 1 orphaned PNG pending user decision. |
| 2026-05-07 | 180 MB | 177 MB | ~3.1 MB — 1 ide lock, 1 shell snapshot, 1 file-history folder (3.1MB), 1 stale plan, 1 orphaned PNG (hayahailogo.png). Rebuilt 16 truncated skill.md files. Added _backups/ cleanup rule (14-day expiry). |

Update this table after every run so you can track accumulation patterns over time.
