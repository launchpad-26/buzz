---
id: corpus-readme
type: governance
status: active
origin: launchpad
audiences:
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 60d4947b7145a6ef25f185b9c25d43e43d99de3c."
    entry_class: FACT
    evidence:
      - "commit 60d4947b7145a6ef25f185b9c25d43e43d99de3c"
  - statement: "Markdown with YAML front matter is the one canonical authored representation of a corpus node; every other serialization is a generated derived view."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The corpus root is launchpad/docs/corpus, and validate.py is the deterministic check that governs it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "Justfile"
  - statement: "The schema/ subtree is excluded from validation because it is the schema's own testing infrastructure rather than corpus content, so a node placed there is never checked."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A node's front matter is validated against node.schema.json, which requires id, type, status, origin, audiences and evidence, additionally permits relationships, and rejects any field beyond those seven."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "AGENTS.md is the corpus's agent-facing instruction node, carrying the create, update and retire procedures, and it is also resolved as the nearest AGENTS.md for every change under launchpad/docs/corpus."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/scripts/preflight_core.py"
  - statement: "At the recorded revision the corpus held exactly one authored node -- AGENTS.md, which records in its own scope section that it is still the only one -- so this node is the second."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "discover_markdown_files('launchpad/docs/corpus') -> AGENTS.md only"
  - statement: "The corpus is the subject of feature #605, whose child tasks author the remaining standards, templates and instruction documents, none of which have merged."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/AGENTS.md"
---

# The Buzz documentation corpus

The canonical, evidence-backed documentation of the Buzz system, written as one
node per idea. This page is the door: it says what the corpus is, what is in it
today, where each rule actually lives, and how the whole thing is checked.

It is a map, not a manual. Nothing here restates a rule that is written down
somewhere else — every rule below is a link to the file that owns it, because the
checker never reads this page's prose and a second copy of a rule stays green
forever after it goes stale.

**If you are an agent, you want
[`launchpad/docs/corpus/AGENTS.md`](AGENTS.md), not this page.** That node carries
the create, update and retire procedures, and it is what an agent harness resolves
as the nearest `AGENTS.md` for any change under this directory.

## What a node is

One file is one node: a Markdown file with YAML front matter. That is the single
canonical authored representation of everything in the corpus — JSON, indexes and
graph serializations are generated derived views, never hand-authored. The front
matter carries the machine-checkable fields and the body carries the prose.

One node is one independently maintainable idea. A second concept, contract or
procedure discovered while writing becomes its own node, not another section.

## What is in the corpus today

Two things, and the difference between them matters:

| Path | What it is | Validated as a node? |
|---|---|---|
| [`launchpad/docs/corpus/AGENTS.md`](AGENTS.md) | The agent-facing instruction node — how to create, update and retire a node | Yes |
| [`launchpad/docs/corpus/README.md`](README.md) | This page — the human-facing entry point | Yes |
| [`launchpad/docs/corpus/schema/`](schema/README.md) | The front-matter contract, its fixtures and its tests | **No** — deliberately excluded |

That is the whole corpus. Two authored nodes.

**This is a corpus under construction, and the emptiness is the current state
rather than an omission.** Feature #605 owns building it out: forty-five further
standards, templates and instruction documents are tracked as its child tasks, and
at the recorded revision none of them had merged. Expect this table to grow and
expect the shape of a node to be tightened by standards that do not exist yet.
