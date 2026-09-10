---
id: ingestion-pull-requests
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "node.schema.json's type enum includes ingestion among its thirteen members, naming the corpus surface a node about an external evidence source -- such as a pull request -- documents."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "node.schema.json requires id, type, status, origin, audiences and evidence, permits relationships as the only other field, and rejects any field beyond those seven."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The evidence standard states directly: when the only source is an issue, a pull request or a conversation, there is no openable file and no way to pin one; do not force it into a FACT on a URL or tool-result citation, because that produces an UNVERIFIED FACT -- a claim checked by nothing wearing the strongest class. Use TEAM_KNOWLEDGE with provided_by naming the issue, the pull request or the person, because ADR-0029 requires GitHub history to stay attributed rather than promoted to fact."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "The code-references standard states that commit references, graph edges, tool results and external URLs that are not pinned repository links -- explicitly including GitHub issue and pull-request URLs -- are routed to a non-fatal UNVERIFIED channel that always prints and never changes validate.py's exit status."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "The evidence standard's own citation-verdict table states that a URL the validator's repository-link pattern does not match -- including a GitHub issue or pull-request URL -- is reported unverified and establishes nothing, because the pattern requires a blob, raw, tree, blame, commits or edit segment that a PR or issue URL never carries, so it never enters that branch and falls through to the unverified case."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "templates/policy.md requires a policy-shaped node to carry six sections -- Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions -- in that relative order, none omitted or reordered among themselves, with an H1 of `# Policy: <subject>` unless a narrower template for the node's specific family states its own convention."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "relationships.schema.json defines depends-on as source requires target to be true/current for source's own claims to hold, and references as source cites target as supporting context with no ownership or currency dependency implied."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "This repository's contributor guide requires a Developer Certificate of Origin sign-off on every commit; the -s flag appends the Signed-off-by trailer, and the DCO Check blocks a pull request lacking it."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "This fork's PR convention requires one closing keyword per issue a batch completes, written as plain text -- not inside backticks or a code fence -- one per line, because GitHub creates no link and closes nothing from a reference written inside code, and a Feature is the PR-worthy unit: its child Tasks land together in one batch PR using Closes #12 per child, while Refs #12 is used when a PR touches but does not complete an issue."
    entry_class: FACT
    evidence:
      - "launchpad/README.md"
  - statement: "Both this fork's human PR template and its agent PR template carry a Related issue field with the identical instruction -- one closing keyword per issue the PR completes, one per line, as plain text. Only the agent template additionally carries an Escalations field, instructing the author to record anything raised rather than decided and stating that an empty escalations list on a complex change is itself a review signal; the human template has no Escalations field at all -- its nearest analog is a differently-scoped Deferred blockers field for defects merged alongside rather than fixed."
    entry_class: FACT
    evidence:
      - ".github/PULL_REQUEST_TEMPLATE.md"
      - "launchpad/AGENT_PR_TEMPLATE.md"
  - statement: "ADR-0055 settles that a pull request in this fork lands as a merge commit only -- allow_squash_merge and allow_rebase_merge are off on the repository, so merge is the only method the platform's button offers -- superseding the question ADR-0052 had left open."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0055-merge-commit-is-the-merge-strategy.md"
      - "launchpad/README.md"
  - statement: "ADR-0054 withdrew ADR-0052's 1,500-line/10-file batch-PR cap and established one-Feature-one-PR regardless of size, on the reasoning that every real Feature batch had already exceeded the cap and that the cap bound the small, compliant per-batch PRs while exempting the large one-Feature PR it existed to bound. ADR-0054 explicitly states it does not itself decide the separate squash-versus-merge question -- that is ADR-0055's -- only that withdrawing the cap raises the cost of leaving it open."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0054-one-feature-one-pr-no-size-cap.md"
      - "launchpad/README.md"
  - statement: "AGENTS.md's creating-a-node step 9 requires a declared relationship target to be checked against the branch being merged into (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus), not the author's own worktree, because the checker loads whatever is present where it runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At this node's authoring time, no ingestion/*.md node exists on origin/launchpad, so no prior ingestion-typed node states citation rules for a pull request specifically. Grepping the merged corpus for the literal text 'PR #' does return matches -- several capabilities/ and layers/ nodes (for example capabilities/channels/channel-templates.md and layers/compute/sprig-runtime.md) narrate a PR number -- but in every matching case it annotates a commit citation or narrative prose, never a bare owner/repo#NNN or PR-URL evidence citation of the kind this node's own MUST rules govern, so this node still has no prior node stating pull-request-specific citation rules to reconcile against."
    entry_class: INFERENCE
    confidence: 0.6
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ directory present"
      - "git_grep(pattern='PR #', ref='origin/launchpad', path='launchpad/docs/corpus') -> matches in capabilities/channels/channel-templates.md, layers/compute/sprig-runtime.md, capabilities/messaging/direct-message.md and others, each annotating a commit citation or narrative prose rather than a bare owner/repo#NNN or PR-URL evidence citation"
  - statement: "Merged pull request #1978 in this repository (launchpad-26/buzz) carries an Escalations section recording four items the authoring agent raised rather than decided, a Related issue section listing eleven Closes # lines (one per child issue of Feature #520), and a recorded merge commit oid of 1ed55e980b0043f92d9c652e6a39a8e49345389c at mergedAt 2026-08-31T08:25:01Z -- a real worked example of a stable, merged pull request whose merge commit is a fixed pin and whose Escalations section is a citable rationale record rather than settled fact."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1978, read via gh pr view at this node's authoring time"
  - statement: "Open pull request #2055 in this repository, at this node's authoring time, is in state OPEN with reviewDecision REVIEW_REQUIRED and carries three commits whose own messages describe successive, materially different approaches to the same fix: an original directory-wide gitleaks allowlist, replaced by a narrower literal-value allowlist after the commit's own message says an independent adversarial review found the first approach too broad, then extended again after the commit's own message says the narrower fix still missed history-walking findings the PR-diff scan checks -- demonstrating directly, rather than by assertion, that an open pull request's description and diff are not settled: this specific PR's own history shows its approach changing twice before any merge."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2055, read via gh pr view at this node's authoring time"
  - statement: "Issue #966's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#966 definition of done"
  - statement: "Parent Feature #620's body lists 32 child issues with the stated outcome 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures,' and its Out of scope line names 'implementation of the knowledge-crate runtime' as excluded from the whole Feature. The body itself lists child issues only by number, not by title."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, read via gh issue view at this node's authoring time"
  - statement: "Among Feature #620's 32 child issues, #962 is titled 'task: document ingestion/issue-comments.md' and #963 is titled 'task: document ingestion/issues.md' -- the plain-issue siblings this node's own boundary is drawn against -- and #970 is titled 'task: document ingestion/review-comments.md'; all three are OPEN (unmerged) at this node's authoring time."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#962, #963 and #970, each read individually via gh issue view at this node's authoring time"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-evidence
  - type: references
    target: corpus-standard-code-references
---

# Policy: citing a pull request

How to cite a **GitHub pull request** -- its description, its diff, its merge state, and
its closing-issue links -- as evidence for a corpus claim, and when a pull request is the
wrong citation entirely because the claim actually belongs to a plain issue or to one of
its own review comments.

## Scope and authority

**This node covers** which claims a pull request may be cited for, how its merge state
changes what a citation to it can honestly assert, how to cite its closing-issue links,
and the boundary against a plain GitHub issue and against an individual review comment
left on a pull request.

**It does not cover** the general FACT/INFERENCE/TEAM_KNOWLEDGE contract itself (the
evidence standard governs that, unconditionally, for every claim in the corpus), the
citation forms that name code -- a repository path, a `path:line` position, a pinned
GitHub file link (the code-references standard governs those), or citing a plain GitHub
issue or an individual review comment (named explicitly below, and owned elsewhere).

**Its authority is derived, not original.** The evidence standard already states the
central rule this node applies specifically to pull requests: a claim whose only source
is an issue, a pull request or a conversation has no openable file and no way to pin one,
so it must be `TEAM_KNOWLEDGE` with `provided_by` naming the source, never a `FACT` resting
on an `UNVERIFIED` citation. The code-references standard already states the mechanical
consequence: a GitHub pull-request URL is routed to the same non-fatal `UNVERIFIED`
channel as any other external link the validator cannot open. What this node adds is the
half neither of those states -- what a pull request's *merge state* changes about whether
a claim resting on it is stable, and how this fork's own PR conventions (`Closes #NNN`,
DCO sign-off, the `Escalations` field, merge-commit-only merging) bear on reading one as a
source.

**Where this node and `standards/evidence.md`, `standards/code-references.md`,
`node.schema.json`, or an accepted ADR disagree, those sources win** -- this node has
drifted and should be fixed.

| For | Read |
|---|---|
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract, and why an issue/PR/conversation citation is `TEAM_KNOWLEDGE` | `launchpad/docs/corpus/standards/evidence.md` |
| The citation forms that name code, and how each is pinned and resolved | `launchpad/docs/corpus/standards/code-references.md` |
| Citing an accepted decision record | `launchpad/docs/corpus/standards/decision-references.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| This fork's PR conventions in full | `launchpad/README.md`, "Opening a PR" section, `.github/PULL_REQUEST_TEMPLATE.md`, `launchpad/AGENT_PR_TEMPLATE.md` |
| Merge strategy and batch-PR sizing | `launchpad/decisions/ADR-0055-merge-commit-is-the-merge-strategy.md`, `launchpad/decisions/ADR-0054-one-feature-one-pr-no-size-cap.md` |

## Which kind of GitHub entity are you citing?

**A pull request is not an issue wearing a diff.** It carries a diff, a merge lifecycle
(open, merged, closed-without-merging), and review state that a plain issue never has.
Citing the wrong one asserts a claim under the wrong evidence shape.

| If the source is | The claim is | Cite it as |
|---|---|---|
| An issue's title, body or comments -- no diff, no merge lifecycle | scoped to `ingestion/issues.md` (#963) and `ingestion/issue-comments.md` (#962), both unmerged siblings at this node's authoring time | not this node's guidance |
| A pull request's own description, diff, merge state, or its own `Closes #NNN` lines | this node | see *MUST* below |
| An individual review comment left on a pull request -- a line comment, a review-summary comment | scoped to `ingestion/review-comments.md` (#970), unmerged at this node's authoring time | not this node's guidance |

**The #970 boundary is deliberate and stated rather than guessed at.** A pull request's
own description and diff are the artifact its author wrote and controls; a review comment
is a *different* author's response to it, with its own provenance and its own honesty
questions (was it addressed, superseded, resolved). Treating the two as one citation shape
would blur who said what. #970 is unmerged and this node cannot read its content, so this
node states only that the boundary exists and where it falls, not what #970 will say.

## MUST

| # | Requirement |
|---|---|
| **PR1** | A claim about what a pull request's description, body, or diff says or does **MUST** be classified `TEAM_KNOWLEDGE`, with `provided_by` naming the pull request (`owner/repo#NNN`), **never `FACT`**. No citation shape makes a pull request's content an openable file to the checker; forcing it into `FACT` on a URL citation produces exactly the `UNVERIFIED FACT` the evidence standard names as dishonest. Enforced by review only -- `validate.py` accepts an `UNVERIFIED`-routed `FACT` and prints a notice, it does not reject one. |
| **PR2** | A claim resting on an **OPEN** (unmerged) pull request **MUST** state that it is open in the claim's `statement`, and **MUST NOT** be worded as if its description or diff is settled. An open PR's content can still change before merge -- worked example #2055 (see evidence ledger) shows a real PR whose own commit history rewrote its approach twice before any merge occurred. |
| **PR3** | A claim that a **merged** pull request changed specific code **MUST** cite the merge commit SHA as a commit reference for the fact of the merge, and **separately** cite the changed file at that SHA (a repository path or a pinned GitHub file link, per `code-references.md`) to make the code-change claim itself `FACT`-eligible. Merging a PR does not turn the PR citation into a `FACT`-conferring one -- a commit reference is `UNVERIFIED` per `code-references.md` and `evidence.md` alike, merged or not; only the file at that revision is openable. |
| **PR4** | A claim about what a **merged** pull request's description currently says **MUST NOT** be treated as permanent. GitHub permits editing a pull request's body at any time, including long after merge; only the diff, pinned to the merge commit, is locked by history. `TEAM_KNOWLEDGE` naming the PR is the honest class regardless of merge state, and re-reading before relying on it again is the citing author's responsibility. |
| **PR5** | A claim that a pull request closes or implements a specific issue **MUST** cite the PR body's own `Closes #NNN` (or `Refs #NNN`) text as the evidence, not an assumed relationship inferred from the diff or from the issue and PR merely discussing the same subject. This fork's own convention requires that text to be written as plain text, never inside backticks or a code fence, because GitHub creates no link and closes nothing from a reference written in code -- so a corpus author checking whether a PR closes a given issue must read the raw closing-keyword line, not infer it from a fenced mention. |
| **PR6** | A pull request that is **closed without merging MUST** be cited, if cited at all, only as evidence of what was proposed and not adopted -- **never** as evidence that a change exists in the codebase. Its closed-not-merged state **MUST** be named in the `statement`. |
| **PR7** | A claim resting on an **individual review comment** left on a pull request, as opposed to the pull request's own description, diff, merge state, or closing-issue lines, **MUST NOT** be sourced under this node's guidance. Route it to `ingestion/review-comments.md` (#970) once it exists; until then, treat it as an explicit gap (see *Scope and omissions*), not as covered by analogy to PR1-PR6. |

## SHOULD

| # | Guidance |
|---|---|
| **Q1** | A `statement` citing a pull request **SHOULD** record the full `owner/repo#NNN` form, not a bare number, so a later reader can re-fetch its current state without first discovering which repository is meant -- state itself is exactly what PR2 and PR4 say can no longer be assumed unchanged. |
| **Q2** | A `statement` **SHOULD** quote the exact sentence relied on from the pull request's description, the same practice `decision-references.md` recommends for a decision record, rather than only linking the PR and trusting a later reader to find the same passage. |
| **Q3** | When the underlying claim is really about **what code changed**, prefer citing the file at the merge commit (per PR3) over the pull request alone -- a repository path is checked structurally by the validator; a pull-request URL is not, per `code-references.md`'s own citation-verdict table. |
| **Q4** | When the cited pull request carries an `Escalations` field -- this fork's `AGENT_PR_TEMPLATE.md` has one; `.github/PULL_REQUEST_TEMPLATE.md` (human-authored PRs) does not, and carries a differently-scoped `Deferred blockers` field instead -- and the claim is about what was flagged, deferred, or left as a judgement call rather than decided, cite that section directly as `TEAM_KNOWLEDGE` -- it is the author's own attributed rationale record, not something to reconstruct secondhand from the diff. |

## Enforcement

**Nothing mechanical distinguishes a pull request's merge state, or its content, from any
other external URL.** `validate.py`'s citation classifier recognises a pull-request URL as
a URL that does not match its repository-link pattern (no `blob`/`raw`/`tree`/`blame`/
`commits`/`edit` segment applies to a PR path), and routes it to the same `UNVERIFIED`
channel as a non-GitHub link, a commit reference, a graph edge, or a tool result -- printed,
never fatal, never contacting GitHub. This holds identically whether the PR is open,
merged, or closed without merging; the checker has no concept of any of those states.

**What a green `validate.py` run does NOT establish about a pull-request citation:**

| Not established | Consequence |
|---|---|
| That the cited pull request exists at all | A PR number that was never opened, or belongs to a different repository, passes identically to a real one |
| That the PR's description says what the `statement` says | Structural checking only; nothing compares the two |
| That an OPEN PR's content hasn't changed since the citation was written | Never re-fetched, never compared against current state |
| That a `Closes #NNN` line was written as plain text rather than inside a fence | The validator reads corpus citations, not PR body text -- PR5's requirement is enforced by whoever reviews the corpus node, not by this checker |
| That a `TEAM_KNOWLEDGE` entry citing a PR is honestly attributed rather than invented | `provided_by` is checked only for being a non-empty string |

**Enforcement is the pull-request review that merges this corpus node**, the same
enforcement model every standard in this corpus already names for its review-only half.
A reviewer checking a node that cites a pull request: confirms the citation is
`TEAM_KNOWLEDGE`, not `FACT` (PR1); confirms an open PR's instability is stated, not
assumed away (PR2); confirms a merged-PR code claim is backed by a separate file citation,
not the PR alone (PR3); and confirms a closing-issue claim quotes the PR's own text (PR5).

## Exceptions and escalation

**There is no exemption from PR1-PR7.** They restate, for pull requests specifically, a
rule the evidence and code-references standards already hold every citation in the corpus
to; a claim that cannot meet one of them is not a candidate for an exception, it needs a
different citation or must be withdrawn per `evidence.md`'s own three-outcomes rule.

**A disputed application -- for example, whether a given claim is really "about the PR's
content" (PR1) or "about the code at its merge commit" (PR3) -- is a judgement, not an
exception.** The author records the tension in the corpus pull request and the reviewer
decides. A repeated disagreement is filed as an issue against this node.

**A case none of PR1-PR7 covers is escalated, not invented.** Raise it as an issue against
parent Feature #620, naming the pull-request citation scenario that was missing and why
PR1-PR7 did not reach it -- individual review comments (#970) are the one gap already
named and routed, not escalated fresh each time it recurs.

## Scope and omissions

**This node covers** which claims a GitHub pull request may be cited for, how its merge
state (open, merged, closed-without-merging) changes what a citation to it can honestly
assert, how to cite its closing-issue links per this fork's own `Closes #NNN` convention,
and the boundary against a plain issue and against an individual review comment.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citing a plain GitHub issue's title, body or comments | `ingestion/issue-comments.md` (#962) and `ingestion/issues.md` (#963), both unmerged at this node's authoring time |
| Citing an individual review comment left on a pull request | `ingestion/review-comments.md` (#970), unmerged at this node's authoring time |
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract and how classes are chosen for any other kind of claim | `launchpad/docs/corpus/standards/evidence.md` |
| The citation forms that name code -- repository paths, positions, pinned GitHub file links | `launchpad/docs/corpus/standards/code-references.md` |
| Citing an accepted decision record | `launchpad/docs/corpus/standards/decision-references.md` |
| How review of a corpus change is itself conducted | referenced but not owned by this node; see `AGENTS.md` |
| Implementation of the knowledge-crate runtime that would consume these citations programmatically | explicitly out of scope for parent Feature #620 |

**No edge to `ingestion-issues`, `ingestion-issue-comments`, or `ingestion-review-comments`.**
None of the three exists on `origin/launchpad` at this node's authoring time (confirmed by
`git ls-tree`, not assumed), so none is a legitimate `relationships` target. Declaring one
now would validate on this branch and become a hard error on merge, the exact hazard
`AGENTS.md` step 9 names. Adding these edges is a follow-up once those siblings merge, not
an oversight here.

**Relationships declared, and why.** `depends-on: corpus-agents` -- this node's evidence
and citation-class rules are drawn from `AGENTS.md`'s conventions, not original to itself.
`depends-on: corpus-standard-evidence` -- PR1's central rule (an issue/PR/conversation
citation is `TEAM_KNOWLEDGE`, never `FACT`) is stated there first and quoted, not
reinvented, here; this node's own claims depend on that text staying current.
`references: corpus-standard-code-references` -- supporting context for PR3's requirement
to cite the changed file separately from the PR, and for the shared fact that a pull-request
URL and a repository link are checked by different, disjoint rules.

**Expected but not verified when this node was written:**

- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **Whether `ingestion/issues.md`, `ingestion/issue-comments.md`, or `ingestion/review-comments.md`,
  once drafted, will declare a relationship toward this node** is each sibling's own edit
  to make, not decided here.
- **Whether GitHub's `closingIssuesReferences` API field (as opposed to the PR body's own
  `Closes #NNN` text, which PR5 requires citing instead) behaves identically regardless of
  which branch a PR targets** was not tested in preparing this node and is not asserted
  either way; PR5 sidesteps the question by requiring the body text itself as the citation.
- **Whether every open pull request behaves like worked example #2055** -- rewriting its
  approach across several commits before merge -- was not established generally; #2055 is
  cited as one real instance proving open-PR content *can* change, not as a claim about how
  often it does.
