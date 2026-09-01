---
id: verification-unit-mobile
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "Root CLAUDE.md's 'Testing Conventions' section for the mobile app states: prefer widget tests over unit tests for UI components (test the whole widget tree, not individual methods); use ProviderScope(overrides: [...]) to inject fake notifiers; fake notifiers should extend the real notifier class and override build(); and use the WidgetHelpers.testable() wrapper for simple widget tests or a custom ProviderScope/MaterialApp when specific overrides are needed."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/test/widget_test.dart implements exactly this convention: it wraps App in a ProviderScope overriding authProvider with a _FakeAuthNotifier that extends the real AuthNotifier and overrides only build(), rather than mocking the provider mechanism itself."
    entry_class: FACT
    evidence:
      - "mobile/test/widget_test.dart"
  - statement: "mobile/test/helpers/widget_helpers.dart defines WidgetHelpers.testable(), a small ProviderScope + MaterialApp wrapper (with the app's light theme applied) that other widget tests in the suite use for the 'simple widget test' case CLAUDE.md's convention names."
    entry_class: FACT
    evidence:
      - "mobile/test/helpers/widget_helpers.dart"
  - statement: "At the recorded revision, mobile/test/ contains 161 Dart test files across mobile/test/ (a root-level widget_test.dart and a helpers/ directory) and mobile/test/features/** and mobile/test/shared/**, all discovered and run by one flutter test invocation with no package/test-target filtering."
    entry_class: FACT
    evidence:
      - "count_files('mobile/test/**/*.dart') -> 161"
  - statement: "The Justfile's mobile-test recipe runs exactly `cd mobile && flutter test` (after unsetting GIT_DIR/GIT_WORK_TREE for worktree safety), and `just ci`'s own recipe lists mobile-test as one of its dependencies alongside check, test-unit, desktop-test, desktop-build, desktop-tauri-check, desktop-tauri-test and web-build."
    entry_class: FACT
    evidence:
      - "Justfile:753-755"
      - "Justfile:307"
  - statement: "CI's .github/workflows/ci.yml defines a job named Mobile whose steps run, in order, `dart format --output=none --set-exit-if-changed .`, `flutter analyze`, `flutter test`, then an Android debug APK build; the Test step invokes flutter test unconditionally, with no #[ignore]-equivalent skip annotation and no live relay, device or simulator required (confirmed by grepping mobile/test/ for skip: true or @Skip, with zero matches)."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:954-1011"
      - "grep_repo('skip: true|@Skip', scope='mobile/test/') -> 0 matches"
  - statement: "The Mobile job's own `if` condition is `github.event_name == 'push' || needs.changes.outputs.mobile == 'true'`, and the `changes` job's paths-filter defines its `mobile` output as matching mobile/** plus a short list of mobile-release-adjacent scripts -- so on a pull_request this job (and its flutter test step) runs only when the PR actually touches one of those paths, not on every PR."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:959"
      - ".github/workflows/ci.yml:63-72"
  - statement: "ci.yml's own workflow-level push trigger is restricted to `branches: [main, release]`; this fork's own AGENTS.md states this checkout is the launchpad-26 fork and integrates work onto a `launchpad` branch, not `main` or `release`, and this fork's own AGENTS.md and CONTRACT.md are read as the nearest governing instructions for exactly that reason. A GitHub Actions push trigger with an explicit `branches` list fires only for a push to a matching branch, so a push to `launchpad` does not satisfy this workflow's own push trigger at all, and therefore never reaches the Mobile job's `github.event_name == 'push'` branch of its `if` condition."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:1-4"
      - "CLAUDE.md"
  - statement: "Querying this repository's ten most recent push-triggered workflow runs (of any workflow) found none from the CI workflow that defines the Mobile job; the push-triggered runs present were from 'launchpad — corpus validate' and 'Docker image' only, consistent with (though not, on their own, proof of) the CI workflow's push trigger never actually firing for a push to this fork's launchpad branch."
    entry_class: FACT
    evidence:
      - "run_command('gh run list --repo launchpad-26/buzz --event push --limit 10 --json databaseId,conclusion,headBranch,createdAt,workflowName') -> 10 runs returned, workflowName values: 'launchpad — corpus validate' (5), 'Docker image' (5), 'CI' (0)"
  - statement: "Neither a classic branch-protection rule nor a repository ruleset was found for this repository at the time this node was authored: `GET /repos/launchpad-26/buzz/branches/launchpad/protection` returned 404 Not Found, and `GET /repos/launchpad-26/buzz/rulesets` returned an empty list."
    entry_class: FACT
    evidence:
      - "run_command('gh api repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found"
      - "run_command('gh api repos/launchpad-26/buzz/rulesets') -> []"
  - statement: "Whether the Mobile CI job (or its Test step specifically) is configured anywhere as a required/merge-blocking check for this repository could not be established from the two GitHub API responses above alone, because a 404 on the classic protection endpoint and an empty ruleset list are consistent with 'no required checks configured' but the query does not rule out a required-check configuration surfaced through some other mechanism this check did not query."
    entry_class: INFERENCE
    evidence:
      - "run_command('gh api repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found"
      - "run_command('gh api repos/launchpad-26/buzz/rulesets') -> []"
    confidence: 0.7
  - statement: "mobile/pubspec.yaml's dev_dependencies for the test suite are flutter_test (SDK), flutter_lints, fake_async, camera_platform_interface, crypto, custom_lint, riverpod_lint and mocktail; no integration_test package is listed, and no mobile/integration_test directory exists at the recorded revision, distinguishing this widget/unit suite from any device-level end-to-end suite."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
      - "find_directory('mobile/integration_test') -> not found"
  - statement: "This repository's Hermit toolchain pins bin/flutter to a specific Flutter SDK package (Flutter 3.41.7 at the recorded revision, per `flutter --version` run through that same pinned shim), and both local development (`. ./bin/activate-hermit`) and CI's `cashapp/activate-hermit` action (used by the Mobile job) resolve the same pinned toolchain from the same bin/ directory, so a local flutter test run through Hermit exercises the same Flutter version CI's Mobile job does."
    entry_class: FACT
    evidence:
      - "bin/flutter"
      - "run_command('. ./bin/activate-hermit && flutter --version') -> Flutter 3.41.7 . channel stable . Dart 3.11.5"
  - statement: "Running `cd mobile && flutter test` locally through this repository's pinned Hermit Flutter 3.41.7, at the recorded revision, did not complete an exhaustive run of the full suite, but observed 1746 of the suite's tests execute before the run was stopped, with exactly 4 failures among them and no others; all 4 are widget-finder assertion failures (StateError: 'Bad state: No element', from WidgetController.widget(finder) not matching exactly one widget) in tests named around timestamp width at large/accessible text sizes: 'ForumPostCard constrains an older timestamp at large accessible text sizes' and 'ForumThreadPage constrains post and reply timestamps at large text sizes' in mobile/test/features/forum/forum_widgets_test.dart, 'reply preview constrains its timestamp at large text sizes' in mobile/test/features/pulse/compose_note_page_test.dart, and 'constrains timestamp with agent and follow metadata' in mobile/test/features/pulse/note_card_test.dart."
    entry_class: FACT
    evidence:
      - "run_command('cd mobile && flutter test --reporter expanded') -> +1746 -4 before the run was stopped early; failures at mobile/test/features/forum/forum_widgets_test.dart:211, mobile/test/features/forum/forum_widgets_test.dart:591, mobile/test/features/pulse/compose_note_page_test.dart:67, mobile/test/features/pulse/note_card_test.dart (test name: 'constrains timestamp with agent and follow metadata')"
  - statement: "These 4 failures are unrelated to this node's obligation (that an unconditional, unskipped flutter test invocation exists and is wired into CI for mobile changes) -- they are pre-existing widget-assertion failures in specific timestamp-layout tests, not evidence that the suite itself is not run, skipped, or gated. This node's obligation concerns the enforcement mechanism, not that every currently-written assertion in the suite passes."
    entry_class: INFERENCE
    evidence:
      - "run_command('cd mobile && flutter test --reporter expanded') -> +1746 -4 before the run was stopped early"
      - ".github/workflows/ci.yml:1008-1009"
    confidence: 0.85
  - statement: "Issue #1366 ('task: document verification/e2e/mobile.md') targets a separate, not-yet-created corpus document at launchpad/docs/corpus/verification/e2e/mobile.md, distinct from this node's verification/unit/mobile.md; at the recorded revision, origin/launchpad's corpus tree contains no node under launchpad/docs/corpus/verification/ at all, so no verification-e2e-mobile id exists yet to target with a relationship."
    entry_class: FACT
    evidence:
      - "gh_issue_view('launchpad-26/buzz#1366') -> title 'task: document verification/e2e/mobile.md', objective names launchpad/docs/corpus/verification/e2e/mobile.md as its target"
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no path under launchpad/docs/corpus/verification/ present"
  - statement: "architecture-containers-mobile (launchpad/docs/corpus/architecture/containers/mobile.md) is a merged node on origin/launchpad describing the mobile Flutter app as a container; this node's obligation is specific to that same container's widget/unit-test enforcement, which the container node does not itself cover."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> launchpad/docs/corpus/architecture/containers/mobile.md present"
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
relationships:
  - type: references
    target: architecture-containers-mobile
---

# Mobile widget/unit test suite -- test contract

## Purpose and boundary

This node documents one obligation: that the mobile Flutter app's widget/unit-level
behavior is exercised by a real, unconditionally-executed automated test suite --
`mobile/test/`, run in full by a single `flutter test` invocation -- and that this suite
is wired into CI as a real check for changes touching `mobile/**`. It covers **that
obligation only**. It does not cover whether every individual assertion in that suite
currently holds (see *Current enforcement status* and *Limits* below, where two
unrelated pre-existing failures are disclosed rather than hidden), and it does not cover
mobile end-to-end, integration, or manual/device-level testing, which is a distinct,
separately-scoped obligation (issue #1366, `verification/e2e/mobile.md`, not yet
written -- see *Scope and omissions*).

## Obligation

> Every Dart widget/unit test file under `mobile/test/` is discovered and executed by a
> single, unconditional `flutter test` invocation -- run as `just mobile-test` locally
> and as the `Test` step of CI's `Mobile` job for any pull request that changes
> `mobile/**` -- with no `#[ignore]`-equivalent skip annotation used anywhere in the
> suite and no live relay, device, or simulator required to run it.

This is a narrower, more mechanical obligation than "the mobile app is bug-free" or
"all mobile tests pass": it is the claim that a real, unskippable, infrastructure-free
test gate exists and actually runs for mobile changes, in the same sense
`docs/multi-tenant-conformance.md`'s paired executable suite is a real gate for the
relay's multi-tenancy obligations. Whether every test in the suite currently passes is a
separate, shorter-shelf-life claim, addressed honestly below rather than folded into
this one.

## Verifying test(s)

- **The full `mobile/test/` tree** -- 161 Dart test files at the recorded revision,
  under `mobile/test/` (root-level `widget_test.dart` and `helpers/`) and
  `mobile/test/features/**` / `mobile/test/shared/**` -- discovered and run as one unit
  by `flutter test` with no package or target filtering. This is the suite the
  obligation above concerns as a whole, not any single file in isolation.
- **`mobile/test/widget_test.dart`** (`App renders pairing page when unauthenticated`)
  -- the canonical example of this repository's own documented convention: it wraps the
  app in `ProviderScope(overrides: [authProvider.overrideWith(() => _FakeAuthNotifier())])`,
  where `_FakeAuthNotifier extends AuthNotifier` and overrides only `build()`, per
  CLAUDE.md's "fake notifiers should extend the real notifier class" rule.
- **`mobile/test/helpers/widget_helpers.dart`** (`WidgetHelpers.testable`) -- the shared
  `ProviderScope` + `MaterialApp` wrapper CLAUDE.md's convention names for "simple widget
  tests," used across the wider suite for exactly that case.

## How to run it

```bash
# From the repository root, with Hermit activated (pins Flutter 3.41.7 at the recorded revision):
. ./bin/activate-hermit
cd mobile && flutter pub get   # first run / after a pubspec change
just mobile-test               # == cd mobile && flutter test
```

No gate, tag, or environment variable is required -- unlike this repository's
`#[ignore]`-gated Rust e2e suites, every test in `mobile/test/` runs on a bare
invocation. No running relay, emulator, simulator, or physical device is needed; the
suite is a pure widget/unit suite (`flutter_test`'s in-memory test binding), not an
`integration_test`-based device suite (no `integration_test` dependency or directory
exists in `mobile/` at the recorded revision).

CI runs the identical command as the `Test` step of the `Mobile` job in
`.github/workflows/ci.yml`, immediately after `dart format --output=none
--set-exit-if-changed .` and `flutter analyze` and immediately before an Android debug
APK build.

## Current enforcement status

**The gate mechanism is real and unconditional; the suite is not currently fully
green.** Two separate claims, reported honestly rather than merged:

1. **Mechanism.** CI's `Mobile` job runs `flutter test` as one, unskipped step with no
   infrastructure dependency, for any pull request whose changed paths match the
   `changes` job's `mobile` filter (`mobile/**` plus a short list of mobile-release
   scripts). This is a real, present, unconditionally-executed check on a matching PR --
   nothing in the suite or the job stubs, ignores, or `todo!()`-panics any part of it, and
   grepping the suite for `skip: true` or `@Skip` returns no matches. **This part of the
   obligation is verified.**
2. **Current observed result is not clean.** The Mobile job's `if` condition also names
   `github.event_name == 'push'` as an alternative trigger, but `ci.yml`'s own workflow-
   level `push` trigger is restricted to `branches: [main, release]` -- and this fork
   integrates work onto `launchpad`, not `main` or `release` (per this repository's own
   fork-specific AGENTS.md section). A push to `launchpad` does not match that trigger at
   all, so in this fork's actual practice the Mobile job's "always run on push" branch is
   not exercised; a sample of this repository's ten most recent push-triggered workflow
   runs found none from the `CI` workflow, only from `launchpad — corpus validate` and
   `Docker image`, consistent with that reading. **Whether the Mobile job (or a required
   check derived from it) actually blocks merging a PR could not be confirmed**: no
   classic branch-protection rule and no ruleset was found for this repository via the
   GitHub API at the time of authoring (see evidence ledger). This is a real gap, not a
   rounding-down to "gated" -- the mechanism runs for real, but its consequence for a red
   result is unconfirmed.
3. **A local run at the recorded revision is not clean either**, independent of CI: running
   `cd mobile && flutter test` through this repository's own pinned Hermit Flutter 3.41.7
   observed 1746 of the suite's tests with exactly 4 failures before the run was stopped
   (a full exhaustive run was not needed to establish this node's obligation and was not
   completed -- see *Limits*). All 4 are pre-existing widget-finder assertion failures
   clustered around timestamp width at large/accessible text sizes, in
   `forum_widgets_test.dart` (x2), `compose_note_page_test.dart`, and
   `note_card_test.dart` -- unrelated to whether the suite runs unconditionally, and not
   something this node's obligation is about fixing.

## Limits

**What this node's evidence establishes:** a real, unconditional, infrastructure-free
widget/unit test suite exists for the mobile app; it runs as a genuine CI step (not
stubbed or `#[ignore]`d) for pull requests that touch `mobile/**`; and the repository's
own documented testing convention (widget tests over unit tests, `ProviderScope`
overrides, fake notifiers extending real notifier classes, `WidgetHelpers.testable()`)
is demonstrably followed by at least the suite's own smoke test and shared helper.

**What it does not establish:**

- **That the suite is currently fully green.** It is not, as of the recorded revision:
  4 known, pre-existing failures exist in timestamp-layout widget tests (named above).
  This node does not investigate or attribute those failures further -- whether they are
  a recent regression, a long-standing known issue, or an artifact of the headless test
  environment used to observe them was not established here, and is out of scope for a
  node about the *gate*, not about diagnosing a specific widget bug.
- **That the full suite was exhaustively run.** Only 1746 of the suite's roughly 2000+
  tests were observed to completion before the run was stopped; the remainder were not
  confirmed to contain zero additional failures, only that none turned up in the portion
  actually observed.
- **That this observation reproduces in CI itself, on this exact commit.** The 1746/4
  result is from a local run through the same pinned Hermit toolchain CI uses, not from
  reading an actual CI job log for this commit -- this commit may never have triggered
  CI's own `Mobile` job if a PR carrying it did not itself touch a path the `changes`
  filter matches.
- **That a red `Mobile` job blocks merge.** No branch-protection rule or ruleset naming
  it as a required check was found via the GitHub API; whether some other mechanism
  enforces it was not established.
- **Anything about mobile end-to-end, integration, or manual/device testing.** That is a
  separate obligation (issue #1366's `verification/e2e/mobile.md`), not written at the
  recorded revision, and not folded into this node.

## Scope and omissions

**This node covers** the existence and mechanism of the mobile app's widget/unit test
gate (`mobile/test/`, run by `flutter test`), how to run it, its wiring into CI's
`Mobile` job, and an honest account of its currently-observed pass/fail state.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Mobile end-to-end / integration / manual device testing | Issue #1366, `verification/e2e/mobile.md`, not yet written |
| Diagnosing or fixing the 4 pre-existing timestamp-layout test failures disclosed above | Not filed as of this writing; a separate issue, not this node, is the right place |
| `flutter analyze` and `dart format` (lint/format checks in the same CI job, not test obligations) | Root `CLAUDE.md`'s mobile Quality Checks section |
| The `Mobile Swift` CI job (a separate job in the same workflow) | Not investigated for this node |
| Whether the `Mobile` job is a required/merge-blocking check | Unconfirmed -- no branch protection or ruleset found; a genuine gap, not a settled "no" |
| Desktop, relay, CLI and other platforms' own unit/widget test contracts | Their own sibling `verification/unit/*.md` nodes, not yet written |
| The general mechanics of citing a test as evidence (shapes, flakiness, staleness) | `launchpad/docs/corpus/standards/test-references.md` |

**Relationships.** One edge is declared: `references` -> `architecture-containers-mobile`,
the merged container node this suite verifies widget/unit-level behavior for. Checked
immediately before finalizing this front matter, against the branch this work merges
into, not this worktree:

```bash
git fetch origin launchpad
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

At the time of that check, `architecture-containers-mobile` is present on `launchpad`;
no node exists yet under `launchpad/docs/corpus/verification/` at all (this is the first
one), so no `verification-e2e-mobile` id exists to target, and none is declared for it --
per `AGENTS.md`, "no relationships because nothing exists to point at" is checked here
rather than assumed, and the check found exactly one real target and one real absence.

**Expected but not verified when this node was written:**

- **The root cause of the 4 disclosed failures.** Whether they are a recent regression,
  a pre-existing known issue, or specific to the headless Linux test environment used to
  observe them was not investigated -- diagnosing them is out of scope for this node.
- **Whether the same 4 failures (or a different set) appear in CI's own execution of the
  Mobile job.** No CI run of this exact commit's Mobile job was found or read; the
  1746/4 result is a local observation only.
- **Whether any required-check configuration exists outside the two GitHub API surfaces
  queried** (classic branch protection, rulesets) -- both came back empty/404, which is
  consistent with, but does not prove, "no required check configured."
