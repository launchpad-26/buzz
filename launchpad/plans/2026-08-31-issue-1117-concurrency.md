# Issue #1117 — corpus node: layers/lifecycle/concurrency.md
Stated size: not stated on the issue → cap: 5 steps (per this batch's dispatch brief for
Feature #611's layers/lifecycle/* task set)

ALREADY TRUE  (verified against git, not notes)
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
  `launchpad/docs/corpus/templates/concept.md` are merged on `origin/launchpad` (confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, HEAD
  `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`). The target file
  `launchpad/docs/corpus/layers/lifecycle/concurrency.md` does not exist yet (confirmed with
  `ls`/`find` in this worktree). No `layers/` directory exists anywhere in `origin/launchpad`'s
  corpus tree yet. Issue #1117's own DoD checklist (define the term in one sentence, state
  boundaries/non-goals, link to related concepts/implementation/verification, use examples only
  to clarify — not a sequence/trigger/outcome shape) matches `templates/concept.md`'s Required
  Sections exactly, not `templates/flow.md`'s shape that siblings #1118/#1120 used — confirmed by
  reading both templates side by side. `crates/buzz-relay/src/connection.rs` and
  `crates/buzz-relay/src/state.rs` already contain concrete, citable concurrency primitives
  (`tokio::sync::Semaphore`, `DashMap`, `tokio::sync::{Mutex,RwLock}`, `mpsc`/`watch` channels,
  `tokio::spawn`, biased `tokio::select!`) confirmed by direct reading, not paraphrase.

STEP 1 — Gather evidence  [independent]
Read `crates/buzz-relay/src/connection.rs` in full (the per-connection task fan-out:
`handle_active_connection`'s semaphore-gated admission via `conn_semaphore`, the four
cooperating tasks spawned per connection — `recv_loop` (driving thread), `send_loop`/`send_loop_inner`
(biased `tokio::select!` prioritizing restart > cancel > control > data, with `feed`/`flush`
batching up to `MAX_WS_SEND_BATCH`), `heartbeat_loop`, and the inline `auth_timeout_task` — and
per-message handler concurrency gated by `handler_semaphore` inside `handle_text_message`, each
spawned handler wrapped in its own tracing span). Read `crates/buzz-relay/src/state.rs`'s
`ConnectionManager` (`DashMap<Uuid, ConnEntry>` as the concurrent connection registry, avoiding one
global `Mutex<HashMap>`), the four named semaphores on `AppState`
(`conn_semaphore`/`handler_semaphore`/`git_semaphore`/`media_upload_semaphore`), and the
`ConnectionState` doc comment's explicit statement of its own locking-by-access-pattern rationale
(`RwLock` for read-heavy `auth_state`, `Mutex` for write-heavy `subscriptions`, channels for
everything needing no shared-memory coordination at all). Identify the connection.rs unit test
(`send_loop_batches_queued_data_frames_into_one_flush`) as a representative verification citation.
Explicitly note where this concept's boundary must stop: `tokio_util::sync::CancellationToken`
usage (owned by #1116 cancellation), the SIGTERM/watch-channel shutdown sequence and drain (owned
by #1118 graceful-shutdown, already merged in its own worktree), and the background-task inventory
spawned at startup (owned by #1115 background-workers) are all visible in the same files but are
each a different sibling's subject — cite them only as boundary callouts, not as this node's own
narrated content.
        done when: `connection.rs` and the cited spans of `state.rs` have been opened and read in
        full (not paraphrased from memory), the representative test has been located by name and
        line, and `git rev-parse HEAD` is recorded for the provenance entry.

STEP 2 — Write the node  [needs 1]
Write front matter (id `layers-lifecycle-concurrency`, type `layers` — with an explicit "note on
type" section mirroring the reasoning already disclosed in siblings #1118/#1120's own bodies:
node.schema.json's `type` enum names `layers` as its own member and Feature #611's directory
taxonomy is `layers/lifecycle/*` — status `draft`, origin `launchpad`, audiences `[agent,
developer, reviewer]`, one `relationships: references` edge to `architecture-containers-relay`
(the only container this node's evidence is drawn from, confirmed present on `origin/launchpad`))
and the body per `templates/concept.md`'s required sections: an opening paragraph, a one-sentence
Definition (concurrency = multiple tokio tasks and shared, `Arc`-wrapped state making progress
inside one relay process, coordinated by primitives chosen per access pattern — locks, channels,
semaphores — rather than one lock protecting everything), an inline Mermaid diagram of the
per-connection task fan-out, Use cases (why an agent/developer needs this before touching
connection.rs or state.rs), a short Comparison table of the primitives actually in use (Semaphore
vs Mutex vs RwLock vs DashMap vs mpsc/watch — when each is reached for, cited to real call sites),
a Boundary section explicitly routing cancellation (#1116), graceful shutdown (#1118) and
background-worker startup ordering (#1115) to their own nodes, and Scope and omissions (including
what was expected but not independently verified, e.g. whether every concurrency primitive
repo-wide was surveyed versus this node's own buzz-relay-scoped sample).
        done when: the file exists at the target path, every claim in the evidence ledger is
        classified FACT/INFERENCE/TEAM_KNOWLEDGE per what was actually opened in Step 1, and every
        `templates/concept.md` required section is present (Definition non-optional; Background,
        visual aid, Comparison and Related-resources included only where they add real content).

STEP 3 — Validate  [needs 2]
Run `python3 launchpad/project-intelligence/corpus/validate.py` against the full tree; fix and
re-run until it prints `PASS` (pre-existing UNVERIFIED noise elsewhere is expected and not this
step's concern).
        done when: the command's output ends with `PASS`.

STEP 4 — Self-review  [needs 3]  ← RUNS HERE
Re-read the diff against issue #1117's Definition-of-Done checklist line by line (one canonical
document only; schema-valid front matter with stable id/type/status/origin/audiences/evidence;
one independently maintainable concept, with any second concept filed separately instead of
folded in; every substantive claim traceable and classified; links instead of duplicated content;
checked against the recorded provenance revision; validator clean; term defined in one sentence;
boundaries/non-goals stated; related concepts/implementation/verification linked; examples used
only to clarify, not to smuggle in a second concept); confirm `git show --stat HEAD` (once
committed in Step 5) shows only the corpus doc + plan file.
        done when: every DoD bullet is checked off against the actual file content, in writing, in
        the final report.

STEP 5 — Earn the stamp and commit  [needs 4]
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call, confirm `OK`, then commit (plan + node) with
`git commit -s` in a separate call. Do not push, do not open a PR.
        done when: the test run reports `OK` and `git log -1` on the worktree branch shows the new
        commit containing both the plan file and the corpus node.

PARALLEL: none of the five steps can run as independent subagents against each other — Step 1
feeds every claim Step 2 writes, Step 2's file is what Step 3 validates, Step 4 reviews Step 2's
actual diff, and Step 5's commit must follow a clean Step 3/4. This is a single-file,
single-worktree task with no independent sub-parts to fan out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must print `PASS` before commit.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
report `OK` before commit — this is the verify-gate stamp for this batch. `review-adjudicate` and
the cross-model final-review pass are explicitly deferred to the batch owner's later integration
step, not run in this session. `qa` explore mode does not apply — this is a documentation-only
change with no runtime interface to exercise.

BUDGET: Step 1 (reading connection.rs's full per-connection task-fan-out shape plus state.rs's
semaphore/DashMap declarations closely enough to cite line ranges honestly) is the step most
likely to eat the budget — the temptation is to paraphrase the file's own doc comments rather than
verify each cited behavior against the code.

OPEN: the issue's DoD does not say whether "concurrency" as a `layers/lifecycle` concept should be
scoped to `buzz-relay` alone or survey every crate's concurrency primitives (buzz-acp's `AgentPool`
uses `JoinSet` and its own locking, for instance). This plan scopes the node to `buzz-relay`'s
per-connection concurrency model as its primary, deeply-cited worked example — the same
single-actor depth choice sibling #1118 made for its relay-side sequence — and names the
not-independently-surveyed remainder (buzz-acp's own concurrency shape) as an explicit gap in
Scope and omissions rather than silently claiming repo-wide coverage.

LEFT OUT: no relationship to any other `layers/lifecycle/*` sibling node (background-workers
#1115, cancellation #1116, graceful-shutdown #1118, resource-cleanup #1119, startup #1120) —
those are drafted in unmerged sibling branches in this same batch run and are not present on
`origin/launchpad`, so per `AGENTS.md` step 9 they are not valid relationship targets yet; they are
instead named as prose boundary callouts in the node's own Boundary section. A full inventory of
`buzz-acp`'s own concurrency primitives (`AgentPool`, `JoinSet`) is out of scope for this node's
evidence ledger — named as a gap, not silently omitted.
