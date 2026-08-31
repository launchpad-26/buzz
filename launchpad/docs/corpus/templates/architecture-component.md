---
id: corpus-template-architecture-component
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template or policy."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's existing meta-documents, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states part-of's directionality as 'source is a constituent section/child of target', with a generated inverse named has-part."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents architecture subject matter."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The C4 model defines a component as 'a grouping of related functionality encapsulated behind a well-defined interface', built from code-level building blocks (classes and interfaces, files, modules, or their language-appropriate equivalent), and states explicitly that components are not separately deployable units -- the container is the deployable unit, and all of its components execute in the same process space."
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/component"
  - statement: "The C4 model's Component diagram lets an author 'zoom in and decompose a container to describe the components that reside inside it; including their responsibilities and the technology/implementation details', is aimed at software architects and developers, and the model advises creating one only 'if you feel they add value'."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams/component"
  - statement: "The C4 model describes its Code diagram as 'very much an optional level of detail', 'not recommended for anything but the most important or complex components', and 'not recommended for long-lived documentation because most IDEs can generate this level of detail on demand'."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams/code"
  - statement: "The C4 model presents four hierarchical levels of abstraction -- software systems, containers, components, and code -- with a corresponding diagram at each level, and Simon Brown is named as its author."
    entry_class: FACT
    evidence:
      - "https://c4model.com/"
  - statement: "arc42 section 5, the Building Block View, documents 'the static decomposition of the system into building blocks ... as well as their dependencies', using a hierarchical whitebox/blackbox form: a Level 1 whitebox of the overall system paired with blackbox descriptions of its building blocks, then a Level 2 whitebox zooming into one selected Level 1 block with its own blackbox children, and so on for further levels."
    entry_class: FACT
    evidence:
      - "https://docs.arc42.org/section-5/"
  - statement: "arc42's overview page lists twelve sections in total, states the template is licensed CC BY-SA 4.0, and gives a copyright line of 2003-2026 with no version number anywhere on the page."
    entry_class: FACT
    evidence:
      - "https://arc42.org/overview"
  - statement: "An unmerged research note frames the C4 model as 'diagrams, not prose' that 'slots into arc42 §3/§5/§7 rather than competing with it'."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates)"
  - statement: "Grouping the three architecture template issues (#1326 component, #1327 container, #1328 context) under the C4 model's System Context, Container and Component diagram layers is this corpus-templates batch's own authoring — each issue's stated subject names the C4 layer it corresponds to — not a grouping the research note above states or implies."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1326, launchpad-26/buzz#1327, launchpad-26/buzz#1328 (corpus-templates batch dispatch brief)"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than the MUST/SHOULD/enforcement/escalation checklist that issue #1326's own Definition of Done carries."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent Feature acceptance criteria) and the #1307-#1351 batch dispatch brief, which identified #1326's DoD text as boilerplate copied from the standards-track issues"
  - statement: "Because this template's own subject is a container's internal building blocks and the C4 model defines a component as never separately deployable, a node built from this template should cite the container's source tree for each building block's existence rather than any deployment manifest, since deployment-level evidence corresponds to the container the component lives inside, not to the component itself."
    entry_class: INFERENCE
    evidence:
      - "https://c4model.com/abstractions/component"
    confidence: 0.7
  - statement: "part-of is the relationship type a node built from this template should declare toward the architecture-container node it decomposes, because the C4 model defines a component as residing inside exactly one container and relationships.schema.json defines part-of as 'source is a constituent section/child of target', which matches that containment relationship more closely than any of the schema's other four types."
    entry_class: INFERENCE
    evidence:
      - "https://c4model.com/abstractions/component"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
    confidence: 0.6
  - statement: "This template directs authors of an architecture-component node to set type: architecture, since node.schema.json defines that enum member as 'the corpus surface this node documents' and offers no finer-grained member distinguishing a component-level node from a container- or context-level one, so all three share the single surface value."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "GitHub's own documentation states that diagram rendering from a fenced Mermaid code block is available natively in Markdown files, GitHub Issues, GitHub Discussions, pull requests and wikis, with no external tooling required."
    entry_class: FACT
    evidence:
      - "https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams"
  - statement: "At the recorded revision, exactly one other Markdown file anywhere in this repository (launchpad/Research/hardening-linux-servers.md, itself a research note rather than an accepted standard) uses a fenced mermaid code block, so Mermaid is this template's own recommendation for the required component diagram rather than an established repository-wide convention this node is merely following."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='```mermaid', scope='**/*.md') -> 2 matches: launchpad/docs/corpus/templates/architecture-component.md (this node) and launchpad/Research/hardening-linux-servers.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
---

# Template: architecture-component

How to write a corpus node whose subject is the internal building blocks of one
container: what the node must contain, what evidence it needs, and the industry
model it adapts. This is a template node, not a policy node -- it prescribes the
shape of a future document rather than a MUST/SHOULD rule about corpus-wide
behavior. See *Note on Definition of Done* below for why that distinction matters
for this specific node.

## Scope and authority

**This node covers** what a corpus node documents when its subject is
"architecture-component" -- the internal building blocks inside a single
container, one level below the container itself and one level above source
code. It states the required sections such a node's body must carry, the
evidence expectations for the claims it makes, and the industry model it
adapts.

**It does not cover** the front-matter contract itself (`node.schema.json`
governs that, unconditionally, for every node type), how to create/update/retire
a node procedurally (`AGENTS.md` governs that), or the sibling architecture
surfaces -- context and container -- which are separate templates with their own
tasks. See *Scope and omissions* for the full boundary.

**Its authority is derived, not original.** The structural half is already
law: `node.schema.json` enforces front matter, `validate.py` runs that schema,
and CI runs `validate.py` on every corpus change. What this node adds is the
half no schema can hold -- which sections a component-level architecture node
needs, what evidence backs a building-block claim, and which industry model
grounds the whole shape. That half is enforced by review, the same way the
existing corpus standards describe their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| The industry model this template adapts | *Industry model* below, and the primary sources it cites |

If this node and any of those disagree, **they win** -- this one has drifted
and should be fixed.

## Industry model this template adapts

**C4 model, Component diagram** (Simon Brown, undated, `c4model.com`) -- the
third of C4's four hierarchical levels (system, container, component, code).
A component is *"a grouping of related functionality encapsulated behind a
well-defined interface"*, built from real code-level building blocks
appropriate to the language (classes and interfaces, files, modules).
Components are explicitly **not** separately deployable: the container is the
deployable unit, and every component inside it runs in the same process
space. The Component diagram *"zoom[s] in and decompose[s] a container to
describe the components that reside inside it; including their
responsibilities and the technology/implementation details"*, and is written
for software architects and developers. C4 also states plainly that a
Component diagram is optional -- create one *"only if you feel [it adds]
value"* -- which is why this template requires the diagram only when a
container's internal structure is not already obvious from its container-level
documentation.

**arc42 §5, Building Block View** (`arc42.org`, CC BY-SA 4.0, © 2003-2026, no
version number) -- the architecture template C4 slots into rather than
competes with. §5 documents *"the static decomposition of the system into
building blocks ... as well as their dependencies"*, using a hierarchical
whitebox/blackbox form: a whitebox of the whole system paired with blackbox
descriptions of its immediate building blocks, then a further whitebox zoom
into one of those blocks with its own blackbox children, repeated as deep as
the documentation needs to go. A component-level corpus node corresponds to
one arc42 Level 2 (or deeper) whitebox: the container is the Level 1 blackbox
being opened, and this node's components are the blackbox children exposed at
that level.

**Why both, together.** An unmerged research note (`launchpad-26/buzz#1466`,
cited as `TEAM_KNOWLEDGE` above because it is not an accepted decision)
observes that C4 is *"diagrams, not prose"* and *"slots into arc42 §3/§5/§7
rather than competing with it"*. That is the shape this template follows: the
diagram supplies the notation, arc42 supplies the prose discipline
(whitebox/blackbox, dependencies, justification for the decomposition) that a
bare picture cannot carry on its own. A corpus node that embedded only a
diagram with no traceable prose would fail this corpus's own evidence
contract regardless of which industry model it borrowed the picture from.

## Boundary: what this template is not

Read this section before drafting. The three architecture template tasks in
this batch (`#1326` component, `#1327` container, `#1328` context) map 1:1
onto C4's outer three diagram layers, and the boundary is easy to blur in
either direction:

- **Not architecture-context (`#1328`).** Context is the system boundary and
  its external actors -- who and what talks to the system from outside it.
  A component-level node never shows an external actor directly; it shows
  internal structure one container already exposes to the outside as a
  single box.
- **Not architecture-container (`#1327`).** Container is the set of
  deployable/runnable units (services, databases, apps) and their technology
  choices. A component-level node documents the **inside** of exactly one of
  those units -- it must name which container it decomposes, and it must not
  re-describe the container's own deployment boundary or its sibling
  containers' internals.
- **Not the Code level.** C4's Code diagram is explicitly optional and
  recommended only for the most important or complex components, "not
  recommended for long-lived documentation because most IDEs can generate
  this level of detail on demand." A component-level node names classes,
  functions or modules only as citation evidence for a building block's
  responsibility -- it does not attempt to document a class's internal
  design. That level of detail, if it is ever wanted as corpus content, is
  `#1341`'s ("implementation-reference") concern, not this template's.

A node built from this template that drifts into any of the three above has
picked the wrong template, not merely written a long document.

## Required sections

A corpus node using this template's `type: architecture` must carry the
following in its body, in addition to whatever schema-required front matter
`node.schema.json` demands of every node:

1. **Purpose and scope statement.** One paragraph naming the container being
   decomposed (by its own corpus node id, once the container template and its
   instances exist -- see *Relationships* below) and what question the
   decomposition answers for a reader.
2. **Component diagram.** A C4-notation component diagram as a fenced
   ```` ```mermaid ```` block -- GitHub renders Mermaid diagrams natively in
   Markdown files with no external tooling, which keeps the diagram inside
   the same reviewable pull-request diff ADR-0028 chose Markdown to preserve.
   This template recommends Mermaid on that basis, not because it is an
   established convention elsewhere in this repository -- at the recorded
   revision only one other file uses it, a research note rather than an
   accepted standard. The fence is evidence-bearing content, not decoration.
   Per C4's own guidance, omit the diagram only when the container's
   components are fully enumerable in the table below with no structure a
   picture would add -- and say so explicitly rather than silently dropping
   the section.
3. **Notation legend.** A short table or list mapping every shape/style used
   in the diagram to its meaning, so the diagram is readable without
   already knowing C4. arc42 and C4 both assume shared background knowledge
   the corpus cannot assume of every reader.
4. **Building block table.** One row per component: name, responsibility (one
   sentence), its interface/contract (what other components or the container
   boundary call on it through), and the evidence citation for its existence
   (see *Evidence expectations*).
5. **Boundary statement.** An explicit paragraph naming what this node does
   not cover, using the three exclusions in *Boundary: what this template is
   not* as the checklist, plus any node-specific exclusion the author found.
6. **Relationships**, per the guidance below.
7. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the
   node does not cover, who owns it, and separately, what was expected but
   could not be verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Container name]: component view

[One paragraph: which container this decomposes, and what question the
decomposition answers.]

## Notation legend

| Shape | Meaning |
|---|---|
| ... | ... |

## Component diagram

```mermaid
[C4-style component diagram: the container as the outer boundary, its
components inside, dependencies between them, and the container/actor
boundaries it exposes to the outside as already-decided by the container-level
node]
```

## Building blocks

| Component | Responsibility | Interface | Evidence |
|---|---|---|---|
| ... | ... | ... | path/symbol citation |

## Boundary

This node does not describe:
- [the container's own deployment topology -- see the architecture-container
  node for <container>]
- [external actors -- see the architecture-context node]
- [class/function-level design -- see #1341's implementation-reference
  template, if instantiated for this container]
- [any node-specific exclusion]

## Relationships

- part-of: <the container node's id>
- depends-on: <any component this one requires to be true/current>

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
````

## Evidence expectations

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means the
author opened the cited source, `INFERENCE` means the author reasoned to the
claim and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated
statement attributed to whoever said it. Nothing about this template relaxes
or narrows that. Two expectations follow specifically from the industry model
this template adapts:

- **A building block's existence and responsibility is a `FACT` or nothing.**
  C4 defines a component as made of real code-level building blocks -- classes,
  files, modules -- so a building-block table row naming a responsibility with
  no source citation is asserting a design that may or may not correspond to
  the actual container. Cite the module, package, directory or class the
  reader can open to confirm the row.
- **A diagram element with no matching evidence-ledger claim is an
  unsupported claim wearing a picture.** `validate.py` never inspects a
  diagram's content -- it is Markdown text to the checker like any other. Every
  box and arrow in the required diagram needs to correspond to a claim
  somewhere in the node's evidence ledger and building-block table; a diagram
  that says more than the prose is the failure mode `AGENTS.md`'s own
  evidence section warns about, just expressed as a picture instead of a
  sentence.
- **Do not cite deployment evidence for a component's existence.** Per this
  node's own `INFERENCE` above, a component is not separately deployable, so
  a Kubernetes manifest, a Dockerfile or a process list is evidence about the
  *container*, not about any one component inside it. Cite source, not
  deployment.

## Relationships

A node built from this template:

- **should** declare `part-of` targeting the id of the architecture-container
  node it decomposes, once that node exists and is merged. Per this node's own
  `INFERENCE` above, `part-of`'s schema directionality --
  "source is a constituent section/child of target" -- is the closest match
  among the five defined types to a component's strict containment inside one
  container.
- **may** declare `depends-on` toward another architecture-component node in
  the same or a different container, when one component's claims depend on
  another component currently being true/current.
- **may** declare `references` toward this template node itself (target:
  `corpus-template-architecture-component`) once this node is merged, if the
  author wants the generated `referenced-by` edge; this is optional, since a
  node's use of `type: architecture` and its shape already show which
  template it followed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time),
  never against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes
present in `origin/launchpad`'s corpus tree at the recorded revision --
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` -- are all procedural/meta-documents
about the corpus itself, not architecture subject matter a template about
architecture-component decomposition would `depends-on`, `references`, or
sit `part-of`. None of the four sibling architecture/decision/runbook
templates in this batch (`#1327`, `#1328`, `#1335`, `#1347`) target this node
or are targeted by it, deliberately: all five are authored in parallel with no
merge ordering between them, so an edge to any of them would be as likely to
break in CI as to resolve. The first architecture-component instance node is
the natural moment to add a `references` edge back to this template, once it
exists.

## Note on Definition of Done

Issue `#1326`'s own Definition of Done carries four bullets -- "states scope
and authority/source of the policy," "separates MUST requirements from SHOULD
guidance," "defines enforcement/checks and exception/escalation process,"
"links decisions or higher-order policy instead of duplicating them" -- copied
verbatim from the standards-track issues that produced
`standards/confidence.md` and `standards/decision-references.md`. Those
describe a **policy/standard** node (a MUST/SHOULD normative document over
existing corpus behavior); this node is a **template** (a prescription for the
shape of a future document). The real acceptance criterion, from parent
Feature `#605` itself, is: *"every template states its purpose, required
sections, evidence expectations and the industry model/standard it adapts."*
This node is built against that sentence -- *Required sections*, *Evidence
expectations* and *Industry model this template adapts* above answer it
directly -- rather than against the standards-track checklist, which does not
fit a document with no MUST/SHOULD normative claims about existing system
behavior to separate.

## Scope and omissions

**This node covers** what a corpus node documents when its subject is one
container's internal component decomposition: the required body sections, the
evidence expectations for a building-block claim, the industry model
(C4 Component diagram + arc42 §5) the shape adapts, the explicit boundary
against the context/container/code levels, and the relationship types a node
built from this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The architecture-context template (system boundary, external actors) | `#1328` |
| The architecture-container template (deployable units, technology choice) | `#1327` |
| Code/class-level documentation, if the corpus ever wants it as content | `#1341` (implementation-reference), open and not yet drafted at time of writing |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Whether deployment topology belongs at the container level or a separate template | Flagged as a possible ambiguity against `#1336` ("deployment") by the batch dispatch brief for this task set; not resolved here because it is the container template's boundary to draw, not this one's |

**No relationships declared in this node's own front matter.** See
*Relationships* above for what was checked and why none of the four nodes
that exist on `origin/launchpad` at the recorded revision are a fit.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above
  about what a component-level node needs is grounded in the C4/arc42 primary
  sources and in this batch's sibling-boundary brief, not in a worked
  instance. The first real architecture-component node -- likely one of the
  already-filed `architecture/containers/*` decomposition tasks once a
  container-level node exists for it to point at -- is what will actually
  test whether the required sections above are sufficient or need revision.
- **Whether `#1336` ("deployment") and the architecture-container template
  (`#1327`) actually overlap on deployment topology was not resolved.** This
  node only flags the ambiguity in the table above; drawing that boundary
  belongs to `#1327`, not to this template.
- **Whether Mermaid's component/flowchart notation can faithfully express
  C4's own component-diagram visual language (which uses a specific box/border
  convention beyond what generic Mermaid flowcharts provide) was not checked
  against a rendered example.** This template recommends Mermaid for its
  native GitHub rendering and reviewability, not because it was confirmed to
  reproduce C4's notation exactly; the *Notation legend* requirement exists
  partly to cover that gap.
