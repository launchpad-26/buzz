---
id: fixture-index-beta
type: implementation
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
  - type: depends-on
    target: fixture-index-alpha
  - type: supersedes
    target: fixture-index-delta
---

# Fixture beta

Depends on alpha and supersedes delta, so the generator's derived inverse maps
have a depended-on-by and a superseded-by edge to derive.
