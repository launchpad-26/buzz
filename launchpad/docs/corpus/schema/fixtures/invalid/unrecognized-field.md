---
id: bad-unrecognized-field-node
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
internal_note: "this field is not part of node.schema.json"
---

Invalid fixture: an unrecognized top-level field (`internal_note`). `additionalProperties:
false` should reject it -- a typo'd field name like `audience` instead of `audiences`
must fail loudly rather than silently validating as an unrelated extra key.
