---
id: validator-fixture-duplicate
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "Second of two fixtures sharing the same id on purpose."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

Invalid fixture (paired with node-1.md): both nodes share `id: validator-fixture-duplicate`.
