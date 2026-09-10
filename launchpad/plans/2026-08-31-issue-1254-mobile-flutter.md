# Issue #1254 — platforms/mobile/flutter corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/mobile/flutter.md` does not exist; no `platforms/`
  directory exists anywhere under `launchpad/docs/corpus/` yet.
- No per-type template for `platforms/**` exists (`AGENTS.md`'s own gap table: "Templates
  for each node type ... somewhere in #1307-#1351"). Closest fits reviewed:
  `templates/component.md` (responsibility / public interface / dependencies / boundary
  shape) matches the issue's DoD almost exactly; `templates/architecture-component.md` is
  the wrong template (C4 container-decomposition-with-diagram subject, not this issue's).
- A sibling architecture node, `launchpad/docs/corpus/architecture/containers/mobile.md`
  (`id: architecture-containers-mobile`, `type: architecture`), already documents the
  mobile container's responsibility, interfaces and deployment at the *container* level.
  This task's node must not duplicate that — it documents Flutter's internal
  architecture (state management, module boundary, theming), one level down.
- Per finding #4 from the orchestrator: sibling nodes under `platforms/**` have settled
  on `type: platforms` (an inference, since no platforms-specific template exists) — used
  here rather than `component.md`'s own `type: implementation` recommendation, since the
  issue places this file under `platforms/mobile/`.
- `origin/launchpad` corpus tree at fetch time has no other node whose id a
  `relationships` entry here could safely target (checked via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`) — the only
  content-bearing candidate, `architecture-containers-mobile`, is a reasonable
  `references`/`part-of` target in spirit, but scope discipline says: only declare it if
  it resolves on `origin/launchpad`, which it does (file exists there). Will add a
  `references` relationship to it.

## STEP 1 — Investigate the real Flutter architecture

Read `mobile/lib/main.dart`, `app.dart`, `mobile/README.md`'s Architecture section,
`mobile/analysis_options.yaml`, `mobile/pubspec.yaml`, and grep for `StatefulWidget` /
`HookConsumerWidget` / `ConsumerWidget` / provider kinds to confirm CLAUDE.md's claims
against real code rather than restating CLAUDE.md. Confirm the `lib/features/` vs
`lib/shared/` split, the part-file pattern for splitting large widgets, and the
`mobile/test/helpers/widget_helpers.dart` testing convention.
**Done when:** every claim below has a citation to a file actually opened.

## STEP 2 — Investigate the theme system

Read `mobile/lib/shared/theme/{theme,color_scheme,app_theme,adaptive_theme,
theme_catalog,theme_provider,grid}.dart` to confirm the Catppuccin Latte/Macchiato
default scheme, the adaptive-theme engine that derives a Material `ColorScheme` from any
of 60 cataloged syntax themes, and the `Grid`/`Radii` spacing/radius tokens.
**Done when:** the theme section cites real files, not just CLAUDE.md's summary.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/mobile/flutter.md` using `component.md`'s shape
(purpose, responsibility, public interface/conventions, dependencies, boundary,
relationships, scope-and-omissions) adapted to `type: platforms`, front matter validated
against `node.schema.json`. Keep it component-level: Android/iOS platform-shell specifics
are #1252/#1255; navigation is #1257 — name them as boundary exclusions, do not describe
their content.
**Done when:** every DoD bullet in the issue is satisfied by a specific section.

## STEP 4 — Validate: no new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py`, note the pre-existing
FAIL set, then temporarily move the new file aside, re-run, and diff the FAIL sets.
**Done when:** the FAIL set is byte-identical with and without the new file.

## STEP 5 — Commit

Run the corpus unittest suite as the sole content of one Bash call, then `git add` +
`git commit -s` as a second call.
**Done when:** `OK` from unittest and a successful commit with a real SHA.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` contributes zero new FAIL
  lines vs. the pre-existing baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  exits `OK`.
- Every evidence citation points to a file this session actually opened; every `A-B` line
  range citation uses the `path:A-B` format.
- Every `relationships[].target` resolves against `origin/launchpad`.

## OPEN

- Whether `architecture-containers-mobile` is the right `references` target versus no
  relationship at all — resolved: it exists on `origin/launchpad` and is a genuine
  neighbor (container vs. this node's platform/framework-internals angle), so declaring
  `references` toward it is honest and low-risk.

## LEFT OUT

- Android/iOS platform-shell integration detail (worktree app identifiers, push
  capability, signing) — owned by sibling issues #1252/#1255.
- Navigation/routing detail — owned by #1257.
- Full inventory of all 60 cataloged syntax themes, or of every feature module's
  internal design — out of scope for a component-level platform node.
- Test-suite structure beyond naming the convention and its helper — not this issue's DoD.
