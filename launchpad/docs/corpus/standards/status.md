---
id: corpus-standard-status
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 919886b4192df6251de50c547548ecae5d85afce."
    entry_class: FACT
    evidence:
      - "commit 919886b4192df6251de50c547548ecae5d85afce"
  - statement: "status is a required field on every corpus node's front matter and is a closed five-value enum: draft, active, deprecated, retired, flagged."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The schema's own description of the status field defines only the flagged value in prose; draft, active, deprecated and retired carry no defined semantics anywhere in the schema beyond their being valid enum members."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "flagged is ADR-0029's unestablished/flagged state: two same-claim-type authoritative sources contradict each other and a human has not yet resolved it. It is explicitly not a generic low-confidence marker."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "ADR-0029 requires the corpus author to stop and record a same-claim-type contradiction rather than resolve it, and requires the affected node to stay unestablished/flagged until a human decides; this is treated as a security decision because incorrect precedence could present stale or unauthorized behavior as current policy."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Retiring a node is documented as a status change, not a deletion: the file stays on disk, the checker keeps loading the node, and inbound relationships keep resolving; the id is never reused or renamed."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Deleting a node instead of retiring it breaks every relationship whose target names that node's id, because a relationships[].target naming an id no loaded node carries is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "validate.py contains no logic that reads or branches on a node's status value beyond generic JSON Schema enum membership checking: it does not compare two nodes' statuses against each other, does not detect a flagged node's unresolved conflict, and does not restrict which status a node may transition to or from. The only occurrences of the string \"status\" in the file belong to an unrelated per-citation ValidationReport.status field (\"ok\"/\"error\"/\"unverified\"), not to the node's front-matter status."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "launchpad/AGENTS.md requires agents to draft issues, PRs and ADRs in full but never to decide an ADR outcome or approve a PR themselves -- the same agents-propose-humans-decide boundary that ADR-0029's escalation route for a flagged node relies on."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "Node front matter rejects any field beyond the seven node.schema.json names (id, type, status, origin, audiences, evidence, relationships), so there is no separate schema field for recording why a status was changed or what a deprecated node is being replaced by -- that has to live in the body or in an evidence entry's statement."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Decision records (ADRs) carry their own, differently-shaped status field in their own front matter -- values seen in this repository include Accepted and \"Superseded by ADR-YYYY\" -- which is a separate vocabulary from the corpus node schema's status enum this document governs."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "launchpad/project-intelligence/CONTRACT.md describes its own status, in its header, as \"proposed, not ratified\" -- a third status vocabulary again distinct from both the corpus node schema's enum and the decision-record status field."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "Because nothing in node.schema.json or validate.py restricts which status a node may move to or from, a status can be changed in either direction on the same file -- including, for example, back out of retired -- without any check objecting; this is a negative claim about the absence of transition-restricting logic across both files, not a positive statement of intended behavior."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.6
  - statement: "Issue #1311, \"task: document corpus standard for deprecation\", parented to PRD #605 and targeting launchpad/docs/corpus/standards/deprecation.md, is open and unlanded at the recorded revision, and is the dedicated task for the deprecated status's full policy and procedure."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1311"
  - statement: "Issue #1410, \"task: encode ADR-0029's claim-type classification and unestablished/flagged state in #605's schema/validator\", is open and unlanded at the recorded revision, and owns making flagged's escalation procedure mechanically enforced rather than a reviewer-and-author convention."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1410"
  - statement: "Issue #1323 requires this node to state the scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define an enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1323 definition of done"
relationships:
  - type: references
    target: corpus-agents
  - type: references
    target: corpus-standard-confidence
---

# Standard: `status`

What each value of a corpus node's `status` field means, which of those meanings this
document owns versus links to, and what an author or reviewer must do at each stage of
a node's lifecycle.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| The field's machine contract -- required, closed five-value enum | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of the front-matter fields | `launchpad/docs/corpus/schema/README.md` |
| Adding a sixth value to the enum | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| The full retirement procedure | `launchpad/docs/corpus/AGENTS.md` -- "Retiring a node" |
| Why `flagged` exists and how a conflict escalates | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| Citing a decision record as evidence, including a `flagged` conflict between two ADRs | `launchpad/docs/corpus/standards/decision-references.md` |
| `confidence` and why it is not a substitute for `flagged` | `launchpad/docs/corpus/standards/confidence.md` |
| Creating, updating and retiring a node -- the general procedure | `launchpad/docs/corpus/AGENTS.md` |
| The full `deprecated` policy and procedure, once it lands | Issue #1311 (unlanded at this writing) |

Those files are authoritative. Where this document and any of them disagree, **they
win** -- this one has drifted and should be fixed.

**This document restates the schema only where its own subject forces it to.** A
standard about `status` cannot omit the five values themselves, so *What each value
means* below names them. What is *not* restated: the retirement procedure (already
full in `AGENTS.md`), the `flagged` escalation mechanics (already full in `ADR-0029`
and in `corpus-standard-decision-references`), and the `deprecated` procedure, which
this document does not yet have anywhere to point to and does not invent in its place.

## Scope and authority

**This standard governs** the `status` key in a corpus node's front matter -- the one
place `draft`, `active`, `deprecated`, `retired` and `flagged` exist as a governed
vocabulary. It states what each value means, when a node may carry it, what an author
must do when setting it, and what nothing currently checks.

**It does not govern** two other fields that are also spelled "status" in this
repository but are different vocabularies entirely:

- A decision record's own front-matter `status` (`Accepted`, `Superseded by ADR-YYYY`,
  and so on) is owned by `launchpad/decisions/README.md`.
- `launchpad/project-intelligence/CONTRACT.md` describes its own status, in its header,
  as "proposed, not ratified" -- a specification-ratification vocabulary that no
  document in this repository currently defines the mechanics of.

Confusing either of those with a corpus node's `status` is an easy mistake because the
word is the same; the schema, the enum members and the authority behind them are not.

**Its authority is derived, not original, for two of the five values and original for
the rest.** `flagged`'s meaning is `ADR-0029`'s, encoded in `node.schema.json`'s own
description; this document does not relitigate it, only applies it. `retired`'s
procedure is `AGENTS.md`'s "Retiring a node" section in full; this document names what
the value means and sends an author there for how. For `draft`, `active` and
`deprecated`, no other document in this repository defines operational semantics
today -- the schema enumerates the three names and nothing more. This document
supplies that meaning as guidance, not as something restated from an existing
authority, and says so plainly rather than dressing an original judgment up as a
citation to something that does not exist. `deprecated`'s own full procedure is
carved out to Issue #1311 rather than authored here, per the one-idea-per-node rule:
a corpus standard for deprecation is a second, independently maintainable knowledge
node, not a section of this one.

## What each value means

| Value | Meaning | Who defines it |
|---|---|---|
| `draft` | The node is being authored or substantially reworked. Its claims have not yet been reviewed against `AGENTS.md`'s creation procedure to completion, and a reader should not treat it as settled guidance. | This document (guidance, not schema-enforced) |
| `active` | The node is current: its evidence ledger is believed sound at the recorded revision, and it is safe to cite, depend on, and treat as the corpus's answer on its subject, subject to the usual FACT/INFERENCE/TEAM_KNOWLEDGE caveats every claim already carries. | This document (guidance, not schema-enforced) |
| `deprecated` | The node is still loaded and still resolves, but is on its way out -- a replacement exists or is planned. What exactly that requires of an author is Issue #1311's, unlanded as of this writing. This document names the value's place in the lifecycle and no more. | Issue #1311 (not yet written) |
| `retired` | The terminal lifecycle state. The node's subject is no longer current or has been fully replaced; the file stays so the id and inbound relationships keep resolving, and the id is spent permanently. Full procedure: `AGENTS.md`, "Retiring a node". | `launchpad/docs/corpus/AGENTS.md` |
| `flagged` | Two same-claim-type authoritative sources contradict each other and a human has not resolved it. Not a lifecycle stage and not a confidence marker -- a live, unresolved conflict. Full procedure: `ADR-0029` and `corpus-standard-decision-references`'s "When two accepted decisions conflict". | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |

**The ordinary path** is `draft` while a node is being written, `active` once its
ledger and body are complete and reviewed, and eventually either `deprecated` then
`retired`, or directly `retired`, when the subject stops being current. `flagged` is
not a stage on that path -- it can interrupt any node that carries `active` (or, in
principle, any other status) the moment a genuine same-claim-type conflict surfaces,
and it clears only when a human resolves the conflict, not on a timer or by review
alone.

## MUST

These are enforced at two different strengths. MUST 1 is structural -- the schema
rejects the node either way. The rest are enforced by review; a reviewer who lets one
through has approved a defect. *Enforcement, and where it stops* below says exactly
which is which.

1. **`status` MUST be exactly one of the five schema-defined values.** No sixth value,
   no free text. Adding a value to the enum is a schema change under
   `launchpad/docs/corpus/schema/COMPATIBILITY.md`, not something an author does in a
   node.
2. **`flagged` MUST be used only for ADR-0029's specific case** -- two same-claim-type
   authoritative sources contradicting each other, unresolved -- **and MUST NOT be
   used as a general low-confidence marker.** A node whose claims merely feel
   uncertain is not flagged; see `corpus-standard-confidence` for what to do with an
   uncertain claim instead, and *Exceptions and escalation* below for what actually
   qualifies.
3. **A node's own author MUST NOT resolve a `flagged` conflict by picking a side.**
   `flagged` is cleared only by the human-decision route ADR-0029 and
   `corpus-standard-decision-references` describe -- a `type:adr` issue, argued,
   decided by a human, written up as a decision record. Silently editing the node back
   to `active` without that happening is exactly the failure ADR-0029 exists to
   prevent.
4. **A node MUST be retired by changing `status` to `retired`, never by deleting the
   file**, and its `id` **MUST NOT** be reused or renamed once retired. This is the
   single most consequential rule on this list: deletion is what breaks every
   relationship pointing at the node, while a status change keeps them resolving. Full
   procedure, including what to do about inbound edges: `AGENTS.md`, "Retiring a
   node".
5. **`deprecated` and `flagged` MUST NOT be used interchangeably to express doubt
   about a node.** They answer different questions: `deprecated` says "a replacement
   exists or is coming" -- a lifecycle fact about succession. `flagged` says "two
   authoritative sources disagree and nobody has settled it" -- a live conflict about
   truth. Marking a genuinely contradicted node `deprecated` instead of `flagged`
   sidesteps ADR-0029's escalation requirement without ever triggering it, because
   nothing distinguishes the two uses mechanically -- see *Enforcement, and where it
   stops*.
6. **Until Issue #1311's deprecation standard lands, an author moving a node to
   `deprecated` MUST record, in that node's own body, what is replacing it or that
   nothing is** -- the same disclosure `AGENTS.md`'s "Retiring a node" step 4 already
   requires for `retired`, applied here because no landed procedure exists yet to
   require it a different way. When #1311 lands, its procedure governs and this MUST
   defers to it.

## SHOULD

These are guidance. Depart from them with a reason.

- **Start a new node at `draft` while its evidence ledger and body are still being
  assembled**, and move it to `active` once `AGENTS.md`'s node-creation procedure is
  complete -- ledger written, claims classified honestly, scope-and-omissions section
  written. A green `validate.py` run does not mean a node is ready; it means the
  front matter is well-formed. Moving to `active` is a separate judgment call the
  checker cannot make.
- **Do not set `status: active` on a node you would not stand behind if a reader
  cited it today.** If a claim is not solid enough for that, the honest fix is either
  to keep working before flipping the status, or to name the gap in the
  scope-and-omissions section -- not to publish it as `active` because the schema
  accepts it either way.
- **When you retire or deprecate a node, look for what points at it** before you
  finish, per `AGENTS.md`'s own step for retirement. A relationship that should be
  repointed at a replacement, and one that should stay pointed at history, are
  different judgment calls; make them deliberately rather than leaving every inbound
  edge exactly as it was.
- **Prefer moving a node to `retired` over leaving it `deprecated` indefinitely.**
  `deprecated` without a plan is a status that never resolves; a reader gets no
  signal from a node that has said "replacement coming" for a year.
- **Do not flip `status` back and forth to relitigate a disagreement about a node's
  content.** If the disagreement is about whether a claim still holds, re-verify it
  against its source per `AGENTS.md`'s "Updating a node" procedure. If it is a genuine
  same-claim-type contradiction between two authoritative sources, that is `flagged`,
  not a status toggle. Neither case is served by changing the value and changing it
  back.

## Enforcement, and where it stops

**Enforced mechanically**, by `node.schema.json` through `validate.py`, in CI on every
change under the corpus root: `status` is present, and its value is one of the five
enum members. That is the entirety of what the checker verifies about this field --
confirmed by reading `validate.py` directly rather than assuming from the schema
alone: the file contains no logic keyed on a node's `status` value at all.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| Whether `flagged` is used only for ADR-0029's specific conflict, or as a general low-confidence marker | A misuse passes cleanly. Only a reviewer applying MUST 2 catches it. |
| Whether `deprecated` is used to sidestep a `flagged`-worthy conflict | Nothing distinguishes the two uses mechanically; a node mislabeled this way validates exactly like a correctly labeled one. MUST 5 is review-enforced only. |
| Whether a `flagged` node was resolved by a human decision or quietly edited back by its author | The checker treats every value as freely settable in either direction; nothing records how a transition happened, only what the value currently is. |
| Whether a `retired` node's inbound relationships were reconsidered | A retired node with stale inbound edges validates exactly like a healthy one -- `AGENTS.md`'s own point, and it applies with full force to the field this document governs. |
| Whether a status transition is even forward-moving | `node.schema.json` and `validate.py` place no ordering on the five values; a node can be moved from `retired` back to `active` on the same file without any check objecting, though nothing in this repository currently does so or explains what it would mean to. |
| Whether a node marked `active` is actually current | Never checked. Review is the trust mechanism for this, as for every other claim in the corpus -- a green run answers a structural question, not this one. |

The pattern is the same one `corpus-standard-confidence` names for its own field:
everything a schema can hold is held, and everything that requires reading the node
and knowing its history is not. Reviewing a `status` value means reading the node it
sits on, not just the value.

## Exceptions and escalation

**There is no exception process for MUST 1.** The enum is closed and structurally
enforced; a sixth value or free text does not merge. Changing the enum itself is a
schema change under `launchpad/docs/corpus/schema/COMPATIBILITY.md`, not an exception
granted in a node.

**When you are unsure whether a node qualifies for `flagged`,** apply the test
`corpus-standard-decision-references` already states for the decision-citation case,
generalized to any two authoritative sources of the same claim type: would a reader,
given both sources and nothing else, conclude they say different things about the
same claim? If yes, that is `flagged`, and the escalation route is fixed --
`ADR-0029` and `corpus-standard-decision-references`'s "When two accepted decisions
conflict" describe it in full and this document does not repeat it. If the
disagreement is between one authoritative source and something weaker (an inference,
team knowledge, a source of a different claim type), that is not a same-claim-type
conflict and ADR-0029's ordinary contextual ranking already resolves it without
`flagged`.

**Draft everything, approve nothing applies here as everywhere else in this
repository.** An agent may record a `flagged` conflict, write the escalation issue,
and draft the eventual decision record. An agent may not decide which side of a
`flagged` conflict is correct and may not clear the status itself on that basis.

**Anything this document does not answer is escalated, not invented.** In particular,
the full `deprecated` procedure is Issue #1311's to write, and whether a status
transition should ever be restricted (for example, whether `retired` should be
one-way) is not decided anywhere in this repository today -- see *Scope and
omissions*. Neither gets resolved by precedent inside a single node's body.

## Scope and omissions

**This document covers** what each of the five `status` values means, which of those
meanings it originates versus links to, the MUST and SHOULD rules for setting and
changing the value, and what enforcement does and does not reach.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full `deprecated` policy and procedure | Issue #1311, unlanded at this writing |
| A decision record's own `status` field | `launchpad/decisions/README.md` |
| How a specification becomes "ratified" (CONTRACT.md's own status vocabulary) | Undefined in this repository -- also named as a gap in `corpus-standard-decision-references` |
| Encoding ADR-0029's claim-type classification and the `flagged` state in the schema and checker, so a conflict is mechanically detectable rather than review-only | Issue #1410, unlanded at this writing |
| The general evidence contract and how FACT/INFERENCE/TEAM_KNOWLEDGE are chosen | Issue #1314 |
| Whether a status transition should ever be restricted (for example, one-way retirement) | Not decided anywhere in this repository today |
| Per-type templates for node bodies | Somewhere in #1307-#1351, per `AGENTS.md`'s own gap table |

**Relationships.** This node's front matter carries two `references` edges: to
`corpus-agents`, because the `retired` value's full procedure lives there and this
document leans on it rather than restating it; and to `corpus-standard-confidence`,
because `flagged` and low confidence are the exact pair of easily-conflated ideas
MUST 2 above exists to keep apart, and `corpus-standard-confidence` already
makes the confidence side of that distinction. Both targets were confirmed present as
loaded nodes before this front matter was finalized:
`git fetch origin launchpad && git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` was run against the branch this PR merges into, not this
node's own worktree, and listed `corpus-agents` (id `corpus-agents`) and
`corpus-standard-confidence` (id `corpus-standard-confidence`) among four loaded
nodes. No edge targets a sibling from this same five-document batch
(`generated-content`, `identifiers`, `naming`, `normative-language`) -- none of those
PRs will have landed by the time this one does, regardless of what any single
worktree shows. `corpus-standard-decision-references` is also confirmed present, but
this node's references to it above stay expository prose rather than a typed edge:
nothing here depends on it being true or supersedes it, and a bare `references` edge
would say less than the prose already does.

**Expected but not verified when this node was written**, per the rule in "Creating a
node" step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No node anywhere in this corpus has ever carried `deprecated`, `retired` or
  `flagged`.** Every claim above about how those values behave is drawn from the
  schema, `AGENTS.md` and `ADR-0029`, never from a worked instance in this corpus. The
  first real deprecation, retirement or conflict will test it.
- **Whether a generated view (an index, a knowledge-crate projection) treats these
  five values differently -- for example, excluding `retired` or `deprecated` nodes
  from a default listing -- was not checked.** No generator exists yet for this
  corpus, so the question has no current answer to verify against.
- **Whether reversing a status (for example, `retired` back to `active`) on the same
  file is intended to be possible was not settled by asking anyone** -- it is stated
  above as an enforcement gap because nothing in `node.schema.json` or `validate.py`
  restricts it, not because any document says it is expected to happen.
