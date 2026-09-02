# Plan: issue #1241 — document platforms/desktop/frontend-backend-bridge.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/frontend-backend-bridge.md` does not exist (checked on this branch, based on `origin/launchpad`).
- `launchpad/docs/corpus/templates/architecture-component.md` is merged and present; its required sections (purpose, component diagram, notation legend, building-block table, boundary, relationships, scope/omissions) map almost 1:1 onto issue #1241's Definition of Done bullets ("well-defined interface/boundary", "names dependencies and collaborators", "links source implementation and tests", "component-level behavior, not the entire containing platform").
- `launchpad/docs/corpus/architecture/containers/desktop.md` (id `architecture-containers-desktop`) is merged on `origin/launchpad` and already states, at container level, that the frontend "Communicates with the Rust backend exclusively through Tauri's IPC (`invoke_handler` commands) and Tauri events" — this task goes one level deeper into that boundary, without restating the container's own content.
- Repository revision recorded for this task: `cad6c375fdcc590158c1456c9fc7875f0f84a844` (`git rev-parse HEAD` on this worktree, tracking `origin/launchpad`).

## STEP 1 — Confirm the corpus `type` value

The template's own text asserts `type: architecture` for architecture-component instances, but that guidance was written for nodes physically filed under `architecture/` (matching `architecture-containers-desktop`'s own placement). This task's target path is `platforms/desktop/...`, and PRD #602 enumerates `platforms` as its own distinct in-scope corpus surface, separate from `architecture`. `validate.py` does not cross-check `type` against directory path, so this is a judgment call, not a schema requirement — record it as an `INFERENCE` in the node itself rather than silently picking one.

## STEP 2 — Investigate the real IPC bridge

Read, don't guess: `desktop/src-tauri/src/lib.rs`'s `invoke_handler!` block, a representative sample of `desktop/src-tauri/src/commands/*.rs` command signatures, `desktop/src/shared/api/tauri.ts` (the central `invokeTauri` wrapper) and its sibling `tauri*.ts` domain modules, `AppState` (`app_state.rs`), the event-emit/listen pairing (`AppHandle::emit` in Rust, `@tauri-apps/api/event`'s `listen`/`emit` in the frontend), the capability/permission file (`capabilities/default.json`), the CSP's `connect-src ipc:` grant in `tauri.conf.json`, and the E2E mock bridge (`desktop/src/testing/e2eBridge.ts`) that substitutes for real IPC in tests.

## STEP 3 — Draft the node against the architecture-component template

One paragraph naming the container (`architecture-containers-desktop`) and the question answered; a Mermaid component diagram; a notation legend; a building-block table (command surface, `invokeTauri` wrapper, domain API modules, `AppState`, event channel, capabilities/permissions, CSP grant, E2E mock bridge); an explicit boundary section; `relationships: part-of -> architecture-containers-desktop`; scope and omissions naming what was expected but not verified (e.g., full enumeration of all 336 registered commands' individual contracts, the mesh-llm-gated command set).

## STEP 4 — Validate in isolation

Stash the new file, run `validate.py`, confirm the pre-existing 21-FAIL baseline is unchanged, restore the file, run `validate.py` again to see the new node's own (expected, non-fatal) `UNVERIFIED` notices on its commit citation.

## STEP 5 — Commit

Run the corpus unittest suite as the sole content of one Bash call, then commit both the node and this plan file with `git commit -s`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, and the new node contributes zero new FAIL lines beyond the pre-existing 21.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Every evidence citation was actually opened; every FACT/INFERENCE/TEAM_KNOWLEDGE classification matches what was actually verified.

## OPEN

- Whether `type: platforms` vs `type: architecture` is the corpus's eventual settled convention for the `platforms/desktop/*` batch is not resolved by this task — flagged as an `INFERENCE` in the node itself, not decided here.

## LEFT OUT

- Documenting any individual command's business logic (channels, messages, agents, etc.) — those are each their own future corpus nodes, not this bridge-mechanism node's concern.
- The mesh-llm feature-gated commands' own protocol — out of scope per the container node's own stated boundary.
- Deciding whether `#[serde(rename_all = "camelCase")]` inconsistency across command-argument structs should be fixed — this is a documentation task, not an implementation change (out of scope per the issue's own "Out of scope" section).
