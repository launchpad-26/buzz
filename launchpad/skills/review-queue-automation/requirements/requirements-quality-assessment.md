# RQA requirements quality assessment

Per-requirement assessment of every requirement in
[`requirements-specification.md`](requirements-specification.md) against the nine individual requirement
characteristics named in [launchpad-26/buzz#2069](https://github.com/launchpad-26/buzz/issues/2069)'s definition
of done: **necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming.**

Linked from requirements-specification.md § Set-level assessment.

**Revision note (round 3).** Following a third adversarial review round, this revision: rewrites the `Verifiable`
bases for RQA-NFR-022/RQA-NFR-028 (whole-record provenance protection) and RQA-NFR-019/020/021 (effective
authority, not benign run history) after review showed both groups' prior fit criteria could pass while the
cited security guarantee was materially violated; corrects `Correct` for RQA-NFR-027 from a bare `Pass` to a
`Caveat` recording its round-3 re-derivation from CL-024 rather than CL-026; replaces "every option ADR-C lists"
with "every **source-conforming** option" in every RQA-FR-030/RQA-NFR-022/RQA-NFR-028 Feasible caveat, so this
document cannot be read as endorsing ADR-C's non-conforming option 3; adds an Unambiguous caveat to RQA-BR-006
for its inherited P5 conjunction ambiguity, matching the treatment already given to RQA-BR-010/RQA-FR-034; and
corrects the Conforming basis for RQA-FR-034 ("component" → "architectural component") to match its restored
statement wording.

---

## How to read this document

One row per (requirement, characteristic) pair — 82 requirements × 9 characteristics = 738 recorded judgements.
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
| RQA-BR-005 | Necessary | Pass | Round 2: CL-002's distinct 'creation-time' framing (see its inventory note) is not captured by P4/CL-009 alone or by any other requirement; deleting the 'creation-time' branch of this row would leave that framing uncarried. |
| RQA-BR-005 | Appropriate | Pass | — |
| RQA-BR-005 | Unambiguous | Pass | — |
| RQA-BR-005 | Complete | Pass | — |
| RQA-BR-005 | Singular | Pass | — |
| RQA-BR-005 | Feasible | Pass | — |
| RQA-BR-005 | Verifiable | Pass | — |
| RQA-BR-005 | Correct | Pass | Reflects both cited clauses' plain readings jointly: P4/CL-009's 'mechanical' and 'procedural' findings, and CL-002's additional 'creation-time' framing of the same shared-blocking-mechanism problem. |
| RQA-BR-005 | Conforming | Pass | — |
| RQA-BR-006 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P5's own specific, independently testable obligation. |
| RQA-BR-006 | Appropriate | Pass | — |
| RQA-BR-006 | Unambiguous | Caveat | 'Shall not require a further contributor and a further review cycle' inherits P5's own conjunction from the source ('the fix still needs another contributor and another review cycle') without resolving whether the prohibition reads as ¬(A∧B) — not both together — or ¬A∧¬B — neither at all; #2006 does not disambiguate the conjunction, and this specification carries the ambiguity rather than silently picking a reading, matching the treatment already given to RQA-BR-010 and RQA-FR-034's own inherited qualifiers. |
| RQA-BR-006 | Complete | Pass | — |
| RQA-BR-006 | Singular | Pass | — |
| RQA-BR-006 | Feasible | Pass | — |
| RQA-BR-006 | Verifiable | Pass | — |
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
| RQA-BR-010 | Unambiguous | Caveat | 'Genuinely requires human judgement' imports P12/AC13's framing into P9's own text, which names no such qualifier; #2006 does not define the line between genuine and non-genuine judgement, and none is invented here. |
| RQA-BR-010 | Complete | Pass | — |
| RQA-BR-010 | Singular | Pass | — |
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
| RQA-BR-012 | Unambiguous | Pass | — |
| RQA-BR-012 | Complete | Pass | — |
| RQA-BR-012 | Singular | Pass | — |
| RQA-BR-012 | Feasible | Pass | — |
| RQA-BR-012 | Verifiable | Pass | — |
| RQA-BR-012 | Correct | Pass | — |
| RQA-BR-012 | Conforming | Pass | — |
| RQA-BR-013 | Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P12's own specific, independently testable obligation. |
| RQA-BR-013 | Appropriate | Pass | — |
| RQA-BR-013 | Unambiguous | Pass | — |
| RQA-BR-013 | Complete | Pass | — |
| RQA-BR-013 | Singular | Pass | — |
| RQA-BR-013 | Feasible | Pass | — |
| RQA-BR-013 | Verifiable | Pass | — |
| RQA-BR-013 | Correct | Pass | — |
| RQA-BR-013 | Conforming | Pass | — |
| RQA-BR-014 | Necessary | Pass | — |
| RQA-BR-014 | Appropriate | Pass | — |
| RQA-BR-014 | Unambiguous | Pass | — |
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
| RQA-FR-001 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); #2064 owns the open question of where launchpad-repo policy/contract documents publish, named in requirements-specification.md § Provenance and pin — not a tension recorded in § Set-level assessment, which discusses only ADR-A/B/C. |
| RQA-FR-001 | Verifiable | Pass | — |
| RQA-FR-001 | Correct | Pass | — |
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
| RQA-FR-017 | Unambiguous | Pass | — |
| RQA-FR-017 | Complete | Pass | — |
| RQA-FR-017 | Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-017 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-A owns an open **mechanism** question (whether RQA itself performs the code modification this row's authority bounds) this row's full satisfaction is contingent on — see requirements-specification.md § Set-level assessment's Consistent row. |
| RQA-FR-017 | Verifiable | Pass | — |
| RQA-FR-017 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds under every option of ADR-A; ADR-A decides whether RQA itself performs the code modification, not whether this row's own obligation is agreed. |
| RQA-FR-017 | Conforming | Pass | — |
| RQA-FR-018 | Necessary | Pass | — |
| RQA-FR-018 | Appropriate | Pass | — |
| RQA-FR-018 | Unambiguous | Pass | — |
| RQA-FR-018 | Complete | Pass | — |
| RQA-FR-018 | Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-018 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-A owns an open **mechanism** question (whether RQA itself performs the code modification this row's authority bounds) this row's full satisfaction is contingent on — see requirements-specification.md § Set-level assessment's Consistent row. |
| RQA-FR-018 | Verifiable | Pass | — |
| RQA-FR-018 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds under every option of ADR-A; ADR-A decides whether RQA itself performs the code modification, not whether this row's own obligation is agreed. |
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
| RQA-FR-025 | Unambiguous | Pass | — |
| RQA-FR-025 | Complete | Pass | — |
| RQA-FR-025 | Singular | Pass | One dominant obligation; CL-040 was split across RQA-FR-025, RQA-FR-026, RQA-FR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-025 | Feasible | Pass | — |
| RQA-FR-025 | Verifiable | Pass | — |
| RQA-FR-025 | Correct | Pass | — |
| RQA-FR-025 | Conforming | Pass | — |
| RQA-FR-026 | Necessary | Pass | — |
| RQA-FR-026 | Appropriate | Pass | — |
| RQA-FR-026 | Unambiguous | Pass | — |
| RQA-FR-026 | Complete | Pass | — |
| RQA-FR-026 | Singular | Pass | One dominant obligation; CL-040 was split across RQA-FR-025, RQA-FR-026, RQA-FR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-026 | Feasible | Pass | — |
| RQA-FR-026 | Verifiable | Pass | — |
| RQA-FR-026 | Correct | Pass | — |
| RQA-FR-026 | Conforming | Pass | — |
| RQA-FR-027 | Necessary | Pass | — |
| RQA-FR-027 | Appropriate | Pass | — |
| RQA-FR-027 | Unambiguous | Pass | — |
| RQA-FR-027 | Complete | Pass | — |
| RQA-FR-027 | Singular | Pass | One dominant obligation; CL-040 was split across RQA-FR-025, RQA-FR-026, RQA-FR-027 — see requirements-specification.md § Singular-split record for how the split was drawn. |
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
| RQA-FR-029 | Singular | Pass | Round 3: rewritten as a single normative biconditional ('shall merge... if and only if...') carrying exactly one `shall` — the two-branch phrasing a prior draft used ('...shall merge...; ...it shall not') is replaced, closing the two-independently-falsifiable-`shall`s gap adversarial review found. |
| RQA-FR-029 | Feasible | Pass | — |
| RQA-FR-029 | Verifiable | Pass | — |
| RQA-FR-029 | Correct | Pass | — |
| RQA-FR-029 | Conforming | Pass | — |
| RQA-FR-030 | Necessary | Pass | — |
| RQA-FR-030 | Appropriate | Pass | See RQA-NFR-002's Appropriate basis for the Could/Must boundary between the two rows describing the same integration path. |
| RQA-FR-030 | Unambiguous | Pass | — |
| RQA-FR-030 | Complete | Pass | — |
| RQA-FR-030 | Singular | Pass | — |
| RQA-FR-030 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-C owns an open **design choice** (how an externally-supplied harness's self-reported identity is authenticated) this row's full satisfaction is contingent on — not a mechanism or feasibility question, and not a conflict: AC15 and forgeable-proof provenance are jointly satisfiable under every **source-conforming** option ADR-C lists (option 3 is explicitly marked as requiring a source amendment, not a conforming resolution) — see § Set-level assessment's Consistent row. |
| RQA-FR-030 | Verifiable | Pass | — |
| RQA-FR-030 | Correct | Pass | Reflects its own source clause's plain reading; ADR-C is an undecided design choice at the intersection of AC15 and Security bullet 4, not a textual inconsistency between them — see the reframed ADR-C draft. |
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
| RQA-FR-034 | Conforming | Pass | Names 'architectural component' — the closing criterion's and §6 rule's own vocabulary for what is being justified; no particular architecture is chosen. |
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
| RQA-FR-038 | Unambiguous | Pass | — |
| RQA-FR-038 | Complete | Pass | — |
| RQA-FR-038 | Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-038 | Feasible | Pass | — |
| RQA-FR-038 | Verifiable | Pass | — |
| RQA-FR-038 | Correct | Pass | — |
| RQA-FR-038 | Conforming | Pass | — |
| RQA-FR-039 | Necessary | Pass | — |
| RQA-FR-039 | Appropriate | Pass | — |
| RQA-FR-039 | Unambiguous | Pass | — |
| RQA-FR-039 | Complete | Pass | — |
| RQA-FR-039 | Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-FR-039 | Feasible | Pass | — |
| RQA-FR-039 | Verifiable | Pass | — |
| RQA-FR-039 | Correct | Pass | — |
| RQA-FR-039 | Conforming | Pass | — |

---

## Non-functional requirements (RQA-NFR-001…029)

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
| RQA-NFR-002 | Appropriate | Pass | Priced Could because C1's own text says a contributor 'may' use the thin integration path — using it is the contributor's option. This does not weaken RQA-FR-030 (Must): once a contributor exercises that option, the system's obligation to admit them via the published contract is unconditional, which is why FR-030 (the system-side support obligation) and NFR-002 (the contributor-side option to use it) carry different priorities for the same integration path. |
| RQA-NFR-002 | Unambiguous | Pass | — |
| RQA-NFR-002 | Complete | Pass | — |
| RQA-NFR-002 | Singular | Pass | One dominant obligation; CL-018 was split across RQA-NFR-001, RQA-NFR-002 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-002 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); #2064 owns the open question of where launchpad-repo policy/contract documents publish, named in requirements-specification.md § Provenance and pin — not a tension recorded in § Set-level assessment, which discusses only ADR-A/B/C. |
| RQA-NFR-002 | Verifiable | Pass | — |
| RQA-NFR-002 | Correct | Pass | — |
| RQA-NFR-002 | Conforming | Pass | Names 'skill, plugin or hook' — C1's own vocabulary for the optional integration path, not a mechanism chosen by this specification. |
| RQA-NFR-003 | Necessary | Pass | — |
| RQA-NFR-003 | Appropriate | Pass | — |
| RQA-NFR-003 | Unambiguous | Caveat | 'Where practical' is C2's own qualifier; #2006 does not state what makes a case impractical. The fit criterion requires a recorded, specific, evidenced reason rather than accepting a bare unsubstantiated excuse, narrowing (without eliminating) the residual ambiguity — what counts as sufficiently 'evidenced' is still not defined by #2006, and none is invented here. |
| RQA-NFR-003 | Complete | Pass | — |
| RQA-NFR-003 | Singular | Pass | — |
| RQA-NFR-003 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); #2064 owns the open question of where launchpad-repo policy/contract documents publish, named in requirements-specification.md § Provenance and pin — not a tension recorded in § Set-level assessment, which discusses only ADR-A/B/C. |
| RQA-NFR-003 | Verifiable | Pass | — |
| RQA-NFR-003 | Correct | Pass | — |
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
| RQA-NFR-007 | Unambiguous | Pass | — |
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
| RQA-NFR-011 | Unambiguous | Caveat | Reworded from a prohibition ('shall operate exclusively') to the scope-release form C8/Non-goal 1 actually state ('is not required' / 'out of scope'). This is a recorded interpretive choice, not the only possible reading — 'GitHub only' in C8 tolerably supports a stronger exclusive reading too — and the fit criterion now tests only the weaker scope reading this row's statement adopts, not exclusivity. |
| RQA-NFR-011 | Complete | Pass | — |
| RQA-NFR-011 | Singular | Pass | — |
| RQA-NFR-011 | Feasible | Pass | — |
| RQA-NFR-011 | Verifiable | Pass | — |
| RQA-NFR-011 | Correct | Pass | Reflects the scope-release reading of C8/CL-025 and Non-goal 1/CL-047 ('not required', 'out of scope') rather than the stronger exclusivity reading also arguable from 'GitHub only' — see this row's Unambiguous basis for the recorded choice between the two. |
| RQA-NFR-011 | Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-025 (C8) is itself stated in those terms. |
| RQA-NFR-012 | Necessary | Pass | — |
| RQA-NFR-012 | Appropriate | Pass | — |
| RQA-NFR-012 | Unambiguous | Pass | — |
| RQA-NFR-012 | Complete | Pass | — |
| RQA-NFR-012 | Singular | Pass | One dominant obligation; CL-026 was split across RQA-NFR-012, RQA-NFR-013 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-012 | Feasible | Pass | — |
| RQA-NFR-012 | Verifiable | Pass | — |
| RQA-NFR-012 | Correct | Pass | — |
| RQA-NFR-012 | Conforming | Pass | — |
| RQA-NFR-013 | Necessary | Pass | — |
| RQA-NFR-013 | Appropriate | Pass | — |
| RQA-NFR-013 | Unambiguous | Caveat | 'Appropriate to sensitivity' is C9's own qualifier; #2006 does not define a sensitivity scale, and none is invented here. |
| RQA-NFR-013 | Complete | Pass | — |
| RQA-NFR-013 | Singular | Pass | One dominant obligation; CL-026 was split across RQA-NFR-012, RQA-NFR-013 — see requirements-specification.md § Singular-split record for how the split was drawn. |
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
| RQA-NFR-019 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-A owns an open **mechanism** question (whether RQA itself performs the code modification this row's authority bounds) this row's full satisfaction is contingent on — see requirements-specification.md § Set-level assessment's Consistent row. |
| RQA-NFR-019 | Verifiable | Pass | — |
| RQA-NFR-019 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds under every option of ADR-A; ADR-A decides whether RQA itself performs the code modification, not whether this row's own obligation is agreed. |
| RQA-NFR-019 | Conforming | Pass | — |
| RQA-NFR-020 | Necessary | Pass | — |
| RQA-NFR-020 | Appropriate | Pass | — |
| RQA-NFR-020 | Unambiguous | Pass | — |
| RQA-NFR-020 | Complete | Pass | — |
| RQA-NFR-020 | Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-020 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-A owns an open **mechanism** question (whether RQA itself performs the code modification this row's authority bounds) this row's full satisfaction is contingent on — see requirements-specification.md § Set-level assessment's Consistent row. |
| RQA-NFR-020 | Verifiable | Pass | — |
| RQA-NFR-020 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds under every option of ADR-A; ADR-A decides whether RQA itself performs the code modification, not whether this row's own obligation is agreed. |
| RQA-NFR-020 | Conforming | Pass | Names 'working tree' — CL-057's own term for the isolation boundary, not a chosen isolation mechanism (the fit criterion deliberately does not name one). |
| RQA-NFR-021 | Necessary | Pass | — |
| RQA-NFR-021 | Appropriate | Pass | — |
| RQA-NFR-021 | Unambiguous | Pass | — |
| RQA-NFR-021 | Complete | Pass | — |
| RQA-NFR-021 | Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-021 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-A owns an open **mechanism** question (whether RQA itself performs the code modification this row's authority bounds) this row's full satisfaction is contingent on — see requirements-specification.md § Set-level assessment's Consistent row. |
| RQA-NFR-021 | Verifiable | Pass | — |
| RQA-NFR-021 | Correct | Pass | Reflects AC09's plain-reading obligation, which holds under every option of ADR-A; ADR-A decides whether RQA itself performs the code modification, not whether this row's own obligation is agreed. |
| RQA-NFR-021 | Conforming | Pass | Names 'force-push', 'merge', 'branch protection' and 'protected branch' — CL-057's own enumerated prohibitions, carried verbatim. |
| RQA-NFR-022 | Necessary | Pass | — |
| RQA-NFR-022 | Appropriate | Pass | — |
| RQA-NFR-022 | Unambiguous | Pass | — |
| RQA-NFR-022 | Complete | Pass | — |
| RQA-NFR-022 | Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-022 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-C owns an open **design choice** (how an externally-supplied harness's self-reported identity is authenticated) this row's full satisfaction is contingent on — not a mechanism or feasibility question, and not a conflict: AC15 and forgeable-proof provenance are jointly satisfiable under every **source-conforming** option ADR-C lists (option 3 is explicitly marked as requiring a source amendment, not a conforming resolution) — see § Set-level assessment's Consistent row. |
| RQA-NFR-022 | Verifiable | Pass | — |
| RQA-NFR-022 | Correct | Pass | Reflects its own source clause's plain reading; ADR-C is an undecided design choice at the intersection of AC15 and Security bullet 4, not a textual inconsistency between them — see the reframed ADR-C draft. |
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
| RQA-NFR-024 | Unambiguous | Pass | — |
| RQA-NFR-024 | Complete | Pass | — |
| RQA-NFR-024 | Singular | Pass | One dominant obligation; CL-060 was split across RQA-NFR-024, RQA-NFR-025 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-024 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-B owns an open, **externally-contingent feasibility** question (whether the enumerated credential scope admits the merge/push actions elsewhere required, given GitHub's own permission model — a premise the extract never states) this row's full satisfaction is contingent on — see § Set-level assessment's Consistent row. |
| RQA-NFR-024 | Verifiable | Pass | — |
| RQA-NFR-024 | Correct | Pass | Reflects the Security implications section's plain-reading credential-scope statement, now stating both the floor and the ceiling (round 3) rather than only a ceiling that under-carried CL-060; ADR-B (reframed) asks whether that scope is feasible given GitHub's external permission model, not whether the scope statement itself is agreed. |
| RQA-NFR-024 | Conforming | Pass | Names 'pull-request write' and 'repository-content read' — the Security implications section's own credential-scope vocabulary, carried verbatim rather than translated into a platform-specific permission name. |
| RQA-NFR-025 | Necessary | Pass | — |
| RQA-NFR-025 | Appropriate | Pass | — |
| RQA-NFR-025 | Unambiguous | Pass | — |
| RQA-NFR-025 | Complete | Pass | — |
| RQA-NFR-025 | Singular | Pass | One dominant obligation; CL-060 was split across RQA-NFR-024, RQA-NFR-025 — see requirements-specification.md § Singular-split record for how the split was drawn. |
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
| RQA-NFR-027 | Correct | Caveat | Round 3: re-derived from CL-024/C7 ('Alternative models/providers only when explicitly configured') rather than CL-026/C9, after adversarial review showed C9's permissive 'may be sent... when explicitly configured' does not itself entail a prohibition on sending when unconfigured. C7's own configuration-gating principle is applied here to the specific act of sending review content to an external provider, reconciled against RQA-NFR-009 (which governs provider/model *selection*) as a distinct axis (content *transmission*) of the same 'only when explicitly configured' principle — see § Singular-split record's CL-024 entry. This is a defensible extension of C7's principle, not C7's own literal text (C7 does not itself name 'code, diffs, metadata and evidence'), and is recorded as such rather than asserted as a bare, uncaveated derivation. |
| RQA-NFR-027 | Conforming | Pass | — |
| RQA-NFR-028 | Necessary | Pass | — |
| RQA-NFR-028 | Appropriate | Pass | — |
| RQA-NFR-028 | Unambiguous | Pass | — |
| RQA-NFR-028 | Complete | Pass | — |
| RQA-NFR-028 | Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028 — see requirements-specification.md § Singular-split record for how the split was drawn. |
| RQA-NFR-028 | Feasible | Caveat | The obligation itself is agreed (status DECIDED); ADR-C owns an open **design choice** (how an externally-supplied harness's self-reported identity is authenticated) this row's full satisfaction is contingent on — not a mechanism or feasibility question, and not a conflict: AC15 and forgeable-proof provenance are jointly satisfiable under every **source-conforming** option ADR-C lists (option 3 is explicitly marked as requiring a source amendment, not a conforming resolution) — see § Set-level assessment's Consistent row. |
| RQA-NFR-028 | Verifiable | Pass | — |
| RQA-NFR-028 | Correct | Pass | Reflects its own source clause's plain reading; ADR-C is an undecided design choice at the intersection of AC15 and Security bullet 4, not a textual inconsistency between them — see the reframed ADR-C draft. |
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

---

## Summary

- 738 judgements recorded across 82 requirements and 9 characteristics.
- Every judgement is `Pass` except the deliberate `Caveat`s below, none of which mark a requirement as failing —
  each records a qualification the requirement inherits from #2006's own text, from an open ADR/#2064 question,
  or (RQA-NFR-027 alone) from a defensible-but-non-literal derivation step, rather than from a defect introduced
  in derivation:
  - **Feasible caveats**, differentiated by which open question they name: mechanism-open under `ADR-A`
    (RQA-FR-017, RQA-FR-018, RQA-NFR-019, RQA-NFR-020, RQA-NFR-021); externally-contingent feasibility under
    `ADR-B` (RQA-NFR-024); design-choice-open under `ADR-C` (RQA-FR-030, RQA-NFR-022, RQA-NFR-028) — each of
    these three now says "every **source-conforming** option", not "every option"; and publication-location-open
    under `#2064` (RQA-FR-001, RQA-NFR-002, RQA-NFR-003).
  - **Unambiguous caveats**: RQA-BR-001, RQA-BR-006 (new round 3 — inherited P5 conjunction ambiguity), RQA-BR-010,
    RQA-FR-034, RQA-NFR-003, RQA-NFR-011, RQA-NFR-013.
  - **Correct caveat**: RQA-NFR-027 (new round 3 — records its re-derivation from CL-024 rather than CL-026 as a
    defensible extension of C7's principle, not C7's own literal text).
- Corrected across rounds 1–2: six `Singular` verdicts split into new rows; twenty-five `Verifiable` verdicts
  whose fit criteria were rewritten; the `Conforming` basis for every GitHub/source-vocabulary row; the
  `Necessary`/`Correct` bases for RQA-BR-005 (jointly derived from CL-009 and the re-dispositioned CL-002).
- Corrected round 3: `Verifiable` for RQA-NFR-022/RQA-NFR-028 (whole authoritative provenance record, not four
  fields) and RQA-NFR-019/020/021 (effective authority, not benign run history) — both genuine blockers a prior
  round's fit criteria would have let pass; `Singular` for RQA-FR-029 (now a true single-`shall` biconditional,
  not a defended two-`shall` non-split); `Correct` for RQA-NFR-027 (Pass → Caveat, recording its re-derivation);
  `Feasible` wording for every ADR-C row ("every option" → "every source-conforming option"); `Conforming` for
  RQA-FR-034 ("component" → "architectural component"); and a new `Unambiguous` caveat for RQA-BR-006.
