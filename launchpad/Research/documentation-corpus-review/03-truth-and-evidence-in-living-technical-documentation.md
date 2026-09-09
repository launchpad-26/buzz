---
description: Research into how content reviewers can assess truth, evidence, conflict, and temporal applicability in the living Buzz documentation corpus.
tags: [documentation, corpus, truth, evidence, provenance, review, research]
---

# Truth and evidence in living technical documentation

Researched 2026-09-06. This is research, not an adopted corpus standard.

## Research question

How can a reviewer decide whether claims in a living technical-documentation corpus
are adequately established, rather than merely cited, structurally valid, or once
true?

The investigation considered six subquestions:

1. What is the difference between a claim, a citation, provenance, evidence, an
   argument, and truth?
2. How should evidence authority change with the kind of claim being made?
3. What does source code, configuration, a passing test, runtime observation, an ADR,
   repository history, testimony, or inference actually establish—and where does each
   stop?
4. How should exact-version evidence and current-state evidence be combined?
5. How should reviewers handle conflicting, missing, negative, or private evidence?
6. Which parts of this work are already governed by Buzz's corpus standards, and what
   additional questions should appear in a future content-review checklist?

## Bottom line

A citation is neither evidence by default nor a truth guarantee. It becomes useful
evidence only after a reviewer establishes an entire chain:

1. the cited artifact is identifiable and accessible;
2. it is the artifact and version the author claims to have inspected;
3. it is relevant to the proposition;
4. its content actually supports that proposition;
5. it has authority for that **kind** of proposition;
6. it applies to the stated system version, environment, scope, and time;
7. the claim does not generalize beyond what the evidence establishes; and
8. material counterevidence has been considered.

For a living technical corpus, truth is best reviewed as a relationship among four
things:

> **proposition × meaning × context × time**

A statement can be supported at one revision and false at another, true in one
deployment and false in another, or accurate about intended behavior while disagreeing
with current implementation. “The source says this” and “the system does this” are
different claims. A useful review preserves that difference instead of declaring one
artifact the universal source of truth.

Buzz already has strong local rules for this problem. Its corpus schema encodes
`FACT`, `INFERENCE`, and `TEAM_KNOWLEDGE`; its evidence standard requires claim-to-ledger
coverage and source inspection; its confidence standard constrains inferences; and
ADR-0029 makes evidence precedence depend on whether the claim concerns current
behavior or intended/authorized behavior. This research should reinforce those rules,
not replace them.

The main addition for a future checklist is a **semantic evidence audit**. Schema and
citation validation can establish form, recognized citation shape, and—in some
cases—file existence. They cannot establish claim coverage, entailment, authority,
applicability, adequate scope, or the absence of counterevidence. Those remain human
review questions, assisted by targeted execution where practical.

Confidence is **high** in that overall conclusion. Confidence is **moderate** in the
exact eight-link chain and proposed review outcomes below: they synthesize assurance,
provenance, documentation-review, versioning, and local corpus practices but have not
yet been calibrated on a sample of Buzz nodes.

## Scope and method

This study concerns the epistemic content of canonical corpus nodes: what they claim,
how those claims are supported, and whether the support remains applicable. “Living”
means that the documented product, deployment, decisions, or practices can change
after a node is written. It does not imply that the prose is generated automatically.

This topic does not design:

- review cadence, ownership, expiry periods, or change triggers, which belong to the
  later freshness and staleness study;
- the corpus-wide coverage model, which belongs to topic 4;
- detailed execution rules for commands and examples, which belong to topic 12;
- disclosure rules for sensitive security material, which belong to topic 15; or
- LLM-specific fact-checking controls, which remain outside the current research scope.

Local inspection covered:

- the node schema and corpus validator;
- the corpus evidence, confidence, and review-requirements standards;
- ADR-0028 and ADR-0029;
- the project-intelligence claim contract and evidence-bundle implementation; and
- the corpus authoring instructions.

External research covered:

- ISO/IEC/IEEE standards for documentation review, verification, validation, and
  assurance cases;
- the OMG Structured Assurance Case Metamodel;
- the W3C PROV model and Data on the Web Best Practices;
- GitHub's permanent-link guidance;
- maintained docs-as-code guidance from Google; and
- empirical studies of documentation defects and code-comment inconsistency.

Primary standards, official documentation, and peer-reviewed research were preferred.
Only publicly accessible ISO abstracts and browsing material were used. No conformance
with ISO/IEC/IEEE 15026-2, ISO/IEC/IEEE 26513, or another paid standard is claimed.

As of the research date, ISO/IEC/IEEE 26513:2017 remains published but is marked for
revision, and an FDIS intended to replace it is under development. The draft was used
only to understand the direction of current terminology; it is not treated as an
adopted standard.
([ISO/IEC/IEEE 26513:2017](https://www.iso.org/standard/67417.html),
[ISO/IEC/IEEE FDIS 26513](https://www.iso.org/standard/89070.html))

## The local baseline

### What Buzz already encodes

The node schema requires every node to carry an `evidence` array. Every entry states a
claim and classifies it as `FACT`, `INFERENCE`, or `TEAM_KNOWLEDGE`. `FACT` and
`INFERENCE` require citations; `INFERENCE` also requires confidence; and
`TEAM_KNOWLEDGE` requires attribution through `provided_by`.
([node schema](../../docs/corpus/schema/node.schema.json))

The evidence standard gives those structural fields their review meaning:

- a `FACT` rests on a source the author opened and which directly supports the claim;
- an `INFERENCE` exposes a reasoning step from cited evidence rather than disguising
  it as observation;
- `TEAM_KNOWLEDGE` preserves attributed testimony instead of promoting it to fact;
- every substantive body claim needs a ledger entry, and every entry must support a
  body claim; and
- a ledger is a present snapshot, not a history of superseded entries.

It also states that a genuine conflict between authorities over the same claim type
must be flagged rather than silently resolved.
([evidence standard](../../docs/corpus/standards/evidence.md))

The confidence standard adds an important boundary: confidence measures assessed
strength of an inference, not probability that it is true, source quality, document
quality, or conflict. A high-confidence inference does not become a fact.
([confidence standard](../../docs/corpus/standards/confidence.md))

ADR-0029 supplies contextual precedence:

- for how the system **currently behaves**, executable evidence such as code,
  configuration, schema, and passing tests outranks documentation and history;
- for what is **intended or authorized**, accepted normative decisions outrank
  implementation that has drifted; and
- two authoritative sources addressing the same claim type in conflict leave the
  matter unestablished for human resolution.

It explicitly rejects both one fixed hierarchy for every claim and a
latest-timestamp-wins rule.
([ADR-0029](../../decisions/ADR-0029-corpus-evidence-precedence.md))

### What Buzz validates mechanically—and what it does not

Direct inspection of `validate.py` confirms that the validator parses front matter,
checks the schema, checks relationship resolution, classifies citation shapes, resolves
some repository paths, and reports other recognized forms as `UNVERIFIED`. It splits
the Markdown at the front-matter delimiter and does not assess body prose. Its
repository-path check establishes that a file exists, not that the cited line exists
or that the file supports the statement.
([corpus validator](../../project-intelligence/corpus/validate.py))

The local review-requirements standard therefore assigns reviewers work that
automation does not reach, including matching body claims to ledger entries, checking
that each source supports its statement, evaluating class honesty, and resolving or
escalating conflict.
([review requirements](../../docs/corpus/standards/review-requirements.md))

This local baseline is more specific than the external research. The external sources
help explain why these distinctions matter and where a future content checklist can
make the review more repeatable.

## What the external evidence establishes

### Provenance supports trust assessment; it is not truth itself

W3C PROV defines provenance as a record of the people, institutions, entities, and
activities involved in producing, influencing, or delivering a thing. Its overview
includes reproducibility, versioning, procedures, and derivation among the provenance
capabilities. Provenance supplies origin and history that a consumer can use when
judging trustworthiness.
([W3C PROV overview](https://www.w3.org/TR/prov-overview/))

The qualification matters. W3C's provenance-constraints recommendation says a valid
PROV instance represents a **consistent history** to which its defined reasoning can
be applied, and explicitly distinguishes that validity from ordinary logical validity.
Thus, internally consistent provenance can still describe an artifact whose content is
wrong. Provenance answers where information came from and how it changed; content
verification answers whether a particular proposition is established.
([W3C PROV constraints, §1.2](https://www.w3.org/TR/prov-constraints/#purpose))

For Buzz, this means a structurally valid evidence ledger is valuable and necessary,
but it is not a certificate that every body claim is true.

### Evidence must be connected to a claim by reasoning and context

ISO/IEC/IEEE 15026-2 defines an assurance case as an auditable artifact providing a
convincing and sound argument for a claim, based on tangible evidence under a given
context. Its public terminology separately identifies claims, evidence, context,
assumptions, and inference. The separation prevents an evidence artifact from being
treated as self-interpreting.
([ISO/IEC/IEEE 15026-2:2022](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:15026:-2:ed-2:v1:en))

OMG SACM 2.3 likewise models auditable claims, arguments, and evidence. It includes
states for claims needing support or defeated by counterevidence, and says confidence
in an assurance case can require examining an artifact's provenance, lifecycle, and
properties. Its evidence model includes documents, expert testimony, test results,
measurements, and process or product records, collected by systematic procedures.
([OMG SACM 2.3](https://www.omg.org/spec/SACM/2.3/PDF))

Buzz nodes are not formal assurance cases, and most should not become them. The useful
transfer is the logical separation:

| Element | Question for a corpus reviewer |
|---|---|
| Claim | What precise proposition is the node asking the reader to accept? |
| Evidence artifact | What observable source is offered? |
| Support relation | What in that source bears on the proposition? |
| Reasoning | Does the evidence state the proposition directly, or is a derivation required? |
| Context | For which version, environment, audience, and conditions does the support hold? |
| Assumption | What must be true but was not established here? |
| Counterevidence | What source challenges or limits the proposition? |

The table explains why “citation present” is too weak a review result. A citation names
an artifact; it does not encode the support relation or close the argument.

### Verification and validation answer different questions

The current ISO draft for reviewing information for users repeats established systems
engineering distinctions: verification confirms through objective evidence that
specified requirements are fulfilled, while validation confirms that requirements for
a specific intended use or application are fulfilled. It also defines testing as
execution under specified conditions with observed or recorded results and evaluation.
Its scope applies to initial development and subsequent releases.
([ISO/IEC/IEEE DIS 26513, terms 3.39, 3.46, and 3.47](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:26513:dis:ed-1:v1:en))

Applied to documentation:

- **document verification** can compare a claim with a specified source, contract, or
  implementation artifact;
- **document validation** asks whether the information works for the intended reader
  in the intended situation; and
- **execution evidence** must name conditions and observations rather than being
  generalized into an unrestricted claim.

A node can be verified against the wrong requirement, or accurately reproduce a source
that is not useful in the target context. Both verification and validation matter, but
they do not substitute for each other.

### Documentation truth decays through ordinary software change

Aghajani et al. analyzed 878 documentation-related artifacts from mailing lists,
Stack Overflow, issue repositories, and pull requests and produced a taxonomy of 162
issue types. Among 485 information-content artifacts, they identified 190
up-to-dateness issues. They define an outdated document as one that was correct and
complete before a change left it out of sync. In their sample, code changes commonly
triggered the discrepancy; the study also found cases where the implementation—not
the documentation—needed correction.
([Aghajani et al., *Software Documentation Issues Unveiled*, pp. 5–6](https://doi.org/10.1109/ICSE.2019.00122))

That last point is especially relevant to Buzz. A mismatch is evidence of a mismatch,
not proof that prose should always be changed to match code. The governing proposition
must first be identified: current implementation and intended contract can both be
accurately documented as different facts.

Wen et al. mined 3,323,198 commits across 1,500 Java projects and manually studied 500
commits likely to repair code-comment inconsistency. Their evidence concerns comments,
not standalone architecture or policy nodes, so it cannot quantify Buzz's risk. It does
show at scale that code and descriptive text do not automatically co-evolve and that
different code changes create different inconsistency risks.
([Wen et al., *A Large-Scale Empirical Study on Code-Comment Inconsistencies*](https://www.inf.usi.ch/lanza/PUBS/P/Wen2019a.pdf))

Google's maintained documentation guidance recommends changing documentation in the
same change as code and prefers a small body of fresh, accurate material over a large
collection in varying states of repair. This is practitioner guidance, not controlled
evidence, but it aligns with the empirical failure pattern.
([Google documentation best practices](https://google.github.io/styleguide/docguide/best_practices.html))

The detailed mechanisms for detecting and responding to decay belong to topic 7. For
this report, the implication is narrower: every current-state claim is implicitly
time-bound, even if its sentence contains no date.

### Immutable evidence and current evidence solve different problems

GitHub documents that a commit-based permalink preserves the exact file version a
person saw, while a branch URL can change as new commits arrive. A permanent link
therefore improves reproducibility of the author's evidence inspection.
([GitHub permanent links](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files))

W3C's Data on the Web Best Practices separately recommends identifiers for individual
versions and for the evolving series or latest version. Its rationale is that users
sometimes need the historical state and sometimes the current one. It also treats
provenance, version indicators, version history, data quality, and keeping material
up to date as distinct practices.
([W3C Data on the Web Best Practices, §§7 and 8.6](https://www.w3.org/TR/dwbp/))

This exposes a real trade-off:

- a **pinned source** shows exactly what supported the claim when it was written but
  says nothing by itself about whether the claim remains current;
- a **floating source** can show the latest material but cannot prove what the author
  reviewed; and
- a **recorded revision plus re-verification** preserves auditability while requiring
  reviewers to determine whether later changes affect the claim.

Pinning is therefore a provenance control, not a freshness control. Topic 7 should
decide how re-verification is triggered and recorded.

## A claim-type evidence map

No single evidence ladder works for all corpus claims. The following table adapts the
local ADR-0029 distinction and makes the review implications explicit.

| Claim type | Strong direct evidence | Important qualification |
|---|---|---|
| Current static implementation | Source code, configuration, schema, generated artifact at the relevant revision | Presence in code does not prove reachability, deployment, or runtime use |
| Current runtime behavior | Reproducible execution or observation tied to build, environment, inputs, and time | One observation establishes only the conditions exercised |
| Procedural success | Exact procedure exercised by a representative operator in a declared environment, with expected results | A successful happy path does not establish recovery, permissions, or other platforms |
| Intended or authorized behavior | Active ADR, ratified specification, policy, accepted product decision | Status, scope, precedence, and supersession must be checked; code may have drifted |
| Interface or compatibility contract | Normative specification plus conformance or integration evidence | One implementation cannot establish interoperability for every consumer |
| Historical event | Immutable commit, release record, PR, issue, or contemporaneous artifact | It establishes what the record contains; stated motives or outcomes may still be testimony or inference |
| Rationale | Accepted decision record or attributed testimony from decision participants | Code shape alone rarely establishes why a choice was made |
| Team practice or unwritten convention | Attributed testimony from the responsible people or accepted issue/decision | It remains team knowledge until corroborated by an authoritative artifact or observed practice |
| Negative or exhaustive claim | Bounded inventory or search with declared scope, method, revision, and exclusions | Failure to find something is not proof of universal absence |
| Derived conclusion | Cited premises plus visible reasoning and confidence | More citations do not remove an inferential step |
| External standard or product fact | Current primary publication from the responsible authority, preferably versioned | Secondary repetition is not independent confirmation; editions and applicability matter |

The table is not a policy hierarchy. It is a candidate routing aid: first classify the
claim, then ask what evidence could establish that kind of proposition.

## The semantic evidence audit

### 1. Claim identity

A reviewer must be able to isolate the proposition. Compound sentences are hazardous
when one citation supports only one clause or when current behavior, intent, and
rationale are compressed into one statement.

Useful questions:

- Can the statement be true or false as written?
- Does it contain more than one independently supportable assertion?
- Does it say whether it concerns current behavior, intended behavior, history,
  testimony, or inference?
- Are important qualifiers—version, environment, actor, condition, and scope—part of
  the claim rather than left to implication?

### 2. Claim-to-ledger coverage

The body and evidence ledger must cover each other in both directions. A source list at
the end of a node cannot show which source supports which claim, and one broad ledger
entry cannot honestly stand behind many unrelated sentences.

A reviewer should identify:

- substantive body claims with no ledger entry;
- ledger entries with no meaningful body counterpart;
- many body claims collapsed into one vague ledger statement; and
- repeated claims whose versions or qualifiers disagree.

### 3. Source identity and reproducibility

The reviewer should establish that the target exists, is the expected artifact, and can
be revisited. For repository evidence this includes checking the actual revision; for
runtime or tool results it includes enough conditions to repeat or challenge the
observation.

A precise-looking location is not necessarily a stable or valid one. The local
validator currently checks a cited path but not the semantic target or line bound. The
reviewer must not infer more precision than the mechanism provides.

### 4. Relevance and entailment

Two different checks are needed:

- **relevance:** the source concerns the same subject;
- **support:** the source states the proposition or supplies premises from which it
  follows.

A file about configuration is relevant to a default-setting claim, but it supports the
claim only if it actually defines that default under the applicable conditions. A test
named after a feature is relevant, but it supports the behavior claim only if its setup
and assertions exercise that behavior.

If reasoning is required, the result is an inference even when the premises are strong.

### 5. Authority for the claim type

Authority is contextual. The reviewer should ask not “Is this source authoritative?”
in the abstract, but “Is it authoritative for this proposition?”

- implementation can establish current mechanics but not team intent;
- an ADR can establish an accepted decision but not prove deployment matches it;
- a commit message can establish that an author wrote a rationale, not that the change
  achieved its stated outcome;
- testimony can establish what a person reports, not independently verify the system;
- external documentation can establish what its publisher claims, not necessarily how
  Buzz integrates or configures the product.

### 6. Applicability and time

The evidence and claim must share relevant conditions:

- repository revision or released version;
- deployment/community/environment;
- platform and configuration;
- inputs, permissions, and feature flags;
- date or observation window; and
- status or supersession state for decisions and policies.

The goal is not to add dates to every sentence. It is to prevent a timeless sentence
from silently generalizing revision-specific evidence.

### 7. Scope and sufficiency

Evidence may support a narrow claim while the prose makes a broad one. Reviewers should
look for jumps such as:

- one unit test → the feature works end to end;
- one local run → the procedure works in production;
- one implementation → the protocol is interoperable;
- one source file → no other implementation exists;
- one current config → all deployments use that value; or
- no search result → the item does not exist anywhere.

The repair is usually to narrow the claim, add evidence, or record a gap—not to raise a
confidence score until the sentence feels acceptable.

### 8. Counterevidence and conflict

A reviewer should deliberately seek the most plausible contradicting artifact when the
claim is consequential, surprising, contested, or security-sensitive. Counterevidence
can defeat a claim, narrow it, reveal that two sources concern different claim types,
or expose a genuine conflict requiring escalation.

The key distinctions are:

| Situation | Honest interpretation |
|---|---|
| ADR says behavior should be X; code currently does Y | Two propositions—authorized intent and current implementation—unless one source claims the other's domain |
| Two active policies impose incompatible requirements on the same subject | Genuine normative conflict; leave unestablished and escalate |
| Two runtime observations differ across environments | Context or nondeterminism must be investigated before claiming conflict |
| Newer source merely has a later timestamp | Recency alone does not establish authority or correctness |
| Strong evidence disproves a prior inference | Revise or remove the inference; do not average the disagreement into medium confidence |

## Evidence strength is not citation count

Multiple citations improve a claim only when they add something material. They may:

- independently corroborate the same proposition;
- establish different necessary parts of a compound argument;
- cover different environments or versions;
- supply authority and implementation evidence for distinct claim types; or
- expose a conflict that one source would conceal.

They do not add independent support when they repeat the same upstream source, cite
different files generated from the same input, or concern the subject without closing
the proposition. One definitive primary source can be stronger than ten derivative
pages. Conversely, a single source is insufficient when the claim generalizes across
implementations, environments, or perspectives that source does not cover.

## Candidate review outcomes

A single “evidence pass” obscures important differences. A future review record could
use outcomes like these without turning them into numeric scores:

| Outcome | Meaning |
|---|---|
| Established for stated context | Direct, applicable, authoritative evidence supports the claim at the reviewed revision and scope |
| Supported inference | Premises are evidenced and reasoning is visible, but the conclusion is not directly stated or observed |
| Attributed team knowledge | The corpus honestly records what an identified person or decision process supplied without independent corroboration |
| Narrower than written | Evidence supports a restricted version of the claim; prose must be qualified or further evidence added |
| Unsupported | Citation is missing, inaccessible, irrelevant, non-entailing, or unauthorized for the proposition |
| Stale or inapplicable | Evidence may have supported the claim previously or elsewhere but not for the asserted version/context |
| Contradicted | Applicable counterevidence defeats the claim |
| Flagged conflict | Same-claim-type authorities disagree and a human decision is required |
| Not verifiable publicly | Material evidence cannot be exposed; the claim must remain unestablished in the public corpus under current local policy |

These labels are a research proposal. Any adopted result vocabulary must align with the
existing `status` and evidence-class contracts rather than creating a second competing
state model.

## A candidate human review sequence

1. **Read the node as prose first.** Identify its purpose, boundaries, and material
   claims without letting the ledger pre-frame what appears important.
2. **Decompose compound claims.** Separate current behavior, intent, history, rationale,
   team knowledge, and inference.
3. **Map claims to entries.** Check body-to-ledger and ledger-to-body coverage.
4. **Check classification.** Confirm that direct observation, inference, and testimony
   have not been relabeled to sound stronger.
5. **Open the exact sources.** Confirm identity, revision, and accessibility; record any
   `UNVERIFIED` citation that received human inspection.
6. **Test semantic support.** Locate what in each source supports the whole statement.
7. **Test authority.** Decide whether the source can establish that kind of claim.
8. **Test applicability.** Compare revision, environment, status, and stated scope.
9. **Exercise high-risk claims where practical.** Run the real workflow or targeted
   test and record conditions and observations; do not generalize beyond them.
10. **Seek counterevidence.** Inspect the likely competing source, especially where
    implementation and accepted intent can diverge.
11. **Choose an honest outcome.** Establish, narrow, reclassify, mark unsupported,
    record a gap, or flag a true conflict.
12. **Re-read the node.** Ensure edits to prose and ledger still agree and that
    qualifications remain visible to the reader.

The sequence is deliberately claim-centered. It does not require reviewers to perform
the same expensive validation for every sentence; risk and consequence should govern
depth.

## Candidate checklist criteria

These are candidates for the eventual synthesis, not requirements in force.

### Claim definition and coverage

- [ ] Each substantive claim is specific enough to evaluate as written.
- [ ] Current behavior, authorized intent, history, testimony, and inference are not
      collapsed into one ambiguous statement.
- [ ] Material version, environment, actor, condition, and scope qualifiers are stated
      where they affect truth.
- [ ] Every substantive body claim maps to an evidence-ledger entry.
- [ ] Every ledger entry supports a claim the body actually makes.
- [ ] Compound claims are split when one source or classification cannot honestly
      support every clause.

### Source and citation

- [ ] The reviewer opened the cited source rather than relying on citation presence,
      path validity, search snippets, or an author's summary.
- [ ] The target is the intended artifact and version, and any location precision is
      genuine rather than decorative.
- [ ] An immutable reference preserves what was reviewed; current applicability is
      checked separately.
- [ ] Runtime and tool evidence records enough build, environment, inputs, command,
      time, and outcome information to interpret or repeat it.
- [ ] Secondary sources are traced to the underlying primary source when they carry a
      material claim.

### Semantic support

- [ ] The source is relevant to the exact proposition, not merely the same subject.
- [ ] The cited content supports the entire claim under the stated conditions.
- [ ] Any reasoning step from source to conclusion is visible and classified as
      inference.
- [ ] Assumptions and unverified premises are explicit.
- [ ] The claim is no broader than the evidence in system surface, version,
      environment, population, or time.
- [ ] Evidence quantity is not mistaken for independence, authority, or sufficiency.

### Claim-specific authority

- [ ] Current implementation claims use applicable executable evidence.
- [ ] Runtime claims use observation or execution evidence rather than static code
      alone.
- [ ] Intended or authorized behavior cites active decisions, specifications, or
      policies and checks status and supersession.
- [ ] Historical records are used to establish what the record contains, without
      automatically promoting stated motives or expected outcomes to fact.
- [ ] Rationale and team-practice claims preserve decision authority or attribution
      rather than being inferred from code shape.
- [ ] Negative and exhaustive claims name the bounded search or inventory from which
      they were derived.

### Conflict and uncertainty

- [ ] The reviewer sought plausible counterevidence in proportion to the claim's risk.
- [ ] Apparent conflicts were first tested for different claim types, versions, or
      environments.
- [ ] Same-claim-type authoritative conflict remains visible and is escalated rather
      than averaged, silently resolved, or hidden in confidence.
- [ ] Missing, private, inaccessible, or non-reproducible evidence is recorded as a
      limit rather than replaced by stronger wording.
- [ ] Evidence that disproves or narrows a claim causes the prose and ledger to be
      corrected together.

### Validation boundaries

- [ ] A green schema/citation-validation run is described only as structural success.
- [ ] `UNVERIFIED` citations receive explicit human handling.
- [ ] Passing tests are interpreted according to their actual setup and assertions,
      not their filename or success status alone.
- [ ] Successful execution is not generalized beyond the conditions exercised.
- [ ] Document verification against a source is not mistaken for validation with the
      intended reader and task.

## Competing positions and unresolved decisions

### “The code is the source of truth”

This is efficient for current implementation mechanics and avoids preserving obsolete
prose over executable behavior. It fails for intent, policy, rationale, requirements,
and cases where implementation is defective or undeployed. Aghajani et al. observed
real disputes over whether code or documentation should change, and ADR-0029 already
settles the local principle: authority depends on the claim type.

The useful replacement is not “documentation is the source of truth,” but “name the
proposition before choosing its authority.”

### “A passing test proves the documentation”

A targeted, passing test can be powerful evidence. Its strength comes from what it
sets up, executes, observes, and asserts—not from the word “pass.” Tests can omit
platforms, configurations, error paths, integration boundaries, or reader actions.
Static validation can also pass while never inspecting body semantics.

The right response is scoped interpretation, not distrust of tests. A narrow test
should support a narrow claim; broader claims need broader evidence.

### “Pin every source and the truth is reproducible”

Pinning makes the original review reproducible, which is essential for auditability.
It can also fossilize evidence. A pin proves what the source said then, not that the
node remains true now. Floating references have the opposite weakness: they can show
current content while erasing what the author reviewed.

The synthesis is to preserve the reviewed revision and separately perform current
applicability checks. Topic 7 must decide when that second check is due.

### “Require two sources for every fact”

Two independent sources can expose error and conflict, but a universal two-source rule
creates waste and false confidence. One schema file can definitively establish its
current enum; two blog posts repeating it add nothing. In contrast, a broad runtime or
interoperability claim may need multiple environments even if every result comes from
the same tool.

Corroboration should respond to uncertainty, consequence, and breadth—not a citation
quota.

### “Only publish claims that can be fully proved”

That rule would make the corpus deceptively sparse and discard valuable, honestly
attributed operational knowledge. The local classes exist to retain inference and team
knowledge without presenting either as direct fact. Assurance models likewise permit
assumptions, claims needing support, and defeated claims to remain visible.

The stronger principle is that no claim should assert more than was established.
Uncertainty is a content property to expose, not a reason to rewrite speculation as
certainty or delete every useful lead.

### “Automate the entire evidence audit”

Automation can check syntax, target resolution, hashes, schema, link health, generated
consistency, executable snippets, and some code-document relationships. The local
validator already provides meaningful safeguards. But natural-language entailment,
claim authority, contextual applicability, and material counterevidence often require
judgment and domain knowledge. W3C's valid provenance distinction is a formal example
of the boundary: consistency of the record is not truth of the content.

The appropriate target is layered automation with an explicit human semantic review,
not an undifferentiated green badge.

## Claim ledger

| Claim | Main support | Counterevidence or qualification | Confidence |
|---|---|---|---|
| Citation presence does not establish truth | Local validator behavior; local evidence standard; W3C PROV validity; ISO 15026 and SACM separation of claim, argument, evidence, and context | A direct citation to a definitive source can close a narrow claim after inspection | High |
| Truth in a living corpus is context- and time-dependent | ISO verification/validation definitions; W3C versioning guidance; empirical staleness studies | Some mathematical, definitional, or historical claims are comparatively stable | High |
| Evidence authority must depend on claim type | ADR-0029; assurance-case context model; empirical cases where either code or docs required correction | The exact precedence rules are local decisions, not a universal external standard | High for the need; high locally for the adopted rule |
| Provenance is necessary but not sufficient | W3C PROV overview and constraints; local ledger/validator boundary | Rich provenance materially improves trust assessment and reproducibility | High |
| Pinned and current references solve different problems | GitHub permalink guidance; W3C version/series identifiers | Repository-local citations plus a recorded revision may implement both differently | High |
| Current behavior needs more than static code for runtime claims | ISO testing definition; assurance evidence under context | Some static properties are completely determined by code/schema without execution | High |
| Documentation drift is a normal consequence of software evolution | Aghajani et al.; Wen et al.; Google same-change guidance | Comment studies do not directly measure Buzz's standalone corpus | High for general risk; unknown rate for Buzz |
| Counterevidence should be part of consequential claim review | SACM defeated/counterevidence model; ADR-0029 conflict rule | Exhaustive counterevidence searches are impossible, so depth must be risk-based | High |
| The proposed eight-link semantic chain will improve review repeatability | Synthesis of local controls and external models | Not tested for reviewer agreement, time, or defect yield | Moderate |

## Limitations

- No representative sample of completed Buzz nodes was audited using the proposed
  chain. The report analyzes standards and mechanisms rather than measured corpus
  defect rates.
- Empirical studies of code comments and general software documentation show plausible
  drift mechanisms but cannot quantify this corpus's risk.
- Public ISO material does not expose all normative requirements. This report cannot
  claim or evaluate conformance.
- The replacement ISO/IEC/IEEE 26513 edition is still under development as of the
  research date. Its public draft terminology may change.
- “Entailment” in technical prose is often judgment-dependent. The checklist can make
  reasoning visible but cannot guarantee reviewer agreement.
- Runtime truth can be nondeterministic, environment-specific, or inaccessible. One
  review cannot exhaust every deployment state.
- The proposed outcome labels could overlap with the existing node `status` and
  evidence classes. They should not be adopted without reconciling that interaction.
- Detailed freshness triggers, evidence-retention history, source ownership, and
  sensitive evidence handling remain for later research topics.

## Implications for the final synthesis

The final content checklist should place truth review ahead of prose polish. A likely
shape is:

1. identify and classify material claims;
2. verify body-to-ledger coverage;
3. apply the eight-link semantic evidence chain;
4. use a claim-type evidence route rather than a universal hierarchy;
5. distinguish pinned provenance from current applicability;
6. seek and preserve counterevidence;
7. narrow, reclassify, or flag claims rather than forcing a binary pass; and
8. state what mechanical validation did and did not establish.

Before adoption, reviewers should independently apply the model to at least these node
shapes:

- a current implementation reference;
- a policy or specification whose implementation may have drifted;
- a procedure containing commands;
- an architecture node with prose and a diagram;
- a test contract or threat model;
- a node relying on team knowledge; and
- a node with an intentionally negative or exhaustive claim.

The trial should record disagreements at each chain link. That will show whether the
model improves semantic review or merely gives reviewers more vocabulary for the same
intuition.

## Sources

### Local corpus sources

- [`node.schema.json`](../../docs/corpus/schema/node.schema.json)
- [`evidence.md`](../../docs/corpus/standards/evidence.md)
- [`confidence.md`](../../docs/corpus/standards/confidence.md)
- [`review-requirements.md`](../../docs/corpus/standards/review-requirements.md)
- [`AGENTS.md`](../../docs/corpus/AGENTS.md)
- [`ADR-0028-corpus-canonical-representation.md`](../../decisions/ADR-0028-corpus-canonical-representation.md)
- [`ADR-0029-corpus-evidence-precedence.md`](../../decisions/ADR-0029-corpus-evidence-precedence.md)
- [`CONTRACT.md`](../../project-intelligence/CONTRACT.md)
- [`corpus/evidence.py`](../../project-intelligence/corpus/evidence.py)
- [`corpus/validate.py`](../../project-intelligence/corpus/validate.py)

### External sources

- [ISO/IEC/IEEE 26513:2017 — Requirements for testers and reviewers of information for users](https://www.iso.org/standard/67417.html)
- [ISO/IEC/IEEE FDIS 26513 — Testing and reviewing of information for users](https://www.iso.org/standard/89070.html)
- [ISO/IEC/IEEE DIS 26513 public browsing material](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:26513:dis:ed-1:v1:en)
- [ISO/IEC/IEEE 15026-2:2022 — Assurance case](https://www.iso.org/standard/80625.html)
- [ISO/IEC/IEEE 15026-2 public terminology](https://www.iso.org/obp/ui/en/#iso:std:iso-iec-ieee:15026:-2:ed-2:v1:en)
- [OMG Structured Assurance Case Metamodel 2.3](https://www.omg.org/spec/SACM/2.3/PDF)
- [W3C PROV overview](https://www.w3.org/TR/prov-overview/)
- [W3C Constraints of the PROV Data Model](https://www.w3.org/TR/prov-constraints/)
- [W3C Data on the Web Best Practices](https://www.w3.org/TR/dwbp/)
- [GitHub — Getting permanent links to files](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files)
- [Google documentation best practices](https://google.github.io/styleguide/docguide/best_practices.html)
- [Aghajani et al., *Software Documentation Issues Unveiled*](https://doi.org/10.1109/ICSE.2019.00122)
- [Aghajani et al. preprint](https://csnagy.github.io/research/pdfs/2019/Aghajani2019-preprint.pdf)
- [Wen et al., *A Large-Scale Empirical Study on Code-Comment Inconsistencies*](https://www.inf.usi.ch/lanza/PUBS/P/Wen2019a.pdf)
