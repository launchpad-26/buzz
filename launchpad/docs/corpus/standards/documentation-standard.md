---
id: corpus-standard-documentation-standard
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109."
    entry_class: FACT
    evidence:
      - "commit ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109"
  - statement: "The deterministic checker never reads a node's Markdown body: the front matter is split off and the remainder is discarded before any check runs."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The checker applies no rule keyed to a subdirectory, so a node under standards/ is validated exactly like a node anywhere else beneath the corpus root."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "ADR-0028 names the human-read pull-request diff as the enforcement mechanism the corpus depends on, and chose Markdown over a machine-readable record format for that reason."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The schema's type enum contains governance and contains no policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The instruction node defers per-type standards and per-type templates to tasks #1307-#1351 and states that until they land there is no per-type template to follow."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Four corpus standards drafted in parallel independently converged on the same five-part shape: a scope-and-authority opening, separated normative requirements, an enforcement section, an exceptions-and-escalation section, and a closing scope-and-omissions section."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/b899609f677317ebde4ba16620b3dd23b1510d62/launchpad/docs/corpus/standards/atomicity.md"
      - "https://github.com/launchpad-26/buzz/blob/5f7e1330b2d422129bb92148c5d4a2ee4cc8958e/launchpad/docs/corpus/standards/code-references.md"
      - "https://github.com/launchpad-26/buzz/blob/e8ba1ec8e2d605ecfbc6a7d9ee0ca058e95a2d24/launchpad/docs/corpus/standards/confidence.md"
      - "https://github.com/launchpad-26/buzz/blob/8eb2d2658a707c025ba7bcf1c2f2063f5de2e387/launchpad/docs/corpus/standards/decision-references.md"
  - statement: "Those same four standards carry four different H1 title forms, disagree on whether top-level sections are numbered, and name their normative and enforcement sections four different ways."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/b899609f677317ebde4ba16620b3dd23b1510d62/launchpad/docs/corpus/standards/atomicity.md"
      - "https://github.com/launchpad-26/buzz/blob/5f7e1330b2d422129bb92148c5d4a2ee4cc8958e/launchpad/docs/corpus/standards/code-references.md"
      - "https://github.com/launchpad-26/buzz/blob/e8ba1ec8e2d605ecfbc6a7d9ee0ca058e95a2d24/launchpad/docs/corpus/standards/confidence.md"
      - "https://github.com/launchpad-26/buzz/blob/8eb2d2658a707c025ba7bcf1c2f2063f5de2e387/launchpad/docs/corpus/standards/decision-references.md"
  - statement: "The atomicity standard states its one-idea requirement generically over corpus nodes rather than per node type, so it already binds a governance-typed standard document without restatement."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/b899609f677317ebde4ba16620b3dd23b1510d62/launchpad/docs/corpus/standards/atomicity.md"
  - statement: "ADR-0029 makes flagged the state for two authoritative sources of the same claim type in conflict, held for a human rather than resolved by the author."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Issue #1313's definition of done requires this node to state scope and authority, to separate MUST requirements from SHOULD guidance, to define enforcement and an exception/escalation process, and to link decisions rather than duplicate them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1313 definition of done"
  - statement: "All nineteen standards issues #1307-#1325 carry those four required-content clauses verbatim, and so do all five sampled template issues #1326, #1330, #1344, #1346 and #1351, which makes them batch-wide document requirements rather than a contract specific to standards."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issues #1307-#1325 and #1326, #1330, #1344, #1346, #1351 definition-of-done clauses"
  - statement: "Because no check reads body prose, every requirement stated in this standard and in every sibling standard is held by pull-request review alone."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
    confidence: 0.9
---

# Standard: corpus standards

## Scope and authority

## MUST

## SHOULD

## Enforcement

## Exceptions and escalation

## Scope and omissions
