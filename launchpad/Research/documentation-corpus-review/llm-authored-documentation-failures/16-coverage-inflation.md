# Coverage inflation

| Metadata | Value |
|---|---|
| Topic number | 16 |
| Exact research question | How can large quantities of generated documentation create a false impression of corpus completeness while important components, workflows, decisions, or failure conditions remain undocumented? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Technical-documentation corpora expanded or maintained by agents, especially repository-derived reference, procedures, architecture, policy, and operational guidance. “Coverage” includes subjects, reader tasks, lifecycle states, variants, decisions, interfaces, and failure conditions—not merely files, words, headings, or documented symbols. Local observations are fixed to branch `docs/llm-research-program` at commit `ec2db2ec943838a7d1e20ebcc93c76cd1fdf2b0b`. |
| Evidence limitations | No located controlled study measures whether LLM-generated documentation volume causes reviewers to infer completeness in a production software corpus. The answer triangulates software-documentation studies, documentation frameworks, requirements traceability, coverage-metric research, hidden-stratification evidence, and local validator behavior. The psychological “impression” mechanism and its production prevalence therefore remain partly inferred. |

## Executive answer

Large quantities of generated documentation can inflate apparent coverage because the
visible numerator—pages, words, headings, symbols, or linked nodes—grows faster than the
team's definition of what must be covered. Agents are particularly good at producing
locally plausible descriptions for enumerable surfaces such as files, functions, and
configuration keys. Those surfaces are not a complete denominator for documentation.
Reader goals, cross-component workflows, operational transitions, rejected decisions,
negative behavior, permissions, rollback, recovery, and rare failure conditions often
live outside any single code unit and may be absent from the evidence supplied to the
agent.

This is a measurement problem before it is a prose problem. A corpus can have 100% of
public symbols documented and still lack a deployable path, an incident-recovery path,
or the reason a dangerous alternative was rejected. Diátaxis distinguishes tutorial,
how-to, reference, and explanation because they answer different user needs; multiplying
reference pages cannot substitute for the other three forms
([Diátaxis foundations](https://diataxis.fr/foundations/)). Practitioner research also
finds that useful documentation depends on the engineering task, while class-level
documentation studies report shortcomings despite the presence of documentation
([Aghajani et al., ICSE 2020](https://homepages.dcc.ufmg.br/~figueiredo/disciplinas/papers/icse20aghajani.pdf);
[Aghajani et al., 2022](https://arxiv.org/abs/2205.03344)).

The strongest supported conclusion is therefore: **volume and structural completeness
are weak proxies for demonstrated task and risk coverage**. This conclusion is high
confidence. The narrower claim that agent generation makes the illusion more common is
moderate confidence because low marginal generation cost, templated uniformity, and
source-bound enumeration plausibly strengthen the proxy, but no direct incidence study
was found.

The defensible remedy is not a universal quota. Define the coverage universe for each
corpus: audiences and tasks, system components and interfaces, lifecycle states,
supported variants, decisions and rationales, and risk/failure scenarios. Trace documents
to those obligations, record deliberately undocumented and not-applicable cells, test
representative reader workflows, and report coverage by meaningful stratum with unknowns
visible. Treat raw counts and schema-valid nodes as inventory evidence only.

## Question, scope, and method

### Subquestions

- Which quantity and structure signals are commonly mistaken for substantive coverage?
- What important documentation obligations are not naturally enumerable from code?
- How do generation, retrieval, templates, and review incentives amplify the mismatch?
- How can coverage be measured without inventing a false or circular denominator?
- Which checks reveal important missing strata, and what can they not prove?
- When is high-volume generated reference genuinely useful rather than inflationary?

### Exclusions

- General omission mechanisms except where they explain a corpus-level coverage claim.
- The factual correctness of present passages; a corpus may be accurate yet incomplete.
- A claim that any particular corpus size is excessive.
- Program-wide synthesis or adoption of a documentation policy.
- A requirement that every system fact be documented; unnecessary detail can reduce
  findability and impose maintenance cost.

### Evidence and source plan

Local inspection counted 945 Markdown files beneath `launchpad/`, including 374 beneath
`launchpad/docs/corpus`, at the recorded revision. These counts are observations, not
quality judgments. The local validator describes a deliberately narrower contract: it
checks schemas, relationships, citation forms, ownership, and canonical locations while
reporting some evidence as unverified
([validator source](../../../project-intelligence/corpus/validate.py)). That is a useful
positive example of a tool stating what a pass does not mean.

External evidence was planned across five strands: practitioner studies of documentation
use; documentation type and task frameworks; requirements traceability; empirical work
on documentation quality; and measurement research showing how aggregates obscure
important subgroups. Material claims were tracked with their context and counterevidence.
Searches sought examples where more documentation helps, where sparse documentation is
intentional, and where task tests or schemas themselves miss unknown categories. The stop
condition was reached when each subquestion had either triangulated support or an explicit
gap and further searches repeated the same distinction between inventory, quality, task,
and risk coverage.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Inventory substitution | File, page, word, heading, or documented-symbol counts are presented or perceived as coverage of the system. | Counts are reproducible inventory measures, but they require an independently justified denominator and say nothing about utility or truth. NIST's AI RMF requires context-relevant metrics and documentation of risks that cannot be measured ([AI RMF Core, Measure 1](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)). |
| Reference monoculture | Agents generate broad API, configuration, or component reference while tutorials, task procedures, and explanations remain sparse. | Diátaxis treats four document forms as answers to distinct practitioner needs; it also warns against merely creating empty structures ([how to use Diátaxis](https://diataxis.fr/how-to-use-diataxis/)). The framework is practice guidance, not a controlled completeness experiment. |
| Code-shaped blind spots | Coverage follows syntax trees, directories, or public symbols and misses cross-service behavior, operations, governance, and intent. | Mixed-method practitioner research found documentation needs vary with software-engineering task ([Aghajani et al.](https://homepages.dcc.ufmg.br/~figueiredo/disciplinas/papers/icse20aghajani.pdf)). Code-derived generation can still be valuable for truly code-defined reference. |
| Happy-path saturation | Many similar setup and usage pages cover common success while prerequisites, partial failure, rollback, repair, and unsupported states remain absent. | The mechanism is an interpretation of source selection and authoring incentives. It should be tested against an explicit scenario catalogue, not inferred from document tone. |
| Variant collapse | One platform, version, role, deployment mode, or permission level is described repeatedly and appears representative of all supported variants. | Hidden-stratification research demonstrates the general measurement hazard: strong aggregate results can conceal poor performance in important rare subsets ([Oakden-Rayner et al., 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7665161/)). Transfer from medical ML evaluation to documentation coverage is analogical. |
| Decision erasure | Current structure is exhaustively described while rationale, alternatives, constraints, and superseded decisions are absent. | Source code often establishes what exists, not why it was chosen. A code-only denominator cannot reveal missing decision evidence by construction. |
| Validation halo | A build, schema, link, lint, or corpus validator passes and the result is generalized to “documentation complete.” | The local validator explicitly separates hard errors from unverified evidence and does not test reader-task completeness. The failure is overclaiming the gate, not running it. |
| Retrieval visibility bias | Frequently linked or lexically repetitive topics dominate search and agent retrieval; absent topics produce no contradictory evidence and remain invisible. | This is a plausible information-retrieval mechanism. No located study quantified it end to end for a generated technical corpus. |
| Unknown-denominator concealment | A percentage is reported without listing excluded, unknown, unsupported, or not-applicable obligations. | NIST recommends documenting metric-selection criteria and unmeasured risks ([AI RMF Playbook, Measure](https://airc.nist.gov/airmf-resources/playbook/measure/)). A percentage is only interpretable with universe, unit, and exclusions. |

## Causes and mechanisms

### Cheap production changes the visible signal

Generation lowers the cost of producing grammatical, similarly structured pages. That is
useful when the target set is correct, but it lets volume grow without a corresponding
increase in discovery work. Uniform templates also make covered and weakly evidenced
subjects look equally mature. This causal account is an inference from agent capability,
not a measured psychological effect size.

### The source supplies a biased denominator

Repository structures expose modules, declarations, flags, and tests more readily than
user goals, informal operational knowledge, external dependencies, and abandoned design
paths. An agent asked to “document the repository” may enumerate what search and parsers
can see. Missing subjects do not announce themselves. A coverage plan generated from the
same incomplete context as the prose is circular: the source that caused the omission
also certifies that nothing was omitted.

### Different genres are not interchangeable

A reference answers “what is this?”; a how-to answers “how do I achieve this goal?”; a
tutorial creates a learning experience; explanation supports understanding. These are not
merely layouts. Repeating reference content inside several pages can increase word count
while leaving a workflow or mental-model gap unchanged. Conversely, not every component
needs all four genres: the required mix depends on audience and task.

### Review samples what exists

Conventional line review directs attention to changed text. Reviewers can correct every
sentence presented without discovering an absent recovery procedure or unrepresented
operator role. Large diffs increase sampling pressure, and a polished table of contents
provides an availability cue. Direct documentation-agent evidence for this review effect
is absent; topic 18 investigates the human factors separately.

### Aggregate status suppresses weak strata

One scalar weights common pages and common tasks more heavily unless explicitly designed
otherwise. Hidden-stratification research provides a transferable warning: aggregate
performance can remain strong while a rare, important subgroup performs badly, and even
expert-defined schemas cannot protect against categories experts failed to define. For
documentation, the analogous strata may be destructive commands, new-user setup,
accessibility, degraded operation, a minority platform, or an infrequent incident.

## Detection and validation

| Method | What it can establish | What it cannot establish |
|---|---|---|
| Artifact inventory | Which expected files, headings, fields, symbols, and links exist. | Whether their contents are correct, sufficient, discoverable, or useful. |
| Traceability matrix | Whether declared components, requirements, decisions, tasks, and risks map to at least one maintained artifact. | Whether the declared universe is complete or the mapped passage actually satisfies the obligation. |
| Audience-task journeys | Whether representative readers can complete specified tasks using the corpus under observed conditions. | Universal coverage; sampled success paths do not expose every role, environment, or failure. |
| Scenario and state-transition review | Whether normal, degraded, failed, recovery, rollback, upgrade, and decommission states have actionable guidance where needed. | Unknown scenarios or whether every instruction works unless executed. |
| Stratified coverage dashboard | Coverage and validation results by component, role, lifecycle state, risk, platform, and genre, including unknowns. | A single truth score; strata and weights remain governance choices. |
| Search and retrieval tests | Whether representative queries find the authoritative current answer and avoid duplicate noise. | Whether unasked questions or unmodeled vocabulary are covered. |
| Change-impact analysis | Whether changed behavior has mapped documentation dependants and owners. | Unrecorded dependencies or historically missing documentation. |
| Qualitative gap audit | Expert comparison of code, tests, incidents, decisions, support questions, and observed workflows against the corpus. | Complete objectivity or low cost; expertise and evidence access constrain results. |

A sound coverage statement should name the unit, universe, revision, exclusions, evidence,
and validation method. “83% of declared operator scenarios have an owned page and passed
their scripted smoke test at revision X” is bounded. “Documentation is 83% complete” is
not.

## Mitigations

1. **Define obligations before generating prose.** Build the initial map from independent
   sources: supported-product declarations, user research, architecture, incidents,
   runbooks, tests, decisions, support requests, and domain experts. Preserve disagreements
   and unknowns.
2. **Keep multiple coverage axes.** Track components, interfaces, roles, tasks, lifecycle
   states, variants, risks, and document genres separately. Do not collapse them into one
   percentage unless the aggregation rule and loss are explicit.
3. **Represent absence.** A cell should distinguish covered, partially covered, planned,
   deliberately omitted, unsupported, not applicable, and unknown. Blank cells invite
   optimistic interpretation.
4. **Prioritize by consequence and demand.** A rare recovery procedure may matter more
   than hundreds of low-risk symbol descriptions. Volume should not determine review
   priority.
5. **Generate in bounded batches.** Require an evidence and coverage delta for each batch:
   which obligations became supported, which remain open, and what new maintenance sites
   were introduced.
6. **Test documents as interfaces.** Run commands and examples where safe, exercise reader
   journeys, test search vocabulary, and record environment and result. Passing one layer
   must not be promoted into an overall assurance claim.
7. **Reduce duplicative volume.** Generate reference from schemas or code when those are
   authoritative; reuse volatile facts; link rather than paraphrase when repetition adds
   no reader value.
8. **Audit the denominator periodically.** Product changes, incidents, and reader support
   reveal new obligations. Treat the coverage model as revisioned evidence, not a fixed
   ontology.

These controls trade speed for discovery and maintenance. Exhaustive matrices can become
performative inventories of their own. The mitigation is risk-based sampling, explicit
ownership, and deletion of fields that do not support a decision—not more metadata for its
own sake.

## Limits and open questions

- No direct study found here establishes that readers systematically equate LLM-generated
  documentation volume with completeness. The proposed “coverage halo” is plausible and
  should be experimentally tested.
- Diátaxis is a coherent practitioner framework, not an empirical guarantee that four
  categories cover every organizational need or that each product needs equal investment
  in them.
- Practitioner surveys report perceptions and task associations; they do not yield a
  universal denominator for a particular repository.
- Hidden stratification is evidence about aggregate evaluation in another domain. It
  supports the measurement warning, not a numerical estimate for documentation defects.
- More documentation is not inherently harmful. Generated exhaustive API reference can
  materially improve access when it is accurate, current, searchable, and paired with the
  other information readers need.
- Sparse documentation can be a deliberate interface choice, and some rationale or
  operational information must remain private. “Not publicly documented” is not
  automatically a quality defect.
- Unknown unknowns remain: any checklist inherits its designers' model of the product.
  Incident analysis, observed reader failure, and rotating external review are important
  because they can expand that model.
- Open questions include how to measure workflow coverage without freezing workflows,
  how to weight rare catastrophic tasks, and whether provenance-aware retrieval can expose
  absence rather than only rank present passages.

## Practical review checks

- Candidate check: reject any completeness percentage that lacks a named universe, unit,
  revision, exclusions, and handling of unknowns.
- Candidate check: compare growth in files and words with growth in independently defined
  covered tasks, risks, decisions, and validated scenarios.
- Candidate check: sample one common and one high-consequence rare task for every intended
  reader role and attempt them using only published documentation.
- Candidate check: enumerate normal, degraded, failed, recovery, rollback, upgrade, and
  retirement states; record covered, partial, not applicable, private, and unknown.
- Candidate check: inspect whether a large reference section is being counted as tutorial,
  how-to, or explanatory coverage without serving those needs.
- Candidate check: construct the coverage map from sources independent of the agent's
  generation context; record evidence conflicts rather than silently reconciling them.
- Candidate check: stratify validation results by component, role, platform, lifecycle,
  risk, and document type; never rely on the corpus-wide average alone.
- Candidate check: sample absent or low-link-density areas, not only popular pages and
  search results.
- Candidate check: require every automated pass statement to name what was not checked.
- Candidate check: delete or consolidate generated pages that add maintenance surface but
  no distinct reader task, evidence, or authoritative reference value.

## References

- [Diátaxis foundations](https://diataxis.fr/foundations/) — Daniele Procida, accessed 2026-09-09; four practitioner needs and corresponding documentation forms.
- [Diátaxis as a guide to work](https://diataxis.fr/how-to-use-diataxis/) — Diátaxis, accessed 2026-09-09; incremental application and warning against empty categorical structure.
- [Software Documentation: The Practitioners’ Perspective](https://homepages.dcc.ufmg.br/~figueiredo/disciplinas/papers/icse20aghajani.pdf) — Aghajani et al., ICSE 2020; survey evidence about useful artifacts and engineering-task context.
- [Shortcomings of Class-level Documentation: A Survey](https://arxiv.org/abs/2205.03344) — Aghajani et al., 2022; survey of 167 experienced developers on shortcomings in present class-level documentation.
- [When Not to Comment: Questions and Tradeoffs with API Documentation for C++ Projects](https://research.google/pubs/when-not-to-comment-questions-and-tradeoffs-with-api-documentation-for-c-projects/) — Parnin et al., ICSE 2018; mixed-method evidence on API-documentation trade-offs and information seeking.
- [Beyond Accuracy: Assessing Software Documentation Quality](https://arxiv.org/abs/2007.10744) — Aghajani et al., 2020; multi-attribute framework and assessment across documentation types.
- [The COCA quality model for user documentation](https://doi.org/10.1007/s11219-014-9252-4) — van der Meij et al., *Software Quality Journal*, 2015; review-based and empirical user-documentation quality model.
- [Artificial Intelligence Risk Management Framework 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) — NIST AI 100-1, January 2023; context-specific measurement, uncertainty, limitations, and unmeasured-risk disclosure.
- [AI RMF Playbook: Measure](https://airc.nist.gov/airmf-resources/playbook/measure/) — NIST AI Resource Center, accessed 2026-09-09; metric-selection criteria, unused metrics, and context-relevant evaluation.
- [Hidden Stratification Causes Clinically Meaningful Failures in Machine Learning for Medical Imaging](https://pmc.ncbi.nlm.nih.gov/articles/PMC7665161/) — Oakden-Rayner et al., CHIL 2020; empirical evidence that aggregates can conceal important weak subsets and discussion of schema-completion limits.
- [Local corpus validator](../../../project-intelligence/corpus/validate.py) — launchpad-26/buzz revision `ec2db2ec943838a7d1e20ebcc93c76cd1fdf2b0b`, inspected 2026-09-09; direct evidence of a bounded structural validator and explicit unverified channel.
