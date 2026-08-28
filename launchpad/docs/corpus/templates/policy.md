---
id: corpus-template-policy
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template or policy; the enum names the corpus surface a node documents, not the document's normative shape."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "AGENTS.md's own scope-and-omissions table lists 'Templates for each node type -- concept, component, capability, interface, flow, policy, procedure, runbook, reference, specification, and the rest' as not covered there and owned by 'somewhere in #1307-#1351', naming policy as one member of the per-node-type template family rather than a synonym for the standards track."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "confidence.md, an active corpus standard, states in its own body 'This is a policy node' -- direct evidence that the standards track already thinks of its own documents as policy-shaped, without a template to point at when it was written."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/confidence.md"
  - statement: "validate.py's _load_frontmatter splits a node's text on the frontmatter delimiter and assigns the remainder to a variable named _body, which no other function in the module reads -- the body is discarded before any check runs, for every node regardless of directory."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py defines exactly one directory-keyed rule that changes whether a node is validated at all -- EXCLUDED_TOP_LEVEL_DIRS = {\"schema\"} -- and one other directory-keyed rule that reports a non-.md file outside generated/ as misplaced and rejects it either way; no rule in the module distinguishes standards/ from templates/ from any other directory beneath the corpus root, so a policy-shaped node validates identically wherever it lives."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "relationships.schema.json's own worked example for the implements relationship type states its directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)' -- the schema itself anticipates a standard document declaring implements toward the template it instantiates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "RFC 2119 (S. Bradner, Harvard University, March 1997) defines MUST as 'an absolute requirement of the specification', MUST NOT as 'an absolute prohibition of the specification', SHOULD as permitting departure only when 'the full implications must be understood and carefully weighed before choosing a different course', and MAY as marking an item 'truly optional'."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119.txt"
  - statement: "This repository already cites RFC 2119 verbatim for its own normative-keyword convention: docs/nips/NIP-DV.md and docs/nips/NIP-PL.md both state under a Terminology heading, 'This document uses MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, and RECOMMENDED as defined in RFC 2119.'"
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-DV.md"
      - "docs/nips/NIP-PL.md"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1344's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1313 (documentation-standard), read at its own branch head, states in its own scope-and-omissions table that 'The required shape of a per-node-type template, which is a different document kind with its own required-content list' is owned by '#1326-#1351', i.e. explicitly not by #1313 itself; and separately states that its own four required-content clauses (scope/authority, MUST/SHOULD split, enforcement/exceptions, link-not-duplicate) are shared 'across the batch's policy-kind tasks rather than a contract specific to standards', naming #1344 by number among five sampled template issues that carry the same clauses."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/8a4b8425089cf64bb3cac990ac8519429c11d7ca/launchpad/docs/corpus/standards/documentation-standard.md"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the four is a policy-subject-shaped instance node this template's own front matter would point at, and #1313/documentation-standard (the one node this template names as a narrower instance) is not merged and not a valid relationship target."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Issue #1344's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1344 definition of done"
  - statement: "This template is the general policy-shape template and #1313/documentation-standard is a narrower, specialized instance of it, rather than the two being unrelated documents that happen to converge on similar sections."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/8a4b8425089cf64bb3cac990ac8519429c11d7ca/launchpad/docs/corpus/standards/documentation-standard.md"
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.8
relationships:
  - type: depends-on
    target: corpus-agents
---

# Template: policy

How to write a corpus node whose body states binding requirements on some subject --
the sections it must carry, how a requirement is identified and cited, the evidence
expectations, and the industry model it adapts. This is a template node: it prescribes
the shape of a future document, the same document kind #1346/reference and its
siblings prescribe for their own forms. **Read *Boundary: this template versus
#1313/documentation-standard* before drafting anything** -- this is the one template in
the batch whose subject and whose own required shape are close enough that getting the
boundary wrong would produce a duplicate rather than a sibling.

## Scope and authority

**This node covers** what a corpus node's body must contain when that node exists to
state binding requirements -- MUST/SHOULD-shaped rules -- about some subject, together
with who enforces those requirements and how a case the rules do not reach is handled.
It states the required sections, how a requirement is identified and cited, the
evidence expectations specific to a normative claim, and the industry model this shape
adapts.

**It does not cover** the front-matter contract itself (`node.schema.json` governs
that, unconditionally, for every node type -- see *A note on `type`* below), how to
create/update/retire a node procedurally (`AGENTS.md` governs that and this node
depends on it, declared below), or what any *particular* policy-shaped node's subject
requires (the topic standard, once one exists, is always more specific and wins on its
own subject -- see *Precedence*).

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. What this node adds is the half no schema can
hold -- which sections a policy-shaped node needs, how its requirements are identified
and cited, and which industry model grounds the shape. That half is enforced by review,
the same way every corpus standard already describes its own review-enforced half.

**Precedence.** Where this document and `node.schema.json`, `validate.py`, an accepted
ADR, or `AGENTS.md` disagree, **they win** -- this one has drifted and should be fixed.
Where it and a specific policy-shaped node disagree about that node's own subject, **the
specific node wins** -- it is the more specific rule, written with the subject in front
of it. Where it and a *narrower specialized template for one family of policy-shaped
node* disagree about that family's own conventions (for example #1313/documentation-
standard's H1 convention for documents under `standards/`, once it merges), **the
narrower template wins for its family** -- see *A note on `type`* and *Boundary* below
for what "family" means here.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The narrower shape for a corpus standard specifically | `launchpad/docs/corpus/standards/documentation-standard.md` (unmerged at this node's authoring time; see Boundary) |
| The industry model this template adapts | *Industry model* below, and the primary sources it cites |

## Industry model this template adapts

**RFC 2119** (S. Bradner, Harvard University, March 1997, `rfc-editor.org`) -- the
IETF's key-words convention for requirement levels, written so that "the specification
and interpretation of standards documents becomes unambiguous." Its definitions are the
ones every MUST/SHOULD/MAY in this corpus already means: **MUST** is "an absolute
requirement of the specification"; **MUST NOT** an absolute prohibition; **SHOULD**
permits departure only when "the full implications must be understood and carefully
weighed before choosing a different course"; **MAY** marks an item "truly optional."
RFC 2119 supplies the *vocabulary discipline* -- what each keyword commits a document
to, and why "should" written in lower case is not the same promise as "SHOULD" written
in upper case.

**This repository already uses it, which is why this template adopts it rather than
inventing a second convention.** `docs/nips/NIP-DV.md` and `docs/nips/NIP-PL.md` each
carry a Terminology section stating plainly: "This document uses MUST, MUST NOT,
SHOULD, SHOULD NOT, MAY, and RECOMMENDED as defined in RFC 2119." A policy-shaped
corpus node sits in the same repository as those NIPs and should mean the same thing by
the same words, not a corpus-local reinterpretation of them.

**What RFC 2119 does not supply is a document shape** -- it defines words, not sections.
The six-section shape below (*Required sections*) is not from RFC 2119; it is what this
corpus's own standards track converged on independently, four times, before any
template existed to tell them to. That convergence is itself evidence, cited in the
front matter: `confidence.md` explicitly calls itself "a policy node" while following
this shape by instinct rather than by instruction. This template's job is to write down
what already happened four times, so the fifth policy-shaped node does not have to
reinvent it.

## A note on `type`

`node.schema.json`'s `type` enum (`architecture`, `layers`, `capabilities`,
`platforms`, `implementation`, `interfaces-events`, `verification`, `operations`,
`development`, `release`, `governance`, `agent`, `ingestion`) names the corpus
**surface** a node documents -- it has no member for a document's normative shape, and
this template does not invent one. A node built from this template takes whichever
`type` its **subject's** surface calls for: a policy about the corpus's own
documentation practice (the standards track) carries `governance`, matching every
meta-document in the corpus so far; a policy about, say, a release process would carry
`release`; a policy about a verification practice would carry `verification`. This
template node itself carries `type: governance` because its subject is the corpus's own
authoring rules, not because policy-shaped nodes in general use `governance`.

**"Family" in the Precedence section above** means a group of policy-shaped nodes
sharing one subject-surface and one narrower template of their own -- the clearest
current example is "corpus standard," the family `#1313/documentation-standard`
governs once it merges, all living under `standards/` and all carrying `governance`.
A narrower template may add conventions this one does not require (a fixed H1 string,
an additional MUST tied to that family's own subject matter) without amending this
node; see *Boundary* for exactly what #1313 adds.

## Boundary: this template versus #1313/documentation-standard

**Read this before drafting.** #1313 (`documentation-standard`, unmerged at this
node's authoring time, branch head `8a4b8425089cf64bb3cac990ac8519429c11d7ca`) governs
"the shape of one kind of document: a corpus node that states requirements on corpus
content," scoped explicitly to documents living under `standards/`. On its face that
description overlaps this template almost completely -- both name a scope-and-authority
opening, separated MUST/SHOULD, an enforcement section, an exceptions-and-escalation
section, and a closing scope-and-omissions section as required. Two readings were
weighed, not guessed at:

- **(a) #1344/policy is a general template, and #1313 is a narrower, specialized
  instance of it** -- a "corpus standard" is one particular family of policy-shaped
  node (subject: the corpus's own construction; location: `standards/`; H1 convention:
  `# Standard: <topic>`), and #1313 exists to add that family's own extra conventions
  on top of the shape every policy-shaped node already needs.
- **(b) #1344/policy and #1313/documentation-standard are two unrelated documents that
  happen to converge on similar sections by coincidence.**

**(a) was chosen.** The evidence, all opened directly rather than assumed:

1. **#1313 names the boundary itself.** Its own scope-and-omissions table lists "The
   required shape of a per-node-type **template**, which is a different document kind
   with its own required-content list" and assigns it to "#1326-#1351" -- explicitly
   not to #1313. A document cannot own a boundary it also disclaims owning; #1313 is
   stating, in its own words, that the template-shape question is somewhere else.
2. **#1313 names this task specifically.** Its scope-and-omissions table separately
   states that its four required-content clauses reach "the batch's policy-kind tasks
   rather than a contract specific to standards," and names #1344 by number among five
   sampled template issues carrying the identical clauses. #1313 is not claiming to be
   the only policy-kind document in the batch; it is naming a family it belongs to.
3. **The schema anticipated the relationship.** `relationships.schema.json`'s own
   worked example for `implements` is "a template instance of a standard" -- a standard
   document declaring `implements` toward the template it instantiates is not a
   relationship this document invented; it is the one the schema's authors already had
   in mind for exactly this shape.
4. **The location and title both say template, not standard.** #1344's file lives
   under `templates/`, not `standards/`; its issue title is the plain noun "policy," in
   the same naming family as #1330 "component" and #1338 "flow," not a second
   "documentation-standard"-shaped title. A second standards-track document would not
   have been filed in the templates batch.

**This reading is recorded as an INFERENCE at confidence 0.8 (High, per this corpus's
own confidence convention) in the front matter, not asserted as a FACT.** The four
points above are read directly from their sources; the conclusion that they add up to
"general template, narrower instance" rather than "coincidence" is this author's step,
and a competent reader given only those same four points would very likely land on the
same conclusion -- which is what the High band means, not certainty.

**What this settles, and what it does not.** This template's *Required sections* below
state the general shape every policy-shaped node needs. #1313, once merged, is expected
to add the `standards/`-specific extras on top -- a fixed H1 string, a restate-ban tied
specifically to the schema and validator it discusses, a deference table naming those
sources by name. **This document does not restate #1313's content and does not amend
it**; it links to it as the worked narrower instance, per D9-style non-duplication
practice already established in this corpus. Whether #1313, once merged, actually
declares `implements: corpus-template-policy` is that node's own edit to make, not
something this template can decide on its behalf -- named as unverified below rather
than asserted as settled.

## Required sections

A corpus node using this template must carry the following in its body, in addition to
whatever schema-required front matter `node.schema.json` demands of every node.

1. **Scope and authority.** States three things, per P2 below: what the node governs,
   what grants it authority, and which source wins when it and that source disagree.
2. **MUST.** Every binding requirement, each carrying a stable identifier.
3. **SHOULD.** Every departable-with-reason guidance item, separated from MUST -- never
   one mixed list.
4. **Enforcement.** What actually checks each requirement (mechanical, review, or
   nothing), and what a passing check does **not** establish about the node's subject.
5. **Exceptions and escalation.** How to depart from a requirement, or that there is no
   exemption, and where a case the node does not cover goes.
6. **Scope and omissions.** What the node does not cover and who owns each omission,
   and -- separately -- what its author expected to verify and could not.

Sections MAY be inserted between these six (an "Industry model" or "Worked example"
section, for instance); none of the six may be dropped, reordered relative to each
other, or left silently empty.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# Policy: [subject]

[One paragraph: what this node states binding requirements about, and for whom.]

## Scope and authority

**This node governs** [subject]. **Its authority comes from** [schema / ADR / decision
/ team charter -- name it]. **Where it and [that source] disagree, [that source] wins.**

## MUST

| # | Requirement |
|---|---|
| **[P1]** | [MUST statement, naming what enforces it or that nothing does] |

## SHOULD

| # | Guidance |
|---|---|
| **[Q1]** | [SHOULD statement] |

## Enforcement

[What checks each requirement today, and what a passing run does NOT establish.]

## Exceptions and escalation

[How to depart from a MUST or SHOULD, or that there is none, and where an uncovered
case is raised.]

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
````

## MUST

These bind any node built from this template. Requirement identifiers below (P1-P10)
are this template's own and are not a namespace a policy-shaped instance node needs to
reuse -- each such node numbers its own requirements starting fresh, per P4.

| # | Requirement |
|---|---|
| **P1** | A policy-shaped node MUST carry the six sections in *Required sections*, in that relative order, none reordered among themselves. Additional sections MAY sit between them; none of the six may be absent or silently empty. |
| **P2** | The scope-and-authority section MUST state three things: what the node governs, what grants it authority, and which source wins when the two disagree. |
| **P3** | MUST requirements and SHOULD guidance MUST occupy two separate sections. One list with mixed modal verbs does not satisfy this. |
| **P4** | Every requirement MUST carry a short identifier, unique within the node and stable once published. A requirement that cannot be named cannot be cited in a review, granted an exception, or referred to by another node. |
| **P5** | Every requirement MUST name what enforces it, or state that nothing does. "Nothing does" is a permitted and common answer for a corpus whose checker discards the document body before validation runs; leaving the question unanswered is not. |
| **P6** | The enforcement section MUST state what a passing validation run does **not** establish about the node's subject. A section naming only what is checked overstates the check. |
| **P7** | The exceptions-and-escalation section MUST say either how to depart from the node's requirements, or that there is no exemption -- and, either way, where a case the node does not cover goes. |
| **P8** | The scope-and-omissions section MUST carry two distinct things: what the node does not cover together with who owns each omission, and -- separately -- what its author expected to verify and could not. A boundary and a confidence disclosure are different disclosures, per `AGENTS.md` step 8. |
| **P9** | A policy-shaped node MUST NOT restate content owned by the schema, the validator, an accepted decision, or a narrower template governing its own family (see *A note on `type`*'s definition of "family"). It links instead. Nothing reads body prose, so a copy that goes stale stays green forever. |
| **P10** | The H1 MUST be `# Policy: <subject>`, unless a narrower template for the node's specific family states its own convention (for example #1313's `# Standard: <topic>` for documents under `standards/`), in which case the narrower convention wins, per this template's own Precedence rule. |

## SHOULD

| # | Guidance |
|---|---|
| **Q1** | Worked examples SHOULD be drawn from this repository rather than invented. An invented example cannot go stale, which sounds like a virtue and means the node was never tested against anything real. |
| **Q2** | A policy-shaped node SHOULD carry a short "for X, read Y" table of the sources it defers to under P9, so a reader who arrived for the duplicated content is sent somewhere rather than left to search. |
| **Q3** | A policy-shaped node SHOULD name the boundary cases where its own requirements are hard to apply, and say which way each goes. The cases an author found difficult are the cases a reader will bring. |
| **Q4** | Top-level sections SHOULD NOT be numbered. They are looked up by name, and a number that shifts when a section is inserted breaks every reference made to it. Requirement identifiers under P4 are the stable handle; section numbers are not. |

## Enforcement

**Nothing automated enforces any requirement on this page, or on any node built from
it.** Verified directly rather than assumed: `validate.py`'s `_load_frontmatter`
splits a node's text on the frontmatter delimiter and discards the remainder into a
variable no other function reads. The body is not passed to anything -- not "not
currently inspected," discarded before any check runs, for every node in every
directory.

**The checker does not know what a policy-shaped node is, either.** Its only two
directory-keyed rules are `EXCLUDED_TOP_LEVEL_DIRS = {"schema"}`, which stops `schema/`
from being validated at all, and a rule that reports a stray non-`.md` file outside
`generated/` and rejects it regardless. Neither one distinguishes `templates/` from
`standards/` from any other directory beneath the corpus root. A node under
`templates/` validates exactly like a node anywhere else -- `templates/` and
`standards/` are conventions authors hold, not namespaces the tooling recognises.

**What a green validation run does not establish about a policy-shaped node**, stated
here because P6 requires every such node to say this about itself:

| Not established | Consequence |
|---|---|
| That the six required sections are present, or in order | A one-section node validates |
| That MUST and SHOULD are separated | A single mixed list validates |
| That requirements carry identifiers | An unciteable requirement validates |
| That a requirement names its own enforcement | Silence on enforcement validates |
| That the H1 follows P10 | Any H1, or none, validates |
| That a MUST or SHOULD statement is itself well-founded | Front-matter `evidence` entries are checked structurally (a citation resolves to a real file); the normative prose sentence itself is never compared against anything |

**Enforcement is the pull-request review**, by design and not by omission. ADR-0028
chose Markdown specifically so the corpus would be reviewed as a human-read diff, and
named that review as the enforcement mechanism the rest of the corpus contract depends
on. This template exists to give that reviewer something concrete to check a
policy-shaped node against, the same way #1313 exists to give a reviewer something to
check a standard against.

## Exceptions and escalation

**There is no exemption from carrying a section.** The six in *Required sections* are
structural; a node with nothing to say in one of them writes the section and says so.
A missing section is indistinguishable from an oversight, which is exactly what a
reviewer scanning for a gap cannot afford.

**A SHOULD is departed from in the open, not waived.** Q1-Q4 are guidance; a
policy-shaped node may do otherwise, but it says which one it departed from and why, in
the section the guidance would have applied to.

**A requirement whose application is disputed is a judgement, not an exception.** The
author records the tension and names it in the pull request; the reviewer decides. If
the two do not agree, the disagreement is filed as an issue against this template,
because a rule two people read differently is a defect in the rule.

**A case none of this covers is escalated, not invented.** Raise it as an issue against
parent Feature #605 describing the document that was needed and could not be written.
Do not widen this template locally to fit -- a policy-shaped node that each author
quietly reinterprets has stopped being one, and no check will notice.

**`status: flagged` is not the escape hatch.** It means what ADR-0029 says it means --
read it there rather than trusting a copy here, which is what P9 forbids and why. It is
a statement about a node's evidence carrying an unresolved conflict, not a substitute
for meeting a requirement here.

## Scope and omissions

**This node covers** what a corpus node's body must contain when that node states
binding MUST/SHOULD requirements about some subject: the required sections, how a
requirement is identified and cited, the industry model (RFC 2119, plus this
repository's own prior use of it) the shape adapts, and the explicit boundary against
#1313/documentation-standard, the one narrower instance drafted so far.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How normative language is worded beyond the MUST/SHOULD/MAY keywords themselves -- register, tone | #1320 |
| Which front-matter fields a node carries, and the rules between them | `node.schema.json`, and #1315 |
| How many ideas one node may hold | #1307, which states it generically over corpus nodes and so already binds a policy-shaped node without restatement here |
| Who reviews a corpus change, against what checklist, with what authority -- this document names review as the enforcement mechanism and says nothing about how it is conducted | #1322 |
| The specific extra conventions a corpus **standard** document carries on top of this shape | #1313/documentation-standard (unmerged at authoring time) |
| Documentation forms that are not normative -- reference, concept, procedure, and the rest | #1326-#1351's other templates |
| The human-facing entry point to the corpus | #639 |

Those issue numbers were looked up by subject, not inferred from a range, per
`AGENTS.md`'s own warning against doing the latter.

**It does not govern ordinary content nodes.** A concept, component, or reference node
is not a policy-shaped node and this template's requirements do not apply to it.

**Relationships.** A node built from this template:

- **should** declare `depends-on` toward `corpus-agents`, the same way this template
  does, when its authority is derived from `AGENTS.md`'s creation and evidence rules
  rather than original to itself.
- **may** declare `implements` toward this template's id (`corpus-template-policy`)
  once this node is merged, if the author wants the generated `implemented-by` edge --
  per `relationships.schema.json`'s own worked example, "source is the concrete
  realization of target (e.g. a template instance of a standard)." This is the edge
  #1313/documentation-standard is positioned to declare once both nodes are merged, per
  *Boundary* above; it is not added here on #1313's behalf.
- **may** declare `references` toward a concept/explanation node that motivates the
  policy's subject, when reading the policy alone would leave a reader without the
  conceptual grounding to apply it.
- **must**, per `AGENTS.md` step 9, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: `depends-on: corpus-agents` -- real and
resolvable, `corpus-agents` being loaded from `origin/launchpad` at the recorded
revision, and a genuine dependency: this template's *Precedence* section states plainly
that its authority is derived from `AGENTS.md`'s rules, not original. No edge to
#1313/documentation-standard: it is unmerged at this node's authoring time and not a
valid relationship target, and the directionality described above runs from a standard
document toward this template, not the reverse -- this node has nothing to declare
against #1313 even once #1313 merges. No edge to any other sibling in this batch: none
of the other five in-flight template issues (#1330, #1338, #1339, #1341, #1350) are
policy-subject-shaped instances of this template, and all six are authored in parallel
with no merge ordering between them.

**Evidence expectations specific to a policy-shaped node.** The corpus-wide rules in
`AGENTS.md` apply unchanged -- `FACT` means the author opened the cited source,
`INFERENCE` means the author reasoned to the claim and rated the reasoning,
`TEAM_KNOWLEDGE` means an uncorroborated statement attributed to whoever said it.
Three expectations follow specifically from a MUST/SHOULD document's own shape:

- **A MUST or SHOULD requirement's normative text is not itself an evidence-ledger
  claim** -- it is the node exercising the authority named in *Scope and authority*,
  the same way this template's own P1-P10 are not each backed by a citation. What
  *does* need a citation is any factual justification the node gives for why the
  requirement exists, or any claim about what currently enforces it.
- **A precedence claim ("X wins over Y") MUST cite the actual authority** -- the
  schema, an ADR, the validator -- not merely assert an ordering. This template's own
  *Precedence* section names `node.schema.json`, `validate.py`, an accepted ADR, and
  `AGENTS.md` as the sources it defers to, each independently verifiable.
- **A claim that something is or is not enforced MUST be checked, not assumed.** This
  template's own Enforcement section cites the exact line in `validate.py` that
  discards a node's body, rather than asserting it from memory or from a sibling
  document's say-so.

## Note on Definition of Done

Issue `#1344`'s own Definition of Done carries the same boilerplate copied across
`#1326-#1351` -- "states scope and authority/source of the policy," "separates MUST
requirements from SHOULD guidance," "defines enforcement/checks and exception/
escalation process," "links decisions or higher-order policy instead of duplicating
them" -- and, unusually among this batch's issues, that boilerplate is close to right
by coincidence rather than by residue: this node's *subject is itself* a MUST/SHOULD
policy shape, so the standards-track checklist and this template's own required
sections overlap almost completely. That overlap is explained, not assumed -- see
*Boundary* above for why it happens and where it stops. The **real** acceptance bar
remains parent Feature `#605`'s sentence: *"every template states its purpose,
required sections, evidence expectations and the industry model/standard it adapts."*
This node is built against that sentence -- *Required sections*, *Evidence
expectations*, and *Industry model this template adapts* above answer it directly --
with the coincidental fit to #1344's own DoD recorded here rather than left for a
reader to notice and wonder whether it was deliberate.

**Expected but not verified when this node was written:**

- **#1313/documentation-standard is an unmerged draft.** Every claim about it above is
  pinned to its branch head (`8a4b8425089cf64bb3cac990ac8519429c11d7ca`) and true at
  that revision. Whether it still reads the same way after its own review rounds, and
  whether it ends up declaring `implements` toward this template once both are merged,
  is unknown and not this node's to decide.
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **No second policy-shaped instance node exists yet to test this template against.**
  `confidence.md` and `decision-references.md` predate this template and were not
  written to it; whether an author actually following this template's *Required
  sections* end to end produces a document as usable as those two is untested.
- **Whether #1313, once merged, needs any edit to conform to P1-P10 as stated here** is
  not established. Its own text already carries an equivalent six-section shape and
  separated MUST/SHOULD, so conformance looks likely on inspection, but this node does
  not audit #1313's diff clause-by-clause -- that check belongs to whoever reconciles
  #1313 against this template once both are on `launchpad`.
