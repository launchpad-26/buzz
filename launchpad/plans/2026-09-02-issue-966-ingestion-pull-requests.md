# Issue #966 — ingestion/pull-requests.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`
(id `corpus-agents`), `launchpad/docs/corpus/standards/evidence.md` (id `corpus-standard-evidence`),
`launchpad/docs/corpus/standards/code-references.md` (id `corpus-standard-code-references`),
`launchpad/docs/corpus/standards/decision-references.md`, and `launchpad/docs/corpus/templates/policy.md`
are merged on `origin/launchpad`. No `ingestion/*.md` node exists there yet — #962/#963 (issues,
issue-comments) and #970 (review-comments) are unmerged siblings and are never legitimate
relationship targets. `git grep "PR #"` across the merged corpus found no existing node citing a
GitHub pull request, so there is no prior worked pattern to reconcile against, only the citation-shape
rules in `AGENTS.md` and `standards/code-references.md` to build on.

STEP 1  Confirm the citation-shape facts this node rests on, directly rather than from memory:
`standards/code-references.md`'s own statement that "GitHub issue and pull-request URLs ... are
routed to a non-fatal UNVERIFIED channel;" `AGENTS.md`'s worked guidance that a PR/issue citation
with no openable file must be `TEAM_KNOWLEDGE` with `provided_by`, never forced into `FACT`; and
`CONTRIBUTING.md` / `launchpad/README.md` / `launchpad/AGENT_PR_TEMPLATE.md` for this repo's actual
PR conventions (DCO sign-off, `Closes #NNN` one-per-line, squash/rebase disabled per ADR-0055,
the `Escalations` section). Fetch one real merged PR (`gh pr view 1978 --repo launchpad-26/buzz`)
and one real open PR (`gh pr view 2055`) as worked, cited examples of a stable merged-state citation
versus a mutable open-state one. ← RUNS HERE

STEP 2  [needs 1] Draft front matter: id `ingestion-pull-requests`, type `ingestion`, status `draft`,
origin `launchpad`, audiences `[agent, developer, reviewer]`, relationships `depends-on: corpus-agents`,
`depends-on: corpus-standard-evidence`, `references: corpus-standard-code-references` (all three
merged and resolvable on `origin/launchpad`). Evidence ledger cites the HEAD commit, the merged/open
PR fetched in STEP 1 as `TEAM_KNOWLEDGE` (never `FACT` — no openable file backs a PR body), and every
schema/standard/AGENTS.md fact as `FACT` against its opened source.

STEP 3  [needs 2] Write the body against `templates/policy.md`'s six required sections
(`Scope and authority`, `MUST`, `SHOULD`, `Enforcement`, `Exceptions and escalation`,
`Scope and omissions`), H1 `# Policy: citing a pull request`. Core MUST content: a PR's own
description/body/diff/merge-state/closing-links are in scope; individual review comments on it are
#970's scope (named explicitly since #970 is unmerged and unreadable); an OPEN PR's diff/description
is not stable evidence (may still change) and MUST NOT be cited for a claim needing that stability,
while a MERGED PR's merge-commit SHA is a stable pin citable as `FACT`-eligible-if-opened; a claim
about the PR's own content (what it says, what it changed) is `TEAM_KNOWLEDGE` with `provided_by`
naming the PR, per `AGENTS.md`'s existing rule, since no citation shape makes a PR body openable to
the checker. Boundary section states the #962/#963 (issue vs. PR) and #970 (PR vs. its review
comments) distinctions by name.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run
until exit 0.

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command to earn the verification
stamp, then commit in a separate call. Do not push or open a PR — the batch owner integrates this
with sibling ingestion/agents docs afterward.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
print `OK`. An independent `review-code` pass runs after the commit, per the batch's build loop.

BUDGET: small — one document, no code changes, evidence gathering scoped to ~6 already-merged
corpus files plus two `gh pr view` calls.

OPEN: Whether to declare `references: corpus-standard-decision-references` as a second structural
analog (another "citing X as evidence, which kind of claim" node) is left to drafting judgement in
STEP 2/3 rather than fixed here — added only if the body actually needs to point a reader there.

LEFT OUT: No relationship to any `ingestion/*.md` or `agents/*.md` sibling — none are merged at
authoring time. No attempt to write #970/review-comments' content even in outline — that boundary is
named, not filled in. No change to `CONTRIBUTING.md`, `launchpad/AGENT_PR_TEMPLATE.md`, or any PR
template file themselves — this node documents citation practice, it does not own or edit the
templates it describes.
