---
name: e2e-playwright
description: "Battle-tested Playwright E2E testing patterns for Next.js/React apps. Use when writing, running, debugging, or fixing Playwright tests. Also triggers on 'e2e', 'end-to-end', 'playwright', 'browser test', 'UI test', 'integration test with browser', 'flaky test', 'test keeps failing'. Covers locators, assertions, fixtures, auth, network mocking, flaky test diagnosis, Next.js-specific patterns, and debugging workflows."
---

# Playwright E2E Testing

> Production-tested patterns from the TestDino Playwright Skill. Every pattern includes when (and when *not*) to use it.

## When to Use This Skill vs `/e2e-test`

| | `/e2e-playwright` (this skill) | `/e2e-test` |
|---|---|---|
| **What it produces** | TypeScript test files committed to the repo | One-time interactive browser session |
| **When to use** | Writing regression tests for a feature, CI test suite | Exploratory validation before code review, one-off UI checks |
| **Runs in CI** | Yes — `npx playwright test` | No — agent-browser CLI only |
| **Output** | `e2e/*.spec.ts` files | `E2E_TEST.md` report + `e2e-screenshots/` |

Use `/e2e-playwright` to write the permanent test suite. Use `/e2e-test` for a quick interactive pass before a PR.

---

## Golden Rules

1. **`getByRole()` over CSS/XPath** — resilient to markup changes, mirrors how users see the page
2. **Never `page.waitForTimeout()`** — use `expect(locator).toBeVisible()` or `page.waitForURL()`
3. **Web-first assertions** — `expect(locator)` auto-retries; `expect(await locator.textContent())` does NOT
4. **Isolate every test** — no shared state, no execution-order dependencies
5. **`baseURL` in config** — zero hardcoded URLs in tests
6. **Retries: `2` in CI, `0` locally** — surface flakiness where it matters
7. **Traces: `'on-first-retry'`** — rich debugging artifacts without CI slowdown
8. **Fixtures over globals** — share state via `test.extend()`, not module-level variables
9. **One behavior per test** — multiple related `expect()` calls are fine
10. **Mock external services only** — never mock your own app; mock third-party APIs, payment gateways, email
11. **No performance assertions in E2E** — timing/CWV/`performance.timing` assertions are a flakiness factory (CI machines vary 5×). Measure performance with `/web-perf-audit` against a deployed URL instead.

**Deep dives available in `references/` directory — read them when working on the relevant topic.**

---

## Feature Tests vs Smoke Tests

Not all E2E tests are equal. Know what tier you're writing.

| Tier | What it tests | Example | Sufficient for feature coverage? |
|------|--------------|---------|----------------------------------|
| **Smoke** | Page loads, no 404, no crash | `goto('/canvas'); expect(heading).toBeVisible()` | **NO** — baseline only |
| **Feature** | User completes a real workflow | Drag entry to project → rule created → future entries auto-link | **YES** — this is the goal |
| **Navigation** | Links route correctly, active states work | Click "Canvas" in sidebar → URL is /canvas → heading visible | **Required when nav changes** |

**The rule:** Every feature shipped MUST have at least one tier-2 (feature) E2E test. Smoke tests are free but DO NOT count toward feature coverage.

**Ask yourself:** "If someone broke this feature tomorrow, would my E2E tests catch it?" If the answer is "only if they deleted the entire page" — you wrote smoke tests, not feature tests.

### Navigation Tests — Required When Nav Changes

When you add or modify navigation (sidebar items, mobile tab bar, header links, route changes), you MUST write tests that verify:

1. Nav item is visible at the correct viewport (desktop sidebar, mobile tab bar)
2. Clicking it navigates to the correct URL
3. Destination page renders its primary content (not just "no 404")
4. Active/selected state highlights correctly

**Desktop + Mobile navigation test template:**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Navigation — Desktop', () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  test('sidebar contains Canvas link and navigates correctly', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.getByRole('navigation');
    const canvasLink = sidebar.getByRole('link', { name: 'Canvas' });
    await expect(canvasLink).toBeVisible();
    await canvasLink.click();
    await page.waitForURL('/canvas');
    await expect(page.getByRole('heading', { name: 'Canvas' })).toBeVisible();
  });
});

test.describe('Navigation — Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('mobile tab bar contains Canvas and navigates correctly', async ({ page }) => {
    await page.goto('/');
    const tabBar = page.getByRole('navigation', { name: /mobile|tab/i });
    const canvasTab = tabBar.getByRole('link', { name: 'Canvas' });
    await expect(canvasTab).toBeVisible();
    await canvasTab.click();
    await page.waitForURL('/canvas');
    await expect(page.getByRole('heading', { name: 'Canvas' })).toBeVisible();
  });
});
```

---

## Config (Next.js — canonical for this workspace)

Based on the most mature config in production across workspace projects:

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,
  reporter: process.env.CI
    ? [['html'], ['junit', { outputFile: 'test-results/junit.xml' }]]
    : 'list',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
  ],

  webServer: {
    command: process.env.CI ? 'npm run build && npm run start' : 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },

  timeout: 30_000,
  expect: { timeout: 10_000 },
  outputDir: 'test-results/',
});
```

**Gitignore additions:**
```
playwright-report/
playwright/.auth/
test-results/
blob-report/
.env*.local
```

**Do NOT gitignore screenshot baselines.** `*.spec.ts-snapshots/` directories MUST be committed — they are the source of truth for visual regression.

---

## Locators — Priority Order

```typescript
page.getByRole('button', { name: 'Submit' })         // 1. Role (ALWAYS preferred)
page.getByLabel('Email address')                      // 2. Label (form fields)
page.getByText('Welcome back')                        // 3. Text (non-interactive content)
page.getByPlaceholder('Search...')                    // 4. Placeholder
page.getByAltText('Company logo')                     // 5. Alt text (images)
page.getByTitle('Close dialog')                       // 6. Title attribute
page.getByTestId('checkout-summary')                  // 7. Test ID (last resort)
page.locator('css=.legacy-widget')                    // 8. CSS/XPath (absolute last resort)
```

**For the full locator decision flowchart, read `references/locators-deep-dive.md`**

---

## Assertions — Web-First vs Non-Retrying

### Web-first (auto-retry) — ALWAYS prefer:

```typescript
await expect(page.getByRole('heading')).toBeVisible();
await expect(page.getByRole('heading')).toHaveText('Dashboard');
await expect(page.getByRole('listitem')).toHaveCount(5);
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByLabel('Name')).toHaveValue('Jane');
await expect(page.getByTestId('card')).toHaveClass(/active/);
await expect(page.getByRole('checkbox')).toBeChecked();
await expect(page.getByRole('dialog')).not.toBeVisible();
```

### Non-retrying — only for already-resolved values:

```typescript
const title = await page.title();
expect(title).toBe('Health Check');

const response = await page.request.get('/api/users');
expect(response.status()).toBe(200);
```

**Critical mistake:** `expect(await locator.textContent()).toBe('x')` resolves once with no retry. Use `await expect(locator).toHaveText('x')` instead.

**ARIA snapshots (Playwright 1.5x+)** — for asserting a whole subtree's accessible structure at once instead of chaining many `getByRole()` assertions:

```typescript
await expect(page.getByRole('navigation')).toMatchAriaSnapshot(`
  - navigation:
    - link "Canvas"
    - link "Settings"
`);
```

Use it for structural checks on a component tree (nav, a data table's header row); still prefer targeted `getByRole()` assertions for single-element behavior — an ARIA snapshot that's too broad becomes as brittle as a DOM snapshot.

---

## Authentication

### Storage state reuse (default pattern):

```typescript
// global-setup.ts
import { chromium, type FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(`${baseURL}/login`);
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');
  await context.storageState({ path: '.auth/user.json' });
  await browser.close();
}
export default globalSetup;
```

Add to `playwright.config.ts`:
```typescript
globalSetup: require.resolve('./global-setup'),
projects: [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'], storageState: '.auth/user.json' },
    dependencies: ['setup'],
  },
],
```

**Add `.auth/` to `.gitignore`** — auth state files contain session tokens.

**For multi-role, API login, and NextAuth patterns, read `references/authentication-deep-dive.md`**

---

## Network Mocking — External Services Only

| Service | Mock? | Why |
|---|---|---|
| Your own API | **Never** | This IS the integration you're testing |
| Stripe / payments | **Always** | Costs money, rate-limited |
| SendGrid / email | **Always** | Side effects, no UI to assert |
| OAuth providers | **Always** | Redirect-heavy, CAPTCHAs |
| Analytics | **Always** | Fire-and-forget, slows tests |

```typescript
// Mock a third-party payment API
await page.route('**/api/create-payment-intent', route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ clientSecret: 'pi_mock_123', amount: 9900 }),
  })
);

// Block analytics
await page.route('**/analytics.example.com/**', route => route.abort());
```

**For HAR recording and advanced patterns, read `references/mocking-deep-dive.md`**

---

## Flaky Test Diagnosis

```
Fails locally with --repeat-each=20?
├── YES → TIMING: missing await, race condition
└── NO → Fails only in CI?
    ├── YES → ENVIRONMENT: viewport, fonts, slower machines
    └── NO → Fails only with other tests?
        ├── YES → ISOLATION: shared state, DB leaks, localStorage
        └── NO → INFRASTRUCTURE: browser crash, OOM
```

```bash
npx playwright test tests/checkout.spec.ts --repeat-each=10   # burn-in
npx playwright test -g "adds item" --workers=1                # isolation check
```

**For the full taxonomy and fix patterns, read `references/flaky-tests-deep-dive.md`**

---

## Debugging

```bash
npx playwright test --ui                           # Interactive UI mode
npx playwright test --headed                       # See browser
npx playwright test --headed --slow-mo=500         # Slow motion
PWDEBUG=1 npx playwright test tests/login.spec.ts  # Step-through inspector
npx playwright show-trace test-results/*/trace.zip # View CI trace
```

**For the full debugging workflow, read `references/debugging-deep-dive.md`**

---

## Common Pitfalls (Top 10)

| # | Pitfall | Fix |
|---|---|---|
| 1 | `page.waitForTimeout()` | Web-first assertion: `expect(locator).toBeVisible()` |
| 2 | Missing `await` | `await` every Playwright call. Enable `no-floating-promises`. |
| 3 | CSS selectors | `getByRole()` > `getByLabel()` > `getByText()` > `getByTestId()` |
| 4 | `isVisible()` return value | `expect(locator).toBeVisible()` (auto-retry) |
| 5 | `expect(await el.textContent())` | `await expect(el).toHaveText(...)` (auto-retry) |
| 6 | Shared state between tests | Fixtures with cleanup, isolated test data |
| 7 | Hardcoded URLs | `baseURL` in config |
| 8 | Mocking own app | Only mock third-party services |
| 9 | Module-level variables | Fixtures via `test.extend()` |
| 10 | No traces in CI | `trace: 'on-first-retry'` in config |

**For all 20 pitfalls with full examples, read `references/common-pitfalls.md`**

---

## Next.js Specific Patterns

```typescript
// Loading states with streaming/suspense
test('loading skeleton during data streaming', async ({ page }) => {
  await page.route('**/api/dashboard/stats', async route => {
    await new Promise(r => setTimeout(r, 2000));
    await route.continue();
  });
  await page.goto('/dashboard');
  await expect(page.getByRole('progressbar')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Stats' })).toBeVisible();
});

// API routes via request fixture
test('API route returns expected data', async ({ request }) => {
  const response = await request.get('/api/users');
  expect(response.ok()).toBe(true);
  const data = await response.json();
  expect(data.users).toHaveLength(3);
});

// Mobile viewport — no horizontal scroll
test('375px viewport has no horizontal scroll', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth
  );
  expect(hasHorizontalOverflow).toBe(false);
});
```

**For middleware, server actions, route groups, and NextAuth, read `references/nextjs-deep-dive.md`**

---

## Reference Files

| File | When to read |
|---|---|
| `locators-deep-dive.md` | Decision flowchart, 12+ element types, frame locators, shadow DOM |
| `authentication-deep-dive.md` | Multi-role, API login, OAuth mocking, NextAuth, MFA |
| `fixtures-deep-dive.md` | Worker-scoped, auto, option, typed fixtures, mergeTests |
| `mocking-deep-dive.md` | HAR recording, conditional mocking, contract validation |
| `common-pitfalls.md` | 20+ pitfalls with BAD/GOOD code examples |
| `nextjs-deep-dive.md` | App Router, middleware/proxy (Next.js 16 rename), server actions, ISR, Auth.js/Better Auth |
| `flaky-tests-deep-dive.md` | 4-category taxonomy, fix patterns, quarantine, prevention |
| `debugging-deep-dive.md` | Systematic workflow, VS Code integration, anti-patterns |
| `visual-regression-deep-dive.md` | `toHaveScreenshot()`, baselines, thresholds, masking |
| `screenshots-and-media-deep-dive.md` | Capture profiles, video, traces, per-iteration debugging |
| `ci-pipeline-deep-dive.md` | GitHub Actions, sharding, artifacts, coverage, Docker Compose |
| `page-object-model-deep-dive.md` | POM vs fixtures vs factory functions, async init |
| `test-data-management-deep-dive.md` | Factory patterns, faker, unique IDs for parallel, DB seeding |
| `clock-and-time-mocking-deep-dive.md` | `page.clock`, countdowns, session timeouts, timezone handling |
| `iframes-and-shadow-dom-deep-dive.md` | `frameLocator()`, cross-origin, shadow DOM, payment widgets |
| `api-testing-deep-dive.md` | `request` fixture, CRUD patterns, auth headers, GraphQL |
| `test-organization-deep-dive.md` | Feature-based structure, tagging, filtering, smoke subsets |
