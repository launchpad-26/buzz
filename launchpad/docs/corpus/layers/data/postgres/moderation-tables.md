---
id: layers-data-postgres-moderation-tables
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
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) with no `data` member; a node whose path lives under `layers/` takes `type: layers`, the same disclosed override the sibling `layers/data/postgres/audit-tables.md` (issue #1075, open PR #1875) chose over `templates/data-entity.md`'s own `type: implementation` suggestion, and the same choice PR #1875's own evidence ledger records the `layers/data/object-storage/` siblings (media-objects, minio, on open PR #1874) already made over `templates/datastore.md`'s `type: architecture` suggestion."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1084 assigns this document the path launchpad/docs/corpus/layers/data/postgres/moderation-tables.md directly via its own corpus-plan:v2 alias header comment and Objective sentence, and describes the subject as 'the single canonical data entity node for moderation tables.' Its Definition of Done requires defining identity/key and semantic ownership; summarizing fields by meaning without duplicating generated schema detail; defining relationships, lifecycle and invariants; and linking authoritative migration/schema and read/write code paths rather than copying DDL -- wording that maps onto templates/data-entity.md's required sections (Identity, Attributes and shape, Invariants, Relationships, Provenance, Storage pointer), not templates/datastore.md's."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1084, read directly via gh issue view"
  - statement: "The unmerged sibling audit-tables.md (issue #1075, open PR #1875, read directly via gh api contents at ref task/610-batch-4-data-storage) states in its own introduction and its Scope-and-omissions gap table that `moderation_actions` -- 'a structurally distinct table (its own primary key is (community_id, id), not a hash chain) recording moderator decisions, defined in its own migrations/0006_moderation.sql section' -- is explicitly out of scope for that document and is named as issue #1084's own subject, confirming this node's exclusive subject is `moderation_actions`, not `moderation_reports` or `community_bans`."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1875 (open PR, audit-tables.md), read directly via gh api contents"
  - statement: "architecture-containers-postgres is a merged, validated node on origin/launchpad (confirmed via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus) whose own body states 'Postgres is Buzz's single system of record. It is the durable event store behind every Nostr event the relay accepts, plus the relational tables for communities, channels, membership, moderation, workflows, push state, and audit' -- naming 'moderation' as one of the domains the Postgres container holds, without itself describing any one moderation table's shape."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "migrations/0006_moderation.sql defines moderation_actions with columns community_id (UUID NOT NULL REFERENCES communities(id)), id (UUID NOT NULL DEFAULT gen_random_uuid()), actor_pubkey (BYTEA NOT NULL, 32-byte CHECK), action (TEXT NOT NULL, CHECK'd against a 12-value vocabulary: delete_message, kick, ban, unban, timeout, untimeout, dismiss_report, escalate, resolve:delete, resolve:kick, resolve:ban, resolve:timeout), target_pubkey (BYTEA, nullable, 32-byte CHECK when present), target_event_id (BYTEA, nullable, 32-byte CHECK when present), channel_id (UUID, nullable), reason_code (TEXT, nullable), public_reason (TEXT, nullable), private_reason (TEXT, nullable), matched_principal (TEXT, nullable, CHECK IN ('self','owner')) and created_at (TIMESTAMPTZ NOT NULL DEFAULT now()), with PRIMARY KEY (community_id, id) and a same-community FOREIGN KEY (community_id, channel_id) REFERENCES channels (community_id, id), under a '── Moderation audit ──' section comment stating 'One row per accepted moderation action. Full detail (reporter identities, private reasons, matched NIP-OA principal) stays mod/audit-only; the public tombstone carries only action_id + reason_code + sanitized public_reason.'"
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql"
  - statement: "migrations/0006_moderation.sql also defines two indexes on moderation_actions -- idx_moderation_actions_created (community_id, created_at DESC) for the audit-log read order, and a partial idx_moderation_actions_target_pubkey (community_id, target_pubkey) WHERE target_pubkey IS NOT NULL for target lookups -- and, after moderation_actions exists, ALTER TABLE moderation_reports ADD FOREIGN KEY (community_id, action_id) REFERENCES moderation_actions (community_id, id), under the comment 'Same-community resolution provenance: a report can only be resolved by an action row in its own community.'"
    entry_class: FACT
    evidence:
      - "migrations/0006_moderation.sql"
  - statement: "crates/buzz-db/src/moderation.rs's own module doc states it 'Backs the NIP-56 report queue (moderation_reports), ban/timeout state (community_bans), and the moderation audit trail (moderation_actions) from migrations/0006_moderation.sql,' and states a tenant invariant that 'every function takes a CommunityId and touches exactly one community's rows... no function here may perform a cross-community or global lookup.' The module's MODERATION_ACTION_CHECK_VOCAB constant (a &[&str] of the same 12 values) carries its own comment: 'Keep this in lockstep with migrations/0006_moderation.sql.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/moderation.rs"
  - statement: "crates/buzz-db/src/moderation.rs's insert_action function runs `INSERT INTO moderation_actions (community_id, actor_pubkey, action, target_pubkey, target_event_id, channel_id, reason_code, public_reason, private_reason, matched_principal) VALUES (...) RETURNING id`, binding a NewAction<'_> struct's fields positionally, and returns the generated Uuid; list_actions runs `SELECT id, actor_pubkey, action, target_pubkey, target_event_id, channel_id, reason_code, public_reason, private_reason, matched_principal, created_at FROM moderation_actions WHERE community_id = $1 ORDER BY created_at DESC LIMIT $2`, with a doc comment 'List audit rows, newest first (`buzz moderation audit`).' No other function in this file, and no UPDATE or DELETE statement against moderation_actions, was found anywhere in the repository (grep for 'UPDATE moderation_actions' and 'DELETE FROM moderation_actions' across crates/ returned zero matches)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/moderation.rs"
  - statement: "crates/buzz-db/src/moderation.rs's resolve_report function updates a moderation_reports row's status, resolved_by, resolved_at and action_id ('linking the audit action,' per its own doc comment), scoped `WHERE community_id = $1 AND id = $2 AND status = 'open'` -- the code-level mechanism that populates moderation_reports.action_id with a moderation_actions.id value."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/moderation.rs"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_MODERATION_BAN=9040, KIND_MODERATION_UNBAN=9041, KIND_MODERATION_TIMEOUT=9042, KIND_MODERATION_UNTIMEOUT=9043 and KIND_MODERATION_RESOLVE_REPORT=9044 under a comment stating these are 'Buzz community moderation commands (mod-signed, processed like 9030-series: validated + executed directly, never stored as regular events; every accepted command writes a moderation_actions audit row).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/moderation_commands.rs's handle_moderation_command dispatches KIND_MODERATION_BAN/UNBAN/TIMEOUT/UNTIMEOUT/RESOLVE_REPORT to dedicated handler functions (handle_ban, handle_unban, handle_timeout, handle_untimeout, handle_resolve); every one of those (checked directly for handle_ban, whose body authorizes the action, applies the ban via buzz-db, then calls the shared insert_audit(state, tenant, actor, \"ban\", Some(&target), None, reason.as_deref()) helper) writes exactly one moderation_actions row per accepted command, and insert_audit's own doc comment states 'matched_principal is left None here: that NIP-OA field records which principal an enforcement check matched at the auth seam (L4), not who issued a command.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "moderation_commands.rs's resolution_audit_action function maps a resolved report's client-supplied action string ('dismiss'|'escalate'|'delete'|'kick'|'ban'|'timeout') to the stored moderation_actions.action value ('dismiss_report'|'escalate'|'resolve:delete'|'resolve:kick'|'resolve:ban'|'resolve:timeout'), and the module's own #[cfg(test)] unit test resolve_audit_actions_are_allowed_by_db_check_vocabulary asserts, for every one of those six mapped values, that `buzz_db::moderation::MODERATION_ACTION_CHECK_VOCAB.contains(&audit_action)` -- pinning the handler's action-name mapping against the database CHECK constraint directly, not merely by convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "crates/buzz-relay/src/api/bridge.rs's own section comment states 'Mod-only structured rows (moderation_reports/moderation_actions/community_bans) are not nostr events, so they are served over dedicated NIP-98-authed GET endpoints rather than the REQ/`/query` path (which would force a synthetic event shape and thread a privileged branch onto the shared read hot path). Gated on ModerationAction::ViewQueue via the one capability helper -- never an inline role check.' Its moderation_audit handler function (`GET /moderation/audit`) authorizes the request, then calls `state.db.list_moderation_actions(tenant.community(), clamp_limit(q.limit))` and serializes the rows to JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "crates/buzz-cli/src/commands/moderation.rs's own module doc states 'Reads (reports/restricted/audit) hit dedicated mod-only, ... audit rows are structured queue rows, not public nostr events -- serving...' (over NIP-98-authed HTTP, matching bridge.rs), and its cmd_audit function calls `client.get_authed(&format!(\"/moderation/audit?limit={limit}\"))`, wired from the `ModerationCmd::Audit { limit }` CLI subcommand -- the `buzz moderation audit` command referenced by moderation.rs's own list_actions doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/moderation.rs"
  - statement: "crates/buzz-db/src/deletion.rs's EXPECTED_SCOPED_TABLES constant (the exact set of community-scoped tables its pre-deletion inventory checks) and its PURGE_SCOPED_TABLES constant (the foreign-key-safe child-before-parent purge order) both include moderation_actions; PURGE_SCOPED_TABLES lists moderation_reports before moderation_actions, consistent with moderation_reports.action_id's foreign key onto moderation_actions.id requiring the child row purged first. The module's own doc comment describes it as owning the 'durable whole-community deletion lifecycle,' and DeletionStage's fixed, forward-only stage order names PostgresPurged as the stage at which all EXPECTED_SCOPED_TABLES rows, moderation_actions included, are physically deleted."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/deletion.rs"
  - statement: "migrations/0029_community_deletion.sql's `SELECT attach_community_write_fence('moderation_actions');` (line 557) attaches the enforce_community_write_fence() BEFORE INSERT/UPDATE/DELETE trigger to moderation_actions, alongside events, channels, audit_log and the rest of this migration's community-scoped table list; that trigger calls assert_community_write_allowed(community_id), which raises 'community write fenced: community % generation %' (SQLSTATE object_not_in_prerequisite_state) whenever the row's community's deletion lifecycle is not 'active' -- so once a community leaves 'active', new moderation_actions rows for it are rejected at the database level, not only by application-level checks."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-relay/src/config.rs's own doc comment on the audit_enabled field states 'Whether tamper-evident event/media audit logging is enabled. Defaults to true. This does not control the separate moderation_actions audit trail. Set BUZZ_AUDIT_ENABLED=false for deployments that do not require it' -- audit_log's BUZZ_AUDIT_ENABLED gate does not gate moderation_actions writes; no equivalent enable/disable flag for moderation_actions was found in this file or in crates/buzz-relay/src/handlers/moderation_commands.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-db/src/moderation.rs's own #[cfg(test)] module (gated `#[ignore = \"requires Postgres\"]`) tests tenant isolation for ban/timeout/report functions (e.g. restrictions_are_confined_to_their_community, checked directly), but no test in that module calls insert_action or list_actions -- grepping the module for those two identifiers finds only their own definitions, not a call site inside `mod tests`. Read/write correctness of moderation_actions itself is exercised indirectly, via moderation_commands.rs's resolution_audit_action test above, not by a Postgres-backed test of insert_action/list_actions."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/moderation.rs"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus carries no path under layers/data/postgres/ or layers/data/object-storage/ -- every sibling data-entity/datastore node for this batch (audit-tables, backup-boundary, channel-members-table, channels-table, communities-table, media-objects, minio, and this document's own moderation-tables) exists only on unmerged task branches, so none is a valid relationships.target for this node per AGENTS.md's step 9 merge-target rule."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ path present"
  - statement: "No source found in this repository establishes that any UPDATE or DELETE ever runs against moderation_actions outside the whole-community purge path in crates/buzz-db/src/deletion.rs, so moderation_actions rows are treated here as append-only for the life of the community that produced them -- the same lifecycle shape audit-tables.md's own audit_log node records, reached independently by the identical grep-for-mutating-statements method rather than assumed by analogy."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/moderation.rs"
      - "crates/buzz-db/src/deletion.rs"
    confidence: 0.8
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Data entity: the `moderation_actions` audit trail

The **`moderation_actions` table** is Buzz's per-community record of accepted
moderator decisions -- bans, timeouts, message deletions, kicks, and report
resolutions. This document is a **data-entity** view of it: its identity and
key, what each field means, the invariants that must hold about any row in
it, its relationships to other rows and tables, and where it is stored -- not
`architecture-containers-postgres`'s job (that Postgres exists, its
connection pools, and its migration mechanism, linked below via `part-of`)
and not the job of any future node covering `moderation_reports` or
`community_bans`, `migrations/0006_moderation.sql`'s two sibling tables:
`moderation_actions` has its own primary key shape `(community_id, id)`, is
structurally distinct from both, and is this document's exclusive subject,
per issue #1084 and per the unmerged sibling `audit-tables.md` (issue #1075),
which explicitly defers this table to this document rather than covering it
itself.

## Identity

A row's identity is the pair **`(community_id, id)`** --
`moderation_actions`'s declared primary key in `migrations/0006_moderation.sql`.
`id` is a `UUID NOT NULL DEFAULT gen_random_uuid()`, server-generated at
insert time by `insert_action`'s `RETURNING id` clause -- not a
client-supplied value, and not a monotonic sequence the way `audit_log`'s
`seq` is. There is no cross-community uniqueness constraint on `id` alone;
only the composite key identifies a row, the same shape
`architecture-containers-postgres` already describes generally for this
repository's tenant-scoped tables.

**Semantic ownership.** `moderation_actions` is written and read exclusively
through `crates/buzz-db/src/moderation.rs`'s `insert_action` and
`list_actions` functions. The module's own doc comment states its tenant
invariant plainly: "every function takes a `CommunityId` and touches exactly
one community's rows... no function here may perform a cross-community or
global lookup." No other crate issues SQL against this table directly.

## Attributes and shape

Not JSON Schema -- `moderation_actions` is a plain relational table with no
JSON-typed column, the same treatment `audit-tables.md`'s own `audit_log`
node gives its own (mostly) relational shape. Each row, per
`migrations/0006_moderation.sql` and `crates/buzz-db/src/moderation.rs`'s
`NewAction`/`ActionRecord` field docs:

| Column | Type | Meaning |
|---|---|---|
| `community_id` | `UUID NOT NULL REFERENCES communities(id)` | Tenant this action belongs to; leads the primary key. |
| `id` | `UUID NOT NULL DEFAULT gen_random_uuid()` | Server-generated row identity. |
| `actor_pubkey` | `BYTEA NOT NULL` (32 bytes) | The acting moderator's pubkey. |
| `action` | `TEXT NOT NULL`, CHECK-constrained | One of `delete_message`, `kick`, `ban`, `unban`, `timeout`, `untimeout`, `dismiss_report`, `escalate`, `resolve:delete`, `resolve:kick`, `resolve:ban`, `resolve:timeout` -- mirrored in `moderation.rs`'s `MODERATION_ACTION_CHECK_VOCAB`, whose own comment warns "keep this in lockstep with `migrations/0006_moderation.sql`." |
| `target_pubkey` | `BYTEA`, nullable (32 bytes when present) | Actioned member, when the action targets a pubkey. |
| `target_event_id` | `BYTEA`, nullable (32 bytes when present) | Actioned event, when the action targets an event. |
| `channel_id` | `UUID`, nullable | Channel context, when known; FK-constrained to `channels (community_id, id)`. |
| `reason_code` | `TEXT`, nullable | Machine-readable rule/reason code (e.g. `"spam"`). |
| `public_reason` | `TEXT`, nullable | Sanitized reason, safe for the public tombstone. |
| `private_reason` | `TEXT`, nullable | Mod-only context; `moderation.rs`'s field doc states it "never leaves the audit surface." |
| `matched_principal` | `TEXT`, nullable, CHECK IN (`'self'`,`'owner'`) | Which NIP-OA principal an *enforcement* check matched, per `insert_audit`'s own doc comment -- not who issued the command. |
| `created_at` | `TIMESTAMPTZ NOT NULL DEFAULT now()` | When the row was written; the sort key for both the read query and the community-purge inventory. |

Unlike `moderation_reports`, this table's DDL has no CHECK forcing exactly one
of `target_pubkey`/`target_event_id`: both are independently nullable, and
which is populated (or neither) follows from `action`'s own semantics at each
call site in `moderation_commands.rs`, not a database constraint.

## Invariants

- **Action vocabulary.** `action` is CHECK-constrained to the 12-value list
  above. `crates/buzz-db/src/moderation.rs`'s `MODERATION_ACTION_CHECK_VOCAB`
  duplicates that list in Rust for the write side, and
  `crates/buzz-relay/src/handlers/moderation_commands.rs`'s own
  `#[cfg(test)]` unit test `resolve_audit_actions_are_allowed_by_db_check_vocabulary`
  asserts, for every value `resolution_audit_action` can produce, that
  `MODERATION_ACTION_CHECK_VOCAB.contains(&audit_action)` -- a direct,
  checked pin between the handler's `resolve:*` mapping and the database
  constraint, not merely a comment promising the two stay in sync.
- **Community write-fence.** `migrations/0029_community_deletion.sql`
  attaches `enforce_community_write_fence()` to `moderation_actions`
  (line 557, alongside `events`, `channels`, and `audit_log`). That trigger
  calls `assert_community_write_allowed(community_id)`, which raises
  `community write fenced: community % generation %` whenever the row's
  community's deletion lifecycle is not `'active'` -- a community leaving
  `'active'` stops new `moderation_actions` writes for it at the database
  level.
- **Append-only in application code.** No `UPDATE` or `DELETE` statement
  against `moderation_actions` was found anywhere in this repository outside
  the whole-community purge path in `crates/buzz-db/src/deletion.rs` --
  checked by grepping `crates/` directly, not assumed by analogy with
  `audit_log`. This is recorded as an `INFERENCE`, not a `FACT`: absence of a
  call site is evidence of the current behavior, not a schema-level
  guarantee the way `audit_log`'s append-only shape is reinforced by its hash
  chain.
- **Not gated by `BUZZ_AUDIT_ENABLED`.** `crates/buzz-relay/src/config.rs`'s
  own doc comment on `audit_enabled` states plainly that the flag "does not
  control the separate `moderation_actions` audit trail" -- unlike `audit_log`,
  no environment flag was found in this repository that disables
  `moderation_actions` writes.

## Lifecycle

A `moderation_actions` row is written once, by
`crates/buzz-relay/src/handlers/moderation_commands.rs`'s shared `insert_audit`
helper, immediately after its triggering command is authorized and applied
(e.g. `handle_ban` applies the ban via `buzz-db`, *then* calls `insert_audit`
with `action = "ban"`). Rows are never updated after insert; a row's
lifespan is bounded by its **community's** own lifecycle rather than treated
as permanent independently of it: `crates/buzz-db/src/deletion.rs` lists
`moderation_actions` in both `EXPECTED_SCOPED_TABLES` and
`PURGE_SCOPED_TABLES`, and `DeletionStage`'s fixed, forward-only stage order
reaches `PostgresPurged` -- the stage at which those rows are physically
deleted. `PURGE_SCOPED_TABLES` purges `moderation_reports` *before*
`moderation_actions`, consistent with `moderation_reports.action_id`'s
foreign key onto `moderation_actions.id` requiring the child row removed
first. A permanently deleted community's moderation history is deleted with
it.

## Relationships

- **Foreign key (community).** `community_id` carries `REFERENCES
  communities(id)` in the table's own DDL -- a row cannot name a community
  that does not exist.
- **Foreign key (channel).** `(community_id, channel_id)` carries
  `REFERENCES channels (community_id, id)`, same-community, when
  `channel_id` is populated.
- **Foreign key (from `moderation_reports`, not to it).**
  `migrations/0006_moderation.sql` adds `moderation_reports.action_id`
  as a foreign key onto `moderation_actions (community_id, id)` *after*
  `moderation_actions` is created, under the comment "Same-community
  resolution provenance: a report can only be resolved by an action row in
  its own community." `crates/buzz-db/src/moderation.rs`'s `resolve_report`
  function is the code path that populates that column, via `UPDATE
  moderation_reports SET ... action_id = $5 WHERE ... status = 'open'`.
  This is a row-to-row relationship in code, not a corpus `relationships`
  edge, because no `moderation_reports`-entity corpus node exists yet.
- **Corpus-level.** This node declares one `relationships` entry: `part-of`
  → `architecture-containers-postgres` (merged), naming that
  `moderation_actions` is one of the tables the Postgres container document's
  "communities, channels, membership, moderation, workflows, push state, and
  audit" description already gestures at generally. No `references` edge is
  declared toward any `layers/data/postgres/*` sibling (`audit-tables`,
  `channels-table`, and the rest) -- none is merged on `origin/launchpad` at
  this node's authoring time, and a `relationships.target` naming an
  unmerged id is a hard validation error on the branch this document merges
  into, per `AGENTS.md`'s step 9.

## Provenance

`moderation_actions` sits between a wire-triggered and a purely
server-derived entity. Its rows are triggered by **mod-signed command
events** -- `crates/buzz-core/src/kind.rs`'s `KIND_MODERATION_BAN` (9040),
`KIND_MODERATION_UNBAN` (9041), `KIND_MODERATION_TIMEOUT` (9042),
`KIND_MODERATION_UNTIMEOUT` (9043) and `KIND_MODERATION_RESOLVE_REPORT`
(9044) -- under that file's own comment: "processed like 9030-series:
validated + executed directly, never stored as regular events; every
accepted command writes a `moderation_actions` audit row." So the
*triggering* event is a real, signed Nostr event on the wire, but it is
**never persisted as a stored event** the way an ordinary `kind:1` message
is, and the resulting `moderation_actions` row is **never re-serialized as
an event** either: `crates/buzz-relay/src/api/bridge.rs`'s own comment states
that these rows "are not nostr events, so they are served over dedicated
NIP-98-authed GET endpoints rather than the REQ/`/query` path," and
`crates/buzz-cli/src/commands/moderation.rs`'s `cmd_audit` reads them the
same way, via `GET /moderation/audit`. A reader expecting to find
`moderation_actions` rows through a standard `REQ` filter or `POST /query`
will not.

## Storage pointer

Postgres, table `moderation_actions`. `architecture-containers-postgres`
(linked above via `part-of`) is the node for the container's own facts --
connection pooling, migration mechanism, deployment/partitioning -- and
already names "moderation" as one of the domains `buzz-db` owns. That detail
is not repeated here; this node names the table `moderation_actions` lives
in and links out, per `AGENTS.md`'s links-instead-of-duplicating rule.

## Scope and omissions

**This document covers** `moderation_actions`'s identity and key, its
column shape and field meanings, the invariants its CHECK constraint and
write-fence trigger enforce, its write-once-per-command lifecycle bounded by
community deletion, its relationships to `communities`, `channels`, and
`moderation_reports`, its provenance as triggered-by-command-event-but-not-
itself-an-event, and where it is physically stored.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `moderation_reports` (NIP-56 report queue) and `community_bans` (ban/timeout restriction state) -- `migrations/0006_moderation.sql`'s two sibling tables | Future `layers/data/postgres/*` corpus nodes, not this one |
| `audit_log` -- a structurally distinct, hash-chained table with a different write path (`crates/buzz-audit`) | `audit-tables.md`, issue #1075 (open PR #1875) |
| Postgres's own connection pooling, migration mechanism, and deployment/partitioning facts | `architecture-containers-postgres` (merged), linked above via `part-of` |
| NIP-OA ban-enforcement semantics (what `matched_principal` values mean at the auth seam, beyond this table's own column) | Not established here -- out of scope for a data-entity node |
| Whether any staging/production deployment sets a rate limit or additional gate on moderation command processing | Not established here -- this repository's deployment pipelines live in separate private repositories this task did not open, the same gap `audit-tables.md` records for `BUZZ_AUDIT_ENABLED` |

**Expected but not verified when this node was written:**

- **Whether the absence of a database-level "exactly one target" CHECK on
  `moderation_actions` (unlike `moderation_reports`'s explicit CHECK) is
  deliberate or incidental was not established.** Every handler call site
  checked (`handle_ban`, and `resolution_audit_action`'s mapping) populates
  target columns consistently with its own action, but nothing in the schema
  enforces that pattern the way `moderation_reports`'s CHECK does.
- **No Postgres-backed test directly exercises `insert_action` or
  `list_actions`.** `moderation.rs`'s own `#[cfg(test)]` module (gated
  `#[ignore = "requires Postgres"]`) tests ban/timeout/report tenant
  isolation, but neither function is called from that module; the closest
  direct test coverage found is `moderation_commands.rs`'s
  `resolve_audit_actions_are_allowed_by_db_check_vocabulary`, which pins the
  `action` vocabulary mapping without exercising the database round trip.
- **Cross-model review was not run.** This task's own instructions scope
  this session to isolate/plan/build/verify/commit only, with the batch
  owner's later bundling step responsible for adjudication and any
  cross-model pass.
