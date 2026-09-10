---
id: capabilities-archive-restore
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "The desktop app lets a user recover a Nostr identity (private key plus profile) on a fresh or reset install by supplying a NIP-49 encrypted backup (`ncryptsec1...`) and its password; `recover_keys_from_input` and `decrypt_ncryptsec` in `key_backup.rs` implement the decrypt path, and the `import_identity` Tauri command wires it to the frontend."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/key_backup.rs"
      - "desktop/src-tauri/src/commands/identity.rs"
  - statement: "A second, independent restore path lets a fresh desktop install recover the same identity by pairing with an already-authorized phone over NIP-AB: the desktop shows a QR code, both sides confirm a short-authentication-string (SAS), and the phone sends the full identity to the desktop, which commits it as an import."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/pairing.rs"
      - "desktop/src/features/onboarding/ui/IdentityRecoveryPairing.tsx"
  - statement: "Both restore variants are entered from the same onboarding surface: the encrypted-backup-file dialog is titled 'Restore from a backup file' and the phone-pairing dialog is titled 'Recover from your phone' when the app's identity is lost; a third entry point, `KeyringLockedScreen`'s 'Re-import your key instead' flow, offers only the encrypted-backup-file variant when the OS keyring is unreachable for the current session rather than lost outright."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/MachineOnboardingFlow.tsx"
      - "desktop/src/features/onboarding/ui/KeyringLockedScreen.tsx"
  - statement: "The `NostrKeyImportForm` component and its shared `BackupPasswordTimeline` decoration explicitly model 'restore' as a first-class mode, distinct from the 'backup' (creation) mode of the same components, with its own doc comment: 'Backup creation reads key -> password -> lock; restore reads encrypted file -> password -> unlocked account.'"
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/NostrKeyImportForm.tsx"
      - "desktop/src/features/onboarding/ui/BackupPasswordTimeline.tsx"
  - statement: "A decrypt attempt is rejected before the password is even checked if the backup's self-described scrypt cost parameter (`log_n`) exceeds `MAX_VERIFY_LOG_N`, the same cost tier Buzz's own backup creation emits; a wrong password or a structurally damaged backup both surface as the single generic error 'wrong backup password or damaged key backup' rather than distinguishing the two causes."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/key_backup.rs"
  - statement: "`egress_guard.rs` fail-closed-blocks any relay-bound payload containing `ncryptsec1`/`NCRYPTSEC1` text at eight named submission boundaries, and its own module doc states this scope is deliberately narrower than the raw `nsec`: the raw key intentionally does transit the NIP-44-encrypted pairing session the phone-pairing restore variant uses, because guarding it there would break pairing -- so the two restore variants carry different in-transit exposure characteristics for the secret material they carry."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/egress_guard.rs"
  - statement: "`commit_imported_identity`'s documented ordering contract requires durable persistence (OS keyring, falling back to an owner-only-permission file) to succeed before the in-memory identity is swapped and the lost/locked recovery flags are cleared, so a failed restore leaves the previously active identity live in memory and on disk rather than leaving the app in a half-restored state."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity.rs"
  - statement: "A case-insensitive search of `mobile/lib` and `crates/buzz-cli/src` for 'ncryptsec', 'nip-49' and 'nip49' returned no matches, so as of the checked revision this restore capability is reachable only from the desktop app, not from the mobile app or the agent-facing CLI."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('ncryptsec|nip-49|nip49', paths=['mobile/lib', 'crates/buzz-cli/src'], ref='cad6c375fdcc590158c1456c9fc7875f0f84a844') -> zero matches"
  - statement: "The encrypted-backup-file restore path is exercised by Rust unit tests (`recover_keys_ncryptsec_happy_path`, `recover_keys_ncryptsec_requires_password`, `recover_keys_ncryptsec_wrong_password`, and related cases) and by frontend unit tests of the form's classification and submit-gating logic (`submit_gating_ncryptsec_requires_passphrase`, `plausible_ncryptsec_requires_complete_checksummed_nip49_payload`)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/key_backup_tests.rs"
      - "desktop/src/features/onboarding/lib/keyImportInput.test.mjs"
  - statement: "The phone-pairing restore variant is exercised by Rust unit tests covering payload-type validation and commit-generation fencing (`recovery_rejects_non_nsec_payloads`, `superseded_recovery_cannot_commit_identity`)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/pairing_generation_tests.rs"
  - statement: "No UI-level end-to-end test (Playwright or an onboarding-flow vitest spec) was found exercising either restore dialog ('Restore from a backup file' or 'Recover from your phone') as a full flow; the onboarding test files that mention 'restore' or 'recover' by name (`machineOnboarding.test.mjs`, `welcome.test.mjs`) use those words for unrelated test-harness helpers (a mock `window.sessionStorage` restore function), not for exercising identity restore."
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/machineOnboarding.test.mjs"
      - "desktop/src/features/onboarding/welcome.test.mjs"
  - statement: "`architecture-containers-desktop` is a merged corpus node describing the desktop container this capability is realized in, and is a legal `references` target because it is present in `origin/launchpad`'s corpus tree at the checked revision."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes architecture/containers/desktop.md, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Treating the encrypted-backup-file path and the phone-pairing path as two variants of one 'identity restore' capability, rather than as two separate capability nodes, is the more consistent reading because both are offered from the same onboarding entry points (the 'identityLost' state and the keyring-locked screen) and both converge on the same `commit_imported_identity` persistence contract; a reasonable alternative split into two capabilities was considered and rejected on that basis."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/features/onboarding/ui/MachineOnboardingFlow.tsx"
      - "desktop/src-tauri/src/commands/identity.rs"
    confidence: 0.75
  - statement: "No `capabilities/archive/` sibling node (`export.md` #717, `identity-archive.md` #718, `local-archive.md` #719) is merged on `origin/launchpad` at the checked revision, so none is a legal `relationships` target from this node yet; whether any of them will scope 'export' or 'local archive' to overlap with the backup-creation half of this same NIP-49 flow is unresolved until they land."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch context for Feature #613's capabilities/archive/* task family (issues #717-#720), read directly via gh issue view for each"
  - statement: "Issue #720 requires this node to state the capability and its primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#720 definition of done"
relationships:
  - type: references
    target: architecture-containers-desktop
---

# Identity restore: capability

A person whose Buzz desktop identity is unreachable -- a fresh install, a reset
machine, or a locked OS keyring -- can restore that same Nostr identity (their
private key and profile) rather than starting over with a new one. Buzz offers two
independent ways to do it: supplying a password-protected local backup file the
person saved earlier, or pairing the new install with a phone that already holds
the identity. Either way, the restored identity resumes as the same npub, with the
same profile, channels and history, once the relay recognizes it.

## Maturity

**Shipped, desktop only.** Both restore variants have working UI, a wired Tauri
command, and passing tests at the checked revision:

- Encrypted-backup-file restore: `NostrKeyImportForm` (`mode="backup"`),
  `BackupPasswordTimeline` (`mode="restore"`), the `import_identity` Tauri command,
  and `key_backup::recover_keys_from_input`/`decrypt_ncryptsec` in Rust.
- Phone-pairing restore: `IdentityRecoveryPairing`, the `start_identity_recovery_pairing`
  Tauri command, and `PairingMode::RecoverIdentity` in `pairing.rs`.

Neither variant was found wired into the mobile app or `buzz-cli` (a case-insensitive
search of `mobile/lib` and `crates/buzz-cli/src` for `ncryptsec`/`nip-49`/`nip49`
returned no matches) -- restore today is a desktop-only capability.

## Boundary

This node does not describe:

- **How the desktop app itself is built** (Tauri/React architecture, the OS
  keyring/file-fallback storage layer, the local data directory) -- that is
  `architecture-containers-desktop`'s territory; this node references it rather
  than restating its content.
- **The NIP-AB pairing protocol's own mechanics** (QR code generation, the SAS
  confirmation handshake, the ephemeral sidecar relay in `buzz-pair-relay`) --
  those belong to device pairing's own capability/architecture documentation,
  not yet drafted in this batch. This node names phone-pairing only as a restore
  *variant*, not as a protocol reference.
- **The interface(s) restore is exposed through** -- the specific Tauri command
  signatures (`import_identity`, `start_identity_recovery_pairing`) and the
  onboarding UI's component boundary. No `interfaces-events`-typed corpus node
  exists yet for this surface to `references` instead.
- **The step-by-step flow through either restore variant** -- the exact sequence
  of screens and confirmations a user or agent walks through. No `flow`-typed
  corpus node exists yet for this capability to `references` instead.
- **How the running system is operated** -- this capability has no relay-side or
  deployment-operator component; it is entirely local to one desktop install
  restoring its own identity.
- **Backup *creation*** -- generating and saving the encrypted `ncryptsec` file
  or app-managed backup in the first place. Restore is the read/decrypt half of
  that pair; creation is a separate concept, potentially owned by a sibling
  `capabilities/archive/*` node once drafted (see *Scope and omissions*).

## Relationships

- references: `architecture-containers-desktop` -- the container this capability
  is realized in.

No other `relationships` are declared. At the checked revision no
`capabilities/archive/*` sibling node, no `interfaces-events`-typed node, and no
`flow`-typed node exists on `origin/launchpad` for this document to point at; each
absence is named explicitly above rather than assumed permanent.

## Scope and omissions

**This node covers** the identity-restore capability as a whole: what a person can
do (recover a lost or unreachable identity rather than starting over), the two
variants Buzz offers today (encrypted local backup file, phone-pairing), the
maturity of each, the constraints governing them (KDF cost capping, generic
decrypt-failure messaging, the persist-before-swap ordering contract, the
differing in-transit exposure of the secret material between the two variants),
and the tests that verify each variant at the unit level.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the desktop container itself is built | `architecture-containers-desktop` |
| NIP-AB pairing protocol mechanics | Not yet drafted (device-pairing capability/architecture) |
| The Tauri command / onboarding UI interface contract | Not yet drafted (`interfaces-events`) |
| The step-by-step restore flow | Not yet drafted (`flow`) |
| Backup **creation** (saving an encrypted file, generating a passphrase) | Potentially a sibling `capabilities/archive/*` node once drafted |
| Whether `export.md` (#717), `identity-archive.md` (#718) or `local-archive.md` (#719) overlap with this capability once drafted | Unresolved; none merged at the checked revision |

**Expected but not verified when this node was written:**

- **No UI-level end-to-end test was found** exercising either restore dialog as a
  full flow (file picked or phone paired through to a restored, usable identity).
  Only unit-level tests were located: Rust decrypt/import logic
  (`key_backup_tests.rs`, `pairing_generation_tests.rs`) and frontend
  classification/gating logic (`keyImportInput.test.mjs`). Whether a Playwright
  spec covering the full restore flow exists elsewhere, or is planned, was not
  established.
- **Whether restore is planned for mobile or the CLI** was not established beyond
  the negative search recorded in the evidence ledger; absence of a hit is not
  proof of no plan.
- **The relative scope of the sibling `capabilities/archive/*` nodes** (`export`,
  `identity-archive`, `local-archive`) was not checked against this node's content,
  because none is merged yet. Backup creation in particular may end up documented
  by one of them, by a future counterpart to this node, or left undocumented --
  unresolved until they land.
