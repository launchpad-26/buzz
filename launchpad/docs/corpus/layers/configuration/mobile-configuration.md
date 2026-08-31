---
id: layers-configuration-mobile-configuration
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "mobile/lib/shared/relay/relay_provider.dart defines a compile-time Env class whose only field, relayUrl, is read via String.fromEnvironment('BUZZ_RELAY_URL', defaultValue: 'http://localhost:3000'); RelayConfigNotifier.build() falls back to const RelayConfig(baseUrl: Env.relayUrl) only when no active Community is stored."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
  - statement: "mobile/.env.json.example documents two dart-define-from-file keys, BUZZ_RELAY_URL and BUZZ_DEV_PUBKEY, and relay_provider.dart's own doc comment names both `flutter run --dart-define=BUZZ_RELAY_URL=...` and a `.env.json` consumed via `--dart-define-from-file=.env.json` as supported invocation forms."
    entry_class: FACT
    evidence:
      - "mobile/.env.json.example"
      - "mobile/lib/shared/relay/relay_provider.dart"
  - statement: "A search of mobile/lib for String.fromEnvironment and bool.fromEnvironment call sites at this revision finds exactly two compile-time environment variables actually read by application code: BUZZ_RELAY_URL (relay_provider.dart) and BUZZ_MOCK_DM_DIRECTORY (channel_management_provider.dart). BUZZ_DEV_PUBKEY, though documented in .env.json.example, has no fromEnvironment call site anywhere under mobile/lib."
    entry_class: FACT
    evidence:
      - "grep(pattern='fromEnvironment', path='mobile/lib/**/*.dart') -> two matches: mobile/lib/shared/relay/relay_provider.dart (BUZZ_RELAY_URL), mobile/lib/features/channels/channel_management_provider.dart (BUZZ_MOCK_DM_DIRECTORY); no match for BUZZ_DEV_PUBKEY"
  - statement: "channel_management_provider.dart defines mockDmDirectoryEnabled as `kDebugMode && bool.fromEnvironment('BUZZ_MOCK_DM_DIRECTORY')`, gating whether the new-DM picker shows local preview identities; this is a feature flag, not a configuration setting, and is out of this node's scope."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channel_management_provider.dart"
  - statement: "mobile/android/app/build.gradle.kts reads four Android upload-signing values from the environment -- BUZZ_ANDROID_UPLOAD_KEYSTORE_PATH, BUZZ_ANDROID_UPLOAD_KEYSTORE_PASSWORD, BUZZ_ANDROID_UPLOAD_KEY_ALIAS, BUZZ_ANDROID_UPLOAD_KEY_PASSWORD -- via providers.environmentVariable(...).orNull, and its gradle.taskGraph.whenReady block throws a GradleException naming every missing one when an assembleRelease or bundleRelease task runs without upload-keystore signing configured."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "The same build.gradle.kts block requires BUZZ_ANDROID_UPLOAD_KEYSTORE_PATH to be an absolute path outside the repository (checked by comparing the keystore's canonicalFile against the repository root's canonicalFile) and to be a readable file, each on a separate check that throws GradleException with a specific message."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "BUZZ_ANDROID_RELEASE_SIGNING selects between two release-signing modes, defaulting to \"upload-keystore\" when unset; a value outside {\"upload-keystore\", \"external\"} throws GradleException, and \"external\" mode throws GradleException if any BUZZ_ANDROID_UPLOAD_* value is also set, deliberately producing an unsigned release bundle for the central APK Signer pipeline instead of local upload-keystore signing."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "mobile/README.md's \"Android release signing\" section documents the same four BUZZ_ANDROID_UPLOAD_* variables plus BUZZ_ANDROID_RELEASE_SIGNING=external, and states explicitly that development and debug builds do not require them."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "scripts/mobile-worktree-overrides.sh detects whether the repository root is a linked git worktree (comparing `git rev-parse --git-dir` against `--git-common-dir`); in a linked worktree it writes mobile/ios/Flutter/WorktreeOverrides.xcconfig (BUNDLE_IDENTIFIER, APP_DISPLAY_NAME) and mobile/android/worktree.properties (label, applicationIdSuffix), both derived from the worktree directory name plus the current branch name or short SHA; in the main checkout it deletes both files instead of writing them."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
  - statement: "mobile/ios/Flutter/Debug.xcconfig and Release.xcconfig each set default BUNDLE_IDENTIFIER = com.buzz.buzzMobile and APP_DISPLAY_NAME = Buzz; only Debug.xcconfig includes WorktreeOverrides.xcconfig, and both files include an optional AppOverrides.xcconfig last, so a developer's own gitignored AppOverrides.xcconfig value wins per variable over both the tracked default and the generated worktree override, while Release builds never see a worktree override at all."
    entry_class: FACT
    evidence:
      - "mobile/ios/Flutter/Debug.xcconfig"
      - "mobile/ios/Flutter/Release.xcconfig"
  - statement: "mobile/android/app/build.gradle.kts sets defaultConfig.applicationId and android.namespace to xyz.block.buzz.mobile. Only the debug build type reads mobile/android/worktree.properties: it applies applicationIdSuffix (validated against the regex \\.[a-z][a-z0-9_]*, else GradleException) and overrides the app_name string resource with label (validated against [A-Za-z0-9._-]+, else GradleException) when the file is present. Release and profile build types never read this file."
    entry_class: FACT
    evidence:
      - "mobile/android/app/build.gradle.kts"
  - statement: "mobile/ios/.gitignore excludes Flutter/AppOverrides.xcconfig and Flutter/WorktreeOverrides.xcconfig, and mobile/android/.gitignore excludes /worktree.properties, so none of the three override files are ever committed. mobile/.gitignore excludes .env.json while mobile/.env.json.example (placeholder-only) is committed, mirroring the repository root's own .env / .env.example split."
    entry_class: FACT
    evidence:
      - "mobile/ios/.gitignore"
      - "mobile/android/.gitignore"
      - "mobile/.gitignore"
  - statement: "relay_provider.dart's own doc comment labels Env as \"Compile-time environment config via --dart-define\", and String.fromEnvironment is evaluated by the Dart compiler at build time rather than read from the process environment at run time, so changing BUZZ_RELAY_URL (or the documented-but-unread BUZZ_DEV_PUBKEY) requires a rebuild, not merely a restart. The Android and iOS build-time settings (release signing, worktree/bundle identity) are likewise read only at Gradle/Xcode build time and are never read by the installed app's own Dart or platform code while running."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
      - "mobile/android/app/build.gradle.kts"
      - "mobile/ios/Flutter/Debug.xcconfig"
  - statement: "The Twelve-Factor App's Config factor names 'developer environments' as one of its own examples of what a deploy varies across (\"everything that is likely to vary between deploys (staging, production, developer environments, etc.)\"), so a value that varies per developer's git worktree sits within that factor's own stated scope rather than being an extension of it."
    entry_class: FACT
    evidence:
      - "https://12factor.net/config"
  - statement: "launchpad/docs/corpus/architecture/containers/mobile.md (id architecture-containers-mobile) already documents RelayConfig deriving both the WebSocket and HTTP base URL from the active Community's relayUrl, falling back to Env.relayUrl only when no community is active, and documents the worktree-scoped debug identity mechanism at container-overview depth; this node specializes that overview into a settings-table-shaped configuration reference and does not restate its prose."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "At repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists architecture-containers-mobile (architecture/containers/mobile.md) and corpus-template-configuration (templates/configuration.md) among merged nodes, and lists no node under layers/configuration/ -- confirming both relationship targets exist on the merge-target branch and confirming the sibling configuration nodes for #1051-#1055 and #1057-#1059 are not yet merged."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus', commit='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> includes architecture/containers/mobile.md and templates/configuration.md, no layers/configuration/* entries"
  - statement: "The mobile app persists per-community relay identity (Community.relayUrl, pubkey, nsec) in FlutterSecureStorage via CommunityStorage, switched at runtime through communityListProvider/activeCommunityProvider with no rebuild or restart required; this is user-seeded runtime state acquired through pairing or invite flows, not deploy-time configuration, and is out of this node's scope."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart"
      - "mobile/lib/shared/community/community_provider.dart"
  - statement: "Issue #1056's Definition of Done requires this node to satisfy templates/configuration.md's type-specific bullets: defining type/shape, source, default/required behavior and validation for each setting; stating whether each is sensitive/secret, environment-specific, restart-required or dynamically reloadable; defining effects/failure behavior and compatibility/deprecation; and linking implementation/deployment examples without embedding real secrets."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1056 definition of done"
  - statement: "Issue #1056 requires this node to scope explicitly to mobile-app-level configuration, alongside sibling configuration nodes for #1051 (agent configuration), #1052 (defaults), #1053 (desktop configuration), #1054 (environment configuration), #1055 (feature flags), #1057 (relay configuration), #1058 (secrets) and #1059 (validation)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1056 issue body"
relationships:
  - type: references
    target: architecture-containers-mobile
  - type: implements
    target: corpus-template-configuration
---

# Mobile app: configuration

This node catalogues the deploy-time configuration surface of the Flutter mobile
client (`mobile/`): the compile-time relay endpoint it embeds via `--dart-define`,
the environment variables Android release builds require for upload-key signing,
and the worktree-scoped build identity overrides that let multiple in-progress
branches install side by side during local development. It applies to the
`mobile/` source tree as built by `flutter build` / `flutter run` and by the
platform build tools (Gradle, Xcode) that wrap it -- not to the private Buzz
mobile Buildkite pipeline that signs and ships release artifacts from an
immutable git tag, which this repository does not contain.

## Settings

| Variable | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `BUZZ_RELAY_URL` | dart-define string (URL) | `http://localhost:3000` | No | No | Compile-time relay origin. `RelayConfigNotifier` uses it only as a fallback when no `Community` is stored (fresh install / no community added yet); once a community exists, its `relayUrl` always wins. |
| `BUZZ_DEV_PUBKEY` | dart-define string (hex pubkey) | none | No | No | Documented in `.env.json.example` for local dev convenience. Not read by any `fromEnvironment` call site under `mobile/lib` at this revision -- currently inert. |
| `BUZZ_ANDROID_UPLOAD_KEYSTORE_PATH` | env var, absolute filesystem path | none -- required for `assembleRelease`/`bundleRelease` unless `BUZZ_ANDROID_RELEASE_SIGNING=external` | Yes (release, upload-keystore mode) | No (locator, not a credential value) | Path to the CI-vended upload keystore, read by Gradle at build time. Must be absolute and outside the repository; the build fails loudly (`GradleException`) if it is relative, inside the repo, missing, or unreadable. |
| `BUZZ_ANDROID_UPLOAD_KEYSTORE_PASSWORD` | env var, string | none -- required alongside the path | Yes (release, upload-keystore mode) | Yes | Keystore password passed to the Gradle `signingConfig`. Never logged; Gradle fails the release task graph if unset. |
| `BUZZ_ANDROID_UPLOAD_KEY_ALIAS` | env var, string | none -- required alongside the path | Yes (release, upload-keystore mode) | No | Key alias within the keystore. An identifier, not a credential value by itself. |
| `BUZZ_ANDROID_UPLOAD_KEY_PASSWORD` | env var, string | none -- required alongside the path | Yes (release, upload-keystore mode) | Yes | Per-key password passed to the Gradle `signingConfig`. |
| `BUZZ_ANDROID_RELEASE_SIGNING` | env var, enum `{upload-keystore, external}` | `upload-keystore` | No | No | Selects the release-signing mode. `external` produces a deliberately *unsigned* bundle for the central APK Signer pipeline and fails the build if any `BUZZ_ANDROID_UPLOAD_*` value is also set. Any other value fails the build. |
| iOS `BUNDLE_IDENTIFIER` | xcconfig build setting | `com.buzz.buzzMobile` | No | No | Set identically in `Debug.xcconfig`/`Release.xcconfig`. A developer's gitignored `AppOverrides.xcconfig` overrides it per variable, on both Debug and Release; a generated `WorktreeOverrides.xcconfig` additionally overrides it on Debug only, unless `AppOverrides.xcconfig` also sets it (later include wins). |
| iOS `APP_DISPLAY_NAME` | xcconfig build setting | `Buzz` | No | No | Same override chain as `BUNDLE_IDENTIFIER` above. |
| Android `applicationId` / `namespace` | Gradle `defaultConfig` string | `xyz.block.buzz.mobile` | No | No | Base Android application id, set once in `build.gradle.kts`. Not itself overridden by worktree state -- see `applicationIdSuffix` below. |
| Android `applicationIdSuffix` (worktree) | `worktree.properties` value, must match `\.[a-z][a-z0-9_]*` | none (unset outside a linked worktree) | No | No | Read only by the `debug` build type from `mobile/android/worktree.properties`; appended to the base `applicationId` so multiple worktrees install side by side. Invalid values fail the build (`GradleException`). Release/profile builds never read it. |
| Android `app_name` label (worktree) | `worktree.properties` value, must match `[A-Za-z0-9._-]+` | `Buzz` (unset outside a linked worktree) | No | No | Read only by the `debug` build type; overrides the `app_name` string resource to `Buzz ($label)`. Invalid values fail the build (`GradleException`). Release/profile builds always keep the plain `Buzz` label. |

Every dart-define row above is baked into the compiled binary at build time --
`String.fromEnvironment`/`bool.fromEnvironment` are Dart compile-time constants, not
process-environment reads, so changing one requires a rebuild, never just a restart.
The Android and iOS rows are read only by their respective build tools (Gradle,
Xcode) at build/link time and are never read by the installed app's own Dart or
platform code while running -- there is no "reload" concept for any row in this
table. No row above is deprecated at this revision.

## Litmus test

Every row above varies between deploys per the Twelve-Factor litmus test --
"whether the codebase could be made open source at any moment, without
compromising any credentials." The four `BUZZ_ANDROID_UPLOAD_*` values and
`BUZZ_ANDROID_RELEASE_SIGNING` vary between the two signing pipelines this
repository supports (local upload-keystore vs. the central APK Signer service) and
between CI and a developer's machine. `BUZZ_RELAY_URL` varies between an
unconfigured fresh install and a deployed relay. The bundle-identifier, display-name
and worktree-identity rows vary per developer git worktree -- explicitly one of
Twelve-Factor's own named deploy types ("developer environments"), not an
extension of the test. `BUZZ_DEV_PUBKEY` is included even though currently unread
because it is a documented, deploy-varying value a future change could wire up; it
is flagged inert above rather than silently included as if live.

**Considered and excluded.** Per-community relay identity (`Community.relayUrl`,
`pubkey`, `nsec`, persisted via `CommunityStorage`/`FlutterSecureStorage`) fails
this node's scope test in the other direction: it genuinely varies, but it is
user-seeded runtime state acquired through pairing or an invite link and switched
without any rebuild, not a value the deploy pipeline supplies -- see *Boundary*
below. `BUZZ_MOCK_DM_DIRECTORY` is a debug-only feature flag, not a configuration
setting, and is excluded for the same reason.

## Secrets discipline

No row above quotes a live credential, key, token, or hostname value.
`BUZZ_ANDROID_UPLOAD_KEYSTORE_PASSWORD` and `BUZZ_ANDROID_UPLOAD_KEY_PASSWORD` are
marked `Secret: yes` because they are credential-shaped values by kind, per
`build.gradle.kts`'s own use of them as a Gradle `signingConfig`'s
`storePassword`/`keyPassword`; this node cites only the environment variable name
and the code path that reads it, never a value. `BUZZ_ANDROID_UPLOAD_KEYSTORE_PATH`
and `BUZZ_ANDROID_UPLOAD_KEY_ALIAS` are marked `Secret: no`: the path is a
filesystem locator (the build enforces it lives outside the repository precisely
so the keystore file itself is never committed, which is a different control than
treating the path string as a secret), and the alias is an identifier within the
keystore, not a credential value on its own.

## Boundary

This node does not describe:
- Per-community relay identity (`relayUrl`, `pubkey`, `nsec`) stored via
  `CommunityStorage` -- that is user-seeded runtime state switched at runtime with
  no rebuild, documented at container-overview depth in
  `architecture-containers-mobile`, not deploy-time configuration.
- The `BUZZ_MOCK_DM_DIRECTORY` feature flag (`channel_management_provider.dart`) --
  a feature flag, owned by the feature-flags configuration node (#1055), not this
  one.
- The parsing/validation logic itself (`Env`, the `build.gradle.kts` checks) beyond
  what is needed to state each setting's type, default and failure behavior --
  an `implementation` node describing that logic in depth, if written, would
  `references` this node rather than duplicate it.
- The private Buzz mobile Buildkite pipeline that actually signs and ships release
  artifacts from an immutable `mobile-vX.Y.Z-rc.N` tag (see `RELEASING.md` and this
  repository's `AGENTS.md`/`CLAUDE.md` ecosystem table) -- that pipeline lives in
  the separate `buzz-releases` repository, outside this repository's OSS source
  tree, and is not inventoried here.
- The `buzz://` deep-link URL scheme registration (`CFBundleURLSchemes` in
  `Info.plist`, the intent filter in `AndroidManifest.xml`) -- a wire/interface
  contract, not a deploy-varying setting; a possible future interface-layer node,
  not folded in here.
- Desktop's own configuration surface (issue #1053) or any other sibling
  configuration node listed in *Scope and omissions* below.

## Relationships

- `references: architecture-containers-mobile` -- the merged container-overview
  node this document specializes; it already describes `RelayConfig`/`Env.relayUrl`
  and the worktree-identity mechanism in prose, and this node adds the
  settings-table-shaped reference view without restating that prose.
- `implements: corpus-template-configuration` -- this node is an instance of the
  configuration template.

No `depends-on` or `part-of` edge is declared: no merged node on `origin/launchpad`
represents a broader capability or deployment surface this configuration is a
subsection of. Sibling configuration nodes for #1051-#1055 and #1057-#1059 are
open, unmerged draft PRs at this revision (verified by `git ls-tree` against
`origin/launchpad`, see evidence ledger) and are therefore not valid relationship
targets regardless of subject-matter adjacency.

## Scope and omissions

**This node covers** the mobile app's compile-time relay-endpoint default
(`BUZZ_RELAY_URL`, and the documented-but-unused `BUZZ_DEV_PUBKEY`), the Android
release upload-signing environment variables and their validation/failure
behavior, and the worktree-scoped iOS/Android build-identity override mechanism
(default, developer override, and generated worktree override), each classified
against the Twelve-Factor litmus test and marked for secrets discipline.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-community relay identity as runtime/user state | `architecture-containers-mobile` (container-overview depth only; no dedicated runtime-state node found at this revision) |
| The `BUZZ_MOCK_DM_DIRECTORY` feature flag | #1055 (feature flags), open and unmerged at time of writing |
| Desktop app configuration | #1053 (desktop configuration), open and unmerged at time of writing |
| Relay-side configuration | #1057 (relay configuration), open and unmerged at time of writing |
| Cross-cutting environment/secrets/validation standards | #1054, #1058, #1059, all open and unmerged at time of writing |
| The private `buzz-releases` mobile signing/build pipeline | Outside this repository's OSS source tree; see `RELEASING.md` |
| The `buzz://` deep-link scheme as a wire contract | A possible future interface-layer node; not filed as an issue by this task |
| The generic reference and configuration templates themselves | `launchpad/docs/corpus/templates/reference.md`, `templates/configuration.md` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**No `depends-on`/`part-of` relationships declared.** See *Relationships* above for
what was checked and why none of the merged nodes on `origin/launchpad` fit either
type.

**Expected but not verified when this node was written:**

- **Whether the private Buzz mobile Buildkite pipeline reads any additional
  environment variables beyond what `mobile/android/app/build.gradle.kts` and this
  repository's own scripts expose was not checked** -- that pipeline's
  configuration lives in the separate `buzz-releases` repository, which this task
  did not open.
- **iOS release signing's own environment-variable surface (an Apple-side
  equivalent to `BUZZ_ANDROID_UPLOAD_*`, if any) was not found in this repository**
  at this revision -- `mobile/ios/Flutter/Release.xcconfig` sets
  `CODE_SIGN_STYLE = Automatic` and `CODE_SIGN_IDENTITY = iPhone Developer` with no
  environment-variable-driven signing path comparable to Android's, but whether the
  private pipeline supplies iOS signing through a mechanism entirely outside this
  tree was not verified.
- **Whether any other `mobile/lib` source reads `dotenv`-style file configuration
  at runtime (rather than compile-time `fromEnvironment`) was not separately
  audited beyond the `.env.json`/`--dart-define-from-file` mechanism already
  documented** -- no `flutter_dotenv` or similar runtime-`.env`-reading dependency
  was found in `mobile/pubspec.yaml`, but that pubspec was read for this claim, not
  exhaustively diffed against every transitive dependency's own behavior.
