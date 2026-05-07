#!/bin/bash
# Scaffold a new Next.js App Router API route for TripIntell
# Usage: ./scaffold_route.sh <route-path> [--method GET,POST,PATCH,DELETE] [--auth] [--stream]
#
# Examples:
#   ./scaffold_route.sh recommendations
#   ./scaffold_route.sh trips/[id]/collaborators --method GET,POST,DELETE --auth
#   ./scaffold_route.sh itinerary/[id]/stream --stream --auth

set -e

ROUTE_PATH="${1}"
METHODS="GET,POST"
AUTH=false
STREAM=false

# Parse flags
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --method) METHODS="$2"; shift 2 ;;
    --auth)   AUTH=true; shift ;;
    --stream) STREAM=true; shift ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

if [[ -z "$ROUTE_PATH" ]]; then
  echo "Usage: $0 <route-path> [--method GET,POST,...] [--auth] [--stream]"
  echo "Example: $0 recommendations --method GET,POST --auth"
  exit 1
fi

TARGET="src/app/api/${ROUTE_PATH}/route.ts"
mkdir -p "$(dirname "$TARGET")"

if [[ -f "$TARGET" ]]; then
  echo "⚠️  File already exists: $TARGET"
  echo "   Delete it first or choose a different path."
  exit 1
fi

# Build auth block
if $AUTH; then
  AUTH_BLOCK='
  const supabase = await createServerClient();
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    return NextResponse.json(
      { error: "Unauthorized", code: "UNAUTHORIZED" },
      { status: 401 }
    );
  }
'
  AUTH_IMPORT="import { createServerClient } from '@/lib/supabase/server';"
else
  AUTH_BLOCK=''
  AUTH_IMPORT=''
fi

# Stream template
if $STREAM; then
cat > "$TARGET" << TEMPLATE
import { NextRequest } from 'next/server';
${AUTH_IMPORT}

export async function POST(request: NextRequest) {
${AUTH_BLOCK}
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      try {
        controller.enqueue(encoder.encode('data: {"status":"starting"}\n\n'));

        // TODO: implement streaming logic here

        controller.enqueue(encoder.encode('data: {"status":"complete"}\n\n'));
        controller.close();
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        controller.enqueue(encoder.encode(\`data: {"error":"\${message}"}\n\n\`));
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
TEMPLATE
  echo "✅ Created streaming route: $TARGET"
  exit 0
fi

# Standard CRUD template — build method handlers
IMPORTS="import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
${AUTH_IMPORT}"

HANDLERS=""

IFS=',' read -ra METHOD_LIST <<< "$METHODS"
for METHOD in "${METHOD_LIST[@]}"; do
  METHOD=$(echo "$METHOD" | tr -d ' ' | tr '[:lower:]' '[:upper:]')

  case "$METHOD" in
    GET)
      HANDLERS+="
export async function GET(request: NextRequest) {
  try {
${AUTH_BLOCK}
    // TODO: implement GET logic
    return NextResponse.json({ data: [] });
  } catch (error) {
    console.error('[GET /${ROUTE_PATH}]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
"
      ;;
    POST)
      HANDLERS+="
const CreateSchema = z.object({
  // TODO: define request body schema
});

export async function POST(request: NextRequest) {
  try {
${AUTH_BLOCK}
    const body = await request.json();
    const data = CreateSchema.parse(body);

    // TODO: implement POST logic

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
        { status: 400 }
      );
    }
    console.error('[POST /${ROUTE_PATH}]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
"
      ;;
    PATCH)
      HANDLERS+="
const UpdateSchema = z.object({
  // TODO: define update schema
}).partial();

export async function PATCH(request: NextRequest) {
  try {
${AUTH_BLOCK}
    const body = await request.json();
    const data = UpdateSchema.parse(body);

    // TODO: implement PATCH logic

    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors },
        { status: 400 }
      );
    }
    console.error('[PATCH /${ROUTE_PATH}]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
"
      ;;
    DELETE)
      HANDLERS+="
export async function DELETE(request: NextRequest) {
  try {
${AUTH_BLOCK}
    // TODO: implement DELETE logic (prefer soft delete)

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('[DELETE /${ROUTE_PATH}]', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
"
      ;;
    *)
      echo "⚠️  Skipping unknown method: $METHOD"
      ;;
  esac
done

printf '%s\n\n%s' "$IMPORTS" "$HANDLERS" > "$TARGET"
echo "✅ Created route: $TARGET"
echo "   Methods: $METHODS"
$AUTH && echo "   Auth: enabled" || echo "   Auth: disabled"
echo ""
echo "Next steps:"
echo "  1. Fill in the TODO sections in $TARGET"
echo "  2. Add database queries via Supabase client"
echo "  3. Write tests in ${TARGET%.ts}.test.ts"
