---
name: fault-tree-analysis
summary: Top-down boolean decomposition from the observed failure through AND/OR gates to basic events
reach-for-when:
  - multiple unrelated systems failed together
  - the failure needed several things to go wrong at once
  - a single fix did not stop the incident because more than one condition had to hold
evidence-required:
  - the top-level failure stated as a single, precise event
  - a list of candidate contributing conditions, each independently verifiable as true or false
  - the dependency or precondition relationships between those conditions
reduces-with: none
cost: high
---

# Fault Tree Analysis

## Reach for it when
The incident does not reduce to one broken component. Several systems that do not normally depend on
each other failed in the same window, or a fix that addressed one clear cause did not restore
service because the outage also required a second, unrelated condition to be true. On the bridge
call this sounds like "we fixed that and it's still broken" or "none of these three things alone
should have taken the service down." It is the right tool when the working hypothesis has already
grown past a single cause and needs a structure to hold multiple conditions and their combination
logic without losing track of which ones are proven.

## Evidence it needs
A precise statement of the top event — the exact failure being explained, not a symptom category.
A candidate list of contributing conditions, each one something that can be checked and marked true
or false against evidence, not a vague suspicion. And the logical relationship between those
conditions: whether the top event needed all of them together (an AND gate) or any one of them alone
(an OR gate). Without evidence for each leaf condition, the tree is a diagram of guesses, not an
analysis.

## How to run it
1. State the top event in one precise sentence — the exact failure, scoped to what was actually
   observed.
2. List every condition that could have contributed, drawn from the evidence gathered so far
   (change records, alerts, dependency maps, prior incidents).
3. For each condition, decide whether it is a basic event (verifiable directly against evidence) or
   an intermediate event (itself caused by a combination of other conditions, and needs its own
   sub-tree).
4. Connect each event to the level above it with an AND gate (all inputs required) or an OR gate (any
   one input sufficient), based on what the evidence supports — not on which is more convenient to
   draw.
5. For every basic event, check it against evidence and mark it true, false, or unresolved. Do not
   mark a leaf true on inference alone.
6. Trace every path through the tree from the top event down to leaves that are all marked true. Any
   path containing a false or unresolved leaf did not happen and is ruled out.
7. Where more than one path survives, the incident has more than one sufficient cause; report all of
   them rather than picking the first.

## Worked example
Top event: primary and secondary SAN controllers both stopped serving reads within the same 90-second
window. Candidate conditions: (a) a firmware bug in the multipath driver, (b) the automatic failover
job, (c) a stale monitoring threshold. Built as an AND gate: outage required (a) AND (b) failed to
trigger. Sub-tree under (b): failover job requires a healthy heartbeat link (true, confirmed in logs)
AND a quorum disk that responds within 2s (false — quorum disk was on the same controller pair and
had stopped responding, confirmed by timestamped health-check failures). Condition (a) confirmed true
via the vendor's firmware changelog. Condition (c) checked and marked false — the stale threshold
delayed the page by four minutes but did not contribute to the outage itself, so it is pruned from
the tree as a red herring. Surviving path: (a) AND (b)-via-quorum-disk. Single sufficient cause,
requiring both a driver defect and a failover precondition to break together.

## Done when
Every leaf in the tree is marked true, false, or unresolved against a specific piece of evidence, and
at least one path from the top event to all-true leaves has been traced and named. A tree containing
unresolved leaves without a way to resolve them is not done — go back to evidence gathering for those
specific leaves before naming a root cause.

## Don't use it for
A fault with a single, already-obvious cause — building a tree to confirm what the evidence already
shows is drawing effort, not analysis; use the direct evidence chain instead. Also don't reach for it
under live time pressure: the tree takes time to build honestly, and a half-built one invites picking
the first plausible-looking path before the leaves are actually verified. Run it in retrospective
tempo, after service is restored.
