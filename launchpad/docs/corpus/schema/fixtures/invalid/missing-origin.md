---
id: bad-missing-origin-node
type: governance
status: active
audiences:
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
---

Invalid fixture: no `origin` field at all (distinct from unknown-origin.md, which
supplies a bad *value*). Confirms `origin` is actually enforced as required.
