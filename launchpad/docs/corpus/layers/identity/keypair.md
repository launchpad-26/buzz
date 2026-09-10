---
id: layers-identity-keypair
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
  - statement: "NIP-01 defines a Nostr identity as a keypair: 'Each user has a keypair. Signatures, public key, and encodings are done according to the Schnorr signatures standard for the curve secp256k1.'"
    entry_class: FACT
    evidence:
      - "https://raw.githubusercontent.com/nostr-protocol/nips/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/01.md"
  - statement: "Buzz depends on the `nostr` crate at workspace version 0.44 for its Nostr protocol types, including the `Keys`, `SecretKey` and `PublicKey` types every crate in the workspace uses via `nostr = { workspace = true }`."
    entry_class: FACT
    evidence:
      - "Cargo.toml:72"
      - "crates/buzz-admin/Cargo.toml:24"
      - "crates/buzz-cli/Cargo.toml:36"
  - statement: "Below the `nostr` crate's `Keys` wrapper, a Buzz keypair is a raw secp256k1 keypair whose public half is serialized as an x-only (32-byte) public key -- the BIP-340/Schnorr shape NIP-01 specifies -- as shown by a test helper that builds one directly with `secp256k1::Secp256k1` and `x_only_public_key()` rather than going through `nostr::Keys`."
    entry_class: FACT
    evidence:
      - "crates/buzz-pair-relay/tests/integration.rs:89-100"
  - statement: "`buzz-admin generate-key` creates a new keypair with `Keys::generate()`, prints the public key as hex and the secret key, and tells the operator to set `BUZZ_PRIVATE_KEY` to the secret key to use it as an identity -- the CLI's own doc comment calls this 'Generate a new Nostr keypair (for bootstrapping).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:77-78"
      - "crates/buzz-admin/src/main.rs:142-150"
  - statement: "`buzz-cli` requires a `BUZZ_PRIVATE_KEY` (hex or nsec) to run any relay operation, parses it with `Keys::parse`, and states directly in code comments: 'Auth: private key is required for all relay operations. The keypair IS the identity -- no tokens, no other auth.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2026-2032"
  - statement: "`BuzzClient` (buzz-cli's relay client) holds the parsed `Keys` for the lifetime of the session and exposes it via a `keys()` accessor; every event the client signs goes through this one keypair."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/client.rs:541-564"
  - statement: "A keypair's two halves have asymmetric roles when an event moves through Buzz: the private half signs (`sign_with_keys`/`sign_event`, buzz-cli), and the public half is what `verify_event` checks the Schnorr signature and event-id hash against, without ever needing the private half."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/verification.rs:1-32"
      - "crates/buzz-cli/src/client.rs:588-594"
  - statement: "The relay's own operational keypair is resolved in a priority order -- an explicit `--relay-key` argument, then the `BUZZ_RELAY_PRIVATE_KEY` environment variable, then (only where safe) an ephemeral `Keys::generate()` fallback -- and a force-republish code path explicitly refuses the ephemeral fallback because it would replace an existing authoritative snapshot with events an unrecoverable key signed."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:97-107"
      - "crates/buzz-admin/src/main.rs:483-507"
  - statement: "Buzz's own code and CLI comments describe a keypair as a full substitute for a token-based auth system for a given identity (buzz-cli's 'no tokens, no other auth'), which generalizes beyond that one comment: buzz-admin's operator-facing generate-key flow, buzz-cli's client construction, and the relay's signature-verification path all key authentication and identity exclusively off possession of a keypair's private half, with no session token, API key or credential store anywhere in that path."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-cli/src/lib.rs:2026-2032"
      - "crates/buzz-admin/src/main.rs:142-150"
      - "crates/buzz-cli/src/client.rs:541-564"
      - "crates/buzz-core/src/verification.rs:1-32"
    confidence: 0.8
  - statement: "AGENTS.md's auth env vars for the agent-facing CLI (`BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`) are auto-injected by the ACP harness into managed agent subprocesses, and in development are set manually -- meaning an agent identity in Buzz is provisioned the same way a human operator's is: as a keypair handed to the process, not as a separately issued credential."
    entry_class: INFERENCE
    evidence:
      - "AGENTS.md:191"
      - "crates/buzz-cli/src/lib.rs:2026-2032"
    confidence: 0.6
---

# Keypair

A **keypair** is the single secp256k1 key pair -- a private key and its
derived public key -- that Buzz uses as one participant's entire identity and
authentication mechanism. Whoever holds the private half of a keypair *is*
that identity in every Buzz surface: relay, CLI, admin tooling and agent
harness alike. There is no separate account system, session token or API key
layered on top; the keypair does that job by itself.

## What this concept covers, and what it does not

This node is the **pairing concept**: what a keypair *is*, why Buzz treats it
as identity, and where in the system a keypair gets created, held and
checked. It deliberately does **not** go deep on either half in isolation:

- How a private key is generated, stored, rotated or kept secret is the
  private-key concept's job, not this node's.
- How a public key functions as an addressable identifier -- in NIP-29
  channel membership, in `p` tags, in mentions -- is the public-key concept's
  job, not this node's.

Both of those are separate, independently maintainable ideas and are tracked
as sibling documentation tasks; this node does not fold them in, per this
corpus's rule that a second concept discovered while writing gets filed as
its own task rather than merged into the one in hand.

Do not confuse a keypair with a **session token**, an **API key**, or an
**auth tag**. Buzz's NIP-OA auth tag (`["auth", owner_pubkey, conditions,
sig]`, carried by `buzz-cli`) is itself *signed by* a keypair -- it is a
capability built on top of keypair-based identity, not an alternative to it.

## Where the shape comes from

NIP-01, the base Nostr protocol specification, is where the shape originates:
"Each user has a keypair. Signatures, public key, and encodings are done
according to the Schnorr signatures standard for the curve secp256k1." Buzz
consumes this through the `nostr` crate (workspace dependency, version 0.44)
rather than implementing secp256k1/Schnorr itself. Underneath that wrapper,
the public half is an x-only (32-byte) public key -- the same BIP-340/Schnorr
shape the spec calls for -- which is visible directly in a test helper that
builds a keypair with the raw `secp256k1` crate instead of going through
`nostr::Keys`.

## Use cases

A reader needs this concept whenever they are provisioning, holding, or
checking a Buzz identity:

- **Bootstrapping a new identity.** `buzz-admin generate-key` calls
  `Keys::generate()`, prints the resulting public key (hex) and secret key,
  and tells the operator to set `BUZZ_PRIVATE_KEY` to that secret to start
  using it. This is the entry point for both human operators and agents that
  need a fresh identity.
- **Authenticating a CLI session.** `buzz-cli` refuses to run any relay
  operation without `BUZZ_PRIVATE_KEY`; it parses that value into a `Keys`
  and holds it for the session's lifetime inside `BuzzClient`. Every event
  the session signs goes through that one keypair -- there is no separate
  login step.
- **Signing and verifying events.** The private half signs; the public half
  (carried as `event.pubkey`) is what the relay's `verify_event` checks the
  Schnorr signature and event-id hash against. A reader who needs to
  understand why an event either is or is not trusted needs this
  asymmetry: the checking side never needs, or sees, the private half.
- **Operating the relay itself.** The relay's own signing identity (used for,
  for example, republishing channel membership snapshots) is resolved from an
  explicit key argument, then an environment variable, and only falls back to
  a freshly generated ephemeral keypair when neither is configured -- and
  that fallback is explicitly refused on the force-republish path, because
  events signed by a keypair nobody retains become unverifiable the moment
  the process exits.

## Persistent versus ephemeral keypairs

Buzz's own code draws this distinction operationally, not just as a
naming convention:

| | Persistent keypair | Ephemeral keypair |
|---|---|---|
| Created by | `buzz-admin generate-key`, then stored (e.g. as `BUZZ_PRIVATE_KEY`) | `Keys::generate()` called inline, with nothing written down |
| Identity survives a restart | Yes | No -- a new process gets a different keypair |
| Used for | CLI sessions, agent identities, the relay's normal operating key | Test fixtures, and the relay's last-resort fallback when no configured key exists |
| Buzz's own guardrail | N/A | The relay's force-republish path refuses this fallback outright, because it would replace an authoritative snapshot with events an unrecoverable key signed |

## Related resources

- NIP-01 (`https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/01.md`) --
  the protocol specification a Buzz keypair implements.
- `crates/buzz-admin/src/main.rs` -- the `generate-key` bootstrapping command
  and the relay's own keypair-resolution logic.
- `crates/buzz-cli/src/lib.rs` and `crates/buzz-cli/src/client.rs` -- how an
  agent or operator session is authenticated by a keypair alone.
- `crates/buzz-core/src/verification.rs` -- how the public half of a keypair
  is used to verify a signed event.

No `relationships` entries are declared. Checked, rather than assumed: at
this node's recorded revision, `origin/launchpad`'s
`launchpad/docs/corpus` tree carries no `layers/` subtree at all (confirmed
via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
before drafting), so there is no sibling identity node -- private-key,
public-key, or otherwise -- for this node to point at yet. The likely future
edges are `references` targeting those two sibling concept nodes once they
merge.

## Scope and omissions

**This node covers** what a Buzz keypair is, the protocol shape it
implements, why Buzz treats it as identity rather than layering a separate
auth system on top, where in the codebase a keypair is created and checked,
and the operational distinction between a persistent and an ephemeral
keypair.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Private-key generation, storage, rotation and secret-handling detail | #1112 (sibling task) |
| Public-key-as-identifier mechanics -- `p` tags, NIP-29 membership, mentions | #1113 (sibling task) |
| NIP-44/NIP-98 encryption and auth-tag mechanics that consume a keypair's derived shared secret (`crates/buzz-sdk/src/nip_oa.rs`) | Not yet filed as its own corpus task at this revision |
| The reference-level catalogue of every `Keys`/`SecretKey`/`PublicKey` call site in the workspace | A future reference-typed node, not this concept node (per this corpus's own template guidance to keep a concept document free of an exhaustive parameter/call-site table) |

**Expected but not verified when this node was written:**

- **Mobile and desktop client-side keypair handling was not inspected.**
  This node's evidence is drawn entirely from the Rust workspace
  (`crates/`); how the desktop (Tauri) or mobile (Flutter) apps generate,
  store or prompt for a keypair was not checked and may differ materially
  from the CLI/admin/relay picture described here.
- **NIP-AB device-pairing's use of ephemeral keypairs**
  (`crates/buzz-core/src/pairing/qr.rs`) was noticed during evidence
  gathering but not investigated in depth -- it is a third kind of
  keypair lifecycle (session-scoped, exchanged via QR code) beyond the
  persistent/ephemeral distinction described above, and is left for
  whichever future node documents device pairing.
