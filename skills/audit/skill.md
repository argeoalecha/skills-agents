---
name: audit
description: Lifecycle audit against the SDLC Structural Plan's gates G0–G7, scaled by project tier (T1–T3) and AI feature class (A1–A4). Three modes — gap (read-only retrofit scorecard of an existing project), gate G3 (pre-merge), gate G5 (pre-release GO/NO-GO). Scores every check Pass / Partial / Missing / N/A with evidence, ranks gaps by the plan's severity rules, writes the report to the private audit-reports folder outside the repo, and issues a sign-off. Use before merging to main, before any production release, when retrofitting an existing project, or for a security, privacy or production-readiness review. Triggers on "audit", "gap audit", "retrofit audit", "security review", "pre-production audit", "is this ready for production", "production readiness", "go/no-go", "ship check", "gate G3", "gate G5".
---

# Lifecycle Audit

The SDLC Structural Plan defines **what** an audit must cover. This skill holds the checks and runs them. Gate exit criteria are the checks in `references/checks.yaml` filtered by gate, tier and AI class — there is no second checklist anywhere else.

Vocabulary used throughout:

| Term | Values | Meaning |
|---|---|---|
| Gate | G0 governance · G1 requirements · G2 design · G3 build · G4 verify · G5 release · G6 operate (standing) · G7 retire | Lifecycle exit gates from the plan |
| Tier | T1 prototype · T2 production · T3 critical/regulated | Sets depth; a check above the project's tier is N/A |
| AI class | A1 assistive internal · A2 customer-facing generation · A3 agentic with tools · A4 decisions about people | Per AI feature; A4 is treated as T3; the stricter of tier and class wins |
| Step | 1–9 below | This skill's procedure (not lifecycle phases) |

---

## Configuration

```
AUDIT_REPORT_DIR=/Users/argeotublealecha/projects-mvp/audit-reports   # default if the env var is unset
```

Before writing anything, check the report folder:

```bash
DIR="${AUDIT_REPORT_DIR:-/Users/argeotublealecha/projects-mvp/audit-reports}"
test -d "$DIR" || { mkdir -p "$DIR" && chmod 700 "$DIR"; }
git -C "$DIR" rev-parse --is-inside-work-tree 2>/dev/null && echo "REFUSE: report dir is inside a git repo"
```

- If the folder cannot be created or is inside a git repository: **stop** and tell the user. Never fall back to writing the report into the project repo.
- Run folder: `$DIR/<client-or-internal>/<project>/<YYYY-MM-DD>-<mode>/` containing `AUDIT.md` and `evidence/`. Create it with `chmod 700`.
- All scan output goes to `evidence/` in the run folder, never to the project tree.

---

## Modes

| Mode | Invoke | Scope | Hard stops | Writes to the repo |
|---|---|---|---|---|
| `gap` | `/audit gap` | Every gate G0–G7 at the project's tier; whole history | None — failures are scored as findings | Nothing. Remediation stays in the report; offer TODO writeback after the owner signs off |
| `gate G3` | `/audit gate G3` (default on a feature branch) | G3 checks on the diff vs. base, plus every critical check | Step 2 and Step 3 | TODO.md writeback (Step 8) |
| `gate G5` | `/audit gate G5` (default on main or a release tag) | G3–G6 on the full codebase, plus every critical check, plus G0–G2 records the release depends on (G0-05, G1-01, G1-02, G2-03) | Step 2 and Step 3 | TODO.md writeback (Step 8) |
| `re-audit` | `/audit re-audit` | Prior report's open findings, files changed since, and every critical check | Same as the prior run's mode | Same as the prior run's mode |

Narrowing: `--agent <security|reliability|efficiency|compliance|quality|ai>` runs one sub-agent's checks; `--path <dir>` scopes code checks to a feature. Critical checks always run.

If the mode is ambiguous (for example, main branch of a project that has never been audited), ask once: gap or gate G5.

---

## Step 1 — Scope

Record in the report before running anything:

1. **Project facts:** name, client (or internal), repos, environments, data stores, hosting, owner.
2. **Project type:** web app (Next.js/React, `app/` or `src/`), AI (model SDK imports, prompt files, tool definitions), Python service (`pyproject.toml`, FastAPI), or a mix. Checks with `applies_if` that don't match are N/A.
3. **Tier with a one-line rationale.** Read it from the G1 record if one exists (the Project Profile in the project `CLAUDE.md`, or PRD §7); otherwise derive it — real users, personal data or a paying client means at least T2; finance, health, industrial/OT or contractual compliance means T3 — and confirm with the user in one question.
4. **AI class per AI feature** (A1–A4) with a one-line rationale. A feature that gained tools or now decides about people moves class.
5. **Operating mode:** team or solo. Solo enables the recorded-substitute rule on G3-61 and related checks.
6. **Lifecycle phase now:** which gate the project is working toward (used for follow-ups in Step 9).

---

## Step 2 — Pre-flight

```bash
git branch --show-current
git status --short
git log origin/main..HEAD --oneline 2>/dev/null
git grep -l "^<<<<<<< " -- ':!*.md' 2>/dev/null
ls package-lock.json pnpm-lock.yaml yarn.lock bun.lock bun.lockb uv.lock poetry.lock 2>/dev/null
ls supabase/migrations/ 2>/dev/null | sort | tail -5   # applied state: supabase migration list, or Supabase MCP list_migrations
```

| Condition | gate G3 | gate G5 | gap |
|---|---|---|---|
| Uncommitted changes | Stop | Stop | Record the commit audited; continue |
| On main | Stop (audit the feature branch) | Expected | Expected |
| Merge conflict markers | Stop | Stop | Finding (High) |
| No lockfile for a manifest present | Stop | Stop | Finding against G3-09 |
| Migrations in repo not applied to production | n/a | Stop | Finding against G3-23 |

On a stop: list the issues, say what to fix, halt.

---

## Step 3 — Build validation

Run what the project has (Node and/or Python):

```bash
npx tsc --noEmit
npx eslint .                      # errors fail; warnings are reported, not blocking
npx prettier --check .
npx vitest run --coverage         # or npm test; changed-lines coverage threshold default 80%
npm run build                     # catches env access, RSC boundaries, route conflicts
ruff check services/ && pytest --cov services/   # if Python services exist
```

Then read the build output table for bundle budgets (check G3-31).

- **Gate modes:** any error halts the audit (G3-30, G3-20 Missing). Report the exact errors.
- **Gap mode:** record results against G3-20 and G3-30 and continue; a failing build is a finding, not a reason to stop scoring.

---

## Step 4 — Evidence scans (read-only)

Run each tool that is installed; for a missing tool, say how to install it and score its checks Partial ("not verified") — never Pass without evidence.

| Tool | Command (output to `$RUN/evidence/`) | Checks |
|---|---|---|
| Gitleaks | gap / gate G5: `gitleaks git --log-opts="--all" --redact --report-format json --report-path $RUN/evidence/gitleaks.json`; gate G3: `--log-opts="<base>..HEAD"` | G3-01 |
| Semgrep CE | `semgrep scan --config p/default --config p/nextjs --config p/typescript --sarif -o $RUN/evidence/semgrep.sarif` (add `--baseline-commit <base>` in gate G3; `p/python` for services) | G3-03, G3-04, G3-06 |
| OSV-Scanner | `osv-scanner scan source -r . --format json --output $RUN/evidence/osv.json` | G3-05 |
| Trivy | `trivy fs --scanners vuln,misconfig,secret . --format json -o $RUN/evidence/trivy.json` (if Dockerfile or IaC) | G4-09 |
| ZAP baseline | Against a preview or staging URL only, never production | G4-02 |
| actionlint, zizmor | over `.github/` | G3-62 |
| Supabase | Security and performance advisors (Supabase MCP `get_advisors`); read-only SQL from G3-08 | G3-08, G3-32 |
| GitHub | `gh api repos/<o>/<r>/branches/main/protection`, `.../rulesets`, `.../environments/production` | G3-60, G3-61, G5-01 |
| Vercel / GCP | `vercel.json`, `vercel ls --prod`, `vercel env ls production`, `gcloud run services list` | G2-08, G5-01, G5-06, G5-07 |

**Secret handling (applies to every step and every sub-agent):**
- Never print, store or quote a secret value. Use `--redact`; report file, line and secret type only.
- A live secret found anywhere is Critical. Tell the owner immediately in the conversation to rotate it, then continue; the report records that rotation was requested, not the value.
- Scan output stays in the run folder. The report cites evidence by relative path or URL; it never copies personal data.

---

## Step 5 — Parallel analysis

Filter `references/checks.yaml` for this run: gate in the mode's scope, `min_tier` ≤ project tier (higher tiers become N/A), `ai_class` matching at least one feature, `applies_if` true. Group the remaining checks by `agent`.

Spawn sub-agents in parallel with `Agent` (`subagent_type: "general-purpose"`), one per non-empty group among: **security, reliability, efficiency, compliance, quality, ai** (ai only when an A2–A4 feature exists; A1 checks go to it too if it runs, otherwise to the main agent). Checks with `agent: main` — platform settings, governance records, pipeline config — are done by the main agent, which has the CLI and MCP access.

Each sub-agent prompt contains: the scope facts from Step 1, its check entries verbatim, the paths to scan output in `evidence/`, the secret-handling rules above, and this return format — one row per check:

```
id | status (Pass/Partial/Missing/N/A) | evidence (path, file:line or URL) | finding (one line, no secret values) | condition flags (pii_exposed / live_secret / no_restore_path / none)
```

Sub-agents report; they do not fix code or change settings.

---

## Step 6 — Score and rank

**Status**

| Status | Rule |
|---|---|
| Pass | In place and enforced, with a linked piece of evidence |
| Partial | Exists but not enforced, incomplete, untested, or could not be verified |
| Missing | Not in place |
| N/A | Above the project's tier, or `applies_if`/`ai_class` does not apply |

**Severity** (fix windows from the plan)

| Severity | Rule | Fix window |
|---|---|---|
| Critical | Personal data exposed, a live secret in history, or no working restore path — regardless of which check found it | Before the next release |
| High | A security (S) or reliability (R) check required at the tier is Missing; any critical check that is Partial | This cycle |
| Medium | Any other Partial at the tier | Within two cycles |
| Low | Efficiency (E), quality and documentation gaps | Backlog |

Repeat findings: any Critical or High that was open in the prior report gets `(flagged N× — first seen YYYY-MM-DD)` and leads its severity section. A repeat High escalates to Critical on its third appearance.

**Gate status**: a gate is *cleared* at the tier when none of its in-scope checks is Missing and every critical check in it is Pass.

---

## Step 7 — Write the report

Write `$RUN/AUDIT.md` using `references/report-template.md`. Include the full scorecard, the gate summary, the critical-check table, the ranked backlog with fix windows, and the sign-off block. Do not suggest code fixes inline; findings state what is wrong and where.

---

## Step 8 — Remediation writeback

| Mode | Behaviour |
|---|---|
| gate G3, gate G5, re-audit of a gate run | Append to the project's `TODO.md` (create if absent) as a new top-level section after the highest existing one, using the format in the report template. Items cite check IDs and file:line only, never secret values or personal data. Skip items already present (same check ID and location). Preserve existing content. `/plan-todo` refreshes keep this section verbatim. |
| gap | Write nothing to the repo. After the owner or client signs off the report, offer to append the backlog to `TODO.md`. |
| re-audit | Strike through resolved items: `~~item~~ (resolved YYYY-MM-DD)`. |

Cheap fixes (scanners, CI checks on changed code, Sentry, uptime, billing alerts, region pin, backups and a restore drill) go under a "First-week safety net" heading; costly ones (RLS on live data, auth redesign, database region move, data-model changes) are listed as scheduled features. Security gaps on live personal data are always first, whatever they cost.

---

## Step 9 — Sign-off and follow-ups

**Gate modes (GO / NO-GO).** Default is NO-GO. Automatic NO-GO when any of these holds:
- any Critical finding;
- any critical check in scope that is not Pass;
- any High in a security or reliability check of the gate being exited (G3 for gate G3; G4 and G5 for gate G5), unless accepted below;
- Step 2 or Step 3 skipped or failed.

GO with risks accepted: the owner may accept specific High findings. Each acceptance records the check ID, a one-sentence justification, the owner, the approver (the client for client engagements), and a review date; each gets a TODO item. Critical findings cannot be accepted.

**Gap mode (no GO/NO-GO).** Report gate status G0–G7 at the tier, the tier the project currently meets, and what blocks the next gate. The report is signed off by the project owner or client.

**Follow-ups** come from tier and lifecycle phase, not from a separate maturity scale:
1. Checks for the next gate the project is working toward that are not yet Pass.
2. If the user plans to raise the tier: the checks that become in scope at the next tier (for T2 → T3: external pen test G4-07, staging and failure injection G4-10, canary and signed images G5-09, feature flags G3-26, PITR under G6-05).
3. Related skills where they produce evidence a check needs: `/load-test` (G4-03), `/e2e-test` (G4-01), `/web-perf-audit` on the deployed URL (G5-04, G2-09), `/ux-review` for flow-level UX and SEO, `/ph-dpa-compliance` when compliance findings exist, `/legal-docs` for templates (not legal advice), `/feature-dev` on the highest-severity item.

**Out of scope** (say so in the report; do not score as Pass): manual penetration testing (required evidence at T3 — score G4-07 on the report, not by testing), legal review by counsel, real-user research, copy editing.

---

## Re-audit cadence

Re-audit after remediation, then quarterly at T2, before each major release at T3, and always before raising a project's tier. Also re-audit after a dependency upgrade of a framework or model SDK, a schema migration touching RLS, or a change of AI class.

---

## Rules

- `gap` mode is read-only: nothing in the project or its platforms changes.
- Critical findings always block a release and cannot be accepted. Do not soften this.
- Pass requires evidence. Unverifiable means Partial.
- Never write the report or scan output into the project repo.
- Never print or store secret values; request rotation of any live secret at once.
- ZAP and other active tests run against preview or staging only.
- Cite RA 10173 sections and NPC advisories precisely in compliance findings (portability is §18; erasure is §16(e); AI transparency is NPC Advisory 2024-04; scraping is NPC Advisory 2026-01).
- A check's wording lives in `references/checks.yaml`. To add or change a check, edit that file; never renumber IDs.
