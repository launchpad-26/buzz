# Documentation corpus review research

This directory holds the research that informs a future content-review
checklist for the Buzz documentation corpus.

Each topic is researched independently using the `deep-research` skill. Research
reports may recommend checklist criteria, but they do not establish project policy
or change the corpus contract. The separate synthesis proposes what to adopt; adoption
still requires a human decision.

## Research loop

For each topic:

1. Select and scope one topic.
2. Invoke the `deep-research` skill.
3. Frame the central question, subquestions, exclusions, and completion criteria.
4. Inspect the relevant Buzz corpus material and local rules.
5. Plan coverage of primary, authoritative, and competing sources.
6. Search broadly, then read the strongest sources in depth.
7. Maintain a claim ledger with support, counterevidence, confidence, and gaps.
8. Synthesize the findings for the Buzz documentation corpus.
9. Record the report in this directory with precise citations.
10. Check that citations support claims and that uncertainty remains visible.
11. Mark the topic complete and move to the next one.

The separate synthesis pass is complete. It reconciles overlap, identifies conflicts
requiring human decisions, and recommends review criteria in
[`SYNTHESIS.md`](SYNTHESIS.md). Those recommendations remain proposed until adopted by
a human decision.

## Synthesis

- [x] Combine the 15 general reports and 20 LLM-authored-documentation failure reports.
- [x] Reconcile overlapping and competing recommendations.
- [x] Define hard gates, universal criteria, genre overlays, agent-specific controls,
      and the corpus-review procedure.
- [x] Link each conclusion area back to the recorded research.
- [ ] Adopt or revise the proposed criteria through a human decision.

Read the result: [Cross-topic synthesis: criteria for reviewing the Buzz documentation
corpus](SYNTHESIS.md).

## Topic queue

- [x] Quality model for technical documentation — [`01-quality-model-for-technical-documentation.md`](01-quality-model-for-technical-documentation.md)
- [x] Genre-specific quality criteria — [`02-genre-specific-quality-criteria.md`](02-genre-specific-quality-criteria.md)
- [x] Truth and evidence in living technical documentation — [`03-truth-and-evidence-in-living-technical-documentation.md`](03-truth-and-evidence-in-living-technical-documentation.md)
- [x] Measuring corpus completeness and coverage — [`04-measuring-corpus-completeness-and-coverage.md`](04-measuring-corpus-completeness-and-coverage.md)
- [x] Information architecture for atomic documentation — [`05-information-architecture-for-atomic-documentation.md`](05-information-architecture-for-atomic-documentation.md)
- [x] Documentation usability and findability — [`06-documentation-usability-and-findability.md`](06-documentation-usability-and-findability.md)
- [x] Freshness, staleness, and change impact — [`07-freshness-staleness-and-change-impact.md`](07-freshness-staleness-and-change-impact.md)
- [x] Reviewing procedural and operational documentation — [`08-reviewing-procedural-and-operational-documentation.md`](08-reviewing-procedural-and-operational-documentation.md)
- [x] Normative versus descriptive technical writing — [`09-normative-versus-descriptive-technical-writing.md`](09-normative-versus-descriptive-technical-writing.md)
- [x] Architecture-documentation quality — [`10-architecture-documentation-quality.md`](10-architecture-documentation-quality.md)
- [x] Terminology and conceptual consistency — [`11-terminology-and-conceptual-consistency.md`](11-terminology-and-conceptual-consistency.md)
- [x] Examples, commands, code, and configuration — [`12-examples-commands-code-and-configuration.md`](12-examples-commands-code-and-configuration.md)
- [x] Documentation accessibility and inclusive comprehension — [`13-documentation-accessibility-and-inclusive-comprehension.md`](13-documentation-accessibility-and-inclusive-comprehension.md)
- [x] Documentation review at corpus scale — [`14-documentation-review-at-corpus-scale.md`](14-documentation-review-at-corpus-scale.md)
- [x] Security and disclosure quality in public technical documentation — [`15-security-and-disclosure-quality-in-public-technical-documentation.md`](15-security-and-disclosure-quality-in-public-technical-documentation.md)

## Report contents

Each report should include:

- research question and scope;
- method and source-selection approach;
- key findings;
- competing positions and contradictory evidence;
- implications for the Buzz corpus;
- candidate checklist criteria;
- uncertainties and limitations;
- precise source citations.
