---
id: interfaces-websocket-event
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision b5dd39acb7ade0a33692edaebe674a1212111dd5."
    entry_class: FACT
    evidence:
      - "commit b5dd39acb7ade0a33692edaebe674a1212111dd5"
  - statement: "node.schema.json's type enum's single value for the corpus's combined interface/event-kind surface is interfaces-events, and this node documents a WebSocket interface (a boundary, not a single event kind), so it is built from launchpad/docs/corpus/templates/interface.md rather than templates/event-kind.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "NIP-01 defines the client-to-relay EVENT message as `[\"EVENT\", <event JSON>]`, used to publish events, and the relay-to-client EVENT message as `[\"EVENT\", <subscription_id>, <event JSON>]`, used to send events requested by clients — the two directions this node documents."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "NIP-01 defines the OK message as `[\"OK\", <event_id>, <true|false>, <message>]`, states the message MAY be an empty string when the third element is true, and standardizes the machine-readable prefixes duplicate, pow, blocked, rate-limited, invalid, restricted, mute and error (\"for when none of the above fits\")."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "NIP-42 adds the `auth-required:` machine-readable prefix, defined as for when a client has not performed AUTH and the relay requires that to fulfill the query or write the event, usable in OK and CLOSED messages — a prefix NIP-01 itself does not standardize."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md"
  - statement: "ClientMessage::parse's \"EVENT\" arm requires a second array element and deserializes it as a nostr::Event, returning ClientMessage::Event(event); an empty array, a non-array frame, or a missing/malformed event payload is rejected as RelayError::InvalidMessage before any handler runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:14-18"
      - "crates/buzz-relay/src/protocol.rs:41-67"
  - statement: "ClientMessage::parse's final match arm rejects any first-array-element other than EVENT/REQ/CLOSE/COUNT/AUTH as RelayError::InvalidMessage(\"unknown message type: {other}\") -- an unrecognized top-level WS message name is refused, not silently ignored, and no version-negotiation field or handshake for the EVENT message was found in protocol.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:170-173"
  - statement: "RelayMessage::event(sub_id, event) formats the relay-to-client push frame as the JSON array [\"EVENT\", sub_id, event_json]; RelayMessage::ok(event_id, accepted, message) formats [\"OK\", event_id, accepted, message]; RelayMessage::notice(message) formats [\"NOTICE\", message]."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs:186-196"
      - "crates/buzz-relay/src/protocol.rs:203-206"
  - statement: "connection.rs's handle_text_message parses each inbound WS frame via ClientMessage::parse; a parse error sends RelayMessage::notice(\"invalid message: {e}\") and returns without reaching any handler, so a malformed EVENT frame is rejected with NOTICE, never with an OK message (OK requires a parsed event_id)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:547-554"
  - statement: "A successfully parsed ClientMessage::Event is dispatched to handlers::event::handle_event on a spawned task inside a tracing span, gated by a bounded handler_semaphore permit; if the semaphore is exhausted, the connection instead receives RelayMessage::notice(\"rate-limited: too many concurrent requests\") without invoking handle_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:568-595"
  - statement: "handle_event first checks conn.auth_state; if not AuthState::Authenticated, it rejects with RelayMessage::ok(event_id, false, \"auth-required: not authenticated\") and returns before any other validation runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:634-654"
  - statement: "AUTH_TIMEOUT is 5 seconds; a connection that has not reached AuthState::Authenticated within that window after connecting is closed by the relay (auth_timeout_cancel.cancel()), independent of and prior to any EVENT submission on that connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:29"
      - "crates/buzz-relay/src/connection.rs:251-272"
  - statement: "handle_event rejects with RelayMessage::ok(event_id, false, \"invalid: event pubkey does not match authenticated identity\") when event.pubkey differs from the connection's authenticated pubkey, unless the event kind is KIND_GIFT_WRAP (NIP-59 gift wraps deliberately use an unrelated ephemeral signing key)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:659-668"
  - statement: "Ephemeral event kinds (20000-29999) are dispatched by handle_event to handle_ephemeral_event, which verifies the signature, applies channel-membership/global publish via Redis pub/sub, and fans out to local subscribers directly — bypassing ingest_event's persistence, duplicate-detection, and storage path entirely; these events are never durably stored."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:694-752"
      - "crates/buzz-relay/src/handlers/event.rs:794-906"
  - statement: "Persistent (non-ephemeral, non-observer-frame) events are delegated by handle_event to super::ingest::ingest_event, and the resulting IngestResult/IngestError is translated into a single RelayMessage::ok(event_id, accepted, message) sent back on the same connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:754-791"
  - statement: "ingest_event_inner rejects on: the community write fence (\"restricted: community writes are fenced\"), kind:AUTH submitted via EVENT (\"invalid: AUTH events cannot be submitted\"), signature verification failure (\"invalid: {verify error}\"), a created_at more than 900 seconds (15 minutes) from server time (\"invalid: event timestamp too far from server time\"), content exceeding 256 KiB (\"invalid: content exceeds maximum size of ...\"), an event.pubkey not matching the authenticated principal (\"invalid: event pubkey does not match authenticated identity\"), and insufficient scope for the event's kind (\"restricted: insufficient scope (need {scope})\") — all checked in that order before any storage write is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2160-2274"
  - statement: "IngestResult carries event_id (hex), accepted (bool), and message (String, e.g. \"duplicate:\" for a deduplicated re-submission); IngestError has three variants — Rejected (client error, WS: OK false), AuthFailed (auth/scope error, WS: OK false), Internal (server error, sanitized to \"error: internal server error\" before being sent over WS so DB/system details never leak to the client)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:373-392"
      - "crates/buzz-relay/src/handlers/event.rs:781-791"
  - statement: "When the durable insert reports the event was not newly inserted (a duplicate id, or a kind:9007 concurrent-create race, etc.), ingest_event_inner returns IngestResult { accepted: true, message: \"duplicate:\", .. } — resubmitting the same signed event is idempotent: the OK response still reports true, with no second fan-out or side-effect run for the duplicate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3192-3198"
  - statement: "A freshly inserted persistent event is delivered relay-to-client via RelayMessage::event through three routes that share one guarded access gate (filter_fanout_by_access): fan_out_event_to_local_subscribers (used by the ephemeral path and as the same-node half of persistent dispatch), dispatch_persistent_event/dispatch_persistent_event_inner (the post-commit path for persistent events, which also republishes to Redis and triggers workflow execution), and fan_out_pubsub_event (the cross-node path consuming the Redis republish, with an echo-dedup check so a node does not redeliver its own already-fanned-out event)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:241-338"
      - "crates/buzz-relay/src/handlers/event.rs:395-561"
  - statement: "filter_fanout_by_access fails closed: it drops recipients whose connection is not bound to the event's community, restricts author-only kinds to the author's own connections, restricts shared-gated kinds to the author plus connections the event marks as shared, and for a private channel keeps a recipient only if a fresh (or exactly-scoped cached) membership lookup confirms current membership — a lookup failure drops all matches for that fan-out rather than leaking events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:115-222"
  - statement: "dispatch_persistent_event_inner applies an additional owner-only delivery fence, after filter_fanout_by_access, for kind:30622 (DM visibility) and the agent-turn-metric kind: only the connection whose authenticated pubkey matches the event's `p`-tagged owner receives the RelayMessage::event push, even if a kindless subscription would otherwise match it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:457-491"
  - statement: "Root AGENTS.md states Buzz's primary API is NIP-29 over WebSocket, with the relay's HTTP surface deliberately narrow (NIP-11/NIP-05 metadata, POST /events, POST /query, POST /count, webhooks, Blossom media, git smart HTTP, git policy hooks, health probes) — this WebSocket EVENT interface is that primary surface's write/push path, distinct from the narrower HTTP bridge equivalent."
    entry_class: FACT
    evidence:
      - "AGENTS.md:158"
  - statement: "No node named interfaces-http-events (or any node under launchpad/docs/corpus/interfaces/) exists on origin/launchpad at this node's recorded revision, so this node cannot declare a relationships[] edge to the HTTP EVENT-equivalent interface (issue #979) without a hard validation failure; it is instead named by filename in prose only, per this task's own dispatch note."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/interfaces') -> empty, path does not exist, verified at commit b5dd39acb7ade0a33692edaebe674a1212111dd5"
  - statement: "The four architecture/flows nodes this document references (architecture-flows-event-ingestion, architecture-flows-live-fanout, architecture-flows-websocket-connection, architecture-flows-websocket-authentication) are present on origin/launchpad at this node's recorded revision, each with status: draft, so each relationships[] target resolves."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/event-ingestion.md"
      - "launchpad/docs/corpus/architecture/flows/live-fanout.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-connection.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "corpus-template-interface is present on origin/launchpad at this node's recorded revision with status: active, so an implements relationships[] edge to it resolves."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "The relay does not document or enforce a global, cross-event delivery-ordering guarantee for EVENT fan-out beyond per-connection FIFO framing on the outbound send channel — no source opened while drafting this node states such a guarantee explicitly, so this is inferred from the absence of any ordering-guarantee code or doc found, not from a positive statement."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1-561"
      - "crates/buzz-relay/src/connection.rs:1-274"
    confidence: 0.6
relationships:
  - type: implements
    target: corpus-template-interface
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: architecture-flows-live-fanout
  - type: references
    target: architecture-flows-websocket-connection
  - type: references
    target: architecture-flows-websocket-authentication
---

# WebSocket EVENT: interface

This node documents the WebSocket EVENT message defined by NIP-01 (extended by
NIP-42's authentication requirement and Buzz's own message-prefix and
delivery-gating conventions): the boundary across which a Nostr client and the
Buzz relay exchange signed events over an already-established WebSocket
connection. Two independent directions exist under the same `["EVENT", ...]`
message type name: **client → relay**, the array `["EVENT", <signed-event>]`
submitting one event for validation, storage and fan-out; and **relay →
client**, the array `["EVENT", <subscription_id>, <event>]` pushing a stored or
newly-matching event to one of that connection's active REQ subscriptions. Both
directions ride the same JSON-array-over-text-frame wire format the rest of
NIP-01 (REQ, CLOSE, AUTH, COUNT, NOTICE, OK) uses.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Client → relay: submit a signed event | NIP-01 `["EVENT", <event>]`; parsed by `ClientMessage::parse`'s `"EVENT"` arm (`crates/buzz-relay/src/protocol.rs:58-67`), variant `ClientMessage::Event` (`protocol.rs:18`) | Client publishes one signed Nostr event for validation and (for non-ephemeral kinds) storage. |
| WS dispatch of a parsed EVENT | `handlers::event::handle_event` (`crates/buzz-relay/src/handlers/event.rs:608`), invoked from `connection::handle_text_message` (`connection.rs:568-595`) | Checks NIP-42 auth, pubkey binding, kind-specific gates, then routes to the ephemeral path or `ingest_event`. |
| Persistent ingest pipeline | `handlers::ingest::ingest_event` / `ingest_event_inner` (`crates/buzz-relay/src/handlers/ingest.rs:2100-2280` and following) | Write-fence, signature verify, timestamp/content-size bounds, pubkey/scope checks, then durable insert (or duplicate no-op). |
| Ephemeral event handling (kind 20000-29999) | `handlers::event::handle_ephemeral_event` (`crates/buzz-relay/src/handlers/event.rs:794-906`) | Verify + Redis publish + local fan-out only; never durably stored, never runs `ingest_event`. |
| Relay → client: push a matching/stored event | NIP-01 `["EVENT", <subscription_id>, <event>]`; formatted by `RelayMessage::event` (`protocol.rs:186-191`) | Delivers one event to one connection's named subscription. |
| Local (same-node) fan-out | `handlers::event::fan_out_event_to_local_subscribers` (`event.rs:241-278`) | Finds this relay's matching subscriptions and sends the guarded `RelayMessage::event` frame to each. |
| Post-commit dispatch for a persisted event | `handlers::event::dispatch_persistent_event` / `dispatch_persistent_event_inner` (`event.rs:349-561`) | Redis publish, local fan-out, DM/agent-turn-metric owner gating, workflow trigger — spawned after the durable write commits. |
| Cross-node fan-out | `handlers::event::fan_out_pubsub_event` (`event.rs:282-338`) | Consumes the Redis republish on other relay nodes and fans out locally, with echo-dedup against the node that ingested the event. |
| Relay → client: acknowledge a submission | NIP-01 `["OK", <event_id>, <accepted>, <message>]`; formatted by `RelayMessage::ok` (`protocol.rs:203-206`) | Reports whether the submitted event was accepted, with a standardized message prefix on rejection. |
| Relay → client: report a transport/parse-level problem | NIP-01 `["NOTICE", <message>]`; formatted by `RelayMessage::notice` (`protocol.rs:193-196`) | Used for frames that never resolve to a parsed `ClientMessage::Event` at all (malformed JSON, unknown message type, semaphore exhaustion), so no `event_id` exists to acknowledge via OK. |

## Examples

**Valid: authenticated submission, acceptance, and push to a matching
subscriber.** A client that has completed NIP-42 `AUTH` sends (client → relay,
per `ClientMessage::parse`'s `"EVENT"` arm, `protocol.rs:58-67`):

```json
["EVENT", {"id":"<64-hex event id>","pubkey":"<64-hex author pubkey>","created_at":1735689600,"kind":40002,"tags":[["h","<channel-uuid>"]],"content":"hello","sig":"<128-hex signature>"}]
```

The relay replies on the same connection, formatted by `RelayMessage::ok`
(`protocol.rs:203-206`):

```json
["OK", "<64-hex event id>", true, ""]
```

Any connection with an active `REQ` subscription matching the event — subject
to `filter_fanout_by_access` (`event.rs:115-222`) — then receives, formatted
by `RelayMessage::event` (`protocol.rs:186-191`):

```json
["EVENT", "<their subscription id>", {"id":"<same event JSON as above>", "...": "..."}]
```

**Failure: submission before authentication completes.** An `EVENT` frame
arriving on a connection whose `auth_state` is not yet
`AuthState::Authenticated` is rejected by `handle_event` before any other
check runs (`event.rs:634-654`):

```json
["OK", "<64-hex event id>", false, "auth-required: not authenticated"]
```

No storage write, fan-out, or workflow trigger occurs for a rejected event —
the client must complete `AUTH` (see `architecture-flows-websocket-authentication`)
and resubmit.

## Contract and stability

**OK response shape.** Every accepted parse of a `["EVENT", ...]` frame ends in
exactly one `RelayMessage::ok(event_id, accepted, message)` sent back on the
same connection (`event.rs:775-779`, `:743-750`, `:997`, `:1100`) — never zero,
never more than one, per submitted event. `accepted` is `true` for a durable
insert *and* for a duplicate no-op (`ingest.rs:3192-3198`); it is `false` for
every `Rejected`/`AuthFailed` branch. `message` is empty on plain success and
otherwise carries one of NIP-01's standardized machine-readable prefixes —
`duplicate:`, `invalid:`, `restricted:`, `blocked:`, `error:` — observed
throughout `ingest.rs`, plus NIP-42's `auth-required:` prefix
(`event.rs:649`), which NIP-01 itself does not define. A caller may rely on
these prefixes as a closed, parseable vocabulary rather than parsing the
trailing human-readable text.

**Authentication.** A connection must reach `AuthState::Authenticated` (a
completed NIP-42 AUTH exchange) before any `EVENT` frame is accepted;
otherwise `handle_event` short-circuits with `OK false
"auth-required: not authenticated"` before any other check runs
(`event.rs:634-654`). Independently of any EVENT submission, a connection that
has not authenticated within `AUTH_TIMEOUT` (5 seconds) of connecting is closed
by the relay (`connection.rs:29,251-272`) — so in practice an unauthenticated
client has, at most, that same 5-second window to submit an EVENT before the
connection itself disappears.

**Identity binding.** `event.pubkey` must equal the connection's authenticated
pubkey, checked once in `handle_event` (`event.rs:659-668`) and again inside
`ingest_event_inner` (`ingest.rs:2242-2247`) for the persistent path — the one
documented exception is `KIND_GIFT_WRAP` (NIP-59), whose envelope is
deliberately signed by an unrelated ephemeral key.

**Idempotency.** Re-submitting an event whose id the relay already holds is
not an error: the durable insert is a no-op, and the caller still receives
`OK true "duplicate:"` (`ingest.rs:3192-3198`) — no second fan-out, side-effect
run, or workflow trigger fires for the duplicate.

**Bounds enforced before storage.** `ingest_event_inner` rejects, in order,
before ever attempting a database write: the community write fence, `kind:AUTH`
submitted via EVENT, signature-verification failure, a `created_at` more than
±900 seconds (15 minutes) from server time, content over 256 KiB, an
identity-binding mismatch, and insufficient scope for the event's kind
(`ingest.rs:2160-2274`). Ephemeral kinds (20000-29999) instead run
`handle_ephemeral_event`'s own narrower verify-and-publish path
(`event.rs:794-906`) and skip storage, deduplication and these bounds
entirely.

**Versioning and compatibility.** The relay does not tolerate unrecognized
top-level message names: `ClientMessage::parse`'s final match arm rejects any
first-array-element other than `EVENT`/`REQ`/`CLOSE`/`COUNT`/`AUTH` as
`RelayError::InvalidMessage("unknown message type: {other}")`
(`protocol.rs:170-173`), which surfaces to the client as a `NOTICE`
(`connection.rs:548-554`), not a silently-ignored frame. A protocol
extension therefore cannot introduce a new top-level WS message type against
an unmodified relay without that relay rejecting it. No explicit
version-negotiation field or handshake for the `EVENT` message itself was
found in `protocol.rs` or NIP-01 — compatibility for this message rests on
NIP-01's own stability as a spec, not on a runtime version check.

**Delivery access control.** Every relay-to-client `EVENT` push, on every
fan-out route (local, post-commit, cross-node), passes through
`filter_fanout_by_access`, which fails closed: a stale subscription surviving
a membership or visibility change (e.g. a channel flipping open→private, or a
cross-node cache lag) cannot leak an event to a recipient who is no longer
entitled to it (`event.rs:115-222`). `dispatch_persistent_event_inner` layers
one further owner-only gate on top for viewer-private kinds (DM visibility,
agent-turn metrics) (`event.rs:457-491`).

**Ordering.** No source opened while drafting this node states a
cross-event, cross-connection delivery-ordering guarantee; the outbound send
path is per-connection FIFO, but that is not the same as a documented ordering
contract a caller may rely on (see the INFERENCE evidence entry above, and
*Scope and omissions* below).

## Boundary

This node does not describe:
- **A single Nostr event kind's own wire contract** — tag shape, content-field
  semantics, or which NIP defines it (e.g. kind:9002 membership, kind:1
  text notes). Such a node, if one exists, is built from
  `templates/event-kind.md`, not this one; this node instead names the flow
  nodes it spans (see *Relationships*).
- **A full parameter-by-parameter catalogue** of every accepted event field for
  domain-expert readers — this template's own *Boundary* section places that
  depth outside its scope.
- **The HTTP equivalent of event submission** — `POST /events` and the rest of
  the relay's HTTP bridge — which is a distinct interface node,
  `interfaces/http/events.md` (issue #979). At this node's recorded revision
  that document is not merged to `origin/launchpad`, so no
  `relationships[]` edge to it exists here (a target that does not resolve is
  a hard validation error); this paragraph is the cross-link until both nodes
  exist and one of their authors adds the typed edge.
- **The REQ/CLOSE/COUNT/EOSE subscription lifecycle itself** — opening,
  closing or counting against a subscription is a different NIP-01 message
  family; this node covers only the `EVENT` message name in both its
  directions.

## Relationships

- implements: corpus-template-interface
- references: architecture-flows-event-ingestion
- references: architecture-flows-live-fanout
- references: architecture-flows-websocket-connection
- references: architecture-flows-websocket-authentication

## Scope and omissions

**This node covers** the WebSocket `EVENT` message in both directions
(client→relay submission, relay→client push): its wire shape per NIP-01, the
WS-side dispatch and validation pipeline (`handle_event`, `ingest_event`,
`handle_ephemeral_event`), the `OK`/`NOTICE` acknowledgment contract and its
standardized message-prefix vocabulary (NIP-01 plus NIP-42's
`auth-required:`), the NIP-42 authentication gate and `AUTH_TIMEOUT`, identity
binding, duplicate idempotency, and the three fan-out routes and their shared
access-control gate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A single Nostr event kind's own tag/content wire contract | An `event-kind`-template node for that kind, if one exists |
| Full parameter-by-parameter cataloguing of every accepted event field | A future reference-depth node, undecided (see `templates/interface.md`'s own boundary) |
| `POST /events`, the HTTP equivalent of event submission | `interfaces/http/events.md` (issue #979), not yet merged |
| The REQ/CLOSE/COUNT/EOSE subscription lifecycle | A future WebSocket-subscription interface node, not yet drafted |
| NIP-42's AUTH challenge/response exchange itself, beyond the timeout and gate this node cites | `architecture-flows-websocket-authentication` |

**Expected but not verified when this node was written:**
- Whether the relay documents (anywhere outside code) an explicit
  cross-connection delivery-ordering guarantee for fan-out — none was found;
  the *Contract and stability* statement above is an inference from absence,
  not a cited guarantee.
- Whether `interfaces/http/events.md` (issue #979), once merged, will declare
  a `relationships[]` edge back to this node — left to that node's own
  author, per the corpus's convention of adding edges once both sides exist.
