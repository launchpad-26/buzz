---
status: Accepted
date: 2026-08-28
issue: launchpad-26/buzz#1765
decided_in: launchpad-26/buzz#1765
supersedes: ADR-0019
---

# ADR-0052 — Agents may approve and merge on quoted human instruction; a Feature is the PR unit; blockers defer

## Decision

**Six parts, taken together. Parts A and B replace the prohibition; C, D, E and F are
what make it survivable.**

**A. Delegated authority, per action, on quoted instruction.** An agent may fill an ADR
*Decision outcome*, submit a code review, request changes, re-review on a requested
review, approve a pull request, and merge it — but only under all five of the following,
together:

1. **A human explicitly instructed the specific action, in the current session.**
   Standing permission does not exist; "while you're in there" does not accumulate.
2. **The instruction is quoted verbatim in the artifact** — the review body, the merge
   commit, or the ADR *Decision outcome* — **and the instructing human is named there.**
   The artifact is the record: it is in git history, addressable, and readable by anyone
   auditing later. A chat session is none of those things, which is why the quote has to
   be copied into the artifact rather than referred to.

   **An earlier draft also required a link to a comment from the human's own account.
   That requirement is withdrawn as ceremony.** While an agent runs under a human's
   token, a comment it could link is authored by the same account as the body it sits
   beside, so it proves nothing the quote does not already prove, and it overstated the
   assurance this record provides. Real attribution needs a separate identity — the agent
   authoring under its own GitHub App, as ADR-0039 already establishes for drop pull
   requests — and until that exists this record does not pretend otherwise.
3. **Below 75% confidence in what the human is asking for, the agent stops and asks.**
   Carried over unchanged from `buzz-infrastructure` ADR-0015 rule 7.3.
4. **Scope is exactly what was instructed.** One instruction, one action. One ruling, one
   ADR question. One approval, one pull request.
5. **Every exercise is recorded** where the repository records such things, naming itself
   as agent-exercised and on whose instruction.

These five conditions are deliberately the shape of `buzz-infrastructure` ADR-0015's
rule 7, which already governs agent action on an irreversible surface. Reusing a
structure that survived review is worth more here than inventing a second one.

**B. An approval submitted under this authority must be self-identifying.** Its body
states that it is agent-submitted, names the instructing human, and quotes the
instruction. An approval that does not do all three is invalid under this decision.

This answers ADR-0019 rather than ignoring it. ADR-0019 rejected an automated `APPROVE`
because it would be *"indistinguishable from a person's in the UI"* — an objection about
indistinguishability, not about authority. A self-identifying approval is
distinguishable, so the objection is met on its own terms.

**C. A Feature — not a Task — is the PR-worthy unit, and batches are capped.** The child
Tasks of one Feature land in one pull request. A Feature whose batch would exceed the cap
splits into sequential batch pull requests rather than one oversized one. The cap is a
number, not a judgement: **1,500 added lines or 10 changed files, whichever binds
first.**

**D. A blocker found in review is deferred, not blocking — except for a closed list.** An
agent that finds a defect while preparing or reviewing a batch files an issue parented to
that pull request's Feature, labels it `deferred-blocker`, names it in the pull request
body, and proceeds with the merge.

**Never deferrable. This list is closed:**

- a credential, secret, or password hash in the diff;
- a disclosure-boundary violation — host state into a public repository, or private
  material outside its repository;
- a failing **deterministic** check;
- anything that leaves the shared trunk broken for other agents.

The four are not a style preference. The first two are unrecoverable on merge: a pushed
secret is on every clone and rotation becomes the remedy, and a disclosure breach cannot
be un-pushed. The third is the one thing ADR-0019 permits to gate, and deferring it would
invert that ruling. The fourth is how one merge becomes everyone's problem.

**E. Deferred work carries a ceiling.** A Feature may not close while it holds open
`deferred-blocker` issues, and a Feature holding more than **five** has its next batch
refused until it is back under. Without E, part D reproduces exactly the parallel queue
§4 rule 6 already forbids — *"PRDs look done while their gaps live in a parallel queue."*
(In `buzz-infrastructure` the equivalent is its §5 rule 6; the numbering differs between
the two repos.)

**F. Deferral of anything OUTSIDE the closed list is pre-authorised by this record** and
needs no per-case instruction. The four classes named in part D are never deferrable at
all, by anyone, with or without an instruction. Requiring a quoted instruction for every
*ordinary* deferral would move the bottleneck rather than remove it, which defeats the
purpose of the change.

**G. Delegated authority never bypasses CI or any rule GitHub enforces.** An agent
exercising parts A and B works *inside* the platform's gates, never around them:

- **No `--admin`, and no other bypass of branch protection.** The token an agent runs
  under holds admin on these repositories and `enforce_admins` is off, so the capability
  is present. Possessing it is not permission to use it.
- **No approving or merging while checks are failing or still running.** A failing
  deterministic check is already never-deferrable under part D; this states the merge-time
  consequence of that plainly. Use `--auto` and let the platform merge when the gates go
  green, rather than merging ahead of them.
- **No dismissing reviews, no force-pushing over a review, no altering branch protection,
  required checks, or rulesets** as part of getting a change in.
- **A blocked merge is a result, not an obstacle.** If the platform refuses, the answer is
  to fix the change or escalate to a human — never to reach for a stronger credential.

This is not a new principle; it is the one that was broken on 2026-08-28, when 132 pull
requests were merged with `--admin` past 77 changes-requested reviews and unresolved CI.
That event is this record's own motivating evidence, and a decision that widens agent
authority without closing that door would be reproducing the failure it cites.

Where a repository's `pr-review-panel` skill already states the same limit — *"Never
`gh pr merge --admin` or any other bypass of branch protection"* — this record makes it
binding on every agent, not only on that lane.

**Retained from ADR-0019, unchanged and restated here because this record supersedes it
in full:**

1. **A required status check may only ever be a deterministic script.** The review agents
   keep running and keep posting findings, and their verdict never turns a check green or
   red. Model verdict reliability was measured at AUROC 0.48–0.64; nothing in this
   decision revisits that measurement.
2. **Enforcement of required checks stays deferred** until the CI/CD pipeline programme
   (`launchpad-26/buzz-infrastructure` #105) is live. `launchpad-26/buzz` #153 and #146
   remain open by decision, not by obstruction. **ADR-0019's review date carries over
   unchanged: revisit this if #105 has not landed by 2026-09-05**, two weeks before the
   cohort's 2026-09-17 hard end. That date matters more under this record than it did
   under ADR-0019, because there is no longer an independent human approval standing
   behind the deferral — if #105 slips, delegated authority is operating with neither a
   second human nor a required check.
3. **`enforce_admins` stays off.** The four repository admins can bypass required checks
   once they exist. A deliberate acceptance, not an oversight.

**Not changed by this decision.** `buzz-infrastructure` §6 rules 7 and 8 — agent host
access, and the prohibition on applying destructive host changes — keep their current
scope exactly. Delegated review and merge authority **does not extend to any action
against the live host.** Nothing here loosens ADR-0015.

## Context

Agent-authored work outran the single human gate that admits it.

Measured 2026-08-28: 110 open pull requests on `launchpad` and 31 on
`buzz-infrastructure`. Of those 141, **zero** were both `CLEAN` and free of
`CHANGES_REQUESTED`; 77 carried `CHANGES_REQUESTED` and 42 had unresolved CI. 107 of the
111 subsequently merged were authored by a single agent identity.

The queue was cleared by an operator using admin bypass. GitHub started only 10 workflow
runs for 103 merges, so most were never checked at all, and the merge commits recorded a
single unverifiable claim of group consensus. That is the failure this record exists to
stop recurring — not the bypass itself, but the condition that made bypass the only
available move.

Three rules combined to produce it. **One issue, one PR**, against Features carrying
15–41 children (#619 → 41, #620 → 32, #621 → 31, infrastructure #1040 → 15), generates
dozens of pull requests per Feature. **Draft everything, approve nothing** makes every
one of them a human touch. **A blocker stops a merge** adds a full re-review round for
defects a follow-up commit fixes more cheaply. Agent throughput was therefore capped by
human review capacity, and when the cap bound, the gate was discarded rather than queued.

The gate itself is thin and always was. `required_approving_review_count` is 1,
`required_status_checks` is empty, and `enforce_admins` is `false` on both trunks. What
ADR-0019 bought was never a wall; it was one human reading one diff.

## Consequences

**Good.**

Review capacity stops being the throughput cap, so the gate stops being bypassed as the
release valve. Pull request count falls roughly twentyfold at current child counts. A
defect no longer costs a review round-trip — it becomes a tracked child of the Feature
with the next action written down. And every exercise of delegated authority now carries
a verbatim instruction and a durable link, which is a materially better audit trail than
the status quo produced.

**Bad, stated honestly.**

**The audit trail rests on a quote no machine can verify.** Requiring the human's own
comment makes the instruction checkable; nothing proves the quote faithfully reproduces
what was said. Rule 6 — *do not fabricate* — remains the only control on quote fidelity,
and it is unenforceable by construction. This is the weakest joint in the decision and it
is load-bearing.

**Dictated instructions are lossy.** The instruction that produced this record contains
"A DRs", "merch", and "Uh". Verbatim quoting of speech preserves noise rather than
resolving ambiguity; where a quote is genuinely ambiguous, condition A.3 is the only
guard.

**Capped batches are still large.** 1,500 added lines is roughly four times the current
median pull request. The cap bounds the damage; it does not make a batch as reviewable as
a single-issue diff.

**Deferred blockers can become a backlog** that makes Features look finished. Part E is
the guard, and if five proves too loose it will not hold.

**`dismiss_stale_reviews` is `true` on both trunks.** Long-lived Feature branches will
have approvals dismissed on every push — the mechanism that dismissed an operator's
2026-08-26 approvals on #1480 and #1490. Under batching this churn multiplies. Whether
Feature branches keep dismiss-stale is left open, and is the most likely early friction.

**Two questions this record deliberately leaves open**, because they were not part of the
instruction and inventing an answer would put a decision nobody made into a decision
record. First, whether Feature branches keep `dismiss_stale_reviews`. Second, whether a
batch squash-merges — collapsing ten Tasks into one commit loses per-Task history and
coarsens `git bisect`, but merge commits break the convention that a PR title becomes the
commit subject on `launchpad`. Until the second is settled, `launchpad/AGENTS.md` §6
directs one commit per child Task on the branch, so the history exists to preserve if the
answer is a merge commit.

**This record was decided under the regime it replaces.** Its *Decision outcome* on
#1765 was filled by an agent, which rule 1 forbade at the time. It is the unavoidable
first case, disclosed rather than glossed: the authority was the operator's quoted
instruction, not the agent's judgement.

## Security implications

This decision **reduces the number of independent humans in the merge path from one to
zero** for any pull request where an agent exercises delegated authority. That is a real
reduction in blast-radius control, and it is the cost being accepted rather than a side
effect to be managed.

What bounds the exposure:

- The closed never-deferrable list keeps the two irreversible classes — committed
  credentials and disclosure-boundary breaches — outside delegated authority entirely.
- Deterministic checks retain sole gating power, so the mechanically verifiable half of
  review is untouched.
- Host access is excluded outright. `buzz-infrastructure` rules 7 and 8 and ADR-0015
  stand unmodified, so the highest-consequence surface in either repository gains no new
  agent authority.
- Self-identifying approvals let anyone auditing history separate agent-exercised
  approvals from human ones — which the bypass merges of 2026-08-28 did not allow.

**Residual risk, accepted:** an agent that misreads an instruction, or fabricates a
quote, can now merge unreviewed work. The compensating controls are condition A.3's
confidence gate, the verbatim-quote-plus-link requirement, and `enforce_admins` remaining
`false` so an operator can always intervene. No technical control prevents a determined
misquote. This record says so rather than implying one exists.

## Provenance

Decided by the operator (`tucktuck101`) in a working session on 2026-08-28, instructing
it explicitly. The instruction is quoted in full on #1765 with its transcription
artefacts intact; it was dictated, and was not tidied, because tidying a quote defeats
the requirement this record establishes.

`ADR-0039-app-token-authors-drop-pr.md` quotes ADR-0019's two-independent-gates finding
and its rejection of an automated `APPROVE`. Its own reasoning — that opening a pull
request produces no approval — survives intact; its citations are re-pointed at this
record.
