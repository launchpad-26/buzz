---
id: agents-corpus-usage
type: agent
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "node.schema.json requires exactly id, type, status, origin, audiences and evidence, additionally permits only relationships, and sets additionalProperties to false, so a reader can trust that every corpus node's machine-checked surface is those seven fields and no others."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "AGENTS.md's own 'Creating a node' step 2 is 'Check nothing already covers it. Read the existing nodes under launchpad/docs/corpus/. If one is close, you are updating, not creating' -- a one-line instruction with no worked method for how a reader actually does that check."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md states that 'relationships are optional and must resolve', that declaring none is always valid but must be justified honestly rather than by the stock phrase 'there was nothing to point at', and that two independent agents authoring sibling nodes previously copied that phrase and produced a false justification because it read as a general rule rather than a fact about one moment -- the corrective is to enumerate what exists (`ls launchpad/docs/corpus/**/*.md`) and give the real reason."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "At repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, origin/launchpad's corpus tree contains AGENTS.md, README.md, agents/invariants.md, the architecture/** subtree, schema/** (excluded from validation), standards/*.md, and templates/*.md; none of the other 30 sibling agents/*.md or ingestion/*.md document tasks under parent Feature #620 are present, so none of them is a valid relationships[] target for this node."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/containers/**, architecture/context/**, architecture/deployment/**, architecture/flows/**, architecture/principles/**, capabilities/** (NOTE: capabilities/, layers/, development/ subtrees are separate in-progress Features, not part of #620's 32), schema/** (excluded), standards/*.md, templates/*.md"
  - statement: "templates/procedure.md prescribes Diátaxis's How-to form for a corpus node's body -- goal-oriented, sequenced instruction for an already-competent reader -- and explicitly distinguishes it from a runbook by when the reader needs the guide: a procedure is for a task the reader chooses to perform on their own schedule, a runbook is for a condition that has already occurred and demands a response."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/procedure.md's Required sections are: Overview, an optional Before you start, one numbered task sequence per logical goal (capped near 8-10 steps, forking into labeled sub-sequences when a task genuinely branches), See also, a Boundary statement, Relationships, and Scope and omissions, per AGENTS.md's own step 8."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "templates/runbook.md grounds its own form in the Google SRE Workbook's definition of a playbook as real-time, alert-triggered response guidance, and separately warns that a deterministic list of commands run every time a particular alert fires should be automated rather than documented -- neither trait fits 'how a reader searches for and traverses the corpus', which is chosen-schedule usage, not an alert response."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
  - statement: "The sibling agents-invariants node reasons that its own type is agent rather than governance because its subject is the same corpus surface AGENTS.md itself documents, whereas governance is this corpus's precedent for the standards/ and templates/ subtrees -- a related but distinct family of meta-documents about the corpus's own authoring rules rather than about how a reader uses it day to day."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "standards/linking.md MUST 3 requires a pointer to a section within a document to name the target heading in prose (conventionally italicized) and MUST NOT rely on a Markdown anchor fragment, and states that across the corpus's merged nodes a body-prose mention of a sibling file or decision record is written as a bare repository-relative path or filename in backticks, not a Markdown hyperlink, when the node's primary purpose is being followed as instructions rather than browsed for navigation."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/linking.md"
  - statement: "In this same authoring session, mcp__repoql__explore, scoped to file:///launchpad/docs/corpus/**, returned corpus nodes ranked by relevance to a stated question, each with its outline of Markdown headings (for example AGENTS.md's 'Working with the documentation corpus' returned at 100% relevance with its full heading tree, followed by templates/specification.md, templates/invariant.md, templates/generated-index.md, and standards/naming.md at descending scores) -- explore answers 'which node(s) are relevant to this question', not 'does an exact string exist'."
    entry_class: FACT
    evidence:
      - "mcp__repoql__explore(keywords='corpus usage agents invariants', question='Which corpus nodes under launchpad/docs/corpus exist about agent invariants?', uriGlob='file:///launchpad/docs/corpus/**') -> ranked list headed by file:///launchpad/docs/corpus/AGENTS.md at 100%, with its heading outline, followed by templates/specification.md (73%), templates/invariant.md (70%), templates/generated-index.md (62%), standards/naming.md (69%)"
  - statement: "In this same session, mcp__repoql__query's SELECT ... FROM glob_files('launchpad/docs/corpus/**/*.md') and SELECT ... FROM glob_files('concept:///**') both returned real file listings over their respective scopes -- the corpus glob returned launchpad/docs/corpus/AGENTS.md, README.md, and architecture/containers/*.md paths; the concept:/// glob returned concept:///README.md and files under concept:///knowledge/**.md and concept:///rule/**.md, none of which are launchpad/docs/corpus paths."
    entry_class: FACT
    evidence:
      - "mcp__repoql__query(sql=\"SELECT uri FROM glob_files('launchpad/docs/corpus/**/*.md') LIMIT 5;\") -> file:///launchpad/docs/corpus/AGENTS.md, README.md, architecture/containers/agent-runtime.md, cli.md, desktop.md"
      - "mcp__repoql__query(sql=\"SELECT uri FROM glob_files('concept:///**') LIMIT 10;\") -> concept:///README.md, concept:///knowledge/CorpusBatchBodiesSkipIssueTypeSection.md, concept:///knowledge/CorpusPolicyTemplateGeneralizesStandardsTrack.md, concept:///rule/CorpusValidateToolResultCitationNoLiteralNewlines.md (and others)"
  - statement: "Also in this same session, mcp__repoql__read on a specific corpus file (with or without a #symbol or #line fragment) and mcp__repoql__query's search() function both failed -- the first read attempts returned 'Out of Memory Error: failed to pin block of size 256.0 KiB (7.4 GiB/7.4 GiB used)', and a subsequent read plus a search() call both returned 'DuckDB failed during read-only query ... The database was invalidated by an earlier fatal failure', after explore and a plain glob_files() SELECT had already succeeded earlier in the identical session -- so at this moment RepoQL's read-by-symbol/line and semantic-search paths were unusable while its explore and plain-SQL-listing paths still were."
    entry_class: FACT
    evidence:
      - "mcp__repoql__read(uri='file:///launchpad/docs/corpus/agents/invariants.md#symbol=* => structure') -> Out of Memory Error: failed to pin block of size 256.0 KiB"
      - "mcp__repoql__read(uri='file:///launchpad/docs/corpus/AGENTS.md#line=128,140') -> Out of Memory Error: failed to pin block of size 256.0 KiB"
      - "mcp__repoql__query(sql=\"SELECT uri, score FROM search(...)\") -> DuckDB failed during read-only query ... database was invalidated by an earlier fatal failure"
  - statement: ".repoql/concepts/README.md, the entry point for this same repository's own RepoQL concept:/// memory, states 'read(\"concept:///... => structure\") if you have RepoQL, else .repoql/concepts/ on disk' and lists its capsules under category headings (Rule) with CamelCase filenames such as concept:///rule/PrGateBlocksCdChainBeforeGhPrCreate.md -- a different location, naming convention, and governing mechanism than a launchpad/docs/corpus node's kebab-case id and node.schema.json contract. The .repoql/ directory itself is not part of this repository's tracked content at all: git check-ignore confirms it is excluded by a global gitignore rule, so a fresh clone or worktree (this one included) starts with no .repoql/ directory present until RepoQL's host creates it locally -- a further, structural difference from launchpad/docs/corpus, which is tracked, reviewed, and merged like any other repository content."
    entry_class: FACT
    evidence:
      - "read(uri='.repoql/concepts/README.md') -> local file present in the main checkout, contents quoted above; not present in this worktree"
      - "git_check_ignore(path='.repoql/concepts/README.md') -> matched by /home/serina/.config/git/ignore:14:'**/.repoql/'"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Whether this node's own type should be agent (the reasoning above, mirroring agents-invariants) or whether a future corpus-wide decision reclassifies reader-facing usage guidance differently, is a judgment call, not a settled rule -- no source states a rule specific to 'usage' versus 'invariants' documents within the agent surface."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "This node draws its boundary against sibling task #650 (agents/repository-navigation.md) from that issue's title alone, reasoning that 'repository navigation' names the wider Buzz repository's directory/file layout (crates/, desktop/, mobile/, etc.) while this node's subject is navigating the docs/corpus knowledge graph itself -- a plausible reading of the title, not a verified boundary, since #650 is unbuilt and its content cannot be read."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/650"
    confidence: 0.55
  - statement: "Parent Feature #620 requires that 'no broad overview page duplicates canonical claims owned by atomic child nodes; navigation links instead' and that 'an independent developer/agent can answer a representative question in this feature area by traversing corpus nodes to implementation and verification evidence' -- this node is built to satisfy that traversal criterion directly, rather than against issue #644's own copied-over Definition of Done tail."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 acceptance criteria"
  - statement: "Issue #644's own Definition of Done asks that the document 'states goal, prerequisites and allowed environment/scope', 'provides ordered steps that are executable and project-specific', 'defines success verification and rollback/cleanup where relevant', and 'links authoritative commands/config rather than giving generic advice' -- how-to/runbook-shaped boilerplate, not the policy-shaped boilerplate seen on sibling #649/#1345/#1346, and read here per the corpus-batch-author brief's own instruction to build against Feature #620's real acceptance criteria rather than follow the copied tail literally."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#644 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-procedure
---

# Using the corpus: finding coverage and traversing to evidence

How a reader -- an agent about to author a node, or anyone else, human or agent, trying
to answer a question -- checks whether `launchpad/docs/corpus/` already covers a subject
before creating a new node, and how to get from a question to the right node's cited
implementation and verification evidence. This is the reader-facing "how" behind
`AGENTS.md`'s own "Creating a node" step 2, not a restatement of it, and it is the
practical traversal step Feature #620 itself names as an acceptance criterion: "an
independent developer/agent can answer a representative question in this feature area by
traversing corpus nodes to implementation and verification evidence."

## Before you start

- Know what a corpus node is (`AGENTS.md`'s *What a corpus node is*) and where the corpus
  root is (`launchpad/docs/corpus/`, excluding `schema/`).
- Know that a node's `evidence[]` ledger is the only place a claim's supporting source is
  recorded, and that `relationships[]` is the only typed, checked pointer between nodes --
  both covered by `AGENTS.md`, not restated here.

## Task 1: Check whether a subject is already covered before creating a node

1. **Enumerate the real tree**, not a guess or a stale memory of it: `ls
   launchpad/docs/corpus/**/*.md` locally, or `git ls-tree -r --name-only
   origin/launchpad -- launchpad/docs/corpus` against the branch you will merge into --
   the same command `AGENTS.md`'s own step 9 requires before adding a relationship, for
   the identical reason: what exists in your worktree and what exists on the merge
   target can differ.
2. **Search by subject, not by guessed id.** Grep the tree for the term your subject
   would naturally be called (`grep -ril <term> launchpad/docs/corpus/`), and separately
   check the directory that matches your subject's `type` -- a `capabilities`-typed
   subject is more likely already covered under `capabilities/` than under `operations/`.
   An id you have not seen yet is not evidence nothing covers the subject; a directory
   you have not searched is.
3. **If RepoQL is available, use `explore` scoped to the corpus** (`uriGlob:
   "file:///launchpad/docs/corpus/**"`) with a full-sentence question about your subject.
   It ranks nodes by relevance to that question and returns each one's heading outline,
   which answers "is something *close* to this already here" faster than reading whole
   files -- see *Tooling notes* below for what this looked like when tried directly.
4. **Read the close candidates, not just their titles.** A node whose title looks
   adjacent may cover a narrower or broader idea than yours; open it and compare against
   `AGENTS.md`'s "one node is one independently maintainable idea" test before deciding.
5. **Decide: update, create, or split.** If an existing node already states your
   subject's canonical claim, you are updating it (`AGENTS.md`'s *Updating a node*), not
   creating a new one. If your subject is genuinely a second idea living inside an
   existing node's scope, that is a candidate for filing separately, not folding in.
6. **If nothing covers it, say so with the enumeration from step 1 as your evidence**,
   not the bare sentence "there was nothing to point at" -- `AGENTS.md` names that exact
   phrase as the one two prior agents copied into a false justification once a second
   node already existed.

## Task 2: Traverse from a question to a node's cited evidence

1. **State the question concretely** -- "does Buzz enforce subsystem isolation between
   `buzz-pubsub` and `buzz-auth`?", not "tell me about architecture" -- the same
   specificity `AGENTS.md`'s "one node is one independently maintainable idea" rule
   assumes a node answers.
2. **Find the candidate node** the same way as Task 1 step 1-3: enumerate or grep the
   real tree, or run `explore` scoped to the corpus with the question itself.
3. **Read the node's front-matter `evidence[]` ledger before its body**, not after. Each
   entry states one claim, its class (`FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`), and the
   source(s) that back it -- the ledger is the map from the node's prose to what a
   reader can independently check, per `AGENTS.md`'s own *Evidence, citations, and what
   validation proves*.
4. **Open every cited source for the claim you actually care about**, not the whole
   ledger indiscriminately. A citation is a repository path, a commit, a URL, or a tool
   result; `AGENTS.md`'s citation-shape table states which of those a reader can open
   directly (a bare path or a path-with-line resolve on disk) and which are `UNVERIFIED`
   by construction (a commit, a graph edge, a tool result, most URLs) -- opening the
   underlying source yourself is what establishes the claim for you, not the node's
   `FACT` label alone. `AGENTS.md`'s own *Three things a passing run does not mean* is
   the fuller statement of why the label is not enough on its own.
5. **Follow `relationships[]` edges when the node's own claim is derived from another
   node**, not original to it -- a `depends-on` or `implements` edge (per
   `relationships.schema.json`) usually means the authority for part of what you are
   reading lives one hop away. A `references` edge is looser: supporting context, not a
   dependency, per that schema's own stated directionality.
6. **When the trail runs out at a node whose own claim is `TEAM_KNOWLEDGE` or an
   unopened citation**, that is the honest end of what the corpus currently establishes
   for your question -- not a defect in your traversal. Escalate or verify further
   yourself; do not treat the node's presence as having already done that.

## Task 3: Use RepoQL's tools, and do not confuse `concept:///` with the corpus

<!-- Only applies where RepoQL is available to the reader; the corpus is fully usable
     without it via `ls`/`grep`/`git ls-tree` as in Tasks 1-2 above. -->

1. **Use `explore`** for "what exists that's relevant to this" -- ranked by relevance to
   a stated question, with heading outlines, not exact-string matching. Scope it to the
   corpus (`uriGlob: "file:///launchpad/docs/corpus/**"`) to keep results inside the
   subject this node covers.
2. **Use `query`'s `glob_files(...)`** for an exact enumeration of the tree, the same
   role as `ls`/`git ls-tree` above but queryable and joinable with other RepoQL data.
3. **Use `read` for a specific file, symbol, or line range once you already know what
   you want** -- it is the tool that opens a cited source for you. At the time this node
   was authored, `read` (and `query`'s `search()` function) returned a fatal database
   error in this same repository's RepoQL instance after `explore` and a plain
   `glob_files()` listing had already succeeded in the identical session -- see the
   evidence ledger above for the exact errors. Treat that as a live-instance condition to
   check for, not a permanent property of the tool: if `read` or `search` fail, `explore`
   and `glob_files()` may still work, and `ls`/`grep`/`git ls-tree` always do.
4. **Do not read `concept:///` as part of this corpus.** RepoQL's own `concept:///`
   scheme resolves against a separate repo-memory store, backed in this repository by
   `.repoql/concepts/<category>/<subcategory?>/<Name>.md` (confirmed by listing
   `concept:///**` in this same session) -- CamelCase filenames under category folders
   (`rule/`, `knowledge/`), governed by RepoQL's own capture-and-verification mechanics,
   not by `node.schema.json` or `validate.py`. A corpus node's id is kebab-case and lives
   under `launchpad/docs/corpus/`; a concept capsule's name is CamelCase and lives under
   `.repoql/concepts/`. The vocabulary overlap ("node", "concept") is coincidental
   between the two systems, not a shared identity.

## See also

- `launchpad/docs/corpus/AGENTS.md` -- creating, updating, and retiring a node, and the
  full evidence/citation contract this node's Task 2 walks a reader through using.
- `launchpad/docs/corpus/agents/invariants.md` -- the MUST/SHOULD invariants a node must
  satisfy, referenced here only for the *type* reasoning it shares with this node.
- `launchpad/docs/corpus/standards/linking.md` -- how a node's own body should point at
  other material; this node's own body follows its bare-path, no-anchor, italicized-
  heading conventions throughout.

## Boundary

This node does not describe:
- The wider Buzz repository's directory/file layout (`crates/`, `desktop/`, `mobile/`,
  and so on) -- a plausible reading of sibling task `#650`
  (`agents/repository-navigation.md`)'s title, drawn here only to state the boundary
  explicitly rather than silently overlap it, since `#650` is unbuilt and its actual
  content is unread.
- How to create, update, or retire a corpus node -- `AGENTS.md` owns that procedure in
  full; this node only walks the reading/searching side.
- The MUST/SHOULD invariants a node's front matter and evidence must satisfy --
  `agents/invariants.md` owns that.
- A full reference-style catalogue of every RepoQL tool, verb, or `read` modifier -- that
  would drift into `templates/reference.md`'s form; *Task 3* above names only what this
  node's author actually exercised and observed, not an exhaustive tool reference.
- What to do when two authoritative sources conflict, or how to resolve which node a
  half-answered question belongs to -- both are separate sibling tasks (`#643`
  conflicting-evidence, `#642` concept-resolution) under Feature #620, unbuilt at this
  node's authoring time.

## Relationships

**Declared:** `depends-on: corpus-agents` -- this node's authority for what a corpus
node is, what its evidence ledger means, and what a passing `validate.py` run does and
does not establish is entirely derived from `AGENTS.md`, not original to this node, the
same relationship `agents-invariants` declares toward the same target for the same
reason. `implements: corpus-template-procedure` -- this node is a How-to-shaped instance
of that template: two task sequences (Task 1, Task 2) built from the reader's real
goals, plus a bounded tooling note (Task 3) rather than a full reference catalogue, per
that template's own boundary against `templates/reference.md`.

**Checked and not declared:** the real `origin/launchpad` corpus tree at this node's
recorded revision (see the evidence ledger above) carries no other node whose subject is
reader-facing corpus usage. `agents/invariants.md` is not targeted with `references`
beyond the `depends-on` edge already declared, because this node's body does not depend
on any specific invariant (I1-I10) stated there -- only on the shared *type* reasoning,
which is prose context, not a load-bearing dependency. No edge to `#650`
(`agents/repository-navigation.md`) or any other sibling `agents/*.md` / `ingestion/*.md`
task: none are merged on `origin/launchpad` at this node's recorded revision, so none is
a valid `relationships[].target`.

## Scope and omissions

**This node covers** how a reader -- agent or human -- checks whether a subject is
already covered by an existing corpus node before creating a new one, and how to
traverse from a stated question to a candidate node and from there to the sources that
actually back its claims; and, as directly observed in this same authoring session, what
RepoQL's `explore`, `query`, and `read` tools do (and, at the time of writing, did not
do) with this corpus, and how RepoQL's own `concept:///` scheme is a separate system
from a `launchpad/docs/corpus/` node despite overlapping vocabulary.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Creating, updating, and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The MUST/SHOULD invariants a node must satisfy | `launchpad/docs/corpus/agents/invariants.md` |
| Body-prose linking conventions (followed here, not restated) | `launchpad/docs/corpus/standards/linking.md` |
| The wider repository's directory/file layout, if that is `#650`'s actual scope | `#650` (`agents/repository-navigation.md`), unbuilt at this node's authoring time |
| Resolving conflicting evidence between sources | `#643` (`agents/conflicting-evidence.md`), unbuilt |
| Deciding whether two candidate subjects are one concept or two | `#642` (`agents/concept-resolution.md`), unbuilt |
| An exhaustive reference catalogue of every RepoQL tool/verb/modifier | No corpus template task currently owns this; out of scope per this node's own *Boundary* above |

**Expected but not verified when this node was written:**

- **Whether RepoQL's `read` and `search()` failures observed above were transient
  host-resource exhaustion or a reproducible limitation** was not established -- no
  `host restart` was issued from this authoring task, and the failure was recorded as an
  observed condition at a timestamp, not diagnosed further.
- **Whether sibling `#650`'s eventual content actually is "wider-repository navigation"
  as this node's *Boundary* section guesses from its title alone** is unverified; the
  first of the two nodes to be read by the other's author is the moment to reconcile
  the boundary if the guess was wrong.
- **No reader has yet followed Task 1 or Task 2 end-to-end against a real, previously
  unseen question** to confirm the steps above are sufficient in practice, as opposed to
  internally consistent on paper -- the same caveat `templates/procedure.md` itself
  states for its own required sections before any instance node existed.
