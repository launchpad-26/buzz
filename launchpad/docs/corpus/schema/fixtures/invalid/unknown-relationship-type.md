---
id: bad-relationship-type-node
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
relationships:
  - type: not-a-real-relationship
    target: corpus-schema-overview
---

Invalid fixture: the relationship's `type` is not one of relationships.schema.json's
closed enum values.
