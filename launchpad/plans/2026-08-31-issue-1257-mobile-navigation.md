# Plan: issue #1257 — document platforms/mobile/navigation.md

## ALREADY TRUE

- Worktree `__worktrees/task-1257-mobile-navigation` exists on branch
  `task/1257-mobile-navigation`, based on `origin/launchpad` at
  `131b02f989684117d9ab1dd426f1673fa638e523`.
- `launchpad/docs/corpus/platforms/mobile/navigation.md` does not exist yet;
  no `platforms/` directory exists in the corpus at all yet, so this is the
  first node of `type: platforms`.
- `launchpad/docs/corpus/templates/component.md` is the closest-fitting
  template (no platforms-specific template exists yet, per sibling-batch
  convention); it prescribes `type: implementation`, but sibling nodes under
  `platforms/**` have settled on `type: platforms` instead (an INFERENCE,
  recorded as such in the node's own evidence ledger).
- `launchpad/docs/corpus/architecture/containers/mobile.md`
  (`architecture-containers-mobile`) already exists on `origin/launchpad` and
  documents deep-link *parsing shapes* as one of the container's inbound
  interfaces, but does not cover dispatch/routing mechanics (queueing,
  community switching, channel lookup, `Navigator` push, thread auto-open
  behavior, or the tab `IndexedStack` model) — that gap is this node's
  subject, so `part-of: architecture-containers-mobile` is a valid,
  non-duplicating relationship.
- `launchpad/docs/corpus/architecture/flows/push-notification.md` covers the
  server-side push delivery pipeline only; it does not discuss client-side
  notification-tap routing, so no relationship to it is needed.
- Issue #1253 (`platforms/mobile/application-lifecycle.md`) is a sibling task
  in the same Feature, unmerged, covering lifecycle transitions — out of
  scope here per the task brief; not cited as a relationship target since it
  does not exist on `origin/launchpad`.
- Mobile routing has no `go_router` dependency (absent from
  `mobile/pubspec.yaml`); navigation is a single `MaterialApp`/`Navigator`
  with imperative `Navigator.push`/`pop`, confirmed by reading `app.dart`,
  `home_page.dart`, `deep_link_dispatcher.dart`, `pending_deep_link_provider.dart`,
  `deep_link.dart`, `push_bridge.dart`, `channel_detail_page.dart`,
  `message_list.dart`, `channel_link_navigation.dart`, `channels_page.dart`,
  and `immediate_page_route.dart`.
- Relevant tests already exist: `mobile/test/features/channels/deep_link_dispatcher_test.dart`,
  `mobile/test/shared/deeplink/deep_link_test.dart`,
  `mobile/test/shared/deeplink/pending_deep_link_provider_test.dart`.

## STEP 1 — Write the corpus node

Create `launchpad/docs/corpus/platforms/mobile/navigation.md` with schema-valid
front matter (`id: platforms-mobile-navigation`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
provenance commit citation, one evidence entry per substantive claim,
`relationships: [{type: part-of, target: architecture-containers-mobile}]`).
Body follows the component template's shape (purpose, responsibility, public
interface, dependencies both directions, boundary, relationships, scope and
omissions), adapted from "one crate" to "one cross-cutting routing mechanism"
since the platform surface has no rustdoc-style crate-level doc comment to
anchor to.

**Done when:** file exists, front matter validates conceptually against
`node.schema.json`'s required fields and enums, every claim has a citation to
a file actually opened during investigation.

## STEP 2 — Diff-isolate and run validate.py

Temporarily move the new file out, run
`python3 launchpad/project-intelligence/corpus/validate.py`, record the FAIL
set, restore the file, re-run, and diff the two FAIL sets.

**Done when:** the FAIL set is byte-identical before and after — i.e. this
node introduces zero new FAILs (some pre-existing FAILs are expected and out
of scope per the task brief).

## STEP 3 — Run the corpus unit test suite

`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole content of its own Bash call (no chaining), confirming `OK`.

**Done when:** the suite reports `OK`.

## STEP 4 — Commit

`git add` the node and this plan file, `git commit -s` with the required
message shape, as a separate Bash call from Step 3.

**Done when:** the commit exists and `git log` shows it on
`task/1257-mobile-navigation`.

## STEP 5 — Re-verify

Re-read the diff against every DoD bullet on #1257; re-open every cited file
and line range; re-confirm the validate.py FAIL-set-unchanged result holds
against the final committed state.

**Done when:** every DoD bullet has a concrete answer in the committed body,
and no citation was invented.

## GATES

- Corpus validation introduces zero new FAIL lines (existing ~21-22 FAILs on
  a clean `origin/launchpad` checkout are out of scope).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`, run as a lone, unchained Bash call.
- Commit gate accepts the commit (retry once per finding #5 if refused).
- Every DoD bullet on issue #1257 is satisfiable by pointing at a specific
  section of the committed document.

## OPEN

- Whether Android's native intent-filter wiring for `buzz://` links mirrors
  iOS exactly was not inspected — only the shared Dart-side `app_links`
  stream consumption was. Recorded as an expected-but-not-verified gap in the
  node's own Scope and omissions section, not resolved here.
- The native (Swift) side of the push-notification method channel
  (`notificationOpened`, `takePendingNotificationResponse`) was not opened —
  only the Dart-side contract in `push_bridge.dart`. Same treatment.
- `MobileHuddleShell`'s own use of the shared root `navigatorKey` for its
  overlay was not investigated beyond confirming its existence; named as an
  explicit exclusion in the node's Boundary section.

## LEFT OUT

- Application lifecycle transitions (#1253) — separate node, separate task.
- Deep-link URI parsing/validation shapes themselves — already covered at
  container level by `architecture-containers-mobile`'s Inbound interfaces
  section and by `deep_link.dart` itself; this node cites but does not
  restate them.
- Server-side push notification delivery pipeline — covered by
  `architecture-flows-push-notification`.
- Settings/profile-edit screen navigation minutiae beyond the one
  `immediatePageRoute` example needed to illustrate the "route with its own
  transition" pattern.
- NIP-AB pairing flow's own screen navigation.
