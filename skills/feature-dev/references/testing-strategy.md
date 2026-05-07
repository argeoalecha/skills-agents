# Testing Strategy for TripIntell Features

Comprehensive testing approach for different types of features in the TripIntell stack.

## Testing Pyramid

```
          /\
         /  \    E2E Tests (Few)
        /----\   - Critical user flows
       /      \  - Complete scenarios
      /--------\
     /          \ Integration Tests (Some)
    /------------\ - API routes
   /              \ - Database operations
  /----------------\
 /                  \ Unit Tests (Many)
/--------------------\ - Utilities
                       - Business logic
                       - Components
```

## Unit Tests (Vitest)

### What to Unit Test

- Pure functions (utilities, helpers, transformers)
- Business logic (validators, calculators, formatters)
- React components (in isolation)
- Hooks (custom React hooks)
- Zod schemas (validation logic)

### Unit Test Patterns

**Utility Function Tests:**

```typescript
// src/lib/utils.test.ts
import { describe, it, expect } from 'vitest';
import { formatCurrency, calculateDaysDifference } from './utils';

describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });

  it('formats PHP correctly', () => {
    expect(formatCurrency(1234.56, 'PHP')).toBe('₱1,234.56');
  });

  it('handles zero', () => {
    expect(formatCurrency(0, 'USD')).toBe('$0.00');
  });

  it('handles negative amounts', () => {
    expect(formatCurrency(-100, 'USD')).toBe('-$100.00');
  });
});

describe('calculateDaysDifference', () => {
  it('calculates days between dates', () => {
    const start = new Date('2024-01-01');
    const end = new Date('2024-01-05');
    expect(calculateDaysDifference(start, end)).toBe(4);
  });

  it('returns 0 for same date', () => {
    const date = new Date('2024-01-01');
    expect(calculateDaysDifference(date, date)).toBe(0);
  });
});
```

**Zod Schema Tests:**

```typescript
// src/schemas/itinerary.test.ts
import { describe, it, expect } from 'vitest';
import { ItineraryPreferencesSchema } from './itinerary';

describe('ItineraryPreferencesSchema', () => {
  it('accepts valid preferences', () => {
    const valid = {
      destination: 'Paris, France',
      duration: 5,
      budget: 'moderate',
      interests: ['culture', 'food'],
    };

    expect(() => ItineraryPreferencesSchema.parse(valid)).not.toThrow();
  });

  it('rejects invalid budget tier', () => {
    const invalid = {
      destination: 'Paris',
      duration: 5,
      budget: 'invalid',
      interests: [],
    };

    expect(() => ItineraryPreferencesSchema.parse(invalid)).toThrow();
  });

  it('enforces minimum duration', () => {
    const invalid = {
      destination: 'Paris',
      duration: 0,
      budget: 'moderate',
      interests: [],
    };

    expect(() => ItineraryPreferencesSchema.parse(invalid)).toThrow();
  });
});
```

**React Component Tests:**

```typescript
// src/components/itinerary-card.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ItineraryCard } from './itinerary-card';

describe('ItineraryCard', () => {
  const mockItinerary = {
    id: '123',
    destination: 'Paris, France',
    duration: 5,
    created_at: '2024-01-01',
  };

  it('renders itinerary details', () => {
    render(<ItineraryCard itinerary={mockItinerary} />);

    expect(screen.getByText('Paris, France')).toBeInTheDocument();
    expect(screen.getByText('5 days')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<ItineraryCard itinerary={mockItinerary} loading />);

    expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
  });
});
```

**Custom Hook Tests:**

```typescript
// src/hooks/use-itinerary.test.ts
import { describe, it, expect } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useItinerary } from './use-itinerary';

describe('useItinerary', () => {
  it('fetches itinerary on mount', async () => {
    const { result } = renderHook(() => useItinerary('123'));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.itinerary).toBeDefined();
    });
  });

  it('handles fetch errors', async () => {
    const { result } = renderHook(() => useItinerary('invalid'));

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
  });
});
```

## Integration Tests

### What to Integration Test

- API routes (request → response flow)
- Database operations (Supabase queries)
- External API integrations (Claude, Google Maps, Stripe)
- Multi-layer operations (frontend → API → database)

### API Route Integration Tests

```typescript
// src/app/api/itineraries/route.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { POST } from './route';
import { createServerClient } from '@/lib/supabase/server';

describe('POST /api/itineraries', () => {
  let supabase: any;
  let testUserId: string;

  beforeEach(async () => {
    supabase = await createServerClient();
    // Create test user
    const { data } = await supabase.auth.signUp({
      email: 'test@example.com',
      password: 'password',
    });
    testUserId = data.user.id;
  });

  afterEach(async () => {
    // Cleanup
    await supabase.from('itineraries').delete().eq('user_id', testUserId);
    await supabase.auth.admin.deleteUser(testUserId);
  });

  it('creates an itinerary', async () => {
    const request = new Request('http://localhost:3000/api/itineraries', {
      method: 'POST',
      body: JSON.stringify({
        destination: 'Paris, France',
        duration: 5,
        budget: 'moderate',
      }),
    });

    const response = await POST(request);
    expect(response.status).toBe(201);

    const data = await response.json();
    expect(data.id).toBeDefined();
    expect(data.destination).toBe('Paris, France');
  });

  it('validates required fields', async () => {
    const request = new Request('http://localhost:3000/api/itineraries', {
      method: 'POST',
      body: JSON.stringify({}),
    });

    const response = await POST(request);
    expect(response.status).toBe(400);

    const data = await response.json();
    expect(data.code).toBe('VALIDATION_ERROR');
  });

  it('requires authentication', async () => {
    // Sign out
    await supabase.auth.signOut();

    const request = new Request('http://localhost:3000/api/itineraries', {
      method: 'POST',
      body: JSON.stringify({
        destination: 'Paris',
        duration: 5,
        budget: 'moderate',
      }),
    });

    const response = await POST(request);
    expect(response.status).toBe(401);
  });
});
```

### Database Integration Tests

```typescript
// src/lib/database/itinerary-repository.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { ItineraryRepository } from './itinerary-repository';
import { createServerClient } from '@/lib/supabase/server';

describe('ItineraryRepository', () => {
  let repository: ItineraryRepository;
  let testUserId: string;

  beforeEach(async () => {
    const supabase = await createServerClient();
    repository = new ItineraryRepository(supabase);

    // Setup test user
    const { data } = await supabase.auth.signUp({
      email: `test-${Date.now()}@example.com`,
      password: 'password',
    });
    testUserId = data.user.id;
  });

  it('creates and retrieves itinerary', async () => {
    const created = await repository.create({
      user_id: testUserId,
      destination: 'Tokyo, Japan',
      duration: 7,
      budget: 'luxury',
    });

    expect(created.id).toBeDefined();

    const retrieved = await repository.findById(created.id);
    expect(retrieved?.destination).toBe('Tokyo, Japan');
  });

  it('enforces RLS policies', async () => {
    // Create itinerary as user A
    const itinerary = await repository.create({
      user_id: testUserId,
      destination: 'Berlin, Germany',
    });

    // Switch to user B
    const { data } = await supabase.auth.signUp({
      email: `other-${Date.now()}@example.com`,
      password: 'password',
    });
    const otherUserId = data.user.id;

    // User B should not see user A's itinerary
    const retrieved = await repository.findById(itinerary.id);
    expect(retrieved).toBeNull();
  });
});
```

## E2E Tests (Playwright)

### What to E2E Test

- Critical user flows (sign up → create itinerary → save → view)
- Payment flows (subscribe → checkout → confirmation)
- Multi-step wizards (itinerary generation wizard)
- Cross-browser compatibility
- Mobile responsiveness

### E2E Test Patterns

```typescript
// tests/e2e/itinerary-generation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Itinerary Generation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Sign in with test user
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('generates itinerary successfully', async ({ page }) => {
    // Navigate to create page
    await page.click('text=Create Itinerary');

    // Fill in wizard - Stage 1: Quick Start
    await page.fill('[name="destination"]', 'Paris, France');
    await page.fill('[name="duration"]', '5');
    await page.click('text=Next');

    // Stage 2: Smart Filters
    await page.click('text=Culture');
    await page.click('text=Food');
    await page.selectOption('[name="budget"]', 'moderate');
    await page.click('text=Next');

    // Stage 3: Generate
    await page.click('text=Generate Itinerary');

    // Wait for generation (streaming)
    await expect(page.locator('text=Generating your itinerary')).toBeVisible();

    // Wait for completion
    await expect(page.locator('text=Day 1')).toBeVisible({ timeout: 60000 });

    // Verify itinerary content
    expect(await page.locator('.itinerary-day').count()).toBeGreaterThan(0);

    // Save itinerary
    await page.click('text=Save Itinerary');
    await expect(page.locator('text=Saved successfully')).toBeVisible();
  });

  test('handles validation errors', async ({ page }) => {
    await page.goto('/itineraries/create');

    // Submit without filling required fields
    await page.click('text=Next');

    // Should show validation errors
    await expect(page.locator('text=Destination is required')).toBeVisible();
    await expect(page.locator('text=Duration is required')).toBeVisible();
  });

  test('supports mobile responsiveness', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    await page.goto('/itineraries/create');

    // Verify mobile layout
    expect(await page.locator('.wizard-progress').isVisible()).toBe(true);
    expect(await page.locator('[name="destination"]').isVisible()).toBe(true);
  });
});
```

**Payment Flow E2E Test:**

```typescript
// tests/e2e/subscription.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Subscription Flow', () => {
  test('completes Stripe checkout', async ({ page }) => {
    await page.goto('/pricing');

    // Click on Voyager tier
    await page.click('text=Subscribe to Voyager');

    // Should redirect to Stripe checkout
    await expect(page).toHaveURL(/checkout.stripe.com/);

    // Fill in test card details
    await page.fill('[name="cardNumber"]', '4242424242424242');
    await page.fill('[name="cardExpiry"]', '12/25');
    await page.fill('[name="cardCvc"]', '123');

    // Submit payment
    await page.click('button[type="submit"]');

    // Should redirect back to success page
    await expect(page).toHaveURL(/\/subscription\/success/, { timeout: 30000 });
    await expect(page.locator('text=Subscription active')).toBeVisible();
  });

  test('handles payment failure', async ({ page }) => {
    await page.goto('/pricing');
    await page.click('text=Subscribe to Voyager');

    // Use card that will be declined
    await page.fill('[name="cardNumber"]', '4000000000000002');
    await page.fill('[name="cardExpiry"]', '12/25');
    await page.fill('[name="cardCvc"]', '123');
    await page.click('button[type="submit"]');

    // Should show error
    await expect(page.locator('text=payment failed')).toBeVisible();
  });
});
```

## Test Coverage Guidelines

### Coverage Targets

- **Unit tests:** > 80% coverage for business logic
- **Integration tests:** All API routes and database operations
- **E2E tests:** All critical user flows

### What NOT to Test

- Third-party libraries (trust their tests)
- Trivial code (getters, setters, simple mappings)
- Auto-generated code (Supabase types)
- Configuration files

### Running Tests

```bash
# Run all unit tests
pnpm test

# Run unit tests in watch mode
pnpm test:watch

# Run unit tests with coverage
pnpm test:coverage

# Run E2E tests
pnpm test:e2e

# Run E2E tests in headed mode (see browser)
pnpm test:e2e --headed

# Run specific test file
pnpm test src/lib/utils.test.ts

# Run tests matching pattern
pnpm test --grep "formatCurrency"
```

## Mocking Strategies

### Mock Supabase

```typescript
import { vi } from 'vitest';

const mockSupabase = {
  from: vi.fn(() => ({
    select: vi.fn().mockResolvedValue({ data: [], error: null }),
    insert: vi.fn().mockResolvedValue({ data: {}, error: null }),
    update: vi.fn().mockResolvedValue({ data: {}, error: null }),
    delete: vi.fn().mockResolvedValue({ data: {}, error: null }),
  })),
  auth: {
    getUser: vi.fn().mockResolvedValue({
      data: { user: { id: '123' } },
      error: null,
    }),
  },
};
```

### Mock Claude API

```typescript
import { vi } from 'vitest';

vi.mock('@/lib/claude/client', () => ({
  generateItinerary: vi.fn().mockResolvedValue({
    destination: 'Paris, France',
    days: [{ day: 1, activities: [] }],
  }),
}));
```

### Mock External APIs

```typescript
import { vi } from 'vitest';

global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ data: 'mocked' }),
});
```

## Test Data Management

### Test Fixtures

```typescript
// tests/fixtures/itineraries.ts
export const mockItinerary = {
  id: 'test-123',
  user_id: 'user-123',
  destination: 'Paris, France',
  duration: 5,
  budget: 'moderate',
  created_at: '2024-01-01T00:00:00Z',
};

export const mockItineraryList = [
  mockItinerary,
  { ...mockItinerary, id: 'test-456', destination: 'Tokyo, Japan' },
];
```

### Database Seeders

```typescript
// tests/helpers/seed-database.ts
export async function seedTestData(supabase: SupabaseClient) {
  const { data: user } = await supabase.auth.signUp({
    email: 'test@example.com',
    password: 'password',
  });

  await supabase.from('itineraries').insert([
    {
      user_id: user.id,
      destination: 'Paris, France',
      duration: 5,
    },
  ]);

  return user;
}
```

## Continuous Testing

### Pre-commit Hooks

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "pnpm lint && pnpm type-check && pnpm test"
    }
  }
}
```

### CI Pipeline

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm lint
      - run: pnpm type-check
      - run: pnpm test
      - run: pnpm test:e2e
```
