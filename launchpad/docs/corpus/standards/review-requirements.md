---
id: corpus-standard-review-requirements
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
  - statement: "The launchpad branch is protected: a pull request there requires at least two approving reviews from reviewers with write access, and an author cannot approve their own pull request."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "Agents may draft any issue, pull request or ADR in full, but may not decide an ADR outcome, approve a pull request, or close another agent's escalation; they raise concerns and never clear them."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "This repository's CODEOWNERS file assigns the entire repository to one team through a single wildcard rule; it contains no entry scoping launchpad/docs/corpus to a distinct set of reviewers."
    entry_class: FACT
    evidence:
      - ".github/CODEOWNERS"
  - statement: "The launchpad-corpus-validate workflow runs validate.py, and its unit tests, on every pull request whose changed paths intersect launchpad/docs/corpus/**, and again on every push of such a change to the launchpad branch."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "validate.py's citation checker resolves a repository-relative citation to a real file, or checks a GitHub link's pin and syntax; in neither case does it open or read the cited source's content, and it never compares two evidence entries against each other."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py never inspects a node's status field anywhere in its validation logic; the only mechanical constraint on status is node.schema.json's five-member enum, so a flagged node is loaded, cited and reported on no differently than a node of any other status."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "validate.py's relationship check confirms only that a relationships[].target string matches some loaded node's id; it never checks a relationship's declared type against relationships.schema.json's relationshipMeta directionality, so a schema-valid type pointed at a real node id passes whether or not that direction is true."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "relationships.schema.json documents each relationship type's directionality and generated inverse in a relationshipMeta block, and states of that block, in its own top-level description, that it is not itself a validation rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "node.schema.json's status enum names flagged as ADR-0029's unestablished/flagged state, naming an unresolved conflict specifically rather than ordinary low confidence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "ADR-0029 requires that when two sources with authority over the same claim type contradict, the corpus author stops and records the contradiction rather than picking a side, and the affected node stays unestablished/flagged until a human resolves it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "decision-references.md fixes the author's behaviour when two accepted decisions conflict: write one evidence entry per contradicting record, state the contradiction in the body, set the node's status to flagged, and escalate through a type:adr issue parented to the PRD that raised it, with the decision outcome left blank."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "confidence.md's Requirement 5 states that an entry must not be an INFERENCE if its citation supports the subject of the claim but not the specific choice the claim makes, and that such an entry must be reclassified to TEAM_KNOWLEDGE naming who decided."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/confidence.md"
  - statement: "AGENTS.md's 'Three things a passing run does not mean' section states that checking is structural, that a FACT citing a real file which says nothing on the subject still passes cleanly, and that only a human reading the source establishes a FACT."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's node-creation step 9 requires a relationships[].target to be checked against the branch a pull request will actually be merged into, not the author's own worktree, because the checker loads whatever nodes are present where it runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md states that nothing enforces a limit on repeated commit-only FACT entries -- the checker treats every commit citation identically and a second, third or tenth such entry produces only non-fatal UNVERIFIED notices -- so more than one commit-only FACT in a ledger is a convention a reviewer has to hold, not a rule the tooling holds."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "ADR-0028's Decision and Consequences state that the corpus is a committed artefact reviewed at the pull request that changes it, not audited after the fact, and that staying reviewable as a human-read pull-request diff is the enforcement mechanism that rule depends on."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The corpus's human-facing entry point states that the corpus is audited in the pull-request diff a human reads, not after the fact, and that a green validation run is the floor, not the verdict."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
  - statement: "AGENTS.md's node-creation step 1 requires confirming a node is one idea before writing it: describing two contracts, or a concept and the procedure that uses it, is two nodes, and the second is filed as its own task rather than folded in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "No corpus document -- AGENTS.md, README.md, schema/README.md, node.schema.json, ADR-0028, ADR-0029, CONTRACT.md, CODEOWNERS or the corpus-validate workflow -- establishes a review or validation requirement specific to a node's status transitioning from draft to active, beyond the checks this document already states for any corpus change."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/schema/README.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/project-intelligence/CONTRACT.md"
      - ".github/CODEOWNERS"
      - ".github/workflows/launchpad-corpus-validate.yml"
    confidence: 0.7
  - statement: "Issue #1323, 'document corpus standard for status', is open and unlanded at the recorded revision, and is the task filed to own the status lifecycle -- including any draft-to-active promotion requirement this document does not find established today."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1323"
  - statement: "Issue #1322's definition of done requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, to define enforcement and an exception/escalation process, and to link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1322 definition of done"
relationships:
  - type: references
    target: corpus-agents
  - type: references
    target: corpus-readme
  - type: references
    target: corpus-standard-confidence
  - type: references
    target: corpus-standard-decision-references
---

# Standard: review requirements for a corpus node

What a reviewer of a pull request touching `launchpad/docs/corpus/**` must additionally
verify, beyond ordinary pull-request review, and why: the deterministic check
(`validate.py`) is structural, and everything it does not establish is establishable
only by a human reading the diff.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| The general pull-request process -- approvals, DCO, agents draft but never approve | `launchpad/AGENTS.md` §5-§6 |
| Creating, updating and retiring a node; what `validate.py` does and does not establish | `launchpad/docs/corpus/AGENTS.md` |
| Review duties specific to a `confidence` value | `launchpad/docs/corpus/standards/confidence.md` |
| Review duties specific to a decision citation, and clearing a `flagged` contradiction | `launchpad/docs/corpus/standards/decision-references.md` |
| The deterministic check itself | `launchpad/project-intelligence/corpus/validate.py` |
| Why review is the corpus's enforcement mechanism | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| Evidence precedence and the `flagged` state | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |

Where this document and any of those disagree, **they win** -- this one has drifted and
should be fixed.

**This document restates none of the field-level MUST lists `confidence.md` and
`decision-references.md` already carry.** It names when they apply and defers to them.
What it adds is the general, node-wide layer no single field-standard owns: claim-to-ledger
correspondence, relationship-type correctness, and what a `flagged` status specifically
asks of a reviewer.

## Scope and authority

**This node covers** what a reviewer checks on a corpus-touching pull request that
`validate.py` does not and cannot check, how the corpus's existing `flagged`-escalation and
evidence-classification rules bear on that review, and what today's review requirement
genuinely is -- not an invented approval process, but the one this repository's own
decisions and documents already assign to review.

**It does not cover** the mechanics of pull-request review itself -- review count, DCO,
who may approve -- which `launchpad/AGENTS.md` §5-§6 already owns, or the field-specific
checklists `confidence.md` and `decision-references.md` already carry for their own
fields.

**Its authority is derived, not original.** `ADR-0028` is explicit that the corpus is
"reviewed at the pull request that changes it, not audited after the fact," and that
staying reviewable as a human-read diff "is the enforcement mechanism" the rest of that
decision depends on. `launchpad/docs/corpus/README.md` restates the same point at the
corpus's own front door: "the corpus is audited in the pull-request diff a human reads...
a green check is the floor, not the verdict." This document does not create that
authority. It collects what `AGENTS.md`'s *Three things a passing run does not mean*,
`confidence.md`'s *Enforcement, and where it stops*, `decision-references.md`'s reviewer
checklist and `ADR-0029`'s escalation rule already assign to a human reviewer, states the
parts none of them individually owns, and puts all of it in the one place a reviewer needs
before approving a corpus change.

## Is there a corpus-specific approval gate beyond ordinary pull-request review?

**No, and this document does not invent one.** Checked directly, at the recorded revision:

- `.github/CODEOWNERS` routes the whole repository through one wildcard rule. Nothing
  scopes `launchpad/docs/corpus/**` to a distinct reviewer or team.
- The corpus-validate workflow runs `validate.py` as a CI job on every pull request
  touching the corpus root. That is a mechanical status check, not a review gate, and it
  is the same structural check this document repeatedly says is not enough on its own.
- No document found -- `AGENTS.md`, `README.md`, `schema/README.md`, `node.schema.json`,
  `ADR-0028`, `ADR-0029`, `CONTRACT.md` -- describes a second approval step, a required
  corpus reviewer role, or a distinct sign-off beyond `launchpad/AGENTS.md` §6's ordinary
  two-approval rule.

So "review requirements for a corpus node" is not a second gate stacked on top of ordinary
review. It is `launchpad/AGENTS.md` §5-§6's ordinary process, **plus a content-verification
duty ordinary code review does not carry**, because nothing else in the pipeline performs
one. That duty is this document's actual subject.

## MUST

These are review-enforced. No check in `validate.py` reaches any of them; see
*Enforcement, and where it stops*.

1. **A reviewer MUST open every citation attached to a `FACT` entry and confirm the source
   actually supports the statement it sits under** -- not merely that the citation resolves
   to a real file. `validate.py`'s citation checker never reads a cited file's content, so a
   `FACT` citing a real, unrelated file passes exactly as cleanly as a correct one.
2. **For every `INFERENCE` entry, a reviewer MUST apply `confidence.md`'s *Reasoning versus
   deciding* test** -- would a competent reader, given only the cited sources, reach this
   statement? -- and confirm `confidence` is present and in range. The mechanical half is
   already enforced by the schema; the judgement half is not, and `confidence.md` owns the
   test. This document does not restate it.
3. **For every `TEAM_KNOWLEDGE` entry, a reviewer MUST confirm `provided_by` names a real,
   checkable source**, and that the entry is not an author's own unstated decision
   attributed to something that merely concerns the same subject. `confidence.md`'s own
   ledger records exactly this mistake being caught in an earlier draft of `AGENTS.md`.
4. **A reviewer MUST confirm every substantive claim in the body has a corresponding
   `evidence` entry, and every `evidence` entry supports a claim actually made in the
   body.** Nothing mechanical pairs the two; `AGENTS.md`'s node-creation procedure assumes
   they are written together, but nothing checks afterward that they stayed that way.
5. **A reviewer MUST re-resolve every `relationships[].target` against the branch the pull
   request will actually merge into**, not the author's worktree -- `AGENTS.md` step 9's
   own rule, restated here because it is a review action, not only an authoring one. A
   target that resolves locally can be a hard error on `launchpad`.
6. **A reviewer MUST confirm a relationship's declared `type` matches its real-world
   direction**, using `relationships.schema.json`'s `relationshipMeta` block. The schema
   enforces only that `type` is one of five enum members and that `target` names a real
   node id; it does not, and by its own description cannot, confirm that a `supersedes` or
   `depends-on` edge is actually true in that direction. A node declaring `type: supersedes`
   at a target it does not, in fact, replace passes validation cleanly.
7. **Where a node cites an accepted decision for an intent claim, a reviewer MUST apply
   `decision-references.md`'s MUST list in full** -- open the record, read its `status`,
   confirm the cited section supports the claim, and confirm no two cited decisions
   contradict. This document does not restate that list; it names when it applies.
8. **Where a node's status is, or is being changed to, `flagged`, a reviewer MUST confirm:**
   each contradicting record is cited as its own evidence entry; the body states the
   contradiction and names both records; and a `type:adr` issue exists, or is filed in the
   same pull request, escalating the resolution to a human, per `ADR-0029` and
   `decision-references.md`'s *When two accepted decisions conflict*. **A reviewer MUST NOT
   approve a pull request that clears a `flagged` status by picking a side without a linked,
   decided ADR settling it.** Agents draft decisions; they do not make them
   (`launchpad/AGENTS.md` §5.1) -- and a reviewer letting a `flagged` node resolve to one
   side without that decision record is the same act by a different name.
9. **A reviewer MUST confirm the node represents one independently maintainable idea.** If
   the diff describes two contracts, or a concept and the procedure that uses it, that is
   two nodes, and the second belongs in its own task (`AGENTS.md` step 1).

## SHOULD

- **Spot-check GitHub link citations by opening them.** The checker verifies only that a
  link is pinned to a full commit SHA and names a file segment -- never that the named file
  exists at that commit. A pinned link to a file that has never existed passes as cleanly
  as a correct one.
- **Treat more than one commit-only `FACT` in a single ledger as a signal to look closer.**
  `AGENTS.md` names this explicitly: the checker produces the same non-fatal notice for the
  first such entry as for the tenth, so nothing but a reviewer will ever raise it.
- **When reviewing an update rather than a new node, check whether the recorded revision
  should move**, using `AGENTS.md`'s *Updating a node* branches. That section is stated
  there as working practice pending #1321, not settled corpus-wide policy -- read it with
  that caveat rather than as a closed rule.
- **Prefer asking the author to open a source over approving an unread citation.** A
  reviewer who cannot check a `FACT` in reasonable time should ask for it to be reclassified
  or verified, not wave it through on the strength of the schema passing.

## Status transitions: `draft` to `active`, and clearing `flagged`

These sit differently, and this document treats them differently rather than inventing one
rule for both.

**`draft` to `active` is a genuine gap, and this document does not fill it.** No corpus
document defines a review or validation requirement specific to that transition.
`validate.py` does not even read a node's `status` field in its logic -- the only
mechanical constraint on it is schema membership in the five-value enum, checked
identically regardless of what the value was before. Issue #1323, "document corpus standard
for status," is open and unlanded at the recorded revision and is the task that owns this.
Until it lands, promoting a node to `active` gets exactly the review this document already
requires for any corpus edit -- MUSTs 1-7 and 9 above -- and nothing beyond that.

**Clearing `flagged` is not a gap.** `ADR-0029` and `decision-references.md`'s *When two
accepted decisions conflict* already establish the mechanics in full: record both sources,
state the contradiction, escalate via a `type:adr` issue, and leave the outcome to a human.
This document's contribution is MUST 8 above -- naming that a reviewer holds the line on it,
since nothing mechanical does.

## Enforcement, and where it stops

**Enforced mechanically**, by `validate.py` in CI on every pull request touching the
corpus root: schema conformance, citation shape and resolution, relationship *target*
existence, duplicate ids, non-canonical files, and the generated-content boundary. A node
violating any of these does not merge.

**Enforced by review only**, and by nothing else: every MUST above. There is no
corpus-specific approval gate distinct from `launchpad/AGENTS.md` §6's ordinary two-review
requirement -- see *Is there a corpus-specific approval gate beyond ordinary pull-request
review?* -- so that ordinary review is the only mechanism available to hold these MUSTs,
and this document is what that review has to include when the diff touches the corpus.

| What passes mechanically | What it does not mean |
|---|---|
| A `FACT` citation resolves to a real file | The file supports the statement (MUST 1) |
| An `INFERENCE` carries an in-range `confidence` | The entry is reasoning rather than a disguised decision (MUST 2) |
| A `relationships[].target` matches a known node id | The declared `type`'s direction is true (MUST 6) |
| `status: flagged` validates like any other status | The contradiction was actually recorded and escalated (MUST 8) |
| The pull request carries two approvals | Either reviewer opened even one cited source |

## Exceptions and escalation

**There is no exception process for the structural checks.** They are enforced before
merge and cannot be waived by agreement; changing them is a schema change under
`launchpad/docs/corpus/schema/COMPATIBILITY.md`, not an exception to this document.

**For the review-enforced MUSTs**, the routine exception is the one *Status transitions*
already names: a `draft`-to-`active` promotion carries no requirement beyond the MUSTs
already listed, because none is established today. Anything else these MUSTs do not
cover is an open question, not a judgement call for a reviewer to make silently. This
repository has one route for that: a `type:adr` issue parented to the governing PRD,
argued in the issue, decided by a human. Do not resolve it in a review comment and do not
widen this standard by precedent.

## Scope and omissions

**This document covers** what a reviewer of a corpus-touching pull request must verify
beyond the mechanical check, when the field-specific standards apply, what today's actual
approval gate is, how `flagged` clearing and `draft`-to-`active` promotion differ as review
questions, and what enforcement does and does not reach.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Ordinary pull-request review mechanics -- approval count, DCO, agents draft-not-approve | `launchpad/AGENTS.md` §5-§6 |
| Review duties specific to a `confidence` value | `launchpad/docs/corpus/standards/confidence.md` |
| Review duties specific to a decision citation | `launchpad/docs/corpus/standards/decision-references.md` |
| The status lifecycle, including any `draft`-to-`active` requirement | #1323, unlanded |
| The general evidence contract and how classes are chosen | #1314, unlanded |
| How a generated artifact proves its provenance for review purposes | #1316, unlanded |
| Line numbers in citations not being verified against file length | #1459 |

**This node declares four `relationships`, all `references`, all checked against
`origin/launchpad` rather than this branch:** `corpus-agents` (the node-creation procedure
this document's review duties sit on top of), `corpus-readme` (the "review is the
enforcement mechanism" framing this document's authority rests on), `corpus-standard-confidence`
and `corpus-standard-decision-references` (the field-level checklists MUSTs 2, 3 and 7
defer to rather than restate). Each edge corresponds to a specific citation above, not a
general sense of relatedness. None targets a sibling standard from this same batch
(`linking`, `provenance`, `taxonomy`, `test-references`) -- those are unmerged at the
recorded revision, and a `relationships[].target` naming an id no loaded node carries is a
hard validation error.

**Expected but not verified when this node was written**, per the rule in *Creating a
node* step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No node anywhere in the corpus carries the `flagged` status.** MUST 8's checklist is
  written from `ADR-0029` and `decision-references.md`'s own procedure, never from a worked
  instance of a reviewer actually clearing one. `decision-references.md` makes the identical
  admission about authoring a flagged node; this document makes it about reviewing one.
- **Whether the two required pull-request approvals are enforced by a GitHub ruleset as a
  required status check, or held only by convention, was not established.**
  `launchpad/AGENTS.md` itself states the ruleset enforcing branch protection on `launchpad`
  is not readable without `admin:org`, and this document did not attempt to re-verify that.
- **Whether an agent reviewer may currently satisfy one of the two required approvals, or
  whether that is blocked at the platform level rather than by convention alone, was not
  verified.** `launchpad/AGENTS.md` §5.1 states agents may not approve; whether GitHub's
  branch protection enforces that mechanically or leaves it to reviewers to honour was not
  checked here.
- **No author or reviewer has applied this document's MUST list in practice.** Whether the
  checklist is followable at review time, rather than merely correct on paper, is untested.
