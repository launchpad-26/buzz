---
description: Research into defining, detecting, prioritizing, and resolving freshness, staleness, and change impact in the Buzz documentation corpus.
tags: [documentation, corpus, freshness, staleness, change-impact, traceability, maintenance, research]
---

# Freshness, staleness, and change impact

Researched 2026-09-06–07. This is research, not an adopted corpus standard.

## Research question

How should Buzz define, detect, prioritize, and resolve documentation freshness and
staleness, and how should changes to code, configuration, decisions, tests, sources,
or other nodes create reviewable impact candidates without implying that every changed
dependency makes a node stale?

The investigation considered nine subquestions:

1. What do *fresh*, *current*, *stale*, *outdated*, *deprecated*, and *retired* mean,
   and which of them are properties of claims rather than whole documents?
2. Why are document age, last-edit time, and review date weak substitutes for semantic
   currency?
3. Which changes can invalidate factual, inferential, normative, procedural, and
   historical content?
4. What does a recorded revision establish, and how does it differ from version
   applicability, lifecycle status, or a review result?
5. How can citations and typed relationships support change-impact analysis without
   creating an unmanageable false-positive queue?
6. Which checks can detect definite defects, and which can only nominate content for
   human review?
7. How should risk, audience, use frequency, and consequence affect review priority
   and acceptable delay?
8. Which outcomes can a reviewer choose after an impact signal?
9. Which measures reveal a controlled maintenance system rather than merely recent
   editing activity?

## Bottom line

Freshness is **semantic currency for a stated use and baseline**, not recency. A claim
is current when it remains accurate, applicable, sufficiently supported, and
authoritative for the reader, environment, product version, and decision or task it is
meant to serve. It becomes stale when a relevant change makes one of those conditions
false. An old statement about a stable invariant can remain current; a statement edited
today can already be stale if it describes the wrong version or copies an incorrect
source.

That definition produces three distinctions that should govern later checklist work:

1. **A change signal is not a staleness verdict.** A cited file changing, a symbol
   disappearing, a test failing, or a dependent node being deprecated establishes a
   reason to inspect. It does not by itself establish that the documentation claim is
   wrong. The empirical literature supplies direct false-positive examples: a removed
   flag remained relevant for a supported installation case, and removed literal code
   did not remove the behavior the documentation described.
2. **Staleness exists at more than one level.** A locator can be broken while its claim
   remains true; one claim can be stale while the rest of a node remains current; a
   node can be internally correct but inapplicable to the deployed version; a journey
   can lead through a retired dependency even when every page renders; and a generated
   projection can lag its canonical nodes.
3. **Verification is an evidence-producing act.** A recent edit, `active` status, green
   schema validation, valid URL, extant commit, or recorded review date is only a
   signal. Currency requires checking the claim against the applicable authoritative
   source or exercising the real workflow where that is the relevant evidence.

Standards reinforce maintenance as a lifecycle and change-control responsibility.
[ISO/IEC/IEEE 26514:2022](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
places information development throughout the software lifecycle and explicitly covers
updating, maintenance, version control, and change control. Its definition of change
control includes identifying, documenting, reviewing, and authorizing changes, examining
effects on other items, and notifying affected people.
[ISO/IEC/IEEE 23026:2023](https://www.iso.org/standard/81896.html)
likewise treats management and sustainment as part of an informational website's
lifecycle and calls for relevant, timely information and consistent, efficient
maintenance. These sources support controlled maintenance; they do not prescribe one
universal review interval.

For Buzz, the current provenance discipline is a sound historical baseline but not a
complete freshness system. Every inspected node records one repository revision for the
whole evidence ledger. The provenance standard says that revision may move only when
every claim is known to hold at the new revision. The schema, however, has no per-claim
verification revision, applicable product version, owner, review trigger, review result,
or freshness state. The validator checks citation forms and file existence, but not
whether cited positions remain within file bounds or whether cited content still
supports the claim.

A read-only scan of the 205 non-fixture nodes at the current worktree found:

- 47 nodes marked `active` and 158 marked `draft`;
- all 205 carrying a recorded revision, drawn from eight distinct commits dated from
  2026-08-26 through 2026-08-31;
- 195 nodes, including all 47 active nodes, citing at least one repository file changed
  between their recorded revision and the current `HEAD`; and
- 32 positional citations beyond the current end of their target file, spread across
  12 nodes and seven files.

The third count is a deliberately broad **impact-candidate queue**, not a count of stale
nodes. Some shared sources are cited by dozens of nodes, so a small set of changes can
create a large review cascade even when most claims remain true. The fourth count is a
definite locator defect, but still not proof that all 32 associated claims are false.
This local result is the strongest argument for a two-stage system: inexpensive
automation should find and rank candidates and definite structural defects; accountable
reviewers should decide semantic currency and record the outcome.

## Scope and method

This report concerns content currency and the propagation of source changes through a
living documentation corpus. It does not decide:

- exact procedure-writing and runbook-testing requirements, covered by topic 8;
- normative versus descriptive language, architecture-document quality, terminology,
  examples, accessibility, or public security disclosure, covered by later topics;
- a schema migration, ownership model, service-level objective, CI gate, or tracking
  product;
- whether every current corpus claim is true; or
- LLM-specific generation, retrieval, attribution, or review controls, which remain set
  aside for this research sequence.

Local inspection covered the node schema, relationship schema, corpus authoring guide,
provenance, evidence, status, deprecation, linking, atomicity, code-reference,
test-reference, and generated-content standards, the validator and its tests, and all
non-fixture node front matter. Read-only scripts parsed recorded revisions and citation
positions, resolved Git commits, compared normalized cited paths against each node's
baseline, and compared positional citations with current file lengths. These scans
identified review candidates; they did not attempt natural-language entailment.

External sources were selected in this order:

1. ISO/IEC/IEEE standards for information lifecycle, maintenance, and change control;
2. peer-reviewed empirical work on outdated code references and software-documentation
   use;
3. controlled experiments on traceability-supported change-impact analysis;
4. primary practitioner guidance for operational playbooks and change review; and
5. platform documentation for a concrete ownership-trigger mechanism.

Search broadened across software documentation, configuration management, artifact
co-evolution, traceability, operational practice, and ownership. Strong claims below
are tied to sources with direct scope. Architecture-traceability experiments are not
treated as proof that the same effect size will occur in Buzz, and results from popular
GitHub and Google-owned repositories are not generalized to all documentation systems.

## Definitions

| Term | Meaning here |
|---|---|
| Baseline | The specific repository revision, product version, deployment state, policy set, or other configuration against which a claim is evaluated |
| Currency | Whether content remains accurate, applicable, supported, and authoritative for its intended use at the target baseline |
| Freshness | Evidence-backed confidence that currency has been established recently enough or after the relevant changes; not merely a recent timestamp |
| Stale claim | A claim that no longer holds or no longer applies at the target baseline because its subject, context, evidence, or authority changed |
| Outdated locator | A citation, path, position, symbol, command, link, or navigation cue that no longer reaches what it purports to identify |
| Change trigger | An event capable of affecting a claim, such as a code, configuration, test, policy, dependency, interface, ownership, or node-status change |
| Impact candidate | A claim, node, journey, or projection nominated for review by a change trigger; not yet judged stale |
| Verification | An accountable check against the relevant authoritative source or real workflow, with enough context to reproduce or audit the judgment |
| Review interval | A maximum elapsed period before a risk-based recheck even if no explicit trigger was captured |
| Applicability | The product version, environment, role, platform, state, or conditions under which a claim is intended to hold |
| Deprecation | A lifecycle warning that content remains an answer for now but is on a path out of currency, subject to the corpus's adopted status semantics |
| Retirement | A lifecycle state stating that the node is no longer the corpus's current answer, while its stable identity remains for inbound references |

The report uses *fresh* cautiously. It is often interpreted as “recently edited,” while
the desired property is “verified after relevant change for the intended context.”
Where precision matters, *current at baseline X* is the stronger formulation.

## A multi-level model of staleness

Treating a document as simply fresh or stale hides both the defect and its repair. A
later review should ask which level failed.

| Level | What can become stale | Example | What the signal proves |
|---|---|---|---|
| Locator | Path, line range, symbol, URL, command name, issue, or anchor | Cited line 899 no longer exists | The reference cannot be followed as written; not necessarily that the proposition is false |
| Evidence | Test result, decision, source file, external authority, or team statement | A cited test passed before the implementation changed | Prior support no longer establishes current behavior |
| Claim | One factual, inferential, normative, or procedural proposition | “The relay rejects X” after acceptance behavior changes | The proposition is wrong or inapplicable for the target baseline |
| Node | A coherent content unit | One procedure mixes current steps with a removed prerequisite | Some or all of the node no longer serves its declared purpose |
| Relationship | A typed dependency or contextual link | A current node depends on a retired prerequisite | The graph can still resolve structurally while its semantic route is invalid |
| Journey | A sequence needed to answer a question or complete a task | Setup instructions omit a newly mandatory configuration step in another node | Individually plausible pages do not produce a current end-to-end outcome |
| Projection | Generated index, graph, report, bundle, or rendered site | Search index generated from an older corpus revision | The view is reproducible but no longer reflects the canonical baseline |
| Subject lifecycle | The documented capability, interface, policy, or system | A feature is removed or a policy superseded | Content may need historical labeling, deprecation, retirement, or replacement rather than editing into apparent continuity |

These levels support precise outcomes. Repairing a line range is different from
rewriting a false claim. Retiring a subject is different from marking a page “reviewed.”
Regenerating an index is different from reverifying the nodes it lists.

### Six dimensions of currency

A claim can be current in one dimension and stale in another:

1. **Truth currency:** does the proposition still match observable behavior or the
   authoritative record?
2. **Applicability currency:** does it identify the versions, environments, roles, and
   preconditions where it holds?
3. **Authority currency:** is this still the source allowed to define the behavior or
   policy, or has a controlling decision superseded it?
4. **Evidence currency:** does the cited evidence still support this proposition at the
   target baseline, with locators that can be inspected?
5. **Operational currency:** can the intended reader still execute the procedure and
   obtain the promised outcome under realistic conditions?
6. **Relationship currency:** do dependencies, replacements, contextual links, and
   generated projections still connect readers to current content?

A recent edit can satisfy none of these. Conversely, a ten-year-old explanation of an
unchanged protocol invariant can satisfy all relevant dimensions.

## What the local corpus already establishes

### Provenance records a historical assertion, not an automatic freshness verdict

The schema gives a node one evidence ledger and no dedicated revision field. By
convention, every current node includes a FACT stating that the node was authored and
checked against a cited commit. The corpus provenance standard interprets this as a
whole-ledger assertion: moving it to a later revision is honest only when every claim
is known to hold there.

That standard supplies two routes for untouched claims. A reviewer may reopen the
source and reverify the claim, or—only where all citations name repository files—use a
normalized Git diff to show that those sources did not change. Any non-file citation
closes the second route. Touched claims always require reverification. Leaving the
recorded revision unchanged is an accepted conservative outcome when the whole ledger
was not checked.

This is valuable provenance discipline because it prevents a small edit from silently
granting every other claim a newer baseline. It has four limits as a freshness system:

- one revision covers an entire ledger, so mixed per-claim currency cannot be expressed;
- an unchanged source proves only that the cited file did not change, not that the claim
  was originally correct or that external reality stayed fixed;
- a changed source says only that review may be needed, not that the claim changed; and
- the validator recognizes commit citations but neither establishes that the commit
  exists nor compares claims with that revision.

There is also a concrete local drift signal. The authoring guide still describes the
provenance question as unestablished work for issue `#1321` and says it will defer when
that work lands, while `standards/provenance.md` now exists and declares that it settles
the question. This is a body-level inconsistency that schema validation cannot see. It
illustrates how duplicated policy statements can diverge even inside a carefully
governed corpus.

### Status is lifecycle information, not proof of currency

The schema permits `draft`, `active`, `deprecated`, `retired`, and `flagged`. It checks
only enum membership. The status and deprecation standards give the values human
semantics, but the validator does not determine whether a transition was justified,
whether an active node remains current, whether a deprecated body explains the risk,
or whether inbound links should be repointed from a retired target.

The deprecation standard usefully separates two cases:

- `deprecated`: still the corpus answer, but on the way out; its body should explain
  why and whether the claims still hold; and
- `retired`: no longer the current answer; its stable file and identifier remain so
  references resolve, and the body should identify a replacement or say none exists.

This reinforces that lifecycle state cannot substitute for verification. An `active`
label can be stale. A `retired` node can remain historically accurate. A `flagged` node
can describe current behavior while exposing an unresolved authority conflict.

### Evidence precedence means “newest” is not always “current”

Buzz already distinguishes claims about observed behavior from claims about intended or
authorized behavior. Executable evidence is authoritative for current system behavior;
accepted normative decisions govern intention or authorization, including when code has
drifted. Therefore a later code commit cannot automatically supersede an accepted policy
for a normative claim, and a newer prose page cannot overrule a current executable
result for a behavioral claim.

Change impact must route by claim type and authority. “Pick the newest source” would
erase precisely the conflicts the corpus's `flagged` state is designed to expose.

### Atomicity is also a freshness control

The atomicity standard's maintenance-clock test asks whether parts of a proposed node
change for different reasons or at different rates. Stable concepts and volatile
implementation details often belong in separate nodes—or the detail may not belong in
the corpus at all. This is not merely an information-architecture preference. It limits
the blast radius of a source change and allows volatile content to carry stronger
triggers and shorter review expectations without forcing stable explanations onto the
same clock.

### The validator deliberately stops before semantic currency

The validator checks that a file citation resolves and that a position is syntactically
well formed. Its tests deliberately accept a cited line beyond the validator file's own
end and explain that bounds checking belongs to future staleness work. It does not open
the cited location to determine whether the text supports the associated statement.
Commit, graph-edge, and tool-result citation forms are reported as unverified rather
than established.

This boundary is sensible: position bounds and path existence are deterministic;
natural-language support and applicability judgments usually are not. The gap is that
the deterministic bound check is not yet implemented, so a green validation run allows
locators that no longer identify any current line.

### Test evidence expires by change and context, not merely time

The test-reference standard states that a pass supports current behavior only for the
invocation and revision that produced it. Conditional suites, ignored integration
tests, retry policies, environmental assumptions, and flaky outcomes all change what a
green result means. A historical pass remains a historical fact, but it is not evidence
that the current implementation still behaves the same after a relevant change.

This suggests an important rule for all dynamic evidence: preserve the old result as a
dated observation, but do not silently relabel it as current. Rerun the relevant check,
record the invocation context, or lower/narrow the claim.

## External evidence

### Maintenance and change control are lifecycle processes

[ISO/IEC/IEEE 26514:2022](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
treats information for users as part of the software lifecycle rather than a one-time
deliverable. It covers managed reuse across software versions and includes updating,
maintenance, version control, and change control in its process structure. Its change-
control concept requires the effect on other items to be examined. The transferable
principle is that a source change and the information products affected by it belong to
one controlled system.

[ISO/IEC/IEEE 23026:2023](https://www.iso.org/standard/81896.html)
extends the same lifecycle stance to websites carrying systems, software, service,
policy, plan, and procedure information. Its scope explicitly includes management and
sustainment and connects timely information with consistent, efficient maintenance.

[ISO 10007:2017](https://www.iso.org/standard/70400.html) is broader configuration-
management guidance, applicable from product or service concept through disposal. It
supports viewing documentation, code, decisions, configuration, and generated views as
configuration information under controlled change. Its public abstract does not justify
specific fields, review periods, or tooling, so this report uses it only for that
lifecycle principle.

### Outdated references are common, persistent, and automatable only in part

Tan, Wagner, and Treude's peer-reviewed study,
[“Detecting Outdated Code Element References in Software Repository Documentation”](https://researchmgt.monash.edu/ws/portalfiles/portal/571668171/559717602_oa.pdf),
examined popular GitHub repositories and Google-owned repositories. At the time of
analysis, 3.9% of detected code-element references in the first dataset and 2.7% in the
second were outdated under the study's definition. At document level the figures were
19.2% and 9.7%; at project level, 28.9% and 5.4%. References still outdated at the time
of analysis had mean durations of 4.7 and 4.2 years. Across project histories, the
problem affected more artifacts than a point-in-time scan exposed.

The numbers should not be imported as a Buzz benchmark. The study's definition is
narrow—a code element once existed, was removed, and the documentation reference
remained—and the authors limit generalization beyond their sampled repositories. Its
more durable findings are methodological:

- machine detection can expose problems that survive for years;
- a repository-, document-, and reference-level result tell different stories;
- historical analysis reveals temporary and recurring inconsistency hidden by a
  current snapshot; and
- maintainers need source revision, documentation revision, timestamps, and links to
  investigate a flag.

Most importantly, the study demonstrates why a detector must produce candidates rather
than verdicts. Four of eight responding maintainers classified reports as false
positives. In one case, a removed build flag remained relevant to a supported user
configuration; in another, the named literal disappeared while equivalent behavior
remained. Changelogs and multi-version documentation can also legitimately mention
removed elements. The authors conclude that some false positives require individual
maintainer verification, and their approach can miss semantically stale text where the
named code element still exists.

### Traceability improves impact analysis, but links have semantics and costs

In two controlled experiments on architecture evolution,
[Javed and Zdun](https://eprints.cs.univie.ac.at/4160/) found statistical evidence that
traceability links reduced missing and incorrectly retrieved assets and improved the
overall quality of change-impact analysis. The setting was software architecture, not
documentation-corpus maintenance, so the safe inference is limited: explicit relations
can help reviewers find ripple effects that unaided inspection misses.

Buzz's typed `depends-on`, `supersedes`, `implements`, `references`, and `part-of` edges
are therefore potentially valuable, but only if change routing respects their meaning.
A `depends-on` edge asserts a currency dependency; `references` supplies context without
one. Treating both as equal invalidation edges would manufacture noise. Conversely,
using only explicit graph edges would miss impacts carried by file citations, shared
terminology, copied prose, operational sequences, and implicit assumptions.

The empirical code-reference study supplies the counterweight: even a seemingly exact
symbol relationship can be semantically ambiguous. Traceability reduces search space;
it does not remove the review judgment or the cost of keeping the trace links current.

### Operational documentation gains currency through use and exercise

Google's SRE guidance on
[on-call practice](https://sre.google/workbook/on-call/) recommends keeping playbooks
current, updating them with fresh information when the corresponding alert fires, and
running emergency-response exercises. It also emphasizes high signal-to-noise alerts,
because false positives create alert fatigue. This is practitioner evidence rather than
a universal standard, but two principles transfer well:

1. a real incident or drill is both a use of operational documentation and a change/
   verification event; and
2. maintenance notifications need prioritization and signal quality, or people will
   learn to ignore them.

This does not mean waiting for incidents to discover stale procedures. It means that
operational use should feed corrections back into the source, while planned exercises
provide evidence where production failure is too costly a test.

### Ownership can route review, but assignment is not verification

GitHub's official
[pull-request review documentation](https://docs.github.com/en/pull-requests/reference/pull-request-reviews)
describes `CODEOWNERS` as a way to request reviews automatically when matching files
change, with repository settings able to require approvals. This is a concrete example
of a source-change trigger reaching accountable people. It does not establish that the
owners understand every dependent claim, that a requested reviewer actually checks the
documentation impact, or that content outside the changed path is covered. Ownership is
a routing mechanism, not a currency claim.

### Old documentation can retain value

Lethbridge, Singer, and Forward's three-study paper,
[“How software engineers use documentation: the state of the practice”](https://ieeexplore.ieee.org/document/1241364/),
reported that documentation was often not updated as promptly or completely as managers
advocated, yet outdated documentation could remain useful. The work is from 2003 and
does not describe Buzz's environment, but it blocks an overly simple policy: “stale” is
not synonymous with “worthless” or “delete.” Historical explanation, rationale, and
structural orientation can retain value if labeled honestly and prevented from posing
as current instruction.

## A change-impact model for Buzz

The following model is a synthesis from the local contract and external evidence. It is
not a recommendation to add all of these concepts to front matter. It defines the
information a maintenance process needs, wherever that information ultimately lives.

```text
change event
    ↓
identify potentially affected dependencies
    ↓
create and deduplicate impact candidates
    ↓
rank by consequence, likelihood, audience, and exposure
    ↓
review the affected claim in its applicable context
    ↓
record one outcome and its evidence
    ↓
repair, narrow, retire, flag, or confirm current
    ↓
check downstream nodes, journeys, and projections
```

Each transition has a distinct burden of proof:

- **Change event:** prove that something changed, not that documentation is wrong.
- **Candidate creation:** show a defensible dependency path from the change to the
  content, with the reason it might matter.
- **Prioritization:** explain consequence and exposure, not semantic truth.
- **Review:** compare the precise claim with the applicable authoritative source or
  execute the relevant workflow.
- **Outcome:** record what was decided, by whom or under what authority, at which
  baseline, and what follow-on work remains.
- **Closure:** ensure that relationships, entry points, generated views, and affected
  journeys now point at the intended current answer.

This chain avoids turning a Git diff into an unsupported semantic conclusion.

### The candidate should be explainable

A useful impact item should answer at least:

- what changed;
- which claim, node, or journey may be affected;
- how the dependency was inferred—citation, typed edge, shared term, ownership rule,
  test, generated-source relation, or manual report;
- the baseline from which change was measured;
- the target baseline and applicability context;
- why the possible error matters; and
- whether the signal is a definite structural defect or a semantic review candidate.

Without that explanation, reviewers must rediscover the causal path and cannot judge
false positives efficiently. The queue becomes a list of changed files rather than a
change-impact system.

### Trigger taxonomy

No single trigger covers all ways content goes stale. A later policy should select
triggers by claim type and risk.

| Trigger | Potential impact | Automatable result | Human question |
|---|---|---|---|
| Cited file changed | Facts, examples, architecture, commands, or procedures may have moved or changed | Candidate with diff and affected citations | Did the changed hunk alter the proposition, applicability, or locator? |
| Cited position outside current file | Locator no longer identifies current text | Definite locator defect | Is the claim still true elsewhere, and what should replace the locator? |
| Named symbol, option, endpoint, event, or config key removed or renamed | Reference or instruction may be unusable | Candidate; sometimes definite broken token | Was behavior removed, renamed, relocated, aliased, or retained for another version? |
| Test changed, stopped running, failed, became flaky, or changed conditions | Behavioral support weakened or changed | Candidate plus execution metadata | What did the cited result actually establish, and does it still? |
| Accepted decision superseded or amended | Normative claim or rationale may lose authority | Candidate along `implements`, `depends-on`, and `supersedes` routes | Which rule now governs, and did implementation or docs drift? |
| Dependency version or environment changed | Applicability, syntax, defaults, or behavior may change | Candidate if dependency is declared | Does the claim apply to the new baseline, old baseline, both, or neither? |
| Corpus node deprecated, retired, or flagged | Downstream currency or navigation may be affected | Candidate along semantically relevant inbound edges | Must the source be updated, repointed, narrowed, flagged, or left as historical context? |
| External source changed, disappeared, or published a new edition | Evidence or authority may change | Link/version signal; semantic review candidate | Is the cited edition still the applicable authority? Does a newer edition supersede it? |
| Ownership or team responsibility changed | Review routing or escalation may fail | Candidate to update routing metadata or process | Who is now competent and accountable to verify the claim? |
| Incident, support case, failed task, or user correction | Procedure or explanation may be incomplete, ambiguous, or wrong | Captured feedback and affected-journey candidate | Was the documentation causal, contributory, or merely encountered? |
| Scheduled risk review reached | Hidden external or implicit change may have been missed | Review candidate, never stale verdict | Does the content still hold despite no captured trigger? |
| Canonical node changed | Index, bundle, graph, or rendered view may lag | Definite generation mismatch when revision contract exists | Must the projection be regenerated, or is it intentionally pinned? |

### Trigger strength is not uniform

Triggers can be classified by what they establish:

1. **Definite structural failure:** missing file, impossible line range, duplicate or
   unresolved identifier, malformed applicability, broken deterministic generation.
2. **Strong semantic candidate:** removed command, failed current test, superseded
   controlling decision, or changed dependency directly named by a claim.
3. **Weak semantic candidate:** any change anywhere in a broadly cited file, elapsed
   time, ownership churn, or a generic shared-term match.
4. **Observed-use failure:** a representative user or operator cannot achieve the
   documented outcome. This is strong evidence against the content in that context,
   though investigation may show a product or environment defect rather than a prose
   defect.

The queue should preserve this class. Collapsing every signal into one “stale” badge
destroys both meaning and priority.

## How claim type changes the review

The same change can have different implications depending on what a sentence asserts.

| Claim type | Appropriate current source | Typical invalidating change | Review action |
|---|---|---|---|
| Descriptive behavior | Current executable system, tests interpreted in context, implementation | Behavior, default, state transition, API, configuration, or environment changes | Exercise or inspect current behavior; distinguish intended from observed |
| Normative requirement | Accepted decision, governing standard, authorized policy | Decision superseded, amended, re-scoped, or authority changed | Read the controlling decision; do not let newer implementation silently overrule it |
| Historical fact | Pinned revision, release artifact, incident record, dated source | Source corruption, misquotation, or scope error; later change usually does not invalidate a clearly historical statement | Preserve the baseline and label history explicitly |
| Inference | Current supporting evidence plus stated reasoning | Evidence changes, assumption fails, or a stronger explanation appears | Re-evaluate reasoning and confidence; do not promote recency to fact |
| Team knowledge | Identified provider and current organizational context | Provider disavows it, responsibility changes, or authoritative evidence becomes available | Reconfirm, replace with supported class, narrow, or remove |
| Procedure | Current system plus prerequisites, permissions, environment, and verified outcome | Any step, order, precondition, command, permission, interface, or verification result changes | Execute the complete path in a representative context |
| Rationale | Accepted decision and contemporaneous context | Decision superseded or context changes enough to invalidate applicability | Preserve historical rationale; add or link the current decision rather than rewriting history |

This is why “latest timestamp wins” is unsafe. A 2026 implementation change may be
evidence that code violates a 2025 accepted policy, not evidence that the policy is
obsolete. Conversely, an old test result cannot prove current behavior merely because
no newer prose contradicts it.

## Review outcomes

An impact review needs more than “close” or “update.” At least these outcomes should be
distinguishable:

| Outcome | Meaning | Required follow-through |
|---|---|---|
| Confirmed current | The claim still holds at the target baseline and applicability | Record the verification basis; update the recorded baseline only within the provenance rules |
| Locator repair | The claim holds, but its citation or navigation target moved | Replace the locator and verify that the new target supports the same claim |
| Content correction | The claim is false, incomplete, ambiguous, or misleading | Correct it, reverify neighboring claims, and inspect affected dependants |
| Applicability narrowed | The claim holds only for some versions, platforms, roles, or environments | State the boundary clearly and route other contexts to their answer |
| Source or product defect | Documentation reflects the authorized requirement, while implementation or another source is wrong | Keep the normative claim; file or link the product/source correction and expose conflict if unresolved |
| Flagged conflict | Same-type authoritative sources conflict and a human decision is required | Record both sources without silently choosing; use the corpus's defined flagged process |
| Deprecated | Content remains the answer temporarily but is on the way out | State why, whether claims still hold, expected replacement, and transition implications |
| Retired | The node is no longer the current answer | Preserve stable identity; state why and link the replacement or say none exists |
| Historical retention | Content is intentionally about an older baseline | Label the baseline and prevent current-task entry points from presenting it as current |
| False positive / no semantic impact | The trigger did not affect the claim | Record enough reason to suppress or refine repeated identical alerts |
| Unresolved / escalated | Evidence or authority is insufficient for a verdict | Name the missing evidence and responsible decision path; do not mark current by default |

The false-positive outcome is operationally important. Without it, a detector cannot be
tuned, the same candidate recurs after every scan, and maintainers receive no evidence
that the queue's precision is improving.

## Prioritizing the impact queue

A flat queue will fail in a corpus where a small number of shared files are cited by
many nodes. Prioritization should combine consequence and likelihood rather than count
days alone.

### Consequence factors

- safety, security, privacy, compliance, financial, or irreversible operational effect;
- production recovery, deployment, rollback, credential, or data-handling use;
- whether a wrong answer causes confident action rather than obvious failure;
- audience reach and frequency of use;
- whether content is a prerequisite or hub for many downstream journeys;
- whether the reader can independently detect and recover from error;
- whether the node is presented as active/current or clearly historical; and
- whether the affected claim controls other documentation, automation, or review.

### Likelihood and exposure factors

- directness and semantic strength of the dependency;
- size and relevance of the changed hunk rather than whole-file change alone;
- volatility of the subject and the elapsed time since last meaningful verification;
- known product, dependency, or organizational churn;
- broken locator, failing check, user report, incident, or other observed contradiction;
- breadth of applicable versions and environments;
- ambiguity or missing applicability metadata; and
- number of independent triggers pointing to the same content.

### A practical ordering

Without adopting numeric weights, a defensible order is:

1. confirmed contradictions and failed high-consequence workflows;
2. definite structural defects blocking verification or leading to the wrong target;
3. direct impacts to high-consequence active content;
4. direct impacts to frequently used or highly connected active content;
5. weaker signals on active content, ordered by volatility and exposure;
6. impacts to draft, deprecated, historical, and retired content where readers can still
   encounter or depend on it; and
7. low-consequence elapsed-time reviews with no other signal.

`draft` should not mean “ignore.” Draft material can still be found, cited, copied, or
used by agents and people. Status can reduce or change priority only when delivery
surfaces reliably expose what that status means.

## Ownership and maintenance clocks

Every high-value current node needs a viable route to someone able to make a currency
judgment. That does not necessarily require a permanent individual owner in each file.
Possible routing units include a team, capability steward, code owner, service owner,
decision authority, or rotating documentation maintainer.

The checklist should separate four roles that organizations often collapse:

- **change author:** knows what changed but may not know every downstream use;
- **content maintainer:** can edit the node and understand its purpose;
- **subject authority:** can decide whether a normative or technical claim holds;
- **reviewer or approver:** independently checks the evidence and change outcome.

One person may fill several roles, but the responsibilities remain distinct. An
automatically requested owner proves only that routing occurred. An approval proves
currency only if the review contract actually required the relevant comparison.

Maintenance clocks should follow volatility and consequence. Stable conceptual nodes
may rely mostly on explicit change triggers and occasional audits. Version-specific
commands, operational recovery steps, external policies, and rapidly changing
interfaces justify stronger triggers and shorter maximum intervals. The interval is a
backstop for missed or external changes, not the primary definition of freshness.

## Measures that reveal maintenance health

Metrics should represent the candidate-to-decision process and the consequences of
missed staleness.

### Useful measures

| Measure | What it can reveal | Required qualification |
|---|---|---|
| Open impact candidates by risk and age | Unreviewed change exposure | Separate definite defects, strong candidates, and weak candidates |
| Time from causal change to candidate creation | Trigger coverage and latency | Requires a defensible causal link |
| Time from candidate creation to reviewed outcome | Maintenance responsiveness | Stratify by consequence and status |
| Confirmed-stale rate by trigger | Detector precision and queue quality | A low rate may mean noisy detection or genuinely healthy content |
| False-positive recurrence | Whether suppressions and trigger logic improve | Preserve reviewer reasons, not just closure counts |
| Confirmed stale duration | How long readers were exposed after an invalidating change | Often knowable only after review establishes the causal event |
| Broken-locator count and repair time | Deterministic reference integrity | Does not measure semantic truth |
| Risk-weighted current content with no viable reviewer route | Ownership/control gap | “Owner present” must mean reachable and competent |
| Scheduled-review yield | Whether intervals discover issues missed by triggers | Low yield may justify longer intervals for that risk class |
| Escaped stale-content incidents or user failures | Consequence of missed detection | Needs careful attribution; reports are undercounted |
| End-to-end procedure or journey pass rate | Operational currency in tested contexts | Record versions, environment, invocation, and flaky/conditional outcomes |
| Projection lag from canonical revision | Whether generated views reflect current nodes | Says nothing about whether canonical claims are true |

### Seductive but weak measures

- percentage of pages edited in the last quarter;
- average document age;
- presence of a “last reviewed” date;
- number of owners assigned;
- number of links returning HTTP 200;
- percentage of documentation touched in the same pull request as code;
- raw count of stale alerts without precision or risk;
- green schema-validation rate; and
- total queue closure rate.

All can be useful diagnostics. None establishes that readers receive current answers.
They are particularly gameable: touching a date, performing a bulk formatting change,
or closing low-risk items can improve the number while leaving the dangerous claim
untested.

## Candidate checklist criteria

These are research outputs for later synthesis, not current Buzz requirements.

### Claim and applicability

- Is each current claim precise enough to compare with an authoritative source or
  observable outcome?
- Does the content state the product version, environment, platform, role, state, and
  preconditions where ambiguity would otherwise result?
- Is historical content explicitly anchored to a historical baseline rather than
  phrased as present behavior?
- Are descriptive behavior, normative requirement, inference, rationale, and team
  knowledge kept distinguishable so the correct authority can be applied?
- Does any “current,” “supported,” “default,” “always,” or “never” statement have
  evidence appropriate to its volatility and consequence?

### Evidence and locators

- Does every citation still resolve to the intended artifact?
- Are file positions within current bounds, and does the current cited content still
  support the associated claim?
- If a symbol, command, option, endpoint, event kind, configuration key, or version is
  named, does it exist and behave as described in the applicable baseline?
- Are test results tied to a revision, invocation, environment, and interpretation,
  including conditional execution, retries, and flakiness?
- For external standards or sources, is the cited edition still the applicable one,
  and is a newer edition a supplement, successor, or irrelevant change?
- Does a pinned citation support a historical proposition only, or has current currency
  been established separately?

### Change triggers and traceability

- What kinds of change could invalidate this content, and are the important ones
  observable?
- Do typed relationships express actual currency dependencies rather than generic
  association?
- Can a source, decision, test, dependency, or node-status change produce an explainable
  candidate for affected content?
- Does candidate generation normalize positional paths and preserve the baseline,
  changed artifact, affected claim/node, and dependency reason?
- Are weak file-level matches kept distinct from definite failures and direct semantic
  dependencies?
- Can reviewers record false positives so recurring noise can be suppressed or refined?
- Are implicit dependencies—shared terminology, prerequisites, copied text, and
  multi-node task journeys—sampled or tested rather than assumed covered by citations?

### Review and disposition

- Is there a viable route to a person or group competent and authorized to judge the
  affected claim?
- Does review compare the claim with the right authority for its claim type rather than
  choosing the newest artifact?
- Is a real workflow exercised where inspection alone cannot establish the promised
  outcome?
- Does the outcome distinguish current, locator repair, correction, narrowed
  applicability, product/source defect, conflict, deprecation, retirement, history,
  false positive, and unresolved escalation?
- Is the decision recorded with its target baseline and evidence?
- When one claim changes, are neighboring claims and dependent nodes checked for
  assumptions invalidated by the same cause?
- After deprecation or retirement, do inbound dependencies and reader entry points lead
  to the intended current answer?
- Are generated projections refreshed from the correct canonical revision and visibly
  identified with that revision?

### Risk and cadence

- What harm could a confidently wrong reader action cause?
- How volatile is the subject, and how quickly could an invalidating change reach users?
- Is content highly connected, frequently used, or a prerequisite for critical tasks?
- Can readers detect failure and recover safely?
- Are explicit triggers the primary mechanism and elapsed-time review a backstop?
- Are review intervals justified by risk and observed audit yield rather than applied
  uniformly?
- Are unresolved high-risk candidates visible and escalated rather than hidden by an
  average freshness score?

### Measurement

- Are queue age and response time stratified by risk and trigger strength?
- Is detector precision measured from confirmed outcomes?
- Are confirmed stale duration and escaped user or operational failures tracked where
  causal evidence exists?
- Are broken locators reported separately from semantically stale claims?
- Do journey and procedure checks record applicability and execution context?
- Can a metric improve through a timestamp-only or formatting-only edit? If so, is it
  being treated as a diagnostic rather than a quality outcome?

## Failure modes to guard against

### Equating age with staleness

Age is an exposure or audit signal, not semantic evidence. Uniform “review every page
every 90 days” rules spend the same effort on stable rationale and volatile production
commands while still missing a breaking change on day one.

### Equating change with staleness

Broad file citations and shared governance sources create large cascades. Treating all
downstream nodes as stale encourages bulk date bumps or alert dismissal. The review
candidate must retain its uncertainty.

### Treating an unchanged source as proof

The source may always have been misunderstood, an external assumption may have changed,
or the content may apply to a different deployed version. A clean diff narrows work; it
does not prove universal truth.

### Updating the revision without updating the evidence

A whole-node revision bump after checking only the edited sentence grants unsupported
currency to untouched claims. Buzz's provenance standard already forbids this. Bulk
automated bumps would make the ledger look fresher while weakening its meaning.

### Using link health as truth testing

An HTTP 200 page can contain different content, a file can exist with unrelated lines,
and a symbol can survive after semantics change. Resolution and bounds checks are
necessary integrity checks, not entailment checks.

### Conflating lifecycle and accuracy

Active content can be wrong; deprecated content can still be current for a transition;
retired content can be accurate history; flagged content can expose a live conflict.
Status changes what the reader should do with content, not whether every sentence is
factually true.

### Requiring same-commit co-change everywhere

Co-changing docs and code can shorten exposure, but not every implementation edit
affects docs and not every documentation dependency is visible in the changed files.
Making file co-change the universal gate encourages ceremonial edits and misses policy,
environment, external-source, and journey impacts.

### Building a dependency graph with no semantics

A graph that treats “mentions,” “references,” “depends on,” “implements,” and
“supersedes” identically produces noise. A sparse, meaningful graph can support impact
analysis better than a dense web of generic associations.

### Alerting without capacity or closure evidence

An ever-growing queue teaches maintainers to ignore it. Candidate creation must be
paired with risk triage, reviewer routing, dispositions, suppressions, and measures of
false positives and response time.

### Deleting stale history

Erasing superseded content can break stable references and remove decision rationale.
The safer pattern is to preserve identity, label lifecycle and applicability, and route
current readers to the replacement.

### Trusting generated projections because they are reproducible

A deterministic artifact built from revision X faithfully represents revision X. It
does not thereby represent current canonical content or prove that revision X's claims
were correct.

## Competing positions and decisions left open

### “Every node needs a review date” versus event-driven verification

A date is easy to understand and useful for audit scheduling. It is also a weak signal
that can be refreshed without examining the content and cannot react immediately to an
invalidating change. The evidence favors event-driven triggers as the primary mechanism,
with risk-based intervals as a backstop for missed, implicit, and external changes.
Whether Buzz should store dates in node metadata, generated records, Git history, or an
external review system remains an implementation decision.

### Node-level versus claim-level currency

Node-level state is simple and matches the current whole-ledger revision. Claim-level
state is more precise but adds authoring, review, and tooling cost. The local scan shows
why precision matters: one changed shared citation can nominate a whole node even when
only one claim might be affected. The current schema cannot express mixed currency.
This research does not decide whether to change the schema; it recommends that any
node-level verdict preserve claim-level uncertainty instead of declaring the whole node
stale automatically.

### Blocking merge versus creating post-merge review work

For direct, high-consequence impacts, merge-time review can prevent exposure. For weak
or broad signals, blocking all change could stop normal development and reward
meaningless acknowledgements. A risk-tiered model is more defensible: deterministic
defects and selected critical dependencies may gate; weaker candidates may enter a
visible, time-bounded queue. The exact boundary requires human policy and maintenance-
capacity decisions.

### Content owner versus source owner

The person changing code has the freshest local context; the content or service owner
may understand downstream users and authority better. Neither is universally sufficient.
Routing can request both for high-risk changes, but mandatory dual ownership everywhere
may be impractical. Buzz should define responsibility by the decision required, not
assume a path-matching owner is automatically the subject authority.

### Automatic semantic checking

Formal or executable documentation can make some claims mechanically verifiable, and
research on controlled natural-language documentation shows this is feasible in bounded
domains. Most corpus prose still requires context, authority, and applicability
judgment. The code-reference study's false positives demonstrate the limit of treating
lexical disappearance as semantic invalidation. Automation should produce inspectable
evidence and narrow the search space; an eventual policy can identify limited claim
families where deterministic checks justify stronger conclusions.

### Uniform intervals versus risk-based clocks

Uniform cadence is administratively simple and comparable. Risk-based clocks allocate
effort more rationally but require a defensible risk classification and can leave low-
risk content untouched for long periods. A hybrid—change triggers, consequence-based
maximum intervals, and sampled audits of supposedly stable content—preserves the
advantages of both without asserting that one interval proves freshness.

## Claim ledger

| Claim | Support | Counterevidence or qualification | Confidence |
|---|---|---|---|
| Freshness should mean semantic currency at a stated baseline, not document recency | ISO lifecycle/change-control framing; local provenance contract; evidence-precedence rules | “Freshness” is not used with one universal definition across all sources; this is a synthesis | High |
| A changed dependency should create a review candidate, not an automatic stale verdict | Code-reference study's maintainer-confirmed false positives; local broad file-change cascade | Some deterministic failures, such as an impossible line position, can be verdicts about the locator | High |
| Staleness must be assessed below whole-document level | Empirical reference/document/project distinctions; local claim ledgers; broken-locator findings | A node-level state may still be an acceptable operational simplification if uncertainty is visible | High |
| Traceability can improve change-impact analysis | Two controlled architecture-evolution experiments; typed local relationships | Effect size may not transfer to Buzz; trace links themselves require maintenance and can create noise | Medium-high |
| Recorded revision, active status, and schema validity do not independently prove current content | Direct schema, standards, validator, and test inspection | They remain useful provenance, lifecycle, and integrity signals | High |
| Operational currency should be exercised through real use or drills where practical | Google SRE on-call guidance; current Buzz test-evidence principles | Practitioner guidance is context-specific; a drill does not cover every environment or future incident | Medium-high |
| Risk-based triggers and intervals are preferable to age-only policy | Consequence and volatility reasoning; alert-fatigue guidance; local cascade | Exact thresholds and capacity effects were not empirically tested in Buzz | Medium-high |
| Old or retired documentation can remain useful if clearly scoped | Lethbridge et al.; local stable-id and retirement design | Old operational instruction presented as current can be dangerous; usefulness depends on labeling and entry points | Medium-high |
| The current corpus has a large potential impact queue | Read-only Git comparison: 195/205 nodes cite at least one changed file since recorded revision | Broad file change is deliberately over-inclusive and is not a stale-node rate | High for the count; low for semantic impact without review |
| The current corpus contains positional locator defects that schema validation misses | 32 out-of-bounds citations; validator test explicitly accepts a beyond-EOF line | The associated claims may remain true and may be findable elsewhere | High |

## Local findings in detail

The read-only scan used each node's conventional recorded-revision evidence entry as
its baseline, stripped supported `:line` and `:start-end` suffixes before Git path
comparison, and excluded schema fixtures. All eight cited revision SHAs resolved in the
local repository. It then asked whether at least one cited repository file changed by
the current `HEAD`.

The result—195 candidate nodes and 222 distinct changed cited paths—is intentionally an
upper bound. Shared sources create visible fan-out: changed paths cited by many nodes
included the corpus authoring guide, root contributor guide, relay routing and ingest
code, evidence standards, and the validator. A file-level trigger cannot determine
whether the cited claim depended on the changed hunk.

The position scan asked a narrower structural question: does a current `path:line` or
`path:start-end` citation name positions within the current file? It found 32 failures
across 12 nodes. Several arose because formerly large implementation files are now much
shorter, while others were one-line boundary drift. The validator's own test deliberately
uses an out-of-range line to preserve the documented boundary that positions are not
bounds-checked. These are actionable locator defects, but repairing them still requires
finding the current evidence and checking that it supports the claim.

The current environment could not rerun the repository's Python validator because the
`jsonschema` dependency was unavailable, and activating Hermit attempted a sandbox-
restricted cache write. This did not affect the Git and file-bound scans or direct code
inspection. It does mean this report does not claim a fresh end-to-end validator result.

## Limitations and uncertainties

- Local counts describe this worktree on 2026-09-06–07, not a merged release or future
  corpus state.
- File-level Git comparison has high recall but unknown precision. It does not inspect
  changed hunks or prove semantic dependence.
- Position bounds detect only one locator failure class. In-range lines can still be
  unrelated; relocated evidence can still support the claim.
- The corpus's conventional recorded-revision statement was parsed as the baseline;
  the validator itself does not identify or verify that convention.
- External URL content, unpublished team knowledge, deployed environments, and live
  operational workflows were not exhaustively checked.
- The code-reference empirical study uses a narrower definition of outdatedness than
  this report and cannot establish Buzz's expected stale rate.
- The traceability experiments concern architecture assets, not atomic documentation
  nodes; transfer is principled but not quantitatively validated here.
- Practitioner guidance from Google and GitHub shows viable mechanisms, not universal
  organizational requirements.
- No ownership, review-cadence, CI-gating, or metadata design was tested with the
  launchpad cohort.
- This report does not evaluate LLM-specific risks or controls.

## Implications for the eventual synthesis

Topic 7 contributes the following propositions to the final checklist synthesis:

1. Define current content relative to claim, applicability, authority, evidence, and
   baseline; do not define it by age.
2. Preserve a three-way distinction between definite structural defect, semantic impact
   candidate, and confirmed stale content.
3. Treat provenance, lifecycle status, review timestamps, and generated revisions as
   different signals with different meanings.
4. Route change impact according to claim type, relationship semantics, and evidence
   authority.
5. Use deterministic checks aggressively for paths, bounds, symbols, versions, graph
   states, and generation contracts, but require contextual review for semantic truth.
6. Prioritize by consequence, exposure, volatility, and trigger strength rather than
   one universal age threshold.
7. Make review outcomes explicit, including false positive, applicability narrowing,
   product or source defect, conflict, deprecation, retirement, and historical retention.
8. Test high-consequence procedures and multi-node journeys in realistic contexts where
   inspection cannot establish operational currency.
9. Measure queue quality, response, confirmed stale duration, escaped failures, and
   audit yield—not recent-edit percentage alone.
10. Preserve uncertainty when the current node-level schema cannot express mixed
    per-claim currency.

## Sources

### Standards and official guidance

- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
- [ISO/IEC/IEEE 23026:2023 — Engineering and management of websites for systems, software and services information](https://www.iso.org/standard/81896.html)
- [ISO 10007:2017 — Guidelines for configuration management](https://www.iso.org/standard/70400.html)
- [Google SRE Workbook — On-call](https://sre.google/workbook/on-call/)
- [GitHub Docs — Pull request reviews](https://docs.github.com/en/pull-requests/reference/pull-request-reviews)

### Research literature

- Tan, Wagner, and Treude, [“Detecting Outdated Code Element References in Software Repository Documentation”](https://researchmgt.monash.edu/ws/portalfiles/portal/571668171/559717602_oa.pdf), *Empirical Software Engineering* 29, article 5 (2024).
- Javed and Zdun, [“The Supportive Effect of Traceability Links in Change Impact Analysis for Evolving Architectures—Two Controlled Experiments”](https://eprints.cs.univie.ac.at/4160/), 14th International Conference on Software Reuse (2015).
- Lethbridge, Singer, and Forward, [“How software engineers use documentation: the state of the practice”](https://ieeexplore.ieee.org/document/1241364/), *IEEE Software* 20(6) (2003).
- Kuhn and Bergel, [“Verifiable source code documentation in controlled natural language”](https://doi.org/10.1016/j.scico.2014.01.002), *Science of Computer Programming* 96 (2014).

### Buzz corpus sources inspected

- `launchpad/docs/corpus/AGENTS.md`
- `launchpad/docs/corpus/schema/node.schema.json`
- `launchpad/docs/corpus/schema/relationships.schema.json`
- `launchpad/docs/corpus/standards/atomicity.md`
- `launchpad/docs/corpus/standards/code-references.md`
- `launchpad/docs/corpus/standards/deprecation.md`
- `launchpad/docs/corpus/standards/evidence.md`
- `launchpad/docs/corpus/standards/generated-content.md`
- `launchpad/docs/corpus/standards/linking.md`
- `launchpad/docs/corpus/standards/provenance.md`
- `launchpad/docs/corpus/standards/status.md`
- `launchpad/docs/corpus/standards/test-references.md`
- `launchpad/project-intelligence/corpus/validate.py`
- `launchpad/project-intelligence/corpus/tests/test_validate.py`
- `launchpad/decisions/ADR-0028-corpus-canonical-representation.md`
- `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`
