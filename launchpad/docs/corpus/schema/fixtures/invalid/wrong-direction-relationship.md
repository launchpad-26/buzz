---
id: bad-relationship-direction-node
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
relationships:
  - type: depended-on-by
    target: corpus-schema-overview
---

Invalid fixture: `depended-on-by` is `depends-on`'s *generated* inverse type
(relationships.schema.json's `relationshipMeta`), never hand-authored. Authoring the
inverse edge directly asserts the relationship in the wrong direction -- the schema's
`type` enum only contains the five authored-direction values, so this is rejected the
same way `unknown-relationship-type.md` is, but for a different, meaningful mistake: not
an arbitrary typo, a real inverse-edge-authored-by-hand error.
