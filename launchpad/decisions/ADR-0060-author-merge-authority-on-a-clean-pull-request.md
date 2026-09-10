---
status: Proposed
date: 2026-09-10
issue: launchpad-26/buzz#2169
decided_in: launchpad-26/buzz#2169
supersedes: none
---

# ADR-0060 — An author may merge their own pull request when it meets a stated bar

> **Status is `Proposed`, deliberately.** The cohort has been asked and has not yet answered.
> This document exists so the group reacts to a concrete rule rather than an abstract question.
> Nothing in it is in force, and `launchpad/AGENTS.md` §5 is unchanged until it is accepted.

## Decision

**Proposed:** a pull request's author may merge it themselves, using their admin bypass of the
one-approval requirement, **only** when all of the following hold. If any is unmet, the pull
request waits for a reviewer as it does today.

1. **Every check that ran is green**, and none is still running.
2. **No unresolved `CHANGES_REQUESTED` review** stands against the current head.
3. **An independent review has been run and posted on the pull request** — by a model other
   than the one that wrote the change, or by a person other than the author. Its findings are
   either fixed or answered in a comment.
4. **The bypass is recorded on the pull request** — a comment stating that the author merged
   their own work, which of these conditions were met, and how the independent review was run.
   A bypass nobody wrote down is indistinguishable from one nobody noticed.

Merging past a failing check, past a standing `CHANGES_REQUESTED`, or without an independent
review is **not** covered by this and remains what §5 already calls routing around the platform.

## Context

### The bottleneck is real

`launchpad` requires one approving review, and GitHub does not let an author approve their own
pull request. So every pull request an author opens needs another person, for changes of any
size. Two examples from 2026-09-10 alone: #2109 — a complete, tested fix for a gate that had
already forced three `--no-verify` pushes that day — sat four days with no reviewer ever
assigned; and #574 sat two weeks carrying a title that was no longer true. In both cases the
work was finished and nothing routed it to a human.

### The bar has to live here, because the platform enforces almost nothing

This is the part most likely to be skipped, so it is stated plainly. On `launchpad` today:

```
required_approving_review_count: 1
required_status_checks.contexts: []      # none
rulesets:                                 # none
enforce_admins: false                     # admins already bypass all of it
```

The single enforced gate is that one approval. **A rule phrased as "merge when it is clean and
mergeable" would therefore mean "merge when nothing is stopping you"** — because after the
bypass nothing is. GitHub's own `mergeable: MERGEABLE` only means the branch has no conflicts;
it does not consider CI here, since no check is required. Hence conditions 1–3 above: they are
the gate, and they exist only in this document.

`enforce_admins: false` also means the capability already exists and always has. This decision
is about when it is legitimate to use, not about granting it.

### Why an independent review is a condition and not a nicety

On 2026-09-10 two documentation pull requests (#2156, #2163) were fully CI-green and had been
judged ready by their author. An independent cross-model review returned REQUEST CHANGES on
both, finding among other things a proposed guard that contradicted the very decision it was
attached to, and wording that granted exactly what its own pull-request body said it refused. A
third pull request reviewed the same way (#2161, a different author) carried a Blocker: a
credential split that left the relay unable to authenticate at all.

Green CI meant nothing about correctness, which is unsurprising given that no check is required.
An author is also the worst-placed reader of their own work. Condition 3 is what keeps "clean"
from collapsing into "the author thinks so."

### What the existing rules do and do not say

- **`AGENTS.md` §5** says *"No `gh pr merge --admin`, and no other bypass of branch
  protection."* That governs **agents**, in the AI contributor guide — but nothing at that line
  says so, and an agent reading it will refuse to act on an author's instruction under this
  decision. §5 needs one clarifying sentence when this is accepted.
- **ADR-0052** governs an *agent* approving or merging on quoted human instruction. This
  decision is about a *human's* authority over their own pull request — a different subject,
  which is why this is a new record rather than an amendment.
- **`launchpad/README.md`** told contributors to expect **two** approving reviews when the
  branch enforces one. Corrected in the same pull request as this document, since it is wrong
  either way.

### The event on the other side of the argument

§5 cites its own motivation: on 2026-08-28, **132 pull requests were merged with `--admin` past
77 changes-requested reviews and unresolved CI.** That is the strongest argument against
loosening anything here and it should not be waved away.

It is also not this. That event was merging past *failing gates and standing rejections* —
conditions 1 and 2 above exist precisely to exclude it. The distinction the group is being asked
to accept is between bypassing a gate that has spoken and bypassing a gate that nobody has
staffed.

## Decision drivers

- Work that is finished and unreviewed for days is a real cost, and it falls hardest on the
  contributor who opens the most pull requests.
- The platform enforces one gate; a rule that defers to the platform therefore defers to almost
  nothing.
- An author cannot approve their own pull request, so "self-merge" necessarily means an admin
  bypass rather than a self-approval. There is no lighter mechanism available.
- `dismiss_stale: true` means any approval is dismissed by the next push, so "get approved, then
  fix a review finding" does not compose — a practical reason the current path stalls.
- Whatever is decided must be visible after the fact. An unrecorded bypass cannot be audited.

## Considered options

1. **Author may merge against a stated bar.** **Proposed above.** Costs: it relies on the author
   applying conditions 1–3 honestly, with condition 4 as the only backstop.
2. **Leave the rule as is; assign reviewers faster.** No new risk, and the honest option if the
   group's answer is no. Costs: it has not worked so far — #2109 and #574 are the evidence, and
   nothing in this option changes what caused them.
3. **Add required status checks, then allow author merge.** Strictly better than option 1,
   because the bar would be enforced rather than written. Costs: it is #154's work and does not
   exist yet; adopting it as a precondition means the bottleneck persists until it ships.
4. **Reduce the required review count to zero for everyone.** Rejected without much thought: it
   removes the gate for all contributors to solve one contributor's queue.

Option 3 is the destination. Option 1 is what is available now, and it should be re-examined
when #154 lands.

## Consequences

**To be completed with the decision.** If accepted, at minimum: `AGENTS.md` §5 gains a sentence
distinguishing the agent prohibition from the author path, and this document becomes the thing a
reviewer points at when a bypass comment appears on a pull request.

**Bad, stated now.** Conditions 1–3 are self-assessed. This decision replaces a gate another
person holds with a gate the author holds, and the only external evidence is the comment
required by condition 4. That is a real reduction in assurance, accepted deliberately in
exchange for unblocking work — not a claim that nothing changes.

## Security implications

No change to credentials, permissions or exposure; the bypass capability already exists via
`enforce_admins: false` and an admin role.

What changes is assurance, and only in one direction. The review requirement is currently the
only enforced gate on `launchpad`, so this decision makes the trunk's protection depend on an
author's own discipline for their own changes. Condition 3 (independent review) and condition 4
(a written record) are what keep that auditable rather than invisible. If the group is
uncomfortable, option 3 — requiring status checks first — is the version that does not trade
assurance away.

## Provenance

Raised by Serina McFall on 2026-09-10, while several finished pull requests were waiting on a
reviewer and blocking dependent work. Drafted by an agent at her instruction, as `Proposed`,
pending the cohort's answer. The supporting figures — branch protection settings, the review
findings of 2026-09-10, and the ages of #2109 and #574 — were gathered the same day and are
reproducible from the repository and its pull request history.
