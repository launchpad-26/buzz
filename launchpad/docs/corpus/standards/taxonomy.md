---
id: corpus-standard-taxonomy
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
  - statement: "type is a required front-matter field, a single string (not an array), constrained to a closed 13-member enum: architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "node.schema.json's own description of the type field states that its values are 'PRD #602's own enumerated list of in-scope surfaces, reused here rather than a second, independently invented taxonomy.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "PRD #602's success criteria list the same 13 surfaces verbatim -- 'architecture, layers, capabilities, platforms, implementation, interfaces/events, verification, operations, development, release, governance, agent and ingestion' -- as what the initial corpus must cover, calling them the surfaces 'recorded in the approved manifest.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 success criteria"
  - statement: "No document found at the checked revision materializes a separate 'approved manifest' artifact enumerating the 13 surfaces independently of PRD #602's own success-criteria bullet; issue #626 (task: generate the one-document one-task corpus manifest) is a different, not-yet-built manifest mapping documents to tasks, not a surface taxonomy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#626, read at the checked revision alongside #602"
  - statement: "Neither node.schema.json nor schema/README.md -- the two documents that own the type field's contract -- defines what each of the 13 enum values individually means beyond the field's one shared description, 'the corpus surface this node documents.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "validate.py contains no field-specific logic for type; the enum is enforced entirely through generic jsonschema validation against node.schema.json, the same mechanism that enforces every other closed-enum field."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "fixtures/invalid/unknown-type.md exists specifically to prove an unrecognized type value is rejected, and schema/tests/test_schema.py's test_unknown_type_rejected pins the single reported error to the type path with validator keyword 'enum.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/fixtures/invalid/unknown-type.md"
      - "launchpad/docs/corpus/schema/tests/test_schema.py"
  - statement: "COMPATIBILITY.md classifies a new enum value as an additive, non-breaking schema change that does not require a dated entry, in contrast to removing a field, removing an enum value, or narrowing a type, which is breaking and requires a dated entry plus a re-validation pass of every existing node in the same pull request."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "AGENTS.md's node-creation step 9 requires a relationships[].target to name a node that exists on the branch being merged into, checked with git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, not on the author's own branch, because the checker loads whatever is present where it runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At the checked revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists exactly four validated nodes -- launchpad/docs/corpus/AGENTS.md, launchpad/docs/corpus/README.md, launchpad/docs/corpus/standards/confidence.md and launchpad/docs/corpus/standards/decision-references.md -- and no status, identifiers, naming or other per-field standard, even though commits authoring several of those exist on unmerged task branches (for example corpus-standard-status on origin/task/1323-corpus-standard-status, confirmed not an ancestor of origin/launchpad by git merge-base --is-ancestor)."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/**, standards/confidence.md, standards/decision-references.md; origin/launchpad was at 0ffc1c9e4d875aab667c1ca5955f29984df0b18d"
  - statement: "The corpus node authored from AGENTS.md carries id corpus-agents and type: agent."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The three other nodes merged to origin/launchpad at the checked revision -- corpus-readme, corpus-standard-confidence and corpus-standard-decision-references -- all carry type: governance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "corpus-readme.md's own scope-and-omissions section reasons that 'type: governance is the closest true fit, not an exact one' because the enum carries no reference or index member, and states its own type is 'a candidate for revision' if a later, better-fitting standard appears -- while its id, being permanent, is not."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
  - statement: "governance is the appropriate type for a policy or standard node about the corpus's own rules, because three of the four type-differentiated nodes merged to origin/launchpad at the checked revision use it for exactly that shape of document, while the fourth (corpus-agents) uses the dedicated agent value reserved for agent-harness procedural instructions rather than defaulting to governance too."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.7
  - statement: "Issue #1324 requires this node to state its scope and authority, separate MUST requirements from SHOULD guidance, define enforcement and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1324 definition of done"
relationships:
  - type: references
    target: corpus-readme
---

# Standard: `type`

How to choose the `type` value for a corpus node -- the closed 13-member enum naming
"the corpus surface this node documents" -- when more than one value could plausibly
fit, and what to do if none of the 13 do.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| The field's machine contract -- required, single string, the 13 enum members | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of the front-matter fields | `launchpad/docs/corpus/schema/README.md` |
| Adding a 14th value to the enum | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| Where the 13 surfaces originate | `launchpad-26/buzz#602` (PRD, success criteria) |
| Creating, updating and retiring a node; the relationships merge-target rule | `launchpad/docs/corpus/AGENTS.md` |
| A worked example of an imperfect `type` fit, reasoned through in a node's own words | `launchpad/docs/corpus/README.md` |

Those files are authoritative. Where this document and any of them disagree, **they
win** -- this one has drifted and should be fixed.

**This document restates the schema only where its own subject forces it to.** A
standard about `type` cannot omit the enum it governs, so the *Where the 13 values
come from* section names all 13 members once. What is *not* restated: the rest of the
field-combination matrix, the other closed enums (`status`, `origin`, `audiences`),
and the relationship-type enum. The checker never reads this document's body, so a
second copy of any of those would go stale without turning anything red.

## Scope and authority

**This standard governs** the `type` key in a corpus node's front matter -- the one
place the field exists -- specifically the question of *which* of the 13 closed values
an author picks and why, when the node's subject could plausibly sit under more than
one.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces the closed set, `validate.py` runs that schema, and CI runs
`validate.py` on every corpus change. This document does not create the enum and
cannot add to or narrow it -- only `COMPATIBILITY.md`'s process can. What this document
adds is the half no schema can hold: how to choose honestly among the 13 when several
fit, and what to do when none do. That half is enforced by review, the same way
`corpus-standard-confidence.md` and `corpus-standard-decision-references.md` describe
their own non-structural halves.

**On where the 13 values themselves come from, PRD #602 outranks this document.** This
document does not invent, redefine or extend that list; it only helps an author pick
among values someone else already approved.

## Where the 13 values come from

`node.schema.json` states this directly: the `type` enum's values are "PRD #602's own
enumerated list of in-scope surfaces, reused here rather than a second, independently
invented taxonomy." Reading PRD #602 confirms it -- its success criteria list the same
13 words, in the same order, as what "the initial corpus" must cover, and call them the
surfaces "recorded in the approved manifest" (`interfaces/events` there and
`interfaces-events` in the enum are the same surface; the schema's value is simply
kebab-cased for the `^[a-z0-9]+(-[a-z0-9]+)*$` pattern every enum member and `id` must
satisfy).

**No separate "approved manifest" file was found at the checked revision.** The phrase
in `node.schema.json`'s description points at PRD #602's own success-criteria bullet,
which is the only concrete artifact enumerating the 13 surfaces this document could
locate. Issue #626 ("generate the one-document one-task corpus manifest") is a
different manifest under construction -- it maps individual documents to individual
GitHub tasks, not surfaces to meanings -- and had not landed at the checked revision.
If a dedicated manifest document is created later, this section should point at it
instead of at the PRD bullet directly.

**No document defines what each of the 13 words means, beyond the shared one-line
description.** `node.schema.json` and `schema/README.md` -- the two files that own the
field's contract -- both describe `type` only as "the corpus surface this node
documents." Neither breaks that description down per value. This document does not
manufacture 13 new definitions to fill that gap -- doing so would be exactly the
"second, independently invented taxonomy" the schema's own description warns against.
What it offers instead is a decision procedure for picking among the 13 as they stand,
grounded in how the corpus has actually used them so far.

## Choosing a value

1. **`type` MUST name exactly one of the 13 enum members.** The field is a single
   string, not an array -- a node cannot carry two. If a node's subject genuinely spans
   two surfaces, that is evidence the node is describing two ideas, not one; `AGENTS.md`'s
   one-node-one-idea rule governs that split, not this document.
2. **Pick the enum member whose plain-English name most concretely names the node's
   primary subject** -- the surface the node exists to document, not an implementation
   detail, file format, or where the node currently happens to live under
   `launchpad/docs/corpus/`.
3. **When more than one value plausibly fits, follow how the corpus has actually used
   the enum, not just what the label could technically stretch to cover.** At the
   checked revision, every merged node whose subject is the corpus's own rules,
   procedures or standards -- `corpus-readme`, `corpus-standard-confidence` and
   `corpus-standard-decision-references` -- carries `type: governance`. The one merged
   node written specifically as instructions for an agent harness -- `corpus-agents`,
   which `AGENTS.md` is -- carries the dedicated `type: agent` instead of defaulting to
   `governance` too. Read that as two data points, not a rule with the force of the
   schema: a node about corpus process and policy (this one included) reads as
   `governance`; a node whose primary job is to be resolved and followed as an agent
   harness's own instructions reads as `agent`.
4. **When the fit is still imperfect after that, say so in the node's own
   scope-and-omissions section, rather than silently picking.** `corpus-readme.md` is
   the worked example: it states plainly that "`type: governance` is the closest true
   fit, not an exact one," names the reason (the enum has no `reference` or `index`
   member), and marks its own `type` as a candidate for revision if a better-fitting
   value or standard shows up later -- while its `id`, being permanent, is not. That
   disclosure is cheap, it survives review, and it leaves a documented trail for the
   choice to be revisited without touching the one field that can never change.
5. **A node's `type` MAY be revised later; its `id` MUST NOT.** Changing `type` because
   a better-fitting value or a new enum member exists is a content correction, not a
   migration -- nothing generated derives its identity from `type` the way it derives
   from `id`.

## If none of the 13 fit

**Do not force a node into the nearest wrong value, and do not invent a 14th value in
one node's front matter.** The schema rejects any `type` outside the closed set --
`fixtures/invalid/unknown-type.md` is the fixture that proves it, and
`test_schema.py`'s `test_unknown_type_rejected` pins the rejection to the `type` path
with the `enum` validator keyword, so this is not a gap a single author can route
around.

Adding a genuinely new surface to the enum is a schema change, governed by
`launchpad/docs/corpus/schema/COMPATIBILITY.md` -- this document does not restate that
procedure. In summary shape only, so an author knows what to expect: a new enum member
is additive and non-breaking under `COMPATIBILITY.md`'s rule, but it still means
opening a pull request against `node.schema.json` itself, not a corpus content change,
and it is a decision about the taxonomy's shape rather than about where one node sits
within it -- read `COMPATIBILITY.md` before starting one.

## Enforcement, and where it stops

**Enforced mechanically**, by `node.schema.json` through `validate.py`, and in CI on
every change under the corpus root: `type` is required, is a string, and is one of the
13 named values. A node with any other value, or none, does not merge --
`fixtures/invalid/unknown-type.md` and `test_unknown_type_rejected` are the proof the
suite carries this today.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| Whether the chosen value is the *best* fit among plausible candidates | Any of the 13 values passes cleanly regardless of how well it fits; `governance` and `agent` are both technically legal on every node in the corpus today. |
| Whether two structurally similar nodes chose the same value | Nothing compares one node's `type` against another's. Drift between similar documents is invisible to every check that exists. |
| Whether an author consulted this document's guidance before picking | Silent. A node that never read the *Choosing a value* section validates identically to one that followed it. |

The pattern matches `corpus-standard-confidence.md`'s own enforcement table: everything
a schema can hold is held, and everything that requires judgment is not. Reviewing a
`type` choice means reading the node's subject and the guidance above, not the
validator's exit code.

## Exceptions and escalation

**There is no exception process for the closed set itself.** A value outside the 13 is
rejected before merge and cannot be waived by agreement -- adding a value is a schema
change under `COMPATIBILITY.md`, not an exception.

**When the choice among the 13 is genuinely unclear**, in order:

1. **Check how the corpus has already used the candidates**, per step 3 above --
   `governance` for corpus process/policy, `agent` for agent-harness instructions, and
   by extension the same look-at-precedent approach for any other pair of candidates as
   more nodes land.
2. **If precedent does not resolve it, pick the closer fit and disclose the gap** in the
   node's own scope-and-omissions section, the way `corpus-readme.md` does. Do not leave
   the reasoning implicit.
3. **If no value fits at all**, that is a signal about the enum, not about the node.
   Raise it as a schema-change proposal under `COMPATIBILITY.md`'s process rather than
   forcing a poor fit.

**When a reviewer disputes a `type` choice**, the author re-reads the node's actual
subject against step 3's precedent and either changes the value or documents why the
chosen value stands. Because `type` -- unlike `id` -- may be revised, this disagreement
does not block the node the way a disputed `id` would; it is resolved by editing the
field, in the same pull request, once agreed.

## Relationships

This node declares one: `references` → `corpus-readme`. `corpus-readme.md` is a merged
node on `origin/launchpad` at the checked revision (confirmed with
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, per
`AGENTS.md` step 9's rule that a target must exist on the branch being merged into, not
the author's own branch), and its own scope-and-omissions section is the concrete
worked example this document cites for *what an imperfect `type` fit looks like in
practice* -- exactly the supporting-context relationship `references` describes in
`relationships.schema.json`, with no ownership or currency dependency implied in either
direction.

No other merged node was found to carry the same kind of direct, substantive
connection. `corpus-standard-confidence.md` and `corpus-standard-decision-references.md`
share this document's shape -- both are closed-field standards with the same
MUST/SHOULD/Enforcement/Exceptions structure -- but that similarity is about how the
three documents are written, not about what either says regarding `type`, so it was not
treated as grounds for an edge here.

## Scope and omissions

**This document covers** what the `type` field is, where its 13 values originate, how
to choose among them when more than one plausibly fits, what to do when none fit, and
what enforcement does and does not reach.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The field-combination matrix and every enum member's exact spelling | `launchpad/docs/corpus/schema/node.schema.json` |
| Adding, removing or narrowing an enum value | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| The other closed front-matter enums (`status`, `origin`, `audiences`) | Their own standards, per-type standards owned somewhere in `#1307`-`#1351` (see `AGENTS.md`'s gap table; this document does not attempt its own subject-to-issue mapping, for the reason `AGENTS.md` itself gives) |
| Per-type templates -- the required sections and evidence expectations for a node of a given `type` | Somewhere in `#1307`-`#1351`, per `AGENTS.md`'s gap table; none had merged at the checked revision |
| Whether a node's classification is per-node or per-claim (that is `entry_class`, a different field) | Settled as per-entry by the schema; not this document's subject |
| Individual definitions for each of the 13 surface words | Not established anywhere in this repository at the checked revision; see *Where the 13 values come from* |

**Expected but not verified when this node was written**, per the rule in *Creating a
node* step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No author besides this one has applied the *Choosing a value* procedure.** The
  precedent it leans on is three `governance` nodes and one `agent` node -- a small
  sample. As more standards land, later authors may find the precedent-based heuristic
  strains in cases this document did not anticipate.
- **Whether a later, merged `corpus-standard-status.md` or similarly-named node changes
  anything here was not checked**, because none exists on `origin/launchpad` at the
  checked revision -- confirmed directly rather than assumed, since an earlier
  assumption that a sibling standard was already merged proved wrong when checked. If
  such a node lands with content bearing on `type` specifically, this document should be
  revisited against it.
- **No generated view or index was tested grouping nodes by `type`.** Whether a reader
  or a generator relies on `type` for navigation, and how forgiving that consumer is of
  an imperfect fit, is unknown.
