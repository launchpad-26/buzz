---
id: layers-identity-private-key
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
  - statement: "Buzz's identity keys are secp256k1 Nostr keypairs handled through the third-party `nostr` crate's `Keys`/`SecretKey` types (workspace version 0.44), not a custom key implementation; both the workspace root and the desktop app depend on it directly."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "desktop/src-tauri/Cargo.toml"
  - statement: "The desktop app's `identity_from_env` function reads `BUZZ_PRIVATE_KEY` into a variable named `nsec`, calls `nostr::Keys::parse` on it, and treats a present-but-malformed value as absent -- logging it and falling through to persisted-key resolution -- rather than silently continuing on an ephemeral identity."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs"
  - statement: "The desktop app's documented private-key resolution priority is: the `BUZZ_PRIVATE_KEY` environment variable, then the OS keyring, then a plaintext `{app_data_dir}/identity.key` file, then generating and saving a new key."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs"
  - statement: "The desktop app stores what it calls 'nsec private keys' in the OS keyring (macOS Keychain, Windows Credential Manager, or Linux Secret Service) rather than in plaintext files, covering both the human identity key and every managed-agent key; when no keyring backend is reachable it falls back to a `0o600` owner-only file, and on migration a key is imported, read back to verify the round-trip, and only then is the old plaintext copy deleted."
    entry_class: FACT
    evidence:
      - "SECURITY.md"
      - "desktop/src-tauri/src/secret_store.rs"
  - statement: "The OS keyring secret store is deliberately not on any environment-variable read path: its own module documentation states that `BUZZ_PRIVATE_KEY` resolution for harnessed agents and CI is handled upstream of the store, so adding an env tier inside it would duplicate that precedence and create a divergent-behavior trap."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
  - statement: "A private key signs a Nostr event entirely client-side, and only the resulting signed `Event` -- a public key, tags, content and a signature, never the private key -- is transmitted: `buzz-ws-client`'s `build_auth_event` constructs a NIP-42 `kind:22242` auth event and calls `EventBuilder::sign_with_keys(keys)` locally before the event is sent to the relay over the WebSocket."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "`buzz-sdk`'s own module documentation states the general pattern every event builder in the crate follows: 'The caller signs with their own keys: builder.sign_with_keys(&keys)?' -- so client-side signing with a private key that never leaves the caller is not specific to authentication events but is how every Nostr event this identity publishes is produced."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/lib.rs"
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "The relay's own NIP-42 verification function, `verify_nip42_event`, takes only a signed `Event` -- no private key or `Keys` value appears anywhere in its signature -- confirming that the relay's authentication path never receives raw private-key material; it checks a Schnorr signature over data the client already signed, via `buzz_core::verify_event`."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "A private key also signs Git commits and tags, not only relay-facing events: `git-sign-nostr` is a pluggable git signing program (`gpg.x509.program`) that signs with BIP-340 Schnorr signatures using the signer's Nostr keypair."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs"
  - statement: "`git-sign-nostr` documents that it deliberately bypasses `nostr::Keys` (which caches non-zeroizable copies) and instead parses a raw key string directly into `secp256k1::SecretKey` via `Zeroizing<String>`, while also documenting that `secp256k1::SecretKey` itself lacks `Zeroize` and that residual copies may persist until process exit -- a private key's exposure window is minimized by design in this crate, not eliminated, and the crate says so about itself rather than claiming a stronger guarantee."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs"
  - statement: "`README.md` instructs agents to set `BUZZ_PRIVATE_KEY` and use `buzz-cli` for JSON-in/JSON-out tool calls, and the repository's own `AGENTS.md` states that `BUZZ_RELAY_URL`, `BUZZ_PRIVATE_KEY` and `BUZZ_AUTH_TAG` are auto-injected by the ACP harness into managed agent subprocesses."
    entry_class: FACT
    evidence:
      - "README.md"
      - "AGENTS.md"
  - statement: "Because a private key is the sole credential that lets a principal prove its Nostr public key over NIP-42/NIP-98, and channel membership -- keyed to that public key -- is the relay's only access-control mechanism per `SECURITY.md`'s own security-design section, losing custody of a private key is equivalent to losing the identity itself and every channel membership it holds; there is no separate, independently revocable credential layered on top of it."
    entry_class: INFERENCE
    evidence:
      - "SECURITY.md"
    confidence: 0.75
---

# Private key

The secret credential behind every Nostr identity in Buzz -- human, managed
agent, or CI principal. Whoever holds a private key *is* the identity it
names: understanding what it can do, where Buzz will and will not store it,
and what a signing operation actually exposes is a precondition for reasoning
about identity, authentication or agent custody anywhere else in this corpus.

## Definition

A private key is the secret half of the secp256k1 keypair that gives a Buzz
identity its Nostr public key, and the only value that can produce a valid
signature verifiable under that public key. Buzz's own code and documentation
name this value `nsec` -- Nostr's bech32-encoded secret-key format (NIP-19) --
distinguishing it from `npub`, the paired public identifier. A private key is
not itself an account record, a session token, or anything the relay
maintains state about: it is a bare cryptographic secret that some piece of
client-side or agent-side software holds, and the relay only ever sees what
that secret was used to sign.

**What it is not.** A private key is narrower than a *keypair* -- the paired
public-and-private value together with how it is generated and derived -- and
narrower than a *public key* -- the shareable half that is safe to disclose
and that other principals use to address and verify this identity. This node
covers only the secret value itself: its formats, where Buzz is and is not
willing to store it, and what operations are allowed to touch it. How a
keypair is generated or derived, and how a public key is used once disclosed,
are each their own concept.

## Use cases

- **Authenticating a relay connection (NIP-42).** The client signs a
  `kind:22242` event containing the relay's challenge and URL; the relay
  verifies the signature and never sees the key that produced it.
- **Authenticating a REST request (NIP-98).** The same signing pattern
  applies to HTTP requests against the relay's narrow HTTP surface.
- **Publishing any Nostr event.** Messages, channel metadata, reactions and
  every other event kind Buzz defines are built with the same
  `sign_with_keys` pattern -- the private key never leaves the process that
  holds it, for any event, not only authentication events.
- **Signing Git commits and tags.** The same key, via `git-sign-nostr`, signs
  Git objects with a BIP-340 Schnorr signature, so a Buzz identity's Git
  history and its relay activity are provable under the same credential.
- **Authenticating a managed or harnessed agent.** `BUZZ_PRIVATE_KEY` is how
  the ACP harness gives a spawned agent subprocess (or a developer running
  `buzz-cli` by hand, or CI) its own signing identity, separate from the
  human operator's key.

## Storage and precedence (desktop)

The desktop app resolves a private key in a fixed order, and the earlier tier
always wins over the later one:

| Tier | What it is | When it applies |
|---|---|---|
| `BUZZ_PRIVATE_KEY` env var | Raw key value from the process environment | Harnessed agents, CI, manual dev override -- always takes precedence |
| OS keyring | macOS Keychain / Windows Credential Manager / Linux Secret Service | Default when a keyring backend is reachable |
| Plaintext `identity.key` file | `0o600` owner-only file in the app data directory | Fallback when no keyring backend is reachable |
| Generated | A fresh key, created and saved | No prior key found anywhere above |

The keyring-backed store is deliberately excluded from ever reading the env
var itself -- that precedence is resolved once, upstream, so the two paths
cannot silently disagree with each other. A malformed `BUZZ_PRIVATE_KEY` is
treated as absent (with a logged warning), not as a reason to fall back to an
ephemeral, unsaved identity.

## Boundary

**Against keypair.** A keypair is the *pair* -- how the public and private
halves are generated and relate to each other. This node's subject is
narrower: the private half alone, once it exists.

**Against public key.** A public key is the identity's shareable, disclosable
half; nothing about its handling requires the storage or zeroization
discipline this node describes, because disclosing it is not a security
event. Confusing the two -- treating a public key as sensitive, or a private
key as safe to log or paste -- is exactly the mistake this boundary exists to
prevent.

**Against a session token or API key.** Buzz has no separate, independently
revocable credential layered on top of the private key for relay access;
authentication *is* proving possession of it. Rotating access means rotating
the key itself, not invalidating a token while the underlying secret stays
valid.

## Related resources

- **Keypair** (issue [#1111](https://github.com/launchpad-26/buzz/issues/1111)) and **public key** (issue [#1113](https://github.com/launchpad-26/buzz/issues/1113)) are this node's
  nearest siblings, described above under *Boundary*; neither has merged into
  `origin/launchpad` at this node's recorded revision, so no `relationships`
  edge to either is legal yet (a target must resolve on the branch being
  merged into). A future edit to this node, once they land, should add
  `references` edges to both.
- `SECURITY.md`'s "Desktop Secret Storage" and "Authentication -- NIP-42"
  sections are this node's primary source for custody and signing behavior.
- `crates/git-sign-nostr/src/lib.rs`'s own module documentation is the
  primary source for Git-signing use and its documented zeroization limits.

## Scope and omissions

**This node covers** what a Buzz private key is, the formats and terms Buzz's
own code uses for it, where it may be stored on desktop and in what priority,
what operations a private key performs (signing, never transmission), and its
boundary against the paired keypair and public-key concepts.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a keypair is generated or derived | The keypair node (issue [#1111](https://github.com/launchpad-26/buzz/issues/1111), not yet merged) |
| How a public key is used once disclosed (addressing, verification) | The public-key node (issue [#1113](https://github.com/launchpad-26/buzz/issues/1113), not yet merged) |
| Mobile and CLI-specific key storage (this node evidenced desktop only) | A future node or a scope amendment here, once evidenced |
| The exact set of raw formats `nostr::Keys::parse` accepts (bech32 `nsec` only, versus also raw hex) | Not verified -- the `nostr` crate is an external dependency; this node's evidence stops at Buzz's own call sites and naming, not the crate's internal parser |
| Key rotation and revocation procedure end-to-end | Not evidenced in this pass -- `SECURITY.md`'s migration description covers keyring *migration*, not rotation |
| NIP-42 and NIP-98 protocol mechanics beyond what a private key does within them | The relevant authentication-flow nodes, once they exist |

**Expected but not verified when this node was written:** whether managed
agents' individual keys are resolved through the same `identity_from_env` /
keyring precedence as the human identity key, or through a separate code
path in `managed_agents/` -- `secret_store.rs`'s own documentation states the
keyring "covers both the human identity key and every managed-agent key," but
this node's evidence did not extend to reading the managed-agent resolution
code itself to confirm the precedence order matches exactly.
