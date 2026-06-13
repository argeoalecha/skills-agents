---
name: web-dev
description: Full modern website generator. Phase A — produces a single-file React artifact (preview-ready, Hayah-AI themed) from a SITE_CONFIG interview. Phase B — explodes the artifact into a full Next.js 15 App Router + TypeScript + Tailwind CSS + Supabase project scaffold. Use when the user says "build a website", "create a landing page", "scaffold a company site", "web-dev", or invokes /web-dev. Not for individual UI components or dashboards — use /ui-builder for those.
user-invocable: true
---

# Web-Dev — Modern Website Generator

Two-phase workflow:
- **Phase A** — Interview → single-file React artifact (instant preview, Hayah themed)
- **Phase B** — Explode artifact into a full Next.js 15 production scaffold

---

## Skill Root

All paths relative to: `~/.claude/skills/web-dev/`

| Path | What it is |
|---|---|
| `assets/site-config-schema.md` | SITE_CONFIG fields reference with descriptions |
| `assets/section-library.md` | All available sections with layout options |
| `assets/scaffold-structure.md` | Next.js 15 file tree template |
| `references/template-industrial.jsx` | Industrial / B2B consulting / agency (dark, professional) |
| `references/template-saas.jsx` | SaaS product landing — pricing-led, signup as primary CTA |
| `references/template-local-business.jsx` | Local service business (salon, restaurant, clinic, contractor) — booking-led, phone-prominent, PH-DPA-compliant |

Theme system lives in `~/.claude/skills/theme-hayahai/` — read it for color tokens and typography.

UI orchestration / branding lives in `~/.claude/skills/ui-builder/` — read it for logo + tagline composition rubric.

Client brand intake lives in `~/.claude/skills/theme-client/` — call it at project start when building for a paying client (not Hayah-AI). Output lives at `<project-root>/brand/`.

---

## Relationship with `/ui-builder`

`/ui-builder` is the **branding + UI orchestration** entry point. `/web-dev` is the **full-stack company website pipeline**. They are composable, not redundant:

| Need | Skill |
|---|---|
| Logo composition, tagline rubric (3 options + rationale), sub-brand mode, canonical Hayah-AI SVG | `/ui-builder` (Phase 3) — called from `/web-dev` Phase 0 |
| Landing-page **mockup** (HTML artifact, no DB, no forms wired) | `/ui-builder` (Phase 4 Landing layout) |
| Dashboard / app shell / auth pages / isolated component | `/ui-builder` (stays there) |
| **Full deployable company website** — artifact + Next.js scaffold + Supabase + RLS + security checklist | `/web-dev` (this skill) |
| Dedicated `/login` route with verification tests | `/auth-page-scaffold` (not the admin modal in `/web-dev` templates) |
| **Client brand intake** (logo + 1–3 colors → theme.json + tokens.css + Tailwind config + BRAND.md) | `/theme-client` — called once at the start of any client project |

**Rule:** when `/web-dev` Phase 0 reaches the Brand/Tagline fields, **invoke `/ui-builder` Phase 3** for the rubric and 3-option output instead of just asking for a string. Save the chosen tagline back into SITE_CONFIG.

---

## Template Selection

Pick the reference template that best matches the user's site type **before** generating anything. Each template is a working, runnable artifact with the canonical SITE_CONFIG / sections for that industry.

| If the site is… | Use template | Default theme variant |
|---|---|---|
| B2B agency, consulting, dev shop, professional services, engineering firm | `template-industrial.jsx` | Midnight (dark) or Classic |
| SaaS product, AI tool, dev tool, API, fintech app — anything with **tiered pricing + signup** | `template-saas.jsx` | Midnight, Bento, or Editorial |
| Restaurant, salon, clinic, gym, spa, automotive, plumber, contractor — any **local service biz with booking + hours + location** | `template-local-business.jsx` | Coral (warm) or Classic |

If none fits, start from the closest and adapt.

---

## Phase 0 — Context Interview

Ask all questions in **one block** before generating anything. Never split into multiple Q&A rounds.

### Required inputs

| Field | Question | Notes |
|---|---|---|
| Brand name | What is the company / product name? | — |
| Short name / initials | Abbreviation for logo badge (2–4 chars) | — |
| Industry | What industry or sector? | Determines copy tone and icon choices |
| Tagline | 4–8 word headline | Will be the H1 — **delegated to `/ui-builder` Phase 3** (see below) |
| Sub-tagline | One-sentence brand promise | Goes under H1 |
| Description | 2–3 sentence company bio | Hero body copy |
| Location | HQ city / country | Shown in hero badge |
| Founded | Year founded | Shown in hero badge |
| Contact | Email, phone, address | Contact section |
| Primary service areas | 3–6 service titles + short descriptions | Services section |

### Tagline composition — call `/ui-builder` Phase 3

Do **not** ask the user for a tagline as a free-form string. Instead, run `/ui-builder` Phase 3 (Logo + Tagline) and apply its rubric:

- **3 options + recommendation** — never propose a single tagline.
- ≤ 6 words (ideally 3–5), sentence case, no period, no exclamation point.
- Action-led or weighted noun phrase. No generic SaaS-speak ("the best", "powerful and easy to use").
- Score each option against the rubric (specificity, verb/weight, memorability, brand-truth, sub-9-word) before recommending.

For Hayah-AI sub-brands, also handle:
- **Logo composition mode** — canonical (parent), sub-brand (uses Hayah-AI palette + complementary serif), or external (client work).
- **Endorsement** — small `by hayah-ai` line for sub-brands if relevant.

Pull the canonical Hayah-AI SVG from `~/.claude/skills/theme-hayahai/hayahai-design/project/assets/HayahaiLogo.jsx` when composing parent-brand sites; do not redraw the mark.

Save the final tagline and brand decisions into the SITE_CONFIG `brand` block before generating the artifact.

### Optional inputs (ask only if not obvious from industry)

| Field | Default if skipped |
|---|---|
| Stats (4 key metrics) | Generate plausible placeholders |
| Case studies / work samples | Generate 3 fictional examples in the right industry |
| Team members (name + role) | Generate 4–6 plausible names |
| Testimonials (1–3) | Generate 2 plausible quotes |
| Open roles | Generate 2–3 common roles for the industry |

### Theme selection (always ask — three modes)

Ask first: **whose brand is this?**

| Mode | When | What to do |
|---|---|---|
| **Hayah-AI portfolio** | Project belongs to your own product suite (TripIntell, Hayah-AI SEO, levelup-crm, etc.) | Pick a Hayah variant (table below). Read the variant JSON from `/theme-hayahai`. |
| **Client brand** | Building for a paying client (the bulk of `/web-dev` work) | Check for `<project-root>/brand/theme.json`. If absent, invoke **`/theme-client`** first to generate it. Then read it. |
| **Generic / unbranded** | Quick prototype, demo, internal tool | Pick a Hayah variant as a starting point — note it's placeholder branding. |

**For Hayah-AI portfolio projects, present the five variants:**

| Variant | Mood | Best for |
|---|---|---|
| **Classic** | Sophisticated, premium | SaaS, professional services, consulting |
| **Midnight** | Powerful, cutting-edge | AI products, fintech, dark-mode tech |
| **Coral** | Warm, approachable | Marketplaces, consumer, wellness, hospitality |
| **Editorial** | Bold, authoritative | B2B thought leadership, premium launches |
| **Bento** | Innovative, dynamic | AI/tech SaaS, developer tools, startups |

Read the chosen variant's JSON from `~/.claude/skills/theme-hayahai/hayahai-design/project/themes/hayah-{variant}.json` to get:
- `colors` block → theme tokens
- `typography.googleFontsUrl` → font import
- `typography.displayFont` + `bodyFont` → font families

**For client-brand projects, read `<project-root>/brand/theme.json`** (same shape as Hayah variant JSON — drop-in compatible) and use:
- `colors` block → theme tokens (map per the `theme-client` Phase 3 mapping table)
- `typography.googleFontsUrl` → font import
- `typography.displayFont` + `bodyFont` → font families
- `<project-root>/brand/logo.svg` → swap the `SITE_CONFIG.brand.shortName` letter-mark for the client wordmark in Nav + Footer; keep shortName as initials fallback for mobile

If `<project-root>/brand/theme.json` doesn't exist when client-brand mode is chosen, **stop and invoke `/theme-client`** before continuing. Do not fall back to a Hayah variant silently.

---

## Phase A — Artifact Generation

Generate a **single-file React component** (no build step needed, runnable in Claude artifact viewer).

### Architecture of the artifact

```jsx
// 1. SITE_CONFIG object (all user content here — easy to swap)
const SITE_CONFIG = { brand, theme, nav, stats, services, work, team, testimonials, careers, social }

// 2. SUPABASE_CONFIG + mock client (identical pattern to template)
// 3. Design tokens (T = SITE_CONFIG.theme)
// 4. Auth context (Supabase auth, same as template)
// 5. Hooks: useInView, useScrollY
// 6. Primitive components: Reveal, Label, H2, Muted, Divider, Tag, Btn, Input, Modal, Toast
// 7. Auth modal
// 8. Apply modal (careers flow)
// 9. Page sections (only the ones the user requested)
// 10. Root App component
```

### Theme token mapping

Map Hayah variant colors to the `SITE_CONFIG.theme` object:

| SITE_CONFIG.theme key | Hayah source |
|---|---|
| `bg` | `colors.background` or darkest surface |
| `surface` | `colors.surface` |
| `card` | `colors.card` or slightly lighter surface |
| `border` | `rgba(255,255,255,0.07)` for dark themes; `rgba(0,0,0,0.08)` for light |
| `accent` | `colors.primary` (`#0a3d3a` deep teal) |
| `accentLit` | `colors.primaryLight` or lighter tint of primary |
| `cyan` | `colors.accent` (`#ff6b47` coral, used as highlight) |
| `text` | `colors.text` |
| `muted` | `colors.textMuted` |
| `subtle` | `colors.border` or low-contrast gray |

For **Midnight** and dark variants: bg is very dark, borders are near-invisible white.
For **Classic** and **Coral**: bg is cream/pearl, borders are light gray.

### Available sections

Include these by default (all have proven patterns in the template):

1. **Nav** — sticky, blur-on-scroll, logo, nav links, Auth + CTA buttons
2. **Hero** — dot-grid background, gradient orbs, H1 tagline, stat cards stack
3. **Services** — grid of service cards with icon, title, description, tech tags
4. **Work** — numbered list of case studies with metric callout
5. **About** — two-column: story text + value props cards
6. **Team** — avatar grid with initials
7. **Testimonials** — carousel with dot navigation
8. **Careers** — job list with Apply modal → Supabase `applications` insert
9. **Contact** — info column + Supabase-connected form → `contacts` insert
10. **Footer** — brand, sitemap, social links, admin link

Ask the user if they want to remove any sections. Add any requested custom sections.

### Supabase mock client

Always include the mock client (identical to the industrial template pattern):
- `supabase.from(table).insert()` — 800ms simulated delay, 95% success rate
- `supabase.auth.signInWithPassword()` / `signUp()` / `signOut()`
- Include the schema comment block showing the SQL to run in Supabase

### Code quality rules

- All inline styles using design token `T.*` — no hardcoded hex values in components
- `SITE_CONFIG` is the only place with content strings — components read from it
- `Reveal` component wraps every section block (scroll-triggered fade-in)
- `clamp()` for all font sizes
- No TypeScript in the artifact (it's a preview file — TS comes in Phase B)
- No `// comments` except the section headers (`// ============================================================`)

---

## Phase A → Phase B Transition

After delivering the artifact, always offer:

> "Want me to scaffold this into a full Next.js 15 project? Run `/web-dev scaffold` to explode it into proper files."

The user triggers Phase B by saying "scaffold", "yes scaffold", or `/web-dev scaffold`.

---

## Phase B — Full Project Scaffold

Read `assets/scaffold-structure.md` for the complete file tree. Generate all files.

### Stack

| Layer | Tool |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript strict (`"strict": true` in tsconfig) |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui (Radix primitives) |
| Database / Auth | Supabase (`@supabase/supabase-js` + `@supabase/ssr`) |
| Forms | React Hook Form + Zod |
| State | Zustand (only if needed; prefer server components) |
| Deployment | Vercel |

### File structure

```
{project-name}/
├── app/
│   ├── layout.tsx              # Root layout, fonts, global CSS
│   ├── page.tsx                # Home page (imports all sections)
│   ├── globals.css             # Tailwind directives + CSS vars (Hayah theme tokens)
│   └── api/
│       ├── contact/route.ts    # POST → Supabase contacts insert
│       └── apply/route.ts      # POST → Supabase applications insert
├── components/
│   ├── nav.tsx
│   ├── hero.tsx
│   ├── services.tsx
│   ├── work.tsx
│   ├── about.tsx
│   ├── team.tsx
│   ├── testimonials.tsx
│   ├── careers.tsx
│   ├── contact.tsx
│   ├── footer.tsx
│   └── ui/                     # Primitive components (Btn, Input, Tag, Modal, Toast, etc.)
│       ├── btn.tsx
│       ├── input.tsx
│       ├── tag.tsx
│       ├── modal.tsx
│       ├── toast.tsx
│       ├── reveal.tsx
│       └── index.ts
├── lib/
│   ├── supabase/
│   │   ├── client.ts           # Browser client
│   │   └── server.ts           # Server client (cookies)
│   ├── site-config.ts          # SITE_CONFIG typed with Zod
│   └── validations.ts          # Zod schemas for contact + application forms
├── types/
│   └── site.ts                 # SiteConfig, Service, WorkItem, TeamMember, etc.
├── public/
│   └── (logo, OG image placeholders)
├── supabase/
│   └── migrations/
│       └── 0001_init.sql       # contacts, applications, subscribers tables + RLS
├── .env.local.example
├── .env.local                  # (gitignored)
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### TypeScript conventions

- `SiteConfig` interface in `types/site.ts` — typed version of SITE_CONFIG
- Zod schemas in `lib/validations.ts` for all form inputs
- Server components by default; add `"use client"` only where needed (Nav, forms, carousel)
- API routes use Zod to validate request bodies before any DB call
- Return `{ error: string, code?: string }` on all API errors

### Supabase setup

Generate `supabase/migrations/0001_init.sql`:
```sql
-- contacts table
CREATE TABLE contacts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text NOT NULL,
  email text NOT NULL,
  company text,
  service text,
  message text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- applications table
CREATE TABLE applications (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  job_title text NOT NULL,
  name text NOT NULL,
  email text NOT NULL,
  linkedin_url text,
  message text,
  created_at timestamptz DEFAULT now()
);

-- subscribers table
CREATE TABLE subscribers (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- RLS
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;

-- Anonymous inserts only (public form submissions)
CREATE POLICY "allow_insert" ON contacts FOR INSERT WITH CHECK (true);
CREATE POLICY "allow_insert" ON applications FOR INSERT WITH CHECK (true);
CREATE POLICY "allow_insert" ON subscribers FOR INSERT WITH CHECK (true);
```

### Environment variables

Generate `.env.local.example`:
```
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY
```

### Tailwind CSS theme

In `globals.css`, map Hayah tokens to CSS custom properties:
```css
:root {
  --color-bg: {T.bg};
  --color-surface: {T.surface};
  --color-card: {T.card};
  --color-accent: {T.accent};
  --color-accent-lit: {T.accentLit};
  --color-cyan: {T.cyan};
  --color-text: {T.text};
  --color-muted: {T.muted};
  --color-subtle: {T.subtle};
}
```

In `tailwind.config.ts`, extend the palette with these CSS vars so Tailwind utilities use the theme.

### Fonts

Read the font families from the chosen theme JSON (`typography.displayFont` + `bodyFont`) and load them with **`next/font/google` in `app/layout.tsx` — never a `<link>` tag to Google Fonts**. `next/font` self-hosts at build time: no render-blocking external CSS, no `fonts.googleapis.com`/`fonts.gstatic.com` CSP allowances, zero layout shift.

Budget (from `/web-perf-audit`): ≤2 typefaces × ≤2 weights, `subsets: ['latin']`, total <60KB / ≤4 files. The theme JSON's `googleFontsUrl` is for artifact preview (Phase A) only.

```ts
import { DM_Serif_Display, Inter } from 'next/font/google';
const display = DM_Serif_Display({ weight: '400', subsets: ['latin'], variable: '--font-display' });
const body = Inter({ weight: ['400', '600'], subsets: ['latin'], variable: '--font-body' });
```

### Component conversion rules

When splitting the single-file artifact into proper components:

1. Each section (Nav, Hero, etc.) → its own file in `components/`
2. Primitive UI components → `components/ui/`
3. `SITE_CONFIG` → `lib/site-config.ts` (add TypeScript types)
4. `supabase` mock → replace with real `lib/supabase/client.ts`
5. API calls in Contact/Apply forms → move to `app/api/*/route.ts` (server-side)
6. Inline `style={}` → Tailwind classes where straightforward; keep inline style only for dynamic values that depend on theme tokens at runtime
7. `AuthContext` → can stay in a `components/providers.tsx` wrapper

### Security checklist (apply before finishing scaffold)

**Mandatory — do not ship without these:**
- [ ] All API routes validate input with Zod **before** DB call
- [ ] Supabase anon key only — service role key never in client code
- [ ] RLS policies defined for all tables (INSERT-only for public form tables)
- [ ] **Rate limiting wired** into `/api/contact`, `/api/apply`, `/api/booking`, `/api/signup` using `@upstash/ratelimit` + Upstash Redis (free tier). Not "noted in README" — actually implemented. Example:
  ```ts
  import { Ratelimit } from "@upstash/ratelimit";
  import { Redis } from "@upstash/redis";
  const limiter = new Ratelimit({ redis: Redis.fromEnv(), limiter: Ratelimit.slidingWindow(5, "10 m") });
  const ip = req.headers.get("x-forwarded-for") ?? "anon";
  const { success } = await limiter.limit(ip);
  if (!success) return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  ```
- [ ] **Cloudflare Turnstile** (or honeypot field) on every public POST form
- [ ] **CSP + Permissions-Policy headers** in `next.config.ts`:
  ```ts
  { key: "Content-Security-Policy", value: "default-src 'self'; script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: https:; connect-src 'self' https://*.supabase.co" }
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" }
  ```
  (No Google Fonts origins needed — fonts are self-hosted via `next/font`, see Fonts section.)
- [ ] **Cache-Control headers** in the same `next.config.ts` `headers()` block — framework defaults ship `max-age=0, must-revalidate` HTML with no CDN persistence (observed 1.4–2.4s cold TTFB):
  ```ts
  // static pages (marketing site = all pages)
  { key: "Vercel-CDN-Cache-Control", value: "public, s-maxage=31536000, stale-while-revalidate=86400" },
  { key: "Cache-Control", value: "public, max-age=0, s-maxage=86400, stale-while-revalidate=300" },
  ```
  On Netlify use `Netlify-CDN-Cache-Control: public, durable, s-maxage=31536000, stale-while-revalidate=86400` instead. Rationale + platform variants: `~/.claude/skills/web-perf-audit/references/host-vercel.md` / `host-netlify.md`.
- [ ] **PH DPA / RA 10173 consent checkbox** on every form that captures personal data (required, not pre-checked). Delegate full privacy-policy generation to `/ph-dpa-compliance`.
- [ ] **Admin login moved off public nav** — put it at `/admin` route, not in marketing footer
- [ ] **Sentry** (`@sentry/nextjs`) installed and `SENTRY_DSN` env var documented
- [ ] **`images.remotePatterns`** whitelist in `next.config.ts` (avoid Next/Image SSRF surface)
- [ ] No secrets in `.env.local.example`
- [ ] `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` set
- [ ] `.gitignore` includes `.env.local`, `.env*.local`, `node_modules/`, `.next/`

**Pre-launch verification:**
- [ ] Run `npm audit --omit=dev` — no high/critical CVEs
- [ ] Confirm RLS policies block anon SELECT on contacts/applications/bookings
- [ ] Test rate limiter triggers at expected threshold
- [ ] Test Turnstile / honeypot blocks bots
- [ ] Verify consent checkbox is required and stored (`consent_dpa` column)

For deeper review run `/audit` (security + compliance gates) and `/ph-dpa-compliance` before deployment. After the first production deploy, run `/web-perf-audit` against the live URL — it verifies delivered headers, TTFB, CDN caching, and DNS-level issues (double-proxy) that no pre-deploy check can see.

---

## Delivery Format

### Phase A
- Output as a **React artifact** the user can preview immediately
- State the theme chosen and why
- List which sections are included
- End with the Phase B offer

### Phase B
- Output each file separately, labelled with its path
- After all files: print a **Quick Start** block:
  ```bash
  npx create-next-app@latest {project-name} --typescript --tailwind --app
  # then copy files...
  npx supabase login
  supabase db push
  vercel --prod
  ```
- Note any manual steps (Supabase project creation, env var setup)

---

## Quality Gates

Before delivering Phase A:
- [ ] All SITE_CONFIG values filled (no "Lorem ipsum", no unreplaced placeholders)
- [ ] Theme tokens correctly mapped from chosen Hayah variant
- [ ] Supabase mock client present and functional
- [ ] All sections render without errors
- [ ] Mobile responsive (CSS grid `auto-fit`, `clamp()` font sizes, `@media` for nav)

Before delivering Phase B:
- [ ] TypeScript compiles with no errors (simulate mentally)
- [ ] No hardcoded secrets
- [ ] RLS migration included
- [ ] All form submissions go through API routes (not direct client Supabase calls)
- [ ] `.env.local.example` committed, `.env.local` in `.gitignore`
- [ ] Bundle within budget: run `npm run build`, read the route table — First Load JS <200KB per route, all routes `○ (Static)` (a marketing site has no excuse for `ƒ (Dynamic)`). Budgets and bloat patterns: `~/.claude/skills/web-perf-audit/references/local-build-audit.md`
