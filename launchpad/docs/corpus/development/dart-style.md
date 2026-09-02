---
id: development-dart-style
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "mobile/analysis_options.yaml is the only analysis_options.yaml in the repository, so it is the single analyzer configuration governing every Dart file here."
    entry_class: FACT
    evidence:
      - "mobile/analysis_options.yaml"
      - "find(name='analysis_options.yaml', root='.', exclude='node_modules') -> ./mobile/analysis_options.yaml (one result)"
  - statement: "mobile/analysis_options.yaml includes package:flutter_lints/flutter.yaml, registers custom_lint as an analyzer plugin, downgrades invalid_use_of_visible_for_overriding_member to ignore, excludes build/ and the six platform directories from analysis, and enables exactly one additional linter rule, prefer_single_quotes."
    entry_class: FACT
    evidence:
      - "mobile/analysis_options.yaml"
  - statement: "mobile/pubspec.yaml declares flutter_lints ^6.0.0, custom_lint ^0.8.0 and riverpod_lint ^3.1.0 as dev dependencies, hooks_riverpod ^3.0.3 and flutter_hooks ^0.21.3 as runtime dependencies, and an SDK constraint of ^3.11.4."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
  - statement: "mobile/pubspec.lock resolves flutter_lints to 6.0.0, custom_lint to 0.8.1 and riverpod_lint to 3.1.0, and records SDK constraints of dart >=3.11.4 <4.0.0 and flutter >=3.38.4."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.lock"
  - statement: "flutter_lints 6.0.0's flutter.yaml includes package:lints/recommended.yaml and adds exactly ten Flutter-specific rules: avoid_print, avoid_unnecessary_containers, avoid_web_libraries_in_flutter, no_logic_in_create_state, prefer_const_constructors_in_immutables, sized_box_for_whitespace, sort_child_properties_last, use_build_context_synchronously, use_full_hex_values_for_flutter_colors and use_key_in_widget_constructors."
    entry_class: FACT
    evidence:
      - "read('/home/serina/.pub-cache/hosted/pub.dev/flutter_lints-6.0.0/lib/flutter.yaml') -> 'include: package:lints/recommended.yaml' plus a linter.rules list of ten entries beginning avoid_print and ending use_key_in_widget_constructors"
  - statement: "lints 6.0.0's recommended.yaml includes package:lints/core.yaml and lists 56 further rules, and core.yaml lists 35, so the effective rule set for this app is 35 + 56 + 10 flutter_lints rules + the locally added prefer_single_quotes."
    entry_class: FACT
    evidence:
      - "read('/home/serina/.pub-cache/hosted/pub.dev/lints-6.0.0/lib/recommended.yaml') -> 'include: package:lints/core.yaml' and 56 rule entries; read('/home/serina/.pub-cache/hosted/pub.dev/lints-6.0.0/lib/core.yaml') -> 35 rule entries"
  - statement: "avoid_print is enabled by flutter_lints 6.0.0 and is not disabled anywhere in mobile/analysis_options.yaml, so the repository's no-print() rule is enforced by flutter analyze rather than only by review."
    entry_class: FACT
    evidence:
      - "mobile/analysis_options.yaml"
      - "read('/home/serina/.pub-cache/hosted/pub.dev/flutter_lints-6.0.0/lib/flutter.yaml') -> linter.rules includes avoid_print; mobile/analysis_options.yaml's analyzer.errors block names only invalid_use_of_visible_for_overriding_member"
  - statement: "The Flutter and Dart binaries are Hermit-pinned: bin/flutter and bin/dart are both symlinks to bin/.flutter-3.41.7.pkg."
    entry_class: FACT
    evidence:
      - "bin/flutter"
      - "bin/dart"
  - statement: "The Justfile defines mobile-fmt as `dart format .`, mobile-fix as `dart format . && flutter analyze`, mobile-check as `dart format --output=none --set-exit-if-changed . && flutter analyze`, and mobile-test as `flutter test`, each run from the mobile directory."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's aggregate `check` recipe includes mobile-check and file-size-check, and its aggregate `ci` recipe includes mobile-test."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "lefthook.yml runs just mobile-fmt on pre-commit with stage_fixed enabled and a mobile/** glob, and runs `just mobile-check && just mobile-test` on pre-push under a mobile/** glob scoped by `git diff --name-only origin/main...HEAD`, with a comment stating the two run serially so parallel hooks do not contend for shared Flutter state."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "The Mobile job in .github/workflows/ci.yml runs `dart format --output=none --set-exit-if-changed .`, then `flutter analyze`, then `flutter test`, then `just mobile-build-android`, and is gated on either a push event or the mobile paths filter reporting true."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "mobile/scripts/check-file-sizes.mjs applies a 1000-line ceiling to .dart files under mobile/lib and delegates to the shared runFileSizeCheck helper; the Justfile's file-size-check recipe invokes it alongside the desktop and web equivalents."
    entry_class: FACT
    evidence:
      - "mobile/scripts/check-file-sizes.mjs"
      - "Justfile"
  - statement: "scripts/check-file-sizes-core.mjs computes the allowed line count as the configured maximum unless the file already exceeded it at the merge base, in which case the base line count becomes the limit, and it inspects only files changed from that base rather than the whole tree."
    entry_class: FACT
    evidence:
      - "scripts/check-file-sizes-core.mjs"
  - statement: "The repository's AGENTS.md Mobile App section states the rules that no StatefulWidget be used in favour of HookConsumerWidget or ConsumerWidget, that print() not be used in favour of debugPrint() or structured logging, that context.colors and context.textTheme be preferred over raw Theme.of(context), that one public widget live per file with private sub-widgets pushed into sibling part files under a <page>/ folder, that feature modules import only from shared/, and that Grid tokens be used for spacing and Radii for border radius."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "mobile/lib/shared/theme/theme_extensions.dart defines AppThemeExtension on BuildContext, supplying the getters theme, colors (returning theme.colorScheme), textTheme (returning theme.textTheme) and appColors (returning the AppColors ThemeExtension, asserting it is present)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/theme_extensions.dart"
  - statement: "Grid is a class of static const double spacing constants declared in mobile/lib/shared/theme/grid.dart, and Radii is a class of static const double border-radius constants declared in mobile/lib/shared/theme/app_theme.dart whose doc comment ties its values to the desktop shadcn New York scale."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/grid.dart"
      - "mobile/lib/shared/theme/app_theme.dart"
  - statement: "The part-file convention is realised in source: mobile/lib/features/settings/settings_page.dart declares three part directives pointing into a sibling settings_page/ folder, and mobile/lib/features/settings/settings_page/community_section.dart opens with `part of '../settings_page.dart';` and declares the private widget _CommunitySection."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/settings/settings_page.dart"
      - "mobile/lib/features/settings/settings_page/community_section.dart"
  - statement: "At the recorded revision mobile/lib contains 376 Dart files, of which 98 carry a `part of` directive, and its longest file is mobile/lib/features/search/search_page.dart at 999 lines -- one line below the ceiling."
    entry_class: FACT
    evidence:
      - "find(root='mobile/lib', name='*.dart') -> 376 files"
      - "grep(pattern='^part of ', root='mobile/lib', files_with_matches=true) -> 98 files"
      - "wc_lines(root='mobile/lib', glob='*.dart', sort='desc') -> largest is 999 lines at mobile/lib/features/search/search_page.dart"
      - "mobile/lib/features/search/search_page.dart"
  - statement: "At the recorded revision mobile/lib declares no direct StatefulWidget subclass; the base-class census is 244 StatelessWidget, 70 HookConsumerWidget, 47 ConsumerWidget, 2 ConsumerStatefulWidget and 0 StatefulWidget, the two ConsumerStatefulWidget subclasses being DeepLinkDispatcher and AvatarImageContent."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/deep_link_dispatcher.dart"
      - "mobile/lib/shared/widgets/avatar_image.dart"
      - "grep_count(pattern='extends <Base>', root='mobile/lib', include='*.dart') -> StatelessWidget 244, HookConsumerWidget 70, ConsumerWidget 47, ConsumerStatefulWidget 2, StatefulWidget 0"
  - statement: "At the recorded revision mobile/lib contains no bare print( call and no import from one lib/features/<module>/ subtree into another."
    entry_class: FACT
    evidence:
      - "grep(pattern='bare print call, dot-prefixed calls such as debugPrint excluded', root='mobile/lib', regex=true) -> 0 matches"
      - "scan_feature_imports(root='mobile/lib/features', rule='import naming a features module other than the importing one') -> 0 matches"
  - statement: "mobile/README.md summarises the same conventions independently of AGENTS.md, naming Riverpod plus Hooks via HookConsumerWidget, Grid tokens for spacing, flutter_lints plus riverpod_lint via custom_lint for linting, and 'No cross-feature imports except shared/' for feature isolation."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
  - statement: "The StatefulWidget, theme-accessor, Grid/Radii, one-public-widget-per-file and feature-isolation rules are enforced by review rather than by the analyzer, because no rule in flutter_lints 6.0.0's ten Flutter rules or in analysis_options.yaml's own linter.rules block names any of them, and the only machine gate covering mobile/lib beyond the analyzer is the 1000-line file-size ratchet."
    entry_class: INFERENCE
    evidence:
      - "mobile/analysis_options.yaml"
      - "mobile/scripts/check-file-sizes.mjs"
      - "Justfile"
      - "read('/home/serina/.pub-cache/hosted/pub.dev/flutter_lints-6.0.0/lib/flutter.yaml') -> ten rules, none naming StatefulWidget, Theme.of, spacing tokens, per-file widget counts or import boundaries"
    confidence: 0.75
  - statement: "custom_lint's registration as an analyzer plugin is what makes riverpod_lint's diagnostics available, since riverpod_lint ships as a custom_lint plugin rather than as analyzer linter rules."
    entry_class: INFERENCE
    evidence:
      - "mobile/analysis_options.yaml"
      - "mobile/pubspec.yaml"
      - "mobile/README.md"
    confidence: 0.7
  - statement: "Issue #854 requires that the node be structured for lookup rather than narrative teaching, contain only facts supported by current source with generated versus authored values labelled, define its scope and omissions, and link authoritative source, schema and configuration."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#854 definition of done"
  - statement: "Issue #854 requires that any newly discovered second concept, contract or procedure be filed as a separate task rather than folded into this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#854 definition of done"
---

# Dart and Flutter style: reference

What the Buzz repository actually enforces about Dart and Flutter source style,
and by what mechanism. Every rule below is listed with the artefact that holds
it, so a reader can tell a lint failure from a review comment before they write
the code. Scope is `mobile/` — the Flutter app is the only Dart in this
repository, and `mobile/analysis_options.yaml` is the only analyzer
configuration in it.

Rules divide into two populations, and the division is the most useful thing on
this page:

- **Machine-enforced** — a failing command names the file. `dart format`,
  `flutter analyze` over `flutter_lints` 6.0.0 plus one locally added rule, and
  the differential file-size ratchet.
- **Review-enforced** — written down in `AGENTS.md` and `mobile/README.md`, held
  by reviewers. No lint rule in any configured layer names any of them.

Each claim below has a matching entry in this node's provenance ledger — the
`evidence` array in its front matter — naming the file that was opened for it.

## Toolchain and configuration

| Item | Value | Source |
|---|---|---|
| Analyzer config | `mobile/analysis_options.yaml` (repository-wide sole instance) | `mobile/analysis_options.yaml` |
| Base rule set | `include: package:flutter_lints/flutter.yaml` | `mobile/analysis_options.yaml` |
| Effective rule count | 35 (`lints/core.yaml`) + 56 (`lints/recommended.yaml`) + 10 (`flutter_lints/flutter.yaml`) + 1 local = 102 | the three upstream YAML files, read from the pub cache |
| Analyzer plugin | `custom_lint` | `mobile/analysis_options.yaml` |
| Locally added lint rule | `prefer_single_quotes: true` — the only entry under `linter.rules` | `mobile/analysis_options.yaml` |
| Locally downgraded diagnostic | `invalid_use_of_visible_for_overriding_member: ignore` | `mobile/analysis_options.yaml` |
| Excluded from analysis | `build/**`, `android/**`, `ios/**`, `web/**`, `windows/**`, `macos/**`, `linux/**` | `mobile/analysis_options.yaml` |
| `flutter_lints` | declared `^6.0.0`, resolved `6.0.0` | `mobile/pubspec.yaml`, `mobile/pubspec.lock` |
| `custom_lint` | declared `^0.8.0`, resolved `0.8.1` | `mobile/pubspec.yaml`, `mobile/pubspec.lock` |
| `riverpod_lint` | declared `^3.1.0`, resolved `3.1.0` | `mobile/pubspec.yaml`, `mobile/pubspec.lock` |
| Dart SDK constraint | declared `^3.11.4`; lock records `dart >=3.11.4 <4.0.0`, `flutter >=3.38.4` | `mobile/pubspec.yaml`, `mobile/pubspec.lock` |
| Pinned toolchain | `bin/flutter` and `bin/dart` both symlink `bin/.flutter-3.41.7.pkg` | `bin/flutter`, `bin/dart` |

`pubspec.yaml` is authored; `pubspec.lock` is **generated** by `flutter pub get`
and its resolved versions are outputs, not choices. `mobile/analysis_options.yaml`
is authored in full. The `Grid` and `Radii` constants below are authored source,
not generated.

## Machine-enforced rules

Each row fails a command. The command is the enforcement; the description is
what it means for source.

| Rule | Enforced by | Where it runs |
|---|---|---|
| Canonical `dart format` output — a file the formatter would rewrite fails | `dart format --output=none --set-exit-if-changed .` | `just mobile-check`, `just check`, CI Mobile job "Format check", lefthook pre-push `mobile-checks` |
| `flutter_lints` 6.0.0's rule set, minus `invalid_use_of_visible_for_overriding_member` | `flutter analyze` | `just mobile-check`, `just mobile-fix`, CI Mobile job "Analyze", lefthook pre-push `mobile-checks` |
| No `print()` — `avoid_print` comes from `flutter_lints` and is not disabled locally | `flutter analyze` | as above |
| `prefer_single_quotes` — single quotes for string literals | `flutter analyze` (rule added locally in `analysis_options.yaml`) | as above |
| `custom_lint` plugin diagnostics, the route by which `riverpod_lint` reaches the analyzer — registered, but whether `flutter analyze` alone surfaces them was **not verified**; see *Scope and omissions* | plugin registration in `analysis_options.yaml` | no recipe, hook or workflow here invokes `custom_lint` directly |
| Tests pass | `flutter test` | `just mobile-test`, `just ci`, CI Mobile job "Test", lefthook pre-push `mobile-checks` |
| 1000-line ceiling on `.dart` files under `mobile/lib` | `node mobile/scripts/check-file-sizes.mjs` | `just file-size-check`, `just check`, pre-push |
| Android debug APK builds | `just mobile-build-android` | CI Mobile job "Build Android debug APK" |

### What `flutter_lints` 6.0.0 contributes

`analysis_options.yaml` names one include, so the rule set arrives in three
layers: `package:lints/core.yaml` (35 rules) → `package:lints/recommended.yaml`
(56 further rules) → `package:flutter_lints/flutter.yaml` (10 further rules).
Only the last layer is Flutter-specific, and it is short enough to list in full:

| Rule | Bears on |
|---|---|
| `avoid_print` | the repository's no-`print()` rule — this is what enforces it |
| `avoid_unnecessary_containers` | widget tree shape |
| `avoid_web_libraries_in_flutter` | imports |
| `no_logic_in_create_state` | `State` construction |
| `prefer_const_constructors_in_immutables` | const correctness |
| `sized_box_for_whitespace` | spacing widgets |
| `sort_child_properties_last` | argument order |
| `use_build_context_synchronously` | `BuildContext` across `await` |
| `use_full_hex_values_for_flutter_colors` | colour literals |
| `use_key_in_widget_constructors` | widget constructors |

None of the ten names `StatefulWidget`, `Theme.of`, spacing tokens, per-file
widget counts or import boundaries — which is why those five rules sit in the
review-enforced table below and `print()` does not.

### The file-size ceiling is a ratchet, not a flat cap

`mobile/scripts/check-file-sizes.mjs` sets `MAX_LINES = 1000` for `.dart` files
rooted at `mobile/lib`, then hands the rule to `runFileSizeCheck` in
`scripts/check-file-sizes-core.mjs`. That helper does two things worth knowing
before reading a failure:

- It inspects **only files changed from the merge base**, not the whole tree, so
  an untouched over-long file never trips it.
- `allowedLineCount(baseLines, maxLines)` returns `maxLines` when the file was
  at or under the ceiling at the base, and returns `baseLines` when it was
  already over. An over-limit file is therefore frozen at its current size
  rather than rejected outright — it may shrink, never grow.

At the recorded revision the longest file under `mobile/lib` is
`mobile/lib/features/search/search_page.dart` at 999 lines, one below the
ceiling. `AGENTS.md` states the response to a trip is to split the file, never
to raise the limit or add an override.

## Review-enforced rules

These are written in `AGENTS.md` (§ Mobile App → Rules) and echoed in
`mobile/README.md`. No rule in any of the three lint layers names any of them,
and no script checks them.

`AGENTS.md` also states "Do NOT use `print()`" in the same list. That one is
**not** in this table: `avoid_print` makes it machine-enforced, so it appears
above instead. The rest of the list is genuinely held by reviewers.

| Rule | Stated in | Observed in `mobile/lib` at the recorded revision |
|---|---|---|
| Never `StatefulWidget`; use `HookConsumerWidget` or `ConsumerWidget` with `flutter_hooks` for local state | `AGENTS.md` | 0 direct `StatefulWidget` subclasses. Census: 244 `StatelessWidget`, 70 `HookConsumerWidget`, 47 `ConsumerWidget`, 2 `ConsumerStatefulWidget` |
| Prefer `context.colors` / `context.textTheme` over raw `Theme.of(context)` | `AGENTS.md` | Getters supplied by `AppThemeExtension` in `mobile/lib/shared/theme/theme_extensions.dart` |
| Use `Grid` tokens for spacing, `Radii` for border radius | `AGENTS.md`, `mobile/README.md` | `Grid` in `mobile/lib/shared/theme/grid.dart`; `Radii` in `mobile/lib/shared/theme/app_theme.dart` |
| One public widget per file; private sub-widgets into sibling `part` files under a `<page>/` folder | `AGENTS.md` | 98 of 376 Dart files carry a `part of` directive |
| Feature modules import only from `shared/`, never from another feature | `AGENTS.md`, `mobile/README.md` | 0 cross-feature imports |

### The `StatefulWidget` rule and its two exceptions

The census above counts zero classes extending `StatefulWidget` directly, and
two extending Riverpod's `ConsumerStatefulWidget`:
`DeepLinkDispatcher` in `mobile/lib/features/channels/deep_link_dispatcher.dart`
and `AvatarImageContent` in `mobile/lib/shared/widgets/avatar_image.dart`.
`AGENTS.md`'s wording bans `StatefulWidget` and names `HookConsumerWidget` and
`ConsumerWidget` as the replacements; it does not mention
`ConsumerStatefulWidget` in either direction. Whether those two are exceptions
to the rule or outside its literal wording is not settled by any source in this
repository — this node records both the rule and the two occurrences rather than
resolving it. Note also that `StatelessWidget`, at 244 subclasses the most
common base class in the app, is untouched by the rule.

### What `context.colors` actually returns

`AppThemeExtension` is a Dart `extension` on `BuildContext`, not a Flutter
`ThemeExtension`. Its four getters:

| Getter | Returns |
|---|---|
| `context.theme` | `Theme.of(this)` |
| `context.colors` | `theme.colorScheme` — a `ColorScheme` |
| `context.textTheme` | `theme.textTheme` |
| `context.appColors` | the `AppColors` `ThemeExtension`, with an `assert` that it is registered in `ThemeData.extensions` |

The distinction matters when reading the rule: `context.colors` is Material's
`ColorScheme`; the app's own palette beyond that lives behind `context.appColors`.

### The part-file shape, as source

`mobile/lib/features/settings/settings_page.dart` declares:

```dart
part 'settings_page/community_section.dart';
part 'settings_page/connection_section.dart';
part 'settings_page/notifications_section.dart';
```

and `mobile/lib/features/settings/settings_page/community_section.dart` opens
with `part of '../settings_page.dart';` followed by
`class _CommunitySection extends ConsumerWidget`. Folder name matches the page
file's stem; sub-widgets are private (`_`-prefixed).

## Commands

Run from the repository root unless noted. Each `mobile-*` recipe does
`cd mobile` itself and unsets `GIT_DIR`/`GIT_WORK_TREE` first, which is what
makes them safe inside a worktree.

| Command | Effect | Exit-on-violation |
|---|---|---|
| `just mobile-fmt` | `dart format .` — rewrites files | no (it fixes) |
| `just mobile-fix` | `dart format . && flutter analyze` | on analyze findings |
| `just mobile-check` | `dart format --output=none --set-exit-if-changed . && flutter analyze` | yes |
| `just mobile-test` | `flutter test` | yes |
| `just file-size-check` | the differential ratchet across desktop, web and mobile, plus its own policy tests | yes |
| `just check` | repository lint/format/policy, includes `mobile-check` and `file-size-check` | yes |
| `just ci` | `check` plus the test and build lanes, includes `mobile-test` | yes |
| `just mobile-install` | `flutter pub get` | n/a |

Activate Hermit first (`. ./bin/activate-hermit`) so the pinned
`bin/.flutter-3.41.7.pkg` toolchain wins over any system Flutter.

## Where each gate fires

| Stage | Lane | Trigger |
|---|---|---|
| pre-commit | `mobile-fmt`, with `stage_fixed: true` | glob `mobile/**` |
| pre-push | `mobile-checks` → `just mobile-check && just mobile-test` | glob `mobile/**`, scoped by `git diff --name-only origin/main...HEAD` |
| pre-push | `file-size-check` (repository-wide) | unconditional |
| CI | Mobile job: format check → analyze → test → build Android debug APK | push event, or the `mobile` paths filter reporting true |

`lefthook.yml` notes that analysis and tests run serially in the pre-push lane
so parallel hooks do not contend for shared Flutter state (`.dart_tool`, the
shader bundle).

## Boundary

This node does not describe:

- **Why** any of these rules exist, or how Riverpod, hooks and the theme system
  relate conceptually. That is explanation, not reference.
- **How to** set up the toolchain, run the simulator, or work through a
  formatting failure step by step — see `development-hermit` and
  `development-prerequisites`, and `mobile/README.md`.
- Style for any other language in this repository. Rust (`cargo fmt`, clippy),
  desktop and web TypeScript (Biome, `tsc --noEmit`) are separate subjects with
  separate gates, mentioned here only where the same `just` recipe happens to
  span them.
- Mobile **testing** conventions — widget tests over unit tests,
  `ProviderScope(overrides:)`, `WidgetHelpers.testable()`. `AGENTS.md` carries
  those under a separate heading; they are a testing subject, not a style one.
- The Swift package under `mobile/ios/BuzzPushKit`, which has its own CI job and
  no Dart style surface.

## Relationships

**Declared: none.** `development-hermit` and `development-prerequisites` both
exist on `origin/launchpad` at the recorded revision and would resolve, so the
absence is a choice rather than a constraint. Neither is a fit: this node's
facts are cited directly to `mobile/analysis_options.yaml`, `Justfile`,
`lefthook.yml` and `.github/workflows/ci.yml`, not drawn from either sibling, so
a `references` edge would assert a supporting-context dependency that does not
exist. See the *Boundary* section above for the prose pointer instead.

## Scope and omissions

**This node covers** the Dart and Flutter style rules this repository enforces
on `mobile/`, split by enforcement mechanism: the analyzer configuration and the
package versions behind it, the formatter and lint commands, the file-size
ratchet and its ratcheting behaviour, the review-held conventions with a census
of how far current source matches them, the command surface, and the
commit/push/CI stages at which each gate fires. Its front matter carries the
provenance ledger backing every claim above.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What each of the 91 `lints` core/recommended rules checks | `package:lints`, upstream |
| The diagnostics `riverpod_lint` 3.1.0 contributes | `riverpod_lint`, upstream |
| Rust, TypeScript and Swift style | their own gates; no corpus node at the recorded revision |
| Mobile testing conventions | `AGENTS.md` § Mobile App → Testing Conventions |
| Toolchain setup and prerequisites | `development-hermit`, `development-prerequisites` |
| Whether `ConsumerStatefulWidget` is an exception to the `StatefulWidget` rule | unresolved; no source in this repository states it either way |

**Expected but not verified when this node was written:**

- **The lint rule set was read from a machine-local pub cache, not from this
  repository.** `flutter_lints` 6.0.0 and `lints` 6.0.0 are not vendored here;
  their YAML was opened at
  `~/.pub-cache/hosted/pub.dev/flutter_lints-6.0.0/lib/flutter.yaml` and the two
  `lints-6.0.0` files beside it. Those paths are outside the repository, so the
  corpus validator cannot check them and their citations are tool results. The
  resolved version is pinned by `mobile/pubspec.lock`, so a reader can reproduce
  the read, but nothing in-repo corroborates the rule list.
- **The rule counts are line counts, not semantic ones.** 35 / 56 / 10 come from
  counting list entries in the three YAML files. A rule listed in both `core`
  and `recommended`, or a commented-out entry, would skew the total of 102.
- **No command was executed to confirm current gate status.** `flutter analyze`,
  `flutter test` and `dart format` were not run; this node describes what the
  gates are and where they fire, read from configuration, not what they report
  today.
- **`dart format`'s effective line length was not established.** No
  `--line-length` appears in any recipe or config, so the formatter's default
  applies, but `dart format --help` produced no output in this environment and
  the default was not confirmed from a source that was opened.
- **`custom_lint`'s reachability from `flutter analyze` was not tested.** The
  plugin is registered in `analysis_options.yaml` and `mobile/README.md`
  describes `riverpod_lint` as running "via `custom_lint`", but whether
  `flutter analyze` alone surfaces those diagnostics — as opposed to a separate
  `dart run custom_lint` invocation — was not verified, and no recipe, hook or
  workflow in this repository invokes `custom_lint` directly.
- **The census counts are `grep`-derived, not analyzer-derived.** They count
  `extends <Base>` occurrences and literal `print(` calls in `mobile/lib`; a
  construct spelled differently, or reached through a typedef or an
  intermediate base class, would not be counted.
