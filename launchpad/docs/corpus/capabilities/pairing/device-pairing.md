---
id: capabilities-pairing-device-pairing
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "NIP-AB (Device Pairing) defines a protocol for securely transferring a secret between two devices over standard Nostr relays using QR-code-initiated, end-to-end encrypted channels with visual (SAS) confirmation; the spec header marks the NIP `draft` and `optional`, and a `source`/`target` terminology (the device holding the secret vs. the device receiving it) is used throughout."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:1-9"
      - "crates/buzz-core/src/pairing/NIP-AB.md:51-68"
  - statement: "An independent security audit of NIP-AB is planned but not yet completed; until it is, the spec itself instructs implementations in high-security contexts to treat the NIP as draft and conduct their own review."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:607-609"
  - statement: "NIP-AB explicitly solves one-time key transfer, is complementary to NIP-46 remote signing (which it can bootstrap via a `bunker`/`connect` payload), and states its own limitations: no ongoing security once transferred, no key revocation, no multi-device coordination in one session, no post-quantum security, and a single-use QR-code window of up to 120 seconds."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:39-49"
      - "crates/buzz-core/src/pairing/NIP-AB.md:70-83"
  - statement: "buzz-core/src/kind.rs registers KIND_PAIRING = 24134 with the doc comment 'NIP-AB: Device pairing event. Ephemeral — relay may discard after delivery.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:464-465"
  - statement: "buzz-core::pairing implements the protocol's cryptographic and state-machine primitives across four modules — crypto (HKDF derivations), qr (QR URI encode/decode), session (PairingSession, Role, SessionState) and types (PairingMessage, PayloadType, AbortReason) — and the crate's own module doc names HKDF-SHA256, ECDH, NIP-44 v2 and SAS as the four building blocks used."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/mod.rs:1-30"
  - statement: "buzz-pair-relay is described in its own crate manifest as 'Ephemeral sidecar relay for NIP-AB device pairing handshakes', and its module doc states it binds loopback-only and persists nothing (events exist only in-flight between matched pub/sub)."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/Cargo.toml"
      - "crates/buzz-pair-relay/src/lib.rs:5-22"
  - statement: "buzz-pairing-cli (binary name buzz-pair) is an interop-testing CLI for the NIP-AB protocol with three subcommands — source (holds and offers the secret), target (receives it), and test-vectors (prints the spec's fixed derivation values) — documented as built for interop testing and NIP submission, not production use."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/README.md"
  - statement: "The desktop app implements both pairing directions as Tauri commands: PairingMode::SendIdentity (desktop is NIP-AB source, exporting the identity to another device) and PairingMode::RecoverIdentity (desktop is NIP-AB target, importing an identity from another device), with start_identity_recovery_pairing exposed to the frontend via desktop/src/shared/api/tauriPairing.ts."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/pairing.rs:37-39"
      - "desktop/src-tauri/src/commands/pairing.rs:96"
      - "desktop/src-tauri/src/commands/pairing.rs:107"
      - "desktop/src/shared/api/tauriPairing.ts:1-5"
  - statement: "Two desktop UI surfaces exercise the two pairing directions: desktop/src/features/settings/ui/MobilePairingCard.tsx (Settings — send this desktop's identity to a mobile device, displaying a QR code and SAS confirmation) and desktop/src/features/onboarding/ui/IdentityRecoveryPairing.tsx (onboarding — recover an identity from another device, also QR + SAS)."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/MobilePairingCard.tsx"
      - "desktop/src/features/onboarding/ui/IdentityRecoveryPairing.tsx"
  - statement: "The mobile app implements the target side of NIP-AB pairing under mobile/lib/features/pairing/ (10 Dart source files including pairing_page.dart, pairing_socket.dart, pairing_qr_scanner.dart, pairing_crypto.dart, pairing_provider.dart) with 4 corresponding widget/unit test files under mobile/test/features/pairing/."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_socket.dart"
      - "mobile/lib/features/pairing/pairing_page.dart"
      - "mobile/test/features/pairing/pairing_socket_test.dart"
      - "mobile/test/features/pairing/pairing_page_test.dart"
  - statement: "buzz-core's pairing module carries 71 #[test]/#[tokio::test]-annotated test functions across its four source files, and buzz-pair-relay has a dedicated integration.rs test file, indicating the capability's cryptographic core and sidecar relay are both under automated test, independent of whether every test currently passes."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/crypto.rs"
      - "crates/buzz-core/src/pairing/session.rs"
      - "crates/buzz-core/src/pairing/qr.rs"
      - "crates/buzz-core/src/pairing/types.rs"
      - "crates/buzz-pair-relay/tests/integration.rs"
  - statement: "Neither VISION.md nor VISION_PROJECTS.md's own 'Capability | Status' table lists device pairing as a named row; VISION.md's product-surface table instead marks the mobile client overall as 🚧 'in active development', listing 'pairing' as one of its features rather than giving device pairing its own maturity marker."
    entry_class: FACT
    evidence:
      - "VISION.md:232"
      - "VISION_PROJECTS.md:247-259"
  - statement: "Three corpus nodes already merged to origin/launchpad describe pieces of this capability from their own architectural surface: architecture-context-nostr-network (the context-level diagram naming buzz-pair-relay and NIP-AB kind:24134 traffic to a 'device-pairing peer'), architecture-containers-mobile (the mobile pairing feature's PairingSocket and QR scanner), and architecture-deployment-multi-relay (buzz-pair-relay's optional Kubernetes Deployment, pairingRelay.* in the Helm chart)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "At the recorded revision, no corpus node of type interfaces-events documents buzz-pairing-cli's subcommands or the desktop Tauri pairing command surface (start_pairing, confirm_pairing_sas, cancel_pairing, start_identity_recovery_pairing), and no corpus node of type capabilities existed anywhere under launchpad/docs/corpus/ prior to this one -- confirmed by listing the corpus tree at origin/launchpad and finding no capabilities/ directory and no interface-shaped node naming these commands."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no capabilities/ directory; no node whose body names start_pairing, confirm_pairing_sas, cancel_pairing or start_identity_recovery_pairing, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Sibling tasks #801 (buzz-pairing-cli), #802 (buzz-pair-relay) and #803 (pairing session/state-machine) are separate, not-yet-drafted document tasks under the same parent Feature #613, scoped to document individual pairing components rather than the overall capability this node covers."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#800 task body (batch dispatch context naming #801/#802/#803 as distinct siblings)"
---

# Device pairing: capability

Device pairing lets a user move their Nostr identity — or bootstrap a NIP-46
remote-signer session — from one device to a second device (for example,
desktop to mobile) without ever trusting the relay that carries the pairing
traffic. The user scans a QR code shown on the device that holds the secret,
confirms a short 6-digit code that appears on both screens, and the secret
(an `nsec`, or a `bunker://`/`nostrconnect://` signer session) arrives
end-to-end encrypted on the new device. Buzz implements this on top of
NIP-AB, an in-repo Nostr Improvement Proposal draft (`crates/buzz-core/src/pairing/NIP-AB.md`),
so "device pairing" here means specifically the NIP-AB QR + SAS handshake,
not a generic pairing concept.

## Maturity

**Implementation: shipped across every client surface.** The protocol's
cryptographic core (HKDF derivations, session state machine, QR encode/decode)
lives in `buzz-core::pairing` with 71 test functions; a dedicated ephemeral
sidecar relay (`buzz-pair-relay`) routes the handshake with its own
integration test; an interop CLI (`buzz-pairing-cli`, binary `buzz-pair`)
exercises both protocol roles end-to-end for spec conformance testing; the
desktop app wires both pairing directions into real UI (`MobilePairingCard.tsx`
to send this desktop's identity to a phone, `IdentityRecoveryPairing.tsx` to
recover an identity from another device during onboarding); and the mobile
app implements the receiving side under `mobile/lib/features/pairing/` with
its own test suite. See the evidence ledger for each citation.

**Protocol: still a draft NIP awaiting audit.** NIP-AB's own document header
marks it `draft` `optional`, and its Audit section states that an independent
security audit is planned but not yet completed, instructing high-security
implementations to conduct their own review in the meantime. Device pairing
is therefore best described as **shipped implementation, unaudited draft
protocol** — the two halves of "maturity" a single label would blur.

Neither VISION.md nor VISION_PROJECTS.md's "Capability | Status" table gives
device pairing its own status row; the closest is VISION.md marking the
mobile client overall 🚧 "in active development" with pairing named as one
of its features, which is a statement about the mobile client, not about
this capability specifically.

## Boundary

This node does not describe:

- **How the capability is built.** The cryptographic derivations, the
  ephemeral-key session state machine, and `buzz-pair-relay`'s own
  loopback-only, no-persistence design are architecture/implementation
  detail, already partly covered from other angles by
  `architecture-context-nostr-network` and `architecture-deployment-multi-relay`
  (see Relationships). No architecture-family (component/container/context)
  node yet exists dedicated to pairing's own internals; that gap is named
  below, not filled here.
- **The interface(s) the capability is exposed through.** `buzz-pairing-cli`'s
  three subcommands and the desktop Tauri command surface
  (`start_pairing`, `confirm_pairing_sas`, `cancel_pairing`,
  `start_identity_recovery_pairing`) are boundary contracts an
  `interfaces-events` node would document. None exists yet at the recorded
  revision — see Scope and omissions.
- **The step-by-step flow through this capability.** The exact sequence a
  user or agent walks through — display QR, scan, compare SAS, confirm,
  receive, import — is flow-node territory (a `flow`-shaped node, not yet
  drafted anywhere in this corpus).
- **How the running system is operated.** Deploying and monitoring
  `buzz-pair-relay` in Kubernetes is `architecture-deployment-multi-relay`'s
  territory, referenced below, not restated here.
- **The NIP-AB protocol specification itself.** Every cryptographic detail —
  HKDF labels, the SAS derivation, the Tamarin-proved security lemmas — lives
  in `crates/buzz-core/src/pairing/NIP-AB.md` and is cited here as evidence,
  never reproduced.

## Relationships

- references: architecture-context-nostr-network
- references: architecture-containers-mobile
- references: architecture-deployment-multi-relay

`relationships.schema.json`'s `references` directionality — "source cites
target as supporting context; no ownership or currency dependency implied" —
fits all three: this capability node stays true even as the context diagram,
the mobile container's internals, or the pairing-relay's deployment topology
are each refactored independently underneath it. All three targets were
confirmed present in `origin/launchpad`'s corpus tree at the recorded
revision (see the evidence ledger's `git_ls_tree` entry). No `implements`,
`depends-on` or `part-of` edge is declared: no broader capability or
higher-level policy node exists yet for this one to sit under.

## Scope and omissions

**This node covers** what the device-pairing capability is for a product
stakeholder (moving or bootstrapping a Nostr identity to a second device via
QR + SAS confirmation), its maturity split between a shipped, tested
implementation and an unaudited draft protocol, its boundary against
architecture/interface/flow/operations neighbors, and its relationships to
the three existing corpus nodes that already describe pieces of it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The cryptographic protocol specification itself (HKDF derivations, SAS math, Tamarin proofs) | `crates/buzz-core/src/pairing/NIP-AB.md`, cited as evidence |
| `buzz-pairing-cli`'s command interface | issue #801 (not yet drafted) |
| `buzz-pair-relay`'s own architecture/deployment detail beyond what `architecture-deployment-multi-relay` already states | issue #802 (not yet drafted) |
| The pairing session/state-machine's internal design | issue #803 (not yet drafted) |
| The step-by-step interaction flow through pairing | a future `flow`-type node (none drafted in this corpus yet) |
| An `interfaces-events` node for the CLI/Tauri command surface | not yet drafted anywhere in this corpus |
| Whether the NIP-AB audit mentioned in the protocol doc has since occurred | not tracked by this node; check `crates/buzz-core/src/pairing/NIP-AB.md`'s own Audit section at current `HEAD` |

**Expected but not verified when this node was written:**
- **Whether the 71 test functions in `buzz-core::pairing` and the
  `buzz-pair-relay` integration test currently pass.** Their presence was
  confirmed by counting `#[test]`/`#[tokio::test]` annotations and locating
  the integration test file; this node does not claim a green test run, only
  that automated tests exist and cover this surface.
- **Whether the NIP-AB security audit named as "planned" in the spec's own
  Audit section has since started or completed.** Not investigated beyond
  reading that one section.
- **Whether the desktop or mobile pairing UI has been exercised end-to-end
  against a live `buzz-pair-relay` for this node.** Evidence here is
  static-code and test-file presence, not a runtime demonstration.
