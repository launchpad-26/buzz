---
status: Superseded by ADR-0052
date: 2026-08-21
issue: launchpad-26/buzz#154
decided_in: launchpad-26/buzz#154
supersedes: none
---

# ADR-0019 — Deterministic checks may gate a merge; model verdicts may only annotate

## Decision

**Three rulings, taken together.**

1. **A required status check may only ever be a deterministic script.** A check with fixed,
   inspectable rules — the kind a reviewer used to verify by eye — may block a merge. The
   review agents (`review-code`, `review-tests`, `review-adjudicate`, `review-final`) keep
   running and keep posting findings, and their verdict **never** turns a check green or red.

2. **A human approval remains required, always.** The aim was never to remove the first
   human. Note that a status check *cannot* substitute for one in any case: GitHub treats
   required approving reviews and required status checks as two independent gates, and a
   check can never satisfy the review count. A GitHub App submitting a literal `APPROVE`
   review is rejected as a mechanism — it would make an automated approval indistinguishable
   from a person's in the UI, and it collides with `launchpad/AGENTS.md` rule 1.

3. **Enforcement is deferred until the CI/CD pipeline is live.** The policy above is settled
   now; *marking* checks as required waits on the DevSecOps CI/CD pipeline programme
   (`launchpad-26/buzz-infrastructure` #105). Required checks configured ahead of that
   pipeline would be re-configured by it. [#153](https://github.com/launchpad-26/buzz/issues/153)
   and [#146](https://github.com/launchpad-26/buzz/issues/146) therefore remain open by
   decision, not by obstruction.

**`enforce_admins` stays off.** Recorded explicitly rather than left silent: the four repository
admins (measured 2026-08-24: `joshuavial`, `baradev`, `tucktuck101`, `jatin-puri-coder`) can
bypass required checks once they exist. This is a deliberate acceptance, not an
oversight — see Consequences.

## Context

Review in this fork is advisory, and the cost of that is documented rather than hypothetical.
The cohort's local pre-push gate states it in its own header: *"Hook is the bouncer; the required check is the
locked door. Both, or say plainly which one you have."* On 2026-08-03 a pull request was merged
from GitHub's UI while its final review was still running; the hook worked correctly and could
do nothing, because it runs on one machine and the merge happened on the platform. On
2026-08-13 a `review-final` pass completed after 6m 4s and its verdict was lost when the
session died. Nothing noticed.

The case against letting model verdicts gate is a measurement, not a preference. #109 (as
amended, primary source [arXiv:2603.06594](https://arxiv.org/abs/2603.06594)) records
AUROC 0.48–0.64 against 6,642 human-verified labels on adversarial security claims — measured
for one judge (JailJudge), one victim model and two attacks, not a range across judges (#122's
correction) — near chance at the bottom of that range. At that accuracy the false-block rate is not
a tuning problem. The variant with a human override was rejected for a different reason: the
override becomes the path of least resistance on the first busy afternoon, and afterwards a
dismissed false positive is indistinguishable from a dismissed true one. That converts a gate
into a log.

Nothing new is built by this decision. The method is extraction, and it already has two working
instances: `launchpad/scripts/pr_body_check.py` and `launchpad/scripts/adr_boundary_check.py`.
Every finding with a fixed rule graduates into a script with controls; what cannot be reduced
to a rule stays judgement, posts a comment, and never blocks.

**Two premises in #154 as filed are now known to be wrong, and are corrected here.**

- **There is no ruleset.** #154 could not determine which ruleset enforces `launchpad` and named
  #70 and #72 as blocking dependencies. Read with repository admin on 2026-08-21:
  `repos/launchpad-26/buzz/rulesets` returns zero entries, and enforcement is **classic branch
  protection**. A required check is added there, not to a repository or organisation ruleset.
  That dependency is resolved; #70 and #72 remain valuable for their own reasons.
- **Required approvals is 1, not 2.** #154 was written against the merge box on #144 reporting
  two approving reviews required, observed 2026-08-13. The setting was already 1 before any
  change on 2026-08-21. The stated goal — stop waiting on a *second* human — was therefore
  already met by something other than this decision, so what this record buys is the locked
  door, not throughput.

Also worth recording, since #154 predates it: `launchpad` gained **push restrictions** on
2026-08-21 — eleven named users may merge. That is a third platform-enforced gate alongside the
approval requirement and the (still absent) required checks.

## Consequences

**Good.** The policy is settled before the pipeline is built, so the pipeline implements a
decided rule rather than inventing one. The line is drawn where the evidence puts it:
deterministic rules gate, judgement annotates. The extraction method needs no new
infrastructure, and each required check added later is something the team already found worth
checking by hand.

**Bad, stated honestly.**

- **The locked door does not exist yet, and this decision does not create it.** Zero required
  status checks are configured. `adr-boundary` runs and passes on every pull request but is not
  required, so it blocks nothing. The 2026-08-03 failure mode — a merge landing past a review
  that is still running — remains live for as long as enforcement is deferred. Deferring is a
  choice with that cost attached.
- **Admins bypass.** With `enforce_admins` off, four of the eleven people who can merge are
  exempt from whatever checks become required. Measured 2026-08-24, ten of the last twelve
  merges into `launchpad` were performed by a non-admin (`maintain` role), who would be fully
  bound by a required check; the other two by an admin, who is exempt. The bypass therefore
  exempts an account doing a real share of recent merging while binding the account doing most
  of it — which makes the exemption a live cost today, not a dormant one. Accepted deliberately,
  in exchange for keeping an emergency-merge path that does not depend on a second person being
  awake.
- **One human plus a script is less review than two humans.** Two people reading a diff catch
  different things; a person and a deterministic check do not. The drop from two approvals to
  one happened outside this decision, but this record is where the cost should be named rather
  than left implicit.
- **Deferral now carries a review date**: revisit this record if `buzz-infrastructure` #105 has
  not landed by **2026-09-05** (two weeks before the cohort's 2026-09-17 hard end). If #105 slips,
  this ruling quietly becomes "review is advisory" again with a decision record that reads as
  though something was fixed.

## Security implications

This decision governs what may block a merge on a public repository whose default branch eleven
people can push to, so it is the enforcement half of the fork's change-control story.

Two exposures are accepted by it. First, until enforcement lands, the only mechanical barrier
between an unreviewed change and `launchpad` is one human approval and the push restriction —
the review chain's findings carry no weight the platform recognises. Second, `enforce_admins`
off means the eventual barrier is bypassable by four accounts; a compromise of any one of them
defeats the check set entirely, which is a reason to keep admin count low rather than a reason
to reverse this ruling.

The prohibition on model verdicts gating is itself a security control. A check that turns green
on a model's opinion is an agent approving work, which `launchpad/AGENTS.md` rule 1 forbids, and
at AUROC 0.48–0.64 it would also be an unreliable one. Preferring CI to local hooks carries a
further safety property learned expensively: on 2026-08-13 a work-in-progress edit to
a local safety hook, mid-edit, refused *every* tool call and locked two working sessions out with no recovery
from inside a session. A broken CI check fails a pull request; it cannot take a machine away
from the person using it.

## Provenance

Decided by @tucktuck101 in conversation on 2026-08-21, after a recommendation to ratify the line
drafted in #154. The direction in #154 is @serina-mcfall's, who asked that anything affecting the
architecture be decided at group level rather than settled inside a pull request.

Two amendments were recommended and both taken: `enforce_admins` addressed in this record rather
than deferred to another (decided **off**, recorded explicitly), and the two incorrect premises
in #154 corrected above. Enforcement timing — deferral to `buzz-infrastructure` #105 — was
@tucktuck101's, not part of the original recommendation.

Drafted by an AI agent (Claude Opus 5). Verified on 2026-08-21 with repository admin: the absence
of repository rulesets, that enforcement is classic branch protection, that zero required status
checks are configured, that required approvals was already 1 before any change that day, and that
`adr-boundary` runs and passes without being required. Not verified: the AUROC figures themselves,
which are quoted from #109 as amended after #122's verification pass (#118's copy of them
predates that pass and still carries a phrase #122 established is not in the paper).
