---
id: bad-inference-missing-confidence-node
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "The schema's enum choices will likely need extension as more corpus surfaces are authored."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
---

Invalid fixture: `entry_class: INFERENCE` with `evidence` present but no `confidence`.
INFERENCE requires both.
