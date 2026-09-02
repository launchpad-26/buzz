---
name: five-whys
summary: Drill a single causal chain by repeatedly asking why the previous answer happened
reach-for-when:
  - it keeps coming back after every fix
  - we fixed it last month and it returned
evidence-required:
  - a single confirmed failure event to drill into, not a pattern of unrelated failures
reduces-with: none
cost: low
---

# 5 Whys

## Reach for it when
The same symptom has recurred after being "fixed" before, and the fix addressed a symptom rather
than a cause. The caller's language is usually "it keeps coming back" or "we already fixed this
once." This technique fits a single, well-understood failure with one apparent chain of causation —
not a failure with several independent contributing factors.

## Evidence it needs
A confirmed statement of the problem (not a guess) and someone who was involved in the incident or
the prior fix, able to answer each "why" with evidence rather than speculation. If an answer cannot
be backed by a log, a config diff, or a person's direct account, stop and gather that evidence before
asking the next why.

## How to run it
1. Write the problem statement in one sentence, backed by evidence, not opinion.
2. Ask "why did that happen?" and record the answer, citing the evidence that supports it.
3. Treat that answer as the new problem statement and ask "why" again.
4. Repeat until the answer names a broken process, a missing control, or a decision that made the
   failure possible — not another symptom.
5. Stop as soon as an answer would recur unless fixed, regardless of whether that took three whys or
   seven; five is a guideline, not a stopping rule.
6. Apply the recurrence test to the final answer: if this cause is addressed, would the problem
   recur? Does the evidence explain the whole observed symptom, not part of it?
7. If an answer branches into two or more independent causes, stop this technique and route to
   fault-tree-analysis or fishbone-ishikawa instead.

## Worked example
Problem: a scheduled batch job on the mainframe misses its nightly SLA for the third time this
quarter. Why did it miss? The job queue was backed up behind a long-running report. Why was the
report long-running? It scanned a full table instead of an index range. Why did it scan the full
table? A statistics job that keeps the query planner's index choice current was disabled last
quarter. Why was it disabled? An operator turned it off during a maintenance window to save CPU and
never re-enabled it. Why was there no check to catch that? Re-enabling scheduled maintenance tasks
was never added to the maintenance-window closeout checklist. Root cause: the closeout checklist is
missing a step, not "the report ran long."

## Done when
The final answer names a process gap, missing control, or decision — not a recurrence of the
original symptom — and passes the recurrence test: fixing it would prevent the specific failure from
returning, and the evidence chain from problem statement to final answer has no unsupported link.

## Don't use it for
Failures with multiple independent contributing causes. Asking "why" five times against a failure
that had three separate things go wrong at once forces a single linear chain onto a branching
problem, manufactures one culprit, and hides the other two causes entirely — they will still be
there the next time the conditions line up differently. When an answer branches, or when several
people give different but equally evidenced answers to the same "why," switch to
fault-tree-analysis or fishbone-ishikawa, which are built to hold more than one cause at a time.
