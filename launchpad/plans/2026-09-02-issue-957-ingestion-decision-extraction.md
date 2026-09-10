# Issue #957 — ingestion/decision-extraction.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md`, `templates/procedure.md` (id
`corpus-template-procedure`), `standards/decision-references.md` (id
`corpus-standard-decision-references`), and `agents/invariants.md` (id
`agents-invariants`) are merged on `origin/launchpad`. No `ingestion/` directory
exists yet — this is the second node in that family after local-only, unmerged
`ingestion/concept-extraction.md` (#955, worktree
`task-955-ingestion-concept-extraction`, NOT a valid relationship target).
`node.schema.json`'s `type` enum includes `ingestion`. `standards/decision-references.md`
already governs HOW to cite a decision once found; this node is the earlier
noticing step, parallel to how #955 is the noticing step #642 (concept-resolution,
also unmerged) dedups against.

STEP 1  Gather one real, verifiable worked example per decision-bearing source shape
named in the task brief, distinguishing an actual settled decision from a mere
proposal or open discussion. ← RUNS HERE
  - ADR-file signal: confirm via `grep -r "^status:" launchpad/decisions/*.md` that
    `status` takes exactly `Accepted`, `Proposed`, or `Superseded by ADR-YYYY`.
    `ADR-0034-knowledge-contract-owned-by-decision-layer.md` has a `Decision` heading
    AND is `Proposed` — its own body says "Not yet settled by a human" — proving a
    `Decision` section's presence alone does not make it extractable; `status` is the
    gate.
  - Ratified-spec signal: `launchpad/project-intelligence/CONTRACT.md:3` reads
    "Status: proposed, not ratified"; `standards/decision-references.md`'s own Scope
    and omissions names "How a specification becomes 'ratified'" as "Undefined in
    this repository." No ratified spec exists to point at today — the worked example
    is the documented absence, not a fabricated instance.
  - Settled-issue-thread signal: `gh issue view 307 --repo launchpad-26/buzz` — the
    templated "Decision outcome" section in the issue body stayed **blank**
    permanently even after settling; the actual decision is a later comment
    ("Human decision recorded — 2026-08-31", quoting Jeffrey's literal reply "a"),
    confirmed only by the merged `ADR-0043-prefer-fork-owned-overrides.md` naming
    `issue: launchpad-26/buzz#307` and `status: Accepted`. The issue stayed **open**
    after the decision comment, pending the batched ADR PR.
  - PRD-document signal: Feature #620's own acceptance criteria contain the phrase
    "explicitly removed from scope by an approved PRD change" — identical boilerplate
    across all 14 sibling corpus Features (`gh search issues`), so no single real,
    already-executed instance of an approved PRD scope change was found to cite; state
    this honestly as an untested branch rather than inventing an example, mirroring
    #955's own honesty about its untested conversation-sourced signal.

STEP 2  [needs 1] Write front matter: `id: ingestion-decision-extraction`,
`type: ingestion`, `status: draft`, `origin: launchpad`,
`audiences: [agent, reviewer]`. One evidence entry per substantive claim: commit
citation for recorded revision; FACT entries for each grep/file-read/`gh issue view`
result above; TEAM_KNOWLEDGE for issue #957/#620's own DoD text and for the #307
comment text (attributed, no single openable file backs a GitHub comment).
`relationships`: `references: corpus-agents`, `implements: corpus-template-procedure`
— both merged and resolvable; no edge to `ingestion-concept-extraction` or any other
Feature #620 sibling (none merged on `origin/launchpad` at authoring time, per
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).

STEP 3  [needs 2] Write the body from `templates/procedure.md`'s required sections
(Overview, Before you start, one numbered task sequence forking by source shape per
Diátaxis's allowed non-linear structure, See also, Boundary, Relationships, Scope and
omissions). State the boundary against `standards/decision-references.md` precisely:
this node notices a decision exists and is worth citing; citing it correctly (form,
pinning, the four-step conflict recipe) is entirely that standard's job, not
restated here. State the boundary against `agents/concept-resolution.md`-shaped dedup
(not this node's concern — a decision, unlike a concept, does not get deduplicated,
it gets checked for accepted status) and against the general evidence-class contract
in `AGENTS.md` (not restated).

STEP 4  [needs 3] Run
`python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until
exit 0.

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command to earn the
verification stamp, then commit the plan + document in a separate call. Do not push,
do not open a PR (batch-run instruction — that is the batch owner's step).

PARALLEL: none — single file, single task, no code changes.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must report OK before commit. `review-code` (or self-review if unreachable) before
calling the task done.

BUDGET: small — one document, no code changes; evidence gathering scoped to
~15 ADR files' status fields, one contract file, one GitHub issue thread's body and
comments, and the already-merged corpus scaffolding (AGENTS.md, procedure template,
decision-references standard).

OPEN: Whether the PRD-document signal (Step 1's fourth bullet) generalizes as
cleanly as the other three once a real approved-scope-change instance exists is
untested — stated explicitly in the body rather than hidden.

LEFT OUT: No claim about implementing a decision-extraction *tool* or pipeline
(explicitly out of scope per parent Feature #620). No relationship to
`ingestion-concept-extraction` (#955) or any other Feature #620 sibling — none
merged on `origin/launchpad` at plan time. No restatement of
`standards/decision-references.md`'s citation forms, pinning rules, or conflict
recipe — that document owns all of it.
