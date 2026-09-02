---
id: ingestion-review-comments
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "node.schema.json's type enum includes ingestion among its thirteen members and has no member named template or policy; templates/policy.md's own 'A note on type' section states the enum names the corpus surface a node documents, not the document's normative MUST/SHOULD shape, so a policy-shaped node under ingestion/ correctly carries type: ingestion rather than governance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "agents/invariants.md is a merged, precedent instance of the identical pattern this node follows: type: agent (matching its own directory's surface, not governance) combined with the policy template, declaring both depends-on: corpus-agents and implements: corpus-template-policy for the same reasons this node declares them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no ingestion/ directory at all, so this node has no merged sibling under ingestion/ to follow as type precedent; the two unmerged siblings that name this node's boundary -- ingestion/issue-comments.md (#962) and ingestion/pull-requests.md (#966), each read directly in its own worktree at authoring time -- are not valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ path present; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "gh api repos/block/buzz/pulls/7187/comments returns exactly four diff-anchored review comments on merged upstream PR #7187 (merge commit b270437a62bc1049b27745799dc44268d0c23489), each carrying its own numeric id (e.g. 3906293393), a path, a line and a separate original_line, a diff_hunk, a position and a separate original_position, and a permalink of the form https://github.com/block/buzz/pull/7187#discussion_r<id> -- a distinct URL-fragment shape (#discussion_r<id>) from an issue comment's #issuecomment-<id> fragment, so the two are not interchangeable citations even though both are GitHub comments on the same numbered thread."
    entry_class: FACT
    evidence:
      - "gh_api(repos/block/buzz/pulls/7187/comments) -> 4 comments; ids 3906293393, 3906552022, 3906817552, 3906817676; paths mobile/ios/Runner.xcodeproj/project.pbxproj and .github/workflows/ci.yml"
  - statement: "On the same PR #7187, three distinct GitHub comment surfaces coexist and return different counts for the identical thread: gh api repos/block/buzz/issues/7187/comments (general conversation, no diff anchor) returns 12 comments; gh api repos/block/buzz/pulls/7187/comments (diff-anchored review comments) returns 4; and gh api repos/block/buzz/pulls/7187/reviews (a review's own top-level verdict/summary, e.g. state: APPROVED with a body, not anchored to any file or line) returns 4 separate top-level reviews -- three different endpoints, three different objects, on one PR."
    entry_class: FACT
    evidence:
      - "gh_api(repos/block/buzz/issues/7187/comments) -> 12 entries"
      - "gh_api(repos/block/buzz/pulls/7187/comments) -> 4 entries"
      - "gh_api(repos/block/buzz/pulls/7187/reviews) -> 4 entries, including one state: APPROVED review from user jedwards27 with an unanchored body"
  - statement: "A GraphQL reviewThreads query against PR #7187 shows two threads in different anchor states at the same point in time: one (path mobile/ios/Runner.xcodeproj/project.pbxproj, line 941) has isOutdated: false, its line unchanged since authoring; the other (path .github/workflows/ci.yml, originalLine 1015) has isOutdated: true and line: null -- the diff moved after the comment was posted and GitHub can no longer place it on the current diff. Both threads are separately isResolved: true, each resolved by a reply comment in the same thread ('Addressed with the broader production-seam guard in f0a3c7b32' / 'the implementation-specific linker script was removed in f0a3c7b32 ... no longer exists') rather than by any edit to the original comment's own body."
    entry_class: FACT
    evidence:
      - "gh_api_graphql(pullRequest(number: 7187) { reviewThreads }) -> two threads: isResolved true/isOutdated false (line 941, unchanged); isResolved true/isOutdated true (line null, originalLine 1015)"
  - statement: "validate.py's _GITHUB_URL_RE matches only the blob, raw, tree, blame, commits and edit verbs immediately after a github.com owner/repo path; a pull-request review-comment permalink's corresponding path segment is pull/<n>, which matches none of them, so _classify_url falls through to its final branch and returns CitationVerdict('unverified', 'is an external URL this validator can neither pin nor open') -- the identical non-fatal outcome ingestion/issue-comments.md (#962) documents for an issue-comment permalink and ingestion/pull-requests.md (#966) documents for a plain PR URL."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's _TOOL_RESULT_RE matches a citation of the shape identifier(...) -> text, which a gh api ... --jq ... result written as evidence (e.g. gh_api(repos/block/buzz/pulls/7187/comments) -> ...) satisfies; _classify_citation routes that shape to the same non-fatal unverified channel as a commit reference, a graph edge, or an external URL, never to a file-existence check."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "standards/decision-references.md's MUST 4 requires opening a cited decision record and reading its front-matter status before citing it for an intent claim; AGENTS.md's 'When the only source is an issue, a PR or a discussion' passage extends the same discipline to an issue or PR thread generally, directing TEAM_KNOWLEDGE with provided_by rather than forcing a FACT onto an UNVERIFIED citation -- both written at the level of an issue or a PR as a whole, and neither one states how to identify one specific diff-anchored comment among several on the same pull request, nor how to read that comment's resolved/outdated state before relying on it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "ingestion/issue-comments.md (#962), read directly in its own worktree at authoring time, states its own subject as one comment on a GitHub issue and explicitly excludes 'Citing a pull request's comments or review threads specifically, as opposed to an issue's' from its own scope, naming it as untested whether its own C1-C5 rules generalize there."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "ingestion/issue-comments.md (#962), an unmerged sibling node read in its own worktree at this node's authoring time"
  - statement: "ingestion/pull-requests.md (#966), read directly in its own worktree at authoring time, states in its own 'Which kind of GitHub entity are you citing?' table and its own MUST rule PR7 that a claim resting on an individual review comment left on a pull request MUST NOT be sourced under its guidance, and routes it explicitly to 'ingestion/review-comments.md (#970)' by number, naming the boundary as deliberate: a pull request's own description and diff are the artifact its author wrote and controls, while a review comment is a different author's response to it, with its own provenance and its own honesty questions (was it addressed, superseded, resolved)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "ingestion/pull-requests.md (#966), an unmerged sibling node read in its own worktree at this node's authoring time"
  - statement: "A review comment supplying no attributable claim beyond the commenter's presence -- 'nit', 'lgtm', a bot's own boilerplate footer with no substantive finding -- has nothing for a TEAM_KNOWLEDGE entry's provided_by to attribute a statement to, so it is not a citable evidence entry at all; this is reasoned guidance extended from #962's identical floor for issue comments, since no review comment of that shape was found being cited as corpus evidence anywhere in this repository at authoring time."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.75
  - statement: "Issue #970's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#970 definition of done"
  - statement: "Parent Feature #620's Out of scope section states: 'Work owned by sibling corpus Features, implementation of the knowledge-crate runtime, and any artifact not required by this Feature outcome or its declared child issues' -- confirming no review-comment-ingestion pipeline or tool is expected from this node, only the citation mechanics an agent or reviewer applies while reading a specific review comment already in front of them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Out of scope section, read via gh issue view at this node's authoring time"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-decision-references
---

# Policy: citing a pull-request review comment

This node states the binding requirements for citing **one diff-anchored review
comment** left on a pull request as evidence in a corpus node — as distinct from a
plain issue comment (sibling task `ingestion/issue-comments.md`, #962's subject) and
from the pull request's own body, description, diff or merge state (sibling task
`ingestion/pull-requests.md`, #966's subject, whose own MUST rule PR7 refuses to
source a review-comment claim under its guidance and names this node by number as
the destination). A review comment is anchored to a specific file and line in a
specific diff, and — unlike a plain issue comment — carries its own resolved/outdated
lifecycle that can move independently of whether the comment's underlying claim is
still true. See the worked example below.

## Scope and authority

**This node governs** how an evidence entry cites one specific, diff-anchored review
comment left on a pull request: which identifier disambiguates it from the pull
request's other review comments, from its general conversation comments, and from a
review's own unanchored summary text; what citation shape the corpus checker
recognizes for it; how a stale positional anchor differs from a resolved thread and
why neither one settles whether the comment's claim still holds; and the floor below
which a review comment carries nothing worth citing at all.

**Its authority is derived, not original.** `standards/decision-references.md`'s
MUST 4 (open a cited record and read its status before citing it) and `AGENTS.md`'s
"When the only source is an issue, a PR or a discussion" passage already establish
that a GitHub-thread-sourced claim takes `TEAM_KNOWLEDGE`, attributed via
`provided_by`, never a `FACT` resting on an `UNVERIFIED` citation. Both are written at
the level of an issue or a pull request as a whole. This node narrows that same
discipline to the case where the citable unit is one diff-anchored comment among
several on a pull request — it does not re-derive the FACT/TEAM_KNOWLEDGE choice, it
applies it to a smaller, harder-to-disambiguate, and independently stateful target.
**Where this node and `standards/decision-references.md`, `AGENTS.md`, or
`node.schema.json` disagree, they win** — this node has drifted and should be fixed.

| For | Read |
|---|---|
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract | `launchpad/docs/corpus/AGENTS.md` |
| Citing a decision (ADR, specification) once found, and citing an issue or PR generally | `launchpad/docs/corpus/standards/decision-references.md` |
| Citing a plain issue comment | `launchpad/docs/corpus/ingestion/issue-comments.md` (#962) |
| Citing a pull request's own body, diff, merge state, or closing-issue lines | `launchpad/docs/corpus/ingestion/pull-requests.md` (#966) |
| The citation forms that name code, and how each is pinned | `launchpad/docs/corpus/standards/code-references.md` |
| What the checker does with a URL or tool-result citation | `launchpad/project-intelligence/corpus/validate.py` |

## Which kind of GitHub comment are you citing?

A pull request carries more comment-shaped surfaces than one bare `owner/repo#NNN`
suggests, and they are not interchangeable. Confirmed directly on one real, merged
PR (`block/buzz#7187`) rather than assumed: `gh api repos/block/buzz/issues/7187/comments`
(general conversation, no diff anchor) returned 12 entries; `gh api
repos/block/buzz/pulls/7187/comments` (diff-anchored review comments) returned 4;
and `gh api repos/block/buzz/pulls/7187/reviews` (a review's own top-level verdict,
e.g. `state: APPROVED`, with a body that is not anchored to any file or line)
returned 4 separate reviews. Three different endpoints, three different objects, one
PR.

| If the source is | Cite it as |
|---|---|
| A general conversation comment on the pull request (the "Conversation" tab, no diff anchor) — fetched via the same `issues/<n>/comments` endpoint an issue comment uses | `ingestion/issue-comments.md` (#962) — not this node's guidance |
| The pull request's own description, diff, merge state, or `Closes #NNN` lines | `ingestion/pull-requests.md` (#966) — not this node's guidance |
| One diff-anchored comment on a specific file and line, fetched via `pulls/<n>/comments` | **this node** |
| A review's own top-level verdict/summary text (`state`, `body`), fetched via `pulls/<n>/reviews`, not anchored to any file or line | not explicitly covered by any Feature #620 task at this node's authoring time — see *Scope and omissions* |

## MUST

| # | Requirement |
|---|---|
| **V1** | An evidence entry resting on a specific review comment MUST identify which comment — by its permalink URL (`https://github.com/<owner>/<repo>/pull/<n>#discussion_r<id>`, distinct in shape from an issue comment's `#issuecomment-<id>`) or by naming the fetch that produced it (`gh api repos/<owner>/<repo>/pulls/<n>/comments`) together with enough of the comment's file path, line, author, or content in the `statement` to locate it among the pull request's other review comments and distinguish it from a general conversation comment on the same PR. Enforced by review only — `validate.py` never reads a citation's semantic target, only its shape (see Enforcement). |
| **V2** | The evidence class MUST be `TEAM_KNOWLEDGE` with `provided_by` naming the pull request and, where useful, the review comment, never `FACT`. Both a `#discussion_r<id>` permalink and a `gh api` tool-result citation are structurally `UNVERIFIED` (see Enforcement) — no citation shape available for a review comment gives the corpus checker anything to open, so no comment-sourced claim clears the bar `AGENTS.md` sets for `FACT`. Enforced by `node.schema.json`'s conditional rules for the field shape; the FACT-vs-TEAM_KNOWLEDGE choice itself is enforced by review only. |
| **V3** | Before citing a review comment for a claim about *where* it applies — which file, which line — the author MUST check whether the comment's positional anchor is still current (a GraphQL `reviewThreads` query's `isOutdated` field, or the REST API's `line` field returning `null` while `original_line` is still populated), rather than assuming the `diff_hunk` captured at fetch time still matches `HEAD`. Worked example: `block/buzz#7187`'s `.github/workflows/ci.yml` review thread carries `isOutdated: true` and `line: null` after later commits moved the diff, while its `.pbxproj` sibling thread remains `isOutdated: false`. Enforced by review only. |
| **V4** | A claim about a review comment's *positional or resolution state* (outdated, resolved) MUST be stated separately from a claim about *whether its underlying suggestion was correct or still applies*. `isResolved: true` records that the thread's participants marked the conversation done — by a reply, a fix, or a maintainer's own judgement — not that the corpus author has independently verified the suggestion was acted on correctly; `isOutdated: true` records that the diff moved, not that the issue was fixed. Worked example `block/buzz#7187` resolved both of its threads by a reply explaining what changed, never by editing the original comment's text — the original claim is exactly as it was written, and a reader who conflates "resolved" with "settled correctly" has not actually checked anything. Enforced by review only. |
| **V5** | Before citing a review comment that carries a reply (a GraphQL thread with more than one comment, or a REST comment whose `in_reply_to_id` is non-null), the author MUST read the full thread in order, not the first comment alone, and — when a later reply contradicts, retracts, or explains resolution of an earlier claim — the `statement` MUST name both and say which one the corpus claim actually rests on, mirroring `ingestion/issue-comments.md`'s (#962) identical C3/C4 discipline for a multi-comment issue thread. |
| **V6** | A review comment supplying no attributable claim beyond the commenter's presence — "nit", "lgtm", a bot's own unsubstantive boilerplate footer — MUST NOT be cited as a `TEAM_KNOWLEDGE` entry. There is nothing for `provided_by` to attribute a *statement* to. |
| **V7** | A claim about what current code at a cited file and line contains MUST NOT rest on a review comment's `diff_hunk` alone, even an `isOutdated: false` one. The comment records what the diff looked like when posted or last matched; the file at the current or a pinned revision (per `standards/code-references.md`) is the only citation that establishes what the code *is*. Citing the review comment establishes what a reviewer said about a moment in the diff's history; it does not stand in for a code-references citation. |

## SHOULD

| # | Guidance |
|---|---|
| **W1** | A `statement` citing a review comment SHOULD quote the load-bearing sentence from the comment body directly, the same practice `ingestion/issue-comments.md` (#962) recommends for an issue comment — a permalink survives the thread being reflowed, but a quotation is what a later reader needs without re-fetching the PR. |
| **W2** | An author SHOULD prefer the comment's `#discussion_r<id>` permalink over a bare mention of "a review comment on #NNN", even though both land on the same `UNVERIFIED` checker outcome (see Enforcement) — the permalink lets a later reader jump directly to the anchored diff line instead of re-reading the whole review. |
| **W3** | When the claim is about whether a review suggestion was acted on, the author SHOULD check both the thread's `isResolved` state and its reply comments (per V4 and V5) before asserting either "ignored" or "fixed" — a resolved thread with no reply, and an unresolved thread with a reply that already fixed the issue, are both real, observed shapes and neither one is safe to infer from `isResolved` alone. |

## Enforcement

**Mechanically enforced today:** none of V1–V7 directly. `validate.py`'s
`_GITHUB_URL_RE` recognizes only the `blob`, `raw`, `tree`, `blame`, `commits` and
`edit` verbs on a `github.com` repository path; a review-comment permalink's
corresponding path segment is `pull/<n>`, matching none of them, so `_classify_url`
falls through to its final branch and reports `unverified — is an external URL this
validator can neither pin nor open`. A `gh api ... -> ...` tool-result citation
matches `_TOOL_RESULT_RE` and lands in the same non-fatal `unverified` channel,
alongside a commit reference or graph edge. Both outcomes are non-fatal and exit 0 —
the checker never distinguishes a review-comment citation that was actually read,
whose resolved/outdated state was actually checked, from one that was fabricated.

**What a green validation run does NOT establish about this node's subject:** that
the cited review comment exists at all; that the `id` or permalink named in a
`statement` resolves to a real comment on the named pull request; that the comment's
`isOutdated` or `isResolved` state was checked before the citation was written, or
that either state means what V3/V4 say it means rather than what an author assumed;
that the comment quoted was read alongside its full reply thread (V5); that a comment
cited as `TEAM_KNOWLEDGE` carries an attributable statement rather than a bare
acknowledgement (V6); or that a code-content claim near a review comment was backed
by a separate code-references citation rather than the comment's own stale
`diff_hunk` (V7). `AGENTS.md`'s "Three things a passing run does not mean" is the
general statement of this; every point above is that statement applied to a review
comment specifically.

**Enforcement is the pull-request review**, the same model `templates/policy.md` and
`agents/invariants.md` both name for themselves: a reviewer checking a node that
cites a review comment opens the permalink (or re-runs the `gh api` fetch and, where
the claim depends on it, the GraphQL `reviewThreads` query), confirms the comment
says what the `statement` claims, confirms the positional/resolution state named in
the `statement` matches what GitHub currently reports, confirms no later reply on the
same thread contradicts or supersedes it, and confirms the entry is `TEAM_KNOWLEDGE`,
not `FACT`.

## Exceptions and escalation

**There is no exemption from V1–V7.** A review-comment-sourced claim that cannot meet
them is not a citable one — reword the claim to rest on something else (the code
itself, per `standards/code-references.md`, or the pull request as a whole, per
`ingestion/pull-requests.md`), or drop it.

**A disputed application is a judgement, not an exception.** Whether a given comment
crosses V6's thinness floor, whether two replies genuinely disagree under V5, or
whether a claim conflates resolution with correctness under V4, is a call an author
and reviewer can read differently. The author records the tension in the pull request
and the reviewer decides; a repeated disagreement is filed as an issue against this
node.

**A case this node does not cover is escalated, not invented** — as an issue against
parent Feature #620, describing the review-comment-citation situation that was needed
and could not be resolved from V1–V7. The unanchored review-summary surface named in
*Scope and omissions* below is one such case, already named rather than left implicit.

## Scope and omissions

**This node covers** the citation mechanics specific to one diff-anchored review
comment on a pull request: disambiguating it from a general conversation comment and
from a review's own unanchored summary, the citation shapes the checker recognizes
and what `UNVERIFIED` means for each, reading a comment's positional
(`isOutdated`/`line`) and resolution (`isResolved`) state before relying on it and
why neither settles the underlying claim (worked from `block/buzz#7187`'s two review
threads), reading a reply thread in order rather than the first comment alone, the
boundary against citing code directly, and the floor below which a review comment is
not worth citing at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citing a general conversation comment on an issue or a pull request | `launchpad/docs/corpus/ingestion/issue-comments.md` (#962, unmerged at this node's authoring time) |
| Citing the pull request's own body, diff, merge state, or closing-issue lines | `launchpad/docs/corpus/ingestion/pull-requests.md` (#966, unmerged at this node's authoring time) |
| Citing a review's own top-level, unanchored verdict/summary text (`pulls/<n>/reviews[].body`) — distinct from an individual diff-anchored comment, confirmed as a separate GitHub object in the worked example above | Not explicitly assigned to any Feature #620 task at this node's authoring time; treat as an untested extension of this node's guidance, not as covered by it |
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract and evidence-class discipline | `launchpad/docs/corpus/AGENTS.md` |
| The citation forms that name code — repository paths, positions, pinned GitHub file links | `launchpad/docs/corpus/standards/code-references.md` |
| Citing an accepted decision record | `launchpad/docs/corpus/standards/decision-references.md` |

**Expected but not verified when this node was written:**

- **V6's thinness floor is reasoned guidance, not a worked instance.** No review
  comment of the "nit"/"lgtm" shape was found being cited as corpus evidence anywhere
  in this repository at authoring time, so the rule is extended from `ingestion/issue-
  comments.md`'s (#962) identical floor for issue comments rather than from a real
  rejected review-comment citation.
- **Whether a thread can be `isResolved: true` with no reply comment at all** (a
  human clicking "Resolve conversation" directly, with no explanatory text) was not
  observed in the one worked example (`block/buzz#7187`) this node draws from, where
  both resolved threads happen to carry an explanatory reply. V4's guidance is
  written to hold regardless, but that specific shape is untested.
- **Whether V1–V7 generalize to a review comment authored by a human reviewer**
  rather than a bot is untested — every comment in the worked example above
  (`chatgpt-codex-connector[bot]`, replied to by a human, `brow`) is bot-authored on
  one side of the thread; no purely human-to-human review-comment thread was examined.
- **No CI run has exercised this node.** All `validate.py` evidence above is local to
  this worktree.
- **No author or harness has applied V1–V7 outside this session.** Whether the
  reply-thread-reading and resolution/staleness discipline (V3–V5) is followable in
  practice on a review with many more than two threads is untested.
