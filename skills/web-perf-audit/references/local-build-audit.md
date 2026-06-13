# Local Build Audit (Vite + Next.js)

Run when the repo is available — before deploy, or when an online audit found JS over budget. Online audits measure delivered weight; only a local build audit explains *what's inside* the chunks.

## Budgets (framework-agnostic)

| Target | Marketing/portfolio site | App/dashboard |
|---|---|---|
| Total JS (raw) | <400KB | <800KB |
| Largest chunk | <150KB | <250KB |
| Initial-load JS (entry + sync imports) | <200KB | <350KB |
| CSS | <60KB | <120KB |

## Vite projects

### 1. Build with size report

```bash
npm run build   # vite build prints per-chunk sizes + gzip by default
```

Read the output table directly — flag any chunk over budget. For Vite 8 / Rolldown (`rolldown-vite`), output format is the same; Rolldown builds are faster but produce comparable chunking, so the same budgets apply.

### 2. Visual bundle analysis

```bash
npm i -D rollup-plugin-visualizer
```

```js
// vite.config.js
import { visualizer } from 'rollup-plugin-visualizer';
export default {
  plugins: [
    visualizer({ filename: 'stats.html', gzipSize: true, brotliSize: true, template: 'treemap' }),
  ],
};
```

`npm run build` → open `stats.html`. Works with both Rollup and Rolldown pipelines. Alternative for quick CLI-only analysis: `npx vite-bundle-visualizer`.

In sandboxed/headless environments: parse `stats.html` is impractical — instead use `visualizer({ template: 'raw-data', filename: 'stats.json' })` and inspect the JSON with Python to rank modules by size.

### 3. Common Vite bloat patterns

1. **Barrel imports from icon/UI libraries** — `import { X } from 'lucide-react'` is fine (tree-shakes), but `import * as Icons` or dynamic icon lookup defeats it. Check stats for the icon lib's total share.
2. **Moment.js / full lodash** — replace with `date-fns`/`dayjs` and `lodash-es` per-function imports.
3. **No manual chunking** — one giant vendor chunk. Split:
   ```js
   build: {
     rollupOptions: {
       output: {
         manualChunks: {
           react: ['react', 'react-dom'],
           charts: ['recharts'],   // heavy libs get own lazy-loadable chunk
         },
       },
     },
   }
   ```
   (Same `manualChunks` API in Rolldown.)
4. **Eager-loaded routes** — use `React.lazy(() => import('./pages/X'))` / dynamic `import()` per route so route code splits.
5. **Dev-only deps in prod** — check stats for testing/devtools libs that leaked into the bundle.

### 4. Test the production build locally

```bash
npm run build && npm run preview   # serves dist/ on :4173
```

Then run the online audit script against it:

```bash
bash scripts/audit.sh http://localhost:4173
```

This validates the *built output* (chunk count, sizes, HTML weight, compression behavior) before deploy. Note: `vite preview` is a plain static server — TTFB/caching results are NOT representative of production CDN behavior; only payload/asset sections are meaningful locally. Never benchmark `vite dev` — dev serves unbundled ESM and is meaningless for perf.

### 5. Compression check

Vite doesn't pre-compress by default; hosts (Vercel/Netlify/CF) compress on the fly. For generic hosts, pre-compress:

```bash
npm i -D vite-plugin-compression2
```

```js
import { compression } from 'vite-plugin-compression2';
plugins: [compression({ algorithms: ['brotliCompress', 'gzip'] })]
```

## Next.js projects

### 1. Bundle analyzer

```bash
npm i -D @next/bundle-analyzer
```

```js
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({ enabled: process.env.ANALYZE === 'true' });
module.exports = withBundleAnalyzer({ /* config */ });
```

```bash
ANALYZE=true npx next build
```

Headless environments: read the build output table instead — `next build` prints First Load JS per route. Any route >200KB First Load JS needs attention.

### 2. Route static/dynamic audit

In `next build` output:
- `○ (Static)` — prerendered, cacheable, fast
- `ƒ (Dynamic)` — server-rendered per request → cold TTFB risk

Routes that should be static but show `ƒ`: search for `cookies()`, `headers()`, `searchParams`, `fetch(..., { cache: 'no-store' })` in that route's tree — any of these opts the route out of static rendering.

### 3. Common Next.js bloat patterns

1. Client components too high in the tree — `'use client'` on a layout drags everything into the client bundle. Push it to leaves.
2. Heavy libs in shared layout — charting/animation in `layout.tsx` loads on every route. Move to the routes that use them + `next/dynamic`.
3. `next/dynamic` with `ssr: false` for browser-only widgets (maps, editors, carousels).
4. Fonts: `next/font` with `subsets: ['latin']`, ≤2 typefaces × ≤2 weights for marketing sites. Mono fonts only in code-block components, not preloaded globally.
5. RSC inline payload >80KB (App Router, visible in online audit) — too much content serialized on one route; split routes or trim server→client props.

## Deliverable

Report local findings in the same prioritized format as online audits, each item naming the module/import responsible (from stats), the fix, and expected KB savings. Then deploy and re-run the online audit to confirm delivered weight dropped.
