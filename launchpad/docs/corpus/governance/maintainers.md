---
id: governance-maintainers
type: governance
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
  - statement: "No MAINTAINERS or MAINTAINERS.md file exists at any path in this repository; the tracked-file search for a roster returns only .github/CODEOWNERS and GOVERNANCE.md."
    entry_class: FACT
    evidence:
      - "git_ls_files(pattern='maintainer|governance|codeowner|owners|roster|team') -> .github/CODEOWNERS, GOVERNANCE.md, and only crates/desktop source files matching 'team'; ls MAINTAINERS MAINTAINERS.md CODEOWNERS -> No such file or directory, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "GOVERNANCE.md is a single line whose entire content is a link to block/.github's GOVERNANCE.md -- it delegates governance to Block's open-source programme and states nothing about this fork."
    entry_class: FACT
    evidence:
      - "GOVERNANCE.md"
  - statement: ".github/CODEOWNERS is one line, '* @block/buzz-oss-team', assigning every path in the repository to a team in the block organization."
    entry_class: FACT
    evidence:
      - ".github/CODEOWNERS"
  - statement: "That CODEOWNERS line is invalid in this fork and valid upstream: GitHub's codeowners-errors endpoint reports 'Unknown owner' on line 1 for launchpad-26/buzz, with the suggestion that the team must exist, be publicly visible and have write access, while the same endpoint for block/buzz returns an empty errors array."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/codeowners/errors') -> errors[0] with line 1, column 3, kind 'Unknown owner', path '.github/CODEOWNERS'; gh_api('repos/block/buzz/codeowners/errors') -> empty errors array"
  - statement: "The launchpad-26 organization carries exactly two teams, maintainers and students, and ADR-0056's provenance records both as already existing with repository access."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0056-fork-owned-drop-branch-ci.md"
      - "gh_api('orgs/launchpad-26/teams', jq='.[].slug') -> maintainers, students"
  - statement: "The launchpad branch is branch-protected on launchpad-26/buzz."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad', jq='{name,protected}') -> name launchpad, protected true"
  - statement: "The branch-protection detail endpoint is unreadable with the token used to author this node, because that token holds maintain rather than admin on the repository; the 404 is a permissions artefact and not evidence that protection is absent."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz', jq='.permissions') -> admin false, maintain true, pull true, push true, triage true; gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> message 'Not Found', status 404"
  - statement: "Three GitHub repository permission levels are in use across the repository's collaborators -- admin, maintain and write -- so the fork distinguishes maintainer-grade access from ordinary write access at the platform level rather than only by convention."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/collaborators', paginate=True, jq='.[].role_name') -> three distinct role_name values: admin, maintain, write"
  - statement: "launchpad/AGENTS.md section 5 rule 1 distinguishes humans from agents by act rather than by identity: an agent may draft any issue, PR or ADR on its own authority, but may not decide an ADR outcome, approve a PR, merge one, or close another agent's escalation on its own judgement."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "ADR-0052 permits an agent to exercise three of those four acts on a human's behalf only under five conditions held together, including that the instruction be quoted verbatim in the artifact and the instructing human named there, and it requires an agent-submitted approval to be self-identifying."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "launchpad/AGENTS.md requires the by:agent label on every issue and pull request an agent creates, because agents run under a human's token and GitHub's author field therefore cannot distinguish them; by:agent is defined in launchpad/labels.yml."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "launchpad/labels.yml"
  - statement: "ADR-0038 restricts advancing main to a small named group of humans, states that only a repository admin can change the restriction list, and deliberately names no accounts on the grounds that the record has no standing to grant push access; it also requires each holder be named individually rather than by team so that widening the list is a visible act."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0038-named-humans-advance-vendor-branch.md"
  - statement: "ADR-0033 assigns CODEOWNERS the job of requesting human review when an ordinary pull request touches the upstream-owned boundary, records that launchpad had no required status checks at the time so the paired drift check is advisory, and names task #1428 as owning the implementation, the path scope and the notification surface."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0033-divergence-review-and-drift-assurance.md"
  - statement: "Squash and rebase merging are disabled on launchpad-26/buzz and merge commits are the only method the platform offers, which launchpad/AGENTS.md section 6 records as ADR-0055's settlement."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "gh_api('repos/launchpad-26/buzz') -> allow_merge_commit true, allow_rebase_merge false, allow_squash_merge false"
  - statement: "Upstream's CONTRIBUTING.md, tracked unchanged in this fork, tells a contributor that 'Once approved, a maintainer will squash-merge your PR' -- a statement about a maintainer's act that the fork's own platform settings make impossible here."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "Changes under launchpad/docs/corpus are validated in CI by a fork-owned workflow, so the corpus contract is enforced mechanically rather than by a maintainer reading each node."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "The governance directory does not exist on origin/launchpad at this node's authoring revision, and sibling tasks #907 (governance/codeowners.md) and #910 (governance/decision-authority.md) are both open and unmerged, so neither is a valid relationship target."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> agents, architecture, capabilities, development, layers, schema, standards, templates -- no governance; gh issue view 907/910 --repo launchpad-26/buzz -> both OPEN"
  - statement: "Because .github/CODEOWNERS resolves to an unknown owner in this fork, no code-owner review routing is in effect on launchpad-26/buzz today, and ADR-0033's first assurance is therefore not operating as that record describes."
    entry_class: INFERENCE
    evidence:
      - ".github/CODEOWNERS"
      - "launchpad/decisions/ADR-0033-divergence-review-and-drift-assurance.md"
      - "gh_api('repos/launchpad-26/buzz/codeowners/errors') -> Unknown owner on line 1"
    confidence: 0.75
  - statement: "This fork has no fork-authored maintainer roster in any tracked file; the operative roster is GitHub organization and team membership, administered in the launchpad-26 organization's settings rather than in the repository."
    entry_class: INFERENCE
    evidence:
      - "GOVERNANCE.md"
      - ".github/CODEOWNERS"
      - "launchpad/decisions/ADR-0056-fork-owned-drop-branch-ci.md"
      - "gh_api('orgs/launchpad-26/teams', jq='.[].slug') -> maintainers, students"
    confidence: 0.85
  - statement: "Issue #913 requires this node to state the scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#913 definition of done"
relationships:
  - type: implements
    target: corpus-template-policy
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-normative-language
---

# Policy: maintainers of the launchpad-26/buzz fork

Who maintains this fork, what that role carries, and where the answer actually lives.
The short version, and the reason this node exists: **the fork has no maintainer roster
of its own.** The two files a reader would reach for — `GOVERNANCE.md` and
`.github/CODEOWNERS` — are both inherited from upstream, and one of them does not work
here. What does the work instead is GitHub organization and team membership, which is
administered outside this repository and is not a tracked file at all.

This node records that state with evidence and names the gaps. It does not invent a
maintainer policy the fork has not adopted.

**Keywords.** MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are used as
`corpus-standard-normative-language` defines them; that standard is referenced, not
restated.

## Scope and authority

**This node governs** how a reader — human or agent — determines who maintains
`launchpad-26/buzz`, what a maintainer may do that a non-maintainer may not, and how a
claim about maintainership must be evidenced when it is written down. It covers the
mechanisms that carry the role today: GitHub repository permission levels, organization
team membership, branch protection on `launchpad`, and the human/agent distinction
`launchpad/AGENTS.md` draws over acts rather than accounts.

**It does not cover** review routing — which reviewer a given path pulls in, and the
`CODEOWNERS` mechanism that would do it — nor who holds authority to decide a given
question. Those are two separate subjects with two separate owners; see *Scope and
omissions*.

**Its authority is derived, not original.** This node grants nobody anything and
withdraws nothing. Every requirement below restates an obligation that already binds,
from one of four sources:

- **The GitHub platform**, which holds repository permission levels, organization team
  membership, and branch protection. Permission is a platform fact; no document can
  confer it and no document can revoke it.
- **Accepted decision records** under `launchpad/decisions/` — principally ADR-0038
  (who may advance `main`), ADR-0052 (delegated authority), ADR-0033 (divergence review)
  and ADR-0056 (which of those survive the no-org-permissions constraint).
- **`launchpad/AGENTS.md`**, which states the fork's operating rules and the human/agent
  distinction.
- **`launchpad/docs/corpus/AGENTS.md`**, from which this node's evidence obligations
  derive — declared as `depends-on` in the front matter above.

**Precedence.** Where this node and the **platform** disagree, the platform wins: the
document has gone stale and must be fixed. Where it and an **accepted ADR** disagree,
the ADR wins. Where it and **`launchpad/AGENTS.md`** disagree, that file wins for
operating rules. Where it and a **more specific governance node** disagree on that
node's own subject — routing, decision authority — the specific node wins once it
exists. This node is last in every one of those orderings, by design.

| For | Read |
|---|---|
| Which reviewer a path pulls in, and the `CODEOWNERS` mechanism | #907 (`governance/codeowners.md`), unmerged |
| Who holds authority to decide a given question | #910 (`governance/decision-authority.md`), unmerged |
| The conditions under which an agent may approve or merge | `launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md` |
| Who may advance `main` to a vendor point, and why no accounts are named | `launchpad/decisions/ADR-0038-named-humans-advance-vendor-branch.md` |
| Divergence review on the upstream boundary | `launchpad/decisions/ADR-0033-divergence-review-and-drift-assurance.md` |
| The fork's operating rules and the human/agent distinction | `launchpad/AGENTS.md` |
| Block's open-source programme governance (upstream, not this fork) | `GOVERNANCE.md`, which is a one-line redirect |
| Evidence classes and citation shapes for a corpus node | `launchpad/docs/corpus/AGENTS.md` |

## Ground truth: what actually exists

Established by inspection at the recorded revision, assuming nothing. Each row was
checked; none was inferred from the presence of a sibling.

| Artefact | State |
|---|---|
| `MAINTAINERS` | **Does not exist**, at any path |
| `MAINTAINERS.md` | **Does not exist**, at any path |
| `GOVERNANCE.md` | Exists. **One line.** Its entire content is a link to `block/.github`'s `GOVERNANCE.md` — Block's programme-level governance, describing upstream, saying nothing about this fork |
| `.github/CODEOWNERS` | Exists. **One line**, `* @block/buzz-oss-team` — every path assigned to a team in the `block` organization |
| A roster under `launchpad/` | **Does not exist.** No file under `launchpad/` names a maintainer set |
| `launchpad-26` organization teams | `maintainers` and `students` — the operative roster, held on the platform, not in the repository |

**`.github/CODEOWNERS` is invalid in this fork.** This is the load-bearing fact of the
whole node, and it was verified against the platform rather than read off the file:

```
gh api repos/launchpad-26/buzz/codeowners/errors
  -> Unknown owner on line 1: make sure the team @block/buzz-oss-team exists,
     is publicly visible, and has write access to the repository

gh api repos/block/buzz/codeowners/errors
  -> {"errors":[]}
```

The same one-line file is valid upstream and invalid here, for the obvious reason:
`buzz-oss-team` is a team in the `block` organization, and this repository lives in
`launchpad-26`. A fork inherits the file; it does not inherit the org the file names.

**Fixing it is already owned.** ADR-0033 names task **#1428** as owning the divergence
review implementation, its path scope and its notification surface. A reader who arrives
here wanting the file fixed should go to #1428, not file a duplicate.

**Both inherited files fail the same way.** `GOVERNANCE.md` and `.github/CODEOWNERS`
are each a pointer at the `block` organization, and each was correct in the repository
it was written for. Neither was rewritten when the fork was taken. The difference is
only that GitHub validates one of them and reports the breakage, and validates nothing
about the other — so `GOVERNANCE.md` misdirects silently while `CODEOWNERS` at least
fails loudly to anyone who asks the right endpoint.

### The roster is org membership, not a file

The `launchpad-26` organization carries two teams, `maintainers` and `students`.
ADR-0056's provenance corroborates this from inside the repository: it records that
"teams `maintainers` and `students` already exist with repository access," which is why
research #369's assumption that "a team would have to be created" no longer applied.

Three repository permission levels are in use across the fork's collaborators —
`admin`, `maintain` and `write` — so maintainer-grade access is a platform grant here,
not a convention. The practical consequences are visible even from a `maintain` token:

- `maintain` can read `branches/<name>` and see `protected: true`.
- `maintain` **cannot** read `branches/<name>/protection`. That endpoint returns 404.
- `admin` is required to change a branch's protection or a push restriction list — which
  is exactly why ADR-0038 declines to name the accounts on `main`'s restriction list: the
  record "has no standing to grant anyone push access."

**Membership itself is deliberately not published here.** See *Scope and omissions*.

### Branch protection on `launchpad`

`launchpad` is protected. Verified directly:

```
gh api repos/launchpad-26/buzz/branches/launchpad --jq '{name,protected}'
  -> {"name":"launchpad","protected":true}
```

**Read that endpoint, not the branch listing.** `branches?per_page=100` is paginated and
`launchpad` is not on page 1; concluding "not protected" from an incomplete page is a
mistake that has already been made in this corpus once and produced a false claim. Ask
about the named branch.

**What protection actually requires is unreadable from here.** The number of approving
reviews, whether code-owner review is required, whether stale reviews are dismissed, and
which status checks are required are all in the `/protection` payload, which 404s under
a `maintain` token. That 404 is a **permissions artefact, not an absence** — the
`protected: true` flag on the branch itself settles that protection exists. An
administrator can read the settings with:

```bash
gh api repos/launchpad-26/buzz/branches/launchpad/protection
```

Until someone does and records the result, those settings are unknowns in this node and
are listed as such below. They are not guessed at, and no requirement here depends on
their value.

### Humans and agents

`launchpad/AGENTS.md` does not maintain two rosters. It draws the line at **acts**, not
at accounts — which is the only line that can hold, because an agent runs under a
human's token and GitHub's author field cannot tell the two apart.

Section 5 rule 1: an agent may **draft** any issue, PR or ADR on its own authority. It
may not, **on its own judgement**, decide an ADR outcome, approve a PR, merge one, or
close another agent's escalation. Three of those four are exercisable *on a human's
behalf* under ADR-0052's five conditions — the instruction quoted verbatim in the
artifact, the instructing human named there, scope exactly what was instructed, and the
agent stopping below 75% confidence. The fourth, closing another agent's escalation, is
never delegable.

Two consequences matter for maintainership specifically:

1. **Maintainer permission and maintainer authority are different things.** An agent
   operating under a maintainer's token holds that token's *permission* while holding
   none of the *authority* — the four withheld acts are withheld regardless of what the
   token can technically do. `launchpad/AGENTS.md` is explicit that holding admin is
   "not permission."
2. **The `by:agent` label is the only attribution mechanism there is.** It is required on
   every issue and PR an agent creates, and it is defined in `launchpad/labels.yml`. A
   reader auditing who did what has the label and the quoted instruction, and nothing
   else — the author field will name a human either way.

## MUST

These bind anyone — human or agent — writing about, relying on, or acting under
maintainership in this fork. Identifiers M1–M8 are this node's own.

| # | Requirement |
|---|---|
| **M1** | A claim about who maintains this fork MUST be evidenced against the platform or a tracked file, never against another document's say-so. Enforced by review only; nothing mechanical checks it. |
| **M2** | A claim about maintainership MUST NOT be sourced from `.github/CODEOWNERS` while that file resolves to an unknown owner. It names a team in another organization and confers nothing here. Enforced by review; GitHub reports the invalidity only to a caller who asks the codeowners-errors endpoint. |
| **M3** | A claim that the fork's governance is defined by `GOVERNANCE.md` MUST NOT be made. That file is a one-line redirect to Block's programme governance and describes upstream. Enforced by review. |
| **M4** | An agent MUST NOT decide an ADR outcome, approve a pull request, merge one, or close another agent's escalation on its own judgement, whatever permission its token holds. Enforced by `launchpad/AGENTS.md` section 5 rule 1 and ADR-0052; **nothing mechanical enforces it**, because the token cannot distinguish the agent from the human whose credential it uses. |
| **M5** | Where an agent exercises a delegated act, it MUST quote the instruction verbatim in the artifact and name the instructing human there. Enforced by ADR-0052 part A condition 2 and part B; **unenforceable by any script** — no check can compare a quote against something that was said. |
| **M6** | Every issue and pull request an agent creates MUST carry the `by:agent` label. Enforced by convention; the label exists in `launchpad/labels.yml` and nothing rejects an unlabelled issue. |
| **M7** | A maintainer MUST NOT route around a platform gate — no `gh pr merge --admin`, no dismissing reviews, no force-push over a review, no changing branch protection, required checks or rulesets to land a change. A blocked merge is an answer. Enforced by `launchpad/AGENTS.md` section 5; the platform permits the bypass to a token holding admin, so this is a rule people keep, not one the platform keeps. |
| **M8** | A statement of what branch protection on `launchpad` requires MUST cite the `/protection` payload read with an administrator's credential, or be recorded as unknown. The branch's `protected: true` flag establishes that protection exists and nothing about its terms. Enforced by review. |

## SHOULD

| # | Guidance |
|---|---|
| **S1** | A document needing to identify maintainers SHOULD name the **mechanism and where it is administered** — organization team membership, in the `launchpad-26` organization's settings — rather than reproducing a member list into a public repository. A list copied into a file goes stale the moment the team changes, and no check will notice. |
| **S2** | A reader trying to establish whether a control is in effect SHOULD query the platform rather than read a document asserting it. Twelve documentation claims about enforcement have been falsified in this corpus's authoring runs; `CODEOWNERS` here is a thirteenth. |
| **S3** | Where the fork has no policy, a node SHOULD record the absence and name who owns filling it, rather than composing a plausible policy. An invented rule that nobody adopted is worse than a named gap, because it reads as settled. |
| **S4** | A change that would alter who effectively maintains the fork — a new team, a permission grant, a change to a restriction list — SHOULD be recorded in an ADR, per the fork's own rule that a decision still being argued is an ADR issue and a decision made is a record. ADR-0038 is the worked example: it decided the *shape* of the restriction list and deliberately left its contents to an admin acting on the issue. |

## Enforcement

**Almost nothing here is mechanically enforced, and the parts that look enforced are the
ones to check hardest.**

| Requirement | What actually checks it |
|---|---|
| M1, M2, M3, M8 | Pull-request review only. No script reads a node's prose — the corpus validator discards the body before any check runs |
| M4, M5 | Nothing. Both are rules an agent keeps or does not; the token cannot tell agent from human, and no check can verify a quote against what was said |
| M6 | Nothing rejects an unlabelled issue. The label is defined; applying it is convention |
| M7 | Nothing, for a token holding admin. Branch protection stops a token that lacks it, which is a different control from the rule |
| Front matter of this node | `.github/workflows/launchpad-corpus-validate.yml`, on every change under `launchpad/docs/corpus` |

**What a green corpus-validate run does not establish about this node:**

| Not established | Consequence |
|---|---|
| That any statement here is true | Citation checking is structural — a path is opened, its contents are never compared against the claim above it |
| That the roster described is current | Org team membership can change with no commit to this repository at all |
| That branch protection still holds, or on what terms | Nothing in CI reads the protection API |
| That `CODEOWNERS` is still invalid — or has been fixed | The validator does not call GitHub. #1428 may land at any time and this section will go stale silently |
| That an agent quoted an instruction faithfully | Unverifiable by construction |

**The `CODEOWNERS` case is the honest illustration of all of this.** ADR-0033 assigns
that file a job — request human review on the upstream boundary — and the file has
carried an unknown owner for as long as it has been in this fork. A decision record
described a control; the control was not operating; nothing reported the difference for
as long as nobody called the endpoint. That is what "enforced by review" costs, and it
is why S2 is written the way it is.

## Exceptions and escalation

**There is no exception to M4 or M5.** The four withheld acts are withheld regardless of
permission, urgency, or how obvious the right answer looks. An agent that believes it
should decide, approve, merge or close on its own judgement is describing the failure
mode ADR-0052 exists to prevent — on 2026-08-28, 132 pull requests were merged with
`--admin` past 77 changes-requested reviews and unresolved CI, and that event is the
motivation ADR-0052 cites for itself.

**A departure from a SHOULD is made in the open.** Say which one, and why, in the
section it would have applied to. Do not depart silently.

**A blocked merge is escalated, not forced.** Fix the change or take it to a human.
Reaching for a stronger credential is M7's exact prohibition.

**A disputed reading of a requirement here is a judgement, not an exception.** The author
records the tension in the pull request and the reviewer decides. If the two do not
agree, that is a defect in the rule: file it as an issue against this node.

**A case none of this covers goes to an issue, not to a local reinterpretation.** Two
specific routes:

- **A question about *who decides* something** belongs to #910
  (`governance/decision-authority.md`), not here. This node describes who holds the
  maintainer role; it does not allocate decision rights.
- **A question about *who reviews* a given path** belongs to #907
  (`governance/codeowners.md`) and, for the mechanism's repair, to #1428.

**Changing who maintains the fork is an administrator's act, not a document's.** No edit
to this file grants or removes access. Permission changes happen in the `launchpad-26`
organization's settings and in repository settings, by someone holding `admin`; per S4
the decision behind such a change should be recorded in an ADR, and per ADR-0038 the
record states the shape while the admin executes the contents.

## Scope and omissions

**This node covers** who maintains `launchpad-26/buzz` and what that role carries: the
absence of any fork-authored roster, the inherited and partly broken state of
`GOVERNANCE.md` and `.github/CODEOWNERS`, the organization teams that carry the roster
in practice, the repository permission levels in use, branch protection on `launchpad`
and the limits of what a non-admin can read about it, and the human/agent distinction
`launchpad/AGENTS.md` draws over acts rather than accounts.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Which reviewer a given path pulls in; the `CODEOWNERS` mechanism as a routing device | #907 (`governance/codeowners.md`), open |
| Who holds authority to decide a given question, and how a decision is recorded | #910 (`governance/decision-authority.md`), open |
| Repairing the invalid `CODEOWNERS` entry, its path scope and its notification surface | #1428, per ADR-0033 |
| Whether `GOVERNANCE.md`'s upstream redirect should be replaced with fork-specific governance | Nobody, as far as this node could establish. See *not verified* below |
| The membership of `main`'s push restriction list | ADR-0038 and #298; an admin's to set, and deliberately unnamed in that record |
| Contribution mechanics — branch, commit, PR, DCO, labels | `launchpad/AGENTS.md` sections 6 and 7 |
| Upstream `block/buzz`'s own maintainership | `GOVERNANCE.md`'s target in `block/.github`; out of this fork's scope entirely |

**Deliberate privacy omissions.** `launchpad-26/buzz` is a public repository and this
corpus ships inside it. The following were **readable** with the credential used to
author this node and are **deliberately not published here**:

- **The membership of the `maintainers` and `students` teams.** Readable via
  `gh api orgs/launchpad-26/teams/<slug>/members`. Not reproduced, in names or in
  counts.
- **The repository's collaborator list.** Readable via
  `gh api repos/launchpad-26/buzz/collaborators`. Only the *set* of permission levels in
  use is recorded above — `admin`, `maintain`, `write` — because that is a structural
  fact about the permission model. Neither the accounts nor the number of accounts at
  each level is recorded.
- **The membership of `main`'s push restriction list**, which ADR-0038 also declines to
  name, for a compatible reason.

This is the intended outcome rather than a shortfall. Publishing a roster of individuals
into a public repository is a disclosure this node has no mandate to make, it would go
stale with no check to catch it, and the platform is already the authoritative place to
ask. **Where this node would otherwise have named people, it names the mechanism and
where it is administered instead.** Accounts that already appear in this repository's own
tracked files — for instance in ADR provenance sections — remain where their own records
put them; this node does not aggregate them into a roster, because a roster assembled
from commit authorship or PR participation would be exactly the personal-data
publication being avoided, arrived at sideways.

**Relationships.** Three declared, each resolved against `origin/launchpad` rather than
this worktree, per `launchpad/docs/corpus/AGENTS.md` step 9:

- `implements: corpus-template-policy` — this node is a concrete instance of the policy
  template, which is the directionality `relationships.schema.json` gives that type
  ("source is the concrete realization of target").
- `depends-on: corpus-agents` — this node's authority over evidence and citation is
  derived from that file's rules, not original to itself.
- `references: corpus-standard-normative-language` — the MUST/SHOULD keywords above mean
  what that standard says they mean, and it is cited rather than restated.

No edge to #907 or #910: both are open and unmerged, and a `relationships[].target`
naming an id no loaded node carries is a hard validation error. Those two are linked in
prose above and should be revisited as typed edges once they merge.

**Expected but not verified when this node was written:**

- **What branch protection on `launchpad` actually requires.** The number of approving
  reviews, `require_code_owner_reviews`, dismissal of stale reviews, and the required
  status check list are all unread — `/protection` 404s under a `maintain` token. The
  admin command is given under *Branch protection on `launchpad`*. Every statement here
  is scoped to the `protected: true` flag and claims nothing about its terms.
- **Whether the invalid `CODEOWNERS` has any effect beyond routing.** If protection
  requires code-owner review, an unresolvable owner could interact with mergeability in
  ways this node cannot observe without the protection payload. Stated as a possibility,
  not a claim.
- **Whether anyone owns replacing `GOVERNANCE.md`'s upstream redirect.** No issue was
  found assigning it. The gap is recorded above with "Nobody, as far as this node could
  establish" rather than being assigned to a plausible-looking issue number.
- **Whether the `maintainers` team's grant on this repository is `maintain`, `admin` or
  something else.** `gh api orgs/launchpad-26/teams/<slug>/repos/launchpad-26/buzz`
  returned no permissions payload for either team with this credential. The team names
  are corroborated by ADR-0056 and by the org teams listing; what each team is *granted*
  is not established here.
- **Whether upstream's `CONTRIBUTING.md` misleads a contributor in practice.** It states
  "Once approved, a maintainer will squash-merge your PR," while `allow_squash_merge` is
  `false` on this fork and merge commits are the only method offered. The contradiction
  is verified; whether anyone has been misled by it, and who owns reconciling an
  upstream-owned file, is not.
- **No CI run has exercised this node.** All validator evidence is local to the authoring
  worktree.
