---
id: bad-duplicate-audiences-node
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
---

Invalid fixture: `audiences` repeats the same value twice. `uniqueItems: true` should
reject it.
