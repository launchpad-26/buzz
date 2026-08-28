---
id: corpus-template-procedure
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template, policy, or procedure; the enum names the corpus surface a node documents, not the documentation form (tutorial/how-to/reference/explanation) its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's existing meta-documents, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content -- the same precedent all ten batch-1 and batch-2 template nodes (#1326-#1328, #1331, #1335-#1336, #1340, #1346-#1347, #1351) already landed on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied', with an inverse named referenced-by that is authored, not generated -- the only one of the five relationship types whose inverse is authored rather than generated."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents procedure-shaped subject matter, and none of the ten open template PRs from batches 1-2 (#1527-#1531, #1533-#1537) are merged, so they are not valid relationship targets either."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Diátaxis defines how-to guides as 'directions that guide the reader through a problem or towards a result', states 'How-to guides are goal-oriented', and states a how-to guide 'helps the user get something done, correctly and safely; it guides the user's action', serving 'the work of the already-competent user, whom you can assume to know what they want to do, and to be able to follow your instructions correctly'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/how-to-guides/"
  - statement: "Diátaxis states 'The fundamental structure of a how-to guide is a sequence', that this sequence 'implies logical ordering in time', and lists a how-to guide's defining traits as 'focused on tasks or problems', 'assume the user knows what they want to achieve', 'action and only action', and 'no digression, explanation, teaching' -- and separately warns against completeness for its own sake: 'Don't pollute your practical how-to guide with every possible thing the user might do related to x', because 'practical usability is more helpful than completeness'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/how-to-guides/"
  - statement: "Diátaxis states 'How-to guides must be written from the perspective of the user, not of the machinery', that a how-to guide 'describes an executable solution to a real-world problem or task', and that it is 'concerned with work -- navigating from one side to the other of a real-world problem-field'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/how-to-guides/"
  - statement: "Diátaxis states reference material 'is information-oriented' and that 'although reference should not attempt to show how to perform tasks, it can and often needs to include a description of how something works or the correct way to use it' -- the boundary this template's own Boundary section states from the how-to side, coordinating with (not restating) the corresponding statement already made from the reference side in the sibling corpus-template-reference node."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/reference/"
  - statement: "Diátaxis's 'What how-to guides are not' section states 'solving a problem or accomplishing a task cannot always be reduced to a procedure ... Real-world problems do not always offer themselves up to linear solutions', and 'The sequences of action in a how-to guide sometimes need to fork and overlap, and they have multiple entry and exit-points' -- an explicit allowance against a strictly linear numbered sequence that this template's own Required sections previously omitted."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/how-to-guides/"
  - statement: "Diátaxis's compass places how-to guides at the intersection of 'informs action' and 'application of skill' (work, not study), while tutorials sit at 'informs action' crossed with 'acquisition of skill' -- the two forms share the action axis and split on acquisition versus application, which is why Diátaxis treats how-to guides and tutorials as 'wholly distinct' despite both being action-oriented and 'often confused'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/compass/"
      - "https://diataxis.fr/how-to-guides/"
  - statement: "The Good Docs Project's canonical template source lists How-to under its Core documentation template pack (alongside Concept, README, Reference, Release notes, Tutorial, Troubleshooting), describing it as 'A concise set of numbered steps to do one task with the product', in the same repository README that enumerates the pack."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/README.md"
  - statement: "The Good Docs Project's fillable How-to template (template_how-to.md) has the section sequence Title, Overview, Before you start (optional prerequisites), one or more numbered {Task name} sections of action-verb steps (with optional {Sub-task} breakdowns using decimal step numbering), and a closing See also section for related how-to, conceptual, and troubleshooting links."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/how-to/template_how-to.md"
  - statement: "The Good Docs Project's accompanying How-to guide instructs authors to 'Address one logical goal (task) per how-to page', to 'restrict to a maximum of 8-10 steps per task' because 'lengthy how-tos can overwhelm users', to assume the reader 'has basic knowledge of the application and has already read the quickstart and the tutorial', and to 'Test your how-to instructions from start to finish so that you can uncover omitted steps, incorrect details, steps out of order, and information gaps that block users', re-testing 'after every notable product release'."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/how-to/guide_how-to.md"
  - statement: "The Good Docs Project's How-to guide states 'How-tos are task-oriented, while tutorials are learning-oriented', contrasting a tutorial's 'carefully managed path from the start to the end' with a how-to's aim to 'guide the user along the safest, surest way to the goal' toward 'a successful result'."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/how-to/guide_how-to.md"
  - statement: "The Good Docs Project templates repository's LICENSE file (gitlab.com/tgdp/templates, current canonical home; the archived github.com/thegooddocsproject/templates mirror carries no usable SPDX license) is the MIT No Attribution License, copyright The Good Docs Project 2024, granting free use/copy/modify/distribute with no attribution requirement -- not 'Zero-Clause BSD' as an unmerged research note (cited below) states; the two licenses grant materially the same no-attribution freedom but are textually distinct instruments. This is the same correction two prior corpus-template batches independently made, and it was verified again here by opening the primary source rather than trusting either the note or the prior batches' restatement of it."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/LICENSE"
  - statement: "An unmerged research note quotes Diátaxis as 'A how-to guide's purpose is to help the already-competent user perform a particular task correctly', lists How-to under the Good Docs Project's Core pack, and calls the Good Docs Project's license 'Zero-Clause BSD ... so they can be copied into a repo with no attribution burden'."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates)"
  - statement: "The sibling corpus-template-reference node (PR #1534, closing issue #1346) states the reference/how-to boundary from its own side -- 'Not #1345 (procedure/how-to), noted but not resolved here' -- and explicitly leaves 'Drawing that boundary formally, for a procedure-shaped node' as '#1345's task, not in this batch'; this node is that formal statement, drawn to coordinate with rather than duplicate PR #1534's own wording."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1534 (PR body, corpus-template-reference)"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1345's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1345's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text independently found copied across #1326-#1351 by the batch dispatch brief for this task set."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1345 definition of done"
  - statement: "No open or closed launchpad-26/buzz issue matches a search for a corpus template task covering Diátaxis's Tutorial form, as distinct from the How-to form this node covers; Diátaxis itself treats the two as 'wholly distinct' despite both being action-oriented, so a corpus node built from this how-to/procedure template would be the wrong shape for tutorial (acquisition-of-skill) content -- at the time of the search; #1538 was then filed to own it."
    entry_class: FACT
    evidence:
      - "gh_issue_list(repo='launchpad-26/buzz', search='corpus template tutorial', state='all') -> []"
      - "gh_issue_list(repo='launchpad-26/buzz', search='corpus-template-tutorial', state='all') -> []"
---

# Template: procedure

How to write a corpus node whose body takes Diátaxis's **How-to guide** form: what
required sections such a node must carry, what evidence backs a procedural claim, the
industry model it adapts, and the explicit boundary against its nearest neighbor --
reference (`#1346`). This is a template node, not a policy node -- it prescribes the
shape of a future document's *body*, not a MUST/SHOULD rule about corpus-wide
behavior. See *Note on Definition of Done* below for why that distinction matters for
this specific node.

## Scope and authority

**This node covers** what a corpus node's body must contain when it is written in
Diátaxis's How-to form -- goal-oriented, sequenced instruction that lets an
already-competent reader perform one task correctly, as opposed to information-oriented
lookup content or understanding-oriented discussion. It states the required sections,
the evidence expectations for a procedural claim, and the industry models it adapts.

**It does not cover** the front-matter contract itself (`node.schema.json` governs
that, unconditionally, for every node type, including which `type` surface value a
procedure-shaped node uses -- see *A note on `type`* below), how to create/update/
retire a node procedurally (`AGENTS.md` governs that -- itself a how-to-shaped
document about corpus authorship, not an instance of this template; see the note in
*Boundary* below), or the neighboring document forms -- reference (`#1346`) and
concept/explanation (`#1331`) -- which are separate templates with their own tasks.
See *Scope and omissions* for the full boundary.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. What this node adds is the half no schema can
hold -- which sections a procedure-shaped node needs, what evidence backs a procedural
claim, and which industry models ground the shape. That half is enforced by review,
the same way the existing corpus standards describe their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| The industry models this template adapts | *Industry model* below, and the primary sources it cites |
| The reference form's own side of the boundary below | `launchpad/docs/corpus/templates/reference.md` (`#1346`, PR #1534) |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model this template adapts

**Diátaxis, How-to guide form** (Daniele Procida, undated, `diataxis.fr`) -- one of
Diátaxis's four documentation forms (tutorial, how-to guide, reference, explanation),
placed by its own compass at the intersection of "informs action" and "application of
skill" (work, not study -- the axis that separates it from tutorial, below). Diátaxis's
own words: how-to guides are *"directions that guide the reader through a problem or
towards a result"* and *"goal-oriented"*. A how-to guide *"helps the user get something
done, correctly and safely; it guides the user's action"*, serving *"the work of the
already-competent user, whom you can assume to know what they want to do, and to be
able to follow your instructions correctly"*. It is *"concerned with work -- navigating
from one side to the other of a real-world problem-field"* and *"must be written from
the perspective of the user, not of the machinery"*.

**Structure.** *"The fundamental structure of a how-to guide is a sequence"*, one that
*"implies logical ordering in time"*. Diátaxis names four defining traits together:
*"focused on tasks or problems"*, *"assume the user knows what they want to achieve"*,
*"action and only action"*, *"no digression, explanation, teaching"*. It also warns
against reference-style completeness creeping in: *"Don't pollute your practical
how-to guide with every possible thing the user might do related to x"*, because *"in
how-to guides, practical usability is more helpful than completeness"*.

**Not the same as a tutorial, despite both being action-oriented.** Diátaxis's compass
puts tutorial at "informs action" crossed with "acquisition of skill" (study, for a
newcomer), against how-to's "application of skill" (work, for someone already
competent) -- the two forms are, in Diátaxis's own words, "often confused" but "wholly
distinct". No corpus template task currently covers the Tutorial form (see the evidence
entry above); this template does not stand in for one, and a document teaching a
newcomer to acquire a skill from scratch is the wrong fit for it.

**The Good Docs Project, How-to template** (Core pack, `gitlab.com/tgdp/templates`,
MIT No Attribution License -- see the evidence entry above for why this node states
that rather than the "Zero-Clause BSD" an unmerged research note claims) -- a fillable
template of **Title**, **Overview** (states the task in one line), an optional
**Before you start** section for prerequisites, one or more numbered **{Task name}**
sections of action-verb steps (with optional **{Sub-task}** breakdowns using decimal
step numbering, e.g. 2.1, 2.2), and a closing **See also** section linking related
how-to, conceptual, and troubleshooting content. Its accompanying guide adds concrete
discipline a theory-only source cannot: *"Address one logical goal (task) per how-to
page"*, *"restrict to a maximum of 8-10 steps per task"* because *"lengthy how-tos can
overwhelm users"*, assume the reader *"has basic knowledge of the application and has
already read the quickstart and the tutorial"*, and -- the requirement with the most
direct bearing on evidence, below -- *"Test your how-to instructions from start to
finish so that you can uncover omitted steps, incorrect details, steps out of order,
and information gaps that block users"*, re-testing *"after every notable product
release"*. The guide states the how-to/tutorial split independently of Diátaxis, in its
own vocabulary: *"How-tos are task-oriented, while tutorials are learning-oriented"*,
contrasting a tutorial's *"carefully managed path from the start to the end"* with a
how-to's aim to *"guide the user along the safest, surest way to the goal"*.

**Why both, together.** Diátaxis supplies the *why* -- the form's purpose, its
action-vs-cognition and application-vs-acquisition boundaries, the reader's
expectation when they open a how-to guide already knowing what they want to do. The
Good Docs Project supplies the *shape* -- concrete sections an author can fill in, plus
the step-count and re-testing discipline no purely theoretical source states. Diátaxis
alone gives no template to copy; the Good Docs Project template alone gives no grounded
reason to keep the guide "action and only action" rather than drifting into
explanation or reference. A corpus node built from only one of the two would either
have no structure or no discipline.

## Boundary: what this template is not

Read this section before drafting.

- **Not `#1346` (reference), stated from this side to close the loop PR #1534 left
  open.** Diátaxis draws the line explicitly: reference *"should not attempt to show
  how to perform tasks"*, while a how-to guide is exactly that -- *"directions that
  guide the reader through a problem or towards a result"*, action-oriented rather
  than information-oriented. The nuance runs both ways. Diátaxis permits reference
  material to *"include a description of how something works"* without that
  description becoming instruction; symmetrically, a how-to guide may need a short
  aside on *how something works* to make a step comprehensible, but the moment that
  aside stops serving the next action and starts cataloguing facts for their own
  sake, it has drifted into `#1346`'s territory and belongs in a linked reference
  node instead -- per Diátaxis's own advice to a how-to author: *"Refer to the x
  reference guide for a full list of options."* Concretely: if a reader wants to look
  up a field's type, a command's flags, or a status code's meaning while they work,
  that is `#1346`'s form. If a reader wants to be walked through completing one task
  correctly, that is this template's form. A node that spends more of its steps
  cataloguing facts than instructing action has picked the wrong template.
- **Not a runbook**, this template's other action-oriented neighbor. Both are
  Diátaxis how-to-shaped, but they split on when the reader needs the guide, not
  on whether the content instructs action. A procedure is for a task the reader
  chooses to perform on their own schedule -- "cut a relay release" -- sequenced
  in the order its steps must happen. A runbook is for a condition that has
  already occurred and demands a response -- "the relay is 5xx-ing, what do I
  do" -- triggered by an alert or failure, not chosen. A node walking through
  routine, planned work is this template's territory; a node responding to an
  already-firing operational condition is a runbook's.
- **Not a tutorial**, per the compass distinction in *Industry model* above --
  acquisition of skill for a newcomer, not application of skill for someone already
  competent. No corpus template task currently exists for the Tutorial form (checked,
  see the evidence entry above); filed as `#1538` rather than folded into this node's
  scope, since inventing a second form inside this template would violate
  `AGENTS.md`'s "one node is one independently maintainable idea" rule.
- **Not `#1331` (concept/explanation).** Diátaxis contrasts explanation's
  understanding-oriented, discursive treatment with a how-to guide's
  action-and-only-action instruction -- a node that spends its steps justifying *why*
  a design exists rather than instructing *how* to do the task has drifted into
  `#1331`'s territory.
- **Not `AGENTS.md` itself**, despite `AGENTS.md` being, in Diátaxis's own terms, a
  how-to-shaped document about creating/updating/retiring a corpus node. `AGENTS.md`
  is the corpus's own governing procedure and predates this template; this template
  governs *future* how-to-shaped nodes about the rest of the repository's subject
  matter, not a retroactive reshaping of `AGENTS.md` itself. Stated here because the
  overlap is real, not because either document requires the other to change.

A node built from this template that drifts into any neighbor above has picked the
wrong template, not merely written prose that needs tightening.

## A note on `type`

`node.schema.json`'s `type` enum (`architecture`, `layers`, `capabilities`,
`platforms`, `implementation`, `interfaces-events`, `verification`, `operations`,
`development`, `release`, `governance`, `agent`, `ingestion`) names the corpus
**surface** a node documents -- it has no member for documentation **form**
(tutorial/how-to/reference/explanation), and this template does not invent one. A
node built from this template takes whichever `type` its subject matter's surface
already calls for -- for example `operations` for a how-to on rotating a credential,
or `development` for a how-to on adding a new event kind -- exactly as it would if the
same subject were documented in prose instead of as sequenced steps. This template
node itself carries `type: governance` because it documents the corpus's own
authoring rules, per the precedent in the evidence ledger above, not because
procedure-shaped nodes in general use `governance`.

## Required sections

A corpus node using this template must carry the following in its body, in addition
to whatever schema-required front matter `node.schema.json` demands of every node:

1. **Overview.** One line stating the task the guide accomplishes (Good Docs
   Project's own "Overview" section) and, where useful, when or why a reader performs
   it -- not a restatement of the node's `id`.
2. **Before you start** (optional). Prerequisites the reader must already have in
   place -- access, tooling, prior state -- before the first numbered step. Omit the
   heading entirely if there are none; do not leave it present and empty.
3. **One numbered task sequence per logical goal.** Steps begin with an action verb,
   are numbered in the order they must be performed (Diátaxis: *"implies logical
   ordering in time"*), and are capped near the Good Docs Project's 8-10-step
   guidance -- a task that needs more should be split into `{Sub-task}` sections with
   decimal numbering, or, if the sub-tasks are independently useful, filed as a
   separate procedure node per `AGENTS.md`'s "one node, one idea" rule rather than
   grown into a single oversized page. **A single strictly linear numbering is the
   default, not an absolute rule.** Diátaxis warns against forcing one where the
   task does not allow it: *"solving a problem or accomplishing a task cannot always
   be reduced to a procedure ... The sequences of action in a how-to guide sometimes
   need to fork and overlap, and they have multiple entry and exit-points."* When a
   task genuinely forks -- a decision point sends the reader down one of several
   branches, or the guide has more than one valid starting point -- number each
   branch's steps in its own sequence (e.g. `2a.`/`2b.`, or a labeled sub-section per
   branch) rather than flattening a fork into a single misleading numbered list.
4. **See also.** Links to related how-to, conceptual (`#1331`-shaped), reference
   (`#1346`-shaped), or troubleshooting content the reader may need next -- per
   Diátaxis's own advice to defer completeness to reference material rather than
   growing it inline.
5. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the three exclusions in *Boundary: what this template is not* that
   apply to any how-to-shaped instance node as the checklist (not reference; not
   tutorial; not concept/explanation -- the fourth bullet there, about `AGENTS.md`,
   is specific to this template node's own self-awareness and does not recur in an
   instance node built from it), plus any node-specific exclusion the author found.
6. **Relationships**, per the guidance below.
7. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node does
   not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Task]: how-to

[One line: the task this guide accomplishes, and when or why a reader performs it.]

## Before you start

<!-- Optional -- omit this heading entirely if the task has no prerequisites. -->

- [Access, tooling, or prior state the reader needs before step 1.]

## [Task name]

1. [Action-verb step.]
2. [Action-verb step.]
   1. [Sub-step, decimal-numbered, only if step 2 genuinely has parts.]
3. [Action-verb step, through to the task's completion or verification.]

<!-- Repeat this section, or use decimal {Sub-task} numbering, only for genuinely
     ordered sub-parts of the SAME task. A second, independently useful task is a
     separate procedure node, not a second top-level section here. -->

## See also

- [Related how-to node, if any.]
- [Related #1331-shaped concept/explanation node, if any.]
- [Related #1346-shaped reference node, for lookup content this guide deliberately
  does not inline.]

## Boundary

This node does not describe:
- [facts to look up rather than actions to perform -- see the reference node for
  <subject>, if one exists]
- [how to acquire the underlying skill from scratch, for a newcomer -- a tutorial,
  which has no corpus template as of this writing]
- [why this design exists, or how its pieces relate conceptually -- see the
  concept/explanation node for <subject>, if one exists]
- [any node-specific exclusion]

## Relationships

- references: <a reference or concept/explanation node this procedure depends on for
  background the reader is assumed to already have, if any>
- part-of: <a broader capability or operations node this is a subsection of, if any>

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
````

## Evidence expectations

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means the author
opened the cited source, `INFERENCE` means the author reasoned to the claim and rated
the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement attributed to
whoever said it. Nothing about this template relaxes or narrows that. Three
expectations follow specifically from the industry model this template adapts:

- **A step is a `FACT` or nothing -- and the Good Docs Project's own discipline goes
  further than the corpus's baseline.** The guide's instruction to *"test your how-to
  instructions from start to finish"* before publishing, and to re-test *"after every
  notable product release"*, is stronger than citing a source that merely describes
  the command. Where practical, the evidence entry for a step should cite having run
  the command or exercised the workflow, not only the code or documentation that
  describes it -- a `FACT` about a procedure that was never executed is exactly the
  "omitted steps, incorrect details, steps out of order" failure mode the guide warns
  about, just moved from the reader's failure to the author's unverified claim.
- **A "why" aside inside a step still needs a citation, and still needs to stay an
  aside.** Diátaxis's nuance permits a short explanatory note inside a how-to guide
  when it serves the next action; it does not exempt that note from the corpus's
  evidence ledger, and it does not license letting the note grow into the guide's
  main content -- if it needs more than a sentence, it belongs in a linked
  `#1331`-shaped or `#1346`-shaped node instead, cited via `references`.
- **Do not cite a reference table as evidence that a procedure works.** Per the
  boundary above, a reference node asserts a general fact (a field's type, a
  command's flags); it does not establish that a specific ordered sequence of actions
  produces a specific result. Cite the actual execution -- a command run, a test
  passed, a workflow exercised -- not a lookup table that happened to describe one
  piece of it.

## Relationships

A node built from this template:

- **may** declare `references` toward a reference node (`#1346`'s template) or a
  concept/explanation node (`#1331`'s template) that the procedure assumes background
  from, or defers completeness to, per the *See also* section above. Per
  `relationships.schema.json`, `references`' directionality is "source cites target as
  supporting context; no ownership or currency dependency implied" -- the loose
  coupling a how-to-to-reference pointer needs, since the guide's steps stay accurate
  even if the reference table's exact rows later change.
- **may** declare `part-of` toward a broader capability or operations node this
  procedure is a subsection of, when the how-to is one part of a larger surface
  rather than independently standing.
- **should** declare `implements` targeting `corpus-template-procedure` (this
  node's id) once this node is merged. `relationships.schema.json` names *"a
  template instance of a standard"* as `implements`' own worked example -- this
  is exactly that case, not the weaker `references` edge.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes present in
`origin/launchpad`'s corpus tree at the recorded revision -- `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`
-- are all procedural/meta-documents about the corpus itself, not how-to-shaped
subject matter this template about procedure documentation would `references`,
`depends-on`, or sit `part-of`. None of the four sibling templates in this batch
(`#1332`, `#1337`, `#1342`, `#1349`) target this node or are targeted by it,
deliberately: all five are authored in parallel with no merge ordering between them,
so an edge to any of them would be as likely to break in CI as to resolve. The
sibling `#1346` (reference, PR #1534) is likewise not targeted, for the same
not-yet-merged reason, even though this node's *Boundary* section discusses it in
prose. The first how-to-shaped instance node is the natural moment to add a
`references` edge back to this template, once it exists.

## Note on Definition of Done

Issue `#1345`'s own Definition of Done carries four bullets -- "states scope and
authority/source of the policy," "separates MUST requirements from SHOULD guidance,"
"defines enforcement/checks and exception/escalation process," "links decisions or
higher-order policy instead of duplicating them" -- copied verbatim from the
standards-track issues that produced `standards/confidence.md` and
`standards/decision-references.md`. Those describe a **policy/standard** node (a
MUST/SHOULD normative document over existing corpus behavior); this node is a
**template** (a prescription for the shape of a future document's body). The real
acceptance criterion, from parent Feature `#605` itself, is: *"every template states
its purpose, required sections, evidence expectations and the industry model/standard
it adapts."* This node is built against that sentence -- *Required sections*,
*Evidence expectations* and *Industry model this template adapts* above answer it
directly -- rather than against the standards-track checklist, which does not fit a
document with no MUST/SHOULD normative claims about existing system behavior to
separate. This is the same mismatch the sibling `corpus-template-reference` node
(`#1346`, PR #1534) independently found and stated the same way.

## Scope and omissions

**This node covers** what a corpus node's body must contain when it takes Diátaxis's
How-to form: the required sections, the evidence expectations for a procedural claim
(including the stronger execute-and-re-test discipline the Good Docs Project adds
beyond the corpus's own baseline), the industry models (Diátaxis's How-to form + the
Good Docs Project's How-to template) the shape adapts, the explicit boundary against
the reference and concept/explanation neighbors and against the tutorial form, the
note that `type` tracks corpus surface rather than documentation form, and the
relationship types a node built from this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The reference template (information-oriented lookup content) | `#1346`, open, not yet merged |
| The concept/explanation template (understanding-oriented, discursive treatment) | `#1331`, open, not yet merged |
| A template for Diátaxis's Tutorial form (acquisition-of-skill, newcomer-oriented) | no corpus template task found to own this; filed as `#1538` |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |

**No relationships declared in this node's own front matter.** See *Relationships*
above for what was checked and why none of the four nodes that exist on
`origin/launchpad` at the recorded revision are a fit, and why the in-flight sibling
`#1346` is deliberately not targeted either.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above about what
  a how-to-shaped node needs is grounded in the Diátaxis/Good Docs Project primary
  sources, not in a worked instance. The first real procedure node -- likely an
  operational runbook-adjacent how-to, given this repository's `operations` and
  `development` surfaces -- is what will actually test whether the required sections
  above, and the 8-10-step guidance in particular, are sufficient or need revision.
- **Whether the Tutorial-form gap noted above should become its own corpus template
  task, or is deliberately out of scope for this corpus**, was not resolved here --
  only flagged in *Boundary* above and tracked in `#1538`.
- **Whether `#1346`'s eventual merged text draws the reference/how-to boundary
  identically to how this node draws it from its own side** was checked against
  PR #1534's current body, not against a merged, possibly-revised version -- neither
  `#1346` nor this node had merged as of this writing.
