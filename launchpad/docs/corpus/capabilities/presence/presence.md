---
id: capabilities-presence-presence
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum lists capabilities as its own dedicated member, distinct from architecture and interfaces-events; a node built from the capability template carries type: capabilities."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "buzz-pubsub's presence.rs stores presence as a Redis key SET buzz:{community}:presence:{pubkey_hex} <status> EX 180, where PRESENCE_TTL_SECS=180 is chosen as 3x the 60s client heartbeat so one missed heartbeat does not flap presence to offline; set_presence, clear_presence, get_presence and get_presence_bulk (MGET) are the four exposed operations, and clear_presence issues a DEL for immediate removal on clean disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:1-94"
  - statement: "presence.rs's own test module asserts PRESENCE_TTL_SECS equals 3*60 exactly, that a presence key is scoped (community, pubkey) rather than pubkey alone, and (behind #[ignore = \"requires Redis\"]) that set/get/clear and bulk lookup round-trip through a real Redis instance and that TTL is set within (0, PRESENCE_TTL_SECS] seconds after a write."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:112-140"
      - "crates/buzz-pubsub/src/presence.rs:142-214"
  - statement: "buzz-core's presence.rs defines a curated PresenceStatus enum (Online, Away, Offline) shared across the REST/MCP and structured-API surfaces, with its own doc comment stating the WebSocket path (kind:20001) accepts arbitrary status strings for forward-compatibility rather than being constrained to this enum."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/presence.rs:1-18"
  - statement: "buzz-core's kind.rs assigns KIND_PRESENCE_UPDATE = 20001 inside the ephemeral range (20000-29999, never stored, WS pub/sub only) and KIND_PRESENCE_SNAPSHOT = 40902 as a relay-signed sidecar kind for bulk presence state, both documented inline as presence-specific."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:448-450"
      - "crates/buzz-core/src/kind.rs:462-463"
      - "crates/buzz-core/src/kind.rs:502-503"
  - statement: "buzz-relay's handle_ephemeral_event special-cases kind:20001: it accepts either a bare status string or a legacy {\"status\":...} JSON body, truncates an overlong status to at most 128 bytes at a char boundary, clears presence in Redis on status \"offline\" and otherwise sets it, then deliberately falls through to the shared global ephemeral publish/fan-out path so other relay pods receive the same live delta -- presence is a channel-less ephemeral event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:813-846"
  - statement: "A unit test in buzz-relay's handlers/event.rs registers a global (channel-less) subscription filtered on kind:20001 and confirms a presence event reaches it, corroborating that presence fan-out is global rather than channel-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1440-1512"
  - statement: "buzz-relay's WebSocket connection cleanup path clears a pubkey's presence only once no other live connection for that same pubkey remains in the community (checked via ConnectionManager::connection_ids_for_pubkey_in_community), so one of several concurrent sessions closing does not wrongly clear presence for the others."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:300-315"
  - statement: "buzz-relay's api/bridge.rs implements synthesize_presence: an HTTP POST /query request whose filters target only kind:20001 or kind:40902 with explicit non-empty authors is intercepted before reaching the database, looked up in Redis via get_presence_bulk, and answered with relay-signed synthetic kind:20001 events -- because ephemeral events are never stored in Postgres, there is no DB fallback for this path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:1042"
      - "crates/buzz-relay/src/api/bridge.rs:2049-2110"
  - statement: "An integration test (#[ignore], requires two live relay instances) named fanout_and_presence_do_not_cross_communities publishes distinct presence statuses for the same keypair against two different communities and asserts each community's synthesized presence query returns only its own status, verifying the Redis presence key is scoped to (community, pubkey) end-to-end through the real relay and bridge, not merely at the key-format unit-test level."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:2361-2372"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:2514-2575"
  - statement: "buzz-cli's users subcommand exposes `presence --pubkeys <csv>` (queries kind:40902 snapshot events over the REST bridge, hex-validates each pubkey, and resolves the subject from a p tag falling back to the event author) and `set-presence --status <online|away|offline>` (builds a kind:20001 event via buzz_sdk::build_presence_update, signs it, and publishes it over the authenticated WebSocket connection, bypassing the HTTP bridge entirely)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/users.rs:455-514"
      - "crates/buzz-cli/src/lib.rs:863-874"
  - statement: "buzz-sdk's build_presence_update validates that status is exactly one of \"online\", \"away\", or \"offline\", rejecting anything else with SdkError::InvalidInput, and builds a kind:20001 EventBuilder carrying a status tag matching the content."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:1703-1714"
  - statement: "Desktop's presence feature (desktop/src/features/presence/lib/presence.ts) parses only the live kind:20001 event's own pubkey as the status subject -- explicitly not trusting a p tag on that path, since any client could forge one -- while treating the relay-signed REST/snapshot path as the only place a p-tag subject is trusted; it also derives an automatic online/away transition from OS-level idle time (a 10-minute PRESENCE_IDLE_TIMEOUT_MS) with an explicit comment that \"away\" means the human is not at the machine, never merely that Buzz is not the focused window, and keeps its local optimistic TTL at the same 3x-60s-heartbeat window the relay enforces."
    entry_class: FACT
    evidence:
      - "desktop/src/features/presence/lib/presence.ts:1-72"
  - statement: "Desktop renders presence with dedicated PresenceDot/PresenceBadge components mapping each of the three statuses to a distinct color and label, and a Playwright end-to-end spec (\"updates presence from the profile menu\") drives the profile popover through online -> away -> offline and asserts the rendered label changes at each step; a second spec asserts an agent's own profile shows a presence badge with aria-label \"Online\"."
    entry_class: FACT
    evidence:
      - "desktop/src/features/presence/ui/PresenceBadge.tsx:1-56"
      - "desktop/tests/e2e/profile.spec.ts:1086-1107"
      - "desktop/tests/e2e/profile.spec.ts:1172-1174"
  - statement: "Mobile's PresenceCacheNotifier subscribes to kind:20001 over the relay WebSocket and caches presence in memory per pubkey; its own code comment records an open gap -- the relay does not yet support a presence:true filter extension, so mobile currently only learns a pubkey is online when that pubkey actually publishes an event, with no way to query a known-offline/never-seen state."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/profile/presence_cache_provider.dart:1-70"
  - statement: "architecture-containers-redis (merged on launchpad) already documents the Redis storage half of presence -- key format, TTL rationale, and buzz-pubsub's ownership of it -- at the architecture layer; this node references that node rather than restating its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/redis.md"
  - statement: "architecture-flows-websocket-connection (merged on launchpad) already documents the WebSocket connection lifecycle, including the step where presence is cleared for a pubkey once its last connection in a community closes; this node references that node rather than restating its sequence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
  - statement: "No sibling document under launchpad/docs/corpus/capabilities/presence/ (presence-expiry, presence-heartbeat, typing-indicator, user-status) is merged on origin/launchpad at the recorded revision, so none exists as a valid relationships target yet; this node's own git ls-tree check against origin/launchpad found the capabilities/ directory absent entirely."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/capabilities') -> no such path, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #806's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#806 definition of done"
relationships:
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-flows-websocket-connection
---

# Presence: capability

Buzz lets a user or agent broadcast, and every other participant observe, a
lightweight online/away/offline status for any account in a community. The
primary actors are the account whose status is being reported (a human on
desktop or mobile, or an agent via `buzz-cli`) and every other participant
who observes it (rendered as a colored dot/badge in the desktop and mobile
UIs, or read programmatically via the CLI or the REST bridge). The outcome
a caller can rely on: a status set by one client is visible to every other
authorized client within moments, through whichever surface it queries
(live WebSocket event or on-demand snapshot), and it disappears on its own
if the reporting client goes silent, without requiring an explicit
"offline" signal.

## Maturity

**Shipped.** The full path is implemented and wired end to end: Redis
storage (`crates/buzz-pubsub/src/presence.rs`), the shared status vocabulary
(`crates/buzz-core/src/presence.rs`), the two event kinds
(`crates/buzz-core/src/kind.rs`), the relay's live-update and cleanup
handling (`crates/buzz-relay/src/handlers/event.rs`,
`crates/buzz-relay/src/connection.rs`), the REST/MCP synthesis bridge
(`crates/buzz-relay/src/api/bridge.rs`), CLI subcommands
(`crates/buzz-cli/src/commands/users.rs`), a desktop UI with live updates,
optimistic local state and automatic idle-based transitions
(`desktop/src/features/presence/`), and a mobile cache provider
(`mobile/lib/features/profile/presence_cache_provider.dart`). One known gap
is noted in mobile's own code: mobile has no `presence:true`-style filter
yet, so it currently infers "online" only from an observed live event
rather than querying known state — a documented TODO, not a design decision
this node can attribute to anything beyond that comment.

## Behavioral rules, constraints and variants

- **Three statuses only, at the vocabulary level.** `online`, `away`,
  `offline` are the curated set (`PresenceStatus` in `buzz-core`), used by
  the REST/MCP surface and by `buzz-cli`'s validated `set-presence`. The
  live WebSocket path (kind:20001) is deliberately looser — the relay
  accepts any string up to 128 bytes as a forward-compatible convention, not
  a closed enum — so a client reading live events must not assume only
  those three strings ever appear on that path.
- **Ephemeral, never stored.** Presence lives only in Redis with a 180-second
  TTL (3x the 60-second client heartbeat interval), never in Postgres. An
  absent key means "unknown/offline," not "explicitly set offline" — there
  is no historical presence record to query.
- **Two independent expiry mechanisms, not one.** A status naturally expires
  after 180 seconds of silence (TTL), **or** it is cleared immediately on a
  clean WebSocket disconnect once no other connection for that pubkey
  remains in the community. Either one alone is sufficient for a status to
  disappear; neither depends on the other firing.
- **Per-community isolation.** The Redis key is `(community, pubkey)`, not
  `pubkey` alone — the same keypair reports independent presence in two
  different communities. `fanout_and_presence_do_not_cross_communities`
  verifies this against two live relay instances, not just the key-format
  unit test.
- **Trust differs by surface.** A live kind:20001 event's subject is always
  its own signing author — desktop's client code explicitly does not trust
  a `p` tag on that path, since any client could forge one naming someone
  else. The relay-signed REST/snapshot path (kind:40902, or the bridge's
  synthesized kind:20001) is the only place a `p`-tag subject is trusted,
  because the relay itself attached it after reading Redis.
- **Two query variants, same underlying state.** A caller either subscribes
  to live kind:20001 deltas over the WebSocket (push, as they happen), or
  queries on demand — CLI/REST against kind:40902 or a kind:20001 filter
  with explicit `authors`, both served by the same `synthesize_presence`
  Redis read rather than two independent code paths.
- **"Away" is a human-idle signal, not a window-focus signal.** Desktop
  derives automatic away/online transitions from OS-level idle time (a
  10-minute threshold) specifically so switching away from the Buzz window
  to another app does not itself report the user as away.

## Boundary

This node does not describe:
- **How Redis itself is deployed, pooled, or reached** — see
  `architecture-containers-redis` for the container-level treatment of
  storage, TTL rationale, and ownership.
- **The full WebSocket connection lifecycle** that presence-clearing is one
  step of — see `architecture-flows-websocket-connection` for the
  connection's own preconditions, authentication gates, and every other
  termination path.
- **The exact heartbeat/TTL tuning rationale and interaction with a
  degraded or restarted relay** — left to a dedicated presence-expiry or
  presence-heartbeat sibling node, per this task's own scope (this document
  is the bare capability overview, not that depth).
- **Typing indicators or NIP-38 user status** — related but separate
  capabilities (kind:20002 and kind:30315 respectively) that happen to
  share this crate and some UI chrome; they are not this capability and are
  not folded in here.
- **Operational tuning of the TTL or heartbeat interval values themselves**
  as a runtime-configurable concern — the values cited above are the
  current constants, not a documented configuration surface.

## Major flows, interfaces and platform implementation

- **Flow:** presence clearing on clean disconnect is one step inside the
  WebSocket connection lifecycle — see `architecture-flows-websocket-connection`.
- **Data:** two Nostr event kinds carry presence — kind:20001 (client-published,
  ephemeral, live) and kind:40902 (relay-signed snapshot, synthesized on
  query, never client-submitted) — both defined in `crates/buzz-core/src/kind.rs`.
- **Interfaces:**
  - `buzz-cli users presence --pubkeys <csv>` and
    `buzz-cli users set-presence --status <online|away|offline>`
    (`crates/buzz-cli/src/commands/users.rs`).
  - `POST /query` with a kind:20001 or kind:40902 filter naming explicit
    `authors`, intercepted by `synthesize_presence`
    (`crates/buzz-relay/src/api/bridge.rs`).
  - The WebSocket protocol itself, for both publishing a live kind:20001
    event and subscribing to receive them.
- **Platform implementation:** Redis storage in `buzz-pubsub`; relay-side
  handling in `buzz-relay`'s event handler, connection cleanup, and REST
  bridge; event construction in `buzz-sdk`; desktop's `features/presence/`
  (parsing, badges, idle-derived automatic status, optimistic cache); and
  mobile's `PresenceCacheNotifier`.

## Verification

- `crates/buzz-pubsub/src/presence.rs` unit tests (TTL value, per-community
  key scoping) and Redis-backed tests behind `#[ignore = "requires Redis"]`
  (set/get/clear round-trip, bulk lookup, TTL bounds).
- `crates/buzz-relay/src/handlers/event.rs`'s unit test confirming a
  kind:20001 event reaches a channel-less global subscription.
- `crates/buzz-test-client/tests/conformance_multitenant.rs::fanout_and_presence_do_not_cross_communities`
  (`#[ignore]`, requires two live relay instances) — the strongest available
  evidence, exercising the real relay, Redis, and the REST bridge together
  to confirm per-community isolation.
- `desktop/tests/e2e/profile.spec.ts` — "updates presence from the profile
  menu" drives the UI through all three statuses; a second case asserts an
  agent's own presence badge renders correctly.

## Relationships

- references: `architecture-containers-redis` — the container that
  implements presence's storage.
- references: `architecture-flows-websocket-connection` — the flow whose
  cleanup step clears presence on disconnect.

No `part-of`, `implements`, or `depends-on` edges are declared. No sibling
node under `capabilities/presence/` (presence-expiry, presence-heartbeat,
typing-indicator, user-status) is merged on `origin/launchpad` at the
recorded revision — checked via `git ls-tree`, not assumed — so none exists
yet as a valid relationships target.

## Scope and omissions

**This node covers** presence as a capability: what it lets a user or agent
do, its current maturity, the behavioral rules and constraints that hold
across every surface, the major flows/interfaces/data/implementation it
touches, and the verification that demonstrates it works, including across
communities.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Redis's own deployment, pooling, and container-level ownership | `architecture-containers-redis` |
| The WebSocket connection's full lifecycle and other termination paths | `architecture-flows-websocket-connection` |
| Heartbeat/TTL tuning depth and degraded-relay interaction | a presence-expiry/presence-heartbeat sibling node (not yet drafted) |
| Typing indicators (kind:20002) | a typing-indicator sibling node (not yet drafted) |
| NIP-38 user status (kind:30315) | a user-status sibling node (not yet drafted) |
| The CLI's own command surface in general | an interface-shaped node for `buzz-cli`, if one exists |

**Expected but not verified when this node was written:**
- **No live run against a real Redis instance was performed for this node.**
  The Redis-backed unit tests in `presence.rs` are marked
  `#[ignore = "requires Redis"]` and were read, not executed, and the
  cross-community integration test is similarly `#[ignore]`d (requires two
  running relay instances) — both are cited as existing, verified
  coverage, not as coverage this node's authoring re-ran.
- **Whether mobile's missing `presence:true` filter is tracked by an open
  issue** was not searched for; the gap is recorded here only as the TODO
  comment in mobile's own source states it.
- **Whether a desktop or mobile end-to-end test exercises the cross-client
  live-update path** (one client's status change appearing on another
  connected client in real time) was not found — the Playwright coverage
  located exercises one client's own UI reacting to its own status changes,
  not a second observer.
