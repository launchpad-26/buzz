---
name: trend-analysis
summary: Plot a metric over a long enough window to expose growth, saturation and the point a limit was crossed
reach-for-when:
  - It has been getting slower for weeks
  - It degrades until we restart it
  - We keep having to bump the limit
  - Nobody noticed until it hit the wall
evidence-required:
  - A single metric sampled at a consistent interval over a window long enough to show the slope, not just the current value
cost: medium
reduces-with: correlate
---

# Trend and Capacity Analysis

## Reach for it when
Someone on the bridge describes a decline rather than an event: response times have been "creeping
up for weeks," a job "degrades until we restart it," or a resource keeps needing headroom bumped.
There is no single onset time to anchor on — the fault built up gradually and only became visible
once a threshold was crossed. Reach for this before change-analysis when the complaint has no clean
before/after boundary; reach for it before fault-tree or fishbone when the story is decline rather
than a discrete failure.

## Evidence it needs
One metric, sampled at a consistent interval, over a window long enough to show a slope rather than
a point. Not optional: the window must extend well before the symptom became noticeable — a trend
that has been building for three weeks will not show its shape in three hours of data. If the metric
resets on a recurring event (a nightly restart, a deploy, a failover), the window must span several
of those resets so the sawtooth pattern is visible rather than mistaken for noise.

## How to run it
1. Pick the metric that best represents the resource or behaviour under complaint: latency, queue
   depth, memory in use, disk free, connection count, error rate.
2. Pull that metric at a consistent sampling interval across a window that spans well before the
   symptom was first noticed through to now.
3. Plot it, or tabulate it at a coarse enough bucket size to see the shape rather than the noise.
4. Identify the slope: is the metric flat with occasional spikes, rising steadily, or rising in a
   repeating sawtooth that resets on some recurring event?
5. If a limit exists — a disk size, a connection pool cap, a queue depth alarm, a timeout — mark
   where the trend line crosses it. That crossing point, not the moment someone complained, is the
   real onset.
6. If the trend resets periodically, use `correlate` to align the metric against the reset events
   (restarts, deploys, cron jobs) and confirm the reset is what is masking the underlying growth.
7. Extrapolate the current slope forward to estimate when the limit will be crossed again, if the
   underlying cause is not addressed.

## Worked example
A database's connection pool sat comfortably under its cap for months. Over the past six weeks, a
new batch integration opened connections it never closed on error. Daily peak in-use connections
climbed from 40% of the pool to 95%, invisible day-to-day because a nightly service restart reset
the count to zero each morning — the sawtooth hid the trend from anyone glancing at current-hour
graphs. Pulling six weeks of daily-peak samples and plotting them showed a steady upward slope
underneath the nightly reset. The pool first hit its cap on a day the restart was delayed past
09:00, causing a two-hour outage that looked, at the time, like a sudden failure with no clear
trigger.

## Done when
The plotted trend line has a stated slope over the full window, the point (if any) where it crosses
a known limit is marked on the chart, and — if the metric resets periodically — the reset events
have been checked against the trend to confirm they mask rather than fix the underlying growth.

## Don't use it for
Sharp-onset failures. A step change — a metric that was flat and then jumped to a new level at a
single, identifiable moment — is a change, not a trend, and plotting a long window around it will
show a cliff, not a slope. Route a step change to change-analysis, which asks what happened at that
moment rather than what built up beforehand.
