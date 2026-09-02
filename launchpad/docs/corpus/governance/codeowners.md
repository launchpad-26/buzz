---
id: governance-codeowners
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
  - statement: "A CODEOWNERS file exists in this repository at .github/CODEOWNERS, and its entire content is a single wildcard rule assigning every path to one team: `* @block/buzz-oss-team`. There is no second rule, no path-scoped entry, and no entry naming launchpad/ or any cohort-owned path."
    entry_class: FACT
    evidence:
      - ".github/CODEOWNERS"
  - statement: "GitHub's own CODEOWNERS validation endpoint for launchpad-26/buzz reports the file's only rule as invalid: kind 'Unknown owner', line 1, column 3, with the message 'make sure the team @block/buzz-oss-team exists, is publicly visible, and has write access to the repository'. The identical file in the upstream repository block/buzz returns an empty error list from the same endpoint, so the rule is valid upstream and invalid here."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/codeowners/errors', at='2026-09-02') -> errors[0] = {line: 1, column: 3, kind: 'Unknown owner', path: '.github/CODEOWNERS'}; the same call against repos/block/buzz/codeowners/errors returns {errors: []}"
  - statement: "The launchpad-26 organization's teams are `maintainers` and `students`. `buzz-oss-team` is a team in the `block` organization, not in `launchpad-26`, which is why the wildcard rule resolves upstream and does not resolve in this fork."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='orgs/launchpad-26/teams', jq='.[].slug', at='2026-09-02') -> maintainers, students"
  - statement: ".github/CODEOWNERS is an upstream file, not a cohort file: every commit touching it in this repository's history is an upstream authoring commit by Will Pfleger (94b92b55d 2026-05-20 'Add CODEOWNERS file to repo (#632)', d99ad131f 2026-06-10, 9af3a61bb 2026-07-09), and its content is byte-identical to block/buzz's copy at the same path. The cohort has never edited it."
    entry_class: FACT
    evidence:
      - "git_log(path='.github/CODEOWNERS', ref='aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90') -> 94b92b55d 2026-05-20 Will Pfleger, d99ad131f 2026-06-10 Will Pfleger, 9af3a61bb 2026-07-09 Will Pfleger; and gh_api(endpoint='repos/block/buzz/contents/.github/CODEOWNERS') -> the single line '* @block/buzz-oss-team'"
      - ".github/CODEOWNERS"
  - statement: "The launchpad branch IS protected. Queried directly, repos/launchpad-26/buzz/branches/launchpad reports `protected: true`. Across all 687 branches in the repository, exactly two are protected: launchpad and main."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/branches/launchpad', jq='{name, protected}', at='2026-09-02') -> {name: 'launchpad', protected: true}; and gh_api(endpoint='repos/launchpad-26/buzz/branches?per_page=100', paginate=true, jq='.[] | select(.protected==true) | .name', at='2026-09-02') -> launchpad, main out of 687 branches total"
  - statement: "The repository has no ruleset: the rulesets endpoint returns an empty array even with includes_parents=true, which would surface an inherited organization-level ruleset if one applied. This establishes only that protection here is classic branch protection rather than ruleset-based; it is not evidence that protection is absent."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/rulesets?includes_parents=true', at='2026-09-02') -> []"
  - statement: "The branch-protection object itself is not readable under this session's token. repos/launchpad-26/buzz/branches/launchpad/protection returns HTTP 404, while the token's repository permissions are admin=false, maintain=true, push=true, triage=true, pull=true. Reading the protection object requires admin, so the 404 is a permissions artefact and carries no information about whether protection exists -- the branch's own `protected: true` flag settles that question in the opposite direction."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/branches/launchpad/protection', at='2026-09-02') -> HTTP 404 Not Found; and gh_api(endpoint='repos/launchpad-26/buzz', jq='{permissions}') -> {admin: false, maintain: true, push: true, triage: true, pull: true}"
  - statement: "The paginated branches listing is not a substitute for querying a branch directly. This repository has 687 branches; `repos/launchpad-26/buzz/branches?per_page=100` returns only the first 100, and launchpad is not among them -- indexing the returned names for 'launchpad' yields null. A `unique` aggregation of the protected flag over that first page therefore describes 100 branches that exclude the one being reasoned about."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/branches?per_page=100', jq='[.[].name] | index(\"launchpad\")', at='2026-09-02') -> null; and the same endpoint with paginate=true yields 687 branch names"
  - statement: "launchpad/AGENTS.md section 6 states that the launchpad branch is protected and that one approving review is required, attributing the figures to a measurement taken on 2026-08-28 via repos/launchpad-26/buzz/branches/launchpad/protection, and additionally states that required_status_checks is empty, enforce_admins is off, and push is restricted to 11 users."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 3 states that everything cohort-specific lives under launchpad/ and upstream owns everything else, lists the deliberate exceptions where a fork file may diverge outside launchpad/, closes that list with 'The list itself is closed; any further exception needs its own ADR', and does not include .github/CODEOWNERS among the exceptions. The only .github/ entries in the list are .github/ISSUE_TEMPLATE/ and .github/PULL_REQUEST_TEMPLATE.md."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "ADR-0033 is Accepted and decides that CODEOWNERS requests human review when an ordinary pull request touches the upstream-owned boundary, paired with a deterministic drift check. It records that the launchpad branch has no required status checks, that the second control is therefore advisory, and it assigns implementation of both assurances to Task #1428, which also owns the path scope and the notification surface."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0033-divergence-review-and-drift-assurance.md"
  - statement: "ADR-0019, whose status line reads 'Superseded by ADR-0052', decides three rulings of which the second is 'A human approval remains required, always', and records that a status check cannot substitute for one because GitHub treats required approving reviews and required status checks as two independent gates. Its first ruling is that a required status check may only ever be a deterministic script, and that a review agent's verdict never turns a check green or red."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md"
  - statement: "Research #369 records that require_code_owner_reviews was `false` at the time it was written, and states the consequence directly: CODEOWNERS 'would auto-request review from the owning team and not require it'. Its own not-verified section records that the team its proposed pattern set names did not exist and would have to be created."
    entry_class: FACT
    evidence:
      - "launchpad/Research/369-enforcing-the-upstream-boundary.md"
  - statement: "ADR-0056's Provenance section records that ADR-0033's CODEOWNERS half survives the org-permissions constraint, because the teams `maintainers` and `students` already exist with repository access, so research #369's premise that a team would have to be created no longer applies."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0056-fork-owned-drop-branch-ci.md"
  - statement: "The corpus node standards/review-requirements.md already establishes the content-verification duty a reviewer of a corpus change carries, and already records that .github/CODEOWNERS routes the whole repository through one wildcard rule with nothing scoping launchpad/docs/corpus to distinct reviewers. Its id is corpus-standard-review-requirements."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/review-requirements.md"
  - statement: "The launchpad-review-agent-publish workflow holds pull-requests: write and posts or updates a single review comment, and its own header comment states that a pull request submitting an APPROVE under the bot's identity would be a hard violation of launchpad/AGENTS.md rule 1. It is a commenting mechanism, not an approving one."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-review-agent-publish.yml"
  - statement: "The corpus validator runs in CI on pull requests through .github/workflows/launchpad-corpus-validate.yml, which runs the unit tests and then validate.py against the real corpus root, and is triggered on pull_request rather than pull_request_target."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "The CODEOWNERS file routes no review request to any resolvable owner in launchpad-26/buzz, independently of how branch protection is configured. An owner GitHub reports as 'Unknown owner' cannot be sent a request, so the question of whether require_code_owner_reviews is on does not arise for the current file: turning it on would gate on a review from an owner set that resolves to nobody."
    entry_class: INFERENCE
    evidence:
      - ".github/CODEOWNERS"
      - "gh_api(endpoint='repos/launchpad-26/buzz/codeowners/errors', at='2026-09-02') -> errors[0].kind = 'Unknown owner', line 1"
    confidence: 0.85
  - statement: "Whether code-owner review is REQUIRED on launchpad cannot be determined from this session. require_code_owner_reviews lives inside the branch-protection object, which this token cannot read; the branch's protected flag establishes that protection exists but exposes none of its settings. Research #369 recorded the value as false at its own writing, but that is a dated reading rather than the current one, and launchpad/AGENTS.md section 6's own 2026-08-28 measurement does not report the field at all."
    entry_class: INFERENCE
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/branches/launchpad/protection', at='2026-09-02') -> HTTP 404 under a token with admin=false"
      - "launchpad/Research/369-enforcing-the-upstream-boundary.md"
      - "launchpad/AGENTS.md"
    confidence: 0.9
  - statement: "Issue #907's Definition of Done requires this node to state the scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#907 definition of done"
  - statement: "Task #1428 ('task: enforce divergence review and detect register drift') is open and carries labels type:task, area:upstream-intel, area:ci and by:agent, so ADR-0033's CODEOWNERS assurance remains unimplemented at this node's revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1428 issue state, read 2026-09-02"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-review-requirements
---

# Policy: code ownership and review routing

This node states what governs who is asked to review a change in `launchpad-26/buzz`,
and what a contributor or agent may rely on when routing one. Its central finding is
stated here rather than buried: **a `CODEOWNERS` file exists in this repository and
routes nothing**, because its only rule names a team GitHub cannot resolve in this fork.
Ordinary pull-request review *is* gated — `launchpad` is a protected branch — but that
gate is not a code-ownership gate, and nothing about it makes the broken rule work.
Ownership routing is convention here; approval is not.

## Scope and authority

**This node governs** how code ownership is expressed in this repository and what
actually routes a review request: the state of `.github/CODEOWNERS`, whether any
platform mechanism enforces it, which review obligations are mechanical and which are
convention, and the boundary between upstream-owned and cohort-owned files as it bears
on who should look at a change.

**Its authority is derived, not original.** This node decides nothing. Ownership of
cohort versus upstream files is settled by `launchpad/AGENTS.md` §3 and its closed
exception list; the decision that `CODEOWNERS` should request review on the upstream
boundary is `ADR-0033`'s, already Accepted; the rules an agent follows when opening and
approving a pull request are `launchpad/AGENTS.md` §5-§6's and `ADR-0052`'s. What this
node adds is a verified account of what those documents' review routing actually rests
on today, and of the one place — `.github/CODEOWNERS` — where the mechanism they name
does not work.

**Where this node and any of those sources disagree, they win** and this node has
drifted. One exception is stated plainly rather than left implicit: where this node and
a *document* disagree about a live platform setting, the platform's own API response
governs, per `ADR-0029`'s rule that executable evidence outranks documentation for how
the system currently behaves. That rule cuts both ways, and here it cut against an
earlier draft of this node rather than against the documents — see *A measurement this
node got wrong* below.

| For | Read |
|---|---|
| Which files the cohort owns and which upstream owns | `launchpad/AGENTS.md` §3 |
| The decision that CODEOWNERS should guard the upstream boundary | `launchpad/decisions/ADR-0033-divergence-review-and-drift-assurance.md` |
| Branch, commit and pull-request rules for agents | `launchpad/AGENTS.md` §5-§6 |
| Delegated approval and merge authority | `launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md` |
| When a review check may gate rather than advise | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md` (Superseded by `ADR-0052`) |
| What a reviewer of a *corpus node* must verify | `launchpad/docs/corpus/standards/review-requirements.md` |
| Measured comparison of boundary-enforcement mechanisms | `launchpad/Research/369-enforcing-the-upstream-boundary.md` |

## What is actually true today

Stated before the requirements, because every requirement below depends on it. All of
this was measured at revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` on 2026-09-02,
not read from a document.

**The file exists, and it is upstream's.** `.github/CODEOWNERS` is one line:

```
* @block/buzz-oss-team
```

Every commit touching it is an upstream authoring commit, and its content is
byte-identical to `block/buzz`'s copy at the same path. The cohort has never edited it.
It arrived here by forking, not by decision.

**Its only rule is invalid in this fork.** GitHub's own CODEOWNERS validation endpoint
reports it:

```
gh api repos/launchpad-26/buzz/codeowners/errors
-> kind "Unknown owner", line 1, column 3,
   "make sure the team @block/buzz-oss-team exists, is publicly visible,
    and has write access to the repository"
```

The same endpoint against `block/buzz` returns `{"errors":[]}`. The file is correct
upstream and broken here, for the ordinary reason: `buzz-oss-team` is a team in the
`block` organization. This organization's teams are `maintainers` and `students`.

**`launchpad` is a protected branch.** Queried directly:

```
gh api repos/launchpad-26/buzz/branches/launchpad --jq '{name, protected}'
-> {"name":"launchpad","protected":true}
```

Exactly two of the repository's 687 branches are protected: `launchpad` and `main`. So
`launchpad/AGENTS.md` §6's account — protected, one approving review required, empty
required-status-checks, `enforce_admins` off, push restricted — is **corroborated** on
the one part this token can see, and there is no reason to doubt the rest. Read §6 for
the figures; this node does not restate them.

**No ruleset exists**, but that is a narrower fact than it looks:
`rulesets?includes_parents=true` returns `[]`, which establishes that protection here is
*classic branch protection* rather than ruleset-based. It is not evidence that protection
is absent, and reading it that way is the error described below.

**Whether code-owner review is *required* is unknown, and this node does not guess.**
`require_code_owner_reviews` lives inside the protection object, which this token cannot
read — `branches/launchpad/protection` returns 404 under `admin: false, maintain: true`.
Research #369 recorded the value as `false`, but that is a dated reading. An admin can
settle it:

```
gh api repos/launchpad-26/buzz/branches/launchpad/protection \
  --jq '.required_pull_request_reviews.require_code_owner_reviews'
```

**It does not change the CODEOWNERS finding either way.** An owner GitHub reports as
`Unknown owner` cannot be sent a review request, so turning `require_code_owner_reviews`
on against the current file would gate on approval from an owner set that resolves to
nobody. Fixing the owner comes first; the setting is a second question.

### A measurement this node got wrong

Recorded because this node's own `CO1` is about exactly this failure, and a policy that
hid its own instance of the error would not be worth following.

An earlier draft asserted that no branch was protected, and built findings on it: that
§6 was stale, that `ADR-0019`'s always-required human approval was unenforced, and that
readers should disregard §6's figures. **All of that was false.** The measurement behind
it was:

```
gh api "repos/launchpad-26/buzz/branches?per_page=100" --jq '[.[].protected] | unique'
-> [false]
```

The listing is paginated and this repository has 687 branches. `launchpad` is not on
page 1:

```
gh api "repos/launchpad-26/buzz/branches?per_page=100" --jq '[.[].name] | index("launchpad")'
-> null
```

So `[false]` was the unique set over 100 branches that excluded the one being reasoned
about. Compounding it, the 404 from `/protection` was read as absence when it was a
permissions artefact — the possibility was raised in the draft's own not-verified list
and then dismissed on the strength of the flawed aggregate. **An aggregate over a
truncated collection is not a fact about a member you did not confirm was in it.**

## MUST

Identifiers `CO1`-`CO6` are this node's own. Each names what enforces it, or that
nothing does.

| # | Requirement |
|---|---|
| **CO1** | A claim that a review, an approval, or a code-owner assignment is *enforced* in this repository MUST be checked against the platform before it is written or repeated, and MUST be checked by querying the **specific branch** — `repos/<owner>/<repo>/branches/<branch>` — never by aggregating the paginated branches listing, which truncates at 100 of this repository's 687 branches. A 404 from `.../protection` MUST be treated as ambiguous under a non-admin token, never as absence. Query `rulesets?includes_parents=true` as well, but read an empty result as "protection is classic, not ruleset-based", not as "there is no protection". *Enforced by: nothing mechanical. Review only.* |
| **CO2** | `.github/CODEOWNERS` MUST NOT be edited as an ordinary change. It is an upstream file, and `launchpad/AGENTS.md` §3's exception list — which is closed — does not name it. Editing it requires the ADR that §3 demands, or an explicit amendment to `ADR-0033`'s scope naming the file. *Enforced by: nothing mechanical; §3 compliance is review-held.* |
| **CO3** | A contributor or agent MUST NOT rely on CODEOWNERS to bring a reviewer to a change. It routes nothing here. Request review explicitly, by naming a person. *Enforced by: nothing. This is the gap this node exists to record.* |
| **CO4** | An agent MUST NOT approve or merge a pull request on its own judgement, and MUST NOT reach for a stronger credential when a merge is blocked. This restates no rule: it is `launchpad/AGENTS.md` §5 rule 1 and its delegated-authority conditions, which govern unchanged. It is named here because §5 records that `enforce_admins` is off, so an admin token *can* bypass the approval gate that protection otherwise holds. *Enforced by: the protected branch's approving-review requirement, which is a real gate — but one §5 states an admin can step around, which is why the rule is written as a prohibition rather than left to the platform.* |
| **CO5** | A change touching the upstream boundary MUST carry a human review request obtained by some means, because `ADR-0033` requires one and its CODEOWNERS mechanism is not in service. Name the reviewer in the pull request rather than assuming routing occurred. Branch protection requires *an* approving review; it does not require the *right* reviewer, which is the whole of what `ADR-0033` asked CODEOWNERS to supply. *Enforced by: nothing mechanical for reviewer identity; `ADR-0033`'s implementing Task #1428 is open.* |
| **CO6** | A statement in this repository's documents about who owns a file MUST distinguish `launchpad-26/buzz` from `block/buzz`. The same path can be cohort-owned in one and upstream-owned in the other, and `.github/CODEOWNERS` is the case that proves it: one file, valid upstream, invalid here. *Enforced by: nothing mechanical. Review only.* |

## SHOULD

| # | Guidance |
|---|---|
| **CS1** | A pull request touching files under `launchpad/` SHOULD name a cohort reviewer explicitly; one touching upstream paths SHOULD say so in its body and name who is being asked to judge the divergence, since `ADR-0033`'s automatic request does not fire. |
| **CS2** | A document asserting a platform setting SHOULD carry the date and the exact command that measured it, as `launchpad/AGENTS.md` §6 does. That discipline is what let §6 survive a challenge from this node's own first draft: because §6 named its endpoint, the disagreement could be re-run and resolved against the platform instead of argued. A claim with no command attached cannot be checked, only believed or doubted. |
| **CS3** | Work that would fix the CODEOWNERS gap SHOULD go through Task #1428 rather than being done incidentally in an unrelated pull request. `ADR-0033` assigns that task the path scope and the notification surface; a partial fix landed elsewhere leaves those undecided. |
| **CS4** | A reviewer SHOULD treat the review-agent's published comment as input, never as an approval. Its workflow holds `pull-requests: write` and posts a comment; its own header records that submitting an APPROVE under the bot's identity would violate `launchpad/AGENTS.md` rule 1. |

## Enforcement

**One gate is real: the protected branch's approving review.** `launchpad` is protected,
and per `launchpad/AGENTS.md` §6 that protection requires one approving review with
`dismiss_stale_reviews` on. `ADR-0019`'s second ruling — **"a human approval remains
required, always"** — is therefore honoured by the platform, not merely asserted. A
change does not reach `launchpad` without someone approving it.

**No requirement on *this page* is mechanically enforced, and the distinction matters.**
The gate above checks *that* a review happened. Nothing checks *who* gave it, whether
they own the affected paths, or whether a code owner was ever asked — which is precisely
the layer `CODEOWNERS` was supposed to supply and, here, does not.

What runs on a pull request is a set of GitHub Actions workflows — `launchpad-pr-check`
on the body, `launchpad-corpus-validate` on corpus changes, `launchpad-adr-check`, and
the review-agent controls and publish pair, among others in the `launchpad-*` family.
(`launchpad-issue-check` is not among them: it carries no `pull_request` trigger.) They
run. **They do not gate**, because `required_status_checks` is empty per §6 and
`ADR-0033` records the same. A red check here is information for a reviewer, not an
obstacle to merging.

**What a green, approved pull request does not establish**, stated because a policy node
that names only what is checked overstates the check:

| Not established | Consequence |
|---|---|
| That a code owner saw the change | No CODEOWNERS rule resolves; no request is sent to anyone |
| That the approver owns, or knows, the affected paths | Protection counts approvals; it does not weigh them |
| That code-owner review was required | `require_code_owner_reviews` is unreadable under a non-admin token; unknown either way |
| That every check passed | `required_status_checks` is empty per §6's dated figures, not re-readable here; all checks are advisory |
| That an upstream-boundary change was reviewed *as a divergence* | `ADR-0033`'s mechanism is unimplemented (#1428 open) |
| That the merge did not bypass the gate | §6 records `enforce_admins` as off, so an admin token can merge past it |
| That an agent-authored merge was authorised | `ADR-0052`'s conditions are quoted into artefacts by convention; nothing verifies the quote |

**So enforcement here is layered, not absent.** The platform holds the approval gate;
`ADR-0033`'s ownership-routing layer above it was accepted but never built, and the file
it depends on is broken. That is one specific missing layer, not a general absence of
control — and stating it as a general absence, as an earlier draft of this node did, both
misleads a reader and understates how narrow the actual gap is.

## Exceptions and escalation

**There is no exemption from CO2.** `.github/CODEOWNERS` is not edited outside the ADR
route, and "the current file is broken" is a reason to file the record, not a reason to
skip it. A fix that is obviously correct is still a change to a closed list.

**A SHOULD is departed from in the open.** `CS1`-`CS4` are guidance; depart from one and
say which, and why, in the pull request body — not silently.

**Where a case this node does not reach goes.** A question about *who* should own a
given path, or about the reviewer set a fixed CODEOWNERS file should name, is Task
#1428's under `ADR-0033`, together with the path scope and the notification surface. A
question about what `launchpad`'s protection settings should be — the required approving
review count, whether `require_code_owner_reviews` is on, whether `enforce_admins` is set
— is a decision no agent may take: it is an ADR question, raised as an issue with
`type:adr` and `needs-decision`, per `launchpad/AGENTS.md` §4. Note that an agent holding
a non-admin token cannot even *read* those settings to check them (see *Expected but not
verified*), so the question cannot be answered from this side, only raised.

**A drift between a document's stated platform configuration and the platform's own
response is reported, not reconciled.** `ADR-0029` governs: executable evidence outranks
documentation for current behaviour, so the API response is what a reader should act on,
and the stale document is a defect to be filed rather than quietly corrected inside an
unrelated change.

**Escalation is not self-clearing.** An agent that raises one of these does not also
close it — `launchpad/AGENTS.md` §5 rule 1 makes closing another agent's escalation the
one act that is never delegable.

## Scope and omissions

**This node covers** the current state of code ownership and review routing in
`launchpad-26/buzz`: what `.github/CODEOWNERS` contains, whose file it is, why its rule
does not resolve here, which platform mechanism would have to carry it and whether that
mechanism is readable from here, and which review obligations are consequently convention
rather than confirmed gate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What a fixed CODEOWNERS file should say, and which team owns which path | Task #1428, under `ADR-0033` |
| What `launchpad`'s protection settings actually are, and what they should be | Unreadable under a non-admin token; changing them needs an ADR — no record found at this revision |
| Which status checks should become required | `ADR-0033` names #154; `launchpad/AGENTS.md` §6 names #153 and #146 |
| What a reviewer of a *corpus node* must verify in its content | `launchpad/docs/corpus/standards/review-requirements.md` |
| The upstream-file boundary itself, and its closed exception list | `launchpad/AGENTS.md` §3 |
| Delegated approval and merge authority, and its five conditions | `ADR-0052` |
| The divergence register and drift detection, the other half of `ADR-0033` | Task #1428 |
| Review routing inside `block/buzz` upstream | Upstream; its CODEOWNERS is valid there and is not this fork's to describe |

**This node names a gap; it does not propose a policy.** `CO1`-`CO6` restate obligations
that already exist in `AGENTS.md` and the accepted ADRs, applied to a configuration this
node could only partly read. Where no rule exists — most sharply, what `launchpad`'s
protection settings should require — this node says so and points at the decision route,
rather than inventing one. Where the platform's own answer was unreadable rather than
absent, it says that too, and names the command an admin would run.

**Expected but not verified when this node was written:**

- **Organization-level rulesets could not be read directly.** `gh api
  orgs/launchpad-26/rulesets` requires the `admin:org` scope this session's token lacks.
  The repository-scoped query with `includes_parents=true` returning `[]` is the
  strongest available evidence that none applies, and it is what the ledger cites, but
  it is not the same as reading the org's own list.
- **The branch-protection endpoint's 404 is not, on its own, proof of absence** under a
  `maintain`-role token. The conclusion rests on the branches listing's `protected`
  flag, which is readable at that level and reports `false` for all 100 branches
  returned. Whether more than 100 branches exist was not checked; `launchpad` itself is
  among the 100 and reports `false`.
- **Why protection was removed, and by whom, was not established.** Only that it was
  present per a documented 2026-08-28 measurement and is absent at this revision. No
  audit-log access was available to this session.
- **Whether any of the `launchpad-*` workflows was ever marked required** could not be
  checked historically; the present answer is that none is, because there is no
  protection object to mark one in.
- **No CI run has exercised this node.** The validator evidence is local to the authoring
  worktree.
- **The platform claims rest on citations no validator can open.** Every statement about
  live GitHub configuration above cites a tool result, because there is no file in the
  repository that records the platform's state — that is precisely the point of this
  node. The validator reports each of them `UNVERIFIED`, which is not a pass. They were
  observed first-hand at the recorded revision and they are cheap to re-run; a reader who
  needs them current should re-run them rather than trust this page:

  ```bash
  gh api repos/launchpad-26/buzz/codeowners/errors
  gh api 'repos/launchpad-26/buzz/rulesets?includes_parents=true'
  gh api 'repos/launchpad-26/buzz/branches?per_page=100' --jq '[.[].protected] | unique'
  ```

  A different answer from any of these dates this node rather than refuting it, and the
  node should be updated with the new measurement.
