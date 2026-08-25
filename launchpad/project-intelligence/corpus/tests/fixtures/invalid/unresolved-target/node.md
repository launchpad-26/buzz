---
id: validator-fixture-unresolved-target
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node's relationship target does not exist in this fixture set."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
relationships:
  - type: references
    target: no-such-node-anywhere
---

Invalid fixture: `relationships[0].target` names an id nothing in this directory has.
