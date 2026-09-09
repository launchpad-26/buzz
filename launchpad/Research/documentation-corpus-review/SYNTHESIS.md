# Cross-topic synthesis: criteria for reviewing the Buzz documentation corpus

**Status:** Research synthesis complete; the criteria below are `PROPOSED`, not adopted project policy.

**Research baseline:** 35 completed reports at repository revision `d4a855f3ba22c5cf0a2de91d2ee5150898ad6572`, reviewed on 2026-09-09.

## Purpose

This synthesis answers one practical question:

> What criteria should a content review of the Buzz documentation corpus use, including when agents generated documentation from code and repository evidence?

It combines the original 15 reports on technical-documentation quality with the 20 reports on LLM-authored documentation failures. It does not itself audit the corpus, set acceptance thresholds, or amend the corpus contract. Those are later human decisions.

## Executive answer

The corpus should not be reviewed with one flat checklist or one quality score. It should use four connected layers:

1. **Hard gates** for defects that other strengths cannot compensate for.
2. **A universal quality profile** applied to every reviewed object.
3. **Genre and artifact overlays** selected according to what the content promises.
4. **A corpus-assurance process** that declares its baseline, population, coverage, methods, findings, ownership, and retest evidence.

Agent authorship should trigger additional evidence-process checks, but it should not be treated as proof that a document is defective. The decisive questions remain about the artifact: whether its claims are supported, its scope is adequate, its instructions work safely, its reader can use it, and its provenance permits correction. The agent controls address recurrent failure mechanisms—missing context, tool-state loss, unsupported inference, temporal mixing, false completeness, transformation drift, deceptive fluency, circular evidence, and source poisoning.

No positive score should offset a failed gate. No green automated result should be described as proving more than the validator actually tested. No completeness claim should be made without a declared denominator. No corpus-wide conclusion should be drawn from a purposive sample.

## Scope and method

This is a synthesis of the recorded research, not a new literature search. The 35 reports were treated as the evidence set; their underlying sources, methods, counterevidence, and limitations remain available in the linked reports. Findings were grouped by the review decision they support, then reconciled where recommendations pulled in different directions.

The synthesis covers canonical content nodes, maps and navigation artifacts, generated projections, examples, commands, configuration, diagrams, and the evidence records used to support them. Renderer behavior is included only where the delivered experience changes accessibility, findability, or task success. Publishing implementation and LLM-model selection are outside scope.

The evidence is strongest for the general review model, claim/evidence discipline, genre differences, accessibility, security, procedural testing, and the limits of automation. It is moderate for how strongly particular LLM failure mechanisms transfer to this exact corpus because direct studies of repository agents writing technical documentation remain sparse. The research does not establish prevalence rates, criterion weights, numerical pass thresholds, or a reliable single score.

## Recommended review model

Run the review in this order: define and freeze; apply gates; review the universal profile; add overlays; remediate and retest; then report bounded coverage and residual risk.

The object of review may be a node, a claim set, an executable artifact, a connected reader journey, a generated view, or the corpus as a population. The review record must name which object it assessed. A result for one object must not silently stand in for another—for example, a valid Markdown file does not establish true prose, and a correct node does not establish a usable journey.

## Hard gates

These are non-compensatory conditions. If one applies, the object does not pass merely because its prose, structure, or other criteria are strong.

### H1 — Material integrity

**Stop or fail:** A consequential claim is contradicted, fabricated, unsupported, circularly supported, or materially broader than its evidence.

**Disposition:** Correct or narrow the claim and evidence together; preserve unresolved conflict.

**Research:** [Truth and evidence](03-truth-and-evidence-in-living-technical-documentation.md), [technical hallucination](llm-authored-documentation-failures/04-technical-hallucination-and-unsupported-inference.md), and [claim provenance](llm-authored-documentation-failures/05-claim-provenance-and-circular-evidence.md).

### H2 — Unsafe action

**Stop or fail:** A consequential procedure, command, example, or configuration can cause harm, targets an unknown environment, lacks necessary authorization, or claims validation that was not performed.

**Disposition:** Stop execution or publication; establish a safe target, validation boundary, recovery path, and appropriate authority.

**Research:** [Procedural documentation](08-reviewing-procedural-and-operational-documentation.md), [examples and configuration](12-examples-commands-code-and-configuration.md), and [LLM executable failures](llm-authored-documentation-failures/08-executable-procedures-examples-and-configuration.md).

### H3 — Disclosure boundary

**Stop or fail:** Content may expose a credential, personal data, private operational detail, or an uncoordinated vulnerability.

**Disposition:** Stop public handling and route privately. Removal alone is not remediation for an exposed secret.

**Research:** [Security and disclosure](15-security-and-disclosure-quality-in-public-technical-documentation.md) and [LLM security failures](llm-authored-documentation-failures/12-security-privacy-and-disclosure-failures.md).

### H4 — False authority

**Stop or fail:** A consequential requirement, prohibition, permission, enforcement claim, or decision lacks the authority attributed to it or merges intent with observed behavior.

**Disposition:** Restore the authority chain and separate required, intended, implemented, enforced, tested, and observed states.

**Research:** [Normative writing](09-normative-versus-descriptive-technical-writing.md) and [normative distortion](llm-authored-documentation-failures/09-normative-distortion.md).

### H5 — Incoherent baseline

**Stop or fail:** Material claims combine incompatible revisions, environments, platforms, roles, or lifecycle states, or their target cannot be identified.

**Disposition:** Establish the applicable baseline or mark the object unable to assess.

**Research:** [Freshness and change impact](07-freshness-staleness-and-change-impact.md) and [temporal coherence](llm-authored-documentation-failures/03-temporal-and-revision-coherence.md).

### H6 — Compromised evidence path

**Stop or fail:** Untrusted content has been treated as an instruction, has expanded tool, action, or publication authority, or credible source poisoning is unresolved.

**Disposition:** Isolate the source, re-establish instruction and evidence authority, and independently validate affected claims and actions.

**Research:** [Adversarial context and source poisoning](llm-authored-documentation-failures/17-adversarial-context-prompt-injection-and-source-poisoning.md).

### H7 — Critical omission or access barrier

**Stop or fail:** Missing information or inaccessible delivery prevents the intended reader from completing a critical task safely, including recovery or escalation.

**Disposition:** Treat the missing capability as a gate, not a low score elsewhere; supply an equivalent usable route.

**Research:** [Quality model](01-quality-model-for-technical-documentation.md), [coverage](04-measuring-corpus-completeness-and-coverage.md), [accessibility](13-documentation-accessibility-and-inclusive-comprehension.md), and [omissions](llm-authored-documentation-failures/07-omissions-and-false-completeness.md).

### H8 — Required assessment unavailable

**Stop or fail:** Evidence or a required tool failed, was inaccessible, truncated, or could not cover a mandatory high-risk criterion.

**Disposition:** Record `unable to assess`; never convert missing observation into a pass or a claim of absence.

**Research:** [Tool-mediated failures](llm-authored-documentation-failures/02-tool-mediated-evidence-failures.md), [automated validation](llm-authored-documentation-failures/19-automated-detection-and-validation.md), and [corpus-scale review](14-documentation-review-at-corpus-scale.md).

## Universal content criteria

Every reviewed object should receive a result against each applicable criterion. Use `pass`, `finding`, `not applicable`, `unable to assess`, or `accepted risk`; do not collapse those states into a number.

### C01 — Review identity, context, and baseline

The review names the object, canonical identifier or path, revision, delivered surface, status, intended audience, reader goal, starting state, environment, and relevant exclusions. Current, proposed, historical, superseded, and uncertain states remain distinct. The reviewer can tell exactly what the result does and does not cover.

Minimum evidence: an identifiable baseline plus a context-of-use statement. A path, timestamp, or audience label alone is insufficient.

Research: [quality model](01-quality-model-for-technical-documentation.md), [usability and findability](06-documentation-usability-and-findability.md), [temporal coherence](llm-authored-documentation-failures/03-temporal-and-revision-coherence.md).

### C02 — Claim integrity and evidential support

Substantive claims are specific enough to test. Evidence is relevant to the exact proposition, entails the claim under its stated conditions, has authority for that claim type, applies to the named baseline, and is sufficiently independent. Inference, assumption, testimony, implementation, runtime observation, intent, and history are not collapsed together. Plausible counterevidence is sought in proportion to consequence.

Minimum evidence: claim-to-source traceability and semantic inspection of material claims. Link existence, citation count, search snippets, an author's summary, or a passing structural validator do not establish this criterion.

Research: [truth and evidence](03-truth-and-evidence-in-living-technical-documentation.md), [technical hallucination](llm-authored-documentation-failures/04-technical-hallucination-and-unsupported-inference.md), [claim provenance](llm-authored-documentation-failures/05-claim-provenance-and-circular-evidence.md), [error propagation](llm-authored-documentation-failures/15-error-propagation-and-false-consensus.md).

### C03 — Sufficiency, relevance, and honest coverage

The content contains what the named audience and task require within its declared scope, makes material omissions visible, and excludes irrelevant detail that obscures the task. Coverage is measured against explicit obligations rather than file counts, template completion, source inventories, or document volume. Applicable obligations map to content with explicit states such as adequate, partial, missing, intentionally omitted, not applicable, unknown, conflicted, or stale.

Minimum evidence: a declared, versioned coverage denominator and semantic adequacy review. Any percentage includes absolute counts and its denominator.

Research: [quality model](01-quality-model-for-technical-documentation.md), [corpus coverage](04-measuring-corpus-completeness-and-coverage.md), [omissions and false completeness](llm-authored-documentation-failures/07-omissions-and-false-completeness.md), [coverage inflation](llm-authored-documentation-failures/16-coverage-inflation.md).

### C04 — Purpose, genre, and statement function

The object has one dominant reader job and uses a form suited to that job. Supporting material from another genre remains subordinate or is split when it has a different authority, applicability, lifecycle, or maintenance boundary. Consequential sentences can be distinguished as descriptions, definitions, requirements, permissions, recommendations, possibilities, proposals, predictions, or procedures.

Minimum evidence: an identified communicative purpose and applicable genre overlay. Template shape by itself does not prove fitness.

Research: [genre-specific criteria](02-genre-specific-quality-criteria.md), [normative writing](09-normative-versus-descriptive-technical-writing.md), [normative distortion](llm-authored-documentation-failures/09-normative-distortion.md).

### C05 — Comprehensibility, precision, and accessibility

The language is direct and precise for the intended audience without erasing necessary technical distinctions. Conditions, responsibility, exceptions, prerequisites, warnings, and uncertainty appear where they govern the claim or action. Structure and meaning survive the delivered medium: headings, lists, tables, links, diagrams, code, color, zoom, reflow, keyboard use, and assistive technology provide equivalent access where applicable.

Minimum evidence: source-level inspection plus rendered-surface checks for applicable accessibility requirements. Readability formulas, polished prose, and automated scans are diagnostic signals, not proof of comprehension or conformance.

Research: [quality model](01-quality-model-for-technical-documentation.md), [accessibility and comprehension](13-documentation-accessibility-and-inclusive-comprehension.md), [reader and task fitness](llm-authored-documentation-failures/11-reader-and-task-fitness.md), [deceptive fluency](llm-authored-documentation-failures/13-epistemic-calibration-and-deceptive-fluency.md).

### C06 — Technical and executable fidelity

Names, symbols, paths, APIs, commands, configuration, control flow, defaults, side effects, and runtime behavior match the authority appropriate to the claim. Every executable-looking artifact declares what it is, its environment and starting state, literal input and placeholders, expected outcome, validation level, side effects, failure behavior, and recovery. Static code is not used as sole proof of runtime, deployment, organizational, or product-intent claims.

Minimum evidence: claim-type-matched validation at the promised layer. High-risk or high-value artifacts require execution or observation in a representative environment and an outcome oracle, not merely parse success or a zero exit code.

Research: [examples and configuration](12-examples-commands-code-and-configuration.md), [code-to-document fidelity](llm-authored-documentation-failures/06-code-to-document-semantic-fidelity.md), [LLM executable failures](llm-authored-documentation-failures/08-executable-procedures-examples-and-configuration.md).

### C07 — Organization, findability, and connected journeys

Each node is independently understandable for a bounded purpose while remaining part of intentional maps and journeys. A direct-arrival reader can orient themselves; titles, descriptions, headings, link text, status, and applicability cues help them predict and reject results correctly. Typed relationships preserve their semantics. Search, browse, maps, indexes, contextual links, and generated views are treated as distinct routes rather than interchangeable proof of findability.

Minimum evidence: inspection of node boundaries and transitions plus at least one realistic end-to-end journey for consequential needs. A valid link graph or search hit does not prove successful navigation.

Research: [information architecture](05-information-architecture-for-atomic-documentation.md), [usability and findability](06-documentation-usability-and-findability.md), [reader and task fitness](llm-authored-documentation-failures/11-reader-and-task-fitness.md).

### C08 — Conceptual and cross-document coherence

Important concepts have stable identities, scoped preferred labels, definitions with boundaries, and mappings to legitimate code, UI, protocol, configuration, and audience terms. Cross-document claims agree on authority, scope, baseline, and lifecycle, while intentional abstraction differences remain visible. Canonical volatile facts are linked or generated rather than copied without a maintenance path. Derivative documents retain lineage and are not counted as independent corroboration.

Minimum evidence: concept-level and claim-level comparison across affected nodes. Lexical sameness is neither necessary nor sufficient; consistent wording must not propagate an error.

Research: [terminology consistency](11-terminology-and-conceptual-consistency.md), [cross-document drift](llm-authored-documentation-failures/14-cross-document-consistency-and-terminology-drift.md), [transformation fidelity](llm-authored-documentation-failures/10-transformation-and-summarization-fidelity.md), [error propagation](llm-authored-documentation-failures/15-error-propagation-and-false-consensus.md).

### C09 — Task effectiveness and operational usability

Representative readers can find, select, understand, perform, verify, and recover using the content in a realistic context. Review distinguishes success, partial success, failure, false success, errors, assists, retries, abandonment, and dangerous outcomes. Procedures expose observable state transitions, branches, coordination, stop conditions, recovery, cleanup, and escalation rather than only a happy-path sequence.

Minimum evidence: task-based evaluation proportionate to risk. Page views, preference ratings, reviewer approval, confidence, and time-on-page may diagnose behavior but do not establish successful use.

Research: [usability and findability](06-documentation-usability-and-findability.md), [procedural documentation](08-reviewing-procedural-and-operational-documentation.md), [reader and task fitness](llm-authored-documentation-failures/11-reader-and-task-fitness.md).

### C10 — Currency, change impact, and maintainability

Current claims remain applicable to their named baseline. Citations still reach the intended evidence and support the same proposition. Important source, decision, dependency, terminology, interface, configuration, or operational changes produce an explainable review candidate. Every volatile or consequential object has a viable owner, trigger, or maintenance path; historical value is preserved when retirement is the correct disposition.

Minimum evidence: semantic comparison after relevant change and a recorded disposition. Age, recent editing, status metadata, a live URL, an unchanged source, or regenerated output are signals only—not freshness verdicts.

Research: [freshness and change impact](07-freshness-staleness-and-change-impact.md), [temporal coherence](llm-authored-documentation-failures/03-temporal-and-revision-coherence.md), [cross-document drift](llm-authored-documentation-failures/14-cross-document-consistency-and-terminology-drift.md).

### C11 — Security, privacy, and disclosure fitness

Security-relevant content is classified before publication. Public material provides the stable model, assumptions, boundaries, limitations, safe actions, and reporting route that readers need without exposing secrets, personal data, private live coordinates, or uncoordinated vulnerability detail. Claims distinguish design intent, implementation, configuration, runtime observation, and delegated responsibility. Examples use non-operational values, minimum privilege, safe defaults, and warnings before consequential actions.

Minimum evidence: deterministic scanning across the complete publication path plus contextual human or specialist review. Pattern scans cannot establish that combination risk, inferred sensitivity, or a security claim is safe and true.

Research: [security and disclosure](15-security-and-disclosure-quality-in-public-technical-documentation.md), [LLM security failures](llm-authored-documentation-failures/12-security-privacy-and-disclosure-failures.md), [adversarial context](llm-authored-documentation-failures/17-adversarial-context-prompt-injection-and-source-poisoning.md).

### C12 — Provenance, uncertainty, validation, and accountability

The record identifies the artifact and task, revision, sources considered and selected, tool actions and failures, transformations, inferences, unresolved uncertainty, validation performed, model contribution, human decision, and a person or role empowered to correct or retire the result. Confidence and caveats appear beside the claims they qualify. Provenance supports assessment and correction; it is not represented as proof of truth.

Minimum evidence: an accessible review record with enough detail to reproduce the material checks, without requiring private chain-of-thought. Every automated result records its inputs, revision, environment, predicate, exclusions, failures, timeouts, and unverified remainder.

Research: [context selection](llm-authored-documentation-failures/01-context-selection-and-evidence-sufficiency.md), [tool-mediated failures](llm-authored-documentation-failures/02-tool-mediated-evidence-failures.md), [deceptive fluency](llm-authored-documentation-failures/13-epistemic-calibration-and-deceptive-fluency.md), [human review bias](llm-authored-documentation-failures/18-human-review-and-automation-bias.md), [automated validation](llm-authored-documentation-failures/19-automated-detection-and-validation.md), [evaluation and accountability](llm-authored-documentation-failures/20-evaluation-provenance-and-accountability.md).

## Genre and artifact overlays

Apply all universal criteria, then add the overlay for the object's dominant job. Mixed objects may need more than one overlay, but incompatible authority or lifecycle usually indicates that the content should be split.

### G01 — Explanatory and conceptual

Ask whether the content builds an accurate mental model, connects causes and consequences, marks limits, and avoids silently becoming instruction or reference inventory. Expect a reader explanation or decision task plus evidence for the model's technical claims.

Research: [genre-specific criteria](02-genre-specific-quality-criteria.md) and [accessibility and comprehension](13-documentation-accessibility-and-inclusive-comprehension.md).

### G02 — Descriptive reference

Ask whether the promised fact set is neutral, precisely scoped, structured for lookup, complete for its declared fields, and traceable to authoritative sources. Expect a bounded inventory or schema comparison and tested lookup tasks.

Research: [genre-specific criteria](02-genre-specific-quality-criteria.md), [examples and configuration](12-examples-commands-code-and-configuration.md), and [code fidelity](llm-authored-documentation-failures/06-code-to-document-semantic-fidelity.md).

### G03 — Architecture and model

Ask whether stakeholder concerns lead to suitable views, consistent correspondences, decisions and rationale, quality scenarios, implementation mappings, risks, and visible lifecycle state. Expect stakeholder task review, cross-view comparison, and claim-layer evidence—not a diagram count.

Research: [architecture quality](10-architecture-documentation-quality.md) and [transformation fidelity](llm-authored-documentation-failures/10-transformation-and-summarization-fidelity.md).

### G04 — Normative and constraint

Ask whether force, authority, bound subject, applicability, enforcement, verification, exceptions, lifecycle, and precedence are explicit and mutually consistent. Expect active authority plus separate implementation and enforcement evidence where claimed.

Research: [normative writing](09-normative-versus-descriptive-technical-writing.md) and [normative distortion](llm-authored-documentation-failures/09-normative-distortion.md).

### G05 — Procedural and operational

Ask whether the right reader can start safely, perform each observable transition, choose branches, coordinate, verify success, stop, recover, clean up, and escalate. Expect a walkthrough or execution at the promised environment and risk level, including adverse paths.

Research: [procedural documentation](08-reviewing-procedural-and-operational-documentation.md), [examples and configuration](12-examples-commands-code-and-configuration.md), and [LLM executable failures](llm-authored-documentation-failures/08-executable-procedures-examples-and-configuration.md).

### G06 — Verification and assurance

Ask whether the artifact connects a named obligation or risk to a fit method, exact evidence, coverage, current status, limitations, and a repeatable result. Expect a reproducible result envelope and explicit unverified remainder.

Research: [truth and evidence](03-truth-and-evidence-in-living-technical-documentation.md) and [automated validation](llm-authored-documentation-failures/19-automated-detection-and-validation.md).

### G07 — Decision and historical

Ask whether status, context, alternatives, authority, outcome, rationale, consequences, confirmation, supersession, and historical boundaries are preserved without promoting the record's claims to current fact. Expect an authoritative decision or history record and a current applicability check where reused.

Research: [genre-specific criteria](02-genre-specific-quality-criteria.md) and [freshness](07-freshness-staleness-and-change-impact.md).

### G08 — Generated and navigation

Ask whether canonical inputs, generator, selection and ordering rules, transformation lineage, baseline, gaps, and deterministic reproduction are visible, with no invented priority, sequence, claim, or false completeness. Expect reproduction from named inputs plus semantic and journey review of the output.

Research: [information architecture](05-information-architecture-for-atomic-documentation.md), [transformation fidelity](llm-authored-documentation-failures/10-transformation-and-summarization-fidelity.md), [coverage inflation](llm-authored-documentation-failures/16-coverage-inflation.md), and [evaluation and accountability](llm-authored-documentation-failures/20-evaluation-provenance-and-accountability.md).

## Additional controls for agent-authored or agent-transformed content

These controls apply when an agent generates, rewrites, merges, summarizes, splits, extracts, or propagates documentation. They supplement the artifact criteria; they are not a substitute for them.

### A01 — Evidence selection record

Record the instruction sources, repositories and revisions in scope, sources considered, sources actually used, retrieval failures, exclusions, and unresolved gaps. Retrieval success shows that evidence was available, not that the selected set was sufficient.

Research: [context selection](llm-authored-documentation-failures/01-context-selection-and-evidence-sufficiency.md).

### A02 — Tool evidence envelope

For material observations, retain working directory, branch and revision, command or tool, inputs, environment, status, relevant output, truncation, timeout, fallback, and postcondition. Reassert state at tool and handoff boundaries. Empty output, partial results, fallback behavior, or a zero exit status must be interpreted by the tool's contract.

Research: [tool-mediated failures](llm-authored-documentation-failures/02-tool-mediated-evidence-failures.md).

### A03 — Claim ledger and evidence typing

Decompose consequential prose into checkable claims and classify each as current implementation, runtime behavior, intent, requirement, history, testimony, or inference. Map each material claim to evidence at the matching layer and keep unsupported or conflicting claims visible. Negative and exhaustive claims require a bounded search or inventory.

Research: [technical hallucination](llm-authored-documentation-failures/04-technical-hallucination-and-unsupported-inference.md), [code fidelity](llm-authored-documentation-failures/06-code-to-document-semantic-fidelity.md).

### A04 — Temporal coherence

Pin material observations to the revision and state actually inspected. Detect dirty, sparse, partial, merged, or mixed checkouts and distinguish historical evidence from current applicability. When a document mixes evidence times intentionally, label the boundary at the affected claim.

Research: [temporal coherence](llm-authored-documentation-failures/03-temporal-and-revision-coherence.md).

### A05 — Transformation and lineage control

Treat summaries, rewrites, merges, splits, translations, generated indexes, and copied claims as transformations with lineage. Compare before and after for lost scope, preconditions, exceptions, certainty, normative force, authority, and links. Deduplicate support by independent root evidence, not by citation or wording count, and propagate corrections to descendants.

Research: [transformation fidelity](llm-authored-documentation-failures/10-transformation-and-summarization-fidelity.md), [cross-document drift](llm-authored-documentation-failures/14-cross-document-consistency-and-terminology-drift.md), [error propagation](llm-authored-documentation-failures/15-error-propagation-and-false-consensus.md).

### A06 — Explicit gap and uncertainty representation

Give missing topics, unavailable evidence, unknown applicability, conflicts, and unverified claims first-class states. Do not ask the same generation process to infer its own omissions solely by rereading a fluent draft. Preserve caveats where they change the conclusion, and do not use hedging style as a substitute for calibrated evidence.

Research: [omissions](llm-authored-documentation-failures/07-omissions-and-false-completeness.md), [deceptive fluency](llm-authored-documentation-failures/13-epistemic-calibration-and-deceptive-fluency.md), [coverage inflation](llm-authored-documentation-failures/16-coverage-inflation.md).

### A07 — Instruction, evidence, and authority separation

Treat retrieved and repository content as evidence, not executable instruction, unless an authorized control channel says otherwise. Reading authority does not imply tool, publication, or policy authority. Restrict sources and privileges, validate outputs independently, and stop if untrusted text attempts to redirect the task or expand scope.

Research: [adversarial context](llm-authored-documentation-failures/17-adversarial-context-prompt-injection-and-source-poisoning.md).

### A08 — Human decision and review design

For consequential claims, require an accountable human decision at the appropriate domain, security, operational, accessibility, or policy boundary. Give reviewers an evidence-bearing change rather than only a polished draft; prompt them to look for omissions, contradictions, and absent authority. Use an independent view for high-risk claims when correlated generation and review could repeat the same error.

Research: [human review bias](llm-authored-documentation-failures/18-human-review-and-automation-bias.md), [evaluation and accountability](llm-authored-documentation-failures/20-evaluation-provenance-and-accountability.md).

### A09 — Bounded automation claims

Classify every check by what it can establish: deterministic formal predicate, bounded execution with an oracle, calibrated detector, assistive semantic judgment, or human decision. Report each result separately with its inputs and exclusions. Never turn green checks into a claim that the documentation is correct.

Research: [automated validation](llm-authored-documentation-failures/19-automated-detection-and-validation.md).

## Recommended corpus-review procedure

The criteria above become trustworthy only inside a controlled review process.

1. **Commission the review.** State the decision it must support, decision owner, audience, applicable criteria version, assurance sought, stopping rules, and handling of sensitive findings.
2. **Freeze and inventory the population.** Record the repository revision, canonical objects, delivery surfaces, generated views, journeys, and exclusions. Preserve changes during the review as a delta rather than silently moving the baseline.
3. **Define coverage obligations.** Derive needs from audiences, tasks, product surfaces, risks, lifecycle stages, variants, and authorities. Version this denominator.
4. **Apply deterministic census checks.** Run cheap explicit predicates over the whole population: schema, parse, path, symbol, link, secret-pattern, required-field, and reproducible-generation checks as applicable. Record failures and blind spots.
5. **Stratify by consequence and uncertainty.** Include all security-sensitive, destructive, recovery, normative, central, incident-affected, highly connected, volatile, weakly evidenced, and agent-transformed objects at appropriate depth.
6. **Select deep-review cases.** Combine the risk strata with a structured cross-section of genres, audiences, statuses, origins, surfaces, and authorship routes, plus a reproducible random sample from the remaining population. Expand when new defect classes appear.
7. **Review connected journeys.** Add prerequisites, transitions, maps, dependent nodes, executable artifacts, and rendered surfaces needed for complete reader tasks.
8. **Use fit methods.** Separate source examination, semantic comparison, execution, security review, accessibility evaluation, search testing, and reader task testing. Each method reports only the question it can answer.
9. **Record findings before editing.** Each finding names object and revision, criterion, condition, evidence, method, consequence, reach, confidence, and disposition. Sensitive findings stay outside the public register.
10. **Assign and remediate.** Give every finding an owner and decision authority. Update affected nodes, relationships, journeys, examples, generated views, and controls—not only the first visible instance.
11. **Retest and close.** Reapply the original criterion at a named new revision. A merged edit is not closure evidence by itself.
12. **Report bounded conclusions.** State population, baseline, criteria, coverage, methods, limitations, findings, remediation state, and residual risk. Bound every completeness claim to its purpose and baseline.

This combines full-population deterministic checks with risk-based depth and a random discovery sample. Risk-only review can miss unknown risks; deep review of everything is usually infeasible. The random sample discovers what the risk model failed to predict, while the risk strata protect high-consequence areas from being diluted by averages.

Primary research: [corpus-scale review](14-documentation-review-at-corpus-scale.md), [corpus coverage](04-measuring-corpus-completeness-and-coverage.md), and [automated validation](llm-authored-documentation-failures/19-automated-detection-and-validation.md).

## Review record and outcomes

A review record should keep these fields at minimum:

- **Review identity:** Review id, criteria version, commissioner, decision owner, lead, and report audience.
- **Object and baseline:** Object type, canonical id or path, revision, surface, and environment.
- **Context:** Audience, task, starting state, applicability, genre or artifact overlays, and exclusions.
- **Authorship and transformation:** Human, model, and automation contribution; source inputs; and generation or transformation lineage.
- **Method:** Criterion, method, tool and version, inputs, coverage, validation level, and relevant raw result.
- **Result:** One of `pass`, `finding`, `not applicable`, `unable to assess`, `accepted risk`, or private routing.
- **Finding:** Condition, evidence, effect, reach, confidence, severity, priority, and owner.
- **Limits:** Missing or inaccessible evidence, conflicts, assumptions, untested environments, and detector limits.
- **Closure:** Remediation revision, retest of the original criterion, residual risk, and deciding authority.

Finding types should remain distinct: defect, missing coverage, contradiction, observation, unable to assess, accepted risk, and sensitive stop-and-route. Severity, priority, and due date answer different questions and should be recorded separately.

## Reconciled tensions

The research raised several recommendations that look contradictory until their scope is made explicit.

- **Universal versus genre-specific criteria:** Use the universal profile for comparability, then a promise-specific overlay. Neither layer substitutes for the other.
- **Atomic nodes versus sufficient context:** Keep one maintainable purpose per node, but include enough local orientation for direct arrival and connect nodes through curated journeys. Atomic does not mean context-free.
- **Consistency versus truth:** Establish authority and truth before propagating consistent wording. Intentional audience terms and abstraction differences are mapped, not flattened.
- **Freshness versus recency:** Judge semantic applicability to a baseline. Dates and changes generate candidates; they do not decide truth.
- **Canonical terminology versus reader language:** Give concepts stable identity and scoped preferred labels while mapping legitimate synonyms, UI labels, protocol names, and legacy forms.
- **Completeness versus minimal documentation:** Define obligations for a bounded audience, task, risk, and baseline; include what those obligations require and omit the rest explicitly. Volume is not completeness.
- **Automation versus human review:** Automate explicit predicates and bounded executions. Use qualified humans for meaning, authority, safety, accessibility, and task fitness. Preserve the boundary in every result.
- **Human review versus automation bias:** Human sign-off is necessary at authority boundaries but is not sufficient. Reviewers need source evidence, omission prompts, and independent challenge for high-risk claims.
- **Transparency versus security and privacy:** Publish the stable security model, safe actions, assumptions, and limitations. Route secrets, personal data, private live controls, and uncoordinated vulnerabilities privately.
- **Provenance versus truth:** Preserve provenance so support, independence, revision, and correction can be assessed. Then test the claim; provenance alone does not make it true.
- **Code as truth versus product and runtime truth:** Use code for the implementation properties it can establish. Use tests, observation, configuration, deployment evidence, policy, decisions, and product intent for their respective claim layers.
- **Inspection versus usability:** Inspection detects many content defects; only realistic reader tasks establish quality in use. Apply each in proportion to consequence.

## Suggested adoption decisions

The research supports the shape of the model, but humans still need to decide how it becomes policy. The next decision should settle:

1. which hard gates and universal criteria are mandatory for all corpus content;
2. which genres and artifacts require which overlays;
3. what evidence depth and independent review each risk tier requires;
4. the authoritative coverage-obligation register and who may approve `not applicable`, intentional omission, exceptions, and accepted risk;
5. the review-record location, schema, retention, and public/private split;
6. the first frozen corpus baseline, sample design, task journeys, and stopping rules;
7. how findings become owned work and what evidence closes them;
8. which continuous, change-triggered, and periodic checks are resourced after the first review.

The first operational version should remain intentionally small: adopt the eight hard gates, twelve universal criteria, eight genre overlays, nine agent controls, and the review-record states in this document. Expand individual checklists only where the first review demonstrates ambiguity or missed defects. This recommendation is about reducing ceremonial complexity, not reducing assurance.

## Evidence map

This table links every report in the evidence set to its main contribution to the synthesis. The reports remain the source for detailed arguments, underlying citations, contrary evidence, and limitations.

### General technical-documentation research

1. [Quality model for technical documentation](01-quality-model-for-technical-documentation.md) — Multidimensional, contextual, non-compensatory quality model and method separation.
2. [Genre-specific quality criteria](02-genre-specific-quality-criteria.md) — Universal baseline plus eight functional genre families and template overlays.
3. [Truth and evidence in living technical documentation](03-truth-and-evidence-in-living-technical-documentation.md) — Claim-level evidence, entailment, authority, applicability, conflict, and validation boundaries.
4. [Measuring corpus completeness and coverage](04-measuring-corpus-completeness-and-coverage.md) — Versioned obligation denominator, traceability, explicit dispositions, and bounded completeness claims.
5. [Information architecture for atomic documentation](05-information-architecture-for-atomic-documentation.md) — Canonical nodes, facets, typed relationships, curated maps, and tested journeys.
6. [Documentation usability and findability](06-documentation-usability-and-findability.md) — Context of use, findability chain, realistic tasks, and limits of analytics.
7. [Freshness, staleness, and change impact](07-freshness-staleness-and-change-impact.md) — Semantic currency, change-triggered candidates, risk-based cadence, and historical disposition.
8. [Reviewing procedural and operational documentation](08-reviewing-procedural-and-operational-documentation.md) — Observable state transitions, safe execution, verification, recovery, escalation, and operational testing.
9. [Normative versus descriptive technical writing](09-normative-versus-descriptive-technical-writing.md) — Statement function, authority, applicability, enforcement, and intent/reality separation.
10. [Architecture-documentation quality](10-architecture-documentation-quality.md) — Stakeholder concerns, coherent views, decisions, quality evidence, and implementation mapping.
11. [Terminology and conceptual consistency](11-terminology-and-conceptual-consistency.md) — Concept identity and scoped terminology.
12. [Examples, commands, code, and configuration](12-examples-commands-code-and-configuration.md) — Executable artifact contract, validation ladder, safe context, outcome oracles, and source synchronization.
13. [Documentation accessibility and inclusive comprehension](13-documentation-accessibility-and-inclusive-comprehension.md) — Source and rendered accessibility, semantic structure, equivalent modes, comprehension, and task recovery.
14. [Documentation review at corpus scale](14-documentation-review-at-corpus-scale.md) — Frozen population, risk strata, census plus sampling, controlled findings, remediation, retest, and bounded reporting.
15. [Security and disclosure quality](15-security-and-disclosure-quality-in-public-technical-documentation.md) — Classification before publication, claim-layer verification, safe public model, private routing, disclosure, and maintenance.

### LLM-authored documentation failure research

1. [Context selection and evidence sufficiency](llm-authored-documentation-failures/01-context-selection-and-evidence-sufficiency.md) — Selection and retrieval limits, and the asymmetry between detecting insufficiency and proving sufficiency.
2. [Tool-mediated evidence failures](llm-authored-documentation-failures/02-tool-mediated-evidence-failures.md) — Observation loss, false success, state mismatch, evidence envelopes, and postconditions.
3. [Temporal and revision coherence](llm-authored-documentation-failures/03-temporal-and-revision-coherence.md) — Model, checkout, and evidence clocks; dirty, sparse, and mixed baselines; and claim-level time boundaries.
4. [Technical hallucination and unsupported inference](llm-authored-documentation-failures/04-technical-hallucination-and-unsupported-inference.md) — Hallucination taxonomy, granularity cliff, and claim-type-matched validation.
5. [Claim provenance and circular evidence](llm-authored-documentation-failures/05-claim-provenance-and-circular-evidence.md) — Fabricated, misapplied, mutable, and circular citations, and independence of support.
6. [Code-to-document semantic fidelity](llm-authored-documentation-failures/06-code-to-document-semantic-fidelity.md) — What static code can and cannot establish about flows, runtime, deployment, and intent.
7. [Omissions and false completeness](llm-authored-documentation-failures/07-omissions-and-false-completeness.md) — Invisible absence, template-filled false completeness, and independent denominators.
8. [Executable procedures, examples, and configuration](llm-authored-documentation-failures/08-executable-procedures-examples-and-configuration.md) — Relational executability, context assumptions, validation layers, authorization, and safe mediation.
9. [Normative distortion](llm-authored-documentation-failures/09-normative-distortion.md) — Separation of force, authority, claim mode, and enforcement, with a human decision gate.
10. [Transformation and summarization fidelity](llm-authored-documentation-failures/10-transformation-and-summarization-fidelity.md) — Scope, precondition, and certainty loss across rewriting, splitting, merging, compression, and propagation.
11. [Reader and task fitness](llm-authored-documentation-failures/11-reader-and-task-fitness.md) — Generic and verbose output biases, and task performance as the relevant outcome.
12. [Security, privacy, and disclosure failures](llm-authored-documentation-failures/12-security-privacy-and-disclosure-failures.md) — Information-flow boundary crossing, synthetic examples, publication-path scans, and specialist review.
13. [Epistemic calibration and deceptive fluency](llm-authored-documentation-failures/13-epistemic-calibration-and-deceptive-fluency.md) — Confidence and uncertainty failure, persuasive fluency, and format-biased review.
14. [Cross-document consistency and terminology drift](llm-authored-documentation-failures/14-cross-document-consistency-and-terminology-drift.md) — Repeated-edit drift, canonical volatile facts, impact discovery, and layered consistency review.
15. [Error propagation and false consensus](llm-authored-documentation-failures/15-error-propagation-and-false-consensus.md) — Derivation lineage, false multiplicity, effective source diversity, and correction fan-out.
16. [Coverage inflation](llm-authored-documentation-failures/16-coverage-inflation.md) — Visible numerator growth, biased denominators, stratified coverage, and the limits of volume metrics.
17. [Adversarial context, prompt injection, and source poisoning](llm-authored-documentation-failures/17-adversarial-context-prompt-injection-and-source-poisoning.md) — Instruction and evidence separation, least privilege, provenance, and independent validation.
18. [Human review and automation bias](llm-authored-documentation-failures/18-human-review-and-automation-bias.md) — Default acceptance, verification cost, cognitive forcing, accountable review, and appropriate reliance.
19. [Automated detection and validation](llm-authored-documentation-failures/19-automated-detection-and-validation.md) — Reliability ladder, explicit predicates, result envelopes, detector limits, and no aggregate green claim.
20. [Evaluation, provenance, and accountability](llm-authored-documentation-failures/20-evaluation-provenance-and-accountability.md) — Minimum provenance record, multidimensional quality profile, ownership, correction, and human decisions.

## Limitations

- This synthesis inherits the limitations of its 35 reports and does not independently revalidate every underlying external source.
- It proposes a review model but does not show how the current corpus performs against it. A favorable or unfavorable corpus conclusion would require the controlled review described above.
- The model does not supply numerical thresholds, criterion weights, sample sizes, review cadences, or risk tiers. Those depend on the decision, population, consequence, resources, and acceptable residual uncertainty.
- Direct empirical evidence about LLM agents authoring repository documentation is thinner than evidence about retrieval, code generation, automation bias, software documentation, accessibility, safety, and quality assurance separately. The agent controls are therefore mechanism-based and should be evaluated during the first review.
- Provenance records can be incomplete or false, human reviewers can share the same bias as the author, and automated validators can be misconfigured. Layering reduces these risks; it does not eliminate them.
- Adoption is still proposed; it requires a human decision and a maintained review package.
