---
name: seed-city
description: Seed component data (sites, hotels, routes) for a city in the hayahai-travels (TripIntell) project. Use when the user asks to seed a city, add a destination, populate component tables, or prepare a city for Tier 2 itinerary generation. Triggers on /seed-city, "seed [city name]", "add [city] to the component DB", "populate components for [city]".
---

# seed-city Skill

## Purpose

Seeds structured component data for a city into the TripIntell (hayahai-travels) database so the itinerary generation engine can create Tier 2 (day-by-day, component-based) itineraries for that city.

Without seeded components, the AI can only produce Tier 1 (generic narrative) itineraries for that city.

**Project location:** `~/projects-mvp/hayahai-travels/`

---

## Component Types

| Component Type | Table | Description |
|---|---|---|
| Sites | `itinerary_components` (type: `site`) | Tourist attractions, landmarks, activities |
| Hotels | `itinerary_components` (type: `hotel`) | Accommodation options across budget tiers |
| Routes | `city_routes` | Travel times and costs between cities or sites |

---

## Step 1 — Extract Parameters

From the user's message:

| Parameter | Required | Notes |
|---|---|---|
| City name | Yes | e.g. "Boracay", "Cebu City", "Davao" |
| Country | Default: PH | Philippines context assumed unless specified |
| Component types | Default: all | sites + hotels + routes |
| Source | Default: AI-generated | Or "manual" if the user provides data |

---

## Step 2 — Check Existing Data

```bash
cd ~/projects-mvp/hayahai-travels

# Check if city already has components
supabase db --local sql "SELECT city, type, COUNT(*) FROM itinerary_components WHERE city ILIKE '%<city>%' GROUP BY city, type;"

# Check routes
supabase db --local sql "SELECT * FROM city_routes WHERE from_city ILIKE '%<city>%' OR to_city ILIKE '%<city>%';"
```

If components already exist for the city, ask the user whether to:
1. Append new components
2. Replace existing ones
3. Just review what's already there

---

## Step 3 — Generate Component Data

Use the Claude API to generate realistic, accurate component data for the city:

### Sites (10–20 per city)

For each site, generate:
```json
{
  "name": "Chocolate Hills",
  "city": "Bohol",
  "country": "PH",
  "type": "site",
  "category": "nature",
  "description": "Iconic karst limestone hills that turn brown in dry season, giving a chocolate-like appearance.",
  "duration_hours": 2.5,
  "cost_php": 200,
  "budget_tier": "budget",
  "best_time": "morning",
  "coordinates": { "lat": 9.9008, "lng": 124.1408 },
  "tags": ["nature", "scenic", "unesco-candidate", "photography"],
  "rating": 4.6,
  "tips": "Visit early morning to avoid crowds and heat."
}
```

**Categories:** `nature`, `culture`, `food`, `adventure`, `shopping`, `beach`, `heritage`, `entertainment`

**Budget tiers:** `budget` (< ₱200), `mid` (₱200–₱1,000), `luxury` (> ₱1,000)

### Hotels (5–10 per city)

For each hotel, generate:
```json
{
  "name": "Henann Regency Resort & Spa",
  "city": "Boracay",
  "country": "PH",
  "type": "hotel",
  "category": "resort",
  "description": "Beachfront resort on White Beach with pools, spa, and multiple restaurants.",
  "price_per_night_php": 8500,
  "budget_tier": "luxury",
  "stars": 5,
  "coordinates": { "lat": 11.9726, "lng": 121.9234 },
  "amenities": ["pool", "spa", "restaurant", "wifi", "beachfront"],
  "rating": 4.7,
  "booking_url": null
}
```

**Budget tiers:** `budget` (< ₱1,500/night), `mid` (₱1,500–₱5,000), `luxury` (> ₱5,000)

### Routes (transport between cities or to nearby destinations)

For each route, generate:
```json
{
  "from_city": "Manila",
  "to_city": "Boracay",
  "transport_type": "flight+ferry",
  "duration_hours": 2.5,
  "cost_php_min": 2800,
  "cost_php_max": 8000,
  "notes": "Fly to Kalibo or Caticlan; ferry from Caticlan is 30 min, Kalibo requires 2hr bus.",
  "operators": ["Cebu Pacific", "Philippine Airlines", "AirAsia"],
  "frequency": "multiple daily"
}
```

---

## Step 4 — Insert into Database

```bash
cd ~/projects-mvp/hayahai-travels

# Use Supabase CLI or the seed script
node scripts/seed-city.js --city "<city>" --data /tmp/seed-data.json

# Or insert directly via SQL
supabase db --local sql "INSERT INTO itinerary_components (...) VALUES (...);"
```

If a seed script doesn't exist at `scripts/seed-city.js`, create one:

```javascript
// scripts/seed-city.js
const { createClient } = require('@supabase/supabase-js')
const data = require(process.argv[process.argv.indexOf('--data') + 1])

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
)

async function seed() {
  const { error } = await supabase.from('itinerary_components').insert(data.sites)
  if (error) throw error
  console.log(`Seeded ${data.sites.length} sites`)
  // repeat for hotels, routes
}

seed().catch(console.error)
```

---

## Step 5 — Verify

```bash
supabase db --local sql "
SELECT type, COUNT(*), AVG(rating) 
FROM itinerary_components 
WHERE city ILIKE '%<city>%' 
GROUP BY type;
"
```

Report to the user:
- Number of sites, hotels, routes inserted
- Coverage (budget/mid/luxury breakdown)
- Any missing component types that may limit itinerary quality

---

## Rules

- Generated data must be factually accurate — use knowledge of Philippines geography and tourism, not invented data
- Coordinates must be real GPS coordinates for the actual location
- Price ranges should reflect current Philippines market rates (₱)
- Never seed a city without at least 5 sites and 3 hotels at different budget tiers
- Always verify the insert completed without errors before reporting success
