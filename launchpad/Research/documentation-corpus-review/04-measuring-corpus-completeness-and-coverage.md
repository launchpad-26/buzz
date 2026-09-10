---
description: Research into defining and measuring completeness and coverage for the evolving Buzz documentation corpus.
tags: [documentation, corpus, completeness, coverage, measurement, traceability, research]
---

# Measuring corpus completeness and coverage

Researched 2026-09-06. This is research, not an adopted corpus standard.

## Research question

How can reviewers measure whether the Buzz documentation corpus covers what it needs
to cover, without mistaking document count, template conformance, or one convenient
inventory for completeness?

The investigation considered six subquestions:

1. Complete relative to which scope, audiences, tasks, product state, and time?
2. What is the correct unit of coverage in an atomic corpus: source artifact, node,
   claim, reader task, product surface, or something else?
3. How should candidate documentation needs be discovered and turned into an explicit
   denominator?
4. Which quantitative measures are meaningful, and which create false confidence?
5. How should partial coverage, deliberate omission, unknown applicability, and
   deferred work be represented?
6. What can tooling establish, and what must remain a human content-review decision?

## Bottom line

There is no meaningful corpus-completeness percentage until the project declares the
set of obligations it expects the corpus to satisfy. The denominator must be designed,
versioned, and reviewable; it cannot be recovered from the number of Markdown files or
from whatever a source scanner happens to recognize.

For Buzz, the useful unit is a **coverage obligation**: a bounded statement that a
particular audience needs a particular kind of information about a particular system
surface, task, decision, risk, or lifecycle state. Nodes are the authored units that
satisfy obligations. They are not themselves the denominator.

A defensible model therefore needs:

1. a declared coverage contract—scope, revision, audiences, product boundaries,
   required lenses, exclusions, and acceptance thresholds;
2. candidate discovery from several independent lenses, including source inventory,
   product intent, user and operator tasks, interfaces, decisions, risks, and document
   genres;
3. human curation of those candidates into uniquely identified obligations;
4. explicit many-to-many traceability between obligations and corpus nodes;
5. states that distinguish adequate, partial, planned, intentionally omitted, not
   applicable, unknown, conflicted, and stale coverage;
6. measures reported per named denominator and per important slice—not one blended
   “corpus completeness” score; and
7. a qualitative adequacy review, because the existence of a mapped node says nothing
   about whether it actually satisfies the reader need.

“Complete enough” should mean that, for the declared baseline, every in-scope
obligation has been dispositioned; all critical obligations are adequately covered or
blocked by a visible human-owned decision; material audience, task, variant, and safety
gaps are exposed; and residual gaps are explicit rather than inferred from silence. It
should never mean that the corpus contains everything that could be said about Buzz.

## Scope and method

This report addresses corpus-level breadth and the boundary between breadth and
content adequacy. It does not define:

- how readers find nodes, deferred to topic 6;
- freshness intervals or change triggers, deferred to topic 7;
- genre-specific completeness inside procedures, architecture, interfaces, and other
  node families, covered by topic 2 and expanded by later topics;
- an implementation or schema migration for a coverage registry; or
- LLM-specific controls, which remain outside the current research sequence.

Local evidence included the corpus schema, taxonomy and atomicity standards, current
node tree, source inventory, manifest and scaffold helpers, review requirements, and
the accepted decision establishing the corpus as canonical. The local snapshot was
also measured directly with reproducible read-only commands.

External coverage intentionally included:

- a software-information standard connecting content to audiences and tasks;
- goal-driven measurement theory;
- requirements traceability and verification matrices;
- topic-map and taxonomy mechanisms for atomic documentation;
- a practical distinction between documentation inventory and gap analysis;
- a testing source showing why coverage percentages need named coverage items and why
  one full measure does not establish another;
- an open-world graph model explaining why absence is not evidence of nonexistence;
  and
- empirical evidence that readers experience incompleteness as a severe documentation
  failure.

Transfer from requirements engineering, testing, and semantic-web research is marked
as analysis. Those disciplines illuminate measurement structure; none directly
establishes a Buzz documentation policy.

## Definitions

This report uses the following distinctions.

| Term | Meaning here |
|---|---|
| Inventory | A record of things that exist in a chosen source or documentation boundary |
| Candidate need | A possible documentation obligation discovered by an inventory, task analysis, decision, risk, or reviewer |
| Coverage obligation | A curated, uniquely identified expectation that the corpus provide bounded information to an audience |
| Mapping | A declared relationship between an obligation and one or more nodes intended to satisfy it |
| Breadth coverage | The disposition of every obligation in a declared denominator |
| Adequacy | Whether mapped content actually satisfies the obligation at the required depth and quality |
| Completeness assertion | A bounded claim that all obligations in a named slice have acceptable dispositions |
| Gap | An applicable obligation not adequately satisfied, including a partial or stale satisfaction |
| Unknown | Applicability or coverage has not yet been established; it is not equivalent to not applicable |

This makes completeness a relation, not an intrinsic property:

> corpus × declared obligations × audience × system baseline × time

Change any coordinate and the conclusion may change.

## What the local system establishes

### Buzz already has useful building blocks

The corpus already encodes several coordinates needed by a coverage model:

- `type` classifies the subject surface through a closed 13-value enum;
- `audiences` identifies one or more of agent, developer, operator, and reviewer;
- `status` separates draft and active material, among other lifecycle states;
- typed `relationships` can connect nodes;
- atomicity makes one file one independently maintainable idea; and
- template standards define content obligations for different node forms.

These support slicing and adequacy review. They do not declare which nodes ought to
exist. As topic 2 established, `type` is a subject surface rather than a writing genre,
so type coverage cannot substitute for task, audience, or genre coverage.

The accepted canonical-corpus decision makes the cost of omissions material:
[`ADR-0050`](../../decisions/ADR-0050-canonical-corpus-supersedes-handbook.md)
retires the handbook as a parallel authority. A gap cannot safely be dismissed on the
assumption that another canonical manual will cover it.

### The source inventory is candidate discovery, not a denominator

[`inventory.py`](../../project-intelligence/corpus/inventory.py) deterministically
discovers selected implementation surfaces: Rust crates, event kinds, declared relay
route strings, migrations, top-level client-feature directories, integration-test
suites, formal models, existing upstream documentation, and `.env.example` keys. It
also reports top-level directories it neither recognizes nor deliberately ignores.

At this working-tree snapshot it reported 390 items:

| Inventory category | Items |
|---|---:|
| Event kinds | 129 |
| Existing upstream documents | 61 |
| Migrations | 40 |
| Declared relay routes | 39 |
| Rust crates | 32 |
| Desktop feature directories | 30 |
| Configuration keys | 19 |
| Integration-test suites | 19 |
| Mobile feature directories | 10 |
| Formal models | 9 |
| Web feature directories | 2 |

It also reported 24 unrecognized top-level directories. Some are tool or workspace
internals and some may be product or operating surfaces. Their presence is a useful
signal that the inventory's boundary needs review, not proof that 24 documentation
sections are missing.

The inventory's own comments disclose material limits. For example, route discovery
records literal `.route()` registrations but does not resolve nested mount paths. A
client “feature” is a top-level directory, while an event kind is an individual
constant and an upstream document is an entire file. These items have different grain
and importance. Treating all 390 as equal denominator units would be mathematically
clean and semantically false.

The inventory also deliberately ignores `launchpad/`, because its original scope is
the Buzz product rather than cohort operations. That is appropriate for its stated
purpose but insufficient for a canonical corpus that also contains governance and
agent-facing material. No single scanner should be presumed exhaustive outside its
declared boundary.

### The manifest machinery does not currently close the traceability loop

[`manifest.py`](../../project-intelligence/corpus/manifest.py) requires planned rows
to carry a path, parent feature, template, purpose, audiences, and
`source_start_points`. It enforces structural guarantees such as unique document paths
and one task per document. Its module documentation is explicit that it does not decide
which documents the corpus needs.

Three current limits matter for measurement:

1. no persisted corpus-plan or manifest data artifact was found in this repository;
2. `build_manifest()` requires `source_start_points` to be a sequence but does not
   resolve its values against `inventory.py` source keys; and
3. [`scaffold.py`](../../project-intelligence/corpus/scaffold.py) does not carry
   `source_start_points`, purpose, task ownership, or a coverage-obligation identifier
   into the canonical node front matter.

Consequently, the code can validate a caller-supplied plan, but the current canonical
corpus cannot be joined mechanically back to the inventory that may have motivated it.
This is a traceability limitation, not evidence that the corpus content is deficient.

### Current counts describe construction state, not completeness

Excluding `schema/`, this working tree contains 205 Markdown nodes. Direct front-matter
inspection found:

- 158 `draft` and 47 `active` nodes;
- six represented subject types: agent, architecture, capabilities, development,
  governance, and layers;
- seven schema-allowed subject types with no current nodes: platforms,
  implementation, interfaces-events, verification, operations, release, and ingestion;
- 192 declared relationships; and
- 116 nodes with no relationship entry.

These facts are useful inventory observations only. They do **not** establish that
seven surfaces are improperly absent, that draft nodes cover nothing, or that 116
nodes are graph defects. Each conclusion requires an obligation model and an
applicability decision. The lack of an edge is particularly ambiguous because the
schema makes relationships optional.

### Structural validation does not test coverage

[`validate.py`](../../project-intelligence/corpus/validate.py) checks schema shape,
identifier uniqueness, citation forms, local citation existence, and relationship
target resolution. It does not compare the corpus with the source inventory, product
vision, user tasks, template-level content obligations, or a required-node manifest.

[`review-requirements.md`](../../docs/corpus/standards/review-requirements.md) assigns
claim-to-ledger correspondence and relationship meaning to human review, but it does
not establish corpus-wide completeness criteria. A green validation run and 205
schema-valid files therefore answer a structural question, not the research question
in this report.

## What the external evidence establishes

### Coverage begins with audience and task needs

[ISO/IEC/IEEE 26514:2022](https://www.iso.org/standard/77451.html) covers requirements
for the structure, content, and format of software information for users. Its public
material makes audience and task analysis part of information architecture, defines an
audience through shared characteristics and needs that shape content and structure,
and defines information for users in terms of concepts, procedures, and reference
material supporting safe and effective use. It also defines minimalism as including
critical information plus only the additional material needed for completeness
([public browsing material, §§3.1.7, 3.1.29, 3.1.34](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)).

This rejects two opposite errors: documenting every detectable implementation detail
is not required, while omitting critical reader information cannot be defended as
minimalism. The denominator must originate in intended use, not volume.

### Inventory and gap analysis are different products

Google's open-source
[`Docs Advisor` guide](https://github.com/google/opendocs/blob/main/docs_advisor/part_3.md#basic-docs-inventory)
defines a basic inventory as a snapshot of what exists and explicitly says it is not a
quality evaluation. Its full gap analysis adds comparison with the desired end state,
target audiences, comprehensiveness, relevance, findability, and currency. It also
warns that a full analysis is expensive and recommends completing qualitative review
section by section when necessary.

The distinction maps directly to Buzz:

- `inventory.py` can supply candidate source surfaces;
- a node scan can supply existing-content inventory;
- neither tells the project what should exist; and
- only a curated gap analysis can compare actual content with intended coverage.

### Metrics should be derived from goals, not selected because they are easy to count

Basili, Caldiera, and Rombach's
[Goal Question Metric approach](https://www.cs.toronto.edu/~sme/CSC444F/handouts/GQM-paper.pdf)
argues that measurement must first specify organizational goals, refine them into
questions, and then choose metrics that operationalize those questions in context
(pp. 1–3). The same observable value can mean different things from different
viewpoints.

Applied here, “number of nodes” is not a goal. A goal might be “operators can safely
restore the relay,” a question might be “are all restoration decisions and failure
paths documented and validated?”, and the measures might include disposition of
runbook obligations, execution evidence, and unresolved high-risk gaps. Starting from
file count reverses that logic.

### Traceability matrices make the denominator and disposition inspectable

NASA's
[Systems Engineering Handbook, Appendix D](https://www.nasa.gov/reference/system-engineering-handbook-appendix/#hds-sidebar-nav-188)
uses a verification matrix that identifies every applicable “shall” by unique ID,
source, verification method, phase, level, and status. The handbook also defines
bidirectional traceability and expects requirements management to preserve it over the
system lifecycle.

Documentation obligations are not engineering requirements, so NASA's matrix cannot
be adopted unchanged. Its transferable lesson is strong: an assurance claim about
“all” requires enumerated items, stable identity, source, planned disposition, and a
way to travel in both directions. For Buzz that means obligation → satisfying node(s)
and node → obligation(s), plus explicit orphan reporting on both sides.

### Atomic topics need maps; file collections do not map themselves

The [OASIS DITA 1.3 specification](https://www.oasis-open.org/standard/ditav1-3/)
separates reusable topics from maps. A topic can stand alone, while maps organize
topic references into hierarchies, groups, and relationships; subject schemes can add
controlled taxonomies
([Part 1, §§2.2.1–2.2.3](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/dita-v1.3-os-part1-base.pdf)).

Buzz does not use DITA, and the research does not recommend adopting it. The relevant
principle is that atomic authored units and corpus-level coverage/navigation are
different structures. Optional pairwise node relationships are not automatically a
map of expected coverage.

### Every percentage needs a named coverage criterion

The current
[ISTQB Foundation Level syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)
defines specific coverage items before calculating a ratio. It also gives a useful
counterexample: 100% statement coverage does not ensure that all branches were tested
(§4.3.1, p. 42).

This is an analogy, not a documentation standard. Its measurement logic transfers:
100% of inventory items mapped to nodes can coexist with 0% coverage of a critical
operator task, an unsupported platform variant, or a missing failure path. Coverage
must always be reported as “coverage of X under criterion Y,” never as an unqualified
percentage.

### Missing graph information is unknown unless a closed boundary has been declared

The W3C's
[RDF Concepts recommendation](https://www.w3.org/TR/rdf10-concepts/#section-design-goals)
states that RDF operates in an open world and generally does not assume complete
information about a resource. Systems using it must tolerate incomplete or inconsistent
sources. Buzz's graph is not RDF, but the logical caution applies: the absence of a
node or relationship cannot by itself mean that the subject does not exist or is not
applicable.

A coverage slice becomes measurable only when the project makes a bounded, partial
closed-world assertion—for example, “these are all production relay environment
variables at revision R” or “these are all operator recovery tasks required for the
supported deployment.” Outside such assertions, missing means unknown.

### Presence is not adequacy, and output metrics are not coverage metrics

Uddin and Robillard's empirical study
[*How API Documentation Fails*](https://doi.org/10.1109/MS.2014.80) used two surveys
covering 323 professional developers and analysis of 179 documentation units. Ambiguity,
incompleteness, and incorrectness were the three severest reported problems. The study
concerns API documentation, so it does not quantify Buzz's corpus; it does show that a
present documentation unit can still be experienced as incomplete.

Google's
[2022 Season of Docs report](https://developers.google.com/season-of-docs/docs/2022/2022-case-study-report#the_metrics)
lists outcome indicators such as contributions, direct feedback, time on page, issues,
and bounce rate, while noting that most projects lacked enough post-publication time to
determine whether targets were met. Those are useful effectiveness signals, not proof
that the intended corpus surface has been covered. Coverage and impact need separate
measurement models.

## A candidate coverage model for Buzz

### 1. Declare a coverage contract

Before calculating anything, record:

| Field | Question it fixes |
|---|---|
| Goal | What decision will the measurement support? |
| System baseline | Which commit, release, deployment, or intended-state record governs? |
| Product boundary | Buzz product, cohort operation, or both? Which repos and deployed services are in scope? |
| Audiences | Which of agent, developer, operator, reviewer—and which meaningful subgroups? |
| Lifecycle | Build, configure, deploy, operate, recover, change, retire, or another phase? |
| Required lenses | Which inventories and human analyses must contribute candidate obligations? |
| Exclusions | What is out of scope, who approved that boundary, and until when? |
| Criticality model | Which omissions are release/safety/security/operability gates? |
| Acceptance rule | What states are acceptable for each criticality class? |
| Measurement date | When was the comparison made? |

Without this contract, two reviewers can calculate different correct percentages over
different invisible denominators.

### 2. Discover candidates through several lenses

No lens is complete alone.

| Lens | Candidate obligations it can reveal | Characteristic blind spot |
|---|---|---|
| Product vision and accepted decisions | Intended capabilities, constraints, principles, non-goals | May describe futures not implemented today |
| Implementation inventory | Crates, kinds, routes, settings, migrations, clients | Over-represents code-shaped facts and misses reader tasks/rationale |
| Audience and task analysis | Goals, prerequisites, decisions, recovery paths | Requires field knowledge and representative users |
| Operational risk and incident history | High-consequence failure and recovery knowledge | Biased toward events that already occurred |
| Interface and data contracts | Inputs, outputs, errors, compatibility, security boundaries | Does not establish explanatory or procedural needs |
| Document-family obligations | Required content inside concepts, reference, procedures, architecture, assurance, decisions | Template presence can become box-ticking |
| Search/support questions | Vocabulary and recurring unmet needs | Demand signals omit silent or rare critical users |
| Corpus graph and navigation | Isolated nodes, missing cross-surface paths, supersession gaps | Edge count does not establish semantic usefulness |

Candidate discovery should retain source and rationale. Human curation then merges
duplicates, splits compound needs, rejects non-needs, and assigns applicability and
criticality.

### 3. Use coverage obligations as the denominator

A candidate obligation record should contain at least:

```text
id: stable obligation identifier
need: bounded information the corpus is expected to provide
audience: one or more intended audiences
surface: product or governance surface
genre: expected communicative job, where known
baseline: version, revision, deployment, or intended-state authority
source: why this obligation exists
criticality: gate / high / normal / low
applicability: applicable / not-applicable / unknown
status: adequate / partial / mapped-unreviewed / planned / omitted / stale / conflicted
nodes: zero or more satisfying node ids
assessment: reviewer, date, method, and rationale
owner: person or work item for an unacceptable gap
```

The obligation need not be added to every node's front matter. That is an
implementation decision. But the canonical trace must be persisted somewhere
reviewable and reproducible, not reconstructed from task history after the fact.

### 4. Preserve many-to-many mapping

One node may satisfy several closely related obligations, while one cross-cutting
obligation may require several nodes. Atomicity therefore does not imply a one-node to
one-obligation rule.

The mapping should report:

- obligations with no satisfying node;
- nodes with no declared obligation;
- mappings to retired, missing, stale, or draft-only nodes;
- obligations whose audience is absent from all mapped nodes;
- obligations split across nodes without a usable joining path; and
- duplicate nodes claiming the same obligation with conflicting authority.

An “orphan node” is a review prompt, not automatically waste. Governance, navigation,
or newly discovered knowledge may be valuable before a prior obligation exists.

### 5. Use explicit disposition states

Binary covered/uncovered is too lossy.

| State | Meaning | Counts as acceptable breadth? |
|---|---|---|
| Adequate | Human review found current nodes satisfy the obligation | Yes |
| Partial | Some required aspect, audience, variant, or depth is missing | No, unless threshold explicitly permits it |
| Mapped-unreviewed | A node is linked but semantic adequacy has not been assessed | No |
| Planned | Work exists but no adequate canonical content exists yet | No |
| Intentionally omitted | Applicable information is excluded by an authorized, reasoned decision | Only under the declared acceptance rule |
| Not applicable | Obligation does not apply within this baseline and boundary; rationale recorded | Removed from denominator, but reported |
| Unknown | Applicability or satisfaction has not been determined | No |
| Stale | Earlier coverage no longer applies to the current baseline | No |
| Conflicted | Authorities disagree and a human decision is pending | No |

“Not applicable” and “intentionally omitted” must never be defaults. They are
substantive dispositions requiring a rationale and authority.

### 6. Report a dashboard, not one score

Candidate measures include:

| Measure | Numerator / denominator | What it can say |
|---|---|---|
| Disposition completeness | Obligations with any explicit disposition / all discovered in-scope obligations | Whether silence has been eliminated |
| Adequate breadth | Adequate obligations / applicable obligations | Coverage under one declared obligation set |
| Critical adequate breadth | Adequate gate/high obligations / applicable gate/high obligations | Whether important gaps remain |
| Semantic review completion | Adequacy-reviewed mappings / all mappings | How much mapping has received human content review |
| Known-gap rate | Partial + planned + stale + conflicted obligations / applicable obligations | Visible outstanding debt |
| Unknown rate | Unknown obligations / all candidate obligations | Unresolved scope and discovery risk |
| Audience-task coverage | Adequate obligations in one audience/task slice / applicable obligations in that slice | Whether a particular reader workflow is covered |
| Variant coverage | Adequate obligations for a platform/version/deployment / applicable obligations for that variant | Whether aggregation hides unsupported variants |
| Source traceability | Inventory candidates mapped or explicitly rejected / candidates reviewed | Whether a named inventory was dispositioned |
| Change-delta coverage | Changed or new obligations reassessed / obligations affected by the change | Whether the baseline moved beyond the assessment |

Every displayed value should name its denominator version, baseline, exclusions, and
date. Counts should accompany percentages, so “100% (2/2)” is not mistaken for broad
assurance.

Weighted totals can assist prioritization but should not replace the unweighted counts
or critical-gap list. A weighting model embeds human value judgments and can hide one
unacceptable omission inside many low-risk successes.

### 7. Keep breadth and adequacy separate

The mapping question is: “Is there candidate content for this obligation?”

The adequacy question is: “Does the mapped content satisfy the obligation for this
audience and baseline?”

Adequacy should reuse the quality model from topic 1, the family criteria from topic 2,
and the semantic evidence audit from topic 3. A node does not count as adequate merely
because:

- its file exists;
- its headings match a template;
- its `status` is `active`;
- it cites the relevant subsystem;
- a keyword search finds the obligation's words; or
- an embedding ranks it highly.

These are candidate-mapping signals. Human review establishes semantic satisfaction,
with runtime or reader-task validation when the obligation requires it.

## A candidate review procedure

1. **Name the decision.** State why coverage is being assessed: baseline completion,
   release readiness, audit, migration, or prioritization.
2. **Freeze the comparison boundary.** Record the system revision, intended-state
   authorities, repositories, deployments, audiences, and lifecycle phases.
3. **Choose required lenses.** Do not let the easiest inventory silently become the
   whole denominator.
4. **Generate candidates.** Run deterministic inventories and gather tasks, risks,
   decisions, interfaces, support questions, and genre obligations.
5. **Curate obligations.** Merge duplicates, split compound needs, set stable IDs,
   classify applicability and criticality, and record source rationale.
6. **Map both directions.** Associate obligations with candidate nodes; identify
   obligation and node orphans.
7. **Assess semantic adequacy.** Read mapped nodes and apply the prior research lenses;
   do not promote automatically discovered matches to adequate.
8. **Challenge completeness.** Seek missing audiences, rare high-impact tasks,
   negative/error paths, variants, lifecycle transitions, and unrecognized source
   areas.
9. **Report by slice.** Publish counts and rates for each important denominator,
   especially gate/high criticality, audience-task, surface, genre, and variant.
10. **Disposition every exception.** Record owner, authority, rationale, and follow-up
    for partial, omitted, unknown, stale, or conflicted obligations.
11. **Make a bounded assertion.** State exactly which slices are complete enough and
    which are not; never label the corpus globally complete without coordinates.

## Candidate checklist criteria

These are candidates for the eventual synthesis, not requirements in force.

### Boundary and denominator

- [ ] The coverage goal and decision it supports are explicit.
- [ ] The system baseline, product boundary, audiences, lifecycle phases, variants,
      and measurement date are recorded.
- [ ] Required discovery lenses and material exclusions are explicit.
- [ ] Every reported percentage names a stable, reviewable denominator.
- [ ] Counts accompany percentages.
- [ ] The denominator is versioned so later results are comparable.

### Obligation quality

- [ ] Coverage is measured against curated audience information needs, not raw file or
      source-item counts.
- [ ] Each obligation has stable identity, bounded scope, source rationale,
      applicability, criticality, and baseline.
- [ ] Compound obligations are split when their parts can have different dispositions.
- [ ] Duplicate candidates from different lenses are reconciled without losing their
      provenance.
- [ ] “Not applicable” and “intentionally omitted” include a reason and approving
      authority.
- [ ] Unknown applicability remains unknown rather than silently leaving the
      denominator.

### Traceability

- [ ] Every applicable obligation maps to zero or more canonical node IDs explicitly.
- [ ] Every node can be traced back to one or more obligations or receives an explicit
      orphan disposition.
- [ ] Mappings preserve audience, variant, lifecycle, and baseline applicability.
- [ ] Missing, retired, draft-only, stale, and conflicting mapped nodes remain visible.
- [ ] A source inventory item can be mapped, rejected, or deferred without pretending
      every item deserves its own node.

### Adequacy and assurance

- [ ] Mapped content receives semantic adequacy review before it counts as covered.
- [ ] Adequacy uses the relevant quality, genre, and evidence criteria rather than file
      presence or template shape.
- [ ] Critical omissions are gates; many low-risk covered items cannot average them
      away.
- [ ] Audience-task, surface, genre, platform/version, lifecycle, and risk slices are
      reviewed independently where applicable.
- [ ] A full result in one coverage dimension is not generalized to unmeasured
      dimensions.
- [ ] Outcome measures such as traffic or issue volume are reported separately from
      breadth coverage.

### Reporting and maintenance

- [ ] The report distinguishes adequate, partial, mapped-unreviewed, planned, omitted,
      not-applicable, unknown, stale, and conflicted states.
- [ ] Results show absolute counts, denominator definitions, exclusions, and the
      assessment date.
- [ ] Residual gaps have a human owner or visible work item where project rules require
      one.
- [ ] New or changed product surfaces trigger delta review rather than waiting for a
      full-corpus recount.
- [ ] The final assertion says “complete enough for X under Y baseline,” not simply
      “complete.”

## Anti-metrics and failure modes

| Signal presented as completeness | Why it fails |
|---|---|
| Number of nodes or words | Rewards volume and duplication; has no reader-need denominator |
| Percentage of schema-valid nodes | Measures structural validity of existing files, not missing files or content |
| Percentage of 13 `type` values represented | Says nothing about depth, applicability, genres, tasks, or criticality |
| Inventory items divided by nodes | Mixes incompatible grains and assumes one source item deserves one node |
| Percentage of nodes with relationships | Optional edge count does not measure relationship truth or useful journeys |
| Percentage of active nodes | Lifecycle state is not semantic adequacy |
| Keyword or embedding recall | Produces candidate matches, not proof that a reader need is satisfied |
| Citation count | Provenance volume is not evidence adequacy or coverage |
| Page views or time on page | Measures interaction ambiguously and misses rare critical needs |
| One weighted score | Hides denominator choices and can average away blocking omissions |
| Zero untracked gaps | Can be achieved by failing to discover candidates or misusing not-applicable |

## Competing positions and unresolved decisions

### “The deterministic source inventory should be the denominator”

This is reproducible and cheap. It is valuable for implementation traceability and
change detection. It is insufficient as the whole denominator because the discoverers
use inconsistent grain, exclude cohort operations, report many unrecognized areas,
and cannot discover audience goals, rationale, rare recovery tasks, or normative
intent. Recommended resolution: keep it as one mandatory candidate lens, with its own
coverage result.

### “The approved manifest already defines completeness”

The manifest data model is a promising planning boundary. Locally, however, no
persisted manifest plan was found; the library explicitly refuses to choose needed
documents; source-start values are not resolved to inventory keys; and that trace is
not preserved in canonical nodes. Recommended resolution: treat it as tooling
infrastructure, not a current completeness proof.

### “Every inventory item should get one atomic node”

This offers a simple ratio and task plan. It conflicts with information minimalism and
reader-centered coverage: one setting may need reference within a configuration node,
while one operator workflow may cross many implementation artifacts. Recommended
resolution: preserve atomic maintenance boundaries, but allow many-to-many obligation
mapping.

### “A single score is necessary for management”

A headline helps comparison, but aggregation conceals scope and critical gaps.
Recommended resolution: if a headline is unavoidable, show it only with the
denominator label, counts, critical-gap count, and slice dashboard. Never permit a
weighted average to override a gate.

### “Only active nodes count”

This is conservative and mechanically easy. It may misrepresent construction progress
and does not prove active content adequate. Recommended resolution: report lifecycle
state separately. Count an obligation as adequate only after content review under the
declared acceptance rule.

### “All nodes should have graph relationships”

Connectedness can aid navigation and expose isolation, but some standalone nodes may
be valid and an incorrect edge is worse than no edge. Recommended resolution: flag
orphans for review, then assess whether a meaningful typed relationship or navigation
path is actually required.

### “The corpus can never be complete because Buzz keeps changing”

Absolute and permanent completeness is unattainable. Bounded completeness assertions
are still useful: a declared obligation set can be fully dispositioned for a named
baseline, audience, and date. Recommended resolution: use versioned assertions and
delta review, while avoiding timeless language.

## Claim ledger

| Claim | Main support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Completeness requires a declared contextual denominator | ISO 26514 audience/task model; GQM goal-first measurement; NASA verification matrix | No cited source defines the exact Buzz obligation model | High for principle; moderate for proposed implementation |
| A source inventory is not a gap analysis | Google OpenDocs guide; direct inspection of `inventory.py` | A sufficiently curated inventory could itself become one denominator | High |
| Nodes should not be the primary coverage unit | Atomicity plus mismatched source-item grain and audience/task evidence | Some narrowly scoped generated-reference corpora can use one-record/one-page coverage | High for Buzz |
| Many-to-many traceability is required | DITA topic/map separation; NASA bidirectional traceability; local atomicity | Exact storage design is undecided | High for principle |
| One percentage cannot establish corpus completeness | ISTQB dimension counterexample; multiple independent discovery lenses | A tightly bounded single-purpose corpus might support one dominant measure | High |
| Missing nodes or edges should default to unknown | Optional local relationships; W3C open-world principle | A declared closed inventory slice can legitimately treat absence as a gap | High |
| Current Buzz tooling cannot calculate semantic corpus coverage | Direct inspection of inventory, manifest, scaffold, schema, and validator | Uninspected external GitHub issue/project data might hold a planning map | High for repository artifacts; moderate for whole project state |
| The candidate state vocabulary is sufficient | Synthesis of local statuses and measurement needs | It has not been trialed on representative obligations | Moderate |

## Limitations

- This report measured the current working tree, not `origin/launchpad` or a release
  tag. The 390 inventory items, 205 nodes, status distribution, and type distribution
  are dated observations, not stable corpus facts.
- Repository inspection did not include live GitHub issue bodies, project fields, or
  private cohort systems. A plan may exist there, but it is not a persisted artifact in
  the inspected tree.
- ISO's public pages expose scope, definitions, and table of contents, not all paid
  normative requirements. This report does not claim ISO conformance.
- NASA requirements verification, ISTQB test coverage, DITA maps, and W3C open-world
  semantics are analogies with explicit transfer boundaries. Buzz documentation is not
  a requirements set, test suite, DITA publication, or RDF graph.
- The empirical API-documentation study is narrower than Buzz's multi-genre corpus.
- No representative group of Buzz readers validated the proposed obligation record,
  state vocabulary, criticality scheme, or dashboard.
- No attempt was made to decide which of the 24 unrecognized inventory directories or
  seven unrepresented corpus types should be in scope.
- This report does not set numerical acceptance thresholds. Those are policy choices
  whose consequences require human decision and trial data.

## Implications for the final synthesis

The eventual content-review checklist should add a corpus-level pass after individual
node review:

1. require a declared, versioned coverage contract;
2. maintain a human-curated obligation registry fed by multiple discovery lenses;
3. trace obligations and nodes in both directions;
4. separate mapping, semantic adequacy, lifecycle state, and user impact;
5. report counts and rates per named slice, with critical gaps unaggregated;
6. treat unknown, not-applicable, omitted, partial, stale, and conflicted as distinct;
7. make completeness assertions bounded by audience, baseline, scope, and date; and
8. test the model on one representative vertical slice before making it policy.

A useful pilot would select one bounded operator workflow and one reference-heavy
surface. For each, build obligations independently from product intent, source
inventory, audience tasks, and genre criteria; map current nodes; compare reviewer
disagreements; and record the cost of maintaining the trace. That would reveal whether
the model exposes real gaps without producing an unmaintainable parallel bureaucracy.

## Sources

### Local corpus sources

- [`node.schema.json`](../../docs/corpus/schema/node.schema.json)
- [`taxonomy.md`](../../docs/corpus/standards/taxonomy.md)
- [`atomicity.md`](../../docs/corpus/standards/atomicity.md)
- [`review-requirements.md`](../../docs/corpus/standards/review-requirements.md)
- [`AGENTS.md`](../../docs/corpus/AGENTS.md)
- [`inventory.py`](../../project-intelligence/corpus/inventory.py)
- [`manifest.py`](../../project-intelligence/corpus/manifest.py)
- [`issue_plan.py`](../../project-intelligence/corpus/issue_plan.py)
- [`scaffold.py`](../../project-intelligence/corpus/scaffold.py)
- [`validate.py`](../../project-intelligence/corpus/validate.py)
- [`ADR-0028-corpus-canonical-representation.md`](../../decisions/ADR-0028-corpus-canonical-representation.md)
- [`ADR-0050-canonical-corpus-supersedes-handbook.md`](../../decisions/ADR-0050-canonical-corpus-supersedes-handbook.md)
- [`VISION.md`](../../../VISION.md)
- [`launchpad/VISION.md`](../../VISION.md)

### External sources

- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/standard/77451.html)
- [ISO/IEC/IEEE 26514:2022 public browsing material](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
- [Basili, Caldiera, and Rombach — *The Goal Question Metric Approach*](https://www.cs.toronto.edu/~sme/CSC444F/handouts/GQM-paper.pdf)
- [NASA Systems Engineering Handbook — Appendix](https://www.nasa.gov/reference/system-engineering-handbook-appendix/)
- [OASIS DITA 1.3 standard](https://www.oasis-open.org/standard/ditav1-3/)
- [OASIS DITA 1.3 Part 1: Base Edition](https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/dita-v1.3-os-part1-base.pdf)
- [Google OpenDocs — Docs Advisor, Part 3](https://github.com/google/opendocs/blob/main/docs_advisor/part_3.md)
- [Google Season of Docs 2022 case-study report](https://developers.google.com/season-of-docs/docs/2022/2022-case-study-report)
- [ISTQB Certified Tester Foundation Level syllabus v4.0.1](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)
- [W3C RDF: Concepts and Abstract Syntax](https://www.w3.org/TR/rdf10-concepts/)
- [Uddin and Robillard — *How API Documentation Fails*](https://doi.org/10.1109/MS.2014.80)
