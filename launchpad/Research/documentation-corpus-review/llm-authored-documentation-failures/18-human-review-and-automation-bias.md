# Human review and automation bias

| Metadata | Value |
|---|---|
| Topic number | 18 |
| Exact research question | Why do reviewers over-trust agent-authored documentation, which conventional review practices fail against it, and what review conditions improve detection? |
| Primary model | Codex |
| Research date | 2026-09-09 |
| Scope | Human review of agent-created or agent-revised technical documentation, including repository pull requests, procedures, reference, architecture, policy, and generated summaries. The report considers factual, omission, procedural, normative, and provenance defects. Evidence from aviation and general AI-assisted decision making is transferred cautiously; no claim is made that every reviewer or review setting exhibits automation bias. |
| Evidence limitations | No located controlled study directly compares defect detection in human- versus LLM-authored technical-documentation pull requests. Most causal evidence comes from automation-assisted decision tasks, and software-specific evidence is stronger for code generation/review than documentation. Review conditions proposed here are therefore a combination of measured human-factors effects and bounded workflow recommendations. |

## Executive answer

Reviewers can over-trust agent-authored documentation when the generated draft becomes a
default answer and substitutes for their own evidence gathering. Classic automation-bias
research distinguishes **omission errors**—failing to act because automation did not flag
a problem—from **commission errors**—following automated guidance despite stronger
contradictory evidence. Skitka, Mosier, and Burdick observed both in decision-support
experiments and found that accountability reduced them
([Skitka et al., 2000](https://doi.org/10.1006/ijhc.1999.0349)). The direct transfer is:
a reviewer may search only where the draft signals uncertainty, or approve a confident
claim despite conflicting code, tests, policy, or runtime evidence.

LLM prose adds a difficult presentation layer. It is complete-looking, fast to produce,
and can include explanations and citations that appear to make verification easier. Yet
explanation is not the same as verifiability. In three human-AI studies, Bansal et al.
found that explanations increased acceptance of AI recommendations whether those
recommendations were correct or incorrect and did not improve complementary team
performance
([Bansal et al., CHI 2021](https://www.microsoft.com/en-us/research/publication/does-the-whole-exceed-its-parts-the-effect-of-ai-explanations-on-complementary-team-performance/)).
Buçinca et al. found that cognitive-forcing designs reduced overreliance relative to
simple explanation interfaces, but participants liked the more effective interventions
less and the benefit varied with motivation for effortful thought
([Buçinca et al., CSCW 2021](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca2021trust.shtml)).

The conclusion is not “humans always trust AI.” Controlled research also finds algorithm
aversion in some conditions and algorithm appreciation in others. Task difficulty,
expertise, observed errors, framing, perceived objectivity, incentives, and the ability to
verify all change reliance. The supported target is **appropriate reliance**: accept
correct assistance and reject incorrect assistance, not maximum skepticism or maximum
trust.

Conventional line-by-line prose review fails when it checks grammar, plausibility, and
internal consistency without independently reconstructing the task, evidence, and
omissions. Better conditions require an evidence-bearing change: reviewers see exact
source revisions and validation results; make or record an independent judgment before
seeing the agent's conclusion for high-risk claims; verify sampled claims and procedures
against primary evidence; review small risk-stratified units; actively search for absent
and contradictory information; and remain accountable for an explicit decision. Human
review works as a control only when the workflow makes verification possible and measures
detection, not merely approval throughput.

## Question, scope, and method

### Subquestions

- Which cognitive and workflow mechanisms produce overreliance or under-monitoring?
- What is distinctive about fluent, explained, citation-shaped generated documentation?
- Which common review practices test presentation but not evidential support or omission?
- Which interventions improve appropriate reliance, and what costs or boundary conditions
  accompany them?
- How should review effectiveness be evaluated without assuming that disagreement with an
  agent is automatically correct?

### Exclusions

- A diagnosis of individual reviewers or a claim that disclosure of AI authorship alone
  determines trust.
- General editorial quality unrelated to reliance on automated output.
- Replacement of deterministic validation with human inspection.
- High-stakes domain requirements or legal conclusions for a particular industry.
- Program-wide synthesis or adoption of a review policy.

### Evidence and source plan

Local inspection used branch `docs/llm-research-program` at commit
`267404b3f` and the program's research contract and report template. They require visible
evidence limits, counterevidence, claim support, and validation boundaries; those
requirements define the review object but do not prove reviewers will use it effectively.

External evidence was divided into foundational automation research, controlled modern
human-AI experiments, counterevidence on algorithm aversion/appreciation, and software-
review analogues. The claim ledger distinguished directly measured effects from transfer
to documentation. Searches looked for failed explanation interventions, costs of forcing
functions, accountability effects, expertise and difficulty moderators, and evidence that
people sometimes discount rather than over-trust automation. Saturation was reached when
the mechanisms, counterconditions, and intervention trade-offs repeated without a direct
technical-documentation review experiment emerging.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| Omission-by-silence | Reviewers do not inspect a risk or missing subject because the agent did not flag it. | Corresponds to automation-bias omission errors. The documentation transfer is plausible but unmeasured directly. |
| Commission against evidence | Reviewers accept a claim or instruction despite contradictory code, test, policy, or operational evidence. | Direct analogue to commission errors in Skitka et al.; expertise and accessible contradiction can reduce but do not eliminate it. |
| Default anchoring | The generated draft frames the problem and becomes the starting answer, narrowing alternative interpretations and searches. | AI-advice studies operationalize movement toward advice; the exact anchoring contribution in document review is not isolated. |
| Fluency and explanation halo | Coherent structure, rationale, citations, or confident wording is mistaken for verified support. | Bansal et al. show explanations can increase acceptance independent of correctness in tested tasks; prose fluency itself was not separately manipulated there. |
| Citation outsourcing | Review confirms that links exist or look authoritative without checking entailment, scope, date, independence, and revision. | A link-validity check is structurally useful but cannot establish support. This is a workflow analysis, not a measured cognitive rate. |
| Change-only tunnel vision | Reviewers inspect altered lines without testing the corpus impact, unchanged contradictions, or missing updates. | Common diff review makes changes visible by design; no direct experiment here quantifies its documentation omission rate. |
| Automation complacency after success | Prior correct outputs establish a generalized trust heuristic, so later defects receive less scrutiny. | Parasuraman and Riley identify reliability, consistency, workload, and trust as factors in misuse and monitoring ([1997 paper](https://web.mit.edu/16.459/www/parasuraman.pdf)). Effects vary substantially by person and setting. |
| Review-volume collapse | Generated output exceeds available attention, causing shallow sampling or rubber-stamp approval. | Plausible capacity mechanism; direct causal documentation evidence was not located. Volume should be measured rather than assumed. |
| Expertise mismatch | A reviewer can assess style but not system behavior, policy authority, security, or reader task success. | Human review is not one capability. Adding a human without the relevant evidence and expertise does not provide the missing judgment. |
| Reflexive rejection | Reviewers discount correct output merely because it is labeled algorithmic or after observing an error. | Algorithm-aversion evidence is important counterevidence; overreliance controls should not reward needless rejection ([Logg et al., 2019](https://www.hbs.edu/ris/Publication%20Files/17-086_610956b6-7d91-4337-90cc-5bb5245316a8.pdf)). |

## Causes and mechanisms

### Cognitive effort and vigilance

Automation can change the human role from primary reasoner to monitor. Monitoring a mostly
correct stream is difficult: the reviewer must sustain attention for rare defects, while
acceptance is usually rewarded with speed. Parasuraman and Riley's synthesis identifies
workload, reliability, consistency, salience, trust, and individual differences as
interacting determinants of automation use and misuse. It does not support a simple rule
that higher trust or higher workload always produces a fixed error rate.

### Verification cost

Agent output is cheap to generate but a consequential claim may require navigating code,
history, tests, configuration, external standards, and live state. If a citation or
explanation merely repeats the agent's reasoning, it lowers perceived uncertainty without
lowering verification cost. Research on cognitive forcing suggests that people
strategically allocate effort: harder verification and low incentives increase reliance,
while interventions that require engagement can reduce it
([Vasconcelos et al., 2023](https://arxiv.org/abs/2212.06823)).

### Presentation and confidence

Review interfaces foreground the proposed text and its local diff. Missing content has no
line to comment on. Uniform templates and citations provide legitimacy cues. Explanations
can aid verification when they expose checkable evidence, but can also become persuasive
additional output. The decisive distinction is whether a reviewer can use the explanation
to independently predict or test behavior.

### Ambiguous accountability

“Human reviewed” can mean opened, skimmed, approved, copyedited, domain-validated, or
executed. If the agent is treated as author while the reviewer is treated as a procedural
gate, responsibility diffuses. Skitka et al. found social accountability reduced both
error classes in their task, but organizational blame pressure could also encourage
defensive rejection; the correct transfer is to require a reasoned, scoped decision, not
punishment.

### Trust is dynamic and bidirectional

People may appreciate algorithmic advice, especially on difficult or perceived-objective
tasks, or become averse after visible errors. Logg, Minson, and Moore found greater
adherence to algorithmic than human advice across several experiments; other studies find
aversion and domain moderators. A review design must calibrate reliance using observed
capability and claim-level evidence rather than a global “AI good” or “AI bad” label.

## Detection and validation

Review effectiveness should be measured against known or subsequently adjudicated defects,
not approvals. Useful measures include omission- and commission-defect recall, false-
positive challenge rate, correction precision, review latency, unsupported-claim escape
rate, and downstream task success. Stratify by defect type, consequence, reviewer
expertise, document genre, model, and batch size.

| Method | What it reveals | What it cannot establish |
|---|---|---|
| Seeded-defect exercises | Whether reviewers detect known factual, omission, procedural, provenance, and normative defects. | Natural prevalence or performance on novel defects; seeds can teach to the test. |
| Independent-first comparison | Whether showing the draft changes a reviewer's prior interpretation or search. | That the prior judgment is correct; both must be checked against evidence. |
| Claim-verification sampling | Rate at which sampled consequential claims are traced to applicable primary evidence. | Unsampled correctness or completeness. |
| Procedure execution | Whether instructions work in the named environment and produce expected results. | Safety and applicability in every supported environment. |
| Review telemetry | Time, files opened, evidence links followed, overrides, and comments can expose rubber-stamp patterns. | Cognitive state or quality by themselves; surveillance can distort behavior. |
| Post-publication outcomes | Reader failures, incidents, support questions, and corrections reveal escaped defects. | Absence of reports is not absence of defects, and attribution may be ambiguous. |

## Mitigations

1. **Make the review object evidence-bearing.** Include the exact task, intended audience,
   changed claims, sources with revisions, commands run, failures, unknowns, and validator
   scope. Do not make reviewers reconstruct basic provenance from prose.
2. **Elicit an independent view for consequential claims.** Before showing the agent's
   conclusion, ask the domain reviewer to state expected behavior, authority, or critical
   risks. Use this selectively; doing it for every sentence is wasteful.
3. **Use cognitive forcing at risk boundaries.** Require the reviewer to open decisive
   evidence, identify one possible contradiction or omission, and state why the selected
   source governs. Expect extra time and lower subjective preference.
4. **Review smaller, coherent batches.** Split generated changes by reader task or claim
   family, cap unreviewed volume, and prevent a large formatting rewrite from hiding
   semantic changes.
5. **Separate review roles.** Editorial, domain, security/privacy, operational, and policy
   review answer different questions. Require only the roles justified by risk.
6. **Validate before persuasion.** Run schemas, link checks, executable examples, code-
   documentation comparisons, and secret scans before human review; show failures and
   skipped scope, not only a green badge.
7. **Search for absence and conflict.** Provide a coverage map, related-document set, and
   contradictory evidence candidates. Line review alone cannot display what was not
   written.
8. **Use checkable explanations.** Prefer source spans, revision identifiers, test output,
   and reproducible commands over free-form rationales. Explanations that cannot be
   verified are additional claims.
9. **Calibrate with feedback.** Periodically use held-out seeded defects and share outcomes
   by failure class. Avoid a single reviewer “trust score.”
10. **Preserve human authority.** The reviewer must be able to reject, narrow, or defer the
   change without production pressure making approval the default.

## Limits and open questions

- The foundational studies often use aviation-like monitoring or bounded classification
  tasks, not multi-hour repository review. Their mechanisms are relevant, but effect sizes
  do not transfer directly.
- Algorithm aversion and appreciation both occur. Labeling content as AI-authored may
  increase or decrease scrutiny depending on context; disclosure alone is not a control.
- Explanations are heterogeneous. Evidence-linked, task-specific explanations can enable
  verification even though generic rationales may increase acceptance. The studies do not
  justify banning explanations.
- Cognitive forcing increases effort and can reduce acceptability. Excessive mandatory
  friction may cause workarounds or superficial compliance.
- Accountability improved performance in a controlled experiment; punitive or ambiguous
  accountability in organizations could have different effects.
- Expertise helps only within its domain and may increase confidence. Multi-role review
  adds cost and can diffuse ownership unless responsibilities are explicit.
- It remains unknown which documentation defect mixtures best predict real review
  failures, how agent disclosure changes behavior longitudinally, and how much review
  volume can rise before detection degrades.

## Practical review checks

- Candidate check: ask what the reviewer independently expected before exposing them to
  the agent's conclusion for high-consequence claims.
- Candidate check: require each material claim to identify its decisive source, revision,
  and why that source has authority for this claim type.
- Candidate check: open and inspect a risk-weighted sample of citations; do not accept link
  existence as support.
- Candidate check: run every safe consequential procedure in the named environment and
  record skipped or destructive steps explicitly.
- Candidate check: inspect related unchanged documents and a coverage map for omissions;
  do not limit review to diff lines.
- Candidate check: split changes whose semantic review cannot be completed within the
  available attention budget.
- Candidate check: distinguish editorial approval, factual validation, policy authority,
  security/privacy review, and operational execution in the review record.
- Candidate check: show validator scope and skipped checks beside the result.
- Candidate check: periodically seed representative defects and measure detection by
  class, not simply approval speed or comment count.
- Candidate check: investigate both automatic acceptance and automatic rejection; the
  desired outcome is evidence-calibrated reliance.

## References

- [Humans and Automation: Use, Misuse, Disuse, Abuse](https://web.mit.edu/16.459/www/parasuraman.pdf) — Raja Parasuraman and Victor Riley, *Human Factors* 39(2), 1997; foundational framework for automation use, monitoring, trust, misuse, and disuse.
- [Accountability and automation bias](https://doi.org/10.1006/ijhc.1999.0349) — Linda Skitka, Kathleen Mosier, and Mark Burdick, *International Journal of Human-Computer Studies* 52(4), 2000; controlled omission/commission errors and accountability intervention.
- [Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance](https://www.microsoft.com/en-us/research/publication/does-the-whole-exceed-its-parts-the-effect-of-ai-explanations-on-complementary-team-performance/) — Bansal et al., CHI 2021; explanations, acceptance, and complementary performance across three tasks.
- [To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-Assisted Decision-Making](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca2021trust.shtml) — Buçinca, Malaya, and Gajos, CSCW 2021; N=199 experiment, reduced overreliance, acceptability and cognitive-motivation trade-offs.
- [Explanations Can Reduce Overreliance on AI Systems During Decision-Making](https://arxiv.org/abs/2212.06823) — Vasconcelos et al., 2023; five studies on strategic engagement, verification cost, difficulty, and incentives as boundary conditions.
- [Algorithm Appreciation: People Prefer Algorithmic to Human Judgment](https://www.hbs.edu/ris/Publication%20Files/17-086_610956b6-7d91-4337-90cc-5bb5245316a8.pdf) — Logg, Minson, and Moore, *Organizational Behavior and Human Decision Processes*, 2019; six experiments providing counterevidence to a universal algorithm-aversion account.
- [Rethinking Code Review Workflows with LLM Assistance: An Empirical Study](https://ieeexplore.ieee.org/document/11323409/) — industrial field study, 2025; software-review analogue concerning AI-led versus on-demand assistance and risk/familiarity variation.
- [Artificial Intelligence Risk Management Framework 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) — NIST AI 100-1, January 2023; human-AI configuration, independent review, contextual evaluation, uncertainty, and documented responsibility.
