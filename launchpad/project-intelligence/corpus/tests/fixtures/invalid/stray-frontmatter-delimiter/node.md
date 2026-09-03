---
id: validator-fixture-stray-frontmatter-delimiter
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node's frontmatter contains a stray '---' line before the real closing delimiter, hiding a relationships block with an unresolvable target."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---
relationships:
  - type: references
    target: no-such-node-anywhere
---

Invalid fixture: a stray '---' line closes the frontmatter early (pre-#1482-fix),
hiding the `relationships` block above -- which names a target nothing in this
fixture set carries -- from ever being read.
