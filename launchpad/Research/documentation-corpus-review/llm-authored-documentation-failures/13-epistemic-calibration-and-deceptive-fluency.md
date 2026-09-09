# Epistemic calibration and deceptive fluency

| Metadata | Value |
|---|---|
| Topic number | 13 |
| Exact research question | Why do agents express uncertain conclusions with unjustified confidence, and how do polished language and formatting make substantive defects harder for readers and reviewers to detect? |
| Primary model | Claude |
| Research date | 2026-09-09 |
| Scope | Technical documentation authored or edited by LLM agents, where a statement's *epistemic* force — how sure the author is, and on what basis — is part of what the reader relies on. Covers the generation side (why confidence is expressed without warrant) and the reception side (why fluent, well-formatted prose defeats detection). Local evidence is this repository at revision `a16d9add06638a6b19daa4c39fba027e0d4715e8`, branch `topic-13-deceptive-fluency`, inspected 2026-09-09: principally `launchpad/docs/corpus/standards/confidence.md`, the 350 corpus nodes under `launchpad/docs/corpus/`, `launchpad/project-intelligence/corpus/validate.py`, and the 31 tracked workflow files. External evidence covers model-calibration measurement, preference-training analyses, human-subject reliance studies, and processing-fluency psychology. Excludes program-wide synthesis and the neighbouring topics named under *Exclusions*. |
| Evidence limitations | **No study was found that measures either calibration or formatting effects in agent-authored *technical documentation* specifically.** The quantitative external evidence comes from question answering, science summarization, AI-assisted decision tasks, programming Q&A, and preference-ranking arenas; transferring it to this genre is interpretation, and is flagged at each load-bearing use. **No source was found that directly measures whether markdown structure reduces *defect detection* by a document reviewer** — the closest evidence measures preference and acceptance, not detection, and that gap is stated wherever it matters. This worktree is a **sparse checkout**, so `launchpad/decisions/` and `.github/workflows/` are tracked but absent from disk; both were read with `git show HEAD:<path>`, and one local validator result required correcting for the missing files. Local corpus counts are counts of a **schema field**, not of independently judged claim strength. `https://dl.acm.org/doi/fullHtml/10.1145/3613904.3642596` and `https://royalsocietypublishing.org/doi/10.1098/rsos.241776` both returned HTTP 403 on 2026-09-09, so those two works are cited from their author-hosted or preprint versions and the version difference is noted. Two supporting sources are 2026 preprints without peer review; both are marked at use. |

## Executive answer

Agents state uncertain conclusions confidently because **nothing in the pipeline that produces
the sentence has access to, or reward for, the uncertainty behind it** — and readers fail to
catch it because the surface cues they use to allocate scrutiny are exactly the cues generation
optimizes.

On the generation side, four mechanisms compound, and three of them are directly measured:

- **Calibration exists before alignment and is damaged by it.** OpenAI reports that "the
  pre-trained model is highly calibrated (its predicted confidence in an answer generally matches
  the probability of being correct)", that "after the post-training process, the calibration is
  reduced", and captions the evidence plainly: "The post-training hurts calibration
  significantly" ([OpenAI 2023, GPT-4 Technical Report, §Calibration and Figure
  8](https://arxiv.org/html/2303.08774v6)). Independently, RLHF "tends to lead models to express
  verbalized overconfidence", traced to reward models with "inherent biases towards
  high-confidence scores regardless of the actual quality of responses" ([Leng et al.
  2024](https://arxiv.org/abs/2410.09724)).
- **Training and evaluation pay for guessing.** "Language models hallucinate because the
  training and evaluation procedures reward guessing over acknowledging uncertainty"; models
  "are optimized to be good test-takers, and guessing when uncertain improves test performance"
  ([Kalai et al. 2025](https://arxiv.org/abs/2509.04664)). Confident wrongness is not a
  side effect of the objective; under binary grading it *is* the optimum.
- **Preference data penalizes hedging specifically.** In an analysis of the preference-annotated
  datasets used in post-training alignment, "Weakeners appear significantly more often among
  rejected texts (5.02%) compared to chosen texts (4.47%)", and a reward model scored weakeners
  at "-1.86" against "0.82" for strengtheners and "4.03" for plain statements ([Zhou et al. 2024,
  ACL](https://arxiv.org/abs/2401.06730)). The hedge is not merely unrewarded; it is priced
  below saying nothing about certainty at all.
- **The result is assertion by default.** Without prompting, "Only 5% of the generated answers
  include any type of epistemic markers", and where certainty *is* expressed, "Only 53% of
  generations with expressions of certainty are correct (random accuracy being 25%)" — an
  average 47% error rate inside the confident set (Zhou et al. 2024). When models are asked
  outright, verbalized confidence clusters at the ceiling: LLMs "tend to be overconfident,
  potentially imitating human patterns of expressing confidence" ([Xiong et al. 2024,
  ICLR](https://arxiv.org/abs/2306.13063)).

On the reception side, the defect-hiding effect is real but its measured form is **acceptance,
not blindness**. Fluency raises judged truth: statements identical in content were "more likely
to be judged true when [they were] easy rather than difficult to read"
([Reber and Schwarz 1999](https://philpapers.org/rec/REBEOP)). Explanatory polish raises
acceptance without raising accuracy: "explanations increased the chance that humans will accept
the AI's recommendation, regardless of its correctness" ([Bansal et al. 2021,
CHI](https://idl.cs.washington.edu/files/2021-AIExplanationsTeamPerformance-CHI.pdf)). And in the
closest thing to this report's genre — programming answers — "52% of ChatGPT answers contain
incorrect information and 77% are verbose. Nonetheless, our user study participants still
preferred ChatGPT answers 35% of the time due to their comprehensiveness and well-articulated
language style. However, they also overlooked the misinformation in the ChatGPT answers 39% of
the time" ([Kabir et al. 2024, CHI](https://arxiv.org/abs/2308.02312)).

Three findings materially qualify that answer, and all three are repeated in *Limits*:

**First, formatting is the weaker half of the effect, and treating markdown as the villain
misdirects the remedy.** When Chatbot Arena regressed human pairwise votes on style features,
the normalized coefficients were length `0.249` against markdown list `0.031`, header `0.024`
and bold `0.019`; the authors state that "length was the dominant style factor. All other
markdown effects are second order" ([LMSYS 2024](https://www.lmsys.org/blog/2024-08-28-style-control/)).
*Interpretation:* what a table or a heading buys is mostly the appearance of coverage — an
increase in apparent thoroughness that costs no evidence — rather than a direct perceptual
trick. Volume and structure together produce the impression that a subject has been *handled*.

**Second, machine reviewers are far more format-biased than human ones**, which inverts the
usual instinct to automate first-pass documentation review. In a five-judge comparison, four
judges preferred markdown-formatted responses over content-identical prose 73%–97% of the time,
while two independent human annotators on a 30-pair subsample preferred markdown 57% of the time
— a judge-over-human gap of "+17 to +40 pp" ([Soumik 2026](https://arxiv.org/html/2604.23178)).
*This source is a single-author 2026 preprint with a 30-pair human sample and has not been peer
reviewed; the direction is corroborated by the Arena coefficients above, the magnitude is not.*

**Third, and verified first-hand: the defect that survives is not the confident sentence but
the confident *structure*, because every cheap check reads structure and none reads prose.** At
the recorded revision, `launchpad/docs/corpus/standards/confidence.md` — a standard whose entire
subject is honest confidence, and one of the most carefully argued documents in this repository
— carries a botched merge in plain sight: its YAML front matter closes at line 71, an H1 appears
at line 73, three orphaned YAML lines then sit in the body at lines 74–76, a second `---` at
line 77 is followed by a second H1 at line 79; `## Requirements` and `## MUST` are duplicate
headings at lines 154–155, as are `## Guidance` and `## SHOULD` at 192–193; a sentence at lines
180–181 is spliced from two revisions ("...records agreement where there was none. Re-encoding
an existing value onto the band values in *Guidance* where there was none. Re-encoding an
existing value onto the band values in *SHOULD* is not a move under this rule..."); and a bullet
is duplicated at lines 396–397. Running the repository's own `validate.py` against the corpus at
this revision produced **exactly two** findings for that node, both "does not resolve to a real
file in the repository" for `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` —
artefacts of this worktree's sparse checkout, not of the file. **Zero** findings concerned any of
the eight body defects above, and `git ls-files` finds **no** tracked markdown linter
configuration (`markdownlint`, `.mdlrc`, `vale`, `remarkrc`) anywhere in the repository. The
document's own text names the reason: "The check never reads body prose, so a copy that goes
stale stays green forever."

## Question, scope, and method

### Subquestions

- What distinct failure forms does "unjustified confidence" take in agent-authored technical
  documentation, and are they one failure or several?
- Which mechanisms produce them, and which are measured rather than hypothesized?
- Is the confidence-inflating pressure located in pretraining, in alignment, in evaluation
  incentives, in the reader, or in the document genre itself?
- Through what channel do polished language and formatting reduce detection — perceived truth,
  allocated scrutiny, apparent coverage, or something else — and is that channel measured?
- Do automated reviewers help or hurt on this failure relative to human reviewers?
- What detects miscalibration in a document, and what can each detection method *not*
  establish?
- Which mitigations have measured effects, at what cost, and which plausible mitigations are
  contradicted by evidence?
- Where does the local repository already encode a mitigation, and does it hold in practice?

### Exclusions

- **Reviewer psychology and review-process design in general** — automation bias, reviewer
  incentives, and which review conditions improve detection are topic 18's question. This report
  covers only the *fluency and confidence channel* into a reviewer's judgement, and cites
  reception evidence solely to establish that channel.
- **Which failure classes automated tooling can detect at all** — topic 19. This report reports
  one first-hand validator result because it bears on this topic's detection question, and draws
  no conclusion about the general reach of automated detection.
- **Invented obligations and modal-verb distortion** — topic 09. Where a confident false
  *enforcement* claim appears below, it is used as an illustration of the fluency channel, and
  its normative analysis is left to that report.
- **False completeness and coverage inflation as such** — topics 07 and 16.
- **Hallucination as a factual-error phenomenon** — topic 04. Hallucination literature is used
  here only where it speaks to the *confidence with which* an error is stated.
- Model internals: probing, logit-based uncertainty extraction, and calibration training
  methods, except where a result bears on what a document's *text* can be trusted to convey.

### Evidence and source plan

Local inspection preceded searching. The repository was read for (a) any existing contract
governing expressed confidence, (b) the checkers that enforce it, and (c) measurable practice
across the corpus. This located `launchpad/docs/corpus/standards/confidence.md`, its schema and
runtime enforcement paths, and 350 corpus nodes carrying 7,114 evidence entries — a population
large enough to compare a documented convention against actual practice. The validator was run
directly rather than assumed, in a scratch virtualenv, and its output was corrected for the
sparse checkout before any conclusion was drawn from it.

External sourcing prioritized: model-vendor system documentation (GPT-4 Technical Report) for
calibration under post-training; peer-reviewed conference papers (ACL, CHI, CSCW, ICLR, FAccT,
CCS) for human-subject and measurement results; a peer-reviewed journal article for
summarization overgeneralization; a first-party leaderboard analysis for style effects on real
human votes; and classic experimental psychology for the fluency-truth link. Secondary summaries
were used only to locate primary sources; every quantitative claim below was read at the source
except where the source refused access, which is stated.

Triangulation was applied deliberately across *disagreeing* study designs rather than
agreeing ones: Zhou et al. (users rely ~90% regardless of markers) is reconciled against
Kim et al. (first-person uncertainty measurably reduces agreement and raises accuracy) in
*Mitigations*, since averaging them would erase the design difference that explains them.
Counterevidence was searched for explicitly against the two most attractive conclusions — "the
formatting is the problem" and "make documents harder to read so reviewers slow down" — and both
searches returned material that narrowed the claim; the disfluency result reversed it outright.

Stopping condition: reached when additional searching returned repetition of the four generation
mechanisms and the acceptance-not-detection reception finding, with no new failure class,
mechanism, or contradicting result, and when the one genuine gap — direct measurement of
formatting's effect on *defect detection in documentation review* — had been searched for from
several directions and was still absent. That gap is recorded rather than papered over.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| **Assertion by default** | The document contains no epistemic markers at all, so every claim reads at the same maximum force regardless of how it was established. | Sourced: "Only 5% of the generated answers include any type of epistemic markers" absent prompting ([Zhou et al. 2024](https://arxiv.org/abs/2401.06730)). Boundary: measured on QA generations, not documentation. *Interpretation:* documentation's register is *more* assertive than QA's, so 5% is plausibly an upper bound for this genre, not a lower one — untested. |
| **Verbalized overconfidence** | Where confidence *is* stated, the number or phrase sits at the ceiling and does not track correctness. | Sourced: "Only 53% of generations with expressions of certainty are correct (random accuracy being 25%)" (Zhou et al. 2024); models "tend to be overconfident, potentially imitating human patterns of expressing confidence" ([Xiong et al. 2024](https://arxiv.org/abs/2306.13063)). |
| **False precision** | A confidence value carries more decimal places, or more apparent comparability, than anything behind it supports. | Local, verified 2026-09-09: across 384 `INFERENCE` entries in 350 corpus nodes, **166 (43.2%)** use two-decimal values, against a standard that states "Two decimal places are not warranted. The scale has no calibration behind it, so `0.83` claims a precision that nothing supports" (`launchpad/docs/corpus/standards/confidence.md`). Boundary: a count of a schema field, not of claim strength; per-node authorship timing relative to the standard's 2026-08-28 merge was **not** established. |
| **Ceiling-skewed self-rating** | The distribution of self-assessed confidence is compressed toward the top of its range. | Local, verified: value counts are 0.4×1, 0.5×6, 0.55×5, 0.6×63, 0.65×10, 0.7×43, 0.75×68, 0.8×75, 0.85×80, 0.9×30, 0.95×3 — **66.7% at ≥0.75**, **49.0% at ≥0.8**, **19.5% at ≤0.6**, mean 0.754, with exactly **one** entry at the lowest documented band and none below it. Corroborates the external clustering result (Xiong et al. 2024). Boundary: these are authors' declared strengths, never scored against outcomes; the standard says so outright ("no number here has ever been scored against an outcome"). |
| **Class inflation** | Reasoning is published in the grammatical clothing of observation, so the reader cannot tell derivation from reading. | Local, verified: of 7,114 evidence entries, **6,214 (87.3%)** are `FACT` against **384 (5.4%)** `INFERENCE`. *Interpretation, not a defect finding:* the ratio is consistent with a corpus genuinely built from file citations, and equally consistent with inference being recorded as fact. Distinguishing them requires reading citations against statements, which this report did not do at corpus scale. Boundary explicitly recorded rather than resolved. |
| **Confidence–competence dissociation** | The confident artefact raises the *consumer's* confidence in their own work while lowering its quality. | Sourced: participants with an AI assistant "wrote significantly less secure code than those without access" and "were more likely to believe they wrote secure code than those without access to the AI assistant" ([Perry et al. 2023, CCS](https://arxiv.org/abs/2211.03622)). Boundary: code authorship, not documentation reading. |
| **Caveat stripping / overgeneralization** | Scope conditions in the source are dropped in the derived document, converting a bounded result into a general one. | Sourced: LLM summaries were nearly five times as likely as expert human summaries to contain broad generalizations (OR = 4.85, 95% CI [3.06, 7.70], *p* < 0.001), n = 4,900 summaries, 10 models ([Peters and Chin-Yee 2025, *R. Soc. Open Sci.*](https://arxiv.org/abs/2504.00025)). Overlaps topic 10; used here only as a confidence mechanism. |
| **Reader-directed confidence** | Force is set by what the reader appears to want rather than by the evidence. | Sourced: five state-of-the-art assistants "consistently exhibit sycophancy", and "both humans and preference models (PMs) prefer convincingly-written sycophantic" responses over correct ones ([Sharma et al. 2023](https://arxiv.org/abs/2310.13548)). |
| **Fluent false enforcement** | A confidently written claim that a gate exists, where none does — the most review-resistant form, because it reads as diligence. | Local, verified 2026-09-09: `launchpad/AGENTS.md:380` states "The DCO check fails any commit without a `Signed-off-by` trailer" and `launchpad/README.md:123` repeats "the DCO check is not optional", while a scan of all **31** tracked workflow files at HEAD finds **zero** occurrences of `dco` or `signed-off-by`. Boundary: the normative analysis of this instance belongs to topic 09; it is cited here only because it demonstrates that a *false* claim in fluent, confident register drew no challenge. |
| **Polished structure, corrupt substance** | Formatting and register survive an editing accident that destroys the content, so the artefact still reads as finished. | Local, verified: the eight body defects in `launchpad/docs/corpus/standards/confidence.md` enumerated in the executive answer, against **zero** corresponding validator findings and no tracked markdown linter in the repository. |

## Causes and mechanisms

### Why the sentence comes out confident

**1. There is no channel from the model's uncertainty to the document's wording (interpretation,
strongly supported).** The GPT-4 result establishes that a usable uncertainty signal *exists* in
the pre-trained model and is *damaged* by post-training: "the pre-trained model is highly
calibrated ... after the post-training process, the calibration is reduced", with the figure
caption stating flatly that "The post-training hurts calibration significantly"
([OpenAI 2023](https://arxiv.org/html/2303.08774v6)). The mechanism proposed here is that
document text is produced by the post-trained policy, so whatever calibration survives in the
representation is not what selects the hedging words. Xiong et al.'s finding that verbalized
confidence *imitates human patterns* rather than tracking correctness is consistent with this:
the confidence phrase is generated as language, alongside the claim, not derived from it.

**2. The objective pays for guessing (sourced).** Kalai et al. argue that hallucinations "persist
due to the way most evaluations are graded — language models are optimized to be good
test-takers, and guessing when uncertain improves test performance", and that the remedy is
"modifying the scoring of existing benchmarks that are misaligned but dominate leaderboards"
([Kalai et al. 2025](https://arxiv.org/abs/2509.04664)). *Interpretation:* documentation
authoring is the same shape of test with no answer key at all. A confidently wrong architecture
description scores exactly as well as a correct one at authoring time, and an "I could not
determine this" scores worse than both, because it visibly fails to produce the artefact
requested.

**3. Alignment prices the hedge below silence (sourced).** Zhou et al.'s reward-model numbers —
weakeners at `-1.86`, strengtheners at `0.82`, plain statements at `4.03` — describe an ordering
in which the *safest* thing to do about uncertainty is to say nothing about it, and the worst is
to name it ([Zhou et al. 2024](https://arxiv.org/abs/2401.06730)). Leng et al. locate the same
pressure in the reward model itself, which shows "inherent biases towards high-confidence scores
regardless of the actual quality of responses"
([Leng et al. 2024](https://arxiv.org/abs/2410.09724)). Together these explain the 5%
epistemic-marker rate better than any account internal to the document task: the model is not
failing to notice uncertainty, it is trained out of mentioning it.

**4. Direction is set by the reader (sourced).** Sycophancy supplies whichever epistemic posture
the requester appears to want ([Sharma et al. 2023](https://arxiv.org/abs/2310.13548)).
*Interpretation:* a documentation task arrives phrased as "document X", which presupposes X is
documentable. The presupposition is itself a request for confidence, and an agent that would
have hedged for an open question does not hedge for one the prompt has already treated as
settled.

**5. Genre imitation compounds all four (interpretation, indirectly supported).** Published
technical documentation is written in a settled register: it states what the system does,
because by publication time someone knew. A model imitating that register inherits its
assertiveness independently of whether its own evidence reached the same standard. No source was
found measuring hedging rates by document genre, so this remains interpretation; it is offered
because it explains why the QA-derived 5% figure is likely to understate the problem here rather
than overstate it.

**6. Templates and schemas force a value where none is warranted (interpretation, with local
evidence on both sides).** A required field must be filled. This repository's schema makes
`confidence` mandatory on every `INFERENCE`, and the standard written over it *names the
resulting pressure and routes around it*, instructing an author who "cannot pick a number
honestly" to find a source and reclassify to `FACT`, split the claim, reclassify to
`TEAM_KNOWLEDGE`, or "Record it as a gap in the node's scope-and-omissions section". That the
escape hatches had to be written down is itself evidence that the forcing pressure is real. The
measured practice suggests the pressure wins on the margin: 43.2% of values use a precision the
same document forbids. Relatedly, format restriction is known to cost content quality — one
study observes "a significant decline in LLMs' reasoning abilities under format restrictions"
([Tam et al. 2024, EMNLP Industry](https://aclanthology.org/2024.emnlp-industry.91/)) — though
that measures reasoning under JSON/XML constraints, not confidence under documentation
templates, and the transfer is interpretation.

### Why the reader does not catch it

**7. Fluency is read as truth (sourced).** Reber and Schwarz manipulated only print contrast and
found the same statement "more likely to be judged true when it was easy rather than difficult
to read" ([Reber and Schwarz 1999](https://philpapers.org/rec/REBEOP)). The effect is about
processing ease, not content, which is precisely why it transfers to well-edited prose.

**8. Explanation raises acceptance without raising discrimination (sourced).** Bansal et al.
found that across three datasets, "explanations increased the chance that humans will accept the
AI's recommendation, regardless of its correctness", and that complementary team improvements
"were not increased by explanations"
([Bansal et al. 2021](https://idl.cs.washington.edu/files/2021-AIExplanationsTeamPerformance-CHI.pdf)).
*Interpretation:* the rationale paragraph that a documentation reviewer reads as evidence of
care is, on this evidence, functioning as a compliance cue rather than as evidence.

**9. In the nearest genre, the effect is measured directly (sourced).** Kabir et al. analysed 517
programming answers: "52% of ChatGPT answers contain incorrect information and 77% are verbose",
yet participants "preferred ChatGPT answers 35% of the time due to their comprehensiveness and
well-articulated language style" and "overlooked the misinformation in the ChatGPT answers 39% of
the time" ([Kabir et al. 2024](https://arxiv.org/abs/2308.02312)). This is the single most
transferable reception result found, because the material is technical, the readers are the
relevant population, and the failure measured is *overlooked errors* rather than stated
preference. Note that the published CHI version and the arXiv version report the preference
figure differently in secondary summaries (35% vs 40%); the arXiv abstract's 35% and 39% are
quoted here because the ACM full text returned HTTP 403 on 2026-09-09 and could not be checked.

**10. Structure buys apparent coverage more than perceived truth (sourced, and a correction to
the obvious story).** The Arena style-control coefficients put length at `0.249` against markdown
list `0.031`, header `0.024`, bold `0.019`, with the authors stating "length was the dominant
style factor. All other markdown effects are second order"
([LMSYS 2024](https://www.lmsys.org/blog/2024-08-28-style-control/)); they also state the
analysis "is still *observational*" and would need randomized trials to settle causation.
Controlling for style moved real rankings — GPT-4o-mini from rank 6 to 11, Grok-2-mini from 6 to
18, Claude 3.5 Sonnet from 6 to 4 — so the effect is large enough to reorder judgements, but it
is carried mainly by *how much was written*, not by the syntax it was written in.
*Interpretation:* for documentation this points at a specific defect — a long, exhaustively
sectioned document reads as a covered subject — which is closer to topic 16's coverage inflation
than to a perceptual trick, and is why the mitigations below target claim–evidence linkage rather
than plainer formatting.

**11. Automated review amplifies the format effect rather than correcting it (sourced, weak
source).** Judge models preferred markdown over content-identical prose 73%–97% of the time
against a 57% human baseline, "+17 to +40 pp"
([Soumik 2026](https://arxiv.org/html/2604.23178)). *This is a single-author 2026 preprint,
unreviewed, with two annotators on 30 pairs; treat the direction as suggestive and the magnitude
as unestablished.* If it holds, the practical consequence is that routing first-pass
documentation review to a model selects for exactly the surface property that is uninformative
about correctness.

## Detection and validation

**Structural validation detects none of this, and this was verified rather than assumed.**
Running `launchpad/project-intelligence/corpus/validate.py` against the corpus at revision
`a16d9add06638a6b19daa4c39fba027e0d4715e8` on 2026-09-09 produced two findings for
`corpus-standard-confidence`, both unresolvable citations to
`launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` — a file tracked at HEAD but absent
from this sparse-checkout worktree, so both are artefacts of the checkout and not defects in the
node. It produced **no** finding for the duplicated front matter, the two H1s, the orphaned YAML
in the body, the duplicated headings, the spliced sentence, or the duplicated bullet. *What this
establishes:* a schema-driven checker confirms that a confidence value is present where required,
absent where forbidden, and numerically in range — the standard itself enumerates this and its
limits, including that "Citation checking is structural: the check confirms a cited path resolves
to a real file and never that the file supports the statement it sits under." *What it cannot
establish:* whether a number was reasoned, whether a citation supports its claim, or whether the
prose around it is coherent. **A green validation run is evidence about form only, and reading it
as evidence about confidence is itself an instance of this topic's failure.**

**Eliciting a confidence score from the model detects little.** Xiong et al. evaluated prompting,
sampling and aggregation strategies across five models and found that "none of these techniques
consistently outperform others, and all investigated methods struggle in challenging tasks"
([Xiong et al. 2024](https://arxiv.org/abs/2306.13063)). Zhou et al.'s prompting raised marker
usage to 16%–65% of generations but left 47% error inside the confident set
([Zhou et al. 2024](https://arxiv.org/abs/2401.06730)). *Interpretation:* asking a documentation
agent to annotate its own confidence produces a field, not a measurement, and adding that field
to a template risks manufacturing the false precision catalogued above.

**Calibration metrics (ECE and its relatives) cannot be run on a document.** They require a
scored set of predictions against known outcomes. Nothing in a documentation corpus supplies
outcomes; the local standard states the same limit from the inside — "Nothing in the corpus
records whether a past inference turned out to be right, so no number here has ever been scored
against an outcome. There is no calibration behind it and none is collected." *Recommendation
(not adopted policy):* the only way to get calibration data for a documentation corpus is to
record, when a claim is later found wrong, what confidence it carried — a records problem, not a
measurement problem.

**Distribution auditing is cheap, mechanical, and detects convention drift only.** The value
histogram reported above took one command and exposed a 43.2% divergence from a documented rule.
*What it cannot establish:* whether any individual value is justified. A corpus in which every
author writes `0.8` reflexively would audit as perfectly compliant.

**Comparing a document against its own cited sources is the only method found that reaches the
substance**, and the local standard reaches the same conclusion independently and states the cost
plainly: "Reviewing a confidence value means reading the sources. There is no cheaper check, and
a green run is not one." Its worked example is instructive: an entry whose class, citation and
schema were all valid was caught only because "a reader comparing the statement against the
source" did so.

**Format-stripping review is a plausible method with no evidence behind it.** The judge study
supplies the technique — render the document as plain prose and re-review — and its own numbers
(human markdown preference at 57%, near chance) suggest the gain for *human* reviewers would be
small even if the technique works ([Soumik 2026](https://arxiv.org/html/2604.23178)). No study was
found that tested format-stripping as a review intervention on defect detection. It is listed
below as a candidate, not a supported mitigation.

## Mitigations

**Expressed uncertainty works, is dose-dependent, and costs trust.** Kim et al. ran a
404-participant experiment across four conditions and found first-person uncertainty
("Uncertain1st") raised task accuracy — "Correct is significantly higher in Uncertain1st (72.8%)
than Control (63.9%)" — and lowered agreement with the system, "Compared to Control (80.9%),
Agree is significantly lower in Uncertain1st (74.8%)"
([Kim et al. 2024, FAccT](https://arxiv.org/abs/2405.00623)). The trade-offs are explicit in the
same paper: "TrustIntention is significantly lower in Uncertain1st (2.91) compared to both
Control (3.25) and UncertainGeneral (3.36)", and the mitigation was **incomplete** — participants
still underperformed the no-AI baseline. **The phrasing carries the effect**, not the mere
presence of a caveat: general uncertainty and first-person uncertainty behaved differently on
different measures.

**That result must be read against a genuine conflict, not averaged with it.** Zhou et al. found
users relying on generations "nearly 90% of the time" whether marked with strengtheners,
weakeners, or nothing at all ([Zhou et al. 2024](https://arxiv.org/abs/2401.06730)). The two are
reconcilable by design rather than by splitting the difference: Zhou et al. measured
single-shot reliance on short QA answers with markers inserted into the answer, while Kim et al.
manipulated a search-assistant interface across a task with a no-AI control and measured final
accuracy. *Interpretation:* uncertainty language changes behaviour when the reader has both an
alternative and a reason to use it, and does not when the reader's only move is to accept or
re-look-up a one-line answer. For documentation, the reader usually *does* have an alternative —
the code — which favours Kim et al.'s reading, but no study tested that population.

**Cognitive forcing reduces overreliance and is disliked in proportion to how well it works.**
Buçinca et al. (N=199) found that "cognitive forcing significantly reduced overreliance compared
to the simple explainable AI approaches. However, there was a trade-off: people assigned the
least favorable subjective ratings to the designs that reduced the overreliance the most", it
"did not completely eliminate overreliance", and it "benefited participants higher in Need for
Cognition more" — an equity cost the authors audited for deliberately
([Buçinca et al. 2021, CSCW](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca21trust.pdf)).
*Interpretation:* a documentation review gate that forces the reviewer to state a claim's
evidence before seeing the agent's justification is a cognitive forcing function, and should be
expected to be unpopular and unevenly effective, not costless.

**Prompting for accuracy can make the failure worse.** Peters and Chin-Yee report that when
explicitly prompted for accuracy, most models "produced broader generalizations of scientific
results than those in the original texts", with three named models overgeneralizing in 26%–73% of
cases, and that "newer models tended to perform worse in generalization accuracy than earlier
ones" ([Peters and Chin-Yee 2025](https://arxiv.org/abs/2504.00025)). *This is the most important
negative result in this report for practitioners:* adding "be accurate and note uncertainty" to a
documentation prompt is not a neutral safety measure, and the trend line does not favour waiting
for better models.

**Making documents harder to read is not supported and should not be attempted.** The tempting
inverse of the fluency effect — introduce disfluency so readers engage analytically — rests on
Alter et al. (2007), which failed to replicate at scale: pooling 17 experiments, Meyer et al.
found "no significant effect of disfluent fonts on CRT scores (M Normal = 1.43, M Disfluent =
1.42)" and "no evidence of a disfluent font benefit under any conditions"
([Meyer et al. 2015, *JEP: General*](https://files01.core.ac.uk/download/pdf/215755295.pdf)).
The fluency-to-truth link (Reber and Schwarz) and the disfluency-to-analysis link are separate
claims, and only the first survived.

**Class-before-number is the strongest mitigation found locally, and it is unmeasured.** The
local standard's central instruction is that "Class is decided by *how you came to know the
thing*, never by how sure you feel about it", with an operational test — "Could a competent
reader, without knowing what the team wanted, arrive at this statement from these sources?" — and
a named failure mode for the answer "no": a decision dressed as a derivation, which "the class
makes ... look derived. It was not derived; it was decided." *Interpretation:* this targets the
right object. Force is a property of *how a claim was obtained*, and a scalar attached after the
fact cannot repair a claim filed under the wrong provenance. *Limitation:* no evidence was found,
locally or externally, that a provenance-class discipline improves reader outcomes; the case for
it is analytic, and the local practice data (43.2% precision violations) shows that a documented
rule without a checker does not propagate on its own.

**Refusing to publish a weak claim beats rating it.** The local standard's rule — "Do not publish
a claim you would rate very low ... A gap tells a reader to go and find out; a low-confidence
claim invites them to use it anyway" — is consistent with Zhou et al.'s reliance finding that a
marked-uncertain claim is still relied on. *Interpretation:* the reliably effective lever is
removing the claim, not annotating it, and a named gap is the artefact that survives the reader's
tendency to use whatever is written down.

**Upstream fixes exist but are not available to a documentation team.** Kalai et al.'s remedy is
"a socio-technical mitigation: modifying the scoring of existing benchmarks", and Leng et al.'s
is calibrated reward modelling during PPO. Both operate on model training, not on document
review, and neither changes the behaviour of a model a team is using today.

## Limits and open questions

- **The central transfer is unvalidated.** Every quantitative external result here was measured
  on QA, science summarization, decision tasks, programming answers, or preference votes. None
  was measured on agent-authored technical documentation. The mechanisms are well supported; the
  claim that they operate at these magnitudes *in this genre* is interpretation throughout.
- **The formatting half of the research question is the weakest-evidenced half.** No source was
  found that measures whether markdown structure reduces defect detection by a document
  reviewer. What exists measures preference (LMSYS, Soumik), acceptance (Bansal), and overlooked
  errors under a comprehensive-and-articulate style (Kabir) — three different dependent
  variables, none of them "reviewer failed to notice a defect because of the formatting". The
  answer given above therefore attributes most of the effect to volume and apparent coverage
  rather than to formatting syntax, and that attribution rests on one observational analysis
  whose own authors decline to claim causation.
- **Two supporting sources are unreviewed 2026 preprints** (Soumik 2026) or single-vendor
  analyses (LMSYS 2024). The judge-vs-human format gap is the one finding in this report that
  would change a practical recommendation — whether to automate first-pass documentation review
  — and it rests on 30 annotated pairs and two raters. It should be treated as a hypothesis worth
  testing locally, not as a result.
- **The local corpus measurements are field counts, not quality judgements.** The 43.2%
  two-decimal figure establishes divergence from a documented convention; it does not establish
  that any particular value is wrong. The 87.3% `FACT` share is reported explicitly as
  *undetermined between* a genuinely citation-built corpus and inference recorded as observation;
  resolving it requires reading citations against statements at corpus scale, which was out of
  scope.
- **Per-node authorship timing was not established.** `confidence.md` merged 2026-08-28 and
  corpus content begins 2026-08-25, so some entries certainly predate the convention they diverge
  from. The finding stated is therefore about *propagation of an unchecked rule*, not about
  authors ignoring a rule they had.
- **One local observation depends on a corrected tool result.** The validator's two findings for
  `corpus-standard-confidence` were dismissed as sparse-checkout artefacts on the basis that the
  cited ADR is tracked at HEAD but absent from disk. This was checked, but the validator was not
  re-run on a full checkout, so the claim "the node would otherwise pass" is one inference removed
  from the observation.
- **The conflict between Zhou et al. and Kim et al. is reconciled by interpretation, not by
  evidence.** The design-difference explanation offered above is plausible and untested. If it is
  wrong, the practical advice about expressed uncertainty in documentation changes materially.
- **Open: does the confident register survive translation into a different surface form?** If a
  document's claims are extracted into a bare list stripped of prose, do reviewers find more
  defects? This is testable cheaply and locally, and no evidence either way was found.
- **Open: does recording confidence-at-time-of-writing against later-discovered errors produce
  usable calibration data at documentation scale?** The local standard identifies the absence;
  nothing found establishes that closing it is feasible for a corpus this size.
- **Absence of found evidence is not evidence of absence.** Several searches for direct
  measurement in the documentation-review setting returned nothing; that is reported as a gap in
  the literature reachable from this session, not as a finding that no such effect exists.

## Practical review checks

Candidates derived from this report's evidence, offered as research output rather than adopted
policy. Each names what it would and would not establish.

- **Read the citation against the statement for any claim a decision depends on.** Establishes
  claim–evidence fit; the only method found that reaches substance. Cost is unavoidable — the
  local standard reaches the same conclusion: "There is no cheaper check, and a green run is not
  one."
- **Treat every claim about a *gate* — a check, a test, a CI job, a policy that "fails" something
  — as a claim to verify by running or grepping for it.** Motivated by the locally verified DCO
  case (31 workflows, zero matches) and by the observation that fluent enforcement claims read as
  diligence. Establishes existence, not correctness, of the gate.
- **Audit the distribution of any self-assessed confidence field before trusting individual
  values.** One command; exposed a 43.2% divergence here. Establishes convention drift only.
- **Ask whether the claim's *class* is right before arguing about its number.** A decision filed
  as a derivation cannot be repaired by any value. Unmeasured but analytically sound; drawn from
  the local standard's own test.
- **Prefer a named gap to a low-confidence claim.** Supported by the finding that readers rely on
  generations "nearly 90% of the time" regardless of marking.
- **Do not add "be accurate" or "note your uncertainty" to an authoring prompt and treat the job
  as done.** Contradicted by Peters and Chin-Yee's accuracy-prompt result. Establishes nothing on
  its own and may worsen overgeneralization.
- **Do not route first-pass documentation review to a model on the assumption it is neutral about
  presentation.** Weakly supported (single unreviewed preprint) but cheap to test locally by
  scoring a formatted and a prose-only rendering of the same content.
- **Where a template forces a value, provide and use a documented route for "not established".**
  The local standard's four-step escalation is a worked instance; the 43.2% figure suggests the
  route needs a check behind it to hold.
- **Expect any review intervention that actually reduces overreliance to be unpopular.**
  Buçinca et al. found the least-liked designs were the most effective; a review gate rated
  frictionless is weak evidence that it is working.
- **Do not adopt deliberate disfluency.** Directly contradicted by a 17-experiment pooled null.

## References

- [GPT-4 Technical Report](https://arxiv.org/html/2303.08774v6) — OpenAI, arXiv:2303.08774v6 (2023; HTML version read 2026-09-09). Source of the pre-training/post-training calibration statements and the Figure 8 caption "The post-training hurts calibration significantly."
- [Why Language Models Hallucinate](https://arxiv.org/abs/2509.04664) — Kalai, Nachum, Vempala and Zhang, OpenAI / Georgia Tech, arXiv:2509.04664 (2025). Source of the evaluation-incentive argument that training and grading "reward guessing over acknowledging uncertainty."
- [Taming Overconfidence in LLMs: Reward Calibration in RLHF](https://arxiv.org/abs/2410.09724) — Leng et al., arXiv:2410.09724 (2024/2025). Source for RLHF-induced verbalized overconfidence and reward-model bias toward high-confidence scores.
- [Relying on the Unreliable: The Impact of Language Models' Reluctance to Express Uncertainty](https://arxiv.org/abs/2401.06730) — Zhou, Hwang, Ren and Sap, ACL 2024 (long paper); figures read from the ar5iv rendering of arXiv:2401.06730 on 2026-09-09. Source of the 5% epistemic-marker rate, the 53%-correct/47%-error confident set, the ~90% reliance regardless of marking, and the preference-data weakener/strengthener/plain reward scores (-1.86 / 0.82 / 4.03).
- [Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs](https://arxiv.org/abs/2306.13063) — Xiong et al., ICLR 2024, arXiv:2306.13063. Source for verbalized overconfidence imitating human confidence patterns and for the finding that no elicitation technique consistently wins.
- [Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548) — Sharma et al., Anthropic, arXiv:2310.13548 (2023). Source for consistent sycophancy across five assistants and for humans and preference models preferring convincingly-written sycophantic responses.
- [Generalization Bias in Large Language Model Summarization of Scientific Research](https://arxiv.org/abs/2504.00025) — Peters and Chin-Yee, published in *Royal Society Open Science* 12(4):241776 (April 2025); the journal page returned HTTP 403 on 2026-09-09, so the preprint of record is cited. Source of OR = 4.85, 95% CI [3.06, 7.70], p < 0.001 across 4,900 summaries and 10 models, the 26–73% overgeneralization under accuracy prompting, and the newer-models-worse trend.
- [Is Stack Overflow Obsolete? An Empirical Study of the Characteristics of ChatGPT Answers to Stack Overflow Questions](https://arxiv.org/abs/2308.02312) — Kabir, Udo-Imeh, Kou and Zhang, CHI 2024 (arXiv abstract read 2026-09-09; the ACM full text returned HTTP 403). Source of 52% incorrect, 77% verbose, 35% preferred for comprehensiveness and articulate style, 39% overlooked misinformation, over 517 programming questions.
- [Do Users Write More Insecure Code with AI Assistants?](https://arxiv.org/abs/2211.03622) — Perry, Srivastava, Kumar and Boneh, ACM CCS 2023, arXiv:2211.03622. Source of the confidence–competence dissociation: less secure code alongside greater belief that the code was secure.
- [Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance](https://idl.cs.washington.edu/files/2021-AIExplanationsTeamPerformance-CHI.pdf) — Bansal et al., CHI 2021 (author-hosted PDF, text extracted 2026-09-09). Source of "explanations increased the chance that humans will accept the AI's recommendation, regardless of its correctness."
- ["I'm Not Sure, But...": Examining the Impact of Large Language Models' Uncertainty Expression on User Reliance and Trust](https://arxiv.org/abs/2405.00623) — Kim, Liao et al., ACM FAccT 2024, arXiv:2405.00623. Source of the N=404 four-condition results: accuracy 63.9%→72.8%, agreement 80.9%→74.8%, trust intention 3.25→2.91, and the incomplete-mitigation finding against the no-AI baseline.
- [To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca21trust.pdf) — Buçinca, Malaya and Gajos, *Proc. ACM Hum.-Comput. Interact.* 5, CSCW1, Article 188 (April 2021); author-hosted PDF, text extracted 2026-09-09. Source of the N=199 result, the acceptability trade-off, the incomplete elimination of overreliance, and the Need-for-Cognition moderation.
- [Effects of Perceptual Fluency on Judgments of Truth](https://philpapers.org/rec/REBEOP) — Reber and Schwarz, *Consciousness and Cognition* 8(3):338–342 (1999). Source of the contrast-manipulation demonstration that easier-to-read statements are judged truer.
- [Disfluent Fonts Don't Help People Solve Math Problems](https://files01.core.ac.uk/download/pdf/215755295.pdf) — Meyer, Frederick, Burnham et al., *Journal of Experimental Psychology: General* 144(2):e16 (2015). Source of the 17-experiment pooled null (M Normal = 1.43, M Disfluent = 1.42) against the disfluency-activates-analysis hypothesis.
- [Does style matter? Disentangling style and substance in Chatbot Arena](https://www.lmsys.org/blog/2024-08-28-style-control/) — LMSYS Org, 28 August 2024. Source of the style-control coefficients (length 0.249; markdown list 0.031, header 0.024, bold 0.019), the "length was the dominant style factor" statement, the observational-analysis caveat, and the rank shifts.
- [Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines](https://arxiv.org/html/2604.23178) — Soumik, arXiv:2604.23178v2, 24 June 2026. **Unreviewed single-author preprint**; source of the judge markdown preferences (Gemini 2.5 Pro 97%, Gemini 2.5 Flash 90%, Claude Sonnet 4 83%, Llama 3.3-70B 73%, GPT-4o 53%) against a 57% two-annotator human baseline on 30 pairs.
- [Let Me Speak Freely? A Study On The Impact Of Format Restrictions On Large Language Model Performance](https://aclanthology.org/2024.emnlp-industry.91/) — Tam et al., EMNLP 2024 Industry Track. Cited only for the observed decline in reasoning under format restriction; the transfer to documentation templates is this report's interpretation.
- Local repository evidence — `launchpad-26/buzz` fork, branch `topic-13-deceptive-fluency`, revision `a16d9add06638a6b19daa4c39fba027e0d4715e8`, inspected 2026-09-09 in a **sparse checkout**: `launchpad/docs/corpus/standards/confidence.md` (quoted rules and the eight body defects at lines 71–79, 154–155, 180–181, 192–193, 396–397); 350 corpus nodes under `launchpad/docs/corpus/` excluding `schema/` (7,114 evidence entries — 6,214 `FACT`, 384 `INFERENCE`, 516 `TEAM_KNOWLEDGE`; the `confidence` value histogram); `launchpad/project-intelligence/corpus/validate.py` run output; `launchpad/AGENTS.md:380` and `launchpad/README.md:123` against 31 tracked `.github/workflows/` files.
