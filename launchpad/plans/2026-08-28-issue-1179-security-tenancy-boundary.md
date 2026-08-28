# Plan: issue #1179 — document layers/security/tenancy-boundary.md

## ALREADY TRUE

- `launchpad/docs/corpus/layers/security/tenancy-boundary.md` does not exist on disk or on `origin/launchpad` (confirmed by `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists no `layers/` subtree at all yet).
- Three merged, `type: architecture` sibling nodes already document the *mechanism* of this boundary in depth: `architecture-principles-community-is-security-boundary`, `architecture-principles-fail-closed-boundaries`, `architecture-principles-host-selects-community`. This task's own dispatch note (issue body) says this node is the *security-taxonomy* framing (what's at risk if the boundary fails, what it must guarantee), distinct from the mechanism framing those three own, and distinct from `layers/tenancy/cross-community-isolation.md` (#1188, not yet drafted).
- `launchpad/docs/corpus/templates/invariant.md` is merged and is the closest-fitting template (the issue's DoD tail — invariant as one property, scope, enforcement points, observable failure behavior, verification-or-gap — matches its required sections almost verbatim).
- `docs/multi-tenant-relay.md` + `docs/spec/MultiTenantRelay.tla` + `docs/spec/MultiTenantAuth.spthy` are real, already-in-repo formal artifacts (non-interference theorem, isolation invariants I1–I5, authorization-soundness lemmas S1–S8) with both machine-checked (TLC exhaustive, Tamarin 32/32 green) — genuinely new evidence not cited by the three mechanism nodes.
- `crates/buzz-test-client/tests/conformance_multitenant.rs` independently verified: 18 `#[tokio::test]` functions, 8 stubbed via `pending_lane(...)` (`todo!()`), and no `.github/workflows/` or `Justfile` reference to `conformance_multitenant` — a real, honest verification gap for the runtime A/B suite.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/layers/security/tenancy-boundary.md` against the invariant
template's shape (lead invariant statement, Scope, a security-guarantee section stating
non-interference + authorization soundness, a threat/consequence section, Enforcement
today across three tiers — code, formal proof, runtime-conformance gap — Boundary,
Relationships, Scope and omissions). `type: layers`, `id: layers-security-tenancy-boundary`,
`status: draft`, `origin: launchpad`, per the dispatch instructions. Declare
`depends-on` to the two most directly load-bearing sibling mechanism nodes
(`architecture-principles-community-is-security-boundary`,
`architecture-principles-host-selects-community`) and `references` to
`architecture-principles-fail-closed-boundaries` (the general pattern this is one
instance of). Every FACT opened directly this session; no restating of the three
sibling nodes' own enumerated call-site tables (link instead, per the linking
standard's no-duplication rule).

Done-when: file exists, front matter is schema-shaped, every DoD bullet in #1179 has
a corresponding section.

## STEP 2 — Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py` (exit 0) and
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` (OK), each as its own command.

Done-when: both commands report success with no manual edits to either script.

## STEP 3 — Self-review against the issue and re-open every cited source

Re-read the diff against every DoD checklist line in #1179, re-open every FACT
citation to confirm it says what the statement claims, confirm no second
hand-authored canonical document was created, and re-run `validate.py` once more
after any fix.

Done-when: every DoD bullet is satisfied and every FACT was re-opened this session.

## STEP 4 — Commit and open the draft PR

Commit with `-s`, push, open a **draft** PR against `launchpad` stating
`Closes #1179`, that validation and the unittest suite both passed, that this was
self-review only (no `review-code` skill), and that adjudication/cross-model review
is deferred to the batch owner.

Done-when: PR is open as a draft with that body.

## GATES

- `validate.py` exit 0 before commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK` before commit.
- Every `relationships[].target` re-checked against `origin/launchpad` immediately before finalizing front matter (not trusted from this plan's earlier snapshot).

## OPEN

- Whether `docs/multi-tenant-relay.md`'s own "Implementation Correspondence" section (which states, in its own text, "today there is no community layer") has ever been reconciled against the current `tenant.rs` implementation the three sibling architecture nodes cite as already-shipped. Not resolved here — recorded as a scope gap in the node itself.
- Full residual-risk enumeration beyond the conformance-suite gap already independently verified here belongs to #1174 (open PR #1826, unmerged — not linkable and not trusted as a source, re-verified independently instead).

## LEFT OUT

- Full per-surface obligation table (`docs/multi-tenant-conformance.md`) — already owned and linked by the sibling architecture nodes; not reproduced here.
- Any relationship to `layers-security-residual-risks` or a `layers-tenancy-*` id — neither exists on `origin/launchpad` yet.
- Re-running the TLA+/Tamarin toolchains or the live two-host conformance suite — reading and citing their existing, already-recorded results only.
