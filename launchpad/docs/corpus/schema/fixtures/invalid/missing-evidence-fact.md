---
id: bad-fact-evidence-node
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node documents the corpus metadata schema introduced by issue #622."
    entry_class: FACT
---

Invalid fixture: the one evidence entry is `entry_class: FACT` but carries no `evidence`
citations. FACT requires evidence per launchpad/project-intelligence/CONTRACT.md and
memory.py's enforced rule.
