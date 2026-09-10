# Plan: issue #1232 — platforms/agents/kubernetes-backend corpus node

## ALREADY TRUE

- Worktree `__worktrees/task-1232-agents-kubernetes-backend` created off
  `origin/launchpad` at `cad6c375fdcc590158c1456c9fc7875f0f84a844`, branch
  `task/1232-agents-kubernetes-backend`.
- Target file `launchpad/docs/corpus/platforms/agents/kubernetes-backend.md`
  does not exist yet.
- The real implementation is the standalone binary crate
  `crates/buzz-backend-kubernetes` (not `buzz-acp`, as the issue's own
  speculative hint suggested) — a provider process implementing the
  `docs/remote-agents.md` Provider Protocol, invoked by the desktop app as a
  discovered `buzz-backend-<id>` subprocess and bundled as a Tauri
  `externalBin` sidecar (`desktop/src-tauri/tauri.conf.json`).
- `launchpad/docs/corpus/templates/component.md` is merged on
  `origin/launchpad` and is the correct template: subject is one standalone
  software component (a crate), `type: implementation`, required sections
  Responsibility / Public interface / Dependencies / Boundary /
  Relationships / Scope and omissions. It fits this task's DoD tail
  ("states responsibility and interface/boundary", "names dependencies and
  collaborators", "links source implementation and tests", "component-level
  behavior only") far better than any architecture-* template.
- No other corpus node currently exists under `launchpad/docs/corpus/platforms/`
  to conflict with or relate to.

## STEP 1 — Confirm merge-target corpus state and relationship targets

Run `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
and enumerate existing node ids. Decide relationships (expect: none, since
no sibling `platforms`/`architecture` node exists yet to point at).

## STEP 2 — Draft the node body against templates/component.md

Sections: Purpose/scope, Responsibility (cite `main.rs` crate doc comment),
Public interface (wire.rs Request/Response + stdin/stdout contract table),
Dependencies (Cargo.toml for "depends on"; tauri.conf.json externalBin +
backend.rs discovery for "depended on by" — a process-invocation dependency,
not a Cargo dependency, disclosed as such), Boundary (not the whole Provider
Protocol spec, not the desktop-side discovery/invocation logic, not the
deploy state machine's full proof), Relationships (none), Scope and
omissions.

## STEP 3 — Front matter

`id: platforms-agents-kubernetes-backend`, `type: implementation`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. Evidence ledger: one commit-pinned FACT for the revision, FACT
entries citing every opened source (main.rs, wire.rs, config.rs, naming.rs,
pod.rs, intent.rs, gc.rs, client.rs, cluster.rs, classify.rs, reconcile.rs,
Cargo.toml, docs/remote-agents.md sections, tauri.conf.json, backend.rs),
INFERENCE only where reasoning beyond a direct read is needed (e.g. the
process-dependency framing), TEAM_KNOWLEDGE for the issue's own DoD text.

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root; fix any reported errors.

## STEP 5 — Gate and commit

Run the corpus unittest suite as its own tool call, confirm `OK`, then commit
both the node and this plan file with `git commit -s`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## OPEN

- Whether a future `architecture-component` node for a "remote agent
  compute" container should declare `part-of` toward this node, or vice
  versa — deferred until that node exists.
- Whether the desktop-side discovery/invocation code deserves its own
  corpus node — out of scope here (this task documents one component only).

## LEFT OUT

- Full restatement of `docs/remote-agents.md`'s Provider Protocol,
  Deploy State Machine, or Conformance sections — linked, not duplicated.
- Documenting `desktop/src-tauri/src/managed_agents/backend.rs` or
  `agents_deploy.rs` as their own components.
- Any relationship edge, since no sibling node exists in the merged corpus
  tree to target.
