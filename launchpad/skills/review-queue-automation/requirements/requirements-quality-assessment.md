# RQA requirements quality assessment

Per-requirement assessment of every requirement in
[`requirements-specification.md`](requirements-specification.md) against the nine individual requirement
characteristics named in [launchpad-26/buzz#2069](https://github.com/launchpad-26/buzz/issues/2069)'s definition
of done: **necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming.**

Linked from requirements-specification.md § Set-level assessment.

**Revision note (round 6).** Following a sixth adversarial review round, this revision: flips `Feasible` from
`Caveat` to `Pass` for RQA-FR-001, RQA-NFR-002, RQA-NFR-003, RQA-FR-030, RQA-NFR-022 and RQA-NFR-028 — none of
these six is actually feasibility-contingent on `#2064` or `ADR-C`; the placement/design-choice context moves to
each row's `Correct` judgement, matching the round-5 treatment already given to `ADR-A`'s five rows (`ADR-B`'s
two rows, RQA-NFR-024/RQA-NFR-030, keep their genuine feasibility caveat); restores a `Correct` caveat on
RQA-NFR-027 that a round-5 rebuild had dropped while two other documents still referenced it; fixes a copy-paste
error in the RQA-NFR-024/RQA-NFR-030 `Correct` bases that mislabelled the floor row as the ceiling; adds
`Unambiguous` caveats to RQA-BR-013, RQA-FR-017, RQA-FR-038, RQA-FR-039, and RQA-NFR-007 for source-inherited
qualifiers or cross-clause imports that were previously bare `Pass`; downgrades RQA-BR-006's `Verifiable` from
`Pass` to `Caveat`, since its fit criterion silently selects the stronger of two source-admitted readings of
P5's own ambiguous conjunction; and updates RQA-BR-010's `Singular`/`Unambiguous` bases to reflect its now-joint
CL-014/CL-017/CL-040 derivation.

---

## How to read this document

One row per (requirement, characteristic) pair — 83 requirements × 9 characteristics = 747 recorded judgements.
Each judgement is `Pass` or `Caveat`; a `Caveat` never means the requirement is dropped or wrong, it means the
judgement is not unqualified and the qualification is recorded rather than smoothed over. `Basis` is `—` where the
judgement follows directly from reading the requirement against its source clause and fit criterion in
requirements-specification.md; a one-line basis is given wherever the judgement takes a position a reader could
reasonably have called differently.

**What each characteristic means, as applied here:**

| Characteristic | Question asked of each requirement |
|---|---|
| Necessary | Would #2006's baseline be under-specified if this requirement were deleted? |
| Appropriate | Is this stated at the right level (business / functional / non-functional) for its source clause? |
| Unambiguous | Does the statement admit only one reading, or does it carry an undefined qualifier from the source? |
| Complete | Does the statement, together with its fit criterion, state the whole of its own obligation? |
| Singular | Does the statement carry exactly one dominant obligation? |
| Feasible | Is satisfying the requirement achievable given #2006's own constraints, or contingent on an open choice? |
| Verifiable | Does the fit criterion in requirements-specification.md give an observable, checkable condition that cannot pass without demonstrating the requirement? |
| Correct | Does the statement accurately reflect its cited source clause's plain reading? |
| Conforming | Does the statement name no mechanism, component, product or technology beyond source-mandated vocabulary? |

---

## Business requirements (RQA-BR-001…014)

| ID | Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|---|
| RQA-BR-001 | Necessary | Pass | — |
| RQA-BR-001 | Appropriate | Pass | — |
| RQA-BR-001 | Unambiguous | Caveat | 'Consistent, auditable, efficient, trustworthy' are the problem statement's own words, each given an operational reading only in the fit criterion, not redefined in the requirement statement itself. |
| RQA-BR-001 | Complete | Pass | — |
| RQA-BR-001 | Singular | Pass | — |
| RQA-BR-001 | Feasible | Pass | — |
| RQA-BR-001 | Verifiable | Pass | — |
| RQA-BR-001 | Correct | Pass | — |
| RQA-BR-001 | Conforming | Pass | — |
| RQA-BR-002 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P1's own specific, independently testable obligation. |
| RQA-BR-002 | Appropriate | Pass | — |
| RQA-BR-002 | Unambiguous | Pass | — |
| RQA-BR-002 | Complete | Pass | — |
| RQA-BR-002 | Singular | Pass | — |
| RQA-BR-002 | Feasible | Pass | — |
| RQA-BR-002 | Verifiable | Pass | — |
| RQA-BR-002 | Correct | Pass | — |
| RQA-BR-002 | Conforming | Pass | — |
| RQA-BR-003 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P2's own specific, independently testable obligation. |
| RQA-BR-003 | Appropriate | Pass | — |
| RQA-BR-003 | Unambiguous | Pass | — |
| RQA-BR-003 | Complete | Pass | — |
| RQA-BR-003 | Singular | Pass | — |
| RQA-BR-003 | Feasible | Pass | — |
| RQA-BR-003 | Verifiable | Pass | — |
| RQA-BR-003 | Correct | Pass | — |
| RQA-BR-003 | Conforming | Pass | — |
| RQA-BR-004 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P3's own specific, independently testable obligation. |
| RQA-BR-004 | Appropriate | Pass | — |
| RQA-BR-004 | Unambiguous | Pass | — |
| RQA-BR-004 | Complete | Pass | — |
| RQA-BR-004 | Singular | Pass | — |
| RQA-BR-004 | Feasible | Pass | — |
| RQA-BR-004 | Verifiable | Pass | — |
| RQA-BR-004 | Correct | Pass | — |
| RQA-BR-004 | Conforming | Pass | — |
| RQA-BR-005 | Necessary | Pass | CL-002's distinct 'creation-time' framing (see its inventory note) is not captured by P4/CL-009 alone or by any other requirement; deleting the 'creation-time' branch of this row would leave that framing uncarried. |
| RQA-BR-005 | Appropriate | Pass | — |
| RQA-BR-005 | Unambiguous | Pass | — |
| RQA-BR-005 | Complete | Pass | — |
| RQA-BR-005 | Singular | Pass | — |
| RQA-BR-005 | Feasible | Pass | — |
| RQA-BR-005 | Verifiable | Pass | — |
| RQA-BR-005 | Correct | Pass | Reworded to a distinguishability obligation, reflecting both cited clauses' plain readings without implying a separate-blocking-mechanism reading that would conflict with C6/AC14. |
| RQA-BR-005 | Conforming | Pass | — |
| RQA-BR-006 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P5's own specific, independently testable obligation. |
| RQA-BR-006 | Appropriate | Pass | — |
| RQA-BR-006 | Unambiguous | Caveat | 'Shall not require a further contributor and a further review cycle' inherits P5's own conjunction from the source ('the fix still needs another contributor and another review cycle') without resolving whether the prohibition reads as ¬(A∧B) — not both together — or ¬A∧¬B — neither at all; #2006 does not disambiguate the conjunction, and this specification carries the ambiguity rather than silently picking a reading, matching the treatment already given to RQA-BR-010 and RQA-FR-034's own inherited qualifiers. |
| RQA-BR-006 | Complete | Pass | — |
| RQA-BR-006 | Singular | Pass | — |
| RQA-BR-006 | Feasible | Pass | — |
| RQA-BR-006 | Verifiable | Caveat | The fit criterion tests the stronger ¬A∧¬B reading (neither a second contributor turn nor a second full review cycle) of P5's own ambiguous conjunction (see this row's Unambiguous caveat), which is one of two source-admitted readings; a solution conforming to the weaker ¬(A∧B) reading alone (avoiding the combination, but still needing one contributor action) would fail this criterion despite conforming to a reading #2006 does not rule out. Recorded here rather than silently resolved by picking the stronger reading as though it were the only one. |
| RQA-BR-006 | Correct | Pass | — |
| RQA-BR-006 | Conforming | Pass | — |
| RQA-BR-007 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P6's own specific, independently testable obligation. |
| RQA-BR-007 | Appropriate | Pass | — |
| RQA-BR-007 | Unambiguous | Pass | — |
| RQA-BR-007 | Complete | Pass | — |
| RQA-BR-007 | Singular | Pass | — |
| RQA-BR-007 | Feasible | Pass | — |
| RQA-BR-007 | Verifiable | Pass | — |
| RQA-BR-007 | Correct | Pass | — |
| RQA-BR-007 | Conforming | Pass | — |
| RQA-BR-008 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P7's own specific, independently testable obligation. |
| RQA-BR-008 | Appropriate | Pass | — |
| RQA-BR-008 | Unambiguous | Pass | — |
| RQA-BR-008 | Complete | Pass | — |
| RQA-BR-008 | Singular | Pass | — |
| RQA-BR-008 | Feasible | Pass | — |
| RQA-BR-008 | Verifiable | Pass | — |
| RQA-BR-008 | Correct | Pass | — |
| RQA-BR-008 | Conforming | Pass | — |
| RQA-BR-009 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P8's own specific, independently testable obligation. |
| RQA-BR-009 | Appropriate | Pass | — |
| RQA-BR-009 | Unambiguous | Pass | — |
| RQA-BR-009 | Complete | Pass | — |
| RQA-BR-009 | Singular | Pass | — |
| RQA-BR-009 | Feasible | Pass | — |
| RQA-BR-009 | Verifiable | Pass | — |
| RQA-BR-009 | Correct | Pass | — |
| RQA-BR-009 | Conforming | Pass | — |
| RQA-BR-010 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P9's own specific, independently testable obligation. |
| RQA-BR-010 | Appropriate | Pass | — |
| RQA-BR-010 | Unambiguous | Caveat | 'Genuinely requires human judgement' synthesises P9/CL-014's own framing with P12/CL-017's and AC13/CL-040's (round 6: now cited as joint source clauses, not merely 'imported'); #2006 does not itself define the line between genuine and non-genuine judgement even across all three clauses, and none is invented here. |
| RQA-BR-010 | Complete | Pass | — |
| RQA-BR-010 | Singular | Pass | One dominant obligation ('progression shall not depend on manual intervention beyond genuine judgement'); citing three source clauses (CL-014, CL-017, CL-040 — round 6) jointly informs that single obligation's qualifier rather than adding a second obligation — see § Singular-split record's CL-017/CL-040 entries. |
| RQA-BR-010 | Feasible | Pass | — |
| RQA-BR-010 | Verifiable | Pass | — |
| RQA-BR-010 | Correct | Pass | — |
| RQA-BR-010 | Conforming | Pass | — |
| RQA-BR-011 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P10's own specific, independently testable obligation. |
| RQA-BR-011 | Appropriate | Pass | — |
| RQA-BR-011 | Unambiguous | Pass | — |
| RQA-BR-011 | Complete | Pass | — |
| RQA-BR-011 | Singular | Pass | — |
| RQA-BR-011 | Feasible | Pass | — |
| RQA-BR-011 | Verifiable | Pass | — |
| RQA-BR-011 | Correct | Pass | — |
| RQA-BR-011 | Conforming | Pass | — |
| RQA-BR-012 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P11's own specific, independently testable obligation. |
| RQA-BR-012 | Appropriate | Pass | — |
| RQA-BR-012 | Unambiguous | Caveat | 'Efficiently' is the problem statement's own word (paraphrasing P11); #2006 does not define an efficiency threshold, and none is invented here — the fit criterion's policy-comparison reading is this specification's own operationalisation, not a definition #2006 supplies. |
| RQA-BR-012 | Complete | Pass | — |
| RQA-BR-012 | Singular | Pass | — |
| RQA-BR-012 | Feasible | Pass | — |
| RQA-BR-012 | Verifiable | Pass | — |
| RQA-BR-012 | Correct | Pass | — |
| RQA-BR-012 | Conforming | Pass | — |
| RQA-BR-013 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P12's own specific, independently testable obligation. |
| RQA-BR-013 | Appropriate | Pass | — |
| RQA-BR-013 | Unambiguous | Caveat | 'Routine, mechanical or non-urgent' is AC13's own vocabulary (P12's framing), undefined there — the same unresolved boundary already caveated on RQA-FR-025's sibling row; #2006 does not state it, and none is invented here. |
| RQA-BR-013 | Complete | Pass | — |
| RQA-BR-013 | Singular | Pass | One dominant obligation; CL-017 was split across RQA-BR-010, RQA-BR-013 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-BR-013 | Feasible | Pass | — |
| RQA-BR-013 | Verifiable | Pass | — |
| RQA-BR-013 | Correct | Pass | — |
| RQA-BR-013 | Conforming | Pass | — |
| RQA-BR-014 | Necessary | Pass | — |
| RQA-BR-014 | Appropriate | Pass | — |
| RQA-BR-014 | Unambiguous | Caveat | 'Important risks, claims and evidence' inherits the problem statement's own qualifier ('the important risks, claims, and evidence associated with a pull request'); #2006 does not define which risks/claims/evidence count as important, and none is invented here. |
| RQA-BR-014 | Complete | Pass | — |
| RQA-BR-014 | Singular | Pass | — |
| RQA-BR-014 | Feasible | Pass | — |
| RQA-BR-014 | Verifiable | Pass | — |
| RQA-BR-014 | Correct | Pass | — |
| RQA-BR-014 | Conforming | Pass | — |

---

## Functional requirements (RQA-FR-001…039)

| ID | Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|---|
| RQA-FR-001 | Necessary | Pass | — |
| RQA-FR-001 | Appropriate | Pass | — |
| RQA-FR-001 | Unambiguous | Pass | — |
| RQA-FR-001 | Complete | Pass | — |
| RQA-FR-001 | Singular | Pass | One dominant obligation; CL-028 was split across RQA-FR-001, RQA-FR-002 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-001 | Feasible | Pass | — |
| RQA-FR-001 | Verifiable | Pass | — |
| RQA-FR-001 | Correct | Pass | Reflects AC01's plain reading; #2064 owns where this specification (and by extension the published protocol definition it requires) is placed, not whether the obligation itself is agreed — a placement question, not a feasibility one (round 6). |
| RQA-FR-001 | Conforming | Pass | — |
| RQA-FR-002 | Necessary | Pass | — |
| RQA-FR-002 | Appropriate | Pass | — |
| RQA-FR-002 | Unambiguous | Pass | — |
| RQA-FR-002 | Complete | Pass | — |
| RQA-FR-002 | Singular | Pass | One dominant obligation; CL-028 was split across RQA-FR-001, RQA-FR-002 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-002 | Feasible | Pass | — |
| RQA-FR-002 | Verifiable | Pass | — |
| RQA-FR-002 | Correct | Pass | — |
| RQA-FR-002 | Conforming | Pass | — |
| RQA-FR-003 | Necessary | Pass | — |
| RQA-FR-003 | Appropriate | Pass | — |
| RQA-FR-003 | Unambiguous | Pass | — |
| RQA-FR-003 | Complete | Pass | — |
| RQA-FR-003 | Singular | Pass | One dominant obligation; CL-029 was split across RQA-FR-003, RQA-FR-004 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-003 | Feasible | Pass | — |
| RQA-FR-003 | Verifiable | Pass | — |
| RQA-FR-003 | Correct | Pass | — |
| RQA-FR-003 | Conforming | Pass | — |
| RQA-FR-004 | Necessary | Pass | — |
| RQA-FR-004 | Appropriate | Pass | — |
| RQA-FR-004 | Unambiguous | Pass | — |
| RQA-FR-004 | Complete | Pass | — |
| RQA-FR-004 | Singular | Pass | One dominant obligation; CL-029 was split across RQA-FR-003, RQA-FR-004 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-004 | Feasible | Pass | — |
| RQA-FR-004 | Verifiable | Pass | — |
| RQA-FR-004 | Correct | Pass | — |
| RQA-FR-004 | Conforming | Pass | — |
| RQA-FR-005 | Necessary | Pass | — |
| RQA-FR-005 | Appropriate | Pass | — |
| RQA-FR-005 | Unambiguous | Pass | — |
| RQA-FR-005 | Complete | Pass | — |
| RQA-FR-005 | Singular | Pass | One dominant obligation; CL-030 was split across RQA-FR-005, RQA-FR-006, RQA-FR-007 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-005 | Feasible | Pass | — |
| RQA-FR-005 | Verifiable | Pass | — |
| RQA-FR-005 | Correct | Pass | — |
| RQA-FR-005 | Conforming | Pass | — |
| RQA-FR-006 | Necessary | Pass | — |
| RQA-FR-006 | Appropriate | Pass | — |
| RQA-FR-006 | Unambiguous | Pass | — |
| RQA-FR-006 | Complete | Pass | — |
| RQA-FR-006 | Singular | Pass | One dominant obligation; CL-030 was split across RQA-FR-005, RQA-FR-006, RQA-FR-007 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-006 | Feasible | Pass | — |
| RQA-FR-006 | Verifiable | Pass | — |
| RQA-FR-006 | Correct | Pass | — |
| RQA-FR-006 | Conforming | Pass | — |
| RQA-FR-007 | Necessary | Pass | — |
| RQA-FR-007 | Appropriate | Pass | — |
| RQA-FR-007 | Unambiguous | Pass | — |
| RQA-FR-007 | Complete | Pass | — |
| RQA-FR-007 | Singular | Pass | One dominant obligation; CL-030 was split across RQA-FR-005, RQA-FR-006, RQA-FR-007 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-007 | Feasible | Pass | — |
| RQA-FR-007 | Verifiable | Pass | — |
| RQA-FR-007 | Correct | Pass | — |
| RQA-FR-007 | Conforming | Pass | — |
| RQA-FR-008 | Necessary | Pass | — |
| RQA-FR-008 | Appropriate | Pass | — |
| RQA-FR-008 | Unambiguous | Pass | — |
| RQA-FR-008 | Complete | Pass | — |
| RQA-FR-008 | Singular | Pass | One dominant obligation; CL-031 was split across RQA-FR-008, RQA-FR-009 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-008 | Feasible | Pass | — |
| RQA-FR-008 | Verifiable | Pass | — |
| RQA-FR-008 | Correct | Pass | — |
| RQA-FR-008 | Conforming | Pass | — |
| RQA-FR-009 | Necessary | Pass | — |
| RQA-FR-009 | Appropriate | Pass | — |
| RQA-FR-009 | Unambiguous | Pass | — |
| RQA-FR-009 | Complete | Pass | — |
| RQA-FR-009 | Singular | Pass | One dominant obligation; CL-031 was split across RQA-FR-008, RQA-FR-009 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-009 | Feasible | Pass | — |
| RQA-FR-009 | Verifiable | Pass | — |
| RQA-FR-009 | Correct | Pass | — |
| RQA-FR-009 | Conforming | Pass | — |
| RQA-FR-010 | Necessary | Pass | — |
| RQA-FR-010 | Appropriate | Pass | — |
| RQA-FR-010 | Unambiguous | Pass | — |
| RQA-FR-010 | Complete | Pass | — |
| RQA-FR-010 | Singular | Pass | One dominant obligation; CL-032 was split across RQA-FR-010, RQA-FR-011 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-010 | Feasible | Pass | — |
| RQA-FR-010 | Verifiable | Pass | — |
| RQA-FR-010 | Correct | Pass | — |
| RQA-FR-010 | Conforming | Pass | — |
| RQA-FR-011 | Necessary | Pass | — |
| RQA-FR-011 | Appropriate | Pass | — |
| RQA-FR-011 | Unambiguous | Pass | — |
| RQA-FR-011 | Complete | Pass | — |
| RQA-FR-011 | Singular | Pass | One dominant obligation; CL-032 was split across RQA-FR-010, RQA-FR-011 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-011 | Feasible | Pass | — |
| RQA-FR-011 | Verifiable | Pass | — |
| RQA-FR-011 | Correct | Pass | — |
| RQA-FR-011 | Conforming | Pass | — |
| RQA-FR-012 | Necessary | Pass | — |
| RQA-FR-012 | Appropriate | Pass | — |
| RQA-FR-012 | Unambiguous | Pass | — |
| RQA-FR-012 | Complete | Pass | — |
| RQA-FR-012 | Singular | Pass | One dominant obligation; CL-033 was split across RQA-FR-012, RQA-FR-013 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-012 | Feasible | Pass | — |
| RQA-FR-012 | Verifiable | Pass | — |
| RQA-FR-012 | Correct | Pass | — |
| RQA-FR-012 | Conforming | Pass | Names 'a single command' — AC06's own vocabulary for the reconstruction interface; no particular command, tool or format is chosen. |
| RQA-FR-013 | Necessary | Pass | — |
| RQA-FR-013 | Appropriate | Pass | — |
| RQA-FR-013 | Unambiguous | Pass | — |
| RQA-FR-013 | Complete | Pass | — |
| RQA-FR-013 | Singular | Pass | One dominant obligation; CL-033 was split across RQA-FR-012, RQA-FR-013 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-013 | Feasible | Pass | — |
| RQA-FR-013 | Verifiable | Pass | — |
| RQA-FR-013 | Correct | Pass | — |
| RQA-FR-013 | Conforming | Pass | — |
| RQA-FR-014 | Necessary | Pass | — |
| RQA-FR-014 | Appropriate | Pass | — |
| RQA-FR-014 | Unambiguous | Pass | — |
| RQA-FR-014 | Complete | Pass | — |
| RQA-FR-014 | Singular | Pass | One dominant obligation; CL-034 was split across RQA-FR-014, RQA-FR-015, RQA-FR-036 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-014 | Feasible | Pass | — |
| RQA-FR-014 | Verifiable | Pass | — |
| RQA-FR-014 | Correct | Pass | — |
| RQA-FR-014 | Conforming | Pass | — |
| RQA-FR-015 | Necessary | Pass | — |
| RQA-FR-015 | Appropriate | Pass | — |
| RQA-FR-015 | Unambiguous | Pass | — |
| RQA-FR-015 | Complete | Pass | — |
| RQA-FR-015 | Singular | Pass | One dominant obligation; CL-034 was split across RQA-FR-014, RQA-FR-015, RQA-FR-036 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-015 | Feasible | Pass | — |
| RQA-FR-015 | Verifiable | Pass | — |
| RQA-FR-015 | Correct | Pass | — |
| RQA-FR-015 | Conforming | Pass | — |
| RQA-FR-016 | Necessary | Pass | — |
| RQA-FR-016 | Appropriate | Pass | — |
| RQA-FR-016 | Unambiguous | Pass | — |
| RQA-FR-016 | Complete | Pass | — |
| RQA-FR-016 | Singular | Pass | — |
| RQA-FR-016 | Feasible | Pass | — |
| RQA-FR-016 | Verifiable | Pass | — |
| RQA-FR-016 | Correct | Pass | — |
| RQA-FR-016 | Conforming | Pass | Names 'one command' — AC08's own vocabulary for the query interface; no particular command, tool or format is chosen. |
| RQA-FR-017 | Necessary | Pass | — |
| RQA-FR-017 | Appropriate | Pass | — |
| RQA-FR-017 | Unambiguous | Caveat | 'Unnecessarily' is AC09's own qualifier ('without unnecessarily creating human intervention'); #2006 does not define which human intervention is necessary versus unnecessary for a given mechanical finding, and none is invented here — round 6's necessity carve-out defers to repository policy where policy speaks, but does not itself define the boundary #2006 leaves open. |
| RQA-FR-017 | Complete | Pass | — |
| RQA-FR-017 | Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-017 | Feasible | Pass | — |
| RQA-FR-017 | Verifiable | Pass | — |
| RQA-FR-017 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds as an agreed obligation under every option of ADR-A; ADR-A decides only whether RQA itself performs the code modification this obligation would apply to, not whether the obligation is agreed. |
| RQA-FR-017 | Conforming | Pass | — |
| RQA-FR-018 | Necessary | Pass | — |
| RQA-FR-018 | Appropriate | Pass | — |
| RQA-FR-018 | Unambiguous | Pass | — |
| RQA-FR-018 | Complete | Pass | — |
| RQA-FR-018 | Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-018 | Feasible | Pass | — |
| RQA-FR-018 | Verifiable | Pass | — |
| RQA-FR-018 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds as an agreed obligation under every option of ADR-A; ADR-A decides only whether RQA itself performs the code modification this obligation would apply to, not whether the obligation is agreed. |
| RQA-FR-018 | Conforming | Pass | — |
| RQA-FR-019 | Necessary | Pass | — |
| RQA-FR-019 | Appropriate | Pass | — |
| RQA-FR-019 | Unambiguous | Pass | — |
| RQA-FR-019 | Complete | Pass | — |
| RQA-FR-019 | Singular | Pass | One dominant obligation; CL-037 was split across RQA-FR-019, RQA-FR-020 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-019 | Feasible | Pass | — |
| RQA-FR-019 | Verifiable | Pass | — |
| RQA-FR-019 | Correct | Pass | — |
| RQA-FR-019 | Conforming | Pass | — |
| RQA-FR-020 | Necessary | Pass | — |
| RQA-FR-020 | Appropriate | Pass | — |
| RQA-FR-020 | Unambiguous | Pass | — |
| RQA-FR-020 | Complete | Pass | — |
| RQA-FR-020 | Singular | Pass | One dominant obligation; CL-037 was split across RQA-FR-019, RQA-FR-020 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-020 | Feasible | Pass | — |
| RQA-FR-020 | Verifiable | Pass | — |
| RQA-FR-020 | Correct | Pass | — |
| RQA-FR-020 | Conforming | Pass | — |
| RQA-FR-021 | Necessary | Pass | — |
| RQA-FR-021 | Appropriate | Pass | — |
| RQA-FR-021 | Unambiguous | Pass | — |
| RQA-FR-021 | Complete | Pass | — |
| RQA-FR-021 | Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-021 | Feasible | Pass | — |
| RQA-FR-021 | Verifiable | Pass | — |
| RQA-FR-021 | Correct | Pass | — |
| RQA-FR-021 | Conforming | Pass | — |
| RQA-FR-022 | Necessary | Pass | — |
| RQA-FR-022 | Appropriate | Pass | — |
| RQA-FR-022 | Unambiguous | Pass | — |
| RQA-FR-022 | Complete | Pass | — |
| RQA-FR-022 | Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-022 | Feasible | Pass | — |
| RQA-FR-022 | Verifiable | Pass | — |
| RQA-FR-022 | Correct | Pass | — |
| RQA-FR-022 | Conforming | Pass | — |
| RQA-FR-023 | Necessary | Pass | — |
| RQA-FR-023 | Appropriate | Pass | — |
| RQA-FR-023 | Unambiguous | Pass | — |
| RQA-FR-023 | Complete | Pass | — |
| RQA-FR-023 | Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-023 | Feasible | Pass | — |
| RQA-FR-023 | Verifiable | Pass | — |
| RQA-FR-023 | Correct | Pass | — |
| RQA-FR-023 | Conforming | Pass | — |
| RQA-FR-024 | Necessary | Pass | — |
| RQA-FR-024 | Appropriate | Pass | — |
| RQA-FR-024 | Unambiguous | Pass | — |
| RQA-FR-024 | Complete | Pass | — |
| RQA-FR-024 | Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-024 | Feasible | Pass | — |
| RQA-FR-024 | Verifiable | Pass | — |
| RQA-FR-024 | Correct | Pass | — |
| RQA-FR-024 | Conforming | Pass | — |
| RQA-FR-025 | Necessary | Pass | — |
| RQA-FR-025 | Appropriate | Pass | — |
| RQA-FR-025 | Unambiguous | Caveat | 'Routine, mechanical or non-urgent' is AC13's own vocabulary, undefined there; #2006 does not state the boundary between a routine/mechanical/non-urgent condition and one requiring escalation, and none is invented here. |
| RQA-FR-025 | Complete | Pass | — |
| RQA-FR-025 | Singular | Pass | One dominant obligation; CL-040 was split across RQA-BR-010, RQA-FR-025, RQA-FR-026, RQA-FR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-025 | Feasible | Pass | — |
| RQA-FR-025 | Verifiable | Pass | — |
| RQA-FR-025 | Correct | Pass | — |
| RQA-FR-025 | Conforming | Pass | — |
| RQA-FR-026 | Necessary | Pass | — |
| RQA-FR-026 | Appropriate | Pass | — |
| RQA-FR-026 | Unambiguous | Pass | — |
| RQA-FR-026 | Complete | Pass | — |
| RQA-FR-026 | Singular | Pass | One dominant obligation; CL-040 was split across RQA-BR-010, RQA-FR-025, RQA-FR-026, RQA-FR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-026 | Feasible | Pass | — |
| RQA-FR-026 | Verifiable | Pass | — |
| RQA-FR-026 | Correct | Pass | — |
| RQA-FR-026 | Conforming | Pass | — |
| RQA-FR-027 | Necessary | Pass | — |
| RQA-FR-027 | Appropriate | Pass | — |
| RQA-FR-027 | Unambiguous | Pass | — |
| RQA-FR-027 | Complete | Pass | — |
| RQA-FR-027 | Singular | Pass | One dominant obligation; CL-040 was split across RQA-BR-010, RQA-FR-025, RQA-FR-026, RQA-FR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-027 | Feasible | Pass | — |
| RQA-FR-027 | Verifiable | Pass | — |
| RQA-FR-027 | Correct | Pass | — |
| RQA-FR-027 | Conforming | Pass | — |
| RQA-FR-028 | Necessary | Pass | — |
| RQA-FR-028 | Appropriate | Pass | — |
| RQA-FR-028 | Unambiguous | Pass | — |
| RQA-FR-028 | Complete | Pass | — |
| RQA-FR-028 | Singular | Pass | One dominant obligation; CL-041 was split across RQA-FR-028, RQA-FR-029, RQA-FR-037 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-028 | Feasible | Pass | — |
| RQA-FR-028 | Verifiable | Pass | — |
| RQA-FR-028 | Correct | Pass | — |
| RQA-FR-028 | Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-041 (AC14) is itself stated in those terms. |
| RQA-FR-029 | Necessary | Pass | — |
| RQA-FR-029 | Appropriate | Pass | — |
| RQA-FR-029 | Unambiguous | Pass | — |
| RQA-FR-029 | Complete | Pass | — |
| RQA-FR-029 | Singular | Pass | Rewritten as a single normative biconditional ('shall merge... if and only if...') carrying exactly one `shall` — a prior two-branch phrasing carried two independently falsifiable `shall`s, which adversarial review found. |
| RQA-FR-029 | Feasible | Pass | — |
| RQA-FR-029 | Verifiable | Pass | — |
| RQA-FR-029 | Correct | Pass | — |
| RQA-FR-029 | Conforming | Pass | — |
| RQA-FR-030 | Necessary | Pass | — |
| RQA-FR-030 | Appropriate | Pass | See RQA-NFR-002's Appropriate basis for the boundary between the two rows: this row concerns any non-built-in harness's admission generally (Must, AC15); RQA-NFR-002 concerns a contributor's optional choice to use a specific conforming integration form (Could, C1's 'may'). |
| RQA-FR-030 | Unambiguous | Pass | — |
| RQA-FR-030 | Complete | Pass | — |
| RQA-FR-030 | Singular | Pass | — |
| RQA-FR-030 | Feasible | Pass | — |
| RQA-FR-030 | Verifiable | Pass | — |
| RQA-FR-030 | Correct | Pass | Reflects its own source clause's plain reading; ADR-C is an undecided design choice at the intersection of AC15 and Security bullet 4, not a textual inconsistency between them, and not a feasibility question — round 6 moved the placement/design-context note here from a Feasible caveat, since satisfaction is not actually contingent on ADR-C's resolution (jointly satisfiable under every source-conforming option) — see the reframed ADR-C draft. |
| RQA-FR-030 | Conforming | Pass | — |
| RQA-FR-031 | Necessary | Pass | — |
| RQA-FR-031 | Appropriate | Pass | — |
| RQA-FR-031 | Unambiguous | Pass | — |
| RQA-FR-031 | Complete | Pass | — |
| RQA-FR-031 | Singular | Pass | — |
| RQA-FR-031 | Feasible | Pass | — |
| RQA-FR-031 | Verifiable | Pass | — |
| RQA-FR-031 | Correct | Pass | — |
| RQA-FR-031 | Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-043 (AC16) is itself stated in those terms. |
| RQA-FR-032 | Necessary | Pass | — |
| RQA-FR-032 | Appropriate | Pass | — |
| RQA-FR-032 | Unambiguous | Pass | — |
| RQA-FR-032 | Complete | Pass | — |
| RQA-FR-032 | Singular | Pass | One dominant obligation; CL-044 was split across RQA-FR-032, RQA-FR-033 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-032 | Feasible | Pass | — |
| RQA-FR-032 | Verifiable | Pass | — |
| RQA-FR-032 | Correct | Pass | — |
| RQA-FR-032 | Conforming | Pass | — |
| RQA-FR-033 | Necessary | Pass | — |
| RQA-FR-033 | Appropriate | Pass | — |
| RQA-FR-033 | Unambiguous | Pass | — |
| RQA-FR-033 | Complete | Pass | — |
| RQA-FR-033 | Singular | Pass | One dominant obligation; CL-044 was split across RQA-FR-032, RQA-FR-033 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-033 | Feasible | Pass | — |
| RQA-FR-033 | Verifiable | Pass | — |
| RQA-FR-033 | Correct | Pass | — |
| RQA-FR-033 | Conforming | Pass | — |
| RQA-FR-034 | Necessary | Pass | — |
| RQA-FR-034 | Appropriate | Pass | — |
| RQA-FR-034 | Unambiguous | Caveat | 'Materially serves' / 'materially simpler' are the source's own qualifiers (§6 rule, closing criterion 1); #2006 does not define a threshold, and none is invented here. Separately, the source's own 'or' between the three grounds admits a literal disjunctive reading under which a component with a materially simpler alternative remains retainable merely for serving a criterion; this specification carries that ambiguity rather than resolving it by silently converting the source's 'or' into an 'and'. |
| RQA-FR-034 | Complete | Pass | — |
| RQA-FR-034 | Singular | Pass | — |
| RQA-FR-034 | Feasible | Pass | — |
| RQA-FR-034 | Verifiable | Pass | — |
| RQA-FR-034 | Correct | Pass | — |
| RQA-FR-034 | Conforming | Pass | Names 'architectural component' — the closing criterion's own vocabulary for what is being justified; no particular architecture is chosen. |
| RQA-FR-035 | Necessary | Pass | — |
| RQA-FR-035 | Appropriate | Pass | — |
| RQA-FR-035 | Unambiguous | Pass | — |
| RQA-FR-035 | Complete | Pass | — |
| RQA-FR-035 | Singular | Pass | — |
| RQA-FR-035 | Feasible | Pass | — |
| RQA-FR-035 | Verifiable | Pass | — |
| RQA-FR-035 | Correct | Pass | — |
| RQA-FR-035 | Conforming | Pass | Names issue numbers #109, #535, #536 verbatim from the source closing criterion (CL-046); these are issue-tracker references the source itself supplies, not a named mechanism, component, product or technology. |
| RQA-FR-036 | Necessary | Pass | — |
| RQA-FR-036 | Appropriate | Pass | — |
| RQA-FR-036 | Unambiguous | Pass | — |
| RQA-FR-036 | Complete | Pass | — |
| RQA-FR-036 | Singular | Pass | One dominant obligation; CL-034 was split across RQA-FR-014, RQA-FR-015, RQA-FR-036 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-036 | Feasible | Pass | — |
| RQA-FR-036 | Verifiable | Pass | — |
| RQA-FR-036 | Correct | Pass | — |
| RQA-FR-036 | Conforming | Pass | — |
| RQA-FR-037 | Necessary | Pass | — |
| RQA-FR-037 | Appropriate | Pass | — |
| RQA-FR-037 | Unambiguous | Pass | — |
| RQA-FR-037 | Complete | Pass | — |
| RQA-FR-037 | Singular | Pass | One dominant obligation; CL-041 was split across RQA-FR-028, RQA-FR-029, RQA-FR-037 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-037 | Feasible | Pass | — |
| RQA-FR-037 | Verifiable | Pass | — |
| RQA-FR-037 | Correct | Pass | — |
| RQA-FR-037 | Conforming | Pass | — |
| RQA-FR-038 | Necessary | Pass | — |
| RQA-FR-038 | Appropriate | Pass | — |
| RQA-FR-038 | Unambiguous | Caveat | 'Safe' is CL-039's own word, used without enumeration; this specification's fit criterion tests the most complete closed set of source-derived safety invariants available (see this row's Verifiable caveat) but cannot claim that set exhausts what #2006 means by 'safe', and none beyond that closed set is invented here. |
| RQA-FR-038 | Complete | Pass | — |
| RQA-FR-038 | Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-038 | Feasible | Pass | — |
| RQA-FR-038 | Verifiable | Caveat | CL-039 uses 'safe' without enumerating what safety consists of. The fit criterion tests every source-derived security invariant this specification separately states (RQA-NFR-010, RQA-NFR-018, RQA-NFR-022, RQA-NFR-028, RQA-NFR-019…021), which is the most complete closed set available from the extract, but cannot rule out a safety property #2006 gestures at without stating; recorded as an open-texture limitation rather than claimed as an exhaustive definition of 'safe'. |
| RQA-FR-038 | Correct | Pass | — |
| RQA-FR-038 | Conforming | Pass | — |
| RQA-FR-039 | Necessary | Pass | — |
| RQA-FR-039 | Appropriate | Pass | — |
| RQA-FR-039 | Unambiguous | Caveat | AC11's 'a configured bound... produces a configured fallback' is read as the fallback becoming the run's terminal outcome (matching RQA-FR-022's 'ends in one of the three named outcomes'), not as the run continuing to a successful disposition through the fallback (the reading AC12's parallel 'continues through an explicitly configured fallback' could support by analogy). The 'produces' / 'continues through' wording contrast is this row's basis for the reading chosen; #2006 does not disambiguate the two readings for AC11 specifically, and this specification records the choice rather than treating it as the only possible one. |
| RQA-FR-039 | Complete | Pass | — |
| RQA-FR-039 | Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-039 | Feasible | Pass | — |
| RQA-FR-039 | Verifiable | Pass | — |
| RQA-FR-039 | Correct | Pass | — |
| RQA-FR-039 | Conforming | Pass | — |

---

## Non-functional requirements (RQA-NFR-001…030)

| ID | Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|---|
| RQA-NFR-001 | Necessary | Pass | — |
| RQA-NFR-001 | Appropriate | Pass | — |
| RQA-NFR-001 | Unambiguous | Pass | — |
| RQA-NFR-001 | Complete | Pass | — |
| RQA-NFR-001 | Singular | Pass | One dominant obligation; CL-018 was split across RQA-NFR-001, RQA-NFR-002 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-001 | Feasible | Pass | — |
| RQA-NFR-001 | Verifiable | Pass | — |
| RQA-NFR-001 | Correct | Pass | — |
| RQA-NFR-001 | Conforming | Pass | — |
| RQA-NFR-002 | Necessary | Pass | — |
| RQA-NFR-002 | Appropriate | Pass | Priced Could because C1's own text says a contributor 'may' use a thin skill/plugin/hook — using one is the contributor's option; the system's obligation to accommodate that choice, once made, is unconditional (round 6 restatement), which is why this row (the contributor-side option) and RQA-FR-030 (the system-side obligation to admit a non-built-in harness generally) carry different priorities without duplicating each other's subject matter. |
| RQA-NFR-002 | Unambiguous | Pass | — |
| RQA-NFR-002 | Complete | Pass | — |
| RQA-NFR-002 | Singular | Pass | One dominant obligation; CL-018 was split across RQA-NFR-001, RQA-NFR-002 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-002 | Feasible | Pass | — |
| RQA-NFR-002 | Verifiable | Pass | — |
| RQA-NFR-002 | Correct | Pass | Round 6: restated so the system's obligation is to accommodate participation through the published contract, not to implement acceptance of three named mechanism forms specifically; #2064's placement question does not bear on whether this obligation is agreed. |
| RQA-NFR-002 | Conforming | Pass | Names 'skill, plugin or hook' — C1's own vocabulary for the optional integration path, not a mechanism chosen by this specification. |
| RQA-NFR-003 | Necessary | Pass | — |
| RQA-NFR-003 | Appropriate | Pass | — |
| RQA-NFR-003 | Unambiguous | Caveat | 'Where practical' is C2's own qualifier; #2006 does not state what makes a case impractical. The fit criterion now evaluates the contract and the format separately, each requiring all three named qualities conjunctively or an independently verified, specific, evidenced impracticality reason, narrowing (without eliminating) the residual ambiguity — what counts as sufficiently 'evidenced' is still not defined by #2006, and none is invented here. |
| RQA-NFR-003 | Complete | Pass | — |
| RQA-NFR-003 | Singular | Pass | — |
| RQA-NFR-003 | Feasible | Pass | — |
| RQA-NFR-003 | Verifiable | Pass | — |
| RQA-NFR-003 | Correct | Pass | Reflects C2's plain reading, conjunctively per artifact (round 6); #2064's placement question does not bear on whether this obligation is agreed. |
| RQA-NFR-003 | Conforming | Pass | — |
| RQA-NFR-004 | Necessary | Pass | — |
| RQA-NFR-004 | Appropriate | Pass | — |
| RQA-NFR-004 | Unambiguous | Pass | — |
| RQA-NFR-004 | Complete | Pass | — |
| RQA-NFR-004 | Singular | Pass | — |
| RQA-NFR-004 | Feasible | Pass | — |
| RQA-NFR-004 | Verifiable | Pass | — |
| RQA-NFR-004 | Correct | Pass | — |
| RQA-NFR-004 | Conforming | Pass | — |
| RQA-NFR-005 | Necessary | Pass | — |
| RQA-NFR-005 | Appropriate | Pass | — |
| RQA-NFR-005 | Unambiguous | Pass | — |
| RQA-NFR-005 | Complete | Pass | — |
| RQA-NFR-005 | Singular | Pass | — |
| RQA-NFR-005 | Feasible | Pass | — |
| RQA-NFR-005 | Verifiable | Pass | — |
| RQA-NFR-005 | Correct | Pass | — |
| RQA-NFR-005 | Conforming | Pass | — |
| RQA-NFR-006 | Necessary | Pass | — |
| RQA-NFR-006 | Appropriate | Pass | — |
| RQA-NFR-006 | Unambiguous | Pass | — |
| RQA-NFR-006 | Complete | Pass | — |
| RQA-NFR-006 | Singular | Pass | — |
| RQA-NFR-006 | Feasible | Pass | — |
| RQA-NFR-006 | Verifiable | Pass | — |
| RQA-NFR-006 | Correct | Pass | — |
| RQA-NFR-006 | Conforming | Pass | — |
| RQA-NFR-007 | Necessary | Pass | — |
| RQA-NFR-007 | Appropriate | Pass | — |
| RQA-NFR-007 | Unambiguous | Caveat | 'Whenever progression remains possible' is imported from AC08/CL-035's 'unable to progress' disposition and AC12/CL-039's mandated safe stop, not stated by C6/CL-023 itself; the harmonisation is necessary (a literal reading of C6 alone would contradict AC12's mandated stop and AC08's disposition, both baseline acceptance criteria in the same extract), and this specification records the cross-clause import rather than treating the qualifier as C6's own unqualified text — matching the treatment already given to RQA-BR-010's own cross-clause import (round 6, fable). |
| RQA-NFR-007 | Complete | Pass | — |
| RQA-NFR-007 | Singular | Pass | One dominant obligation; CL-023 was split across RQA-NFR-007, RQA-NFR-008 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-007 | Feasible | Pass | — |
| RQA-NFR-007 | Verifiable | Pass | — |
| RQA-NFR-007 | Correct | Pass | — |
| RQA-NFR-007 | Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-023 (C6) is itself stated in those terms. |
| RQA-NFR-008 | Necessary | Pass | — |
| RQA-NFR-008 | Appropriate | Pass | — |
| RQA-NFR-008 | Unambiguous | Pass | — |
| RQA-NFR-008 | Complete | Pass | — |
| RQA-NFR-008 | Singular | Pass | One dominant obligation; CL-023 was split across RQA-NFR-007, RQA-NFR-008 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-008 | Feasible | Pass | — |
| RQA-NFR-008 | Verifiable | Pass | — |
| RQA-NFR-008 | Correct | Pass | — |
| RQA-NFR-008 | Conforming | Pass | — |
| RQA-NFR-009 | Necessary | Pass | — |
| RQA-NFR-009 | Appropriate | Pass | — |
| RQA-NFR-009 | Unambiguous | Pass | — |
| RQA-NFR-009 | Complete | Pass | — |
| RQA-NFR-009 | Singular | Pass | One dominant obligation; CL-024 was split across RQA-NFR-009, RQA-NFR-010, RQA-NFR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-009 | Feasible | Pass | — |
| RQA-NFR-009 | Verifiable | Pass | — |
| RQA-NFR-009 | Correct | Pass | — |
| RQA-NFR-009 | Conforming | Pass | — |
| RQA-NFR-010 | Necessary | Pass | — |
| RQA-NFR-010 | Appropriate | Pass | — |
| RQA-NFR-010 | Unambiguous | Pass | — |
| RQA-NFR-010 | Complete | Pass | — |
| RQA-NFR-010 | Singular | Pass | One dominant obligation; CL-024 was split across RQA-NFR-009, RQA-NFR-010, RQA-NFR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-010 | Feasible | Pass | — |
| RQA-NFR-010 | Verifiable | Pass | — |
| RQA-NFR-010 | Correct | Pass | — |
| RQA-NFR-010 | Conforming | Pass | — |
| RQA-NFR-011 | Necessary | Pass | — |
| RQA-NFR-011 | Appropriate | Pass | — |
| RQA-NFR-011 | Unambiguous | Pass | — |
| RQA-NFR-011 | Complete | Pass | — |
| RQA-NFR-011 | Singular | Pass | — |
| RQA-NFR-011 | Feasible | Pass | — |
| RQA-NFR-011 | Verifiable | Pass | — |
| RQA-NFR-011 | Correct | Pass | — |
| RQA-NFR-011 | Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-025 (C8) is itself stated in those terms. |
| RQA-NFR-012 | Necessary | Pass | — |
| RQA-NFR-012 | Appropriate | Pass | — |
| RQA-NFR-012 | Unambiguous | Pass | — |
| RQA-NFR-012 | Complete | Pass | — |
| RQA-NFR-012 | Singular | Pass | One dominant obligation; CL-026 was split across RQA-NFR-012, RQA-NFR-013, RQA-NFR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-012 | Feasible | Pass | — |
| RQA-NFR-012 | Verifiable | Pass | — |
| RQA-NFR-012 | Correct | Pass | — |
| RQA-NFR-012 | Conforming | Pass | — |
| RQA-NFR-013 | Necessary | Pass | — |
| RQA-NFR-013 | Appropriate | Pass | — |
| RQA-NFR-013 | Unambiguous | Caveat | 'Appropriate to sensitivity' is C9's own qualifier; #2006 does not define a sensitivity scale, and none is invented here. |
| RQA-NFR-013 | Complete | Pass | — |
| RQA-NFR-013 | Singular | Pass | One dominant obligation; CL-026 was split across RQA-NFR-012, RQA-NFR-013, RQA-NFR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-013 | Feasible | Pass | — |
| RQA-NFR-013 | Verifiable | Pass | — |
| RQA-NFR-013 | Correct | Pass | — |
| RQA-NFR-013 | Conforming | Pass | — |
| RQA-NFR-014 | Necessary | Pass | — |
| RQA-NFR-014 | Appropriate | Pass | — |
| RQA-NFR-014 | Unambiguous | Pass | — |
| RQA-NFR-014 | Complete | Pass | — |
| RQA-NFR-014 | Singular | Pass | — |
| RQA-NFR-014 | Feasible | Pass | — |
| RQA-NFR-014 | Verifiable | Pass | — |
| RQA-NFR-014 | Correct | Pass | — |
| RQA-NFR-014 | Conforming | Pass | — |
| RQA-NFR-015 | Necessary | Pass | — |
| RQA-NFR-015 | Appropriate | Pass | — |
| RQA-NFR-015 | Unambiguous | Pass | — |
| RQA-NFR-015 | Complete | Pass | — |
| RQA-NFR-015 | Singular | Pass | One dominant obligation; CL-055 was split across RQA-NFR-015, RQA-NFR-016 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-015 | Feasible | Pass | — |
| RQA-NFR-015 | Verifiable | Pass | — |
| RQA-NFR-015 | Correct | Pass | — |
| RQA-NFR-015 | Conforming | Pass | — |
| RQA-NFR-016 | Necessary | Pass | — |
| RQA-NFR-016 | Appropriate | Pass | — |
| RQA-NFR-016 | Unambiguous | Pass | — |
| RQA-NFR-016 | Complete | Pass | — |
| RQA-NFR-016 | Singular | Pass | One dominant obligation; CL-055 was split across RQA-NFR-015, RQA-NFR-016 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-016 | Feasible | Pass | — |
| RQA-NFR-016 | Verifiable | Pass | — |
| RQA-NFR-016 | Correct | Pass | — |
| RQA-NFR-016 | Conforming | Pass | — |
| RQA-NFR-017 | Necessary | Pass | — |
| RQA-NFR-017 | Appropriate | Pass | — |
| RQA-NFR-017 | Unambiguous | Pass | — |
| RQA-NFR-017 | Complete | Pass | — |
| RQA-NFR-017 | Singular | Pass | One dominant obligation; CL-056 was split across RQA-NFR-017, RQA-NFR-018, RQA-NFR-026 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-017 | Feasible | Pass | — |
| RQA-NFR-017 | Verifiable | Pass | — |
| RQA-NFR-017 | Correct | Pass | — |
| RQA-NFR-017 | Conforming | Pass | — |
| RQA-NFR-018 | Necessary | Pass | — |
| RQA-NFR-018 | Appropriate | Pass | — |
| RQA-NFR-018 | Unambiguous | Pass | — |
| RQA-NFR-018 | Complete | Pass | — |
| RQA-NFR-018 | Singular | Pass | One dominant obligation; CL-056 was split across RQA-NFR-017, RQA-NFR-018, RQA-NFR-026 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-018 | Feasible | Pass | — |
| RQA-NFR-018 | Verifiable | Pass | — |
| RQA-NFR-018 | Correct | Pass | — |
| RQA-NFR-018 | Conforming | Pass | — |
| RQA-NFR-019 | Necessary | Pass | — |
| RQA-NFR-019 | Appropriate | Pass | — |
| RQA-NFR-019 | Unambiguous | Pass | — |
| RQA-NFR-019 | Complete | Pass | — |
| RQA-NFR-019 | Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-019 | Feasible | Pass | — |
| RQA-NFR-019 | Verifiable | Pass | — |
| RQA-NFR-019 | Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. This bound holds as an agreed obligation under every option of ADR-A; ADR-A decides only whether remediation authority has a live case to constrain, not whether the bound itself is agreed — an applicability scenario, not a satisfaction contingency. |
| RQA-NFR-019 | Conforming | Pass | — |
| RQA-NFR-020 | Necessary | Pass | — |
| RQA-NFR-020 | Appropriate | Pass | — |
| RQA-NFR-020 | Unambiguous | Pass | — |
| RQA-NFR-020 | Complete | Pass | — |
| RQA-NFR-020 | Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-020 | Feasible | Pass | — |
| RQA-NFR-020 | Verifiable | Pass | — |
| RQA-NFR-020 | Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. This bound holds as an agreed obligation under every option of ADR-A; ADR-A decides only whether remediation authority has a live case to constrain, not whether the bound itself is agreed — an applicability scenario, not a satisfaction contingency. |
| RQA-NFR-020 | Conforming | Pass | Names 'working tree' — CL-057's own term for the isolation boundary, not a chosen isolation mechanism (the fit criterion deliberately does not name one). |
| RQA-NFR-021 | Necessary | Pass | — |
| RQA-NFR-021 | Appropriate | Pass | — |
| RQA-NFR-021 | Unambiguous | Pass | — |
| RQA-NFR-021 | Complete | Pass | — |
| RQA-NFR-021 | Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-021 | Feasible | Pass | — |
| RQA-NFR-021 | Verifiable | Pass | — |
| RQA-NFR-021 | Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. This bound holds as an agreed obligation under every option of ADR-A; ADR-A decides only whether remediation authority has a live case to constrain, not whether the bound itself is agreed — an applicability scenario, not a satisfaction contingency. |
| RQA-NFR-021 | Conforming | Pass | Names 'force-push', 'merge', 'branch protection' and 'protected branch' — CL-057's own enumerated prohibitions, carried verbatim. |
| RQA-NFR-022 | Necessary | Pass | — |
| RQA-NFR-022 | Appropriate | Pass | — |
| RQA-NFR-022 | Unambiguous | Pass | — |
| RQA-NFR-022 | Complete | Pass | — |
| RQA-NFR-022 | Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-022 | Feasible | Pass | — |
| RQA-NFR-022 | Verifiable | Pass | — |
| RQA-NFR-022 | Correct | Pass | Reflects its own source clause's plain reading; ADR-C is an undecided design choice at the intersection of AC15 and Security bullet 4, not a textual inconsistency between them, and not a feasibility question — round 6 moved the placement/design-context note here from a Feasible caveat, since satisfaction is not actually contingent on ADR-C's resolution (jointly satisfiable under every source-conforming option) — see the reframed ADR-C draft. |
| RQA-NFR-022 | Conforming | Pass | — |
| RQA-NFR-023 | Necessary | Pass | — |
| RQA-NFR-023 | Appropriate | Pass | — |
| RQA-NFR-023 | Unambiguous | Pass | — |
| RQA-NFR-023 | Complete | Pass | — |
| RQA-NFR-023 | Singular | Pass | One dominant obligation; CL-059 was split across RQA-NFR-023, RQA-NFR-029 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-023 | Feasible | Pass | — |
| RQA-NFR-023 | Verifiable | Pass | — |
| RQA-NFR-023 | Correct | Pass | — |
| RQA-NFR-023 | Conforming | Pass | — |
| RQA-NFR-024 | Necessary | Pass | — |
| RQA-NFR-024 | Appropriate | Pass | — |
| RQA-NFR-024 | Unambiguous | Caveat | Round 6 follow-up: whether CL-060's credential floor applies unconditionally to every managed repository or only to those configured for authority CL-056 would actually exercise is not resolved by CL-060's own text; this row picks the narrower, activity-conditioned reading (see its Correct caveat) rather than treating the unconditional reading as the only one, but #2006 itself does not disambiguate the two. |
| RQA-NFR-024 | Complete | Pass | — |
| RQA-NFR-024 | Singular | Pass | Split from a prior two-`shall` row (floor + ceiling) into this row (floor only, the positive permission set) and RQA-NFR-030 (ceiling only, the no-broader-permission and no-unmanaged-repository prohibition) — see § Singular-split record's CL-060 entry. |
| RQA-NFR-024 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-B owns an open, **externally-contingent feasibility** question (whether the enumerated credential scope admits the merge/push actions elsewhere required, given GitHub's own permission model — a premise the extract never states) this row's full satisfaction is contingent on — see § Set-level assessment's Consistent row. |
| RQA-NFR-024 | Verifiable | Pass | — |
| RQA-NFR-024 | Correct | Caveat | CL-060 states the credential floor unconditionally ('A GitHub token scoped to the target repositories with pull-requests write and contents read'), with no activity-configuration qualifier in its own text. This row reads that floor as conditioned on the repository being configured to submit authoritative review outcomes — narrower activity (e.g. advisory-only, per CL-055's own contemplation of that authority level) needs only the permissions that narrower activity requires — because an unconditional floor would hand pull-request write to a repository configured never to exercise it, which conflicts with CL-056's own least-privilege, default-disabled, per-activity authorisation principle for the same credential. This is a recorded interpretive choice, not CL-060's own literal, unconditional wording; ADR-B (kept) already owns the adjacent external-feasibility question of whether this scope suffices for the activities configured, so no second ADR is raised for this narrower, source-internal reading. |
| RQA-NFR-024 | Conforming | Pass | Names 'pull-request write' and 'repository-content read' — the Security implications section's own credential-scope vocabulary, carried verbatim rather than translated into a platform-specific permission name. |
| RQA-NFR-025 | Necessary | Pass | — |
| RQA-NFR-025 | Appropriate | Pass | — |
| RQA-NFR-025 | Unambiguous | Pass | — |
| RQA-NFR-025 | Complete | Pass | — |
| RQA-NFR-025 | Singular | Pass | One dominant obligation; CL-060 was split across RQA-NFR-024, RQA-NFR-025, RQA-NFR-030 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-025 | Feasible | Pass | — |
| RQA-NFR-025 | Verifiable | Pass | — |
| RQA-NFR-025 | Correct | Pass | — |
| RQA-NFR-025 | Conforming | Pass | Names 'deploy-key', 'relay' and 'VPS' — the Security implications section's own enumerated exclusions, carried verbatim. |
| RQA-NFR-026 | Necessary | Pass | — |
| RQA-NFR-026 | Appropriate | Pass | — |
| RQA-NFR-026 | Unambiguous | Pass | — |
| RQA-NFR-026 | Complete | Pass | — |
| RQA-NFR-026 | Singular | Pass | One dominant obligation; CL-056 was split across RQA-NFR-017, RQA-NFR-018, RQA-NFR-026 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-026 | Feasible | Pass | — |
| RQA-NFR-026 | Verifiable | Pass | — |
| RQA-NFR-026 | Correct | Pass | — |
| RQA-NFR-026 | Conforming | Pass | — |
| RQA-NFR-027 | Necessary | Pass | — |
| RQA-NFR-027 | Appropriate | Pass | — |
| RQA-NFR-027 | Unambiguous | Pass | — |
| RQA-NFR-027 | Complete | Pass | — |
| RQA-NFR-027 | Singular | Pass | One dominant obligation; CL-024 was split across RQA-NFR-009, RQA-NFR-010, RQA-NFR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-027 | Feasible | Pass | — |
| RQA-NFR-027 | Verifiable | Pass | — |
| RQA-NFR-027 | Correct | Caveat | Derivation is conjunctive — cited from both CL-024 and CL-026, not a single clause. C7's 'only when explicitly configured' configuration-gating principle is applied to C9's own named content types (code, diffs, metadata, evidence) and C9's own permitted act (sending to an external provider); neither clause alone states this prohibition, but read together they entail it. This is an inferential step across two clauses, not a quotation from either, and is recorded as such rather than asserted as a single-clause literal derivation. |
| RQA-NFR-027 | Conforming | Pass | — |
| RQA-NFR-028 | Necessary | Pass | — |
| RQA-NFR-028 | Appropriate | Pass | — |
| RQA-NFR-028 | Unambiguous | Pass | — |
| RQA-NFR-028 | Complete | Pass | — |
| RQA-NFR-028 | Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-028 | Feasible | Pass | — |
| RQA-NFR-028 | Verifiable | Pass | — |
| RQA-NFR-028 | Correct | Pass | Reflects its own source clause's plain reading; ADR-C is an undecided design choice at the intersection of AC15 and Security bullet 4, not a textual inconsistency between them, and not a feasibility question — round 6 moved the placement/design-context note here from a Feasible caveat, since satisfaction is not actually contingent on ADR-C's resolution (jointly satisfiable under every source-conforming option) — see the reframed ADR-C draft. |
| RQA-NFR-028 | Conforming | Pass | — |
| RQA-NFR-029 | Necessary | Pass | — |
| RQA-NFR-029 | Appropriate | Pass | — |
| RQA-NFR-029 | Unambiguous | Pass | — |
| RQA-NFR-029 | Complete | Pass | — |
| RQA-NFR-029 | Singular | Pass | One dominant obligation; CL-059 was split across RQA-NFR-023, RQA-NFR-029 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-029 | Feasible | Pass | — |
| RQA-NFR-029 | Verifiable | Pass | — |
| RQA-NFR-029 | Correct | Pass | — |
| RQA-NFR-029 | Conforming | Pass | — |
| RQA-NFR-030 | Necessary | Pass | — |
| RQA-NFR-030 | Appropriate | Pass | — |
| RQA-NFR-030 | Unambiguous | Pass | — |
| RQA-NFR-030 | Complete | Pass | — |
| RQA-NFR-030 | Singular | Pass | One dominant obligation; CL-060 was split across RQA-NFR-024, RQA-NFR-025, RQA-NFR-030 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-030 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-B owns an open, **externally-contingent feasibility** question (whether the enumerated credential scope admits the merge/push actions elsewhere required, given GitHub's own permission model — a premise the extract never states) this row's full satisfaction is contingent on — see § Set-level assessment's Consistent row. |
| RQA-NFR-030 | Verifiable | Pass | — |
| RQA-NFR-030 | Correct | Pass | Reflects the Security implications section's plain-reading credential-scope statement, split into its floor (RQA-NFR-024) and ceiling (this row) rather than one row asserting both; ADR-B (reframed) asks whether that scope is feasible given GitHub's external permission model, not whether the scope statement itself is agreed. |
| RQA-NFR-030 | Conforming | Pass | Names 'pull-request write' and 'repository-content read' — the Security implications section's own credential-scope vocabulary, carried verbatim rather than translated into a platform-specific permission name. |

---

## Summary

- 747 judgements recorded across 83 requirements and 9 characteristics.
- Every judgement is `Pass` except the deliberate `Caveat`s below, none of which mark a requirement as failing —
  each records a qualification the requirement inherits from #2006's own text, from an open ADR question, from a
  multi-clause derivation step, or from an open-textured source term, rather than from a defect introduced in
  derivation:
  - **Feasible caveats**: only `ADR-B`'s two rows now carry one — RQA-NFR-024, RQA-NFR-030 (round 6: the other
    six rows that previously carried a `#2064`- or `ADR-C`-attributed caveat, RQA-FR-001/RQA-NFR-002/
    RQA-NFR-003/RQA-FR-030/RQA-NFR-022/RQA-NFR-028, are now `Pass` — none of the six is actually contingent on
    those questions; see each row's `Correct` judgement for the placement/design context instead).
  - **Unambiguous caveats**: RQA-BR-001, RQA-BR-006, RQA-BR-010, RQA-BR-012, RQA-BR-013, RQA-BR-014, RQA-FR-017,
    RQA-FR-025, RQA-FR-034, RQA-FR-038, RQA-FR-039 (new round 6), RQA-NFR-003, RQA-NFR-007 (new round 6),
    RQA-NFR-013, RQA-NFR-024 (new, follow-up fix). RQA-NFR-011 is `Pass` (its round-3 ambiguity was removed by the round-4 positive-only rewrite).
  - **Correct caveats**: RQA-NFR-027 (restored round 6 — records its conjunctive CL-024-and-CL-026 derivation
    as an inferential step across two clauses, not a quotation from either); RQA-NFR-024 (follow-up fix —
    records that this row conditions CL-060's unconditional credential floor on the repository being
    configured to submit authoritative review outcomes, an interpretive choice adopted because the
    unconditional reading would conflict with CL-056's least-privilege, default-disabled principle for the
    same credential).
  - **Verifiable caveats**: RQA-FR-038 (records CL-039's open-textured "safe" rather than an unqualified Pass);
    RQA-BR-006 (new round 6 — records that the fit criterion selects the stronger of two source-admitted
    readings of P5's ambiguous conjunction, rather than treating it as the only possible reading).
- Corrected across rounds 1–5: six `Singular` verdicts split into new rows; well over two dozen `Verifiable`
  verdicts whose fit criteria were rewritten across successive rounds; the `Conforming` basis for every
  GitHub/source-vocabulary row; the `Necessary`/`Correct` bases for RQA-BR-005; `Singular` for RQA-FR-029 and
  RQA-NFR-024; `Feasible`/`Correct` for the five `ADR-A` rows (round 5).
- Corrected round 6: `Verifiable` for RQA-NFR-002 (no longer three mandated mechanism forms), RQA-FR-008 (no
  invented exactly-one cardinality), RQA-BR-013 (interruption only, not resolution/progression), RQA-FR-013
  (restored assurance-use predicate), RQA-FR-018 (validity retention only, not re-run avoidance), RQA-FR-005 and
  RQA-NFR-003 (oscillation-adjudicated compromise wordings — see requirements-specification.md's Revision note),
  and RQA-FR-017 (necessity carve-out clarified, not replaced); `Feasible` for six rows (see above); `Correct`
  for RQA-NFR-027 (restored caveat) and RQA-NFR-024/RQA-NFR-030 (copy-paste fix); `Singular`/`Unambiguous` for
  RQA-BR-010 (joint CL-014/CL-017/CL-040 derivation); new `Unambiguous` caveats for RQA-BR-013, RQA-FR-017,
  RQA-FR-038, RQA-FR-039, RQA-NFR-007.
