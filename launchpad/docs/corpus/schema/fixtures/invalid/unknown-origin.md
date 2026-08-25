---
id: bad-origin-node
type: governance
status: active
origin: not-a-real-origin
audiences:
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
---

Invalid fixture: `origin` is not one of node.schema.json's closed enum values.
