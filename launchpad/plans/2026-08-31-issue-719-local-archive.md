# Issue #719: document capabilities/archive/local-archive.md

Parent Feature: #613. Repo: launchpad-26/buzz. Base: origin/launchpad.

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/archive/local-archive.md` does not exist
  (confirmed via `test -f`).
- No corpus node under `launchpad/docs/corpus/capabilities/` exists yet at all
  (`find` returned nothing) — this is the first `capabilities`-typed instance
  node in the corpus.
- The capability template (`launchpad/docs/corpus/templates/capability.md`)
  exists and is unambiguous: `type: capabilities`, required sections are
  Capability statement / Maturity / Boundary / Relationships / Scope and
  omissions.
- `origin/launchpad`'s corpus tree currently has no other capability-shaped
  node, so no `relationships` targets resolve — none will be declared.
- The desktop app ships a real, wired "Local archive" capability: a per-identity
  SQLite database (`desktop/src-tauri/src/archive/`) that persists relay
  messages, observer frames (kind 24200) and agent turn metrics (kind 44200)
  for offline/local read access, exposed to users as the "Local archive"
  Settings panel (`desktop/src/features/local-archive/ui/LocalArchiveSettingsCard.tsx`,
  labeled literally "Local archive" in `SettingsPanels.tsx`).
- `launchpad/docs/Observability/current-state/coverage.md` row D04 independently
  names this same capability "Local archive, migrations, and saved
  subscriptions", confirming the name and file scope.

## STEP 1 — Confirm scope and gather evidence (done during investigation)

Sources read: `desktop/src-tauri/src/archive/mod.rs` (module doc + command
registrations), `retention.rs` (retention policy), `store.rs` (schema),
`sync.rs` (backend sync task), `desktop/src/shared/api/tauriArchive.ts` (JS
wrapper), `desktop/src/features/local-archive/**`, `SettingsPanels.tsx`,
`desktop/tests/e2e/{observer-archive-policy,local-archive-screenshots}.spec.ts`,
`CHANGELOG.md`, `launchpad/docs/Observability/current-state/coverage.md`,
`VISION_PROJECTS.md` (no dedicated status row — maturity established from code
instead), `launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md`.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/capabilities/archive/local-archive.md` against
`node.schema.json` and the capability template's required sections:
Capability statement, Maturity (shipped, cited to code/CHANGELOG), Boundary
(not architecture/interface/flow/operations), Relationships (none — no
existing corpus target), Scope and omissions.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm zero
new FAIL entries beyond the known pre-existing baseline (issue #1951).

## STEP 4 — Earn the commit gate

Run, alone: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`, then commit in a separate call.

## GATES

- `validate.py` exits 0 with no new FAIL.
- `unittest discover` on corpus tests prints `OK`.

## BUDGET

Single file + this plan file. No code changes outside `launchpad/`.

## OPEN

- No relationships declared: no capability/architecture/interface node exists
  yet on `origin/launchpad` for this to point at.

## LEFT OUT

- Any second node (e.g. an architecture or interface node for the archive
  subsystem) — out of scope per issue #719 and the one-node-per-task rule.
- Editing runtime code.
