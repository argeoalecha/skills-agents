# Report template

Write this to `$RUN/AUDIT.md`. Keep every section; write "None" where empty.

```markdown
# Audit Report — <project>

| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| Mode | gap / gate G3 / gate G5 / re-audit (of <prior run>) |
| Client | <client or internal> |
| Repos · commit | <repo>@<short SHA> (branch <name>) |
| Tier | T1 / T2 / T3 — <one-line rationale> |
| AI features | <feature>: A1–A4 — <rationale> (or "none") |
| Operating mode | team / solo |
| Working toward | G<n> |
| Auditor | Claude (audit skill) for <owner> |

## Summary
Critical: N · High: N · Medium: N · Low: N
Checks in scope: N (Pass N · Partial N · Missing N) · N/A: N
Verdict: GO / GO with risks accepted / NO-GO     ← gate modes
Tier met: T<n>; next gate blocked by: <check IDs> ← gap mode

## Critical checks
| ID | Check | Status | Evidence |
|---|---|---|---|
| G3-01 | No secrets in git history | | |
| G3-02 | No secret keys in the browser | | |
| G3-08 | RLS on every exposed table | | |
| G2-08 | Function region co-located with DB | | |
| G4-04 | Restore drill passed | | |
| G5-01 | Production changes only through the pipeline | | |
| G6-05 | Backups working | | |
| G3-61 | Main protected; solo substitute recorded | | |
| G0-05 | Client access register | | |
| G7-04 | Handover pack | | |
| G2-03 | LLM threat model (A2–A4) | | |
| G4-05 | Eval gate (A2–A4) | | |
| G6-08 | Token budgets (A2–A4) | | |

## Gate status
| Gate | Pass | Partial | Missing | N/A | Cleared at tier |
|---|---|---|---|---|---|
| G0 | | | | | yes / no |
| … | | | | | |
| G7 | | | | | |

## Build and scans
- Build: tsc · eslint · tests (coverage) · build · bundle — results
- Scans run: gitleaks / semgrep / osv / trivy / zap / advisors — each with evidence path, or "not installed"

## Findings (ranked)
### Critical — fix before the next release
- [G3-01] <finding> — `file:line` — evidence: evidence/gitleaks.json (rotation requested YYYY-MM-DD)
### High — fix this cycle
### Medium — fix within two cycles
### Low — backlog

Repeat findings lead their section and carry `(flagged N× — first seen YYYY-MM-DD)`.

## Scorecard
| ID | Gate | Pillar | Tier | Check (short) | Status | Severity | Evidence | Finding |
|---|---|---|---|---|---|---|---|---|

## Remediation plan
### First-week safety net (cheap)
### Scheduled features (costly)
### Risk acceptances
- [ID] — Justification: … — Owner: … — Approved by: … — Review: YYYY-MM-DD

## Sign-off
**Verdict / gate status:** …
Blockers: …
Approved for: production / preview / n/a (gap)
Signed by: <owner> · <client approver> · On: YYYY-MM-DD

## Follow-ups
- Next gate: …
- Next tier (if planned): …
- Related skills: …
- Out of scope: manual pen testing, legal review, user research, copy editing

## Next re-audit
<date or trigger: quarterly (T2) / before major release (T3) / before raising tier / framework or model SDK upgrade / RLS migration / AI class change>
```

## TODO.md writeback format

```markdown
## Audit Remediation (YYYY-MM-DD, <mode>)
Source: audit-reports/<client>/<project>/<run>/AUDIT.md (private)
Verdict: <GO / NO-GO / GO with risks accepted>

### Critical — before next release
- [ ] [G3-08] Enable RLS on `public.invoices` — `supabase/migrations/…`
### High — this cycle
- [ ] [G5-01] Disable Vercel git auto-deploy for production; deploy only via release.yml
### Medium — within two cycles
### Low — backlog
```

Items cite check ID plus location only — no secret values, no personal data.
