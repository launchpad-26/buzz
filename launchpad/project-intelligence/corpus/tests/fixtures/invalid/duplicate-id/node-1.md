---
id: validator-fixture-duplicate
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "First of two fixtures sharing the same id on purpose."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

Invalid fixture (paired with node-2.md): both nodes share `id: validator-fixture-duplicate`.
