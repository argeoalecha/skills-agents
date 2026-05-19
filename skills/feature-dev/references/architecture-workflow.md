# Architecture Design Workflow

This guide covers the architectural design process for new features in the Hayah-AI workspace, including when to create Architecture Decision Records (ADRs).

## When to Create an ADR

Create an ADR for decisions that:
- Affect multiple components or layers
- Introduce new dependencies or external services
- Change data models or database schema significantly
- Establish patterns that other developers will follow
- Have long-term implications (> 6 months)
- Involve tradeoffs between competing approaches

**Examples requiring ADRs:**
- Choosing between REST vs GraphQL for a new API
- Selecting a state management approach (Zustand vs Redux vs Context)
- Deciding on caching strategy (Redis vs in-memory vs CDN)
- Implementing real-time features (WebSockets vs Server-Sent Events vs polling)

**Examples NOT requiring ADRs:**
- Adding a new UI component using existing patterns
- Writing a new API endpoint following existing conventions
- Bug fixes or refactoring that don't change architecture

## Architectural Design Process

### 1. Understand Requirements

**Questions to answer:**
- What problem does this feature solve?
- Who are the users and what are their needs?
- What are the performance requirements?
- What are the scalability constraints?
- What are the security/privacy requirements?

**Output:** Feature specification document (use `assets/feature-spec-template.md`)

### 2. Identify Architectural Concerns

**System Components:**
- Frontend (React components, state management, routing)
- Backend (API routes, business logic, data validation)
- Database (schema, queries, indexes, RLS policies)
- External Services (Stripe, PayMongo, Claude API, Google Maps)
- Infrastructure (Vercel, Supabase, Redis)

**Cross-Cutting Concerns:**
- Authentication & authorization
- Error handling & logging
- Performance & caching
- Testing strategy
- Monitoring & observability

### 3. Design the Solution

**Frontend Architecture:**
- Component hierarchy and data flow
- State management approach (local vs global)
- API integration patterns
- Error handling and loading states
- Accessibility considerations

**Backend Architecture:**
- API endpoint design (RESTful conventions)
- Data validation (Zod schemas)
- Business logic layer
- Database queries and optimizations
- Rate limiting and quotas

**Database Design:**
- Table schema and relationships
- Indexes for query performance
- Row-Level Security (RLS) policies
- JSONB vs normalized columns
- Migration strategy

**Integration Points:**
- External API integration
- Webhook handling
- Asynchronous processing
- Cache invalidation

### 4. Evaluate Tradeoffs

For each major decision, consider:

**Performance:**
- Response time impact
- Database query efficiency
- Caching opportunities
- Network requests

**Scalability:**
- Can this handle 10x current load?
- Database query patterns
- Memory usage
- API rate limits

**Security:**
- Authentication requirements
- Authorization rules (RLS)
- Data validation
- Sensitive data handling

**Maintainability:**
- Code complexity
- Testing difficulty
- Developer experience
- Documentation needs

**Cost:**
- Infrastructure costs
- External service costs
- Development time
- Maintenance burden

### 5. Document Decision

Use the ADR template (`assets/adr-template.md`) to document significant decisions:

**ADR Structure:**
- **Title:** Short noun phrase (e.g., "Use WebSockets for Real-time Collaboration")
- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Context:** What problem are we solving? What constraints exist?
- **Decision:** What did we decide and why?
- **Consequences:** What are the positive and negative outcomes?
- **Alternatives Considered:** What other options did we evaluate?

**Example Decision:**

```markdown
# ADR 001: Use Server-Sent Events for Itinerary Generation Streaming

**Status:** Accepted

**Context:**
A Claude API operation takes 15-45 seconds. Users need real-time feedback to understand progress and reduce perceived wait time.

**Decision:**
Use Server-Sent Events (SSE) to stream progress from the Claude API to the frontend. Update UI progressively as content becomes available.

**Consequences:**
✅ Reduced perceived latency
✅ Better user experience with progress indicators
✅ Simpler than WebSockets (unidirectional)
❌ Requires special handling for API routes
❌ Limited browser support (IE11 not supported)

**Alternatives Considered:**
- WebSockets: Overkill for unidirectional streaming
- Polling: Higher latency, more server load
- Wait for full response: Poor UX for 30+ second operations
```

## Project-Specific Patterns

### Next.js App Router Conventions

**Server Components (default):**
- Use for data fetching and initial page load
- Can directly access Supabase server client
- Cannot use hooks or browser APIs

**Client Components:**
- Use for interactivity (forms, buttons, state)
- Mark with `"use client"` directive
- Can use React hooks and browser APIs

**API Routes:**
- Location: `src/app/api/[route]/route.ts`
- Export named functions: GET, POST, PATCH, DELETE
- Always validate with Zod schemas
- Return standardized error format

### Supabase Patterns

**RLS Policies:**
```sql
-- Owner-only access pattern
CREATE POLICY "Users can CRUD their own items"
ON items
FOR ALL
USING (auth.uid() = user_id);

-- Public read, owner write pattern
CREATE POLICY "Public read access"
ON items FOR SELECT
USING (true);

CREATE POLICY "Owner write access"
ON items FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

**JSONB Usage:**
- Use for semi-structured data (itinerary details, preferences)
- Add GIN indexes for query performance
- Validate structure in application code (Zod)

### State Management Patterns

**Zustand for Global State:**
```typescript
// Prefer Zustand for complex state with actions
const useItineraryStore = create<State & Actions>((set) => ({
  itinerary: null,
  setItinerary: (itinerary) => set({ itinerary }),
}));
```

**React State for Local UI:**
```typescript
// Use React state for component-local UI state
const [isOpen, setIsOpen] = useState(false);
```

### Error Handling Patterns

**API Routes:**
```typescript
// Standardized error response
return NextResponse.json(
  { error: 'Resource not found', code: 'NOT_FOUND' },
  { status: 404 }
);
```

**Frontend:**
```typescript
// Use toast notifications for user-facing errors
toast.error('Failed to generate itinerary. Please try again.');

// Log detailed errors to Sentry
Sentry.captureException(error, { extra: { context } });
```

## Checklist: Architecture Design Complete

Before moving to implementation, verify:

- [ ] Requirements are clearly documented
- [ ] All system components are identified
- [ ] Data models and schemas are designed
- [ ] API endpoints are specified
- [ ] State management approach is chosen
- [ ] Error handling strategy is defined
- [ ] Performance considerations are addressed
- [ ] Security requirements are met
- [ ] Testing strategy is outlined
- [ ] ADR created for significant decisions (if applicable)
- [ ] Stakeholders have reviewed and approved design
