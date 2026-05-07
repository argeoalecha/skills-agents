/**
 * Dynamic segment route template — copy to src/app/api/<resource>/[id]/route.ts
 * Handles GET (single), PATCH (update), DELETE (soft-delete) for one resource.
 */
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { createServerClient } from '@/lib/supabase/server';

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

const UpdateSchema = z.object({
  // TODO: define updatable fields
  name: z.string().min(1).max(200),
}).partial();

// ---------------------------------------------------------------------------
// GET /api/<resource>/[id]
// ---------------------------------------------------------------------------

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = await createServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    const { data, error } = await supabase
      .from('TODO_table')            // TODO: table name
      .select('*')
      .eq('id', params.id)
      .is('deleted_at', null)
      .single();

    if (error?.code === 'PGRST116' || !data) {
      return NextResponse.json(
        { error: 'Not found', code: 'NOT_FOUND' },
        { status: 404 }
      );
    }
    if (error) throw error;

    return NextResponse.json(data);
  } catch (error) {
    console.error('[GET /api/TODO_route/[id]]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}

// ---------------------------------------------------------------------------
// PATCH /api/<resource>/[id]
// ---------------------------------------------------------------------------

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
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
    const validated = UpdateSchema.parse(body);

    const { data, error } = await supabase
      .from('TODO_table')            // TODO: table name
      .update(validated)
      .eq('id', params.id)
      .eq('user_id', user.id)        // enforce ownership
      .is('deleted_at', null)
      .select()
      .single();

    if (error?.code === 'PGRST116' || !data) {
      return NextResponse.json(
        { error: 'Not found', code: 'NOT_FOUND' },
        { status: 404 }
      );
    }
    if (error) throw error;

    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
        { status: 400 }
      );
    }
    console.error('[PATCH /api/TODO_route/[id]]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}

// ---------------------------------------------------------------------------
// DELETE /api/<resource>/[id]  — soft delete
// ---------------------------------------------------------------------------

export async function DELETE(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = await createServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    const { error } = await supabase
      .from('TODO_table')            // TODO: table name
      .update({ deleted_at: new Date().toISOString() })
      .eq('id', params.id)
      .eq('user_id', user.id);      // enforce ownership

    if (error) throw error;

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('[DELETE /api/TODO_route/[id]]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
