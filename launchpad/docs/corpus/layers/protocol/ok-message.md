---
id: layers-protocol-ok-message
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "RelayMessage::ok(event_id, accepted, message) serializes the four-element JSON array [\"OK\", event_id, accepted, message] and returns it as a String, so the OK frame carries exactly one event id, one boolean and one free-text message."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "protocol.rs's module documentation records these frames as NIP-01 client/relay messages, and the ok constructor's own doc comment describes it as acknowledging an EVENT submission."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "No upstream NIP-01 specification text exists anywhere in this repository; docs/nips/ holds only Buzz's own two-letter custom NIPs, so any claim about what NIP-01 requires cannot rest on a repository path."
    entry_class: FACT
    evidence:
      - "find_iname('NIP-01*', path='.', exclude='node_modules') -> no matches"
      - "docs/nips/NIP-OA.md"
  - statement: "There are 30 RelayMessage::ok call sites in crates/: 20 in buzz-relay/src/handlers/event.rs, 7 in buzz-relay/src/handlers/auth.rs, 1 in buzz-relay/src/state.rs, and 2 in buzz-relay/src/protocol.rs that both sit inside its #[cfg(test)] mod tests, leaving 28 production emitters."
    entry_class: FACT
    evidence:
      - "grep_rn('RelayMessage::ok(', path='crates/') -> 30 matches: event.rs 20, auth.rs 7, state.rs 1, protocol.rs 2 (both below the #[cfg(test)] boundary)"
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "An accepted OK carries the empty string in its message field on every ordinary success path: ingest_event's terminal success returns IngestResult { accepted: true, message: String::new() }, and the ephemeral, agent-observer and NIP-42 AUTH paths each call RelayMessage::ok(id, true, \"\") directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "The general deduplication path reports a duplicate as accepted: true with message \"duplicate:\", and every command_executor.rs PersistResult::Duplicate arm likewise returns accepted: true with \"duplicate: already processed\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/command_executor.rs"
  - statement: "Two entity-specific duplicate paths in ingest.rs instead report accepted: false — \"duplicate: channel already exists\" and \"duplicate: reaction already exists\" — so the duplicate: prefix does not map to a single value of the accepted flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "One accepted path carries a non-empty non-duplicate message: a NIP-43 relay-leave request returns IngestResult { accepted: true, message: \"info: you have left this relay\" }."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Eight machine-readable reason prefixes appear on OK emit paths — auth-required:, invalid:, restricted:, blocked:, rate-limited:, error:, duplicate: and info: — and no other prefix does; a census of quoted prefixes across buzz-relay's handlers and state.rs finds invalid: 141, error: 67, restricted: 39, duplicate: 11, blocked: 11, auth-required: 8 and rate-limited: 1 occurrence, with zero for pow: and unsupported:."
    entry_class: FACT
    evidence:
      - "grep_rhoE('\"(auth-required|invalid|restricted|blocked|rate-limited|duplicate|error|pow|unsupported|deleted|mute|nip05|too-fast):', path='crates/buzz-relay/src/handlers/ crates/buzz-relay/src/state.rs') -> invalid 141, error 67, restricted 39, duplicate 11, blocked 11, auth-required 8, rate-limited 1; all other candidates 0"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "rate-limited: reaches an OK from exactly one emitter, the agent-observer telemetry limiter in event.rs, which sends \"rate-limited: observer frame rate exceeded (100/sec per agent)\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "The relay acknowledges NIP-42 AUTH events with OK as well as EVENT submissions: handle_auth emits OK true on success and OK false carrying auth-required:, blocked:, restricted: or error: on each denial."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "ingest_event's error taxonomy is collapsed onto OK false at the WebSocket seam: IngestError::Rejected and IngestError::AuthFailed forward their own message text, while IngestError::Internal is replaced with the fixed string \"error: internal server error\" so system detail is not leaked over the socket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Every IngestResult in ingest.rs sets event_id to event_id_hex, the hex id of the event the client submitted, so an OK produced by the ingest pipeline always echoes the submitted id."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ConnectionManager::disconnect_pubkey emits an unsolicited OK false whose event_id is supplied by the caller rather than by the recipient, and its sole production caller passes the moderator's ban-command event id, so a banned member receives an OK naming an event they never submitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "disconnect_pubkey's doc comment states that a synthetic all-zero id is used because the ban has no triggering client event, which its only production caller contradicts by passing event.id.to_hex() of the moderation command."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
      - "crates/buzz-relay/src/handlers/moderation_commands.rs"
  - statement: "Ban-path OK frames are queued on the connection's control channel with try_send rather than the ordinary data channel, so the send loop drains the reason ahead of the Close it emits on cancel, and a full control buffer silently drops the reason frame while the socket still closes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "buzz-ws-client's parse_relay_message defaults accepted to false when element 2 is absent or is not a boolean, and defaults message to the empty string when element 3 is absent, so a malformed OK is read as a rejection with no reason rather than raising a parse error."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "buzz-cli reads the accepted flag and the message field as two separate checks: parse_write_response and submit_engram both fail outright when accepted is false, then map an accepted response whose message starts with \"duplicate:\" onto a Conflict error rather than reporting success."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/mod.rs"
      - "crates/buzz-cli/src/commands/mem.rs"
  - statement: "Because duplicate: and info: ride on accepted: true while duplicate: also appears on accepted: false, a client that branches on the accepted flag alone cannot distinguish a stored write from a deduplicated one, which is why buzz-cli inspects both fields."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-cli/src/commands/mod.rs"
      - "crates/buzz-cli/src/commands/mem.rs"
    confidence: 0.9
  - statement: "protocol.rs's two OK unit tests assert the serialized shape for both outcomes — the accepted case checks element 0 is \"OK\", element 2 is true and element 3 is empty; the rejected case checks element 2 is false and element 3 is the message passed in — but both exercise the constructor only and assert nothing about which prefix any handler chooses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "No wire-frame prefix assertion was found in the relay end-to-end suite: searching crates/buzz-test-client/tests/e2e_relay.rs for OK returns only HTTP status-code comparisons and prose comments."
    entry_class: FACT
    evidence:
      - "grep_n('OK', path='crates/buzz-test-client/tests/e2e_relay.rs') -> 7 matches, all reqwest::StatusCode::OK comparisons or comments"
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "No RelayMessage::closed call site in crates/ passes a duplicate: message, and the string \"pow:\" does not occur anywhere in crates/, yet the desktop client's classifyRelayClosed treats both prefixes as terminal CLOSED reasons."
    entry_class: FACT
    evidence:
      - "grep_rn('RelayMessage::closed(', path='crates/') -> 28 matches, 0 containing 'duplicate'"
      - "grep_rn('pow:', path='crates/') -> 0 matches"
      - "desktop/src/shared/api/relayClosedPolicy.ts"
  - statement: "The sibling Feature #609 tasks covering the EVENT, NOTICE and CLOSED frames and the event id are filed as launchpad-26/buzz#1154, #1160, #1147 and #1152 and are not merged on origin/launchpad at the recorded revision, so no relationship is declared to them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1161 dispatch brief for Feature #609"
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: verification-contracts-nostr
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: implementation-crates-buzz-ws-client
---

# The `OK` message

An `OK` message is the relay's per-event verdict: a four-element JSON array
`["OK", <event_id>, <true|false>, <message>]` that tells one client, on the socket
it submitted from, whether one specific event was taken and — when it was not — why,
in a prefix a program can branch on.

## Definition

`RelayMessage::ok(event_id, accepted, message)` in
`crates/buzz-relay/src/protocol.rs` is the single constructor. It serializes
`["OK", event_id, accepted, message]` and returns the frame as a `String`; there is
no builder, no optional field and no fifth element. The three payload slots each
carry one thing:

| Slot | Type | What it means |
|---|---|---|
| `event_id` | hex string | Which event this verdict is about. Every `IngestResult` sets it to `event_id_hex`, the submitted event's own id. |
| `accepted` | boolean | Whether the relay took the event. |
| `message` | string | Empty on an ordinary acceptance; otherwise a reason, prefixed. |

**`OK` is not only an `EVENT` acknowledgement.** `protocol.rs`'s constructor doc
comment calls it one, but `handlers/auth.rs` answers a NIP-42 `AUTH` event with `OK`
too — `OK true ""` when verification and the ban, allowlist and relay-membership
gates all pass, `OK false` carrying a prefixed reason on each denial. A client that
only listens for `OK` after publishing an event will miss its own auth verdict.

**`OK` is per-event and unicast.** It is addressed to the connection that submitted
the event, names one event id, and says nothing about any other client's view. It is
not a broadcast, not a subscription signal, and not a delivery receipt: an `OK true`
means the relay accepted the event, not that any subscriber has received it.

**Where the prefixes come from.** No upstream NIP text lives in this repository —
`docs/nips/` holds only Buzz's own two-letter NIPs (`NIP-OA.md`, `NIP-AA.md`, and so
on) and a search for `NIP-01*` returns nothing. So the vocabulary below is stated as
what Buzz's own emitters actually send, enumerated from the call sites, and not as a
restatement of what any specification requires.

## The reason-prefix vocabulary

Across the 28 production `RelayMessage::ok` emitters — 20 in
`handlers/event.rs`, 7 in `handlers/auth.rs`, 1 in `state.rs` — plus the
`IngestResult` and `IngestError` values those emitters forward, exactly eight
prefixes reach a client on an `OK`:

| Prefix | Typical `accepted` | Where it is emitted, and for what |
|---|---|---|
| *(empty message)* | `true` | Ordinary acceptance. `ingest.rs` returns `message: String::new()`; the ephemeral, agent-observer and AUTH paths pass `""` literally. |
| `auth-required:` | `false` | `event.rs` for an unauthenticated `EVENT`; `auth.rs` for an `AUTH` sent while already authenticated, after a failed auth, or failing verification. |
| `invalid:` | `false` | The client's event is malformed or disallowed — pubkey not matching the authenticated identity, an `AUTH` kind submitted via `EVENT`, an observer frame outside the ±5-minute freshness window, or any `IngestError::Rejected`. |
| `restricted:` | `false` | An authorization refusal that is not a ban — insufficient scope for ephemeral or observer writes, a fenced community, an observer frame not authorized for its owner, a connection that is not a relay member. |
| `blocked:` | `false` | A durable community ban, from the `auth.rs` ban seam, from ingest, and from the live-disconnect frame. |
| `rate-limited:` | `false` | Exactly one emitter: the agent-observer telemetry limiter in `event.rs`, at 100 frames per second per agent. |
| `error:` | `false` | A relay-side fault. `IngestError::Internal` is deliberately replaced with the fixed text `"error: internal server error"` at the WebSocket seam so database and system detail never reach the socket. |
| `duplicate:` | **both** | See below. |
| `info:` | `true` | One emitter: a NIP-43 relay-leave request returns `"info: you have left this relay"`. |

A prefix census over `buzz-relay`'s handlers and `state.rs` finds no other
candidate in use: `invalid:` 141 occurrences, `error:` 67, `restricted:` 39,
`duplicate:` 11, `blocked:` 11, `auth-required:` 8, `rate-limited:` 1, and zero for
`pow:` or `unsupported:`. (That census counts every quoted prefix in those files,
including strings that leave over HTTP or `CLOSED` rather than `OK`; the eight above
are the ones traced to an `OK` emitter.)

## `duplicate:` — the case that breaks the obvious reading

The intuitive reading of the frame is that `accepted` decides the outcome and
`message` merely explains a rejection. `duplicate:` breaks it in both directions.

The **general deduplication path** in `ingest.rs` — the `!was_inserted` branch after
the write — returns `accepted: true` with the message `"duplicate:"`. Every
`PersistResult::Duplicate` arm in `command_executor.rs` does the same with
`"duplicate: already processed"`. The event was not stored again, and the relay
still says `true`.

Two **entity-specific paths** in the same file do the opposite: `"duplicate: channel
already exists"` and `"duplicate: reaction already exists"` are both returned with
`accepted: false`.

So `duplicate:` is not a rejection prefix, nor an acceptance prefix. It is a prefix
whose meaning is completed by the flag beside it, and the two fields have to be read
together. `info:` is the second case of a non-empty message on an accepted `OK`.

This is not theoretical. `buzz-cli` reads both fields in sequence:
`parse_write_response` in `crates/buzz-cli/src/commands/mod.rs` and `submit_engram`
in `crates/buzz-cli/src/commands/mem.rs` each fail outright when `accepted` is
false, and then — on an *accepted* response — test whether the message starts with
`"duplicate:"` and raise a `Conflict` instead of reporting success. A caller that
branched on the flag alone would report a NIP-33 write as stored when a later head
had already superseded it.

## Reading an `OK` defensively

`parse_relay_message` in `crates/buzz-ws-client/src/message.rs` is the reference
consumer, and it fails soft rather than loud: a missing or non-boolean element 2
becomes `accepted: false`, and a missing element 3 becomes an empty `message`. A
truncated or malformed `OK` therefore arrives at the caller as a rejection with no
stated reason, not as a parse error. Any client that must distinguish "the relay
refused this" from "the frame was mangled" needs to establish that at a layer above
this parser.

## The unsolicited `OK`

`ConnectionManager::disconnect_pubkey` in `crates/buzz-relay/src/state.rs` uses `OK`
for something no client asked for: when a community ban is enforced live, each open
socket for the banned principal is sent an `OK false` carrying the ban reason, and
is then cancelled. Two consequences follow that no other emitter has.

**The `event_id` names someone else's event.** The id is supplied by the caller, and
the sole production caller — `handlers/moderation_commands.rs` — passes
`event.id.to_hex()` of the *moderator's* ban command. The banned member receives a
verdict addressed to an event they never submitted. (`disconnect_pubkey`'s own doc
comment says a synthetic all-zero id is used here; the caller contradicts it. Per
`ADR-0029`, executable evidence outranks documentation for how the system currently
behaves, so the behaviour above is what this node records, and the stale comment is
noted as a defect rather than resolved here.)

**Delivery is best-effort.** Both the `auth.rs` ban seam and `state.rs` queue the
frame on the connection's *control* channel with `try_send`, deliberately not the
data channel, so the send loop drains the reason ahead of the `Close` it emits on
cancel. A full control buffer drops the reason frame; the socket still closes. A
client must therefore treat a close without a preceding `OK` as possible, not as
evidence that no reason existed.

## Use cases

Read this node when you are writing anything that publishes to the relay and needs
to know whether the write landed — a CLI subcommand, an agent harness, a desktop
mutation — or when you are adding a rejection path to the relay and need to pick a
prefix that existing clients already understand. The two things it is most useful
for are the ones easiest to get wrong: that an accepted `OK` can still carry a
message, and that the prefix set is a closed vocabulary derived from emit sites
rather than an open-ended human string.

## Scope and omissions

**This node covers** the `OK` frame's shape, the meaning of each of its three
payload slots, the eight reason prefixes that reach a client on it, the
`duplicate:`/`info:` cases where an accepted `OK` carries text, how the reference
client parses the frame, and the one emitter that sends `OK` unsolicited.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The ingest pipeline that *decides* the verdict — validation order, the write path, dedup mechanics | `architecture-flows-event-ingestion` |
| The `EVENT`, `NOTICE`, `CLOSED`, `EOSE`, `COUNT` and `AUTH` frames, and the event id itself | Separate unmerged tasks in Feature #609 (#1154, #1160, #1147, #1152) — no relationship is declared to them because none is merged on `origin/launchpad` |
| The HTTP `POST /events` bridge, which returns the same `IngestResult` as a JSON `{event_id, accepted, message}` object rather than an `OK` frame | Not filed as its own task at the recorded revision |
| Kind-by-kind rejection conditions — which validation rule produces which `invalid:` text for which kind | `architecture-flows-event-ingestion` and the per-kind implementation nodes |

**Expected but not verified when this node was written:**

- **No test asserts the reason-prefix vocabulary.** `protocol.rs`'s two `OK` unit
  tests exercise the constructor only — the accepted case checks that element 0 is
  `"OK"`, element 2 is `true` and element 3 is empty; the rejected case checks
  elements 2 and 3 against what was passed in. Nothing checks that a handler chose
  the right prefix, so the eight-prefix set above is established by reading the emit
  sites and would not be defended by CI if an emitter drifted. Searching
  `crates/buzz-test-client/tests/e2e_relay.rs` for `OK` returns only HTTP
  status-code comparisons and prose comments — no wire-frame prefix assertion.
- **The relay was not run.** Every claim here is read from source at the recorded
  revision; no frame was observed on a live socket, so the *ordering* of an
  unsolicited ban `OK` relative to the WebSocket `Close` is taken from the code's
  own control-channel reasoning rather than from an observed trace.
- **`duplicate:`'s reach into `CLOSED` was checked but its client handling was not
  pursued.** No `RelayMessage::closed` call site in `crates/` passes a `duplicate:`
  message and `"pow:"` does not occur in `crates/` at all, yet
  `desktop/src/shared/api/relayClosedPolicy.ts` classifies both as terminal `CLOSED`
  reasons. Whether that is dead defensive code or a real mismatch is `CLOSED`'s
  question, not this node's, and it is left open here.
