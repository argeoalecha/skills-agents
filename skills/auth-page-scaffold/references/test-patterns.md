# Auth Test Patterns

## Table of Contents
1. [Vitest + React Testing Library (component/unit tests)](#vitest-rtl)
2. [Playwright (end-to-end tests)](#playwright)
3. [Jest + React Testing Library](#jest-rtl)
4. [Mocking Supabase](#mocking-supabase)
5. [Mocking NextAuth](#mocking-nextauth)

---

## Vitest + React Testing Library {#vitest-rtl}

Best for: email validation errors, form state, client-side error messages.

### File: `__tests__/login.test.tsx`

```tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import LoginPage from '@/app/(auth)/login/page'

// Mock Supabase — see "Mocking Supabase" section below
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(),
}))

// Mock Next.js router
const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush, refresh: vi.fn() }),
}))

import { createClient } from '@/lib/supabase/client'

describe('LoginPage', () => {
  const mockSignIn = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(createClient).mockReturnValue({
      auth: { signInWithPassword: mockSignIn },
    } as unknown as ReturnType<typeof createClient>)
  })

  // --- Email validation ---

  it('shows an error when email is empty', async () => {
    render(<LoginPage />)
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText(/valid email/i)).toBeInTheDocument()
  })

  it('shows an error when email format is invalid', async () => {
    render(<LoginPage />)
    await userEvent.type(screen.getByLabelText(/email/i), 'notanemail')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText(/valid email/i)).toBeInTheDocument()
  })

  it('does not show an email error for a valid email', async () => {
    render(<LoginPage />)
    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'anypassword')
    mockSignIn.mockResolvedValue({ data: {}, error: null })
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    await waitFor(() => expect(screen.queryByText(/valid email/i)).not.toBeInTheDocument())
  })

  // --- Wrong password ---

  it('shows an error message on invalid credentials', async () => {
    render(<LoginPage />)
    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpassword')
    mockSignIn.mockResolvedValue({ data: null, error: { message: 'Invalid login credentials' } })
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument()
  })

  // --- Successful login ---

  it('redirects to /dashboard on successful login', async () => {
    render(<LoginPage />)
    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'correctpassword')
    mockSignIn.mockResolvedValue({ data: { user: { id: '1' } }, error: null })
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/dashboard'))
  })
})
```

### File: `__tests__/signup.test.tsx`

```tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SignupPage from '@/app/(auth)/signup/page'

vi.mock('@/lib/supabase/client', () => ({ createClient: vi.fn() }))
const mockPush = vi.fn()
vi.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush }) }))

import { createClient } from '@/lib/supabase/client'

describe('SignupPage', () => {
  const mockSignUp = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(createClient).mockReturnValue({
      auth: { signUp: mockSignUp },
    } as unknown as ReturnType<typeof createClient>)
  })

  it('shows error when passwords do not match', async () => {
    render(<SignupPage />)
    await userEvent.type(screen.getByLabelText(/^email/i), 'user@example.com')
    await userEvent.type(screen.getByLabelText(/^password/i), 'password123')
    await userEvent.type(screen.getByLabelText(/confirm/i), 'different123')
    await userEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument()
  })

  it('shows a generic server error (does not leak provider message)', async () => {
    render(<SignupPage />)
    await userEvent.type(screen.getByLabelText(/^email/i), 'user@example.com')
    await userEvent.type(screen.getByLabelText(/^password/i), 'password123')
    await userEvent.type(screen.getByLabelText(/confirm/i), 'password123')
    mockSignUp.mockResolvedValue({
      data: null,
      error: { message: 'User already registered in auth.users' },
    })
    await userEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText(/could not create your account/i)).toBeInTheDocument()
    expect(screen.queryByText(/auth\.users/i)).not.toBeInTheDocument()
  })

  it('redirects after successful signup', async () => {
    render(<SignupPage />)
    await userEvent.type(screen.getByLabelText(/^email/i), 'user@example.com')
    await userEvent.type(screen.getByLabelText(/^password/i), 'password123')
    await userEvent.type(screen.getByLabelText(/confirm/i), 'password123')
    mockSignUp.mockResolvedValue({ data: { user: {} }, error: null })
    await userEvent.click(screen.getByRole('button', { name: /create account/i }))
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/check-email'))
  })
})
```

### Required `vitest.config.ts` settings

```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './') },
  },
})
```

### `vitest.setup.ts`

```ts
import '@testing-library/jest-dom'
```

---

## Playwright (end-to-end) {#playwright}

Best for: testing full auth flow against a real or mock server.

### File: `e2e/login.spec.ts`

```ts
import { test, expect } from '@playwright/test'

test.describe('Login page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('shows email validation error for empty email', async ({ page }) => {
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page.getByRole('alert').filter({ hasText: /valid email/i })).toBeVisible()
  })

  test('shows error for wrong password', async ({ page }) => {
    await page.getByLabel(/email/i).fill('user@example.com')
    await page.getByLabel(/password/i).fill('wrongpassword')
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page.getByRole('alert').filter({ hasText: /invalid/i })).toBeVisible()
  })

  test('redirects to dashboard on successful login', async ({ page }) => {
    // Use a known test account seeded in the test DB or Supabase local dev
    await page.getByLabel(/email/i).fill(process.env.TEST_USER_EMAIL!)
    await page.getByLabel(/password/i).fill(process.env.TEST_USER_PASSWORD!)
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page).toHaveURL('/dashboard')
  })
})
```

**Note:** Playwright e2e tests require a running app (`npx playwright test` runs against `baseURL` in `playwright.config.ts`). For unit-level scenarios, prefer Vitest.

---

## Jest + React Testing Library {#jest-rtl}

Same test patterns as Vitest. Replace `vi.fn()` with `jest.fn()`, `vi.mock()` with `jest.mock()`, and `vi.clearAllMocks()` with `jest.clearAllMocks()`. Ensure `@testing-library/jest-dom` is imported in `jest.setup.ts`.

---

## Mocking Supabase {#mocking-supabase}

Two approaches:

**Option A — vi.mock the client factory** (shown in examples above)
```ts
vi.mock('@/lib/supabase/client', () => ({ createClient: vi.fn() }))
```
Then in each test, mock the returned auth methods via `(createClient as vi.Mock).mockReturnValue(...)`.

**Option B — MSW (Mock Service Worker)** for more realistic HTTP mocking
```ts
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'

server.use(
  http.post('https://*.supabase.co/auth/v1/token', () =>
    HttpResponse.json({ error: 'Invalid login credentials' }, { status: 400 }),
  ),
)
```
Use MSW when you want to test the full fetch chain rather than mocking at the module boundary.

---

## Mocking NextAuth {#mocking-nextauth}

```ts
import { signIn } from 'next-auth/react'
vi.mock('next-auth/react', () => ({
  signIn: vi.fn(),
  useSession: vi.fn(() => ({ data: null, status: 'unauthenticated' })),
}))

// In test:
vi.mocked(signIn).mockResolvedValue({ error: 'CredentialsSignin' } as never)
```
