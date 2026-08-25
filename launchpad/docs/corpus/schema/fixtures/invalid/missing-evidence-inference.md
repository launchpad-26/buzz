---
id: bad-inference-evidence-node
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "The schema's enum choices will likely need extension as more corpus surfaces are authored."
    entry_class: INFERENCE
    confidence: 0.6
---

Invalid fixture: the one evidence entry is `entry_class: INFERENCE` with a `confidence`
but no `evidence` citations. INFERENCE requires both -- the exact gap an independent
plan review (serina:review-plan) found this schema would otherwise have shipped with
no test for it.
