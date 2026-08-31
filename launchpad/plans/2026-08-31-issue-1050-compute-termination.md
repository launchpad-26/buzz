# Plan: issue #1050 — document layers/compute/termination.md

Issue #1050 (task, child of Feature #611): create
`launchpad/docs/corpus/layers/compute/termination.md` as the single canonical
concept node for termination. This is a documentation-only task: one
Markdown file plus this plan. No runtime code changes.

Stated size: one document, one corpus node -> cap: 5 steps.

ALREADY TRUE

- Worktree `task-1050-compute-termination` exists on branch
  `task/1050-compute-termination`, checked out at `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`
  (HEAD, matches sibling `layers/compute/*` drafts' recorded revision).
- `launchpad/docs/corpus/layers/compute/termination.md` does not exist yet
  (confirmed: no such path in this worktree or in `origin/launchpad`).
- `node.schema.json`'s `type` enum contains `layers` (among 13 values); every
  merged/drafted `layers/compute/*` sibling (`lifecycle.md`, `liveness.md`,
  `local-agent-compute.md`, `remote-agent-compute.md`, in sibling worktrees)
  uses `type: layers`, matching parent Feature #611's stated surface.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  contains **no `layers/` directory at all** — none of the sibling
  `layers/compute/*` nodes (#1041-#1049, all still `OPEN`) exist as mergeable
  `relationships` targets today. Confirmed directly, not assumed.
- `launchpad/docs/corpus/templates/concept.md` is the template whose required
  sections (Definition, Use cases, optional Visual aid/Background/Comparison/
  Related resources, required Scope and omissions) match issue #1050's own
  DoD bullets (define the term in one sentence, state boundaries/non-goals,
  link related concepts, examples-only) more closely than the `flow.md`
  template `lifecycle.md` used — this node documents a **concept**
  ("termination"), not a scenario narration.
- Primary sources already read and line-verified in this worktree:
  `docs/remote-agents.md` (I5 "Intentional termination is final", lines
  243-303; "Stop and Delete", 884-923; "Auto-Stop", 925-972),
  `crates/buzz-acp/src/lib.rs` (`is_owner_control_command`, `shutdown_tx`
  watch channel, SIGTERM wiring), `desktop/src-tauri/src/managed_agents/
  runtime/stop.rs` (`stop_managed_agent_pair`, direct `terminate_process`),
  `desktop/src-tauri/src/commands/agents.rs` (`delete_managed_agent`'s
  `force_remote_delete` guard), `crates/buzz-backend-kubernetes/src/{wire,
  classify,gc}.rs` (two-op wire contract, fenced `Action::Delete`, GC as the
  asynchronous destroy path).
- Existing merged corpus nodes usable as `relationships` targets today:
  `architecture-containers-agent-runtime` (`architecture/containers/
  agent-runtime.md`) — the harness this node's termination paths run inside.

STEP 1 — Draft `layers/compute/termination.md` [independent]

<!-- RUNS HERE -->

Write the concept node per `templates/concept.md`'s shape: intro + Definition
(termination = an agent's compute instance permanently ceasing to run,
triggered intentionally — owner `!shutdown`/local kill, or Auto-Stop
inactivity self-termination — as distinct from an abnormal death, from
"destroy"/GC of substrate residue, and from liveness detection), Visual aid
(one Mermaid diagram contrasting local direct-kill vs. remote relay-message
termination), Use cases, Comparison table (local vs. remote termination:
trigger, mechanism, synchronicity, residue cleanup), `relationships` (one
`references` edge to `architecture-containers-agent-runtime`; none to
unmerged `layers/*` siblings, per *ALREADY TRUE*), and a Scope and omissions
section naming what this node does not cover (liveness detection #1044,
lifecycle flow narration #1043, Kubernetes GC/fencing mechanics #1042,
local-agent supervision #1045, remote-agent umbrella concept #1048,
mesh-compute #1046) and what was expected but not independently verified
(Known Defects 6/7's current status, whether `sprout-backend-blox` shares
this termination model). Every evidence entry cites a source actually opened
in this session (see *ALREADY TRUE*); no fabricated symbols or line ranges.

done when: `launchpad/docs/corpus/layers/compute/termination.md` exists,
schema-valid front matter (`id: layers-compute-termination`, `type: layers`,
`status: draft`, `origin: launchpad`), and every bullet in issue #1050's DoD
checklist is satisfied by the body.

STEP 2 — Validate and test [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` (expect a
`PASS` line; pre-existing `UNVERIFIED` noise elsewhere in the corpus is not
this task's concern) and, in a separate step, `python3 -m unittest discover
-s launchpad/project-intelligence/corpus/tests -p "test_*.py"` (expect `OK`).

done when: both commands are run and both report success (`validate.py`
prints a line ending `PASS`; the unittest run ends `OK`).

STEP 3 — Commit [needs 2]

`git add` the new document plus this plan file; `git commit -s` with message
`docs(corpus): document compute termination (#1050)`. No push, no PR — this
child document ships later as part of one batched PR for all of Feature
#611's 36 documents.

done when: `git show --stat HEAD` shows exactly two files (the corpus
document and this plan), and the commit carries `Signed-off-by`.

PARALLEL

None — three steps, each depending on the previous (draft, then validate,
then commit). Nothing here runs concurrently with anything else in this
worktree.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must print a
  `PASS` line before committing.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` must print `OK` before committing.
- The repo's commit gate (signed commit, no `--no-verify`) applies as normal;
  if it refuses with no stamp found, that is reported as BLOCKED rather than
  routed around.

BUDGET

One Markdown file (~250-400 lines, matching the sibling concept-shaped nodes
`local-agent-compute.md`/`remote-agent-compute.md`) plus this plan. No code
changes, no new tests beyond the existing corpus validator/unittest suite.

OPEN

- Whether `layers-compute-termination` should later gain `relationships`
  edges to the sibling `layers/compute/*` nodes once they all merge together
  in the same batched PR — left for a post-merge pass, not decided here,
  since none of them exist on `origin/launchpad` at draft time and this
  task's own instructions restrict relationships to what resolves there today.
- Whether Known Defect 6 (pinned clean-exit-code contract) or Known Defect 7
  (shared shutdown-tail budget) have closed since `docs/remote-agents.md`'s
  own `28ae6cd21` pin — not re-verified independently for this node; recorded
  as an open gap in the document's own Scope and omissions section instead of
  resolved here.

LEFT OUT

- Any second corpus node (e.g., a separate node for "destroy"/GC as its own
  concept) — a newly discovered second concept is filed as its own task per
  `AGENTS.md`, not folded into this one.
- Re-narrating the full deploy/lifecycle flow already covered by sibling
  issue #1043's `lifecycle.md` — this node defines the term "termination";
  it does not re-tell the sequence diagram.
- Any change to `docs/remote-agents.md` itself, or to any Rust/TS source —
  this task is documentation-only.
