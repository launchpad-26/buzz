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
  - statement: "Those same four standards carry four different H1 title forms, disagree on whether top-level sections are numbered, and name their normative and enforcement sections four different ways."
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
requirements on corpus content. Those live under
`launchpad/docs/corpus/standards/`, they declare `type: governance`, and there are
nineteen of them in flight. It governs how such a document is built — which sections it
carries, how it states a requirement, how it says what holds that requirement — and
nothing about any particular subject one of them covers.

**It does not govern what those standards say.** Whether a citation may name a line,
what a confidence number means, how many ideas a node may hold: each is its own
standard's, and this document has no opinion on any of them.

**Where the authority comes from.** Every task in this batch carries the same four
required-content clauses — state scope and authority, separate MUST from SHOULD, define
enforcement and an exception process, link decisions rather than duplicate them. They
are the requirement; this node is only where they stop being a checklist inside issue
bodies and become something the corpus itself carries after those issues close.

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

## Exceptions and escalation

## Scope and omissions
