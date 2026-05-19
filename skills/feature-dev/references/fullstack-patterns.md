# Full-Stack Development Patterns

Common patterns and best practices for building features in the Hayah-AI workspace stack (Next.js App Router, TypeScript strict, Supabase, Tailwind, shadcn/ui).

## Table of Contents

1. [API Route Patterns](#api-route-patterns)
2. [Database Patterns](#database-patterns)
3. [Frontend Patterns](#frontend-patterns)
4. [Authentication Patterns](#authentication-patterns)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Performance Patterns](#performance-patterns)

## API Route Patterns

### Standard API Route Structure

```typescript
// src/app/api/items/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase/server';
import { z } from 'zod';

// Schema validation
const CreateItemSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
});

export async function POST(request: NextRequest) {
  try {
    // 1. Get authenticated user
    const supabase = await createServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    // 2. Parse and validate request body
    const body = await request.json();
    const validatedData = CreateItemSchema.parse(body);

    // 3. Perform business logic
    const { data, error } = await supabase
      .from('items')
      .insert({
        ...validatedData,
        user_id: user.id,
      })
      .select()
      .single();

    if (error) throw error;

    // 4. Return success response
    return NextResponse.json(data, { status: 201 });

  } catch (error) {
    // 5. Handle errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Error creating item:', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
```

### Streaming Responses (SSE)

```typescript
// src/app/api/stream/route.ts
import { createServerClient } from '@/lib/supabase/server';

export async function POST(request: NextRequest) {
  const supabase = await createServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Send initial message
        controller.enqueue(encoder.encode('data: {"status":"starting"}\n\n'));

        // Stream data from Claude API or other source
        for await (const chunk of dataSource) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(chunk)}\n\n`));
        }

        // Complete
        controller.enqueue(encoder.encode('data: {"status":"complete"}\n\n'));
        controller.close();
      } catch (error) {
        controller.enqueue(encoder.encode(`data: {"error":"${error.message}"}\n\n`));
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

## Database Patterns

### Row-Level Security (RLS)

```sql
-- Enable RLS on table
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- Owner-only CRUD
CREATE POLICY "Users manage own items"
ON items
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Public read, owner write
CREATE POLICY "Public can view"
ON items FOR SELECT
USING (true);

CREATE POLICY "Owners can modify"
ON items FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Owners can update"
ON items FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Owners can delete"
ON items FOR DELETE
USING (auth.uid() = user_id);
```

### JSONB Queries

```typescript
// Query JSONB columns
const { data } = await supabase
  .from('itineraries')
  .select('*')
  .contains('preferences', { budget: 'moderate' });

// Update nested JSONB
const { data } = await supabase
  .from('itineraries')
  .update({
    itinerary_data: {
      ...existingData,
      days: updatedDays,
    }
  })
  .eq('id', itineraryId);

// Use JSONB operators in raw SQL
const { data } = await supabase.rpc('search_itineraries', {
  search_term: 'Paris',
  min_budget: 1000,
});
```

### Soft Deletes

```sql
-- Add deleted_at column
ALTER TABLE items ADD COLUMN deleted_at TIMESTAMPTZ;

-- Update RLS policies to exclude soft-deleted
CREATE POLICY "Exclude deleted items"
ON items FOR SELECT
USING (deleted_at IS NULL AND auth.uid() = user_id);
```

```typescript
// Soft delete
await supabase
  .from('items')
  .update({ deleted_at: new Date().toISOString() })
  .eq('id', itemId);

// Restore
await supabase
  .from('items')
  .update({ deleted_at: null })
  .eq('id', itemId);
```

## Frontend Patterns

### Server Component Data Fetching

```typescript
// src/app/dashboard/page.tsx (Server Component)
import { createServerClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const supabase = await createServerClient();

  // Fetch user
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  // Fetch data server-side
  const { data: items } = await supabase
    .from('items')
    .select('*')
    .order('created_at', { ascending: false });

  return (
    <div>
      <ItemList items={items} />
    </div>
  );
}
```

### Client Component with API

```typescript
// src/components/create-item-form.tsx
'use client';

import { useState } from 'react';
import { toast } from 'sonner';

export function CreateItemForm() {
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData(e.currentTarget);
      const data = {
        name: formData.get('name'),
        description: formData.get('description'),
      };

      const response = await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create item');
      }

      const item = await response.json();
      toast.success('Item created successfully');

      // Refresh data (using router or state management)
      router.refresh();

    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

### Zustand State Management

```typescript
// src/stores/item-store.ts
import { create } from 'zustand';

interface Item {
  id: string;
  name: string;
}

interface ItemStore {
  items: Item[];
  selectedItem: Item | null;
  setItems: (items: Item[]) => void;
  setSelectedItem: (item: Item | null) => void;
  addItem: (item: Item) => void;
  removeItem: (id: string) => void;
}

export const useItemStore = create<ItemStore>((set) => ({
  items: [],
  selectedItem: null,
  setItems: (items) => set({ items }),
  setSelectedItem: (selectedItem) => set({ selectedItem }),
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
  removeItem: (id) => set((state) => ({
    items: state.items.filter((i) => i.id !== id),
  })),
}));
```

## Authentication Patterns

### Protected Route

```typescript
// src/app/dashboard/layout.tsx
import { createServerClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createServerClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect('/login');
  }

  return <>{children}</>;
}
```

### Auth State in Client Component

```typescript
'use client';

import { useEffect, useState } from 'react';
import { createBrowserClient } from '@/lib/supabase/client';
import type { User } from '@supabase/supabase-js';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const supabase = createBrowserClient();

  useEffect(() => {
    // Get initial session
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  return { user };
}
```

## Error Handling Patterns

### API Error Response Format

```typescript
interface ApiError {
  error: string;          // User-friendly message
  code: string;           // Machine-readable code
  details?: any;          // Additional context (validation errors, etc.)
  statusCode?: number;    // HTTP status code
}

// Usage
return NextResponse.json(
  {
    error: 'Validation failed',
    code: 'VALIDATION_ERROR',
    details: zodError.errors,
  },
  { status: 400 }
);
```

### Frontend Error Handling

```typescript
async function fetchData() {
  try {
    const response = await fetch('/api/items');

    if (!response.ok) {
      const error: ApiError = await response.json();

      // Log to Sentry
      Sentry.captureException(new Error(error.error), {
        extra: { code: error.code, details: error.details },
      });

      // Show user-friendly message
      toast.error(error.error);
      return;
    }

    const data = await response.json();
    // Process data

  } catch (error) {
    // Network or parse error
    console.error('Request failed:', error);
    toast.error('Something went wrong. Please try again.');
    Sentry.captureException(error);
  }
}
```

## Performance Patterns

### Caching with Vercel KV

```typescript
import { kv } from '@vercel/kv';

export async function getCachedData(key: string) {
  // Try cache first
  const cached = await kv.get(key);
  if (cached) return cached;

  // Fetch from database
  const data = await fetchFromDatabase();

  // Cache for 1 hour
  await kv.set(key, data, { ex: 3600 });

  return data;
}

// Invalidate cache
export async function invalidateCache(pattern: string) {
  await kv.del(pattern);
}
```

### Database Query Optimization

```typescript
// ❌ Bad: N+1 query problem
for (const item of items) {
  const user = await supabase
    .from('users')
    .select('*')
    .eq('id', item.user_id)
    .single();
}

// ✅ Good: Join query
const { data } = await supabase
  .from('items')
  .select(`
    *,
    user:users(*)
  `);

// ✅ Good: Use indexes
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_created_at ON items(created_at DESC);
```

### Image Optimization

```typescript
import Image from 'next/image';

// Use Next.js Image component
<Image
  src="/photo.jpg"
  alt="Description"
  width={800}
  height={600}
  placeholder="blur"
  blurDataURL="data:image/..." // Low-quality placeholder
/>

// For Supabase Storage images
const { data } = supabase.storage
  .from('photos')
  .getPublicUrl('path/to/image.jpg', {
    transform: {
      width: 800,
      height: 600,
      quality: 80,
    },
  });
```

### React Query (for Client-Side Caching)

```typescript
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function useItems() {
  return useQuery({
    queryKey: ['items'],
    queryFn: async () => {
      const res = await fetch('/api/items');
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    },
    staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
  });
}

function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data) => {
      const res = await fetch('/api/items', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to create');
      return res.json();
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}
```
