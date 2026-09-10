# Plan: issue #1256 — document platforms/mobile/key-storage.md

## ALREADY TRUE

- Feature #614 ("runtime platform corpus exists") is the parent; issue #1256
  is one of nine sibling `platforms/mobile/*.md` document tasks under it.
- `launchpad/docs/corpus/platforms/mobile/key-storage.md` does not exist yet,
  on `origin/launchpad` or in this worktree.
- No open PR targets issue #1256 or this task's branch.
- No `platforms/**` corpus node is merged on `origin/launchpad` yet, so there
  is no already-settled sibling instance to match structurally — only the
  batch-wide `type: platforms` convention (an inference from the orchestrating
  session, since no platforms-specific template exists).
- `launchpad/docs/corpus/templates/` has no `platforms-*` template. The two
  closest templates are `architecture-component.md` (`type: architecture`,
  requires a Mermaid diagram, decomposes one *container*) and `component.md`
  (`type: implementation`, documents one *standalone* component: crate/module,
  responsibility, public interface, dependencies both directions). Issue
  #1256's DoD bullets — "states responsibility and well-defined
  interface/boundary", "names dependencies and collaborators", "links source
  implementation and tests", "explains only component-level behavior, not the
  entire containing platform" — map onto `component.md`'s Required Sections
  almost verbatim, not onto `architecture-component.md`'s
  diagram/building-block-table shape (there is no need to decompose a
  container's full internals here; the subject is one storage boundary).
- The mobile app already has a working, tested secure-storage implementation
  for the user's Nostr private key (`nsec`): `CommunityStorage`
  (`mobile/lib/shared/community/community_storage.dart`), backed by
  `flutter_secure_storage` (`mobile/pubspec.yaml:21`, `^10.0.0`), with no
  platform-specific `AndroidOptions`/`IOSOptions` configured anywhere in
  `mobile/lib`.
- `Community` (`mobile/lib/shared/community/community.dart`) is the model
  carrying the optional `nsec` field; `CommunityStorage` persists the whole
  community list as one JSON blob under a single secure-storage key
  (`buzz_communities`), plus a separate `buzz_active_community_id` key, with
  documented migration from three older key shapes (`buzz_workspaces`+
  `buzz_active_workspace_id`, and the original flat
  `buzz_relay_url`/`buzz_token`/`buzz_pubkey`/`buzz_nsec`).
- Real, direct consumers exist and are inspectable: `community_provider.dart`
  (`communityStorageProvider`, the Riverpod singleton), `relay_provider.dart`
  (`RelayConfig`/`relayConfigProvider` derives the signing key for NIP-42 AUTH
  and event signing from the active community), and `auth_provider.dart`
  (reads storage directly to restore/validate auth state at startup).
- `mobile/test/shared/community/community_storage_test.dart` is a real,
  substantial test suite covering round-trip persistence and all three
  migration paths.
- A related but distinct export path exists: `push_bridge.dart`'s
  `registerBuzzPushCommunitySnapshot` copies decoded signing-key bytes to
  native iOS storage (via a MethodChannel) for the notification service
  extension, only for push-enabled communities. This is a second concept
  (push notification snapshotting) already covered by sibling issue #1258
  (`platforms/mobile/push-integration.md`) — it will be named as an explicit
  out-of-scope boundary here, not folded in.
- Repository revision for this task: `131b02f989684117d9ab1dd426f1673fa638e523`.

## STEP 1 — Confirm scope and evidence sources

Re-read `community_storage.dart`, `community.dart`, `community_provider.dart`
(`communityStorageProvider`), `relay_provider.dart`
(`RelayConfig`/`relayConfigProvider`/`pubkeyFromNsec`), `auth_provider.dart`
(`_hasValidNsec` gate), and `community_storage_test.dart` in full. Confirm no
`AndroidOptions`/`IOSOptions`/`KeychainAccessibility` configuration exists
anywhere in `mobile/lib` (already grepped: none found). Done when every claim
the node will make traces to one of these already-opened files.

## STEP 2 — Draft `platforms/mobile/key-storage.md`

Hand-author front matter directly against `node.schema.json` (no
`platforms`-specific template exists, so this follows `AGENTS.md`'s
documented no-template path) but structure the body on `component.md`'s
Required Sections, adapted:
`id: platforms-mobile-key-storage`, `type: platforms` (batch convention),
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. Body: purpose/scope, Responsibility, Public interface (the
`CommunityStorage` methods table), Dependencies (depends on
`flutter_secure_storage`; depended on by `community_provider.dart` /
`relay_provider.dart` / `auth_provider.dart`), migration behavior, Boundary
(excludes the native iOS push-snapshot export, excludes pairing-session
secrets in `pairing_crypto.dart`, excludes the platform-level Flutter/iOS/
Android containers), Relationships (`part-of` →
`architecture-containers-mobile`, confirmed present on `origin/launchpad`),
Scope and omissions. Done when every DoD bullet in #1256 has a corresponding
section or explicit statement.

## STEP 3 — Classify every claim

Mark direct reads of the four source files and the test file as `FACT`. Mark
the "no explicit platform options configured, so default plugin backend
applies" claim as `INFERENCE` (the plugin's own Keychain/Keystore internals
are not vendored in this repository to open as `FACT`). Do not promote the
`registerBuzzPushCommunitySnapshot` boundary note past what's directly read.
Done when no evidence entry's class exceeds what was actually verified.

## STEP 4 — Validate: no new FAIL

Run `python3 launchpad/project-intelligence/corpus/validate.py` with the new
file present (expect 0 new errors beyond the ~21-22 pre-existing FAILs); then
temporarily move the new file out, re-run, confirm the FAIL set is byte-
identical to the pre-existing baseline, then restore the file. Done when both
runs are captured and compared.

## STEP 5 — Test, then commit (two separate calls)

Run the corpus unittest suite as the sole content of one Bash call, confirm
`OK`, then in a second call `git add` both new files and commit with
`git commit -s`. Done when the commit succeeds or is retried exactly once per
the known commit-gate quirk.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with no
  new FAIL lines versus the clean-checkout baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`, run as the sole content of its own Bash call.
- Every evidence citation is a real file this session opened, or (for the
  provenance entry only) the recorded commit SHA.
- Every DoD bullet in issue #1256 is satisfied by a named section in the
  drafted body.

## OPEN

- Whether `type: platforms` (this batch's working convention) or
  `type: implementation` (what the merged `component.md` template's own
  INFERENCE recommends for a component-shaped node) is the corpus's eventual
  settled answer for a `platforms/**`-path node built from `component.md`'s
  shape is not resolved by this task — flagged in the node's own scope
  section rather than silently picked.
- Whether `architecture-containers-mobile` (draft status, unmerged risk
  noted) will still exist with that id by the time this branch's sibling PRs
  are integrated — checked against `origin/launchpad` at authoring time only.

## LEFT OUT

- No new template is created; per `AGENTS.md`, a later task reshapes this
  once a `platforms`-specific template lands.
- No changes to `push_bridge.dart`, `push_lease_revocation_outbox.dart`, or
  any runtime code — this is a documentation-only task.
- No second corpus document — the native iOS push-snapshot export is named
  as an out-of-scope boundary pointing at issue #1258, not drafted here.
