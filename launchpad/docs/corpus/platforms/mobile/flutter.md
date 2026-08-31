---
id: platforms-mobile-flutter
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
  - statement: "The mobile app declares hooks_riverpod and flutter_hooks as direct dependencies in pubspec.yaml, and at the recorded revision zero files under mobile/lib extend StatefulWidget, while 63 extend HookConsumerWidget and 31 extend ConsumerWidget."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
      - "grep_repo(pattern='extends StatefulWidget', scope='mobile/lib/**') -> 0 matches; grep_repo(pattern='extends HookConsumerWidget', scope='mobile/lib/**') -> 63 matches; grep_repo(pattern='extends ConsumerWidget', scope='mobile/lib/**') -> 31 matches, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "mobile/lib/app.dart's top-level App widget extends HookConsumerWidget, reads Riverpod providers with ref.watch/ref.read/ref.listen, and calls the flutter_hooks useEffect hook to run a one-time badge-sync effect on first build."
    entry_class: FACT
    evidence:
      - "mobile/lib/app.dart"
  - statement: "The app's providers are built from Riverpod's Provider, FutureProvider and NotifierProvider families -- including .family and .autoDispose variants -- rather than the legacy StateNotifierProvider; a repository-wide count at the recorded revision found 12 FutureProvider.autoDispose, 9 FutureProvider.family, 5 NotifierProvider.family, 4 Provider.autoDispose, 2 Provider.family and 2 NotifierProvider.autoDispose declarations under mobile/lib, plus concrete examples in mobile/lib/shared/theme/theme_provider.dart (NotifierProvider<ThemeNotifier, ThemeMode>) and mobile/lib/app.dart (FutureProvider.family)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/theme_provider.dart"
      - "mobile/lib/app.dart"
      - "grep_repo(pattern='(Provider|FutureProvider|NotifierProvider)\\.(family|autoDispose)', scope='mobile/lib/**') -> counts above, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Feature code lives under mobile/lib/features/ as one directory per surface (activity, channels, forum, home, invites, pairing, profile, pulse, search, settings), and cross-cutting code lives under mobile/lib/shared/ (auth, community, crypto, custom_emoji, deeplink, emoji, huddle, mentions, profile, push, read_state, relay, reminders, security, theme, utils, widgets)."
    entry_class: FACT
    evidence:
      - "list_dir(path='mobile/lib/features') -> activity, channels, forum, home, invites, pairing, profile, pulse, search, settings; list_dir(path='mobile/lib/shared') -> auth, community, crypto, custom_emoji, deeplink, emoji, huddle, mentions, profile, push, read_state, relay, reminders, security, theme, utils, widgets, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
      - "mobile/lib/features/home/home_page.dart"
      - "mobile/lib/shared/theme/theme.dart"
  - statement: "mobile/README.md's Architecture section states the feature-isolation rule as 'No cross-feature imports except shared/', matching the same rule stated in this repository's root CLAUDE.md; at the recorded revision this boundary is not encoded in mobile/analysis_options.yaml (flutter_lints plus the custom_lint/riverpod_lint plugin, neither of which includes an import-boundary rule), so the boundary is enforced by convention and code review, not by a build-time or lint-time gate."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
      - "mobile/analysis_options.yaml"
  - statement: "A large widget is split by factoring private sub-widgets into Dart `part` files under a same-named subdirectory rather than growing a single file; for example mobile/lib/features/profile/profile_avatar_editor.dart declares `part 'profile_avatar_editor/emoji_avatar_picker.dart';` with the part file living in the sibling profile_avatar_editor/ directory."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/profile/profile_avatar_editor.dart"
  - statement: "mobile/scripts/check-file-sizes.mjs runs runFileSizeCheck against every .dart file under mobile/lib with a 1000-line ceiling, matching the 1000-line/file rule stated in this repository's root CLAUDE.md for Desktop, Web and Mobile alike; it is invoked by `just mobile-check`."
    entry_class: FACT
    evidence:
      - "mobile/scripts/check-file-sizes.mjs"
  - statement: "mobile/lib/shared/theme/color_scheme.dart defines lightColorScheme and darkColorScheme as hardcoded Material ColorScheme constants labeled 'Catppuccin Latte (mauve accent)' and 'Catppuccin Macchiato (mauve accent)' respectively, each annotated as matching the corresponding Buzz desktop theme, and mobile/lib/shared/theme/app_theme.dart's AppTheme.light()/AppTheme.dark() build the app's ThemeData from these schemes by default."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/color_scheme.dart"
      - "mobile/lib/shared/theme/app_theme.dart"
  - statement: "Beyond the static Catppuccin default, mobile/lib/shared/theme/adaptive_theme.dart implements an 'Adaptive Theme Engine' that derives a Material 3 ColorScheme from any cataloged syntax theme's key colors (background, foreground, comment, git added/deleted), detecting light vs. dark from background luminance; its own header comment states it is 'Ported from desktop/src/shared/theme/adaptive-theme.ts'. mobile/lib/shared/theme/theme_catalog.dart catalogs 60 such syntax themes (ThemeColors entries), including catppuccin-latte, catppuccin-frappe, catppuccin-macchiato and catppuccin-mocha among many non-Catppuccin themes; mobile/lib/app.dart's App widget calls resolveSchemes(schemeName, themeMode) to turn the community's selected scheme name into the light/dark ColorScheme pair actually rendered."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/adaptive_theme.dart"
      - "mobile/lib/shared/theme/theme_catalog.dart"
      - "mobile/lib/app.dart"
  - statement: "mobile/lib/shared/theme/theme_provider.dart names Buzz's own first-party scheme (buzzThemeName) as the default for a fresh install ('Buzz ships as the default: the first-party pair, so a fresh install gets the branded top-section gradient without picking a theme first'), and persists the user's appearance-mode (ThemeNotifier) and accent-color (AccentNotifier) choices to SharedPreferences, which mobile/lib/main.dart pre-loads before runApp and injects via savedPrefsProvider.overrideWithValue(prefs)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/theme_provider.dart"
      - "mobile/lib/main.dart"
  - statement: "mobile/lib/shared/theme/grid.dart defines a Grid class of named spacing constants (quarter=2 through xxxl=80) and mobile/lib/shared/theme/app_theme.dart defines a Radii class of named corner-radius constants, whose doc comment states they match 'desktop shadcn \"New York\" style' radii (desktop's --radius: 0.625rem/10px base)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/grid.dart"
      - "mobile/lib/shared/theme/app_theme.dart"
  - statement: "Widget tests use a shared WidgetHelpers.testable() helper (mobile/test/helpers/widget_helpers.dart) that wraps a widget in a ProviderScope with caller-supplied overrides and a MaterialApp using AppTheme.light(); at least one test, mobile/test/features/pairing/pairing_provider_test.dart, defines a fake notifier (FakeAuthNotifier extends AsyncNotifier<AuthState> implements AuthNotifier) following the pattern of extending the real Riverpod notifier base class and overriding its build method, matching the convention this repository's root CLAUDE.md states for mobile tests."
    entry_class: FACT
    evidence:
      - "mobile/test/helpers/widget_helpers.dart"
      - "mobile/test/features/pairing/pairing_provider_test.dart"
  - statement: "mobile/README.md's Checks section names dart format --output=none --set-exit-if-changed ., flutter analyze and flutter test as this container's quality gates, runnable from the repository root as just mobile-fmt / just mobile-check / just mobile-test."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "launchpad/docs/corpus/architecture/containers/mobile.md (id: architecture-containers-mobile) already documents the mobile container's responsibility, technology summary, ownership boundary, inbound/outbound interfaces, deployment and security implications at the container level, including the same Riverpod+hooks, feature/shared-boundary and Catppuccin-theme facts summarized there in one paragraph each; this node exists to go one level deeper into those same three subjects without restating the container node's other sections (deployment, security, connected systems)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "The corpus schema's type enum has no member specific to a client platform/framework, and this node is placed under launchpad/docs/corpus/platforms/mobile/ per the issue that created it; sibling document tasks under platforms/** have used type: platforms for this reason, which this node follows for consistency even though no platforms-specific template exists yet to make that choice canonical."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-containers-mobile
---

# Flutter mobile client architecture

This node documents how the Buzz mobile app (`mobile/`) is built as a Flutter
application: its state-management pattern, its `lib/features/` vs.
`lib/shared/` module boundary, its large-widget-splitting convention, and its
theme system. It is the platform/framework-internals companion to
`architecture-containers-mobile`, which already covers the mobile container's
responsibility, interfaces and deployment at the container level -- this node
goes one level deeper into the three subjects both documents touch, without
restating that node's other sections.

## Responsibility

This node's subject is *how the mobile client is put together as Flutter code*
-- the conventions a developer or agent must follow to add or modify a screen,
a piece of state, or a themed surface without breaking the app's own internal
consistency. It does not restate what the mobile app does for a user (that is
`architecture-containers-mobile`'s "Responsibility" section) or how it talks to
the relay (that node's "Inbound/outbound interfaces" sections).

## State management

- **Pattern:** [Riverpod](https://riverpod.dev) (`hooks_riverpod`) combined
  with [`flutter_hooks`](https://pub.dev/packages/flutter_hooks) for local
  widget state. Widgets extend `HookConsumerWidget` (or plain `ConsumerWidget`
  when no hook is needed) and read/write state through a `WidgetRef` --
  `ref.watch`, `ref.read`, `ref.listen`. `mobile/lib/app.dart`'s top-level
  `App` widget is a representative example: it extends `HookConsumerWidget`,
  watches several providers, and calls `useEffect` for a one-time
  badge-sync side effect.
- **No `StatefulWidget`.** At the recorded revision, zero files under
  `mobile/lib` extend `StatefulWidget`; 63 extend `HookConsumerWidget` and 31
  extend `ConsumerWidget`. This matches the rule stated in this repository's
  root `CLAUDE.md` ("NEVER use `StatefulWidget`").
- **Provider shapes in use:** `Provider`, `FutureProvider` and
  `NotifierProvider`, each with `.family` and `.autoDispose` variants used
  throughout the codebase (see evidence ledger for counts) -- not the legacy
  `StateNotifierProvider` API. `mobile/lib/shared/theme/theme_provider.dart`'s
  `ThemeNotifier` (`NotifierProvider<ThemeNotifier, ThemeMode>`) and
  `mobile/lib/app.dart`'s `_inviteRelayConnectedProvider`
  (`FutureProvider.family`) are concrete examples of each shape.

## Module boundary: `lib/features/` vs. `lib/shared/`

- **`lib/features/`** holds one directory per user-facing surface:
  `activity`, `channels`, `forum`, `home`, `invites`, `pairing`, `profile`,
  `pulse`, `search`, `settings`.
- **`lib/shared/`** holds cross-cutting code every feature may depend on:
  `auth`, `community`, `crypto`, `custom_emoji`, `deeplink`, `emoji`,
  `huddle`, `mentions`, `profile`, `push`, `read_state`, `relay`,
  `reminders`, `security`, `theme`, `utils`, `widgets`.
- **The rule, and its actual enforcement.** `mobile/README.md` and this
  repository's root `CLAUDE.md` both state the boundary as "no cross-feature
  imports except `shared/`". At the recorded revision this is **not** encoded
  in `mobile/analysis_options.yaml` -- the analyzer runs `flutter_lints` plus
  the `custom_lint`/`riverpod_lint` plugin (Riverpod-specific best-practice
  lints), and neither enforces an import-boundary rule. The boundary is held
  by convention and code review, not by a lint or build-time gate, mirroring
  the same characterization already given for it in
  `architecture-containers-mobile`.

## Splitting a large widget

Rather than letting one file grow indefinitely, a large widget factors its
private sub-widgets into Dart `part` files placed in a same-named sibling
directory. `mobile/lib/features/profile/profile_avatar_editor.dart` is a
concrete example: it declares `part
'profile_avatar_editor/emoji_avatar_picker.dart';`, with the part file living
in the sibling `profile_avatar_editor/` directory. This is one mechanism
behind the hard ceiling this repository's root `CLAUDE.md` states for
Desktop, Web and Mobile alike -- **1000 lines per file** -- which
`mobile/scripts/check-file-sizes.mjs` enforces for every `.dart` file under
`mobile/lib` and which `just mobile-check` runs as part of this container's
gate.

## Theme system

- **Default scheme.** `mobile/lib/shared/theme/color_scheme.dart` hardcodes
  `lightColorScheme` and `darkColorScheme` as Material `ColorScheme` constants
  explicitly labeled Catppuccin Latte (light) and Catppuccin Macchiato (dark),
  each commented as matching the corresponding Buzz desktop theme.
  `mobile/lib/shared/theme/app_theme.dart`'s `AppTheme.light()` /
  `AppTheme.dark()` build the app's `ThemeData` from these schemes by
  default.
- **Beyond the default: the adaptive theme engine.**
  `mobile/lib/shared/theme/adaptive_theme.dart` implements an "Adaptive Theme
  Engine" -- its own header comment says it is "Ported from
  `desktop/src/shared/theme/adaptive-theme.ts`" -- that derives a full
  Material 3 `ColorScheme` from any cataloged syntax theme's key colors
  (background, foreground, comment, and optional git added/deleted colors),
  detecting light vs. dark from background luminance.
  `mobile/lib/shared/theme/theme_catalog.dart` catalogs 60 such themes,
  including several more Catppuccin variants (`catppuccin-latte`,
  `catppuccin-frappe`, `catppuccin-macchiato`, `catppuccin-mocha`) alongside
  many non-Catppuccin ones. `mobile/lib/app.dart`'s `App` widget calls
  `resolveSchemes(schemeName, themeMode)` to turn the active community's
  selected scheme name into the light/dark pair actually rendered, and
  derives the branded top-section gradient from the same resolved theme
  rather than from the raw persisted selection.
- **Buzz's own first-party default and persistence.**
  `mobile/lib/shared/theme/theme_provider.dart` names Buzz's own scheme
  (`buzzThemeName`) as the default for a fresh install, and persists the
  user's appearance-mode (`ThemeNotifier`) and accent-color
  (`AccentNotifier`) choices to `SharedPreferences`. `mobile/lib/main.dart`
  pre-loads that `SharedPreferences` instance before `runApp` and injects it
  via `savedPrefsProvider.overrideWithValue(prefs)`, so the very first frame
  already reflects the saved theme and accent rather than flashing a default.
- **Spacing and radius tokens.** `mobile/lib/shared/theme/grid.dart` defines
  a `Grid` class of named spacing constants (`quarter` = 2px through
  `xxxl` = 80px). `mobile/lib/shared/theme/app_theme.dart` defines a `Radii`
  class of named corner-radius constants, whose own doc comment states they
  match "desktop shadcn \"New York\" style" radii.

## Testing convention

Widget tests share a `WidgetHelpers.testable()` helper
(`mobile/test/helpers/widget_helpers.dart`) that wraps the widget under test
in a `ProviderScope` (with caller-supplied overrides) inside a `MaterialApp`
using `AppTheme.light()`. Where a provider's real implementation is
impractical to exercise directly, tests define a fake notifier that extends
the real Riverpod notifier base class and overrides its `build()` method --
for example `FakeAuthNotifier extends AsyncNotifier<AuthState> implements
AuthNotifier` in `mobile/test/features/pairing/pairing_provider_test.dart`.

## Quality gates

`mobile/README.md`'s Checks section names `dart format --output=none
--set-exit-if-changed .`, `flutter analyze` and `flutter test` as this
container's gates, runnable from the repository root as `just mobile-fmt`
(auto-fix), `just mobile-check` (lint + format check, including the file-size
guard above) and `just mobile-test`.

## Dependencies and collaborators

- **Framework packages:** `hooks_riverpod` and `flutter_hooks` (state
  management, declared in `mobile/pubspec.yaml`), `shared_preferences`
  (theme/accent persistence).
- **Desktop, as a design source:** the adaptive theme engine
  (`adaptive_theme.dart`) is an explicit Dart port of
  `desktop/src/shared/theme/adaptive-theme.ts`, and the default `ColorScheme`
  and `Radii` values are deliberately kept in step with the desktop app's own
  Catppuccin theme and shadcn "New York" radius scale -- see
  `architecture-containers-mobile` for the wider claim that mobile and
  desktop are sibling clients against the same relay protocol.
- **The relay's event-kind registry**, and the rest of this container's
  network-facing collaborators, are documented in
  `architecture-containers-mobile`, not restated here.

## Boundary

This node does not describe:
- **Android/iOS platform-shell integration** -- worktree-scoped app
  identifiers, push-notification capability and signing, and other
  per-platform build concerns. These are the subject of sibling issues
  #1252 (Android) and #1255 (iOS), not this node.
- **Navigation/routing.** How the app moves between pages and dialogs is
  #1257's subject.
- **The mobile container's responsibility, wire protocol, deployment
  pipeline, or security posture at the container level.** Those are
  `architecture-containers-mobile`'s subject; this node references it rather
  than duplicating it.
- **Per-feature internal design** inside any one `lib/features/*` module --
  if a feature's internal design warrants its own corpus node, that is a
  separate task, not folded in here.
- **A full inventory of all 60 cataloged syntax themes** or of every
  provider/notifier in the codebase -- the counts and named examples above
  are representative evidence for the architectural pattern, not a complete
  catalog.

## Relationships

- `references`: `architecture-containers-mobile` -- this node's platform/
  framework-internals content sits alongside that node's container-level
  content; `references` is used (rather than `part-of` or `depends-on`)
  because this node's own claims do not depend on that node staying current,
  it only points a reader to related context, per `references`'s schema
  directionality ("source cites target as supporting context; no ownership
  or currency dependency implied").

## Scope and omissions

**This node covers** the Flutter mobile app's state-management pattern
(Riverpod + `flutter_hooks`, no `StatefulWidget`), its `lib/features/` vs.
`lib/shared/` module boundary and how that boundary is actually enforced
(convention/review, not lint), its large-widget part-file splitting
convention and the file-size gate behind it, its theme system (the
Catppuccin-based default plus the desktop-ported adaptive theme engine and
its 60-theme catalog), its shared widget-test helper and fake-notifier
convention, and its quality gates.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Android platform-shell integration | #1252 |
| iOS platform-shell integration | #1255 |
| Navigation/routing | #1257 |
| Mobile container responsibility, wire protocol, deployment, security | `architecture-containers-mobile` |
| Per-feature internal design (e.g. `lib/features/channels`) | Not yet filed as separate tasks at time of writing |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No `platforms/**` template exists yet.** `type: platforms` is used
  because sibling document tasks under this same directory have settled on
  it, not because a reviewed template makes that choice canonical --
  `AGENTS.md`'s own gap table lists per-type templates as unowned pending
  issues #1307-#1351. If a `platforms`-specific template lands later with a
  different required shape, this node may need reshaping to match it.
- **Whether every provider in the codebase follows the family/autoDispose
  conventions named above was not checked file-by-file** -- the counts cited
  are a repository-wide grep at the recorded revision, not a review of each
  matched declaration's correctness.
- **The mobile test suite's coverage of the conventions described here was
  not assessed.** This node describes what the code and its test *helpers*
  do, not how thoroughly each convention is exercised by the test suite.
