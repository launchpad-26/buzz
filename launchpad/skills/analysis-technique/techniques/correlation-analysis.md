---
name: correlation-analysis
summary: Align two or more event or metric series by time bucket to test whether they co-move
reach-for-when:
  - These two things seem to spike together
  - Is the database causing this or reacting to it
  - Intermittent, no obvious pattern
evidence-required:
  - Two or more timestamped series covering the same window, at a comparable granularity
cost: medium
reduces-with: correlate
---

# Correlation Analysis

## Reach for it when
Someone on the bridge notices that two things move together — CPU climbs whenever queue depth
climbs, or error rate on one service tracks latency on another — but nobody can yet say which one
is driving which, or whether they are both downstream of a third cause. Reach for this before
naming either series a cause; it tells you whether the co-movement is real and how tightly the two
track, not which one is upstream.

## Evidence it needs
Two or more timestamped series that cover the same incident window: metrics, event counts, or log
signatures reduced to a rate. Not optional: the series must share a comparable time granularity — a
metric sampled every 10 seconds against one sampled every 5 minutes will not align without first
resampling one of them to match the other.

## How to run it
1. Pick the two (or more) series that appear to move together.
2. Confirm they cover the same time window and normalise them to the same bucket size and timezone.
3. Run the `correlate` script over the series to align them by time bucket and report co-movement.
4. Read the output for the bucket-by-bucket relationship, not just a single summary number — a
   strong overall correlation can hide a relationship that only holds for part of the window.
5. Check the lag: does one series's movement consistently lead the other by a fixed offset, move in
   lockstep, or lag behind it?
6. Treat the result as a lead for the next technique, not a conclusion — hand a leading series to a
   change-analysis or timeline pass to test whether it explains the onset.

## Worked example
An identity provider's authentication latency and a downstream API gateway's 5xx rate both spiked
during a 20-minute window. Running `correlate` over the two series showed the gateway's 5xx rate
rising in the same bucket the authentication latency crossed 800ms, with no consistent lead or lag
between them — they moved together, bucket for bucket. That ruled out the gateway as the trigger
(a trigger should lead, not move in lockstep) and pointed the investigation at a shared upstream
dependency: both systems were calling the same certificate validation service, which a check of its
own metrics confirmed had started timing out at the same moment.

## Done when
The `correlate` output shows, for every time bucket in the window, whether the series moved together,
apart, or with a stated lag — and the investigation has recorded which series (if either) leads,
rather than stopping at "they're related."

## Don't use it for
Naming a cause. A correlated metric is exactly as likely to be a downstream symptom as an upstream
trigger, and correlation alone cannot tell you which — the database spiking alongside the API could
mean the database is causing the API's trouble, or the API's retries are hammering the database. Once
correlation confirms two series move together, causation has to be established separately, by
tracing the mechanism (a dependency check, a change record, or a timeline) that would make one
actually drive the other.
