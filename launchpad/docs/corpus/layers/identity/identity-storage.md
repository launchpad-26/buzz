---
id: layers-identity-identity-storage
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
  - statement: "No `layers`-specific corpus template exists in `launchpad/docs/corpus/templates/` at the recorded revision (26 templates present, covering architecture/component/capability/etc. shapes but none named `layers*`), so this node is hand-authored directly against `node.schema.json`, following the same no-template path `AGENTS.md` documents and that sibling node `layers-identity-human-identity` (issue #1106) already took."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "desktop/src-tauri/src/secret_store.rs's `SecretStore` is the desktop app's single OS-keychain-backed store: every secret for a given `service` (in practice only `\"buzz-desktop\"`) is kept as one JSON blob under one keychain entry, so the OS prompts the user once per process lifetime rather than once per key; the active backend (Data Protection Keychain or the legacy `keyring` crate on macOS, the `keyring` crate directly on Windows/Linux) is selected at compile time, and cross-process safety is enforced by an advisory `flock`/named-mutex lock (`acquire_blob_lock`/`BlobLockGuard`) keyed by service name."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
  - statement: "`SecretStore` also handles a one-time migration off an older per-key-entry format (`migrate_legacy_key`) and, on sign-out, `delete_all_with_legacy_cleanup` removes the blob plus every legacy per-key entry so a stale entry cannot resurrect an identity on next boot; `verify_fully_wiped` fails closed (returns `false`, i.e. \"not confirmed wiped\") if the keychain is unreachable rather than assuming success."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
  - statement: "desktop/src-tauri/src/managed_agents/storage.rs stores each locally-spawned managed agent's nsec under the key `agent_keyring_name(pubkey)` (a `\"agent:<pubkey>\"`-style name namespaced from the human identity's own `\"identity\"` key) in the same shared `SecretStore` instance used for the owner's own identity, so both share one in-memory cache and mutex and cannot race each other on a blob write."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage.rs"
  - statement: "When the OS keyring is reachable, `migrate_inline_key`/`persist_agent_keys` write an agent's key to the keyring, read it back to verify, and only then strip the plaintext copy from the agent's JSON record before it is serialized; when the keyring is unreachable, the key stays inline in `managed-agents.json`, which `atomic_write_json_restricted` creates with `0o600` permissions set at file-creation time (not chmod'd afterward) specifically because that file \"carries plaintext agent nsecs in the keyringless fallback\"; `spawn_key_refusal` refuses to launch any agent whose resolved key is empty, since an empty key after `hydrate_keys` means a keyring outage or a genuinely absent secret, never a deliberately keyless agent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage.rs"
  - statement: "mobile/lib/shared/community/community_storage.dart's `CommunityStorage` keeps every community's credentials, including each community's own optional `nsec` field on its `Community` object, JSON-encoded together as a single `flutter_secure_storage` entry under the key `buzz_communities` (`_saveList`/`loadAll`) — not one secure-storage entry per community or per key. A legacy migration path folds forward both an older multi-community format and a still-older single-community format (`buzz_nsec`, `buzz_pubkey`, `buzz_relay_url`, `buzz_token` legacy keys), deleting the legacy entries once the migrated data is written."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart"
  - statement: "crates/buzz-cli/src/lib.rs's `Cli.private_key` field is sourced from the `--private-key` flag or the `BUZZ_PRIVATE_KEY` environment variable (clap `env = \"BUZZ_PRIVATE_KEY\", hide_env_values = true`), is required for every relay operation (\"Auth: private key is required for all relay operations. The keypair IS the identity — no tokens, no other auth\"), and is parsed fresh via `Keys::parse` on each invocation; the CLI process itself never writes the key to disk, so its only \"storage\" is whatever the caller's own shell/environment/secret manager provides before invocation."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
  - statement: "crates/buzz-backend-kubernetes/src/env.rs's `AUTHORITATIVE_KEYS` list includes `BUZZ_PRIVATE_KEY` and `NOSTR_PRIVATE_KEY`; `build_env` writes both from `agent.private_key_nsec` (`env.insert(\"BUZZ_PRIVATE_KEY\".into(), agent.private_key_nsec.clone())`) into the environment that becomes a Kubernetes Secret referenced by the deployed pod's `envFrom` — the provider process (`buzz-backend-kubernetes`, invoked one-process-per-operation with a JSON request on stdin per `main.rs`'s module doc) never itself writes the key to its own disk; it only ever holds it in memory for the duration of one `deploy` call."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/env.rs"
      - "crates/buzz-backend-kubernetes/src/main.rs"
  - statement: "docs/remote-agents.md's System Model states the Desktop app `D` \"Holds the agent's identity (nsec in the OS keyring)\" and is the sole principal trusted with it; invariant I2 (\"No secrets in configuration\") states secrets \"flow exclusively inside the `deploy` payload (`private_key_nsec`, `auth_tag`, `env_vars`), which is never persisted by `D` and never rendered\" to the provider-config UI; the residual-exposure statement for the Kubernetes binding is explicit: \"any principal with pod-exec or secret-read in the namespace can read the nsec\" once it is materialized as a Kubernetes Secret, which the document treats as substrate-level RBAC exposure rather than something Buzz's own protocol further encrypts."
    entry_class: FACT
    evidence:
      - "docs/remote-agents.md"
  - statement: "crates/buzz-dev-mcp/src/shim.rs's `write_keyfile_atomic` materializes a session-scoped `.nostr-key` file with `0o600` permissions (mode set at creation, per `OpenOptions`) from whatever raw key the shim received, so that git helpers (git-sign-nostr, git-credential-nostr) read the key from this keyfile rather than from the process environment directly; crates/git-sign-nostr/src/lib.rs's key resolution reads `NOSTR_PRIVATE_KEY` first, then `BUZZ_PRIVATE_KEY`, and calls `std::env::remove_var` on whichever it consumed immediately after reading it, so the raw key does not linger in that process's own environment block."
    entry_class: FACT
    evidence:
      - "crates/buzz-dev-mcp/src/shim.rs"
      - "crates/git-sign-nostr/src/lib.rs"
  - statement: "crates/buzz-core/src/kind.rs declares `KIND_PRIVATE_MANAGED_AGENT: u32 = 30179` (\"NIP-PMA: owner-encrypted private managed-agent aggregate\"), and crates/buzz-core/src/private_managed_agent.rs defines a `Payload`/`ActivePayload`/`PrivateIdentity` codec whose `PrivateIdentity.private_key_nsec` field is the same shape of secret described above, encrypted NIP-44 v2 from the owner's key to itself (`build_event`/`validate_and_decrypt`) so that, once live, a managed agent's private key could be synced durably through the relay as ciphertext the relay itself cannot read — this is a defined-but-not-yet-live storage/sync path, not one of the storage locations described above that is actually reachable today."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-core/src/private_managed_agent.rs"
  - statement: "docs/nips/NIP-PMA.md's \"Required deployment order\" lists eight phases, of which phase 1 is \"this inert codec/kind reservation while ingest still rejects `30179`\" and phase 8 (\"Desktop reader and verified dual-write migration\") is the phase where the Desktop app would actually start reading/writing this format; a repository-wide search for callers of `private_managed_agent::validate_and_decrypt`/`build_event`/`PrivateIdentity` outside the module's own unit tests and one relay-side kind-classification test found none, consistent with the deployment order's own statement that the relay currently rejects ingest of kind `30179` rather than storing or serving it."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-PMA.md"
  - statement: "desktop/src-tauri/src/identity_storage.rs's `IdentityStorage` enum (`Ephemeral`=0, `SystemKeyring`=1, `LocalFile`=2, `Environment`=3) names the four possible backends for the desktop app's active human identity key, stored on `AppState` as an `AtomicU8` (`identity_storage`/`set_identity_storage`) so any command can read the active backend without locking the identity mutex; `RecoveryState` (`None`/`Lost`/`KeyringLocked`) and `ResolvedIdentity` (a `Keys`/`RecoveryState`/`IdentityStorage` bundle) are the other two types startup identity resolution produces."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/identity_storage.rs:6-33"
      - "desktop/src-tauri/src/identity_storage.rs:49-62"
  - statement: "desktop/src-tauri/src/app_state.rs implements the actual fallback chain in strict priority order at startup: `build_app_state`'s `identity_from_env` check wins outright over any persisted key when `BUZZ_PRIVATE_KEY` is set and parses (`IdentityStorage::Environment`), and a malformed value is logged and treated as absent rather than left ephemeral; otherwise `resolve_persisted_identity` calls `load_or_create_identity`, which probes the OS keyring (`IdentityStorage::SystemKeyring`) when the `system-keyring` Cargo feature is compiled in; the `0o600` `identity.key` file is the fallback (`IdentityStorage::LocalFile`) when that feature is absent, when the keyring is unreachable with a recoverable file, or when a keyring write fails during generation or import; and an in-memory `Keys::generate()` (`IdentityStorage::Ephemeral`) is the last resort."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:142-157"
      - "desktop/src-tauri/src/app_state.rs:180-192"
      - "desktop/src-tauri/src/app_state.rs:358-389"
      - "desktop/src-tauri/src/app_state.rs:447-462"
  - statement: "`resolve_identity_with_store` (app_state.rs) branches on `IdentityKeyStore::probe`'s three-way `KeyringProbe` result rather than a single try/fallback: `Present` with a parseable nsec resolves to `SystemKeyring` immediately and falls through to `recover_from_keyring` only on a parse failure; `ReachableButEmpty` one-time-migrates a leftover `identity.key` via `migrate_identity_file` (store, read-back verify, then delete) or, with the migration marker present and no file to recover, returns an ephemeral key with `RecoveryState::Lost`; `Unreachable` uses a leftover file directly without migrating it (`load_file_or_generate`, since migrating a stale file this late could resurrect a rotated key) or, with the marker present and no file, returns an ephemeral key with `RecoveryState::KeyringLocked`; and a genuine first launch (no keyring value, no file, no marker) falls through to `generate_and_persist`, which resolves to `SystemKeyring` or `LocalFile` via `store_key_preferring_keyring` depending on whether the keyring write succeeds -- never to `Ephemeral`, which is reserved for the two recovery states above."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:467-660"
      - "desktop/src-tauri/src/app_state.rs:933-955"
      - "desktop/src-tauri/src/app_state.rs:962-979"
  - statement: "Across the desktop keychain blob, the mobile secure-storage blob, the CLI's env-var-only handling, and the dev-mcp session keyfile, the pattern each surface independently converges on is: the raw private key is durably written to at most one place by exactly one component for exactly one purpose, and every hop after that (subprocess env for the ACP harness, a Kubernetes Secret for a remote pod) either avoids writing the key to a file at all or writes it once with restrictive permissions and strips it from the environment that produced it once its consumer has read it."
    entry_class: INFERENCE
    evidence:
      - "desktop/src-tauri/src/secret_store.rs"
      - "desktop/src-tauri/src/managed_agents/storage.rs"
      - "mobile/lib/shared/community/community_storage.dart"
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-dev-mcp/src/shim.rs"
      - "crates/git-sign-nostr/src/lib.rs"
    confidence: 0.7
  - statement: "Issue #1110's definition of done requires this node to define the term in one sentence before deeper explanation, state boundaries/non-goals, link related concepts, implementation and verification without duplicating their content, and use examples only to clarify the concept rather than introduce a second canonical concept; the issue's objective separately describes the node as \"the single canonical concept node for identity storage,\" but neither the objective nor the DoD checklist names sibling node #1106 (human-identity) or states that #1106 should reference this node rather than duplicate it -- that expectation is inferred from the DoD's general anti-duplication requirement plus this node's own single-canonical-treatment framing, not a literal statement in the issue text."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/1110"
    confidence: 0.7
---

# Identity Storage

**Identity storage** is where and how a Nostr private key (`nsec`) — the sole material
that proves control of an identity in Buzz — is kept at rest and in transit, across
every surface that holds one: desktop, mobile, the CLI, and the server/remote-agent
launch path. This node is the single canonical, cross-surface treatment of that
question; it does not restate how identity is *represented* on the relay (kind:0
profile sync, the `users` table) — that is `layers-identity-human-identity`'s subject
(issue #1106, not yet merged — see *Related resources* below).

## Boundaries and non-goals

This node is about **custody of the raw key material**, not about:

- How a human or agent identity is *represented* to the rest of the system (kind:0
  profile sync, the community-scoped `users` table) — `layers-identity-human-identity`'s
  subject.
- Authentication mechanics (NIP-42 for humans, NIP-98/NIP-OA for agents) — a separate
  concern from where the key that signs those challenges is stored.
- The Kubernetes deploy state machine, Secret garbage collection, or reconciliation
  loop — `docs/remote-agents.md`'s own subject, cited below only for the one fact that
  matters here (where the key sits at each hop).
- Kubernetes' own Secret-at-rest encryption in etcd — a cluster-operator/substrate
  concern `docs/remote-agents.md` itself places out of scope (`§Non-Goals`), not
  something Buzz's own protocol adds encryption on top of.

## Desktop: single OS-keychain blob

The desktop app keeps every secret for one `service` — in practice always
`"buzz-desktop"` — as **one JSON blob under one OS keychain entry**
(`secret_store.rs`'s `SecretStore`), so the OS prompts the user once per process
lifetime rather than once per secret. The active backend is chosen at compile time:
the Data Protection Keychain or the legacy `keyring` crate on macOS (the DPK path
needs a hardened-runtime entitlement that unsigned dev builds lack, so those fall back
to the legacy path), and the `keyring` crate directly on Windows and Linux.
Cross-process safety is enforced by an advisory lock (`flock` on Unix, a named kernel
mutex on Windows) so a GUI-launched build and a terminal-launched dev build contend on
the same lock rather than racing a read-modify-write of the blob.

`managed_agents/storage.rs` stores each **locally-spawned managed agent's** nsec in
that same shared `SecretStore` instance, under a key namespaced from the human
identity's own `"identity"` entry (`agent_keyring_name(pubkey)`), so agent and owner
keys share one cache/mutex and cannot last-writer-wins race each other. Persisting an
agent's key is write-then-verify-then-strip: `migrate_inline_key`/`persist_agent_keys`
write the key to the keyring, read it back to confirm, and only then remove the
plaintext copy from the agent's JSON record before that record is serialized. If the
keyring is unreachable, the key stays **inline** in `managed-agents.json` — a file
`atomic_write_json_restricted` creates with `0o600` permissions set at creation (not
chmod'd afterward, closing the umask window) specifically because, in that fallback,
the file "carries plaintext agent nsecs." `spawn_key_refusal` refuses to launch any
agent whose resolved key is empty — after `hydrate_keys` runs, an empty key means a
keyring outage or a genuinely absent secret, never a deliberately keyless agent, so
spawning anyway would silently launch an agent with no identity.

Sign-out uses `delete_all_with_legacy_cleanup`, which removes the blob plus every
legacy per-key entry (so a stale entry cannot resurrect an identity on the next boot),
and `verify_fully_wiped` fails **closed**: if the keychain is unreachable it reports
"not confirmed wiped" rather than assuming success.

## Desktop: startup resolution fallback chain

The `SecretStore` blob above is where the human identity key ends up once resolved --
but resolving *which* key that is, and *where* it currently lives, happens earlier, at
startup. `identity_storage.rs` names the four possible answers as `IdentityStorage`
(`Ephemeral`, `SystemKeyring`, `LocalFile`, `Environment`), tracked on `AppState` as an
`AtomicU8` so any command can read the active backend without locking the identity
mutex, alongside `RecoveryState` (`None`, `Lost`, `KeyringLocked`) and `ResolvedIdentity`
(the `Keys`/`RecoveryState`/`IdentityStorage` bundle resolution produces).

`app_state.rs` implements the actual chain, in strict priority order, once per boot:

1. **Environment.** `build_app_state`'s `identity_from_env` check runs first: if
   `BUZZ_PRIVATE_KEY` is set and parses, it wins outright over any persisted key (the
   dev/CI/harness override) and resolution stops here. A malformed value is logged and
   treated as absent rather than left on an ephemeral identity -- it falls through to
   the next tier instead.
2. **SystemKeyring.** With no env override, `resolve_persisted_identity` calls
   `load_or_create_identity`, which -- when the `system-keyring` Cargo feature is
   compiled in -- probes the OS keyring through a three-way `KeyringProbe`. A
   `Present`, parseable key resolves to `SystemKeyring` immediately, with no
   fall-through to lower tiers.
3. **LocalFile.** The `0o600` `identity.key` file backs three distinct paths to this
   tier: the `system-keyring` feature not being compiled in at all (the file is the
   only store); the keyring being `Unreachable` this boot with a leftover file present
   (`load_file_or_generate` reads it directly and deliberately does **not** migrate it
   into the keyring -- a stale file could resurrect a rotated key, so migration retries
   next boot when the keyring is reachable again); and a keyring *write* failing during
   key generation (`store_key_preferring_keyring`) or import
   (`persist_identity_to_keyring`), which demotes the outcome to `LocalFile` rather
   than failing startup.
4. **Ephemeral.** The last resort: an in-memory-only `Keys::generate()` with nothing
   ever persisted under it, reserved for two specific unrecoverable-this-boot states
   rather than for creating a new identity -- `ReachableButEmpty` with the migration
   marker present but no importable file (`RecoveryState::Lost`: a prior identity
   existed and is now gone), and `Unreachable` with the marker present but no file
   (`RecoveryState::KeyringLocked`: the prior identity still exists in the keyring,
   merely inaccessible this boot). `AppState.identity_lost`/`keyring_locked` (set from
   `RecoveryState` in `resolve_persisted_identity`) drive distinct frontend recovery
   screens for the two cases.

A genuine first-ever launch -- no keyring value, no leftover file, no migration
marker -- falls through all of the above to `generate_and_persist`, which resolves to
`SystemKeyring` or `LocalFile` via `store_key_preferring_keyring` depending on whether
the keyring write succeeds. It never lands on `Ephemeral`: that backend is reserved
exclusively for the two recovery scenarios above, not the normal case of creating a
brand-new identity.

## Mobile: one secure-storage blob for all communities

`mobile/lib/shared/community/community_storage.dart`'s `CommunityStorage` keeps every
community's credentials — including each community's own optional `nsec` — JSON-encoded
together as **one `flutter_secure_storage` entry** under the key `buzz_communities`
(`_saveList`/`loadAll`), not one secure-storage entry per community or per key. A
migration path folds forward both an older multi-community shape and a still-older
single-community shape (legacy keys `buzz_nsec`, `buzz_pubkey`, `buzz_relay_url`,
`buzz_token`), deleting the legacy entries once the migrated data is written.

## CLI: environment only, never persisted

`buzz-cli`'s `Cli.private_key` is sourced from the `--private-key` flag or the
`BUZZ_PRIVATE_KEY` environment variable (`hide_env_values = true` so clap never echoes
it in `--help` or error text), and is required for every relay operation — "the keypair
IS the identity — no tokens, no other auth." It is parsed fresh via `Keys::parse` on
each invocation. The CLI process itself never writes the key to disk; its only
"storage" is whatever the caller's shell, `.env` file, or secret manager provides
before invocation, which is out of this node's control and not described here.

## Server-managed / remote-agent launch: in-memory only, then a Kubernetes Secret

For an agent the desktop launches **locally**, its key is hydrated from the desktop's
own keychain (above) directly into the spawned subprocess's environment — the ACP
harness reads `BUZZ_PRIVATE_KEY`/equivalent from its own process environment.

For an agent the desktop deploys to a **remote substrate** (the Kubernetes binding is
the one implemented in this repository), `docs/remote-agents.md`'s System Model states
plainly that the desktop app `D` "Holds the agent's identity (nsec in the OS keyring)"
and is the only principal trusted with it. Its invariant **I2 ("No secrets in
configuration")** states that secrets "flow exclusively inside the `deploy` payload
(`private_key_nsec`, `auth_tag`, `env_vars`), which is never persisted by `D` and never
rendered" anywhere in the persisted, UI-visible provider configuration. The provider
process (`buzz-backend-kubernetes`, invoked one-process-per-operation with a JSON
request on stdin and a JSON response on stdout, per `main.rs`) receives the key in that
one request, writes it into the environment that becomes a Kubernetes Secret
(`env.rs`'s `AUTHORITATIVE_KEYS` includes `BUZZ_PRIVATE_KEY` and `NOSTR_PRIVATE_KEY`,
both set from `agent.private_key_nsec`), and never itself persists it to disk — it only
holds it in memory for the duration of that one `deploy` call.

Once materialized as a Kubernetes Secret, the key's at-rest exposure is a substrate/RBAC
question the spec states explicitly rather than hides: "any principal with pod-exec or
secret-read in the namespace can read the nsec." Buzz's own protocol does not add a
further encryption layer on top of the Secret; that residual exposure is accepted and
documented, not solved, by `docs/remote-agents.md`.

## Agent runtime: an ephemeral 0o600 keyfile for git signing

Inside a running agent's environment, `buzz-dev-mcp`'s shim (`shim.rs`) re-materializes
the key **once more**, in a different shape, for the git credential/signing helpers
(`git-sign-nostr`, `git-credential-nostr`): `write_keyfile_atomic` writes a
session-scoped `.nostr-key` file with `0o600` permissions set at creation, and those
git helpers read the key from that keyfile rather than from the process environment.
`git-sign-nostr`'s own key resolution (checked independently of the shim, since the
helper can also be invoked directly) reads `NOSTR_PRIVATE_KEY` first, then
`BUZZ_PRIVATE_KEY`, and calls `std::env::remove_var` on whichever it consumed
immediately after reading it — so the raw key does not linger in that process's own
environment block once it has been captured.

## Not yet live: an encrypted-at-rest sync format on the relay (NIP-PMA)

`buzz-core` defines kind `30179` (`KIND_PRIVATE_MANAGED_AGENT`, "NIP-PMA": owner-
encrypted private managed-agent aggregate) and a `PrivateIdentity`/`ActivePayload`/
`Payload` codec whose `PrivateIdentity.private_key_nsec` field carries the same shape
of secret described throughout this node, NIP-44 v2 encrypted from the owner's key to
itself. Once live, this would let a managed agent's private key be synced durably
through the relay — as ciphertext only, which the relay cannot decrypt — rather than
existing only on the one desktop machine that spawned it. **This path is defined but
not yet reachable**: `docs/nips/NIP-PMA.md`'s required deployment order states phase 1
is "this inert codec/kind reservation while ingest still rejects `30179`," and phase 8
("Desktop reader and verified dual-write migration") — the phase where the desktop
would actually start reading and writing this format — has not landed. No caller of
`private_managed_agent::validate_and_decrypt`/`build_event`/`PrivateIdentity` was found
anywhere in the repository outside the module's own unit tests and one relay-side
kind-classification test, consistent with the ingest rejection the deployment order
itself describes.

## Comparison

| Surface | What's stored | Where | Granularity |
|---|---|---|---|
| Desktop (owner + local agents) | nsec, keyed by identity/agent pubkey | Resolved at startup via a fallback chain (`identity_storage.rs`/`app_state.rs`: `Environment` → `SystemKeyring` → `LocalFile` → `Ephemeral`), then held in one OS-keychain blob per `service` (`secret_store.rs`); `0o600` `managed-agents.json` inline fallback only when the keyring is unreachable | One blob for everything under that service |
| Mobile | nsec, per community | One `flutter_secure_storage` entry (`buzz_communities`) holding all communities' credentials | One blob for every community |
| CLI | nsec | Not stored by the CLI itself — read fresh from `--private-key`/`BUZZ_PRIVATE_KEY` on each invocation | N/A — caller's environment |
| Remote agent (Kubernetes) | nsec, in transit then at rest as a Secret | In-memory only across `D`→`P`; a Kubernetes Secret at the substrate (`env.rs`) | One Secret per deploy generation |
| Agent runtime (git signing) | nsec, ephemeral copy | A session-scoped `0o600` `.nostr-key` file (`shim.rs`) | One keyfile per dev-mcp session |
| Relay (NIP-PMA, not yet live) | nsec, NIP-44 v2 ciphertext | A kind `30179` event, ingest currently rejected | N/A — inert reservation only |

## Related resources

This node currently carries no `relationships` entries: at the recorded revision, no
sibling `layers/identity/*` node — including `layers-identity-human-identity`
(issue #1106), which briefly touches desktop/mobile custody in passing — is merged on
`origin/launchpad` yet (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` shows no `layers/` path at all). Once #1106 merges, its
document should be updated to `references` this node for identity-storage mechanics
rather than duplicating them, per this node's own definition-of-done intent; that
update belongs to #1106's own PR, not this one, since it lives in a different
worktree.

## Scope and omissions

**This document covers** where and how the raw Nostr private key is kept at rest and
in transit across desktop, mobile, the CLI, the server/remote-agent launch path, and
an agent's own git-signing runtime, plus one not-yet-live relay-side sync format
reserved for the same purpose. On desktop, this includes both the at-rest blob
(`secret_store.rs`) and the startup fallback chain that decides which backend and
which key are active in the first place (`identity_storage.rs`/`app_state.rs`).

**This document does not cover, deliberately:**

- How identity is represented publicly (kind:0 profile sync, the `users` table) —
  `layers-identity-human-identity`'s subject.
- Authentication/authorization mechanics (NIP-42, NIP-98, NIP-OA auth tags).
- The Kubernetes deploy state machine, Secret garbage collection, reconciliation, or
  fingerprinting — `docs/remote-agents.md`'s own subject beyond the one fact needed
  here (where the key sits at each hop).
- Any non-Kubernetes remote-agent binding (e.g. `sprout-backend-blox`, a systemd/SSH
  deployer referenced in `docs/remote-agents.md` as "the live example" of a
  third-party binding) — out of this repository's source tree.

**Expected but not verified when this node was written:**

- Whether every desktop code path that ever holds a raw key in a local variable
  scrubs it from memory (as opposed to only from disk/env) was not investigated —
  this node describes storage locations, not in-process memory hygiene.
- Whether Android Keystore / iOS Secure Enclave hardware backing is actually enabled
  for `flutter_secure_storage`'s default configuration, versus a software-only
  fallback, was not inspected — only that the package and its single-blob usage are
  confirmed.
- Whether any non-Kubernetes provider binding that may exist outside this repository
  (per `docs/remote-agents.md`'s "provider" abstraction) follows the same
  in-memory-only, never-persisted discipline `buzz-backend-kubernetes` follows — only
  the one binding present in this repository was inspected.
