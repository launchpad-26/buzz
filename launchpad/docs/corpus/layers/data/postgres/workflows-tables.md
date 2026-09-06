---
id: layers-data-postgres-workflows-tables
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
  - statement: "type is overridden to `layers` rather than `templates/data-entity.md`'s own worked-example type of `implementation`. This mirrors a convention earlier tasks in this same #610 batch already applied to every other document under `layers/data/...` -- confirmed to be current batch guidance from the task dispatch brief, not independently verified against a merged sibling file, because no `layers/data/postgres/*` sibling exists on `origin/launchpad` at the recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#610 batch task dispatch brief (overnight corpus-batch-author run, 2026-08-30)"
  - statement: "`node.schema.json`'s `type` enum is a closed 13-member list -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and `layers` is one of its members."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1090 targets `launchpad/docs/corpus/layers/data/postgres/workflows-tables.md` as the single canonical data entity node for workflows tables, with a definition of done requiring: identity/key and semantic ownership; fields summarized by meaning without duplicating generated schema detail; relationships, lifecycle and invariants; and links to authoritative migration/schema and read/write code paths."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1090 definition of done, opened directly via gh issue view"
  - statement: "`templates/data-entity.md` states its six required sections for a real data-entity instance are Identity, Attributes and shape, Invariants, Relationships to other entities, Provenance, and Storage pointer, and that a data-entity node is not a storage document (that is the datastore template's job) and not a wire-protocol document (that is the event-kind template's job)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/data-entity.md"
  - statement: "`migrations/0001_initial_schema.sql` defines four workflow tables under the comment 'Conformance: \"Workflows, runs, approvals, webhooks, schedules\"': `workflows` (community_id, id, name, owner_pubkey, channel_id, definition JSONB, definition_hash, status workflow_status, enabled, created_at, updated_at; PRIMARY KEY (community_id, id); FK community_id -> communities(id); FK (community_id, owner_pubkey) -> users(community_id, pubkey); FK (community_id, channel_id) -> channels(community_id, id)); `workflow_runs` (community_id, id, workflow_id, status run_status, trigger_event_id, current_step, execution_trace JSONB, trigger_context JSONB, started_at, completed_at, error_message, created_at; PRIMARY KEY (community_id, id); FK (community_id, workflow_id) -> workflows(community_id, id) ON DELETE CASCADE); `workflow_approvals` (community_id, token BYTEA, workflow_id, run_id, step_id, step_index, approver_spec, status approval_status, approver_pubkey, note, granted_at, denied_at, expires_at, created_at; PRIMARY KEY (community_id, token); FK (community_id, workflow_id) -> workflows ON DELETE CASCADE; FK (community_id, run_id) -> workflow_runs ON DELETE CASCADE); and `scheduled_workflow_fires` (community_id, workflow_id, scheduled_for, claimed_at, workflow_run_id; PRIMARY KEY (community_id, workflow_id, scheduled_for); FK (community_id, workflow_id) -> workflows ON DELETE CASCADE; FK (community_id, workflow_run_id) -> workflow_runs ON DELETE NO ACTION)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "The same file defines three enum types used by these tables: `workflow_status AS ENUM ('active', 'disabled', 'archived')`, `run_status AS ENUM ('pending', 'running', 'waiting_approval', 'completed', 'failed', 'cancelled')`, and `approval_status AS ENUM ('pending', 'granted', 'denied', 'expired')`."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "The file's own inline comments state `scheduled_workflow_fires` implements 'the at-most-once cron fire claim' via `UNIQUE (community_id, workflow_id, scheduled_for)' -- 'only the pod that wins the claim insert creates the run' -- and that its FK to `workflow_runs` uses `NO ACTION` rather than `SET NULL` because 'community_id is shared with the claim PK and is NOT NULL, so SET NULL is unimplementable here; a future delete of a still-linked run is blocked rather than orphaning the at-most-once claim row.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "`migrations/0031_workflow_run_error_codes.sql` is the only migration after `0001_initial_schema.sql` that alters any of these four tables (checked by grepping every migration for `ALTER TABLE (workflows|workflow_runs|workflow_approvals|scheduled_workflow_fires)`, one hit). It adds `workflow_runs.error_code TEXT` and backfills `'legacy_unclassified'` for pre-existing rows with `status IN ('failed', 'cancelled')`, under the comment 'Stable workflow failure classification, kept separate from redacted human diagnostics.'"
    entry_class: FACT
    evidence:
      - "migrations/0031_workflow_run_error_codes.sql"
  - statement: "`crates/buzz-db/src/store/workflow.rs` is the sole read/write code path for all four tables (its own module doc states 'Workflow CRUD -- workflows, workflow_runs, and workflow_approvals tables'; grepping `crates/` for `FROM workflows`, `INSERT INTO workflows`, `UPDATE workflows`, `workflow_runs`, `workflow_approvals` and `scheduled_workflow_fires` outside `buzz-db` and `buzz-workflow` returns only test/router references, no other SQL call sites)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "`workflows` is keyed `(community_id, id)`, not by a globally unique `id` alone: `get_workflow`'s doc comment states 'the same workflow UUID can exist in two communities, so a request-scoped lookup must bind both,' and `claim_scheduled_workflow_fire`'s doc comment states the same for its own claim binding, adding that 'resolving the owning community from `id` alone is ambiguous and would fan a single claim across every community holding that UUID.' `workflow_approvals` is keyed `(community_id, token)` for the identical reason, per `get_approval_by_stored_hash`'s doc comment: 'the same token bytes could in principle collide across communities, so the lookup binds the server-resolved community alongside the token.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "`community_id` on every row is server-resolved, never client-supplied: `buzz-core`'s `CommunityId` newtype wraps a `Uuid` and its constructor doc comment states 'this is intentionally not a parse-from-client entry point: callers must already hold a server-trusted UUID.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "Approval tokens are never stored in plaintext: `hash_approval_token` SHA-256-hashes the raw token before every INSERT/SELECT/UPDATE against `workflow_approvals.token`, and the module's own security note states 'Approval tokens are stored as SHA-256 hashes (never plaintext).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "A `workflows` row's lifecycle has two independent axes: `status` (`workflow_status`, comment 'Update a workflow's status (active -> disabled -> archived)') and `enabled` (a boolean gate toggled independently by `set_workflow_enabled`, and forced to `FALSE` in bulk by `disable_workflows_for_owner_in_channel` -- labeled `SEC-006` -- 'when the owner loses channel membership ... so their workflows stop firing durably -- across pods and restarts.'). `list_enabled_channel_workflows`'s doc comment confirms the trigger-matching path requires both: 'Only returns workflows with status = 'active' AND enabled = TRUE.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "Deleting a `workflows` row cascades to its `workflow_runs` and `workflow_approvals` (and, via `workflow_runs`, blocks a `scheduled_workflow_fires.workflow_run_id` link rather than orphaning it): `delete_workflow`'s doc comment states plainly 'Delete a workflow and all its runs/approvals (CASCADE).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
      - "migrations/0001_initial_schema.sql"
  - statement: "`upsert_workflow` inserts at a caller-supplied NIP-33 `d`-tag UUID with `ON CONFLICT (community_id, id) DO UPDATE ... WHERE workflows.owner_pubkey = EXCLUDED.owner_pubkey AND workflows.channel_id IS NOT DISTINCT FROM EXCLUDED.channel_id`, and its doc comment states this predicate 'keeps a learned workflow UUID from becoming a cross-user or cross-channel overwrite primitive while still making retries idempotent' -- a row whose owner or channel does not match the existing one is rejected (`AccessDenied`), not silently overwritten."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "`update_approval`'s WHERE clause includes `AND status = 'pending'`, documented under '# TOCTOU safety (N5)' as ensuring 'two concurrent grant/deny requests cannot both succeed'; a second request against an already-decided approval updates zero rows and the function returns `Ok(false)`, which callers are told to treat as an HTTP 409 conflict rather than a silent success."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "`claim_scheduled_workflow_fire` performs its INSERT with `ON CONFLICT (community_id, workflow_id, scheduled_for) DO NOTHING ... RETURNING ...`, so only the first caller to reach a given `(community_id, workflow_id, scheduled_for)` triple receives `Some`; every other caller for the same triple receives `None` and must not create a duplicate `workflow_runs` row for that schedule instant."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "`update_workflow_run`'s SQL sets `started_at` via `CASE WHEN $6 = 'running' AND started_at IS NULL THEN NOW() ELSE started_at END` and `completed_at` via `CASE WHEN $7 IN ('completed','failed','cancelled') THEN NOW() ELSE completed_at END`, both compared against the bind parameter rather than the column's post-UPDATE value -- the function's own comment ('Fix C3') states an earlier version read `status` from the column after `SET status = ?` had already changed it, making the `started_at` condition always false, and that the fix now checks the bind parameter directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "None of these four tables carries a Nostr event id or any other event-derived column; every write is issued directly by relay-side code in `crates/buzz-db/src/store/workflow.rs` in response to a command, an event-triggered `WorkflowEngine` decision, a cron/interval fire, or an HTTP approval action -- not by ingesting and storing a signed Nostr event the way `events` or `thread_metadata` are populated."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
    confidence: 0.75
  - statement: "`architecture-flows-workflow-execution` (merged, `type: architecture`) documents that a workflow run's three trigger paths -- an in-process channel-event hook, a 60-second cron/interval loop, and an HTTP webhook handler -- are wired through `WorkflowEngine`, and separately that the per-channel enabled-workflow list is read through a 10-second TTL cache invalidated at 'the two workflow mutation sites (command upsert, NIP-09 deletion).' This corroborates, from the execution side, `update_workflow`'s own cache-invalidation NOTE cited above from the storage side."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "`architecture-containers-postgres` (merged, `type: architecture`) is the corpus's existing container-level document for this repository's single Postgres instance, the technology that physically holds all four tables described here."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "At the recorded revision, `origin/launchpad`'s corpus tree carries no `layers/data/postgres/*` sibling document -- only `layers/data/postgres/workflows-tables.md` (this node) is being introduced by this task -- so a `relationships` edge to any such sibling would not resolve in CI and is correctly omitted."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ path present at this revision"
---

# Workflows tables (Postgres)

The four Postgres tables backing Buzz's workflow engine: `workflows` (a
workflow's definition and lifecycle state), `workflow_runs` (one execution of
a workflow), `workflow_approvals` (a pending or resolved human approval gate
inside a run), and `scheduled_workflow_fires` (the at-most-once claim record
for a `schedule`-triggered workflow's cron/interval fires). This is a
data-entity node, following `templates/data-entity.md`: what these tables
are, what identifies a row, what must always be true, and how they relate --
not a description of the workflow *definition* JSON/DSL itself, which is
`buzz-workflow`'s own concern.

## Identity

- **`workflows`** — primary key `(community_id, id)`. The `id` UUID is *not*
  globally unique: the same UUID can exist in two different communities
  (`get_workflow`'s own doc comment states this explicitly), because a
  workflow's `id` is frequently the caller-supplied NIP-33 `d`-tag value from
  the defining event, not a server-minted global identifier. Every lookup and
  mutation therefore binds both `community_id` and `id`.
- **`workflow_runs`** — primary key `(community_id, id)`. Same non-global-
  uniqueness reasoning as `workflows`: a run's `id` is scoped to its owning
  community, and every run row also carries `workflow_id` (itself only unique
  within that same community).
- **`workflow_approvals`** — primary key `(community_id, token)`, where
  `token` is the *hashed* (SHA-256) form of a raw approval token minted at
  approval-creation time. The raw token is never stored; every lookup hashes
  the caller-supplied token before querying.
- **`scheduled_workflow_fires`** — primary key `(community_id, workflow_id,
  scheduled_for)`. This is the table's whole reason to exist: the primary key
  itself is the at-most-once claim boundary for one workflow's one schedule
  instant. A row's existence, not any status column, is the fact being
  recorded.

**Semantic ownership.** `community_id` on every row is a server-resolved
value, never accepted from a client — it is produced by host-derived tenant
resolution upstream (`buzz-core::CommunityId`'s constructor is explicitly not
a parse-from-client entry point) and threaded through every `buzz-db`
function in this file as an explicit parameter rather than re-derived from
another column. `workflows.owner_pubkey` is the human/agent identity that
owns a workflow definition; `workflow_approvals.approver_pubkey` is the
identity that acted on one approval. Neither of these pubkey columns
participates in either table's primary key.

## Attributes and shape

Only fields whose *meaning* is not already obvious from the migration's
column list are described here; see `migrations/0001_initial_schema.sql`
(lines 358–466) for exact types, defaults and nullability.

- **`workflows.status`** (`workflow_status`) — the workflow *definition's*
  own lifecycle stage: `active`, `disabled`, or `archived`. Distinct from
  `enabled` (see Invariants) — a workflow can be `active` and yet not fire
  because `enabled = FALSE`.
- **`workflows.definition`** / **`definition_hash`** — the canonical JSON of
  the workflow's trigger/step definition, and a SHA-256 hash of that same
  JSON. The hash lets a caller detect a definition change without diffing
  the full JSON blob.
- **`workflow_runs.execution_trace`** — a JSON array, one entry per completed
  step, appended to as a run progresses; it is the run's own audit trail, not
  a separate table.
- **`workflow_runs.trigger_context`** — the serialized `TriggerContext`
  captured at run start, so a post-approval resume can restore the original
  trigger data and resolve `{{trigger.*}}` template variables later in
  execution. Nullable, and explicitly documented as `NULL` for runs created
  before this column existed.
- **`workflow_runs.error_code`** vs **`error_message`** — deliberately
  separate columns, added in `migrations/0031_workflow_run_error_codes.sql`:
  `error_code` is a stable, machine-readable classification (`TEXT`, additive
  across rolling upgrades, per that migration's own comment); `error_message`
  is a redacted human-readable diagnostic. `WorkflowRunFailure`'s own doc
  comments state callers should key logic off `error_code`, never parse
  `error_message`.
- **`workflow_approvals.approver_spec`** — *who may act* on this approval
  (a user mention or role spec), fixed at creation time, distinct from
  `approver_pubkey` — *who actually acted*, `NULL` until someone does.
- **`scheduled_workflow_fires.claimed_at`** — a server (database) timestamp
  for when a pod won this claim, distinct from `scheduled_for` — the
  authoritative schedule instant the claim represents. `claimed_at` is what
  the retention janitor prunes by; `scheduled_for` is what interval
  schedulers read back as their `last_fired` anchor.

## Invariants

- **CASCADE ownership.** Deleting a `workflows` row deletes all of its
  `workflow_runs` and `workflow_approvals` (`ON DELETE CASCADE` on both FKs);
  a `scheduled_workflow_fires` row whose `workflow_run_id` still points at a
  deleted run is *not* nulled out (`ON DELETE NO ACTION`) — the migration's
  own comment states this is deliberate: `community_id` is `NOT NULL` and
  shared with the claim's primary key, so `SET NULL` is not implementable,
  and blocking the delete guards the at-most-once claim row rather than
  orphaning it silently.
- **Independent lifecycle axes.** `workflows.status` and `workflows.enabled`
  gate trigger eligibility together, not separately: the trigger-matching
  path requires `status = 'active' AND enabled = TRUE`. A workflow can move
  `active -> disabled -> archived` without ever touching `enabled`, and
  `enabled` can flip independently of `status` (including a bulk, owner-
  scoped disable when its owner loses channel membership).
- **At-most-once scheduled fire.** Only the first `INSERT ... ON CONFLICT
  (community_id, workflow_id, scheduled_for) DO NOTHING RETURNING ...` for a
  given triple returns a row; every other concurrent caller for the same
  triple must not create a duplicate `workflow_runs` row for that instant.
  This is the only invariant this table exists to enforce.
- **TOCTOU-safe approval resolution.** An approval can move from `pending` to
  `granted`/`denied` exactly once: the UPDATE's own `WHERE ... AND status =
  'pending'` predicate makes a second concurrent grant/deny touch zero rows,
  which callers must treat as a conflict, not a silent success.
- **Owner/channel-locked upsert.** A NIP-33 `d`-tag upsert
  (`ON CONFLICT (community_id, id) DO UPDATE ... WHERE
  workflows.owner_pubkey = EXCLUDED.owner_pubkey AND workflows.channel_id IS
  NOT DISTINCT FROM EXCLUDED.channel_id`) only succeeds when the existing
  row's owner and channel match; a mismatched attempt returns zero rows and
  is surfaced as `AccessDenied`, not a cross-user overwrite.
- **Timestamp transitions read the intended state, not the stored one.**
  `update_workflow_run`'s `started_at`/`completed_at` CASE expressions
  compare against the bind parameter being written, not the row's
  post-UPDATE column value — the function's own "Fix C3" comment documents a
  prior version that silently never stamped `started_at` because it made
  this exact mistake.
- **A mutation is not visible to trigger-matching until the cache clears.**
  `update_workflow`, `update_workflow_status`, and `set_workflow_enabled` all
  carry the same NOTE: a caller changing trigger-relevant state must
  explicitly invalidate `WorkflowEngine`'s per-`(community_id, channel_id)`
  cache, or matching lags the change by up to the cache's TTL (documented
  elsewhere, in `architecture-flows-workflow-execution`, as 10 seconds).

## Relationships to other entities

As foreign keys in code (not yet as corpus `relationships`, since no sibling
data-entity node for `workflows`/`workflow_runs`/`workflow_approvals` exists
in the corpus today):

- `workflow_runs.(community_id, workflow_id)` → `workflows.(community_id,
  id)`, `ON DELETE CASCADE`.
- `workflow_approvals.(community_id, workflow_id)` → `workflows.(community_id,
  id)`, `ON DELETE CASCADE`.
- `workflow_approvals.(community_id, run_id)` → `workflow_runs.(community_id,
  id)`, `ON DELETE CASCADE`.
- `scheduled_workflow_fires.(community_id, workflow_id)` →
  `workflows.(community_id, id)`, `ON DELETE CASCADE`.
- `scheduled_workflow_fires.(community_id, workflow_run_id)` →
  `workflow_runs.(community_id, id)`, `ON DELETE NO ACTION` (see Invariants).
- `workflows.(community_id, channel_id)` → `channels.(community_id, id)`, and
  `workflows.(community_id, owner_pubkey)` → `users.(community_id, pubkey)`
  — a workflow definition belongs to exactly one channel (or none) and one
  owner identity.

As corpus `relationships` (declared in this node's own front matter): a
`part-of` edge to `architecture-containers-postgres`, the container-level
document for the single Postgres instance holding these tables; and a
`references` edge to `architecture-flows-workflow-execution`, which documents
the runtime code paths (`WorkflowEngine`, the trigger-matching cache, the
cron/interval loop, the webhook handler) that read and write the rows
described here.

## Provenance

None of these four tables has a Nostr event as its own canonical form — no
column stores an event id the way `thread_metadata` or the `events` table
does. Instead, every write is issued directly by relay-side code in
`crates/buzz-db/src/store/workflow.rs`, reached from: a command handler (workflow
create/upsert), `WorkflowEngine`'s event-triggered execution path, the
cron/interval scheduler loop, or the HTTP approval-grant/deny handlers. A
workflow's `id` frequently originates from a NIP-33 `d`-tag on the defining
event (per `upsert_workflow`'s own doc comment), but the row itself — its
`status`, `enabled` flag, run history, and approval decisions — is
server-derived state, not a materialized projection kept in sync with a
still-existing event stream the way thread counters are.

## Storage pointer

Postgres — this repository's single Postgres instance, per
`architecture-containers-postgres` (linked above via `part-of`). No column
type, index, or partitioning detail is restated here; see
`migrations/0001_initial_schema.sql` (lines 358–466) and
`migrations/0031_workflow_run_error_codes.sql` for the authoritative schema,
and `crates/buzz-db/src/store/workflow.rs` for every read/write code path against
it.

## Scope and omissions

**This document covers** the identity, field meanings, invariants,
relationships, provenance and storage location of the `workflows`,
`workflow_runs`, `workflow_approvals`, and `scheduled_workflow_fires`
Postgres tables, as they exist in `migrations/0001_initial_schema.sql` and
`migrations/0031_workflow_run_error_codes.sql`, and as they are read and
written by `crates/buzz-db/src/store/workflow.rs`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The workflow definition's own JSON/DSL semantics (trigger types, step types, `evalexpr` conditions) | `buzz-workflow` crate — not a subject of this table-storage document |
| The runtime execution flow (trigger matching, the per-channel cache, the cron loop, the webhook handler) at a walkthrough level | `architecture-flows-workflow-execution` (linked above via `references`) |
| Postgres as a container — its technology, version, and container-level responsibility | `architecture-containers-postgres` (linked above via `part-of`) |
| A formal `datastore`-template document for Postgres as a whole (schema/namespace inventory across *all* tables, migration mechanism generally, access-pattern summary generally) | not yet authored; `templates/datastore.md` exists but no instance has been written |

**Expected but not verified when this node was written:**

- **No live database was queried.** Every claim above is checked against the
  migration SQL and the `buzz-db` code that issues queries against it, not
  against a running Postgres instance's actual `information_schema`.
- **`WorkflowEngine`'s cache TTL** (cited above as "10 seconds," per
  `architecture-flows-workflow-execution`) was not independently re-verified
  against `crates/buzz-workflow/src/lib.rs` in this task — it is carried
  from that already-merged sibling node rather than re-derived here, to
  avoid restating what that node already establishes.
- **Whether a future `layers/data/postgres/*` sibling for another table
  family will want to declare a relationship back to this node** was not
  resolved — no such sibling exists on `origin/launchpad` at the recorded
  revision, so none is declared here (see the evidence ledger's `git_ls_tree`
  entry).
