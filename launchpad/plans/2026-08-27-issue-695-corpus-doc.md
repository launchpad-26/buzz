# Plan: issue #695 — corpus node `relay-is-source-of-truth`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; no `architecture/`
subtree exists yet under `launchpad/docs/corpus/` and
`launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md` does not
exist.

STEP 1 — Gather evidence. Read `ARCHITECTURE.md`, `CONTRIBUTING.md`, `README.md`,
`VISION.md`, `docs/nips/NIP-PL.md`, `crates/buzz-relay/src/tenant.rs`, and the
`Cargo.toml` of `buzz-relay`/`buzz-workflow`/`buzz-pubsub`/`buzz-search`/`buzz-audit`/
`buzz-media`/`desktop/src-tauri` for the invariant's statement, scope, enforcement
points and observable failure behavior. RUNS HERE.

STEP 2 — Write front matter (id `architecture-principles-relay-is-source-of-truth`,
type `architecture`, status `draft`, origin `launchpad`, no `relationships` — no sibling
node id exists yet in the merged corpus to target) and the body: one MUST-level
invariant statement, scope, enforcement points, observable failure behavior, and a
verification-mechanism section that is honest about what is and is not automated.
RUNS HERE.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0. RUNS HERE.

STEP 4 — Commit (plan + node together) and open a draft PR against `launchpad`.
RUNS HERE.

PARALLEL: none — single file, single worktree, no fan-out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
commit. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` is run once, alone, to earn the commit verification stamp. Adjudication and
any cross-model review pass are explicitly deferred to the batch owner's morning review —
not run in this session.

BUDGET: one file, one commit, one draft PR. No code changes, no generated-index
regeneration expected (none exist yet to regenerate).

OPEN: the repository has **no automated check** that the "subsystems don't call each
other directly" half of this invariant holds beyond the crate dependency graph itself
(confirmed via each subsystem crate's `Cargo.toml`) — `deny.toml`'s `[bans]` section
governs duplicate external crate versions, not internal import boundaries. The document
records this as a verification gap rather than inventing a check. This is a real
ambiguity in the DoD's "verification/conformance mechanism" bullet, not something this
plan resolves.

LEFT OUT: no `relationships` entries (no other corpus node exists yet to target — the
same situation `AGENTS.md` itself records and the same reasoning applies here);
per-type template application (none merged, per `AGENTS.md`); any change to
`docs/nips/*`, `ARCHITECTURE.md`, or code — this task documents the existing invariant,
it does not modify it.
