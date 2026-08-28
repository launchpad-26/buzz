---
id: corpus-template-generated-index
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
relationships:
  - type: references
    target: corpus-agents
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "AGENTS.md's own definition of a corpus node states that a Markdown file with YAML front matter is the single canonical authored representation, and that 'anything else -- JSON, an index, a graph serialization -- is a generated derived view, never hand-authored,' naming an index as its own paradigm example of generated content rather than a passing mention."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "README.md restates the identical example near-verbatim -- 'JSON, indexes and graph serializations are generated derived views, never hand-authored' -- independently confirming an index is the corpus's own recurring example of what a generated (never hand-authored) artifact looks like."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- none named index or reference, so governance is the closest true fit for this template node itself, the same reasoning README.md gives for its own type choice."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's four nodes merged to origin/launchpad at the recorded revision, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance -- the precedent this node's own type: governance choice follows, and the same precedent the templates/capability.md template (read directly via git show, branch task/1329-corpus-template-capability) independently cites for its own identical choice."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "validate.py's discover_markdown_files walks the corpus root with a sorted rglob('*.md'), excludes the schema/ subtree by name, and resolves each path to reject anything that only appears to live under the corpus root (a symlink escaping it); find_non_canonical_nodes performs the same walk to report what discover_markdown_files silently excludes, rather than letting an excluded file go unmentioned."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "grep_recursive('index', paths=['launchpad/project-intelligence/corpus/', 'launchpad/docs/corpus/']) -> no generator or listing script found under either tree at the recorded revision; the only hits were validate.py's own generated-artifact test fixtures (misplaced-generated/index.json, unestablished-generated/generated/index.json) and this node's own scope table -- no script today walks the corpus and emits a table-of-contents-shaped document."
    entry_class: FACT
    evidence:
      - "grep_recursive('index', paths=['launchpad/project-intelligence/corpus/', 'launchpad/docs/corpus/']) -> no indexing/listing generator found, run against this fork's checkout at revision a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "launchpad/project-intelligence/indexer.py exists in the repository but is a RepoQL-backed crate-level symbol indexer for issue #206 (Symbol/CommitSummary/DefinedAt records, call-site scanning) -- a code-indexing tool unrelated to walking corpus nodes or producing a table-of-contents document, despite the name-alone similarity to what this template governs."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/indexer.py"
  - statement: "grep_case_insensitive('index', path='launchpad/Research/project-documentation-templates.md', ref='b0553469d9dff25eb3636ce1d0400e60dca1b559') -> zero matches, run 2026-08-27 against the docs/research-project-doc-templates branch tip (unmerged PR #1466) -- this topic is not covered by that note at all, so it is not cited here."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('index', path='launchpad/Research/project-documentation-templates.md', ref='b0553469d9dff25eb3636ce1d0400e60dca1b559') -> zero matches, run 2026-08-27"
  - statement: "PR #1513 (unmerged, branch task/1316-corpus-standard-generated-content) states two kinds of generated content are both generated derived views under ADR-0028 but the checker treats them completely differently: a non-Markdown artifact must live under generated/ and is rejected today because no generator can yet prove reproducibility, while a Markdown corpus node produced by a generator is loaded and schema-validated exactly like a hand-authored node -- its .md suffix is never inspected by the ownership check and is 'not an exemption from anything.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz PR #1513 (unmerged, branch task/1316-corpus-standard-generated-content), read via git show"
  - statement: "PR #1513's own evidence ledger names this issue directly -- 'Issue #1339 ... is open and scoped to create launchpad/docs/corpus/templates/generated-index.md as the per-type authoring template for a generated index node, distinct from this node's scope of policy rather than template' -- and its own MUST 5 and reference table both point the per-type template question at #1339 rather than answering it themselves."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz PR #1513 (unmerged, branch task/1316-corpus-standard-generated-content), read via git show"
  - statement: "Issue #891 ('generate corpus document generated/corpus-index.md', parent PRD #621) states its objective as creating that file 'as the single canonical generated index node for corpus index,' and its definition of done requires the generated file to name its generator, inputs, inclusion/exclusion rules and deterministic ordering; to carry an explicit generated/do-not-edit marker; to be regenerable from canonical nodes without authored knowledge; and to produce no diff on a no-change rerun at the same revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#891"
  - statement: "The generated/*.md issue family under parent PRD #621 (#891-#906, sixteen issues, titles read directly via gh issue view) carries the identical boilerplate phrase 'single canonical generated index node for X' in every issue body (confirmed directly on #891 and #892) regardless of the target document's actual name; nine of the sixteen are literally *-index.md named (corpus-index, crate-index, database-index, decision-index, event-kind-index, layer-index, nip-index, provenance-index, test-index) and seven are not (coverage, dependency-graph, doc-to-code-map, documentation-graph, orphaned-docs, stale-docs, test-to-doc-map)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#891 through #906 (issue titles read directly via gh issue view; only #891 and #892 bodies were read in full)"
  - statement: "Reasoning from each of the seven non-*-index.md-named documents' own filename alone (not from reading their full issue bodies, which was not done for #893-#906): dependency-graph.md and documentation-graph.md name graphs (edges between nodes, not a flat listing); doc-to-code-map.md and test-to-doc-map.md name mappings (pairs, not a listing of one node type); orphaned-docs.md and stale-docs.md name audit-style exception filters rather than a full listing; coverage.md names a metric report. None of the seven is therefore a table-of-contents-shaped listing of other corpus nodes in the sense this template governs, though this is inferred from filename semantics, not confirmed by reading each issue's full body."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/892"
      - "https://github.com/launchpad-26/buzz/issues/896"
      - "https://github.com/launchpad-26/buzz/issues/897"
      - "https://github.com/launchpad-26/buzz/issues/898"
      - "https://github.com/launchpad-26/buzz/issues/902"
      - "https://github.com/launchpad-26/buzz/issues/904"
      - "https://github.com/launchpad-26/buzz/issues/906"
    confidence: 0.7
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts,' and this is the acceptance bar this node is built against rather than issue #1339's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria (read directly via gh issue view; AGENTS.md requires an issue-URL-only citation to stay TEAM_KNOWLEDGE, not be promoted to FACT, since the validator can only report it UNVERIFIED and issue content is mutable GitHub state, not committed code)"
  - statement: "Issue #1339's own Definition of Done is byte-identical to the standards-track boilerplate copied across #1326-#1351 ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same residue the batch dispatch brief for this task set independently identified."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1339 Definition of Done (read directly via gh issue view; same TEAM_KNOWLEDGE-not-FACT rule as above applies)"
  - statement: "Sphinx's toctree/genindex mechanism was considered as a candidate industry model for auto-generated documentation indexes, but two WebFetch attempts against sphinx-doc.org (usage/index.html and usage/restructuredtext/domains.html) returned navigation and redirect pages with no substantive content on either mechanism, so no primary-source claim about Sphinx is made anywhere in this node."
    entry_class: FACT
    evidence:
      - "webfetch('https://www.sphinx-doc.org/en/master/usage/index.html') -> navigation page, no genindex/toctree content; webfetch('https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html') -> redirect page, no content; both run 2026-08-27"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the batch-1 through batch-4 template PRs (#1527-#1548) nor this batch's own siblings (#1330, #1338, #1341, #1344, #1350) are merged, so none of them are valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
---

# Template: generated-index

How to write the body of a corpus node that is a **generated index** -- a Markdown
node, produced by a tool rather than a person, that is a table-of-contents-shaped
listing of other corpus nodes (for example the eventual
`launchpad/docs/corpus/generated/corpus-index.md`, `crate-index.md`,
`database-index.md`, `decision-index.md`, `event-kind-index.md`, `layer-index.md`,
`nip-index.md`, `provenance-index.md` or `test-index.md`). This is a template node,
not a policy node -- it prescribes the shape of a future generated document's *body*,
not a MUST/SHOULD rule about corpus-wide behavior. See *Note on Definition of Done*
for why that distinction matters for this specific node, and *Boundary* for why this
is a narrower thing than "any generated content."

## Scope and authority

**This node covers** what a generated-index node's body must contain: its required
sections, the evidence expectations that apply to a document nobody hand-wrote, and
the model this template adapts.

**It does not cover:**
- What counts as "generated" at all, where a non-Markdown generated artifact must
  live, or the MUST/SHOULD rules the corpus applies to any generated content. That is
  `#1316`'s policy (unmerged PR #1513 at the time this node was written) -- see
  *Boundary against #1316* below for the exact line, stated once rather than restated
  throughout this document.
- The front-matter contract itself (`node.schema.json` governs that, unconditionally,
  for every node type, generated or not) or how to create/update/retire a node
  procedurally (`AGENTS.md` governs that).
- Building the generator itself, or any specific generated document's actual content.
  Each is its own task under parent PRD #621 (`#891`-`#906`), not this node.
- A generated document that is not index-shaped -- a dependency graph, a
  documentation-to-code map, an audit report of orphaned or stale docs, a coverage
  report. See *Boundary against the rest of the `generated/*.md` family* below.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter on a generated Markdown node exactly as on a
hand-authored one, `validate.py` runs that schema, and CI runs `validate.py` on every
corpus change. What this node adds is the half no schema can hold -- which sections a
generated-index node's body needs, what a reader can trust about a document nobody
wrote by hand, and what model was checked before this template's structure was
decided. That half is enforced by review, the same way `#1316`'s own policy describes
its own SHOULD half as review-enforced rather than validator-enforced.

| For | Read |
|---|---|
| What counts as generated content, and the MUST/SHOULD rules for it | `#1316` / `standards/generated-content.md` (unmerged PR #1513 at authoring time) |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The deterministic corpus-node walk this template adapts | `launchpad/project-intelligence/corpus/validate.py` (`discover_markdown_files`) |
| Building the generator | `launchpad-26/buzz#633` |
| Each concrete generated document under `generated/` | `launchpad-26/buzz#891`-`#906` (parent PRD #621) |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Boundary against `#1316`

`#1316` (`standards/generated-content.md`, unmerged PR #1513 at the time this node was
written) is the general policy: what "generated" means anywhere under the corpus root,
where a non-Markdown artifact must live, and that a Markdown node produced by a
generator is validated exactly like a hand-authored one -- its own words, "a `.md`
suffix is not an exemption from anything." That node's own evidence ledger names this
issue directly as "the per-type authoring template for a generated index node,
distinct from this node's scope of policy rather than template," and its own reference
table points the per-type template question at `#1339` rather than answering it. This
node does not restate any of `#1316`'s MUST/SHOULD rules, its enforcement table, or
its exception process -- read `#1316` for those. What this node adds is narrower and
lower-level: given that a document is a generated Markdown node and that document is
specifically index-shaped, what must its body contain.

## Boundary against the rest of the `generated/*.md` family

The sixteen tasks under parent PRD #621 (`#891`-`#906`) all target
`launchpad/docs/corpus/generated/*.md` and all carry the identical boilerplate phrase
"single canonical generated index node for X" in their issue bodies (confirmed by
reading #891 and #892 in full), regardless of what X actually is. Read past the
boilerplate: nine of the sixteen are literally `*-index.md` named -- `corpus-index`,
`crate-index`, `database-index`, `decision-index`, `event-kind-index`, `layer-index`,
`nip-index`, `provenance-index`, `test-index` -- a direct, strong signal that they are
table-of-contents-shaped listings of other corpus nodes or repository artifacts. The
other seven are generated, and Markdown, and governed by `#1316`'s policy exactly the
same way, but their own names signal a different shape -- **inferred from the
filename alone, since #893-#906's full bodies were not read** (see the evidence
ledger's `INFERENCE` entry for this table, confidence 0.7):

| Document | Shape inferred from its name | Why not an index |
|---|---|---|
| `coverage.md` (`#892`) | A coverage report | States a metric, not a listing of nodes |
| `dependency-graph.md` (`#896`) | A graph | Edges between nodes, not a flat listing |
| `doc-to-code-map.md` (`#897`) | A mapping | Pairs, not a listing of one node type |
| `documentation-graph.md` (`#898`) | A graph | Same reason as `dependency-graph.md` |
| `orphaned-docs.md` (`#902`) | An audit report | A filtered exception list, not a full listing |
| `stale-docs.md` (`#904`) | An audit report | Same reason as `orphaned-docs.md` |
| `test-to-doc-map.md` (`#906`) | A mapping | Same reason as `doc-to-code-map.md` |

A future author of one of those seven should not reach for this template on the
strength of its issue's boilerplate phrase alone; a graph, a mapping, and an audit
report each need their own per-type template, none of which exist yet and none of
which are this node's to write. If any of the seven turns out, on reading its full
issue body, to actually be index-shaped despite its name, that is new information this
node did not have and does not anticipate.

**What makes a document index-shaped, for this template's purposes**: it walks a
defined, bounded set of other corpus nodes or repository artifacts of one kind, and
lists each one with enough identifying information (an id, a path, a title) for a
reader to go find it -- structurally the same shape `discover_markdown_files` already
produces for the corpus's own `.md` nodes, applied to whatever the specific index's
subject is (crates, database tables, decisions, event kinds, NIPs, and so on).

## Model this template adapts

**`validate.py`'s own discovery contract is the verified model**, per the brief's
explicit steer for this node and because it is the one precedent this repository
actually runs today. `discover_markdown_files` walks the corpus root with a sorted
`rglob("*.md")`, excludes `schema/` by name (not by pattern -- a known, named
exception, not a heuristic), and resolves every path to reject anything that only
*appears* to live under the corpus root, such as an escaping symlink;
`find_non_canonical_nodes` performs the identical walk to report what the first
function silently excludes, so an excluded file is never simply dropped without a
trace. The habit this template adapts from it: **an index generator should reuse the
same "what counts as a node" contract the validator already enforces, rather than
inventing a second, independent notion of the corpus's contents that can silently
diverge from the one CI actually checks.** A generated index built against its own,
separate discovery logic could list a node the validator has already rejected, or omit
one the validator accepts -- the exact kind of drift a *generated* document, whose
whole premise is that nobody is proofreading it by hand, is least equipped to catch.

**An external model was sought and not found readable.** Static-site generators
commonly auto-generate an index or table of contents from source documents (Sphinx's
`toctree`/`genindex` is the best-known example), and that was the first candidate
checked. Two `WebFetch` attempts against `sphinx-doc.org` -- the top-level usage page
and the reStructuredText domains page -- returned navigation and redirect content with
no substantive description of either mechanism, so this node makes no claim about what
Sphinx actually does; it is named here as a considered-and-blocked candidate, in the
same spirit the batch-4 `capability` template documented TOGAF's login wall, not as a
source this template draws on.

## Required sections

A corpus node using this template's shape must carry the following in its body, in
addition to whatever schema-required front matter `node.schema.json` demands of every
node, generated or not:

1. **A generated/do-not-edit marker**, near the top of the body, stating plainly that
   the file was produced by a tool and naming the tool. `#1316`'s own SHOULD guidance
   already asks for this on any generated Markdown node; this template makes it the
   first required section specifically for an index, because a reader who mistakes a
   generated listing for a hand-authored one may "fix" a missing entry by editing the
   file directly instead of by fixing the generator or its input.
2. **Generator, inputs, and ordering rule.** Which script produced this file (once
   `#633`'s generator exists), what it read to produce the listing (a glob, a schema
   field, a directory), and the deterministic order the listing is sorted in. Without
   this a reader cannot tell whether a missing entry is a generator bug or an
   intentional exclusion.
3. **Inclusion and exclusion rules, stated explicitly.** What makes something appear
   in this index, and what is deliberately left out -- the same distinction
   `validate.py` draws between `discover_markdown_files` (what is walked) and the
   `schema/` exclusion (what is deliberately not). An index with no stated exclusion
   rule invites the question of whether an absence is a bug.
4. **The listing itself**, one entry per indexed item, each carrying enough to find
   the source: at minimum an id (or equivalent stable identifier) and a path.
5. **Relationships**, per the guidance below.
6. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node does
   not cover, who owns it, and separately, what was expected but could not be verified
   when the node was written. For a generated node this section is generated too, not
   an authored afterthought -- see *Evidence expectations*.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Index name]: generated index

> **Generated -- do not edit by hand.** Produced by [generator script path], from
> [inputs]. Edits made directly to this file are overwritten on the next
> regeneration; change [generator script path] or its inputs instead.

## Generator

- **Script**: [path to the generator, once #633's generator exists]
- **Inputs**: [what it reads -- e.g. `discover_markdown_files(corpus_root)`'s output,
  a specific front-matter field, a directory glob]
- **Ordering**: [the deterministic sort rule -- e.g. by id, alphabetically]

## Inclusion and exclusion rules

This index includes:
- [what qualifies an item for a listing entry]

This index deliberately excludes:
- [what is left out, and why -- e.g. "the schema/ subtree, for the same reason
  validate.py excludes it: schema-testing infrastructure, not corpus content"]

## [Index name]

| [Column] | [Column] |
|---|---|
| [entry] | [entry] |

## Relationships

- references: <corpus-agents, or whatever node names the concept this index
  instantiates a generated view of>

## Scope and omissions

**This node covers** a generated listing of [subject], as of [generation revision or
timestamp].

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- [A generated node's version of this section should name what the *generator*
  could not establish -- e.g. an input it could not read -- not what a human author
  forgot to check, since no human authored this body.]
````

## Evidence expectations

The corpus-wide evidence rules in `AGENTS.md` apply unchanged, with one adaptation for
a document nobody hand-wrote: **the generator, not a human author, is the source of
the claims a generated-index node makes**, so its evidence ledger's job shifts from
"what did the author verify" to "what does the generator guarantee, and by what
mechanism." Two expectations follow specifically:

- **The listing itself needs no per-entry `FACT` citation.** Each row is itself
  produced by a deterministic, re-runnable walk (per the model above) -- the
  generator run *is* the evidence, the same way `AGENTS.md` treats a directly-run
  check like `git cat-file -e <sha>` as checkable even though `validate.py` cannot
  check it. Citing the generator script and its inputs (Required section 2) is what
  makes that walk re-checkable by a reader; it stands in for citing each row
  individually, which would be circular -- the row exists because the walk produced
  it, not because a source document independently confirms it belongs.
- **A claim about the generator's own behavior -- determinism, reproducibility, no
  hand-editing -- is `TEAM_KNOWLEDGE` until a real generator exists and a no-change
  rerun has actually been observed**, per `#891`'s own definition of done requiring
  exactly that test. Asserting determinism as `FACT` before any generator has ever
  run against this corpus would be the same "a source exists that probably says so"
  failure `AGENTS.md` warns `FACT` is not for.

## Relationships

A node built from this template:

- **should** declare `references` toward `corpus-agents` (or a more specific node,
  once one exists) naming the concept the index is a generated view of, mirroring
  this template node's own edge -- justified below.
- **must not** hand-author any of the four generated-inverse relationship types
  (`depended-on-by`, `superseded-by`, `implemented-by`, `has-part`) -- `#1316`'s MUST 6
  already states this for every generated node, and `node.schema.json`'s enum has no
  field for any of those names regardless.
- **may** declare `implements` toward this template node itself (target:
  `corpus-template-generated-index`), once this node is merged, if the generator's
  author wants the generated `implemented-by` edge -- optional, since the
  generated/do-not-edit marker and the required-sections shape already show which
  template a document followed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: `references -> corpus-agents`. Checked
immediately before finalizing this front matter, not from memory: `git ls-tree -r
--name-only origin/launchpad -- launchpad/docs/corpus` (run 2026-08-27) returned
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence` and
`corpus-standard-decision-references` -- all four merged to `launchpad`. The edge to
`corpus-agents` is justified, not decorative: `AGENTS.md` itself names an index as its
own paradigm example of a generated derived view ("anything else -- JSON, an index, a
graph serialization -- is a generated derived view"), and this node exists to give
that exact example a body shape to follow -- the same justification standard `#1316`'s
own `references -> corpus-agents` edge used ("names the exact gap this node fills").
No edge is declared to `corpus-readme` or either sibling standard: neither states or
depends on anything about a generated index specifically beyond the same one-line
example `AGENTS.md` already carries, and an edge without a claim it supports would be
decoration. This node deliberately does **not** target `#1316`/`corpus-standard-
generated-content` (or any other sibling drafted in this same batch or the templates
track generally) -- none of them exist on `origin/launchpad` as of the check above,
regardless of what any individual worktree shows.

## Note on Definition of Done

Issue `#1339`'s own Definition of Done carries the same four bullets found copied
across `#1326`-`#1351` -- "states scope and authority/source of the policy,"
"separates MUST requirements from SHOULD guidance," "defines enforcement/checks and
exception/escalation process," "links decisions or higher-order policy instead of
duplicating them" -- verbatim from the standards-track issues that produced
`standards/confidence.md` and, separately, `#1316`'s own (unmerged) `standards/
generated-content.md`. That checklist describes a **policy/standard** node: a
MUST/SHOULD normative document over existing corpus behavior. This node is a
**template**: a prescription for the shape of a future document's body, and in this
node's specific case, a future document nobody will hand-write at all. The real
acceptance criterion, from parent Feature `#605` itself, is: *"every template states
its purpose, required sections, evidence expectations and the industry model/standard
it adapts."* This node is built against that sentence -- *Required sections*,
*Evidence expectations* and *Model this template adapts* above answer it directly --
rather than against the standards-track checklist, which does not fit a document with
no MUST/SHOULD normative claims of its own to separate; those already live in `#1316`,
which this node links to rather than duplicates.

## Scope and omissions

**This node covers** what a generated-index node's body must contain: the
generated/do-not-edit marker, the generator/inputs/ordering-rule disclosure, explicit
inclusion and exclusion rules, the listing itself, the boundary against `#1316`'s
general policy and against the seven non-index-shaped siblings in the `generated/*.md`
family, the evidence expectations adapted for a document nobody hand-wrote, and the
model considered (`validate.py`'s own discovery contract, verified; Sphinx's
`toctree`/`genindex`, sought and not found readable).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What counts as generated content at all, and the MUST/SHOULD rules for it | `#1316` (unmerged PR #1513 at authoring time) |
| Building the generator itself | `#633` |
| Any specific generated document's actual content | The individual `#891`-`#906` tasks (parent PRD #621) |
| A generated document that is a graph, a mapping, or an audit report rather than an index | Not this template; none of those per-type templates exist yet |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**

- **No generator exists yet, and no generated-index document has ever been produced
  from this template.** Every required section and the skeleton above is validated
  only against `validate.py`'s existing (non-index-producing) discovery contract and
  against the sixteen `generated/*.md` issue bodies' stated intentions, not against a
  real generated-index node passing `validate.py` end to end. `#891`'s own no-change-
  rerun requirement is stated here as a requirement, not as something observed.
- **Sphinx's `toctree`/`genindex` mechanism was never actually read.** Two `WebFetch`
  attempts against its own documentation returned no substantive content; this node
  makes no claim about what Sphinx does beyond that it could not be reached in the
  time available, and does not guess at its behavior from secondhand familiarity.
- **Whether `launchpad/project-intelligence/indexer.py` (issue #206's crate-symbol
  indexer) will ever share code, conventions, or output shape with a future corpus
  generated-index generator was not established.** They are confirmed to be different
  things today by reading `indexer.py` directly; whether a later generator reuses any
  part of it is a design question for `#633`, not answered here.
