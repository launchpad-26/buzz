---
id: bad-team-knowledge-missing-provided-by-node
type: governance
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "The team originally chose PyYAML over ruamel.yaml for this suite because these tests never rewrite a human-authored file in place."
    entry_class: TEAM_KNOWLEDGE
---

Invalid fixture: `entry_class: TEAM_KNOWLEDGE` with no `provided_by`. TEAM_KNOWLEDGE
requires naming who said it -- that is the one thing distinguishing it from an
unattributed claim.
