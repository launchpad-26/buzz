---
id: verification-e2e-mobile
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
  - statement: "AGENTS.md's 'Testing Conventions' section for the mobile app states a preference for widget tests over unit tests for UI components, directs using ProviderScope(overrides: [...]) to inject fake Riverpod notifiers that extend the real notifier class and override build(), and names WidgetHelpers.testable() as the wrapper for simple widget tests."
    entry_class: FACT
    evidence:
      - "AGENTS.md:633-640"
  - statement: "mobile/pubspec.yaml's dev_dependencies lists flutter_test, flutter_lints, fake_async, camera_platform_interface, crypto, custom_lint, riverpod_lint and mocktail, and does not list integration_test -- the Flutter SDK package that drives a built app on a real or simulated device -- as a dependency."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml:50-59"
  - statement: "No directory or file whose name contains 'integration_test' or 'e2e' exists anywhere under mobile/ at this revision."
    entry_class: FACT
    evidence:
      - "find_paths('mobile -iname *integration_test* -o -iname *e2e*') -> no matches"
  - statement: "At this revision mobile/test/ contains 161 Dart test files. mobile/test/features/channels/channels_page_test.dart is one of them and uses flutter_test's testWidgets (e.g. at line 133) inside a helper that wraps the widget tree in ProviderScope with fake provider overrides (at line 46), matching the widget-test convention AGENTS.md's Testing Conventions section describes; mobile/test/features/channels/channel_messages_provider_test.dart is a sibling example that exercises a Riverpod ProviderContainer directly, with no widget tree at all, against a fake in-memory relay-session notifier rather than a real relay connection."
    entry_class: FACT
    evidence:
      - "count_files('mobile/test', pattern='*_test.dart') -> 161"
      - "mobile/test/features/channels/channels_page_test.dart:46"
      - "mobile/test/features/channels/channels_page_test.dart:133"
      - "mobile/test/features/channels/channel_messages_provider_test.dart"
  - statement: "The 'Mobile' job in .github/workflows/ci.yml runs on ubuntu-latest, installs the Flutter SDK via Hermit, and runs dart format --output=none --set-exit-if-changed ., flutter analyze, flutter test, and then a debug Android APK build; none of those steps launches the mobile app on an emulator, simulator, or physical device, or connects it to a relay."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:954-1011"
  - statement: "The Mobile job runs on every push event regardless of changed paths, and on pull requests only when the repository-wide changes job's dorny/paths-filter reports its mobile filter -- mobile/** plus a fixed list of mobile-release shell scripts -- as changed."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:63-72"
      - ".github/workflows/ci.yml:959"
  - statement: "The Justfile's mobile-check recipe runs dart format --output=none --set-exit-if-changed . and flutter analyze, and its mobile-test recipe runs flutter test, both from mobile/; the full block of mobile-* recipes (install, fmt, fix, check, test, emoji-data, build-android, dev, clean) contains no recipe named or described as an end-to-end or integration test."
    entry_class: FACT
    evidence:
      - "Justfile:735-781"
  - statement: "ADR-0020 states the adopted testing methodology has five levels separated by the infrastructure they need -- unit, integration, relay E2E, desktop E2E smoke, and desktop E2E integration -- and names no mobile E2E level among them; the same decision records 123 Flutter tests as part of the fork's measured test-count baseline as of 2026-08-21."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md:14-19"
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md:50"
  - statement: "AGENTS.md documents desktop E2E as two pnpm scripts run from desktop/ -- pnpm test:e2e:smoke for 'mock-bridge smoke coverage' and pnpm test:e2e:integration for 'relay-backed coverage' -- both of which build and drive the actual desktop app via Playwright; no equivalent script, or any script, is documented anywhere in AGENTS.md or mobile/README.md for driving the built mobile app the same way."
    entry_class: FACT
    evidence:
      - "AGENTS.md:257-258"
      - "mobile/README.md"
  - statement: "No automated test in this repository exercises the built mobile app end-to-end -- that is, driving its UI against a real or mocked relay through a real user flow on a device, simulator, or emulator -- at this revision."
    entry_class: INFERENCE
    evidence:
      - "mobile/pubspec.yaml:50-59"
      - "find_paths('mobile -iname *integration_test* -o -iname *e2e*') -> no matches"
      - ".github/workflows/ci.yml:954-1011"
      - "Justfile:735-781"
    confidence: 0.6
relationships:
  - type: references
    target: architecture-containers-mobile
  - type: implements
    target: corpus-template-test-contract
---

# Mobile end-to-end verification -- test contract

## Purpose and boundary

This node documents the single obligation of whether, and how, the Buzz mobile
(Flutter) client is verified **end-to-end** -- the built app's UI driven
through a real user flow against a real or mocked relay, on a device,
simulator, or emulator -- before a change merges. It covers that one
obligation only: what currently runs in CI and locally for mobile, and
whether any of it is end-to-end in that sense. It does not cover mobile's
widget- and provider-level test suite as a general testing-practice topic (see
*Scope and omissions*), and it does not cover any other platform's end-to-end
suite.

## Obligation

> Before a change under `mobile/**` (or the fixed list of mobile-release
> scripts) merges, or on any push to any branch, the CI `Mobile` job's
> `flutter test` run -- exercising the Flutter widget- and provider-test
> suite under `mobile/test/` -- passes. No automated test in this repository
> drives the built mobile app's UI against a real or mocked relay through an
> end-to-end user flow on a device, simulator, or emulator.

This is stated as one obligation with two halves, in the same register
`docs/multi-tenant-conformance.md` uses for a row that is partly enforced
today and partly an open gap: a positive claim about what actually runs, and
an explicit negative claim about what does not exist. Naming the second half
is the point of filing this node under `verification/e2e/` -- the obligation
this path implies (a real end-to-end tier for mobile) does not exist, and
saying so plainly is the honest content, not a weaker substitute for it.

## Verifying test(s)

- **`mobile/test/**/*_test.dart`** (161 files at this revision), run via
  `flutter test`. These are `flutter_test`-based widget tests
  (`testWidgets`, e.g. `mobile/test/features/channels/channels_page_test.dart`)
  and Riverpod provider tests (`test`, using a bare `ProviderContainer`, e.g.
  `mobile/test/features/channels/channel_messages_provider_test.dart`).
  Widget tests wrap the widget tree in `ProviderScope` with fake notifier
  overrides (per AGENTS.md's Testing Conventions); provider tests construct a
  `ProviderContainer` directly against a fake in-memory relay-session
  notifier. Both run inside Flutter's simulated test binding -- no real
  device, simulator, emulator, or relay connection is involved in either
  case. This is the positive half of the obligation above.
- **No test exists for the negative half.** There is no `integration_test`
  dependency, no `integration_test/` directory, and no CI step or Justfile
  recipe that launches the built app and drives it against a relay. This half
  is not gated or stubbed -- it is simply absent, and no issue was found at
  this revision tracking it by name.

## How to run it

```bash
# From the repository root, activating Hermit first for the pinned Flutter SDK:
. ./bin/activate-hermit
just mobile-test        # flutter test, from mobile/
just mobile-check       # dart format --set-exit-if-changed . && flutter analyze
```

Or directly:

```bash
cd mobile && flutter test
```

CI runs the same `flutter test` invocation (plus format/analyze/lint and a
debug Android APK build) in the `Mobile` job of `.github/workflows/ci.yml`,
unconditionally on every push and, on pull requests, only when the `mobile`
path filter reports a change under `mobile/**` or the listed mobile-release
scripts.

There is no command to run for the negative half, because no such test
exists to invoke.

## Current enforcement status

**Split, as of `473205a7457b208455f188847bfb27b01aa83cac`.**

- The widget/provider-test half is **verified**: `flutter test` runs
  unconditionally in the `Mobile` CI job on every push, and on every pull
  request that touches `mobile/**`, with no `#[ignore]`-style gate. This node
  does not itself include a fresh run of the suite -- see *Limits* -- so
  "verified" here means "runs unconditionally and unskipped," not "was
  observed passing while authoring this node."
- The end-to-end half is **pending**: no test exists. It is not gated
  (there is nothing present to skip) and not stubbed (no `todo!()`- or
  `skip`-marked placeholder names the gap in code); the gap is documented
  only by this node.

## Limits

- **The widget/provider suite proves UI and provider logic against fakes, not
  against a real relay or a real device.** Every relay interaction in the
  cited tests is a hand-built fake notifier or fake session object; none
  opens a real WebSocket to a `buzz-relay` instance, and none runs on an
  actual Android/iOS device, simulator, or emulator. A regression that only
  manifests against real relay wire behaviour, real platform rendering, real
  navigation timing, or real OS-level permissions (camera, notifications,
  secure storage) is outside what this suite can catch.
- **"161 files" and "no integration_test directory" are a snapshot**, not an
  enduring property. Either could change in a later commit without this
  node's evidence being re-checked; see `AGENTS.md`'s rule that a claim
  re-verified at a new revision needs its ledger entry updated in the same
  edit.
- **The INFERENCE above is an absence-of-evidence argument over a checked
  scope, not proof of a negative in general.** It was reached by checking the
  declared dependencies, the `mobile/` directory tree, the CI job's steps,
  and the Justfile's mobile recipes -- not by exhaustively ruling out every
  possible undocumented manual or ad hoc verification process a developer
  might run by hand outside those four places.
- **This node does not assert that the missing end-to-end half is a defect
  Buzz "must" fix.** No ADR, PRD, or accepted decision found while authoring
  this node establishes that mobile requires an end-to-end tier the way
  ADR-0020 establishes desktop's two E2E tiers; asserting that requirement
  here, unsourced, would be exactly the "decision dressed up as a finding"
  `standards/evidence.md` warns against. The gap is reported as a fact about
  the current repository, not issued as a new requirement.

## Scope and omissions

**This node covers** whether an automated end-to-end test exists for the
mobile client, what does run today (the widget/provider-test suite) and how
it differs from end-to-end verification, and how to run what exists.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| General mobile testing conventions and widget-test authoring style | `AGENTS.md`'s "Testing Conventions" section |
| The mobile app's architecture, features, and relay-connection model | `architecture-containers-mobile` |
| Desktop's own end-to-end suites (smoke, integration) | Not yet a corpus node at this revision; documented today in `AGENTS.md` and `TESTING.md` |
| The relay's own `#[ignore]`-gated end-to-end suites in `buzz-test-client` | Not yet a corpus node at this revision; documented today in `TESTING.md` |
| Whether a mobile end-to-end tier *should* be built, and what it should cover | No accepted decision found at this revision; not decided by this node |
| How to cite a test as evidence in a corpus node, generally | `corpus-standard-test-references` |

**Expected but not verified when this node was written:**

- **`flutter test` was not actually executed against this revision while
  authoring this node.** The "verified" enforcement status for the
  widget/provider half rests on reading the CI workflow and the Justfile,
  not on a fresh observed pass. Per `standards/test-references.md` and
  `standards/evidence.md`, "this test currently passes" is a claim with a
  short shelf life that needs an actual run to back it as a `FACT`; none was
  performed here, so no claim above asserts an observed pass.
  `just mobile-test` (equivalently `cd mobile && flutter test`, after
  `. ./bin/activate-hermit`) is the command a future check should run.
- **Whether the `Mobile` CI job is a required status check on the
  `launchpad` branch's ruleset was not checked.** This node only establishes
  that the job runs under the stated conditions, not whether GitHub itself
  blocks a merge on its failure.
- **No manual or exploratory device/simulator testing process outside the
  four sources cited for the INFERENCE above was investigated.** If one
  exists as an unwritten team practice, it is not reflected here and would
  be `TEAM_KNOWLEDGE` this node does not carry.
