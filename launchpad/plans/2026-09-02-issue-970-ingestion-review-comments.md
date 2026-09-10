# Issue #970 — ingestion/review-comments.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md` (id `corpus-agents`),
`templates/policy.md` (id `corpus-template-policy`), and
`standards/decision-references.md` (id `corpus-standard-decision-references`) are
merged on `origin/launchpad` (confirmed via `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus` at HEAD
`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`). No `ingestion/` directory exists there
yet. Sibling `ingestion/issue-comments.md` (#962) and `ingestion/pull-requests.md`
(#966) are both local-only, unmerged, and NOT valid relationship targets — but both
are readable in their own worktrees and both explicitly name this task (#970) as
owning "an individual review comment left on a pull request," distinct from a plain
issue comment (#962's subject) and from the PR's own body/diff/merge-state (#966's
subject, whose own PR7 rule refuses to source a review-comment claim and points here
by number). Issue #970's own Definition of Done tail is the identical policy-shaped
boilerplate `templates/policy.md`, `agents/invariants.md` (merged, `type: agent`),
and #962/#966 all carry: state scope/authority, separate MUST/SHOULD, define
enforcement/exceptions, link rather than duplicate. `templates/policy.md`'s "A note
on `type`" confirms `type` names the corpus surface (here: `ingestion`), not the
document's normative shape — so `type: ingestion` + policy template is the same
precedent pattern `agents-invariants` and #962/#966 already establish.

STEP 1  Gather one real, verifiable worked example of citing a specific pull-request
review comment, distinct from an issue comment and from the PR's own body/diff. ←
RUNS HERE
  - Confirm the fetch command directly: `gh api repos/<owner>/<repo>/pulls/<n>/comments`
    is a different REST endpoint from `gh issue view --json comments` (issue/PR-body
    comments) — scanned 100 recent merged PRs in `launchpad-26/buzz` (none carry
    review comments) and upstream `block/buzz` PR #7187 (merged,
    `b270437a62bc1049b27745799dc44268d0c23489`) returns 4 real review comments, each
    with its own numeric `id`, `path`, `line`/`original_line`, `diff_hunk`,
    `position`/`original_position`, and a permalink of the form
    `.../pull/<n>#discussion_r<id>` — a distinct fragment shape from an issue
    comment's `#issuecomment-<id>` (per #962), so the two are not interchangeable
    citations even when both are GitHub comments.
  - Confirm the staleness mechanic with real, not invented, data: GraphQL
    `reviewThreads` on PR #7187 shows one thread `isOutdated: false` (`line: 941`,
    unchanged) and a second `isOutdated: true` (`line: null`, `originalLine: 1015`)
    — the diff moved after the comment was posted and GitHub can no longer place it
    on the current diff, even though the comment's own text is untouched. Both
    threads are separately `isResolved: true`, each resolved by a reply comment
    ("Addressed with ... in `f0a3c7b32`" / "... removed in `f0a3c7b32` ... no longer
    exists") rather than by editing the original comment — a real instance of
    "resolved/superseded without the comment text being edited," not a hypothetical.
  - Confirm the citation-shape mechanics against `validate.py` directly: `_GITHUB_URL_RE`
    matches only `blob|raw|tree|blame|commits|edit` verbs after `github.com/<owner>/<repo>/`;
    a PR permalink's path segment is `pull/<n>`, matching none of them, so
    `_classify_url` falls through to the same non-fatal `unverified — is an external
    URL...` branch #962 and #966 already document for an issue-comment permalink and
    a PR URL respectively. A `gh_api(...) -> ...`-shaped tool-result citation matches
    `_TOOL_RESULT_RE` and lands in the same channel.

STEP 2  [needs 1] Write front matter: `id: ingestion-review-comments`,
`type: ingestion`, `status: draft`, `origin: launchpad`,
`audiences: [agent, reviewer]`. One evidence entry per substantive claim: commit
citation for the recorded revision; FACT entries for the type-enum/no-template-member
fact, the `_GITHUB_URL_RE`/`_classify_url` behavior read directly from `validate.py`,
and the `gh api .../pulls/<n>/comments` + GraphQL `reviewThreads` shapes/fields
observed on PR #7187; TEAM_KNOWLEDGE for the PR #7187 comment bodies and resolution
state themselves (attributed, no openable file backs a GitHub comment) and for issue
#970's own DoD text and #962/#966's stated boundary against this node.
`relationships`: `depends-on: corpus-agents` (evidence-classification and
front-matter authority derived from `AGENTS.md`, not original here — the same
justification `agents-invariants`, #962 and #966 give for the identical edge),
`implements: corpus-template-policy` (policy-shaped instance),
`references: corpus-standard-decision-references` (this node's MUST list specializes
that standard's "when the only source is an issue, a PR or a conversation" passage
for the single-review-comment case, cited as supporting context rather than
restated). No edge to `ingestion-issue-comments` (#962) or `ingestion-pull-requests`
(#966) — neither is merged on `origin/launchpad` at authoring time.

STEP 3  [needs 2] Write the body from `templates/policy.md`'s six required sections
(Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and
omissions), each MUST/SHOULD item carrying its own stable id (starting fresh, per
`templates/policy.md`'s P4) and naming what enforces it or that nothing does. State
the boundary against #962 (issue comment — no diff, no line anchor, no
resolved/outdated state) and #966 (the PR's own body/diff/merge-state — a different
author's artifact than a reviewer's response to it) explicitly by title in Scope and
authority. Cover, as the review-comment-specific additions neither sibling states:
disambiguating a review comment by its `#discussion_r<id>` permalink or `path`+`line`
position, reading `isResolved`/`isOutdated` (or the REST `line`-vs-`original_line`
divergence) before relying on a comment's positional anchor, and treating "resolved"
or a stale anchor as independent of whether the comment's substantive claim still
holds.

STEP 4  [needs 3] Run
`python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until
exit 0.

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command to earn the
verification stamp, dispatch an independent `serina:review-code` pass (fresh context)
on the diff and fix real findings, then commit the plan + document in a separate
call. Do not push, do not open a PR (batch-run instruction — that is the batch
owner's step).

PARALLEL: none — single file, single task, no code changes.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must report OK before commit. `review-code` (or self-review if unreachable) before
calling the task done.

BUDGET: small — one document, no code changes; evidence gathering scoped to one real
`gh api .../pulls/<n>/comments` + GraphQL `reviewThreads` fetch against a genuine
merged PR, the relevant `validate.py` regex/classification functions, and the
already-merged corpus scaffolding (`AGENTS.md`, policy template,
decision-references standard).

OPEN: Whether the resolved-without-edit and stale-position mechanics generalize
beyond the one worked PR (#7187) — e.g. a review comment resolved by a human
clicking "Resolve conversation" with no reply comment at all, which #7187 does not
exhibit — is untested and will be stated as an unverified expectation rather than
hidden.

LEFT OUT: No claim about implementing a review-comment-ingestion *tool* or pipeline
(explicitly out of scope per parent Feature #620). No relationship to
`ingestion-issue-comments` (#962) or `ingestion-pull-requests` (#966) — neither
merged on `origin/launchpad` at plan time. No restatement of
`standards/decision-references.md`'s citation forms, pinning rules, MUST list, or
conflict recipe for *decisions* generally — that document owns all of it; this node
only adds what is specific to a single PR review comment.
