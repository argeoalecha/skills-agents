/**
 * Webhook route template — copy to src/app/api/webhooks/<provider>/route.ts
 * Skips JWT auth (handled by middleware exclusion) and verifies via HMAC signature.
 */
import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

// ---------------------------------------------------------------------------
// Signature verification helpers
// ---------------------------------------------------------------------------

function verifySignature(payload: string, signature: string, secret: string): boolean {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  // Use timingSafeEqual to prevent timing attacks
  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expected)
    );
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// POST — receive webhook event
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest) {
  // 1. Read raw body (MUST be raw string for signature verification)
  const body = await request.text();

  // 2. Verify signature — exact header name depends on the provider:
  //    Stripe:    'stripe-signature'
  //    PayMongo:  'x-paymongo-signature'
  //    GitHub:    'x-hub-signature-256'
  const signature = request.headers.get('TODO-signature-header') ?? '';
  const secret    = process.env.TODO_WEBHOOK_SECRET ?? '';

  if (!verifySignature(body, signature, secret)) {
    return NextResponse.json(
      { error: 'Invalid signature', code: 'UNAUTHORIZED' },
      { status: 401 }
    );
  }

  // 3. Parse event
  let event: { type: string; data: unknown };
  try {
    event = JSON.parse(body);
  } catch {
    return NextResponse.json(
      { error: 'Invalid JSON', code: 'BAD_REQUEST' },
      { status: 400 }
    );
  }

  // 4. Handle event types
  try {
    switch (event.type) {
      case 'TODO.event_type':
        await handleTodoEvent(event.data);
        break;

      default:
        // Acknowledge unhandled events without error
        break;
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('[POST /api/webhooks/TODO]', event.type, error);
    // Return 200 to prevent provider retries on processing errors.
    // Log and handle failures asynchronously instead.
    return NextResponse.json({ received: true, error: 'Processing failed' });
  }
}

// ---------------------------------------------------------------------------
// Event handlers
// ---------------------------------------------------------------------------

async function handleTodoEvent(data: unknown) {
  // TODO: implement event handling
  console.log('Handling event', data);
}
