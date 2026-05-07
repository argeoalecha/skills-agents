---
name: auth-page-scaffold
description: >
  Scaffold login and/or signup pages with verification tests. Use when the user asks to add
  a login page, signup page, registration page, or auth screen — and especially when they
  also ask to write and run tests for it. Handles email validation, wrong password, successful
  login/signup scenarios. Triggers on prompts like "Add a login page", "Create a signup page",
  "Write tests for login", "Add auth with tests", "Test email validation and wrong password".
---

# Auth Page Scaffold

Scaffolds production-ready login and signup pages with Zod validation and tests. Reads project context first, then generates code targeting the actual stack and auth provider.

---

## Step 1 — Detect Context

Before generating anything, check:

```bash
# Identify stack
ls package.json && cat package.json | grep -E '"next"|"vite"|"react"'

# Identify auth provider
grep -r "supabase\|nextauth\|clerk\|auth0" package.json

# Check if Hayah-AI design system is in use
grep -r "hayah\|#0a3d3a\|#ff6b47" tailwind.config* src/ --include="*.ts" --include="*.tsx" -l 2>/dev/null | head -5
```

**Stack matrix:**

| Stack | Auth provider | Pattern to use |
|---|---|---|
| Next.js App Router | Supabase | `references/auth-patterns.md` → Next.js App Router + Supabase |
| Next.js App Router | NextAuth | `references/auth-patterns.md` → Next.js App Router + NextAuth |
| React + Vite | Supabase | `references/auth-patterns.md` → React + Vite + Supabase |

---

## Step 2 — Detect Hayah-AI Design System

If the project uses Hayah-AI colors (`#0a3d3a`, `#ff6b47`) or the theme system, use the Hayah-AI variant from `references/auth-patterns.md` (Next.js App Router + Supabase + Hayah-AI Design System section). This produces the split-screen layout: teal left panel + cream form right.

Otherwise, use the plain unstyled variant and let the user apply their own styles.

---

## Step 3 — Scaffold Pages

Determine which pages to generate:
- Login only
- Signup only
- Both (most common)

**File paths:**
- Next.js App Router: `app/(auth)/login/page.tsx`, `app/(auth)/signup/page.tsx`
- React + Vite: `src/pages/LoginPage.tsx`, `src/pages/SignupPage.tsx`

Copy from `references/auth-patterns.md` and adapt:
1. Replace placeholder text with project-specific copy (app name, tagline)
2. Replace `/dashboard` redirect with the project's actual post-login route
3. Update the `createClient` import path to match the project's Supabase setup

If both login + signup are generated, extract shared Zod schemas to `lib/validations/auth.ts` (see Shared Zod Schema section in references).

---

## Step 4 — Generate Tests

Read `references/test-patterns.md` for the matching test framework:

| Project test setup | Test pattern |
|---|---|
| Vitest + RTL present | Use Vitest + React Testing Library |
| Jest + RTL present | Use Jest + React Testing Library (same patterns, replace `vi.` → `jest.`) |
| Playwright configured | Add E2E tests |
| No test setup | Scaffold Vitest + RTL first, then tests |

**Required test cases for login:**
- Empty email → validation error shown
- Invalid email format → validation error shown
- Valid email + wrong password → server error shown ("Invalid email or password")
- Valid credentials → redirect to dashboard (mock Supabase + router)

**Required test cases for signup:**
- Password mismatch → "Passwords do not match" error
- Short password → validation error
- Successful signup → redirect to `/check-email`

Copy from `references/test-patterns.md` and adapt imports/mocks to match project paths.

---

## Step 5 — Run Tests

After generating tests, run them:

```bash
# Vitest
npx vitest run __tests__/login.test.tsx __tests__/signup.test.tsx

# Jest
npx jest __tests__/login.test.tsx __tests__/signup.test.tsx
```

Fix any import path errors or missing mock configurations until all tests pass before reporting completion.

---

## Additional Files

Check if these helpers already exist before creating them:

```bash
ls lib/supabase/client.ts 2>/dev/null || echo "missing"
ls lib/validations/auth.ts 2>/dev/null || echo "missing"
```

**`lib/supabase/client.ts`** (create only if missing):
```typescript
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}
```

---

## Rules

- Always read project files before generating — never assume the stack
- Do not duplicate the Supabase client helper if it already exists
- If the project uses a design system, match it — never output unstyled HTML in a themed project
- Always run tests after generating them — passing tests are the acceptance criterion
- If a test fails due to a missing `vitest.config.ts`, scaffold it from `references/test-patterns.md`
