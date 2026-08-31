---
id: corpus-template-concept
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
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no template or policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every other corpus meta-document at the recorded revision -- AGENTS.md excepted, which is type: agent -- uses type: governance: README.md, standards/confidence.md and standards/decision-references.md all do."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "This node is a meta-document about how to author a corpus node, not itself a concept, so governance is chosen by the same reasoning corpus-readme already recorded for its own type choice, rather than as an independent precedent this node invents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.6
  - statement: "A corpus node instance actually written from this template -- a real concept document about a real Buzz idea -- may take a type value other than governance, decided by that instance's own subject against PRD #602's corpus-surface list; this template document itself is not such an instance."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries exactly four validated content nodes: AGENTS.md (corpus-agents), README.md (corpus-readme), standards/confidence.md (corpus-standard-confidence) and standards/decision-references.md (corpus-standard-decision-references); schema/ is present but excluded from validation."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md; schema/ present but excluded from validation"
  - statement: "None of the four existing content nodes has documentation forms, Diátaxis, the Good Docs Project, or corpus templates as its subject, so no relationships.target among them would be a substantive edge rather than a citation duplicate of what this node's evidence ledger already cites directly."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.8
  - statement: "Diátaxis defines Explanation as 'a discursive treatment of a subject, that permits reflection,' stating plainly that 'Explanation is understanding-oriented.'"
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/explanation/"
  - statement: "Diátaxis further characterizes Explanation as documentation that 'deepens and broadens the reader's understanding of a subject. It brings clarity, light and context,' and frames it from the reader's side as 'an answer to the question: Can you tell me about ...?'"
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/explanation/"
  - statement: "Diátaxis defines Reference guides, by contrast, as 'technical descriptions of the machinery and how to operate it,' stating plainly that 'Reference material is information-oriented.'"
    entry_class: FACT
    evidence:
      - "https://diataxis.fr/reference/"
  - statement: "The canonical repository for The Good Docs Project's templates is gitlab.com/tgdp/templates; its GitHub mirror at github.com/thegooddocsproject/templates is archived (archived: true) with a last push of 2022-09-18, while the GitLab project shows activity as recent as 2026-08-25, two days before this node's recorded revision (2026-08-27)."
    entry_class: FACT
    evidence:
      - "github_api(repos/thegooddocsproject/templates) -> archived: true, pushed_at: 2022-09-18T16:20:39Z"
      - "gitlab_api(projects/tgdp%2Ftemplates) -> last_activity_at: 2026-08-25T00:59:45.440Z"
  - statement: "The current canonical Concept template (gitlab.com/tgdp/templates, concept/template_concept.md) is structured as: an untitled opening block covering a summary/introductory paragraph and the concept's definition, an optional visual aid, an optional '(Optional) Background' section, a required 'Use cases' section, an optional '(Optional) Comparison of {thing}' section, and an optional '(Optional) Related resources' section."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/concept/template_concept.md"
  - statement: "The accompanying Concept template guide instructs authors to 'Dedicate to a single concept: Ensure that your document focuses on just one concept to prevent confusion or information overload. If the explanation begins to explain another concept, it is advisable to start a different concept document and provide a link,' and separately to 'Avoid instructional and referential information: The concept document should also avoid instructional text and step-by-step guides which are different types of documentation.'"
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/concept/guide_concept.md"
  - statement: "The guide also instructs authors to use the definition section to 'define the scope of the concept - define its boundaries, what you'll cover ... and how deep into details you will dive,' including stating explicitly 'what you don't mean by that concept,' and to disambiguate synonyms used elsewhere so the reader's understanding stays uniform."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/concept/guide_concept.md"
  - statement: "The current canonical repository's LICENSE file (gitlab.com/tgdp/templates) is the MIT No Attribution License (MIT-0): 'Permission is hereby granted, free of charge, to any person obtaining a copy of this software ... to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,' dated Copyright (c) 2024 The Good Docs Project."
    entry_class: FACT
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/LICENSE"
  - statement: "The archived GitHub mirror's LICENSE.txt is instead the Zero-Clause BSD text: 'Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,' with no copyright-holder or date line."
    entry_class: FACT
    evidence:
      - "https://raw.githubusercontent.com/thegooddocsproject/templates/104c4e69179166d18eebd752ed9901916ef5e348/LICENSE.txt"
  - statement: "The research note at launchpad/Research/project-documentation-templates.md, on unmerged PR #1466, describes the Good Docs Project templates as licensed 'Zero-Clause BSD (\"Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted\")' and cites only the GitHub URL for that claim, not the GitLab one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1466 (unmerged research note)"
  - statement: "Because the archived GitHub mirror and the live GitLab project carry two different license texts, the note's Zero-Clause BSD claim describes a source that is no longer the project's canonical one; the license actually governing the current Concept template (fetched directly for this node) is MIT No Attribution, not Zero-Clause BSD."
    entry_class: INFERENCE
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/LICENSE"
      - "https://raw.githubusercontent.com/thegooddocsproject/templates/104c4e69179166d18eebd752ed9901916ef5e348/LICENSE.txt"
      - "github_api(repos/thegooddocsproject/templates) -> archived: true"
    confidence: 0.8
  - statement: "Both the Zero-Clause BSD and MIT No Attribution texts grant unrestricted use, copy, modification and redistribution with no attribution requirement, so this correction changes which license text an author should point to, not whether the template may be copied into this corpus without attribution."
    entry_class: INFERENCE
    evidence:
      - "https://gitlab.com/tgdp/templates/-/raw/main/LICENSE"
      - "https://raw.githubusercontent.com/thegooddocsproject/templates/104c4e69179166d18eebd752ed9901916ef5e348/LICENSE.txt"
    confidence: 0.8
  - statement: "AGENTS.md states that one node is one independently maintainable idea, and that a second concept, contract or procedure discovered while writing does not get folded in but is filed as its own task and linked instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md states that every non-.md file under the corpus root is rejected today, including one placed under generated/, because no generator exists yet to reproduce it from canonical Markdown (issue #1316), so a corpus change may add Markdown only until that lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "relationships.schema.json defines the references relationship type's directionality as 'source cites target as supporting context; no ownership or currency dependency implied,' with an authored (not generated) inverse edge, referenced-by."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Issue #605 (parent PRD) states the acceptance criterion for every template task in this batch as: every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts -- distinct from the byte-identical MUST/SHOULD/enforcement/policy checklist copied into this node's own issue #1331 from the standards-track issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (parent PRD, relayed via the corpus-templates batch dispatch brief)"
  - statement: "Issue #1331's definition of done otherwise requires one hand-authored canonical document, schema-valid front matter, one independently maintainable idea, traceable FACT/INFERENCE/TEAM_KNOWLEDGE claims, links instead of duplicated content, a check against the recorded provenance revision, and a clean validator run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1331 definition of done"
  - statement: "Issue #1346 (task: define the reference corpus template) and issue #1345 (task: define the procedure corpus template) both exist as open, filed sibling template tasks, so the boundaries this node draws against reference-typed and procedure-typed content name real filed issues rather than hypothetical future ones. AGENTS.md requires an issue URL to stay TEAM_KNOWLEDGE rather than be forced into FACT on a URL citation, since the validator can neither pin nor open it -- this entry follows that rule rather than the FACT class the rest of this ledger favors where a file is available."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "gh issue view 1346/1345 --repo launchpad-26/buzz, run directly while authoring this node"
---

# Template: concept

How to write a corpus node whose subject is a **concept** — an idea, abstraction, or
mechanism in the Buzz system that a reader needs to understand before the reference
material or the how-to material about it will make sense. This node is the template
itself, not an instance of one: it states what a concept node must contain, not an
explanation of any real Buzz concept.

## Scope and authority

**This node covers** the purpose of a concept document, the sections it must
contain, what evidence each section needs, the industry model it adapts (Diátaxis's
Explanation form, read together with the Good Docs Project's Concept template), and
the boundary against the sibling document forms a concept is most often confused
with.

**A note on this node's own definition of done.** Issue #1331's checklist carries a
MUST/SHOULD/enforcement/exception block copied verbatim from the standards-track
issues that produced `standards/confidence.md` and `standards/decision-references.md`
— documents whose subject is a normative policy. This node's subject is a template,
and the parent PRD (#605) states the acceptance bar that actually applies to a
template task: *every template states its purpose, required sections, evidence
expectations and the industry model/standard it adapts.* This document is built
against that sentence. The rest of #1331's checklist — one hand-authored document,
schema-valid front matter, one independently maintainable idea, traceable claims,
links instead of duplication, a check against the recorded revision, a clean
validator run — is generic to any corpus node and is honoured below regardless.

**Its authority is derived, not original.** `node.schema.json` is the front-matter
law; `AGENTS.md` is the create/update/retire procedure; `standards/confidence.md`
and `standards/decision-references.md` are the two evidence-mechanics standards
merged so far. This document adds nothing to any of those. What it adds is the part
none of them can: what a *concept-scoped* node must say, and where that shape comes
from.

| For | Read |
|---|---|
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Evidence classes and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Relationship types and directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Diátaxis, primary source | `https://diataxis.fr/explanation/`, `https://diataxis.fr/reference/` |
| The Good Docs Project Concept template, primary source | `https://gitlab.com/tgdp/templates/-/raw/main/concept/template_concept.md`, `https://gitlab.com/tgdp/templates/-/raw/main/concept/guide_concept.md` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## Purpose

A concept node exists to answer one question for a reader who does not yet share
the corpus's vocabulary: ***what is this, and how does it fit with everything else
I already know?*** It is understanding-oriented, not task-oriented and not
lookup-oriented. A reader should come away able to name the idea, state its
boundary (what it is and, just as importantly, what it is not), and place it
against the concepts around it — without being told how to operate it and without
being handed a catalogue of its parameters.

**The failure this template exists to prevent.** Left unscoped, a concept document
drifts in one of two directions: sideways into **reference** territory — turning
into an exhaustive technical catalogue of fields, methods or configuration, which
is a different form with a different job (issue #1346's territory) — or forward
into **how-to/procedure** territory — turning into a set of steps ("first do this,
then do that"), which is also a different form (issue #1345's territory). Both
drifts produce a document that is not wrong so much as mis-shelved: the facts might
be true, but a reader who came here to understand an idea has to wade through
operating instructions or a parameter table to find the understanding they were
looking for. The sections below, and the boundary section that follows them, exist
to keep those two drifts out.

## The industry model this adapts

**Diátaxis, Explanation form** (Daniele Procida, `https://diataxis.fr/explanation/`,
undated — no version number is published). The primary source defines Explanation
as "a discursive treatment of a subject, that permits reflection," stating plainly
that "Explanation is understanding-oriented." It further characterizes the form as
documentation that "deepens and broadens the reader's understanding of a subject. It
brings clarity, light and context," and frames it from the reader's side as an
answer to the question "Can you tell me about ...?" A concept node is this corpus's
instance of that form: the question a reader brings to it is exactly "can you tell
me about {X}?", not "how do I do {X}?" and not "what are {X}'s exact parameters?"

**The Good Docs Project, Concept template** (`gitlab.com/tgdp/templates`,
`concept/template_concept.md` and its accompanying `guide_concept.md`; Zero-Clause
BSD is what the *research note behind this batch* cites, but see the correction in
this node's own evidence ledger — the project's canonical home moved from an
archived GitHub mirror to GitLab, and the live repository's license is MIT No
Attribution, not Zero-Clause BSD; both are unrestricted, no-attribution licenses, so
the correction changes the citation, not whether the template may be reused here).
This is the template the *required sections* below are drawn from directly. Its
guide states the scope discipline in almost the same words `AGENTS.md` already uses
for the whole corpus: "Dedicate to a single concept ... If the explanation begins to
explain another concept, it is advisable to start a different concept document and
provide a link." That is not a coincidence this node needs to argue for — it is two
independent sources (a generic documentation-corpus rule and a concept-specific
industry template) converging on the same discipline from different directions.

**Both sources agree on the shape of the drift to avoid**, from opposite ends: the
Good Docs guide's own words are "Avoid instructional and referential information:
The concept document should also avoid instructional text and step-by-step guides
which are different types of documentation" — the same boundary Diátaxis draws
structurally by keeping Explanation, How-to and Reference as three of its four
distinct forms.

## Required sections

A concept node MUST contain the following. ("MUST" here is this template's own
requirement for the shape of an instance node, not a restatement of any MUST/SHOULD
normative-policy framework — this document is a template, not a standard, per the
*Scope and authority* note above.) Section order follows the Good Docs Concept
template's own layout; bracketed sections are optional there and remain optional
here for the same reason the template gives.

1. **Title and, where useful, an introductory paragraph (optional).** Name the
   concept in the title. An introductory paragraph, if used, states the concept's
   relevance and previews what the document covers — the Good Docs guide calls this
   applying "the inverted pyramid technique," starting from a high-level overview
   before the detail.

2. **Definition.** The one section this template does not allow to be optional.
   State what the concept *is*, in language a reader unfamiliar with it can follow.
   The Good Docs guide is explicit that this section does double duty as a scope
   statement: "define the scope of the concept — define its boundaries, what you'll
   cover in a document ... It may be useful to define what is out of scope — what
   you don't mean by that concept." If the concept has a name that collides with a
   different meaning elsewhere (in the wider industry, or in a different part of
   this corpus), disambiguate it here, explicitly, rather than letting a reader
   assume the wrong one.

3. **Visual aid or diagram (optional).** If a diagram clarifies how the concept is
   organized or fits into a larger system, include one — but it must be authored as
   text inside the Markdown body (a Mermaid fenced code block is the recommended
   form), never as a linked or embedded external image file. `AGENTS.md` states that
   every non-Markdown file under the corpus root is rejected today, including one
   placed under `generated/`, because no generator exists yet to reproduce it from
   canonical Markdown (issue #1316). A concept node with a linked PNG and no inline
   diagram does not validate today.

4. **Background (optional).** Historical, industry or design context for the
   concept — why it exists, what came before it, what alternatives were considered
   — when that context helps the reader's understanding rather than merely
   decorating the document. Claims here are frequently INFERENCE or TEAM_KNOWLEDGE
   rather than FACT; see *Evidence expectations* below.

5. **Use cases.** How a reader benefits from understanding this concept, and in
   what situations they will need it. This section is what keeps a concept
   document from being purely definitional — it is where the "why does this
   matter to me" question gets answered.

6. **Comparison (optional).** If the concept has a small number of variants,
   versions or close alternatives, a short table naming each and why one would be
   chosen over another. Omit this section entirely rather than forcing a
   comparison table onto a concept with nothing to compare against.

7. **Related resources (optional).** Links to material that helps a reader go
   deeper. **In this corpus, prefer a typed `relationships` entry over a prose
   link whenever the target is itself a corpus node.** `relationships.schema.json`
   defines `references` as "source cites target as supporting context; no
   ownership or currency dependency implied," with an authored inverse edge
   (`referenced-by`) — which is exactly the Good Docs guide's own grouping of this
   section into "How-to guides," "Linked concepts" and "External resources."
   Genuinely external material (a primary source, an RFC, a paper) stays as a
   prose citation in the evidence ledger or the body; a sibling corpus node
   becomes a `relationships` edge instead, so the corpus's own graph carries the
   link rather than a paragraph that can drift out of sync with it.

8. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover and who owns it, and — separately — what was expected to be
   verified when the node was written and could not be.

## Evidence expectations

**The definition (required section 2) is where FACT is most reachable.** If the
concept is something Buzz's own code, schema or an accepted decision defines
precisely, cite that source directly and classify the claim FACT. Do not describe a
concept from memory when its defining source is one file away.

**Background (optional section 4) is where INFERENCE and TEAM_KNOWLEDGE do the most
work.** "Why was it designed this way" is frequently a claim nobody wrote down
verbatim — it is reasoned from what the sources do establish (INFERENCE, with
`confidence` set honestly per `standards/confidence.md`) or it is something someone
on the team said and no source corroborates (TEAM_KNOWLEDGE, with `provided_by`
naming them). Neither is a lesser class than FACT; misclassifying a decision as an
INFERENCE because a citation happens to be nearby is the failure
`standards/confidence.md` names as "reasoning versus deciding," and it applies here
exactly as it does anywhere else in the corpus.

**The single-concept discipline is an evidence discipline, not just a style
preference.** `AGENTS.md`'s "one node is one independently maintainable idea" and
the Good Docs guide's "dedicate to a single concept" are the same rule stated twice,
independently, for two different reasons — one about keeping the corpus's graph of
nodes maintainable, one about keeping a single document's evidence ledger legible.
If drafting reveals that explaining concept A requires fully explaining concept B,
that is B's own node, linked with a `references` edge, not a second Definition
folded into A's.

## Boundary against reference (#1346) and procedure (#1345)

**Against reference.** Diátaxis draws this line directly: Explanation "permits
reflection" and "is understanding-oriented"; Reference is "technical descriptions of
the machinery and how to operate it" and "is information-oriented." A concept node
answers "what is this and why does it matter"; a reference node answers "what are
its exact parameters, fields or operations, so I can look one up." If a section of a
concept draft reads like a table of fields with no surrounding narrative, that
content belongs in a reference node instead (issue #1346's template, not this one).

**Against procedure/how-to.** Both primary sources for this template state the same
prohibition from their own side: the Good Docs guide says to "avoid instructional
and referential information: The concept document should also avoid instructional
text and step-by-step guides," and Diátaxis keeps How-to as a separate, fourth form
entirely. If a concept draft starts numbering steps for the reader to perform, that
content belongs in a procedure node instead (issue #1345's template, not this one).
This node does not attempt to state where Diátaxis draws *that* boundary in detail —
that is #1345's to establish — it only names the boundary as one this template's
author needs to recognize and route around.

**The tell, either way**, is the question the section is actually answering. "What
is it, and how does it relate to what I know" stays here. "What does it require me
to do" or "what exactly does it accept as input" belongs to one of the two siblings
above.

**Against glossary term (#1340).** A subject that is a single defined term — one
piece of jargon needing only a one-to-three-sentence, dictionary-style meaning —
is not a concept. `glossary-term.md` (#1340) is the narrower template for exactly
that case, and its own boundary table already routes the other direction: a term
needing several paragraphs of discursive "why does this exist and how does it fit
together" reasoning is not a glossary term any more, and belongs here instead. If
what is being drafted is a short, lookup-shaped definition with no reflection or
surrounding narrative, use `glossary-term.md`, not this template.

## A note on `type`

`node.schema.json`'s `type` enum (`architecture`, `layers`, `capabilities`,
`platforms`, `implementation`, `interfaces-events`, `verification`, `operations`,
`development`, `release`, `governance`, `agent`, `ingestion`) names the corpus
**surface** a node documents, not the documentation form (explanation, reference,
how-to) its prose takes. A corpus node instance actually written from this
template — a real concept document about a real Buzz idea — may take a `type`
value other than `governance`, decided by that instance's own subject against PRD
#602's corpus-surface list. This template document itself carries
`type: governance` because it documents the corpus's own authoring rules, per the
precedent in the evidence ledger above, not because concept-shaped nodes in
general use `governance`.

## Scope and omissions

**This document covers** the purpose of a concept node, the sections it must
contain (including its own required scope-and-omissions section), what evidence
each section needs, the industry model it adapts, and what `type` a concept
instance carries. It does not itself explain any real Buzz concept.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The reference document form and its required sections | #1346 |
| The procedure/how-to document form and its required sections | #1345 |
| The glossary-term document form, for a single defined term needing only a short lookup definition | #1340, `glossary-term.md` |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Evidence classification mechanics beyond what this template's own sections need | `launchpad/docs/corpus/AGENTS.md`, `standards/confidence.md` |
| Whether a diagram-authoring convention (e.g. a fixed Mermaid style) should be standardized corpus-wide | Not yet filed as its own issue at the recorded revision |

**No `relationships` in this node's own front matter.** Checked before deciding
that rather than assuming it: at the recorded revision, `origin/launchpad`'s
`launchpad/docs/corpus` tree carries exactly four validated content nodes
(`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references`), and none has documentation forms, Diátaxis,
the Good Docs Project or corpus templates as its subject. An edge to any of them
would be a citation duplicate of what this node's evidence ledger already cites
directly, not a substantive typed relationship. The likeliest future edges are
`references` targeting the reference (#1346) and procedure (#1345) templates once
they merge, and a `part-of` or `references` edge to whatever standard eventually
governs diagram-authoring conventions corpus-wide — none of which exist yet on
`origin/launchpad`.

**Expected but not verified when this node was written:**

- **No real concept instance has been authored from this template yet.** Whether
  the `relationships`-over-prose-link guidance for "Related resources" (required
  section 7) actually reads well in a finished node, rather than merely sounding
  right in the abstract, is untested. The first real concept node is the place to
  find out.
- **Whether corpus review will treat this template's "MUST" list as binding on a
  future concept instance, or only as strong guidance**, was not tested against an
  actual review of such an instance — no such instance exists yet to review.
- **The Good Docs Project's Concept template and guide are dated by their GitLab
  commit history, not by an explicit version number on the page.** No claim above
  depends on that history's exact dates beyond establishing that the GitLab project
  is live and the GitHub mirror is archived; the fuller commit history was not
  read.
