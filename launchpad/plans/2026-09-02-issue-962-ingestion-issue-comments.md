# Issue #962 — ingestion/issue-comments.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md` (id `corpus-agents`),
`templates/policy.md` (id `corpus-template-policy`), and
`standards/decision-references.md` (id `corpus-standard-decision-references`) are
merged on `origin/launchpad` (confirmed via `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus` at HEAD `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`).
No `ingestion/` directory exists there yet — sibling `ingestion/decision-extraction.md`
(#957) is local-only, unmerged, and NOT a valid relationship target, same for
companion task `ingestion/issues.md` (#963, being authored in parallel this same
batch run — also not a valid target). Unlike #957 (a noticing/screening *procedure*),
issue #962's own Definition of Done tail is policy-shaped: "states scope and
authority/source of the policy", "separates MUST requirements from SHOULD guidance",
"defines enforcement/checks and exception/escalation process", "links decisions or
higher-order policy instead of duplicating them" — the identical boilerplate
`templates/policy.md` and `agents/invariants.md` (id `agents-invariants`, merged,
type `agent`, template `policy`) both carry. `templates/policy.md`'s own "A note on
`type`" section confirms `type` names the corpus surface, not the document's
normative shape — so `type: ingestion` (this node lives under `ingestion/`) combined
with the policy template is the same pattern `agents-invariants` (`type: agent` +
policy template) already establishes.

STEP 1  Gather one real, verifiable worked example of citing a specific GitHub issue
comment, distinct from citing the issue's own body/title/state. ← RUNS HERE
  - Fetch `gh issue view 307 --repo launchpad-26/buzz --json comments` directly (not
    reused from #957's prose). Confirms two comments exist, each with its own
    `id` (GraphQL node id, e.g. `IC_kwDOTv8O788AAAABQmeCTA`), a comment permalink URL
    (`https://github.com/launchpad-26/buzz/issues/307#issuecomment-5409047116`),
    `createdAt`, and `author.login` — none of which a bare `owner/repo#307` citation
    names, so a citation naming only the issue number cannot disambiguate which of
    several comments supports a claim.
  - Confirm the retraction/supersession mechanic with real timestamps: the first
    comment (2026-08-25T10:23:56Z, "Decision recorded") states the outcome was
    "Decided automatically" and that Jeff "did not personally select this individual
    outcome" — i.e. it reads as a decision record but does not meet
    `launchpad/AGENTS.md` §5.1's bar (a human's verbatim choice). The second comment
    (2026-08-31T08:03:26Z, "Human decision recorded") is the one that actually
    supplies a verbatim human quote ("a") over named options. A reader stopping at
    the first, chronologically-earlier comment would cite the wrong one.
  - Confirm the citation-shape mechanics against `validate.py` directly, not by
    inference from `AGENTS.md`'s prose alone: `_GITHUB_URL_RE` matches only
    `blob|raw|tree|blame|commits|edit` verbs, so an `issues/307#issuecomment-<id>`
    permalink matches none of them and falls through `_classify_url` to
    `CitationVerdict("unverified", "is an external URL...")` — structurally identical
    to how a bare issue URL is treated, extending `AGENTS.md`'s "When the only source
    is an issue" rule specifically to a single comment. A `gh_issue_view(...) -> ...`
    tool-result citation matches `_TOOL_RESULT_RE` and is also `unverified` for the
    same structural reason.
  - Note the thinness boundary as guidance, not from a second worked instance: a
    comment supplying no attributable claim ("+1", "lgtm", "done") has nothing for
    `provided_by` to attribute beyond the commenter's presence, so it is not a citable
    `TEAM_KNOWLEDGE` entry at all — state this honestly as reasoned guidance, since no
    real "+1"-only comment was found being cited as evidence anywhere in this corpus.

STEP 2  [needs 1] Write front matter: `id: ingestion-issue-comments`,
`type: ingestion`, `status: draft`, `origin: launchpad`,
`audiences: [agent, reviewer]`. One evidence entry per substantive claim: commit
citation for the recorded revision; FACT entries for the `node.schema.json`
type-enum/no-template-member fact, the `_GITHUB_URL_RE`/`_classify_url` behavior read
directly from `validate.py`, and the `gh issue view --json comments` shapes/fields
observed on #307; TEAM_KNOWLEDGE for the #307 comment bodies themselves (attributed,
no openable file backs a GitHub comment) and for issue #962's own DoD text.
`relationships`: `depends-on: corpus-agents` (evidence-classification and
front-matter authority derived from `AGENTS.md`, not original here — the same
justification `agents-invariants` and `templates/policy.md` give for the identical
edge), `implements: corpus-template-policy` (policy-shaped instance),
`references: corpus-standard-decision-references` (this node's MUST list specializes
that standard's MUST 4 and its "when the only source is an issue" passage for the
single-comment case, cited as supporting context rather than restated). No edge to
`ingestion-decision-extraction` (#957) or `ingestion-issues` (#963) — neither is
merged on `origin/launchpad` at authoring time.

STEP 3  [needs 2] Write the body from `templates/policy.md`'s six required sections
(Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and
omissions), each MUST/SHOULD item carrying its own stable id (starting fresh, per
`templates/policy.md`'s P4) and naming what enforces it or that nothing does. State
the boundary against companion task `ingestion/issues.md` (#963) explicitly by title
in Scope and authority: that task covers the issue's own body/title/state as a
citable unit; this node covers one comment on that issue as a narrower, independently
citable unit. State the boundary against `standards/decision-references.md` (its MUST
4 and "When the only source is an issue" passage govern citing an issue generally;
this node covers the comment-specific mechanics that standard does not: which comment,
how ordering/retraction works, and the thinness floor) and against `AGENTS.md` (the
general FACT/INFERENCE/TEAM_KNOWLEDGE contract, not restated).

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
`gh issue view --json comments` fetch, the relevant `validate.py` regex/classification
functions, and the already-merged corpus scaffolding (`AGENTS.md`, policy template,
decision-references standard).

OPEN: Whether the thinness-floor guidance (Step 1's fourth bullet) holds up against a
real "+1"-shaped comment someone actually tried to cite is untested — no such instance
exists yet in this corpus to check it against; stated explicitly in the body as an
unverified expectation rather than hidden.

LEFT OUT: No claim about implementing a comment-ingestion *tool* or pipeline
(explicitly out of scope per parent Feature #620). No relationship to
`ingestion-decision-extraction` (#957) or `ingestion-issues` (#963) — neither merged
on `origin/launchpad` at plan time. No restatement of
`standards/decision-references.md`'s citation forms, pinning rules, MUST list, or
conflict recipe for *decisions* generally — that document owns all of it; this node
only adds what is specific to a single comment.
