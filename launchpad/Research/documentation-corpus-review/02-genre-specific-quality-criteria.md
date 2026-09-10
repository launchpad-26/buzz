---
description: Research into genre-specific content criteria for reviewing the Buzz documentation corpus.
tags: [documentation, corpus, genre, templates, review, research]
---

# Genre-specific quality criteria

Researched 2026-09-06. This is research, not an adopted corpus standard.

## Research question

What genre model and genre-specific criteria could help reviewers decide whether a
Buzz corpus node contains the right kind of information, given that the corpus has
26 templates and a separate `type` field that classifies subject matter rather than
writing form?

The investigation considered five subquestions:

1. Which distinctions between documentation forms recur across authoritative
   information models and documentation frameworks?
2. Which criteria should apply to every node, and which only make sense for a
   particular form of writing?
3. Can the 26 Buzz templates be grouped into a smaller number of review families
   without erasing meaningful differences between them?
4. How should reviewers handle a node that mixes explanation, description,
   instruction, requirements, or assurance?
5. What should this research establish now, and what should remain for the later
   specialist studies in the research queue?

## Bottom line

Genre should be treated as a **content contract**, not merely as a filename, heading
pattern, or visual layout. The contract begins with the reader's need and the
document's dominant communicative act:

- explain a subject;
- describe facts about a subject;
- model a system from a defined viewpoint;
- direct action;
- impose a constraint;
- make an assurance case;
- preserve a decision; or
- expose navigation derived from other material.

The Buzz corpus should not be reviewed as though every node has the same completeness
requirements. A procedure without ordered action is incomplete even if its prose is
excellent. A reference can be complete without explaining why the system was designed
that way. A policy must identify authority and enforcement; a descriptive page must
not accidentally create requirements. A threat model and a test strategy are not
adequate merely because they describe the system accurately: each must show the
analysis or assurance work it exists to record.

The most practical model for a future review is therefore three-layered:

1. **Universal criteria** apply to every node: a defined reader need, honest scope,
   factual integrity, relevant evidence, internal coherence, and explicit omissions.
2. **Family criteria** apply to eight broad functional families: explanatory,
   descriptive reference, architecture/model, normative, procedural/operational,
   verification/assurance, decision/historical, and generated/navigation.
3. **Template overlays** preserve the narrower obligations and boundaries of each of
   the 26 existing templates.

This eight-family grouping is a research synthesis for review purposes. It is not a
proposal to replace or rename the templates, change the schema, or reorganize the
published corpus. Confidence is **high** that genre-specific review is necessary and
that the corpus `type` field is not genre. Confidence is **moderate** that these eight
families are the best consolidation; they have not yet been tested through an actual
corpus review.

## Scope and method

This study is limited to **content form**: what kind of writing a node is, what job it
does for a reader, and what information that job requires. It does not establish:

- detailed runbook and procedure criteria, which belong to topic 8;
- the full treatment of normative language, which belongs to topic 9;
- detailed architecture-documentation criteria, which belong to topic 10;
- terminology rules, executable-example rules, accessibility conformance, corpus-scale
  sampling, or public security-disclosure rules, which have their own later topics.

Local inspection covered:

- all 26 files in `launchpad/docs/corpus/templates/`;
- `launchpad/docs/corpus/schema/node.schema.json`;
- `launchpad/docs/corpus/standards/taxonomy.md`; and
- the corpus-wide atomicity, evidence, confidence, and review guidance used in the
  first research loop.

External research prioritized primary or authoritative sources:

- ISO/IEC/IEEE 26514's public description of software information for users;
- OASIS DITA's technical-content information types;
- Diátaxis's reader-need model;
- The Good Docs Project's maintained content-type templates;
- ISO/IEC/IEEE 42010 and the C4 model for architecture descriptions;
- BCP 14 and the RFC style guide for requirements-bearing specifications;
- ISO/IEC/IEEE 29119's public testing material;
- MADR for decision records;
- OWASP for threat modelling; and
- one empirical software-documentation quality study that compared genres.

Paid standards were not obtained. This report uses only their public abstracts or
public browsing material and does not claim conformance with ISO/IEC/IEEE 26514,
ISO/IEC/IEEE 42010, or ISO/IEC/IEEE 29119.

## The critical local distinction: surface is not genre

The schema defines `type` as “the corpus surface this node documents” and constrains
it to 13 subject-area values such as `architecture`, `operations`, `governance`, and
`verification`. The corpus taxonomy standard confirms that this field answers **what
surface is being documented**. It does not answer **what kind of document this is**.
([node schema](../../docs/corpus/schema/node.schema.json),
[taxonomy standard](../../docs/corpus/standards/taxonomy.md))

The 26 templates answer the second question. A node with `type: operations` might be
a concept, a reference, a procedure, a runbook, a policy, or an invariant. Conversely,
a procedure could plausibly document a development, release, operations, ingestion,
or agent surface. Treating `type` as genre would therefore create two review errors:

1. applying content criteria based on the subject label rather than the reader's need;
2. assuming that two nodes with the same `type` require the same internal content.

For review purposes, a node needs both coordinates:

| Coordinate | Review question | Local mechanism |
|---|---|---|
| Subject surface | What part of Buzz does this node document? | Front-matter `type` |
| Writing form | What job does this node perform for its reader? | Template and content |

The second coordinate is not currently a schema field. A reviewer must infer it from
the template used, the node's stated purpose, and the content itself. This report does
not recommend adding another field; it only identifies the distinction a content
review must preserve.

## What the strongest sources establish

### Reader need, not subject matter, determines the basic form

Diátaxis distinguishes tutorial, how-to, reference, and explanation by two questions:
whether the content informs action or cognition, and whether it serves study or work.
Each form responds to a different reader need and must be written differently. It
also identifies blurred boundaries between forms as a common source of documentation
problems.
([Diátaxis: start here](https://diataxis.fr/start-here/))

OASIS DITA independently distinguishes concept, task, reference, glossary, and
troubleshooting information. Its concept type builds understanding; reference
separates fact-based material from concepts and tasks; task content identifies
prerequisites, commands, results, and supporting information; and a glossary entry
defines one sense of one term. DITA 1.3 adds a troubleshooting specialization rather
than treating all corrective content as an undifferentiated task.
([OASIS DITA 1.3 overview](https://docs.oasis-open.org/dita/dita/v1.3/os/part0-overview/introduction/about-the-dita-specification.html),
[OASIS DITA technical-content types](https://docs.oasis-open.org/dita/v1.2/os/spec/archSpec/dita_technicalContent_InformationTypes.html),
[OASIS DITA troubleshooting](https://docs.oasis-open.org/dita/dita/v1.3/cos01/part2-tech-content/archSpec/technicalContent/TroubleshootingElements.html))

ISO/IEC/IEEE 26514's public material defines information for users as information that
provides a target audience with concepts, procedures, and reference material for safe,
effective, and efficient use. Its scope also includes troubleshooting and information
for specialized interfaces. This supports the core distinction while showing that a
real technical corpus extends beyond a single four-part website model.
([ISO/IEC/IEEE 26514:2022](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:26514:ed-1:v1:en))

The Good Docs Project supplies separate templates for concepts, how-to guides,
reference, tutorials, troubleshooting, API reference, installation, and other common
forms. Its concept guide explicitly advises keeping one concept per document and
avoiding instructional and referential material in that form.
([Good Docs templates](https://gitlab.com/tgdp/templates/-/tree/main/),
[Good Docs concept guide](https://www.thegooddocsproject.dev/template/concept))

These models use different labels and scopes, but their stable common ground is that
**different reader jobs require different content structures and success criteria**.

### Broad frameworks do not cover every specialist artifact

Diátaxis is deliberately a guide rather than a mandatory corpus plan. It warns users
not to create empty four-part structures merely to mirror the framework. That warning
matters here: forcing policy, threat models, test contracts, architecture views, ADR
references, and generated indexes into the four Diátaxis labels would hide rather
than clarify their obligations.
([Diátaxis as a guide to work](https://diataxis.fr/how-to-use-diataxis/))

Specialist sources impose different content models:

- ISO/IEC/IEEE 42010 distinguishes an architecture from the architecture description
  that expresses it, and treats viewpoints and model kinds as part of the description
  framework. The C4 model separates context, container, component, and deployment
  views and says teams should use only the views that add value.
  ([ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html),
  [C4 diagrams](https://c4model.com/diagrams))
- BCP 14 gives defined meanings to uppercase requirement words, while RFC 8174 also
  makes clear that normative text can exist without those keywords. A specification
  therefore requires more than detecting `MUST` and `SHOULD` tokens.
  ([BCP 14](https://www.rfc-editor.org/info/bcp14/),
  [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html))
- ISO/IEC/IEEE 29119-3 publicly describes test-documentation templates as outputs of
  test processes; its companion concepts standard describes a test strategy as the
  approach to testing for a project, level, or type. These are assurance artifacts,
  not ordinary product reference.
  ([ISO/IEC/IEEE 29119-3:2021](https://www.iso.org/standard/79429.html),
  [ISO/IEC/IEEE 29119-1:2022](https://www.iso.org/standard/81291.html))
- MADR records one justified decision using context, options, outcome, consequences,
  and confirmation. OWASP distinguishes the activity of threat modelling from the
  document produced and organizes the work around scope, threats, mitigations, and
  assessment.
  ([MADR](https://adr.github.io/madr/),
  [MADR template](https://adr.github.io/madr/decisions/adr-template.html),
  [OWASP threat-modelling process](https://owasp.org/www-community/Threat_Modeling_Process))

No one of these sources is a universal genre taxonomy. Together they support a
two-level approach: broad families for a manageable review, then specialist template
obligations for correctness.

### The same rating can mean different things in different genres

Treude, Middleton, and Atapattu asked four technical editors to assess 41 R-related
documents across reference documentation, README files, tutorials, articles, and
Stack Overflow threads, producing 75 assessments. Ratings varied by genre, especially
for structure. The authors caution that editors may bring different expectations to
each form: an 8 for a README may not mean the same thing as an 8 for a Stack Overflow
thread. They call for quality dimensions to be understood under each genre's
constraints.
([Treude et al., *Beyond Accuracy: Assessing Software Documentation Quality*](https://doi.org/10.1145/3368089.3417045))

The study is small and preliminary. It does not validate the eight families proposed
here. It does, however, provide empirical support for a point the information models
make conceptually: context-free scores can conceal different genre expectations.

## Candidate eight-family review model

The table groups every current template once according to its **dominant reader job**.
The grouping is for routing review questions, not for replacing template identities.

| Review family | Dominant job | Current templates |
|---|---|---|
| Explanatory and conceptual | Build understanding of what, why, and how ideas relate | `concept`, `capability` |
| Descriptive reference | Supply facts to consult while working | `component`, `configuration`, `data-entity`, `datastore`, `event-kind`, `glossary-term`, `implementation-reference`, `interface`, `reference` |
| Architecture and model | Express a bounded system view, structure, interaction, or deployment arrangement | `architecture-context`, `architecture-container`, `architecture-component`, `deployment`, `flow` |
| Normative and constraint | State what is required, permitted, prohibited, or invariant | `policy`, `specification`, `invariant` |
| Procedural and operational | Help a competent reader perform or recover a real task | `procedure`, `runbook` |
| Verification and assurance | State how confidence, coverage, testing, or security reasoning is established | `test-contract`, `test-strategy`, `threat-model` |
| Decision and historical | Preserve an authoritative decision and its rationale or connect it into the corpus | `decision-reference` |
| Generated and navigation | Provide reproducible access paths derived from canonical material | `generated-index` |

Some placements are contestable:

- `capability` combines explanatory material with bounded descriptive facts.
- `deployment` is both an architecture view and a reference to runtime reality.
- `configuration` can become normative if it says what operators must set rather than
  neutrally recording settings and consequences.
- `flow` models interaction but may contain procedural-looking sequences.
- `threat-model` contains a system description, yet the reason it exists is the
  security analysis and assurance result.
- `decision-reference` is not the ADR itself; its local template is a bridge from an
  external decision record into the corpus graph.

These are reasons to keep the template overlay, not reasons to abandon families. A
family chooses the primary review lens; the template resolves the boundary cases.

## Universal criteria before genre criteria

Every node should pass the following questions before its family-specific content is
assessed:

1. **Purpose:** Does the node state or make evident the reader need it serves?
2. **Audience:** Is the assumed reader identifiable, including the competence the
   node expects them to bring?
3. **Atomicity:** Does one primary subject and one dominant job hold the node together?
4. **Integrity:** Are factual claims, commands, defaults, relationships, and current
   state supported by appropriate evidence?
5. **Scope:** Is the coverage boundary explicit enough that a reader will not mistake
   selective coverage for complete coverage?
6. **Relevance:** Does each section advance the node's primary job or provide only the
   minimum supporting context that job needs?
7. **Coherence:** Do terminology, claims, links, diagrams, and examples agree within
   the node and with the authoritative sources it cites?
8. **Omissions:** Are material exclusions, unknowns, unsupported areas, and deferred
   specialist content visible?

A node that fails one of these may still be grammatically polished and may still
match its template headings. Neither establishes content quality.

## Family-specific criteria

### 1. Explanatory and conceptual

**Reader need:** understand a concept, capability, rationale, relationship, or larger
picture.

A satisfactory node should:

- define the subject and its boundary;
- connect it to concepts the intended audience is likely to know;
- explain important relationships, mechanisms, trade-offs, or reasons;
- distinguish current fact from interpretation or rationale;
- use examples or comparisons only where they improve understanding; and
- lead readers to separate task or reference nodes when they need to act or look up
  exhaustive facts.

Typical failure signals are a definition followed by no explanation, an unbounded
catalog of facts, step-by-step instructions taking over the node, or persuasive claims
presented as neutral explanation.

**Template overlay:** a `concept` centers one idea and answers what it is and how it
fits. A `capability` must additionally define what the system can do, its maturity,
boundary, and relationships without turning into a component inventory or roadmap.

### 2. Descriptive reference

**Reader need:** retrieve accurate, specific information while doing work.

A satisfactory node should:

- define exactly what object or surface is described;
- cover the fields, operations, values, defaults, constraints, states, or relationships
  promised by its scope;
- be structured for consultation rather than linear reading;
- mirror the stable structure of the described thing where that improves lookup;
- state facts neutrally and distinguish generated, observed, and inferred material;
- identify version, applicability, stability, and exceptions where relevant; and
- link to explanation or procedure instead of allowing those modes to obscure the
  reference structure.

Typical failure signals are undocumented fields, narrative that hides lookup facts,
unstated defaults, examples treated as exhaustive behavior, or advice and opinion
masquerading as product truth.

**Template overlays:**

| Template | Distinguishing content obligation |
|---|---|
| `component` | Responsibility, public interface, dependencies, and boundary of one implementation component |
| `configuration` | Settings, accepted values, defaults, effects, precedence, validation, and secrets discipline |
| `data-entity` | Meaning, identity, fields, lifecycle, relationships, and integrity constraints of one entity |
| `datastore` | Stored responsibility, data ownership, access boundary, persistence behavior, and operational characteristics |
| `event-kind` | Kind identity, tags/content contract, producers, consumers, validation, and lifecycle behavior |
| `glossary-term` | One term, one intended sense, concise definition, disambiguation, and controlled usage |
| `implementation-reference` | Exact artifact target, implementation surface, known divergences, and a way to verify current behavior |
| `interface` | Operations or messages, inputs/outputs, errors, stability, compatibility, and boundary |
| `reference` | A deliberately scoped, consistently structured set of facts that does not fit a narrower subtype |

### 3. Architecture and model

**Reader need:** understand a system through a defined abstraction, viewpoint, or
interaction model.

A satisfactory node should:

- identify the system or entity of interest and the purpose of the view;
- state the abstraction level, viewpoint, boundary, and material stakeholder concerns;
- define the notation or include a legend;
- name elements and relationships consistently;
- describe why each included element or relationship matters at that level;
- maintain correspondence between the prose, diagram, and evidenced system; and
- omit lower- or higher-level detail that would mix abstraction levels.

Typical failure signals are unlabeled boxes and arrows, mixed context/container/
component detail, a diagram with no stated question, prose and diagram disagreement,
or an exhaustive view that adds detail without serving a stakeholder concern.

**Template overlays:** context shows the system in its environment; container shows
deployable or executable building blocks inside the system; architecture-component
zooms into one container; deployment maps software instances to an execution
environment; flow expresses a bounded runtime scenario or interaction sequence. The
local `component` reference template is deliberately not the same artifact as an
`architecture-component` view.

### 4. Normative and constraint

**Reader need:** know what is required, allowed, forbidden, or guaranteed and how that
claim has authority.

A satisfactory node should:

- identify its authority, subjects, applicability, and precedence;
- separate binding requirements from recommendations and explanation;
- phrase each requirement so its actor, condition, action, and permitted outcome are
  unambiguous;
- define specialized terms and requirement keywords;
- explain enforcement, verification, exceptions, and escalation where applicable;
- expose compatibility, versioning, and supersession rules where relevant; and
- avoid converting present implementation behavior into an obligation without an
  authoritative decision.

Typical failure signals are unsupported `MUST` statements, passive requirements with
no responsible actor, a policy with no enforcement or exception path, or descriptive
observations that readers could reasonably interpret as binding rules.

**Template overlays:** a `policy` governs behavior and distinguishes MUST from SHOULD;
a `specification` defines an implementable/interoperable contract, definitions,
compatibility, and security considerations; an `invariant` states one condition that
must remain true, its scope, current enforcement, and consequence of violation.

### 5. Procedural and operational

**Reader need:** achieve a real goal, respond to a condition, or restore a system.

A satisfactory node should:

- name the goal or triggering condition in terms a competent reader can recognize;
- state prerequisites, permissions, environmental assumptions, and risk;
- provide ordered actions and meaningful decision points;
- give expected observations or verification after consequential actions;
- include safe recovery, rollback, stopping, or escalation behavior where failure is
  plausible; and
- keep conceptual background and exhaustive reference subordinate to action.

Typical failure signals are prose that explains without telling the reader what to do,
commands with no context or success signal, hidden prerequisites, irreversible action
without warning, or steps that assume the happy path is the only path.

**Template overlay:** a `procedure` supports one planned task. A `runbook` starts from
an operational condition, alert, or failure and adds severity/impact, diagnosis,
mitigation, resolution, and escalation under pressure. Detailed criteria are deferred
to topic 8.

### 6. Verification and assurance

**Reader need:** understand what confidence exists, how it was established, and where
it stops.

A satisfactory node should:

- identify the object, property, obligation, or risk being evaluated;
- state the method, model, evidence source, and current enforcement or execution state;
- connect conclusions to named evidence rather than merely asserting confidence;
- distinguish planned coverage from implemented and passing coverage;
- expose limits, residual risk, exclusions, and invalidating conditions; and
- be reproducible or independently inspectable to the extent its method permits.

Typical failure signals are test names without an obligation, a strategy that is only
a tool list, a threat list without a system model or mitigations, planned controls
written as implemented controls, or a passing result generalized beyond the tested
scope.

**Template overlays:** a `test-contract` links one precise obligation to named tests,
an exact run path, enforcement status, and limits; a `test-strategy` describes the
levels, types, coverage logic, environments, and deliberate exclusions for a bounded
surface; a `threat-model` connects a defined system model and trust boundaries to
threats, mitigations, validation, and residual exposure.

### 7. Decision and historical

**Reader need:** know what was decided, why, under what context, and whether that
decision still governs.

A satisfactory artifact should:

- identify the decision and its status;
- preserve the problem context and important decision drivers;
- record considered alternatives at a level sufficient to understand the choice;
- state the outcome, rationale, and consequences;
- explain how implementation or compliance can be confirmed; and
- retain history rather than silently rewriting an old decision to describe the
  current system.

Typical failure signals are an outcome without rationale, options reconstructed after
the fact as false certainty, current implementation presented as the original reason,
or a superseded decision presented as active.

**Template overlay:** Buzz's `decision-reference` does not replace or duplicate an ADR.
It must accurately identify the source decision, summarize only what is needed for
corpus use, preserve status and outcome, and connect the authoritative record into the
corpus graph.

### 8. Generated and navigation

**Reader need:** locate canonical material through a dependable derived view.

A satisfactory node should:

- identify itself as generated and name the generator and inputs;
- state inclusion, exclusion, ordering, and grouping rules;
- be reproducible from canonical sources;
- avoid introducing claims that do not exist in or follow mechanically from inputs;
- make empty, partial, stale, or failed generation visible; and
- direct corrections to the generator or canonical input rather than the output.

Typical failure signals are hand-authored facts in generated output, undocumented
selection rules, silently omitted nodes, links to non-canonical copies, or an index
whose apparent completeness exceeds its actual input scope.

**Template overlay:** `generated-index` is the only current member. Its own template
requires the generator, inputs, inclusion/exclusion rules, index body, relationships,
and scope/omissions.

## How to review mixed-purpose nodes

Mixed content is not automatically a defect. A task may need a sentence of context;
a reference entry may need a compact usage example; an architecture view needs
explanatory prose; and a policy may need non-normative rationale. The defect appears
when a supporting mode competes with or obscures the node's primary contract.

A reviewer can use this sequence:

1. **Name the reader's immediate need.** What prompted them to open this node?
2. **Name the dominant act.** Is the node mainly explaining, describing, modelling,
   requiring, directing action, establishing assurance, recording a decision, or
   deriving navigation?
3. **Choose the family lens.** Apply the universal criteria and the corresponding
   family criteria.
4. **Apply the exact template overlay.** Check the local required sections, evidence
   expectations, and sibling-template boundaries.
5. **Test every secondary mode.** Is it the minimum support the primary job needs, or
   has a second reader job taken over?
6. **Choose a remedy.** Keep and signpost genuinely supporting content; link to a
   separate node when the other job already exists; split the node when both jobs need
   independent development, evidence, or maintenance.

The split decision should be driven by reader need and maintenance boundary, not by a
mechanical ban on paragraphs of another form.

## Content anti-patterns the model can expose

| Anti-pattern | Why it fails | Likely review action |
|---|---|---|
| Template-shaped emptiness | Correct headings hide missing genre obligations | Assess the substance required by the family and overlay |
| Surface/genre confusion | Subject classification is used as a proxy for reader need | Identify both coordinates explicitly |
| Explanation inside every step | The task becomes slow and hard to scan | Retain minimum context; move the deeper explanation |
| Procedure embedded in reference | Lookup structure is interrupted by one opinionated path | Keep concise usage facts; link a procedure |
| Description that sounds normative | Readers cannot tell current fact from obligation | Identify authority or rewrite as observation |
| Architecture diagram as decoration | No viewpoint, boundary, or traceable claim is communicated | Define the question/view or remove it |
| Assurance by assertion | “Tested” or “secure” has no method, evidence, scope, or limits | Require the assurance chain |
| Decision rewritten as current truth | Historical rationale and supersession are lost | Preserve the decision; describe current state elsewhere |
| Generated page with authored claims | Canonical ownership and reproducibility become ambiguous | Move the claim to an input or generator-owned rule |

## Candidate checklist criteria

These are candidates for the eventual synthesis, not requirements in force.

### Genre identification

- [ ] The node's subject surface and writing form are treated as separate properties.
- [ ] The intended reader need and dominant communicative act are identifiable.
- [ ] The selected template fits that job; a familiar heading pattern is not the only
      evidence of fit.
- [ ] Supporting content from another genre remains subordinate to the primary job.
- [ ] If two reader jobs compete, the node is split or the decision to keep them
      together is justified by a shared evidence and maintenance boundary.

### Universal content contract

- [ ] Purpose, audience assumptions, scope, and material omissions are clear.
- [ ] The node has one primary subject and one dominant job.
- [ ] Factual, operational, normative, and assurance claims use evidence appropriate
      to their claim type.
- [ ] Terminology, prose, diagrams, examples, and linked claims do not contradict one
      another.
- [ ] The node's apparent completeness does not exceed its declared scope.

### Family routing

- [ ] Explanatory nodes build understanding and do not become instructions or fact
      catalogs.
- [ ] Reference nodes are neutral, scoped, structured for lookup, and complete for the
      fields or facts they promise.
- [ ] Architecture/model nodes state viewpoint, boundary, notation, elements,
      relationships, and correspondence to evidence at one abstraction level.
- [ ] Normative nodes expose authority, applicability, requirement strength,
      verification/enforcement, and exceptions or compatibility where relevant.
- [ ] Procedural nodes state goal/trigger, prerequisites, ordered action, decision
      points, verification, and recovery or escalation where needed.
- [ ] Verification/assurance nodes connect an explicit obligation or risk to method,
      evidence, current status, coverage, and limitations.
- [ ] Decision nodes preserve status, context, alternatives, outcome, rationale,
      consequences, confirmation, and history at the level their subtype owns.
- [ ] Generated/navigation nodes disclose generator and inputs, define selection
      rules, reproduce deterministically, and add no unsupported authored claims.

### Template overlay

- [ ] The node satisfies the required content and evidence expectations in its exact
      template, not only its broad family.
- [ ] The node respects the template's stated boundary against neighboring templates.
- [ ] Any deliberate omission of a normally required section is explained rather than
      silently represented by an empty heading.

## Competing positions and decisions still open

### Four forms may be enough for reader-facing documentation

Diátaxis offers a powerful, memorable model and could plausibly govern a conventional
product-documentation website with tutorial, how-to, reference, and explanation.
Reducing the number of review families would make training and reviewer calibration
easier.

The counterargument is local fit. Buzz contains requirements-bearing, architectural,
assurance, historical, and generated artifacts whose defining obligations are not
captured by those four labels. Calling a policy “reference” does not tell a reviewer
to inspect its authority and exception path; calling a threat model “explanation” does
not require a threat-to-mitigation chain. The recommended compromise is to use
Diátaxis for its reader-need distinctions without making it the whole taxonomy.

### Twenty-six template-specific checklists may be more precise

A separate checklist for every template would minimize ambiguity and align directly
with local required sections. It would also create duplication, make calibration
difficult, and encourage reviewers to check headings rather than understand the
function shared by sibling templates.

The eight-family layer is useful only if template overlays remain available. Removing
the overlays would lose exactly the precision the local template system was built to
provide.

### Mixed forms may be realistic rather than defective

DITA permits supporting context, results, examples, and troubleshooting inside task
content. Diátaxis reference may include succinct examples and necessary descriptions
of correct use. The Good Docs concept guidance nevertheless warns against allowing
instructional or referential content to take over a concept.

The evidence therefore supports **dominant purpose with controlled support**, not a
purity test. The unresolved implementation question is how much secondary content a
review checklist should tolerate before recommending a split. That threshold should
be calibrated on real Buzz nodes and reader tasks rather than invented here.

### Genre could become machine-readable metadata

An explicit genre field could make routing and automated checks easier. Against that,
the corpus already has 26 templates, and a second closed classification could drift,
create migrations, or falsely imply that genre conformance is machine-verifiable.
This research establishes a review distinction, not a schema-change case. Any metadata
proposal would need separate design work and evidence of an actual operational need.

## Claim ledger

| Claim | Main support | Counterevidence or qualification | Confidence |
|---|---|---|---|
| Genre-specific criteria are necessary | Diátaxis and DITA distinguish content by reader need and structure; Treude et al. observe genre effects and genre-conditioned ratings | The empirical study is small and preliminary | High |
| Buzz `type` is not genre | Schema description, closed 13-surface enum, and local taxonomy standard | A surface can correlate with common genres, but correlation is not identity | High |
| Universal criteria must be combined with genre criteria | ISO 26514's broad quality scope plus multiple specialist models | Exact division between universal and family criteria is a synthesis | High for layering; moderate for this allocation |
| A small family layer is preferable to either 4 or 26 top-level review paths | Partial overlap among Diátaxis, DITA, and specialist artifacts; local 26-template inventory | No comparative study tests eight families against this corpus | Moderate |
| Mixed content is acceptable when subordinate to one primary job | DITA task structure and Diátaxis reference examples permit supporting modes | No quantitative split threshold exists | High for principle; low for any universal threshold |
| Architecture, normative, assurance, decision, and generated artifacts require specialist overlays | ISO 42010/C4, BCP 14, ISO 29119, MADR, OWASP, and local generated-index contract | These sources differ in authority and scope; local adaptation is still required | High |
| The proposed mapping covers every current template | Direct inventory of 26 template files | Future templates could require a new family or remapping | High for current inventory |

## Limitations

- The study classified templates, not a representative sample of completed corpus
  nodes. Real content may reveal hybrid forms or weak template fit.
- The eight families have not been tested for reviewer agreement, speed, defect yield,
  or reader outcomes.
- The corpus is unusual: it combines user-facing information with architecture,
  governance, evidence ledgers, decision references, and generated projections.
  Findings should not be generalized unchanged to other documentation systems.
- Public summaries of ISO standards cannot support detailed conformance claims.
- The report does not settle whether genre should remain implicit in templates or
  become metadata.
- Specialist criteria here are intentionally high-level. Later research topics may
  revise the procedural, normative, architecture, example, accessibility, review, or
  security portions before checklist synthesis.

## Implications for the final synthesis

The eventual content-review checklist should not be one flat list. A defensible shape
would be:

1. universal integrity and scope gates;
2. identification of reader need, subject surface, and writing form;
3. one family-specific branch;
4. the exact local template overlay;
5. specialist overlays from later research topics; and
6. a recorded outcome that preserves uncertainty instead of collapsing everything to
   one quality score.

Before adoption, the proposed routing model should be trialled on a varied sample:
at least one node from every family, several nodes that share a `type` but use different
templates, and the ambiguous placements identified in this report. Reviewers should
independently select the dominant family and record where they disagree. That trial
would reveal whether eight families improve consistency or merely add another label.

## Sources

### Local corpus sources

- [`node.schema.json`](../../docs/corpus/schema/node.schema.json)
- [`taxonomy.md`](../../docs/corpus/standards/taxonomy.md)
- [`templates/`](../../docs/corpus/templates/)
- [`concept.md`](../../docs/corpus/templates/concept.md)
- [`reference.md`](../../docs/corpus/templates/reference.md)
- [`procedure.md`](../../docs/corpus/templates/procedure.md)
- [`runbook.md`](../../docs/corpus/templates/runbook.md)
- [`architecture-context.md`](../../docs/corpus/templates/architecture-context.md)
- [`policy.md`](../../docs/corpus/templates/policy.md)
- [`specification.md`](../../docs/corpus/templates/specification.md)
- [`test-contract.md`](../../docs/corpus/templates/test-contract.md)
- [`threat-model.md`](../../docs/corpus/templates/threat-model.md)
- [`decision-reference.md`](../../docs/corpus/templates/decision-reference.md)
- [`generated-index.md`](../../docs/corpus/templates/generated-index.md)

### External sources

- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:26514:ed-1:v1:en)
- [OASIS DITA 1.3 overview](https://docs.oasis-open.org/dita/dita/v1.3/os/part0-overview/introduction/about-the-dita-specification.html)
- [OASIS DITA technical-content information types](https://docs.oasis-open.org/dita/v1.2/os/spec/archSpec/dita_technicalContent_InformationTypes.html)
- [OASIS DITA troubleshooting information](https://docs.oasis-open.org/dita/dita/v1.3/cos01/part2-tech-content/archSpec/technicalContent/TroubleshootingElements.html)
- [Diátaxis — start here](https://diataxis.fr/start-here/)
- [Diátaxis — reference](https://diataxis.fr/reference/)
- [Diátaxis as a guide to work](https://diataxis.fr/how-to-use-diataxis/)
- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/tree/main/)
- [The Good Docs Project concept guide](https://www.thegooddocsproject.dev/template/concept)
- [ISO/IEC/IEEE 42010:2022 — Architecture description](https://www.iso.org/standard/74393.html)
- [C4 model diagrams](https://c4model.com/diagrams)
- [C4 model notation](https://c4model.com/diagrams/notation)
- [BCP 14 — Requirements language](https://www.rfc-editor.org/info/bcp14/)
- [RFC 7322 — RFC Style Guide](https://www.rfc-editor.org/info/rfc7322/)
- [RFC 8174 — Ambiguity of uppercase and lowercase requirement words](https://www.rfc-editor.org/rfc/rfc8174.html)
- [ISO/IEC/IEEE 29119-1:2022 — Software testing concepts](https://www.iso.org/standard/81291.html)
- [ISO/IEC/IEEE 29119-3:2021 — Test documentation](https://www.iso.org/standard/79429.html)
- [MADR](https://adr.github.io/madr/)
- [MADR template](https://adr.github.io/madr/decisions/adr-template.html)
- [OWASP threat-modelling process](https://owasp.org/www-community/Threat_Modeling_Process)
- [Treude, Middleton, and Atapattu, *Beyond Accuracy: Assessing Software Documentation Quality*](https://doi.org/10.1145/3368089.3417045)
