---
id: capabilities-onboarding-first-identity
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "On desktop, `build_app_state` gives every process an in-memory identity immediately at startup: `BUZZ_PRIVATE_KEY` if set and parseable, otherwise a fresh ephemeral `Keys::generate()` keypair used only until `resolve_persisted_identity` runs later in `setup()`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:140-155"
      - "desktop/src-tauri/src/app_state.rs:178-190"
  - statement: "`resolve_persisted_identity` resolves the durable identity in priority order — `BUZZ_PRIVATE_KEY` env var (already handled), OS keyring, `{app_data_dir}/identity.key` file, then generate-and-save — and writes the result into `AppState.keys` before setting the `identity_lost`/`keyring_locked` recovery flags, so a genuine first-ever launch (no key anywhere) generates and persists a brand-new keypair with no recovery flag set."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:315-361"
      - "desktop/src-tauri/src/app_state.rs:422-437"
  - statement: "`resolve_identity_with_store` disambiguates a genuine first launch from a post-migration boot with an unreachable or emptied keyring using a durable `identity.migrated` marker file: keyring reachable-but-empty plus marker present means the identity is lost (boots an ephemeral key with `RecoveryState::Lost`, awaiting re-import) rather than silently generating a replacement, while keyring reachable-but-empty with no marker and no legacy file falls through to `generate_and_persist` as a legitimate first run."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:442-591"
  - statement: "The same first-launch-vs-locked disambiguation applies when the keyring is unreachable this boot: no legacy file and no migration marker generates a fresh identity to the `0o600` file (first run), while no legacy file with the marker present boots a `RecoveryState::KeyringLocked` ephemeral placeholder instead of generating (the real key still exists in the unreachable keyring)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:592-635"
  - statement: "`generate_and_persist` is the single function that actually mints a new identity for a first-ever launch: it calls `Keys::generate()`, stores the resulting keypair preferring the OS keyring (falling back to the `0o600` `identity.key` file), and — when the keyring write succeeds — writes the `identity.migrated` marker (or falls back to the plaintext file if the marker write fails) so a later keyring-unreachable boot never mistakes an existing identity for a fresh install."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:901-929"
  - statement: "A user can replace the generated identity with one they already hold: the `import_identity` Tauri command accepts either a raw `nsec`/hex secret key or a NIP-49 `ncryptsec1…` backup (decrypted with a supplied password), persists it via `commit_imported_identity` (persist first, then swap in-memory keys and clear both recovery flags, then best-effort clean up the previous identity's stale app-managed backup), and is used both for genuine key import and for `RecoveryState::Lost`/`KeyringLocked` re-entry."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity.rs:336-389"
      - "desktop/src-tauri/src/commands/identity.rs:407-452"
      - "desktop/src-tauri/src/key_backup.rs:115-129"
  - statement: "The frontend's `NostrKeyImportForm` component is explicitly shared between the first-run welcome flow (no community yet) and the later profile-onboarding flow, and its `OnboardingFlow` host renders a distinct `key-import` page — reached automatically when `identityLost` is true, or manually via a 'use a different key' action from the profile page — separately from the default `profile` landing page."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/NostrKeyImportForm.tsx:50-56"
      - "desktop/src/features/onboarding/ui/OnboardingFlow.tsx:166-170"
      - "desktop/src/features/onboarding/ui/types.ts:7-11"
  - statement: "`app_state_tests.rs` exercises `resolve_identity_with_store` and `generate_and_persist` against a fake keyring across every combination this node describes (fresh install, corrupt keyring with and without a migration marker, corrupt legacy file, reachable-but-empty keyring, unreachable keyring) — for example `corrupt_keyring_generates_fresh_only_when_no_file`, `reachable_but_empty_corrupt_file_generates_fresh`, and `unreachable_corrupt_file_generates_fresh` — confirming the generate-on-first-launch behavior is implemented and tested, not merely commented."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state_tests.rs:363-364"
      - "desktop/src-tauri/src/app_state_tests.rs:1108-1109"
      - "desktop/src-tauri/src/app_state_tests.rs:1215-1217"
  - statement: "Mobile does not independently generate or import a first Nostr identity the way desktop does; its `pairing` feature instead transfers an existing identity from a paired desktop over an authenticated, ECDH-secured device-pairing channel (NIP-AB), tracked in mobile pairing state via fields such as `sendsIdentityToDesktop`."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_provider.dart:1-52"
      - "crates/buzz-core/src/pairing/NIP-AB.md:1-17"
  - statement: "The onboarding identity UI surface is covered by Playwright E2E specs under `desktop/tests/e2e/` — `onboarding.spec.ts`, `key-import-reveal.spec.ts`, and `identity-lost.spec.ts` all exist in that directory, exercising the key-import form and the identity-lost recovery screen — though this node confirms only the files' existence and naming (via directory listing), not a fresh run of the suite."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/onboarding.spec.ts"
      - "desktop/tests/e2e/key-import-reveal.spec.ts"
      - "desktop/tests/e2e/identity-lost.spec.ts"
  - statement: "No corpus node for a neighboring onboarding capability (`capabilities/onboarding/first-channel.md`, `first-community.md`, or the overall `onboarding.md`) exists on `origin/launchpad` at the recorded revision, so this node declares no `part-of` or `references` relationship toward any of them; `architecture-containers-desktop` and `architecture-containers-mobile` are the only capability-adjacent nodes already merged, and this node `references` both as the containers that implement first-identity resolution/pairing."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no capabilities/ subtree present at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
---

# First identity: capability

When a person opens Buzz for the first time with no prior identity anywhere
on the machine, the app gives them a working cryptographic identity — a
Nostr keypair — without asking them to do anything: it is generated and
durably stored before the first onboarding screen appears. From that moment
the person's npub is their portable identity across every Buzz community.
Someone who already has a Nostr identity (from another Buzz install, another
Nostr client, or a backup) can bring it in instead of using the freshly
generated one, at any point onboarding offers a key-import step.

## Maturity

**Shipped.** The generate-on-first-launch path (`build_app_state` →
`resolve_persisted_identity` → `load_or_create_identity` →
`resolve_identity_with_store` → `generate_and_persist`) and the
bring-your-own-key import path (`import_identity` /
`commit_imported_identity`) are both implemented in
`desktop/src-tauri/src/app_state.rs` and
`desktop/src-tauri/src/commands/identity.rs`, and both are covered by unit
tests in `desktop/src-tauri/src/app_state_tests.rs` that exercise fresh
install, corrupt-keyring, and keyring-unreachable variants against a fake
keyring seam (`IdentityKeyStore`). The onboarding UI surface
(`NostrKeyImportForm`, the `key-import` page in `OnboardingFlow`) is likewise
implemented and covered by Playwright specs under `desktop/tests/e2e/`
(`onboarding.spec.ts`, `key-import-reveal.spec.ts`, `identity-lost.spec.ts`).

## Boundary

This node does not describe:
- **How the identity is durably stored or migrated** (OS keyring vs. the
  `0o600` `identity.key` file, the `identity.migrated` marker protocol, the
  keyring-locked/identity-lost recovery states) — that is implementation
  detail of the `architecture-containers-desktop` container, cited here as
  evidence of the capability's existence, not restated as this node's own
  subject matter.
- **Key backup** (NIP-49 `ncryptsec` encrypted export, the download-key and
  encrypted-backup onboarding steps) — a related but distinct capability:
  first-identity is about acquiring a working keypair, backup is about not
  losing it afterward.
- **Device pairing itself** (NIP-AB's ECDH/SAS protocol that lets mobile
  receive an identity from a paired desktop) — mobile's identity-acquisition
  path is noted here as a boundary against desktop's generate/import path,
  not documented in its own protocol detail.
- **Profile, avatar, or community-selection onboarding steps** — those are
  the neighboring `first-channel`/`first-community`/overall `onboarding`
  capabilities (not yet drafted corpus nodes as of this node's authoring;
  see the relationships note below), which begin only after an identity
  already exists.
- **The step-by-step sequence of onboarding screens a user clicks through**
  — that is a flow node's territory, not a capability node's.

## Relationships

- references: architecture-containers-desktop
- references: architecture-containers-mobile

## Scope and omissions

**This node covers** the capability of acquiring a first working Nostr
identity when opening Buzz with no prior identity: silent auto-generation on
desktop's first launch, the priority order that generation is skipped in
favor of an existing keyring/file identity, the first-launch-vs.-recovery
disambiguation via the migration marker, the bring-your-own-key import path
(raw nsec/hex or NIP-49 encrypted backup) exposed through onboarding, and
mobile's structurally different identity-acquisition path (pairing from an
already-identified desktop rather than independent generation).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Keyring/file storage internals, migration marker protocol, recovery states | `architecture-containers-desktop` (and any future `implementation`/`operations` node on identity storage) |
| Key backup / NIP-49 encrypted export | a future backup-focused corpus node, not yet drafted |
| NIP-AB device-pairing protocol details | a future pairing-focused corpus node, not yet drafted |
| Profile, avatar, and community-selection onboarding steps | the `first-channel`/`first-community`/`onboarding` capability nodes (#796/#797/#799), not yet merged at authoring time |
| The step-by-step onboarding flow sequence | a future flow-type corpus node, not yet drafted |

**Expected but not verified when this node was written:**
- Whether the `first-channel`, `first-community`, and overall `onboarding`
  capability nodes (drafted in parallel by sibling tasks #796/#797/#799) will
  want a `part-of` or `references` edge to or from this node once merged —
  left for whichever of those nodes lands and is authored against a corpus
  that already contains this one.
- The exact current behavior of the Playwright specs cited under *Maturity*
  was not re-executed for this node; their existence and file names were
  confirmed by directory listing and `grep`, not by running the suite.
