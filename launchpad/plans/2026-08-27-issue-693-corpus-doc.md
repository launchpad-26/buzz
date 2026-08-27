# Issue #693 — document architecture/principles/humans-and-agents-are-peers.md

ALREADY TRUE: `node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on
`origin/launchpad` (confirmed at `a44cf52fc740ebebbdd671427480d14f0bce0115`), and
`launchpad/docs/corpus/architecture/principles/humans-and-agents-are-peers.md` does not
yet exist (confirmed by `test -f`, and no `architecture/principles/` directory exists
yet in the corpus tree).

STEP 1 — Gather evidence for the invariant from source: `VISION.md`'s Identity section,
`IngestAuth`/`required_scope_for_kind`/`author_type_label` in
`crates/buzz-relay/src/handlers/ingest.rs`, `MemberRole` in
`crates/buzz-core/src/channel.rs`, `Scope` in `crates/buzz-auth/src/scope.rs`, the
Bot-promotion carve-out in `crates/buzz-relay/src/api/git/policy.rs`, and
`buzz-acp`'s NIP-42 WebSocket auth. RUNS HERE.

STEP 2 — Write front matter (id
`architecture-principles-humans-and-agents-are-peers`, type `architecture`, status
`draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, no
`relationships` — no sibling `architecture/principles/*` node exists yet on
`origin/launchpad` to point at) and the body: state the invariant with MUST/MUST NOT,
scope (identity, auth, event-kind authorization, channel membership/role, explicitly
naming the Bot-designation carve-out), enforcement points and observable failure
behavior, and link verification.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 4 — Earn the verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit plan + node in a separate call.

PARALLEL: none — one file, one worktree.

GATES: `validate.py` must exit 0 locally; the unittest suite above must report OK to
earn the commit stamp. `review-adjudicate` and the cross-model review pass are
deferred to the batch owner's morning review — not run in this session.

BUDGET: single-session, single-document task — no sub-agents, no multi-step build.

OPEN: the issue's DoD does not say whether "verification/conformance mechanism" means
an automated test asserting the invariant, or documentation of the enforcement code
path plus its own test coverage. No dedicated automated test exists that asserts
"humans and agents get identical scopes/kind-authorization" as a standalone
proposition — the node records this as verification-by-code-reading plus the existing
unit/e2e tests of the underlying mechanisms (`Scope`, `required_scope_for_kind`,
`MemberRole`), not a dedicated peer-parity test. This is left explicit in the node's
own body rather than resolved by inventing a claim.

LEFT OUT: no second corpus document; no new automated test; no promotion to
`status: active`; no resolution of `#1321`'s provenance-update policy (irrelevant
here — this is a new node, not an update).
