---
id: validator-fixture-misplaced-generated
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This fixture directory also contains a stray .json file, sitting outside generated/."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

Invalid fixture: valid on its own, but paired with a stray index.json sitting
directly beside it (outside generated/) to prove the ownership check fires.
