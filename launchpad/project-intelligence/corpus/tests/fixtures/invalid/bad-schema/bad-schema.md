---
id: validator-fixture-bad-schema
type: not-a-real-type
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node deliberately violates node.schema.json's type enum."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

Invalid fixture: `type` is not one of node.schema.json's closed enum values. Used to
prove validate.py rejects a structurally invalid node and names it.
