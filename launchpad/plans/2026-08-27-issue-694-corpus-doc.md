# Issue #694 — corpus doc: architecture/principles/nostr-first.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad` (confirmed via `git ls-tree origin/launchpad`); `launchpad/docs/corpus/architecture/principles/nostr-first.md` does not exist yet (confirmed via `test -f`).

STEP 1 — Gather evidence for the nostr-first invariant: read `AGENTS.md`'s "Nostr-first HTTP surface" / "Prefer Nostr events over new HTTP endpoints" notes, `CONTRIBUTING.md`'s "How to Add a New Event Kind" / "How to Add a New API Endpoint" sections, `crates/buzz-relay/src/router.rs`'s `build_router()` for the real route list, and `ARCHITECTURE.md`'s HTTP endpoints table (found to have drifted from `router.rs`, which is itself evidence about verification). Check for any automated enforcement (test, lint, CI) — none found.

STEP 2 (RUNS HERE) — Write the node's front matter (id `architecture-principles-nostr-first`, type `architecture`, status `draft`, origin `launchpad`) and body: the invariant as one MUST/MUST NOT statement, scope, enforcement points, observable failure behavior, and an explicit statement that no automated verification mechanism exists today. No `relationships` — no other `architecture-*` node is merged on `origin/launchpad` yet, so there is nothing to point at.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0, then run the corpus unittest suite to earn the commit verification stamp.

STEP 4 — Commit the plan + document together, push, open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK (this is what earns the commit hook's verification stamp for a fresh worktree this session). `review-adjudicate` and the cross-model final review pass are explicitly **not** run here — deferred to the batch owner's morning review per the task brief.

BUDGET: single document, no code changes, no test/build changes. Expect ~10 tool calls total for evidence gathering plus the write/validate/commit/PR sequence.

OPEN: the issue's DoD asks for "enforcement points and observable failure behavior" — the honest answer found is that enforcement is **human-only** (CONTRIBUTING.md guidance + PR review); no test, lint, or CI check bounds the relay's route list, and ARCHITECTURE.md's own HTTP-endpoints table has already drifted out of sync with `router.rs`. This is recorded as a real gap in the node rather than resolved by inventing a mechanism that doesn't exist.

LEFT OUT: NIP-98 auth mechanics, the admin API's separate mount/config-gating rationale, and any future automated HTTP-surface conformance check — all out of scope for this single-node task per the issue's own "Out of scope" section.
