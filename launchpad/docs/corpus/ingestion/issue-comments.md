---
id: ingestion-issue-comments
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
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no ingestion/ directory at all, so this node has no merged sibling under ingestion/ to follow as type precedent; both locally-drafted, unmerged siblings -- ingestion/decision-extraction.md (#957) and ingestion/issues.md (#963, this node's companion task, authored in parallel in this same batch run) -- are not valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ path present; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "gh issue view 307 --repo launchpad-26/buzz --json comments returns exactly two comments, each carrying its own id (a GraphQL node id, e.g. IC_kwDOTv8O788AAAABQmeCTA), a distinct permalink URL of the form https://github.com/launchpad-26/buzz/issues/307#issuecomment-<numeric-id>, a createdAt timestamp, and an author.login -- none of which a bare owner/repo#307 citation names, so citing only the issue number cannot disambiguate which of several comments a claim rests on."
    entry_class: FACT
    evidence:
      - "gh_issue_view(307, repo='launchpad-26/buzz', field='comments') -> two comments: id IC_kwDOTv8O788AAAABQmeCTA, url .../issues/307#issuecomment-5409047116, createdAt 2026-08-25T10:23:56Z, author tucktuck101; id IC_kwDOTv8O788AAAABRl3HjA, url .../issues/307#issuecomment-5475518348, createdAt 2026-08-31T08:03:26Z, author tucktuck101"
  - statement: "The first comment on launchpad-26/buzz#307 (2026-08-25T10:23:56Z) is headed 'Decision recorded' and states the outcome was 'Decided automatically' because 'Jeff authorized automated selection of Low and clear-Medium ADR outcomes and did not personally select this individual outcome' -- it reads as a settled decision record but does not supply a human's own verbatim choice. The second comment (2026-08-31T08:03:26Z, six days later) is headed 'Human decision recorded' and states that Jeffrey (@tucktuck101) 'reviewed options A-D with their positive and negative consequences, then chose Option A..., replying verbatim: \"a\"' -- the comment that actually meets launchpad/AGENTS.md §5.1's bar. An agent citing only the first, chronologically-earlier comment would attribute the decision to an automated placeholder rather than to the human choice the later comment records."
    entry_class: FACT
    evidence:
      - "gh_issue_view(307, repo='launchpad-26/buzz', field='comments') -> first comment body opens 'Decision recorded' and states 'Decided automatically... did not personally select this individual outcome'; second comment body opens 'Human decision recorded — 2026-08-31' and quotes 'a'"
  - statement: "validate.py's _GITHUB_URL_RE matches only the blob, raw, tree, blame, commits and edit verbs after a github.com repository path; an issue-comment permalink (.../issues/<n>#issuecomment-<id>) matches none of them, so _classify_url falls through its match branch entirely and returns CitationVerdict('unverified', 'is an external URL this validator can neither pin nor open') -- structurally identical to how validate.py treats a bare issue URL, and confirming that a specific-comment citation carries no more mechanical verification than a whole-issue one."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's _TOOL_RESULT_RE matches a citation of the shape identifier(...) -> text, which a gh issue view --json comments result written as evidence (e.g. gh_issue_view(307, repo='launchpad-26/buzz', field='comments') -> ...) satisfies; _classify_citation routes that shape to the same non-fatal unverified channel as a commit reference or graph edge, never to a file-existence check."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "standards/decision-references.md's MUST 4 requires opening a cited decision record and reading its front-matter status before citing it for an intent claim; its 'When the only source is an issue, a PR or a discussion' passage extends the same discipline to an issue thread generally, directing TEAM_KNOWLEDGE with provided_by naming the issue rather than forcing a FACT onto an UNVERIFIED citation -- both written at the level of the issue as a whole, and neither one states how to identify which specific comment on a multi-comment issue a claim rests on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "launchpad/AGENTS.md §5.1 reserves choosing between decision options for a human, and requires an agent recording someone else's decision to quote them verbatim and link where they said it, never resting on the agent's own judgement -- the bar the second #307 comment meets and the first, automated-selection comment does not, even though both are headed as decision records."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad/AGENTS.md §5.1, as applied to the launchpad-26/buzz#307 comment thread"
  - statement: "A comment supplying no attributable claim beyond the commenter's presence -- '+1', 'lgtm', 'done' -- has nothing for a TEAM_KNOWLEDGE entry's provided_by to attribute a statement to, so it is not a citable evidence entry at all; this is reasoned guidance rather than a worked instance, since no comment of that shape was found being cited as corpus evidence anywhere in this repository at authoring time."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.75
  - statement: "Issue #962's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#962 definition of done"
  - statement: "Parent Feature #620's Out of scope section states: 'Work owned by sibling corpus Features, implementation of the knowledge-crate runtime, and any artifact not required by this Feature outcome or its declared child issues' -- confirming no comment-ingestion pipeline or tool is expected from this node, only the citation mechanics an agent or reviewer applies while reading a specific comment already in front of them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Out of scope section"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-decision-references
---

# Policy: citing a specific GitHub issue comment

This node states the binding requirements for citing **one comment** on a GitHub
issue as evidence in a corpus node — as distinct from citing the issue's own body,
title, or open/closed state, which is companion task `ingestion/issues.md` (#963)'s
subject, not this one's. A comment is where a human decision, correction, or
retraction is actually recorded in this repository's workflow; the issue body around
it is frequently a template that stays unchanged. See the worked example below.

## Scope and authority

**This node governs** how an evidence entry cites one specific comment on a GitHub
issue: which identifier disambiguates it from the issue's other comments, what
citation shape the corpus checker actually recognizes for it, how to handle a later
comment that retracts or supersedes an earlier one on the same issue, and the floor
below which a comment carries nothing worth citing at all.

**Its authority is derived, not original.** `standards/decision-references.md`'s
MUST 4 (open a cited record and read its status before citing it) and its "When the
only source is an issue, a PR or a discussion" passage already establish that an
issue-sourced claim takes `TEAM_KNOWLEDGE`, attributed via `provided_by`, never a
`FACT` resting on an `UNVERIFIED` citation. Both are written at the level of an issue
as a whole. This node narrows that same discipline to the case where the citable unit
is one comment among several — it does not re-derive the FACT/TEAM_KNOWLEDGE choice,
it applies it to a smaller, harder-to-disambiguate target. **Where this node and
`standards/decision-references.md`, `AGENTS.md`, or `node.schema.json` disagree, they
win** — this node has drifted and should be fixed.

| For | Read |
|---|---|
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract | `launchpad/docs/corpus/AGENTS.md` |
| Citing a decision (ADR, specification) once found, and citing an issue generally | `launchpad/docs/corpus/standards/decision-references.md` |
| Citing an issue's own body, title, labels or state | `launchpad/docs/corpus/ingestion/issues.md` (#963) |
| Noticing that a decision exists and screening whether it is settled | `launchpad/docs/corpus/ingestion/decision-extraction.md` (#957) |
| What the checker does with a URL or tool-result citation | `launchpad/project-intelligence/corpus/validate.py` |

## MUST

| # | Requirement |
|---|---|
| **C1** | An evidence entry resting on a specific comment MUST identify which comment — by its permalink URL (`https://github.com/<owner>/<repo>/issues/<n>#issuecomment-<id>`) or by naming the fetch that produced it (e.g. `gh issue view <n> --json comments`) together with enough of the comment's own content, author, or timestamp in the `statement` to locate it among the issue's other comments. A bare `owner/repo#<n>` citation names the issue, not a comment, and cannot disambiguate one comment from another on the same thread. Enforced by review only — `validate.py` never reads a citation's semantic target, only its shape (see Enforcement). |
| **C2** | The evidence class MUST be `TEAM_KNOWLEDGE` with `provided_by` naming the issue and, where useful, the comment, never `FACT`. Both a comment permalink and a `gh issue view` tool-result citation are structurally `UNVERIFIED` (see Enforcement) — no citation shape available for a comment gives the corpus checker anything to open, so no comment-sourced claim clears the bar `AGENTS.md` sets for `FACT`. Enforced by `node.schema.json`'s conditional rules for the field shape (a hard error if `confidence` and `provided_by` are both present or both absent for the wrong class); the FACT-vs-TEAM_KNOWLEDGE choice itself is enforced by review only. |
| **C3** | Before citing a comment, the author MUST read **every** comment on the issue in chronological order, not stop at the first one that looks relevant. A later comment can retract, correct, or supersede an earlier one on the same issue without editing or deleting it — the earlier comment stays visible and citable-looking. Enforced by review only. |
| **C4** | When two comments on the same issue speak to the same claim and disagree, the `statement` MUST name both, in chronological order, and say which one the claim actually rests on and why — mirroring `standards/decision-references.md`'s own "quote the sentence you are relying on" discipline, applied here to *which* comment rather than *which* decision record. Silently citing only the later comment leaves a reader unable to tell whether the earlier one was read and rejected, or never read at all. Enforced by review only. |
| **C5** | A comment supplying no attributable claim beyond the commenter's presence — an acknowledgement, an emoji reaction rendered as a comment, a bare "+1" or "done" — MUST NOT be cited as a `TEAM_KNOWLEDGE` entry. There is nothing for `provided_by` to attribute a *statement* to; the entry would name a source without saying what it told the corpus. Enforced by review only. |

## SHOULD

| # | Guidance |
|---|---|
| **D1** | The `statement` SHOULD quote the load-bearing sentence from the comment directly, the same way `standards/decision-references.md`'s own SHOULD list prefers a quotation to a line position — a comment permalink survives the thread being reflowed or the comment being edited, but a quotation is what a later reader actually needs to confirm the claim without re-fetching the issue. |
| **D2** | Where a decision is being recorded from a comment specifically (not merely a fact about repository history), the author SHOULD also check whether a decision record now exists that names the issue in its own `issue`/`decided_in` front matter, per `standards/decision-references.md`'s own "confirm the decision actually landed" step — a settled comment is not the last word if a record has since superseded it as the citable source. |
| **D3** | An author SHOULD prefer the comment's permalink URL over a bare mention of "a comment on #NNN" in the `statement`, even though both land on the same `UNVERIFIED` checker outcome (see Enforcement) — the permalink is what lets a later reader jump directly to the comment instead of re-reading the whole thread to find it. |

## Enforcement

**Mechanically enforced today:** none of C1–C5 directly. `validate.py`'s
`_GITHUB_URL_RE` recognizes only the `blob`, `raw`, `tree`, `blame`, `commits` and
`edit` verbs on a `github.com` repository path; an issue-comment permalink
(`.../issues/<n>#issuecomment-<id>`) matches none of them, so `_classify_url` falls
through to its final branch and reports `unverified — is an external URL this
validator can neither pin nor open`. A `gh issue view --json comments` tool-result
citation (`identifier(...) -> text`) matches `_TOOL_RESULT_RE` and lands in the same
non-fatal `unverified` channel, alongside a commit reference or graph edge. Both
outcomes are non-fatal and exit 0 — the checker never distinguishes a comment
citation that was actually read from one that was fabricated.

**What a green validation run does NOT establish about this node's subject:** that
the cited comment exists at all; that the `id` or permalink named in a `statement`
resolves to a real comment on the named issue; that the comment quoted was the
earliest, the latest, or the one that actually settled the claim among several on
the same thread; that a comment cited as `TEAM_KNOWLEDGE` carries an attributable
statement rather than a bare acknowledgement (C5); or that a retraction/supersession
between two comments on the same issue (C3, C4) was checked for at all.
`AGENTS.md`'s "Three things a passing run does not mean" is the general statement of
this; every point above is that statement applied to a comment specifically.

**Enforcement is the pull-request review**, the same model `templates/policy.md` and
`agents/invariants.md` both name for themselves: a reviewer checking a node that
cites an issue comment opens the permalink (or re-runs the `gh issue view` fetch),
confirms the comment says what the `statement` claims, confirms no later comment on
the same issue contradicts or supersedes it, and confirms the entry is
`TEAM_KNOWLEDGE`, not `FACT`.

## Exceptions and escalation

**There is no exemption from C1–C5.** A comment-sourced claim that cannot meet them
is not a citable one — reword the claim to rest on something else, or drop it.

**A disputed application is a judgement, not an exception.** Whether a given comment
crosses C5's thinness floor, or whether two comments genuinely disagree under C4, is
a call an author and reviewer can read differently. The author records the tension
in the pull request and the reviewer decides; a repeated disagreement is filed as an
issue against this node.

**A case this node does not cover is escalated, not invented** — as an issue against
parent Feature #620, describing the comment-citation situation that was needed and
could not be resolved from C1–C5.

## Scope and omissions

**This node covers** the citation mechanics specific to one comment on a GitHub
issue: disambiguating which comment, the citation shapes the checker recognizes and
what `UNVERIFIED` means for each, reading comments in order rather than stopping at
the first relevant one, handling a later comment that retracts or supersedes an
earlier one on the same issue (worked from `launchpad-26/buzz#307`'s two comments),
and the floor below which a comment is not worth citing at all.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citing the issue's own body, title, labels, or open/closed state | `launchpad/docs/corpus/ingestion/issues.md` (#963, unmerged at this node's authoring time) |
| Noticing that a decision exists in a source and screening whether it is settled, across ADRs, specifications, issues, and PRD/Feature bodies generally | `launchpad/docs/corpus/ingestion/decision-extraction.md` (#957, unmerged at this node's authoring time) |
| Citing a decision record once found — form, pinning, the four-step conflict recipe | `launchpad/docs/corpus/standards/decision-references.md` |
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract and evidence-class discipline | `launchpad/docs/corpus/AGENTS.md` |
| Citing a pull request's comments or review threads specifically, as opposed to an issue's | Not addressed here — untested whether C1–C5 generalize to a PR review thread, which carries additional comment kinds (review comments anchored to a diff line) an issue thread does not |

**Expected but not verified when this node was written:**

- **C5's thinness floor is reasoned guidance, not a worked instance.** No comment of
  the "+1"/"lgtm"/"done" shape was found being cited as corpus evidence anywhere in
  this repository at authoring time, so the rule is stated from the schema's own
  `provided_by` requirement rather than from a real rejected citation.
- **Whether C1–C5 generalize to a pull-request review-comment thread**, which anchors
  comments to a diff line and carries its own resolved/unresolved state, is untested
  — every worked example here is an issue comment, not a PR review comment.
- **No CI run has exercised this node.** All `validate.py` evidence above is local to
  this worktree.
- **No author or harness has applied C1–C5 outside this session.** Whether the
  chronological-reading and retraction-handling steps (C3, C4) are followable in
  practice on an issue with many more than two comments is untested.
