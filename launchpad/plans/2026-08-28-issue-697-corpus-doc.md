# Issue #697: docs(corpus) — architecture/principles/signed-events.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(`a44cf52fc740ebebbdd671427480d14f0bce0115`); the target file
`launchpad/docs/corpus/architecture/principles/signed-events.md` does not exist yet.

STEP 1 — gather evidence: read `buzz-core/src/verification.rs`, `buzz-core/src/event.rs`,
`buzz-core/src/error.rs`, and the three call sites in `buzz-relay/src/handlers/event.rs`
and `buzz-relay/src/handlers/ingest.rs` that enforce it (WS ephemeral, WS agent-observer,
shared WS/HTTP persistent-event seam). Confirm which parts have unit-test coverage and
which do not (grep for `InvalidSignature`/`invalid event id` across `crates/`).

STEP 2 — write front matter (id `architecture-principles-signed-events`, type
`architecture`, status `draft`, origin `launchpad`) and body: the MUST/MUST NOT
statement, scope (states/operations it applies to and does not), the three enforcement
points with observable failure behavior (NIP-01 `OK false` message shape), and links to
verification (the three unit tests) plus the explicit gap that no E2E/integration test
exercises rejection through the wire protocol. RUNS HERE.

STEP 3 — validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0 against the full corpus tree including the new file.

STEP 4 — commit: run the corpus unittest suite as the sole prior command to earn the
verification stamp, then in a separate call stage and commit the plan file and the new
document with `git commit -s`.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must report OK to earn the commit hook's verification stamp. review-adjudicate and the
cross-model review pass are deferred to the batch owner's morning review — not run here.

BUDGET: single document, ~1-2 hours of agent time; no code changes, no test changes.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but no
other `principles`/architecture-category sibling node is merged yet at this revision, so
there is no existing id this node could safely target — `relationships[].target` naming
an id no loaded node carries is a hard schema-validation error per the REPO FACTS. This
node ships with no `relationships` entries, matching the precedent in
`launchpad/docs/corpus/standards/confidence.md`. Also open: the `StoredEvent.verified`
field exists but has zero non-test call sites in the current tree (grepped), so it is not
part of this invariant's enforcement — recorded as a scope note, not resolved.

LEFT OUT: no runtime/product code change; no second canonical document; no
`relationships` edges (see OPEN); no per-type template (none exists yet, per
`launchpad/docs/corpus/AGENTS.md`); no E2E/integration-level test added — the coverage
gap is recorded in the document, not closed.
