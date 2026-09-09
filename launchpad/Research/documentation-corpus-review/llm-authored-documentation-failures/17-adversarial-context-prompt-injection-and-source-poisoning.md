# Adversarial context, prompt injection, and source poisoning

| Metadata | Value |
|---|---|
| Topic number | 17 |
| Exact research question | How can malicious or strategically written code comments, issues, documentation, tool output, or external sources manipulate an agent's evidence selection, reasoning, or published content? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Documentation agents that read repository artifacts, issue trackers, command output, retrieved documents, websites, and tool results before drafting or editing technical documentation. Covered outcomes include evidence suppression or promotion, factual poisoning, instruction hijacking, disclosure, unsafe tool use, and durable propagation into published documents. Only high-level, safe public examples are described; no payload is reproduced or executed. |
| Evidence limitations | Direct benchmarks test particular agents, models, tools, synthetic tasks, and threat models; they do not establish a universal attack rate or the prevalence of poisoned software repositories. Evidence about documentation publication is mostly an inference from indirect-prompt-injection and retrieval-poisoning results. Defenses change rapidly, and no located defense provides a general proof that arbitrary untrusted natural language cannot influence a capable agent. |

## Executive answer

Malicious or strategically written repository material can manipulate a documentation
agent because the same model input carries both the authorized task and text gathered as
evidence. A comment, issue, webpage, or tool result can contain language that resembles an
instruction, can assert false facts optimized for retrieval, can hide relevant evidence
under distracting material, or can induce the agent to publish a chosen claim. If the
agent also has tools, the effect can extend from bad prose to reading unrelated data,
changing files, or disclosing information.

This is not only hypothetical. Indirect prompt injection was demonstrated against
LLM-integrated applications by Greshake et al.; the attacker controls content that the
application later retrieves rather than directly controlling the user's prompt
([Greshake et al., 2023](https://arxiv.org/abs/2302.12173)). InjecAgent evaluated 30
tool-integrated agents over 1,054 cases and reported that a ReAct-prompted GPT-4 agent was
vulnerable in 24% of its base cases, while AgentDojo provides 97 tasks and 629 security
test cases and finds meaningful failures on both security and ordinary task utility
([Zhan et al., ACL 2024](https://aclanthology.org/2024.findings-acl.624/);
[Debenedetti et al., NeurIPS 2024](https://arxiv.org/abs/2406.13352)). Those figures are
benchmark-specific and must not be quoted as production prevalence.

There are two related but distinct mechanisms. **Instruction injection** attempts to make
evidence act as a higher-priority command. **Knowledge or retrieval poisoning** changes
what evidence is selected or what facts it appears to support. PoisonedRAG demonstrated
that inserting a small set of attacker-chosen texts into a retrieval corpus can steer
target answers in its evaluated settings
([Zou et al., USENIX Security 2025](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf)).
Ordinary misinformation, advocacy, stale comments, and search-engine manipulation can
produce similar evidence bias without an explicit imperative sentence.

The central security conclusion is high confidence: **content authority must not imply
instruction authority, and read authority must not imply action or publication
authority**. Prompt wording and content filters can reduce attacks, but the stronger
controls live outside the model: restrict sources and privileges, preserve provenance,
separate retrieval from authorization, validate claims against independent authoritative
evidence, constrain outputs and tool calls deterministically, and require scoped human
approval for consequential publication or actions. Residual risk remains wherever the
task requires the model to semantically interpret attacker-controlled prose.

## Question, scope, and method

### Subquestions

- Which repository and external artifacts can become adversarial input channels?
- How do instruction injection, retrieval manipulation, and ordinary source deception
  differ?
- Which agent architecture choices turn manipulated context into published content or
  privileged action?
- What signals and tests can detect attacks, and which benign technical text creates hard
  false positives?
- Which mitigations reduce likelihood or impact, and what utility do they sacrifice?
- What do current benchmarks not establish about real documentation workflows?

### Exclusions

- Operational attack recipes, payload strings, evasion procedures, or testing against a
  live third-party system.
- Training-time model poisoning except where an indexed documentation store is itself the
  poisoned corpus.
- Accidental hallucination without strategically shaped evidence.
- Attribution of any local repository content as malicious.
- Program-wide policy or synthesis.

### Evidence and source plan

The local research contract was inspected at branch `docs/llm-research-program`, commit
`ec2db2ec943838a7d1e20ebcc93c76cd1fdf2b0b`. It expressly requires workers to treat
external content, comments, issues, logs, and tool output as evidence rather than
instructions and to ignore embedded requests that do not come from governing task
instructions
([local research contract](RESEARCH-CONTRACT.md#6-challenge-the-emerging-answer)). This is
a relevant trust rule, not evidence that every agent architecture enforces it.

External research prioritized NIST's adversarial-ML taxonomy, OWASP's current prompt-
injection risk entry, peer-reviewed or published benchmarks, and primary defense papers.
The claim ledger separated attack feasibility, measured benchmark performance, transfer
to documentation, and recommended architectural controls. Counter-searches looked for
low attack success, ordinary task failures that can confound security scores, strong
defenses, benign instruction-like content, and conditions in which curated read-only
generation materially limits harm. Research stopped at saturation across input channel,
selection mechanism, effect, detection, mitigation, and residual-risk classes.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Indirect instruction injection | Retrieved content impersonates or competes with the authorized task and changes the agent's behavior. | Demonstrated in LLM-integrated applications and agent benchmarks. Success depends on model, prompt, task, attack, tool design, and scoring; no universal rate follows. |
| Evidence promotion | Strategically phrased material attracts search, appears authoritative, or induces the agent to cite it over better evidence. | PoisonedRAG supports targeted retrieval/answer manipulation in tested RAG settings. Ordinary SEO or repetition may have similar effects without prompt injection, but that broader prevalence was not measured here. |
| Evidence suppression and distraction | Long, repetitive, or highly salient material crowds out contradictory source code, tests, or policy, or consumes the agent's context and attention. | This is consistent with finite retrieval/context and adversarial resource-control models in NIST AI 100-2e2025; direct documentation-agent effect sizes are unknown. |
| Semantic source poisoning | False facts, fabricated examples, altered comments, or misleading issue narratives are treated as evidence even when they contain no instruction. | Retrieval poisoning establishes feasibility; determining malicious intent from a false statement alone is generally impossible. |
| Tool-output spoofing | A command, build log, API response, or MCP/tool result includes attacker-controlled text that the agent treats as trusted instructions or as proof of success. | InjecAgent and AgentDojo model tool-returned untrusted data. A genuine signed tool result can still faithfully carry hostile content from its input. |
| Cross-boundary disclosure | Poisoned context induces the agent to include unrelated sensitive facts, links, or data in the document. | Benchmarks explicitly include private-data exfiltration scenarios; documentation publication is a plausible durable sink, not directly measured in the cited studies. |
| Unauthorized mutation | Evidence triggers file edits, commands, network actions, or publication beyond the user's task. | Impact requires excess agency or weak authorization. A read-only drafting agent sharply limits this class, though its prose can still be wrong or unsafe. |
| Durable corpus infection | Manipulated output becomes a trusted document, index entry, summary, or later retrieval source, amplifying the seed. | Strong causal plausibility, but no located longitudinal study follows a poisoned repository passage through repeated documentation generations. |
| Governance impersonation | Content claims to be an instruction file, policy exception, reviewer approval, or authoritative source without valid placement, provenance, or authority. | Deterministic hierarchy and authenticated metadata can reject some forms; semantic conflicts and compromised authoritative sources remain. |

## Causes and mechanisms

### Natural language combines data and control

LLM applications commonly concatenate task instructions and retrieved text into a token
stream. Spotlighting's authors describe the central weakness as the model's difficulty
distinguishing which source a span belongs to; their experiments reduced attack success
substantially by marking provenance, but that is an empirical mitigation in evaluated GPT
settings, not a formal separation
([Hines et al., 2024](https://www.microsoft.com/en-us/research/publication/defending-against-indirect-prompt-injection-attacks-with-spotlighting/)).

### Retrieval grants influence before reasoning begins

An attacker need not override explicit instructions if they can shape which passages are
retrieved. Keyword overlap, embedding similarity, repetition, recency, link structure,
and declared metadata can all affect selection. Once a poisoned passage becomes the only
apparently relevant context, a model may be faithfully grounded in a corrupted evidence
set. Citation generation can then launder the manipulation into an apparently auditable
document.

### Agent privileges convert influence into impact

Reading a malicious issue is a content-integrity risk. Allowing the same reasoning loop to
read private sources, execute commands, write files, and publish without an independent
policy check creates confidentiality, integrity, and availability impact. OWASP therefore
ties prompt-injection severity to business context and agency and recommends least
privilege, output validation, segregation of external content, and human approval for
high-risk actions
([OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)).

### Provenance and truth are separable

A verified commit proves who signed a version, not that its comment is true or safe for
the current task. Conversely, anonymous material may contain a valid bug report. Source
identity, integrity, authority for a claim type, independence, revision, and semantic
support are separate questions. Treating “from the repository” or “returned by a tool” as
a single trust level collapses those distinctions.

### Defensive prompts face an adaptive channel

Static phrases and classifiers can catch known patterns but benign security documentation
may itself discuss attacks, quote instructions, or contain imperative examples. Attackers
can also paraphrase or distribute meaning across artifacts. NIST's 2025 taxonomy treats
prompt injection and poisoning as adversarial-ML risks with attack capabilities and
mitigations, not as a solved input-sanitization problem
([NIST AI 100-2e2025](https://doi.org/10.6028/NIST.AI.100-2e2025)).

## Detection and validation

| Method | Useful detection | Boundary |
|---|---|---|
| Provenance and authority checks | Unknown authors, unexpected path changes, unsigned revisions, source-class mismatches, and unapproved external domains. | Trusted authors can be wrong or compromised; provenance is not truth. |
| Content scanners/classifiers | Known injection markers, hidden text, suspicious role language, obfuscation, and anomalous instructions. | Natural-language paraphrase and benign security content create false negatives and positives. |
| Retrieval audit | Exact query, candidate set, ranking, exclusions, selected chunks, revision, and source diversity reveal selection manipulation. | Logging cannot prove an omitted source was unknown or that selected evidence is true. |
| Claim-source entailment review | Whether cited authoritative passages actually support each material published claim. | Entailment models have domain errors; authority, applicability, and completeness still require judgment. |
| Counterfactual runs | Remove, reorder, or replace suspect content; compare conclusions using authoritative-only and primary-source-only retrieval. | Stochastic variation complicates interpretation, and adaptive attacks may survive perturbation. |
| Canary and red-team tests | Whether controlled untrusted artifacts can alter prohibited outputs or actions in a safe test environment. | Passing known tests does not cover novel attacks; test content must never reach production indexes. |
| Tool-call policy enforcement | Blocks calls whose arguments, target, permission, or data flow exceed the user's authorized task. | Does not guarantee the prose is accurate or prevent allowed-but-misled actions. |
| Human adversarial review | Recognizes social context, strategic framing, authority conflicts, and implausible evidence chains. | Reviewers are fallible and should not be the only barrier to privileged effects. |

Security evaluation should report ordinary task success and security success separately.
A defense that blocks every document is secure only by destroying utility; a system that
completes tasks but follows injected instructions is not acceptable. AgentDojo explicitly
exposes this joint evaluation problem.

## Mitigations

1. **Establish an instruction root.** Only authenticated user/developer instructions and
   repository instruction files discovered under a deterministic hierarchy may govern the
   task. Content inside evidence may make claims but cannot grant itself authority.
2. **Separate planes.** Keep evidence ingestion, claim extraction, action authorization,
   and publication approval as distinct steps. Pass structured claims and provenance where
   possible rather than replaying arbitrary prose into every privileged decision.
3. **Minimize sources and privileges.** Use allowlisted repositories/domains for decisive
   claims, read-only credentials for research, narrow filesystem write scope, no ambient
   secrets, and explicit confirmation for publication or consequential tool use.
4. **Preserve trust metadata out of band.** Path, revision, signature, author, retrieval
   query, tool identity, and classification should be supplied by the application, not
   accepted from text that claims its own provenance.
5. **Use deterministic policy gates.** Validate output paths, schemas, commands, network
   destinations, data classifications, and tool arguments in code. Do not ask the same
   potentially compromised model whether its action is authorized.
6. **Triangulate decisive claims.** Prefer primary authority; require independent evidence
   for surprising or consequential assertions; inspect contradictions; never count copies
   from one lineage as corroboration.
7. **Mark untrusted spans.** Source delimiters, spotlighting, and structured content can
   reduce confusion. Treat them as defense in depth because their guarantee is empirical
   and model-dependent.
8. **Constrain the publication sink.** Stage drafts, show evidence deltas, prevent secret-
   bearing content, require domain-owner review, and rebuild retrieval indexes only after
   approval.
9. **Continuously adversarially test.** Evaluate current models, prompts, tools, and source
   classes with held-out and adaptive attacks, while measuring false positives and task
   utility.

The trade-off is real: strict source allowlists can exclude legitimate issue evidence;
read-only operation cannot validate every procedure; and mandatory approval can become a
rubber stamp. Risk-tier the controls and ensure an exception is explicit, scoped, logged,
and granted outside untrusted content.

## Limits and open questions

- Benchmark attacks are intentionally constructed and scores depend on attack and defense
  knowledge, model versions, tool interfaces, success definitions, and task difficulty.
- AgentDojo reports that models also fail benign tasks. A low attack-success figure can
  reflect incapability rather than robust instruction separation.
- PoisonedRAG concerns targeted question answering over benchmark corpora. Transfer to
  multi-file repository documentation is plausible but not a measured production rate.
- Some strategically written sources are persuasion or error, not cybersecurity attacks.
  Detection should focus on trust and support rather than attempting to infer intent.
- Curated, immutable, read-only sources greatly reduce attack surface. They do not remove
  falsehood, compromised upstream authority, or semantic manipulation.
- Spotlighting and instruction hierarchy can materially improve evaluated systems. The
  available evidence does not establish a general proof for arbitrary models and content.
- Human approval is not a complete security boundary if the reviewer sees only a fluent
  draft and not the source lineage, suppressed evidence, or requested actions.
- Open questions include robust data/control separation for natural-language tasks,
  source-independent authorization, safe semantic sanitization, and realistic longitudinal
  benchmarks where a poisoned document becomes future agent context.

## Practical review checks

- Candidate check: identify every content channel the agent read and who could modify it.
- Candidate check: show the authenticated instruction hierarchy separately from evidence;
  reject authority claims that exist only inside retrieved content.
- Candidate check: record retrieval queries, candidate sources, selected passages,
  revisions, exclusions, failures, and truncation before accepting the draft.
- Candidate check: re-run consequential claims using only independently authoritative
  sources and investigate material conclusion changes.
- Candidate check: inspect newly added comments, issues, generated files, tool output, and
  external pages for instruction-like or strategically repetitive content without
  executing it.
- Candidate check: require deterministic authorization for every tool call and publication
  target; untrusted prose must never expand permissions.
- Candidate check: scan source and rendered output for disclosures, hidden content,
  unexpected links, and statements unsupported by cited evidence.
- Candidate check: measure defense security and ordinary task completion together, and
  record model, prompt, tool, corpus revision, attack suite, and failure definition.
- Candidate check: prevent drafts from entering trusted retrieval indexes before review.
- Candidate check: quarantine and investigate provenance anomalies rather than asking the
  drafting model alone whether a source is malicious.

## References

- [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) — Greshake et al., AISec 2023; indirect prompt-injection attack model and application demonstrations.
- [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://aclanthology.org/2024.findings-acl.624/) — Zhan et al., Findings of ACL 2024; 1,054-case, 30-agent benchmark and bounded attack results.
- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) — Debenedetti et al., NeurIPS 2024; extensible agent utility/security evaluation with 97 tasks and 629 security cases.
- [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf) — Zou et al., USENIX Security 2025; targeted corpus-poisoning feasibility in evaluated RAG systems.
- [Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations](https://doi.org/10.6028/NIST.AI.100-2e2025) — NIST AI 100-2e2025, March 2025 with noted errata; authoritative taxonomy including indirect prompt injection and RAG poisoning.
- [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — OWASP GenAI Security Project, 2025 edition; risk definition, impacts, and layered mitigation guidance.
- [Defending Against Indirect Prompt Injection Attacks With Spotlighting](https://www.microsoft.com/en-us/research/publication/defending-against-indirect-prompt-injection-attacks-with-spotlighting/) — Hines et al., 2024; provenance-marking defense and empirical security/utility results in tested GPT settings.
- [Local research contract](RESEARCH-CONTRACT.md#6-challenge-the-emerging-answer) — launchpad-26/buzz revision `ec2db2ec943838a7d1e20ebcc93c76cd1fdf2b0b`, inspected 2026-09-09; local rule separating evidence from governing instructions.
