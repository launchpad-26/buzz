---
id: corpus-template-capability
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and capabilities is one of them, distinct from architecture, interfaces-events and operations; none of the thirteen is template or policy, because the enum names the corpus surface a node documents, not the prose form its body takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "schema/README.md's own prose table restates the same thirteen-value list for the `type` field with no further elaboration of what distinguishes `capabilities` from its neighbors -- the enum member exists, but nothing in the schema or its prose companion defines the boundary a capability-shaped node must hold."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "Of the corpus's four nodes merged to origin/launchpad at the recorded revision, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance -- the precedent for a node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content, the same precedent the interface and architecture-component templates in this same task family cite for their own type: governance choice."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states part-of's directionality as 'source is a constituent section/child of target', implements' as 'source is the concrete realization of target (e.g. a template instance of a standard)', and references' as 'source cites target as supporting context; no ownership or currency dependency implied'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Parent Feature #602's success criteria list the corpus's in-scope surfaces as a single combined item -- 'architecture, layers, capabilities, platforms, implementation, interfaces/events, verification, operations, development, release, governance, agent and ingestion' -- naming capabilities as its own surface, not folded into architecture or interfaces/events the way interfaces and events were combined into one surface."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 success criteria (read directly via gh issue view; AGENTS.md requires an issue-URL-only citation to stay TEAM_KNOWLEDGE, not be promoted to FACT, since the validator can only report it UNVERIFIED and issue content is mutable GitHub state, not committed code)"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1329's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria (read directly via gh issue view; same TEAM_KNOWLEDGE-not-FACT rule as above applies)"
  - statement: "Issue #1329's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text the batch dispatch brief for this task set independently found copied across #1326-#1351."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1329 Definition of Done (read directly via gh issue view; same TEAM_KNOWLEDGE-not-FACT rule as above applies)"
  - statement: "Root VISION_PROJECTS.md's own 'Status' section is headed by a two-column table literally titled 'Capability | Status', listing eleven rows -- among them 'Channels, forums, DMs, canvases', 'Workflow engine (triggers, traces, conditional logic)', 'MCP server + ACP agent harness', 'Blossom media storage (SHA-256, S3)', 'Approval gates', 'Git hosting (smart HTTP + NIP-34)' -- each marked Ships today, in-progress, or Designed, describing what the product can do at a product/feature level rather than how any of it is built."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-259"
  - statement: "Root VISION_MODERATION.md states 'Authority is structured as capabilities, so adding a moderator tier later is a policy change, not a rewrite,' a second, independent repo-native use of 'capability' as a product-level unit of what the system can do, distinct from its own internal architecture."
    entry_class: FACT
    evidence:
      - "VISION_MODERATION.md:57"
  - statement: "Root AGENTS.md's 'Prefer Nostr events over new HTTP endpoints' section directs new feature work toward modeling an operation as a Nostr event kind rather than a new HTTP endpoint, and its 'Key Patterns' section overall describes implementation conventions (event kinds, channel scoping, workflow conditions) rather than naming or cataloguing product capabilities -- confirming this repository's own root docs do not already maintain a capability catalogue outside VISION_PROJECTS.md's Status table."
    entry_class: FACT
    evidence:
      - "AGENTS.md:143-185"
  - statement: "A Guide to the Business Architecture Body of Knowledge (BIZBOK Guide), Part 1: Introduction, freely distributed by the Business Architecture Guild without membership or login, states: 'a business is broken down into business units, each of which has certain capabilities. Capabilities enable stages within various value streams and require certain information,' and illustrates capabilities as stable over long timeframes with the example 'a 100-year-old insurance company would have had similar capabilities as it does today: Customer Management, Insurance Policy Management, and Claims Management' -- named as noun phrases, not verbs or processes."
    entry_class: FACT
    evidence:
      - "https://cdn.ymaws.com/www.businessarchitectureguild.org/resource/resmgr/bizbok_10/introduction_v10_final.pdf"
  - statement: "The BIZBOK Guide's own formal Business Capability Model chapter -- which would carry the Guild's precise capability definition, capability levels, and capability heat-map notation -- sits behind Business Architecture Guild membership, not in the freely distributed Part 1: Introduction excerpt this node was able to read directly."
    entry_class: FACT
    evidence:
      - "https://cdn.ymaws.com/www.businessarchitectureguild.org/resource/resmgr/bizbok_10/introduction_v10_final.pdf"
  - statement: "The Open Group's TOGAF Standard business-capabilities page (pubs.opengroup.org/togaf-standard/business-architecture/business-capabilities.html) redirects unauthenticated requests to an OAuth login at identity.opengroup.org, so TOGAF's own capability definition and its capability-mapping guidance were not read directly for this node -- a blocker of the same shape #1348 (specification template) hit and documented when iso.org blocked every fetch of ISO/IEC/IEEE 29148:2018."
    entry_class: FACT
    evidence:
      - "https://pubs.opengroup.org/togaf-standard/business-architecture/business-capabilities.html"
  - statement: "An unmerged research note (launchpad/Research/project-documentation-templates.md, PR #1466, branch docs/research-project-doc-templates) discusses Diataxis's four forms and The Good Docs Project's templates as its main subject matter, and a case-insensitive grep of that note's full text for 'capabilit' returns zero matches -- neither #1329 nor any capability-shaped topic is covered by it."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('capabilit', path='launchpad/Research/project-documentation-templates.md', ref='b0553469d9dff25eb3636ce1d0400e60dca1b559') -> zero matches, run 2026-08-27 against the docs/research-project-doc-templates branch tip"
  - statement: "Issue #1338 (flow) is not part of this task batch and was not opened or read while drafting this node; its scope is inferred only from the batch dispatch brief's own one-line description -- 'how a capability plays out step-by-step' -- which this node treats as a boundary to state, not as a claim about #1338's actual drafted content."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch brief for #1329/#1333/#1334/#1343/#1348 (BRIEF4.md), section 5"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four is capability-shaped subject matter, and none of the batch-1/batch-2/batch-3 template PRs (#1527-#1543) nor this batch's own siblings (#1333, #1334, #1343, #1348) are merged, so none of them are valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
---

# Template: capability

How to write a corpus node documenting one **capability** -- a named thing the
product can do for its users, stated at the level VISION_PROJECTS.md's own
"Capability | Status" table already states them (for example "Git hosting", "Approval
gates", "Workflow engine"), distinct from the architecture that implements it, the
interfaces that expose it, and the step-by-step flow one interaction through it takes.
This is a template node, not a policy node -- it prescribes the shape of a future
document's *body*, not a MUST/SHOULD rule about corpus-wide behavior. See *Note on
Definition of Done* for why that distinction matters for this specific node.

## Scope and authority

**This node covers** what a corpus node's body must contain when it documents one
capability: the required sections, the evidence expectations for a capability claim,
and the industry model considered (and how far it could be verified).

**It does not cover**:
- The front-matter contract itself (`node.schema.json` governs that, unconditionally,
  for every node type) or how to create/update/retire a node procedurally
  (`AGENTS.md` governs that).
- How a capability is built -- the containers, components and technology choices that
  realize it. That is the architecture family's territory (`#1326` component, `#1327`
  container, `#1328` context), all three following the C4 model.
- The boundary contract a capability is exposed through -- a CLI command group, an
  HTTP route group, a protocol surface. That is `#1342`'s template (interface).
- The step-by-step path one interaction through a capability takes. That is `#1338`
  (flow), not in this batch. See *Boundary* below for the exact line.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. What this node adds is the half no schema can
hold -- which sections a capability-shaped node needs, what evidence backs a
capability claim, and what industry model was checked before this template's
structure was decided. That half is enforced by review, the same way the existing
corpus standards describe their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| How a capability is built | `#1326`/`#1327`/`#1328`'s templates (architecture) |
| The boundary contract exposing a capability | `#1342`'s template (interface) |
| The step-by-step path through a capability | `#1338` (flow, not yet drafted) |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model considered, and what could and could not be verified

**Business Architecture Guild's BIZBOK Guide is the closest fit, partially read.**
Its freely distributed Part 1: Introduction -- no membership or login required --
states the same "what, not how" idea this repository's own VISION_PROJECTS.md
independently uses: "a business is broken down into business units, each of which
has certain capabilities. Capabilities enable stages within various value streams and
require certain information." It illustrates capabilities as **stable over long
timeframes**, using a hundred-year-old insurance company whose capabilities --
Customer Management, Insurance Policy Management, Claims Management -- would have
existed in some form throughout, even before any of today's automation. Capabilities
are named as noun phrases, never verbs -- the same shape VISION_PROJECTS.md's own
rows take ("Git hosting", not "Host git repositories").

**The Guide's formal capability chapter was not reached.** The precise capability
definition, capability levels (the Guild's leveled decomposition of a capability into
sub-capabilities), and capability heat-map notation live in the BIZBOK Guide's later
Business Capability Model chapter, which sits behind Business Architecture Guild
membership -- outside the freely distributed introduction this node could read
directly. This template therefore borrows BIZBOK's *habit* (name what the business
can do, as a stable noun, independent of how it is currently implemented), not its
full leveled notation, which was never read.

**TOGAF was checked and could not be read at all.** The Open Group's own TOGAF
Standard page for business capabilities redirects an unauthenticated request straight
to an OAuth login wall. No TOGAF wording appears anywhere in this node as a result --
this is the same shape of blocker `#1348` (specification template) documented for
ISO/IEC/IEEE 29148:2018, and this node follows the same rule: do not cite a source
secondhand because a paraphrase of it is easy to find. If TOGAF's own text becomes
readable later, this node's *Industry model considered* section is the place to
revisit, not a reason to guess at its content now.

**What this template adapts.** Not a leveled capability-mapping notation, but the
"what, not how" discipline both BIZBOK's readable introduction and this repository's
own VISION_PROJECTS.md independently demonstrate: a capability node names something
the product can do, in language a user or product stakeholder would recognize,
without describing the components, containers or protocol details that currently
implement it -- those get cited as evidence of the capability's existence, not
folded into the capability's own description.

## A note on `type`

Unlike `#1342`'s `interfaces-events` (a single enum value standing in for two
combined PRD #602 surfaces), `node.schema.json`'s `capabilities` enum member is
capability's own dedicated value -- PRD #602's success criteria list `capabilities`
as its own item, not merged with `architecture` or `interfaces/events`. A node built
from this template therefore carries `type: capabilities`, with no combination or
disambiguation needed at the front-matter level; the disambiguation this node exists
to make is entirely in body content and the *Boundary* section below, since
`schema/README.md`'s own prose table gives `capabilities` no further elaboration
beyond restating the enum. This template node itself carries `type: governance`
because it documents the corpus's own authoring rules, per the precedent in the
evidence ledger above, not because capability-shaped instance nodes in general use
`governance`.

## Boundary: what this template is not

Read this section before drafting.

- **Not architecture (`#1326`/`#1327`/`#1328`, component/container/context).** Those
  three document *how* a system is built, following the C4 model's outer three
  layers. A capability node never contains a component diagram, a deployment
  topology, or a technology choice as its own subject matter -- it may `references`
  the architecture node(s) that realize it, but its own body stays at the level a
  product stakeholder, not an engineer, would recognize. A node that spends most of
  its body describing containers or components has picked the wrong template.
- **Not interface (`#1342`).** An interface node documents the boundary a capability
  is exposed through -- a CLI command group, an HTTP route group, a protocol
  surface. A single capability can be exposed through more than one interface (for
  example, "Git hosting" is reachable through both `buzz-cli`'s subcommands and the
  relay's git smart-HTTP routes), and a single interface can expose more than one
  capability. A capability node names *what the product can do*; it `references` the
  interface node(s) that expose it rather than re-describing their operations.
- **Not flow (`#1338`, not in this batch).** Per the batch dispatch brief for this
  task set, a flow node documents how a capability plays out step-by-step -- the
  path one interaction through it takes. A capability node states that the product
  can do the thing; it does not narrate the sequence of steps a user or agent takes
  to do it. This boundary is stated on the brief's own description of `#1338`, not
  on a reading of that issue itself, which was not opened while drafting this node
  (see the evidence ledger).
- **Not operations.** `node.schema.json`'s `operations` enum value covers how the
  running system is operated -- deployment, monitoring, incident response. A
  capability node describes what the product does for its users, not how the team
  keeps it running.

A node built from this template that drifts into any of the four above has picked
the wrong template, not merely written prose that needs tightening.

## Required sections

A corpus node using this template's `type: capabilities` must carry the following in
its body, in addition to whatever schema-required front matter `node.schema.json`
demands of every node:

1. **Capability statement.** One paragraph naming the capability as a product
   stakeholder would recognize it (a noun phrase, per the industry model above --
   "Git hosting", not "Hosting git repositories"), and what a user or agent can do
   because it exists.
2. **Maturity.** Where the capability currently stands -- shipped, in progress, or
   designed but not built -- grounded in a cited source (code, a merged PR, a
   VISION document's own status marker) rather than assumed. This is a statement
   about the *capability's* product maturity, and is a distinct concept from the
   corpus node's own front-matter `status` field, which describes the *document's*
   authoring state (draft/active/deprecated/retired/flagged) and says nothing about
   whether the capability itself has shipped. Do not let one stand in for the other.
3. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the four exclusions in *Boundary: what this template is not* as the
   checklist (not how it's built; not the interface it's exposed through; not the
   step-by-step flow through it; not how it's operated), plus any node-specific
   exclusion the author found.
4. **Relationships**, per the guidance below.
5. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Capability name]: capability

[One paragraph: what the product can do because this capability exists, stated as a
product stakeholder would recognize it, not as an implementation description.]

## Maturity

[Shipped / in progress / designed. Cite the source -- code, a merged PR, a VISION
document's own status marker -- that establishes this, not an assumption.]

## Boundary

This node does not describe:
- [how the capability is built -- see the architecture node(s) for <container/
  component>, if one exists]
- [the interface(s) the capability is exposed through -- see the interface node
  for <interface>, if one exists]
- [the step-by-step flow through this capability -- see the flow node for
  <flow>, if one exists]
- [any node-specific exclusion]

## Relationships

- references: <architecture node(s) that realize this capability, if any>
- references: <interface node(s) that expose this capability, if any>

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
author opened the cited source, `INFERENCE` means the author reasoned to the claim
and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement
attributed to whoever said it. Nothing about this template relaxes or narrows that.
Two expectations follow specifically from the industry model considered above:

- **A maturity claim is a `FACT` or nothing.** "Shipped" needs the code, test, or
  merged PR that shipped it; "designed" needs the document that designed it and no
  more. A capability node asserting maturity from impression rather than a citation
  is exactly the unverifiable-claim problem a status marker exists to prevent --
  VISION_PROJECTS.md's own Status table is itself citable evidence for a capability
  whose maturity it already records.
- **Do not restate an architecture or interface node's content instead of citing
  it.** When a capability's implementation is already documented by an architecture
  node, or its exposure by an interface node, cite that node's id in `relationships`
  and let it own that content -- re-describing a container's technology choice or an
  interface's operation list inside a capability node is the same drift this
  template's *Boundary* section exists to prevent, one document at a time.

## Relationships

A node built from this template:

- **may** declare `references` toward one or more architecture nodes (`#1326`/
  `#1327`/`#1328`'s templates) that realize this capability, when they exist.
  `relationships.schema.json` states `references`' directionality as "source cites
  target as supporting context; no ownership or currency dependency implied" -- the
  loose coupling a capability-to-architecture pointer needs, since the capability
  stays true even as its implementation is refactored underneath it.
- **may** declare `references` toward one or more interface nodes (`#1342`'s
  template) that expose this capability, for the same reason.
- **may** declare `part-of` toward a broader capability this one is a constituent
  piece of, when one exists, per `relationships.schema.json`'s "source is a
  constituent section/child of target" directionality.
- **may** declare `implements` toward this template node itself (target:
  `corpus-template-capability`), once this node is merged, if the author wants the
  generated `implemented-by` edge -- optional, since a node's own shape (Capability
  statement / Maturity / Boundary) already shows which template it followed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes present
in `origin/launchpad`'s corpus tree at the recorded revision -- `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`
-- are all procedural/meta-documents about the corpus itself, not capability-shaped
subject matter this template about capability documentation would `references`,
`implements`, or sit `part-of`. None of this batch's four sibling templates
(`#1333`, `#1334`, `#1343`, `#1348`) target this node or are targeted by it,
deliberately: all five are authored in parallel with no merge ordering between them,
so an edge to any of them would be as likely to break in CI as to resolve. The first
capability-shaped instance node is the natural moment to add a `references` or
`implements` edge back to this template, once it exists.

## Note on Definition of Done

Issue `#1329`'s own Definition of Done carries the same four bullets found copied
across `#1326`-`#1351` -- "states scope and authority/source of the policy,"
"separates MUST requirements from SHOULD guidance," "defines enforcement/checks and
exception/escalation process," "links decisions or higher-order policy instead of
duplicating them" -- verbatim from the standards-track issues that produced
`standards/confidence.md` and `standards/decision-references.md`. Those describe a
**policy/standard** node (a MUST/SHOULD normative document over existing corpus
behavior); this node is a **template** (a prescription for the shape of a future
document's body). The real acceptance criterion, from parent Feature `#605` itself,
is: *"every template states its purpose, required sections, evidence expectations
and the industry model/standard it adapts."* This node is built against that
sentence -- *Required sections*, *Evidence expectations* and *Industry model
considered, and what could and could not be verified* above answer it directly --
rather than against the standards-track checklist, which does not fit a document
with no MUST/SHOULD normative claims about existing system behavior to separate.

## Scope and omissions

**This node covers** what a corpus node's body must contain when it documents one
capability: the required sections, the evidence expectations for a capability or
maturity claim, the industry model considered (BIZBOK's freely readable
introduction, and TOGAF's login-gated page that could not be read at all), the habit
adapted from BIZBOK instead of a full leveled notation, the explicit boundary
against the architecture, interface, flow and operations neighbors, the note that
`type: capabilities` is its own dedicated PRD #602 surface with no combination
needed (unlike `interfaces-events`), and the relationship types a node built from
this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How a capability is built (containers, components, technology) | `#1326`/`#1327`/`#1328` (architecture templates) |
| The boundary contract a capability is exposed through | `#1342` (interface template) |
| The step-by-step path through a capability | `#1338` (flow, not yet drafted) |
| How the running system is operated | the `operations` corpus surface |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**
- **No corpus node instance has yet been drafted from this template.** Every
  required section and the skeleton above is validated only against this
  repository's own VISION_PROJECTS.md Status table and against the freely readable
  portion of BIZBOK, not against a real capability instance node passing
  `validate.py` end to end. The first capability node drafted from this template may
  surface a required section that does not fit every capability shape cleanly.
- **TOGAF's own business-capability text was never read**, only searched for and
  found to redirect to a login wall -- this node makes no claim about what TOGAF
  says beyond that it could not be reached.
- **BIZBOK's formal Business Capability Model chapter (capability levels, heat-map
  notation, the Guild's precise capability definition) was not read**, because it
  sits behind Business Architecture Guild membership outside the freely distributed
  Part 1: Introduction this node cites. This template's "what, not how" habit is
  drawn from that introduction alone, not from the fuller model.
- **`#1338` (flow) was not opened.** Its boundary against this template is stated
  from the batch dispatch brief's one-line description of it, not from reading the
  issue directly -- see the `TEAM_KNOWLEDGE` evidence entry above.
