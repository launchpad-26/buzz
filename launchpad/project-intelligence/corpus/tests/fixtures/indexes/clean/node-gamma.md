---
id: fixture-index-gamma
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node is a fixture used only by the index generator's own tests."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/indexes.py"
relationships:
  - type: implements
    target: fixture-index-alpha
  - type: part-of
    target: fixture-index-beta
  - type: references
    target: fixture-index-delta
---

# Fixture gamma

Implements alpha, is part of beta, and references delta -- covering the
implemented-by and has-part derived inverses plus the authored-only
referenced-by case that must never be derived.
