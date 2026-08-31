---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#302
decided_in: launchpad-26/buzz#302
supersedes: none
---

# ADR-0036 — Only one vendor drop may be in flight

## Decision

Only one vendor-drop pull request may be open at a time. A scheduled
daily invocation that finds an existing open drop does not open a second overlapping pull
request, replace the first, force-push it, or silently add a newer upstream point to its
reviewed content.

Instead, that invocation records that the attempt is blocked by the active drop and records
the newest upstream commit waiting behind it. After the active drop merges, or after a human
explicitly closes it as abandoned, the next invocation starts from the then-current adopted
baseline and includes the accumulated upstream changes.

**The security exception, bounded.** An urgent upstream security fix does not wait behind a
large vendor drop. A human may authorise a separately scoped hotfix or backport pull
request when both hold:

- the fix addresses a published upstream security advisory, or a CVE rated High or
  Critical (CVSS v3.1 base score 7.0 or above); and
- the pull request touches only the files required by that fix, and states the advisory or
  CVE identifier in its body.

Authorisation is by one of the named humans who may advance the vendor branch under
ADR-0038 (#298). Anything that does not meet both conditions waits for the next normal
drop. That exception is not a concurrent vendor drop, does not replace the active drop, and
is reconciled by the next normal drop.

The daily cadence in ADR-0035 is a cadence of attempts. It does not override the existing
human review gate or guarantee that a new drop lands while the previous one remains under
review.

## Context

Issue #302 was narrowed when vendor drops were still assumed to be unscheduled human acts.
The later daily-cadence authority in #520, #525, and #541 makes overlap a routine condition
the scheduled job must handle rather than an unlikely convention for people to remember.

**Why this is a separate record rather than folded into ADR-0035.** #302 raised folding as
the likely outcome, on the assumption that the drop-trigger decision would arrive with a
runbook clear enough to absorb it. It did not: ADR-0035 rules on *when an attempt starts*
and is silent on concurrency, and the concurrency rule here carries its own security
exception with its own authorisation path. Two rules with different subjects and different
escape hatches are clearer as two records that cite each other. This reasoning is offered
for a human to accept or reject.

Concurrent drop pull requests contain overlapping upstream history and make precedence
ambiguous. Automatically superseding the older one can discard expensive conflict
resolution and review evidence. Updating the older one to a newer upstream point while it
is under review changes what an approval means. Serialising drops preserves one coherent
candidate and lets accumulated upstream movement wait visibly rather than becoming a
second, competing candidate.

The strict rule needs a security escape hatch. Delaying one known, urgent fix behind an
unrelated large drop is a worse outcome than allowing a narrowly scoped, explicitly
authorised hotfix through the ordinary pull-request controls.

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
  normal serialization rule. A fix below the stated severity floor waits, which is a
  deliberate availability cost.
- **Task #541 does not cover this record's mechanism.** Its only acceptance criterion is
  *"a scheduled job exists that runs the daily upstream merge"* — nothing about detecting an
  active drop, recording a blocked attempt, or recording the newest upstream commit waiting
  behind it. Those must be added to #541 before it is built, or filed separately under
  Feature #525. This record does **not** claim no additional implementation work is
  required; an earlier draft inferred that from #541's ownership of the scheduled job, and
  the inference was wrong.

## Security implications

The one-in-flight rule reduces ambiguity about which untrusted upstream content is being
reviewed and prevents automation from invalidating an approval by replacing its input. Its
availability cost is delayed adoption while review is pending, including for security fixes
that fall below the exception's severity floor. The narrowly scoped hotfix exception keeps
that delay from becoming a blanket rule against urgent security fixes, and still requires an
attributable human authorisation plus the normal pull-request controls.

## Supersedes

none

## Provenance

Drafted by an agent from #302's narrowed options. Jeffrey (@tucktuck101) made the
decision on 2026-08-31 after reviewing the options (serialize with recorded blocked
attempts; concurrent drops; automatic supersession; update-in-place) with their positive
and negative consequences, the bounded security exception, and the fold-vs-separate
question; he accepted the agent's recommendation — Option A, kept as a separate record —
by replying verbatim: **"agreed"**. The original alternatives remain in #302; ADR-0035
and the later daily delivery authority in #520, #525, and #541 establish the cadence
this record serialises.
