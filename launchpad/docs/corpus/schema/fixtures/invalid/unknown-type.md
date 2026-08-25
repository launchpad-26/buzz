---
id: bad-type-node
type: not-a-real-type
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
---

Invalid fixture: `type` is not one of node.schema.json's closed enum values.
