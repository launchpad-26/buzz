# Issue #680 — corpus doc: architecture/flows/huddle-audio.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
are merged on `origin/launchpad`; `launchpad/docs/corpus/architecture/flows/huddle-audio.md`
does not exist yet (confirmed via `test -f`, and `find launchpad/docs/corpus -name '*.md'`
lists only `README.md`, `AGENTS.md`, `standards/decision-references.md`,
`standards/confidence.md`).

STEP 1 (RUNS HERE): Gather evidence — read `crates/buzz-relay/src/audio/{handler,join,room,mesh,wire,mod}.rs`,
the huddle kind constants in `crates/buzz-core/src/kind.rs`, the route registration in
`crates/buzz-relay/src/router.rs`, and the Huddles/Buzz Mesh sections of `VISION.md`. Record
trigger/preconditions/interactions/auth crossings/failure paths as found in code, not assumed.

STEP 2 (RUNS HERE): Write `launchpad/docs/corpus/architecture/flows/huddle-audio.md` with
schema-valid front matter (`id: architecture-flows-huddle-audio`, `type: architecture`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer]`) and a body covering the
issue's DoD checklist plus the category tail (trigger/preconditions/termination, ordered
interactions, auth/authz crossings, failure/abort/rollback with verification links). No
`relationships` — no sibling flow/architecture node is merged on `origin/launchpad` to point at.

STEP 3 (RUNS HERE): Validate — `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0. Fix and re-run until clean.

STEP 4 (RUNS HERE): Commit (plan + doc together) after earning the verification stamp via the
corpus unittest suite, then push and open a draft PR closing #680.

PARALLEL: none — single document, single file, no fan-out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The commit
verification stamp is earned by `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
run as the sole prior command. `review-adjudicate` and the cross-model final-review pass are
explicitly deferred to the batch owner's morning review — not run in this session.

BUDGET: single session, no live model spend — this is a documentation-only task authored from
static source reading.

OPEN: The issue's own DoD does not resolve how deeply to describe the cross-pod mesh ownership
protocol (`buzz-relay-mesh` / Redis fenced CAS) versus treating it as a linked but separate
concern. This document describes the ownership *handshake as it affects the audio join/leave
flow* (resolve_join_owner_ready, generation fencing, teardown causes) because those are
observable state transitions in the flow itself, but does not attempt to document the mesh
crate's internals — that boundary is asserted here, not settled by the issue.

LEFT OUT: No `relationships` edges (no sibling corpus node exists to target). No new
architecture/container/component node for `buzz-relay-mesh` itself — out of scope per the
issue's "second canonical document" restriction. No live/manual testing of a huddle session —
evidence is drawn from source and existing unit tests only, and the doc says so.
