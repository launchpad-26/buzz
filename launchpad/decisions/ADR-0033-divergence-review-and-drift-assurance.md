---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#301
decided_in: launchpad-26/buzz#301
supersedes: none
---

# ADR-0033 — Divergence requires human review and deterministic drift detection

## Decision

**Not yet settled by a human, and the option below is not one #301 offered.** This
record is `Proposed`, not `Accepted`. #301's considered options are A (deterministic
check in `launchpad-pr-check.yml`), B (generated register with no check), C (convention
only) and D (content/prose validation). `CODEOWNERS` appears in none of them, so the
pairing below is a fifth option composed while drafting. It has been added to #301 as
Option E so a human can weigh it against the original four; `launchpad/AGENTS.md` §5.1
reserves that choice for a human. When a human states the outcome in #301, this
record's `status` becomes `Accepted`.

The proposed option: the upstream boundary receives two complementary assurances.

1. `CODEOWNERS` requests human review when an ordinary pull request touches the
   upstream-owned boundary.
2. A deterministic scheduled or post-merge check compares the divergence register's
   paths with the computed contested set and reports an unmatched path in either set.

**Scope of the set comparison.** The comparison covers only upstream-owned paths. Pure
fork additions are excluded: #301 measured 21 of 48 diverged files as fork-only files
that cannot conflict, and a check demanding a register row for each of them fires on
files that will never matter. Task #1428 owns drawing that boundary precisely and is
the place to record how it is computed.

**What "reports" means today, stated plainly.** `launchpad` has no required status
checks, so this control is *advisory* until the required-checks work (#154) lands.
Research #369 ranks a post-merge assertion as a *"[r]eport nobody reads"* with zero
enforcement, and #301 says it directly: *"An advisory check on a branch with no
required checks is, in practice, a comment."* This record therefore does not claim the
check fails loudly. Task #1428 must name the notification surface — where an unmatched
path is sent and who is expected to act on it — and until it does, the second assurance
detects drift without guaranteeing anyone sees it.

The drift check validates membership and required structure, not whether a prose
justification is correct. Vendor-drop pull requests must not create a blind spot: the
set comparison runs independently of any ordinary-PR exemption.

## Context

ADR-0021 makes the divergence register the durable record of a declined upstream
change, while ADR-0022 limits per-drop adjudication to the registered contested
surface. A missing row is therefore a lost decision. Research in #369 established
that a small `CODEOWNERS` rule accurately requests review on the boundary — a six-line
ruleset tested against 4,351 tracked files, partitioning 4,029 upstream-owned from 322
fork-owned with a two-file residue — at a measured cost of one review request per pull
request touching an upstream path (11 of 60 merged PRs in its sample). Human review
cannot prove the register remains complete. Conversely, a mechanical set check can
prove completeness but not informed review. Both properties are required and neither
substitutes for the other.

## Consequences

- Boundary changes receive a visible human review request.
- Register drift is detected even where a drop workflow bypasses ordinary path checks.
- The deterministic check remains explainable and stable because it compares sets
  rather than asking a model to judge prose.
- Contributors touching the boundary incur an additional review request on roughly one
  pull request in six, per #369's sample.
- Two controls must be maintained, because they answer different questions.
- A genuinely inaccurate but structurally complete reason can still pass; review owns
  judgement.
- The second control is advisory until #154 lands, so for now drift is *recorded*
  rather than *blocked*.
- Task #1428 (*enforce divergence review and detect register drift*, under Feature
  #525) implements both assurances, owns the path scope, and owns the notification
  surface. Task #537 does not implement either.

## Security implications

The controls reduce the chance that an undocumented divergence silently suppresses an
upstream security fix. They add no credential and make no model verdict authoritative.
Because the drift check is advisory until #154, a suppressed security-relevant
divergence is currently detectable but not blocked. Security relevance still requires
human judgement in the register/drop process.

## Supersedes

none

## Provenance

Drafted by an agent from #301's options plus a fifth option composed while drafting;
the decision itself is pending a human, as stated at the top of *Decision*. Full
options are in #301 and the measured enforcement evidence is in #369.
