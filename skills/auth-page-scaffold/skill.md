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
```

**Stack matrix:**

| Stack | Auth provider | Pattern to use |
|---|---|---|
| Next.js App Router | Supabase | `references/auth-patterns.md` → Next.js App Router + Supabase (full) |
| Next.js App Router | NextAuth | `references/auth-patterns.md` → NextAuth stub (extend before use) |
| React + Vite | Supabase | `references/auth-patterns.md` → Vite stub (extend before use) |
| Any | Clerk / Auth0 | Not scaffolded — tell the user and point to the provider's prebuilt components; don't improvise |

Only the Next.js + Supabase path is fully scaffolded end-to-end. The other two are starting points that need filling in.

---

## Step 2 — Detect Design System

Check in this order — first hit wins:

```bash
# 1. Client brand from /theme-client (project-scoped overrides)
ls brand/theme.json brand/tokens.css 2>/dev/null

# 2. Hayah-AI design system
grep -r "hayah\|#0a3d3a\|#ff6b47" tailwind.config* src/ app/ --include="*.ts" --include="*.tsx" --include="*.css" -l 2>/dev/null | head -5
```

| Detection | Action |
|---|---|
| `brand/theme.json` exists | Use the plain unstyled variant, then apply tokens from `brand/tokens.css`. Tell the user to confirm the auth pages match the client brand spec. |
| Hayah-AI tokens present | Use the Hayah-AI variant (split-screen, teal + coral) from `references/auth-patterns.md`. |
| Neither | Use the plain unstyled variant; let the user apply styles. |

---

## Step 3 — Scaffold Pages

Determine which pages to generate:
- Login only
- Signup only
- Both (most common — this is the default for new projects)

**Always scaffolded together for a working Next.js + Supabase auth flow:**

(If Step 2 selected the Hayah-AI variant, take the login/signup page bodies from the "Hayah-AI Design System" section of `references/auth-patterns.md` instead — all other files below are shared across variants.)

| File | From section in `references/auth-patterns.md` | Required? |
|---|---|---|
| `app/(auth)/login/page.tsx` | Next.js App Router + Supabase | Yes |
| `app/(auth)/signup/page.tsx` | Next.js App Router + Supabase | Yes |
| `app/(auth)/check-email/page.tsx` | Email Confirmation Flow | Yes (signup redirects here) |
| `app/auth/callback/route.ts` | Email Confirmation Flow | Yes (Supabase confirmation links) |
| `lib/supabase/client.ts` | Next.js App Router + Supabase | Yes (if missing) |
| `lib/supabase/server.ts` | Server Client + Middleware | Yes |
| `lib/supabase/middleware.ts` | Server Client + Middleware | Yes |
| `middleware.ts` (root) | Server Client + Middleware | Yes (route protection) |
| `app/auth/signout/route.ts` | Sign Out Helper | Yes |
| `app/(auth)/forgot-password/page.tsx` | Forgot / Reset Password Flow | Yes |
| `app/(auth)/reset-password/page.tsx` | Forgot / Reset Password Flow | Yes |
| `lib/validations/auth.ts` | Shared Zod Schema | Yes if both login + signup |

Before creating any file, check it doesn't already exist:

```bash
ls <path> 2>/dev/null
```

When copying from `references/auth-patterns.md`, adapt:
1. Replace placeholder copy (app name, taglines) with project-specific text.
2. Replace `/dashboard` redirect with the project's actual post-login route.
3. Confirm the `createClient` import path matches the project's Supabase setup.
4. Confirm the middleware `PUBLIC_PATHS` list matches what the project actually exposes publicly.
5. When both login and signup are scaffolded, import the schemas from `lib/validations/auth.ts` (Shared Zod Schema section) instead of leaving them defined inline in each page — the reference page bodies define them inline for standalone use.
6. If the project is on Zod 4, replace `z.string().email(...)` with `z.email(...)` in all schemas.

---

## Step 4 — Generate Tests

Read `references/test-patterns.md` for the matching framework:

| Project test setup | Test pattern |
|---|---|
| Vitest + RTL present | Vitest + React Testing Library |
| Jest + RTL present | Jest + React Testing Library (replace `vi.` → `jest.`) |
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
- Server error path → generic "Could not create your account" message shown (not raw provider error)
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

Fix any import path errors or missing mock configurations until all tests pass before moving on.

---

## Step 6 — Post-Scaffold Report

After tests pass, report the following to the user as a checklist of work still required outside this skill's scope:

```
Auth pages scaffolded. Still required before going live:

[ ] Supabase project: confirm Site URL + Redirect URLs include
    - <your-domain>/auth/callback
    - <your-domain>/reset-password

[ ] Database: create `profiles` table (or equivalent) with a trigger to insert
    a row on `auth.users` INSERT. Add RLS policies — owner read/write only.
    Use /db-migrate for this.

[ ] Rate limiting: protect /login, /signup, /forgot-password, and the
    /auth/callback route at the edge (middleware, Upstash, or platform).

[ ] Middleware `matcher`: root middleware.ts runs on EVERY request by default,
    forcing dynamic serving and bypassing CDN caching on static assets and
    public marketing pages (shows up as frequent x-vercel-cache: MISS / slow
    TTFB in /web-perf-audit). Scope it:
      export const config = {
        matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|webp|woff2)$).*)'],
      };
    and exclude public marketing routes that need no auth check.

[ ] Env vars set in production:
    - NEXT_PUBLIC_SUPABASE_URL
    - NEXT_PUBLIC_SUPABASE_ANON_KEY

[ ] Legal pages exist at /terms and /privacy (linked from signup).
    Use /legal-docs and /ph-dpa-compliance if missing.

[ ] Email templates: customize Supabase confirmation + reset templates
    to match brand voice.

[ ] OAuth providers (Google / GitHub / etc.): not scaffolded by this skill.
    Add via supabase.auth.signInWithOAuth() if needed.
```

Tailor the list to what was actually scaffolded (skip items that already existed).

---

## Downstream Handoffs

After the report, offer the matching next step — don't auto-run it:

| Need | Hand off to |
|---|---|
| `profiles` table, trigger, RLS policies | `/db-migrate` |
| Playwright E2E coverage of the auth flow (beyond the unit tests here), or flaky auth tests | `/e2e-playwright` |
| `/terms` and `/privacy` pages | `/legal-docs` + `/ph-dpa-compliance` |
| Pre-production security/readiness gate | `/audit` |

---

## Rules

- Always read project files before generating — never assume the stack.
- Never overwrite an existing helper without confirming first.
- Never output unstyled HTML when a design system is detected.
- Always run tests after generating them — passing tests are the acceptance criterion.
- Never leak provider error messages directly to the UI — sanitize to generic copy.
- Use `next/link` for in-app navigation in Next.js, never raw `<a href>`.
- If `vitest.config.ts` is missing, scaffold it from `references/test-patterns.md`.
