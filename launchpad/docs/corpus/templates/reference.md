---
id: corpus-template-reference
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template, policy, or reference; the enum names the corpus surface a node documents, not the documentation form (tutorial/how-to/reference/explanation) its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's existing meta-documents, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/capability/etc. content -- the same precedent five independent batch-1 template nodes (#1326-#1328, #1335, #1347) already landed on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied', with a generated inverse named referenced-by."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents reference-shaped subject matter, and none of batch 1's five open template PRs (#1527-#1531) are merged, so they are not valid relationship targets either."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Diátaxis defines Reference material as 'technical descriptions of the machinery and how to operate it', states 'Reference material is information-oriented', and adds the nuance that although reference 'should not attempt to show how to perform tasks', it 'can and often needs to include a description of how something works or the correct way to use it'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/reference/"
  - statement: "Diátaxis states reference material 'is led by the product it describes' (contrasted with tutorials and how-to guides, which are 'led by needs of the user'), and that it demands 'neutral description' focused on 'accuracy, precision, completeness and clarity', explicitly warning against introducing explanation that 'runs counter to the needs of technical reference'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/reference/"
  - statement: "Diátaxis defines Explanation as 'a discursive treatment of a subject, that permits reflection', states 'Explanation is understanding-oriented', and states explanation 'does not take the user's eye-level view, as in a how-to guide, or a close-up view of the machinery, like reference material' -- the explicit contrast this template's boundary against #1331 (concept) is grounded in."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/explanation/"
  - statement: "Diátaxis's compass places reference at the intersection of 'informs cognition' (theoretical/propositional knowledge, thinking) and 'application of skill' (work), while explanation sits at 'informs cognition' crossed with 'acquisition of skill' (study) -- the two forms share the cognition axis and split on acquisition versus application, which is the axis that does not apply to the concept/reference boundary this template states in prose."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/compass/"
  - statement: "Diátaxis defines How-to guides as 'directions that guide the reader through a problem or towards a result', states 'How-to guides are goal-oriented', and states 'How-to guides must be written from the perspective of the user, not of the machinery', with explicit guidance not to let a how-to guide's own reference-like digressions grow: \"Refer to the x reference guide for a full list of options. Don't pollute your practical how-to guide with every possible thing the user might do related to x.\""
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/how-to-guides/"
  - statement: "Diátaxis's colophon states 'Diátaxis is the work of Daniele Procida'."
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/colophon/"
  - statement: "The Good Docs Project's canonical template source lists Reference under its Core documentation template pack (alongside Concept, How-to, README, Release notes, Troubleshooting, Tutorial) and lists Glossary separately under its Miscellaneous pack, in the same repository README that enumerates both packs."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/README.md"
  - statement: "The Good Docs Project's fillable Reference template (template_reference.md) has exactly three sections -- '{Reference description}', '{Table name or other structured entry}' (a table of Field/Description/Example), and an optional 'Commands' section (a table of Command/Description/Argument/Example) -- with no procedural or step-ordered content in any of them."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/reference/template_reference.md"
  - statement: "The Good Docs Project's accompanying Reference guide states 'It is important to limit procedural or instructional content', distinguishes a Reference article from an API Reference by audience ('Users who are unfamiliar with the problem space and product' versus 'Domain experts who know the problem space and wish to interact with the product using the product's API'), and instructs authors to 'Avoid high-level usage instructions or descriptions for the application'."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/reference/guide_reference.md"
  - statement: "The Good Docs Project templates repository's LICENSE file (gitlab.com/tgdp/templates, current canonical home; the archived github.com/thegooddocsproject/templates mirror carries no usable SPDX license) is the MIT No Attribution License, copyright The Good Docs Project 2024, granting free use/copy/modify/distribute with no attribution requirement -- not 'Zero-Clause BSD' as an unmerged research note (cited below) states; the two licenses grant materially the same no-attribution freedom but are textually distinct instruments, and this discrepancy was found by opening the primary source rather than trusting the note's prose, the same kind of check that caught the note's separate MADR-naming error."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/LICENSE"
  - statement: "An unmerged research note frames Diátaxis's reference/how-to boundary as 'Diátaxis does not forbid describing how something works; it forbids instructing', calls the Good Docs Project's license 'Zero-Clause BSD ... so they can be copied into a repo with no attribution burden', and lists Reference under the Good Docs Project's Core pack alongside Concept, How-to, README, Release notes, Troubleshooting and Tutorial."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note, launchpad/Research/project-documentation-templates.md on branch docs/research-project-doc-templates)"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1346's own copied-over standards-track Definition of Done."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/605"
  - statement: "Issue #1346's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text independently found copied across #1326-#1351 by the batch dispatch brief for this task set."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/1346"
---

# Template: reference

How to write a corpus node whose body takes Diátaxis's **Reference** form: what
required sections such a node must carry, what evidence backs a reference claim, the
industry model it adapts, and the explicit boundary against its two nearest
neighbors -- concept/explanation and how-to/procedure. This is a template node, not a
policy node -- it prescribes the shape of a future document's *body*, not a
MUST/SHOULD rule about corpus-wide behavior. See *Note on Definition of Done* below
for why that distinction matters for this specific node.

## Scope and authority

**This node covers** what a corpus node's body must contain when it is written in
Diátaxis's Reference form -- technical, information-oriented description of "the
machinery and how to operate it," as opposed to task-shaped instruction or
understanding-oriented discussion. It states the required sections, the evidence
expectations for a reference claim, and the industry models it adapts.

**It does not cover** the front-matter contract itself (`node.schema.json` governs
that, unconditionally, for every node type, including which `type` surface value a
reference-shaped node uses -- see *A note on `type`* below), how to create/update/
retire a node procedurally (`AGENTS.md` governs that), or the neighboring document
forms -- concept/explanation (`#1331`) and procedure/how-to (`#1345`, not in this
batch) -- which are separate templates with their own tasks. See *Scope and
omissions* for the full boundary.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. What this node adds is the half no schema can
hold -- which sections a reference-shaped node needs, what evidence backs a reference
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

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model this template adapts

**Diátaxis, Reference form** (Daniele Procida, undated, `diataxis.fr`) -- one of
Diátaxis's four documentation forms (tutorial, how-to guide, reference, explanation),
placed by its own compass at the intersection of "informs cognition" (theoretical,
propositional knowledge) and "application of skill" (work, not study). Diátaxis's own
words: reference guides are *"technical descriptions of the machinery and how to
operate it"* and *"information-oriented"*. Reference *"is led by the product it
describes"* rather than by a user's task, and demands *"neutral description"* focused
on *"accuracy, precision, completeness and clarity"* -- explanation, opinion and
instruction are all named as things that *"run counter to the needs of technical
reference"*.

**The nuance that is easy to miss.** Diátaxis does not ban description of behavior
from reference material: *"Although reference should not attempt to show how to
perform tasks, it can and often needs to include a description of how something
works or the correct way to use it."* The line is between describing *how something
works* (permitted, often required) and instructing the reader through *performing a
task with it* (not permitted -- that is a how-to guide's job). A reference node that
drifts into step-ordered task instruction has picked the wrong template regardless of
how accurate its content is.

**The Good Docs Project, Reference template** (Core pack, `gitlab.com/tgdp/templates`,
MIT No Attribution License -- see the evidence entry above for why this node states
that rather than the "Zero-Clause BSD" an unmerged research note claims) -- a three-
section fillable template: a **Reference description** section that "concisely
summarizes the reference article's content," a **structured-entry** section (table,
list, or object schema) for the actual reference data, and an optional **Commands**
section for CLI/code-block reference material. Its accompanying guide states plainly:
*"It is important to limit procedural or instructional content"* -- the same boundary
Diátaxis draws, restated from a template-author's rather than a theorist's angle. The
guide also distinguishes a plain Reference article from an **API Reference**: a
Reference article targets *"Users who are unfamiliar with the problem space and
product, and users seeking clarification on CLI commands and arguments,"* while an
API Reference targets *"Domain experts who know the problem space and wish to
interact with the product using the product's API."* This template follows the
former; a corpus node about an API surface's endpoints/parameters may need the
latter's depth instead, and should say so in its own scope section rather than
silently under-documenting.

**Why both, together.** Diátaxis supplies the *why* -- the form's purpose, its
information-vs-understanding-vs-instruction boundaries, the reader's expectation when
they open a reference document. The Good Docs Project supplies the *shape* -- three
concrete sections an author can actually fill in. Diátaxis alone gives no template to
copy; the Good Docs Project template alone gives no grounded reason to keep
instruction and opinion out of it. A corpus node built from only one of the two would
either have no structure or no discipline.

## Boundary: what this template is not

Read this section before drafting.

- **Not `#1331` (concept/explanation).** Diátaxis draws this line itself:
  explanation *"is understanding-oriented"* and *"permits reflection,"* while
  reference *"is information-oriented"* and gives *"a close-up view of the
  machinery."* Explanation *"does not take ... a close-up view of the machinery,
  like reference material"* -- the two forms are stated as opposites in the same
  sentence. Concretely: if a reader wants to understand *why* a design exists or
  how its pieces relate conceptually, that is `#1331`'s form. If a reader wants to
  look up a specific fact -- a field's type, a command's flags, a status code's
  meaning -- while they work, that is this template's form. A node that spends more
  words justifying a design than cataloguing its facts has drifted into `#1331`'s
  territory.
- **Not `#1345` (procedure/how-to), noted but not resolved here.** Diátaxis states
  how-to guides *"must be written from the perspective of the user, not of the
  machinery"* and are *"goal-oriented,"* with explicit advice against letting a
  how-to guide's asides grow into reference content: *"Don't pollute your practical
  how-to guide with every possible thing the user might do."* The mirror-image trap
  is this template's to name: a reference node that starts numbering steps
  ("first configure X, then run Y") has stopped being information-oriented and has
  become an unlabelled how-to guide. Drawing that boundary formally, for a
  procedure-shaped node, is `#1345`'s task, not in this batch -- this template only
  states the shared edge from its own side, per the batch dispatch brief for this
  task set.
- **Not an API Reference**, per the Good Docs Project's own audience split above.
  If the subject is a full API surface for domain experts rather than a CLI/config
  surface for unfamiliar users, say so in the node's scope section; this template's
  three-section shape may be too shallow for that depth.

A node built from this template that drifts into either neighbor has picked the
wrong template, not merely written prose that needs tightening.

## A note on `type`

`node.schema.json`'s `type` enum (`architecture`, `layers`, `capabilities`,
`platforms`, `implementation`, `interfaces-events`, `verification`, `operations`,
`development`, `release`, `governance`, `agent`, `ingestion`) names the corpus
**surface** a node documents -- it has no member for documentation **form**
(tutorial/how-to/reference/explanation), and this template does not invent one. A
node built from this template takes whichever `type` its subject matter's surface
already calls for -- for example `interfaces-events` for a CLI command reference,
or `capabilities` for a feature's configuration-option reference -- exactly as it
would if the same subject were documented in prose instead of as reference tables.
This template node itself carries `type: governance` because it documents the
corpus's own authoring rules, per the precedent in the evidence ledger above, not
because reference-shaped nodes in general use `governance`.

## Required sections

A corpus node using this template must carry the following in its body, in addition
to whatever schema-required front matter `node.schema.json` demands of every node:

1. **Reference description.** One paragraph (Good Docs Project's own "Reference
   description" section) stating what the node catalogues, its scope, and how it
   relates to other documentation -- e.g. a task-oriented node it is linked from.
2. **Structured entries.** The actual reference content, as a table, list, or
   object-schema block -- one row/entry per fact (field, command, status code,
   configuration key). Ordered to match the reference material's own order (e.g.
   source declaration order), not alphabetically, per the Good Docs Project guide's
   convention. Prose sentences describing *how something works* are permitted
   alongside the structured entries per Diátaxis's own nuance above; step-by-step
   task instruction is not.
3. **Commands** (optional). A table of command/flag/argument reference, when the
   subject is CLI- or code-shaped, per the Good Docs Project's optional third
   section.
4. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the three exclusions in *Boundary: what this template is not* as
   the checklist (not concept/explanation; not step-ordered procedure; not an API
   Reference, unless the author deliberately widened scope to that depth), plus any
   node-specific exclusion the author found.
5. **Relationships**, per the guidance below.
6. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Subject]: reference

[One paragraph: what this node catalogues, its scope, and what task-oriented or
conceptual document it is linked from, if any.]

## [Table name or structured-entry heading]

[Prose describing how the subject works, where that description is needed to make
the entries below legible -- permitted per Diátaxis's own nuance, not a violation of
the information-oriented boundary.]

| Field / Item | Description | Example |
|---|---|---|
| ... | ... | ... |

## Commands

<!-- Optional -- omit this section entirely if the subject has no command surface. -->

| Command | Description | Argument | Example |
|---|---|---|---|
| ... | ... | ... | ... |

## Boundary

This node does not describe:
- [why this design exists, or how its pieces relate conceptually -- see the
  concept/explanation node for <subject>, if one exists]
- [how to accomplish a task using this subject, step by step -- see the how-to /
  procedure node for <subject>, if one exists]
- [any node-specific exclusion]

## Relationships

- references: <a concept/explanation node this reference material supports, if any>
- part-of: <a broader reference or capability node this is a subsection of, if any>

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

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means the
author opened the cited source, `INFERENCE` means the author reasoned to the claim
and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement
attributed to whoever said it. Nothing about this template relaxes or narrows that.
Three expectations follow specifically from the industry model this template adapts:

- **A structured-entry row is a `FACT` or nothing.** Diátaxis frames reference as
  information a user "looks to in their work" -- a row asserting a field, command or
  status code that no source confirms is exactly the kind of unverifiable fact
  reference material exists to prevent. Cite the code, schema, config, or
  specification the reader can open to confirm the row, the same discipline
  `AGENTS.md`'s evidence section already requires of every claim.
- **A prose description of "how something works" still needs a citation.**
  Diátaxis's nuance permits this content in a reference node; it does not exempt it
  from the corpus's evidence ledger. A sentence explaining mechanism without a
  citation is an unsupported claim wearing the reference form's permission to
  describe mechanism.
- **Do not cite a how-to guide or tutorial as evidence for a reference claim.**
  Per the boundary above, a procedure document shows one path through a system
  under specific conditions; a reference table asserts the general fact. Cite the
  thing itself (the code, the schema, the spec), not a walkthrough that happened to
  demonstrate it once.

## Relationships

A node built from this template:

- **may** declare `references` toward a concept/explanation node (`#1331`'s
  template) that motivates or contextualizes the subject, when reading the
  reference alone would leave a reader without the conceptual grounding to use it.
  Per `relationships.schema.json`, `references`' directionality is "source cites
  target as supporting context; no ownership or currency dependency implied" --
  exactly the loose coupling a reference-to-concept pointer needs, since the
  reference table stays accurate even if the concept's framing later changes.
- **may** declare `part-of` toward a broader node this reference material is a
  subsection of, when the reference is one part of a larger capability or interface
  node rather than independently standing.
- **may** declare `references` toward this template node itself (target:
  `corpus-template-reference`) once this node is merged, if the author wants the
  generated `referenced-by` edge; this is optional, since a node's shape (Reference
  description / structured entries / optional Commands) already shows which
  template it followed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes present
in `origin/launchpad`'s corpus tree at the recorded revision -- `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`
-- are all procedural/meta-documents about the corpus itself, not reference-shaped
subject matter this template about reference documentation would `references`,
`depends-on`, or sit `part-of`. None of the four sibling templates in this batch
(`#1331`, `#1336`, `#1340`, `#1351`) target this node or are targeted by it,
deliberately: all five are authored in parallel with no merge ordering between them,
so an edge to any of them would be as likely to break in CI as to resolve. The first
reference-shaped instance node is the natural moment to add a `references` edge back
to this template, once it exists.

## Note on Definition of Done

Issue `#1346`'s own Definition of Done carries four bullets -- "states scope and
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
separate.

## Scope and omissions

**This node covers** what a corpus node's body must contain when it takes Diátaxis's
Reference form: the required sections, the evidence expectations for a
reference-table claim, the industry models (Diátaxis's Reference form + the Good
Docs Project's Reference template) the shape adapts, the explicit boundary against
the concept/explanation and how-to/procedure neighbors, the note that `type` tracks
corpus surface rather than documentation form, and the relationship types a node
built from this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The concept/explanation template (understanding-oriented, discursive treatment) | `#1331` |
| The procedure/how-to template (goal-oriented, step-ordered task instruction) | `#1345`, open and not yet drafted at time of writing |
| API Reference depth for a full API surface, distinct from a plain Reference article | `#1532`, filed against this gap while drafting this node; unresolved at time of writing |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |

**No relationships declared in this node's own front matter.** See *Relationships*
above for what was checked and why none of the four nodes that exist on
`origin/launchpad` at the recorded revision are a fit.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above about
  what a reference-shaped node needs is grounded in the Diátaxis/Good Docs Project
  primary sources, not in a worked instance. The first real reference node --
  likely a CLI command or configuration-option catalogue -- is what will actually
  test whether the required sections above are sufficient or need revision.
- **Whether a corpus node will ever need API Reference depth**, and if so whether
  that becomes its own template task or an extension of this one, was not resolved
  here -- only flagged in *Industry model* above and tracked in `#1532`.
- **Whether `#1345`'s eventual procedure/how-to template will draw the boundary
  against this one the same way this node draws it from its own side** was not
  checked, since `#1345` does not exist yet.
