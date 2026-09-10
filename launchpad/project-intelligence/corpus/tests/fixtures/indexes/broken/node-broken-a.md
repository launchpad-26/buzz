---
id: fixture-index-broken-a
type: architecture
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
    target: fixture-index-missing
---

# Fixture broken-a

Declares a depends-on edge to a target that exists nowhere, so the generator's
broken-edge report has something to catch. validate.py would fail this corpus;
the generator must report the edge and keep going, never crash.
