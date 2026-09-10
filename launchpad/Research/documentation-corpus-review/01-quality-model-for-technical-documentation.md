---
description: Research into the quality dimensions and evaluation model that could govern a future content review of the Buzz documentation corpus.
tags: [documentation, corpus, quality, review, research]
---

# Quality model for technical documentation

Researched 2026-09-06. This is research, not an adopted corpus standard.

## Research question

What model of technical-documentation quality would give reviewers a defensible way
to assess the content of the Buzz documentation corpus without reducing quality to
style, structural conformance, or a single subjective score?

The investigation considered five subquestions:

1. Which quality dimensions recur across authoritative standards, documentation
   frameworks, and empirical software-documentation research?
2. Which dimensions describe the document itself, and which require comparison with
   the system, corpus, reader, or task?
3. Which failures should be acceptance gates rather than scores that can be averaged?
4. How much can one general model cover before genre-specific criteria are required?
5. What is the smallest useful model for a future review of the Buzz corpus?

## Bottom line

Technical-documentation quality is **multidimensional, contextual, and
non-compensatory**.

- Multidimensional means accuracy, completeness, clarity, consistency, usefulness,
  currency, accessibility, and other qualities can vary independently. One overall
  impression is not a sufficient assessment.
- Contextual means relevance, completeness, and usability can only be judged against
  a defined audience, purpose, system state, and task.
- Non-compensatory means excellence in one dimension must not cancel a critical
  failure in another. Clear prose does not offset a false instruction; comprehensive
  coverage does not offset an unsafe one.

For Buzz, the most defensible starting point is an eight-dimension model:

1. integrity;
2. sufficiency and relevance;
3. purpose and genre fitness;
4. comprehensibility and precision;
5. organization and findability;
6. consistency and coherence;
7. task effectiveness and usability;
8. currency and maintainability.

Accessibility should be applied as a cross-cutting condition on all eight rather than
treated as an optional ninth score. The model should use hard gates for integrity and
safety-critical sufficiency, separate dimension findings rather than one aggregate
number, and user/task evaluation where a claim cannot be established by inspection.

Confidence in this conclusion is **high** for the overall shape and **moderate** for
the exact eight-dimension consolidation. The sources strongly agree that quality has
multiple independent dimensions and depends on context. The exact grouping is a
synthesis for Buzz and has not been tested against the corpus or its readers.

## Scope and method

This research concerns **content quality**: what a reader encounters in canonical
corpus nodes and whether that information is trustworthy and useful. It does not
design the pull-request workflow, sampling plan, reviewer assignment, automation, or
LLM-specific controls. Those belong to later topics in the research queue.

Local inspection covered the corpus instructions and the standards for documentation
standards, review requirements, evidence, confidence, atomicity, and taxonomy. The
external search covered:

- international standards for software information, plain language, usability, and
  web accessibility;
- the Diátaxis documentation framework;
- a maintained developer-documentation style guide;
- four empirical or research-derived software-documentation quality models or issue
  studies.

Primary and authoritative sources were preferred. Standards were used only to the
extent described by their publicly accessible ISO pages. No paid standard was
obtained, and this report does not claim conformance with ISO/IEC/IEEE 26514,
IEC/IEEE 82079-1, ISO 24495-1, ISO 9241-11, or ISO/IEC/IEEE 26513.

## What the strongest sources establish

### Quality is broader than accuracy and prose style

The public introduction to ISO/IEC/IEEE 26514:2022 says the standard supports
consistent, complete, accurate, and usable information and covers both development
process and characteristics of the resulting information. Its scope includes audience
and task analysis, structure, content, format, review, release, updating, and change
control. This makes it a broad reference point, but not a ready-made review checklist
for an internal technical knowledge corpus.
([ISO/IEC/IEEE 26514:2022](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:26514:ed-1:v1:en))

IEC/IEEE 82079-1:2019 similarly covers principles, quality of information, its
management process, content, structure, media, format, professional competencies, and
empirical evaluation. Its scope is information for use across products, so some of it
is broader than software and some is more instruction-oriented than the Buzz corpus.
([IEC/IEEE 82079-1:2019](https://www.iso.org/standard/71620.html))

Diátaxis calls accuracy, completeness, consistency, usefulness, and precision
independent aspects of *functional quality*. It distinguishes those from *deep
quality*: flow, fit to human needs, anticipation, and the experience of using the
documentation. It also argues that deep quality depends on functional quality rather
than compensating for failures in it.
([Diátaxis: quality](https://diataxis.fr/quality/))

The useful synthesis is that document quality has at least three layers:

| Layer | Question | Typical evaluation |
|---|---|---|
| Factual and functional integrity | Is the information true, sufficient, current, and safe? | Source comparison, system exercise, expert review |
| Communicative fitness | Can the intended reader find and understand it in the right form? | Editorial and structural review |
| Quality in use | Can the intended reader achieve the intended goal effectively? | Task-based evaluation with representative users |

The layers require different evidence. A readability review cannot establish factual
accuracy, and a source comparison cannot establish that a reader can find or apply the
information.

### Quality depends on the reader, goal, and context

ISO 9241-11 defines usability in relation to specified users achieving specified goals
with effectiveness, efficiency, and satisfaction in a specified context of use. The
definition prevents a context-free declaration that documentation is simply “usable.”
([ISO 9241-11:2018](https://www.iso.org/standard/63500.html))

The COCA quality model makes the same dependency explicit. It defines completeness as
providing the information end users need to use the described software, and observes
that usefulness can change when the software version changes. COCA reduces user-manual
quality to Completeness, Operability, Correctness, and Appearance, evaluated from the
end-user viewpoint in a given system context.
([Zalewski et al., *The COCA quality model for user documentation*](https://doi.org/10.1007/s11219-014-9252-4))

COCA is useful evidence for keeping dimensions distinct and evaluation contextual, but
its scope is too narrow to adopt unchanged. Buzz contains architecture, policy,
invariants, interfaces, evidence-bearing reference, development material, and agent
instructions—not only manuals supporting end users performing business tasks.

### Intrinsic quality and contextual quality must not be confused

Treude, Middleton, and Atapattu proposed ten dimensions that technical editors could
judge largely from a document alone: general writing quality, appeal, readability,
understandability, structure, cohesion, conciseness, effective technical vocabulary,
terminology consistency, and clarity. They deliberately excluded accuracy,
completeness, relevance, and timeliness because those require comparison with an
external artifact or task. Their pilot involved four technical editors and 41
R-related documents, producing 75 assessments.
([Treude et al., *Beyond Accuracy: Assessing Software Documentation Quality*](https://doi.org/10.1145/3368089.3417045))

That exclusion is a methodological strength for evaluating prose in isolation and a
reason the framework cannot govern the Buzz review by itself. The most consequential
qualities of an authoritative technical corpus—truth, coverage, relevance, and
currency—are precisely the ones that require leaving the page and checking the world.
The study is also explicitly preliminary; its authors call for end-user validation and
further work on overlap and trade-offs between dimensions.

An industrial action-research study offers a complementary view. Twenty-five of 135
invited engineers at one company rated ten attributes: completeness, organization,
visual models, relevance, precision, readability, accuracy, consistency, currency,
and examples. Readability, relevance, and organization were perceived as having the
largest impact; currency, precision, and examples showed the largest gaps between
existing and desired quality. The small, single-company sample limits generalization,
but the study demonstrates that practitioners value both page-intrinsic qualities and
qualities requiring context.
([Garousi et al., *Evaluating usage and quality of technical software documentation*](https://doi.org/10.1145/2460999.2461003))

### A compact model is useful, but oversimplification hides defects

COCA argues for four orthogonal characteristics so assessors do not double-count the
same concern. Treude et al. use ten text-focused dimensions. Garousi et al. ask
practitioners about ten broader attributes. Diátaxis warns that several functional
qualities can fail independently. These are competing decompositions rather than one
consensus taxonomy.

The 2019 ICSE study *Software Documentation Issues Unveiled* analyzed 878 artifacts
from mailing lists, Stack Overflow, issue repositories, and pull requests and derived
162 documentation-issue types across information content, presentation, process, and
tool support. Its conclusion summarizes reader and developer preference for
documentation that is correct, complete, current, usable, maintainable, readable, and
useful. The study is an issue taxonomy rather than a quality model, but it is strong
counterevidence to the idea that a short prose-style checklist captures the defect
surface.
([Aghajani et al., *Software Documentation Issues Unveiled*](https://doi.org/10.1109/ICSE.2019.00122))

The appropriate compromise for Buzz is a compact set of top-level dimensions with
genre-specific criteria beneath them. This keeps the review navigable without claiming
that every document has the same content obligations.

### Style guidance is subordinate to quality standards

The Google developer documentation style guide presents itself as a house style, not
an industry standard. It tells readers to follow project-specific guidance first and
allows departure when clarity and consistency improve. Its value here is concrete
editorial guidance—active voice, direct address, descriptive links, unambiguous dates,
accessible images, and consistent terminology—not authority over factual or
architectural correctness.
([Google developer documentation style guide](https://developers.google.com/style),
[guide philosophy](https://developers.google.com/style/philosophy))

ISO 24495-1:2023 applies plain-language principles to technical writing as well as
general-public documents, but explicitly leaves digital accessibility to other
guidance. Plain language therefore supports comprehensibility; it is not a complete
technical-documentation quality model.
([ISO 24495-1:2023](https://www.iso.org/standard/78907.html))

### Accessibility is part of content quality but has its own conformance model

WCAG 2.2 covers perceivable, operable, understandable, and robust web content. Its
success criteria are designed to be testable using both automation and human
evaluation, and W3C recommends 2.2 as the current conformance target. WCAG applies to
the published rendering as well as authored content: meaningful structure, link text,
text alternatives, readable language, and non-visual equivalents begin in the source,
while keyboard behavior, contrast, and responsive reflow depend on presentation.
([WCAG 2.2](https://www.w3.org/TR/WCAG22/),
[WAI accessibility principles](https://www.w3.org/WAI/fundamentals/accessibility-principles/))

For a content-only review, the checklist should assess accessibility properties the
author controls and explicitly defer renderer-dependent conformance rather than
declaring the node accessible in isolation.

## Candidate quality model for the Buzz corpus

The following model is a synthesis, not a finding copied from any one source.

### 1. Integrity

**Definition:** Substantive claims are correct at the stated revision, supported by
appropriate authority, classified honestly, and do not conceal material uncertainty
or contradiction.

**Why it is distinct:** A document can be clear, complete, and useful while being
wrong. Those qualities must not compensate for false information.

**Candidate review questions:**

- Does each claim agree with the appropriate primary evidence?
- Does the evidence support the exact claim rather than merely concern the same topic?
- Are current behaviour, intended behaviour, requirements, inference, and team
  knowledge kept distinct?
- Are material conflicts and limitations visible where they affect the conclusion?
- Could following an inaccurate claim create security, data-loss, or operational harm?

**Evaluation:** Evidence replay, source comparison, and exercising the system where
practical. Treat a material failure as a gate.

### 2. Sufficiency and relevance

**Definition:** The node contains enough of the information its declared purpose and
audience require, excludes irrelevant digression, and states important omissions.

**Why it is distinct:** Completeness is never “everything known.” COCA and usability
theory make it relative to a reader and goal. Relevance can also be high while required
information is absent.

**Candidate review questions:**

- Is the node's purpose specific enough to judge what belongs?
- Does it answer the questions that purpose creates?
- Are prerequisites, constraints, boundary conditions, failure modes, and exceptions
  present when the genre requires them?
- Does it claim or imply exhaustiveness beyond the evidence?
- Are omissions explicit enough that a reader will not mistake silence for absence?

**Evaluation:** Coverage against the node's declared scope, representative reader
questions, and the system surface it documents. Safety-critical omissions are gates;
ordinary coverage gaps are findings.

### 3. Purpose and genre fitness

**Definition:** The node performs one recognizable job for its intended reader and
uses a form appropriate to that job.

**Why it is distinct:** A factually correct explanation can still be a poor runbook,
and a detailed procedure can obstruct a reference lookup. Diátaxis is persuasive here
as a diagnostic framework, though Buzz's taxonomy also includes normative and
architecture genres outside its four-part model.

**Candidate review questions:**

- What reader need does this node serve?
- Is it primarily describing, explaining, directing action, or imposing a requirement?
- Does its structure match that purpose?
- Has material belonging to another genre obscured the primary job?
- Is it one independently maintainable idea rather than several adjacent topics?

**Evaluation:** Genre-specific review. The next research topic must define the detailed
criteria; this dimension only establishes the common requirement.

### 4. Comprehensibility and precision

**Definition:** The intended reader can derive the intended meaning without avoidable
ambiguity, unexplained terminology, or unnecessary cognitive burden.

**Why it is distinct:** Readability, understandability, clarity, concision, and
technical-vocabulary use repeatedly appear in research, but are overlapping lenses on
whether meaning transfers accurately.

**Candidate review questions:**

- Are sentences and terms unambiguous in context?
- Is technical vocabulary necessary, defined, and used with its domain meaning?
- Are actors, conditions, scope, and causality explicit?
- Is the prose concise without deleting necessary reasoning or qualifications?
- Can a reader distinguish examples, facts, recommendations, and requirements?

**Evaluation:** Editorial review, terminology checks, and comprehension testing where
consequences justify it. Readability formulas alone are insufficient because they do
not establish technical meaning.

### 5. Organization and findability

**Definition:** Information is divided, ordered, titled, and linked so the intended
reader can locate the needed statement with reasonable effort.

**Why it is distinct:** A reader can understand every paragraph after finding it while
still being unable to discover the right paragraph. Structure and retrievability are
properties of both node and corpus.

**Candidate review questions:**

- Do the title and opening reveal the node's subject and purpose?
- Do headings and tables expose its information structure?
- Is information placed where a reader would predict?
- Do links provide necessary context without duplicating another authority?
- Can likely search terms lead to this node and the relevant section?

**Evaluation:** Inspection plus lookup tasks. Corpus-level navigation cannot be fully
judged one node at a time.

### 6. Consistency and coherence

**Definition:** The node is internally coherent and uses concepts, terminology,
relationships, and conventions consistently with the rest of the corpus unless a
difference is intentional and explained.

**Why it is distinct:** Locally correct nodes can collectively give contradictory or
fragmented answers. Treude et al. separate cohesion from terminology consistency;
Buzz also needs cross-node consistency.

**Candidate review questions:**

- Do sections support rather than contradict the central account?
- Are the same things named the same way?
- Do definitions and relationship directions agree across nodes?
- Is repeated information genuinely necessary and kept subordinate to its authority?
- Are intentional differences in scope or version explicit?

**Evaluation:** Within-node review, cross-node comparison, terminology search, and
relationship traversal.

### 7. Task effectiveness and usability

**Definition:** Representative readers can use the node to achieve its intended goal
effectively, with reasonable effort and confidence, in the relevant context.

**Why it is distinct:** Usefulness cannot be established by prose inspection alone.
ISO 9241-11's context-of-use model and COCA's operability focus both make this a
relationship between information, reader, goal, and system.

**Candidate review questions:**

- Can the intended reader answer the target question or complete the target task?
- Does the node reduce rather than transfer uncertainty?
- Are instructions executable in the stated environment?
- Can the reader recognize success, failure, and the next safe action?
- Does the node demand unnecessary time or prior knowledge?

**Evaluation:** Scenario-based lookup or task testing with representative readers.
Reviewer intuition is only a preliminary proxy.

### 8. Currency and maintainability

**Definition:** The node's claims, scope, and references correspond to the relevant
system and policy versions, and the content is shaped so likely changes can be located
and updated without hidden collateral drift.

**Why it is distinct:** A historically accurate document can become wrong without any
prose defect. Both empirical studies and the Buzz corpus contract identify staleness as
a separate failure mode.

**Candidate review questions:**

- What system or decision revision does the node describe?
- Have its cited sources or governed behavior changed?
- Does it duplicate volatile details that should be referenced or generated?
- Are statements with different maintenance clocks incorrectly fused?
- Is deprecated or retired knowledge visibly marked and connected to its replacement?

**Evaluation:** Revision comparison, source-change review, and maintenance-boundary
inspection. A valid old citation establishes reproducibility, not present currency.

### Cross-cutting condition: accessibility

For every dimension, ask whether the source content remains perceivable,
understandable, navigable, and semantically meaningful to readers with a wide range of
capabilities. At the source level this includes meaningful heading order, descriptive
links, text alternatives, non-color-dependent meaning, understandable language, and
accessible table structure. Renderer-dependent WCAG criteria need separate publication
testing.

## Evaluation model

### Do not produce a single quality score

The sources do not establish defensible weights for this corpus. An average also hides
non-compensatory failures. Report each dimension separately using findings supported by
examples.

A practical result format would be:

| Verdict | Meaning |
|---|---|
| Gate failure | The content cannot be trusted or safely used until corrected |
| Material deficiency | The node substantially fails its purpose for the intended audience |
| Improvement | The node is usable but has a bounded quality defect |
| Meets current criterion | No material defect was found within the evidence reviewed |
| Not applicable | The criterion does not apply to this node's purpose or genre |
| Not evaluated | The criterion applies but the review did not establish it |

“Meets current criterion” is deliberately not “perfect” or “complete.” It records what
the review established within its stated scope.

### Separate inspection from use testing

| Method | Can establish | Cannot establish alone |
|---|---|---|
| Schema and automated checks | Required structure, allowed values, resolvable forms | Semantic truth, usefulness, comprehension |
| Expert content review | Claim support, technical plausibility, genre and structural defects | Representative-reader success |
| Editorial review | Clarity, consistency, ambiguity, organization | System correctness or task success |
| Source and system verification | Accuracy and version alignment | Findability or human comprehension |
| Reader/task testing | Effectiveness, efficiency, comprehension, confidence | Exhaustive technical accuracy |
| Accessibility evaluation | Applicable source and rendered-content barriers | General technical correctness |

A trustworthy assessment states which methods were actually used. “Reviewed” is too
ambiguous to carry that information.

## Fit with the current Buzz corpus

The local corpus already has meaningful pieces of this model:

- [`AGENTS.md`](../../docs/corpus/AGENTS.md) requires one independently maintainable
  idea, claim-level evidence, explicit scope and omissions, and honest classification
  of facts, inferences, and team knowledge.
- [`review-requirements.md`](../../docs/corpus/standards/review-requirements.md)
  requires reviewers to open `FACT` citations, pair body claims with ledger entries,
  judge inferences, check relationship direction, and preserve unresolved conflicts.
- [`atomicity.md`](../../docs/corpus/standards/atomicity.md) addresses maintenance
  boundaries rather than merely document length.
- [`documentation-standard.md`](../../docs/corpus/standards/documentation-standard.md)
  governs the shape of corpus *standards*. It explicitly records that the human chose
  that narrow reading over a prose-quality standard across all nodes. It must not be
  mistaken for the general quality model this research explores.

The major content-quality gap is not absence of rules. It is absence of one explicit
model connecting those truth and maintenance rules to reader-centred dimensions such
as purpose, comprehensibility, findability, task success, and accessibility. The
existing validator also discards body prose; local standards correctly say that a
green run cannot establish the content dimensions above.

This research does not conclude that a new corpus standard should be written. It only
identifies the model against which a future content review could be designed.

## Competing positions and resolution

### Minimal versus comprehensive models

- **Minimal position:** COCA's four characteristics make evaluation manageable and
  reduce overlapping findings.
- **Comprehensive position:** Empirical issue taxonomies and practitioner studies show
  many independently meaningful failure modes.
- **Resolution for this research:** Use eight stable top-level dimensions, then attach
  genre-specific checks. Do not flatten every defect into a new top-level dimension.

### Context-free inspection versus contextual evaluation

- **Context-free position:** Treude et al.'s ten dimensions allow consistent editorial
  assessment without reconstructing the task or system.
- **Contextual position:** Accuracy, relevance, sufficiency, currency, and usability
  cannot be established from the page alone.
- **Resolution:** Preserve both as different evaluation methods. Intrinsic prose
  quality is necessary but insufficient for an authoritative corpus.

### Objective conformance versus human judgement

- **Conformance position:** Testable rules make quality repeatable and auditable.
- **Judgement position:** Diátaxis argues that fit, flow, and anticipation of user needs
  require human judgement.
- **Resolution:** Automate objective constraints, structure expert review around named
  dimensions, and use representative users for claims about quality in use. Never
  present one method as establishing what only another can observe.

### Universal criteria versus genre-specific criteria

- **Universal position:** A shared model makes corpus-wide results comparable.
- **Genre-specific position:** Completeness and fitness mean different things for a
  reference node, runbook, architectural flow, invariant, or policy.
- **Resolution:** The eight dimensions are universal questions; their acceptance
  criteria are genre-specific. Topic 2 must develop that second layer.

## Claim ledger

| Material claim | Main support | Counterevidence or limitation | Confidence |
|---|---|---|---|
| Documentation quality is multidimensional | ISO 26514 public introduction; Diátaxis; COCA; Treude; Garousi | Sources disagree on grouping and dimension count | High |
| Quality dimensions can fail independently | Diátaxis functional-quality model; COCA orthogonality argument | Some proposed dimensions overlap in practice | High |
| Usability, relevance, and completeness require context | ISO 9241-11; COCA; Treude's explicit exclusions | Editorial proxies may still identify likely problems | High |
| Accuracy is necessary but insufficient | ISO 26514; Diátaxis; Treude; Aghajani | “Necessary” depends on the claim being used as current authority; clearly marked fiction/examples differ | High for this corpus |
| One aggregate score is unsuitable for Buzz | Independent dimensions and non-compensatory integrity failures | No Buzz-specific scoring experiment was performed | Moderate-high |
| Eight dimensions are a workable consolidation | Crosswalk and analysis in this report | This exact model is novel and untested | Moderate |
| Accessibility must cross-cut the content model | WCAG; ISO 26514 accessibility definition; ISO 24495's explicit accessibility boundary | Some WCAG obligations belong to the renderer rather than the source node | High |
| Local structural validation cannot establish content quality | Corpus validator behavior as documented by local standards | A future validator could add semantic heuristics, but still not establish all dimensions | High |

## Candidate criteria produced by this research

These are inputs to a later checklist synthesis, not adopted requirements:

1. Assess every node against named, separate quality dimensions.
2. Define the node's audience, purpose, task, and relevant system state before judging
   completeness, relevance, or usability.
3. Treat material integrity failures and safety-critical omissions as gates.
4. Do not average dimension results into a score that can hide a gate failure.
5. Distinguish “not applicable” from “not evaluated.”
6. Record the evaluation method used for each finding.
7. Use source/system verification for accuracy, editorial review for communication,
   and representative-reader tasks for quality-in-use claims.
8. Apply universal quality dimensions through genre-specific acceptance criteria.
9. Evaluate source-level accessibility during content review and renderer-dependent
   WCAG conformance separately.
10. Preserve limitations and unresolved evidence beside the affected conclusion.

## Uncertainties and limitations

- No full ISO or IEC standard was accessed. Public ISO descriptions establish their
  scope and status, not their complete requirements. ISO's site also restricts use of
  its publications with AI systems; this report therefore does not reproduce or claim
  to operationalize protected standard text.
- ISO/IEC/IEEE 26513:2017 is the current published review standard but is expected to
  be replaced by a second edition whose final draft is in approval. Because this topic
  concerns the quality model rather than review process, neither edition was used to
  derive detailed criteria.
- The empirical studies have limited samples or contexts: four editors and 41
  R-related documents for Treude et al.; 25 respondents in one company for Garousi et
  al.; nine education-software manuals for COCA's initial quality profiles.
- This research did not sample the 205 Buzz corpus nodes or test the candidate model
  with Buzz developers, operators, reviewers, or agents.
- No weights, pass threshold, sampling rate, or review cadence is proposed.
- Detailed completeness, usability, freshness, accessibility, and corpus-scale review
  methods remain separate queued research topics.

## Sources

### Standards and authoritative frameworks

- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/standard/77451.html)
- [IEC/IEEE 82079-1:2019 — Preparation of information for use](https://www.iso.org/standard/71620.html)
- [ISO 24495-1:2023 — Plain language](https://www.iso.org/standard/78907.html)
- [ISO 9241-11:2018 — Usability: definitions and concepts](https://www.iso.org/standard/63500.html)
- [ISO/IEC/IEEE 26513:2017 — Requirements for testers and reviewers](https://www.iso.org/standard/67417.html)
- [ISO/IEC/IEEE FDIS 26513 — replacement under development](https://www.iso.org/standard/89070.html)
- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
- [Diátaxis: Towards a theory of quality in documentation](https://diataxis.fr/quality/)
- [Google developer documentation style guide](https://developers.google.com/style)

### Research

- [Treude, Middleton, and Atapattu (2020), *Beyond Accuracy: Assessing Software Documentation Quality*](https://doi.org/10.1145/3368089.3417045)
- [Zalewski et al. (2015), *The COCA quality model for user documentation*](https://doi.org/10.1007/s11219-014-9252-4)
- [Garousi et al. (2013), *Evaluating usage and quality of technical software documentation: An empirical study*](https://doi.org/10.1145/2460999.2461003)
- [Aghajani et al. (2019), *Software Documentation Issues Unveiled*](https://doi.org/10.1109/ICSE.2019.00122)

### Buzz corpus sources inspected

- [`launchpad/docs/corpus/AGENTS.md`](../../docs/corpus/AGENTS.md)
- [`launchpad/docs/corpus/standards/documentation-standard.md`](../../docs/corpus/standards/documentation-standard.md)
- [`launchpad/docs/corpus/standards/review-requirements.md`](../../docs/corpus/standards/review-requirements.md)
- [`launchpad/docs/corpus/standards/evidence.md`](../../docs/corpus/standards/evidence.md)
- [`launchpad/docs/corpus/standards/confidence.md`](../../docs/corpus/standards/confidence.md)
- [`launchpad/docs/corpus/standards/atomicity.md`](../../docs/corpus/standards/atomicity.md)
- [`launchpad/docs/corpus/standards/taxonomy.md`](../../docs/corpus/standards/taxonomy.md)
