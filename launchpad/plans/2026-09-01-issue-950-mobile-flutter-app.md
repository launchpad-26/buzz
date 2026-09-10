Issue #950 — task: document implementation/mobile/flutter-app.md
Stated size: no `Size` line  →  cap: 5 steps (set by the corpus-batch-author dispatch
  brief for this task: "Write a plan ... capped at 5 steps", not asked per-issue)

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-950-mobile-flutter-app` is on branch
    `task/950-mobile-flutter-app`, based on `origin/launchpad`, HEAD
    `76a0a4ebbe4bc4d852b0d04362ed768620da34b3`, working tree clean.
  `launchpad/docs/corpus/implementation/` does NOT exist anywhere in this tree —
    this will be the corpus's first `type: implementation` node.
  `launchpad/docs/corpus/architecture/containers/mobile.md` exists on
    `origin/launchpad` (`id: architecture-containers-mobile`, `status: draft`), is a
    loaded node for validation purposes regardless of its `draft` status, and already
    documents the mobile app's responsibility/interfaces/deployment at container
    grain — this node must not restate that content, only its own architecture slice.
  Sibling issue #949 (`implementation/mobile/feature-map.md`) is unmerged and shares
    no relationship-safe id with this task — no edge to it can be declared.
  `templates/implementation-reference.md` requires seven body sections (Realization
    statement, Target, Implementation surface, Divergences, Verification,
    Relationships, Scope and omissions) and states a target with no corpus node id
    yet (true of `CLAUDE.md`, the mobile-conventions document this node traces) must
    be named by real path in prose, with no `implements` edge invented.
  Verified against real code in `mobile/lib/`, not assumed from `CLAUDE.md`'s prose:
    `App` (`mobile/lib/app.dart`) and `main.dart`'s `runBuzzApp` build on
      `HookConsumerWidget` / `ProviderScope` (`hooks_riverpod` + `flutter_hooks`).
    `grep -rln "extends StatefulWidget" mobile/lib` returns zero files — the "never
      StatefulWidget" convention holds today, checked directly rather than trusted.
    `mobile/lib/shared/theme/theme_extensions.dart` defines `context.colors` /
      `context.textTheme` exactly as `CLAUDE.md` describes.
    `mobile/lib/shared/theme/color_scheme.dart` defines `lightColorScheme` /
      `darkColorScheme` as Catppuccin Latte/Macchiato (mauve accent), matching
      desktop — but `theme_catalog.dart` also ships a 60-entry Shiki-derived theme
      catalog selectable per community, which `CLAUDE.md`'s one-line theme claim
      does not mention. Catppuccin is the shipped *default*, not the only theme.
    `mobile/scripts/check-file-sizes.mjs` enforces `MAX_LINES = 1000` over `lib/**/*.dart`.
    `Justfile` shows `mobile-check` runs `dart format --set-exit-if-changed . &&
      flutter analyze` only; the file-size guard is a *separate* recipe
      (`file-size-check`, line 106, which itself calls
      `node mobile/scripts/check-file-sizes.mjs`), and `check` (line 96) depends on
      both `mobile-check` and `file-size-check` as siblings — `CLAUDE.md`'s phrase
      "enforced ... via `just mobile-check`" is imprecise about which recipe runs it.
    `scripts/mobile-worktree-overrides.sh` writes worktree-scoped iOS/Android debug
      identity files, invoked by `just mobile-dev` / `just mobile-build-android`.
    `mobile/lib/shared/relay/nostr_models.dart:7` carries the literal comment "Keep
      in sync with `desktop/src/shared/constants/kinds.ts`" above `EventKind`.
    `mobile/test/shared/theme/` and `mobile/test/helpers/widget_helpers.dart`
      (`WidgetHelpers.testable()`) exist with real theme/provider test coverage.

STEP 1  [independent]  ← RUNS HERE  Create
        `launchpad/docs/corpus/implementation/mobile/flutter-app.md` with schema-valid
        front matter (`id: implementation-mobile-flutter-app`, `type: implementation`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
        an `evidence` ledger with one commit-citation provenance entry plus one entry
        per substantive claim, classified honestly; `relationships: [part-of ->
        architecture-containers-mobile]`, no other edges) and the full body per
        `templates/implementation-reference.md`'s seven required sections. Realization
        statement + Target: this node documents `mobile/lib`'s app-wide architecture
        (state management, theming, `shared/` layer, and enforced conventions) as the
        concrete realization of this repository's `CLAUDE.md` "Mobile App (Flutter)"
        section (named by path — no `implements` edge, `CLAUDE.md` carries no corpus
        id). Implementation surface: a table pairing each `CLAUDE.md` claim with the
        file/symbol verified in ALREADY TRUE. Divergences: name the `mobile-check` vs
        `file-size-check` recipe imprecision and the Catppuccin-default-vs-60-theme-
        catalog gap found above — not "none found". Verification: `dart format`,
        `flutter analyze`, `flutter test`, `file-size-check`, and the real test files
        under `mobile/test/shared/theme/`. Scope and omissions: explicitly excludes
        per-feature detail (owned by #949's sibling node) and anything
        `architecture-containers-mobile` already states at container grain.
        done when: the file exists, and `python3
        launchpad/project-intelligence/corpus/validate.py` produces zero lines
        mentioning `implementation-mobile-flutter-app` or the new file's path (other
        output may exist — see STEP 2 for how that is judged, not assumed clean).

STEP 2  [needs 1]  Establish that no validation failure was introduced, distinguishing
        this node's own status from the pre-existing baseline the task brief warns
        about (~21 unrelated failures already on `origin/launchpad`).
        done when: `git stash` (removing the new file), a captured run of
        `python3 launchpad/project-intelligence/corpus/validate.py`, then
        `git stash pop` and a second captured run, show the same FAIL count in both
        runs, i.e. this file adds zero new FAIL lines to whatever baseline already
        exists.

STEP 3  [needs 2]  Run the corpus test suite as the sole command in its own tool call,
        earning the commit-gate stamp per the task's explicit instruction to keep it
        isolated from any other command.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

STEP 4  [needs 3]  Stage exactly the node and this plan, and commit signed-off, as two
        separate tool calls per the task's explicit instruction (stage, then commit).
        done when: `git show --stat HEAD` lists exactly
        `launchpad/docs/corpus/implementation/mobile/flutter-app.md` and
        `launchpad/plans/2026-09-01-issue-950-mobile-flutter-app.md`, and
        `git log -1 --format=%B` contains a `Signed-off-by:` trailer.

STEP 5  [needs 4]  Self-review (via `corpus-review` skill if reachable in-session for a
        docs-only corpus node, else a careful manual pass, stated explicitly either
        way) the committed diff against every Definition of Done bullet in issue #950,
        confirming each evidence citation was reopened and actually supports its
        statement rather than merely resolving structurally.
        done when: a written note maps each of the DoD's ten bullets to where the diff
        satisfies it, names any evidence entry re-opened and found not to support its
        statement (fixed before this step closes), and states plainly whether
        `corpus-review` ran or a manual pass substituted for it.

PARALLEL  None. Steps 1-5 form one linear chain over one target file plus its own
          plan; nothing here is independently dispatchable, and the task's explicit
          "no push, no PR" instruction rules out any parallel integration step.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (STEP 1-2).
          `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the commit
          gate (STEP 3). `corpus-review` or an equivalent manual self-review (STEP 5).
          `review-code`/`review-tests` do not apply — the diff adds no implementation
          or test code, only a Markdown corpus node and this plan.

BUDGET    STEP 1. The Divergences section is the part with a wrong-by-default failure
          mode: an author under time pressure writes "none found" without having
          actually re-checked `CLAUDE.md`'s claims one by one, which is exactly the
          "silence is not evidence of agreement" trap the template names. The two
          divergences already found in ALREADY TRUE must survive into the body, cited
          precisely (`Justfile` line numbers, `theme_catalog.dart`'s comment), not
          softened into agreement.

OPEN      Whether `type: implementation` or `type: interfaces-events` fits better.
          Planned choice: `implementation` — the realizing artifact is an app's
          internal architecture (state/theming/shared-layer conventions), not a
          protocol/wire-contract surface, so the template's default resolution
          applies. Stated so a reviewer can overturn it cheaply.
          Whether `architecture-containers-mobile`'s `status: draft` disqualifies it
          as a `part-of` target. Planned reading: no — `AGENTS.md`'s relationship rule
          is that the target id must be loaded by the validator (i.e. merged on
          `origin/launchpad`), not that its own `status` be `active`; nothing in
          `node.schema.json` or `relationships.schema.json` conditions edge validity
          on the target's `status`.

LEFT OUT  An `implements` edge toward `CLAUDE.md`. `CLAUDE.md` carries no corpus node
          id, and inventing one to satisfy the template's preferred relationship type
          is exactly the "edge to a nonexistent id is a hard validation error, not a
          soft placeholder" mistake `AGENTS.md` and the template both warn against.
          Named by real path in the Target section instead.
          Any `references`/`part-of` edge toward `implementation/mobile/feature-map.md`
          (#949). It is a sibling task in the same unmerged batch, not present on
          `origin/launchpad`, so an edge to it is a hard CI failure waiting to happen —
          exactly the trap `AGENTS.md` step 9 names. The natural moment to add it is
          once both land in the same integration pass.
          Per-feature breakdown of `lib/features/*` (activity, channels, forum, home,
          invites, pairing, profile, pulse, search, settings). That is #949's stated
          territory per the task brief; duplicating it here would violate the "one
          independently maintainable idea" rule both `AGENTS.md` and the issue's DoD
          state.
          Editing `architecture-containers-mobile` or `CLAUDE.md` even where this
          investigation surfaced a real imprecision in both (the `mobile-check` vs
          `file-size-check` recipe claim). Out of this issue's scope; the divergence
          is recorded in the new node's own Divergences section instead, which is
          exactly what that section exists for.
