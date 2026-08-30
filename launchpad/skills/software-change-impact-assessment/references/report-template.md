# Software Change Impact Assessment

## 1. Change Identification

Assessment ID:  
Assessment date:  
Prepared by:  

Source repository:  
Source branch/tag:  
Source revision (SHA):  

Downstream repository:  
Downstream branch:  
Downstream revision (SHA):  

Baseline/common revision (SHA):  
Merge-base (SHA, if applicable):  
Comparison scope and commands:  

---

## 2. Executive Summary

Overall Risk: `LOW | MEDIUM | HIGH | CRITICAL`  
Assessment: `LOW CONCERN | PROCEED WITH ROUTINE VERIFICATION | PROCEED WITH SPECIFIC ATTENTION | SIGNIFICANT REVIEW REQUIRED | BLOCKING ISSUE IDENTIFIED`  

This change ...

Key findings:
- `[CIA-...]` ... (`CONFIRMED | STRONGLY_SUPPORTED | POTENTIAL | UNKNOWN`)

Primary areas requiring attention:
- ...

Unknowns:
- ...

---

## 3. Change Scope

Incoming commits:  
Changed files:  
Files added:  
Files modified:  
Files removed:  
Renames:  
Lines added:  
Lines removed:  

Affected areas:
- ...

## 4. Significant Functional Changes
### New functionality
### Changed behaviour
### Removed or deprecated behaviour

## 5. Architecture and Technical Impact

## 6. API and Interface Impact

For each relevant interface: compatibility = `COMPATIBLE | POTENTIALLY_BREAKING | BREAKING | UNKNOWN`; evidence, consumers, and rationale.

## 7. Data and Schema Impact

State migration, serialization, compatibility, destructive/irreversible effects, and evidence availability explicitly.

## 8. Configuration Impact

## 9. Dependency and Supply-Chain Impact

## 10. Build and Toolchain Impact

## 11. CI/CD Impact

## 12. Security Impact

## 13. Operational and Observability Impact

## 14. Downstream Impact
### Downstream-specific modifications affected
### Overlap
### Changed assumptions

## 15. Conflict Assessment
### Textual conflicts
### Semantic conflicts
### Policy conflicts

## 16. Risk Assessment

Overall risk:  
Rationale:  

| Risk | Likelihood | Impact | Rating | Confidence | Evidence |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 17. Required Attention and Verification

- ...

## 18. Unknowns and Limitations

- ...

## 19. Assessment Recommendation

Recommendation:  
Rationale:  
Advisory only; this report does not authorize or execute the change.

## 20. Evidence

Baseline:  
Incoming revision:  
Comparison:  
Relevant commits:  
Relevant PRs:  
Relevant files:  
Dependency evidence:  
Security evidence:  
Test evidence:  
Documentation / ADR / policy evidence:  
Evidence availability: `AVAILABLE | UNAVAILABLE | INCOMPLETE | ERROR | NOT_APPLICABLE`
