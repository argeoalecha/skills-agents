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

# Stale plan files older than 30 days (active plans have no age filter — skip those)
find ~/.claude/plans -type f -mtime +30 2>/dev/null

# Shell snapshots
find ~/.claude/shell-snapshots -type f 2>/dev/null

# Todos older than 7 days (active session todos must not be deleted)
find ~/.claude/todos -type f -mtime +6 2>/dev/null

# Stale tasks session folders older than 7 days
find ~/.claude/tasks -maxdepth 1 -mindepth 1 -type d -mtime +6 2>/dev/null

# Paste cache older than 7 days
find ~/.claude/paste-cache -type f -mtime +6 2>/dev/null

# Skill asset files — PDFs, old JSONs, images possibly superseded
find ~/.claude/skills -type f \( -name "*.pdf" -o -name "*.png" -o -name "*.jpg" \) 2>/dev/null

# Skill directories with no skill.md (orphaned skill fragments)
find ~/.claude/skills -maxdepth 2 -mindepth 2 -name "skill.md" 2>/dev/null | sed 's|/skill.md||' | sort > /tmp/_hk_skill_dirs
find ~/.claude/skills -maxdepth 1 -mindepth 1 -type d -not -name "_backups" 2>/dev/null | sort > /tmp/_hk_all_dirs
comm -23 /tmp/_hk_all_dirs /tmp/_hk_skill_dirs

# Skill backup folders older than 14 days (auto-safe — live skill.md files are the source of truth)
find ~/.claude/skills/_backups -maxdepth 1 -mindepth 1 -type d -mtime +13 2>/dev/null

# agent-browser: leftover screenshots in tmp (auto-safe — e2e-test skill cleans these, but old runs may linger)
find ~/.agent-browser/tmp -name "screenshot-*.png" -type f 2>/dev/null

# agent-browser: stale Chromium builds — all but the newest directory are superseded
# After an agent-browser upgrade, old chrome-X.Y.Z dirs accumulate at ~345 MB each
ls -dt ~/.agent-browser/browsers/*/ 2>/dev/null | tail -n +2
```

### Step 2 — Cross-Check Skills for Internal Redundancy

For each skill directory under `~/.claude/skills/`, read its `skill.md` and check:

- Do any `references/` files go unmentioned in the skill.md?
- Do any `assets/` files go unmentioned in the skill.md?
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

**AUTO-SAFE** — Safe to move to Trash without hesitation. Always accumulate silently and offer as a batch:
- `.DS_Store` files
- `debug/` log files
- `telemetry/` failed event files
- `statsig/` cache and session files
- `ide/` stale `.lock` files
- `shell-snapshots/` files
- `file-history/` session folders older than 7 days (undo snapshots for sessions too old to revert)
- `skills/_backups/` dated subfolders older than 14 days (live skill.md files are the source of truth; old backups are not needed)
- `~/.agent-browser/tmp/screenshot-*.png` files (e2e scratch files; canonical copies are in the project's `e2e-screenshots/` folder)

**STALE** — Files older than a set threshold with no clear active use. Show with age and size. Require confirmation per item or group before moving to Trash:
- `todos/` JSON files older than 7 days (never delete todos without age filter — active session todos must survive)
- `tasks/` session folders older than 7 days
- `paste-cache/` files older than 7 days
- Plan files older than 30 days
- `~/.agent-browser/browsers/chrome-X.Y.Z/` directories that are not the newest — each is ~345 MB. After an `agent-browser` upgrade, old Chromium builds are never auto-removed. Confirm the newest build is working before trashing older ones.

**SUPERSEDED** — Confirmed replaced by a newer file (e.g., PDF replaced by HTML, single JSON replaced by variant JSONs). Require explicit confirmation per item or as a group.

**ORPHANED** — Files in skill `assets/` or `references/` not mentioned in the skill's `skill.md`. Flag individually — some may be intentionally unlisted.

**REVIEW NEEDED** — Agents, plans, or config files that may be outdated but require human judgment. Do not offer to delete — only surface for awareness.

---

## Step 5 — Present the Report

Format the report clearly. Do not delete anything yet.

```
## ~/.claude/ Housekeeping Report
Date: [today's date PHT]

### AUTO-SAFE (move to Trash as a batch)
[count] files · [total size]

  debug/          [n files] · [size]
  telemetry/      [n files] · [size]
  statsig/        [n files] · [size]
  .DS_Store       [n files] · [size]
  ide/ locks      [n files] · [size]
  shell-snapshots [n files] · [size]
  file-history/         [n session folders, 7+ days old] · [size]
  _backups/             [n dated folders, 14+ days old] · [size]
  agent-browser/tmp/    [n screenshot files] · [size]

→ Move all AUTO-SAFE to Trash? [yes/no]

---

### SUPERSEDED
Files confirmed replaced by newer equivalents:

  [file path] ([size]) — replaced by [newer file]
  ...

→ Move all SUPERSEDED to Trash? Or review individually?

---

### STALE (age threshold exceeded, requires confirmation)
  [file path] ([size]) — last modified [date] · category: todos|tasks|paste-cache|plans|agent-browser-builds
  ...

agent-browser builds (if multiple found):
  ~/.agent-browser/browsers/chrome-OLD/ ([size]) — superseded by chrome-NEW/ (current)

→ Review each before deciding.

---

### ORPHANED SKILL ASSETS
Assets not referenced in their skill's skill.md:

  [skill name]/[file] ([size]) — not mentioned in skill.md
  ...

→ Review each. May be safe to move to Trash or may need skill.md update.

---

### REVIEW NEEDED (no deletion offered)
  [file path] — reason for flagging
  ...

---

### Summary
Total recoverable if all confirmed: [X MB]
```

---

## Step 6 — Move to Trash (not permanent deletion)

Only after explicit user confirmation per category or per file.

All removals use `mv` to `~/.Trash/` — never `rm`. This sends files to the macOS system Trash so the admin user can review and empty it manually.

```bash
# Move a single file to Trash (handle name collisions with timestamp)
_trash() {
  local src="$1"
  local base
  base=$(basename "$src")
  local dest="${HOME}/.Trash/${base}"
  if [[ -e "$dest" ]]; then
    dest="${HOME}/.Trash/${base%.*}_$(date +%s).${base##*.}"
  fi
  mv "$src" "$dest"
}

# Batch-move AUTO-SAFE items (call _trash for each)
for f in <auto-safe-file-list>; do _trash "$f"; done

# For directories (file-history, _backups, tasks):
for d in <dir-list>; do _trash "$d"; done
```

- Move AUTO-SAFE items as a batch
- Move SUPERSEDED and STALE files one group at a time, after confirmation
- Never touch REVIEW NEEDED files — surface them only
- After all moves, run `du -sh ~/.claude/` and `du -sh ~/.Trash/` to show reclaimed space and what awaits final deletion

---

## What This Skill Never Touches

These are off-limits regardless of age or apparent redundancy:

- `CLAUDE.md` (global config)
- `settings.json` / `settings.local.json`
- `.credentials.json`
- `history.jsonl`
- `stats-cache.json`
- `SESSION_CHECKPOINT.md` (active session checkpoint from /checkpoint skill)
- `skills/*/skill.md` files (lowercase — the live source of truth for each skill)
- `agents/*.md` files (flag only, never delete)
- `secret-agent/` directory (treated as agents — flag only, never delete)
- `projects/` directory (contains memory system and project-scoped state)
- `plugins/` directory
- `cache/changelog.md`
- `keybindings.json`
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
| 2026-05-25 | 244 MB | 237 MB | ~7 MB — 17 .DS_Store, 1 ide lock, 2 shell snapshots, 35 file-history folders, 2 _backups folders (2026-05-07+08), 4 stale task folders, 1 orphaned skills/.vscode/ (Power Query IDE config). No debug/telemetry/statsig this run. |
| 2026-06-06 | 181 MB | 172 MB | ~9 MB — 17 .DS_Store, 1 ide lock, 2 telemetry, 2 shell snapshots, 24 file-history folders, 2 stale task folders, 9 paste-cache files, 1 orphaned skills/.vscode/ (same one — wasn't cleaned May 25). |

Update this table after every run so you can track accumulation patterns over time.
