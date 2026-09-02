---
name: change-analysis
summary: Establish onset time, then enumerate everything that changed in the window before it — including implicit changes nobody logged
reach-for-when:
  - it started suddenly and nothing changed
  - it broke overnight
  - it was fine yesterday and today it isn't
evidence-required:
  - a confirmed onset time, not a guess
  - a change window drawn around that onset time
  - access to every change source that touches the affected system, not just the official change log
reduces-with: first-occurrence
cost: low
---

# Change Analysis

## Reach for it when
The failure has a sharp onset — a system that worked stopped working, or started failing a
specific way, at a moment that can be pointed to. On the bridge call this sounds like "it started
suddenly and nothing changed" or "it broke overnight" or "it was fine yesterday." That last phrase
is the trap this technique exists to catch: something always changed, and the caller's confidence
that "nothing changed" usually means no *human-initiated* change was logged, not that the system's
state was static. Change analysis widens the search past the official change log to the changes
nobody thought to record.

## Evidence it needs
A confirmed onset time — pinned by evidence, not memory; run timeline-reconstruction first if the
onset itself is disputed. A window drawn around that onset, wide enough to catch a slow-propagating
change (a config pushed hours earlier, applied at the next restart) without being so wide it pulls
in noise. And access to every change source that could have touched the affected system: the formal
change log, deployment history, infrastructure-as-code commits, scheduled job calendars,
certificate and credential expiry dates, quota and capacity thresholds, and the calendar itself —
daylight saving transitions, month-end and quarter-end jobs, license renewal dates. A change search
that only queries the ticketing system is not this technique; it is a subset of it.

## How to run it
1. Confirm the onset time against evidence — a log entry, an alert, a metric inflection — not a
   participant's recollection.
2. Run the `first-occurrence` script over the available change sources to draw the window and
   surface every recorded change inside it.
3. Extend the search past what the script surfaced: check certificate and credential expiry dates,
   scheduled jobs and batch calendars, quota or capacity counters crossing a threshold, and calendar
   effects (DST, month-end, license renewal) that fall inside the window without appearing in any
   change log.
4. Build a two-column grid: one row per candidate change, one column "IS" (what changed, where, and
   when) and one column "IS NOT" (a comparable system, path, or population the same change did
   *not* touch, and that did not fail).
5. Fill every IS NOT cell before ranking anything — a change with no IS NOT comparison is unranked,
   not confirmed.
6. For each candidate, check whether it explains every observed symptom, not just the first one
   reported — a partial fit is a coincidence until proven otherwise.
7. Rank surviving candidates by how tightly the change's timing tracks the onset and how completely
   it explains the symptom set, and hand the top candidate to a confirming test (revert, replay, or
   direct evidence check) before calling it the cause.

## Worked example
Onset: single-sign-on logins for one regional office started failing at 06:02 UTC, no error on the
identity provider's status page. Change window: the 12 hours before onset. Recorded changes: none in
the formal change log. Extended search found an intermediate TLS certificate on that region's
authentication proxy had expired at 06:00 UTC — a renewal job existed but targeted the wrong
hostname after a DNS migration three weeks earlier, so it had been silently failing since. IS:
logins through the regional proxy, at 06:02, for every user in that region. IS NOT: logins through
the other two regional proxies, whose certificates were unaffected and kept working the whole time.
The certificate explained every symptom — the regional scope, the exact timestamp, and the absence
of any application-layer error — and reissuing it resolved the incident.

## Done when
The IS/IS NOT grid has an entry in every cell for every candidate change, and the surviving
candidate's timing and symptom coverage have been checked against a comparison system that the same
change did not touch. A candidate found near the onset time but never checked against an IS NOT
comparison is not done — it is a suspect, not a cause.

## Don't use it for
Slow degradations with no sharp onset — a system that has been quietly worsening over days or weeks
has no single moment to draw a window around, and forcing one manufactures a false onset time; route
those to trend-analysis instead. And even with a sharp onset, watch the trap this technique invites:
a change found near the onset is a candidate, not a cause, until it has been checked against an IS
NOT comparison and shown to explain every observed symptom — a change that merely coincides with
the timing, or explains only part of the failure, is not yet confirmed.
