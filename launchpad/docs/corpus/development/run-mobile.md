---
id: development-run-mobile
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Justfile's mobile-dev recipe is a bash script that, when no process named Simulator is running, runs `open -a Simulator` and sleeps 3 seconds; then runs ./scripts/mobile-worktree-overrides.sh, changes into the mobile directory, unsets GIT_DIR and GIT_WORK_TREE, and runs `flutter run` with no further arguments."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The mobile-dev recipe body contains no step that starts Docker, Postgres, Redis, the relay, or any other local service, and no step that passes a relay URL, community, or --dart-define to Flutter."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "AGENTS.md states that `just mobile-dev` 'runs `flutter run` against the app's configured community; it does not start Docker or local relay services', that agents should 'reuse an already-running simulator/emulator and the app's configured staging or production community when that is sufficient', and should 'Do not start or rebuild local relay services unless the task specifically requires relay-side or isolated integration behavior'."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "AGENTS.md instructs contributors not to 'rebuild, reinstall, or relaunch merely for ceremony', to 'Preserve Flutter's incremental build cache and use hot reload/restart where appropriate', to 'Use `flutter clean` only when stale build artifacts are a credible cause', and to 'Run `flutter upgrade` only when the task explicitly requires a toolchain change'."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Justfile's mobile-install recipe unsets GIT_DIR and GIT_WORK_TREE, changes into the mobile directory and runs `flutter pub get`; mobile-clean runs ./scripts/mobile-worktree-clean.sh; mobile-build-android runs ./scripts/mobile-worktree-overrides.sh and then `flutter build apk --debug --no-pub` inside the mobile directory."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile defines no recipe that launches the mobile app on an Android device or emulator: the mobile recipes are mobile-install, mobile-fmt, mobile-fix, mobile-check, mobile-test, mobile-emoji-data, mobile-build-android, mobile-dev and mobile-clean, and mobile-build-android compiles an APK rather than running one."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/mobile-worktree-overrides.sh unsets GIT_DIR and GIT_WORK_TREE, then treats the checkout as a worktree only when `git rev-parse --git-dir` and `git rev-parse --git-common-dir` differ; when they do not differ it deletes mobile/ios/Flutter/WorktreeOverrides.xcconfig and mobile/android/worktree.properties and exits 0."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
  - statement: "In scripts/mobile-worktree-overrides.sh the install identity is derived from the worktree DIRECTORY name (`basename` of the repository root), while the display label is derived from the branch name's final path segment (`${branch##*/}`), or the short SHA when HEAD is detached; both are sanitized, the iOS slug lowercased with non-alphanumerics collapsed to hyphens and the Android slug swapping those hyphens for underscores."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
  - statement: "Running ./scripts/mobile-worktree-overrides.sh from the worktree directory task-865-development-run-mobile on branch task/865-development-run-mobile exited 0 and wrote an iOS BUNDLE_IDENTIFIER of xyz.block.buzz.dogfood.mobile.task-865-development-run-mobile with APP_DISPLAY_NAME `Buzz (865-development-run-mobile)`, and an Android applicationIdSuffix of .task_865_development_run_mobile with appName `Buzz (865-development-run-mobile)` -- confirming in one run that the identifier follows the directory name while the label follows only the branch's final segment."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
      - "bash(./scripts/mobile-worktree-overrides.sh, cwd=__worktrees/task-865-development-run-mobile, revision=aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90) -> exit 0, stdout '📱 Worktree task-865-development-run-mobile: iOS label \"865-development-run-mobile\" (xyz.block.buzz.dogfood.mobile.task-865-development-run-mobile); Android label \"Buzz (865-development-run-mobile)\" (xyz.block.buzz.mobile.task_865_development_run_mobile)'"
      - "cat(mobile/ios/Flutter/WorktreeOverrides.xcconfig) -> 'BUNDLE_IDENTIFIER = xyz.block.buzz.dogfood.mobile.task-865-development-run-mobile' and 'APP_DISPLAY_NAME = Buzz (865-development-run-mobile)'"
      - "cat(mobile/android/worktree.properties) -> 'label=865-development-run-mobile', 'appName=Buzz (865-development-run-mobile)', 'applicationIdSuffix=.task_865_development_run_mobile'"
  - statement: "Both generated override files are gitignored -- mobile/android/.gitignore lists /worktree.properties and /AppOverrides.properties, mobile/ios/.gitignore lists Flutter/AppOverrides.xcconfig and Flutter/WorktreeOverrides.xcconfig -- and `git status --porcelain` reported no output after the generator had written both files."
    entry_class: FACT
    evidence:
      - "mobile/android/.gitignore"
      - "mobile/ios/.gitignore"
      - "git_status(--porcelain, cwd=__worktrees/task-865-development-run-mobile, after running scripts/mobile-worktree-overrides.sh) -> empty output"
  - statement: "mobile/ios/Flutter/Debug.xcconfig sets BUNDLE_IDENTIFIER to xyz.block.buzz.dogfood.mobile and APP_DISPLAY_NAME to Buzz, then includes WorktreeOverrides.xcconfig and finally AppOverrides.xcconfig -- both with the optional `#include?` form -- so a developer's AppOverrides value wins per variable; Release.xcconfig sets BUNDLE_IDENTIFIER to xyz.block.buzz.mobile and includes AppOverrides.xcconfig only, never WorktreeOverrides.xcconfig."
    entry_class: FACT
    evidence:
      - "mobile/ios/Flutter/Debug.xcconfig"
      - "mobile/ios/Flutter/Release.xcconfig"
  - statement: "mobile/android/app/build.gradle.kts reads worktree.properties and AppOverrides.properties from the android project root and applies applicationIdSuffix and the app_name string resource inside the `debug` buildTypes block only, with AppOverrides values taking precedence over the generated worktree values; the `release` block sets only a signing config."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "Flutter is pinned by Hermit at version 3.41.7, and running `flutter --version` after activating Hermit in this worktree reported 'Flutter 3.41.7 • channel stable', framework revision cc0734ac71, and 'Tools • Dart 3.11.5', satisfying mobile/pubspec.yaml's declared `environment: sdk: ^3.11.4`."
    entry_class: FACT
    evidence:
      - "bin/.flutter-3.41.7.pkg"
      - "mobile/pubspec.yaml"
      - "bash(. ./bin/activate-hermit && flutter --version, cwd=__worktrees/task-865-development-run-mobile) -> exit 0, 'Flutter 3.41.7 • channel stable • https://github.com/flutter/flutter.git', 'Framework • revision cc0734ac71 (5 months ago)', 'Tools • Dart 3.11.5 • DevTools 2.54.2'"
  - statement: "Justfile's setup recipe depends on bootstrap and then runs ./scripts/dev-setup.sh; bootstrap warms the Hermit cache by running `cargo --version`, `node --version` and `pnpm --version` only, and a grep of scripts/dev-setup.sh for `mobile` or `flutter` returns no matches -- so neither recipe resolves Flutter packages."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/dev-setup.sh"
      - "grep(-n 'mobile\\|flutter', scripts/dev-setup.sh) -> no matches"
  - statement: "scripts/mobile-worktree-clean.sh uninstalls only bundle identifiers beginning xyz.block.buzz.dogfood.mobile. on booted iOS simulators and only packages matching xyz.block.buzz.mobile.<lowercase-suffix> on connected Android devices, accepts a --dry-run first argument, and prints a closing count; run with --dry-run in this worktree it exited 0 and reported 'no worktree-suffixed Buzz installs found (production apps untouched)'."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-clean.sh"
      - "bash(./scripts/mobile-worktree-clean.sh --dry-run, cwd=__worktrees/task-865-development-run-mobile) -> exit 0, stdout 'no worktree-suffixed Buzz installs found (production apps untouched)'"
  - statement: "mobile/README.md's Run section gives exactly two forms -- `just mobile-dev` from the repo root, described as applying a worktree-isolated debug identity and starting or reusing the Simulator, and `cd mobile && flutter run`, described as using the app's configured community with worktree overrides applied first -- and instructs developers using Xcode, Android Studio or direct `flutter run` to run ./scripts/mobile-worktree-overrides.sh from the repo root once per branch switch to refresh the display label, the install identity being unchanged by a branch switch."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "mobile/README.md states that `mobile-build-android` intentionally builds with --no-pub, and that if an IDE or an external Flutter SDK has touched mobile/.dart_tool the developer should rerun mobile-install with the pinned SDK before building so flutter_test, sky_engine and the engine all come from the same Flutter version."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "The mobile app persists its communities in flutter_secure_storage under the keys buzz_communities and buzz_active_community_id, migrating legacy buzz_workspaces / buzz_relay_url keys on first load, and CommunityStorage.loadAll returns an empty list when neither the current nor any legacy key is present."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart"
  - statement: "Because a worktree-suffixed debug build installs under its own bundle identifier or application id, it does not share the unsuffixed install's secure storage, so the first launch of a newly suffixed build starts with no stored community and needs one configured in the app before it can reach a relay."
    entry_class: INFERENCE
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
      - "mobile/lib/shared/community/community_storage.dart"
      - "mobile/README.md"
    confidence: 0.85
  - statement: "The mobile-dev recipe targets macOS and the iOS Simulator specifically: `pgrep -x Simulator` names the Simulator application process and `open -a Simulator` is macOS's open(1) launching an application by name, neither of which has an equivalent on a Linux or Windows host, so on those hosts the reader must use the direct `flutter run` path instead."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
      - "mobile/README.md"
    confidence: 0.9
  - statement: "At revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90 the development/ directory of the corpus on origin/launchpad contains exactly four nodes -- build.md, debugging.md, hermit.md and prerequisites.md -- and no run-desktop.md, run-relay.md or run-web.md, so no sibling run-* node exists to relate to or defer to."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "git_ls_tree(-r --name-only origin/launchpad -- launchpad/docs/corpus) -> under development/: build.md, debugging.md, hermit.md, prerequisites.md; no run-desktop.md, run-relay.md or run-web.md anywhere in the listing"
  - statement: "Every relationship target declared by this node was read from origin/launchpad rather than from the authoring worktree: development/prerequisites.md carries id development-prerequisites, development/hermit.md carries development-hermit, development/build.md carries corpus-development-build, architecture/containers/mobile.md carries architecture-containers-mobile, layers/configuration/mobile-configuration.md carries layers-configuration-mobile-configuration, and templates/procedure.md carries corpus-template-procedure."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
      - "launchpad/docs/corpus/layers/configuration/mobile-configuration.md"
      - "launchpad/docs/corpus/templates/procedure.md"
      - "git_show(origin/launchpad:launchpad/docs/corpus/development/prerequisites.md) -> 'id: development-prerequisites'"
      - "git_show(origin/launchpad:launchpad/docs/corpus/development/hermit.md) -> 'id: development-hermit'"
      - "git_show(origin/launchpad:launchpad/docs/corpus/development/build.md) -> 'id: corpus-development-build'"
      - "git_show(origin/launchpad:launchpad/docs/corpus/architecture/containers/mobile.md) -> 'id: architecture-containers-mobile'"
      - "git_show(origin/launchpad:launchpad/docs/corpus/layers/configuration/mobile-configuration.md) -> 'id: layers-configuration-mobile-configuration'"
      - "git_show(origin/launchpad:launchpad/docs/corpus/templates/procedure.md) -> 'id: corpus-template-procedure'"
  - statement: "corpus-development-build owns building rather than running: its 'Build a platform frontend' section documents just mobile-build-android as step 4c, producing an unsigned debug APK, and its 'See also' section defers running what was built to a separate node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
  - statement: "No corpus node declares `type: verification` at this revision -- the only two files declaring it are templates/test-contract.md and templates/test-strategy.md -- and launchpad/decisions/ contains no accepted decision governing how the mobile app is run."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/test-contract.md"
      - "launchpad/docs/corpus/templates/test-strategy.md"
      - "grep(-rl '^type: verification', launchpad/docs/corpus/) -> launchpad/docs/corpus/templates/test-contract.md, launchpad/docs/corpus/templates/test-strategy.md (no other file)"
      - "grep(-i 'mobile\\|flutter\\|worktree\\|run', over the filenames listed by ls of launchpad/decisions/) -> ADR-0013-config-management-ubuntu-baseline-runtime-shape.md only, matched on 'run' inside 'runtime'; it concerns the Ubuntu baseline runtime shape, not the mobile app"
  - statement: "relationships.schema.json states implements' directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)', depends-on's as 'source requires target to be true/current for source's own claims to hold', and references' as 'source cites target as supporting context; no ownership or currency dependency implied'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Issue #865's definition of done requires that the node state goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands and configuration rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#865 definition of done"
  - statement: "Issue #865's definition of done also requires that any newly discovered second concept, contract or procedure be filed as a separate task rather than folded into this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#865 definition of done"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: depends-on
    target: development-hermit
  - type: references
    target: development-prerequisites
  - type: references
    target: corpus-development-build
  - type: references
    target: architecture-containers-mobile
  - type: references
    target: layers-configuration-mobile-configuration
---

# Run the Buzz mobile app

Launch the Flutter mobile client on a simulator, emulator or device and iterate on
it, with a debug identity that does not collide with any other checkout of this
repository. Compiling an APK is a different task and belongs to
`corpus-development-build`; this node covers getting a running app in front of you
and keeping it running.

## Before you start

- **The Hermit toolchain is activated.** Run `. ./bin/activate-hermit` from the
  repository root so `./bin` leads `PATH` and the pinned Flutter wins over any
  system or Homebrew install. Flutter is pinned at **3.41.7** by
  `bin/.flutter-3.41.7.pkg`; with Hermit active, `flutter --version` reports
  `Flutter 3.41.7 • channel stable` and `Tools • Dart 3.11.5`, which satisfies
  `mobile/pubspec.yaml`'s declared `environment: sdk: ^3.11.4`. Toolchain
  installation itself is `development-hermit`'s and `development-prerequisites`'
  subject, not this node's.
- **Flutter packages are resolved.** Run `just mobile-install` (which unsets
  `GIT_DIR`/`GIT_WORK_TREE` and runs `flutter pub get` inside `mobile/`). This is a
  separate step from `just setup`: `setup` depends on `bootstrap` and then runs
  `scripts/dev-setup.sh`, `bootstrap` warms only the `cargo`, `node` and `pnpm`
  Hermit packages, and `scripts/dev-setup.sh` mentions neither `mobile` nor
  `flutter`. Rerun `just mobile-install` with the pinned SDK if an IDE or an
  external Flutter SDK has touched `mobile/.dart_tool`, so `flutter_test`,
  `sky_engine` and the engine all come from the same Flutter version.
- **A target is available.** An iOS Simulator, an Android emulator, or a connected
  device. `flutter run` selects the target; no `just` recipe boots an Android
  emulator for you.
- **A community is configured in the app.** The app persists its communities in
  `flutter_secure_storage` under `buzz_communities` and `buzz_active_community_id`,
  and `CommunityStorage.loadAll` returns an empty list when neither those nor the
  legacy `buzz_workspaces` / `buzz_relay_url` keys are present. A freshly installed
  worktree-suffixed build therefore starts with nothing stored and needs a community
  added in the app's own UI before it can reach a relay. What those settings mean is
  `layers-configuration-mobile-configuration`'s subject.

**Allowed environment and scope.** These steps run against a simulator, emulator or
device on your own machine, using **the app's already-configured staging or
production community**. Nothing here starts Docker, Postgres, Redis or a local
relay, and the `mobile-dev` recipe body contains no step that does — per `AGENTS.md`,
do not start local relay services unless the task specifically requires relay-side or
isolated integration behavior. This node's steps are all debug-build steps; release
and profile builds keep the production identity and are out of scope.

## 1. Run on the iOS Simulator with `just mobile-dev`

This is the shortest path on macOS, and `AGENTS.md` names it the preferred one for
iOS runtime validation.

1. **Activate Hermit** from the repository root: `. ./bin/activate-hermit`.
2. **Run `just mobile-dev`.** The recipe, in order: starts the Simulator with
   `open -a Simulator` and waits 3 seconds if no process named `Simulator` is already
   running; runs `./scripts/mobile-worktree-overrides.sh`; changes into `mobile/`;
   unsets `GIT_DIR` and `GIT_WORK_TREE`; and runs `flutter run` with no further
   arguments.
3. **Read the identity line the overrides script prints** before Flutter starts. It
   names the bundle identifier and label this build will install under — see
   *3. Understand the worktree debug identity* below for how they are derived.
4. **Select a community in the app** if this identifier has never been installed
   before (see *Before you start*).

**This step is macOS-only.** `pgrep -x Simulator` names the Simulator application
process and `open -a Simulator` is macOS's `open(1)` launching an application by
name; on a Linux or Windows host, use step 2 instead.

## 2. Run directly, or from Xcode or Android Studio

Use this path for Android, for a non-macOS host, or when you want the IDE's debugger.
`mobile/README.md` and `AGENTS.md` both permit it.

1. **Apply the worktree overrides first**, from the repository root:
   `./scripts/mobile-worktree-overrides.sh`. The two files it writes are picked up by
   the native build systems, so a direct `flutter run`, an Xcode build and an Android
   Studio build all inherit the same identity. Re-run it once per branch switch to
   refresh the display label; the install identity does not change with the branch.
2. **Run the app**, either `cd mobile && flutter run`, or build and run the `Runner`
   scheme in Xcode / the `app` configuration in Android Studio.
3. **Select a community in the app** if this identifier has never been installed
   before.

There is no `just` recipe that launches the app on Android. The Justfile's mobile
recipes are `mobile-install`, `mobile-fmt`, `mobile-fix`, `mobile-check`,
`mobile-test`, `mobile-emoji-data`, `mobile-build-android`, `mobile-dev` and
`mobile-clean` — and `mobile-build-android` compiles an APK (`flutter build apk
--debug --no-pub`) rather than running one. Building that APK is
`corpus-development-build`'s step 4c, not this node's.

## 3. Understand the worktree debug identity

`scripts/mobile-worktree-overrides.sh` treats the checkout as a worktree only when
`git rev-parse --git-dir` and `git rev-parse --git-common-dir` differ. In the main
checkout they do not, so the script deletes both override files and exits 0 — the
plain `Buzz` identity is restored and nothing else happens.

In a worktree it writes two gitignored files:

| File | Consumed by |
|---|---|
| `mobile/ios/Flutter/WorktreeOverrides.xcconfig` | `mobile/ios/Flutter/Debug.xcconfig`, via `#include?` **before** `AppOverrides.xcconfig` |
| `mobile/android/worktree.properties` | `mobile/android/app/build.gradle.kts`, inside the `debug` buildTypes block only |

Two different sources feed two different values, and confusing them is the trap:

- **The install identity follows the worktree DIRECTORY name** (`basename` of the
  repository root), lowercased with non-alphanumerics collapsed to hyphens for the
  iOS bundle identifier and to underscores for the Android application id suffix. It
  is stable across branch switches, so one worktree keeps exactly one installed app
  and one login state however many branches it visits.
- **The display label follows only the branch name's FINAL path segment**
  (`${branch##*/}`), or the short SHA when HEAD is detached.

Run in the worktree `task-865-development-run-mobile` on branch
`task/865-development-run-mobile`, the script produced:

```
BUNDLE_IDENTIFIER = xyz.block.buzz.dogfood.mobile.task-865-development-run-mobile
APP_DISPLAY_NAME  = Buzz (865-development-run-mobile)
applicationIdSuffix = .task_865_development_run_mobile
```

The identifier kept the full directory name; the label dropped the `task/` prefix.

**Precedence and blast radius.** On iOS, `Debug.xcconfig` includes
`WorktreeOverrides.xcconfig` before `AppOverrides.xcconfig`, and xcconfig
later-include-wins is per variable, so a developer's personal `BUNDLE_IDENTIFIER` for
device signing beats the worktree default while unset variables still fall through.
`Release.xcconfig` includes `AppOverrides.xcconfig` only and never
`WorktreeOverrides.xcconfig`. On Android, `build.gradle.kts` applies
`applicationIdSuffix` and the `app_name` resource inside the `debug` block only, with
`AppOverrides.properties` taking precedence over the generated `worktree.properties`;
the `release` block sets only a signing config. **Release and profile builds are
unaffected by everything in this section.**

## 4. Verify the app is actually running

- **The overrides script exited 0** and printed one `📱 Worktree …` line naming the
  iOS bundle identifier and Android package it generated.
- **`git status --porcelain` is unchanged** after the script runs. Both generated
  files are gitignored — `mobile/android/.gitignore` lists `/worktree.properties`,
  `mobile/ios/.gitignore` lists `Flutter/WorktreeOverrides.xcconfig` — and in this
  worktree that command produced no output after both files had been written. Any
  output means something other than the generator wrote into the tree.
- **`flutter run` attached** and is printing its own console, offering hot reload and
  hot restart.
- **The launcher shows the labelled app**, e.g. `Buzz (865-development-run-mobile)`,
  not plain `Buzz`, when running from a worktree. Plain `Buzz` from a worktree means
  the overrides did not apply.
- **The app reached its community** rather than sitting on an empty community list.

Reporting a runtime check, per `AGENTS.md`, means naming the device or simulator, the
connected community, and the workflow actually exercised — not merely that the app
launched.

## 5. Iterate, then clean up

**Iterate in place.** Use `flutter run`'s hot reload and hot restart. `AGENTS.md` is
explicit: do not rebuild, reinstall or relaunch merely for ceremony; preserve
Flutter's incremental build cache; use `flutter clean` **only when stale build
artifacts are a credible cause**; run `flutter upgrade` only when the task explicitly
requires a toolchain change.

**Remove stale worktree installs.** `just mobile-clean` runs
`scripts/mobile-worktree-clean.sh`, which uninstalls only bundle identifiers
beginning `xyz.block.buzz.dogfood.mobile.` from booted iOS simulators and only
packages matching `xyz.block.buzz.mobile.<lowercase-suffix>` from connected Android
devices. Unsuffixed production and dogfood installs are never touched. To preview,
call the script directly — `./scripts/mobile-worktree-clean.sh --dry-run` — because
the `just` recipe passes no arguments through. With nothing to remove it exits 0 and
prints `no worktree-suffixed Buzz installs found (production apps untouched)`.

**Revert the identity overrides.** Running `./scripts/mobile-worktree-overrides.sh`
from the **main checkout** deletes both files and restores the plain `Buzz` identity;
from a worktree it rewrites rather than removes them, so deleting
`mobile/ios/Flutter/WorktreeOverrides.xcconfig` and
`mobile/android/worktree.properties` by hand is the way to drop them there. Both are
gitignored, so leaving them in place commits nothing.

## See also

- `corpus-development-build` — compiling the workspace and the platform frontends,
  including `just mobile-build-android`.
- `development-hermit`, `development-prerequisites` — installing and activating the
  pinned toolchain this node assumes is already in place.
- `layers-configuration-mobile-configuration` — what the app's settings and community
  configuration mean.
- `architecture-containers-mobile` — what the mobile client is and how it fits the
  system.
- `mobile/README.md` — the authoritative in-repo run instructions, Android
  `AppOverrides.properties`, iOS push capability and Android release signing.

## Boundary

This node does not describe:

- **Facts to look up rather than actions to perform** — `flutter run`'s full flag
  list, every Justfile recipe, or the complete set of xcconfig variables. No
  reference-shaped corpus node covers the Flutter CLI; this node names only the
  commands and variables its steps use.
- **Acquiring Flutter, Dart or mobile development skill from scratch**, for a
  newcomer — that is a tutorial, which has no corpus template as of this writing.
- **Why the worktree identity scheme exists** or why it is keyed to the directory
  rather than the branch — a concept/explanation node's subject; this node states the
  behaviour as read from the script and the build files.
- **Building the Android APK** — `corpus-development-build` owns it.
- **Running the desktop app, the relay, or the web client** — no corpus node covers
  any of those at this revision.
- **Testing, linting or formatting mobile code** (`just mobile-test`,
  `just mobile-check`, `just mobile-fmt`) — verification, a separate task.
- **Release and profile builds, signing, and distribution** — including Android
  upload-key configuration and iOS dogfood signing, both documented in
  `mobile/README.md` and owned by the release surface.

## Relationships

Declared, each target read from `origin/launchpad` with `git show` rather than from
this worktree:

- `implements` → `corpus-template-procedure`. This node is a template instance of the
  procedure standard, which `relationships.schema.json` names as `implements`' own
  worked example.
- `depends-on` → `development-hermit`, whose directionality the schema states as
  "source requires target to be true/current for source's own claims to hold". Every
  step here assumes the Hermit-pinned Flutter is on `PATH`; the steps do not hold
  without it.
- `references` → `development-prerequisites`, `corpus-development-build`,
  `architecture-containers-mobile`, `layers-configuration-mobile-configuration` —
  supporting context this node defers to rather than restates.

**No verification or decision edge.** The corpus carries no `type: verification`
content node at this revision — the only files declaring that type are the
`templates/test-contract.md` and `templates/test-strategy.md` templates — and no
accepted decision in `launchpad/decisions/` governs running the mobile app, so there
is nothing of either kind to point at. The implementation this node describes is
cited directly in the ledger by path (`Justfile`, the two `scripts/mobile-worktree-*`
scripts, the iOS xcconfigs and the Android Gradle build file) rather than through a
corpus node, because no implementation-reference node covers them.

At the recorded revision, no edge was declared to any `run-*` sibling: the corpus's
`development/` directory on `origin/launchpad` contained exactly `build.md`,
`debugging.md`, `hermit.md` and `prerequisites.md`, with no `run-desktop.md`,
`run-relay.md` or `run-web.md` to target. All three have since landed in this same
integration, so the natural edges now resolve; they are not added here, since wiring
them in under the pressure of a pre-merge fix pass risks the same kind of error this
fix pass exists to catch. Adding them belongs to a dedicated pass across the whole
`development`/`governance`/`releases` shelf once all 37 nodes are stable.

## Scope and omissions

**This node covers** launching the Buzz Flutter mobile client for development — the
`just mobile-dev` path on macOS, the direct `flutter run` / Xcode / Android Studio
path elsewhere, the prerequisites both assume, how the worktree-scoped debug identity
is derived and where it applies, how to tell the app is genuinely running under that
identity, and how to iterate and clean up afterwards.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Compiling the workspace and the platform frontends, including `just mobile-build-android` | `corpus-development-build` |
| Installing and activating the pinned toolchain | `development-hermit`, `development-prerequisites` |
| What the mobile app's settings and community configuration mean | `layers-configuration-mobile-configuration` |
| What the mobile client is architecturally | `architecture-containers-mobile` |
| Running the desktop app, the relay, or the web client | no corpus node at this revision |
| Mobile testing, linting and formatting | no corpus node at this revision |
| Release/profile builds, signing and distribution | `mobile/README.md` and the release surface |
| Flutter CLI reference material | no corpus node at this revision |

**Expected but not verified when this node was written:**

- **`just mobile-dev` was never executed end to end.** Its first action is
  `open -a Simulator`, and no iOS Simulator was reachable from the environment this
  node was checked in. Steps 1.2 and 1.3 describe the recipe body as read from the
  `Justfile`, not an observed run. That the recipe's `flutter run` does start,
  attach to a Simulator and connect to a configured community is the single largest
  unexercised claim here.
- **`flutter run` itself was never executed**, on any target. `flutter --version` was
  run and is cited; nothing beyond it.
- **The generated override files were never consumed by a build.** They were written
  and read back, and the include chain in `Debug.xcconfig` and the `debug` block in
  `build.gradle.kts` were read; no Xcode or Gradle build was run to confirm the values
  reach an installed app. The precedence claims in step 3 rest on reading those two
  build files, not on observing a resulting install.
- **`just mobile-clean` was not observed removing anything.** The underlying script
  was run with `--dry-run` against a host with no booted simulator and no connected
  Android device, so it exercised the "nothing found" branch only. Its
  suffix-matching behaviour is read from the script.
- **Whether an Android run path should get its own `just` recipe** was not decided
  here. The Justfile's absence of one is stated as read, not filed as a defect.
- **`mobile/README.md`'s iOS push, physical-device signing and Android release
  signing sections were read but are not documented here**, being release- and
  device-provisioning subjects rather than steps in running the app for development.
