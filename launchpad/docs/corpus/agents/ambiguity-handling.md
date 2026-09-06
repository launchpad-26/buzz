---
id: agents-ambiguity-handling
type: agent
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "This node's type is agent rather than governance: standards/taxonomy.md's own choosing-a-value test says that when more than one enum value plausibly fits, the tie-break is how the corpus has actually used the enum, not what the label could stretch to cover, and names corpus-agents (AGENTS.md) as the one merged node written specifically as an agent harness's own instructions, carrying type: agent rather than defaulting to governance. This node, like agents-invariants before it, documents agent conduct within that same agents/ path family rather than corpus-wide process/policy in general, so it follows the same precedent rather than governance."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/taxonomy.md"
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.85
  - statement: "This node is built from templates/procedure.md (Diátaxis how-to form) rather than templates/runbook.md: procedure.md's own Boundary section draws the line as 'a task the reader chooses to perform on their own schedule' versus a runbook's 'condition that has already occurred and demands a response ... triggered by an alert or failure, not chosen.' Ambiguity handling is a decision point reached mid-way through a task an agent already chose to perform (creating, updating or retiring a corpus node per AGENTS.md), not an operational alert with severity/impact and an alerting-rule trigger -- runbook.md's own required sections (Trigger citing an alerting rule, Severity and impact) have no fitting referent here, since no alerting configuration exists for a documentation-authoring decision point."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
      - "launchpad/docs/corpus/templates/runbook.md"
    confidence: 0.85
  - statement: "AGENTS.md itself names a worked failure of skipping the check before concluding there is nothing to relate to: 'There was nothing to point at' was true when the corpus held only one node and stopped being true the moment a second one merged, and two independent agents authoring sibling nodes copied an earlier version of that paragraph and produced a false justification from it because they read a fact about one moment as a general rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md names a second worked failure of building on an unverified reading of a source: an earlier version of its own citation-shapes table claimed to summarize CONTRACT.md section 3's six shapes when it in fact listed seven, and an agent authoring a sibling node built a scope argument on that miscount before their plan review caught it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md names a third worked failure, of a source being classifiable in a way that once had no honest label at all: an earlier draft of its evidence-classification guidance left the case of an issue/PR/discussion-only source with no honest evidence class, which an agent authoring a sibling node hit directly, before the guidance was corrected to name TEAM_KNOWLEDGE with provided_by as the honest choice rather than forcing FACT or leaving the case unaddressed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "standards/taxonomy.md's step 3 states that when more than one type value plausibly fits, an author follows how the corpus has actually used the enum rather than what the label could technically stretch to cover, citing two data points (governance for corpus-process/policy nodes, agent for an agent-harness-instructions node) rather than a rule with the force of the schema; its step 4 states that when the fit is still imperfect after that test, the author says so in the node's own scope-and-omissions section rather than silently picking, naming corpus-readme.md's own disclosed imperfect fit as the worked example."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/taxonomy.md"
  - statement: "standards/taxonomy.md's step 1 states that type is a single string, not an array, and that if a node's subject genuinely spans two surfaces, that is evidence the node describes two ideas rather than one, and that AGENTS.md's one-node-one-idea rule (elaborated by standards/atomicity.md) governs that split, not the taxonomy document itself -- so a type-fit ambiguity that survives taxonomy.md's own test can turn out to be a node-count ambiguity in disguise, owned by a different document."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/taxonomy.md"
  - statement: "ADR-0029 states that evidence precedence is contextual by claim type, not one fixed hierarchy, and that this resolves the ordinary case of two different claim types each with their own tiebreaker; what it does not resolve is two sources with authority over the same claim type that contradict each other, where the corpus author stops and records the contradiction rather than picking a side, and the affected node stays unestablished/flagged until a human resolves it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "standards/decision-references.md fixes the author's behaviour when two accepted decisions conflict on the same intent claim as four concrete steps: write one evidence entry per contradicting record citing its own record and stating what it says; state the contradiction in the body naming both records; set the node's status to flagged; and escalate via a type:adr issue parented to the PRD that raised it, with the decision outcome left blank, because agents draft decisions but do not make them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "standards/review-requirements.md's MUST 8 requires a reviewer, when a node's status is or is being changed to flagged, to confirm each contradicting record is its own evidence entry, the body states the contradiction and names both records, and a type:adr issue exists or is filed in the same pull request -- and states a reviewer must not approve a pull request that clears a flagged status by picking a side without a linked, decided ADR settling it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/review-requirements.md"
  - statement: "agents-invariants.md's Q4 states that an author who finds two authoritative sources of the same claim type in conflict SHOULD stop and record the conflict rather than resolving it themselves, per ADR-0029, and SHOULD set status: flagged when the conflict touches a claim central to the node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "agents-invariants.md's Exceptions and escalation section states that a case none of its own I1-I10 invariants covers is escalated, not invented: it is raised as an issue against parent Feature #620, describing the invariant that seemed to be missing and why existing tooling did not catch its absence -- the same escalate-rather-than-invent pattern this node generalizes to any corpus-authoring ambiguity that no existing document already resolves."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "launchpad/AGENTS.md section 5's Rule 1 states that agents draft on their own authority but decide only on a human's: an agent may write any issue, PR, or ADR in full, but may not decide an ADR outcome, approve a PR, merge one, or close another agent's escalation on its own judgement."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 5's Rule 2 states that when the type is unclear an agent files a Task, adds needs-triage, and says so in the Objective, and states never to guess silently between PRD and Task because misfiling a PRD as a Task hides an approval gate -- a top-level, repository-wide instance of the same surface-and-ask discipline this node states for corpus-node ambiguity specifically."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: ".claude/skills/corpus-plan/SKILL.md's 'Stop on ambiguous scope' section instructs an agent not to resolve certain manifest-planning ambiguities by guessing, but to surface them and ask, naming as examples a parent Feature that doesn't obviously match its subject, two rows describing what looks like the same document under different paths, and a blocker alias spelled differently from any real path in the plan -- stating plainly that none of these is the manifest builder's job to catch, because its validation is structural, not semantic."
    entry_class: FACT
    evidence:
      - ".claude/skills/corpus-plan/SKILL.md"
  - statement: ".claude/skills/corpus-batch-author/SKILL.md states that this skill does not resolve an ambiguous DoD: an issue whose checklist does not resolve cleanly against the current schema/AGENTS.md is reported, not guessed at, and should not have been in the batch list to begin with, per what it names as plan-issue's own 'ambiguity is surfaced, not resolved' rule."
    entry_class: FACT
    evidence:
      - ".claude/skills/corpus-batch-author/SKILL.md"
  - statement: "The user-level plan-issue skill (not tracked in this repository) states, under 'How to write a step': 'Ambiguity in the issue is surfaced, not resolved. State both readings and ask. Picking one silently is how an agent builds the wrong thing confidently.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "~/.claude/skills/plan-issue/SKILL.md, a user-level skill outside this repository's tracked tree -- read directly on the authoring machine, but not citable as an in-repo FACT because validate.py's citation checker resolves a bare path against files inside this repository only"
  - statement: ".claude/skills/corpus-review/SKILL.md states that missing or unverifiable evidence is a finding, never a silent pass, and names a citation you cannot open -- a broken path, an ambiguous target, or an UNVERIFIED-only chain -- as an example that does not default to OK merely because validate.py did not reject it structurally, since validate.py checks that a citation resolves, never that it supports the claim."
    entry_class: FACT
    evidence:
      - ".claude/skills/corpus-review/SKILL.md"
  - statement: "Parent Feature #620's real acceptance criteria require schema/graph/provenance validation to pass with a genuinely-fitting template, concrete source start points, no broad overview duplicating another node's canonical claims, and that an independent reader can traverse from this node to implementation/verification evidence for a representative question -- the bar this node is built against rather than issue #640's own copied-over how-to-shaped Definition of Done tail, applied by checking each of the four criteria in turn against the finished draft."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 acceptance criteria, relayed in the corpus-batch-author dispatch brief for this task"
  - statement: "Issue #640's own Definition of Done states the objective as creating this file as 'the single canonical procedure node for ambiguity handling' and carries a how-to-shaped tail (states goal/prerequisites/scope, provides ordered executable steps, defines success verification and rollback/cleanup where relevant, links authoritative commands/config rather than generic advice), matching the same boilerplate DoD-tail pattern corpus-batch-author's own SKILL.md and templates/procedure.md's Note on Definition of Done both document recurring across this batch of tasks."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#640 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-taxonomy
  - type: references
    target: corpus-standard-atomicity
  - type: references
    target: corpus-standard-decision-references
  - type: references
    target: corpus-standard-review-requirements
  - type: references
    target: agents-invariants
  - type: implements
    target: corpus-template-procedure
---

# Ambiguity handling: how-to

What an agent authoring, updating, or retiring a corpus node under
`launchpad/docs/corpus/` does the moment it hits genuine ambiguity partway through the
task -- an unclear requirement, a subject that could plausibly carry more than one
`type`, or a source readable more than one way -- rather than silently picking a
reading and continuing. The working principle across this whole corpus program is one
sentence: **ambiguity is surfaced, not resolved.** This node is the concrete sequence
that principle becomes in practice, for corpus-node authoring specifically; it does not
restate the substantive rule each branch below defers to, only the recognition step and
the order of action.

## Before you start

- You are already inside `AGENTS.md`'s create/update/retire procedure, or a
  batch-authoring run of `corpus-plan`/`corpus-batch-author`, and something in front of
  you does not resolve cleanly no matter how you read it.
- You have this node's *See also* links within reach: `standards/taxonomy.md`,
  `standards/atomicity.md`, `standards/decision-references.md`, `ADR-0029`, and
  `agents/invariants.md`. Several branches below hand you to one of them rather than
  re-deriving its rule here.

## Recognize genuine ambiguity, before choosing a branch

1. **Confirm you actually opened the source, rather than recalling what it probably
   says.** `AGENTS.md`'s own worked failure is exactly this shortcut: "there was
   nothing to point at" was true when the corpus held one node and stopped being true
   the moment a second one merged, and two independent agents copied an earlier
   version of that sentence into their own nodes as if it were a standing rule rather
   than a fact about one moment. A claim of absence needs the enumeration
   (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`) run again,
   not remembered from the last time it was true.
2. **Confirm the reading you are about to build on is actually right, not merely
   plausible.** `AGENTS.md` names a second worked failure of skipping this: an earlier
   version of its own citation-shapes table claimed to summarize a cited section's six
   shapes when it in fact listed seven, and an agent built a scope argument on that
   miscount before their plan review caught it. Re-count, re-read, re-run the command
   — do not build the next step on an unverified premise, even one that looks settled.
3. **If, having actually checked, one reading survives** — the source says one thing,
   the requirement resolves against the current schema, the subject fits one `type`
   cleanly — this procedure does not apply. Resolve it and continue the task you were
   already doing; over-invoking an escalation procedure for an ambiguity that dissolved
   under inspection is its own form of not doing the work.
4. **If two readings both survive that check, or two authoritative sources disagree, or
   nothing already documented covers the case** — this is genuine ambiguity. Go to the
   branch below that matches what kind it is.

## A. The requirement or Definition-of-Done text is unclear

1. Check whether the issue's checklist resolves cleanly against the current schema and
   `AGENTS.md`, and — where the task is part of a Feature — against that Feature's own
   stated acceptance criteria, not only the issue's own copied checklist text.
2. If it does not resolve cleanly, stop. Do not guess between two readings and proceed
   on the one that seems more likely. `.claude/skills/corpus-plan/SKILL.md`'s own "Stop
   on ambiguous scope" section states this for planning-time ambiguity — a parent
   Feature that doesn't obviously match its subject, two rows describing what looks
   like the same document, a misspelled blocker alias — and is explicit that none of
   these is the tooling's job to catch, because its validation is structural, not
   semantic. `.claude/skills/corpus-batch-author/SKILL.md` states the same discipline
   for build-time ambiguity: an issue whose checklist does not resolve cleanly is
   reported, not guessed at, per what it names as the underlying rule from
   `plan-issue` — "ambiguity in the issue is surfaced, not resolved. State both
   readings and ask. Picking one silently is how an agent builds the wrong thing
   confidently."
3. State both readings explicitly, in the plan or in the node's own body. If the
   governing Feature's acceptance criteria already resolve the tension (as they did for
   this node — see the evidence ledger above), build against that and say so instead of
   the issue's own copied checklist tail. If they do not, escalate per *Escalating what
   nothing existing covers*, below, rather than picking silently.

## B. The subject could plausibly carry more than one `type`

1. Apply `standards/taxonomy.md`'s own choosing-a-value test: when more than one of the
   13 enum values plausibly fits, follow how the corpus has actually used the enum, not
   what the label could technically stretch to cover. That document's own worked data
   points — `governance` for corpus-process/policy nodes, `agent` for a node written as
   an agent harness's own instructions — are precedent, not a rule with the force of the
   schema; read them as such rather than mechanically pattern-matching.
2. If the fit is still imperfect after that test, do not silently pick. Say so in this
   node's own *Scope and omissions* section, name the reason, and mark the choice as a
   candidate for revision later — exactly as `corpus-readme.md` does for its own `type`
   choice, per `standards/taxonomy.md`'s step 4. A node's `type` may be revised later;
   its `id` must not, so the disclosure costs nothing durable and leaves a trail for the
   choice to be revisited.
3. Check whether the ambiguity is actually about node *count*, not `type`. If the
   subject genuinely spans two surfaces rather than merely two plausible labels for one
   surface, `standards/taxonomy.md`'s own step 1 hands that off explicitly:
   `AGENTS.md`'s one-node-one-idea rule, elaborated in full by `standards/atomicity.md`,
   governs a split, not the type-choice test. Re-run `standards/atomicity.md`'s own
   five-test decision procedure rather than trying to resolve a node-count question by
   picking harder at the `type` enum.

## C. A source is readable two ways, or two authoritative sources disagree

1. First distinguish which situation this actually is: thin evidence (only one source
   exists and it is hard to classify), or a genuine contradiction (two sources with
   authority over the *same* claim type say different things). They get different
   responses, below.
2. **Thin evidence — classify honestly, do not force `FACT`.** `AGENTS.md` names its
   own worked failure of this: an earlier draft of its evidence-classification guidance
   left the case of an issue/PR/discussion-only source with no honest class at all,
   which an agent authoring a sibling node hit directly, before the guidance was fixed
   to name `TEAM_KNOWLEDGE` with `provided_by` as the honest choice. If the only source
   is a comment, an issue, a PR review, or a discussion, that is `TEAM_KNOWLEDGE`,
   attributed — not a `FACT` resting on an `UNVERIFIED`-shape citation, and not an
   `INFERENCE` dressed up with a `confidence` number to avoid admitting it is
   uncorroborated.
3. **Genuine same-claim-type contradiction — do not pick a side.** `ADR-0029` resolves
   the ordinary case (different claim types, each with its own tiebreaker) but is
   explicit that it does not resolve two sources of authority over the *same* claim
   type disagreeing — there, the corpus author stops and records the contradiction.
   `standards/decision-references.md` fixes the concrete behaviour into four steps: one
   evidence entry per contradicting record, each citing its own source; state the
   contradiction in the body, naming both records; set the node's `status` to
   `flagged`; and escalate via a `type:adr` issue parented to the PRD that raised it,
   with the decision outcome left blank. Do all four — a `flagged` status alone, with
   no linked escalation issue, is the exact gap `standards/review-requirements.md`'s
   MUST 8 tells a reviewer to catch, not a stopping point on its own.
4. **Never resolve step 3's contradiction yourself, however confident the reading.**
   `launchpad/AGENTS.md` section 5's Rule 1 states plainly that an agent decides an ADR
   outcome only on a human's behalf, never on its own judgement. Picking between two
   accepted records is making a decision, not documenting one.

## Escalating what nothing existing covers

Some ambiguity survives every branch above because nothing in the corpus's own rules
already answers it — not a mis-fitting `type`, not a contradiction between two accepted
records, just a genuine gap. Do not invent an answer to fill it.

1. **Name the gap precisely** — the invariant, rule, or classification that seemed to
   be missing, and why the existing schema, `AGENTS.md`, standards, or templates did not
   already cover it. `agents/invariants.md`'s own *Exceptions and escalation* section
   states this pattern for its own ten invariants: a case none of them covers is
   escalated by raising an issue against the governing Feature or PRD, not invented on
   the spot.
2. **File the issue against the Feature or PRD that governs the work in front of you**
   — for a corpus-authoring gap discovered while working a Feature #620 child task,
   that is #620 itself; for a gap discovered elsewhere, the Feature or PRD actually
   governing that work. `launchpad/AGENTS.md` section 5's Rule 2 states the same
   discipline at the repository's top level for a different ambiguity (issue type):
   file a Task, label it, say so in the Objective, and never guess silently, because
   guessing hides an approval gate rather than closing it.
3. **Record the gap in the node itself, not only in the filed issue.** A reader
   arriving at this node later needs to see the open question without cross-referencing
   GitHub — put it in *Scope and omissions*' "expected but not verified" list, per
   `AGENTS.md`'s own step 3 for what that section is for.
4. **Draft; never decide.** Whatever the escalation resolves to — a schema change, a new
   ADR, a corrected standard — an agent may draft the recommendation in full.
   `launchpad/AGENTS.md` section 5's Rule 1 withholds the decision itself for a human,
   the same constraint `standards/decision-references.md` names specifically for
   clearing a `flagged` contradiction in branch C above.

## See also

- `launchpad/docs/corpus/AGENTS.md` — the create/update/retire procedure this node's
  branches interrupt, and the source of the three worked failures in *Recognize genuine
  ambiguity* above.
- `launchpad/docs/corpus/standards/taxonomy.md` — the full `type`-choice decision
  procedure branch B hands off to.
- `launchpad/docs/corpus/standards/atomicity.md` — the full node-count decision
  procedure branch B's step 3 hands off to.
- `launchpad/docs/corpus/standards/decision-references.md` and
  `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` — the full
  evidence-conflict escalation mechanics branch C hands off to.
- `launchpad/docs/corpus/agents/invariants.md` — the MUST/SHOULD invariants (I2, I7,
  Q4) this node's branches act out as ordered steps rather than restate as rules.
- `launchpad/docs/corpus/standards/review-requirements.md` — what a reviewer checks
  once this node's branch C has run, particularly MUST 8.

## Boundary

This node does not describe:

- **Facts to look up rather than actions to perform.** There is no dedicated
  reference-shaped corpus node for corpus-authoring lookup content as of this writing;
  where one exists for a specific field or enum (for example `node.schema.json` for the
  front-matter contract itself), this node points to it inline rather than inlining the
  lookup content here.
- **The full `type`-choice test itself.** `standards/taxonomy.md` owns the five-step
  procedure branch B applies; this node only states when to invoke it and what to do
  if it still leaves the fit imperfect.
- **The full node-count (one-idea-per-node) test itself.** `standards/atomicity.md`
  owns the five-test decision procedure and its six boundary cases; this node only
  states when a `type` ambiguity turns out to be a node-count ambiguity in disguise.
- **The full evidence-conflict escalation mechanics.** `ADR-0029` and
  `standards/decision-references.md` own the substantive rule (contextual precedence,
  the four-step author behaviour, the `type:adr` issue route); this node only states
  the recognition step (thin evidence versus genuine contradiction) and points to them.
- **How to acquire the underlying skill of authoring a corpus node from scratch, for a
  newcomer.** That is a tutorial, which has no corpus template as of this writing
  (`templates/procedure.md` names the same gap and the issue tracking it).
- **Why any of the referenced rules exist, beyond the one-line reason given inline.**
  See the linked node for its own reasoning, rather than a second copy of it here.
- **An operational alert or failure condition.** This node is deliberately built from
  `templates/procedure.md` rather than `templates/runbook.md` — see the evidence entry
  above for why an ambiguity encountered mid-authoring is a chosen task's decision
  point, not an already-firing alert with a severity/impact profile and an alerting-rule
  trigger.

## Relationships

- **`depends-on: corpus-agents`.** This node's own authority to interrupt the
  create/update/retire procedure is derived from that procedure, not original to
  itself, the same relationship `agents/invariants.md` already declares toward the same
  target for the same reason.
- **`references: corpus-standard-taxonomy`, `corpus-standard-atomicity`,
  `corpus-standard-decision-references`, `corpus-standard-review-requirements`.** Each
  is a substantive procedure this node's branches or *See also* section cite and hand
  off to rather than restate — the fourth is MUST 8, the reviewer-side counterpart to
  branch C's escalation steps — cited as supporting context per
  `relationships.schema.json`'s own directionality for `references`: this node's claims
  do not depend on any of the four staying byte-identical, only on their existing and
  covering the subject named.
- **`references: agents-invariants`.** The sibling `agents/*.md` node whose I2, I7 and
  Q4 state the MUST/SHOULD obligations this node's branches carry out as ordered steps;
  a loose coupling for the same reason as the standards above, not a currency
  dependency. This is also the one sibling task under parent Feature #620 that is
  merged at this node's authoring time (issue #649) — the point made explicitly here
  because it is easy to misstate as "no Feature #620 sibling is merged yet," which
  would be false the moment this edge exists.
- **`implements: corpus-template-procedure`.** This node is a how-to-shaped instance of
  that template, per `relationships.schema.json`'s own worked example for `implements`
  — "source is the concrete realization of target (e.g. a template instance of a
  standard)."
- **All seven targets were checked against `origin/launchpad`**
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), not this
  worktree, per `AGENTS.md`'s own node-creation step 9 — all seven resolve there. No
  edge was declared toward any *unmerged* task under parent Feature #620 — the other 30
  `agents/*.md`/`ingestion/*.md` siblings besides `agents-invariants` — because none of
  those 30 is merged at this node's authoring time.

## Scope and omissions

**This node covers** the recognition step for genuine ambiguity encountered while
authoring, updating, or retiring a corpus node (versus a reading that only looked
uncertain until actually checked); three named branches for the ambiguity kinds this
task's brief named explicitly (unclear requirement, plausible dual `type`, source
readable two ways); and the general escalate-rather-than-invent pattern for a gap none
of the corpus's existing rules already covers.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full `type`-choice decision procedure | `launchpad/docs/corpus/standards/taxonomy.md` |
| The full node-count (one-idea-per-node) decision procedure | `launchpad/docs/corpus/standards/atomicity.md` |
| The full evidence-conflict / `flagged`-clearing mechanics | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`, `launchpad/docs/corpus/standards/decision-references.md` |
| What a reviewer specifically checks once a node reaches `flagged` or cites a contested decision | `launchpad/docs/corpus/standards/review-requirements.md` |
| Creating, updating and retiring a node procedurally in general | `launchpad/docs/corpus/AGENTS.md` |
| Ambiguity encountered in manifest planning specifically (before a Task issue exists) | `.claude/skills/corpus-plan/SKILL.md`'s "Stop on ambiguous scope" |
| A tutorial-form treatment of corpus authoring for a newcomer | No corpus template exists for the Tutorial form as of this writing, per `templates/procedure.md`'s own note |

**No `type: template` or `type: policy` distinction is made in this node's front
matter.** `node.schema.json`'s `type` enum names the corpus surface a node documents,
not the documentation form its prose takes — this node's body takes the how-to form
while carrying `type: agent`, the same distinction `templates/procedure.md`'s own "A
note on `type`" section states for any node built from it.

**Expected but not verified when this node was written:**

- **No corpus node has yet been authored by following this procedure end to end from
  a live ambiguity.** Every branch above is derived from the sources it hands off to
  (`AGENTS.md`'s worked failures, `standards/taxonomy.md`, `standards/atomicity.md`,
  `ADR-0029`, `standards/decision-references.md`, `launchpad/AGENTS.md` section 5) and
  from this task's own authoring experience choosing `type: agent` and the procedure
  template (documented in the evidence ledger above as the two INFERENCE entries), not
  from having been the resolution path for a separate, later ambiguity.
- **Whether any *unmerged* sibling `agents/*.md` or `ingestion/*.md` node, once drafted,
  will declare a relationship toward this node** is that sibling's own edit to make, not
  something decided here — 30 of the 31 siblings under parent Feature #620 are unmerged
  at this node's authoring time. The 31st, `agents-invariants` (#649), is already merged
  and already targeted by this node's own `references` edge above.
- **Whether the three branches (A, B, C) exhaust every kind of authoring-time ambiguity
  a corpus author can hit**, or whether a fourth kind exists that this node's three
  named examples did not anticipate, was not audited against a corpus of real
  authoring sessions -- only against the sources this node already cites and the
  specific three examples this task's own brief named.
