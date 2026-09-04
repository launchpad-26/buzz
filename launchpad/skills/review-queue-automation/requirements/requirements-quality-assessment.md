# RQA requirements quality assessment

Per-requirement assessment of every requirement in
[`requirements-specification.md`](requirements-specification.md) against the nine individual requirement
characteristics named in [launchpad-26/buzz#2069](https://github.com/launchpad-26/buzz/issues/2069)'s definition
of done: **necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming.**

## How to read this

One heading per requirement, nine judgements each — 86 × 9 = 774 recorded judgements in total. Each judgement
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
| Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018, RQA-NFR-031, RQA-NFR-033 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
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
| Singular | Pass | One dominant obligation; CL-036 was split across RQA-FR-017, RQA-FR-018, RQA-NFR-031, RQA-NFR-033 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
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
| Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021, RQA-NFR-031 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
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
| Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021, RQA-NFR-031 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
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
| Singular | Pass | One dominant obligation; CL-057 was split across RQA-NFR-019, RQA-NFR-020, RQA-NFR-021, RQA-NFR-031 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects CL-057's (Security implications, bullet 3) plain-reading obligation, not AC09's. The 2026-09-04 amendment confirms remediation authority to modify and push code for mechanical findings is now source-granted (previously an open design question, draft ADR-A) — this bound is therefore a currently live, binding constraint on an exercised authority, not a pre-emptive one held in reserve against a future grant. |
| Conforming | Pass | Names 'force-push', 'merge', 'branch protection' and 'protected branch' — CL-057's own enumerated prohibitions, carried verbatim. |


### RQA-NFR-022

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | — |
| Appropriate | Pass | — |
| Unambiguous | Pass | 'Any model output, authenticated or not' makes explicit what the amended source states ('never by reviewed content or model output'); the pre-amendment 'unauthenticated' qualifier that left authenticated model output outside the prohibition is removed. |
| Complete | Pass | — |
| Singular | Pass | One prohibition widened to the amended writer set; CL-058 is split across the prohibition row, the tamper-evidence row (RQA-NFR-028) and the positive sole-writer row (RQA-NFR-032). |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Directly the amended CL-058 sentence 'Provenance is written by RQA, never by reviewed content or model output'; the prohibition now matches the source's unqualified model-output exclusion. |
| Conforming | Pass | Names only the source's own writer categories ('reviewed content', 'model output') and the elements RQA-FR-012 reconstructs. |


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
| Necessary | Pass | Carries the configured-scope-growth half of amended CL-060 that no other row states — the base scopes plus exactly the write scope a remediation-push or merge-after-review repository's operations require. |
| Appropriate | Pass | Stated at the non-functional credential-scope level alongside RQA-NFR-030, its ceiling complement. |
| Unambiguous | Pass | Maps directly to amended CL-060's structure: a base scope on every managed repository, plus an exactly-bounded additional scope where configured operations require it; no round-6-of-NFR-arch interpretive gap remains because the source states this structure itself. |
| Complete | Pass | — |
| Singular | Pass | One floor obligation — 'carry the configured scopes on each managed repository' — whose additional-scope conjunct is keyed to the same configuration axis, not an independent obligation. |
| Feasible | Pass | The scope is stated to grow exactly as configured authority requires; satisfaction is not contingent on any external premise. |
| Verifiable | Pass | — |
| Correct | Pass | Directly reflects amended CL-060's sentences: the base scopes over the target repositories, the additional operation-scope where a repository's policy grants remediation push or merge-after-review, and the advisory cap — all source text, no interpretive step. |
| Conforming | Pass | Names the scopes in CL-060's own vocabulary ('pull-requests write and contents read', lightly normalised) and no mechanism. |


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
| Unambiguous | Pass | The 2026-09-04 amendment explicitly selects tamper-evidence: CL-058 now says provenance 'is tamper-evident within the operator's trust boundary, and does not defend against a compromised operator machine', which is the acceptance/authority-boundary reading this row's fit criterion operationalises — the prior Caveat recorded an ambiguity the amendment resolved. |
| Complete | Pass | — |
| Singular | Pass | One dominant obligation; CL-058 was split across RQA-NFR-022, RQA-NFR-028, RQA-NFR-032 — see [singular-splits.md](singular-splits.md) for how the split was drawn. |
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
| Necessary | Pass | Carries the per-repository activity-relative ceiling that RQA-NFR-024's floor does not; the two are independently falsifiable in each direction. |
| Appropriate | Pass | — |
| Unambiguous | Pass | 'No permission beyond what that repository's configured activities require' is CL-060's own 'and no more' ceiling, restated over the managed-repository and non-managed boundaries; the removed fixed-cap reading that the pre-amendment clause forced is gone. |
| Complete | Pass | — |
| Singular | Pass | One ceiling obligation tested across the configured-activity and managed-repository boundaries; its three clauses are facets of the same upper bound, matching how RQA-NFR-021 tests four never-actions in one row. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | CL-060 now states exactly this per-repository ceiling ('the token for that repository additionally carries the write scope those operations require, and no more — repositories configured for advisory-only review carry no write scope beyond pull-requests'); the advisory example in the fit criterion treats holding base pull-requests write as compliant, matching the source's 'no write scope beyond pull-requests'. |
| Conforming | Pass | — |


### RQA-NFR-031

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Now carries both necessary properties of a mechanical remedy — deterministic AND non-behaviour-changing — that amended AC09 states; no other row bounds determinism. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | Two source-inherited open-textured points: 'behaviour'/'behavioural' are the amended source's own undefined terms, and the statement qualifies AC09's 'the system's behaviour' as 'the software under review's behaviour' so a reader does not misread the referent as RQA itself (this document's usual 'the system'); the fit criterion tests the classification outcome, not a definition #2006 leaves open. |
| Complete | Pass | — |
| Singular | Pass | — |
| Feasible | Pass | — |
| Verifiable | Pass | Strengthened fit criterion closes the prior false-green: no mechanical-only handling may occur — classification, treatment, or suppression of the human-attention path — rather than only the final gate before remediation authority acts. |
| Correct | Pass | AC09 defines a mechanical remedy as 'deterministic and does not change the system's behaviour' and CL-057 states the behavioural line is the ceiling on what policy may classify as mechanical; the statement carries both conjuncts. |
| Conforming | Pass | Uses the source's own 'deterministic'/'behaviour' vocabulary with a Conforming-scoped referent qualification recorded in the Unambiguous basis. |


### RQA-NFR-032

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Carries the positive half of amended CL-058 ('Provenance is written by RQA') that neither NFR-022 (a prohibition) nor NFR-028 (tamper-evidence) states; a design where every prohibited writer is excluded but no authoritative writer is designated would fail nothing else. |
| Appropriate | Pass | — |
| Unambiguous | Pass | 'Written by the system itself' and 'input the system records, not a write of its own' state the sole-writer rule and the self-report-as-input distinction in plain terms. |
| Complete | Pass | — |
| Singular | Pass | One obligation — RQA writes the authoritative record; the semicolon clause is an explanatory clarification of what 'written by the system itself' means for a harness/model self-report, not a second shall. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | Reflects CL-058's 'Provenance is written by RQA, never by reviewed content or model output' directly; the fit criterion permits a self-report to remain input while requiring RQA's own write path to construct and commit every authoritative provenance element. |
| Conforming | Pass | — |


### RQA-NFR-033

| Characteristic | Verdict | Basis (where not obvious) |
|---|---|---|
| Necessary | Pass | Carries AC09's 'and requires human attention' conjunct, which no other row states: RQA-FR-025/026/027 govern escalations actually raised, yet nothing compels one for a behaviour-changing finding — a finding could be classified non-mechanical and left unprogressed with no human seeing it while every other criterion passes. |
| Appropriate | Pass | — |
| Unambiguous | Caveat | Same source-inherited open-textured 'behaviour' term as RQA-NFR-031, and the same qualified referent ('the software under review'); the fit criterion makes 'human attention' observable as a named human receiving and considering the finding without equating attention with approval. |
| Complete | Pass | — |
| Singular | Pass | One obligation — a behaviour-changing finding receives human attention; the conjoined CL-036/AC09 citation is the amendment's own single sentence. |
| Feasible | Pass | — |
| Verifiable | Pass | — |
| Correct | Pass | AC09's closing sentence 'A finding whose remedy would change behaviour is never mechanical, regardless of how small it is, and requires human attention' states the obligation directly. |
| Conforming | Pass | Names no implementation mechanism; the fit criterion permits a specific escalation or another recorded human-review path and requires only the source's human-attention outcome. |


---

## Summary

774 judgements recorded across 86 requirements and 9 characteristics. Every judgement is `Pass` except the
`Caveat`s below — none of which mark a requirement as failing. Each records a qualification the requirement
inherits from #2006's own text or from a multi-clause derivation, rather than a defect in the derivation:

- **Unambiguous:** RQA-BR-001, RQA-BR-006, RQA-BR-010, RQA-BR-012, RQA-BR-013, RQA-BR-014, RQA-FR-005, RQA-FR-006, RQA-FR-017, RQA-FR-025, RQA-FR-034, RQA-FR-038, RQA-FR-039, RQA-NFR-003, RQA-NFR-007, RQA-NFR-013, RQA-NFR-031, RQA-NFR-033 — each carries an undefined qualifier the source itself leaves open
  (for example, "material", "genuinely requires human judgement", "behaviour") that this specification does not
  resolve. These include RQA-NFR-031 and RQA-NFR-033, whose statements govern remedies to the software under
  review and therefore carry a documented referent qualification alongside the unresolved "behaviour" term.
- **Correct:** RQA-NFR-027 — rests on a stated interpretive choice against its source clause's plain
  reading (a conjunctive derivation from C7 and C9), recorded rather than asserted as the only possible one.
- **Verifiable:** RQA-BR-001, RQA-BR-006, RQA-FR-038 — RQA-BR-001 (verified only transitively, through the rows it defers to),
  RQA-BR-006 (its fit criterion tests only the weaker of two source-admitted readings), RQA-FR-038 (tested
  against an explicitly bounded, individually-justified invariant set).
- **Conforming:** RQA-FR-005 — its fit criterion introduces an audit-apparatus element (independently
  corroborated evidence) that AC03 itself does not name.

No `Pass` judgement was weakened to reach these counts, and no `Caveat` was smoothed into an unqualified `Pass`.

**Round 9 (2026-09-04 amendment).** Six judgements that were `Caveat` became `Pass` for RQA-NFR-024 and
RQA-NFR-030 (their Unambiguous, Feasible and Correct, three each) when the amendment's CL-060 stated the
configured-authority credential structure directly. That promotion was later re-examined (round 9b): the two
credential rows were re-derived against the amended clause, so their judgements here are fresh for the reworded
statements. RQA-NFR-022, RQA-NFR-031 were reworded and re-judged; RQA-NFR-032 and RQA-NFR-033 were added as new
rows with nine fresh judgements each; RQA-NFR-028's Unambiguous Caveat was promoted to Pass because the
amendment explicitly selects tamper-evidence over physical immutability. RQA-NFR-024 and RQA-NFR-030's
Unambiguous, Feasible and Correct were Pass in the round-9 commit; the 9b re-derivation keeps each Pass but on
the amended statement, and is recorded as a fresh judgement rather than a surviving promotion.
