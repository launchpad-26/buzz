---
id: bad-missing-status-node
type: governance
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
---

Invalid fixture: no `status` field at all (distinct from unknown-status.md, which
supplies a bad *value*). Confirms `status` is actually enforced as required.
