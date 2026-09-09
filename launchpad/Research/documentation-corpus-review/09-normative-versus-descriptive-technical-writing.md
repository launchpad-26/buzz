---
description: Research into distinguishing normative, descriptive, aspirational, procedural, and predictive claims in the Buzz documentation corpus.
tags: [documentation, corpus, normative-language, descriptive-writing, requirements, authority, conformance, evidence, research]
---

# Normative versus descriptive technical writing

Researched 2026-09-07. This is research, not an adopted corpus standard.

## Research question

How should Buzz review technical writing so a reader can distinguish what is true now
from what is required, recommended, permitted, intended, predicted, possible, or merely
proposed—and can identify who has authority, what is in scope, how conformance is judged,
and what to conclude when implementation and policy disagree?

The investigation considered eleven subquestions:

1. What do *normative*, *descriptive*, *informative*, *prescriptive*, *requirement*,
   *recommendation*, *permission*, *constraint*, and *conformance* mean in the source
   traditions most relevant to Buzz?
2. Can a modal verb or capitalization convention make a statement authoritative?
3. How do IETF, ISO, NASA, W3C, and general developer-documentation conventions differ?
4. How should a reviewer distinguish a local obligation from a quoted or inherited
   external obligation?
5. Which statement functions are easily confused with one another?
6. What properties make a requirement reviewable and verifiable?
7. How should responsibility, scope, conditions, exceptions, enforcement, and lifecycle
   state be represented?
8. How should an intended requirement and its implemented behavior be documented when
   they agree or diverge?
9. Where may explanatory examples, rationale, notes, procedures, and predictions sit
   without accidentally changing conformance?
10. What can automated language checks detect, and what remains a semantic and
    authority judgment?
11. What does Buzz's current normative-language and evidence system already establish,
    and where does it remain ambiguous or unenforced?

## Bottom line

Normativity is an **authority-and-conformance relationship**, not a typographic effect.
A word such as `MUST`, `shall`, or `must` can signal the force a document intends, but it
cannot answer whether the document is authorized to impose that obligation, who is
bound, when it applies, how compliance is verified, or whether the requirement is
currently implemented.

Five distinctions should govern later checklist work:

1. **Statement function:** Is the sentence describing current or historical fact,
   assigning a definition, imposing a requirement or prohibition, recommending a
   course, granting permission, stating capability or possibility, predicting an
   outcome, expressing a goal, or instructing a reader through a procedure?
2. **Authority:** Who adopted or imposed the norm, through which current instrument,
   over which subject and audience? A quotation of an external `MUST` remains that
   source's requirement unless Buzz has adopted it.
3. **Conformance:** What observable criterion distinguishes compliant from
   non-compliant, under which conditions, and what exceptions or relief process exists?
4. **Reality:** Does code, configuration, a test, or observed workflow implement the
   norm? “Required” and “implemented” are separate claims even when both are true.
5. **Lifecycle:** Is the statement current, accepted but not implemented, proposed,
   superseded, historical, or unresolved? Future tense and confident prose are not
   lifecycle states.

The compact review model is:

> **Classify the speech act → identify the authority → bound the obligation → make it
> verifiable → compare it with reality → expose lifecycle and conflict.**

Buzz already has strong foundations: an active normative-language standard adopts the
BCP 14 vocabulary for corpus nodes; the evidence system distinguishes behavior claims
from intent claims; accepted decisions outrank code for authorization, while executable
evidence outranks prose for current behavior; and unresolved same-type authority
conflicts are meant to remain `flagged` for a human.

The important gaps are equally concrete. The normative-language standard is enforced
only by review. It explicitly says its reach into decision records is recommendation,
not authority. BCP 14 defines keyword meanings but does not grant a Buzz document local
authority. The current schema does not classify a claim as normative or descriptive,
connect a requirement to its responsible party or verification, or record whether an
accepted norm is implemented. A capitalized-word scan therefore finds candidates, not
requirements and certainly not compliance.

## Scope and method

This report concerns content whose interpretation changes depending on whether it tells
readers what *is* or what *ought, must, may,* or *is intended* to be. It applies to
policies, standards, specifications, invariants, architecture principles, requirements,
decision summaries, procedures, and explanatory nodes that quote or discuss them.

It does not decide:

- whether Buzz should replace its BCP 14 convention with ISO or NASA vocabulary;
- the substantive correctness of any current Buzz policy or requirement;
- who may create binding corpus policy beyond the authority already recorded locally;
- a schema migration, conformance system, waiver process, or automated linter;
- detailed architecture-document quality, terminology consistency, or code-example
  review, covered by later topics; or
- LLM-specific generation and review controls, which remain set aside for this research
  sequence.

Local inspection covered the corpus authoring guide, normative-language,
documentation-standard, evidence, confidence, status, and decision-reference standards;
the policy and specification templates; the decision-record lifecycle; Launchpad's
vision markers; and representative architecture, lifecycle, and agent-invariant nodes.
A read-only scan then counted normative-keyword-shaped tokens in the body of all 205
canonical nodes, excluding front matter and the schema subtree. Counts include quoted
and metalinguistic uses and are therefore candidate counts, not requirement counts.

External sources were selected in this order:

1. the IETF's BCP 14 and RFC style guidance;
2. ISO's public drafting and conformance guidance;
3. NASA's current directives and software-requirements guidance;
4. W3C specification-authoring guidance on normative and informative material;
5. public ISO/IEC/IEEE requirements-engineering definitions;
6. Google's developer-documentation guidance as a contrasting prose convention; and
7. peer-reviewed empirical work on automatic detection of requirement “smells.”

The vocabularies are not interchangeable. IETF guidance is for protocol specifications;
ISO's verbal forms are for ISO deliverables; NASA's `shall` convention is tied to its
directives and engineering processes; W3C guidance is for technical reports; and Google
is advising general developer documentation rather than defining conformance. Their
disagreement is evidence that a corpus needs a declared local convention, not evidence
that one authority is universally right.

## Definitions and statement functions

### Normative, descriptive, and informative are not grammatical synonyms

| Term | Meaning here |
|---|---|
| Normative statement | A statement that imposes, prohibits, recommends, or permits conduct or system behavior under an identified authority and scope |
| Requirement | An objectively assessable criterion that must be met to claim the relevant conformance or satisfy the governing authority |
| Prohibition | A requirement that specified conduct or state must not occur |
| Recommendation | A preferred course from which departure is allowed under stated or understood conditions |
| Permission | An authorized option; choosing not to use it is not non-conformance |
| Descriptive statement | A claim about what is or was true, including observed behavior, structure, history, ownership, or the content/status of another record |
| Informative material | Material that assists understanding or use but does not itself create conformance obligations in the document's declared scheme |
| Prescriptive guidance | Advice or instruction that selects a course of action; it may be a recommendation or procedure without being a binding organizational norm |
| Constraint | A limitation imposed from outside the solution or subject under design |
| Conformance | Fulfilment of the specified requirements applicable to a declared subject and scope |
| Enforcement | A mechanism that detects, prevents, rejects, remediates, or otherwise responds to violation; distinct from the existence of the requirement |
| Verification | Objective evidence that specified requirements were fulfilled |
| Validation | Evidence that requirements or a system serve the intended use; not simply a synonym for schema checking |

Several grammatical forms can carry either function:

- “The relay rejects unsigned events” is descriptive if reporting current behavior.
- “The relay **MUST** reject unsigned events” is normative under Buzz's declared
  convention if the document has authority over that subject.
- “ADR-XXXX requires the relay to reject unsigned events” is a descriptive claim about
  a normative source. Its truth depends on the ADR, not on current code.
- “Reject unsigned events” can be a procedural imperative to an operator, a requirement
  in a checklist, or concise advice. Genre and authority decide which.
- “The relay will reject unsigned events” can describe expected behavior, promise future
  behavior, or hide an unapproved plan. Future tense does not resolve the ambiguity.
- “The relay should reject unsigned events” can mean recommendation, expectation, or
  an author's belief about current behavior.
- “The relay may reject the event” can grant permission or report possibility.
- “The relay can reject the event” usually states capability, but some style guides use
  `can` for an optional reader action.

A reviewer cannot classify these safely by modal verb alone.

### Normative status exists at several levels

A document can be authoritative as a whole without every sentence being a requirement.
Its requirements can include declarative definitions, tables, algorithms, and formulas,
not only modal sentences. Conversely, an informative document can quote `MUST` without
acquiring authority over the reader.

The levels to distinguish are:

1. **Instrument status:** Is the document accepted, proposed, superseded, draft,
   informative, or historical?
2. **Section status:** Is this section normative or informative?
3. **Statement force:** Does the sentence impose a requirement, recommendation,
   permission, or no norm at all?
4. **Referenced dependency:** Is a cited source necessary for conformance or merely
   useful background?
5. **Implementation status:** Is the norm enforced, tested, partly implemented, known to
   be violated, or not checked?

Collapsing these levels creates familiar errors: treating an accepted document's
rationale as a requirement, treating an example as the only conforming implementation,
treating a proposal's `MUST` as current policy, or treating green code as proof that a
behavior was authorized.

## There is no universal normative keyword set

### IETF: uppercase BCP 14 terms

[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) defines `MUST`, `MUST NOT`,
`SHOULD`, `SHOULD NOT`, and `MAY`, with synonyms, for requirement levels in IETF
documents. `MUST` is absolute within the specification; `SHOULD` permits departure only
after weighing the implications; `MAY` is truly optional. It also says these terms
should be used carefully and sparingly, particularly for interoperability or harm.

[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html) clarifies that the special
meanings apply only to fully capitalized forms when the BCP 14 convention is invoked.
It makes an equally important point: normative text does not require these keywords.
The words aid clarity and consistency; they do not define the whole set of normative
content.

[RFC 7322](https://www.rfc-editor.org/rfc/rfc7322) requires a document using the IETF
interpretation to state or cite that interpretation. It also notes that requirement
keywords are technical content normally motivated by interoperability. RFC 2119 itself
says their force is modified by the requirement level of the containing document. A
`MUST` therefore cannot bootstrap an informational draft into an adopted standard.

### ISO: shall, should, may, and can

ISO's public drafting guidance uses a different controlled vocabulary:

- `shall` for a requirement;
- `should` for a recommendation;
- `may` for permission; and
- `can` for possibility or capability.

ISO also defines a requirement in relation to objectively verifiable criteria and a
claim of conformance. Its public guidance stresses that ISO standards are voluntary and
do not themselves create legal or contractual obligations; another instrument can make
their use obligatory. This is the cleanest evidence that requirement wording and the
source of obligation are separate questions.

### NASA: shall, accountable actor, and verification

NASA's current directive-writing rules also use `shall` for mandatory compliance, but
add structural requirements that are more important than the word. Each requirement is
to identify an accountable official or organization, a specific action, and how
compliance will be measured or verified. Requirements are stated separately, use active
voice, and should be significant enough that deviation warrants a waiver or other
relief.

NASA's software-requirements handbook similarly recommends unique identifiers, one
requirement per statement, traceability, unambiguous and measurable wording,
implementation freedom, stakeholder review, and verification. Its systems-engineering
checklist distinguishes `shall` as requirement, `will` as fact or declaration of
purpose, and `should` as goal. These are NASA conventions, not definitions Buzz inherits.

### W3C: partition normative and informative material

The W3C Manual of Style requires authors to make normative and informative material
visibly distinct. Entirely informative documents should say so and avoid requirement
keywords; informative sections should be labeled; and examples, figures, and notes are
treated as informative so they do not unexpectedly create conformance obligations. Its
older specification-quality guidance describes normative content as the prescriptive
part against which conformance is measured and recommends atomic, identifiable
conformance requirements.

This partition solves a different problem from modal vocabulary: it tells readers where
requirements may live and what supporting material cannot silently require.

### General developer documentation: optimize for action clarity

Google's developer-documentation guide illustrates why ordinary documentation may
choose another style. It recommends `must` or an imperative for required reader actions,
`can` for optional actions, `might` or `can` for possible outcomes, and an explicit “We
recommend” formulation for recommendations; it generally avoids `should` because the
word can blur recommendation, expectation, and state.

That advice is useful for procedures and explanatory prose, but it conflicts with
Buzz's current rule that lowercase `must`, `should`, and `may` do not carry binding force
in corpus policy. A reviewer must apply Buzz's declared convention within its scope,
while still asking whether an action-oriented page is a procedure rather than a
conformance specification.

## A review model for normative claims

### 1. Classify what the sentence is doing

Use a rewrite test. Replace the sentence with the closest explicit form:

- **Observation:** “At revision X, component Y does Z.”
- **Historical fact:** “Between A and B, policy Y required Z.”
- **Definition:** “Within this document, term Y means Z.”
- **Requirement:** “Authority A requires subject Y to satisfy Z under condition C.”
- **Prohibition:** “Authority A forbids Y from doing Z under C.”
- **Recommendation:** “Authority A recommends Z; departure is allowed for these
  reasons.”
- **Permission:** “Authority A permits Y to choose Z.”
- **Capability/possibility:** “Y is able to do Z” or “Z can occur.”
- **Prediction/expectation:** “Given C, Z is expected but not guaranteed.”
- **Goal/aspiration:** “The project seeks Z; it has not adopted or implemented it.”
- **Procedure:** “To obtain outcome Z, perform action Y.”

If two rewrites fit, the sentence is ambiguous. “The value should be true” is the
classic case: it might mean the user must set it, the system normally sets it, or a false
value should initiate recovery. Split or rewrite it.

### 2. Establish the authority chain

For every local norm, review:

- **issuer:** person, role, decision body, standard, specification, contract, regulator,
  or governing file;
- **authority source:** the current accepted instrument that permits the issuer to bind
  this subject;
- **subject:** implementation, operator, contributor, reviewer, document, service, or
  external implementer;
- **scope:** repository, subsystem, interface, version, environment, audience, and time;
- **effective state:** proposed, accepted, active, superseded, expired, or historical;
- **precedence:** what wins when local documents or external authorities conflict; and
- **change and relief:** who may amend, supersede, waive, or interpret it.

Do not infer authority from location, filename, `active` status, confident tone, or
capitalization alone. Those may be part of a locally adopted authority system, but the
chain still needs to be stated or discoverable.

### 3. Separate imported, adopted, and local requirements

External normative text can appear in Buzz in at least four ways:

1. **Description:** “NIP-X requires clients to do Y.” This reports the external norm.
2. **Applicability:** “Because Buzz implements NIP-X version V, NIP-X requirement Y
   applies to this surface.” This needs evidence for both the external requirement and
   the adoption/applicability claim.
3. **Local adoption:** “Buzz requires Y, adopting NIP-X's rule.” This needs a local
   authority capable of making that choice.
4. **Quotation or example:** external words are reproduced for explanation without
   becoming local requirements.

A citation proves none of these transformations by itself. Review the external source's
own status and version, the local adoption decision, the exact scope adopted, and any
intentional profile or extension. Preserve its native normative vocabulary inside a
quotation; use Buzz's convention when stating Buzz's own norm.

### 4. Make each obligation atomic and testable

A reviewable requirement should identify:

- a responsible subject;
- one required behavior or property;
- conditions and triggers;
- object and scope;
- quantitative bounds, enumerated states, or other observable success criteria where
  applicable;
- exceptions or absence of exceptions;
- rationale outside the requirement when needed;
- stable identifier;
- parent authority or derivation;
- verification method and evidence; and
- enforcement or the explicit fact that none exists.

Challenge these requirement smells:

- compound obligations joined by `and`, `or`, or nested lists;
- passive voice that hides the responsible actor;
- vague subjects such as “the system,” “the team,” or “it” where several qualify;
- loopholes such as “where possible,” “as appropriate,” “normally,” or “if needed”
  without a decision rule;
- subjective qualities such as “easy,” “secure,” “robust,” or “sufficient” without a
  measure or accepted evaluation method;
- comparatives and superlatives without a fixed baseline;
- open-ended phrases such as “including but not limited to” in a conformance set;
- unstated units, tolerance, timeframe, or environmental conditions;
- negative wording that leaves the desired state unclear;
- implementation detail presented as the need when multiple solutions should remain
  valid; and
- a requirement so trivial that a violation would never trigger correction or relief.

The 2017 Requirements Smells study operationalized several of these language signals
and tested a detector across three industrial and one academic context. Its average
precision was 59% and recall 82%, with substantial variation. The authors present smell
detection as a supplement to review, not an automatic defect verdict. That result is
directly relevant to any future Buzz linter: suspicious wording is a queue, while domain
meaning, authority, and acceptability remain human judgments.

### 5. Keep requirement, rationale, example, and procedure distinct

Supporting content makes norms usable but can accidentally change them.

| Content | Purpose | Review boundary |
|---|---|---|
| Requirement | Define the conformance obligation | Must stand alone and survive removal of rationale or example |
| Rationale | Explain why the norm exists and consequences of departure | Must not introduce an extra obligation |
| Example | Demonstrate one conforming or non-conforming instance | Must not imply it is the only implementation unless the requirement says so |
| Note | Add clarification or context | Must not contain indispensable conformance content under the declared convention |
| Definition | Fix the meaning of a term | Can be normative even without a modal if conformance depends on it |
| Procedure | Help a reader achieve an outcome | An imperative necessary for task success is not automatically an organizational requirement |
| Enforcement description | State what tooling or review currently checks | Must not be written as though desired enforcement already exists |
| Future work | Record an unresolved need or proposal | Must not be phrased as current policy or current behavior |

The test is subtractive: if removing an “informative” note, example, or rationale changes
what must be done to conform, the normative boundary is false.

### 6. Pair intent with reality without merging them

For a normative claim, ask two independent questions:

1. **What is authorized or required?** Cite the accepted decision, ratified
   specification, governing standard, contract, or other authority.
2. **What is implemented and verified?** Cite code, configuration, schema, a passing
   test, a controlled observation, or another executable source appropriate to the
   behavior.

The answers can form four states:

| Norm adopted? | Behavior implemented? | Honest documentation |
|---|---|---|
| Yes | Yes | State two claims with their separate evidence; name verification scope |
| Yes | No or partly | State the requirement and the implementation gap together; do not soften the norm or claim compliance |
| No | Yes | Describe observed behavior; do not launder it into authorized policy |
| No | No | Label proposal, goal, or open question; it is not current corpus truth |

When two accepted authorities over the same intent claim disagree, code cannot resolve
the policy conflict. When two executable sources disagree about current behavior, a
decision cannot make the observed inconsistency disappear. Buzz's existing
claim-type-aware precedence is stronger than a single hierarchy precisely because it
keeps these cases apart.

## Findings in the current Buzz corpus

### Buzz has an explicit local vocabulary

The active [normative-language
standard](../../docs/corpus/standards/normative-language.md) adopts `MUST`, `MUST NOT`,
`SHOULD`, `SHOULD NOT`, and `MAY` in the RFC 2119/8174 sense for corpus nodes. It
requires full capitals for binding statements, distinguishes lowercase ordinary English,
requires attribution when importing an external obligation, separates MUST-class and
SHOULD-class statements, and advises sparse, checkable use.

That is a coherent local choice. The external comparison adds three caveats:

- RFC 8174 explicitly says normative text does not require BCP 14 keywords. Buzz's rule
  that binding corpus statements use them is therefore a stricter local convention, not
  a requirement inherited from BCP 14.
- RFC 2119 focuses the keywords on interoperability and harm in technical
  specifications. Buzz also applies them to document-authoring and review policy. The
  definitions transfer, but the wider subject scope is Buzz's choice.
- BCP 14 defines the meaning of tokens inside an applicable document. It does not grant
  a corpus node authority to make Launchpad policy. That authority must come from the
  local governance chain.

### The authority boundary is recorded but incomplete

The normative-language standard says it is the first local source of the keyword rule,
not a restatement of an accepted ADR. It also says its reach into
`launchpad/decisions/` is recommendation because the decision-record lifecycle does not
defer to corpus standards. This is admirably candid and a material boundary: the same
keywords can be governed in corpus nodes but merely conventional in ADRs.

The documentation-standard node supplies a local review-enforced shape for standards
and says topic-specific standards win on their subject. The corpus's nearest
`AGENTS.md` is a governing instruction file. Even so, no single machine-readable chain
answers “this active standard is authorized to bind every corpus node because X.” A
future synthesis should not silently turn the standard's self-described scope into
broader authority than the repository grants.

### Buzz already separates intent and behavior evidence

The [decision-reference
standard](../../docs/corpus/standards/decision-references.md) asks a decisive question:
if code and a decision disagree, which one would be considered defective? If the
decision is outdated, the claim is about behavior and executable evidence controls. If
the code has drifted, the claim is about intent and the accepted decision controls.

This is the corpus's most valuable existing protection against normative/descriptive
confusion. It also reveals current enforcement limits: validation cannot determine claim
type, read ADR status, test whether a decision supports a claim, or detect two
contradictory decisions. The reviewer holds all four judgments.

### Lifecycle markers outside the corpus provide a useful model

[Launchpad's vision](../../VISION.md) explicitly marks claims `IMPLEMENTED`,
`DECIDED`, `PROPOSED`, or `OPEN`, with evidence expectations for each. It also warns
that a section-level marker does not automatically cover a later row. This is a strong
local example of separating present truth from accepted intent and proposal—and of why
status granularity matters.

The markers are not corpus schema fields and should not be imported automatically. The
lesson is functional: every forward-looking statement needs an explicit state and
authority at the same granularity as the claim it qualifies.

### Normative wording is widespread but concentrated

The read-only body scan found:

- 205 canonical nodes;
- 58 nodes containing at least one BCP-14-shaped token;
- 896 token occurrences in those bodies;
- 45 of 46 governance nodes accounting for 830 occurrences;
- 10 of 48 architecture nodes accounting for 37;
- one of two agent nodes accounting for 27;
- two of 36 layer nodes accounting for two; and
- no occurrences in the 69 capability or four development nodes.

No node declares a relationship whose target is
`corpus-standard-normative-language`. Relationships are optional, so this is not a
violation. It does mean graph traversal cannot currently find all content that uses or
implements the standard, and a standard change has no explicit relationship-based
impact set.

The 896 figure is not a requirement count. It includes headings, explanations of the
keywords, quotations, and references to named requirements. That limitation is the
point: lexical automation can find review candidates but cannot identify normative
force.

### Current nodes contain the exact distinctions a reviewer must preserve

The [event-driven extension
principle](../../docs/corpus/architecture/principles/event-driven-extension.md) states a
MUST-level design rule and then explains that its authority comes from contributor
instructions rather than from current route topology. This is an intent claim whose
absence of mechanical enforcement is disclosed.

The [graceful-shutdown
node](../../docs/corpus/layers/lifecycle/graceful-shutdown.md) distinguishes observed
shutdown behavior from a separately sourced normative bound that is “not yet met.” This
is a good example of refusing to make desired and actual behavior agree on paper.

The [signed-events
principle](../../docs/corpus/architecture/principles/signed-events.md) begins with
uppercase `MUST NOT` and `MUST`, then says a failed event “must never” be silently
dropped. That lowercase phrase appears to carry binding force inside the same invariant.
Under the active local standard, it is a concrete review candidate: either make it part
of the uppercase requirement, or rewrite it as description if it is only reporting
behavior. A word scan can locate it; only semantic review can choose the repair.

### The checker does not inspect normative semantics

The normative-language standard states that nothing mechanically enforces its rules.
The node schema has no claim-function, authority, responsible-party, applicability,
requirement identifier, exception, verification, or implementation-state field. The
validator does not inspect body prose. Consequently, all of the following can pass:

- a proposal written as current policy;
- a descriptive sentence mislabeled with a binding keyword;
- an unauthorized requirement;
- an external `MUST` presented as Buzz's own;
- a compound or unverifiable obligation;
- a norm citing only implementation;
- a behavior claim citing only an ADR;
- a superseded decision presented as current authority; and
- a known implementation gap phrased as compliance.

These are not arguments that every field belongs in front matter. They are limits a
review checklist must state honestly.

## Candidate content-review checklist

These are research outputs for later synthesis, not current policy.

### Statement classification

- [ ] Can each consequential sentence be classified as description, definition,
  requirement, prohibition, recommendation, permission, possibility/capability,
  prediction, goal/proposal, or procedure?
- [ ] Does a sentence combine two functions that need separate claims and evidence?
- [ ] Are `should`, `may`, `can`, `will`, `required`, imperatives, and passive
  constructions interpreted from context rather than assumed from the word alone?
- [ ] Is every forward-looking claim explicitly accepted, proposed, open, or otherwise
  lifecycle-qualified at the claim's own granularity?
- [ ] Does informative material avoid creating indispensable obligations implicitly?

### Authority and applicability

- [ ] Does each norm identify or link to the current authority able to impose it?
- [ ] Are issuer, bound subject, object, repository or system scope, version,
  environment, audience, conditions, and effective period clear?
- [ ] Does the document say what wins if it conflicts with a schema, executable source,
  accepted decision, external specification, or more specific standard?
- [ ] Is an external obligation visibly attributed and distinguished from local
  adoption?
- [ ] If Buzz adopts an external requirement, is the adoption decision and exact profile
  or subset evidenced?
- [ ] Are superseded, expired, proposed, and historical authorities described as such?
- [ ] Are amendment, interpretation, exception, waiver, and escalation authorities
  stated where applicable?

### Requirement quality

- [ ] Does the requirement bind one identifiable actor, component, document, or role?
- [ ] Does it express one behavior or property rather than a compound set?
- [ ] Are trigger, preconditions, scope, object, bounds, units, tolerance, and timing
  precise enough for independent assessment?
- [ ] Are vague, subjective, comparative, superlative, open-ended, or loophole phrases
  replaced with criteria or explicitly justified?
- [ ] Is the requirement necessary, feasible, consistent with peer requirements, and at
  the correct abstraction level?
- [ ] Does it state the needed outcome without over-constraining implementation unless
  the implementation itself is the authorized constraint?
- [ ] Does it have a stable identifier when it must be cited, traced, tested, excepted,
  or superseded independently?
- [ ] Is rationale adjacent but outside the requirement?

### Normative and informative boundaries

- [ ] Does the document declare its normative convention and use it consistently?
- [ ] Are normative and informative sections or elements visibly distinguishable where
  both occur?
- [ ] Are examples clearly non-exclusive unless the norm intentionally permits only that
  realization?
- [ ] Do notes, diagrams, tables, definitions, algorithms, and appendices have an
  unambiguous conformance status?
- [ ] Would removing supposedly informative content leave the conformance obligations
  unchanged and complete?
- [ ] Are recommendations distinguishable from requirements, and permissions from
  capabilities or possible outcomes?

### Intent, implementation, and evidence

- [ ] Is the intent claim supported by its accepted authority rather than by code that
  happens to agree?
- [ ] Is the current-behavior claim supported by executable or observational evidence
  rather than by the document that desired it?
- [ ] When both claims matter, are they recorded separately with separate evidence?
- [ ] Is verification tied to the same subject, conditions, version, and criterion as the
  requirement?
- [ ] Does the content distinguish “specified,” “implemented,” “enforced,” “tested,” and
  “observed in one case”?
- [ ] Is absence of enforcement stated rather than converted into apparent compliance?
- [ ] Are mismatches exposed as gaps or conflicts instead of being reconciled by wording?

### Local Buzz convention

- [ ] Within the normative-language standard's actual scope, are binding keywords fully
  capitalized and limited to the declared set?
- [ ] Is lowercase modal language ordinary English rather than a hidden requirement?
- [ ] Are externally quoted or paraphrased BCP 14 terms visibly attributed?
- [ ] Are MUST-class and SHOULD-class rules separated where the current local standard
  requires it?
- [ ] Is the BCP 14 vocabulary being used for interoperability, harm, or another
  explicitly local purpose rather than decoratively?
- [ ] Does the content avoid assuming that the normative-language standard binds
  decision records, given the standard's own disclosed authority boundary?
- [ ] If a node depends on the normative-language standard, is that dependency discoverable
  enough for future change-impact review even though a relationship is not currently
  mandatory?

## Measures worth collecting

Useful measures concern interpretability, traceability, and conformance—not the density
of capital letters:

- requirements with an identifiable authority, subject, scope, and stable identifier;
- requirements linked to an applicable verification method and current result;
- adopted norms classified by implementation state;
- normative claims supported only by executable evidence and behavior claims supported
  only by decisions;
- external requirements with and without a local adoption/applicability record;
- proposed or superseded sources cited as current authority;
- requirement conflicts, waivers, exceptions, and unresolved interpretations;
- compound, vague, subjective, unbounded, or actorless requirement candidates;
- “informative” notes or examples that contain indispensable conformance content;
- normative-language findings accepted as intentional versus repaired after review; and
- latency from adopted requirement change to impact review of implementations, tests,
  procedures, and dependent nodes.

Treat these cautiously:

- total `MUST` count;
- ratio of `MUST` to `SHOULD`;
- percentage of uppercase modal words;
- absence of banned words;
- requirement length;
- number of linked tests without checking applicability or result; and
- a binary “policy compliant” label.

They can measure syntax or inventory. They cannot establish authority, necessity,
semantic precision, or conformance.

## Common failure modes

1. **Typography as authority:** capitalizing `MUST` in a draft or explanatory report is
   treated as making policy.
2. **Implemented therefore authorized:** current code behavior is rewritten as a
   requirement without an adopting decision.
3. **Required therefore implemented:** an ADR or specification is cited as proof of
   runtime behavior.
4. **External-MUST laundering:** another standard's requirement is paraphrased as
   Buzz's own without adoption or applicability evidence.
5. **Proposal laundering:** future tense, confident tone, or an issue's acceptance
   criteria are presented as current policy.
6. **Epistemic `must`:** “this must mean X” is mistaken for a requirement rather than an
   inference.
7. **Ambiguous `should`:** recommendation, expected state, and current defect are left in
   one sentence.
8. **Permission/capability collapse:** `may` or `can` leaves it unclear whether an actor
   is allowed or technically able to act.
9. **Actorless obligation:** passive voice states that something “must be reviewed” but
   nobody owns review or timing.
10. **Compound compliance:** one identifier contains several independently passable or
    fail-able obligations.
11. **Normative rationale:** an explanation adds an uncatalogued extra requirement.
12. **Example monopoly:** implementers believe one informative example is the only
    conforming design.
13. **Decorative severity:** excessive `MUST` usage erodes the distinction between
    conformance-critical and preferred behavior.
14. **Green-check equivalence:** schema validity or a keyword linter is reported as
    semantic compliance.
15. **Silent conflict repair:** an author chooses between authoritative sources instead
    of recording and escalating the contradiction.

## Competing positions and judgments

| Question | Position A | Position B | Research judgment for Buzz |
|---|---|---|---|
| Which mandatory word is best? | IETF uses uppercase `MUST`; ISO and NASA use `shall`; general docs often use lowercase `must` or imperatives | Each convention is optimized for its document system | Keep Buzz's declared local vocabulary unless humans decide otherwise; judge consistency and authority, not universal superiority |
| Must all normative content use BCP 14 words? | Keywords make obligations searchable and consistent | Definitions, tables, algorithms, and ordinary normative prose can bind without them | Within Buzz's currently declared scope, follow the local rule; still review non-keyword content for normative effect because RFC 8174 says normativity is broader than the keywords |
| Should normative and informative material be separated physically? | Clear partition protects conformance interpretation | Excessive partition can fragment explanations and harm usability | Label the boundary at the smallest level readers can reliably interpret; keep rationale and examples adjacent but unmistakably non-normative |
| Should every requirement dictate implementation? | Prescriptive detail can make conformance deterministic | Solution constraints reduce design freedom and become stale | Specify observable outcome by default; constrain implementation only when the mechanism is itself authorized and necessary |
| Can automation police requirement quality? | Keywords and smell dictionaries find issues cheaply | Meaning, authority, and acceptable ambiguity require domain judgment | Automate candidate detection and traceability; never promote findings directly to defects or compliance verdicts |
| Should actual behavior or accepted intent win? | Code is executable truth | Decisions define authorized truth | Ask which claim is being made; maintain both, expose mismatch, and use claim-type-specific authority |
| Should recommendations use `SHOULD`? | BCP 14 gives departure a disciplined meaning | General docs readers often read “should” ambiguously | Use `SHOULD` only in documents that invoke Buzz's convention; use explicit recommendation prose in action guidance where conformance is not intended |

## Claim ledger

| Claim | Main support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Normative force depends on document status and conformance context, not capitalization alone | RFC 2119/8174; ISO voluntary-standard guidance; NASA authority rules | Local systems can intentionally assign legal meaning to typography through an adopted rule | High |
| There is no universal mandatory modal vocabulary | IETF BCP 14, ISO drafting guidance, NASA requirements guidance, Google prescriptive-doc guidance | A project can and should adopt one vocabulary within a defined scope | High |
| Normative and informative material should be distinguishable | W3C Manual of Style and specification guidance; ISO distinction among provisions | Exact partition and markup depend on genre | High |
| Reviewable requirements need actor, atomicity, scope, traceability, and verification | NASA NPR 1400.1I; NASA Software Engineering Handbook; ISO/IEC/IEEE 29148 public definitions | Product requirements, process rules, and protocol conformance need different fields and abstraction | High for principle |
| Modal and smell scanning can assist but cannot decide defects | Femmer et al. multi-case study; BCP 14's contextual semantics | Tool performance and dictionaries will differ on Buzz content | High for limitation; medium for expected local utility |
| Buzz has a coherent BCP 14 convention for corpus nodes | Local normative-language standard | Its authority beyond corpus nodes is explicitly limited; nothing mechanically enforces it | High |
| Buzz's claim-type precedence correctly separates intent from behavior | Local decision-reference standard and ADR-0029 | The schema and validator do not enforce classification or conflicts | High as documented policy; not a claim of complete practice |
| Normative-language impact is not graph-discoverable today | Read-only scan: zero relationships target the normative-language standard | Relationships are optional and other discovery mechanisms could be added | High |
| The signed-events node contains an apparent lowercase binding statement | Local body text compared with normative-language Requirement 3 | Author intent was not elicited; semantic review must decide whether it binds or describes | Medium-high as a review candidate, not a final defect verdict |

## Uncertainties and limitations

- The complete normative clauses of ISO/IEC/IEEE 29148 and the current ISO/IEC
  Directives were not reproduced. Public ISO pages and the Online Browsing Platform
  supplied definitions and scope sufficient for the claims made here; no inaccessible
  clause is attributed.
- NASA guidance is intentionally strict because it governs directives and engineered
  systems. Not every field should be imposed on a low-consequence explanatory node.
- W3C and IETF guidance targets specifications. Procedures, tutorials, and descriptive
  architecture material may need clearer ordinary language rather than conformance
  boilerplate.
- Google's guide optimizes developer-documentation usability and does not create a
  standards conformance system. Its lowercase usage conflicts with Buzz's local policy
  convention and is presented as a countermodel, not a recommendation to mix styles.
- The Requirements Smells study used four contexts and reported substantial variation.
  Its precision and recall are not forecasts for Buzz.
- The local modal scan excluded front matter but did not parse quotations, code fences,
  tables, headings, or the semantic role of each occurrence. It deliberately cannot
  count requirements.
- Only representative content nodes were semantically inspected. The report does not
  claim the remaining keyword-bearing nodes comply or fail.
- “Authority” within a repository is partly social and procedural. A schema can record
  an authority edge but cannot prove that humans legitimately granted it.
- This research did not interview authors, reviewers, operators, or the humans who
  accepted current governance documents.

## Implications for later synthesis

The final checklist should review a claim through two parallel records:

| Normative record | Descriptive implementation record |
|---|---|
| Authority and lifecycle | Baseline and environment |
| Bound subject and scope | Observed component and behavior |
| Requirement/recommendation/permission | Implemented/not implemented/partial/divergent |
| Conditions and exceptions | Test or observation method |
| Stable identifier and parent/derivation | Result and limitations |
| Verification criterion | Evidence that the criterion was exercised |
| Enforcement or declared absence | Actual enforcement point and failure behavior |

They may be presented together, but they should not become one claim with one citation.

Four questions need explicit human resolution during synthesis:

1. What grants corpus topic standards authority over ordinary content nodes, and how
   should that chain be made discoverable?
2. Should `launchpad/decisions/README.md` adopt the corpus normative-language standard,
   define a separate ADR convention, or leave current practice informal?
3. Does Buzz want explicit requirement identifiers and links to verification for all
   MUST-class system claims, only policy/specification nodes, or a risk-based subset?
4. Should compliance with a normative-language standard be represented through graph
   relationships, structured claim metadata, review records, or only prose and review?

Until those decisions are made, reviewers should preserve the distinction Buzz already
gets right: an accepted requirement can be unimplemented, an implemented behavior can be
unauthorized, and honest documentation must be able to say both.

## Sources

### Standards and official guidance

- IETF, [RFC 2119 / BCP 14, *Key words for use in RFCs to Indicate Requirement
  Levels*](https://www.rfc-editor.org/rfc/rfc2119), 1997.
- IETF, [RFC 8174 / BCP 14, *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key
  Words*](https://www.rfc-editor.org/rfc/rfc8174.html), 2017.
- RFC Editor, [RFC 7322, *RFC Style Guide*](https://www.rfc-editor.org/rfc/rfc7322),
  2014.
- ISO, [*Foreword — Supplementary
  information*](https://www.iso.org/foreword-supplementary-information.html), including
  public definitions of requirements, recommendations, permissions, and capability.
- ISO, [*How to write
  standards*](https://www.iso.org/files/live/sites/isoorg/files/developing_standards/docs/en/how-to-write-standards.pdf).
- ISO/IEC/IEEE, [ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life
  cycle processes — Requirements
  engineering*](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A29148%3Aed-2%3Av1%3Aen),
  public scope and terminology.
- NASA, [NPR 1400.1I Chapter 3, *Requirements for the Content and Structure of NASA
  Directives*](https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_1400_001I_&page_name=Chapter3),
  effective 2024-11-01.
- NASA, [Software Engineering Handbook SWE-050, *Software
  Requirements*](https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604503/SWE-050%2B-%2BSoftware%2BRequirements).
- NASA, [Systems Engineering Handbook Appendix C, *How to Write a Good
  Requirement*](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/).
- W3C, [*Manual of Style — Normative
  material*](https://www.w3.org/guide/manual-of-style/#normative).
- W3C, [*QA Framework: Specification Guidelines — Clearly identify conformance
  requirements*](https://www.w3.org/TR/2003/CR-qaframe-spec-20031110/guidelines-chapter#Gd-identify-reqs).

### Practitioner and empirical sources

- Google, [*Prescriptive documentation*](https://developers.google.com/style/prescriptive-documentation),
  Developer Documentation Style Guide.
- Femmer, Méndez Fernández, Wagner, and Eder, [*Rapid quality assurance with
  Requirements Smells*](https://doi.org/10.1016/j.jss.2016.02.047), *Journal of
  Systems and Software* 123, 2017; [open manuscript](https://arxiv.org/abs/1611.08847).

### Local Buzz material

- [Corpus normative-language standard](../../docs/corpus/standards/normative-language.md)
- [Corpus documentation standard](../../docs/corpus/standards/documentation-standard.md)
- [Corpus evidence standard](../../docs/corpus/standards/evidence.md)
- [Corpus decision-reference standard](../../docs/corpus/standards/decision-references.md)
- [Corpus confidence standard](../../docs/corpus/standards/confidence.md)
- [Corpus status standard](../../docs/corpus/standards/status.md)
- [Corpus authoring guide](../../docs/corpus/AGENTS.md)
- [Policy template](../../docs/corpus/templates/policy.md)
- [Specification template](../../docs/corpus/templates/specification.md)
- [Launchpad vision](../../VISION.md)
- [Launchpad decision-record lifecycle](../../decisions/README.md)
- [Event-driven extension principle](../../docs/corpus/architecture/principles/event-driven-extension.md)
- [Signed-events principle](../../docs/corpus/architecture/principles/signed-events.md)
- [Graceful-shutdown node](../../docs/corpus/layers/lifecycle/graceful-shutdown.md)
