---
id: layers-authorization-operator-authorization
type: layers
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The relay's private, read-only deployment-admin HTTP API (reports and product-feedback routes under crates/buzz-relay/src/api/admin/) is gated by authorize(), which requires the inbound Host header to exactly match a configured AdminConfig.host and, when an Origin header is present, requires it to match that same host; failing either check returns HTTP 403 Forbidden, and the whole surface returns 404 Not Found when no admin host is configured at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs"
      - "crates/buzz-relay/src/api/admin/mod.rs"
  - statement: "The admin/mod.rs module's own doc comment describes this HTTP surface as a 'Private, read-only deployment moderation API,' and its router's only routes are GET /reports, GET /reports/{id}, GET /feedback, GET /feedback/{id} and GET /feedback/{id}/attachments/{sha256} -- a cross-community, read-only reporting and feedback view rather than a write surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs"
  - statement: "A dedicated test drives the real router and asserts that /reports/{id} and /feedback/{id}/attachments/{sha256} return 403 Forbidden when the request's Host header does not match the configured admin host, before any database access occurs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs"
  - statement: "The deployment-operator HTTP API under crates/buzz-relay/src/api/operator.rs (community provisioning, archiving, unarchiving, transfer, listing, and availability checks) is gated by authorize_operator_request(), which requires a NIP-98-signed request (no X-Pubkey dev-mode fallback is permitted on these routes) verified against a configured relay_operator_api_origin, and then requires the signer's hex pubkey to appear in the configured relay_operator_pubkeys allowlist; a signer not on that allowlist is refused with HTTP 403 and the message 'actor not authorized: not a relay operator.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "authorize_operator_request() additionally calls check_operator_replay(), which marks the request's NIP-98 event id as spent inside a dedicated 'operator-management' replay scope with a fixed TTL, rejecting a reused signed request with HTTP 401 even from an allowlisted operator pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "The NIP-43 relay-admin command handler (kinds 9030-9033, crates/buzz-relay/src/handlers/relay_admin.rs) states its own permission matrix in a doc comment: kind 9030 (add member) and 9031 (remove member) require the sender's role in the tenant-scoped relay_members table to be admin or owner; kind 9032 (change role) requires owner; kind 9033 (set workspace profile/icon) requires admin or owner, except on a relay that is both open (require_relay_membership is false) and has no admin/owner row for the community at all, where any NIP-42-authenticated sender may set it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "execute_relay_admin_command() enforces that matrix in code, not only in the doc comment: it looks up the sender's role from relay_members via get_relay_member(), rejects 9030/9031 when the sender's role is neither \"admin\" nor \"owner\", rejects a 9032 sender whose role is not exactly \"owner\", and rejects a 9033 sender who is neither admin nor owner unless may_set_workspace_profile()'s rosterless-open-relay branch admits them; each rejection path returns a distinct 'actor not authorized: ...' error string rather than a generic denial."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "The relay-admin command handler blocks granting or assuming the 'owner' role at runtime through any of kinds 9030-9032: kind 9030 rejects a role tag of 'owner' outright ('use kind:9032 to promote to owner'), and kind 9032 rejects a new_role of 'owner' outright, with a code comment stating this is a deliberate design choice because ownership transfer is high-risk and could permanently lock out the current owner; the doc comment states the only route to changing ownership is the RELAY_OWNER_PUBKEY configuration value plus a relay restart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "handle_relay_admin_event() checks the sender's durable moderation-restriction state (via moderation_restriction_state()) before executing any relay-admin command, and admits_relay_admin_command() rejects the command outright if the sender is durably banned; a database error during that lookup also rejects the command (fails closed) rather than admitting it, per the function's own 'Fail closed: a DB blip must never admit a banned admin' comment. A sender who is only timed out (muted_until set, not banned) is still admitted, because a timeout restricts content writes and ingest_event's exemption for relay-admin kinds is deliberately ban-blind rather than restriction-blind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "The buzz-admin operator CLI (crates/buzz-admin/src/main.rs) performs no per-invocation identity or permission check of its own before mutating relay_members or signing relay-authoritative events: connect_member_services() only requires the BUZZ_RELAY_PRIVATE_KEY, DATABASE_URL and REDIS_URL environment variables to be set, and its resulting Db and Keys handles are used directly against a single tenant resolved from the RELAY_URL host, with no NIP-98 signature, token or allowlist check anywhere in the binary."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "buzz-admin's deployment shape -- the CLI is invoked as 'compose exec relay buzz-admin ...', i.e. inside the already-running relay container -- is documented in a function-level doc comment on resolve_admin_tenant(), not in a top-of-file/module doc comment. Separately, its AddMember/RemoveMember role validation (validate_role()) rejects role \"owner\" with the error \"role 'owner' cannot be set via CLI -- use RELAY_OWNER_PUBKEY config\"; that phrasing echoes a code comment in relay_admin.rs's kind:9032 handler ('Use RELAY_OWNER_PUBKEY config to change ownership'), not any runtime error string relay_admin.rs itself returns -- relay_admin.rs's actual owner-rejection error strings are 'invalid role: use kind:9032 to promote to owner' (kind:9030) and 'cannot set role to owner' (kind:9032), neither of which mentions RELAY_OWNER_PUBKEY. Both surfaces still agree, in effect, that ownership is never grantable at runtime, only through relay restart configuration."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "cmd_remove_member() cannot remove the relay owner regardless of caller: db.remove_relay_member() returns RemoveResult::IsOwner for an owner-role target, and the CLI reports this as a distinct error ('cannot remove relay owner') rather than performing the removal, mirroring the owner-is-protected invariant kind:9031's execute_relay_admin_command() enforces for the same table."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "Community and channel content moderation -- deleting a message, kicking or banning a user, timing out a user, and resolving reports -- is decided by a structurally separate function, authorize_moderation_action() in crates/buzz-relay/src/handlers/moderation_authz.rs, whose own doc comment states there is 'no Moderator tier in v1' and that its authority comes from the same tenant-scoped relay_members role plus a channel's own owner/admin role, routed through 'one capability seam for every moderation decision' distinct from the relay-admin command handler."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
  - statement: "Because relay_admin.rs and moderation_authz.rs are independently implemented modules -- different files, different public entry points, different result/error types, and moderation_authz.rs's own doc comment describing itself as covering a distinct action set (ModerationAction::DeleteMessage/Kick/Ban/Unban/Timeout/Untimeout/ResolveReport/ViewQueue) from relay_admin.rs's roster-and-workspace-profile matrix -- roster/workspace administration (this node's subject) and content/user moderation are two separate authorization decisions in this codebase even though both may read the same relay_members.role value for the same pubkey."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
      - "crates/buzz-relay/src/handlers/moderation_authz.rs"
    confidence: 0.8
  - statement: "The four mechanisms this node documents are each implemented independently with their own checks: the admin-host HTTP gate, the operator-pubkey-allowlist HTTP gate, the buzz-admin CLI's deployment-access boundary, and the relay_members-role check inside execute_relay_admin_command() do not call a shared 'is this pubkey an operator' helper, and no such helper was found across those four call sites."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs"
      - "crates/buzz-relay/src/api/operator.rs"
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
      - "crates/buzz-admin/src/main.rs"
    confidence: 0.6
  - statement: "Reaching the relay-admin command handler at all over the WebSocket/HTTP event-ingest path is itself gated a second way, ahead of and separate from relay_admin.rs's own relay_members-role check: ingest_event() in crates/buzz-relay/src/handlers/ingest.rs maps kinds 9030-9033 to buzz_auth::Scope::AdminUsers via required_scope_for_kind(), rejects the event with 'restricted: insufficient scope' if the authenticated connection's granted scopes do not contain AdminUsers, and separately rejects a relay-admin kind outright if the connection authenticated with a channel-scoped token rather than a global one -- both checks run before relay_admin::handle_relay_admin_event() is ever called."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-auth's own module doc comment states that in pure Nostr mode every NIP-42-authenticated connection receives the full scope set (including AdminUsers), so the ingest-time scope gate is a real second check specifically for connections authenticated via a scoped API token rather than NIP-42 -- for a NIP-42-authenticated sender, relay_admin.rs's own relay_members-role check is what actually discriminates admin/owner from member, not the scope gate."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/scope.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.6
  - statement: "The fail-closed-boundaries architecture principle states that a relay decision which admits, authenticates, authorizes, or scopes a request to a tenant MUST deny rather than substitute an implicit allow when the underlying lookup fails, and names authorization decisions generally as within its scope; admits_relay_admin_command()'s ban-lookup-error handling is a concrete instance of that same fail-closed shape applied to operator-tier authorization specifically."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/fail-closed-boundaries.md"
      - "crates/buzz-relay/src/handlers/relay_admin.rs"
  - statement: "Issue #1038's Definition of Done requires this node to have schema-valid front matter with a stable id, typed relationships where appropriate, evidence classified honestly across FACT/INFERENCE/TEAM_KNOWLEDGE, links to relevant implementation/verification/decision material and neighboring corpus nodes without duplicating their content, a definition of the term in one sentence before deeper explanation, a boundary/non-goals statement, and examples used only to clarify rather than to introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1038 definition of done"
relationships:
  - type: references
    target: architecture-context-relay-operator
  - type: references
    target: architecture-principles-fail-closed-boundaries
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Operator authorization

**Operator authorization** is the set of checks Buzz uses to decide whether a given
actor may administer a relay deployment or a community's membership and workspace
configuration — as distinct from moderating content or users within a community, which
a separate authorization seam governs. Concretely, "operator" here means: whoever
provisions, configures, or administers the relay process itself, and whoever holds an
`owner`/`admin` role in a community's `relay_members` roster.

## Boundary: what this covers, and what it does not

**In scope**, and the subject of this node: the mechanisms that decide who may run
deployment-operator HTTP endpoints, who may add, remove, or promote a community's
relay members, who may set a community's workspace icon, and how `buzz-admin` — the
operator CLI shipped inside the relay's own Docker image — establishes its own trust.

**Out of scope, and owned by a separate concept.** Deciding who may delete a message,
kick or ban a user, apply or lift a timeout, or resolve a moderation report is a
structurally distinct decision, made by `authorize_moderation_action()` in
`crates/buzz-relay/src/handlers/moderation_authz.rs`, not by anything this node
describes. The two seams can read the *same* `relay_members.role` value for the same
pubkey — a community `owner` or `admin` is authoritative for both roster
administration and content moderation — but they are enforced by different functions
answering different questions, and a future corpus node on community/channel
moderation is where the moderation seam belongs, not here.

**Also out of scope:** the `architecture-context-relay-operator` node's own broader
"relay operator" role — provisioning secrets, choosing an image, running Compose or
Helm, backing up state. That node's own scope-and-omissions table names "internal
implementation of `buzz-admin`'s subcommands" and "`buzz-relay`'s internal request
routing, module structure, or security model" as gaps owned by a future
container/component-level node; this node is that follow-on for the authorization
half specifically. It does not restate that node's deployment-toolchain content.

## The four mechanisms

Buzz enforces operator authorization at four independently implemented points, not
through one shared "is this pubkey an operator" check.

1. **Read-only deployment-admin HTTP API** (`crates/buzz-relay/src/api/admin/`). Gates
   `GET /reports`, `/reports/{id}`, `/feedback`, `/feedback/{id}` and
   `/feedback/{id}/attachments/{sha256}` on the inbound request's `Host` header
   matching a configured `AdminConfig.host`, plus an `Origin` header (when present)
   matching that same host. No admin host configured means the whole surface 404s;
   a mismatched host or origin means 403. This is a cross-community, read-only view —
   there is no write route on this router at all.

2. **Deployment-operator HTTP API** (`crates/buzz-relay/src/api/operator.rs`).
   Provisions, archives, unarchives, transfers and lists communities, and checks
   host-name availability. Every route requires a NIP-98-signed request — there is
   no dev-mode `X-Pubkey` fallback here — verified against a configured
   `relay_operator_api_origin`, and then requires the signer's pubkey to be a member
   of the configured `relay_operator_pubkeys` allowlist. A signed-but-not-allowlisted
   request is refused with `actor not authorized: not a relay operator`. A dedicated
   replay guard additionally rejects a reused signed request even from an allowlisted
   operator.

3. **NIP-43 relay-admin commands** (kinds 9030–9033,
   `crates/buzz-relay/src/handlers/relay_admin.rs`). Mutate a *community's* own
   `relay_members` roster and workspace icon, and are gated twice. Before the command
   handler ever runs, `ingest_event()` requires the connection's granted scopes to
   include `Scope::AdminUsers` and requires a global (not channel-scoped) token — a
   check that matters for a connection authenticated via a scoped API token, since a
   NIP-42-authenticated connection receives every scope by default. Inside the handler
   itself, the sender's current role in `relay_members` decides what they may do:
   `admin` or `owner` may add (9030) or remove (9031) a plain member; only `owner` may
   change a member's role (9032); `admin` or `owner` may set the workspace icon (9033),
   with a narrow exception for a genuinely rosterless open relay. No path through any
   of these commands can grant the `owner` role itself — both 9030 and 9032 refuse a
   role of `owner` outright, and the code comments state this is deliberate: ownership
   only ever changes through the `RELAY_OWNER_PUBKEY` configuration value and a relay
   restart. A durable ban on the sender is checked and fails the command closed before
   it runs (a lookup error also denies rather than admits); a mere timeout does not
   block these commands, because a timeout restricts content, not administrative
   capability.

4. **`buzz-admin`, the operator CLI.** Ships inside the relay's own Docker image and is
   invoked as `compose exec relay buzz-admin ...` — i.e., from inside the already-running
   container. It performs no per-invocation authorization check of its own: given the
   right environment variables (`BUZZ_RELAY_PRIVATE_KEY`, `DATABASE_URL`, `REDIS_URL`),
   it connects to the database and Redis directly and signs relay-authoritative events
   (the kind:13534 membership roster) with the relay's own private key. Its trust
   boundary is deployment access — whoever can exec into the container, or set those
   variables — not a runtime credential. It still respects the same "owner is
   config-only" invariant as mechanism 3: its `add-member`/`remove-member` subcommands
   refuse `--role owner`, and removing the configured owner is refused regardless of
   who runs the command.

## Example, for illustration only

Adding a community member through the desktop client and adding one through
`buzz-admin` exercise two different mechanisms above, not two different rules: a
signed-in `owner`/`admin` sending a kind:9030 event goes through mechanism 3 and is
checked against their live `relay_members` role; an operator running
`buzz-admin add-member --pubkey <npub> --role admin` from inside the relay container
goes through mechanism 4 and is trusted because they could reach the container at
all. Both paths write the same `relay_members` row and both refuse `--role owner` /
`role: "owner"` for the same stated reason. This example exists to show the same
invariant enforced twice, not to introduce a third mechanism.

## Related corpus nodes

- **`architecture-context-relay-operator`** (`references`) — the broader relay-operator
  role this node's authorization mechanisms serve; that node names `buzz-admin` and the
  relay's membership commands as touchpoints but explicitly leaves their internal
  security model as a gap. This node is that gap's authorization half.
- **`architecture-principles-fail-closed-boundaries`** (`references`) — the fail-closed
  invariant for tenant-authorization decisions generally; this node's ban-check-fails-
  closed behavior in the relay-admin command handler is a concrete instance of that
  principle applied to operator-tier commands specifically.
- **`architecture-principles-community-is-security-boundary`** (`references`) — the
  host-derived community fence every tenant-scoped operation obeys; the deployment-wide
  mechanisms this node documents (the admin-host HTTP gate, the operator-pubkey
  allowlist) are the parts of Buzz that deliberately operate *across* that fence, which
  is worth naming explicitly rather than leaving as an implicit exception to it.

## Scope and omissions

**This node covers** the four mechanisms Buzz uses to authorize relay- and
community-administration actions — the read-only deployment-admin HTTP API, the
deployment-operator HTTP API, the NIP-43 relay-admin command matrix, and the
`buzz-admin` CLI's trust boundary — and the boundary between operator authorization
and community/channel content moderation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Content and user moderation (delete, kick, ban, timeout, reports) | `authorize_moderation_action()`, `crates/buzz-relay/src/handlers/moderation_authz.rs` — not yet a corpus node at this revision |
| The relay operator's broader deployment responsibilities (image selection, secrets, backups, Compose/Helm) | `architecture-context-relay-operator` |
| The full `buzz-auth` `Scope` enum and API-token scope machinery beyond the `AdminUsers`/`AdminChannels` gate on relay-admin and NIP-29 group-admin kinds specifically | `crates/buzz-auth/src/scope.rs`, `crates/buzz-relay/src/handlers/ingest.rs` — not yet a corpus node at this revision |
| Community provisioning's own request/response shape and validation rules | `crates/buzz-relay/src/handlers/community_provisioning.rs` — not yet a corpus node at this revision |
| Whether Block's internally-operated staging instance (reached through `squareup/sprout-oss` and `squareup/block-coder-tf-stacks`) configures `relay_operator_pubkeys` or the admin host any differently than the self-hosted path | not verifiable from this checkout — those repositories are external and not imported here |

**Expected but not verified when this node was written:**

- **No live relay was exercised end-to-end for any of the four mechanisms.** Every
  claim above is read from source and from each mechanism's own unit/integration
  tests, not observed against a running deployment.
- **Whether `relay_operator_pubkeys` and the admin `host` are ever the same value in a
  real deployment, or deliberately kept disjoint, was not established.** Both are
  independent configuration values; nothing in the code ties them together or asserts
  they should differ.
- **Whether a corpus node for community/channel moderation exists on `origin/launchpad`
  by the time this node merges was checked once, immediately before finalizing this
  front matter, and found absent** (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` names no `layers/authorization/*` node other than this one).
  If one lands first, a `references` edge from that node back to this one — not an edit
  to this node — is the way to connect them, per this corpus's own linking convention.
