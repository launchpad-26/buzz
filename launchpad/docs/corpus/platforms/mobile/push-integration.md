---
id: platforms-mobile-push-integration
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The mobile app's push subsystem talks to native iOS code over a single Flutter MethodChannel named `buzz/push`, declared identically on both sides: Dart's `_channel = MethodChannel('buzz/push')` in push_bridge.dart, and Swift's `FlutterMethodChannel(name: \"buzz/push\", ...)` created in `AppDelegate.didInitializeImplicitFlutterEngine` and routed to `handlePushMethodCall`."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart"
      - "mobile/ios/Runner/AppDelegate.swift"
  - statement: "Dart-to-native calls on `buzz/push` are: `notificationAuthorizationStatus`, `openNotificationSettings`, `startRegistration`, `endpointGrants`, `enrollPush`, `syncPushSnapshot` (handled separately by `BuzzPushSnapshotBridge.handle`), and `takePendingNotificationResponse`; native-to-Dart calls (via `setMethodCallHandler` in push_bridge.dart) are `apnsTokenChanged`, `apnsRegistrationFailed`, and `notificationOpened`."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart"
      - "mobile/ios/Runner/AppDelegate.swift"
      - "mobile/ios/Runner/PushSnapshotBridge.swift"
  - statement: "The Dart-side lease kind constant `buzzPushLeaseKind = 30350` (dev_push_lease.dart:13) matches the relay's registered `KIND_PUSH_LEASE: u32 = 30350` (crates/buzz-core/src/kind.rs:109), so the mobile client and relay agree on the NIP-PL lease event kind."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/dev_push_lease.dart:13"
      - "crates/buzz-core/src/kind.rs:109"
  - statement: "Push subscriptions are modeled as `BuzzPushFilter`/`BuzzPushSubscription`/`BuzzPushSuppression` value objects (push_subscription.dart) that validate kind allow-lists, exact-hex author/tag values, and channel-id shape at construction; `BuzzPushLeaseSubscriptionState` tracks `desired` (client policy) and `accepted` (relay-acknowledged) subscription sets separately, plus a monotonically-advancing lease `generationCursor` and an optional `pendingTombstoneGeneration`, so relay rejection or expiry of a lease is detectable instead of assumed."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_subscription.dart"
  - statement: "`buildDesiredBuzzPushSubscriptions` derives the desired subscription set from exactly the caller's own pubkey (self-directed mentions/approvals) plus the joined, non-archived DM channels the caller is a member of; muted channels are moved into per-subscription `ignore` filters rather than dropped, and every subscription carries a `p_tags_max` suppression to avoid notifying on large ('hellthread') threads. `pushSubscriptionSyncProvider` (push_subscription_provider.dart) recomputes this from `channelsProvider`/`channelMutesProvider` and only includes DM channels the user has joined -- channel-wide (non-DM) traffic is deliberately not subscribed to here, to avoid over-notifying compared with the product's mention/thread-participation predicate."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_subscription.dart"
      - "mobile/lib/shared/push/push_subscription_provider.dart"
  - statement: "`currentRelayPushDescriptorProvider` (push_relay_capability_provider.dart) discovers the active relay's NIP-11 push capability and fails closed on any error: an absent, malformed, or unreachable descriptor is represented as `null`, which `BuzzPushBootstrap` (`buzzPushLifecycleEnabled`) treats as no capability -- no notification-permission prompt, APNs registration, gateway enrollment, or relay lease publication begins without a successfully fetched descriptor."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_relay_capability_provider.dart"
      - "mobile/lib/shared/push/push_bootstrap.dart"
  - statement: "`BuzzPushBootstrap` (push_bootstrap.dart) is a `HookConsumerWidget` that only starts the push lifecycle once the relay session is connected, the active community has a signing `nsec`, a member pubkey is known, and a push-capable descriptor was discovered; it separately gates native APNs registration (`startBuzzPushRegistrationIfCapable`) and lease publication (which additionally requires a non-empty desired subscription set and an APNs device token), and retries either independently on failure via a `BuzzPushAttemptGate` with a five-second backoff."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bootstrap.dart"
  - statement: "Lease publication in `BuzzPushBootstrap._publish` calls `enrollBuzzPush` (native App Attest gateway enrollment via `buzz/push`'s `enrollPush`) and `publishBuzzPushLeaseRecoverably` (reserve a durable lease generation, publish the kind:30350 event through the relay, then mark it accepted) as two independent steps: a code comment in push_bootstrap.dart states 'Relay lease replacement and gateway delegation are independent state machines. Subscription changes advance only the kind-30350 generation; the opaque grant remains reusable until its own authority changes.'"
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bootstrap.dart"
  - statement: "Push state is per-`Community` (mobile/lib/shared/community/community.dart): `pushNotificationsEnabled` (opt-in flag, default false), `pushSubscriptionState` (the `BuzzPushLeaseSubscriptionState` above), and `pushLeaseInstallationId` (a stable per-community installation id assigned at community creation) are fields on the `Community` model, so push is enabled and tracked independently for each connected relay/community rather than globally for the app."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community.dart"
  - statement: "`registerBuzzPushCommunitySnapshot` (push_bridge.dart) exports, over `syncPushSnapshot`, a minimal per-community snapshot (id, name, relay URL, pubkey, authoritative push policies) for every community with `pushNotificationsEnabled`, plus a map of community id to raw 64-byte private key decoded from each community's `nsec` via `Nip19.decode`; a key is only included if it decodes to a well-formed `nsec` payload, and decode failures are silently skipped rather than exported."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart"
  - statement: "On the native side, `BuzzPushSnapshotBridge.handle` (PushSnapshotBridge.swift) routes `syncPushSnapshot` by a `section` argument ('communities', 'profiles', 'channels', 'avatar') into a `BuzzPushPresentationCacheStore` backed by an App Group shared container, and separately replaces exported private keys in the iOS Keychain via `BuzzPushKeychain.replace` (PushNativeState.swift), which deletes prior entries for the same service before writing new per-community `kSecAttrAccessibleAfterFirstUnlock` items."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/PushSnapshotBridge.swift"
      - "mobile/ios/Runner/PushNativeState.swift"
  - statement: "The iOS Notification Service Extension (`NotificationService.swift`, target `NotificationService`) receives every incoming APNs notification and, via `BuzzPushNotificationResolver` (BuzzPushKit), reads the same App Group snapshot file and the same Keychain-stored private key (looked up by community id) to resolve a locally-computed title, body, optional subtitle, thread identifier, and navigation target for the fixed reconnect payload -- entirely from client-cached, previously-synced data, with no network request made by the extension itself in the code read for this node."
    entry_class: FACT
    evidence:
      - "mobile/ios/NotificationService/NotificationService.swift"
      - "mobile/ios/BuzzPushKit/Sources/BuzzPushKit/BuzzPushNotificationResolver.swift"
  - statement: "A resolved notification's navigation target is written back into the delivered notification's `userInfo` (`BuzzPushNavigationTarget.userInfoKey`); when the user taps the notification, `AppDelegate.userNotificationCenter(_:didReceive:withCompletionHandler:)` decodes that target, buffers it in `BuzzPushNavigationBuffer`, and invokes `notificationOpened` on the same `buzz/push` channel (or the buffered value is returned later via `takePendingNotificationResponse` for a cold app launch), which push_bridge.dart turns into a `MessageDeepLink` and publishes on `pendingPushNotificationLink` -- reusing the app's existing deep-link handling rather than a separate notification-routing path."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
      - "mobile/lib/shared/push/push_bridge.dart"
  - statement: "Gateway enrollment (obtaining a `BuzzPushEndpointGrant`) is performed natively by `BuzzDevPushEnrollmentDriver` (BuzzPushKit), invoked from `AppDelegate.handleDevPushEnrollment` only when an APNs device token is already present; the resulting grant is persisted through a `BuzzPushEndpointGrantKeychainStore` and returned to Dart as the result of the `enrollPush` channel call, matching the `BuzzPushEndpointGrant` fields (`relayOrigin`, `relayPubkey`, `installationId`, `endpointGrant`, `endpointHash`, `appProfile`, `endpointEpoch`, `generation`, `expiresAt`) parsed by `BuzzPushEndpointGrant.fromMap` in push_bridge.dart."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
      - "mobile/lib/shared/push/push_bridge.dart"
  - statement: "`BuzzPushLeaseRevocationOutbox` (push_lease_revocation_outbox.dart) durably persists and retries tombstone (lease-cancellation) publication with capped exponential backoff plus jitter, and is triggered both on app-lifecycle resume and on relay reconnection (`BuzzPushBootstrap`'s `useEffect` calling `revocationOutbox.trigger`/`.start`), so disabling push for a community while offline does not silently drop the relay-side cancellation."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_lease_revocation_outbox.dart"
      - "mobile/lib/shared/push/push_bootstrap.dart"
  - statement: "`NostrHTTPAuth.swift` in BuzzPushKit defines a shared `VerifiedNostrEvent` model with `hasValidIDAndSignature()`, used by both the main app target and the Notification Service Extension target so event-shape/signature verification logic is not duplicated between the two Swift targets that both link BuzzPushKit."
    entry_class: FACT
    evidence:
      - "mobile/ios/BuzzPushKit/Sources/BuzzPushKit/NostrHTTPAuth.swift"
  - statement: "As of the recorded revision, no file under `mobile/android` names push, FCM, or Firebase, and `mobile/pubspec.yaml` declares no Firebase/FCM package dependency -- the shipped mobile push integration is iOS/APNs-only; there is no corresponding Android push implementation to document."
    entry_class: FACT
    evidence:
      - "grep_recursive('push|fcm|firebase', scope='mobile/android', case_insensitive=true) -> no matches, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
      - "grep('firebase|fcm', scope='mobile/pubspec.yaml', case_insensitive=true) -> no matches, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Automated coverage for this integration includes nine Dart unit-test files under mobile/test/shared/push/ (one per push_*.dart source file: push_snapshot, push_bridge, push_presentation_cache, push_lease_revocation_outbox, push_subscription_provider, dev_push_lease, push_relay_capability_provider, push_bootstrap, push_subscription) and Swift XCTest targets under mobile/ios/BuzzPushKit/Tests/BuzzPushKitTests/ (PushLeaseTests, BuzzPushNotificationResolverTests, BuzzDevPushEnrollmentDriverTests, BuzzPushConversationResolverTests, BuzzPushNavigationTargetTests, BuzzPushPresentationCacheTests, BuzzPushTranscriptTests) plus mobile/ios/RunnerTests/BuzzCommunicationNotificationTests.swift."
    entry_class: FACT
    evidence:
      - "mobile/test/shared/push/push_snapshot_test.dart"
      - "mobile/test/shared/push/push_bridge_test.dart"
      - "mobile/test/shared/push/push_presentation_cache_test.dart"
      - "mobile/test/shared/push/push_lease_revocation_outbox_test.dart"
      - "mobile/test/shared/push/push_subscription_provider_test.dart"
      - "mobile/test/shared/push/dev_push_lease_test.dart"
      - "mobile/test/shared/push/push_relay_capability_provider_test.dart"
      - "mobile/test/shared/push/push_bootstrap_test.dart"
      - "mobile/test/shared/push/push_subscription_test.dart"
      - "mobile/ios/BuzzPushKit/Tests/BuzzPushKitTests/PushLeaseTests.swift"
      - "mobile/ios/RunnerTests/BuzzCommunicationNotificationTests.swift"
  - statement: "The relay-side flow node `architecture-flows-push-notification` records, as of its own recorded revision, that no mobile or desktop client code in this repository implements NIP-PL; at this node's own later recorded revision that claim is stale for mobile specifically -- the push integration described here now exists -- so this node exists as the counterpart the earlier flow node's own Scope section anticipated revisiting."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
      - "mobile/lib/shared/push/push_bridge.dart"
    confidence: 0.85
  - statement: "`architecture-containers-mobile` and `architecture-flows-push-notification` are both present in the corpus tree on `origin/launchpad` at the recorded revision, confirmed by listing that tree directly rather than this worktree's own branch."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes architecture/containers/mobile.md and architecture/flows/push-notification.md, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
---

# Mobile push notification integration

How the mobile app (`mobile/`) registers for, maintains, and locally resolves
push notifications under NIP-PL (Push Leases): the Flutter/native platform
channel contract, the Dart-side subscription and lease-lifecycle logic, and
the iOS-native enrollment, Keychain/App-Group storage, and Notification
Service Extension that turns a relay wake into a rich local notification.

This node documents the **mobile client's own component**: registration,
subscription policy, lease publication/revocation, and local notification
resolution. It does not restate the relay-side delivery pipeline (trigger,
match, deliver, retry) -- see `architecture-flows-push-notification` for that
-- and it does not restate the full NIP-PL wire protocol or gateway operations,
which remain canonical in `docs/nips/NIP-PL.md` and
`docs/push-gateway-deployment.md` respectively.

## Responsibility

This component is responsible for: discovering whether the connected relay
supports push (NIP-11 descriptor); requesting iOS notification display
authorization and APNs device-token registration independently of each other;
enrolling the installation with the push gateway (App Attest) to obtain an
opaque endpoint grant; deriving the user's desired push subscription policy
from their joined DM channels and mute state; publishing and renewing a
`kind:30350` push lease through the relay; durably retrying lease
cancellation (tombstone) when push is disabled or a publish attempt is lost;
exporting the minimal per-community state and signing keys the iOS
Notification Service Extension needs to resolve a notification entirely
offline; and routing a tapped notification back into the app's existing
deep-link navigation.

It is scoped to iOS. As of the recorded revision no Android/FCM
implementation exists in this repository (see evidence ledger) -- this node
therefore also functions as the current statement of that gap, not merely a
description of a platform choice.

## Public interface: the `buzz/push` platform channel

All Dart/native interaction for this component crosses one Flutter
`MethodChannel` named `buzz/push`.

| Direction | Method | Purpose | Evidence |
|---|---|---|---|
| Dart -> native | `notificationAuthorizationStatus` | Read the current `UNAuthorizationStatus`, mapped to `BuzzPushAuthorizationStatus` | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Dart -> native | `openNotificationSettings` | Deep-link into iOS Settings for this app | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Dart -> native | `startRegistration` | Request display authorization and call `UIApplication.registerForRemoteNotifications()`, independently | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Dart -> native | `endpointGrants` | Read persisted `BuzzPushEndpointGrant`s from the native Keychain-backed store | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Dart -> native | `enrollPush` | Run App Attest gateway enrollment and return a new endpoint grant | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Dart -> native | `syncPushSnapshot` | Write per-community snapshot data (communities/profiles/channels/avatar sections) and signing keys for NSE use | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/PushSnapshotBridge.swift` |
| Dart -> native | `takePendingNotificationResponse` | Pull a cold-start notification tap buffered before the Dart handler attached | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Native -> Dart | `apnsTokenChanged` | Deliver a new APNs device token | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Native -> Dart | `apnsRegistrationFailed` | Report an APNs registration failure | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |
| Native -> Dart | `notificationOpened` | Deliver a warm (foreground/background) notification tap's navigation target | `mobile/lib/shared/push/push_bridge.dart`, `mobile/ios/Runner/AppDelegate.swift` |

Every call is a no-op (or returns a fixed non-iOS default) when
`defaultTargetPlatform != TargetPlatform.iOS`, and `MissingPluginException` is
caught and ignored where a test harness or non-Runner embedding has not
installed the native bridge.

## Subscription policy and lease lifecycle

- **Filter model.** `BuzzPushFilter`/`BuzzPushSubscription`/`BuzzPushSuppression`
  (`mobile/lib/shared/push/push_subscription.dart`) validate kind allow-lists,
  exact-hex author/tag values, and channel-id shape at construction, so an
  invalid subscription cannot be built in the first place.
- **Desired vs. accepted.** `BuzzPushLeaseSubscriptionState` keeps the
  client's `desired` policy and the relay's last `accepted` policy as
  separate sets with an explicit lease `generationCursor`, so relay
  rejection, expiry, or drift is detectable rather than assumed away.
- **Deriving desired subscriptions.** `buildDesiredBuzzPushSubscriptions`
  subscribes to the caller's own self-directed mentions/approvals plus every
  joined, non-archived DM channel; muted channels become `ignore` filters
  rather than being dropped, and a `p_tags_max` suppression bounds
  hellthread notification volume. Non-DM channel-wide traffic is not
  subscribed to here.
- **Discovery gates everything, fail-closed.**
  `currentRelayPushDescriptorProvider` returns `null` on any fetch failure,
  and `BuzzPushBootstrap` treats `null` as "no push capability" -- no
  authorization prompt, APNs registration, gateway enrollment, or lease
  publish begins without a successfully fetched NIP-11 push descriptor.
- **Independent registration and publication.** `BuzzPushBootstrap`
  (`mobile/lib/shared/push/push_bootstrap.dart`) gates native APNs
  registration and relay lease publication as two independent
  `useEffect`-driven attempts, each with its own `BuzzPushAttemptGate` retry
  timer, so a stalled or failed step does not block the other.
  `publishBuzzPushLeaseRecoverably` reserves a durable generation, publishes
  the `kind:30350` event, and only then marks it accepted -- gateway
  delegation and relay lease generation are documented in-source as
  independent state machines.
- **Per-community, opt-in.** Push state (`pushNotificationsEnabled`,
  `pushSubscriptionState`, `pushLeaseInstallationId`) lives on the
  `Community` model (`mobile/lib/shared/community/community.dart`), so a user
  can enable or disable push per connected community.
- **Revocation is durable.** `BuzzPushLeaseRevocationOutbox`
  (`mobile/lib/shared/push/push_lease_revocation_outbox.dart`) persists and
  retries lease tombstones with backoff and jitter, triggered on app resume
  and relay reconnection, so disabling push while offline is not silently
  lost.

## Local notification resolution (offline-first)

NIP-PL's APNs payload carries no message content (see
`architecture-flows-push-notification`), so this component pre-stages the
data a rich local notification needs, entirely client-side:

1. `registerBuzzPushCommunitySnapshot` exports a minimal per-community
   snapshot (id, name, relay URL, pubkey, authoritative push policies) for
   every push-enabled community, plus that community's raw private key
   (decoded and validated from its `nsec`), over `syncPushSnapshot`.
2. Natively, `BuzzPushSnapshotBridge` writes the snapshot into an App
   Group-shared `BuzzPushPresentationCacheStore` and the signing keys into
   the iOS Keychain (`BuzzPushKeychain.replace`, full delete-then-write per
   sync).
3. When APNs delivers a notification, the `NotificationService`
   `UNNotificationServiceExtension` target -- a separate process from the
   main app -- reads that same App Group snapshot and Keychain entry via
   `BuzzPushNotificationResolver` (BuzzPushKit) to compute a title, body,
   optional subtitle, thread identifier, and navigation target, then hands
   the enriched content back to iOS. No network request was observed in the
   extension code read for this node.
4. The resolved navigation target rides in the delivered notification's
   `userInfo`. On tap, `AppDelegate` decodes it and either forwards it
   immediately (`notificationOpened`) or buffers it for cold start
   (`takePendingNotificationResponse`); push_bridge.dart turns either path
   into the same `MessageDeepLink` the app's existing deep-link handling
   already understands.

## Dependencies

**Depends on:**

| Component | Why | Evidence |
|---|---|---|
| Relay NIP-11 push descriptor | Gates the entire push lifecycle (fail-closed) | `mobile/lib/shared/push/push_relay_capability_provider.dart` |
| Relay `kind:30350` lease acceptance | The published lease is the relay-side authority this component's `accepted` state tracks | `mobile/lib/shared/push/dev_push_lease.dart`, `crates/buzz-core/src/kind.rs:109` |
| Push gateway (App Attest enrollment) | Source of the opaque `BuzzPushEndpointGrant` embedded in the lease | `mobile/ios/BuzzPushKit/Sources/BuzzPushKit/BuzzDevPushEnrollmentDriver.swift`, `mobile/ios/Runner/AppDelegate.swift` |
| iOS Keychain + App Group container | Shared storage between the main app and the Notification Service Extension process | `mobile/ios/Runner/PushNativeState.swift`, `mobile/ios/Runner/PushSnapshotBridge.swift` |
| `architecture-containers-mobile` (the mobile container) | This component is one constituent part of that container | `launchpad/docs/corpus/architecture/containers/mobile.md` |

**Depended on by:** no other documented corpus component was found to depend
on this one at the recorded revision; within the mobile app itself,
`pushSubscriptionSyncProvider` is driven by the channels/mutes features
(`mobile/lib/features/channels/`), not the reverse.

## Boundary

This node does not describe:
- The relay-side trigger/match/deliver/retry pipeline, the relay-gateway
  wire protocol, or gateway deployment/secrets/alerting -- see
  `architecture-flows-push-notification` and `docs/push-gateway-deployment.md`.
- The full NIP-PL wire protocol (exact JSON schemas, HTTP route bodies, quota
  parameters) -- see `docs/nips/NIP-PL.md`.
- Any Android/FCM push implementation -- none exists in this repository at
  the recorded revision.
- The mobile container's other responsibilities (relay WebSocket session,
  media, deep links generally, device pairing) -- see
  `architecture-containers-mobile`.
- Per-type internal detail of every `BuzzPushKit` type (e.g. the full
  `BuzzPushNotificationResolver` resolution algorithm or the
  `BuzzPushTranscript` wire format) beyond what is needed to state this
  component's responsibility and interface; those are named as implementation
  paths below rather than restated here.

## Relationships

- part-of: architecture-containers-mobile
- references: architecture-flows-push-notification

## Implementation paths

- `mobile/lib/shared/push/` -- all Dart-side push logic: bridge, bootstrap,
  subscription model, lease descriptor fetch/publish, revocation outbox,
  presentation-cache export.
- `mobile/ios/Runner/AppDelegate.swift` -- `buzz/push` channel registration
  and native APNs/UNUserNotificationCenter integration.
- `mobile/ios/Runner/PushNativeState.swift`,
  `mobile/ios/Runner/PushEndpointGrantStore.swift`,
  `mobile/ios/Runner/PushSnapshotBridge.swift` -- Keychain and App Group
  storage bridged from `syncPushSnapshot`/`enrollPush`/`endpointGrants`.
- `mobile/ios/NotificationService/` -- the `UNNotificationServiceExtension`
  target that resolves a rich local notification offline.
- `mobile/ios/BuzzPushKit/` -- the shared Swift package linked by both the
  `Runner` and `NotificationService` targets (lease model, App Attest
  enrollment driver, notification resolver, presentation cache store, Nostr
  event verification).
- `mobile/test/shared/push/`,
  `mobile/ios/BuzzPushKit/Tests/BuzzPushKitTests/`,
  `mobile/ios/RunnerTests/BuzzCommunicationNotificationTests.swift` -- test
  coverage for the above.

## Scope and omissions

**This node covers** the mobile app's push notification integration as a
standalone component: its platform-channel public interface, subscription
and lease lifecycle, offline notification-resolution design, its
dependencies and boundary, and its current iOS-only scope.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Relay-side trigger/match/deliver/retry pipeline | `architecture-flows-push-notification` |
| Gateway deployment, secrets, alerting | `docs/push-gateway-deployment.md` |
| Full NIP-PL wire protocol | `docs/nips/NIP-PL.md` |
| The mobile container's other responsibilities | `architecture-containers-mobile` |
| Android/FCM push | Not implemented in this repository at the recorded revision |

**Expected but not verified when this node was written:**

- **Whether the Notification Service Extension ever makes a network
  request under some code path not read for this node** (for example, a
  fallback fetch when the App Group snapshot is stale or missing) was not
  exhaustively ruled out; only `NotificationService.swift`'s `didReceive`
  path and `BuzzPushNotificationResolver`'s public surface were read, not
  every internal helper.
- **Whether `mobile/android` will ever gain an FCM implementation, and
  whether this node's iOS-specific interface table would need a parallel
  Android section, is unresolved** -- this node states the current gap, not
  a plan to close it.
- **The exact resolution algorithm inside `BuzzPushNotificationResolver`**
  (how title/body/subtitle/thread-identifier are derived from cached
  profile/channel/message data) was not traced statement-by-statement; this
  node names it as the responsible component, not as a fully audited
  algorithm.
- **Whether any corpus node currently declares a relationship targeting this
  one** was not checked, since no such node can exist before this one
  merges.
