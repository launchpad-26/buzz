---
id: capabilities-communities-community-creation
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's `type` enum names the corpus surface a node documents, not the prose form its body takes; no enum member is named `flow`. This node's body is organized in the trigger/preconditions/ordered-interactions/failure-and-rollback shape the already-merged architecture-flows nodes use (e.g. architecture-flows-event-ingestion), but its own `type` is `capabilities` rather than `architecture` because the target path and this task's own directive place it under the capabilities/communities surface, not the architecture family; the community-creation capability, not a piece of standing system structure, is the subject this node's id and location commit it to."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch instructions for issue #732 (id capabilities-communities-community-creation, type capabilities, target launchpad/docs/corpus/capabilities/communities/community-creation.md)"
  - statement: "`POST /operator/communities` creates a community host and, when `initial_owner_pubkey` is supplied with `create_only: true`, atomically bootstraps its initial owner in one call; the route is registered on the relay's operator router distinct from the Nostr event ingest data plane."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:1-27"
      - "crates/buzz-relay/src/router.rs:83-86"
  - statement: "The request body accepts `host` (required), `initial_owner_pubkey` (optional), and `create_only` (optional, default false); the response reports `community_id`, the canonical stored `host`, a `status` of `created` or `existed`, and the echoed `owner_pubkey` when an owner bootstrap ran."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:41-69"
  - statement: "`validate_host` requires the caller to submit an already-normalized authority: non-empty, at most 255 bytes (matching `communities.host VARCHAR(255)`), free of control/whitespace characters, free of scheme/path/query/userinfo, and byte-identical to its own re-serialization through `normalize_host` and a bare-authority URL parse — rejecting, for example, uppercase hosts, trailing dots, and default ports (:80/:443) rather than silently normalizing them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:77-171"
  - statement: "When `create_only` is true, an `initial_owner_pubkey` is required and must be a 64-character hex string; the handler calls `Db::create_community_with_owner`, which opens one Postgres transaction, takes a per-owner-pubkey advisory lock (`pg_advisory_xact_lock`, keyed by an FNV-1a hash of the pubkey) to serialize concurrent creates against the same intended owner, inserts the `communities` row with `ON CONFLICT (lower(host)) DO NOTHING`, and — only if a new row was actually inserted — checks the owner's existing `relay_members` owner-role count against the effective per-owner limit before inserting the new owner's `relay_members` row; the whole sequence commits or rolls back as one transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:280-316"
      - "crates/buzz-db/src/store/community.rs:317-405"
  - statement: "The per-owner limit defaults to 5 (`MAX_COMMUNITIES_PER_OWNER`) and can be raised deployment-wide via `BUZZ_MAX_COMMUNITIES_PER_OWNER` (a missing, unparsable, or non-positive value falls back to the default); `create_community_with_owner` enforces it inside the same transaction as the owner insert, so two concurrent creates for the same owner cannot both pass the count check."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_members.rs:406-426"
  - statement: "`create_community_with_owner` distinguishes three non-error outcomes: `Created` (a new host row and owner, or an identical retried create that found the same host+owner pairing already present), `HostExists` (the host row already belongs to a different owner, or belongs to no still-active owner match — the transaction is rolled back and no owner row is touched), and `LimitReached` (the host row's own insert would-be-committed community is discarded by rollback because the intended owner is already at the cap)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/community.rs:42-49"
      - "crates/buzz-db/src/store/community.rs:317-405"
  - statement: "When `create_only` is false (the legacy convergence mode, still used by deployment operators and startup tooling), the handler instead calls `Db::ensure_configured_community`, an idempotent upsert keyed on `lower(host)` that only converges into an existing row still `deletion_state = 'active'` and `deleted_at IS NULL` (a permanently tombstoned host is rejected as `AccessDenied` rather than silently resurrected), and separately calls `Db::bootstrap_owner` if `initial_owner_pubkey` was supplied — which upserts that pubkey as `owner` in `relay_members` and demotes any other existing owner row for that community to `admin`, without checking the per-owner community limit at all, because this path is deployment-root authority (startup seeding, operator convergence), not the end-user create path the limit exists to bound."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:318-334"
      - "crates/buzz-db/src/store/community.rs:277-310"
      - "crates/buzz-db/src/store/relay_members.rs:343-381"
  - statement: "The same `ensure_configured_community` function seeds the relay's own deployment community at process startup, before any relay-membership backfill or owner bootstrap runs, from a host derived by normalizing `BUZZ_RELAY_URL`'s authority (`relay_url_authority` then `normalize_host` — the same normalization request-time host resolution uses); an empty derived host is a fatal misconfiguration only when `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true`, otherwise it is logged and membership backfill/bootstrap is skipped non-fatally."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:254-297"
  - statement: "`communities` is a single Postgres table (`id UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `host VARCHAR(255) NOT NULL`, optional `signing_key BYTEA`, `created_at`) with a `UNIQUE INDEX` on `lower(host)` as a database-level backstop on top of the application-level `normalize_host` rule, so no two differently-cased or differently-ported spellings of the same host can ever become two tenant rows."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:53-61"
  - statement: "On successful creation or owner bootstrap, and only when the deployment has `require_relay_membership` enabled, the handler publishes a NIP-43 membership-list snapshot for the new/updated community; publication is best-effort — a publish failure is logged as a warning and does not turn an already-committed database success into an HTTP failure, matching every other membership-mutation path in this relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:204-230"
  - statement: "The HTTP wrapper around `provision_community` maps its `Result<_, String>` outcomes onto status codes by matching the error message's own prefix: `actor not authorized` -> 403, `community already exists` or a `limit_reached:`-prefixed message -> 409, a `failed to create community:`/`community provisioned but owner bootstrap failed:`-prefixed message -> a sanitized 500 (the underlying error is logged server-side but never echoed to the client), and anything else -> 400."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:149-193"
  - statement: "Every `POST /operator/communities` request is authenticated by a NIP-98 signature verified against the deployment's configured `RELAY_OPERATOR_API_ORIGIN` (no dev-mode `X-Pubkey` header fallback is accepted on this surface), then checked for replay via a scoped in-memory replay guard keyed by the signed event id, and only then checked against the `RELAY_OPERATOR_PUBKEYS` allowlist; an empty allowlist (the default) makes every requester fail the authorization check, so provisioning is disabled by default rather than open by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:55-135"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:249-266"
  - statement: "The operator gate is deliberately not a `relay_members` lookup the way every other admin surface on this relay is: creating a community brings tenancy itself into existence, so the authorizing identity has to sit above any one tenant, and the code comment on `community_provisioning.rs` states this explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:1-16"
  - statement: "`buzz-cli` (the agent-facing CLI) has a `moderation` command group scoped to an existing community selected via `--relay`/`BUZZ_RELAY_URL` (bans, timeouts, the report queue, audit trail), but no subcommand for creating or provisioning a community; a case-insensitive search of `crates/buzz-cli/src/` for `communit` surfaces only the moderation group's own doc comments, never a create/provision command."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:1884-1922"
      - "grep_case_insensitive('communit', path='crates/buzz-cli/src/') -> only moderation.rs and its lib.rs doc comments, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Representative test coverage: `crates/buzz-relay/src/api/operator.rs`'s `happy_path_create_returns_created_and_bootstraps_owner` (create_only path returns `created`, stores the host, and bootstraps the owner's `relay_members` row) and `fresh_host_at_owner_limit_returns_limit_reached_conflict` (the (N+1)th create for an owner at the cap returns 409 `limit_reached:` and leaves no `communities` row for the rejected host) exercise the HTTP handler end to end; `crates/buzz-db/src/lib.rs`'s `create_community_with_owner_is_atomic_and_create_only` and `create_community_with_owner_enforces_per_owner_limit` exercise the same DB function directly, including that a same-owner retry returns the original row and a different-owner collision leaves the original owner's role untouched."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:1043-1109"
      - "crates/buzz-db/src/store/community.rs:712-771"
      - "crates/buzz-db/src/store/community.rs:846-875"
  - statement: "All of the tests cited above carry `#[ignore = \"requires Postgres\"]` and are excluded from a plain `cargo test`/`just test-unit` run; they run only under `just test`, which provisions Postgres and Redis first."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:1041-1042"
      - "crates/buzz-db/src/store/community.rs:710-711"
  - statement: "architecture-deployment-multi-community's own evidence ledger already states that community creation is authorized above the tenant boundary via the NIP-98-authenticated, `RELAY_OPERATOR_PUBKEYS`-gated `POST /operator/communities` endpoint, deliberately outside the Nostr event ingest data plane -- the same endpoint and the same gate this node narrates the internal mechanics of."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/multi-community.md"
  - statement: "architecture-principles-host-selects-community documents `normalize_host` as the one shared host-normalization rule applied on both the write side (the `communities.host` column is stored already-normalized) and the read side (request `Host` header resolution); `validate_host` in the community-creation path is the write-side enforcement point for that same shared rule -- it rejects any host that is not already in `normalize_host`'s own normal form rather than normalizing it for the caller."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:77-100"
relationships:
  - type: references
    target: architecture-deployment-multi-community
  - type: references
    target: architecture-principles-host-selects-community
---

# Community creation

How a new Buzz community (a relay tenant, identified by a normalized host
authority) comes into existence, from a relay operator's provisioning
request through to a durably stored `communities` row with a bootstrapped
initial owner.

## Trigger, preconditions, and termination

**Trigger.** A relay operator sends `POST /operator/communities` with a JSON
body `{ "host": "<normalized authority>", "initial_owner_pubkey": "<hex>",
"create_only": true }`, handled by `provision_community` in
`crates/buzz-relay/src/api/operator.rs`, which delegates the actual
create-or-converge decision to `crate::handlers::community_provisioning::provision_community`.
A second, non-HTTP trigger exists: the relay process itself calls the same
underlying `ensure_configured_community` function once at startup, to seed
its own deployment community from `BUZZ_RELAY_URL`.

**Preconditions.**

- The request must carry a valid NIP-98 signature verified against the
  deployment's configured `RELAY_OPERATOR_API_ORIGIN`, must not be a replay of
  a previously seen signed event, and the signer's pubkey must appear in the
  deployment-level `RELAY_OPERATOR_PUBKEYS` allowlist. An empty allowlist (the
  default) rejects every request.
- `host` must already be in normalized, canonical-authority form: non-empty,
  ≤255 bytes, free of scheme/path/query/userinfo/control characters, and
  byte-identical to its own `normalize_host` + authority-parse round-trip.
- When `create_only: true`, `initial_owner_pubkey` is required and must be a
  64-character hex string.
- There is no agent-facing path to this trigger: `buzz-cli`'s community
  commands are scoped to moderating an *existing* community and carry no
  create/provision subcommand.

**Termination and outcome.** The call terminates in exactly one of:

1. **Created** — a new `communities` row was inserted (`create_only` path),
   or the legacy convergence path inserted or matched an existing row;
   `status: "created"` (or, on the legacy path re-hitting an existing row,
   `status: "existed"`). When an owner was requested, that owner now holds
   `role = 'owner'` in `relay_members` for this community.
2. **Host exists** (`create_only` only) — the host already belongs to a
   different owner (or to no active owner match); rejected `409` with
   `"community already exists"`. No owner row is touched.
3. **Limit reached** (`create_only` only) — the intended owner already owns
   `max_communities_per_owner()` communities (default 5); rejected `409`
   `limit_reached:`. The new host's own row insert is rolled back with it —
   the transaction never commits a host with no valid owner.
4. **Rejected** — a validation failure (bad host shape, malformed pubkey,
   `create_only` without an owner); `400`.
5. **Internal error** — a genuine database failure; `500`, sanitized so no
   underlying `DbError` detail reaches the client.

## Ordered interactions and data/state movement

**`create_only: true` path** (the atomic create-with-owner path, intended for
end-user-facing provisioning):

1. **Operator authorization.** `authorize_operator_request` verifies the NIP-98
   signature against `RELAY_OPERATOR_API_ORIGIN`, checks replay via a scoped
   in-memory guard keyed on the signed event id, then checks the signer
   against `RELAY_OPERATOR_PUBKEYS`. (`crates/buzz-relay/src/api/operator.rs:55-135`)
2. **Input validation.** `validate_host` and `validate_pubkey_hex` reject a
   malformed host or owner pubkey before any database call.
   (`crates/buzz-relay/src/handlers/community_provisioning.rs:77-171,268-278`)
3. **Transaction begins; advisory lock taken.** `create_community_with_owner`
   opens a Postgres transaction and takes `pg_advisory_xact_lock`, keyed by an
   FNV-1a hash of the owner pubkey, so two concurrent creates for the same
   intended owner serialize against each other.
   (`crates/buzz-db/src/lib.rs:1490-1503`, `crates/buzz-db/src/relay_members.rs:437-449`)
4. **Host row insert, `ON CONFLICT DO NOTHING`.** If a new `communities` row
   is inserted, proceed to step 5. If not (the host already exists), the
   transaction instead looks up whether the *same* owner already owns that
   exact host (an idempotent retry) — if so, returns the existing row as
   `Created`; otherwise rolls back and returns `HostExists`.
   (`crates/buzz-db/src/lib.rs:1505-1565`)
5. **Owner-limit check.** With a new host row in hand, count the intended
   owner's existing `role = 'owner'` rows in `relay_members`. If at or over
   the effective limit, roll back the whole transaction (the new host row is
   discarded too) and return `LimitReached`.
   (`crates/buzz-db/src/lib.rs:1521-1532`, `crates/buzz-db/src/relay_members.rs:403-423`)
6. **Owner row insert; commit.** Insert the owner's `relay_members` row
   (`role = 'owner'`), then commit the transaction — host row and owner row
   land together or not at all.
   (`crates/buzz-db/src/lib.rs:1534-1567`)
7. **Best-effort NIP-43 publication.** If `require_relay_membership` is
   enabled, publish a membership-list snapshot for the new community;
   failure only logs a warning.
   (`crates/buzz-relay/src/handlers/community_provisioning.rs:204-230,309`)
8. **Response.** The handler returns `community_id`, `host`, `status:
   "created"`, and the echoed `owner_pubkey`.
   (`crates/buzz-relay/src/handlers/community_provisioning.rs:290-315`)

**Legacy convergence path** (`create_only` absent/false — deployment startup
seeding and operator convergence):

1. Steps 1-2 above run identically (authorization, host validation; owner
   pubkey validation only if supplied).
2. **`ensure_configured_community`.** An `INSERT ... ON CONFLICT (lower(host))
   DO UPDATE ... WHERE deletion_state = 'active' AND deleted_at IS NULL`
   converges the host row idempotently; a permanently tombstoned host (the
   `WHERE` guard excludes it, so the conflicting row is never touched) fails
   the whole call with `AccessDenied` rather than resurrecting it.
   (`crates/buzz-db/src/store/community.rs:277-310`)
3. **`bootstrap_owner`, if an owner was supplied.** Upserts that pubkey as
   `role = 'owner'` and demotes any *other* existing owner row for this
   community to `admin` — no per-owner limit is enforced on this path.
   (`crates/buzz-db/src/relay_members.rs:347-378`)
4. Best-effort NIP-43 publication and response, as in the `create_only` path
   above (`status` is `"existed"` when the host row was not newly inserted).

**Startup seeding trigger.** At relay process startup, `ensure_configured_community`
is called directly (bypassing the HTTP operator surface entirely) with the
host derived from `BUZZ_RELAY_URL`, before any relay-membership backfill or
owner bootstrap runs, so that deployment-root operations land in the correct
tenant from the first startup onward.
(`crates/buzz-relay/src/main.rs:254-297`)

## Authentication/authorization/trust-boundary crossings

- **Operator authority spans tenants, so it cannot be a `relay_members`
  lookup.** Every other admin action on this relay checks the sender's role
  in `relay_members` for one host-resolved tenant; community *creation*
  brings tenancy itself into existence, so its authorizing identity is the
  deployment-level `RELAY_OPERATOR_PUBKEYS` allowlist instead — an identity
  that sits above any one community.
  (`crates/buzz-relay/src/handlers/community_provisioning.rs:1-16`)
- **Fail-closed by default.** An empty `RELAY_OPERATOR_PUBKEYS` allowlist (the
  default) means every request fails the authorization check — provisioning
  is off by default, not merely unauthenticated by default.
  (`crates/buzz-relay/src/api/operator.rs:89-99`)
- **No dev-mode bypass on this surface.** Unlike some other HTTP bridges in
  this relay, the operator NIP-98 check accepts no `X-Pubkey` development
  fallback.
  (`crates/buzz-relay/src/api/operator.rs:78-85`)
- **Replay protection is scoped separately from ordinary NIP-98 use.**
  A dedicated `operator-management` replay scope, keyed by the signed
  event's id, guards this surface independently of any other NIP-98 replay
  tracking in the relay.
  (`crates/buzz-relay/src/api/operator.rs:55,104-135`)
- **The database's write-fence/tenant-scoping machinery used for ordinary
  event ingestion (community write fence, channel scoping, moderation
  checks) does not apply here at all** — creation runs entirely outside the
  Nostr event ingest data plane described by `architecture-flows-event-ingestion`,
  as this node's own front-matter evidence and `architecture-deployment-multi-community`
  both state.
- **Owner authority is granted, not asserted by the caller.** The caller
  supplies a bare pubkey string for `initial_owner_pubkey`; nothing about the
  request itself proves that pubkey's holder consented. Trust here rests
  entirely on the operator's own authorization, not on any signature from the
  intended owner.

## Failure, abort, and rollback behavior

- **Any authorization or validation failure leaves no trace.** A rejected
  NIP-98 signature, a replay hit, a non-allowlisted operator, or a malformed
  host/pubkey all return before any database call runs; no `communities` or
  `relay_members` row is touched.
- **The `create_only` path is one atomic transaction.** Advisory lock, host
  insert, owner-count check, and owner insert all happen inside one Postgres
  transaction (`pool.begin()` / commit). A `LimitReached` result rolls back
  the *whole* transaction, including the host row that had just been
  inserted — the database never durably holds a community with no valid
  owner as a side effect of a rejected create.
  (`crates/buzz-db/src/lib.rs:1496-1567`)
- **A host collision is a clean rejection, not a partial write.** When the
  host row already exists for a different owner, the transaction is rolled
  back before any owner-role check or insert runs.
  (`crates/buzz-db/src/lib.rs:1560-1565`)
- **The legacy convergence path has no owner-limit rollback, by design.**
  `ensure_configured_community` and `bootstrap_owner` are separate calls, not
  one transaction; if `ensure_configured_community` succeeds and the
  subsequent `bootstrap_owner` call fails, the handler returns a
  `"community provisioned but owner bootstrap failed"` error while the
  community row itself remains created — a partial outcome the response
  mapping surfaces as a sanitized `500`, and a caller must retry the same
  request (idempotent on both calls) to converge rather than assume the
  whole operation rolled back.
  (`crates/buzz-relay/src/handlers/community_provisioning.rs:318-334`,
  `crates/buzz-relay/src/api/operator.rs:184-190`)
- **NIP-43 publication failure never rolls back a committed creation.** By
  the time the best-effort publish step runs, the `communities`/`relay_members`
  writes have already committed; a publish failure is logged and the HTTP
  response still reports success.
  (`crates/buzz-relay/src/handlers/community_provisioning.rs:210-230`)
- **A genuine database error is sanitized before it reaches the client.**
  Whatever the underlying `DbError` says, the client only ever sees the fixed
  string implied by the `500` mapping; the real error is logged
  server-side only.
  (`crates/buzz-relay/src/api/operator.rs:184-190`)
- **Representative verification.** `happy_path_create_returns_created_and_bootstraps_owner`
  and `fresh_host_at_owner_limit_returns_limit_reached_conflict` exercise the
  HTTP-level create-only path (success and limit-rejection respectively);
  `create_community_with_owner_is_atomic_and_create_only` and
  `create_community_with_owner_enforces_per_owner_limit` exercise the same
  atomicity and limit-enforcement at the `Db` layer directly. All four
  require Postgres and are excluded from a plain unit-test run.

## Boundary

This node does not describe:
- The standing multi-tenant deployment structure a created community becomes
  part of (host resolution at request time, the `communities` table's role
  in that resolution beyond its own schema) — see
  `architecture-deployment-multi-community` and
  `architecture-principles-host-selects-community`.
- What a relay operator can do with a community once it exists (archive,
  unarchive, transfer ownership, list) — these are separate handlers
  (`archive_community`, `unarchive_community`, `transfer_community`,
  `list_owned_communities`) in the same `operator.rs` file, not narrated here.
- The Nostr event ingestion pipeline (`architecture-flows-event-ingestion`)
  that runs once a community exists and is write-serving — community
  creation happens entirely outside that pipeline.
- The full NIP-43 membership-list wire format or the workflow-engine/side-effect
  machinery `handle_side_effects` runs for other event kinds.
- Any human-facing operator tooling or runbook for actually invoking this
  endpoint in production (credential handling, `kgoose` or other operator
  clients) — this node covers the relay-side mechanics only.

## Relationships

- references: architecture-deployment-multi-community
- references: architecture-principles-host-selects-community

## Scope and omissions

**This node covers** the `POST /operator/communities` create-only and legacy
convergence paths, the startup seeding call to the same underlying function,
the operator authorization/authentication gate, the atomicity and per-owner
limit enforced inside `create_community_with_owner`, the non-atomic
convergence-then-bootstrap shape of the legacy path, the best-effort NIP-43
publication side effect, and the HTTP-level outcome/status-code mapping.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The standing multi-tenant/host-resolution structure a community participates in once created | `architecture-deployment-multi-community`, `architecture-principles-host-selects-community` |
| Archiving, unarchiving, and ownership transfer of an existing community | not yet a corpus node (see `crates/buzz-relay/src/api/operator.rs`'s `archive_community`/`unarchive_community`/`transfer_community`) |
| The Nostr event ingestion pipeline that runs once a community is write-serving | `architecture-flows-event-ingestion` |
| The NIP-43 membership-list wire format itself | not yet a corpus node |
| Operator-side tooling/runbooks for invoking this endpoint in a real deployment | not yet a corpus node |

**Expected but not verified when this node was written:**
- **Whether every downstream side effect of a newly created community (cache
  warmup, metrics, any provisioning webhook) is captured above.** This node
  follows the code path through the database commit and the NIP-43
  publication step only; it does not claim these are the only observable
  effects of a successful create.
- **The `kgoose` client mentioned in `community_provisioning.rs`'s own doc
  comment (the availability-check consumer) was not independently located or
  read** — its existence and behavior are taken from that doc comment, not
  from opening its source.
- **Concurrent-request behavior beyond the single advisory-lock scenario
  documented in code comments** (same owner, two simultaneous creates) was
  read from the source and its own tests, not independently re-verified
  under load.
