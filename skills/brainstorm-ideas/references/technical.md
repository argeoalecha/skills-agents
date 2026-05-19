# Technical Problem Methodologies

Use for architecture decisions, stack selection, system design, agent design, debugging, and engineering trade-offs.

---

## 1. First Principles Thinking
**Source:** Aristotelian logic (Aristotle, ~350 BC) — "a first principle is the first basis from which a thing is known." Modernized and popularized by Elon Musk (SpaceX, Tesla) and applied broadly in engineering decision-making. Also documented in *The Great Mental Models Vol. 1* (Shane Parrish, Farnam Street, 2019).
**Answers:** What is actually true here, stripped of all assumptions, analogies, and inherited conventions?
**Best for:** Architecture decisions where conventional wisdom may be wrong; cost/performance optimization; justifying non-standard approaches

### Core Concept
Most technical decisions are made by **analogy** ("we do it this way because everyone does it this way").
First principles breaks this by asking: if you had to justify every decision from scratch, what would you actually choose?

### Application
1. **State the goal** — what outcome does the system need to produce?
2. **List all current assumptions** — everything you're taking for granted about the approach
3. **Challenge each assumption** — ask "Is this actually true, or is it just the convention?"
4. **Identify the atomic truths** — what do you know for certain about the constraints (latency, cost, scale, team size)?
5. **Rebuild the solution** from those atomic truths, ignoring prior art initially
6. **Reintroduce prior art selectively** — where does it help? Where does it add unnecessary complexity?

### Assumption Challenge Patterns
- "We need a microservices architecture" → Do we actually have independent scaling requirements today?
- "We need Redis for caching" → What's the actual read latency problem? Have we measured it?
- "We need Kubernetes" → What's our actual deployment complexity and team ops capacity?
- "We need a vector database" → What's the actual retrieval task? Could plain SQL with pg_vector work?

### Example — Multi-agent AI system design
**Assumption:** "We need LangGraph because we need stateful multi-agent workflows."
**First principles challenge:**
- What state actually needs to persist between agent calls? (conversation history + task status)
- Does LangGraph's state machine add value, or does it add complexity we don't need yet?
- What's the simplest structure that handles the state we actually need?

**Atomic truths:** Supabase already manages persistent state. The workflow has 3 sequential steps with one conditional branch. Team size is 1.

**Rebuilt solution:** Simple Python orchestrator with Supabase state table. Add LangGraph only if workflow complexity grows beyond 5 nodes or requires parallel branches.

---

## 2. Constraint Analysis (Theory of Constraints)
**Source:** Eliyahu M. Goldratt, *The Goal* (1984) and *Theory of Constraints* (1990), North River Press
**Answers:** What is the single bottleneck that limits the entire system's output — and what should we do about it?
**Best for:** Performance optimization, system throughput problems, pipeline debugging, capacity planning

### Core Concept
Every system has exactly one constraint at any point in time that limits overall throughput.
Optimizing anything other than the constraint is waste — it doesn't improve system output.

### The Five Focusing Steps

1. **Identify** the constraint — what is the single slowest, most limited part of the system?
2. **Exploit** the constraint — get maximum output from it without major investment
3. **Subordinate** everything else — align all other parts of the system to support the constraint
4. **Elevate** the constraint — if exploitation isn't enough, invest in expanding the constraint's capacity
5. **Repeat** — once the constraint is resolved, a new one emerges; find and fix it

### Constraint Identification Techniques
- **Queue buildup:** Where does work pile up waiting? That's the constraint.
- **Utilization analysis:** What component is at or near 100% utilization while others idle?
- **Latency profiling:** In a pipeline, which step takes the longest?
- **Error propagation:** Which failure cascades into the most downstream problems?

### Example — AI data pipeline is slow
Steps: Data ingestion → Embedding generation → Vector store upsert → LLM query → Response formatting

**Profile results:** Embedding generation = 4.2s, all other steps < 0.3s combined.

**TOC application:**
1. **Constraint identified:** Embedding generation
2. **Exploit:** Batch embed instead of per-document; use async calls
3. **Subordinate:** Pre-fetch documents during off-peak; don't wait for real-time requests
4. **Elevate:** Switch from OpenAI ada-002 to a local embedding model if batching isn't enough
5. Don't optimize the vector store until embedding is no longer the bottleneck

---

## 3. TRIZ for Technical Contradictions
**Source:** Genrich Altshuller — see `references/ideation.md` for full TRIZ background.
**Technical application focus** documented here separately.
**Answers:** How do we resolve engineering trade-offs where improving one parameter degrades another?

### 40 Inventive Principles Most Relevant to Software/AI Systems

| # | Principle | Software/AI Application |
|---|---|---|
| 1 | **Segmentation** | Split monolith into services; separate read/write paths; isolate agent roles |
| 2 | **Taking out (Extraction)** | Separate the interfering component; extract the problematic function |
| 3 | **Local quality** | Different parts of the system optimized differently (e.g., hot/cold storage) |
| 9 | **Preliminary anti-action** | Add circuit breakers, retries, and fallbacks before failure modes appear |
| 10 | **Preliminary action** | Pre-compute, pre-cache, pre-warm — do work before it's requested |
| 15 | **Dynamics** | Make system parameters adaptive rather than fixed (dynamic batching, adaptive rate limiting) |
| 17 | **Another dimension** | Move from synchronous to async; add a queue layer |
| 25 | **Self-service** | Let the component handle its own optimization (auto-scaling, self-healing) |
| 26 | **Copying** | Replace expensive operation with cheaper approximation (cached result, smaller model) |
| 35 | **Parameter changes** | Change data structure, encoding, or representation to resolve the contradiction |
| 40 | **Composite materials** | Combine approaches (hybrid retrieval: keyword + semantic; hybrid rendering: SSR + CSR) |

### Application for Technical Problems
1. State the contradiction: "If I increase [parameter A], then [parameter B] degrades"
2. Identify which category the contradiction falls into (speed vs. accuracy, cost vs. quality, flexibility vs. security)
3. Select 2–3 applicable principles from the table
4. Generate one concrete solution idea per principle
5. Evaluate using the convergence framework

### Example — RAG system contradiction
**Contradiction:** Increasing chunk size improves answer quality but increases latency and cost.

- **Principle #26 — Copying:** Cache responses for common queries; serve from cache, not re-retrieval
- **Principle #10 — Preliminary action:** Pre-generate answers for top-100 anticipated questions
- **Principle #3 — Local quality:** Use large chunks for complex queries, small chunks for factual lookups — route by query type
