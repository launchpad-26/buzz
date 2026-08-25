---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#306
decided_in: launchpad-26/buzz#306
supersedes: none
---

# ADR-0042 — The change agent produces a deterministic contested-surface report

## Decision

Choose Option A. The change agent's artifact for a vendor drop is a deterministic,
contested-surface report: it lists only files where upstream's changes intersect the
fork's divergence (the 8 of 796 in the current drop), each with its divergence-register
row, conflict status, and the upstream commits touching it. The uncontested remainder is
summarised in one line under the standing blanket-adoption policy with a link to the full
diff. No model-written commentary is included until the containment question (#303) is
settled.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

ADR-0022 settled that per-drop adjudication covers only the contested surface. What a
reviewer is actually handed was still open. A per-commit artifact asks a human to consider
67 items, a per-file artifact 796, and the contested-surface artifact 8 — the only
affordable shape at upstream's tempo. The artifact is regenerable, and the unit of the
register's recorded declines is the file, so the report and the register agree.

Rejected: per-commit adjudication of all 67 (B, excluded by ADR-0022), model commentary
(C, puts untrusted upstream text through a model before #303 is settled), the raw diff
(D, a 796-file haystack), area-level grouping (E, hides file-level surprises).

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 2; reversibility 1;
security/trust 1; data/state 0; contracts/dependencies 1; operations 1. The artifact
renders untrusted upstream text for a human to read — a smaller version of the #303
surface — which is why model commentary is withheld until #303 settles. No hard High-risk
trigger.

## Consequences

- The change agent's principal output is defined; the largest work item under #273 is
  writable.
- The cohort formally states it adopts ~99% of upstream unread by policy — a clarification
  of existing practice, not a weakening.
- An incomplete register produces a confidently incomplete report; the strongest argument
  yet for the register being machine-checked (#301).

## Security implications

The artifact is the point where upstream-authored text is rendered next to instructions.
A deterministic spine renders it for humans only; commenta.y would put it through a model,
which is why C waits on #303.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #306.