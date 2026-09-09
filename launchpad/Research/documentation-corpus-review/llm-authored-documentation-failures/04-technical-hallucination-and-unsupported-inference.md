# Technical hallucination and unsupported inference

| Metadata | Value |
|---|---|
| Topic number | 04 |
| Exact research question | What kinds of technical facts do documentation agents invent or infer without sufficient support, why do these failures occur, and which verification methods detect them? |
| Primary model | Codex |
| Research date | 2026-09-08 |
| Scope | English-language documentation generated from source code, repository files, API documentation, specifications, package registries, tests, and tool or runtime output. The evidence covers general-purpose and code-oriented LLMs reported from 2020 through 2025, with direct documentation evidence concentrated in Java method comments and code summaries. Security disclosure, citation fabrication, temporal coherence, omission, and normative distortion are considered only where they bound unsupported technical inference. |
| Evidence limitations | Direct empirical research on autonomous agents writing repository-scale manuals, architecture documents, and runbooks is sparse. The strongest documentation-specific studies use Java methods or code snippets; API and package studies evaluate generated code rather than prose. Their failure mechanisms transfer plausibly to technical documentation, but prevalence figures do not. Closed-model versions, unknown training data, synthetic benchmark prompts, and fast-moving toolchains further limit generalization. |

## Executive answer

Documentation agents invent technical facts in two importantly different ways. They
make **contradictory claims**, such as reversing a condition or stating the wrong
return/exception behavior, and **unsupported claims**, such as introducing a database
query, helper method, package, datatype, API, default, or design intention that the
available evidence never establishes. The latter can occasionally be true, but it is
still unsafe documentation until independently supported. This distinction follows
the intrinsic/extrinsic split used in summarization research and code-summary
evaluation: a statement may conflict with its source, or may simply be unverifiable
from it ([Maynez et al., 2020, §§2.1–2.2](https://aclanthology.org/2020.acl-main.173.pdf);
[Maharaj et al., 2025, §2](https://aclanthology.org/2025.acl-long.1480.pdf)).

**Supported finding (high confidence):** observed classes include nonexistent or wrong
references; incorrect API names, arguments, and packages; invented types and values;
misstated control flow, side effects, return values, and exceptions; behavior attributed
to callees without inspecting them; and purpose, business-rule, or design-intent claims
inferred from suggestive names or comments. In one study of 411 Java code summaries
from seven models, 31.63% contained at least one hallucinated entity description; in a
separate preprint's 540 generated Java method comments, even the best of three studied
models produced inaccurate content in 18% of comments
([Maharaj et al., 2025, Table 1](https://aclanthology.org/2025.acl-long.1480.pdf);
[Kang, Milliken, and Yoo, 2024, §§1–2](https://arxiv.org/pdf/2406.14836)). These are
bounded demonstrations, not estimates for all documentation agents or genres.

Failures arise because fluent continuation is not source entailment; low-frequency or
mutable technical facts are weakly represented; prompts reward completion instead of
abstention; incomplete evidence leaves gaps that plausible language can fill; lexical
cues such as method names and stale comments can override program logic; long or
branching code strains entity and relationship tracking; and a bad retrieved passage or
an earlier invented premise can anchor later generation. NIST characterizes
confabulation as a natural risk of systems that approximate training-data distributions,
while an OpenAI-authored analysis adds that accuracy-only evaluation rewards guessing
over acknowledging uncertainty ([NIST AI 600-1, §2.2](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf);
[Kalai et al., 2025](https://cdn.openai.com/pdf/d04913be-3f6f-4d2b-b283-ff432ef4aaa5/why-language-models-hallucinate.pdf)).
This explains risk, not inevitability: stronger models, appropriate abstention,
high-quality grounding, and verification all reduce some failures.

No single verifier establishes technical truth. The best-supported approach is a
**claim-type-matched verification stack**: decompose prose into atomic claims; trace
each named entity to a versioned repository or authoritative registry; check signatures
and configuration against machine-readable specifications; inspect control/data flow;
compile and type-check examples; turn behavioral claims into tests and execute them in
the target environment; observe real workflows for integration claims; and require a
maintainer or decision record for intent. Automated entailment, similarity, another LLM,
or a green test suite can triage risk but cannot serve as a universal oracle. This
conclusion is high confidence for entity, API, and executable-behavior claims, and
moderate confidence for repository-scale architecture and intent claims because those
genres lack comparable direct evaluation.

## Question, scope, and method

### Subquestions

- What counts as hallucination versus a potentially true but unsupported technical
  inference?
- Which entities, attributes, relationships, behaviors, conditions, and rationales have
  been observed or can cautiously be derived as failure classes?
- Which model and workflow mechanisms produce these claims?
- Which source, program-analysis, execution, runtime, and human-review methods detect
  each class, and what can each method not prove?
- Which mitigations reduce failure without converting a detection signal into false
  assurance?

### Exclusions

- Fabricated or circular citations except where source verification is one detection
  layer; that is topic 05.
- Revision mixing and stale documentation as primary failures; that is topic 03.
- Incorrect commands, procedures, and configuration as an end-to-end safety topic;
  this report covers only the unsupported factual assertions within them, leaving their
  broader execution risks to topic 08.
- Normative invention, omissions, security disclosure, reviewer automation bias, and
  corpus-wide propagation except for narrow boundary conditions.
- A policy decision for the Launchpad corpus or synthesis across the 20-topic program.

### Evidence and source plan

Local inspection covered the governing Launchpad instructions, vision, this program's
four control files, and the current corpus guidance on evidence, provenance, code/test
references, confidence, and validation. Those materials framed the documentation
context; no claim about Buzz product behavior was needed. The checkout began at
`4bac39fe512c9b289992951de1222abd61d5790c` on branch
`topic-04-technical-hallucination` on 2026-09-08.

External searching prioritized peer-reviewed code-summary, package, factuality, and
self-verification studies; reproducible preprints where peer-reviewed evidence was not
available; and NIST guidance. A working claim ledger tracked proposition, claim type,
support, counterevidence, context, confidence, and gap. Consequential claims were
triangulated where practical: the documentation taxonomy uses two independent Java
studies, referent errors use independent package and cloud-API studies, and mechanism
claims pair official risk guidance with empirical studies. Counter-searches targeted
successful self-verification, retrieval regressions, correct extrinsic inference,
stronger-model improvements, and metric failures. Searching stopped when additional
sources repeated existing classes or shifted into the neighboring topics, and every
subquestion had either a supported answer or an explicit gap.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Fabricated referent | The document names a symbol, method, file, datatype, package, command, API, option, or resource that does not exist in the claimed system. | Directly observed: generated Java comments referenced a nonexistent `addOption` method; code summaries invented an `int16` Java datatype; cloud code used nonexistent APIs; package-generation models invented dependencies ([Kang et al., 2024, §3](https://arxiv.org/pdf/2406.14836); [Maharaj et al., 2025, §1](https://aclanthology.org/2025.acl-long.1480.pdf); [Jain et al., 2024, Appendix A.5](https://arxiv.org/pdf/2407.09726); [Spracklen et al., 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen)). **Confidence: high** for the class, not its frequency in prose documentation. |
| Wrong identity or role | A real entity is selected, but it is the wrong one for the task or is assigned a capability, ownership, dependency, or relationship it does not have. | CloudAPIBench distinguishes use of an incorrect existing API from use of the correct API incorrectly. Code-summary examples attach database access to a method whose implementation only returns `-1` ([Jain et al., 2024, §2 and Appendix A.5](https://arxiv.org/pdf/2407.09726); [Maharaj et al., 2025, §1](https://aclanthology.org/2025.acl-long.1480.pdf)). Extending this to service ownership and architecture edges is a **moderate-confidence interpretation** requiring repository-scale study. |
| Wrong attribute, value, or contract | The entity exists, but the document invents or changes a type, parameter, required/optional argument, value range, default, supported variant, compatibility statement, or output shape. | Direct observations include invalid API argument configurations and a comment claiming all enum options were supported when only a subset was ([Jain et al., 2024, Appendix A.5](https://arxiv.org/pdf/2407.09726); [Kang et al., 2024, §3](https://arxiv.org/pdf/2406.14836)). Defaults and compatibility are included by **moderate-confidence inference** because they are the same claim shape but were not separately measured in documentation-agent studies. |
| Misstated program behavior | The document reverses a branch, invents validation, assigns a side effect to the wrong path, or states an incorrect return, exception, mutation, ordering, or failure behavior. | Code-summary annotations found confusion over nested conditions. Document testing exposed a comment claiming an unknown key returns `null` when execution throws `UnknownKeyException` ([Maharaj et al., 2025, §4](https://aclanthology.org/2025.acl-long.1480.pdf); [Kang et al., 2024, §§3 and 6.4](https://arxiv.org/pdf/2406.14836)). **Confidence: high.** |
| Unsupported transitive inference | A local snippet is treated as proof of behavior implemented in a callee, dependency, generated artifact, configuration layer, or runtime service that was not inspected. | Kang et al. found comments that incorrectly described properties of a returned `Node` object and classified the problem as lacking code context; the authors note that relevant context can balloon across classes and calls ([Kang et al., 2024, §3](https://arxiv.org/pdf/2406.14836)). **Confidence: high** for cross-call behavior and **moderate** for wider deployment topology. |
| Identifier- or prose-led story | Names, comments, log messages, or familiar conventions prompt a plausible narrative that conflicts with executable logic. | Maharaj et al.'s taxonomy identifies identifier-name bias and natural-language context: `getJobID` prompted an invented database retrieval, and a commented-out pattern prompted the wrong input-format description ([Maharaj et al., 2025, §4](https://aclanthology.org/2025.acl-long.1480.pdf)). **Confidence: high.** |
| Invented intent, rationale, or guarantee | The document upgrades what code does into why it exists, its business purpose, the developer's intent, a design guarantee, or a non-functional property without an authoritative human or decision source. | Kang et al. directly observed “hallucinating intent” and stress that a model cannot access the developer's mind; code alone did not expose the supported-option intent in their example ([Kang et al., 2024, §3](https://arxiv.org/pdf/2406.14836)). Architecture rationale, performance, security, and reliability guarantees are **moderate-confidence extensions**: they require different evidence types and should not be inferred from one successful path. |
| Contradictory synthesis | The prose recombines real source elements into a relation the source contradicts: wrong actor/action, negation, chronology, branch, or causal link. | Maynez et al. call this intrinsic hallucination and show that fluent, topical summaries can miscombine source facts despite good overlap scores ([Maynez et al., 2020, §§1–2](https://aclanthology.org/2020.acl-main.173.pdf)). The evidence is not code-specific, but the pattern is independently instantiated by the branch and entity errors above. **Confidence: high.** |
| Unmarked extrinsic addition | A claim is absent from the designated evidence. It may be false, or it may be correct background knowledge, but the author presents it without marking or independently verifying the inference. | Maynez et al. found some extrinsic additions were factual, establishing the counterexample: “not in source” is not synonymous with “false.” In their XSum setting, however, more than 90% of extrinsic hallucinations were erroneous ([Maynez et al., 2020, §§1–2](https://aclanthology.org/2020.acl-main.173.pdf)). The percentage must not be transferred to technical documentation. **Confidence: high** for the distinction. |

## Causes and mechanisms

**Sourced facts.** NIST explains that generative models approximate statistical
distributions—LLMs predict successive tokens—so factual accuracy is not guaranteed,
especially for open-ended, long-form, highly contextual, or expert tasks. The
OpenAI-authored mechanism paper argues that pretraining provides fluent positive
examples rather than truth labels and that accuracy-only evaluations reward a guess
while an abstention scores zero ([NIST AI 600-1, §2.2](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf);
[Kalai et al., 2025, §§2–4](https://cdn.openai.com/pdf/d04913be-3f6f-4d2b-b283-ff432ef4aaa5/why-language-models-hallucinate.pdf)).
The second source is produced by a model vendor and should not alone establish a
universal theory; NIST independently supports the distributional account, while the
evaluation-incentive explanation remains a well-argued mechanism rather than a direct
study of documentation agents.

Technical evidence adds more specific mechanisms:

- **Sparse and changing knowledge.** CloudAPIBench's 622 synthetic AWS/Azure tasks
  showed substantially worse valid invocations for low-frequency APIs; its authors
  connect this to under-representation and API evolution. The package study likewise
  found higher hallucination rates on more recent prompts. These results support the
  narrower claim that uncommon and recent identifiers are higher-risk in the tested
  settings, not that frequency alone causes every error
  ([Jain et al., 2024, §§1–2](https://arxiv.org/pdf/2407.09726);
  [Spracklen et al., 2025, §§4–5](https://www.usenix.org/system/files/usenixsecurity25-spracklen.pdf)).
- **Missing observability.** A method body cannot by itself establish a called class's
  complete behavior, deployment configuration, or developer intent. When a prompt
  still demands a detailed “business purpose,” the model has an answer slot but no
  adequate witness. **Researcher interpretation:** this mismatch between requested
  specificity and observable evidence converts an evidence gap into plausible prose;
  it is supported by the context and intent errors in both Java studies but has not
  been isolated experimentally as a causal variable.
- **Misleading shortcuts.** Identifier names and nearby natural-language comments are
  cheap semantic cues. Maharaj et al. directly observed models following those cues
  over logic, while code complexity—length, lexical load, multiple paths, and distant
  calls—was the largest category in their annotated sample
  ([Maharaj et al., 2025, §§4 and 6](https://aclanthology.org/2025.acl-long.1480.pdf)).
- **Error anchoring.** Chain-of-Verification experiments found that a verifier allowed
  to attend to the original answer tends to repeat its hallucinations; factored
  verification reduced that repetition. **Researcher interpretation:** a documentation
  agent that drafts, retrieves, verifies, and rewrites within one contaminated context
  risks treating its own prose as evidence
  ([Dhuliawala et al., 2024, §§3 and 5](https://aclanthology.org/2024.findings-acl.212.pdf)).
- **Imperfect retrieval.** Supplying documentation is beneficial only when retrieval
  returns the right material and the generator uses it correctly. On CloudAPIBench,
  documentation augmentation improved GPT-4o's valid low-frequency API invocations
  from 38.58% to 47.94% but, with a 50%-precision retriever, reduced its high-frequency
  performance by 39.02 percentage points. Selective retrieval using an API index and
  model confidence improved the benchmark average instead
  ([Jain et al., 2024, §§3–4, Table 3](https://arxiv.org/pdf/2407.09726)).

**Counterevidence and boundary.** Hallucination rates are not fixed. Maynez et al.
found pretrained summarizers more faithful than non-pretrained systems, retrieval and
selective grounding improve low-frequency API use, and factored self-verification
improves factual tasks ([Maynez et al., 2020, §5](https://aclanthology.org/2020.acl-main.173.pdf);
[Jain et al., 2024, §4](https://arxiv.org/pdf/2407.09726);
[Dhuliawala et al., 2024, §5](https://aclanthology.org/2024.findings-acl.212.pdf)).
The evidence therefore supports “predictable residual failure requiring verification,”
not “LLMs always invent facts” or “more context always helps.”

## Detection and validation

Verification should match the claim's semantics and use evidence independent of the
generated sentence wherever possible.

| Method | Detects best | Evidence | What it cannot establish |
|---|---|---|---|
| Atomic claim decomposition and evidence entailment | Mixed long-form prose where one sentence contains supported and unsupported parts; contradictions and unmarked additions. | FActScore decomposes generations into atomic facts and checks each against a reliable source; Maynez et al. found textual-entailment measures correlated with faithfulness better than ROUGE/BERTScore ([Min et al., 2023](https://aclanthology.org/2023.emnlp-main.741/); [Maynez et al., 2020, §5](https://aclanthology.org/2020.acl-main.173.pdf)). | Decomposition can omit or distort claims; the selected source can be wrong or insufficient; entailment is not runtime truth. Five factuality metrics were inconsistent and biased across 11 datasets, so a metric requires domain validation ([Godbole and Jia, 2025](https://aclanthology.org/2025.findings-acl.1175/)). |
| Exact entity and version resolution | Nonexistent symbols, files, commands, flags, APIs, packages, schema fields, and cross-version names. | ETF parses an AST and maps summary entities back to code; CloudAPIBench checks candidate calls against API specifications; the package study compares names with date-stamped PyPI/npm inventories ([Maharaj et al., 2025, §5](https://aclanthology.org/2025.acl-long.1480.pdf); [Jain et al., 2024, §2 and Appendix A](https://arxiv.org/pdf/2407.09726); [Spracklen et al., 2025, §4](https://www.usenix.org/system/files/usenixsecurity25-spracklen.pdf)). | Existence does not prove correct use, provenance, maintenance, or safety. A registry can already contain a malicious package, and imports do not map uniquely to package names. |
| Signature, schema, compiler, type, and static-analysis checks | Wrong names, arguments, types, required fields, syntax, and some control/data-flow or invariant claims. | CloudAPIBench's API-specification matching distinguishes incorrect existing APIs, invalid target-API use, and nonexistent APIs; ETF shows that entity existence must be followed by entity-intent verification ([Jain et al., 2024, Appendix A.5](https://arxiv.org/pdf/2407.09726); [Maharaj et al., 2025, §§5.1–5.2](https://aclanthology.org/2025.acl-long.1480.pdf)). | Static acceptance does not prove runtime behavior, dynamic dispatch, reflection, external services, configuration-dependent paths, or intent. ETF reached 73% F1 in its own dataset and depends partly on an LLM verifier; it is not an oracle. |
| Executable documentation and document-derived tests | Claimed outputs, exceptions, state changes, pre/postconditions, examples, and branch-specific behavior. | Kang et al. extract executable properties from comments, generate tests, inject them into the existing suite, and execute them. Test results had a strong statistical relationship with behavioral-comment accuracy where nine consistency/similarity/self-inspection baselines did not ([Kang et al., 2024, §§4–6](https://arxiv.org/pdf/2406.14836)). | A passing test proves only the tested property under that setup. Generated tests can test a property absent from the document; missing fixtures can make a correct claim fail; non-compiling tests were ignored in the study. Results were from Java/Defects4J, and extending the method to installation or API documents was proposed future work, not demonstrated. |
| Controlled end-to-end execution and runtime observation | Installation and operational procedures, integration paths, effective defaults, network/service interactions, permissions, side effects, and failure handling. | NIST recommends empirically validated evaluation under conditions similar to deployment and warns against extrapolating from narrow or anecdotal assessments ([NIST AI 600-1, Measure 2.3 and Measure 2.5](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)). | A successful run is an observation, not a universal guarantee. It does not cover unexercised branches, other versions, load, failure injection, platforms, or future state; destructive or security-sensitive procedures require isolated environments. |
| Independent source triangulation and authoritative human confirmation | Intent, rationale, ownership, trust boundaries, policy status, guarantees, and claims whose truth is not encoded in executable artifacts. | Kang et al.'s intent error could not be resolved from the method/class code alone. NIST recommends domain knowledge, source verification, grounded retrieval data, and documented generalizability limits ([Kang et al., 2024, §3](https://arxiv.org/pdf/2406.14836); [NIST AI 600-1, Measure 2.5](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)). | Maintainers can be mistaken, disagree, or describe desired rather than actual behavior. A decision record proves the decision, not implementation; code proves some implementation behavior, not rationale. Conflicts must remain visible. |
| Independent or factored model review, sampling, and uncertainty signals | Cheap triage for inconsistent answers, suspicious low-confidence names, or claims needing stronger verification. | Factored Chain-of-Verification reduced factual hallucinations, and CloudAPIBench found API-token confidence useful for selectively triggering retrieval ([Dhuliawala et al., 2024](https://aclanthology.org/2024.findings-acl.212/); [Jain et al., 2024, §4](https://arxiv.org/pdf/2407.09726)). | Agreement can be a shared misconception. CoVe did not eliminate errors, and ICLR 2024 experiments found intrinsic self-correction on reasoning tasks could fail or degrade performance without external feedback ([Dhuliawala et al., 2024, Limitations](https://aclanthology.org/2024.findings-acl.212.pdf); [Huang et al., 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html)). Use this to prioritize, never to certify. |

The methods are complementary. Entity resolution catches `addOption` immediately but
not a wrong description of a real method. Static analysis can expose a reversed branch
but not a business rationale. A unit test can refute “returns null” but not demonstrate
all error modes. Runtime evidence can establish what happened once, while an
authoritative decision record establishes intended policy rather than execution. A
review should therefore ask both **“what evidence supports this exact claim?”** and
**“what kind of evidence could refute it?”**

## Mitigations

The following are research-supported controls, not adopted project policy.

- **Make abstention a valid output.** Require “not established by the inspected
  evidence” when a claim cannot be verified, and evaluate unsupported specificity more
  harshly than bounded uncertainty. This targets the guessing incentive identified by
  Kalai et al.; it trades apparent completeness for lower false-assertion risk.
- **Separate extraction from composition.** First inventory entities and atomic claims
  with revision/version locators, then write only from that ledger. FActScore and ETF
  support atomicization and entity tracing. This improves auditability but can still
  miss relational errors and costs more than unconstrained generation.
- **Route each claim to a deterministic witness.** Resolve names against the checked-out
  tree, `--help` output, registry snapshot, schema, compiler, or official API
  specification; translate behavioral statements into executable assertions; send
  rationale or intent to a maintainer/decision source. Determinism narrows the verifier's
  task but cannot make an incomplete witness complete.
- **Ground selectively and record retrieval boundaries.** Retrieve exact, versioned
  sources for rare or uncertain APIs, then validate the candidate against an index or
  specification. CloudAPIBench shows both the gain and the regression risk: irrelevant
  retrieval can make a previously correct answer worse.
- **Keep draft and verification contexts independent.** Do not let a verifier treat the
  draft as source evidence. Factored CoVe reduced repetition of earlier hallucinations;
  an external compiler, test runner, schema, or human is stronger feedback than the same
  model's ungrounded opinion.
- **Use risk-proportional execution.** Compile examples and run focused tests for local
  behavior; use sandboxed integration workflows and failure cases for operational
  claims. Preserve environment, version, inputs, and output so the observation is
  interpretable. The trade-offs are time, infrastructure, test flakiness, and incomplete
  path coverage.
- **Review unsupported additions rather than only contradictions.** An extrinsic claim
  may be true and useful, but it needs its own source and label. Deleting every
  non-source phrase would also delete legitimate abstraction and background context;
  Maynez et al.'s factual extrinsic cases are counterevidence to such a blanket rule.
- **Continuously sample real outputs.** NIST recommends ongoing source/citation
  verification, grounded retrieval provenance, empirically validated capability claims,
  and monitoring for confabulation. Static release-time benchmarks cannot represent
  every repository, model update, or tool environment.

## Limits and open questions

- The two direct documentation studies cover Java method comments and summaries, not
  autonomous agents authoring multi-file architecture, deployment, or incident
  documentation. Whether their taxonomies and detector performance persist at
  repository scale is unresolved.
- The 18% and 31.63% figures use different units, samples, models, prompts, and labeling
  rules. They triangulate existence and variety of failure, not a common prevalence.
- Kang et al.'s document-testing work is a 2024 preprint and reports one language,
  Defects4J projects, and an LLM-generated test oracle. ETF is peer-reviewed but uses
  411 summaries and relies on large-model stages. Both explicitly limit
  generalizability.
- CloudAPIBench uses 622 synthetic Python tasks for AWS/Azure, while the USENIX package
  study covers Python and JavaScript package references. Generated-code results are
  strong evidence for entity/API failure shapes but indirect evidence for prose agents.
- “Unsupported” is relative to a declared evidence boundary. External knowledge can be
  correct and useful. The unresolved design problem is how to let an agent add it while
  preserving a visible distinction among observed fact, cited background fact, and
  inference.
- Verification can inherit the generator's failure: an LLM may hallucinate extracted
  entities or test properties, retrieval may surface irrelevant or poisoned material,
  and automated factuality metrics disagree. Independence is a gradient, not a binary
  property.
- No accessible study compared the complete proposed stack—claim decomposition,
  versioned source resolution, static analysis, compilation, targeted tests, runtime
  observation, and human intent review—on repository-scale generated documentation.
  Its combined effectiveness and cost remain open.
- Current evidence does not justify a universal claim that a particular model size,
  temperature, prompt, or review model prevents technical hallucination. Model and
  benchmark results are snapshots, and the package study found that changing common
  decoding parameters did not consistently reduce its measured hallucinations.

## Practical review checks

- Candidate check: split every changed paragraph into atomic technical claims; mark each
  as observed, externally sourced, inferred, or not established.
- Candidate check: for every named symbol, path, command, flag, package, API, schema
  field, and version, resolve the exact identifier in the target revision or
  authoritative versioned source.
- Candidate check: for a real entity, verify role and usage separately—existence is not
  proof that it performs the stated task or accepts the stated arguments.
- Candidate check: search for words that often hide unsupported upgrades—“default,”
  “always,” “never,” “automatically,” “ensures,” “designed to,” “because,” “secure,”
  and “supported”—and demand evidence appropriate to each proposition.
- Candidate check: trace transitive claims through callees, configuration, generated
  artifacts, dependencies, and services; otherwise narrow the statement to the local
  evidence.
- Candidate check: turn claims about outputs, exceptions, side effects, and boundary
  conditions into focused tests; retain the failing/passing evidence and target
  environment.
- Candidate check: exercise integration and operational claims in an isolated
  target-like environment, including at least one relevant failure path; record what
  remains unexercised.
- Candidate check: obtain a decision record or accountable human confirmation for
  intent, rationale, ownership, policy, and guarantees; do not infer them from names or
  implementation alone.
- Candidate check: ensure the verifier does not cite the generated draft or another
  derivative summary as independent evidence; re-open the original source.
- Candidate check: treat LLM agreement, confidence, similarity, entailment scores, and
  green tests as triage signals with documented false-negative/false-positive limits,
  not as a truth certificate.
- Candidate check: when evidence is absent or conflicting, preserve the gap beside the
  claim and prefer a narrower statement or explicit abstention over a plausible fill.

## References

- [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — NIST, July 2024; definition and mechanism of confabulation, empirically grounded evaluation, source verification, deployment-context testing, monitoring, and generalization limits.
- [ETF: An Entity Tracing Framework for Hallucination Detection in Code Summaries](https://aclanthology.org/2025.acl-long.1480/) — Maharaj et al., ACL 2025; Java code-summary dataset, taxonomy, static entity/intent verification, results, and limitations.
- [Identifying Inaccurate Descriptions in LLM-generated Code Comments via Test Execution](https://arxiv.org/abs/2406.14836) — Kang, Milliken, and Yoo, arXiv v1, 21 June 2024; Java comment error taxonomy, baseline negative results, document-testing method, and threats to validity.
- [On Mitigating Code LLM Hallucinations with API Documentation](https://arxiv.org/abs/2407.09726) — Jain et al., arXiv v1, 13 July 2024; CloudAPIBench API failure classes, low-frequency risk, retrieval gains/regressions, index checks, and confidence-triggered retrieval.
- [We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen) — Spracklen et al., 34th USENIX Security Symposium, August 2025; 576,000-sample Python/JavaScript package study, registry comparison, mitigations, and the limit of existence checks.
- [On Faithfulness and Factuality in Abstractive Summarization](https://aclanthology.org/2020.acl-main.173/) — Maynez et al., ACL 2020; intrinsic/extrinsic hallucination distinction, correct extrinsic additions as counterevidence, human evaluation, and entailment-versus-similarity findings.
- [Why Language Models Hallucinate](https://cdn.openai.com/pdf/d04913be-3f6f-4d2b-b283-ff432ef4aaa5/why-language-models-hallucinate.pdf) — Kalai et al., OpenAI/Georgia Tech, 4 September 2025; statistical account of pretraining errors and the evaluation incentive to guess rather than abstain.
- [FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation](https://aclanthology.org/2023.emnlp-main.741/) — Min et al., EMNLP 2023; atomic-fact decomposition and source-supported precision for long-form output.
- [Verify with Caution: The Pitfalls of Relying on Imperfect Factuality Metrics](https://aclanthology.org/2025.findings-acl.1175/) — Godbole and Jia, Findings of ACL 2025; re-evaluation of five metrics on 11 datasets and evidence of disagreement, misestimation, and domain-sensitive bias.
- [Chain-of-Verification Reduces Hallucination in Large Language Models](https://aclanthology.org/2024.findings-acl.212/) — Dhuliawala et al., Findings of ACL 2024; factored self-verification, reduced repetition, gains, computational cost, and residual errors.
- [Large Language Models Cannot Self-Correct Reasoning Yet](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html) — Huang et al., ICLR 2024; counterevidence showing intrinsic self-correction without external feedback can fail or degrade reasoning performance.
