# Auth Page Patterns

## Table of Contents
1. [Next.js App Router + Supabase + React Hook Form + Zod](#nextjs-app-router)
2. [Next.js App Router + NextAuth.js](#nextjs-nextauth)
3. [React + Vite + Supabase](#react-vite)
4. [Shared Zod Schema](#shared-zod-schema)

---

## Next.js App Router + Supabase + React Hook Form + Zod {#nextjs-app-router}

### File: `app/(auth)/login/page.tsx`

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
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
          No account? <a href="/signup">Sign up</a>
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
    })
    if (error) {
      setServerError(error.message)
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

        <p>Already have an account? <a href="/login">Sign in</a></p>
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

## Next.js App Router + NextAuth.js {#nextjs-nextauth}

Use `signIn('credentials', { email, password, redirect: false })` inside `onSubmit`. Check the returned `error` field for failed attempts. On success, call `router.push('/dashboard')`.

For NextAuth setup (`auth.ts`, `app/api/auth/[...nextauth]/route.ts`), check existing project structure first — do not duplicate if already present.

---

## React + Vite + Supabase {#react-vite}

Same logic as Next.js App Router, but:
- Use `useNavigate()` from `react-router-dom` instead of `useRouter()`
- No `'use client'` directive needed
- Place file at `src/pages/LoginPage.tsx`
- Import Supabase from `src/lib/supabase.ts` (a singleton `createClient()` call)

---

## Next.js App Router + Supabase + Hayah-AI Design System {#nextjs-hayahai}

Use this template when the project uses the Hayah-AI design system (see [Hayah-AI Detection in SKILL.md](../SKILL.md)). It produces a split-screen layout (left: branded dark-teal panel, right: form on cream) matching the `auth-classic` reference variant in `theme-hayahai/auth-pages/`.

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
          <span className="font-serif text-[22px] text-[#faf7f5]">Hayah</span>
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
        <p className="text-xs text-[#7a9b96]">© 2026 Hayah AI</p>
      </div>

      {/* Right Panel — form */}
      <div className="flex flex-col items-center justify-center bg-[#faf7f5] px-6 py-12 lg:px-12">
        <div className="w-full max-w-[420px]">
          <div className="mb-9">
            <p className="text-[11px] font-bold uppercase tracking-widest text-[#7a9b96] mb-2.5">
              Welcome back
            </p>
            <h2 className="text-[34px] leading-tight tracking-tight text-[#0a3d3a] mb-2">
              Sign in to Hayah
            </h2>
            <p className="text-[15px] text-[#7a9b96]">
              New here?{' '}
              <a href="/signup" className="font-semibold text-[#ff6b47] hover:underline">
                Create a free account
              </a>
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
                <a href="/forgot-password" className="text-[13px] font-semibold text-[#ff6b47] hover:underline">
                  Forgot password?
                </a>
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
    })
    if (error) {
      setServerError(error.message)
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
          <span className="font-serif text-[22px] text-[#faf7f5]">Hayah</span>
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
            Join thousands of teams already building smarter with Hayah.
          </p>
        </div>
        <p className="text-xs text-[#7a9b96]">© 2026 Hayah AI</p>
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
              <a href="/login" className="font-semibold text-[#ff6b47] hover:underline">
                Sign in
              </a>
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
            <a href="/terms" className="text-[#1E6E66] hover:underline">Terms</a>
            {' '}and{' '}
            <a href="/privacy" className="text-[#1E6E66] hover:underline">Privacy Policy</a>.
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
