---
id: agents-change-impact-analysis
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
  - statement: "node.schema.json requires id, type, status, origin, audiences and evidence, permits relationships as the only other property, and rejects (additionalProperties: false) any field beyond those seven; its type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- with no member for template, policy or procedure, because the enum names the corpus surface a node documents, not the documentation form its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node's type is agent rather than governance, on the same reasoning agents-invariants.md already used for itself: its subject is the corpus's own agent-facing authoring surface, the same surface AGENTS.md (type: agent) documents, whereas governance is this corpus's precedent for the standards/ and templates/ subtrees -- a related but distinct family of meta-documents this node is neither a standard nor a template instance of."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.8
  - statement: "templates/procedure.md's own Boundary section draws the procedure-versus-runbook line explicitly: 'A procedure is for a task the reader chooses to perform on their own schedule ... sequenced in the order its steps must happen. A runbook is for a condition that has already occurred and demands a response ... triggered by an alert or failure, not chosen.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "Assessing what else is affected before editing or retiring a corpus node is a task an author chooses to perform on their own schedule, before any alert or already-firing condition exists -- the procedure shape templates/procedure.md's own Boundary section describes, not the runbook shape templates/runbook.md describes for 'the relay is 5xx-ing, what do I do.'"
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
      - "launchpad/docs/corpus/templates/runbook.md"
    confidence: 0.85
  - statement: "AGENTS.md's Updating a node procedure states: 'Re-verify the claims you are touching, against those sources at current HEAD (git rev-parse HEAD). A claim whose source moved is not still a FACT because it used to be,' and separately: 'Decide whether the recorded revision moves ... Re-verified every claim at HEAD -> move it. Re-verified some -> move it only if the rest still hold at HEAD too. Check, do not assume. Re-verified nothing -> leave it. Every cited source byte-identical between the recorded revision and HEAD -> leave it.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's Retiring a node procedure states: 'Find what points at it. Search the corpus for the node's id. Those edges will still resolve -- that is the problem, not the safety net,' and: 'Decide what replaces it, and say so in the vocabulary. If another node takes over the subject, that node declares supersedes targeting the retired id,' and: 'If nothing replaces it, say that in the retired node's body. A reader arriving from an old link needs to be told the subject is gone, not left guessing.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "validate.py's find_unresolved_relationship_targets (line 437) reports a hard error only when a relationships[].target matches no loaded node's id; AGENTS.md states that deleting a node breaks every relationship targeting it while retiring it by status change leaves those relationships resolving -- so a mechanically passing validation run after a retirement proves only that the id still exists, never that an inbound edge's claim about this node still holds."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:437"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "standards/atomicity.md states: 'The checker confirms only that a relationship target matches some loaded node's id; it never establishes that the target still covers the subject the edge was drawn for,' and separately: 'Over-merging fails silently ... The edges now point somewhere wrong and no run will ever say so. Over-splitting fails visibly ... A reader arriving on an old edge is told where to go.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "relationships.schema.json defines five relationship types with these directionalities: depends-on -- 'source requires target to be true/current for source's own claims to hold'; supersedes -- 'source replaces target; target becomes historical'; implements -- 'source is the concrete realization of target'; references -- 'source cites target as supporting context; no ownership or currency dependency implied'; part-of -- 'source is a constituent section/child of target'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "standards/linking.md states that a relationships[] edge 'is what a generated graph view, or a future relationship-aware tool, resolves. It is invisible to a reader of the rendered body ... unless that reader separately opens the front matter,' while 'a body-prose mention is the reverse: it is exactly what that reader sees, and it resolves to nothing a machine can traverse,' and that 'validate.py never reads a node's body past the frontmatter delimiter, so no MUST above has any mechanical backing. A body containing a link to a node that has never existed ... validates exactly as cleanly as a body with none of those problems.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/linking.md"
  - statement: "Running 'grep -rn \"agents-invariants\" launchpad/docs/corpus --include=\"*.md\"', excluding agents/invariants.md itself, at repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90 returns zero matches: no other corpus node currently declares a relationships[] edge toward agents-invariants, and none mentions its id in body prose or an evidence citation either."
    entry_class: FACT
    evidence:
      - "grep(pattern='agents-invariants', scope='launchpad/docs/corpus/**/*.md', excluding='launchpad/docs/corpus/agents/invariants.md') -> no matches, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Running 'grep -rl \"corpus-template-procedure\" launchpad/docs/corpus --include=\"*.md\"' at the same revision returns five files: templates/procedure.md (the id's own home), templates/runbook.md, templates/flow.md, development/build.md, and development/debugging.md -- a single id search surfacing hits of two structurally different kinds that require different handling."
    entry_class: FACT
    evidence:
      - "grep(pattern='corpus-template-procedure', scope='launchpad/docs/corpus/**/*.md') -> templates/procedure.md, templates/runbook.md, templates/flow.md, development/build.md, development/debugging.md, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Of those five hits, development/debugging.md (id debugging) declares an actual relationships[] edge -- '- implements: corpus-template-procedure' under its own Relationships heading -- while development/build.md (id corpus-development-build) mentions the same id only inside one evidence-ledger FACT statement and states explicitly in its own Scope and omissions, 'No relationships declared,' with no relationships field anywhere in its front matter; a change to templates/procedure.md's required sections would structurally affect debugging.md's declared conformance but would only make build.md's evidence-ledger sentence about the template stale, not break anything the checker enforces on build.md itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/build.md"
  - statement: "node.schema.json's status enum holds draft, active, deprecated, retired, flagged, and describes flagged as ADR-0029's 'unestablished/flagged' state: two same-claim-type authoritative sources contradict each other and a human has not yet resolved it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Parent Feature #620's stated Out of scope is: 'Work owned by sibling corpus Features, implementation of the knowledge-crate runtime, and any artifact not required by this Feature outcome or its declared child issues' -- so this node describes a manual procedure using existing tools (grep, the corpus's own relationship semantics), not a proposal for automated impact-analysis tooling."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
  - statement: "Issue #641's Definition of Done requires schema-valid front matter with typed relationships appropriate to the node, that every substantive claim be traceable to current code/test/spec/decision/history or attributed GitHub evidence without conflating FACT/INFERENCE/TEAM_KNOWLEDGE, that the document link relevant nodes without duplicating their canonical content, and that corpus validation pass locally with no broken node IDs or schema violations."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#641 definition of done"
  - statement: "Issue #641's Definition of Done also carries a boilerplate how-to-shaped tail -- 'States goal, prerequisites and allowed environment/scope,' 'Provides ordered steps that are executable and project-specific,' 'Defines success verification and rollback/cleanup where relevant,' 'Links authoritative commands/config rather than giving generic advice' -- copied mechanically onto this task rather than written for it, the same pattern templates/procedure.md's own 'Note on Definition of Done' documents for its sibling #1345; this node is built against Feature #620's real acceptance criteria and against AGENTS.md's own Updating/Retiring text, not against a rollback/cleanup framing that does not fit a document-impact assessment."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#641 definition of done, compared against launchpad-26/buzz#1345's definition of done as documented in templates/procedure.md"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: agents-invariants
  - type: references
    target: corpus-standard-atomicity
  - type: references
    target: corpus-standard-linking
  - type: references
    target: corpus-template-runbook
---

# Change impact analysis: how-to

How to assess the blast radius of a change to an existing corpus node -- what else
in the corpus, or pointing into the corpus, could go stale -- before editing or
retiring it. This generalizes the change-impact reasoning `AGENTS.md`'s own
*Updating a node* and *Retiring a node* sections already do in miniature into one
repeatable procedure, so it applies the same way whichever of the two you are
about to do.

## Before you start

- The node's `id` and its current `status`.
- Whether you are about to **update** it (some claims change, the node stays
  current) or **retire** it (`status` becomes `deprecated`/`retired`, the node
  stays but is no longer current) -- the last step below forks on this, mirroring
  `AGENTS.md`'s own two separate procedures.
- The merge-target branch fetched locally (`git fetch origin launchpad`, or
  whatever branch this change will merge into) -- work from `origin/<branch>`'s
  tree, not your own worktree, for the same reason `AGENTS.md`'s *Creating a
  node* step 9 states for relationship targets: what resolves in your worktree
  can differ from what CI checks.

## Assess the blast radius

1. Confirm the node's `id` and, if the merge target is not already local,
   `git fetch origin launchpad` (or the target branch), then work from that
   branch's corpus tree for every step below.
2. Search the whole corpus for every mention of the `id` -- not only its
   declared `relationships[]` edges: `grep -rn "<id>" launchpad/docs/corpus
   --include="*.md"`, excluding the node's own file. This single search
   surfaces two structurally different kinds of hit that `validate.py` itself
   does not distinguish, and that you must (see *Two kinds of hit, one grep*
   below): a `relationships[].target` entry, which is machine-checked, and a
   body-prose or evidence-ledger mention, which is not.
3. For each hit, open the referencing node and classify it: does it declare a
   `relationships[]` edge naming this `id` (check the edge's own `type`), or
   does it only mention the `id` in prose or in an evidence citation with no
   accompanying edge?
4. For each declared inbound edge, reason about impact from that relationship
   type's own directionality (`relationships.schema.json`), not from the fact
   that it merely resolves -- a target matching a loaded `id` is all
   `find_unresolved_relationship_targets` checks; it says nothing about whether
   the edge still means what it did when it was declared:
   - **`depends-on`** pointing at this node: the referencing node's own claims
     require this node to be true/current. This is the highest-impact case --
     re-check whether the referencing node's dependent claim still holds after
     your change.
   - **`implements`** pointing at this node, when this node is itself a
     template or standard: every node with an inbound `implements` edge is a
     concrete instance of it. A change to this node's required sections or
     normative rules is a candidate to invalidate each of them structurally,
     not merely to make a citation of them stale.
   - **`part-of`** pointing at this node: the referencing node is a
     constituent of this one. A change to this node's own scope can change
     what its parent can still truthfully say it contains.
   - **`supersedes`** pointing at this node: the referencing node already
     declares this one historical. A change here does not need propagating to
     the superseding node; it may need propagating to whatever else still
     points at this node as though it were current.
   - **`references`** pointing at this node: `relationships.schema.json`
     states this directionality outright -- "no ownership or currency
     dependency implied." Worth a note in the referencing node's prose if the
     cited claim changed; not a structural break.
5. For each mention with no declared edge, remember it will not resurface on
   its own: `validate.py` discards a node's body before any check runs, so a
   sentence naming this node, once wrong, "passes exactly as cleanly as a
   correct one." Decide now whether it needs fixing; there is no later
   automated prompt that will raise it.
6. Decide the action, forking on what you are doing:
   - **6a. Updating.** Per `AGENTS.md`'s own four branches, decide whether the
     recorded provenance revision moves: every touched claim re-verified at
     `HEAD` -> move it; some re-verified and the rest confirmed still holding
     at `HEAD` -> move it; nothing re-verified, or every cited source
     byte-identical between the recorded revision and `HEAD` -> leave it. For
     every referencing node found in steps 3-5 whose own claim depended on
     what you changed, re-verify that claim there too and update its ledger if
     it no longer holds -- a `depends-on` or `implements` edge from step 4
     names exactly which referencing nodes that applies to.
   - **6b. Retiring.** Per `AGENTS.md`'s own steps, decide what replaces this
     node -- if another node takes over the subject, that node declares
     `supersedes` targeting the retired `id`; if nothing replaces it, say so in
     the retired node's own body. For every inbound edge found in step 4 whose
     type implies currency (`depends-on`, `implements`, `part-of` -- not
     `references`, which explicitly implies none), decide whether to repoint
     it at the replacement or leave it pointing at the now-retired node
     because it genuinely meant the historical content, per `AGENTS.md`'s own
     "repoint the ones that wanted the subject, leave the ones that genuinely
     meant the retired node."
7. Record what you found and decided for every hit from step 2, including a
   hit that needed no change. An assessment that lists only the changes made
   is, to the next reader, indistinguishable from one that never searched.

### Two kinds of hit, one grep

A real, current example makes the distinction concrete rather than abstract.
`grep -rl "corpus-template-procedure" launchpad/docs/corpus --include="*.md"`
returns five files, two of which matter here: `development/debugging.md`
declares `- implements: corpus-template-procedure` under its own Relationships
heading -- a real edge `find_unresolved_relationship_targets` checks and a
future edit to `templates/procedure.md`'s required sections would structurally
affect. `development/build.md` mentions the identical `id` only inside one
evidence-ledger `FACT` statement and states outright in its own Scope and
omissions, "No relationships declared" -- the same edit would make that one
sentence stale, but nothing the checker enforces on `build.md` would move. Both
are real hits on the same grep; only opening each referencing node tells you
which kind you have.

## See also

- `launchpad/docs/corpus/AGENTS.md` -- the literal *Updating a node* and
  *Retiring a node* step sequences this procedure generalizes; follow them for
  the mechanics once impact is assessed.
- `launchpad/docs/corpus/agents/invariants.md` -- the binding invariants (I5,
  unresolved relationship targets; I10, retirement by status change) this
  procedure exists to help an author keep satisfied under change.
- `launchpad/docs/corpus/standards/atomicity.md` -- a different question
  answered from the same asymmetry: how many nodes a *new* subject becomes,
  argued from the same "over-merging fails silently, over-splitting fails
  visibly" observation this node reuses for an *existing* node's edges.
- `launchpad/docs/corpus/standards/linking.md` -- the edge-versus-prose
  distinction step 2's search depends on, and the syntax for fixing a
  body-prose mention once step 5 finds one that needs it.
- `launchpad/docs/corpus/schema/relationships.schema.json` -- the five
  relationship types and their exact directionality, for step 4.

## Boundary

This node does not describe:

- **How to create, update, or retire a node, mechanically** -- `AGENTS.md`
  owns the literal procedures; this node only tells you what to check *before*
  running them, and points back to `AGENTS.md` for the steps themselves.
- **How many nodes a new subject should become** -- that is
  `standards/atomicity.md`'s question, asked before a node exists. This
  node's question is asked about a node that already exists and is about to
  change; the two are easy to conflate because both reason about the same
  edge-resolution asymmetry.
- **The syntax for writing a body-prose pointer** -- `standards/linking.md`
  owns that, once step 5 has found a mention that needs fixing.
- **The five relationship types' exact contract** -- `relationships.schema.json`
  is the source; this node only tells you which situations call for consulting
  it.
- **How to acquire this skill from scratch, for a newcomer** -- a tutorial,
  which has no corpus template as of this writing.
- **Automated impact-analysis tooling.** Parent Feature #620 explicitly
  excludes "implementation of the knowledge-crate runtime." Every step above
  uses `grep` and manual reasoning about declared relationship types; none of
  it proposes or assumes a future tool that walks the graph automatically.

## Relationships

- **`depends-on: corpus-agents`.** This node's authority is derived from
  `AGENTS.md`'s *Updating a node* and *Retiring a node* text, not original to
  itself -- the same reasoning, and the same target, `agents-invariants`
  already declares for itself.
- **`implements: corpus-template-procedure`.** Per `templates/procedure.md`'s
  own guidance, a how-to-shaped instance node "should declare `implements`
  targeting `corpus-template-procedure` ... once this node is merged."
- **`references: agents-invariants`.** This node's own front-matter `type`
  choice (`agent`, not `governance`) is argued directly from
  `agents-invariants`' precedent -- supporting context, not a currency
  dependency.
- **`references: corpus-standard-atomicity`.** This node's central argument --
  that a mechanically-resolving edge is not proof an edge's claim still holds
  -- is drawn directly from `atomicity.md`'s own stated asymmetry between
  over-merging and over-splitting, quoted above.
- **`references: corpus-standard-linking`.** Step 2's search technique and the
  *Two kinds of hit, one grep* worked example both rest on `linking.md`'s
  distinction between a machine-resolved edge and an unchecked body mention.
- **`references: corpus-template-runbook`.** The *Before you start* /
  *Boundary* reasoning for why this is a procedure and not a runbook is drawn
  directly from `runbook.md`'s own stated trigger condition ("an alert or
  failure, not chosen"), contrasted against `procedure.md`'s.

All six targets were checked against `origin/launchpad`'s corpus tree
immediately before finalizing this front matter (`git fetch origin launchpad
&& git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, at
the revision this node's provenance entry records) and are present there. No
edge targets any sibling `agents/*.md` or `ingestion/*.md` task under Feature
#620: none of the other 31 are merged at this node's authoring time, so none
is a valid relationship target, the same reasoning `agents-invariants`
recorded for itself.

## Scope and omissions

**This node covers** searching the corpus for every mention -- declared edge or
prose -- of a node about to change; reasoning about impact from each
relationship type's own declared directionality rather than from mere
resolution; the fork between updating (re-verification, moving the recorded
revision) and retiring (deciding a replacement, repointing or leaving inbound
edges); and recording the assessment even when a hit needs no change.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The literal steps of creating, updating, or retiring a node once impact is assessed | `launchpad/docs/corpus/AGENTS.md` |
| How many nodes a new subject should become | `launchpad/docs/corpus/standards/atomicity.md` |
| The syntax for a body-prose pointer | `launchpad/docs/corpus/standards/linking.md` |
| The five relationship types and their exact contract | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Building tooling that automates any part of this search | out of scope per Feature #620's exclusion of "implementation of the knowledge-crate runtime" |
| Concrete procedures for the other agent surfaces under Feature #620 -- ambiguity handling, evidence resolution, documentation creation/update/validation, concept resolution, repository navigation, stale-documentation handling, and corpus usage | sibling tasks under parent Feature #620 -- #640, #642, #643, #644, #645, #646, #647, #648, #650, #651, none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **No real retirement has yet exercised step 6b.** Every merged corpus node
  at the recorded revision carries `status: draft` or `active`; none is
  `deprecated` or `retired`. The retirement fork is grounded in `AGENTS.md`'s
  own text, not in having walked a real retirement end-to-end.
- **Whether `grep` finds every prose mention, versus one that paraphrases a
  node without ever typing its exact `id` string** ("the invariants node," with
  no `id` or filename), was not tested. A mention written that way would not
  surface in step 2, and nothing here proposes a fix for that gap.
- **Whether every sibling `agents/*.md` or `ingestion/*.md` node under Feature
  #620 should, once drafted, declare a relationship toward this one** is each
  sibling's own edit to make, not decided here.
- **No CI run has exercised this node.** All grep and validator evidence above
  is local to this worktree.
