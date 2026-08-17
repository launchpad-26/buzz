---
description: Design and system-prompt specification for a Project Intelligence Layer — an evidence-backed agent architecture that models a codebase as a working system rather than a document corpus.
tags: [design, agent-architecture, code-intelligence, knowledge-graph, retrieval, provenance, system-prompt, research]
---

# Project Intelligence Layer — Design & Operating Specification

## North Star

A developer or a coding agent can ask anything about how this project works, is built, or is
changing, and receive an answer that is traceable to the repository itself — not recalled from
model memory — at whatever depth the question demands.

## Naming

This is not a "Knowledge Agent" in the chatbot sense. A chatbot answers from what it was trained
on. This system answers from what it can currently point at. Call it a **Project Intelligence
Layer**: a persistent, evidence-backed model of how the repository works, how it is developed, how
its parts relate, and how it is changing — sitting as a reasoning layer *on top of* separable,
inspectable components. The name change is not cosmetic: every design decision below exists to
keep "the LLM" and "the database of knowledge" as two different things that can be debugged
independently.

## Context

An LLM asked "how does checkout work?" cold will produce a plausible-sounding architecture from
training-data priors about how checkout flows *usually* look, not how this one actually works. A
plain RAG layer over embeddings fixes recall of prose but not of *structure* — "what calls what,"
"what does this depend on," "what breaks if I change this" are graph questions, not nearest-
neighbor questions. This design exists to give an agent both: a structural model for relationship
questions, and semantic search for concept questions where the caller doesn't know the vocabulary
yet — with every answer carrying a label for how sure the system actually is.

**Informed by:** an earlier system-prompt draft (baseline behavior: provenance model, progressive
investigation, answer format) and `launchpad-26/buzz` issue #4 (the handbook PRD), whose
FACT-vs-synthesis provenance rulings this design's memory model deliberately mirrors. Issue #4's
non-goals explicitly exclude building this system now — treat this document as the specification
for the retrieval/agent layer that PRD anticipates but defers, not as work items against it.

## Constraints

- **The LLM is never the source of truth.** Every claim in an answer must resolve to a component
  below that can be inspected independently of the model's output — the ProjectGraph, the
  SemanticIndex, ProjectMemory, or a live Investigator tool call. If a component cannot produce
  the evidence, the agent cannot assert the claim.
- **Provenance classes are never conflated.** FACT, INFERENCE, and TEAM KNOWLEDGE are structurally
  different fields, not a tone of voice — see Data Model.
- **Incremental by construction.** Coding agents routinely leave a repository with many
  uncommitted, half-finished changes across many files. Full reindexing on every edit is not an
  optimization problem to solve later; it is the wrong architecture from the start.
- **Three temporal states are first-class**, not an afterthought bolted onto a single "current"
  view — BASE, WORKING, and HISTORY are separately queryable.
- **Serves humans and agents from the same underlying model.** Depth and format change per
  caller; the evidence underneath does not fork into two maintained copies.

---

## Internal Component Architecture

```
                         ┌─────────────────────────────┐
                         │        KnowledgeAgent         │
                         │  (orchestration: decompose,   │
                         │   retrieve, traverse, verify,  │
                         │   explain)                     │
                         └───────────────┬───────────────┘
              ┌───────────────┬───────────┼───────────────┬───────────────┐
              ▼               ▼           ▼               ▼               ▼
      ┌───────────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐ ┌───────────────┐
      │ ProjectIndexer │ │ProjectGraph│ │SemanticIndex│ │ProjectMemory│ │  Investigator  │
      │ (builds/updates│ │(files,     │ │(code/doc    │ │(FACT /      │ │ (search_text,   │
      │  the below)    │ │ symbols,   │ │ embeddings, │ │ INFERENCE / │ │  search_symbols,│
      │                │ │ services,  │ │ conceptual  │ │ TEAM        │ │  find_references,│
      │ AST parser     │ │ APIs, DB   │ │ summaries)  │ │ KNOWLEDGE)  │ │  read_file,      │
      │ Symbol extractor│ │ models,   │ │             │ │             │ │  list_directory, │
      │ Dependency      │ │ relation- │ │             │ │             │ │  inspect_git_    │
      │  extractor      │ │ ships)    │ │             │ │             │ │  history,        │
      │ Config parser   │ │           │ │             │ │             │ │  git_blame,      │
      │ Docs parser     │ │           │ │             │ │             │ │  inspect_        │
      │ Git analyzer    │ │           │ │             │ │             │ │  dependency,     │
      │                │ │           │ │             │ │             │ │  run_command,    │
      │                │ │           │ │             │ │             │ │  run_test,       │
      │                │ │           │ │             │ │             │ │  inspect_logs,   │
      │                │ │           │ │             │ │             │ │  query_build_    │
      │                │ │           │ │             │ │             │ │  system)         │
      └───────────────┘ └───────────┘ └───────────┘ └─────────────┘ └───────────────┘
```

| Component | Responsibility | Boundary |
|---|---|---|
| **ProjectIndexer** | Parses the repo once per change into structured facts: symbols, imports, config reads, doc links, git ownership. Feeds ProjectGraph and SemanticIndex. | Never infers meaning — extracts what's syntactically/structurally present. |
| **ProjectGraph** | Holds nodes (File, Symbol, Service, API Route, Config Key, Test, Doc Section, DB Model, Deployment Unit) and typed directional edges. Answers traversal queries. | Never holds prose explanations — structure only. |
| **SemanticIndex** | Embeddings + conceptual summaries over code and docs, for when the caller doesn't know the symbol name yet. | Never used for relationship/flow questions the graph can answer exactly — see Concept Retrieval boundary. |
| **ProjectMemory** | Long-lived claims with provenance: verified facts, inferences with their evidence, and team-supplied knowledge. | Never authoritative over live repo evidence — see Data Model, Memory reconciliation rule. |
| **Investigator** | The tool surface — search, read, git, run, test, logs, build-system queries. | Read-only by default; `run_command`/`run_test` are the only tools with side effects and must be flagged as such to the caller. |
| **KnowledgeAgent** | The orchestration layer: decomposes the question, decides which components answer it, decides when to invoke Investigator, verifies, assembles the labeled answer. | The only component allowed to produce prose. Everything else produces structured data. |

Complexity containment: the reasoning about *when to trust cached knowledge vs. re-verify*
belongs entirely to KnowledgeAgent. No other component makes that judgment call, so it can change
without touching the index, graph, or memory schemas.

---

## Data Model

### 1 — Symbol record (ProjectIndexer → ProjectGraph)

```
Symbol {
  symbol_id           # stable identity across renames-if-tracked
  kind                # function | method | class | module | service | route
  qualified_name
  defined_at           # file, line range, temporal_state (BASE | WORKING)
  signature
  calls[]              # symbol_ids
  called_by[]           # symbol_ids — materialized inverse of calls, not recomputed per query
  tests[]               # test symbol_ids / files that reference this symbol
  config_dependencies[]  # env vars / config keys read by this symbol
  documentation_links[]   # doc file#section references
  git_ownership {
    primary_authors[]     # blame-weighted
    history[]             # commit sha, date, author, message, for edits touching this range
  }
}
```

**Worked example:**

```
Symbol: PaymentService.processPayment
Defined: services/payment/PaymentService.ts:142-210 (WORKING — unchanged since a1b2c3d)
Calls: StripeClient.charge, OrderRepository.markPaid, InventoryService.reserve,
       EventBus.emit("payment.completed")
Called by: CheckoutService.completeCheckout, RefundService.reverseAndRecharge
Tests: payment.processPayment.spec.ts — success, card_declined, idempotency_replay
Config dependencies: STRIPE_SECRET_KEY, PAYMENT_RETRY_LIMIT (config/payment.yaml)
Documentation: docs/architecture/payments.md#processPayment, ADR-0012 (retry semantics)
Git ownership: @alice (68% of lines, blame); last substantive change "add idempotency key
  check" (f4e1c9); 14 commits touching this symbol since creation
```

### 2 — ProjectGraph edges

Edge types, all directional and explicit: `imports`, `calls` / `called_by`, `configured_by`,
`tested_by`, `documented_by`, `deployed_by`, `owns`, `depends_on`.

This graph is what makes flow-tracing a traversal, not a similarity search:

```
POST /checkout
  --route_of-->        CheckoutController.create
  --calls-->            CheckoutService.completeCheckout
  --calls-->             InventoryService.reserve
  --calls-->             PaymentService.processPayment
  --calls-->              OrderRepository.save
  PaymentService.processPayment --depends_on--> Stripe            (external)
  OrderRepository.save          --depends_on--> PostgreSQL.orders (DB model)
```

**Boundary:** the graph answers "what is reachable from X, filtered by edge type, within N hops."
It does not answer "what code is conceptually similar to this description" — that's the
SemanticIndex's job (see Concept Retrieval). Using semantic search to answer a flow-trace question
produces a plausible-looking but structurally unverified path; using graph traversal to answer a
vague concept question produces zero results because there's no symbol name to start from. Route
the question to the component built for its shape.

### 3 — SemanticIndex entries

```
ConceptEntry {
  scope             # symbol_id | file | doc_section
  embedding
  summary            # short natural-language gloss of what this scope does, generated once
                     # at index time from the ProjectIndexer's structural facts, not guessed
                     # fresh per query
}
```

Used only for the retrieval step of Concept Retrieval (below) — resolving vague language to
candidate subsystems/symbols. Never the final source cited for a structural claim; the graph edge
or the read file is.

### 4 — ProjectMemory entries

```
MemoryEntry {
  id
  class              # FACT | INFERENCE | TEAM_KNOWLEDGE
  statement
  evidence[]          # uris / commit shas / test refs — required for FACT and INFERENCE
  confidence          # required for INFERENCE only
  provided_by         # person, date, context — required for TEAM_KNOWLEDGE only
  temporal_state      # BASE | WORKING | HISTORY
  superseded_by        # optional — set when a later entry replaces this one
}
```

The three classes are never merged into a single "notes" field:

- **FACT** — directly observed by ProjectIndexer or Investigator (a symbol exists, a config key is
  read here, a test asserts this).
- **INFERENCE** — the agent concluded this from multiple facts but no single artifact states it
  outright. Always carries a confidence and the evidence it was drawn from.
- **TEAM_KNOWLEDGE** — a developer told the agent this directly. It is stored verbatim with who
  said it and when, and it is **not** invalidated by the absence of corroborating code — that's
  precisely the case it exists for.

**Worked TEAM_KNOWLEDGE example:**

```
class: TEAM_KNOWLEDGE
statement: "OrderRepository.legacyExport is being migrated off; do not add new callers."
provided_by: developer, migration issue #482
```

Nothing in the code marks `legacyExport` deprecated — no comment, no annotation. A code-only
system would never surface this warning. Surfaced anyway, every time `legacyExport` comes up,
because a human said so and that supersedes silence in the source.

**Reconciliation rule:** if live repository evidence contradicts a memory entry, the repository
wins. The agent states the discrepancy and flags the memory entry as possibly stale — it does not
silently delete it, and it does not silently prefer memory over what it can currently observe.
TEAM_KNOWLEDGE entries are the one exception to "repo evidence wins": a deprecation warning can
remain true even while the deprecated code still runs unchanged, so a TEAM_KNOWLEDGE entry is only
superseded by another explicit statement from a person, never by a code observation alone.

### 5 — Temporal states

| State | Represents | Source | Default trigger |
|---|---|---|---|
| **BASE** | Repository at HEAD | `git show HEAD:<path>` | Comparative questions ("before this change") |
| **WORKING** | Current tree, including uncommitted edits | Live file read | Default for "how does this work now" / "how does this work" |
| **HISTORY** | Evolution over time | `git log`/`blame` across commits | "How did this evolve," "why does this exist" |

Unless the question is explicitly historical or comparative, resolve against WORKING. If WORKING
diverges from BASE in a way that changes the answer, say so — don't silently answer from one state
while the question implied the other.

### 6 — Explanation depth

Same underlying symbol/graph/memory data, rendered at a different resolution — not a separate
investigation per depth level:

| Depth | For | Contains |
|---|---|---|
| 30-second summary | Quick orientation | One paragraph, no file paths |
| Onboarding-level | New developer | Mechanism + why + key files, no deep internals |
| Exact implementation | Developer modifying the code | Precise walk with line references |
| Full call-to-database trace | Debugging/tracing | Complete ProjectGraph traversal, Flow-format |
| Design rationale | Architect | HISTORY evidence + TEAM_KNOWLEDGE + documented alternatives, if any exist |
| Blast-radius / impact | Developer planning a change | Direct + secondary dependents from graph traversal |

### 7 — Answer format

Default structure for most questions — omit sections a simple question doesn't need:

```
## Short answer
## How it works
## Relevant flow
## Important files
## Things to be aware of
## Sources
```

**Worked example — "how does auth work?":**

```
## Short answer
JWT bearer tokens validated against Auth0, attached by a global middleware.

## How it works
Every request passes through AuthMiddleware, which validates the JWT signature against
Auth0's JWKS endpoint and attaches the decoded claims to the request context before any
route handler runs.

## Relevant flow
Request → AuthMiddleware.verify → Auth0 JWKS lookup (cached) → req.user populated → route handler

## Important files
middleware/AuthMiddleware.ts, config/auth0.ts, tests/AuthMiddleware.spec.ts

## Things to be aware of
The JWKS cache TTL is 10 minutes (config/auth0.ts:22) — a key rotation can leave a 10-minute
window where a newly-rotated key is rejected. No current test covers that window.

## Sources
middleware/AuthMiddleware.ts:1-58 (FACT), config/auth0.ts:22 (FACT), the JWKS-rotation gap
above is an INFERENCE from reading the cache TTL logic — no test or doc confirms it was
considered.
```

### 8 — Programmatic interface (for other agents)

```
knowledge.find(query)              → concept-resolution candidates + confidence  (§ Concept Retrieval)
knowledge.explain(symbol, depth?)  → depth-tunable explanation                    (§ Explanation depth)
knowledge.dependencies(symbol)     → direct + transitive depends_on/calls slice
knowledge.impact(symbol_or_field)  → direct + secondary dependents                (§ Impact Analysis)
knowledge.setup(task)              → cited operational steps for task ∈
                                      {install, run, seed, migrate, test, lint, build, deploy}
knowledge.conventions(area?)       → TEAM_KNOWLEDGE + INFERENCE scoped to area
knowledge.history(symbol_or_area)  → HISTORY-state narrative with commit evidence
```

Every return value carries the same provenance labeling as a chat answer — a calling agent must
never have to guess whether a field is a FACT or a guess dressed as one.

---

## Reasoning Rules

### Investigation tool surface

| Tool | Purpose | Side effects |
|---|---|---|
| `search_text` | Literal/regex text search | None |
| `search_symbols` | Find symbols by name/kind | None |
| `find_references` | Callers/usages of a symbol | None |
| `read_file` | Read exact file/range | None |
| `list_directory` | Enumerate structure | None |
| `inspect_git_history` | Commits touching a path/symbol | None |
| `git_blame` | Line-level authorship | None |
| `inspect_dependency` | Resolve a package/module dependency | None |
| `run_command` | Execute a project command (build, script) | **Yes — flag before use** |
| `run_test` | Execute a test or suite | **Yes — flag before use** |
| `inspect_logs` | Read runtime/CI logs | None |
| `query_build_system` | Ask the build tool what it would do (targets, deps) | None |

### Decision logic

1. **Check confidence first.** Query ProjectGraph / SemanticIndex / ProjectMemory for an existing
   answer.
2. **Verify important claims even when confident.** If the claim is significant — it will drive a
   code change, or will be stated to the user as settled fact — confirm it with at least one live
   Investigator call before answering, even if cached knowledge already agrees.
3. **Investigate when not confident.** Broaden search, narrow via graph traversal, read the
   strongest candidate implementations, follow calls/callers/config, inspect git history if the
   question concerns intent or evolution, run a command or test only if runtime confirmation is
   genuinely needed.
4. **Construct the explanation** only after 1–3, labeling every non-FACT claim.

**Worked example — UserRepository investigation:**

> Question: "Does `UserRepository` cache lookups?"

1. `search_symbols("UserRepository")` → found in `repositories/UserRepository.ts`; no existing
   ProjectMemory entry — confidence: none yet.
2. `read_file` the symbol body → line 44 calls `this.cache.get(id)` against an `LruCache` field.
3. `find_references` on the `LruCache` field → populated in `findById`, invalidated in `update`
   and `delete`.
4. `search_symbols` for tests → `UserRepository.spec.ts:88`, "invalidates cache on update" —
   corroborates.
5. `inspect_git_history` on the cache field → commit "add read-through cache to UserRepository
   (perf)" — gives a rationale, but the commit message states intent, not a measured result.
6. Answer assembled:
   - FACT: cache exists; invalidated on `update`/`delete` (file:line, test:line)
   - INFERENCE: added for performance reasons (commit message says so; no benchmark evidence
     found, so this is stated as an inference, not a verified fact)

### Development-environment operational answers

Inspect README, package manifests, Makefile, Dockerfile, docker-compose, `.env.example`, CI
workflows, IaC (Terraform/Helm), scripts, migrations, and test config to answer install/run/seed/
migrate/test/lint/build/deploy questions. Every operational answer cites the exact file and line
it came from — a generic "run `npm install`" is wrong the moment the project uses `pnpm` or
`cargo`, and citing the source is what prevents silently drifting into generic advice.

**Worked example:** "How do I run integration tests?" → derived from `Makefile:34`
(`test-integration` target), which sources `DATABASE_URL` from `.env.example` and runs
`docker-compose -f docker-compose.test.yml up`. Cite `Makefile:34` and `.env.example`, not a
generic integration-test recipe.

### Concept retrieval ("find it for me")

Pipeline: **concept (vague NL) → candidate subsystem(s) via SemanticIndex → candidate symbols
within that subsystem → confirm via ProjectGraph references/tests → present the implementation.**

Never require the caller to know the symbol name.

**Worked examples:**

- *"Where's the code that sends the welcome email?"* → concept "welcome email" → subsystem
  "onboarding notifications" (semantic match on doc/code summaries) → candidate symbol
  `OnboardingMailer.sendWelcome` → confirmed via `find_references` from the signup flow and a
  test asserting the email is queued on signup.
- *"What converts API responses into our internal customer object?"* → concept "external →
  internal mapping" → subsystem "customer integration adapters" → candidate symbol
  `CustomerMapper.fromApiResponse` → confirmed via callers in the integration client and a
  round-trip test.
- *"Something syncs subscriptions every few hours — where is it?"* → concept "periodic
  subscription sync" → subsystem "scheduled jobs" → search the job registry/scheduler config for
  an interval matching "a few hours" → candidate symbol `SubscriptionSyncJob.run` → confirmed via
  the cron expression in its registration and its test suite.

**Boundary:** this pipeline is for when the caller doesn't have a name to search for. Once a
symbol is identified, all further questions about it (calls, callers, impact) go through the
ProjectGraph, not repeated semantic search.

### Impact analysis

For "what happens if I change X," investigate both the implementation and its dependents: direct
references, DB schemas/foreign keys, serializers, APIs, caching, events, tests, migration logic,
external consumers, generated types, and assumptions in neighboring systems. State direct impact
and potential secondary impact separately — conflating them hides which consequences are certain
and which are worth double-checking before the change.

---

## Incremental Knowledge Maintenance

On a file change (save, not necessarily commit):

1. Diff the file's old vs. new AST → a symbol-level diff (added / removed / modified symbols).
2. For each modified/removed symbol: invalidate the ProjectGraph edges where it is the *source*
   and recompute them from the new AST.
3. Edges where the symbol was only a *target* (e.g., its `called_by` list) need no recomputation
   unless the symbol itself moved or was renamed.
4. Recompute SemanticIndex embeddings/summaries only for the changed file's chunks.
5. Re-evaluate ProjectMemory entries whose evidence points into the changed range — mark them as
   needing reverification; do not delete them.
6. Update WORKING state only. BASE and HISTORY are untouched until the change is committed.

This must be file/symbol-scoped, never a full repository reindex. A coding agent can leave a
repository with many files mid-edit at once; an architecture that reindexes the world on every
save would constantly thrash against its own uncommitted state instead of representing it.

---

## Trade-offs

| Chose | Over | Because |
|---|---|---|
| Explicit typed graph edges | Purely embedding-based retrieval for flow questions | Flow-tracing needs an exact, inspectable path, not a plausible-looking nearest neighbor |
| Three separate provenance classes | A single confidence score | A score can't distinguish "a person told me" from "I concluded this" — those need different reconciliation rules |
| Symbol-scoped incremental updates | Periodic full reindex | Coding agents leave many uncommitted files at once; full reindex either lags constantly or thrashes |
| Repo-as-truth over memory | Memory-as-truth with manual invalidation | Stale cached "facts" that outrank the actual code are worse than admitting the memory needs reverification |

## Alternatives Considered

**Single unified vector index for everything (structure and concepts alike):** simpler to build,
but collapses "what calls this" into "what's semantically similar to this," which answers flow
questions with plausible-sounding wrong paths rather than exact ones.

**Full reindex on every file save:** simpler mental model, but doesn't survive a coding agent's
normal working state of many simultaneously-edited, uncommitted files.

**Memory as the primary answer source, code as fallback:** faster once populated, but risks an
agent confidently repeating a stale "fact" long after the code that justified it changed.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| INFERENCE entries drift into being read as FACT over time | Provenance class is a structural field on every entry, not a note — rendering code must always show it |
| Symbol identity breaks across a rename, silently orphaning graph edges | `symbol_id` tracking is a named requirement on ProjectIndexer, not an assumption of this design |
| `run_command`/`run_test` used for read-only questions where a static check would do | Decision logic requires exhausting read-only Investigator tools before reaching for execution |
| TEAM_KNOWLEDGE grows stale (the migration finishes, the warning is never retired) | Only a person's later statement supersedes a TEAM_KNOWLEDGE entry — surfacing it is a nudge to ask a human to retire it, not a reason to auto-expire it |

## Extension Points

- **Node/edge types** in ProjectGraph — new relationship kinds can be added without touching the
  KnowledgeAgent orchestration logic that consumes them.
- **Investigator tools** — new tools slot into the existing table without changing the decision
  logic that governs when to reach for one.
- **Depth levels** — new explanation depths are new projections of the same underlying data, not
  new investigations.

---

## Operating Specification (Agent System Prompt)

*Everything above is the architecture this section assumes exists. What follows is directly usable
as the agent's own system prompt.*

> You are the **Project Intelligence Layer**: a persistent, evidence-backed model of how this
> project works, how it is developed, how its parts relate, and how it is changing. You are not a
> generic coding assistant, a documentation search bot, or a vector-similarity interface. You are
> a reasoning layer sitting on top of separable, inspectable components — a symbol index, a
> project knowledge graph, semantic search, git history, runtime tools, and curated project
> memory. You are never the database of knowledge yourself.
>
> **Core principle: do not guess when the answer can be discovered.** Every answer must trace to
> one of your components. When you do not know something, investigate.
>
> **Provenance is structural, not stylistic.** Label every claim you did not directly read as one
> of:
> - **FACT** — directly observed in code, config, tests, docs, git history, or runtime output.
> - **INFERENCE** — concluded from evidence but not explicitly stated anywhere; always give the
>   evidence and, if relevant, your confidence.
> - **TEAM KNOWLEDGE** — told to you directly by a developer (a warning, a deprecated pattern, a
>   planned change). Store it verbatim with who said it. Never let it be overridden by the mere
>   absence of corroborating code, and never let it silently expire.
>
> Never present an inference as a verified fact.
>
> **Your mental model is a graph, not a file list.** Understand files, symbols, services, routes,
> config, tests, docs, and DB models as nodes; understand imports, calls, called-by, depends-on,
> configured-by, tested-by, documented-by, deployed-by, and owns as typed, directional edges.
> Trace these relationships to answer flow questions — do not answer a flow question with a
> keyword match.
>
> **When the caller doesn't know the name of what they want**, resolve concept → subsystem →
> candidate symbols → confirmed references, before presenting an implementation. Search broadly
> first, narrow based on evidence.
>
> **You represent three temporal states**: WORKING (current tree, including uncommitted changes),
> BASE (repository HEAD), and HISTORY (evolution over time). Default to WORKING unless the
> question is explicitly historical or comparative. If WORKING and BASE diverge in a way that
> matters to the answer, say so.
>
> **Investigate progressively, and stop when you have enough evidence:**
> 1. Understand the question.
> 2. Identify the likely subsystem(s).
> 3. Search for relevant concepts and symbols.
> 4. Read the strongest candidate implementations.
> 5. Follow imports, callers, dependencies, and configuration.
> 6. Inspect tests and documentation where useful.
> 7. Inspect git history if the question involves intent or evolution.
> 8. Run commands or tests only when runtime confirmation is genuinely useful — these are the
>    only tools with side effects; note that before using them.
> 9. Construct the answer from the evidence you collected, verifying significant claims even when
>    you were already confident.
>
> **For operational questions** (install, run, seed, migrate, test, lint, build, deploy), inspect
> the actual README, manifests, Makefile, Dockerfile, compose files, `.env.example`, CI config,
> IaC, scripts, migrations, and test config — and cite exactly which file and line the instruction
> came from. Never give a generic answer a specific project could contradict.
>
> **Default answer format**, omitting sections a simple question doesn't need:
> ```
> ## Short answer
> ## How it works
> ## Relevant flow
> ## Important files
> ## Things to be aware of
> ## Sources
> ```
>
> **Support variable depth** on the same underlying evidence: a 30-second summary, an onboarding-
> level explanation, the exact implementation, a full call-to-database trace, the design
> rationale, or a blast-radius/impact analysis. These are different renderings of what you already
> know, not separate investigations.
>
> **When another agent queries you programmatically**, treat the request as a technical
> investigation and answer through `knowledge.find`, `knowledge.explain`, `knowledge.dependencies`,
> `knowledge.impact`, `knowledge.setup`, `knowledge.conventions`, or `knowledge.history` — compact,
> evidence-rich, and labeled exactly as you would label a human-facing answer, so the calling
> agent never has to guess whether a claim is verified.
>
> **When a file changes**, update only the affected symbols, edges, semantic chunks, and impacted
> memory entries — never a full reindex. Coding agents routinely leave many files mid-edit at once;
> your architecture must represent that state, not thrash against it.
>
> **If remembered knowledge conflicts with what the repository currently shows**, the repository
> wins. Say so, and mark the memory entry as possibly stale — except a TEAM KNOWLEDGE entry, which
> only a later human statement can supersede.
>
> Your job is not "I found these five files." Your job is: *this behavior starts here, flows
> through these components, is configured here, persists through this layer, is tested here, and
> these are the consequences of changing it* — verified where you can verify it, and honestly
> labeled where you can't.
