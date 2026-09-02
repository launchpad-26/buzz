# Plan — issue #865: document `development/run-mobile.md`

Target: `launchpad/docs/corpus/development/run-mobile.md`
Node id: `development-run-mobile` · type `development` · status `draft` · origin `launchpad`
Shape: procedure node, modelled on `launchpad/docs/corpus/templates/procedure.md`
Branch: `task/865-development-run-mobile` · worktree `__worktrees/task-865-development-run-mobile`
Revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`

## ALREADY TRUE

- The worktree exists on `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`.
- `launchpad/docs/corpus/development/run-mobile.md` **does not exist**
  (`test -f` reports absent; `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  lists only `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md` under `development/`).
- No `run-desktop.md`, `run-relay.md` or `run-web.md` exists in that listing — siblings
  #864/#866/#867 are unlanded, so none of them is a legal relationship target.
- `development/build.md` is merged and owns building, including
  `just mobile-build-android` (its §"Build a platform frontend", step 4c).
- Confirmed relationship targets on `origin/launchpad` (each read with `git show`):
  `development-prerequisites`, `development-hermit`, `corpus-development-build`,
  `architecture-containers-mobile`, `layers-configuration-mobile-configuration`,
  `corpus-template-procedure`.
- ID convention: 48 of 205 non-`schema/` corpus nodes carry a `corpus-` prefix; those are
  the templates/standards/meta documents. Content nodes use `<path>-<stem>`
  (`development-hermit`, `development-prerequisites`, `architecture-containers-mobile`).
  `development-run-mobile` follows the settled form; `corpus-development-build` is a known
  outlier tracked at #2029 and is **not** copied.

## STEP 1 — read the sources that back every claim

Open, in the worktree, and take verbatim notes:

- `Justfile` — `mobile_dir`, `mobile-install`, `mobile-dev`, `mobile-build-android`,
  `mobile-clean`, `mobile-check`, `mobile-test`, `bootstrap`, `setup`.
- `scripts/mobile-worktree-overrides.sh` and `scripts/mobile-worktree-clean.sh`.
- `mobile/README.md` §Setup, §Run, §Worktree-aware debug identity.
- `mobile/ios/Flutter/Debug.xcconfig` and `Release.xcconfig` (include chain).
- `mobile/android/app/build.gradle.kts` (debug build type wiring).
- `mobile/android/.gitignore`, `mobile/ios/.gitignore` (override files are gitignored).
- `mobile/pubspec.yaml` (`environment.sdk`), `bin/.flutter-3.41.7.pkg` (Hermit pin).
- `AGENTS.md` §Mobile App rules (hot reload over ceremony; `flutter clean` only on a
  credible stale-artifact cause; do not start local relay services).

**done-when** every claim intended for the body has a named source file open and read.

## STEP 2 — execute what can honestly be executed

Run and record exact output:

1. `. ./bin/activate-hermit && flutter --version`
2. `./scripts/mobile-worktree-overrides.sh` then `cat` both generated files
3. `./scripts/mobile-worktree-clean.sh --dry-run`
4. `git status --porcelain` (proves the generated files are gitignored)

Do **not** attempt `just mobile-dev` — its body calls `open -a Simulator` and
`pgrep -x Simulator`, macOS-only, and no iOS Simulator exists in this environment.
That gap goes in *Expected but not verified*, stated as a property of the recipe
(macOS/iOS Simulator target), never as a fact about the checking machine's OS.

**done-when** each executed command's real output is captured for the evidence ledger.

## STEP 3 — write the node

Front matter per `node.schema.json`: `id`, `type: development`, `status: draft`,
`origin: launchpad`, `audiences: [developer, agent]`, `evidence`, `relationships`.
First evidence entry is the commit citation for `aef93f2c2…`. FACT entries cite bare
repository paths (checked on disk) or tool-result strings for the executed commands.
INFERENCE entries carry `confidence`. TEAM_KNOWLEDGE entries carry `provided_by` and
no `confidence`.

Body, per the procedure template's required sections:

1. One `#` heading, first line after front matter.
2. Overview — one line: run the Flutter mobile app against a configured community.
3. Before you start — Hermit, `just mobile-install`, a booted simulator/emulator,
   a community already configured in the app.
4. Forked numbered sequences: iOS Simulator via `just mobile-dev`; direct
   `flutter run` / Xcode / Android Studio via the overrides script.
5. Verify it is running; iterate with hot reload; rollback/cleanup
   (`just mobile-clean`, removing the two gitignored override files, `flutter clean`
   only on a credible cause).
6. See also, Boundary, Relationships, Scope and omissions.

**done-when** the file exists, is under 1000 lines, and every body claim maps to a
ledger entry.

## STEP 4 — validate and re-verify

`python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
Then re-open every cited path and re-read the DoD line by line **before** committing
(`git commit --amend` is blocked by `git-safety.sh`).

**done-when** validate.py exits 0 and every DoD bullet is answered from the file.

## STEP 5 — gate, then commit

Sole, unpiped tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then a separate call: `git add` the document and this plan, `git commit -s`.
No `--no-verify`. Stop at the commit.

**done-when** one signed commit contains exactly the node and this plan.

## PARALLEL

None. Steps 1–5 are strictly sequential: step 2's outputs are step 3's evidence, and
step 4 gates step 5.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  reports `OK`, run bare and unpiped as its own tool call.
- Every `relationships[].target` resolves against `origin/launchpad`, not this worktree.
- Exactly one hand-authored corpus document changes.

## BUDGET

Five steps, one document, one plan, one commit. No pushes, no PR, no second node.

## OPEN

- Whether `just mobile-dev` succeeds end to end on a macOS host with a booted
  Simulator is unverified here — no iOS Simulator was reachable. Documented as a gap.
- Whether Android has an equivalent one-command run recipe: the Justfile defines
  `mobile-build-android` (a build, not a run) and no `mobile-dev-android`. Stated as
  read from the Justfile, not as a defect.

## LEFT OUT

- Building the Android APK (`just mobile-build-android`) — `corpus-development-build`
  owns it; referenced, not restated.
- Toolchain installation — `development-prerequisites` and `development-hermit`.
- Mobile settings/configuration semantics — `layers-configuration-mobile-configuration`.
- Mobile architecture and technology choices — `architecture-containers-mobile`.
- `flutter test` / `flutter analyze` — verification, a different task.
- Running desktop, relay or web — siblings #864/#866/#867, unlanded.
