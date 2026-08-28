---
id: validator-fixture-nan-confidence
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This entry's confidence is NaN on purpose."
    entry_class: INFERENCE
    evidence:
      - "Justfile"
    confidence: .nan
---

Invalid fixture: `confidence: .nan` satisfies node.schema.json's `minimum`/`maximum`
keywords (every comparison against NaN is false, so the range assertion never fires)
but must be rejected by the validator's explicit finite-number check (#1463).
