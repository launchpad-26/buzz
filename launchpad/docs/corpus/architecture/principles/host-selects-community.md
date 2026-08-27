---
id: architecture-principles-host-selects-community
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The row-zero invariant is stated as: req.community = resolve_host(connection.host), bound at connection establishment, before any WebSocket EVENT/REQ, REST handler, media handler, git transport handler, webhook handler, workflow side effect, search query, or pub/sub fan-out path observes tenant data."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "bind_community is the single row-zero entry point: it normalizes the raw host, resolves it through a HostResolver, and returns a fail-closed BindError on either an unmapped host or a lookup failure; there is deliberately no path that yields a default or fallback community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "An empty or whitespace-only raw host is rejected by bind_community before the resolver is ever consulted, even when a resolver is configured with an empty-host mapping; a red-team regression test (redteam_attack2) asserts this for both an empty string and a whitespace-only string."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "normalize_host is the one shared normalization rule applied on both sides of the fence: the communities.host column is stored already-normalized, and host resolution normalizes the incoming Host header with the same function before lookup, so case, a trailing FQDN-root dot, and a default port (:80/:443) can never split one tenant into two, while a non-default port is preserved as a legitimate distinct selector."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "The communities table carries a UNIQUE INDEX on lower(host) as a belt-and-suspenders database constraint on top of the shared normalize_host rule, so Relay.Example and relay.example can never become two tenant rows even if a writer forgot to normalize."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "bind_community (or bind_deployment_community for paths with no inbound Host header) is called as the tenant-establishing step at the start of the externally reachable relay surfaces: the WebSocket upgrade path, NIP-11/NIP-05 metadata, relay invites, the /events, /query, /count and moderation REST bridge, git smart-HTTP transport, media upload/read, workflow run listing, the huddle audio WebSocket, and relay admin feedback ingestion."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/api/nip05.rs"
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/api/workflows.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/api/admin/mod.rs"
  - statement: "The WebSocket upgrade handler binds the connection to its community from the request host before calling WebSocketUpgrade::from_request, and rejects with a generic 404 body ('relay: no community is configured for this host') on any bind failure, so no frame is ever read on an unbound connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The NIP-11 relay-info document is deliberately served before host binding and stays fail-open, so an unmapped host still receives the document with host-scoped fields (such as the community icon) simply absent, rather than a generic bind rejection; this keeps the document itself from acting as an oracle for which hosts are mapped."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "docs/multi-tenant-conformance.md"
  - statement: "bind_deployment_community exists for server-internal paths that have no inbound request Host header at all -- the git smart-HTTP transport, the localhost pre-receive hook callback, the workflow execution sink, and startup tasks -- and resolves the deployment's own relay_url host through the same fail-closed bind_community path rather than a separate default/fallback mechanism; an unmapped relay_url host fails exactly like any other unmapped host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "TenantContext has no Default and no Deserialize implementation and can only be constructed via TenantContext::resolved, so a community cannot be parsed directly from client-supplied request data; a CommunityId can only originate from CommunityId::from_uuid, which requires a UUID the server already trusts (e.g. read back from the communities table during host resolution)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "At the recorded revision, every non-test call site of TenantContext::resolved sits inside code that has already derived its community from a trusted source: bind_community's own resolver result, buzz-admin's community lookup, community/workflow provisioning after a DB read, and startup/admission paths that mint the deployment's own context -- none of them parse a community id out of unauthenticated client request data."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-relay/src/api/operator.rs"
      - "crates/buzz-relay/src/handlers/community_provisioning.rs"
      - "crates/buzz-relay/src/admission.rs"
    confidence: 0.6
  - statement: "The doc comment on buzz-core's tenant module states plainly that this is a lint-and-review fence, not a compiler fence: TenantContext::resolved and CommunityId::from_uuid are pub so the host-resolution path in another crate can call them, which means a determined caller elsewhere could call them too; the type system removes only the accidental path (deserializing a client-chosen community), and a deliberate misuse is meant to be caught by review, not the compiler."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "No script or CI check matching the name 'migration-lint harness' -- which crates/buzz-relay/src/tenant.rs's doc comment describes as forbidding TenantContext construction outside host resolution and tests -- was found under scripts/, .github/workflows/, or crates/buzz-conformance/ in this checkout; a repository-wide grep for row_zero/row-zero/RowZero outside that doc comment and one seeding script returned nothing further."
    entry_class: FACT
    evidence:
      - "grep(pattern='row_zero|row-zero|RowZero', scope='scripts/,.github/workflows/,crates/buzz-conformance/') -> only scripts/seed-local-community.sh matches"
  - statement: "A live end-to-end test connects two WebSocket clients to hosts A and B, then forges a NIP-42 AUTH event on the B-bound connection whose relay tag names host A's URL; the per-tenant host check rejects the cross-host forgery, and the comment records that this same forgery passed before the fix (when the check compared against the single process-wide state.config.relay_url instead of the per-connection bound host)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs"
  - statement: "The buzz-conformance test fixtures encode the row-zero terminology directly: an auth_check action carries both a claimed_community (from client-supplied event data) and, in state_after, a resolved_community and bound_host, modelling the distinction between what a client claims and what the host binding actually resolved."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/tests/fixtures/bad_host_channel_mismatch.jsonl"
  - statement: "The multi-tenant conformance checklist's migration gates require that every externally reachable handler obtain TenantContext from host binding before reading request body data that can cause tenant effects, but the checklist itself is prose, not an automated check; per the FACT above, no repository-wide automated gate enforcing that specific property was located, so its enforcement is presently by per-call-site test coverage and review rather than a single mechanical check."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
---

# Principle: the request host is the sole community selector (row zero)

## The invariant

**A request's community MUST be resolved from the connection's host by the server,
and MUST NOT be supplied, influenced, or overridden by the client.** Concretely:

> `req.community = resolve_host(connection.host)`, bound at connection or request
> establishment, before any handler observes tenant data.

An unknown or unmapped host **MUST** fail closed with a generic rejection. There is
**no** default or fallback community: a lookup that finds no matching host and a
lookup that fails outright (for example a database error) both produce the same
kind of rejection, never a degraded-but-working tenant.

A client-supplied signal that looks like a community selector -- a NIP-98 or API
token's community stamp, or an event's `h` tag -- **MAY** narrow or authenticate
what the connection is allowed to do inside the host-resolved community, but
**MUST NOT** override which community that is. A token whose stamped community
disagrees with the host-resolved community is rejected, not reconciled in the
token's favor.

This is the invariant Buzz's own conformance documentation names "row zero":
the one fact every other tenant-scoping rule in the system is built on top of.

## Scope: what this governs, and what it does not

**In scope.** Every externally reachable surface that can read or write
tenant-scoped data: the WebSocket upgrade and its `EVENT`/`REQ`/`COUNT` traffic,
the `/events`, `/query`, `/count` and moderation REST bridge, NIP-11/NIP-05
metadata, relay invites, git smart-HTTP transport, media upload/read, workflow
run listing and webhook/schedule triggers, the huddle audio WebSocket, and relay
admin feedback ingestion. At the recorded revision these all call `bind_community`
(or, for server-internal paths with no inbound `Host` header -- git's pre-receive
hook callback, the workflow execution sink, and startup -- `bind_deployment_community`,
which resolves the deployment's own `relay_url` host through the identical
fail-closed path rather than a separate default).

**Not in scope.** This node states the selection invariant itself: which
community a request belongs to, and that the host alone decides it. It does not
restate the full per-surface conformance table (schema shape, index scoping,
Redis key prefixing, and so on for each of channels, search, pub/sub, media,
git, and audit) -- that lives in `docs/multi-tenant-conformance.md` and is
linked, not duplicated, below. It also does not cover *authorization* inside a
resolved community (membership, roles, channel ACLs) -- only *which* community
a request is scoped to before any of that authorization logic runs.

**Applies to every operation**, not only reads: event submission, channel
creation, media upload, git push, workflow trigger firing, and administrative
provisioning are all bound to `req.community` the same way a read is. The
single-community deployment is the degenerate case of the same rule: one
configured host resolves to the one default community, so an existing
single-tenant deployment observes no behavior change.

## Enforcement points and observable failure behavior

**The mechanism.** `bind_community` (`crates/buzz-relay/src/tenant.rs`) is the
one row-zero entry point. It normalizes the raw host with
`buzz_core::tenant::normalize_host` -- the single rule shared by both the
`communities.host` storage side and the lookup side, so case, a trailing FQDN
root dot, and a default port can never split one tenant into two, while a
non-default port is kept as a legitimate distinct selector -- then resolves the
normalized host through a `HostResolver`. An empty or whitespace-only raw host
is rejected *before* the resolver is ever consulted, so a misconfigured
empty-host row in `communities` (the schema does not forbid one) cannot be
reached by a request with a missing `Host` header.

**Where it is called.** At the start of every in-scope surface listed above,
before any tenant data is read: most visibly, the WebSocket upgrade handler
binds the connection's community immediately before calling
`WebSocketUpgrade::from_request`, so no `EVENT`/`REQ` frame is ever read on an
unbound connection.

**One deliberate exception, and why it does not weaken the invariant.** The
NIP-11 relay-info document is served *before* host binding and stays fail-open:
an unmapped host still receives the document, with host-scoped fields such as
the community icon simply absent. This is not a bypass of row zero -- NIP-11
carries no tenant data write or scoped read -- it exists so the document itself
cannot be used to probe which hosts are mapped on a deployment (a fail-closed
NIP-11 would let an attacker distinguish "unmapped" from "mapped" by the shape
of the response).

**Observable failure behavior.** A host that fails to bind -- unmapped, or a
lookup error such as a database outage -- produces a **generic** rejection that
does not distinguish the two cases and does not echo the requested host back.
At the WebSocket upgrade path this is HTTP 404 with the body `"relay: no
community is configured for this host"`. The generic shape is deliberate: an
unauthenticated caller must not be able to enumerate which hosts exist on a
deployment by observing different error shapes for "wrong host" versus "our
database is down."

**Type-level backstop, and its honest limit.** `TenantContext` has no `Default`
and no `Deserialize`, so a community cannot be parsed directly out of
client-supplied request data, and a `CommunityId` can only be minted from a
UUID the server already trusts. This closes the *accidental* path (a handler
deserializing a client-chosen community by mistake). It is explicitly **not** a
compiler-enforced guarantee that no code path ever constructs a `TenantContext`
outside host resolution: `TenantContext::resolved` and `CommunityId::from_uuid`
are `pub`, because the host-resolution code lives in a different crate
(`buzz-relay`) than the type itself (`buzz-core`) and needs to call them. The
module's own doc comment names this directly as "a lint-and-review fence, not a
compiler fence." At the recorded revision, every non-test call site of
`TenantContext::resolved` found in the repository sits inside code that already
derived its community from a trusted source (a resolver result, a DB read, a
startup/admission path) rather than from unauthenticated client input -- but
this was established by reading each call site, not by an automated check, so
it is recorded here as an inference, not a fact.

## Verification and conformance

**A live regression test exercises the cross-host attack directly.** Two
WebSocket clients connect to hosts A and B; a client on the B-bound connection
forges a NIP-42 `AUTH` event whose `relay` tag names host A's URL. The
per-connection host check rejects it. The test's own comment records that this
exact forgery passed before the fix, when the check compared against a single
process-wide configured relay URL instead of the connection's own bound host --
i.e. the property this test guards is not hypothetical; it was previously
broken. See `crates/buzz-test-client/tests/nip42_host_binding_live.rs`.

**A red-team unit test guards the empty-host fence.** `bind_community`'s tests
include a `redteam_attack2` module that configures a resolver with an
`""`-keyed mapping (schema-legal, since `communities` has no CHECK against an
empty host) and asserts that both an empty and a whitespace-only raw host still
fail closed with the same generic `UnmappedHost` error, never reaching that
row. See `crates/buzz-relay/src/tenant.rs#symbol=redteam_attack2`.

**The conformance model names the same distinction in its fixtures.**
`buzz-conformance`'s trace fixtures record both a `claimed_community` (from
client-supplied event data) and a `resolved_community` plus `bound_host` (from
host binding) on the same action, so a mismatch between what a client claims
and what the connection actually resolved to is a first-class, checkable shape
in the conformance model rather than an implicit assumption. See
`crates/buzz-conformance/tests/fixtures/bad_host_channel_mismatch.jsonl`.

**What is stated but not automatically enforced.** `docs/multi-tenant-conformance.md`'s
migration gates state, as a requirement, that "every externally reachable
handler obtains `TenantContext` from host binding before reading request body
data that can cause tenant effects." At the recorded revision this document
did not find a repository-wide automated check (lint, CI job, or test) that
verifies *that* property across all handlers as a single mechanical gate -- a
targeted search for `row_zero`/`row-zero`/`RowZero` under `scripts/`,
`.github/workflows/`, and `crates/buzz-conformance/` turned up only
`scripts/seed-local-community.sh`, which seeds a community rather than checking
this property. The property currently holds by virtue of every in-scope handler
individually calling `bind_community` (verified per-surface above) plus code
review, not by one automated gate that would catch a new handler omitting the
call. This is recorded as a known verification gap, not resolved by this
document.

**One further unresolved reference.** `crates/buzz-relay/src/tenant.rs`'s
module doc comment additionally asserts that "the migration-lint harness
forbids constructing a `TenantContext` outside host resolution and tests." No
script or CI configuration matching that description was located in this
checkout at the recorded revision. This document does not assert the harness
exists, and does not assert it does not -- only that it could not be found by
search, which is itself worth recording so a later reader does not rely on a
harness that may never have been built, or may live outside this repository.

## Related material (linked, not duplicated)

- `docs/multi-tenant-conformance.md` -- the full per-surface conformance table
  (schema/index/Redis-key scoping for channels, search, pub/sub, media, git,
  audit, and more) that this node's invariant underlies. This node states the
  selector rule; that document states what every scoped surface must do once
  the selector has run.
- `migrations/0001_initial_schema.sql` -- the `communities` table and its
  `UNIQUE INDEX ON communities (lower(host))`, the durable storage side of the
  same normalization rule `normalize_host` applies on the read side.
- `crates/buzz-core/src/tenant.rs` and `crates/buzz-relay/src/tenant.rs` -- the
  implementation: `TenantContext`, `CommunityId`, `normalize_host`,
  `bind_community`, and `bind_deployment_community`.

No `relationships` entries are declared in this node's front matter. At the
recorded revision no other `architecture`/`principles` corpus node is merged,
so any `relationships[].target` would name an id no loaded node carries, which
`node.schema.json` treats as a hard validation error. This is the same
constraint `standards/confidence.md` recorded for the same reason, and the same
resolution: add the edge once a sibling node exists to point at.

## Scope and omissions

**Expected but not verified when this node was written:**

- Whether an automated gate for "every externally reachable handler calls
  `bind_community` first" exists anywhere outside this repository (for
  example, in a separate CI configuration repo) was not checked -- only this
  checkout was searched.
- Whether the "migration-lint harness" named in `crates/buzz-relay/src/tenant.rs`'s
  doc comment once existed and was later removed, was always aspirational, or
  is implemented by a mechanism this search did not recognize, was not
  established.
- The full list of `bind_community`/`bind_deployment_community` call sites in
  the *Enforcement points* section above was assembled by grepping call sites
  in `crates/buzz-relay/src`, not by an exhaustive audit of every route
  registered in `crates/buzz-relay/src/router.rs`; a route added after this
  node's recorded revision that omits the call would not be caught by
  re-reading this document.
