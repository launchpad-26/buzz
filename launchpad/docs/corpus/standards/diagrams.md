---
id: corpus-standard-diagrams
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
  - statement: "Markdown with YAML front matter is the one canonical authored representation of a corpus node, and every other serialization is a generated derived view that is never hand-authored."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "ADR-0028's deciding factor is that the corpus is reviewed at the pull request that changes it, so the authored form has to be something a human reviewer can read comfortably in a PR diff."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The corpus root is launchpad/docs/corpus, and validate.py is the deterministic check that governs it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Every non-.md file under the corpus root is rejected today, including one placed under generated/, because no generator exists yet to reproduce it from canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The validator refuses a generated artifact whose provenance it cannot establish rather than deciding the question, and names #1316 as the owner of that contract."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A node is parsed by splitting its leading front matter from the remainder, and only the front matter is returned, so no check reads a node's body."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A node whose body carries a fenced diagram asserting a wholly invented topology, and a Markdown link to a file that does not exist, validates clean and exits 0."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The evidence array is the node's provenance ledger, carrying one entry per claim, classified FACT, INFERENCE or TEAM_KNOWLEDGE."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "A bare repository path in a citation is opened on disk and must resolve to a real file inside the repository, so a directory fails."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation naming a line or line range is checked for the path and for the position's internal consistency only; the line number is never compared against the file's length."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Five relationship types are defined, each with its own directionality and an inverse marked generated or authored."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "Evidence precedence is contextual by claim type, and two authoritative sources of the same claim type in conflict leave the node flagged for a human rather than silently resolved."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Changes under launchpad/docs/corpus are validated in CI on pull requests and on pushes to the launchpad branch, by the same command run locally."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "ARCHITECTURE.md and README.md each carry a component topology drawn in box-drawing characters, and launchpad/Research/hardening-linux-servers.md carries a Mermaid flowchart, so diagram-as-text is an established convention in this repository rather than something this standard introduces."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md"
      - "README.md"
      - "launchpad/Research/hardening-linux-servers.md"
  - statement: "At the recorded revision, one tracked Markdown file in the repository carries a Mermaid fence and twenty carry box-drawing characters."
    entry_class: FACT
    evidence:
      - "git_grep(pattern=mermaid_fence, glob=*.md) -> 1 tracked file"
      - "git_grep(pattern=box_drawing_chars, glob=*.md) -> 20 tracked files"
  - statement: "A diagram drawn in a node's body is invisible to every check that exists, so a relationship asserted only in a diagram is unevidenced by construction and the ledger is the only surface on which a diagram's claims can be recorded at all."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.9
  - statement: "Diagram-as-text satisfies ADR-0028's reviewability requirement in a way an image file cannot, because every edge a fence asserts appears as reviewable text in the pull-request diff."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.9
  - statement: "Human review of the pull-request diff is the only enforcement a diagram has, which is the same mechanism ADR-0028 states the corpus as a whole depends on."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.85
  - statement: "This node declares no relationships because of merge order rather than an empty corpus: corpus-agents is loadable from this branch and absent from the merge target, where an unmatched relationship target is a hard error."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "git_ls_tree(ref=origin/launchpad, path=launchpad/docs/corpus) -> schema only"
    confidence: 0.95
  - statement: "Issue #1312's definition of done requires this node to state scope and authority, separate MUST requirements from SHOULD guidance, define enforcement and an exception or escalation process, and link decisions instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1312 definition of done"
  - statement: "The generated-content standard, including how a generated artifact proves its provenance and the exception process for one, is #1316's to write."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1316"
  - statement: "Extending staleness detection to canonical documentation corpus nodes is #556's to build."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#556"
  - statement: "The validator accepting a path-and-line citation whose line does not exist is a known defect tracked as #1459."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1459"
  - statement: "Node classification and taxonomy is #1324's subject, and the evidence standard is #1314's."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1324 and launchpad-26/buzz#1314"
---

# Diagrams in corpus nodes

## 1. What this standard governs

## 2. Authority and scope

## 3. What form a diagram takes

## 4. When a node carries a diagram

## 5. What evidence a diagram owes

## 6. Keeping a diagram honest

## 7. Enforcement, and what no check can see

## 8. Exceptions and escalation

## 9. Scope, omissions, and what was not verified
