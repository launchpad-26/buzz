---
id: governance-decision-authority
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
  - statement: "launchpad/AGENTS.md §5 rule 1 withholds exactly four acts from an agent's own judgement -- deciding an ADR outcome, approving a pull request, merging one, and closing another agent's escalation -- and states that the first three may be exercised on a human's behalf while the fourth never may, because the agent that raised an escalation is not the one who should clear it."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "The delegated-authority grant is conditional on five things holding together: an explicit instruction for the specific action in the current session, the instruction quoted verbatim in the artifact with the instructing human named, a stop-and-ask below 75% confidence, scope limited to exactly what was instructed, and the artifact naming itself as agent-exercised."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "ADR-0052 carries status Accepted and supersedes ADR-0019 in full; ADR-0019's own front matter reads 'status: Superseded by ADR-0052', so ADR-0019 still contains the withdrawn prohibition ('A human approval remains required, always') as live-looking prose, and a reader who opens it alone gets the rule that no longer binds."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
      - "launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md"
  - statement: "ADR-0052 part A names six delegable acts -- fill an ADR Decision outcome, submit a code review, request changes, re-review on a requested review, approve a pull request, merge it -- and its text nowhere mentions closing another agent's escalation, which is the fourth act launchpad/AGENTS.md §5 rule 1 withholds and calls never delegable."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
      - "launchpad/AGENTS.md"
  - statement: "launchpad/decisions/README.md states the ADR lifecycle: an open question becomes a type:adr issue, the issue's Decision outcome stays blank until a human settles it, an agent may write the outcome only under §5's delegated authority quoting the deciding human verbatim, and the record is written to launchpad/decisions/ in the same pull request that closes the issue -- closing without the document is not done."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "launchpad/decisions/README.md says 'Accepted ADRs live here', yet at the recorded revision three records in that directory carry 'status: Proposed' -- ADR-0034, ADR-0044 and ADR-0046 -- and ADR-0046 is one of the authorities launchpad/AGENTS.md §3 cites for a member of its closed upstream-boundary exception list."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
      - "launchpad/decisions/ADR-0046-root-mcp-registration-exception.md"
      - "launchpad/decisions/ADR-0034-knowledge-contract-owned-by-decision-layer.md"
      - "launchpad/decisions/ADR-0044-tiered-cli-instrumentation.md"
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md §3 enumerates six named exceptions to the never-edit-upstream rule, each pointing at its own ADR, and closes the enumeration with 'The list itself is closed; any further exception needs its own ADR'; for the deployment-image entry it adds 'This is settled -- do not raise it as a §3 violation in review' and 'Adding a sixth file to this exception is a change to that record, not a call to make in a pull request.'"
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/scripts/adr_boundary_check.py checks two things only -- that ADR-0005's file table, the ADR's own prose count and AGENTS.md §3 name the same files, and that each sanctioned file actually carries a Launchpad value -- and nothing in it detects a seventh exception added to §3 without an ADR."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/adr_boundary_check.py"
  - statement: ".github/workflows/launchpad-adr-check.yml runs that checker on every pull request with no paths filter, fails closed when the checker or either document is missing, and runs the checker's own unit tests before trusting its verdict."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-adr-check.yml"
  - statement: "launchpad/AGENTS.md §4 defines six issue types decided by an ordered first-yes-wins test with ADR first, requires exactly one type: label per issue, and states that an ADR is never a work item and never has children while a Task never has children either."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: ".github/workflows/launchpad-issue-check.yml mechanically rejects an issue carrying zero or more than one type: label and reports missing or empty required sections per type, writing the result back as an issue comment."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-issue-check.yml"
  - statement: "launchpad/scripts/pr_body_check.py's check_delegated requires an '### Authority' section on an agent pull request, requires a blockquote in it unless the answer starts 'n/a', requires a '### Deferred blockers' section, enforces DEFERRED_CEILING = 5, refuses a body that closes a Feature while deferring blockers against it, and rejects a deferred blocker that is not a child of the named Feature."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/pr_body_check.py"
      - "launchpad/scripts/test_pr_body_check.py"
  - statement: "pr_body_check.py's looks_agent_authored keys the strict agent checks on the body -- a provenance table row or a filled Authority section -- and not only on the by:agent label, so removing the label does not remove the requirements and produces its own error instead; PROVENANCE_FIELDS requires a value for 'Harness / provider', 'Model' and 'Initiating human'."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/pr_body_check.py"
  - statement: "pr_body_check.py's own docstring for check_delegated states that the quote itself cannot be verified by any script and that what it enforces is only that a warrant was offered at all, in a shape a reader can follow."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/pr_body_check.py"
  - statement: "ADR-0052 names the unverifiable quote as the decision's own weakest joint -- 'The audit trail rests on a quote no machine can verify... Rule 6 -- do not fabricate -- remains the only control on quote fidelity, and it is unenforceable by construction' -- and records that the decision reduces the number of independent humans in the merge path from one to zero for any pull request where an agent exercises the authority."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "ADR-0052 part G and launchpad/AGENTS.md §5 both forbid routing around the platform: no gh pr merge --admin or other branch-protection bypass, no approving or merging while checks fail or run, no dismissing reviews or force-pushing over one, no altering branch protection, required checks or rulesets -- and both cite 2026-08-28, when 132 pull requests were merged with --admin past 77 changes-requested reviews and unresolved CI, as the motivating event."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
      - "launchpad/AGENTS.md"
  - statement: "ADR-0052 retains ADR-0019's ruling that a required status check may only ever be a deterministic script and that a model verdict never turns a check green or red, and retains the deferral of marking any check required until buzz-infrastructure #105 lands, with a review date of 2026-09-05."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "ADR-0052 discloses that it was itself decided under the regime it replaces: its Decision outcome on #1765 was filled by an agent, which rule 1 forbade at the time, and it names that as the unavoidable first case rather than glossing it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "The launchpad branch is protected: a read of the specific branch returns protected true."
    entry_class: FACT
    evidence:
      - "tool_result(gh api repos/launchpad-26/buzz/branches/launchpad --jq '{name,protected}') -> {\"name\":\"launchpad\",\"protected\":true}, run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The protection detail endpoint is unreadable under this node's token: repos/launchpad-26/buzz/branches/launchpad/protection returns HTTP 404 while repos/launchpad-26/buzz reports permissions admin false, maintain true -- so the 404 is a permissions artefact and not evidence that protection is absent."
    entry_class: FACT
    evidence:
      - "tool_result(gh api repos/launchpad-26/buzz/branches/launchpad/protection) -> {\"message\":\"Not Found\",\"status\":\"404\"}; tool_result(gh api repos/launchpad-26/buzz --jq .permissions) -> {\"admin\":false,\"maintain\":true,\"pull\":true,\"push\":true,\"triage\":true}"
  - statement: "repos/launchpad-26/buzz/rulesets?includes_parents=true returns an empty array, which means the branch is guarded by classic branch protection rather than by a ruleset -- not that it is unguarded."
    entry_class: FACT
    evidence:
      - "tool_result(gh api 'repos/launchpad-26/buzz/rulesets?includes_parents=true') -> [], run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "launchpad/AGENTS.md §6 records a 2026-08-28 measurement of the protection settings this node cannot read today: one approving review required, dismiss_stale_reviews on, required_status_checks empty, enforce_admins off, and push restricted to 11 users."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad/AGENTS.md §6, recording a measurement taken 2026-08-28 by a reader holding repository admin"
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "The repository's merge-method settings are readable and match what launchpad/AGENTS.md §6 and ADR-0055 claim: allow_squash_merge false, allow_rebase_merge false, allow_merge_commit true, merge_commit_title MERGE_MESSAGE, merge_commit_message PR_TITLE."
    entry_class: FACT
    evidence:
      - "tool_result(gh api repos/launchpad-26/buzz --jq '{allow_squash_merge,allow_rebase_merge,allow_merge_commit,merge_commit_title,merge_commit_message}') -> {\"allow_merge_commit\":true,\"allow_rebase_merge\":false,\"allow_squash_merge\":false,\"merge_commit_message\":\"PR_TITLE\",\"merge_commit_title\":\"MERGE_MESSAGE\"}"
      - "launchpad/decisions/ADR-0055-merge-commit-is-the-merge-strategy.md"
  - statement: "CONTRIBUTING.md states 'The DCO Check will block your PR without it' and launchpad/AGENTS.md §6 states 'The DCO check fails any commit without a Signed-off-by trailer', but no check named DCO Check appears in gh pr checks output for pull requests #1997 or #1978 on this fork."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "launchpad/AGENTS.md"
      - "tool_result(gh pr checks 1997 --repo launchpad-26/buzz; gh pr checks 1978 --repo launchpad-26/buzz) -> 25 and 25 check rows respectively, none named 'DCO Check'"
  - statement: "The absent DCO Check is already tracked as an open bug rather than being a new finding."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2044, titled 'bug: CONTRIBUTING.md and AGENTS.md claim a DCO Check that does not run on this fork', state OPEN"
  - statement: ".github/CODEOWNERS contains a single wildcard rule assigning every path to @block/buzz-oss-team, an upstream Block team rather than a launchpad-26 team, and nothing in it scopes launchpad/ or launchpad/decisions/ to a cohort reviewer."
    entry_class: FACT
    evidence:
      - ".github/CODEOWNERS"
  - statement: "The merged corpus node corpus-standard-review-requirements explicitly excludes this node's subject, deferring 'the mechanics of pull-request review itself -- review count, DCO, who may approve' to launchpad/AGENTS.md §5-§6, and separately records that .github/CODEOWNERS routes the whole repository through one wildcard rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/review-requirements.md"
  - statement: "At the recorded revision launchpad/docs/corpus/governance/ does not exist on origin/launchpad; the merged corpus carries AGENTS.md, README.md, agents/, architecture/, capabilities/, development/, layers/, schema/, standards/ and templates/ only."
    entry_class: FACT
    evidence:
      - "tool_result(git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus) -> 231 paths, none beginning launchpad/docs/corpus/governance/, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The governance directory's other nodes are separately owned tasks: #907 codeowners, #908 compatibility-policy, #909 contribution-process, #911 deprecation-policy, #912 documentation-governance, #913 maintainers, #914 ownership, #915 security-policy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issue titles #907-#915, all of the form 'task: document governance/<stem>.md'"
  - statement: "Issue #910's Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#910 definition of done"
  - statement: "ADR-0054 withdrew ADR-0052 part C's 1,500-line / 10-file batch cap, and pr_body_check.py's report_size now prints a batch's size as a note without ever rejecting it -- the one place a number that used to gate now only informs."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0054-one-feature-one-pr-no-size-cap.md"
      - "launchpad/scripts/pr_body_check.py"
  - statement: "Every rule in launchpad/AGENTS.md §5 that governs who may decide is enforced by convention and reviewer attention rather than by the platform: the checks that do exist verify the shape of a warrant, never its truth, and none of them is a required status check while ADR-0052's deferral stands."
    entry_class: INFERENCE
    evidence:
      - "launchpad/scripts/pr_body_check.py"
      - ".github/workflows/launchpad-pr-check.yml"
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
      - "launchpad/AGENTS.md"
    confidence: 0.8
relationships:
  - type: implements
    target: corpus-template-policy
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-review-requirements
  - type: references
    target: corpus-standard-normative-language
  - type: references
    target: corpus-standard-decision-references
---

# Policy: decision authority in launchpad-26/buzz

Who may decide what in this fork: which acts an agent may take on its own judgement,
which it may take only on a named human's quoted instruction, which no delegation
reaches, and which questions may be settled only by an accepted ADR. This node states
the authority; it does not state the pipeline a change travels down — that belongs to
`governance/contribution-process.md` (#909), and the boundary between the two is drawn
in *Scope and omissions*.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| The rules themselves, as normative spec | `launchpad/AGENTS.md` §3–§6 |
| The delegated-authority grant and why it exists | [`launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md`](../../../decisions/ADR-0052-delegated-authority-and-feature-batching.md) |
| What an ADR is, and how one becomes binding | [`launchpad/decisions/README.md`](../../../decisions/README.md) |
| What MUST / SHOULD / MAY commit a document to | [`launchpad/docs/corpus/standards/normative-language.md`](../standards/normative-language.md) |
| How to cite a decision record from a corpus node | [`launchpad/docs/corpus/standards/decision-references.md`](../standards/decision-references.md) |
| Review duties on a corpus-touching pull request | [`launchpad/docs/corpus/standards/review-requirements.md`](../standards/review-requirements.md) |
| The shape this node is built to | [`launchpad/docs/corpus/templates/policy.md`](../templates/policy.md) |

Where this node and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Scope and authority

**This node governs** the allocation of decision rights in `launchpad-26/buzz`: the acts
an agent may perform on its own judgement, the acts it may perform only under a quoted
human instruction, the acts nothing delegates, the questions reserved to an accepted
ADR, and — separately from all of that — which of those allocations anything actually
checks.

**Its authority is derived, not original.** Every rule below already exists in
`launchpad/AGENTS.md` §3–§6, in `launchpad/decisions/README.md`, or in an accepted
decision record. This node creates no authority and grants none. It collects the
allocation that is currently scattered across a normative spec, a directory README and
four decision records, states it in one place a reader can check, and — the part none of
those sources does in one view — records what enforces each allocation and what does not.

**Precedence, in this order.** Where this node and `launchpad/AGENTS.md` disagree, **the
spec wins**; §1 of that file says so of itself, and this node is downstream of it. Where
`launchpad/AGENTS.md` and an accepted ADR disagree, **the ADR wins on the question it
decided**, because the spec's own §2 makes the decision record the artifact and the spec
the restatement. Where an ADR carrying `status: Superseded by ADR-YYYY` and its successor
disagree, **the successor wins in full** — `launchpad/decisions/README.md` is explicit
that superseding does not edit the old record, so a superseded ADR keeps its withdrawn
prose intact and reads as though it still binds. Where any document and the platform
disagree about what the platform enforces, **the platform is the fact** and the document
is a claim about it; see *Enforcement*.

**Normative keywords** below carry their RFC 2119 meanings, as
`corpus-standard-normative-language` defines them for this repository. A MUST here is a
restatement of an existing binding rule with its source named, never a new obligation
this node invents.

## The authority map

Read this as the answer to "may I do this myself?" Each row names the source, not this
node, as the authority.

| Act | Who may do it | Source |
|---|---|---|
| Draft any issue, pull request, or ADR body, in full | An agent, alone | §5 rule 1 |
| Choose an issue's type | An agent, alone, by §4's ordered first-yes-wins test; when unclear, file a Task, add `needs-triage`, and say so in the Objective | §4, §5 rule 2 |
| Fix something small in a file already being touched | An agent, alone, noting it in the pull request body | §4 *When to raise at all* |
| Defer a blocker outside the closed never-deferrable list | An agent, alone — pre-authorised, no per-case instruction | ADR-0052 part F, §6 |
| Fill an ADR *Decision outcome* | A human; or an agent **only** on that human's quoted instruction | §5 rule 1, `decisions/README.md`, ADR-0052 part A |
| Submit a code review, request changes, re-review | ADR-0052 part A lists these under the same five conditions; §5 rule 1 does not withhold them at all — see *Two divergences* | ADR-0052 part A |
| Approve a pull request | A human; or an agent **only** on that human's quoted instruction, in a self-identifying approval | §5 rule 1, ADR-0052 parts A and B |
| Merge a pull request | A human; or an agent **only** on that human's quoted instruction | §5 rule 1, ADR-0052 part A |
| Close another agent's escalation | A human. **Never delegable** — the agent that raised it is not the one who should clear it | §5 rule 1 |
| Defer a blocker inside the closed list | **Nobody**, with or without an instruction | ADR-0052 part D, §6 |
| Bypass branch protection, dismiss a review, alter required checks or rulesets | **Nobody** | ADR-0052 part G, §5 |
| Take any action against a live host | Out of scope entirely; governed by `launchpad-26/buzz-infrastructure` §6 rules 7–8 and its ADR-0015, unchanged | ADR-0052, §5 |
| Add a seventh exception to §3's upstream-boundary list | **Only an ADR.** Not a reviewer, not a pull request | §3 |
| Settle a question that changes how the fork works | **Only an ADR**, written to `launchpad/decisions/` in the same pull request that closes its issue | §2, §4 rule 3, `decisions/README.md` |

### The five conditions, and what they are worth

Delegated authority exists only when all five hold together: an explicit instruction for
the **specific** action in the **current** session; the instruction quoted **verbatim**
in the artifact with the instructing human named; a stop-and-ask below 75% confidence;
scope limited to exactly what was instructed; and the artifact naming itself as
agent-exercised. Standing permission does not exist, and one approval is not an
instruction to approve the next one.

**The quote is load-bearing and unverifiable, and the decision that created it says so.**
ADR-0052 records this as its own weakest joint: no machine can prove a quote reproduces
what was said, "do not fabricate" is the only control, and it is unenforceable by
construction. The same record states plainly that this reduces the independent humans in
the merge path from one to zero for any pull request where an agent exercises the
authority. That is not an objection this node is raising; it is the cost the decision
accepted in writing.

### Two divergences between the spec and the decision it cites

Both were read directly, at the recorded revision, and neither is resolved here.

1. **`launchpad/AGENTS.md` §5 rule 1 withholds a fourth act the ADR never mentions.**
   Closing another agent's escalation appears in the spec as never-delegable; ADR-0052's
   text does not contain it. The spec is stricter than the record it cites — which is
   the safe direction, but it means the ADR is not the whole authority for rule 1.
2. **ADR-0052 part A conditions three acts the spec does not withhold.** Submitting a
   code review, requesting changes, and re-reviewing on a requested review are listed in
   part A under the five conditions; §5 rule 1's four withheld acts do not include them,
   and the spec's *Acting on a human's instruction* says "Rule 1 withholds four acts.
   Three of them" are delegable. Read together, an agent reviewing a diff without a
   quoted instruction is unconditionally permitted by the spec and conditionally
   permitted by the ADR.

Per *Precedence*, the ADR wins on the question it decided. Both divergences are named in
*Scope and omissions* as gaps needing an owner rather than settled here.

## MUST

These restate binding rules that already exist. Each names its source; none is new.

| # | Requirement |
|---|---|
| **A1** | An agent MUST NOT decide an ADR outcome, approve a pull request, or merge one on its own judgement. (§5 rule 1) |
| **A2** | An agent MUST NOT close another agent's escalation, with or without an instruction. (§5 rule 1) |
| **A3** | Where an agent exercises delegated authority, all five conditions MUST hold together — specific action, current session, verbatim quote naming the human, ≥75% confidence, scope exactly as instructed, self-identifying artifact. Any one failing means the authority is absent. (§5 *Acting on a human's instruction*; ADR-0052 part A) |
| **A4** | An approval exercised under delegation MUST state that it is agent-submitted, name the instructing human, and quote the instruction. An approval missing any of the three is invalid. (ADR-0052 part B) |
| **A5** | A quoted instruction MUST NOT be paraphrased, tidied, or grammar-repaired; a dictated instruction keeps its transcription noise. (§5; ADR-0052 *Consequences*) |
| **A6** | No agent MUST route around the platform: no `gh pr merge --admin` or other branch-protection bypass, no approving or merging while checks fail or run, no dismissing reviews, no force-pushing over a review, no altering branch protection, required checks or rulesets. A blocked merge is an answer. (§5; ADR-0052 part G) |
| **A7** | The four never-deferrable classes MUST NOT be deferred by anyone: a credential, secret or password hash in the diff; a disclosure-boundary violation; a failing deterministic check; anything that leaves `launchpad` broken for other agents. The list is closed. (§6; ADR-0052 part D) |
| **A8** | An ADR outcome MUST be written to `launchpad/decisions/ADR-XXXX-slug.md` in the same pull request that closes its issue. Closing the issue without the document is not done. (§4 rule 3; `decisions/README.md`) |
| **A9** | A further exception to §3's upstream-boundary list MUST come from its own ADR, never from a reviewer's call in a pull request. The list is closed. (§3) |
| **A10** | Superseding a decision MUST NOT edit it: write a new record, set the old one's `status` to `Superseded by ADR-YYYY`, and name it in the new record's *Supersedes*. (`decisions/README.md`) |
| **A11** | Every issue MUST carry exactly one `type:` label, chosen by §4's ordered test with the first "yes" winning; the order MUST NOT be reordered to reach a different answer. (§4) |
| **A12** | An agent MUST NOT claim a check it did not run or an instruction it did not receive; quote it, link where it was said, or do not claim it. (§5 rule 4) |
| **A13** | Delegated review or merge authority MUST NOT be read as authority over a live host. Host action stays under `buzz-infrastructure` §6 rules 7–8 and its ADR-0015. (§5; ADR-0052) |

## SHOULD

| # | Guidance |
|---|---|
| **B1** | A reader establishing what is currently binding SHOULD open the superseding record, not the superseded one. ADR-0019 still reads "A human approval remains required, always" — true when written, withdrawn by ADR-0052, and nothing in ADR-0019's body says so except its front-matter `status`. |
| **B2** | An agent unsure whether the type is a PRD or a Task SHOULD file a Task with `needs-triage` and say so, rather than guess silently — misfiling a PRD as a Task hides an approval gate. (§5 rule 2) |
| **B3** | A claim that a rule is enforced SHOULD be checked against the config, workflow or platform that would enforce it, not against the document that asserts it. This node found three documented-but-unenforced claims by doing exactly that; see *Enforcement*. |
| **B4** | A caveat that changes how a decision should be read SHOULD sit with the claim, not in a closing confidence section below it. (§5 rule 7) |
| **B5** | Where an instruction's meaning is genuinely ambiguous, an agent SHOULD stop and ask rather than lean on the 75% threshold as a rounding rule. ADR-0052 names condition A.3 as the only guard against a lossy dictated instruction. |

## Enforcement

**Split the question in two: what is checked mechanically, and what is checked by nobody.**
Most of the authority allocation above is in the second group, and saying so is the point
of this section.

### Mechanically checked

| Rule | What checks it | What that check is worth |
|---|---|---|
| A warrant was *offered* for a delegated act | `launchpad/scripts/pr_body_check.py` `check_delegated`: requires an `### Authority` section, a blockquote unless the answer starts `n/a`, and a `### Deferred blockers` section | Shape only. The script's own docstring says the quote "cannot be verified by any script" |
| Agent provenance is disclosed | `pr_body_check.py` requires a value for `Harness / provider`, `Model` and `Initiating human`, plus a non-empty `### Not verified` section and a fenced code block | Presence, not truth |
| Dropping the `by:agent` label does not drop the checks | `looks_agent_authored` keys the strict path on the body — a provenance row or a filled Authority section — and reports the missing label as its own error | Real, and deliberate: a label is metadata anyone can edit after the fact |
| A Feature does not close over open deferred blockers; the ceiling of five | `pr_body_check.py`, `DEFERRED_CEILING = 5`, plus membership of the named Feature's children read from GitHub | Real, when GitHub answers; an unreadable child list degrades to "unverified", not to "pass" |
| §3's exception list agrees with itself and is actually used | `launchpad/scripts/adr_boundary_check.py`, run unfiltered on every pull request by `.github/workflows/launchpad-adr-check.yml`, which fails closed on a missing file and runs the checker's own tests first | Real for drift between the ADR and §3 — and blind to a *seventh* exception added without an ADR |
| Exactly one `type:` label; required sections per type | `.github/workflows/launchpad-issue-check.yml` | Real, and comments the result on the issue |
| Merge method | The platform: `allow_squash_merge` false, `allow_rebase_merge` false, `allow_merge_commit` true. Verified by API, not taken from the doc | Genuinely enforced — the rare case where §6's claim and the platform agree |

### Not checked by anything

- **Whether a quoted instruction is real.** ADR-0052 says so itself. Nothing compares the
  blockquote to anything a human said.
- **Whether the five conditions held.** A body can satisfy every `pr_body_check.py` rule
  while the instruction was for a different pull request, from a previous session, or
  reconstructed after the fact.
- **Whether an ADR *Decision outcome* was filled by a human or by an agent on its own
  judgement.** No check reads `launchpad/decisions/` for status, authorship or lifecycle
  state.
- **Whether a never-deferrable class was deferred.** `pr_body_check.py` validates the
  *shape* of the deferred list and its ceiling; it cannot tell a typo from a leaked
  credential.
- **Whether the ordered §4 test was actually applied.** The issue check counts labels; it
  cannot know whether the first "yes" was skipped.

### The gate above all of this is thinner than it reads

`launchpad` **is** protected — verified by reading the specific branch, which returns
`protected: true`. Two cautions, both learned the hard way:

- **Do not infer protection from a branch listing.** `branches?per_page=100` is paginated
  and `launchpad` is not on the first page; reading absence from it produces a false
  negative. Query the branch.
- **`rulesets?includes_parents=true` returning `[]` means classic protection, not none.**

**Three settings that decide who can merge are unreadable from here, and this node does
not guess at them.** `repos/launchpad-26/buzz/branches/launchpad/protection` returns HTTP
404 under a token reporting `admin: false, maintain: true` — a permissions artefact, not
an absence. So each of the following is an explicit **unknown**:

- `required_approving_review_count`
- `require_code_owner_reviews`
- `enforce_admins`

An account with repository admin can settle all three in one command:

```bash
gh api repos/launchpad-26/buzz/branches/launchpad/protection \
  --jq '{reviews: .required_pull_request_reviews, checks: .required_status_checks, admins: .enforce_admins, restrictions: (.restrictions.users // [] | length)}'
```

`launchpad/AGENTS.md` §6 records a 2026-08-28 measurement of exactly these — one
approving review, `dismiss_stale_reviews` on, `required_status_checks` empty,
`enforce_admins` off, push restricted to 11 users. That is carried here as attributed,
dated team knowledge and **must not be repeated as a current fact**: it is five days old
at this node's authoring time and unverifiable from this vantage point.

**If `required_status_checks` is still empty, every check named above is informational.**
ADR-0052 retains ADR-0019's deferral of marking any check required until
`buzz-infrastructure` #105 lands, with a review date of **2026-09-05** — three days after
this node was written. Under that deferral the mechanical column of this section reports
to a reviewer; it stops nothing.

### Two enforcement claims in the documents that do not hold

- **The DCO check.** `CONTRIBUTING.md` says "The **DCO Check** will block your PR without
  it"; `launchpad/AGENTS.md` §6 says "The DCO check fails any commit without a
  `Signed-off-by` trailer". No check named `DCO Check` appears among the 25 checks on
  either pull request #1997 or #1978 on this fork. Tracked at #2044. `git commit -s`
  remains required by the spec — it is simply required by convention here, not by a gate.
- **`.github/CODEOWNERS` names an upstream team.** One wildcard rule assigns every path to
  `@block/buzz-oss-team`. Nothing routes `launchpad/decisions/` to a cohort decision-maker.
  Whether `require_code_owner_reviews` is on is one of the three unknowns above, so the
  consequence cannot be stated either way from here. `governance/codeowners.md` (#907)
  owns this file.

## Exceptions and escalation

**There is no exemption from A1–A13.** They restate rules this node did not create, so
this node cannot waive them. An agent that believes a MUST above should not apply to its
case is describing a change to `launchpad/AGENTS.md` or to an ADR, not an exception.

**A SHOULD is departed from in the open.** Say which one, and why, in the artifact the
guidance would have applied to.

**A question about who decides is escalated to an ADR, not resolved locally.** §2 is
categorical: a decision still being argued is an ADR issue, and once made it becomes
`launchpad/decisions/ADR-XXXX-slug.md`. That is the escalation path for every gap this
node names, including the two divergences above.

**Escalating an authority question:**

1. File a `type:adr` issue, parented to the PRD or Feature that raised it, with
   `--parent`. An ADR nothing raised is filed standalone.
2. Add `needs-decision` explicitly — filing from the CLI does not apply the template's
   label.
3. Leave *Decision outcome* blank. An agent may fill it **only** under §5's delegated
   authority, quoting the deciding human verbatim.
4. Write the record in the same pull request that closes the issue.

**A blocked merge is a result, not an obstacle.** If the platform refuses, fix the change
or escalate to a human. Reaching for a stronger credential is the specific failure
ADR-0052 exists to prevent, and the record cites the 2026-08-28 bypass of 132 pull
requests as its own motivating evidence.

**`status: Proposed` is not a decision.** Three records in `launchpad/decisions/` carry
it — ADR-0034, ADR-0044 and ADR-0046 — while `decisions/README.md` says "Accepted ADRs
live here". An agent MUST NOT treat a `Proposed` record as settled authority. This
matters concretely: §3 cites ADR-0046 as the authority for one member of its closed
exception list, so that member's authority is a record the directory's own README implies
should not yet be there. Named as a gap; not resolved here.

## Scope and omissions

**This node covers** the allocation of decision rights in `launchpad-26/buzz` — what an
agent may decide alone, what needs a named human's quoted instruction, what nothing
delegates, what is reserved to an ADR — together with an evidence-checked account of what
enforces each allocation and what does not.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The process a change moves through — branch, commit convention, PR body shape, batching, merge mechanics | #909 `governance/contribution-process.md` |
| `.github/CODEOWNERS` as a subject, and what it should say for this fork | #907 `governance/codeowners.md` |
| Who the maintainers are by name, and the push-restriction roster | #913 `governance/maintainers.md`, #914 `governance/ownership.md` |
| Documentation governance and the corpus's own review duties | #912 `governance/documentation-governance.md`; and the merged `corpus-standard-review-requirements`, which already defers "review count, DCO, who may approve" to `launchpad/AGENTS.md` §5–§6 — the seam this node fills |
| Security disclosure authority and the private-advisory path | #915 `governance/security-policy.md` |
| Deprecation and compatibility decision rights | #911, #908 |
| Authority over a live host | `launchpad-26/buzz-infrastructure` §6 rules 7–8 and its ADR-0015, unchanged by anything here |
| The two spec/ADR divergences named above, and the three `Proposed` records | Unowned at this node's authoring time. Each needs an ADR or a spec correction; naming them is all this node may do |

**It does not decide anything.** Every MUST above restates an existing rule with its
source named. Where this node found a gap, it recorded the gap.

**Relationships.** `implements: corpus-template-policy` — this node is a concrete
instance of the merged policy template, which is the directionality
`relationships.schema.json` names for `implements`. `depends-on: corpus-agents` — this
node's evidence discipline and creation procedure derive from the corpus agent guide, per
that template's own convention. Three `references` edges: to
`corpus-standard-review-requirements`, whose scope section explicitly hands this subject
back; to `corpus-standard-normative-language`, which defines the keywords used above; and
to `corpus-standard-decision-references`, which governs how the ADR citations here are
made. Every target was confirmed present on `origin/launchpad` with
`git show origin/launchpad:<path>` before being declared, not resolved against this
worktree. No edge to any governance sibling: `launchpad/docs/corpus/governance/` does not
exist on the merge target, so every one of #907–#915 would be a hard validation error in
CI.

**Expected but not verified when this node was written:**

- **`required_approving_review_count`, `require_code_owner_reviews` and `enforce_admins`
  are unknown.** The protection endpoint 404s under this token. The command an admin
  would run is given in *Enforcement*. Nothing above concludes in either direction, and
  §6's 2026-08-28 figures are carried as dated team knowledge only.
- **Whether any status check is currently required.** Same 404. If ADR-0052's deferral
  still stands the answer is none, but that is the deferral's claim, not a measurement.
- **The current push-restriction roster.** Unreadable for the same reason; §6's "11
  users" is a 2026-08-28 figure.
- **Whether `@block/buzz-oss-team` resolves to any team in the `launchpad-26`
  organisation.** Not checked; team membership is not readable from here.
- **No CI run has exercised this node.** All validator evidence is local to this
  worktree.
- **The two spec/ADR divergences were read, not adjudicated.** Whether §5 rule 1's fourth
  withheld act should be added to ADR-0052, or whether ADR-0052's three review acts
  should be added to §5, is a decision this node has no authority to make — which is,
  fittingly, exactly what it is about.
