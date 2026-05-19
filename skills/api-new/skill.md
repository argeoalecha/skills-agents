---
name: api-new
description: Guided workflow for creating new API endpoints across any project in the workspace. Use this skill when adding any new API route or endpoint. Triggers on /api-new, "create a new API endpoint", "add an API route", "new endpoint for", "build an API for", or "I need an API that". Walks through route type selection, scaffold generation, implementation, and test creation following the project's conventions (Zod validation, auth, RLS, standardized error format).
---

# API Endpoint Creation Workflow

Guided 4-step workflow for adding a production-ready API endpoint to any project.

| Route Type | Use Case | Template |
|---|---|---|
| **CRUD collection** | List + create resources | `assets/route-crud.ts` |
| **Dynamic resource** | Single item: get/update/delete | `assets/route-dynamic.ts` |
| **Streaming (SSE)** | Long AI generation, real-time output | `assets/route-stream.ts` |
| **Webhook** | Stripe/PayMongo/GitHub inbound events | `assets/route-webhook.ts` |

**Script location:** `scripts/scaffold_route.sh`

Alternatively, copy the appropriate template from `assets/`.

---

## Step 1 — Identify Route Type and Path

Ask the user (or infer from context):
1. What HTTP methods are needed? (GET, POST, PATCH, DELETE)
2. Does the route reference a single resource by ID? → `[id]/route.ts`
3. Will it stream output? → streaming template
4. Is it receiving webhook events? → webhook template
5. What path should it live at? (e.g. `/api/trips`, `/api/itinerary/[id]`)

**File placement** (Next.js App Router):
```
src/app/api/
├── <resource>/
│   └── route.ts          # /api/<resource>  — collection (GET list + POST create)
├── <resource>/[id]/
│   └── route.ts          # /api/<resource>/[id] — single item (GET + PATCH + DELETE)
└── webhooks/<provider>/
    └── route.ts          # /api/webhooks/<provider>
```

---

## Step 2 — Scaffold the File

Run the scaffold script to generate the route file:

```bash
cd <project-root>

# Standard route (specify methods with --method, add --auth if protected)
bash ~/.claude/skills/api-new/scripts/scaffold_route.sh <route-path> --method GET,POST --auth

# Streaming (SSE) route
bash ~/.claude/skills/api-new/scripts/scaffold_route.sh <route-path> --stream --auth

# Examples
bash ~/.claude/skills/api-new/scripts/scaffold_route.sh trips --method GET,POST --auth
bash ~/.claude/skills/api-new/scripts/scaffold_route.sh trips/[id] --method GET,PATCH,DELETE --auth
bash ~/.claude/skills/api-new/scripts/scaffold_route.sh generate --stream --auth
```

For webhook routes, copy the template manually (the script does not support webhooks):

```bash
cp ~/.claude/skills/api-new/assets/route-webhook.ts src/app/api/webhooks/<provider>/route.ts
```

For fine-grained control, copy any template directly:

```bash
cp ~/.claude/skills/api-new/assets/route-crud.ts    src/app/api/<resource>/route.ts
cp ~/.claude/skills/api-new/assets/route-dynamic.ts src/app/api/<resource>/[id]/route.ts
cp ~/.claude/skills/api-new/assets/route-stream.ts  src/app/api/<resource>/route.ts
```

---

## Step 3 — Implement the Route

Every route follows this structure:

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'
import { z } from 'zod'

// 1. Define Zod schema at top of file
const CreateSchema = z.object({
  name: z.string().min(1).max(100),
  // ... fields
})

export async function POST(request: NextRequest) {
  try {
    // 2. Authenticate (skip for public or webhook routes)
    const supabase = await createServerClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      )
    }

    // 3. Parse and validate body
    const body = await request.json()
    const data = CreateSchema.parse(body)

    // 4. Business logic (Supabase, AI, etc.)
    const { data: result, error } = await supabase
      .from('table_name')
      .insert({ ...data, user_id: user.id })
      .select()
      .single()

    if (error) throw error

    // 5. Return success
    return NextResponse.json(result, { status: 201 })

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
        { status: 400 }
      )
    }
    console.error('[POST /api/<resource>]', error)
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    )
  }
}
```

### Standard error codes

| Code | Status | When |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Auth OK, lacks permission |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `VALIDATION_ERROR` | 400 | Zod parse failure |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `CONFLICT` | 409 | Duplicate resource |

### Dynamic route params
```typescript
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const { id } = params
  // ...
}
```

### Soft deletes (preferred over hard delete)
```typescript
await supabase
  .from('items')
  .update({ deleted_at: new Date().toISOString() })
  .eq('id', id)
  .eq('user_id', user.id)

return new NextResponse(null, { status: 204 })
```

---

## Step 4 — Write Tests

After implementing, write at minimum:
1. One happy-path test (valid input → correct response)
2. One validation test (invalid input → 400 VALIDATION_ERROR)
3. One auth test (missing auth → 401 UNAUTHORIZED)

See `assets/route-webhook.ts` for webhook signature verification patterns. For rate limiting and caching, follow the project's CLAUDE.md conventions.
