# Issue #692 — corpus doc: architecture/principles/host-selects-community.md

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
`launchpad` at a44cf52f; `launchpad/docs/corpus/architecture/principles/host-selects-community.md`
does not exist yet (confirmed with `test -f`).

STEP 1 — Gather evidence. Read `crates/buzz-relay/src/tenant.rs`,
`crates/buzz-core/src/tenant.rs`, `docs/multi-tenant-conformance.md`,
`migrations/0001_initial_schema.sql` (communities table), `crates/buzz-relay/src/router.rs`
(WS-upgrade bind site), and the NIP-42 cross-host test
(`crates/buzz-test-client/tests/nip42_host_binding_live.rs`) to ground every claim in
real source. RUNS HERE.

STEP 2 — Write front matter (id `architecture-principles-host-selects-community`,
type `architecture`, status `draft`, origin `launchpad`) and a body stating the
row-zero invariant as one MUST, its scope/operations, enforcement points, observable
failure behavior, and verification links, satisfying the issue DoD plus the
principles-category tail.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until it exits 0 against the full tree including the new file.

STEP 4 — Commit (after earning the verification stamp via the unittest suite) and
open a draft PR against `launchpad`.

PARALLEL: none — single file, single task, no fan-out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
review-adjudicate and any cross-model final-review pass are explicitly deferred to
the batch owner's morning review of all 47 issues in #608 — not run in this task.

BUDGET: single document, ~1-2 hours of agent time; no code changes, no test-suite
changes beyond the corpus validator/unittest run already required by the workflow.

OPEN: the issue's own DoD asks for "typed relationships appropriate to the node," but
no other architecture/principles node is merged yet at this revision, so any
`relationships[].target` would name an id no loaded node carries — a hard validation
error per node.schema.json. This document ships with no `relationships` array,
matching the precedent in `standards/confidence.md`. Also open: the source docstring
in `crates/buzz-relay/src/tenant.rs` asserts a "migration-lint harness" forbids
constructing `TenantContext` outside host resolution and tests; no such script was
found under that name in this checkout, so the document records this as unverified
rather than asserting it exists.

LEFT OUT: no second canonical document; no changes to `crates/`, `docs/`, or
`migrations/`; no promotion to `status: active`; no resolution of the
"migration-lint harness" ambiguity above (recorded as a gap, not resolved).
