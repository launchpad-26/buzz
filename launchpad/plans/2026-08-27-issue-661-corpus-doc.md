# Plan: issue #661 — corpus doc `architecture/containers/web.md`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`;
`launchpad/docs/corpus/architecture/containers/web.md` does not exist yet.

STEP 1 — Gather evidence: read `web/package.json`, `web/src/**` (routes,
features/repos, features/invite, shared/lib), `crates/buzz-relay/src/router.rs`
and `config.rs` (how the relay serves the built bundle), `Dockerfile` (build +
runtime wiring), `Justfile` (`relay-web`, `web-build`, `web` targets),
`web/playwright.config.ts` and `web/tests/e2e/smoke.spec.ts`.

STEP 2 — RUNS HERE: write front matter (id
`architecture-containers-web`, type `architecture`, status `draft`, origin
`launchpad`, audiences `developer`+`agent`, evidence ledger citing only paths
actually opened in Step 1) and body covering: responsibility/technology/
ownership boundary, inbound/outbound interfaces and directly-connected
containers, deployment/data/security implications, links to implementation
paths (not duplicated detail), scope-and-omissions.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
must exit 0 against the full tree including the new file.

STEP 4 — Commit: run the corpus unittest suite as the sole command to earn the
verification stamp, then in a separate call stage and commit the plan file and
the new doc.

PARALLEL: none — single file, single writer.

GATES: `validate.py` only. `review-adjudicate` and the cross-model final-review
pass are deferred to the batch owner's morning review; not run in this
worktree.

BUDGET: single document, ~1-2 hours equivalent of read+write+validate. No code
changes, no test changes beyond the corpus's own suite (unmodified).

OPEN: the issue's DoD asks for "typed relationships appropriate to the node"
but also requires that any relationship target already exist as a loaded node.
No sibling `architecture/containers/*` node is merged on `origin/launchpad` at
this revision (the batch's other 4 in-flight issues are unmerged siblings), so
this node declares no `relationships`, consistent with the precedent set by
`corpus-readme` and `corpus-standard-confidence`. This is stated as fact in the
node's own scope-and-omissions section rather than silently omitted.

LEFT OUT: no per-type template exists for `architecture`/containers nodes
(0 of 26 merged per AGENTS.md); this node is written directly against
`node.schema.json` and expects a later reshape task, per AGENTS.md's own
instruction. No second canonical document is created. No runtime/product
behavior is changed.
