---
description: Research into information architecture for a corpus of atomic, independently maintainable technical-documentation nodes.
tags: [documentation, corpus, information-architecture, atomicity, navigation, relationships, research]
---

# Information architecture for atomic documentation

Researched 2026-09-06. This is research, not an adopted corpus standard.

## Research question

How should the Buzz documentation corpus be architected so that each atomic node is
useful when encountered alone, while the corpus still provides coherent paths,
relationships, and larger explanations without duplicating canonical content?

The investigation considered seven subquestions:

1. What distinguishes an atomic node from either a fragment or an over-broad bundle?
2. What context must live inside a node, and what context should be supplied by links
   or a larger assembly?
3. What different jobs should physical folders, metadata, semantic relationships,
   body links, and navigational maps perform?
4. How can the same canonical nodes support different audiences and goals without
   being copied?
5. Which structures must contain human-authored judgment, and which can safely be
   generated?
6. Which graph and map diagnostics expose architectural risk without turning edge
   density into a false quality target?
7. What should a future content reviewer inspect at node, connection, journey, and
   corpus levels?

## Bottom line

An atomic corpus should not be treated as one hierarchy of small files. It needs at
least four distinguishable architectural layers:

1. **Nodes** hold canonical content. Each has one independently maintainable purpose
   and enough local context to be understood by its intended, qualified audience.
2. **Classification** describes nodes through stable identity and controlled facets
   such as subject surface, audience, lifecycle state, and other applicability
   dimensions.
3. **Semantic connections** state durable facts about how nodes relate, while
   contextual body links explain why a particular connection matters where the reader
   encounters it.
4. **Maps or assemblies** select, order, group, and branch through nodes for a defined
   audience, goal, or deliverable. The same node can appear in more than one map.

Search, indexes, graphs, and audit reports are projections over those layers, not
substitutes for them.

The governing tension is not “standalone versus connected.” A good node is both. It
does not depend on an undocumented reading order to make sense, but it also does not
repeat every prerequisite, definition, rationale, or adjacent task. It establishes
its purpose, scope, assumptions, and applicability locally; gives the minimum context
needed to interpret its main content; and uses meaningful links to let readers change
level, satisfy a prerequisite, inspect evidence, or continue a task.

For Buzz, the most important architectural gap is not simply that many nodes have few
declared relationships. It is that the current canonical model has no explicit way to
represent a reader journey. The five relationship types describe semantic connections,
not an audience-specific sequence. Body links are visible to readers but are not
machine-checked or available to a generator. Planned generated indexes and graphs can
therefore expose what has already been encoded, but they cannot legitimately invent
which nodes an operator, developer, reviewer, or agent should read—and in what order—to
accomplish a goal.

Any future solution needs a canonical source for that human judgment: for example,
authored map definitions, an extension to the corpus model, or another reviewed data
structure from which reader-facing maps are generated. The exact representation is a
project design decision and is not settled by this report.

## Scope and method

This report addresses the content architecture of an atomic documentation corpus. It
does not decide:

- search ranking, navigation-interface usability, or user testing, deferred to topic
  6;
- freshness and change-impact policy, deferred to topic 7;
- detailed procedure, architecture, terminology, example, accessibility, or security
  criteria, covered by later topics;
- a schema change, generator implementation, or migration plan; or
- LLM-specific review controls, which remain outside the current sequence.

Local inspection covered the corpus instructions, schema, atomicity, linking,
identifier and taxonomy standards, generated-index template, validator, physical node
tree, and current relationship graph. The graph snapshot was computed from the
working tree's YAML front matter and deliberately excludes body links, because the
current tooling does not parse those links as graph data.

External sources were selected in this order:

1. an international software-information standard defining information architecture,
   audience, navigation, and minimalism;
2. the OASIS DITA standard, because it explicitly separates reusable topics from maps,
   navigation, relationships, taxonomies, and conditional metadata;
3. the W3C SKOS Recommendation, as a model for controlled labels, hierarchical and
   associative relations, and ordered collections;
4. Red Hat's maintained modular-documentation guide, as a large-scale practitioner
   model of self-contained modules assembled around user stories; and
5. Mark Baker's *Every Page Is Page One* material, as a practitioner argument for
   locally established context and bottom-up navigation.

DITA, SKOS, Red Hat modular documentation, and Every Page Is Page One are models, not
requirements that Buzz adopt their formats. Findings transferred from them are marked
as synthesis rather than presented as direct mandates.

## Definitions

| Term | Meaning here |
|---|---|
| Atomic node | One canonical, independently maintainable idea with a specific purpose and enough content to be useful by itself |
| Fragment | A file whose main content cannot be understood or used without an unstated neighboring context |
| Bundle | One node containing subjects that have different purposes, applicability, authority, or maintenance clocks |
| Local context | Information inside the node that lets the intended reader identify the subject, purpose, scope, assumptions, and applicability |
| Classification | Controlled metadata that says what a node is about and to whom or where it applies |
| Semantic relationship | A typed assertion about how two whole nodes relate, independent of one particular reading path |
| Contextual link | A link in prose whose surrounding words explain why the target matters at that point |
| Map | A separate, goal-bound selection and organization of nodes into a hierarchy, sequence, group, branch, or related set |
| Assembly | A reader-facing composition of reusable modules for a user story or goal; one possible realization of a map |
| Projection | A generated index, graph, filtered view, or report derived from canonical nodes and map data |
| Journey | The path a defined audience can follow from a known entry state to an information or task outcome |

Atomicity and brevity are not synonyms. A long node can be atomic if all of its
content serves one purpose and changes together. A short file can be a fragment if it
merely points elsewhere or assumes an invisible predecessor.

## What the local system establishes

### The node contract already encodes useful foundations

Buzz defines one Markdown file with YAML front matter as one canonical node. Stable
`id` values provide machine identity; `type`, `status`, `origin`, and `audiences`
provide controlled classification; `evidence` records claim support; and optional
typed `relationships` connect whole-node IDs.

The local atomicity standard is unusually clear about the desired unit: one node is
one independently maintainable idea. Its decision procedure tests one-sentence scope,
single-valued metadata, maintenance clocks, relationship boundaries, and standalone
meaning. It also captures both failure modes:

- over-merging conceals independently changing subjects inside one lifecycle and
  evidence envelope; and
- over-splitting produces visible fragments that need a neighbor merely to mean
  anything.

The standard's `part-of` relationship is explicitly not permission to divide one idea
into chapter-like fragments. When a subject is split, the node must record what was
declined and where it went. These are strong foundations for atomic authoring.

### The current architecture has several distinct connection surfaces

Buzz already distinguishes two kinds of explicit connection:

- a body link is visible where a human or agent reads the prose and can explain the
  relevance of its target; and
- a `relationships[]` edge is machine-readable, resolves by stable node ID, and can
  support a future graph or generated view.

The linking standard correctly states that neither always substitutes for the other.
An edge without prose can be invisible to a reader following an argument. A prose
link without an edge is unavailable to relationship-aware tooling. It also discourages
copying another source's bounded rule set: the current node should provide the minimum
context and link to the canonical owner.

The five relationship types have deliberately narrow meanings:

| Type | Meaning in the current schema | What it does not necessarily mean |
|---|---|---|
| `depends-on` | The source's claims require the target to remain true or current | “Read this first” or “perform this task first” |
| `supersedes` | The source replaces the target | A general next step |
| `implements` | The source concretely realizes the target | A parent-child table-of-contents relationship |
| `references` | The target supplies supporting context, without ownership or currency dependency | A curated recommendation for every reader |
| `part-of` | The source is a constituent or child of the target | Sequence among siblings or permission to create fragments |

That vocabulary describes semantic structure, not reader sequence. In particular,
none of the types says “prerequisite knowledge for audience A,” “next step in workflow
W,” “alternative path,” or “start here.” Reusing `depends-on` or `part-of` for those
meanings would weaken the existing contract.

### The physical tree is useful, but it is only one view

The corpus is stored in subject-oriented directories such as `architecture/`,
`capabilities/`, `development/`, `layers/`, `standards/`, and `templates/`, with
additional subdirectories beneath several of them. That gives authors and repository
readers a predictable physical browse path.

It cannot be the whole information architecture:

- a file has one physical location but can be relevant to several audiences, tasks,
  lifecycle stages, or product surfaces;
- the schema's `type` is a subject-surface classification, not a universal reading
  order or writing genre;
- a task journey may cross architecture, configuration, operations, verification, and
  recovery material; and
- stable IDs, rather than paths, are the relationship targets.

The folder tree should therefore be treated as a maintainership and default-browse
structure, not as proof that every reader's conceptual model is hierarchical or that
every useful path begins at the repository root.

### The explicit relationship graph is sparse and uneven

At this working-tree snapshot, direct front-matter inspection found:

| Graph observation | Count |
|---|---:|
| Loaded corpus nodes | 205 |
| Authored directed relationships | 192 |
| Nodes with at least one outgoing relationship | 89 |
| Nodes with at least one incoming relationship | 36 |
| Nodes with neither incoming nor outgoing relationships | 81 |
| Weakly connected components | 84 |
| Largest component sizes | 101, 21, 2 |

Relationship types were distributed as follows:

| Type | Edges |
|---|---:|
| `references` | 167 |
| `implements` | 17 |
| `depends-on` | 6 |
| `part-of` | 2 |
| `supersedes` | 0 |

The largest incoming hubs included `architecture-containers-relay` (29),
`corpus-agents` (15), `architecture-flows-event-ingestion` (14),
`architecture-containers-agent-runtime` (12), and
`architecture-containers-desktop` (10).

These counts are diagnostic signals, not a quality verdict. The schema makes
relationships optional; some relationship backfill was intentionally deferred; a
valid standalone node can be isolated; and body links were not counted. Conversely,
192 resolving edges do not prove that a reader has a coherent path. Almost 87% are the
broad `references` type, and resolution proves only that the target ID exists.

The useful conclusion is narrower: the current explicit graph alone is not a complete
representation of corpus navigation, and connectedness cannot be assessed by edge
count without reviewing purpose and audience.

### Generated views are planned but do not yet supply the missing architecture

The corpus contains a generated-index template and references planned artifacts such
as a corpus index, dependency graph, documentation graph, orphan report, stale report,
and documentation-to-code or test mappings. No `generated/` directory or generated
corpus index is present in the current tree.

The template correctly requires a future generator to name its inputs,
inclusion/exclusion rules, deterministic ordering, and generated status. That protects
reproducibility. It also exposes an important boundary: a deterministic projection can
only render knowledge already present in canonical inputs.

If no canonical field says that a relay restoration overview precedes a backup
procedure for operators, a generator cannot derive that ordering merely because both
nodes exist. Choosing that order is information architecture, not formatting. A
generated journey therefore needs an authored, reviewed source of map intent even if
the final Markdown view is generated.

### Validation establishes integrity, not navigational adequacy

The validator checks schema shape, identifier uniqueness, citation forms, local
citation existence, and relationship target resolution. It does not inspect body
links, judge whether a relationship type is semantically correct, require inverse
edges, test atomicity, or determine whether a reader can reach a goal.

A graph can consequently be structurally valid while still containing:

- a false or unhelpful relationship;
- a high-value node that no relevant map exposes;
- an ordered task represented only as unordered references;
- a contextual link whose label or target is wrong;
- a node that is individually sound but appears in the wrong audience journey; or
- a connected component that has no meaningful entry point.

Those are content and architecture review questions.

## What the external evidence establishes

### Information architecture is about access semantics, not file placement

[ISO/IEC/IEEE 26514:2022 public browsing material](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
defines information architecture as the structure of an information space and the
semantics for accessing information about tasks, system functions, features, and
other information (§3.1.27). It defines an audience by shared characteristics and
needs that determine content, structure, and use (§3.1.7), and places audience and
task analysis inside the information-architecture process (§6.2 and the abstract).

This definition is broader than directories or menus. The “semantics for accessing”
part means that a connection needs meaning: prerequisite, sequence, hierarchy,
alternative, explanation, evidence, or another declared relation. A pile of links is
not yet an architecture.

The same standard defines navigation as accessing information and viewing different
topics (§3.1.35), a signpost as something that helps a reader understand where
information is located or how the current display fits into the whole (§3.1.45), and
minimalism as including critical information plus the least other material needed for
completeness (§3.1.34). Together these definitions support both local orientation and
controlled restraint: a node needs enough context and signposting to work, not a copy
of the whole system around it.

The public material does not expose every paid normative clause, so this report does
not claim ISO conformance.

### Topic content and maps solve different problems

The [OASIS DITA 1.3 specification](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/dita-v1.3-os-part1-base.html)
defines a topic as the basic unit of content and reuse, containing a single subject.
Its guidance on
[disciplined topic-oriented writing](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/topicorientation.html)
says a topic should contain what the reader needs for its focused purpose, avoid
transitional language that assumes another context, and remain reusable across
contexts.

DITA then separates navigation from that reusable content. A
[DITA map](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/definition-of-ditamaps.html)
organizes references into structured collections, defines hierarchy, ordering, and
non-hierarchical relationships, and supplies the context that lets topics remain
relatively context-free. The same topic can be used in different maps. The
[purpose-of-maps section](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/purpose-of-ditamaps.html)
distinguishes defining an information architecture, a deliverable manifest,
navigation, related links, authoring context, and key scopes.

The transferable principle is not that Buzz should adopt XML or DITA. It is that
canonical content units should not also carry every possible table of contents. A
separate map can express one audience and goal without making that ordering an
intrinsic property of each reused node.

DITA also shows why “map” is more than “graph.” Its map attributes can declare an
ordered `sequence` and enable next/previous behavior, while relationship tables can
express non-hierarchical association. Those are different structures with different
reader effects. A generic related edge should not silently become an ordered step.

### Controlled vocabularies support multiple reliable views

DITA
[subject-scheme maps](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/subject-scheme-maps-and-usage.html)
define controlled values and subject definitions. Values such as audience can classify
content for filtering, while hierarchical subject definitions can support retrieval
and traversal. Its
[conditional-processing model](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/conditional-processing-attributes.html)
distinguishes dimensions such as audience, product, platform, delivery target,
revision, importance, and status.

The [W3C SKOS Recommendation](https://www.w3.org/TR/2009/REC-skos-reference-20090818/)
provides a complementary lightweight model. Concepts have stable identifiers,
preferred, alternative, and hidden labels, scope notes, hierarchical
`broader`/`narrower` links, associative `related` links, concept schemes, and labeled
or ordered collections. SKOS also cautions that a taxonomy or thesaurus is an informal
knowledge-organization structure, not automatically a formal ontology or a set of
facts about the world.

For Buzz, the practical lesson is to keep facets and relation meanings controlled,
documented, and distinct. Preferred labels and synonyms support consistent language
and retrieval; hierarchical and associative relationships should not be conflated;
and an ordered collection should be explicit when order matters. Buzz need not use
SKOS serialization to benefit from those distinctions.

### Self-contained modules still require assemblies

Red Hat's maintained
[Modular Documentation Reference Guide](https://redhat-documentation.github.io/modular-docs/)
defines a module as an independent, self-contained chunk that can work alone or be
reused, and an assembly as modules organized around a user story. It explicitly says
that legacy text split into small meaningless pieces is not modular documentation,
and that an unorganized collection of modules is confusing. Assemblies provide an
introduction, optional shared prerequisites, and an ordered combination of concept,
procedure, and reference modules.

This practitioner model exposes a useful division of context:

- context intrinsic to understanding a module belongs in the module;
- context about the larger user goal and shared prerequisites belongs in the
  assembly; and
- copied content is not required merely because one module appears in several
  assemblies.

It also warns that deeply nested assemblies add complexity. Reuse does not justify an
unbounded hierarchy of wrappers.

### Local orientation and bottom-up links are necessary when entry points vary

Mark Baker's
[*Every Page Is Page One* overview](https://everypageispageone.com/the-book/)
argues that a topic reached from anywhere should be self-contained, have a specific
and limited purpose, establish its own context, assume a suitably qualified reader,
stay on one level, and link richly. His
[bottom-up information-architecture summary](https://everypageispageone.com/2015/02/10/bottom-up-information-architecture-q-and-a-part-1/)
clarifies that “self-contained” does not mean explaining everything to everyone. The
topic gives qualified readers what they need and gives other readers enough context
to recognize missing prerequisites and find them.

This is practitioner guidance rather than a standard or controlled study. It is still
valuable because it resolves a common false choice in atomic documentation: either
repeat every dependency or force a linear reading order. The middle path is a bounded
audience assumption, a locally explicit context, and purposeful links to change
level.

## A candidate architecture for Buzz

### 1. Keep the atomic node as the canonical content unit

The existing node unit should remain responsible for one purpose and one maintenance
clock. A reviewer should be able to answer:

- What reader question, decision, or action does this node support?
- Does every material section serve that purpose?
- Can any section change independently in authority, applicability, status, or
  evidence?
- If the node were encountered from search or a direct link, would its intended reader
  know what it covers and how to use it?
- If another node disappeared, would this node still state its own main claim or
  procedure?

The test is semantic independence, not isolation. A node can require external facts,
tools, privileges, or prior knowledge as long as it names the relevant assumptions and
points to their canonical owners.

### 2. Give each node a small orientation contract

Not every node needs an identical “Context” section, but its opening and metadata
should jointly make the following discoverable where applicable:

- exact subject and purpose;
- intended audience and assumed qualification;
- scope boundary and important exclusions;
- product, platform, deployment, version, or lifecycle applicability;
- prerequisites that affect whether the content can be used safely;
- the outcome, decision, or understanding the node supplies; and
- where to go for adjacent levels or tasks.

This is not an invitation to repeat a glossary, architecture overview, or full workflow
inside every node. Include the minimum context needed to interpret the local content,
then link to the canonical source with words that explain the target's role.

### 3. Treat classification as faceted, not as one master tree

The existing `type`, `audiences`, `status`, and `origin` fields already show that one
node can participate in several classification dimensions. A future architecture may
need additional controlled facets—such as platform, lifecycle phase, product version,
or genre—but only when a concrete retrieval, filtering, review, or generation use case
justifies them.

Each facet should have:

- a defined question it answers;
- controlled values with stable meaning;
- a preferred label and, where retrieval needs it, known synonyms;
- applicability and cardinality rules;
- an owner and change process; and
- at least one actual consumer, such as a review slice, map filter, or generated view.

Do not make folders, tags, and front-matter fields three independent taxonomies for
the same concept. Duplicate classification systems drift just as duplicate prose does.

### 4. Keep semantic relationships typed and conservative

An edge should exist because its declared type is true, not because a node “ought to
have more links.” Review each relationship for:

- correct source-to-target direction;
- exact fit with the schema definition;
- current target and stable identity;
- whether the body must also explain the connection;
- whether an inverse is required by project convention;
- whether a more specific relation or map membership is actually intended; and
- whether the edge stays true across all contexts in which the source is reused.

Avoid treating `references` as a universal “related to” bucket. A large generic edge
set creates a visually connected graph while conveying little about a reader's next
decision.

### 5. Add goal-bound maps without copying node content

A useful reader map should declare:

- map identity and purpose;
- intended audience and assumed starting state;
- product baseline and applicability;
- entry points;
- selected node IDs;
- grouping, sequence, branches, alternatives, and stop conditions where they matter;
- why each transition exists;
- treatment of draft, retired, missing, or conditional nodes; and
- the human owner and review trigger for the map intent.

Different map families serve different questions:

| Map family | Reader question | Likely structure |
|---|---|---|
| Orientation map | “What is this system or area, and where do I start?” | Hierarchy with a small number of entry points |
| Task or operational journey | “How do I reach this outcome from my current state?” | Sequence with prerequisites, branches, verification, and recovery exits |
| Learning path | “What knowledge should I acquire in what order?” | Ordered progression with qualification assumptions |
| Reference map | “Where is the exact detail for this surface?” | Faceted index or exhaustive bounded listing |
| Decision/evidence map | “Why is this true or required?” | Typed semantic graph rather than a forced sequence |
| Maintenance map | “What else must be reviewed when this changes?” | Dependency and traceability graph |

The same node may belong to several maps. Its canonical body remains single-sourced;
each map supplies the audience-and-goal context around it.

### 6. Separate authored map intent from generated presentation

Some projections can be generated entirely from existing node data:

- an alphabetical ID/title index;
- a list grouped by `type`, audience, status, or origin;
- a raw relationship graph;
- unresolved-target, isolation, staleness, and other audit reports; and
- source-to-node or test-to-node mappings when the underlying trace is canonical.

Other outputs contain editorial judgment and cannot be generated faithfully unless
that judgment is first recorded:

- “start here” recommendations;
- learning order;
- operational prerequisites and safe branches;
- the preferred next step for one audience;
- which explanation is sufficient before a risky procedure; and
- where a journey is complete.

For those, generation should render an authored map definition, not infer a curriculum
from path names, link counts, embedding similarity, or a generic `references` graph.
The generated file can still be deterministic; the knowledge it renders remains
human-owned and reviewable.

### 7. Support both top-down and bottom-up traversal

Readers should be able to:

- start from an audience or goal map and move downward into atomic nodes;
- land directly on a node from search, an issue, code, or another document and orient
  themselves locally;
- move sideways to closely related material;
- move up or down a level of abstraction deliberately; and
- return to the map or outcome they were pursuing.

A top-level index cannot repair a contextless node reached directly. Rich local links
cannot repair the absence of a curated path for a multi-node workflow. Both traversal
modes are necessary.

### 8. Review journeys as products, not merely as sets of valid nodes

A map or journey should be tested against a scenario:

1. Give a representative reader an explicit goal and starting state.
2. Identify the entry point they are expected to find.
3. Follow only the content and links exposed by the map and nodes.
4. Record ambiguity, backtracking, prerequisite surprises, dead ends, unsafe branches,
   duplicated explanation, and missing confirmation.
5. Verify that the journey reaches a recognizable outcome and provides recovery or
   escalation where applicable.

This is architecture-level content review. Topic 6 will examine how to validate
findability and usability empirically.

## Graph and map diagnostics worth using

Automated diagnostics should create a human review queue, not declare architectural
quality on their own.

| Diagnostic | What it can reveal | Why it is not a verdict |
|---|---|---|
| Nodes with no inbound or outbound edges | Possible orphans or missing semantic connections | Some nodes are legitimately standalone; body links are absent from the graph |
| Nodes absent from every reader map | Content with no declared journey or browse exposure | Exhaustive reference nodes may be reached primarily by search or an index |
| Map entries whose node is missing, draft, flagged, or retired | Broken or risky routes | A map may intentionally expose draft or historical material if labeled |
| High fan-in hubs | Foundational nodes or overused generic targets | Popularity can be correct; it can also conceal an over-broad node |
| High fan-out nodes | Useful overview or indiscriminate link list | Count does not measure relevance |
| `depends-on`, `part-of`, or `supersedes` cycles | Possible semantic contradiction or modeling error | Some dependency cycles may represent genuine coupling and need interpretation |
| Long required sequences | High reader burden or over-fragmentation | Some complex tasks are inherently long |
| Multiple paths with contradictory order | Audience/variant distinction missing or map drift | Different paths may be intentionally audience-specific |
| Dominance of `references` edges | Relationship vocabulary being used generically | A reference can be exactly the right type |
| Folder/metadata/map disagreement | Misclassification or a legitimate multi-faceted node | Physical placement and reader maps answer different questions |
| Duplicate titles or uncontrolled synonyms | Ambiguous navigation and search cues | Different scoped concepts can legitimately share a natural-language term |
| Broken body links | Direct navigational failure | Passing links still may be irrelevant or misleading |

Do not set a target such as “every node has three relationships.” It rewards invented
edges. Better gates are semantic: every node that is required by a declared journey is
reachable in that journey; every transition has a reason; every edge's type is true;
and every intentional orphan has a defensible access model.

## Candidate review procedure

For a representative corpus slice:

1. **Name the audience and goal.** Do not review architecture against an undefined
   universal reader.
2. **Inventory the nodes and access surfaces.** Record folders, metadata, body links,
   relationships, indexes, and maps separately.
3. **Review node boundaries.** Apply the local atomicity tests and identify fragments,
   bundles, and mixed maintenance clocks.
4. **Review local orientation.** Open each node without its neighbors and assess
   whether its intended reader can identify purpose, scope, assumptions, and
   applicability.
5. **Review every material connection.** Check target existence, link wording,
   relationship semantics, direction, and the distinction between prose and graph
   needs.
6. **Trace the intended journey.** Start at the declared entry point and follow the
   actual order and branches to an outcome.
7. **Inspect alternate entry.** Land on a middle node directly and test whether local
   signposting recovers the necessary context.
8. **Run graph diagnostics.** Use islands, hubs, cycles, missing map membership, and
   status conflicts to select cases for human review.
9. **Check reuse pressure.** Identify places where a node has accumulated generic
   transitional prose or duplicated context because it appears in multiple journeys.
10. **Record architectural gaps explicitly.** Distinguish missing content, missing
    connection, missing map intent, bad classification, and bad presentation; they need
    different remedies.

## Candidate checklist criteria

These are candidates for the eventual synthesis, not requirements in force.

### Node boundary and independence

- [ ] The node serves one bounded reader purpose or independently maintainable idea.
- [ ] All major sections share the same authority, applicability, lifecycle, and
      maintenance clock.
- [ ] The node is not merely a pointer, transition, or chapter fragment.
- [ ] The node does not absorb an adjacent concept solely to reduce file count.
- [ ] A split subject names the sibling node or tracked destination for the declined
      material.
- [ ] The node can state its own main claim, explanation, reference, or procedure even
      if neighboring nodes are unavailable.

### Local orientation

- [ ] A direct-arrival reader can identify the exact subject and purpose promptly.
- [ ] The intended audience and assumed qualification are clear from metadata and
      prose together.
- [ ] Scope, important exclusions, and applicability are explicit where ambiguity is
      plausible.
- [ ] Safety- or success-critical prerequisites are visible before the dependent
      content.
- [ ] The node contains the minimum context needed to interpret its main content.
- [ ] It does not rely on phrases such as “as described earlier” or an unstated reading
      order.
- [ ] Readers who lack assumed knowledge can recognize the gap and reach an appropriate
      source without the node becoming a textbook.

### Classification

- [ ] Each metadata facet answers a defined classification or retrieval question.
- [ ] Values come from the canonical controlled vocabulary and match the node's actual
      content.
- [ ] Subject surface, audience, status, origin, genre, platform, and lifecycle are not
      conflated.
- [ ] Folder placement is treated as one physical view, not the node's only possible
      location in reader space.
- [ ] Synonyms and alternate labels do not create competing canonical terms.
- [ ] Proposed metadata has a real consumer and is not collected speculatively.

### Links and semantic relationships

- [ ] Every body link resolves and its surrounding prose explains why the target is
      relevant.
- [ ] Link text identifies the destination or reader outcome rather than saying only
      “here” or “more.”
- [ ] Canonical content is linked with minimal local context rather than copied.
- [ ] Every `relationships[]` edge uses the correct type and direction.
- [ ] `depends-on`, `part-of`, and `references` are not overloaded as reader sequence.
- [ ] A body link and machine-readable edge are both present when their distinct
      readers require both.
- [ ] Related links are curated for relevance rather than accumulated for density.
- [ ] Relationship cycles, hubs, and islands receive semantic review rather than an
      automatic pass or fail.

### Maps, assemblies, and journeys

- [ ] Every map declares its audience, goal, baseline, entry state, and intended
      outcome.
- [ ] Sequence, hierarchy, association, prerequisite, alternative, and branch meanings
      remain distinguishable.
- [ ] Every ordered transition has a reader-centered reason.
- [ ] Shared prerequisites live at the appropriate assembly level without making the
      reused nodes contextless.
- [ ] The same canonical node can appear in several maps without copied source
      content.
- [ ] Conditional paths make product, platform, version, role, or lifecycle differences
      explicit.
- [ ] Draft, flagged, retired, missing, or conflicting nodes cannot enter a map
      silently.
- [ ] A reader can enter from the map and can also recover orientation after landing
      directly on a middle node.
- [ ] The journey reaches a recognizable information or task outcome, including
      verification, recovery, or escalation where relevant.
- [ ] Map nesting and path length have not become a new form of fragmentation.

### Generation and governance

- [ ] Every generated view declares its canonical inputs and deterministic selection
      and ordering rules.
- [ ] Generated presentation does not invent human-authored sequence, priority, or
      recommendation.
- [ ] Human map intent has a canonical, reviewable owner before it is rendered.
- [ ] Indexes, semantic graphs, task maps, coverage reports, and audit reports are not
      treated as interchangeable artifacts.
- [ ] Graph metrics are used to select review cases, not to reward link volume.
- [ ] Architecture changes are tested on at least one real audience-goal journey.

## Failure modes and architectural smells

| Smell | Likely problem |
|---|---|
| One universal table of contents for every audience | The physical or authorial hierarchy has been mistaken for reader intent |
| “Read the previous page first” | The node does not establish its own context and cannot be reused safely |
| A one-paragraph file that only links elsewhere | A fragment is being counted as a node |
| A long node with several unrelated applicability conditions | Independent maintenance clocks have been bundled |
| The same explanation appears in several nodes | Map or link context is missing, or canonical ownership is unclear |
| Every edge is `references` | Association has been encoded without useful semantics |
| `depends-on` is rendered automatically as “previous” | Claim dependency has been confused with reader prerequisite |
| A generated “recommended path” derived from link popularity | Editorial judgment is being invented rather than sourced |
| A node is considered findable because its file exists | Repository presence has been confused with map, index, search, or contextual exposure |
| An isolated node is automatically deleted or forcibly linked | Graph neatness is overriding semantic truth |
| A hub node must be read before everything else | The corpus is rebuilding a linear book around an over-broad overview |
| A map contains summaries that become authoritative copies | Assembly context has turned into duplicated canonical content |
| Metadata values exist but no view or review uses them | Taxonomy cost is being incurred without an information-architecture benefit |

## Competing positions and unresolved decisions

### “If every node is standalone, maps are optional”

Standalone meaning protects direct arrival and reuse. It does not tell a reader which
of 205 nodes matters for a particular goal or how a multi-step operation proceeds.
Recommended resolution: require both local intelligibility and goal-bound paths where
the reader need spans nodes.

### “The directory tree should be the canonical information architecture”

One tree is simple for authors and repository browsing. A file can have only one
parent, while a node can legitimately serve several audiences and journeys.
Recommended resolution: keep the physical tree predictable, but represent other views
through controlled metadata and maps rather than duplicating files.

### “All navigation should live in topic body links”

Contextual links are visible and can give excellent bottom-up orientation. They mix
one path's transitional language into reusable content, are not currently checked,
and cannot provide a centrally reviewable journey. Recommended resolution: use body
links when the connection matters locally, and separate maps for audience-specific
selection and ordering.

### “All navigation should be generated from `relationships[]`”

This is reproducible and keeps prose cleaner. The current types do not encode reader
order, audience-specific prerequisites, branches, or start/end conditions. Inferring
those meanings would be unsound. Recommended resolution: generate semantic views from
relationships, and generate reader journeys only from a canonical map source designed
to hold that intent.

### “Every node must be richly connected”

Dense linking can improve bottom-up exploration. It can also produce noise, unstable
maintenance, and generic edges that convey no decision. Recommended resolution:
review isolation and hubs, but optimize for meaningful access paths and truthful
relations rather than minimum edge counts.

### “Self-contained means context-free”

DITA uses context-free to mean avoiding location-dependent transitions so a topic can
be reused. Direct-arrival readers still need to recognize subject, purpose,
applicability, and assumed qualification. Recommended resolution: remove navigational
dependency, not semantic orientation.

### “Generated maps can remove human curation”

Generation can guarantee deterministic presentation of declared facts. It cannot
decide the safest or most useful path without a rule or authored data that already
contains that judgment. Recommended resolution: automate projection and validation;
retain accountable human ownership of map semantics.

### “A taxonomy is the same thing as an ontology or system architecture”

SKOS explicitly distinguishes informal knowledge-organization schemes from formal
facts about the world. Buzz's subject classification can help readers retrieve content
without asserting that its hierarchy is the product's runtime architecture.
Recommended resolution: document what each hierarchy means and never transfer
semantics from one view implicitly.

## Claim ledger

| Claim | Main support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Atomic nodes, semantic relationships, and reader maps are distinct architectural layers | DITA topic/map separation; local atomicity and relationship contracts; Red Hat module/assembly model | A small single-purpose corpus can collapse some layers operationally | High |
| A good atomic node is locally intelligible but need not explain everything | DITA locational independence; Red Hat self-contained modules; Every Page Is Page One qualified-reader model; local standalone test | Exact minimum context varies by genre, audience, and risk | High for principle; moderate for a universal checklist |
| One physical hierarchy cannot express all legitimate audience and task paths | DITA reuse across maps; faceted local metadata; direct inspection of the corpus tree | A single hierarchy may be adequate for a narrowly bounded corpus | High for Buzz |
| Buzz's current relationship vocabulary cannot represent a reader journey | Direct comparison of `relationships.schema.json` meanings with sequence, branch, prerequisite, and entry/exit needs | A particular path could be narrated in body prose, but not recovered reliably as canonical graph data | High |
| A generator cannot legitimately invent an audience-specific path from current relationships | Generated-content reproducibility principle; current relationship semantics; DITA maps as explicit context | Heuristics can propose paths for human review, but proposal is not authority | High |
| Controlled facets and labels support multiple views without content duplication | DITA subject schemes and conditional attributes; W3C SKOS | Buzz has not established a need for every possible facet or SKOS implementation | High for principle; moderate for additions |
| Current graph counts do not measure navigability | Local snapshot; optional edges; body-link/relationship distinction; broad dominance of `references` | The counts remain useful for selecting review cases | High |
| Reader journeys need scenario-based review in addition to structural validation | ISO audience/task orientation; Red Hat user-story assemblies; local validator boundary | This report did not run reader tests | High for need; moderate for proposed procedure |
| The proposed four-layer model is sufficient as a basis for synthesis | Combined source synthesis | It has not been trialed on a Buzz vertical slice and may need a separate traceability layer | Moderate |

## Limitations

- The local graph snapshot describes the current working tree on 2026-09-06, not a
  release tag or `origin/launchpad`. Several files in the research directory and one
  unrelated script are untracked; no claim is made that the snapshot represents a
  published corpus state.
- Graph extraction counted front-matter relationships only. It did not parse Markdown
  body links, references from code or issues, or search-engine reachability.
- Weakly connected components ignore edge direction and meaning. They are useful for
  detecting structural islands, not for proving a usable route.
- No representative Buzz reader completed a task using the current corpus or the
  candidate architecture. Usability and findability evidence belongs in topic 6.
- ISO's public browser exposes definitions, abstract, and contents but not the full
  paid normative text. This report does not assert conformance.
- DITA is an XML architecture, SKOS an RDF knowledge-organization model, Red Hat's
  guide an AsciiDoc practice, and Every Page Is Page One practitioner guidance. Their
  concepts transfer; their file formats and complete rule sets do not automatically
  fit Buzz.
- The report did not inspect live GitHub tasks for every planned generated artifact.
  Local committed templates and standards establish that the family is planned, not
  its final implementation.
- The proposed map record and map families are conceptual. Storage format, schema,
  ownership, review frequency, and rendering remain undecided.
- The four-layer model may need a fifth explicit traceability layer once topic 4's
  coverage obligations are implemented. This report treats traceability as a consumer
  of nodes, classification, and semantic connections rather than settling that design.

## Implications for the final synthesis

The eventual content-review checklist should not stop after checking individual node
quality. It should include four passes:

1. **Node:** atomic boundary, standalone meaning, local context, and restrained reuse.
2. **Connection:** body-link purpose, relationship truth, direction, and canonical
   ownership.
3. **Journey:** audience, entry state, ordering, branches, outcome, and direct-arrival
   recovery.
4. **Corpus:** controlled facets, map coverage, graph risks, generated-view provenance,
   and architectural drift.

Before adopting new fields or tooling, Buzz should pilot the model on one bounded
vertical slice—for example, an operator journey that crosses architecture,
configuration, procedure, verification, and recovery nodes. The pilot should:

- create an authored map outside the node bodies;
- reuse existing canonical nodes without copying their main content;
- identify context that genuinely belongs in each node versus the assembly;
- compare the authored journey with what the current relationship graph can generate;
- run isolation, hub, cycle, status, and broken-link diagnostics;
- ask a reader to enter both from the map and directly at a middle node; and
- record maintenance cost and reviewer disagreement.

That experiment would test the central proposal: atomic documentation becomes a
coherent corpus when canonical nodes remain independently meaningful and separate,
human-owned maps supply reader context that the nodes should not duplicate.

## Sources

### Local corpus sources

- [`AGENTS.md`](../../docs/corpus/AGENTS.md)
- [`README.md`](../../docs/corpus/README.md)
- [`node.schema.json`](../../docs/corpus/schema/node.schema.json)
- [`relationships.schema.json`](../../docs/corpus/schema/relationships.schema.json)
- [`atomicity.md`](../../docs/corpus/standards/atomicity.md)
- [`linking.md`](../../docs/corpus/standards/linking.md)
- [`identifiers.md`](../../docs/corpus/standards/identifiers.md)
- [`taxonomy.md`](../../docs/corpus/standards/taxonomy.md)
- [`generated-content.md`](../../docs/corpus/standards/generated-content.md)
- [`generated-index.md`](../../docs/corpus/templates/generated-index.md)
- [`validate.py`](../../project-intelligence/corpus/validate.py)
- [`ADR-0028-corpus-canonical-representation.md`](../../decisions/ADR-0028-corpus-canonical-representation.md)
- [`ADR-0050-canonical-corpus-supersedes-handbook.md`](../../decisions/ADR-0050-canonical-corpus-supersedes-handbook.md)
- [`VISION.md`](../../../VISION.md)
- [`launchpad/VISION.md`](../../VISION.md)

### External sources

- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/standard/77451.html)
- [ISO/IEC/IEEE 26514:2022 public browsing material](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
- [OASIS DITA 1.3 standard](https://www.oasis-open.org/standard/ditav1-3/)
- [OASIS DITA 1.3 — DITA topics](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/topicover.html)
- [OASIS DITA 1.3 — Disciplined, topic-oriented writing](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/topicorientation.html)
- [OASIS DITA 1.3 — Definition of DITA maps](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/definition-of-ditamaps.html)
- [OASIS DITA 1.3 — Purpose of DITA maps](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/purpose-of-ditamaps.html)
- [OASIS DITA 1.3 — DITA map attributes](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/ditamap-attributes.html)
- [OASIS DITA 1.3 — Subject scheme maps and their usage](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/subject-scheme-maps-and-usage.html)
- [OASIS DITA 1.3 — Conditional processing attributes](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/conditional-processing-attributes.html)
- [W3C — SKOS Simple Knowledge Organization System Reference](https://www.w3.org/TR/2009/REC-skos-reference-20090818/)
- [W3C — SKOS Simple Knowledge Organization System Primer](https://www.w3.org/TR/2009/NOTE-skos-primer-20090818/)
- [Red Hat — Modular Documentation Reference Guide](https://redhat-documentation.github.io/modular-docs/)
- [Mark Baker — *Every Page Is Page One* overview](https://everypageispageone.com/the-book/)
- [Mark Baker — Bottom-Up Information Architecture Q and A, Part 1](https://everypageispageone.com/2015/02/10/bottom-up-information-architecture-q-and-a-part-1/)
