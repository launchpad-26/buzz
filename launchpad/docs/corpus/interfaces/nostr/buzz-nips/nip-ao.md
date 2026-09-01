---
id: interfaces-nostr-buzz-nips-nip-ao
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "docs/nips/NIP-AO.md is Buzz's own custom-NIP proposal document titled 'NIP-AO: Agent Observability', carrying the stability badges 'draft optional', and its Motivation section states it 'defines ephemeral, encrypted event kinds for streaming internal session telemetry between AI agent processes and their owners' desktop clients via Nostr relays' so that telemetry is never 'stored on any relay or visible to third parties'."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "docs/nips/NIP-AO.md defines exactly one event kind, 24200 ('Agent Observer Frame'), and states it 'falls in the ephemeral range (20000-29999) defined by NIP-01' and that 'Relays MUST NOT persist it'."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-core/src/kind.rs declares `pub const KIND_AGENT_OBSERVER_FRAME: u32 = 24200;` with the doc comment 'Ephemeral: owner-scoped encrypted agent observer telemetry and control frame', and separately declares `EPHEMERAL_KIND_MIN = 20000` / `EPHEMERAL_KIND_MAX = 29999`, confirming 24200 falls inside the ephemeral range the spec claims for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:456-469"
  - statement: "crates/buzz-relay/src/handlers/event.rs's `handle_agent_observer_event` carries the doc comment 'These frames bypass storage and are routed as global ephemeral events', and its body never calls any database insert or `ingest_event` persistence path — it verifies the signature, checks freshness and authorization, then calls `state.pubsub.publish_event` and `fan_out_event_to_local_subscribers` directly, confirming the spec's 'Relays MUST NOT persist' and 'fan out ... only via in-memory pub/sub, never via a database write path' clauses against actual relay code, not merely the spec text."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:947-1101"
  - statement: "crates/buzz-relay/src/subscription.rs's tests `test_global_p_kind_index_fan_out_targets_matching_p` and `test_global_p_kind_index_removal_cleanup` confirm kind 24200 subscriptions are routed through an in-memory `global_kind_index`/p-tag index inside `SubscriptionRegistry`, not through any storage-backed query path, matching the spec's in-memory-pub/sub-only fan-out clause."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/subscription.rs:1573-1606"
  - statement: "docs/nips/NIP-AO.md's Event Structure section requires 'exactly one `p` tag, exactly one `agent` tag, and exactly one `frame` tag' with `frame` restricted to `telemetry` or `control`, and states relays SHOULD silently drop events with unrecognized `frame` values while returning OK to the publisher."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-core/src/observer.rs declares the exact tag-name and frame-value constants the spec's tag shape names: `OBSERVER_AGENT_TAG = \"agent\"`, `OBSERVER_FRAME_TAG = \"frame\"`, `OBSERVER_FRAME_TELEMETRY = \"telemetry\"`, `OBSERVER_FRAME_CONTROL = \"control\"`, and crates/buzz-relay/src/handlers/event.rs's `single_tag_content` helper rejects an event carrying zero or more than one of a named tag with 'invalid: observer frame missing {tag} tag' / 'invalid: observer frame has multiple {tag} tags', enforcing the spec's 'exactly one' cardinality in code, not only in prose."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/observer.rs:13-19"
      - "crates/buzz-relay/src/handlers/event.rs:1149-1164"
  - statement: "crates/buzz-relay/src/handlers/event.rs's `agent_observer_route` derives direction from tag values rather than trusting a client-asserted role: telemetry requires `event.pubkey == agent` and `recipient != agent`; control requires `recipient == agent` and `event.pubkey != agent`; any other combination is rejected with 'invalid: observer frame must be agent-to-owner telemetry or owner-to-agent control'; and an event whose `frame` tag does not match the direction its pubkey/recipient combination implies is silently dropped (`Ok(None)`) rather than erroring, matching the spec's 'relays SHOULD silently drop events with unrecognized frame values' forward-compatibility clause."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1103-1141"
  - statement: "docs/nips/NIP-AO.md's Encryption section requires all `content` fields be NIP-44 v2 (XChaCha20-Poly1305 over a secp256k1 ECDH shared secret), with telemetry encrypted `(agent_privkey, owner_pubkey)` and control encrypted `(owner_privkey, agent_pubkey)`, and states the decrypted payload MUST NOT exceed 65,535 bytes."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-core/src/observer.rs's `encrypt_observer_payload`/`decrypt_observer_payload` implement exactly that: `nip44::encrypt`/`nip44::decrypt` keyed by `(sender_keys.secret_key(), recipient)`, `nip44::Version::V2`; `OBSERVER_MAX_PLAINTEXT_LEN = 65_535` bytes matching the spec's decrypted-payload limit; `content_looks_like_nip44` bounds ciphertext length to `NIP44_MIN_CONTENT_LEN = 132` / `NIP44_MAX_CONTENT_LEN = 87_472` bytes, a precise envelope the spec text itself does not state numerically; and the plaintext buffer is explicitly `zeroize()`d after encryption/decryption, matching the spec's 'Plaintext SHOULD be zeroized from memory immediately after encrypt/decrypt' recommendation."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/observer.rs:20-105"
  - statement: "docs/nips/NIP-AO.md's Decrypted Payload section states a telemetry frame's `content` decrypts to an object with REQUIRED fields `seq, timestamp, kind, payload` and OPTIONAL fields `agentIndex, channelId, sessionId, turnId`, and that `seq` is monotonically increasing per session for drop detection."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-acp/src/observer.rs's `ObserverEvent` struct (the concrete Rust type the harness serializes into `content` before NIP-44 encryption) carries `#[serde(rename_all = \"camelCase\")]` and fields `seq: u64` (from an `AtomicU64` bumped on every `emit`), `timestamp: String` (RFC3339 via `chrono::Utc::now().to_rfc3339()`), `kind: String`, `agent_index: Option<usize>`, `channel_id: Option<String>`, `session_id: Option<String>`, `turn_id: Option<String>`, and `payload: serde_json::Value` — matching the spec's seven named fields field-for-field once camelCase-serialized."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/observer.rs:56-79"
  - statement: "crates/buzz-acp/src/observer.rs's `ObserverEvent` additionally serializes an eighth field, `started_at: Option<String>` (camelCase `startedAt`, `#[serde(skip_serializing_if = \"Option::is_none\")]`), that docs/nips/NIP-AO.md's Decrypted Payload section does not mention anywhere in its field list — a real divergence between the merged NIP text and the harness's actual wire payload, not reconciled by this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/observer.rs:56-79"
      - "docs/nips/NIP-AO.md"
  - statement: "docs/nips/NIP-AO.md's Frame Kinds table names four telemetry `kind` values (`acp_read`, `acp_write`, `turn_started`, `session_resolved`) and states unknown `kind` values MUST be ignored by clients."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "docs/nips/NIP-AO.md's Control section states the only defined control `type` is `cancel_turn`, decrypting to `{\"type\": \"cancel_turn\", \"channelId\": \"<channel_uuid>\"}`, with unrecognized `type` values MUST be ignored."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-acp/src/lib.rs's control-frame dispatcher matches `Some(\"cancel_turn\") => handle_cancel_turn_control(...)`, and `handle_cancel_turn_control` logs `\"observer cancel_turn control frame missing valid channelId\"` and no-ops when the field is absent/invalid rather than erroring, matching the spec's 'ignore unrecognized type values' and 'best-effort, advisory, idempotent' framing for control commands."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/lib.rs:1132-1325"
  - statement: "docs/nips/NIP-AO.md's Authorization section requires, for both directions, that the relay 'verify `is_agent_owner(agent, owner)` via authenticated ownership lookup' and states '#p tag matching alone is insufficient' and unauthorized attempts 'MUST be rejected with `AUTH required`'."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-relay/src/handlers/event.rs's `handle_agent_observer_event` checks a fast path (the connection's own NIP-42-authenticated `agent_owner_pubkey` context) and otherwise calls `state.db.is_agent_owner(community, agent_bytes, owner_bytes)` through an `observer_owner_cache`, and rejects with the relay message `(\"OK\", id, false, \"restricted: observer frame is not authorized for this agent owner\")` when that check fails — a database-backed ownership lookup, not a bare tag match, matching the spec's authorization requirement in actual relay code."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1007-1061"
  - statement: "The rejection-message wording actually returned by the relay ('restricted: observer frame is not authorized for this agent owner') differs from the exact literal string docs/nips/NIP-AO.md's prose names ('AUTH required') for the same failure case — Buzz's own relay message-string convention (`restricted:`/`invalid:`/`rate-limited:` prefixes) rather than the spec's illustrative wording, confirmed by a passing test asserting the exact returned frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1415-1436"
  - statement: "crates/buzz-core/src/kind.rs's `P_GATED_KINDS` array includes `KIND_AGENT_OBSERVER_FRAME` alongside `KIND_MEMBER_ADDED_NOTIFICATION`, `KIND_MEMBER_REMOVED_NOTIFICATION`, `KIND_GIFT_WRAP`, `KIND_DM_VISIBILITY`, `KIND_AGENT_TURN_METRIC`, and crates/buzz-relay/src/handlers/req.rs's `p_gated_filters_authorized` rejects a REQ filter that names a P-gated kind without a matching `#p` tag equal to the authenticated pubkey — enforcing the spec's 'Clients subscribe with {\"kinds\": [24200], \"#p\": [\"<own_pubkey>\"]}' contract at the relay's REQ handler, not merely as client-side convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:159-169"
      - "crates/buzz-relay/src/handlers/req.rs:1182-1212"
  - statement: "docs/nips/NIP-AO.md's Relay Behavior section states relays SHOULD enforce a 100 events/second per-agent rate limit and are RECOMMENDED to reject events whose `created_at` falls outside a +/-5-minute freshness window."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "crates/buzz-relay/src/handlers/event.rs's `observer_frame_rate_limited` implements a per-community, per-agent-pubkey sliding one-second window that rejects once a counter exceeds 100 (`*count > 100`), scoped explicitly by community id so 'an agent key active in one tenant does not consume another tenant's logical rate budget' (a per-community scoping the spec text does not itself state); and `handle_agent_observer_event` separately rejects an event whose `created_at` differs from `chrono::Utc::now()` by more than 300 seconds with 'invalid: observer frame timestamp outside +/-5 minute freshness window', matching the spec's two RECOMMENDED relay checks with concrete numeric thresholds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:921-991"
      - "crates/buzz-relay/src/handlers/event.rs:1325-1345"
  - statement: "Rate limiting applies only to the telemetry direction: `handle_agent_observer_event` gates the rate-limit check behind `matches!(route.direction, AgentObserverDirection::Telemetry)`, with a code comment stating control frames 'bypass the limiter — they are rare and must not be starved by bursty telemetry from the agent' — an asymmetry the spec's own Relay Behavior text states only as a blanket 'per agent pubkey' rule without naming this direction-specific carve-out."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1063-1076"
  - statement: "crates/buzz-relay/src/handlers/event.rs additionally gates EVENT submission of kind 24200 on the connection's OAuth-style scopes before reaching `handle_agent_observer_event` at all: when the connection's `scopes` are non-empty and do not contain `buzz_auth::Scope::MessagesWrite`, the relay rejects with 'restricted: insufficient scope for agent observer frames' — a scope check the NIP-AO spec text does not mention, layered on top of the spec's agent-owner authorization."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:680-692"
  - statement: "docs/nips/NIP-AO.md's Relationship to Other NIPs section states NIP-42 is 'Recommended for relay-side authentication gating', and a relay test builds the authenticated connection state for observer-frame handling with `auth_method: buzz_auth::AuthMethod::Nip42`, confirming NIP-42 as the actual authentication method exercised for this kind's own tests, not merely a spec recommendation."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
      - "crates/buzz-relay/src/handlers/event.rs:1394-1406"
  - statement: "crates/buzz-sdk/src/builders.rs's `build_agent_observer_frame(recipient_pubkey, agent_pubkey, frame, encrypted_content)` is the typed SDK constructor for a kind-24200 event: it rejects a `frame` value other than `\"telemetry\"`/`\"control\"` and rejects `encrypted_content` that fails `content_looks_like_nip44`, before building the `p`/`agent`/`frame` tags and the `Kind::Custom(KIND_AGENT_OBSERVER_FRAME as u16)` event."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:247-282"
  - statement: "desktop/src/shared/api/observerRelay.ts's `subscribeToAgentObserverFrames` subscribes with `kinds: [KIND_AGENT_OBSERVER_FRAME]`, `\"#p\": [ownerPubkey]`, `limit: 1000` and `since: now - 300` seconds (`OBSERVER_LIVE_LOOKBACK_SECS`), with an inline comment stating the 300-second lookback exists so that a turn-start frame emitted before the desktop subscribed is not silently missed, and that the archive backfill path deduplicates any frame already ingested — a concrete, stated divergence from docs/nips/NIP-AO.md's own Client Behavior text, 'Clients SHOULD subscribe with since=<now>; historical replay is not supported.'"
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/observerRelay.ts"
      - "docs/nips/NIP-AO.md"
  - statement: "docs/nips/NIP-AO.md closes with a Reference Implementation link to block/sprout PR #421, an external (non-buzz) repository this node's own evidence checking cannot open or verify — reported here as the spec's own stated pointer, not independently confirmed."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-AO.md"
  - statement: "node.schema.json's `type` enum has thirteen members and `interfaces-events` is its only interface/event-surface value; both launchpad/docs/corpus/templates/interface.md and templates/event-kind.md (both merged on origin/launchpad at the recorded revision) state that a real instance node built from either template carries `type: interfaces-events`, so this node's type choice is not a guess between two possible enum values."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "This node's subject is stateable as a single 'kind: 24200' wire contract — templates/event-kind.md's own stated criterion for choosing its template over templates/interface.md — but issue #993 explicitly directs a node at the path launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-ao.md, under the interfaces/ tree; this node follows the issue's explicit path and treats the event-kind template's Required sections (kind identity, referenced NIP, range/classification, tag shape, content semantics, access control, worked examples) as the right content shape for a single-kind NIP regardless of which of the two templates' directory convention it sits under, since both share the identical `type: interfaces-events` value and neither template's own boundary section resolves which wins when an issue's assigned path and a subject's natural template shape disagree."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
      - "launchpad/docs/corpus/templates/event-kind.md"
    confidence: 0.7
  - statement: "Issue #993 (task: document interfaces/nostr/buzz-nips/nip-ao.md) requires exactly one hand-authored canonical document at this path; schema-valid front matter with a stable id, type, status, origin, audiences, evidence and typed relationships; one independently maintainable node; every substantive claim traceable and classified; links to relevant implementation/verification/spec/neighboring nodes without duplicating them; a check against the recorded revision; a clean local validator run; and explicit coverage of inputs/messages, outputs/responses, error/rejection behavior, auth, versioning/compatibility, ordering/idempotency where applicable, a link to the authoritative spec, and at least one valid and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#993 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
---

# NIP-AO: Agent Observability — interface

This node documents Buzz's custom NIP-AO extension: the boundary across which an AI
agent process and its owner's desktop client exchange ephemeral, NIP-44-encrypted
session telemetry and turn-control commands over a Nostr relay, using a single
dedicated ephemeral event kind (24200) that the relay never persists and fans out
only through in-memory pub/sub. One side is a managed agent harness (`buzz-acp`)
publishing telemetry and consuming control frames; the other is the owner's desktop
client, publishing control frames and subscribing to telemetry. The wire format is a
WebSocket-delivered Nostr event whose `content` is NIP-44 v2 ciphertext.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Publish a telemetry frame (agent → owner) | `docs/nips/NIP-AO.md` (spec); `crates/buzz-core/src/observer.rs#encrypt_observer_payload`; `crates/buzz-acp/src/observer.rs#ObserverHandle::emit`; `crates/buzz-sdk/src/builders.rs#build_agent_observer_frame`; relay entry point `crates/buzz-relay/src/handlers/event.rs#handle_agent_observer_event` / `#agent_observer_route` | Agent-signed kind-24200 event, `frame=telemetry`, `pubkey`=agent, `p`=owner, `agent`=agent; `content` is NIP-44-encrypted `ObserverEvent` JSON. |
| Publish a control frame (owner → agent) | `docs/nips/NIP-AO.md` (spec); `crates/buzz-sdk/src/builders.rs#build_agent_observer_frame`; consumed by `crates/buzz-acp/src/lib.rs#handle_cancel_turn_control` | Owner-signed kind-24200 event, `frame=control`, `pubkey`=owner, `p`=agent, `agent`=agent (target); `content` decrypts to `{"type": "cancel_turn", "channelId": ...}`. |
| Subscribe to observer frames (owner) | `docs/nips/NIP-AO.md` §Client Behavior; `desktop/src/shared/api/observerRelay.ts#subscribeToAgentObserverFrames`; relay-side gate `crates/buzz-relay/src/handlers/req.rs#p_gated_filters_authorized`; fan-out `crates/buzz-relay/src/subscription.rs` (`global_kind_index`) | `REQ` with `kinds:[24200]`, `#p:[owner_pubkey]`; relay rejects a bare-kind filter with no matching `#p` tag; matching events delivered only via in-memory pub/sub, never a stored-event query. |

## Kind identity, range and tag shape

- **Kind**: 24200, constant `KIND_AGENT_OBSERVER_FRAME` in `crates/buzz-core/src/kind.rs:469`.
- **Range**: ephemeral (20000-29999) per NIP-01, confirmed against `kind.rs`'s own `EPHEMERAL_KIND_MIN`/`MAX` constants — relays MUST NOT persist it.
- **Referenced spec**: `docs/nips/NIP-AO.md` — Buzz's own custom-NIP proposal document (no existing community NIP governs this kind).
- **Tags**: exactly one `p` (recipient), exactly one `agent` (the managed agent's pubkey, present in both directions so a relay can resolve the owning agent regardless of who signed), exactly one `frame` (`telemetry` or `control`); an `h` tag MAY be present when the session is scoped to a NIP-29 group. Cardinality is enforced in code (`single_tag_content`), not only documented in prose.

## Content field semantics

`content` is always NIP-44 v2 ciphertext (never plaintext), encrypted `(agent_privkey,
owner_pubkey)` for telemetry and `(owner_privkey, agent_pubkey)` for control. The
decrypted payload is one of two JSON shapes depending on `frame`:

- **`frame=telemetry`** decrypts to an `ObserverEvent`: REQUIRED `seq` (monotonic
  per-session counter), `timestamp` (RFC3339), `kind` (one of `acp_read`, `acp_write`,
  `turn_started`, `session_resolved`, or any value a client MUST otherwise ignore), and
  `payload` (kind-specific JSON, may be `{}`); OPTIONAL `agentIndex`, `channelId`,
  `sessionId`, `turnId`, each nullable. The concrete Rust type serialized into this
  field, `crates/buzz-acp/src/observer.rs`'s `ObserverEvent`, additionally carries an
  optional `startedAt` field the spec text never names — a real spec/code divergence,
  not reconciled here.
- **`frame=control`** decrypts to `{"type": "cancel_turn", "channelId": "<uuid>"}`; the
  only defined `type` is `cancel_turn`, and any other value MUST be ignored by the
  receiving agent.

## Access control and storage model

- **Not stored.** Ephemeral kind; the relay's own handler explicitly bypasses any
  ingestion/persistence path and routes only through in-memory pub/sub
  (`state.pubsub.publish_event` + `fan_out_event_to_local_subscribers`).
- **P-gated on read.** `KIND_AGENT_OBSERVER_FRAME` is a member of `kind.rs`'s
  `P_GATED_KINDS`; the relay's REQ handler rejects a subscription filter naming this
  kind unless it also carries a `#p` tag equal to the authenticated pubkey — the spec's
  "`#p` tag matching alone is insufficient [for publish]" concern is publish-side; the
  read-side gate is this P-gated-filter check.
- **Gated on write by two independent checks**, both enforced in relay code before a
  frame is accepted: (1) an OAuth-style scope check (`MessagesWrite`, when the
  connection's token carries scopes at all) and (2) a database-backed
  `is_agent_owner(agent, owner)` lookup (cached, and fast-pathed when the connection's
  own NIP-42-authenticated session already carries the matching owner context) —
  never a bare tag comparison.
- **Client-authored, both directions.** The agent signs telemetry; the owner (or an
  owner-authenticated client) signs control frames.

## Contract and stability

- **Versioning/compatibility.** The spec is marked `draft` `optional` in
  `docs/nips/NIP-AO.md`'s own title line. Forward compatibility for new `frame`,
  telemetry `kind`, or control `type` values is by silent-ignore convention, enforced
  in relay code for `frame` (`agent_observer_route` returns `Ok(None)` on a
  frame/direction mismatch, and the caller replies `OK true` with no message rather
  than an error) and left to client-side dispatch for telemetry `kind`/control `type`.
- **Ordering/idempotency.** `seq` is a per-process, per-session monotonically
  increasing counter (`AtomicU64`, starts at 1) intended for drop detection on the
  consuming side, not a relay-enforced ordering guarantee — the relay does not persist
  or replay these events, so ordering across a reconnect is the consuming client's
  responsibility. Control commands are explicitly best-effort: the spec states they
  "SHOULD be treated as advisory with idempotent semantics" and "MUST NOT rely on
  guaranteed delivery," and the harness's own `cancel_turn` handler no-ops rather than
  erroring on a missing/invalid `channelId`, consistent with that framing.
- **Error/rejection behavior.** The relay replies with a Nostr `OK` frame
  (`[event_id, false, "<reason>"]`) for every rejection case, using its own
  message-string convention rather than the spec's illustrative `AUTH required`
  wording: `"invalid: observer content must be NIP-44 encrypted"`, `"invalid: observer
  frame missing/has multiple <tag> tag(s)"`, `"invalid: observer frame must be
  agent-to-owner telemetry or owner-to-agent control"`, `"invalid: observer frame
  timestamp outside +/-5 minute freshness window"`, `"restricted: insufficient scope
  for agent observer frames"`, `"restricted: observer frame is not authorized for this
  agent owner"`, `"rate-limited: observer frame rate exceeded (100/sec per agent)"`. An
  unrecognized `frame` value is the one case that is *not* an error: it is silently
  dropped with `OK true`.
- **Rate and freshness.** 100 events/second per (community, agent pubkey) for
  telemetry only — control frames explicitly bypass the limiter so they are not
  starved by bursty telemetry — and a +/-5-minute `created_at` freshness window,
  rejecting frames outside it (replay mitigation).
- **Authentication.** NIP-42 is the authentication method actually exercised in this
  kind's own relay tests; the spec recommends it for relay-side gating generally.

## Boundary

This node does not describe:

- **NIP-01's base event envelope, tag grammar, or ephemeral-range semantics** in
  general — only where this kind sits against them. NIP-01 itself is the source for
  those.
- **NIP-44's encryption algorithm** in general — only which keys derive the
  conversation secret for each direction of this kind. NIP-44 itself is the source for
  the cipher construction.
- **A domain-expert, field-by-field parameter catalogue** beyond what `docs/nips/NIP-AO.md`
  already states — this node points at that spec rather than re-deriving it.
- **The wider ACP session/turn lifecycle** that produces the telemetry `payload` this
  kind carries (`acp_read`/`acp_write`/`turn_started`/`session_resolved` bodies) — this
  node describes the transport envelope and dispatch contract, not the harness's
  internal session state machine.
- **`buzz-acp`'s in-process, pre-encryption observer bus** (`ObserverHandle`,
  `ObserverContext`, the 1000-event in-memory replay buffer) beyond stating that it is
  the source of the `ObserverEvent` this kind's telemetry frames carry — that bus has
  no wire format of its own and is process-local infrastructure, not part of this
  interface's contract with the outside world.

## Relationships

- `implements: corpus-template-interface` — this node is authored against
  `launchpad/docs/corpus/templates/interface.md`'s required-sections shape (confirmed
  resolvable: that template is merged on `origin/launchpad` at the recorded revision).
- No `references`/`depends-on` edge to any sibling `buzz-nips` node is declared: at the
  recorded revision, `origin/launchpad`'s corpus tree has no `interfaces/` subtree and
  no other NIP-AA/AE/AM/AP/etc. node exists to link to. NIP-AO's own
  "Relationship to Other NIPs" section separately names NIP-01, NIP-29, NIP-42 and
  NIP-44 as protocol dependencies and a proposed external "NIP-XX (PR #2226)" as a
  complementary, non-overlapping plane (agent *output* vs. this NIP's *observability*)
  — those are prose-mentioned above rather than declared as corpus relationships,
  since none of NIP-01/29/42/44/NIP-XX is itself a corpus node with a resolvable id.

## Examples

**Valid — telemetry frame, `acp_write`.** Wire event and decrypted payload, taken
directly from `docs/nips/NIP-AO.md`'s own worked example (the plaintext below is
shown only for illustration; on the wire, `content` is NIP-44 v2 ciphertext):

```json
{
  "kind": 24200,
  "pubkey": "agent_pubkey_hex",
  "created_at": 1777464041,
  "content": "<NIP-44 v2 ciphertext>",
  "tags": [
    ["p", "owner_pubkey_hex"],
    ["agent", "agent_pubkey_hex"],
    ["frame", "telemetry"]
  ],
  "sig": "..."
}
```

Decrypted payload:

```json
{
  "seq": 42,
  "timestamp": "2026-04-29T12:00:41.500Z",
  "kind": "acp_write",
  "agentIndex": 0,
  "channelId": "52a85618-0f8f-4542-94ec-599e6e1c6f2e",
  "sessionId": "a1b2c3d4",
  "turnId": "e5f6g7h8",
  "payload": {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": { "name": "shell", "arguments": { "command": "ls -la" } }
  }
}
```

**Failure — unauthorized owner.** `crates/buzz-relay/src/handlers/event.rs`'s test
`observer_frame_rate_limiter_is_scoped_by_community` (despite its name, its final
assertions cover this case) builds a validly-signed, validly-shaped telemetry frame
from a real agent key to a real owner key, but registers the connection's
`agent_owner_pubkey` as unset and caches `is_agent_owner(community_b, agent, owner)
= false` for the connection's own community. `handle_agent_observer_event` rejects it
with the exact relay frame:

```json
["OK", "<event_id>", false, "restricted: observer frame is not authorized for this agent owner"]
```

confirming the spec's authorization requirement is enforced even for an
otherwise-well-formed, correctly-encrypted, correctly-tagged event — the failure is
authorization, not shape.

## Scope and omissions

**This node covers** the kind-24200 Agent Observability wire contract end to end:
identity and range, tag shape, encrypted content semantics for both frame directions,
access control (storage, read-gating, write-gating), and the contract a caller may
rely on (versioning, ordering/idempotency, error/rejection behavior, rate/freshness,
authentication) — cross-checked against the actual relay, SDK, harness and desktop
client code that implements it, not restated from the spec alone.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-01's base event envelope and ephemeral-range rules in general | `https://github.com/nostr-protocol/nips` (NIP-01), external |
| NIP-44's encryption construction in general | `https://github.com/nostr-protocol/nips` (NIP-44), external |
| NIP-42 relay authentication in general | `https://github.com/nostr-protocol/nips` (NIP-42), external |
| The proposed agent-output-plane NIP referenced as "NIP-XX (PR #2226)" | Not a corpus node at the recorded revision |
| The ACP session/turn lifecycle whose activity this kind's telemetry reports on | Not yet a corpus node at the recorded revision |
| Whether this subject should instead have been authored from `templates/event-kind.md` given its single-kind identity, versus `templates/interface.md` per the issue's assigned path | Flagged in this node's own evidence ledger (INFERENCE entry) and in this task's plan `OPEN` section; not settled here |

**Expected but not verified when this node was written:**

- **`block/sprout` PR #421**, the spec's own named reference implementation, was not
  opened — it is an external, non-`buzz` repository outside this evidence-checking
  session's reach.
- **No live relay/harness/desktop round trip of a kind-24200 event was exercised.**
  Every claim above is grounded in reading the relay handler, SDK builder, harness
  observer module, and desktop subscription code and their own unit tests directly —
  not in running the system end to end.
- **Whether `origin/launchpad`'s `interfaces/` tree gains further `buzz-nips` sibling
  nodes before this one merges was not re-checked at commit time** beyond the single
  `git ls-tree` run recorded in this node's ledger; a reviewer merging this alongside
  other in-flight corpus PRs should re-run that check before assuming the `relationships`
  list above is still complete.
