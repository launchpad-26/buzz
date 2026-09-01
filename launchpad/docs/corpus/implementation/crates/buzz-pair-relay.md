---
id: implementation-crates-buzz-pair-relay
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-pair-relay's Cargo.toml describes it as 'Ephemeral sidecar relay for NIP-AB device pairing handshakes', ships a library (buzz_pair_relay) and a binary (buzz-pair-relay), depends on tokio/tokio-tungstenite/hyper/hyper-util/http-body-util for its own minimal HTTP+WebSocket server and secp256k1/sha2 for Schnorr signature verification, and declares no dependency on buzz-core or any other Buzz crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/Cargo.toml"
  - statement: "lib.rs's module doc states the crate 'Accepts WebSocket connections, matches incoming kind:24134 events against live #p-filtered subscriptions, and forwards matches to the subscriber. No persistence. No auth. No history,' and separately states it 'binds loopback only' and MUST run behind a reverse proxy."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:1-16"
  - statement: "The NIP-AB device pairing specification this crate realizes lives at crates/buzz-core/src/pairing/NIP-AB.md, not at docs/nips/NIP-AB.md, which does not exist anywhere in this repository (docs/nips/ contains NIP-AA through NIP-WP but no NIP-AB)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "NIP-AB.md defines the 'pairing relay' role narrowly: 'Any NIP-01 compliant relay used to route pairing events. The relay learns nothing about the payload' (glossary), and states of kind:24134 that 'Relays do not need any special handling for this kind -- standard NIP-01 event routing is sufficient.' The spec's own stated minimum for a conforming pairing relay is therefore a generic NIP-01 relay, not a purpose-built one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:55"
      - "crates/buzz-core/src/pairing/NIP-AB.md:125"
  - statement: "handle_conn's REQ branch accepts exactly one subscription per connection, restricted to a single filter object containing only kinds (if present, must equal exactly [24134]) and a required #p tag with exactly one 64-lowercase-hex value, and rejects a second REQ on the same connection until CLOSE; the EVENT branch calls validate_event then verify_event_sig then Relay::deliver_single, which requires exactly one live subscriber for the event's #p value (zero or more than one is rejected); the CLOSE branch removes the connection's own subscription and silently ignores an unknown sub_id."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:690-769"
      - "crates/buzz-pair-relay/src/lib.rs:771-865"
      - "crates/buzz-pair-relay/src/lib.rs:867-885"
      - "crates/buzz-pair-relay/src/lib.rs:311-335"
      - "crates/buzz-pair-relay/src/lib.rs:160-212"
  - statement: "verify_event_sig rebuilds the NIP-01 commitment array [0, pubkey, created_at, kind, tags, content], SHA-256 hashes its compact-JSON serialization, checks the hash against the event's claimed id, and verifies a Schnorr signature over that hash using secp256k1's verification-only context -- full NIP-01 event-identity and signature verification, applied only to kind:24134 events."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:513-579"
  - statement: "validate_nip44_content checks that an EVENT's content is standard-alphabet base64 of at least 99 decoded bytes whose first decoded byte is 0x02 (the NIP-44 v2 version byte); it decodes only the first byte and never attempts decryption, so the relay establishes the ciphertext's shape without reading the plaintext -- consistent with NIP-AB.md's 'the relay learns nothing about the payload'."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:337-409"
      - "crates/buzz-core/src/pairing/NIP-AB.md:68"
  - statement: "Beyond NIP-AB.md's stated minimum ('standard NIP-01 event routing is sufficient'), buzz-pair-relay enforces a fixed 128-connection cap (MAX_CONNS), a 4096-byte max WebSocket frame/message size (MAX_FRAME), a 120-second per-connection lifetime (CONN_TIMEOUT), a 6-EVENT-per-connection session cap (MAX_EVENTS_PER_CONN), a 20-message/10s and 10-EVENT/10s per-connection rate limit (RATE_MSG_MAX/RATE_EVENT_MAX), a 12-delivery-per-#p budget (MAX_DELIVERED_PER_P), a 300-second dedup/delivery-counter TTL (ENTRY_TTL), and a +/-120-second created_at freshness window (FRESHNESS_SECS) -- none of which NIP-AB.md requires of a conforming pairing relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:58-89"
  - statement: "lib.rs's module doc states 'Session cap -- at most 6 accepted EVENTs per connection,' but events_attempted is incremented for every signature-verified EVENT attempt regardless of whether delivery subsequently succeeds (the code comment at the increment reads 'Count all valid+sig-verified attempts toward the session cap'), so the cap counts sig-verified attempts, not accepted deliveries -- the doc's word 'accepted' overstates what triggers the count."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:24"
      - "crates/buzz-pair-relay/src/lib.rs:783-810"
  - statement: "This same doc/code mismatch was independently found by the repository's 2026-08-18 full-ecosystem audit and characterized there as 'stricter than documented, not laxer.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:242"
  - statement: "KIND_PAIR is hardcoded to 24134 in lib.rs; the crate has no dependency on buzz-core (confirmed by Cargo.toml's dependency list), so this duplicates rather than imports buzz_core::kind::KIND_PAIRING, which is independently defined as 24134 with the doc comment 'NIP-AB: Device pairing event. Ephemeral -- relay may discard after delivery.' The two constants agree today; nothing keeps them in sync if either changes."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:63"
      - "crates/buzz-pair-relay/Cargo.toml"
      - "crates/buzz-core/src/kind.rs:464-465"
  - statement: "tests/integration.rs contains 51 #[tokio::test] cases (numbered 1-51 in inline comments), matching the count the 2026-08-18 ecosystem audit records for this crate, exercising REQ/EVENT/CLOSE protocol behavior, signature/hex/shape validation, rate limits, session/connection/delivery caps, dedup, the freshness window, and WebSocket-level framing (ping/pong, close, oversized frames, binary frames) end-to-end against a relay bound to 127.0.0.1:0 -- no unit tests exist outside this integration suite, and nothing mocks the WebSocket/TCP stack."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/tests/integration.rs"
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:80"
  - statement: "Running `cargo test -p buzz-pair-relay --release` at the recorded revision produces 49 passed / 2 failed on the default parallel run (test_120s_timeout and test_cancellation_immediate, both #[tokio::test(start_paused = true)], fail with 'connection did not close within 2 s'); re-run with --test-threads=1 still fails test_cancellation_immediate once, but both tests pass reliably when run in isolation -- an intermittent failure exposed by contention with the rest of the suite, not by either test alone. This was executed directly in this session, not read from a report."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/tests/integration.rs:441-453"
      - "crates/buzz-pair-relay/tests/integration.rs:1179-1191"
  - statement: "Neither the Justfile's test-unit recipe nor any cargo nextest/cargo test invocation in .github/workflows/ci.yml names buzz-pair-relay; the nextest archive step that backs most backend CI test jobs only archives buzz-db, buzz-relay and buzz-test-client, and the Justfile's own comments state explicitly that workspace membership alone does not run a crate's tests in CI ('nothing in CI runs cargo test --workspace'). buzz-pair-relay's 51 integration tests therefore do not run in CI today."
    entry_class: FACT
    evidence:
      - "Justfile:316-385"
      - ".github/workflows/ci.yml:376-386"
  - statement: "The 2026-08-18 ecosystem audit independently names buzz-pair-relay among the crates missing from the Justfile's enumerated test-unit recipe and proposes adding a cargo nextest run invocation for it, following the existing enumerated pattern."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:84"
  - statement: "The repository's root Dockerfile compiles buzz-pair-relay's binary explicitly (-p buzz-pair-relay --bin buzz-pair-relay), strips it, and copies it into the runtime image at /usr/local/bin/buzz-pair-relay; the Helm chart's pairing-relay.yaml Deployment (rendered only when pairingRelay.enabled is true) runs that binary directly and sets BUZZ_PAIR_RELAY_BIND_ADDR to 0.0.0.0:<port> -- the opposite of lib.rs's own module-doc claim that the binary 'binds loopback only.'"
    entry_class: FACT
    evidence:
      - "Dockerfile:80"
      - "Dockerfile:179"
      - "deploy/charts/buzz/templates/pairing-relay.yaml:33-38"
      - "crates/buzz-pair-relay/src/lib.rs:9"
  - statement: "The 2026-08-18 ecosystem audit's finding M23 independently identifies this same loopback-doc-vs-Helm-chart contradiction and leaves it as an open design decision (align the doc, or add the missing Ingress/NetworkPolicy to the chart)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:231"
  - statement: "buzz-relay's own ingest.rs implements a byte-for-byte structurally identical NIP-44 envelope check for a different event kind (agent-engram content), and its doc comment states explicitly that it 'Mirrors the validator in buzz-pair-relay::validate_nip44_content' -- confirming the two checks are independently maintained, parallel implementations rather than a shared function."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1802-1816"
      - "crates/buzz-pair-relay/src/lib.rs:337-409"
  - statement: "The corpus node architecture-context-nostr-network states that buzz-pair-relay 'is a separate, ephemeral sidecar relay (not buzz-relay itself) that handles NIP-AB device-pairing handshakes... binds loopback-only, and persists nothing,' citing crates/buzz-pair-relay/src/lib.rs directly, and separately states that no code in buzz-relay's production path opens an outbound WebSocket connection to buzz-pair-relay or any other relay -- confirming buzz-pair-relay is architecturally distinct from, not a component of, buzz-relay's own container."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
  - statement: "The corpus node architecture-containers-mobile describes mobile's PairingSocket as the client-side entry point for NIP-AB device pairing and states plainly that it did not open buzz-pair-relay's own source to confirm the endpoint directly -- an explicit gap this node closes from the relay side."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "The corpus nodes architecture-deployment-single-relay and architecture-deployment-kubernetes both document buzz-pair-relay's packaging: the former as one of three binaries (buzz-relay, buzz-admin, buzz-pair-relay) built into the single-relay Docker image, the latter as pairingRelay.enabled rendering a second, independent Deployment/Service running the same image with the buzz-pair-relay entrypoint."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/single-relay.md"
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "No corpus node yet documents crates/buzz-core/src/pairing/NIP-AB.md itself (the target this node's subject realizes) or crates/buzz-pairing-cli (the sibling interop-testing CLI, tracked separately as issue #931 in this same batch), so no implements edge to the spec and no references/part-of edge to the CLI can be declared -- both are named by real repository path in this node's Target and Scope sections instead, per AGENTS.md's rule that an edge to a nonexistent node id is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
relationships:
  - type: references
    target: architecture-context-nostr-network
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-containers-mobile
---

# buzz-pair-relay: implementation reference

`crates/buzz-pair-relay` is a standalone crate (library `buzz_pair_relay` plus binary
`buzz-pair-relay`) that implements the **transport role** NIP-AB calls the "pairing
relay": a minimal, purpose-built WebSocket relay that routes `kind:24134` device-pairing
events between exactly two ephemeral connections. It claims to realize NIP-AB's pairing
relay role as specified in `crates/buzz-core/src/pairing/NIP-AB.md` -- not the wider
pairing *protocol* (the message-type state machine, key derivation and SAS
confirmation), which lives in `buzz-core/src/pairing/` and is exercised end-to-end by
the sibling `buzz-pairing-cli` crate (documented separately, issue #931).

## Target

**Spec realized:** `crates/buzz-core/src/pairing/NIP-AB.md` ("NIP-AB", Device Pairing).
This file, not `docs/nips/NIP-AB.md`, is the real location -- the latter does not exist
anywhere in this repository. NIP-AB.md has no corpus node id yet, so this node declares
no `implements` edge toward it (an edge to a nonexistent id is a hard validation error
per `AGENTS.md`); open the spec directly for its normative text.

**The relevant part of the spec is narrow.** NIP-AB.md's own glossary defines a
"pairing relay" as "Any NIP-01 compliant relay used to route pairing events. The relay
learns nothing about the payload," and its `kind:24134` section states plainly: "Relays
do not need any special handling for this kind -- standard NIP-01 event routing is
sufficient." The spec's actual requirements for a relay are close to nothing: route
`kind:24134` events, learn nothing about the encrypted payload, optionally treat the
kind as ephemeral. Everything else NIP-AB describes (the offer/accept/sas-confirm/
payload/complete message flow, ECDH key agreement, HKDF derivation, SAS verification,
timeouts and zeroization) is a *client*-side (source/target) responsibility that
`buzz-pair-relay` does not implement and does not need to, since it never decrypts or
interprets `content`.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `Relay::new`, `run_server` (`lib.rs`) | The "pairing relay" role (NIP-AB.md:55) -- accepts WebSocket connections and routes `kind:24134` events | Purpose-built, single-kind relay; not a general NIP-01 relay |
| `handle_conn`'s `REQ` arm + `validate_filter` (`lib.rs:690-769`, `lib.rs:311-335`) | Subscriber registration for the `#p`-filtered delivery NIP-AB's flow depends on (source/target "connect to the pairing relay and exchange... via `kind:24134` events", NIP-AB.md:63) | Restricts to exactly one filter, `kinds:[24134]` if present, one `#p` value, one live subscriber per `#p` -- all stricter than plain NIP-01 |
| `handle_conn`'s `EVENT` arm + `validate_event`/`verify_event_sig` (`lib.rs:771-865`, `lib.rs:411-503`, `lib.rs:513-579`) | Publishing and single-recipient delivery of a `kind:24134` event, with NIP-01 id/signature verification | NIP-AB.md does not itself mandate relay-side signature verification for this kind; the crate performs standard NIP-01 verification anyway |
| `validate_nip44_content` (`lib.rs:337-409`) | The spec's "the relay learns nothing about the payload" (NIP-AB.md:68) | Checks base64 shape and the NIP-44 v2 version byte only; never decrypts |
| `handle_conn`'s `CLOSE` arm (`lib.rs:867-885`) | Session teardown implied by NIP-AB's per-step/session timeouts (client-side) | Relay-side bookkeeping only; the 120 s timeout itself is `CONN_TIMEOUT`, a relay-imposed bound, not a spec requirement |
| `MAX_CONNS`, `MAX_FRAME`, `RATE_MSG_MAX`, `RATE_EVENT_MAX`, `MAX_EVENTS_PER_CONN`, `MAX_DELIVERED_PER_P`, `ENTRY_TTL`, `FRESHNESS_SECS` (`lib.rs:58-89`) | No NIP-AB requirement -- operational hardening (DoS resistance) the crate adds on top of the spec's stated minimum | See *Divergences* |
| `src/main.rs` (`buzz-pair-relay` binary) | Deployment entry point, not part of NIP-AB itself | Reads `BUZZ_PAIR_RELAY_BIND_ADDR`, defaults to loopback-only |

## Divergences

**Deliberate, documented additive strictness (not drift).** NIP-AB.md's own bar for a
conforming relay is "standard NIP-01 event routing is sufficient" -- `buzz-pair-relay`
does far more: connection/frame/rate/session/delivery caps, single-filter-per-
connection, exactly-one-subscriber-per-`#p`, a `created_at` freshness window, and
structural (non-decrypting) validation of the NIP-44 envelope. This is documented in the
crate's own module-level "Security Model" doc comment (`lib.rs:18-26`), so it reads as a
deliberate hardening choice above the spec's floor, not an unreconciled gap against it.

**A real, if narrow, doc/code mismatch inside the crate itself.** The module doc says
"Session cap -- at most 6 accepted EVENTs per connection" (`lib.rs:24`), but the counter
it describes (`events_attempted`, `lib.rs:783-810`) increments for every
signature-verified attempt, whether or not that event is subsequently delivered. The
cap is therefore stricter than "accepted" implies -- it bounds attempts, not successes.
Independently corroborated by the repository's own 2026-08-18 full-ecosystem audit,
which reaches the same conclusion ("stricter than documented, not laxer").

**Loopback-only doc claim contradicted by the shipped deployment.** `lib.rs`'s module
doc states the binary "binds loopback only" and MUST run behind a reverse proxy, but the
Helm chart's `pairingRelay` Deployment sets `BUZZ_PAIR_RELAY_BIND_ADDR=0.0.0.0:<port>`
directly, with no chart-level Ingress/NetworkPolicy enforcing the documented proxy. This
is a deployment-topology question, not a NIP-AB conformance question, so resolving it is
left to the `architecture/deployment/*` nodes that own topology (see *Scope and
omissions*); it is named here because a reader relying on the module doc alone would be
misled about the shipped default. The 2026-08-18 audit's finding M23 independently
raises the same contradiction as an open, unresolved design decision.

**Independently maintained, not shared, with a structurally identical check elsewhere.**
`buzz-relay`'s `ingest.rs` implements the same NIP-44 envelope shape check for a
different event kind and says in its own comment that it mirrors
`buzz-pair-relay::validate_nip44_content`. The two implementations are not drifted
today (both were read and compared), but nothing keeps them in sync if either changes --
a duplication risk, not a current divergence.

## Verification

**No automated CI coverage today.** `buzz-pair-relay`'s 51 `#[tokio::test]` cases in
`tests/integration.rs` are the crate's only test suite. Neither the Justfile's
`test-unit` recipe nor any `cargo nextest`/`cargo test` invocation in
`.github/workflows/ci.yml` names `buzz-pair-relay`; the nextest archive step backing
most backend CI jobs only archives `buzz-db`, `buzz-relay` and `buzz-test-client`. The
Justfile's own comments state this pattern explicitly: crate workspace membership alone
does not run a crate's tests in CI. This gap is independently named by the 2026-08-18
ecosystem audit, which proposes adding an enumerated `cargo nextest run -p
buzz-pair-relay` invocation.

**Run manually in this session** (`cargo test -p buzz-pair-relay --release`, at the
recorded revision): 49 of 51 tests pass. `test_120s_timeout` and
`test_cancellation_immediate` (both `#[tokio::test(start_paused = true)]`) failed on the
default parallel run with "connection did not close within 2 s"; a `--test-threads=1`
re-run still failed `test_cancellation_immediate` once, but both tests passed reliably
when run in isolation. This reads as flakiness from contention with the rest of the
suite under real-wall-clock assertions racing virtual-time advancement, not a defect in
either test's own logic -- but it was not root-caused further, and it means "51/51
green" cannot honestly be claimed as this crate's current, CI-invisible state.

## Relationships

- **implements:** none declared. The target (`crates/buzz-core/src/pairing/NIP-AB.md`)
  has no corpus node id yet; see *Target* above.
- **references:** `architecture-context-nostr-network` (positions `buzz-pair-relay` in
  the wider Nostr network and confirms it is architecturally separate from
  `buzz-relay`), `architecture-deployment-single-relay` and
  `architecture-deployment-kubernetes` (both document its build/deployment packaging),
  `architecture-containers-mobile` (documents the client-side counterpart,
  `PairingSocket`, and explicitly notes it did not verify the relay-side endpoint --
  this node is that verification).
- **part-of:** none. This is the first `implementation`-typed node in the corpus; there
  is no broader implementation-reference node to sit under yet.

## Scope and omissions

**This node covers** what `crates/buzz-pair-relay` is responsible for (routing
`kind:24134` events between exactly two connections, with NIP-01 signature
verification and hardening beyond NIP-AB's stated minimum), its public entry points
(`Relay`, `run_server` as the library surface; the `buzz-pair-relay` binary as the
deployment surface), its dependencies (none on other Buzz crates), its test coverage,
and where its own documentation diverges from its own code or its own deployment.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-AB pairing protocol itself (message types, ECDH/HKDF/SAS, session state machine) | `crates/buzz-core/src/pairing/NIP-AB.md` and its implementing modules (`crypto.rs`, `session.rs`, `types.rs`, `qr.rs`) -- not this node's subject, and not yet a corpus node |
| `buzz-pairing-cli`, the interop-testing client that exercises the full protocol end-to-end | issue #931, same batch, kept as its own node to preserve one concept per node |
| Whether the crate should bind loopback-only or `0.0.0.0` in production, and the missing Ingress/NetworkPolicy question the 2026-08-18 audit's M23 raises | `architecture/deployment/*` nodes (topology is their subject, not NIP-AB conformance) |
| A corpus node for NIP-AB.md itself, which is the prerequisite for a real `implements` edge from this node | unresolved; not filed as its own task here -- check for an existing issue before filing a new one, per `AGENTS.md`'s own guidance |

**Expected but not verified when this node was written:**

- **Root cause of the `test_cancellation_immediate` / `test_120s_timeout`
  intermittent failure** was not investigated beyond confirming it is a
  suite-contention effect (fails amid the full run, passes in isolation) rather than a
  failure of either test alone. Whether it is a `tokio::time::pause` interaction, a
  real-wall-clock budget that is simply too tight under load, or something else in the
  relay's shutdown path was not determined.
- **Whether `cargo nextest run -p buzz-pair-relay` (the tool CI actually standardizes
  on for other crates) reproduces the same two-test flakiness** was not checked --
  `cargo-nextest` was not installed in this session's environment, so only plain
  `cargo test` was run.
- **Whether the Helm chart's `pairingRelay` Service is ever exposed outside the
  cluster** (the actual internet-exposure question M23 leaves open) was not checked --
  only the Deployment's bind address and the absence of a chart-rendered
  Ingress/NetworkPolicy were confirmed directly.
