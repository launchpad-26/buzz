---
id: platforms-mobile-ios
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The iOS platform shell lives at mobile/ios/ and consists of an Xcode project (Runner.xcodeproj / Runner.xcworkspace), a Runner app target, a NotificationService app-extension target, a local Swift package (BuzzPushKit), and CocoaPods-managed Flutter/plugin pods installed via Podfile."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner.xcodeproj/project.pbxproj"
      - "mobile/ios/Podfile"
      - "mobile/ios/BuzzPushKit/Package.swift"
  - statement: "Runner/Info.plist declares the buzz:// custom URL scheme (CFBundleURLTypes), disables FlutterDeepLinkingEnabled, and requests four usage-description strings (NSFaceIDUsageDescription, NSCameraUsageDescription, NSMicrophoneUsageDescription, NSPhotoLibraryUsageDescription/NSPhotoLibraryAddUsageDescription) plus an INSendMessageIntent NSUserActivityTypes entry for Siri/Shortcuts communication-notification integration."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/Info.plist"
  - statement: "Runner/Info.plist reads two custom keys, BuzzAppGroupIdentifier and BuzzKeychainAccessGroup, from build-setting substitutions ($(BUZZ_APP_GROUP_IDENTIFIER), $(AppIdentifierPrefix)$(BUZZ_KEYCHAIN_ACCESS_GROUP)) rather than hardcoded values, so the app-group and keychain-access-group identifiers vary per build configuration and per worktree override without editing the plist."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/Info.plist"
      - "mobile/ios/Flutter/Debug.xcconfig"
  - statement: "Runner/Runner.entitlements grants aps-environment (from $(BUZZ_IOS_PUSH_ENVIRONMENT)), com.apple.developer.devicecheck.appattest-environment, com.apple.developer.usernotifications.communication, an application-groups entry, and a keychain-access-groups entry -- all templated from the same build-setting variables Info.plist reads."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/Runner.entitlements"
  - statement: "NotificationService is a UNNotificationServiceExtension target (NotificationService/Info.plist's NSExtensionPointIdentifier is com.apple.usernotifications.service) whose own entitlements (NotificationService.entitlements) grant only application-groups and keychain-access-groups -- not aps-environment or app-attest -- scoped to the same $(BUZZ_APP_GROUP_IDENTIFIER)/$(BUZZ_KEYCHAIN_ACCESS_GROUP) values as the Runner target, so the extension can read the shared App Group cache and a keychain item the main app wrote, but is not itself a push-registration participant."
    entry_class: FACT
    evidence:
      - "mobile/ios/NotificationService/Info.plist"
      - "mobile/ios/NotificationService/NotificationService.entitlements"
  - statement: "NotificationService.swift's didReceive(_:withContentHandler:) resolves an incoming push's display content via a BuzzPushNotificationResolver built from BuzzPushKit, loading a per-community private key from the Keychain (kSecClassGenericPassword, service \"buzz.push.nse.signing\", account keyed by community ID, scoped to the shared keychain-access-group) and a cached snapshot file from the shared App Group container (BuzzPushPresentationCacheStore.fileName, size-bounded by BuzzPushPresentationCacheStore.maximumSnapshotBytes); if resolution fails or times out (serviceExtensionTimeWillExpire), it falls back to delivering the original, unresolved content rather than dropping the notification."
    entry_class: FACT
    evidence:
      - "mobile/ios/NotificationService/NotificationService.swift"
  - statement: "AppDelegate.swift (Runner/AppDelegate.swift) is a FlutterAppDelegate conforming to FlutterImplicitEngineDelegate; its didInitializeImplicitFlutterEngine(_:) is where every native-to-Flutter bridge for this platform is wired: FlutterMethodChannel instances named buzz/media_upload, buzz/push, buzz/qr_scanner, buzz/inline_photo_picker, buzz/concentric_sheet_surface, and buzz/native_message_action_surface, plus platform-view factory registrations for BuzzInlinePhotoPicker, BuzzConcentricSheetSurface, BuzzJumpToLatestGlassButton, BuzzNavigationGlassButton, BuzzNativeSegmentedControl, BuzzNativeSkinToneControl, BuzzStickyDateGlassHeader, BuzzThemePaginationGlassControl, BuzzNativeAttachmentPopover, BuzzNativeEmojiPicker, BuzzNativeProfileTextEditor, and (iOS 16+) BuzzNativeMessageActionSurface."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
  - statement: "AppDelegate's buzz/push method channel handles startRegistration (calls UNUserNotificationCenter.requestAuthorization for display permission and, independently, UIApplication.registerForRemoteNotifications() for the APNs device token -- the code comments that a denied or failed display-permission prompt must not prevent token registration or gateway enrollment), takePendingNotificationResponse, notificationAuthorizationStatus, openNotificationSettings, endpointGrants (reads BuzzPushEndpointGrantKeychainStore records), and enrollPush (development-only enrollment via BuzzDevPushEnrollmentDriver, requiring a non-empty APNs device token plus relayUrl/gatewayUrl arguments)."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
  - statement: "AppDelegate stores the App Group identifier and keychain access group by reading the same Info.plist keys (BuzzAppGroupIdentifier, BuzzKeychainAccessGroup) that NotificationService.swift reads independently, and constructs a BuzzPushEndpointGrantKeychainStore and BuzzPushSnapshotBridge scoped to those values -- the main app and the notification-service extension are two separate processes sharing state only through the App Group container and the keychain access group, never through in-process calls."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
      - "mobile/ios/NotificationService/NotificationService.swift"
  - statement: "BuzzPushKit (mobile/ios/BuzzPushKit/Package.swift) is a local Swift package, not a CocoaPod: swift-tools-version 5.9, targeting iOS 15 and macOS 12, depending on 21-DOT-DEV/swift-secp256k1 pinned to exact version 0.21.1, with a BuzzPushKitTests test target that also depends on that same secp256k1 package plus a checked-in Fixtures/app_attest_transcripts.json fixture."
    entry_class: FACT
    evidence:
      - "mobile/ios/BuzzPushKit/Package.swift"
  - statement: "The Podfile pins platform :ios, '16.0', disables CocoaPods analytics (COCOAPODS_DISABLE_STATS), and wires the Runner target to Flutter's own generated pod installation (flutter_ios_podfile_setup, flutter_install_all_ios_pods) plus a nested RunnerTests target that inherits Runner's search paths rather than declaring its own pods."
    entry_class: FACT
    evidence:
      - "mobile/ios/Podfile"
  - statement: "project.pbxproj defines a NotificationService PBXNativeTarget (product type wrapper.app-extension, product NotificationService.appex) embedded into the Runner app via an \"Embed App Extensions\" build phase with the RemoveHeadersOnCopy attribute, and every one of NotificationService's three build configurations (Debug/Release/Profile) sets CODE_SIGN_ENTITLEMENTS to NotificationService/NotificationService.entitlements, CODE_SIGN_STYLE to Automatic, DEVELOPMENT_TEAM to the same $(BUZZ_DEVELOPMENT_TEAM) variable as Runner, INFOPLIST_FILE to NotificationService/Info.plist, and PRODUCT_BUNDLE_IDENTIFIER to $(BUNDLE_IDENTIFIER).NotificationService -- i.e. the extension's bundle ID is always Runner's bundle ID with a fixed suffix, never set independently."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner.xcodeproj/project.pbxproj"
  - statement: "project.pbxproj sets Runner's own PRODUCT_BUNDLE_IDENTIFIER to $(BUNDLE_IDENTIFIER) (an xcconfig-level variable, not hardcoded in the project file), and RunnerTests' PRODUCT_BUNDLE_IDENTIFIER to $(BUNDLE_IDENTIFIER).RunnerTests, so all three targets (Runner, RunnerTests, NotificationService) derive their bundle identifiers from one variable resolved per build configuration."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner.xcodeproj/project.pbxproj"
  - statement: "Flutter/Debug.xcconfig sets the tracked defaults BUNDLE_IDENTIFIER = xyz.block.buzz.dogfood.mobile, BUZZ_DEVELOPMENT_TEAM = JMTDPW9CG3, BUZZ_IOS_PUSH_ENVIRONMENT = development, BUZZ_APP_ATTEST_ENVIRONMENT = development, and derives BUZZ_APP_GROUP_IDENTIFIER / BUZZ_KEYCHAIN_ACCESS_GROUP from $(BUNDLE_IDENTIFIER); it then #include?s the gitignored WorktreeOverrides.xcconfig before the gitignored AppOverrides.xcconfig, so xcconfig's later-include-wins ordering makes a developer's personal override always beat the generated worktree default, which in turn always beats the tracked default."
    entry_class: FACT
    evidence:
      - "mobile/ios/Flutter/Debug.xcconfig:1-29"
  - statement: "Flutter/Release.xcconfig sets the tracked defaults BUNDLE_IDENTIFIER = xyz.block.buzz.mobile, CODE_SIGN_STYLE = Automatic, CODE_SIGN_IDENTITY = 'iPhone Developer', BUZZ_DEVELOPMENT_TEAM = EYF346PHUG, BUZZ_IOS_PUSH_ENVIRONMENT = production, and BUZZ_APP_ATTEST_ENVIRONMENT = production, and does not include WorktreeOverrides.xcconfig at all -- only the gitignored AppOverrides.xcconfig -- so Release (and, per Podfile's project mapping of 'Profile' => :release, Profile) builds never pick up worktree-scoped identity."
    entry_class: FACT
    evidence:
      - "mobile/ios/Flutter/Release.xcconfig:1-19"
      - "mobile/ios/Podfile"
  - statement: "scripts/mobile-worktree-overrides.sh detects a linked git worktree (git rev-parse --git-dir differing from --git-common-dir) and, only in that case, writes mobile/ios/Flutter/WorktreeOverrides.xcconfig with BUNDLE_IDENTIFIER = xyz.block.buzz.dogfood.mobile.<worktree-directory-name, lowercased and slugified> and APP_DISPLAY_NAME = Buzz (<branch-or-short-sha label>); in the main checkout (not a worktree) it deletes any stale override file instead."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
  - statement: "mobile/README.md documents that this worktree-scoped iOS bundle identifier is keyed to the worktree directory name (stable across branch switches) rather than the branch name, so one worktree keeps exactly one installed app and its login state across branch switches, and that release/profile builds always keep the production identity -- matching what Flutter/Release.xcconfig's omission of WorktreeOverrides.xcconfig establishes independently."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "mobile/README.md's \"iOS push capability\" section states that every iOS artifact builds and embeds the NotificationService extension and native push bridge unconditionally, that runtime activation is fail-closed and gated on the current relay advertising a fully valid NIP-11 nip-pl descriptor, that Buzz requests display permission and registers with APNs independently once connectivity is authenticated, and that display-permission denial does not gate device-token registration, gateway enrollment, or lease publication -- consistent with the independent requestAuthorization / registerForRemoteNotifications calls this node observed directly in AppDelegate.startPushRegistration."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
      - "mobile/ios/Runner/AppDelegate.swift"
  - statement: "mobile/README.md documents a local physical-device development path that overrides identity and push/attest sandbox environment via a gitignored mobile/ios/Flutter/AppOverrides.xcconfig (BUNDLE_IDENTIFIER, BUZZ_DEVELOPMENT_TEAM, BUZZ_IOS_PUSH_ENVIRONMENT, BUZZ_APP_ATTEST_ENVIRONMENT), and states that enabling Apple's Communication Notifications capability on the Block dogfood and App Store App IDs is a release follow-up not performed by changes in this repository, and that without a matching parent provisioning profile the app cannot be signed for a physical device even though source and unit validation still work."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "mobile/ios/RunnerTests/ contains two XCTest files at this revision: RunnerTests.swift (1205 lines, @testable import Buzz, covering at least AppDelegate.pushAuthorizationStatusName and a HuddleActiveTalkerSelector unit under test) and BuzzCommunicationNotificationTests.swift (282 lines), giving the native iOS layer its own XCTest suite distinct from the Dart-level flutter test suite."
    entry_class: FACT
    evidence:
      - "mobile/ios/RunnerTests/RunnerTests.swift"
      - "mobile/ios/RunnerTests/BuzzCommunicationNotificationTests.swift"
  - statement: "The Runner/ directory contains roughly twenty native Swift files beyond AppDelegate.swift (e.g. HuddleAudioEngine.swift, HuddleMediaPlugin.swift, MediaSanitizer.swift, InlinePhotoPicker.swift, NativeEmojiPicker*.swift, NativeAttachmentPopover*.swift, NativeMessageActionSurface.swift, NativeProfileTextEditor.swift, NativeSkinToneControl.swift, StickyDateGlassHeader.swift, ThemePaginationGlassControl.swift, JumpToLatestGlassButton.swift, ConcentricSheetSurface.swift, PushEndpointGrantStore.swift, PushNativeState.swift, PushSnapshotBridge.swift), each implementing one of the platform-view factories or plugin classes AppDelegate registers -- the native halves of the Flutter method-channel/platform-view bridges named above, rather than application-level business logic."
    entry_class: FACT
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
  - statement: "This node's evidence for AppDelegate's method-channel and plugin registrations names the channel and platform-view identifiers it wires up, but did not open every individual native Swift file listed above (e.g. HuddleAudioEngine.swift's internal audio-engine implementation) to verify their internal behavior beyond what AppDelegate's registration call sites show; that internal detail is out of this node's component-level scope by design, not an oversight."
    entry_class: INFERENCE
    evidence:
      - "mobile/ios/Runner/AppDelegate.swift"
    confidence: 0.9
  - statement: "architecture-containers-mobile (launchpad/docs/corpus/architecture/containers/mobile.md) already documents the mobile app at the cross-platform Flutter/Riverpod level -- state management, feature/shared code organization, the Nostr wire protocol, community model, deep links, security, and release pipeline -- without describing the iOS-specific native shell (Xcode project/targets, Info.plist, entitlements, the NotificationService extension, or native Swift plugin bridges) this node covers, so the two nodes are complementary rather than duplicative."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
relationships:
  - type: part-of
    target: architecture-containers-mobile
---

# iOS Platform (mobile/ios)

This node documents the iOS-specific native shell of the Buzz mobile app:
the Xcode project and its three targets, the Info.plist and entitlements
that grant iOS capabilities, the `NotificationService` app extension, the
local `BuzzPushKit` Swift package, and the native Swift plugin bridge that
connects platform-specific iOS APIs to the cross-platform Flutter/Dart code.
It answers "what does the iOS platform shell provide, and where is the
line between it and the rest of the mobile app?" It does not describe the
Flutter/Dart application itself (`architecture-containers-mobile`, of which
this node is `part-of`) or the Android platform shell.

## Responsibility

The iOS platform shell (`mobile/ios/`) is responsible for everything a Flutter
app cannot do from Dart alone on iOS: declaring the app's iOS capabilities and
identity (bundle identifier, URL scheme, entitlements, usage-description
strings), building and embedding a `UNNotificationServiceExtension` that can
run even when the main app is not, and exposing native iOS APIs (APNs
registration, Keychain, App Group shared storage, `AVFoundation` media
transcoding, native UI surfaces) to the Flutter engine over method channels
and platform views. It is one of two platform shells around the same Dart
codebase — the other is `mobile/android/`, out of scope here.

## Public interface

The contract the Flutter/Dart layer relies on, and that other native code
(the `NotificationService` extension) relies on, is exposed at three levels:

**Flutter method channels**, registered in
`AppDelegate.didInitializeImplicitFlutterEngine(_:)`:

| Channel | Purpose | Evidence |
|---|---|---|
| `buzz/media_upload` | Sanitize/transcode images and video before upload (`sanitizeImageForUpload`, `transcodeImageToJpeg`, `transcodeVideoToMp4`, `generateVideoPoster`, clipboard image read) | `mobile/ios/Runner/AppDelegate.swift` |
| `buzz/push` | Push registration, authorization status, pending-notification handoff, endpoint-grant read, dev enrollment (`startRegistration`, `notificationAuthorizationStatus`, `openNotificationSettings`, `endpointGrants`, `enrollPush`, `takePendingNotificationResponse`) | `mobile/ios/Runner/AppDelegate.swift` |
| `buzz/qr_scanner` | Dynamic Island scanner portal detection, status-bar visibility, success haptic | `mobile/ios/Runner/AppDelegate.swift` |
| `buzz/inline_photo_picker` | `isSupported` capability probe (iOS 17+) | `mobile/ios/Runner/AppDelegate.swift` |
| `buzz/concentric_sheet_surface` | `isSupported` capability probe (iOS 26+) | `mobile/ios/Runner/AppDelegate.swift` |
| `buzz/native_message_action_surface` | `isSupported` capability probe (iOS 16+) | `mobile/ios/Runner/AppDelegate.swift` |

**Platform-view factories** (native UI embedded into the Flutter view tree),
registered the same way: `BuzzInlinePhotoPicker`, `BuzzConcentricSheetSurface`,
`BuzzJumpToLatestGlassButton`, `BuzzNavigationGlassButton`,
`BuzzNativeSegmentedControl`, `BuzzNativeSkinToneControl`,
`BuzzStickyDateGlassHeader`, `BuzzThemePaginationGlassControl`,
`BuzzNativeAttachmentPopover`, `BuzzNativeEmojiPicker`,
`BuzzNativeProfileTextEditor`, and (iOS 16+)
`BuzzNativeMessageActionSurface`.

**Cross-process state**, shared between the `Runner` app and the
`NotificationService` extension (two separate OS processes) only through:

| Mechanism | Key(s) | Evidence |
|---|---|---|
| App Group container | `BuzzAppGroupIdentifier` Info.plist key → `$(BUZZ_APP_GROUP_IDENTIFIER)` | `mobile/ios/Runner/Info.plist`, `mobile/ios/NotificationService/Info.plist` |
| Shared Keychain | `BuzzKeychainAccessGroup` Info.plist key → `$(AppIdentifierPrefix)$(BUZZ_KEYCHAIN_ACCESS_GROUP)`, keychain service `buzz.push.nse.signing` | `mobile/ios/NotificationService/NotificationService.swift` |

## Dependencies

**Depends on** (this platform shell requires these to build/run):

| Dependency | Why | Evidence |
|---|---|---|
| Flutter engine + generated plugin pods | `GeneratedPluginRegistrant`, `flutter_ios_podfile_setup`/`flutter_install_all_ios_pods` install every Dart-declared plugin's iOS pod | `mobile/ios/Podfile`, `mobile/ios/Runner/AppDelegate.swift` |
| `BuzzPushKit` (local Swift package) | Supplies `BuzzPushNotificationResolver`, `BuzzPushNavigationTarget`, `BuzzPushEndpointGrantKeychainStore`, `BuzzDevPushEnrollmentDriver`, `BuzzPushSnapshotBridge`, `BuzzCommunicationNotificationPresenter` used by both `AppDelegate` and `NotificationService` | `mobile/ios/BuzzPushKit/Package.swift`, `mobile/ios/Runner/AppDelegate.swift`, `mobile/ios/NotificationService/NotificationService.swift` |
| `swift-secp256k1` (21-DOT-DEV, pinned `0.21.1`) | `BuzzPushKit`'s own declared dependency, for the `P256K` product | `mobile/ios/BuzzPushKit/Package.swift` |
| CocoaPods | Vendors Flutter's own iOS framework and every plugin pod into the `Runner` target | `mobile/ios/Podfile` |

**Depended on by** (what requires this platform shell):

| Dependent | Why | Evidence |
|---|---|---|
| `NotificationService` extension | Embedded into `Runner` via an "Embed App Extensions" build phase; cannot run standalone | `mobile/ios/Runner.xcodeproj/project.pbxproj` |
| `just mobile-dev` / `scripts/mobile-worktree-overrides.sh` | Writes `WorktreeOverrides.xcconfig`, which `Flutter/Debug.xcconfig` includes, to give debug builds a per-worktree identity | `scripts/mobile-worktree-overrides.sh`, `mobile/ios/Flutter/Debug.xcconfig` |
| Mobile release pipeline (`buzz-releases`, per `RELEASING.md`) | Consumes the Release-configuration bundle identifier and signing settings this shell declares | `mobile/ios/Flutter/Release.xcconfig` |

## Build identity and worktree isolation

Three build configurations (Debug, Release, Profile — `Podfile` maps Profile
to the Release CocoaPods configuration) resolve `BUNDLE_IDENTIFIER`,
`BUZZ_DEVELOPMENT_TEAM`, `BUZZ_IOS_PUSH_ENVIRONMENT`, and
`BUZZ_APP_ATTEST_ENVIRONMENT` from `Flutter/Debug.xcconfig` or
`Flutter/Release.xcconfig`. Debug additionally `#include?`s the gitignored,
generated `WorktreeOverrides.xcconfig` (written by
`scripts/mobile-worktree-overrides.sh` when run from a linked git worktree)
before an optional developer-authored `AppOverrides.xcconfig` — xcconfig's
later-include-wins ordering means a personal override always beats the
worktree default, which always beats the tracked default. Release never
includes `WorktreeOverrides.xcconfig`, so shipped builds always carry the
production identity regardless of which worktree produced them.

## Push notification entitlements and the notification-service extension

`Runner.entitlements` grants `aps-environment`,
`com.apple.developer.devicecheck.appattest-environment`,
`com.apple.developer.usernotifications.communication`, an
`application-groups` entry, and a `keychain-access-groups` entry, all
templated from build-setting variables so Debug and Release resolve
different sandbox/production values. `NotificationService.entitlements`
grants only `application-groups` and `keychain-access-groups` — it is not a
push-registration participant, only a reader of state the main app wrote.
`NotificationService.swift`'s `didReceive(_:withContentHandler:)` resolves
push display content by reading a per-community private key from the shared
Keychain and a cached snapshot from the shared App Group container, falling
back to the original unresolved notification content on failure or
`serviceExtensionTimeWillExpire()` rather than dropping it silently.

## Links to implementation and tests

- `mobile/ios/Runner/AppDelegate.swift` — every method channel and
  platform-view registration for this platform.
- `mobile/ios/Runner/Info.plist`, `mobile/ios/Runner/Runner.entitlements` —
  declared capabilities and identity.
- `mobile/ios/NotificationService/` — the notification-service extension
  (`Info.plist`, `NotificationService.entitlements`,
  `NotificationService.swift`).
- `mobile/ios/BuzzPushKit/Package.swift` — the local Swift package backing
  push resolution on both sides of the extension boundary.
- `mobile/ios/Flutter/Debug.xcconfig`, `mobile/ios/Flutter/Release.xcconfig`,
  `mobile/ios/Runner.xcodeproj/project.pbxproj` — build configuration,
  signing, and per-target settings.
- `scripts/mobile-worktree-overrides.sh` — generates the worktree-scoped
  debug identity this node describes.
- `mobile/ios/RunnerTests/RunnerTests.swift`,
  `mobile/ios/RunnerTests/BuzzCommunicationNotificationTests.swift` — the
  native XCTest suite for this platform shell, run via Xcode/`xcodebuild`,
  distinct from `flutter test`'s Dart-level suite.
- `mobile/README.md` (§ "Worktree-aware debug identity", § "iOS push
  capability") — the existing prose documentation this node adds structure
  to rather than duplicates.

## Boundary

This node does not describe:
- The cross-platform Flutter/Dart application (state management, feature
  organization, the Nostr wire protocol, community model) — see
  `architecture-containers-mobile`, this node's `part-of` target.
- The push notification *protocol* itself (the NIP-11 `nip-pl` descriptor,
  gateway enrollment, lease semantics, relay-side rollout gating) — that is
  a separate corpus task's subject; this node names only the iOS-side native
  mechanics (entitlements, the extension, keychain/App Group plumbing) that
  implement it on this platform.
- The Android platform shell (`mobile/android/`) — a separate, unwritten
  sibling node's subject.
- The internal implementation of each individual native Swift plugin file
  (e.g. `HuddleAudioEngine.swift`'s audio engine internals) beyond the
  method-channel/platform-view contract `AppDelegate` exposes for it — see
  *Scope and omissions* below.
- Crate-level Rust/relay behavior — out of scope for a platform shell node.

## Relationships

- `part-of`: `architecture-containers-mobile` — this node documents one
  platform-specific constituent of the mobile container that node already
  describes at the cross-platform level.

## Scope and omissions

**This node covers** the iOS-specific native shell of the Buzz mobile app:
its Xcode project/target structure, Info.plist and entitlement declarations,
the `NotificationService` app extension and its cross-process state sharing
with the main app, the `BuzzPushKit` local Swift package dependency, the
Flutter method-channel and platform-view bridge `AppDelegate` exposes, build
identity across Debug/Release/Profile, worktree-scoped debug identity, and
where the native XCTest suite lives.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The cross-platform Flutter/Dart application | `architecture-containers-mobile` |
| The push notification protocol (NIP-11 descriptor, gateway, leases) | a separate, not-yet-identified corpus task |
| The Android platform shell | a separate, unwritten sibling node |
| Per-native-plugin internal implementation detail | not yet owned by any corpus node |
| Corpus front-matter contract, node lifecycle, evidence classification | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json` |

**Expected but not verified when this node was written:**

- **Individual native Swift plugin files beyond their `AppDelegate`
  registration call sites were not opened.** `HuddleAudioEngine.swift`,
  `MediaSanitizer.swift`, and the various `Native*.swift` files each
  implement one bridge `AppDelegate` wires up; this node describes the
  contract at the registration boundary, not each file's internal behavior.
- **`xcodebuild`/Xcode was not run.** This node describes the project and
  target configuration as declared in `project.pbxproj` and the `.xcconfig`
  files; it does not confirm the project currently builds or that
  `RunnerTests`/`BuzzCommunicationNotificationTests` currently pass.
- **`BuzzPushKit`'s own test suite (`BuzzPushKitTests`) was not opened**,
  only its `Package.swift` manifest; its internal test coverage of the
  `P256K`-dependent push-resolution logic is unverified here.
- **Whether a sibling `platforms/mobile/android.md` node exists or is
  planned was not checked against `origin/launchpad` beyond confirming no
  `platforms/` subtree exists there at the recorded revision.**
