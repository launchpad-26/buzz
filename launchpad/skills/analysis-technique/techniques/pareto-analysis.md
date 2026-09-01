---
name: pareto-analysis
summary: Rank causes or error signatures by frequency or impact and act on the vital few
reach-for-when:
  - There are hundreds of errors and we do not know which matter
  - Which of these should we fix first
  - One noisy log is drowning out everything else
evidence-required:
  - A set of events, errors, or tickets large enough that eyeballing them will not work
  - A way to group events into distinct signatures or categories
reduces-with: frequency
cost: low
---

# Pareto Analysis

## Reach for it when
A log, alert queue, or ticket backlog has far more entries than anyone can read one by one, and the
question on the bridge is which of them is actually worth chasing. This is the shape when someone
says "we're getting hundreds of errors a minute" or "there's a huge backlog and we need to triage
it" — the goal is to find the small number of signatures responsible for most of the volume, not to
explain any single occurrence yet.

## Evidence it needs
A collection of events — log lines, error codes, alert firings, or ticket subjects — covering the
window in question, plus a way to reduce each event to a signature that strips out what varies
(timestamps, request IDs, user identifiers, IP addresses) so that identical failures group together
instead of each looking unique. Not optional: enough volume that ranking is actually informative —
Pareto on twelve events is eyeballing with extra steps.

## How to run it
1. Collect the events for the window under investigation — a log slice, an alert export, or a ticket
   list.
2. Run the `frequency` script over the collection to normalise out identifiers and rank the distinct
   signatures by count.
3. Read the ranked output and mark the smallest set of signatures whose combined count accounts for
   most of the volume — commonly, but not necessarily exactly, 80%.
4. For each signature in that vital-few set, confirm it is a real distinct failure mode and not the
   same underlying fault logged in two slightly different formats.
5. Hand the vital-few signatures to the next step — a hypothesis, a change-analysis pass, or a
   deeper technique — as the ranked list of what to investigate first.

## Worked example
An identity provider's authentication log for a one-hour window held 42,000 failed-login lines.
Running `frequency` over it collapsed those into 14 distinct signatures. The top three —
"token validation failed: signature mismatch" (61%), "session expired mid-request" (19%), and
"MFA challenge timeout" (9%) — accounted for 89% of all failures. The remaining eleven signatures,
including a handful of "unknown realm" errors that had triggered a separate on-call page, were each
under 1% of volume. The team focused first on the signature-mismatch cluster, which traced to a
clock-skew issue on one identity provider node, and left the low-volume signatures for later triage.

## Done when
The vital-few signatures — the smallest set that accounts for most of the volume — are named and
handed to a hypothesis or a deeper technique for investigation. Not done until every signature in
that set has been checked against evidence, not just counted.

## Don't use it for
Rare-but-catastrophic failures. Pareto ranks by count, so a failure mode that fires once a quarter
but takes down the whole service will sit at the bottom of the list next to noise, not at the top
where its impact belongs. If the concern is a low-frequency, high-severity event rather than "what's
generating the most volume," reach for fault tree analysis or a dependency and blast-radius review
instead — those weigh consequence, not count.
