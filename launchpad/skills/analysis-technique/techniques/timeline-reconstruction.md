---
name: timeline-reconstruction
summary: Merge every timestamped source into one ordered sequence, normalised to a single timezone
reach-for-when:
  - We are not sure what happened in what order
  - Different teams report different start times
  - The change record, the alert, and the ticket all give a different onset time
reduces-with: timeline
evidence-required:
  - At least two independent timestamped sources covering the incident window
  - Each source's timezone or UTC offset
cost: medium
---

# Timeline Reconstruction

## Reach for it when
Nobody on the bridge agrees on when the problem started, or each team is quoting a time from their
own tool that does not match anyone else's. The application team says 09:14, the network team says
09:31, and the change log says 08:58 — before anyone can reason about cause and effect, those need to
land on one shared, ordered sequence.

## Evidence it needs
Pull every timestamped source that touches the incident window: application logs, infrastructure
metrics, change records, alert history, ticket notes, and any manual notes from the bridge call. Not
optional: the timezone or UTC offset each source actually uses — a log in server-local time merged
against one in UTC without conversion produces a timeline that is wrong, not merely imprecise.

## How to run it
1. Gather every source with a timestamp that overlaps the incident window, including sources owned by
   different teams.
2. Confirm the timezone or offset each source is emitting in; do not assume UTC.
3. Run the `timeline` script over the sources to merge them into one ordered, normalised table.
4. Read the merged table start to finish and flag any gap larger than expected for the systems
   involved.
5. Mark the earliest entry that is plausibly the trigger, and note which source it came from.
6. Hand the merged table to the technique or hypothesis it feeds — a timeline is an input, not a
   conclusion.

## Worked example
A storage cluster's replication lag alert fired at 09:31 UTC. The storage team assumed that was the
onset. Merging the storage metrics, the SAN controller's change log, and the backup job scheduler's
history into one timeline showed a firmware push to the SAN controller completed at 08:52 UTC, a
single node's replication queue started climbing at 08:54, and the lag crossed the alert threshold
only at 09:31 — the alert was 39 minutes downstream of the real trigger, and the "root cause" the
storage team was about to chase (a concurrent backup job at 09:28) turned out to be coincidental,
not causal.

## Done when
The merged timeline has every source's events plotted on one normalised clock, spans from before the
earliest reported symptom to the point of restoration or the current moment, and every timestamp has
a stated timezone or offset — no entry left ambiguous.

## Don't use it for
Treating the merged timeline as the analysis itself. A timeline tells you *when*, not *why* — it is
the input that a hypothesis, a change-analysis pass, or a refutation attempt reasons over next.
Presenting the ordered sequence alone as the root cause skips the step where evidence is judged
against a claim.
