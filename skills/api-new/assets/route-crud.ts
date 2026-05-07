/**
 * CRUD route template — copy to src/app/api/<route>/route.ts
 * Replace every TODO and the [Resource] placeholder.
 */
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { createServerClient } from '@/lib/supabase/server';

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

const CreateSchema = z.object({
  // TODO: define fields
  name: z.string().min(1).max(200),
});

const UpdateSchema = CreateSchema.partial();

// ---------------------------------------------------------------------------
// GET  — list resources belonging to the authenticated user
// ---------------------------------------------------------------------------

export async function GET(request: NextRequest) {
  try {
    const supabase = await createServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const page  = Number(searchParams.get('page')  ?? '1');
    const limit = Number(searchParams.get('limit') ?? '20');
    const offset = (page - 1) * limit;

    const { data, error, count } = await supabase
      .from('TODO_table')            // TODO: table name
      .select('*', { count: 'exact' })
      .eq('user_id', user.id)
      .is('deleted_at', null)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (error) throw error;

    return NextResponse.json({
      data,
      pagination: {
        page,
        limit,
        total: count ?? 0,
        hasNext: offset + limit < (count ?? 0),
      },
    });
  } catch (error) {
    console.error('[GET /api/TODO_route]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}

// ---------------------------------------------------------------------------
// POST — create a new resource
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest) {
  try {
    const supabase = await createServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    const body = await request.json();
    const validated = CreateSchema.parse(body);

    const { data, error } = await supabase
      .from('TODO_table')            // TODO: table name
      .insert({ ...validated, user_id: user.id })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
        { status: 400 }
      );
    }
    console.error('[POST /api/TODO_route]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
