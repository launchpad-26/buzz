---
id: platforms-desktop-secure-key-storage
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - reviewer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "SecretStore stores every desktop secret -- the human identity nsec and every managed agent's own nsec -- as a single JSON blob under one keychain entry (service = the store's service name, username = the constant \"secrets\"), so a process needs at most one OS keychain-access prompt for its whole lifetime regardless of how many keys it holds; the module's own doc comment states this is deliberately the same pattern Goose uses."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs:1-21"
      - "desktop/src-tauri/src/secret_store.rs:216-247"
  - statement: "The active OS keyring backend is chosen at compile time by Cargo target-specific dependencies gated behind the system-keyring feature (on by default): Linux links the `keyring` crate's sync-secret-service feature (freedesktop Secret Service over D-Bus), macOS links its apple-native feature (legacy SecKeychain API) for the blob entry plus the separate `security-framework` crate for the Data Protection Keychain used only by one-time legacy migration, and Windows links its windows-native feature; when system-keyring is compiled out, `SecretStore` is unusable and callers fall back to their own 0o600 file storage."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:24-29"
      - "desktop/src-tauri/Cargo.toml:37-67"
      - "desktop/src-tauri/src/secret_store.rs:1-21"
  - statement: "`mutate_blob` acquires a cross-process exclusive advisory lock -- `flock(2)` on a deterministic per-user path `/tmp/buzz-keychain-<uid>-<service>.lock` on Unix, a named kernel mutex on Windows -- before always performing a fresh keychain read, applying the caller's mutation, and writing back; this exists because two concurrent Buzz processes (e.g. a signed release build and an unsigned dev build) share the same keychain blob under the constant service name \"buzz-desktop\", and without re-reading inside the lock a warm in-process cache in one process would silently drop a key written by the other."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs:46-99"
      - "desktop/src-tauri/src/secret_store.rs:394-452"
  - statement: "`keyring_service()` returns the constant \"buzz-desktop\" in release builds and a distinct \"buzz-desktop-dev\" (or a caller-scoped \"buzz-desktop-dev.<name>\" for standalone worktree launches, via the `BUZZ_DEV_KEYRING_SERVICE` env var) in debug builds, so a developer's local build never shares a keychain entry with a signed release build on the same machine."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state_keyring.rs:1-18"
  - statement: "`KeyringProbe` is a three-state enum -- Present, ReachableButEmpty, Unreachable -- returned by `SecretStore::probe`, and the identity-resolution state machine branches on all three so it can distinguish \"no key has ever existed\" from \"the keyring backend is merely down this boot\"; the module doc for the enum states this distinction exists specifically so a transient keyring outage is never treated as license to re-import a leftover plaintext file, which could resurrect a rotated or stale key."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs:27-40"
  - statement: "`resolve_identity_with_store` is the full identity-resolution state machine: on `Present` it loads and parses the stored nsec, detects and adopts a leftover `identity.key` that holds a *different* pubkey (a user re-imported after a prior boot that only wrote the file), and self-heals a missing migration marker; on `ReachableButEmpty` it runs a one-time migration of a leftover `identity.key` with read-back verification before deleting the file, or -- when a migration marker exists but neither the keyring nor a file holds a key -- returns an ephemeral key with `RecoveryState::Lost` rather than silently generating a fresh identity; on `Unreachable` it loads directly from a leftover file without migrating (to avoid resurrecting a rotated key later), or -- when a marker exists but no file does -- returns an ephemeral key with `RecoveryState::KeyringLocked` so the app can still boot while signing stays disabled."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:442-635"
  - statement: "`migrate_identity_file` and `persist_identity_to_keyring` both write an atomically-committed, fsynced migration marker file (one byte, path `identity.migrated` under the app data dir, or `identity.<service>.migrated` for a non-default keyring service per `migration_marker_name`) BEFORE deleting the legacy `identity.key` file that was just imported; the doc comments on both functions state this ordering exists so that a crash between the two steps can never leave \"file gone, no marker\" -- a state indistinguishable from a genuine first launch that would otherwise cause a later keyring-unreachable boot to silently generate and persist a brand-new identity."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:716-841"
      - "desktop/src-tauri/src/app_state.rs:877-899"
      - "desktop/src-tauri/src/app_state_keyring.rs:20-26"
  - statement: "When the `system-keyring` Cargo feature is not compiled in, or a keyring write fails on an availability error, the identity nsec falls back to a plaintext-bech32 file `identity.key` inside the app data directory, written through `atomic-write-file` (temp file + fsync + atomic rename + parent-directory fsync) with Unix file mode set to `0o600` before the secret bytes are written; on Windows no explicit mode is set and the per-user app-data directory ACL is relied on instead."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:422-433"
      - "desktop/src-tauri/src/app_state.rs:1009-1050"
      - "desktop/src-tauri/Cargo.toml:27-29"
  - statement: "`SecretStore::delete_all_with_legacy_cleanup` (the sign-out wipe path) reads the blob to collect every key name it holds, deletes legacy per-key DPK and keyring entries for every one of those names plus \"identity\" and the legacy DPK blob itself, then deletes the main blob entry and clears the in-memory cache -- its own doc comment states this ordering is the fix for an earlier `delete_all` that skipped the per-key cleanup and let a stale legacy entry resurrect an identity on the next boot via `migrate_legacy_key`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs:743-839"
  - statement: "`SecretStore::verify_fully_wiped` re-reads directly from the OS backend, bypassing the in-process cache, and checks all three shapes `load(\"identity\")` could otherwise resurrect (main blob, legacy per-key keyring entry, legacy DPK blob/per-key entry on macOS); any ambiguous error from any of those reads returns `false` (fail-closed) rather than being treated as proof of absence, and only an explicit \"not found\" result counts as verified-absent."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/secret_store.rs:841-898"
  - statement: "`desktop/src-tauri/src/reset.rs`'s `ResetKeychain` trait binds `delete_all_with_legacy_cleanup` and `verify_fully_wiped` as the two operations the boot-time/sign-out reset flow needs, abstracted behind a trait specifically so the wipe-then-verify decision logic is unit-testable against a fake keychain without touching the live OS keyring."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/reset.rs:59-79"
  - statement: "`desktop/src-tauri/src/managed_agents/storage.rs` calls `SecretStore::shared(keyring_service())` -- the same process-global singleton constructor the identity path uses -- to store each managed agent's own nsec under the namespaced key `agent:<pubkey>`, so the human identity key and every agent key share one in-memory cache, one mutex, and one interprocess advisory lock rather than racing independent `SecretStore` instances against the same OS blob."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage.rs:1-33"
      - "desktop/src-tauri/src/secret_store.rs:224-247"
  - statement: "`desktop/src-tauri/src/managed_agents/storage.rs`'s `migrate_inline_key` is the single decision function, shared by a load-time opportunistic re-migration path and the save-time persistence chokepoint, for lifting one agent record's inline nsec into the keyring with read-back verification; it returns a three-state `KeyMigration` (Persisted / KeptInline / Nothing) rather than a boolean specifically so an empty key left by a keyring outage is never mistaken for a key verified present in the keyring."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/storage.rs:133-204"
  - statement: "`IdentityStorage` is a four-variant, `repr(u8)` enum (Ephemeral, SystemKeyring, LocalFile, Environment) held on `AppState` as an `AtomicU8` and surfaced to the Tauri frontend as a lowercase string (e.g. \"system-keyring\") through `IdentityInfo.storage` in the `get_identity` command."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/identity_storage.rs:1-46"
      - "desktop/src-tauri/src/commands/identity.rs:27-51"
  - statement: "The Tauri commands `import_identity` and `persist_current_identity` are the two frontend-facing entry points that durably persist a new or previously-ephemeral identity; both acquire `state.identity_mutation` for their full body so a concurrent import and persist cannot race, and both call `crate::app_state::persist_imported_identity` -- keyring first via `persist_identity_to_keyring`, `0o600` file fallback only when that call returns `Err` -- returning `Err` only when both backends fail."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity.rs:336-389"
      - "desktop/src-tauri/src/commands/identity.rs:466-522"
      - "desktop/src-tauri/src/app_state.rs:843-875"
  - statement: "`architecture-containers-desktop`, already merged on `origin/launchpad`, states at container level that the human owner's identity key \"is held in memory as an AppState field and is durably persisted through one of four backends ... tracked by an explicit IdentityStorage enum,\" citing `app_state.rs`, `identity_storage.rs`, `secret_store.rs` and `Cargo.toml` as one summary bullet; this node is the deeper, component-level elaboration of that single claim and declares `part-of` it rather than restating its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "`node.schema.json`'s `type` enum names `platforms` as one of PRD #602's thirteen enumerated corpus surfaces, and Feature #614 (this node's parent) states its own outcome as \"Relay, desktop, mobile, web, CLI and agent runtime platforms are documented as atomic implementation-facing system views\" -- a per-runtime-platform implementation-facing surface is this node's literal, planned placement (`launchpad/docs/corpus/platforms/desktop/`), not a location this node was placed in and then justified after the fact."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.7
  - statement: "No corpus template exists yet, at the checked revision, whose front matter targets `type: platforms` specifically; `templates/component.md` (subject: one software component, documented as a standalone knowledge artifact -- responsibility, public interface, dependencies) is the closest-fitting existing template for this node's shape, even though its own guidance recommends `type: implementation` for its generic case, because this node's directory placement was already assigned as a `platforms`-surface node by this task's own planning."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.6
  - statement: "Issue #1248's Definition of Done requires that this node state responsibility and a well-defined interface/boundary, name dependencies and collaborators, link source implementation and tests, and explain only component-level behavior rather than the entire desktop platform."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1248 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-desktop
---

# Desktop: secure key storage

How the desktop app durably and confidentially stores private Nostr keys --
the human owner's identity nsec and every managed agent's own nsec -- across
macOS, Windows and Linux, including the OS-keyring-first / plaintext-file-
fallback split, the legacy-migration state machine, and the sign-out wipe
path. This is the component-level elaboration of the one summary bullet
`architecture-containers-desktop` already carries about identity storage; see
*Relationships* below for why it does not restate that bullet's content.

## Responsibility

`desktop/src-tauri/src/secret_store.rs`'s `SecretStore` is the single storage
primitive: every secret the desktop app holds -- the human identity nsec and
every managed agent's nsec -- lives as one entry per key inside a single JSON
blob under one OS keychain entry per service, so a process needs at most one
OS keychain-access prompt for its whole lifetime regardless of how many keys
it stores (`secret_store.rs:1-21`, `secret_store.rs:216-247`). Two call sites
build on top of `SecretStore`: `desktop/src-tauri/src/app_state.rs` owns the
human identity's resolve/generate/migrate state machine, and
`desktop/src-tauri/src/managed_agents/storage.rs` owns the same lifecycle for
each managed agent's own key, sharing the identity path's `SecretStore`
instance rather than opening a second one (`managed_agents/storage.rs:1-33`).

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `SecretStore::probe` | fn | Returns `KeyringProbe::{Present, ReachableButEmpty, Unreachable}` for one key name, without side effects. | `secret_store.rs:27-40`, `secret_store.rs:476-502` |
| `SecretStore::load` / `SecretStore::load_all_readonly` | fn | `load` may trigger one-time legacy-format migration as a side effect; `load_all_readonly` never does. | `secret_store.rs:540-594` |
| `SecretStore::store` / `SecretStore::store_all` | fn | Writes one or many keys into the blob; skips the durable write entirely when the candidate equals the freshly-read blob (avoids an unnecessary macOS keychain ACL prompt). | `secret_store.rs:394-452`, `secret_store.rs:596-615`, `secret_store.rs:727-741` |
| `SecretStore::verify_stored_raw` | fn | Reads directly from the OS backend, bypassing the in-process cache, to prove a value was durably written -- used before deleting any plaintext source it was migrated from. | `secret_store.rs:697-725` |
| `SecretStore::delete` / `delete_all_with_legacy_cleanup` | fn | `delete` removes one key (plus its legacy shapes); `delete_all_with_legacy_cleanup` is the sign-out wipe of every key plus every legacy shape. | `secret_store.rs:743-839`, `secret_store.rs:900-921` |
| `SecretStore::verify_fully_wiped` | fn | Fail-closed proof that no identity-bearing entry, in any shape `load` could resurrect, remains after a wipe. | `secret_store.rs:841-898` |
| `IdentityStorage` (enum) | type | Ephemeral / SystemKeyring / LocalFile / Environment; held as `AtomicU8` on `AppState`, surfaced to the frontend as a string. | `identity_storage.rs:1-46` |
| `get_identity` (Tauri command) | fn | Reports the active `pubkey`, display name, current `IdentityStorage` as a string, and the `lost`/`locked`/`reset_failed` recovery flags. | `commands/identity.rs:27-51` |
| `import_identity`, `persist_current_identity` (Tauri commands) | fn | Durably persist a supplied or previously-ephemeral identity: keyring first, `0o600` file fallback on keyring failure; both hold `state.identity_mutation` for their full body. | `commands/identity.rs:336-389`, `commands/identity.rs:466-522` |
| `sign_out` (Tauri command) | fn | Writes a boot-reset sentinel; the actual wipe (via `ResetKeychain`) runs on the next boot, before migrations or identity resolution. | `commands/identity.rs:536-562`, `reset.rs:59-135` |

## Backend selection

The active OS keyring backend is chosen at Cargo compile time, gated behind
the `system-keyring` feature (on by default; `Cargo.toml:24-29`):

| Target | Backend for the blob entry | Notes |
|---|---|---|
| Linux | `keyring` crate, `sync-secret-service` feature (freedesktop Secret Service over D-Bus) | `Cargo.toml:37-42` |
| macOS | `keyring` crate, `apple-native` feature (legacy `SecKeychain` API) | Chosen deliberately over the newer Data Protection Keychain so signed release and unsigned dev builds share one store; `security-framework`'s DPK API is used only by the one-time legacy-migration path. `Cargo.toml:53-60`, `secret_store.rs:1-21`, `secret_store.rs:268-299` |
| Windows | `keyring` crate, `windows-native` feature | `Cargo.toml:65-67` |

When `system-keyring` is not compiled in, `SecretStore` is unusable and every
caller falls back to its own `0o600`-permission plaintext file
(`secret_store.rs:1-21`, `app_state.rs:422-433`).

## Identity resolution and legacy migration

`app_state::resolve_identity_with_store` is the state machine that decides,
on every boot, where the human identity key comes from
(`app_state.rs:442-635`):

- **Keyring `Present`** -- load and parse the stored nsec; if a leftover
  `identity.key` file also exists and holds a *different* pubkey, adopt the
  file's key into the keyring (the user re-imported after an older boot that
  only wrote the file); if it holds the *same* pubkey, it is a stale leftover
  and gets cleaned up; a missing migration marker is self-healed.
- **Keyring `ReachableButEmpty`** -- if a leftover `identity.key` exists, run
  a one-time migration: write the nsec into the keyring, read it back
  directly from the OS backend to verify the round-trip, write an atomically
  committed migration marker, and only then delete the file
  (`app_state.rs:716-767`, `app_state.rs:769-841`). If no file exists but the
  migration marker does, the prior identity is gone from both backends: the
  app boots on an ephemeral key with `RecoveryState::Lost` rather than
  silently generating a new identity.
- **Keyring `Unreachable`** -- load directly from a leftover file without
  migrating (migrating now could later resurrect a rotated key once the
  keyring returns); with no file and a migration marker present, boot on an
  ephemeral key with `RecoveryState::KeyringLocked` so the app can still open
  while all signing stays disabled.

The migration marker (`app_state.rs:877-899`, named via
`app_state_keyring::migration_marker_name`, `app_state_keyring.rs:20-26`) is
what makes an `Unreachable`-with-no-file boot distinguishable from a genuine
first launch: it is always written, fsynced and committed *before* the
legacy file is deleted, so a crash between the two steps can never produce
"file gone, no marker" -- a state that would otherwise look identical to a
fresh install and cause a silent identity rotation.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `keyring` crate (per-target features) | The OS keyring backend abstraction for the blob entry. | `Cargo.toml:29,42,59,67` |
| `security-framework` crate (macOS only) | Data Protection Keychain access, used only by the legacy per-key migration path. | `Cargo.toml:60` |
| `windows-sys` crate (Windows only) | The named-mutex interprocess lock primitive. | `Cargo.toml:66` |
| `libc` crate (Unix only) | `flock(2)` for the interprocess advisory lock, and `getuid()` for the per-user lockfile path. | `Cargo.toml:38` |
| `atomic-write-file` crate | Atomic, fsynced writes for both the `0o600` identity file and the migration marker. | `app_state.rs:891-899`, `app_state.rs:1027-1050` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `managed_agents::storage` | Stores and migrates every managed agent's own nsec through the same `SecretStore::shared` instance, namespaced `agent:<pubkey>`. | `managed_agents/storage.rs:1-33`, `managed_agents/storage.rs:133-204` |
| `reset` (sign-out / boot-time wipe) | Wipes and verifies the keychain via the `ResetKeychain` trait bound to `SecretStore`. | `reset.rs:59-79` |
| `commands::identity` (Tauri commands) | The frontend-facing surface: `get_identity`, `import_identity`, `persist_current_identity`, `sign_out`. | `commands/identity.rs:27-51`, `commands/identity.rs:336-522` |

## Boundary

This node does not describe:
- The desktop container's full architecture (relay connection, media proxy,
  managed-agent process spawning, CSP, release lane, and so on) -- see
  `architecture-containers-desktop` for the container-level view this node
  is `part-of`.
- How a managed agent's identity is *used* once persisted (spawn-time env
  injection, reserved-key protection) -- that is `architecture-containers-
  desktop`'s own claim and `managed_agents::runtime`'s concern, not this
  node's.
- Mobile or web key storage. Each runtime platform's own storage mechanism,
  if and when documented, is a separate `platforms/` node.
- The NIP-49 passphrase-encrypted key-backup format (`identity.ncryptsec`,
  referenced by `commands/identity.rs`'s `key_backup` module) -- a distinct
  export/backup mechanism from the live storage this node covers.

## Relationships

- part-of: `architecture-containers-desktop`

## Scope and omissions

**This node covers** the desktop app's secure key storage component: the
OS-keyring-first / `0o600`-file-fallback split and per-platform backend
choice, the interprocess advisory lock protecting the shared keychain blob,
the identity-resolution and legacy-migration state machine including its
crash-safety ordering, the sign-out wipe-and-verify path, and this
component's dependencies and dependents.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The desktop container's full architecture | `architecture-containers-desktop` |
| How a persisted agent key is used at process-spawn time | `managed_agents::runtime` (no corpus node yet at this revision) |
| The NIP-49 encrypted key-backup/export format | Not yet a corpus node at this revision |
| Mobile/web equivalent key storage | Separate `platforms/` nodes, not yet authored |
| Whether `type: platforms` is the enum's best long-term fit for a node this granular, versus `type: implementation` | Flagged here per `standards/taxonomy.md`'s own disclosure guidance; not resolved because no `platforms`-specific standard or template exists yet at this revision |

**Expected but not verified when this node was written:**
- The Linux Secret Service backend's actual runtime behavior (D-Bus
  availability, keyring-unlock prompts) was not exercised on a live Linux
  desktop session -- this node's Linux claims rest on the `Cargo.toml`
  feature wiring and the backend-agnostic `keyring` crate contract, not on an
  observed run.
- Whether every one of `secret_store.rs`'s `#[ignore]`d real-keychain
  integration tests (cross-process race, blob migration, full wipe) passes
  on a machine with a reachable keychain was not re-run for this node; their
  presence and stated intent were read, not their live pass/fail result.
