# Issue #681 — corpus doc: architecture/flows/live-fanout.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(commit a44cf52fc740ebebbdd671427480d14f0bce0115); the target file
`launchpad/docs/corpus/architecture/flows/live-fanout.md` does not exist.

STEP 1 — Gather evidence: read `crates/buzz-relay/src/handlers/event.rs`
(`handle_event`, `filter_fanout_by_access`, `fan_out_event_to_local_subscribers`,
`fan_out_pubsub_event`, `dispatch_persistent_event`/`_inner`), `subscription.rs`
(`fan_out_scoped`), `buzz-pubsub/src/publisher.rs` (`publish_event`), and
`main.rs`'s multi-node fan-out consumer task. RUNS HERE.

STEP 2 — Write front matter (id `architecture-flows-live-fanout`, type
architecture, status draft, origin launchpad, audiences developer/operator/agent,
evidence ledger) and the body: trigger/preconditions/termination, ordered
interactions and data movement, trust-boundary crossings, failure/abort/rollback
behavior with representative verification links. RUNS HERE.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
must exit 0. RUNS HERE.

STEP 4 — Commit the plan + document with `git commit -s`.

PARALLEL: none — single file, single worktree.

GATES: `validate.py` only. `review-adjudicate` and the cross-model review pass
are deferred to the batch owner's morning review of the PR, not run in this
session.

BUDGET: one document, one commit, one draft PR. No code changes.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node."
No other `architecture`/flow-typed corpus node is merged on `origin/launchpad`
as of this revision (`ls-tree` of `launchpad/docs/corpus` shows only
`AGENTS.md`, `README.md`, `schema/`, `standards/`), so there is nothing this
node can correctly point at yet. Per `AGENTS.md`'s relationship-target rule,
`relationships` is omitted rather than guessed at.

LEFT OUT: any second canonical document; any relationship edges; any code or
runtime behavior change; resolving how the `KIND_DM_VISIBILITY`/DM-fanout
architecture should evolve (out of scope per the issue).
