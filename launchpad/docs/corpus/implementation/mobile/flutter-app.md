---
id: implementation-mobile-flutter-app
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "CLAUDE.md's Mobile App (Flutter) section states the app must never use StatefulWidget, favoring Riverpod plus flutter_hooks (HookConsumerWidget/ConsumerWidget) for state instead."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/lib/app.dart's App widget, the app's root, extends HookConsumerWidget (hooks_riverpod) and reads Riverpod providers via ref.watch inside its build method; mobile/lib/main.dart's runBuzzApp wraps the app in a ProviderScope."
    entry_class: FACT
    evidence:
      - "mobile/lib/app.dart"
      - "mobile/lib/main.dart"
  - statement: "No file under mobile/lib declares a class extending StatefulWidget."
    entry_class: FACT
    evidence:
      - "grep(pattern='extends StatefulWidget', path='mobile/lib/**') -> zero matches, checked directly against mobile/lib/app.dart, main.dart and the full lib/ tree at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "CLAUDE.md's Mobile App section states feature code is isolated under lib/features/ and shared code under lib/shared/, and that feature modules must not import from other feature modules, only from shared/."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/lib contains exactly two top-level code directories, features/ and shared/, plus app.dart and main.dart at the root; features/ holds one subdirectory per surface (activity, channels, forum, home, invites, pairing, profile, pulse, search, settings) and shared/ holds cross-cutting modules (auth, community, crypto, custom_emoji, deeplink, emoji, huddle, mentions, profile, push, read_state, relay, reminders, security, theme, utils, widgets)."
    entry_class: FACT
    evidence:
      - "mobile/lib/app.dart"
      - "mobile/lib/features/home/home_page.dart"
      - "mobile/lib/shared/theme/theme.dart"
  - statement: "CLAUDE.md's Mobile App section states the theme matches desktop's Catppuccin Latte (light) / Macchiato (dark) and that context.colors / context.textTheme (via theme extensions) should be preferred over raw Theme.of(context) calls."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/lib/shared/theme/theme_extensions.dart defines an AppThemeExtension on BuildContext exposing context.theme, context.colors (ColorScheme), context.textTheme and context.appColors, reading from Theme.of(this)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/theme_extensions.dart"
  - statement: "mobile/lib/shared/theme/color_scheme.dart defines lightColorScheme and darkColorScheme as Catppuccin Latte and Catppuccin Macchiato (mauve accent) respectively, each color commented with its Catppuccin token name, matching Buzz desktop's light/dark themes by the file's own comments."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/color_scheme.dart"
  - statement: "Beyond the Catppuccin default pair, mobile/lib/shared/theme/theme_catalog.dart defines a themeCatalog of 60 Shiki-derived ThemeColors entries (bg/fg/comment plus optional added/deleted), consumed by an adaptive theme engine to derive a full Material ColorScheme per community-selected theme; CLAUDE.md's theme description names only the Catppuccin Latte/Macchiato pair and does not mention this per-community catalog."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/theme/theme_catalog.dart"
  - statement: "mobile/lib/app.dart's App widget reads the active community's theme selection via ref.watch(communityThemeProvider) and resolves it through resolveSchemes/applyAccent before passing the result to AppTheme.light/dark, confirming theme selection is per-community and not fixed to the Catppuccin pair alone."
    entry_class: FACT
    evidence:
      - "mobile/lib/app.dart"
  - statement: "CLAUDE.md's Mobile App section states a hard 1000-line-per-file ceiling enforced by mobile/scripts/check-file-sizes.mjs via just mobile-check (runs in just check + pre-push, mirroring desktop/web), and that the guard must never be bumped or overridden -- files must be split instead."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/scripts/check-file-sizes.mjs sets MAX_LINES = 1000 and applies it to every .dart file under lib/, delegating the walk/report logic to the shared scripts/check-file-sizes-core.mjs used identically by desktop and web."
    entry_class: FACT
    evidence:
      - "mobile/scripts/check-file-sizes.mjs"
  - statement: "In the repository root Justfile, mobile-check (line 750) runs only `dart format --output=none --set-exit-if-changed .` and `flutter analyze`; the file-size guard is invoked by a separate recipe, file-size-check (line 106), which runs `node mobile/scripts/check-file-sizes.mjs` (and the desktop/web equivalents) directly. The top-level check recipe (line 96) depends on mobile-check and file-size-check as two independent, sibling prerequisites, not one calling the other -- so CLAUDE.md's phrasing that the file-size ceiling is enforced 'via just mobile-check' names the wrong recipe for the direct invocation, even though both do run under just check."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "CLAUDE.md's Mobile App section states debug builds run from a git worktree get a worktree-scoped app identifier and display name via scripts/mobile-worktree-overrides.sh, applied through just mobile-dev, so multiple worktrees can install side by side, and that release/profile builds are unaffected."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "scripts/mobile-worktree-overrides.sh detects whether it is running inside a linked git worktree (comparing --git-dir against --git-common-dir); when it is, it derives an iOS bundle-id slug and Android application-id suffix from the worktree directory name and a display label from the branch name (or short SHA if detached), then writes gitignored mobile/ios/Flutter/WorktreeOverrides.xcconfig (Debug builds only) and mobile/android/worktree.properties (debug build type only); in the main checkout it removes any stale override files instead."
    entry_class: FACT
    evidence:
      - "scripts/mobile-worktree-overrides.sh"
  - statement: "The Justfile's mobile-dev recipe (line 768) and mobile-build-android recipe (line 763) both invoke ./scripts/mobile-worktree-overrides.sh before running flutter, consistent with CLAUDE.md's claim that just mobile-dev applies the override."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "CLAUDE.md's Mobile App section states mobile's Nostr models (lib/shared/relay/nostr_models.dart) must stay in sync with desktop/src/shared/constants/kinds.ts so event kinds don't drift between clients."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/lib/shared/relay/nostr_models.dart line 7 carries the doc comment 'Keep in sync with `desktop/src/shared/constants/kinds.ts`.' directly above the abstract final class EventKind, which declares the app's Nostr event-kind integer constants."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
  - statement: "CLAUDE.md's Testing Conventions for mobile state preferring widget tests over unit tests, using ProviderScope(overrides: [...]) to inject fake notifiers that extend the real notifier class and override build(), and using a WidgetHelpers.testable() wrapper or a custom ProviderScope for widget tests."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile/test/helpers/widget_helpers.dart defines WidgetHelpers.testable({required child, overrides}) which wraps its child in a ProviderScope(overrides: overrides) inside a MaterialApp/Scaffold using AppTheme.light(); multiple test files under mobile/test/features/ (for example forum_widgets_test.dart, compose_drafts_provider_test.dart, presence_cache_provider_test.dart) define fake notifier classes extending a real notifier and overriding build(), matching CLAUDE.md's stated convention."
    entry_class: FACT
    evidence:
      - "mobile/test/helpers/widget_helpers.dart"
      - "mobile/test/features/forum/forum_widgets_test.dart"
      - "mobile/test/features/activity/compose_drafts_provider_test.dart"
  - statement: "mobile/test/shared/theme/ contains real automated test coverage for the theming layer described in this node: community_theme_preference_test.dart, community_theme_sync_test.dart, community_theme_provider_test.dart, theme_pairs_test.dart, buzz_theme_test.dart, utility_surface_theme_test.dart and app_theme_test.dart all exist as files in that directory."
    entry_class: FACT
    evidence:
      - "mobile/test/shared/theme/community_theme_preference_test.dart"
      - "mobile/test/shared/theme/community_theme_provider_test.dart"
      - "mobile/test/shared/theme/app_theme_test.dart"
  - statement: "The corpus node architecture-containers-mobile (launchpad/docs/corpus/architecture/containers/mobile.md) already documents the mobile container's responsibility, technology summary, ownership boundary, inbound/outbound interfaces and deployment/security implications at container grain, including the same Riverpod/flutter_hooks, shared/ layer, secure-storage and worktree-identity facts this node also verifies at implementation grain; this node's Scope and omissions section defers to it rather than restating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "Issue #949 (task: document implementation/mobile/feature-map.md) is the sibling corpus task in this same batch responsible for the per-feature breakdown of mobile/lib/features/*; it is unmerged at the time this node was written, so no relationship edge toward it validates."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#949 (issue title, batch dispatch brief for issue #950)"
relationships:
  - type: part-of
    target: architecture-containers-mobile
---

# Buzz mobile Flutter app: implementation reference

This node documents `mobile/lib`'s app-wide implementation architecture --
state management, theming, the `shared/` versus `features/` code layout, and
the enforced-convention tooling around it (file-size ceiling, worktree debug
identity, event-kind sync with desktop) -- as the concrete realization of the
conventions this repository's `CLAUDE.md` states for mobile under its
"Mobile App (Flutter)" section. It documents the app's overall architecture,
not the per-feature breakdown of `lib/features/*`, which is `#949`'s
sibling node's territory.

## Target

The target is `CLAUDE.md`'s "Mobile App (Flutter)" section (repository root,
`## Mobile App (Flutter)` heading and its `### Architecture`, `### Rules`,
`### Quality Checks` and `### Testing Conventions` subsections) -- a
convention document, not itself a corpus node. `CLAUDE.md` carries no corpus
node id, so this node declares no `implements` edge toward it (per
`AGENTS.md`'s rule that an edge to a nonexistent id is a hard validation
error, not a placeholder); a reader can open `CLAUDE.md` directly at the
repository root to read the target prose this node traces.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `mobile/lib/app.dart` (`App extends HookConsumerWidget`), `mobile/lib/main.dart` (`runBuzzApp`'s `ProviderScope`) | "favor Riverpod for state and always use `HookConsumerWidget` or `ConsumerWidget`" | Root widget itself is the pattern's own instance, not just a downstream convention. |
| `mobile/lib` (zero `extends StatefulWidget` matches, repo-wide grep) | "NEVER use `StatefulWidget`" | Checked directly against the tree, not assumed from the rule's existence. |
| `mobile/lib/features/*` (ten feature directories), `mobile/lib/shared/*` (sixteen shared modules) | "Feature code under `lib/features/`... shared code under `lib/shared/`" | Directory layout matches the stated convention as of this revision. |
| `mobile/lib/shared/theme/theme_extensions.dart` (`AppThemeExtension.colors`, `.textTheme`) | "Prefer `context.colors` and `context.textTheme`... over raw `Theme.of(context)`" | Extension exists and is the mechanism the rule names. |
| `mobile/lib/shared/theme/color_scheme.dart` (`lightColorScheme`, `darkColorScheme`) | "Theme: Catppuccin Latte (light) / Macchiato (dark) -- matches desktop" | True as the shipped *default* pair; see Divergences for the fuller picture. |
| `mobile/scripts/check-file-sizes.mjs` (`MAX_LINES = 1000`) | "Hard ceiling: 1000 lines/file" | Delegates to the shared `scripts/check-file-sizes-core.mjs` also used by desktop/web. |
| `scripts/mobile-worktree-overrides.sh`, `Justfile` `mobile-dev` / `mobile-build-android` recipes | "worktree-specific debug identity... via `scripts/mobile-worktree-overrides.sh`, applied through `just mobile-dev`" | Script and both invoking recipes verified directly. |
| `mobile/lib/shared/relay/nostr_models.dart:7` (`EventKind`, "Keep in sync with `desktop/src/shared/constants/kinds.ts`") | "event kinds must stay in sync with `desktop/src/shared/constants/kinds.ts`" | The sync obligation is stated in-code as a doc comment, not only in `CLAUDE.md`. |
| `mobile/test/helpers/widget_helpers.dart` (`WidgetHelpers.testable`), fake-notifier test files under `mobile/test/features/*` | "Use the `WidgetHelpers.testable()` wrapper... Fake notifiers should extend the real notifier class and override `build()`" | Both stated testing-convention shapes exist in real test code. |

## Divergences

Two divergences were found by checking `CLAUDE.md`'s claims against the code
directly, rather than assuming agreement:

1. **Which recipe enforces the file-size ceiling.** `CLAUDE.md` states the
   1000-line guard is "enforced by `mobile/scripts/check-file-sizes.mjs` via
   `just mobile-check`". In the repository's `Justfile`, `mobile-check`
   (`dart format --set-exit-if-changed . && flutter analyze`) never invokes
   `check-file-sizes.mjs`; the guard is invoked by a separate recipe,
   `file-size-check`, which the top-level `check` recipe depends on
   independently of `mobile-check` (both are listed as sibling prerequisites
   on the same line). The end state `CLAUDE.md` promises -- the ceiling is
   enforced under `just check` -- holds; the specific recipe name it credits
   does not. This is a naming imprecision worth correcting at the source, not
   filed here as a defect against this node's own subject.
2. **The theme system is broader than the stated Catppuccin pair.** `CLAUDE.md`
   describes the app's theme as "Catppuccin Latte (light) / Macchiato (dark)
   -- matches desktop", which is accurate for `lightColorScheme` /
   `darkColorScheme`, the compiled-in default pair. It does not mention
   `theme_catalog.dart`'s 60-entry Shiki-derived theme catalog, which
   `communityThemeProvider` and `App`'s own `build()` resolve against so each
   community can select a different theme pair -- Catppuccin is the shipped
   default a fresh community starts on, not the only theme the app renders.
   Whether this omission is a documentation gap in `CLAUDE.md` or a
   deliberate simplification (naming only the default) was not resolved by
   this node; it is recorded as a divergence either way, per the template's
   rule that a divergence needs the same evidentiary weight as a compliance
   claim.

No other divergence was found among the claims checked in *Implementation
surface* above -- each row's code was opened directly and matches the rule
it realizes.

## Verification

- `dart format --output=none --set-exit-if-changed .` and `flutter analyze`
  (`just mobile-check`) gate formatting and static analysis.
- `flutter test` (`just mobile-test`) runs the automated suite, including
  real coverage for the theming layer under `mobile/test/shared/theme/` and
  provider/widget tests using the `WidgetHelpers.testable()` /
  fake-notifier pattern described above.
- `node mobile/scripts/check-file-sizes.mjs` (`just file-size-check`, a
  dependency of `just check`, not of `just mobile-check` -- see
  Divergences) gates the 1000-line ceiling.
- `just mobile-dev` / `just mobile-build-android` exercise
  `scripts/mobile-worktree-overrides.sh` as a side effect of running or
  building, rather than through a dedicated test of the script itself; no
  automated test of the override script's own output was located.
- No automated check enforces the `nostr_models.dart` / `kinds.ts` sync
  obligation -- it is a doc comment convention, checked by review rather than
  by tooling, as far as this node's investigation found.

## Relationships

- part-of: `architecture-containers-mobile` -- this node documents mobile's
  implementation architecture as a constituent detail of the container that
  node already describes at higher grain.
- implements: none. See *Target* above for why (target has no corpus node id).
- references: none. No verification/test-strategy corpus node exists yet to
  cite for the *Verification* section above.

## Scope and omissions

**This node covers** the Buzz mobile app's overall implementation
architecture as traced against `CLAUDE.md`'s Mobile App (Flutter)
conventions: state management (Riverpod + `flutter_hooks`, no
`StatefulWidget`), the `features/` versus `shared/` code layout, theming
(the `context.colors`/`context.textTheme` extension mechanism and the
Catppuccin-default-plus-catalog reality), the file-size ceiling and which
recipe actually enforces it, worktree-scoped debug build identity, the
Nostr event-kind sync obligation with desktop, and the stated widget-testing
conventions -- each checked against real code, not merely restated from
`CLAUDE.md`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-feature architecture inside `lib/features/*` (activity, channels, forum, home, invites, pairing, profile, pulse, search, settings) | `#949`'s sibling node, `implementation/mobile/feature-map.md`, unmerged at this node's authoring time |
| The mobile container's responsibility, inbound/outbound interfaces, deployment pipeline and security posture at architecture grain | `architecture-containers-mobile` (this node's `part-of` target) |
| The relay-side event kinds mirrored into `EventKind`, or any server-side behavior | `buzz-core`/`buzz-relay`, out of this container's ownership per `architecture-containers-mobile` |
| Whether the `CLAUDE.md` file-size-recipe imprecision or the theme-catalog omission should be corrected in `CLAUDE.md` itself | unresolved by this node; recorded as a divergence, not fixed, per this task's out-of-scope list forbidding edits to a second document |
| Full inventory of `mobile/test/`'s coverage across every feature and shared module | not attempted; only the theme layer and the testing-helper pattern this node's own claims depend on were checked |

**Expected but not verified when this node was written:**

- Whether any automated check (CI job, lint rule, or test) enforces the
  `nostr_models.dart` `EventKind` / `desktop/src/shared/constants/kinds.ts`
  sync obligation was not found; the *Verification* section above records
  this as an apparent gap rather than asserting one exists, since a
  repository-wide search for such a check was not exhaustive.
- Whether `scripts/mobile-worktree-overrides.sh` itself has any automated
  test (as opposed to being exercised incidentally by `just mobile-dev`) was
  not located during this investigation.
- Whether the two divergences recorded above are already tracked by an open
  issue against `CLAUDE.md` was not checked before writing this node.
