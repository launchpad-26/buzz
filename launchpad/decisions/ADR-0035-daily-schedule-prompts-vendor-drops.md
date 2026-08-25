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

A manual dispatch may retry a failed run or expedite a time-sensitive upstream change, but
it invokes the same policy and does not create a separate adoption path. Human review still
controls whether a resulting pull request merges to `launchpad`; the schedule neither
approves nor merges it.

The project-level choice of daily cadence is the deliberate act. Individual executions do
not require another person to remember to start them. This is consistent with ADR-0021's
chosen-point model because every attempt records a specific upstream commit and the
protected pull-request path decides whether it lands.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff delegated low-complexity, non-design ADR outcomes to
the agent even where the original risk rubric classifies them above Low; he did not
personally select this individual outcome.

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
drop grew from 67 to 80 upstream commits during one working session, so a report computed
before the merge attempt can be stale when used. Computing it from the same pinned input as
the attempt preserves the evidence-to-action relationship.

## Risk classification

**Clear Medium (4/12), high confidence.** Blast radius 1; reversibility 0;
security/trust 0; data/state 1; contracts/dependencies 1; operations/uncertainty 1.

No hard High-risk trigger applies. The decision changes when one existing repository
workflow acts and advances shared Git state non-destructively; it does not change the
workflow's identity, token permissions, branch protection, production credentials, public
interfaces, or a cross-repository contract. The cadence is trivially changed, while the
human merge gate contains each attempt. Complexity is Low because later Project 20 work has
already selected daily scheduling; that complexity assessment routes decision authority and
does not lower this risk score.

## Consequences

- Vendor-drop attempts start without relying on a person to remember them.
- A no-change day remains visible without creating an empty pull request.
- The report and merge attempt describe the same pinned upstream commit.
- Tag arrival and accumulated-change thresholds may enrich a report, but cannot silently
  suppress the daily attempt.
- The workflow consumes CI capacity every day, including no-op days.
- A bad upstream change can reach a candidate pull request sooner; ADR-0022's curation,
  required validation, and human merge review remain the controls before adoption.
- Task #541 already owns the scheduled daily merge job, so this decision creates no new
  implementation task.

## Security implications

Scheduling increases how often the existing write-capable workflow executes, but grants no
new permission or identity. The workflow must retain the already-approved least-privilege
token and may only prepare a reviewable pull request; it cannot approve or merge that pull
request. Pinning the observed upstream commit prevents the reviewed report from referring to
a different input than the merge attempt.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization for
low-complexity ADRs. The original alternatives remain in #295; the later daily-cadence
authority is recorded in #520, #525, and #541.
