# Issue #935 — implementation/crates/buzz-relay-mesh.md

Stated size: single hand-authored corpus document (child of Feature #615)  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/schema/relationships.schema.json` are merged on `origin/launchpad`.
`launchpad/docs/corpus/implementation/crates/buzz-relay-mesh.md` does not exist yet (confirmed
via `ls`). The crate `crates/buzz-relay-mesh` exists at HEAD `76a0a4ebbe4bc4d852b0d04362ed768620da34b3`
(9 source files, 3139 lines, no crate-local README). `crates/buzz-relay/src/mesh_boot.rs` is the
sole consumer wiring the crate into the running relay. Two corpus nodes already document the
mesh from the architecture surface — `architecture-deployment-multi-relay` and
`architecture-containers-relay` — both already merged and both citing `crates/buzz-relay-mesh/**`
directly; neither is an `implementation`-typed node, so neither is a candidate `implements`
target, but both are legitimate `references` targets since this node covers ground they already
describe at a coarser grain and should not re-derive.

STEP 1  [independent]  Gather evidence: read every module in `crates/buzz-relay-mesh/src/` (`lib.rs`, `endpoint.rs`,
peer.rs`, `registry.rs`, `gossip.rs`, `membership.rs`, `runtime.rs`, `status.rs`, `wire.rs`) for
public types/traits/fns, the two consumer seams (`RelayMeshMembership`, `RelayPeerTransport`), the
error taxonomy, and every `#[test]`/`#[tokio::test]` name per file. Read `crates/buzz-relay/src/mesh_boot.rs`
(`boot_mesh`, `MeshHandle`, `MeshInboundDispatcher`) and `crates/buzz-relay/src/config.rs` (`BUZZ_MESH`,
`BUZZ_MESH_BIND_ADDR` resolution) to confirm the ownership boundary: the crate owns transport/membership/wire,
the relay owns session-directory fencing (`crates/buzz-relay/src/tunnel/directory.rs`), tunnel routing, and
huddle audio fan-out (`crates/buzz-relay/src/audio/mesh.rs`) — confirmed by both crates' own module docs
naming that split explicitly. Record `git rev-parse HEAD`. ← RUNS HERE
done when: every module has been opened and its test function names listed; `boot_mesh`'s signature and
`MeshHandle`'s fields have been read; the ownership-boundary claim is backed by an opened line in each of
`crates/buzz-relay/src/tunnel/directory.rs` and `crates/buzz-relay/src/audio/mesh.rs`, not inferred from
`lib.rs`'s comment alone.

STEP 2  [needs 1] Write the front matter (id `implementation-crates-buzz-relay-mesh`, type `implementation`,
status `draft`, origin `launchpad`, audiences `[agent, developer, operator, reviewer]`, one evidence entry
per substantive claim classified FACT/INFERENCE/TEAM_KNOWLEDGE per `AGENTS.md`'s rules, `relationships: [{type:
references, target: architecture-deployment-multi-relay}, {type: references, target: architecture-containers-relay}]`)
and the body, following the template skeleton exactly: Realization statement, Target, Implementation surface
(table of module/symbol -> responsibility, each row citing an opened file), Divergences, Verification (naming
the test files/functions from STEP 1), Relationships, Scope and omissions (stating what the crate deliberately
does not own, per STEP 1's boundary evidence, plus anything expected but not verified — e.g., no live multi-pod
mesh run was exercised, only static code/test reading).
done when: the file exists at the target path with schema-required front-matter fields present and every DoD
bullet from issue #935 addressed in the body.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root; fix any
FAIL entries naming this node and re-run until either it exits 0 or the only remaining FAILs are the
pre-existing ~21 unrelated ones already on `origin/launchpad` (confirm via `git stash`/diff, not assumption).
done when: the validator run's output contains zero FAIL lines whose node id is `implementation-crates-buzz-relay-mesh`.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call to earn the commit-gate stamp; confirm `OK`. Then, in a separate call,
`git add` the plan and the new corpus doc and `git commit -s` with a `docs(corpus):` message referencing #935.
done when: the unittest run prints `OK` and `git log -1` shows the new commit containing exactly the two added files.

PARALLEL: none — one file, one task, no independent sub-work to farm out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 for this node (STEP 3).
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
before commit (STEP 4). `review-adjudicate` and cross-model final review are deferred to the batch's later
integration-PR review pass, per the dispatch brief — not run in this session.

BUDGET: small-to-medium — one crate (9 files, ~3100 lines, no README) to read closely, two already-merged
architecture nodes to cite for `references`, no code changes, no new relationship types to invent.

OPEN: Whether either `architecture-deployment-multi-relay` or `architecture-containers-relay` should instead
be `part-of` targets (this node's crate as a "constituent" of their broader topology) rather than `references`
is a judgment call this plan resolves as `references`: `part-of`'s schema directionality is "source is a
constituent section/child of target," which fits a sub-document of a larger *document*, not an independent
implementation-reference node describing code those architecture nodes already discuss from a different
angle. A future implementation-reference node for a sibling mesh-adjacent crate is a better moment to revisit
if that reading turns out wrong.

LEFT OUT: No `implements` edge — no ADR or NIP in this repository specifies the mesh wire contract or
protocol as its own corpus-eligible target (checked: `launchpad/decisions/*.md` and `docs/nips/*.md` both
grep clean for genuine mesh-protocol matches), so per the template's own guidance ("declare no `implements`
edge... an edge to a nonexistent id is a hard validation error") none is declared. No second corpus document —
if evidence surfaces a genuinely separate concept (e.g. the fencing law as its own invariant node) it is filed
as a new task, not folded in here. No attempt to fix or annotate the `MeshConfig.enabled` doc-comment vs.
`config.rs` default-off discrepancy noticed in passing — that is implementation, not corpus-authoring, work.
