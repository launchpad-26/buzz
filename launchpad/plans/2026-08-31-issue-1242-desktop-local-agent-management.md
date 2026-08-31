# Plan: issue #1242 — platforms/desktop/local-agent-management.md

## ALREADY TRUE

- Worktree `__worktrees/task-1242-desktop-local-agent-management` created off
  `origin/launchpad` at commit `cad6c375fdcc590158c1456c9fc7875f0f84a844`.
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`)
  — no prior canonical document for this task, and no `platforms/` precedent
  to match against.
- `launchpad/docs/corpus/templates/component.md` is merged and its Required
  sections (Responsibility, Public interface, Dependencies, Boundary,
  Relationships, Scope and omissions) line up with issue #1242's own DoD
  bullets (responsibility/interface/boundary, dependencies/collaborators,
  links to implementation/tests, component-level only). It prescribes
  `type: implementation`, but `node.schema.json`'s enum also carries a
  `platforms` surface that matches this task's own path
  (`platforms/desktop/...`) and the precedent set by
  `architecture/containers/desktop.md` (type mirrors its own top-level
  corpus directory). No template targets `type: platforms` specifically, so
  per `AGENTS.md`'s documented gap this node is hand-authored against
  `node.schema.json` while borrowing `component.md`'s section shape, and the
  node says so explicitly.
- `desktop/src-tauri/src/managed_agents/types.rs`'s `BackendKind` enum
  (`Local` vs `Provider { id, config }`) is the actual code-level boundary
  between this task's subject (local) and sibling issue #1247's subject
  (remote/provider-backed) — read directly, not inferred from titles.
- `architecture-containers-desktop` (id in
  `launchpad/docs/corpus/architecture/containers/desktop.md`) already exists
  on `origin/launchpad` — a valid `part-of` relationship target.

## STEP 1 — Confirm scope boundary in code

Read `desktop/src-tauri/src/managed_agents/{types.rs,mod.rs,backend.rs}` to
fix the local/remote line at `BackendKind`, and identify which submodules
implement local spawn/supervise/persist (runtime.rs, process_lifecycle.rs,
runtime/{lifecycle,process,orphan_sweep,stop}.rs, storage.rs, restore.rs,
reconcile.rs, reserved_env_keys.rs) versus remote deploy (backend.rs).

## STEP 2 — Gather evidence for each claim

Read spawn_agent_child (runtime.rs), reserved-env-key filtering
(reserved_env_keys.rs + env_vars.rs), cross-platform process supervision
(runtime/lifecycle.rs, runtime/process.rs, process_lifecycle.rs — Windows
Job Objects vs Unix process groups), local persistence (storage.rs), and
boot-time restore/reconcile (restore.rs, reconcile.rs). Record exact
path:line citations for every claim.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/desktop/local-agent-management.md`
with schema-valid front matter (`type: platforms`, `status: draft`,
`origin: launchpad`), one evidence entry per claim (FACT for everything
opened directly), a `part-of` relationship to `architecture-containers-desktop`,
and a body covering: responsibility, spawn/env interface, dependencies (both
directions), cross-platform supervision, security gates (reserved env keys,
PID-reuse-safe ownership checks), explicit boundary against remote/provider
agent management (#1247) and against the desktop container's other
responsibilities, and scope/omissions.

## STEP 4 — Validate in isolation

Run `validate.py` with the new file present and again with it removed (via
`git stash` scoped to the file) to confirm the new node contributes zero new
FAIL lines beyond the pre-existing 21.

## STEP 5 — Commit

Run the corpus unit tests as the sole content of one Bash call, then commit
both the node and this plan file with `git commit -s`. No push, no PR.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, and
  the new node adds zero new FAIL lines versus the pre-existing 21-FAIL
  baseline on a clean checkout.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Every evidence citation is a bare repo path (or `path:A-B` range) actually
  opened for this task.

## OPEN

- Whether a future `platforms`-specific template (once authored under
  #1307-#1351) will reshape this node's section headings — expected, per
  `AGENTS.md`'s own statement that pre-standard nodes get reshaped later.

## LEFT OUT

- `backend.rs`'s remote/Kubernetes-backed provider deploy path — issue
  #1247's subject, not duplicated here.
- The desktop container's other responsibilities (identity storage, media
  proxy, terminal, relay connection) — already covered by
  `architecture-containers-desktop`.
- The ACP protocol / `buzz-acp` binary's own internal behavior once spawned
  — a separate component, out of this node's one-idea scope.
