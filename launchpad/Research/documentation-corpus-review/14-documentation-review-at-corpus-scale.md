---
description: Research into designing and operating an evidence-backed review programme for the Buzz documentation corpus.
tags: [documentation, corpus, review, audit, sampling, assurance, governance, remediation, research]
---

# Documentation review at corpus scale

Researched 2026-09-08. This is research, not an adopted corpus standard, audit plan,
assurance statement, or finding against an individual corpus node.

## Research question

How should Buzz design and execute a repeatable, evidence-backed review programme for a
205-node living technical-documentation corpus so that it finds important defects,
measures coverage honestly, prioritizes risk, maintains reviewer consistency, and turns
findings into owned remediation without implying that every node received equal or
complete assurance?

The investigation considered fourteen subquestions:

1. What is the review population and what should count as the unit of review?
2. Which decisions, criteria, baseline, scope, and exclusions must be fixed before review
   begins?
3. When should Buzz review every node, and when is sampling defensible?
4. How should risk determine priority, reviewer expertise, depth, and cadence?
5. How should targeted selection and random selection be combined?
6. Which review methods provide distinct evidence, and what does each fail to prove?
7. How should population coverage, method coverage, review depth, and assurance be kept
   separate?
8. How should reviewers be selected, calibrated, and supported without assuming either
   independence or subject-matter expertise is sufficient alone?
9. How should observations, defects, uncertainties, accepted risks, and improvement ideas
   be classified and prioritized?
10. What evidence makes a review reproducible and its conclusions appropriately bounded?
11. How should findings acquire owners, decisions, retests, and defensible closure?
12. How should change-time review, event-triggered review, and periodic corpus audit fit
    together?
13. Which measures support governance without rewarding shallow review or producing a
    misleading corpus-quality score?
14. What does the current Buzz corpus already support, and what would a review programme
    still need?

## Bottom line

A corpus review is not 205 repetitions of one checklist. It is an assurance programme
that makes a bounded decision about a defined population at a recorded revision. The
programme has to decide what matters most, select appropriate evidence-producing methods,
state what was and was not examined, and keep findings alive until a responsible person
has resolved and rechecked them.

The strongest practical model for Buzz is:

> **Decision and criteria → frozen population and baseline → risk strata → universal
> deterministic checks → structured and random selection → declared methods, depth, and
> coverage → evidence-backed findings → ownership, remediation, and retest → trend and
> control improvement.**

Ten conclusions should govern the later checklist:

1. **Define the assurance question before examining nodes.** “Review the corpus” is not
   an objective. A review might seek publication readiness, factual reliability,
   operational safety, conformance to the corpus contract, discovery of systemic defects,
   or a remediation baseline. Those objectives require different evidence and support
   different conclusions.
2. **Freeze the population and revision.** The review record needs the corpus root,
   included and excluded objects, inventory, generated projections, and repository
   revision. Otherwise node changes during the exercise make the denominator and the
   evidence irreproducible.
3. **Do not collapse coverage, depth, and assurance.** A validator can inspect all 205
   nodes for schema defects while deeply establishing the truth and usability of none.
   A technically deep review of 20 selected nodes can provide strong evidence about those
   nodes while covering only part of the population. Both results are useful when named
   honestly.
4. **Use census checks where they are cheap and deterministic; use risk-based depth where
   judgment is expensive.** Every node can receive structural, link, vocabulary, and
   inventory checks. High-consequence instructions, normative controls, security claims,
   operational recovery paths, and central architecture nodes warrant deeper human and
   task evidence than low-impact descriptive leaves.
5. **Risk targeting needs a discovery sample.** Reviewing only what reviewers already
   believe is risky reinforces the existing model and cannot reveal omitted strata. Pair
   a deliberately structured sample with a recorded random sample from the remaining
   population, and expand the review if the random set reveals new content or defect
   classes.
6. **Use multiple assessment methods.** Source examination, cross-node comparison,
   interview, command or workflow exercise, reader task evaluation, and deterministic
   scanning answer different questions. No one method proves correctness, completeness,
   usability, and continued fitness together.
7. **Reviewers need both competence and calibration.** A neutral reviewer without domain
   knowledge can miss technical falsehoods; a domain owner can normalize familiar gaps.
   Define operational criteria, pilot them on shared examples, resolve disagreements,
   overlap a portion of later work, and bring specialist or independent review where
   consequence requires it.
8. **A finding is not resolved when text changes.** It needs a recorded disposition,
   responsible owner, due or accepted state, correction evidence, and a recheck against
   the original criterion and affected dependants. Recurring findings should change a
   template, standard, authoring practice, or automated control, not merely the latest
   node.
9. **Use both continuous and periodic review.** Pull-request review catches introduced
   defects while context is fresh. Dependency-triggered and event-triggered reviews react
   to code, decision, incident, release, or threat changes. Periodic corpus review finds
   accumulated drift, cross-node contradictions, orphaned knowledge, and blind spots that
   no individual diff exposes.
10. **Report evidence and limits, not a ceremonial pass.** The result should say which
    nodes and claims were assessed, by which methods and criteria, to what depth, what was
    sampled, what remains unverified, and which conclusions are supported. A single
    percentage or red/amber/green label cannot carry that information.

Buzz has valuable foundations: a canonical inventory of nodes, stable identifiers,
structured evidence ledgers, status and audience metadata, typed relationships, an
all-node validator, review-specific content duties, and a pull-request diff as an audit
surface. It does not have a corpus-review plan or result model. The node schema has no
review owner, risk, method, depth, finding, waiver, retest, or next-review field, and the
current validator deliberately does not judge body meaning. These omissions do not imply
that all such data belongs in node front matter. A separate review register may preserve
the canonical corpus contract more cleanly.

## Scope and method

This report concerns review of the canonical Markdown corpus as a population and of the
reader-facing products and workflows derived from it. It covers review planning,
inventory, baselining, risk, selection, methods, reviewer competence, calibration,
findings, remediation, evidence, cadence, and reporting.

It does not:

- perform the actual content review of the 205 current nodes;
- approve a sample size, review cadence, severity model, owner, or tool;
- make a statistical estimate of the present corpus defect rate;
- reclassify any current node, evidence entry, relationship, or status;
- change the schema, validator, branch protection, CODEOWNERS, or pull-request process;
- claim conformity with ISO, NIST, W3C, GAO, or another audit framework;
- treat documentation review as a legal, financial, security, or accessibility audit;
- infer present GitHub settings from a locally recorded historical observation; or
- introduce LLM-specific controls, which remain set aside for this research sequence.

Local inspection covered all 205 Markdown nodes under `launchpad/docs/corpus/`, excluding
the `schema/` subtree, at repository revision
`eb1cedb19d02e61426bc5e75b7a43cc485c8a133`. It examined the node schema, validator,
corpus instructions, review, status, provenance and documentation standards, CODEOWNERS,
inventory tooling, and the 2026-08-18 full-ecosystem audit as a local precedent. Counts
were produced by read-only parsing of YAML front matter. They describe the current
checkout, not a timeless corpus property or a content-quality result.

External sources were selected in this order:

1. ISO/IEC/IEEE 26513:2017, the current published international standard specifically
   about testing and reviewing information for users, using only its public ISO and IEEE
   descriptions;
2. ISO 19011:2026, the current international guidance for audit programmes, principles,
   competence, evidence and risk, using only its public preview;
3. NIST SP 800-53A Revision 5 for its explicit separation of assessment method, depth,
   coverage, assurance and evidence reuse;
4. W3C WCAG-EM 2.0 for a current, explicit method that combines scope definition,
   exploration, structured selection, random discovery, complete-process evaluation, and
   reporting;
5. the NIST/SEMATECH statistical handbook for the limits of sampling, stratification,
   randomization and precision;
6. GAO's 2024 Government Auditing Standards for evidence, findings, recommendations,
   quality management and reporting boundaries;
7. current GOV.UK content-management and periodic-review guidance for inventory,
   ownership, review records and content lifecycle; and
8. NASA's software peer-review guidance for domain competence, independence, agreed
   criteria and consistency among reviewers.

The external frameworks govern different subjects. NIST SP 800-53A assesses security and
privacy controls; WCAG-EM evaluates accessibility conformance; ISO 19011 concerns
management-system audits; GAO governs government audits; and NASA's guidance concerns
software-engineering reviews. This report borrows their assessment architecture, not
their domain verdicts. Public access did not expose the complete ISO standards, so no
unseen clause is attributed to them.

## What “review the corpus” can mean

At least six activities are commonly called review. They should not share an unqualified
result.

| Activity | Primary object | Typical question | Honest result |
|---|---|---|---|
| Change review | One proposed diff and affected context | Is this change acceptable to merge? | Approved, changes requested, or unresolved for the named diff |
| Node assessment | One node and its claims | Is this node fit for its declared purpose at this revision? | Criteria and evidence by node |
| Cross-node review | A connected set, topic, journey, or invariant | Do these nodes form a coherent and non-contradictory answer? | Findings for the set and relationships |
| Corpus audit | A defined population or sample | What defect patterns, gaps, and risks exist across the corpus? | Bounded findings and coverage statement |
| Task evaluation | Documentation used in context | Can intended readers find, understand, perform, and recover? | Observed task outcomes under named conditions |
| Programme monitoring | Review system over time | Is review finding and reducing important defects? | Trends, escapes, recurrence, closure and control changes |

Pull-request approval is therefore evidence about a proposed change, not proof that the
unchanged remainder is correct. A corpus audit is a snapshot, not a guarantee that the
next change preserves its result. A reader task can expose usability and procedural
failure, but it does not prove every factual claim. A later Buzz programme should name
the activity before using the word “reviewed.”

[ISO/IEC/IEEE 26513:2017](https://www.iso.org/standard/67417.html) is directly relevant
because its public ISO and
[IEEE description](https://standards.ieee.org/ieee/26513/6082/) support the need for
consistent, complete, accurate and usable information and place testing and review
throughout the information-management lifecycle, not only at a final review stage. It
applies to initial and subsequent releases and to organizations with or without a
dedicated documentation department. That lifecycle framing argues against treating the
planned corpus review as a one-time cleanup.

## The unit of review

Buzz's stable node is a useful unit of ownership and reporting, but it is not the only
unit that matters. A review programme should inventory at least five layers:

| Layer | Examples | Why node-only review misses it |
|---|---|---|
| Claim | One evidence-ledger statement and corresponding prose | A node can mix strong and weak claims |
| Node | One canonical Markdown file with stable `id` | This is the lifecycle and relationship unit |
| Connected set | Architecture parent and children, terminology family, invariant and implementations | Contradictions and gaps exist between individually plausible nodes |
| Reader journey | Install, configure, diagnose, recover, release | Task completion often crosses several nodes and external artifacts |
| Delivery surface | Source, diff, generated site, terminal view, exported document | Source quality does not prove rendered or navigational quality |

The audit population should therefore not be recorded as “205 files” alone. It should
state whether the population includes 205 nodes, 3,936 evidence entries, typed edges,
reader journeys, generated views, external citations, executable examples, and source
artifacts. Each extra object changes both the denominator and the needed reviewer skills.

## Stage 1: define the decision, criteria, and stopping rules

Before selection begins, record:

- the commissioner or decision owner;
- the decision the review must support;
- the applicable standards and local corpus requirements;
- the population and delivery surfaces;
- the baseline revision and inventory date;
- explicit exclusions and their consequence;
- the desired assurance and acceptable residual uncertainty;
- available reviewers, specialist skills, time, and tools;
- finding categories and severity definitions;
- escalation and exception routes;
- what prevents publication, activation, or closure;
- the treatment of unresolved, inaccessible, or untestable objects; and
- the form and audience of the final report.

This is the review's contract. It prevents criteria from changing silently after results
are known and stops an open-ended exercise from ending only when time runs out.
[NASA's peer-review guidance](https://swehb.nasa.gov/pages/viewpage.action?navigatingVersions=true&pageId=200212800)
similarly expects the product, reviewers, agenda, success criteria, instructions, and
consistency rules to be agreed before review. The
[GOV.UK periodic-review checklist](https://www.gov.uk/government/publications/handbook-for-standard-managers/checklist-undertaking-a-major-or-periodic-review)
begins with the owner, previous feedback, timescale, approach, and implications.

Stopping rules should distinguish at least:

- **review execution complete:** every planned method and selected object has a result or
  a recorded inability to assess;
- **report complete:** findings, limitations, sample design and evidence are documented;
- **release or activation acceptable:** no open finding in a predefined blocking class,
  or a responsible authority has explicitly accepted it;
- **remediation complete:** every accepted fix has been rechecked and every deferral or
  risk acceptance has an owner and rationale; and
- **programme cycle closed:** lessons and recurring causes have been routed into future
  standards, templates, tools, training or selection.

These states should not be compressed into one “done.”

## Stage 2: freeze and characterize the population

A reproducible baseline needs more than a commit SHA. Record:

- canonical corpus root and revision;
- exact inventory of node ids and paths;
- node status, type, origin and audiences;
- claim and relationship counts;
- included generated representations and renderer versions;
- excluded directories, fixtures, archives and external documents;
- inaccessible sources or environments;
- changes accepted during the review and how they are rebased into results; and
- the deterministic command and tool version that created the inventory.

The current Buzz baseline has:

| Characteristic | Current observation |
|---|---:|
| Canonical Markdown nodes, excluding `schema/` | 205 |
| `active` nodes | 47 |
| `draft` nodes | 158 |
| Evidence entries | 3,936 |
| `FACT` / `INFERENCE` / `TEAM_KNOWLEDGE` entries | 3,449 / 212 / 275 |
| Typed relationship edges | 192 |
| Nodes with / without relationship edges | 89 / 116 |
| Evidence entries per node, minimum / median / maximum | 9 / 19 / 48 |

Status is not a review result. The status standard defines `active` as a node believed
current and safe to depend on, but it also says the validator does not test that belief.
Conversely, `draft` does not mean every claim is false. It means the population includes
a large amount of content whose lifecycle state already warns against a settled-guidance
interpretation. A review should report results by status rather than averaging the two
groups together.

Inventory also has to detect coverage error: nodes that should exist but do not. The
current 205 files are the observable population, not necessarily the required knowledge
population. The earlier [completeness and coverage research](04-measuring-corpus-completeness-and-coverage.md)
therefore remains a prerequisite for deciding whether the inventory itself is adequate.

## Stage 3: stratify by consequence and uncertainty

Risk-based review should alter priority, depth, expertise, independence and cadence. It
should not mean that known high-risk objects are the only ones ever examined.

A candidate risk profile can combine:

| Factor | Higher-risk signal |
|---|---|
| Consequence of error | Could cause security exposure, data loss, failed recovery, outage, unsafe operation, or irreversible action |
| Normative authority | Defines a MUST, governance gate, accepted decision, invariant, permission or prohibition |
| Actionability | Invites commands, configuration, deployment, migration, incident response, release, deletion or credential handling |
| Exposure | Public, broadly used, copied into automation, or relied on across teams |
| Dependency centrality | Many nodes, workflows or decisions depend on it |
| Change velocity | Underlying product, interface, policy or threat model changes often |
| Evidence fragility | Sources are mutable, inaccessible, indirect, weakly pinned, or dependent on live state |
| Reader vulnerability | Used under time pressure, during failure, by new operators, or through accessibility constraints |
| Defect history | Prior incidents, repeated findings, reopened corrections or high support burden |
| Ownership | No clear accountable maintainer or unavailable specialist |
| Novelty | New content form, technology, subsystem, authoring route or source class |
| Staleness signal | Old review evidence plus meaningful environmental or dependency change |

The score, if one is used, should route work rather than claim quality. A high score says
“apply more assurance,” not “this node is bad.” A low score says “lower known
consequence,” not “safe to ignore.” Risk factors and thresholds should be versioned and
reviewed after escapes reveal what the model failed to predict.

Some objects warrant a census regardless of score:

- security and disclosure boundaries;
- destructive or difficult-to-reverse instructions;
- incident response, backup, restore and rollback paths;
- mandatory governance and compliance statements;
- high-centrality architecture and terminology nodes;
- nodes being promoted to a trusted publication or lifecycle state;
- nodes implicated by an incident, changed decision, interface change or vulnerability;
- every node affected by a known changed dependency; and
- every open finding from a previous cycle.

## Stage 4: select what receives deep review

### Census, structured selection, and random selection

There are three legitimate selection modes:

| Mode | Best use | Strength | Main limit |
|---|---|---|---|
| Census | Cheap deterministic properties; small or uniformly critical populations | Known population coverage for the named check | Human depth may become rushed and superficial |
| Structured or purposive selection | High-risk nodes, each genre/type/audience, central relationships, known change and known defect patterns | Assures coverage of known important variation | Cannot reveal how much the risk model omitted and does not support probability inference |
| Probability selection | Discovery and population estimates when a valid frame and design exist | Reduces selection bias and can support quantified inference | May miss rare critical cases unless stratified or supplemented |

W3C's current [WCAG-EM 2.0](https://www.w3.org/TR/wcag-em-2/) uses an instructive hybrid.
It explores the product, chooses a structured sample covering known variety, adds a
random set from the remaining product, includes complete processes, and then compares
random with structured findings. If the random set exposes new content or finding types,
the structured sample was not adequate and selection is repeated. The exact WCAG-EM
sample formula belongs to accessibility evaluation and should not be copied blindly into
Buzz content review; the architecture of targeted coverage plus a discovery check is the
transferable lesson.

For Buzz, a defensible sample record should state:

- the complete sampling frame and exclusions;
- selected strata and why they matter;
- census strata;
- purposively selected nodes and selection reason;
- the residual population eligible for random selection;
- randomization method, seed and replacement rule;
- sample size and the precision or discovery rationale behind it;
- additions made after new defect or content classes appeared;
- connected nodes or complete journeys pulled in with an initially selected node; and
- whether any result is intended to be projected to a population.

The NIST/SEMATECH handbook warns that
[facts about a sample are not automatically facts about the population](https://www.itl.nist.gov/div898/handbook/ppc/section1/ppc134.htm).
Adequacy depends on representativeness, size, population variability and desired
precision. Its sampling guidance also explains that
[stratification and randomization reduce systematic sampling error](https://www.itl.nist.gov/div898/handbook/ppc/section3/ppc332.htm),
and that more consequential decisions justify lower risk and therefore
[larger samples](https://www.itl.nist.gov/div898/handbook/ppc/section3/ppc333.htm). If Buzz
selects nodes purposively, it can report what it found in those nodes but should not
publish an estimated corpus-wide defect rate.

### Select complete knowledge paths

Atomic nodes improve maintenance but can hide journey failure. When a selected node is
part of an installation, decision, incident, recovery, release or troubleshooting path,
review the complete path needed to reach the promised outcome. Include relevant branches,
prerequisites, definitions, cross-references, source artifacts, and recovery. This adapts
WCAG-EM's complete-process rule to documentation without implying WCAG conformance.

### Expand on discovery

A fixed sample can become indefensible as review teaches the team about the corpus.
Expansion triggers should be decided in advance, for example:

- a random node exposes a content form absent from the structured sample;
- the same severe defect appears in two nodes from different strata;
- a selected claim depends on an unreviewed central node;
- a source-of-truth check reveals a changed interface affecting a family;
- reviewer disagreement exposes an ambiguous criterion; or
- an inventory gap means the sampling frame was incomplete.

Expansion is evidence that the method is learning, not that the original reviewers
failed. Record the reason so the final denominator remains intelligible.

## Stage 5: declare method, depth, and coverage

[NIST SP 800-53A Revision 5](https://doi.org/10.6028/NIST.SP.800-53Ar5) offers a useful
assessment grammar: **examine**, **interview**, and **test**, each with separate depth and
coverage attributes. It explicitly says that not every method must be applied to every
object and that rigor and scope should increase with assurance needs and adverse impact.
Buzz should adapt the grammar, not the security control conclusions.

| Method | Documentation adaptation | Can establish | Cannot establish alone |
|---|---|---|---|
| Deterministic scan | Parse schema, ids, citations, links, vocabulary, headings, graph, examples or source mappings | Defined machine-detectable properties across a known population | Truth, relevance, adequate explanation, task success |
| Examine | Read node, sources, implementation, decisions, history and connected nodes | Claim support, scope, consistency, provenance and visible defects | Real-world execution or reader performance |
| Compare | Trace the same fact, term, rule or journey across nodes and authoritative artifacts | Contradictions, duplication, gaps and relationship defects | Which source reflects actual behavior without further evidence |
| Interview | Ask owner, subject-matter expert, support or intended reader about practice and intent | Context, tacit knowledge, ownership and candidate gaps | Present truth; recollection is evidence to verify, not a substitute for it |
| Test | Execute command, workflow, recovery, link path, build, rendering or retrieval under stated conditions | Actual behavior for the tested case and environment | Every environment, branch, reader or future version |
| Reader evaluation | Observe an intended reader finding, interpreting, performing and recovering | Comprehension and use under named participant/task conditions | Corpus-wide correctness or universal usability |
| Independent challenge | Have a suitably competent non-author examine assumptions and evidence | Reduces familiarity and self-review blind spots | Domain competence automatically |

Each method needs both **depth** and **coverage**:

- **Depth** is the rigor and detail within each assessment. For example, opening one
  citation is shallower than reconstructing every material claim against source and
  implementation; executing a happy path is shallower than exercising errors, rollback
  and recovery.
- **Coverage** is the breadth of objects, conditions and variants. For example, a full
  structural scan covers every node but one property; a deep operational test might cover
  one runbook, one platform and three branches.

A practical three-level vocabulary could be:

| Level | Depth | Coverage |
|---|---|---|
| Basic | Obvious errors and minimum criterion evidence | One or a small representative set of objects/conditions |
| Focused | Source-aware analysis of likely failure modes and important branches | All high-risk objects in the selected scope plus representative variants |
| Comprehensive | Detailed source, interaction, failure, recovery and cross-node analysis suitable for the desired high assurance | Broad object, environment, reader and branch coverage defined by the review plan |

These labels require operational definitions per method. Calling a review
“comprehensive” without listing what was examined and tested adds confidence language but
no evidence.

## Stage 6: build a controlled assessment package

The checklist used in review should be assembled from the relevant topic research and
local standards rather than presented as one flat universal list. For every criterion,
record:

- stable criterion id and version;
- purpose and quality risk addressed;
- applicability rule;
- pass, fail, not applicable and unable-to-assess definitions;
- required evidence and acceptable method/depth;
- examples and counterexamples;
- severity guidance;
- specialist competence needed;
- automation available and its tested boundary;
- related local standard or decision; and
- escalation route for ambiguity or conflict.

Then generate a review package for each object based on its genre, audiences, risk,
status, content features and delivery surface. A runbook should receive operational,
command-safety, recovery and stress-use criteria. A terminology node should receive
definition, distinction and cross-corpus consistency criteria. An architecture node
should receive scope, viewpoint, relationship, rationale and change-impact criteria.
Universal criteria still apply, but identical review effort does not.

Version the criteria. A result under checklist version 1 does not silently become a
result under version 2. If a new rule is material, decide whether prior nodes need a
targeted retrospective review.

## Stage 7: make reviewer judgment consistent enough to trust

Consistency is not produced by a long checklist alone. Reviewers can interpret “clear,”
“supported,” “complete,” “safe,” and “material” differently.

A calibration cycle should:

1. choose a small set spanning obvious passes, obvious failures, boundary cases and
   several corpus types;
2. have reviewers apply the same versioned criteria independently;
3. compare applicability, result, severity and evidence, not only final pass/fail;
4. resolve disagreements by refining operational definitions and examples;
5. preserve genuinely judgment-dependent disagreement rather than forcing false
   consensus;
6. repeat the pilot after material criterion changes;
7. double-review a disclosed portion of production work; and
8. monitor disagreement and reversals by criterion to find unclear rules or training
   needs.

[NASA's peer-review guidance](https://swehb.nasa.gov/pages/viewpage.action?navigatingVersions=true&pageId=200212800)
expects independent reviewers selected for relevant technical background and rules that
promote consistency. [WCAG-EM](https://www.w3.org/TR/wcag-em-2/#using-this-methodology)
similarly allows individual or combined expertise and describes the accessibility
knowledge the evaluation requires. The general lesson is two-dimensional: independence
can improve challenge, and competence makes the challenge meaningful.

Candidate roles include:

- **review lead:** owns scope, baseline, sampling, assignments, issue consistency and
  report limits;
- **domain reviewer:** verifies system, protocol, operational or policy truth;
- **documentation reviewer:** assesses genre, structure, language, navigation and
  cross-node coherence;
- **specialist reviewer:** handles security, accessibility, release, legal or another
  consequential specialty;
- **reader or task participant:** supplies observed use evidence rather than approval;
- **finding owner:** decides and implements remediation or explicitly seeks risk
  acceptance; and
- **independent quality reviewer:** checks a sample of review work and evidence, not just
  the underlying nodes.

One person may hold several roles in a small cohort, but the record should say so.

## Stage 8: record observations and findings before editing

Directly correcting every defect while it is found destroys the review trail and makes
counts, severity decisions and systemic analysis unreliable. Keep the observation and
disposition separate from the eventual patch.
[GOV.UK's periodic-review guidance](https://www.gov.uk/government/publications/handbook-for-standard-managers/checklist-undertaking-a-major-or-periodic-review)
follows this pattern by keeping comments in a master review sheet, deciding whether to
accept, modify, reject, note or defer, and retaining the sheet as an audit trail.

A candidate finding record should include:

- finding id and review id;
- criterion id and version;
- node id, path, claim, section, relationship, journey or delivery surface;
- baseline revision and observed evidence;
- method, depth, coverage and environment;
- concise condition: what was observed;
- criterion: what the object was evaluated against;
- consequence: why the difference matters to a reader, system or governance decision;
- classification and provisional severity;
- confidence and unresolved questions;
- related or duplicate findings;
- responsible finding owner;
- disposition, rationale and authority;
- remediation reference and due state;
- retest method and evidence; and
- closure identity and date.

Separate these result classes:

| Result | Meaning |
|---|---|
| Conforms / no finding | The tested criterion passed under the recorded method and scope |
| Defect | Evidence shows the object fails an applicable criterion |
| Gap | Required content, coverage, owner, source or path is absent |
| Contradiction | Two relevant claims or authorities cannot both hold as written |
| Observation | Relevant improvement or pattern that does not establish criterion failure |
| Unable to assess | Required source, environment, expertise or access was unavailable |
| Not applicable | The criterion does not govern this object, with reason |
| Accepted risk or exception | An authorized decision accepts a known departure for a stated period or condition |

An “unable to assess” is not a pass. “Not applicable” needs a reason. An accepted risk is
not defect removal. A contradiction may need Buzz's existing `flagged` and human-decision
route, but only when it meets that local standard's specific definition.

## Stage 9: prioritize by consequence, reach, and likelihood

Severity should reflect harm, not how visually large the edit is. A one-word reversal in
a security boundary can matter more than a page of awkward prose.

A candidate model for synthesis is:

| Severity | Candidate meaning |
|---|---|
| Critical | Likely to cause severe security, privacy, data, safety or operational harm, or directs a high-consequence action contrary to an authoritative requirement |
| High | Blocks or materially corrupts an important task or decision, creates broad false understanding, or undermines a central corpus control |
| Medium | Causes material ambiguity, rework, avoidable error or a workaround for a meaningful audience |
| Low | Localized clarity, consistency, presentation or maintenance defect with limited consequence |
| Observation | Improvement opportunity or unverified concern without a demonstrated criterion failure |

Severity factors should include:

- consequence if followed;
- likelihood the reader reaches and trusts it;
- breadth of affected readers, nodes and workflows;
- detectability before harm;
- reversibility and recovery cost;
- authority of the claim;
- availability and visibility of a safe alternative; and
- evidence confidence.

Urgency can differ from severity. A medium defect in tomorrow's release path may need
action sooner than a high-severity defect in an unreachable draft. Keep severity,
priority and due date as separate decisions.

## Stage 10: own, remediate, recheck, and close

A finding lifecycle should be explicit:

> **Discovered → validated and deduplicated → classified and prioritized → assigned →
> fixed, accepted, rejected, or deferred with rationale → retested → closed or reopened.**

Closure should require evidence that the original criterion now passes at a named
revision and that material dependants were reconsidered. “PR merged,” “author says
fixed,” and “text changed” are events, not retest results.

[GAO's 2024 Government Auditing Standards](https://www.gao.gov/products/gao-24-106786)
require sufficient appropriate evidence for findings and conclusions, corrective
recommendations when findings are significant in context, evaluation of action on
significant prior findings, and appropriately limited conclusions when results cannot be
projected. Buzz need not imitate government audit machinery, but the principle transfers
directly: a review that generates findings without tracked correction and verification
is an observation exercise, not a closed quality loop.

Recurring findings should receive cause-oriented treatment:

1. group recurrence by criterion, template, source, authoring route, subsystem and
   failure mechanism;
2. determine whether the local standard, example, template, tooling, ownership or change
   signal failed;
3. change the earliest effective control;
4. apply the correction to the affected population, not only the sampled instance; and
5. measure whether recurrence falls in later cycles.

This is how audit becomes quality improvement rather than repeated defect harvesting.

## Stage 11: combine change-time, event-triggered, and periodic review

| Review route | Trigger | Strength | Blind spot |
|---|---|---|---|
| Pull-request review | Proposed corpus change | Context is fresh; changed lines are visible | Unchanged contradictions, stale dependencies and missing content remain invisible |
| Dependency-triggered review | Code, interface, decision, policy, standard or source changes | Targets likely drift quickly | Requires a trustworthy impact map |
| Event-triggered review | Incident, failed task, support cluster, vulnerability, audit escape, release or ownership change | Learns from real consequence | Reactive and potentially late |
| Scheduled risk review | Time or risk cadence | Rechecks high-consequence nodes and aging evidence | Calendar age alone does not prove staleness |
| Periodic corpus audit | Planned population-level cycle | Finds systemic, graph and interaction defects | Snapshot starts aging immediately |
| Continuous deterministic monitoring | Every change or scheduled scan | Cheap and repeatable across the population | Limited to encoded rules and tool support |

The earlier [freshness research](07-freshness-staleness-and-change-impact.md) argues that
change signals are stronger than age alone. Review evidence should therefore be reusable
only after confirming that the node, its sources, the environment, the criteria and the
required independence have not changed materially. NIST SP 800-53A makes the analogous
point for prior assessment results: credibility depends on change, elapsed time,
applicability and independence, and reused evidence should retain its original date and
type.

## Automation and human judgment

### Strong candidates for deterministic population-wide checks

- schema, required fields and controlled vocabularies;
- duplicate, malformed and changed stable identifiers;
- unresolved relationship targets and known inverse rules;
- citation shape, path existence, pinning and line-range plausibility;
- broken internal and external links, with network limitations reported;
- missing required sections, labels or template elements where mechanically defined;
- corpus inventory, unrecognized locations, generated-content boundaries and orphans;
- heading, link-label, table, diagram, fence and image discovery;
- duplicate or near-duplicate text for human routing;
- vocabulary and identifier inconsistencies;
- source-to-doc change-impact candidates;
- executable sample parsing, compilation or tests where a harness exists;
- review sampling from a recorded frame and seed;
- open finding, overdue owner, waiver and retest state; and
- generation of coverage denominators and review packages.

### Human judgment remains necessary for

- whether a substantive claim is true and sufficiently evidenced;
- whether the scope includes what readers need and excludes what it promises not to do;
- whether an inference follows without making an unauthorized decision;
- whether two claims genuinely contradict or describe different contexts;
- whether a relationship type and direction represent reality;
- whether language, structure, examples and diagrams communicate the intended meaning;
- whether a command is safe and appropriate despite executing successfully;
- whether a reader can use the documentation in a realistic task;
- whether a defect's consequence and severity are correctly characterized;
- whether an exception or residual risk is acceptable;
- whether remediation addresses the cause and affected dependants; and
- what the accumulated evidence permits the final report to claim.

A tool error, unsupported content type, network failure, permission failure or parser
crash should become “unable to assess” or an explicit tooling finding. Silently converting
it to pass corrupts the review evidence.

## Review records and reproducibility

The minimum review-level record should contain:

| Field | Purpose |
|---|---|
| Review id and objective | Distinguishes one assurance decision from another |
| Commissioner and decision owner | Names who will use and accept the result |
| Baseline and inventory | Fixes the population and denominator |
| Criteria version | Makes results interpretable after standards change |
| Risk model and strata | Explains prioritization and depth |
| Selection frame, reasons, seed and sample | Makes coverage and bias inspectable |
| Reviewers, roles, competence and conflicts | Bounds trust and independence |
| Methods, tools, versions, depth and coverage | States what was actually done |
| Per-object results and evidence | Supports replication and correction |
| Findings, dispositions, owners and due states | Connects observation to action |
| Retest and closure evidence | Proves whether correction worked |
| Exclusions, failures and limitations | Prevents overclaiming |
| Final conclusions and permitted uses | Ties evidence back to the decision |

Store raw observations separately from interpretive findings where practical. Preserve
commands, tool versions, outputs, selected identifiers and environment details for tests.
For reader research, preserve task design and aggregate outcomes while respecting
privacy. For sensitive security findings, the public corpus is not an appropriate finding
store; topic 15 will address disclosure quality and boundaries.

## Metrics without a misleading quality score

A review dashboard should retain denominators and strata. Useful measures include:

- inventory coverage by node status, type, audience, risk stratum and delivery surface;
- method coverage: nodes receiving scan, source examination, cross-node comparison,
  workflow test, reader task or specialist assessment;
- depth coverage by method and risk tier;
- proportion of high-risk nodes with current deep evidence;
- findings by criterion, severity, type, status and source class;
- unable-to-assess and not-applicable rates with reasons;
- time from discovery to validation, owner, remediation, retest and closure;
- reopen rate and escaped defects found after a review claimed readiness;
- repeat findings and recurrence by root cause;
- accepted risks and exceptions by age, owner and expiry;
- sampling-frame exclusions and random discoveries that expanded the structured set;
- estimated prevalence with uncertainty only when a probability design supports it; and
- control improvements caused by recurring findings.

Measures need interpretation:

- More findings can mean worse content, deeper review, better reviewers, broader scope or
  a newly effective detector.
- Fewer findings can mean improvement, shallow review, narrow sampling, premature closure
  or selection of familiar nodes.
- A high “nodes reviewed” percentage can hide one-minute checks and missing claim-level
  evidence.
- A low mean time to close can reward trivial fixes and inappropriate dismissal.
- Zero severe findings is not reassuring when high-risk nodes were excluded or unable to
  assess.

Do not average severity into one corpus score. Do not compare cycles without normalizing
scope, criteria, depth and selection. Publish trends with the review design that produced
them.

## Findings in the current Buzz corpus

### The canonical node population is enumerable

All 205 in-scope Markdown files parsed as front-matter-bearing nodes in this checkout.
Stable ids, paths, types, statuses, origins, audiences, evidence ledgers and optional
relationships give a review programme a strong sampling frame. The corpus's validator
already performs population-wide discovery and rejects several structural classes.

This does not establish inventory completeness. The project-intelligence inventory tool
catalogues Buzz product surfaces, but it deliberately excludes `launchpad/`; the corpus
population and the product-surface inventory answer different questions. A future review
needs an explicit mapping between required knowledge and existing nodes.

### Structural coverage is broad; semantic coverage is absent

The validator checks schema conformance, duplicate ids, relationship-target resolution,
citation form and resolution, canonical placement, and ownership/generated-content
boundaries. Local standards repeatedly and explicitly state that it does not determine
whether citations support claims, relationships are true, status is semantically correct,
or body content is sound. A green run is therefore a census result for a defined set of
structural properties, not a corpus content-review result.

### Review duties exist for changes, not for a corpus audit programme

The review-requirements standard demands that a reviewer open FACT sources, test
INFERENCE reasoning and confidence, validate TEAM_KNOWLEDGE attribution, pair substantive
body claims with ledger entries, check relationship direction, apply decision-citation
rules, respect `flagged` escalation, and verify atomicity. These are substantial duties.

The standard also says this is the ordinary pull-request review plus content-verification
duties, not a separate corpus-specific review role. The current CODEOWNERS file contains
one repository-wide wildcard owner and no corpus path entry. Neither observation proves
who is presently competent, available, or authorized to lead a corpus audit.

### A node can say `active` without machine-readable review evidence

The current schema permits only `id`, `type`, `status`, `origin`, `audiences`, `evidence`
and optional `relationships`. It has no review result, reviewer, reviewed revision,
criteria version, method, depth, risk, finding, exception or next-review field. The
status standard explicitly says only enum membership is mechanically enforced.

This is not automatically a schema defect. Mixing transient audit workflow into every
canonical knowledge node could create churn, couple node format to one process and make
evidence reuse harder. A separate review register keyed by stable node id and commit may
be the better design. That choice belongs to synthesis and human decision.

### Draft content dominates the current population

158 of 205 nodes are `draft`; 47 are `active`. Review planning should decide whether the
first objective is to assess the reliability of active content, establish what drafts
need before promotion, or review both for different decisions. Reporting one combined
pass rate would hide the lifecycle distinction.

### Evidence-ledger scale changes the feasibility of full manual verification

The 205 nodes contain 3,936 entries, with a median of 19 and a maximum of 48 per node.
The current node-review standard requires opening every FACT citation for a changed node
and pairing substantive body claims with ledger entries. Re-performing that depth over
the entire current population is a materially larger task than reading 205 prose files.
The audit plan should estimate effort at the claim and source level, not only the file
level.

### The graph can support impact review but is incomplete as a dependency model

There are 192 recorded relationship edges across 89 nodes, while 116 nodes have none.
An edgeless node may be legitimately standalone, may express relationships only in prose,
or may be missing useful connections. The current validator checks that targets resolve,
not that edge types are true or that necessary edges exist. Graph centrality can help
route review, but absent edges cannot be interpreted as low dependency without further
inspection.

### The local ecosystem audit is a useful precedent with limits

The 2026-08-18 full-ecosystem audit grouped findings by severity, recorded positive
non-findings, reported coverage by dimension, and explicitly listed areas at lower depth
and unverified suspicions. Those are strong reporting patterns to reuse. It was a
whole-repository technical audit rather than a controlled corpus review; its seven-shard
coverage language, finding criteria, selection method, reviewer calibration and closure
records do not constitute the missing corpus-review programme.

## Candidate corpus-review checklist

These are research outputs for later synthesis, not approved requirements.

### A. Commission and scope

- [ ] Is the decision this review must support stated rather than merely “review the
      corpus”?
- [ ] Are commissioner, decision owner, review lead and report audience named?
- [ ] Are applicable local standards and checklist version frozen?
- [ ] Are the canonical population, delivery surfaces, journeys and external artifacts in
      scope defined?
- [ ] Are exclusions, access limitations and expected consequences disclosed?
- [ ] Is the baseline revision fixed, with rules for changes during review?
- [ ] Are desired assurance, residual uncertainty and acceptable evidence stated?
- [ ] Are execution, reporting, release, remediation and cycle-closure rules distinct?

### B. Inventory and risk

- [ ] Does the inventory enumerate node ids and paths deterministically?
- [ ] Does it record status, type, origin, audiences, claims, edges and content features
      needed for stratification?
- [ ] Are required-but-missing knowledge and excluded content considered separately from
      existing-node quality?
- [ ] Is risk based on consequence, authority, actionability, exposure, dependency,
      volatility, evidence, reader context, history, ownership and novelty?
- [ ] Does risk route depth, competence, independence and cadence without becoming a
      quality score?
- [ ] Are all security, destructive, recovery, normative, central and incident-affected
      objects included at appropriate depth?

### C. Selection

- [ ] Are cheap deterministic criteria applied to the full in-scope population?
- [ ] Does the structured sample cover risk tiers, types, statuses, audiences, origins,
      content forms, authorship routes and delivery surfaces?
- [ ] Is a random discovery sample selected from a complete recorded residual frame?
- [ ] Are seed, method, sample size, replacement and exclusions reproducible?
- [ ] Are connected nodes and complete reader journeys added where a selected object
      depends on them?
- [ ] Are expansion triggers defined for newly discovered content or defect classes?
- [ ] Are statistical estimates made only from a design capable of supporting them, with
      uncertainty disclosed?

### D. Methods and evidence

- [ ] Does each criterion name the assessment method, object, expected evidence, depth
      and coverage?
- [ ] Are deterministic scan, source examination, comparison, interview, test, reader
      evaluation and independent challenge used only for questions they can answer?
- [ ] Are source truth, cross-node coherence, workflow behavior and reader task success
      assessed separately where material?
- [ ] Are tool, environment, renderer, platform, inputs, conditions and outputs recorded?
- [ ] Does a tool failure or inaccessible source become `unable to assess` rather than
      pass?
- [ ] Is reused review evidence checked for changed object, source, environment, criteria,
      time and required independence?

### E. Reviewers and calibration

- [ ] Does each reviewer have the domain, documentation, accessibility, security,
      operational or reader expertise the assigned criteria require?
- [ ] Are self-review, conflicts and independence disclosed?
- [ ] Was a representative calibration set reviewed independently before production work?
- [ ] Were disagreements about applicability, result, severity and evidence resolved into
      clearer definitions or preserved as uncertainty?
- [ ] Is a disclosed portion double-reviewed during the cycle?
- [ ] Are reversal and disagreement patterns used to improve criteria and training?

### F. Findings and disposition

- [ ] Does every finding identify condition, criterion, evidence, consequence, object,
      revision, method and confidence?
- [ ] Are defect, gap, contradiction, observation, unable-to-assess, not-applicable and
      accepted-risk states distinct?
- [ ] Is severity based on consequence, reach, likelihood, detectability and recovery
      rather than edit size?
- [ ] Are severity, priority and due date recorded separately?
- [ ] Are duplicates and systemic instances linked without hiding affected nodes?
- [ ] Does each finding have an owner and explicit disposition authority?
- [ ] Are deferral, rejection, exception and risk acceptance accompanied by rationale and
      review or expiry conditions?

### G. Remediation and closure

- [ ] Does remediation update all materially affected nodes, relationships, journeys,
      examples, projections and controls?
- [ ] Is the original criterion retested at a named revision with recorded evidence?
- [ ] Is a merged change prevented from serving as closure evidence by itself?
- [ ] Are unresolved findings carried visibly into later cycles?
- [ ] Are reopened and escaped findings analyzed?
- [ ] Do recurring defects trigger changes to standards, templates, source generation,
      automation, ownership or reviewer guidance?

### H. Reporting and claims

- [ ] Does the report state population, baseline, criteria, risk model, sample frame,
      methods, depth, coverage and limitations?
- [ ] Are positive results, findings, unverified suspicions and unable-to-assess areas
      distinguished?
- [ ] Are denominators given for every coverage percentage?
- [ ] Are purposive-sample observations kept from becoming corpus-wide prevalence claims?
- [ ] Are current content quality, review execution quality and remediation progress
      reported separately?
- [ ] Does the conclusion say exactly what decision the evidence supports and what it does
      not support?
- [ ] Is sensitive finding information routed outside the public corpus where required?

## Common failure modes

- **Checklist ceremony:** every box is checked with no evidence or operational pass rule.
- **Validator equivalence:** an all-node structural scan is described as full content
  review.
- **File-count budgeting:** effort is estimated from 205 files while ignoring 3,936 claim
  entries, source chains, journeys and tests.
- **Equal-depth review:** low-risk descriptive leaves and destructive recovery procedures
  receive identical effort.
- **Risk tunnel vision:** only known critical nodes are selected, so the risk model can
  never discover its own blind spots.
- **Convenience sampling:** reviewers choose familiar or short nodes and call the result
  representative.
- **Random-only sampling:** rare but catastrophic instructions are left to chance.
- **Purposive projection:** defect rates from a targeted high-risk sample are generalized
  to the corpus.
- **Frozen sample despite discovery:** new defect classes appear, but selection does not
  expand.
- **Node isolation:** atomic nodes pass individually while the reader journey between
  them fails.
- **One-method assurance:** desk review substitutes for execution, or execution
  substitutes for truth and reader comprehension.
- **Interview as truth:** owner recollection is accepted without corroborating artifacts
  or behavior.
- **Expert familiarity:** the author or owner unconsciously fills gaps the target reader
  cannot.
- **Independent ignorance:** an outside reviewer lacks enough domain knowledge to detect
  false but plausible claims.
- **Uncalibrated reviewers:** each reviewer applies a private definition of clarity,
  support and severity.
- **Silent correction:** reviewers edit defects immediately, erasing the observation,
  prevalence and root-cause trail.
- **Pass by tool failure:** unsupported syntax, network failure or unavailable environment
  disappears from the denominator.
- **N/A laundering:** difficult criteria receive unexplained not-applicable results.
- **PR-equals-closure:** a patch merges without retesting the criterion or dependants.
- **Finding landfill:** issues are recorded without owners, due states, escalation or
  follow-up.
- **Perpetual waiver:** accepted risks have no authority, condition or expiry.
- **Score compression:** a large number of low-risk passes hides one severe operational or
  security defect.
- **Metric gaming:** teams optimize reviewed-node count or closure time by shrinking depth
  or dismissing hard findings.
- **Snapshot confidence:** a successful periodic audit is treated as protection against
  later drift.
- **Audit-only maintenance:** review happens periodically but not when code, decisions,
  sources or incidents change.
- **Defect harvesting:** repeated classes are fixed locally without changing the control
  that allowed them.

## Competing positions and reconciliations

### “Review everything deeply” versus “sample to make the work feasible”

A full deep review avoids sampling uncertainty but can become slow, inconsistent and
superficial at 205 nodes and 3,936 evidence entries. Sampling preserves depth but omits
objects. Use a census for cheap deterministic checks and the highest-consequence strata;
apply structured plus random deep review elsewhere; expand when discovery shows the
sample is inadequate. Never call sampled depth full-corpus assurance.

### “Prioritize by risk” versus “risk scoring hides unknown risk”

Risk directs scarce expertise toward consequence. It also encodes current assumptions.
Retain a random discovery component, review the risk model after escapes, and include
novelty and ownership gaps as risk signals. Risk is a routing hypothesis, not a property
the node proves about itself.

### “Independent review” versus “review by the person who understands it”

Independence improves challenge and reduces self-confirmation; expertise is necessary to
recognize technical error. Use competent independent reviewers for high-consequence work
where available and combine documentation and domain expertise when one person cannot
supply both. Disclose self-review rather than pretending a small team has separation it
does not.

### “One universal checklist” versus “genre-specific review packages”

A universal core improves consistency and comparison. A flat list becomes irrelevant and
encourages mechanical N/A answers. Maintain a versioned core, then compose criteria by
genre, content features, risk, audience and delivery surface. Report which package each
object received.

### “Fix as you find” versus “preserve an audit trail”

Immediate correction shortens exposure and is appropriate for urgent harm. Silent
correction loses the finding, cause and denominator. Record the observation first, issue
interim notification for urgent defects, then remediate and retest. The evidence need not
delay a critical fix.

### “Review status belongs in each node” versus “keep review state separate”

Embedding status makes review visible beside content and can simplify queries. It also
adds volatile workflow fields to canonical knowledge, creates churn and confuses node
lifecycle with assurance at a specific revision. A separate register keyed by stable node
id, revision and criterion version is likely cleaner, but synthesis should compare query,
atomicity, retention and governance requirements before deciding.

### “Automate as much as possible” versus “review is human judgment”

Automation supplies repeatable population coverage for encoded rules and frees people for
meaning. It cannot decide truth, relevance, safe context or comprehension. Use tools as
named assessment methods with tested boundaries, and preserve human evidence for the
criteria that require it.

### “A passing review should activate the node” versus “status and assurance differ”

A review may be one prerequisite for `active`, but status expresses the node's lifecycle
and present standing while a review result is scoped to criteria, methods and revision.
Do not equate them implicitly. If Buzz wants review to govern promotion, establish that
relationship explicitly with authority, evidence and handling for later change.

### “Count defects to measure quality” versus “findings measure the review too”

Findings are jointly produced by content and detection. Deeper review often raises counts
before quality improves. Interpret findings with coverage, depth, selection, reviewer and
criteria changes. Favor recurrence, escapes, current high-risk evidence and verified
closure over a raw count target.

### “Periodic audit” versus “continuous review”

Change-time review is timely and efficient but sees only diffs and predicted dependants.
Periodic audit sees accumulated and cross-cutting conditions but ages immediately. Use
both, joined by dependency and event triggers and a shared finding register.

## Claim ledger

| Claim | Support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Information review belongs throughout the lifecycle and applies to subsequent releases, not only final publication. | ISO/IEC/IEEE 26513:2017 public ISO and IEEE descriptions | The complete normative procedures were not publicly available | High |
| A managed review programme should be evidence-based, risk-based, competent, repeatable and continually improved. | ISO 19011:2026 public description and preview headings; GAO 2024 quality-management overview | Both frameworks govern audit domains other than documentation corpora | Medium-high |
| Method, depth and coverage are separate dimensions of assessment and should scale with assurance and adverse impact. | NIST SP 800-53A Rev. 5, sections 3.2.3 and Appendix C | NIST's defined levels assess security and privacy controls; Buzz would need its own operational definitions | High |
| Structured selection should be checked by a random discovery set and expanded when new content or finding types appear. | WCAG-EM 2.0 steps 3.1, 3.2 and 4.3 | Its exact sample rule and conformance conclusions belong to accessibility, not generic content quality | High |
| Complete processes should be included when selected objects participate in a workflow. | WCAG-EM 2.0 step 3.3 | Documentation journeys require adaptation because nodes are not web application views | Medium-high |
| Facts about a sample are not automatically facts about its population; representativeness, size, variability and precision matter. | NIST/SEMATECH handbook on populations and sampling | Corpus defects may not satisfy simple statistical assumptions; expert design may be required | High |
| Stratification and randomization reduce systematic sampling error. | NIST/SEMATECH sampling-scheme guidance | Bad strata or an incomplete frame can preserve bias | High |
| Review conclusions and significant findings need sufficient appropriate evidence tied to objectives. | GAO Government Auditing Standards 2024, reporting requirements | Buzz is not performing a GAGAS engagement | High |
| A review record should preserve comments, dispositions, rationale and the completed trail. | GOV.UK periodic-review checklist | The guidance governs UK government standards, not software documentation nodes | Medium-high |
| Relevant technical competence, independence and agreed consistency rules strengthen peer review. | NASA software peer-review guidance | Full independence may be impractical and does not replace documentation or user expertise | Medium-high |
| Prior evidence can be reused only after checking changes, time, applicability and independence. | NIST SP 800-53A Rev. 5 section 3.2.3.5 | The source addresses security assessments; exact reuse periods for Buzz remain undecided | High |
| Buzz's validator provides broad structural census coverage but no semantic body verdict. | Local validator, corpus instructions and standards | Other checks outside this validator could assess some body properties in future | High |
| Buzz currently has 205 parsed nodes and 3,936 evidence entries, of which 158 nodes are draft. | Read-only front-matter parse at the recorded repository revision | Counts change with the corpus and exclude `schema/` | High |
| The current node schema has no fields for a corpus-review result or lifecycle. | Local node schema | A separate system may exist outside the inspected corpus; absence from node schema may be intentional | High |
| Stable ids and structured metadata make a separate review register feasible. | Local schema and identifier model | Feasibility does not establish that a separate register is the best adopted design | Medium |
| Pull-request content review and periodic corpus review answer different assurance questions. | Local review standard; lifecycle and audit sources; analysis in this report | A highly mature continuous impact system could reduce periodic effort, but none proves the two questions identical | High |
| One composite corpus score would conceal method, depth, coverage, severity and selection differences. | NIST dimension separation; W3C reporting model; metric analysis | A carefully defined index can be useful for a narrow operational decision if its components and limits remain visible | Medium-high |

## Implications for the later corpus checklist

This topic should contribute a **review wrapper** around the substantive criteria from
topics 1–13 and 15. It should not duplicate all of those criteria into a larger flat
checklist.

The wrapper needs at least nine controls:

1. **Objective and authority:** the decision, owner, criteria and stopping rules.
2. **Population and baseline:** inventory, revision, surfaces, journeys and exclusions.
3. **Risk and selection:** census strata, structured sample, random discovery and
   expansion triggers.
4. **Assessment design:** applicable criteria, methods, depth, coverage and required
   expertise.
5. **Calibration:** pilot, examples, overlap, disagreements and criterion revision.
6. **Finding record:** condition, criterion, evidence, consequence, severity and
   uncertainty.
7. **Disposition and closure:** owner, authority, remediation, retest, expiry and reopen.
8. **Reporting:** denominators, assurance boundaries, unverified areas and permitted
   conclusions.
9. **Learning loop:** recurrence, escapes and improvements to upstream controls.

The substantive packages then draw from:

- the [quality model](01-quality-model-for-technical-documentation.md);
- [genre-specific criteria](02-genre-specific-quality-criteria.md);
- [truth and evidence](03-truth-and-evidence-in-living-technical-documentation.md);
- [completeness and coverage](04-measuring-corpus-completeness-and-coverage.md);
- [information architecture](05-information-architecture-for-atomic-documentation.md);
- [usability and findability](06-documentation-usability-and-findability.md);
- [freshness and change impact](07-freshness-staleness-and-change-impact.md);
- [procedural and operational review](08-reviewing-procedural-and-operational-documentation.md);
- [normative and descriptive writing](09-normative-versus-descriptive-technical-writing.md);
- [architecture documentation](10-architecture-documentation-quality.md);
- [terminology consistency](11-terminology-and-conceptual-consistency.md);
- [examples, commands, code and configuration](12-examples-commands-code-and-configuration.md);
- [accessibility and inclusive comprehension](13-documentation-accessibility-and-inclusive-comprehension.md);
  and
- the forthcoming security and disclosure research.

The eventual checklist should be executable as a review plan and record, not only as
questions. Every applied criterion should produce evidence, an explicit result and a
bounded conclusion.

## Limitations and open questions

- This research did not perform the actual corpus review, so it provides no present
  defect prevalence or readiness conclusion.
- The 205-node and 3,936-entry counts are a snapshot of one local revision and exclude the
  corpus schema subtree.
- No current rendered corpus, reader journey, link graph completeness, source-access
  rate, ownership map or review-cost measurement was established.
- No statistically valid sample was drawn, and no sample size should be inferred from
  W3C's accessibility-specific formula.
- No reviewer calibration trial or inter-reviewer agreement measurement was performed.
- Public ISO material exposed scope, status and high-level structure, not the complete
  normative clauses of ISO/IEC/IEEE 26513:2017 or ISO 19011:2026.
- The 26513:2017 ISO page says a replacement is expected; this report uses the current
  published edition and records that revision risk rather than researching the final
  unpublished replacement text.
- NIST, W3C, GAO, NASA and GOV.UK sources govern different domains. Their transferable
  process patterns require Buzz-specific validation.
- The present branch-protection and required-check configuration was not queried live;
  local standards' dated observations were treated as local evidence, not asserted as
  current platform state.
- The current schema's lack of review fields does not establish whether review data
  belongs in front matter, a separate repository file, GitHub issues, or another system.
- A public finding register may be inappropriate for security-sensitive observations;
  topic 15 must inform that boundary.
- The appropriate audit owner, approval authority, reviewer pool, time budget and cadence
  are governance decisions not answered by research alone.
- Status promotion, review assurance and publication readiness are currently distinct
  ideas; any binding relationship among them needs an explicit decision.

Questions for synthesis:

1. What first decision should the corpus review support: active-node trust, draft
   promotion, remediation planning, publication readiness, or another outcome?
2. Should the first cycle census all 47 active nodes deeply before sampling among the 158
   drafts?
3. Which nodes and journeys qualify as high consequence, and who has authority to approve
   the risk model?
4. Which deterministic criteria can be safely added without making the existing
   validator imply semantic assurance?
5. Where should review plans, per-node results, findings, exceptions and retest evidence
   live?
6. What fields belong in canonical node metadata, and which would create workflow churn?
7. What sample precision or discovery goal justifies the sample size?
8. What minimum overlap is feasible for calibration and independent challenge?
9. Which specialists are required for security, operations, accessibility, architecture
   and evidence review?
10. What finding classes block publication or `active` status, and who may accept the
    rest?
11. How will dependency changes trigger focused reassessment and invalidate reusable
    evidence?
12. Which metrics will be used for learning, and which will explicitly not become
    performance targets?
13. How will sensitive findings be separated from the public report while leaving an
    auditable disposition?
14. What constitutes enough evidence to close a finding and prevent recurrence?

## Sources

Standards and assessment frameworks:

- [ISO/IEC/IEEE 26513:2017 — Requirements for testers and reviewers of information for users](https://www.iso.org/standard/67417.html)
- [IEEE/ISO/IEC 26513-2017 public description](https://standards.ieee.org/ieee/26513/6082/)
- [ISO 19011:2026 — Guidelines for auditing management systems](https://www.iso.org/standard/19011)
- [ISO 19011:2026 public preview](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A19011%3Aed-4%3Av1%3Aen)
- [NIST SP 800-53A Revision 5 — Assessing Security and Privacy Controls](https://doi.org/10.6028/NIST.SP.800-53Ar5)
- [W3C WCAG Evaluation Methodology 2.0](https://www.w3.org/TR/wcag-em-2/)
- [NIST/SEMATECH handbook — Populations and sampling](https://www.itl.nist.gov/div898/handbook/ppc/section1/ppc134.htm)
- [NIST/SEMATECH handbook — Choosing a sampling scheme](https://www.itl.nist.gov/div898/handbook/ppc/section3/ppc332.htm)
- [NIST/SEMATECH handbook — Selecting sample sizes](https://www.itl.nist.gov/div898/handbook/ppc/section3/ppc333.htm)
- [GAO Government Auditing Standards 2024 Revision](https://www.gao.gov/products/gao-24-106786)
- [NASA Software Engineering Handbook — Peer reviews and inspections](https://swehb.nasa.gov/pages/viewpage.action?navigatingVersions=true&pageId=200212800)

Content-governance practice:

- [GOV.UK — Manage existing content](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/manage-existing-govuk-content/)
- [GOV.UK — Checklist for a major or periodic review](https://www.gov.uk/government/publications/handbook-for-standard-managers/checklist-undertaking-a-major-or-periodic-review)

Local evidence:

- [Corpus README](../../docs/corpus/README.md)
- [Corpus instructions](../../docs/corpus/AGENTS.md)
- [Node schema](../../docs/corpus/schema/node.schema.json)
- [Review-requirements standard](../../docs/corpus/standards/review-requirements.md)
- [Status standard](../../docs/corpus/standards/status.md)
- [Provenance standard](../../docs/corpus/standards/provenance.md)
- [Documentation standard](../../docs/corpus/standards/documentation-standard.md)
- [Corpus validator](../../project-intelligence/corpus/validate.py)
- [Corpus inventory tool](../../project-intelligence/corpus/inventory.py)
- [Full-ecosystem audit, 2026-08-18](../../docs/audits/audit-2026-08-18-full-ecosystem.md)
