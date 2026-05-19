---
name: seo-leads-gen
description: >
  Run the Hayah-AI SEO agency lead generation pipeline. Scrapes Clutch, DesignRush,
  Google Maps, Legiit, and competitor testimonial pages for Philippine SEO agency
  leads. Scores, tiers (A/B/C), enriches with Hunter.io, and exports a styled
  5-sheet Excel workbook with cold email drafts. Use when the user wants to run
  the SEO leads campaign, find SEO agency clients, or generate outreach for the
  Hayah-AI SEO product. NOT for general business scraping — use /leads-scraper for that.
---

# seo-leads-gen

Trigger on:
- `/seo-leads-gen`
- "run SEO leads campaign" | "find SEO agency leads" | "find agency clients"
- "generate leads for Hayah-AI SEO" | "run the lead pipeline"
- "scrape Clutch" | "scrape DesignRush" | "mine competitor testimonials"
- "find whitelabel SEO prospects" | "find agencies to pitch"

**NOT this skill:** General business scraping from Google Maps/Facebook/Instagram → use `/leads-scraper` instead.

## What this skill does

Runs the pipeline at `~/projects-mvp/seo-leads-gen/scripts/pipeline_runner.py`.

**Sources:**
| Source | Method | Target |
|--------|--------|--------|
| Clutch.co | HTTP + BeautifulSoup | Pre-vetted PH SEO agencies |
| DesignRush | HTTP + BeautifulSoup | Curated PH agency directory |
| Google Maps API | Places REST API | Agencies doing their own local SEO |
| Legiit.com | HTTP + BeautifulSoup | Freelance PH SEO sellers |
| Competitor testimonials | BeautifulSoup + JSON-LD | Warm leads already buying whitelabel SEO |

**Pipeline:** Scrape → Deduplicate → Hunter.io enrichment → Score → Tier A/B/C → Export 5-sheet XLSX + cold email drafts

**Output file:** `~/projects-mvp/seo-leads-gen/leads/hayah_ai_seo_leads_{timestamp}.xlsx`

**5-sheet workbook:**
1. All Leads
2. Tier A - Contact Now (score 4-5)
3. Tier B - Next Week (score 2-3)
4. Email Drafts (Tier A with emails)
5. Source Summary

---

## Lead Scoring Criteria

Every lead is scored 0–5 across these signals, then tiered:

| Signal | Points |
|--------|--------|
| Email found (Hunter.io or scraped) | +1 |
| Website or domain found | +1 |
| Rating >= 4.0 | +1 |
| Reviews >= 10 | +1 |
| Competitor testimonial lead (already buying whitelabel SEO) | +1 |
| Philippines location (Manila, Cebu, Davao, "PH") | +1 |

Score is capped at 5.

**Tiers:**
- **Tier A (score 4–5)** — verified, reachable, likely buying. Contact this week.
- **Tier B (score 2–3)** — partial data or unverified. Worth a second enrichment pass.
- **Tier C (score 0–1)** — directory listing with no contact data. Low-priority.

Deduplication is by `domain` — the same agency found on Clutch and Google Maps becomes one record, inheriting the best data from both sources and keeping the higher source-quality score.

---

## Step 1: Extract parameters

From the user's message, extract:

| Parameter | Default | Notes |
|-----------|---------|-------|
| `sources` | all | clutch, designrush, gmaps, legiit, competitors, all |
| `--limit` | 3 | Pages per source (3 = ~50-100 leads/source) |
| `--no-enrich` | off | Pass if user says "skip enrichment" or no Hunter key |
| `--tier` | all | a / b / c — export only that tier |
| `--min-score` | none | Integer 0–5 — filter out leads below this score |
| `--dry-run` | off | Pass if user says "preview" or "dry run" |

**Source shortcuts:**
| User says… | --sources value |
|---|---|
| "all sources" / "full pipeline" | `all` |
| "just Clutch" | `clutch` |
| "directories only" | `clutch designrush` |
| "Google Maps + Clutch" | `gmaps clutch` |
| "warm leads only" | `competitors` |
| "skip Google Maps" | `clutch designrush legiit competitors` |

---

## Step 2: Show preview and confirm

```
About to run SEO leads pipeline:
  Sources:  {sources}
  Pages:    {limit} per source
  Enrich:   {yes/no} (Hunter.io email lookup)
  Tier:     {tier_filter or "all"}

Command:
  cd ~/projects-mvp/seo-leads-gen && python3 scripts/pipeline_runner.py \
    --sources {sources...} --limit {limit} [flags...]

Proceed? (yes/no)
```

Wait for confirmation before running.

---

## Step 3: Run the command

### Command template

```bash
cd ~/projects-mvp/seo-leads-gen && source .venv/bin/activate && \
python3 scripts/pipeline_runner.py \
  --sources {source1} {source2} ... \
  --limit {max_pages} \
  [--no-enrich] \
  [--tier {a|b|c}] \
  [--min-score {0-5}] \
  [--dry-run]
```

### Prompt → flag mapping

| User says… | Flag |
|---|---|
| "skip enrichment" / "no Hunter" | `--no-enrich` |
| "just Tier A" / "hot leads only" | `--tier a` |
| "score 3 and above" / "min score 3" | `--min-score 3` |
| "preview" / "dry run" | `--dry-run` |
| "more leads" / "deeper scrape" | `--limit 5` |
| "quick test" | `--limit 1` |

---

## Step 4: Report results

After the command completes, report:

```
Pipeline complete.
  Total leads:   {N}
  Tier A:        {N} — contact this week  (score 4-5)
  Tier B:        {N} — contact next week  (score 2-3)
  Tier C:        {N} — low value          (score 0-1)
  With email:    {N}
  Email drafts:  {N}
  Output:        ~/projects-mvp/seo-leads-gen/leads/hayah_ai_seo_leads_{timestamp}.xlsx

Tier A sample:
1. {company} — {domain} — {email} — Score: {score}/5 — Source: {source}
2. {company} — {domain} — {email} — Score: {score}/5 — Source: {source}
...

Sample email draft (first Tier A lead with email):
  Subject: {subject line from Email Drafts sheet}
  Body preview: {first 2-3 lines}
```

---

## Setup: Virtual environment

```bash
cd ~/projects-mvp/seo-leads-gen
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Setup: API keys

Keys are loaded from `~/projects-mvp/seo-leads-gen/.env` or `.env.local`.

**Check:**
```bash
grep -E "GOOGLE_MAPS|HUNTER" ~/projects-mvp/seo-leads-gen/.env 2>/dev/null || \
  echo "No .env found — copy .env.example and fill in keys"
```

**If not set:**
```
GOOGLE_MAPS_API_KEY — get free key at https://console.cloud.google.com
HUNTER_API_KEY      — get free key at https://hunter.io/users/sign_up (25 lookups/month)

cp ~/projects-mvp/seo-leads-gen/.env.example ~/projects-mvp/seo-leads-gen/.env
# Then edit .env with your keys
```

Sources without API keys are automatically skipped with a message. Pipeline continues with remaining sources.

---

## Error handling

| Error | Action |
|-------|--------|
| `GOOGLE_MAPS_API_KEY` not set | GMaps source skipped automatically — other sources continue |
| `HUNTER_API_KEY` not set | Enrichment skipped — leads still scored and exported without emails |
| Clutch/DesignRush returns 0 cards | Site structure may have changed — check CSS selectors in scraper file |
| Import error / module not found | Check venv is activated and `pip install -r requirements.txt` has been run |
| "No leads to export" | All scrapers returned 0 results — check site connectivity and API keys |

---

## Examples

```bash
# Full pipeline - all sources, enrich, export
python3 scripts/pipeline_runner.py

# Quick test - Clutch only, 1 page
python3 scripts/pipeline_runner.py --sources clutch --limit 1

# Warm leads only (competitor testimonials)
python3 scripts/pipeline_runner.py --sources competitors

# Skip Google Maps (no API key)
python3 scripts/pipeline_runner.py --sources clutch designrush legiit competitors

# Export Tier A leads only, no enrichment
python3 scripts/pipeline_runner.py --no-enrich --tier a

# Dry run - preview without making requests
python3 scripts/pipeline_runner.py --dry-run
```

---

## Output files

Results saved to `~/projects-mvp/seo-leads-gen/leads/`:
- `all_leads_raw_{timestamp}.csv` — deduplicated leads before scoring
- `hayah_ai_seo_leads_{timestamp}.xlsx` — full 5-sheet styled workbook

---

---

## Step 5 — Post-Pipeline Outreach Sequence

After exporting, suggest this outreach sequence for Tier A leads. Present this only when the user confirms they're ready to start outreach.

**LinkedIn Boolean searches:**
- `("SEO agency" OR "digital marketing agency") AND (owner OR founder OR CEO) AND Philippines`
- `("whitelabel SEO" OR "white label SEO") AND (owner OR founder) AND Philippines`

**Facebook groups to join:**
- SEO Philippines (~50K), Digital Marketing Philippines (~80K), Agency Owners Philippines (~5K)
- White Label SEO Resellers (~8K) — warmest group, already buying this service type

**Search terms within groups:** "monthly report", "client dashboard", "VA hours", "automate reports"

**DM script:** "Saw your post about [topic] - built something for this. Happy to show you in 15 min?"
