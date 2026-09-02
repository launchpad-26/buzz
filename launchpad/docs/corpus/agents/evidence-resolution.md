---
id: agents-evidence-resolution
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
  - statement: "CONTRACT.md section 3 enumerates six citation shapes -- file range, file line, bare path, graph edge, tool result, commit -- and states that a consumer parsing an evidence entry must handle all six, that three of the six are openable (file range, file line, bare path) and three are not (graph edge, tool result, commit), and that the openable bare-path form 'resolves to a whole file rather than to the lines the claim is about.'"
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "AGENTS.md states that CONTRACT.md section 3 has zero occurrences of the string 'http', that its own citation-shape table therefore adds two URL forms section 3 does not enumerate (a pinned GitHub file link, and an external non-GitHub URL), and that the resulting table is seven rows rather than a summary of section 3 -- and separately records that an earlier draft's claim that it *was* a summary led an agent authoring a sibling node to build a scope argument on the miscount."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "node.schema.json's evidence-entry schema requires every entry to carry statement and entry_class, and its allOf conditionals require FACT to carry evidence and forbid confidence and provided_by, require INFERENCE to carry evidence and confidence and forbid provided_by, and require TEAM_KNOWLEDGE to carry provided_by and forbid confidence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "standards/evidence.md's 'Three outcomes, not two' section states that when cited sources compel a claim the class is INFERENCE rated per the confidence standard, that when the sources leave the choice open and a real person, issue or record made it the class is TEAM_KNOWLEDGE naming that source, and that when the sources leave the choice open and there is nobody to name because the author made the choice while writing, the honest response is to withdraw the claim as a named gap rather than relabel it into a class that looks derived."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "standards/evidence.md's 'The test' subsection states the question a FACT or INFERENCE citation must be read against is 'Does the cited source say this, or does it merely concern this?', and that a source discussing the subject while saying nothing about the specific thing asserted is the tell to read for adversarially."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "standards/evidence.md's citation-verdict table reports commit references, graph edges, tool results, and any URL its repository-link pattern does not match (including GitHub issue and pull-request URLs and every non-GitHub URL) as unverified -- establishing nothing, not even that a commit id has ever existed in the repository -- while a well-formed pinned repository link is reported ok on shape alone with nothing fetched, and states plainly that 'a FACT resting only on UNVERIFIED citations has been checked by nothing at all.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "AGENTS.md's 'Nothing enforces this' subsection states that validate.py treats every commit citation identically, so a second, third or tenth FACT resting only on a commit citation produces nothing but further non-fatal UNVERIFIED notices and the run still exits 0 -- a convention a reviewer must hold, because no check will raise it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's 'When the only source is an issue, a PR or a discussion' subsection states that such a source has no openable file and no way to pin one, that forcing it into a FACT on a tool-result or URL citation is wrong, and that TEAM_KNOWLEDGE with provided_by naming the issue is the correct class -- because ADR-0029 requires GitHub history to stay attributed rather than promoted to fact."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "standards/evidence.md states that its 'forms that name no openable file' half -- commit, graph edge, tool result, and any URL its repository-link pattern cannot open -- is the node's own authoritative subject, while the forms that name code -- a bare repository path, a path:line position, and a well-formed pinned GitHub link (itself a URL, but one the pattern can open) -- are allocated to the not-yet-merged code-references standard (#1308), so a node written today still reads AGENTS.md's own table for that code-naming half until #1308 lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "templates/procedure.md requires a node built from it to carry, in its body, an Overview, an optional Before you start, one numbered task sequence per logical goal with action-verb steps, a See also section, an explicit Boundary statement, a Relationships section, and a Scope and omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "node.schema.json's type enum has thirteen members including agent, and AGENTS.md and agents-invariants both carry type: agent as the corpus surface for documents about agent authoring behavior -- the same surface this node's subject (an agent's own claim-classification and citation behavior while authoring) belongs to."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "relationships.schema.json defines depends-on, references and implements among its five relationship types, giving implements the worked example 'source is the concrete realization of target (e.g. a template instance of a standard)' and references the directionality 'source cites target as supporting context; no ownership or currency dependency implied.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, corpus-agents, corpus-standard-evidence, agents-invariants and corpus-template-procedure are all present on origin/launchpad's corpus tree, and none of this task's 31 unmerged sibling agents/*.md or ingestion/*.md document tasks under Feature #620 (including #643) are."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/**, capabilities/**, development/**, layers/**, schema/** (excluded from validation), standards/** (includes standards/evidence.md), templates/** present; no other file under agents/ or ingestion/ present, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "A sibling task, #643 (agents/conflicting-evidence.md), is drafted on local branch task/643-agents-conflicting-evidence and covers what to do when two authoritative sources of the same claim type contradict each other, routing the general case to standards/evidence.md's MUST 10 and the two-decision-record case to standards/decision-references.md -- a distinct subject from this node's single-source classification and citation procedure. It is read here for boundary-drawing only; it is not a valid relationships target because it is unmerged."
    entry_class: FACT
    evidence:
      - "read(file='/home/serina/Launchpad/buzz/__worktrees/task-643-agents-conflicting-evidence/launchpad/docs/corpus/agents/conflicting-evidence.md') -> id agents-conflicting-evidence, status draft, body sections Overview/Before you start/Recognize the conflict then route it/See also/Boundary/Relationships/Scope and omissions, commit 0a95ed834 and 52b8c567b on branch task/643-agents-conflicting-evidence"
  - statement: "Parent Feature #620 lists #648 among 32 child document tasks under an agents/ and ingestion/ path family with the stated outcome that 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures', and its acceptance criteria require that no broad overview page duplicate canonical claims owned by atomic child nodes and that an independent reader be able to traverse from a node to implementation/verification evidence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body and acceptance criteria"
  - statement: "Issue #648's own Definition of Done requires this node to state goal, prerequisites and allowed scope, provide ordered executable steps, define success verification and rollback/cleanup where relevant, and link authoritative commands/config rather than giving generic advice -- a how-to-shaped Definition of Done, distinct from the standards-track boilerplate copied across several sibling tasks in this same batch."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#648 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-evidence
  - type: references
    target: agents-invariants
  - type: implements
    target: corpus-template-procedure
---

# Evidence resolution: how-to

How to take one candidate claim, at the moment of drafting or updating a corpus node,
from "I believe this" to a correctly classified, correctly cited entry in the node's
`evidence` ledger -- recognizing the claim's type, finding and opening the best
available source, choosing `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` honestly, citing it in a
shape the validator recognizes, and catching the `UNVERIFIED` trap before it ships as an
unchecked `FACT`.

## Before you start

- You already know the `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` contract and which further
  fields the schema requires or forbids for each -- see `corpus-standard-evidence` if
  not; it is not re-derived here.
- You have one statement you intend to add to a node's body and its `evidence` ledger.
  If you are not sure it is one statement, split it first -- a compound claim resting
  half on code and half on a conversation cannot be classified honestly as one entry.
- **This procedure assumes a single candidate source, or several sources that agree.**
  If two sources you are citing for the same claim appear to disagree, stop here and go
  to `agents-conflicting-evidence` instead -- that is a different procedure with its own
  routing, not a variant of this one.

## Resolve one claim to a cited, classified entry

1. **Name the claim type.** Decide whether the statement describes how the system
   **currently behaves** (code, configuration, schema, a passing test) or what was
   **intended or authorized** (an accepted decision, a ratified specification).
   `corpus-standard-evidence`'s "When sources disagree" section is the authority for
   which kind of source outranks which for each type; this step only asks you to name
   the type before you go looking, since picking the wrong one and then searching is how
   an author ends up citing documentation for a behavior claim.
2. **Find a candidate source for that claim type**, and open it. Not "a source exists
   that probably says so" -- opened, at the revision this node's ledger records.
3. **Apply the test before choosing a class**: does the source you opened *say* the
   statement, or does it merely *concern* the same subject? `corpus-standard-evidence`'s
   "The test" subsection is the authority for this question and states the tell to read
   for: a source that discusses the subject while saying nothing about the specific
   thing asserted will feel like support because it is relevant, and relevance is not
   entailment.
4. **Classify against the three outcomes, in order, and stop at the first that
   genuinely applies:**
   - The source you opened states the claim directly -> `FACT`. You must have opened
     it; "the sort of thing that file would say" is not sufficient.
   - The sources compel the claim by reasoning, without stating it directly ->
     `INFERENCE`, rated for strength per the confidence standard (a different
     document's subject, linked below, not this one's).
   - The sources leave the choice open, and a real person, issue, pull request, decision
     record or commit message made it -> `TEAM_KNOWLEDGE`, with `provided_by` naming
     that source by name. Attributing your own extrapolation to the thing it started
     from does not count -- `AGENTS.md` and `corpus-standard-evidence` both name this
     failure directly.
   - The sources leave the choice open and there is nobody to name, because you made
     the call while writing -> **withdraw the claim.** Move it to the node's Scope and
     omissions section as a named gap instead of forcing a label onto it. A gap sends a
     reader to find out; a misclassified claim invites them to rely on it.
5. **Cite the source in a shape the validator recognizes.** `CONTRACT.md` §3 names six
   shapes; `AGENTS.md`'s own table adds two URL forms the validator also accepts. Which
   of the eight are checked against the repository at all, and what each verdict does
   and does not establish, is `corpus-standard-evidence`'s canonical table -- read it
   there rather than from a copy here, since a copy is exactly what goes stale first.
6. **Recognize the `UNVERIFIED` trap before you finish.** Several of the eight shapes
   -- notably a commit reference, a graph edge, and a tool result -- are reported
   `UNVERIFIED`: printed, never fatal, and establishing nothing the checker can stand
   behind. If every citation behind a `FACT` resolves this way, the entry has been
   checked by nothing wearing the strongest available label. Two exits: open a source
   that resolves (return to step 2), or reclassify honestly per step 4. One narrow,
   named exception exists for the ledger's own provenance entry recording the node's
   revision -- see `corpus-standard-evidence` for exactly which case that is and why.
7. **When the only available source is an issue, a pull request, or a conversation**,
   do not force it into a `FACT` on a tool-result or URL citation to make it look
   checked. Use `TEAM_KNOWLEDGE` with `provided_by` naming the issue or pull request
   directly -- that is what the class exists for.
8. **Write the entry into the ledger, and the corresponding statement into the node's
   body, in the same edit.** Nothing checks either direction: the validator discards a
   node's body before any check runs, so a body claim with no ledger entry and a ledger
   entry supporting no body claim are both invisible to every automated check that
   exists. Check both directions yourself before moving to the next claim.
9. **Run the validator** (`python3 launchpad/project-intelligence/corpus/validate.py`
   from the repository root) once every claim in the node has an entry. A hard error
   names a citation shape it could not recognize or a path that does not resolve; an
   `UNVERIFIED` notice on a `FACT` is not itself an error, but per step 6 it is a signal
   to go back and check.

## See also

- `corpus-standard-evidence` -- the full contract this procedure operationalizes: what
  each class is *for*, the complete citation-verdict table, and the rule for when two
  sources of the same claim type disagree.
- `agents-invariants` -- the schema-enforceable half of the same rules (I6, I7) stated
  as short, citable invariants rather than as a walkthrough.
- `agents-conflicting-evidence` -- the companion procedure for when two authoritative
  sources you are citing for the same claim appear to disagree; this node assumes they
  do not, per *Before you start* above.
- `launchpad/docs/corpus/schema/node.schema.json` -- the field-combination rules each
  class requires and forbids, enforced mechanically.
- `launchpad/project-intelligence/CONTRACT.md` §3 -- the six citation shapes as
  vocabulary, before `AGENTS.md`'s two additional URL forms.

## Boundary

This node does not describe:

- **What to do when two sources you are citing disagree with each other.** That is
  `agents-conflicting-evidence`'s subject -- a distinct procedure this node routes to
  at *Before you start* rather than folding in.
- **What each evidence class means, or the schema's field-combination rules in full.**
  See `corpus-standard-evidence`; this node assumes that contract and only sequences
  the moment-of-authoring decision it produces.
- **How to choose an `INFERENCE`'s `confidence` value.** A different subject (the
  confidence standard), unrelated to whether a claim is honestly an `INFERENCE` at all.
- **The citation forms that name code specifically -- how a bare path, a `path:line`
  position, or a pinned GitHub link is pinned and resolved.** `corpus-standard-evidence`
  states that half is allocated to the not-yet-merged code-references standard (#1308);
  until it lands, `AGENTS.md`'s own table is the source for that half, and step 5 above
  links there rather than restating its resolution rules.
- **Creating, updating or retiring a corpus node procedurally, beyond the evidence
  ledger.** See `AGENTS.md`.
- **Why ADR-0029 settled on contextual precedence with escalation, rather than a fixed
  hierarchy.** That reasoning belongs to the ADR itself, not to a how-to about the
  ordinary single-source case.

## Relationships

- `depends-on: corpus-agents` -- this procedure's authority to exist as a corpus node,
  and its own creation and evidence rules, derive from `AGENTS.md`, not original to
  itself.
- `references: corpus-standard-evidence` -- the general evidence contract (class
  definitions, the full citation-verdict table, the disagreement rule) this procedure
  sequences into an ordered set of actions.
- `references: agents-invariants` -- the same rules' schema-enforceable invariants
  (I6, I7), stated as short citable ids rather than walked through step by step.
- `implements: corpus-template-procedure` -- this node is a how-to-shaped instance of
  that template.

All four targets were checked against `origin/launchpad`'s corpus tree at the recorded
revision (see the `git_ls_tree` evidence entry above), not against this worktree. No
edge is declared toward `agents-conflicting-evidence` (#643): it is drafted locally but
unmerged at this node's authoring time, so a `relationships` target naming it would
validate on this branch and become a hard error once merged onto `origin/launchpad`
before #643 lands, per `AGENTS.md`'s own step 9 warning. That edge is a follow-up once
#643 merges, not an oversight now.

## Scope and omissions

**This node covers** the moment-of-authoring sequence an agent follows for one
candidate claim: naming its claim type, finding and opening a source, applying the
"say this or merely concern this" test, classifying honestly against the three
possible outcomes (including withdrawal when none apply), citing it in a recognized
shape, recognizing when a citation resolves to nothing but `UNVERIFIED` notices, and
keeping the ledger and body in sync.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What each evidence class means, and the schema's field-combination rules | `corpus-standard-evidence` |
| How to choose an `INFERENCE`'s `confidence` value | the confidence standard (`launchpad/docs/corpus/standards/confidence.md`) |
| What to do when two sources of the same claim type disagree | `agents-conflicting-evidence` |
| The two-decision-record conflict recipe specifically | `standards/decision-references.md` |
| The citation forms that name code, and how each is pinned and resolved | `AGENTS.md`'s table until the code-references standard (#1308) lands |
| Creating, updating and retiring a corpus node procedurally | `AGENTS.md` |
| `ADR-0029`'s own decision, context and consequences | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| Other agent-facing authoring procedures (ambiguity handling, documentation creation/update/validation, concept resolution, change-impact analysis, repository navigation, stale-documentation handling, corpus usage) | the remaining sibling tasks under parent Feature #620, none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **No node anywhere has been drafted end-to-end using this procedure and then
  reviewed against it**, so whether the nine-step sequence above is complete in
  practice, rather than only on paper, is untested.
- **Whether a future `agents/*.md` or `ingestion/*.md` sibling will declare a
  relationship toward this node** is that sibling's own edit to make, not decided
  here.
- **This node's own ledger entries recording what exists on `origin/launchpad` and
  what `agents-conflicting-evidence` contains are each classified `FACT` resting on a
  single tool-result citation** (a `git_ls_tree` call, and a direct file read), which
  `validate.py` can only ever report `UNVERIFIED` -- the same shape of tension step 6
  above warns about, but for a claim type (a tool observation the author performed
  directly) the "one permitted exception" in `corpus-standard-evidence` names only for
  the revision-recording entry specifically. This node follows the same precedent
  already set by `corpus-template-procedure`, whose own ledger classifies an identical
  `git_ls_tree`-only claim as `FACT`, rather than resolving the tension itself.
  `agents-invariants` was checked for the same pattern and does not carry one -- its
  merge-target claim (I5) cites `AGENTS.md` directly rather than a tool result -- so
  this precedent rests on one sibling node, not two.
