# Plan: issue #716 — document capabilities/agents/remote-agent.md

## ALREADY TRUE

- `docs/remote-agents.md` (1779 lines, status `draft`) is the primary source: provider
  protocol, remote lifecycle model (five invariants I1-I5), Kubernetes binding.
- Sibling capability nodes are drafted as local, unmerged worktree commits (not on
  `origin/launchpad`): `capabilities-agents-managed-agent` (#713, local-subprocess
  counterpart), `capabilities-agents-backend-provider` (#712, the pluggable
  provider/wire-protocol mechanism), `capabilities-agents-agent` (#711, umbrella
  capability, explicitly lists remote-agent as an undrafted sibling and declines any
  edge to it). `layers-compute-remote-agent-compute` (#1048) documents the umbrella
  technical concept/invariants at `layers` level. `platforms-desktop-remote-agent-management`
  (#1247, `type: architecture`) decomposes the desktop-side component realizing this.
  None of these five is present in `git ls-tree origin/launchpad -- launchpad/docs/corpus`
  (verified directly) — none is a valid `relationships` target under AGENTS.md's
  merge-target-branch rule.
- `launchpad/docs/corpus/capabilities/agents/remote-agent.md` does not exist yet.
- Desktop code already enforces the "no management channel" boundary at the command
  layer: `stop_managed_agent` (desktop/src-tauri/src/commands/agents.rs:1039) refuses any
  non-`Local` backend; `delete_managed_agent` (same file:1092) refuses to delete a
  deployed remote agent without `force_remote_delete: true`. A Kubernetes-bundling test
  (desktop/src-tauri/src/commands/agents_tests.rs:545) and the provider wire-fixture
  suite (crates/buzz-backend-kubernetes/tests/wire_fixtures.rs:49) are real, runnable
  verification for this capability.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/agents/remote-agent.md` using the
`capabilities` template (`launchpad/docs/corpus/templates/capability.md`) plus the
`Behavioral rules, constraints and variants` section #711 used to satisfy the same DoD
wording. Frame the capability as the *product-level counterpart to managed-agent*
(what an operator gets: an agent running elsewhere, with no process handle, no exec/
log/kill — only relay presence and a signed stop message) — distinct from
backend-provider's own subject (the pluggable *mechanism* that gets it there) and from
remote-agent-compute's subject (the full invariant/conformance specification). Cite
real `path:line` evidence only (no `#symbol=`/`#line=` fragments): the desktop command
guards, the platform-gating test, the wire-fixture test, and `docs/remote-agents.md`'s
own Abstract/M1/Stop-and-Delete sections. Declare exactly one relationship
(`references: architecture-containers-agent-runtime`, merged) and record, as
`TEAM_KNOWLEDGE`, why no capabilities/layers/platforms-typed sibling is targeted.

Done when: file exists, front matter matches `node.schema.json`'s enum values, every
FACT cites a real path:line I re-opened, Boundary/Scope-and-omissions name the same
five neighbors without restating their content.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm the new node
adds zero new FAIL entries beyond the known 21 pre-existing ones (issue #1951).

Done when: validator output shows the new file passing and the pre-existing FAIL count
is unchanged.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`.

Done when: `OK` observed, no `--no-verify`, no manual stamp edits.

## STEP 4 — Commit

`git add` the new node + this plan file; `git commit -s` referencing #716. Do not push,
do not open a PR (integration is a later phase).

Done when: commit exists on `task/716-remote-agent`, working tree clean.

## STEP 5 — Self-review

Re-read the diff against #716's own DoD checklist line by line; re-open every cited
source; confirm no second canonical document was created; confirm `validate.py`'s FAIL
count is unchanged from baseline.

## PARALLEL

None — single-file task, no independent sub-steps.

## GATES

- `validate.py` — zero new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — must print `OK` before commit.

## BUDGET

One file, ~1 commit. No code changes, no test changes, no push, no PR.

## OPEN

- Whether the eventual integration PR will add relationships from this node to its
  five now-unmerged siblings once they land together — left to the integration phase,
  not this task.

## LEFT OUT

- Any relationship to `capabilities-agents-managed-agent`, `capabilities-agents-backend-provider`,
  `capabilities-agents-agent`, `layers-compute-remote-agent-compute`, or
  `platforms-desktop-remote-agent-management` — none is merged to `origin/launchpad`,
  so none is a valid target today (same reasoning #713 and #711 already applied to
  their own sibling edges).
- Restating the Kubernetes binding's internals, the provider wire schema, or the five
  invariants' full argument — all owned by other (existing or future) nodes.
