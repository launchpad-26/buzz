---
id: corpus-template-implementation-reference
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and implementation is one of them; the enum names the corpus surface a node documents, not the documentation form (tutorial/how-to/reference/explanation) its prose takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "relationships.schema.json defines implements with directionality 'source is the concrete realization of target (e.g. a template instance of a standard)' and a generated inverse named implemented-by; this is the one relationship type in the corpus whose stated purpose is code-realizes-spec traceability, not documentation-to-documentation linkage."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "Of the corpus's existing meta-documents, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance, so governance is the precedent for a corpus node that documents the corpus's own authoring rules rather than a piece of architecture/capability/implementation/etc. content -- the same precedent independent batch-1 and batch-2 template nodes (#1326-#1328, #1335, #1347, #1346) already landed on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four documents is implementation-reference subject matter, and none of this batch's siblings (#1330, #1338, #1339, #1344, #1350) are merged, so none are valid relationship targets either."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "crates/git-sign-nostr/README.md ends its 'How It Works' section with 'See NIP-GS for the full specification', linking to docs/nips/NIP-GS.md, which exists in this repository -- a real, already-existing example of code documentation pointing at the spec it realizes, the same shape this template formalizes for the corpus."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md:46"
      - "docs/nips/NIP-GS.md"
  - statement: "Six crates in this repository ship their own README.md (buzz-acp, buzz-agent, buzz-cli, buzz-pairing-cli, git-credential-nostr, git-sign-nostr); buzz-core and buzz-relay, both larger and more central crates, do not -- so a corpus-level traceability artifact is not redundant with an existing per-crate convention that already covers the whole codebase."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/README.md"
      - "crates/buzz-agent/README.md"
      - "crates/buzz-cli/README.md"
      - "crates/buzz-pairing-cli/README.md"
      - "crates/git-credential-nostr/README.md"
      - "crates/git-sign-nostr/README.md"
  - statement: "launchpad/REQUIREMENTS.md carries its own 'Traceability' section, described in its own prose as 'Requirement -> the work that would satisfy it -> the milestone that work sits on', implemented as a two-column-plus table (ID, Satisfying work, Milestone) already in working use in this repository -- a lighter-weight but real precedent for the requirement/decision-to-work traceability shape this template formalizes for the corpus."
    entry_class: FACT
    evidence:
      - "launchpad/REQUIREMENTS.md:243-246"
  - statement: "No decision record under launchpad/decisions/ uses a '### Confirmation' heading (checked by grep across all 51 files, zero matches), even though MADR -- the template several of this repository's own ADRs are visibly structured after -- names Confirmation as an established, if optional, sub-section of Decision Outcome."
    entry_class: FACT
    evidence:
      - "grep(pattern='^### Confirmation', path='launchpad/decisions/*.md') -> no matches, 51 files checked"
  - statement: "The ISTQB Glossary defines traceability as 'The ability to identify related items in documentation and software, such as requirements with associated tests,' and traceability matrix as 'A two-dimensional table, which correlates two entities (e.g., requirements and test cases). The table allows tracing back and forth the links of one entity to the other, thus enabling the determination of coverage achieved and the assessment of impact of proposed changes.'"
    entry_class: FACT
    evidence:
      - "https://istqb-glossary.page/traceability/"
      - "https://istqb-glossary.page/traceability-matrix/"
  - statement: "MADR's own adr-template.md names an optional '### Confirmation' sub-section of 'Decision Outcome' with the guidance 'Describe how the implementation / compliance of the ADR can/will be confirmed... Note that although we classify this element as optional, it is included in many ADRs,' and MADR's own README states the project's expansion is 'Markdown Architectural Decision Records', not 'Markdown Any Decision Records' -- a name the project's own CHANGELOG.md records renaming to 'Markdown Any Decision Record' and then explicitly back to 'Markdown Architectural Decision Record' in a later release, which is the rename history the batch dispatch brief for this task set warns an unmerged research note gets wrong."
    entry_class: FACT
    evidence:
      - "https://github.com/adr/madr/blob/d1698d0b8b6b8ef83a0a255d3e3920cbcda159ba/template/adr-template.md"
      - "https://github.com/adr/madr/blob/d1698d0b8b6b8ef83a0a255d3e3920cbcda159ba/README.md"
      - "https://github.com/adr/madr/blob/d1698d0b8b6b8ef83a0a255d3e3920cbcda159ba/CHANGELOG.md"
  - statement: "PR #1534 (unmerged, launchpad/docs/corpus/templates/reference.md on branch task/1346-corpus-template-reference) states explicitly that node.schema.json's type enum 'names the corpus surface a node documents -- it has no member for documentation form (tutorial/how-to/reference/explanation), and this template does not invent one,' and that a node built from that template 'takes whichever type its subject matter's surface already calls for... exactly as it would if the same subject were documented in prose instead of as reference tables' -- the surface/form distinction this node's boundary against #1346 depends on."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1346 (unmerged, PR #1534, task/1346-corpus-template-reference branch)"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1341's own copied-over standards-track Definition of Done. Verified by opening the issue directly (`gh issue view 605`), not merely cited."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 (Feature parent issue body, checklist item 3)"
  - statement: "Issue #1341's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text independently found copied across #1326-#1351 by the batch dispatch brief for this task set."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1341 (issue body, Definition of Done section)"
---

# Template: implementation-reference

How to write a corpus node whose subject is **a piece of code's concrete realization
of a spec, decision, or contract** -- what such a node must state, what evidence backs
a realization claim, the industry model it adapts, and the explicit boundary against
`#1346`/reference, whose name this template's own name is easy to confuse it with.
This is a template node, not a policy node -- it prescribes what a future document's
body must establish (that named code realizes a named target, and where it does not),
not a MUST/SHOULD rule about corpus-wide behavior. See *Note on Definition of Done*
below for why that distinction matters for this specific node.

**A note on the name, before anything else.** "Implementation reference" reads two
ways. It is *not* "reference implementation" (a canonical, exemplary implementation of
a spec, word order aside) -- this template does not designate any code as canonical.
It is also not `#1346`'s Diátaxis Reference *form* applied to implementation content --
see *Boundary* below for why that reading is wrong too, and why the collision is a
real one worth naming rather than a coincidence. What it *does* mean: a **reference
from code to what it implements** -- a traceability pointer, in the ISTQB Glossary's
sense of "the ability to identify related items in documentation and software" cited
below, not a prose genre.

## Scope and authority

**This node covers** what a corpus node's body must contain when its subject is
tracing a piece of code back to the spec, decision, or contract it realizes: the
required sections, the evidence expectations for a realization claim, and the
industry models it adapts.

**It does not cover** the front-matter contract itself (`node.schema.json` governs
that, unconditionally, for every node type -- see *A note on `type`* below), how to
create/update/retire a node procedurally (`AGENTS.md` governs that), or the
neighboring template `#1346` (reference, the Diátaxis documentation *form*), which is
a separate template with its own task. See *Boundary* for the full distinction.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `relationships.schema.json` already defines
`implements` with exactly this directionality, `validate.py` runs the schema, and CI
runs `validate.py` on every corpus change. What this node adds is the half no schema
can hold -- which sections a realization claim needs, what evidence backs it, and
which industry model grounds the shape. That half is enforced by review, the same way
the existing corpus standards describe their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| `implements`' directionality and its `implemented-by` inverse | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| The documentation *form* a reference-shaped node's prose takes | `launchpad/docs/corpus/templates/reference.md` (`#1346`, unmerged at time of writing) |
| The industry models this template adapts | *Industry model* below, and the primary sources it cites |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model this template adapts

**ISTQB Glossary, `traceability` and `traceability matrix`** -- traceability is *"the
ability to identify related items in documentation and software, such as requirements
with associated tests"*; a traceability matrix is *"a two-dimensional table, which
correlates two entities (e.g., requirements and test cases). The table allows tracing
back and forth the links of one entity to the other, thus enabling the determination
of coverage achieved and the assessment of impact of proposed changes."* That second
sentence is the operative one for this template: a realization claim is not just an
assertion that code satisfies a spec, it is a link that must be walkable **both**
ways -- from the spec to the code that realizes it, and from the code back to the spec
that authorizes it -- which is exactly what `implements`'s generated `implemented-by`
inverse gives the corpus for free, once a node declares the forward edge.

**MADR's `Confirmation` section** (`github.com/adr/madr`) -- MADR's own template names
an optional `### Confirmation` sub-section of `## Decision Outcome` whose guidance
reads: *"Describe how the implementation / compliance of the ADR can/will be
confirmed... Note that although we classify this element as optional, it is included
in many ADRs."* MADR's own `CHANGELOG.md` records that the section was originally
named "Validation" before being renamed to "Confirmation" and nested under Decision
Outcome -- the same changelog that records the project's own name being renamed to
"Markdown Any Decision Record" and then explicitly back to "Markdown Architectural
Decision Record," confirming independently, from the primary source, the correction
the batch dispatch brief for this task set flags in an unmerged research note. This
repository's own decision records are visibly MADR-structured, and not one of the
fifty-one files under `launchpad/decisions/` uses that section (checked directly,
zero matches) -- so the question MADR gestures at ("does the code actually match what
was decided?") exists in this repository today with no place that answers it for any
ADR. This template is that place, generalized past ADRs to any spec/decision/contract
a node can point at.

**This repository's own `REQUIREMENTS.md` "Traceability" section** -- already working
precedent, not a hypothetical: *"Requirement -> the work that would satisfy it -> the
milestone that work sits on"*, realized as a table of requirement ID, satisfying
GitHub issue, and milestone. It is lighter-weight than what this template asks for --
it points at an issue, not at the code the issue produced, and it carries no evidence
classification -- but it establishes that requirement-to-work traceability is already
a convention this repository reaches for, not an idea imported wholesale from outside.

**Why three, together.** ISTQB supplies the *vocabulary and the bidirectional-check
discipline* -- what a traceability claim is, and why it must be checkable from both
ends. MADR supplies the *gap* -- the question decision records already invite but
this repository's own decisions never answer. `REQUIREMENTS.md` supplies the
*existing shape* -- proof that a table linking a governing artifact to the work that
satisfies it is already how this repository thinks, at a coarser grain than a single
node. A template built from only one of the three would either have no discipline, no
motivation, or no continuity with what already exists here.

## Boundary: what this template is not

Read this section before drafting -- the naming collision with `#1346` is real and
worth addressing head-on.

- **Not `#1346` (reference, the Diátaxis Reference documentation *form*).** These sit
  on two different, orthogonal axes of the same schema, and the collision is a naming
  accident, not a conceptual overlap:
  - `#1346` fixes the **form** (Diátaxis's Reference shape: information-oriented,
    "technical descriptions of the machinery and how to operate it") and lets the
    **surface** (`type`) vary with whatever the subject actually is -- its own text
    states a node built from it "takes whichever `type` its subject matter's surface
    already calls for... exactly as it would if the same subject were documented in
    prose instead of as reference tables."
  - This template fixes the **surface** -- a node built from it documents the
    `implementation` surface (or occasionally another surface value, if the
    realizing artifact's own nature calls for it -- see *A note on `type`*) and
    declares an `implements` edge -- and lets the **form** vary: the realization
    statement and divergence list below could be written as Diátaxis Reference-shaped
    tables, as discursive prose, or as a mix; this template does not prescribe a form
    any more than `#1346` prescribes a surface.
  - Concretely: a node using `#1346`'s template about, say, a CLI command surface
    catalogues *what the commands are*. A node using *this* template about the same
    CLI surface establishes *that the CLI's code matches whatever spec or decision
    said the commands should look like that, and names where it does not*. Nothing
    stops a single node from doing both -- being reference-shaped prose **and**
    carrying an `implements` edge -- but the two obligations are independent, and a
    node can satisfy either without the other.
  - A node that states only what the code does, with no named target it is
    realization of, has picked `#1346`'s job (or a plain `implementation`-typed node
    with no template at all), not this one's.
- **Not the spec/decision/contract file itself.** `docs/nips/NIP-GS.md` (a NIP
  specification) is not, itself, a candidate for this template -- it is the
  **target** a node built from this template would `implements` toward, once such a
  target has (or is given) a corpus node id. This template governs the node that
  documents the *realization*, never the thing being realized.
- **Not "reference implementation."** See the naming note above -- this template
  designates no code as canonical or exemplary; it only requires a realization claim
  to be traceable and evidenced, the way any other corpus claim must be.

A node built from this template that drifts into `#1346`'s territory (cataloguing
facts with no named target) or omits the `implements` edge and divergence discussion
entirely has picked the wrong template, not merely written prose that needs
tightening.

## A note on `type`

`node.schema.json`'s `type` enum (`architecture`, `layers`, `capabilities`,
`platforms`, `implementation`, `interfaces-events`, `verification`, `operations`,
`development`, `release`, `governance`, `agent`, `ingestion`) names the corpus
**surface** a node documents. A node built from this template most often carries
`type: implementation` -- the enum's own value for exactly this kind of content --
but is not required to: if the realizing artifact is itself a protocol/contract
surface (for example, documenting how a handler realizes a wire-level NIP), an author
may reasonably choose `interfaces-events` instead and still use this template's
required sections, the same way `#1346`'s reference form does not fix a single
surface either. What is fixed is the **relationship**, not the `type` value: a node
built from this template declares `implements` toward its target regardless of which
surface value it carries. This template node itself carries `type: governance`
because it documents the corpus's own authoring rules, per the precedent in the
evidence ledger above, not because implementation-reference nodes in general use
`governance`.

## Required sections

A corpus node using this template must carry the following in its body, in addition
to whatever schema-required front matter `node.schema.json` demands of every node:

1. **Realization statement.** One paragraph stating what code artifact (crate,
   module, service, command surface) this node documents, and what spec, decision, or
   contract it claims to realize. Name the target explicitly, even before the
   `implements` edge formalizes it.
2. **Target reference.** What is being implemented, and how a reader can open it
   themselves -- a file path, an ADR id, a NIP document, or (once one exists) another
   corpus node's id. If the target is not itself a corpus node yet, say so; do not
   invent an `implements` edge to a node id that does not exist.
3. **Implementation surface.** The actual realizing code: a table of
   component/file/symbol and what part of the target it satisfies, evidenced per
   *Evidence expectations* below -- not a narrative summary standing in for citations.
4. **Divergences.** Where the code and the target disagree -- deliberately (a
   documented, accepted deviation) or as drift (nobody has reconciled them yet). An
   empty divergence section on a node checked against real code is a claim, and per
   *Evidence expectations* below it needs the same evidentiary weight as any row that
   found a divergence -- silence is not evidence of agreement.
5. **Verification.** How the realization is checked today -- an automated test, a CI
   job, manual review, or "none" if that is the honest answer. This is the corpus's
   answer to MADR's `Confirmation` question, generalized past ADRs.
6. **Relationships**, per the guidance below.
7. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node does
   not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Artifact]: implementation reference

[One paragraph: what code artifact this node documents, and what spec, decision, or
contract it claims to realize.]

## Target

[What is being implemented, and how a reader opens it themselves -- a file path, ADR
id, NIP document, or corpus node id. State plainly if the target has no corpus node
yet.]

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| ... | ... | ... |

## Divergences

[Where the code and the target disagree, deliberately or as drift. If none were
found, say so explicitly and name what was checked to reach that conclusion -- an
empty section reads as "not checked," not as "checked and clean."]

## Verification

[How the realization is checked today: automated test, CI job, manual review, or
"none" if that is the honest answer.]

## Relationships

- implements: <the target spec/decision/contract node, if it has a corpus node id>
- references: <a verification/test node, if one exists>
- part-of: <a broader implementation node this is a sub-component of, if any>

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

- **A realization-surface row is a `FACT` or nothing.** ISTQB's traceability matrix
  is a table that must be walkable both ways; a row claiming a file or symbol
  realizes part of a target that no one opened both ends of is not traceable, it is
  asserted. Cite the code **and** the target for each row -- one citation without the
  other is half a traceability edge, not a full one.
- **A divergence claim needs the same evidentiary weight as a compliance claim, not
  less.** Per `ADR-0029`'s precedence rule (executable evidence outranks
  documentation for how the system currently behaves), a divergence row is what
  happens when the code, read directly, disagrees with the target, read directly --
  both reads are required before the row exists, not just the one that surprised the
  author.
- **Do not cite the target as evidence for the code's behavior, or the code as
  evidence for the target's requirement.** Per the boundary above, this template
  documents a relationship between two independently verifiable things. Cite the
  code for what the code does and the target for what the target requires; citing
  either as a stand-in for the other collapses the traceability check this template
  exists to make possible.

## Relationships

A node built from this template:

- **must** declare `implements` toward its target, once the target itself carries a
  corpus node id. Per `relationships.schema.json`, `implements`' directionality is
  "source is the concrete realization of target" with a generated `implemented-by`
  inverse -- exactly the bidirectional traceability edge ISTQB's definition above
  calls for, given for free once the forward edge is declared.
- **may** declare `references` toward a verification/test-strategy node (`#1350`,
  not in this batch's scope to define) that backs the *Verification* section's claim,
  when that verification is itself substantial enough to be its own node rather than
  a one-line description.
- **may** declare `part-of` toward a broader implementation node this one is a
  sub-component of, when the realizing artifact is one part of a larger
  crate/service's own implementation-reference node rather than independently
  standing.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree. If the target spec/decision/contract has no
  corpus node id yet (the common case today -- ADRs, NIP documents and code
  themselves are not corpus nodes), declare no `implements` edge and name the target
  by its real path or id in the *Target* section's prose instead; an edge to a
  nonexistent id is a hard validation error, not a soft placeholder.

**This node's own relationships.** Declared: none. Checked: the four nodes present
in `origin/launchpad`'s corpus tree at the recorded revision -- `corpus-agents`,
`corpus-readme`, `corpus-standard-confidence`, `corpus-standard-decision-references`
-- are all procedural/meta-documents about the corpus itself, not implementation
subject matter this template (itself about documenting *other* code's realization of
*other* targets) would `implements`, `depends-on`, or sit `part-of`. None of the five
sibling templates in this batch (`#1330`, `#1338`, `#1339`, `#1344`, `#1350`) target
this node or are targeted by it, deliberately: all six are authored in parallel with
no merge ordering between them, so an edge to any of them would be as likely to break
in CI as to resolve. The first implementation-reference instance node -- likely one
documenting `git-sign-nostr`'s realization of NIP-GS, given that pairing is already
the strongest real precedent found while drafting this template -- is the natural
moment to add an `implements` edge back to this template, once it exists.

## Note on Definition of Done

Issue `#1341`'s own Definition of Done carries four bullets -- "states scope and
authority/source of the policy," "separates MUST requirements from SHOULD guidance,"
"defines enforcement/checks and exception/escalation process," "links decisions or
higher-order policy instead of duplicating them" -- copied verbatim from the
standards-track issues that produced `standards/confidence.md` and
`standards/decision-references.md`. Those describe a **policy/standard** node (a
MUST/SHOULD normative document over existing corpus behavior); this node is a
**template** (a prescription for the shape of a future document's body, and for
which relationship type that document declares). The real acceptance criterion, from
parent Feature `#605` itself, is: *"every template states its purpose, required
sections, evidence expectations and the industry model/standard it adapts."* This
node is built against that sentence -- *Required sections*, *Evidence expectations*
and *Industry model this template adapts* above answer it directly -- rather than
against the standards-track checklist, which does not fit a document with no
MUST/SHOULD normative claims about existing system behavior to separate. Unlike
`#1344` (policy) in this same batch, there is no live question here about whether the
boilerplate is secretly apt: this node has no enforcement mechanism, no exception
process and no MUST/SHOULD rules of its own to state -- it prescribes a future
document's *shape*, exactly as `#1346` does for its own, different, axis.

## Scope and omissions

**This node covers** what a corpus node's body must contain when it documents a
piece of code's concrete realization of a spec, decision, or contract: the required
sections, the evidence expectations for a realization or divergence claim, the
industry models (ISTQB traceability, MADR's Confirmation section, this repository's
own `REQUIREMENTS.md` Traceability precedent) the shape adapts, the explicit boundary
against `#1346`'s documentation-form template, the note that `type` usually but not
always resolves to `implementation`, and the relationship types a node built from
this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Diátaxis Reference documentation-form template (information-oriented prose shape, independent of surface) | `#1346` |
| The test-strategy template (overall testing approach a *Verification* section might cite) | `#1350`, this batch, drafted in parallel |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Whether/when a NIP document or an ADR itself gets promoted to a corpus node id (a prerequisite for a real `implements` edge to point at it) | unresolved; not filed as its own task by this node -- an author hitting this gap should check for an existing issue before filing a new one |

**No relationships declared in this node's own front matter.** See *Relationships*
above for what was checked and why none of the four nodes that exist on
`origin/launchpad` at the recorded revision are a fit.

**Expected but not verified when this node was written:**

- **No node has yet been authored from this template.** Every claim above about what
  an implementation-reference node needs is grounded in the ISTQB/MADR/`REQUIREMENTS.md`
  precedents and in `git-sign-nostr`/NIP-GS as an illustrative pairing, not in a worked
  instance. The first real node -- plausibly documenting that exact pairing -- is what
  will actually test whether the required sections above are sufficient or need
  revision.
- **Whether a target spec/decision/contract will typically already have a corpus node
  id by the time an implementation-reference node is written about it**, or whether
  authors will routinely hit the "no id yet" case this node's *Relationships* section
  describes, was not checked -- it depends on how quickly ADRs and NIP documents get
  their own corpus nodes, which is outside this task's scope to predict.
- **Whether `#1346`'s eventual merge changes any cross-reference in this node's
  Boundary section** was not checked, since `#1346` is unmerged at time of writing and
  this node cites it as `TEAM_KNOWLEDGE`, not `FACT`, for exactly that reason.
