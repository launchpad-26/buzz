---
id: layers-data-postgres-row-level-security
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum has thirteen members (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) and no member for 'data' or 'postgres'; this node uses type: layers per this batch's own established precedent for launchpad/docs/corpus/layers/data/... documents, overriding whatever type either candidate template's own worked example suggests."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Two templates were read in full before choosing a shape: templates/datastore.md (a full running-instance profile — schema inventory, migration mechanism, access-pattern summary, operational characteristics for one datastore) and templates/reference.md (Diátaxis's Reference form — an information-oriented catalogue of 'the machinery and how it operates,' explicitly bounded against a how-to and against a full datastore profile). This node uses templates/reference.md's shape because its subject — how Buzz enforces tenant isolation across many tables — is a cross-cutting mechanism, not a single running instance's full profile; a full Postgres datastore profile already exists in outline at architecture-containers-postgres and duplicating it here would violate the corpus's 'one independently maintainable idea' rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/templates/reference.md"
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "architecture-containers-postgres (launchpad/docs/corpus/architecture/containers/postgres.md) is a merged, draft-status corpus node that already names community_id as 'the security-relevant boundary the container exists to hold' and explicitly defers table-by-table schema contents and the multi-tenant conformance contract to migrations/0001_initial_schema.sql and docs/multi-tenant-conformance.md, without itself detailing the enforcement mechanism — the gap this node fills."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "A repository-wide search for CREATE POLICY, ENABLE ROW LEVEL SECURITY, and FORCE ROW LEVEL SECURITY across every file in migrations/ (31 SQL files, 0001 through 0031) and every .rs/.sql file in the repository returns zero matches; Postgres row-level security is not implemented anywhere in this codebase at the recorded revision."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='ENABLE ROW LEVEL SECURITY|CREATE POLICY|FORCE ROW LEVEL SECURITY', scope='migrations/**/*.sql, **/*.rs, **/*.sql') -> 0 matches"
  - statement: "migrations/0001_initial_schema.sql is the from-scratch multi-tenant schema and states its own governing contract is docs/multi-tenant-conformance.md; every tenant-scoped table declares community_id UUID NOT NULL REFERENCES communities(id), and primary keys and indexes for channels, channel_members, users, events, event_mentions, and related tables all lead with community_id (e.g. events' PRIMARY KEY is (community_id, created_at, id), and idx_events_community_id is (community_id, id, created_at DESC))."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "buzz-db's query-construction functions in crates/buzz-db/src/event.rs take community_id: CommunityId as an explicit parameter (documented as 'Server-resolved community scope' on EventQuery) and bind it into every SELECT/INSERT/UPDATE statement's WHERE or VALUES clause — e.g. query_events binds q.community_id into 'WHERE e.community_id = ' and 'AND m.community_id = ' for the mentions join, soft_delete_event's UPDATE carries 'WHERE community_id = $1 AND id = $2', and insert_event's INSERT lists community_id as its first column."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs"
  - statement: "crates/buzz-relay/src/tenant.rs implements the 'row zero' host-binding seam: bind_community normalizes the connection's Host header and resolves it to a CommunityId through the HostResolver trait, and every non-success path — an empty/missing host, a host that maps to no community, or a lookup error — returns BindError::UnmappedHost (or BindError::Lookup) and is rejected with what the module's own doc comment calls a 'generic rejection,' with no code path that yields a default or fallback community; a client-supplied token stamp or event h tag may narrow authority but can never override the host-derived community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "crates/buzz-relay/src/conformance/mod.rs's state_for_request builds its AbstractState from TenantContext::community() ('server-resolved, never client input'), and claimed_community_from_event separately extracts the client-claimed community from an event's h tag, with a doc comment stating the relay 'does NOT trust this value for resolution' and that recording the two separately 'is what makes the M2 (claim doesn't-equal resolved) bite visible to the checker' — i.e. the codebase already distinguishes claimed-by-client from resolved-by-server community at the tracing layer, not only in prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs"
  - statement: "docs/multi-tenant-conformance.md's 'Migration gates' section lists, as gate 1 of 5 that 'must' exist 'before multi-tenant mode is admitted': 'Every tenant-scoped table has community_id, RLS policy, and no unique/FK constraint that can be observed across tenants unless explicitly admitted as operator-global' — RLS is named as a future admission requirement for a mode this document frames as not yet admitted, not as a description of current behavior."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "docs/multi-tenant-relay.md is tagged 'draft' at its own top and states in its Scope and Non-Goals section that 'Postgres's internal correctness. RLS enforcement, MVCC snapshot isolation, and ON CONFLICT DO NOTHING semantics are trusted and stated as axioms (Axioms). We prove our composition on top of them; we do not reprove them' — its Axioms section (A-RLS-1 through A-RLS-5) states RLS-enabled tables, a non-superuser NOBYPASSRLS request role, transaction-local app.community_id, and composite-key closure as assumptions the document's safety proof depends on, not as verified facts about this repository's actual Postgres configuration."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs is the executable form of docs/multi-tenant-conformance.md's obligation table; its own module doc comment states 'A row is todo!()-stubbed until the lane it depends on lands on the integration branch' and that its A/B isolation tests 'require a running multi-tenant relay with two host mappings, so they are #[ignore] by default' — the file itself carries #![allow(clippy::todo, unused)], confirming the todo!() stubs are a currently-committed, not historical, state."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "migrations/0029_community_deletion.sql adds a deletion_state column to communities (CHECK IN ('active','quiescing','fenced','tombstone')) and a community_deletion_requests table with a stage CHECK spanning submitted through retention_pending, and its own header comment states 'The community row is never removed: it becomes the permanent name tombstone' and 'every existing community-scoped table receives the same database-enforced write fence' — tenant lifecycle/retention is a durable, lease/fence/checkpoint-guarded state machine, not an ad hoc DELETE."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-db/src/lib.rs's is_community_active queries 'SELECT EXISTS(SELECT 1 FROM communities WHERE id = $1 AND archived_at IS NULL AND deleted_at IS NULL AND deletion_state = 'active')' — a community's lifecycle state (not merely its existence) gates whether it is treated as accepting tenant traffic, giving the isolation boundary a consistency check independent of the community_id column's mere presence on a row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Whether crates/buzz-relay/src/conformance/mod.rs's tracer (JsonlTracer/NoopTracer) is wired into the relay's live single-community request path today, or is exercised only by the not-yet-landed multi-tenant integration branch that conformance_multitenant.rs's stubs are waiting on, was not fully resolved from the files read for this node; the module's own doc comment ('ingest.rs: AuthCheck at check_channel_membership call site... req.rs/event.rs: held back as additive patch for Eva to apply onto Max's req.rs writes') reads as a partially-landed instrumentation effort rather than a fully wired one."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/conformance/mod.rs"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
    confidence: 0.55
  - statement: "Issue #1088's Definition of Done requires this node to name tenancy/security boundaries and failure behavior, and to describe owned data, key access patterns, lifecycle/retention and consistency semantics — the acceptance bar this node is built against, distinct from what its own title and target filename ('row-level-security') would otherwise imply about the mechanism's actual existence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1088 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Postgres tenant isolation (row-level security): reference

This node catalogues how Buzz actually enforces cross-community data isolation
in Postgres today, and states plainly where that enforcement stops. It is
linked from, and zooms one level deeper than, `architecture-containers-postgres`
(`launchpad/docs/corpus/architecture/containers/postgres.md`), which names
`community_id` as "the security-relevant boundary the container exists to
hold" without detailing the mechanism. **The honest finding this node exists to
record: Postgres row-level security (`CREATE POLICY` / `ENABLE ROW LEVEL
SECURITY`) is not implemented anywhere in this repository.** Tenant isolation
is enforced today by a discriminator column plus server-side, fail-closed
query scoping — a different, and weaker in the database-defense-in-depth
sense, mechanism than RLS. See *Boundary* below for what that means and does
not mean.

## Enforcement points

| Enforcement point | Mechanism | Evidence |
|---|---|---|
| Row-zero host binding | Every inbound connection's `Host` header is normalized and resolved to a `CommunityId` server-side, before any handler observes tenant data. An empty, unmapped, or unresolvable host is rejected with the same generic error as any other unmapped host — there is no code path that yields a default or fallback community. A client-supplied token stamp or event `h` tag may narrow authority but never overrides the host-derived community. | `crates/buzz-relay/src/tenant.rs` (`bind_community`, `HostResolver`, `BindError`) |
| Schema discriminator column | Every tenant-scoped table carries `community_id UUID NOT NULL REFERENCES communities(id)`. Primary keys and indexes lead with `community_id` rather than treating it as an incidental filter column — e.g. `events`' primary key is `(community_id, created_at, id)`, and `idx_events_community_id` is `(community_id, id, created_at DESC)`. | `migrations/0001_initial_schema.sql` |
| Query-level filtering | `buzz-db`'s data-access functions take `community_id: CommunityId` as an explicit, non-optional parameter and bind it into every read and write statement's `WHERE`/`VALUES` clause. There is no code path in `buzz-db`'s event module that constructs a community-scoped query without it. | `crates/buzz-db/src/event.rs` (`query_events`, `insert_event`, `soft_delete_event`, and siblings) |
| Claimed-versus-resolved tracing | The relay's conformance tracer records the community a client *claims* (an event's `h` tag) separately from the community the server actually *resolved* the connection to, specifically so a mismatch between the two is observable rather than silently normalized away. | `crates/buzz-relay/src/conformance/mod.rs` (`claimed_community_from_event`, `state_for_request`) |
| Lifecycle / retention gating | A community's own row carries a `deletion_state` lifecycle (`active` -> `quiescing` -> `fenced` -> `tombstone`); the row itself is never removed — it becomes a permanent tombstone. `is_community_active` gates on lifecycle state, not merely row existence, before treating a community as live traffic. Whole-community deletion is a durable, lease/fence/checkpoint-guarded control plane that applies "the same database-enforced write fence" to every community-scoped table, not an ad hoc `DELETE`. | `migrations/0029_community_deletion.sql`, `crates/buzz-db/src/lib.rs` (`is_community_active`) |
| RLS — documented intent, not implemented behavior | `docs/multi-tenant-conformance.md` lists "every tenant-scoped table has `community_id`, RLS policy, ..." as migration gate 1 of 5 required "before multi-tenant mode is admitted" — a future requirement, not a present one. `docs/multi-tenant-relay.md`, tagged `draft`, states RLS enforcement as a *trusted axiom* (A-RLS-1..5) its safety proof builds on top of rather than a verified property of this deployment, and its own executable conformance suite (`crates/buzz-test-client/tests/conformance_multitenant.rs`) is `todo!()`-stubbed and `#[ignore]`d "until the lane it depends on lands on the integration branch." | `docs/multi-tenant-conformance.md`, `docs/multi-tenant-relay.md`, `crates/buzz-test-client/tests/conformance_multitenant.rs` |

Prose beyond the table, permitted by the reference form's own nuance for
describing how something works: the enforcement above composes as
defense-*in-depth-of-one-layer* today — host binding decides `community_id`
once per connection, and every subsequent read or write must independently
carry and check that same value in application code. There is no database-level
backstop that would still hold if an application code path forgot to bind
`community_id` into a query; the schema's `NOT NULL` constraint stops a row
from being written *without* a community, but does not stop a query from
being written that reads or writes the *wrong* one. That is the concrete gap
RLS, if implemented, would close — and precisely the gap `docs/multi-tenant-relay.md`
names as a trusted axiom rather than a proven property.

## Boundary

This node does not describe:
- The full Postgres datastore profile — technology version, connection
  pooling, migration mechanism, or the complete schema/namespace inventory.
  That is `architecture-containers-postgres`'s territory today, and would be a
  future `datastore.md`-shaped node's territory if one is written; duplicating
  either here would violate the corpus rule that one node covers one
  independently maintainable idea.
- How to add a new tenant-scoped table or migration correctly (a how-to /
  procedure concern) — this node catalogues the mechanism as it exists, it
  does not walk a reader through building on it.
- Whether Postgres RLS *should* be added, or a design for adding it. That is a
  decision for whoever next works the multi-tenant-relay lane
  `docs/multi-tenant-relay.md` and `docs/multi-tenant-conformance.md` describe,
  not a call this reference document makes.
- The `docs/multi-tenant-relay.md` formal proof's correctness, its TLA+/Tamarin
  models, or the isolation/authorization-soundness theorems themselves — only
  that document's own stated status (draft, RLS as axiom, stubbed conformance
  tests) is recorded here as fact.

## Relationships

- part-of: `architecture-containers-postgres` — this node zooms into the
  security/tenancy boundary that node names but defers.

## Scope and omissions

**This node covers** the enforcement points that make cross-community data
isolation hold in Postgres today (host binding, the `community_id`
discriminator column and its key/index shape, query-level filtering in
`buzz-db`, claimed-versus-resolved tracing, and lifecycle/retention gating via
community deletion state), and states explicitly that Postgres row-level
security is not implemented — it exists only as a named future migration gate
and as a trusted axiom in a draft formal specification whose own conformance
tests are stubbed and skipped.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres's full container-level responsibility, technology, and connection topology | `architecture-containers-postgres` (`launchpad/docs/corpus/architecture/containers/postgres.md`) |
| A full datastore schema/namespace/migration profile for Postgres | A future `datastore.md`-shaped `layers/data/postgres/*` node, not yet written |
| The multi-tenant-relay formal proof's own correctness (TLA+, Tamarin, the isolation/authorization theorems) | `docs/multi-tenant-relay.md`, `docs/spec/MultiTenantRelay.tla`, `docs/spec/MultiTenantAuth.spthy` |
| The full multi-tenant conformance obligation table (search, media, git, workflows, audit, and more, beyond the isolation mechanism itself) | `docs/multi-tenant-conformance.md` |
| Whether RLS should be added, and any design for doing so | Unresolved; a decision for whoever next works the multi-tenant-relay lane |

**Expected but not verified when this node was written:**

- Whether `crates/buzz-relay/src/conformance/mod.rs`'s tracer is wired into the
  relay's *current* single-community request path in production, or is
  exercised only by the not-yet-landed multi-tenant integration branch —
  recorded above as an `INFERENCE` at `confidence: 0.55`, not asserted as
  settled fact.
- Whether every data-access module in `buzz-db` (beyond `event.rs`, which was
  read directly) follows the identical explicit-`community_id`-parameter
  pattern, or whether any module has a gap — this node's query-level-filtering
  claim is checked against `event.rs` specifically, not against every module
  in the crate.
- Whether any deployment-level Postgres configuration outside this
  repository (a managed database's own role/grant setup) happens to restrict
  cross-tenant access by means this repository's code does not itself
  configure or verify — out of reach of a repository-scoped review.
