---
id: bad-missing-type-node
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

Invalid fixture: no `type` field at all (distinct from unknown-type.md, which supplies a
bad *value*). Confirms `type` is actually enforced as required, not merely enum-checked
when present.
