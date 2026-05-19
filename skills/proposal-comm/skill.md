---
name: proposal-comm
description: Generate a filled-in commercial proposal for Hayah-AI Systems platform/SaaS engagements. Produces a complete, print-ready A4 HTML document covering scope of work, package & investment (full pricing, tier comparison, pricing summary), payment schedule, delivery timeline, T&Cs, and dual signature block. Three market variants — Philippines (₱, BIR/EWT, RA 10173), Malaysia O&G (RM/MYR, PDPA 2010, 10% WHT, NDA), Global (USD, GDPR-aware, UNCITRAL). Always pairs with /proposal-tech (technical). Triggers on "generate a commercial proposal", "create a proposal", "draft a proposal", "new proposal", "client proposal", "Malaysia proposal", "commercial document", or /proposal-comm.
---

# Commercial Proposal Generator — Hayah-AI Systems

Generates a complete, client-specific **commercial proposal** for Hayah-AI platform and SaaS engagements. Covers scope of work, full pricing breakdown, package comparison, payment schedule, delivery timeline, terms & conditions, and dual signature block.

Always pair this with `/proposal-tech` (technical). The two documents share a proposal number base and cross-reference each other. Generate the tech proposal first, then this commercial proposal with the matching `-Comm-` number.

All templates are self-contained, print-ready A4 HTML files. Export as PDF via File → Print → Save as PDF (A4, no margins).

---

## Step 1 — Choose a Template

| Client market | Template | Currency | Proposal No. format |
|---|---|---|---|
| Malaysia / SE Asia | `templates/proposal-malaysia.html` | RM | Pro-MY-YYYY-NNN-Comm-[Slug] |
| Philippines | `templates/proposal-template.html` | ₱ | Pro-PH-YYYY-NNN-Comm-[Slug] |
| Global / Other | `templates/proposal-global.html` | USD | Pro-USD-YYYY-NNN-Comm-[Slug] |

The `[Slug]` matches the one used in the companion technical proposal.

---

## Skill Root

All paths are relative to `~/.claude/skills/proposal-comm/`.

| Path | Purpose |
|---|---|
| `templates/proposal-malaysia.html` | Malaysia / SE Asia O&G — RM, PDPA 2010, 10% WHT, KL courts |
| `templates/proposal-template.html` | Philippines — ₱, RA 10173, BIR EWT, Las Piñas RTC |
| `templates/proposal-global.html` | Global (all other markets) — USD, GDPR-aware, UNCITRAL |
| Output | Written to path user specifies; default `~/projects-mvp/hayahai-portfolio/prototype-proposals/` |

---

## Step 2 — Gather Document Metadata

| Field | Placeholder | Example |
|---|---|---|
| Commercial proposal number | `[PROPOSAL_NUMBER_COMM]` | Pro-MY-2026-003-Comm-ClientSlug |
| Companion technical number | `[PROPOSAL_NUMBER_TECH]` | Pro-MY-2026-003-Tech-ClientSlug |
| Client / business name | `[CLIENT_NAME]` | Matco Malaysia Sdn Bhd |
| Contact person | `[CONTACT_PERSON]` | Name, Position |
| Industry | `[INDUSTRY]` | Oil & Gas · Valve & Actuator Maintenance Services |
| Contact email | `[CONTACT_EMAIL]` | contact@clientcompany.com |
| Proposal date | `[DATE]` | 16 May 2026 |
| Valid until | `[VALID_UNTIL]` | 15 July 2026 (60 days) |
| Prepared by | `[AUTHOR]` | Argeo Alecha |
| Estimated start date | `[START_DATE]` | 2 June 2026 |

---

## Step 3 — Gather Product & Solution Details

| Field | Placeholder | Example |
|---|---|---|
| Product name | `[PRODUCT_NAME]` | ValvePulse |
| Product tagline | `[PRODUCT_TAGLINE]` | Actuator Predictive Maintenance Platform |
| Doc-title label | `[DOC_TITLE_LABEL]` | Commercial Proposal — Malaysia · Oil & Gas |
| Package card name (Section 5) — proposed tier, branded | `[PACKAGE_NAME]` | ValvePulse POC — Tier 1 |
| Package card tagline (Section 5) — scope one-liner | `[PACKAGE_TAGLINE]` | 1 platform · 60 actuators · 12-week program · no hardware change |

---

## Step 4 — Gather Section Content

Row counts below are **fixed** — templates were tuned for A4 layout. Do not assume the template will accept additional rows.

### Section 1 — Executive Summary

| Element | Placeholders |
|---|---|
| Intro paragraph 1 — what the POC delivers, timeline, key constraints | `[EXEC_SUMMARY_P1]` |
| Intro paragraph 2 — Year 1 ROI figure, ROI multiple, payback logic | `[EXEC_SUMMARY_P2]` |

### Section 2 — Current State Assessment

| Element | Placeholders |
|---|---|
| Intro context paragraph | `[CURRENT_STATE_CONTEXT]` |
| Pain points table — **3 rows** | `[CS_AREA_{1..3}]` · `[CS_METHOD_{1..3}]` · `[CS_IMPACT_{1..3}]` · `[CS_PRIORITY_{1..3}]` (High/Medium/Low) |
| Footnote — italicised competitive-risk sentence | `[CURRENT_STATE_FOOTNOTE]` |

### Section 3 — Proposed Solution

| Element | Placeholders |
|---|---|
| Solution paragraph 1 — what the platform does, scope, no-disruption note | `[SOLUTION_P1]` |
| Solution paragraph 2 — coverage details | `[SOLUTION_P2]` |
| Key outcomes — **6 bullets** (two-column layout) | `[OUTCOME_{1..6}]` |

### Section 4 — Scope of Work

| Element | Placeholders |
|---|---|
| Deliverables table — **7 rows** (Deliverable · Description) | `[SOW_DELIV_{1..7}]` · `[SOW_DESC_{1..7}]` |
| Excluded items — **4 bullets** | `[EXCLUDED_{1..4}]` |

NDA notice and "Status" column are hardcoded in the template.

### Section 5 — Package & Investment

This is the densest section. Three distinct content blocks: **(a) package card**, **(b) tier comparison**, **(c) pricing summary + payment schedule + post-POC**.

#### (a) Package card (highlighting the proposed tier)

| Element | Placeholders |
|---|---|
| POC total amount (also reused in pricing summary) | `[POC_TOTAL]` |
| Price note under total (e.g., "12-week total · RM 38k setup + RM 12k/month") | `[POC_PRICE_NOTE]` |
| "What's included" bullets — **7 items** | `[PKG_INCLUDE_{1..7}]` |
| "Why start here" bullets — **5 items** | `[PKG_WHY_{1..5}]` |

#### (b) Tier comparison table

| Element | Placeholders |
|---|---|
| Tier 1 — name, scope, setup, monthly, total | `[TIER_1_NAME]` · `[TIER_1_SCOPE]` · `[TIER_1_SETUP]` · `[TIER_1_MONTHLY]` · `[TIER_1_TOTAL]` |
| Tier 2 — name, scope, setup, monthly, total | `[TIER_2_NAME]` · `[TIER_2_SCOPE]` · `[TIER_2_SETUP]` · `[TIER_2_MONTHLY]` · `[TIER_2_TOTAL]` |
| Tier 3 — name, scope, setup, monthly, total | `[TIER_3_NAME]` · `[TIER_3_SCOPE]` · `[TIER_3_SETUP]` · `[TIER_3_MONTHLY]` · `[TIER_3_TOTAL]` |
| Comparison feature rows — **5 row labels** | `[TIER_FEATURE_{1..5}]` |
| Comparison feature cells — **5 rows × 3 tiers** | `[T1_F{1..5}]` · `[T2_F{1..5}]` · `[T3_F{1..5}]` |

> **`TIER_{1,2,3}_SCOPE` must match the tech proposal's Section 8 tier summary exactly** — same scope wording in both documents.

#### (c) Pricing summary, payment schedule, post-POC

| Element | Placeholders |
|---|---|
| Pricing summary line 1 — description (uses `[TIER_1_SETUP]` amount) | `[PRICING_LINE_1_DESC]` |
| Pricing summary line 2 — description + amount | `[PRICING_LINE_2_DESC]` · `[PRICING_LINE_2_AMOUNT]` |
| Pricing total label (e.g., "Total 12-Week POC Investment") | `[PRICING_TOTAL_LABEL]` |
| Payment milestone 1 — label · pct · note (include amount in note) | `[PAYMENT_M1_LABEL]` · `[PAYMENT_M1_PCT]` · `[PAYMENT_M1_NOTE]` |
| Payment milestone 2 — label · pct · note | `[PAYMENT_M2_LABEL]` · `[PAYMENT_M2_PCT]` · `[PAYMENT_M2_NOTE]` |
| Payment milestone 3 — label · pct · note | `[PAYMENT_M3_LABEL]` · `[PAYMENT_M3_PCT]` · `[PAYMENT_M3_NOTE]` |
| Post-POC continuation sentence (monthly SaaS + notice period) | `[POST_POC_CONTINUATION]` |
| Payment methods callout block | `[PAYMENT_METHODS_CALLOUT]` |

> Default milestone split is `50% / 25% / 25%` with M1 label "Upon Agreement" — fill those defaults unless the deal terms differ. SST/EWT/WHT context lines are hardcoded per market template.

### Section 6 — Delivery Timeline

| Element | Placeholders |
|---|---|
| Header dates line (Start · Platform go-live · 12-week POC end) | `[TIMELINE_HEADER_DATES]` |
| Timeline rows — **5 rows** (Week label · Milestone name · Description) | `[TL_{1..5}_WEEK]` · `[TL_{1..5}_NAME]` · `[TL_{1..5}_DESC]` |

### Section 7 — Terms & Conditions

| Element | Placeholders |
|---|---|
| Validity term | `[TERM_VALIDITY]` |
| Project start trigger | `[TERM_PROJECT_START]` |
| Post-POC term (monthly rate + notice period) | `[TERM_POST_POC]` |
| Client responsibilities | `[TERM_CLIENT_RESP]` |

Standard boilerplate (cancellation, WHT/EWT note per market, governing law, dispute resolution) is hardcoded per market template.

### Section 8 — Acceptance

| Element | Placeholders |
|---|---|
| Hayah-AI signatory | Hardcoded "Argeo Alecha, Founder" — pulls from `[AUTHOR]` for the header only |
| Client signatory — name, position, client name | Hardcoded `[Authorised Signatory Name]` / `[Position]` / `[CLIENT_NAME]` with `.placeholder-text` class |

Per generation rule 4, when the client signatory is actually known: replace these placeholders **and** remove the `.placeholder-text` class from the surrounding `div`.

---

## Step 5 — Package Tiers & Rates

### Malaysia (RM) — Platform / SaaS Engagements

| Tier | Setup | Monthly SaaS | Extra revisions |
|---|---|---|---|
| Tier 1 — POC | RM 30,000 – RM 50,000 | RM 8,000 – RM 15,000 | RM 500/hr |
| Tier 2 — Multi-site | RM 40,000 – RM 65,000 | RM 18,000 – RM 28,000 | RM 500/hr |
| Tier 3 — Enterprise | RM 55,000 – RM 80,000 | RM 30,000 – RM 45,000 | RM 500/hr |

### Philippines (₱) — Platform / SaaS Engagements

| Tier | Setup | Monthly SaaS | Extra revisions |
|---|---|---|---|
| Tier 1 — POC | ₱150,000 – ₱250,000 | ₱40,000 – ₱70,000 | ₱2,000/hr |
| Tier 2 — Multi-site | ₱200,000 – ₱350,000 | ₱80,000 – ₱130,000 | ₱2,000/hr |
| Tier 3 — Enterprise | ₱280,000 – ₱450,000 | ₱150,000 – ₱220,000 | ₱2,000/hr |

### Global (USD) — Platform / SaaS Engagements

| Tier | Setup | Monthly SaaS | Extra revisions |
|---|---|---|---|
| Tier 1 — POC | $8,000 – $14,000 | $2,500 – $4,500 | $150/hr |
| Tier 2 — Multi-site | $12,000 – $20,000 | $5,500 – $9,000 | $150/hr |
| Tier 3 — Enterprise | $18,000 – $28,000 | $10,000 – $16,000 | $150/hr |

---

## Step 6 — Generation Rules

1. Read the selected template in full before generating.
2. Replace every `[BRACKETED]` placeholder with the client-specific value.
3. Remove `<!-- FILL: ... -->` guide comments from the output.
4. Remove the `.placeholder-text` class from filled-in signature fields.
5. The `[PROPOSAL_NUMBER_TECH]` reference in the meta block must match the companion technical proposal exactly.
6. **Never leave a `[BRACKETED]` placeholder unfilled** — ask the user for the missing value rather than generating with visible placeholders.
7. Write output to `[user-specified path]/[proposal-number].html`.
8. Report the output path. Remind user: Chrome → File → Print → Save as PDF (A4, no margins).

---

## Market-Specific Differences

| | Malaysia (MY) | Philippines (PH) | Global (USD) |
|---|---|---|---|
| Currency | RM | ₱ | $ |
| Payment method | PayPal + Maybank/CIMB/Public Bank | GCash + BDO/BPI/UnionBank | Wise (preferred) + PayPal + SWIFT |
| Tax note | 10% WHT under ITA 1967 (if applicable) + SST self-assess | 2% EWT; client issues BIR Form 2307 | VAT/GST/WHT — client's jurisdiction |
| Privacy law | PDPA 2010 + RA 10173 | RA 10173 | GDPR principles + client's law |
| Governing law | Laws of Malaysia; KL courts | Philippines; Las Piñas RTC | Philippines law + UNCITRAL arbitration |
| NDA notice block | Yes — include | Yes — include | Yes — include if client data shared |
| Messaging | WhatsApp | Messenger | Email / web |

---

## Coordination with /proposal-tech (Technical)

- The two documents form a matching set — same serial number base, `-Tech-` vs `-Comm-`
- The commercial doc's `doc-meta` block must reference the technical proposal number under "Technical doc:"
- The tech proposal's companion-ref block must reference this commercial doc's title, number, and POC total
- Both documents share the same product name, client name, date, and valid-until date
- The tier summary in the tech proposal's Section 8 must match the pricing in this commercial doc's Section 5 exactly
