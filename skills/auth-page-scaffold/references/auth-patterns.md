# Auth Page Patterns

## Table of Contents
1. [Next.js App Router + Supabase + React Hook Form + Zod](#nextjs-app-router)
2. [Server Client + Middleware + Route Protection](#server-protection)
3. [Email Confirmation Flow (`/check-email` + `/auth/callback`)](#email-confirmation)
4. [Forgot / Reset Password Flow](#forgot-password)
5. [Sign Out Helper](#sign-out)
6. [Next.js App Router + NextAuth.js](#nextjs-nextauth) — stub, extend before use
7. [React + Vite + Supabase](#react-vite) — stub, extend before use
8. [Next.js App Router + Supabase + Hayah-AI Design System](#nextjs-hayahai)
9. [Shared Zod Schema](#shared-zod-schema)

---

## Next.js App Router + Supabase + React Hook Form + Zod {#nextjs-app-router}

### File: `app/(auth)/login/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/client'

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const supabase = createClient()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) })

  async function onSubmit(data: LoginFormData) {
    setServerError(null)
    const { error } = await supabase.auth.signInWithPassword({
      email: data.email,
      password: data.password,
    })
    if (error) {
      setServerError('Invalid email or password.')
      return
    }
    router.push('/dashboard')
    router.refresh()
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="w-full max-w-sm space-y-4"
        aria-label="Login form"
      >
        <h1 className="text-2xl font-semibold">Sign in</h1>

        {serverError && (
          <p role="alert" className="text-sm text-red-600">{serverError}</p>
        )}

        <div>
          <label htmlFor="email">Email</label>
          <input id="email" type="email" {...register('email')} />
          {errors.email && (
            <p role="alert">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="password">Password</label>
          <input id="password" type="password" {...register('password')} />
          {errors.password && (
            <p role="alert">{errors.password.message}</p>
          )}
        </div>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in...' : 'Sign in'}
        </button>

        <p>
          No account? <Link href="/signup">Sign up</Link>
        </p>
        <p>
          <Link href="/forgot-password">Forgot password?</Link>
        </p>
      </form>
    </main>
  )
}
```

### File: `app/(auth)/signup/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/client'

const signupSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type SignupFormData = z.infer<typeof signupSchema>

export default function SignupPage() {
  const router = useRouter()
  const supabase = createClient()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormData>({ resolver: zodResolver(signupSchema) })

  async function onSubmit(data: SignupFormData) {
    setServerError(null)
    const { error } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) {
      setServerError('Could not create your account. Please try again.')
      return
    }
    router.push('/check-email')
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="w-full max-w-sm space-y-4"
        aria-label="Signup form"
      >
        <h1 className="text-2xl font-semibold">Create account</h1>

        {serverError && (
          <p role="alert" className="text-sm text-red-600">{serverError}</p>
        )}

        <div>
          <label htmlFor="email">Email</label>
          <input id="email" type="email" {...register('email')} />
          {errors.email && <p role="alert">{errors.email.message}</p>}
        </div>

        <div>
          <label htmlFor="password">Password</label>
          <input id="password" type="password" {...register('password')} />
          {errors.password && <p role="alert">{errors.password.message}</p>}
        </div>

        <div>
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input id="confirmPassword" type="password" {...register('confirmPassword')} />
          {errors.confirmPassword && <p role="alert">{errors.confirmPassword.message}</p>}
        </div>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account...' : 'Create account'}
        </button>

        <p>Already have an account? <Link href="/login">Sign in</Link></p>
      </form>
    </main>
  )
}
```

### Supabase Client Helper (if not yet present)

`lib/supabase/client.ts`:
```ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )
}
```

---

## Server Client + Middleware + Route Protection {#server-protection}

The browser client alone doesn't protect routes. For any Next.js App Router + Supabase project you also need a server client and middleware to refresh sessions and gate protected pages.

### File: `lib/supabase/server.ts`

```ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            )
          } catch {
            // Called from a Server Component — safely ignored if middleware refreshes the session.
          }
        },
      },
    },
  )
}
```

### File: `lib/supabase/middleware.ts`

```ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

const PUBLIC_PATHS = ['/login', '/signup', '/forgot-password', '/reset-password', '/check-email', '/auth/callback']

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          response = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options))
        },
      },
    },
  )

  const { data: { user } } = await supabase.auth.getUser()
  const pathname = request.nextUrl.pathname
  const isPublic = PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`))

  if (!user && !isPublic) {
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    url.searchParams.set('next', pathname)
    return NextResponse.redirect(url)
  }

  return response
}
```

### File: `middleware.ts` (project root)

```ts
import { updateSession } from '@/lib/supabase/middleware'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  return updateSession(request)
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
}
```

---

## Email Confirmation Flow {#email-confirmation}

Supabase defaults to email confirmation. Without the callback route, the confirmation link goes nowhere. Without `/check-email`, signup users hit a 404.

### File: `app/auth/callback/route.ts`

```ts
import { NextResponse, type NextRequest } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`)
}
```

### File: `app/(auth)/check-email/page.tsx`

```tsx
import Link from 'next/link'

export default function CheckEmailPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md space-y-4 text-center">
        <h1 className="text-2xl font-semibold">Check your email</h1>
        <p className="text-sm text-gray-600">
          We sent a confirmation link to your inbox. Click it to activate your account.
        </p>
        <p className="text-sm">
          Didn&apos;t get it? Check your spam folder, or{' '}
          <Link href="/signup" className="underline">try signing up again</Link>.
        </p>
      </div>
    </main>
  )
}
```

---

## Forgot / Reset Password Flow {#forgot-password}

### File: `app/(auth)/forgot-password/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/client'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})
type FormData = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const supabase = createClient()
  const [submitted, setSubmitted] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  async function onSubmit(data: FormData) {
    await supabase.auth.resetPasswordForEmail(data.email, {
      // Route through /auth/callback so the code is exchanged for a session
      // server-side before landing on /reset-password — updateUser needs it.
      redirectTo: `${window.location.origin}/auth/callback?next=/reset-password`,
    })
    // Always show success to prevent email enumeration.
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-md text-center">
          <h1 className="text-2xl font-semibold">Check your email</h1>
          <p className="mt-2 text-sm text-gray-600">
            If an account exists for that email, we&apos;ve sent a reset link.
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-sm space-y-4" aria-label="Forgot password form">
        <h1 className="text-2xl font-semibold">Reset password</h1>
        <div>
          <label htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="email" {...register('email')} />
          {errors.email && <p role="alert">{errors.email.message}</p>}
        </div>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Sending...' : 'Send reset link'}
        </button>
        <p><Link href="/login">Back to sign in</Link></p>
      </form>
    </main>
  )
}
```

### File: `app/(auth)/reset-password/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/client'

const schema = z
  .object({
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })
type FormData = z.infer<typeof schema>

export default function ResetPasswordPage() {
  const router = useRouter()
  const supabase = createClient()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  async function onSubmit(data: FormData) {
    setServerError(null)
    const { error } = await supabase.auth.updateUser({ password: data.password })
    if (error) {
      setServerError('Could not reset your password. The link may have expired.')
      return
    }
    router.push('/login?reset=success')
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-sm space-y-4" aria-label="Reset password form">
        <h1 className="text-2xl font-semibold">Set a new password</h1>
        {serverError && <p role="alert" className="text-sm text-red-600">{serverError}</p>}
        <div>
          <label htmlFor="password">New password</label>
          <input id="password" type="password" autoComplete="new-password" {...register('password')} />
          {errors.password && <p role="alert">{errors.password.message}</p>}
        </div>
        <div>
          <label htmlFor="confirmPassword">Confirm new password</label>
          <input id="confirmPassword" type="password" autoComplete="new-password" {...register('confirmPassword')} />
          {errors.confirmPassword && <p role="alert">{errors.confirmPassword.message}</p>}
        </div>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Updating...' : 'Update password'}
        </button>
      </form>
    </main>
  )
}
```

---

## Sign Out Helper {#sign-out}

### File: `app/auth/signout/route.ts`

```ts
import { NextResponse, type NextRequest } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function POST(request: NextRequest) {
  const supabase = await createClient()
  await supabase.auth.signOut()
  return NextResponse.redirect(new URL('/login', request.url), { status: 303 })
}
```

Trigger from any client component with a plain form: `<form action="/auth/signout" method="post"><button>Sign out</button></form>`.

---

## Next.js App Router + NextAuth.js {#nextjs-nextauth}

> **Stub — extend before use.** The Supabase variant above is the only fully scaffolded option. NextAuth requires its own `auth.ts` config, route handler, and provider setup that vary by app. If you choose NextAuth, treat the notes below as a starting point and fill in the missing config from the NextAuth.js docs.

In the login form `onSubmit`:

```ts
import { signIn } from 'next-auth/react'

const result = await signIn('credentials', {
  email: data.email,
  password: data.password,
  redirect: false,
})
if (result?.error) {
  setServerError('Invalid email or password.')
  return
}
router.push('/dashboard')
```

Confirm `auth.ts` and `app/api/auth/[...nextauth]/route.ts` exist before scaffolding. Do not duplicate them.

---

## React + Vite + Supabase {#react-vite}

> **Stub — extend before use.** Reuse the Next.js Supabase form bodies and adapt the imports below. There is no middleware / SSR session refresh in a Vite SPA — protect routes with a `<RequireAuth>` wrapper or react-router loader instead.

Differences vs. the Next.js variant:

- Replace `'use client'` — remove it (Vite has no directives).
- Replace `useRouter` with `useNavigate` from `react-router-dom`. `router.push('/x')` → `navigate('/x')`.
- Replace `next/link` `<Link>` with `react-router-dom` `<Link to="/x">`.
- File location: `src/pages/LoginPage.tsx`, `src/pages/SignupPage.tsx`.
- Supabase client: singleton in `src/lib/supabase.ts`:
  ```ts
  import { createClient } from '@supabase/supabase-js'
  export const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL!,
    import.meta.env.VITE_SUPABASE_ANON_KEY!,
  )
  ```
- Email-confirmation callback in a Vite SPA: use a `/auth/callback` route component that reads `code` from the URL and calls `supabase.auth.exchangeCodeForSession(code)`.

---

## Next.js App Router + Supabase + Hayah-AI Design System {#nextjs-hayahai}

Use this template when the project uses the Hayah-AI design system (see Step 2 — Detect Design System in `../skill.md`). It produces a split-screen layout (left: branded dark-teal panel, right: form on cream) matching the `auth-classic` reference variant in `theme-hayahai/auth-pages/`.

Color tokens used (all via Tailwind arbitrary values):

| Token | Hex | Usage |
|---|---|---|
| Deep Teal | `#0a3d3a` | Left panel bg, headings, input text |
| Coral | `#ff6b47` | CTA button, logo mark, links, error text |
| Cream | `#faf7f5` | Right panel bg, text on dark |
| Pearl | `#e8f4f1` | Subtle surface, error background |
| Medium Teal | `#1C5753` | Form labels |
| Aqua | `#25A497` | Focus ring |
| Mint Light | `#A1E4DB` | Input border, left panel text |
| Sage | `#7a9b96` | Muted text, placeholders |

### File: `app/(auth)/login/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, ArrowRight } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const supabase = createClient()
  const [serverError, setServerError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) })

  async function onSubmit(data: LoginFormData) {
    setServerError(null)
    const { error } = await supabase.auth.signInWithPassword({
      email: data.email,
      password: data.password,
    })
    if (error) {
      setServerError('Invalid email or password.')
      return
    }
    router.push('/dashboard')
    router.refresh()
  }

  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      {/* Left Panel */}
      <div className="relative hidden lg:flex flex-col justify-between bg-[#0a3d3a] p-12 overflow-hidden">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-[#ff6b47] rounded-[10px] flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 3v14M16 3v14M4 10h12" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <span className="font-serif text-[22px] text-[#faf7f5]">Hayah-AI</span>
        </div>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-widest text-[#A1E4DB] mb-7">
            Trusted by 12,000+ teams
          </p>
          <h1 className="text-5xl leading-[1.1] tracking-tight text-[#faf7f5] mb-6">
            Intelligence that<br />
            <em className="text-[#ff6b47] not-italic">elevates</em> your work.
          </h1>
          <p className="text-base leading-relaxed text-[#A1E4DB] max-w-sm">
            The AI command center built for professionals who refuse to compromise on quality or clarity.
          </p>
        </div>
        <p className="text-xs text-[#7a9b96]">© 2026 Hayah-AI</p>
      </div>

      {/* Right Panel — form */}
      <div className="flex flex-col items-center justify-center bg-[#faf7f5] px-6 py-12 lg:px-12">
        <div className="w-full max-w-[420px]">
          <div className="mb-9">
            <p className="text-[11px] font-bold uppercase tracking-widest text-[#7a9b96] mb-2.5">
              Welcome back
            </p>
            <h2 className="text-[34px] leading-tight tracking-tight text-[#0a3d3a] mb-2">
              Sign in to Hayah-AI
            </h2>
            <p className="text-[15px] text-[#7a9b96]">
              New here?{' '}
              <Link href="/signup" className="font-semibold text-[#ff6b47] hover:underline">
                Create a free account
              </Link>
            </p>
          </div>

          {serverError && (
            <p role="alert" className="mb-5 rounded-lg bg-[#ffb5a0] px-4 py-3 text-sm font-medium text-[#0a3d3a]">
              {serverError}
            </p>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate aria-label="Login form">
            <div className="flex flex-col gap-[18px] mb-6">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="email" className="text-[13px] font-semibold text-[#1C5753]">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  autoComplete="email"
                  {...register('email')}
                  className="h-12 px-4 rounded-[10px] border border-[#A1E4DB] bg-white text-[15px] text-[#0a3d3a] placeholder:text-[#7a9b96] outline-none transition focus:border-[#25A497] focus:ring-[3px] focus:ring-[#25A497]/20"
                />
                {errors.email && (
                  <p role="alert" className="text-xs text-[#ff6b47]">{errors.email.message}</p>
                )}
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="password" className="text-[13px] font-semibold text-[#1C5753]">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    {...register('password')}
                    className="h-12 w-full px-4 pr-12 rounded-[10px] border border-[#A1E4DB] bg-white text-[15px] text-[#0a3d3a] placeholder:text-[#7a9b96] outline-none transition focus:border-[#25A497] focus:ring-[3px] focus:ring-[#25A497]/20"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#7a9b96] hover:text-[#1C5753] transition"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.password && (
                  <p role="alert" className="text-xs text-[#ff6b47]">{errors.password.message}</p>
                )}
              </div>

              <div className="flex justify-end">
                <Link href="/forgot-password" className="text-[13px] font-semibold text-[#ff6b47] hover:underline">
                  Forgot password?
                </Link>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 h-[52px] bg-[#ff6b47] hover:bg-[#e85730] disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold text-base rounded-[10px] shadow-[0_4px_16px_rgba(255,107,71,0.35)] hover:shadow-[0_6px_20px_rgba(255,107,71,0.45)] transition"
            >
              {isSubmitting ? 'Signing in...' : <><span>Sign in</span><ArrowRight size={16} /></>}
            </button>
          </form>
        </div>
      </div>
    </main>
  )
}
```

### File: `app/(auth)/signup/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, ArrowRight } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

const signupSchema = z
  .object({
    email: z.string().email('Enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type SignupFormData = z.infer<typeof signupSchema>

export default function SignupPage() {
  const router = useRouter()
  const supabase = createClient()
  const [serverError, setServerError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormData>({ resolver: zodResolver(signupSchema) })

  async function onSubmit(data: SignupFormData) {
    setServerError(null)
    const { error } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) {
      setServerError('Could not create your account. Please try again.')
      return
    }
    router.push('/check-email')
  }

  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      {/* Left Panel */}
      <div className="relative hidden lg:flex flex-col justify-between bg-[#0a3d3a] p-12 overflow-hidden">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-[#ff6b47] rounded-[10px] flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 3v14M16 3v14M4 10h12" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <span className="font-serif text-[22px] text-[#faf7f5]">Hayah-AI</span>
        </div>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-widest text-[#A1E4DB] mb-7">
            Free to start
          </p>
          <h1 className="text-5xl leading-[1.1] tracking-tight text-[#faf7f5] mb-6">
            Your <em className="text-[#ff6b47] not-italic">creative</em><br />
            workspace awaits.
          </h1>
          <p className="text-base leading-relaxed text-[#A1E4DB] max-w-sm">
            Join thousands of teams already building smarter with Hayah-AI.
          </p>
        </div>
        <p className="text-xs text-[#7a9b96]">© 2026 Hayah-AI</p>
      </div>

      {/* Right Panel — form */}
      <div className="flex flex-col items-center justify-center bg-[#faf7f5] px-6 py-12 lg:px-12">
        <div className="w-full max-w-[420px]">
          <div className="mb-9">
            <p className="text-[11px] font-bold uppercase tracking-widest text-[#7a9b96] mb-2.5">
              Get started
            </p>
            <h2 className="text-[34px] leading-tight tracking-tight text-[#0a3d3a] mb-2">
              Create your account
            </h2>
            <p className="text-[15px] text-[#7a9b96]">
              Already a member?{' '}
              <Link href="/login" className="font-semibold text-[#ff6b47] hover:underline">
                Sign in
              </Link>
            </p>
          </div>

          {serverError && (
            <p role="alert" className="mb-5 rounded-lg bg-[#ffb5a0] px-4 py-3 text-sm font-medium text-[#0a3d3a]">
              {serverError}
            </p>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate aria-label="Signup form">
            <div className="flex flex-col gap-[18px] mb-6">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="email" className="text-[13px] font-semibold text-[#1C5753]">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  autoComplete="email"
                  {...register('email')}
                  className="h-12 px-4 rounded-[10px] border border-[#A1E4DB] bg-white text-[15px] text-[#0a3d3a] placeholder:text-[#7a9b96] outline-none transition focus:border-[#25A497] focus:ring-[3px] focus:ring-[#25A497]/20"
                />
                {errors.email && (
                  <p role="alert" className="text-xs text-[#ff6b47]">{errors.email.message}</p>
                )}
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="password" className="text-[13px] font-semibold text-[#1C5753]">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Create a password (8+ characters)"
                    autoComplete="new-password"
                    {...register('password')}
                    className="h-12 w-full px-4 pr-12 rounded-[10px] border border-[#A1E4DB] bg-white text-[15px] text-[#0a3d3a] placeholder:text-[#7a9b96] outline-none transition focus:border-[#25A497] focus:ring-[3px] focus:ring-[#25A497]/20"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#7a9b96] hover:text-[#1C5753] transition"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.password && (
                  <p role="alert" className="text-xs text-[#ff6b47]">{errors.password.message}</p>
                )}
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="confirmPassword" className="text-[13px] font-semibold text-[#1C5753]">
                  Confirm password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  placeholder="Repeat your password"
                  autoComplete="new-password"
                  {...register('confirmPassword')}
                  className="h-12 px-4 rounded-[10px] border border-[#A1E4DB] bg-white text-[15px] text-[#0a3d3a] placeholder:text-[#7a9b96] outline-none transition focus:border-[#25A497] focus:ring-[3px] focus:ring-[#25A497]/20"
                />
                {errors.confirmPassword && (
                  <p role="alert" className="text-xs text-[#ff6b47]">{errors.confirmPassword.message}</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 h-[52px] bg-[#ff6b47] hover:bg-[#e85730] disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold text-base rounded-[10px] shadow-[0_4px_16px_rgba(255,107,71,0.35)] hover:shadow-[0_6px_20px_rgba(255,107,71,0.45)] transition"
            >
              {isSubmitting ? 'Creating account...' : <><span>Create account</span><ArrowRight size={16} /></>}
            </button>
          </form>

          <p className="mt-4 text-center text-[12px] text-[#7a9b96]">
            By signing up, you agree to our{' '}
            <Link href="/terms" className="text-[#1E6E66] hover:underline">Terms</Link>
            {' '}and{' '}
            <Link href="/privacy" className="text-[#1E6E66] hover:underline">Privacy Policy</Link>.
          </p>
        </div>
      </div>
    </main>
  )
}
```

### Variant selection guide

The classic split-screen above is the default. For other moods, reference the corresponding HTML file in `theme-hayahai/auth-pages/` and adapt the color tokens:

| Variant | HTML file | Best for | Key difference |
|---|---|---|---|
| Classic (default) | `auth-classic.html` | SaaS, professional tools | Split-screen, teal left panel |
| Coral | `auth-coral.html` | Consumer apps, marketplaces | Top nav, warm coral accents |
| Editorial | `auth-editorial.html` | B2B enterprise | Bold typography, minimal color |
| Midnight | `auth-midnight.html` | AI/dev tools | Dark mode, glassmorphism |
| Bento | `auth-bento.html` | Modern AI products | Grid layout with metrics |

---

## Shared Zod Schema {#shared-zod-schema}

When both login and signup pages exist, extract shared validation into `lib/validations/auth.ts`:

```ts
import { z } from 'zod'

export const emailField = z.string().email('Enter a valid email address')
export const passwordField = z.string().min(8, 'Password must be at least 8 characters')

export const loginSchema = z.object({
  email: emailField,
  password: z.string().min(1, 'Password is required'),
})

export const signupSchema = z
  .object({ email: emailField, password: passwordField, confirmPassword: z.string() })
  .refine((d) => d.password === d.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })
```
