---
description: Research into reviewing procedure-shaped and operational documentation for correctness, safety, executability, resilience, and evidence of realistic use.
tags: [documentation, corpus, procedures, operations, runbooks, playbooks, troubleshooting, testing, human-factors, research]
---

# Reviewing procedural and operational documentation

Researched 2026-09-07. This is research, not an adopted corpus standard.

## Research question

How should Buzz review procedure-shaped and operational documentation so that an
intended, appropriately qualified reader can select the right document, start from a
valid state, perform and coordinate the required actions safely, recognize divergence,
recover or escalate, and verify the promised result under realistic conditions?

The investigation considered twelve subquestions:

1. What distinctions among procedures, how-to guides, runbooks, playbooks,
   troubleshooting guides, checklists, and standard operating procedures matter during
   review?
2. What would make a procedure correct, reliable, robust, resilient, safe, usable, and
   operationally appropriate?
3. What must a reader know about applicability, competence, authority, starting state,
   tools, access, dependencies, and risk before acting?
4. How should actions, system responses, decisions, branches, warnings, stop conditions,
   handoffs, and completion criteria be represented?
5. When is linear instruction appropriate, and when would it conceal diagnosis,
   uncertainty, or adaptation?
6. How much explanation belongs beside action, and when should background move to a
   linked concept or reference node?
7. Which review methods establish textual accuracy, executability, team coordination,
   or readiness, and what does each method fail to prove?
8. How should destructive, irreversible, privileged, or time-sensitive actions be
   reviewed?
9. What makes operational documentation usable under interruption, degraded systems,
   time pressure, and incomplete information?
10. How should deviations and discoveries during execution feed maintenance?
11. Which measures reveal effective procedures rather than merely polished or recently
   edited pages?
12. What do Buzz's current procedure template and procedure-shaped nodes already cover,
   and where are the material gaps?

## Bottom line

A procedure is not good because its commands exist or its prose is easy to read. It is
good when the right reader can use it, in the stated conditions, to obtain the stated
result without unacceptable harm. For operational material, that result must hold not
only along the happy path but also at meaningful decision points, failures, interruptions,
handoffs, and recovery boundaries.

Five principles should govern the later review checklist:

1. **Review the whole action system, not only the sentences.** The relevant system is
   the reader, their competence and authority, the document, tools and interfaces,
   dependencies, environment, collaborators, and expected outcome. The UK Health and
   Safety Executive explicitly treats the task, individual, and organization as
   interacting human-factors concerns and warns that procedures do not replace
   competence or better hazard controls.
2. **Separate correctness from executability and readiness.** Source inspection may
   establish that a command is spelled as the repository defines it. It does not show
   that a qualified reader can complete the sequence in a representative environment.
   A walkthrough tests interpretation; a tabletop tests roles and decisions; a
   functional exercise tests coordinated performance in simulation; a live or
   production-like execution tests the actual workflow. Each produces different
   evidence.
3. **Make state transitions observable.** A useful action identifies its valid starting
   state, what the reader does, the expected system response, how to detect divergence,
   and the state that permits the next action. Final success needs positive evidence,
   not merely the absence of an error message.
4. **Treat recovery and escalation as part of the procedure.** Risky actions need a
   warning before the point of commitment, authority boundaries, termination criteria,
   and a tested recovery, rollback, roll-forward, cleanup, or escalation path. A
   procedure that succeeds only when nothing goes wrong is incomplete for operational
   use.
5. **Do not force uncertainty into a script.** Operational incidents can leave the
   initial state unknown and change while responders act. Research on industrial-control
   incident response reports that static playbooks can fail outside their designed
   scope. Procedures should constrain known safe actions while playbooks and
   troubleshooting material expose evidence gathering, decision criteria, coordination,
   and explicit routes for adaptation.

The strongest review model for Buzz is therefore:

> **Select → Prepare → Act and observe → Decide and coordinate → Verify → Recover or
> escalate → Learn and maintain.**

That model is deliberately broader than “are there numbered steps?” and narrower than a
full operational-readiness program. It can be applied to a small build how-to, a
destructive reset procedure, or a multi-role incident playbook with depth proportional
to consequence.

## Scope and method

This report covers action-oriented documentation used for planned technical work and
for diagnosis, response, restoration, and recovery. It includes procedures, how-to
guides, runbooks, playbooks, checklists, troubleshooting guides, and standard operating
procedures to the extent that their content tells people what to do.

It does not decide:

- a final Buzz vocabulary or whether the corpus needs every form named here;
- service-specific incident policy, release policy, access control, approval chains,
  recovery objectives, or on-call staffing;
- one universal test cadence or a corpus schema change;
- whether the current build and debugging nodes work in every environment;
- the technical correctness of every current procedure step; or
- LLM-specific generation and review controls, which remain set aside for this research
  sequence.

Local inspection covered the corpus procedure template, corpus authoring rules, schema,
evidence and testing guidance, all four `development` nodes, and the two nodes whose
bodies are procedure-shaped: the build and local-relay debugging guides. The inspection
looked at declared scope, evidence ledgers, prerequisites, action sequences, branches,
warnings, verification, recovery, relationships, and disclosed omissions. It did not
execute either procedure end to end.

External evidence was selected in this order:

1. ISO, IEC, and IEEE information-for-use standards for definitions, lifecycle scope,
   safety, and evaluation;
2. NASA and UK HSE human-factors guidance for procedure and checklist design;
3. current NIST incident-response guidance and NIST recovery and exercise publications;
4. peer-reviewed incident-playbook research for counterevidence to rigid scripts; and
5. primary practitioner guidance from AWS and Google SRE for software-operations
   conventions and testing practice.

The standards support general information quality and safety obligations, not a
Buzz-specific checklist. Aviation and process-safety sources concern higher-consequence
systems than most Buzz development work. Cybersecurity sources concern incidents, not
ordinary builds. Vendor guidance is experience-based rather than neutral consensus.
The report uses the common principles these sources converge on and does not transfer
their domain-specific effect sizes or mandates.

## Vocabulary is local, not universal

The authorities do not supply a single stable taxonomy. ISO/IEC/IEEE 26514 defines a
*procedure* as an ordered series of steps for performing a task and distinguishes a
user action step from a software response. Diátaxis uses *how-to guide* for practical,
goal-oriented directions addressed to an already-competent user. AWS uses *runbook* for
documented steps that achieve a specific, often planned or routine outcome, and
*playbook* for investigating incidents and determining scope and cause.

Buzz's [procedure template](../../docs/corpus/templates/procedure.md) instead draws its
procedure/runbook boundary by trigger: a procedure is a task the reader chose or
scheduled; a runbook starts from an alert, failure, or other already-firing condition.
That is coherent, but it conflicts with AWS's common usage. NIST recovery guidance uses
*playbook* broadly for recovery plans with preconditions, actions, milestones,
dependencies, communications, validation, and improvement. “Runbook” and “playbook”
therefore cannot serve as quality criteria without a local definition.

For review purposes, the following functional distinctions are more dependable than
labels:

| Form | Reader's initial need | Typical shape | Main review risk |
|---|---|---|---|
| Planned procedure / how-to | Achieve one known goal | Preconditions, ordered actions, bounded branches, verification | A plausible sequence has never worked from the stated starting state |
| Runbook | Execute a repeatable operational response, often after a trigger | Trigger, immediate checks/actions, expected responses, escalation and recovery | Trigger or authority is unclear; the document assumes healthy dependencies during degradation |
| Playbook | Investigate and coordinate a class of uncertain event | Goals, roles, evidence gathering, hypotheses or decision points, communications, adaptable actions | A rigid path creates false certainty outside its scenario |
| Troubleshooting guide | Diagnose or resolve a symptom whose cause is unknown | Symptom, discriminating observations, diagnostic branches, remedies, confirmation | It lists causes or commands without decision criteria or risks circular diagnosis |
| Checklist | Prompt or verify known work | Compact items in operational order, often with completion marks | It is mistaken for training or omits the context that makes an item safe |
| Standard operating procedure | Prescribe an organizationally governed way to perform normal or abnormal work | Scope, roles, mandated and discretionary actions, records, approvals | Normative force, exceptions, and responsible authority are ambiguous |

One document can combine these shapes, but a reviewer should identify the function of
each section. A checklist embedded in a runbook does not make the whole page a checklist;
a diagnostic branch inside a procedure does not make every step optional.

## The qualities to review

NASA's flight-deck procedure work offers a useful hierarchy, with cautious transfer to
software operations. Its primary requirements are correctness, reliability, robustness,
and resilience. It also considers efficiency, usability, coordination, workflow
integration, consistency with policy and operating philosophy, trainability, and
adaptability. Applied to Buzz:

| Quality | Review question |
|---|---|
| Correct | If the stated actions are performed in the stated state, do they lead to the stated outcome without contradicting authoritative behavior or policy? |
| Reliable | Under the documented normal conditions, does the procedure repeatedly produce that outcome rather than succeeding by accident? |
| Robust | Does it tolerate expected variation in platform, timing, data, operator action, dependency state, and output, or state its narrower applicability? |
| Resilient | When errors, interruptions, unexpected states, or partial failures occur, can the reader detect them and recover, adapt, or escalate safely? |
| Safe | Are hazards, data loss, security impact, cost, irreversibility, and blast radius controlled at the point where decisions are made? |
| Usable | Can the intended reader find, interpret, and execute it in the real work context with acceptable cognitive and coordination load? |
| Integrated | Does it fit actual tools, permissions, handoffs, policy, alerts, records, and neighboring procedures rather than describing an isolated ideal? |
| Maintainable | Are ownership, applicability, dependencies, change triggers, test evidence, and discovered deviations available for future review? |

This is not a scoring formula. A beautifully usable unsafe procedure should fail review;
an accurate procedure that nobody can select or complete should also fail. Consequence
sets the necessary depth: a local disposable build and production data restoration do
not need identical controls.

## Review the reader's path through state

### 1. Select the right document

Before the first command, the reader needs to know:

- the single promised goal or event class;
- the trigger or circumstances in which the document applies;
- explicit exclusions and nearby alternatives;
- supported versions, platforms, deployment types, and environments;
- whether the task is planned, diagnostic, emergency, or mandatory;
- current lifecycle status and any superseding procedure; and
- the competence and role assumed.

Wrong-procedure selection is itself a failure mode. Titles such as “reset,” “recover,”
or “build” are insufficient when multiple scopes exist. Symptoms must not be presented
as causes, and alerts must link to the appropriate operational response where possible.

### 2. Prepare a valid starting state

“Prerequisites” should describe observable preconditions rather than an inventory of
links. Depending on risk, review for:

- required knowledge, training, and role;
- tools and their supported versions;
- authentication, privileges, and approval authority;
- inputs, identifiers, configuration, secrets, and safe placeholder conventions;
- dependency health and relevant capacity;
- backups, restore points, or last-known-good state;
- maintenance window, customer impact, and communication needs;
- other people or third parties who must be available;
- a safe test or staging environment; and
- a preflight check proving the start state.

The HSE guidance is important here: a procedure and competence complement one another.
Adding more explanation cannot make an unqualified reader safe to perform privileged
work. Conversely, “expert audience” cannot excuse missing system state that even an
expert cannot infer.

### 3. Act and observe

Each action should make four things inspectable:

1. **Action:** what the reader does, with exact targets and unambiguous placeholders.
2. **Expected response:** what the system should show or become. This is not another
   numbered user action.
3. **Divergence:** what output, timeout, or state means the expected transition did not
   occur.
4. **Next route:** continue, retry, choose a branch, stop, recover, or escalate.

Reviewers should challenge:

- compound steps whose partial completion cannot be located;
- commands whose working directory, shell, account, environment, or target is implicit;
- copied output that is not distinguished from literal input;
- placeholders that can be pasted unchanged or expand to the wrong target;
- relative terms such as “recent,” “large,” “normally,” or “if needed” without decision
  criteria;
- timing assumptions without timeout or retry boundaries;
- branching labels that do not state the observation selecting the branch;
- hidden side effects, cleanup obligations, or cross-system consequences;
- a step order that differs from real tool or workflow order; and
- links that force the reader to reconstruct the sequence across many pages during the
  task.

Minimalism is valuable only when the least information needed for completeness remains.
ISO/IEC/IEEE 26514 defines minimalism around critical information plus what completeness
requires. It does not justify removing a precondition, expected response, or recovery
route because the result looks shorter.

### 4. Decide and coordinate

Decision points should be driven by observable conditions. A branch needs to state what
evidence distinguishes it, what uncertainty remains, who has authority, and whether the
choice changes customer impact or recovery options. If no documented branch fits, the
reader needs an explicit safe stop or escalation route rather than encouragement to
improvise invisibly.

Multi-role operations additionally need:

- an incident or task lead and named functional responsibilities;
- authority for high-impact actions such as shutdown, rebuild, data restoration, or
  public communication;
- handoff inputs and acknowledgements;
- a working record of observations, decisions, actions, owners, and times;
- communication channels and update expectations;
- third-party contacts and constraints; and
- a way to reconcile simultaneous work and prevent conflicting actions.

Current NIST incident-response guidance treats response as shared work spanning
leadership, handlers, technical staff, legal, public affairs, HR, asset owners, and
external parties. Google SRE guidance similarly emphasizes a clear command line,
defined roles, early declaration, and a working record. A command list alone cannot
establish operational coordination.

### 5. Verify the result

Verification must match the procedure's promise. Review for:

- intermediate checkpoints at consequential transitions;
- final positive evidence that the desired service, artifact, data, or state exists;
- negative checks for prohibited or residual states where relevant;
- validation from the user's or dependent system's perspective, not only the component
  that was changed;
- security and integrity checks before a restored asset returns to service;
- persistence across restart, redeploy, or handoff if the promised outcome requires it;
  and
- an explicit completion or termination declaration.

“The command exited zero” proves only that command's exit status. “No new alert fired”
proves only absence of that observation. Neither automatically proves the operational
goal. NIST recovery guidance explicitly calls for verifying that restored assets are
functional and secure before returning them to normal operation.

### 6. Recover, clean up, or escalate

Risk controls should appear immediately before the risky action, when the reader can
still change course. Reviewers should identify:

- destructive, irreversible, security-sensitive, costly, or wide-blast-radius actions;
- the exact target and scope, resolved before commitment;
- backup or restoration assumptions and evidence that they are valid;
- retry safety and idempotency;
- rollback feasibility, deadline, and loss of rollback options;
- roll-forward alternatives where rollback is unsafe or impossible;
- cleanup of temporary access, feature flags, credentials, resources, and partial state;
- stop-work criteria and who can terminate the operation;
- escalation thresholds, destination, required context, and interim safe state; and
- a fallback that does not depend on the same failed system.

A rollback instruction is not evidence that rollback works. It needs its own applicable
preconditions and verification. For high-risk work, the recovery path may deserve a
separate tested procedure rather than a final sentence in the primary path.

### 7. Learn and maintain

Execution should produce maintenance evidence without turning the canonical procedure
into a live incident log. Capture:

- baseline, environment, date, executor role, and procedure revision;
- branches taken and deviations from the documented path;
- unexpected states, missing permissions, hidden dependencies, and unclear steps;
- actual result, duration, assists, retries, rollback or escalation;
- safety or security observations; and
- assigned improvement actions and their closure.

NIST's exercise guidance ties evaluation criteria to objectives, records observations,
uses a prompt debrief, and turns findings into an after-action report and plan updates.
Google SRE likewise recommends realistic drills followed by an account of what worked,
what did not, and what should improve. A “tested” badge with no scope, result, or open
findings is much weaker evidence.

## An evidence ladder for procedural review

No single test proves every quality. A later checklist should ask for the strongest
reasonable evidence for the risk and claim, and record exactly what was exercised.

| Level | Method | What it can establish | What it does not establish |
|---|---|---|---|
| 0 | Structural and editorial review | Required fields, sequence readability, terminology, link and syntax validity | Command truth, successful execution, realistic usability |
| 1 | Source and policy inspection | Commands, flags, paths, defaults, interfaces, and authority match cited sources at a baseline | That dependencies are available or the sequence works end to end |
| 2 | Static or isolated executable checks | Command parsing, example validation, linting, individual step behavior, safe dry runs | Cross-step state, realistic permissions, timing, handoffs, final outcome |
| 3 | Qualified peer walkthrough | Selection, interpretation, missing knowledge, ambiguous decisions, apparent coordination gaps | Actual system behavior or performance under operational conditions |
| 4 | End-to-end execution in a disposable representative environment | Starting-state sufficiency, sequence executability, observable transitions, final verification, basic recovery | Production-only scale, degradation, real coordination, rare failure modes |
| 5 | Scenario or tabletop exercise | Roles, authority, decision criteria, communication, dependencies, gaps in a plan | Operation of the real systems; NIST distinguishes exercises from system tests |
| 6 | Functional simulation or game day | Coordinated performance with tools and injected failures in a simulated environment | Every production interaction or consequence |
| 7 | Controlled live execution or evidence from a real event | Behavior in the actual operational system and context | General reliability across future states; one success remains one observation |

This ladder is not a maturity score and higher is not always appropriate. A live test
can be unethical or excessively risky; a representative restoration test may provide
better evidence. Conversely, source inspection is enough for a claim that a recipe
defines a command but not for a claim that a reader can recover a service with it.

NIST SP 800-84 provides the clearest distinction: tests use quantifiable criteria to
assess systems or components in an operational or near-operational environment;
tabletops discuss roles and decisions; functional exercises perform responsibilities in
a simulated environment. It is an older cybersecurity publication, but its central
lesson remains valuable: exercising a plan and testing a system answer different
questions.

### Design tests from the promise and risk

Before testing, specify:

- the exact procedure revision and applicable baseline;
- the claimed outcome and evaluation criteria;
- starting state, environment, data, roles, and allowed assistance;
- representative variations and failure injections;
- safety controls and immediate termination authority;
- observations and artifacts to capture; and
- how findings become owned changes and a retest.

Useful scenarios include fresh setup, repeat execution, partial prior execution,
interruption and resume, dependency unavailable, permission denied, command timeout,
unexpected but valid output, wrong target caught at preflight, rollback after a partial
change, handoff between roles, and an out-of-scope condition that should trigger safe
escalation.

## Procedures under uncertainty

There is genuine tension between standardization and adaptation.

The case for standardization is strong: known safe sequences reduce recall burden,
support training, make coordination predictable, and preserve important checks. NASA's
procedure research, HSE safety guidance, and ISO information-for-use standards all
support clear, coherent, usable procedural support.

The counterposition is equally important. HSE warns against relying on procedures as
the sole control for hazards. NASA's earlier work warns that not everything can be
proceduralized. A 2021 peer-reviewed industrial-control incident-response study,
developed from interviews and refined through three red-team exercises, reports that
static playbooks can be ignored or fail to support events outside their initial scope;
communication, cross-domain information sharing, and organizational buy-in were major
concerns. A 2023 study argues that incident playbooks should connect response actions to
an explicit model of operational impacts and thresholds rather than describe process in
isolation.

The practical resolution is not “no procedures.” It is to distinguish:

- **known, safety-critical invariants**, which should be explicit and difficult to
  bypass;
- **repeatable actions**, which can be proceduralized and tested;
- **diagnostic observations and decisions**, which need branch criteria and working
  records;
- **uncertain strategy**, which needs roles, goals, constraints, communication, and
  authority for adaptation; and
- **out-of-scope states**, which need a safe hold, escalation, or transition to another
  playbook.

A procedure should never imply exhaustive coverage merely because it is detailed.

## Findings in the current Buzz corpus

### The corpus has two draft procedure-shaped development nodes

The 205 non-fixture nodes currently include four `development` nodes and no nodes typed
`operations`, `release`, or `verification`. Of the four development nodes,
[build.md](../../docs/corpus/development/build.md) and
[debugging.md](../../docs/corpus/development/debugging.md) are clearly action-oriented;
both are `draft`. The other two are reference-shaped prerequisites and Hermit material.
This does not prove an operations-coverage gap by itself—the schema type names product
surfaces rather than prose genres—but it means the corpus has little live procedural
evidence from which to infer a settled review practice.

### The procedure template already establishes a useful shape

The active template correctly emphasizes one goal, a competent reader, ordered action,
genuine branches, prerequisites, scope, boundaries, relationships, and disclosure of
what was not verified. It also distinguishes procedure-shaped prose from the schema's
subject-matter `type` field and warns against treating a reference table as evidence
that a procedure works.

Several points need attention during synthesis:

- Its procedure/runbook terminology is local and conflicts with AWS usage; the corpus
  should state that choice wherever both terms appear.
- The “around 8–10 steps” guidance may be a useful authoring prompt, but step count is
  not an evidence-backed quality threshold. A short procedure can omit vital recovery;
  a longer one can be safer when it exposes real state transitions.
- It says a procedure step should be a `FACT` or carry no claim label while also
  recommending end-to-end testing “where practical.” That permits a source-backed
  command to look stronger than the unexecuted sequence it belongs to. The later
  checklist should distinguish **step source accuracy** from **procedure execution
  evidence**.
- Its closing note says the first real procedure node has not yet been authored, but
  build and debugging nodes now exist. This is a small, concrete freshness defect in
  the template itself.

### The build guide is transparent but only partly executed

The build node has a goal, prerequisites, a Rust sequence, platform branches, success
checks, cleanup, boundaries, relationships, and a detailed omissions section. Its
evidence records that the full workspace debug build failed on a TLS certificate issue
in a voice dependency and that a build excluding `buzz-voice` succeeded. It also says
the desktop, web, mobile Android, and release build commands were read from source but
not executed.

That is good disclosure. It also demonstrates why claim granularity matters. The node
can truthfully say those recipes define the commands; it cannot yet say every platform
branch succeeds from the stated prerequisites. Review status should preserve this
difference rather than collapse it into “tested” or “untested.”

The body says it follows the procedure template, but it does not declare an
`implements` relationship in the relationship section. That weakens machine-visible
genre traceability even though the prose connection is evident.

### The debugging guide models risk disclosure but lacks live execution evidence

The debugging node provides a goal, prerequisites, logging steps, health checks,
symptom localization, a destructive reset branch, recovery verification, boundaries,
and omissions. It warns that `just reset` can wipe Desktop's local data because the
environments may share Docker names and ports, gives safer alternatives, and asks the
reader to recheck health afterward. Those are strong local examples of placing blast
radius, avoidance, and post-action verification beside a risky operation.

The node explicitly discloses that the `RUST_LOG=buzz_relay=debug` override was inferred
from source and tests but was not run against a live relay. It also identifies itself as
the first real test of the template's step-count guidance. The document therefore
should not be treated as end-to-end verified merely because its individual claims have
citations. Unlike build, its body declares `implements: corpus-template-procedure`, but
neither node records that connection in the schema's machine-readable top-level
`relationships` field.

### Local implications

Buzz already has unusually explicit evidence and omission practices. The missing layer
is an execution record capable of saying:

- which procedure revision and branch were run;
- on which platform, environment, configuration, and starting state;
- by what reader role and with how much assistance;
- which intermediate and final checks passed;
- whether failures, recovery, cleanup, and repeat execution were exercised; and
- which findings remain open.

That does not necessarily require new front matter. It does require the future checklist
to refuse an inference from “all steps cite source” to “the procedure works.”

## Candidate content-review checklist

These are research outputs for later synthesis, not current requirements.

### Identity and selection

- [ ] Does the title name one observable goal or a recognizable operational condition?
- [ ] Does the document say when to use it, when not to use it, and which alternative
  applies outside its boundary?
- [ ] Are supported versions, platforms, environments, deployment shapes, and lifecycle
  status explicit where they affect the result?
- [ ] Is the intended role, competence, and training level realistic?
- [ ] Is the document's function—planned instruction, response, diagnosis, checklist,
  or policy—clear even if local terminology differs from external conventions?

### Preconditions and risk

- [ ] Are tools, versions, working directory, inputs, access, privileges, approvals,
  dependencies, and starting state stated and checkable?
- [ ] Does a preflight check detect the wrong target, unhealthy dependency, missing
  backup, insufficient capacity, or absent authority before change begins?
- [ ] Are customer impact, cost, data loss, security impact, irreversibility, and blast
  radius identified in proportion to consequence?
- [ ] Are warnings placed immediately before the action while avoidance is still
  possible?
- [ ] Does the procedure supplement rather than pretend to replace necessary competence,
  engineering controls, or supervision?

### Actions, observations, and decisions

- [ ] Is each action unambiguous about actor, target, context, exact input, and order?
- [ ] Are expected system responses visually and semantically distinct from reader
  actions?
- [ ] Can the reader detect partial completion, timeout, unexpected output, and other
  divergence before continuing?
- [ ] Do branches name the observable condition that selects them and converge on a
  verified state, recovery path, or escalation?
- [ ] Are placeholders safe to recognize and replace, and are secrets kept out of
  examples and records?
- [ ] Does the sequence match the real interface and workflow, including waits,
  propagation, handoffs, and asynchronous state?
- [ ] Is background limited to what safe execution needs, with durable concepts and
  reference detail linked rather than duplicated?

### Coordination and uncertainty

- [ ] For multi-role work, are lead, responsibilities, authority, handoffs,
  communications, and record-keeping explicit?
- [ ] Can two responders follow it without issuing conflicting actions or losing the
  current state?
- [ ] Does it preserve evidence needed for diagnosis, audit, or later recovery?
- [ ] Does an out-of-scope or unknown state lead to a safe stop, constraint, or
  escalation rather than invented certainty?
- [ ] Are operational impacts and critical thresholds visible at decision points?

### Completion, recovery, and cleanup

- [ ] Do intermediate checks prove each consequential state transition?
- [ ] Does final verification positively establish the promised outcome from the
  relevant user or dependent-system perspective?
- [ ] Are residual unsafe, insecure, inconsistent, or temporary states checked?
- [ ] Are retry and repeat-execution semantics known?
- [ ] Are rollback, roll-forward, restoration, and cleanup instructions applicable and
  themselves verifiable?
- [ ] Are stop and escalation thresholds, destinations, required context, and interim
  safe state explicit?
- [ ] Can critical recovery information be reached when the primary service or normal
  documentation path is unavailable?

### Evidence and maintenance

- [ ] Does each procedural claim distinguish source/policy support from observed
  execution?
- [ ] Is there end-to-end evidence for the supported branch and environment, or a precise
  disclosure of what was not run?
- [ ] Was the intended reader involved in a walkthrough or test where ambiguity and
  usability matter?
- [ ] Were roles and decisions exercised separately from system operability where both
  matter?
- [ ] Were realistic variations, failures, interruption, recovery, and escalation tested
  in proportion to risk?
- [ ] Does the record identify revision, baseline, environment, objective, result,
  assistance, deviations, findings, and unresolved limitations?
- [ ] Do changes to commands, interfaces, dependencies, permissions, policy, alerts,
  ownership, or operational architecture trigger review?
- [ ] Are execution findings assigned, incorporated, and retested rather than merely
  archived?

## Measures worth collecting

Metrics should diagnose the procedure system, not reward document production. Useful
measures include:

- task completion and correct final-state rate by supported branch;
- unsafe or wrong-target actions caught before commitment;
- step-level divergence, retry, rollback, and escalation rates;
- time to detect divergence and time to reach verified recovery;
- reader assists, clarifying questions, and undocumented expert interventions;
- branch, environment, platform, failure-mode, and recovery-path execution coverage;
- frequency and severity of deviations from the documented path;
- tabletop or drill findings by role, decision, dependency, and communication;
- age and closure rate of procedure-derived corrective actions;
- changes since the last applicable execution;
- procedures inaccessible during the degradation they are meant to address; and
- real events in which no suitable procedure existed or an unsuitable one was selected.

Measures to treat cautiously include word count, number of steps, number of procedures,
recent edit date, page views, link validity, citation count, and a binary “tested” flag.
They can describe inventory or activity but do not establish safe task success.

## Common failure modes

1. **Command inventory masquerading as a procedure:** every command is real, but the
   starting state, order, transitions, and outcome are untested.
2. **Happy-path tunnel:** errors are acknowledged only by “try again” or “contact
   support,” with no safe state or context to preserve.
3. **Cause-free troubleshooting:** a list of possible causes has no observations that
   discriminate among them.
4. **Warnings after commitment:** the reader learns about data loss or customer impact
   after running the destructive action.
5. **Rollback theatre:** a rollback command exists but depends on an unverified backup,
   expired artifact, removed schema, or lost permission.
6. **Expertise as omission:** the author assumes an expert can infer local ports,
   identities, targets, policy, or hidden system state.
7. **Over-proceduralization:** an uncertain incident is presented as a complete linear
   script, suppressing observation and adaptation.
8. **Under-proceduralization:** “use judgment” replaces known invariants, authority
   boundaries, or safety checks.
9. **Checklists as training:** a compact cognitive aid is handed to someone who lacks
   the skill and mental model it assumes.
10. **Test collapse:** source review, command linting, a walkthrough, a tabletop, and a
    live execution are all reported simply as “validated.”
11. **Environment laundering:** success on one platform or disposable dataset is
    generalized to every supported branch.
12. **Normal-channel dependency:** the recovery guide, credentials, contacts, or status
    information becomes unavailable in the same outage.
13. **Unowned findings:** drills reveal gaps, but no one updates and reruns the procedure.
14. **Procedure-policy mismatch:** actual operators use a safer or more effective path
    than the official document, leaving practice and authority split.

## Competing positions and judgments

| Question | Position A | Position B | Research judgment for Buzz |
|---|---|---|---|
| Should every procedure be linear? | Linear steps reduce ambiguity and memory load | Real tasks can branch, overlap, and begin in uncertain states | Use the simplest faithful structure; require explicit decision criteria rather than artificial linearity |
| Is source inspection enough? | Repository truth can verify commands cheaply and reproducibly | Only a real run shows cross-step behavior and environmental assumptions | Source inspection establishes claim accuracy; execution evidence is separate and necessary for workflow claims |
| Should every procedure be fully tested? | Untested instructions create false confidence | Live tests can be costly, unsafe, or disproportionate | Scale evidence to risk and promise; disclose untested branches and prefer representative safe environments when live execution is inappropriate |
| Should procedures be minimal? | Short action-focused guidance reduces cognitive load | Missing context, warnings, responses, or recovery makes brevity unsafe | Remove explanatory detours, not operationally necessary state and decisions |
| Are runbooks and playbooks distinct universal genres? | Consistent labels improve navigation | Authoritative sources use the words differently | Adopt and publish local definitions; review functional shape rather than label alone |
| Should operators follow the document exactly? | Standardization protects known safe behavior and coordination | Novel incidents require adaptation | Mark mandatory invariants and discretionary decisions; log deviations and provide authority and escalation for out-of-scope states |
| Is a successful execution enough? | It is direct evidence the workflow can work | One success does not establish reliability or failure handling | Record it as scoped evidence and add representative variation according to consequence |

## Claim ledger

| Claim | Main support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Procedure quality concerns the reader, task, system, and organization, not prose alone | HSE human-factors and procedure guidance; NASA procedure design | Much source material is safety-critical and more demanding than ordinary developer tasks | High for principle; medium for any specific control |
| Correctness, reliability, robustness, and resilience are distinct procedural qualities | NASA/TM-2016-219421 | Flight-deck definitions are not software-operations standards | Medium-high as an analytic model |
| A software response should be distinguished from a user action step | ISO/IEC/IEEE 26514 public definition of step | Presentation conventions can vary | High |
| Procedure execution, plan exercise, and system testing produce different evidence | NIST SP 800-84 | Publication is from 2006 and cybersecurity-focused | High for the conceptual distinction |
| Operational response needs roles, authority, communication, records, and learning | NIST SP 800-61r3; Google SRE; NIST SP 800-84 | Exact role structures vary by organization and event | High |
| Recovery plans need preconditions, dependencies, restoration order, validation, termination, and improvement | NIST SP 800-184 | Cybersecurity recovery scope; published 2016 | High for recovery material |
| Static playbooks can fail under novel, uncertain incidents | AIR4ICS interview and exercise study; NASA/HSE warnings against over-proceduralization | One industrial-control context; does not show all static playbooks fail | Medium |
| Playbooks should expose operational impact as well as response process | Shaked et al. 2023 | Conceptual contribution demonstrated on a ransomware case, not broad outcome evidence | Medium |
| Buzz's procedure template covers core planned-task structure but not a full operational test model | Local template compared with source set | This report did not exercise the template with authors or readers | High for textual comparison; medium for workflow consequence |
| Buzz's two procedure-shaped nodes disclose important execution gaps | Local build and debugging nodes | Their current behavior was not independently rerun here | High for disclosure; no conclusion about current executability |

## Uncertainties and limitations

- Full normative text for IEC/IEEE 82079-1 and ISO/IEC/IEEE 26514 was not available
  without purchase. This report relies on official scope and public definitions and does
  not attribute inaccessible clause-level requirements to them.
- NASA's procedure-quality model and HSE's guidance come from aviation and major-hazard
  contexts. They strongly inform human-factors questions but do not make every control
  mandatory for low-risk developer documentation.
- NIST SP 800-84 and SP 800-184 are older publications. SP 800-61r3 is current as of
  April 2025 and still points organizations toward testing, training, and exercises, but
  local threat, system, and policy details change faster than these frameworks.
- AWS and Google SRE reflect mature large-scale operating environments and may assume
  tooling, staffing, or incident volume that Buzz does not have.
- The peer-reviewed playbook studies concern cybersecurity and industrial control. They
  support the need for operational context and adaptability but do not quantify a
  universal advantage over conventional runbooks.
- The local corpus scan is a snapshot of the current worktree. The research directory
  itself is untracked, and node counts will change.
- No intended reader performed a build or debugging task for this report. Local findings
  are content and evidence audits, not usability or operational-readiness results.
- Accessibility and inclusive comprehension are deferred to topic 13, though readable
  warnings and use under pressure overlap with that work.

## Implications for later synthesis

The final corpus checklist should not contain one undifferentiated “procedure is tested”
question. It should record a review profile with at least:

- procedural function and applicability;
- intended reader, authority, and starting state;
- consequence and recovery class;
- branches and environments covered;
- evidence level and exact execution scope;
- final verification and recovery evidence;
- open findings and untested claims; and
- change triggers for re-review.

Three questions require an explicit human decision during synthesis:

1. whether to retain the template's trigger-based procedure/runbook distinction and how
   to publish it so contributors are not misled by external terminology;
2. whether procedure execution evidence belongs in node front matter, a linked
   verification node, test artifacts, or a review system outside the corpus; and
3. which consequence classes require peer execution, recovery testing, a tabletop, or
   a functional exercise before a node can become `active`.

Until those decisions are made, the honest minimum is precise disclosure: which claims
came from source, which steps were actually performed, what conditions were represented,
what result was observed, and what remains unverified.

## Sources

### Standards and government guidance

- ISO, [ISO/IEC/IEEE 26514:2022, *Systems and software engineering — Design and
  development of information for users*](https://www.iso.org/standard/77451.html),
  with [public terminology and informative
  material](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen).
- IEC, [IEC/IEEE 82079-1:2019, *Preparation of information for use (instructions for
  use) of products — Part 1: Principles and general
  requirements*](https://webstore.iec.ch/en/publication/29075).
- Barshi, Mauro, Degani, and Loukopoulou, NASA/TM-2016-219421,
  [*Designing Flightdeck
  Procedures*](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20160013263.pdf),
  2016.
- UK Health and Safety Executive, [*Procedures*](https://www.hse.gov.uk/humanfactors/topics/procedures.htm)
  and [*Operating
  procedures*](https://www.hse.gov.uk/comah/sragtech/techmeasoperatio.htm).
- NIST, [SP 800-61 Rev. 3, *Incident Response Recommendations and Considerations for
  Cybersecurity Risk
  Management*](https://csrc.nist.gov/pubs/sp/800/61/r3/final), April 2025.
- NIST, [SP 800-184, *Guide for Cybersecurity Event
  Recovery*](https://www.nist.gov/publications/guide-cybersecurity-event-recovery),
  2016.
- NIST, [SP 800-84, *Guide to Test, Training, and Exercise Programs for IT Plans and
  Capabilities*](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-84.pdf),
  2006.

### Peer-reviewed and practitioner sources

- Smith, Janicke, He, Ferra, and Albakri, [*The Agile Incident Response for Industrial
  Control Systems (AIR4ICS)
  framework*](https://doi.org/10.1016/j.cose.2021.102398), *Computers & Security* 109,
  2021; [open accepted
  manuscript](https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/93044/He%20The%20Agile%20Incident%20Response%202021%20Accepted.pdf?isAllowed=y&sequence=2).
- Shaked, Cherdantseva, Burnap, and Maynard, [*Operations-informed incident response
  playbooks*](https://orca.cardiff.ac.uk/id/eprint/165303/), *Computers & Security* 134,
  2023.
- AWS, [*Operational Excellence Pillar — AWS Well-Architected
  Framework*](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html),
  2024.
- Google, [*Google SRE Workbook: Incident
  Response*](https://sre.google/workbook/incident-response/).
- Diátaxis, [*How-to guides*](https://diataxis.fr/how-to-guides/).
- The Good Docs Project, [*How-to guide
  template*](https://gitlab.com/tgdp/templates/-/raw/main/how-to/guide_how-to.md).

### Local Buzz material

- [Corpus procedure template](../../docs/corpus/templates/procedure.md)
- [Build the Buzz workspace](../../docs/corpus/development/build.md)
- [Debugging a local buzz-relay](../../docs/corpus/development/debugging.md)
- [Corpus authoring guide](../../docs/corpus/AGENTS.md)
- [Node schema](../../docs/corpus/schema/node.schema.json)
- [Evidence standard](../../docs/corpus/standards/evidence.md)
- [Test-reference standard](../../docs/corpus/standards/test-references.md)
