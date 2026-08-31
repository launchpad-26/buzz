# Issue #690 — corpus node: architecture/principles/event-driven-extension.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; the target file
`launchpad/docs/corpus/architecture/principles/event-driven-extension.md` does not
exist yet.

STEP 1 — Gather evidence: read root `AGENTS.md` §Key Patterns ("Prefer Nostr events
over new HTTP endpoints"), `CONTRIBUTING.md` §"How to Add a New Event Kind" / §"How
to Add a New API Endpoint" / §Architecture Overview, `crates/buzz-core/src/kind.rs`
(registry + `ALL_KINDS` + `no_duplicate_kind_values` test), `crates/buzz-relay/src/router.rs`
(actual HTTP route set, to check it against the documented "narrow surface" claim),
and `crates/buzz-relay/src/handlers/event.rs` (automatic audit enqueue on the generic
event-storage path) plus a check of `api/invites.rs` / `api/operator.rs` for whether
those bespoke endpoints call the audit service themselves. RUNS HERE.

STEP 2 — Write front matter (id `architecture-principles-event-driven-extension`,
type `architecture`, status `draft`, origin `launchpad`, audiences `[developer,
agent, reviewer]`, no `relationships` — no other node in the merged corpus is a
relevant target) and the body: the MUST/MUST-NOT statement, scope, enforcement
points and observed failure/drift, and verification status. RUNS HERE.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py` against the
full tree; fix and re-run until exit 0. RUNS HERE.

STEP 4 — Run the corpus unittest suite as the sole prior command, then commit (plan +
node) in a separate call, push, and open a draft PR. RUNS HERE.

PARALLEL: none — single file, single worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK before commit. `review-adjudicate` and the cross-model
final-review pass are explicitly deferred to the batch owner's morning review — not
run in this session.

BUDGET: single document, one sitting — no multi-hour scope expected.

OPEN: the issue's DoD does not say whether "event-driven extension" is scoped to the
relay's *write*/ingest surface only, or also to how clients *discover* new
capabilities (event kinds are additive and backward compatible for readers too). The
node states both, since both are directly evidenced by the same sources, but the
issue itself does not disambiguate which was intended — recorded here rather than
silently narrowed.

LEFT OUT: no `relationships` edges (no sibling corpus node exists yet to target — the
architecture/ subtree is empty at HEAD); no attempt to reconcile the drift found
between the documented "narrow HTTP surface" and the actual broader route table in
`router.rs` — that drift is recorded as an observed fact in the node's body, not
resolved by this task, per the issue's "Out of scope: Broad 'while here' documentation
cleanup."
