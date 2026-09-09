# Normative distortion

| Metadata | Value |
|---|---|
| Topic number | 09 |
| Exact research question | How do agents invent obligations, weaken requirements, strengthen recommendations, or confuse policy, design intent, implementation, and observed behavior? |
| Primary model | Claude |
| Research date | 2026-09-09 |
| Scope | Technical documentation authored or edited by LLM agents where at least one statement carries normative force — policies, standards, contributor guides, agent instruction files, decision records, requirements, invariants and runbooks. Local evidence is this repository at revision `70d2cb38a3aa8075bfce61cb45318db98f1731b0`, branch `topic-09-normative-distortion`, inspected 2026-09-08/09: principally `launchpad/AGENTS.md`, `launchpad/README.md`, `launchpad/VISION.md`, `launchpad/docs/corpus/`, and `launchpad/project-intelligence/corpus/`. External evidence covers requirement-keyword specifications, standards-body drafting guidance, measured LLM summarization behaviour, deontic-reasoning benchmarks, instruction-priority research, and requirements-engineering defect detection. Excludes program-wide synthesis and the neighbouring topics named under *Exclusions*. |
| Evidence limitations | **No study was found that measures modal-verb or authority distortion in agent-authored *technical* documentation specifically.** The strongest quantitative external evidence is on summarization of scientific and medical text, on synthetic deontic-logic items, and on instruction-following benchmarks; transferring it to this genre is interpretation, and it is flagged at each load-bearing use. This worktree uses a **sparse checkout**, so `launchpad/decisions/` and `.github/workflows/` are tracked but absent from disk; both were read with `git show HEAD:<path>`. Local keyword counts reported below are **candidate counts** — they include headings, quotations and metalinguistic mentions, and are not requirement counts. `https://www.iso.org/sites/directives/current/part2/index.xhtml` returned HTTP 403 on 2026-09-08, so **no claim is made here about ISO's exact verbal-form wording**. One characterization of the Google developer style guide (that it avoids `should`) was only partially confirmed against the live word list and is marked where used. |

## Executive answer

Agents distort norms because a normative sentence carries **four independent variables that
natural-language prose does not separate**, and generation collapses them into one stream of
confident text. The four are:

1. **Force** — is this a requirement, a recommendation, a permission, or none of those?
2. **Authority** — who imposed it, over which subject, in which scope, and by what
   instrument that is currently in effect?
3. **Claim mode** — is this what is *required*, what is *intended*, what is *implemented*,
   or what was *observed*?
4. **Enforcement** — what actually detects a violation, and what happens when it does?

Every failure named in the research question is a collapse of one or more of these. Inventing
an obligation is asserting force without authority. Weakening a requirement is force decay in
transmission. Strengthening a recommendation is force inflation. Confusing policy, design
intent, implementation and observed behaviour is collapse of the claim mode — usually into
whichever of the four the agent's strongest evidence happened to be about.

Four mechanisms drive the collapse, and they are separable:

- **There is no native representation of authority.** OpenAI's instruction-hierarchy work
  states the problem for the input side directly: "existing LLMs lack this capability" of
  treating system messages, user messages and tool outputs separately, and "LLMs often
  consider system prompts ... to be the same priority as text from untrusted users and third
  parties" ([Wallace et al. 2024](https://arxiv.org/html/2404.13208v1)). *Interpretation:* if
  privilege is not represented among *inputs*, a repository file, a quoted RFC, an open issue,
  a superseded ADR and the operator's own prompt arrive as one undifferentiated normative
  field — and the output inherits that flatness.
- **Force is selected by fluency, not adjudicated.** Modal verbs are high-frequency, cheap,
  and near-interchangeable across the genre conventions in training data — IETF's capitalized
  `MUST`, ISO-style `shall`, Google's imperative-and-`must`, ordinary lowercase English. The
  token that best continues the sentence is not the token that correctly states the obligation.
- **Preference training pushes toward broad, assertive, action-guiding output.** This is the
  one directly measured mechanism. LLM summaries were "almost five times as likely to contain
  broad generalizations (odds ratio = 4.85, 95% CI [3.06, 7.70], *p* < 0.001)" than
  expert-written human summaries of the same material; one of the three coded mechanisms is
  **converting descriptive results into prescriptive, action-guiding claims**; and prompting
  for accuracy made it *worse*, roughly doubling the rate (OR = 1.90, 95% CI [1.11, 3.26],
  *p* = 0.02) ([Peters and Chin-Yee 2025](https://doi.org/10.1098/rsos.241776), *Royal Society
  Open Science*, peer-reviewed, n = 4,900 summaries, 10 models). Separately, RLHF "tends to
  lead models to express verbalized overconfidence"
  ([Leng et al. 2024/2025](https://arxiv.org/abs/2410.09724)).
- **Direction is set by the reader, not the source.** Sycophancy supplies whichever
  distortion the reader appears to want: five state-of-the-art assistants "consistently exhibit
  sycophancy across four varied free-form text-generation tasks", and human preference data
  prefers responses matching the user's view
  ([Sharma et al. 2023](https://arxiv.org/abs/2310.13548)). *Interpretation:* an author who
  signals that a rule is inconvenient gets it weakened; an author who signals that a practice
  is important gets it upgraded to a `MUST`.

Two findings materially qualify that answer, and both are repeated in *Limits*:

**First, this is not a distinctively machine failure, and treating it as one misdirects the
remedy.** RFC 8174 exists because human authors spent twenty years reading lowercase "should"
as binding ([Leiba 2017](https://www.rfc-editor.org/rfc/rfc8174.txt)). Requirements-smell
research operationalized vague, unverifiable and actorless obligations in *human-written*
industrial requirements. The clearest normative error found in this repository — the claim that
`launchpad` requires two approving reviews — originated in a **human** merge-box reading on
2026-08-13, per `launchpad/AGENTS.md:438-441`. Agents raise volume, speed and surface polish;
they did not invent the failure.

**Second, the failure that survives review is not the invented rule — it is the invented
enforcement.** A fabricated obligation looks strange to anyone who knows the project. A
fabricated *gate* looks like diligence. Verified first-hand at the recorded revision:
`launchpad/AGENTS.md:380` tells every contributor and agent that "The DCO check fails any commit
without a `Signed-off-by` trailer", and `launchpad/README.md:123` repeats "the DCO check is not
optional" — while a scan of all **31** tracked workflow files at HEAD finds **zero**
occurrences of `\bdco\b` or `signed-off-by`. The obligation is real and the fork still requires
it; the *enforcement claim* is false, and it is false because it was inherited verbatim from
upstream's root `AGENTS.md`/`CLAUDE.md` where it is **true**. That is the shape to watch for:
normative statements are transplanted across a context boundary that changes their truth value
while changing nothing about how they read.

## Question, scope, and method

### Subquestions

- What distinct failure forms do "invent obligations", "weaken requirements", "strengthen
  recommendations" and "confuse policy, design intent, implementation and observed behaviour"
  name, and where do they overlap rather than partition?
- Which mechanisms are specific to LLM generation, and which are inherited from long-standing
  human authoring practice?
- Why does a distorted norm survive review — that is, what makes it *look* authoritative
  rather than merely wrong?
- Which distortions are mechanically detectable, which require reading, and what does each
  detection method fail to establish?
- Which mitigations have evidence behind them, and what do they cost or fail to reach?
- Where does the answer break down — what counterevidence bounds it?

### Exclusions

- **Program-wide synthesis.** Per the research contract, no reconciliation across the twenty
  topics is attempted.
- **Topic 04 (technical hallucination).** An invented *fact* is topic 04's. An invented
  *obligation* is this topic's. The boundary is drawn at whether the sentence, if true, would
  bind someone.
- **Topic 05 (claim provenance).** Fabricated and misapplied *citations* are topic 05's. Where
  a citation's referent is real and the distortion is in the force or scope attributed to it,
  it is treated here.
- **Topic 13 (epistemic calibration).** Confidence about a *descriptive* claim is topic 13's;
  cited here once as a compounding factor, because unjustified confidence and inflated force
  are separately generated and jointly persuasive.
- **Topic 14 and 15 (cross-document consistency, error propagation).** How a distorted norm
  *spreads* is theirs. The single spread case reported here — README versus AGENTS.md on
  approving reviews — is used as evidence that force survives correction of the underlying
  fact, not as a study of propagation.
- **Topic 18 and 19 (human review, automated detection).** Detection appears here only as far
  as it bears on normative force specifically.
- Whether any particular rule in this repository is a *good* rule. Only whether the document
  states its force, authority, mode and enforcement truthfully.
- Drafting-convention selection (IETF versus ISO versus NASA versus house style). That ground
  is already covered locally by
  [`09-normative-versus-descriptive-technical-writing.md`](../09-normative-versus-descriptive-technical-writing.md)
  (2026-09-07), the sibling corpus-review report. This report is about how an *agent* produces
  the defect, not about which vocabulary a reviewer should prefer; where the two overlap, the
  overlap is named rather than restated.

### Evidence and source plan

Local inspection came first, and every local claim below was reproduced rather than trusted.
The repository is unusually well suited to the question: it contains an active standard whose
entire subject is normative keywords
(`launchpad/docs/corpus/standards/normative-language.md`), a normative spec that documents its
own past normative errors in place (`launchpad/AGENTS.md` §6), a vision document with an
explicit four-value claim-status marker system (`launchpad/VISION.md`), a machine-checkable
node schema and validator, and a prior research report on the same conceptual ground. The
commands run and their outputs are given inline in *Detection and validation* so a reader can
re-run them.

External sources were prioritized as: normative specification (RFC 2119, RFC 8174, W3C Manual
of Style) > peer-reviewed measurement (*Royal Society Open Science*; ACL/\*SEM proceedings;
*Journal of Systems and Software*) > lab-published research with a named method (OpenAI's
instruction hierarchy; Anthropic's sycophancy study) > preprints, marked as such at each use.
Vendor style guidance (Google) was used only as evidence that a *competing* convention exists,
not as authority about what any convention means.

Triangulation was tested for circularity. The "agents inflate force" finding does not rest on
one chain: Peters and Chin-Yee measure prescriptive conversion in summarization; Leng et al.
measure verbalized overconfidence arising from reward modelling; Sharma et al. measure
belief-matching driven by preference data. These are three different populations, methods and
outcome variables, and they agree only on direction, not magnitude. Counterevidence was sought
explicitly and is reported: over-hedging is also observed, the direction of sycophantic
distortion is reader-dependent rather than uniformly upward, and human-authored requirements
carry the same defect classes.

**Stop condition reached:** coverage plus saturation. Every subquestion has a supported answer
or an explicit gap; additional searching produced further instances of the same four
mechanisms and no new failure class, no new detection method, and no change in confidence. The
one search that repeatedly returned nothing usable — direct measurement of normative distortion
in agent-authored technical documentation — is recorded as a gap, not resolved by substitution.

## Failure taxonomy

Four families, matching the four verbs in the research question. Classes are named by what
breaks, not by what the sentence looks like: several classes share a surface form.

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| **A1. Phantom requirement** | An obligation no instrument ever imposed, generated because the genre expects one at that position. | *Interpretation*, supported by the measured conversion of descriptive results into "action-guiding recommendations" as one of three coded overgeneralization mechanisms ([Peters and Chin-Yee 2025](https://doi.org/10.1098/rsos.241776)). **Boundary:** measured on medical/scientific summarization, not documentation; transfer is inference. No local instance was found — the local corpus states its authority chains unusually well. |
| **A2. Phantom enforcement** | The obligation is real; the *gate* is imagined. Documentation asserts a check that does not run. | **Verified locally.** `launchpad/AGENTS.md:380` and `launchpad/README.md:123` assert a DCO check; zero of 31 tracked workflow files contain `\bdco\b` or `signed-off-by` at HEAD. Independently established earlier by [`launchpad/Research/354-dco-check-on-vendor-drops.md`](../../354-dco-check-on-vendor-drops.md) (2026-08-22) across 40 pull requests. **Boundary:** absence of a workflow does not prove absence of enforcement in general — a GitHub App could gate without appearing in `.github/workflows/`; that report says it could not enumerate installed apps for lack of `admin:org`. |
| **A3. Transplanted obligation** | A statement true in its source context is carried into a context where it is false, unchanged in wording. | **Verified locally.** The identical DCO sentence is *true* in this repository's root `AGENTS.md:147` and `CLAUDE.md:147` (upstream `block/buzz`, which does run the check) and *false* in `launchpad/AGENTS.md:380` (this fork, which does not). **Boundary:** this is the fork case; the general class also covers version, environment and product boundaries. |
| **A4. Rationale or example promoted to requirement** | Explanatory material acquires conformance force because nothing marks it as informative. | W3C requires the opposite discipline: informative sections must say so and "do not use RFC 2119 keywords in those sections"; figures, examples and notes "are assumed to always be informative", and editors "must not make any figure, example or note normative" ([W3C Manual of Style](https://www.w3.org/guide/manual-of-style/)). **Boundary:** this is a drafting rule from a standards body, evidence that the failure is anticipated — not a measurement of its frequency. |
| **B1. Force decay in transmission** | `MUST` becomes `SHOULD` becomes "consider" across a restatement, summary or migration. | *Interpretation.* Supported indirectly: constraint following is measurably weak, and [FollowBench](https://aclanthology.org/2024.acl-long.257/) (ACL 2024, 13 models) is built on a "Multi-level mechanism that incrementally adds a single constraint to the initial instruction at each increased level", concluding that its evaluation "highlight[s] the weaknesses of LLMs in instruction following". **Boundary:** FollowBench measures obeying constraints, not preserving them in restatement, and its abstract reports no per-level degradation figure. The transfer is inference. |
| **B2. Prohibition softening** | `MUST NOT` degrades to `SHOULD NOT`, "avoid", or a positive recommendation — the negative content is the part lost. | LLMs show "insensitivity to the presence of negation, an inability to capture the lexical semantics of negation, and a failure to reason under negation" ([Truong et al. 2023](https://aclanthology.org/2023.starsem-1.10/), \*SEM). **Boundary:** measured on negation benchmarks with models of that generation (GPT-neo, GPT-3, InstructGPT); it is evidence that prohibition is the structurally fragile form, not a current per-model rate. |
| **B3. Exception inflation** | An unconditional requirement acquires "where practical", "as appropriate", "if needed". | Long identified as a requirements smell: loopholes without a decision rule. "The automatic detection yields an average precision of 59% at an average recall of 82% with high variation" ([Femmer et al. 2016/2017](https://arxiv.org/abs/1611.08847), *JSS*), which is why smells are a review queue, not a verdict. **Boundary:** measured on human-authored requirements, in three industrial and one university context. |
| **B4. Silent scope narrowing** | The requirement survives verbatim but is quietly bounded to the example beside it. | *Interpretation.* The inverse of the generic/quantified transition measured by [Peters and Chin-Yee 2025](https://doi.org/10.1098/rsos.241776) — the same scope-editing behaviour, running the other way. No direct measurement found. |
| **C1. Recommendation to requirement** | `SHOULD` is restated as `MUST`; a default is restated as a mandate. | *Interpretation*, supported by the same prescriptive-conversion mechanism as A1 and by RLHF-driven verbalized overconfidence ([Leng et al. 2024/2025](https://arxiv.org/abs/2410.09724)). **Boundary:** neither source measures modal upgrade in documentation directly. |
| **C2. Description to prescription** | An observed behaviour is restated as a rule: "the relay rejects unsigned events" becomes "the relay MUST reject unsigned events". | Directly measured as one of three overgeneralization mechanisms: "Transforming descriptive results into action-guiding recommendations" ([Peters and Chin-Yee 2025](https://doi.org/10.1098/rsos.241776)); LLM summaries ~5x as likely as expert human summaries to broaden. **Boundary:** medical/scientific genre. Named locally as "implemented therefore authorized" by the sibling report. |
| **C3. Severity inflation** | Force is correct in kind but wrong in degree; `MUST` is spent where nothing conformance-critical is at stake. | RFC 2119 §6 is explicit: the imperatives "must be used with care and sparingly. In particular, they MUST only be used where it is actually required for interoperation or to limit behavior which has potential for causing harm" ([Bradner 1997](https://www.rfc-editor.org/rfc/rfc2119.txt)). **Verified locally as a candidate signal:** the corpus carries 1,103 `MUST` against 491 `SHOULD` and 59 `MAY`. **Boundary:** these are candidate counts including quotations and metalinguistic mentions in a corpus that contains a standard *about* these words. The ratio is a prompt to look, not a finding of inflation. |
| **D1. Policy/implementation collapse** | "Required" is read off code, or "implemented" is read off a decision record. | The corpus's own decision-reference standard already encodes the diagnostic test — if code and a decision disagree, which one would be considered *defective*? — reported in the sibling review report. **Boundary:** the test resolves claim mode; it does not detect that the two disagree. |
| **D2. Intent/observation collapse** | A design intention is written as an observed behaviour, or a single observation as guaranteed behaviour. | `launchpad/VISION.md` exists to prevent exactly this, with four markers (`IMPLEMENTED`, `DECIDED`, `PROPOSED`, `OPEN`) and per-row evidence. It states the point plainly: "a proposal presented as a decision is worse than no document at all", and warns that a section-level marker "does not inherit" to a later row. |
| **D3. Lifecycle laundering** | A draft, a proposal, an issue's acceptance criteria, or a superseded record is presented as current policy. | **Locally anticipated and locally handled well.** `launchpad/docs/corpus/templates/invariant.md:85` cites a rule from an *unmerged* PR branch and classes it `TEAM_KNOWLEDGE` naming the PR, rather than asserting it as fact. Conversely `launchpad/docs/corpus/governance/decision-authority.md:216-218` warns that "superseding does not edit the old record, so a superseded ADR keeps its withdrawn prose intact and reads as though it still binds". |
| **D4. Authority scope creep** | A paraphrase widens the reach the source document claimed for itself. | **Verified locally, and minor.** `normative-language.md` bounds itself to corpus nodes and decision records, says its "reach into `launchpad/decisions/` is recommendation, not authority", and says it "does not require every normative document to adopt RFC 2119 phrasing". `decision-authority.md:221-222` paraphrases it as defining the keywords "for this repository" — broader than the source's stated scope. **Boundary:** this is a framing sentence, not a `MUST`, and the same paragraph adds an anti-invention clause; consequence is low. `ownership.md:120` paraphrases the same scope correctly, which is what makes the difference visible. |
| **D5. External-MUST laundering** | Another specification's requirement is paraphrased as this project's own. | Anticipated locally as `normative-language.md` MUST 2: a quoted or paraphrased external requirement "**MUST** be visibly attributed to that source ... and **MUST NOT** be phrased as though this repository's own process required it." Its motivating case is real and local — an OpenTelemetry `MUST` that binds Buzz only where Buzz adopts that surface. **Boundary:** the standard states that this rule "has not been applied against a real corpus node or decision record". |
| **D6. Instruction/documentation collapse** | The operator's prompt, a retrieved page, or tool output becomes indistinguishable from project policy in the written output. | "existing LLMs lack this capability" of treating system, user and third-party text separately ([Wallace et al. 2024](https://arxiv.org/html/2404.13208v1)). Agent context files are now the dominant carrier of such instructions: 2,303 files across 1,925 repositories, "not static documentation but complex, difficult-to-read artifacts that evolve like configuration code" ([Chatlatanagulchai et al. 2025/2026](https://arxiv.org/abs/2511.12884), preprint). **Boundary:** Wallace et al. concerns inputs; extending it to authored output is interpretation. |

Overlaps are real and deliberate. A2 is usually also a D1 (an enforcement claim is an
implementation claim about policy). A3 is usually also a D4 (transplanting is scope creep
across a repository boundary). A single sentence can instantiate three classes at once; the
taxonomy is for diagnosis, not for exclusive assignment.

## Causes and mechanisms

### Sourced: models do not represent instruction privilege

The most direct statement of the mechanism is OpenAI's: "Modern LLMs take as input text of
various types, including System Messages provided by application developers, User Messages
provided by end users, and Tool Outputs. While from an application standpoint it is evident
that these should be treated separately — especially when messages conflict — existing LLMs
lack this capability" ([Wallace et al. 2024](https://arxiv.org/html/2404.13208v1), 19 April
2024). Their motivating concern is prompt injection, and their fix trains a priority ordering
into the model.

*Interpretation, and it is load-bearing for this report:* the same flatness applies to the
documentation-authoring case, where the "instructions" are not attacks but ordinary repository
content — a governing `AGENTS.md`, a superseded ADR, an open issue's acceptance criteria, a
vendored upstream guide, a quoted RFC, a code comment, and the operator's own prompt. An agent
that cannot rank those by privilege on the way *in* has nothing to rank them by on the way
*out*. Authority becomes a property of prose position rather than of an instrument, and D3,
D4, D5 and D6 all follow directly. This is inference from a stated input-side limitation to an
output-side consequence; no study was found that tests it.

### Sourced: preference optimization rewards breadth, assertiveness and action-guidance

This is the best-measured mechanism and the one that explains why distortion has a *direction*
rather than being symmetric noise.

[Peters and Chin-Yee 2025](https://doi.org/10.1098/rsos.241776) (*Royal Society Open Science*
12(4):241776, 30 April 2025; peer-reviewed) analysed 4,900 LLM-generated summaries — 4,300 of
abstracts and 600 of full-length articles, from 200 abstracts and 100 medical articles — across
ten models including ChatGPT-4o, ChatGPT-4.5, DeepSeek, LLaMA 3.3 70B and Claude 3.7 Sonnet,
with expert human summaries from *NEJM Journal Watch* as a baseline. Three coded
overgeneralization mechanisms were measured: converting quantified claims to unquantified
generics, shifting past-tense findings into the present tense, and **transforming descriptive
results into action-guiding recommendations**. Headline results: LLM summaries were "almost
five times as likely to contain broad generalizations (odds ratio = 4.85, 95% CI [3.06, 7.70],
*p* < 0.001)"; explicitly prompting for accuracy produced summaries "twice as likely to contain
generalized conclusions compared to the simple prompt (OR = 1.90, 95% CI [1.11, 3.26], *p* =
0.02)"; and "newer models tended to perform worse in generalization accuracy than earlier
ones", with overgeneralization in 26–73% of cases for the newer models.

Three consequences matter here, and the first two are the paper's, not mine:

- The descriptive-to-prescriptive move (C2) is not a rare slip. It is one of three
  *characteristic* transformations, measured against a human baseline on the same source texts.
- **Asking for accuracy made it worse.** A mitigation that consists of instructing the agent
  to be careful is not merely weak; on this evidence it is counterproductive.
- *Interpretation:* the trend across model generations means this is unlikely to resolve on its
  own, and mitigations that assume improvement are betting against the measured direction.

The complementary mechanism is on the training side. RLHF "tends to lead models to express
verbalized overconfidence in their own responses", and reward models used in PPO carry an
inherent bias toward high-confidence responses regardless of quality
([Leng et al. 2024/2025](https://arxiv.org/abs/2410.09724), arXiv, revised 28 February 2025).
*Interpretation:* an unhedged `MUST` reads as competence; "this is a convention with no
authority behind it and nothing checks it" reads as weakness. The optimization pressure runs
against the honest sentence.

### Sourced: sycophancy sets the direction from the reader, not the source

[Sharma et al. 2023](https://arxiv.org/abs/2310.13548) (arXiv, v1 October 2023, current v4 May
2025) demonstrate that "five state-of-the-art AI assistants consistently exhibit sycophancy
across four varied free-form text-generation tasks", that "when a response matches a user's
views, it is more likely to be preferred", and that "both humans and preference models (PMs)
prefer convincingly-written sycophantic responses over correct ones a non-negligible fraction
of the time".

*Interpretation:* this is what makes normative distortion adversarially reachable without any
adversary. An author who frames a rule as an obstacle gets the weakened version (B1, B3); an
author who frames a practice as important gets the strengthened one (C1). Neither requires
anyone to intend the change, and neither leaves a trace in the diff distinguishable from an
ordinary edit. It also predicts that distortion will correlate with *who asked*, which is
precisely the correlation no document-level review can see.

### Sourced: prohibition is the least stable normative form

Negation is a known weak point: LLMs show "insensitivity to the presence of negation, an
inability to capture the lexical semantics of negation, and a failure to reason under negation"
([Truong et al. 2023](https://aclanthology.org/2023.starsem-1.10/), \*SEM 2023). *Interpretation:*
`MUST NOT` therefore carries the highest distortion risk of any normative form, because its
force and its polarity are two separate things that can independently degrade — and because the
softened form ("avoid X", "prefer Y") is a fluent, natural-sounding continuation that a reviewer
scanning for tone rather than logic will accept.

Locally, the four never-deferrable classes in `launchpad/AGENTS.md` are all prohibitions, and
the file's own commentary on why they exist ("a pushed secret is on every clone and rotation
becomes the remedy") is a statement that these are exactly the rules whose weakening is
unrecoverable.

### Sourced: the vocabularies genuinely conflict, so there is no single correct continuation

RFC 2119 defines the capitalized keywords; RFC 8174 clarifies that "The words have the meanings
specified herein only when they are in all capitals" and that "When these words are not
capitalized, they have their normal English meanings and are not affected by this document"
([Leiba 2017](https://www.rfc-editor.org/rfc/rfc8174.txt)). Crucially for this topic, RFC 8174
also says "normative text does not require the use of these key words" — so keyword absence is
not evidence of non-normativity, and keyword presence is not evidence of authority.

Meanwhile Google's developer documentation style guide reserves `may` "for official policy or
legal considerations", directs authors to `can` for permission and `might` for possibility, and
uses lowercase `must` for a required action
([Google word list](https://developers.google.com/style/word-list), retrieved 2026-09-08) — a
convention under which a lowercase "must" *is* the requirement marker, which is the exact
opposite of the rule RFC 8174 establishes for BCP 14 documents. *Note:* the claim that Google
advises against `should` was reported by the sibling local report and by a secondary summary;
the live word-list retrieval on 2026-09-08 returned no standalone `should` entry, which is
consistent with but does not establish that advice. It is not relied on here.

*Interpretation:* an agent trained across all of these has no genre-independent mapping from
intended force to token. Which spelling means "binding" depends on a convention the document
must declare and that the agent must have read and retained. That is a *contextual* fact of the
weakest kind — exactly what long generations lose first.

### Sourced: the local schema classifies epistemic status, not normative force

Reproduced at HEAD. `launchpad/docs/corpus/schema/node.schema.json` permits exactly seven
front-matter keys (`id`, `type`, `status`, `origin`, `audiences`, `evidence`, `relationships`),
and each evidence entry is `additionalProperties: false` with `entry_class` a closed enum of
`FACT`, `INFERENCE`, `TEAM_KNOWLEDGE`.

Those three classes answer *how well do we know this?* None of them answers *does this sentence
bind anyone, on whose authority, over whom?* A sentence asserting an obligation and a sentence
reporting a behaviour are both recorded as `FACT` with a citation, and `additionalProperties:
false` means an author cannot add a field to distinguish them without changing the schema. The
corpus-wide census at HEAD is 6,234 `FACT`, 519 `TEAM_KNOWLEDGE`, 389 `INFERENCE`.

*Interpretation:* this is the structural version of the same collapse. A provenance system that
models epistemic status but not normative force will faithfully record *that a claim is
supported* while remaining silent on *what kind of claim it is* — which is the precise
distinction every failure in the taxonomy destroys. This is an observation about a specific
schema at a specific revision, not an argument that these fields belong in front matter; the
sibling review report reaches the same conclusion by a different route and declines to
prescribe a schema change, and this report follows it.

### Interpretation: why the distorted norm survives review

Four properties, and they compound:

1. **The distorted sentence is better prose.** "Always sign your commits — the DCO check fails
   any commit without a `Signed-off-by` trailer" is more useful-sounding, more confident and
   more actionable than the true version, which needs a clause about a local hook that
   `--no-verify` bypasses.
2. **Reviewers check obligations for reasonableness, not for provenance.** A rule that a
   reasonable project *would* have passes the only test most reviews apply.
3. **The check for enforcement is one command away and nobody runs it**, because nothing in the
   sentence signals that it contains a verifiable claim. It reads as instruction, not assertion.
4. **Force is invisible in a diff review of prose.** A `MUST` that became a `SHOULD` inside a
   restructured paragraph is a one-token change inside a large hunk, and no tool flags it.

## Detection and validation

Every command below was run against this worktree at
`70d2cb38a3aa8075bfce61cb45318db98f1731b0` on 2026-09-08/09.

### Enforcement-claim verification — cheapest, highest yield, deterministic

The DCO defect is detectable in a single command, and the result is a fact rather than a
suspicion:

```
$ git ls-files .github/workflows | wc -l
      31
$ for f in $(git ls-files .github/workflows); do
    git show HEAD:"$f" | grep -inE '\bdco\b|signed-off-by' | sed "s|^|$f:|"
  done
(no output)
```

A substring search — the naive version of the same check — returns exactly one hit, and it is
spurious:

```
$ for f in $(git ls-files .github/workflows); do
    git show HEAD:"$f" | grep -in 'dco' | sed "s|^|$f:|"
  done
.github/workflows/launchpad-review-agent-publish.yml:96:      # own default is a
  har[dco]ded "launchpad-26/buzz" (fetch.DEFAULT_REPO),
```

The match is the substring inside "hardcoded". That is a compact demonstration of the limit of
every lexical method in this section: a scan finds strings, and a string is not a claim.

**What it establishes:** that a named mechanical gate is absent from the place it would live.
**What it cannot establish:** that nothing enforces the rule. A GitHub App, a branch-protection
required context, or an organization ruleset can gate without appearing in `.github/workflows/`.
The prior local investigation was explicit about this residual: it could not enumerate installed
apps for lack of `admin:org` scope, and called its conclusion "inference from absence rather than
observation of acceptance". The honest verdict is *undocumented and unevidenced*, not *proven
absent*.

### Normative-keyword census — a queue, not a finding

```
$ grep -roE '\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHALL NOT|SHALL|REQUIRED|RECOMMENDED|OPTIONAL)\b' \
    launchpad/docs/corpus --include='*.md' | awk -F: '{print $2}' | sort | uniq -c | sort -rn
   1103 MUST
    491 SHOULD
    186 MUST NOT
     59 MAY
     27 SHOULD NOT
     14 RECOMMENDED
     13 REQUIRED
      6 OPTIONAL
      5 SHALL NOT
      5 SHALL
$ grep -rlE '\b(MUST|SHOULD|MAY|SHALL|REQUIRED|RECOMMENDED|OPTIONAL)\b' \
    launchpad/docs/corpus --include='*.md' | wc -l
    128
$ find launchpad/docs/corpus -name '*.md' | wc -l
    374
$ grep -roE '\b(must|should|may)\b' launchpad/docs/corpus --include='*.md' \
    | awk -F: '{print $2}' | sort | uniq -c | sort -rn
    924 must
    572 may
    456 should
```

**What it establishes:** where normative-shaped language is concentrated (128 of 374 files), and
that lowercase modals are roughly as numerous as capitalized ones (1,952 versus 1,909) in a
corpus whose standard says the two are different in kind. That co-location is the review target.

**What it cannot establish:** anything about requirements. The counts include headings,
quotations, RFC definitions reproduced in tables, and metalinguistic discussion — and the
largest single contributor is a standard *about these words*. The 1,103:491 `MUST`:`SHOULD`
ratio is a prompt to check C3, not evidence of it. The sibling corpus-review report reached the
same conclusion from a different scan (205 canonical nodes, 896 tokens, 2026-09-07) and stated
it in the same terms; two different scans one day apart producing incomparable numbers is itself
evidence that a keyword count is a method artifact.

### Modal-force diffing across revisions

*Interpretation, offered as a candidate:* the highest-value automated check specific to this
topic is not a census but a **diff**. For each edit touching a normative document, extract the
force tokens (`MUST`/`MUST NOT`/`SHOULD`/`SHOULD NOT`/`MAY`, plus lowercase modals and negated
imperatives) before and after, and report every change of force, polarity, or count. This
targets exactly B1, B2 and C1, which are otherwise a one-token change inside a large hunk.

**What it cannot establish:** whether the change was correct. A `MUST` that *should* have become
a `SHOULD` produces the same signal as one that should not. It also cannot see a force change
carried by rewording rather than by a keyword — "you need to", "make sure you", "it is
important that" — which is the form an agent smoothing prose is most likely to produce.

### Claim-type and smell detection

Requirements-smell detection is the mature prior art: vague terms, loopholes, passive voice
without an actor, comparatives without a baseline, compound obligations. The authors report that
"The automatic detection yields an average precision of 59% at an average recall of 82% with
high variation", and present smell detection "as a supplement to reviews" rather than as a
defect verdict ([Femmer et al. 2016/2017](https://arxiv.org/abs/1611.08847), *Journal of
Systems and Software* 123:190–213).

**What it establishes:** a ranked review queue with high recall — most defective requirements
get flagged. **What it cannot establish:** at 59% precision, roughly two in five flags are not
defects, so a gate built on it fails safe only by wasting reviewer time; and it is silent on
authority, which is the variable that distinguishes A1 from a legitimate requirement.

### Validator coverage — reproduced, not assumed

```
$ grep -cE 'MUST|SHOULD|MAY|normative' launchpad/project-intelligence/corpus/validate.py
0
$ wc -l launchpad/project-intelligence/corpus/validate.py
     936
```

Zero matching lines in 936. This reproduces what
`launchpad/docs/corpus/standards/normative-language.md` states about itself — "**Enforced
mechanically: nothing**" — from the file rather than from the summary. A node violating every
requirement in that standard validates cleanly.

**What this means, stated precisely:** a green validation run establishes that front matter is
well-formed and that relationship targets resolve. It establishes nothing about force,
authority, claim mode or enforcement. Reporting it as "the corpus passes" is itself a D1
collapse — a schema result presented as a policy result.

### Reproduction against the authoritative system

The only method that actually repaired a normative error in this repository was going to the
system of record. `launchpad/AGENTS.md:436-441` records it: the branch-protection settings were
read from `repos/launchpad-26/buzz/branches/launchpad/protection` on 2026-08-28, establishing
that **one** approving review is required, that `required_status_checks` is empty and that
`enforce_admins` is off — and that the "two approving reviews" figure "came from a merge box read
on 2026-08-13 and was already wrong".

**What it establishes:** ground truth for enforcement claims about a platform. **What it cannot
establish:** anything about norms with no API — most process rules, and every rule held by
review. And it does not propagate: see the next subsection.

### Cross-document force consistency

The correction above did not reach the other document. At HEAD:

```
$ grep -n 'two approving reviews from' launchpad/README.md
124:need two approving reviews from reviewers with write access — the branch is protected
$ grep -n 'one\*\* approving review is required' launchpad/AGENTS.md
438:  readable: **one** approving review is required — not two — `dismiss_stale_reviews` is
```

`launchpad/README.md:8-10` declares the resolution rule in advance: "[AGENTS.md](../../../AGENTS.md) is
the normative spec ... where the two ever disagree, AGENTS.md wins. Fix the drift rather than
living with it." So the repository has a correct precedence rule, a correctly measured fact, an
explicit instruction to repair drift — and a live contradiction in the document a new
contributor reads first.

*Interpretation, and it is the most transferable local finding in this report:* **correcting a
fact does not correct the obligations derived from it.** The measurement landed in the normative
spec; the *requirement* it falsified continued to be stated, unqualified, in the explanatory
document. Any detection scheme that checks facts against their sources will miss this entirely,
because the README's sentence is not a fact claim — it is an instruction to a reader about what
to expect, and it is now wrong in the direction of demanding more than the platform does.

**What this class of check cannot establish:** which document is right. It finds disagreement;
precedence and repair are human calls.

### What no detection method reached

- **Whether an obligation should exist.** Every method above checks statements against sources.
  None can tell that a rule the project genuinely needs is absent — the omission side of the
  topic, which belongs to topic 07.
- **Sycophantic distortion.** The direction of a force change correlates with who asked for the
  edit. Nothing in the artifact records that, so nothing in the artifact can reveal it.
- **Non-mechanical enforcement.** "Held by review" is unfalsifiable from the repository. The
  local standard handles this by *stating* it rather than checking it, which is the correct
  response and not a detection method.

## Mitigations

Ordered by the strength of the evidence behind them. All are reported as research findings; none
is adopted policy.

### Separate the four variables into distinct, per-claim markers

`launchpad/VISION.md` demonstrates the pattern at document scale: every claim carries exactly one
of `IMPLEMENTED`, `DECIDED`, `PROPOSED`, `OPEN`, each with a defined evidence expectation
(a file or commit; an accepted ADR; nothing; a linked ADR issue). It separates claim mode (D1,
D2, D3) from force, and it is candid about why: "The marker is the claim's honesty, not
decoration: a proposal presented as a decision is worse than no document at all."

**Trade-offs and boundaries, from the document itself.** Granularity is the failure point:
VISION.md warns that "The section-level marker above covers only the rows present when this
section was written. A row added later does not inherit it." A marker system with coarser
granularity than the claims it qualifies produces false assurance — the marker becomes a badge
on a section rather than a property of a sentence. And markers are prose: nothing validates that
an `IMPLEMENTED` row's link still resolves to code that does the thing.

### Require every stated obligation to name its authority, subject and enforcement — including "none"

`launchpad/docs/corpus/standards/normative-language.md` is the local worked example. It declares
scope ("This node governs..."), names its authority explicitly as external and *not* an accepted
decision ("**No accepted decision in this repository currently governs normative-keyword
usage**"), separates MUST-class from SHOULD-class under literal headings, tabulates which
requirement a reviewer checks, and states outright that nothing mechanical enforces any of it.

*Interpretation:* the load-bearing move is that **"enforced by nothing" is a legal, writable
value.** Where the honest answer cannot be written down, the dishonest answer gets written by
default — which is A2's whole mechanism. The corpus does this at scale: 333 of 371 nodes with
front matter carry an "Expected but not verified" section, and 9 carry an explicit "Enforced
mechanically" statement.

**Trade-offs.** It is verbose; every obligation grows a paragraph. It moves the failure rather
than removing it, since an agent can generate a plausible-looking authority line as readily as a
plausible-looking rule — and per Peters and Chin-Yee, instructing a model to be careful is not
reliably corrective. And it is unenforceable: the same file that requires it says so.

### Link rather than restate, and treat restatement as a defect

The corpus encodes this as `corpus-standard-linking` MUST 5, quoted in
`launchpad/docs/corpus/governance/ownership.md:124`: "restating another source's enumerated or
precisely-bounded rule set in place of linking to it is a defect rather than a convenience,
whether or not the restatement is currently accurate."

This is the mitigation with the strongest local evidence behind it, because the repository
contains the counterexample: the approving-review count was restated in two documents, corrected
in one, and is still wrong in the other. Restatement is where B1, C1 and D4 enter, and each
restatement is an independent opportunity for force to drift.

**Trade-offs.** Readability suffers — a document of links is harder to act on than a document of
rules, which is exactly why `launchpad/README.md` exists alongside `AGENTS.md`. Link rot moves
the failure to resolvability. And "whether or not the restatement is currently accurate" is a
strong rule that will be resisted precisely where restating is most tempting.

### Name the never-invent constraint explicitly in the document

`launchpad/docs/corpus/governance/decision-authority.md:222-224` carries the sharpest local
control: "A MUST here is a restatement of an existing binding rule with its source named, never
a new obligation this node invents." Its authority map then lists each act against the source
that authorizes it, "name[s] the source, not this node, as the authority".

*Interpretation:* this converts A1 from a judgement call into a checkable property. For every
`MUST` in the document, either a source is named or the sentence violates the document's own
opening. A reviewer can check that mechanically-ish without knowing the subject matter.

**Boundary:** it only works where the document genuinely is a restatement. A document that *is*
the first statement of a rule — as `normative-language.md` says of itself — cannot use it, and
that is exactly the document where invention is possible.

### Attribute external requirements visibly (`normative-language.md` MUST 2)

Directly targets D5: a quoted or paraphrased external requirement "**MUST** be visibly
attributed to that source ... and **MUST NOT** be phrased as though this repository's own
process required it." W3C's partition rule is the same discipline applied to sections rather
than sources: mark informative material, and do not use RFC 2119 keywords in it
([W3C Manual of Style](https://www.w3.org/guide/manual-of-style/)).

**Boundary, from the standard itself:** it "has not been applied against a real corpus node or
decision record". It is a designed control with a motivating case, not a tested one.

### Keep the MUST budget

RFC 2119 §6's restraint principle — keywords "must be used with care and sparingly", and "MUST
only be used where it is actually required for interoperation or to limit behavior which has
potential for causing harm" — is the direct countermeasure to C3.

**Boundary, stated candidly in the local standard:** "sparingly" has no bright line, so this is
guidance, not a requirement, and "a reviewer's discretion is the only mechanism". A budget
expressed as a ratio would be worse than nothing, since the census above shows the denominator
is not measurable.

### Keep the human decision gate on normative change

`launchpad/AGENTS.md` §5 rule 1 — "Draft on your own authority. Decide only on a human's" — is
the only local control that addresses *invented authority* rather than invented wording. An
agent may write any rule; it cannot make one binding. §5 rule 4 pairs with it on the enforcement
side: "Never claim a check you did not run ... Paste the command and its raw output."

*Interpretation:* had rule 4 been applied to the DCO sentence — paste the workflow that runs the
check — A2 would have been impossible to write. The rule already exists and reaches the case; it
was simply never applied to a claim inherited from an upstream file rather than freshly authored.
That is worth stating precisely: **inherited text is the blind spot of every "verify your
claims" rule, because nothing about it looks like a claim the current author made.**

**Trade-offs.** The gate is only as good as its scope: `AGENTS.md` itself notes that the quoting
requirement underpinning delegated authority "is the load-bearing part, and it is the part
nothing can check."

### What the evidence says not to rely on

- **Instructing the agent to be accurate.** Measured to make overgeneralization roughly twice as
  likely in the summarization setting (OR = 1.90) ([Peters and Chin-Yee 2025](https://doi.org/10.1098/rsos.241776)).
  Transfer to documentation is inference, but this is the one mitigation with direct evidence
  *against* it, and it is the most commonly proposed.
- **Newer models.** "Newer models tended to perform worse in generalization accuracy than earlier
  ones" (same study). Waiting is not a mitigation.
- **A model-assisted reviewer, unqualified.** An LLM judge inherits the same generalization and
  sycophancy pressures as the author, and sycophancy specifically predicts that a judge shown
  the author's framing will agree with it ([Sharma et al. 2023](https://arxiv.org/abs/2310.13548)).
  This does not make model-assisted review useless; it makes an *independent* judge, blind to
  the author's framing, a different and better instrument than a reviewing pass in the same
  session.

## Limits and open questions

**The central evidence gap.** No study was found that measures normative distortion — modal
force, authority attribution, or claim-mode confusion — in agent-authored *technical
documentation*. Everything quantitative here comes from adjacent settings: medical and
scientific summarization, synthetic deontic-logic items, negation benchmarks,
instruction-following benchmarks, and requirements-engineering defect detection on human-written
requirements. Every transfer to this genre is interpretation and is marked as such at each use.
A reader who needs a rate rather than a mechanism should treat this report as producing
hypotheses, not measurements.

**Preprints and generation gaps.** The agent-context-file study
([arXiv:2511.12884](https://arxiv.org/abs/2511.12884)) is a preprint. Truong et al. tested
models of the GPT-3/InstructGPT generation; the finding that negation is structurally fragile is
used here as a claim about form, not a current per-model rate. Leng et al. tested Llama3-8B and
Mistral-7B. None of these establishes behaviour of the models most likely to author
documentation today.

**The local corpus is an unrepresentative sample, and it cuts both ways.** This repository is
unusually self-instrumented: it has a standard about normative keywords, a schema, a validator,
per-claim evidence ledgers, status markers, and prior research reports on adjacent questions. It
therefore almost certainly **understates** how bad normative distortion is in an ordinary corpus
and **overstates** how visible it is. Two of the three verified local defects (the DCO claim,
the approving-review contradiction) were found because the repository had already documented its
own correction; a corpus without that habit would have yielded neither. Conversely, the
mitigations reported here are drawn from a corpus that adopted them voluntarily, so nothing
below is evidence that they work in a project that has not.

**Provenance of the local defects is not established.** The DCO sentence and the
approving-review sentence are both in agent-maintained files in a repository where agents and
humans both write. `AGENTS.md:438-441` attributes the approving-review error to a **human**
merge-box reading on 2026-08-13. I did not attempt to attribute the DCO sentence to a specific
author, and it should not be read as an agent error. It is used here as evidence about a failure
*shape* — an enforcement claim true in one context and false in another — not about who makes it.

**Counterevidence: the direction is not uniformly upward.** Three qualifications.

- *Over-hedging is also real.* Verbose, caveat-laden output that buries a firm requirement under
  qualifications is a recognized complaint, and hedging language is plausibly reinforced by the
  same preference-based finetuning that reinforces assertiveness. I found no peer-reviewed
  measurement of over-hedging comparable in rigour to Peters and Chin-Yee, so this is recorded
  as a bounded counter-consideration, not a competing finding.
- *Sycophancy makes direction reader-dependent.* Sharma et al. establish belief-matching, not
  force inflation. Under their mechanism, the same agent weakens a rule for one author and
  strengthens it for another. Any mitigation assuming a single direction will miss half the
  cases.
- *Fluent, hedged overgeneralizations still count.* Peters and Chin-Yee note that broadened
  claims "often contained hedges" such as "suggests", "may", "can lead to" — so hedging and
  scope inflation co-occur rather than trading off. A hedge is not evidence that force was
  preserved.

**Counterevidence: humans do this, at scale, and have for decades.** RFC 8174 was published in
2017 to fix a twenty-year misreading of RFC 2119 by human specification authors. Requirements
smells were catalogued in human industrial requirements. NASA, ISO, IETF and W3C each maintain
drafting rules for this failure precisely because it is endemic to human technical writing. The
correct claim is that agents change the *rate, uniformity and reviewability* of the failure, not
that they introduce it. A mitigation programme designed on the assumption that this is an AI
problem will build AI-specific controls for a general one.

**Boundary conditions on the main mechanism claim.** The instruction-hierarchy finding concerns
model *inputs*. Extending it to authored *output* — that an agent which cannot rank input
privilege cannot preserve authority distinctions in what it writes — is my inference. It is the
most load-bearing inference in this report and it is untested. A model could in principle
represent authority well in generation while failing to prioritize it in instruction-following;
nothing here rules that out.

**Open questions.**

1. What is the base rate of force change (`MUST`↔`SHOULD`↔`MAY`, and polarity flips) when an
   agent restructures, summarizes or migrates a normative document? A modal-force diff over a
   corpus's own history would measure this directly, and no such measurement was found.
2. Does the distortion direction correlate with the requester's framing in a documentation
   setting, as sycophancy predicts? This is testable and, if confirmed, would rule out
   artifact-only detection.
3. Do prohibitions (`MUST NOT`) degrade at a higher rate than positive requirements in
   documentation, as the negation literature predicts for reasoning?
4. Does adding a normative-force field to a claim ledger reduce distortion, or merely relocate
   it into a fabricated field value? The local schema cannot answer this today, and the sibling
   review report deliberately declined to prescribe the change.
5. Is a `MUST`:`SHOULD` ratio interpretable at all once metalinguistic uses are excluded, and
   what would a defensible extraction look like?

## Practical review checks

Candidates derived from this research. **Not adopted policy** — offered for a future checklist,
and several restate rules this repository already states for itself.

- For every sentence asserting that a check, gate, hook or CI job enforces a rule, require the
  mechanism to be named and pinned. Then run the search. An enforcement claim is a factual claim
  wearing an instruction's clothes.
- Treat text inherited from another repository, an upstream guide, or a vendored file as
  unverified on arrival, however long it has been present. Truth here is not transitive across
  a fork, a version or an environment.
- For each obligation, require four answers: force, authority, subject and enforcement — with
  "nothing enforces this" a legal answer. Where the honest answer cannot be written, the
  dishonest one will be.
- Diff force tokens across every revision of a normative document, and treat any change of
  keyword, polarity or count as requiring an explanation in the same change.
- Read prohibitions twice. `MUST NOT` is the least stable form under restatement, and its
  softened version ("avoid", "prefer") is the most fluent continuation.
- When a paraphrase describes another document's scope, compare it against the scope that
  document claims for itself. "For this repository" and "for corpus nodes and decision records"
  are different documents' rules.
- Ask whether the sentence would still bind if the adjacent example, rationale or note were
  deleted. If deleting informative material changes what conformance requires, the boundary is
  false.
- Separate "required" from "implemented" from "observed" at the granularity of the claim, not of
  the section. A status marker that covers a section does not cover a row added later.
- Never report a passing schema or link validation as evidence that a document's rules are
  correct, authorized, or enforced. State what the green run covered.
- Treat a keyword census as a review queue and say so wherever it is reported. Candidate counts
  include quotations, headings and discussion *about* the keywords.
- When a fact is corrected, search the corpus for obligations derived from the old fact. The
  correction does not propagate to them, and the derived requirement is where the harm lives.
- Distrust "be accurate" as a control. It is the one mitigation with direct measured evidence
  against it, and it is the one most likely to be proposed.
- Where a rule was changed at a reader's or requester's suggestion, record who asked. Sycophantic
  force change leaves no other trace.

## References

### Local repository evidence

At revision `70d2cb38a3aa8075bfce61cb45318db98f1731b0`, branch `topic-09-normative-distortion`,
inspected 2026-09-08 and 2026-09-09. This worktree is a **sparse checkout**;
`.github/workflows/` and `launchpad/decisions/` are tracked but absent from disk and were read
with `git show HEAD:<path>`.

- `launchpad/AGENTS.md` — the fork's normative spec. §5 rules 1 and 4 (draft/decide boundary;
  never claim an unrun check); §6 line 380 (the DCO enforcement claim); §6 lines 436–441 (the
  branch-protection measurement of 2026-08-28 and the retraction of the "two approving reviews"
  figure); the four never-deferrable prohibition classes.
- `launchpad/README.md` — lines 8–10 (AGENTS.md wins on disagreement; "fix the drift"); line 123
  ("the DCO check is not optional"); line 124 ("two approving reviews"), still stated at HEAD.
- `CLAUDE.md:147` and `AGENTS.md:147` (repository root, upstream `block/buzz`) — the same DCO
  sentence, true in its own context.
- `.github/workflows/` — 31 tracked files at HEAD; zero occurrences of `\bdco\b` or
  `signed-off-by`; one substring hit inside "hardcoded".
- `launchpad/VISION.md` — the four-marker claim-status system, the "a proposal presented as a
  decision is worse than no document at all" rationale, and the non-inheritance warning for
  section-level markers.
- `launchpad/docs/corpus/standards/normative-language.md` — the local BCP 14 adoption; MUST 1–5;
  the SHOULD-class restraint guidance; "**Enforced mechanically: nothing**"; the disclosed
  authority boundary into `launchpad/decisions/`; the "expected but not verified" list.
- `launchpad/docs/corpus/governance/decision-authority.md` — the never-invent clause
  (lines 222–224); the authority map naming sources rather than itself; the superseded-ADR
  warning (lines 216–218); the scope-widening paraphrase at lines 221–222.
- `launchpad/docs/corpus/governance/ownership.md:120,124` — an accurate restatement of the same
  scope, and `corpus-standard-linking` MUST 5 on restatement as a defect.
- `launchpad/docs/corpus/governance/maintainers.md` — "It does not invent a maintainer policy the
  fork has not adopted."
- `launchpad/docs/corpus/templates/invariant.md:85` — a rule from an unmerged PR branch recorded
  as `TEAM_KNOWLEDGE` with the PR named, rather than asserted.
- `launchpad/docs/corpus/schema/node.schema.json` — seven permitted front-matter keys;
  `additionalProperties: false`; `entry_class` enum `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`.
- `launchpad/project-intelligence/corpus/validate.py` — 936 lines, zero lines matching
  `MUST|SHOULD|MAY|normative`.
- Corpus census at HEAD — 374 markdown files, 371 with `id:` front matter, 128 containing at
  least one capitalized keyword; keyword and `entry_class` counts as tabulated above.
- [`launchpad/Research/354-dco-check-on-vendor-drops.md`](../../354-dco-check-on-vendor-drops.md)
  (established 2026-08-22) — no DCO check runs in this fork; the scan of 40 pull requests; the
  stated limits (could not enumerate installed GitHub Apps; inference from absence).
- [`launchpad/Research/documentation-corpus-review/09-normative-versus-descriptive-technical-writing.md`](../09-normative-versus-descriptive-technical-writing.md)
  (researched 2026-09-07) — the sibling corpus-review report on the same conceptual ground, from
  the reviewer's side: the five distinctions, the convention comparison, its own fifteen failure
  modes, and its 2026-09-07 corpus scan (205 nodes / 896 tokens) which this report's differently
  scoped scan does not reproduce.

### External sources

- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/rfc/rfc2119.txt)
  — Scott Bradner, BCP 14, March 1997. Definitions of MUST/SHOULD/MAY and §6's restraint rule
  ("must be used with care and sparingly ... MUST only be used where it is actually required for
  interoperation or to limit behavior which has potential for causing harm"). Supports C3 and the
  MUST-budget mitigation.
- [RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://www.rfc-editor.org/rfc/rfc8174.txt)
  — Barry Leiba, BCP 14, May 2017. "The words have the meanings specified herein only when they
  are in all capitals"; "normative text does not require the use of these key words". Supports
  the counterevidence that this is a long-standing human failure, and the claim that keyword
  presence/absence is not evidence of authority.
- [W3C Manual of Style](https://www.w3.org/guide/manual-of-style/) — W3C (retrieved 2026-09-08).
  Informative sections must say so and avoid RFC 2119 keywords; figures, examples and notes are
  assumed informative and "must not" be made normative. Supports failure class A4 and the
  partition mitigation.
- [Google developer documentation style guide — word list](https://developers.google.com/style/word-list)
  — Google (retrieved 2026-09-08). `must` for a required action; `may` reserved "for official
  policy or legal considerations"; `can` for permission; `might` for possibility. Used only as
  evidence that a conflicting convention exists. The frequently repeated claim that the guide
  advises against `should` was **not** confirmed by this retrieval and is not relied on.
- [Generalization bias in large language model summarization of scientific research](https://doi.org/10.1098/rsos.241776)
  — Uwe Peters and Benjamin Chin-Yee, *Royal Society Open Science* 12(4):241776, 30 April 2025
  (peer-reviewed; open access at [PMC12042776](https://pmc.ncbi.nlm.nih.gov/articles/PMC12042776/)).
  4,900 summaries, 10 models, expert human baseline; OR 4.85 versus human summaries; accuracy
  prompt OR 1.90; newer models worse; descriptive-to-prescriptive conversion as one of three
  coded mechanisms. The primary quantitative support for C1, C2 and the anti-mitigation finding.
- [Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548)
  — Mrinank Sharma, Meg Tong, Tomasz Korbak, Ethan Perez et al. (Anthropic), arXiv:2310.13548,
  v1 October 2023, current v4 May 2025. Five assistants, four free-form tasks; preference data
  favours belief-matching; humans and preference models prefer convincing sycophantic responses
  over correct ones. Supports the reader-dependent direction of force change.
- [Taming Overconfidence in LLMs: Reward Calibration in RLHF](https://arxiv.org/abs/2410.09724)
  — Jixuan Leng, Chengsong Huang, Banghua Zhu, Jiaxin Huang, arXiv:2410.09724, October 2024,
  revised February 2025; PPO-M/PPO-C evaluated on Llama3-8B and Mistral-7B across six datasets.
  RLHF "tends to lead models to express verbalized overconfidence"; PPO reward models biased
  toward high-confidence responses. Supports assertiveness inflation as a training-side mechanism.
- [The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/html/2404.13208v1)
  — Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, Alex Beutel (OpenAI),
  arXiv:2404.13208, 19 April 2024. "existing LLMs lack this capability" of treating system, user
  and third-party text separately; system prompts treated at the same priority as untrusted
  input. The primary support for the no-native-authority mechanism and failure class D6.
- [Language models are not naysayers: an analysis of language models on negation benchmarks](https://aclanthology.org/2023.starsem-1.10/)
  — Thinh Hung Truong, Timothy Baldwin, Karin Verspoor, Trevor Cohn, \*SEM 2023, pp. 101–114.
  Insensitivity to negation, failure to reason under negation. Supports failure class B2.
- [Normative Reasoning in Large Language Models: A Comparative Benchmark from Logical and Modal Perspectives](https://aclanthology.org/2025.blackboxnlp-1.17/)
  — Kentaro Ozeki, Risako Ando, Takanobu Morishita, Hirohiko Abe, Koji Mineshima, Mitsuhiro
  Okada, BlackboxNLP Workshop, November 2025. LLMs "exhibit notable inconsistencies in specific
  types of normative reasoning" relative to structurally matched epistemic reasoning, with
  human-like cognitive biases. Supports the claim that deontic modality is handled less reliably
  than its epistemic counterpart, on synthetic items.
- [FollowBench: A Multi-level Fine-grained Constraints Following Benchmark for Large Language Models](https://aclanthology.org/2024.acl-long.257/)
  — Yuxin Jiang, Yufei Wang, Xingshan Zeng et al., ACL 2024. Five constraint types; a multi-level
  mechanism adding one constraint per level; 13 closed- and open-source models; the abstract
  concludes that the evaluation highlights "the weaknesses of LLMs in instruction following" and
  states no per-level figure. Supports constraint difficulty as a mechanism for B1, with the
  boundary that it measures obeying rather than preserving constraints.
- [Rapid quality assurance with Requirements Smells](https://arxiv.org/abs/1611.08847)
  — Henning Femmer, Daniel Méndez Fernández, Stefan Wagner, Sebastian Eder; arXiv:1611.08847
  (author version, November 2016), published in *Journal of Systems and Software* 123:190–213,
  [doi:10.1016/j.jss.2016.02.047](https://doi.org/10.1016/j.jss.2016.02.047). Smell catalogue
  transferring code smells to Requirements Engineering; the Smella prototype evaluated in three
  industrial and one university context; "average precision of 59% at an average recall of 82%
  with high variation"; smells offered "as a supplement to reviews". Supports B3 and the
  detection-limits discussion, and is counterevidence that these defects are AI-specific.
  **The ScienceDirect page of record returned HTTP 403 on 2026-09-09; the quotations above are
  from the arXiv author version's abstract.**
- [Agent READMEs: An Empirical Study of Context Files for Agentic Coding](https://arxiv.org/abs/2511.12884)
  — Worawalan Chatlatanagulchai, Hao Li, Yutaro Kashiwa et al., arXiv:2511.12884, November 2025,
  revised August 2026 (**preprint, not peer-reviewed**). 2,303 context files from 1,925
  repositories; files "evolve like configuration code"; security (14.8%) and performance (14.5%)
  rarely specified. Supports D6's context: the normative instruction genre is large, fast-moving,
  and thin on guardrails.
