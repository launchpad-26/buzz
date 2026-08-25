---
id: bad-fact-forbidden-fields-node
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
    confidence: 0.9
    provided_by: "someone"
---

Invalid fixture: `entry_class: FACT` carrying `confidence` and `provided_by`, fields that
belong to INFERENCE and TEAM_KNOWLEDGE respectively. memory.py's `__post_init__` raises
on either field being set for the wrong class; this schema must too, not just require the
right class's own fields.
