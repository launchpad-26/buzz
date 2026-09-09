# Cross-document consistency and terminology drift

| Metadata | Value |
|---|---|
| Topic number | 14 |
| Exact research question | How do repeated agent edits produce contradictory claims, inconsistent terminology, incompatible instructions, and divergent mental models across a documentation corpus? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Repeated LLM-agent edits to multi-file technical-documentation corpora, including prose, procedures, policy, architecture descriptions, glossaries, structured metadata, and versioned documentation. The analysis covers creation, revision, retrieval, review, and corpus-level validation. Local repository observations are fixed to branch `docs/llm-research-program` at revision `81b5a1d059ea897968c4fe412497a351892d4598`. |
| Evidence limitations | No cited controlled study isolates repeated agent edits to a multi-file technical-documentation corpus. The most direct evidence is a 2026 preprint stress test of repeated edits to professional artifacts; the cross-document causal account therefore triangulates that result with peer-reviewed long-context, contradiction-detection, software-documentation, and corpus-consistency research plus authoritative documentation standards. Prevalence in production documentation remains unknown, and every affected conclusion below is bounded accordingly. |

## Executive answer

Repeated agent edits produce corpus drift when each edit is locally plausible but is not
validated against the corpus's shared claims, concepts, authority hierarchy, versions, and
reader workflows. The agent may preserve the edited paragraph while failing to update a
duplicate statement, rename a concept in only some locations, blend requirements from
different authorities, or rewrite one architectural view without its related views. Later
edits then operate on this already-divergent state. The result is not one failure but a
feedback process: local context selection hides dependencies; stochastic generation varies
wording and interpretation; copied facts create multiple maintenance sites; version and
scope qualifiers disappear; and weak validation accepts fluent, schema-valid text.

**Confidence is high** that repeated delegated editing can accumulate semantic damage in
the tested conditions. DELEGATE-52 found degradation across all 19 tested models and worse
results with longer interactions, larger documents, and distractor files. However, it is a
transformation-and-inversion stress test over professional artifacts, not a longitudinal
study of documentation teams or a multi-file technical-doc corpus. Its authors explicitly
warn against treating it as a measure of overall capability or real-user outcomes
([Laban, Schnabel, and Neville, 2026](https://arxiv.org/abs/2604.15597);
[authors' limitations note](https://www.microsoft.com/en-us/research/blog/further-notes-on-our-recent-research-on-ai-delegation-and-long-horizon-reliability/)).
**Confidence is moderate** in the full causal account for technical documentation because
it is a triangulated inference rather than a directly measured end-to-end effect.

The defensible control strategy is layered. Give each mutable claim and concept a declared
authority, scope, and version; reuse volatile content from one maintained representation
where practical; keep a controlled concept/term register; require change-impact discovery;
run lexical, structural, executable, and semantic checks; and have a human review the
remaining conflicts in the context of real reader tasks. No single layer proves corpus
consistency. In particular, style lint detects preferred forms but not truth, schemas detect
shape but not meaning, tests cover only encoded invariants, and semantic models still miss
nuanced or distant contradictions.

## Question, scope, and method

### Subquestions

- What distinct forms can inconsistency and terminology drift take across a corpus?
- Which properties of repeated agent editing make these failures accumulate?
- How do divergent documents produce incompatible reader actions and mental models?
- Which lexical, structural, executable, semantic, temporal, and human checks detect each
  class, and what can each check not establish?
- Which mitigations reduce the number of independent facts and meanings that must
  co-evolve, and what new risks or trade-offs do they introduce?
- Where is direct evidence about agents insufficient, and which alternative explanations
  or boundary cases weaken the emerging answer?

### Exclusions

- General hallucination, citation fabrication, security disclosure, and summarization
  fidelity except where they directly create or conceal cross-document inconsistency.
- Consistency between documentation and source code as the central problem; it appears
  only where code, configuration, or tests can validate a corpus claim.
- Model-parameter knowledge editing, collaborative-editor convergence algorithms, and
  translation quality as independent research topics.
- A synthesis of the other reports in this research program or a proposal to adopt policy.
- Claims about a specific vendor agent beyond the model/version/date actually studied.

### Evidence and source plan

The inquiry first inspected the governing local documents, the research controls, the
current documentation-corpus validator, and an observable contradiction between a
reader-facing README and its declared normative source. External research then covered:
(1) direct repeated document editing, (2) long-context evidence use, (3) real corpus and
document contradiction detection, (4) software-practitioner experience, (5) terminology
and normative-writing standards, and (6) reuse, versioning, and lint mechanisms.

Material claims were tracked by support, counterevidence, context, confidence, and gap.
Searches explicitly sought negative results, benchmark limitations, legitimate terminology
variation, and controls that do not generalize. The stop condition was reached when each
subquestion had either triangulated support or an explicit gap and further searches repeated
the same mechanisms or tools without adding a new failure class.

| Evidence strand | Best evidence used | What it establishes | Important boundary |
|---|---|---|---|
| Repeated agent edits | DELEGATE-52, 19 models, 52 domains | Semantic fidelity can degrade over long edit sequences; length and distractors matter | Preprint stress test; mostly single work environments, not a production documentation corpus |
| Global document operations | DocOps benchmark | Agents exhibit long-term state-tracking and semantic-verification failures | July 2026 preprint; not independently replicated here |
| Long input use | TACL multi-document retrieval experiments | Relevant evidence is not used uniformly across long contexts | Retrieval and QA tasks, not authoring |
| Corpus contradictions | WIKICOLLIDE/CLAIRE on a frozen Wikipedia dump | Corpus-level search is distinct from pairwise fact checking; automated detection has substantial headroom | Encyclopedic facts, not instructions; estimates depend on assisted discovery |
| Documentation maintenance | ICSE survey of 146 practitioners | Inconsistency and co-evolution are material practitioner concerns | Perception survey; 125 participants came from one company |
| Terms and authority | ISO, W3C, IETF, and Google guidance | Concepts, preferred terms, scope, and normative force need explicit conventions | Authoritative guidance, not causal experiments on agents |
| Reuse and validation | DITA, GitHub Docs, Vale, and local validator | Reuse and lint can reduce duplicate maintenance and lexical variance | They cannot establish that the canonical meaning is true or complete |

### Local bounded case

At the inspected revision, the launchpad README says a pull request should expect two
approving reviews, while the normative `launchpad/AGENTS.md` says one is required and
explicitly records that the old figure was wrong. The README also declares that AGENTS.md
wins when they disagree
([README, “Opening a PR”](../../../README.md#opening-a-pr);
[AGENTS.md, section 6](../../../AGENTS.md#6-branch-commit-pr)). This is a directly observed
cross-document contradiction, not evidence that an agent caused it. It illustrates two
separate findings: an authority hierarchy lets a diligent reader resolve a conflict, but it
does not stop the lower-authority entry point from giving an incompatible instruction.

The local deterministic validator describes its remit as schema validation plus duplicate
IDs, unresolved relationship targets, citation forms, and canonical-file checks; it does
not claim semantic comparison of prose
([`validate.py`](../../../project-intelligence/corpus/validate.py)). This demonstrates the
boundary between structural validity and semantic consistency in one corpus. It does not
show that this validator is deficient relative to its own contract.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Direct factual contradiction | Two claims about the same scoped subject cannot both be true: different defaults, limits, owners, dates, states, or behaviors. | Corpus-level inconsistency requires finding a refuting fact anywhere in the corpus, not merely finding one supporting passage ([Semnani et al., 2025](https://aclanthology.org/2025.emnlp-main.1765/)). Apparent conflicts may instead describe different times, products, or environments. |
| Term-form drift | One concept acquires variant names, capitalization, abbreviations, or spelling across documents, leading readers and tools to infer distinct concepts. | Google's current guidance says to use the same term and capitalization for a concept and identifies ambiguity and translation cost as consequences ([Google, updated 2026-08-25](https://developers.google.com/style/translation)). Variation is not automatically wrong when audience or interface vocabulary legitimately differs. |
| Concept collision | One surface term is used for multiple concepts, or an old term is reused after its meaning changes. | ISO 704 distinguishes objects, concepts, definitions, and designations; managing spelling alone is therefore insufficient ([ISO 704:2022](https://www.iso.org/standard/79077.html)). Domain-specific polysemy can be valid if the subject field and definition are explicit. |
| Definition fork | Multiple glossaries or inline definitions for one concept evolve independently, including aliases whose relationships are unstated. | W3C advises importing precise terminology and linking to existing definitions rather than creating new ones ([W3C Manual of Style](https://www.w3.org/guide/manual-of-style/)). A local definition can still be necessary when the external definition has different scope. |
| Instruction incompatibility | Two procedures prescribe mutually exclusive commands, orderings, prerequisites, flags, or approval requirements for the same task and environment. | The local one-review/two-review case is direct repository evidence. RFC 2119/8174 also shows why changing requirement level is semantic, not stylistic: MUST, SHOULD, and MAY have different defined force ([BCP 14](https://www.rfc-editor.org/info/bcp14/)). |
| Normative-authority drift | Explanatory text, examples, generated views, or old decisions are treated as co-equal with the governing specification; recommendations silently become obligations or vice versa. | W3C guidance requires normative and informative material to be distinguishable and treats figures, examples, and notes as informative ([W3C Manual of Style](https://www.w3.org/guide/manual-of-style/)). Markers help only if retrieval and readers preserve them. |
| Temporal or variant collision | Individually correct claims for different releases, products, branches, locales, or environments are presented without qualifiers and appear contradictory. | GitHub Docs uses version metadata and conditional text in one source so readers can select the applicable product version ([GitHub Docs](https://docs.github.com/en/contributing/writing-for-github-docs/versioning-documentation)). Conditional systems can themselves be misconfigured or leave unsupported combinations. |
| Projection divergence | A summary, index, runbook, diagram, generated page, or copied fragment ceases to match the canonical representation it projects. | DITA content references provide inclusion-by-reference and validate the result in its new context ([OASIS DITA 1.3](https://docs.oasis-open.org/dita/dita/v1.3/os/part3-all-inclusive/archSpec/base/conref.html)). Reuse reduces independent copies but does not validate the source's truth. |
| Cross-view model inconsistency | Architecture, data-flow, deployment, security, and operational views use incompatible entities or relationships, so different readers construct different models of the same system. | ISO/IEC/IEEE 42010 distinguishes an entity's architecture from the descriptions and viewpoints that express it and specifies common concepts for their relationships ([ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html)). The link from contradictory views to divergent reader models is a reasoned interpretation, not directly measured here. |
| Latent conflict masked by agreement | A detector or agent finds supporting text and stops although contradictory text exists elsewhere; repeated similar phrasing creates an appearance of coherence. | WIKICOLLIDE formalizes why a supporting item is insufficient: consistency requires finding no contradiction across the corpus, an exhaustive condition that is infeasible at scale ([Semnani et al., 2025](https://aclanthology.org/2025.emnlp-main.1765/)). |
| Edit collateral damage | A requested local change alters, deletes, or semantically weakens unrelated content, leaving other corpus elements inconsistent with the changed artifact. | DELEGATE-52 observed sparse but severe degradation that compounded over 20 interactions ([Laban et al., 2026](https://arxiv.org/abs/2604.15597)). Its round-trip artifacts are broader than technical documentation, so this class's corpus prevalence is unknown. |

## Causes and mechanisms

### 1. Local edits do not carry a corpus transaction boundary

A documentation request usually names a page or section, while the invariant lives across
several artifacts: a term in a glossary, a number in a runbook, a decision in an ADR, and a
diagram node. If the agent searches only the named file or accepts the first supporting
passage, it has no representation of the full update set. Semnani et al.'s distinction is
important: ordinary verification can stop after one support or refutation, whereas
corpus-level consistency must continue looking for any refutation anywhere
([Semnani et al., 2025](https://aclanthology.org/2025.emnlp-main.1765/)).

This mechanism does not require an LLM. Human editors also miss distant dependencies. The
agent-specific risk is scale and speed: an agent can make more individually fluent edits
before a human observes the accumulated state. The ICSE practitioner survey found that 59%
considered code/document inconsistency important and identified it as a recurring issue,
while warning that the 146-person sample was concentrated in one multinational
([Aghajani et al., 2020, pp. 6 and 9](https://emadpres.github.io/pdfs/icse2020.pdf)).

### 2. Available context is not equivalent to used context

Giving an agent the entire corpus does not prove that it will use every relevant claim.
On multi-document question answering and key-value retrieval, Liu et al. found that model
performance varied with the position of relevant information and often declined when it
appeared in the middle of a long context
([Liu et al., 2024](https://aclanthology.org/2024.tacl-1.9/)). DELEGATE-52 independently
found worse fidelity with larger artifacts and distractor context. These are adjacent tasks,
not direct documentation-authoring experiments, so applying them to corpus edits is a
moderate-confidence inference.

Retrieval can reduce input size but creates another selection boundary. A synonym may not
retrieve its preferred term; a changed product name may split an entity into two clusters;
and a stale high-ranking page can displace the governing source. In effect, terminology
drift makes the retrieval problem that might otherwise detect it harder.

### 3. Sequential generation turns small state errors into future context

Repeated edits do not start from the original corpus; they start from the last edited
state. DELEGATE-52's reversible edit chains make this cumulative property directly
measurable in a controlled setting: short-run performance did not predict 20-interaction
performance, and every tested model degraded over the interaction horizon
([Laban et al., 2026](https://arxiv.org/abs/2604.15597)). DocOps, a separate 2026 preprint,
reports long-term state-tracking collapse, shallow semantic verification, and destructive
structural edits in complex document operations
([Jiang et al., 2026](https://arxiv.org/abs/2607.19865)).

The counterevidence matters. DELEGATE-52 found Python far more robust than most domains,
and its authors report less than 1% average degradation there. They also state that their
simplified agent harness does not represent production-grade, domain-optimized systems and
that verification and human oversight can mitigate failures
([authors' limitations note, 2026-05-15](https://www.microsoft.com/en-us/research/blog/further-notes-on-our-recent-research-on-ai-delegation-and-long-horizon-reliability/)).
The evidence therefore supports a risk mechanism, not a universal corruption rate.

### 4. Linguistic variation changes concept boundaries and normative force

Generative editing is optimized for plausible language, so paraphrase is natural. In
ordinary prose, variation can improve readability. In a technical corpus, however,
substituting “workspace,” “project,” and “repository,” or “must,” “should,” and “can,” can
change the entity or obligation. NIST includes outputs that contradict prior statements
under confabulation and notes special risk for long-form, highly contextual work
([NIST AI 600-1, section 2.2, 2024](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)).
ISO's concept-oriented terminology model and BCP 14's defined requirement levels show why
surface fluency is not a substitute for stable semantics.

### 5. Duplication multiplies independent maintenance sites

Copied prose is initially consistent by construction but becomes independent after the
copy. Each later edit can update one instance, update different instances in incompatible
ways, or fail to identify all of them. GitHub Docs explicitly uses single-source versioning
to avoid repetition, and DITA provides content references for reuse. These authoritative
designs support the maintenance rationale, but neither is a randomized comparison of drift
rates.

Single-sourcing is also not an unconditional cure. If the canonical content is wrong, reuse
distributes the same error everywhere. If variants genuinely require different scope or
audience treatment, excessive reuse can erase important distinctions. The goal is one
maintained representation per invariant, not one prose paragraph for every context.

### 6. Different documents legitimately select different views

An operator runbook, architecture overview, API reference, and newcomer guide should not
contain identical detail. Divergence becomes a defect when they disagree on shared entities,
relationships, or invariants rather than merely select different concerns. ISO/IEC/IEEE
42010's separation of architecture, architecture description, viewpoints, and model kinds
supports this distinction. I infer that unlinked or inconsistent views form divergent mental
models because readers infer the system from different subsets; the sources here do not
measure readers' internal representations directly.

## Detection and validation

### Lexical and terminology checks

A controlled vocabulary can flag deprecated aliases, capitalization variants, acronym
expansions, and forbidden ambiguous terms. Vale demonstrates a substitution rule that can
fail CI and describes its focus as consistency across authors, not general correctness
([Vale documentation](https://docs.vale.sh/)). This boundary is essential: a corpus can use
one preferred term consistently and still define the concept incorrectly, or use two
legitimate terms in different domains and trigger a false positive.

More useful terminology checks bind a term to a concept identifier, definition, subject
field, allowed aliases, and lifecycle status. ISO 704 provides the conceptual basis. A
reviewer should inspect one-to-many and many-to-one mappings: several terms for one concept
and one term for several concepts.

### Structural and referential checks

Schemas, parsers, link checkers, duplicate-ID checks, and relationship-target checks are
deterministic and cheap. They establish that documents can be loaded and references resolve.
The local validator is an example of an explicitly bounded structural gate. These checks
cannot decide whether two valid nodes contradict, whether a citation supports the claim, or
whether a relationship is semantically correct unless that invariant has been encoded.

Reusable content and generated projections make some consistency properties structural:
instead of checking whether two copies match, build both views from the same value. DITA
adds context-validity checks when content references resolve. This still cannot tell whether
the reused claim is current, authoritative, or appropriate for the reader.

### Executable and source-of-truth checks

For commands, schemas, defaults, API signatures, and configuration, execute examples or
compare extracted facts with the authoritative artifact. A documentation change that alters
a command can run that command in a safe fixture; a documented enum can be generated from
the schema; a default can be asserted from configuration. These tests provide strong
evidence only for the exact environment, version, and path exercised. They do not validate
intent, explanatory prose, untested branches, or whether the chosen source is itself
authoritative.

### Semantic contradiction checks

A scalable pipeline can extract bounded claims, normalize entities and units, retrieve
potentially related claims, then apply rules or natural-language inference (NLI) to candidate
pairs. It should report the source passages, scope, version, and confidence for human
resolution rather than silently rewrite one side.

The evidence argues against treating such a pipeline as proof:

- ContraDoc found that GPT-4 was strongest among four tested model families and could
  outperform humans on its benchmark, yet remained unreliable on nuanced,
  context-dependent contradictions
  ([Li, Raheja, and Kumar, 2024](https://aclanthology.org/2024.naacl-long.362/)).
- SummaC found that sentence-trained NLI had a granularity mismatch with document-level
  inconsistency; its segmented aggregation reached 74.4% balanced accuracy, not perfect
  detection ([Laban et al., 2022](https://aclanthology.org/2022.tacl-1.10/)).
- On WIKICOLLIDE, the best fully automated corpus-level system reached 75.1% AUROC. The
  authors treat inconsistent labels backed by a found contradiction as gold but only call
  consistent labels strong verification because exhaustive absence is infeasible
  ([Semnani et al., 2025](https://aclanthology.org/2025.emnlp-main.1765/)).

These results are not directly comparable because the tasks, metrics, corpora, and model
dates differ. Together they establish a detection ceiling: candidate ranking is useful, but
an automated “no conflicts” verdict is not justified by these studies.

### Change-impact and temporal checks

Before merging an edit, search by concept ID, preferred term, aliases, identifiers, quoted
numbers, requirement IDs, and inbound links. Compare every affected claim on a matrix of
product, release, environment, branch, audience, and authority. A difference becomes a
contradiction only when those dimensions overlap.

Run this analysis on the resulting corpus state, not just the changed lines. A clean patch
can preserve an existing conflict; a correct local replacement can create a new conflict in
an untouched file. Historical snapshots are useful for reproducibility but should not be
mixed with current instructions without visible version labels.

### Human task and model review

Give reviewers concrete reader tasks: follow the installation path from each entry point,
explain ownership from the architecture and runbook, or state the required approval from the
policy and README. Compare the actions and models they derive. This detects pragmatic
incompatibility that sentence-pair NLI misses.

Human review is not automatically exhaustive. Semnani et al.'s eight-editor study found
participants identified 64.7% more inconsistencies per hour with the CLAIRE assistant than
without it, suggesting machine retrieval can complement expert verification. The sample is
small, Wikipedia-specific, and measured assisted discovery, not technical-doc review.

## Mitigations

### Establish authority, scope, and revision before editing

Maintain a machine-readable map from claim type to governing artifact: for example,
configuration for runtime defaults, an accepted decision for rationale, and a named policy
for obligations. Mark projections and examples as informative. Record product, release,
environment, audience, status, and verification date beside mutable claims. When sources
with the same authority conflict, preserve and escalate the conflict rather than blending
them into a plausible compromise.

Trade-off: authority metadata adds maintenance work and can become stale. It must itself be
validated, and authority does not make a false source true.

### Manage concepts, not only words

Use a concept register with a stable identifier, concise definition, preferred term,
allowed aliases, domain, owner, and deprecated/replaced relationships. Agents should resolve
mentions to concepts before rewriting and should preserve interface terms verbatim when
they refer to code or UI labels. Google explicitly cautions that word-for-word replacement
can be technically inaccurate and advises matching terms to context
([Google word list](https://developers.google.com/style/word-list)).

Trade-off: a global vocabulary can flatten legitimate domain distinctions. Local scopes and
explicit aliases are safer than banning every synonym.

### Reduce independent copies of volatile facts

Generate tables, version strings, default values, API signatures, and repeated warnings from
authoritative structured data. Use references or transclusion for wording that truly must be
identical. GitHub Docs' single-source conditional versioning and DITA's content references
are implementation examples.

Trade-off: reuse increases coupling, can make source text harder to read, and propagates a
bad canonical value broadly. Prefer reuse for invariants and volatile facts, not for all
explanation.

### Treat an edit as a claim-set change

Require an agent to return both the patch and an impact set: concepts changed, claims added
or removed, authorities consulted, variants affected, searches performed, and checks not
run. Re-query the repository after editing to find old terms and values. Use small patches
and compare untouched regions so collateral changes are visible.

This is a recommendation inferred from the evidence, not an evaluated guarantee.
DELEGATE-52 found that a basic agentic tool harness did not remove degradation, so merely
adding tools is insufficient; the tools need domain-specific invariants and enforced
validation.

### Layer deterministic, semantic, and human gates

Run cheap deterministic gates on every change, semantic candidate detection on the affected
claim neighborhood, executable tests where possible, and targeted human review for authority,
scope, exceptions, and reader consequences. Keep machine findings inspectable and require
the conflicting passages rather than a bare score.

Trade-off: broader semantic comparison costs more and raises false positives. Risk-based
selection is necessary, but sampling cannot prove absence of rare conflicts.

### Evaluate long horizons and real workflows

Test an agent over a sequence of realistic corpus changes, not only isolated prompts.
Seed known conflicts and terminology variants, measure preservation of untouched claims,
and rerun actual reader tasks after multiple edits. Stratify results by document size,
domain, model/version, tool harness, and human intervention. Short-horizon success should
not be extrapolated because DELEGATE-52 found it was not predictive of 20-interaction
performance.

## Limits and open questions

- **Directness:** No source located measures repeated LLM edits to a version-controlled,
  multi-file technical-documentation corpus over its real maintenance history. The central
  explanation remains a moderate-confidence synthesis.
- **Prevalence:** The studies cannot estimate how often contradictory claims, term drift,
  incompatible instructions, or divergent mental models occur in production agent-authored
  corpora.
- **Causation:** The local contradiction is not attributed to an agent. Human maintenance,
  organizational ownership, release pressure, and concurrent branches can produce the same
  observable state.
- **Benchmark fit:** DELEGATE-52 is a controlled stress test with reversible edits and
  limited human intervention. Its percentage degradation should not be transferred to a
  docs-as-code workflow. DocOps is also a recent preprint.
- **Model currency:** Model and agent capabilities change quickly. Findings tied to 2023–26
  model versions and harnesses require re-evaluation before product decisions.
- **Language and culture:** Most cited model evaluations and all local inspection are
  English-language. Terminology behavior across translations and multilingual corpora is
  not established here.
- **Semantic ground truth:** Some conflicts have no purely textual resolution. Sources may
  differ because reality changed, authorities disagree, or a policy decision is still open.
- **Mental models:** Divergent reader mental models are analytically plausible and grounded
  in the role of architecture descriptions, but were not directly measured by the cited
  studies.
- **False positives:** Exact-term enforcement can reject helpful audience-specific language;
  semantic detectors can confuse exceptions, negation, temporal qualifiers, and distinct
  entities.
- **False negatives:** Proving a corpus consistent is generally infeasible. Retrieval can
  miss the contradictory passage, and a detector can agree with whichever subset it sees.
- **Reuse counter-risk:** A canonical source reduces divergence but can create consistent
  wrongness everywhere. Independent reality checks remain necessary.
- **Open evaluation question:** A useful benchmark would combine real repository history,
  seeded and naturally occurring conflicts, explicit authority/version metadata, actual
  agent patches, and task-based human outcomes over many revisions. No such benchmark was
  located.

## Practical review checks

- Candidate check: state the governing source, scope, product/release/environment, and
  verification date for every changed mutable claim.
- Candidate check: search the corpus for the old value, new value, preferred term, aliases,
  identifiers, and likely paraphrases before and after editing.
- Candidate check: distinguish a legitimate variant from a contradiction by comparing time,
  audience, environment, authority, and subject before raising a conflict.
- Candidate check: map every term change to a concept definition; flag one term mapped to
  multiple concepts and one concept with undeclared competing terms.
- Candidate check: compare requirement force explicitly; treat changes among MUST, SHOULD,
  MAY, required, recommended, and optional as semantic changes.
- Candidate check: identify all summaries, indexes, diagrams, runbooks, generated pages, and
  reused fragments that project the changed claim.
- Candidate check: prefer generation or reference for repeated volatile facts, then verify
  that the canonical source is correct and that each inclusion context remains valid.
- Candidate check: run schemas, parsers, link checks, terminology lint, executable examples,
  and domain assertions, recording exactly what each check does not prove.
- Candidate check: feed semantic detectors the candidate passages plus authority, version,
  entity, and temporal context; never accept a bare consistency score as resolution.
- Candidate check: require the agent's impact set and inspect unexpected edits or deletions
  outside the requested claim set.
- Candidate check: review the resulting whole-corpus state and at least one real reader task,
  not only the changed file or a fluent diff.
- Candidate check: repeat evaluation across a sequence of edits and preserve untouched-claim
  checks; do not infer long-horizon safety from one successful edit.
- Candidate check: if authoritative sources genuinely conflict, retain both with visible
  status and escalate; do not synthesize a compromise without a deciding authority.

## References

- [LLMs Corrupt Your Documents When You Delegate](https://arxiv.org/abs/2604.15597) —
  Laban, Schnabel, and Neville, arXiv:2604.15597, 2026-04-17; DELEGATE-52 method,
  repeated-edit degradation, long-horizon and distractor findings. Preprint.
- [Further Notes on Our Recent Research on AI Delegation and Long-Horizon Reliability](https://www.microsoft.com/en-us/research/blog/further-notes-on-our-recent-research-on-ai-delegation-and-long-horizon-reliability/) —
  Laban, Schnabel, and Neville, Microsoft Research, 2026-05-15; benchmark scope,
  Python counterexample, production-system and human-oversight limitations.
- [DocOps: A Verifiable Benchmark for Autonomous Agents in Complex Document Operations](https://arxiv.org/abs/2607.19865) —
  Jiang et al., arXiv:2607.19865, 2026-07-22; global-state, semantic-verification,
  and structural-edit failure modes. Preprint.
- [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/) —
  Liu et al., TACL 12, 2024, pp. 157–173; position-dependent use of relevant
  information in long and multi-document contexts.
- [Detecting Corpus-Level Knowledge Inconsistencies in Wikipedia with Large Language Models](https://aclanthology.org/2025.emnlp-main.1765/) —
  Semnani et al., EMNLP 2025, pp. 34839–34866; CLID formulation, WIKICOLLIDE,
  human-in-the-loop results, automated-detection ceiling, and absence-proof limit.
- [ContraDoc: Understanding Self-Contradictions in Documents with Large Language Models](https://aclanthology.org/2024.naacl-long.362/) —
  Li, Raheja, and Kumar, NAACL 2024, pp. 6509–6523; long-document contradiction
  dataset and nuance/context limitations of tested LLMs.
- [SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization](https://aclanthology.org/2022.tacl-1.10/) —
  Laban et al., TACL 10, 2022, pp. 163–177; granularity mismatch and bounded
  performance of NLI-based consistency detection.
- [Software Documentation: The Practitioners' Perspective](https://emadpres.github.io/pdfs/icse2020.pdf) —
  Aghajani et al., ICSE 2020, pp. 590–601; surveys of 146 practitioners on
  documentation inconsistency, maintenance, and study validity limits.
- [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) —
  NIST AI 600-1, July 2024, section 2.2; confabulation across outputs and contexts.
- [ISO 704:2022, Terminology work — Principles and methods](https://www.iso.org/standard/79077.html) —
  ISO, edition 4, 2022-07; relationships among objects, concepts, definitions,
  and designations. Only the public abstract was accessible.
- [Write for a global audience](https://developers.google.com/style/translation) —
  Google developer documentation style guide, updated 2026-08-25; stable term use,
  ambiguity, and translation effects.
- [Google developer documentation word list](https://developers.google.com/style/word-list) —
  Google, accessed 2026-09-09; preferred terms, contextual exceptions, and the
  risk of mechanically replacing technical vocabulary.
- [BCP 14: Requirement-level key words](https://www.rfc-editor.org/info/bcp14/) —
  IETF/RFC Editor, RFC 2119 (1997) as updated by RFC 8174 (2017); distinct
  normative force of MUST, SHOULD, and MAY.
- [W3C Manual of Style](https://www.w3.org/guide/manual-of-style/) — W3C,
  accessed 2026-09-09; normative/informative separation and reuse of defined terms.
- [ISO/IEC/IEEE 42010:2022, Architecture description](https://www.iso.org/standard/74393.html) —
  ISO/IEC/IEEE, edition 2, 2022-11; architecture descriptions, viewpoints, model
  kinds, and their conceptual relationships. Only the public abstract was accessible.
- [Content reference (conref)](https://docs.oasis-open.org/dita/dita/v1.3/os/part3-all-inclusive/archSpec/base/conref.html) —
  OASIS DITA 1.3, 2015-12-17; reuse and context-validity rules for referenced content.
- [Versioning documentation](https://docs.github.com/en/contributing/writing-for-github-docs/versioning-documentation) —
  GitHub Docs, accessed 2026-09-09; single-source, scoped product and release variants.
- [Vale documentation](https://docs.vale.sh/) — Vale, accessed 2026-09-09;
  cross-author consistency and terminology substitutions, explicitly not general correctness.
- [Launchpad README](../../../README.md#opening-a-pr) and
  [normative AGENTS.md](../../../AGENTS.md#6-branch-commit-pr) —
  launchpad-26/buzz revision `81b5a1d059ea897968c4fe412497a351892d4598`,
  inspected 2026-09-09; bounded local authority hierarchy and approval-count conflict.
- [Launchpad corpus validator](../../../project-intelligence/corpus/validate.py) —
  launchpad-26/buzz, same revision and inspection date; direct evidence of the local
  deterministic validator's structural remit and semantic boundary.
