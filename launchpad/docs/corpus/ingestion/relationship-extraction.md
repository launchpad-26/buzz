---
id: ingestion-relationship-extraction
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
  - statement: "node.schema.json requires id, type, status, origin, audiences and evidence, permits relationships as the only other property, and rejects any field beyond those seven; its type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- described as reusing 'PRD #602's own enumerated list of in-scope surfaces, reused here rather than a second, independently invented taxonomy.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "relationships.schema.json defines exactly five relationship types with this directionality and inverse metadata: depends-on -- 'source requires target to be true/current for source's own claims to hold' (generated inverse depended-on-by); supersedes -- 'source replaces target; target becomes historical' (generated inverse superseded-by); implements -- 'source is the concrete realization of target (e.g. a template instance of a standard)' (generated inverse implemented-by); references -- 'source cites target as supporting context; no ownership or currency dependency implied' (authored inverse referenced-by -- the only one of the five whose inverse is authored rather than generated); part-of -- 'source is a constituent section/child of target' (generated inverse has-part)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "AGENTS.md states: \"'There was nothing to point at' was true when this was the corpus's only node and stops being true the moment a second one merges. Enumerate what exists (ls launchpad/docs/corpus/**/*.md) and give the real reason... Two independent agents authoring sibling nodes copied an earlier version of this paragraph and produced a false justification from it, because it read as a general rule rather than a fact about one moment.\""
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's 'Creating a node' step 9 requires relationship targets to be checked against the branch being merged into (e.g. git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus), not the author's own worktree, because 'the checker loads whatever is present where it runs.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "standards/review-requirements.md's own reviewer MUST 6 states: 'A reviewer MUST confirm a relationship's declared type matches its real-world direction, using relationships.schema.json's relationshipMeta block. The schema enforces only that type is one of five enum members and that target names a real node id; it does not, and by its own description cannot, confirm that a supersedes or depends-on edge is actually true in that direction. A node declaring type: supersedes at a target it does not, in fact, replace passes validation cleanly.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/review-requirements.md"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no ingestion/ directory at all, and no file under agents/ besides invariants.md -- so no sibling document task under parent Feature #620 besides #649 (agents/invariants.md, merged) is a valid relationship target for this node."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> agents/invariants.md present; no other agents/*.md; no ingestion/ directory; run at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Two merged corpus nodes declare a real part-of edge: layers/configuration/relay-configuration.md declares part-of: architecture-containers-relay, reasoning in its own evidence ledger that 'architecture-containers-relay (a merged node) already treats crates/buzz-relay/src/config.rs as core evidence for the relay container's own description... making it the natural part-of target for a node that documents that same file's settings in full'; layers/compute/sprig-runtime.md declares part-of: architecture-containers-agent-runtime for the same whole-to-part reason. Both were opened directly."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/configuration/relay-configuration.md"
      - "launchpad/docs/corpus/layers/compute/sprig-runtime.md"
  - statement: "A search across the merged corpus (grep -rc \"^  - type: implements\" launchpad/docs/corpus, excluding schema/) returns implements declared by 17 capability, layer, agent and configuration nodes toward their own template's id (for example moderation-authorization.md, push-capability.md, huddle.md, community-discovery.md, media.md, workflow-channel.md, agents/invariants.md, and every layers/configuration/*.md node), and a parallel search for references (grep -rn \"type: (depends-on|supersedes|implements|references|part-of)\" launchpad/docs/corpus, excluding schema/fixtures) shows it as the large majority of all declared edges corpus-wide -- both far more numerous than depends-on, part-of or supersedes."
    entry_class: FACT
    evidence:
      - "grep(pattern='^  - type: implements', scope='launchpad/docs/corpus/**/*.md', excluding='schema/') -> 17 matches, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
      - "grep(pattern='type: (depends-on|supersedes|implements|references|part-of)', scope='launchpad/docs/corpus/**/*.md', excluding='schema/fixtures') -> references and implements are the two most frequent types by a wide margin, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "agents-invariants (the one merged sibling in this node's own Feature #620 family) declares depends-on: corpus-agents, reasoning in its own evidence ledger that 'this node's own authority is derived from AGENTS.md, not original to itself'; standards/evidence.md, standards/documentation-standard.md and templates/decision-reference.md each declare the same type toward a target their own body restates or is built directly on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
      - "launchpad/docs/corpus/standards/evidence.md"
      - "launchpad/docs/corpus/standards/documentation-standard.md"
      - "launchpad/docs/corpus/templates/decision-reference.md"
  - statement: "No merged corpus node currently declares type: supersedes -- a grep for the literal string across launchpad/docs/corpus (excluding schema/fixtures and schema/relationships.schema.json/README.md's own enum listings) returns zero hits as a declared relationships[] entry; every other hit is prose discussion in AGENTS.md, standards/atomicity.md, standards/deprecation.md, standards/linking.md, or a template's own evidence-ledger restatement of the five-type enum."
    entry_class: FACT
    evidence:
      - "grep(pattern='type: supersedes', scope='launchpad/docs/corpus/**/*.md') -> zero matches as a declared relationships[] entry, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "standards/deprecation.md states: 'supersedes declares that the source replaces the target and the target becomes historical' and 'supersedes carries a generated rather than an authored inverse... so a replaced node cannot declare the reverse edge itself,' and separately, on retirement: 'The direction is fixed: the source replaces the target. The retired node cannot declare the reverse.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/deprecation.md"
  - statement: "templates/procedure.md's own Relationships section states a how-to-shaped instance node 'should declare implements targeting corpus-template-procedure (this node's id) once this node is merged,' naming relationships.schema.json's own worked example for implements -- 'a template instance of a standard' -- as the reason, 'not the weaker references edge.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/reference.md quotes Diátaxis directly: 'Reference material is information-oriented' and, although reference 'should not attempt to show how to perform tasks', it 'can and often needs to include a description of how something works or the correct way to use it' -- and its own Scope and authority section separately names 'procedure/how-to (#1345, not in this batch)' as a neighboring form it does not cover."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
  - statement: "templates/concept.md states in its own boundary discussion: 'If a concept draft starts numbering steps for the reader to perform, that content belongs in a procedure node instead (issue #1345's template, not this one).'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
  - statement: "standards/atomicity.md states its own governed question verbatim as 'given a subject you are about to document, is it one node or more than one?' -- a question about node count, not about which typed edge connects two already-decided nodes -- and its Boundary case F states that part-of 'is a description of a structure that already exists, never a licence to create one,' warning specifically against using it to split a single idea into sections."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "standards/linking.md's own Scope and authority section states it governs 'how body prose points a reader at something else,' explicitly distinct from the relationships[].target field's own contract, and its MUST 6 states: 'A relationships[] edge MUST NOT stand in for a body-prose mention when the connection matters to a reader following the argument, and a body-prose mention MUST NOT stand in for a relationships[] edge when the connection is one of the five typed kinds and resolves against the branch this change will merge into.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/linking.md"
  - statement: "agents/concept-resolution.md's (issue #642, unmerged at this node's authoring time) own Scope and omissions table names, as a gap it does not cover: 'How an ingestion-side agent (drawing evidence from a specific source type -- git history, CI, issues, PRs) should apply this same resolution question to ingested claims rather than to whole candidate nodes,' assigning it to 'the ingestion/*.md document family under Feature #620' -- the family this node belongs to."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#642 (unmerged node body, read from worktree __worktrees/task-642-agents-concept-resolution/launchpad/docs/corpus/agents/concept-resolution.md)"
  - statement: "Issue #968's Objective states: 'Create launchpad/docs/corpus/ingestion/relationship-extraction.md as the single canonical procedure node for relationship extraction,' and its Definition of Done requires schema-valid front matter with typed relationships appropriate to the node, one independently maintainable idea with any second concept filed separately, every substantive claim traceable to an opened source with FACT/INFERENCE/TEAM_KNOWLEDGE not conflated, links to relevant nodes without duplicating their canonical content, and a clean local validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#968 body, Objective and Definition of done sections"
  - statement: "Parent Feature #620's Acceptance criteria require every node to pass corpus schema/graph/provenance validation and use the assigned template, name concrete source start points, record evidence appropriate to its claims, avoid duplicating canonical claims owned by other atomic nodes, and let an independent reader traverse corpus nodes to implementation and verification evidence; its Out of scope section excludes 'implementation of the knowledge-crate runtime.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, Acceptance criteria and Out of scope sections"
  - statement: "This node's type is ingestion rather than agent, on the reasoning that node.schema.json's ingestion enum member names a corpus surface distinct from agent, and this node's subject -- correctly typing an edge while drafting or ingesting evidence for any corpus node, not the agent-facing authoring invariants AGENTS.md and agents-invariants already occupy -- matches the file's own ingestion/ path family rather than the agents/ one. No merged node currently uses type: ingestion, so there is no prior sibling's precedent to check consistency against, unlike agents-invariants' own type: agent choice, which had AGENTS.md itself as a direct precedent."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.7
  - statement: "Ordering the five diagnostic tests as supersedes, part-of, implements, depends-on, references (rather than any other order) follows from three properties visible in the schema text and worked examples above: supersedes and part-of are the narrowest and most structurally distinctive (replacement-with-historical-target; whole-to-part containment already reflected in the target's own scope), so testing them first resolves the clearest cases fastest and avoids miscategorizing a genuine containment or replacement as the weaker implements/depends-on/references; implements and depends-on are the pair most likely to be confused with each other (both involve the source's authority tracing to the target), and are distinguished by whether the target is specifically a template/standard the source instances (implements) or not (depends-on); references is the correct default precisely because its directionality explicitly disclaims 'no ownership or currency dependency,' the weakest and therefore safest claim to fall back to when none of the first four decisively fit."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/standards/review-requirements.md"
    confidence: 0.8
  - statement: "This node's own question -- given a connection already recognized as real between two known nodes, which of the five types correctly describes it -- is genuinely distinct from agents-concept-resolution's question -- whether a whole candidate node duplicates an existing one under a different name -- because the two operate on different objects (an edge between two settled nodes, versus a not-yet-settled candidate node itself) and can be run in either order without one making the other unnecessary: a candidate node can pass concept-resolution as genuinely new and still need every one of its outbound edges typed correctly, and an edge between two already-existing, already-resolved nodes can still be mistyped regardless of how either node was resolved."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.85
relationships:
  - type: references
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-atomicity
  - type: references
    target: corpus-standard-linking
  - type: references
    target: corpus-standard-review-requirements
  - type: references
    target: corpus-template-reference
  - type: references
    target: corpus-template-concept
  - type: implements
    target: corpus-template-procedure
---

# Relationship extraction: how-to

Given a connection you have already noticed between the corpus node you are
drafting and another node, decide which one of `relationships.schema.json`'s five
typed edges — not whether a connection exists at all — honestly describes it,
before writing the `relationships[]` entry.

## Before you start

- The candidate target's `id`, confirmed to exist among the nodes on the branch
  this change will merge into (`git fetch origin launchpad && git ls-tree -r
  --name-only origin/launchpad -- launchpad/docs/corpus`), per `AGENTS.md`'s own
  step 9 rule — not your own worktree.
- A one-sentence statement of *why* the source and target are connected: which
  claim in the node you are drafting depends on, replaces, instantiates, cites,
  or is a part of, which claim in the target. Skipping this and jumping straight
  to a type risks fitting the connection to whichever type is easiest to write,
  instead of the reverse.
- Confirmation that you actually enumerated the merge-target tree rather than
  assumed there was nothing to relate to. `AGENTS.md` documents this exact
  failure by name: "'There was nothing to point at' was true when this was the
  corpus's only node and stops being true the moment a second one merges...
  Two independent agents authoring sibling nodes copied an earlier version of
  this paragraph and produced a false justification from it, because it read as
  a general rule rather than a fact about one moment." This node assumes that
  enumeration has already happened and a real candidate connection has already
  been noticed — it starts one question later, at *which type applies*, not
  *whether any type applies*.

## Choose the relationship type

Run these five tests in order, against `relationships.schema.json`'s own
directionality text. Stop at the first one that clearly fits. Do not force a fit
if none does — declaring no relationship is always valid once the enumeration
above has actually happened.

Each test below quotes `relationshipMeta`'s directionality and inverse text
verbatim rather than only linking to it. This is a deliberate, narrow
exception to `standards/linking.md`'s MUST 5 (no duplicated enumerations):
the operative sentence is exactly what each test applies, is one line long,
and this procedure's value is letting an author run all five tests without
switching files mid-decision — the same self-containment carve-out
`standards/linking.md` itself describes for a MUST that cannot omit a
target's own exact rule. It is not exempt from drift for being justified: if
`relationships.schema.json`'s `relationshipMeta` wording ever changes, every
quoted line below must be re-checked against it before this node is trusted
again.

1. **Does the source specifically exist to replace the target, so the target's
   own claims should be read as historical from this point on?** This is
   `supersedes` — schema text: "source replaces target; target becomes
   historical" (inverse `superseded-by`, generated). Test this first: it is the
   narrowest test and the most consequential to get wrong, in either direction.
   `standards/deprecation.md` states the direction is fixed — "the retired node
   cannot declare the reverse" — and `standards/review-requirements.md`'s
   reviewer MUST 6 names this exact type as one the schema "does not, and by its
   own description cannot, confirm... is actually true in that direction": a
   node declaring `supersedes` at a target it does not actually replace passes
   validation cleanly. **No merged corpus node currently declares this type** —
   checked by grep, zero hits outside prose discussion — so this test is
   grounded in schema text and `AGENTS.md`'s retirement procedure, not in a
   worked instance.
2. **Is the source a constituent section or child the target's own body would
   legitimately claim as one of its parts — not merely a topically related
   node, but one whose existence the target's own scope is already responsible
   for?** This is `part-of` — schema text: "source is a constituent
   section/child of target" (inverse `has-part`, generated). Two real merged
   instances show the shape: `layers/configuration/relay-configuration.md`
   declares `part-of: architecture-containers-relay` because it catalogues one
   container's own configuration surface in full, something the container node
   already treats as its own subject matter; `layers/compute/sprig-runtime.md`
   declares `part-of: architecture-containers-agent-runtime` for the identical
   reason. `standards/atomicity.md`'s own boundary case F is the corresponding
   trap: `part-of` "is a description of a structure that already exists, never
   a licence to create one" — do not reach for it to justify splitting one idea
   into sections that did not already exist as sections.
3. **Is the target itself a template, standard, or schema-shaped prescription,
   and is the source the concrete instance that realizes it?** This is
   `implements` — schema text: "source is the concrete realization of target
   (e.g. a template instance of a standard)" (inverse `implemented-by`,
   generated). This is the most common non-`references` edge in the corpus by a
   wide margin — 17 capability, layer, agent and configuration nodes each
   declare `implements` toward the template they were drafted from — and
   `templates/procedure.md` states the rule for its own family directly: a node
   built from it "should declare `implements` targeting
   `corpus-template-procedure`... once this node is merged." Do not reach for
   `depends-on` here merely because the source's authority also traces to the
   target — if the target is a template or standard and the source is a
   filled-in instance of it, `implements` is the more specific and more honest
   type.
4. **Setting the template-instance framing of test 3 aside, would the target
   becoming false, retired, or materially different make one of the source's
   own stated claims stop holding?** This is `depends-on` — schema text:
   "source requires target to be true/current for source's own claims to hold"
   (inverse `depended-on-by`, generated). `agents-invariants` — the one merged
   sibling in this node's own Feature #620 family — declares `depends-on:
   corpus-agents` on exactly this reasoning: "this node's own authority is
   derived from `AGENTS.md`, not original to itself." `standards/evidence.md`,
   `standards/documentation-standard.md` and `templates/decision-reference.md`
   each declare the same type for the identical reason: the source restates or
   is built directly on the target's own rule, not merely informed by it in
   passing.
5. **Otherwise: does the source cite the target only as supporting context,
   with no ownership or currency dependency implied?** This is `references` —
   schema text: "source cites target as supporting context; no ownership or
   currency dependency implied" (the only one of the five whose inverse,
   `referenced-by`, is authored rather than generated — the corpus never
   auto-derives the backward pointer, because nothing about a `references` edge
   forces one to exist). This is the correct default when tests 1-4 do not
   decisively fit, and it is also the large majority of edges actually declared
   in the corpus today. Reaching for one of the stronger four types when
   `references` is the honest answer overstates the connection — and, per
   `review-requirements.md` MUST 6 again, a reviewer has no mechanical way to
   catch that overstatement after the fact.

**If two tests both seem to fit**, stop and record the tension rather than
picking silently — the same author-records/reviewer-decides pattern
`standards/atomicity.md`'s own *Exceptions and escalation* uses for a disputed
node-count call, applied here to a disputed edge-type call instead. A repeated
disagreement over the same pair of types is a defect in this procedure's own
test ordering, not a one-off judgement call, and should be filed as an issue
against this node.

## See also

- `corpus-agents` (`AGENTS.md`) — the enumeration discipline this node's
  *Before you start* section assumes has already run.
- `agents-concept-resolution` (#642, unmerged at this node's authoring time) —
  the adjacent, upstream question: whether the candidate *node* is new at all,
  asked before this node's question about typing a *connection* is even
  reachable.
- `corpus-standard-atomicity` — the node-count question, a different axis
  entirely from edge-typing.
- `corpus-standard-linking` — once a type is chosen here, the body-prose
  syntax for the corresponding pointer, and when a `relationships[]` edge is
  required versus optional.
- `corpus-standard-review-requirements` — MUST 6, the reviewer-side mirror of
  this node's authoring-time concern.
- `relationships.schema.json` — the authoritative source for all five types'
  directionality and inverse metadata this whole procedure is built from.

## Boundary

Per `templates/procedure.md`'s own required Boundary checklist for a how-to-shaped
instance, this node is not:

- **A reference node.** It is not an information-oriented lookup table of what
  the five types mean in isolation — `relationships.schema.json` and
  `schema/README.md` already own that lookup, and this node cites rather than
  restates it. Diátaxis states reference material "should not attempt to show
  how to perform tasks," and choosing a type for one specific real connection
  is exactly a task.
- **A tutorial.** It assumes the reader already knows how to author a corpus
  node and already has a specific candidate connection in hand; it does not
  teach corpus authorship from scratch.
- **A concept/explanation node.** It does not discursively explain why the
  corpus has five relationship types or the design history behind
  `relationships.schema.json` — `templates/concept.md`'s own words describe
  that as belonging to a concept node instead, stating directly that "if a
  concept draft starts numbering steps for the reader to perform, that content
  belongs in a procedure node instead." This node numbers steps, so it is not
  that.

This node also does not describe:

- **Whether the candidate subject is a duplicate of an existing node.** That is
  `agents-concept-resolution`'s (#642) own question, asked one step earlier and
  about a different object — a whole candidate *node*, not a *connection*
  between two nodes already known to exist. #642's own Scope and omissions
  table names this exact gap and assigns it to "the `ingestion/*.md` document
  family," which this node is part of.
- **How many nodes a subject becomes.** `standards/atomicity.md`'s five-test
  procedure answers that, on a different axis (node count, not edge type),
  before this node's question is even reachable.
- **The syntax for writing the resulting body-prose pointer, or when a
  `relationships[]` edge is required versus optional.** `standards/linking.md`
  owns both, once a type has been chosen here.
- **Reassessing an edge's type or currency after something it points at
  changes.** That is the sibling family's change-impact-analysis question
  (drafted as #641, unmerged at this node's authoring time), asked about an
  edge that already exists; this node is asked once, at drafting time, about
  an edge that does not yet exist.
- **Whether a relationship-shaped connection exists at all**, as distinct from
  which type it is. `AGENTS.md`'s own enumeration trap governs the former;
  this node assumes that question has already been answered "yes" and a
  specific candidate target is already in hand.

## Relationships

- **references: `corpus-agents`.** This node's *Before you start* section
  assumes, and directly quotes, `AGENTS.md`'s own documented enumeration trap —
  supporting context, not a claim whose currency this node's own tests depend
  on.
- **depends-on: `corpus-standard-atomicity`.** Test 2 above states
  `standards/atomicity.md`'s boundary case F — `part-of` "is a description of
  a structure that already exists, never a licence to create one" — as this
  node's own operative warning against misusing `part-of`, not as background
  colour. Applying this node's own test 4 criterion to this edge: if case F
  were retired or materially changed, test 2's stated warning above would stop
  holding — which is `depends-on`'s own directionality ("source requires
  target to be true/current for source's own claims to hold"), not
  `references`'s ("no ownership or currency dependency implied"). This edge
  was typed `references` in an earlier draft and retyped to `depends-on` on
  review, on exactly this reasoning. It is also cited in *Boundary* as the
  adjacent node-count question this node's own edge-type question is not.
- **references: `corpus-standard-linking`.** Cited in *Boundary* and *See
  also* as the next step once a type is chosen here — the body-prose syntax
  and the `relationships[]`-versus-prose question this node's own five tests do
  not answer.
- **references: `corpus-standard-review-requirements`.** MUST 6's exact
  wording — that the schema "does not, and by its own description cannot,
  confirm that a `supersedes` or `depends-on` edge is actually true in that
  direction" — is the direct textual justification, quoted twice above, for
  why this authoring-time procedure needs to exist at all rather than trusting
  review or the checker to catch a mistyped edge after the fact.
- **references: `corpus-template-reference`.** Its own Diátaxis quote —
  reference material "should not attempt to show how to perform tasks" — is
  used directly in *Boundary* above to argue this node is not reference-shaped.
- **references: `corpus-template-concept`.** Its own stated boundary — "if a
  concept draft starts numbering steps for the reader to perform, that content
  belongs in a procedure node instead" — is quoted directly in *Boundary*
  above, from the concept side, to argue the same point from its side.
- **implements: `corpus-template-procedure`.** Per that template's own
  guidance, a how-to-shaped instance node "should declare `implements`
  targeting `corpus-template-procedure`... once this node is merged" — and per
  `relationships.schema.json`'s own worked example for `implements`, "a
  template instance of a standard," which is exactly this case.

**Checked, not assumed.** All seven targets above were confirmed present on
`origin/launchpad`'s corpus tree (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`, at the revision this node's provenance entry records)
immediately before finalizing this front matter. **No edge to
`agents-concept-resolution` (#642) or `agents-change-impact-analysis` (#641)**,
both discussed by name in *Boundary* and *See also* above: neither is merged at
this node's authoring time, so neither is a valid `relationships[].target` — the
same reasoning `agents-invariants`, `agents-concept-resolution` and
`agents-change-impact-analysis` each independently recorded for themselves
against the same unmerged sibling family. **No `type: supersedes` edge is
declared anywhere in this node's own front matter**, consistent with test 1
above: nothing this node says replaces an existing target.

## Scope and omissions

**This node covers** the decision procedure an agent runs, once a genuine
candidate connection between the node being authored and an existing node has
already been noticed, to determine which one of `relationships.schema.json`'s
five typed edges honestly describes it: five ordered tests keyed to each type's
own directionality text, a worked merged example for four of the five types
(the corpus has none yet for `supersedes`), and the escalation path for a
genuinely disputed call between two candidate types.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Whether a candidate connection or a candidate node is a duplicate of something that already exists | `agents-concept-resolution` (#642, unmerged at this node's authoring time) |
| How many nodes a subject becomes | `corpus-standard-atomicity` |
| The body-prose syntax for the pointer once a type is chosen, and when a `relationships[]` edge is required versus optional | `corpus-standard-linking` |
| Reassessing an existing edge's type or currency after something it points at changes | `agents-change-impact-analysis` (#641, unmerged at this node's authoring time) |
| The five types' full authoritative contract (enum, inverse names, generated-vs-authored inverse) | `relationships.schema.json` |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Concrete agent procedures for the other agent/ingestion surfaces under Feature #620 -- ambiguity handling, evidence resolution, documentation creation/update/validation, repository navigation, stale-documentation handling, corpus usage, and the rest of the `ingestion/*.md` family | sibling tasks under parent Feature #620 (#640, #643-#648, #650-#651, #953-#967, #969-#972) -- none merged at this node's authoring time |

**Expected but not verified when this node was written:**

- **No real relationship has yet been typed using this procedure.** Every test
  above is derived from `relationships.schema.json`'s own directionality text
  and from worked examples already merged into the corpus for four of the five
  types — not from having applied the five-test sequence to a brand-new
  candidate connection end to end. The first real use is what actually tests
  whether the ordering (supersedes, part-of, implements, depends-on,
  references) resolves cases decisively or needs revision.
- **Whether `supersedes` is simply rare so far, or whether its test above
  needs revision once a real retirement happens.** No merged node currently
  declares it; the retirement flow it belongs to (`AGENTS.md`'s *Retiring a
  node*) has not yet been exercised on a real corpus node, so this node's test
  1 is grounded in schema text and prose discussion, not in a worked merged
  instance.
- **Whether the same-connection, two-candidate-types ambiguity this node's
  escalation path anticipates will actually occur**, and how often, was not
  tested — only reasoned by analogy to `standards/atomicity.md`'s own
  disputed-granularity escalation for a different axis of the same kind of
  judgement call.
- **Whether this node's own `type: ingestion` is the precedent later
  `ingestion/*.md` siblings should follow**, or whether the corpus surface this
  family occupies should instead be `type: agent` like `AGENTS.md` and
  `agents-invariants` — this is the first node under Feature #620 to use the
  `ingestion` enum member, so there is no prior sibling to check consistency
  against.
