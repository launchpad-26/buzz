# Plan: issue #1255 — corpus node for platforms/mobile/ios

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/mobile/ios.md` does not exist yet; no
  `platforms/` subtree exists anywhere in the corpus on `origin/launchpad`.
- `launchpad/docs/corpus/architecture/containers/mobile.md` (id
  `architecture-containers-mobile`) already documents the mobile container at
  the Flutter/cross-platform level and is present on `origin/launchpad`, so it
  is a valid relationship target.
- No template exists yet specifically for `type: platforms` documents. Prior
  batch work (per repo memory) settled on `type: platforms` as an inference
  for anything under `platforms/**`, with body shape borrowed from the closest
  fitting existing template (`templates/component.md`) since this issue's own
  DoD bullets ("states responsibility and interface/boundary", "names
  dependencies and collaborators", "links source implementation and tests",
  "component-level behavior only") mirror that template's shape almost
  verbatim.
- `mobile/ios/` is a real, substantial native shell: an Xcode project
  (`Runner.xcodeproj`), a `NotificationService` app extension, a local Swift
  package (`BuzzPushKit`), CocoaPods (`Podfile`), and ~20 native Swift files
  bridging Flutter method channels to native iOS APIs (push, media transcode,
  QR scanner, native UI surfaces).
- `mobile/README.md` already documents worktree-scoped debug identity and the
  iOS push capability at a prose level; this node cites it rather than
  duplicating it, and adds the structured responsibility/interface/dependency
  view the README does not attempt.

## STEP 1 — Confirm scope boundary against sibling issues

Read `mobile/ios/` source directly (Info.plist, entitlements, AppDelegate.swift,
NotificationService, BuzzPushKit/Package.swift, Podfile, xcconfig files,
project.pbxproj signing/target config, mobile-worktree-overrides.sh,
mobile/README.md). Confirm the natural iOS-specific surface: Xcode
project/targets, Info.plist keys, entitlements, native Swift plugin bridge
(method channels), and per-worktree debug identity — while leaving generic
Flutter (#1254) and generic push integration (#1258) undescribed beyond what
is needed to name the iOS-specific piece of each.

**Done when:** every file read is either cited as evidence or explicitly
excluded as out of scope in the body's Boundary section.

## STEP 2 — Draft front matter

`id: platforms-mobile-ios`, `type: platforms` (inferred convention, see
above), `status: draft`, `origin: launchpad`, `audiences: [agent, developer]`
(matching the sibling `architecture-containers-mobile` node's audience
choice), one `relationships` entry (`part-of` → `architecture-containers-mobile`,
confirmed present on `origin/launchpad`). Evidence ledger: one commit citation
for provenance, then one FACT/INFERENCE entry per substantive claim in the
body, each citing a file actually opened in Step 1.

**Done when:** front matter validates against `node.schema.json` structurally
(checked by running `validate.py` in Step 4).

## STEP 3 — Write the body

Sections: purpose/scope, Responsibility, Public interface (method channels +
Info.plist/entitlement keys the Flutter layer relies on), Dependencies
(depends on: BuzzPushKit/swift-secp256k1, CocoaPods-vendored Flutter pods;
depended on by: the Flutter app via `GeneratedPluginRegistrant` and named
method channels), Worktree debug identity, Boundary (explicitly excludes
generic Flutter architecture, generic push-protocol design, Android), Links
to implementation and tests, Relationships, Scope and omissions.

**Done when:** every DoD bullet in issue #1255 has a corresponding section or
sentence, and every claim cited traces to a file opened in Step 1.

## STEP 4 — Validate: no new FAIL entries

Run `python3 launchpad/project-intelligence/corpus/validate.py` with the new
file present, then with it moved aside, and diff the FAIL sets — they must be
identical (the known ~21-22 pre-existing FAILs, unrelated to this node).

**Done when:** the new file contributes zero new FAIL lines.

## STEP 5 — Earn the commit gate and stop

Run the corpus unittest suite as the sole content of one Bash call, then
`git add` + `git commit -s` as a second, separate call. Do not push, do not
open a PR — this task ends at a local commit on `task/1255-mobile-ios`, to be
folded into Feature #614's single integrated draft PR later.

**Done when:** the commit exists locally with a passing verification stamp,
or, on a second consecutive gate refusal, the task is reported BLOCKED per
the orchestrator's finding #5.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`, run as the sole content of its Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` must show zero new FAIL entries versus the pre-existing baseline.
- Every evidence citation must point to a real file this session actually opened; no `path#line=A,B` syntax — line ranges use `path:A-B`.
- The `relationships` target (`architecture-containers-mobile`) must be confirmed present on `origin/launchpad`, not merely in this worktree.

## OPEN

- Whether `type: platforms` is the eventual settled convention for this
  subtree remains an inference (per finding #4) until a platforms-specific
  standard/template lands; this node follows the sibling-batch precedent.
- Whether Android (`mobile/android/`) will get a parallel sibling node under
  `platforms/mobile/android.md` is assumed but not this task's concern.

## LEFT OUT

- Generic Flutter/Dart architecture of the mobile app (state management,
  feature/shared split) — already covered by `architecture-containers-mobile`
  and explicitly the subject of issue #1254, not repeated here beyond a
  boundary-statement pointer.
- The push notification *protocol* (NIP-11 `nip-pl` descriptor, gateway
  enrollment/lease semantics, relay-side rollout gating) — issue #1258's
  subject; this node names only the iOS-side native mechanics (entitlements,
  `NotificationService` extension, keychain/App Group plumbing) that make that
  protocol work on this platform.
- Android-specific platform detail — out of scope for this issue.
