---
id: corpus-template-glossary-term
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
  - statement: "A node's front matter is validated against node.schema.json, whose type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every other corpus meta-document at the recorded revision -- AGENTS.md excepted, which is type: agent -- uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "schema/README.md and schema/COMPATIBILITY.md were both read in full while choosing this node's type, and neither names a template-specific or policy-specific enum value; COMPATIBILITY.md's only content is the v1 history entry for issue #622 and the additive-change rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "This node is a meta-document about how to author a corpus node, not itself a glossary term, so governance is chosen for the same reason corpus-readme and the architecture-container template (unmerged PR #1529) already recorded for their own type choice, rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
      - "https://github.com/launchpad-26/buzz/pull/1529"
    confidence: 0.6
  - statement: "Unlike an architecture-container instance, which maps cleanly onto type: architecture because containers are themselves a named PRD #602 surface, a real glossary-term instance's subject can belong to any of the thirteen surfaces (a relay-protocol term is architecture or implementation; a review-process term is governance; and so on), so this template cannot fix one type value for instance nodes -- an instance author must choose type from the term's own subject matter, not from this template's type."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "Relationships must resolve against the corpus tree on the branch being merged into, and at the recorded revision origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is excluded from validation."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
  - statement: "None of batch 1's five sibling corpus-template PRs (#1527-#1531) is merged at the recorded revision -- all five are still open -- so none of the nodes they would add is a valid relationships.target yet either."
    entry_class: FACT
    evidence:
      - "gh_pr_list(launchpad-26/buzz, numbers=1527..1531) -> #1527 OPEN, #1528 OPEN, #1529 OPEN, #1530 OPEN, #1531 OPEN"
  - statement: "None of the four existing content nodes has glossaries, terminology or templates as its subject, so a relationships.target among them would be a citation duplicate of what this node's evidence ledger already cites directly by path, not a substantive typed relationship."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.8
  - statement: "The Good Docs Project's Glossary template (misc pack) is a single Markdown file with a four-column table -- Term, an optional Abbreviation column, Definition, and an optional Source column -- with one boilerplate row showing placeholder text for each column, and a note pointing to a companion guide for how to fill it in."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/glossary/template_glossary.md"
  - statement: "The companion Glossary template guide states a glossary 'is a common reference document that organizes terms and their definitions' and states as best practice that 'glossaries only store terms that are specific to a particular industry, organization, or team,' adding that 'terms or descriptions defined in an established dictionary typically shouldn't be included in a glossary.'"
    entry_class: FACT
    evidence:
      - "https://www.thegooddocsproject.dev/template/glossary"
  - statement: "The same guide distinguishes a base glossary ('a term, definition, and abbreviation (if there is one)') from a richer document type it names a terminology system, which 'can include additional information, including localization notes, related terms, term provenance, and more' -- a terminology system is a named, more complex sibling document type, not a larger glossary."
    entry_class: FACT
    evidence:
      - "https://www.thegooddocsproject.dev/template/glossary"
  - statement: "The guide lists a glossary's benefits as: acting as a cheat sheet for team jargon that speeds up contributor onboarding; lowering miscommunication from obscure or multiply-defined terms; helping users understand a product's language; enabling interactive hover-over definitions when saved in a machine-readable format; improving accessibility of websites and pages; and simplifying translation for international teams."
    entry_class: FACT
    evidence:
      - "https://www.thegooddocsproject.dev/template/glossary"
  - statement: "The Good Docs Project's own template-pack listing places Glossary in the Miscellaneous pack (alongside API getting started, API reference, Contact support, Installation guide, Quickstart, SDK overview, Style guide, Terminology system, User personas), not in the Core pack (Concept, How-to, README, Reference, Release notes, Troubleshooting, Tutorial)."
    entry_class: FACT
    evidence:
      - "https://www.thegooddocsproject.dev/template"
  - statement: "The Good Docs Project's templates repository changed its license from the Zero-Clause BSD license to the MIT-No-Attribution license (MIT-0), effective with the v1.3 'Friendship' release announced 2024-12-12; the templates repository's current LICENSE file at gitlab.com/tgdp/templates names MIT No Attribution, not Zero-Clause BSD."
    entry_class: FACT
    evidence:
      - "https://www.thegooddocsproject.dev/blog/release-friendship"
      - "https://gitlab.com/tgdp/templates/-/blob/main/LICENSE"
  - statement: "launchpad/Research/project-documentation-templates.md, on unmerged PR #1466, describes the Good Docs Project's templates as licensed 'Zero-Clause BSD... so they can be copied into a repo with no attribution burden,' and lists Glossary under that note's 'Misc pack' grouping -- the pack placement matches the primary source directly, but the license claim does not: the templates repository moved to MIT-0 in its v1.3 release (2024-12-12), before this note's stated 2026-08-26 research date, so the note's Zero-Clause BSD claim was already stale when written, not merely outdated since. This is a second, independently found primary-source correction to the note, the same shape as the MADR-naming error a batch-1 agent already found -- verified here by fetching the templates repository's own LICENSE file and its release announcement rather than trusting the note's summary."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note), correction found by independently fetching https://gitlab.com/tgdp/templates/-/blob/main/LICENSE and https://www.thegooddocsproject.dev/blog/release-friendship"
  - statement: "Issue #605 (parent PRD) states the real acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts -- distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1340 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD, relayed via the corpus-templates batch dispatch brief)"
  - statement: "Issue #1340's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1340 definition of done"
  - statement: "AGENTS.md states that one corpus node is one independently maintainable idea, and that if a second concept, contract or procedure turns up while writing, it is filed as its own task rather than folded in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "node.schema.json constrains a node's id to kebab-case (^[a-z0-9]+(-[a-z0-9]+)*$), which cannot represent a term's natural capitalization, punctuation or spacing (for example 'NIP-29' or an acronym with mixed case), so the id and the term it names are never guaranteed to read the same way."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issues #1331 (concept), #1336 (deployment), #1346 (reference) and #1351 (threat model) are sibling template tasks in the same batch as this one, none merged at the recorded revision, so none is a valid relationships.target and none targets this node either."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issues #1331, #1336, #1346, #1351 (relayed via the corpus-templates batch dispatch brief); an issue is not an openable file per AGENTS.md's citation-shape guidance, so this is TEAM_KNOWLEDGE rather than FACT even though the issues were read directly"
---

# Template: glossary term

How to write a corpus node whose subject is a **single defined term** -- one piece
of jargon or one specialized usage this cohort's corpus needs a shared, citable
meaning for. This node is the template itself, not an instance of one: it states
what a glossary-term node must contain, not the definition of any real term.

## Scope and authority

**This node covers** the purpose of a glossary-term document, the sections it
must contain, what evidence its definition needs, and the industry model it
adapts (The Good Docs Project's Glossary template, misc pack). It does not
itself define any real term.

**A note on this node's own definition of done.** Issue #1340's checklist
carries a MUST/SHOULD/enforcement/exception block copied verbatim from the
standards-track issues that produced `standards/confidence.md` and
`standards/decision-references.md` -- documents whose subject is a normative
policy. This node's subject is a template, and the parent PRD (#605) states the
acceptance bar that actually applies to a template task: *every template states
its purpose, required sections, evidence expectations and the industry
model/standard it adapts.* This document is built against that sentence. The
rest of #1340's checklist -- one hand-authored document, schema-valid front
matter, one independently maintainable idea, traceable claims, links instead of
duplication, a check against the recorded revision, a clean validator run -- is
generic to any corpus node and is honoured below regardless.

**Its authority is derived, not original.** `node.schema.json` is the
front-matter law; `AGENTS.md` is the create/update/retire procedure;
`standards/confidence.md` and `standards/decision-references.md` are the two
evidence-mechanics standards merged so far. This document adds nothing to any
of those. What it adds is the part none of them can: what a *term-definition*
node must say, and where that shape comes from.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The Good Docs Project Glossary template, primary source | `https://gitlab.com/tgdp/templates/-/raw/main/glossary/template_glossary.md` |
| The Good Docs Project Glossary guide, primary source | `https://www.thegooddocsproject.dev/template/glossary` |

If this file and any of those disagree, **they win** -- this one has drifted
and should be fixed.

## Purpose

A glossary-term node exists to answer one question for a reader who has hit an
unfamiliar word or phrase somewhere else in the corpus or the codebase: ***what
does this mean, here, in this project?*** It is deliberately not a place to
re-derive what a general dictionary already covers -- the primary source this
template adapts states as best practice that "terms or descriptions defined in
an established dictionary typically shouldn't be included in a glossary." A
term earns a node here only because this project uses it in a specific,
non-obvious, or otherwise load-bearing way that a dictionary definition would
not capture. If that is not true of a term under consideration, this is the
wrong template.

**The failure this template exists to prevent.** Left unscoped, a
glossary-term document drifts in one of three directions:

- **Up into a full explanation.** A term that needs several paragraphs of
  discursive "why does this exist and how does it fit together" reasoning is
  not a glossary term any more -- it is a concept/explanation document
  (issue #1331's territory). A glossary term stays a short, lookup-shaped
  definition; if the reader needs to reflect on the idea, link to a concept
  node instead of writing the reflection here.
- **Sideways into a terminology system.** The primary source names a richer,
  separate document type -- a terminology system -- that adds alternative
  terms, related terms, term provenance and localization notes on top of a
  base glossary entry. Those fields do not belong in a glossary-term node
  (see *What this template deliberately excludes* below); wanting them is a
  sign of writing a terminology system, not a term.
- **Sideways into one file holding many terms.** The Good Docs Project's own
  template is shaped as a single Markdown file with one table row per term.
  This corpus rejects that shape for its own content (see the same section)
  because `AGENTS.md`'s one-node-one-idea rule treats each term as its own
  independently maintainable idea.

## The industry model this adapts

**The Good Docs Project, Glossary template** (misc pack, `https://gitlab.com
/tgdp/templates`, currently licensed MIT-No-Attribution -- see the *Licensing
correction* note below). The primary source's base structure is a four-column
table: **Term**, an optional **Abbreviation**, **Definition**, and an optional
**Source**. The companion guide gives one hard constraint worth keeping
verbatim: a definition should be "no more than one to three sentences." It also
states the two purposes this template's own *Purpose* section above is built
from: excluding terms an established dictionary already covers, and -- in its
own words -- "if the definition already exists elsewhere (for example, in an
online dictionary), and that definition matches your team's use of the term,
use the published definition" rather than inventing a new one.

**Licensing correction to the batch's research note.** The unmerged research
note this batch is grounded in (`launchpad/Research/project-documentation-templates.md`,
PR #1466) states the Good Docs Project's templates are licensed Zero-Clause
BSD. That was true once, but the templates repository's steering committee
voted to move to the MIT-No-Attribution license (MIT-0) with the v1.3
"Friendship" release, announced 2024-12-12 -- before the note's own stated
2026-08-26 research date. The current `LICENSE` file at
`gitlab.com/tgdp/templates` names MIT No Attribution, not Zero-Clause BSD. The
two licenses are both attribution-free and permissive, so nothing here changes
because of the correction; it is recorded because it is the same shape of
error as the MADR-naming correction a batch-1 agent already found in the same
note -- another example of why this batch fetches primary sources directly
rather than trusting the note's prose alone.

**Why the corpus's own evidence ledger already exceeds the primary source's
own "Source" column.** The Good Docs Project's Source column is optional and
free-form. `node.schema.json` already requires every substantive claim in a
corpus node -- including a term's definition -- to carry an `evidence` entry
classified `FACT`, `INFERENCE` or `TEAM_KNOWLEDGE`. That ledger is a stronger,
schema-enforced version of the same idea the primary source's Source column
gestures at, so this template does not add a second, competing "source" field
to the body: the evidence ledger is where a glossary term's provenance goes,
full stop.

## Required sections

A glossary-term node's **body** MUST contain the following three sections, in
this order. ("MUST" here is this template's own requirement for the shape of
an instance node, not a restatement of any MUST/SHOULD normative-policy
framework -- this document is a template, not a standard, per the *Scope and
authority* note above.)

1. **Term statement.** One line naming the term exactly as it is written or
   spoken in this project -- its real capitalization, punctuation and spacing
   -- plus its abbreviation or acronym if it has one. This is required
   separately from the node's `id`, because `id` is constrained to kebab-case
   and frequently cannot represent the term's natural form (an id of
   `nip-29` says nothing about whether the term is written "NIP-29," "nip29,"
   or "NIP 29" in practice).

2. **Definition.** One to three sentences -- the primary source's own limit --
   stating what the term means *as this project uses it*. Not a restatement
   of a dictionary sense already available elsewhere; per the *Purpose*
   section above, if a dictionary definition would do, this node should not
   exist.

3. **Scope and omissions**, per `AGENTS.md`'s own required shape for this
   section: what this node does not cover and who owns it (a fuller
   discussion of the concept the term names, if one exists, belongs to a
   concept/explanation node instead -- see *Boundary against sibling
   templates* below), and -- separately -- anything expected to verify while
   drafting this node and unable to.

Separately, in the **front matter** (not a body heading, and not a fourth
item in the list above -- front matter has no position relative to body
sections), the Definition's claim needs its own `evidence` entry, classified
honestly per `AGENTS.md`: `FACT` when it cites an accepted decision,
specification, code symbol or comment that establishes the meaning;
`INFERENCE` with `confidence` when the meaning is reasoned from usage
patterns rather than stated anywhere directly; `TEAM_KNOWLEDGE` with
`provided_by` when this is the first time the meaning has been written down
and no source corroborates it yet. This maps directly onto the primary
source's own guidance to prefer an existing authoritative definition and
write one only when none exists.

## What this template deliberately excludes

Everything below is something the primary source's own richer sibling
document -- a terminology system, not a glossary -- would add. None of it
belongs in a glossary-term node, and wanting one of these fields is the
signal that the document being written is not actually a glossary term:

- **No "related terms" field.** This corpus already has a typed mechanism for
  exactly this: a `references` relationship (`relationships.schema.json`)
  targeting another glossary-term node's `id`. Use that instead of free-text
  prose naming related terms -- it is checked by the validator, a free-text
  list is not.
- **No "alternative terms" or synonym field.** If a second name for the same
  concept is common enough to need its own definition, that is a separate
  glossary-term node with its own `id`, connected by `references`, not a
  second name folded into one node -- per `AGENTS.md`'s one-node-one-idea
  rule, a term and its synonym are still two independently maintainable
  lookup entries even when their definitions are nearly identical.
- **No "term provenance" or "localization notes" fields.** These are named,
  specific features of a terminology system the primary source describes as a
  distinct, more complex document type. A glossary-term node's provenance is
  its `evidence` ledger (see above); it has no localization concerns of its
  own to document.
- **No single file holding many terms.** The primary source's own template is
  shaped as one Markdown table, many term rows, one file. This corpus does
  not adopt that shape: `AGENTS.md` states one file is one node and one node
  is one independently maintainable idea, so a document defining ten terms is
  ten nodes, not one node with a ten-row table. Adapting the primary source
  here means taking its *field* structure (term, abbreviation, definition)
  and rejecting its *document* structure (one file per glossary) in favor of
  this corpus's own atomicity rule.

## Choosing `type` for a real instance node

Unlike an architecture-container instance, which maps directly onto
`type: architecture` because containers are themselves a named PRD #602
surface, a glossary term has no single natural surface. A term about a relay
protocol detail might be `architecture` or `implementation`; a term about this
corpus's own review process might be `governance`; a term about a mobile-only
concept might be `platforms`. This template does not fix one answer: an
instance author chooses `type` from the term's own subject matter, the same
way they would for any other node about that subject, and states the
reasoning if the choice is not obvious. That is an open judgement call this
template surfaces rather than resolves -- see *Scope and omissions* below.

## Relationships an instance node should consider

This template's own front matter declares none (see *Scope and omissions*
below), but an instance node written from this template usually has real
edges to declare once its siblings exist:

- **`references`**, targeting another glossary-term node whose definition
  this one's definition mentions, assumes, or is easily confused with.
  `references` is `relationships.schema.json`'s type for "supporting context,
  no ownership or currency dependency implied," and its inverse is
  `authored`, not `generated` -- so if the relationship is genuinely mutual,
  each term node authors its own `references` edge to the other rather than
  relying on a generated back-edge that does not exist for this type.
- **`part-of`**, targeting a glossary index or collection node, if and when
  one is created. No such node exists in this corpus today (checked against
  the four content nodes on `origin/launchpad` at the recorded revision), so
  this cannot be declared by any instance yet -- it is named here so a future
  author knows the mechanism exists once an index node is written.
- **`implements`**, targeting this template's own id
  (`corpus-template-glossary-term`), once this node is merged --
  `relationships.schema.json` names exactly that directionality ("source is
  the concrete realization of target, e.g. a template instance of a
  standard") for a document pointing at the template it was written from.
  This node is unmerged at the recorded revision, so no instance can declare
  this edge yet without failing validation against `origin/launchpad`.

None of these can be declared by *this* template document itself -- a
template is not an instance of the term it describes, and declaring
`references` or `part-of` here would target a node that does not exist for a
term that is never named.

## Boundary against sibling templates

| This template (glossary term) | Its neighbors |
|---|---|
| **Up:** concept (#1331, not yet written) | Covers understanding-oriented, discursive explanation of a subject. This template stops at a one-to-three-sentence definition; if a term needs reflection or "why this matters" reasoning, that content belongs in a concept node, linked via `references`, not folded into the term's definition. |
| **Sideways:** reference (#1346, not yet written) | Covers technical descriptions of machinery and how to operate it -- information-oriented, like this template, but scoped to a system's operable surface rather than to one word's meaning. A glossary term that starts describing how to *use* something, not just what it *means*, has drifted into reference territory. |
| **Sideways, within the same primary source:** terminology system (Good Docs Project misc pack, not assigned to any issue in this batch) | Adds alternative terms, related terms, provenance and localization notes on top of a base glossary entry. This template deliberately stops short of that richer shape -- see *What this template deliberately excludes* above. |

## Scope and omissions

**This node covers** the purpose of a glossary-term document, its required
sections, its evidence expectations, and the industry model (The Good Docs
Project's Glossary template, misc pack) it adapts.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Discursive explanation of a term's surrounding concept | #1331 (concept template, not yet written) |
| Technical description of machinery or how to operate something | #1346 (reference template, not yet written) |
| Alternative terms, related-term webs, provenance and localization notes as a document's primary subject | Good Docs Project's terminology system template (no corpus issue currently assigned) |
| The evidence-class contract itself (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |
| The `confidence` field's meaning and requirements | `launchpad/docs/corpus/standards/confidence.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Which `type` a real glossary-term instance should declare | Not fixed by this template -- see *Choosing `type` for a real instance node* above; genuinely an instance-by-instance judgement call, not a gap this template failed to close |

**No `relationships` in this node's front matter.** At the recorded revision,
`origin/launchpad`'s corpus tree carries four validated content nodes --
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` -- and none of the four has glossaries,
terminology or templates as its subject. An edge to any of them would be a
citation duplicate of what this node's evidence ledger already cites directly
by path, not a substantive typed relationship. This was checked against the
actual tree (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`),
not assumed from "the corpus is new." No edge to the sibling template issues
in this batch (#1331, #1336, #1346, #1351) either: all are being authored in
parallel by independent agents with none merged when review starts on the
others, so declaring an edge to any of their ids today would be a hard
validation error against `origin/launchpad` even though it might resolve
inside this node's own worktree.

**Expected but not verified when this node was written:**

- **No instance of this template has been written yet.** Whether the three
  required body sections and the front-matter evidence requirement above are
  sufficient, or whether a real term surfaces a concern this template does
  not anticipate, is untested. The first real glossary-term node is the test.
- **Whether any term in this repository or cohort actually needs a
  glossary-term node was not surveyed.** This template states how to write
  one if a term needs it; it does not identify a first candidate term.
- **The Good Docs Project's separate "Glossary Process" document**, which the
  guide references for how to write an original definition when no
  authoritative one exists, was not fetched or read -- the guide names it but
  this node does not cite its content, because doing so was outside this
  task's scope of adapting the Glossary *template* itself.
- **Cross-model review was not run.** Issue #1467 records that the
  cross-model review provider (Codex) is currently unavailable; a same-model
  final pass was substituted, per the corpus-templates batch dispatch brief.
