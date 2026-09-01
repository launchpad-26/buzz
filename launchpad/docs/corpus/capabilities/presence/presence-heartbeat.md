---
id: capabilities-presence-presence-heartbeat
type: capabilities
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
  - statement: "presence.rs stores presence as a Redis key SET buzz:{community}:presence:{pubkey_hex} with a fixed PRESENCE_TTL_SECS=180 TTL, and its own module doc states this TTL is chosen as 3x the 60s heartbeat interval so a single missed heartbeat does not cause presence to flap; set_presence re-issues the SET (and therefore the EX 180 TTL) on every call, and clear_presence issues DEL for immediate removal on clean disconnect."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:1-16"
      - "crates/buzz-pubsub/src/presence.rs:27-59"
  - statement: "The desktop client's usePresenceSession hook re-publishes the current presence status on a window.setInterval firing every PRESENCE_HEARTBEAT_INTERVAL_MS (60_000ms, defined in presence.ts), and skips a tick (does not call syncPresence) when relayClient.getConnectionState() !== \"connected\" or isRateLimited() is true, rather than queuing the publish for later."
    entry_class: FACT
    evidence:
      - "desktop/src/features/presence/hooks.ts:399-416"
      - "desktop/src/features/presence/lib/presence.ts:52-56"
  - statement: "presence.ts derives PRESENCE_TTL_SECONDS as exactly 3 * (PRESENCE_HEARTBEAT_INTERVAL_MS / 1000) = 180, matching the relay-side PRESENCE_TTL_SECS constant, and its own comment states the relay owns the authoritative TTL and that a slower client heartbeat requires deploying a relay TTL increase first."
    entry_class: FACT
    evidence:
      - "desktop/src/features/presence/lib/presence.ts:52-56"
  - statement: "relayClientSession.ts's sendPresence signs and publishes a kind:20001 event with content set to the literal status string (no JSON envelope) and no tags; usePresenceSession calls this both on a status transition (online/away/offline) and on every heartbeat tick via the shared syncPresence effect event."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts:282-295"
      - "desktop/src/features/presence/hooks.ts:380-416"
  - statement: "buzz-core/src/kind.rs defines KIND_PRESENCE_UPDATE = 20001 in the ephemeral kind range and lists it among the kinds handle_ephemeral_event routes to; the relay's handle_ephemeral_event function special-cases kind:20001, accepting either a bare status string or a legacy {\"status\": ...} JSON envelope, and truncates any other content longer than 128 bytes to a 128-byte, char-boundary-safe prefix before treating it as the status."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:463"
      - "crates/buzz-relay/src/handlers/event.rs:808-828"
  - statement: "handle_ephemeral_event calls state.pubsub.clear_presence when the parsed status is the literal string \"offline\", and state.pubsub.set_presence (refreshing the 180s TTL) for any other status value, then lets the event fall through to the same publish/fan-out path as other ephemeral events so other relay nodes receive the live delta."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:830-845"
  - statement: "buzz-cli's cmd_set_presence signs and submits exactly one kind:20001 event per invocation over an authenticated WebSocket connection (bypassing the HTTP bridge, since ephemeral kinds are WS-only) and returns; it contains no internal repeat/interval loop, so a CLI-driven or ACP-agent actor needing to keep presence alive across the 180s TTL must be re-invoked externally on its own schedule -- the CLI provides the one-shot primitive, not a heartbeat scheduler."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/users.rs:502-514"
  - statement: "The relay's HTTP /query bridge synthesizes relay-signed kind:20001 (or kind:40902) events on demand from the current Redis presence_map for REQ/query filters that target only those kinds with an authors list, rather than replaying a stored event -- this is the read/seed path a client or buzz-cli's cmd_get_presence uses to learn current status without waiting for a live heartbeat delta, and is a distinct capability from the heartbeat mechanism this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2049-2116"
      - "crates/buzz-cli/src/commands/users.rs:455-486"
  - statement: "The desktop app also runs an unrelated WebSocket-level heartbeat_loop (connection.rs) that pings every 30 seconds and disconnects after 3 missed pongs; this is transport keep-alive for the WebSocket connection itself and carries no presence status content -- it must not be conflated with the 60-second presence-status heartbeat this node documents, which is an application-level, content-bearing kind:20001 republish."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:436-460"
  - statement: "No unit or integration test in this repository was found exercising handle_ephemeral_event's legacy-JSON-envelope parsing branch or its 128-byte truncation branch directly, nor a test exercising usePresenceSession's actual setInterval-driven re-publish or its skip-on-disconnected/rate-limited branch; existing tests cover the bare-string status path (presence_event test helper in event.rs) and the pure PRESENCE_HEARTBEAT_INTERVAL_MS/PRESENCE_TTL_SECONDS constants and helper functions in presence.test.mjs, but not the periodic-timer behavior itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1514-1516"
      - "desktop/src/features/presence/lib/presence.test.mjs:36-40"
  - statement: "This capability is shipped, not designed-only: both the relay-side TTL refresh (presence.rs, handle_ephemeral_event) and the desktop client's periodic re-publish (usePresenceSession) exist as merged, non-experimental code with passing unit tests on each side (presence_ttl_is_three_one_minute_heartbeat_windows and related tests in presence.rs; the constant and pure-helper tests in presence.test.mjs)."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/presence.rs:112-116"
      - "desktop/src/features/presence/lib/presence.test.mjs:36-40"
      - "desktop/src/features/presence/hooks.ts:399-416"
    confidence: 0.9
  - statement: "Issue #805's definition of done, for a capabilities-typed node, requires stating the capability and primary actors/outcomes, defining behavioral rules/constraints/variants, linking major flows/interfaces/data/platform implementation, and linking verification demonstrating the capability -- the shape this node is structured against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#805 definition of done"
relationships:
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-flows-live-fanout
---

# Presence heartbeat: capability

A connected client (a human user's desktop app, or an agent/CLI actor) keeps its
online/away presence status current in the eyes of every other client by
periodically re-publishing that status, so presence never silently goes stale
between explicit status changes and a crashed or disconnected client's status
expires automatically rather than sticking at "online" forever.

## Primary actors and outcomes

- **The presence subject** -- the human user or agent whose status is being kept
  alive. Their outcome: other participants see their status (online/away/offline)
  reflect reality within one heartbeat window, and if their client disappears
  without a clean disconnect, their status lapses to unknown (TTL expiry) rather
  than staying stuck online indefinitely.
- **The desktop client**, via `usePresenceSession` -- derives the automatic
  online/away status from user activity and OS idle time, and re-publishes it on
  every `PRESENCE_HEARTBEAT_INTERVAL_MS` (60s) tick as well as on every status
  transition. It is the one implementation in this repository that runs a
  genuine repeating heartbeat.
- **`buzz-cli`, via `cmd_set_presence`** -- a one-shot kind:20001 publish per
  invocation, with no internal loop. An agent that wants to hold presence for
  longer than the 180s TTL must re-invoke it on its own external schedule; the
  CLI is the primitive a heartbeat is built from, not a heartbeat itself.
- **Other participants viewing presence** -- read current status either from the
  live kind:20001 fan-out (fast path, see *Boundary*) or from the relay's
  synthesized snapshot on `/query` (backstop/seed path, see *Boundary*), neither
  of which this node documents in depth.
- **The relay** -- accepts each republished kind:20001 event, refreshes the
  Redis-backed TTL, and forwards the update into the same ephemeral fan-out path
  as any other ephemeral event, so the heartbeat both keeps the subject's
  presence alive and pushes a live delta to anyone subscribed.

## Maturity

Shipped. Both halves of the mechanism are merged, non-experimental code with
passing unit coverage on their own narrow claims: the relay-side TTL constant
and refresh behavior (`crates/buzz-pubsub/src/presence.rs`, including
`presence_ttl_is_three_one_minute_heartbeat_windows`), and the desktop client's
heartbeat interval and derived-TTL constants
(`desktop/src/features/presence/lib/presence.test.mjs`). See the evidence
ledger's INFERENCE entry for what specifically was and was not directly tested
(the periodic-timer firing itself was not, only its constants and the
downstream Redis/parsing logic it drives).

## Behavioral rules and constraints

1. **The heartbeat interval and the relay TTL are coupled by a fixed 3x ratio,
   not independently configurable.** Desktop's `PRESENCE_TTL_SECONDS` is computed
   from `PRESENCE_HEARTBEAT_INTERVAL_MS` as `3 * (interval / 1000)`, and the
   relay's `PRESENCE_TTL_SECS` is a separate, hardcoded `180`. They currently
   agree (60s heartbeat, 180s TTL) only because both sides were set to match
   deliberately -- presence.ts's own comment states a slower client heartbeat
   requires deploying the relay TTL increase *first*. Nothing in code enforces
   this pairing across the two crates/apps; it is a manual invariant.
2. **A heartbeat tick that cannot be delivered is skipped, not queued or
   retried.** The desktop client drops a heartbeat tick outright when the relay
   connection is not `"connected"` or the client is rate-limited, rather than
   buffering it for the next successful tick -- deliberately, so a struggling
   connection is not asked to also carry a backlog of stale presence publishes.
   The consequence is that a client disconnected for longer than the 180s TTL
   will have its presence lapse (correct: it silently expires rather than
   staying "online" during a real outage), and will re-publish "online" again
   once ticks resume, without a "catch-up" burst.
3. **The relay accepts two content shapes and always emits status as plain
   text downstream.** A heartbeat's `content` may be a bare status string
   (`"online"`) or a legacy `{"status": "..."}` JSON envelope; either is
   normalized to a bare status string before being stored in Redis or
   forwarded. Content longer than 128 bytes is truncated to a
   char-boundary-safe 128-byte prefix rather than rejected.
4. **`"offline"` is the one status value that clears rather than refreshes.**
   Every other status string (including values neither client UI currently
   offers) is written to Redis with a fresh TTL; only the literal string
   `"offline"` triggers `clear_presence` (immediate `DEL`).
5. **The heartbeat is per-connection-derived, not per-account.** Presence is
   keyed by `{community, pubkey}`, and the desktop hook's automatic status is
   derived from that browser/app instance's own activity and OS idle signal --
   a user connected from two devices is not reconciled by this mechanism beyond
   whichever device's heartbeat landed most recently in Redis.

## Boundary

This node does not describe:
- **How presence is read back or seeded on subscribe** -- the relay's
  `/query` bridge synthesizing a relay-signed kind:20001/kind:40902 snapshot
  from the live Redis map, and the desktop app's 60s REST backstop poll
  (`PRESENCE_REFETCH_INTERVAL_MS`) and live-subscription reconciliation. These
  are a related but distinct read-path capability; see
  `architecture-containers-redis` and `architecture-flows-live-fanout` for the
  fan-out mechanics this node's heartbeat feeds into.
- **How the heartbeat's ephemeral event is built and technically built,
  Redis-backed, or containerized** -- see the `architecture-containers-redis`
  node for `buzz-pubsub`'s presence module in the context of the wider Redis
  container, and `architecture-flows-live-fanout` for how `handle_ephemeral_event`
  fits the relay's broader event-dispatch flow.
- **The interface(s) the heartbeat is exposed through** (the WebSocket ephemeral
  event surface, `buzz-cli`'s `presence set`/`presence get` subcommands) at the
  level of a full interface contract -- no interface-typed corpus node exists
  yet to `references`.
- **The step-by-step request/response sequence of one heartbeat tick** as a
  flow narrative -- `architecture-flows-live-fanout` already narrates the
  ephemeral-event dispatch path this heartbeat's events travel; this node
  states the capability's rules, not that sequence.
- **The unrelated WebSocket-transport ping/pong keepalive** (`heartbeat_loop` in
  `connection.rs`, 30s interval, 3 missed pongs -> disconnect). That mechanism
  keeps the WebSocket connection itself alive and carries no presence status;
  it is a different "heartbeat" sharing only the name, not the mechanism, with
  what this node documents.
- **Presence expiry as its own concept** (what happens to readers once a TTL
  lapses with no replacement heartbeat) beyond stating that `clear_presence`/TTL
  expiry is how a stale presence disappears -- a sibling capability node for
  presence expiry may cover that in more depth; no such node is merged on
  `origin/launchpad` at the time of writing, so no relationship to it is
  declared here (see *Relationships*).

## Relationships

- `references`: `architecture-containers-redis` -- documents `buzz-pubsub`'s
  `presence.rs` module (the `SET`/`GET`/`DEL` operations and TTL) as part of the
  Redis container's own responsibilities; this node relies on that description
  rather than restating it.
- `references`: `architecture-flows-live-fanout` -- documents
  `handle_ephemeral_event`'s role in the relay's event-dispatch flow, including
  that ephemeral kinds (presence among them) run the inline path and skip
  audit/workflow steps; this node relies on that description for how a
  heartbeat's event is dispatched once accepted.
- Not declared: a relationship to a presence-expiry or presence-query sibling
  node. `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  at the recorded revision carries no `capabilities/presence/*` node other than
  this one -- the directory did not exist before this change -- so no such
  target resolves yet. The first sibling capability node to merge under
  `capabilities/presence/` is the point to revisit this.

## Scope and omissions

**This node covers** the presence-heartbeat mechanism specifically: what
publishes a repeating kind:20001 status update, what interval and TTL relationship
governs it, how the relay normalizes and stores what it receives, which actors
implement a genuine repeating heartbeat versus a one-shot primitive, and the
behavioral rules and constraints that follow from the code as written.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Redis container's full responsibilities (pub/sub fan-out, typing indicators, rate limiting) beyond presence | `architecture-containers-redis` |
| The relay's full ephemeral/persistent event dispatch flow beyond the presence special-case | `architecture-flows-live-fanout` |
| Presence read/query/seed mechanics (`/query` bridge synthesis, desktop's REST backstop poll and live-subscription reconciliation) | a presence-query/read-path node, not yet drafted |
| Presence expiry as a named capability in its own right | a presence-expiry node, not yet drafted/merged as of this writing |
| The WebSocket transport-level ping/pong keepalive (`heartbeat_loop`, `connection.rs`) | out of scope entirely -- unrelated mechanism, named here only to prevent confusion |
| A formal interface contract for the ephemeral presence surface or `buzz-cli`'s presence subcommands | no interface-typed corpus node exists yet |

**Expected but not verified when this node was written:**
- **The actual periodic firing of `usePresenceSession`'s `setInterval` and its
  skip-on-disconnected/rate-limited branch was read in source but not confirmed
  by a passing test exercising real timer behavior** -- existing desktop tests
  cover the pure constants and helper functions in `presence.ts`, not the
  effectful interval loop in `hooks.ts`.
- **`handle_ephemeral_event`'s legacy-JSON-envelope parsing and 128-byte
  truncation branches were read in source but no test exercising either branch
  directly was found** -- existing relay tests build bare-string status events
  only.
- **Mobile's own presence-heartbeat behavior, if any, was not checked.** This
  node's client-side evidence is desktop-only and `buzz-cli`-only; whether the
  Flutter app runs an equivalent periodic re-publish was not searched.
