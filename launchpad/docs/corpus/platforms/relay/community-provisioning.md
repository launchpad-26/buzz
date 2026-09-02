---
id: platforms-relay-community-provisioning
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum includes platforms, and at the recorded revision no template file matching platforms-*.md exists under launchpad/docs/corpus/templates/; templates/component.md is the closest fit by section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) but its own front matter prescribes type: implementation for a node built from it, not type: platforms. This node follows this Feature's own settled batch convention of type: platforms for platforms/** documents, borrowing component.md's section shape rather than inventing a new one."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
      - "ls_templates_dir(launchpad/docs/corpus/templates/) -> architecture-component.md, architecture-container.md, architecture-context.md, capability.md, component.md, concept.md, configuration.md, data-entity.md, datastore.md, decision-reference.md, deployment.md, event-kind.md, flow.md, generated-index.md, glossary-term.md, implementation-reference.md, interface.md, invariant.md, policy.md, procedure.md, reference.md, runbook.md, specification.md, test-contract.md, test-strategy.md, threat-model.md -- no platforms-*.md present, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
    confidence: 0.75
  - statement: "Two merged corpus nodes already cover ground adjacent to community provisioning without documenting the handler-level contract this node covers: architecture-principles-host-selects-community documents the row-zero host-resolution invariant (which community a request belongs to), and architecture-deployment-multi-community documents deployment topology and summarizes community creation as one bullet (operator-gated, NIP-98, RELAY_OPERATOR_PUBKEYS) without detailing the two distinct code paths, their request/response contracts, or the buzz-db functions backing them."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
      - "launchpad/docs/corpus/architecture/deployment/multi-community.md"
    confidence: 0.85
  - statement: "crates/buzz-relay/src/handlers/community_provisioning.rs's module doc comment states that community creation cannot be authorized the way every other admin surface is (a relay_members role lookup scoped to a resolved tenant), because its effect is the creation of tenancy itself; the gate is instead the deployment-level RELAY_OPERATOR_PUBKEYS allowlist, checked before any tenant is resolved, and an empty allowlist (the default) disables provisioning entirely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:1-16"
  - statement: "The public surface POST /operator/communities takes a JSON body { host: String, initial_owner_pubkey: Option<String>, create_only: bool } (ProvisionCommunityRequest) and returns { community_id, host, status: \"created\"|\"existed\", owner_pubkey: Option<String> } (ProvisionCommunityResponse); create_only and initial_owner_pubkey both default to their type's Default via #[serde(default)] when omitted from the request body."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:41-69"
  - statement: "validate_host requires the caller to submit an already-normalized authority: it rejects an empty host, a host over 255 bytes (matching the communities.host VARCHAR(255) column), and any value for which normalize_host would produce a different string (catching uppercase, a trailing FQDN-root dot, and a default port of 80/443), then further rejects control/whitespace characters, a scheme/path/query/userinfo component, and any authority that does not round-trip byte-identically through URL-authority parsing (catching malformed IPv6 bracket literals, invalid domain labels, and out-of-range ports)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:77-171"
      - "migrations/0001_initial_schema.sql:53-59"
  - statement: "A separate function, normalize_candidate_host, is used only by the read-only availability-check endpoint and is deliberately more permissive than validate_host: it accepts a non-canonical but normalizable authority (uppercase, trailing dot, default port) and returns the canonical normalized form, so a client can ask the relay what host string create would accept before submitting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:173-202"
  - statement: "provision_community (the handler-support function, not the axum handler of the same name) implements two distinct modes selected by the request's create_only flag. In create_only mode, initial_owner_pubkey is required, and the community and its owner are created atomically via buzz_db::Db::create_community_with_owner, which returns Created, HostExists (the host already belongs to another owner), or LimitReached (the intended owner already owns the maximum number of communities) -- an existing host is always rejected outright, never converged or owner-rotated. In the default (non-create_only) 'legacy convergence' mode, the host is idempotently ensured via ensure_configured_community, and if initial_owner_pubkey is present it is (re)bootstrapped via bootstrap_owner even for an already-existing community, which can rotate an existing owner -- the function's own doc comment states this makes the operator allowlist deployment-root authority, not create-only authority."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:232-351"
  - statement: "buzz_db::Db::create_community_with_owner runs in a single transaction: it takes a per-owner-pubkey Postgres advisory lock before counting that owner's existing owned communities, so two concurrent creates for the same owner cannot both pass the per-owner limit check; a fresh host is inserted (ON CONFLICT DO NOTHING), the owner-count limit is enforced before the relay_members owner row is inserted (rolling back and returning LimitReached if the limit is met), and a host collision with a different owner returns HostExists without mutating anything; a retried request from the same host+owner pair re-reads and returns the original row rather than erroring."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/community.rs:317-405"
  - statement: "buzz_db::Db::ensure_configured_community performs an idempotent INSERT ... ON CONFLICT (lower(host)) DO UPDATE SET host = communities.host, gated by a WHERE clause that only matches an active, non-deleted row, and reports whether this call was the one that inserted the row via (xmax = 0) AS created; a host whose row has been fully tombstoned (deletion_state or deleted_at outside 'active') causes the query to match no row at all, and the function surfaces that as an AccessDenied error naming the host as permanently tombstoned rather than silently reactivating it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/community.rs:272-310"
  - statement: "buzz_db::bootstrap_owner (the free function backing Db::bootstrap_owner) upserts the given pubkey as 'owner' for the given community_id and, in the same transaction, demotes any other current owner of that community to 'admin'; its doc comment states explicitly that, unlike create_community_with_owner and transfer_ownership, it does NOT enforce MAX_COMMUNITIES_PER_OWNER and does NOT take the per-owner advisory lock, because it is a deployment-root-authority path (startup initialization and the legacy convergence mode of the operator endpoint), not an end-user path."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_members.rs:335-381"
  - statement: "MAX_COMMUNITIES_PER_OWNER is a constant set to 5, and relay_members::max_communities_per_owner() reads BUZZ_MAX_COMMUNITIES_PER_OWNER once per process (caching the result) to let a deployment override that default rather than hardcoding it permanently."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/relay_members.rs:409-434"
  - statement: "The axum handler POST /operator/communities (crate::api::operator::provision_community, distinct from the same-named function in handlers/community_provisioning.rs) authenticates the caller via authorize_operator_request before doing anything else, then maps the handler-support function's Err(String) variants to specific HTTP statuses: an 'actor not authorized' prefix maps to 403 Forbidden, 'community already exists' or a 'limit_reached:' prefix maps to 409 Conflict, a 'failed to create community:' or 'community provisioned but owner bootstrap failed:' prefix is logged as an internal error and returned as a generic 500 (not echoing the underlying DB error text to the caller), and any other error string falls through to 400 Bad Request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:137-193"
  - statement: "authorize_operator_request (shared by every /operator/communities* route) requires RELAY_OPERATOR_API_ORIGIN to be configured server-side, builds the NIP-98-signed URL from that fixed canonical origin plus the literal request path (never the inbound Host header), verifies the NIP-98 signature and a replay guard scoped to 'operator-management' with a fail-closed error if the replay check itself is unavailable, and only then checks the signer's pubkey against RELAY_OPERATOR_PUBKEYS."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:55-135"
  - statement: "GET /operator/communities/availability is read-only: it authenticates the same way as create, normalizes the candidate host via normalize_candidate_host, looks up whether a community already exists at that host via lookup_community_by_host_for_management (which, unlike lookup_community_by_host, matches regardless of archived/deletion lifecycle state), and returns { host, normalized_host, available, community_id } without creating or mutating anything."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:466-498"
  - statement: "The five /operator/communities* routes (POST /operator/communities for create, GET for list-owned, /archive, /unarchive, /availability, /transfer) are registered in the relay's router alongside the NIP-98-authenticated Nostr HTTP bridge routes, distinct from the WebSocket/event-ingest route group."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:85-105"
  - statement: "RELAY_OPERATOR_PUBKEYS is parsed as a comma-separated list of 64-char-hex pubkeys; an entry that is not valid hex of that length is a hard config-parse error at startup (unlike RELAY_OWNER_PUBKEY, whose own comment says an invalid value is only warned-and-ignored), and duplicate entries are silently deduplicated. If the allowlist is non-empty but RELAY_OPERATOR_API_ORIGIN is unset, startup does not fail closed -- it only logs a warning -- because the same allowlist also gates a separate NIP-98 admin console that does not need the origin; the provisioning endpoints themselves still fail closed at request time in that case, inside authorize_operator_request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:744-790"
  - statement: "At relay startup, ensure_configured_community is called with the host derived from the deployment's own configured relay_url (via relay_url_authority, which applies the same normalize_host rule used by request-time host resolution), before any pubkey_allowlist backfill or bootstrap_owner call, so the deployment's own single-tenant community is seeded from configuration rather than from an operator API call; an empty/unparseable relay_url authority is a fatal startup error when BUZZ_REQUIRE_RELAY_MEMBERSHIP is true, and only a logged non-fatal skip otherwise. This is the N=1 single-tenant provisioning path, distinct from and independent of the POST /operator/communities multi-tenant path documented above."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:266-355"
  - statement: "publish_membership_snapshot_if_required runs after a successful create or owner bootstrap in either provisioning mode; it is a no-op unless config.require_relay_membership is set, and on failure it only logs a warning naming the community and host rather than turning the already-committed provisioning success into an HTTP error -- the function's own comment states this deliberately matches every other membership-mutation path's best-effort publication semantics."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:204-230"
  - statement: "The communities table (migrations/0001_initial_schema.sql) has exactly four columns at creation -- id UUID PRIMARY KEY, host VARCHAR(255) NOT NULL, signing_key BYTEA (nullable), created_at TIMESTAMPTZ -- plus a CHECK constraint forbidding the nil UUID and a UNIQUE INDEX on lower(host); no channel, membership, or configuration row is created by this table definition itself."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:53-61"
  - statement: "Neither buzz_db::Db::create_community_with_owner nor buzz_db::Db::ensure_configured_community nor buzz_db::bootstrap_owner inserts a row into channels or any other community-scoped table beyond communities and relay_members; a community is provisioned with zero channels, and any initial channel a deployment wants must be created through a separate, later call to whatever creates a channels row, not as part of provisioning."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/community.rs:272-405"
      - "crates/buzz-db/src/store/relay_members.rs:350-381"
  - statement: "Issue #1266's Definition of Done requires this node to state responsibility and a well-defined interface/boundary, name dependencies and collaborators, link source implementation and tests, and explain only component-level behavior rather than the entire containing platform."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1266 definition of done"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-deployment-multi-community
---

# Relay community provisioning

How a Buzz relay deployment brings a new community (tenant) into existence:
the operator-gated HTTP surface used for multi-tenant provisioning, the
startup-time seeding path used for a single-tenant (N=1) deployment, the
`buzz-db` functions both call, and the request/response contract a caller of
either path can rely on. This node answers "how does a community get
created and how does its first owner get set," not "how is a request
resolved into an existing community" (see *Relationships*) or "what does the
deployment topology around the relay look like" (see *Relationships*).

## Responsibility

`crates/buzz-relay/src/handlers/community_provisioning.rs`'s own module doc
comment states the core design constraint directly: every other admin
surface in the relay authorizes an action by looking up the caller's role in
`relay_members (community_id, pubkey)` for an already-resolved tenant, but
community *creation* cannot work that way, because its effect is the
creation of tenancy itself — there is no tenant yet to scope a role lookup
to. The authorizing identity therefore sits above tenants entirely: the
deployment-level `RELAY_OPERATOR_PUBKEYS` allowlist, empty (provisioning
disabled) by default. This module owns request validation and the two
provisioning code paths (atomic create-only, and idempotent legacy
convergence); it delegates persistence to `buzz-db` and HTTP framing/auth to
`crate::api::operator`.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `POST /operator/communities` | HTTP route | Body `{host, initial_owner_pubkey?, create_only?}` → `{community_id, host, status: "created"\|"existed", owner_pubkey?}`. NIP-98-signed against `RELAY_OPERATOR_API_ORIGIN`, caller pubkey must be in `RELAY_OPERATOR_PUBKEYS`. | `crates/buzz-relay/src/router.rs:85-89`, `crates/buzz-relay/src/api/operator.rs:137-193` |
| `GET /operator/communities/availability?host=` | HTTP route | Read-only; returns `{host, normalized_host, available, community_id?}`. Same auth as create. | `crates/buzz-relay/src/api/operator.rs:466-498` |
| `fn provision_community` | async fn | Validates the request, then dispatches to create-only or legacy-convergence persistence; returns `Result<ProvisionCommunityResponse, String>` with string error prefixes the HTTP handler pattern-matches to a status code. | `crates/buzz-relay/src/handlers/community_provisioning.rs:249-351` |
| `fn validate_host` / `fn normalize_candidate_host` | fn | Strict (create) vs. permissive-then-canonicalizing (availability) authority validation. | `crates/buzz-relay/src/handlers/community_provisioning.rs:77-202` |
| `Db::create_community_with_owner` | async fn (buzz-db) | Atomic create-only path: `Created`/`HostExists`/`LimitReached`. | `crates/buzz-db/src/store/community.rs:317-405` |
| `Db::ensure_configured_community` | async fn (buzz-db) | Idempotent ensure, used by both the legacy-convergence operator path and relay startup seeding. | `crates/buzz-db/src/store/community.rs:272-310` |
| `Db::bootstrap_owner` | async fn (buzz-db) | Upserts an owner and demotes any other current owner; deployment-root authority, no per-owner limit. | `crates/buzz-db/src/store/relay_members.rs:335-381` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-db` (`Db::create_community_with_owner`, `Db::ensure_configured_community`, `Db::bootstrap_owner`) | Persists the `communities` and `relay_members` rows this module validates requests for. | `crates/buzz-db/src/store/community.rs`, `crates/buzz-db/src/store/relay_members.rs` |
| `buzz-core` (`normalize_host`, `TenantContext`) | Shared host-normalization rule and the tenant-context type used to publish the post-provisioning membership snapshot. | `crates/buzz-relay/src/handlers/community_provisioning.rs:33` |
| NIP-98 request signing + replay guard (`crate::api::bridge::verify_bridge_auth_with_options`, `state.nip98_replay`) | Authenticates and replay-protects every `/operator/communities*` request before this module's validation runs. | `crates/buzz-relay/src/api/operator.rs:60-102` |
| Deployment config (`RELAY_OPERATOR_PUBKEYS`, `RELAY_OPERATOR_API_ORIGIN`, `RELAY_OWNER_PUBKEY`, `relay_url`) | Supplies the operator allowlist, the fixed NIP-98 origin, and (for startup seeding) the host the deployment's own community is provisioned under. | `crates/buzz-relay/src/config.rs:744-790`, `crates/buzz-relay/src/main.rs:266-355` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/api/operator.rs` (the axum handlers) | Calls `handlers::community_provisioning::provision_community` and its validation helpers directly to implement the HTTP routes. | `crates/buzz-relay/src/api/operator.rs:20-22, 171` |
| `crates/buzz-relay/src/main.rs` (startup) | Calls `Db::ensure_configured_community` and `Db::bootstrap_owner` directly for N=1 deployment seeding, independent of the operator HTTP surface. | `crates/buzz-relay/src/main.rs:293, 340` |

No other module in this checkout was found calling
`handlers::community_provisioning::provision_community` itself (the
grep-based search in *Evidence expectations* below covers only this
checkout's call sites, not any external caller).

## Boundary

This node does not describe:
- **Which community a request resolves to, or why an unmapped host fails
  closed** — that is the row-zero invariant, owned by
  `architecture-principles-host-selects-community`. This node assumes that
  invariant and documents only how a `communities` row and its first owner
  come to exist in the first place.
- **The relay's deployment topology, execution nodes, or Kubernetes/Helm
  shape** — owned by `architecture-deployment-multi-community`, which also
  covers community archival (`migrations/0016_community_archival.sql`) and
  whole-community deletion (`migrations/0029_community_deletion.sql`) in
  more depth than the one-bullet mention this node needed to distinguish
  from provisioning.
- **Any channel, message, or other community-scoped content model.**
  Provisioning creates a `communities` row and, optionally, one
  `relay_members` owner row — nothing else. See the `channels`-table FACT
  above; this is a verified absence, not an omission.
- **Community archival, unarchival, or transfer** (`/operator/communities/archive`,
  `/unarchive`, `/transfer`) — these are lifecycle operations on an
  *existing* community, not provisioning, and are out of this node's scope.
- **Install/usage instructions for a human running the relay** — no
  crate-level README exists for `buzz-relay` to link here (per
  `templates/component.md`'s own audit, only 6 of 30 crates have one, and
  `buzz-relay` is not among them).

## Relationships

- `references`: `architecture-principles-host-selects-community` — this
  node's every provisioning path terminates in a `communities` row that the
  row-zero invariant later resolves requests against; this node does not
  restate that invariant.
- `references`: `architecture-deployment-multi-community` — that node
  already names `community_provisioning.rs` as the operator-gated creation
  surface at the deployment-topology level; this node is the detailed,
  handler-level companion it points to without duplicating.
- No `part-of` relationship is declared. `templates/architecture-component.md`
  (the C4-component decomposition template) is unmerged at the recorded
  revision, and no `architecture/components/*.md` node exists in the corpus
  to decompose the relay container into building blocks this node could sit
  under.

## Scope and omissions

**This node covers** the two ways a Buzz relay community comes into
existence — the NIP-98-gated, deployment-root-authorized
`POST /operator/communities` HTTP surface (both its atomic create-only and
idempotent legacy-convergence modes) and the startup-time N=1 seeding path —
their request/response contracts, the validation rules for an acceptable
host authority, the `buzz-db` functions both call, the owner-bootstrap
semantics (including the deliberate exception where `bootstrap_owner` can
rotate an existing owner), and the verified fact that provisioning creates
no channel or other community-scoped content.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Which community an already-provisioned request resolves to, and why an unmapped host fails closed | `architecture-principles-host-selects-community` |
| Deployment topology, execution nodes, Kubernetes/Helm shape | `architecture-deployment-multi-community` |
| Community archival, unarchival, transfer, and whole-community deletion | `architecture-deployment-multi-community` (topology-level); no handler-level node exists yet for these lifecycle operations specifically |
| The channel/message data model | Not yet a corpus node at the recorded revision |
| The NIP-98 signing/replay-verification mechanism itself (`verify_bridge_auth_with_options`) | Not yet a corpus node at the recorded revision; only this module's use of it is described here |
| Per-type corpus template conformance for `type: platforms` | No `platforms`-specific template exists yet in the merged corpus; this node borrows `component.md`'s section shape per the batch convention recorded in this node's own `INFERENCE` evidence above, and expects a later reshaping task once a dedicated template lands |

**Expected but not verified when this node was written:**

- Whether any code outside this checkout (a private downstream repo) calls
  `handlers::community_provisioning::provision_community` or the
  `/operator/communities` HTTP route was not checked — only this checkout's
  call sites were searched.
- Whether an end-to-end integration test exercises the full HTTP path
  (NIP-98 signing → route → handler → `buzz-db`) for the create-only mode
  specifically, versus the unit tests inside
  `crates/buzz-relay/src/handlers/community_provisioning.rs`'s own
  `#[cfg(test)] mod tests` (which cover `validate_host` and
  `normalize_candidate_host` only) and the `#[ignore = "requires Postgres"]`
  tests inside `crates/buzz-db/src/store/community.rs` (which cover
  `create_community_with_owner` and `ensure_configured_community` directly
  against a database but not through the HTTP layer), was not independently
  re-run — their presence was confirmed by reading the files, not by
  executing them against a live Postgres in this task.
