---
id: validator-fixture-missing-citation
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This citation points at a path that does not exist in this repository."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/this-file-does-not-exist.md"
---

Invalid fixture: the one evidence citation does not resolve to a real file.
