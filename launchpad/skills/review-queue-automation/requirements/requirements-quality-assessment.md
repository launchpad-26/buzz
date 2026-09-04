# RQA requirements quality assessment

Per-requirement assessment of every requirement in
[`requirements-specification.md`](requirements-specification.md) against the nine individual requirement
characteristics named in [launchpad-26/buzz#2069](https://github.com/launchpad-26/buzz/issues/2069)'s definition
of done: **necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming.**

## How to read this

One heading per requirement, nine judgements each — 84 × 9 = 756 recorded judgements in total. Each judgement
is `Pass` or `Caveat`. A `Caveat` never means the requirement fails; it means the judgement is not unqualified,
and the qualification is written out rather than smoothed over. Basis is `—` where the judgement follows
directly from reading the requirement against its source clause and fit criterion; a one-line basis is given
wherever the judgement takes a position a reader could reasonably have called differently.

**What each characteristic asks of a requirement:**

| Characteristic | Question |
|---|---|
| Necessary | Would #2006's baseline be under-specified if this requirement were deleted? |
| Appropriate | Is this stated at the right level (business / functional / non-functional) for its source clause? |
| Unambiguous | Does the statement admit only one reading, or does it carry an undefined qualifier from the source? |
| Complete | Does the statement, together with its fit criterion, state the whole of its own obligation? |
| Singular | Does the statement carry exactly one dominant obligation? |
| Feasible | Is satisfying the requirement achievable given #2006's own constraints, or contingent on an open choice? |
| Verifiable | Does the fit criterion give an observable, checkable condition that cannot pass without demonstrating the requirement? |
| Correct | Does the statement accurately reflect its cited source clause's plain reading? |
| Conforming | Does the statement name no mechanism, component, product or technology beyond source-mandated vocabulary? |

---

### RQA-BR-001

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Consistent, auditable, efficient, trustworthy' are the problem statement's own words, each given an operational reading only in the fit criterion, not redefined in the requirement statement itself. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Caveat | Verified only transitively, by construction: RQA-BR-001's fit criterion defers entirely to the source-derived obligations already in the set (consistency→BR-002, auditability→FR-012/NFR-022/NFR-028, efficiency→FR-019/FR-020/FR-021, trustworthiness→FR-011/FR-013 and the no-manufactured-success rows). Deleting BR-001 would fail no single check, because its evidence is the conjunction of other rows; this is the accepted shape of an umbrella clause (CL-001 still needs a disposition), and it is recorded here so the transitive-by-construction nature is explicit rather than silently passed. |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-002

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P1's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-003

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P2's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-004

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P3's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-005

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | CL-002's distinct 'creation-time' framing (see its inventory note) is not captured by P4/CL-009 alone or by any other requirement; deleting the 'creation-time' branch of this row would leave that framing uncarried. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reworded to a distinguishability obligation, reflecting both cited clauses' plain readings without implying a separate-blocking-mechanism reading that would conflict with C6/AC14. |
| Conforming | Pass | — |

### RQA-BR-006

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P5's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Shall not require a further contributor and a further review cycle' inherits P5's own conjunction from the source ('the fix still needs another contributor and another review cycle') without resolving whether the prohibition reads as ¬(A∧B) — not both together — or ¬A∧¬B — neither at all; #2006 does not disambiguate the conjunction. Round 7: the fit criterion now tests only the weaker ¬(A∧B) reading (correcting a prior criterion that silently operationalised the stronger ¬A∧¬B reading), but the underlying source ambiguity is unresolved and this caveat continues to record it rather than treat the chosen reading as the only one #2006 admits. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Caveat | Round 7: the fit criterion now tests only ¬(A∧B) — the combination is not required — correcting a prior criterion that operationalised the stronger ¬A∧¬B reading and would have rejected a system needing one further contributor action alone. The underlying source ambiguity (see this row's Unambiguous caveat) is recorded, not resolved: this criterion picks the weaker, source-permitted reading rather than claiming #2006 forces it. |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-007

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P6's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-008

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P7's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-009

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P8's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-010

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P9's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Genuinely requires human judgement' synthesises P9/CL-014's own framing with P12/CL-017's and AC13/CL-040's (cited as joint source clauses since round 6); #2006 does not itself define the line between genuine and non-genuine judgement even across all three clauses, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation ('progression shall not depend on manual intervention beyond genuine judgement'); citing three source clauses (CL-014, CL-017, CL-040) jointly informs that single obligation's qualifier rather than adding a second obligation — see [singular-splits.md](singular-splits.md)'s CL-017/CL-040 entries. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-011

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P10's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-012

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P11's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Efficiently' is the problem statement's own word (paraphrasing P11); #2006 does not define an efficiency threshold, and none is invented here — the fit criterion's policy-comparison reading is this specification's own operationalisation, not a definition #2006 supplies. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-013

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-BR-001's synthesis: states P12's own specific, independently testable obligation. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Routine, mechanical or non-urgent' is AC13's own vocabulary (P12's framing), undefined there — the same unresolved boundary already caveated on RQA-FR-025's sibling row; #2006 does not state it, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-017 was split across RQA-BR-010, RQA-BR-013 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-BR-014

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Important risks, claims and evidence' inherits the problem statement's own qualifier ('the important risks, claims, and evidence associated with a pull request'); #2006 does not define which risks/claims/evidence count as important, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-001

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-028 was split across RQA-FR-001, RQA-FR-002 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects AC01's plain reading; #2064 owns where this specification (and by extension the published protocol definition it requires) is placed, not whether the obligation itself is agreed — a placement question, not a feasibility one. |
| Conforming | Pass | — |

### RQA-FR-002

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-028 was split across RQA-FR-001, RQA-FR-002 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-003

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-029 was split across RQA-FR-003, RQA-FR-004 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-004

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-029 was split across RQA-FR-003, RQA-FR-004 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-005

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Nothing material' is AC03's own undefined qualifier, and 'material' is not defined anywhere in #2006; what counts as a materially-immaterial change is left to the same undefined boundary already caveated on RQA-FR-034's 'materially serves'/'materially simpler'. This specification does not invent a definition, and this row's fit criterion tests only the observable consequence (zero reviewer invocations), not the boundary itself. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-030 was split across RQA-FR-005, RQA-FR-006, RQA-FR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Caveat | The fit criterion introduces an audit-apparatus element beyond AC03: it requires the zero-reinvocation observation to be 'independently corroborated' (a boundary trace, an audited invocation log, or an equivalent), where AC03 itself imposes nothing about how the zero is observed. This is a verification-hygiene choice, not a source-scope widening of the obligation itself; recorded here rather than weakening the criterion, because an independently checkable observation is the one reading that makes the row's own fit criterion answerable by someone who did not write it. |

### RQA-FR-006

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | The set of obligations a push 'invalidates' depends on the same undefined 'material' boundary RQA-FR-005's Unambiguous caveat records; #2006 does not itself state how invalidation is determined for a given file change, and none is invented here — the fit criterion tests set equality with whatever that determination produces, not the determination itself. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-030 was split across RQA-FR-005, RQA-FR-006, RQA-FR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-007

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-030 was split across RQA-FR-005, RQA-FR-006, RQA-FR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-008

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-031 was split across RQA-FR-008, RQA-FR-009 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-009

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-031 was split across RQA-FR-008, RQA-FR-009 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-010

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-032 was split across RQA-FR-010, RQA-FR-011 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-011

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-032 was split across RQA-FR-010, RQA-FR-011 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-012

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-033 was split across RQA-FR-012, RQA-FR-013 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names 'a single command' — AC06's own vocabulary for the reconstruction interface; no particular command, tool or format is chosen. |

### RQA-FR-013

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-033 was split across RQA-FR-012, RQA-FR-013 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-014

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-034 was split across RQA-FR-014, RQA-FR-015, RQA-FR-036 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-015

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-034 was split across RQA-FR-014, RQA-FR-015, RQA-FR-036 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-016

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-035 was split across RQA-FR-016, RQA-NFR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names 'one command' — AC08's own vocabulary for the query interface; no particular command, tool or format is chosen. |

### RQA-FR-017

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Unnecessarily' is AC09's own qualifier ('without unnecessarily creating human intervention'); #2006 does not define which human intervention is necessary versus unnecessary for a given mechanical finding, and none is invented here — round 6/7's necessity carve-out defers to repository policy where policy speaks, but does not itself define the boundary #2006 leaves open. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects AC09's plain-reading obligation. The 2026-09-04 amendment confirms directly that RQA itself may apply and push a deterministic, non-behavioural fix under this obligation — previously an open design question (draft ADR-A), now the source's own stated position. |
| Conforming | Pass | — |

### RQA-FR-018

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects AC09's plain-reading obligation. The 2026-09-04 amendment confirms directly that RQA itself may apply and push a deterministic, non-behavioural fix under this obligation — previously an open design question (draft ADR-A), now the source's own stated position. |
| Conforming | Pass | — |

### RQA-FR-019

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-037 was split across RQA-FR-019, RQA-FR-020 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-020

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-037 was split across RQA-FR-019, RQA-FR-020 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-021

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-022

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-023

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038, RQA-NFR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-024

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038, RQA-NFR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-025

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Routine, mechanical or non-urgent' is AC13's own vocabulary, undefined there; #2006 does not state the boundary between a routine/mechanical/non-urgent condition and one requiring escalation, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-040 was split across RQA-BR-010, RQA-FR-025, RQA-FR-026, RQA-FR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-026

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-040 was split across RQA-BR-010, RQA-FR-025, RQA-FR-026, RQA-FR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-027

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-040 was split across RQA-BR-010, RQA-FR-025, RQA-FR-026, RQA-FR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-028

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-041 was split across RQA-FR-028, RQA-FR-029, RQA-FR-037 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-041 (AC14) is itself stated in those terms. |

### RQA-FR-029

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | Rewritten as a single normative biconditional ('shall merge... if and only if...') carrying exactly one `shall` — a prior two-branch phrasing carried two independently falsifiable `shall`s, which adversarial review found. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-030

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | See RQA-NFR-002's Appropriate basis for the boundary between the two rows: this row concerns any non-built-in harness's admission generally (Must, AC15); RQA-NFR-002 concerns a contributor's optional choice to use a specific conforming integration form (Could, C1's 'may'). |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects its own source clause's plain reading. The 2026-09-04 amendment resolves what was an undecided design choice at the intersection of AC15 and Security bullet 4 (draft ADR-C): provenance is now stated to be written by RQA itself, never by reviewed content or model output, so a harness's self-reported identity is input RQA acts on, not an authoritative write of its own — resolved at the source, not by this specification. |
| Conforming | Pass | — |

### RQA-FR-031

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-043 (AC16) is itself stated in those terms. |

### RQA-FR-032

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-044 was split across RQA-FR-032, RQA-FR-033 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-033

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-044 was split across RQA-FR-032, RQA-FR-033 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-034

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Materially serves' / 'materially simpler' are the source's own qualifiers (§6 rule, closing criterion 1); #2006 does not define a threshold, and none is invented here. Separately, the source's own 'or' between the three grounds admits a literal disjunctive reading under which a component with a materially simpler alternative remains retainable merely for serving a criterion; this specification carries that ambiguity rather than resolving it by silently converting the source's 'or' into an 'and'. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names 'architectural component' — the closing criterion's own vocabulary for what is being justified; no particular architecture is chosen. |

### RQA-FR-035

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names issue numbers #109, #535, #536 verbatim from the source closing criterion (CL-046); these are issue-tracker references the source itself supplies, not a named mechanism, component, product or technology. |

### RQA-FR-036

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-034 was split across RQA-FR-014, RQA-FR-015, RQA-FR-036 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-037

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-041 was split across RQA-FR-028, RQA-FR-029, RQA-FR-037 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-038

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Safe' is CL-039's own word, used without enumeration; this specification's fit criterion tests the most complete, explicitly-bounded set of source-derived standing security invariants available (see this row's Verifiable caveat) but cannot claim that set exhausts what #2006 means by 'safe', and none beyond that closed, justified set is invented here. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-039 was split across RQA-FR-023, RQA-FR-024, RQA-FR-038, RQA-NFR-007 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Caveat | CL-039 uses 'safe' without enumerating what safety consists of. Round 7: the fit criterion tests every standing security invariant this specification states, with the excluded rows (RQA-NFR-015/016/017/026/023/027/029) each given a stated reason (ongoing-conduct or configuration-setting properties, not a resting-state property) rather than silently omitted; this is the most complete, explicitly-bounded set available from the extract, but cannot rule out a safety property #2006 gestures at without stating. |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-FR-039

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | AC11's 'a configured bound... produces a configured fallback' is read as the fallback becoming the run's terminal outcome (matching RQA-FR-022's 'ends in one of the three named outcomes'), not as the run continuing to a successful disposition through the fallback (the reading AC12's parallel 'continues through an explicitly configured fallback' could support by analogy). The 'produces' / 'continues through' wording contrast is this row's basis for the reading chosen; #2006 does not disambiguate the two readings for AC11 specifically, and this specification records the choice rather than treating it as the only possible one. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-038 was split across RQA-FR-021, RQA-FR-022, RQA-FR-039 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-001

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-018 was split across RQA-NFR-001, RQA-NFR-002 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-002

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | Priced Could because C1's own text says a contributor 'may' use a thin skill/plugin/hook — using one is the contributor's option; the system's obligation to accommodate that choice, once made, is unconditional, which is why this row (the contributor-side option) and RQA-FR-030 (the system-side obligation to admit a non-built-in harness generally) carry different priorities without duplicating each other's subject matter. |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-018 was split across RQA-NFR-001, RQA-NFR-002 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Restated so the system's obligation is to accommodate participation through the published contract, not to implement acceptance of three named mechanism forms specifically; #2064's placement question does not bear on whether this obligation is agreed. |
| Conforming | Pass | Names 'skill, plugin or hook' — C1's own vocabulary for the optional integration path, not a mechanism chosen by this specification. |

### RQA-NFR-003

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Where practical' is C2's own qualifier; #2006 does not state what makes a case impractical. The fit criterion now evaluates the contract and the format separately, each requiring all three named qualities conjunctively or an independently verified, specific, evidenced impracticality reason, narrowing (without eliminating) the residual ambiguity — what counts as sufficiently 'evidenced' is still not defined by #2006, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects C2's plain reading, conjunctively per artifact; #2064's placement question does not bear on whether this obligation is agreed. |
| Conforming | Pass | — |

### RQA-NFR-004

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-005

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-006

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-007

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Whenever progression remains possible' is imported from AC08/CL-035's 'unable to progress' disposition and AC12/CL-039's mandated safe stop, not stated by C6/CL-023 itself; the harmonisation is necessary (a literal reading of C6 alone would contradict AC12's mandated stop and AC08's disposition, both baseline acceptance criteria in the same extract). Round 7: CL-035 and CL-039 are now cited as joint source clauses for this qualifier (previously only admitted here, not encoded as reference-graph edges), matching the fix already applied to RQA-BR-010 in round 6; #2006 still does not itself define where 'possible' stops, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation ('the system shall manage every lifecycle step through to an authoritative outcome whenever progression remains possible'); citing three source clauses (CL-023, CL-035, CL-039 — round 7) jointly informs that single obligation's qualifier rather than adding a second obligation. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-023 (C6, AC08, AC12) is itself stated in those terms. |

### RQA-NFR-008

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-023 was split across RQA-NFR-007, RQA-NFR-008 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-009

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-024 was split across RQA-NFR-009, RQA-NFR-010, RQA-NFR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-010

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-024 was split across RQA-NFR-009, RQA-NFR-010, RQA-NFR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-011

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names GitHub / its review-state vocabulary under the Methodology's deliberate exception: CL-025 (C8) is itself stated in those terms. |

### RQA-NFR-012

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-026 was split across RQA-NFR-012, RQA-NFR-013, RQA-NFR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-013

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Appropriate to sensitivity' is C9's own qualifier; #2006 does not define a sensitivity scale, and none is invented here. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-026 was split across RQA-NFR-012, RQA-NFR-013, RQA-NFR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-014

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-015

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-055 was split across RQA-NFR-015, RQA-NFR-016 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-016

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-055 was split across RQA-NFR-015, RQA-NFR-016 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-017

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-056 was split across RQA-NFR-017, RQA-NFR-018, RQA-NFR-024, RQA-NFR-026, RQA-NFR-030 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-018

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-056 was split across RQA-NFR-017, RQA-NFR-018, RQA-NFR-024, RQA-NFR-026, RQA-NFR-030 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-019

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. The 2026-09-04 amendment confirms remediation authority to modify and push code for mechanical findings is now source-granted (previously an open design question, draft ADR-A) — this bound is therefore a currently live, binding constraint on an exercised authority, not a pre-emptive one held in reserve against a future grant. |
| Conforming | Pass | — |

### RQA-NFR-020

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. The 2026-09-04 amendment confirms remediation authority to modify and push code for mechanical findings is now source-granted (previously an open design question, draft ADR-A) — this bound is therefore a currently live, binding constraint on an exercised authority, not a pre-emptive one held in reserve against a future grant. |
| Conforming | Pass | Names 'working tree' — CL-057's own term for the isolation boundary, not a chosen isolation mechanism (the fit criterion deliberately does not name one). |

### RQA-NFR-021

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. The 2026-09-04 amendment confirms remediation authority to modify and push code for mechanical findings is now source-granted (previously an open design question, draft ADR-A) — this bound is therefore a currently live, binding constraint on an exercised authority, not a pre-emptive one held in reserve against a future grant. |
| Conforming | Pass | Names 'force-push', 'merge', 'branch protection' and 'protected branch' — CL-057's own enumerated prohibitions, carried verbatim. |

### RQA-NFR-022

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects its own source clause's plain reading. The 2026-09-04 amendment resolves what was an undecided design choice at the intersection of AC15 and Security bullet 4 (draft ADR-C): provenance is now stated to be written by RQA itself, never by reviewed content or model output, so a harness's self-reported identity is input RQA acts on, not an authoritative write of its own — resolved at the source, not by this specification. |
| Conforming | Pass | — |

### RQA-NFR-023

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-059 was split across RQA-NFR-023, RQA-NFR-029 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-024

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | The 2026-09-04 amendment states the activity-conditioned floor directly in CL-060's own text; what was previously an interpretive reading (see this row's Correct basis) is now the source's own explicit statement. |
| Complete | Pass | — |
| Singular | Pass | Round 7: now floor-only — a single obligation conditioned on one configuration ('carry X on repositories configured for authoritative outcomes'). The activity-relative ceiling a prior draft joined to this row with a semicolon (breaking singularity, since it was independently falsifiable from the floor) moved to RQA-NFR-030 — see [singular-splits.md](singular-splits.md)'s CL-060 entry. |
| Feasible | Pass | The 2026-09-04 amendment resolves what draft ADR-B owned: the credential scope is no longer a fixed enumeration asserted to somehow suffice for merge/push; the amended CL-060 states the scope grows to cover whatever a repository's configured activity requires, self-adjusting rather than resting on an external premise about GitHub's permission model. |
| Verifiable | Pass | — |
| Correct | Pass | The 2026-09-04 amendment states this floor's activity-conditioning directly: “where a repository's policy additionally grants remediation push or merge-after-review, the token for that repository additionally carries the write scope those operations require, and no more — repositories configured for advisory-only review carry no write scope beyond pull-requests.” What round 7 recorded as an interpretive choice (reading CL-060's floor as conditioned on configured activity, via CL-056's least-privilege principle) is now CL-060's own literal wording; no second ADR is needed because there is no longer a reading to choose between. |
| Conforming | Pass | Names 'pull-request write' and 'repository-content read' — the Security implications section's own credential-scope vocabulary (CL-060 says 'pull-requests write and contents read'), carried in lightly normalised form, not translated into a platform-specific permission name. |

### RQA-NFR-025

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-060 was split across RQA-NFR-024, RQA-NFR-025, RQA-NFR-030 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | Names 'deploy-key', 'relay' and 'VPS' — the Security implications section's own enumerated exclusions, carried verbatim. |

### RQA-NFR-026

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-056 was split across RQA-NFR-017, RQA-NFR-018, RQA-NFR-024, RQA-NFR-026, RQA-NFR-030 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-027

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-024 was split across RQA-NFR-009, RQA-NFR-010, RQA-NFR-027 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Caveat | Derivation is conjunctive — cited from both CL-024 and CL-026, not a single clause. C7's 'only when explicitly configured' configuration-gating principle is applied to C9's own named content types (code, diffs, metadata, evidence) and C9's own permitted act (sending to an external provider); neither clause alone states this prohibition, but read together they entail it. This is an inferential step across two clauses, not a quotation from either, and is recorded as such rather than asserted as a single-clause literal derivation. |
| Conforming | Pass | — |

### RQA-NFR-028

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Caveat | Round 7: 'forgeable-proof' is read at the authority/acceptance boundary (an unauthorised alteration must be detectable and refused as authoritative, not physically impossible to make) rather than as literal storage immutability; CL-058's own text does not state which of the two readings is intended, and this specification records the interpretive choice rather than treating the stronger, immutability reading as the only one available. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects its own source clause's plain reading. The 2026-09-04 amendment resolves what was an undecided design choice at the intersection of AC15 and Security bullet 4 (draft ADR-C): provenance is now stated to be written by RQA itself, never by reviewed content or model output, so a harness's self-reported identity is input RQA acts on, not an authoritative write of its own — resolved at the source, not by this specification. |
| Conforming | Pass | — |

### RQA-NFR-029

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | — |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-059 was split across RQA-NFR-023, RQA-NFR-029 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | — |
| Conforming | Pass | — |

### RQA-NFR-030

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | The 2026-09-04 amendment states the activity-relative ceiling directly in CL-060's own text (see this row's Correct basis); what round 7 recorded as an interpretive reading is now the source's own explicit statement. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation ('the credential's permissions shall never exceed what type, repository-scope and configured activity allow'), tested across three ceiling dimensions the way RQA-NFR-021 tests four never-actions in one row — each dimension is a facet of the same upper-bound obligation, not an independent obligation on a different subject. |
| Feasible | Pass | The 2026-09-04 amendment resolves what draft ADR-B owned: the credential scope is no longer a fixed enumeration asserted to somehow suffice for merge/push; the amended CL-060 states the scope grows to cover whatever a repository's configured activity requires, self-adjusting rather than resting on an external premise about GitHub's permission model. |
| Verifiable | Pass | — |
| Correct | Pass | CL-060 now states the activity-relative ceiling directly: a repository's additional write scope is capped to “the write scope those operations require, and no more,” and an advisory-only repository “carries no write scope beyond pull-requests.” What round 7 read in from CL-056's least-privilege principle (see RQA-NFR-024's Correct basis) is now CL-060's own literal wording for all three ceiling dimensions (type, repository-scope, activity-relative). |
| Conforming | Pass | Names 'pull-request write' and 'repository-content read' — the same lightly-normalised credential-scope vocabulary as RQA-NFR-024. |

### RQA-NFR-031

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Distinct from RQA-NFR-019: that row bounds authority to whatever categories policy names as mechanical, but does not itself bound what policy may name as mechanical — this row states the ceiling on the category itself, a load-bearing obligation the amendment adds that no existing row carried. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | 'Behaviour' and 'behavioural' are the amended source's own undefined terms (CL-036/CL-057 use them without further definition, mirroring the deterministic/non-behavioural distinction AC09 itself draws); this specification does not invent a boundary #2006 leaves open, and the fit criterion tests the classification outcome, not the definition of 'behaviour' itself. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation, jointly cited from CL-036 and CL-057 — both amended clauses state the same ceiling from opposite sides (AC09's own grant, and the Security section's authority description); see [singular-splits.md](singular-splits.md)'s CL-036 and CL-057 entries for how the joint citation was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects both cited clauses' plain reading directly; the 2026-09-04 amendment states this ceiling explicitly in both AC09 and Security bullet 3, so no interpretive step is needed to derive it. |
| Conforming | Pass | Names no mechanism; 'classified or treated as mechanical' and 'repository policy' are the source's own vocabulary from AC09 and Security bullet 3. |

---

## Summary

756 judgements recorded across 84 requirements and 9 characteristics. Every judgement is `Pass` except the
`Caveat`s below — none of which mark a requirement as failing. Each records a qualification the requirement
inherits from #2006's own text or from a multi-clause derivation, rather than a defect in the derivation:

- **Unambiguous:** RQA-BR-001, RQA-BR-006, RQA-BR-010, RQA-BR-012, RQA-BR-013, RQA-BR-014, RQA-FR-005, RQA-FR-006, RQA-FR-017, RQA-FR-025, RQA-FR-034, RQA-FR-038, RQA-FR-039, RQA-NFR-003, RQA-NFR-007, RQA-NFR-013, RQA-NFR-028, RQA-NFR-031 — each carries an undefined qualifier the source itself leaves open (for example, "material", "genuinely requires human judgement") that this specification does not resolve.
- **Correct:** RQA-NFR-027 — rests on a stated interpretive choice against its source clause's plain reading (a conjunctive derivation from C7 and C9), recorded rather than asserted as the only possible one.
- **Verifiable:** RQA-BR-001 (verified only transitively, through the rows it defers to), RQA-BR-006 (its fit criterion tests only the weaker of two source-admitted readings), RQA-FR-038 (tested against an explicitly bounded, individually-justified invariant set).
- **Conforming:** RQA-FR-005 — its fit criterion introduces an audit-apparatus element (independently corroborated evidence) that AC03 itself does not name.

No `Pass` judgement was weakened to reach these counts, and no `Caveat` was smoothed into an unqualified `Pass`.

**Round 9 (2026-09-04 amendment).** Six judgements that were `Caveat` are now `Pass`: RQA-NFR-024's and
RQA-NFR-030's Unambiguous, Feasible and Correct, three characteristics each. This is not a smoothing-over:
the 2026-09-04 amendment states, in CL-060's own text, exactly what round 6/7 had read in as an interpretive,
externally-contingent choice — the activity-conditioned credential floor and ceiling, and the resolution of the
external GitHub-permission-model premise draft ADR-B owned. Eight further `Correct` bases were reworded without
changing their verdict (RQA-FR-017, RQA-FR-018, RQA-NFR-019, RQA-NFR-020, RQA-NFR-021, RQA-FR-030, RQA-NFR-022,
RQA-NFR-028) to record that the design questions draft ADR-A and draft ADR-C once owned are now resolved at the
source; none of these eight was ever a `Caveat` on Correct, since each already held as an agreed obligation
under every option the drafts considered.

A new requirement, `RQA-NFR-031`, was also added in round 9 with nine fresh judgements — the amendment states a
behavioural-ceiling obligation (a finding whose remedy would change the system's behaviour is never classified as
mechanical) that no existing row carried; `RQA-NFR-019` bounds authority to whatever policy names as mechanical
but does not itself bound what policy may name. `RQA-NFR-031`'s own Unambiguous judgement is a `Caveat`, for the
same reason as several existing rows: 'behaviour'/'behavioural' are the amended source's own undefined terms.
