---
name: load-test
description: Run load, stress, soak, and spike tests against a deployed application using k6. Generates k6 scripts from the project's routes, executes against a target URL, measures p50/p95/p99 latency and error rate against thresholds, then writes findings to LOADTEST.md and appends remediation tasks to TODO.md. Adapts to project type — web app HTTP load tests vs. AI agent endpoints (with token cost tracking and hard cost cap). Use when the user says "load test", "stress test", "performance test", "can it handle traffic", "find the breakpoint", "soak test", "spike test", "test scaling", or as a follow-up after /audit at pre-launch or pre-scale stage. Requires explicit confirmation before testing any production URL.
---

# Load Test Skill — k6 Performance Gate

Runs scripted load tests against a deployed application, measures performance against thresholds, and produces an actionable report. Designed to be invoked by `/audit` Recommended Follow-ups at Stage B (pre-launch) and Stage D (pre-scale), or directly by the user.

---

## Workflow Summary

```
Phase 0 — Pre-flight        (k6 installed, target URL, prod safety check)   HARD STOP
Phase 1 — Project Type      (web app / AI-agent — determines scenarios)
Phase 2 — Scenario Gen      (auto-generate k6 script from detected routes)
Phase 3 — Smoke Test        (1 user, 1 min — sanity check)                  HARD STOP
Phase 4 — Main Test         (load / stress / soak / spike per mode)
Phase 5 — Analysis          (compare results vs. thresholds)
Phase 6 — TODO Writeback    (append findings to TODO.md)
Phase 7 — Recommendations   (next test, remediation, /feature-dev handoff)
```

---

## Test Modes

```
Smoke     — 1 VU, 1 minute             baseline sanity check
Load      — projected peak traffic     "can it handle launch day?"
Stress    — ramp until breakpoint      "where does it fail?"
Soak      — sustained load 30+ min     find memory leaks, conn pool exhaustion
Spike     — sudden surge then drop     test autoscaling / queue handling
```

Default mode if user just says "load test": **Load**.

---

## Phase 0 — Pre-flight (Hard Stop)

```bash
# 1. k6 installed?
command -v k6 >/dev/null 2>&1 || echo "k6 not installed"

# 2. Target URL provided?
# User must specify or skill auto-detects from VERCEL_URL / vercel project / package.json scripts
```

### Install k6 if missing

```bash
brew install k6                        # macOS (this user is on Darwin)
# Or: https://grafana.com/docs/k6/latest/set-up/install-k6/
```

### Production URL safety check

If the target URL points to:
- A custom domain configured as production
- Vercel `production` deployment URL
- Any URL the user explicitly tags as production

**Halt and require explicit confirmation in this exact form:**

```
This will generate <N> requests/second against PRODUCTION at <URL>.

Risks:
  - Real users may experience degraded service during the test
  - Database connection pool may saturate
  - You may incur infrastructure costs (Vercel function invocations, Supabase, Claude API tokens)
  - Rate limits may trip and lock out real traffic

Type the production URL exactly to confirm: <URL>
```

Default target should be a preview/staging URL. Production tests require this explicit ceremony.

---

## Phase 1 — Project Type Detection

| Type | Signals | Test approach |
|---|---|---|
| **Web App** | Next.js, Express, public HTTP routes | HTTP load against representative routes |
| **AI / Agent** | imports `@anthropic-ai/sdk`, agent endpoints | HTTP load against agent route + token cost tracking + cost cap |
| **Hybrid** | Both | Web app routes + agent routes tested separately |

For AI/Agent projects, **a hard cost cap is mandatory** before Phase 4. See "AI/Agent Cost Cap" below.

---

## Phase 2 — Scenario Generation

Auto-generate a k6 script based on detected routes. Save to `.loadtest/<mode>.js` at the project root.

### Detect routes

```bash
# Next.js App Router
find app -name "route.ts" -o -name "route.tsx" 2>/dev/null

# Next.js Pages Router
find pages/api -name "*.ts" 2>/dev/null

# Express / Fastify
grep -rE "(app|router)\.(get|post|put|patch|delete)\(" --include="*.ts" --include="*.js" -l
```

### Web App k6 Script Template

```javascript
// .loadtest/load.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency', true);

export const options = {
  stages: [
    { duration: '1m', target: 20 },     // ramp up
    { duration: '3m', target: 50 },     // sustain projected peak
    { duration: '1m', target: 0 },      // ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1500'],   // ms
    'http_req_failed': ['rate<0.01'],                   // <1% errors
    'errors': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.TARGET_URL;

export default function () {
  // GET — list endpoint
  const list = http.get(`${BASE_URL}/api/<resource>`);
  apiLatency.add(list.timings.duration);
  errorRate.add(list.status !== 200);
  check(list, { 'list 200': (r) => r.status === 200 });

  sleep(1);

  // POST — create endpoint (auth required — set TOKEN env var)
  const created = http.post(
    `${BASE_URL}/api/<resource>`,
    JSON.stringify({ name: `loadtest-${__VU}-${__ITER}` }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${__ENV.TOKEN}`,
      },
    }
  );
  errorRate.add(created.status !== 201);
  check(created, { 'create 201': (r) => r.status === 201 });

  sleep(2);
}
```

### AI/Agent k6 Script Template

```javascript
// .loadtest/agent-load.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const errorRate = new Rate('agent_errors');
const agentLatency = new Trend('agent_latency', true);
const tokensUsed = new Counter('total_tokens');
const estimatedCost = new Counter('estimated_cost_cents');

export const options = {
  scenarios: {
    agent_load: {
      executor: 'constant-arrival-rate',
      rate: 5,                          // 5 requests per second
      timeUnit: '1s',
      duration: '3m',
      preAllocatedVUs: 10,
      maxVUs: 30,
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<8000', 'p(99)<15000'],   // ms — agents are slow
    'http_req_failed': ['rate<0.005'],                    // <0.5% errors
    'agent_errors': ['rate<0.005'],
    'estimated_cost_cents': [`count<${__ENV.COST_CAP_CENTS || 100}`],  // hard cap
  },
};

const BASE_URL = __ENV.TARGET_URL;
const PROMPTS = [
  'Summarize the benefits of mobile money in the Philippines.',
  'Plan a 3-day Cebu itinerary.',
  // ... representative prompts
];

export default function () {
  const prompt = PROMPTS[Math.floor(Math.random() * PROMPTS.length)];
  const res = http.post(
    `${BASE_URL}/api/agent`,
    JSON.stringify({ prompt }),
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${__ENV.TOKEN}`,
      },
      timeout: '60s',
    }
  );

  agentLatency.add(res.timings.duration);
  errorRate.add(res.status !== 200);

  if (res.status === 200) {
    const body = res.json();
    if (body.usage) {
      const inputTokens = body.usage.input_tokens || 0;
      const outputTokens = body.usage.output_tokens || 0;
      tokensUsed.add(inputTokens + outputTokens);
      // Sonnet 4.6 pricing: $3/M input, $15/M output → cents
      const cents = (inputTokens * 0.0003 + outputTokens * 0.0015);
      estimatedCost.add(cents);
    }
  }

  check(res, { 'agent 200': (r) => r.status === 200 });
  sleep(1);
}
```

---

## AI/Agent Cost Cap (Mandatory)

Before running Phase 4 against AI/agent endpoints, calculate and confirm the cost cap with the user.

### Estimation formula

```
Cost cap = duration_seconds × RPS × avg_tokens_per_request × price_per_token
```

Example:
- 3-minute test × 5 RPS × ~3000 tokens avg × Sonnet 4.6 pricing
- = 180 × 5 × 3000 = 2.7M tokens
- = ~$8.10 estimated

Surface to user:
```
This AI agent load test will execute approximately N requests, consuming
~M tokens, costing an estimated $X.XX at current Sonnet 4.6 pricing.

Hard cost cap (will abort test if exceeded): $Y.YY

Type "yes" to proceed, or specify a lower cap.
```

The k6 script enforces the cap via the `estimated_cost_cents` threshold — k6 will abort if exceeded.

---

## Phase 3 — Smoke Test (Hard Stop)

Always run smoke first. If it fails, do not proceed to main test.

```bash
TARGET_URL=<staging-url> TOKEN=<auth-token> k6 run --vus 1 --duration 1m .loadtest/load.js
```

Pass criteria for smoke:
- All checks pass
- Zero 5xx errors
- p95 < threshold

If smoke fails: report the failure, do not proceed. The app is broken at 1 VU — load testing is meaningless.

---

## Phase 4 — Main Test

```bash
TARGET_URL=<url> TOKEN=<token> COST_CAP_CENTS=<cap> k6 run .loadtest/<mode>.js \
  --summary-export=.loadtest/results-<mode>-<timestamp>.json
```

Modes adjust the `options.stages` or `options.scenarios` block:

**Load** (default):
- Ramp 1m → 20 VUs, sustain 3m at projected peak, ramp down 1m

**Stress**:
- Ramp 1m → 50 VUs, ramp 2m → 100 VUs, ramp 2m → 200 VUs, hold 2m
- Stop when error rate > 5% or p95 > 5s

**Soak**:
- 30 min sustained at 50% of projected peak
- Watch for memory leaks, connection pool exhaustion

**Spike**:
- 30s baseline (10 VUs) → 30s spike (200 VUs) → 30s baseline (10 VUs)
- Tests autoscaling and recovery

---

## Phase 5 — Analysis

Read `.loadtest/results-<mode>-<timestamp>.json` and compare against thresholds.

### Findings categorization

- **CRITICAL** — Smoke failed, error rate > 5%, p99 > 10× p50, cost cap exceeded
- **HIGH** — p95 above threshold, error rate 1–5%, breakpoint below 2× projected peak
- **MEDIUM** — p95 within threshold but trending up, p99 high, slow endpoints identified
- **LOW** — Headroom observations, optimization opportunities

### Bottleneck attribution

For each finding, attempt to attribute the bottleneck:
- HTTP 504 / timeout → server-side processing or downstream API
- HTTP 502 / 503 → infrastructure (Vercel function timeout, cold start, region)
- HTTP 429 → rate limiting (verify it's the *intended* limit)
- HTTP 5xx in clusters → DB connection pool, deadlock
- High p99 with low p50 → tail latency (cold starts, GC, slow query path)
- AI agent timeouts → Claude API rate limit, model overload

---

## Phase 6 — TODO Writeback (Auto)

Append findings to `TODO.md` as a Performance Remediation phase. Always runs.

```markdown
## Phase X: Performance Remediation (YYYY-MM-DD)
Source: LOADTEST.md (this run)
Mode: load | stress | soak | spike
Target: <URL>
Verdict: <PASS / FAIL — see thresholds>

### Critical
- [ ] [LOAD] /api/agent timed out at >50 RPS — verify Claude API rate limit headroom
- [ ] [LOAD] DB connection pool exhausted at 80 VUs — increase pool size or add pgbouncer

### High
- [ ] [LOAD] p95 of /api/trips at 850ms (target 500ms) — investigate query plan
- [ ] [LOAD] Cold start adds ~2s to first request per region — pre-warm or use Edge

### Medium / Low
- [ ] [LOAD] p99 trending up over 30min soak — possible memory leak in <route>
```

Rules:
- Insert as new top-level Phase, numbered after highest existing phase
- Preserve existing TODO content unchanged
- Do not duplicate items (same `[LOAD] description — endpoint`)
- If running in re-test mode after fixes, mark resolved items with `~~strikethrough~~ (resolved YYYY-MM-DD)`

---

## Phase 7 — Recommendations

After analysis, output:

```
Next action: <single concrete remediation>
Skill: /feature-dev <on remediation TODO> | /db-migrate <if DB tuning> | /audit <re-audit after fix>

Suggested follow-up tests:
- <e.g. "Re-run /load-test stress after DB pool increase">
- <e.g. "Run /load-test soak for 1hr to verify no leak">
```

---

## Output: LOADTEST.md

Write to project root.

```markdown
# Load Test Report
Date: YYYY-MM-DD HH:MM PHT
Mode: load | stress | soak | spike
Target: <URL>
Project type: <Web App / AI Agent / Hybrid>
Tool: k6 v<version>

## Configuration
- VUs: <range>
- Duration: <total>
- Scenario file: `.loadtest/<mode>.js`
- Cost cap (AI only): $<value>

## Thresholds
| Metric | Target | Actual | Status |
|---|---|---|---|
| p95 latency | <500ms | <Nms> | PASS / FAIL |
| p99 latency | <1500ms | <Nms> | PASS / FAIL |
| Error rate | <1% | <N%> | PASS / FAIL |
| AI cost cap | <$X> | <$Y> | PASS / FAIL |

## Findings

### Critical
- <description> — endpoint, evidence (latency, error code)

### High
- ...

### Medium / Low
- ...

## Per-Endpoint Latency
| Endpoint | RPS | p50 | p95 | p99 | error % |
|---|---|---|---|---|---|
| GET /api/trips | <N> | <ms> | <ms> | <ms> | <%> |

## Bottleneck Attribution
- <observation linking finding to root cause>

## Verdict
PASS / FAIL vs. configured thresholds.

## TODO Writeback
Appended N items to TODO.md under "Phase X: Performance Remediation (YYYY-MM-DD)"

## Suggested Next Test
<re-run mode | new mode | retest after fix>
```

---

## Integration Points

- **Triggered by `/audit`** — Recommended Follow-ups at Stage B (pre-launch) and Stage D (pre-scale)
- **Pre-flight: `/web-perf-audit` first** — load-testing a site with broken CDN caching measures the origin, not the real user path. If `/web-perf-audit` shows bimodal TTFB or cold-cache markers (`fwd=miss`, `x-vercel-cache: MISS`), fix caching before burning k6 compute. Its 5-sample curl diagnosis also explains "high p99 / low p50" results in 30 seconds.
- **Feeds `/feature-dev`** — Performance Remediation TODO items become feature-dev inputs
- **Re-test cycle** — After fixes, run `/load-test` again in re-test mode to mark items resolved
- **Vercel preview URLs** — Default target. Find via `vercel ls` or `VERCEL_URL` env var
- **Cost guardrail for AI** — Always enforced; the test self-aborts if exceeded

---

## Rules

- **Never run against production without explicit URL-typing confirmation**
- **Always run smoke (Phase 3) first** — even in re-test mode
- **AI/agent tests require an explicit cost cap** — no exceptions
- **Default target is preview/staging URL**, not production
- **Save every k6 script** to `.loadtest/` — versioned in git so reruns are reproducible
- **Save every result** to `.loadtest/results-<mode>-<timestamp>.json` — for trend analysis
- **TODO writeback always runs** — same closure-loop principle as `/audit`
- **Halt on smoke failure** — do not waste compute or money load-testing a broken endpoint

---

## Out of Scope

- Real-user monitoring (RUM) — needs production traffic + analytics tool
- Frontend delivery performance (TTFB, caching, headers, payload weight) — use `/web-perf-audit` (curl-based, works in this sandbox; Lighthouse is not available here)
- Distributed load from multiple regions — k6 Cloud or BlazeMeter; out of scope for solo MVP
- Browser-based load (full page render under load) — k6 browser module; defer until needed
- Chaos / fault injection — separate discipline
