---
id: ingestion-issues
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
  - statement: "node.schema.json's type enum includes ingestion among its thirteen members, and describes the field as naming the corpus surface a node documents, not the documentation form its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no ingestion/ directory at all, so this node has no merged sibling under ingestion/ to follow as type precedent; the same tree lists AGENTS.md (id corpus-agents), agents/invariants.md (id agents-invariants), standards/evidence.md (id corpus-standard-evidence), standards/decision-references.md (id corpus-standard-decision-references) and templates/policy.md (id corpus-template-policy), each confirmed by reading its own front matter."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ path present; AGENTS.md, agents/invariants.md, standards/evidence.md, standards/decision-references.md, templates/policy.md all present, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Issue #963's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them -- the same checklist templates/policy.md itself formalizes into six required sections."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#963 definition of done"
  - statement: "standards/evidence.md states, under its own heading 'When the only source is an issue, a pull request, or a conversation': 'Do not force it into a FACT on a URL or a tool-result citation... Use TEAM_KNOWLEDGE with provided_by naming the issue, the pull request or the person. That is what the class is for, and ADR-0029 requires GitHub history to stay attributed rather than be promoted to fact.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "standards/decision-references.md's own scope-and-authority section states it covers 'which claims a decision record may be cited for, how to cite one, what to do when two accepted decisions conflict, what to do when a cited decision is superseded' -- an accepted decision record, not the raw GitHub issue that may have argued the question before a record existed -- and its MUST 4 requires opening the record's front-matter status before citing it for an intent claim, because 'proposed and superseded records live in the same directory under the same filename pattern as accepted ones.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "standards/code-references.md's own scope-and-authority section states it governs 'every citation, in any node's evidence ledger, that names code in a repository: which forms are permitted, which are forbidden, how they are pinned and positioned' -- a subject that does not include a GitHub issue, which names no repository file at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "launchpad-26/buzz#307 carries the type:adr label; its own GitHub issue timeline records exactly five 'labeled' events, all timestamped 2026-08-21T12:03:15Z to 2026-08-21T12:03:47Z (the minutes after the issue was opened), and zero 'unlabeled' or 'reopened' events at any later time -- this issue's own label set was set once, at creation, and never changed again."
    entry_class: FACT
    evidence:
      - "gh_api(repos/launchpad-26/buzz/issues/307/timeline) -> five labeled events dated 2026-08-21T12:03:15Z-2026-08-21T12:03:47Z (type:adr, area:process, by:agent, area:agents-and-automation, needs-decision); zero unlabeled or reopened events"
  - statement: "launchpad-26/buzz#307's state field reads CLOSED with closedAt 2026-08-31T08:25:07Z, and its closedByPullRequestsReferences field names exactly one pull request, #1978, whose own title reads 'docs(decisions): accept the 11 vendor-drop ADRs -- daily-cadence decision set (Feature #520)' and whose own body states it 'accepts all 11 vendor-drop / change-agent ADRs under Feature #520, each decided individually by Jeffrey in session on 2026-08-31' -- one merge closing eleven issues at once, #307 among them."
    entry_class: FACT
    evidence:
      - "gh_issue_view(307, repo='launchpad-26/buzz', field='closedByPullRequestsReferences') -> [{number: 1978}]"
      - "gh_pr_view(1978, repo='launchpad-26/buzz') -> title 'docs(decisions): accept the 11 vendor-drop ADRs -- daily-cadence decision set (Feature #520)', body opens 'Accepts all 11 vendor-drop / change-agent ADRs under Feature #520, each decided individually by Jeffrey in session on 2026-08-31'"
  - statement: "GitHub's issue-events vocabulary, exercised directly by #307's own timeline above, models closed, reopened, labeled and unlabeled as distinct, independently repeatable event types rather than a single set-once state -- the same repository's own tooling can therefore relabel or reopen an issue at any time after this node's own citation of it, even though #307 itself happened not to be."
    entry_class: INFERENCE
    evidence:
      - "gh_api(repos/launchpad-26/buzz/issues/307/timeline) -> distinct event-type field values labeled, unlabeled, closed, reopened, cross-referenced observed in one timeline response"
    confidence: 0.85
  - statement: "Issue #957's own body states its objective as 'Create launchpad/docs/corpus/ingestion/decision-extraction.md as the single canonical procedure node for decision extraction' -- a noticing-and-screening step for whether a decision exists in a source generally, not the citation mechanics of an issue's own fields."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#957 body, Objective section"
  - statement: "Issue #962's own body states its objective as 'Create launchpad/docs/corpus/ingestion/issue-comments.md as the single canonical policy node for issue comments' -- a policy about individual comments on an issue, distinct from this node's subject: the issue's own title, body, state and labels."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#962 body, Objective section"
  - statement: "node.schema.json constrains provided_by to a non-empty string only, and validate.py's citation classifier never contacts GitHub, so nothing checks that a provided_by value names a real issue, that an issue's state was actually re-read before a claim was finalized, or that an evidence entry names which of an issue's title, body, state or labels it drew from."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
relationships:
  - type: depends-on
    target: corpus-standard-evidence
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-decision-references
  - type: references
    target: corpus-agents
---

# Policy: citing a GitHub issue

How a corpus node cites a **GitHub issue as a whole** — its title, body, current
state, and labels, and the pull request that closed it — as evidence for a claim, and
where that citation stops being honest as the issue moves.

## Scope and authority

**This node governs** an evidence entry whose source is an issue's own top-level
fields: `title`, `body` (including a Definition-of-Done or acceptance-criteria
checklist inside it), `state` (open/closed), `labels`, and the pull request(s) that
closed it. It states how such an entry must be classified, what it must record about
the issue's mutability, how a structured checklist claim differs from a free-text
discussion claim, and how a `type:adr`-labeled issue interacts with a settled-decision
claim.

**Its authority is derived, not original.** `standards/evidence.md` already states the
governing rule in full: an issue has no openable file and no way to pin one, so a claim
resting on it must be `TEAM_KNOWLEDGE` with `provided_by` naming the issue, never a
`FACT` propped up on a URL or tool-result citation. This node does not restate that
rule as its own finding — it depends on it (declared below) and adds what
`standards/evidence.md` does not: the specific hazards of an issue's own fields, which
that document names only as one example among several no-openable-file sources.

**Where this document and `standards/evidence.md` disagree, `standards/evidence.md`
wins** — this node has drifted and should be fixed. Where this document and
`standards/decision-references.md` disagree about citing an *accepted decision
record*, that document wins on its own subject; this node never governs citing an ADR
once one exists.

| For | Read |
|---|---|
| The general TEAM_KNOWLEDGE-for-no-openable-file rule this node depends on | `standards/evidence.md` |
| Citing an accepted decision record once one exists | `standards/decision-references.md` |
| Noticing and screening whether a decision exists in a source (including an issue thread) before deciding whether to cite it at all | `ingestion/decision-extraction.md` (#957, sibling, not yet merged) |
| Citing an individual **comment** on an issue | `ingestion/issue-comments.md` (#962, sibling, not yet merged) |
| Citing code, tests, or configuration | `standards/code-references.md` |
| Creating, updating and retiring a node | `AGENTS.md` |

## Boundary: what this node does not cover, stated before the rules

Four adjacent documents cover ground this node's subject sits directly beside. Getting
the boundary wrong produces either a duplicate or a gap, so each is named here rather
than left for a reader to infer.

**Versus `ingestion/issue-comments.md` (#962).** #962's own body states its objective
as documenting "the single canonical policy node for issue comments." This node's
subject is the issue's *own* fields — title, body, state, labels, closing PR — never
an individual comment posted underneath it. A comment thread is where a decision is
often actually announced (`ingestion/decision-extraction.md`'s own worked example,
`launchpad-26/buzz#307`, found the real decision in a comment while the issue body's
placeholder stayed unedited) — but reading that comment and citing it is #962's
procedure, not this one's. This node's MUST 6 below states the same boundary from the
other side: a claim resting on what a comment says is not this node's to license.

**Versus `standards/decision-references.md`.** That node governs citing an *accepted
decision record* — an ADR file under `launchpad/decisions/`, once one exists — for a
claim about what is intended or authorized. This node governs citing the *issue*
itself, before or regardless of whether a decision record exists. A `type:adr`-labeled
issue is the clearest overlap case, and MUST 5 below draws the line: this node's
`TEAM_KNOWLEDGE` convention covers a claim that a question was *raised* or *discussed*
in the issue; the moment a claim is about what was *decided*, the issue stops being the
right citation and the resulting ADR record — read under `standards/decision-references.md`
— becomes it.

**Versus `ingestion/decision-extraction.md` (#957).** #957's own body states its
objective as documenting "the single canonical procedure node for decision
extraction" — recognizing, while reading a source for another reason, that a decision
worth citing exists there, and screening whether it is settled. That is a
*noticing* step, upstream of this node. This node starts one step later: an author has
already decided to cite the issue itself for some claim, and needs to know how.
Neither node restates the other's procedure.

**Versus `standards/code-references.md`.** That node's own scope-and-authority section
states it governs "every citation, in any node's evidence ledger, that names code in a
repository." A GitHub issue names no repository file, so nothing in that node's subject
applies here, and nothing here duplicates it.

## MUST

1. **An evidence entry whose only source is an issue's title, body, state, or labels
   MUST carry `entry_class: TEAM_KNOWLEDGE`, with `provided_by` naming the issue** (for
   example `launchpad-26/buzz#307`) **— never `FACT` resting on a URL or tool-result
   citation.** This is `standards/evidence.md`'s own rule; it is restated here as the
   governing case for this node's subject, not as a second, independent finding.
2. **The `statement` MUST record the issue's `state` (open or closed) and the date, or
   the commit the node itself records, at which that state was read.** An issue's
   `state` is not a fixed property of the issue the way a file's content is fixed at a
   commit — it is read live, and the entry must say when it was read so a later
   reader can tell whether it might have changed since.
3. **A claim whose truth depends on an issue's *current* state or label set MUST be
   re-checked with a fresh `gh issue view` (or equivalent) call immediately before the
   draft is finalized — not left resting on a read taken earlier in the same authoring
   session.** GitHub's own issue-events vocabulary models `closed`, `reopened`,
   `labeled` and `unlabeled` as independently repeatable events, not a value fixed at
   authoring time (see the front-matter INFERENCE entry, grounded in `#307`'s own
   timeline); a state read at the start of a session is not evidence of the state at
   the moment the node is committed.
4. **A claim drawn from an issue's Definition-of-Done or acceptance-criteria checklist
   MUST be worded as a claim about what the issue specifies or requires, and MUST NOT
   be merged with a claim drawn from the same issue's free-text discussion.** A
   checklist item is structured, quasi-normative content the issue's author committed
   to as a condition of closing it; a paragraph of discussion is narrative that may
   propose, question, or argue against exactly that requirement. Citing both under one
   `statement` lets the checklist's authority cover the narrative's uncertainty.
5. **An issue carrying the `type:adr` label MUST NOT be cited as authority for a
   settled decision or intent claim, regardless of its `state`.** `TEAM_KNOWLEDGE`
   attributed to such an issue may support a claim that a question was *raised* or
   *discussed* there (per MUST 1); it may never support a claim about what was
   *decided*. Once a decision is recorded, the resulting ADR file is the correct
   citation for that claim, under `standards/decision-references.md` — an issue closing
   does not by itself mean a decision landed, and `#307` is the worked counter-example:
   its body's own placeholder Decision-outcome section reads unedited even after the
   question was actually settled in a comment, days before the issue closed.
6. **An evidence entry MUST name which of the issue's own fields it draws from — title,
   body, state, or labels — and MUST NOT rest on an individual comment.** These are
   structurally different fields fetched by different calls (`gh issue view` for the
   first three, a separate comments endpoint for the fourth), and a citation that does
   not say which one was read cannot be checked by a reviewer who was not there. A
   claim resting on a comment is `ingestion/issue-comments.md`'s (#962) subject, not
   this node's.
7. **A citation to an issue's closing pull request MUST NOT be treated as confirming
   that the PR's diff addresses that issue's specific concern, when the same PR closes
   more than one issue.** `#307`'s own closing PR, `#1978`, closed eleven issues in one
   merge; the PR's existence establishes that *something* in it was judged to resolve
   `#307`, not which commit or file did. A claim that a *specific* change addresses the
   issue needs its own citation to that change, separate from the closing-PR reference.

## SHOULD

- **Prefer `gh issue view <n> --json <fields>` naming explicit fields over unstructured
  `gh issue view` output**, so the exact field an entry drew from is reproducible by a
  later reader running the same command.
- **Quote the specific sentence or checklist line relied on in the `statement`**, rather
  than summarizing the whole issue. A summary drifts from the source silently; a
  quotation is checkable against it.
- **Re-read the issue rather than trusting an earlier read from the same session**,
  even when nothing seems to have changed. MUST 3 makes this binding for a
  state-dependent claim; this extends the same caution as working practice to any
  claim, because the cost of a stale read and the cost of one more `gh` call are not
  close to symmetric.
- **Note in the `statement` when an issue's label set could plausibly change** — for
  example, an open issue still under active discussion — rather than treating every
  label as settled. A closed issue's labels are less likely to move again, though
  nothing here or in `standards/evidence.md` establishes that as a rule; it is offered
  as judgement, not as a MUST.

## Enforcement

**Nothing automated checks any requirement on this page.** Verified directly:
`node.schema.json` constrains `provided_by` to a non-empty string and nothing more, and
`validate.py`'s citation classifier never contacts GitHub — it cannot confirm that a
`provided_by` value names a real issue, that an issue's state was actually re-read
before a claim was finalized, that a checklist claim and a discussion claim were kept
separate, or that an entry names which field it drew from. A `TEAM_KNOWLEDGE` entry
attributed to a nonexistent issue number validates exactly like one attributed to a
real one.

**What a green validation run does not establish about a node citing an issue:**

| Not established | Consequence |
|---|---|
| That `provided_by` names a real, existing issue | Any non-empty string satisfies the schema |
| That the recorded `state` was current at the moment of citation, or ever re-checked | Never fetched, never compared against GitHub |
| That a DoD/checklist claim and a discussion claim were kept in separate entries | Both validate identically as `TEAM_KNOWLEDGE` |
| That a `type:adr` issue's citation supports only "raised/discussed" and not "decided" | The schema does not distinguish claim intent; only a reviewer reading the `statement` can |
| That a closing-PR citation names the specific change, not just *a* PR that happened to close the issue | The validator does not resolve GitHub URLs or PR content at all |

**Enforcement is the pull-request review**, the same mechanism every corpus standard
depends on for the half no schema can hold. A reviewer checking a node that cites an
issue: opens the issue and confirms `provided_by` names it accurately; confirms the
`statement` states an observed state and date; confirms a checklist claim is not
blended with a discussion claim; confirms a `type:adr` citation stops at "raised or
discussed" and does not smuggle in "decided"; and confirms a closing-PR citation is not
standing in for a specific-change citation it has not made.

## Exceptions and escalation

**There is no exception from the `TEAM_KNOWLEDGE` classification in MUST 1.** An issue
never becomes an openable file by virtue of being important, frequently cited, or
long-closed.

**When two issues, or an issue and another source, disagree about the same claim
type**, this node does not introduce a new resolution procedure — `ADR-0029`'s ranking
and `standards/evidence.md`'s escalation apply unchanged: record the contradiction, set
the node's `status` to `flagged`, and leave it for a human rather than picking a side.

**A case this node does not reach is escalated, not invented.** Raise it as an issue
against parent Feature #620 describing the citation that was needed and could not be
written honestly under the rules above. Do not widen this node's MUSTs locally to
cover it.

## Relationships in this node's front matter

- **`depends-on: corpus-standard-evidence`.** This node's central rule — `TEAM_KNOWLEDGE`
  with `provided_by`, never `FACT` on a URL or tool result — is `standards/evidence.md`'s
  own stated rule for any no-openable-file source, and this node's claims depend on that
  rule staying current to remain true; it is not this node's own finding.
- **`implements: corpus-template-policy`.** This node carries the six required
  sections that template names — scope/authority, MUST, SHOULD, enforcement,
  exceptions/escalation, scope/omissions — as a policy-shaped instance of it, per
  `relationships.schema.json`'s own worked example for `implements`.
- **`references: corpus-standard-decision-references`.** The boundary above depends on
  what that node says about citing an accepted decision, as supporting context; this
  node's own claims do not depend on that document's text staying fixed the way MUST 1
  depends on `standards/evidence.md`'s.
- **`references: corpus-agents`.** `AGENTS.md`'s node-authoring evidence discipline is
  the procedure this node's citations ultimately feed into; this node's own rules stay
  accurate even if `AGENTS.md`'s later wording changes, so the coupling is loose rather
  than a dependency, the same reasoning `ingestion/decision-extraction.md` gives for the
  identical edge.
- **No edge to `ingestion/decision-extraction.md` (#957) or `ingestion/issue-comments.md`
  (#962).** Neither is merged on `origin/launchpad` at this node's authoring time
  (confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`,
  recorded in the front matter), and a `relationships[].target` naming an id no loaded
  node carries is a hard validation error. Both are named in prose above, by title, as
  the boundary requires; the edges are a follow-up once both merge.

## Scope and omissions

**This node covers** how to cite a GitHub issue's own title, body (including a
Definition-of-Done or acceptance-criteria checklist inside it), state, labels, and
closing pull request as evidence for a claim: the required classification, the
mutability an issue's state and labels carry that a pinned file does not, the boundary
against a `type:adr` issue standing in for its own eventual decision record, and the
boundary against a closing PR standing in for a specific-change citation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citing an individual comment on an issue | `ingestion/issue-comments.md` (#962, not yet merged) |
| Citing an accepted decision record once one exists | `standards/decision-references.md` |
| Noticing and screening whether a decision exists in a source generally, including an issue thread | `ingestion/decision-extraction.md` (#957, not yet merged) |
| The general evidence contract, citation-shape table, and how classes are chosen | `standards/evidence.md` |
| Citing code, tests, or configuration | `standards/code-references.md` |
| How a specification becomes "ratified" | Undefined in this repository — `standards/decision-references.md`'s own gap |
| Encoding any rule in this node into the schema or validator | No issue currently owns this for this node's specific subject |

**Expected but not verified when this node was written:**

- **No corpus node yet exists that actually cites an issue under this node's rules.**
  Every rule above is written from `standards/evidence.md`'s existing convention and
  from the worked examples of `#307`/`#1978`, `#957` and `#962`'s own bodies, rather
  than from an author having applied MUST 1–7 end to end and found them followable.
- **Whether `#307`'s label set staying fixed after creation is typical or unusual for
  this repository** was not established beyond that one issue; the INFERENCE in the
  front-matter ledger rests on GitHub's general issue-events vocabulary supporting
  repeatable `labeled`/`unlabeled`/`reopened` events, not on a second worked instance
  of an issue in this repository actually being relabeled or reopened after citation.
- **Whether `#957` and `#962`, once built, declare the inverse edges this node expects**
  (`ingestion/decision-extraction.md` pointing here for the citation step that follows
  its own screening step, and `ingestion/issue-comments.md` pointing here for the
  issue-versus-comment boundary) is those nodes' own edit to make, not something this
  node can decide on their behalf.
