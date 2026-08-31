---
id: layers-identity-device-pairing
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "NIP-AB defines a protocol for securely transferring secrets between two devices over standard Nostr relays using QR-code-initiated, end-to-end encrypted channels with visual confirmation, calling the initiating, secret-holding device 'source' and the receiving device 'target'."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "NIP-AB's own Motivation section states it solves 'one-time transfer' (the key moves and the source device is no longer required), distinguishing itself from NIP-46 remote signing, which solves 'ongoing delegation' (the key stays on one device and signs remotely) and requires the signer device online for every operation; the two are described as complementary, and NIP-AB can bootstrap a NIP-46 session as one of its own payload types."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "The NIP-AB overview is: source generates an ephemeral keypair and a 32-byte session secret and encodes them in a QR code; target scans the code and generates its own ephemeral keypair; both devices exchange ephemeral public keys over the pairing relay via kind:24134 events; both derive a shared secret via ECDH and display a Short Authentication String (SAS) for the user to visually confirm; after confirmation source sends the encrypted payload via a kind:24134 event; target decrypts and imports it. All events use ephemeral keypairs discarded after the session, and the relay sees only opaque ciphertext addressed to throwaway public keys."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "kind.rs defines KIND_PAIRING = 24134 in the ephemeral event range (20000-29999, never stored), documented inline as 'NIP-AB: Device pairing event. Ephemeral -- relay may discard after delivery.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "buzz-pair-relay is a purpose-built ephemeral sidecar relay, documented in its own module doc comment as accepting WebSocket connections, matching incoming kind:24134 events against live #p-filtered subscriptions, and forwarding matches to the subscriber, with 'No persistence. No auth. No history.' It MUST bind loopback-only and run behind a reverse proxy per its own Deployment section, and its Security Model section states signature verification against the NIP-01 event ID hash, bounded resources (128 max WebSocket connections, 4 KiB max frame, 120 s TTL), a session cap of at most 6 accepted EVENTs per connection, a +-120 s created_at freshness window, and event-ID deduplication with 300 s expiry."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs"
  - statement: "buzz-pair-relay's observable protocol surface -- kind and tag-shape rejection, duplicate-event handling, signature verification ordering, and single-subscriber delivery -- is exercised by an integration test suite that spins up the relay on a random port and drives it over real WebSocket connections."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/tests/integration.rs"
  - statement: "buzz-relay's NIP-11 document carries an optional pairing_relay_url field, documented as 'Public WebSocket URL of the dedicated NIP-AB device-pairing relay,' populated from the BUZZ_PAIRING_RELAY_URL environment variable read into RelayConfig; this is how a client discovers a community's dedicated buzz-pair-relay instance rather than assuming a fixed address."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "buzz-relay's own event handler also has explicit support for routing kind:24134 alongside other channel-less ephemeral events: events with no channel tag are fanned out through a Redis global pub/sub key (a nil UUID sentinel) rather than through buzz-pair-relay, per an inline comment naming 'NIP-AB pairing kind:24134' as an example of this path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-core's pairing module (crates/buzz-core/src/pairing/) implements the protocol as a session state machine (session.rs: PairingSession, Role::{Source,Target}, and states including Waiting, Confirming, AwaitingConfirmation, Transferring, PayloadExchanged), HKDF-SHA256 derivation primitives for session_id, the SAS input/code, and the transcript hash (crypto.rs), the QR URI codec (qr.rs), and the pairing message/payload types and PairingError enum (types.rs, mod.rs)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/mod.rs"
      - "crates/buzz-core/src/pairing/session.rs"
      - "crates/buzz-core/src/pairing/crypto.rs"
      - "crates/buzz-core/src/pairing/qr.rs"
      - "crates/buzz-core/src/pairing/types.rs"
  - statement: "The SAS is a zero-padded 6-digit decimal code derived as HKDF-SHA256(IKM=ecdh_shared, salt=session_secret, info='nostr-pair-sas-v1') truncated to a big-endian u32 mod 1,000,000, displayed on both devices for the user to visually compare; NIP-AB's own Step 3 states this SAS denial is 'the primary MITM defense' and that a later transcript-hash check is a detection mechanism, not a prevention gate, because source may already have sent the payload before target can react."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
      - "crates/buzz-core/src/pairing/crypto.rs"
  - statement: "The kind:24134 event's content is NIP-44 v2 encrypted JSON carrying a type field of offer, sas-confirm, payload, complete, or abort; buzz-pair-relay independently validates that content decodes as base64, is at least 99 bytes decoded, and begins with the 0x02 NIP-44 v2 version byte, without itself decrypting the ciphertext."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
      - "crates/buzz-pair-relay/src/lib.rs"
  - statement: "A payload event's payload_type is one of nsec (a NIP-49 ncryptsec1 or raw nsec1 private key), bunker (a NIP-46 signer-initiated bunker:// session URI), connect (a NIP-46 client-initiated nostrconnect:// session URI), or custom (application-specific data); buzz-core's PayloadType enum mirrors this set."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
      - "crates/buzz-core/src/pairing/types.rs"
  - statement: "buzz-pairing-cli's buzz-pair binary implements both the source and target roles end-to-end against a live Nostr relay for interop testing, plus a test-vectors subcommand that prints every derived cryptographic value from the NIP-AB spec's fixed test keys; its README states it is 'designed for interop testing and NIP submission, not production use.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-pairing-cli/README.md"
  - statement: "The desktop app's pairing.rs Tauri command module implements both pairing roles over the same buzz-core pairing module: a PairingMode::SendIdentity variant (desktop acts as source) and a PairingMode::RecoverIdentity variant (desktop acts as target)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/pairing.rs"
  - statement: "The mobile app carries its own pairing feature directory (mobile/lib/features/pairing/) with pairing_socket.dart, pairing_qr_scanner, pairing_page and pairing_provider.dart, distinct from the desktop and CLI implementations of the same NIP-AB protocol."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_socket.dart"
      - "mobile/lib/features/pairing/pairing_qr_scanner.dart"
      - "mobile/lib/features/pairing/pairing_page.dart"
  - statement: "NIP-AB's own Limitations section states, in its own terms, that the protocol provides no ongoing security once the payload is transferred, no key-revocation mechanism, no multi-device coordination beyond one pairing session per device, no relay confidentiality (the pairing relay learns timing and approximate frequency even though not content), no post-quantum security, a physical-presence assumption for SAS comparison, a QR-code exposure window of up to 120 seconds, and that it is 'not designed for repeated or automated transfers.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "architecture-context-nostr-network, architecture-containers-mobile and architecture-deployment-multi-relay already document buzz-pair-relay and NIP-AB device pairing at the system-context, mobile-client, and multi-relay-topology altitudes respectively, so this node's own Related resources point to them by relationships[] rather than restating their content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "Sibling identity-layer tasks scope keypair.md (#1111), private-key.md (#1112) and public-key.md (#1113) to the keypair concept itself and identity-recovery.md (#1109) to identity recovery, distinct subjects from this one; device pairing assumes a secret already exists and is live on the source device, and moves it to a second device, rather than defining what the secret is or how a lost one is recovered."
    entry_class: INFERENCE
    evidence:
      - "gh_issue_view(1109, 1111, 1112, 1113, repo='launchpad-26/buzz') -> titles 'task: document layers/identity/identity-recovery.md', 'task: document layers/identity/keypair.md', 'task: document layers/identity/private-key.md', 'task: document layers/identity/public-key.md', each scoped by its own DoD to its own single concept node"
      - "crates/buzz-core/src/pairing/NIP-AB.md"
    confidence: 0.7
  - statement: "None of the sibling layers/identity/* tasks (#1102-#1114) has landed a node on origin/launchpad as of this node's recorded revision, so no layers-identity-* id besides this node's own exists yet as a relationships[] target."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, standards/**; no layers/ directory present"
relationships:
  - type: references
    target: architecture-context-nostr-network
  - type: references
    target: architecture-containers-mobile
  - type: references
    target: architecture-deployment-multi-relay
---

# Device pairing

Device pairing is how a Buzz identity gets onto a second device without ever
putting the raw secret on a wire the community relay — or anyone watching
it — can read. It is Buzz's implementation of NIP-AB, a draft Nostr protocol
for moving a secret between two devices over an untrusted relay.

## Definition

**Device pairing is the identity-layer mechanism that transfers a secret —
an `nsec` private key or a NIP-46 remote-signer session — from a device that
already holds it (the *source*) to a new device (the *target*), over an
ordinary Nostr relay, using a QR-code-initiated, end-to-end encrypted
handshake with a user-verified Short Authentication String (SAS).**

It is scoped to one live session between two devices already in the user's
possession. It is **not**:

- **The private key or keypair itself.** What is being transferred, and how
  it is stored once it arrives, are the identity-layer subjects `keypair`,
  `private-key` and `public-key` name (sibling tasks, unmerged at this node's
  recorded revision) — device pairing moves the secret, it does not define
  it.
- **Identity recovery.** NIP-AB assumes the secret is present and live on
  the source device at the moment of pairing. Recovering a secret that has
  been lost or is not currently accessible on any device is a different
  problem, owned by the `identity-recovery` node.
- **NIP-46 remote signing.** NIP-AB's own Motivation section draws this line
  itself: NIP-46 solves *ongoing delegation* — the key stays on one device
  and signs remotely, requiring that device online for every operation — while
  NIP-AB solves *one-time transfer* — the key (or a NIP-46 session bootstrap)
  moves, and the two devices then operate independently. The protocols are
  complementary: one of NIP-AB's own payload types (`bunker`/`connect`) exists
  specifically to bootstrap a NIP-46 session instead of moving raw key
  material.

## Protocol shape

```mermaid
sequenceDiagram
    participant S as source device
    participant R as pairing relay
    participant T as target device

    Note over S: generates ephemeral keypair<br/>+ 32-byte session secret
    S->>S: encode QR: nostrpair://pubkey?secret=..&relay=..&v=1
    Note over T: scans QR, generates<br/>its own ephemeral keypair
    S->>R: REQ kinds:[24134] #p:[source_ephemeral_pubkey]
    T->>R: REQ kinds:[24134] #p:[target_ephemeral_pubkey]
    T->>R: EVENT kind:24134 "offer" (NIP-44 encrypted)
    R->>S: EVENT "offer"
    Note over S,T: both derive ecdh_shared via ECDH,<br/>then sas_code via HKDF-SHA256
    Note over S,T: user visually compares<br/>SAS on both screens
    S->>R: EVENT kind:24134 "sas-confirm"
    R->>T: EVENT "sas-confirm"
    S->>R: EVENT kind:24134 "payload" (encrypted secret)
    R->>T: EVENT "payload"
    Note over T: decrypts, imports<br/>into secure storage
    T->>R: EVENT kind:24134 "complete" (advisory)
    R->>S: EVENT "complete"
```

Every event on the wire is `kind:24134`, NIP-44-v2-encrypted, and signed by a
throwaway ephemeral keypair discarded at the end of the session — the relay
sees only ciphertext addressed to a public key with no link to any real
identity.

## Background

NIP-AB exists because the alternatives it names in its own Motivation
section are each deficient for the one-time-transfer case: pasting a raw
`nsec` is insecure and unauthenticated in transit; NIP-46 remote signing
requires the signer device online for every operation rather than
transferring the key; a NIP-06 mnemonic is manual, error-prone, and not
universally supported by clients. NIP-AB's SAS step exists specifically to
give the user an out-of-band check against a relay-in-the-middle
substituting its own ephemeral public key for the real peer's.

The spec is versioned (currently only version `1` is defined: secp256k1
ECDH, HKDF-SHA256 key derivation, a 6-digit SAS, and NIP-44 v2 encryption),
and both the QR URI's `v` parameter and the `offer` message's `version`
field carry that version so a future algorithm change does not silently
break an older implementation.

## Where the pairing relay lives

A pairing session needs *some* relay that both ephemeral keypairs can reach,
but that relay does not have to be — and by design should not need to
be — the community's own `buzz-relay`. Buzz ships two ways a `kind:24134`
event can be routed:

1. **`buzz-pair-relay`**, a dedicated, ephemeral, loopback-only sidecar with
   no persistence, no auth and no history of its own, purpose-built for this
   traffic. A community relay can advertise its address to clients via the
   NIP-11 `pairing_relay_url` field, itself sourced from the
   `BUZZ_PAIRING_RELAY_URL` environment variable — so a client discovers the
   dedicated pairing endpoint rather than assuming a fixed address.
2. **`buzz-relay` itself**, whose event handler has explicit support for
   channel-less ephemeral events — `kind:24134` is named directly in its own
   code comment as an example — fanned out through a global Redis pub/sub
   key rather than a per-channel one.

Which of the two a given deployment actually uses is a topology decision,
not a protocol one; `architecture-deployment-multi-relay` covers that
decision in depth and this node does not repeat it.

## Use cases

- **Adding a second device to an already-provisioned identity** — the
  ordinary case: a user with the desktop app installed scans a QR code with
  their phone to bring the same identity onto mobile, without the `nsec`
  ever crossing the community relay in the clear.
- **Bootstrapping a NIP-46 remote-signer session** instead of moving raw key
  material, via the `bunker` or `connect` payload types — the target ends up
  with a signing relationship to the source rather than a copy of the key.
- **Interop testing and NIP-spec verification** — `buzz-pairing-cli`'s
  `source`/`target`/`test-vectors` subcommands exercise the full protocol
  end-to-end against a live relay and print every derived value against the
  spec's own fixed test keys, independent of the desktop or mobile clients.

## Client implementations

Both Buzz clients that hold identities implement NIP-AB against the same
`buzz-core` pairing module rather than each reimplementing the protocol:

- **Desktop** — `commands/pairing.rs` implements both roles: sending an
  identity (source) and recovering one (target). Deeper desktop detail is
  `architecture-containers-desktop`'s to cover, not restated here.
- **Mobile** — a dedicated `pairing/` feature directory (QR scan, pairing
  socket, pairing page) implements the same protocol as its own client.
  `architecture-containers-mobile` documents the mobile pairing surface in
  depth and is linked from this node's front matter rather than repeated.

## Non-goals and limitations

NIP-AB states its own boundary explicitly, and this node inherits it rather
than restating a softer version:

- **No ongoing security.** Once transferred, the secret's security is
  entirely the receiving device's problem from then on.
- **No key revocation.** There is no mechanism to invalidate a completed
  pairing after the fact.
- **No multi-device coordination.** Pairing N devices takes N separate
  sessions; there is no group or fan-out primitive.
- **No relay confidentiality.** The relay — whichever of the two above is in
  use — still observes pairing timing and frequency, even though it cannot
  read the payload.
- **No post-quantum security.** The ECDH exchange and NIP-44 encryption
  layer share the same limitation any secp256k1-based protocol has today.
- **A physical-presence assumption.** SAS verification depends on the user
  comparing two physical screens; it does not defend against an attacker
  with simultaneous physical access to both.
- **A single-use, time-boxed session.** The QR code exposes the session
  secret for up to 120 seconds, and the protocol is not designed for
  repeated or automated transfers.

## Scope and omissions

**This node covers** what device pairing is, the six-step NIP-AB protocol
shape, the two relay paths a `kind:24134` event can take, the `buzz-core`
crypto/session/QR modules that implement it, the desktop, mobile and CLI
client entry points, and the protocol's own stated non-goals.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The private key / keypair concept being transferred | `keypair`, `private-key`, `public-key` (#1111, #1112, #1113 — unmerged at this node's recorded revision) |
| Recovering a secret that is lost or inaccessible on every device | `identity-recovery` (#1109 — unmerged) |
| Full desktop and mobile UI walkthroughs of the pairing flow | `architecture-containers-desktop`, `architecture-containers-mobile` |
| Which relay path (dedicated sidecar vs. `buzz-relay`'s own ephemeral routing) a given deployment topology chooses, and why | `architecture-deployment-multi-relay` |
| `buzz-pair-relay`'s specific hardening tightenings (rate windows, per-connection session caps, dedup TTLs) as implementation detail | Not yet filed as its own corpus task at this revision |
| The NIP-46 protocol itself, beyond NIP-AB's own `bunker`/`connect` bootstrap payload types | Not covered by any corpus node at this revision |

**No `relationships` edge to a sibling `layers/identity` node.** Checked
before deciding that rather than assumed: at this node's recorded revision
`origin/launchpad`'s corpus tree carries no `layers/` directory at all, so
none of `keypair`, `private-key`, `public-key` or `identity-recovery` has an
`id` yet for a `relationships[].target` to name. The boundary against each
is stated in prose above instead, per `standards/linking.md`'s guidance for
a real connection that does not yet resolve — the first of those siblings to
land is the moment to add the edge.

**Expected but not verified when this node was written:**

- **Which relay path — `buzz-pair-relay` or `buzz-relay`'s own ephemeral
  routing — any actual deployed community configures** was not checked
  against a live `BUZZ_PAIRING_RELAY_URL` setting; both paths are confirmed
  to exist in code, not which one a given community runs.
- **The Tamarin formal model referenced by the spec (`NIP-AB.spthy`)** was
  named in the spec's own text but not opened or run in this pass; this node
  makes no claim about what it proves.
- **Whether `buzz-pairing-cli` and the desktop/mobile clients stay
  byte-for-byte interoperable over time** was not independently verified
  beyond both implementing against the same `buzz-core` pairing module —
  sharing the module is evidence toward interoperability, not proof of it.
