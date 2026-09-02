---
id: agents-documentation-creation
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
  - statement: "AGENTS.md's own 'Scope and omissions' section states, in the paragraph immediately after its 'not covered here' table, 'Until the standards land there is no per-type template to follow: write the node against node.schema.json and the rules above, and expect a later task to reshape it' -- a caveat written before the templates/ catalog existed, and distinct from the numbered 'Creating a node' step 4 ('Choose the id') and step 5 ('Create the file'), which say nothing about templates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md:447"
  - statement: "At this node's recorded revision, launchpad/docs/corpus/templates/ contains 26 template files, every one carrying status: active and origin: launchpad, and every one of the 26 ids resolves as a real node on origin/launchpad -- the per-type template catalog AGENTS.md's own 'Scope and omissions' section anticipated as a future task is now complete."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus/templates) -> architecture-component.md, architecture-container.md, architecture-context.md, capability.md, component.md, concept.md, configuration.md, data-entity.md, datastore.md, decision-reference.md, deployment.md, event-kind.md, flow.md, generated-index.md, glossary-term.md, implementation-reference.md, interface.md, invariant.md, policy.md, procedure.md, reference.md, runbook.md, specification.md, test-contract.md, test-strategy.md, threat-model.md (26 files, all status: active per each file's own front matter)"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- naming the corpus surface a node documents, not the documentation form its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "templates/procedure.md's own 'A note on type' section states this distinction explicitly for the how-to form: 'A node built from this template takes whichever type its subject matter's surface already calls for ... exactly as it would if the same subject were documented in prose instead of as sequenced steps,' naming operations and development as worked examples of surface-driven type choice independent of template."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/concept.md's Boundary section against reference and procedure states the deciding question directly: 'What is it, and how does it relate to what I know' stays a concept; 'What does it require me to do' or 'what exactly does it accept as input' belongs to procedure or reference respectively -- a stated test rather than a subjective impression."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
  - statement: "templates/reference.md's own Boundary section states the mirror-image trap from its side: a reference node that starts numbering steps ('first configure X, then run Y') has stopped being information-oriented and become an unlabelled how-to guide, and explicitly defers formalizing the reference/procedure line to procedure.md's own task rather than resolving it there."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
  - statement: "templates/procedure.md's own 'Note on Definition of Done' section documents that its source issue's DoD checklist was copied verbatim from the standards-track issues (policy/standard language: 'states scope and authority', 'separates MUST from SHOULD', 'defines enforcement ... exception and escalation process') and did not fit a template-shaped node with no MUST/SHOULD normative claims to separate, so the node was built against parent Feature #605's own acceptance-criteria sentence instead of the issue's mismatched checklist."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "Feature #620's acceptance criteria require that 'every node passes corpus schema/graph/provenance validation and uses the assigned template,' that nodes 'name concrete source start points and record evidence from current code/tests/specs/decisions/history appropriate to its claims,' and that 'no broad overview page duplicates canonical claims owned by atomic child nodes; navigation links instead.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, acceptance criteria"
  - statement: "Issue #645's own Definition of Done combines a generic corpus-authoring checklist (one hand-authored document, schema-valid front matter, one independently maintainable idea, traceable evidence, links to neighbors, checked against recorded revision, validation passes) with four how-to-specific bullets: 'States goal, prerequisites and allowed environment/scope,' 'Provides ordered steps that are executable and project-specific,' 'Defines success verification and rollback/cleanup where relevant,' 'Links authoritative commands/config rather than giving generic advice.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#645 definition of done"
  - statement: "Issue #646 is titled 'task: document agents/documentation-update.md' and issue #647 is titled 'task: document agents/documentation-validation.md'; both are children of parent Feature #620 alongside this node's own issue #645, and neither is merged at this node's authoring time."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#646 and launchpad-26/buzz#647 issue titles"
  - statement: "This node's type is agent rather than governance, on the same reasoning AGENTS.md and the sibling agents-invariants node already apply: governance is this corpus's precedent for the templates/ and standards/ meta-documents about documentation form, while agent is the precedent for a node whose subject is a procedure an agent (or a reviewer checking an agent's work) follows when authoring corpus content -- the same surface AGENTS.md itself and agents-invariants.md already document under type: agent."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.75
  - statement: "At this node's recorded revision, launchpad/docs/corpus/agents/ contains only invariants.md besides this node -- none of the other 31 child document tasks under parent Feature #620 (including #646 and #647, built in parallel in the same batch) has merged, so none is a valid relationship target yet."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus/agents) -> invariants.md"
  - statement: "relationships.schema.json states implements' directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)' and references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "AGENTS.md's own 'Creating a node' step 9 requires relationship targets to be checked against the branch being merged into (e.g. git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus), not the author's own worktree, because the checker loads whatever is present where it runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: corpus-template-concept
  - type: references
    target: corpus-template-reference
---

# Creating a new corpus node: how-to

How to create a new `launchpad/docs/corpus/` node today, now that the templates/
catalog is complete: choosing the node's `type` from the corpus-surface enum,
separately choosing which of the 26 templates fits the content's *form*, and
reconciling a task issue's Definition of Done when it does not perfectly match the
chosen template's required sections. This node supersedes the stale caveat in
`AGENTS.md`'s own "Scope and omissions" section -- written when "there is no
per-type template to follow" was still true -- without restating the rest of that
procedure, including its numbered "Creating a node" steps, which this node cites
by number instead.

## Before you start

- Read `AGENTS.md` once, in full. This node cites nine of its ten numbered
  "Creating a node" steps by number rather than reproducing their text (this
  node's steps 1, 2, 5, 6, 7, 8, 9 each cite one or more of AGENTS.md's steps
  1-2, 3, 4-5, 6-7, 8, 9, 10 respectively); skipping `AGENTS.md` means missing
  what those citations point to.
- Have `git` access to the branch you are merging into (usually `origin/launchpad`),
  so template ids and any relationship target can be confirmed to resolve there
  rather than only in your own worktree.
- Know your task's own issue number and its Definition of Done -- it is the spec for
  what "done" means for your node, not the parent Feature's acceptance criteria
  restated below for context only.

## Choose the type, choose the template, write the node

1. **Confirm the node is one idea and that nothing already covers it.**
   `AGENTS.md`'s "Creating a node" steps 1-2 govern this unchanged; this node adds
   nothing to them.
2. **Record what you inspect before drafting** -- revision, source paths, tests,
   specs, and anything expected but unverifiable -- per `AGENTS.md`'s step 3. Its own
   table of where each category ends up in the finished node still applies.
3. **Choose the node's `type` from the corpus-surface it documents, independent of
   any template decision you make later.** `node.schema.json`'s thirteen-member
   `type` enum names *what the node is about* -- `architecture`, `layers`,
   `capabilities`, `platforms`, `implementation`, `interfaces-events`,
   `verification`, `operations`, `development`, `release`, `governance`, `agent`,
   `ingestion` -- never the shape its prose takes. `templates/procedure.md`'s own
   "A note on `type`" section states this explicitly for the how-to form: a node
   built from any template "takes whichever `type` its subject matter's surface
   already calls for," naming `operations` for a how-to on rotating a credential
   and `development` for a how-to on adding an event kind as its own worked
   examples. The same independence holds in the other direction: this node's
   subject is an agent-facing procedure, so it takes `type: agent` -- the same
   surface `AGENTS.md` and the sibling `agents-invariants` node already document
   under that value, as distinct from `governance`, this corpus's precedent for the
   `templates/` and `standards/` meta-documents about documentation form itself.
   **Decide `type` first, and do not let template choice leak into it** -- a
   how-to-shaped node about a `capabilities` subject is still `type: capabilities`.
4. **Choose the template by matching the content's form, using each candidate
   template's own Boundary section rather than a first impression.** Every one of
   the 26 templates under `launchpad/docs/corpus/templates/` states, in its own
   words, what it is not and where the reader should go instead -- read the
   candidate's Boundary (or "what this template is not") section before drafting,
   not just its opening paragraph. Two worked examples, because guessing from a
   template's name alone is exactly the failure mode these sections exist to
   prevent:
   - `templates/concept.md`'s Boundary names the deciding question directly:
     *"What is it, and how does it relate to what I know"* stays a concept guide;
     *"What does it require me to do"* belongs to `procedure.md` instead, and
     *"what exactly does it accept as input"* belongs to `reference.md` instead.
   - `templates/reference.md`'s own Boundary states the same edge from its side --
     a reference node that starts numbering steps ("first configure X, then run
     Y") has stopped being information-oriented and become an unlabelled how-to
     guide -- and explicitly leaves formalizing that exact line to
     `templates/procedure.md`'s own task rather than resolving it on its own side.
     Two templates deliberately describing the same boundary from opposite
     directions, without either claiming to be the authority on it, is the normal
     shape of this catalog, not a gap to close.

   If a candidate's Boundary section routes you to a different template, follow it
   -- that redirection is the template catalog doing its job, not a sign you chose
   wrong to begin with.
5. **Choose the `id` and create the file**, per `AGENTS.md`'s steps 4-5: kebab-case,
   permanent from assignment, anywhere under `launchpad/docs/corpus/` except
   `schema/`.
6. **Write the front matter and one evidence entry per substantive claim**, per
   `AGENTS.md`'s steps 6-7: a commit citation for the revision from step 2 above,
   `FACT` only for sources actually opened, `INFERENCE` with `confidence` for
   reasoned claims, `TEAM_KNOWLEDGE` with `provided_by` for uncorroborated
   attribution.
7. **Write the body to the chosen template's required sections**, which subsumes
   `AGENTS.md`'s step 8 requirement to structure the body for lookup with a scope
   section -- every template's own "Scope and omissions" section satisfies it.
   Reconcile any mismatch between your task issue's Definition of Done and what
   the template actually requires. See *Note on Definition of Done* below for how
   this node itself resolved that question, and for the general principle: build
   against the real acceptance criteria, not a checklist copied from an unrelated
   document shape.
8. **Add relationships only to nodes that already exist on the branch you are
   merging into**, per `AGENTS.md`'s step 9 -- check with `git ls-tree -r
   --name-only origin/launchpad -- launchpad/docs/corpus`, not your own worktree.
   A node built from any template should, at minimum, declare `implements` toward
   its chosen `corpus-template-*` id once that id is confirmed present -- per
   `relationships.schema.json`'s own worked example for `implements`, "a template
   instance of a standard." Declaring none is valid when nothing else resolves; it
   is not valid to skip checking and assume nothing does.
9. **Run the check and iterate**, per `AGENTS.md`'s step 10:
   `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
   root, fixing what it names until it exits 0. For what a passing run does and
   does not establish, and for how to interpret its output in more depth than this
   step covers, see the sibling procedure this node hands off to below.

## See also

- `launchpad/docs/corpus/AGENTS.md` -- the full create/update/retire procedure this
  node's steps 1, 2, 5, 6, 7, 8, 9 cite by number rather than restate (this node's
  own steps 3-4 are new content, not citations -- see *Boundary* below).
- `launchpad/docs/corpus/agents/invariants.md` -- the binding invariants (I1-I10)
  a node created via this procedure must still satisfy; this node states *how* to
  create one, that node states what must hold true of the result.
- `launchpad/docs/corpus/templates/*.md` -- the 26-template catalog itself; read
  the candidate's Boundary section before committing to it, per step 4 above.
- The sibling procedure for validating a drafted node and interpreting
  `validate.py`'s output in depth (task: document `agents/documentation-validation.md`,
  issue #647, not merged at this node's authoring time) -- this node's step 9 hands
  off there rather than duplicating it.

## Boundary

This node does not describe:
- **Updating an existing corpus node.** That is a distinct procedure with its own
  re-verification and revision-movement questions (task: document
  `agents/documentation-update.md`, issue #646, not merged at this node's authoring
  time) -- not a variation on the steps above.
- **Running or interpreting `validate.py` in depth**, beyond the single command
  named in step 9. What a passing run does and does not establish is its own
  procedure (task: document `agents/documentation-validation.md`, issue #647, not
  merged at this node's authoring time), and this node defers to it rather than
  restating `AGENTS.md`'s own "Three things a passing run does not mean" section a
  third time.
- **`AGENTS.md`'s full authoring procedure**, which this node cites by number
  rather than reproduces -- `AGENTS.md` remains the sole authority for all ten of
  its own numbered "Creating a node" steps. This node's steps 1, 2, 5, 6, 7, 8, 9
  each cite one or more of them (AGENTS.md steps 1-2, 3, 4-5, 6-7, 8, 9, 10
  respectively); this node's only genuinely new content is `type`-versus-template
  reasoning (this node's own steps 3-4) and the Definition-of-Done reconciliation
  folded into this node's step 7 (see below).
- **A newcomer's introduction to the corpus** -- this is Diátaxis's how-to form for
  a reader who already knows what a corpus node is and wants to create one
  correctly, not a tutorial teaching the concept from scratch.
- **Which per-type template is correct for any specific subject not discussed
  above.** Only two worked examples (concept vs. procedure vs. reference) are
  given in step 4; the remaining 23 templates are not individually walked through
  here, on the same "practical usability over completeness" principle
  `templates/procedure.md` itself states for a how-to guide. Read the candidate's
  own Boundary section for any template not named above.

## Relationships

Declared: `depends-on: corpus-agents` -- this node's own authority for its steps
1, 2, 5, 6, 7, 8, 9 above (each citing AGENTS.md's own numbered steps, per
*Boundary* above) is derived from `AGENTS.md`, not original to itself. `implements:
corpus-template-procedure` -- this node is a how-to-shaped instance of that
template, per `relationships.schema.json`'s own worked example for `implements`.
`references: corpus-template-concept` and `references: corpus-template-reference` --
both cited above as the worked examples for step 4's boundary-reading technique;
`references`' directionality ("source cites target as supporting context; no
ownership or currency dependency implied") fits a citation used as a worked example
rather than a structural dependency.

Checked and deliberately not declared: `agents-invariants` (cited in prose above as
a companion node, but this node makes no claim that depends on its content holding),
and the sibling tasks `agents/documentation-update.md` (#646) and
`agents/documentation-validation.md` (#647) -- both discussed above by title only,
and neither resolves as a node id on `origin/launchpad` at this node's authoring
time, per `AGENTS.md`'s own step-9 rule against targeting a worktree-only node.

## Note on Definition of Done

Issue #645's Definition of Done is not the same shape as the mismatch
`templates/procedure.md`'s own "Note on Definition of Done" section describes for
its source issue (#1345): that issue's checklist was copied verbatim from the
standards/policy-track issues -- "states scope and authority," "separates MUST from
SHOULD," "defines enforcement ... exception and escalation process" -- language with
no fit at all for a template-shaped node carrying no MUST/SHOULD normative claims to
separate. Issue #645's checklist is smaller and closer to the mark: its first seven
bullets are the generic corpus-authoring boilerplate this batch's tasks share (one
hand-authored document, schema-valid front matter, one independently maintainable
idea, traceable evidence, links to neighbors, checked against recorded revision,
validation passes) -- genuinely true of every corpus node regardless of shape, so
not a mismatch to reconcile -- and its remaining four bullets ("states goal,
prerequisites and scope," "ordered executable steps," "success verification and
rollback/cleanup where relevant," "links authoritative commands") map directly onto
`templates/procedure.md`'s own required sections (Overview, Before you start, the
numbered task sequence, and citing real commands throughout).

The one genuine gap: `templates/procedure.md` does not mandate a dedicated
"rollback/cleanup" section, only that a task sequence run "through to the task's
completion or verification." This node's own rollback is folded into its
Boundary/Relationships sections rather than given a heading of its own: creating a
node has no state to roll back beyond the file and the commit that added it, so
"rollback" here means deleting the uncommitted file or reverting the local commit --
stated once, here, rather than manufacturing a numbered rollback step that would
repeat it. The general principle this node draws from `procedure.md`'s own
precedent: build against the template's real required sections and the parent
Feature's real acceptance criteria, and name a checklist bullet that does not fit as
a small, explained gap -- not as license to skip the bullet, and not as grounds to
invent a bigger mismatch than the one that is actually there.

## Scope and omissions

**This node covers** how to create a new `launchpad/docs/corpus/` node today: how to
choose its `type` from the corpus-surface enum independent of any template
decision, how to choose which of the 26 templates fits the content's form using
each candidate's own Boundary section, and how to reconcile a task issue's
Definition of Done against a chosen template's real required sections rather than
against generic or mismatched boilerplate.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Updating an existing corpus node | `agents/documentation-update.md`, issue #646, not merged |
| Running or interpreting `validate.py` in depth | `agents/documentation-validation.md`, issue #647, not merged |
| The full authoring/updating/retiring procedure this node's steps cite by number | `launchpad/docs/corpus/AGENTS.md` |
| The binding invariants a created node must still satisfy | `launchpad/docs/corpus/agents/invariants.md` |
| Per-template required sections for the 23 templates not walked through in step 4 | each template's own file under `launchpad/docs/corpus/templates/` |
| Whether a recorded revision may stay put across a later edit | `AGENTS.md`'s own "Updating a node" section notes this is unsettled, owned by #1321 |

**Expected but not verified when this node was written:**

- **No node has yet been authored by following this procedure end to end**,
  because this node is itself the first attempt at the type-then-template
  sequence it describes. Whether the two-step ordering (type first, template
  second) holds up cleanly for a subject where the two pulls in different
  directions -- e.g. a `governance`-surfaced subject that is also how-to-shaped --
  was not tested against a real case.
- **Whether issues #646 and #647, once drafted, will declare a relationship back
  toward this node** is their own edit to make, not decided here.
- **Whether every one of the 26 templates' own Boundary sections was read in
  full** -- only `procedure.md`, `concept.md`, and `reference.md` were opened and
  quoted directly above; the remaining 23 were confirmed to exist and to carry
  `status: active` via the directory listing, not individually read for this
  node's evidence ledger.
