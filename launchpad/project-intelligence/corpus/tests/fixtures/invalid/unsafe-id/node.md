---
id: "some/private/path/id_rsa"
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node's own id is credential-shaped and violates the id pattern."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

Invalid fixture: the sibling leak to `leaky-schema-error/`. Every error message names
its node, and the obvious way to name one is its `id` -- but `id` is only known to be
kebab-case *after* schema validation passes, and this node's does not. A schema-invalid
node can carry any string at all in that field, including the credential-shaped path
here, so messages fall back to the file path whenever the id is not schema-shaped.
