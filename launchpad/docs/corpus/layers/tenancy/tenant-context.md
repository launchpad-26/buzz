---
id: layers-tenancy-tenant-context
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "TenantContext and CommunityId are both defined in buzz-core (crates/buzz-core/src/tenant.rs), a zero-I/O-dependency crate, specifically so the DB, auth, pub/sub, search, audit, media, and relay-wiring layers can all name a community the same way without depending on each other; TenantContext derives only Debug, Clone, PartialEq, Eq and holds two private fields, community: CommunityId and host: String, readable only through the community() and host() accessor methods."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "TenantContext deliberately has no Default and no Deserialize impl, and CommunityId::from_uuid and TenantContext::resolved are the only ways to construct either type; the module's own doc comment calls this 'a lint-and-review fence, not a compiler fence' because both constructors must stay pub for the host-resolution path to call them, so a determined caller elsewhere could still call them, and a migration-lint harness (not independently verified in this pass) is what actually forbids constructing a TenantContext outside host resolution and tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "TenantContext::resolved's own doc comment states it must be called only from the host-resolution path, and that every other consumer takes &TenantContext and reads it rather than constructing one; the doc comment on host() separately warns never to re-derive the community from the host string downstream, because the community is already fixed at construction."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "bind_community (crates/buzz-relay/src/tenant.rs) is the row-zero entry point that constructs a TenantContext: on a normalized, non-empty host that a HostResolver maps to Ok(Some(community)), it returns Ok(TenantContext::resolved(community, host)); an empty/whitespace host, an unmapped host (Ok(None)), or a resolver failure (Err) all become a BindError instead, so a TenantContext is never constructed from a request that failed to bind, and there is no default/fallback tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "bind_deployment_community constructs a TenantContext through the identical bind_community path for server-internal callers with no inbound request Host header (the git Smart-HTTP transport, the workflow execution sink, and startup tasks), by resolving the deployment's own configured relay_url host via relay_url_authority instead of a connection's Host header."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-core/src/tenant.rs"
  - statement: "There is no Extension<TenantContext> anywhere in the relay: on the WebSocket surface, nip11_or_ws_handler calls bind_community and, on success, passes the resulting TenantContext by value as a plain function argument through WebSocketUpgrade::on_upgrade into handle_connection, which passes it into handle_active_connection, which stores it as an owned tenant field on the per-connection ConnectionState struct that every WebSocket message handler thereafter reads from."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "On the REST/bridge HTTP surface there is no shared middleware layer that binds the tenant once; each handler independently calls bind_community inline near the top of its own function body (for example submit_event in crates/buzz-relay/src/api/bridge.rs) and then passes the resulting TenantContext onward by reference (&tenant) to the inner functions it calls."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "On the git Smart-HTTP surface, a custom Axum extractor bundles the tenant with the caller's authenticated identity: GitAuth is a struct holding pubkey and tenant: TenantContext, and its FromRequestParts::from_request_parts implementation calls bind_community and returns Ok(GitAuth { pubkey, tenant }); handlers such as info_refs then take auth: GitAuth as an extractor parameter and read auth.tenant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "On the media (Blossom) surface, two further custom extractors each embed a tenant: TenantContext field alongside surface-specific auth data -- AuthenticatedUpload (also holding auth_event, route_mode, and an upload permit) and the read-only MediaReadAuth -- and their FromRequestParts implementations likewise call bind_community internally rather than reading a shared request extension."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "Representative reads of an already-bound TenantContext use its community() accessor to scope a data operation to the right tenant -- for example crates/buzz-relay/src/connection.rs binds community_id = tenant.community() to check the community is still active and to key connection-registry bookkeeping, and crates/buzz-relay/src/api/git/transport.rs's info_refs handler passes auth.tenant.community() into authorize_git_read -- and its host() accessor for tenant-scoped labelling rather than re-resolution, for example crates/buzz-relay/src/api/media.rs passing Some(tenant.host()) into verify_blossom_auth_event for the NIP-98 host check."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/media.rs"
  - statement: "buzz-core's own unit tests construct a TenantContext directly and assert its accessors round-trip the values it was resolved with (tenant_context_exposes_resolution_inputs), and crates/buzz-relay/src/tenant.rs's redteam_attack2 test module proves bind_community never constructs a TenantContext for an empty or whitespace-only raw host even when a resolver is configured with an empty-string-keyed community mapping, plus a negative control that an ordinary unmapped non-empty host is unaffected."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "A separately merged corpus node states the row-zero invariant that TenantContext's construction and threading exist to carry -- that a request's community MUST be resolved from the connection host by the server and MUST NOT be supplied or overridden by the client -- and documents the full per-surface enforcement-point enumeration that this document does not restate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
  - statement: "A sibling corpus task documenting the host-to-CommunityId resolution mechanism itself (layers/tenancy/host-resolution.md, issue #1189) has an open, unmerged pull request at the time this node was authored, so no corpus node for that subject exists on the branch this node targets; the same is true of the sibling node on CommunityId and community identity generally (layers/identity/community-identity.md, issue #1104)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz PR #1839 (issue #1189, unmerged at authoring time) and PR #1811 (issue #1104, unmerged at authoring time)"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
---

# TenantContext: the per-request tenant carrier

## Definition

**`TenantContext`** is the small, immutable value type that carries one already-resolved
`CommunityId` (plus the normalized host it was resolved from) through the rest of a
request's or connection's lifetime, once host resolution has succeeded — it is the thing
every downstream handler reads to know which tenant it is operating on, and it is never
itself the mechanism that does the resolving.

## Boundaries: what this document is, and is not

**This is the carrier, not the resolution mechanism.** How a raw `Host` header becomes a
`CommunityId` — normalization, the database lookup, the fail-closed empty-host guard — is
a separate concern, owned by the sibling `host-resolution` node (issue #1189, not yet
merged at the time this node was authored — see Scope and omissions). This document starts
from the moment `bind_community` has already succeeded and a `TenantContext` exists.

**This is not `CommunityId` or community identity generally.** `TenantContext` wraps a
`CommunityId` (see "Relationship to `CommunityId`" below), but the identifier type itself —
its lifecycle, what a `communities` row means, archival and deletion — is the sibling
`community-identity` node's subject (issue #1104, not yet merged).

**This is not authorization inside a resolved community.** Once a handler holds a
`TenantContext`, membership, roles, and channel ACLs are separate checks this document does
not cover.

**This is not the row-zero invariant's justification.** *Why* the community must come from
the host and never from client input, and the full list of surfaces that enforce it, is
`architecture-principles-host-selects-community`'s subject; this document assumes that
invariant and documents the type that expresses it in code.

## Shape and construction

`TenantContext` is defined in `crates/buzz-core/src/tenant.rs` alongside `CommunityId`, in
a crate with zero I/O dependencies — deliberately, so the DB, auth, pub/sub, search, audit,
media, and relay-wiring layers can all name a community the same way without depending on
each other. It derives only `Debug`, `Clone`, `PartialEq`, `Eq` — no `Copy`, no `Hash`, no
`Ord`, no `Default`, no `Serialize`/`Deserialize` — and holds two private fields:
`community: CommunityId` and `host: String`, reachable only through the `community()` and
`host()` accessor methods.

The missing `Default` and `Deserialize` are a deliberate type-system expression of the
row-zero invariant: there is no way to parse or default-construct a `TenantContext` from
client input. The module's own doc comment is explicit that this is "a lint-and-review
fence, not a compiler fence" — `TenantContext::resolved` and `CommunityId::from_uuid` must
stay `pub` so the host-resolution path (in another crate) can call them, which means a
determined caller elsewhere technically could too; a migration-lint harness is named as the
thing that actually forbids constructing a `TenantContext` outside host resolution and
tests, though this document did not independently verify that harness's implementation.

The one production constructor, `TenantContext::resolved(community, host)`, is called from
exactly two places, both in `crates/buzz-relay/src/tenant.rs`:

- **`bind_community`** — the row-zero entry point. On a normalized, non-empty host that a
  `HostResolver` maps to `Ok(Some(community))`, it returns
  `Ok(TenantContext::resolved(community, host))`. An empty or whitespace-only host, an
  unmapped host (`Ok(None)`), or a resolver failure (`Err`) all become a `BindError`
  instead — a `TenantContext` is never constructed for a request that failed to bind, and
  there is no default or fallback tenant.
- **`bind_deployment_community`** — for server-internal callers with no inbound request
  `Host` header at all (the git Smart-HTTP transport, the workflow execution sink, and
  startup tasks). It resolves the deployment's own configured `relay_url` host via
  `relay_url_authority` and then runs the identical `bind_community` path, so it is not a
  separate default mechanism.

`TenantContext::resolved`'s own doc comment states it should be called *only* from the
host-resolution path, and that every other consumer takes `&TenantContext` and reads it
rather than constructing one. The `host()` accessor's doc comment separately warns never to
re-derive the community from the host string downstream — the community is already fixed
at construction; `host()` exists for NIP-05/audit labelling and the NIP-98 `u`-host check,
not for re-resolution.

## Threading through the request lifecycle

There is no `Extension<TenantContext>` anywhere in the relay, and the threading mechanism
is not uniform across surfaces — it differs by how each surface's request lifecycle is
shaped:

- **WebSocket.** `nip11_or_ws_handler` (`crates/buzz-relay/src/router.rs`) calls
  `bind_community` and, on success, passes the resulting `TenantContext` **by value** as a
  plain function argument through `WebSocketUpgrade::on_upgrade` into `handle_connection`,
  which passes it into `handle_active_connection`, which stores it as an owned `tenant`
  field on the per-connection `ConnectionState` struct
  (`crates/buzz-relay/src/connection.rs`). Every WebSocket message handler thereafter reads
  tenant scope from that field for the life of the connection.
- **REST/bridge HTTP.** There is no shared middleware layer that binds the tenant once for
  this surface; each handler independently calls `bind_community` inline near the top of
  its own function body (for example `submit_event` in
  `crates/buzz-relay/src/api/bridge.rs`) and then passes the resulting `TenantContext`
  onward **by reference** (`&tenant`) to the inner functions it calls.
- **git Smart-HTTP.** A custom Axum extractor bundles the tenant with the caller's
  authenticated identity: `GitAuth` (`crates/buzz-relay/src/api/git/transport.rs`) is a
  struct holding `pubkey` and `tenant: TenantContext`, and its
  `FromRequestParts::from_request_parts` implementation calls `bind_community` and returns
  `Ok(GitAuth { pubkey, tenant })`. Handlers such as `info_refs` take `auth: GitAuth` as an
  extractor parameter and read `auth.tenant`.
- **Media (Blossom).** Two further custom extractors in
  `crates/buzz-relay/src/api/media.rs` each embed a `tenant: TenantContext` field alongside
  surface-specific auth data — `AuthenticatedUpload` (also holding `auth_event`,
  `route_mode`, and an upload permit) and the read-only `MediaReadAuth` — and their
  `FromRequestParts` implementations likewise call `bind_community` internally rather than
  reading a shared request extension.

The common thread across all four is that every surface's *own* call to `bind_community` or
`bind_deployment_community` is what mints the `TenantContext` for that request or
connection; nothing threads a pre-bound tenant in from outside through a generic mechanism
like an Axum `Extension`.

## Representative read call sites

- `crates/buzz-relay/src/connection.rs` binds `community_id = tenant.community()` to check
  the community is still active and to key connection-registry bookkeeping for the life of
  the WebSocket connection.
- `crates/buzz-relay/src/api/git/transport.rs`'s `info_refs` handler passes
  `auth.tenant.community()` into `authorize_git_read` to scope the repository-read
  authorization check to the bound tenant.
- `crates/buzz-relay/src/api/media.rs` passes `Some(tenant.host())` into
  `verify_blossom_auth_event` for the NIP-98 `u`-host check — a `host()` read, not a
  `community()` read, and used for label/verification purposes rather than to re-derive the
  tenant.

## Relationship to `CommunityId`

`TenantContext` **contains** a `CommunityId` as a private field; it does not replace or
extend it. `CommunityId` is the opaque `Uuid` newtype (`Copy`, `Hash`, `Ord`) used directly
as the DB/Redis scoping key everywhere a community must be named as a value on its own —
`TenantContext` is not itself `Copy`, is not used as a map key, and is not passed to
storage-layer calls in place of a `CommunityId`; callers read `tenant.community()` to get
the `CommunityId` that a storage or scoping call actually wants. The `host: String` field
that `TenantContext` additionally carries has no equivalent on `CommunityId` at all — it
exists only to record which normalized host this particular resolution came from, for
labelling and the NIP-98 check described above.

## Related material (linked, not duplicated)

- `architecture-principles-host-selects-community` — the row-zero invariant that
  `TenantContext`'s construction and threading exist to carry: the community MUST be
  resolved from the connection host by the server and MUST NOT be supplied or overridden by
  the client, with the full per-surface enforcement-point list.
- `crates/buzz-core/src/tenant.rs` and `crates/buzz-relay/src/tenant.rs` — the
  implementation: `CommunityId`, `TenantContext`, `bind_community`,
  `bind_deployment_community`.
- `layers/tenancy/host-resolution.md` (issue #1189) — the sibling node on the mechanism
  that produces the `CommunityId` a `TenantContext` wraps. Not yet merged at the time this
  node was authored (open PR #1839), so no `relationships` edge targets it; this document
  points to it in prose only, per `AGENTS.md`'s rule that an edge may only name a node that
  already exists on the branch being merged into.
- `layers/identity/community-identity.md` (issue #1104) — the sibling node on `CommunityId`
  and community identity generally. Also not yet merged (open PR #1811); same prose-only
  treatment as above.

## Scope and omissions

**This document covers** what `TenantContext` is, its derives and constructor, the
lint-and-review (not compiler) nature of its "cannot be built from client input" guarantee,
where and how it is constructed (`bind_community`, `bind_deployment_community`), how it
threads through each of the four surfaces read for this document (WebSocket, REST/bridge,
git Smart-HTTP, media), representative read sites, and its containment relationship to
`CommunityId`.

**It does not cover, and these are gaps rather than silence:**

- The host-to-`CommunityId` resolution algorithm itself (header extraction, normalization,
  the database lookup, the empty-host guard) — owned by the sibling `host-resolution` node.
- `CommunityId` and community identity generally, beyond how `TenantContext` contains one —
  owned by the sibling `community-identity` node once merged.
- Authorization inside a resolved community (membership, roles, channel ACLs).
- The migration-lint harness that is claimed to forbid constructing a `TenantContext`
  outside host resolution and tests — its doc-comment claim was read, but the harness's own
  implementation was not located or independently verified in this pass.

**Expected but not verified when this node was written:**

- Whether every surface that threads a `TenantContext` beyond the four read here (WebSocket,
  REST/bridge, git Smart-HTTP, media) — for example the huddle audio WebSocket door named by
  the principle node — follows one of these same four threading shapes, or a fifth, was not
  independently re-audited; the principle node's own enforcement-points list already claims
  coverage per-surface, and this document does not repeat that audit.
