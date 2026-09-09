---
description: Research into evaluating architecture-documentation quality in the Buzz documentation corpus.
tags: [documentation, corpus, architecture, views, stakeholders, quality-attributes, decisions, traceability, research]
---

# Architecture-documentation quality

Researched 2026-09-07. This is research, not an adopted corpus standard.

## Research question

How should Buzz determine whether its architecture documentation lets intended
stakeholders understand system boundaries, structures, interactions, quality-attribute
reasoning, decisions, deployment, and uncertainty well enough to make or verify a
change?

The investigation considered ten subquestions:

1. What is the object being reviewed: the architecture, its description, or the
   implementation's conformance to that description?
2. Which stakeholders and work should determine what architecture information is
   included?
3. What makes a set of views sufficient without requiring every possible view?
4. What information must accompany a diagram for it to function as an architecture
   model rather than an illustration?
5. How should context, structural, runtime, deployment, and cross-cutting views relate?
6. How should business goals, quality attributes, constraints, decisions, tactics,
   trade-offs, and risks be connected?
7. How should current state, intended state, uncertainty, and known divergence be
   represented?
8. What evidence shows that documentation supports stakeholder tasks rather than merely
   conforming to a template?
9. How much documentation is proportionate to a system's risk, novelty, volatility, and
   audience?
10. What does the current Buzz architecture corpus make easy or difficult to establish?

## Bottom line

Architecture-documentation quality is **fitness for identified stakeholder uses**, not
the presence of a prescribed diagram set. A strong architecture description forms a
coherent, bounded argument:

> **Purpose and concerns → selected views and models → correspondences between them →
> decisions and rationale → quality scenarios and evidence → implementation status,
> risks, and gaps.**

Three review targets must remain separate:

1. **Description quality:** Can the intended reader find, interpret, relate, and use the
   architecture information for a named task?
2. **Architecture quality:** Does the design actually satisfy its important business
   and quality goals, with acceptable risks and trade-offs?
3. **Conformance and currency:** Does the implemented and deployed system match the
   description at the claimed revision and lifecycle state?

A documentation review can find missing rationale, ambiguous boundaries, inconsistent
views, or an unusable deployment model. It cannot establish that the architecture is
good. A design evaluation such as ATAM can expose risks and trade-offs, but it does not
establish that documentation is current. A code or runtime comparison can establish
divergence without showing that the document serves its audience. A future Buzz
checklist should say which of the three it is testing on every item.

The current Buzz corpus has valuable node-level properties: architecture nodes identify
scope and omissions, distinguish observed behavior from intended direction, cite
evidence, and often expose failure and trust boundaries. It does not yet read as one
coherent architecture description. In the snapshot inspected, 48 nodes declare
`type: architecture`; all are `draft`, only seven contain Mermaid diagrams, two declare
any relationships, and five relationship edges exist in total. The active architecture
templates require diagrams and supporting structure that many current instances do not
contain. More importantly, the corpus supplies little explicit linkage from stakeholder
concerns and quality drivers through decisions to views, evidence, and risks. Those are
description gaps; they are not evidence that Buzz's underlying architecture is poor.

## Scope and method

This report concerns architecture documentation used to explain a software-intensive
system: its environment, boundaries, decomposition, interactions, deployment, important
cross-cutting mechanisms, decisions, quality reasoning, and known uncertainty. It
includes diagrams and prose, but treats both as representations of an architecture
model rather than as the model itself.

It does not:

- evaluate whether Buzz's architecture is technically good;
- perform an implementation-to-document conformance audit;
- prescribe one notation, framework, or universal list of diagrams;
- redesign the corpus schema or architecture templates;
- decide which draft nodes should become active;
- assess terminology, code examples, accessibility, or corpus-scale review in depth,
  which are later research topics; or
- introduce LLM-specific generation controls, which remain set aside for this research
  sequence.

Local inspection covered the architecture directories, every node declaring
`type: architecture`, active architecture and diagram templates, the corpus schema and
validator boundaries, evidence and review standards, the older Launchpad architecture
document, and representative context, container, deployment, flow, principle, and
capability nodes. Counts came from a read-only structural and lexical scan of the current
working tree. A lexical scan can establish the presence of syntax or words; it cannot
establish whether a concern is adequately addressed.

External evidence was selected in this order:

1. the public page for ISO/IEC/IEEE 42010:2022 and explanatory material for its
   predecessor;
2. the Software Engineering Institute's *Views and Beyond* and structured architecture-
   documentation review material;
3. the C4 model's official diagram guidance and review checklist;
4. arc42's official architecture-documentation guidance;
5. the SEI's quality-attribute and ATAM material;
6. the original Architecture Decision Record proposal; and
7. empirical studies of developers' architecture-documentation needs and whether a
   structured format improves architecture understanding.

The full normative text of ISO/IEC/IEEE 42010:2022 was not publicly accessible during
this research. Claims about the current edition are therefore limited to ISO's public
abstract. Older IEEE 1471 material is used only to explain the stakeholder-and-viewpoint
model, not to claim conformance with the 2022 standard.

## What architecture-documentation quality means

### Architecture and architecture description are different objects

[ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) standardizes the
structure and expression of architecture descriptions and the conceptual relationships
among architectures, descriptions, frameworks, viewpoints, and model kinds. Its public
abstract explicitly does not prescribe a particular architecting method, notation,
tool, format, or medium.

The distinction matters operationally:

| Review object | Question | Appropriate evidence |
|---|---|---|
| Architecture description | Can a stakeholder use the representations to answer the questions needed for a task? | Task-based review, source inspection, consistency checks, reader observation |
| Architecture | Does the design satisfy its drivers with acceptable trade-offs and risks? | Architecture evaluation, scenarios, analysis, prototypes, measurements |
| Implementation conformance | Does code, configuration, infrastructure, and runtime behavior realize the described design? | Code/configuration mapping, tests, deployment inspection, runtime evidence |

The SEI's [structured approach to reviewing architecture documentation](https://www.sei.cmu.edu/library/a-structured-approach-for-reviewing-architecture-documentation/)
makes the same boundary explicit: reviewing the documentation is not an evaluation of
architecture quality. It defines documentation quality relative to an anticipated use
and organizes reviews around purpose, stakeholders, their questions, expected answers,
and evidence. A later checklist should preserve that boundary in its title and verdicts.

### Fitness for use precedes format

The stakeholder-and-concern model inherited from IEEE 1471 treats an architecture
description as multiple views governed by viewpoints selected to address stakeholder
concerns. The explanatory paper by Maier, Emery, and Hilliard says there is no fixed,
universal viewpoint set; the useful set depends on the stakeholders and their concerns
([PDF](https://www.iso-architecture.org/ieee1471/wav2001/positions/maier-emery-hilliard.pdf)).

SEI's [*Views and Beyond* collection](https://www.sei.cmu.edu/library/views-and-beyond-collection/)
likewise defines an architecture document as relevant views plus information that
applies across views. The operative word is *relevant*. A view is justified when it
answers an important question for a real stakeholder or supports an important analysis.

This makes four things review prerequisites:

- the intended stakeholders;
- the work or decisions they must perform;
- the concerns and questions arising from that work; and
- the acceptance evidence showing that the documentation answers them.

Buzz's `audiences` field is useful routing metadata, but `developer`, `operator`,
`reviewer`, and `agent` are broad categories. On their own they do not identify tasks,
concerns, required detail, or success criteria. “For operators” is less testable than
“lets the on-call operator locate the affected trust boundary and deployment component
during incident triage.”

### A view is more than a diagram

SEI's [agile architecture-documentation guidance](https://www.sei.cmu.edu/documents/2028/2003_004_001_14171.pdf)
summarizes a view package as more than a primary visual representation. Depending on the
view, useful supporting information includes an element catalog, relations, interfaces,
behavior, context, variability, rationale, analysis results, assumptions, and a glossary.
Information across views includes a roadmap, overview, mappings among views, common
background and constraints, and shared rationale.

The [C4 review checklist](https://c4model.com/diagrams/checklist) expresses a compact
diagram-level version of the same idea. A diagram should identify its title, type, scope,
and notation; name, type, and describe elements; and label relationships with enough
direction and technology or protocol detail to interpret them. C4 is explicitly
[notation- and tooling-independent](https://c4model.com/diagrams/notation).

A diagram therefore needs at least:

- declared purpose, viewpoint or diagram type, and scope;
- a notation legend when meaning is not self-evident;
- named elements with responsibilities or semantics;
- named relationships, direction, and interaction meaning;
- interfaces or protocols where material;
- important behavior, variability, assumptions, and constraints;
- source or evidence boundaries; and
- prose that states claims the picture alone cannot safely carry.

Buzz's active [diagram standard](../../docs/corpus/standards/diagrams.md) already takes a
sound position: diagrams are text-native, cannot be the only source of a claim, and must
not create relationships absent from front matter. It also recommends diagrams only
where topology, sequence, state, or containment is the information shape. That avoids
two opposite errors: treating pictures as self-proving architecture and requiring
decorative diagrams where prose or a table is clearer.

### Relevant views form a system, not a gallery

Common architecture frameworks use different labels, but converge on several concern
families:

| Concern family | Questions a useful view answers |
|---|---|
| Context and boundaries | What is the system, what is outside it, who or what interacts with it, and where do trust or ownership boundaries lie? |
| Static structure | What are the major elements, their responsibilities, interfaces, dependencies, and permitted relationships? |
| Runtime behavior | How do elements collaborate in representative success, failure, recovery, concurrency, or lifecycle scenarios? |
| Deployment | What runs where in each material environment, under which network, identity, data, and operational constraints? |
| Data and state | Where is important state created, transformed, stored, replicated, retained, and protected? |
| Cross-cutting mechanisms | How are security, observability, configuration, errors, availability, consistency, and other shared concerns handled? |
| Decisions and rationale | Which consequential choices were made, why, against which alternatives, with what consequences and status? |
| Quality and risk | Which measurable scenarios matter, which tactics address them, what evidence exists, and what risks or debt remain? |

This table is a question inventory, not a mandatory document inventory. One view can
answer several concern families; a high-risk concern can require several views. The
[C4 model](https://c4model.com/) says system-context and container views are sufficient
for many teams and recommends component detail only where it adds value. arc42 similarly
advises selecting representative, architecturally relevant runtime scenarios rather
than documenting every possible sequence
([runtime view](https://docs.arc42.org/section-6/)).

The missing test in many diagram collections is **correspondence**. A container shown in
a structural view should be recognizable in the deployment view. A runtime participant
should map to a structural element. A trust boundary should be consistent across context,
flow, and deployment views. Names, identifiers, directions, cardinality, environment,
and lifecycle state should not silently change between views. Cross-view mappings are
architecture content, not navigation polish.

### Architecture drivers must lead to inspectable reasoning

An architecture description becomes decision-support material when it exposes why the
structure exists. The minimum reasoning chain is:

> **Business or mission goal → stakeholder concern → constraint or quality scenario →
> decision/tactic → affected views and elements → evidence/analysis → residual risk.**

The SEI's [quality-attribute guidance](https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes/)
uses concrete scenarios to turn broad words such as security, modifiability, performance,
and availability into analyzable requirements. arc42's
[quality-requirements guidance](https://docs.arc42.org/section-10/) recommends a small
set of prioritized quality goals and scenarios containing source, stimulus, environment,
affected artifact, response, and response measure.

This prevents claims such as “the system is scalable” from passing as architectural
reasoning. A reviewer should be able to identify the operational condition, affected
part, expected response, measurable threshold, and evidence—or see that these remain
unknown.

The SEI's [ATAM collection](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/)
adds another essential idea: quality attributes interact. Decisions create sensitivities,
trade-off points, and risks. “Improves security” is incomplete when the same choice
increases operational burden, latency, coupling, recovery time, or cost. Architecture
documentation should expose material negative consequences and unresolved risk, not
only justify the chosen design.

### Decisions require history without turning every detail into an ADR

Michael Nygard's original
[Architecture Decision Record proposal](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
argues for small, stable records of architecturally significant decisions: context,
decision, status, and positive and negative consequences, while retaining superseded
records as history. arc42's [decision guidance](https://docs.arc42.org/section-9/) adds
alternatives and rationale.

The useful threshold is significance, not architectural vocabulary. A decision merits
durable rationale when it materially affects structure, externally visible qualities,
dependencies, interfaces, constraints, cost of change, or a likely future dispute. The
architecture views should link to that decision; they should not copy its rationale into
several places and allow the copies to drift.

### Current state, target state, and uncertainty need separate labels

An architecture document can legitimately describe:

- the implemented current state;
- an approved target state;
- a transition or migration between them;
- a rejected or superseded state;
- an option under evaluation; or
- an unknown or disputed condition.

The defect is not describing a future state. It is making the reader infer which state
is shown. Every material view and claim should make its time/lifecycle scope visible,
identify known divergence, and state the evidence date or revision when claiming current
behavior.

Buzz's older [Launchpad architecture document](../../ARCHITECTURE.md) demonstrates the
value of explicitly separating intended end state from what existed at the time it was
written, and it lists ownership and open decisions. Its dated snapshot also demonstrates
why lifecycle labeling does not replace a freshness check: a clearly labeled historical
claim can still be unsuitable for a current operational question.

### “Just enough” is a risk decision

Architecture documentation has carrying cost. Every view introduces review,
correspondence, and freshness obligations. arc42 recommends concentrating on surprising,
risky, complex, and volatile parts rather than documenting every implementation detail
([building-block view](https://docs.arc42.org/section-5/)). C4 also warns against adding
deeper diagram levels automatically.

The proportionate set depends on:

- consequence and likelihood of misunderstanding;
- number and diversity of stakeholders;
- regulatory, security, or audit exposure;
- novelty, complexity, coupling, and distribution;
- volatility and cost of keeping a view current;
- reversibility and cost of the decisions involved; and
- whether the information can be generated reliably from a source of truth.

“Just enough” does not mean undocumented by default. It means that inclusion and
omission are argued against stakeholder tasks and risk. A deliberately absent component
view is stronger than an unexplained hole when context and container views already
support the needed decisions.

## How to review architecture documentation

### Begin with use scenarios

The SEI structured-review method begins by establishing review purpose and stakeholders,
then adapting question sets, planning the review, conducting it, and reporting results.
A practical Buzz review can turn that into a compact test:

1. **Name a stakeholder and consequential task.** For example: a developer changing
   authentication, an operator diagnosing event-delivery failure, or a reviewer checking
   whether a proposed service crosses the community boundary.
2. **Write the questions the stakeholder must answer.** Do not begin with filenames or
   expected diagrams.
3. **Locate the view or model that should answer each question.** Record absent,
   duplicated, ambiguous, or conflicting answers.
4. **Trace important answers.** Follow element names across context, structural,
   runtime, and deployment views; then follow the relevant decision, driver, evidence,
   and risk.
5. **Check the claimed lifecycle.** Determine whether the answer concerns current,
   intended, transitional, superseded, or uncertain state.
6. **Exercise the task.** Have an appropriate reader make the decision or perform the
   analysis, recording time, wrong turns, assumptions, unresolved questions, and
   confidence.

This produces evidence about fitness for use. A heading audit or diagram count does not.

### Then inspect document and model properties

For each view or model, check:

- identifiable purpose, stakeholder concerns, and scope;
- system-of-interest and environment;
- lifecycle state, version/revision, and applicability;
- consistent names and identifiers;
- defined notation and relationship semantics;
- responsibilities, interfaces, and externally important behavior;
- happy path plus material failure, degradation, recovery, and operational behavior;
- assumptions, constraints, variability, and omissions;
- links to decisions, evidence, implementation, and related views;
- agreement with mapped views; and
- ownership or a credible mechanism for detecting change.

For the architecture description as a whole, check concern coverage, cross-view
correspondence, driver-to-decision traceability, current/target separation, known risks,
and a navigable entry point or roadmap.

### Evaluate architecture only when that is the declared purpose

If the question is whether the design can satisfy important qualities, use quality
scenarios and an architecture-evaluation method. Trace scenarios to tactics and
decisions, identify sensitivity and trade-off points, and record evidence and risks. Do
not label a description-review result “architecture approved.” Conversely, do not fail a
clear and usable document merely because the reviewer disagrees with a documented
decision; that disagreement belongs in design evaluation or governance.

## Evidence against template-only review

A 2023 controlled study by Ernst and Robillard compared a structured *Views and Beyond*
document with a narrative document for architecture-understanding tasks. Across 65
participants, it found no significant association between document format and task
performance; familiarity with the source code was the dominant factor, and higher-order
questions drew participants toward source inspection
([paper](https://arxiv.org/abs/2305.17286)). The participants were upper-year students at
two universities, so the result should not be generalized to every professional setting.
It nevertheless refutes a safe assumption that applying a recognized template, by
itself, establishes usability.

A 2013 Fraunhofer IESE developer survey found recurring demand for an up-to-date big
picture, architectural decisions and rationale, components, interfaces, relationships,
and mappings to implementation
([PDF](https://www.iese.fraunhofer.de/content/dam/iese/dokumente/alte-dateien/study_software_architecture_documentation_for_developers_survey-en-fraunhofer_iese.pdf)).
The study used a convenience sample, mixed roles and organizations, optional questions,
and researcher categorization, and it predates today's Buzz toolchain. It is useful as
corroboration of task and currency needs, not as a universal ranking of required content.

Together these studies support a restrained conclusion: structure can improve
consistency and reviewability, but stakeholder task performance and implementation
mapping must be tested directly.

## Buzz current-state findings

### Snapshot and counting method

The inspected working tree contained 47 Markdown nodes under
`launchpad/docs/corpus/architecture/`:

| Directory | Nodes |
|---|---:|
| `context` | 6 |
| `containers` | 10 |
| `deployment` | 7 |
| `flows` | 14 |
| `principles` | 10 |

One additional node,
[`community-provisioning.md`](../../docs/corpus/capabilities/communities/community-provisioning.md),
declares `type: architecture`, bringing the schema-type total to 48. All 48 declare
`status: draft`.

The following figures are structural signals, not quality scores:

| Signal across the 48 `type: architecture` nodes | Observed |
|---|---:|
| Nodes containing a Mermaid fence | 7 |
| Nodes declaring one or more front-matter relationships | 2 |
| Declared relationship edges | 5 |
| Nodes whose body cites a specific `ADR-` identifier | 1 |
| Nodes whose body contains `risk` or `technical debt` | 1 |
| Nodes using the exact phrases `quality attribute`, `quality goal`, or `quality requirement` | 0 |
| Nodes whose body uses `trade-off` | 0 |
| Nodes with a glossary section | 0 |

Audience labels are broad: all 48 include `developer`, 40 include `agent`, 29 include
`operator`, and 20 include `reviewer`. These counts cannot show whether a node answers a
task for any of those audiences. Keyword absence also does not prove conceptual absence;
a node can discuss latency or trust without saying “quality attribute.” The counts are
useful only for locating questions that require semantic review.

### Strong node-level properties

Representative nodes—including
[`buzz-platform.md`](../../docs/corpus/architecture/context/buzz-platform.md),
[`relay.md`](../../docs/corpus/architecture/containers/relay.md),
[`hosted-topology.md`](../../docs/corpus/architecture/deployment/hosted-topology.md),
[`event-ingestion.md`](../../docs/corpus/architecture/flows/event-ingestion.md), and
[`community-is-security-boundary.md`](../../docs/corpus/architecture/principles/community-is-security-boundary.md)—show
several useful practices:

- evidence is attached to explicit claims rather than relegated to a bibliography;
- scope and omissions are routinely stated;
- current behavior and intended direction are often distinguished;
- trust, failure, rejection, and degradation behavior receive attention; and
- nodes are small enough to be reviewed independently.

These strengths align with earlier findings on
[evidence](03-truth-and-evidence-in-living-technical-documentation.md),
[atomic information architecture](05-information-architecture-for-atomic-documentation.md),
and [freshness](07-freshness-staleness-and-change-impact.md).

### The fragments do not yet expose a coherent description package

Only two architecture nodes declare relationships, with five edges total. One is the
platform context's reference to the corpus agent guide; the other is community
provisioning's four links to architecture nodes. This makes it difficult to establish
from encoded structure:

- which context, structural, runtime, and deployment views describe the same system;
- how a runtime participant maps to a container and then to infrastructure;
- which principle constrains which design element or flow;
- which stakeholder concerns each view resolves;
- where an architecture decision or quality driver is realized; and
- which view supersedes, refines, or depends on another.

Body links or shared vocabulary may carry some of these connections, but the sparse
relationship graph and absence of a current architecture roadmap mean a reviewer cannot
derive coverage or cross-view consistency mechanically. The corpus is presently better
described as a collection of architecture fragments than as an inspectable multi-view
architecture description.

The corpus [README](../../docs/corpus/README.md) also describes a much earlier state of
construction rather than providing a current architecture entry point. That is primarily
a freshness and navigation issue, but it removes the roadmap that *Views and Beyond*
expects across views.

### Drivers, decisions, and quality reasoning are weakly connected

The scan found almost no explicit decision-record, trade-off, risk, or quality-attribute
vocabulary in architecture-node bodies. Terminology alone is not the standard; the more
important semantic question is whether a reader can trace a driver through a decision
to a model, evidence, consequences, and residual risk. That trace is not visible in the
current node relationships.

Buzz has separate vision and decision material, including
[`launchpad/VISION.md`](../../VISION.md) and the ADR directory. The architecture nodes
do not need to duplicate it. They do need stable links where a driver or accepted
decision explains the architecture. Otherwise a correct structural description can say
*what* exists without exposing *why*, what it protects, or which change would violate an
important trade-off.

This is also where the distinctions from
[normative versus descriptive writing](09-normative-versus-descriptive-technical-writing.md)
matter. A principle, accepted decision, current implementation fact, and desired target
can all point toward the same design, but they are different claim types with different
authorities and conformance questions.

### Current nodes diverge from active templates

The active templates establish a stronger presentation contract than the current draft
instances follow:

- the [context template](../../docs/corpus/templates/architecture-context.md) calls for a
  system-context diagram, notation legend, business context, and technical context;
  existing context nodes contain generic Mermaid flowcharts but do not record a notation
  legend or the C4 fallback condition;
- the [container template](../../docs/corpus/templates/architecture-container.md) calls
  for an inline diagram, inventory, and communication summary; the ten current container
  nodes instead read as individual container profiles and contain no diagrams;
- the [deployment template](../../docs/corpus/templates/deployment.md) requires an inline
  diagram and container-to-infrastructure mapping; the seven deployment nodes contain no
  diagrams; and
- the [flow template](../../docs/corpus/templates/flow.md) calls for a Mermaid sequence
  diagram and explicit outcome/failure path; the fourteen current flow nodes contain no
  diagrams.

Because all of these nodes are `draft`, this is a current-snapshot mismatch, not proof
that an active contract has been violated in production. It may also expose a modelling
decision that needs human resolution: are “container” nodes intended to be system-level
container views or one-container reference pages? Renaming, restructuring, or changing
the template are all possible responses; research alone should not select among them.

The schema validator does not inspect body structure or diagram semantics. A node can
therefore pass structural validation while omitting every template section, and a
diagram can be present while semantically misleading. Buzz's active
[`review-requirements`](../../docs/corpus/standards/review-requirements.md) and
[`evidence`](../../docs/corpus/standards/evidence.md) standards correctly assign source
support and body-to-ledger agreement to human review. Architecture review needs an
additional semantic layer for concerns, view sufficiency, correspondence, rationale,
and task fitness.

## Candidate content-review checklist

These are research-derived candidates, not current Buzz requirements. Apply them to a
declared review purpose; do not turn every item into a requirement for every node.

### Review target and use

- [ ] The review says whether it evaluates description quality, architecture quality,
      implementation conformance, or a clearly separated combination.
- [ ] Intended stakeholders are named more specifically than a broad audience label when
      their concerns differ.
- [ ] At least one consequential task or decision is named for each primary stakeholder.
- [ ] The questions the documentation must answer for those tasks are explicit.
- [ ] Success criteria concern task completion, correct decisions, or resolved questions,
      not template completion alone.

### Scope, identity, and lifecycle

- [ ] The system of interest and its external environment are unambiguous.
- [ ] Ownership, trust, security, data, and deployment boundaries relevant to the view
      are identified.
- [ ] The view states whether it represents current, intended, transitional,
      superseded, proposed, or uncertain state.
- [ ] Current-state claims identify a meaningful revision, evidence date, or other
      freshness boundary.
- [ ] Known implementation divergence and unresolved uncertainty are visible.
- [ ] Scope, assumptions, constraints, variability, and deliberate omissions are stated.

### View selection and internal quality

- [ ] Each view exists to answer an identified stakeholder concern or support an
      analysis; redundant decoration is excluded.
- [ ] The selected views cover the material context, structural, runtime, deployment,
      data, security, and operational questions for this system and review purpose.
- [ ] The view declares its type or viewpoint, purpose, and scope.
- [ ] Notation and relationship semantics are defined where they are not self-evident.
- [ ] Elements are named and their responsibilities are described.
- [ ] Relationships have meaningful labels and direction; relevant interfaces,
      protocols, cardinality, and technology are supplied.
- [ ] Representative failure, degradation, recovery, and concurrent behavior accompany
      happy-path behavior where consequential.
- [ ] Prose, tables, or an element catalog carry claims that a diagram alone cannot.

### Cross-view coherence

- [ ] Elements and relationships can be mapped across context, structural, runtime,
      deployment, and data views where applicable.
- [ ] Names, identifiers, boundaries, directions, and lifecycle states are consistent
      across those views.
- [ ] Any intentional inconsistency or abstraction difference is explained.
- [ ] The description has a roadmap or entry point showing which views exist, their
      scope, and how they relate.
- [ ] Corpus relationships encode material dependencies or refinements rather than
      leaving every connection implicit in prose.

### Drivers, decisions, quality, and risk

- [ ] The most important business or mission goals and external constraints are
      discoverable from the architecture description.
- [ ] Prioritized quality goals are stated through concrete, measurable scenarios where
      analysis or acceptance depends on them.
- [ ] Architecturally significant decisions link to context, alternatives, rationale,
      status, and positive and negative consequences.
- [ ] Views identify where consequential decisions and tactics are realized.
- [ ] Analysis, tests, measurements, prototypes, or operational evidence support claims
      about important quality responses.
- [ ] Sensitivity points, trade-offs, assumptions, residual risks, and technical debt are
      visible rather than converted into confident prose.

### Implementation and maintainability

- [ ] Major documented elements map to code, configuration, infrastructure, ownership,
      or other maintained artifacts at the appropriate abstraction.
- [ ] A stakeholder can follow a documented flow into the artifacts needed to inspect or
      change it.
- [ ] A credible change signal, owner, review trigger, or generation path exists for
      volatile views.
- [ ] Duplicated rationale and facts have an identified source of truth.
- [ ] The information set is proportionate to risk and use; omitted views have a reason,
      and included views have a maintenance justification.

### Task-based acceptance

- [ ] Representative users can perform the named tasks with the documentation and
      allowed supporting artifacts.
- [ ] The review records time, wrong turns, incorrect answers, unresolved questions,
      source-code detours, and reader confidence.
- [ ] A second reviewer can reproduce consequential conclusions from the cited evidence.
- [ ] Findings distinguish missing documentation, poor design, and implementation drift.

## Candidate measures

Counts should diagnose where to inspect, not become a universal score.

| Measure | What it can indicate | What it cannot establish |
|---|---|---|
| Concern-to-view coverage | Questions with no apparent representation | Whether the answer is correct or usable |
| Cross-view mapping coverage | Elements or relationships without correspondence | Whether mappings reflect reality |
| Driver-to-decision-to-view trace coverage | Missing reasoning links | Whether the decision is good |
| Quality-scenario evidence coverage | Claims lacking measurable evidence | Whether all important qualities were selected |
| Architecture task success rate | Whether readers completed declared tasks correctly | Fitness for untested audiences and tasks |
| Time, wrong turns, and source detours | Friction and hidden dependencies | Root cause without observation and follow-up |
| Current-state verification age | Likely freshness exposure | Actual staleness |
| Known divergence count and age | Visible conformance debt | Undocumented divergence |
| Unmapped implementation elements | Possible abstraction or coverage gaps | Whether every low-level element belongs in the documentation |
| Template-section presence | Structural consistency | Semantic completeness, correctness, or usefulness |
| Diagram and relationship counts | Possible thinness or isolation | Quality; zero can be appropriate for a principle or decision |

A useful scorecard should retain item-level findings and severity. Collapsing all of this
into one percentage would hide whether a low result means an absent deployment model,
stale names, an unresolved security trade-off, or an untested audience.

## Common failure modes

1. **Template completion as quality.** Every heading exists, but readers still cannot
   answer their questions or make a safe change.
2. **Diagram as authority.** A picture makes claims with no supporting prose, evidence,
   lifecycle, or relationship semantics.
3. **View gallery.** Several attractive diagrams exist without mappings, shared names,
   or an explanation of how they compose.
4. **Structure without drivers.** Components and flows are listed, but no important goal,
   quality scenario, constraint, or decision explains why they have that form.
5. **Happy-path architecture.** Runtime views omit rejection, degradation, recovery,
   security failure, backpressure, and operational behavior.
6. **Current and target collapse.** A desired topology is written as present fact, or a
   current limitation is mistaken for permanent policy.
7. **Rationale duplication.** The same decision is restated in several views and drifts
   from its governing record.
8. **Quality adjectives without scenarios.** “Secure,” “resilient,” and “scalable” are
   asserted without conditions, measures, tactics, or evidence.
9. **Architecture review inflation.** A documentation pass is reported as proof that the
   design is sound.
10. **Exhaustive inventory.** Low-value detail increases maintenance cost and obscures
    risky, surprising, or volatile architecture.
11. **Code as the only map.** Familiar developers can infer the architecture from source,
    while new developers, operators, reviewers, and decision-makers cannot.
12. **Tool-shaped content.** Documentation is organized around what a diagram generator
    or schema can express rather than the questions stakeholders need answered.

## Competing positions and how the evidence resolves them

### Fixed document set versus stakeholder-selected views

A fixed set improves consistency, predictability, and automation. ISO/IEEE's
stakeholder-and-viewpoint model, SEI, C4, and arc42 all leave room to select what is
relevant. The defensible Buzz position is a small expected baseline plus explicit
concern/risk-based inclusion and omission—not an unlimited menu and not a universal full
template.

### Diagrams versus prose

Diagrams are efficient for topology, containment, sequence, state, and mapping. They are
weak at evidence, rationale, conditions, uncertainty, and precise semantics unless those
are supplied around them. The right unit is a view package: the smallest combination of
visual, prose, table, and source links that answers the stakeholder question.

### Manual descriptions versus generated views

Generated models can improve repeatability and reduce drift when a reliable source
contains the required semantics. They can also omit intent, rationale, rejected
alternatives, quality drivers, and uncertainty. Generation is valuable for observable
structure and inventory; human-maintained reasoning remains necessary unless those
semantics have an authoritative structured source.

### One architecture document versus atomic nodes

A monolith makes the whole easier to browse but harder to maintain and review. Atomic
nodes improve ownership and focused updates but require a roadmap, typed relationships,
stable identifiers, and cross-view mappings. Buzz has chosen atomic nodes; it therefore
inherits the integration obligations rather than escaping them.

### Comprehensive documentation versus minimal documentation

Comprehensiveness reduces some discovery gaps but increases drift and cognitive load.
Minimal documentation reduces carrying cost but can externalize architecture knowledge
into a few people's memories or source-code familiarity. Risk, stakeholder diversity,
volatility, and decision cost should determine the level—not an abstract preference for
more or less.

## Claim ledger

| Claim | Support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Architecture-description quality is relative to anticipated stakeholder use. | ISO/IEC/IEEE 42010 public scope; SEI structured-review method; IEEE 1471 explanatory material | A project can still impose a mandatory baseline independent of a particular review task. | High |
| A coherent architecture description requires relevant views plus information and mappings across views. | SEI *Views and Beyond* collection and agile-documentation report | Small systems may express several views in one compact artifact. | High |
| A diagram needs scope, notation, element, and relationship semantics to be reviewable. | C4 official checklist; SEI view guidance | Familiar teams can infer conventions, but that does not make the artifact portable or independently reviewable. | High |
| Quality attributes should be represented through concrete scenarios and tied to decisions and evidence. | SEI quality-attribute and ATAM material; arc42 quality guidance | Scenario form can be disproportionate for low-consequence qualities or purely explanatory overview material. | High |
| Template conformance alone does not establish architecture understanding. | Ernst and Robillard controlled study; conceptual separation between format and task fitness | Student sample and two formats limit generalization; templates may still improve consistency and review efficiency. | Medium-high |
| Developers value currency, big picture, rationale, components, relationships, and implementation mapping. | Fraunhofer IESE survey | Convenience sample, mixed roles, self-report, and 2013 context limit generalization. | Medium |
| Buzz's current architecture nodes are strong as bounded evidence-led fragments but weakly integrated as a multi-view package. | Local inspection: scope sections, evidence ledgers, 48 draft nodes, seven diagrams, two related nodes, five edges, sparse decision/quality terminology | Body semantics and unstated conventions may carry connections a structural scan misses; no stakeholder task study was run. | Medium-high |
| Current node/template divergence is invisible to the validator. | Active templates; schema; validator and review standards; local node inspection | Human review may already catch the divergence; all relevant nodes are draft. | High |
| Sparse diagrams are not inherently a quality defect. | C4/arc42 proportionality; Buzz diagram standard | For view types whose declared contract requires topology or sequence, a missing representation is a concrete structural gap. | High |
| The report cannot determine whether Buzz's architecture is sound or whether implementation conforms. | Review scope; no design evaluation or code/runtime conformance audit performed | Individual local evidence entries support some current-behavior claims, but not a corpus-wide verdict. | High |

## Implications for the future Buzz checklist

1. Start an architecture review by choosing the review object and stakeholder tasks.
2. Review the architecture corpus as both individual nodes and one connected description.
3. Treat active templates as minimum presentation contracts only after resolving what
   each node type is meant to represent.
4. Require concern coverage and cross-view mapping where risk justifies them; do not
   require every framework section universally.
5. Add explicit trace tests from goals and quality scenarios through decisions, views,
   evidence, and risks.
6. Keep current, target, transitional, and uncertain states visibly separate.
7. Use automated checks for syntax, presence, target resolution, identifiers, and
   mechanically derivable mappings; reserve semantic sufficiency and diagram meaning for
   human review.
8. Validate important architecture documentation through realistic developer, operator,
   agent, and reviewer tasks.
9. Record description defects, design risks, and implementation divergence in separate
   finding categories.
10. Prefer a small set of severe, traceable findings over a single architecture-
    documentation score.

## Uncertainties and limitations

- The full text of ISO/IEC/IEEE 42010:2022 was not available, so this report does not
  claim clause-level conformance or reproduce normative requirements from it.
- IEEE 1471 explanatory material predates the current edition and is background only.
- The SEI book itself was not fully accessible; the report relies on the official book
  page, collection page, and freely available SEI report summarizing the method.
- C4 and arc42 are practitioner frameworks, not evidence that their sections or diagrams
  are universally necessary.
- Nygard's ADR article is influential first-person practitioner experience, not a
  controlled study.
- The empirical studies have material external-validity limits described above.
- Local findings are a working-tree snapshot on 2026-09-07. No commit baseline was
  assigned because the research directory and corpus work may contain uncommitted state.
- String counts can undercount concepts expressed with different language and overcount
  incidental mentions. They are prompts for semantic review, not defect counts.
- Representative nodes were read closely, but no stakeholder performed a real
  architecture task during this research.
- No code, configuration, deployment, or runtime conformance audit was performed.
- All 48 architecture-typed nodes are draft, so findings describe maturity and
  integration gaps, not noncompliance by active documents.

## Questions for synthesis

1. Which architecture tasks must the future corpus review actually support for
   developers, operators, agents, and reviewers?
2. What minimum view baseline, if any, applies to every Buzz system, and which views are
   selected by risk and concern?
3. Should individual `containers` nodes remain component profiles, be renamed, or be
   assembled beneath a distinct system-level container view?
4. Where should the architecture roadmap and cross-view mappings live in an atomic
   corpus?
5. Which quality goals and scenarios are important enough to become architecture review
   anchors?
6. How should architecture nodes link to vision, decisions, implementation evidence,
   deployment state, risks, and supersession without duplicating them?
7. Which template rules should be schema- or lint-enforced, and which require semantic
   human review?
8. What sample tasks would constitute acceptable evidence that the architecture corpus
   is usable?

## Sources

### Standards and standards background

- ISO, [ISO/IEC/IEEE 42010:2022 — Software, systems and enterprise — Architecture description](https://www.iso.org/standard/74393.html).
- David Emery, Rich Hilliard, and Mark Maier,
  [*ANSI/IEEE 1471 and Systems Engineering*](https://www.iso-architecture.org/ieee1471/wav2001/positions/maier-emery-hilliard.pdf).
- IEEE Standards Association,
  [IEEE 1016-2009 — Software Design Descriptions](https://standards.ieee.org/ieee/1016/4502/)
  (inactive-reserved; corroborating historical source only).

### Architecture documentation and evaluation

- Software Engineering Institute,
  [*Views and Beyond Collection*](https://www.sei.cmu.edu/library/views-and-beyond-collection/).
- Software Engineering Institute,
  [*Documenting Software Architectures: Views and Beyond, Second Edition*](https://www.sei.cmu.edu/library/documenting-software-architectures-views-and-beyond-second-edition/).
- Software Engineering Institute,
  [*Architecture Documentation and Agile Development*](https://www.sei.cmu.edu/documents/2028/2003_004_001_14171.pdf).
- Software Engineering Institute,
  [*A Structured Approach for Reviewing Architecture Documentation*](https://www.sei.cmu.edu/library/a-structured-approach-for-reviewing-architecture-documentation/).
- Software Engineering Institute,
  [*Reasoning About Software Quality Attributes*](https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes/).
- Software Engineering Institute,
  [*Architecture Tradeoff Analysis Method Collection*](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/).
- C4 model, [official introduction](https://c4model.com/),
  [diagram types](https://c4model.com/diagrams),
  [review checklist](https://c4model.com/diagrams/checklist), and
  [notation guidance](https://c4model.com/diagrams/notation).
- arc42, [official documentation](https://docs.arc42.org/home/), including
  [goals and stakeholders](https://docs.arc42.org/section-1/),
  [building blocks](https://docs.arc42.org/section-5/),
  [runtime](https://docs.arc42.org/section-6/),
  [deployment](https://docs.arc42.org/section-7/),
  [cross-cutting concepts](https://docs.arc42.org/section-8/),
  [decisions](https://docs.arc42.org/section-9/),
  [quality requirements](https://docs.arc42.org/section-10/), and
  [risks and technical debt](https://docs.arc42.org/section-11/).
- Michael Nygard,
  [*Documenting Architecture Decisions*](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

### Empirical evidence

- Neil A. Ernst and Martin P. Robillard,
  [*Understanding Software Architecture through Structure and Narrative*](https://arxiv.org/abs/2305.17286), 2023.
- Fraunhofer IESE,
  [*Software Architecture Documentation for Developers: A Survey*](https://www.iese.fraunhofer.de/content/dam/iese/dokumente/alte-dateien/study_software_architecture_documentation_for_developers_survey-en-fraunhofer_iese.pdf), 2013.

### Buzz material inspected

- [Corpus authoring guide](../../docs/corpus/AGENTS.md)
- [Corpus README](../../docs/corpus/README.md)
- [Diagram standard](../../docs/corpus/standards/diagrams.md)
- [Evidence standard](../../docs/corpus/standards/evidence.md)
- [Review-requirements standard](../../docs/corpus/standards/review-requirements.md)
- [Status standard](../../docs/corpus/standards/status.md)
- [Architecture context template](../../docs/corpus/templates/architecture-context.md)
- [Architecture container template](../../docs/corpus/templates/architecture-container.md)
- [Deployment template](../../docs/corpus/templates/deployment.md)
- [Flow template](../../docs/corpus/templates/flow.md)
- [Invariant template](../../docs/corpus/templates/invariant.md)
- [Launchpad architecture document](../../ARCHITECTURE.md)
- [Launchpad vision](../../VISION.md)
