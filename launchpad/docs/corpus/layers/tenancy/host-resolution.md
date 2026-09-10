---
id: layers-tenancy-host-resolution
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
  - statement: "The WebSocket/NIP-11 handler reads the raw connection host from the inbound `Host` header, falling back to an empty string when the header is absent or not valid UTF-8/ASCII text — there is no separate 'missing header' code path; a missing header and an empty header produce the identical raw_host value."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "normalize_host is the one shared normalization rule: it trims surrounding whitespace, lowercases the host, strips a trailing `:443` or `:80` suffix (and only that exact suffix, so IPv6 literals like `[::1]` are left untouched), and strips a single trailing FQDN-root dot. A non-default port is preserved as a legitimate distinct selector."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "bind_community rejects an empty or whitespace-only raw host with the same UnmappedHost error BEFORE the HostResolver is ever consulted, specifically so a misconfigured empty-host row in the communities table (the schema does not forbid one) can never be reached by a request with a missing or unreadable Host header."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "A dedicated red-team regression test module (redteam_attack2) asserts that both an empty raw host and a whitespace-only raw host fail closed with UnmappedHost even when the resolver is configured with an empty-string-keyed community mapping, and a negative control confirms an ordinary non-empty unmapped host is unaffected by the fix."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "The production HostResolver looks up a normalized host with an exact, case-folded equality comparison (`WHERE lower(host) = lower($1)`) restricted to communities whose lifecycle state is live (`archived_at IS NULL AND deleted_at IS NULL AND deletion_state = 'active'`); there is no LIKE, regex, or other pattern-matching lookup anywhere in this query."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Host resolution therefore supports no wildcard or subdomain pattern: each community maps to exactly one literal, already-normalized host string, and a deployment that wants one community per subdomain (e.g. `*.example.com`) needs one `communities` row per subdomain, not a pattern rule."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "migrations/0001_initial_schema.sql"
    confidence: 0.85
  - statement: "The communities table carries a UNIQUE INDEX on lower(host) as the durable-storage half of the same case-fold rule normalize_host applies on the lookup side, so a lookup and a stored row can never disagree on case."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "A community can be archived (archived_at set, migration 0016) or placed into a non-'active' deletion_state (quiescing/fenced/tombstone, migration 0029); either state removes it from lookup_community_by_host's result set, so a host that used to resolve stops resolving and produces the identical generic UnmappedHost rejection as a host that was never mapped."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "migrations/0016_community_archival.sql"
      - "migrations/0029_community_deletion.sql"
  - statement: "The three possible outcomes of a lookup -- host maps to a community, host is valid but maps to nothing, and the lookup itself fails (e.g. database unreachable) -- are Ok(Some), Ok(None), and Err respectively on the HostResolver trait, and bind_community turns the latter two into the same BindError family; there is no code path that yields a default or fallback community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "The WebSocket/NIP-11 handler calls bind_community immediately after content-negotiating away the NIP-11 JSON case, and BEFORE calling WebSocketUpgrade::from_request, so no WebSocket frame is ever read on a connection that failed to bind; a bind failure of either kind returns HTTP 404 with the fixed body 'relay: no community is configured for this host', never echoing the requested host or distinguishing which failure occurred."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "bind_deployment_community exists for server-internal paths with no inbound request Host header at all, and resolves the deployment's own relay_url host through the identical fail-closed bind_community path -- via relay_url_authority, which extracts host-plus-non-default-port in the same normalized shape normalize_host produces for a live request, including correct IPv6 bracket handling -- rather than a separate default/fallback mechanism."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-core/src/tenant.rs"
  - statement: "is_admin_host, which gates the separate deployment-admin HTTP surface, is an unrelated exact-string comparison of the raw Host header against one configured admin host; it does not call normalize_host, does not consult the communities table, and does not produce a CommunityId -- it is not part of tenant host resolution and must not be conflated with it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/auth.rs"
  - statement: "A separately merged corpus node states the row-zero invariant this document's mechanism implements -- that a request's community MUST be resolved from the connection host by the server and MUST NOT be supplied or overridden by the client -- and explicitly names the full per-surface conformance table and implementation detail as material it defers rather than restates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/host-selects-community.md"
  - statement: "A sibling corpus task documenting community identity (layers/identity/community-identity.md, issue #1104) has an open, unmerged pull request at the time this node was authored, so no corpus node for that subject exists on the branch this node targets."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1104, tracked via its open pull request #1811 (unmerged at authoring time)"
relationships:
  - type: references
    target: architecture-principles-host-selects-community
---

# Host resolution: the `Host` header to `CommunityId` mechanism

## Definition

**Host resolution** is the mechanism by which the relay turns the inbound connection's
`Host` header into a `CommunityId`: extract the raw header, normalize it into a
canonical form, and look it up against the `communities` table's exact-match, case-folded
host index, producing either a resolved tenant or a generic fail-closed rejection.

## Boundaries: what this document is, and is not

**This is mechanism, not invariant.** `architecture-principles-host-selects-community`
already states and defends the *invariant* -- host alone selects the community, the
client can never override it, an unmapped host fails closed -- across every externally
reachable surface. This document does not restate that invariant or its per-surface
enumeration. It documents the one function call chain that invariant runs through:
header → normalized string → database row → `CommunityId`.

**This is not authorization inside a resolved community.** Once `bind_community`
succeeds, membership, roles, and channel ACLs are separate concerns this document does
not cover.

**This is not the deployment-admin host check.** `is_admin_host`
(`crates/buzz-relay/src/api/admin/auth.rs`) compares the raw `Host` header against one
configured admin authority with a plain string equality. It never calls
`normalize_host`, never touches the `communities` table, and never produces a
`CommunityId`. It gates an entirely separate, non-tenant-scoped HTTP surface and is
named here only so a reader does not mistake it for tenant host resolution.

**This is not the full per-surface conformance table.** Schema/index/Redis-key scoping
for channels, search, pub/sub, media, git, and audit once a `CommunityId` exists lives
in `docs/multi-tenant-conformance.md` and is linked, not duplicated, below.

## The resolution algorithm

Four steps, run in this order for every externally reachable, host-bound request:

1. **Extract the raw host.** The handler reads the `Host` header from the inbound
   request. A missing header, or one that fails to decode as a string, both collapse to
   an empty `raw_host` -- there is no separate "no header" branch downstream; an absent
   header and an empty one are indistinguishable from this point on.
   (`crates/buzz-relay/src/router.rs`)

2. **Normalize.** `normalize_host` (`crates/buzz-core/src/tenant.rs`) trims surrounding
   whitespace, lowercases the whole string (hosts are case-insensitive per RFC 3986),
   strips an exact trailing `:443` or `:80` suffix (a non-default port, and any IPv6
   literal such as `[::1]`, is left untouched because neither ends in that literal
   suffix), and strips a single trailing FQDN-root dot. `Relay.Example`,
   `relay.example.`, and `relay.example:443` all normalize to `relay.example`; they can
   never resolve to two different communities.

3. **Fail closed on empty before touching the resolver.** `bind_community`
   (`crates/buzz-relay/src/tenant.rs`) checks `host.is_empty()` immediately after
   normalization and returns `BindError::UnmappedHost` without ever calling
   `HostResolver::resolve_host`. This exists specifically because the `communities`
   schema does not forbid an empty-host row; without the guard, a request with a
   missing or blank `Host` header could bind to a misconfigured empty-host community.
   The `redteam_attack2` test module in the same file exercises exactly this: it
   configures a resolver with an `""`-keyed mapping and asserts both an empty and a
   whitespace-only raw host still fail closed, plus a negative control that an ordinary
   unmapped non-empty host is unaffected by the guard.

4. **Look up.** The `HostResolver` trait abstracts the lookup so `bind_community` is
   testable without a database; the production implementation is
   `impl HostResolver for buzz_db::Db`, which calls
   `Db::lookup_community_by_host` (`crates/buzz-db/src/lib.rs`). That query is an exact,
   case-folded equality match --
   `WHERE lower(host) = lower($1) AND archived_at IS NULL AND deleted_at IS NULL AND
   deletion_state = 'active'` -- against the `communities` table, which carries a
   `UNIQUE INDEX ON communities (lower(host))` (`migrations/0001_initial_schema.sql`) as
   the durable-storage half of the same case-fold rule. Three outcomes are possible on
   the `HostResolver` trait: `Ok(Some(id))` (resolved), `Ok(None)` (valid lookup, no
   match), and `Err(_)` (the lookup itself failed, e.g. the database is unreachable).
   `bind_community` maps `Ok(Some(_))` to a resolved `TenantContext` and folds the other
   two into `BindError::UnmappedHost` and `BindError::Lookup(e)` respectively --
   distinct variants internally, but every caller turns both into the same generic
   rejection. There is no code path that yields a default or fallback community.

## Where this runs in the request pipeline

The WebSocket/NIP-11 handler (`nip11_or_ws_handler`, `crates/buzz-relay/src/router.rs`)
calls `bind_community` immediately after the NIP-11-JSON content-negotiation branch and
**before** calling `WebSocketUpgrade::from_request` -- so no `EVENT`/`REQ` frame is ever
read on a connection whose host failed to bind. A bind failure of either kind (unmapped
or lookup error) produces `HTTP 404` with the fixed body `"relay: no community is
configured for this host"`; the requested host is never echoed back, and the two
failure kinds are not distinguished in the response, so an unauthenticated caller
cannot enumerate which hosts exist on a deployment or infer a database outage from the
response shape.

**One documented exception**, already covered by the principle node and not restated
here in full: the NIP-11 relay-info document is served *before* this binding step and
stays fail-open on an unmapped host, because it carries no tenant-scoped read or write.

**Server-internal paths with no inbound `Host` header at all** -- the git Smart-HTTP
transport's server-side hooks, the workflow execution sink, and startup tasks -- have no
connection host to resolve. For these, `bind_deployment_community`
(`crates/buzz-relay/src/tenant.rs`) resolves the deployment's own configured `relay_url`
host through the identical `bind_community` path, via `relay_url_authority`
(`crates/buzz-core/src/tenant.rs`), which extracts the URL's host plus any non-default
port in the same normalized shape `normalize_host` produces for a live request --
including preserving IPv6 brackets, which a bare `Url::host_str()` call would drop. This
is not a separate default mechanism: an unmapped `relay_url` host fails exactly like any
other unmapped host.

## Edge cases

**Missing or unparseable `Host` header.** Collapses to an empty `raw_host` at
extraction (step 1 above), which `normalize_host` leaves empty, which `bind_community`
rejects before ever consulting the resolver (step 3). The observable failure is
byte-identical to any other unmapped host -- there is no separate "no host" error shape
for a client to distinguish.

**Unknown/unmapped host.** A well-formed host that matches no row in `communities`
produces `Ok(None)` from the resolver, `BindError::UnmappedHost`, and the same generic
404. The host is never echoed back.

**No wildcard or subdomain matching.** The lookup is an exact, case-folded string
equality, not a pattern match -- there is no `LIKE`, regex, or subdomain-suffix rule
anywhere in `lookup_community_by_host` or the schema around it. A deployment that wants
one community per subdomain (for example `*.example.com`) needs one literal
`communities.host` row per subdomain; there is no single configuration that maps a
whole domain pattern to a resolution rule.

**Archived or mid-deletion communities.** `lookup_community_by_host` filters out any
row where `archived_at` is set or `deletion_state` is not `'active'` (archival added in
migration `0016_community_archival.sql`; the deletion state machine in
`0029_community_deletion.sql`). A host that used to resolve, once its community is
archived or enters deletion, stops resolving and produces the identical generic
`UnmappedHost` rejection as a host that was never mapped -- there is no distinct
"tenant existed but is gone" response.

**Lookup failure (e.g. database unreachable).** Surfaces as `Err(_)` on `HostResolver`,
`BindError::Lookup(e)` internally, but the same generic rejection externally as an
unmapped host -- fail-closed, never a default tenant, and not distinguishable from
"unmapped" by an unauthenticated caller.

## Related material (linked, not duplicated)

- `architecture-principles-host-selects-community` -- the row-zero invariant this
  mechanism implements: that the host alone selects the community, across every
  externally reachable surface, with the full per-surface enforcement-point list.
- `docs/multi-tenant-conformance.md` -- the full per-surface conformance table for what
  every scoped surface must do once a `CommunityId` has been resolved.
- `crates/buzz-core/src/tenant.rs` and `crates/buzz-relay/src/tenant.rs` -- the
  implementation: `normalize_host`, `relay_url_authority`, `HostResolver`,
  `bind_community`, `bind_deployment_community`.
- `layers/identity/community-identity.md` (issue #1104) -- the sibling node on
  `CommunityId` and community identity generally. Not yet merged at the time this node
  was authored (open PR #1811), so no `relationships` edge targets it; this document
  points to it in prose only, per `AGENTS.md`'s rule that an edge may only name a node
  that already exists on the branch being merged into.

## Scope and omissions

**This document covers** the exact algorithm that turns an inbound `Host` header into a
`CommunityId` (or a fail-closed rejection): header extraction, normalization, the
empty-host guard, the database lookup and its lifecycle filter, where this runs in the
request pipeline, and the edge cases -- missing header, unknown host, no
wildcard/subdomain support, and archived/deleting communities.

**It does not cover, and these are gaps rather than silence:**

- The row-zero invariant's full justification and its complete per-surface enumeration
  -- owned by `architecture-principles-host-selects-community`.
- The full per-surface conformance table (schema/index/Redis-key scoping once a
  `CommunityId` exists) -- owned by `docs/multi-tenant-conformance.md`.
- Authorization inside a resolved community (membership, roles, channel ACLs).
- `CommunityId` and community-identity concepts generally, beyond how one is minted by
  this resolution path -- owned by the sibling `community-identity` node once merged.

**Expected but not verified when this node was written:**

- Whether every externally reachable call site beyond the ones read for this
  document (`router.rs`'s `nip11_or_ws_handler`) also routes through
  `bind_community`/`bind_deployment_community` was not re-audited here; the principle
  node's own enforcement-points section already claims this per-surface, and repeating
  that audit would duplicate its evidence rather than add to it.
- Whether axum's `HeaderMap` lookup for the `Host` header name itself is
  case-insensitive at the HTTP-framework level (as HTTP header *names* generally are)
  was not independently verified by reading axum's source; this document only
  establishes what happens to the header *value* once obtained.
