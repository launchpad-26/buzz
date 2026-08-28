---
id: layers-authentication-websocket-challenge
type: layers
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
  - statement: "generate_challenge produces a NIP-42 challenge as 32 CSPRNG bytes, hex-encoded to a 64-character string."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "On a new WebSocket connection, the relay calls generate_challenge() once, stores the result as AuthState::Pending { challenge } on the connection's per-connection state, and sends it as the very first frame -- before the connection is registered with the connection manager -- via RelayMessage::auth_challenge, which formats it as the JSON array [\"AUTH\", \"<challenge>\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/protocol.rs"
  - statement: "The client's signed response travels as the JSON array [\"AUTH\", <kind:22242 event>], parsed relay-side by ClientMessage::Auth; kind 22242 is buzz-core's KIND_AUTH constant, whose own source comment states events of this kind are never stored (they may carry bearer tokens)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/protocol.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "verify_nip42_event reads the signed event's \"challenge\" tag and rejects with AuthError::ChallengeMismatch unless its content is byte-identical to the challenge string the relay generated for that connection; a missing challenge tag is rejected the same way. This check is independent of, and runs alongside, the event's kind check, Schnorr signature check, \"relay\" tag match (after normalization), and the +/-60 second created_at tolerance -- all five must pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "The client-side buzz-ws-client crate (NostrWsConnection::authenticate) waits up to AUTH_CHALLENGE_TIMEOUT_SECS (20 seconds, enforced by both a runtime wait and a const assertion in its own tests) for the relay's AUTH challenge, extracts the challenge string, and passes it to build_auth_event, which calls EventBuilder::auth(challenge, relay_url) to attach the \"challenge\" and \"relay\" tags to a new kind:22242 event before signing it with the caller's keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "buzz-ws-client's wait_for_auth_challenge rejects an incoming AUTH challenge longer than 1024 bytes with WsClientError::AuthFailed(\"challenge exceeds 1024 bytes\") before ever handing it to build_auth_event -- a client-side sanity bound with no counterpart on the relay's generate_challenge, which always emits exactly 64 hex characters."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "The relay's own AUTH_TIMEOUT (5 seconds, crates/buzz-relay/src/connection.rs) bounds how long a connection may stay unauthenticated before the relay cancels it outright; buzz-ws-client's AUTH_CHALLENGE_TIMEOUT_SECS (20 seconds) bounds only how long the client waits to receive the challenge frame, a separate, client-side wait with no message back to the relay. The challenge string itself carries no expiry field or timestamp of its own -- its effective lifetime is bounded externally, by the relay's 5-second connection timeout and, once a response arrives, by the signed event's own +/-60 second created_at tolerance."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-ws-client/src/connection.rs"
      - "crates/buzz-auth/src/nip42.rs"
    confidence: 0.7
  - statement: "A challenge is generated exactly once per connection (a single generate_challenge() call inside handle_active_connection) and is never regenerated or reused for a later AUTH attempt on the same connection -- the state-machine guard in the relay's AUTH handler rejects a second AUTH message on an already-Authenticated or already-Failed connection without re-running verification or re-issuing a challenge."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "crates/buzz-auth/src/nip42.rs's own unit tests (challenge_is_64_hex_chars_and_unique, wrong_challenge_rejected) assert the 64-hex-character shape, uniqueness across two calls, and that a mismatched challenge string is rejected with AuthError::ChallengeMismatch specifically -- distinct from wrong-kind, wrong-relay, and expired-timestamp rejections, which the same test module covers with separate cases."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "A hand-rolled client independent of buzz-ws-client can and does implement the challenge round trip directly against the wire format: crates/buzz-test-client/tests/nip42_host_binding_live.rs reads raw WebSocket frames, extracts the challenge as array index 1 of a [\"AUTH\", ...] JSON message, and signs it with nostr::EventBuilder::auth(&challenge, relay_url) -- the same construction buzz-ws-client uses internally, confirming the wire contract is implementable without the client crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs"
  - statement: "architecture-flows-websocket-authentication is a corpus node, merged on origin/launchpad, that narrates the full NIP-42 connection-to-authenticated round trip end to end (challenge issuance through ban/allowlist/membership gates to AuthState::Authenticated); this node's subject -- the challenge string's own generation, wire shape, matching rule, and client-side handling -- is a proper subset of that node's Sequence, so a references relationship is used here instead of restating that node's steps."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "Issue #1030's Definition of Done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link to related concepts/implementation/verification, and use examples only to clarify the concept rather than introduce a second canonical concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1030 definition of done"
  - statement: "Issue #1028 (task: document layers/authentication/nip-42-authentication.md), the parallel sibling task for the overall NIP-42 authentication concept, was open and its target file did not exist on origin/launchpad's corpus tree at the recorded revision, so no relationships edge to it is used here -- AGENTS.md requires a relationships target to exist on the branch being merged into, not merely on a sibling's own in-progress branch."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1028 --repo launchpad-26/buzz, run directly while authoring this node; git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, re-checked while authoring this node"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
---

# WebSocket Challenge (NIP-42)

The one-time random value at the heart of Buzz's WebSocket authentication handshake --
what it is, how it is generated and matched, and how it differs from the connection
lifecycle that surrounds it.

## Definition

The **NIP-42 challenge** is a one-time, connection-scoped random string the relay
generates and sends as the very first frame on every new WebSocket connection, which a
connecting client must echo back verbatim inside a signed `kind:22242` event to prove
control of a Nostr keypair *for that specific connection*. Concretely: 32
cryptographically-random bytes, hex-encoded to 64 characters
(`generate_challenge`, `crates/buzz-auth/src/nip42.rs`), sent as `["AUTH",
"<challenge>"]` and expected back inside a `"challenge"` tag on a signed
`kind:22242` (`KIND_AUTH`) event, checked for byte-identical equality by
`verify_nip42_event`.

**What this is not.** The challenge is a single value, not a protocol or a state
machine. It does not, by itself, decide whether a connection ends up authenticated --
that is the job of the surrounding handshake (signature check, relay-URL match,
timestamp tolerance, and the ban/allowlist/membership gates that run after), documented
in full in `architecture-flows-websocket-authentication`. This node covers only the
challenge value's own lifecycle: how it is made, where it lives while a connection is
pending, and what "matching" it means.

## Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Generated: generate_challenge() (32 CSPRNG bytes, hex)
    Generated --> Pending: stored as AuthState::Pending{challenge}\nsent as ["AUTH", "<challenge>"]
    Pending --> Matched: signed kind:22242 event's\n"challenge" tag == stored value
    Pending --> Mismatched: tag missing or != stored value
    Matched --> [*]: consumed -- AuthState moves on\n(subject to the flow's other checks)
    Mismatched --> [*]: AuthError::ChallengeMismatch
    Pending --> Discarded: relay's 5s AUTH_TIMEOUT elapses\nwith no valid AUTH received
    Discarded --> [*]
```

A challenge is generated exactly once per connection and is never reused: the relay's
AUTH handler rejects a second `AUTH` message on a connection that has already reached
`Authenticated` or `Failed` without re-verifying anything or issuing a new challenge
(`crates/buzz-relay/src/connection.rs`, `crates/buzz-relay/src/handlers/auth.rs`).

## Matching rule

`verify_nip42_event` treats the challenge as one of five independent checks a
candidate `AUTH` event must all pass (kind, Schnorr signature, challenge match,
relay-URL match, `created_at` tolerance). The challenge check specifically: the
event's `"challenge"` tag must be present, and its content must be byte-identical to
the string the relay generated for that connection; anything else --
missing tag, wrong value, stale value from a previous connection -- produces
`AuthError::ChallengeMismatch`, distinct from the other four failure reasons the same
function can return (`crates/buzz-auth/src/nip42.rs`).

The challenge string itself carries no expiry timestamp or signature of its own. Its
effective lifetime is bounded externally by two unrelated mechanisms: the relay's
5-second `AUTH_TIMEOUT`, which cancels the whole connection if no valid `AUTH` arrives
in time, and, once a response does arrive, the signed event's own +/-60 second
`created_at` tolerance (`crates/buzz-relay/src/connection.rs`,
`crates/buzz-auth/src/nip42.rs`). Neither mechanism inspects the challenge value
itself -- both act on the connection or the event around it.

## Client-side handling

`buzz-ws-client`'s `NostrWsConnection::authenticate` waits up to
`AUTH_CHALLENGE_TIMEOUT_SECS` (20 seconds) for the `AUTH` frame, then hands the
extracted challenge string to `build_auth_event`, which calls
`EventBuilder::auth(challenge, relay_url)` to attach the `"challenge"` and `"relay"`
tags before signing (`crates/buzz-ws-client/src/connection.rs`,
`crates/buzz-ws-client/src/message.rs`). Before that hand-off, `wait_for_auth_challenge`
rejects any incoming challenge longer than 1024 bytes with
`WsClientError::AuthFailed("challenge exceeds 1024 bytes")` -- a client-side sanity
bound; the relay itself never emits anything but exactly 64 hex characters, so this
bound exists to protect the client against a malformed or hostile peer, not against
normal relay behavior.

The wire contract is implementable without `buzz-ws-client` at all:
`crates/buzz-test-client/tests/nip42_host_binding_live.rs` reads the raw
`["AUTH", "<challenge>"]` frame, takes array index 1 as the challenge string, and
signs it with the same `nostr::EventBuilder::auth(&challenge, relay_url)` construction
`buzz-ws-client` uses internally -- a real, working example of the minimum a
hand-rolled client needs to implement this half of NIP-42.

## Use cases

- **Implementing or auditing a Nostr client against this relay.** A client author
  needs to know exactly what to echo back (the tag name, that it must be
  byte-identical, and that it lives inside a signed event rather than a bare reply)
  to get past authentication at all.
- **Diagnosing a `ChallengeMismatch` rejection.** Distinguishing "wrong challenge
  value" from the handshake's other four failure reasons (bad signature, wrong relay
  URL, expired timestamp, or a later ban/allowlist/membership denial) starts with
  knowing the challenge check is a single, independent equality test.
- **Reasoning about replay protection.** The challenge is connection-scoped and
  single-use by construction (a fresh value per connection, discarded once matched or
  once the connection times out), which is one of two properties (the other being the
  `created_at` window) that keep a captured `AUTH` event from being replayed against a
  different connection.

## Boundary

**Against the full authentication flow.** This node does not narrate the connection
lifecycle, the ban/allowlist/membership gates that run after a challenge is matched,
NIP-OA agent-to-owner delegation, or per-message-type (`EVENT`/`REQ`/`COUNT`)
enforcement -- all of that is `architecture-flows-websocket-authentication`'s
territory, linked via this node's `references` relationship rather than restated here.

**Against NIP-98 HTTP auth.** `crates/buzz-auth/src/nip98.rs` (kind:27235) is a
sibling authentication path for the relay's HTTP surface. It has no relay-issued
challenge at all -- its replay protection is a distinct mechanism
(`nip98_replay.rs`). Not covered here.

**Against Blossom upload auth.** `KIND_BLOSSOM_AUTH` (24242, BUD-01) is a separate,
differently-shaped authorization event for media upload, unrelated to the NIP-42
challenge. Not covered here.

**Against `layers-authentication-nip-42-authentication` (issue #1028, not yet
merged).** That sibling task documents NIP-42 authentication as a whole concept; this
node's subject -- the challenge value's own mechanics -- is a proper subset of it. No
relationship edge exists yet because that node is not present on `origin/launchpad`.

## Scope and omissions

**This document covers** what the NIP-42 challenge string is, how it is generated,
stored, transmitted, and matched, its client-side handling (including the 1024-byte
sanity bound and the hand-rolled-client example), what bounds its effective lifetime,
and its boundary against the surrounding authentication flow and the NIP-98/Blossom
sibling mechanisms.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full connection-to-authenticated round trip, including ban/allowlist/membership gates and NIP-OA delegation | `architecture-flows-websocket-authentication` |
| NIP-42 authentication as a whole concept | `#1028` (`layers-authentication-nip-42-authentication`, not yet merged) |
| NIP-98 HTTP auth and its replay protection | Not yet in this corpus |
| Blossom (BUD-01) upload authentication | Not yet in this corpus |
| Per-message-type (`EVENT`/`REQ`/`COUNT`) enforcement of the resulting authenticated state | `architecture-flows-websocket-authentication` |

**Expected but not verified when this node was written:**

- **Whether any client other than `buzz-ws-client` and the test-client examples cited
  above implements this wire contract** (e.g. the desktop or mobile app's own
  networking code, if it bypasses `buzz-ws-client`) was not checked; only the crates
  cited in the evidence ledger were opened.
- **The `EventBuilder::auth` implementation itself** (from the external `nostr` crate)
  was not read -- this node trusts its tag-construction behavior based on the
  `"challenge"`/`"relay"` tags `verify_nip42_event` and the test suite actually observe
  on the resulting signed events, not on that crate's own source.
