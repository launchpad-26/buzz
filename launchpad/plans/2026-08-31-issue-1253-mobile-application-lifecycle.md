# Plan: issue #1253 — document platforms/mobile/application-lifecycle.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist anywhere on `origin/launchpad`
  (HEAD `131b02f989684117d9ab1dd426f1673fa638e523`) — this task creates the first
  node in that subtree, so `type: platforms` has no prior file precedent in this
  worktree even though the batch orchestrator reports sibling `platforms/**`
  tasks in other worktrees have already settled on `type: platforms`.
- `launchpad/docs/corpus/architecture/containers/mobile.md` (id
  `architecture-containers-mobile`) and
  `launchpad/docs/corpus/architecture/flows/push-notification.md` (id
  `architecture-flows-push-notification`) already exist and validate, so both
  are legal `relationships[].target` values.
- The mobile app's lifecycle plumbing is real, working code, not a stub:
  `mobile/lib/shared/relay/app_lifecycle_provider.dart` (`AppLifecycleNotifier`,
  a Riverpod `Notifier<AppLifecycleState>` wrapping Flutter's
  `AppLifecycleListener` — no `StatefulWidget`) drives
  `RelaySessionNotifier.onAppPaused`/`onAppResumed` in
  `mobile/lib/shared/relay/relay_session.dart`, and several independent
  consumers (`channels_provider.dart`, `profile_provider.dart`,
  `push_bridge.dart`, `mobile_huddle_controller.dart`,
  `read_state_provider.dart`) watch the same `appLifecycleProvider`.
- Cold-start notification routing is a separate, verified path:
  `main.dart` → `push_bridge.dart`'s native `MethodChannel('buzz/push')` →
  `pendingPushNotificationLink` → `pending_deep_link_provider.dart` →
  `deep_link_dispatcher.dart` → `Navigator.push(ChannelDetailPage)`.
- Sibling issue #1259 (`platforms/mobile/relay-connection.md`) is unmerged and
  its target id (`platforms-mobile-relay-connection`, by convention) does not
  exist on `origin/launchpad` — it cannot be a relationship target yet.
- `mobile/test/shared/relay/relay_session_test.dart` already has two tests
  directly exercising `onAppPaused`/`onAppResumed` (lines 521-575, 577-632).

## STEP 1 — Confirm scope and template shape

Read `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, and the `templates/component.md` template
(closest fit: the issue's DoD bullets — responsibility, interface/boundary,
dependencies/collaborators, links to implementation/tests, component-level
only — are copied nearly verbatim from that template's *Required sections*).
No `platforms`-specific template exists yet, so the component shape is
adapted with `type: platforms` per the batch's established convention rather
than `type: implementation` (that value is reserved for crate/module-level
Rust components per `templates/component.md`'s own reasoning).

**Done when:** template shape and front-matter type decided and written down
here (done — see above).

## STEP 2 — Investigate the real lifecycle code, verify every citation myself

Read, personally, each of: `app_lifecycle_provider.dart`,
`relay_session.dart` (lines ~100-470), `channels_provider.dart` (~120-135),
`profile_provider.dart` (~290-345), `push_bridge.dart` (~14-135, ~290-326),
`mobile_huddle_controller.dart` (~100-125), `read_state_provider.dart`
(~120-127), `pending_deep_link_provider.dart` (full file, 111 lines),
`deep_link_dispatcher.dart` (full file, 221 lines), `main.dart`, and
`mobile/pubspec.yaml`. Confirm each fact with line numbers before citing it as
`FACT` — no citation is copied from a delegated research pass without
independently opening the file.

**Done when:** every claim intended for the document body has been read
directly by this session and the exact line numbers noted (done).

## STEP 3 — Write the corpus node

Create `launchpad/docs/corpus/platforms/mobile/application-lifecycle.md` with:

- Front matter: `id: platforms-mobile-application-lifecycle`,
  `type: platforms`, `status: draft`, `origin: launchpad`,
  `audiences: [agent, developer, reviewer]`, a full `evidence` ledger (one
  commit-provenance entry + one entry per substantive claim, each `FACT`
  citing an opened file, with one `INFERENCE` for the `type: platforms`
  choice and one `TEAM_KNOWLEDGE` entry attributing the unmerged #1259
  boundary to that issue), and `relationships: [part-of →
  architecture-containers-mobile, references → architecture-flows-push-notification]`.
- Body: purpose/scope paragraph; Responsibility; Interface/boundary (state
  machine: `AppLifecycleState` → `resumed`/`paused`/`detached` handling,
  `inactive`/`hidden` as explicit no-ops); Dependencies (depends on:
  `RelaySessionNotifier`, `connectivity_plus`, `push_bridge`'s
  `pendingPushNotificationLink`; depended on by: the five consumer
  providers/widgets); Notification-launch handling (cold start vs. warm tap,
  iOS-only today); Boundary (excludes reconnect/backoff internals — #1259's
  subject; excludes relay-side push delivery — already
  `architecture-flows-push-notification`'s subject; excludes deep-link
  parsing/routing detail beyond what's needed to show the lifecycle
  connection); Tests; Scope and omissions (including the Android
  push-notification gap as an explicit, verified-absent fact, not a guess).

**Done when:** the file exists, every DoD bullet from #1253 is satisfied, and
every evidence citation points at a file this session actually opened.

## STEP 4 — Validate without introducing new FAILs

Stash the new file, run `python3 launchpad/project-intelligence/corpus/validate.py`,
record the pre-existing FAIL set, restore the file, re-run, and diff the FAIL
sets — they must be identical (new `UNVERIFIED` notices on this node's own
commit-citation and TEAM_KNOWLEDGE/GitHub-issue citation are expected and are
not FAILs).

**Done when:** the FAIL set before and after adding the file is byte-identical.

## STEP 5 — Earn the commit gate and stop

Run the corpus unittest suite as its own, sole Bash call, then commit with
`git commit -s`. Do not push, do not open a PR — this document is one node in
a future integrated batch PR for Feature #614.

**Done when:** `python3 -m unittest discover ...` reports `OK` and the commit
succeeds (or the documented one-retry-then-BLOCKED fallback is followed).

## GATES

- Schema validation: `python3 launchpad/docs/corpus/schema/node.schema.json`
  conformance (front matter fields, evidence conditional rules).
- Corpus-wide validation: `validate.py` contributes zero new FAIL lines.
- Corpus unit tests: `python3 -m unittest discover -s
  launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- Commit gate: signed commit (`-s`) with the required stamp.

## OPEN

- Whether Android ever gets an equivalent native push bridge is unknown —
  recorded as an explicit "expected but not verified" gap, not asserted
  either way beyond what the current absence of `firebase_messaging` /
  `flutter_local_notifications` in `pubspec.yaml` and the iOS-only guard in
  `push_bridge.dart` establish today.
- Whether `platforms-mobile-relay-connection` (issue #1259) lands before or
  after this node is outside this task's control; no relationship targets it
  because it does not exist on `origin/launchpad` yet.

## LEFT OUT

- Relay-side reconnect/backoff mechanics (`RelaySessionNotifier`'s socket
  factory, exponential backoff, subscription replay internals) — #1259's
  subject, referenced by name only, not restated.
- Relay-side push delivery mechanics (lease acceptance, matcher, delivery
  worker) — already covered by `architecture-flows-push-notification`,
  referenced not duplicated.
- Deep-link URI parsing/community-switching logic in full — only the slice
  relevant to notification-launch routing is described; the general
  `app_links`-based deep-link feature is out of scope for a lifecycle node.
- Any runtime behavior change — this is a documentation-only task.
