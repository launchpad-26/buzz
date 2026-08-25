---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#306
decided_in: launchpad-26/buzz#306
supersedes: none
---

# ADR-0042 — The change agent produces a deterministic contested-surface report

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human and the half of #306 this record
addresses has no *Decision outcome* recorded. When a human states the outcome in #306, this
record's `status` becomes `Accepted`.

**Two records share `#306`, and that is intentional.** #306's only recorded decision names
[ADR-0022](ADR-0022-curation-scoped-to-the-contested-surface.md), which settled the *scope*
question — which files are adjudicated and which are adopted wholesale — and states in its
own Context that *"the drop report's shape and format, how contested items are presented,
whether a model writes any part of it, and how the uncontested remainder is summarised"*
were left open. **This record settles that remaining half — the report's shape — and nothing
ADR-0022 already decided.** Two ADRs therefore carry `issue: #306` and `decided_in: #306`
legitimately: ADR-0022 for scope, this one for the report. Neither supersedes the other.

The proposed option: Option A. The change agent's artifact for a vendor drop is a
deterministic, contested-surface report: it lists only files where upstream's changes
intersect the fork's divergence, each with its divergence-ledger row, conflict status, and
the upstream commits touching it. The uncontested remainder is summarised in one line under
the standing blanket-adoption policy with a link to the full diff. No model-written
commentary is included until the containment question (#303) is settled.

**"Deterministic" is a testable property, not a tone.** The same drop inputs — the same
fork commit, the same upstream commit, the same ledger — must produce a **byte-identical**
report: files ordered by a stable key, rows rendered in a fixed field order, no timestamps
or run identifiers in the body, and no text whose wording can vary between runs. Two runs
over the same inputs are expected to compare equal under `diff`; that is the check.
[ADR-0019](ADR-0019-review-checks-gate-only-when-deterministic.md) makes determinism the
condition for anything allowed to gate a merge, and holding this artifact to the same
standard is what would let it ever be checked mechanically rather than trusted.

## Context

ADR-0022 settled that per-drop adjudication covers only the contested surface. What a
reviewer is actually handed was still open. In the drop measured while ADR-0022 was decided
— 2026-08-21, against merge-base `f8692fa9b` (2026-08-17) — a per-commit artifact asks a
human to consider 67 items, a per-file artifact 796, and the contested-surface artifact 8.
Those three figures describe one drop at one point in time and are not a standing property
of the fork; the next drop will have its own. The ratio is the durable part, and it is why
the contested surface is the only affordable shape at upstream's tempo. The artifact is
regenerable, and the unit of the divergence ledger's recorded declines is the file, so the
report and the ledger agree.

**One name for one artefact: "ledger".** This record uses ADR-0022's term throughout, and
the issue that defines its rows is #294 — *"the fork's standing position on each contested
upstream file, and how each is enforced on a drop"*. The naming is not yet uniform
upstream of this record: #301, which asks whether that artefact is machine-checked, still
titles it a "divergence register". They are one artefact, not two.

Rejected: per-commit adjudication of all 67 (B, excluded by ADR-0022), model commentary
(C, puts untrusted upstream text through a model before #303 is settled), the raw diff
(D, a 796-file haystack), area-level grouping (E, hides file-level surprises).

## Consequences

- The change agent's principal output is defined; the largest work item under #273 is
  writable.
- The cohort formally states it adopts ~99% of upstream unread by policy — a clarification
  of existing practice, not a weakening.
- An incomplete ledger produces a confidently incomplete report; the strongest argument
  yet for the ledger being machine-checked (#301).
- Byte-identical regeneration means a report can be re-derived and compared rather than
  trusted, which is what lets it be checked mechanically at all.

## Security implications

The artifact is the point where upstream-authored text is rendered next to instructions.
A deterministic spine renders it for humans only; commentary would put it through a model,
which is why C waits on #303.

## Supersedes

none

## Provenance

Drafted by an agent from #306's options; the decision itself is pending a human, as stated
at the top of *Decision*. Full alternatives remain in #306. The 67 / 796 / 8 figures are
ADR-0022's, measured on 2026-08-21 against merge-base `f8692fa9b`, and are reproduced here
rather than re-measured. The term "ledger" is taken from ADR-0022; #294's and #301's titles
were read directly to confirm which issue defines the artefact and which asks whether it is
machine-checked. An earlier draft of this record called it a "register" and cited only
#301, which is the machine-checking question rather than the artefact.
