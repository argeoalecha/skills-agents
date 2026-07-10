---
name: unit-test
description: Write Vitest unit tests for functions, Zod schemas, services, stores, hooks, and component states across any project in the workspace. Owns unit-testing conventions — Supabase client mocking, Claude API mocking, fake timers, React Testing Library patterns — and the boundary of what NOT to unit test (integration and E2E layers own those). Use when the user says "write unit tests", "test this function", "test the schema", "mock supabase in tests", "add test coverage", "set up vitest", or invokes /unit-test. NOT for API-route integration tests or RLS verification (integration-test-engineer agent), NOT for browser tests (/e2e-playwright, /e2e-test).
---

# Vitest Unit Testing

## When to Use This Skill vs the Other Test Layers

| | `/unit-test` (this skill) | integration-test-engineer agent | `/e2e-playwright` | `/e2e-test` |
|---|---|---|---|---|
| **Subject** | One function/module in isolation | API route → DB → response | Full user flow in a real browser | Exploratory browser pass |
| **Dependencies** | All mocked | Real test DB, real auth | Real running app | Real running app + DB |
| **Speed** | Milliseconds | Seconds | Minutes | Interactive |
| **Catches** | Logic bugs, edge cases, schema drift | RLS gaps, contract violations | Broken journeys, regressions | UX issues |

If the behavior under test crosses a network, database, or browser boundary, it is not a unit test — hand it to the next layer.

---

## Setup (skip if the project already has Vitest configured)

Check `package.json` for `vitest` and a `test` script first. If missing:

```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @vitejs/plugin-react jsdom
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'node',
    environmentMatchGlobs: [
      ['**/*.test.tsx', 'jsdom'],
      ['src/components/**', 'jsdom'],
      ['src/hooks/**', 'jsdom'],
    ],
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
});
```

```typescript
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
```

Add to `package.json` scripts: `"test": "vitest run", "test:watch": "vitest"`.

---

## What to Unit Test

Priority order — branchy logic first:

1. **`lib/` and `services/` functions** — pricing, scoring, formatting, transforms, anything with conditionals
2. **Zod schemas** — every schema guarding an API boundary: one valid case, each rejection path
3. **Zustand stores** — actions and derived state, tested as plain functions via `useStore.getState()`
4. **Custom hooks** — via `renderHook` when they hold real logic (not thin wrappers over TanStack Query)
5. **Component states** — loading / error / empty / populated for components with conditional rendering
6. **Market-specific formatting** — ₱ currency (`₱1,234.00`), Asia/Manila dates, barangay → region address assembly

## What NOT to Unit Test

- **API route handlers end-to-end** — integration-test-engineer calls them with real auth and DB
- **RLS policies** — meaningless against a mock; requires a real test database
- **Third-party libraries** — trust Zod, Supabase SDK, TanStack Query internals
- **Trivial code** — re-exports, constants, prop pass-through components, styles
- **Performance** — timing assertions are flaky everywhere; use `/load-test` and `/web-perf-audit`

Do not chase a coverage number. Cover every branch of business logic; skip glue. A meaningful target for `lib/`/`services/` is ~90% branch coverage; for the project overall, whatever that yields.

---

## Golden Rules

1. **Colocate tests** — `src/lib/pricing.ts` → `src/lib/pricing.test.ts`; match the export name
2. **`describe` per function, `it` per behavior** — name the behavior, not the method: `it('rejects amounts below the COD minimum')`
3. **Arrange–act–assert, no branching in tests** — a test with `if` is two tests
4. **Mock at the module boundary with `vi.mock`** — never reach into implementation internals
5. **`vi.useFakeTimers()` for anything time-based** — set an explicit date; never depend on wall-clock or machine timezone (CI is UTC, you are Asia/Manila)
6. **One `expect` theme per test** — multiple asserts on one behavior fine; multiple behaviors, split
7. **Test the contract, not the mock** — if every assertion checks the mock was called, the test proves nothing
8. **Deterministic** — no `Math.random`, `Date.now`, or network without stubbing; failed CI runs must reproduce locally
9. **TypeScript strict in tests too** — no `any`; type mock returns with `satisfies` or the real types

---

## Patterns

### Zod schemas

```typescript
import { describe, it, expect } from 'vitest';
import { CreateListingSchema } from './listing';

describe('CreateListingSchema', () => {
  const valid = { title: 'Bike', priceCentavos: 150000, categoryId: crypto.randomUUID() };

  it('accepts a valid payload', () => {
    expect(CreateListingSchema.safeParse(valid).success).toBe(true);
  });

  it('rejects a non-positive price', () => {
    const result = CreateListingSchema.safeParse({ ...valid, priceCentavos: 0 });
    expect(result.success).toBe(false);
  });
});
```

Cover: valid case, each field's rejection, coercion/defaults, `.transform()` output shape.

### Supabase client mock

Mock the factory module, not `@supabase/supabase-js`. The query builder chains, so each method returns the mock itself and the awaited terminal resolves the data:

```typescript
import { vi } from 'vitest';

const mockQuery = {
  select: vi.fn().mockReturnThis(),
  eq: vi.fn().mockReturnThis(),
  is: vi.fn().mockReturnThis(),
  order: vi.fn().mockReturnThis(),
  single: vi.fn().mockResolvedValue({ data: { id: 'abc' }, error: null }),
};

vi.mock('@/lib/supabase/server', () => ({
  createServerClient: vi.fn().mockResolvedValue({
    from: vi.fn(() => mockQuery),
    auth: { getUser: vi.fn().mockResolvedValue({ data: { user: { id: 'user-1' } }, error: null }) },
  }),
}));
```

Assert on what the function *returns* given that data — not on the chain calls. If you find yourself asserting `mockQuery.eq` was called with the right args, the logic worth testing lives in SQL/RLS — hand it to integration-test-engineer.

### Claude API mock

```typescript
vi.mock('@anthropic-ai/sdk', () => ({
  default: vi.fn(() => ({
    messages: {
      create: vi.fn().mockResolvedValue({
        content: [{ type: 'text', text: '{"category":"electronics"}' }],
        usage: { input_tokens: 100, output_tokens: 20 },
      }),
    },
  })),
}));
```

Test your parsing/fallback logic around the response — malformed JSON from the model, empty content, refusals — not the SDK.

### Zustand store

```typescript
import { useCartStore } from './cart-store';

beforeEach(() => useCartStore.setState(useCartStore.getInitialState()));

it('increments quantity for an existing item instead of duplicating', () => {
  useCartStore.getState().addItem({ id: 'p1', priceCentavos: 5000 });
  useCartStore.getState().addItem({ id: 'p1', priceCentavos: 5000 });
  expect(useCartStore.getState().items).toHaveLength(1);
  expect(useCartStore.getState().items[0].quantity).toBe(2);
});
```

### Component states (RTL)

```typescript
import { render, screen } from '@testing-library/react';

it('shows the empty state when there are no listings', () => {
  render(<ListingGrid listings={[]} />);
  expect(screen.getByText(/no listings yet/i)).toBeInTheDocument();
});
```

Query by role/text as a user would (`getByRole`, `getByLabelText`) — never by class or test-id unless there is no accessible handle (then fix the accessibility first).

### Time and currency

```typescript
beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2026-07-10T08:00:00+08:00'));
});
afterEach(() => vi.useRealTimers());

it('formats centavos as Philippine peso', () => {
  expect(formatPeso(123400)).toBe('₱1,234.00');
});
```

---

## Process

1. Read the module under test and its callers — understand the contract before writing a test
2. List behaviors: happy path, each branch, boundary values, error paths
3. Write tests colocated with the module, following the patterns above
4. Run `pnpm test` — all green, no skipped tests left behind
5. Hand off: integration-test-engineer covers the API/RLS layer, `/e2e-playwright` the browser layer, then `/audit` before deploy

## Where This Skill Sits in the Pipeline

Called from `/feature-dev` Phase 4 (testing), from team-orchestrator's test + review phase, and standalone whenever logic changes. Run it before `/code-review` and `/audit` — reviewers should see failing logic caught by tests, not find it themselves.
