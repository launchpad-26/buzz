---
id: interfaces-nostr-nip-01
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
  - statement: "buzz-relay/src/protocol.rs defines ClientMessage as a five-variant enum (Event, Req, Close, Count, Auth) parsed from a raw JSON WebSocket frame by ClientMessage::parse, and RelayMessage as a set of formatting functions (auth_challenge, event, notice, eose, ok, closed, count) that produce NIP-01 (plus NIP-42/NIP-45) relay-to-client JSON strings."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "buzz-relay/src/protocol.rs declares MAX_SUB_ID_LENGTH = 256 and MAX_FILTERS_PER_REQ = 10, and ClientMessage::parse rejects a REQ or COUNT message whose subscription id exceeds 256 bytes or whose filter list exceeds 10 filters at parse time, before any handler runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "buzz-relay/src/nip11.rs's relay_limitation function sets the NIP-11 relay information document's limitation.max_filters to 10 and limitation.max_subid_length to 256, the same two values protocol.rs enforces as MAX_FILTERS_PER_REQ and MAX_SUB_ID_LENGTH, and its SUPPORTED_NIPS constant includes the literal integer 1 (NIP-01) alongside 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50 and 56."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "buzz-core/src/verification.rs's verify_event checks an event's id (recomputed via EventId::new from pubkey, created_at, kind, tags and content, then compared to the claimed id) and its Schnorr signature, returning VerificationError::InvalidId or VerificationError::InvalidSignature on failure; its own doc comment states it is CPU-bound and must be called via tokio::task::spawn_blocking from async contexts, never directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
  - statement: "buzz-relay/src/handlers/ingest.rs's ingest_event_inner calls verify_event inside tokio::task::spawn_blocking before an EVENT submission is persisted, and rejects the event with 'invalid: <verification error>' if verification fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "ingest_event_inner rejects an EVENT submission whose created_at is more than 900 seconds (MAX_TIMESTAMP_DRIFT_SECS, +/-15 minutes) away from the relay's own clock, with the message 'invalid: event timestamp too far from server time'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "When ingest_event_inner's storage call reports the event was not newly inserted (was_inserted is false, i.e. an event with the same id was already stored), it returns IngestResult { accepted: true, message: \"duplicate:\", .. } rather than an error, so resubmitting an already-accepted event id is idempotent at the OK-message level rather than being rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "buzz-relay/src/handlers/event.rs's handle_event rejects an EVENT message with OK(false, \"auth-required: not authenticated\") when the connection's AuthState is not Authenticated, and separately rejects an EVENT whose pubkey does not match the authenticated identity (except NIP-59 gift wraps) with OK(false, \"invalid: event pubkey does not match authenticated identity\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-relay/src/handlers/req.rs's handle_req rejects a REQ from a connection whose AuthState is not Authenticated by sending NOTICE(\"auth-required: authenticate before subscribing\") followed by CLOSED(sub_id, \"auth-required: not authenticated\"), and separately rejects a REQ from an authenticated connection lacking the MessagesRead scope with NOTICE(\"restricted: insufficient scope\") followed by CLOSED(sub_id, \"restricted: insufficient scope\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "handle_req also rejects opening a new subscription once a connection already holds MAX_SUBSCRIPTIONS open subscriptions, with CLOSED(sub_id, \"error: too many subscriptions\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
  - statement: "buzz-relay/src/handlers/close.rs's handle_close removes the named subscription from the connection's subscription map, deregisters it from the relay's fan-out index (releasing any global or per-channel pubsub topics it held), and then sends CLOSED(sub_id, \"\") to acknowledge the cancellation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/close.rs"
  - statement: "buzz-core/src/filter.rs's module doc states 'Multiple filters are OR-ed; fields within one filter are AND-ed', and its filters_match function implements this by returning true if any filter in the slice matches the event via filter_match_one; the Filter type itself is nostr::Filter, imported from the external nostr crate rather than defined in buzz-core."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/filter.rs"
  - statement: "buzz-core/src/event.rs's StoredEvent wraps the underlying nostr::Event with relay-assigned metadata: received_at (wall-clock receipt time), channel_id (None for global/DM events) and a verified flag, constructed via StoredEvent::new (verified: false) or StoredEvent::with_received_at (explicit received_at and verification status)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/event.rs"
  - statement: "This repository's root AGENTS.md states 'Buzz's primary API is NIP-29 over WebSocket' and describes the HTTP surface as deliberately narrow, with channel scoping built on 'h' tags (NIP-29 group tags) layered on top of the NIP-01 message envelope this node documents."
    entry_class: FACT
    evidence:
      - "AGENTS.md:145-160"
  - statement: "architecture-context-nostr-network states that 'every action in Buzz is a Nostr NIP-01 wire-format signed event, dispatched by its integer kind', naming buzz-core/src/kind.rs as the kind registry -- the same NIP-01 envelope (id, pubkey, created_at, kind, tags, content, sig) this node's Operations section documents at the message-exchange level rather than at the kind-registry level."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
  - statement: "Issue #1006's Definition of done requires this node to define inputs/messages, outputs/responses and error/rejection behavior; authentication/authorization, versioning/compatibility and ordering/idempotency where applicable; a link to the authoritative machine/spec representation; and at least one valid example and one failure example."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1006 definition of done"
relationships:
  - type: implements
    target: corpus-template-interface
  - type: references
    target: architecture-context-nostr-network
---

# NIP-01 (basic protocol): interface

This node documents Buzz's implementation of the standard upstream Nostr NIP-01
("basic protocol flow description"): the WebSocket message envelope client and
relay exchange once connected -- `EVENT`, `REQ`, `CLOSE` and `COUNT` from
client to relay, and `EVENT`, `OK`, `EOSE`, `CLOSED` and `NOTICE` from relay to
client -- plus the signed-event structure and filter-matching semantics those
messages carry. The boundary is a single WebSocket connection to `buzz-relay`;
both sides exchange newline-free JSON arrays whose first element names the
message type. `crates/buzz-relay/src/protocol.rs` is the parse/format layer for
every message named below, and `crates/buzz-relay/src/handlers/*.rs` is where
each one is actually handled.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| `EVENT` (client to relay) | `ClientMessage::Event` (protocol.rs); `handle_event` (handlers/event.rs) | Submits a signed event. The relay verifies the caller is authenticated and that the event's pubkey matches the authenticated identity (except NIP-59 gift wraps), then dispatches to `ingest_event`. |
| `REQ` (client to relay) | `ClientMessage::Req { sub_id, filters }` (protocol.rs); `handle_req` (handlers/req.rs) | Opens a subscription with 1-10 NIP-01 filters. Requires an authenticated connection holding the `MessagesRead` scope; a matching historical pull followed by live fan-out delivers events on the subscription. |
| `CLOSE` (client to relay) | `ClientMessage::Close(sub_id)` (protocol.rs); `handle_close` (handlers/close.rs) | Cancels a subscription: removes it from the connection's map, releases its pubsub topics, and acknowledges with `CLOSED`. |
| `COUNT` (client to relay, NIP-45) | `ClientMessage::Count { sub_id, filters }` (protocol.rs) | Requests an aggregate count instead of matching events; not itself part of NIP-01 but parsed by the same envelope and subject to the same subscription-id and filter-count limits. |
| `AUTH` (client to relay, NIP-42) | `ClientMessage::Auth(Event)` (protocol.rs) | Responds to a relay `AUTH` challenge with a signed NIP-42 event. The handshake itself is out of this node's scope -- see *Boundary*. |
| `EVENT` (relay to client) | `RelayMessage::event` (protocol.rs) | Delivers one event matching an open subscription, tagged with that subscription's id. |
| `OK` (relay to client) | `RelayMessage::ok` (protocol.rs) | Acknowledges an `EVENT` submission: event id, `true`/`false` acceptance, and a machine-prefixed human-readable message (`"invalid: ..."`, `"auth-required: ..."`, `"restricted: ..."`, `"duplicate:"`, `"error: ..."`). |
| `EOSE` (relay to client) | `RelayMessage::eose` (protocol.rs) | Signals that all currently stored (historical) matches for a subscription have been sent; later matches arrive as live `EVENT` messages on the same subscription id. |
| `CLOSED` (relay to client) | `RelayMessage::closed` (protocol.rs) | Terminates a subscription from the relay's side -- either acknowledging a client `CLOSE`, or the relay's own rejection (auth, scope, subscription-limit) of a `REQ`. |
| `NOTICE` (relay to client) | `RelayMessage::notice` (protocol.rs) | A human-readable, connection-level message; used here ahead of a rejecting `CLOSED` for `REQ`. |
| Event verification | `verify_event` (buzz-core/src/verification.rs) | Recomputes the event id hash and checks the Schnorr signature; called via `tokio::task::spawn_blocking` from `ingest_event_inner` before any `EVENT` is accepted. |
| Filter matching | `filters_match` (buzz-core/src/filter.rs) | Multiple filters in one `REQ`/`COUNT` are OR-ed; the fields inside one filter are AND-ed. The `Filter` type itself is `nostr::Filter` from the external `nostr` crate. |

## Contract and stability

**Every accepted `EVENT` is verified before storage.** `ingest_event_inner` runs
`verify_event` (id-hash and Schnorr signature) inside `spawn_blocking` and
rejects with `"invalid: <error>"` on failure -- an unsigned or tampered event
never reaches storage or fan-out.

**Resubmission is idempotent at the OK-message level, not an error.**
Submitting an `EVENT` whose id is already stored returns `OK(id, true,
"duplicate:")` rather than rejecting it -- a client that retries a
submission after a dropped acknowledgment gets a truthful `true` back both
times, not a spurious failure on the second attempt.

**`EVENT` and `REQ` both require an authenticated connection in this relay's
deployment.** This is Buzz's own NIP-42 gate layered on top of the NIP-01
envelope, not part of the NIP-01 specification itself: an unauthenticated
`EVENT` gets `OK(id, false, "auth-required: not authenticated")`, and an
unauthenticated `REQ` gets `NOTICE` followed by `CLOSED(sub_id,
"auth-required: not authenticated")`. An authenticated connection lacking the
`MessagesRead` scope is rejected the same way with a `"restricted: ..."`
message instead.

**An event's declared timestamp must sit within +/-15 minutes of the
relay's own clock** (`MAX_TIMESTAMP_DRIFT_SECS = 900`), or `ingest_event_inner`
rejects it with `"invalid: event timestamp too far from server time"`.

**Subscription shape is bounded and the bounds are advertised, not just
enforced.** `protocol.rs` rejects a `REQ`/`COUNT` whose subscription id
exceeds 256 bytes (`MAX_SUB_ID_LENGTH`) or whose filter list exceeds 10
entries (`MAX_FILTERS_PER_REQ`) at parse time, before any handler runs; a
connection is separately capped at `MAX_SUBSCRIPTIONS` concurrently open
subscriptions by `handle_req`. `nip11.rs`'s `relay_limitation` advertises the
identical `max_filters: 10` and `max_subid_length: 256` in the relay's NIP-11
information document, so a well-behaved client can read the same bounds the
server enforces rather than discovering them by trial and error.

**NIP-01 itself is a versioned, advertised part of this relay's contract.**
`nip11.rs`'s `SUPPORTED_NIPS` constant lists the integer `1` alongside NIP-29,
NIP-42, NIP-45 and the rest of what this relay speaks; a client can read the
relay's NIP-11 document to confirm NIP-01 support rather than assuming it.

## Boundary

This node does not describe:

- **Any single Nostr event kind's own tag shape or content semantics** --
  `kind:1` (Nostr's own text-note kind) is unrelated to this NIP number, and
  no event-kind corpus node exists yet for any kind riding on this envelope.
  A future event-kind node references this one as the envelope it rides on,
  not the reverse.
- **A field-by-field, parameter-by-parameter catalogue of every `OK`/`NOTICE`
  message string this relay emits.** The Operations table above names the
  functions that format them; it is not an exhaustive enumeration.
- **NIP-42's own `AUTH` challenge/response handshake** -- issuing the
  challenge, verifying the signed response, and what scopes an authenticated
  session ends up with are `architecture/flows/websocket-authentication.md`'s
  subject, not this node's; this node only states that `EVENT` and `REQ`
  require the result of that handshake to have already succeeded.
- **NIP-29 channel/group scoping semantics** -- how `h` tags bind an event to
  a channel, and how membership gates read/write access -- which
  `architecture/context/nostr-network.md` and this repository's root
  `AGENTS.md` describe as layered on top of the envelope documented here.
- **NIP-45 `COUNT`'s own response semantics beyond the message existing.**
  `RelayMessage::count` is named in the Operations table because it shares
  this envelope and its parse-time limits, not because this node analyzes its
  behavior in depth.
- **The historical-query and live-fan-out delivery paths `REQ`/`EVENT` sit on
  top of** -- see `architecture/flows/historical-query.md` and
  `architecture/flows/live-fanout.md` for how a matched event actually reaches
  a subscriber.

### Examples

**Valid `EVENT` round-trip** (authenticated connection, well-formed event):
client sends `["EVENT", {"id": "...", "pubkey": "...", "created_at": 1234567890, "kind": 1, "tags": [], "content": "hello", "sig": "..."}]`;
relay verifies the id hash and signature (`verify_event`), checks the
timestamp is within +/-15 minutes, stores the event, and replies
`["OK", "<id>", true, ""]`.

**Failure: unauthenticated `EVENT` submission.** The same message sent on a
connection whose `AuthState` is not `Authenticated` never reaches
`verify_event` or storage; `handle_event` replies immediately with
`["OK", "<id>", false, "auth-required: not authenticated"]`.

## Relationships

- **`implements: corpus-template-interface`.** This node was drafted against
  that template's *Required sections* (Interface description, Operations,
  Contract and stability, Boundary, Relationships, Scope and omissions), and
  the template itself lists this self-link as its preferred optional edge for
  a node built from it.
- **`references: architecture-context-nostr-network`.** That node's own
  ledger states "every action in Buzz is a Nostr NIP-01 wire-format signed
  event, dispatched by its integer `kind`" -- the same envelope this node
  documents at the message-exchange level; the edge is supporting context,
  not a dependency in either direction.
- Both targets were confirmed present in `origin/launchpad`'s corpus tree
  (this worktree was branched directly from `origin/launchpad` at commit
  `650354eab8d41ab6ce1a71de079a6c6d95c69052`, with no intervening corpus
  changes of its own) before this front matter was finalized.
- No `references` edge is declared to any event-kind node, because none
  exists in the corpus yet -- per this template's own guidance, that edge is
  a follow-up once the first event-kind node merges, not an omission now.

## Scope and omissions

**This node covers** the NIP-01 client/relay message envelope Buzz's relay
implements -- `EVENT`, `REQ`, `CLOSE`, `COUNT` (client to relay) and `EVENT`,
`OK`, `EOSE`, `CLOSED`, `NOTICE` (relay to client) -- the signed-event
verification and filter-matching rules that back them, the authentication and
size/count limits this relay's deployment enforces around them, and where
that contract is advertised (NIP-11).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Any single Nostr event kind's tag/content contract | A future event-kind corpus node, once one exists |
| NIP-42's `AUTH` challenge/response handshake | `architecture/flows/websocket-authentication.md` |
| NIP-29 channel/group scoping (`h` tags, membership) | `architecture/context/nostr-network.md`, this repository's root `AGENTS.md` |
| Historical-query and live-fan-out delivery mechanics | `architecture/flows/historical-query.md`, `architecture/flows/live-fanout.md` |
| Field-by-field cataloguing of every `OK`/`NOTICE`/`CLOSED` message string | Not established anywhere in this repository at the time this node was written |
| NIP-45 `COUNT`'s own semantics beyond parse-time envelope handling | Not established anywhere in this repository at the time this node was written |

**Expected but not verified when this node was written:**

- **No corpus event-kind node exists yet to link back to this one.** The
  `references`-from-an-event-kind-node direction this node's *Boundary*
  section describes is aspirational until a first such node is drafted.
- **The upstream NIP-01 specification text itself was not fetched from
  `github.com/nostr-protocol/nips`** during this node's authoring; its
  content is described here from this repository's own code
  (`protocol.rs`, `verification.rs`, `filter.rs`, `event.rs`) and from this
  repository's own `AGENTS.md` pointer to the upstream NIPs repository as the
  reference for the Nostr protocol family, per this repository's root
  `AGENTS.md`.
- **NIP-45 `COUNT`'s handler was not located or read** in the course of
  authoring this node -- only its parse-time envelope handling in
  `protocol.rs` was verified. Its own response-construction code, if any
  beyond `RelayMessage::count`, is unverified here.
