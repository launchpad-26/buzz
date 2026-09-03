---
id: validator-fixture-missing-closing-delimiter
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node opens with '---' and never closes it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
body text, frontmatter delimiter never closed
