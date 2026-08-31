# Plan: issue #709 — document capabilities/agents/agent-shutdown.md

## ALREADY TRUE

- Worktree `__worktrees/task-709-agent-shutdown` exists, branch `task/709-agent-shutdown`,
  based on `origin/launchpad` at `131b02f989684117d9ab1dd426f1673fa638e523` — confirmed
  identical to `git fetch origin launchpad && git rev-parse origin/launchpad` re-run
  immediately before drafting.
- Target file `launchpad/docs/corpus/capabilities/agents/agent-shutdown.md` does not exist
  anywhere in the worktree.
- `launchpad/docs/corpus/templates/flow.md` (id `corpus-template-flow`) is merged and
  establishes that a flow-shaped instance node — one narrating an ordered runtime
  interaction — carries `type: architecture` (there is no `flow` enum member), with
  required sections: Flow statement, Sequence, Diagram (Mermaid `sequenceDiagram`),
  Outcome, Boundary statement, Relationships, Scope and omissions. A real merged instance,
  `architecture/flows/agent-turn.md` (id `architecture-flows-agent-turn`), follows this
  shape exactly and is the structural precedent for this node.
- Candidate `references` targets already merged on `origin/launchpad`:
  `architecture-containers-agent-runtime` (the `buzz-acp` harness container) and
  `architecture-flows-agent-turn` (the sibling per-turn flow this shutdown flow drains
  in-flight instances of).
- Every code citation below (shutdown trigger, kill sequence, harness drain order,
  presence publish, circuit breaker, panic recovery, tests) was opened directly in
  `crates/buzz-acp/src/{lib,acp,pool}.rs` at the recorded revision and line ranges
  verified against the actual file content, not taken from a prior research pass
  without re-checking.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/agents/agent-shutdown.md`:
front matter (`id: capabilities-agents-agent-shutdown`, `type: architecture`,
`status: draft`, `origin: launchpad`, `audiences: [developer, operator, reviewer]`,
one evidence entry per substantive claim, `relationships` to the two ids above) plus
body sections per the flow template: Flow statement (trigger + preconditions), Sequence
(ordered, cited steps for owner command / inactivity timeout / SIGTERM / SIGINT triggers,
and for crash detection), Diagram (Mermaid `sequenceDiagram`), Outcome (success and
failure/crash paths, cited), Boundary statement, Relationships, Scope and omissions
(naming the untested SIGKILL-only kill sequence and the whole-harness sequence as gaps,
per the crate's own test coverage).
**Done when:** file exists, every evidence entry backed by an opened citation, no
`entry_class: FACT` resting on an unopened or `pr_review`/`issue_discussion` source.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree root.
**Done when:** the new node adds zero new FAIL entries beyond the 21 pre-existing ones
tracked in issue #1951 (confirm by diffing the error count/names against a baseline run
with the new file removed, or by inspecting that every reported FAIL predates this node).

## STEP 3 — Earn the commit gate

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
**Done when:** output ends `OK`.

## STEP 4 — Commit

`git add` the new node and this plan file; `git commit -s` with message
`docs(corpus): document capabilities/agents/agent-shutdown (#709)`.
**Done when:** commit created, `git status` clean apart from the new commit, no push,
no PR opened.

## PARALLEL

None — single file, single task, no independent sub-work to fan out.

## GATES

- `validate.py` exits 0 with zero new FAIL entries (Step 2).
- Unit test discovery run as a lone, unpiped command prints `OK` (Step 3).
- Both gates pass before the commit in Step 4 — no `--no-verify`, no touching the stamp
  file if blocked.

## BUDGET

4 steps, one file created (plus this plan), no code changes outside
`launchpad/docs/corpus/` and `launchpad/plans/`.

## OPEN

- Whether the whole-harness graceful shutdown sequence (`crates/buzz-acp/src/lib.rs`
  lines ~3420-3541) has any dedicated end-to-end test is unresolved — grep found none;
  the node states this as a scope gap rather than asserting a test exists.
- Whether `capabilities/agents/` is the right long-term home for a flow-shaped node given
  `architecture/flows/` already holds `agent-turn.md` is not this task's call — the
  manifest assigned this exact path, and the naming standard permits `id` and directory
  placement to vary independently.

## LEFT OUT

- No second document. Nothing encountered while researching (owner control commands
  `!cancel`/`!rotate`, the lazy-pool idle-sleep teardown, the circuit breaker as a general
  mechanism) is folded in beyond what backs this node's own shutdown/termination claims;
  each is mentioned only insofar as it feeds the shutdown path itself.
- No relationship to `architecture-containers-relay` — the relay's own `shutdown()` is one
  step this node cites as evidence, not a claim about the relay container's own shape;
  adding the edge would assert a dependency this node's subject does not need.
