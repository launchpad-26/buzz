---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#295
decided_in: launchpad-26/buzz#295
supersedes: none
---

# ADR-0035 — The daily schedule prompts each vendor-drop attempt

## Decision

The scheduled daily run is the primary prompt for a vendor drop. A fresh human
instruction, an upstream tag, or a size threshold is not required before the workflow
attempts the next drop.

Each run pins the exact upstream commit it observed. If upstream has not moved since the
last adopted point, the run is a recorded no-op. If upstream has moved, the same run
computes the drop report from that pinned input and attempts the merge path governed by
ADR-0021 and ADR-0022. The report is not produced by a separate earlier schedule, because
that would let upstream move between the report and the drop it purports to describe.

**Unless a drop is already in flight.** ADR-0036 (#302) serialises drops: an invocation
that finds an existing open drop records a blocked attempt instead of attempting a merge.
This record sets the cadence of *attempts*; ADR-0036 governs what an attempt does when one
is already outstanding. The two are intended to land together and neither is complete
alone.

A manual dispatch may retry a failed run or expedite a time-sensitive upstream change, but
it invokes the same policy and does not create a separate adoption path. Human review still
controls whether a resulting pull request merges to `launchpad`; the schedule neither
approves nor merges it.

The project-level choice of daily cadence is the deliberate act. Individual executions do
not require another person to remember to start them. This is consistent with ADR-0021's
chosen-point model because every attempt records a specific upstream commit and the
protected pull-request path decides whether it lands.

## Context

Issue #295 was rewritten on 2026-08-22 around an earlier premise: vendor drops would be
unscheduled human acts and only a read-only reminder might run periodically. Later,
more-specific delivery authority replaced that premise. Feature #520 requires the sync
decision set to be resolved under the daily-cadence ruling, Feature #525 requires a
scheduled daily merge and three consecutive daily drops, and Task #541 owns the scheduled
merge job.

Keeping the old report-only recommendation would make the accepted decision contradict the
work already authorised to implement it. It would also recreate the observed failure mode:
an important maintenance activity with no self-starting trigger depends on someone noticing
that it has not happened.

Research #365 adds a narrower reason not to schedule the report separately. The measured
drop grew from 67 to 80 upstream commits during one working session — #365 records
*"Thirteen commits, 19% growth, within one working session"* — so a report computed before
the merge attempt can be stale when used. Computing it from the same pinned input as the
attempt preserves the evidence-to-action relationship.

## Consequences

- Vendor-drop attempts start without relying on a person to remember them.
- A no-change day remains visible without creating an empty pull request.
- The report and merge attempt describe the same pinned upstream commit.
- Tag arrival and accumulated-change thresholds may enrich a report, but cannot silently
  suppress the daily attempt.
- The workflow consumes CI capacity every day, including no-op days.
- A bad upstream change can reach a candidate pull request sooner; ADR-0022's curation,
  required validation, and human merge review remain the controls before adoption.
- **Task #541 owns the scheduled daily merge job but does not yet cover this record's
  mechanism.** Its only acceptance criterion is *"a scheduled job exists that runs the
  daily upstream merge"*. Three requirements here are outside it and must be added to #541
  before it is built, or filed separately under Feature #525: pinning the exact upstream
  commit observed by each run; computing the drop report from that same pinned input; and
  recording a visible no-op when upstream has not moved. This record does **not** claim it
  creates no implementation work.

## Security implications

Scheduling increases how often the existing write-capable workflow executes, but grants no
new permission or identity. The workflow must retain the already-approved least-privilege
token and may only prepare a reviewable pull request; it cannot approve or merge that pull
request. Pinning the observed upstream commit prevents the reviewed report from referring to
a different input than the merge attempt.

## Supersedes

none

## Provenance

Drafted by an agent from #295's options and the later delivery authority. Jeffrey
(@tucktuck101) made the decision on 2026-08-31 after reviewing the options, their positive
and negative consequences, and the agent's recommendation of Option E. He accepted that
recommendation by replying verbatim: **"agreed"**. The original alternatives remain in
#295; the later daily-cadence authority is recorded in #520, #525, and #541.
