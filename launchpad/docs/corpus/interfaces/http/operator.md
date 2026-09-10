---
id: interfaces-http-operator
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "node.schema.json's type enum has no HTTP-specific value; the only interface-shaped member is the single hyphenated token interfaces-events, and the corpus's own interface template states an interface instance node carries type: interfaces-events regardless of whether the interface is HTTP, WebSocket, CLI, or an embedded external protocol."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "At repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052, git ls-tree of origin/launchpad's launchpad/docs/corpus tree contains no interface-shaped node (only AGENTS.md, README.md, schema/, standards/, templates/, and a handful of architecture nodes), so relationships has no legitimate target and is omitted from this node's front matter."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052; no interfaces/ directory present"
  - statement: "crates/buzz-relay/src/router.rs registers five routes under /operator/communities* -- GET+POST /operator/communities, POST /operator/communities/archive, POST /operator/communities/unarchive, GET /operator/communities/availability, and POST /operator/communities/transfer -- all backed by handlers in crates/buzz-relay/src/api/operator.rs, distinct from the /api/admin/v1 nested router mounted separately in the same file only when state.config.admin is Some."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:53-105"
  - statement: "Every operator.rs handler calls authorize_operator_request first, which builds the full request URL from the deployment-configured RELAY_OPERATOR_API_ORIGIN (never the inbound Host header or tenant registry), verifies a NIP-98 (kind:27235) Authorization: Nostr signature over that URL via bridge::verify_bridge_auth_with_options with require_auth_token=true (no X-Pubkey dev-mode fallback permitted on this surface), rejects a replayed event id in the operator-management replay scope, and finally checks the signer's hex pubkey against the config-level relay_operator_pubkeys allowlist, returning 403 Forbidden if the origin is unconfigured (500), the signature is invalid (401), the event id was already seen (401), or the pubkey is not allowlisted (403)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:55-135"
      - "crates/buzz-relay/src/api/bridge.rs:72-128"
  - statement: "POST /operator/communities (provision_community) accepts { host, initial_owner_pubkey?, create_only? } and returns { community_id, host, status: \"created\"|\"existed\", owner_pubkey? }; failures map to 403 (actor not authorized), 409 Conflict (\"community already exists\" or a limit_reached: message), 500 (a persistence failure, logged server-side and returned as a generic internal-error body), or 400 for any other rejection (e.g. invalid host or pubkey shape)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:137-193"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:41-69"
  - statement: "community_provisioning.rs documents the request as idempotent on the host row: re-sending it never duplicates a community, and when initial_owner_pubkey is present the owner is (re)bootstrapped even for an already-existing host, demoting any previous owner to admin -- the same rotation path RELAY_OWNER_PUBKEY uses at startup. create_only=true instead rejects an existing host with community already exists rather than converging, so a caller can choose atomic-create-or-fail versus converge-or-rotate semantics."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:232-351"
  - statement: "POST /operator/communities/archive and POST /operator/communities/unarchive are documented as idempotent, take { host, owner_pubkey } asserting the caller-supplied owner, refuse to archive the deployment's own host with 409 Conflict, return 404 Not Found when no matching community/owner row exists, and archive additionally returns 503 Service Unavailable (with a retry-safe partial-success body) if cluster-wide connection disconnection after the DB commit fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:195-299"
  - statement: "GET /operator/communities (list_owned_communities) requires an owner_pubkey query parameter validated as a 64-char hex pubkey (400 otherwise) and returns { owner_pubkey, communities: [{ community_id, host, created_at, archived_at }] } for every community where that pubkey currently holds the owner role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:301-340"
  - statement: "POST /operator/communities/transfer takes { community_id, new_owner_pubkey, expected_owner_pubkey } and demotes the previous owner to member (never admin); its four possible outcomes map to Transferred -> 200 { status: \"transferred\", previous_owner }, AlreadyOwner -> 200 { status: \"already_owner\" }, NoOwner -> 404, and OwnerConflict -> 409 (\"the current owner no longer matches expected_owner_pubkey\", an optimistic-concurrency check against expected_owner_pubkey) or LimitReached -> 409. Publication of the updated NIP-43 membership snapshot afterward is explicitly best-effort and never turns a committed transfer into an HTTP error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:342-465"
  - statement: "GET /operator/communities/availability takes a host query parameter, normalizes it the same way create does, and returns { host, normalized_host, available, community_id? } without requiring the host to already be canonical -- letting a caller ask the relay for the canonical spelling before calling create."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:466-498"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:173-202"
  - statement: "Every error response on this surface (and on the sibling Nostr HTTP bridge api_error/internal_error helpers this module reuses) is a JSON object shaped { \"error\": \"<message>\" }; internal_error additionally logs the real failure server-side via tracing::error! and returns only the fixed string \"internal server error\" to the caller, so no internal detail is echoed on a 500."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/mod.rs:18-33"
  - statement: "crates/buzz-relay/src/config.rs documents, in its own boot-time comment, that RELAY_OPERATOR_PUBKEYS is the shared allowlist for BOTH the community-provisioning endpoints documented in this node AND the separate NIP-98 admin console (/api/admin/v1, config.rs's AdminConfig/AdminAuth), and that only the provisioning endpoints additionally require RELAY_OPERATOR_API_ORIGIN to be configured -- an allowlisted operator with no origin configured gets a clean 500 from every /operator/communities* call while the admin console remains unaffected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:742-791"
  - statement: "AdminConfig/AdminAuth (config.rs:27-73) gate a structurally separate surface: an exact admin HTTP authority checked via the request Host header (is_admin_host), its own auth-mode selection via BUZZ_ADMIN_AUTH (nip98 default or disabled, never the operator-endpoints' always-NIP-98 requirement), and NIP-98-mode principal resolution into Operator/Config, Operator/OwnerFallback, or Moderator/Db (from a relay_operators DB table) rather than this surface's single allow/deny pubkey check -- RELAY_OPERATOR_PUBKEYS membership is only one of three ways to resolve a principal there, not the sole gate the way it is for /operator/communities*."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:27-73"
  - statement: "buzz-admin (crates/buzz-admin/src/main.rs) is a separate CLI that connects directly to Postgres via connect_db()/DATABASE_URL and to Redis for membership-list publication; it never issues an HTTP request to this relay and has no client relationship to /operator/communities* -- it is a distinct administration surface (member add/remove, migrations, product feedback, deletions, channel reconciliation) reachable only by running the binary inside the relay's own container."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:1-30"
      - "crates/buzz-admin/src/main.rs:433-472"
  - statement: "No OpenAPI or AsyncAPI specification document exists anywhere in this repository describing this or any other Buzz-owned HTTP surface; the only openapi-adjacent dependency is k8s-openapi, Rust bindings generated from the Kubernetes API server's own types and used exclusively by buzz-backend-kubernetes to talk to the Kubernetes control plane, not a document Buzz authors for its own interfaces."
    entry_class: FACT
    evidence:
      - "grep_repo('asyncapi|swagger|openapi', types='rs,toml,md,yaml,yml,json', exclude='node_modules,target') -> only k8s-openapi references (Cargo.toml:70, crates/buzz-backend-kubernetes/**) and this repository's own corpus/research prose discussing OpenAPI as an industry model, verified 2026-09-01 against commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "operator.rs's own test suite exercises a valid round trip: happy_path_create_returns_created_and_bootstraps_owner signs a NIP-98 request from an allowlisted operator key, calls provision_community for a fresh host with a distinct owner key, asserts a 200 OK response with status: \"created\" and the echoed host, and then asserts the owner key holds the owner role in relay_members and in the published NIP-43 snapshot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:1043-1075"
  - statement: "operator.rs's own test suite exercises a failure case: non_allowlisted_operator_key_gets_403 signs a syntactically valid NIP-98 POST /operator/communities request from a key that is not in the configured operator allowlist and asserts the response status is 403 Forbidden."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:707-735"
  - statement: "Issue launchpad-26/buzz#977 ('task: document interfaces/http/admin.md'), open as of this node's authoring, targets launchpad/docs/corpus/interfaces/http/admin.md as the canonical node for the /api/admin/v1 admin dashboard -- the sibling this node's Boundary section names but does not fold into itself."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#977 (gh issue view, state: OPEN, title: 'task: document interfaces/http/admin.md')"
  - statement: "Issue launchpad-26/buzz#985's own Definition of Done requires defining inputs/messages, outputs/responses and error/rejection behavior; authentication/authorization, versioning/compatibility and ordering/idempotency where applicable; linking the authoritative machine/spec representation when one exists; and including at least one valid and one failure example -- the acceptance bar this node is built against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#985 definition of done"
---

# Operator communities: interface

The deployment-root HTTP control plane a relay **operator** (the entity that runs a
Buzz relay deployment, distinct from any single community's owner or admin) uses to
create, look up, archive/unarchive, and transfer ownership of communities (tenants)
hosted on that deployment. Requests are plain HTTP + JSON, signed with NIP-98
(`Authorization: Nostr <base64 kind:27235 event>`) the same way the generic Nostr
HTTP bridge (`POST /events`/`/query`/`/count`) is signed, but this surface sits
outside the Nostr event data plane entirely: it does not run through event ingest,
relay membership, channel scoping, storage, or fan-out, and it is authorized against
a deployment-level pubkey allowlist rather than any per-community role.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `POST /operator/communities` | `api::operator::provision_community` (`crates/buzz-relay/src/api/operator.rs`) | Create a community host and optionally bootstrap/rotate its initial owner. Idempotent on the host row; `create_only: true` makes it atomic-create-or-409 instead of converge-or-rotate. |
| `GET /operator/communities` | `api::operator::list_owned_communities` | List every community where a given `owner_pubkey` currently holds the `owner` role. |
| `POST /operator/communities/archive` | `api::operator::archive_community` | Idempotently archive a community, asserting its current `owner_pubkey`. Refuses to archive the deployment's own host. |
| `POST /operator/communities/unarchive` | `api::operator::unarchive_community` | Idempotently restore an archived community, asserting its current `owner_pubkey`. |
| `GET /operator/communities/availability` | `api::operator::community_availability` | Check whether a (possibly non-canonical) host is free, returning the canonical normalized form `create` would use. |
| `POST /operator/communities/transfer` | `api::operator::transfer_community` | Transfer ownership to `new_owner_pubkey`, guarded by an `expected_owner_pubkey` optimistic-concurrency check; demotes the previous owner to `member`. |

Route registration for all six: `crates/buzz-relay/src/router.rs:86-105`.

## Contract and stability

**Authentication and authorization.** Every request is authenticated with NIP-98
(kind:27235) exactly as the Nostr HTTP bridge is, with no `X-Pubkey` development
fallback ever permitted on this surface (`authorize_operator_request` always passes
`require_auth_token = true`). The signed URL is built from the deployment-configured
`RELAY_OPERATOR_API_ORIGIN`, never from the inbound `Host` header or the tenant
registry — this is a deployment-root surface, not a tenant-scoped one. The signer's
pubkey must additionally appear in the config-level `RELAY_OPERATOR_PUBKEYS`
allowlist; an empty allowlist (the default) disables provisioning for everyone. NIP-98
replay protection is scoped separately (`operator-management`) from the bridge's own
replay scope. `RELAY_OPERATOR_PUBKEYS` is also one input to the *separate*
`/api/admin/v1` admin console's principal resolution (see *Boundary* below) — the one
piece of configuration the two surfaces share.

**Versioning and compatibility.** No version segment appears in these paths and no
versioning scheme is documented for them; a breaking change to the request/response
JSON shapes above would be a breaking change to this contract.

**Idempotency and ordering.** `provision_community` is idempotent on the host row by
design (documented in `community_provisioning.rs`); `archive_community` and
`unarchive_community` are explicitly documented as idempotent. `transfer_community` is
not idempotent in the sense of "same effect every time" — its `expected_owner_pubkey`
check makes a second identical call after a successful transfer return `409
owner_conflict` rather than repeating the transfer, which is the intended
optimistic-concurrency guard against a stale caller re-asserting an owner that has
already changed.

**Error and rejection behavior.** Every error body is `{"error": "<message>"}`.
Authorization failures: 500 if the operator origin is not configured server-side, 401
for an invalid/missing/replayed NIP-98 signature, 403 if the signer is not
allowlisted. Domain failures use 400 (malformed input), 404 (no matching
community/owner), or 409 (a real conflict: already exists, owner mismatch, or a
per-owner community limit reached). A persisted mutation that could not finish a
best-effort side effect (cluster-wide disconnect after archive, NIP-43 snapshot
publication after provision/transfer) is never turned into a false error for the
already-committed core operation — archive alone returns 503 with a retry-safe
partial-success body when disconnect propagation is pending; the other best-effort
failures are logged and the success response still returns.

**Authoritative machine/spec representation.** None exists. No OpenAPI, AsyncAPI, or
other machine-readable description of this HTTP surface is present anywhere in this
repository; the route table in `router.rs` plus the handler doc comments in
`operator.rs` are the surface's only description, and this node points at that code
rather than re-encoding it.

## Boundary

This node does not describe:

- **`/api/admin/v1/*`, the separate deployment-admin dashboard** (issue
  `launchpad-26/buzz#977`, open and unmerged as of this node's authoring, targets
  `launchpad/docs/corpus/interfaces/http/admin.md`). That surface is a distinct route
  tree (nested under `/api/admin/v1`, mounted only when `state.config.admin` is set),
  bound to its own exact HTTP authority via a `Host`-header check, with its own
  `BUZZ_ADMIN_AUTH` mode selection (`nip98` default or `disabled`, never this
  surface's always-required NIP-98) and its own three-way principal resolution
  (`Operator/Config`, `Operator/OwnerFallback`, `Moderator/Db`). **The two surfaces
  are not the same routes wearing different names, but they are not fully
  independent either**: `RELAY_OPERATOR_PUBKEYS` is documented in `config.rs` itself
  as the shared allowlist for both — membership in it is the *sole* gate for
  `/operator/communities*` and is *one of three* paths to a resolved principal on
  `/api/admin/v1`. Whichever node documents that dashboard should name this same
  overlap rather than treat the two allowlists as independent facts.
- **A single Nostr event kind's own wire contract.** This surface issues no Nostr
  events itself (its best-effort side effects publish an existing NIP-43 membership
  snapshot kind, not a kind this surface owns). Kind-level contracts belong to a
  future event-kind node, not this one.
- **`buzz-admin`, the CLI crate.** Confirmed by reading its `main.rs`: it talks
  directly to Postgres and Redis from inside the relay's own container and never
  calls this or any other HTTP surface. It is a different administration tool
  entirely, not a client of `/operator/communities*`.
- **Field-by-field, domain-expert-depth parameter cataloguing** beyond the operation
  table and contract above.

## Relationships

None declared. At the recorded revision, no interface-shaped node is merged on
`origin/launchpad`'s corpus tree to `references`, `implements`, or sit `part-of` —
only governance/architecture nodes and the `templates/interface.md` template (not
itself a valid relationship target) exist there. The natural moment to add a
`references` edge toward `interfaces-http-admin` is once issue `#977` merges that
node.

## Scope and omissions

**This node covers** the `/operator/communities*` HTTP surface end to end: its six
operations, their request/response JSON shapes, NIP-98 authentication and the
`RELAY_OPERATOR_PUBKEYS`/`RELAY_OPERATOR_API_ORIGIN` authorization gate, error and
status-code behavior, idempotency and ordering guarantees, the absence of any
machine-readable spec, and one valid and one failure example drawn from this
surface's own test suite.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `/api/admin/v1` deployment-admin dashboard's own routes, auth modes, and principal resolution in full | `launchpad-26/buzz#977` |
| A parameter-by-parameter, domain-expert-depth API reference for this surface | Undecided corpus-wide (`#1346`/`#1532`) |
| The NIP-43 membership-list event kind this surface publishes as a best-effort side effect | A future event-kind node, not filed as part of this task |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No end-to-end HTTP request was actually sent against a running relay.** Every
  claim above is grounded in reading `operator.rs`, `community_provisioning.rs`,
  `router.rs`, `config.rs`, `bridge.rs`, and `api/mod.rs`, plus the two cited unit
  tests exercised through axum's `oneshot` test harness — not a live deployment.
- **Whether any deployment currently sets `RELAY_OPERATOR_API_ORIGIN`/
  `RELAY_OPERATOR_PUBKEYS` in production, and what value it uses**, was not checked;
  this node describes the code's behavior for any configuration, not a specific
  deployment's actual configuration.
- **The full three-way principal-resolution logic for `/api/admin/v1`** (referenced
  in *Boundary* to establish the shared-allowlist overlap) was read only in
  `config.rs`'s own doc comments, not traced through
  `crates/buzz-relay/src/api/admin/auth.rs`'s runtime resolution function in full —
  that belongs to `#977`'s own evidence-gathering, not this node's.
