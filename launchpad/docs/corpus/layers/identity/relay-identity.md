---
id: layers-identity-relay-identity
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
  - statement: "`AppState` (the relay's shared runtime state) carries a `relay_keypair: nostr::Keys` field -- the relay's own Nostr keypair, held once per running relay process and distinct from any human or agent user's keypair."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:670"
  - statement: "At startup, `main.rs` sources `relay_keypair` in exactly three branches: parse `BUZZ_RELAY_PRIVATE_KEY` when set; otherwise, if `BUZZ_REQUIRE_AUTH_TOKEN=false` (dev mode), fall back to a hardcoded deterministic key (`DEV_RELAY_PRIVKEY = 0x...0001`) so addressable events (kind:39000/39001/39002) replace correctly across restarts instead of duplicating under a fresh pubkey each time; otherwise panic with 'BUZZ_RELAY_PRIVATE_KEY must be set when BUZZ_REQUIRE_AUTH_TOKEN=true.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:425-446"
  - statement: "`Config::from_env` reads the relay's signing key from exactly one environment variable, `BUZZ_RELAY_PRIVATE_KEY`, into `Config.relay_private_key: Option<String>`; a stable value is additionally required (checked and rejected fast, before any DB mutation) whenever `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true`, because NIP-43 events signed under an ephemeral key become unverifiable after restart."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:127"
      - "crates/buzz-relay/src/config.rs:709"
      - "crates/buzz-relay/src/main.rs:244-252"
  - statement: "The NIP-11 relay information document exposes the relay's own signing pubkey as the `self` field (`relay_self`), populated only when the relay holds a stable key (`state.config.relay_private_key.is_some()`); the field's doc comment states NIP-29 group-metadata events (kinds 39000/39001/39002, which Buzz always signs with `state.relay_keypair`) must be verified by clients against this same `self` value, and NIP-43 is advertised in `supported_nips` only when a stable key exists, since NIP-43 events are likewise verified against `self`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:55-57"
      - "crates/buzz-relay/src/nip11.rs:122-140"
      - "crates/buzz-relay/src/nip11.rs:294-311"
  - statement: "The relay signs several categories of events with `state.relay_keypair` via `sign_with_keys`: system messages (kind 40099, `emit_system_message`), NIP-29 group discovery events (kinds 39000/39001/39002, 'signed by the relay keypair' per that function's own doc comment), the NIP-43 relay membership list (kind 13534, `KIND_NIP43_MEMBERSHIP_LIST`), and git ref-state events -- none of these are events any user or agent keypair can produce."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:763-775"
      - "crates/buzz-relay/src/handlers/side_effects.rs:1052"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2941-2982"
      - "crates/buzz-relay/src/handlers/side_effects.rs:2864-2865"
      - "crates/buzz-core/src/kind.rs:398"
  - statement: "`buzz-core::kind::is_relay_only_kind` names a closed set of kinds -- including `KIND_NIP43_MEMBERSHIP_LIST` (13534), channel summary, presence snapshot, DM visibility, thread summary, and window bounds -- that only the relay may author, and its doc comment states 'Client submission of these kinds must be rejected,' which the ingest path enforces as an authorship boundary rather than a convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:828-839"
  - statement: "Accepting a push-lease request requires decrypting its NIP-44 payload with `state.relay_keypair.secret_key()` against the requester's pubkey (`nostr::nips::nip44::decrypt(state.relay_keypair.secret_key(), &event.pubkey, &event.content)`) -- the relay keypair is used for decryption, not only for signing outbound events."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs:487-490"
  - statement: "When the inter-relay mesh (`BUZZ_MESH`) is enabled, `boot_mesh` anchors `ReadyRecord` acceptance to `relay_keypair.public_key()` via `MeshMembership::with_expected_relay_pubkey`, so that every pod in a deployment shares one relay signing key and a `ReadyRecord` attested by any other key is rejected as foreign; the surrounding comment states this directly: 'all pods share the relay signing key... a seed attested by any other key is foreign and rejected (possession is not authorization).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs:415"
      - "crates/buzz-relay/src/mesh_boot.rs:442-451"
  - statement: "`RELAY_OWNER_PUBKEY` (`config.relay_owner_pubkey`) is a separate concept from `relay_keypair`: `main.rs` requires it only to bootstrap an administrative row, and `relay_members::bootstrap_owner` upserts it into the `relay_members` table with `role = 'owner'` -- a stored pubkey string the relay never holds a matching secret key for and never uses to sign or decrypt anything; it identifies a human administrator, not the relay's own runtime identity."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:244-253"
      - "crates/buzz-relay/src/main.rs:322-345"
      - "crates/buzz-db/src/store/relay_members.rs:350-378"
  - statement: "`git-sign-nostr` signs git commits and tags with a Nostr keypair loaded from `NOSTR_PRIVATE_KEY`, then `BUZZ_PRIVATE_KEY`, then a keyfile -- the acting user's or agent's own key, never the relay's `relay_keypair` -- and Buzz's dev MCP tooling (`buzz-dev-mcp`) depends on it for that purpose; it is a per-actor git-signing mechanism, not a relay-identity mechanism."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
      - "crates/buzz-dev-mcp/Cargo.toml"
  - statement: "The Helm chart's operator-facing documentation states plainly that rotating `BUZZ_RELAY_PRIVATE_KEY` changes the relay's identity and that federation peers will not recognize the relay afterward, and lists it as one of five items whose loss is data loss for a deployment -- corroborating from the deployment side what this node establishes from the code side, that `relay_keypair` is a durable, load-bearing identity rather than an ordinary rotatable secret."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md:214"
      - "deploy/charts/buzz/values.yaml:89"
  - statement: "The dev-mode hardcoded fallback keypair exists specifically so addressable-event replacement (kind:39000/39001/39002, NIP-33 semantics) behaves correctly across relay restarts in local development, where an operator has not set `BUZZ_RELAY_PRIVATE_KEY`; without a stable pubkey each restart would mint a new relay identity and `replace_addressable_event` would insert duplicates instead of replacing."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs:428-439"
    confidence: 0.85
  - statement: "Issue #1114's Definition of Done requires exactly one hand-authored canonical document with schema-valid front matter, evidence and typed relationships appropriate to the node, representing one independently maintainable knowledge node, with every substantive claim traceable to FACT/INFERENCE/TEAM_KNOWLEDGE evidence, linking neighboring corpus nodes without duplicating their content, checked against the recorded revision, passing corpus validation, defining the term in one sentence before deeper explanation, stating boundaries/non-goals, linking related concepts/implementation/verification, and using examples only to clarify rather than introduce a second concept."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1114 definition of done"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-context-relay-operator
---

# Relay Identity

**The Buzz relay itself has its own Nostr keypair.** It is a single
cryptographic identity held by the running relay process (`relay_keypair`,
sourced from the `BUZZ_RELAY_PRIVATE_KEY` environment variable), used to sign
and decrypt the events only the relay is allowed to produce -- distinct from
every human's, agent's, or relay operator's own keypair.

## Definition

`AppState.relay_keypair` is an `nostr::Keys` value constructed once at relay
startup and shared by every request the process handles. It is sourced from
`BUZZ_RELAY_PRIVATE_KEY` when set; in local development
(`BUZZ_REQUIRE_AUTH_TOKEN=false`) it falls back to a hardcoded, deterministic
key so kind:39000/39001/39002 addressable events keep replacing correctly
across restarts instead of duplicating under a fresh pubkey each time; in a
production configuration (`BUZZ_REQUIRE_AUTH_TOKEN=true`) with no key set,
startup panics rather than boot with an unstable identity. When relay
membership enforcement is on (`BUZZ_REQUIRE_RELAY_MEMBERSHIP=true`), a stable
key is required outright, because NIP-43 membership events signed under an
ephemeral key become unverifiable the moment the relay restarts and mints a
new one.

## Boundary -- what this is not

- **Not the relay owner.** `RELAY_OWNER_PUBKEY` names a human administrator
  and is written into the `relay_members` table with `role = 'owner'` --
  the relay never holds a secret key for it and never signs or decrypts
  anything with it. `relay_keypair` and the owner's pubkey are two
  independent values that happen to both be configured by the same
  operator.
- **Not a per-agent or per-human identity.** Every user and every AI agent
  in Buzz has its own keypair (see the sibling `layers/identity/` nodes on
  agent and human identity once merged); `relay_keypair` is the one
  identity the *relay process itself* holds, used only for events the
  protocol reserves to the relay.
- **Not what `git-sign-nostr` signs with.** `git-sign-nostr` (used by
  `buzz-dev-mcp` and any git client configured to use it) signs git commits
  and tags with the *acting user's or agent's* key, loaded from
  `NOSTR_PRIVATE_KEY`, then `BUZZ_PRIVATE_KEY`, then a keyfile -- never from
  `relay_keypair`. A relay-signed git ref-state event (see *What it signs*
  below) and a user's signed git commit are produced by two different keys
  for two different purposes.
- **Not necessarily unique per pod.** In a multi-pod deployment, every pod
  is configured with the same `BUZZ_RELAY_PRIVATE_KEY`, so `relay_keypair`
  identifies the *deployment*, not an individual process instance -- the
  inter-relay mesh's readiness registry explicitly anchors trust to this
  shared key for exactly that reason (see *Federation and mesh* below).

## What it signs and decrypts

Only the relay ever holds `relay_keypair`, so only the relay can produce the
events built with it:

- **System messages** -- kind 40099, via `emit_system_message`.
- **NIP-29 group discovery events** -- kinds 39000 (metadata), 39001, and
  39002 (membership), described in code as "signed by the relay keypair."
- **The NIP-43 relay membership list** -- kind 13534
  (`KIND_NIP43_MEMBERSHIP_LIST`), published by
  `publish_nip43_membership_list`.
- **Git ref-state events**, built and signed alongside the relay's git smart
  HTTP handling.
- **NIP-44 decryption of push-lease requests** -- accepting a push lease
  decrypts the requester's payload with `relay_keypair.secret_key()`, so the
  key is used to decrypt inbound content, not only to sign outbound events.

`buzz-core::kind::is_relay_only_kind` enforces the authorship side of this
boundary directly: it names a closed set of kinds -- including the NIP-43
membership list plus channel summary, presence snapshot, DM visibility,
thread summary, and window-bounds events -- that the ingest path rejects if
a client attempts to submit them itself. Being relay-only in code means
being reachable only through `relay_keypair`.

## How it is advertised

Clients discover the relay's pubkey through the standard NIP-11 relay
information document (`GET /` with `Accept: application/nostr+json`), whose
`self` field mirrors `relay_keypair.public_key()` whenever a stable key is
configured. Two things are gated on that same stable-key condition: the
`self` field is populated (an ephemeral dev key is deliberately excluded,
since it changes on every restart and would leave previously signed events
permanently unverifiable), and NIP-43 is listed in `supported_nips` only
when the relay both has a stable key and is actually enforcing membership --
NIP-43 events are verified against `self`, so advertising the NIP without a
`self` value would give clients no way to check them.

## Federation and mesh

When the inter-relay mesh (`BUZZ_MESH`) is enabled, `boot_mesh` uses
`relay_keypair.public_key()` to anchor trust in the mesh's peer-readiness
registry: every `ReadyRecord` a peer publishes is checked against the
deployment's expected relay pubkey, and a record attested by any other key
is rejected as foreign. The code comment states the reasoning directly --
"all pods share the relay signing key... possession is not authorization" --
meaning `relay_keypair` is the identity the *deployment* presents to other
relays in a mesh, not an identity scoped to one running process.

## Operational consequence of rotation

Because so much depends on `relay_keypair` staying stable across restarts,
rotating `BUZZ_RELAY_PRIVATE_KEY` is a relay identity change, not an ordinary
secret rotation: previously signed NIP-29 group-metadata and NIP-43
membership events stop verifying against the new `self`, and mesh peers stop
recognizing the deployment. The Helm chart's own operator documentation
states this plainly and lists the key among the items whose loss is
irrecoverable data loss for a deployment -- this node's code-level findings
and that deployment-level guidance describe the same fact from two
directions.

## Scope and omissions

**This node covers** the relay's own Nostr keypair: where it comes from,
what it signs and decrypts, how it is advertised over NIP-11, how it differs
from the relay owner's pubkey and from `git-sign-nostr`'s per-actor signing,
and its role as the deployment's identity in the inter-relay mesh.

**It does not cover, and these are gaps rather than silence:**

- **Human and agent identity** -- `layers-identity-human-identity` and
  `layers-identity-agent-identity` (issues #1106 and #1103) are unmerged at
  this revision, so no `relationships` edge to either exists yet; this node
  does not restate their content.
- **NIP-29, NIP-43, or NIP-44 protocol semantics themselves** -- this node
  documents *whose key* signs or decrypts relay-authored events, not how
  those NIPs work.
- **The mesh's broader design** (gossip, reconciliation, transport) --
  covered by `buzz-relay-mesh` and its own documentation; only the identity
  boundary the mesh enforces is in scope here.
- **Whether any deployment tooling automates key rotation** -- not inspected
  for this node; the operational-consequence section above states what
  rotation *breaks*, not how or whether it is currently performed safely.
