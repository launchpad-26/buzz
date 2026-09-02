# Issue #648 — agents/evidence-resolution.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/evidence.md`,
`launchpad/docs/corpus/agents/invariants.md` and `launchpad/docs/corpus/templates/procedure.md`
(id `corpus-template-procedure`) are all present and merged on `origin/launchpad` at HEAD
`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (confirmed via `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus`). `launchpad/docs/corpus/agents/evidence-resolution.md`
does not exist yet on this branch or on `origin/launchpad`. Sibling task #643
(`agents/conflicting-evidence.md`) is drafted locally on branch `task/643-agents-conflicting-evidence`
(commits `0a95ed834`, `52b8c567b`) but is unmerged, so it is read for boundary-drawing only and is
not a valid `relationships` target.

STEP 1  Confirm shape: read issue #648's DoD (how-to-shaped: goal/prerequisites/scope, ordered
executable steps, success verification, links authoritative commands) against
`templates/procedure.md`'s required sections (Overview, optional Before you start, one numbered
task sequence per logical goal, See also, Boundary, Relationships, Scope and omissions) — confirmed
matching template, not `templates/policy.md` or `templates/reference.md`. ← RUNS HERE

STEP 2  [needs 1] Draft front matter: id `agents-evidence-resolution`, type `agent` (this node's
subject — an agent's own evidence-classification/citation behavior while authoring — is the same
corpus surface `AGENTS.md` and `agents-invariants` both use `type: agent` for), status `draft`,
origin `launchpad`, audiences `[agent, reviewer]` (matching `agents-invariants` and
`agents-conflicting-evidence`'s own author-selected audience choice for the same document family).
Relationships: `depends-on: corpus-agents`, `references: corpus-standard-evidence`,
`references: agents-invariants`, `implements: corpus-template-procedure` — all four confirmed
present on `origin/launchpad`; no edge to `agents-conflicting-evidence` (unmerged) or any other
sibling.

STEP 3  [needs 2] Write the body as a how-to: Overview (the moment-of-authoring procedure from
candidate claim to correctly-classified, correctly-cited evidence entry); numbered task sequence
covering recognize claim type → identify best source → classify honestly (open before FACT) →
cite in one of the six `CONTRACT.md` §3 shapes plus the two URL forms `AGENTS.md`'s table adds →
recognize the UNVERIFIED trap and decide when a citation alone is not enough; See also; explicit
Boundary excluding conflicting-evidence's cross-source-disagreement subject (named as #643's
subject, not linked as a relationship since unmerged) and excluding `standards/evidence.md`'s own
MUST/SHOULD rules (link, do not restate); Relationships section; Scope and omissions naming what
was expected but not verified (no CI run, no node yet exercising a real classification decision
end-to-end).

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root; fix and re-run until exit 0.

STEP 5  [needs 4] Run the corpus unittest suite (`python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole command in its own tool
call to earn the verification stamp; confirm `OK`; then commit in a separate call. No push, no PR
— this branch stays local per the batch's integration step.

PARALLEL: none — single file, single task, no dependency on another in-flight sibling's merge.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The unittest
discover command above must print `OK` before the commit is made — this is the local commit gate,
not a substitute for `review-adjudicate` or cross-model final review, both deferred to the batch
owner's integration pass.

BUDGET: small — one document, no code changes; evidence gathering scoped to `AGENTS.md`,
`standards/evidence.md`, `templates/procedure.md`, `agents/invariants.md`, and reading (not citing)
the unmerged `#643` sibling for boundary language.

OPEN: `check-plan.sh` does not exist anywhere in this repository (confirmed in an earlier corpus
batch and re-checked here with `find . -iname 'check-plan*'` returning nothing) — proceeding
without it, as instructed. Whether a future merged `agents/*.md` or `ingestion/*.md` sibling will
declare a relationship toward this node is that sibling's own edit to make, not decided here.

LEFT OUT: No relationship edge to `agents-conflicting-evidence` (#643) — real content, but unmerged
at authoring time, so declaring the edge now would validate locally and hard-fail once merged
before #643 lands, per `AGENTS.md` step 9's own warning. No restatement of `standards/evidence.md`'s
MUST/SHOULD rules, the six-plus-two citation-shape table's full verdict semantics, or ADR-0029's
precedence rule — this node links to each rather than duplicating. No treatment of what to do when
two sources *disagree* — that is #643's subject, named explicitly in this node's Boundary section
rather than re-derived.
