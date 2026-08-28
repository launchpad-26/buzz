---
id: architecture-principles-signed-events
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "verify_event checks that an event's id is the correct hash of its own fields and that its signature is a valid Schnorr signature, returning VerificationError::InvalidId or VerificationError::InvalidSignature when either check fails."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-core/src/error.rs"
  - statement: "The relay calls verify_event at three points: ingest_event_inner for persistent events (the seam shared by the WebSocket EVENT frame and the HTTP POST /events bridge), handle_ephemeral_event for WS-only ephemeral kinds 20000-29999, and handle_agent_observer_event for kind:24200 agent observer frames."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "submit_event_authed, the handler behind POST /events, calls the same ingest_event function the WebSocket EVENT handler calls, passing IngestAuth::Http instead of IngestAuth::Nip42."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "verify_event's own doc comment states it is CPU-bound and must be called via tokio::task::spawn_blocking in async contexts; all three call sites wrap it in spawn_blocking."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "On rejection the relay sends a NIP-01 OK message with accepted=false and a message prefixed 'invalid: ' built from the VerificationError's Display string ('invalid event id: computed X, got Y' or 'invalid schnorr signature')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-core/src/error.rs"
  - statement: "A spawn_blocking panic during verification is routed to a distinct branch (IngestError::Internal / a generic 'error: internal error' OK message) rather than the 'invalid:' rejection branch, so an OK-false message beginning 'invalid:' specifically means verification ran to completion and rejected the event, not that verification could not run."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-core carries two unit tests exercising this directly: verification::tests::rejects_tampered_id and verification::tests::rejects_tampered_signature, each mutating a signed event's JSON and asserting verify_event returns the matching VerificationError variant. event::tests::tampered_signature_fails_verify asserts the same at the nostr::Event method level. No test found under crates/buzz-test-client or crates/buzz-relay exercises rejection of a tampered event through the WebSocket or HTTP wire protocol."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-core/src/event.rs"
  - statement: "kind:22242 (NIP-42 AUTH) cannot be submitted through the EVENT/ingest path at all -- both handle_event and ingest_event_inner reject it outright before any verify_event call on that path -- so buzz-auth's own AUTH-event signature check (verify_nip42_event) is a separate mechanism, not a fourth enforcement point of this invariant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "kind:44100 and kind:44101 (membership add/removed notifications) are rejected by ingest_event_inner if a client attempts to submit them via EVENT, with the rejection message stating they are relay-signed only, so they are produced by a different, relay-internal code path than the one this invariant governs for client-submitted events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/kind.rs"
  - statement: "StoredEvent carries its own verified: bool field, defaulting to false in StoredEvent::new and set explicitly via StoredEvent::with_received_at at various call sites, but no call site anywhere under crates/ reads it through is_verified() outside verification.rs's own module -- the field is not consulted by anything downstream of storage at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/event.rs"
  - statement: "The check that event.pubkey equals the authenticated NIP-42 identity (with a carved-out exception for kind:1059 gift wrap) runs immediately before ephemeral/persistent dispatch in handle_event, as a check distinct from verify_event -- it constrains who may submit an event, not whether the event's own signature is valid."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "verify_event's verify_signature call takes only the event itself, with no separate expected-pubkey argument, so it checks the signature against the pubkey embedded in the event -- meaning a correctly self-signed event from a keypair other than the authenticated session's would pass signature verification and be rejected only by the separate identity-binding check described above, not by verify_event."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/verification.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
    confidence: 0.8
---

# Principle: every accepted event carries a valid signature over its own id

## The invariant

The relay **MUST NOT** accept, store, or fan out any client-submitted event whose `id`
is not the correct hash of its own fields, or whose `sig` is not a valid signature over
that `id` under the key named in its own `pubkey` field. An event failing either check
**MUST** be rejected with an explicit negative acknowledgement; it must never be
silently dropped or partially processed.

This is one property with two mechanical parts (id-hash correctness and signature
validity), checked together by a single function, `verify_event`
(`crates/buzz-core/src/verification.rs`). Both parts gate the same accept/reject
decision, which is why this document treats them as one invariant rather than two.

## Scope

**Applies to:** every event a client submits through the relay's client-facing
ingestion surface -- the WebSocket `EVENT` frame and the HTTP `POST /events` bridge --
across all three kind classes the relay routes it through: persistent events (via
`ingest_event_inner`), WS-only ephemeral events in the 20000-29999 range (via
`handle_ephemeral_event`), and kind:24200 agent observer frames (via
`handle_agent_observer_event`). All three call the same `verify_event` function.

**Does not apply to** (deliberately, at this revision):

- **kind:22242 (NIP-42 `AUTH`)**, which cannot be submitted through this surface at
  all -- it is rejected before any `verify_event` call reachable from `EVENT` -- and is
  governed by `buzz-auth`'s own `verify_nip42_event` instead. That mechanism is a
  sibling to this invariant, not a case of it.
- **kind:44100 / kind:44101 (membership add/removed notifications)**, which
  `ingest_event_inner` rejects outright if a client tries to submit them, because they
  are relay-signed and produced by a different, relay-internal code path.
- **Identity binding** -- whether `event.pubkey` matches the authenticated NIP-42
  session (with the documented gift-wrap exception) -- is a separate check in
  `handle_event`, run next to this invariant's enforcement points but not part of it.
  A correctly self-signed event can satisfy this invariant and still be rejected by that
  other check; see the identity-binding evidence entry above.

## Enforcement points and observable failure behavior

| Path | Function | File |
|---|---|---|
| Persistent events, WS and HTTP alike | `ingest_event_inner` | `crates/buzz-relay/src/handlers/ingest.rs` |
| Ephemeral events (kinds 20000-29999) | `handle_ephemeral_event` | `crates/buzz-relay/src/handlers/event.rs` |
| Agent observer frames (kind:24200) | `handle_agent_observer_event` | `crates/buzz-relay/src/handlers/event.rs` |

All three wrap `verify_event` in `tokio::task::spawn_blocking`, per the function's own
doc comment, because Schnorr verification is CPU-bound and must not run inline on an
async task.

**Observable failure.** On the invariant's own rejection path (not a panic), the caller
receives a standard NIP-01 `OK` message: `accepted = false`, with a human-readable
message prefixed `"invalid: "` and suffixed with the `VerificationError`'s `Display`
text -- `"invalid event id: computed <hash>, got <hash>"` for a bad id, or `"invalid
schnorr signature"` for a bad signature. This is the same `OK`-message channel every
other rejection reason in the relay uses; nothing distinguishes a signature failure from
any other `invalid:`-prefixed rejection except the message text itself. A
`spawn_blocking` panic during verification is routed to a separate branch (a generic
`"error: internal error"` message) rather than this one -- so an `invalid:`-prefixed `OK
false` specifically means verification ran and rejected the event, not that it could not
run.

## Verification

**Unit-level, confirmed at this revision:**

- `verification::tests::rejects_tampered_id` and
  `verification::tests::rejects_tampered_signature` in
  `crates/buzz-core/src/verification.rs` each mutate a signed event's JSON (content or
  `sig`) and assert `verify_event` returns the matching error variant.
- `event::tests::tampered_signature_fails_verify` in `crates/buzz-core/src/event.rs`
  asserts the same at the underlying `nostr::Event::verify_signature` level.

Run with `cargo test -p buzz-core`.

**Verification recorded as missing, not merely unmentioned:** no test under
`crates/buzz-test-client` or `crates/buzz-relay` was found exercising rejection of a
tampered event through the actual WebSocket or HTTP wire protocol -- i.e. nothing
confirms the `invalid:` `OK`-message shape end-to-end, only that the underlying function
returns the right `Result`. This gap was checked by searching `crates/` for the
`VerificationError` display strings and finding no match outside `buzz-core`'s own unit
tests and the handler code itself. Closing it is out of scope for this node -- the
originating task (launchpad-26/buzz#697) is documentation-only and does not own adding
new tests -- and it is not tracked by an existing issue at this revision.

## Scope and omissions

- **`StoredEvent.verified`** is a `bool` field on the relay's in-memory event wrapper,
  defaulting to `false` and set at construction time in various call sites, but no
  non-test call site anywhere under `crates/` reads it through `is_verified()` at this
  revision. It does not gate any decision this invariant depends on, and this document
  does not claim it will stay that way.
- **The `nostr` crate's own `verify_id`/`verify_signature` implementations** (NIP-01
  hash construction, BIP-340 Schnorr verification) are treated as a trusted external
  dependency here. This node describes how Buzz calls and enforces that check, not the
  cryptographic implementation itself, which was not opened for this node.
- **Identity binding and AUTH/membership-notification signing** are named above as
  adjacent, out-of-scope mechanisms rather than described in full; each is a candidate
  for its own corpus node.
