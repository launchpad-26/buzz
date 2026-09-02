# Plan: issue #1291 — corpus node `releases/auto-update.md`

## Issue

launchpad-26/buzz#1291 — "task: document releases/auto-update.md", parent PRD #619.
Objective: create `launchpad/docs/corpus/releases/auto-update.md` as the single
canonical procedure node for the desktop app's auto-update mechanism. DoD checklist
shape matches the `procedure` template (goal/prerequisites, ordered executable
steps, success verification/rollback, links to authoritative commands/config).

## Steps

1. **Gather evidence.** Read `desktop/src-tauri/tauri.conf.json`, `build.rs`,
   `desktop/scripts/build-release-config.mjs`, `.github/workflows/release.yml`,
   `.github/workflows/promote-oss-desktop-release.yml`,
   `scripts/promote-oss-desktop-release.sh`,
   `desktop/scripts/generate-oss-latest-json.sh`, `RELEASING.md`,
   `desktop/src-tauri/src/lib.rs`, `desktop/src-tauri/src/commands/updater.rs`,
   `desktop/src/features/settings/hooks/use-updater.ts`, and confirm the mock
   E2E updater bridge in `desktop/src/testing/e2eBridge.ts`. Confirm no existing
   corpus node under `releases/` exists (none found) and check
   `layers-configuration-desktop-configuration` / `architecture-containers-desktop`
   for content already covering the topic (partial overlap, not duplication).
2. **Confirm shape and id.** `node.schema.json`'s `type` enum confirms `release`
   (singular) is the correct surface value regardless of the plural directory
   name. Template: `templates/procedure.md` (merged on `origin/launchpad`). ID:
   `releases-auto-update`, following the `<directory-path>-<stem>` convention
   used by the majority of already-merged content nodes (no `corpus-` prefix).
3. **Draft the node** at `launchpad/docs/corpus/releases/auto-update.md`:
   Overview + Before you start (build-time enablement prerequisites) + one
   numbered task sequence (promote a release, then confirm clients receive it)
   + See also/Boundary/Relationships/Scope-and-omissions, per the procedure
   template's required sections. Classify every claim FACT (all evidence here
   was read directly) and note the one real gap found: no automated test
   exercises the real check/download/install network path.
4. **Validate.** Run `python3 launchpad/project-intelligence/corpus/validate.py`
   until it exits 0.
5. **Commit gate.** Run the corpus test suite bare/unpiped as its own tool call,
   then `git add` the node + this plan and `git commit -s`. Stop at the commit —
   no push, no PR.
