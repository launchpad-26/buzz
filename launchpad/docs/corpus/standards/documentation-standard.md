---
id: corpus-standard-documentation-standard
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109."
    entry_class: FACT
    evidence:
      - "commit ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109"
  - statement: "The deterministic checker never reads a node's Markdown body: the front matter is split off and the remainder is discarded before any check runs."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The checker applies no rule keyed to a subdirectory, so a node under standards/ is validated exactly like a node anywhere else beneath the corpus root."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "ADR-0028 names the human-read pull-request diff as the enforcement mechanism the corpus depends on, and chose Markdown over a machine-readable record format for that reason."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The schema's type enum contains governance and contains no policy value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The instruction node defers per-type standards and per-type templates to tasks #1307-#1351 and states that until they land there is no per-type template to follow."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Four corpus standards drafted in parallel independently converged on the same five-part shape: a scope-and-authority opening, separated normative requirements, an enforcement section, an exceptions-and-escalation section, and a closing scope-and-omissions section."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/b899609f677317ebde4ba16620b3dd23b1510d62/launchpad/docs/corpus/standards/atomicity.md"
      - "https://github.com/launchpad-26/buzz/blob/5f7e1330b2d422129bb92148c5d4a2ee4cc8958e/launchpad/docs/corpus/standards/code-references.md"
      - "https://github.com/launchpad-26/buzz/blob/e8ba1ec8e2d605ecfbc6a7d9ee0ca058e95a2d24/launchpad/docs/corpus/standards/confidence.md"
      - "https://github.com/launchpad-26/buzz/blob/8eb2d2658a707c025ba7bcf1c2f2063f5de2e387/launchpad/docs/corpus/standards/decision-references.md"
  - statement: "Those same four standards carry four distinct H1 strings following three different title conventions, disagree on whether top-level sections are numbered, and name their normative and their enforcement sections four different ways each."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/b899609f677317ebde4ba16620b3dd23b1510d62/launchpad/docs/corpus/standards/atomicity.md"
      - "https://github.com/launchpad-26/buzz/blob/5f7e1330b2d422129bb92148c5d4a2ee4cc8958e/launchpad/docs/corpus/standards/code-references.md"
      - "https://github.com/launchpad-26/buzz/blob/e8ba1ec8e2d605ecfbc6a7d9ee0ca058e95a2d24/launchpad/docs/corpus/standards/confidence.md"
      - "https://github.com/launchpad-26/buzz/blob/8eb2d2658a707c025ba7bcf1c2f2063f5de2e387/launchpad/docs/corpus/standards/decision-references.md"
  - statement: "The atomicity standard states its one-idea requirement generically over corpus nodes rather than per node type, so it already binds a governance-typed standard document without restatement."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/b899609f677317ebde4ba16620b3dd23b1510d62/launchpad/docs/corpus/standards/atomicity.md"
  - statement: "ADR-0029 makes flagged the state for two authoritative sources of the same claim type in conflict, held for a human rather than resolved by the author."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Issue #1313's definition of done requires this node to state scope and authority, to separate MUST requirements from SHOULD guidance, to define enforcement and an exception/escalation process, and to link decisions rather than duplicate them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1313 definition of done"
  - statement: "All nineteen standards issues #1307-#1325 carry those four required-content clauses verbatim, and so do all five sampled template issues #1326, #1330, #1344, #1346 and #1351, which makes them batch-wide document requirements rather than a contract specific to standards."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issues #1307-#1325 and #1326, #1330, #1344, #1346, #1351 definition-of-done clauses"
  - statement: "Because no check reads body prose, every requirement stated in this standard and in every sibling standard is held by pull-request review alone."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
    confidence: 0.9
---

# Standard: corpus standards

What a corpus **standard** must itself be and contain. Look up the requirement you
need; this is a reference, not a tutorial.

## Scope and authority

**This standard governs the shape of one kind of document:** a corpus node that states
requirements on corpus content. Those live under `launchpad/docs/corpus/standards/`,
they declare `type: governance`, and there are nineteen of them in flight. It governs
how such a document is built — which sections it carries, how it states a requirement,
how it says what holds that requirement — and nothing about any particular subject one
of them covers.

`governance` is the type because it is the enum member that fits and because there is no
alternative: the schema's `type` enum has no `policy` value. If a standard ever needs
one, that is a schema change under `launchpad/docs/corpus/schema/COMPATIBILITY.md`, not
a choice an author makes per node.

**Why this document exists at all.** The instruction node hands per-type standards and
per-type templates to the tasks in this batch and says outright that until they land
there is no per-type template to follow. Nineteen standards are being written against
that gap at once. Four are far enough along to compare, and they show both halves of the
problem: left to themselves, independent authors converged on the same five-part
shape — a scope-and-authority opening, separated normative requirements, an enforcement
section, an exceptions-and-escalation section, and a closing scope-and-omissions
section — and then diverged on nearly every surface detail of it. Convergence is the
evidence that the shape is the natural one. Divergence is the evidence that nothing
holds it.

**It does not govern what those standards say.** Whether a citation may name a line,
what a confidence number means, how many ideas a node may hold: each is its own
standard's, and this document has no opinion on any of them.

**Where the authority comes from.** Every task in this batch carries the same four
required-content clauses — state scope and authority, separate MUST from SHOULD, define
enforcement and an exception process, link decisions rather than duplicate them. This
node's own task, #1313, requires exactly those four of it, as every sibling task
requires them of its own node. They are the requirement; this document is only where
they stop being a checklist inside issue bodies and become something the corpus itself
carries after those issues close.

Be precise about what that evidence shows: those four clauses are **batch-wide**, not
specific to standards. The template tasks sampled alongside the standards tasks carry
them verbatim too. This document scopes them to `standards/` because that is the family
it sits in and the only one with drafted documents to check against — not because the
clauses single that family out. The templates' own required-content rule is a different
list and is not this node's.

**Why the shape is the thing worth standardising.** ADR-0028 chose Markdown over a
machine-readable record format because the corpus is reviewed at the pull request that
changes it, and named that human-read diff as the enforcement mechanism the rest of the
corpus contract depends on. A reviewer reading a diff finds a missing requirement by
knowing where it should have been. Sections in a predictable order are not house style
here; they are what makes the one enforcement mechanism the corpus has usable.

**Precedence.** Where this document and `node.schema.json`,
`launchpad/project-intelligence/corpus/validate.py`, an accepted ADR, or
`launchpad/docs/corpus/AGENTS.md` disagree, **they win** and this one has drifted.
Where it and a topic standard disagree about that standard's own subject, **the topic
standard wins** — it is the more specific rule and the one written with the subject in
front of it. Two topic standards in conflict is not this document's to settle;
ADR-0029's escalation applies, as it does to any same-claim-type conflict.

**This document obeys its own requirements.** It is the worked example: its sections,
in their order, are D1's list. A standard that could not be written to its own rule
would be evidence the rule is wrong.

## MUST

| # | Requirement |
|---|---|
| **D1** | A standard MUST carry these six sections, in this order and no other: *Scope and authority*, *MUST*, *SHOULD*, *Enforcement*, *Exceptions and escalation*, *Scope and omissions*. Additional sections MAY sit between them; none of the six may be absent, and a section that is genuinely empty says so rather than being dropped. |
| **D2** | The scope-and-authority section MUST state three things: what the standard governs, what grants it authority, and which source wins when it and that source disagree. |
| **D3** | MUST requirements and SHOULD guidance MUST occupy two separate sections. One list with mixed modal verbs does not satisfy this, however clearly the verbs are written. |
| **D4** | Every requirement MUST carry a short identifier, unique within the standard and stable once published. A requirement that cannot be named cannot be cited in a review, granted an exception, or referred to by another node. |
| **D5** | Every requirement MUST name what enforces it, or state that nothing does. "Nothing does" is a permitted and common answer; leaving the question unanswered is not. |
| **D6** | The enforcement section MUST state what a passing validation run does **not** establish about the standard's subject. A section naming only what is checked overstates the check. |
| **D7** | The exceptions-and-escalation section MUST say either how to depart from the standard's requirements, or that there is no exemption — and, either way, where a case the standard does not cover goes. |
| **D8** | The scope-and-omissions section MUST carry two distinct things: what the standard does not cover together with who owns each omission, and — separately — what its author expected to verify and could not. A boundary and a confidence disclosure are different disclosures. |
| **D9** | A standard MUST NOT restate content owned by the schema, the validator, an accepted decision, or another standard. It links instead. Nothing reads body prose, so a copy that goes stale stays green forever. |
| **D10** | The H1 MUST be `# Standard: <topic>`, with the topic matching the subject the node's `id` names. |

## SHOULD

| # | Guidance |
|---|---|
| **G1** | Worked examples SHOULD be drawn from this repository rather than invented. An invented example cannot go stale, which sounds like a virtue and means the standard is never tested against anything real. |
| **G2** | A standard SHOULD carry a short "for X, read Y" table of the sources it defers to under D9, so a reader who arrived for the duplicated content is sent somewhere rather than left to search. |
| **G3** | A standard SHOULD name the boundary cases where its own requirements are hard to apply, and say which way each goes. The cases an author found difficult are the cases a reader will bring. |
| **G4** | Top-level sections SHOULD NOT be numbered. These are looked up by name, and a number that shifts when a section is inserted breaks every reference made to it. Requirement identifiers under D4 are the stable handle; section numbers are not. |

## Enforcement

**Nothing automated enforces any requirement on this page, and nothing can.**

The deterministic checker splits a node's front matter off and discards the body before
any check runs. Not "does not currently inspect it" — the body is not passed to
anything. Every check the corpus has is therefore a check on front matter, ids,
relationship targets, citation forms and file placement, and none of those is a property
of how a document's sections are arranged. `AGENTS.md` and
`launchpad/project-intelligence/corpus/validate.py` are where what *is* checked lives;
D9 says not to copy it here.

A standard with none of D1's six sections passes exactly as cleanly as this one. So does
a standard whose H1 is anything at all, whose requirements have no identifiers, and
whose deference table points at files that were deleted a year ago.

**Nor does the checker know what a standard is.** It applies no rule keyed to a
directory: a node under `standards/` is validated identically to a node anywhere else.
`standards/` is a convention held by authors, not a namespace the tooling recognises.

**Enforcement is the pull-request review**, and that is by design rather than by
omission. ADR-0028 chose the canonical representation specifically so the corpus would
be reviewed as a human-read diff, and named that review as the enforcement mechanism the
rest of the corpus contract depends on. This standard exists to give that reviewer
something to hold: D1-D10 are the checklist, and G1-G4 are what to ask for when the
checklist passes and the document is still hard to use.

**What a green run does not establish about a standard**, stated plainly because D6
requires every standard to say this about its own subject:

| Not established | Consequence |
|---|---|
| That the six sections are present, or in order | A one-section standard validates |
| That MUST and SHOULD are separated | A single mixed list validates |
| That requirements have identifiers | An unciteable requirement validates |
| That a requirement names its enforcement | Silence on enforcement validates |
| That a deference table's targets exist | Only citations in the `evidence` ledger are resolved; a link in body prose is never opened |
| That the H1 follows D10 | Any H1, or none, validates |

The only failure mode any of this has is a reviewer who does not look. That is the same
failure mode the corpus already accepts elsewhere — the instruction node names a ledger
carrying more than one commit-only `FACT` as a convention a reviewer has to hold because
no check will — and this standard belongs to that class rather than introducing it.

## Exceptions and escalation

**There is no exemption from carrying a section.** D1's six are structural, and a
standard with nothing to say in one of them writes the section and says so. "Nothing
here yet, owned by #NNNN" is a useful sentence; a missing section is indistinguishable
from an oversight, which is exactly what a reviewer scanning for a gap cannot afford.

**A SHOULD is departed from in the open, not waived.** G1-G4 are guidance, so a standard
may do otherwise — but it says which one it departed from and why, in the section the
guidance would have applied to. An unexplained departure is not an exercise of
discretion; it is indistinguishable from not having read this page.

**A requirement whose application is disputed is a judgement, not an exception.** The
author records the tension in the standard and names it in the pull request; the
reviewer decides, and that is where it ends almost always. If the two do not agree, the
disagreement is filed as an issue against this standard, because a rule two people read
differently is a defect in the rule.

**A standard written before this one is non-conforming, not exempt.** Bringing it into
shape is an ordinary edit to that node by whoever owns it, not a migration and not this
node's to perform. Four already exist in this position; see *Scope and omissions*.

**A case none of this covers is escalated, not invented.** Raise it as an issue against
the parent feature #605 describing the document you needed to write and could not. Do
not widen a requirement locally to fit: a standard that each author quietly adjusts has
stopped being one, and no check will notice.

**`status: flagged` is not the escape hatch.** ADR-0029 gives that state one meaning:
two authoritative sources of the same claim type contradict each other and no human has
resolved it. It is a statement about a node's evidence. A requirement you find
inconvenient, or a section you would rather not write, is neither.

## Scope and omissions

**This document covers** which sections a corpus standard carries and in what order,
how it states and identifies a requirement, how it declares what enforces that
requirement, how it defers rather than duplicates, and what its H1 looks like.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How normative language is worded — the MUST/SHOULD/MAY register itself | #1320 |
| Which front-matter fields a standard carries, and the rules between them | `node.schema.json`, and #1315 |
| How many ideas one node may hold | #1307, which states it generically over corpus nodes and so already binds a standard without restatement here |
| Who reviews a corpus change, against what checklist, with what authority — this document names review as the enforcement mechanism and says nothing about how it is conducted | #1322 |
| File naming, id naming, and whether `standards/` is the settled directory for these documents | #1319 |
| The required shape of a per-node-type **template**, which is a different document kind with its own required-content list | #1326-#1351 |
| The human-facing entry point to the corpus | #639 |

Those issue numbers were looked up by subject rather than inferred from a range.

**It does not govern ordinary content nodes.** A concept, component or runbook node is
not a standard and D1-D10 do not apply to it. The instruction node governs how any node
is created; per-type templates will govern their shapes.

**The four standards already in flight do not conform to this one.** At the revisions
cited in the ledger, they carry four distinct H1 strings across three conventions, one
numbers its top-level sections and three do not, and they name their normative sections
four different ways (`Requirements` with `MUST`/`SHOULD` beneath it; numbered `MUST` and
`SHOULD`; `Requirements` and `Guidance`; bare `MUST` and `SHOULD`) and their enforcement
sections four different ways, one of which does not use the word at all. That divergence
is this document's evidence and its cost in the same breath: the rule is retroactive on
four documents whose pull requests are open, and reconciling them is their owners' work
under the exceptions process above, not something this node does to them.

**No `relationships` in this node's front matter.** Not because there is nothing to
point at — `corpus-agents` exists on this branch and this node depends on it. It is
absent because a relationship target must resolve on the branch being **merged into**,
and on `launchpad` no corpus node exists yet at all. An edge declared here would validate
cleanly in this worktree and be a hard error in CI. The reason is merge order; the edges
are worth adding in one pass once the batch has landed.

**Expected but not verified when this node was written:**

- **No CI run has exercised this node.** Every claim about the checker comes from
  reading it and running it locally in this worktree. The CI workflow that runs it was
  not read for this node.
- **The four sibling standards are unmerged drafts.** Each claim about them is pinned to
  a revision and true at it. Whether the merged versions still look that way after their
  own review rounds is unknown, and nothing here tracks it.
- **The template issues were sampled, not enumerated.** The claim that the four
  required-content clauses are batch-wide rests on all nineteen standards issues and on
  five of the twenty-six template issues, not on all of them.
- **No agent harness was observed reading this file.** The same gap the instruction node
  records about itself.
- **Nothing establishes `standards/` as the settled location.** No schema field, checker
  rule or decision fixes it; it is the path the task named and the four siblings used.
  That is convention, and #1319 owns turning it into a rule or replacing it.
