# Issue #923 — corpus node: implementation/crates/buzz-conformance.md

Stated size: issue #923 carries no explicit Size line; the dispatching batch-author task caps this document at 5 steps -> cap: 5 steps.

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, and `launchpad/docs/corpus/templates/implementation-reference.md`
are merged on `origin/launchpad`. `launchpad/docs/corpus/architecture/flows/event-ingestion.md`
(id `architecture-flows-event-ingestion`) and
`launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md` (id
`architecture-principles-community-is-security-boundary`) already document the conformance
tracer's wiring and the multi-tenant invariant it checks, citing
`crates/buzz-relay/src/conformance/mod.rs` and `docs/multi-tenant-conformance.md`. No
`implementation/` subtree exists yet in the corpus — this is the first node under it. The target
file does not exist (confirmed via `ls`). All evidence gathering below (Cargo.toml, src/lib.rs,
src/checker.rs, src/transitions.rs, LIMITS.md, TRACE_SCHEMA.md, tests/, git log, the buzz-relay
emitter side, Justfile CI wiring, and the .tla spec) was already completed in this session before
this plan was written. <- RUNS HERE

STEP 1 [independent] — Write front matter: id `implementation-crates-buzz-conformance`, `type:
verification` (the crate's whole reason for being is an independent conformance/replay checker
against a formal spec, not product behavior — the template's "note on type" permits a
non-`implementation` surface when the realizing artifact's own nature calls for it), `status:
draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, one `evidence` entry per
substantive claim (FACT for everything opened directly, including the independence-rule comment,
the 3 fixture verdicts, the LIMITS.md scope gaps, and the Justfile CI wiring), plus a provenance
commit citation. `relationships`: `references` toward `architecture-flows-event-ingestion`
(documents the same `EmitGuard`/tracer wiring this crate's checker consumes) and toward
`architecture-principles-community-is-security-boundary` (documents the same multi-tenant
invariant this crate checks) — both verified to exist and resolve on `origin/launchpad`. No
`implements` edge: the spec target (`docs/spec/MultiTenantRelay.tla`) has no corpus node id.
done when: the front matter block is written and both cited relationship targets are confirmed
present in `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`.

STEP 2 [needs 1] — Write the body against the template's required sections: Realization statement,
Target (the .tla spec file + line-range grounding, stated as a non-corpus-node path),
Implementation surface (table: `lib.rs` schema types, `checker.rs::check_trace`,
`transitions.rs::check_step`, mapped to what spec obligation each realizes), Divergences
(LIMITS.md's own named gaps: read-seam not yet armed, cross-pod leaks out of scope,
execution-coverage-only, no proof), Verification (the 3-surface CI command from LIMITS.md — 9+5+2
tests — cited exactly), Relationships, Scope and omissions (states responsibility: schema +
independent checker; NOT: production reducer, DB policy, the emitter itself which lives in
buzz-relay, cross-pod attacks, timing properties). done when: all 7 required sections from
`templates/implementation-reference.md` are present in the file, each substantive claim in the
body has a matching `evidence` entry.

STEP 3 [needs 2] — Run `python3 launchpad/project-intelligence/corpus/validate.py` against the
full tree; fix and re-run until exit 0. If nonzero, diff against a `git stash`d baseline on
`origin/launchpad` to confirm any residual failures are the pre-existing ~21, not new ones from
this node. done when: the command exits 0, or exits nonzero with only the pre-existing baseline
failures confirmed by diff (none naming this node's file).

STEP 4 [needs 3] — Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own tool call; confirm `OK`. done when: the suite
reports `OK` with zero failures/errors.

STEP 5 [needs 4] — In a separate tool call, `git add` the node file and this plan, then `git commit
-s` with the prescribed message. Do not push, do not open a PR (batch integration happens in a
later phase). done when: `git log -1` shows the new commit containing exactly the node file and
this plan, and `git status` shows a clean tree.

PARALLEL: none — single file, single worktree, no dependency on sibling batch documents.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (or show only the
pre-existing baseline failures, verified by diff). `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK` before commit.
`review-adjudicate` and cross-model final review are explicitly deferred to the batch owner's
later integration phase — not run in this session; a careful self-review substitutes if
`corpus-review` is unreachable.

BUDGET: single document, one sitting — no multi-hour scope expected.

OPEN: whether `type: verification` or `type: implementation` is the better fit is a judgment call
the issue explicitly defers to this session ("weigh both... pick whichever the crate's actual
nature calls for"); `verification` is chosen and the reasoning is recorded in the node's evidence
ledger rather than silently picked.

LEFT OUT: no `implements` edge (the .tla spec target has no corpus node id yet — inventing one
would be a hard validation error per `AGENTS.md` step 9). No edit to
`architecture-containers-relay.md`, `architecture-flows-event-ingestion.md`, or
`architecture-principles-community-is-security-boundary.md` to add inbound edges back to this new
node — out of scope per issue #923's "Out of scope: Broad 'while here' documentation cleanup" and
"Creating or materially editing a second hand-authored canonical corpus document." No attempt to
stand up the ignored `crates/buzz-test-client/tests/conformance_multitenant.rs` A/B suite or the
held-back req.rs read-seam patch — both are named as known gaps, not resolved here.
