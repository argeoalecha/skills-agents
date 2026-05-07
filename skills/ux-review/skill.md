---
name: ux-review
description: Heuristic UX evaluation for web apps. Reviews React/Next.js components and live pages against Nielsen's 10 usability heuristics, conversion friction, mobile responsiveness, copy clarity, error handling, empty/loading/success states, dark patterns, and Philippines mobile-market considerations. Produces UX_REVIEW.md with severity-graded findings and appends remediation tasks to TODO.md. Does NOT replace real user research — heuristic review only. Use when the user says "review UX", "usability check", "friction audit", "UX review", "review the signup flow", "is this confusing", "review mobile UX", "conversion review", or as a follow-up after /audit at pre-launch (Stage B). Triggers on /ux-review, "audit UX", "heuristic review".
---

# UX Review — Heuristic Evaluation

A structured heuristic UX evaluation. Reviews component code and (optionally) live pages against Nielsen's 10 heuristics plus mobile-first and Philippines-market considerations. Surfaces friction points, dark patterns, missing states, and confusing copy. Findings flow to `TODO.md` so they cannot be forgotten.

This skill cannot run real user research, A/B tests, or quantitative usage analysis. It is a structured second-pair-of-eyes review.

---

## Workflow Summary

```
Phase 0 — Pre-flight       (target: live URL, dev server, or code-only)
Phase 1 — Scope & Mode     (full app / flow / page / mobile-only)
Phase 2 — Code Review      (read components, pages, layouts, copy)
Phase 3 — Live Walk        (optional — browser-based via agent-browser)
Phase 4 — Heuristic Pass   (Nielsen 10 + dark patterns)
Phase 5 — Mobile & PH      (responsiveness, copy, payment patterns, connectivity)
Phase 6 — TODO Writeback   (append findings to TODO.md)
Phase 7 — Recommendations  (priorities + handoff to /feature-dev)
```

---

## Review Modes

```
Full      — entire public surface (all pages + key flows)
Flow      — one user flow end-to-end (signup, checkout, onboarding)
Page      — single page deep review
Mobile    — same as Full but mobile-only (320px / 375px / 414px)
Heuristic — Nielsen 10 only, no flow analysis
```

Default if user just says "review UX": **Full** at moderate depth.

---

## Phase 0 — Pre-flight

Identify what to review against. In priority order:

1. **Live deployed URL** (preview or staging) — best signal, allows live walk
2. **Local dev server running** — `localhost:3000` or similar — supports live walk
3. **Code only** — no live target, code review of components/pages

```bash
# Detect dev server
lsof -nP -iTCP:3000 -sTCP:LISTEN 2>/dev/null

# Detect Next.js project structure
find . -maxdepth 3 -type d -name "app" -o -name "pages" 2>/dev/null | head -5

# Detect component locations
find . -maxdepth 4 -type d -name "components" 2>/dev/null
```

If live target is available, ask the user once:
> "Run a live walk-through via browser, or code-review only? (live walk catches what code review misses, takes ~3 minutes longer)"

Default to live walk when available.

---

## Phase 1 — Scope & Mode

If user did not specify a flow or page:

1. List the app's routes (from `app/` or `pages/`)
2. Identify critical flows automatically:
   - Auth: `(auth)/login`, `(auth)/signup`, `forgot-password`
   - Onboarding: any `onboarding/*`, `welcome`, `getting-started`
   - Core action: depends on project (booking, checkout, create-trip, etc.)
3. Ask the user to confirm scope (1 question, defaults pre-filled)

Output the agreed scope at the top of `UX_REVIEW.md`.

---

## Phase 2 — Code Review

Read in this order:

1. **Layouts** — global navigation, headers, footers (`app/layout.tsx`, `app/(group)/layout.tsx`)
2. **Page files** for in-scope routes
3. **Components** referenced by those pages
4. **Form schemas** — Zod validators (catch missing inline validation)
5. **Tailwind/theme tokens** — color contrast, spacing consistency
6. **Copy strings** — button labels, error messages, empty states

Note for each:
- Components missing loading/error/empty states
- Forms missing inline validation
- Buttons with vague labels ("OK", "Submit", "Click here")
- Hardcoded English copy with no i18n hooks (relevant for PH bilingual context)
- Raw HTML when semantic elements should be used (`<div onClick>` instead of `<button>`)

---

## Phase 3 — Live Walk (Optional)

If a live URL or dev server is available, use the browser tools to walk the in-scope flows:

```
1. Open the entry point (landing page or login)
2. Execute the happy path of the in-scope flow
3. Take screenshots at each step
4. Trigger error states intentionally:
   - Submit empty form
   - Submit with invalid data (bad email, weak password, etc.)
   - Navigate away mid-flow (browser back, refresh)
   - Slow network (Chrome devtools throttling — Slow 3G)
5. Test mobile viewport (resize to 375px width)
6. Capture console errors / warnings
```

Use `mcp__claude-in-chrome__navigate`, `mcp__claude-in-chrome__form_input`, `mcp__claude-in-chrome__read_page`, `mcp__claude-in-chrome__resize_window` to perform the walk. Save screenshots to `.uxreview/screenshots/` for the report.

---

## Phase 4 — Heuristic Evaluation (Nielsen 10 + Dark Patterns)

Score each heuristic per scoped page/flow: **PASS / MINOR ISSUE / MAJOR ISSUE / FAIL**.

| # | Heuristic | What to look for |
|---|---|---|
| 1 | **Visibility of system status** | Loading states present? Progress bars on multi-step? Submit button shows "Saving…"? |
| 2 | **Match between system and real world** | Plain language, not jargon? Icons recognizable? Mental models match user expectations? |
| 3 | **User control and freedom** | Cancel/back available? Undo for destructive actions? Confirm modals on destructive ops? |
| 4 | **Consistency and standards** | Same word for same thing? Buttons in consistent positions? Platform conventions followed? |
| 5 | **Error prevention** | Form validation prevents bad input? Confirm dialogs for destructive actions? Smart defaults? |
| 6 | **Recognition rather than recall** | User doesn't have to remember info from another screen? Recently-used items surfaced? |
| 7 | **Flexibility and efficiency** | Keyboard shortcuts? Tab order sensible? Power users can move fast? Autocomplete where helpful? |
| 8 | **Aesthetic and minimalist design** | No irrelevant info competing with primary action? Visual hierarchy clear? |
| 9 | **Help users recover from errors** | Errors specific (not "Something went wrong")? Suggest the fix? Highlight the problem field? |
| 10 | **Help and documentation** | Empty states explain what to do? Tooltips on non-obvious controls? Inline help where needed? |

### Dark Patterns to flag

- **Forced continuity** — auto-renew without clear cancel
- **Roach motel** — easy to sign up, hard to delete account
- **Privacy zuckering** — defaults that share more than user expects
- **Confirmshaming** — "No thanks, I don't want to save money"
- **Disguised ads** — content that looks editorial but is paid
- **Hidden costs** — fees revealed only at checkout
- **Bait and switch** — UI looks one way, behaves another
- **Misdirection** — visual emphasis on the answer the company prefers
- **Trick questions** — double negatives in checkboxes

Any dark pattern is automatically a **High** severity finding.

---

## Phase 5 — Mobile & Philippines-Market Check

### Mobile responsiveness

Test at viewport widths: **320px** (small phone), **375px** (iPhone), **414px** (large phone), **768px** (tablet).

Check at each:
- No horizontal scroll
- Tap targets ≥ 44×44 px
- Text readable without zoom (min 16px body)
- Modals fit screen, scrollable inside
- Inputs don't trigger ugly zoom on iOS (font-size ≥ 16px on inputs)
- Sticky headers don't eat too much vertical space
- Bottom nav doesn't overlap content
- Long forms scrollable with keyboard open

### Connectivity resilience (PH context — many users on slow mobile)

- Loading states for every fetch (not just blank screen)
- Skeletons or spinners visible within 200ms
- Optimistic UI on common actions where safe
- Error message + retry on network failure (not just blank or stuck spinner)
- Images use `next/image` with proper sizing
- No autoplay video on mobile data
- Polling intervals reasonable (no 1s polling on mobile data)

### Currency, address, language

- Currency formatted as `₱1,234.00` (Philippine Peso, not `$`)
- Address fields support PH structure: Barangay → Municipality/City → Province → Region
- Phone format supports `+63 9XX XXX XXXX`
- If bilingual: language toggle accessible, language preference persisted
- Date format: `MMM DD, YYYY` or `DD/MM/YYYY` (avoid US `MM/DD/YYYY`)
- No assumption of English-only literacy in critical error/help copy

### Payment patterns

- Cash on Delivery (COD) prominently offered for ecom
- GCash / Maya / bank transfer present alongside card
- Payment method names use familiar PH terms (not "wallet" alone)

---

## Phase 6 — TODO Writeback (Auto)

Append to `TODO.md` as a new phase. Always runs.

```markdown
## Phase X: UX Remediation (YYYY-MM-DD)
Source: UX_REVIEW.md (this run)
Scope: <full app / flow / page>
Mode: <Full / Flow / Page / Mobile / Heuristic>

### Critical (blocks task completion)
- [ ] [UX] "Submit" button never enables on signup form — see UX_REVIEW.md §4.5
- [ ] [UX] Empty cart state shows blank screen with no recovery action

### High (likely to hurt conversion)
- [ ] [UX] Error messages on login are generic ("Invalid credentials") — say what's wrong
- [ ] [DARK-PATTERN] Newsletter checkbox pre-checked on signup
- [ ] [MOBILE] Bottom nav overlaps content on iPhone SE width

### Medium (confusing but recoverable)
- [ ] [UX] Currency shown as $ on a PH-targeted page — use ₱
- [ ] [UX] No loading state on /api/trips fetch — blank for ~2s

### Low (polish)
- [ ] [UX] Button copy "Click here" → use action-oriented label
- [ ] [UX] Tooltip missing on advanced filter
```

Rules:
- Insert as new top-level Phase numbered after the highest existing phase
- Preserve existing TODO content unchanged
- Do not duplicate items (same `[CATEGORY] description — location`)
- Use `[DARK-PATTERN]`, `[MOBILE]`, `[A11Y-OVERLAP]`, `[COPY]`, `[UX]` prefixes for filtering

---

## Phase 7 — Recommendations

After analysis, output:

```
Highest-impact fix: <single concrete change>
Why: <one sentence on why this is highest-leverage — usually conversion or task completion>
Skill: /feature-dev <on the UX TODO> | /audit re-run after fixes

Suggested follow-up:
- Real user testing with 5 users for the in-scope flow (Claude cannot do this — schedule it)
- Re-run /ux-review after fixes to verify resolutions
```

---

## Output: UX_REVIEW.md

Write to project root.

```markdown
# UX Review Report
Date: YYYY-MM-DD
Scope: <full app / flow / page>
Mode: <mode>
Live walk: <yes / no — URL or "code only">
Reviewer: Claude Code (/ux-review)

## Pages / Flows Reviewed
- <route> — <purpose>
- <route> — <purpose>

## Heuristic Scorecard
| # | Heuristic | Score | Findings |
|---|---|---|---|
| 1 | Visibility of system status | PASS / MINOR / MAJOR / FAIL | <one-line> |
| 2 | Match real world | PASS | — |
| ... | ... | ... | ... |

## Findings

### Critical (blocks task completion)
- **[UX]** <description>
  - Where: `app/(auth)/signup/page.tsx` line ~45
  - Evidence: <screenshot ref / code excerpt>
  - Fix direction: <what good looks like>

### High (likely to hurt conversion)
- **[DARK-PATTERN]** <description>
  - ...

### Medium / Low
- ...

## Mobile Review (if applicable)
| Viewport | Issue | Severity |
|---|---|---|
| 320px | Bottom nav overlaps form | High |
| 375px | Headline truncated | Medium |
| 414px | OK | — |

## Philippines-Market Check
- Currency formatting: PASS / FAIL
- Address structure: PASS / FAIL
- Language considerations: PASS / FAIL
- Payment options: PASS / FAIL
- Connectivity resilience: PASS / FAIL

## Dark Patterns Detected
- <pattern> at <location>

## Screenshots
<paths to .uxreview/screenshots/* — only if live walk ran>

## Summary
Critical: N | High: N | Medium: N | Low: N
Highest-impact fix: <description>

## TODO Writeback
Appended N items to TODO.md under "Phase X: UX Remediation (YYYY-MM-DD)"
```

---

## Integration Points

- **Triggered by `/audit`** — Recommended Follow-ups at Stage B (pre-launch) and Stage C → D (post-launch optimization)
- **Feeds `/feature-dev`** — UX Remediation TODO items become feature-dev inputs
- **Verification via `/e2e-test`** — after fixes, run e2e to confirm flows still work
- **Re-run after fixes** — `/ux-review` in re-test mode marks resolved items with `~~strikethrough~~`

---

## Rules

- **Heuristic only** — never claim to validate UX without real users
- **Always include the why** — every finding must explain *why* it's a problem (task failure, conversion drop, error frustration)
- **Severity must reflect impact** — Critical = blocks task; High = significant friction; Medium = confusing but recoverable; Low = polish
- **Dark patterns are always High minimum** — no softening
- **Copy issues count** — confusing copy is a UX problem, not a "nice to have"
- **PH-market checks always run** for projects with PH context (per CLAUDE.md or PRD)
- **TODO writeback always runs** — same closure-loop as `/audit` and `/load-test`
- **Live walk preferred when available** — code review misses real interaction issues
- **Do not propose visual redesigns inline** — surface findings, let `/feature-dev` plan the fix

---

## Out of Scope

- Real user testing / interviews / usability sessions — schedule with actual users
- A/B testing recommendations — needs traffic + analytics
- Quantitative analytics review (heatmaps, session replay) — requires Hotjar/FullStory data
- Brand identity / visual design critique — separate discipline
- Conversion optimization with test data — needs analytics, not heuristics
- Accessibility deep audit — basic a11y is in `/audit` Sub-Agent E; full WCAG audit is a separate engagement
- Information architecture redesign — heuristic review can flag IA pain, not redesign sitemaps

If those are needed, surface as separate follow-up tasks in the report.
