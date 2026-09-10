---
id: layers-authentication-authentication-failure
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
  - statement: "buzz-auth's AuthError enum enumerates every rejection reason a NIP-42 or NIP-98 verification attempt can produce: InvalidSignature, ChallengeMismatch, RelayUrlMismatch, EventExpired, Nip98Invalid(String), Nip98Replay, PubkeyMismatch, InsufficientScope{required, have}, ChannelAccessDenied, and Internal(String). Its own doc comment states variants are designed to be safe to return to callers without leaking internal implementation details."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/error.rs"
  - statement: "verify_nip42_event (NIP-42 WebSocket AUTH verification) returns InvalidSignature if the event kind is not Authentication (kind:22242) or the Schnorr signature fails buzz_core::verify_event; ChallengeMismatch if the event carries no challenge tag or it does not equal the relay-issued challenge; RelayUrlMismatch if the event carries no relay tag or its normalized value does not equal the relay's own normalized URL; and EventExpired if created_at is more than +/-60 seconds from now. These are exactly the identity-establishment checks -- nothing here consults a database."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "verify_nip98_event (NIP-98 HTTP Auth verification, kind:27235) returns Nip98Invalid with a specific inner message for: JSON parse failure, wrong kind, invalid Schnorr signature, created_at outside +/-60 seconds, a missing or mismatched `u` (URL) tag, a missing or mismatched `method` tag, or (when a payload tag and a request body are both present) a SHA-256 payload-hash mismatch. On success it returns only the verified pubkey -- no scopes, no session, no DB lookup."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "buzz-auth's module documentation states as a security invariant that every successful auth path produces an AuthContext bound to the connection with no JWT validation, token management, or IdP runtime dependency -- authentication failure in this system is therefore always a cryptographic or freshness/binding check failing, never a call to an external identity provider timing out or returning an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "On the WebSocket path, handle_auth's Err branch (verify_auth_event failing) sets the connection's AuthState to Failed, increments the buzz_auth_failures_total{reason=\"nip42_invalid\"} metric, and replies OK false with the message \"auth-required: verification failed\" -- the raw AuthError variant and its detail are logged (warn!) but never echoed to the client, consistent with AuthError's own doc comment about not leaking internal detail."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "A connection whose AuthState is already Failed and receives another AUTH message is rejected immediately, without re-running verification, with OK false \"auth-required: authentication already failed\" -- a failed authentication attempt is terminal for that connection's identity, not retried in place."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "On the HTTP path, a NIP-98 verification failure is mapped directly to an HTTP 401 Unauthorized response: crates/buzz-relay/src/api/bridge.rs's Nostr-auth extraction wraps verify_nip98_event's Err in api_error(StatusCode::UNAUTHORIZED, ...), and crates/buzz-relay/src/api/git/transport.rs's git-credential path does the same, returning (StatusCode::UNAUTHORIZED, \"NIP-98 auth failed\") after logging the error server-side with warn!."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The EVENT and COUNT WebSocket handlers each independently read the connection's AuthState before doing any work, and reject with \"auth-required: not authenticated\" when it is not AuthState::Authenticated (an OK-false frame for EVENT, a CLOSED frame for COUNT) -- this is a distinct failure from a verification failure: it is a request arriving on a connection that never completed the AUTH handshake at all, rather than an AUTH event that was rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "AuthState is a three-state enum on the per-connection ConnectionState: Pending{challenge} (challenge sent, awaiting a signed AUTH event), Authenticated(AuthContext) (identity established), and Failed (authentication attempt was rejected) -- there is no fourth state distinguishing 'never attempted' from 'attempted and failed' once an AUTH event has actually been rejected once."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs"
  - statement: "After buzz_auth::AuthService::verify_auth_event succeeds (identity is cryptographically established), handle_auth runs three further gates -- a community ban check (cascading to a NIP-OA-proven owner pubkey), a pubkey-allowlist check, and a relay-membership check -- and a denial from any of these also sets AuthState::Failed and replies OK false, with messages \"blocked: you are banned from this community\", \"auth-required: verification failed\" (allowlist), or \"restricted: not a relay member\" respectively. Each of these three gates fails closed on its own DB error (denies rather than treating the error as a pass), distinct from the ban gate's own internal-error message \"error: internal error checking restriction state\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
  - statement: "Because the ban, allowlist, and relay-membership gates run only after verify_auth_event has already succeeded, and because a denial from any of them lands the connection in the same AuthState::Failed used for a genuine cryptographic verification failure, the relay's connection-level state machine does not distinguish 'identity could not be established' from 'identity was established but access was denied' -- both collapse into AuthState::Failed and both are logged under the same buzz_auth_failures_total counter family (with a different `reason` label). This is a real property of the current implementation, not an assumption -- confirmed by reading the state transitions in handle_auth directly."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/connection.rs"
    confidence: 0.85
  - statement: "crates/buzz-auth/src/nip42.rs's own #[cfg(test)] module verifies each rejection branch directly: wrong_challenge_rejected asserts ChallengeMismatch, expired_event_rejected asserts EventExpired, wrong_relay_rejected asserts RelayUrlMismatch, and wrong_kind_rejected asserts InvalidSignature for a non-Authentication-kind event -- these are the tests that establish, rather than merely assert, that the failure examples given in this node's Examples section actually behave as described."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "Issue #1025's Definition of done requires this document to define the term in one sentence before deeper explanation, state boundaries/non-goals or what the concept must not be confused with, link the concept to related concepts/implementation/verification, and use examples only to clarify -- not to introduce a second canonical concept -- distinct from the generic corpus-node DoD items (one hand-authored document, schema-valid front matter, traceable evidence, links instead of duplication, a check against recorded provenance, a clean validator run) that apply to every corpus task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1025 definition of done"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# Authentication failure

## Definition

**Authentication failure** is the relay's rejection of an attempt to establish
a cryptographically-verified identity for a connection or request. In Buzz,
authentication is always one of two challenge-bound signature checks --
NIP-42 for WebSocket connections (`verify_nip42_event`) or NIP-98 for HTTP
requests (`verify_nip98_event`) -- and a failure is any case where that check
does not pass: an invalid or missing Schnorr signature, a challenge or URL
that does not match what the relay expects, a timestamp outside the +/-60
second freshness window, or (NIP-98 only) a request body whose hash does not
match the signed payload tag. `buzz-auth`'s `AuthError` enum is the closed
list of reasons a verification attempt can fail this way.

**What it is not.** A pubkey that verifies cleanly but is then denied --
because it is banned, not on an allowlist, or not a member of the relay --
has *authenticated successfully*; what follows is an authorization decision,
not an authentication one. See *Boundary against authorization failure*
below: this distinction matters for reasoning about the system even though,
as implemented today, the relay's connection-level state machine does not
keep the two apart (see the INFERENCE evidence entry above).

## Use cases

A reader reaches for this concept when: diagnosing why a client's connection
never reaches `AuthState::Authenticated`; distinguishing a client bug (bad
signature, clock skew, wrong relay URL) from a deliberate server-side denial
(ban, allowlist, membership) when triaging a support report; or auditing
what information the relay is and is not allowed to leak back to a caller
who fails to authenticate (per `AuthError`'s own doc comment: safe to return
without leaking internal detail, and the relay logs the specific
`AuthError` variant server-side while returning only a generic message to
the client).

## Examples

- A client's kind:22242 AUTH event carries the previous connection's
  challenge (perhaps replayed from a cached value) instead of the one the
  relay just issued for this connection. `verify_nip42_event` returns
  `ChallengeMismatch`; the client sees `OK false "auth-required:
  verification failed"`.
- A client's system clock is more than 60 seconds off from the relay's.
  Every AUTH event it signs falls outside the freshness window and
  `verify_nip42_event` returns `EventExpired`, regardless of how correct the
  signature and challenge are.
- A git push carries a NIP-98 event whose `u` tag names a different path
  than the one actually being pushed to (e.g. a stale token reused across
  repositories). `verify_nip98_event` returns `Nip98Invalid("URL mismatch:
  ...")`, and the git HTTP transport responds `401 Unauthorized`.

These illustrate the one concept above; they are not an exhaustive
enumeration of `AuthError`'s variants -- that catalogue already lives in
`crates/buzz-auth/src/error.rs` itself and in the evidence ledger above, and
duplicating it here would be reference-shaped content misplaced in a concept
node (see *Boundary against reference*, `templates/concept.md`).

## Boundary against authorization failure

Authentication asks "is this really the pubkey it claims to be, right now,
for this relay/URL?" Authorization asks "given that it really is this
pubkey, is it allowed to do the thing it's asking to do?" In Buzz, the ban,
pubkey-allowlist, and relay-membership gates in `handle_auth` are
authorization decisions: each runs only *after* `verify_auth_event` has
already succeeded, each consults the database rather than cryptography, and
each can change its answer over time for the *same* pubkey (a ban can be
lifted, a membership can be granted) in a way a signature-verification
failure cannot -- a stale challenge or an out-of-window timestamp is not
"wrong" in a way that later becomes "right" for the same event.

**Where this boundary blurs in the current implementation**, and why that
is named rather than hidden: a denial from any of the three post-verification
gates still sets the connection's `AuthState` to `Failed` -- the same state a
genuine cryptographic verification failure produces -- and is counted under
the same `buzz_auth_failures_total` metric family, distinguished only by its
`reason` label (`nip42_invalid` vs. `banned` vs. `allowlist_denied` vs.
`not_relay_member`). A reader inspecting connection state or that metric
family alone cannot tell identity-establishment failure apart from
access-denial without also reading the `reason` label. Whether the corpus
should therefore have a separate "authorization failure" concept node, given
that the underlying code does not cleanly separate the two, is a question
this task does not resolve -- see *Scope and omissions*.

## Boundary against the WebSocket authentication flow

`architecture-flows-websocket-authentication` (linked above) is the
procedural document: it walks the full handshake step by step, success and
failure alike, including the AUTH_TIMEOUT background task, the ordering of
the ban/allowlist/membership gates, and the client-side `buzz-ws-client`
half of the round trip. This node does not restate that sequence. It exists
to answer a narrower, understanding-oriented question -- *what does it mean
for authentication to fail, and how is that different from being denied
access once authenticated* -- that the flow node, by design, does not stop
to define.

## Related resources

- `architecture-flows-websocket-authentication` -- the full NIP-42 handshake
  procedure, including every failure branch described here.
- `architecture-principles-fail-closed-boundaries` -- the corpus-wide
  fail-closed convention that the ban, allowlist, and relay-membership gates
  each follow on their own DB errors (deny rather than pass).
- `crates/buzz-auth/src/error.rs` -- the `AuthError` enum, the authoritative
  and only list of authentication-failure reasons.
- `crates/buzz-auth/src/nip42.rs`, `crates/buzz-auth/src/nip98.rs` -- the two
  verification functions this concept is defined in terms of, and (in
  `nip42.rs`) the unit tests (`wrong_challenge_rejected`,
  `expired_event_rejected`, `wrong_relay_rejected`, `wrong_kind_rejected`)
  that verify the failure examples above.

## Scope and omissions

**This node covers** what authentication failure means as a concept in
Buzz's relay, the closed set of reasons it can occur (NIP-42 and NIP-98),
how a failure is surfaced to a caller on both the WebSocket and HTTP paths,
and its boundary against authorization failure and against the sibling
procedural flow node.

**It does not cover, and these are gaps rather than silence:**

- The full step-by-step WebSocket handshake, including timing (`AUTH_TIMEOUT`,
  the client library's challenge/OK wait bounds) and the client-side retry
  behavior on failure -- owned by `architecture-flows-websocket-authentication`.
- Whether the current conflation of authentication-failure and
  authorization-failure into one `AuthState::Failed` bucket and one metric
  family (named above) should change, or whether a separate
  "authorization-failure" concept node should exist -- not resolved here;
  this is a genuine open question about the corpus's own coverage, not a
  claim about what the code should do.
- Rate limiting and brute-force protection around repeated authentication
  attempts (`crates/buzz-auth/src/rate_limit.rs` exists but was not read for
  this node) and NIP-98 replay prevention
  (`crates/buzz-auth/src/nip98_replay.rs`) -- both are adjacent but distinct
  concerns (throttling and freshness-window enforcement, not authentication
  failure itself) and were not verified for this node.
- Desktop, mobile, and CLI client-side UX when authentication fails (what a
  human user actually sees) -- out of scope for a relay-side concept node.

**Expected but not verified when this node was written:** whether any
authentication surface beyond NIP-42 (WebSocket) and NIP-98 (HTTP) exists
elsewhere in the codebase (e.g. an admin-specific auth path) was not
exhaustively searched; the two paths cited above were confirmed as the ones
`buzz-auth`'s own module documentation describes.
