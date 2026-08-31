# Plan: issue #1258 — platforms/mobile/push-integration corpus node

## ALREADY TRUE

- Issue #1258 (parent Feature #614) asks for exactly one new corpus node at
  `launchpad/docs/corpus/platforms/mobile/push-integration.md`, documenting the
  mobile app's push notification integration.
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (confirmed via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`) — this is the first node under `platforms/`.
- No `platforms`-specific template exists under `launchpad/docs/corpus/templates/`.
  Per prior-batch findings, sibling `platforms/**` nodes have settled on
  `type: platforms` as an inference; body shape is adapted from the
  `component.md`/`architecture-component.md` templates (responsibility,
  interface, dependencies, boundary) since the DoD asks for component-level
  behavior, not full-platform behavior.
- Two existing, merged corpus nodes are directly relevant and confirmed present
  on `origin/launchpad`:
  - `architecture-containers-mobile` (`architecture/containers/mobile.md`) —
    the mobile container itself. Natural `part-of` target.
  - `architecture-flows-push-notification` (`architecture/flows/push-notification.md`)
    — the relay-side delivery flow. Its own Scope section states (as of its
    recorded revision) that no mobile/desktop client code implements NIP-PL.
    That is now stale: real mobile push code exists at the current HEAD. This
    new node is the natural `references` counterpart — it does not restate
    relay-side delivery, only the mobile-side registration/receipt half.
- Real mobile push code exists today under `mobile/lib/shared/push/*.dart`,
  `mobile/ios/Runner/Push*.swift`, `mobile/ios/NotificationService/`, and
  `mobile/ios/BuzzPushKit/Sources/BuzzPushKit/*.swift`, with matching Dart
  tests (`mobile/test/shared/push/*_test.dart`) and Swift tests
  (`mobile/ios/BuzzPushKit/Tests/BuzzPushKitTests/*.swift`,
  `mobile/ios/RunnerTests/BuzzCommunicationNotificationTests.swift`).
- Confirmed by inspection: this is an **iOS-only, APNs-only** implementation
  (`kind:30350` / NIP-PL lease). No `mobile/android` push/FCM/Firebase files
  and no Firebase/FCM dependency in `mobile/pubspec.yaml` exist at HEAD
  `131b02f989684117d9ab1dd426f1673fa638e523`.

## STEP 1 — Read schema, AGENTS.md, templates, confirm target absence

Done. `node.schema.json`, `AGENTS.md`, and the `templates/` directory were
read. `platforms/mobile/push-integration.md` does not exist.

## STEP 2 — Investigate the real implementation

Done. Read/grepped:
- Dart: `push_bridge.dart`, `push_bootstrap.dart`, `push_subscription.dart`,
  `push_subscription_provider.dart`, `push_snapshot.dart`,
  `push_relay_capability_provider.dart`, `dev_push_lease.dart` (signatures),
  `push_lease_revocation_outbox.dart` (signatures),
  `push_presentation_cache.dart` (signatures).
- iOS native: `AppDelegate.swift` (`buzz/push` channel wiring),
  `PushNativeState.swift`, `PushSnapshotBridge.swift`,
  `NotificationService.swift`, plus signature-level reads of
  `BuzzPushNotificationResolver.swift`, `PushLease.swift`, `NostrHTTPAuth.swift`,
  `BuzzDevPushEnrollmentDriver.swift`.
- Confirmed `KIND_PUSH_LEASE = 30350` in `crates/buzz-core/src/kind.rs:109`,
  matching the Dart-side `buzzPushLeaseKind = 30350` constant.

## STEP 3 — Write the corpus node

Body shape: responsibility, public interface (the `buzz/push` MethodChannel
contract, both directions), dependencies (relay NIP-11/NIP-PL descriptor,
push gateway, App Group/Keychain, `architecture-containers-mobile`), boundary
(not the relay-side flow, not FCM/Android, not the full mobile container),
relationships (`part-of` the mobile container, `references` the relay flow
node), scope and omissions.

Front matter: `id: platforms-mobile-push-integration`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`.
Every FACT cites a real opened path/line; the "iOS-only, no FCM" claim is a
FACT backed by absence-of-file greps; the App Attest App Group/keychain path
count is exact.

## STEP 4 — Validate

- Run the corpus unit tests (step 5a of the outer task) as the sole content of
  a Bash call.
- Run `python3 launchpad/project-intelligence/corpus/validate.py` with the new
  file present and with it temporarily removed, diff the FAIL sets, confirm
  no new FAILs are introduced.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `validate.py` new-FAIL diff empty.
- `git commit -s` succeeds (commit-gate stamp).

## OPEN

- Whether `type: platforms` is the corpus's permanent convention for
  platform-specific component nodes, or will be superseded once a
  `platforms`-specific template lands, is not settled by this task — it
  follows the existing-batch precedent only.

## LEFT OUT

- Any relay-side or gateway-side content — fully owned by
  `architecture-flows-push-notification` and `docs/push-gateway-deployment.md`.
- FCM/Android push, since no such implementation exists in this repository at
  the recorded revision.
- Per-file exhaustive documentation of every `BuzzPushKit` type (e.g. the full
  `BuzzPushNotificationResolver` resolution algorithm, `BuzzPushTranscript`
  wire format) — named and cited as implementation paths, not restated.
