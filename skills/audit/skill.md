---
name: audit
description: Pre-production hard gate. Runs build validation, then parallel deep static analysis across security, reliability, performance, compliance, quality, and accessibility, then production-readiness gates (env, monitoring, CI, rate limits, backups), then writes findings back to TODO.md as an Audit Remediation phase, then issues an explicit GO/NO-GO sign-off. Use before any production deployment, PR merge to main, or security review. Adapts to project type (web app vs. AI/agent). Triggers on "audit the code", "security review", "check for vulnerabilities", "pre-production audit", "is this ready for production", "code quality check", "production readiness", "go/no-go", or "ship check".
---

# Pre-Production Audit — Production Hard Gate

A multi-phase production gate. Every project that runs through `/audit` must clear all phases before earning a GO sign-off. Findings flow into the project's `TODO.md` as an Audit Remediation phase so they cannot be forgotten.

---

## Phase Summary

```
Phase 0 — Pre-flight checks         (git hygiene + branch state)        HARD STOP
Phase 1 — Build Validation          (typecheck, lint, test, build)      HARD STOP
Phase 2 — Parallel Static Analysis  (5 sub-agents in parallel)
Phase 3 — Production Readiness      (env, monitoring, CI, rate limits, backups)
Phase 4 — TODO Writeback            (append findings to TODO.md)
Phase 5 — Sign-off Gate             (explicit GO / NO-GO)
```

---

## Audit Modes

```
Full Audit    → All phases (10–20 min)                        — default
Quick Check   → Phases 0+1, Critical findings only             — fast pre-commit
Targeted      → Phases 0+1 + one sub-agent                     — /audit security
Component     → All phases scoped to specific files/feature
Re-audit      → Diff vs. last AUDIT.md, re-check prior issues  — after fixes
```

---

## Project Type Detection

Before Phase 0, detect project type from the codebase or TDD:

- **Web App**: has `app/` or `src/`, `package.json` with Next.js/React, DB migrations
- **AI / Agent / Automation**: imports `@anthropic-ai/sdk`, has prompt files, tool definitions, agent flow
- **Hybrid**: both signals present

Adapt sub-agent checks accordingly (see Phase 2).

---

## Phase 0 — Pre-flight Checks (Hard Stop)

Block audit if any of these fail. The user must clean up first.

```bash
# Branch state
git branch --show-current                              # Should not be 'main' for a real audit
git status --short                                     # Should be empty (no uncommitted)
git log origin/main..HEAD --oneline 2>/dev/null        # Commits to be deployed

# Working tree sanity
test -f package.json && test -f package-lock.json      # Lockfile present
git ls-files | xargs grep -l "<<<<<<< HEAD" 2>/dev/null # Merge conflict markers

# Migrations
ls supabase/migrations/ 2>/dev/null | sort | tail -5   # Check for un-applied migrations
```

**Block conditions:**
- Uncommitted changes present
- On `main`/`master` directly (audit a feature branch before merge)
- Merge conflict markers in any tracked file
- Missing lockfile

If blocked: list the issues, suggest fixes, halt. Do not proceed.

---

## Phase 1 — Build Validation (Hard Stop)

Run sequentially. Any failure halts the audit.

```bash
# 1. Type check
npx tsc --noEmit

# 2. Lint
npx eslint . --ext .ts,.tsx --max-warnings 0

# 3. Tests
npx vitest run        # or: npm test / npx jest

# 4. Production build
npm run build         # catches what tsc misses (env access, RSC boundaries, route conflicts)

# 5. Bundle size sanity (if applicable)
ls -lh .next/static/chunks/*.js 2>/dev/null | sort -k5 -h | tail -5  # largest 5 chunks
```

**Pass criteria:** Zero TS errors, zero ESLint errors, all tests green, production build succeeds, no chunk exceeds 500KB without justification.

If Phase 1 fails: report exact errors, halt. Do not proceed to Phase 2.

---

## Phase 2 — Parallel Static Analysis

After Phase 1 passes, spawn 5 sub-agents in parallel using `Agent` with `subagent_type: "general-purpose"`. Each agent receives a focused prompt and returns findings in a structured format. Merge results in the audit report.

### Sub-Agent A: Security

**Web App + AI/Agent (always check):**
- Hardcoded secrets, API keys, credentials, tokens (search for `sk_live_`, `pk_`, `Bearer `, `password =`, `apiKey =`)
- Hardcoded production URLs that should be env vars
- Exposed service role keys or admin keys in client-side code
- Environment variable leakage in client bundle (`NEXT_PUBLIC_*` exposing secrets)
- `eval()`, `Function()`, dynamic imports of user input
- Open redirects, path traversal, SSRF in URL fetch operations
- Dependency vulnerabilities: `npm audit --audit-level=high`

**Web App-specific:**
- SQL injection: unparameterized queries, string-concatenated SQL
- XSS: `dangerouslySetInnerHTML` with unsanitized input, unescaped user content
- CSRF: missing SameSite cookies, unprotected POST/PATCH/DELETE
- Missing auth guards on protected routes / API endpoints
- Missing RLS policies on user-facing Supabase tables
- Webhook endpoints without signature verification

**AI/Agent-specific:**
- Prompt injection vectors (untrusted input concatenated into system prompt)
- Tool permission scope (least privilege — what can each tool actually access?)
- Output validation before consuming tool results in downstream actions
- API key handling (env vars only, never in prompts or logs)

### Sub-Agent B: Reliability

**Always:**
- Unhandled promise rejections (async without try/catch)
- Missing null/undefined guards at data boundaries
- Race conditions in concurrent operations
- Idempotency on POST endpoints with side effects (payment, email, write)
- Database transaction boundaries on multi-step writes

**Web App-specific:**
- Missing error boundaries in React component trees
- Missing loading and error states in UI components
- Memory leaks: event listeners not cleaned up, intervals not cleared
- Database queries with no `.single()` guard for expected single-row results

**AI/Agent-specific:**
- Error/fallback handling on Claude API failures, parse failures, timeouts
- Bad-output recovery (retry with stricter prompt, default value, or escalation)
- Tool call failure recovery (retry, skip, abort)
- Max iteration / max token guard on agent loops

### Sub-Agent C: Performance

**Always:**
- N+1 query patterns (queries inside loops)
- Synchronous operations blocking the event loop
- Missing database indexes for common query patterns

**Web App-specific:**
- Missing pagination on list endpoints
- Large bundle size, unoptimized imports
- Missing `React.memo`, `useMemo`, `useCallback` on expensive computations
- Missing caching on expensive routes (`fetch` `cache: 'force-cache'` or Next.js `revalidate`)
- Unoptimized images (missing `next/image`, large uncompressed files)

**AI/Agent-specific:**
- Prompt caching not configured for repeated long system prompts
- Missing token usage logging
- No batch API usage where applicable
- Cost guard rails (max tokens, max iterations) absent

### Sub-Agent D: Compliance — Philippines DPA (RA 10173)

- Missing consent checkbox on registration and public data collection forms
- No privacy policy page linked from auth and landing pages
- Missing cookie consent banner on EU/PH-targeted public sites
- PII in log statements (`console.log(user.email)`, etc.)
- PII in Claude prompts or tool inputs (sanitization layer absent)
- Personal data stored beyond stated retention period
- No data export endpoint (right to data portability — RA 10173 §16)
- No account deletion / data purge endpoint (right to erasure)
- Missing IP anonymization in analytics
- Full IP addresses stored in logs or analytics tables
- Unencrypted PII in DB columns that should use hashing
- Missing Data Processing Agreement when third-party processors are used

### Sub-Agent E: Quality + Accessibility

**Code Quality:**
- TODO/FIXME/HACK/XXX comments left in code (list them all)
- `console.log`, `debugger`, `// eslint-disable` left in production paths
- Files exceeding 500 lines without clear modular structure
- Functions with cyclomatic complexity > 15
- Dead code (exported but never imported)
- Naming inconsistent with project standards (file naming, component naming)
- Magic numbers without named constants
- `any` types in TypeScript code

**Accessibility (Web App only):**
- Interactive elements without keyboard support (`onClick` without `onKeyDown`)
- Missing ARIA labels on icon-only buttons
- Missing `alt` attributes on images
- Form inputs without associated `<label>` or `aria-label`
- Color contrast violations (WCAG AA: 4.5:1 normal, 3:1 large)
- Missing focus states on interactive elements
- Non-semantic markup (`<div onClick>` instead of `<button>`)
- Missing skip-to-content link on long pages
- No focus management on route changes / modal opens

---

## Phase 3 — Production Readiness Gates

Each item is a checkbox: PASS / FAIL / N/A. Fail blocks deployment.

### Environment & Secrets
- [ ] All required env vars documented in `.env.example`
- [ ] No real secrets in `.env.example` (placeholders only)
- [ ] `.env*` files in `.gitignore` (verify with `git check-ignore`)
- [ ] No hardcoded secrets in source (already covered Sub-Agent A — re-verify here)
- [ ] Production env vars set in deployment platform (Vercel/Netlify dashboard)

### Monitoring & Observability
- [ ] Error monitoring configured (Sentry client + server, or equivalent)
- [ ] `/api/health` (or platform health check) endpoint exists and returns 200
- [ ] Structured logging in place for API routes (request id, user id, duration)
- [ ] **AI/Agent**: token usage logging, cost tracking, error rate monitoring

### Rate Limiting & Abuse
- [ ] Rate limiting on public POST/PATCH/DELETE endpoints
- [ ] Rate limiting on auth endpoints (login, signup, password reset)
- [ ] **AI/Agent**: per-user rate limit on agent runs, max-cost guardrail

### Security Headers
- [ ] CSP configured (`next.config.js` `headers()` or middleware)
- [ ] HSTS enabled
- [ ] X-Frame-Options or frame-ancestors set
- [ ] X-Content-Type-Options: nosniff

### Data Integrity & Disaster Recovery
- [ ] All Supabase migrations have reversal SQL (or documented rollback plan)
- [ ] Foreign keys with appropriate `ON DELETE` behavior (CASCADE vs. RESTRICT vs. SET NULL — intentional)
- [ ] Backup schedule confirmed for production DB (Supabase: PITR enabled on Pro plan)
- [ ] Soft-delete columns indexed where queried

### CI/CD
- [ ] GitHub Actions (or platform CI) runs Phase 1 checks on every PR
- [ ] Branch protection on `main`: require PR review, require CI passing
- [ ] Preview deploys configured (Vercel/Netlify auto-preview on PRs)

### Documentation
- [ ] `README.md` with setup instructions, env var docs, deploy instructions
- [ ] `CLAUDE.md` present (project-specific Claude instructions if applicable)
- [ ] Runbook for common production incidents (or note "first incident → write runbook")

### Deployment Platform-Specific
- **Vercel**: project linked, env vars set per environment (preview/production), domains configured
- **Supabase**: production project URL set, RLS confirmed enabled on all user-facing tables (`SELECT tablename FROM pg_tables WHERE schemaname='public'` then check each)
- **Netlify**: build command set, publish directory correct, redirect rules in `netlify.toml`

---

## Phase 4 — TODO Writeback (Auto)

After Phase 2 and Phase 3 complete, append findings to the project's `TODO.md` as a new phase. **This always runs — do not ask first.** If `TODO.md` does not exist, create it.

### Format

```markdown
## Phase X: Audit Remediation (YYYY-MM-DD)
Source: AUDIT.md (this audit run)
Audit verdict: <GO / NO-GO / GO with risks accepted>

### Critical (BLOCKS DEPLOYMENT)
- [ ] [SECURITY] Remove hardcoded API key in `lib/api.ts:23`
- [ ] [RELIABILITY] Add error boundary to `app/dashboard/layout.tsx`

### High (must fix before merge)
- [ ] [COMPLIANCE] Add consent checkbox on `app/signup/page.tsx`
- [ ] [READINESS] Configure Sentry server-side

### Medium (fix this sprint)
- [ ] [PERFORMANCE] Optimize N+1 in `lib/getTrips.ts:45`
- [ ] [QUALITY] Remove 14 TODO comments — see AUDIT.md §5.2

### Low / Advisory (next sprint)
- [ ] [A11Y] Add skip-to-content link
- [ ] [QUALITY] Replace 3 magic numbers with named constants
```

### Rules for writeback
- Insert as a new top-level Phase, numbered after the highest existing phase
- Preserve existing TODO content unchanged
- Do not duplicate items: if an item with the same `[CATEGORY] description — file:line` already exists, skip it
- Re-audit mode: mark previously-found items that are now resolved with `~~strikethrough~~ (resolved YYYY-MM-DD)`

---

## Phase 5 — Sign-off Gate (Hard Gate)

Default verdict is **NO-GO**. The verdict only flips to **GO** if all conditions below are met. The user must read this section and respond before deployment.

### Auto NO-GO conditions
- Any Critical finding from Phase 2
- Any FAIL from Phase 3 in: Env/Secrets, Monitoring, Rate Limiting, Data Integrity
- Phase 0 or Phase 1 was skipped or failed

### Conditional GO with risks accepted
The user may accept specific High findings to proceed. Each accepted risk must be:
- Listed by name in the Sign-off block
- Justified in one sentence
- Have a follow-up TODO item with a date

### Sign-off Block (output)

```markdown
## Sign-off

**Verdict: GO / NO-GO**

### Blockers (must resolve before deploy)
- <Critical or required-pass items still open>

### Risks Accepted (deploying anyway)
- <High item> — Justification: <why>. Follow-up due: YYYY-MM-DD.

### Approved for deployment to: <production / staging / canary>
By: <user>
On: YYYY-MM-DD

### Next re-audit triggered by:
- Code change in audited files
- Dependency upgrade
- Schema migration
- Time elapsed: 30 days
```

---

## Output: AUDIT.md

Always write a full report to `AUDIT.md` at the project root.

```markdown
# Pre-Production Audit Report
Date: YYYY-MM-DD
Project type: <Web App / AI Agent / Hybrid>
Branch: <branch name>
Commit: <short SHA>

## Phase 0: Pre-flight — PASS / FAIL
<details>

## Phase 1: Build Validation — PASS / FAIL
- TypeScript: PASS / FAIL (N errors)
- ESLint: PASS / FAIL
- Tests: PASS / FAIL (N passing / N failing)
- Production build: PASS / FAIL
- Bundle size: largest chunk N KB

## Phase 2: Static Analysis Findings

### Critical (block deployment)
- [SECURITY] <description> — `file:line`
- [RELIABILITY] <description> — `file:line`

### High (fix before merge)
- ...

### Medium / Low / Advisory
- ...

## Phase 3: Production Readiness Checklist
| Category | Item | Status |
|---|---|---|
| Env | All vars in `.env.example` | PASS |
| Monitoring | Sentry client | FAIL |
| ... | ... | ... |

## Phase 4: TODO Writeback
Appended N items to TODO.md under "Phase X: Audit Remediation (YYYY-MM-DD)"

## Summary
Critical: N | High: N | Medium: N | Low: N
Readiness: M/N gates passing
Verdict: GO / NO-GO

## Sign-off
<sign-off block from Phase 5>
```

---

## Re-Audit Mode

When the user runs `/audit` after a previous audit:

1. Read prior `AUDIT.md` if present.
2. Diff prior Critical/High findings vs. current code state.
3. Mark resolved items in TODO.md with `~~strikethrough~~ (resolved YYYY-MM-DD)`.
4. Run only Phase 1 (build validation) + Phase 2 (focused on prior issues + new files since last audit) + Phase 3 (recheck all gates) + Phase 4 + Phase 5.
5. Issue new sign-off.

---

## Rules

- Phase 0 and Phase 1 are hard stops — never skip them, even for targeted audits.
- Critical findings always block deployment. Do not soften this.
- Do not suggest fixes inline in the audit report — report findings, let the user decide. (Fixes go into TODO.md, then run `/feature-dev` to implement.)
- For compliance findings, reference the specific RA 10173 article or NPC Advisory when known.
- Default verdict is NO-GO. GO requires explicit pass on all blocking conditions.
- TODO writeback always runs — the audit's value is in the closure loop.
- After audit, offer to run `/ph-dpa-compliance` if compliance findings present, or `/feature-dev` on the highest-severity TODO item.

---

## Out of Scope

This audit does NOT cover:
- Load testing / performance benchmarking under realistic traffic (separate tooling)
- Manual penetration testing
- UX research / usability testing
- Content review / copy editing
- Legal review of terms of service or privacy policy

If those are needed, surface as separate follow-up tasks.
