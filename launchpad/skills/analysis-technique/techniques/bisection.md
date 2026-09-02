---
name: bisection
summary: Halve the search space with each test, whether across a request path, a time range, a config set or a batch of records
reach-for-when:
  - somewhere between the client and the database it fails
  - we can reproduce it but not locate it
evidence-required:
  - a reliable, repeatable test that returns pass or fail
  - an ordered search space to cut in half — a chain of hops, a time range, a commit range, or a batch of records
reduces-with: window
cost: low
---

# Bisection

## Reach for it when
The fault is reproducible but its location within a chain is not known. On a bridge call this
sounds like "somewhere between the client and the database it fails" — a long path with many
plausible fault points — or "we can reproduce it but not locate it": there is a working test, just
not yet a suspect. Reach for this whenever the space to search is ordered (a request path, a time
range, a batch of records, a range of commits or config versions) and a single test at the midpoint
tells you which half to keep.

## Evidence it needs
A test that reliably returns pass or fail on demand, at any point you choose to run it. Without
this, bisection has nothing to converge on — see **Don't use it for**. You also need the search
space itself laid out as an ordered sequence: the hops between client and database, the commits
between last-known-good and first-known-bad, the time range between last-good and first-bad
observation, or the batch of records between a known-clean and known-corrupt boundary.

Where the space is a time range and each candidate test point requires pulling a fresh slice of
logs or records, run `window` to cut that slice rather than hand-trimming it.

## How to run it
1. Confirm the test is reliable: run it twice at a known-bad point and twice at a known-good point
   without changing anything else. If either point flips answer between runs, stop — see
   **Don't use it for**.
2. Lay out the search space in order, end to end, with a confirmed-bad point at one end and a
   confirmed-good point at the other.
3. Pick the midpoint of the remaining space and run the test there.
4. If the midpoint fails, the fault is between the good end and the midpoint; discard the other
   half. If it passes, the fault is between the midpoint and the bad end; discard that half.
5. Repeat steps 3–4 on the remaining half only, narrowing the confirmed-good and confirmed-bad
   boundaries each time.
6. Stop when the confirmed-good and confirmed-bad points are adjacent — one hop apart, one commit
   apart, one config change apart, or a batch of one — and name the fault point.
7. Confirm the finding: reproduce failure at the identified point and success immediately upstream
   or downstream of it, at least once more each.

## Worked example
A nightly batch job that writes 40,000 records from a staging table to a downstream reporting
table has started silently dropping rows — output count is short of input count by a few hundred,
different rows each night. The job processes records in fixed-size ranges by primary key, so the
range is a natural ordered space. Splitting the key range in half and re-running the job against
each half in isolation (with a row-count check as the test) shows the shortfall appears only in the
upper half. Repeating on that half, then the resulting quarter, narrows the loss to a single
20,000-row window covering one source partition. Within that window a second bisection on
timestamp — rather than key — isolates the drop to records written during a five-minute overlap
with the partition's own maintenance job, which was holding a lock the batch job silently skipped
past. Four halvings located the exact partition; a fifth located the exact time window.

## Done when
The confirmed-good and confirmed-bad boundaries are one unit apart — one hop, one commit, one
config change, one record — and re-running the test at that exact boundary reproduces the pass/fail
split at least once more on each side.

## Don't use it for
Non-reproducible or intermittent faults. Bisection needs a reliable test at every step; if the
symptom does not fire consistently at a genuinely bad point, or fires occasionally at a genuinely
good one, the test at each midpoint cannot be trusted, and bisection will converge confidently on
the wrong half. If step 1's reliability check ever flips, stop bisecting and first establish the
triggering pattern with `correlation-analysis` or `pareto-analysis`, or pin down onset with
`timeline-reconstruction` — then come back once a dependable test exists.
