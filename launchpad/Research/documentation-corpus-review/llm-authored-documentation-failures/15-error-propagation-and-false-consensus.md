# Error propagation and false consensus

| Metadata | Value |
|---|---|
| Topic number | 15 |
| Exact research question | How do unsupported claims spread through summaries, indexes, runbooks, architecture documents, and later agent context until repetition appears to constitute confirmation? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Technical-documentation corpora in which human- or model-authored claims are copied, summarized, indexed, operationalized, or retrieved for later agents. Included: claim derivation, apparent source multiplicity, human repetition and consensus judgments, summarization factuality, retrieval-augmented generation (RAG), correction propagation, and repository controls. Local observations are from branch `docs/llm-research-program` at commit `81b5a1d059ea897968c4fe412497a351892d4598`. |
| Evidence limitations | **No located study follows one unsupported technical-documentation claim end to end through all five named artifact classes and later agents.** The mechanism is therefore a triangulation of direct evidence from citation networks, controlled human experiments, summarization and RAG evaluations, one bounded repository example, and provenance standards. Human laboratory effects and evaluated model/task combinations do not establish incidence or effect size in this corpus. |

## Executive answer

Unsupported claims spread when a documentation pipeline preserves the *content* of a
claim but drops or obscures its *evidential state*. A tentative statement in one source
can become a declarative sentence in a summary, a label in an index, a prerequisite in
a runbook, a component or invariant in an architecture document, and finally several
retrieved passages in an agent's context. Those passages are multiple publications but
may still be only one evidentiary lineage. If reviewers or agents count matching
statements instead of independent roots, derivation is mistaken for corroboration.

The strongest direct analogue is Greenberg's complete citation-network study of one
biomedical claim: citation bias, papers adding no new data, and citation-mediated
conversion of hypothesis into fact produced 242 papers, 675 citations, and 220,553
supporting citation paths around an authority the study found to be unfounded
([Greenberg 2009](https://pubmed.ncbi.nlm.nih.gov/19622839/)). Controlled human studies
likewise found that participants can give a dependent consensus—many reports ultimately
based on one source—similar weight to independent consensus
([Yousif, Aboody, and Keil 2019](https://pubmed.ncbi.nlm.nih.gov/31291546/)). Repetition
also raises perceived truth on average, but a 2026 meta-analysis characterizes the
corrected mean effect as small (`g = 0.37`) and substantially heterogeneous rather than
inevitable ([Ye et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13066098/)).

For later agents, the risk is more than a human analogy. In controlled RAG evaluations,
models favored evidence that appeared more frequently when external passages conflicted
([Jin et al. 2024](https://aclanthology.org/2024.lrec-main.1466/)); another study found
tested GPT and Llama models often favored model-generated context over conflicting
retrieved context even when the generated context was wrong
([Tan et al. 2024](https://aclanthology.org/2024.acl-long.337/)). These results are
model-, prompt-, dataset-, and period-specific. They support a plausible retrieval echo
mechanism; they do **not** show that every agent treats repetition as confirmation.

The practical conclusion is **high confidence** that untracked derivation can create
false evidentiary multiplicity, **moderate confidence** that this multiplicity increases
acceptance by humans and some RAG systems in technical-documentation workflows, and
**low/unknown confidence** about its prevalence and quantitative impact in real software
documentation. The appropriate control target is not duplicate wording alone. It is the
claim's lineage: independent primary roots, transformation steps, current status,
contradictions, and all descendants that must change when a root is corrected.

## Question, scope, and method

### Subquestions

- What is an unsupported claim, and when do repeated documents remain one evidentiary
  lineage rather than independent confirmation?
- Which transformations let a seed claim gain reach, certainty, or authority across
  summaries, indexes, runbooks, architecture documents, and agent context?
- What mechanisms make repeated or dependent claims persuasive to humans and later
  language models?
- How can a reviewer reconstruct propagation, distinguish independent corroboration
  from copying, and find stale descendants after correction?
- Which mitigations interrupt propagation without treating all reuse or repetition as
  an error?
- Where do the evidence and proposed checks fail to establish truth, independence, or
  real-world prevalence?

### Exclusions

- Model-training feedback and “model collapse”; the question concerns documents used as
  published artifacts or runtime context, not recursive training on synthetic data.
- Deliberate source poisoning and prompt injection except where they expose the same
  lineage problem; adversarial manipulation is assigned to topic 17.
- General cross-document terminology drift except where it is a propagation symptom;
  that wider problem is assigned to topic 14.
- A program-wide policy or synthesis. The checks below are candidate research outputs,
  not adopted controls for Buzz or the launchpad corpus.
- Claims that are repeated *and independently supported*. Agreement among genuinely
  independent, applicable sources is corroboration, not false consensus.

### Evidence and source plan

The research first inspected the local governing documents and history, then searched
four evidence streams: empirical citation/copying networks; experimental work on
repetition and dependent consensus; factuality and source-conflict evaluations for
summarization and RAG; and authoritative provenance/risk guidance. Material claims were
tracked against supporting evidence, contrary evidence, context, confidence, and gaps.
Searches explicitly sought conditions where warnings, source-independence cues, or
excessive repetition weaken the effect.

The local inspection found a small, directly relevant correction-fan-out example. At
the recorded commit, the explanatory
[`launchpad/README.md`](../../../README.md#opening-a-pr)
says two approving reviews are needed, while the normative
[`launchpad/AGENTS.md`](../../../AGENTS.md#6-branch-commit-pr)
says a live measurement found one and explains that the earlier figure was already
wrong. `git blame` attributed the surviving README line to commit `aa025924c` and the
normative correction to later commit `87abbed79`. This proves a stale derivative in this
revision, not an LLM cause, reader deception, or wider corpus rate. It is useful because
the README itself declares that AGENTS is authoritative, showing that declared authority
does not automatically propagate corrections.

#### Claim/evidence ledger

| Material claim | Best support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Many visible mentions can descend from one unsupported root and create unfounded authority. | Greenberg's content-coded citation network directly traced citation bias, amplification without data, and invention. | One biomedical controversy is not a software-documentation corpus; genuine independent replications do add evidence. | High for possibility and mechanism; unknown prevalence here. |
| People may mistake dependent repetition for independent consensus. | Yousif et al.'s preregistered/open-material experiments; Weaver et al.'s six experiments on a repeated voice sounding prevalent. | Connor Desai et al. found people distinguished the two when source independence was made salient and a no-consensus baseline was used. | High in tested settings; moderate generalization to documentation review. |
| Repetition can increase perceived truth and further sharing. | Meta-analysis across 182 studies; Pennycook et al.'s fake-news experiments; Henderson et al.'s sharing experiments. | Mean effect is small and heterogeneous; context, warnings, extreme implausibility, and perceived persuasion can reduce or reverse it. | High for average human effect; low for its magnitude in technical review. |
| Generated summaries can introduce a seed error that later artifacts inherit. | Large-scale human evaluations found substantial hallucinated content; source-summary consistency research demonstrates transformation errors. | These studies summarize news, not repositories; stronger systems and source-grounded methods improve faithfulness. | High for capability; unknown corpus incidence. |
| Some RAG systems prefer repeated or generated misinformation under conflict. | Jin et al. found frequency-based majority behavior; Tan et al. found bias toward generated context in tested GPT/Llama systems. | Artificial conflict tasks and dated model sets; behavior is not universal and can change with prompts, segmentation, decoding, and models. | Moderate. |
| Provenance enables lineage inspection but does not prove factual truth. | W3C PROV models derivation/revision/quotation; C2PA explicitly separates provenance from truth. | Complete, honest provenance still requires source validation; provenance can itself be incomplete or false. | High. |

Source saturation was reached when further searching repeated the same mechanisms—
transformation error, copied authority, repetition effects, source-dependence neglect,
and RAG conflict bias—without locating the missing end-to-end field study. That gap is
retained rather than filled by inference.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Seed fabrication | A source summary or newly drafted document introduces an unsupported entity, relationship, default, status, or causal claim. | Human evaluation found substantial hallucinated content in every assessed neural abstractive summarizer, including fluent and topical errors ([Maynez et al. 2020](https://aclanthology.org/2020.acl-main.173/)). The study used XSum news and older systems; it establishes the failure mode, not a rate for technical documentation or current models. |
| Certainty ratchet | A transformation changes “proposed,” “observed once,” or “may” into an unqualified fact, then later documents inherit only the stronger form. | Greenberg directly identified hypothesis-to-fact conversion through citation alone ([Greenberg 2009](https://pubmed.ncbi.nlm.nih.gov/19622839/)). In this repository, the vision's explicit `PROPOSED`, `OPEN`, `DECIDED`, and `IMPLEMENTED` states are a local attempt to preserve this dimension ([VISION.md](../../../VISION.md#how-to-read-this)); their effectiveness was not evaluated here. |
| Derivation laundering | A summary cites an intermediate document rather than the evidence that supports the claim. Each hop makes the origin and transformation harder to inspect, while the newest artifact looks self-contained. | W3C PROV distinguishes derivation, revision, quotation, usage, and primary-source relations precisely so origins and transformations can be represented ([PROV Primer §2](https://www.w3.org/TR/prov-primer/#intuitive-overview-of-prov)). A provenance relation describes lineage; it does not establish that the root supports the claim. |
| Copy-count consensus | Search or review surfaces several agreeing artifacts that all copy one root, and the number of artifacts is treated as the number of confirmations. | Participants in Yousif et al. gave true and false consensus similar confidence ([Yousif et al. 2019](https://pubmed.ncbi.nlm.nih.gov/31291546/)); a 2020 corrigendum corrected reported statistics but said the conclusions were unchanged ([corrigendum](https://journals.sagepub.com/doi/10.1177/0956797620948511)). Applicability to agents requires separate evidence. |
| Popularity-from-familiarity | Repeated exposure makes a statement easier to process or more accessible, increasing perceived prevalence, truth, or share-worthiness without new evidence. | One repeated speaker could sound like a chorus across six experiments ([Weaver et al. 2007](https://www.apa.org/pubs/journals/releases/psp-925821.pdf)); a 2026 meta-analysis found a small heterogeneous illusory-truth effect after small-study correction ([Ye et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13066098/)). This is probabilistic, not deterministic. |
| Genre-authority laundering | A copied statement gains practical force because its destination is treated as authoritative: an index makes it discoverable, an architecture diagram makes it structural, or a runbook turns it into an action. | NIST warns that confident GAI errors and confabulated citations can cause people to act on or promote false information ([NIST AI 600-1 §2.2, pp. 9–10](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)). No located experiment isolates these technical-document genres, so the genre-specific escalation is a structural interpretation. |
| Selective amplification | Supporting derivatives multiply while counterevidence, caveats, or failed tests remain in low-visibility sources; apparent agreement grows without the evidence balance changing. | Greenberg found citation bias against papers that weakened a claim and marked expansion by papers offering no relevant data ([Greenberg 2009](https://pubmed.ncbi.nlm.nih.gov/19622839/)). A single case cannot establish frequency in software corpora. |
| Retrieval echo | A later agent retrieves several semantically relevant descendants of one claim; repeated tokens or passages dominate a conflicting primary source or the model's other knowledge. | Jin et al. report frequency-based majority behavior and confirmation bias in tested RALMs ([Jin et al. 2024](https://aclanthology.org/2024.lrec-main.1466/)). Tan et al. found tested models biased toward generated contexts, partly because those contexts resembled the question more and retrieved chunks lost completeness ([Tan et al. 2024](https://aclanthology.org/2024.acl-long.337/)). These are controlled evaluations, not universal agent laws. |
| Self-citation loop | An agent cites or paraphrases an earlier generated artifact; the new document is then ingested as context for another agent, creating more apparently distinct support without an external check. | The RAG conflict studies show that generated and repeated context can influence answers, and NIST recommends grounding RAG data and verifying output sources ([NIST AI 600-1, MS-2.5-003–005, p. 34](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)). Direct longitudinal evidence for this exact documentation loop was not located; this class is an evidence-bounded synthesis. |
| Correction asymmetry | A root or authority is corrected but summaries, indexes, cached embeddings, runbooks, and architecture pages are not invalidated, leaving “zombie” copies available. | The local README/AGENTS mismatch at the recorded commit is direct evidence of one stale explanatory descendant after the normative file recorded a measurement and correction. It does not identify cause or user impact. W3C PROV's versioned entities and revision relations provide a representation for such dependencies, not an automatic repair ([PROV Primer §2.6–2.9](https://www.w3.org/TR/prov-primer/#intuitive-overview-of-prov)). |

## Causes and mechanisms

### A propagation chain

The following chain is an interpretation that joins the direct evidence; it is not a
single experimentally observed pipeline.

1. **Seed:** a claim is invented, overgeneralized, taken from a stale revision, or left
   unsupported. It may already be fluent. Summarization research shows why readability
   or lexical-overlap scores cannot be assumed to measure source faithfulness
   ([Kryściński et al. 2020](https://aclanthology.org/2020.emnlp-main.750/)).
2. **Compression:** a summary retains the proposition but drops modality, scope,
   version, counterexample, or source locator. An index compresses it further into a
   heading, label, link description, or search snippet.
3. **Functional promotion:** a runbook makes the proposition a prerequisite or step;
   an architecture document depicts it as a component, boundary, invariant, or settled
   decision. The claim now has consequences even though no new evidence was added.
4. **Replication:** authors or agents reuse those artifacts because they are concise,
   local, highly linked, or written in the vocabulary of the current task. Reuse is
   cheaper than reopening code, configuration, live state, or a primary record.
5. **Apparent corroboration:** search results, backlinks, or a reviewer reveal several
   matching passages. Without derivation edges, `n` documents look like `n` sources;
   evidentially they may be one source copied `n` times.
6. **Retrieval reinforcement:** chunking turns descendants into separately ranked
   context items. A generator sees a textual majority and may adopt it, particularly
   where the original evidence is absent, fragmented, or phrased less similarly to the
   query. The new response can become another corpus artifact.
7. **Persistence after correction:** downstream artifacts and retrieval indexes have no
   reverse dependency or invalidation path, so fixing the root does not remove its old
   descendants.

### Why repetition can look like evidence

Independent agreement is normally useful: separately produced observations are less
likely to share the same error. False consensus exploits that useful heuristic while
violating its independence condition. Yousif et al. found that participants knew in the
abstract that independent consensus was more believable yet often failed to apply that
distinction to the task ([2019 study](https://pubmed.ncbi.nlm.nih.gov/31291546/)). Weaver
et al. independently showed that familiarity from one person's repeated expression
inflated estimates of an opinion's prevalence even when the speaker identity was known
([2007 study](https://www.apa.org/pubs/journals/releases/psp-925821.pdf)). The relevant
documentation risk is therefore not merely forgetting a URL; it is failing to reason
over the dependency structure among apparently separate statements.

Repetition and consensus are related but distinct mechanisms. Repetition can increase a
single claim's familiarity; a group of agreeing documents can imply social or epistemic
consensus; and a retrieval system can implement a numerical majority over passages.
Calling all three “illusory truth” would hide important detection differences. A claim
graph can expose dependent consensus even if no reader experiences a cognitive truth
effect; an exposure warning may affect a reader but cannot deduplicate a retriever.

### Why artifact type matters

The named artifacts are not equal copies. A summary has high reach because it replaces
reading its source. An index controls discovery and may place a terse assertion next to
an authoritative link. A runbook is evaluated as an action sequence, so a factual premise
may escape review if the commands look plausible. An architecture document encourages
system-level inferences from a box, arrow, or declared boundary. Later agent context
often removes document-level layout and feeds passages as peers. This analysis predicts
that propagation can change both *reach* and *claim force* without changing wording.
No located study estimated those genre-specific multipliers, so they should be measured
rather than assumed.

### Why ordinary checks miss it

- Agreement checks can report consistency while every agreeing artifact is wrong.
- Link checkers prove reachability, not that the target contains supporting evidence.
- Citation counts count paths or mentions, not independent observations. Greenberg's
  220,553 supporting paths around one claim is the clearest warning against equating
  network volume with evidentiary weight.
- Text similarity can find verbatim copies but miss paraphrased descendants, while
  semantic similarity can mistake topical alignment for entailment.
- Factuality detectors are useful triage but not a stable oracle. Across nine annotated
  summarization datasets, detector performance varied by generator and error type, and
  no metric was best in every setting
  ([Tang et al. 2023](https://aclanthology.org/2023.acl-long.650/)).
- Human review of one diff sees the new sentence but often not its future retrieval
  weight, existing cousins, or reverse dependencies.

## Detection and validation

### Reconstruct claim lineage before counting support

For each consequential proposition, represent an atomic claim and its relationships:
`quoted-from`, `summarized-from`, `generated-from`, `revised-from`, `tested-by`,
`contradicted-by`, and `superseded-by`. Record artifact version or commit, relevant
environment, authoring activity, and exact evidence locator. W3C PROV provides a standard
conceptual vocabulary for entities, activities, agents, usage, generation, derivation,
revision, and primary sources ([PROV Primer](https://www.w3.org/TR/prov-primer/)). The
test is then “how many applicable independent roots support this claim?” rather than
“how many pages say it?”

This detects visible dependence only. Two documents may independently repeat the same
unrecorded source, and two authors may share the same upstream dataset or observation.
Conversely, shared provenance does not make a claim false; it only prevents the copies
from being counted as independent confirmation.

### Perform root entailment and applicability checks

Trace every material descendant to the earliest accessible evidence and ask separately:

- Does the cited span actually entail the atomic claim, including negation and modality?
- Does it support the same version, environment, component, population, and time?
- Is it an observation, proposal, decision, requirement, or implementation fact?
- Does any cited source merely cite another descendant in the same loop?
- What is the strongest contrary source or failed validation?

Sentence-level natural-language inference, question-answering checks, and span extraction
can prioritize suspicious claims. FactCC demonstrated scalable source-summary conflict
detection with supporting/inconsistent span extraction
([Kryściński et al. 2020](https://aclanthology.org/2020.emnlp-main.750/)), and a later
RAG checker traced nonfactual output to context chunks
([Sankararaman et al. 2024](https://aclanthology.org/2024.emnlp-industry.97/)). Neither
establishes real-world truth when all supplied context shares the same error, and Tang
et al.'s cross-dataset results argue against using one detector as a universal gate.

### Measure effective source diversity

Cluster sources by common root and transformation, not wording alone. Candidate review
metrics include:

- number of visible mentions;
- number of distinct provenance roots;
- number of roots with direct evidence rather than assertion;
- number of organizationally, methodologically, and temporally independent roots;
- ratio of descendant mentions to independent roots;
- whether supporting and contradicting roots receive comparable discovery weight.

These are diagnostic counts, not aggregate assurance scores. Independence is partly a
judgment about shared data, methods, incentives, and information channels. A high root
count can still be circular; a single definitive primary record may be sufficient.

### Test retrieval sensitivity

For an agent-facing corpus, repeat representative questions under controlled context
changes:

1. baseline retrieval;
2. deduplicated-by-lineage retrieval;
3. only the primary root plus explicit status/version;
4. balanced supporting and contrary evidence;
5. shuffled passage order and equivalent paraphrases;
6. removal of the most prolific derived family.

If the answer or confidence changes mainly with descendant count, that is evidence of
propagation sensitivity, not proof that the baseline answer was false. Jin et al.'s
majority findings motivate this test, while Chiang and Lee's finding that publication
time and, for one model, page appearance could change conflict answers shows why source
metadata and presentation should also be varied
([Chiang and Lee 2024](https://aclanthology.org/2024.blackboxnlp-1.24/)).

### Validate correction fan-out

When a root is corrected or superseded, traverse reverse dependencies and check every
summary, index entry, runbook premise, architecture assertion, generated corpus page,
embedding/index snapshot, and evaluation fixture derived from it. Search both exact old
wording and semantic paraphrases. Record descendants that intentionally retain history
so they are not confused with current guidance.

The local two-review/one-review mismatch can serve as a bounded regression fixture: a
corpus-level check should flag the contradictory current claims and authority relation.
It cannot infer the live GitHub setting; that still requires a current authoritative
measurement.

## Mitigations

### Preserve provenance and epistemic state through every transformation

A derived claim should carry its root locator, version/date/environment, derivation
type, confidence or status, and known counterevidence. Generated text should identify
which content is observation, inference, or recommendation. NIST specifically recommends
tracing content origins and modifications, reviewing and verifying GAI sources and
citations, verifying RAG grounding, and using version control to track generation,
modification, and sharing ([NIST AI 600-1, pp. 31, 34, 37](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)).

Trade-off: rich provenance costs authoring and review time, can become stale, and may
expose sensitive metadata. W3C PROV describes how to express a history, not how much to
collect. Collect the minimum that lets a reviewer recover evidential independence and
applicability.

### Separate canonical assertions from presentations

Where several artifacts must state the same operational fact, maintain one reviewed
canonical assertion or generate/transclude the repeated value, and make summaries and
indexes point to it. This reduces independent copies and gives corrections a bounded
fan-out. It does not make the canonical assertion true: centralization can turn one bad
claim into a high-blast-radius single point of failure. Require primary validation and
an owner before promoting a claim into a canonical source.

### Make authority and lifecycle machine-visible

Encode whether a document is normative, explanatory, historical, proposed, measured,
or generated; identify supersession and expiry; and prevent lower-authority derivatives
from being used as evidence for their own authority. The local VISION status vocabulary
is a concrete design example, while the README/AGENTS mismatch shows that an authority
declaration without automated fan-out is insufficient.

### Deduplicate retrieval by lineage, not only text

At ingestion, fingerprint exact copies, cluster paraphrases, retain parent/root IDs, and
cap the weight of one derivation family. Retrieve primary evidence and current normative
sources before summaries, then provide contrary evidence and source metadata. Treat ten
chunks from one root as one evidentiary family. This recommendation assumes a corpus
whose provenance is available; aggressive clustering can incorrectly collapse genuinely
independent evidence or remove useful genre-specific instructions.

### Gate promotion into action-bearing genres

Require stronger evidence when a claim moves from descriptive prose into a runbook step,
architecture invariant, security boundary, default, or agent instruction. Validate
runbook premises against executable or live evidence where safe, and architecture claims
against code, configuration, deployment state, or accepted decisions. A successful
command verifies behavior in its tested environment; it does not validate every prose
claim or future version.

### Publish corrections as graph events, not silent edits

Mark a claim retracted, superseded, or narrowed; preserve the reason; notify owners of
known descendants; rebuild search/RAG indexes; and add a regression question that would
have returned the old answer. Silent root edits leave cached and quoted descendants
untouched and can erase why the earlier text was unsafe.

### Use warnings and independence cues, but do not rely on them alone

Counterevidence matters. Connor Desai, Xie, and Hayes found that participants gave more
weight to true than false consensus when source independence was made salient and
judgments used a no-consensus baseline
([2022 study](https://pubmed.ncbi.nlm.nih.gov/35149359/)). Accuracy focus and warnings
can also reduce illusory truth in some experiments, while over-repetition can trigger
perceived persuasion and reduce credibility
([Koch and Zerback 2013](https://onlinelibrary.wiley.com/doi/10.1111/jcom.12063)). These
results argue against fatalism. They do not show that a badge, disclaimer, or prompt will
correct an agent's retrieval weighting or a stale runbook.

### Keep provenance distinct from truth

Signed or well-formed provenance can show who asserted what and how an artifact changed;
it cannot show that the assertion is accurate. C2PA states this limit explicitly and
notes that provenance may be incomplete
([C2PA Explainer §7.2](https://c2pa.org/specifications/specifications/2.2/explainer/Explainer.html#_provenance)).
Therefore lineage controls must be paired with source-entailment, applicability, and
reality checks.

## Limits and open questions

- **End-to-end evidence gap:** no located longitudinal study measured a false technical
  claim moving through summaries, indexes, runbooks, architecture documents, and agent
  context. A repository-seeded study with versioned claim lineage, controlled corrections,
  human reviewers, and several agent/retriever configurations would materially change
  confidence.
- **Prevalence is unknown:** the local mismatch is one purposively inspected case, not a
  random sample. It establishes possibility and a concrete failure of correction fan-out,
  not frequency, severity, cause, or reader impact.
- **Human-to-agent transfer is limited:** human familiarity and consensus experiments do
  not explain neural generation. The RAG studies provide direct agent evidence but use
  bounded tasks and models. Treat the mechanisms as convergent, not interchangeable.
- **The human repetition effect is not absolute:** the 2026 meta-analysis reports a small
  corrected mean with substantial heterogeneity. Extreme implausibility, warnings,
  accuracy attention, contextual cues, or perceived manipulation can bound or reverse
  effects. Repetition can also be a rational signal when sources are truly independent.
- **Research self-correction matters:** the central Yousif et al. study has a published
  corrigendum for inconsistent `d'` calculations; its authors state the conclusions are
  unchanged. This correction strengthens the report's insistence on revision-aware
  citation and cautions against treating even a relevant primary paper as timeless.
- **Truth may be dynamic:** software configuration, dependencies, and live platform
  settings change. A claim can have sound provenance and have been true when authored
  yet be false now. Version and observation time are therefore part of support, not
  optional metadata.
- **Paraphrase lineage remains hard:** exact-copy detection is straightforward; semantic
  lineage can confuse common knowledge, independent rediscovery, and copied claims.
  Automated clustering requires human review at consequential boundaries.
- **Authority can conflict:** code, tests, accepted decisions, live state, and normative
  documents may each be authoritative for different claim types. “Prefer primary
  sources” is insufficient without naming what source can decide the particular claim.
- **Provenance systems can fail:** missing edges, dishonest attribution, private sources,
  and inaccessible historical versions can create a false appearance of complete
  lineage. Absence of recorded provenance is not proof of fabrication; presence is not
  proof of truth.

Open empirical questions include: Which artifact types have the highest propagation and
correction latency? How should “effective number of independent sources” be operationalized
for code and configuration? Do current coding agents respond to lineage-aware retrieval
weights, or merely to passage count and order? Can a claim-level reverse-dependency graph
be maintained at acceptable cost? Which corrections reliably evict stale claims from
embeddings, summaries, and agent memory?

## Practical review checks

- Candidate check: for each consequential claim, show the earliest accessible supporting
  evidence and every intermediate derivative; do not count derivatives as corroboration.
- Candidate check: label each supporting root as independent, shared-data, copied,
  unknown-lineage, or definitive single authority, with a one-line rationale.
- Candidate check: compare the claim's modality, scope, version, status, and exceptions at
  each hop; flag any unreviewed certainty ratchet.
- Candidate check: search summaries, indexes, runbooks, and architecture pages for exact
  and paraphrased copies before approving a correction.
- Candidate check: when a claim is corrected, enumerate and update or explicitly retain
  every known descendant, then rebuild agent-facing retrieval indexes.
- Candidate check: reject citations that resolve only to another assertion in the same
  derivation family when direct evidence should exist.
- Candidate check: do not accept corpus consistency, link validity, citation count, or
  retrieval frequency as a truth test.
- Candidate check: test agent answers after lineage deduplication, primary-source-only
  retrieval, counterevidence inclusion, passage reordering, and removal of the dominant
  derivative family.
- Candidate check: require a current observation or executable validation before a claim
  becomes a runbook prerequisite, architecture invariant, or operational default.
- Candidate check: preserve `proposed`, `decided`, `implemented`, `observed`, `historical`,
  `superseded`, and `unknown` states through summaries and index entries.
- Candidate check: pair provenance validation with a separate source-support check;
  provenance proves lineage or integrity only within its stated boundary.
- Candidate check: record what could not be traced or validated beside the affected
  conclusion, not only in a closing limitations section.

## References

- [How citation distortions create unfounded authority: analysis of a citation network](https://pubmed.ncbi.nlm.nih.gov/19622839/) — Steven A. Greenberg, *BMJ*, 2009; complete claim-specific citation network showing bias, amplification without data, invention, and information cascades around one biomedical claim.
- [The Illusion of Consensus: A Failure to Distinguish Between True and False Consensus](https://pubmed.ncbi.nlm.nih.gov/31291546/) — Sami R. Yousif, Rosie Aboody, and Frank C. Keil, *Psychological Science* 30(8), 2019; controlled experiments comparing independent primary-source consensus with many reports derived from one primary source.
- [Corrigendum: The Illusion of Consensus](https://journals.sagepub.com/doi/10.1177/0956797620948511) — *Psychological Science* 31(8), 2020; corrected inconsistent `d'` statistics and related tests while reporting unchanged conclusions.
- [Getting to the source of the illusion of consensus](https://pubmed.ncbi.nlm.nih.gov/35149359/) — Saoirse Connor Desai, Belinda Xie, and Brett K. Hayes, *Cognition* 223, 2022; counterevidence showing discrimination improves when source independence is salient and an appropriate baseline is used.
- [Inferring the Popularity of an Opinion From Its Familiarity: A Repetitive Voice Can Sound Like a Chorus](https://www.apa.org/pubs/journals/releases/psp-925821.pdf) — Kimberlee Weaver, Stephen M. Garcia, Norbert Schwarz, and Dale T. Miller, *Journal of Personality and Social Psychology* 92(5), 2007; six experiments on repeated expression, familiarity, and perceived prevalence.
- [Systematic review and meta-analysis of the evidence for an illusory truth effect and its determinants](https://pmc.ncbi.nlm.nih.gov/articles/PMC13066098/) — Steeven Ye et al., *Nature Communications*, 2026; 182 studies, 366 effect sizes, and 31,184 participants, with small-study correction and substantial heterogeneity.
- [Prior exposure increases perceived accuracy of fake news](https://pubmed.ncbi.nlm.nih.gov/30247057/) — Gordon Pennycook, Tyrone D. Cannon, and David G. Rand, *Journal of Experimental Psychology: General*, 2018; controlled evidence that a single exposure can raise perceived accuracy, including under disputed labels, with extreme implausibility as a boundary.
- [The illusory truth effect leads to the spread of misinformation](https://pubmed.ncbi.nlm.nih.gov/36871397/) — Jennifer M. Henderson, Y. C. Wang, and Eryn J. Newman, *British Journal of Psychology*, 2023; two experiments linking repetition to sharing through perceived accuracy.
- [Helpful or Harmful? How Frequent Repetition Affects Perceived Statement Credibility](https://onlinelibrary.wiley.com/doi/10.1111/jcom.12063) — Thomas Koch and Thomas Zerback, *Journal of Communication*, 2013; countervailing truth and persuasion/reactance effects under frequent repetition.
- [On Faithfulness and Factuality in Abstractive Summarization](https://aclanthology.org/2020.acl-main.173/) — Joshua Maynez et al., ACL 2020; large-scale human evaluation of intrinsic and extrinsic hallucinations in XSum summarization systems.
- [Evaluating the Factual Consistency of Abstractive Text Summarization](https://aclanthology.org/2020.emnlp-main.750/) — Wojciech Kryściński et al., EMNLP 2020; source-summary consistency checking with supporting and inconsistent span extraction.
- [Understanding Factual Errors in Summarization: Errors, Summarizers, Datasets, Error Detectors](https://aclanthology.org/2023.acl-long.650/) — Liyan Tang et al., ACL 2023; comparison across nine annotated datasets showing detector performance varies by generator and error type.
- [Tug-of-War between Knowledge: Exploring and Resolving Knowledge Conflicts in Retrieval-Augmented Language Models](https://aclanthology.org/2024.lrec-main.1466/) — Zhuoran Jin et al., LREC-COLING 2024; controlled evidence of frequency-based majority and internal-memory confirmation preferences in evaluated RALMs.
- [Blinded by Generated Contexts: How Language Models Merge Generated and Retrieved Contexts When Knowledge Conflicts?](https://aclanthology.org/2024.acl-long.337/) — Hexiang Tan et al., ACL 2024; controlled conflicts showing tested GPT and Llama models often favored generated context, with similarity and segmentation identified as factors.
- [Do Metadata and Appearance of the Retrieved Webpages Affect LLM's Reasoning in Retrieval-Augmented Generation?](https://aclanthology.org/2024.blackboxnlp-1.24/) — Cheng-Han Chiang and Hung-yi Lee, BlackboxNLP 2024; controlled source-conflict tests varying publication time, source, and page appearance.
- [Provenance: A Light-weight Fact-checker for Retrieval Augmented LLM Generation Output](https://aclanthology.org/2024.emnlp-industry.97/) — Hithesh Sankararaman et al., EMNLP Industry 2024; context-grounded NLI factuality checking and chunk attribution across open datasets.
- [PROV Model Primer](https://www.w3.org/TR/prov-primer/) — World Wide Web Consortium, Working Group Note, 30 April 2013; authoritative model for entity/activity/agent provenance, derivation, revision, quotation, primary sources, and time.
- [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — NIST AI 600-1, July 2024; confabulation risk and recommended source verification, RAG grounding, provenance, versioning, and monitoring actions.
- [C2PA and Content Credentials Explainer](https://c2pa.org/specifications/specifications/2.2/explainer/Explainer.html) — Coalition for Content Provenance and Authenticity, specification 2.2 explainer, 2025; authoritative boundary that provenance can show origin/history but not whether content is factual and may be incomplete.
- [Toxic Code Snippets on Stack Overflow](https://ieeexplore.ieee.org/document/8643998/) — Chaiyong Ragkhitwetsagul et al., *IEEE Transactions on Software Engineering* 47(3), published online 2019; empirical software analogue showing copied snippets can remain outdated or harmful and spread without adequate checking or attribution.
