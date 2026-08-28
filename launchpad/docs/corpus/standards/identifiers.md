---
id: corpus-standard-identifiers
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
  - statement: "id is a required top-level field on every corpus node, must be a string matching ^[a-z0-9]+(-[a-z0-9]+)*$, and the schema's own description of the field states it is stable, kebab-case, and never renamed once assigned, citing ADR-0028's canonical-representation requirement that generated projections derive reproducibly from one source."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "That pattern admits only lowercase ASCII letters, digits, and hyphens; it rejects an empty string, a leading or trailing hyphen, and two consecutive hyphens, because every hyphen in the pattern sits between two non-empty runs of [a-z0-9]."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A non-kebab-case id (uppercase letters and spaces) fails schema validation specifically on the pattern keyword at the id path, confirmed by a dedicated fixture and a test asserting that exact validator and path."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/fixtures/invalid/malformed-id.md"
      - "launchpad/docs/corpus/schema/tests/test_schema.py"
  - statement: "id is one of exactly seven property names node.schema.json permits at the top level, and additionalProperties is false, so no second identifier-shaped field can be added beside it without a schema change."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A duplicate id used by more than one loaded node is a hard validation error naming every colliding path, detection is scoped to the corpus root the validator is given minus the schema/ subtree it excludes by name, and a dedicated test asserts the error is raised and names the fixture's id."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/project-intelligence/corpus/tests/test_validate.py"
  - statement: "Duplicate-id detection and relationship-target resolution both key exclusively on ids that are Python str; a non-string id (for example a YAML list or mapping written where a scalar id was expected) is skipped by both checks rather than raising, and is instead reported through its own schema violation, with dedicated tests for both the list and dict cases."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/project-intelligence/corpus/tests/test_validate.py"
  - statement: "A relationships[].target that does not match any loaded node's id is a hard validation error naming the citing node and the unresolved target string, confirmed by a dedicated fixture and test."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/project-intelligence/corpus/tests/test_validate.py"
  - statement: "validate.py defines its own copy of the same kebab-case pattern, independently of node.schema.json, to decide whether a node's id is safe to print in an error label; when the id does not match, the label falls back to the node's file path instead. Two tests cover this: one that an unsafe id from a schema-invalid node is never echoed and the path is used instead, and one that a schema-shaped id, None, and a non-string id are each labelled correctly by the same helper."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/project-intelligence/corpus/tests/test_validate.py"
  - statement: "At the recorded revision, node.schema.json's id pattern and validate.py's independent label-safety pattern are character-for-character identical strings, and no test in either test suite asserts they stay that way."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Neither validate.py nor test_schema.py contains any logic or test tying a node's id to its file path, filename, or directory location; id and path vary independently by design, illustrated by the schema's own valid fixtures, whose ids (corpus-schema-full-example, corpus-schema-overview) do not derive mechanically from their filenames (node-full.md, node-minimal.md)."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/tests/test_schema.py"
      - "launchpad/docs/corpus/schema/fixtures/valid/node-full.md"
      - "launchpad/docs/corpus/schema/fixtures/valid/node-minimal.md"
  - statement: "ADR-0028 requires every generated projection of the corpus -- indexes, dependency graphs, knowledge-crate serializations -- to stay reproducible from the canonical Markdown, and calls a generator that free-hands content instead of deriving it from the corpus a silent second authored corpus; this is the consequence node.schema.json's id description cites when it says a renamed id breaks that reproducibility."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "AGENTS.md instructs an author, as explicit steps, to choose an id that describes the idea rather than where the file currently sits, to treat it as permanent from the moment of creation, to leave it alone during every later update, and -- when retiring a node -- to never reuse or rename its id, because reuse would silently point old references at new content and renaming would break every generated view that resolves through it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Retiring a node is a status change: the file and its id both stay, so the checker keeps loading the node and inbound relationships keep resolving. Deleting a node instead is what breaks every relationship targeting it, because a relationships[].target naming an id nothing carries is the same hard error covered above for any unresolved target."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A relationships[].target is resolved against whatever set of nodes one validator run actually loads under its --root, with no reference to any other branch or the merge target; AGENTS.md records a concrete case where a target resolved on an author's own worktree, branched from an unmerged ancestor node, and would have failed once the same change landed on launchpad without that ancestor."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "relationships.schema.json defines no mechanism, and validate.py contains no logic, requiring or generating the inverse side of an authored relationship type such as references; declaring only the forward edge from one node is schema-valid and passes validation on its own."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Checked by running `git fetch origin launchpad` and `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` on 2026-08-27 immediately before finalizing this node's front matter: the merge target carries exactly four loaded nodes outside schema/, with ids corpus-agents (AGENTS.md), corpus-readme (README.md), corpus-standard-confidence (standards/confidence.md), and corpus-standard-decision-references (standards/decision-references.md); none of the other four documents in this same five-way batch (generated-content, naming, normative-language, status) are present."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus', run 2026-08-27) -> AGENTS.md(id=corpus-agents), README.md(id=corpus-readme), schema/** (excluded), standards/confidence.md(id=corpus-standard-confidence), standards/decision-references.md(id=corpus-standard-decision-references)"
  - statement: "Every id merged into the corpus at the recorded revision begins with the literal prefix corpus-, and every id for a node under standards/ continues with the singular standard- even though the directory itself is named standards (plural); the schema's pattern does not require any prefix or word, so this is an observed authoring convention, not a mechanically enforced one."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.6
  - statement: "Issue #1489 exists specifically to backfill authored relationships across the corpus standards nodes once the #605 batch has merged, and records that every standards node in this batch was branched from task/636-corpus-agents-md rather than from launchpad, so at the time each was authored the merge target loaded zero corpus nodes and any relationships[].target would have failed post-merge; both already-merged sibling standards (confidence.md, decision-references.md) accordingly declared no relationships even though their own text notes an edge to corpus-agents would have resolved on their working branch, deferring the whole edge set to that backfill pass rather than adding it piecemeal."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1489"
  - statement: "Issue #1489's own premise -- that the merge target loads zero corpus nodes -- no longer held at the time this node was checked: the FACT entry above, run fresh against origin/launchpad rather than taken from #1489's text, shows four nodes already merged, including corpus-agents. Declaring a references edge to corpus-agents from this node is therefore schema-valid today, not merely valid on this node's own working branch."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus', run 2026-08-27) -> AGENTS.md(id=corpus-agents), README.md(id=corpus-readme), schema/** (excluded), standards/confidence.md(id=corpus-standard-confidence), standards/decision-references.md(id=corpus-standard-decision-references)"
  - statement: "Issue #1317 requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1317 definition of done"
relationships:
  - type: references
    target: corpus-agents
---

# Standard: `id`

What the `id` field on a corpus node's front matter means, the shape it must take, why
it is permanent, and what a relationship's `target` inherits from all of that. This is
a policy node about one field. Look up the section you need.

## Scope and authority

**This standard governs** the `id` key required on every corpus node's front matter,
and by extension the `target` key on a `relationships` entry, which is the same kind
of string used to point at one.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces the field's presence, type, and pattern; `validate.py`
enforces uniqueness across the corpus and resolves every relationship target against
it; CI runs `validate.py` on every change under the corpus root. This document does not
create those rules and cannot relax them. What it adds is the half no schema can hold —
how to choose an id, why it must never move once assigned, and what a reviewer has to
check that no green run does.

| For | Read |
|---|---|
| The field's machine contract — type, pattern, required/optional | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of the front-matter fields | `launchpad/docs/corpus/schema/README.md` |
| The relationship-type enum and each type's directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Why Markdown with front matter is canonical, and why generated projections must derive reproducibly from it | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| Creating, updating and retiring a node — including the id-permanence steps this document expands on | `launchpad/docs/corpus/AGENTS.md` |
| Checking a relationship target against the branch a PR will actually merge into | `launchpad/docs/corpus/AGENTS.md`, step 9 of *Creating a node* |

Those files are authoritative. Where this document and any of them disagree, **they
win** — this one has drifted and should be fixed.

**This document restates the schema only where its own subject forces it to.** A
standard about `id` cannot omit the pattern `id` must match, so MUST 1 and 2 state it.
What is *not* restated: the other six top-level field names, their own rules, and the
relationship-type enum's members beyond the one row (`target`) that shares `id`'s
shape. If the schema's rules on `id` or `target` change, MUST 1 and 2 below are the
places in this document that must change with them, and there is nowhere else.

## What the field is for

An `id` names one corpus node, permanently. Two things depend on that permanence
holding:

- **Every `relationships[].target` in the corpus is a bare id.** A relationship
  resolves by string match against loaded nodes' `id` values and nothing else — no
  path, no title, no fuzzy match. If an id moves, every edge naming it breaks or,
  worse, silently starts naming nothing a reviewer notices.
- **Every generated projection of the corpus — index, dependency graph, knowledge-crate
  serialization — is required to derive reproducibly from the canonical Markdown.**
  ADR-0028 is explicit that a generator which free-hands content instead of deriving it
  is a silent second authored corpus, which the whole one-canonical-representation
  decision exists to forbid. A projection keyed on id can only stay reproducible if the
  key does not move under it.

`id` is not a title, a slug for a URL, or a filename. It exists so that one string can
be depended on by everything downstream of a node — a relationship, a generated view,
a future citation — without also depending on where the file lives or what it is
called today.

## MUST

These are enforced mechanically unless a bullet says otherwise.

1. **`id` MUST be present on every node** and **MUST be a string**. `node.schema.json`
   lists it among the required fields; a node missing it fails schema validation.
2. **`id` MUST match `^[a-z0-9]+(-[a-z0-9]+)*$`** — lowercase ASCII letters, digits, and
   single hyphens between non-empty runs of them. No uppercase, no underscores, no
   spaces, no leading, trailing, or doubled hyphen. A malformed id fails on the
   schema's `pattern` keyword specifically, not on some other rule, and a dedicated
   fixture and test confirm that exact failure shape.
3. **`id` MUST be unique across every node the validator loads** (the corpus root
   given to it, minus the `schema/` subtree it excludes by name). A collision is a
   hard error naming every path that shares the id. This governs only what the
   validator actually scans — a collision with something outside the corpus root
   (an ADR slug, a filename in another system entirely) is not checked by anything
   named here.
4. **Every `relationships[].target` MUST name an id that resolves against the
   branch the change will actually merge into** — for this repository, `launchpad`.
   Resolving on an author's own worktree is not sufficient: `validate.py` resolves a
   target against whatever nodes one run loads, with no notion of a merge base, so a
   target that only exists because the author branched from an unmerged ancestor
   node can validate cleanly on the working branch and still fail once the change
   lands without that ancestor. Check `git ls-tree -r --name-only origin/launchpad --
   launchpad/docs/corpus` yourself, immediately before finalizing front matter, not
   from memory or from what an earlier document in the same batch reports — the set
   changes as siblings merge. This document's own ledger records exactly that check,
   at the revision it was run.
5. **Once a node has merged, its `id` MUST NOT be renamed.** Nothing mechanical
   enforces this — see *Enforcement, and where it stops* — but it is not optional. A
   renamed id silently breaks reproducibility for every generated view keyed on it,
   and any inbound relationship whose `target` still names the old value becomes an
   unresolved-target error on whatever node cites it, discoverable only if such a
   citing node exists.
6. **A retired node's `id` MUST NOT be reused for a different node**, and retiring a
   node MUST be a status change, never a deletion. Deleting the file is what breaks
   inbound relationships — a `relationships[].target` naming an id nothing carries is
   the same hard error MUST 4 describes for any other unresolved target. Reusing a
   spent id would let a new node silently inherit whatever still points at the old
   one.

## SHOULD

These are enforced by review. A reviewer who lets one through has approved a defect
even though the check stayed green.

- **Choose the id to name the idea, not the file's current location.** Directories
  reorganize; the corpus's own top-level nodes have already moved once (from a flat
  layout into `standards/`) without their ids changing, which is the point of MUST 1
  in `launchpad/docs/corpus/AGENTS.md`'s *Creating a node* section restated here for
  this field specifically.
- **Follow the corpus's own convention where one is observable, and say when you
  are inferring it rather than reading a rule.** Every id merged at the time this
  document was written begins with the literal prefix `corpus-`, and every node
  under `standards/` continues with the singular `standard-`, not the directory's
  plural. Nothing in the schema requires this — it is a pattern across four
  examples, not a written rule, and this document rates that reasoning as a
  medium-confidence inference rather than dressing it up as a stated policy. Follow
  it anyway unless you have a specific reason not to: consistency here is what lets
  a reader guess a sibling node's id well enough to check it, and a break in the
  pattern with no stated reason reads as an accident.
- **Assign the id once, at creation, before you have finished writing the body.**
  Fixing it early removes the temptation to reshape it as the draft's scope settles
  — the id should describe where the node lands, not track every revision of what
  it was going to be about.
- **When retiring a node that something else replaces, express that with a
  `supersedes` relationship from the new node to the retired id**, rather than
  reusing the id or leaving the connection to prose alone. `relationships.schema.json`
  defines the type for exactly this.
- **Cite an id, never a path, when the thing you mean is the node** — in a
  `relationships[].target`, and in prose that tells a reader which node to open next.
  A path describes where a file currently is; an id describes what it permanently is,
  and MUST 5 is why the second is the more durable thing to point at.

## Enforcement, and where it stops

**Enforced mechanically**, by `node.schema.json` through `validate.py`, in CI on every
change under the corpus root: presence, string type, the kebab-case pattern (MUSTs 1
and 2), corpus-wide uniqueness among loaded nodes (MUST 3), and that every
`relationships[].target` resolves against the set of nodes the run actually loaded
(part of MUST 4 — the *what is loaded* half). A node violating any of these does not
merge.

**Enforced twice, independently, for different reasons.** `node.schema.json`'s
`pattern` keyword is what makes a malformed id fail validation at all.
`validate.py` separately carries its own copy of the same character class, used only
to decide whether an id is safe to print inside an error message or whether the
message must fall back to the file's path instead. At the recorded revision the two
patterns are identical strings, but nothing asserts they stay that way — unlike the
relationship-type enum, which a dedicated test pins against drifting between
`node.schema.json` and `relationships.schema.json`, no test here compares the two
copies of the id pattern. A drift between them would not make an id validate
differently; it would only change whether a malformed id shows up in an error message
or gets silently replaced by a path.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| That an id, once merged, is never renamed (MUST 5) | Nothing on disk prevents editing an existing node's `id` in a later change. A rename is caught only indirectly: if some other loaded node's `relationships[].target` still names the old value, that becomes an unresolved-target error on the *citing* node, not on the one that was renamed. If nothing yet cites the node, the rename passes with no signal at all. |
| That the merge-target check in MUST 4 was actually run, and run recently | `validate.py` has no concept of a merge target — it resolves against whatever tree it is pointed at. The check is a step a human or an agent performs before merging, not something the tool performs for them. |
| That an id follows the observed `corpus-`/`corpus-standard-` convention | The schema's pattern accepts any kebab-case string. A conforming but conventionless id (`abc123`, `x-y-z`) validates identically to one that follows the convention. |
| That an id actually names the idea rather than a snapshot of the file's path at creation time | Nothing checks the *content* of the string against the node's subject — only its shape. |
| That a retired id is never reused (MUST 6) | Uniqueness (MUST 3) only compares ids among nodes the validator currently loads. A retired node's file stays on disk carrying its id, so reusing that exact id on a second file is still caught as a duplicate — but nothing stops choosing a *different* id for the replacement and treating the old one as free, because nothing records that an id was ever "retired" as opposed to simply assigned once and left alone. |
| That the inverse side of an authored relationship type (`references` → `referenced-by`) gets declared on the target node | `relationships.schema.json` documents that `references`' inverse is `authored`, meaning a human writes both directions, but `validate.py` contains no logic requiring, checking, or generating it. A forward-only edge, like the one this node declares to `corpus-agents`, is schema-valid on its own. |

The pattern across that table is the same one the sibling standards for `confidence`
and decision references name for their own fields: everything a schema can hold on
shape is held; everything that depends on *when* it was checked, or on intent, is not.

## Exceptions and escalation

**There is no exception process for MUSTs 1 through 4.** They are enforced before
merge and cannot be waived by agreement. Changing the pattern, the required-field
list, or how uniqueness or relationship resolution work means changing
`node.schema.json` or `validate.py` under
`launchpad/docs/corpus/schema/COMPATIBILITY.md`'s breaking-change rule — a schema or
tooling change, not an exception granted to one node.

**MUST 5 has no defined migration path.** This document does not invent one. If a
genuine need to rename a merged id ever arises — because it was chosen before its
subject was fully understood, for instance — that is an open question this repository
has one route for: a `type:adr` issue parented to the PRD that raised it, decided by a
human, and written up before anything renames. Treating a rename as an ordinary edit
because no check stops it would be exactly the failure MUST 5 exists to prevent.

**When MUST 4's check finds nothing to link to**, that is a legitimate answer, not a
default. Say which command was run, when, and what it returned — this document's own
ledger records exactly that for the edge it does and does not declare. A stale
justification copied from an earlier sibling ages out the moment another sibling
merges; re-run the check rather than trusting what an earlier node's prose says the
merge target looked like when it was written.

**When two nodes are found to share an id**, that is covered by MUST 3 and fails the
run outright; there is nothing to escalate beyond fixing it before merge.

## Scope and omissions

**This document covers** the `id` field's format, permanence, and uniqueness
contract; how a `relationships[].target` inherits the same shape and resolution
rules; what is mechanically enforced about all of that and what is not; and how to
choose and change an id in practice.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Human-readable naming — node titles, headings, and the words chosen for a subject beyond the bare id string | #1319 |
| The other six top-level front-matter fields, and the field-combination rules between them | `launchpad/docs/corpus/schema/node.schema.json`; the `confidence` and evidence-class rules specifically are `corpus-standard-confidence` and #1314 |
| Whether a node's recorded provenance revision may stay put across an edit that does not touch its id | #1321 |
| How generated artifacts (indexes, graphs, crate serializations) prove they derive from a node's id rather than free-handing one | #1316 |
| The relationship-type enum's other four members, and when to reach for which one | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Corpus-wide review process and checklist, beyond the id-specific checks this document names | #1322 |

**This node declares one relationship: a `references` edge to `corpus-agents`.**
Checked immediately before finalizing front matter (`git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus`, 2026-08-27): the merge target carries
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`, and
`corpus-standard-decision-references`, none of the other four documents in this
batch. `corpus-agents` is the node this standard most directly extends — the
create/update/retire id rules MUST 1 through 6 restate and generalize all come from
it — so citing it as supporting context is a real dependency, not decoration.
`corpus-readme` only redirects to `corpus-agents` and adds nothing this document
depends on; the two sibling standards (`corpus-standard-confidence`,
`corpus-standard-decision-references`) are peers on unrelated fields, not sources
this one draws on. Issue #1489 tracks a broader backfill of authored relationships
across this whole batch once every sibling has merged — its own text was written when
the merge target loaded zero corpus nodes and recommended deferring every edge for
that reason; that premise had already stopped holding by the time this node was
checked, which is exactly why the check was run fresh here rather than trusted from
that issue's prose. Declaring this one edge now does not conflict with #1489 — it
reduces what that backfill pass has left to do for this node, and #1489 remains the
right place for edges to the other standards once they exist to name.

**Expected but not verified when this node was written:**

- **No node's id has ever actually been renamed or a retired id reused in this
  corpus.** Every claim in *Enforcement, and where it stops* about what a rename or
  reuse would look like is reasoned from reading `validate.py`, not observed against
  a real incident.
- **Whether any generated projection (index, graph, crate serialization) exists yet
  that consumes `id` as a key.** None was found to inspect; whether the
  reproducibility property ADR-0028 requires has ever actually been exercised by a
  real generator is unknown.
- **Whether the observed `corpus-`/`corpus-standard-` prefix convention is written
  down anywhere as a decision**, as opposed to being an unstated pattern four authors
  happened to converge on. No such record was found. If one exists, this document's
  SHOULD guidance should cite it directly instead of rating it an inference.
