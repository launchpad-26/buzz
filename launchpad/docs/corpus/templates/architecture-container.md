---
id: corpus-template-architecture-container
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
  - statement: "A node's front matter is validated against node.schema.json, whose type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every other corpus meta-document at the recorded revision — AGENTS.md excepted, which is type: agent — uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "schema/README.md and schema/COMPATIBILITY.md were both read in full while choosing this node's type, and neither names a template-specific or policy-specific value; COMPATIBILITY.md's only content is the v1 history entry for issue #622 and the additive-change rule, with no enum discussion of its own beyond what node.schema.json already states."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "This node is a meta-document about how to author a corpus node, not itself architecture, capability or other content, so governance is chosen by the same reasoning corpus-readme already recorded for its own type choice, rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.6
  - statement: "A corpus node instance actually written from this template — a real architecture-container document about a real system — takes type: architecture, because that value is one of PRD #602's enumerated corpus surfaces and this template's subject (containers) sits under it; this template document itself is not such an instance."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.8
  - statement: "Relationships must resolve against the corpus tree on the branch being merged into, and at the recorded revision origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is excluded from validation."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
  - statement: "None of the four existing content nodes has architecture, C4, arc42, containers or templates as its subject, so no relationships.target among them would be a substantive edge rather than a citation duplicate of what this node's evidence ledger already cites directly."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.8
  - statement: "C4's abstractions page for 'container' opens with an explicit disambiguation before defining the term: 'Not Docker! In the C4 model, a container represents an application or a data store,' distinguishing the model's own vocabulary from the Docker/OCI container runtime technology that shares the same word."
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/container"
  - statement: "In the C4 model, a container represents an application or a data store — a runtime boundary around some code that is being executed or some data that is being stored, and something that needs to be running for the overall software system to work; examples given include server-side and client-side applications, desktop and mobile apps, serverless functions, databases and blob stores."
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/container"
  - statement: "The C4 Container diagram zooms in on the system boundary to show the high-level shape of the software architecture, how responsibilities are distributed across it, the major technology choices, and how the containers communicate with one another; its audience is technical people inside and outside the development team, including architects, developers and operations/support staff."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams/container"
  - statement: "The C4 Container diagram explicitly says very little about deployment aspects such as clustering, load balancers, replication or failover, because those vary across environments, and states that a separate deployment diagram should capture that information instead."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams/container"
  - statement: "The C4 Deployment diagram illustrates how instances of software systems and/or containers in the static model are deployed onto infrastructure within a given deployment environment (e.g. production, staging), showing deployment nodes and infrastructure nodes such as DNS services, load balancers and firewalls; it is a distinct, separately named diagram from the Container diagram, not a section within it."
    entry_class: FACT
    evidence:
      - "https://c4model.com/diagrams/deployment"
  - statement: "The C4 model's hierarchical core diagrams are, in order: System Context, Container, Component and Code, with System Landscape, Dynamic and Deployment named as separate supporting diagrams rather than members of that core hierarchy."
    entry_class: FACT
    evidence:
      - "https://c4model.com/"
  - statement: "C4's abstractions page for 'component' defines a component as 'a grouping of related functionality encapsulated behind a well-defined interface,' executing inside a container's shared process space rather than being a separately deployable unit; its FAQ, addressing whether a Java JAR, C# assembly, DLL, module, package, namespace or folder is a component, answers 'Perhaps but, again, typically not,' because the C4 model is about showing runtime units (containers) and how functionality is partitioned across them (components) rather than organisational units such as modules, packages, namespaces or folder structures."
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/component"
  - statement: "C4's abstractions page for 'component' distinguishes the Code level (classes, interfaces, functions and other language-specific constructs) from the Component level (groupings of related code elements), stating a component is 'a way to step up one level of abstraction from the code-level building blocks' — so classes exist at C4's Code level, not its Component level."
    entry_class: FACT
    evidence:
      - "https://c4model.com/abstractions/component"
  - statement: "arc42's overview page states section 5, Building Block View, as 'Structure of source code, modularization, hierarchically refined,' describing it as usually the most extensive section of an architecture documentation; it states section 3, Context & Scope, as 'External systems and interfaces,' and section 7, Deployment View, as 'Hardware, infrastructure and deployment' — three separate, non-overlapping sections."
    entry_class: FACT
    evidence:
      - "https://arc42.org/overview"
  - statement: "arc42's Building Block View documentation defines Level 1 as the overall system shown as a whitebox with all top-level building blocks shown as blackboxes, and Level 2 as zooming into a selected Level 1 block and treating it as a whitebox with its own internal blackboxes — a hierarchy of at least two refinement steps within section 5 alone."
    entry_class: FACT
    evidence:
      - "https://docs.arc42.org/section-5/"
  - statement: "A C4 Container diagram's top-level containers correspond to arc42 section 5's Level 1 whitebox decomposition of the whole system, and C4's Component diagram corresponds to arc42's Level 2 zoom into one such building block; arc42 itself does not name 'container' or 'component' as its own vocabulary, so this correspondence is a mapping between the two models' language rather than a claim either model asserts about the other."
    entry_class: INFERENCE
    evidence:
      - "https://c4model.com/"
      - "https://docs.arc42.org/section-5/"
    confidence: 0.6
  - statement: "The research note at launchpad/Research/project-documentation-templates.md, on unmerged PR #1466, describes the C4 model generically as 'System context diagram · Container diagram · Component diagram · Code diagram,' cites C4 as 'diagrams, not prose' that 'slots into arc42 §3/§5/§7 rather than competing with it,' and separately notes arc42 is 'too heavy for a component' with the recommendation to 'lift only §5/§9' for a component-scale document. The note is issue-agnostic: it contains zero issue-number references (confirmed by `grep -coE '#[0-9]{3,4}'` against its full text, which returns 0) and does not itself name or group #1326, #1327 or #1328 under any C4 layer."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note)"
  - statement: "Grouping the three architecture template issues (#1326 component, #1327 container, #1328 context) under the C4 model's System Context, Container and Component diagram layers is this corpus-templates batch's own authoring — each issue's stated subject names the C4 layer it corresponds to — not a grouping the research note above states or implies."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1326, launchpad-26/buzz#1327, launchpad-26/buzz#1328 (corpus-templates batch dispatch brief)"
  - statement: "The unmerged research note does not itself discuss the C4 Deployment diagram or the container/deployment boundary at all -- it names only System Context, Container, Component and Code for C4. The boundary this template draws against issue #1336's deployment template therefore rests entirely on the two c4model.com pages fetched directly for this node (see the two FACT entries above citing https://c4model.com/diagrams/container and https://c4model.com/diagrams/deployment), not on anything the note says, so there is nothing here to defer to the note about or to disagree with it on."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note) -- absence claim, confirmed by reading the note's full text via git show origin/docs/research-project-doc-templates:launchpad/Research/project-documentation-templates.md"
  - statement: "Every non-.md file under the corpus root is rejected by validate.py today, including one placed under a generated/ directory, because no generator exists yet to reproduce it from canonical Markdown, so a corpus change may add Markdown only until issue #1316 lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Because the corpus accepts Markdown only and not a linked or embedded external image file, a Container diagram authored into a corpus node under this template must be expressed as text inside the Markdown body — for example a Mermaid fenced code block — rather than as a separate diagram asset, until issue #1316's generated-artifact mechanism exists."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.8
  - statement: "buzz-relay and buzz-cli each declare a [[bin]] target in their Cargo.toml and carry a src/main.rs, making each an independently runnable artifact, while buzz-db declares no [[bin]] target and carries only a src/lib.rs, making it a library compiled into a binary rather than something separately runnable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-cli/Cargo.toml"
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-db/src/lib.rs"
  - statement: "The repository's own crate map describes buzz-db as 'Postgres event store and data access layer' and buzz-relay as the 'WebSocket relay server — main entry point,' language that itself distinguishes a data-access library from the running server that links it in."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "Issue #605 (parent PRD) states the real acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts — distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1327 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD, relayed via the corpus-templates batch dispatch brief)"
  - statement: "Issue #1327's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1327 definition of done"
  - statement: "Issue #1336 (task: define the deployment corpus template) exists as a sibling, out-of-scope-for-this-batch template task, so this node's boundary statement against deployment content names a real, filed issue rather than a hypothetical future one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1336"
---

# Template: architecture container

How to write a corpus node whose subject is a system's (or subsystem's) **container
architecture** — the deployable, runnable units that make it up, the technology
choice for each, and how they communicate. This node is the template itself, not an
instance of one: it states what an architecture-container node must contain, not a
container diagram for any real system.

## Scope and authority

**This node covers** the purpose of an architecture-container document, the sections
it must contain, what evidence each section needs, and the industry model it adapts
(the C4 model's Container diagram, read together with arc42 section 5). It does not
itself document any real system's containers.

**A note on this node's own definition of done.** Issue #1327's checklist carries a
MUST/SHOULD/enforcement/exception block copied verbatim from the standards-track
issues that produced `standards/confidence.md` and `standards/decision-references.md`
— documents whose subject is a normative policy. This node's subject is a template,
and the parent PRD (#605) states the acceptance bar that actually applies to a
template task: *every template states its purpose, required sections, evidence
expectations and the industry model/standard it adapts.* This document is built
against that sentence. The rest of #1327's checklist — one hand-authored document,
schema-valid front matter, one independently maintainable idea, traceable claims,
links instead of duplication, a check against the recorded revision, a clean
validator run — is generic to any corpus node and is honoured below regardless.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` is the create/update/retire procedure; `standards/confidence.md`
and `standards/decision-references.md` are the two evidence-mechanics standards
merged so far. This document adds nothing to any of those. What it adds is the part
none of them can: what a *container-scoped* architecture node must say, and where
that shape comes from.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The C4 model, primary source | `https://c4model.com/abstractions/container`, `https://c4model.com/diagrams/container` |
| arc42, primary source | `https://arc42.org/overview`, `https://docs.arc42.org/section-5/` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Purpose

A container-architecture node exists to answer one question for a reader who
already knows the system's outer boundary (its context diagram, if one exists):
***what actually has to be running, and in what technology, for this system to
work?*** It is the level between "the system as one box" (context) and "what's
inside one of those running things" (component). A reader should come away able to
name every deployable unit, what it is built in, and who talks to whom — without
yet knowing anything about the internal structure of any one of them, and without
being told where any of them physically run.

**The failure this template exists to prevent.** Left unscoped, an
architecture-container document drifts in one of two directions: down into
component-level internals (modules, request handlers — arc42's own
"Level 2" concern, C4's Component diagram; classes go a level deeper still,
into C4's Code diagram, which is out of scope for a component-level document
too), or sideways into deployment concerns (clusters, replicas, load
balancers, which environment runs what — arc42 section 7, C4's Deployment
diagram, and issue #1336's territory). Both drifts produce a
document that is not wrong so much as mis-shelved: the facts might be true, but a
reader looking for "what are the moving parts" has to wade through "how many
replicas does each one have" or "which method calls which" to find them. The
sections below exist to keep those two concerns out.

## The industry model this adapts

**C4 model, Container diagram** (Simon Brown, `https://c4model.com/`, undated —
no version number is published). **"Not Docker!"** is how the primary source
opens its own definition of the term, before defining anything else — because
"container" is heavily overloaded by the Docker/OCI container runtime
technology, and this repository ships one (`Dockerfile`, `crates/buzz-backend-kubernetes`)
that makes the two words easy to conflate. A C4 container is an architectural
abstraction — an application or a data store that has to be running for the
system to work — not a synonym for a Docker container. The two are related (a
C4 container is often literally deployed as one or more Docker containers) but
are not the same thing, and this document uses "container" in the C4 sense
throughout. With that disambiguated, the primary source defines a container as
"an application or a data store... a runtime boundary around some code that is
being executed or some data that is being stored" and "something that needs to be
running in order for the overall software system to work." The Container diagram
"zoom[s] in to the system boundary" to show "the high-level shape of the software
architecture and how responsibilities are distributed across it," including "the
major technology choices and how the containers communicate with one another," for
an audience of "technical people inside and outside the software development team;
including software architects, developers and operations/support staff." The same
source states the diagram explicitly excludes deployment aspects — "clustering,
load balancers, replication, failover, etc" — reserving those for a separate
Deployment diagram.

**arc42, section 5 (Building Block View)**, read as a partial match, not a full
one. arc42's own vocabulary is "building blocks," not "containers," and its
Level 1 (the whole system as a whitebox, its top-level parts shown as blackboxes)
is the section of arc42 that corresponds to a Container diagram's scope. arc42's
Level 2 — zooming into one Level 1 block — is the Component diagram's territory
(issue #1326), not this template's. Section 3 (Context & Scope: "External systems
and interfaces") and section 7 (Deployment View: "Hardware, infrastructure and
deployment") are both explicitly out of scope for this node, by arc42's own
section boundaries.

**Both sources agree C4 is diagrams, not prose** — it names diagram types and what
each must show, and leaves the surrounding write-up to whatever documentation
method a project already uses. This template is that surrounding write-up: it
tells an author what prose has to accompany the diagram so a reader can trust it,
because a corpus node cannot be an image with no traceable claims under it.

## Required sections

An architecture-container node MUST contain the following, in this order. ("MUST"
here is this template's own requirement for the shape of an instance node, not a
restatement of any MUST/SHOULD normative-policy framework — this document is a
template, not a standard, per the *Scope and authority* note above.)

1. **Purpose & scope statement.** One paragraph naming the system or subsystem
   this document covers, and stating explicitly: this is a container-level view —
   one level inside that system's context boundary, one level above any single
   container's internal component structure. Name the sibling context node (if one
   exists) that this document zooms into, and the sibling component node(s) (if
   any exist) that zoom further into one of this document's containers.

2. **Notation legend.** What a box, an arrow, and any grouping mean in the diagram
   that follows. A reader who has never seen a C4 diagram before should not have
   to already know the convention.

3. **The container diagram itself**, authored as text inside the Markdown body —
   a Mermaid fenced code block is the recommended form. **This is not optional
   and it is not an external image file.** `AGENTS.md` states that every
   non-Markdown file under the corpus root is rejected today, including one
   placed under `generated/`, because no generator exists yet to reproduce it
   from canonical Markdown (issue #1316). An architecture-container node with a
   linked PNG and no inline diagram does not validate today and would not survive
   review even if it did — the corpus's canonical representation is the
   Markdown, and a diagram that only exists as a binary asset is not part of it.

4. **Container inventory.** One row per container named in the diagram: its name,
   its technology (language, runtime, framework — whatever answers "what is this
   built in"), and a one-line statement of its responsibility. This is the table
   that turns diagram boxes into checkable claims — every row needs an evidence
   entry (see below) tying it to something real.

5. **Communication summary.** For each arrow in the diagram: what two containers
   it connects, and in what protocol or mechanism (HTTP, WebSocket, a message
   queue, a direct library call is a sign the two are *not* separate containers —
   see the boundary note below). This is where "how the containers communicate,"
   which the C4 source names as part of the diagram's job, becomes prose a reader
   can verify against real code rather than trusting the arrow alone.

6. **Scope and omissions**, per `AGENTS.md`'s own required shape for this
   section: what this document does not cover and who owns it (deployment
   topology → issue #1336's future template; internal component structure of any
   one container → issue #1326's template; the system's external actors and
   boundary → issue #1328's template), and — separately — anything expected to
   verify while drafting this node and unable to.

## What counts as a container, and what does not

**The test, from the primary source:** would the system stop working if this
stopped running? A compiled library linked into another artifact's binary is not
a container by that test, however large or important it is — it runs *inside*
whichever container links it, not as a container of its own. That test settles
container membership only. It does **not** by itself make the library a C4
*component*: a library crate, module, package, namespace or folder is an
organizational unit, and C4's own FAQ says these are "typically not"
components, because the model shows how functionality is partitioned across
runtime units rather than how it is packaged. Whether a given library
constitutes one component, several, or is folded into a larger one depends on
how the container's functionality is actually decomposed at runtime — a
separate question this test does not answer.

**A worked, evidence-checked illustration from this repository** (illustrative
only — not a claim that this is Buzz's authoritative or complete container
inventory, which is future work for whoever writes that instance node, not this
template):

| Name | Container? | Why |
|---|---|---|
| `buzz-relay` (`crates/buzz-relay`) | Yes | Declares a `[[bin]]` target and a `src/main.rs` — an independently runnable binary, described in this repository's own crate map as the relay server's "main entry point." |
| `buzz-cli` (`crates/buzz-cli`) | Yes | Same test: a `[[bin]]` target and `src/main.rs` of its own, producing a separate binary a user runs directly. |
| `buzz-db` (`crates/buzz-db`) | No | No `[[bin]]` target; only a `src/lib.rs`. It is Postgres data-access code *linked into* `buzz-relay`'s binary, so it is not itself a container. **This table does not conclude it is therefore a component.** A Rust library crate is an organizational unit — comparable to a JAR, assembly, DLL, module, package, namespace or folder — and C4's own FAQ says these are "typically not" components, because the model shows runtime partitioning of functionality, not packaging structure. Whether `buzz-db` constitutes one C4 component, several, or is folded into a larger one depends on how `buzz-relay`'s functionality is actually decomposed at runtime — a question this illustration does not answer, since it only establishes container membership, not component boundaries. See `https://c4model.com/abstractions/component`. |

The same test applies to third-party runtime dependencies: a Postgres or Redis
instance the system requires to run is a container in the C4 sense (a data store
that has to be running), even though nobody in this repository writes its code —
"container" describes a runtime boundary, not authorship.

## Evidence expectations

Every row in the container inventory and every line in the communication summary
is a claim, and needs the same evidence-ledger treatment `AGENTS.md` requires of
any corpus node — classified honestly, not defaulted to FACT:

- **A container's existence and technology** is a `FACT` when it cites something
  that runs or builds it: a `Cargo.toml`/`package.json`/`pubspec.yaml` manifest,
  a `Dockerfile`, a CI build step, an entry point file (`main.rs`, `main.ts`). A
  `Dockerfile` is evidence *of* a container's existence and technology — it
  names what runs — not itself the definition of a C4 container; see the
  "Not Docker!" disambiguation above. Do not cite a README's prose description
  alone — descriptions drift; build configuration is what actually runs.
- **A communication edge between two containers** is a `FACT` when it cites the
  client/server code that makes the call (an HTTP client, a WebSocket connection,
  a queue publish/subscribe) — not a diagram from another document, and not an
  architecture description that predates the code it claims to describe.
- **A container's future or planned technology** — something the diagram shows
  because it is intended, not because it exists yet — is `TEAM_KNOWLEDGE`
  attributed to the issue, PR or decision that intends it, never `FACT`.
- **Whether two related running things are one container or two** is frequently
  a judgement call rather than something a single file settles (a monorepo
  workspace can blur this). Where it is a judgement call, it is an `INFERENCE`
  with `confidence`, and the reasoning must be visible per
  `standards/confidence.md`'s Requirement 4 — not asserted as settled fact.

**This template does not restate the FACT/INFERENCE/TEAM_KNOWLEDGE contract
itself, `confidence`'s meaning, or the six-plus-one citation shapes.**
`AGENTS.md` and `standards/confidence.md` own those, and a second copy here would
be exactly the drift-prone duplication `AGENTS.md` warns against.

## Relationships an instance node should consider

This template's own front matter declares none (see *Scope and omissions*
below), but an instance node written from this template usually has real edges
to declare once its siblings exist:

- **`part-of`**, authored by *this container document*, targeting the
  architecture-context node it zooms into, if one has been written for the same
  system — the container view is a constituent part of the whole the context
  node describes, which is `part-of`'s stated forward direction.
- **`part-of`**, authored the same way but by the *architecture-component*
  document (#1326) that zooms into one of this container document's own
  containers, targeting this container node — not the other way around. The
  container document does not hand-author a matching edge back down to each of
  its components: `has-part` is `part-of`'s generated inverse, produced by
  tooling from the component's own forward edge, and `relationships.schema.json`
  itself rejects an inverse type authored by hand
  (`fixtures/invalid/wrong-direction-relationship.md`). A container document
  that also authors a forward edge to its components would either duplicate
  what the generated inverse already supplies or use the wrong relationship
  type to say it.
- **`depends-on`**, targeting another *corpus node* (not a decision record) whose
  own claims this document's claims would stop holding if they changed — for
  example a shared platform or capability node describing an infrastructure
  primitive every container in this document assumes. This is a different
  mechanism from citing an accepted decision as evidence: an ADR or ratified
  specification is never a `relationships[].target` (targets are corpus node
  ids; decisions live outside the corpus under `launchpad/decisions/` and are
  not loaded as nodes), so a technology choice that rests on a decision is cited
  in the evidence ledger per `standards/decision-references.md`, not declared as
  a relationship.

None of these can be declared by *this* template document itself — a template is
not an instance of the system it describes, and declaring `part-of` or
`depends-on` here would target a node that does not exist for a system that is
never named.

## Boundary against sibling templates

The three architecture template issues (#1326 component, #1327 container, #1328
context) map onto the C4 model's outer three diagram layers. Getting the
boundary right matters more than getting any one document exhaustive, because
these three documents will describe the same system from adjacent zoom levels and
overlap is where duplicated, silently-drifting claims come from.

| This template (container) | Its neighbors |
|---|---|
| **Above:** architecture-context (#1328) | Shows the system as one box plus its external actors. This template does not repeat that box's contents — it names the context node and moves straight to what is inside the boundary. |
| **Below:** architecture-component (#1326) | Shows what is inside one container. This template stops at "what is this container, in what technology, talking to what" — it does not describe a container's internal modules or request handlers (C4's Component level), nor the classes inside them (C4's Code level, one layer deeper still). |
| **Sideways:** deployment (`corpus-template-deployment`, #1336) | Shows where containers run — clustering, replicas, environments, infrastructure. Checked directly against the C4 primary source while drafting this node: `c4model.com`'s own Deployment diagram page independently states this is a separate diagram type answering "where do these run," not a section of the Container diagram. The boundary is not ambiguous at the primary-source level; `corpus-template-deployment` owns it. |

## Scope and omissions

**This node covers** the purpose of an architecture-container document, its
required sections, its evidence expectations, and the industry model (C4
Container diagram, arc42 section 5) it adapts.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The system's external boundary and actors | #1328 (architecture-context template) |
| One container's internal building blocks | #1326 (architecture-component template) |
| Where containers physically or virtually run | `corpus-template-deployment` (#1336) |
| The evidence-class contract itself (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |
| The `confidence` field's meaning and requirements | `launchpad/docs/corpus/standards/confidence.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| A per-type diagram standard (notation conventions across all corpus diagrams, not just this one) | #1312, `task/1312-corpus-standard-diagrams`, unmerged at the recorded revision |

**No `relationships` in this node's front matter.** At the recorded revision,
`origin/launchpad`'s corpus tree carries four validated content nodes —
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` — and none of the four has architecture,
containers, C4 or templates as its subject. An edge to any of them would be a
citation duplicate of what this node's evidence ledger already cites directly by
path, not a substantive typed relationship. This was checked against the actual
tree (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`),
not assumed from "the corpus is new." The most likely first genuine edge for
this node is an `implements` relationship to a future per-type diagram standard
(#1312) once it merges — `relationships.schema.json` names exactly that
directionality ("source is the concrete realization of target, e.g. a template
instance of a standard") as the intended shape for a template pointing at its
governing standard, but #1312 is unmerged today and that relationship would not
resolve in CI.

**No edges to the sibling templates #1326 or #1328.** All three architecture
template issues are being authored in parallel by independent agents with none
merged when review starts on the others, so declaring an edge to either sibling
id today would be a hard validation error against `origin/launchpad` even though
it might resolve inside this node's own worktree. The *Relationships an instance
node should consider* section above exists so a future author of an actual
architecture-container node — not this template — knows to add those edges once
the siblings exist.

**Expected but not verified when this node was written:**

- **No instance of this template has been written yet.** Whether the six
  required sections above are sufficient, or whether a real system's container
  diagram surfaces a seventh concern this template does not anticipate, is
  untested. The first real architecture-container node is the test.
- **Whether Mermaid is the only workable in-Markdown diagram notation for this
  corpus was not surveyed.** It is recommended above because it renders on
  GitHub without a generator and is plain text a diff can show meaningfully;
  no alternative was evaluated against those two properties.
- **The worked buzz-relay/buzz-cli/buzz-db illustration was checked only for
  those three crates**, not for the repository's full crate list, and is
  explicitly not offered as Buzz's own container inventory.
- **Cross-model review was not run.** Issue #1467 records that the cross-model
  review provider (Codex) is currently unavailable; a same-model final pass was
  substituted, per the corpus-templates batch dispatch brief.
