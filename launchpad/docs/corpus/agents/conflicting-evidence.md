---
id: agents-conflicting-evidence
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
  - statement: "ADR-0029 ranks evidence contextually by claim type -- executable evidence is authoritative for claims about how the system currently behaves, and accepted normative decisions are authoritative for claims about intended or authorized behavior -- and requires that two sources with authority over the same claim type that contradict each other are not silently resolved; the affected node stays unestablished/flagged until a human resolves it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "ADR-0029's security implications state that repository and GitHub text remain untrusted evidence for ranking purposes only, that private evidence must not be copied into the public corpus to resolve a conflict, and that where evidence cannot be published the claim stays unestablished rather than asserted from a source that cannot be shown."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "node.schema.json's status enum includes flagged, described there as ADR-0029's 'unestablished/flagged' state naming an unresolved conflict between authoritative sources rather than simple low confidence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "corpus-standard-evidence's MUST 10 requires that two authorities of the same claim type in conflict leave the node status: flagged for a human rather than being resolved by its author, and its 'When sources disagree' section states that a real conflict is escalated, not resolved: record the contradiction, set status to flagged, and leave it for a human."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "corpus-standard-evidence's 'Three outcomes, not two' section states that when a claim's sources leave a choice open and there is nobody to name because the author made the choice while writing, the honest response is to withdraw the claim as a named gap in scope-and-omissions, not to relabel it into a class that looks derived."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "corpus-standard-decision-references's MUST 6 and its 'When two accepted decisions conflict' section give a four-step author recipe specific to two accepted decision records of the same claim type contradicting each other: one evidence entry per contradicting record, state the contradiction in the body, set status to flagged, and escalate via a type:adr issue parented to the PRD that raised it, with the decision outcome left blank because agents draft decisions and do not make them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "agents-invariants's Q4 already states, as a SHOULD, that an author who finds two authoritative sources of the same claim type in conflict should stop and record the conflict rather than resolving it themselves, per ADR-0029, and should set status: flagged when the conflict touches a claim central to the node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "agents-invariants's own scope-and-omissions table lists 'Concrete agent procedures for ambiguity handling, evidence resolution, documentation creation/update/validation, concept resolution, change-impact analysis, repository navigation, stale-documentation handling and corpus usage' as owed to sibling tasks under parent Feature #620 including #643, naming this task's subject a procedure rather than a second policy statement."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "corpus-template-procedure requires a node built from it to carry, in its body, an Overview, an optional Before you start, one numbered task sequence per logical goal with action-verb steps (permitting branches when a task genuinely forks), a See also section, an explicit Boundary statement, a Relationships section, and a Scope and omissions section, and states that a node's type tracks the corpus surface its subject matter belongs to rather than its documentation form."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "node.schema.json's type enum has thirteen members and includes agent; corpus-agents (AGENTS.md) and agents-invariants both carry type: agent as the corpus surface for documents about agent authoring behavior, which this node's subject -- an agent's own conflict-handling behavior while authoring a node -- belongs to as well."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "relationships.schema.json defines references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied', and implements' directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, corpus-agents, corpus-standard-evidence, corpus-standard-decision-references, agents-invariants and corpus-template-procedure are all present on origin/launchpad's corpus tree, and none of this task's 30 unmerged agents/*.md or ingestion/*.md sibling document tasks under Feature #620 are."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/**, capabilities/**, development/**, layers/**, schema/** (excluded from validation), standards/**, templates/** present; no other file under agents/ or ingestion/ present, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Parent Feature #620 lists #643 among 32 child document tasks under an agents/ and ingestion/ path family with the stated outcome that 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures', and its acceptance criteria require that no broad overview page duplicate canonical claims owned by atomic child nodes."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body and acceptance criteria"
  - statement: "Issue #643's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them -- boilerplate copied mechanically across the batch's document tasks, the same pattern corpus-template-procedure and corpus-template-policy both record independently for their own sibling issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#643 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-evidence
  - type: references
    target: corpus-standard-decision-references
  - type: references
    target: agents-invariants
  - type: implements
    target: corpus-template-procedure
---

# Conflicting evidence: how-to

What to do, in the moment, when two authoritative sources you are citing for the same
corpus claim appear to disagree with each other while you are drafting or updating a
node's evidence ledger.

## Before you start

- You already know the `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` contract and how a citation
  is classified -- see `corpus-standard-evidence` if not.
- You already know `ADR-0029`'s two claim types -- **current behavior** (what the
  system does today) and **intended or authorized behavior** (what was decided) -- each
  with its own tiebreaker.
- You have identified two or more candidate sources that appear to say different things
  about the same statement you are about to write into a node's body.

## Recognize the conflict, then route it

1. **Name the claim type each source is actually answering.** Does it describe how the
   system **currently behaves** (code, config, schema, a passing test), or what was
   **intended or authorized** (an accepted ADR, a ratified specification)?
   `corpus-standard-evidence`'s "When sources disagree" section is the authority for
   this question; it is not re-derived here.
2. **Check whether the two sources are actually answering the same claim type.** This
   step forks into three outcomes -- follow the one that applies:
   - **2a. Different claim types.** A spec states intent and code shows current
     behavior: this is not a same-claim-type conflict at all, and most apparent
     conflicts dissolve exactly here. Write two separate evidence entries, one per
     claim, each classified against its own claim type's own tiebreaker -- executable
     evidence for the behavior entry, the accepted decision for the intent entry.
     Continue authoring normally. No escalation, no `flagged` status.
   - **2b. Same claim type, and both sources are accepted decision records** (two
     ADRs, or an ADR and a ratified specification, both governing the same intent
     claim). Stop here and follow `corpus-standard-decision-references`'s "When two
     accepted decisions conflict" section exactly -- its four-step recipe (one entry
     per record, state the contradiction, `status: flagged`, escalate via a `type:adr`
     issue) is the authority for this specific pairing. Do not improvise a variant of
     it in this node's terms; go there.
   - **2c. Same claim type, and the sources are not both decision records** (for
     example, two executable-behavior sources that disagree with each other, or a
     `TEAM_KNOWLEDGE` attribution that contradicts a `FACT` about the same intent
     claim). This is the general case, and `corpus-standard-evidence`'s MUST 10
     governs it. Continue to step 3.
3. **For the general case (2c): write one evidence entry per contradicting source.**
   Each entry cites its own source and states only what that source says. Do not write
   a third entry stating a resolution -- there is none yet, and inventing one is the
   act ADR-0029 forbids.
4. **State the contradiction explicitly in the node's body**, naming both sources and
   the claim they disagree about, so a reader does not have to reconstruct it from the
   ledger alone.
5. **Set the node's `status` to `flagged`.** This is the schema's dedicated value for
   exactly this state -- an unresolved conflict between authorities -- not a stand-in
   for low confidence or "still drafting."
6. **Before escalating, check whether either source is private or cannot be
   published.** If so, per `ADR-0029`'s security clause, do not copy it into the
   public corpus to settle the conflict. The claim stays unestablished, and that fact
   is itself part of what gets recorded and escalated -- it is not a reason to quietly
   prefer the source you happen to be able to show.
7. **Escalate the way this repository turns an open question into a decision.** Raise
   it, or point to an existing one, as a `type:adr` issue parented to the PRD that
   governs the subject, with the decision outcome left blank. Agents draft decisions;
   they do not make them -- choosing between two same-claim-type authorities is making
   one.
8. **Finish authoring the rest of the node normally.** A `flagged` status on one
   contested claim does not block the rest of the ledger or body from being completed.
   Only the contested claim itself stays unestablished until a human resolves it.

## See also

- `corpus-standard-evidence` -- the general evidence contract, class choice, and the
  full "When sources disagree" rule this procedure routes into at steps 1 and 2c.
- `corpus-standard-decision-references` -- the decision-specific conflict recipe this
  procedure defers to by name at step 2b, rather than restating it.
- `agents-invariants` -- Q4's one-sentence statement of this same rule, and the
  corpus-wide invariants an authoring agent must otherwise hold.
- `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` -- the accepted decision
  this entire procedure operationalizes.

## Boundary

This node does not describe:

- What each evidence class (`FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`) means, or how the
  schema's field rules between them work -- see `corpus-standard-evidence`.
- The four-step recipe for two conflicting decision records specifically -- see
  `corpus-standard-decision-references`; this node routes to it at step 2b rather than
  restating it.
- `ADR-0029`'s own decision text, context, and consequences -- see the ADR itself; this
  node states only the agent-facing procedure it implies.
- The mechanics of the ordinary, non-escalating case at step 2a beyond naming it --
  which claim type wins which tiebreaker is `corpus-standard-evidence`'s subject, not
  re-derived here.
- How to choose an `INFERENCE`'s confidence value -- a different subject (the
  confidence standard), unrelated to whether a conflict exists at all.
- How to acquire the underlying evidence-classification skill from scratch, for a
  newcomer -- a tutorial, which has no corpus template as of this writing.
- Why ADR-0029 settled on contextual precedence with escalation, rather than a fixed
  hierarchy or latest-timestamp-wins -- that reasoning belongs to the ADR, not to a
  how-to about following it.

## Relationships

- `depends-on: corpus-agents` -- this procedure's authority to exist as a corpus node,
  and its own creation/evidence rules, derive from `AGENTS.md`, not original to itself.
- `references: corpus-standard-evidence` -- the general same-claim-type-conflict rule
  (MUST 10) this procedure operationalizes into a routed sequence of actions.
- `references: corpus-standard-decision-references` -- the decision-specific conflict
  recipe step 2b defers to by name rather than restating.
- `references: agents-invariants` -- Q4 already states this rule's one-sentence SHOULD
  form; this node is its expanded how-to.
- `implements: corpus-template-procedure` -- this node is a how-to-shaped instance of
  that template.

All five targets were checked against `origin/launchpad`'s corpus tree at the recorded
revision (see the `git_ls_tree` evidence entry above), not against this worktree.

## Scope and omissions

**This node covers** the moment-of-authoring recognition-and-routing sequence an agent
follows when two sources it is citing for the same corpus claim appear to disagree:
how to tell whether the two are actually answering the same claim type, where to go
when they are two decision records specifically, what to do in the general
same-claim-type case, the security check before escalating, and how to keep authoring
the rest of the node once a claim is flagged.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` contract itself, and the corpus-wide evidence rules | `corpus-standard-evidence` |
| The decision-specific conflict recipe (two ADRs, or an ADR and a ratified specification) | `corpus-standard-decision-references` |
| `ADR-0029`'s own decision, context, and consequences | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| What an `INFERENCE`'s confidence value means and how to choose one | the confidence standard (`launchpad/docs/corpus/standards/confidence.md`) |
| How a specification becomes "ratified" | undefined in this repository, per `corpus-standard-decision-references`'s own scope-and-omissions table |
| Creating, updating and retiring a corpus node procedurally | `AGENTS.md` |
| Other agent-facing authoring procedures (ambiguity handling, documentation creation/update/validation, concept resolution, change-impact analysis, repository navigation, stale-documentation handling, corpus usage) | the remaining sibling tasks under parent Feature #620 (#640-#642, #644-#648, #650-#651), none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **No node anywhere carries the `flagged` status, and no real same-claim-type
  conflict has been worked through end-to-end using this procedure.** Both
  `corpus-standard-evidence` and `corpus-standard-decision-references` record the
  identical caveat for their own conflict-handling sections; this node inherits it
  rather than resolving it.
- **Whether a future `agents/*.md` or `ingestion/*.md` sibling will declare a
  relationship toward this node** is that sibling's own edit to make, not decided
  here.
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
