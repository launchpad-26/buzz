---
id: platforms-relay-operator-api
type: platforms
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum includes platforms as one of PRD #602's named in-scope corpus surfaces, and no platforms-specific template exists in launchpad/docs/corpus/templates/ at the recorded revision; this node instead borrows templates/component.md's section shape (responsibility, public interface, dependencies, boundary, relationships, scope and omissions), following the same convention sibling platforms/relay/** tasks in this Feature have already adopted."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.75
  - statement: "launchpad/docs/corpus/architecture/context/relay-operator.md documents the relay-operator role at context level (actors, two deployment paths, a context diagram) and explicitly defers buzz-admin's command handling and the relay's own internal request routing to 'a future container/component-level node' in its own Scope and omissions table, rather than describing the operator HTTP surface itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/relay-operator.md"
  - statement: "crates/buzz-relay/src/api/operator.rs opens with a module doc comment stating these routes are outside the Nostr event data plane: they use NIP-98 request signing and replay protection but do not run through event ingest, relay membership, channel scoping, storage, or fan-out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "crates/buzz-relay/src/router.rs wires exactly five operator routes: GET and POST /operator/communities (list_owned_communities, provision_community), POST /operator/communities/archive (archive_community), POST /operator/communities/unarchive (unarchive_community), GET /operator/communities/availability (community_availability), and POST /operator/communities/transfer (transfer_community)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "authorize_operator_request rejects every request when config.relay_operator_api_origin is unset (internal_error), otherwise verifies NIP-98 via bridge::verify_bridge_auth_with_options against a URL built from that configured origin plus the request path and query string -- never the inbound HTTP Host header -- with require_auth_token hardcoded true (no X-Pubkey dev fallback, unlike the tenant-scoped bridge auth other endpoints accept) and require_payload set whenever a body is present; it then checks the recovered pubkey against config.relay_operator_pubkeys and returns 403 if absent."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "check_operator_replay marks each verified event id in the fixed scope operator-management via state.nip98_replay.try_mark_in_scope with buzz_auth::DEFAULT_REPLAY_TTL_SECS; a detected replay returns 401, and a replay-guard error (e.g. the backing store being unavailable) also returns 401 rather than allowing the request through, per its own tracing::warn message noting the request is rejected fail-closed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "provision_community (POST /operator/communities) creates a community host and atomically bootstraps its initial owner by delegating to crate::handlers::community_provisioning::provision_community, translating its string error prefixes to HTTP status: 'actor not authorized' to 403, 'community already exists' or 'limit_reached:' to 409, persistence-failure prefixes to a generic 500, and anything else to 400."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "archive_community and unarchive_community (POST /operator/communities/archive and /unarchive) idempotently archive or restore a community that the asserted owner_pubkey currently owns, look the community up by normalized host, and archive_community additionally refuses to archive the deployment's own community host (409 CONFLICT) and best-effort disconnects existing cluster-wide connections after a successful archive, returning 503 with the archived record if that disconnect propagation fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "list_owned_communities (GET /operator/communities) returns every community a given owner_pubkey currently owns; community_availability (GET /operator/communities/availability) reports whether a normalized host is free, returning the relay-canonical normalized_host alongside the raw input host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "transfer_community (POST /operator/communities/transfer) atomically swaps a community's owner at the database layer (guarded by an expected_owner_pubkey compare-and-swap that returns 409 owner_conflict on mismatch, 404 if there is no current owner, and 409 limit_reached if the transferee already owns the maximum communities per owner), demotes the previous owner to the member role rather than admin, and -- only when require_relay_membership is enabled -- best-effort republishes an updated NIP-43 membership snapshot without turning a publication failure into an HTTP error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "config.rs documents relay_operator_pubkeys (env RELAY_OPERATOR_PUBKEYS) as deployment-level pubkeys that 'span tenants' -- unlike relay_owner_pubkey, which is a role within one deployment community, an operator pubkey holds no implicit tenant membership row -- and states the allowlist is empty by default, which disables community provisioning entirely (fail closed). An invalid entry in the comma-separated list is a hard startup ConfigError, not silently skipped."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "config.rs documents relay_operator_api_origin (env RELAY_OPERATOR_API_ORIGIN) as required only to use the community-provisioning endpoints, and states it is deliberately NOT required at boot even when relay_operator_pubkeys is non-empty, because that same allowlist is also shared with the NIP-98 admin console, which needs no origin; when pubkeys are set without an origin, Config::from_env emits a warn! log naming that POST /operator/communities will reject every request until the origin is set, rather than failing the process at boot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "operator.rs's own test module includes provisioning_fails_closed_when_origin_unset_but_pubkeys_set, which asserts that with relay_operator_pubkeys set and relay_operator_api_origin left None, provision_community returns 500 INTERNAL_SERVER_ERROR (not a panic or silent success), corroborating config.rs's documented request-time fail-closed behavior with a runnable check that needs no Postgres connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "crates/buzz-relay/src/api/admin/mod.rs opens with a module doc comment calling itself a 'Private deployment moderation API', mounted separately at /api/admin/v1 only when config.admin is configured, exposing routes for reports and feedback moderation plus /operators roster staffing (list/upsert/delete), gated by AdminConfig's AdminAuth mode: Disabled (read-only, no principal resolved) or Nip98 (mutation and staffing routes require a resolved principal)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs"
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/api/admin/auth.rs's principal-resolution doc comment shows that any pubkey present in RELAY_OPERATOR_PUBKEYS -- the identical allowlist the /operator/* routes authorize against -- is also granted the AdminRole::Operator principal inside the admin API's NIP-98 mode, with config outranking any relay_operators database row for that same pubkey; this grant requires no RELAY_OPERATOR_API_ORIGIN at all and touches only the /api/admin/v1 route set, never the /operator/communities* routes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs"
  - statement: "Because one allowlist (RELAY_OPERATOR_PUBKEYS) grants access to two materially different HTTP surfaces -- the deployment-root community-lifecycle routes this node documents, origin-bound to RELAY_OPERATOR_API_ORIGIN, and the /api/admin/v1 moderation/staffing routes documented by the sibling admin-api node, origin-bound to the admin host in AdminConfig -- a reader must not assume 'operator' names one API; it names one shared identity allowlist reused by two separately routed, separately origin-bound surfaces."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
      - "crates/buzz-relay/src/api/admin/auth.rs"
      - "crates/buzz-relay/src/config.rs"
    confidence: 0.85
  - statement: "Sibling issues launchpad-26/buzz#1261 ('task: document platforms/relay/admin-api.md') and #1266 ('task: document platforms/relay/community-provisioning.md') scope the admin API's own route detail and the community-provisioning algorithm (host normalization, ownership bootstrap, membership snapshot publication) as separate corpus tasks under the same platforms/relay path, so this node deliberately does not re-document either in depth."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1261 and #1266 issue bodies"
  - statement: "crates/buzz-relay/Cargo.toml declares buzz-core, buzz-db, and buzz-auth as workspace dependencies of buzz-relay, and operator.rs's handlers concretely use buzz_core::{CommunityId, TenantContext} for community identity/tenant context, buzz_db::relay_members::TransferResult and the Db methods each handler calls (archive_community_owned_by, unarchive_community_owned_by, list_communities_owned_by, transfer_ownership, lookup_community_by_host_for_management, lookup_community_host), and buzz_auth::DEFAULT_REPLAY_TTL_SECS plus the Nip98ReplayGuard trait for replay protection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-relay/src/api/operator.rs"
---

# Relay operator API

The relay operator API is the deployment-root HTTP surface at `/operator/communities*`
in `buzz-relay`, used by a small, statically configured set of deployment-level
operators to create, look up, archive/unarchive, check the availability of, and
transfer ownership of communities hosted on one relay deployment. This node answers:
what routes exist, how a caller authenticates to them, and how this surface differs
from the deployment's separate admin API, which shares part of its identity allowlist
but is a distinct route surface with a distinct origin binding.

This node is the container/component-level detail that
`architecture-context-relay-operator` names but explicitly defers -- see that node's
own *Scope and omissions* table, which reserves "the relay's own internal request
routing" for a future node.

## Responsibility

`crates/buzz-relay/src/api/operator.rs` implements deployment-global control-plane
operations for community lifecycle, kept deliberately outside the Nostr event data
plane: it does not run through event ingest, relay membership, channel scoping,
storage, or fan-out, per its own module-level doc comment. It answers "does this
deployment have a community at this host, and who owns it" and "make it so" --
create, archive, unarchive, transfer -- for callers a deployment operator has
explicitly allowlisted.

## Public interface

| Route | Method | Handler | Purpose |
|---|---|---|---|
| `/operator/communities` | `GET` | `list_owned_communities` | List every community a given `owner_pubkey` currently owns. |
| `/operator/communities` | `POST` | `provision_community` | Create a community host and atomically bootstrap its initial owner. |
| `/operator/communities/archive` | `POST` | `archive_community` | Idempotently archive a community owned by the asserted `owner_pubkey`; refuses to archive the deployment's own host. |
| `/operator/communities/unarchive` | `POST` | `unarchive_community` | Idempotently restore an archived community owned by the asserted `owner_pubkey`. |
| `/operator/communities/availability` | `GET` | `community_availability` | Report whether a normalized host is free, alongside the relay-canonical `normalized_host`. |
| `/operator/communities/transfer` | `POST` | `transfer_community` | Atomically swap a community's owner (compare-and-swap on `expected_owner_pubkey`), demoting the previous owner to `member`. |

Route wiring: `crates/buzz-relay/src/router.rs`. Handler bodies and request/response
shapes: `crates/buzz-relay/src/api/operator.rs`.

### Authentication and authorization

Every route above shares one auth prelude, `authorize_operator_request`:

1. **Fixed canonical origin, not the inbound `Host` header.** The NIP-98 `u` tag is
   verified against `config.relay_operator_api_origin` (`RELAY_OPERATOR_API_ORIGIN`)
   plus the request path and query -- never the tenant registry or an inbound proxy
   `Host` header. If the origin is unconfigured, every request fails closed with a 500
   before any other check runs.
2. **NIP-98 only, always.** `require_auth_token` is hardcoded `true` for this surface --
   there is no `X-Pubkey` development fallback, unlike some tenant-scoped bridge
   endpoints. A body-bearing request additionally requires the NIP-98 event's `payload`
   sha256 tag.
3. **Static allowlist, not a database role.** The recovered pubkey must appear in
   `config.relay_operator_pubkeys` (`RELAY_OPERATOR_PUBKEYS`), a comma-separated,
   config-time-validated list. There is no per-community or per-tenant grant here --
   membership in this list is deployment-wide.
4. **Replay protection.** Each verified event id is marked in the fixed scope
   `operator-management` via the shared NIP-98 replay guard; a replay, or a
   replay-guard failure, both reject with 401 rather than letting the request through.

`RELAY_OPERATOR_PUBKEYS` defaults to empty, which disables the whole surface (fail
closed); an invalid pubkey entry is a hard startup config error rather than being
silently dropped. `RELAY_OPERATOR_API_ORIGIN` is not required at boot even when the
allowlist is non-empty -- only at request time -- because the same allowlist is shared
with the admin API (see *Boundary* below); `Config::from_env` logs a warning naming
this when it detects the gap.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-core` | `CommunityId` and `TenantContext` identify the community/tenant a request operates on. | `crates/buzz-relay/Cargo.toml`, `crates/buzz-relay/src/api/operator.rs` |
| `buzz-db` | `buzz_db::relay_members::TransferResult` and the `Db` methods each handler calls (`archive_community_owned_by`, `unarchive_community_owned_by`, `list_communities_owned_by`, `transfer_ownership`, `lookup_community_by_host_for_management`, `lookup_community_host`). | `crates/buzz-relay/Cargo.toml`, `crates/buzz-relay/src/api/operator.rs` |
| `buzz-auth` | `DEFAULT_REPLAY_TTL_SECS` and the `Nip98ReplayGuard` trait back the replay check; NIP-98 verification itself is shared with `api::bridge::verify_bridge_auth_with_options`. | `crates/buzz-relay/Cargo.toml`, `crates/buzz-relay/src/api/operator.rs` |
| `crate::handlers::community_provisioning` | `provision_community`'s actual create-and-bootstrap logic, plus host normalization and pubkey-hex validation helpers reused by the archive/unarchive/availability handlers. | `crates/buzz-relay/src/api/operator.rs` |

**Depended on by:**

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/router.rs` | Mounts all five routes directly on the main API router (not behind the separate admin-only sub-router). | `crates/buzz-relay/src/router.rs` |

## Boundary

This node does not describe:

- **The admin API's own route detail** (`/api/admin/v1/*`: reports, feedback,
  `/operators` staffing roster) -- a separate, sibling corpus task
  (`launchpad-26/buzz#1261`) owns that surface. This node only states the one point
  where the two surfaces intersect: a shared `RELAY_OPERATOR_PUBKEYS` allowlist also
  grants an `AdminRole::Operator` principal inside the admin API's NIP-98 mode, with no
  `RELAY_OPERATOR_API_ORIGIN` requirement and no reach into the `/operator/communities*`
  routes. Same identity list, two different doors.
- **Community-provisioning mechanics** -- host normalization rules, the ownership
  bootstrap transaction, and NIP-43 membership-snapshot publication are
  `launchpad-26/buzz#1266`'s scope (`community-provisioning.md`). This node names that
  `provision_community` delegates to `crate::handlers::community_provisioning`, not how
  that module works internally.
- **The relay-operator role at large** -- deployment topology, Compose/Helm operator
  tooling, backup responsibilities, and the two operator paths (self-hosted vs.
  Block-operated) are `architecture-context-relay-operator`'s scope, which this node
  `references` rather than restates.
- **Deployment/runbook instructions** for setting `RELAY_OPERATOR_PUBKEYS` or
  `RELAY_OPERATOR_API_ORIGIN` operationally -- that is deploy-tooling material the
  referenced context node already scopes out too.

## Relationships

- references: architecture-context-relay-operator

## Scope and omissions

**This node covers** the `/operator/communities*` HTTP route surface in `buzz-relay`:
its five routes and handlers, the shared NIP-98 + fixed-origin + static-allowlist +
replay-scope authorization prelude every route runs through, its direct code
dependencies, and the explicit distinction between this surface and the deployment's
separate admin API (which shares the same operator-pubkey allowlist as one of two ways
to obtain an `AdminRole::Operator` grant, but is otherwise a different, separately
origin-bound route surface).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The admin API's own moderation/staffing route detail | `launchpad-26/buzz#1261` (`admin-api.md`), unmerged local branch, not present on `origin/launchpad` at the recorded revision |
| Community-provisioning algorithmic detail | `launchpad-26/buzz#1266` (`community-provisioning.md`) |
| Relay-operator role, deployment topology, and operator tooling at large | `architecture-context-relay-operator` (referenced above) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No `relationships[].target` toward an `admin-api` node was declared**, because
  `launchpad-26/buzz#1261`'s node does not exist on `origin/launchpad` at the recorded
  revision (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` does
  not list it); per `AGENTS.md`'s own rule, a relationship may only target a node
  present on the branch being merged into. Once that sibling merges, a `references`
  edge naming the admin/operator allowlist overlap documented above in *Boundary* would
  be the natural addition.
- **Whether any deployment currently sets `RELAY_OPERATOR_PUBKEYS` non-empty in
  production** was not checked -- this node describes the code's behavior, not any
  specific deployment's live configuration.
- **The exact shape of `crate::handlers::community_provisioning`'s internals** was read
  only far enough to confirm what `provision_community`, `normalize_candidate_host`,
  and `validate_pubkey_hex` are imported and called for; the module's own algorithm is
  intentionally left to `#1266`.
