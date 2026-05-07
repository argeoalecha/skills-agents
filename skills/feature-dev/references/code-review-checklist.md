# Code Review Checklist

Comprehensive checklist for reviewing pull requests in the TripIntell codebase.

## Pre-Review: PR Requirements

Before starting the review, verify the PR meets these requirements:

- [ ] PR has a clear, descriptive title
- [ ] PR description explains **what** changed and **why**
- [ ] PR is focused (single feature/fix, not multiple unrelated changes)
- [ ] All CI checks are passing (tests, linting, type-checking)
- [ ] Branch is up-to-date with `main`
- [ ] No merge conflicts
- [ ] Appropriate reviewers assigned

## Functionality Review

### Requirements & Logic

- [ ] **Feature completeness:** Does it fully implement the requirements?
- [ ] **Edge cases:** Are edge cases handled (empty states, null values, errors)?
- [ ] **Business logic:** Is the logic correct and aligned with specifications?
- [ ] **Data validation:** Are inputs validated before processing?
- [ ] **Error states:** Are errors handled gracefully with user-friendly messages?

### Testing

- [ ] **Test coverage:** Are there tests for new functionality?
- [ ] **Test quality:** Do tests cover happy paths and edge cases?
- [ ] **Test organization:** Are tests well-structured and readable?
- [ ] **E2E tests:** Are critical user flows covered by E2E tests?
- [ ] **Manual testing:** Has the feature been manually tested locally?

## Code Quality

### Readability & Maintainability

- [ ] **Clear naming:** Variables, functions, and types have descriptive names
- [ ] **Code organization:** Code is logically organized and modular
- [ ] **Comments:** Complex logic has explanatory comments
- [ ] **Simplicity:** Code is as simple as possible (no over-engineering)
- [ ] **Consistency:** Follows existing codebase patterns and conventions
- [ ] **Magic numbers:** No unexplained magic numbers (use named constants)
- [ ] **DRY principle:** No unnecessary code duplication

### TypeScript Best Practices

- [ ] **Type safety:** No `any` types (use proper types or `unknown`)
- [ ] **Type inference:** Leverages TypeScript inference where appropriate
- [ ] **Type definitions:** Complex types are well-defined and reusable
- [ ] **Null safety:** Handles null/undefined cases explicitly
- [ ] **Zod schemas:** API inputs/outputs validated with Zod
- [ ] **Type imports:** Uses `import type` for type-only imports

### React & Next.js Patterns

- [ ] **Component structure:** Appropriate use of Server vs Client Components
- [ ] **"use client":** Only used when necessary (interactivity, hooks, browser APIs)
- [ ] **Props types:** Components have proper prop types
- [ ] **Hooks:** React hooks follow Rules of Hooks
- [ ] **Dependencies:** useEffect/useMemo/useCallback have correct dependencies
- [ ] **Key props:** Lists use stable, unique keys (not array indexes)
- [ ] **Accessibility:** Semantic HTML and ARIA attributes where needed

## Performance

### Frontend Performance

- [ ] **Bundle size:** No unnecessary dependencies added
- [ ] **Code splitting:** Heavy components are lazy-loaded if appropriate
- [ ] **Images:** Uses Next.js `<Image>` component with proper sizing
- [ ] **Memoization:** Expensive computations are memoized if needed
- [ ] **Re-renders:** Components don't re-render unnecessarily

### Backend Performance

- [ ] **Database queries:** Queries are optimized (use indexes, avoid N+1)
- [ ] **Caching:** Appropriate use of caching (Redis, Vercel KV)
- [ ] **API efficiency:** No redundant API calls or over-fetching
- [ ] **Pagination:** Large datasets use pagination
- [ ] **Rate limiting:** Rate limits applied to API routes if needed

## Security

### Authentication & Authorization

- [ ] **Auth checks:** Protected routes verify authentication
- [ ] **User verification:** API routes validate user identity
- [ ] **RLS policies:** Database has proper Row-Level Security policies
- [ ] **Ownership:** Users can only access their own data
- [ ] **Session handling:** Proper session management (no token leakage)

### Data Security

- [ ] **Input sanitization:** User inputs are sanitized/validated
- [ ] **SQL injection:** No raw SQL with user input (use parameterized queries)
- [ ] **XSS prevention:** User-generated content is escaped
- [ ] **Secrets:** No API keys or secrets in code (use env variables)
- [ ] **Sensitive data:** PII/sensitive data properly handled
- [ ] **CORS:** CORS configured correctly (not overly permissive)

### API Security

- [ ] **Validation:** API inputs validated with Zod schemas
- [ ] **Error messages:** Error messages don't leak sensitive info
- [ ] **Rate limiting:** APIs have rate limiting where appropriate
- [ ] **CSRF protection:** Forms use CSRF tokens if needed
- [ ] **HTTPS only:** External API calls use HTTPS

## Database Changes

### Schema & Migrations

- [ ] **Migration naming:** Follows convention (YYYYMMDDHHMMSS_description.sql)
- [ ] **RLS enabled:** New tables have RLS enabled
- [ ] **RLS policies:** Appropriate policies for CRUD operations
- [ ] **Indexes:** Performance-critical columns have indexes
- [ ] **Constraints:** Appropriate use of NOT NULL, UNIQUE, FOREIGN KEY
- [ ] **Soft deletes:** Uses soft deletes (deleted_at) instead of hard deletes
- [ ] **Backward compatibility:** Migration doesn't break existing data
- [ ] **Rollback plan:** Migration is reversible if needed

### Data Integrity

- [ ] **Referential integrity:** Foreign keys properly defined
- [ ] **Data validation:** CHECK constraints for business rules
- [ ] **Default values:** Sensible defaults for columns
- [ ] **Transaction safety:** Complex operations use transactions

## API Design

### REST Conventions

- [ ] **HTTP methods:** Correct use of GET/POST/PATCH/DELETE
- [ ] **Status codes:** Appropriate HTTP status codes
- [ ] **Response format:** Consistent JSON response structure
- [ ] **Error format:** Standardized error response format
- [ ] **Pagination:** Large result sets use pagination
- [ ] **Filtering/sorting:** Query parameters for filtering/sorting

### API Documentation

- [ ] **Types defined:** Request/response types clearly defined
- [ ] **Error codes:** Error codes documented
- [ ] **Examples:** Example requests/responses provided

## DevOps & Infrastructure

### Configuration

- [ ] **Environment variables:** New env vars documented in README
- [ ] **Secrets management:** Secrets stored in Vercel/Supabase, not in code
- [ ] **Feature flags:** Use feature flags for gradual rollouts if needed

### Deployment

- [ ] **CI/CD:** Changes don't break CI/CD pipeline
- [ ] **Database migrations:** Migrations applied in correct order
- [ ] **Rollback plan:** Feature can be rolled back safely
- [ ] **Monitoring:** Error tracking (Sentry) for critical paths
- [ ] **Logs:** Appropriate logging for debugging

## UI/UX

### User Experience

- [ ] **Loading states:** Loading indicators for async operations
- [ ] **Error states:** Clear error messages with recovery actions
- [ ] **Empty states:** Helpful empty states with calls-to-action
- [ ] **Feedback:** User feedback for actions (toasts, confirmations)
- [ ] **Accessibility:** Keyboard navigation and screen reader support
- [ ] **Mobile responsive:** Works on mobile devices

### Design Consistency

- [ ] **Design system:** Uses Shadcn UI components consistently
- [ ] **Tailwind patterns:** Follows existing Tailwind conventions
- [ ] **Spacing/sizing:** Consistent with design system
- [ ] **Colors:** Uses theme colors (not hardcoded values)
- [ ] **Typography:** Uses consistent font sizes and weights

## Documentation

- [ ] **Code comments:** Complex logic is explained
- [ ] **JSDoc comments:** Public functions have JSDoc comments
- [ ] **README updates:** README updated if needed
- [ ] **CLAUDE.md updates:** CLAUDE.md updated for significant patterns/decisions
- [ ] **ADR created:** Architecture Decision Record for significant decisions
- [ ] **API docs:** API changes documented

## Common Anti-Patterns to Avoid

### React Anti-Patterns

- ❌ Using array index as key in lists
- ❌ Mutating state directly (use immutable updates)
- ❌ Missing cleanup in useEffect
- ❌ Over-using useEffect (prefer derived state)
- ❌ Props drilling (use context or state management)

### Next.js Anti-Patterns

- ❌ Using "use client" unnecessarily (default to Server Components)
- ❌ Fetching data in Client Components when Server Components can do it
- ❌ Not using Next.js Image component for images
- ❌ Client-side navigation with `<a>` instead of `<Link>`

### TypeScript Anti-Patterns

- ❌ Using `any` type (use `unknown` or proper types)
- ❌ Type assertions (`as`) without validation
- ❌ Ignoring TypeScript errors with `@ts-ignore`
- ❌ Not leveraging type inference

### Database Anti-Patterns

- ❌ N+1 query problem (fetch related data in loops)
- ❌ Missing indexes on frequently queried columns
- ❌ Not using RLS (relying only on application-level auth)
- ❌ Storing sensitive data in plain text

### API Anti-Patterns

- ❌ Not validating inputs
- ❌ Exposing internal error details to users
- ❌ Missing rate limiting on expensive endpoints
- ❌ Not handling edge cases (null, empty arrays, etc.)

## Review Comments Best Practices

When leaving review comments:

**Be constructive:**
- ✅ "Consider extracting this logic into a separate function for reusability"
- ❌ "This code is messy"

**Be specific:**
- ✅ "This query could cause N+1 problem. Try using .select('*, user:users(*)') to join"
- ❌ "Performance issue here"

**Explain why:**
- ✅ "Using array index as key can cause bugs when items are reordered. Use item.id instead"
- ❌ "Don't use index as key"

**Distinguish importance:**
- **Critical:** Security issues, data loss, breaking changes
- **Important:** Performance issues, error handling, test coverage
- **Nit:** Code style, minor refactoring suggestions

**Approve when:**
- Code meets quality standards (not perfection)
- Critical issues are resolved
- Important issues have a plan to address

**Request changes when:**
- Security vulnerabilities exist
- Core functionality is broken
- Tests are missing for critical paths
- Breaking changes without migration plan
