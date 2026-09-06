---
id: agents-concept-resolution
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
  - statement: "AGENTS.md's own 'Creating a node' step 2 states: 'Check nothing already covers it. Read the existing nodes under launchpad/docs/corpus/. If one is close, you are updating, not creating.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md states 'One node is one independently maintainable idea' as the corpus's own atomicity rule, and refers its full treatment to a per-type standard rather than restating it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md documents, as a named trap rather than a hypothetical, that 'There was nothing to point at' was true when the corpus held only its own instruction node and stops being true the moment a second node merges, and that two independent agents authoring sibling nodes copied an earlier version of that paragraph and produced a false justification from it because it read as a general rule rather than a fact about one moment."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "standards/atomicity.md's own Scope and authority states its governed question as, verbatim, 'given a subject you are about to document, is it one node or more than one?' -- a question about a subject the author has already decided to write about, not about whether that subject already exists in the corpus under a different name. Its Scope and omissions table names, across its four rows, taxonomy, identifiers, naming, linking (twice -- once generally and once for split-subject linking mechanics), normative language, evidence, the general scope-section convention, generated-content granularity, and review requirements as subjects it does not decide -- and none of them is duplicate detection against the existing corpus, confirming the gap by omission rather than by assuming it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "standards/atomicity.md's Boundary case A names 'a concept and the procedure that uses it' as a pair the create procedure itself already calls two nodes, and grounds that in its own maintenance-clock test: 'a procedure changes when the tooling it drives changes, and a concept changes when the design changes' -- different clocks in the ordinary case."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "standards/atomicity.md's Exceptions and escalation section states that a disputed granularity call is 'a judgement, not an exception,' and resolves it in four steps: the author records the tension and names it in the pull request; the reviewer decides and this is where enforcement lives; if author and reviewer disagree the node ships as the tie-break outcome; and a repeated disagreement is filed as an issue against the standard because 'a boundary two people read differently is a defect in the procedure above.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "validate.py's find_duplicate_ids keys duplicate detection exclusively on exact, case-sensitive string equality of a node's id field; it reports an error only when two loaded nodes' id strings are identical, and it has no logic that compares two nodes' bodies, claims, or subjects for conceptual overlap."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:408"
  - statement: "Because find_duplicate_ids' only signal is id-string equality, a second node describing the same idea under a different id passes every mechanical check the corpus runs; the checker validates front matter, duplicate ids, relationship targets, citation forms and non-canonical files, and none of those is a property of whether two different ids describe one idea -- the same reasoning standards/atomicity.md states for its own, related but distinct, question of how many ideas one node holds."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:408"
      - "launchpad/docs/corpus/standards/atomicity.md"
    confidence: 0.85
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- naming the corpus surface a node documents, not the documentation form (how-to/reference/explanation) its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "templates/procedure.md requires a corpus node built from it to carry, in its body: an Overview stating the task in one line; an optional Before you start section; one numbered task sequence per logical goal, which Diátaxis's own words permit to fork rather than stay strictly linear when 'the sequences of action in a how-to guide sometimes need to fork and overlap, and they have multiple entry and exit-points'; a See also section; an explicit Boundary statement; a Relationships section; and a Scope and omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/concept.md states its own Purpose as answering 'what is this, and how does it fit with everything else I already know,' names the drift this template exists to prevent as sideways into reference or forward into how-to/procedure territory, and states in its own Boundary section that 'if a concept draft starts numbering steps for the reader to perform, that content belongs in a procedure node instead.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
  - statement: "Concept resolution's own subject -- an ordered sequence with a genuine decision fork (match found, no match, ambiguous) that an agent performs before drafting -- numbers steps for the reader to perform rather than discursively explaining an abstraction, so templates/concept.md's own boundary against procedure-shaped drafts routes this subject to templates/procedure.md instead, not the reverse."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
      - "launchpad/docs/corpus/templates/concept.md"
    confidence: 0.85
  - statement: "agents/invariants.md (id agents-invariants) carries type: agent, reasoning in its own evidence ledger that its subject -- the invariants an agent or reviewer must hold when authoring, updating or retiring a corpus node -- 'is the same corpus surface AGENTS.md itself documents (type: agent), whereas governance is used in this corpus for the standards/ and templates/ subtrees, a related but distinct family of meta-documents.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "This node's subject -- a decision procedure an agent runs before authoring any corpus node -- is the same agent-facing corpus surface agents-invariants and AGENTS.md itself already occupy, so this node's type: agent follows the same precedent agents-invariants already established rather than an independently invented choice; it is not a template meta-document, so the governance precedent templates carry for documenting the corpus's own authoring rules does not apply here."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.75
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no file under agents/ besides invariants.md, and no ingestion/ directory at all, so no sibling document task under parent Feature #620 besides #649 (agents/invariants.md, merged) is a valid relationship target."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> agents/invariants.md present; no other agents/*.md; no ingestion/ directory; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "A RepoQL explore call in this authoring session, scoped to file:///launchpad/docs/corpus/** and asking whether an existing node already covers checking a candidate concept against the existing corpus before authoring a duplicate, returned templates/concept.md as its top-ranked (99%) semantic match -- surfaced by meaning rather than by the literal words 'concept' or 'resolution' appearing in a title."
    entry_class: FACT
    evidence:
      - "mcp__repoql__explore(keywords='concept resolution, checking for duplicate corpus concept, is this already covered', question='Given a candidate subject an agent is about to document, is there an existing corpus node that already covers it under a different name?', uriGlob='file:///launchpad/docs/corpus/**') -> top result 99% file:///launchpad/docs/corpus/templates/concept.md"
  - statement: "A follow-up RepoQL keywords call in the same session and scope, made immediately after the explore call above, failed with a DuckDB out-of-memory fatal error rather than returning a semantic answer, so this node's endorsement of such tooling in its See also section is grounded in one successful run, not in a tool proven reliable across repeated calls."
    entry_class: FACT
    evidence:
      - "mcp__repoql__keywords(keywords='duplicate concept check, is this idea already documented, same idea different name', uriGlob='file:///launchpad/docs/corpus/**') -> DuckDB FATAL Error: database has been invalidated because of a previous fatal error (Out of Memory)"
  - statement: "Issue #642's own Objective states: 'Create launchpad/docs/corpus/agents/concept-resolution.md as the single canonical procedure node for concept resolution,' naming the node explicitly as a procedure node rather than leaving the documentation form to be inferred."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#642 body, Objective section"
  - statement: "Issue #642's Definition of Done requires that the document represent one independently maintainable knowledge node, that any newly discovered second concept/contract/procedure be filed as its own task rather than folded in, that every substantive claim be traceable to an opened source with FACT/INFERENCE/TEAM_KNOWLEDGE not conflated, and that corpus validation pass locally with no broken node ids, invalid source paths, duplicate ids or schema violations introduced."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#642 body, Definition of done section"
  - statement: "Parent Feature #620's Out of scope section states, verbatim: 'Work owned by sibling corpus Features, implementation of the knowledge-crate runtime, and any artifact not required by this Feature outcome or its declared child issues,' confirming there is no ingestion-pipeline runtime this node is expected to describe -- only agent-facing procedural guidance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Out of scope section"
  - statement: "Parent Feature #620's Acceptance criteria require that every node passes corpus schema/graph/provenance validation and uses the assigned template, names concrete source start points, records evidence appropriate to its claims, does not duplicate canonical claims owned by other atomic nodes, and lets an independent reader traverse corpus nodes to implementation and verification evidence for a representative question in the feature's area."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Acceptance criteria section"
relationships:
  - type: references
    target: corpus-agents
  - type: references
    target: corpus-standard-atomicity
  - type: implements
    target: corpus-template-procedure
---

# Concept resolution: how-to

Before drafting any new `launchpad/docs/corpus/` node, decide whether the candidate
subject is genuinely new or is an existing node in different clothes, so the work
becomes an update rather than a silent duplicate. This is AGENTS.md's "Creating a
node" step 2 made procedural: "Check nothing already covers it... If one is close,
you are updating, not creating."

## Before you start

- A candidate subject you can attempt to state in one sentence. If it already needs
  an *and* or an *or* to be true, you may be holding two candidates rather than one —
  a screening habit shared with `standards/atomicity.md`'s own test 1, though that
  standard's question (how many nodes does new content become) is not this one's
  (does this content already have a node).
- Know which branch a Feature-wide PR will actually merge into (`origin/launchpad`
  at the time of writing this node). Every check below runs against that branch, not
  the author's own worktree — the same distinction AGENTS.md states for relationship
  targets applies here for equal reason: a node that looks absent in your own tree
  can already exist on the branch your work will land on.

## Resolve the candidate against the existing corpus

1. **State the candidate in one sentence.** No conjunction joining two nouns. This
   proves nothing on its own — a sentence can always be rewritten — but an author who
   cannot say what the candidate is about without an *and* usually already knows why,
   and a two-part sentence is worth splitting before either half is checked against
   the corpus.
2. **Enumerate what exists, on the branch you are merging into.** Run
   `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` (or
   whatever the real merge-target ref is) before deciding anything. Do not reason
   from memory of what the corpus "probably" holds, and do not reuse an earlier
   enumeration from a previous session — the corpus grows with every merged sibling
   task. AGENTS.md names the failure mode this step exists to prevent: an
   enumeration-shaped claim that was true once and stopped being true the moment a
   second node merged, copied forward as a general rule by two independent agents
   who each produced a false justification from it.
3. **Search the enumerated nodes for near matches — by meaning, not only by
   filename.** Read titles and, for anything with overlapping vocabulary, the front
   matter's `id`, `type`, and the body's opening definition or overview, not the
   filename alone; two nodes can use unrelated filenames for the same underlying
   idea. Where a semantic search aid is available in the authoring session (this
   node's own evidence ledger records a verified instance: a RepoQL `explore` query
   asking, in plain language, whether an existing node covered this exact
   concern surfaced `templates/concept.md` as its top match, ahead of anything
   matching on the literal words "concept" or "resolution"), it widens the candidate
   list past what a filename or exact-phrase search would find — but it is an aid
   that was verified working once, not a step proven reliable across repeated calls
   (a follow-up call in the same session failed outright on an infrastructure
   error), and it never substitutes for actually enumerating step 2's tree or
   reading step 4's candidates.
4. **For each candidate surfaced in step 3, apply the same-idea test.** Does the
   candidate answer the same reader question this new subject would answer, from
   the same corpus surface (would it plausibly carry the same `type`), such that
   adding the new claim to the candidate's body — rather than authoring a second
   file — keeps the result one independently maintainable idea, per AGENTS.md's own
   rule? A candidate that only mentions the same words in passing, or that covers a
   related but genuinely separate idea (a concept and the procedure that uses it are
   `standards/atomicity.md`'s own worked example of two nodes, not one, precisely
   because they sit on different maintenance clocks), is not a match.
5. **Decide, and act on exactly one branch:**
   - **A close match exists.** Stop. Do not draft a new file. Follow AGENTS.md's
     "Updating a node" procedure against the matched node instead of this one.
   - **No close match exists.** Proceed to author a new node, and hand off
     immediately to `standards/atomicity.md`'s five-test decision procedure to
     decide how many nodes the now-confirmed-new subject becomes. Concept
     resolution only answers *does this already exist*; atomicity answers *how many
     files does it become*, and that second question only makes sense once this
     one has answered no.
   - **Genuinely ambiguous** — the same-idea test in step 4 reads differently
     depending on which reader's question is assumed, or a plausible case exists on
     both sides. Do not decide silently. Record the tension in the node (or, if one
     is not yet drafted, in the task) and name it in the pull request, letting the
     reviewer decide — the same author-records/reviewer-decides pattern
     `standards/atomicity.md`'s own Exceptions and escalation section uses for its
     disputed granularity calls, extended here from a splitting dispute to a
     resolution dispute for the identical reason: a boundary two people read
     differently is worth escalating, not guessing at.

## See also

- `corpus-agents` (`AGENTS.md`) — the full create/update/retire procedure this
  resolution step is a prerequisite step of; step 5's "close match" branch routes
  there directly.
- `corpus-standard-atomicity` (`standards/atomicity.md`) — the decision procedure
  for how many nodes a *confirmed-new* subject becomes, run immediately after this
  one answers "new."
- `templates/procedure.md` and `templates/concept.md` — read the candidate node's
  own template-shaped section before ruling it a match or a miss; a false negative
  here often hides behind two documents describing the same idea in different
  template clothing (a concept node's Definition restating a procedure node's
  Overview, or the reverse).

## Boundary

Per `templates/procedure.md`'s own required Boundary checklist for any how-to-shaped
instance, this node is not:

- **A reference node.** It is not an information-oriented lookup table of corpus
  `id`s, `type`s, or field values a reader consults mid-task — it is a sequenced
  decision an agent performs once, before drafting. A reader wanting to look up
  what `type` values exist, rather than to resolve a specific candidate, wants a
  reference node instead.
- **A tutorial.** It assumes the reader is already a competent corpus author who
  knows how to read and write a node — the same "application of skill" reader
  `templates/procedure.md`'s own Industry model section describes — not a newcomer
  acquiring that skill from scratch.
- **A concept/explanation node.** It does not discursively explain what "a
  concept" is in the abstract, why the corpus organizes itself into atomic nodes,
  or the design history behind that choice — `templates/concept.md` and
  `standards/atomicity.md` respectively already own those questions. This node
  only states the steps for checking one specific candidate against what already
  exists.

This node also does not describe:

- **How many nodes a genuinely new subject becomes**, once resolution answers
  "new." `standards/atomicity.md`'s five-test procedure owns that question
  entirely; concept resolution stops at the yes/no and hands off rather than
  restating any of its five tests.
- **Which `type`, template, or body shape a resolved-as-new subject should
  take.** That is each template's own scope under `templates/`, decided by the new
  subject's own corpus surface, not by anything here.
- **The internals or general reliability of any particular search tool** used in
  step 3. RepoQL's `explore`/`keywords` tooling is named as one aid this node's own
  evidence ledger verified working once, in this authoring session — not as a
  required step, and not as exhaustively tested (the immediate follow-up call in
  the same session failed on an infrastructure error, not a content finding). An
  agent without such tooling still resolves correctly by enumerating step 2's tree
  and reading step 4's candidates; nothing in this procedure depends on a search
  tool being present.
- **What counts as "close enough" to be the same idea, in a genuinely disputed
  case.** Step 5's ambiguous branch routes that dispute to the reviewer rather than
  defining a numeric or structural threshold here, for the same reason
  `standards/atomicity.md` declines to define one for its own disputed granularity
  calls: a boundary read differently by two people is a defect to fix in the
  procedure, not a threshold to guess at in advance.

## Relationships

- **references: `corpus-agents`.** This node's own authority is derived from
  AGENTS.md's "Creating a node" step 2, not original to itself — the same
  `references` directionality `relationships.schema.json` states, "source cites
  target as supporting context."
- **references: `corpus-standard-atomicity`.** The sibling decision procedure this
  node hands off to once resolution answers "new"; a loose citation edge, since
  this node's own steps stay accurate even if atomicity's five tests are later
  revised.
- **implements: `corpus-template-procedure`.** Per `relationships.schema.json`'s own
  worked example for `implements`, "a template instance of a standard" — this node
  is exactly that: a How-to-shaped instance of `templates/procedure.md`.

**Checked, not declared.** No sibling `agents/*.md` or `ingestion/*.md` task under
parent Feature #620 besides `agents-invariants` (#649, merged) exists as a node on
`origin/launchpad` at the recorded revision — confirmed by `git ls-tree` in this
node's own evidence ledger — so none of them is a valid relationship target yet.

## Scope and omissions

**This node covers** the decision procedure an agent runs, before drafting any new
corpus node, to determine whether a candidate subject already has an existing node
under a different name or angle: stating the candidate, enumerating the real
merge-target tree, searching by meaning rather than filename alone, applying a
same-idea test to each candidate, and acting on exactly one of three outcomes
(update, create-and-hand-off, or escalate an ambiguous call).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How many nodes a confirmed-new subject becomes | `standards/atomicity.md` |
| Which template or `type` a resolved-as-new subject should use | `templates/*.md`, chosen per subject |
| The full create/update/retire procedure this step is one part of | `AGENTS.md` |
| Evidence classification mechanics beyond what this node's own claims need | `AGENTS.md`, `standards/confidence.md` |
| Concrete agent procedures for ambiguity handling, evidence resolution, documentation creation/update/validation, change-impact analysis, repository navigation, stale-documentation handling and corpus usage more broadly | sibling tasks under parent Feature #620 (#640, #641, #643-#648, #650-#651, #953-#972) — none merged besides #649 at this node's authoring time |
| How an *ingestion*-side agent (drawing evidence from a specific source type — git history, CI, issues, PRs) should apply this same resolution question to ingested claims rather than to whole candidate nodes | the `ingestion/*.md` document family under Feature #620, none merged at this node's authoring time |

**No relationship declared to any sibling `agents/*.md` or `ingestion/*.md` task.**
Checked before deciding that rather than assumed: at the recorded revision, only
`agents-invariants` (#649) exists as a merged node in that family, and its subject
(binding invariants for authoring a node) is adjacent to but distinct from this
node's subject (whether a candidate node is a duplicate) — an edge between them
would cite the same two authoritative sources (`AGENTS.md`, `node.schema.json`)
this node's own ledger already cites directly, not a substantive typed
relationship. The natural moment to add one is when a genuine dependency between
the two is drafted, not assumed here.

**Expected but not verified when this node was written:**

- **No real candidate node has been resolved using this procedure yet.** Every step
  above is derived from `AGENTS.md`'s stated rule, `standards/atomicity.md`'s
  worked precedent, and one verified search-tool run in this authoring session —
  not from a body of practice. The first real resolution call (accepting an
  update, rejecting a false match, or escalating a genuine ambiguity) is what
  actually tests whether step 4's same-idea test is sufficient or needs revision.
- **Whether RepoQL's `explore`/`keywords` tooling is reliably available to every
  agent authoring a corpus node**, or specific to this session's tool
  configuration, was not established — only that it worked once here and failed
  once immediately after. This node's Boundary section states explicitly that
  nothing in the procedure depends on it being present, precisely because this was
  not verified.
- **Whether the same-idea test in step 4 produces the same verdict for two
  independent agents given the same candidate and the same enumerated corpus** was
  not tested — only `standards/atomicity.md`'s own reviewer checklist, for its
  distinct splitting question, has that kind of precedent to draw on, and it names
  the same gap for itself.
