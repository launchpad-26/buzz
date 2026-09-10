---
status: Proposed
date: 2026-09-10
issue: launchpad-26/buzz#2169
decided_in: launchpad-26/buzz#2169
supersedes: none
---

# ADR-0060 — An author may merge their own pull request when it meets a stated bar

> **Status is `Proposed`, deliberately.** The cohort has been asked and has not yet answered.
> Nothing here is in force, and `launchpad/AGENTS.md` §5 is unchanged.
>
> **Revised 2026-09-10 after an independent adversarial review** (Codex) returned REQUEST
> CHANGES with a Blocker against the first draft. The Blocker was that the first draft's
> independent-review condition read *"findings are either fixed **or answered** in a comment"* —
> which let the author answer a Blocker with "disagree" and merge, making the author the judge
> of their own compliance. It was written as the condition that stopped "clean" collapsing into
> "the author thinks so", and it collapsed into exactly that. Two further conditions failed the
> same way and are rewritten below; the review's full findings are on #2169.

## Decision

**Proposed:** a pull request's author may merge it themselves, bypassing the one-approval
requirement, **only** when all of the following hold. If any is unmet, the pull request waits.

1. **The required-check set completed successfully against the exact commit being merged.**
   Not "every check that ran" — zero checks satisfies that, and this branch requires none, so a
   missing trigger or disabled workflow would pass silently. Queued, cancelled, skipped or
   stale-commit results do not count. A later successful re-run supersedes an earlier failure on
   the same commit.
2. **No blocking finding is open** — from a GitHub `CHANGES_REQUESTED` review, or from any
   review posted as a comment. A finding stays open across pushes and across review dismissal
   until it is closed under condition 3. It does not lapse because the head moved.
3. **An independent review covering the final diff has been run, posted, and its blocking
   findings closed by someone other than the author.** A model review is *evidence*, not
   authorisation: it can find defects but cannot clear them. The prompt and full output are
   retained and linked. **See Open question A — who may close a finding is the substantive
   choice this decision turns on, and it is not settled here.**
4. **The evidence is posted before the merge, not after.** A comment naming the commit to be
   merged, the check run, the review and its disposition — then the resulting merge commit
   recorded afterwards. A named person other than the author audits these periodically. A
   record written after the fact is a log, not a control, and logging establishes
   accountability rather than correctness.

**Scope is not settled.** As drafted this exception has no expiry, excludes no class of change,
and requires no attempt to find a reviewer first — so on its own terms it could be applied
immediately to a security, workflow or governance change, including one that widens bypass
authority further. **See Open question B.**

Merging past a failing check, past an open blocking finding, or without independent review is
not covered by this and remains what §5 calls routing around the platform.

## Open questions the group must answer

**A. Who may close a blocking finding?** The whole value of the decision rests here.

- *A1 — only an independent reviewer may.* Preserves independent acceptance. Costs: reintroduces
  a dependency on another person, which is the bottleneck this decision exists to relieve —
  though a narrower one, since closing a finding is smaller than a full review.
- *A2 — the author may, with a written justification on the pull request.* Keeps the flow
  unblocked. Costs: the author judges their own compliance. **This is a bypass with a logging
  requirement, and should be described that way rather than as assurance.**
- *A3 — unresolved findings simply block.* Simplest and strictest. Costs: a wrong or low-quality
  finding can stall correct work with no route around it.

**B. What is out of scope, and for how long?** Candidates: exclude changes to
`.github/workflows/`, `launchpad/decisions/`, `launchpad/AGENTS.md`, and anything touching
credentials or deployment; require that a reviewer was requested and did not respond within a
stated window; set an expiry date after which the exception lapses unless renewed.

**C. Who accepts this, given the proposer benefits from it?** This document was raised by the
contributor it would unblock and drafted by an agent working for her. That is not a reason to
reject it, but the acceptance should be recorded as a decision of the group with the interest
disclosed, not as the proposer's own.

## Context

### The bottleneck is real

`launchpad` requires one approving review and GitHub does not let an author approve their own
pull request. Finished work therefore waits on another person noticing. Two examples from
2026-09-10: **#2109**, a complete fix with its own passing test suite for a gate that had
already forced three `--no-verify` pushes that day, sat four days with no reviewer assigned;
**#574** sat two weeks under a title that was no longer true.

Those show *delay*. They do not by themselves show that better reviewer assignment, rotation or
escalation could not fix it — option 2 below is the honest alternative and has not been tried
deliberately.

### The bar has to live here, because the platform enforces almost nothing

```
required_approving_review_count: 1
required_status_checks.contexts: []      # none
rulesets:                                 # none
enforce_admins: false                     # admins already bypass all of it
dismiss_stale_reviews: true
require_last_push_approval: false
```

One approval is the only enforced gate. A rule phrased as *"merge when it is clean and
mergeable"* would therefore mean *"merge when nothing is stopping you"* — GitHub's `mergeable`
flag reports the absence of conflicts, not the presence of assurance.

`enforce_admins: false` means the capability already exists. This is about when using it is
legitimate, not about granting it.

To be precise about what is being changed: an author merging their own pull request is already
permitted once someone else approves it. The disputed act is merging **without** the required
approval.

### Why independent review is a condition

On 2026-09-10 an independent cross-model review returned REQUEST CHANGES on three of three
fully CI-green pull requests — #2156 and #2163 (this author's, judged ready by her) and #2161
(another author's), the last carrying a Blocker where a credential split left the relay unable
to authenticate at all. On #2163 it found a proposed guard that contradicted the decision it
was attached to.

The accurate reading is narrow: **passing CI did not detect those defects.** Since no check is
required here, the platform also does not guarantee checks run at all. Neither fact makes a
green tick meaningless in general — it means it is not evidence of the kind this decision needs.

That same review is what produced this revision, which is the most direct evidence available
that condition 3 is doing real work rather than adding ceremony.

### What the existing rules do and do not say

- **`AGENTS.md` §5** says *"No `gh pr merge --admin`, and no other bypass of branch
  protection."* It sits in the AI-agent contributor guide, but nothing at that line scopes it to
  agents. **This decision authorises a human's direct action only. Agents remain prohibited.**
  If the group later wants an agent to perform the merge on instruction, that is a substantive
  amendment to §5 and must be reconciled with ADR-0052 — not a clarification, and not in scope
  here.
- **ADR-0052** governs an *agent* approving or merging on quoted human instruction. Different
  subject, hence a new record.
- **`launchpad/README.md`** told contributors to expect two approving reviews when the branch
  enforces one. Corrected in the same pull request, since it is wrong either way.

### The event on the other side

§5 records its motivation: on 2026-08-28, **132 pull requests were merged with `--admin` past
77 changes-requested reviews and unresolved CI.**

The first draft answered this by distinguishing *"a gate that has spoken from a gate nobody has
staffed."* That framing is withdrawn: an approval gate requires affirmative acceptance, so
silence is the gate's unmet state, not evidence a bypass is safe. Absence of rejection is not
authorisation. The 2026-08-28 event remains directly relevant evidence about discretionary
bypass, and conditions 1–3 exclude *that specific pattern* only to the extent they are honoured.

## Decision drivers

- Finished work waiting days on an unassigned reviewer is a real cost, heaviest on whoever opens
  the most pull requests.
- The platform enforces one gate, so a rule that defers to the platform defers to almost nothing.
- `dismiss_stale_reviews: true` means an approval dies on the next push, so "get approved, then
  fix a review finding" does not compose.
- Any answer must be auditable afterwards by someone other than the person it governs.

## Considered options

1. **Author may merge against the bar above.** Costs: depends on Open question A. Under A2 it is
   a bypass with a logging requirement and should be labelled as such.
2. **Leave the rule; staff review properly** — assignment, rotation, escalation. No new risk,
   and the honest answer if the group says no. Costs: untested as a deliberate practice.
3. **Add required status checks first, then allow author merge.** Better on the automated half.
   Costs: it is #154's work and does not exist; and it would *not* restore independent human
   acceptance, nor bind a merge path that can still bypass it while `enforce_admins` is false.
4. **Reduce the required review count to zero for everyone.** Rejected: removes the gate for all
   contributors to solve one contributor's queue.

Option 3 was called "the destination" in the first draft. That overstated it — required checks
enforce their own predicates, not review quality — and is corrected here.

## Consequences

To be completed with the decision.

**Stated now, whatever is chosen.** This replaces a gate another person holds with a gate the
author holds, moderated only by whatever Open question A settles. Under A2 the external evidence
is a comment the author writes about their own work. That is a real reduction in assurance,
accepted in exchange for unblocking work — not a claim that nothing changes.

## Security implications

No change to credentials, permissions or exposure; the bypass capability already exists.

What changes is assurance, in one direction. The review requirement is currently the **only**
enforced gate on `launchpad`, so this makes the trunk's protection depend on the author's own
discipline for the author's own changes. Conditions 3 and 4 are what keep that auditable rather
than invisible — and under A2 they do not make it independent.

Open question B matters most here: without excluded change classes, the exception's first
legitimate use could be on a workflow file, a credential path, or an ADR that widens bypass
authority further. That should be settled before acceptance, not after.

## Provenance

Raised by Serina McFall on 2026-09-10 while finished pull requests waited on a reviewer and
blocked dependent work. Drafted by an agent at her instruction as `Proposed`.

Revised the same day after an independent adversarial review (Codex, a different model from the
one that drafted it) returned REQUEST CHANGES with one Blocker and eleven further findings
against the first draft. Findings accepted and applied: the "or answered" gap in condition 3,
"every check that ran" passing on zero checks, findings lapsing on a push, condition 4 being a
post-hoc self-attestation, the false claim that self-merge necessarily requires an admin bypass,
the "gate nobody has staffed" framing, the overstatement of option 3, calling the §5 change a
clarification, and the absence of scope limits and an adoption process. One finding was
disputed and not applied: the review argued *"an approval is dismissed by any later push"* is
too broad, but the GitHub setting is `dismiss_stale_reviews` — "dismiss stale pull request
approvals when new commits are pushed" — so the original wording matches the platform. The full
review is on #2169.

Branch-protection figures were read from the GitHub API the same day and are reproducible.
