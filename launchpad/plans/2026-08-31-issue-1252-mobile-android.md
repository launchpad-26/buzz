# Plan: issue #1252 — corpus node platforms/mobile/android.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (`launchpad/docs/corpus/platforms/mobile/android.md` confirmed absent in
  this worktree, checked out from `origin/launchpad` at
  `131b02f989684117d9ab1dd426f1673fa638e523`).
- `launchpad/docs/corpus/schema/node.schema.json` requires `id`, `type`,
  `status`, `origin`, `audiences`, `evidence`; `type` is a closed enum of
  13 values including `platforms`; `relationships` is optional and, if
  present, every `target` must resolve against a node id that exists on the
  merge-target branch (`AGENTS.md` "Creating a node" step 9).
- `launchpad/docs/corpus/templates/component.md` (merged) is the closest
  fitting template — it documents one standalone software component
  (responsibility, public interface, dependencies, boundary) — but it
  prescribes `type: implementation`. Per the orchestrator's known finding
  #4, sibling `platforms/**` nodes already committed in earlier batches of
  this same Feature (#614) have settled on `type: platforms` for consistency
  across the platform-doc family, which is an inference (no
  `platforms`-specific template exists yet) rather than the component
  template's own literal instruction.
- No existing corpus node under `origin/launchpad`'s
  `launchpad/docs/corpus/` tree is a valid `relationships` target for this
  node (no platforms/mobile sibling merged yet; the four/handful of existing
  nodes are meta/governance documents about the corpus itself).
- Real Android-specific implementation exists at `mobile/android/`:
  `app/build.gradle.kts` (Gradle build config, signing modes, worktree debug
  identity), `app/src/main/AndroidManifest.xml` (permissions, deep link
  intent filter, package-visibility query), `app/src/{debug,profile}/AndroidManifest.xml`
  (build-variant INTERNET permission), and native Kotlin plugins under
  `app/src/main/kotlin/xyz/block/buzz/mobile/` (`MainActivity.kt`,
  `HuddleMediaPlugin.kt`, `HuddleAudioEngine.kt`, `AndroidMediaSanitizer.kt`)
  wired to Flutter via method channels. `just mobile-build-android` (Justfile)
  runs `scripts/mobile-worktree-overrides.sh` then
  `flutter build apk --debug --no-pub`.

## STEP 1 — Confirm scope boundary against sibling issues

Read #1252's own DoD (already fetched) and note sibling issues #1254
(Flutter generically) and #1257 (navigation) own adjacent ground. Keep this
node to Android-platform-specific concerns only: Gradle build/signing
config, `AndroidManifest.xml` permissions/components, the native Kotlin
plugin surface, and the `just mobile-build-android` build path. Do not
describe generic Flutter/Dart app structure or navigation.

Done when: a one-paragraph scope statement is drafted that names this
boundary explicitly, for use in the node's Boundary/Scope sections.

## STEP 2 — Draft front matter and evidence ledger

Front matter: `id: platforms-mobile-android`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. No `relationships` (nothing to point at yet, per ALREADY TRUE).
Evidence ledger: one provenance FACT citing commit
`131b02f989684117d9ab1dd426f1673fa638e523`, plus one FACT per substantive
body claim, each citing a real path already opened during investigation
(`mobile/android/app/build.gradle.kts`, `mobile/android/app/src/main/AndroidManifest.xml`,
the four Kotlin source files, `Justfile`, `scripts/mobile-worktree-overrides.sh`).
One TEAM_KNOWLEDGE entry attributing the sibling-batch `type: platforms`
convention to the orchestrator's stated finding, since it is not
independently corroborated by any file in this worktree.

Done when: `evidence` array entries are each traceable to a specific
already-opened file, correctly classed FACT vs TEAM_KNOWLEDGE (no
INFERENCE needed — nothing here requires reasoning beyond what was read).

## STEP 3 — Write the body

Sections: purpose/scope statement naming the Android platform surface;
Gradle build & signing (namespace, compileSdk/minSdk/targetSdk inherited
from the Flutter Gradle plugin, the `upload`/`external` release signing
modes and their required env vars, the worktree debug-identity override
mechanism); Manifest & permissions (table of declared permissions and what
each is for, the `buzz://` deep-link intent filter, the `PROCESS_TEXT`
queries entry, the debug/profile-only INTERNET permission); Native plugin
surface (`MainActivity` method channel `buzz/media_upload` and its four
methods, `HuddleMediaPlugin`'s `buzz/huddle_media` channel and its
responsibility for mic permission/audio focus/output routing,
`HuddleAudioEngine`'s foreground-only Opus capture/playback engine,
`AndroidMediaSanitizer`'s PNG/JPEG metadata scrubbing); Build & tooling
(`just mobile-build-android`, the worktree overrides script); Boundary
naming #1254/#1257 and generic Flutter/Dart content as out of scope; Scope
and omissions per `AGENTS.md` step 8, naming anything expected but not
verified (e.g., actual numeric compileSdk/minSdk/targetSdk values, since
those are supplied by the Flutter tool rather than pinned in this repo's
own Gradle files, and were not independently resolved).

Done when: every DoD bullet in #1252 (responsibility/boundary, dependencies
and collaborators, links to source/tests, component-level-only scope) is
addressed by a named section.

## STEP 4 — Validate in isolation, then commit

Run the corpus unittest suite, then temporarily move the new file aside and
run `validate.py` to record the baseline pre-existing FAIL set, restore the
file, run `validate.py` again and diff the FAIL sets (expect identical set
plus at most non-fatal UNVERIFIED notices on this node's own commit
citation). Commit per the two-call sequence in the task brief.

Done when: `python3 -m unittest discover ...` reports `OK`; the FAIL-set
diff before/after adding the file is empty; the commit is created.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `python3 launchpad/project-intelligence/corpus/validate.py` contributes
  zero new FAIL lines versus the baseline with the new file removed.
- Every evidence citation is a real, opened file path (no bare directories,
  no `#line=` fragments — `path:A-B` form only if a range is used).

## OPEN

- The exact numeric `compileSdk`/`minSdk`/`targetSdk` values are supplied by
  the Flutter Gradle plugin (`flutter.compileSdkVersion` etc. in
  `app/build.gradle.kts`), not pinned anywhere in this repository's own
  Gradle files, so this node states that they are inherited rather than
  citing specific numbers it cannot verify from this repo alone.
- Whether any `platforms`-specific template will later reshape this node
  (per `AGENTS.md`'s "until the standards land" note) is left to a future
  task, per finding #4's own framing.

## LEFT OUT

- Generic Flutter/Dart app architecture, state management (Riverpod/hooks),
  and navigation — owned by sibling issues #1254 and #1257.
- iOS-platform-specific content (`mobile/ios/`) — a separate sibling task's
  subject, not this node's.
- Desktop/Tauri and relay-side Huddle audio handling — out of scope for a
  mobile-platform node.
