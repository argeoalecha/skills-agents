# Next.js 15 Scaffold File Structure

## Create the project

```bash
npx create-next-app@latest {project-slug} \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"
cd {project-slug}
npm install @supabase/supabase-js @supabase/ssr react-hook-form zod zustand
```

## Full file tree

```
{project-slug}/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout — fonts, metadata, providers wrapper
│   │   ├── page.tsx                # Home — imports all section components
│   │   ├── globals.css             # Tailwind directives + Hayah CSS custom properties
│   │   └── api/
│   │       ├── contact/
│   │       │   └── route.ts        # POST /api/contact → Supabase contacts insert
│   │       └── apply/
│   │           └── route.ts        # POST /api/apply → Supabase applications insert
│   ├── components/
│   │   ├── nav.tsx                 # "use client" — scroll state, auth
│   │   ├── hero.tsx                # Server component — reads SITE_CONFIG
│   │   ├── services.tsx            # Server component
│   │   ├── work.tsx                # Server component
│   │   ├── about.tsx               # Server component
│   │   ├── team.tsx                # Server component
│   │   ├── testimonials.tsx        # "use client" — carousel state
│   │   ├── careers.tsx             # "use client" — apply modal state
│   │   ├── contact.tsx             # "use client" — form state, fetch /api/contact
│   │   ├── footer.tsx              # Server component
│   │   ├── providers.tsx           # "use client" — AuthProvider wrapper
│   │   └── ui/
│   │       ├── btn.tsx
│   │       ├── input.tsx
│   │       ├── tag.tsx
│   │       ├── modal.tsx           # "use client" — keyboard close handler
│   │       ├── toast.tsx           # "use client"
│   │       ├── reveal.tsx          # "use client" — IntersectionObserver
│   │       ├── label.tsx
│   │       ├── divider.tsx
│   │       └── index.ts            # Re-export all
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts           # createBrowserClient()
│   │   │   └── server.ts           # createServerClient() with cookies()
│   │   ├── site-config.ts          # SITE_CONFIG object + TypeScript type (SiteConfig)
│   │   └── validations.ts          # Zod schemas: ContactSchema, ApplicationSchema
│   └── types/
│       └── site.ts                 # SiteConfig, Service, WorkItem, TeamMember, etc.
├── supabase/
│   └── migrations/
│       └── 0001_init.sql           # Tables + RLS policies
├── public/
│   ├── og-image.png                # Placeholder OG image (replace)
│   └── favicon.ico
├── .env.local                      # gitignored — real keys here
├── .env.local.example              # committed — placeholder values
├── .gitignore
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Key file templates

### src/lib/site-config.ts

```typescript
import type { SiteConfig } from "@/types/site";

export const SITE_CONFIG: SiteConfig = {
  // ... all content
};
```

### src/types/site.ts

```typescript
export interface SiteConfig {
  brand: BrandConfig;
  theme: ThemeConfig;
  nav: string[];
  stats: Stat[];
  services: Service[];
  work: WorkItem[];
  team: TeamMember[];
  testimonials: Testimonial[];
  careers: JobListing[];
  social: SocialLinks;
}

export interface BrandConfig {
  name: string;
  shortName: string;
  tagline: string;
  subTagline: string;
  description: string;
  founded: string;
  location: string;
  phone: string;
  email: string;
  address: string;
  industry: string;
}

export interface ThemeConfig {
  bg: string;
  surface: string;
  card: string;
  border: string;
  accent: string;
  accentLit: string;
  cyan: string;
  text: string;
  muted: string;
  subtle: string;
}

export interface Stat { value: string; label: string; }
export interface Service { icon: string; title: string; desc: string; tags: string[]; }
export interface WorkItem { label: string; title: string; desc: string; metric: string; tags: string[]; }
export interface TeamMember { name: string; role: string; initials: string; }
export interface Testimonial { quote: string; author: string; }
export interface JobListing { title: string; type: "Full-time" | "Part-time" | "Contract"; location: string; dept: string; }
export interface SocialLinks { linkedin?: string; twitter?: string; github?: string; }
```

### src/lib/validations.ts

```typescript
import { z } from "zod";

export const ContactSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  company: z.string().max(100).optional(),
  service: z.string().max(100).optional(),
  message: z.string().min(10).max(2000),
});

export const ApplicationSchema = z.object({
  job_title: z.string().min(2).max(200),
  name: z.string().min(2).max(100),
  email: z.string().email(),
  linkedin_url: z.string().url().optional().or(z.literal("")),
  message: z.string().max(2000).optional(),
});

export type ContactInput = z.infer<typeof ContactSchema>;
export type ApplicationInput = z.infer<typeof ApplicationSchema>;
```

### src/app/api/contact/route.ts

```typescript
import { NextRequest, NextResponse } from "next/server";
import { ContactSchema } from "@/lib/validations";
import { createServerClient } from "@/lib/supabase/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = ContactSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid input" }, { status: 400 });
  }
  const supabase = createServerClient();
  const { error } = await supabase.from("contacts").insert(parsed.data);
  if (error) {
    return NextResponse.json({ error: "Submission failed" }, { status: 500 });
  }
  return NextResponse.json({ success: true });
}
```

### next.config.ts (security headers)

```typescript
import type { NextConfig } from "next";

const config: NextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default config;
```

### src/app/globals.css (Hayah theme tokens)

```css
@import "tailwindcss";

:root {
  --color-bg: {T.bg};
  --color-surface: {T.surface};
  --color-card: {T.card};
  --color-border: {T.border};
  --color-accent: {T.accent};
  --color-accent-lit: {T.accentLit};
  --color-highlight: {T.cyan};
  --color-text: {T.text};
  --color-muted: {T.muted};
  --color-subtle: {T.subtle};
}

html { scroll-behavior: smooth; }
body { background: var(--color-bg); color: var(--color-text); overflow-x: hidden; -webkit-font-smoothing: antialiased; }
::selection { background: var(--color-accent); color: #fff; }
input, textarea, select { color-scheme: dark; }
```
