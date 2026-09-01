---
id: capabilities-presence-typing-indicator
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
  - statement: "kind:20002 (KIND_TYPING_INDICATOR) is a channel-scoped typing indicator, defined in the ephemeral event range 20000-29999, which the relay never persists to storage."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The relay's ephemeral-event handler (handle_ephemeral_event) has no branch specific to kind:20002; unlike kind:20001 (presence), which gets special-cased status normalization and a Redis presence-state write, a typing indicator falls straight through the generic ephemeral path: signature verification, channel-membership check via extract_channel_id/check_channel_membership, state.mark_local_event, buzz_pubsub::publish_event to the channel's Redis topic, and local WebSocket fan-out via fan_out_event_to_local_subscribers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-pubsub's own crate- and module-level doc comments assert 'presence tracking, and typing indicators' and 'Typing indicator tracking in Redis,' but the crate defines a dedicated presence module (presence.rs, with a 180-second PRESENCE_TTL_SECS SET+EXPIRE) and no equivalent typing module; the doc comment describing Redis-backed typing tracking sits directly above an unrelated `pub use error::PubSubError` re-export, not above any typing-specific code."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
      - "crates/buzz-pubsub/src/presence.rs"
  - statement: "buzz-pubsub's typing-tracking doc comment most likely predates a refactor that removed or never implemented a dedicated typing module, since every other module the crate's doc comment describes (presence, cache invalidation, connection control, rate limiting, NIP-98 replay) does have a corresponding module, and only typing does not."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-pubsub/src/lib.rs"
    confidence: 0.6
  - statement: "The relay's own multi-tenant conformance test suite asserts two things about kind:20002 directly: subscribing to it and collecting until EOSE returns zero historical events ('typing is ephemeral and should not return historical events'), and a live-published typing event delivered to one community's subscribers is never delivered to a second community's subscribers of the same channel UUID and kind, even though the same in-memory SubscriptionRegistry serves both."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "The desktop client publishes a typing indicator with empty content, tagged with the channel's h tag plus optional thread parent/root reference tags via buildThreadReferenceTags, sent fire-and-forget with no wait for relay acknowledgement (sendTypingIndicator); the caller (useTypingBroadcast) throttles this to at most one publish per 3 seconds per channel."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts"
      - "desktop/src/features/messages/useTypingBroadcast.ts"
  - statement: "The desktop client's receiving side (useChannelTyping) computes typing expiry itself: a received kind:20002 event is treated as expiring at its own created_at plus an 8-second TTL (TYPING_INDICATOR_TTL_MS), the local typing-state map is pruned every second, a sender's own typing events are ignored, and a sender's typing indicator is suppressed for 2 seconds after that sender's own subsequent stream message arrives in the same thread scope."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/useChannelTyping.ts"
  - statement: "The desktop client renders active typists as a single row ('X is typing...', 'X and Y are typing...', 'X, Y, and N others are typing...' for one, two, three-plus typists respectively), and marks that row aria-live=\"polite\" so a screen reader announces the change without interrupting focus."
    entry_class: FACT
    evidence:
      - "desktop/src/features/messages/ui/TypingIndicatorRow.tsx"
  - statement: "The mobile (Flutter) client defines the same kind constant (EventKind.typingIndicator = 20002) and subscribes to it per channel through ChannelTypingNotifier, confirming the capability is implemented on a third independent client surface using the identical wire kind."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
      - "mobile/lib/features/channels/channel_typing_provider.dart"
  - statement: "The ACP agent harness (buzz-acp) publishes typing indicators on behalf of a running AI agent: while the agent has an active turn in one or more channels, a 3-second interval timer rebuilds and best-effort (non-blocking try_publish) republishes a kind:20002 event for every channel currently tracked as active, stopping once that channel's turn completes; this is enabled by default and can be disabled per agent via the --no-typing flag / BUZZ_ACP_NO_TYPING environment variable."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/relay.rs"
      - "crates/buzz-acp/src/lib.rs"
      - "crates/buzz-acp/src/config.rs"
  - statement: "Neither buzz-cli nor buzz-sdk contains any reference to typing indicators — no subcommand, no event-builder function — so an agent or script driving the CLI directly, outside the buzz-acp harness, has no supported way to broadcast one today."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('typing', path='crates/buzz-cli', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> zero matches"
      - "grep_case_insensitive('typing', path='crates/buzz-sdk', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> zero matches"
  - statement: "Root VISION.md states 'Typing indicators — real-time. Agents broadcast them too,' and separately marks 'Channel features — messaging, threads, reactions, canvases, media uploads, editing, deletion, typing indicators, NIP-29, soft-delete' with a shipped (✅) status marker in its own Area status table."
    entry_class: FACT
    evidence:
      - "VISION.md:147"
      - "VISION.md:224"
  - statement: "Root AGENTS.md's repo-structure listing names buzz-pubsub as handling 'Redis pub/sub fan-out, presence, typing indicators,' the same product-level grouping VISION.md uses, even though (per the INFERENCE entry above) no dedicated Redis-backed typing module actually exists in that crate today."
    entry_class: FACT
    evidence:
      - "AGENTS.md:65"
---

# Typing indicator: capability

When a human or an AI agent is actively composing a message in a Buzz channel
or thread, other participants connected to that channel see a lightweight,
real-time "is typing" indicator naming who is composing. It is ephemeral by
design: never stored, never replayable as history, and expires on its own
within seconds if the composer stops or disconnects. The capability is live
on three independent client surfaces today — the desktop app, the mobile
app, and AI agents running under the `buzz-acp` harness — all riding the
same relay-side wire kind.

## Maturity

**Shipped.** VISION.md's own Area status table marks channel features
including typing indicators with a shipped (✅) marker, and the capability
is independently implemented and exercised in code across four surfaces:
the relay (`crates/buzz-core/src/kind.rs`, `crates/buzz-relay/src/handlers/event.rs`,
and the multi-tenant conformance test in
`crates/buzz-test-client/tests/conformance_multitenant.rs`), the desktop
client (`relayClientSession.ts`, `useTypingBroadcast.ts`, `useChannelTyping.ts`,
`TypingIndicatorRow.tsx`), the mobile client (`nostr_models.dart`,
`channel_typing_provider.dart`), and the ACP agent harness
(`crates/buzz-acp/src/relay.rs`, `crates/buzz-acp/src/lib.rs`).

## Behavioral rules, constraints and variants

- **Wire shape.** A typing indicator is a signed Nostr event of kind:20002,
  in the ephemeral range (20000-29999), scoped to a channel with an `h` tag
  and optionally to a thread with the same parent/root reference tags used
  for threaded messages. Content is empty; the tags carry all the meaning.
- **Never stored, never historical.** The relay's own conformance test
  asserts that subscribing to kind:20002 and draining to EOSE returns zero
  historical events — a client that reconnects sees no typing state until a
  new event arrives.
- **No relay-side special handling.** Unlike kind:20001 (presence), which
  the relay's ephemeral handler special-cases with status normalization and
  a Redis-backed presence write, kind:20002 takes the same generic ephemeral
  path as any other ephemeral event: signature check, channel-membership
  check, mark-as-local, Redis publish to the channel's pub/sub topic, and
  local WebSocket fan-out. It has no dedicated relay-side logic of its own.
- **No server-side "who is typing" state.** buzz-pubsub's own module
  documentation describes "typing indicator tracking in Redis," but no such
  module exists (unlike presence's dedicated `presence.rs` with a 180-second
  Redis TTL) — the doc comment most likely predates a refactor and no longer
  matches the code. All typing state today is computed client-side, from the
  live event stream alone, with no server-authoritative source of truth.
- **Client-computed expiry (independent per client).**
  - **Desktop:** the sender throttles broadcast to at most one publish every
    3 seconds per channel while composing; a receiver treats any incoming
    event as valid for `created_at + 8 seconds`, prunes its local state once
    per second, ignores its own pubkey, and suppresses a sender's indicator
    for 2 seconds once that sender's own message arrives in the same thread
    scope.
  - **AI agents (`buzz-acp`):** the harness republishes a typing event every
    3 seconds for each channel the agent currently has an active turn in,
    using a non-blocking best-effort publish so a slow or reconnecting relay
    connection never blocks the agent's own turn, and stops once that turn
    completes. Enabled by default; disableable per agent via `--no-typing` /
    `BUZZ_ACP_NO_TYPING`.
  - **Mobile:** subscribes to the same kind:20002 per channel through its own
    notifier, independent of the desktop and harness implementations.
- **Multi-typist presentation.** The desktop client composes up to three
  named typists into one sentence ("X is typing...", "X and Y are typing...",
  "X, Y, and N others are typing...") and marks the row `aria-live="polite"`
  so assistive technology announces the change without stealing focus.
- **No CLI/SDK surface.** `buzz-cli` and `buzz-sdk` carry no typing-indicator
  subcommand or event builder. An agent or script driving the CLI directly,
  rather than running under the `buzz-acp` harness, cannot broadcast a
  typing indicator today.

## Boundary

This node does not describe:
- **How ephemeral events are published and fanned out in general** — the
  shared relay mechanism (signature check, Redis publish, local and
  cross-node WebSocket fan-out, community/channel scoping) that this
  capability rides on unmodified is `architecture-flows-live-fanout`'s
  subject, not this node's.
- **The protocol/interface boundary itself** — the NIP-01 `EVENT`/`REQ` wire
  semantics a client uses to publish and subscribe are not documented by
  this node; no dedicated interface-type corpus node for the relay's
  WebSocket protocol exists yet to `references` here.
- **The step-by-step flow of one typing interaction** — the ordered sequence
  a single compose-then-stop interaction takes through client, relay, and
  back is a flow node's subject, not documented here; no flow node for
  typing indicators exists yet.
- **How the running system is operated** — deployment, monitoring, or
  incident response for the relay or Redis are out of scope here.
- **Presence (kind:20001)** — a sibling ephemeral capability with its own
  dedicated Redis-backed state and TTL; distinct enough from typing (which
  has no server-side state at all) to warrant its own node rather than
  being folded into this one.

## Relationships

- references: architecture-flows-live-fanout
- implements: corpus-template-capability

## Scope and omissions

**This node covers** what the typing indicator capability is, where it
currently stands (shipped, on three client surfaces plus the relay), the
behavioral rules and constraints each implementation follows (wire shape,
ephemeral/non-persisted semantics, per-client expiry and throttling,
multi-typist rendering, and the current CLI/SDK gap), and the architecture
node it depends on for the underlying fan-out mechanism.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How ephemeral events are published and fanned out generally | `architecture-flows-live-fanout` |
| The relay's WebSocket protocol boundary itself | no interface-type node exists yet |
| The step-by-step path one typing interaction takes | no flow-type node exists yet |
| How the running system is operated | the `operations` corpus surface |
| Presence (kind:20001) | a separate, not-yet-drafted capability node |

**Expected but not verified when this node was written:**
- **Whether buzz-pubsub's "typing indicator tracking in Redis" doc comment
  reflects removed code, a stale plan, or a typo copied from the presence
  module's own description** was not established — no git history search
  was run to find when that comment was introduced or whether a typing
  module ever existed and was deleted. The INFERENCE entry above states a
  plausible reading, not a settled one.
- **Whether any load or chaos test exercises typing indicator volume** (many
  concurrent typists in one channel, or sustained 3-second-interval refresh
  from many agents at once) was not checked; the only test found
  (`conformance_multitenant.rs`) exercises correctness (ephemeral, tenant
  isolation), not load.
- **Whether the CLI/SDK gap noted above (`buzz-cli`/`buzz-sdk` carrying no
  typing support) is an intentional scope decision or an unfilled gap** was
  not established from any issue, PR, or design document — it is reported
  here only as an observed absence in the code.
