Issue: launchpad-26/buzz#1043 — task: document layers/compute/lifecycle.md
Parent: Feature #611 (compute observability, configuration and lifecycle corpus), PRD #602

Stated size: no explicit Size line on #1043; dispatch prompt says cap: 5 steps (single small document)

ALREADY TRUE

- Worktree `__worktrees/task-1043-compute-lifecycle` exists, branched from
  `origin/launchpad` at `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`, on branch
  `task/1043-compute-lifecycle`.
- `launchpad/docs/corpus/layers/compute/lifecycle.md` does not exist yet
  (confirmed: `ls` on `layers/` and `layers/compute/` both fail — no such
  directory). No BLOCKED condition.
- `launchpad/docs/corpus/layers/` does not exist at all yet on
  `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` lists no `layers/*` path) — this is the first node
  in that surface.
- The issue's Objective names the document's kind: "the single canonical
  **flow** node for lifecycle" -> template `launchpad/docs/corpus/templates/flow.md`
  exists and matches.
- `node.schema.json`'s `type` enum has 13 members including both
  `architecture` and `layers`. `flow.md`'s own worked skeleton defaults a
  flow instance to `type: architecture`, but that default is precedent from
  the `architecture/flows/*` family specifically (12 existing merged/drafted
  nodes there, e.g. `architecture-flows-agent-turn`). This task's own target
  path is `layers/compute/lifecycle.md` and Feature #611's stated Outcome is
  "cross-cutting compute, telemetry, configuration and runtime-lifecycle
  behavior" -- i.e. the `layers` surface, not the C4 `architecture` surface.
  Per `standards/taxonomy.md` step 2 ("pick the enum member whose plain-
  English name most concretely names the node's primary subject... not
  where the node currently happens to live"), `type: layers` is the
  deliberate, disclosed choice here, not a default. This will be stated
  explicitly in the node's own body (a "note on type" paragraph, mirroring
  `flow.md`'s own template).
- Deep investigation (general-purpose subagent, cross-checked directly by
  this agent against primary source) has located the real compute-provider
  lifecycle: `docs/remote-agents.md` (draft spec) + `crates/buzz-backend-kubernetes`
  (the only shipped provider binding in this OSS repo) implement create
  (`Action::Create` in `reconcile.rs`/`classify.rs`), start/readiness
  (poll until `Startup::Started` or `DEADLINE`), stop (`!shutdown` /
  inactivity auto-stop handled in `crates/buzz-acp/src/lib.rs`, NOT a
  provider operation), and destroy (fenced `Action::Delete` plus
  preflight/orphan garbage collection in `gc.rs`). Verified directly by this
  agent: `wire.rs`, `classify.rs` (Startup/Action/PullFailure enums,
  `classify()` body), `reconcile.rs` (`Substrate` trait, `deploy()` body,
  `DEADLINE`/`POLL_INTERVAL` consts), `gc.rs` (`OPERATION_DEADLINE_SECS`,
  `ORPHAN_SECRET_MIN_AGE_SECS`), `crates/buzz-acp/src/lib.rs` (`!shutdown`
  handling ~2737-2760, presence-offline publish ~3517-3529), `crates/buzz-acp/src/config.rs:479`
  (`exit_after_inactivity`), `desktop/src-tauri/src/managed_agents/types.rs:6-13`
  (`BackendKind`), and `docs/remote-agents.md` (`### Stop and Delete`,
  `### Auto-Stop`, `### Garbage collection` sections).
- Candidate `relationships` target confirmed to exist on `origin/launchpad`:
  `architecture-containers-agent-runtime` (id read directly from
  `git show origin/launchpad:launchpad/docs/corpus/architecture/containers/agent-runtime.md`) —
  it documents what runs *inside* the pod this flow deploys (sprig/buzz-acp/
  buzz-agent), a natural `references` target, no ownership implied.

STEP 1 [independent]

Write `launchpad/docs/corpus/layers/compute/lifecycle.md` using the `flow.md`
template shape: front matter (`id: layers-compute-lifecycle`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences`, `evidence`,
`relationships: [{type: references, target: architecture-containers-agent-runtime}]`),
body sections Flow statement / Sequence / Diagram (Mermaid `sequenceDiagram`) /
Outcome / Boundary / Relationships / Scope and omissions, scoped to the
Kubernetes provider binding's deploy-run-stop-destroy lifecycle only (explicitly
excluding: `layers/lifecycle/*` process-level relay lifecycle; buzz-acp's own
inner ACP-subprocess spawn/shutdown; `sprout-backend-blox`, a separate closed
repo per this repo's own CLAUDE.md ecosystem table).

<- RUNS HERE

done when: the file exists, front matter parses as valid YAML, and every
Sequence/Outcome step cites a real file path (and where relevant, a line or
line range) this agent directly opened in this worktree.

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and fix every reported error (schema violations, broken node
IDs, invalid source paths, duplicate IDs) until it exits 0.

done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3 [needs 2]

Self-review: re-read the drafted node against #1043's own Definition-of-Done
checklist line by line (schema-valid front matter; one independently
maintainable node; FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links without
duplicating; checked against the recorded revision; validation passes; states
trigger/preconditions/termination; lists ordered interactions and state
movement; identifies auth/trust-boundary crossings; documents failure/abort/
rollback with representative verification links). Confirm no second
hand-authored canonical document was created.

done when: each DoD bullet is confirmed satisfied by a specific section of the
drafted file, or a gap is explicitly named in the final report as a finding
rather than silently left.

STEP 4 [needs 3]

Run the verify-gate stamp command as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then, in a separate tool call, commit with
`git commit -s -m "docs(corpus): document compute lifecycle (#1043)"`.

done when: the unittest run reports `OK` and the commit exists on
`task/1043-compute-lifecycle` (`git log -1 --oneline`), with no push and no
PR opened (per the dispatch prompt's explicit instruction — this task's
commit is integrated into a shared batch PR by a separate later process).

PARALLEL

None. Steps 1-4 are a strict chain (each step's output gates the next); there
is no independent second workstream inside this single-document task.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit (Step 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK` before commit (Step 4) — this is the verify-gate stamp
  command; it must be the sole command in its own tool call, per the
  dispatch prompt.
- No push, no `gh pr create` — this task's commit lands in a later shared
  batch PR.

BUDGET

Single document, already-completed deep-research phase. Remaining work is
drafting (Step 1, the bulk of the effort), one validator fix loop (Step 2,
expected 0-2 iterations), a line-by-line DoD self-review (Step 3), and the
stamp-then-commit sequence (Step 4). No code changes, no new dependencies, no
new tests beyond the existing corpus validator/test suite.

OPEN

- Whether `type: layers` (this plan's choice, disclosed in-body) or
  `type: architecture` (the `flow.md` template's own precedent-based default
  for the `architecture/flows/*` family) is the better fit is a judgment
  call per `standards/taxonomy.md` step 5 ("a node's type MAY be revised
  later") — left to reviewer confirmation, not decided unilaterally as
  unrevisable. The node's own text discloses the reasoning either way.
- Whether Known Defect 6 (pinned intentional-exit-implies-exit-code-0
  contract) and Known Defect 7 (shared shutdown-tail budget with reserved
  finalization slice) in `docs/remote-agents.md` are still open at the
  current worktree HEAD (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`, later
  than the spec's own `28ae6cd21` pin) was not conclusively re-verified for
  either defect — the drafted node will mark this explicitly as "expected
  but not verified" rather than asserting either state.

LEFT OUT

- Drafting a second node for `layers/lifecycle/*` (process-level relay
  startup/shutdown) — explicitly a sibling Feature area per the dispatch
  prompt, not this task's scope.
- Drafting a node for the provider wire protocol as a general, durable
  `interfaces-events` contract (info/deploy operations independent of any
  one scenario) — no such node exists yet on `origin/launchpad`; this flow
  node `references` nothing there because nothing there exists to
  reference, and narrates the protocol's use in this one scenario only, per
  `flow.md`'s own boundary rule against restating an interface's general
  contract.
- Re-deriving or disputing `docs/remote-agents.md`'s own shutdown-timing
  arithmetic (Known Defect 7) — out of scope for a documentation task; the
  drafted node cites what the spec and code state and flags the open
  question above rather than resolving it.
- Filing a follow-up issue for any second concept discovered while
  drafting — none was found that rises to "a second concept/contract/
  procedure" distinct from the one flow being narrated; if one surfaces
  during Step 1 it will be named as a candidate follow-up in the final
  report instead of being folded in, per #1043's own DoD bullet.
