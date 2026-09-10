---
id: interfaces-nostr-nip-42
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f."
    entry_class: FACT
    evidence:
      - "commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f"
  - statement: "NIP-42 defines two wire messages: the relay sends [\"AUTH\", <challenge-string>] to the client, and the client responds [\"AUTH\", <signed-event-json>] with a kind:22242 event carrying at least a relay tag (the relay URL) and a challenge tag (the challenge string)."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md"
  - statement: "NIP-42 states 'Relays MUST exclude kind: 22242 events from being broadcasted to any client,' defines the created_at check as the event needing to be 'close (e.g. within ~10 minutes) of the current time,' and defines two new OK/CLOSED message prefixes for authorization-related rejections: auth-required: (the client has not authenticated) and restricted: (the client authenticated but is not authorized for the requested action)."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md"
  - statement: "NIP-42 permits a client to send multiple AUTH messages with different pubkeys on the same connection, stating relays 'MUST treat all pubkeys as authenticated accordingly' -- the spec does not require a connection to be bound to a single authenticated identity."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/42.md"
  - statement: "buzz-auth's nip42.rs implements generate_challenge (32 CSPRNG bytes, hex-encoded) and verify_nip42_event, which checks the event's kind equals nostr::Kind::Authentication, its Schnorr signature verifies (buzz_core::verify_event), its challenge tag matches the expected challenge, its relay tag matches the relay URL after normalization (localhost/::1 treated as 127.0.0.1, trailing slash stripped), and its created_at is within a fixed 60-second tolerance (TIMESTAMP_TOLERANCE_SECS) of the verifier's clock -- stricter than NIP-42's own '~10 minutes' guidance."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "buzz-core/src/kind.rs documents KIND_AUTH = 22242 with the comment 'NIP-42 auth event -- never stored (carries bearer tokens),' a stronger guarantee than NIP-42's own 'MUST exclude from being broadcasted' text, since a never-stored event cannot be broadcast to anyone including its own sender."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The relay's handle_auth (crates/buzz-relay/src/handlers/auth.rs) implements a per-connection AuthState state machine (Pending, Authenticated, Failed) that rejects a second AUTH message once a connection has reached Authenticated or Failed with an immediate OK-false reply and no re-verification -- a stricter, one-shot contract than NIP-42's own text, which permits multiple AUTH messages with different pubkeys on one connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "Buzz's relay handlers use exactly the two OK/CLOSED prefixes NIP-42 defines: auth-required: appears in crates/buzz-relay/src/handlers/{auth,event,req,count}.rs for the not-yet-authenticated case, and restricted: appears in the same files (plus additional call sites) for the authenticated-but-not-authorized case."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "buzz-ws-client's message.rs parses a relay's AUTH frame into RelayMessage::Auth{challenge} and builds the client's response event via build_auth_event, which signs a kind:22242 event with EventBuilder::auth(challenge, relay_url), optionally attaching a single NIP-OA auth tag alongside the required relay/challenge tags."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "buzz-ws-client's connection.rs implements the client half of the round trip in NostrWsConnection::authenticate: it waits up to AUTH_CHALLENGE_TIMEOUT_SECS (20s) for the relay's AUTH challenge, sends [\"AUTH\", <signed-event>], and waits up to AUTH_OK_TIMEOUT_SECS (20s) for a matching OK response, returning WsClientError::AuthFailed(message) when the relay's OK carries accepted=false."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "The relay's own NIP-11 relay-information document (crates/buzz-relay/src/nip11.rs) sets limitation.auth_required to true unconditionally, and a source comment states this exists because the REQ, EVENT and COUNT handlers unconditionally require an authenticated connection -- i.e. every Buzz relay is auth_required regardless of runtime configuration, not merely capable of requiring it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "A companion corpus node, architecture-flows-websocket-authentication, already documents Buzz's own end-to-end NIP-42 implementation flow in full -- the connection-admission sequence, the AuthState machine, the post-cryptographic ban/allowlist/relay-membership gates, NIP-OA owner-delegation extraction, per-message-type enforcement in EVENT/REQ/COUNT, and a complete failure table -- at repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "Issue #1014's Definition of done requires this node to define inputs/messages, outputs/responses and error/rejection behavior; authentication/authorization, versioning/compatibility and ordering/idempotency where applicable; link the authoritative machine/spec representation; and include at least one valid and one failure example -- distinct from, and in addition to, the generic corpus-node checklist (schema-valid front matter, one independently maintainable idea, traceable evidence, links instead of duplication, a clean validator run) that applies to every corpus task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1014 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# NIP-42: WebSocket Authentication Interface

The boundary this node documents is the **NIP-42 AUTH message-level wire
protocol** between a Nostr client and the Buzz relay over an already-open
WebSocket connection: two JSON-array messages (`AUTH` from the relay, `AUTH`
from the client) and the `OK` acknowledgement that follows. This is the
*upstream protocol contract* -- what NIP-42 itself specifies and what any
conforming relay or client must honor -- not Buzz's own implementation flow
(covered by `architecture-flows-websocket-authentication`) and not kind
22242's own tag/content wire shape as a standalone event (a future
`events-kinds-*` node, issue #873, not yet in this corpus).

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Relay -> client: issue challenge | NIP-42 (`["AUTH", "<challenge>"]`); `crates/buzz-auth/src/nip42.rs::generate_challenge` | Relay sends a fresh challenge string as the first message after a connection is admitted. Buzz's challenge is 32 CSPRNG bytes, hex-encoded (64 hex characters). |
| Client -> relay: respond with signed event | NIP-42 (`["AUTH", <signed-event>]`, kind `22242`); `crates/buzz-ws-client/src/message.rs::build_auth_event` | Client signs a kind:22242 event carrying `relay` and `challenge` tags (and, in Buzz's case, an optional NIP-OA `auth` tag) and sends it back as an `AUTH` message. |
| Relay -> client: acknowledge | NIP-01 `OK` message, reused by NIP-42; `crates/buzz-relay/src/handlers/auth.rs::handle_auth` | Relay replies `["OK", <event-id>, <accepted>, <message>]`. `accepted: false` carries a human-readable reason string. |
| Relay -> client: reject unauthenticated/unauthorized action | NIP-42's two message prefixes; used across `crates/buzz-relay/src/handlers/{auth,event,req,count}.rs` | `auth-required: <reason>` when no valid AUTH has succeeded yet; `restricted: <reason>` when a valid AUTH succeeded but the requested action is not authorized. |

## Contract and stability

**Timestamp tolerance is a Buzz-specific tightening, not a spec value.**
NIP-42 asks only that an AUTH event's `created_at` be "close (e.g. within
~10 minutes)" to the verifier's clock. Buzz enforces a fixed 60-second
window (`TIMESTAMP_TOLERANCE_SECS` in `crates/buzz-auth/src/nip42.rs`) --
conforming to the spec's intent while being considerably stricter than the
example figure the spec itself gives. A client relying on the spec's
~10-minute figure rather than Buzz's actual 60-second window will see its
AUTH event rejected as expired well before the spec's own example bound.

**One authenticated identity per connection, not NIP-42's "all pubkeys."**
NIP-42's text permits a client to send multiple AUTH messages with
different pubkeys on one connection, and states relays "MUST treat all
pubkeys as authenticated accordingly." Buzz does not implement that
permissiveness: `crates/buzz-relay/src/handlers/auth.rs`'s `AuthState`
state machine treats a connection that has already reached `Authenticated`
or `Failed` as terminal for AUTH purposes -- a second `AUTH` message is
rejected immediately (`auth-required: already authenticated` /
`auth-required: authentication already failed`) without re-verification,
and the connection keeps exactly the one pubkey it first authenticated as.
A caller may not use this interface to add a second authenticated identity
to an already-authenticated connection; a new connection is required.

**Never stored, never broadcast.** NIP-42 requires relays to exclude
kind:22242 events from being broadcast to any client. Buzz's own
`kind.rs` comment for `KIND_AUTH` goes further -- "never stored (carries
bearer tokens)" -- so the event is absent from storage entirely, which by
construction also satisfies the spec's narrower broadcast exclusion.

**Error-prefix contract matches the spec exactly.** Buzz's relay handlers
use precisely the two OK/CLOSED prefixes NIP-42 defines --
`auth-required:` and `restricted:` -- and use them for exactly the
distinction the spec draws: not-yet-authenticated versus
authenticated-but-not-authorized. There is no third, Buzz-invented prefix
for this boundary.

**auth_required is unconditional, not configurable.** Buzz's NIP-11
document always advertises `limitation.auth_required: true`
(`crates/buzz-relay/src/nip11.rs`) because every `EVENT`/`REQ`/`COUNT`
handler enforces the requirement unconditionally; a caller cannot assume an
anonymous, unauthenticated session will ever be permitted to read or write
on a Buzz relay, regardless of relay configuration.

**Ordering.** The AUTH round trip has a strict two-step order at the wire
level: the relay's challenge must be received before the client's signed
response can be built (the response's `challenge` tag is copied from it),
and the client's response must be acknowledged (`OK`) before the connection
may be used for `EVENT`/`REQ`/`COUNT`. There is no idempotency guarantee on
resubmission: replaying an already-consumed challenge inside a new AUTH
event does not succeed, because a challenge is single-use per connection
(`crates/buzz-relay/src/connection.rs` stores exactly one pending challenge
per connection, generated fresh at connection start).

## Examples

**Valid exchange.**

```json
["AUTH", "<challenge>"]
```
```json
["AUTH", {
  "id": "...",
  "pubkey": "...",
  "created_at": 1732900000,
  "kind": 22242,
  "tags": [
    ["relay", "wss://relay.example.com"],
    ["challenge", "b0635d6a9851d3aed0cd6c495b061d3406b3ae6b6b5cec98be36ecd3025c0866"]
  ],
  "content": "",
  "sig": "..."
}]
```
```json
["OK", "<event-id>", true, ""]
```

**Failure example: expired timestamp.** A response signed more than 60
seconds off the relay's clock (per Buzz's `TIMESTAMP_TOLERANCE_SECS`, not
NIP-42's looser ~10-minute guidance):

```json
["OK", "<event-id>", false, "auth-required: verification failed"]
```

`crates/buzz-auth/src/nip42.rs`'s own unit test `expired_event_rejected`
exercises this exact case (a `created_at` 120 seconds in the past),
asserting `AuthError::EventExpired` from `verify_nip42_event`.

## Boundary

This node does not describe:
- **Kind 22242's own tag/content wire shape as a standalone event** --
  cardinality of every tag it MAY or MUST carry beyond `relay`/`challenge`,
  and any content-field convention. That is an event-kind node's subject
  (issue #873, `events-kinds-kind-22242-auth` once merged); this node cites
  the kind by number and points at the code that constructs and verifies
  it, but does not restate its full tag catalogue.
- **Buzz's own end-to-end authentication implementation flow** -- the
  connection-admission sequence, the ban/pubkey-allowlist/relay-membership
  gates that run after cryptographic verification, NIP-OA owner-delegation
  extraction, and the full state-transition failure table. All of that is
  already documented in `architecture-flows-websocket-authentication`,
  linked via this node's `references` relationship rather than restated
  here.
- **NIP-98 HTTP Auth** (`crates/buzz-auth/src/nip98.rs`, kind 27235) -- the
  sibling authentication mechanism for the relay's HTTP surface. A
  different interface with its own wire contract; not covered here.
- **A full parameter-by-parameter API-reference catalogue** for every
  relay message type NIP-42 touches (`REQ`, `COUNT`, `CLOSED` in general)
  -- only the auth-specific messages and the two auth-related prefixes are
  in scope.

## Relationships

- `references`: `architecture-flows-websocket-authentication` -- the
  companion node documenting Buzz's own implementation of this protocol in
  full mechanical detail. This node describes the protocol contract itself
  (what NIP-42 promises and how Buzz's wire-level behavior compares to it);
  the flow node describes the concrete sequence of relay-internal steps
  that realize it.
- No `relationships` entry targets an event-kind node for kind 22242,
  because none is merged in the loaded corpus yet (`events-kinds-*` for
  issue #873 does not resolve on `origin/launchpad` at the recorded
  revision) -- see *Boundary* above for the prose pointer in its place.

## Scope and omissions

**This node covers** the NIP-42 AUTH wire protocol as a contract: the two
messages it defines, the `OK`/error-prefix vocabulary it specifies, where
Buzz's own implementation conforms to that contract and where it is
deliberately stricter or narrower than the spec's own permissiveness
(timestamp tolerance, single-identity-per-connection, unconditional
`auth_required`), and one valid plus one failure example.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 22242's full tag/content wire shape as an event-kind node | Issue #873 (`events-kinds-kind-22242-auth`, not yet merged) |
| Buzz's end-to-end implementation flow (state machine, ban/allowlist/membership gates, NIP-OA delegation) | `architecture-flows-websocket-authentication` |
| NIP-98 HTTP Auth | Not yet in this corpus |
| Rate limiting and admission control applied after authentication | Not yet in this corpus |
| Per-type corpus node templates and standards | `#1307`-`#1351` (unsettled at the time this node was written; this node is written directly against `node.schema.json` and the unmerged `templates/interface.md` draft, read for structural guidance only) |

**Expected but not verified when this node was written:**
- **The unmerged `templates/interface.md` draft's own boundary against a
  future event-kind node for kind 22242 was read for structural guidance
  but is not itself an authorized corpus standard** -- no per-type
  standard for interface-shaped nodes has landed under
  `launchpad/docs/corpus/standards/` as of the recorded revision, so this
  node's shape may need revision once one does.
- **Whether the `relationships` edge to `architecture-flows-websocket-authentication`
  should instead be typed `depends-on` was not settled by any corpus
  standard** -- `references`' looser "cites as supporting context"
  directionality was chosen because this node's own claims (what the spec
  says, how Buzz's wire behavior compares) stand on their own evidence
  ledger and do not become false if the flow node is later revised, but no
  authority beyond this node's own reasoning adjudicates that choice.
