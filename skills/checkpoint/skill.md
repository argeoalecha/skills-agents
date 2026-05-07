---
name: checkpoint
description: End-of-session skill. Saves a structured checkpoint file so the next session can resume instantly. Invoke before ending any working session. Triggers on /checkpoint, "save checkpoint", "save session", "save my place", "I'm stopping", "end of session", or "before I go".
---

# Session Checkpoint

Saves `SESSION_CHECKPOINT.md` to the project root so `/resume` can reconstruct your exact state in the next session without re-reading all project files.

---

## When to Use

Run `/checkpoint` before:
- Closing Claude Code
- Switching to a different project
- Taking a break from active development

If a session ends unexpectedly, `/resume` will detect the stale checkpoint and reconstruct from git history — but a fresh checkpoint is always more accurate.

---

## Checkpoint File Format

Save to: `<project-root>/SESSION_CHECKPOINT.md`

```markdown
# Session Checkpoint
Saved: YYYY-MM-DD HH:MM PHT

## Project
<project name and one-line purpose>

## What We Accomplished This Session
- <specific thing completed>
- <specific thing completed>
- ...

## Currently In Progress
<what is actively being worked on — be precise about which file/feature/step>

## Next Steps (in order)
1. <first thing to do in next session>
2. <second thing>
3. <third thing>

## Key Decisions Made
- <decision + brief rationale>
- ...

## Files Changed This Session
- `path/to/file.ts` — <what changed and why>
- ...

## Known Issues / Blockers
- <issue or blocker — include error messages or reproduction steps if relevant>

## Environment / Setup Notes
<anything needed to run the project — env vars to set, servers to start, etc.>

## Relevant Context
<anything that would be lost without this checkpoint — constraints, user preferences for this project, links, account IDs, etc.>
```

---

## How to Create the Checkpoint

1. **Review the session**: Scan recent conversation for what was accomplished
2. **Check git status**: `git status && git log --oneline -10` to confirm what was committed
3. **Check open tasks**: Any TODOs or in-progress work that wasn't finished
4. **Write the file**: Use the template above — be specific, not generic
5. **Confirm**: Tell the user where it was saved and what the next recommended action is

---

## Rules

- Be specific — "modified the login form" is useless; "added Zod validation to `app/(auth)/login/page.tsx`, tests pass" is useful
- List next steps in priority order — the first one should be immediately actionable
- If there are merge conflicts, uncommitted changes, or broken tests, note them under "Known Issues"
- Do not write lengthy prose — bullet points are faster to scan on resume
- The checkpoint is for the next Claude session — write it so a fresh context can pick up instantly
