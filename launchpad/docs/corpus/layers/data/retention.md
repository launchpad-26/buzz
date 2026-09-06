---
id: layers-data-retention
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
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion), and layers is a real member of it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real instance node (type: architecture, an INFERENCE at confidence 0.6 in that template's own ledger), for consistency with the sibling layers/data/** documents already authored in this same batch under the identical override (#1072's object-storage/retention.md, #1062's data-lifecycle.md), both of which independently disclose the same tension per standards/taxonomy.md's rule to disclose an imperfect fit rather than silently pick."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.65
  - statement: "Issue #1100 assigns this document the path launchpad/docs/corpus/layers/data/retention.md directly, via its own corpus-plan:v2 alias header comment and its Objective sentence, and its Definition of Done requires a one-sentence definition, a boundaries/non-goals statement, links to related concepts/implementation/verification, and examples used only to clarify rather than to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1100, read directly via gh issue view"
  - statement: "templates/datastore.md's own Purpose section scopes that template to documenting the internal shape of one running datastore instance a container inventory already lists as one row -- not a synthesis spanning multiple datastores -- while templates/reference.md imposes no such single-subject constraint, so reference.md is the better-fitting template for a cross-cutting retention document spanning Postgres, Redis, and object storage."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/templates/reference.md"
  - statement: "architecture-containers-postgres, architecture-containers-redis, and architecture-containers-object-storage are merged nodes on origin/launchpad at the recorded revision, each documenting one of the three datastores this node's structured-entries table covers."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "launchpad/docs/corpus/architecture/containers/redis.md"
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "insert_event's soft-delete functions (soft_delete_event, soft_delete_by_coordinate, soft_delete_event_and_update_thread) all set deleted_at = NOW() rather than issuing a DELETE, every ordinary read path filters on deleted_at IS NULL, and a dedicated function, get_event_by_id_including_deleted, exists specifically for callers -- its own doc comment names audit trails and compliance queries -- that must distinguish 'never existed' from 'was deleted'; nothing in this code path removes the row."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs"
  - statement: "Exactly two coordinate shapes are hard-purged (a real DELETE, not a tombstone) the instant they are superseded or soft-deleted: kind:30078 NIP-RS read-state markers matching a 'read-state:<32-hex>' d-tag (migrations/0007_nip_rs_retention.sql, whose own header states its purpose is to 'Bound NIP-RS storage while preserving NIP-33 replay ordering' by retaining 'the only historical fact replacement needs without retaining user payloads'), and kind:30003 buzz-mesh-member-status heartbeats (migrations/0019_mesh_status_retention.sql, whose own header states 'Only the live head has product value; retaining every superseded 45-second payload creates unbounded physical history')."
    entry_class: FACT
    evidence:
      - "migrations/0007_nip_rs_retention.sql"
      - "migrations/0019_mesh_status_retention.sql"
  - statement: "An ephemeral channel (ttl_seconds set) carries a ttl_deadline refreshed forward on every new durable event via a deferred, per-channel-locked trigger (migrations/0022_event_ttl_refresh.sql, migrations/0024_event_ttl_refresh_shared_lock.sql); crates/buzz-db/src/store/channel.rs's reaper archives (sets archived_at) a channel whose deadline has passed -- it does not delete the channel or the events inside it, and a permanent channel (ttl_seconds NULL) is never touched by this mechanism."
    entry_class: FACT
    evidence:
      - "migrations/0022_event_ttl_refresh.sql"
      - "migrations/0024_event_ttl_refresh_shared_lock.sql"
      - "crates/buzz-db/src/store/channel.rs"
  - statement: "buzz-audit's own module doc comment describes AuditService as backing an 'append-only, per-community hash-chain audit log'; the per-event soft-delete path never touches audit_log, and audit_log is one of the tables named in buzz-db/src/deletion.rs's PURGE_SCOPED_TABLES constant, meaning it is physically purged only as part of a whole-community deletion, never by any individual event's own lifecycle."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "crates/buzz-pubsub/src/presence.rs's own module doc comment states presence is stored as 'SET buzz:{community}:presence:{pubkey_hex} \"online\" EX 180', a 3x-heartbeat TTL so a single missed heartbeat does not flap status; set_presence issues that SET ... EX call, and clear_presence deletes the key immediately on a clean disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "crates/buzz-pubsub/src/rate_limiter.rs implements a fixed-window rate limiter as an atomic Lua script that INCRs a Redis key and conditionally EXPIREs it on first call, with an explicit repair path that re-issues EXPIRE if a prior crash left the key without one -- every rate-limit key this module writes carries a bounded lifetime, never an unbounded one."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
  - statement: "crates/buzz-pubsub/src/cache_invalidation.rs's own module doc comment states its purpose is to carry membership/visibility cache-key drops to every relay pod immediately, because 'other pods would otherwise rely on the 10s TTL to expire stale entries' -- naming a 10-second TTL as the fallback bound on how long any pod's local cache can serve stale membership state even if the invalidation message is lost."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
  - statement: "crates/buzz-auth/src/nip98_replay.rs documents its own Redis-backed replay guard as requiring 'TTL >= 120s' to cover NIP-98's +/-60s timestamp tolerance, and defines DEFAULT_REPLAY_TTL_SECS = 120 as that floor -- another Redis key class that is bounded-lifetime by construction, not indefinitely retained."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98_replay.rs"
  - statement: "Every Redis-backed mechanism inspected in crates/buzz-pubsub and crates/buzz-auth (presence, rate limiting, cache invalidation, NIP-98 replay guard) writes keys with an explicit TTL or EXPIRE. This is not universal, though: crates/buzz-relay/src/tunnel/directory.rs's mesh session directory INCRs a companion key its own doc comment calls the 'non-expiring generation key', with no TTL applied at all, alongside a separate, PX-TTL-bound lease key. buzz-pubsub's own module doc comment describes Redis's role as pub/sub fan-out, presence, and typing indicators layered on top of PostgreSQL as the durable store, but that description does not extend to the tunnel-mesh directory, a different crate. This was checked against every TTL/EXPIRE call site found in crates/buzz-pubsub and crates/buzz-auth, plus the one non-expiring key surfaced while investigating this claim in crates/buzz-relay/src/tunnel/directory.rs -- not against every Redis key ever written in the repository, so it is reported as a reasoned pattern with one known, disclosed exception rather than an exhaustive inventory."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-pubsub/src/cache_invalidation.rs"
      - "crates/buzz-auth/src/nip98_replay.rs"
      - "crates/buzz-relay/src/tunnel/directory.rs"
    confidence: 0.7
  - statement: "crates/buzz-media/src/bucket_index.rs's tenant_prefixes function has a doc comment stating verbatim that shared immutable CAS/thumb/probe data is 'deliberately outside' the three tenant-owned prefixes it returns, because 'fleet-wide physical GC is a separate retention phase' -- and no TTL, expiry, or scheduled-deletion mechanism for object-storage keys was found anywhere in crates/buzz-media at this revision (grepped for ttl/expire/TTL across every non-test source file in that crate)."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/bucket_index.rs"
  - statement: "crates/buzz-db/src/store/deletion.rs's DeletionStage enum documents a fixed, ordered, no-skip whole-community deletion lifecycle ending at PostgresPurged (a physical DELETE across every table in PURGE_SCOPED_TABLES, including events and audit_log) then CachePurged; crates/buzz-deletion/src/lib.rs's purge_redis_namespace function implements that Redis step as a SCAN/UNLINK loop over the buzz:{community}:* key pattern -- a real, whole-namespace purge, not a reliance on individual keys' own TTLs to eventually clear community-scoped Redis state."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
      - "crates/buzz-deletion/src/lib.rs"
  - statement: "Whole-community deletion's object-storage step removes only the tenant-owned key bindings is_tenant_owned_key recognizes (media sidecars, upload records, git repository pointers); shared content-addressed blob, thumbnail, and git-CAS bytes are never targeted by any deletion code path in this repository, per #1072's own independently-cited evidence for that same function -- restated here only as a one-line summary, not re-derived, since #1072 (layers/data/object-storage/retention.md) owns the full bucket-level retention detail and is not yet merged to origin/launchpad."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1072 (unmerged, PR #1874, layers/data/object-storage/retention.md), and independently confirmed in this node's own evidence above (crates/buzz-media/src/bucket_index.rs)"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-containers-object-storage
---

# Data retention

## Reference description

**Retention** is how long a piece of Buzz's stored data survives, by default,
and what actually removes it once it stops surviving. This node catalogues
that answer once per datastore — Postgres, Redis, and the shared
S3-compatible object store — as the umbrella, cross-cutting view a reader
checking "how long is X kept, and why" needs before drilling into any one
datastore's own document. It links out rather than restates: the
container-level existence of each datastore is
[`architecture-containers-postgres`](../../architecture/containers/postgres.md),
[`architecture-containers-redis`](../../architecture/containers/redis.md), and
[`architecture-containers-object-storage`](../../architecture/containers/object-storage.md);
the deeper retention mechanics of the object-storage bucket specifically, and
the full per-event/channel/community lifecycle phase structure, are each
owned by their own sibling documents (see *Boundary*, below).

## Retention by datastore

Prose is included where needed to make each row legible, per Diátaxis's own
reference-form nuance that description of *how something works* is
permitted alongside structured entries — step-by-step task instruction is
not, and none is given here.

| Datastore | Default retention | What actually removes data |
|---|---|---|
| **Postgres — events** | Indefinite. A NIP-09 (`kind:5`) or NIP-29 (`kind:9005`) deletion request soft-deletes an event by setting `deleted_at`, not by removing the row. Every ordinary read filters `deleted_at IS NULL`, so a deleted event disappears from normal queries while its row — and a dedicated escape hatch, `get_event_by_id_including_deleted`, for audit and compliance callers — still exists. | Nothing, by default. A whole-community deletion request's `PostgresPurged` stage is the terminal mechanism that physically removes tombstoned rows. |
| **Postgres — two named high-churn kinds** | None. `kind:30078` NIP-RS read-state markers and `kind:30003` mesh-status heartbeats are the sole exception to the tombstone default: a database trigger issues a real `DELETE` the instant either is superseded or soft-deleted. Migration 0007's own header states its purpose is to bound NIP-RS storage while preserving replay ordering, retaining only a compact watermark rather than every superseded payload; migration 0019's header states — in its own words — that "only the live head has product value" for a mesh-status heartbeat. | The trigger itself, on every write, for these two kinds only. This is a hardcoded exception list, not a general TTL policy any new high-churn kind gets automatically. |
| **Postgres — ephemeral channels** | Indefinite — the same as a permanent channel. Nothing about `ttl_seconds` removes data; the deadline it sets (refreshed forward on every new durable event) bounds only how long the channel stays *active*, not how long its data survives. | A background reaper archives (`archived_at`) an ephemeral channel once its deadline passes. Archiving is not deletion — the channel container and the events inside it are untouched by this mechanism; only the container stops being active. |
| **Postgres — audit log** | Indefinite, and structurally so: the audit log is an append-only, per-community hash chain. No per-event soft-delete or hard-purge path ever touches it. | Only a whole-community deletion's `PostgresPurged` stage, which lists `audit_log` among the tables it physically purges. |
| **Redis** | Bounded by construction for the mechanisms inspected in `buzz-pubsub`/`buzz-auth` — presence keys carry a 180-second TTL (three times the heartbeat interval); rate-limit keys are `INCR`'d with a conditionally-applied `EXPIRE`, repaired if a crash left one missing; cross-pod cache-invalidation messages exist only as a fallback to a 10-second local-cache TTL; NIP-98 replay-guard keys carry a 120-second floor. One disclosed exception: the mesh tunnel session directory's generation key (`buzz:{community}:tunnel:{session}:generation`, `crates/buzz-relay/src/tunnel/directory.rs`) is `INCR`'d with no TTL applied — its own doc comment calls it "non-expiring" by design. | The key's own TTL, where one is set. A whole-community deletion's `CachePurged` stage additionally `SCAN`s and `UNLINK`s the entire `buzz:{community}:*` namespace, so a community's Redis footprint is not left to expire key-by-key on deletion — this also reaches the non-expiring generation key, since it is community-scoped and sits inside that same namespace. |
| **Object storage — tenant-owned bindings** | Indefinite; no per-object TTL or scheduled expiry exists anywhere in `crates/buzz-media` at this revision. | Only an explicit whole-community deletion, which removes the tenant-owned key bindings (media sidecars, upload records, git repository pointers) it recognizes. |
| **Object storage — shared content-addressed bytes** | Indefinite, and not merely by omission: `tenant_prefixes`' own doc comment states shared blob/thumbnail/git-CAS data is "deliberately outside" every tenant-owned prefix, naming "fleet-wide physical GC" as "a separate retention phase" that this codebase does not implement. | Nothing in this repository. No deletion code path — including whole-community deletion — ever targets these bytes. |

**The one recurring shape across all three datastores.** Nothing here is
deleted opportunistically or on a background sweep tied to *age* alone.
Postgres tombstones and Redis TTLs (with one disclosed exception — the mesh
tunnel session directory's non-expiring generation key, see the table above)
each bound what a normal read or a normal key lookup can see, but the
underlying bytes persist — sometimes literally
(a tombstoned row, an un-swept object), sometimes not (an expired Redis key
is gone) — until either a narrow, explicitly named mechanism fires (the two
hard-purge kinds, a Redis key's own expiry) or an operator-triggered
whole-community deletion request runs to completion. There is no general,
configurable "retain for N days" policy anywhere in this codebase; every
bound above is either indefinite, hardcoded to a specific kind or key class,
or driven by an explicit deletion request.

## Boundary

This node does not describe:
- **The object-storage bucket's own full retention mechanics** — the
  bucket-level key-shape table, the deletion pipeline's audit trail, and the
  versioning-detection safety gate before any destructive delete — which
  belongs to `layers/data/object-storage/retention.md` (issue #1072). That
  document is not yet merged to `origin/launchpad` at this node's authoring
  revision, so no `relationships` edge to it exists here; it is named in
  prose only, per this task's own instructions.
- **The full per-event/channel/community lifecycle phase structure** —
  ingestion, live, deletion request, tombstone retention, the narrow
  hard-purge exception, channel TTL, and whole-community purge, read together
  as one connected sequence with its own use cases — which belongs to
  `layers/data/data-lifecycle.md` (issue #1062), for the same unmerged-branch
  reason as above.
- **Why data is retained or deleted** in a compliance, product, or policy
  sense (GDPR-style user rights, contractual data-handling commitments) —
  this node states only what the code currently does and cites, not a
  compliance posture or its rationale.
- **Per-environment retention configuration** (whether a given deployment
  actually enables versioning, backups, or a longer/shorter TTL) — that is a
  deployment-layer concern, not a retention-layer one.
- Any step-by-step procedure for running a whole-community deletion request —
  that is a procedure-shaped node, not this reference-shaped one.

## Relationships

- `references`: `architecture-containers-postgres`, `architecture-containers-redis`,
  `architecture-containers-object-storage` — each container's own existence,
  technology, and one-line responsibility, which this node's retention table
  builds on without repeating.

No edge to `layers-data-object-storage-retention` (#1072) or
`layers-data-data-lifecycle` (#1062) is declared: neither id resolves against
`origin/launchpad` at this node's authoring revision (both exist only on
unmerged sibling task branches), and `AGENTS.md`'s own creation step 9 treats
declaring an edge to a target that does not resolve on the merge-target
branch as a hard CI error, not a soft mismatch. Revisit once either merges.

## Scope and omissions

**This node covers** a one-sentence definition of retention, a per-datastore
table stating each datastore's default retention window and the mechanism
that actually removes data, the one recurring shape connecting all three
datastores, and the boundary against the two sibling documents that own
deeper retention/lifecycle detail for object storage and for the per-event
phase structure respectively.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Object-storage bucket-level retention detail (key-shape table, deletion audit trail, versioning gate) | `layers/data/object-storage/retention.md` (#1072), not yet merged |
| The full per-event/channel/community lifecycle phase structure | `layers/data/data-lifecycle.md` (#1062), not yet merged |
| Each datastore's container-level existence and technology name | `architecture-containers-postgres`, `architecture-containers-redis`, `architecture-containers-object-storage` |
| The evidence-class contract (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |
| Compliance/policy rationale for any retention window | Not addressed by this node |
| Per-environment retention configuration (versioning, backups, actual TTL values in production vs. local dev) | A deployment-layer document, not this one |

**Expected but not verified when this node was written:**

- **Whether any Redis key class outside `crates/buzz-pubsub` and
  `crates/buzz-auth` is written without a TTL.** The "nothing in Redis is a
  system of record" claim above is an `INFERENCE`, checked against every
  TTL/EXPIRE call site found in those two crates specifically, not against
  every Redis write in the repository.
- **Whether `.env.example`'s still-present Typesense variables reflect a
  removed datastore with its own now-orphaned retained state** — flagged
  independently in `templates/datastore.md`'s own worked illustration and not
  re-verified here; out of scope for a retention-specific node.
- **Whether production or staging enables S3 bucket versioning**, which
  changes what "delete" actually means for the object-storage row above —
  the same gap `architecture-containers-object-storage` and #1072 already
  name; the answer lives in the private `squareup/block-coder-tf-stacks`
  repository, outside this checkout.
- **Whether either sibling document (#1072, #1062) will land with the exact
  ids assumed in this node's *Boundary* and *Scope* sections above.** Read
  directly from those branches at this node's authoring time, but unmerged
  content can still change before it lands.
