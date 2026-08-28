---
id: architecture-flows-websocket-authentication
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "WebSocket authentication is NIP-42 challenge/response: the relay sends [\"AUTH\", \"<challenge>\"], the client signs a kind:22242 event carrying the challenge and relay URL, and the relay validates it with verify_nip42_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "Kind 22242 is the relay's KIND_AUTH constant, documented as never stored (it may carry bearer tokens)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The challenge is 32 CSPRNG bytes, hex-encoded (64 hex characters), generated fresh per connection by generate_challenge."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "verify_nip42_event checks, in order: event kind equals Authentication, the Schnorr signature verifies, the event's challenge tag matches the expected challenge, the event's relay tag matches this relay's URL after normalization (localhost/::1 treated as equivalent to 127.0.0.1, trailing slash stripped), and the event's created_at is within +/-60 seconds of now."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "AuthError enumerates the rejection reasons a NIP-42 or NIP-98 verification attempt can produce: InvalidSignature, ChallengeMismatch, RelayUrlMismatch, EventExpired, Nip98Invalid, Nip98Replay, PubkeyMismatch, InsufficientScope, ChannelAccessDenied, and Internal."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs"
  - statement: "buzz-auth's own module documentation states as a security invariant that AUTH events (kind:22242) are never stored or logged, and that every successful auth path produces an AuthContext bound to the connection with no JWT validation, token management, or IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "On a new WebSocket connection, the relay acquires a connection-semaphore permit, generates a challenge, stores it as AuthState::Pending{challenge} on the per-connection ConnectionState, and sends the AUTH challenge frame before registering the connection with the connection manager -- registration happens only after the challenge send succeeds, so an immediate client disconnect leaves no leaked registry entry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "A background task enforces AUTH_TIMEOUT = 5 seconds: if the connection has not reached AuthState::Authenticated within 5 seconds of being established, the task cancels the connection's CancellationToken, which tears down the send loop, heartbeat loop, and receive loop and closes the socket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "handle_auth (the relay's NIP-42 AUTH message handler) first checks the connection's current AuthState: an AUTH received while already Authenticated or already Failed is rejected immediately with an OK-false reply and does not re-run verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "After buzz_auth::AuthService::verify_auth_event succeeds, handle_auth runs three further gates in order before marking the connection Authenticated: (1) a community ban check on the authenticated pubkey, cascading to the NIP-OA-proven owner pubkey if the agent itself is clear; (2) a pubkey-allowlist check, only when pubkey_allowlist_enabled is set and the auth method is Nip42; (3) a relay-membership check via enforce_relay_membership, which supports NIP-OA owner-delegation fallback. Any DB error during the ban or allowlist check fails closed (denies) rather than treating the error as a pass."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "On success, handle_auth sets the connection's AuthState to Authenticated(auth_ctx), registers the pubkey with the connection manager via set_authenticated_pubkey, and replies OK true; a successful NIP-42 verification alone grants every known Scope, since fine-grained access in pure-Nostr mode is enforced later by NIP-29 channel membership rather than by scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-auth/src/lib.rs"
  - statement: "The EVENT, REQ, and COUNT handlers each independently read the connection's AuthState and reject with an \"auth-required: not authenticated\" (or, for REQ, \"auth-required: authenticate before subscribing\") message when it is not AuthState::Authenticated -- there is no single central gate; each handler enforces the requirement itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "The relay's own NIP-11 relay-information document advertises limitation.auth_required = true unconditionally, and a source comment records that this exists specifically because the REQ, EVENT, and COUNT handlers unconditionally require an authenticated connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "For a persistent or ephemeral EVENT submitted on an authenticated connection, the relay rejects the event unless event.pubkey equals the connection's authenticated pubkey, except for kind:1059 gift-wrap events (NIP-17), whose outer signer is an ephemeral key by design. This check runs before both the ephemeral and persistent event branches."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "A kind:22242 (AUTH) event submitted via an EVENT message rather than an AUTH message is rejected by the ingest path rather than accepted as an ordinary event."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The client-side buzz-ws-client crate implements the other half of the round trip: NostrWsConnection::connect_authenticated opens the socket, waits up to AUTH_CHALLENGE_TIMEOUT_SECS (20s) for the relay's AUTH challenge, builds and signs a kind:22242 event via build_auth_event (EventBuilder::auth, optionally carrying a NIP-OA auth tag), sends it as [\"AUTH\", event], and waits up to AUTH_OK_TIMEOUT_SECS (20s) for the matching OK response; a false OK.accepted becomes WsClientError::AuthFailed(message)."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "The relay's 5-second AUTH_TIMEOUT (bounding how long an unauthenticated socket may hold a connection-semaphore permit) and the ws-client library's 20-second challenge-wait and 20-second OK-wait bounds are sized for different failure domains -- the relay's bound protects server-side resource exhaustion from slow or malicious sockets, while the client library's longer bounds tolerate ordinary network latency for a cooperating client -- so a well-behaved client on a normal network completes well inside the relay's 5-second window despite the client library nominally tolerating much longer."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-ws-client/src/connection.rs"
    confidence: 0.6
  - statement: "Issue #686's Definition of done, combined with this task's category-specific tail for flow nodes, requires this document to state trigger/preconditions/termination, list ordered interactions and data/state movement, identify authentication/authorization/trust-boundary crossings, and document failure/abort/rollback behavior linked to representative verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#686 definition of done and its category-specific DoD tail"
---

# Flow: WebSocket Authentication (NIP-42)

How a Buzz relay WebSocket connection moves from an anonymous socket to an
authenticated, pubkey-bound connection, and what happens when it does not.

## Trigger, preconditions, and termination

**Trigger.** A client opens a WebSocket connection to the relay (e.g.
`wss://relay.example.com`). The relay resolves the connection's community
(`TenantContext`) from the connection host before any frame is read; that
tenant binding is fixed for the connection's lifetime and is not part of the
auth flow itself.

**Preconditions.**

- The connecting party holds a Nostr keypair (`nostr::Keys`) capable of
  signing a Schnorr event.
- The relay has a free connection-semaphore permit; if not, the connection is
  rejected before a challenge is ever sent (`crates/buzz-relay/src/connection.rs`).
- The community the connection is scoped to is active
  (`is_community_active`), checked before the connection is admitted at all.

**Termination / outcome.** The flow ends in exactly one of:

1. **Authenticated** -- `AuthState::Authenticated(AuthContext)`. The
   connection may now send `EVENT`, `REQ`, and `COUNT` messages, all of which
   independently require this state (see *Trust-boundary crossings*).
2. **Failed** -- `AuthState::Failed`. Set on any rejected AUTH attempt (bad
   signature, wrong challenge, wrong relay, expired timestamp, ban, allowlist
   denial, or membership denial). A `Failed` connection is not retried
   in-place: a second AUTH message on the same connection is rejected
   immediately without re-verification (see *Failure, abort, and rollback*).
3. **Closed on timeout** -- the connection never reaches `Authenticated`
   within 5 seconds of being established and is cancelled by the relay.

There is no partial or intermediate authenticated state: a connection is
either `Pending`, `Authenticated`, or `Failed`.

## Ordered interactions and data/state movement

1. **Relay: admit the socket.** `handle_connection` acquires a
   connection-semaphore permit and creates the connection's shared state
   (`ConnectionState`), including a fresh `RwLock<AuthState>`.
2. **Relay: issue the challenge.** `generate_challenge()` produces 32 CSPRNG
   bytes, hex-encoded. The relay stores it as
   `AuthState::Pending { challenge }` on the connection and sends
   `["AUTH", "<challenge>"]` as the first frame. The connection is registered
   with the connection manager only *after* this send succeeds, so a client
   that disconnects before receiving the challenge leaves no registry entry.
3. **Relay: start the auth-timeout clock.** A background task races a
   5-second sleep against the connection's cancellation token. If
   `AuthState` is not `Authenticated` when the sleep elapses, the task
   cancels the connection.
4. **Client: receive the challenge and build the response.**
   `NostrWsConnection::authenticate` (buzz-ws-client) waits up to 20 seconds
   for the `AUTH` frame, then calls `build_auth_event`, which uses
   `EventBuilder::auth(challenge, relay_url)` to construct a kind:22242
   event carrying the `challenge` and `relay` tags, optionally attaching a
   NIP-OA `auth` tag, and signs it with the caller's keys.
5. **Client: send the signed AUTH event.** The client sends
   `["AUTH", <signed kind:22242 event>]` and waits up to 20 seconds for a
   matching `OK` response keyed by the event id.
6. **Relay: dispatch to the AUTH handler.** `handle_text_message` parses the
   frame as `ClientMessage::Auth(event)` and calls `handlers::auth::handle_auth`.
7. **Relay: state-machine guard.** `handle_auth` reads the current
   `AuthState`. If it is already `Authenticated` or already `Failed`, the
   handler replies `OK false` immediately and returns -- no re-verification
   is attempted (see *Failure, abort, and rollback*).
8. **Relay: extract the NIP-OA tag before verification.** The handler pulls
   any `auth` tag out of the event now, ahead of consuming it in
   verification. This is safe because the tag is inside the same signed
   event: if it were tampered with, NIP-42 verification fails first and the
   extracted value is never used.
9. **Relay: pure cryptographic verification.** `AuthService::verify_auth_event`
   runs `verify_nip42_event` (via `spawn_blocking`, since Schnorr
   verification is CPU-bound), checking kind, signature, challenge match,
   relay-URL match, and the +/-60s timestamp window, in that order. No
   database or network call happens in this step.
10. **Relay: ban gate.** On successful crypto verification, the relay checks
    `moderation_restriction_state` for the authenticated pubkey, and -- if
    that pubkey is clear -- for its NIP-OA-proven owner pubkey (owner ban
    cascades to the agent; agent ban does not cascade to the owner). A DB
    error here denies fail-closed, distinguished from a real ban so an
    innocent user is never told they are banned on a false premise.
11. **Relay: pubkey-allowlist gate.** Only when `pubkey_allowlist_enabled`
    is on and the auth method is `Nip42`, the relay checks
    `is_pubkey_allowed` for the community. A DB error denies fail-closed.
12. **Relay: relay-membership gate.** `enforce_relay_membership` checks
    community membership, with a NIP-OA owner-delegation fallback so an
    agent can authenticate on its owner's behalf. On an open relay that does
    not require membership, the handler separately backfills the NIP-OA
    owner mapping for observer-frame auth even when this gate was not
    exercised.
13. **Relay: commit state.** On passing every gate, the handler sets
    `AuthState::Authenticated(auth_ctx)`, calls
    `set_authenticated_pubkey` on the connection manager (binding the
    connection id to the pubkey for the rest of its life), and replies
    `OK true`.
14. **Client: unblock.** The client's pending `wait_for_ok` call resolves,
    `authenticate()` returns `Ok(())`, and the caller may now send `EVENT`,
    `REQ`, or `COUNT` messages on this same connection.
15. **Relay: bind every later `EVENT` to this identity.** For every
    subsequent `EVENT` on the connection, the relay compares
    `event.pubkey` against the connection's authenticated pubkey (except
    kind:1059 gift wraps) before either the ephemeral or persistent event
    path runs, rejecting a mismatch outright. Authentication is therefore
    not just a one-time gate -- it fixes the identity every later event on
    the connection is checked against.

## Trust-boundary and authorization crossings

- **Anonymous socket to cryptographically-proven pubkey (step 9).** The
  only thing crossing this boundary is a Schnorr-signed challenge; no
  password, token, or session cookie is ever involved. `buzz-auth`'s module
  documentation states this as a design invariant: no JWT validation, no
  token management, no IdP dependency.
- **Proven pubkey to community-scoped principal (steps 10-12).** A
  cryptographically valid signature only proves *who signed*; the ban,
  allowlist, and membership gates decide whether that identity is allowed
  to act inside *this* community. All three are DB-backed and all three
  fail closed on a DB error.
- **Agent to owner (NIP-OA delegation, steps 8, 10, 12).** An `auth` tag
  inside the signed AUTH event can assert that the authenticating pubkey is
  acting as an agent for a separate owner pubkey. Because the tag rides
  inside the Schnorr-signed event, it is integrity-protected by the same
  signature check as the rest of the event -- a forged or duplicated `auth`
  tag (more than one present) is treated as no valid tag at all, per
  NIP-OA, rather than an ambiguous one being trusted.
- **Authenticated connection to per-event identity (step 15).** Completing
  AUTH does not, by itself, authorize arbitrary future events. Each `EVENT`
  is separately checked against the bound pubkey, so a connection cannot be
  authenticated as one identity and then used to publish as another.
- **Connection-level auth to per-message-type enforcement.** There is no
  single chokepoint enforcing "must be authenticated" -- `EVENT`, `REQ`, and
  `COUNT` each read `AuthState` independently inside their own handlers. A
  future new message type that forgets this check would silently admit
  unauthenticated traffic; NIP-11's `auth_required: true` is a
  relay-level *claim* about this behavior, not an enforcement mechanism
  for it.

## Failure, abort, and rollback behavior

There is no partially-authenticated state to roll back -- every rejection
either leaves the connection in `AuthState::Pending` (recoverable, the
client may try again) or moves it to `AuthState::Failed` (terminal for that
connection) or closes the socket outright. Specifically:

| Failure | Detected by | Resulting state | Client-visible signal |
|---|---|---|---|
| Wrong event kind (not 22242) | `verify_nip42_event` | `Failed` | `OK false`, `"auth-required: verification failed"` |
| Bad Schnorr signature | `buzz_core::verify_event` inside `verify_nip42_event` | `Failed` | `OK false`, `"auth-required: verification failed"` |
| Challenge does not match the one issued | `verify_nip42_event` | `Failed` | `OK false`, `"auth-required: verification failed"` |
| Relay URL tag does not match (after normalization) | `verify_nip42_event` | `Failed` | `OK false`, `"auth-required: verification failed"` |
| `created_at` outside +/-60s | `verify_nip42_event` | `Failed` | `OK false`, `"auth-required: verification failed"` |
| Authenticated pubkey (or its NIP-OA owner) is banned | ban gate in `handle_auth` | `Failed`, then immediate WebSocket close | `OK false`, `"blocked: you are banned from this community"`, socket closed via the control channel ahead of cancellation |
| DB error during the ban check | ban gate in `handle_auth` | `Failed`, then immediate WebSocket close | `OK false`, `"error: internal error checking restriction state"` |
| Pubkey not on the allowlist (when enabled) | allowlist gate | `Failed` | `OK false`, `"auth-required: verification failed"` |
| Not a relay member (no NIP-OA fallback applies) | `enforce_relay_membership` | `Failed` | `OK false`, `"restricted: not a relay member"` |
| A second AUTH is sent after `Authenticated` | state-machine guard | unchanged (`Authenticated`) | `OK false`, `"auth-required: already authenticated"` |
| A second AUTH is sent after `Failed` | state-machine guard | unchanged (`Failed`) | `OK false`, `"auth-required: authentication already failed"` |
| No valid AUTH within 5 seconds of connecting | `AUTH_TIMEOUT` background task | connection cancelled | socket closed; no further application-level message |
| A later `EVENT`'s pubkey does not match the authenticated pubkey (non-gift-wrap) | pubkey-binding check in the event handler | connection state unchanged | that `EVENT` rejected with `OK false`; the connection itself is not torn down |
| `EVENT`, `REQ`, or `COUNT` sent while still `Pending` or `Failed` | each handler's own `AuthState` check | unchanged | `OK false` / `CLOSED` with an `"auth-required: ..."` message, connection stays open |
| Kind:22242 sent as an ordinary `EVENT` instead of an `AUTH` message | ingest path | unchanged | rejected, not stored |

The ban-check-DB-error and allowlist/membership-DB-error cases are
deliberately distinguished from a genuine denial in the warning logs (not
in the client-visible message), so an operator can tell a transient
infrastructure fault from an actual ban or membership decision without the
denied client itself being told which one occurred.

## Verification

- **Unit tests, pure crypto layer:** `crates/buzz-auth/src/nip42.rs`'s
  `#[cfg(test)] mod tests` cover a valid event, wrong challenge, wrong kind,
  expired timestamp, wrong relay, and the localhost/trailing-slash
  normalization rules. `crates/buzz-auth/src/lib.rs`'s tests cover the same
  boundary through `AuthService::verify_auth_event`.
- **Unit tests, NIP-OA tag extraction:** `crates/buzz-relay/src/handlers/auth.rs`'s
  `mod tests` cover a single `auth` tag extracted verbatim, no tag present,
  and duplicate tags treated as no valid tag.
- **End-to-end, happy path:** `test_connect_and_authenticate` in
  `crates/buzz-test-client/tests/e2e_relay.rs` connects and authenticates
  against a live relay.
- **End-to-end, unauthenticated write rejected:** `test_unauthenticated_rejected`
  in the same file connects without completing AUTH and asserts the relay
  either rejects the write, closes the connection, or times out -- all
  three are treated as acceptable relay behavior by that test.
- **End-to-end, AUTH-kind-as-EVENT rejected:** `test_auth_event_kind_rejected`
  asserts a kind:22242 event submitted via `EVENT` is rejected with a
  message mentioning "invalid" or "auth".
- **End-to-end, pubkey binding enforced:** `test_pubkey_mismatch_rejected`
  authenticates as one keypair, then attempts to send an event signed by a
  second keypair on the same connection, and asserts the relay rejects it.
- **End-to-end, protocol advertisement:** a test in the same file asserts
  the relay's NIP-11 document advertises `limitation.auth_required: true`.

These end-to-end tests are marked `#[ignore]` (the repository's convention
for tests that require a live relay plus Postgres and Redis, run via
`just test`, not `just test-unit`) -- this document links them as
representative coverage rather than asserting they were executed as part of
authoring it.

## Scope and omissions

**This document covers** the NIP-42 WebSocket authentication round trip
between `buzz-ws-client` (or an equivalent client) and `buzz-relay`: the
challenge/response mechanics, the connection-state machine, the ban /
allowlist / membership gates that run immediately after cryptographic
verification, NIP-OA agent-to-owner delegation as it appears in this flow,
and per-message-type auth enforcement for `EVENT` / `REQ` / `COUNT`.

**It does not cover, and these are gaps rather than silence:**

- **NIP-98 HTTP Auth** (`crates/buzz-auth/src/nip98.rs`, kind:27235) --
  the sibling auth path for the relay's HTTP surface (`POST /events`,
  git smart HTTP, media upload). It shares `buzz-auth`'s module but is a
  distinct flow with its own replay-protection mechanism
  (`nip98_replay.rs`) and deserves its own node.
  Not yet in this corpus.
- **The full NIP-29 channel-membership and moderation model** -- this
  document names the relay-membership gate that runs during auth, but the
  broader channel read/write access model (`buzz-auth/src/access.rs`,
  `crate::api::relay_members`) is a separate, larger surface.
  Not yet in this corpus.
- **NIP-OA's full owner-delegation and attestation format** -- this
  document describes how the `auth` tag is extracted and how a ban
  cascades, but not the attestation's own structure or how it is minted.
  Not yet in this corpus.
- **Rate limiting and admission control** (`crate::admission`,
  `LimitType::WsEvents`) applied to authenticated connections after this
  flow completes.
  Not yet in this corpus.
- **Numeric precision of the reconciliation between the relay's 5-second
  `AUTH_TIMEOUT` and the client library's 20-second wait bounds is an
  inference (see the INFERENCE evidence entry above), not something either
  source states directly.** Neither file cross-references the other's
  constant, so the relationship was reasoned rather than read.

**No `relationships` in this node's front matter.** No other
`architecture`/flow corpus node is confirmed merged at the recorded
revision, and a `relationships[].target` naming an id no loaded node
carries is a hard validation error (`launchpad/docs/corpus/AGENTS.md`).
The natural future edges are `implements` toward the NIP-98 HTTP-auth
sibling node and `part-of` toward a broader "connection lifecycle"
container node, once either exists.
