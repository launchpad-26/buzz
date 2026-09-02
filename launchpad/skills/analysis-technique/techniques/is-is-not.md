---
name: is-is-not
summary: Bound a problem by contrasting what is affected against what demonstrably is not, across What, Where, When and Extent
reach-for-when:
  - it works for some users but not others
  - one site is affected and the others are fine
  - it only fails for certain requests
  - it started failing for one region at a particular time while the others stayed up
  - some of the estate is broken and the rest is untouched
evidence-required:
  - at least one confirmed failing case, described specifically enough to name the object, location and time
  - at least one confirmed working case of the same kind — a user, site, request type or device that is demonstrably fine
  - the ability to ask someone, or check a source, about cases nobody has reported yet
reduces-with: delta
cost: medium
---

# IS / IS NOT (Kepner-Tregoe problem specification)

## Reach for it when
Part of the estate is broken and part of it is fine. On a bridge call this arrives as "it works for
some users but not others", "one site is affected and the others are fine", or "it only fails for
certain requests" — and often with a first hypothesis already attached, built on the affected half
alone. Reach for this whenever a working comparison case exists, especially before anyone starts
testing hypotheses: the grid narrows the search space first, so that fewer hypotheses need testing
at all. It is also the right move when the reported scope is suspect — callers report what they
noticed, not what is true, and the IS NOT column is what tests that.

## Evidence it needs
One confirmed failing case and one confirmed **working** case of the same kind, both specific enough
to name: which user, which site, which request type, which device, and at what time. Without a
working case there is nothing to put in the IS NOT column and the technique has no discriminating
power — see **Don't use it for**.

You also need reachability: someone to ask, or a source to query, about cases nobody has reported.
An IS NOT cell filled in from assumption is worse than an empty one, because it will be trusted.
Mark any cell you could not confirm as `unknown` rather than guessing it.

Where the comparison is between two machine-readable states — two config exports, two policy dumps,
a working device's settings against a broken one's — run `delta` on the pair first and fill the grid
from its output rather than by eye.

## How to run it
1. Write the problem statement as one line: the object and the deviation, nothing else. "Card
   payments fail at three of eleven branches", not "the payment platform is broken".
2. Draw four rows — **What**, **Where**, **When**, **Extent** — and two columns, **IS** and
   **IS NOT**.
3. Fill the IS column from confirmed failing cases only. *What* is the object and the specific
   deviation. *Where* is the location, both geographic and logical (which site, which subnet, which
   tenant, which tier). *When* is first occurrence, the pattern since, and where it sits relative to
   any change or business cycle. *Extent* is how many, how much, and whether it is growing.
4. Fill the IS NOT column with cases that **could reasonably have been affected but are not**. This
   is the half that does the work, and it is the half that gets skipped. For each IS entry, ask what
   the nearest neighbour is that is fine: if branches 4, 7 and 9 fail, branches 1–3, 5, 6, 8, 10 and
   11 are the IS NOT — and so are the other card types those branches process successfully, and the
   hours before onset. Confirm each one; do not infer it from silence.
5. Where a pair of states can be diffed mechanically, run `delta` on working-versus-broken and use
   its output to populate the neighbouring cells, rather than comparing by inspection.
6. For each row, write the **distinction**: what is true of the IS side and not of the IS NOT side.
   Branches 4, 7 and 9 are the three migrated to the new network path; the other eight are not.
7. Note any **change** associated with each distinction — what altered in, on or around the thing
   that distinguishes the IS side.
8. Derive hypotheses from the distinctions only. A cause that would also have broken the IS NOT
   cases is already refuted by the grid; discard it without further testing.
9. Test each surviving hypothesis against the whole grid: it must explain every IS entry **and** the
   absence of every IS NOT entry. A cause that explains the failures but not the survivals is
   incomplete.

## Worked example
Problem statement: staff at two of nine offices cannot sign in to the federated identity provider;
authentication returns a policy failure.
- **What IS**: sign-in to the federated IdP fails with a conditional-access policy denial.
  **IS NOT**: sign-in to the local directory succeeds; VPN authentication against the same directory
  succeeds; password resets work.
- **Where IS**: offices C and G. **IS NOT**: the other seven offices, and remote workers homed to
  offices C and G who sign in over VPN rather than on-site.
- **When IS**: from 06:40 local on the Monday, continuously since. **IS NOT**: not before 06:40; the
  weekend's overnight sign-ins were clean.
- **Extent IS**: all on-site staff at those two offices, roughly 240 accounts. **IS NOT**: not
  growing to other offices over four hours.
- **Distinction**: offices C and G are the two whose public egress addresses were re-mapped during a
  weekend network migration; remote workers at the same offices egress through the VPN concentrator
  instead, and are fine.
- Hypothesis "expired signing certificate" is refuted by the grid — it would have denied all nine
  offices and the VPN users too. Surviving hypothesis: the conditional-access policy's trusted-IP
  list still names the old egress ranges. Confirmed against the policy's named-location entries.

## Done when
Every cell in the four-by-two grid has either a confirmed entry or an explicit `unknown`, with no
cell left blank; each of the four rows has a written distinction or is explicitly marked "no
distinction found"; and every surviving hypothesis has been checked against the whole grid and shown
to explain each IS entry and the absence of each IS NOT entry.

## Don't use it for
A total outage with no working comparison case. When everything of the relevant kind is down, the
IS NOT column is empty and the grid has no discriminating power — it will look like a completed
analysis while telling you nothing. If the first attempt to fill IS NOT comes back empty across all
four rows, stop and route to a technique that works on a single failing case: `fault-tree-analysis`
to decompose which combination of conditions could take down the whole thing, or
`timeline-reconstruction` to establish onset and what changed around it.

Two narrower cases go elsewhere as well. If a single case has recurred after being fixed and there is
no scope contrast to draw, use `five-whys`. If the scope contrast is real but the object is failing
intermittently in a way nobody can pin to a user, site or request type, the IS side cannot be
specified yet — establish the pattern first with correlation or frequency analysis, then come back
and build the grid.
