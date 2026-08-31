---
status: Accepted
date: 2026-08-31
issue: launchpad-26/buzz#1956
decided_in: launchpad-26/buzz#1956
supersedes: none
---

# ADR-0054 — A Feature's whole batch lands in one pull request; the size cap is withdrawn

## Decision

**Option A, selected by @tucktuck101 on 2026-08-31 in #1956.**

**All of the work done for one Feature lands in one pull request, whatever its size.** The
child Tasks of a Feature are reviewed together, as one Feature's worth of work, and a
Feature does not split into sequential batch pull requests because of how large it is.

**ADR-0052 part C's numeric cap — 1,500 added lines or 10 changed files, whichever binds
first — is withdrawn.** Part C's other half, *a Feature and not a Task is the PR-worthy
unit*, is retained and is now unconditional.

`launchpad/scripts/pr_body_check.py` no longer fails a pull request for its size. It still
**reports** additions and changed files as a note, so the number a reviewer is taking on is
stated on every batch rather than discovered by scrolling.

**Nothing else in ADR-0052 changes.** Parts A and B (delegated authority, self-identifying
approvals), D (deferred blockers and the closed never-deferrable list), E (the ceiling of
five open `deferred-blocker` issues), F (pre-authorised ordinary deferral) and G (no bypass
of CI or branch protection) keep their current scope exactly. This record touches one
number and one sentence.

This rejects **option B** (keep the cap, give up one-Feature-one-PR) and **option C** (cap
only Features that modify existing code, exempt purely additive ones).

## Context

Part C contradicted itself, and the contradiction resolved the wrong way.

It says *"The child Tasks of one Feature land in one pull request"* and then *"A Feature
whose batch would exceed the cap splits into sequential batch pull requests."* Features in
this repository carry **15–41 children** — ADR-0052's own Context measures #619 → 41,
#620 → 32, #621 → 31, `buzz-infrastructure` #1040 → 15. Every one of them exceeds 1,500
added lines or 10 changed files. So the second sentence cancelled the first in every real
case, and the operating rule became one PR per batch of two or three Tasks: the micro-PR
volume ADR-0052 was written to end.

**Feature #612 is the worked case.** Its collaboration-capability corpus run produced 25
batch pull requests — #1904, #1911–#1934, #1939 — each individually within the cap. They
were then consolidated by hand into **PR #1944, at +16,113 lines across 70 files**, because
25 PRs is not a reviewable presentation of one Feature either. The cap did not prevent a
16,000-line review; it prevented that review from being requested once, and it produced 25
review requests plus a manual consolidation on top.

**The mechanism was already inoperative for the shape it aimed at.** `check_cap` in
`launchpad/scripts/pr_body_check.py` returns early when a pull request closes one issue or
fewer. PR #1944 carries a single `Closes #612`, so its `check` job read
`PR_ADDITIONS: 16113`, `PR_CHANGED_FILES: 70` and raised **no cap error** — its only
failure was a missing `by:agent` label. Enforcement therefore keyed on how a body was
worded, not on how large the diff was: it bound the small per-batch PRs and exempted the
large one-Feature PR. A gate that fires on the compliant shape and not the oversized one is
not bounding review load.

**The tooling had already moved.** PR #1945 (merged 2026-08-31) changed
`.claude/skills/corpus-batch-author/SKILL.md` to produce one pull request per Feature rather
than one per batch, precisely so the next Feature would not need #1944's manual
consolidation. Part C and the skill were in open disagreement; this record settles it in the
skill's direction.

## Consequences

- **Pull request count falls to one per Feature.** At 15–41 children that is the
  twentyfold reduction ADR-0052 predicted and part C's cap prevented.
- **A reviewer takes on a whole Feature at once, and some of those are very large.** #1944's
  16,113 lines is not a line-by-line read. What makes it reviewable is per-child-Task
  commits: `launchpad/AGENTS.md` §6's interim *one commit per child Task* rule stops being a
  hedge against an unsettled squash question and becomes the review structure itself.
- **This removes the only mechanical bound on diff size, and nothing replaces it.** Stated
  plainly rather than dressed up: review thoroughness on a large batch now rests on
  reviewer discipline. ADR-0052 already conceded the cap did not deliver reviewability
  either — *"1,500 added lines is roughly four times the current median pull request. The
  cap bounds the damage; it does not make a batch as reviewable as a single-issue diff"* —
  so what is lost is a bound that was both self-cancelling and misdirected, not a working
  control.
- **The squash-versus-merge question ADR-0052 left open is now load-bearing.** Squashing a
  41-Task Feature into one commit discards exactly the per-Task history that a reviewer of a
  16,000-line PR walks. This record does not decide it — deciding it here would put a ruling
  nobody made into a decision record — but it raises the cost of leaving it open, and it is
  the next question to take to a human.
- **`dismiss_stale_reviews` churn gets worse.** One long-lived Feature branch collecting 41
  Tasks has its approval dismissed on every push. ADR-0052 flagged this as the most likely
  early friction; consolidating further into one PR per Feature increases the window in which
  it bites.
- **Size stays visible.** The check reports `+N lines across M files` on every batch, so
  removing the gate does not remove the number.

## Security implications

**No change to any never-deferrable class.** ADR-0052 part D's closed list — a credential,
secret or password hash in the diff; a disclosure-boundary violation; a failing
deterministic check; anything that breaks the shared trunk — is untouched and remains
non-deferrable with or without an instruction. Part G's prohibition on bypassing branch
protection or merging past failing checks is likewise unchanged.

**The residual risk this record does add:** a secret or a disclosure-boundary violation is
easier to miss in a 16,000-line diff than in a 300-line one, and the two classes that matter
most are the two that are unrecoverable after merge. The compensating controls are
deterministic and unaffected — secret scanning, the `check`/`validate`/`audit` jobs, and the
disclosure-boundary rules in §8 — which is exactly why part D puts them outside human
judgement. This record relies on those checks more heavily than the capped regime did, and
does not pretend a human reading 16,000 lines is the control.

The withdrawn cap was never a security control. It bounded review effort, not exposure, and
as measured above it did not bind the largest pull requests at all.

## Supersedes

none — this **amends `ADR-0052` part C**. ADR-0052 stays Accepted and in force; its part C
now reads as one-Feature-one-PR without a numeric cap. Nothing else in that record is
affected, and no earlier record is retired.

## Amends

- **`ADR-0052` part C** — the 1,500-line / 10-file cap and the split-into-sequential-batches
  instruction are withdrawn. The Feature-is-the-PR-unit rule is retained unconditionally.
- **`launchpad/AGENTS.md` §6** — the capped-batch bullet is replaced, amended in this same
  pull request so the two documents do not disagree.
- **`launchpad/scripts/pr_body_check.py`** — `check_cap` is replaced by `report_size`,
  which prints the batch's additions and changed files and returns no error, changed in
  this same pull request for the same reason. A rule withdrawn in prose while the script
  still enforces it is not withdrawn.

## Related

- **`ADR-0052` (#1765)** — the record amended here. Its parts A, B, D, E, F and G stand;
  its Context supplies the 15–41 child counts and the 2026-08-28 bypass event that motivated
  batching in the first place.
- **`ADR-0019`** — superseded by ADR-0052, cited here only for the rule that survives both:
  a required status check may only ever be a deterministic script. Removing the cap removes
  a deterministic check, which is why the size number is still reported.
- **#612 / PR #1944** — the 25-batch Feature and its +16,113-line consolidation.
- **PR #1945** — `corpus-batch-author`'s one-PR-per-Feature default, merged before this
  record and previously in conflict with part C.

## Provenance

Decided by @tucktuck101 in a working session on 2026-08-31, instructing it explicitly. The
instruction is quoted verbatim in #1956's *Decision outcome* comment and is not tidied.

The evidence was read rather than recalled: part C's text and ADR-0052's child counts from
`launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md`; `check_cap`'s
single-issue early return from `launchpad/scripts/pr_body_check.py:369-405`; #1944's
`additions: 16113` / `changedFiles: 70` and its `check`-job log line
`PR_ADDITIONS: 16113` with no cap error, from the GitHub API and the job log for run
33352691883; PR #1945's merge time and diff from the same API. ADR-0053 was confirmed
already claimed by open PR #1941 before this record took 0054.

**Not verified:** no Feature has yet been merged under this rule, so the claim that
per-child-Task commits make a 16,000-line batch reviewable is an expectation, not a measured
result. The first Feature merged under it is the test. Whether option C's
additive-versus-modifying distinction would have been workable was never settled — the
option was rejected in favour of A without measuring it.
