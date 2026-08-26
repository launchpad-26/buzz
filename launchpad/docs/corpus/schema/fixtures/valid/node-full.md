---
id: corpus-schema-full-example
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The schema's enum choices will likely need extension as more corpus surfaces are authored."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "The team originally chose PyYAML over ruamel.yaml for this suite because these tests never rewrite a human-authored file in place."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "issue #622's build report"
relationships:
  - type: references
    target: corpus-schema-overview
---

# Corpus Schema Full Example

A second valid fixture, complementary to `node-minimal.md`. Where the minimal fixture
carries only the required fields with a single FACT entry, this one exercises every
optional path in the same pass: multiple audiences, all three evidence classes
(FACT, INFERENCE, TEAM_KNOWLEDGE) on their own happy path, and a relationship.
