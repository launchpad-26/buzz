---
name: valid-technique-2
summary: Second valid test technique
reach-for-when:
  - Timeouts are intermittent
  - Latency spikes on schedule
evidence-required:
  - Request timing data
  - System metrics
reduces-with: timeline
cost: medium
---

# Valid Technique 2

## Reach for it when
Requests are timing out inconsistently or performance degrades at specific times.

## Evidence it needs
Complete request timing logs and corresponding system resource usage (CPU, memory, disk I/O).

## How to run it
1. Collect timing data across requests
2. Correlate with system metrics timeline
3. Identify patterns in the timing

## Worked example
Web requests timeout every 5 minutes during peak hours. Timeline revealed garbage collection pauses in the JVM every 5 minutes coinciding exactly with timeout spikes.

## Done when
You have identified when the problem occurs and what system component behavior correlates with it.

## Don't use it for
Analyzing one-off latency spikes without pattern.
