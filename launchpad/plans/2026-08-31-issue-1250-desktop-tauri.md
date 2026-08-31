# Plan: issue #1250 — document platforms/desktop/tauri.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/tauri.md` does not exist (checked on this branch, based on `origin/launchpad`; `launchpad/docs/corpus/platforms/` has no directory at all yet on `origin/launchpad`).
- `launchpad/docs/corpus/templates/component.md` is merged and present. Its required sections (responsibility, public interface, dependencies in both directions, boundary, relationships, scope/omissions) map closely onto issue #1250's Definition of Done bullets ("well-defined interface/boundary", "names dependencies and collaborators", "links source implementation and tests", "component-level behavior, not the entire containing platform").
- `launchpad/docs/corpus/architecture/containers/desktop.md` (id `architecture-containers-desktop`) is merged on `origin/launchpad` and already states, at container level, that the desktop app is a Tauri 2 application (Rust backend crate `buzz_lib` + React 19 frontend). This task goes one level deeper into the Tauri shell/runtime layer itself, without restating the container's own content.
- The sibling task branch `task/1241-desktop-frontend-backend-bridge` (unmerged, local-only) already documents the IPC command/event bridge (`platforms-desktop-frontend-backend-bridge`) and settled `type: platforms` as its working convention for `platforms/desktop/*` nodes, as an `INFERENCE` since no platforms-specific template exists yet. This task follows that same convention for consistency, per the orchestrator's own known-findings brief — the issue's own DoD does not call for anything else.
- Repository revision recorded for this task: `131b02f989684117d9ab1dd426f1673fa638e523` (`git rev-parse HEAD` on this worktree, tracking `origin/launchpad`).

## STEP 1 — Confirm scope boundary against #1241

#1241 (already committed on its own branch) owns the frontend/backend IPC bridge: `invoke_handler!` command dispatch, `AppState`, the `invokeTauri` wrapper, and the event-emit/listen channel. This task must not restate any of that. Its own subject is the Tauri *shell* itself: window lifecycle (creation, reveal, hide-to-tray, huddle companion windows), the capabilities/permissions allowlist, the CSP, and the plugin registration chain in `run()` — the mechanisms that exist whether or not any IPC command ever fires.

## STEP 2 — Investigate the real shell/runtime configuration

Read, don't guess: `desktop/src-tauri/tauri.conf.json` (window config, CSP, macOS private API flag, plugin config block, bundle/externalBin), `desktop/src-tauri/capabilities/default.json` (permission allowlist scoped to `main`/`huddle-*` windows), `desktop/src-tauri/src/lib.rs`'s plugin builder chain in `run()` (single-instance, deep-link, notification, opener, window-state, the inline `initial-window-reveal` plugin, native-websocket, dialog, process, ptt_shortcut's global-shortcut plugin, conditional updater), `desktop/src-tauri/src/initial_window.rs` (first-frame reveal/geometry-settle logic), `desktop/src-tauri/src/app_menu.rs` (macOS menu customization), `desktop/src-tauri/src/ptt_shortcut.rs` (global-shortcut lifecycle tied to huddle state), `desktop/src-tauri/src/huddle/window.rs` (dynamic `huddle-*` companion window creation matching the capability glob), the `RunEvent::WindowEvent`/`CloseRequested` handling near the end of `lib.rs` (hide-to-tray, huddle companion restore), and `desktop/src-tauri/Cargo.toml`/`build.rs` for plugin versions and the `buzz_updater_enabled` cfg gate.

## STEP 3 — Draft the node against the component template

`type: platforms`, id `platforms-desktop-tauri`, `part-of: architecture-containers-desktop`. Sections: purpose/scope naming the container and the question answered; Responsibility (the Tauri shell hosts the webview(s), owns window lifecycle, and enforces two independent security boundaries — CSP and capability permissions — around whatever the frontend/backend bridge does inside it); Public interface (plugin registration chain, window creation API, capability-scoped permission surface); Dependencies (Tauri core + named plugins in Cargo.toml, tauri.conf.json as configuration input, capabilities/default.json); Boundary (explicitly excluding #1241's IPC command/event content, excluding container-level deployment/bundling detail already owned by `architecture-containers-desktop`); Relationships; Scope and omissions naming what was expected but not verified (e.g., Windows/Linux-specific plugin behavior not runtime-tested, the tray-menu module gated to macOS only).

## STEP 4 — Validate in isolation

Stash the new file, run `validate.py`, confirm the pre-existing FAIL baseline (~21-22 entries) is unchanged, restore the file, run `validate.py` again to see the new node's own (expected, non-fatal) `UNVERIFIED` notice on its commit citation.

## STEP 5 — Commit

Run the corpus unittest suite as the sole content of one Bash call, then commit both the node and this plan file with `git commit -s`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, and the new node contributes zero new FAIL lines beyond the pre-existing baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Every evidence citation was actually opened; every FACT/INFERENCE/TEAM_KNOWLEDGE classification matches what was actually verified.
- No content duplicates #1241's IPC-bridge scope.

## OPEN

- Whether `type: platforms` is the corpus's eventual settled convention for the `platforms/desktop/*` batch (versus `type: architecture`, which the component template's sibling `architecture-component` template directs toward) is not resolved by this task — inherited as an open question from #1241, not re-litigated here.

## LEFT OUT

- The frontend/backend IPC command and event bridge — entirely #1241's scope.
- Any individual command's business logic — future per-feature corpus nodes.
- The desktop container's own deployment topology, release lane, and bundling — `architecture-containers-desktop`'s scope.
- Deciding whether the current CSP/capabilities configuration is correct or should change — this is a documentation task, not an implementation change.
