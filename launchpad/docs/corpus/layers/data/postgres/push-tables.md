---
id: layers-data-postgres-push-tables
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
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) with no `data` member; this document takes `type: layers` because it lives under `launchpad/docs/corpus/layers/`, the same choice open PR #1874's layers/data/object-storage siblings and open PR #1875's layers/data/postgres siblings (audit-tables, backup-boundary, channel-members-table, channels-table, communities-table) already made over `templates/data-entity.md`'s own `type: implementation` suggestion for a real instance, each disclosing the same tension in its own evidence ledger."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "PR #1875 (open, launchpad-26/buzz#1875) states in its own audit-tables.md evidence ledger that a node under `layers/` takes `type: layers` as the batch's established precedent over the datastore/data-entity templates' own type suggestions, and that this precedent traces to open PR #1874's layers/data/object-storage siblings."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1875 (open PR, docs(corpus): postgres layer batch 4), read directly via gh pr diff"
  - statement: "Issue #1086 assigns this document the path launchpad/docs/corpus/layers/data/postgres/push-tables.md directly via its own corpus-plan:v2 alias header comment and Objective sentence, describing the subject as 'the single canonical data entity node for push tables,' and its Definition of Done requires defining identity/key and semantic ownership, summarizing fields by meaning without duplicating generated schema detail, defining relationships/lifecycle/invariants, and linking authoritative migration/schema and read/write code paths -- wording that maps onto templates/data-entity.md's required sections (Identity, Attributes and shape, Invariants, Relationships, Provenance, Storage pointer) rather than templates/datastore.md's storage-mechanics sections, checked by reading the issue body directly."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1086 definition of done, read directly via gh issue view"
  - statement: "architecture-containers-postgres is a merged, validated node on origin/launchpad (confirmed via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus) documenting the relay's own Postgres container; architecture-flows-push-notification and architecture-containers-push-gateway are likewise merged nodes on origin/launchpad, the former describing the end-to-end NIP-PL push flow and the latter describing buzz-push-gateway as a standalone service with its own database."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
      - "launchpad/docs/corpus/architecture/containers/push-gateway.md"
  - statement: "migrations/0012_push_leases.sql creates push_leases with columns community_id (UUID NOT NULL REFERENCES communities(id)), author (BYTEA, 32-byte pubkey), installation_id (TEXT, 1-64 octets), source_event_id (BYTEA, 32 bytes), source_created_at (BIGINT), generation (BIGINT > 0), active (BOOLEAN), app_profile/endpoint_hash/endpoint_grant/max_class/subscriptions (all nullable, populated only when active), and expires_at (BIGINT); PRIMARY KEY (community_id, author, installation_id), UNIQUE (community_id, source_event_id), a partial unique index push_leases_endpoint_unique on (community_id, author, app_profile, endpoint_hash) WHERE active, and a CHECK constraint requiring the five active-only columns to be all-present when active is true and all-NULL when active is false. The same migration creates push_wake_outbox with a foreign key to push_leases on (community_id, author, installation_id), a state column constrained to ('pending','sending','delivered','failed'), and a UNIQUE (community_id, endpoint_hash, event_id) dedup key."
    entry_class: FACT
    evidence:
      - "migrations/0012_push_leases.sql"
  - statement: "migrations/0013_push_endpoint_state.sql adds push_leases.endpoint_enabled (BOOLEAN NOT NULL DEFAULT true), with a comment stating 'transport invalidation is generation-scoped and does not rewrite the signed lease's active/tombstone state; a higher-generation replacement re-enables it.'"
    entry_class: FACT
    evidence:
      - "migrations/0013_push_endpoint_state.sql"
  - statement: "migrations/0018_push_match_queue.sql creates push_match_queue (community_id, event_id, state constrained to ('pending','matching'), attempts, next_attempt_at, lease_until, claim_id, created_at; PRIMARY KEY (community_id, event_id)) and an enqueue_push_match_job() AFTER INSERT trigger function on events that inserts a push_match_queue row, ON CONFLICT DO NOTHING, whenever the inserted event's kind is in (7, 9, 1059, 40007, 46010); its own comment states 'the trigger runs in the event insert transaction, so every accepted persistent event has a crash-safe match job.'"
    entry_class: FACT
    evidence:
      - "migrations/0018_push_match_queue.sql"
  - statement: "migrations/0023_push_match_gate.sql replaces enqueue_push_match_job() (same trigger, same table) so the push_match_queue insert only happens when an active, endpoint_enabled, unexpired push_leases row exists for that community, gated by a per-community pg_advisory_xact_lock_shared keyed 'buzz_push_gate:{community_id}'; its own header comment names this the 'T1b push gate' and states its purpose is to skip matcher cost entirely in the common case of a community with no active lease, and explains a lost-wake race is closed by making lease-activating transitions take the same lock key EXCLUSIVE in crates/buzz-db/src/store/push.rs (acquire_push_gate_lock)."
    entry_class: FACT
    evidence:
      - "migrations/0023_push_match_gate.sql"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_PUSH_LEASE = 30350 (the addressable kind:30350 lease envelope) and, among the push-match trigger's allow-listed kinds, KIND_REACTION = 7, KIND_STREAM_MESSAGE = 9, KIND_GIFT_WRAP = 1059, KIND_STREAM_REMINDER = 40007 and KIND_WORKFLOW_APPROVAL_REQUESTED = 46010; crates/buzz-relay/src/handlers/push_lease.rs independently defines the identical PUSH_KINDS = [7, 9, 1059, 40007, 46010] constant used for envelope validation."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
  - statement: "crates/buzz-db/src/store/push.rs's module doc states it implements 'community-scoped NIP-PL lease and durable wake-outbox persistence' and that 'every operation requires a server-resolved CommunityId; client-provided origins never select rows in this module.' Its accept_lease_event and replace_lease functions atomically upsert push_leases keyed on (community_id, author, installation_id), enforcing NIP-01 addressable-event ordering (higher source_created_at wins, ties broken by lower source_event_id) and strictly increasing generation before accepting a replacement, returning distinct outcomes (StaleEvent, StaleGeneration, EndpointAlreadyLeased, LeaseQuotaExceeded, SourceEventCollision, ConstraintViolation) rather than a bare boolean. accept_lease_event also inserts the signed kind:30350 event into the events table and soft-deletes the author's prior kind:30350 event for that installation_id in the same transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs"
  - statement: "crates/buzz-db/src/store/push.rs's enqueue_wakes function atomically inserts into push_wake_outbox, copying endpoint_hash and endpoint_grant from the current push_leases row rather than trusting caller-supplied values, with the comment 'callers cannot redirect a wake by supplying either value'; claim_due_wakes and revalidate_wake_for_send join push_wake_outbox to push_leases (and to events, checking deleted_at IS NULL) on every claim and again immediately before send, with revalidate_wake_for_send's own comment calling that final join 'the load-bearing RF1 gate' that neither claim-time eligibility nor replacement-time cancellation can replace."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs"
  - statement: "crates/buzz-db/src/store/push.rs's claim_due_match_batch_with_loader claims due push_match_queue rows for exactly one community per call (SELECT ... FOR UPDATE SKIP LOCKED, community-scoped via a target CTE), and complete_match_batch/retry_match_batch/reap_exhausted_matches operate on push_match_queue keyed by claim_id and community_id; reap_exhausted_matches and claim_due_match_batch_with_loader's queries both gate on community_write_allowed(community_id)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs"
  - statement: "crates/buzz-relay/src/push_runtime.rs's module doc states it is the 'durable NIP-PL event matcher and gateway delivery worker'; run_matcher's own doc comment states it 'continuously claims accepted events in per-community batches and matches them against active leases,' periodically calling state.db.reap_exhausted_push_matches() on a fixed REAP_INTERVAL (30s) off the claim path; a second function (run_delivery_worker, referenced by push_runtime.rs's own symbol list) claims due push_wake_outbox rows and sends them to buzz-push-gateway's delivery endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "crates/buzz-db/src/store/deletion.rs's EXPECTED_SCOPED_TABLES constant (the exact catalog of community-scoped tables a whole-community deletion purges) lists push_leases, push_match_queue and push_wake_outbox alongside events, channels, users and the rest; its PURGE_SCOPED_TABLES constant (the FK-safe child-before-parent purge order) orders push_wake_outbox before push_match_queue and push_leases, consistent with push_wake_outbox's foreign key onto push_leases."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql creates push_gateway_challenges, push_gateway_installations, push_gateway_delegations, push_gateway_endpoint_quotas, push_gateway_delivery_auth_replays and push_gateway_delivery_request_replays; the main relay's own migrations/0015_push_gateway_authority.sql creates byte-identical table definitions and additionally records all six as `_operator_global_tables` (deployment-global, outside community tenancy); crates/buzz-push-gateway/src/postgres.rs is buzz-push-gateway's own separate Postgres connection module, and crates/buzz-db/src/runtime/migration.rs's own destructive-lock test explicitly names crates/buzz-push-gateway/src/postgres.rs and crates/buzz-push-gateway/migrations as an exception to its single-migration-runner assertion, confirming buzz-push-gateway runs its own independent migration set rather than sharing buzz-db's."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
      - "migrations/0015_push_gateway_authority.sql"
      - "crates/buzz-push-gateway/src/postgres.rs"
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Whether the main relay's own copy of the push_gateway_* tables (migrations/0015, marked _operator_global_tables) is a live, load-bearing second store the relay itself queries, or historical drift left over from an earlier co-located architecture that buzz-push-gateway's later split did not clean up, was not established: no call site in crates/buzz-relay/src querying push_gateway_challenges, push_gateway_installations, push_gateway_delegations, push_gateway_endpoint_quotas, push_gateway_delivery_auth_replays or push_gateway_delivery_request_replays was found by inspection of crates/buzz-relay/src's push-related modules (config.rs, push_runtime.rs, nip11.rs, main.rs, handlers/push_lease.rs), which reference push_gateway_ only as configuration (the gateway's URL/keys), not as SQL table names."
    entry_class: INFERENCE
    evidence:
      - "migrations/0015_push_gateway_authority.sql"
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/push_runtime.rs"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
    confidence: 0.6
  - statement: "crates/buzz-db/src/store/push.rs's own #[cfg(test)] module contains 16 #[tokio::test] cases, each #[ignore = \"requires Postgres\"], directly exercising the invariants named above by name: acceptance_constraint_failure_rolls_back_source_event, source_event_collision_is_protocol_outcome_without_event_insert and replacement_and_revoke_are_community_scoped_and_dual_ordered (addressable-event ordering and generation monotonicity), concurrent_enqueue_is_atomic_and_community_scoped and setwise_enqueue_maps_outcomes_per_request (endpoint/event dedup), send_revalidation_suppresses_rotated_claim_and_retry_preserves_id (the send-time revalidation gate), endpoint_invalidation_is_scoped_to_community_and_generation (endpoint_enabled scoping), matcher_trigger_is_allowlisted_and_deleted_events_are_discarded, matcher_claim_is_exclusive_across_workers and batch_claim_is_single_community_and_setwise_ops_honor_the_fence (write fencing and per-community claim isolation), exhausted_match_job_is_reaped_and_cannot_pin_retention and exhausted_match_reaper_skips_quiescing_tenant_and_reaps_active_bystanders (poison-job termination), and gate_orders_lease_activation_after_in_flight_event_and_backfills_it (the T1b lost-wake race closure)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-flows-push-notification
  - type: references
    target: architecture-containers-push-gateway
---

# `layers/data/postgres`: push tables

The three community-scoped Postgres tables (`push_leases`, `push_wake_outbox`,
`push_match_queue`) that together hold the durable, server-side state of Buzz's
NIP-PL push-notification pipeline in the relay's own database — the effective lease
a client's push registration produces, the durable wake jobs matched events queue for
delivery, and the crash-safe matcher work queue that produces those wakes.

**A note on this node's `type`.** `node.schema.json`'s `type` enum has no `data`
member. This document takes `type: layers` because it lives under
`launchpad/docs/corpus/layers/`, matching the precedent already established by open PR
#1874 (`layers/data/object-storage/*`) and open PR #1875 (`layers/data/postgres/*`,
this task's own sibling batch), both of which override `templates/data-entity.md`'s own
`type: implementation` suggestion for a real instance the same way. See the evidence
ledger entry above for the exact citations.

## Identity

All three tables are **community-scoped**, never globally unique, and each has a
distinct composite identity:

- **`push_leases`**: `PRIMARY KEY (community_id, author, installation_id)`. One row per
  (community, pubkey, installation) — the *effective, mutable* state for that
  installation's push registration, replaced in place as newer signed events arrive.
  Separately, `UNIQUE (community_id, source_event_id)` pins exactly one lease row to
  the specific signed kind:30350 event that most recently won addressable-event
  ordering for it.
- **`push_wake_outbox`**: `PRIMARY KEY (community_id, id)` where `id` is a
  server-generated `UUID`, plus `UNIQUE (community_id, endpoint_hash, event_id)` as the
  idempotency key that makes re-matching the same (endpoint, event) pair a no-op. `id`
  doubles as the stable request id the gateway delivery call carries.
- **`push_match_queue`**: `PRIMARY KEY (community_id, event_id)`. One row per event
  the push-eligible-kind trigger decided needs matching; the primary key is also the
  dedup key the trigger's `ON CONFLICT DO NOTHING` relies on.

## Attributes and shape

**`push_leases`** — the effective lease. `active` and its five active-only columns
(`app_profile`, `endpoint_hash`, `endpoint_grant`, `max_class`, `subscriptions`) are
governed by a single CHECK constraint: all five are non-NULL when `active` is true and
all five are NULL when `active` is false — there is no partially-populated state.
`endpoint_hash` is a SHA-256 of the platform push token (never the raw token itself);
`endpoint_grant` is an opaque capability issued by the stateless gateway, not a secret
the relay interprets; `max_class` is one of `silent`/`default`/`time_sensitive`/
`urgent`; `subscriptions` is validated `JSONB` used for matcher filtering.
`endpoint_enabled` (migration 0013) is a second, transport-level flag distinct from
`active`: a delivery failure can disable the endpoint without rewriting the
signed-event-derived `active`/tombstone state, and a higher-generation replacement
re-enables it. `generation` is a strictly increasing installation-supplied counter
that, together with `source_created_at`/`source_event_id`, is the ordering state a
replacement must beat to be accepted.

**`push_wake_outbox`** — one durable delivery job. `lease_generation` and
`endpoint_hash` are copied from the lease at enqueue time, not re-read from the caller,
so a caller cannot redirect a wake to a different endpoint. `state` is one of
`pending`/`sending`/`delivered`/`failed`; `attempts`/`next_attempt_at`/`lease_until`/
`claim_id` are the same claim-lease-retry shape `push_match_queue` uses.

**`push_match_queue`** — one durable matcher job, keyed only by `(community_id,
event_id)`; it carries no payload beyond `state`/`attempts`/`next_attempt_at`/
`lease_until`/`claim_id` because the event it names is looked up from `events` at
claim time, not duplicated into the queue row.

Field-by-field SQL types are not restated here beyond what a claim above needs; the
authoritative shape is the `CREATE TABLE` statements in migrations 0012, 0013 and 0018
(cited above), not this prose.

## Invariants

- **Active/tombstone completeness** (`push_leases`): the five active-only columns are
  all-present or all-NULL together — enforced by a database CHECK constraint, not
  merely application discipline.
- **Addressable-event ordering and generation monotonicity**: a lease replacement is
  accepted only if it wins NIP-01 addressable-event ordering against the currently
  stored `(source_created_at, source_event_id)` *and* its `generation` strictly exceeds
  the stored one; `crates/buzz-db/src/store/push.rs`'s `accept_lease_event`/`replace_lease`
  enforce both gates atomically inside one transaction, returning `StaleEvent` or
  `StaleGeneration` rather than silently ignoring a losing write.
- **Endpoint/event dedup**: `push_wake_outbox`'s `UNIQUE (community_id, endpoint_hash,
  event_id)` makes re-enqueuing the same (endpoint, event) pair idempotent —
  `enqueue_wakes` treats a conflict as `Duplicate`, not an error.
- **Send-time revalidation is load-bearing, not an optimization**: `revalidate_wake_for_send`
  re-joins `push_wake_outbox` to the *current* `push_leases` row (active, endpoint-enabled,
  unexpired) and to a non-deleted `events` row immediately before every gateway send;
  claim-time eligibility and replacement-time cancellation are explicitly documented as
  optimizations that cannot replace this check.
- **Lost-wake race closure (T1b push gate)**: migration 0023's trigger and
  `push.rs`'s `acquire_push_gate_lock` share one per-community advisory lock namespace
  (`buzz_push_gate:{community_id}`) — event inserts take it `SHARED`, lease
  activations that can flip a community from ineligible to eligible take it
  `EXCLUSIVE` — forcing a total order so a concurrent event insert either observes the
  committed lease or is strictly ordered before the activation, closing the gap where
  an event is silently skipped because a lease was still being written when it landed.
- **Poison-job termination**: `push_match_queue` and `push_wake_outbox` claims are
  bounded (`MAX_MATCH_ATTEMPTS` for the match queue); `reap_exhausted_matches` deletes
  jobs that exhausted their attempts so a malformed or permanently-failing job cannot
  pin the table forever.
- **Write fencing**: every claim/enqueue/reap query in `push.rs` gates on
  `community_write_allowed(community_id)` (migration 0029), so a community mid-deletion
  cannot accept new push writes even between the moment its lifecycle changes and the
  moment its rows are physically purged.

**Verification.** All ten invariants above are directly exercised, by name, in
`crates/buzz-db/src/store/push.rs`'s own `#[cfg(test)]` module — 16 `#[tokio::test]` cases,
each `#[ignore = "requires Postgres"]` (see the evidence ledger entry above for the
per-invariant test-name mapping). No integration/E2E test exercising these tables
through the live WebSocket protocol was located while drafting this node; that gap is
not resolved here.

## Relationships and lifecycle

**In code:** `push_wake_outbox.(community_id, author, installation_id)` is a real
foreign key onto `push_leases`; `push_match_queue` and `push_wake_outbox` both carry
`event_id` references resolved against `events` at read time (not enforced as SQL
foreign keys, since `events` is partitioned — see `architecture-containers-postgres`
for that constraint). The `enqueue_push_match_job` trigger (migrations 0018, 0023) is
the sole producer of `push_match_queue` rows, firing inside the same transaction as
`events` insertion for every kind in the push-eligible allow-list (`7, 9, 1059, 40007,
46010`, `crates/buzz-core/src/kind.rs`). `push_runtime.rs`'s matcher is the sole
producer of `push_wake_outbox` rows, and its delivery worker is the sole consumer that
calls out to `buzz-push-gateway`.

**Community-deletion lifecycle:** `crates/buzz-db/src/store/deletion.rs`'s
`EXPECTED_SCOPED_TABLES` lists all three tables as community-scoped and subject to
whole-community purge; `PURGE_SCOPED_TABLES` orders `push_wake_outbox` before
`push_match_queue` and `push_leases`, consistent with `push_wake_outbox`'s foreign key
onto `push_leases`.

**Corpus relationships** (front matter, above): `references` →
`architecture-containers-postgres` (the container these tables physically live in),
`references` → `architecture-flows-push-notification` (the end-to-end flow that
produces and consumes rows in all three tables), and `references` →
`architecture-containers-push-gateway` (the boundary — see *Scope and omissions*
below).

## Provenance

None of the three tables has a Nostr event kind of its own as source of truth in the
usual sense; instead:

- `push_leases` is a **server-derived projection of a client-signed event**: its
  effective row is derived from, and kept in generation/ordering sync with, the
  author's most recent accepted kind:30350 (`KIND_PUSH_LEASE = 30350`) event, which is
  itself stored in `events` and soft-deleted on replacement in the same transaction
  that updates the projection.
- `push_wake_outbox` and `push_match_queue` are **purely server-derived** — durable
  work-queue rows with no event of their own, produced entirely by relay-side logic
  (a trigger and a matcher loop) in response to other events landing in `events`.

## Storage pointer

Postgres — the relay's primary database, the same instance `architecture-containers-postgres`
documents. Table names: `push_leases`, `push_wake_outbox`, `push_match_queue`, defined
by `migrations/0012_push_leases.sql`, `migrations/0013_push_endpoint_state.sql` and
`migrations/0018_push_match_queue.sql`, mutated by `migrations/0014_push_lease_fts.sql`
(unrelated column exclusion on `events.search_tsv` for kind:30350, not a `push_*` table
change) and `migrations/0023_push_match_gate.sql`. No dedicated datastore-level node
exists yet for the relay's Postgres schema mechanics; `architecture-containers-postgres`
is the nearest merged node and is the `references` target above.

## Scope and omissions

**This document covers** the three community-scoped push tables in the relay's own
Postgres database — their identity, field meaning, invariants, code-level
relationships, community-deletion lifecycle, provenance, and the migrations/code paths
that read and write them.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `push_gateway_*` authority/session tables (`push_gateway_challenges`, `push_gateway_installations`, `push_gateway_delegations`, `push_gateway_endpoint_quotas`, `push_gateway_delivery_auth_replays`, `push_gateway_delivery_request_replays`) — a different concept: `buzz-push-gateway`'s own deployment-global authority state, migrated independently by that service | `architecture-containers-push-gateway` (merged); a future `layers/data/postgres` or gateway-scoped data-entity task, not this one |
| The end-to-end NIP-PL flow (client lease publication through APNs delivery) | `architecture-flows-push-notification` (merged) |
| Postgres's own schema/namespace mechanics, migration ordering machinery, and connection pooling as a datastore-level concern | `architecture-containers-postgres` (merged, container-level only); no datastore-level node exists yet |
| The wire contract of kind:30350 itself (tag semantics, NIP-44 plaintext shape) | a future `interfaces-events` node for kind:30350, not created by this document |

**Expected but not verified when this node was written:**

- **Whether the main relay's own `push_gateway_*` table copy (migration 0015) is a live
  second store the relay code actually queries, or unused drift left over from an
  earlier co-located architecture that `buzz-push-gateway`'s later split into its own
  service and database did not clean up.** No SQL call site against any
  `push_gateway_*` table name was found in `crates/buzz-relay/src`'s push-related
  modules by inspection; the relay's references to `push_gateway_` there are
  configuration (URL, keys), not table access. This is named as a real, checked gap
  (see the `INFERENCE` evidence entry above), not resolved either way, and is
  explicitly out of scope for this document regardless of the answer — the two copies
  are the same *concept* (gateway authority state) whichever database instance is
  actually live, and that concept belongs to `architecture-containers-push-gateway` or
  a future dedicated node, not here.
- **Whether a dedicated `layers/data/postgres/*` or datastore-level node for the
  relay's Postgres schema mechanics (migration ordering, connection pooling,
  partitioning generally) exists or is planned** was not established beyond the
  merged, container-level `architecture-containers-postgres` node this document already
  cites.
