# SITE_CONFIG Schema Reference

Every generated website uses this object as its single source of truth for content.
All components read from it — no content strings live elsewhere.

```typescript
interface SiteConfig {
  brand: {
    name: string;           // Full company name
    shortName: string;      // 2–4 char initials for logo badge
    tagline: string;        // H1 headline (4–8 words)
    subTagline: string;     // One-sentence brand promise
    description: string;   // 2–3 sentence bio (hero body)
    founded: string;        // Year, e.g. "2015"
    location: string;       // City, Country
    phone: string;
    email: string;
    address: string;
    industry: string;
  };

  theme: {
    bg: string;             // Page background hex
    surface: string;        // Section background hex
    card: string;           // Card/panel background hex
    border: string;         // rgba border value
    accent: string;         // Primary brand color (buttons, highlights)
    accentLit: string;      // Lighter variant for hover states
    cyan: string;           // Complementary highlight (metrics, badges)
    text: string;           // Primary text color
    muted: string;          // Secondary / body text
    subtle: string;         // Placeholder, disabled, low-priority text
  };

  nav: string[];            // Section names for nav links

  stats: Array<{
    value: string;          // "200+", "98%", "40+"
    label: string;          // "Projects Shipped", "Client Retention"
  }>;

  services: Array<{
    icon: string;           // Unicode symbol or single char
    title: string;
    desc: string;           // 1–2 sentences
    tags: string[];         // 2–5 tech/topic tags
  }>;

  work: Array<{
    label: string;          // Industry label ("Fintech", "SaaS", "AI")
    title: string;          // Project title
    desc: string;           // 1–2 sentences
    metric: string;         // Key result ("4M txns/day", "300+ tenants")
    tags: string[];
  }>;

  team: Array<{
    name: string;
    role: string;
    initials: string;       // 2-char initials for avatar
  }>;

  testimonials: Array<{
    quote: string;
    author: string;         // Title, Company (no real names)
  }>;

  careers: Array<{
    title: string;
    type: "Full-time" | "Part-time" | "Contract";
    location: string;
    dept: string;
  }>;

  social: {
    linkedin?: string;
    twitter?: string;
    github?: string;
    [key: string]: string | undefined;
  };
}
```

## Icon suggestions by industry

| Industry | Icons to use |
|---|---|
| Technology / SaaS | ◈ ◉ ◐ ◑ ◒ ◓ ◆ ◇ |
| Industrial / Engineering | ⬡ ⬢ ⌬ △ ▲ ◼ ◻ |
| Healthcare / Medical | ✦ ✧ ◎ ⊕ ⊗ |
| Finance / Fintech | ◈ ▣ ▤ ▥ ▦ |
| Creative / Design | ◐ ◑ ◒ ◓ ● ○ |
| Legal / Professional | ▶ ▷ ◀ ◁ ◆ ◇ |
| Education | ◉ ◎ ○ ● ◯ |
| Real Estate | ⬡ ⬢ ◼ ◻ ▲ △ |

## Placeholder generation rules

When the user doesn't provide data, generate plausible placeholders that:
- Match the industry (don't put "Kafka" tags on a law firm)
- Use realistic numbers (don't claim "99.9999% uptime" without context)
- Use anonymous attributions for testimonials ("VP Engineering, Series B Fintech")
- Use realistic role names for the team
