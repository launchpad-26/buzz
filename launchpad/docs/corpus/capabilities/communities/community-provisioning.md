---
id: capabilities-communities-community-provisioning
type: architecture
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
  - statement: "node.schema.json's type enum has no member named flow, dynamic, capabilities-flow or similar, and the already-merged flow-shaped instance nodes in this corpus (architecture/flows/websocket-authentication.md, architecture/flows/http-event-submission.md and their siblings) all carry type: architecture rather than type: capabilities -- the precedent this node follows for its own type choice, extending it to a flow whose canonical path happens to sit under capabilities/communities/ rather than architecture/flows/."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
      - "launchpad/docs/corpus/templates/flow.md"
  - statement: "The already-merged capability template (launchpad/docs/corpus/templates/capability.md) explicitly excludes step-by-step narration from a capability node's scope, deferring it to the flow template instead -- so a document whose own Definition of Done asks it to state trigger/preconditions/termination, ordered interactions, trust-boundary crossings and failure/rollback behavior (issue #735's own checklist) is a flow-shaped body, not a capability-shaped one, regardless of which directory it is filed under."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/templates/flow.md"
  - statement: "A relay operator provisions a new community by sending POST /operator/communities, routed to api::operator::provision_community, which is NIP-98 authenticated and gated by the deployment-level RELAY_OPERATOR_PUBKEYS allowlist -- an empty allowlist (the default) disables provisioning entirely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:84-85"
      - "crates/buzz-relay/src/api/operator.rs:137-148"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:1-11"
  - statement: "Two preconditions must hold on the deployment before any provisioning request can succeed: RELAY_OPERATOR_API_ORIGIN must be configured (the canonical origin the NIP-98 signature is verified against) and the caller's pubkey must already be listed in RELAY_OPERATOR_PUBKEYS -- config.rs enforces that the origin is required as soon as the pubkey allowlist is non-empty, and defaults the allowlist itself to empty, i.e. provisioning disabled by default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:190-205"
      - "crates/buzz-relay/src/config.rs:662-686"
      - "crates/buzz-relay/src/config.rs:1136-1137"
  - statement: "The handler builds the canonical request URL from RELAY_OPERATOR_API_ORIGIN plus the request path and query, verifies a NIP-98 signature over it via bridge::verify_bridge_auth_with_options with no X-Pubkey development fallback (operator endpoints always require NIP-98), then checks the signing pubkey against RELAY_OPERATOR_PUBKEYS -- an unlisted pubkey is rejected with 403 Forbidden and the message 'actor not authorized: not a relay operator'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:60-102"
  - statement: "Before authorization proceeds, the verified NIP-98 event id is checked against a replay-detection scope named 'operator-management' with a shared default TTL; a previously-seen event id is rejected with 401 Unauthorized, and a failure of the replay-check mechanism itself (not merely a detected replay) is also rejected 401, fail-closed rather than fail-open."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:104-135"
  - statement: "The request body deserializes to ProvisionCommunityRequest{host, initial_owner_pubkey: Option<String>, create_only: bool}; malformed JSON is rejected 400 Bad Request before any database call."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:164-169"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:41-54"
  - statement: "validate_host rejects an empty host, a host over 255 bytes (matching the communities.host VARCHAR(255) column), a host that is not already in normalized form (lowercase, no default port, no trailing FQDN dot -- normalize_host must be a no-op on it), and a host that is not a bare authority (rejecting scheme/path/query/userinfo, control/whitespace characters, and invalid domain labels or IPv6 literals) -- any violation is surfaced to the caller as 400 Bad Request via provision_community's own generic error-message fallthrough."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:77-171"
      - "crates/buzz-relay/src/api/operator.rs:191"
  - statement: "When create_only is true, initial_owner_pubkey is required (its absence is rejected before any database call), and the request calls Db::create_community_with_owner, which serializes on a per-owner-pubkey Postgres advisory transaction lock (pg_advisory_xact_lock), attempts an INSERT INTO communities ... ON CONFLICT (lower(host)) DO NOTHING, and -- only if a new row was actually inserted -- checks the caller's current owned-community count against the configured per-owner limit before inserting the relay_members owner row, all inside one transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:280-300"
      - "crates/buzz-db/src/lib.rs:1490-1528"
  - statement: "create_community_with_owner rolls back and returns LimitReached when the owner is already at the configured per-owner community limit (never inserting the community row's owner, though the host row itself was already inserted by the earlier ON CONFLICT DO NOTHING in the same transaction and is undone by the rollback), and rolls back and returns HostExists when the host already existed for a different owner or role -- both are surfaced by the HTTP handler as 409 Conflict, never 500, and never leave a partially-provisioned row behind because the whole sequence is one transaction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:1529-1567"
      - "crates/buzz-relay/src/api/operator.rs:181-183"
  - statement: "A live integration test (ignored by default, requiring Postgres) exercises exactly this limit path: it provisions communities up to buzz_db::relay_members::MAX_COMMUNITIES_PER_OWNER for one owner, then asserts the next provisioning attempt returns 409 Conflict with an error message starting 'limit_reached:', and separately asserts the rejected fresh host was never persisted (lookup_community_by_host returns None for it) -- the representative verification for the LimitReached failure/rollback path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:1079-1109"
  - statement: "When create_only is false (the legacy/convergence mode), the request calls Db::ensure_configured_community, whose INSERT ... ON CONFLICT (lower(host)) DO UPDATE SET host = communities.host is guarded by WHERE communities.deletion_state = 'active' AND communities.deleted_at IS NULL, so the statement is idempotent for a live host but returns no row (mapped to a DbError::AccessDenied 'is permanently tombstoned') for a host whose community was already deleted -- a tombstoned host cannot be silently resurrected by a provisioning retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:1450-1480"
  - statement: "In convergence mode, when initial_owner_pubkey is present the handler always calls Db::bootstrap_owner for the resolved community, even if the community already existed -- the module's own doc comment states this explicitly rotates any previous owner to admin, the same semantics as rotating the deployment-wide RELAY_OWNER_PUBKEY env var, so an operator-signed convergence request is documented as deployment-root authority rather than create-only authority (the reason create_only exists as a separate, non-rotating code path for client-triggered self-serve creation)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:240-248"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:318-334"
  - statement: "After a successful owner bootstrap or rotation, and only when the deployment has require_relay_membership enabled, the handler publishes a best-effort NIP-43 membership-list snapshot for the community; a publication failure is logged as a warning and does not turn an already-committed database success into an HTTP error, because the row-level provisioning is already durable by that point."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:204-230"
  - statement: "On success the handler returns 200 OK with ProvisionCommunityResponse{community_id, host, status: \"created\"|\"existed\", owner_pubkey}; a database persistence failure after the operator/host/owner-format checks have already passed (either the create_only insert or the legacy owner-bootstrap call) is mapped to 500 Internal Server Error and logged server-side as 'operator community persistence failed', never leaking the underlying database error text to the caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:171-193"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:56-69"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs:310-350"
  - statement: "A live integration test (ignored by default, requiring Postgres) exercises the create_only happy path end to end: POST /operator/communities with create_only, asserts 200 OK and status \"created\", then reads back the community row and the relay_members row to assert the initial owner was persisted with role \"owner\", and asserts the resulting NIP-43 membership snapshot reflects that single owner role -- the representative verification for the successful-creation outcome."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:1043-1075"
  - statement: "A community is a durable row in Postgres's communities table (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), host VARCHAR(255) NOT NULL with a UNIQUE index on lower(host), signing_key BYTEA, created_at TIMESTAMPTZ) -- creating a community is exactly the INSERT this flow performs, never a DDL or schema-migration operation, and this table is explicitly documented as operator-global (the tenant registry itself), not tenant-scoped by a community_id column of its own."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:53-62"
      - "docs/multi-tenant-relay.md:70-74"
  - statement: "Separately from the operator HTTP surface this node documents, relay startup (crates/buzz-relay/src/main.rs) calls the same Db::ensure_configured_community idempotently every boot to seed the deployment's own single community from its configured relay_url, before any relay-membership allowlist backfill or RELAY_OWNER_PUBKEY bootstrap runs -- so a single-tenant/local deployment provisions its one community automatically at startup, while the /operator/communities endpoint documented here is the on-demand path a running multi-tenant deployment uses to provision additional communities without a restart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:254-297"
  - statement: "The per-owner community limit and its advisory-lock serialization exist specifically so that two concurrent create_only requests from the same owner cannot both observe the count check before either commits, which would let one owner exceed the configured quota -- read from the function's own inline comment rather than from a separate design document."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/lib.rs:1494-1497"
    confidence: 0.85
  - statement: "Issue #735's own Definition of Done requires the document to state trigger/preconditions/termination-outcome, list ordered interactions and data/state movement, identify authentication/authorization/trust-boundary crossings, and document failure/abort/rollback behavior linked to representative verification -- this is the checklist this node's Sequence, Diagram, Outcome and Boundary sections are built to satisfy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#735 definition of done"
  - statement: "Sibling issue #732 ('community-creation') carries a byte-identical Definition of Done template targeting launchpad/docs/corpus/capabilities/communities/community-creation.md, giving no further text distinguishing 'creation' from 'provisioning' beyond the two different filenames -- this node does not assume or assert what #732's document covers, and declares no relationship to community-creation because that node is unmerged and its actual scope was not read from committed content, only from its own issue body."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#732 issue body (read directly via gh issue view)"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
  - type: references
    target: architecture-principles-community-is-security-boundary
  - type: references
    target: architecture-deployment-multi-community
  - type: references
    target: architecture-flows-websocket-authentication
---

# Community provisioning: flow

This node narrates one flow: a relay operator provisioning a community -- a new
tenant row plus (optionally) its initial owner -- on a running Buzz relay, via
the `POST /operator/communities` HTTP surface. The trigger is an authenticated
HTTP request from a pubkey already listed in the deployment's
`RELAY_OPERATOR_PUBKEYS` allowlist. Preconditions: `RELAY_OPERATOR_API_ORIGIN`
must be configured (required as soon as the allowlist is non-empty), and the
allowlist itself must be non-empty, since an empty allowlist -- the default --
disables provisioning entirely and fails every request closed. The flow
terminates either in a durably persisted `communities` row (and, when an owner
was supplied, a durably persisted owner membership row) or in a rejection with
no partial state left behind.

This is one of two provisioning code paths that call the same underlying
database operations. The path narrated here is the **on-demand operator HTTP
surface**, used by a running multi-tenant deployment to provision additional
communities without a restart. A **separate, second path** -- relay process
startup in `crates/buzz-relay/src/main.rs` -- calls the same
`ensure_configured_community` idempotently on every boot to seed the
deployment's own single community from its configured `relay_url`; that
startup path is described here only as context for *Outcome* and is not this
node's own subject.

## Sequence

1. A relay operator's client sends `POST /operator/communities` with a JSON
   body `{ "host", "initial_owner_pubkey"?, "create_only"? }`, NIP-98 signed.
   (`crates/buzz-relay/src/router.rs:84-85`, `crates/buzz-relay/src/api/operator.rs:137-148`)
2. `authorize_operator_request` reconstructs the canonical request URL from
   `RELAY_OPERATOR_API_ORIGIN` plus the request path, and verifies the NIP-98
   signature against it with no development fallback -- operator endpoints
   always require NIP-98. (`crates/buzz-relay/src/api/operator.rs:60-85`)
3. The verified event id is checked against the `"operator-management"` replay
   scope; a previously-seen id, or a failure of the replay check itself, is
   rejected 401 before authorization is even attempted.
   (`crates/buzz-relay/src/api/operator.rs:104-135`)
4. The signing pubkey is checked against `RELAY_OPERATOR_PUBKEYS`. An unlisted
   pubkey is rejected 403 -- this check is deliberately **not** a
   community-scoped `relay_members` role lookup, because provisioning creates
   tenancy itself and so its authorizing identity must sit above any one
   tenant. (`crates/buzz-relay/src/api/operator.rs:88-99`,
   `crates/buzz-relay/src/handlers/community_provisioning.rs:1-11`)
5. The body is parsed into `ProvisionCommunityRequest`; malformed JSON is
   rejected 400 before any database call.
   (`crates/buzz-relay/src/api/operator.rs:164-169`)
6. `validate_host` checks the host is non-empty, ≤255 bytes, already
   normalized (lowercase, no default port, no trailing dot), and a bare
   authority (no scheme/path/query/userinfo, valid domain labels or IPv6
   literal); any violation is rejected 400.
   (`crates/buzz-relay/src/handlers/community_provisioning.rs:77-171`)
7. **If `create_only` is true**: `initial_owner_pubkey` is required and
   hex-validated, then `Db::create_community_with_owner` runs inside one
   transaction: it takes a per-owner-pubkey Postgres advisory lock, attempts
   `INSERT INTO communities ... ON CONFLICT (lower(host)) DO NOTHING`, and only
   if a row was actually inserted checks the owner's current community count
   against the configured limit before inserting the `relay_members` owner
   row. (`crates/buzz-relay/src/handlers/community_provisioning.rs:280-300`,
   `crates/buzz-db/src/lib.rs:1490-1528`)
8. **If `create_only` is false** (legacy/convergence mode):
   `Db::ensure_configured_community` runs
   `INSERT ... ON CONFLICT (lower(host)) DO UPDATE ... WHERE deletion_state = 'active' AND deleted_at IS NULL`,
   idempotently converging on the existing live row (or erroring if the host
   was already tombstoned). If `initial_owner_pubkey` is present, the handler
   *always* calls `Db::bootstrap_owner` for the resolved community -- even if
   it already existed -- rotating any previous owner to admin.
   (`crates/buzz-db/src/lib.rs:1450-1480`,
   `crates/buzz-relay/src/handlers/community_provisioning.rs:318-334`)
9. When `require_relay_membership` is enabled and an owner bootstrap/rotation
   ran, the handler best-effort publishes a NIP-43 membership-list snapshot
   for the community; a publish failure is logged, not surfaced as an HTTP
   error, since the database write is already committed.
   (`crates/buzz-relay/src/handlers/community_provisioning.rs:204-230`)
10. The handler returns 200 OK with `{community_id, host, status, owner_pubkey?}`
    on success. (`crates/buzz-relay/src/api/operator.rs:171-177`)

## Diagram

```mermaid
sequenceDiagram
    participant Op as Operator client
    participant API as api::operator::provision_community
    participant H as handlers::community_provisioning
    participant DB as Postgres (communities, relay_members)

    Op->>API: POST /operator/communities (NIP-98 signed)
    API->>API: verify NIP-98 signature vs RELAY_OPERATOR_API_ORIGIN
    API->>API: check replay scope "operator-management"
    API->>API: check pubkey in RELAY_OPERATOR_PUBKEYS
    alt not authorized
        API-->>Op: 403 Forbidden
    else replay detected
        API-->>Op: 401 Unauthorized
    else authorized
        API->>H: provision_community(request)
        H->>H: validate_host(request.host)
        alt create_only = true
            H->>DB: BEGIN; advisory lock(owner); INSERT communities ON CONFLICT DO NOTHING
            alt host already existed
                DB-->>H: no row inserted
                H->>DB: ROLLBACK
                H-->>API: HostExists
                API-->>Op: 409 Conflict
            else owner at limit
                DB-->>H: row inserted, count >= limit
                H->>DB: ROLLBACK
                H-->>API: LimitReached
                API-->>Op: 409 Conflict
            else within limit
                H->>DB: INSERT relay_members(owner); COMMIT
                H-->>API: Created
                API-->>Op: 200 OK {status: "created"}
            end
        else create_only = false
            H->>DB: INSERT communities ON CONFLICT DO UPDATE WHERE active
            DB-->>H: EnsuredCommunityRecord{id, created}
            opt initial_owner_pubkey present
                H->>DB: bootstrap_owner(community, owner)
                H->>H: publish_membership_snapshot_if_required (best-effort)
            end
            H-->>API: {status: created|existed}
            API-->>Op: 200 OK
        end
    end
```

## Outcome

**Success.** A durable row exists in `communities` (and, when an owner was
supplied, a durable `relay_members` row with role `owner`), and the caller
receives 200 OK with the community id, canonical host, a `status` of
`"created"` or `"existed"`, and the owner pubkey when one was bootstrapped.
This is verified end to end by a live (Postgres-requiring) integration test
that provisions a community, then reads back both the `communities` row and
the `relay_members` owner row, and asserts the NIP-43 membership snapshot
reflects that single owner
(`crates/buzz-relay/src/api/operator.rs:1043-1075`).

**Failure paths, each verified not to leave partial state:**

- **Unauthorized caller** (pubkey not in `RELAY_OPERATOR_PUBKEYS`, or
  `RELAY_OPERATOR_API_ORIGIN` unconfigured) → 403 Forbidden or an internal
  configuration error; no database call is made
  (`crates/buzz-relay/src/api/operator.rs:60-99`).
- **Replayed NIP-98 event, or replay-check failure** → 401 Unauthorized before
  authorization is attempted (`crates/buzz-relay/src/api/operator.rs:104-135`).
- **Malformed request body or invalid host/pubkey format** → 400 Bad Request
  before any database call
  (`crates/buzz-relay/src/api/operator.rs:164-169,191`).
- **`create_only`, host already exists, or owner at the per-owner limit** → the
  whole `create_community_with_owner` transaction rolls back (the host insert
  performed earlier in the same transaction is undone), and the handler
  returns 409 Conflict. A live integration test provisions communities up to
  the configured per-owner limit, asserts the next attempt returns 409 with an
  error starting `"limit_reached:"`, and asserts the rejected fresh host was
  never persisted (`crates/buzz-db/src/lib.rs:1529-1567`,
  `crates/buzz-relay/src/api/operator.rs:1079-1109`).
- **Database persistence failure** after all format/authorization checks
  passed → 500 Internal Server Error, logged server-side without leaking the
  underlying database error text to the caller
  (`crates/buzz-relay/src/api/operator.rs:184-190`).
- **Best-effort NIP-43 snapshot publish failure** (convergence-mode owner
  bootstrap/rotation only) → logged as a warning; does **not** roll back or
  fail the already-committed provisioning, and does not change the HTTP
  response (`crates/buzz-relay/src/handlers/community_provisioning.rs:204-230`).

## Boundary

This node does not describe:

- **The standing structure of the relay or Postgres containers** the flow's
  steps run inside -- see `architecture-containers-relay` and the deployment
  topology nodes for that.
- **What a "community" lets a user or agent do** as a product-level
  capability (channels, membership, workflows, audit chains) -- that is a
  capability node's territory, not narrated here.
- **The general, durable contract of the `/operator/communities` route group**
  independent of this one scenario (its sibling `/archive`, `/unarchive`,
  `/transfer`, and `/availability` routes) -- an interface node's territory,
  not this flow's.
- **Community *creation* as a distinct concern from provisioning**, per issue
  #732 (`community-creation.md`, unmerged at the time this node was written).
  This node does not assume or assert what that document covers; see *Scope
  and omissions* below.
- **The multi-tenant isolation proof itself** (row-level security, the
  resolved-`community_id`-is-sole-authority invariant, non-interference
  theorems) -- that is `docs/multi-tenant-relay.md`'s and
  `architecture-principles-community-is-security-boundary`'s subject; this
  flow only provisions the tenant row those proofs then isolate.
- **Relay-startup community seeding** as its own subject -- it is described
  above only to distinguish it from the on-demand operator flow this node
  narrates; it is the same underlying `ensure_configured_community` call, run
  from a different trigger (process boot, not an HTTP request).

## Relationships

- references: `architecture-principles-host-selects-community` -- the
  host-to-community resolution this flow's provisioned row becomes the target
  of for every subsequent request to that host.
- references: `architecture-principles-community-is-security-boundary` -- the
  isolation guarantee that begins applying to a community the moment this
  flow's `INSERT` commits.
- references: `architecture-deployment-multi-community` -- the deployment
  topology in which more than one community coexists behind one relay, which
  this flow is how an operator grows into.
- references: `architecture-flows-websocket-authentication` -- the sibling
  authentication flow this node's NIP-98/replay steps parallel structurally
  (a different credential, the same fail-closed-on-replay discipline).

## Scope and omissions

**This node covers** the `POST /operator/communities` flow: its trigger,
preconditions, authentication/authorization/replay steps, the two internal
code paths (`create_only` atomic creation vs. legacy convergence), their
success and failure outcomes, and the trust boundary between deployment-root
operator authority and per-community `relay_members` authority.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `/operator/communities/archive`, `/unarchive`, `/transfer`, and `/availability` routes in the same file | a future interface- or flow-shaped node, not yet drafted |
| What a community *is* as a product capability, or the multi-tenant isolation proof | `architecture-principles-community-is-security-boundary`, `docs/multi-tenant-relay.md` |
| Community creation as a possibly-distinct concern (issue #732) | #732's own document, unmerged at authoring time |
| The `buzz-admin` CLI's own tenant-resolution path (mentioned in `crates/buzz-core/src/tenant.rs`'s doc comments but not read for this node) | not yet drafted |

**Expected but not verified when this node was written:**

- **Whether any first-party client (desktop, mobile, `buzz-cli`) calls
  `POST /operator/communities` today.** Only the relay-side handler, its unit
  tests, and its live integration tests were read; no client-side caller was
  searched for.
- **Whether issue #732's `community-creation.md` narrates this same endpoint
  from a different angle, a different endpoint entirely, or a client-facing
  self-serve flow.** That document was unmerged and unread beyond its own
  issue body at authoring time, so this node declares no relationship to it
  and does not guess at overlap or its absence.
- **The exact value of `MAX_COMMUNITIES_PER_OWNER` / `max_communities_per_owner()`**
  was not read from `crates/buzz-db/src/relay_members.rs` itself, only its use
  at the two call sites cited above; this node makes no claim about its
  numeric value.
