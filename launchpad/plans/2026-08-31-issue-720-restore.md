# Plan: issue #720 — document capabilities/archive/restore.md

## ALREADY TRUE

- Repo root at `origin/launchpad` HEAD `cad6c375fdcc590158c1456c9fc7875f0f84a844` (worktree
  branch `task/720-restore` created directly from it; verified `git rev-parse` matches).
- `launchpad/docs/corpus/capabilities/archive/restore.md` does not exist.
- `launchpad/docs/corpus/templates/capability.md` (`corpus-template-capability`) exists and
  is merged — this task drafts against it, not raw `node.schema.json` alone.
- `node.schema.json`'s `type` enum member for this family is `capabilities` (plural).
- Sibling batch tasks in the same `capabilities/archive/` family: #717 (`export.md`), #718
  (`identity-archive.md`), #719 (`local-archive.md`) — none merged yet (no
  `capabilities/` directory exists on `origin/launchpad`), so **no relationship targets
  among them** are available.
- `architecture-containers-desktop` is a merged node on `origin/launchpad` (confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`) — a legal
  `references` target since restore is realized in the desktop container.
- Investigation (direct code reads, not secondhand) identified the actual "restore"
  capability: **desktop identity restore** — recovering a Nostr identity on a
  fresh/locked install, via two variants:
  1. Encrypted local backup file (NIP-49 `ncryptsec`) + password —
     `desktop/src-tauri/src/key_backup.rs` (`recover_keys_from_input`,
     `decrypt_ncryptsec`), `desktop/src-tauri/src/commands/identity.rs`
     (`import_identity` Tauri command), `desktop/src/features/onboarding/ui/
     {NostrKeyImportForm,BackupPasswordTimeline,MachineOnboardingFlow,
     KeyringLockedScreen}.tsx`.
  2. Phone-pairing recovery (NIP-AB) — `desktop/src-tauri/src/commands/pairing.rs`
     (`start_identity_recovery_pairing`, `PairingMode::RecoverIdentity`),
     `desktop/src/features/onboarding/ui/IdentityRecoveryPairing.tsx`.
  Desktop-only today — no `ncryptsec`/NIP-49 hits in `mobile/` or `crates/buzz-cli/src`.
- Ruled out as NOT this capability (each is a distinct concept, filed or owned elsewhere):
  channel `unarchive` (`crates/buzz-cli/src/commands/channels.rs`,
  `cmd_unarchive_channel`), community `unarchive_community_owned_by`
  (`crates/buzz-db/src/store/community.rs`, `crates/buzz-relay/src/api/operator.rs`),
  community-deletion abort internals (`crates/buzz-db/src/store/deletion.rs`),
  `local-archive` desktop feature folder (zero "restore" hits), snapshot export dialogs
  (one-way, no restore counterpart).

## STEP 1 — Draft front matter + evidence ledger

Fields: `id: capabilities-archive-restore`, `type: capabilities`, `status: draft`,
`origin: launchpad` (matches every merged product-documenting node's precedent),
`audiences: [developer, agent, reviewer]`. One `relationships` entry: `references` →
`architecture-containers-desktop`. Evidence entries per substantive claim, classified
honestly (FACT for opened code, INFERENCE+confidence only where reasoning is added,
TEAM_KNOWLEDGE+provided_by for anything sourced from an issue/PR only). Include the
provenance commit citation for `cad6c375fdcc590158c1456c9fc7875f0f84a844`.
**Done when:** every claim in the body has a matching ledger entry and every FACT cites
an opened file.

## STEP 2 — Draft body per capability template's required sections

Capability statement (identity restore, noun-phrase framing), Maturity (shipped,
desktop-only, cited to the files above), Boundary (not architecture/interface/flow/
operations — link to `architecture-containers-desktop` instead of restating it; not the
NIP-AB pairing protocol's own mechanics, which belong to a device-pairing capability/
architecture node not yet drafted; not the backup-*creation* half, which is the
counterpart capability #717/other export work may own), Relationships section restating
the one declared edge, Scope and omissions (gaps table + expected-but-not-verified list,
naming: mobile/CLI parity unchecked beyond a negative grep, whether #718/#719/#717 will
overlap once drafted).
**Done when:** all 5 required-sections bullets from the template are present and the
Boundary section names both restore variants without re-describing NIP-AB's protocol
steps.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root. Confirm
exit 0 and that the only errors/warnings present, if any, match the pre-existing 21
baseline FAIL entries already tracked in issue #1951 (unrelated to this node) — zero new
FAIL entries attributable to this file.
**Done when:** validator exits 0 and a diff against the known baseline shows no new
failures.

## STEP 4 — Earn commit gate, then commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call; confirm `OK`. Then, in a separate
call, `git add` the new document + this plan file and `git commit -s` with the required
message. No push, no PR.
**Done when:** commit exists locally on `task/720-restore`, `git status` clean aside from
the new commit.

## GATES

- `validate.py` exit 0, zero new FAIL entries vs. the #1951 baseline.
- `unittest discover` on `launchpad/project-intelligence/corpus/tests` reports `OK`,
  run as the sole command in its own tool call before any `git add`/`commit`.
- Exactly one hand-authored canonical document created (`capabilities/archive/restore.md`).
- `git commit -s` (signed off), no `--no-verify`, no push, no PR.

## BUDGET

5 steps max (used: 4). Single node, no code changes, no test-suite changes.

## OPEN

- Whether #717 (`export.md`) will scope "export" to include the backup-*creation* half
  of this same NIP-49 flow, which would make this node's Boundary note about that split
  more or less precise once #717 lands — left as a documented gap, not resolved here
  (per `AGENTS.md`'s rule not to fold a second concept in and not to guess at an
  unmerged sibling's actual scope).
- Whether NIP-AB phone-pairing recovery deserves its own future capability/architecture
  node (device pairing) distinct from this one — flagged as an omission, not decided.

## LEFT OUT

- Any relationship to #717/#718/#719 (`identity-archive`, `local-archive`, `export`) —
  none are merged on `origin/launchpad`, so none are legal targets yet.
- Describing NIP-AB pairing protocol mechanics (SAS confirmation, QR relay) beyond
  naming it as a variant — that belongs to pairing's own architecture/capability
  documentation, not duplicated here.
- Any code change to identity restore itself — this is a documentation-only task.
