---
id: agents-invariants
type: agent
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "One file is one corpus node -- the single canonical, authored representation; anything else (JSON, an index, a graph serialization) is a generated derived view, never hand-authored."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Markdown files with YAML front matter are the one canonical, authored representation of every corpus node; JSON, search indexes, dependency graphs and any knowledge-crate-facing serialization are generated derived views, never hand-authored, always reproducible from the canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "One node is one independently maintainable idea; if a second concept, contract or procedure turns up while writing, it is filed as its own task rather than folded in."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "A node's id is kebab-case, assigned once, and never renamed -- generated views derive from it reproducibly, so renaming an id is a migration, not an edit."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "node.schema.json requires id, type, status, origin, audiences and evidence, permits relationships as the only other property, and rejects any field beyond those seven (additionalProperties: false)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "An evidence entry's entry_class of FACT requires an evidence array and forbids confidence and provided_by; INFERENCE requires evidence and confidence and forbids provided_by; TEAM_KNOWLEDGE requires provided_by and forbids confidence -- enforced by node.schema.json's allOf conditionals on entry_class."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "validate.py's find_duplicate_ids reports a hard error whenever two loaded nodes share the same id string."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's find_unresolved_relationship_targets reports a hard error whenever a relationships[].target names an id that matches no loaded node."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md's own creating-a-node step 9 requires relationship targets to be checked against the merge-target branch (e.g. git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus), not the author's own worktree, because the checker only loads whatever is present where it runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "validate.py's _classify_url rejects a GitHub repository file link that is not pinned to a full 40-character commit SHA, and separately rejects a pinned link that names no file within the repository."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's find_ownership_violations rejects every non-.md file under the corpus root that does not live in a generated/ directory, and rejects a hand-authored file placed inside generated/ too, because no generator yet exists to reproduce it from canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's _load_frontmatter splits a node's text on the frontmatter delimiter and assigns the remainder to a variable named _body, which no other function in the module reads -- the body is discarded before any check runs, for every node in every directory."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py defines EXCLUDED_TOP_LEVEL_DIRS = {\"schema\"} as its one directory-keyed rule that stops a subtree from being validated at all; no other directory (including templates/ or standards/) is excluded or treated specially."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's find_non_finite_confidence rejects a NaN or Infinity confidence value even though node.schema.json's minimum/maximum keywords cannot catch it, because every numeric comparison against NaN evaluates false and so silently passes the schema's own range check."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Retiring a node is a status change, not a deletion: the file stays, the checker keeps loading it, and inbound relationships keep resolving; the id is never reused or renamed once retired."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Citation checking is structural: the validator confirms a cited path resolves to a real file inside the repository, never that the file supports the statement it sits under; a FACT resting only on UNVERIFIED citations has not been checked by anything."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Two sources with authority over the same claim type that contradict each other are not silently resolved; the affected node stays unestablished/flagged (node.schema.json's status enum) until a human resolves it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "The launchpad -- corpus validate workflow runs validate.py on pull_request and on push to the launchpad branch, scoped to paths under launchpad/project-intelligence/corpus/**, launchpad/docs/corpus/** and the workflow file itself, so a local failure of the identical command is a CI failure."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "A policy-shaped corpus node must carry six required sections in this relative order -- Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions -- with additional sections permitted between them but none of the six absent, reordered among themselves, or silently empty."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "This node's type is agent rather than governance, on the reasoning that its subject -- the invariants an agent (or reviewer) must hold when authoring, updating or retiring a corpus node -- is the same corpus surface AGENTS.md itself documents (type: agent), whereas governance is used in this corpus for the standards/ and templates/ subtrees, a related but distinct family of meta-documents."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/templates/policy.md"
    confidence: 0.75
  - statement: "Parent Feature #620 ('corpus agent and ingestion guidance exists') lists #649 among 32 child document tasks under an agents/ and ingestion/ path family, with its stated outcome that 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures' -- the family this node's siblings (#640-#648, #650-#651) belong to, none of them merged at this node's authoring time."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
  - statement: "Issue #649's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#649 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
---

# Policy: agent-authored corpus node invariants

This node states the binding invariants an agent, or a reviewer checking an agent's
work, MUST hold whenever a `launchpad/docs/corpus/` node is created, updated, or
retired. It exists because `AGENTS.md` states these rules as connected prose without
stable, citable identifiers -- this node gives each one a short id (I1-I10) so a review
comment, a future corpus node, or a validator failure message can point at exactly one
of them, the same gap `templates/policy.md` itself exists to close for a policy-shaped
subject in general.

## Scope and authority

**This node governs** the invariants that MUST hold for any node under
`launchpad/docs/corpus/` at the moment it is created, updated, or retired -- what a
node's file representation must be, how its identity and relationships must behave,
what its front matter and evidence ledger must satisfy, and what retirement must and
must not do. **Its authority comes from** `node.schema.json` (the schema itself),
`launchpad/project-intelligence/corpus/validate.py` (the mechanical check CI runs), and
two accepted decisions, `ADR-0028` and `ADR-0029` -- all reused here, not reinvented.
**Where this node and any of those four sources disagree, that source wins** -- this
node has drifted and should be fixed, per `AGENTS.md`'s own stated precedence rule for
itself, which this node inherits.

| For | Read |
|---|---|
| Full authoring/updating/retiring procedure, not just its invariants | `launchpad/docs/corpus/AGENTS.md` |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| What the deterministic checker actually enforces | `launchpad/project-intelligence/corpus/validate.py` |
| Why Markdown + front matter is canonical | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| How conflicting evidence is ranked and escalated | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The general policy-node shape this document instantiates | `launchpad/docs/corpus/templates/policy.md` |

## MUST

| # | Requirement |
|---|---|
| **I1** | A corpus node MUST be exactly one Markdown file with YAML front matter -- the single canonical authored representation of its subject. Any other serialization (JSON, an index, a graph projection) MUST be a generated derived view, never hand-authored. Enforced by review only; `validate.py` rejects a stray non-`.md` file (see I9) but does not detect a second, duplicate representation of the same idea. |
| **I2** | A corpus node MUST document exactly one independently maintainable idea. A second concept, contract or procedure discovered while writing MUST be filed as its own task, not folded in. Enforced by review only -- `validate.py` never reads a node's body (see I7), so nothing mechanical can tell one idea from two. |
| **I3** | A node's `id` MUST be kebab-case and, once assigned, MUST NOT be renamed. Enforced partially: `node.schema.json`'s pattern constraint checks the kebab-case shape (a hard schema error otherwise); permanence itself -- that today's `id` is the same string as yesterday's -- is enforced by review, not the checker. |
| **I4** | A node's `id` MUST be unique across the whole corpus. Enforced by `validate.py`'s `find_duplicate_ids`, a hard error. |
| **I5** | A `relationships[].target` MUST name an `id` that exists among the nodes on the branch being merged INTO, not merely in the author's own worktree. Enforced by `validate.py`'s `find_unresolved_relationship_targets`, a hard error -- but only against whatever tree the validator is run against; checking the merge-target branch specifically is the author's own responsibility, not something the tool verifies for you. |
| **I6** | A node's front matter MUST validate against `node.schema.json` exactly: `id`, `type`, `status`, `origin`, `audiences` and `evidence` are required, `relationships` is the only other permitted field, and no additional field is allowed. Enforced by `validate.py`'s schema validation, a hard error. |
| **I7** | Every `evidence` entry's `entry_class` MUST be `FACT`, `INFERENCE` or `TEAM_KNOWLEDGE`, and the class chosen decides which further fields are required or forbidden. Enforced by `node.schema.json`'s conditional rules, a hard error for the field shape -- but whether the class chosen is the *honest* one (a `FACT` whose source was actually opened, not merely believed to exist) is enforced by review only; nothing mechanical can tell a verified claim from an unverified one wearing the same label. |
| **I8** | A GitHub repository file citation MUST be pinned to a full 40-character commit SHA and MUST name a file, never a mutable ref (`blob/main`) and never a repository/tree view with no file after it. Enforced by `validate.py`'s `_classify_url`, a hard error for both failure modes. |
| **I9** | A non-`.md` file placed under the corpus root MUST live inside a `generated/` directory, and even there is currently rejected, because no generator yet exists to reproduce it from canonical Markdown (owned by #1316 until one does). Enforced by `validate.py`'s `find_ownership_violations`, a hard error either way. |
| **I10** | Retiring a node MUST be done by changing its `status`, never by deleting the file, and a retired `id` MUST NOT be reused or renamed. Enforced only indirectly and only in part: deleting the file instead would surface as an I5 failure in every node whose relationship still targets it -- a side effect of a different check, not a dedicated one -- and reuse of a spent `id` is caught by review alone. |

## SHOULD

| # | Guidance |
|---|---|
| **Q1** | An author SHOULD run `python3 launchpad/project-intelligence/corpus/validate.py` locally before proposing a node as complete. The identical command runs in CI on every change under `launchpad/docs/corpus/`, so a local failure is a CI failure caught earlier. |
| **Q2** | An author SHOULD record the repository revision (`git rev-parse HEAD`) as a commit citation in the evidence ledger before drafting a claim, per `AGENTS.md`'s "Creating a node" step 3 and step 6. |
| **Q3** | An author updating a node SHOULD move the recorded revision only when every touched claim was re-verified at `HEAD`, or when the untouched claims were separately confirmed still to hold; otherwise it SHOULD be left in place. This is `AGENTS.md`'s own stated working practice, not yet settled corpus-wide (#1321). |
| **Q4** | An author who finds two authoritative sources of the same claim type in conflict SHOULD stop and record the conflict rather than resolving it themselves, per `ADR-0029`, and SHOULD set `status: flagged` when the conflict touches a claim central to the node. |

## Enforcement

**Mechanically enforced today**, via `validate.py` and the CI workflow that runs it on
every pull request and every push to `launchpad` touching the corpus: I4 (duplicate
ids), I5 (unresolved relationship targets, though only against whatever tree is
validated), I6 (schema shape), I7's field-shape half (which fields a given
`entry_class` requires or forbids), I8 (GitHub link pinning), and I9 (non-`.md`
placement).

**Enforced by review only, not by any check**: I1's ban on a second authored
representation of the same idea, I2's one-idea-per-node rule, I3's permanence of an
`id` once assigned, I7's honesty half (whether a claim labelled `FACT` was actually
verified), and I10's ban on reusing or renaming a retired `id`. `validate.py` discards
a node's Markdown body before any check runs, so nothing about prose content, claim
honesty, or historical `id` continuity is ever inspected mechanically -- these five
depend entirely on the pull-request reviewer, the same enforcement model
`templates/policy.md` names for itself.

**What a green `validate.py` run does NOT establish about a node's subject** -- stated
here because I7 and the Enforcement discipline above both require naming this
explicitly, not because it is repeated at length: that a citation actually supports the
statement it sits under, that an `UNVERIFIED` citation was ever opened, that a node's
body carries any particular structure, or that a line-numbered citation's line is
within the file's length. `AGENTS.md`'s own "Three things a passing run does not mean"
section is the fuller treatment; this node names the conclusion and links there rather
than restating it.

## Exceptions and escalation

**There is no blanket exemption from I1-I10.** They are the invariants the schema, the
validator, and the two cited ADRs already hold every node to; a node that cannot meet
one of them is not a candidate for an exception, it is not yet ready to merge.

**A disputed application of I1-I10 is a judgement, not an exception.** If an author and
a reviewer read a requirement differently -- for example, whether a given addition
counts as "a second concept" under I2 -- the author records the tension in the pull
request and the reviewer decides. A repeated disagreement is filed as an issue against
this node, because a rule two people read differently is a defect in the rule.

**`status: flagged` is Q4's mechanism, not a general escape hatch.** It names an
unresolved evidence conflict per `ADR-0029`; it is not a substitute for meeting I1-I10.

**A case none of I1-I10 covers is escalated, not invented.** Raise it as an issue
against parent Feature #620, describing the invariant that seemed to be missing and why
existing tooling did not catch its absence.

## Scope and omissions

**This node covers** the structural and procedural invariants a `launchpad/docs/corpus/`
node MUST satisfy when created, updated, or retired; which of those invariants are
mechanically enforced today versus review-only; and where each one's authority comes
from.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full authoring/updating/retiring procedure this node's invariants are drawn from | `launchpad/docs/corpus/AGENTS.md` |
| Per-type template requirements beyond the front-matter contract (what a concept, component, flow, etc. node's body must contain) | `launchpad/docs/corpus/templates/*.md`, most still landing per #605 |
| The corpus-wide standards track (naming, atomicity, provenance and the rest, under `standards/`) | the `standards/*.md` nodes |
| How review itself is conducted, by whom, with what authority | #1322 |
| Whether a recorded revision may stay put across an edit, and what partial re-verification requires | #1321 (unsettled) |
| The generated-artifact provenance and exception process for files under `generated/` | #1316 |
| Concrete agent procedures for ambiguity handling, evidence resolution, documentation creation/update/validation, concept resolution, change-impact analysis, repository navigation, stale-documentation handling and corpus usage | sibling tasks under parent Feature #620 -- #640, #641, #642, #643, #644, #645, #646, #647, #648, #650, #651 -- none merged at this node's authoring time |

**It does not restate `AGENTS.md`'s full procedural text.** Where a requirement here
needs its "why" or its worked examples, the table under *Scope and authority* names
where to read them; this node names the constraint and its enforcement, not the
reasoning behind it.

**This node's own relationships.** Declared: `depends-on: corpus-agents` -- real and
resolvable on `origin/launchpad`, and a genuine dependency: this node's own authority is
derived from `AGENTS.md`, not original to itself, the same relationship
`templates/policy.md` declares toward the same target for the same reason. Declared:
`implements: corpus-template-policy` -- real and resolvable on `origin/launchpad`; per
`relationships.schema.json`'s own worked example for `implements`, "source is the
concrete realization of target (e.g. a template instance of a standard)," and this node
is exactly that: a policy-shaped instance of `templates/policy.md`. No edge to any
sibling `agents/*.md` or `ingestion/*.md` task under Feature #620: none of them are
merged at this node's authoring time, so none is a valid relationship target.

**Expected but not verified when this node was written:**

- **Whether I1-I10 is an exhaustive extraction of every MUST-shaped statement in
  `AGENTS.md`**, or whether that document carries additional invariants this node
  omitted, was not audited clause-by-clause against `AGENTS.md`'s full text beyond the
  passages cited in the evidence ledger above.
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **Whether any sibling `agents/*.md` node, once drafted, will declare `depends-on`
  toward this node** is that sibling's own edit to make, not something decided here.
