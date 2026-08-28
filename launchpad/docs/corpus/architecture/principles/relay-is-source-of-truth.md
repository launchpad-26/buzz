---
id: architecture-principles-relay-is-source-of-truth
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
  - statement: "ARCHITECTURE.md states the relay is the single source of truth, that all reads and writes flow through it, and that there is no peer-to-peer event exchange, no gossip, and no replication."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:7"
  - statement: "ARCHITECTURE.md names this the key architectural principle a second time when describing crate composition: buzz-relay orchestrates buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit and buzz-workflow by calling them directly, those subsystem crates are isolated from each other, cross-subsystem coordination happens only through the relay, and in multi-community mode the relay also owns propagation of TenantContext."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:97"
  - statement: "CONTRIBUTING.md restates the same principle: all state flows through the event store, and crates communicate through the database and Redis pub/sub rather than through direct function calls across crate boundaries, with buzz-core's shared types as the sole exception."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md:379-382"
  - statement: "README.md summarizes the workspace as having a single source of truth: the relay."
    entry_class: FACT
    evidence:
      - "README.md:221"
  - statement: "buzz-search, buzz-audit, buzz-pubsub and buzz-media carry no dependency on buzz-db or on each other in their own Cargo.toml; buzz-workflow depends on buzz-db (the shared database-access crate) and buzz-deletion but not on buzz-pubsub, buzz-search, buzz-audit or buzz-media; buzz-relay's own Cargo.toml is the only manifest that imports buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit and buzz-workflow together."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/Cargo.toml"
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-pubsub/Cargo.toml"
      - "crates/buzz-media/Cargo.toml"
      - "crates/buzz-workflow/Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "The desktop Tauri backend's Cargo.toml carries no Postgres or database-client dependency, so the desktop client's only path to relay state is the relay's own WebSocket/HTTP surface."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml"
  - statement: "buzz-relay's row-zero host binding resolves req.community from the connection host before any handler (AUTH, EVENT, REQ, REST, media, git, search, workflow, or pub/sub) observes tenant data, and bind_community fails closed: an empty, unmapped, or lookup-erroring host returns BindError::UnmappedHost or BindError::Lookup, never a default community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:1-9"
      - "crates/buzz-relay/src/tenant.rs:71-92"
  - statement: "The unmapped_host_fails_closed unit test asserts that binding a host with no mapped community returns BindError::UnmappedHost rather than defaulting to any community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:243-248"
  - statement: "NIP-PL.md specifies that push delivery is a wake signal only -- never relay-supplied bytes, event ids, event content, URLs, ciphertext, or extensible custom data -- and that on wake the client reconnects and fetches authoritative events over normal REQ, because the relay remains the single source of truth even though push delivery is lossy and best-effort."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PL.md:22"
  - statement: "buzz-relay-mesh implements an inter-relay QUIC mesh -- a warm full mesh of authenticated connections with scuttlebutt membership gossip on a control substream -- but its own module documentation states that mesh membership is only a hint, that the Redis fenced generation is the arbiter, and that the crate grants no ownership."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/lib.rs:1-19"
  - statement: "buzz-relay-mesh was added by commit ccb021d71339009aabedc383c8f3d8e5c23e1e42 (2026-07-14, \"Relay mesh: cross-pod tunnel + huddle transport (buzz-relay-mesh) (#1670)\"); the most recent commit to touch ARCHITECTURE.md is 909a3b2c318b2ec477a3438a998a3b611f5b6d6a (2026-08-01, \"docs: fix stale kind count, quick-start numbering, and empty Further Reading (#2613)\"), which postdates the mesh crate but whose own title names only unrelated fixes."
    entry_class: FACT
    evidence:
      - "commit ccb021d71339009aabedc383c8f3d8e5c23e1e42"
      - "commit 909a3b2c318b2ec477a3438a998a3b611f5b6d6a"
      - "ARCHITECTURE.md:7"
  - statement: "ARCHITECTURE.md's unqualified line 7 (\"no peer-to-peer event exchange, no gossip, no replication\") was not reconciled with buzz-relay-mesh's existence when ARCHITECTURE.md was last edited, so a reader relying on that sentence alone would not learn that a gossip-based inter-pod mesh exists in the codebase; because the mesh's own documentation frames it as internal transport for one logical relay deployment rather than an independently-writable second copy of state, this reads as a documentation-precision gap about the relay's own internals rather than a second source of truth."
    entry_class: INFERENCE
    evidence:
      - "ARCHITECTURE.md:7"
      - "crates/buzz-relay-mesh/src/lib.rs:1-19"
      - "commit ccb021d71339009aabedc383c8f3d8e5c23e1e42"
      - "commit 909a3b2c318b2ec477a3438a998a3b611f5b6d6a"
    confidence: 0.7
  - statement: "deny.toml's only architecture-adjacent section is [bans], which sets multiple-versions = \"warn\" and wildcards = \"allow\" -- governing duplicate external crate versions, not internal crate-import boundaries -- so no automated lint, cargo-deny ban, or CI check enforces that buzz-relay's subsystem crates avoid depending on each other."
    entry_class: FACT
    evidence:
      - "deny.toml"
---

# Relay is the single source of truth

## The invariant

The relay (the `buzz-relay` service -- one logical deployment, which MAY run as
a single process or as multiple pods behind the same deployment; see
*Scope* below) MUST be the sole authority for all Buzz application state.
Every read of that state and every write to it MUST pass through the relay;
no client and no other workspace component MUST hold or serve an
independently-writable copy of it.

Within the relay's own implementation, the subsystem crates it orchestrates
(`buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit`,
`buzz-workflow`, `buzz-media`) MUST NOT call each other directly to
coordinate state. Cross-subsystem coordination MUST happen only through the
relay itself, or through the shared database / Redis pub-sub substrate --
never through a direct function call from one subsystem crate into another.

## Scope

Applies to:

- All Nostr event state persisted through `buzz-db` -- messages, reactions,
  workflow runs, canvas updates, huddle events, git objects and their
  metadata, and media metadata.
- Community/tenant resolution itself: `req.community` is derived from the
  connection host by the relay before any handler runs, not supplied or
  overridden by a client.
- Every client class: human clients (desktop, web, mobile), agent clients
  (`buzz-cli`, ACP-managed agents), and operator tooling (`buzz-admin`).
  None of these hold a direct database or Redis connection; their only path
  to state is the relay's WebSocket/HTTP surface.
- The relay's own internal composition: `buzz-relay` is the one crate in the
  workspace permitted to import `buzz-db`, `buzz-auth`, `buzz-pubsub`,
  `buzz-search`, `buzz-audit` and `buzz-workflow` together; those subsystem
  crates do not import each other.

Does not extend to (separate, narrower invariants, out of scope for this
node):

- The git-on-object-storage manifest pointer as the source of truth for one
  repository's git state (`docs/git-on-object-storage.md`) -- a different,
  narrower claim about git storage specifically, not the relay as a whole.
- The git-signing trust model in `crates/git-sign-nostr` and
  `crates/git-credential-nostr`.

**A qualification this node makes explicit rather than silently resolving.**
"The relay" is not necessarily one OS process. `buzz-relay-mesh` implements a
QUIC mesh with gossip-based pod membership so one logical relay deployment
can scale horizontally across multiple pods (cross-pod tunnel and huddle
transport). Its own module documentation is explicit that mesh membership is
only a hint, that the Redis fenced generation is the arbiter, and that the
crate "grants no ownership" -- so a multi-pod relay deployment does not
create a second source of truth; Postgres and the Redis fenced generation
remain the arbiters regardless of how many pods the relay runs as.

What this does mean is that `ARCHITECTURE.md`'s plain-English sentence "There
is no peer-to-peer event exchange, no gossip, no replication" is imprecise
about the relay's *own* internal transport, not only about clients --
`buzz-relay-mesh` is, by its own docstring, a full mesh with gossip. That
crate was added on 2026-07-14; `ARCHITECTURE.md` was last touched on
2026-08-01 by a change whose own title names unrelated fixes, so the wording
was not reconciled. This node records that gap rather than repeating the
stale wording as fact or rewriting `ARCHITECTURE.md` on this task's behalf --
reconciling the prose is a documentation task for whoever owns
`ARCHITECTURE.md`, not something in scope here.

## Enforcement points

1. **Row-zero host binding** (`crates/buzz-relay/src/tenant.rs`).
   `req.community = resolve_host(connection.host)` runs before any handler --
   AUTH, EVENT, REQ, REST, media, git, search, workflow, or pub/sub -- observes
   tenant data. `bind_community` fails closed: an empty host, an unmapped
   host, or a lookup error all return `BindError::UnmappedHost` or
   `BindError::Lookup`; there is no code path that yields a default or
   fallback community.
2. **Crate dependency graph.** `buzz-search`, `buzz-audit`, `buzz-pubsub` and
   `buzz-media` carry no `buzz-db` dependency and no dependency on each other.
   `buzz-workflow` depends on `buzz-db` (the shared database-access crate,
   consistent with "communicate through the database") but not on the other
   subsystem crates. Only `buzz-relay/Cargo.toml` imports all of them
   together. Compiling a direct call from one subsystem crate into another
   would require adding that dependency first.
3. **No direct client data path.** `desktop/src-tauri/Cargo.toml` carries no
   Postgres or database-client dependency, so the desktop backend cannot read
   or write relay state except by calling the relay.
4. **Push delivery is non-authoritative by specification.** Per NIP-PL, the
   wake payload MUST carry no relay-supplied bytes, event ids, content, URLs,
   ciphertext, or extensible data; the client MUST reconnect and re-fetch over
   `REQ` rather than treat anything in the push payload as authoritative.

## Observable failure behavior

- An unrecognized or unmapped request host is rejected with a generic error
  and is never admitted to a default or neighboring community -- exercised by
  `unmapped_host_fails_closed` in `crates/buzz-relay/src/tenant.rs`.
- Nothing in the current codebase prevents a future change from adding a
  direct dependency between two subsystem crates (for example, `buzz-search`
  depending on `buzz-pubsub`). If that were added, the "subsystems don't call
  each other directly" half of this invariant would silently stop holding --
  no test or lint would fail. See *What verification covers* below.

## What verification covers

- **Covered.** The host-binding fail-closed path has unit test coverage in
  `crates/buzz-relay/src/tenant.rs` (for example `unmapped_host_fails_closed`,
  `maps_known_host_to_its_community`).
- **Not covered -- recorded as a gap, not invented as a check that doesn't
  exist.** No automated lint, `cargo-deny` ban, or architecture test asserts
  that subsystem crates avoid depending on each other. `deny.toml`'s `[bans]`
  section (`multiple-versions = "warn"`, `wildcards = "allow"`) governs
  duplicate external crate versions, not internal import boundaries. Today
  this half of the invariant holds only because of the crate dependency graph
  as it currently stands, plus code review -- not because CI would catch a
  regression.
- **Related but distinct, and not cited as covering this claim.**
  `buzz-conformance` independently replays a `MultiTenantRelay.tla` formal
  spec against the relay's runtime trace. That verifies multi-tenant
  isolation (community-boundary correctness), which is a related invariant --
  the relay must not leak one community's state into another's -- but it is
  not the same claim as "the relay is the sole authority for state," so it is
  named here rather than cited as if it covered this node's invariant.

## Scope and omissions

- This node documents the invariant as the codebase currently implements and
  states it. It does not decide whether `buzz-relay-mesh`'s gossip-based
  membership should be reworded around in `ARCHITECTURE.md`, or resolve that
  drift -- that is a documentation-maintenance task, not something settled
  here.
- **Expected but not verified.** Whether any client beyond the desktop Tauri
  backend holds a cached, independently-writable copy of relay state was not
  checked exhaustively -- specifically, the mobile app's dependency manifest
  was not inspected for this document, so its absence of a direct database
  path is asserted for desktop only, not for mobile.
- **No `relationships` are declared.** At this node's recorded revision, no
  other corpus node exists under `launchpad/docs/corpus/` on `origin/launchpad`
  besides schema fixtures, `AGENTS.md`, `README.md`, and the two `standards/`
  nodes -- none of which is a node this invariant would correctly target. The
  absence is deliberate, not an oversight; per `launchpad/docs/corpus/AGENTS.md`,
  it should be revisited once a sibling `architecture` node merges.
