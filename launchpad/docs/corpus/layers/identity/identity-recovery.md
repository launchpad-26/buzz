---
id: layers-identity-identity-recovery
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
  - statement: "A Buzz identity is a self-custodied secp256k1 Nostr keypair; nothing in buzz-auth or buzz-relay implements a password-reset or server-side account-recovery mechanism, so the relay cannot restore a key it never held."
    entry_class: INFERENCE
    evidence:
      - "desktop/src-tauri/src/key_backup.rs"
      - "desktop/src-tauri/src/identity_storage.rs"
      - "grep_search(pattern='password reset|forgot password|account recovery|recover.*account', paths=['crates/buzz-auth', 'crates/buzz-relay']) -> no matches"
    confidence: 0.85
  - statement: "identity_storage.rs defines RecoveryState as an enum of exactly three variants -- None, Lost, KeyringLocked -- used to distinguish a genuinely missing local key from a keyring that is merely unreachable this boot."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/identity_storage.rs:51-55"
  - statement: "app_state.rs's signing_keys() returns Err and blocks all event signing/publishing whenever identity_lost or keyring_locked is set, with the message 'identity is in recovery mode; event signing is disabled until the identity is restored and Buzz is relaunched', so recovery mode is enforced at the one call site every signing and publish command must go through."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:298-318"
  - statement: "When identity resolution detects RecoveryState::Lost or RecoveryState::KeyringLocked, app_state.rs generates a fresh in-memory ephemeral Keys::generate() so the app has a structurally valid key to hold, but that ephemeral key is never persisted or usable for signing while the recovery flag is set -- it exists only to keep AppState valid until the real identity is restored or abandoned."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:604-612"
      - "desktop/src-tauri/src/app_state.rs:632-641"
      - "desktop/src-tauri/src/app_state.rs:692-701"
  - statement: "key_backup.rs implements a NIP-49 password-encrypted local backup: create_backup_blob() encrypts the identity secret key into a bech32 ncryptsec1... string and immediately decrypt-verifies it against the live public key before returning it, so a returned blob is provably recoverable with the same password before the user ever sees it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/key_backup.rs:52-92"
  - statement: "key_backup.rs's module doc states the ncryptsec backup blob is local-only by contract and must never be transmitted to a relay on any path, enforced at runtime by egress_guard and structurally by a source-allowlist scan in the module's own tests."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/key_backup.rs:1-11"
  - statement: "recover_keys_from_input() accepts either an ncryptsec1... backup string (requires a password) or a raw nsec/hex private key (the format accepted before encrypted imports were added), and is the single entry point import_identity uses to turn re-entered key material back into usable Keys."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/key_backup.rs:115-129"
  - statement: "commands/identity.rs's import_identity command calls recover_keys_from_input, then commit_imported_identity persists the recovered key (OS keyring first, falling back to a 0o600 identity.key file only if the keyring is unavailable), swaps it into state.keys, and clears both identity_lost and keyring_locked before deleting any stale backup that encrypted the previous identity."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity.rs:336-452"
  - statement: "commands/identity.rs's persist_current_identity command is documented as LOST-only: it deliberately returns Err when keyring_locked is set rather than identity_lost, because in the locked case the user's real key still exists in an unreachable keyring, and persisting the ephemeral placeholder key to identity.key would cause the mismatched-file adoption path to clobber the real key once the keyring becomes reachable again -- the documented correct action for a locked keyring is to unlock it and relaunch, not to abandon the identity."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity.rs:454-465"
  - statement: "commands/pairing.rs's start_identity_recovery_pairing command starts the same pairing session machinery as ordinary device pairing but with PairingMode::RecoverIdentity, and appends '&mode=recover' to the generated nostrpair:// QR URI; unlike PairingMode::SendIdentity (used by ordinary device pairing), the recovering side attaches no nsec payload to the session, because it has no key to send."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/pairing.rs:99-155"
  - statement: "The NIP-AB pairing specification defines the QR URI's own query parameters (source pubkey, secret, relay, v) but states plainly that 'Clients MAY support additional query parameters for forward compatibility. Unknown parameters MUST be ignored,' so Buzz's 'mode=recover' is an application-level convention layered on top of the spec, not part of NIP-AB itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:115"
  - statement: "NIP-AB defines 'nsec' as a first-class payload_type carrying a NIP-49 ncryptsec1... string (recommended) or a raw nsec1... string for private-key transfer; Buzz's recovery pairing reuses this same defined payload type and transport rather than inventing a new one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:336-341"
  - statement: "On the mobile side, pairing_provider.dart sets _sendIdentityToSource to true only when the scanned nostrpair:// URI's 'mode' query parameter equals 'recover', which is what causes the phone (already holding a valid identity) to become the side that sends its key over the pairing channel instead of receiving one."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_provider.dart:360-362"
  - statement: "pairing_page.dart shows the phone-side confirmation copy 'This sends your full Buzz identity to the desktop and grants it permanent access. Only confirm a desktop you trust and a recovery you started' specifically in the recovery-sends-identity branch, distinct from the ordinary receive-identity copy in the same conditional."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_page.dart:280-284"
  - statement: "The desktop e2e suite identity-lost.spec.ts exercises the full lost-boot UX: the onboarding gate opens directly on 'Enter your private key' when identity_lost is set, offers a 'Send identity to desktop' phone-recovery path via a single-use QR (testid identity-recovery-qr) with SAS confirmation before the phone sends its key, refreshes the recovery QR before the pairing relay expires it, accepts a pasted nsec/ncryptsec import that then requires a relaunch (testid relaunch-required), and offers an explicit confirmation-gated 'Start new identity' action that abandons the lost key."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/identity-lost.spec.ts:53-158"
      - "desktop/tests/e2e/identity-lost.spec.ts:347-399"
  - statement: "The same suite shows the keyring-locked boot state renders a distinct 'keyring-locked' screen (not the lost-mode onboarding gate or key-import UI) offering only 'Re-import your key instead' or a relaunch action, matching persist_current_identity's documented refusal to treat a locked keyring the same as a lost key."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/identity-lost.spec.ts:424-493"
  - statement: "Onboarding's BackupStep.tsx frames the local encrypted backup as the user's own responsibility rather than something Buzz can restore on their behalf: 'Buzz keeps your identity key protected on this device. Make a separate backup in case you lose access.'"
    entry_class: FACT
    evidence:
      - "desktop/src/features/onboarding/ui/BackupStep.tsx:166"
  - statement: "buzz-cli takes the operator's private key fresh on every invocation via the required BUZZ_PRIVATE_KEY environment variable or --private-key flag rather than persisting it in any app-managed store, so the desktop/mobile recovery machinery described in this node -- which exists to recover a key that was durably stored and then lost -- has no CLI counterpart to lose in the first place."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:86"
      - "crates/buzz-cli/src/lib.rs:2029-2032"
  - statement: "Issue #1109's definition of done requires this node to document identity recovery as a single canonical concept node, distinguishing it from device pairing (#1105), and to honestly document the actual (lack of) recovery mechanism for a truly lost key rather than inventing one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1109 definition of done"
---

# Identity recovery

What happens, and what a Buzz user can actually do, when a device's copy of a
Buzz identity key goes missing or becomes unreachable.

## Definition

**Identity recovery is what Buzz offers a device that has lost its own local
copy of a Nostr private key — and, first and plainly, that is *not* recovery of
a key that has no surviving copy anywhere.** A Buzz identity is an ordinary
self-custodied secp256k1 Nostr keypair (see NIP-01). Nothing in `buzz-auth` or
`buzz-relay` stores a password, a recovery question, or any other server-side
credential that could restore a key the relay never held, and no such
mechanism was found anywhere in this repository. If a key's only copy is lost
— no local backup, no other device still holding it — that identity is gone,
permanently, exactly as it would be for any other self-custodied Nostr key.
That is not a limitation this document is scoping around; it is the actual,
current answer, and the two mechanisms below are best understood as ways
Buzz's desktop app tries to prevent that permanent-loss case from being
reached in the first place, not as ways it reverses it once reached.

**What "recovery" means in the code is narrower and more concrete than the
word suggests.** The desktop app tracks two distinct failure states —
`RecoveryState::Lost` (the local key is genuinely gone: a keyring-migration
marker exists but the keyring came back empty and no plaintext fallback file
was found) and `RecoveryState::KeyringLocked` (the OS keyring itself is
unreachable this boot, but a migration marker shows the key is still inside
it). Both states set an in-memory flag that blocks `signing_keys()` from
returning a usable key — no event can be signed or published — until the
identity is restored and the app relaunches. A fresh, unpersisted ephemeral
keypair is generated in memory purely so the rest of `AppState` has something
structurally valid to hold; it is never the identity the user gets back.

## Background

Nostr has no protocol-level account-recovery authority: there is no operator
who can reset a private key, because no operator ever holds one. Buzz's relay
and auth layers do not change that — they authenticate signed events (NIP-42),
they do not custody keys. Given that constraint, "recovery" in Buzz is
necessarily about **local mitigations against key loss**, not about reversing
loss after every copy is gone. The desktop app ships two such mitigations,
and a third, more drastic option when neither applies.

## Use cases

A user reaches this node's territory when:

- **The desktop's OS keyring is emptied or corrupted** (its migration marker
  is present, but the keyring itself is unreachable or, on the next boot,
  reachable but empty) — `RecoveryState::Lost`.
- **The OS keyring is temporarily unreachable** — locked, permission-denied,
  or the OS keyring service is down — while the key itself is still inside it
  — `RecoveryState::KeyringLocked`. This is not key loss at all, and the
  desktop deliberately treats it differently.
- **A user sets up a new desktop install** and wants to bring an existing
  identity across without having pre-arranged an ordinary device-pairing
  session from an already-signed-in device.

### Path 1 — restore from an encrypted local backup

Onboarding and Settings let a user create a password-encrypted local backup
(`key_backup.rs`'s `create_backup_blob`): a NIP-49 `ncryptsec1...` bech32
string, written to a user-chosen file (or the app-managed
`identity.ncryptsec` inside the app data directory), and immediately
decrypt-verified against the live identity before it is ever shown as
"backed up." The blob is contractually local-only — `egress_guard` and a
source-allowlist test enforce that it is never sent to a relay on any code
path. To recover, the user re-enters the backup string and its password (or a
raw `nsec`/hex key, the format supported before encrypted backups existed)
into `import_identity`, which decrypts it, persists it into the OS keyring
(falling back to a `0o600` file only if the keyring is unavailable), and
clears both recovery flags. **This backup is the user's own responsibility to
create and store somewhere Buzz cannot reach** — onboarding says so directly:
"Buzz keeps your identity key protected on this device. Make a separate
backup in case you lose access." A user who never created one has nothing to
restore from.

### Path 2 — recover from another device that still holds the key

If a phone (or another already-signed-in device) still holds the identity,
the lost desktop can recover it over the same NIP-AB pairing protocol
ordinary device pairing uses (see the sibling device-pairing node once it
merges), but in a distinct mode. `start_identity_recovery_pairing` starts a
session with `PairingMode::RecoverIdentity` and appends `&mode=recover` to
the standard `nostrpair://` QR URI — an application-level extension NIP-AB
explicitly permits ("Clients MAY support additional query parameters for
forward compatibility"), not a change to the spec itself. Recovery reuses
NIP-AB's own `nsec` payload type (an `ncryptsec1...` or raw `nsec1...`
string), the same payload type ordinary pairing uses to send a key to a new
device. The direction is what differs: in ordinary pairing the desktop that
already has a key is the one that sends it; in recovery pairing the lost
desktop shows the QR but sends nothing, and the phone — recognizing
`mode=recover` in the scanned URI — is the side that sends its identity,
after both devices confirm a 6-digit SAS code shown on each. The desktop's
e2e suite exercises this end to end: the QR refreshes before the pairing
relay's session would expire, a codes-don't-match cancellation is handled
the same way ordinary pairing cancellation is, and a successful recovery
proceeds straight to harness setup without a relaunch. **This path recovers
nothing if no other device still holds the key** — it moves an existing copy,
it does not conjure one.

### Path 3 — abandon and start a new identity

If neither backup nor another device is available, the onboarding lost-key
screen offers an explicit, confirmation-gated "Start new identity" action.
This does not recover anything: `persist_current_identity` takes the
ephemeral in-memory key `RecoveryState::Lost` already generated and makes it
permanent by persisting it to the keyring (or file). It is documented as
**lost-only** — it deliberately refuses to run when the state is
`KeyringLocked` rather than `Lost`, because in the locked case the real key
is still recoverable once the keyring is reachable again, and persisting a
throwaway ephemeral key over it would risk the mismatched-key adoption logic
clobbering the real one on a later boot. In locked state the documented
correct action is to unlock the keyring and relaunch, not to abandon the
identity. Choosing this path means the previous identity — and everything a
relay or another user associated with its public key — is permanently
orphaned from this device; nothing in the codebase reconnects the two.

## Comparison

| Path | Recovers the *same* key? | Requires | Desktop state cleared |
|---|---|---|---|
| Restore from encrypted local backup | Yes | A password-protected `ncryptsec` (or raw `nsec`/hex) the user saved earlier | `identity_lost` and `keyring_locked`, either state |
| Recover from another device (phone) | Yes | Another device that still holds the key, physically present to scan a QR and confirm a SAS code | `identity_lost` and `keyring_locked`, either state |
| Start a new identity | No — abandons the old key | Nothing but confirmation | `identity_lost` only; refuses when `keyring_locked` |
| Wait / relaunch after unlocking the OS keyring | Yes, and no import needed | The OS keyring becoming reachable again | `keyring_locked` (not a recovery action at all — the key was never gone) |

## Related resources

No `relationships` entries are declared. At the time this node was written,
`launchpad/docs/corpus/layers/` does not exist on `origin/launchpad` — none of
the other twelve `layers/identity/*` nodes in this same batch (#607, issues
#1102–#1114, including `layers-identity-device-pairing` and
`layers-identity-identity-storage`, both directly relevant) have merged yet,
so a `relationships.target` naming any of them would be a hard validation
error today. `architecture-containers-desktop` and
`architecture-principles-signed-events` do exist on `origin/launchpad` and
would resolve, but this corpus has an established convention (see
`standards/front-matter.md`'s own "No relationships" note) of deferring edges
to already-merged nodes to a batch-wide relationship pass rather than adding
them ad hoc mid-authoring; this node follows that same convention rather than
inventing an exception for itself. The likeliest future edges, once their
targets merge, are `references` to `layers-identity-device-pairing` (the
mechanism this node's Path 2 reuses) and `layers-identity-identity-storage`
(the keyring/file storage this node's recovery states are defined against).

## Scope and omissions

**This node covers** what recovery means for a Buzz desktop identity, the
honest absence of any true server-side or protocol-level recovery for a
key with zero surviving copies, and the three concrete paths Buzz's desktop
app offers when a local key is lost or its keyring is unreachable.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The mechanics of ordinary (non-recovery) device pairing — adding a new device while the original still holds a working key | `layers-identity-device-pairing` (#1105), not yet merged |
| How the OS keyring, the `identity.key` file fallback, and the migration marker actually work day to day | `layers-identity-identity-storage` (#1110), not yet merged |
| The keypair itself — what it is, how it is generated, its relationship to NIP-01 | `layers-identity-keypair` (#1111), not yet merged |
| Mobile's *own* first-run key generation and any mobile-native loss scenario distinct from "phone still has the key, desktop doesn't" | Not established here — evidence gathered was about the phone acting as the *source* of a recovery, not about the phone losing its own key |
| Whether `buzz-agent`/managed-agent identities have any loss/recovery story of their own, distinct from the human desktop/mobile identity described here | Not inspected — out of scope; this node concerns the human/device identity layer only |

**Expected but not verified when this node was written:**

- **Whether an OS-keyring-unreachable state can ever silently resolve into a
  false `Lost` classification** (i.e., a slow or transiently-erroring keyring
  backend misread as "empty" rather than "locked") was not tested against a
  real OS keyring failure mode — only the code's own stated branching logic
  was read.
- **The mobile-side settings entry point** (`settings_page.dart`'s
  "identity-recovery page pushed from the recovery settings row") was
  confirmed to exist by name but its full UI flow was not read line by line;
  the desktop-side behavior in this node is verified in more depth than the
  phone-side "Send identity to desktop" screen it pairs with.
