---
name: proposal-tech
description: Generate a filled-in technical proposal for Hayah-AI Systems platform/SaaS engagements. Produces a complete, print-ready A4 HTML document covering solution architecture, platform features, integration requirements, implementation roadmap, SLA, and a companion commercial reference block. Three market variants — Philippines (₱, RA 10173), Malaysia O&G (RM/MYR, PDPA 2010, NDA), Global (USD, GDPR-aware, UNCITRAL). Always pairs with /proposal-comm (commercial). Triggers on "generate a technical proposal", "create a tech proposal", "draft a technical proposal", "new technical proposal", "technical document for proposal", or /proposal-tech.
---

# Technical Proposal Generator — Hayah-AI Systems

Generates a complete, client-specific **technical proposal** for Hayah-AI platform and SaaS engagements. Covers solution architecture, platform features, integration requirements, implementation roadmap, SLA, and a reference block pointing to the companion commercial proposal.

Always pair this with `/proposal-comm` (commercial). The two documents share a proposal number base and cross-reference each other. Generate tech first, note the serial number, then generate the commercial with the matching `-Comm-` number.

All templates are self-contained, print-ready A4 HTML files. Export as PDF via File → Print → Save as PDF (A4, no margins).

---

## Step 1 — Choose a Template

| Client market | Template | Currency | Proposal No. format |
|---|---|---|---|
| Malaysia / SE Asia | `templates/tech-malaysia.html` | RM | Pro-MY-YYYY-NNN-Tech-[Slug] |
| Philippines | `templates/tech-ph.html` | ₱ | Pro-PH-YYYY-NNN-Tech-[Slug] |
| Global / Other | `templates/tech-global.html` | USD | Pro-USD-YYYY-NNN-Tech-[Slug] |

The `[Slug]` is a short CamelCase client identifier, e.g., `Matco`, `EssemCorp`, `PetroClient`.

---

## Skill Root

All paths are relative to `~/.claude/skills/proposal-tech/`.

| Path | Purpose |
|---|---|
| `templates/tech-malaysia.html` | Malaysia / SE Asia O&G — RM, PDPA 2010, 10% WHT, KL courts |
| `templates/tech-ph.html` | Philippines — ₱, RA 10173, BIR EWT, Las Piñas RTC |
| `templates/tech-global.html` | Global (all other markets) — USD, GDPR-aware, UNCITRAL |
| Output | Written to path user specifies; default `~/projects-mvp/hayahai-portfolio/prototype-proposals/` |

---

## Step 2 — Gather Document Metadata

Collect before generating. Do not generate with unfilled placeholders.

| Field | Placeholder | Example |
|---|---|---|
| Tech proposal number | `[PROPOSAL_NUMBER_TECH]` | Pro-MY-2026-003-Tech-ClientSlug |
| Companion commercial number | `[PROPOSAL_NUMBER_COMM]` | Pro-MY-2026-003-Comm-ClientSlug |
| Client / business name | `[CLIENT_NAME]` | Matco Malaysia Sdn Bhd |
| Proposal date | `[DATE]` | 16 May 2026 |
| Valid until | `[VALID_UNTIL]` | 15 July 2026 (60 days) |
| Prepared by | `[AUTHOR]` | Argeo Alecha |
| Confidential data types (closing block) | `[CLIENT_DATA_TYPES]` | operational data, valve readings, maintenance logs |

---

## Step 3 — Gather Product & Solution Details

| Field | Placeholder | Example |
|---|---|---|
| Product name | `[PRODUCT_NAME]` | ValvePulse |
| Product tagline (full) | `[PRODUCT_TAGLINE]` | Actuator Predictive Maintenance Platform |
| Doc-title label | `[DOC_TITLE_LABEL]` | Technical Proposal — Malaysia · Oil & Gas |

> The companion-doc title in Section 8 is rendered from `[PRODUCT_NAME]` + " — Commercial Proposal" — there is no separate `COMPANION_TITLE` placeholder.

---

## Step 4 — Gather Section Content

Row counts below are **fixed** — templates were tuned for A4 layout. Do not assume the template will accept additional rows.

### Section 1 — Executive Summary

| Element | Placeholders |
|---|---|
| Intro paragraph 1 — situation | `[EXEC_SUMMARY_P1]` |
| Intro paragraph 2 — solution + delivery timeline + constraints | `[EXEC_SUMMARY_P2]` |
| Metrics table — **3 rows** | `[METRIC_{1,2,3}_VALUE]` · `[METRIC_{1,2,3}_DELIVERY]` · `[METRIC_{1,2,3}_BASIS]` |
| **Optional** ROI sub-table — **3 driver rows + total** | `[ROI_DRIVER_{1,2,3}]` · `[ROI_BASIS_{1,2,3}]` · `[ROI_VALUE_{1,2,3}]` · `[ROI_TOTAL]` |

> The ROI sub-table is conditional. If no quantified ROI data is available, delete the block (HTML comment marks the start: `<!-- ROI TABLE — include if ROI data is available; delete this section if not -->`). The ROI table also references `[TIER_1_NAME]`, `[TIER_1_POC_MONTHS]`, and `[POC_TOTAL]` already filled elsewhere.

### Section 2 — Current State Assessment

| Element | Placeholders |
|---|---|
| Intro context paragraph | `[CURRENT_STATE_INTRO]` |
| Current state — **6 bullets** | `[CURRENT_STATE_{1..6}]` |
| Required state column label (e.g., "Client / Market Expectations") | `[REQUIRED_STATE_LABEL]` |
| Required state — **6 bullets** | `[REQUIRED_STATE_{1..6}]` |
| Callout heading | `[CALLOUT_HEADING]` |
| Callout body — 1–2 sentences | `[CALLOUT_TEXT]` |

### Section 3 — Solution Architecture

| Element | Placeholders |
|---|---|
| Section intro | `[ARCHITECTURE_INTRO]` |
| Layer 1 (Data Ingestion) | `[LAYER_1_TYPE]` · `[LAYER_1_TITLE]` · `[LAYER_1_ITEM_{1..5}]` |
| Layer 2 (Analytics / AI Engine) | `[LAYER_2_TYPE]` · `[LAYER_2_TITLE]` · `[LAYER_2_ITEM_{1..5}]` |
| Layer 3 (User Layer) | `[LAYER_3_TYPE]` · `[LAYER_3_TITLE]` · `[LAYER_3_ITEM_{1..5}]` |
| Flow heading (e.g., "End-to-End Data Flow") | `[FLOW_HEADING]` |
| Flow steps — **6 steps** | `[STEP_{1..6}_TAG]` · `[STEP_{1..6}_NAME]` · `[STEP_{1..6}_SUB]` |
| Infrastructure row — 4 items | `[INFRA_HOSTING_SUB/VAL]` · `[INFRA_ACCESS_SUB/VAL]` · `[INFRA_SECURITY_SUB/VAL]` · `[INFRA_RETENTION_SUB/VAL]` |

### Section 4 — Platform Features

| Element | Placeholders |
|---|---|
| Section intro | `[FEATURES_INTRO]` |
| Feature 1 — title + subtitle + 1–2 paragraph description | `[F1_TITLE]` · `[F1_SUBTITLE]` · `[F1_DESCRIPTION]` |
| Feature 1 — supporting table (4 columns × 3 rows) | `[F1_COL{1..4}]` headers · `[F1_R{1..3}_C{1..4}]` cells |
| Feature 2 — title + subtitle + description | `[F2_TITLE]` · `[F2_SUBTITLE]` · `[F2_DESCRIPTION]` |
| Feature 2 — supporting bullet list (**5 items**) | `[F2_ITEM_{1..5}]` |
| Feature 3 — title + subtitle + description | `[F3_TITLE]` · `[F3_SUBTITLE]` · `[F3_DESCRIPTION]` |
| Feature 3 — supporting table (2 columns × 4 rows) | `[F3_COL{1,2}]` headers · `[F3_R{1..4}_C{1,2}]` cells |

### Section 5 — Use Case / Module Coverage

| Element | Placeholders |
|---|---|
| Table title | `[COVERAGE_SECTION_TITLE]` |
| Section intro | `[COVERAGE_INTRO]` |
| Column headers — **6 columns, fully configurable** | `[COV_COL{1..6}]` |
| Rows — **6 rows × 6 columns** | `[COV_R{1..6}_C{1..6}]` |
| Closing coverage note (threshold/SIL/compliance) | `[COVERAGE_NOTE]` |

> Default semantic for the 6 columns: Mode/use case · Detection signal · Threshold · Lead time · System action · Applicable scope. Override `[COV_COL_*]` headers if the use case (module coverage, capability matrix, etc.) needs different labels.

### Section 6 — Integration Requirements

| Element | Placeholders |
|---|---|
| Section intro | `[INTEGRATION_INTRO]` |
| POC-required inputs — **5 rows** | `[POC_SOURCE_{1..5}]` · `[POC_FORMAT_{1..5}]` |
| Phase 2 optional integrations — **5 rows** | `[P2_INT_{1..5}]` · `[P2_METHOD_{1..5}]` |
| No-disruption reassurance note | `[NO_DISRUPTION_NOTE]` |
| Inline client reference (used in the integration narrative) | `[CLIENT_NAME]` |

### Section 7 — Implementation Roadmap

| Element | Placeholders |
|---|---|
| Headline timing paragraph (e.g., "3–5 weeks to POC, 8–10 weeks to full deployment") | `[ROADMAP_INTRO]` |
| Timeline rows — **5 rows** | `[TL_{1..5}_WEEK]` · `[TL_{1..5}_NAME]` · `[TL_{1..5}_DESC]` |

### Section 8 — Commercial Proposal Reference

| Element | Placeholders |
|---|---|
| Companion doc description (one sentence) | `[COMPANION_DESC]` |
| Companion doc number | `[PROPOSAL_NUMBER_COMM]` |
| POC investment amount | `[POC_TOTAL]` |
| POC scope note (e.g., "1 platform · 60 actuators · 12 weeks") | `[POC_SCOPE_NOTE]` |
| Tier 1 — name · scope · setup · monthly · total · POC months · total-row note | `[TIER_1_NAME]` · `[TIER_1_SCOPE]` · `[TIER_1_SETUP]` · `[TIER_1_MONTHLY]` · `[TIER_1_TOTAL]` · `[TIER_1_POC_MONTHS]` · `[TIER_1_TOTAL_NOTE]` |
| Tier 2 — name · scope · setup · monthly · total | `[TIER_2_NAME]` · `[TIER_2_SCOPE]` · `[TIER_2_SETUP]` · `[TIER_2_MONTHLY]` · `[TIER_2_TOTAL]` |
| Tier 3 — name · scope · setup · monthly · total | `[TIER_3_NAME]` · `[TIER_3_SCOPE]` · `[TIER_3_SETUP]` · `[TIER_3_MONTHLY]` · `[TIER_3_TOTAL]` |

> Companion-doc title is rendered as `[PRODUCT_NAME] — Commercial Proposal` (no separate placeholder).

### Section 9 — Support & SLA

| Element | Placeholders |
|---|---|
| Section intro | `[SLA_INTRO]` |
| Priority 1 — Safety Critical / Production | `[SLA_P1_LABEL]` · `[SLA_P1_RESPONSE]` · `[SLA_P1_DESC]` |
| Priority 2 — Data & Reporting | `[SLA_P2_LABEL]` · `[SLA_P2_RESPONSE]` · `[SLA_P2_DESC]` |
| Priority 3 — General | `[SLA_P3_LABEL]` · `[SLA_P3_RESPONSE]` · `[SLA_P3_DESC]` |
| Included services — **6 rows** | `[SLA_SVC_{1..6}_ITEM]` · `[SLA_SVC_{1..6}_STD]` |
| Support channels — **6 rows** | `[SLA_CH_{1..6}_NAME]` · `[SLA_CH_{1..6}_DETAIL]` |

### Section 10 — Next Steps

| Element | Placeholders |
|---|---|
| Section intro | `[NEXT_STEPS_INTRO]` |
| Step A — title · description · CTA | `[STEP_A_TITLE]` · `[STEP_A_DESC]` · `[STEP_A_ACTION]` |
| Step B — title · description · CTA | `[STEP_B_TITLE]` · `[STEP_B_DESC]` · `[STEP_B_ACTION]` |
| Step C — title · description · CTA | `[STEP_C_TITLE]` · `[STEP_C_DESC]` · `[STEP_C_ACTION]` |

### Closing — Confidentiality Notice

The closing block uses `[CLIENT_DATA_TYPES]` (e.g., "operational data, maintenance logs, valve readings") together with `[CLIENT_NAME]`. Fill both — the surrounding NDA boilerplate is hardcoded.

---

## Step 5 — Generation Rules

1. Read the selected template in full before generating.
2. Replace every `[BRACKETED]` placeholder with the client-specific value.
3. Remove `<!-- FILL: ... -->` guide comments from the output.
4. **The tech proposal does NOT include pricing detail** — it references the companion commercial proposal number only. Do not add a price breakdown to this document.
5. **No signature block** — signatures are in the commercial proposal only. The confidentiality notice at the end is sufficient.
6. The `[COMPANION_NUMBER]` in the meta block and the companion-ref section must match the commercial proposal number exactly.
7. Write output to `[user-specified path]/[proposal-number].html`.
8. Report the output path. Remind user: Chrome → File → Print → Save as PDF (A4, no margins).

---

## Market-Specific Differences

| | Malaysia (MY) | Philippines (PH) | Global (USD) |
|---|---|---|---|
| Currency | RM | ₱ | $ |
| Privacy law ref | PDPA 2010 + RA 10173 | RA 10173 | GDPR principles + client's law |
| NDA note | Yes — references commercial companion | Yes — references commercial companion | Yes — references commercial companion |
| Governing law ref | Laws of Malaysia; KL courts | Philippines; Las Piñas RTC | Client's jurisdiction; UNCITRAL arbitration |

---

## Coordination with /proposal-comm (Commercial)

The two documents form a set. Key coordination points:
- Serial numbers share the same base: `-Tech-` vs `-Comm-`
- Section 8 (companion-ref block) in the tech must match the commercial title, serial number, and POC investment exactly
- The `doc-meta` block in each doc cross-references the other's serial number
- Both documents share the same product name, client name, date, and valid-until date
