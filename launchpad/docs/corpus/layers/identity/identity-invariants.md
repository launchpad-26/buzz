---
id: layers-identity-identity-invariants
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
  - statement: "verify_event checks that an event's id is the correct hash of its (pubkey, created_at, kind, tags, content) tuple, and that its signature is a valid Schnorr signature over that id; either check failing returns an error (InvalidId or InvalidSignature) and the function never returns Ok for a mismatched pair."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs:11-32"
  - statement: "verify_event's own unit tests construct a validly signed event, tamper with its content while leaving the original id and signature untouched, and confirm verify_event rejects it as InvalidId; a second test tampers with the signature bytes directly on an otherwise-valid event and confirms verify_event still returns an error -- the id/signature binding is test-enforced, not merely asserted in a comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs:34-71"
  - statement: "buzz-relay's event-ingestion code calls verify_event via spawn_blocking at three call sites -- the ephemeral-event path, the agent-observer-event path, and the real persisted-event path in ingest_event_inner -- and in all three, a verification failure sends the client OK false \"invalid: {e}\" (or an internal-error message if the verification task itself panics) and returns immediately, before any storage, fan-out, or further processing of the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:805"
      - "crates/buzz-relay/src/handlers/event.rs:960"
      - "crates/buzz-relay/src/handlers/ingest.rs:1990"
  - statement: "verify_nip42_event, the check that authenticates a WebSocket connection via NIP-42, checks the event's kind first and only then calls buzz_core::verify_event (inside the same function body), proceeding to the challenge, relay-URL, and timestamp checks once the event's id and signature both pass; a wrong-kind AUTH event is rejected before signature verification ever runs, and a forged or malformed AUTH event of the correct kind never reaches those later challenge/relay/timestamp checks."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:47-86"
  - statement: "verify_nip42_event's unit tests separately cover a wrong challenge, a non-Authentication event kind, an expired timestamp (created_at more than 60 seconds from now), and a mismatched relay URL, each asserted to return the specific corresponding AuthError variant -- the NIP-42 checks beyond signature/id are also test-enforced, not merely documented."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs:88-183"
  - statement: "AuthContext, the struct returned by a successful NIP-42 or NIP-98 verification, carries pubkey: nostr::PublicKey as the identity bound to that authenticated context. There is no separate account identifier anywhere in the struct -- the pubkey itself is the identity a connection authenticates as."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:63-79"
  - statement: "AuthService::verify_auth_event's public signature takes an already-signed nostr::Event, an expected challenge string, and a relay URL -- never a private key or any key material. Nothing in buzz-auth's public API accepts a private key from a caller; a connection can only be authenticated by presenting a signature over a challenge, never by presenting key material directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs:118-124"
  - statement: "handle_auth, the relay's NIP-42 AUTH message handler, reads the connection's current AuthState before verifying anything new; if it is already AuthState::Authenticated, the handler sends an OK-false \"already authenticated\" response and returns without calling verify_auth_event at all. A second AUTH message on an already-authenticated connection cannot rebind that connection to a different pubkey -- the code path that would perform a rebind is never reached."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:43-56"
  - statement: "Grepping crates/buzz-test-client/tests/ and crates/buzz-relay/src/ for \"already authenticated\" and for AuthState::Authenticated usage in test code returns no matching test that exercises the already-authenticated rejection path -- only production call sites (connection.rs, auth.rs, count.rs, event.rs, req.rs) use the variant. This sub-invariant is held by the handler's structure (the early-return match arm in handle_auth), not backed by a test that would fail if that early return were removed."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='already authenticated|AuthState::Authenticated', path='crates/buzz-test-client/tests/;crates/buzz-relay/src/') -> matches only in crates/buzz-relay/src/{connection.rs,nip11.rs,handlers/auth.rs,handlers/count.rs,handlers/event.rs,handlers/req.rs}, none of which are test files; verified against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The desktop client's private-key storage module states in its own module doc that private keys (nsecs) are held in a single JSON blob in the OS keyring (keyring crate / macOS SecKeychain), and explicitly keeps that store off any env-read path so a private key is never exposed through the same environment-variable resolution used for agent credentials."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs:1-21"
  - statement: "That the relay's authentication surface (buzz-auth's public API, plus both relay auth handlers read this session) contains no code path accepting a raw private key was established by reading buzz-auth's public function signatures and the NIP-42/NIP-98 handlers in buzz-relay, not by an exhaustive search of every crate in the workspace for a private-key-accepting function. A private-key-accepting path elsewhere (e.g. a dev/test-only helper gated behind a feature flag) cannot be fully ruled out from this evidence alone."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/lib.rs:118-124"
      - "crates/buzz-relay/src/handlers/auth.rs:43-56"
    confidence: 0.7
  - statement: "Issue #1108's Definition of Done requires that the node state the invariant as one unambiguous property, explain its scope and the states/operations it applies to, name enforcement points and observable failure behavior, and link at least one verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1108 definition of done"
---

# Identity is keypair control, proven per event: invariant

A Buzz identity is exactly a secp256k1 keypair. No relay-side mechanism attributes
an event, a connection, or an authenticated context to a given pubkey without a
Nostr event bearing that exact pubkey and a valid Schnorr signature over that
event's id -- there is no server-side account record, password, or session token
that establishes identity independently of a signature.

## Scope

This invariant binds every Nostr event the relay ingests: `verify_event` runs on
every event passed to the relay's event-ingestion handlers, with no kind-based
exception, so the id/signature check applies uniformly whether the event is a
channel message, a reaction, a git-repo announcement, or any other kind.

It binds NIP-42 AUTH events (kind:22242) specifically at connection-authentication
time: a WebSocket connection has no identity until a valid AUTH event is verified,
and once verified, `AuthContext.pubkey` is the identity for that connection's
remaining lifetime. That binding is a per-connection, externally-visible state
change (per the industry model this template adapts, Design by Contract's
"invariant holds at every externally visible moment" -- not necessarily every
intermediate instruction): a connection is momentarily un-identified between
socket-open and a successful AUTH, and once identified, a second AUTH message
cannot change which pubkey the connection is bound to. It also binds NIP-98 HTTP
Auth events (kind:27235) at request-authentication time, verified the same way
(kind check first, then signature, then the remaining claim checks), though
that path was not independently re-read this session beyond `AuthMethod::Nip98`'s
existence in `buzz-auth`.

It does not bind which actions an already-identified pubkey is authorized to
perform inside a community or channel -- that is a separate authorization layer
(scopes, relay membership, moderation bans) described in *Boundary* below.

## Enforcement today

Naming the weakest true tier honestly, per facet, rather than rounding up:

- **Event id/signature binding (`verify_event`): test-enforced.** A test tampers
  with content while leaving id/signature alone and confirms rejection; a second
  test tampers with the signature and confirms rejection. Both call the real
  function, not a mock.
- **NIP-42 challenge/relay/timestamp checks (`verify_nip42_event`): test-enforced.**
  Four separate tests each drive one failure mode (wrong challenge, wrong kind,
  expired timestamp, wrong relay) and assert the specific `AuthError` variant
  returned.
- **No-rebind-on-reauth (`handle_auth`'s early return on `AuthState::Authenticated`):
  structurally enforced, but untested.** The code's shape makes a rebind
  unreachable today -- the match arm returns before `verify_auth_event` is ever
  called -- but nothing would fail if a future edit removed that early return and
  let a second AUTH silently rebind the connection. No test in this repository
  exercises this path.
- **Private key never crosses the wire to the relay: convention-only, by protocol
  design, not by an explicit runtime check.** `AuthService`'s public API and both
  relay auth handlers only ever accept an already-signed `nostr::Event`; there is
  no parameter, field, or code path in the surface read this session that accepts
  raw key material. Nothing enforces that a future addition to the protocol
  couldn't introduce one -- this is the shape of the API today, not a compiler or
  test guarantee that it can never change.

## Consequence of violation

A relay-ingested event with a mismatched id, an invalid signature, or (for AUTH)
a wrong challenge, kind, relay, or expired timestamp is rejected before it is
stored, broadcast, or acted on: the client receives `["OK", <event_id>, false,
"invalid: <reason>"]` and the handler returns immediately. A failed AUTH sets
`AuthState::Failed`, which blocks that connection from any authenticated
operation for the remainder of its lifetime (a fresh connection must be opened to
retry). Nothing downstream of `verify_event` or `verify_nip42_event` ever
observes an event or an `AuthContext` whose pubkey was not proven by a valid
signature.

## Boundary

This node does not describe:

- **Authorization once identity is established.** Whether an authenticated pubkey
  may act inside a given community or channel -- relay membership, per-channel
  scopes, the pubkey allowlist gate, and moderation bans (`moderation_restriction_state`)
  -- is a separate layer, evaluated in `handle_auth` only after this invariant's
  checks already passed. No corpus node for that layer exists yet to `references`.
- **NIP-OA owner-delegation.** An agent's cryptographically-proven owner pubkey
  (extracted from a self-proving `auth` tag) is a related but distinct mechanism
  layered on top of NIP-42 identity, not a restatement of it.
- **Private-key custody's full lifecycle** (generation, OS-keyring storage,
  migration between backends, encrypted backup/recovery via `key_backup.rs`).
  This node cites the client-custody boundary as one supporting fact; it does not
  document that subsystem's own contract.
- **A corpus document's own citation/authoring rules.** `node.schema.json` and
  `launchpad/docs/corpus/AGENTS.md` govern that, unconditionally, for this node
  as for every other.

## Relationships

Declared: none. Checked against `origin/launchpad`'s corpus tree at the recorded
revision: `architecture/principles/signed-events.md` and
`architecture/flows/websocket-authentication.md` are both plausible neighbors by
subject, but per `templates/invariant.md`'s own stated relationship direction, an
interface- or flow-shaped node is expected to `references` *this* invariant node
once it exists as a target, not the other way around -- this node does not
originate that edge. No node currently merged on `origin/launchpad` documents
per-channel authorization, NIP-OA delegation, or key custody, so no `references`
or `depends-on` target exists for those boundary items either. The first sibling
node covering one of them is the natural moment to add the edge, from that node
back to this one.

## Scope and omissions

**This node covers** the core identity invariant for Buzz: a pubkey is the whole
of an identity, proven per event by a valid Schnorr signature, and never
established or rebound by any relay-side mechanism other than a freshly verified
signature -- including how that plays out for general event ingestion, for NIP-42
connection binding, and for private-key custody staying client-side.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Authorization / access-control once a pubkey is identified (scopes, relay membership, channel access, moderation bans) | No corpus node exists yet |
| NIP-OA owner-delegation's own contract | No corpus node exists yet |
| Private-key custody's full lifecycle (generation, keyring backend selection, migration, backup/recovery) | No corpus node exists yet |
| NIP-98 HTTP Auth's full contract beyond its existence as `AuthMethod::Nip98` | No corpus node exists yet |
| Mobile's identity handling and the NIP-AB device-pairing flow (`buzz-pair-relay`, `buzz-pairing-cli`) | No corpus node exists yet |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether any dev/test-only or feature-gated code path in the workspace accepts
  a raw private key was not exhaustively checked.** The claim that the relay's
  authentication surface never accepts key material rests on reading `buzz-auth`'s
  public API and the two relay auth handlers, not a workspace-wide search; it is
  recorded as an `INFERENCE` at confidence 0.7 above, not a `FACT`.
- **NIP-98 HTTP Auth's own verification function (`buzz-auth/src/nip98.rs`) was
  not independently re-read this session** beyond confirming `AuthMethod::Nip98`
  exists; this node's claims about "kind check first, then signature, then the
  remaining claim checks" for NIP-98 are extrapolated from the NIP-42 pattern
  (`verify_nip42_event` checking the event's kind before calling
  `buzz_core::verify_event`), not verified against NIP-98's own code.
- **No-rebind-on-reauth has no test today**, named honestly in *Enforcement
  today* above rather than rounded up to "enforced."
