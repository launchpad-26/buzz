---
id: platforms-mobile-android
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
  - statement: "The Android Gradle module declares namespace/applicationId xyz.block.buzz.mobile, applies the com.android.application, kotlin-android and dev.flutter.flutter-gradle-plugin Gradle plugins in that order, and derives compileSdk/ndkVersion/minSdk/targetSdk/versionCode/versionName from the Flutter Gradle plugin (flutter.compileSdkVersion etc.) rather than pinning numeric SDK levels itself."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "Release signing has two modes selected by the BUZZ_ANDROID_RELEASE_SIGNING environment variable: the default \"upload-keystore\" mode signs with a CI-vended keystore whose four BUZZ_ANDROID_UPLOAD_* credentials (path, password, key alias, key password) must all be present or an assembleRelease/bundleRelease task fails with a GradleException naming the missing ones; \"external\" mode deliberately produces an unsigned release bundle for a separate APK-signing pipeline and fails if any upload keystore credential is also set."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "A configured BUZZ_ANDROID_UPLOAD_KEYSTORE_PATH is validated at task-graph time before a release build proceeds: it must be an absolute path, must resolve outside the repository root, and must be a readable file, each violation raising a distinct GradleException."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "Only the debug build type reads worktree-scoped identity overrides (an applicationIdSuffix matching \\.[a-z][a-z0-9_]* and an app display name) from worktree.properties (generated) and AppOverrides.properties (optional developer override, takes precedence); both files are validated against a regex and rejected with a GradleException if malformed. Release and profile build types never read either file."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "gradle.properties sets org.gradle.jvmargs (8G heap, 4G max metaspace, 512m reserved code cache, heap-dump-on-OOM), android.useAndroidX=true, and two Flutter-migrator-added flags (android.builtInKotlin=false, android.newDsl=false); settings.gradle.kts pins com.android.application to version 8.11.2 and org.jetbrains.kotlin.android to version 2.2.21 and includes the Flutter SDK's own Gradle build via includeBuild against the flutter.sdk path read from local.properties."
    entry_class: FACT
    evidence:
      - "mobile/android/gradle.properties"
      - "mobile/android/settings.gradle.kts"
  - statement: "The main AndroidManifest.xml declares INTERNET, RECORD_AUDIO, MODIFY_AUDIO_SETTINGS, CAMERA, READ_EXTERNAL_STORAGE (maxSdkVersion 32), WRITE_EXTERNAL_STORAGE (maxSdkVersion 28), READ_MEDIA_IMAGES, READ_MEDIA_VIDEO and READ_MEDIA_VISUAL_USER_SELECTED permissions; declares MainActivity as the launcher activity with a second intent-filter matching VIEW/DEFAULT/BROWSABLE for the buzz:// URI scheme, alongside a meta-data entry disabling Flutter's own built-in deep-link handler (flutter_deeplinking_enabled=false) so app_links owns routing in Dart instead; and declares a <queries> block for android.intent.action.PROCESS_TEXT/text-plain, needed by Flutter's ProcessTextPlugin under Android's package-visibility rules."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/AndroidManifest.xml"
  - statement: "The debug and profile build-variant AndroidManifest.xml overlays each add only one additional permission not present in the main manifest -- INTERNET -- explicitly scoped by comment to Flutter tooling needs (hot reload, breakpoints, VM service communication) during development and profiling builds."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/debug/AndroidManifest.xml"
      - "mobile/android/app/src/profile/AndroidManifest.xml"
  - statement: "MainActivity (FlutterFragmentActivity) registers a buzz/media_upload MethodChannel in configureFlutterEngine with four methods -- sanitizeImageForUpload, transcodeImageToJpeg, transcodeVideoToMp4, generateVideoPoster -- plus a synchronous requiresLegacyMediaStoragePermission query answered by an SDK-version check (true at or below Android P); image handling routes through an internal AndroidImageProcessor object that decodes to a color-managed sRGB Bitmap (ImageDecoder on API 28+, BitmapFactory with inPreferredColorSpace on API 26-27, plain BitmapFactory below API 26) and encodes+scrubs through AndroidMediaSanitizer; video transcode-to-MP4 and poster-frame generation each run on a background Thread using MediaExtractor/MediaMuxer and MediaMetadataRetriever respectively, never on the calling thread."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/MainActivity.kt"
  - statement: "MainActivity forwards onRequestPermissionsResult and onDestroy to a HuddleMediaPlugin instance it owns, disposing that plugin (and its native audio engine) in onDestroy."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/MainActivity.kt"
  - statement: "HuddleMediaPlugin is documented in its own class-level KDoc as the 'foreground-only native seam for mobile Huddle media', owning microphone permission, foreground audio-communication routing (AudioManager mode/focus/output device selection, with separate code paths for Android S+ communication-device APIs versus the deprecated speakerphone API below it), and the native realtime Opus engine; it exposes a buzz/huddle_media MethodChannel with getCapabilities, requestMicrophonePermission, openSystemSettings, prepare, start, setMuted, setSpeakerEnabled, playRemoteOpusFrame, removeRemotePeer and stop, and asserts a fixed Huddle Opus v2 media configuration (protocolVersion 2, 48000 Hz, 1 channel, 960-sample frames) in prepare, rejecting any other configuration."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/HuddleMediaPlugin.kt"
  - statement: "HuddleAudioEngine is documented in its own class-level KDoc as 'foreground-only Android Huddle audio engine' where PCM audio never crosses the Flutter boundary: an AudioRecord captures 48 kHz mono PCM which is fed to Android's MediaCodec Opus encoder, whose compressed output is delivered to Flutter as HuddleLocalOpusPacket values; inbound compressed packets are decoded per-peer via MediaCodec and written to per-peer AudioTrack instances (capped at 15 remote peers) mixed by Android's own communication audio mixer, with a bounded per-peer jitter queue (HuddlePacketJitterQueue) and a fixed-capacity active-talker selector (HuddleActiveTalkerSelector) that evicts the quietest or most-inactive peer when a new peer needs a slot."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/HuddleAudioEngine.kt"
  - statement: "HuddleAudioEngine.isSupported() gates Huddle audio availability on whether MediaCodecList reports both an encoder and a decoder for MediaFormat.MIMETYPE_AUDIO_OPUS on the running device, and capture applies AcousticEchoCanceler and NoiseSuppressor when the platform reports them available, while only inspecting (never toggling) AutomaticGainControl so debug diagnostics can report the platform's default AGC state without changing it."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/HuddleAudioEngine.kt"
  - statement: "AndroidMediaSanitizer.scrubPng and scrubJpeg parse the PNG chunk stream and the JPEG marker/segment stream respectively to remove metadata that can leak information: PNG ancillary chunks are dropped unless their four-character type is in an explicit allow-list (cHRM, gAMA, sBIT, sRGB, bKGD, hIST, tRNS, sPLT, acTL, fcTL, fdAT), and JPEG APP0/APP14/other APPn/comment segments are dropped unless they match a narrow structural check (e.g. an APP0 segment is kept only if it starts with the literal JFIF marker and its declared length matches an embedded thumbnail's own declared dimensions)."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/AndroidMediaSanitizer.kt"
  - statement: "AndroidMediaSanitizer's PNG- and JPEG-scrubbing behavior is covered by JVM unit tests (AndroidMediaSanitizerTest, asserting that a canonical sRGB PNG round-trips unchanged, that a Display P3 ICC profile and trailing appended bytes are removed, and equivalently for JPEG); AndroidImageProcessor's sRGB-decode behavior is covered by an instrumented on-device test (AndroidImageProcessorTest, @RunWith(AndroidJUnit4::class)); and HuddleActiveTalkerSelector's eviction policy is covered by a JVM unit test (HuddleActiveTalkerSelectorTest, asserting capacity enforcement and re-activation of an evicted peer)."
    entry_class: FACT
    evidence:
      - "mobile/android/app/src/test/kotlin/xyz/block/buzz/mobile/AndroidMediaSanitizerTest.kt"
      - "mobile/android/app/src/androidTest/kotlin/xyz/block/buzz/mobile/AndroidImageProcessorTest.kt"
      - "mobile/android/app/src/test/kotlin/xyz/block/buzz/mobile/HuddleActiveTalkerSelectorTest.kt"
  - statement: "Justfile's mobile-build-android recipe runs scripts/mobile-worktree-overrides.sh and then `flutter build apk --debug --no-pub` from the mobile/ directory, producing an unsigned debug APK; the sibling mobile-dev recipe runs the same overrides script before `flutter run`."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/mobile-worktree-overrides.sh detects whether the repository checkout is a linked git worktree (comparing `git rev-parse --git-dir` against `--git-common-dir`); when it is, it writes mobile/android/worktree.properties (gitignored) with a label, an app display name defaulting to \"Buzz (<branch-or-short-SHA>)\", and an applicationIdSuffix derived from the worktree directory name (hyphens converted to underscores, prefixed with `w_` if the slug starts with a digit) so debug builds from different worktrees install side by side; in the non-worktree main checkout it deletes any stale override files instead. Both the app-name and the applicationIdSuffix are validated by regex before being written, and Android's build.gradle.kts re-validates the same two patterns when it reads them back."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
      - "mobile/android/app/build.gradle.kts"
  - statement: "Sibling platforms/** corpus nodes authored in earlier batches of parent Feature #614 have already settled on front-matter type: platforms for documents under launchpad/docs/corpus/platforms/, ahead of any platforms-specific template landing in the corpus."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#614 (parent Feature), batch-dispatch convention communicated for this document-authoring task"
---

# Android platform (mobile app)

This node documents the Android-specific concerns of the Buzz mobile app
(`mobile/`, a single Flutter/Dart codebase): the Gradle build and signing
configuration, the `AndroidManifest.xml` permission and component surface,
the native Kotlin plugin layer bridging Flutter to Android platform APIs,
and the local build tooling (`just mobile-build-android`). It answers "what
does Android need that the rest of the Flutter app does not provide for
itself" for an agent or developer working in `mobile/android/`.

## Responsibility

The Android platform layer is responsible for everything the Flutter engine
cannot do on its own on this platform: declaring the app's identity, SDK
targeting and release signing to the Android build system
(`mobile/android/app/build.gradle.kts`, `mobile/android/gradle.properties`,
`mobile/android/settings.gradle.kts`); declaring the app's permissions,
launch activity, deep-link intent filter and package-visibility queries to
the OS (`mobile/android/app/src/main/AndroidManifest.xml` and the
`debug`/`profile` variant overlays); and exposing platform capabilities that
have no cross-platform Flutter equivalent -- color-managed image
decode/encode and metadata scrubbing for uploads, video transcode/poster
generation, and a foreground-only native Opus voice engine for Huddle calls
-- as Flutter method channels implemented in Kotlin under
`mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/`.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `buzz/media_upload` channel: `sanitizeImageForUpload`, `transcodeImageToJpeg`, `transcodeVideoToMp4`, `generateVideoPoster`, `requiresLegacyMediaStoragePermission` | Flutter `MethodChannel` (registered in `MainActivity.configureFlutterEngine`) | Sanitizes/transcodes image and video bytes for upload; reports whether the running SDK needs the legacy (pre-scoped) storage permission | `mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/MainActivity.kt` |
| `buzz/huddle_media` channel: `getCapabilities`, `requestMicrophonePermission`, `openSystemSettings`, `prepare`, `start`, `setMuted`, `setSpeakerEnabled`, `playRemoteOpusFrame`, `removeRemotePeer`, `stop` | Flutter `MethodChannel` (constructed by `MainActivity`, owned by `HuddleMediaPlugin`) | Owns mic permission, audio-focus/output routing and the native Opus engine lifecycle for one Huddle call; `prepare` enforces a fixed 48 kHz/mono/960-sample/protocol-v2 configuration | `mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/HuddleMediaPlugin.kt` |
| `HuddleAudioEngine.isSupported()`, `.start()`, `.stop()`, `.setMuted()`, `.enqueueRemote()`, `.removeRemotePeer()` | Internal Kotlin class, used only by `HuddleMediaPlugin` | Foreground-only capture/playback of compressed Opus frames; PCM never crosses into Dart | `mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/HuddleAudioEngine.kt` |
| `AndroidMediaSanitizer.scrubPng()`, `.scrubJpeg()` | Internal Kotlin object, used by `AndroidImageProcessor` inside `MainActivity.kt` | Removes non-allow-listed PNG ancillary chunks / JPEG APPn-comment segments before an image leaves the device | `mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/AndroidMediaSanitizer.kt` |

## Dependencies

**Depends on** (this Android layer requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `dev.flutter.flutter-gradle-plugin`, the Flutter SDK's own Gradle build (`includeBuild`) | Supplies `compileSdk`/`minSdk`/`targetSdk`/`versionCode`/`versionName`, the Flutter plugin registrant, and the `flutter { source = "../.." }` link back to the shared Dart codebase | `mobile/android/app/build.gradle.kts`, `mobile/android/settings.gradle.kts` |
| `com.android.application` 8.11.2, `org.jetbrains.kotlin.android` 2.2.21 | Android application build and Kotlin compilation | `mobile/android/settings.gradle.kts` |
| `androidx.appcompat:appcompat:1.6.1` | Runtime AndroidX compatibility library used by the app module | `mobile/android/app/build.gradle.kts` |
| `androidx.test.ext:junit`, `androidx.test:runner`, `kotlin("test")` | Test-only: JVM unit tests and instrumented on-device tests | `mobile/android/app/build.gradle.kts` |
| `scripts/mobile-worktree-overrides.sh` (invoked by `just mobile-build-android` / `just mobile-dev`) | Writes the gitignored `worktree.properties` the debug build type reads for its per-worktree app identity | `Justfile`, `scripts/mobile-worktree-overrides.sh` |

**Depended on by**:

| Component | Why | Evidence |
|---|---|---|
| The shared Flutter/Dart app (`mobile/lib/`) | Calls the `buzz/media_upload` and `buzz/huddle_media` method channels this layer exposes for upload sanitization/transcoding and Huddle audio | `mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/MainActivity.kt`, `mobile/android/app/src/main/kotlin/xyz/block/buzz/mobile/HuddleMediaPlugin.kt` |

## Boundary

This node does not describe:
- Generic Flutter/Dart app architecture, state management, or screen
  composition -- covered by sibling corpus tasks for the mobile platform
  (issue #1254), not this Android-specific node.
- Navigation and routing (including how `buzz://` deep links are handled
  once `app_links` receives them in Dart) -- covered by issue #1257; this
  node states only that the Android manifest routes the `buzz://` scheme to
  Flutter and disables Flutter's own built-in deep-link handler so `app_links`
  owns it.
- iOS-platform-specific build/signing/entitlement configuration
  (`mobile/ios/`) -- a distinct platform surface, not this node's subject.
- The relay-side or desktop-side (Tauri) Huddle audio implementations --
  this node covers only the Android native engine.
- Install/usage instructions for a human running the Android app locally --
  `mobile/README.md`, if and when one exists, would be the place for that;
  none was found under `mobile/` at the time this node was written.

## Relationships

None declared. No `platforms/mobile/*` sibling node, nor any other node
documenting the Flutter app generally, exists yet on `origin/launchpad`'s
`launchpad/docs/corpus/` tree at the recorded revision (checked via this
worktree, which was created directly from `origin/launchpad`). The natural
future edges -- `part-of` toward a mobile-platform overview node, or
`references` toward whatever documents `mobile/lib/`'s deep-link handling --
should be added once those nodes exist and are merged, per `AGENTS.md`'s
rule that a relationship target must resolve on the branch being merged
into, not merely in an author's own worktree.

## Scope and omissions

**This node covers** the Android-specific Gradle build and release-signing
configuration, the `AndroidManifest.xml` permission and component surface
across the main/debug/profile variants, the native Kotlin plugin layer
(`MainActivity`, `HuddleMediaPlugin`, `HuddleAudioEngine`,
`AndroidMediaSanitizer`) and its Flutter method-channel contracts, the tests
that exercise that native layer, and the `just mobile-build-android` /
worktree-override build tooling.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Generic Flutter/Dart app structure and state management | Issue #1254 |
| Navigation and deep-link routing once received in Dart | Issue #1257 |
| iOS platform specifics (`mobile/ios/`) | A separate, not-yet-written platform node |
| The relay-side / desktop-side Huddle audio implementations | Out of scope for this node |
| Whether a `platforms`-specific corpus template will later reshape this node's structure | `AGENTS.md`'s own "until the standards land" note; no such template exists yet |

**Expected but not verified when this node was written:**

- **The concrete numeric `compileSdk`/`minSdk`/`targetSdk`/NDK version
  values.** `app/build.gradle.kts` reads these from the Flutter Gradle
  plugin (`flutter.compileSdkVersion`, etc.) rather than pinning them in
  this repository's own Gradle files, so this node states that they are
  Flutter-tool-supplied rather than asserting specific numbers it did not
  independently resolve from the installed Flutter SDK.
- **Whether `mobile/` carries its own `README.md`** with install/usage
  instructions was not exhaustively checked beyond the top-level listing
  used while investigating this node; none was opened or cited here.
- **The `type: platforms` front-matter convention** for `platforms/**`
  nodes is recorded as `TEAM_KNOWLEDGE` above because no merged sibling
  node or template was available in this worktree to independently confirm
  it as a `FACT`; a reviewer with visibility into the other in-flight
  batches of Feature #614 should confirm the convention still holds when
  this node is integrated.
