---
id: Not Kebab Case!
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
---

Invalid fixture: `id` is not kebab-case (spaces and uppercase). ADR-0028 requires a
stable identifier that is never renamed once assigned; an unenforced pattern would let
non-kebab-case ids through today, later forcing exactly the rename the schema exists to
prevent.
