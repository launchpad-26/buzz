---
id: corpus-schema-overview
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

# Corpus Schema Overview

This is the minimal valid corpus node fixture used by issue #622's schema tests. It
carries every required frontmatter field and nothing else -- no relationships, no
optional fields -- so a validator regression that starts requiring an unlisted field
shows up here first.
