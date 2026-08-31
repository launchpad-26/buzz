---
id: capabilities-presence-presence-expiry
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "A presence entry is the Redis key `buzz:{community}:presence:{pubkey_hex}`, written with `SET <status> EX 180`; the 180-second TTL (`PRESENCE_TTL_SECS`) is fixed at 3x the 60-second client heartbeat interval specifically so that a single missed heartbeat does not flip a still-online user's presence to expired."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:1-25"
  - statement: "`set_presence` is the only write path that establishes or extends an entry's lifetime: it always issues `SET ... EX 180`, so there is no separate 'renew' operation -- every resent heartbeat both confirms the current status and pushes the expiry 180 seconds further out."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:27-44"
  - statement: "`clear_presence` issues a Redis `DEL`, removing an entry immediately rather than waiting out its TTL. The relay calls it on exactly two occasions: when it receives a kind:20001 presence event whose content is the literal string \"offline\", and when a WebSocket connection closes and it was that pubkey's last remaining connection in the community."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:46-59"
      - "crates/buzz-relay/src/handlers/event.rs:813-847"
      - "crates/buzz-relay/src/connection.rs:303-314"
  - statement: "The desktop client resends its current non-offline presence status every `PRESENCE_HEARTBEAT_INTERVAL_MS` (60,000ms), skipping a tick when the relay connection is not \"connected\" or the client is rate-limited. `PRESENCE_TTL_SECONDS` is derived client-side as 3x that same interval to mirror the relay's `PRESENCE_TTL_SECS`, and a source comment states the relay's TTL must be raised before shipping a build with a slower heartbeat."
    entry_class: FACT
    evidence:
      - "desktop/src/features/presence/hooks.ts:399-416"
      - "desktop/src/features/presence/lib/presence.ts:52-56"
  - statement: "A presence entry that is neither refreshed by a resent heartbeat nor explicitly cleared -- a silent client crash, a killed process, or a dropped network with no clean Close frame -- is not deleted by any code path in this repository; it is left for Redis's own key-expiry mechanism to remove once the TTL elapses. A crashed client's presence is therefore only ever cleared by expiry, never by an explicit `clear_presence` call."
    entry_class: INFERENCE
    confidence: 0.85
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:46-59"
      - "crates/buzz-relay/src/connection.rs:303-314"
  - statement: "An expired (or never-set) presence key is not distinguished from one that was explicitly cleared: `get_presence_bulk` returns entries only for pubkeys whose Redis key currently exists, silently omitting any pubkey with no key, and the relay's presence-query bridge synthesizes a relay-signed kind:20001 event only for pubkeys present in that map -- an expired pubkey produces no synthetic event at all, rather than an explicit \"offline\" one."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:73-94"
      - "crates/buzz-relay/src/api/bridge.rs:2216-2230"
  - statement: "The desktop client's own presence utilities document this same omission from the consuming side: a source comment states \"get_presence omits offline/unknown pubkeys\", and the live-update merge helper only ever adds or overwrites a pubkey's entry from a live event -- it never treats an absent pubkey in the last snapshot as a signal to mark it offline."
    entry_class: FACT
    evidence:
      - "desktop/src/features/presence/lib/presence.ts:40-50"
  - statement: "A unit test asserts `PRESENCE_TTL_SECS` equals both 180 and `3 * 60` directly, and an ignored (`requires Redis`) integration test asserts a live key's observed TTL falls between 1 and `PRESENCE_TTL_SECS` seconds immediately after `set_presence` -- both exercise the expiry window's exact numeric value, not merely that some expiry exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:132-136"
      - "crates/buzz-pubsub/src/presence.rs:212-234"
  - statement: "The websocket-connection flow's own corpus node already documents the clean-disconnect half of this capability: 'clears presence for that pubkey once no other connection from the same pubkey remains in the community,' as part of every connection-termination path converging on one cleanup routine."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md:90"
relationships:
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-flows-websocket-connection
---

# Presence expiry: capability

Buzz never requires a human or an AI agent to explicitly announce that they have gone
offline for the rest of the system to find out. A user's or agent's presence --
online, away, or offline -- is backed by a Redis key that carries its own 180-second
lifetime, refreshed by a resent heartbeat roughly three times over that window. If the
heartbeat stops arriving for any reason -- a clean sign-off, a closed window, a crashed
process, a lost network connection -- the presence entry stops being true within, at
most, that same 180-second window, without any other part of the system needing to
notice the client is gone and say so on its behalf. This is what lets every other
presence-consuming surface (channel member lists, DM headers, agent status badges)
treat "no current entry" as a safe default rather than a stale one.

## Maturity

**Shipped.** `crates/buzz-pubsub/src/presence.rs` implements the Redis-backed
TTL entry and is called from production code paths in `buzz-relay`
(`crates/buzz-relay/src/handlers/event.rs`, `crates/buzz-relay/src/connection.rs`,
`crates/buzz-relay/src/api/bridge.rs`), and the desktop client's presence heartbeat
loop (`desktop/src/features/presence/hooks.ts`) is wired into the running app rather
than gated behind a flag. The expiry window's exact value (180 seconds, derived as 3x
a 60-second heartbeat) is covered by both a fast unit test and an ignored
Redis-requiring integration test.

## Behavioral rules and variants

- **The expiry window is 180 seconds, derived, not arbitrary.** `PRESENCE_TTL_SECS`
  is fixed at 3x the 60-second client heartbeat interval specifically so a single
  missed heartbeat tick does not flap a still-connected user's presence to expired.
  The client and relay each define this multiple independently (`PRESENCE_TTL_SECONDS`
  client-side, `PRESENCE_TTL_SECS` relay-side) and a source comment on the client
  constant warns that the relay's window must be widened before a slower client
  heartbeat ships, since the relay's value is authoritative.
- **Every heartbeat is a full re-write, not an increment.** There is no dedicated
  "extend TTL" operation -- `set_presence` always performs `SET <status> EX 180`, so
  resending the same status both re-confirms it and resets the clock to a full 180
  seconds from that moment.
- **Two paths clear an entry immediately, ahead of its TTL.** An explicit
  "offline" presence event (kind:20001 with content `"offline"`) triggers `DEL`
  immediately. Separately, when a WebSocket connection that had authenticated closes
  and no other connection from the same pubkey remains open in that community, the
  relay also clears the entry immediately. Both are "clean" exits; neither waits on
  expiry.
- **Everything else relies on expiry alone.** A hard crash, a force-quit, or a
  network drop with no Close frame reaches neither of the two immediate-clear paths.
  In that case the entry is left exactly as it was until Redis expires the key on its
  own -- there is no separate reaper, sweep, or liveness check anywhere in this
  repository that clears a stale presence entry early or late.
- **Expiry is silent, not announced.** Nothing in this repository publishes an
  explicit "this pubkey went offline by expiry" event. A presence lookup
  (`get_presence`, `get_presence_bulk`) for an expired or never-set key simply
  returns nothing for that pubkey, and the relay's presence-query bridge synthesizes a
  relay-signed kind:20001 event only for pubkeys still present in the lookup. A
  consuming client is expected to treat "absent from the last snapshot" as offline by
  omission, and the desktop client's own presence utilities are written against
  exactly that expectation.
- **The heartbeat itself pauses under two conditions**, both client-side: while the
  relay connection is not in a "connected" state, and while the client is
  rate-limited. Neither pause clears presence explicitly -- it simply stops
  refreshing the TTL, so the entry expires on schedule if the condition does not
  clear before 180 seconds elapse.

## Boundary

This node does not describe:
- **How the underlying storage is built** -- the Redis container, its tenant-scoped
  key convention, and its role as a volatile coordination layer rather than a system
  of record. See the architecture node for Redis.
- **The interface(s) a client uses to set or query presence** -- the kind:20001
  ephemeral event shape, the relay's presence-query bridge over `POST /query`, and the
  CLI's presence subcommands. No dedicated interface node for this exists yet in the
  corpus at the time of writing.
- **The step-by-step path a heartbeat or a connection-close event takes through the
  relay** -- that belongs to a flow node. The clean-disconnect half of this capability
  is already narrated by the websocket-connection flow node; no flow node yet
  documents the heartbeat-resend half specifically.
- **General presence status itself** -- how online/away/offline is set, broadcast,
  and displayed. This node is scoped to the expiry mechanism only: what causes an
  entry to stop being true, and how fast. A broader presence capability node, if and
  when one exists, owns the rest.
- **How the running relay or Redis instance is operated** -- monitoring, alerting on
  Redis outages, or capacity planning for the presence keyspace.

## Relationships

- references: `architecture-containers-redis` -- the Redis container node already
  documents this exact TTL mechanism (`presence.rs`'s key convention, TTL value, and
  operations) as part of its own account of every TTL-bounded write path in
  `buzz-pubsub`.
- references: `architecture-flows-websocket-connection` -- the websocket-connection
  flow node already narrates the clean-disconnect clear as one step in its single
  converged connection-termination cleanup path.

## Scope and omissions

**This node covers** what causes a Buzz presence entry to stop being true and how
quickly: the 180-second Redis TTL and its derivation from the 60-second client
heartbeat, the two immediate-clear paths (explicit offline, last-connection-closed),
the fact that a crash or network drop relies on TTL expiry alone with no reaper or
sweep, and that expiry is silent -- surfaced only as an absence in later lookups, never
as an explicit event.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the Redis-backed store is built | `architecture-containers-redis` |
| The interface(s) used to set/query presence | not yet drafted in the corpus |
| The step-by-step heartbeat-resend flow | not yet drafted in the corpus (the clean-disconnect half is in `architecture-flows-websocket-connection`) |
| General presence status semantics (online/away/offline, broadcast, display) | a separate, broader presence capability node, if drafted |
| Operating Redis / the relay in production | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No test in this repository exercises the crash/network-drop path directly** --
  that an entry left un-refreshed actually disappears from Redis at 180 seconds relies
  on the ignored (`requires Redis`) TTL test's assertion about the TTL value plus
  ordinary Redis key-expiry semantics, not on a test that lets 180 seconds elapse and
  observes the key gone.
- **No production metric or log line confirming expiry-driven clears in practice was
  found or checked** -- the claim that expiry is the sole cleanup path for a crashed
  client rests on reading every call site of `clear_presence` in this repository
  (two), not on operational telemetry showing the crash case actually occurring and
  resolving this way.
