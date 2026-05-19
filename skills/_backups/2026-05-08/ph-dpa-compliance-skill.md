---
name: ph-dpa-compliance
description: Implements Philippines Data Privacy Act (RA 10173) compliance for Next.js + Supabase CRM/SaaS projects. Run this after /audit flags compliance gaps in AUDIT.md — covers consent on registration and public forms, privacy policy page, data subject rights API (purge + export), IP anonymization in retention policy, and PII minimization in AI prompts. Triggers on "DPA compliance", "Philippines privacy law", "consent mechanism", "right to erasure", "data subject rights", "privacy policy", "PII minimization", or "RA 10173".
---

# Philippines DPA Compliance — RA 10173

Remediates Philippines Data Privacy Act compliance findings produced by `/audit` (Sub-agent D: Compliance).

---

## Overview

RA 10173 (Data Privacy Act of 2012) and NPC Circular 16-01 require:

| Requirement | Implementation |
|---|---|
| Informed consent before data collection | Consent checkbox on registration + public forms |
| Right to access | Data export endpoint |
| Right to erasure | Account deletion / data purge endpoint |
| Right to rectification | Profile update functionality (usually already exists) |
| Data minimization | No unnecessary PII collected or stored |
| Security of personal data | Encryption, RLS, no PII in logs |
| Privacy notice | Privacy policy page linked from all data collection points |

---

## Compliance Checklist

Work through each item, implementing only what the audit flagged as missing:

---

### 1. Consent Mechanism on Registration

Add a consent checkbox to the signup form:

```tsx
// In signup form component
<div className="flex items-start gap-2">
  <input
    id="consent"
    type="checkbox"
    {...register('consent', { required: 'You must accept the Privacy Policy to continue' })}
    className="mt-1"
  />
  <label htmlFor="consent" className="text-sm text-gray-600">
    I agree to the{' '}
    <a href="/privacy" className="underline text-teal-700" target="_blank">
      Privacy Policy
    </a>{' '}
    and consent to the collection and processing of my personal data.
  </label>
</div>
{errors.consent && (
  <p role="alert" className="text-xs text-red-500">{errors.consent.message}</p>
)}
```

Zod schema addition:
```ts
const signupSchema = z.object({
  // ... existing fields
  consent: z.literal(true, {
    errorMap: () => ({ message: 'You must accept the Privacy Policy to continue' }),
  }),
})
```

Record consent in the database:
```sql
-- Add to users table or a separate consent_log table
ALTER TABLE public.user_profiles
  ADD COLUMN consent_given_at TIMESTAMPTZ,
  ADD COLUMN consent_ip TEXT,      -- anonymize: store first 3 octets only
  ADD COLUMN privacy_policy_version TEXT;
```

---

### 2. Privacy Policy Page

Create `app/privacy/page.tsx` with at minimum:

```tsx
export default function PrivacyPage() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1>Privacy Policy</h1>
      <p>Effective date: {EFFECTIVE_DATE}</p>

      <h2>1. What data we collect</h2>
      <p>Email address, name, and usage data.</p>

      <h2>2. How we use your data</h2>
      <p>To provide the service, send transactional emails, and improve the product.</p>

      <h2>3. Your rights under RA 10173</h2>
      <ul>
        <li>Right to be informed</li>
        <li>Right to access your data — <a href="/account/export">Export your data</a></li>
        <li>Right to rectification — update your profile</li>
        <li>Right to erasure — <a href="/account/delete">Delete your account</a></li>
        <li>Right to data portability</li>
      </ul>

      <h2>4. Data retention</h2>
      <p>We retain your data for as long as your account is active, plus 30 days after deletion.</p>

      <h2>5. Contact</h2>
      <p>
        Data Protection Officer: dpo@yourdomain.com<br />
        National Privacy Commission: www.privacy.gov.ph
      </p>
    </main>
  )
}
```

Link to `/privacy` from:
- Footer on all marketing pages
- Registration form (next to consent checkbox)
- Login page footer

---

### 3. Data Export Endpoint (Right to Access / Portability)

```typescript
// app/api/account/export/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const supabase = await createServerClient()
  const { data: { user }, error: authError } = await supabase.auth.getUser()

  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 })
  }

  // Collect all user data across tables
  const [profile, orders, activity] = await Promise.all([
    supabase.from('user_profiles').select('*').eq('user_id', user.id).single(),
    supabase.from('orders').select('*').eq('user_id', user.id),
    supabase.from('activity_log').select('*').eq('user_id', user.id),
  ])

  const exportData = {
    exported_at: new Date().toISOString(),
    account: {
      email: user.email,
      created_at: user.created_at,
    },
    profile: profile.data,
    orders: orders.data,
    activity: activity.data,
  }

  return new NextResponse(JSON.stringify(exportData, null, 2), {
    headers: {
      'Content-Type': 'application/json',
      'Content-Disposition': `attachment; filename="my-data-${Date.now()}.json"`,
    },
  })
}
```

---

### 4. Data Purge Endpoint (Right to Erasure)

```typescript
// app/api/account/delete/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function DELETE(request: NextRequest) {
  const supabase = await createServerClient()
  const { data: { user }, error: authError } = await supabase.auth.getUser()

  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 })
  }

  // Soft-delete all user data first (set deleted_at)
  const tables = ['orders', 'user_profiles', 'activity_log']
  for (const table of tables) {
    await supabase
      .from(table)
      .update({ deleted_at: new Date().toISOString() })
      .eq('user_id', user.id)
  }

  // Delete the auth account (hard delete — use admin client)
  const adminSupabase = createAdminClient()
  await adminSupabase.auth.admin.deleteUser(user.id)

  return new NextResponse(null, { status: 204 })
}
```

---

### 5. IP Anonymization

Never store full IP addresses. Store only the first 3 octets:

```typescript
function anonymizeIp(ip: string): string {
  const parts = ip.split('.')
  if (parts.length === 4) {
    return `${parts[0]}.${parts[1]}.${parts[2]}.0`
  }
  // IPv6: truncate last 4 groups
  const ipv6Parts = ip.split(':')
  return ipv6Parts.slice(0, 4).join(':') + ':0000:0000:0000:0000'
}
```

Apply in middleware or any endpoint that logs IP addresses.

---

### 6. PII Minimization in AI Prompts

When sending user data to AI models (Claude, OpenAI, etc.), strip or pseudonymize PII:

```typescript
function sanitizeForAI(userData: UserData): SafeUserData {
  return {
    // Replace real identifiers with hashed/generic ones
    userId: hashUserId(userData.id),   // deterministic hash, not reversible
    // Keep aggregate data
    accountAgeMonths: getAccountAgeMonths(userData.createdAt),
    tier: userData.subscriptionTier,
    // Strip: email, name, phone, address, IP
  }
}
```

Never include:
- Email addresses
- Full names
- Phone numbers
- Physical addresses
- IP addresses
- Financial account details

---

### 7. PII in Logs

Audit all `console.log`, `console.error`, and Sentry captures for PII:

```typescript
// BAD
console.error('Login failed for user:', user.email)
Sentry.captureException(err, { extra: { user: user } })

// GOOD
console.error('Login failed for user:', user.id)
Sentry.captureException(err, { extra: { userId: user.id } })
```

---

## Rules

- Never delete user data without confirmation — use soft deletes and a grace period
- The DPO contact email must be a real monitored inbox, not a placeholder
- Privacy policy version must be stored with consent records so you can prove which policy the user agreed to
- Do not send user data to third-party services not mentioned in the privacy policy
