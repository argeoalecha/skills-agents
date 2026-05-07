---
name: audit
description: Pre-production code audit. Runs build validation, type checking, and tests first — then launches parallel sub-agents for deep static analysis across security, reliability, performance, compliance, and code quality. Use before any production deployment, PR merge to main, or security review. Triggers on "audit the code", "security review", "check for vulnerabilities", "pre-production audit", "is this ready for production", or "code quality check".
---

# Comprehensive Pre-Production Audit

## Overview

Two-stage workflow: first validates the build compiles and tests pass (Phase 0), then runs parallel deep static analysis across all dimensions (Phase 1: Parallel Analysis). A Phase 0 failure is a hard stop — there is no point auditing code that cannot be built.

## Audit Modes

```
User requests audit
├─ Full Audit   → Phase 0 + all 4 parallel sub-agents (10-15 min)
├─ Quick Check  → Phase 0 + Critical findings only (5 min)
├─ Targeted     → Phase 0 + one sub-agent (/audit security|reliability|performance|compliance|quality)
└─ Component    → Phase 0 + all sub-agents scoped to specific files/feature
```

---

## Phase 0 — Build Validation (Hard Stop)

Run all three sequentially. If any fail, halt and report — do not proceed to Phase 1.

```bash
# 1. Type check
npx tsc --noEmit

# 2. Lint
npx eslint . --ext .ts,.tsx --max-warnings 0

# 3. Tests
npx vitest run   # or: npm test / npx jest
```

**Pass criteria:** Zero TypeScript errors, zero ESLint errors, all tests green.

If Phase 0 fails: report the exact errors, suggest fixes, and tell the user to re-run `/audit` after fixing.

---

## Phase 1 — Parallel Sub-Agent Analysis

After Phase 0 passes, spawn four sub-agents in parallel. Each focuses on one audit dimension.

### Sub-Agent A: Security
Scan for:
- Hardcoded secrets, API keys, credentials in source files
- SQL injection vectors (unparameterized queries)
- XSS vulnerabilities (unsafe `dangerouslySetInnerHTML`, unescaped user data)
- CSRF: missing SameSite cookies, unprotected mutations
- Insecure `eval()` or `Function()` calls
- Exposed service role keys in client-side code
- Missing auth guards on protected routes
- Dependency vulnerabilities: `npm audit --audit-level=high`
- Environment variable leakage (client bundle exposing `NEXT_PUBLIC_*` secrets)

### Sub-Agent B: Reliability
Scan for:
- Unhandled promise rejections (no try/catch around async operations)
- Missing null/undefined guards at data boundaries
- Race conditions in concurrent operations
- Missing error boundaries in React component trees
- Infinite loops or missing base cases in recursion
- Memory leaks: event listeners not cleaned up, intervals not cleared
- Missing loading and error states in UI components
- Database queries with no `.single()` guard for expected single-row results

### Sub-Agent C: Performance
Scan for:
- N+1 query patterns (queries inside loops)
- Missing pagination on list endpoints
- Large bundle size: unoptimized imports, missing tree-shaking
- Missing `React.memo`, `useMemo`, `useCallback` on expensive computations
- Synchronous operations blocking the event loop
- Missing caching on expensive or frequently-called routes
- Unoptimized images (missing `next/image`, large uncompressed files)
- Missing database indexes for common query patterns

### Sub-Agent D: Compliance (Philippines DPA / RA 10173)
Scan for:
- Missing consent checkbox on registration and public data collection forms
- No privacy policy page linked from auth and landing pages
- Personal data stored beyond stated retention period
- PII in log statements (`console.log(user.email)`, etc.)
- No data export endpoint (right to data portability)
- No account deletion / data purge endpoint (right to erasure)
- Missing IP anonymization in analytics
- Full IP addresses stored in logs or analytics tables
- Unencrypted PII in database columns that should use hashing

---

## Output Format

Produce an `AUDIT.md` file at the project root:

```markdown
# Pre-Production Audit Report
Date: YYYY-MM-DD
Auditor: Claude Code (/audit)

## Phase 0: Build Status
- TypeScript: PASS / FAIL (N errors)
- ESLint: PASS / FAIL (N warnings)
- Tests: PASS / FAIL (N passing, N failing)

## Critical Findings (block deployment)
- [SECURITY] <description> — <file:line>
- [RELIABILITY] <description> — <file:line>

## High Findings (fix before merge)
- [PERFORMANCE] <description> — <file:line>
- [COMPLIANCE] <description> — <file:line>

## Medium Findings (fix soon)
- ...

## Low / Advisory
- ...

## Summary
Critical: N | High: N | Medium: N | Low: N
Deployment recommendation: BLOCKED / PROCEED WITH CAUTION / CLEAR
```

---

## Rules

- Never skip Phase 0 even for targeted audits
- Do not suggest fixes inline — report findings and let the user decide
- For compliance findings, reference the specific RA 10173 article or NPC Advisory when possible
- Critical findings always block deployment — do not soften this recommendation
- After audit, offer to run `/ph-dpa-compliance` if compliance findings are present
