---
id: validator-fixture-a
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node is a valid fixture used by the corpus validator's own tests."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

# Validator fixture A

A minimal valid corpus node, used only by validate.py's own test suite. It is not
real corpus content and lives under project-intelligence/corpus/tests/fixtures/, never
under the real launchpad/docs/corpus/ root.
