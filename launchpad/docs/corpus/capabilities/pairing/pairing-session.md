---
id: capabilities-pairing-pairing-session
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "PairingSession is documented as tracking protocol state for one side of a NIP-AB device-pairing exchange, and is constructed via new_source (the secret-holding device) or new_target (the scanning, receiving device), giving each session exactly one Role — Source or Target."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:76-107"
      - "crates/buzz-core/src/pairing/session.rs:112-142"
      - "crates/buzz-core/src/pairing/session.rs:328-352"
  - statement: "SessionState is a seven-variant enum — Waiting, Confirming, AwaitingConfirmation, Transferring, PayloadExchanged, Completed, Aborted — and every state-producing PairingSession method (handle_offer, confirm_sas, handle_sas_confirm, confirm_target_sas, handle_payload/handle_return_payload, send_complete/send_source_complete, abort/handle_abort) asserts the session's current state and role with expect_state/expect_role before acting, returning PairingError::UnexpectedMessage on a mismatch."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:59-75"
      - "crates/buzz-core/src/pairing/session.rs:748-767"
  - statement: "A session created via new_source generates a fresh ephemeral secp256k1 keypair (Keys::generate()) and a fresh random 32-byte session_secret, and derives session_id from that secret via HKDF-SHA256 (derive_session_id, salt=[], info=\"nostr-pair-session-id\") — the session secret and derived session_id are zeroized on PairingSession::drop, and the session secret is never reused across sessions."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:112-124"
      - "crates/buzz-core/src/pairing/crypto.rs:44-55"
      - "crates/buzz-core/src/pairing/session.rs:773-781"
  - statement: "The Short Authentication String (SAS) is derived only after the source learns the peer's ephemeral pubkey from a received offer event: handle_offer computes an ECDH shared secret between the local ephemeral key and the peer's ephemeral pubkey, derives a 6-digit SAS code and a transcript-hash input from it via HKDF, zeroizes the raw ECDH shared secret immediately after derivation, and transitions the session to SessionState::Confirming."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:149-196"
      - "crates/buzz-core/src/pairing/crypto.rs:70-88"
  - statement: "The transcript hash binds the session_id, both parties' ephemeral pubkeys, the SAS input, and the session secret, and is checked on the target's handle_sas_confirm; a mismatch returns PairingError::TranscriptMismatch, which the pairing-cli caller treats as a hard security failure (possible MITM) and aborts the session with AbortReason::SasMismatch rather than silently retrying."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/crypto.rs:89-100"
      - "crates/buzz-core/src/pairing/session.rs:210-224"
      - "crates/buzz-pairing-cli/src/main.rs:263-286"
  - statement: "The target's session only advances to Transferring (able to receive the payload) after two separate confirmations: handle_sas_confirm moves it to AwaitingConfirmation, and a second, explicit call to confirm_target_sas — gated on the user visually re-approving the SAS code — is required before handle_payload will accept anything; this two-step gate is asserted by the test target_must_confirm_sas_before_payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:63-66"
      - "crates/buzz-pairing-cli/src/main.rs:263-301"
  - statement: "Only one payload is accepted per session in either direction: handle_payload and handle_return_payload each advance the session to SessionState::PayloadExchanged on success, and a second payload attempt is rejected by expect_state's mismatch check — asserted directly by the test reject_duplicate_payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:230-249"
      - "crates/buzz-core/src/pairing/session.rs:748-756"
  - statement: "A pairing session carries a hard, non-extendable lifetime: DEFAULT_TIMEOUT is 120 seconds from session creation (created_at), is_expired() compares elapsed wall-clock time against it, and check_expired() is called at the top of every state-advancing method, returning PairingError::SessionExpired once the deadline has passed regardless of the session's current state."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:43-43"
      - "crates/buzz-core/src/pairing/session.rs:517-520"
      - "crates/buzz-core/src/pairing/session.rs:739-745"
  - statement: "abort() rejects being called from either terminal state (Completed or Aborted) — a finished session cannot be regressed — and returns None (still transitioning locally to Aborted) rather than an event when no peer is known yet, since there is no key to encrypt an abort message to; handle_abort() separately rejects an abort from an unknown peer to prevent any relay observer from killing a session before the peer is authenticated."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:472-515"
  - statement: "AbortReason is a closed, spec-defined set for outbound aborts (SasMismatch, UserDenied, Timeout, ProtocolError) plus an inbound-only Unknown variant produced when deserializing an unrecognized reason string from a peer, which callers MUST NOT construct for outbound use and MUST treat as ProtocolError."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/types.rs:79-96"
  - statement: "Every inbound pairing message is a NIP-44-v2-encrypted, kind:24134 Nostr event; validate_event_basics/validate_nip44_content reject malformed content before decryption, and duplicate event IDs already recorded in the session's processed_ids set are silently discarded (NIP-AB's own Duplicate Event Handling section) to tolerate relay re-delivery, without poisoning the dedup set for a message that fails type-dispatch after passing basic validation."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs:634-767"
      - "crates/buzz-pair-relay/src/lib.rs:343-409"
  - statement: "PairingSession is consumed by two real callers in this repository: crates/buzz-pairing-cli/src/main.rs (a Rust interop-testing CLI exercising both the source and target roles end-to-end over a live relay) and desktop/src-tauri/src/commands/pairing.rs (the shipped Tauri desktop command handling the app's own pairing UI, in both send-identity and recover-identity modes)."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs:106-112"
      - "desktop/src-tauri/src/commands/pairing.rs:1-20"
      - "desktop/src-tauri/src/commands/pairing.rs:36-49"
  - statement: "The mobile app's device-pairing feature (mobile/lib/features/pairing/) is a separate, independent Dart implementation of the client side of the same NIP-AB protocol — it does not call into buzz-core's PairingSession — so its session lifecycle is a parallel implementation of the same protocol state machine, not a consumer of this Rust type."
    entry_class: INFERENCE
    evidence:
      - "mobile/lib/features/pairing/pairing_crypto.dart"
      - "mobile/lib/features/pairing/pairing_provider.dart"
    confidence: 0.75
  - statement: "The pairing-session state machine is exercised by 20 unit tests inside crates/buzz-core/src/pairing/session.rs, covering the full happy path (both forward and reverse payload direction), out-of-order operation rejection, abort from both sides and from terminal states, expired-session rejection, duplicate-event and wrong-type-message dedup edge cases, and secret zeroization on drop."
    entry_class: FACT
    evidence:
      - "grep_count('#[test]', 'crates/buzz-core/src/pairing/session.rs') -> 20"
      - "crates/buzz-core/src/pairing/session.rs:798-1425"
  - statement: "NIP-AB's own spec document states its purpose as defining 'a protocol for securely transferring secrets between two devices over standard Nostr relays using QR-code-initiated, end-to-end encrypted channels with visual confirmation,' is versioned (version 1 is the only currently defined, active version: secp256k1 ECDH, HKDF-SHA256, SAS-6digit, NIP-44 v2 encryption), and requires implementations to surface an error rather than silently ignore an unrecognized protocol version."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:1-33"
  - statement: "No merged corpus node on origin/launchpad at the recorded revision documents this session/state-machine capability directly; two merged architecture nodes discuss device pairing from their own vantage points — architecture-context-nostr-network describes buzz-pair-relay as the transport pairing peers talk to, and architecture-containers-mobile describes the mobile app's own (independent) PairingSocket client — and both are cited here as references rather than duplicated."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md:48"
      - "launchpad/docs/corpus/architecture/containers/mobile.md:55-62"
  - statement: "VISION_PROJECTS.md's own product-capability status table does not list device pairing or a pairing session among its rows, so this capability's maturity claim below rests on shipped code and its test suite rather than on a VISION status marker."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md"
  - statement: "Issue #613 (parent PRD) scopes this task to creating exactly one canonical corpus document at launchpad/docs/corpus/capabilities/pairing/pairing-session.md, distinct from sibling tasks #800 (device-pairing, the overall capability), #801 (pairing-cli) and #802 (pairing-relay), none of which were open or merged at the time this node was drafted."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#803 definition of done, read directly via gh issue view"
relationships:
  - type: part-of
    target: capabilities-pairing-device-pairing
  - type: references
    target: architecture-context-nostr-network
  - type: references
    target: architecture-containers-mobile
---

# Pairing session: capability

A **pairing session** is the bounded, stateful exchange that lets two Buzz
devices — a *source* device that already holds a secret (an `nsec` or a
NIP-46 bunker/connect string) and a *target* device that wants it — transfer
that secret over an untrusted Nostr relay, with a human on each side visually
confirming a short code before anything sensitive moves. It is the protocol
core underneath device pairing: everything a source or target device does
during one QR-initiated pairing attempt, from the moment a session is created
until it completes, aborts, or times out.

## Maturity

**Shipped.** The session state machine (`PairingSession`, `Role`,
`SessionState`) lives in `buzz-core` and is exercised by 20 unit tests
covering the full protocol in both directions, abort handling, expiry, and
dedup edge cases. It has two real callers today: `buzz-pairing-cli` (a Rust
interop-testing tool that runs both roles end-to-end against a live relay)
and `desktop/src-tauri/src/commands/pairing.rs` (the desktop app's own
pairing UI, wired for both sending and recovering an identity). The mobile
app independently re-implements the same protocol's client side in Dart
rather than calling this type. VISION_PROJECTS.md's own capability-status
table does not list pairing, so this maturity claim rests on the code and
tests above, not on a VISION status marker.

## Primary actors and outcomes

- **Source device.** Already holds the secret. Generates the session's
  ephemeral keypair and session secret, displays the resulting QR code,
  and — once a target's offer arrives and the user visually confirms the
  SAS — sends the secret and waits for confirmation that it was imported.
- **Target device.** Scans the source's QR code, sends an offer proving it
  knows the session secret, confirms the SAS the user sees, and — after an
  explicit second user approval — receives and imports the secret.
- **Outcome.** Either the secret moves from source to target (or, in the
  recovery direction, an already-paired target's own held secret moves back
  to a requesting source) and both sides record a completed session, or the
  session ends in an explicit abort (SAS mismatch, user denial, protocol
  error) or a silent timeout — never in an ambiguous or partially-applied
  state.

## Behavioral rules, constraints and variants

- **One role, one state machine per session.** A session is created as
  either `Role::Source` or `Role::Target` and stays that role for its whole
  life; every state-changing method checks both the session's role and its
  current `SessionState` before acting, rejecting anything out of order.
- **States.** `Waiting` (session created, QR displayed or offer sent) →
  `Confirming` (source has computed the SAS and is waiting on the user) /
  `AwaitingConfirmation` (target has verified the transcript hash and is
  waiting on a second, explicit user approval before it will accept a
  payload) → `Transferring` (SAS confirmed, payload may move) →
  `PayloadExchanged` (the one allowed payload has moved) → `Completed`.
  `Aborted` is reachable from any non-terminal state.
- **Key material is per-session and ephemeral.** Each session generates a
  fresh secp256k1 keypair and a fresh random 32-byte session secret; nothing
  is reused across sessions. The session ID, SAS code, and transcript hash
  are all HKDF-SHA256 derivations chained from that session secret and an
  ECDH shared secret computed once the peer's ephemeral pubkey is known. The
  session secret, the derived session ID, and the raw SAS input are zeroized
  when the session is dropped.
- **SAS is a two-sided, two-step gate, not a single check.** The source
  computes and displays the SAS as soon as it receives a valid offer; the
  target already knows it from the QR scan and displays it as soon as it
  sends the offer. The target's own state machine additionally requires an
  explicit second confirmation call after verifying the source's
  transcript-hash-bearing `sas-confirm` message — a transcript mismatch is
  treated as a possible MITM attempt and aborts the session immediately
  rather than being retried.
- **Exactly one payload, either direction.** A session accepts at most one
  payload event; a repeat is rejected by the state check rather than
  silently overwriting anything. The forward direction (source → target)
  and the recovery direction (target → source, used when an
  already-authorized device is asked to return a secret) are both supported,
  but each session only carries the payload in the direction its role was
  created for.
- **Hard timeout, not a renewable one.** Every session has a fixed lifetime
  (120 seconds by default) measured from creation; every state-advancing
  method checks expiry first and fails the same way regardless of what state
  the session was in when time ran out. There is no extension or renegotiation
  of the deadline.
- **Abort is one-way and cannot be replayed.** Once a session reaches
  `Completed` or `Aborted`, both local abort attempts and incoming abort
  events from the peer are rejected — a finished session cannot be
  regressed to a still-in-progress or newly-aborted state. An abort attempted
  before the peer's pubkey is known still transitions the session locally,
  but produces no event to send, since there is no key to encrypt to yet;
  conversely, an abort event is not accepted from an unknown peer, so a relay
  observer cannot kill a session it isn't part of.
- **Duplicate and malformed messages are tolerated, not fatal.** Every
  inbound message must decrypt as a valid NIP-44 v2 payload inside a
  kind:24134 event; a message whose event ID has already been processed in
  this session is silently discarded rather than re-applied (relays may
  re-deliver), and a message that fails type-dispatch for the current state
  does not get recorded as processed, so the same event ID remains available
  if a differently-typed message with that ID legitimately arrives later.

## Boundary

This node does not describe:
- **How events reach the peer.** That is `buzz-pair-relay`'s own job — an
  ephemeral, loopback-only, unauthenticated sidecar relay with its own
  connection caps and rate limits, described at the architecture level in
  `architecture-context-nostr-network` (referenced below) and by #802's own
  pending capability node.
- **The CLI's command-line interface or test-vector tooling.** `buzz-pair`'s
  `source`/`target`/`test-vectors` subcommands are #801's capability, not
  this one — this node covers the session state machine those subcommands
  drive, not their argument parsing or terminal UX.
- **The mobile app's own pairing implementation.** `mobile/lib/features/pairing/`
  is an independent Dart re-implementation of the same protocol's client
  side, described (at the container level) by the already-merged
  `architecture-containers-mobile` node; this document does not restate its
  content or assert that the two implementations share code.
- **The overall device-pairing product capability** (QR generation and
  display, user-facing pairing flows in the desktop and mobile UIs) — that
  is #800's node.
- **The NIP-AB wire specification's full text** — `crates/buzz-core/src/pairing/NIP-AB.md`
  is the spec; this node summarizes the session lifecycle it produces, not
  every MUST/SHOULD clause in the spec itself.

## Relationships

- references: `architecture-context-nostr-network` — the context-level
  description of `buzz-pair-relay` as the transport pairing sessions run
  over.
- references: `architecture-containers-mobile` — the container-level
  description of the mobile app's own (independent) pairing client.

## Scope and omissions

**This node covers** the pairing-session capability: its two actors (source,
target), the `SessionState` state machine and the role/state checks that
gate every transition, how session key material (ephemeral keypair, session
secret, session ID, SAS, transcript hash) is derived and zeroized, the
120-second hard timeout, the single-payload and duplicate/abort handling
rules, and where the capability is realized in code today (`buzz-core`,
`buzz-pairing-cli`, the desktop Tauri command).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The ephemeral sidecar relay's own connection/rate/session caps | `#802` (pairing-relay, not yet drafted) |
| The `buzz-pair` CLI's commands and interop-testing UX | `#801` (pairing-cli, not yet drafted) |
| The overall device-pairing product capability and its UI flows | `#800` (device-pairing, not yet drafted) |
| The mobile app's own Dart pairing implementation, in detail | `architecture-containers-mobile` (merged) |
| The NIP-AB wire specification's full normative text | `crates/buzz-core/src/pairing/NIP-AB.md` |
| The step-by-step flow one pairing interaction takes, start to finish | a future flow-type corpus node, not yet scheduled |

**Expected but not verified when this node was written:**

- **The desktop Tauri pairing command's full behavior was not read in
  detail.** Only its imports, module-level shape, and its use of
  `PairingSession` were confirmed (793 lines total); its event-emission
  contract to the frontend and its recovery-mode logic were not traced
  line by line.
- **The mobile Dart implementation's own protocol fidelity to NIP-AB was
  not verified.** This node cites its existence and its independence from
  `buzz-core`'s `PairingSession` (already established by the merged
  `architecture-containers-mobile` node), but did not re-derive or compare
  its HKDF/ECDH/SAS logic against `buzz-core/src/pairing/crypto.rs`.
- **No relationship to `#800`/`#801`/`#802`.** Those sibling capability nodes
  were unopened pull requests at the time this node was drafted, so per
  `AGENTS.md` step 9 none of their ids are valid relationship targets yet;
  the first of them to merge is the natural moment to add a `part-of` or
  `references` edge back to or from this node.
