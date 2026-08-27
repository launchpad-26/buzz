---
id: architecture-principles-community-is-security-boundary
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Every request's community is bound exactly once, at connection or request establishment, by resolving the connection's Host header through `bind_community`, before any handler observes tenant data — the module's own doc comment names this 'row-zero host binding'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "`bind_community` fails closed: an unmapped host, an empty or whitespace-only host, and a resolver-lookup error are all rejected through `BindError`, and none of these paths yields a default or fallback community — verified both in the function body and in its `unmapped_host_fails_closed`, `lookup_error_fails_closed_not_default_tenant`, and `redteam_attack2::*` unit tests."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "`CommunityId` is documented as never constructed from client input: `CommunityId::from_uuid`'s doc comment states there is deliberately no `community_id` parsed from client input anywhere, and `TenantContext::resolved`'s doc comment restricts its use to the host-resolution path — every other call site takes `&TenantContext` and only reads it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "On the WebSocket door, `router.rs` calls `bind_community` before `WebSocketUpgrade::from_request`, so no frame is ever read on an unbound connection; on bind failure it returns a fixed `404 Not Found` body, 'relay: no community is configured for this host', that does not echo the requested host or distinguish an unmapped host from a lookup failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`bind_community` is called at the start of every other observed non-WebSocket request surface — admin, NIP-11, NIP-05, relay invites, git Smart HTTP transport, the REST event/query/count bridge, media upload and download, the audio/huddle handler, and workflow webhooks — 24 call sites across 11 files, all before any tenant-scoped work begins."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/admin/mod.rs"
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/api/nip05.rs"
      - "crates/buzz-relay/src/api/invites.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/media.rs"
      - "crates/buzz-relay/src/audio/handler.rs"
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/api/workflows.rs"
      - "crates/buzz-relay/src/tenant.rs"
  - statement: "At the storage layer, `EventQuery::for_community` requires a `CommunityId` argument to construct a query filter at all, so an event query cannot be built without a resolved community; `buzz-db`'s channel functions write and read `channels` and `channel_members` rows keyed by the same `community_id` parameter (including the `ON CONFLICT (community_id, channel_id, pubkey)` membership upsert)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/event.rs"
      - "crates/buzz-db/src/channel.rs"
  - statement: "A client-supplied `#h` channel tag is checked against the host-derived community rather than honored as an alternate selector: `check_channel_membership` resolves membership as `is_member_cached(tenant.community(), ch_id, pubkey_bytes)`, where `tenant` is the connection's `TenantContext` and never the tag; a caller who is not a member and the channel is not `open` is rejected with the fixed string `restricted: not a channel member`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "`NOSTR.md` states the same rule in prose: Buzz treats the relay URL/domain as authoritative for the community, the Nostr wire format does not grow a tenant tag, and client-supplied `#h` tags still name channels/groups but are checked against the host-derived community."
    entry_class: FACT
    evidence:
      - "NOSTR.md"
  - statement: "The `communities` table enforces one canonical host-to-community mapping at the database level — migration `0001_initial_schema.sql` creates `CREATE UNIQUE INDEX idx_communities_host ON communities (lower(host))` — and `normalize_host` is the single shared normalization rule applied to both the stored key and every incoming Host header before lookup, so case, trailing-dot, and default-port variants of one host resolve to one community rather than splitting into two."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-core/src/tenant.rs"
  - statement: "`docs/multi-tenant-conformance.md` records the same contract as the deployment's own 'row zero' specification: `req.community = resolve_host(connection.host)`, bound before any WebSocket EVENT/REQ, REST handler, media handler, git transport handler, webhook handler, workflow side effect, search query, or pub/sub fan-out path observes tenant data, and states that NIP-98/API-token community stamps may narrow or authenticate authority but never override the host-derived community."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "The repository carries an executable A/B isolation conformance suite for this invariant, `conformance_multitenant.rs`, including `unmapped_host_fails_closed_generically` (asserts the unmapped-host 404, the non-echoing body, and that a raw WebSocket handshake to an unmapped host is rejected at the upgrade rather than admitted and bound later) and `client_supplied_community_cannot_override_host` (asserts that a channel existing only in community B is rejected, not silently admitted, when claimed via `#h` from a connection bound to community A)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "Every test in that suite carries `#[ignore]` and the file's header doc comment states they require a running multi-tenant relay with two live host-to-community mappings sharing one database and Redis, selected only with `cargo test -p buzz-test-client --test conformance_multitenant -- --ignored`; this node was authored without standing up that two-host deployment, so the suite's current pass/fail status against this revision was not executed or observed while writing this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "Because `CommunityId` cannot be constructed by parsing client input anywhere in the codebase, and every scoped storage call inspected above (event queries, channel writes, channel-membership checks) requires one, defeating this boundary from a client would require finding a code path that fabricates or bypasses `TenantContext` entirely rather than crafting a malicious request payload — a materially harder bar than a typical input-validation bypass."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/tenant.rs"
      - "crates/buzz-db/src/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.6
  - statement: "Issue #689's category-specific definition of done requires this node to state the invariant as one unambiguous property using MUST/MUST NOT only where normative, explain its scope, name enforcement points and observable failure behavior, and link a verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#689 definition of done"
---

# Principle: a community is the security boundary

## The invariant

**A community, resolved solely from the connection's Host header at connection or
request establishment, MUST be the sole authority for every tenant-scoped operation on
that connection or request. No signal supplied by the client — an `h` tag, an API
token's community stamp, a NIP-98 URL, or any other client-controlled field — MUST
ever override, widen, or substitute for the host-derived community.**

Equivalently: `req.community = resolve_host(connection.host)`, bound once, before any
handler observes tenant data, and nothing downstream is entitled to name a different
community than the one that binding produced.

This is a security boundary in the ordinary sense — the property that makes it
meaningful to run more than one community on one relay deployment without one
community's data, membership, or side effects becoming reachable from another. It is
not a convenience default; it is the thing every other multi-tenant guarantee in the
codebase is built on top of.

## Scope: what this governs

**Applies to:** every external request or connection the relay accepts — WebSocket
`EVENT`/`REQ`/`COUNT` frames, the REST event/query/count bridge, media upload and
download, git Smart HTTP, workflow webhooks, relay invites, NIP-05/NIP-11 metadata,
the admin surface, and the audio/huddle handler. See `docs/multi-tenant-conformance.md`
for the full per-surface obligation table this principle is drawn from.

**Applies within a community, not merely between them:** a client-supplied `#h`
channel tag is checked *against* the host-derived community's own channel set, not
against some other community's. It narrows which channel inside the already-resolved
community is meant; it can never cause a different community to be resolved.

**Does not govern:** internal server-to-server paths that have no inbound `Host`
header at all — the git pre-receive hook callback, startup community seeding, and
similar server-internal call sites. These resolve the deployment's own community from
its configured relay URL through the same fail-closed binding function, not through a
separate or weaker path — see `bind_deployment_community` in the enforcement points
below — so the invariant still holds there, it is just bound from a different input.

## Enforcement points

| Point | What it does |
|---|---|
| `bind_community` (`crates/buzz-relay/src/tenant.rs`) | The single seam every request surface calls. Normalizes the Host header, looks it up, and returns a `TenantContext` on success or a generic `BindError` on any failure — unmapped host, empty host, or a lookup error alike. |
| `router.rs`'s WebSocket door | Calls `bind_community` before `WebSocketUpgrade::from_request`, so a socket that fails to bind never has a frame read from it. |
| 24 REST/media/git/workflow call sites (11 files, listed in the evidence ledger) | Each calls `bind_community` before doing any tenant-scoped work, so the same fail-closed rule applies uniformly rather than being re-implemented per surface. |
| `EventQuery::for_community` (`crates/buzz-db/src/event.rs`) | Requires a `CommunityId` to construct a query filter at all — there is no query-building path that omits it. |
| `check_channel_membership` (`crates/buzz-relay/src/handlers/ingest.rs`) | Resolves a `#h`-tagged channel against `tenant.community()`, the connection's own bound community, never against a value read from the tag. |
| `communities` table's unique index on `lower(host)` (`migrations/0001_initial_schema.sql`) | Guarantees, at the database level, that normalized host variants cannot be split across two different community rows. |

## Observable failure behavior

A request that fails to bind is rejected **generically**: the same response — an HTTP
`404 Not Found` with the fixed body `"relay: no community is configured for this
host"` on the WebSocket door — is returned whether the host is simply unmapped or the
lookup itself failed, and the response never echoes the requested host. This is
deliberate: an unauthenticated caller must not be able to use the rejection to probe
which hosts or communities exist on a deployment. A rejected `#h` override attempt
inside an already-bound community surfaces as the ordinary channel-membership error,
`"restricted: not a channel member"` — the same string a legitimate non-member gets,
so an override attempt is not distinguishable from an unrelated permission failure.

## Verification

The repository's executable conformance mechanism for this invariant is
`crates/buzz-test-client/tests/conformance_multitenant.rs`, an A/B isolation suite
that runs two host-to-community mappings against one relay deployment and asserts
that no tenant-observable state crosses between them. The two rows most directly on
this invariant are `unmapped_host_fails_closed_generically` and
`client_supplied_community_cannot_override_host` (see the evidence ledger for what
each asserts).

**This verification was not run while authoring this node.** Every test in that suite
carries `#[ignore]` and requires a live relay with two real host mappings sharing one
database and Redis instance — infrastructure this documentation task neither stood up
nor was in scope to stand up. What is verified above is the *presence and shape* of
the enforcement code and of the test assertions that target it, read directly from the
source; whether those assertions currently pass against this revision is an open
verification gap, not a claim this node makes.

## Scope and omissions

**Not covered here, and out of scope for this node:**

- The full per-surface obligation table (search, git object storage, presence,
  pub/sub key prefixing, audit log labelling, and so on) — that is
  `docs/multi-tenant-conformance.md`'s job, and this node links it rather than
  reproducing it.
- The mechanics of `normalize_host`'s specific normalization rules (case folding,
  trailing-dot stripping, default-port handling) — see `crates/buzz-core/src/tenant.rs`
  directly; restating them here would drift the moment that function's doc comment
  changes and nothing would catch it.
- Whether every row in `docs/multi-tenant-conformance.md`'s obligation table is
  currently implemented versus still aspirational. This node verified the row-zero
  binding mechanism and a representative sample of downstream call sites (event
  queries, channel writes, channel membership) directly in code; it did not audit
  every surface in that table (for example Redis key prefixing or git object-store
  pointer scoping) and makes no claim about them.

**Expected but not verified when this node was written:**

- Whether `conformance_multitenant.rs`'s `#[ignore]`-gated assertions currently pass
  against this revision — see *Verification* above.
- Whether any request surface added after this revision correctly threads
  `TenantContext` through to its storage calls; this node documents the invariant and
  its current enforcement points, not a guarantee that every future surface complies.
