---
id: corpus-standard-atomicity
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 60d4947b7145a6ef25f185b9c25d43e43d99de3c."
    entry_class: FACT
    evidence:
      - "commit 60d4947b7145a6ef25f185b9c25d43e43d99de3c"
  - statement: "The corpus instruction node states the atomicity rule in one line -- one node is one independently maintainable idea -- and refers the full treatment to the per-type standards it does not itself carry."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "One authored Markdown file with YAML front matter is one corpus node, so deciding how many nodes a subject becomes is deciding how many files it becomes."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Naming, identifiers, linking, provenance, status, taxonomy, diagrams and evidence each have their own standard task, distinct from this one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "A second concept, contract or procedure discovered while drafting is filed as a separate task rather than folded into the document being written."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1307 definition of done: 'any newly discovered second concept/contract/procedure is filed as a separate task instead of being folded into this document'"
---

# Atomicity

How many corpus nodes a subject becomes, and how an author decides.

## Scope and authority

**This standard governs one question:** given a subject you are about to document,
is it one node or more than one?

That question is worth a standard because the answer is not recoverable later. A
subject wrongly split stays split behind edges that resolve; a subject wrongly merged
stays merged behind an `id` that cannot be renamed. Neither state is detectable by any
check, so the decision is made once, by an author, at the moment of drafting.

**Where the authority comes from.** `launchpad/docs/corpus/AGENTS.md` is the
instruction node for corpus work and states the rule in a line: one node is one
independently maintainable idea. It does not say how to apply it, and refers per-type
standards, including this one, to their own tasks. This node is that treatment. Where
the two disagree, the instruction node is the one an agent is handed, so a
disagreement is a defect in this document and should be fixed here.

**Why "one node" and "one file" are the same question.** ADR-0028 makes Markdown with
YAML front matter the single canonical authored representation of a node, with every
other serialization generated from it. There is no sub-node unit to author into, so
granularity decisions land on file boundaries and nowhere else.

**What this standard does not decide.** Each of these is its own task, and folding one
in here would break the very rule this node states:

| Not decided here | Owned by |
|---|---|
| Which `type` a node takes, and what the surfaces mean | #1324, taxonomy |
| What an `id` looks like and how it is chosen | #1317, identifiers |
| What a node or its file is called | #1319, naming |
| How a node points at another, and in which direction | #1318, linking |
| What MUST, SHOULD and MAY mean as normative keywords | #1320, normative language |
| Whether a node needs a scope section at all, and what belongs in it | #1313, documentation standard |
| How evidence is classified and cited | #1314, evidence |

This node uses MUST and SHOULD in the ordinary normative sense and links #1320 rather
than defining them.
