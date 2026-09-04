# RQA traceability

How every requirement is bound to its source clause, and the two checks that confirm the binding holds. Feeds
[`requirements-specification.md`](requirements-specification.md) and
[`singular-splits.md`](singular-splits.md).

## Traceability rule

CL-062, the success-criteria preamble sentence 2, states: **"A criterion is satisfied only when its complete
behaviour is demonstrated — passing one clause of a multi-part criterion does not satisfy the criterion."** This
specification carries that sentence forward as a binding traceability rule for **acceptance-criterion splits**
rather than as a numbered requirement, because it is not itself an obligation on the delivered system — it is an
obligation on how this specification's own AC-derived splits must be read:

> **A source acceptance criterion is satisfied only when every requirement derived from it is satisfied, not
> merely one.**

CL-062's own text speaks only to acceptance criteria ("passing one clause of a multi-part *criterion*"). This
specification separately **adopts the same atomicity discipline as its own methodology choice** — not as
something CL-062 itself mandates — for splits of P, C, project-requirement, closing-criterion, and
security-implications clauses: a source P/C/security bullet is likewise satisfied only when every requirement
derived from it holds, not merely one.

Every multi-requirement entry in [singular-splits.md](singular-splits.md) below is subject to this rule (both the CL-062-mandated
half for AC splits, and this specification's own adopted extension for the rest). Where one clause produced
several requirements — for example CL-034/AC07 into RQA-FR-014, RQA-FR-015 and RQA-FR-036 — a gap analysis that
reports the clause "covered" because one child requirement holds, while the others remain unmet, misreads this
specification exactly as CL-062 forbids for AC splits, and exactly as this specification's own adopted rule
forbids for every other split. This rule is CL-062's own disposition: **Derived — traceability rule**, the one
clause in [clause-inventory.md](clause-inventory.md) that derives no numbered requirement of its own (the checks below
record this exception explicitly).

---



## Bidirectional clause↔requirement check

**Method.** Two checks, both re-run after every change to the clause list or a requirement table:

1. **Reference-graph check**: every requirement's `cl` (source-clause) reference is checked against the clause
   inventory: (a) every clause in the inventory carries exactly one of the four dispositions and no clause ID is
   duplicated or missing (65 clauses, verified); (b) every requirement across all three classes names a clause ID
   that exists in the inventory (verified — zero references to a non-existent clause); (c) every clause disposed
   **Derived** is named by at least one requirement, and CL-062 (**Derived — traceability rule**) is named by the
   traceability rule in the traceability rule above rather than by a numbered requirement — the one deliberate exception
   to "derived clause names a requirement" (verified — zero numbered-requirement-derived clauses are
   unreferenced).
2. **Note-cell equality check**: for every **Derived** clause, every requirement ID that check 1's reference graph
   actually associates with that clause is verified present, as a substring, in that clause's inventory Note
   cell. The check does not flag a Note cell that additionally cites an unrelated clause's requirement ID for
   cross-reference explanation — its purpose is catching silent omission, not penalising legitimate
   cross-reference. This check is scoped to **Derived** clauses only, and — as rounds 6 and 7 both confirm
   concretely — it can only catch an omission from an edge already present in a requirement's `cl` list; it
   cannot detect a semantically genuine source clause a requirement's `cl` list never named in the first place.
   Both round 6 (RQA-BR-010's CL-017/CL-040) and round 7 (RQA-NFR-007's CL-035/CL-039, RQA-NFR-024's CL-056)
   omissions were found by adversarial review reading the QA document's own prose against the reference graph,
   not by this automated check — recorded here as a standing limitation, not a one-off.

**Result: PASS in both directions, on both checks.**

- Clause → requirement: all 50 numbered-requirement-derived clauses are named by ≥1 requirement (0 unreferenced);
  CL-062 is named by the traceability rule, its recorded exception.
- Requirement → clause: all 86 requirements (14 business, 39 functional, 33 non-functional) name at least one
  existing derived clause, and none names a clause disposed as context or scope exclusion (0 such references).
  RQA-BR-005 names two source clauses (CL-009 and CL-002), RQA-BR-010 names three (CL-014, CL-017, CL-040),
  RQA-NFR-007 names three (CL-023, CL-035, CL-039 — round 7), RQA-NFR-024 and RQA-NFR-030 each name two
  (CL-060, CL-056 — round 7), RQA-NFR-027 names two (CL-024 and CL-026), RQA-NFR-031 names two (CL-036 and
  CL-057 — round 9), and RQA-NFR-032 (CL-058) and RQA-NFR-033 (CL-036) were each added in round 9b, so there
  are 95 requirement→clause derivation edges across the 86 requirement rows.
- Note-cell equality: every Derived clause's Note cell names every requirement its `cl` reference set actually
  contains (0 stale cells within the check's Derived-only scope).
- Total requirements: 86 = 14 + 39 + 33 (RQA-FR-036…039 and RQA-NFR-026…030 were appended across rework rounds,
  RQA-NFR-031 was appended in round 9, and RQA-NFR-032/RQA-NFR-033 in round 9b; no existing ID was renumbered
  or retired). Total clauses: 65 = 50 numbered-requirement-derived + 1
  traceability-rule-derived (CL-062) + 8 scope exclusion + 6 context.

