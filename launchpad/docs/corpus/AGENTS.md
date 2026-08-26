---
id: corpus-agents
type: agent
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 0052f5a7820ca4ca261efa233feb8bb53858ade6."
    entry_class: FACT
    evidence:
      - "commit 0052f5a7820ca4ca261efa233feb8bb53858ade6"
  - statement: "Markdown with YAML front matter is the one canonical authored representation of a corpus node; every other serialization is a generated derived view."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "A node's front matter is validated against node.schema.json, which requires id, type, status, origin, audiences and evidence, and permits no field outside that set."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The corpus root is launchpad/docs/corpus, and validate.py is the deterministic check that governs it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "Justfile"
  - statement: "The schema/ subtree is excluded from validation because it is the schema's own testing infrastructure rather than corpus content."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Evidence precedence is contextual by claim type, and two authoritative sources of the same claim type in conflict leave the node flagged for a human rather than silently resolved."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Citations take six shapes and only three of them name a file that can be opened."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "Citation checking is structural: the validator confirms a cited path resolves to a real file inside the repository, never that the file supports the statement it sits under."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A relationship whose target matches no loaded node's id is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "This file is also resolved as the nearest AGENTS.md for every change under launchpad/docs/corpus, so it is read as governing instructions and not only as a corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/preflight_core.py"
  - statement: "Every change under launchpad/docs/corpus is gated in CI by the corpus validate workflow."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
---

# Working with the documentation corpus

Instructions for creating, updating and retiring one node in
`launchpad/docs/corpus/`. Look up the section you need; this is a reference, not a
tutorial.

**Authoritative sources — this file duplicates none of them:**

| For | Read |
|---|---|
| The front-matter contract (fields, enums, conditional rules) | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose explanation of those fields | `launchpad/docs/corpus/schema/README.md` |
| Adding a value to a closed enum | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Why Markdown + front matter is canonical | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| How to rank conflicting evidence | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The six citation shapes | `launchpad/project-intelligence/CONTRACT.md` §3 |
| What the checker actually enforces | `launchpad/project-intelligence/corpus/validate.py` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## What a corpus node is

**One file is one node.** A node is a Markdown file with YAML front matter, and that
is the single canonical authored representation; anything else — JSON, an index, a
graph serialization — is a generated derived view, never hand-authored.

**One node is one independently maintainable idea.** If a second concept, contract or
procedure turns up while you are writing, it does not get folded in. File it as its
own task and link to it.

**Where it goes.** Anywhere under `launchpad/docs/corpus/`, except `schema/` — that
subtree is the schema's own testing infrastructure and is deliberately skipped by the
checker, so a node placed there is never validated at all.

**Front matter.** Validated against `node.schema.json`. Field names, which fields are
required, the closed enums and the conditional rules between fields all live in that
file and in `schema/README.md`; they are not repeated here, because a second copy
drifts silently — the checker never reads this document's prose, so a stale copy
would stay green forever.

**`id` is permanent.** Kebab-case, assigned once, never renamed. Generated views
derive from it reproducibly, so renaming an id is a migration, not an edit.

**Relationships are optional and must resolve.** A `relationships[].target` naming an
id no node in the corpus carries is a hard error. A node with no sibling to point at
correctly declares none.

**Authored versus generated.** Every non-`.md` file under the corpus root must live
in a `generated/` directory. Today the checker rejects such files even there, because
no generator exists yet to reproduce them from canonical Markdown, and a hand-written
file in `generated/` is indistinguishable from a real projection. That contract is
owned by #1316; until it lands, a corpus change adds Markdown only.

## Evidence, citations, and what validation proves

## Creating a node

## Updating a node

## Retiring a node

## Scope and omissions
