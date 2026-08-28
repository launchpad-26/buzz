---
id: layers-authentication-nip-42-authentication
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
  - statement: "buzz-auth's nip42 module doc states the mechanism in three steps: the relay sends [\"AUTH\", \"<challenge>\"] via generate_challenge, the client signs a kind:22242 event with challenge and relay tags, and the relay validates it via verify_nip42_event; AUTH events are never stored or logged because they may contain bearer tokens."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "generate_challenge produces a NIP-42 challenge as 32 CSPRNG bytes, hex-encoded."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "verify_nip42_event checks, in order: the event's kind equals Kind::Authentication, the event passes buzz_core::verify_event (id hash and Schnorr signature), the event's challenge tag matches the expected challenge, the event's relay tag matches this relay's URL after normalization (localhost/::1 treated as 127.0.0.1, trailing slash stripped), and the event's created_at is within a 60-second tolerance (TIMESTAMP_TOLERANCE_SECS) of now."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "kind.rs defines KIND_AUTH = 22242 with the doc comment 'NIP-42 auth event -- never stored (carries bearer tokens)', distinguishing it from KIND_BLOSSOM_AUTH = 24242 (BUD-01 Blossom upload auth, also never stored)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-auth's crate-level doc comment lists exactly two auth paths in one table -- NIP-42 over WebSocket (challenge/response, client signs kind:22242) and NIP-98 over HTTP (signed kind:27235 event in an Authorization: Nostr header) -- and states three security invariants: AUTH events (kind:22242) are never stored or logged, all paths produce an AuthContext bound to the connection, and there is no JWT validation, token management, or IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "AuthError enumerates the rejection reasons an authentication attempt can produce: InvalidSignature, ChallengeMismatch, RelayUrlMismatch, EventExpired, Nip98Invalid(String), Nip98Replay, PubkeyMismatch, InsufficientScope{required,have}, ChannelAccessDenied, and Internal(String) -- the first four (InvalidSignature, ChallengeMismatch, RelayUrlMismatch, EventExpired) are NIP-42-specific per their own doc comments, the two Nip98* variants are NIP-98-specific, and the remainder are shared post-authentication concerns."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs"
  - statement: "buzz-auth's nip98 module doc describes NIP-98 as 'the standard Nostr HTTP Auth pattern used by Nostr.build, Blossom, and other Nostr HTTP services,' explicitly 'stateless -- no WebSocket session required,' verified per-request from a short-lived kind:27235 event carrying a target URL, HTTP method, and optional body-hash tag, sent as an Authorization: Nostr header rather than a persistent connection state."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "The relay's NIP-11 relay-information document's auth_required field is documented as 'Whether NIP-42 authentication is required before subscribing or publishing events.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "crates/buzz-relay/src/connection.rs and crates/buzz-relay/src/handlers/auth.rs are the relay-side consumers of nip42.rs: connection.rs owns the per-connection AuthState and the 5-second AUTH_TIMEOUT background task, and handlers/auth.rs's handle_auth calls AuthService::verify_auth_event (which wraps verify_nip42_event) before running community ban, pubkey-allowlist, and relay-membership gates."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "crates/buzz-ws-client/src/connection.rs implements the client half of the NIP-42 round trip: NostrWsConnection::authenticate waits up to AUTH_CHALLENGE_TIMEOUT_SECS (20s, asserted >= 20 in a const block) for the AUTH challenge frame, builds and signs a kind:22242 event, sends it, and waits up to AUTH_OK_TIMEOUT_SECS (20s) for the matching OK response."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
  - statement: "crates/buzz-ws-client's connect_authenticated and NostrWsConnection are consumed directly, within this repository's Rust crates, only by crates/buzz-test-client/src/lib.rs -- the desktop app's WebSocket client is implemented separately in TypeScript, not through this Rust crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/lib.rs"
      - "crates/buzz-test-client/src/lib.rs"
  - statement: "The desktop app's relayAuthPolicy.ts implements its own client-side policy for interpreting NIP-42 AUTH OK responses: its module doc states that historically any OK false latched the session terminal, but the relay sends OK false for conditions that are transient from the client's side (a duplicate AUTH on an already-authenticated connection, or a verification failure covering clock-skew and fail-closed DB-lookup errors on retry), and only restricted:/blocked: rejections are treated as permanent, with a MAX_CONSECUTIVE_AUTH_REJECTIONS latch guarding against flapping on a genuinely broken identity."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayAuthPolicy.ts"
  - statement: "crates/buzz-cli, the agent-first CLI, authenticates its HTTP requests via NIP-98 (sign_nip98, an Authorization: Nostr header built for each POST /events, POST /query, and GET request), not via a NIP-42 WebSocket round trip -- BUZZ_PRIVATE_KEY signs the per-request NIP-98 event, not a NIP-42 AUTH event."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs"
      - "crates/buzz-cli/src/lib.rs"
  - statement: "verify_nip42_event calls buzz_core::verify_event, the same signature/id verification function the relay's persistent-event, ephemeral-event, and agent-observer-event ingest paths call -- NIP-42's cryptographic proof is Buzz's general signed-event verification applied to one specific event kind (22242), not a separate cryptographic mechanism."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-core/src/verification.rs"
  - statement: "NIP-42 exists in the Nostr protocol specifically so a relay can learn who a connecting client is without any password, session cookie, or bearer token ever crossing the wire -- the challenge/response exchange proves control of a keypair using the same signing mechanism every other Nostr event already uses, rather than introducing a second, protocol-specific credential system."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-auth/src/lib.rs"
    confidence: 0.7
  - statement: "Issue #1028's Definition of done requires this document to define the term in one sentence before deeper explanation, state boundaries/non-goals or what the concept must not be confused with, link the concept to related concepts/implementation/verification, and use examples only to clarify the concept without introducing a second canonical concept -- section shapes that correspond to templates/concept.md's Definition, Boundary, Related-resources/relationships, and Use-cases sections respectively."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1028 definition of done"
  - statement: "crates/buzz-auth/src/nip42.rs carries its own #[cfg(test)] mod tests with eight #[test] functions exercising generate_challenge and verify_nip42_event directly, independent of the end-to-end tests architecture-flows-websocket-authentication catalogues."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-principles-signed-events
---

# Concept: NIP-42 Authentication

How a Buzz relay learns, over a WebSocket connection, which Nostr keypair a
connecting client controls -- without a password, session cookie, JWT, or
identity-provider dependency ever being involved.

## Definition

**NIP-42 authentication is the challenge/response mechanism by which a Buzz
relay WebSocket connection proves the connecting party controls a specific
Nostr keypair: the relay issues a random challenge, the client returns it
inside a Schnorr-signed `kind:22242` event carrying `challenge` and `relay`
tags, and the relay verifies that event's signature and tag contents before
binding the connection to the signer's pubkey** (`crates/buzz-auth/src/nip42.rs`,
`crates/buzz-core/src/kind.rs`).

Buzz implements this over WebSocket only. A structurally similar but
distinct mechanism, NIP-98, authenticates the relay's separate HTTP surface
per-request rather than per-connection -- see *Boundary*, below, for how the
two differ and why they are not the same concept.

## Use cases

A reader needs this concept when:

- **Building or debugging a Nostr client that connects to a Buzz relay over
  WebSocket.** Any such client must complete the NIP-42 round trip before
  `EVENT`, `REQ`, or `COUNT` messages are accepted -- the relay's NIP-11
  document advertises `auth_required: true` for exactly this reason
  (`crates/buzz-relay/src/nip11.rs`). `crates/buzz-ws-client` is Buzz's own
  Rust implementation of the client half (`NostrWsConnection::authenticate`),
  and `crates/buzz-test-client` is, within this repository's Rust crates, its
  only direct consumer -- the desktop app's WebSocket client is written
  separately in TypeScript.
- **Interpreting a NIP-42 `OK false` response correctly on the client
  side.** The desktop app's `relayAuthPolicy.ts` exists because not every
  `OK false` means the same thing: a duplicate AUTH on an already-authenticated
  connection and a transient clock-skew or DB-lookup failure are both
  recoverable, while `restricted:`/`blocked:` rejections are not. A reader
  building similar client logic needs this concept's boundary between
  "authentication mechanism" and "what a rejection reason implies" to avoid
  re-deriving that policy from scratch.
- **Deciding which auth path a new HTTP-facing feature should use.** Because
  NIP-42 is WebSocket-only, a feature that authenticates an HTTP request
  (as `buzz-cli` does for `POST /events`, `POST /query`, and reads) reaches
  for NIP-98 instead, not NIP-42 -- confusing the two produces code that
  tries to complete a connection-bound challenge/response handshake for a
  request that has no persistent connection to bind it to.

## Boundary

**NIP-42 is not NIP-98.** Both live in `buzz-auth` and both ultimately
verify a Schnorr-signed Nostr event, but they differ in transport and
statefulness: NIP-42 is a WebSocket-only, per-connection challenge/response
exchange (the relay issues a challenge, the client proves it once per
connection, and the result is cached as connection state); NIP-98 is
stateless and per-request, verifying a fresh, short-lived `kind:27235` event
on every HTTP call with no challenge and no connection to bind to
(`crates/buzz-auth/src/nip98.rs`). `AuthError`'s variant set reflects this
split directly: `ChallengeMismatch`, `RelayUrlMismatch`, and `EventExpired`
are NIP-42-shaped rejections; `Nip98Invalid` and `Nip98Replay` are NIP-98's
own (`crates/buzz-auth/src/error.rs`). Do not use this document as the
reference for NIP-98 -- it is out of scope here (see *Scope and omissions*).

**NIP-42 authentication is not the WebSocket authentication flow.** This
node explains *what NIP-42 is and why it exists as a concept*: the
challenge/response mechanism, its one required event kind, and where it sits
relative to NIP-98 and to Buzz's general signed-event verification. It does
not walk through the connection state machine, the ordered handler
sequence, the post-crypto ban/allowlist/membership gates, or the full
failure table -- `architecture-flows-websocket-authentication` (linked
below) already documents that flow in detail, and duplicating it here would
create two sources that can drift out of sync. A reader who needs the
step-by-step mechanics should follow that link, not expect them here.

**NIP-42 authentication is not general Nostr event signing.** Every event
Buzz accepts is Schnorr-signed and passes through the same
`buzz_core::verify_event` that `verify_nip42_event` itself calls
(`architecture-principles-signed-events`, linked below) -- NIP-42 is that
general mechanism applied to one specific event kind (`22242`) for one
specific purpose (proving connection identity), not a separate
cryptographic primitive.

**NIP-42 authentication is not authorization.** A successful NIP-42
handshake proves *who signed*, nothing more. What that identity is then
permitted to do -- channel membership, community bans, pubkey allowlisting
-- is decided by gates that run immediately afterward, documented in
`architecture-flows-websocket-authentication` rather than here.

## Verification

`crates/buzz-auth/src/nip42.rs`'s own `#[cfg(test)] mod tests` exercises
`generate_challenge` and `verify_nip42_event` directly -- the unit-level
proof that this concept's mechanism, as described above, actually behaves
as claimed. The fuller verification catalogue (integration and end-to-end
coverage of the surrounding flow) is
`architecture-flows-websocket-authentication`'s to maintain, linked below
rather than repeated here.

## Scope and omissions

**This document covers** what NIP-42 authentication is (the challenge/response
mechanism and its one event kind), why Buzz uses it, its relationship to
Buzz's general signed-event verification, and its boundary against NIP-98
HTTP Auth and against the detailed WebSocket authentication flow.

**It does not cover, and these are gaps rather than silence:**

- **The full WebSocket authentication flow** -- trigger/preconditions,
  ordered relay/client interactions, the post-crypto ban/allowlist/membership
  gates, and the complete failure table. Owned by
  `architecture-flows-websocket-authentication` (linked via `relationships`
  below), not duplicated here.
- **NIP-98 HTTP Auth in depth** -- named here only for the boundary this
  concept needs; it is not documented as its own corpus node yet.
- **NIP-OA agent-to-owner delegation** (the `auth` tag inside a NIP-42 AUTH
  event) -- mentioned nowhere in this document; it is a separate concept
  layered on top of a successful NIP-42 handshake, not part of the
  handshake itself.
- **Rate limiting and admission control** applied to a connection after
  authentication completes.
- **Whether every Buzz client (desktop, mobile) implements the NIP-42
  client half identically to `buzz-ws-client`.** Only `buzz-ws-client` (via
  `buzz-test-client`) and the desktop app's TypeScript implementation
  (`relayAuthPolicy.ts`, cited above) were checked directly; the mobile
  Flutter client's own WebSocket auth handling was not inspected while
  writing this node and is not claimed here either way.
