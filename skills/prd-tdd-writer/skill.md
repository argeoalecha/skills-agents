---
name: prd-tdd-writer
description: Create OR review Product Requirements Documents (PRDs) and Technical Design Documents (TDDs) for software, web app, AI agent, and automation projects. Use when the user wants to write a PRD/TDD, spec out a product, plan a feature, document architecture, define system behavior, OR review/evaluate/critique an existing draft. Trigger on phrases like "write a PRD", "create a TDD", "spec this out", "document this feature", "design doc", "spec doc", "system design", "review my PRD", "evaluate this TDD", "critique this spec", "what's missing from this PRD", "is this TDD complete", or when the user describes an app or agent they want to build and needs formal documentation.
---

# PRD & TDD Writer / Reviewer — Hayah-AI Services

A skill for producing and reviewing lean, professional PRDs and TDDs for web apps, AI agents, automation systems, and data products.

---

## Upstream: invoked by /init

`/init` is the project bootstrapper and auto-runs this skill at the end of its chain. When invoked that way (or any time the cwd is a freshly-bootstrapped project), **a concept doc exists at `docs/concept.md`** — read it first (see Write Mode step 3). The skeleton's `CLAUDE.md` will say `Stack: TBD — decided in the TDD`; this skill's TDD is where stack, theme variant, and deploy target actually get pinned down. Treat that as a responsibility: the rest of the pipeline (`/company-site`, `/feature-dev`) reads the TDD to author framework files, so the TDD must state the chosen stack, the Hayah theme variant, and the deploy target explicitly.

---

## Mode Detection

Determine mode from the user's intent:

- **Write mode**: user wants to create a new PRD and/or TDD
- **Review mode**: user has an existing draft and wants critique, gaps identified, or quality assessed

If ambiguous, ask in one sentence before proceeding.

---

## Write Mode

### Workflow

1. **Identify doc type**: PRD (what + why), TDD (how), or both.
2. **Identify project type**: web app, AI/agent/automation, or data product. This determines which TDD template to use.
3. **Extract context.** First, if `docs/concept.md` exists in the project folder (it will when reached via `/init`), read it — it is the seed idea and the primary input. For an existing project being re-spec'd, also check for an OKF knowledge bundle (`okf/index.md`) — read it before drafting so the TDD doesn't contradict already-documented architecture/schema decisions. Then supplement from the conversation:
   - Problem / goal
   - Target users / personas
   - Core features (MVP vs. later)
   - Tech constraints already stated
   - Timeline or budget constraints
   - Philippines market relevance (Y/N)
4. **Fill gaps** — ask only what is missing, in a single block before drafting. Max 3 questions. Never ask follow-ups mid-draft.
5. **Draft document** using the matching template below.
6. **Offer follow-up**: companion doc (PRD → TDD or vice versa), task breakdown (`/plan-todo`), or save as `.md` file using Write tool at `~/projects-mvp/<project-name>/docs/`.

---

## Review Mode

### Workflow

1. Read the full document the user provides.
2. Identify doc type (PRD or TDD) and project type (web app / AI agent / data product).
3. Score against the relevant rubric below.
4. Output a structured critique.
5. Offer to produce a revised draft inline.

### PRD Review Rubric

Score each dimension: **Strong / Adequate / Weak / Missing**

| Dimension | What to check |
|---|---|
| Problem statement | Is the problem specific, bounded, and user-facing? Or vague/solution-first? |
| Goals | Are goals measurable (with numbers/targets)? Or aspirational filler? |
| Non-goals | Are exclusions explicit? Or left implicit? |
| User personas | Are personas distinct with real behavioral differences? Or generic? |
| User stories | Do stories follow As a / I can / so that? Are MVP vs. future items separated? |
| Success metrics | Are metrics tied to goals? Is measurement method defined? |
| Constraints | Are budget, timeline, technical, scale (expected traffic), and regulatory constraints stated? |
| Open questions | Are unresolved decisions surfaced? Or buried/ignored? |
| Scope clarity | Can an engineer read this and know what to build and what NOT to build? |
| Philippines DPA | Required if PII is collected — is consent mechanism mentioned? |

Output format:

```
## PRD Review

### Scores
| Dimension | Rating | Notes |
|---|---|---|
| Problem statement | Strong/Adequate/Weak/Missing | <one-line note> |
...

### Critical Gaps (must fix before building)
- <gap 1>
- <gap 2>

### Improvement Suggestions
- <suggestion 1>
- <suggestion 2>

### Verdict
<One paragraph: is this ready to hand to an engineer? What's the single most important thing to fix?>
```

### TDD Review Rubric

Score each dimension: **Strong / Adequate / Weak / Missing**

**Web App TDD:**

| Dimension | What to check |
|---|---|
| Architecture overview | Is the component interaction clear? Is there a diagram or ASCII flow? |
| Tech stack justification | Is every layer chosen with a reason? Or just defaults listed? |
| Database schema | Are all entities defined with types and constraints? Soft deletes? Audit fields? |
| RLS policies | Is row-level security defined for every user-facing table? |
| API design | Are endpoints, auth requirements, and error shapes defined? |
| Request/response shapes | Are TypeScript interfaces or Zod schemas specified? |
| Security | Auth, input validation, PII handling, DPA compliance, security headers (CSP allowlist from actual origins), rate limiting plan |
| Performance & delivery | Per-route rendering strategy (static/ISR/dynamic with reasons)? JS/font budgets stated? CDN caching plan (immutable assets, HTML s-maxage/SWR)? |
| Operational readiness | Monitoring (Sentry, health endpoint, logging), backups + migration rollback, CI gates, domain/DNS plan (incl. Cloudflare gray-cloud if applicable) |
| Testing strategy | Unit, integration, E2E coverage defined? Feature-tier E2E per MVP story? Accessibility planned (keyboard, labels, contrast)? |
| Open questions | Unresolved technical decisions surfaced? |

**AI/Agent TDD:**

| Dimension | What to check |
|---|---|
| Agent flow | Is the trigger → decision → action → output loop defined? |
| Prompt design | Are system prompt, user prompt templates, and output format specified? |
| Tool definitions | Are all tools defined with schema and purpose? |
| Model selection | Is the model chosen with rationale? Is there a fallback? |
| Token cost estimate | Estimated input/output tokens per run? Frequency? Monthly cost? |
| Cost guardrails | Hard cost cap per run? Max iterations? Per-user rate limit on runs? (Estimates are not limits) |
| Error / fallback handling | What happens on API failure, bad model output, tool error, or runaway loop? |
| Orchestration | Multi-agent: is delegation and handoff logic defined? |
| Data flow | What data enters, transforms, and exits the agent? |
| Security | Prompt injection risks? Tool permission scope? |
| Testing strategy | How is agent behavior validated? Evals defined? |

Output format: same structure as PRD review, adapted to TDD dimensions.

---

## Write Mode Templates

### PRD Template

```markdown
# Product Requirements Document
**Product:** <name>
**Author:** argeoalecha
**Date:** YYYY-MM-DD
**Status:** Draft

---

## 1. Problem Statement
<2–3 sentences: who is affected, what is the problem, why does it matter now>

## 2. Goals
- <measurable goal with target: e.g., "Reduce booking time from 15 min to under 3 min">

## 3. Non-Goals (out of scope)
- <explicit exclusion — what this product will NOT do>

## 4. User Personas
| Persona | Who they are | Primary need |
|---|---|---|
| <name> | <role/context> | <what they need from this product> |

## 5. User Stories / Requirements

### Must Have (MVP)
- [ ] As a <persona>, I can <action> so that <benefit>

### Should Have (V1+)
- [ ] ...

### Nice to Have (future)
- [ ] ...

## 6. Success Metrics
| Metric | Target | How Measured |
|---|---|---|
| <metric> | <value> | <measurement method> |

## 7. Constraints
- **Budget:** <if relevant>
- **Timeline:** <if relevant>
- **Technical:** <known limitations>
- **Scale:** <expected users / requests at launch and at 6 months — sizes /load-test thresholds and the TDD rendering/caching strategy>
- **Regulatory:** Philippines DPA (RA 10173) — <required / not required>

## 8. Open Questions
- <question that must be answered before building begins>
```

---

### TDD Template — Web App

```markdown
# Technical Design Document
**Feature/System:** <name>
**Author:** argeoalecha
**Date:** YYYY-MM-DD
**Status:** Draft
**Related PRD:** [link or "see PRD above"]

---

## 1. Overview
<2–3 sentences: what this builds technically and the key design approach>

## 2. Architecture

### System Diagram
<ASCII diagram or component interaction description>

### Tech Stack
| Layer | Technology | Why |
|---|---|---|
| Frontend | <e.g. Next.js 16 App Router + TypeScript> | <reason — Next 16: Turbopack is the default bundler, Node.js 20+ required, `middleware.ts` deprecated in favor of `proxy.ts`> |
| Styling | <e.g. Tailwind CSS v4 + shadcn/ui> | <reason — Tailwind v4 is CSS-first (`@theme` in globals.css); `tailwind.config.js` is optional, not required by default> |
| Theme | <Hayah variant: classic / midnight / coral / editorial / bento / console> | <fit for audience/mood — drives /company-site + /ui-builder> |
| Backend | <e.g. Next.js API Routes / Express> | <reason> |
| Database | <e.g. Supabase PostgreSQL> | <reason> |
| Auth | <e.g. Supabase Auth via `@supabase/ssr`> | <reason — `@supabase/auth-helpers-nextjs` is deprecated; `@supabase/ssr`'s `createBrowserClient`/`createServerClient` is the current path> |
| Deployment | <e.g. Vercel> | <reason> |

## 3. Database Schema

### Tables

#### `<table_name>`
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PRIMARY KEY DEFAULT gen_random_uuid() | |
| user_id | UUID | NOT NULL REFERENCES auth.users(id) | |
| <column> | <type> | <constraints> | <description> |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | | Soft delete |

### RLS Policies
```sql
-- Users see only their own rows
CREATE POLICY "<table>_own" ON <table>
  USING (auth.uid() = user_id);
```

## 4. API Design

### Endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/<resource> | Required | List |
| POST | /api/<resource> | Required | Create |
| GET | /api/<resource>/[id] | Required | Get single |
| PATCH | /api/<resource>/[id] | Required | Update |
| DELETE | /api/<resource>/[id] | Required | Soft delete |

### Request/Response Shapes

#### POST /api/<resource>
```typescript
interface CreateRequest {
  name: string
}

// 201 Created
interface ResourceResponse {
  id: string
  name: string
  created_at: string
}

// 4xx/5xx
interface ErrorResponse {
  error: string
  code?: string
}
```

## 5. Frontend Structure

```
app/
├── (auth)/login/page.tsx
├── dashboard/
│   ├── layout.tsx
│   └── page.tsx
└── api/<resource>/route.ts
components/<feature>/
lib/supabase/
lib/validations/
```

## 6. Key Technical Decisions
| Decision | Choice | Rationale | Trade-off |
|---|---|---|---|
| <decision> | <choice> | <why> | <what was given up> |

## 7. Security Considerations
- Auth: <how auth is enforced at the route level — if via `proxy.ts` (Next.js 16's renamed `middleware.ts`), note that it runs on the Node.js runtime only; edge is no longer supported there>
- RLS: <which tables have RLS and the policy logic>
- Input validation: Zod schemas on all API inputs
- Security headers: CSP allowlist derived from the third-party origins THIS design uses (Supabase, Turnstile, analytics — list them), plus HSTS, X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy. Planned here = ships in `next.config.ts` headers() from day one, not flagged 3 audits in a row.
- Rate limiting: <which public endpoints, limit + window, store (e.g. Upstash sliding window 5/10m)>
- PII: <what personal data is handled and how>
- Philippines DPA: <consent mechanism, data rights endpoints — or "not applicable">

## 8. Performance & Delivery
### Rendering strategy (per route)
| Route | Mode (Static / ISR / Dynamic) | Why |
|---|---|---|
| / | Static | marketing |
| /dashboard | Dynamic | per-user data |

Anything `ƒ (Dynamic)` needs a stated reason (`cookies()`, auth, personalization). `proxy.ts` (Next.js 16's renamed `middleware.ts`) `matcher` scoped so it never force-dynamics static routes or assets.

### Budgets (enforced later by /web-perf-audit — set targets now)
- Total JS <300KB raw, largest chunk <150KB, First Load JS <200KB/route
- Fonts: ≤2 typefaces × ≤2 weights via `next/font` latin subset, <60KB total
- TTFB: <200ms warm, no cold sample >600ms
- Memoization: state whether `reactCompiler: true` (Next.js 16, React Compiler — stable but opt-in) is enabled; if not, expensive components still need manual `React.memo`/`useMemo`/`useCallback`

### CDN & data caching
- Hashed assets: `immutable, max-age=31536000`
- HTML (static routes): `s-maxage` + `stale-while-revalidate` + platform CDN header (Vercel-CDN-Cache-Control / Netlify-CDN-Cache-Control durable)
- Data caching: <what is cached and TTL>
- Pagination: <cursor-based / offset, page size>
- N+1 avoidance: <join strategy>

## 9. Testing Strategy
- Unit tests: <what is unit tested, e.g. validation logic, utilities>
- Integration tests: <e.g. API routes against real DB>
- E2E tests: <critical user journeys — Playwright>. Every Must-Have (MVP) user story gets at least one feature-tier test (completes a real workflow — smoke tests don't count toward coverage)
- Accessibility: keyboard navigation, labels/alt text, WCAG 2.2 AA contrast (4.5:1 normal / 3:1 large — unchanged from 2.1) plus 2.2's newer criteria where relevant (24×24px min target size, focus not obscured by sticky headers) — planned per component, not retrofitted after /audit flags it

## 10. Deployment & Operations
- Environment: Vercel (preview + production)
- Domain & DNS: <registrar, DNS provider, apex + www both resolving to one canonical>. If DNS is on Cloudflare with a Vercel/Netlify host: records gray-clouded (DNS-only) — orange-cloud creates a double-proxy (observed 3+ seconds added TTFB)
- Migrations: `supabase db push` before app deploy; rollback plan (reversal SQL or documented restore path) per migration
- Monitoring: Sentry (`instrumentation-client.ts` + `sentry.server.config.ts`/`sentry.edge.config.ts` + root `instrumentation.ts` exporting `onRequestError` — current Next.js SDK layout), `/api/health` endpoint, structured logging (request id, user id, duration)
- Backups: <Supabase PITR (Pro/Team/Enterprise add-on, requires ≥Small compute add-on, replaces daily backups rather than supplementing them) / schedule, restore tested when>
- CI: typecheck + lint + tests + build on every PR; branch protection on main
- Required env vars: `<VAR_NAME>`, `<VAR_NAME>` — placeholders in `.env.example`, set per environment in platform dashboard

## 11. Open Questions
- <technical decision that needs resolution before implementation>
```

---

### TDD Template — AI / Agent

```markdown
# Technical Design Document — AI Agent / Automation
**System:** <name>
**Author:** argeoalecha
**Date:** YYYY-MM-DD
**Status:** Draft
**Related PRD:** [link or "see PRD above"]

---

## 1. Overview
<2–3 sentences: what this agent does, how it's triggered, and what it produces>

## 2. Agent Flow

```
[Trigger] → [Input parsing] → [Decision / routing] → [Tool calls] → [Output generation] → [Delivery]
```

<Narrative description of each step: what data flows in/out, what decisions are made>

## 3. Model Configuration
| Parameter | Value | Rationale |
|---|---|---|
| Model | claude-sonnet-5 | <reason — or justify using claude-opus-4-8 (harder reasoning), claude-haiku-4-5 (high-volume/low-latency), or claude-fable-5> |
| Max tokens | <value> | <expected output size> |
| Temperature | <value> | <deterministic vs. creative> |
| Caching | <yes/no — which prompt parts> | <cost/latency reason> |
| Fallback model | <model or "none"> | <if primary fails> |

## 4. Prompt Design

### System Prompt
```
<system prompt content or description of what it contains>
```

### User Prompt Template
```
<template with {{variable}} placeholders>
```

### Output Format
<How the model is instructed to format output: JSON schema, markdown, plain text, structured fields>

## 5. Tools / Functions
| Tool name | Purpose | Input schema | Output |
|---|---|---|---|
| <tool_name> | <what it does> | `{ field: type }` | <what it returns> |

## 6. Multi-Agent Orchestration (if applicable)
| Agent | Role | Triggered by | Hands off to |
|---|---|---|---|
| <agent> | <role> | <trigger> | <next agent or output> |

## 7. Token Cost Estimate
| Item | Tokens | Notes |
|---|---|---|
| System prompt | ~<N> | Cached after first call |
| User prompt (avg) | ~<N> | Per run |
| Tool results (avg) | ~<N> | Per run |
| Output (avg) | ~<N> | Per run |
| **Total per run** | ~<N> | |
| **Est. monthly cost** | $<X> | At <N> runs/day |

### Cost guardrails (hard limits, not estimates)
- Max cost per run: $<X> — agent self-aborts beyond this
- Max iterations per agent loop: <N>
- Per-user rate limit on agent runs: <N per period>

## 8. Error & Fallback Handling
| Failure mode | Behavior |
|---|---|
| Claude API error | <retry logic / fallback / notify> |
| Bad model output (parse failure) | <retry with stricter prompt / default value / escalate> |
| Tool call failure | <retry / skip / abort run> |
| Timeout | <max wait, then fallback> |
| Runaway loop | Abort at max iterations / max cost per run (see §7 guardrails) — never unbounded |

## 9. Data Flow & Storage
- **Input source**: <where data comes from — DB, webhook, user input>
- **Output destination**: <DB table, file, API call, notification>
- **PII handled**: <yes/no — what fields, how stored>
- **Retention**: <how long data is kept>

## 10. Security Considerations
- Prompt injection: <mitigations — input sanitization, output validation>
- Tool permission scope: <least-privilege — what each tool can access>
- API key handling: env vars only, never in prompts or logs
- Philippines DPA: <consent / data rights — or "not applicable">

## 11. Testing Strategy
- Unit: <test individual tools and parsing logic with mocked model responses>
- Evals: <define golden set of input/output pairs for regression testing>
- Integration: <run agent end-to-end in staging with real Claude API>
- Monitoring: <log token usage, latency, error rate per run>

## 12. Deployment
- Runtime: <Vercel function / cron / local script / Supabase Edge Function>
- Trigger: <HTTP endpoint / cron schedule / event webhook>
- Required env vars: `ANTHROPIC_API_KEY`, `<other vars>`

## 13. Open Questions
- <unresolved technical decision — model choice, tool scope, output format>
```

---

## Design for the Downstream Gates

Every project specced here later passes through hard gates. A gap found at gate time is a planning failure — the TDD must pre-answer each gate. When drafting or reviewing, walk this table:

| Downstream gate | What it will check | TDD/PRD section that must answer it |
|---|---|---|
| `/audit` Phase 3 | Env/secrets, monitoring, rate limits, security headers, backups, CI | Web TDD §7, §10 |
| `/web-perf-audit` | TTFB, CDN caching, delivered headers, JS/font budgets, DNS double-proxy | Web TDD §8, §10 (Domain & DNS) |
| `/load-test` | p95/p99 vs. expected traffic, cost cap on AI endpoints | PRD §7 Scale + Web TDD §8; AI TDD §7 guardrails |
| `/ux-review` | Loading/error/empty states, PH mobile resilience | Web TDD §9 + PRD personas |
| `/ph-dpa-compliance` | Consent, data rights endpoints, PII minimization | PRD §7 Regulatory + TDD security sections |
| `/e2e-test` / `/e2e-playwright` | Feature-tier coverage of every MVP story | Web TDD §9 + PRD §5 Must-Haves |

If a TDD section can't answer its gate yet, that's an Open Question (§11/§13) — never silence.

---

## Philippines Market Notes

When the project targets the Philippines market, add to PRD constraints and TDD:
- Currency: Philippine Peso (₱), format as `₱1,234.00`
- Address structure: Barangay → Municipality → Province → Region
- Primary payments: COD, GCash, Maya, bank transfer
- DPA compliance required (RA 10173) — add consent mechanism and data rights endpoints
- Optimize for mobile-first, slower connections — JS weight is the lever: ~600KB raw JS ≈ 2–4s parse+execute on mid-range Android over 4G (budgets in Web TDD §8)
