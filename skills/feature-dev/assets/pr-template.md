# Pull Request

## Description

<!-- Briefly describe what this PR does and why -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Refactor (code change that neither fixes a bug nor adds a feature)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test coverage improvement

## Related Issues

<!-- Link to related issues/tickets -->

Fixes #
Relates to #

## Changes Made

<!-- List the key changes in this PR -->

-
-
-

## Architecture Decisions

<!-- If this PR introduces significant architectural changes, briefly describe them -->
<!-- Reference ADR if one was created -->

-

## Testing

### Test Coverage

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing completed

### How to Test

<!-- Describe how reviewers can test this PR -->

1.
2.
3.

### Test Results

<!-- Paste relevant test output or screenshots -->

```
```

## Database Changes

<!-- If this PR includes database changes -->

- [ ] Migration file created (`YYYYMMDDHHMMSS_description.sql`)
- [ ] Migration tested locally
- [ ] RLS policies added/updated
- [ ] Database types regenerated (`pnpm db:types`)
- [ ] Backward compatible

**Migration details:**


## Deployment Notes

<!-- Any special considerations for deployment? -->

- [ ] Requires environment variable changes (documented below)
- [ ] Requires database migration
- [ ] Requires cache invalidation
- [ ] Feature flag needed
- [ ] Breaking changes (requires communication)

**Environment variables needed:**

```bash
# Add these to Vercel:
```

## Screenshots/Recordings

<!-- If UI changes, add screenshots or GIFs -->

**Before:**


**After:**


## Checklist

<!-- Mark completed items with an "x" -->

### Code Quality

- [ ] Code follows project conventions
- [ ] TypeScript types are properly defined (no `any`)
- [ ] Code is DRY (no unnecessary duplication)
- [ ] Comments added for complex logic
- [ ] Unused code/imports removed
- [ ] Console logs removed (except intentional logging)

### Performance

- [ ] No unnecessary re-renders
- [ ] Database queries optimized
- [ ] Appropriate caching used
- [ ] Images optimized (Next.js Image component)

### Security

- [ ] User inputs validated (Zod schemas)
- [ ] Authentication/authorization checked
- [ ] RLS policies reviewed
- [ ] No secrets in code
- [ ] Sensitive data handled appropriately

### Documentation

- [ ] Code is self-documenting or has comments
- [ ] README updated (if needed)
- [ ] CLAUDE.md updated (if significant patterns added)
- [ ] ADR created (if architectural decision made)

### CI/CD

- [ ] All CI checks pass (lint, type-check, tests)
- [ ] Build succeeds locally
- [ ] Preview deployment reviewed

## Reviewer Notes

<!-- Any specific areas you'd like reviewers to focus on? -->

## Post-Merge Tasks

<!-- Things to do after merging -->

- [ ] Monitor Sentry for errors
- [ ] Check performance metrics
- [ ] Verify feature in production
- [ ] Update project board/tickets
- [ ] Communicate changes to team

---

**Estimated Review Time:** <!-- e.g., 10 minutes, 30 minutes, 1 hour -->

**Reviewers:** @<!-- mention reviewers -->
