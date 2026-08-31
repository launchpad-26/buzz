---
id: capabilities-pairing-pairing-relay
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "buzz-pair-relay is an ephemeral, stateless sidecar relay -- a separate binary from buzz-relay -- purpose-built to route NIP-AB device-pairing handshakes: it accepts WebSocket connections, matches kind:24134 EVENTs against live #p-filtered REQ subscriptions, and forwards a match to exactly one subscriber. It persists nothing and authenticates no client identity of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:1-26"
      - "crates/buzz-pair-relay/Cargo.toml:3"
  - statement: "The capability exists to let a user attach a second device (for example, a mobile phone) to an identity already active on a first device (for example, desktop), by transferring a secret over a short-lived, end-to-end encrypted channel that the relay itself cannot read -- NIP-AB's stated motivation, distinct from NIP-46 remote signing (key stays on one device) and NIP-06 mnemonic entry (manual, error-prone)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:41-49"
  - statement: "The relay's own role in the protocol is definitionally minimal: NIP-AB defines 'pairing relay' as any NIP-01-compliant relay used to route pairing events, stating explicitly that the relay learns nothing about the payload -- buzz-pair-relay is one concrete, purpose-built implementation of that role, not a requirement of the protocol itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:55"
  - statement: "The relay enforces a closed, narrow protocol surface rather than general Nostr relay behavior: a REQ filter must be exactly {\"kinds\":[24134]} plus a single #p value (one subscriber per pubkey, enforced atomically); an EVENT must carry exactly the seven standard NIP-01 fields, exactly one [\"p\", \"<64-hex>\"] tag, a created_at within a 120-second freshness window, NIP-44-v2-shaped content, and a verified Schnorr signature matching its own id hash before delivery is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:312-335"
      - "crates/buzz-pair-relay/src/lib.rs:411-503"
      - "crates/buzz-pair-relay/src/lib.rs:521-579"
  - statement: "The relay bounds its own resource use rather than relying on an operator-side gateway alone: at most 128 concurrent WebSocket connections, a 120-second hard per-connection lifetime, a 4 KiB max frame/message size, at most 6 accepted (signature-verified) EVENTs per connection, at most 12 delivered events per #p recipient, and capacity-bounded, TTL-evicted dedup/delivery-tracking structures that fail closed (reject new entries) rather than grow unbounded once full."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:58-89"
      - "crates/buzz-pair-relay/src/lib.rs:135-217"
  - statement: "The binary's own module documentation states it binds loopback only and MUST run behind a reverse proxy that routes only /pair to it, enforces HTTP read timeouts, and terminates TLS -- the relay itself performs no path restriction and no pre-upgrade connection limiting."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/lib.rs:7-16"
  - statement: "The bind address is runtime-configurable via BUZZ_PAIR_RELAY_BIND_ADDR, defaulting to 127.0.0.1:5000 (loopback) when unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/src/main.rs:9-11"
  - statement: "This capability is shipped, not merely designed: buzz-pair-relay is a declared workspace member, its binary is compiled into the same container image as buzz-relay and buzz-admin, and its behavior is covered by a dedicated integration test suite exercising the WebSocket protocol surface end to end."
    entry_class: FACT
    evidence:
      - "Cargo.toml:27"
      - "Dockerfile:80-87"
      - "Dockerfile:179-186"
      - "crates/buzz-pair-relay/tests/integration.rs:1-30"
  - statement: "Deployment of this capability is optional and off by default: the Helm chart's pairingRelay.enabled value defaults to false, and when enabled it renders a separate Deployment/Service running the same container image with the buzz-pair-relay entrypoint, sized independently from the main relay."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:213-217"
      - "deploy/charts/buzz/templates/pairing-relay.yaml:2-14"
  - statement: "The Helm chart's own container spec sets BUZZ_PAIR_RELAY_BIND_ADDR to 0.0.0.0:<port> rather than a loopback address, and renders no Ingress or NetworkPolicy for the pairing-relay Service -- an operator who deploys the chart's optional pairingRelay without adding their own reverse proxy and network restriction does not get the loopback-plus-proxy posture the crate's own module doc describes as a MUST."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/pairing-relay.yaml:37-38"
  - statement: "This same discrepancy between the crate's documented deployment posture and the reference Helm chart's actual bind address was independently found and recorded as finding M23 in a full-ecosystem audit, which notes it as not confirmed to be directly internet-exposed (Service type was not checked in that audit) and recommends a design decision to reconcile the doc and the chart rather than assuming either is correct."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:231"
  - statement: "buzz-pairing-cli exercises this relay as a client for interop testing, and buzz-ws-client is the shared WebSocket client library used to connect to it -- both are separate crates from buzz-pair-relay itself and are not this capability's own subject matter."
    entry_class: FACT
    evidence:
      - "AGENTS.md:76-82"
  - statement: "No corpus node of type capabilities exists yet on origin/launchpad at the recorded revision -- the capabilities/ subtree did not exist before this node -- so no sibling capability node (an overview device-pairing node, a pairing-cli node, or a pairing-session node) is a resolvable relationships target; declaring an edge to any of them would fail validate.py's relationship-target check until that sibling merges."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.9
---

# Pairing relay: capability

Buzz lets a user attach a second device to an identity already active on a
first device -- for example, adding a mobile phone to an account already
signed in on desktop -- without ever pasting a raw private key between them.
**Pairing relay** is the piece of infrastructure that makes the handshake
possible: an ephemeral, stateless WebSocket relay, `buzz-pair-relay`, that
exists solely to route the short-lived NIP-AB pairing handshake between the
two devices and then forgets it ever happened.

## Maturity

**Shipped.** `buzz-pair-relay` is a declared Rust workspace member with its
own binary entrypoint, is compiled into the same container image that ships
`buzz-relay` and `buzz-admin`, and its protocol behavior (REQ/EVENT
validation, signature verification, delivery, rate limiting, session caps)
is exercised by a dedicated integration test suite. Deployment of a
standalone instance via the reference Helm chart is optional and disabled
by default (`pairingRelay.enabled: false`) -- the capability ships in the
image either way; a given deployment chooses whether to run it as its own
scaled service or rely on the legacy same-host `/pair` convention the
chart's own comment references.

## Boundary

This node does not describe:

- **The NIP-AB protocol itself** -- the QR-code exchange, ephemeral key
  derivation, SAS confirmation, and encrypted payload format are a Nostr
  protocol specification (`crates/buzz-core/src/pairing/NIP-AB.md`), not
  this relay's own behavior. The relay is one implementation of the
  protocol's "pairing relay" role; it does not define the role.
- **`buzz-pairing-cli`**, the interop-testing client that talks to this
  relay, or `buzz-ws-client`, the shared WebSocket client library it and
  other crates use to connect. Both are separate crates with their own
  subject matter.
- **The broader device-pairing capability from a product/user-journey
  angle** (what a user sees and does end to end) -- that is a distinct,
  not-yet-drafted capability node; this node stays at the level of the one
  piece of relay infrastructure the handshake depends on.
- **How the capability is operated in production** -- Kubernetes topology,
  scaling, and monitoring for an enabled `pairingRelay` deployment belong to
  the deployment/operations surface (see `architecture/deployment/
  multi-relay.md` and `architecture/deployment/hosted-topology.md`, which
  already describe the Helm chart's pairing-relay Deployment/Service from
  that angle).

## Relationships

None declared. No `type: capabilities` node exists yet on `origin/launchpad`
at the recorded revision -- this is the first -- so there is no sibling
device-pairing overview, pairing-cli, or pairing-session node to
`references` or sit `part-of`. The architecture/deployment nodes that
already describe `buzz-pair-relay` from other angles
(`architecture/context/nostr-network.md`,
`architecture/deployment/hosted-topology.md`,
`architecture/deployment/multi-relay.md`,
`architecture/deployment/single-relay.md`,
`architecture/containers/mobile.md`) were read as corroborating evidence for
this node's claims but are not cited as `relationships` targets: this
template's guidance treats `references` as pointing to the architecture
that *realizes* a capability, and adding four edges to nodes that only
mention this capability in passing, without checking each one's own
`relationships` conventions, risks asserting a stronger coupling than any
of them actually documents. A future revision of this node is the place to
add those edges once its own review has settled which direction they
should point.

## Scope and omissions

**This node covers** what the pairing-relay capability is, for whom, what
protocol surface it accepts (kind:24134 EVENTs under a single-#p REQ
filter), what its own resource and validation bounds are, and its current
shipped/optional-deployment maturity.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-AB protocol specification itself | `crates/buzz-core/src/pairing/NIP-AB.md` |
| `buzz-pairing-cli` (the interop test client) | a future `pairing-cli` capability/component node |
| The end-to-end device-pairing user journey | a future device-pairing capability node |
| Kubernetes deployment topology for an enabled `pairingRelay` | `architecture/deployment/multi-relay.md`, `architecture/deployment/hosted-topology.md` |

**Expected but not verified when this node was written:**

- **Whether any live deployment actually enables `pairingRelay`** was not
  checked -- this node describes what the chart renders when enabled, not
  whether any environment currently runs it.
- **Whether the loopback-doc-vs-`0.0.0.0`-chart discrepancy (noted above,
  and independently recorded as audit finding M23) has since been resolved
  one way or the other** was not re-checked beyond the chart's state at the
  recorded revision -- this node states the discrepancy as observed, not a
  claim about which side is intended to be correct.
- **Whether NIP-AB version 1 (the only version currently defined) remains
  the only version in use** was not verified beyond reading the spec's own
  version table; a future version bump is the spec's concern, not this
  relay's.
