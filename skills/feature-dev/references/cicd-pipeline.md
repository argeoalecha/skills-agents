# CI/CD Pipeline for TripIntell

Guide for Continuous Integration and Continuous Deployment setup and best practices.

## CI/CD Overview

TripIntell uses GitHub Actions for CI and Vercel for CD. The pipeline ensures code quality, runs tests, and deploys automatically to production.

## GitHub Actions Workflows

### Pull Request Workflow

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on:
  pull_request:
    branches: [main]

jobs:
  lint-and-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run ESLint
        run: pnpm lint

      - name: Run TypeScript type checking
        run: pnpm type-check

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run unit tests
        run: pnpm test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Install Playwright browsers
        run: pnpm exec playwright install --with-deps

      - name: Run E2E tests
        run: pnpm test:e2e
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}

      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build application
        run: pnpm build
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
```

### Database Migration Workflow

```yaml
# .github/workflows/db-migrate.yml
name: Database Migration

on:
  push:
    branches: [main]
    paths:
      - 'supabase/migrations/**'

jobs:
  validate-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate migration files
        run: |
          # Check naming convention
          for file in supabase/migrations/*.sql; do
            if ! echo "$(basename $file)" | grep -qE '^[0-9]{14}_[a-z_]+\.sql$'; then
              echo "Invalid migration name: $file"
              exit 1
            fi
          done

      - name: Check for dangerous operations
        run: |
          # Scan for potentially dangerous SQL
          if grep -r "DROP TABLE\|DROP DATABASE" supabase/migrations/ --exclude-dir=node_modules; then
            echo "Found dangerous DROP operations. Review required."
            exit 1
          fi

  apply-migrations:
    needs: validate-migrations
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1
        with:
          version: latest

      - name: Run migrations
        run: supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}

      - name: Generate types
        run: |
          pnpm db:types
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add src/types/database.ts
          git commit -m "chore: update database types" || echo "No changes"
          git push
```

### Deployment Workflow (Production)

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'

      - name: Post-deployment checks
        run: |
          # Wait for deployment
          sleep 30

          # Health check
          curl -f https://tripintell.com/api/health || exit 1

      - name: Notify Sentry of deployment
        run: |
          curl -X POST https://sentry.io/api/0/organizations/tripintell/releases/ \
            -H "Authorization: Bearer ${{ secrets.SENTRY_AUTH_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d "{
              \"version\": \"${{ github.sha }}\",
              \"projects\": [\"tripintell\"]
            }"
```

## Vercel Configuration

### vercel.json

```json
{
  "buildCommand": "pnpm build",
  "devCommand": "pnpm dev",
  "installCommand": "pnpm install",
  "framework": "nextjs",
  "regions": ["sfo1"],
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "@supabase-service-role-key",
    "ANTHROPIC_API_KEY": "@anthropic-api-key",
    "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY": "@google-maps-api-key"
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "no-store, must-revalidate"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/docs",
      "destination": "/documentation",
      "permanent": true
    }
  ]
}
```

## Environment Management

### Environment Tiers

**Production:**
- Vercel Production deployment
- Main Supabase project
- Real payment gateways (Stripe + PayMongo live keys)
- Production analytics (PostHog, Sentry)

**Preview (PR deployments):**
- Vercel Preview deployment per PR
- Staging Supabase project
- Test payment gateways (Stripe + PayMongo test keys)
- Staging analytics

**Local Development:**
- Local Next.js dev server
- Local Supabase (Docker)
- Test payment keys
- No analytics

### Secret Management

**Vercel Secrets:**
```bash
# Add secrets to Vercel
vercel secrets add supabase-url "https://xxx.supabase.co"
vercel secrets add supabase-anon-key "eyJxxx..."
vercel secrets add anthropic-api-key "sk-ant-xxx"

# Link secrets to project
vercel env add SUPABASE_SERVICE_ROLE_KEY production
```

**GitHub Secrets:**
Add these in GitHub repository settings → Secrets and variables → Actions:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `SUPABASE_ACCESS_TOKEN`
- `SUPABASE_DB_PASSWORD`
- `SENTRY_AUTH_TOKEN`

## Deployment Strategy

### Branch Strategy

```
main (production)
  ├── feature/new-feature (preview deployment)
  ├── fix/bug-fix (preview deployment)
  └── release/v1.4 (preview deployment)
```

**Rules:**
- All changes go through PRs to `main`
- PRs get preview deployments automatically
- Merging to `main` triggers production deployment
- No direct commits to `main`

### Deployment Checklist

Before deploying to production:

- [ ] All CI checks pass (lint, type-check, tests)
- [ ] Code review approved
- [ ] Database migrations tested locally
- [ ] Environment variables configured
- [ ] Feature flags set appropriately
- [ ] Monitoring/alerts configured
- [ ] Rollback plan documented
- [ ] Stakeholders notified

### Rollback Process

**If deployment fails:**

1. **Instant Rollback (Vercel):**
   ```bash
   # Via Vercel CLI
   vercel rollback

   # Or via Vercel dashboard
   # Deployments → Select previous deployment → Promote to Production
   ```

2. **Database Rollback (if needed):**
   ```bash
   # Revert migration
   supabase migration revert
   ```

3. **Notify team:**
   - Post in #incidents Slack channel
   - Create post-mortem document
   - Update status page

## Monitoring & Alerts

### Health Checks

```typescript
// src/app/api/health/route.ts
export async function GET() {
  try {
    // Check database connection
    const { error: dbError } = await supabase
      .from('users')
      .select('count')
      .limit(1);

    if (dbError) throw new Error('Database unhealthy');

    // Check Redis
    await kv.ping();

    // Check external APIs
    const anthropicHealthy = await checkAnthropicAPI();

    return Response.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      checks: {
        database: 'ok',
        redis: 'ok',
        anthropic: anthropicHealthy ? 'ok' : 'degraded',
      },
    });
  } catch (error) {
    return Response.json(
      {
        status: 'unhealthy',
        error: error.message,
      },
      { status: 503 }
    );
  }
}
```

### Sentry Error Tracking

```typescript
// src/lib/sentry.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.VERCEL_ENV || 'development',
  tracesSampleRate: 1.0,

  // Filter sensitive data
  beforeSend(event) {
    // Remove sensitive data from error context
    if (event.request) {
      delete event.request.cookies;
      delete event.request.headers?.['authorization'];
    }
    return event;
  },
});
```

### PostHog Analytics

```typescript
// Track deployment
posthog.capture({
  distinctId: 'system',
  event: 'deployment',
  properties: {
    version: process.env.VERCEL_GIT_COMMIT_SHA,
    environment: process.env.VERCEL_ENV,
    timestamp: new Date().toISOString(),
  },
});
```

## Performance Monitoring

### Web Vitals Tracking

```typescript
// src/app/layout.tsx
export function reportWebVitals(metric: NextWebVitalsMetric) {
  // Send to analytics
  posthog.capture('web_vitals', {
    metric: metric.name,
    value: metric.value,
    id: metric.id,
  });

  // Send to Vercel Analytics
  if (window.va) {
    window.va('event', {
      name: metric.name,
      data: metric.value,
    });
  }
}
```

### Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on:
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://${{ steps.vercel.outputs.preview-url }}
            https://${{ steps.vercel.outputs.preview-url }}/dashboard
          uploadArtifacts: true
          temporaryPublicStorage: true
```

## Optimization Tips

### Cache Strategy

```typescript
// Cache API responses
export const revalidate = 3600; // 1 hour

// Cache database queries
const cachedData = await unstable_cache(
  async () => {
    const { data } = await supabase
      .from('itineraries')
      .select('*');
    return data;
  },
  ['itineraries'],
  { revalidate: 3600 }
)();
```

### Build Optimization

```javascript
// next.config.js
module.exports = {
  // Remove console logs in production
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },

  // Analyze bundle
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          vendor: {
            name: 'vendor',
            chunks: 'all',
            test: /node_modules/,
          },
        },
      };
    }
    return config;
  },
};
```

## Troubleshooting

### Common Issues

**Build fails with TypeScript errors:**
- Run `pnpm type-check` locally
- Ensure all types are up-to-date (`pnpm db:types`)
- Check for missing environment variables

**E2E tests failing:**
- Check if preview deployment is ready
- Verify test environment variables
- Review Playwright traces in artifacts

**Deployment slow:**
- Check bundle size (`pnpm build` locally)
- Review dependencies (remove unused packages)
- Optimize images and assets

**Health check fails:**
- Verify database connection
- Check external API status
- Review Sentry for errors
