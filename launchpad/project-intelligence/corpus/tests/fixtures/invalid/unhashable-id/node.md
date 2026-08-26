---
id:
  - some/private/path/id_rsa
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node's id is a YAML list, which is unhashable."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

Invalid fixture: `id` is a list. Valid YAML, a schema violation, and unhashable -- so
duplicate-id detection, which deliberately includes schema-invalid nodes because two
nodes can collide on an id neither of which validates, crashed with an unhandled
`TypeError: unhashable type: 'list'` instead of the controlled, node-naming failure the
definition of done requires. A stack trace names no node. An independent cross-model
review-final pass found this.
