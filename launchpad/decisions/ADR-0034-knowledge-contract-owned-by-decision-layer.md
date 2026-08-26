---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#589
decided_in: launchpad-26/buzz#589
supersedes: none
---

# ADR-0034 — The knowledge contract is owned by the decision layer

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human, and #589's *Decision
outcome* reads *"Left blank — a human's call, per `launchpad/AGENTS.md` §5 rule 6."*
When a human picks between #589's options A–D, this record's `status` becomes
`Accepted`.

The proposed option is D. The normative `knowledge.*` interface contract is a shared,
implementation-neutral specification owned by `launchpad/decisions/`, and both the
Python project-intelligence pipeline and the shipped Rust crate maintain executable
conformance tests against it. Neither implementation owns the contract or serves as
the other's unchecked source of truth.

**Destination.** The contract moves from `launchpad/project-intelligence/CONTRACT.md`
to its own accepted decision record, `launchpad/decisions/ADR-XXXX-knowledge-interface-contract.md`,
whose number is allocated when that record is written. This record decides *where the
contract lives and who owns it*; it does not itself contain the contract.

Changes to the normative interface are made through a superseding decision record;
accepted ADR files are not edited in place as a living specification. Mechanical test
fixtures may derive from the accepted contract, but they must identify the ADR version
they assert.

## Context

`launchpad/project-intelligence/CONTRACT.md` currently sits beside the Python
implementation. Leaving the contract there makes one implementer the apparent owner
and leaves Rust conformance unchecked. Moving it into the crate reverses the asymmetry.
The decision layer is the existing home for binding cross-component rationale and
provides a neutral authority.

**The two implementations will not ship the same public surface, and the case for a
neutral contract does not depend on their doing so.** ADR-0031 (#1418) decides that
*"`knowledge.find(query)` and `knowledge.ask(text)` — the two of #211's seven methods
with an unbounded free-text input domain — are permanently out of scope for the shipped
knowledge crate"*, and that the Python implementation of both *"stays in the tree,
documented and tested on the Python side, but unreachable from the shipped crate."*

So the surfaces diverge by construction: Python implements seven methods, the crate
implements five. That makes a neutral contract *more* useful rather than less — it is
now the only artifact that can state which methods are common, which are
Python-only, and what conformance means for each side. A contract owned by either
implementation would encode that asymmetry as the owner's private business. #589
recommended deciding this after #578, which is closed; ADR-0031 is the resulting
surface, and the reasoning above is stated against it rather than against the
seven-method assumption an earlier draft used.

## Consequences

- Python and Rust are peers against one neutral normative contract, each conforming to
  the subset of it that applies to them.
- Drift becomes observable on both sides rather than only in the pipeline.
- Interface changes incur a new ADR version, which preserves history but is heavier
  than editing a living document.
- Two conformance suites must be maintained and kept aligned with the named decision
  version.
- **The move breaks `test_contract.py` until it is repointed.** #589 states it:
  *"Any option except A means moving a file that a passing test suite imports by
  relative path, so the move is not free and will briefly break `test_contract.py`."*
  Whoever performs the move updates that import in the same change.
- **Task #553 and Task #552 do not yet cover this record's obligations.** #553 owns
  defining the contract and #552 owns packaging the corpus into the crate; neither
  covers *relocating* the contract into `launchpad/decisions/`, repointing
  `test_contract.py`, or standing up a **Rust** conformance suite. Those must be added
  to #553's acceptance criteria or filed separately. This record does **not** claim no
  additional task is required.

## Security implications

No exposure or trust boundary changes. The contract continues to govern provenance
behavior, but this record changes only where that internal specification is authoritative
and how implementations demonstrate conformance.

## Supersedes

none

## Provenance

Drafted by an agent from #589's options; the decision itself is pending a human, as
stated at the top of *Decision*. Full alternatives remain in #589.
