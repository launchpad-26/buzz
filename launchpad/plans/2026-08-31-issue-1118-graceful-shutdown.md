# Issue #1118 — corpus node: layers/lifecycle/graceful-shutdown.md
Stated size: not stated on the issue → cap: 5 steps (per this batch's dispatch brief for Feature #611's layers/lifecycle/* task set)

ALREADY TRUE  (verified against git, not notes)
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
  `launchpad/docs/corpus/templates/flow.md` are merged on `origin/launchpad`. The target file
  `launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md` does not exist yet (`test -f`
  confirmed NOT EXISTS in the fresh worktree). No `layers/` directory exists anywhere in
  `origin/launchpad`'s corpus tree yet (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` lists none). `crates/buzz-relay/src/main.rs` already documents its own
  shutdown budget in a doc-comment above `GRACEFUL_DRAIN_TIMEOUT` (SIGTERM → 5s grace → 30s hard
  drain), and `docs/remote-agents.md` names buzz-acp's shutdown tail as an unbounded "Known Defect
  7" as of this repository's current `docs/remote-agents.md` text.

STEP 1 — Gather evidence  [independent]
Read `crates/buzz-relay/src/main.rs` (`shutdown_signal`, `serve`'s
shutdown wiring, the `GRACEFUL_DRAIN_TIMEOUT` doc comment, the post-`serve` `audit_shutdown.drain`
and OTEL tracer-provider shutdown calls), `crates/buzz-relay/src/state.rs` (`drain_all`,
`drain_all_jittered`, `AuditShutdownHandle::drain`, the audit worker's cancel-then-drain loop),
`crates/buzz-relay/src/router.rs` (`readiness_handler`'s `shutting_down` 503, the WS-upgrade
handler's shutdown refusal), `crates/buzz-acp/src/lib.rs` (the SIGINT/SIGTERM/`!shutdown` watch
channel, the wake-task drain, in-flight-prompt drain, per-slot serial reap, presence-offline
publish, relay shutdown call), `crates/buzz-acp/src/acp.rs` (`AcpClient::shutdown`'s 5s bounded
kill-and-wait) and `crates/buzz-acp/src/relay.rs` (`HarnessRelay::shutdown`'s 5s bounded close),
plus `docs/remote-agents.md`'s "Stop and Delete" section for the shutdown-tail-budget requirement
and Known Defect 7. Also read one existing merged flow instance
(`launchpad/docs/corpus/architecture/flows/websocket-connection.md`) for front-matter/id/origin
convention, and `launchpad/docs/corpus/architecture/containers/{relay,agent-runtime}.md` to confirm
their ids as `references` targets.
        done when: every symbol/path above has been opened and its cited behavior confirmed by
        reading the actual code (not paraphrased from memory), and `git rev-parse HEAD` is
        recorded for the provenance entry.

STEP 2 — Write the node  [needs 1]
Write front matter (id `layers-lifecycle-graceful-shutdown`, type `layers` — with an
explicit "note on type" section explaining the departure from `flow.md`'s own worked-skeleton
default of `type: architecture`, since node.schema.json's `type` enum names `layers` as its own
member and this Feature's own directory taxonomy (`layers/lifecycle/*`) uses it — status `draft`,
origin `launchpad` matching the existing flow-instance precedent, audiences `[agent, developer,
reviewer]`, `relationships: references` → `architecture-containers-relay` and
`architecture-containers-agent-runtime` only, since those are the only two nodes confirmed present
on `origin/launchpad` that this flow's actors are built from) and the body: Flow statement,
Sequence (relay-side and buzz-acp-side, each step cited to code), Diagram(s), Outcome (success +
failure paths for both processes), Boundary statement, Relationships, Scope and omissions — the
latter explicitly recording the buzz-acp shutdown-tail-budget gap (Known Defect 7) as
"expected but not verified" / an open gap rather than folding a fix or a second concept into this
node.
        done when: the file exists at the target path, every claim in the evidence ledger is
        classified FACT/INFERENCE/TEAM_KNOWLEDGE per what was actually opened in Step 1, and the
        required flow.md sections are all present.

STEP 3 — Validate  [needs 2]
Run `python3 launchpad/project-intelligence/corpus/validate.py` against the full tree;
fix and re-run until exit 0.
        done when: the command prints exit status 0.

STEP 4 — Self-review  [needs 3]  ← RUNS HERE
Re-read the diff against issue #1118's Definition-of-Done checklist line by line;
confirm no second hand-authored canonical document was created and `validate.py` still exits 0.
        done when: every DoD bullet is checked off against the actual file content, in writing, in
        the final report.

STEP 5 — Earn the stamp and commit  [needs 4]
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call, confirm `OK`, then commit (plan + node)
with `git commit -s` in a separate call. Do not push, do not open a PR.
        done when: the test run reports `OK` and `git log -1` on the worktree branch shows the new
        commit containing both the plan file and the corpus node.

PARALLEL: none of the five steps can run as independent subagents against each other — Step 1
feeds every claim Step 2 writes, Step 2's file is what Step 3 validates, Step 4 reviews Step 2's
actual diff, and Step 5's commit must follow a clean Step 3/4. This is a single-file,
single-worktree task with no independent sub-parts to fan out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
report `OK` before commit — this is the verify-gate stamp for this batch. `review-adjudicate` and
the cross-model final-review pass are explicitly deferred to the batch owner's later integration
step, not run in this session. `qa` explore mode does not apply — this is a documentation-only
change with no runtime interface to exercise.

BUDGET: Step 1 (evidence gathering across two crates' shutdown paths, relay and buzz-acp) is the
step most likely to eat the budget, since it requires reading real signal-handling, drain, and
reap code across `buzz-relay` and `buzz-acp` rather than paraphrasing `docs/remote-agents.md`'s
own prose.

OPEN: the issue's DoD does not say whether "graceful shutdown" as "the single canonical flow node"
should cover exactly one process's shutdown sequence or narrate both of Buzz's long-running
processes (`buzz-relay`, `buzz-acp`) that implement it. The dispatch brief names both explicitly
(relay SIGTERM handling and the buzz-acp shutdown-tail budget), so this plan treats the node as
covering both as two coordinated sequences within one "graceful shutdown" idea, rather than
splitting into two nodes — recorded here rather than silently narrowed to one process.

LEFT OUT: no relationship to any other `layers/lifecycle/*` sibling node (background-workers
#1115, cancellation #1116, concurrency #1117, resource-cleanup #1119, startup #1120) — those are
drafted in unmerged sibling branches in this same batch run and are not present on
`origin/launchpad`, so per `AGENTS.md` step 9 they are not valid relationship targets yet. Fixing
buzz-acp's unbounded shutdown-tail (Known Defect 7, per `docs/remote-agents.md`) is explicitly out
of scope — it is documented as an observed gap, not resolved, per issue #1118's own "Out of scope:
Changing runtime product behavior unless a separately linked implementation issue owns that
change."
