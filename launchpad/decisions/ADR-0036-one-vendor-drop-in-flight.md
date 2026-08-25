---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#302
decided_in: launchpad-26/buzz#302
supersedes: none
---

# ADR-0036 — Only one vendor drop may be in flight

## Decision

Only one vendor-drop pull request may be open at a time. A scheduled daily invocation
that finds an existing open drop does not open a second overlapping pull request, replace
the first, force-push it, or silently add a newer upstream point to its reviewed content.

Instead, that invocation records that the attempt is blocked by the active drop and records
the newest upstream commit waiting behind it. After the active drop merges, or after a human
explicitly closes it as abandoned, the next invocation starts from the then-current adopted
baseline and includes the accumulated upstream changes.

An urgent upstream security fix does not wait behind a large vendor drop. A human may
authorise a separately scoped hotfix or backport pull request for that fix. That exception is
not a concurrent vendor drop, does not replace the active drop, and is reconciled by the next
normal drop.

The daily cadence in ADR-0035 is a cadence of attempts. It does not override the existing
human review gate or guarantee that a new drop lands while the previous one remains under
review.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff delegated low-complexity, non-design ADR outcomes to
the agent even where the original risk rubric classifies them above Low; he did not
personally select this individual outcome.

## Context

Issue #302 was narrowed when vendor drops were still assumed to be unscheduled human acts.
The later daily-cadence authority in #520, #525, and #541 makes overlap a routine condition
the scheduled job must handle rather than an unlikely convention for people to remember.

Concurrent drop pull requests contain overlapping upstream history and make precedence
ambiguous. Automatically superseding the older one can discard expensive conflict
resolution and review evidence. Updating the older one to a newer upstream point while it
is under review changes what an approval means. Serialising drops preserves one coherent
candidate and lets accumulated upstream movement wait visibly rather than becoming a
second, competing candidate.

The strict rule needs a security escape hatch. Delaying one known, urgent fix behind an
unrelated large drop is a worse outcome than allowing a narrowly scoped, explicitly
authorised hotfix through the ordinary pull-request controls.

## Risk classification

**Clear Medium (4/12), high confidence.** Blast radius 1; reversibility 0;
security/trust 0; data/state 1; contracts/dependencies 1; operations/uncertainty 1.

No hard High-risk trigger applies. This sets concurrency semantics for one existing
repository workflow and affects shared Git/PR state non-destructively. It does not change
identity, credentials, branch protection, production data, public interfaces, or a
cross-repository contract, and the convention can be changed without migration. A wrong
choice can delay upstream adoption or waste conflict-resolution work, which is the bounded
operational exposure reflected in the score. Complexity is Low because this is a single
serialization default with one explicit emergency exception; complexity routes decision
authority and does not lower the risk score.

## Consequences

- Reviewers see one authoritative vendor-drop candidate.
- Conflict-resolution work and review evidence are not discarded by an automatic
  supersession.
- A daily run can be successful as an observable blocked attempt without creating another
  pull request.
- Upstream changes accumulate while a drop waits for review, so the next drop may be larger
  than one day's movement.
- An abandoned drop must be closed explicitly before the next begins.
- A known urgent security fix has a focused human-authorised route that does not weaken the
  normal serialization rule.
- Task #541 already owns the scheduled job and therefore owns detecting an active drop and
  reporting the blocked attempt; no additional implementation task is required.

## Security implications

The one-in-flight rule reduces ambiguity about which untrusted upstream content is being
reviewed and prevents automation from invalidating an approval by replacing its input. Its
availability cost is delayed adoption while review is pending. The narrowly scoped hotfix
exception keeps that delay from becoming a blanket rule against urgent security fixes, and
still requires an attributable human instruction plus the normal pull-request controls.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization for
low-complexity ADRs. The original alternatives remain in #302; ADR-0035 and the later daily
delivery authority in #520, #525, and #541 establish the cadence this record serialises.
