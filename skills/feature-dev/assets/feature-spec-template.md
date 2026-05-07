# Feature Specification: [FEATURE NAME]

**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** [Draft | In Review | Approved | In Development | Completed]
**Priority:** [P0 - Critical | P1 - High | P2 - Medium | P3 - Low]

---

## Overview

### Summary

<!-- 1-2 sentences describing what this feature does -->

### Goals

<!-- What are we trying to achieve with this feature? -->

1.
2.
3.

### Non-Goals

<!-- What is explicitly out of scope for this feature? -->

1.
2.

---

## Background

### Problem Statement

<!-- What problem are we solving? Why is this important? -->

### User Needs

<!-- What do users need? How does this feature address those needs? -->

**User Stories:**

- As a [user type], I want to [action], so that [benefit]
- As a [user type], I want to [action], so that [benefit]

### Success Metrics

<!-- How will we measure success? -->

| Metric | Target | Measurement |
|--------|--------|-------------|
| | | |

---

## User Experience

### User Flow

<!-- Describe the step-by-step user flow -->

1. User starts at [location]
2. User [action]
3. System [response]
4. User sees [result]

### Wireframes/Mockups

<!-- Link to design files or embed mockups -->

[Figma/Design Link]

### Key UI Elements

**Components needed:**
-
-

**Interactions:**
-
-

---

## Technical Design

### Architecture Overview

<!-- High-level technical approach -->

**Affected Components:**
- Frontend: [What changes in the UI?]
- Backend: [What APIs are needed?]
- Database: [What schema changes?]
- External Services: [What integrations?]

### Frontend Implementation

**New Components:**
-

**Modified Components:**
-

**State Management:**
- What state is needed?
- Where does it live (local, Zustand, server)?

**API Integration:**
- What endpoints will the frontend call?

### Backend Implementation

**API Endpoints:**

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| | | | | |

**Business Logic:**
-

**Validation:**
- What inputs need validation?
- What error cases need handling?

### Database Schema

**New Tables:**

```sql
CREATE TABLE table_name (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  -- columns
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Modified Tables:**

```sql
ALTER TABLE existing_table ADD COLUMN new_column TYPE;
```

**Indexes:**

```sql
CREATE INDEX idx_name ON table_name(column);
```

**RLS Policies:**

```sql
CREATE POLICY "policy_name"
ON table_name
FOR SELECT
USING (auth.uid() = user_id);
```

### External Integrations

**APIs:**
- Which external services are needed?
- What data is exchanged?

**Third-party Libraries:**
- New dependencies to add
- Why are they needed?

---

## Security & Privacy

### Authentication & Authorization

- Who can access this feature?
- What permissions are required?
- How is access controlled?

### Data Security

- What sensitive data is handled?
- How is it protected?
- What compliance requirements apply?

### Privacy Considerations

- What PII is collected?
- How is user consent obtained?
- How can users delete their data?

---

## Testing Strategy

### Unit Tests

<!-- What should be unit tested? -->

-

### Integration Tests

<!-- What integration tests are needed? -->

-

### E2E Tests

<!-- What critical user flows need E2E coverage? -->

1.
2.

### Manual Testing Checklist

- [ ] Happy path works correctly
- [ ] Error cases handled gracefully
- [ ] Edge cases tested (empty states, max values, etc.)
- [ ] Mobile responsive
- [ ] Accessibility (keyboard navigation, screen readers)
- [ ] Cross-browser compatibility
- [ ] Performance acceptable

---

## Performance Considerations

### Expected Load

- Concurrent users:
- Requests per second:
- Data volume:

### Performance Targets

| Metric | Target |
|--------|--------|
| API response time | < XXX ms |
| Page load time | < XXX ms |
| Database query time | < XXX ms |

### Optimization Strategy

-

---

## Deployment Plan

### Rollout Strategy

- [ ] Feature flag (gradual rollout)
- [ ] All users at once
- [ ] Specific user segments first

### Feature Flag Configuration

```typescript
const featureEnabled = await checkFeatureFlag('feature-name', {
  userId: user.id,
  rolloutPercentage: 10, // Start with 10%
});
```

### Database Migration

- Migration order:
- Backward compatibility:
- Rollback plan:

### Monitoring & Alerts

**Metrics to track:**
-

**Alerts to set:**
-

---

## Dependencies

### Blocked By

<!-- What needs to happen before we can start? -->

-

### Blocking

<!-- What is waiting on this feature? -->

-

### Team Dependencies

<!-- Which teams need to be involved? -->

| Team | Involvement | Contact |
|------|-------------|---------|
| | | |

---

## Timeline

| Phase | Duration | Start Date | End Date |
|-------|----------|------------|----------|
| Requirements & Design | | | |
| Architecture Planning | | | |
| Development | | | |
| Testing & QA | | | |
| Code Review | | | |
| Deployment | | | |

**Key Milestones:**
- [ ] Design approved
- [ ] Architecture approved
- [ ] Development complete
- [ ] Tests pass
- [ ] Code review approved
- [ ] Deployed to staging
- [ ] Deployed to production

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| | High/Med/Low | High/Med/Low | |

---

## Open Questions

<!-- Questions that need to be answered before proceeding -->

1.
2.

---

## Future Enhancements

<!-- Ideas for future iterations (out of scope for v1) -->

-

---

## References

<!-- Links to related docs, designs, tickets -->

- [Design Mockups](link)
- [Technical Spec](link)
- [Related ADR](link)
- [GitHub Issue #XXX](link)

---

## Approval

**Stakeholders:**

- [ ] Product: [Name]
- [ ] Engineering: [Name]
- [ ] Design: [Name]
- [ ] Security: [Name]

**Approval Date:** YYYY-MM-DD

---

## Implementation Notes

<!-- Notes added during development -->

**Deviations from spec:**
-

**Learnings:**
-

**Post-launch todos:**
-
