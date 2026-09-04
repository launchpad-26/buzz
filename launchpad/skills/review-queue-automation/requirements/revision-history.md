# RQA revision history

This specification went through eight review rounds before being frozen for
[#2069](https://github.com/launchpad-26/buzz/issues/2069) at commit `be77edee5`. Each round re-checked the whole
document against [`prd-2006-normative-extract.md`](prd-2006-normative-extract.md) and against itself; every
round after the first was adversarial peer review by two independent reviewer models. This page records what
each round changed, briefly and without the review commentary that produced it.

| Round | What it did |
|---|---|
| 1 | First derivation from the extract: numbered every clause (`CL-001`–`CL-065`), derived the initial requirement set, and ran the bidirectional clause↔requirement check for the first time. |
| 2 | Split two security-implications clauses that had been under-split: `CL-058` into a specific untrusted-writer prohibition and a general provenance-integrity obligation (`RQA-NFR-022`/`RQA-NFR-028`); `CL-059` into a per-repository and a per-change external-send decision (`RQA-NFR-023`/`RQA-NFR-029`). |
| 3 | Re-derived `RQA-NFR-027`'s source clauses (`C7` and `C9` jointly, not `C7` alone) and corrected `RQA-FR-029`'s EARS pattern (`Optional-feature` → `State-driven`, since its biconditional obligates both branches of the merge-configuration fact). |
| 4 | Split the credential-scope obligation in two: `RQA-NFR-024` (the floor — what the credential must carry) and `RQA-NFR-030` (the ceiling — what it must not exceed). Recast `RQA-NFR-007`'s scope and corrected two requirements whose fit criteria could pass on evidence weaker than the obligation required (`RQA-FR-037`, `RQA-NFR-018`) and two whose fit criteria demanded more than the source clause actually asked for (`RQA-FR-009`, `RQA-FR-034`). |
| 5 | Repaired the EARS classification rule itself — it had excluded author-supplied artifacts (like a pull request) from the artifact-class test, and applied a standing-capacity carve-out inconsistently — then reclassified the six rows the repaired rule newly reached (`RQA-BR-013`, `RQA-FR-017`, `RQA-FR-028`, `RQA-FR-029`, `RQA-NFR-016`, `RQA-FR-030`). |
| 6 | Stated an explicit test distinguishing the `State-driven` and `Ubiquitous` patterns (condition-subject vs. produced-record-subject), reclassified `RQA-FR-025` under it, and closed a traceability gap: `RQA-BR-010`'s qualifier had always depended on `CL-017`/`CL-040` as well as its primary clause, but that dependency was not yet recorded as a reference-graph edge. |
| 7 | Closed the equivalent traceability gap for `RQA-NFR-007` (`CL-035`/`CL-039`) and `RQA-NFR-024` (`CL-056`); completed the round-6 differentiator registry for three more rows (`RQA-BR-006`, `RQA-BR-009`, `RQA-NFR-018`); and repaired eleven fit criteria found capable of passing on a false green or failing on a false red, including `RQA-NFR-028` (tested at the authority boundary, not physical storage immutability) and `RQA-BR-006` (tested against the weaker of two source-admitted readings its own Unambiguous caveat already recorded). |
| 8 | Final polish: added an explicit EARS-classification check for the two credential rows most changed in round 7; added a `Conforming` caveat to `RQA-FR-005` (its fit criterion asks for corroborated evidence beyond what AC03 itself names) and a `Verifiable` caveat to `RQA-BR-001` (it is verified only transitively, through the rows it defers to); recorded that `RQA-FR-011` and `RQA-FR-037` restate the same proposition from two source clauses; and clarified how the singular-split count treats a joint-citation edge versus a genuine content split. |

**Every round preserved:** the 83 requirement IDs (14 business, 39 functional, 30 non-functional), the 65-clause
inventory, and both directions of the bidirectional check. No round retired or renumbered an identifier; rounds
that discovered a bundled obligation appended a new ID rather than reusing or renumbering an existing one (see
[`singular-splits.md`](singular-splits.md)).

**Open questions this specification could not settle** are recorded once, as ADR drafts, rather than resolved
here: see [`adr-drafts/`](adr-drafts/).
