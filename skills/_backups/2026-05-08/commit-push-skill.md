---
name: commit-push
description: Automates the complete git commit and push workflow to GitHub. Use when the user asks to commit and push changes, save changes to GitHub, or wants to quickly commit and push without manual intervention. Triggers on requests like "commit and push", "save to GitHub", "push my changes", or "commit everything and push".
---

# Commit and Push to GitHub

Automates the git commit and push workflow in a single command.

---

## Workflow

### Step 1 — Inspect current state (run in parallel)

```bash
git status
git diff --staged
git log --oneline -5
```

Use `git log` output to match the repo's existing commit message style.

### Step 2 — Stage files

Stage specific files — never use `git add .` or `git add -A` blindly:

```bash
# Stage changed tracked files only
git add <file1> <file2> ...

# Or stage all modified+deleted tracked files (not untracked)
git add -u
```

**Never stage:**
- `.env`, `.env.local`, `.env.*` — secrets
- Large binaries not previously tracked
- Auto-generated lock files that the user didn't explicitly change

### Step 3 — Write the commit message

Follow conventional commits:

| Prefix | When |
|---|---|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `refactor:` | Code restructure, no behavior change |
| `chore:` | Build, config, tooling changes |
| `test:` | Adding or updating tests |
| `docs:` | Documentation only |
| `style:` | Formatting, no logic change |
| `perf:` | Performance improvement |

Message format:
```
<type>(<optional scope>): <short imperative description>

<optional body — the WHY, not the WHAT>
```

Examples:
```
feat(auth): add Zod validation to login form
fix(api): handle missing user_id in itinerary creation
refactor(db): extract query helpers into lib/supabase/queries.ts
chore: update supabase package to 2.x
```

### Step 4 — Commit

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

### Step 5 — Push

```bash
# First push on a new branch
git push -u origin <branch-name>

# Subsequent pushes
git push
```

After push, confirm with `git status` and report the branch name and commit hash.

---

## Rules

- Never force-push to `main` or `master`
- Never commit `.env` files
- Never use `--no-verify` to skip hooks
- If a pre-commit hook fails, fix the underlying issue and create a new commit — never amend a published commit
- If the user is on `main` and hasn't branched, ask before pushing directly
- Always echo the final commit message to the user before committing so they can review it
