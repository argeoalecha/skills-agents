/**
 * Streaming (SSE) route template — copy to src/app/api/<route>/route.ts
 * Used for long-running AI generation tasks that stream progress to the client.
 */
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { createServerClient } from '@/lib/supabase/server';

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

const RequestSchema = z.object({
  // TODO: define request fields
  prompt: z.string().min(1),
});

// ---------------------------------------------------------------------------
// POST — begin streaming response
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest) {
  const supabase = await createServerClient();
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    return new Response(
      JSON.stringify({ error: 'Unauthorized', code: 'UNAUTHORIZED' }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    );
  }

  let body: z.infer<typeof RequestSchema>;
  try {
    body = RequestSchema.parse(await request.json());
  } catch (error) {
    if (error instanceof z.ZodError) {
      return new Response(
        JSON.stringify({ error: 'Validation failed', code: 'VALIDATION_ERROR', details: error.errors }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }
    return new Response(
      JSON.stringify({ error: 'Bad request', code: 'BAD_REQUEST' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      function send(payload: Record<string, unknown>) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`));
      }

      try {
        // Stage 1 — announce start
        send({ status: 'starting', message: 'Processing your request...' });

        // TODO: replace with actual streaming logic, e.g. Claude SDK stream
        // Example with Anthropic SDK:
        //
        // const stream = await anthropic.messages.stream({
        //   model: 'claude-sonnet-4-5-20250514',
        //   max_tokens: 4096,
        //   messages: [{ role: 'user', content: body.prompt }],
        // });
        //
        // for await (const chunk of stream) {
        //   if (chunk.type === 'content_block_delta') {
        //     send({ status: 'streaming', delta: chunk.delta.text });
        //   }
        // }
        //
        // const finalMessage = await stream.finalMessage();
        // send({ status: 'complete', result: finalMessage });

        send({ status: 'complete', message: 'Done' });
        controller.close();
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        console.error('[POST /api/TODO_route]', error);
        send({ status: 'error', error: message });
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
