# TripIntell API Conventions

## File Location

All API routes live in `src/app/api/`. Each route is a directory with a `route.ts` file:

```
src/app/api/
├── recommendations/
│   └── route.ts              # /api/recommendations
├── trips/
│   └── [id]/
│       ├── route.ts          # /api/trips/[id]
│       └── collaborators/
│           └── route.ts      # /api/trips/[id]/collaborators
└── webhooks/
    └── stripe/
        └── route.ts          # /api/webhooks/stripe
```

## HTTP Method Semantics

| Method | When | Status Code |
|--------|------|-------------|
| GET    | Read/list resources | 200 |
| POST   | Create resource | 201 |
| PATCH  | Partial update | 200 |
| PUT    | Full replacement (rare) | 200 |
| DELETE | Delete (use soft delete) | 204 |

Dynamic segment params are accessed via the second argument:

```typescript
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
```

## Standard Response Shapes

### Success

```typescript
// Single resource (GET by ID, POST, PATCH)
return NextResponse.json(resource);                    // 200
return NextResponse.json(resource, { status: 201 });   // 201 Created

// List
return NextResponse.json({ data: items, total: count });

// Delete
return new NextResponse(null, { status: 204 });

// Paginated
return NextResponse.json({
  data: items,
  pagination: { page, limit, total, hasNext },
});
```

### Error

Always use this shape — never vary it:

```typescript
return NextResponse.json(
  { error: string, code: string, details?: unknown },
  { status: number }
);
```

**Standard error codes:**

| Code | Status | When |
|------|--------|------|
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Auth OK, lacks permission |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `VALIDATION_ERROR` | 400 | Zod parse failure |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `CONFLICT` | 409 | Duplicate resource |

## Authentication Pattern

Always use this exact block for protected routes:

```typescript
import { createServerClient } from '@/lib/supabase/server';

const supabase = await createServerClient();
const { data: { user }, error: authError } = await supabase.auth.getUser();
if (authError || !user) {
  return NextResponse.json(
    { error: 'Unauthorized', code: 'UNAUTHORIZED' },
    { status: 401 }
  );
}
```

**Webhooks are excluded from auth** — they authenticate via signature verification instead.

## Zod Validation Pattern

Define schemas at the top of the file, then parse inside try/catch:

```typescript
import { z } from 'zod';

const CreateSchema = z.object({
  name: z.string().min(1).max(100),
  budget: z.enum(['budget', 'moderate', 'luxury']),
  duration: z.number().int().min(1).max(30),
  interests: z.array(z.string()).optional().default([]),
});

// In handler:
const body = await request.json();
const data = CreateSchema.parse(body);       // throws ZodError on invalid

// Catch ZodError specifically:
if (error instanceof z.ZodError) {
  return NextResponse.json(
    { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
    { status: 400 }
  );
}
```

## Rate Limiting

Import from `src/lib/rate-limit.ts` for routes that call AI or are expensive:

```typescript
import { checkRateLimit } from '@/lib/rate-limit';

const { allowed, remaining } = await checkRateLimit({
  userId: user.id,
  tier: userTier,       // 'explorer' | 'voyager' | 'navigator'
  action: 'generate',  // action key for tracking
});

if (!allowed) {
  return NextResponse.json(
    { error: 'Rate limit exceeded', code: 'RATE_LIMITED' },
    { status: 429, headers: { 'X-RateLimit-Remaining': '0' } }
  );
}
```

**Tiers and limits:**
- `explorer` (free): 5 itineraries/month, 3 AI queries/trip
- `voyager` ($3.99): 15 itineraries/month, 15 AI queries/trip
- `navigator` ($9.99): 300 itineraries/month, 10K queries/trip
- Anonymous: 3 itineraries/day

## Supabase Query Patterns

```typescript
// Fetch own resource (RLS enforces ownership)
const { data, error } = await supabase
  .from('itineraries')
  .select('*')
  .eq('id', id)
  .single();

if (error?.code === 'PGRST116') {          // no rows returned
  return NextResponse.json(
    { error: 'Not found', code: 'NOT_FOUND' },
    { status: 404 }
  );
}

// Soft delete (preferred over hard delete)
await supabase
  .from('itineraries')
  .update({ deleted_at: new Date().toISOString() })
  .eq('id', id)
  .eq('user_id', user.id);                 // double-check ownership

// Insert and return created row
const { data, error } = await supabase
  .from('items')
  .insert({ ...validated, user_id: user.id })
  .select()
  .single();
```

**Never expose `service_role` operations in user-facing routes.** Use `createServerClient()` (anon key + RLS) for user data and `createAdminClient()` only for system operations (webhooks, background jobs).

## Error Logging

Log unexpected errors with context — never expose raw errors to clients:

```typescript
} catch (error) {
  if (error instanceof z.ZodError) { /* handle separately */ }

  console.error('[POST /api/recommendations]', error);   // tag with route
  return NextResponse.json(
    { error: 'Internal server error', code: 'INTERNAL_ERROR' },
    { status: 500 }
  );
}
```

In production, pipe to Sentry via the global error handler — no extra code needed in each route.

## Caching

Use Vercel KV (Redis) for routes with stable, expensive responses:

```typescript
import { kv } from '@vercel/kv';
import { cacheKey } from '@/lib/cache/keys';

const key = cacheKey.recommendations(userId);
const cached = await kv.get(key);
if (cached) return NextResponse.json(cached);

const result = await computeExpensiveResult();
await kv.set(key, result, { ex: 3600 });   // 1 hour TTL
return NextResponse.json(result);
```

## Webhook Routes

Webhook routes skip auth middleware but validate signatures:

```typescript
// In src/middleware.ts the matcher already excludes /api/webhooks/*
// Inside the route, verify the signature:
import { verifyWebhookSignature } from '@/lib/webhooks/verify';

const body = await request.text();
const signature = request.headers.get('stripe-signature') ?? '';
const valid = verifyWebhookSignature(body, signature, process.env.STRIPE_WEBHOOK_SECRET!);
if (!valid) {
  return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
}
```

## Streaming Routes (SSE)

Use `ReadableStream` + `text/event-stream` — not WebSockets:

```typescript
return new Response(stream, {
  headers: {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  },
});
```

Each SSE message: `data: <JSON>\n\n`

## Naming Conventions

- Route paths: `kebab-case` (`generate-itinerary`, not `generateItinerary`)
- Schema names: `PascalCase` + `Schema` suffix (`CreateItinerarySchema`)
- Handler functions: exported named functions matching HTTP verbs (`GET`, `POST`)
- Internal helpers: `camelCase` (`fetchUserSubscription`)

## Existing Routes to Reference

| Path | File | Pattern |
|------|------|---------|
| `POST /api/generate-itinerary` | `src/app/api/generate-itinerary/route.ts` | Streaming, rate-limited, 3-tier |
| `GET /api/destinations` | `src/app/api/destinations/route.ts` | Cached search |
| `GET/PATCH /api/itinerary/[id]` | `src/app/api/itinerary/[id]/route.ts` | Dynamic segment, auth |
| `POST /api/subscription` | `src/app/api/subscription/route.ts` | Multi-gateway |
| `POST /api/webhooks/stripe` | `src/app/api/webhooks/stripe/route.ts` | Signature-verified webhook |
