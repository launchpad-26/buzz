---
id: ingestion-decision-extraction
type: ingestion
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
  - statement: "node.schema.json's type enum includes ingestion among its thirteen members, and describes the field as naming the corpus surface a node documents, not the documentation form its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no ingestion/ directory at all, so this node has no merged sibling under ingestion/ to follow as type precedent; it is the second node planned for that family, after locally-drafted, unmerged ingestion/concept-extraction.md (#955)."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no ingestion/ path present; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "launchpad/decisions/README.md states the decision lifecycle: an open question becomes a type:adr issue parented to the PRD that raised it; the issue is where the decision is argued and its Decision outcome stays blank until a human settles it; when settled, the decision is written to launchpad/decisions/ in the same pull request that closes the issue, because a decision recorded only in a closed issue is lost to the noise."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "A decision record's front-matter status field takes one of at least three values observed across the decisions directory: Accepted (e.g. ADR-0005, ADR-0043), Proposed (e.g. ADR-0034, ADR-0044, ADR-0046), and Superseded by ADR-YYYY (e.g. ADR-0001, superseded by ADR-0050) -- the path alone never distinguishes them, per standards/decision-references.md's own observation that every ADR path looks identical to the structural checker."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md"
      - "launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md"
      - "launchpad/decisions/ADR-0034-knowledge-contract-owned-by-decision-layer.md"
      - "launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md"
  - statement: "ADR-0034-knowledge-contract-owned-by-decision-layer.md carries a ## Decision heading whose own first line reads: 'Not yet settled by a human. This record is Proposed, not Accepted.' -- the section's presence does not mean the question is settled; the front-matter status field is what actually gates it, and this record supplies its own explicit counter-example to reading the heading alone."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0034-knowledge-contract-owned-by-decision-layer.md"
  - statement: "standards/decision-references.md's MUST 4 requires an author to open a cited record and read its front-matter status before citing it for an intent claim, and states that a record which is not accepted MUST NOT be cited as authority for one, because proposed and superseded records live in the same directory under the same filename pattern as accepted ones."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "launchpad/project-intelligence/CONTRACT.md's own header line states of itself: 'Status: proposed, not ratified.'"
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md:3"
  - statement: "standards/decision-references.md's own Scope and omissions table names 'How a specification becomes ratified' as 'Undefined in this repository', immediately after naming CONTRACT.md as the nearest candidate and noting it describes itself as proposed and not ratified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "launchpad-26/buzz#307 carries the type:adr label, is closed, and its issue body's own 'Decision outcome' section reads only: '_Left blank. Agents draft; humans decide (launchpad/AGENTS.md §5.1)._' -- unedited even after the question was later settled."
    entry_class: FACT
    evidence:
      - "gh_issue_view(307, repo='launchpad-26/buzz') -> labels include type:adr; state CLOSED; body's Decision outcome section reads the quoted placeholder text verbatim"
  - statement: "A comment on launchpad-26/buzz#307, posted 2026-08-31 -- six days after an earlier same-day comment on the same issue that itself later turned out to be a placeholder-bug artifact -- states: 'Human decision recorded... Jeffrey (@tucktuck101) reviewed options A-D with their positive and negative consequences, then chose Option A... replying verbatim: \"a\".' The same comment states the issue 'stays open until the single batched ADR PR merges', so the issue's own open/closed state does not confirm settlement either."
    entry_class: FACT
    evidence:
      - "gh_issue_view(307, repo='launchpad-26/buzz', field='comments') -> comment dated 2026-08-31, 'Human decision recorded' heading, quotes Jeffrey's verbatim reply 'a' and names Option A"
  - statement: "launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md carries status: Accepted, issue: launchpad-26/buzz#307, and decided_in: launchpad-26/buzz#307 -- the merged record that actually confirms #307's decision landed, distinct from and later than either comment on the issue itself."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md"
  - statement: "launchpad/AGENTS.md §5.1 reserves choosing between decision options for a human; an agent may write a settled decision's outcome only by quoting the deciding human verbatim and linking where they said it, never on the agent's own judgement -- the shape both the #307 comment and ADR-0034's own 'Proposed, not Accepted' self-description independently follow."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad/AGENTS.md §5.1, as quoted by launchpad/decisions/README.md and by the launchpad-26/buzz#307 comment thread"
  - statement: "Parent Feature #620's acceptance criteria and Feature #618's, #609's, #619's, #617's, #615's, #610's, #616's, #614's, #607's, #613's, #611's, #612's, #608's acceptance criteria all contain the identical boilerplate clause 'explicitly removed from scope by an approved PRD change' (confirmed via a repository-wide issue search), which describes a *kind* of decision a PRD or Feature body can carry but is not itself evidence that such a change has ever actually been approved and executed in this repository; no single already-executed instance was found to cite as a worked example for this branch."
    entry_class: FACT
    evidence:
      - "gh_search_issues(query='approved PRD change', repo='launchpad-26/buzz') -> 14 Feature issues, all sharing identical acceptance-criteria boilerplate, none individually confirming an executed scope change"
  - statement: "Issue #957's own Definition of Done requires that every substantive factual claim be traceable to current code, test, specification, accepted decision, migration/configuration, or attributed GitHub evidence with FACT, INFERENCE and TEAM_KNOWLEDGE not conflated, and that the document state goal, prerequisites, allowed scope, ordered executable project-specific steps, and success verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#957 definition of done"
  - statement: "Parent Feature #620's Out of scope section states: 'Work owned by sibling corpus Features, implementation of the knowledge-crate runtime, and any artifact not required by this Feature outcome or its declared child issues' -- confirming no ingestion pipeline or tool is expected from this node, only agent-facing procedural guidance for a screening step a human or agent performs while reading source material."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Out of scope section"
relationships:
  - type: references
    target: corpus-agents
  - type: implements
    target: corpus-template-procedure
---

# Decision extraction: how-to

Recognize, while reading a source you are already looking at for another reason — an
ADR record, a document claiming to be a specification, a PRD or Feature issue, or a
GitHub issue thread — that a decision worth citing exists there, and screen whether it
has actually been **settled**, before handing it off to `standards/decision-references.md`
for how to cite it.

## Before you start

- Read `standards/decision-references.md` in full. It governs the citation form,
  pinning, and the four-step recipe for conflicting decisions once a settled decision
  is in hand — none of that is restated here. This node is the step before that one:
  recognizing a decision exists at all and is worth screening.
- Know that this is a **noticing-and-screening** step, not the **citing** step, the
  same split `ingestion/concept-extraction.md` (#955, sibling, not yet merged) draws
  for concepts generally against `agents/concept-resolution.md`'s dedup check.
- Read access to `launchpad/decisions/*.md`, `launchpad/decisions/README.md`, `gh
  issue view`/`gh issue list` for the repository, and whichever specification-shaped
  document you were already reading (e.g. `launchpad/project-intelligence/CONTRACT.md`).

## Notice a candidate decision, and screen its status

1. **Notice the trigger.** It arrives while drafting a different claim, not from a
   scheduled search: you are about to state what the system is *intended or
   authorized* to do — an **intent claim**, per `standards/decision-references.md`'s
   own test, "if the code and the decision said different things, which one would a
   reader call the defect?" — or you are reading a document that itself uses
   decision-language (`Decision`, `Accepted`, `Decision outcome`, `ADR`). Stop before
   writing that claim's evidence entry and screen the source first.
2. **Branch by what you are reading.** The four branches below are the source shapes
   this node's own task names; a real one was checked in each during this node's
   authoring, and 2d is stated honestly as untested rather than forced.

   **2a. Reading an ADR file directly (`launchpad/decisions/ADR-*.md`).**
   1. Open the file's front matter and read its `status` field. Do not read only the
      `## Decision` heading and assume the section's presence means the question is
      settled.
   2. **Worked in this session:** `ADR-0034-knowledge-contract-owned-by-decision-layer.md`
      carries a `## Decision` heading whose own first line reads "**Not yet settled by
      a human.** This record is `Proposed`, not `Accepted`." A `Decision` section
      existing is not sufficient; `status: Accepted` is the actual gate, per
      `standards/decision-references.md`'s MUST 4.
   3. Only `status: Accepted` clears the gate for citing as authority for an intent
      claim. `Superseded by ADR-YYYY` (e.g. `ADR-0001`, superseded by `ADR-0050`) needs
      `standards/decision-references.md`'s own re-read-against-the-superseding-record
      procedure, not this node's. `Proposed` (e.g. `ADR-0034`, `ADR-0044`, `ADR-0046`)
      is not yet a decision at all — treat its content as a candidate proposal, never
      as evidence.

   **2b. Reading a document that claims to be a specification.**
   1. Look for the document's own stated ratification status before treating any of
      its sentences as settled.
   2. **Worked in this session:** `launchpad/project-intelligence/CONTRACT.md` states
      of itself, in its own header line, "Status: proposed, not ratified." No document
      in this repository currently defines how a specification becomes "ratified" —
      `standards/decision-references.md`'s own Scope and omissions names this an open,
      undefined gap, not a settled process this node can walk you through.
   3. Absent a defined ratification marker, do not treat a specification's content as
      a settled decision merely because it reads normatively (MUST/SHOULD language, a
      numbered contract) — normative *tone* is not the same as normative *status*.

   **2c. Reading a GitHub issue thread.**
   1. Do not trust the issue body's templated "Decision outcome" section alone. It is
      designed to start blank, and it often *stays* blank even after a human has
      actually decided, because writing the settled answer back into that field is
      optional and separate from the decision itself happening.
   2. **Worked in this session:** `launchpad-26/buzz#307`'s body Decision outcome
      section reads only "_Left blank. Agents draft; humans decide (`launchpad/AGENTS.md`
      §5.1)._" — unedited, even after the question was settled. The actual decision
      surfaced days later, in a comment: "Human decision recorded — 2026-08-31...
      Jeffrey (@tucktuck101) reviewed options A–D... then chose Option A... replying
      verbatim: 'a'." The issue itself **stayed open** after that comment, pending a
      separate batched ADR pull request — so neither the body's placeholder nor the
      issue's open/closed state tells you what actually happened.
   3. Read the issue's **comments**, not only its body, for one naming a human's
      explicit decision and quoting them verbatim — the shape `launchpad/AGENTS.md`
      §5.1 requires of an agent recording someone else's decision.
   4. Confirm the decision actually landed: check whether a matching ADR file now
      exists under `launchpad/decisions/` naming this issue in its `issue`/`decided_in`
      front matter. Here, `ADR-0043-prefer-fork-owned-overrides.md` names
      `issue: launchpad-26/buzz#307`, `status: Accepted`. Until that file exists on
      the branch you are checking against, treat the decision as still in flight,
      however confident a comment reads.

   **2d. Reading a PRD or Feature issue body.**
   1. A PRD's or Feature's body is itself a proposal — its acceptance criteria and
      scope statements describe what is being asked for, not something already
      decided merely by existing in a tracked issue.
   2. A scope change inside one only becomes a decision once it was actually approved
      and reflected back into that same tracked issue. Noticing the boilerplate phrase
      "approved PRD change" — present, word for word, across all fourteen sibling
      corpus Feature issues including this node's own parent #620 — is not evidence
      that such an approval ever occurred; check for a specific, dated approval, not
      the clause itself. This branch is stated here as guidance rather than a worked
      instance: no already-executed approved PRD scope change was found to cite during
      this node's own authoring (see *Scope and omissions*).
3. **Write down the candidate before the thread is lost.** Capture the source (file
   path, or issue number and comment), its screened status (Accepted / Proposed /
   Superseded / ratified-undefined / in-flight), and the one-sentence claim it would
   support if cited. State plainly whether that claim is an **intent** claim or a
   **behaviour** claim — `standards/decision-references.md`'s own "which kind of claim
   are you making?" test decides everything that follows, and getting it wrong there
   is the failure that standard calls a security concern.
4. **Hand off.** A written-down, status-screened candidate's next stop is
   `standards/decision-references.md` for how to cite it, how to pin it, and what to
   do if it conflicts with another settled decision of the same claim type. This node
   stops at "does a decision exist here, and is it settled" — never at "how do I write
   the citation."

## See also

- `standards/decision-references.md` — citation form, pinning, and the conflict
  recipe for a decision already screened as settled.
- `launchpad/decisions/README.md` — the decision-record lifecycle and file
  conventions this node's screening steps rely on.
- `ingestion/concept-extraction.md` (#955, sibling, not yet merged at this node's
  authoring time) — the parallel noticing step for concepts generally.

## Boundary

This node does not describe:

- **How to cite a decision once found** — citation form, pinning, and the four-step
  recipe for conflicting decisions. That is entirely `standards/decision-references.md`'s
  territory.
- **A catalog of citation shapes or evidence classes for lookup.** That is reference
  material's territory; this node instructs one action — noticing and screening — not
  a table an author consults mid-task for a fact.
- **How to acquire the underlying skill of reading an ADR or issue thread from
  scratch, for a newcomer.** That is a tutorial's territory, and no corpus template
  currently covers that form.
- **Why the decision-precedence rule (`ADR-0029`) exists conceptually, or the theory
  behind ranking evidence by claim type.** That is concept/explanation territory.
- **Whether two already-settled decisions of the same claim type conflict, and what to
  do about it.** That is `standards/decision-references.md`'s own "When two accepted
  decisions conflict" section, which runs only after this node's screening has already
  identified two settled candidates.
- **Deciding an open question itself.** Agents draft; humans decide
  (`launchpad/AGENTS.md` §5.1). This node's every worked example is a *screening* of
  something a human already decided, never a decision made by this node.

## Relationships

- **`references: corpus-agents`.** `AGENTS.md`'s node-authoring evidence discipline is
  the procedure this node's screened output ultimately feeds into, and this node's own
  procedure stays accurate even if `AGENTS.md`'s later steps are later reworded — the
  same loose coupling `ingestion/concept-extraction.md` (#955) declares toward the same
  target for the same reason.
- **`implements: corpus-template-procedure`.** This node is a how-to-shaped instance of
  that template, per `relationships.schema.json`'s own worked example for `implements`:
  "a template instance of a standard."
- **No edge to `ingestion-concept-extraction` (#955) or any other Feature #620
  sibling.** None besides `agents-invariants` are merged on `origin/launchpad` at this
  node's authoring time (checked via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`), and `agents-invariants` is not a genuine dependency of this
  node's own subject.

## Scope and omissions

**This node covers** noticing that a decision exists and is worth citing across four
source shapes — an ADR file, a document claiming to be a specification, a GitHub issue
thread, and a PRD/Feature issue body — screening each for whether it has actually been
settled rather than merely proposed or discussed, writing the candidate down, and
handing it off to `standards/decision-references.md`. It grounds three of the four
branches in a real occurrence found during this node's own authoring; the fourth is
stated honestly as untested.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citing a screened, settled decision — form, pinning, conflict recipe | `standards/decision-references.md` |
| Resolving a conflict between two settled decisions of the same claim type | `standards/decision-references.md`'s "When two accepted decisions conflict" |
| Checking a candidate *concept* (as opposed to a decision) against the existing corpus | `agents/concept-resolution.md` (#642), not yet merged |
| Noticing a candidate concept generally, across code, decision rationale, or issues | `ingestion/concept-extraction.md` (#955), not yet merged |
| Creating, updating, or retiring the resulting corpus node | `AGENTS.md` |
| How a specification becomes "ratified" | Undefined in this repository — `standards/decision-references.md`'s own gap |

**Expected but not verified when this node was written:**

- **Whether the PRD/Feature branch (2d) generalizes as cleanly as the other three.**
  No already-executed, already-approved PRD scope change was found to cite as a worked
  example; only the identical boilerplate clause naming the possibility was found,
  repeated verbatim across fourteen sibling Feature issues.
- **Whether a ratified specification will ever exist in this repository, and if so
  what marks it as such**, is undefined today, per `standards/decision-references.md`'s
  own Scope and omissions — this node's guidance for branch 2b is built from that
  documented absence, not from a worked ratified instance.
- **No author or harness has applied this node's screening steps outside this
  session.** Whether the four-branch fork is followable in practice, rather than
  merely correct, is untested.
