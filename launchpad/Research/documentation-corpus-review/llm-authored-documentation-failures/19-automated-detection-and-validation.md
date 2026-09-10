# Automated detection and validation

| Metadata | Value |
|---|---|
| Topic number | 19 |
| Exact research question | Which failure classes can be detected reliably through schemas, repository analysis, executable examples, claim-evidence checks, consistency analysis, static validation, or model-assisted review—and which still require human judgment? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Automated and semi-automated validation of agent-authored technical documentation stored with software repositories. Covered artifacts include Markdown, structured metadata, cross-references, API/configuration reference, commands and code examples, behavioral claims, citations, terminology, and multi-document consistency. “Reliable” means a check has a bounded machine-verifiable predicate and reports its scope, not that it proves overall document quality. |
| Evidence limitations | Tool accuracy is highly dependent on language, schema, environment, dataset, model, and defect distribution. Published semantic-detector results are mostly benchmark results, not production documentation guarantees. No located study compares all listed validation families over one representative LLM-authored technical-doc corpus; the allocation of checks is therefore partly a formal analysis of what each predicate can prove. |

## Executive answer

Automation is reliable when documentation quality can be reduced to an explicit,
reproducible predicate over available evidence. Parsers and schemas can establish that
required fields exist and values have permitted shapes. Repository analysis can establish
that a path, symbol, flag, or link resolves at a named revision. Documentation tests can
establish that extracted examples compile or execute and satisfy encoded assertions in a
specified environment. Generated-reference comparison can establish that every item in a
declared API or configuration inventory is represented.

None of those results establishes that the prose is true, complete, safe, useful, or
authoritative outside the encoded boundary. Rust's official documentation states that
`rustdoc` extracts and runs examples to keep them working, but it also supports `no_run`,
`ignore`, preprocessing, and target-specific behavior; a compiling example need not prove
an operational procedure or its security
([rustdoc documentation tests](https://doc.rust-lang.org/rustdoc/documentation-tests.html)).
Likewise, JSON Schema separates core structure from validation keywords, but a schema only
validates constraints its author expressed
([JSON Schema specification](https://json-schema.org/specification)).

Semantic automation is useful but less conclusive. Code-comment inconsistency models,
natural-language inference, citation entailment, contradiction search, and LLM judges can
prioritize review. DocChecker reported 72.3% accuracy on its evaluated inconsistency task,
which is evidence of signal and simultaneously evidence against treating it as a complete
gate
([Dau et al., 2023](https://arxiv.org/abs/2306.06347)). Cross-dataset research on
factuality detectors finds performance varies by error type, source dataset, and generator
([Tang et al., ACL 2023](https://aclanthology.org/2023.acl-long.650/)). LLM judges add
position, verbosity, self-preference, and reasoning biases in evaluated settings
([Zheng et al., 2023](https://arxiv.org/abs/2306.05685)).

The defensible architecture is a **portfolio of scoped claims**. Use deterministic gates
for structure, resolution, policy patterns, and executable invariants; use semantic tools
as calibrated detectors with thresholds, abstention, counterfactual tests, and human-
labeled evaluations; then require human judgment for authority, intent, audience/task
fitness, material omissions, trade-offs, acceptable risk, and conflicts the evidence
cannot decide. Every pass must name its revision, inputs, environment, exclusions,
timeouts, and unverified classes. A green aggregate must never imply “documentation is
correct.”

## Question, scope, and method

### Subquestions

- What exact predicates can schemas, repository analysis, and static checks decide?
- Which parts of procedures and examples can execution validate, and what remains outside
  the test oracle?
- How well do semantic code-document, factuality, consistency, and model-assisted checks
  generalize beyond their benchmarks?
- How should false positives, false negatives, abstention, and incomplete analysis be
  reported?
- Which documentation decisions inherently require contextual human judgment?

### Exclusions

- Selection or endorsement of a particular commercial documentation platform.
- A complete implementation plan for this repository.
- Security penetration testing or execution of destructive examples.
- Treating human review as error-free or model review as inherently invalid.
- Program-wide synthesis or adoption of quality gates.

### Evidence and source plan

Local evidence was inspected on branch `docs/llm-research-program` at commit
`c38691ec4`. The corpus validator explicitly distinguishes hard errors from an
`UNVERIFIED` channel for evidence it recognizes but cannot open offline, and its module
documentation enumerates schema, relationship, citation, and canonical-location scope
([local validator](../../../project-intelligence/corpus/validate.py)). This is direct
evidence of one implementation's contract, not proof of its defect-detection performance
or applicability to these research reports.

External sources were selected for formal specifications, official executable-document
behavior, empirical code-comment detection, cross-domain factuality meta-evaluation, and
LLM-judge limitations. A working ledger recorded each method's predicate, oracle, input
coverage, false-positive/negative routes, and unsupported claims. Searches sought negative
and out-of-domain results rather than vendor accuracy claims. Saturation was reached when
each requested validation family had a bounded “can establish / cannot establish” answer
and remaining searches repeated tools without stronger validity evidence.

## Failure taxonomy

| Failure class | Best automated treatment | Reliability boundary |
|---|---|---|
| Parse and schema defects | Deterministic parser and versioned schema gate. | High for supplied valid inputs and encoded constraints; cannot detect semantically wrong valid values or a defective schema. |
| Broken internal links and anchors | Resolve against the built artifact at a named revision. | High for local resolvability; external availability, link meaning, and future persistence remain open. |
| Missing declared symbols/fields | Compare documentation inventory with compiler, schema, CLI help, or generated metadata. | High when the authoritative universe is machine-enumerable; hidden, dynamic, deprecated, or intentionally undocumented surfaces need policy. |
| Stale names/signatures/defaults | AST/schema diff and generated reference checks. | Strong for syntactic facts represented in the source; runtime defaults and contextual behavior may not be statically visible. |
| Non-executable examples | Extract, compile, run, and assert output in a pinned sandbox. | Strong only for exercised path, environment, fixtures, permissions, and oracle; skipped, destructive, networked, timing, and negative paths remain. |
| Prohibited strings/secrets/style | Pattern and entropy scanners, linters, terminology rules. | Reliable for known patterns; paraphrase, unknown formats, contextual PII, meaning, and intentional exceptions create misses and noise. |
| Code-comment inconsistency | Static heuristics and learned code-text classifiers. | Useful triage; DocChecker's bounded benchmark accuracy and dataset construction do not justify an unconditional correctness gate. |
| Unsupported citations | Link resolution plus claim-source entailment and provenance analysis. | Can flag absent or weak support; source authority, applicability, circularity, and implicit reasoning need judgment. |
| Cross-document contradictions | Exact-value extraction, rule engines, temporal graphs, NLI/LLM comparison. | Deterministic for formalized claims; semantic detectors struggle with scope, modality, versions, legitimate perspectives, and long-range context. |
| Hallucinated or misleading prose | Source-grounded factuality checks and model-assisted critique. | Recall and calibration vary across error types and domains; a second model can share the first model's blind spots. |
| Omission and false completeness | Compare against an independent requirements/task/risk inventory; mutation or seeded-gap tests. | Can find missing declared items, never all unknown obligations. |
| Reader/task unfitness | Search tests, usability tasks, comprehension and task-success observation. | Instrumentation can measure specified outcomes; audience needs, acceptable explanation, and value judgments remain human/contextual. |
| Normative or risk decisions | Rule extraction can compare defined modal terms and authorities. | Whether a requirement should exist, an exception is justified, or residual risk is acceptable requires accountable authority. |

## Causes and mechanisms

### Validators prove predicates, not documents

If a validator checks “every node has an `id`,” a pass proves that predicate over files it
actually loaded. It does not prove unique meaning, factual support, or complete discovery.
Failures occur when teams omit the predicate, choose the wrong oracle, skip inputs, swallow
errors, or promote a local pass to an overall assurance claim.

### Executability depends on environment and oracle

A command can exit zero while producing the wrong state. A code block can compile while
using unsafe defaults. An example can pass with a mock but fail against a real service.
Useful execution therefore records environment, versions, fixtures, privileges, network,
side effects, assertions, cleanup, and skipped blocks. Negative and failure paths need
explicit oracles; “did not crash” is rarely enough.

### Semantic detection is distribution-sensitive

Learned evaluators encode their training labels, synthetic corruptions, source genre, and
model family. Tang et al. compared factual-error detectors across nine annotated datasets
and found performance differences by summarizer and error type. Tam et al. found LLMs
usually preferred consistent summaries in their benchmark, yet preferred an inconsistent
summary when that text appeared verbatim in the source—an important copy/entailment
failure mode
([Tam et al., Findings of ACL 2023](https://aclanthology.org/2023.findings-acl.322/)).

### Model judges are correlated reviewers

An LLM critique can cheaply spot contradictions, ambiguity, missing prerequisites, and
unsupported transitions. It can also be biased toward verbosity, order, familiar style,
or its own generation family and may rationalize a false conclusion. Rephrasing, swapping
order, hiding authorship, using independent models, and checking against gold labels can
measure some instability; none converts subjective judgment into formal verification.

### Human judgment supplies goals and authority

Automation can test a specified reader task, but humans decide which readers and tasks
matter. It can show two requirements conflict, but an accountable owner decides which
authority, version, or risk treatment governs. This is not a celebration of intuition:
the human decision should cite evidence and be auditable, and deterministic checks should
remove avoidable cognitive load first.

## Detection and validation

### A reliability ladder

1. **Level A — formal and reproducible:** parsing, schemas, exact reference resolution,
   enumerated inventory comparison, cryptographic integrity, and deterministic policy
   rules. Gate when inputs and failure behavior are complete and explicit.
2. **Level B — executable under bounded conditions:** compilation, doctests, command
   execution, generated-output comparison, and scenario tests. Gate only for the named
   environment and assertions; report skips and unavailable dependencies.
3. **Level C — empirically calibrated detectors:** secret/PII scanners, code-text models,
   NLI, contradiction search, and factuality classifiers. Evaluate precision, recall,
   calibration, and subgroup performance on representative labeled defects; support
   abstention and human triage.
4. **Level D — assistive judgment:** LLM critique, rubric scoring, style analysis, and
   open-ended gap suggestions. Use for prioritization and hypothesis generation; do not
   call it verification without an external oracle.
5. **Level E — accountable human decision:** audience, authority, materiality, acceptable
   uncertainty, trade-offs, harm, and unknown omissions. Record reviewer role, evidence,
   decision, and unresolved risk.

### Required result envelope

Each automated result should record tool/version, configuration, input discovery rule,
revision, environment, start/end status, timeout or truncation, passed/failed/skipped
counts, findings, and the proposition a pass supports. False-positive suppressions should
be scoped and owned. Incomplete analysis must fail closed for a blocking claim or be shown
as a separate unresolved status—not silently converted to green.

### Validity evaluation

For learned or heuristic checks, construct representative labeled cases from actual
documentation genres and defect classes. Preserve a held-out set; include hard negatives,
paraphrases, version conflicts, legitimate terminology variants, and adversarial examples.
Report precision and recall by class and consequence rather than one accuracy score. Re-run
after changes to model, prompt, repository, schema, or authoring process.

## Mitigations

- Generate machine-defined reference directly from authoritative schemas or compiler
  metadata where possible; reserve prose for semantics and use cases the generator cannot
  infer.
- Treat schemas, link checks, and linters as mandatory narrow gates, with explicit file
  discovery and failure-on-timeout behavior.
- Extract examples into executable tests or include tested source into documentation so
  prose and test do not fork; pin safe environments and assert effects, not only exit code.
- Maintain a claim/evidence representation for consequential assertions, including source
  revision, authority, scope, and inference. Apply semantic checks as flags until locally
  calibrated.
- Run cross-document checks over normalized identifiers, versions, modality, defaults,
  units, and state transitions before open-ended semantic comparison.
- Use diverse model-assisted review for discovery, counterevidence, and perturbation—not
  as self-certification. Compare with human-labeled cases and expose disagreement.
- Route findings by consequence and detector confidence. High-impact uncertainty should
  block or require accountable adjudication; low-impact style noise should not bury it.
- Publish validation as a matrix of scoped results and unknowns rather than a single badge
  or corpus score.

## Limits and open questions

- Formal checks can be highly reliable while the formalization is incomplete. The schema
  author and file-discovery logic are part of the trusted computing base.
- Execution may be unsafe, costly, flaky, or impossible for production procedures. Static
  review and simulation remain necessary, but weaker evidence must be labeled.
- Benchmark accuracy does not provide a production error bound without representative
  prevalence, labels, thresholds, and drift monitoring.
- Human labels can disagree or encode organizational assumptions. Inter-rater agreement
  and adjudication records improve transparency but do not create objective truth.
- LLM judges can add valuable recall and scale. Their biases justify calibration and an
  external oracle, not blanket rejection.
- Strong automated checks may change author behavior toward what the tool measures,
  leaving unencoded qualities neglected.
- Open questions include realistic benchmark corpora for mixed documentation genres,
  mutation operators that model agent-specific errors, semantic checker calibration under
  version drift, and safe execution of privileged runbooks.

## Practical review checks

- Candidate check: require every validator to state its exact pass proposition and
  enumerate discovered, excluded, skipped, timed-out, and unverified inputs.
- Candidate check: fail a blocking gate on parser errors, incomplete analysis, or missing
  environment rather than converting them to zero findings.
- Candidate check: compare schema and generated-reference coverage against an independently
  selected authoritative inventory.
- Candidate check: compile and run safe examples in pinned environments with assertions on
  output and side effects; record `ignore` and `no_run` cases separately.
- Candidate check: evaluate learned detectors on held-out representative defects and hard
  negatives; report precision/recall by failure class and consequence.
- Candidate check: swap order, paraphrase inputs, remove author labels, and compare models
  before trusting an LLM-judge finding.
- Candidate check: require human adjudication for authority conflicts, material omissions,
  reader-task value, policy exceptions, and residual risk.
- Candidate check: do not collapse deterministic passes, semantic flags, and human
  decisions into one “quality” percentage.
- Candidate check: version validation evidence with the document and rerun it when source,
  dependencies, prompts, models, or schemas change.

## References

- [JSON Schema specification](https://json-schema.org/specification) — JSON Schema project, current specification index accessed 2026-09-09; separation of core and validation vocabularies for structural constraints.
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) — OpenAPI Initiative, latest published specification accessed 2026-09-09; machine-readable API description and schema contract.
- [Documentation tests](https://doc.rust-lang.org/rustdoc/documentation-tests.html) — Rust project, rustdoc book accessed 2026-09-09; extraction, compilation/execution, assertions, preprocessing, `no_run`, and `ignore` boundaries.
- [DocChecker: Bootstrapping Code Large Language Model for Detecting and Resolving Code-Comment Inconsistencies](https://arxiv.org/abs/2306.06347) — Dau, Guo, and Bui, 2023; evaluated learned inconsistency detection and its bounded accuracy.
- [Understanding Factual Errors in Summarization: Errors, Summarizers, Datasets, Error Detectors](https://aclanthology.org/2023.acl-long.650/) — Tang et al., ACL 2023; cross-dataset and error-type variation in factuality-detector performance.
- [Evaluating the Factual Consistency of Large Language Models Through News Summarization](https://aclanthology.org/2023.findings-acl.322/) — Tam et al., Findings of ACL 2023; FIB evaluation and verbatim-inconsistent-text boundary.
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) — Zheng et al., NeurIPS Datasets and Benchmarks 2023; agreement and identified position, verbosity, and self-enhancement limitations.
- [A Meta-Evaluation of Faithfulness Metrics for Long-Form Hospital-Course Summarization](https://proceedings.mlr.press/v219/adams23a.html) — Adams, Zucker, and Elhadad, MLHC 2023; domain-specific meta-evaluation and faithfulness-metric boundaries.
- [Verifying the consistency of web-based technical documentations](https://doi.org/10.1016/j.jvlc.2010.11.003) — Chouali et al., *Journal of Visual Languages & Computing*, 2011; formalized criteria, model checking, counterexamples, and technical-documentation case study.
- [Local corpus validator](../../../project-intelligence/corpus/validate.py) — launchpad-26/buzz revision `c38691ec4`, inspected 2026-09-09; direct evidence of bounded structural checks and a separate unverified channel.
