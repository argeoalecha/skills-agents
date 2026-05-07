---
name: leads-scraper
description: >
  Scrape business and profile data from Google Maps, Facebook, and Instagram.
  Use when the user asks to scrape, find leads, or extract data from Google Maps
  (by category + location), Facebook pages (by slug), or Instagram profiles (by username).
  Triggers on /leads-scraper, "scrape [X] in [Y]", "find [business type] in [city]",
  "get leads for [X]", "scrape Google Maps", "scrape Facebook pages",
  "scrape Instagram accounts", "scrape these IG profiles", "get data from Facebook".
---

# leads-scraper

**NOT this skill:** Clutch/DesignRush/Legiit directory scraping, lead scoring/tiering, cold email drafts, or SEO agency campaign → use `/seo-leads-gen` instead.

Trigger on:
- `/scrape` (any platform)
- "scrape [X] in [Y]" | "find [business type] in [city]" | "get leads for [X]" | "scrape Google Maps" | "find [X] on Google Maps"
- "scrape Facebook [pages/page]" | "scrape these FB pages" | "get data from Facebook"
- "scrape Instagram [profiles/accounts]" | "scrape these IG accounts" | "get data from Instagram"

## What this skill does

Runs scrapers from `~/projects-mvp/scraper-skill/`:
- **Google Maps** → `scripts/pipeline_runner.py` — search by category + location
- **Facebook** → `scripts/social_pipeline_runner.py --platform fb` — scrape public pages by slug
- **Instagram** → `scripts/social_pipeline_runner.py --platform ig` — scrape public profiles by username

**Detect the platform first** from the user's message, then follow the matching section below.

Pipeline: Query builder → Playwright scraper → Website enrichment → Export (JSON/CSV/XLSX) → optional Google Sheets upload.

**Capabilities:**
- **Google Maps enrichment** crawls business websites (homepage + /contact, /about pages) for emails, phones, and social links. Falls back to common email patterns (info@domain) when no email is found on the site.
- **Facebook scraper** navigates both the main page and /about tab for structured contact data (phone, email, address, hours). Includes retry with exponential backoff.
- **Instagram scraper** intercepts API responses for richer profile data (business email, phone, address, category). Extracts from embedded JSON and bio text. Includes retry with exponential backoff.

Working directory: `~/projects-mvp/scraper-skill/`

---

# GOOGLE MAPS SCRAPER

Entrypoint: `python3 scripts/pipeline_runner.py`

## Step 1: Extract parameters

From the user's message, extract:

| Parameter | Default | Notes |
|---|---|---|
| `search` | required | Business type keyword (e.g. "dental clinics", "restaurants") |
| `location` | required | City/province — auto-append ", PH" if Philippines context |
| `limit` | 30 | Max results. Cap at 200 for safety. |
| `min_rating` | none | Float 0–5 (e.g. 4.0, 4.5) |
| `min_reviews` | none | Integer (e.g. 50) |
| `enrich` | false | Enable if user says "with emails", "with website data", "enrich", "full data", "with contacts", "find emails" |
| `format` | xlsx | `json` / `csv` / `xlsx` / `all` |
| `sort` | rating | `rating` / `reviews` / `name` |
| `--sheets` | false | Enable if user says "to Google Sheets", "in Sheets", "upload to Sheets" |
| `--sheets-id` | none | Optional existing spreadsheet ID |
| `--sheets-title` | auto | Default: "{search} - {timestamp}" |

Philippines location rule: if the location is any PH city, province, or region (Manila, Cebu, Makati, Davao, Quezon City, Metro Manila, BGC, Taguig, etc.), append ", PH" if not already present.

---

## Step 2: Show preview and confirm

Before running, show the user:

```
About to scrape:
  Search: {search} in {location}
  Limit: {limit}
  Enrich: {yes/no}
  Format: {format}
  Google Sheets: {yes/no}

Command:
  cd ~/projects-mvp/scraper-skill && python3 scripts/pipeline_runner.py \
    --search "{search}" --location "{location}" --limit {limit} [flags...]

Proceed? (yes/no)
```

Wait for confirmation before running.

---

## Step 3: Run the command

### Command template

```bash
cd ~/projects-mvp/scraper-skill && python3 scripts/pipeline_runner.py \
  --search "{search}" \
  --location "{location}" \
  --limit {limit} \
  [--min-rating {min_rating}] \
  [--min-reviews {min_reviews}] \
  [--enrich] \
  --format {format} \
  --sort {sort} \
  [--sheets] \
  [--sheets-id "{sheets_id}"] \
  [--sheets-title "{sheets_title}"]
```

Only include optional flags when they have values.

### Prompt → flag mapping

| User says… | Flag |
|---|---|
| "get me 50 businesses" | `--limit 50` |
| "as a spreadsheet" / "xlsx" | `--format xlsx` |
| "as CSV" | `--format csv` |
| "all formats" | `--format all` |
| "with emails" / "with website data" / "enrich" | `--enrich` |
| "rated 4+" / "min rating 4" | `--min-rating 4.0` |
| "minimum 100 reviews" | `--min-reviews 100` |
| "sort by reviews" | `--sort reviews` |
| "sort by name" | `--sort name` |
| "to Google Sheets" / "upload to Sheets" | `--sheets` |
| "show browser" / "headed" | `--headed` |

---

## Step 4: Report results

After the command completes, report:

```
Scraped {N} businesses
Saved to: {output_file_path(s)}
[Google Sheets: {url}]

Top 5:
1. {name} — {rating}★ ({review_count} reviews)
   {address}
...
```

---

## Setup: Virtual environment

The project uses a venv. Activate before running:

```bash
cd ~/projects-mvp/scraper-skill
source .venv/bin/activate  # if venv exists
python3 scripts/pipeline_runner.py ...
```

If not set up:

```bash
cd ~/projects-mvp/scraper-skill
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

---

## Setup: Google Sheets (one-time)

Required only when `--sheets` is used.

**Check first:**
```bash
echo $GOOGLE_SHEETS_CREDENTIALS_PATH
```

**If not set:**
```
Google Sheets upload requires a service account JSON.

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Create a service account → download JSON key
3. Enable Google Sheets API and Google Drive API in your project
4. Run: export GOOGLE_SHEETS_CREDENTIALS_PATH=~/path/to/service-account.json
5. Add to ~/.zshrc to persist

Then retry the scrape with --sheets.
```

Never proceed with `--sheets` if the env var is unset — surface the setup instructions instead.

---

## Error handling

| Error | Action |
|---|---|
| "No results found" | Suggest broader search or different location |
| "Google Maps blocked" | Tell user to wait 5–10 minutes and retry |
| "playwright not found" | Run setup (venv + `pip install -r requirements.txt` + `playwright install chromium`) |
| "Missing GOOGLE_SHEETS_CREDENTIALS_PATH" | Surface Google Sheets setup instructions |
| Import errors | Check venv is activated and deps installed |

---

## Examples

```bash
# Basic — 30 restaurants in Manila, XLSX output
python3 scripts/pipeline_runner.py --search "restaurants" --location "Manila, PH" --format xlsx

# Lead generation — 100 dental clinics in Cebu, with email enrichment
python3 scripts/pipeline_runner.py --search "dental clinics" --location "Cebu City, PH" \
  --limit 100 --enrich --min-rating 4.0 --format xlsx

# Market research — coffee shops sorted by review count
python3 scripts/pipeline_runner.py --search "coffee shops" --location "BGC, Taguig, PH" \
  --limit 50 --enrich --sort reviews --format csv

# Upload to Google Sheets
python3 scripts/pipeline_runner.py --search "hotels" --location "Boracay, PH" \
  --limit 30 --format xlsx --sheets --sheets-title "Boracay Hotels"

# Replay a previous run
python3 scripts/pipeline_runner.py --config scrape_output/run_record_20260309_120000.json
```

---

## Output files

Results are saved to `~/projects-mvp/scraper-skill/scrape_output/`:
- `businesses_{timestamp}.json` — full nested JSON
- `businesses_{timestamp}.csv` — flat CSV, Excel-compatible
- `businesses_{timestamp}.xlsx` — styled spreadsheet with frozen headers
- `run_record_{timestamp}.json` — replay config

---

# FACEBOOK SCRAPER

Entrypoint: `python3 scripts/social_pipeline_runner.py --platform fb`

## Step 1: Extract parameters

From the user's message, extract:

| Parameter | Default | Notes |
|---|---|---|
| `slugs` | required | Facebook page slugs or full FB URLs (e.g. `mycafe`, `facebook.com/mycafe`) |
| `format` | xlsx | `json` / `csv` / `xlsx` / `all` |
| `min_followers` | none | Integer filter |
| `sort` | followers | `followers` / `name` |
| `session_file` | none | Path to cookie JSON — ask user if they want authenticated scraping |

If the user provides full Facebook URLs, extract the slug from the URL.
If the user provides a file of pages, use `--input {file}`.

## Step 2: Show preview and confirm

```
About to scrape Facebook pages:
  Pages:    {slug1}, {slug2}, ...
  Format:   {format}
  Filter:   {min_followers? or "none"}
  Auth:     {session_file or "none (public data only)"}

Command:
  cd ~/projects-mvp/scraper-skill && python3 scripts/social_pipeline_runner.py \
    --platform fb --slugs {slugs...} [flags...]

Proceed? (yes/no)
```

## Step 3: Run the command

```bash
cd ~/projects-mvp/scraper-skill && source .venv/bin/activate && \
python3 scripts/social_pipeline_runner.py \
  --platform fb \
  --slugs {slug1} {slug2} ... \
  --format {format} \
  [--min-followers {min_followers}] \
  [--sort {sort}] \
  [--session-file {session_file}] \
  [--headed]
```

Or from a file:
```bash
  --input {file_path}
```

### Prompt → flag mapping

| User says… | Flag |
|---|---|
| "scrape facebook.com/mycafe" | `--slugs mycafe` |
| "from this list / from a file" | `--input {file}` |
| "as a spreadsheet" | `--format xlsx` |
| "1000+ followers only" | `--min-followers 1000` |
| "I'm logged in / use my cookies" | `--session-file cookies.json` |
| "show browser" | `--headed` |

## Step 4: Report results

```
Scraped {N} Facebook pages
Saved to: {output_file_path(s)}

Top 5:
1. {name} (@{slug}) — {follower_count} followers
   Category: {category}
   Website: {website}
...
```

## Error handling

| Error | Action |
|---|---|
| Login wall detected | Tell user: "Facebook is showing a login wall for this page. Pass `--session-file` with your browser cookies for full data." |
| confidence_score = 0.0 | The page may be private or require login — surface this to the user |
| Blocked / captcha | Tell user to wait 10 minutes and retry with `--headed` to see what's happening |
| No results | Verify the page slug is correct by checking `facebook.com/{slug}` in browser |

---

# INSTAGRAM SCRAPER

Entrypoint: `python3 scripts/social_pipeline_runner.py --platform ig`

## Step 1: Extract parameters

From the user's message, extract:

| Parameter | Default | Notes |
|---|---|---|
| `slugs` | required | Instagram usernames or full IG URLs (e.g. `mycafe_ph`, `@mycafe_ph`, `instagram.com/mycafe_ph`) |
| `format` | xlsx | `json` / `csv` / `xlsx` / `all` |
| `min_followers` | none | Integer filter |
| `sort` | followers | `followers` / `name` |
| `session_file` | none | Path to cookie JSON — ask user if they want authenticated scraping |

Strip leading `@` from usernames automatically. If the user provides full Instagram URLs, extract just the username.

## Step 2: Show preview and confirm

```
About to scrape Instagram profiles:
  Accounts: @{username1}, @{username2}, ...
  Format:   {format}
  Filter:   {min_followers? or "none"}
  Auth:     {session_file or "none (public profiles only)"}

Command:
  cd ~/projects-mvp/scraper-skill && python3 scripts/social_pipeline_runner.py \
    --platform ig --slugs {usernames...} [flags...]

Proceed? (yes/no)
```

## Step 3: Run the command

```bash
cd ~/projects-mvp/scraper-skill && source .venv/bin/activate && \
python3 scripts/social_pipeline_runner.py \
  --platform ig \
  --slugs {username1} {username2} ... \
  --format {format} \
  [--min-followers {min_followers}] \
  [--sort {sort}] \
  [--session-file {session_file}] \
  [--headed]
```

Or from a file:
```bash
  --input {file_path}
```

### Prompt → flag mapping

| User says… | Flag |
|---|---|
| "scrape @mycafe_ph" | `--slugs mycafe_ph` |
| "scrape instagram.com/mycafe" | `--slugs mycafe` |
| "from a file" | `--input {file}` |
| "as a spreadsheet" | `--format xlsx` |
| "1000+ followers only" | `--min-followers 1000` |
| "I'm logged in / use my cookies" | `--session-file cookies.json` |
| "show browser" | `--headed` |

## Step 4: Report results

```
Scraped {N} Instagram profiles
Saved to: {output_file_path(s)}

Top 5:
1. @{username} ({display_name}) — {follower_count} followers
   Bio: {bio_preview}
   Link: {website}
...
```

## Error handling

| Error | Action |
|---|---|
| Login wall detected | Tell user: "Instagram is showing a login wall. Pass `--session-file` with your browser cookies." |
| confidence_score = 0.0 | Profile may be private or login-gated |
| not_found | Username doesn't exist — verify spelling |
| Blocked / try again later | Instagram rate-limited the scraper. Wait 15+ minutes. Try `--headed` to diagnose. |

## Output files (FB & IG)

Results saved to `~/projects-mvp/scraper-skill/scrape_output/`:
- `fb_{timestamp}.json / .csv / .xlsx` — Facebook pages
- `ig_{timestamp}.json / .csv / .xlsx` — Instagram profiles
- `run_record_{timestamp}.json` — replay config (use with `--config`)
