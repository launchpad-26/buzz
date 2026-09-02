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
  - statement: "No branch in this repository is protected and no repository ruleset exists. All 100 branches returned by the branches listing report `protected: false`, the unique set of that field across them being `[false]`; the rulesets endpoint returns an empty array even with includes_parents=true, which would surface an inherited organization-level ruleset if one applied."
    entry_class: FACT
    evidence:
      - "gh_api(endpoint='repos/launchpad-26/buzz/branches?per_page=100', jq='[.[].protected] | unique', at='2026-09-02') -> [false]; and gh_api(endpoint='repos/launchpad-26/buzz/rulesets?includes_parents=true', at='2026-09-02') -> []"
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
  - statement: "Because the sole CODEOWNERS rule names an owner GitHub cannot resolve in this fork, and because no branch protection or ruleset exists to carry a require_code_owner_reviews setting, the CODEOWNERS file currently routes no review request to anyone in launchpad-26/buzz and would route none even if protection were enabled without first fixing the owner."
    entry_class: INFERENCE
    evidence:
      - ".github/CODEOWNERS"
      - "gh_api(endpoints=['repos/launchpad-26/buzz/codeowners/errors', 'repos/launchpad-26/buzz/rulesets?includes_parents=true', 'repos/launchpad-26/buzz/branches?per_page=100'], at='2026-09-02') -> Unknown owner on line 1; []; and [false] as the unique set of the protected flag"
    confidence: 0.9
  - statement: "launchpad/AGENTS.md section 6's protection figures no longer describe the repository. Between its 2026-08-28 measurement and this node's revision, protection on launchpad was removed or lapsed rather than merely becoming unreadable, because the branches listing's protected flag is readable without admin permission and reports false."
    entry_class: INFERENCE
    evidence:
      - "launchpad/AGENTS.md"
      - "gh_api(endpoint='repos/launchpad-26/buzz/branches?per_page=100', jq='[.[].protected] | unique', at='2026-09-02', token_permissions='admin=false maintain=true push=true triage=true pull=true') -> [false]"
    confidence: 0.8
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
negative and it is stated here rather than buried: **a `CODEOWNERS` file exists in this
repository and routes nothing.** Its only rule names a team GitHub cannot resolve in
this fork, and no branch protection or ruleset exists that could require code-owner
review even if the rule resolved. Review routing here is convention held by people and
agents, not a gate held by a machine.

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
node adds is a single verified account of the *current* state, because the documents
above describe a configuration that is not the one the platform is currently in.

**Where this node and any of those sources disagree, they win** and this node has
drifted. One exception is stated plainly rather than left implicit: where this node and
a *document* disagree about a live platform setting, the platform's own API response
governs, per `ADR-0029`'s rule that executable evidence outranks documentation for how
the system currently behaves. That rule is why this node contradicts
`launchpad/AGENTS.md` §6 below rather than repeating it.

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

**Nothing could enforce it even if it resolved.** No branch in this repository is
protected — the unique set of the `protected` field across all 100 branches returned by
the branches listing is `[false]` — and the rulesets endpoint returns `[]` even with
`includes_parents=true`, which is the query that would surface an inherited
organization-level ruleset. `require_code_owner_reviews` is a branch-protection setting;
with no protection object, there is nowhere for it to be set.

**This contradicts `launchpad/AGENTS.md` §6, and the contradiction is the point.** That
section states `launchpad` is protected, that one approving review is required, and
attributes the figures to a measurement on 2026-08-28. Five days later the branch is not
protected. The `protected` flag used here is readable without admin permission — the
token that measured it holds `maintain`, not `admin` — so this is not a permissions
artefact masquerading as an absence. **Do not restate §6's protection figures.** Re-run
the query.

## MUST

Identifiers `CO1`-`CO6` are this node's own. Each names what enforces it, or that
nothing does.

| # | Requirement |
|---|---|
| **CO1** | A claim that a review, an approval, or a code-owner assignment is *enforced* in this repository MUST be checked against the platform before it is written or repeated. Query both `repos/launchpad-26/buzz/rulesets?includes_parents=true` and the branch-protection endpoint, and treat the branches listing's `protected` flag as the reading that survives a non-admin token. *Enforced by: nothing mechanical. Review only.* |
| **CO2** | `.github/CODEOWNERS` MUST NOT be edited as an ordinary change. It is an upstream file, and `launchpad/AGENTS.md` §3's exception list — which is closed — does not name it. Editing it requires the ADR that §3 demands, or an explicit amendment to `ADR-0033`'s scope naming the file. *Enforced by: nothing mechanical; §3 compliance is review-held.* |
| **CO3** | A contributor or agent MUST NOT rely on CODEOWNERS to bring a reviewer to a change. It routes nothing here. Request review explicitly, by naming a person. *Enforced by: nothing. This is the gap this node exists to record.* |
| **CO4** | An agent MUST NOT approve or merge a pull request on its own judgement, and MUST NOT reach for a stronger credential when a merge is blocked. This restates no rule: it is `launchpad/AGENTS.md` §5 rule 1 and its delegated-authority conditions, which govern unchanged, and is named here only because the absence of branch protection removes the platform backstop that made ignoring them visible. *Enforced by: nothing mechanical, and now less than before — with no protection object, `enforce_admins` is not merely off, it does not exist.* |
| **CO5** | A change touching the upstream boundary MUST carry a human review request obtained by some means, because `ADR-0033` requires one and its CODEOWNERS mechanism is not in service. Name the reviewer in the pull request rather than assuming routing occurred. *Enforced by: nothing mechanical; `ADR-0033`'s implementing Task #1428 is open.* |
| **CO6** | A statement in this repository's documents about who owns a file MUST distinguish `launchpad-26/buzz` from `block/buzz`. The same path can be cohort-owned in one and upstream-owned in the other, and `.github/CODEOWNERS` is the case that proves it: one file, valid upstream, invalid here. *Enforced by: nothing mechanical. Review only.* |

## SHOULD

| # | Guidance |
|---|---|
| **CS1** | A pull request touching files under `launchpad/` SHOULD name a cohort reviewer explicitly; one touching upstream paths SHOULD say so in its body and name who is being asked to judge the divergence, since `ADR-0033`'s automatic request does not fire. |
| **CS2** | A document asserting a platform setting SHOULD carry the date and the exact command that measured it, as `launchpad/AGENTS.md` §6 does. That discipline is why this node could detect the drift rather than inherit it — a claim with no measurement attached cannot be falsified, only believed. |
| **CS3** | Work that would fix the CODEOWNERS gap SHOULD go through Task #1428 rather than being done incidentally in an unrelated pull request. `ADR-0033` assigns that task the path scope and the notification surface; a partial fix landed elsewhere leaves those undecided. |
| **CS4** | A reviewer SHOULD treat the review-agent's published comment as input, never as an approval. Its workflow holds `pull-requests: write` and posts a comment; its own header records that submitting an APPROVE under the bot's identity would violate `launchpad/AGENTS.md` rule 1. |

## Enforcement

**Nothing mechanical enforces any requirement on this page.** That is the honest answer
and it is the same answer for every row in the MUST table above.

What *does* run on a pull request is a set of GitHub Actions workflows —
`launchpad-pr-check` on the body, `launchpad-corpus-validate` on corpus changes,
`launchpad-adr-check`, and the review-agent controls and publish pair, among others in
the `launchpad-*` family. (`launchpad-issue-check` is not among them: it carries no
`pull_request` trigger.) They run. **They do not gate**, because no branch protection
exists to mark any of them required, and `ADR-0033` had already recorded that
`launchpad` has no required status checks even while protection did exist. A red check
on a pull request here is information for a reviewer, not an obstacle to merging.

**What a green pull request does not establish**, stated because a policy node that
names only what is checked overstates the check:

| Not established | Consequence |
|---|---|
| That a code owner saw the change | No CODEOWNERS rule resolves; no request is sent |
| That anyone with write access approved it | No protection object requires an approving review |
| That the author did not approve their own change | The self-approval bar lives in branch protection, which is absent |
| That every required check passed | There are no required checks; all of them are advisory |
| That an upstream-boundary change was reviewed as a divergence | `ADR-0033`'s mechanism is unimplemented (#1428 open) |
| That an agent-authored merge was authorised | `ADR-0052`'s conditions are quoted into artefacts by convention; nothing verifies the quote |

**Enforcement here is review and self-discipline, by circumstance rather than by
design.** `ADR-0019` (Superseded by `ADR-0052`) settled that only a deterministic script
may gate a merge, and — its second ruling — that **"a human approval remains required,
always"**, noting that a status check can never substitute for one because GitHub treats
required approvals and required checks as independent gates. `ADR-0033` then accepted an
advisory control knowingly, while expecting required checks to land later.

**Neither anticipated the state measured here.** With no protection object, the
independent gate `ADR-0019` relied on is not merely unsatisfied — it is not configured,
so the approving review it called always-required is not required by anything. That is a
gap between an accepted decision and the live platform, and under `ADR-0029` an accepted
decision governs *intended* behaviour even where configuration has drifted from it. So
the requirement stands as policy and is simply unenforced. This node reports that; it
does not decide what to do about it.

## Exceptions and escalation

**There is no exemption from CO2.** `.github/CODEOWNERS` is not edited outside the ADR
route, and "the current file is broken" is a reason to file the record, not a reason to
skip it. A fix that is obviously correct is still a change to a closed list.

**A SHOULD is departed from in the open.** `CS1`-`CS4` are guidance; depart from one and
say which, and why, in the pull request body — not silently.

**Where a case this node does not reach goes.** A question about *who* should own a
given path, or about the reviewer set a fixed CODEOWNERS file should name, is Task
#1428's under `ADR-0033`, together with the path scope and the notification surface. A
question about whether branch protection should be restored, and with what settings, is
a decision no agent may take: it is an ADR question, raised as an issue with
`type:adr` and `needs-decision`, per `launchpad/AGENTS.md` §4.

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
does not resolve here, what platform mechanism could enforce it and does not exist, and
which review obligations are consequently convention rather than gate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What a fixed CODEOWNERS file should say, and which team owns which path | Task #1428, under `ADR-0033` |
| Whether branch protection should be restored, and with what settings | Undecided; needs an ADR — no record found at this revision |
| Which status checks should become required | `ADR-0033` names #154; `launchpad/AGENTS.md` §6 names #153 and #146 |
| What a reviewer of a *corpus node* must verify in its content | `launchpad/docs/corpus/standards/review-requirements.md` |
| The upstream-file boundary itself, and its closed exception list | `launchpad/AGENTS.md` §3 |
| Delegated approval and merge authority, and its five conditions | `ADR-0052` |
| The divergence register and drift detection, the other half of `ADR-0033` | Task #1428 |
| Review routing inside `block/buzz` upstream | Upstream; its CODEOWNERS is valid there and is not this fork's to describe |

**This node names a gap; it does not propose a policy.** `CO1`-`CO6` restate obligations
that already exist in `AGENTS.md` and the accepted ADRs, applied to a configuration that
has changed underneath them. Where no rule exists — most sharply, whether protection
should be restored — this node says no rule exists and points at the decision route,
rather than inventing one.

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
