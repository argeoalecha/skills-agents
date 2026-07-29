# Frontend SPA — Pattern Reference

Extracted from `~/projects-mvp/isp-billing/sheets-version/isp-billing-app-sheets.{jsx,html}`
(the SILAGO ISP billing console). The console-styled skeleton is
`assets/app-template.html`.

## Two build forms, one app

- `<app>.jsx` — the source; bundler-deployable later if ever needed.
- `<app>.html` — **zero-build standalone wrapper**: CDN React + ReactDOM (+
  Recharts if charting) + lucide-react UMD + in-browser Babel, the entire app
  inline in one `<script type="text/babel">`. This is the default deploy
  artifact — no Node/npm, opens directly in a browser, deploys anywhere static.

Both files **must be kept in sync on every edit** — same app code, different
wrapper. Verify parity with grep-diffs after edits (config consts especially).
If the project only ever needs the .html, skip the .jsx entirely.

## CDN load order and the lucide shim

lucide-react's UMD bundle reads `window.react` (lowercase) but React's UMD only
sets `window.React`. Immediately after the React scripts, before lucide:

```html
<script>window.react = window.React; window['react-dom'] = window.ReactDOM;</script>
```

Order: React → ReactDOM → shim → (Recharts) → lucide-react → Babel →
`<script type="text/babel">` app code.

## Config consts (top of file, first thing in the app script)

```js
const APPS_SCRIPT_URL = ""; // the deployed /exec URL
const isConfigured = APPS_SCRIPT_URL.startsWith("https://script.google.com/");
const API_TOKEN = ""; // must match the API_TOKEN Script Property; blank = auth off
```

These must be updated in **both** the .jsx and the .html — changing one and
forgetting the other is the classic failure. Never commit a real token to a
public repo.

## API client

```js
async function apiGet(action, params = {}) {
  const qs = new URLSearchParams({ action, token: API_TOKEN, ...params }).toString();
  const res = await fetch(`${APPS_SCRIPT_URL}?${qs}`);
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data;
}

async function apiPost(action, payload = {}) {
  const res = await fetch(APPS_SCRIPT_URL, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify({ action, token: API_TOKEN, ...payload }),
  });
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data;
}
```

- `text/plain` is deliberate — Apps Script Web Apps can't answer a CORS
  preflight; text/plain keeps the POST a "simple request".
- Both throw on `data.error` because Apps Script always returns HTTP 200.
- For must-not-duplicate writes, generate the idempotency id client-side
  (`"PAY" + Date.now()` style) and resend the same id on retry — see the
  backend reference.

## Required UI states

- `SetupScreen` — shown when `isConfigured` is false; tells the operator to
  paste the `/exec` URL into `APPS_SCRIPT_URL`.
- **First-load skeletons** — on the initial fetch (no data yet), render the
  shell (sidebar + topbar) with pearl shimmer blocks that mirror the final
  layout (`SkeletonMetrics`, `SkeletonTable`), not a blank page. Console spec:
  `#e8f4f1` blocks, 1.5s shimmer, respects `prefers-reduced-motion`.
- **Background refreshes** (Refresh button, post-write re-fetch) keep the shell
  visible and show a live "Syncing" badge — the coral-dot pulse (the logo dot,
  reserved for in-progress states) — plus a 16px inline arc spinner in the
  button. The full skeleton is first-load only.
- `ErrorScreen` — message + retry button; shown when the initial load fails
  and there is no data to render.
- Toast for write feedback — Console spec: dark `#0F3836` pill, bottom-right,
  leading status dot, 4s auto-dismiss (danger sticky).

The arc sweep remains the Console loading signature (never a generic spinner);
skeletons and the arc are complementary — skeleton for whole-surface loads,
arc for inline/button-level waits.

## Data flow

- Full `getAll` on mount; full `refresh()` re-fetch after every successful
  write. No pagination, no incremental sync — acceptable at tens-to-hundreds
  of rows; revisit if that grows.
- All state lives in the root component (`useState` per tab's dataset plus UI
  state); derived views (balances, overdue, KPIs) computed client-side with
  `useMemo` — never stored in the Sheet.
- No component splitting until scope demands it — single file is deliberate.

## Styling — hayah-console

App/product screens use the **hayah-console** variant of `/theme-hayahai`
(`hayahai-design/project/themes/hayah-console.json`) unless the client
mandates their own brand (the ISP console itself was rebranded to client
colors — the structure survives a palette swap cleanly):

- Chrome: cream `#faf7f5` page, white cards (xs shadow only — app UI doesn't
  float), dark `#0F3836` sidebar, pearl `#e8f4f1` table headers.
- Type: Geist 400/500/600 everywhere; Space Grotesk only for metric values;
  JetBrains Mono for ids/code. No display font. `tabular-nums` on every cell,
  metric, and timestamp.
- Status: dot + label, never color alone — semantic triplets from the JSON's
  `colors.status`. Coral dot reserved for live states.
- Charts: fixed categorical order `#25A497 #ff6b47 #1E6E66 #ffb5a0 #7a9b96
  #A1E4DB`, on white cards only.
- Tables: 44px rows, sticky pearl header (11px uppercase tracked labels),
  horizontal borders only, numeric columns right-aligned, `#F3FFF9` row hover;
  a `.dense` modifier drops rows to 36px for scan-heavy tabs.
- Cards: default (white, xs shadow), `metric` (label → value → optional
  status-colored delta), and `panel` (pearl, no border — inline help,
  summaries, calc explanations). Buttons: primary / secondary / ghost / cta
  (coral, ≤1 per screen) / destructive (outlined, confirm-gated).
- 4px spacing grid; content padding 24px 32px; focus ring
  `0 0 0 2px cream, 0 0 0 4px #25A497` on every interactive element.

Tailwind via CDN is fine in the zero-build wrapper; put the console tokens in
a `:root` CSS-variable block and use arbitrary-value classes or the provided
component classes (see `assets/app-template.html`).

## Print surfaces (SOA precedent)

For printable documents (statements, receipts): render in an overlay, scope a
`@media print` block to an overlay/printable class pair so only the document —
not the app chrome — prints, auto-fire `window.print()` after fonts load for a
"click → Save as PDF" flow. Browser-print-only, no PDF library — see
`okf/decisions/soa-print-only.md` in the reference project for the rationale.

## Mobile

Collapsible drawer sidebar, top bar, horizontally scrollable tables
(`overflow-x-auto` wrappers). PH-market connectivity: the CDN wrapper loads
~1MB of script — acceptable for an operator tool, not for a consumer surface.
