---
id: agents-repository-navigation
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
  - statement: "CLAUDE.md's 'Repo Structure' section (lines 56-94) enumerates every crates/* workspace member with a one-line purpose (for example buzz-db as 'Postgres event store and data access layer'), plus the desktop/, web/, mobile/, migrations/, and scripts/ top-level trees -- the map an agent should start from rather than guessing which crate owns a subject."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:56-94"
  - statement: "git grep -n descendant_count -- crates/ returns exactly three files: crates/buzz-core/src/kind.rs:434 (a doc comment on KIND_THREAD_SUMMARY describing the field as part of a thread-summary overlay's content), crates/buzz-db/src/store/thread.rs (multiple lines), and crates/buzz-db/src/store/event.rs:931 and :1309 (two inlined update sites) -- one grep, three files, two crates."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:434"
      - "crates/buzz-db/src/store/thread.rs:229"
      - "crates/buzz-db/src/store/event.rs:931"
      - "crates/buzz-db/src/store/event.rs:1309"
  - statement: "crates/buzz-db/src/store/thread.rs defines increment_reply_count (line 256) and decrement_reply_count (line 297) as free functions that update the thread_metadata.descendant_count column, and separately defines a second decrement_reply_count (line 1138) as a thin wrapper method on a store struct, annotated #[datastore_span(name = \"decrement_reply_count\", ...)], that only calls the free function at line 297 -- grepping the name alone surfaces two definitions, and only one holds the real update logic."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:256"
      - "crates/buzz-db/src/store/thread.rs:297"
      - "crates/buzz-db/src/store/thread.rs:1138"
  - statement: "crates/buzz-db/src/store/event.rs also updates descendant_count directly, inlined in two other code paths (a deletion-path decrement at line 931, an insert-time increment at line 1309) rather than calling the standalone functions in thread.rs -- the same counter is touched from at least three separate call sites in the same crate, not one centralized function."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:921-935"
      - "crates/buzz-db/src/store/event.rs:1300-1312"
  - statement: "migrations/0001_initial_schema.sql:523 defines the descendant_count column (INT NOT NULL DEFAULT 0) on the table thread.rs's queries update -- the schema-level source of truth behind every code-level reference grep finds."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:523"
  - statement: "crates/buzz-db/src/store/thread.rs carries its own #[cfg(test)] mod tests block (opening at line 1155) with ten #[tokio::test] functions in the same file, rather than in a sibling crates/buzz-db/tests/ directory -- confirmed separately by grep -rln descendant_count across crates/buzz-db/tests/ and crates/buzz-test-client/tests/, which returned no matches, meaning this counter's coverage would be invisible to a search of only the repository's dedicated tests/ directories."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:1155"
      - "git_grep(pattern='descendant_count', pathspec='crates/buzz-db/tests/;crates/buzz-test-client/tests/') -> no matches"
  - statement: "git log --oneline -- crates/buzz-db/src/store/thread.rs returns exactly one commit (a3730784f), while git log --follow --oneline on the identical path returns fifteen commits reaching back to crates/sprout-db/src/thread.rs -- the plain form silently stops at the file's most recent rename, and the discrepancy is only visible by running both and comparing counts."
    entry_class: FACT
    evidence:
      - "git_log(pathspec='crates/buzz-db/src/store/thread.rs', follow=false) -> 1 commit (a3730784f)"
      - "git_log(pathspec='crates/buzz-db/src/store/thread.rs', follow=true) -> 15 commits, oldest 3e7c9d900"
  - statement: "git log --oneline --diff-filter=R --follow on the same path isolates exactly the two commits that renamed the file: d99ad131f ('refactor: rename sprout backend to buzz', #958) and a3730784f ('refactor(db): extract domain stores from database runtime', #6987) -- naming when and under which PR the file moved, not just that history continues further back."
    entry_class: FACT
    evidence:
      - "git_log(pathspec='crates/buzz-db/src/store/thread.rs', diff_filter='R', follow=true) -> d99ad131f, a3730784f"
  - statement: "git blame -L 275,282 -- crates/buzz-db/src/store/thread.rs attributes seven of those eight lines to commit 3e7c9d900, naming the file at that commit as crates/sprout-db/src/thread.rs, and the eighth (line 282) to a later commit, 14fba21e57, naming the file at that point as crates/buzz-db/src/thread.rs -- a third, intermediate path, distinct from both the original crates/sprout-db/src/thread.rs and the file's current crates/buzz-db/src/store/thread.rs; a single blame call can therefore surface more than one historical path in one range, not just the oldest one, without needing --follow on log first."
    entry_class: FACT
    evidence:
      - "git_blame(pathspec='crates/buzz-db/src/store/thread.rs', range='275,282') -> lines 275-281: 3e7c9d900 crates/sprout-db/src/thread.rs; line 282: 14fba21e57 crates/buzz-db/src/thread.rs"
  - statement: "The doc comment at crates/buzz-core/src/kind.rs:432 points a reader to docs/bridge-channel-window.md for further detail on channel-window overlays; that file exists in the repository (confirmed by test -f), but the pointer itself is unchecked prose -- nothing but reading the comment and then independently confirming the file establishes that the pointer is live."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:430-432"
      - "docs/bridge-channel-window.md"
  - statement: "git grep -n \"function resetCommunityState\" -- desktop/src/ locates the definition at desktop/src/features/communities/useCommunityInit.ts:54, the same symbol CLAUDE.md's 'Community Switching' section names -- the identical grep technique used against Rust above works unchanged against TypeScript, because git grep is a text search over the working tree, not a language-aware index."
    entry_class: FACT
    evidence:
      - "desktop/src/features/communities/useCommunityInit.ts:54"
  - statement: "At this node's authoring time, mcp__repoql__explore and mcp__repoql__query, each scoped to crates/**, both failed with 'DuckDB failed during read-only query ... The database was invalidated by an earlier fatal failure'; a repeated query call failed identically, and command(command='host status') reported an active sweep (1,364,921 dirty of 1,369,330 total files, 24 failed) rather than a settled index -- a live-instance condition observed and cited honestly, not retried past or smoothed over. No host restart was issued from this task, since that is a shared side-effect outside this document's scope."
    entry_class: FACT
    evidence:
      - "mcp__repoql__explore(keywords='descendant_count reply_count thread counters materialize', uriGlob='file:///crates/**') -> DuckDB failed during read-only query ... database was invalidated by an earlier fatal failure"
      - "mcp__repoql__query(sql=\"SELECT uri FROM glob_files('crates/buzz-db/src/store/thread.rs') LIMIT 5;\") -> DuckDB failed during read-only query ... database was invalidated by an earlier fatal failure"
      - "mcp__repoql__command(command='host status') -> Files: 13494 complete, 12917 indexed, 1023074 embedded, 24 failed of 1369330 total; In flight: 0 active, 1364921 dirty, 319821 discovered"
  - statement: "A fresh git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run for this task rather than copied from an earlier count, shows the merged corpus tree already includes capabilities/**, layers/**, and development/** (four files: build.md, debugging.md, hermit.md, prerequisites.md) in addition to AGENTS.md, README.md, agents/invariants.md, architecture/**, schema/** (excluded from validation), standards/*.md, and templates/*.md; none of the four development/*.md nodes documents navigating the repository to gather authoring evidence (they cover running cargo build, reading relay logs, activating Hermit, and prerequisite tooling versions, confirmed by opening each), and none of the other 30 sibling agents/*.md or ingestion/*.md tasks under Feature #620 is present, so none is a valid relationships[] target for this node."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, agents/invariants.md, architecture/**, capabilities/**, development/build.md, development/debugging.md, development/hermit.md, development/prerequisites.md, layers/**, schema/** (excluded), standards/*.md, templates/*.md"
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "This node's type is agent rather than governance or development, on the same reasoning agents-invariants and agents-corpus-usage give for their own type: its subject is the same corpus surface AGENTS.md itself documents (what an agent must do before drafting a claim), not the standards/templates governance family, and not a development/*.md node about running or debugging the product itself."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/agents/invariants.md"
    confidence: 0.8
  - statement: "Sibling #644 (agents/corpus-usage.md), a local commit on an unmerged worktree branch as of this writing, states its own subject as finding and traversing coverage within launchpad/docs/corpus/ itself, and states this node's subject (drawn only from #650's title, since #644 could not read this node's actual content) as the wider repository's directory/file layout -- read directly from #644's worktree file to draw this node's boundary against it, not merely from #644's title."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#644 (unmerged local commit, __worktrees/task-644-agents-corpus-usage, read directly)"
  - statement: "Parent Feature #620's acceptance criteria require 'concrete source start points named' and that 'an independent developer/agent can answer a representative question in this feature area by traversing corpus nodes to implementation and verification evidence' -- this node is built to satisfy that traversal criterion for the wider repository directly, rather than against issue #650's own copied-over Definition of Done tail alone."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 acceptance criteria"
  - statement: "Issue #650's own Definition of Done asks that the document 'states goal, prerequisites and allowed environment/scope', 'provides ordered steps that are executable and project-specific', 'defines success verification and rollback/cleanup where relevant', and 'links authoritative commands/config rather than giving generic advice' -- how-to-shaped boilerplate matching templates/procedure.md's own form, not the policy-shaped boilerplate on other sibling tasks."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#650 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-procedure
---

# Navigating the repository: how-to

How an agent locates the source paths, symbols, tests, migrations, and configuration inside
the wider Buzz repository -- `crates/`, `desktop/`, `web/`, `mobile/`, `migrations/`,
`launchpad/`, and the rest -- that it must open and cite as evidence before making a corpus
claim. This is the search half of `AGENTS.md`'s own "Creating a node" step 3 ("Record what you
inspected, before drafting"), demonstrated on real symbols in this same repository rather than
described abstractly. It is not about searching `launchpad/docs/corpus/` itself; that is
`agents/corpus-usage.md`'s subject (see *Boundary* below).

## Before you start

- Know the crate/directory map. `CLAUDE.md`'s "Repo Structure" section names every
  `crates/*` workspace member with a one-line purpose, plus the `desktop/`, `web/`, `mobile/`,
  `migrations/`, and `scripts/` top-level trees. Start there rather than guessing which of the
  repository's 30 top-level `crates/*` directories owns a subject.
- Know `AGENTS.md`'s "Creating a node" step 3: a source you inspect must end up cited on the
  claim it supports. A path you read but cite nowhere is either a missing claim in your draft or
  a note you no longer need.
- Know that a bare repository path or `path:line` is the citation shape `validate.py` actually
  resolves against the filesystem (`AGENTS.md`'s citation-shape table) -- the navigation
  practiced here is what produces that citation, not a substitute for it.

## Task 1: Trace a symbol or concept to every place it matters

1. Start from the crate or top-level directory that plausibly owns the subject, using
   `CLAUDE.md`'s Repo Structure map rather than guessing -- for example, thread/reply behavior
   points at `buzz-db`, described there as "Postgres event store and data access layer."
2. Run `git grep -n <term> -- <scope>`, scoped to that crate first and widened to the whole
   repository if the owner is unclear. This is a plain text search, not a language-aware index,
   so it matches a doc comment, a SQL string, and a function body identically -- for example,
   `git grep -n descendant_count -- crates/` surfaces a hit in a Rust doc comment
   (`crates/buzz-core/src/kind.rs:434`) and hits inside two different files of a second crate
   (`crates/buzz-db/src/store/thread.rs`, `crates/buzz-db/src/store/event.rs`) from one command.
3. Expect more than one definition and read each before deciding which is the real logic. Grepping
   `decrement_reply_count` in `thread.rs` alone returns both the free function that runs the
   actual `UPDATE` query (line 297) and a thin wrapper method on a store struct (line 1138,
   annotated `#[datastore_span(...)]`) that only calls the free function -- citing the wrapper as
   if it were the update logic would misattribute the claim.
4. Check the schema and migration layer separately from the code. A field name in Rust does not
   always share exactly one `grep` hit with its Postgres column: `descendant_count`'s column
   definition lives in `migrations/0001_initial_schema.sql:523`, a file `git grep -- crates/`
   never reaches because it is outside that scope.
5. Check whether the surrounding module's tests live beside the code or in a sibling `tests/`
   directory before concluding a claim is untested. `crates/buzz-db/src/store/thread.rs` carries
   its own `#[cfg(test)] mod tests` (opening at line 1155, ten `#[tokio::test]` functions) in the
   same file; a search scoped only to `crates/buzz-db/tests/` or `crates/buzz-test-client/tests/`
   for the same term returns nothing, which would wrongly read as "no test coverage" rather than
   "coverage is inline."
6. Follow a comment's pointer to another file only after independently confirming the target
   exists (`test -f`, or `git grep -l` for the filename) -- a comment is prose, not a checked
   link. The doc comment at `crates/buzz-core/src/kind.rs:430-432` names
   `docs/bridge-channel-window.md`; that file does exist, but nothing checked that automatically,
   and a stale or typo'd pointer would read identically until opened.

## Task 2: Read a symbol's real history through a rename

1. Run `git log --oneline -- <path>` first. It is cheap, but it silently stops at the file's most
   recent rename rather than erroring or warning.
2. Run `git log --follow --oneline -- <path>` and compare the count against step 1 before trusting
   either number alone. For `crates/buzz-db/src/store/thread.rs`, the plain form returns exactly
   one commit; the `--follow` form returns fifteen, reaching back to a file that no longer exists
   at that path.
3. When the counts differ, run `git log --oneline --diff-filter=R --follow -- <path>` to isolate
   the rename commits themselves -- for this file, exactly two: `d99ad131f` ("refactor: rename
   sprout backend to buzz", #958) and `a3730784f` ("refactor(db): extract domain stores from
   database runtime", #6987). This names *when* and under *which PR* the file moved, which the
   full `--follow` log alone does not make obvious among fifteen entries.
4. Use `git blame -L <range> -- <path>` for line-level attribution once the current logic is
   located. Blame's own output can still name a historical path, and more than one within the
   same range: attributing `crates/buzz-db/src/store/thread.rs:275-282` shows seven of those
   eight lines as commit `3e7c9d900`, naming the file at that point as
   `crates/sprout-db/src/thread.rs` -- the original, pre-rename path -- while the eighth line
   attributes to a later commit naming a third, intermediate path,
   `crates/buzz-db/src/thread.rs`. Read the whole range's output, not just its first line, before
   concluding a chunk has one uniform history.

## Task 3: Prefer RepoQL when it is reachable; fall back to `git` when it is not

- When reachable, RepoQL's `explore` (ranked relevance across a glob) and `query`'s
  `glob_files(...)`/`search(...)` (exact enumeration, joinable SQL) can answer "what exists
  relevant to this" faster than an unscoped `git grep`, and `read` can retrieve a specific
  symbol's body directly by URI.
- At this node's authoring time, both `mcp__repoql__explore` and `mcp__repoql__query`, scoped to
  `crates/**`, failed with a fatal DuckDB error ("the database was invalidated by an earlier
  fatal failure"), confirmed non-transient by a second failed `query` call and by
  `command(command="host status")` reporting an active sweep rather than a settled index. Treat
  this as a live-instance condition to check for -- run one cheap call first and fall back to
  `git grep`/`git log`/`git blame` if it errors -- not as a permanent property of the tool. The
  sibling `agents/corpus-usage.md` node independently hit the identical failure mode on a
  different occasion, scoped to the corpus rather than to `crates/**`, for whatever that
  corroboration is worth.
- The `git`-based techniques in Tasks 1-2 always work, need no host, and are this node's
  fallback of first resort precisely because they were the only technique available when this
  node was authored.

## See also

- `launchpad/docs/corpus/AGENTS.md` -- what to do with what this node helps you find: cite it on
  an `evidence` entry, classify `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` honestly, and never promote an
  unopened source to `FACT`.
- `launchpad/docs/corpus/agents/invariants.md` -- the MUST/SHOULD rules the resulting evidence
  ledger must satisfy once the sources this node helped locate are cited.
- `agents/corpus-usage.md` (unmerged as of this writing) -- the corpus-internal counterpart:
  finding whether a subject is already covered inside `launchpad/docs/corpus/` itself, and
  traversing a question to a node's cited evidence once you already have a candidate node.

## Boundary

This node does not describe:

- **Finding or traversing coverage within `launchpad/docs/corpus/` itself.** That is
  `agents/corpus-usage.md`'s subject, read directly from its (unmerged) worktree file for this
  boundary rather than guessed from its title.
- **Creating, updating, or retiring a corpus node**, or what a node's front matter must contain.
  `AGENTS.md` and `node.schema.json` own that in full; this node only helps an author find the
  sources a node's `evidence` entries then cite.
- **The MUST/SHOULD invariants a node's evidence ledger and body must satisfy.**
  `agents/invariants.md` owns that.
- **Running or debugging the product itself** (building with `cargo build`, reading relay logs,
  activating Hermit, prerequisite tooling versions) -- that is `development/build.md`,
  `development/debugging.md`, `development/hermit.md`, and `development/prerequisites.md`, all
  already merged and none of which overlaps this node's subject of navigating the repository to
  gather *authoring evidence*, confirmed by opening each.
- **A full reference catalogue of every RepoQL verb, `read` modifier, or every crate in
  `crates/`.** The worked examples above demonstrate the technique on real symbols; no
  reference-shaped node for this Feature exists to hold a complete catalogue, and building one
  here would drift into `templates/reference.md`'s form per `templates/procedure.md`'s own
  warning against reference-style completeness inside a how-to.
- **Acquiring the underlying skill of reading Rust, TypeScript, SQL, or Dart from scratch.** That
  is a tutorial, a Diátaxis form `templates/procedure.md` states no corpus template currently
  covers; this node assumes an already-competent reader, per that template's own industry model.

## Relationships

**Declared:** `depends-on: corpus-agents` -- this node's authority for *why* an inspected source
must end up cited on the claim it supports, and for what a `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`
classification means once a source is found, is entirely `AGENTS.md`'s, not original to this
node -- the same relationship `agents/corpus-usage.md` declares toward the same target for the
same reason. `implements: corpus-template-procedure` -- this node is a How-to-shaped instance of
that template (three task sequences built from an author's real goals, a bounded Task 3 rather
than a full tool reference), per that template's own "should declare `implements`" guidance.

**Checked and not declared:** the real `origin/launchpad` corpus tree at this node's recorded
revision (see the `git_ls_tree` evidence entry above) includes `development/build.md`,
`development/debugging.md`, `development/hermit.md`, and `development/prerequisites.md`; none
was targeted with `references`, `depends-on`, or `part-of` because none documents navigating the
repository to gather authoring evidence -- opened and confirmed, not assumed from their
directory name. `agents/invariants.md` is not targeted beyond the shared *type* reasoning already
cited above, because this node's body does not depend on any specific MUST/SHOULD invariant
stated there. No edge to `#644` (`agents/corpus-usage.md`) or any other sibling `agents/*.md` /
`ingestion/*.md` task under Feature #620: none is merged on `origin/launchpad` at this node's
recorded revision (confirmed by the same `git_ls_tree` run), so none is a valid
`relationships[].target`.

## Scope and omissions

**This node covers** how an agent locates the source paths, symbols, tests, migrations, and
configuration in the wider Buzz repository that a corpus claim needs to cite: tracing a symbol
or concept across files and crates with `git grep`, distinguishing a real implementation from a
delegating wrapper once more than one definition surfaces, checking the schema/migration layer
and the test layer separately from the code that references them, reading a symbol's full
history through a file rename with `git log --follow` and `--diff-filter=R` and `git blame`, and
when to prefer RepoQL's `explore`/`query`/`read` over `git`-based search versus when to fall back.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Finding/traversing coverage within `launchpad/docs/corpus/` itself | `agents/corpus-usage.md` (unmerged) |
| Creating, updating, and retiring a corpus node | `launchpad/docs/corpus/AGENTS.md` |
| The MUST/SHOULD invariants a node's evidence must satisfy | `launchpad/docs/corpus/agents/invariants.md` |
| Running or debugging the product itself (build, logs, Hermit, prerequisites) | `launchpad/docs/corpus/development/{build,debugging,hermit,prerequisites}.md` |
| A complete reference catalogue of every RepoQL verb or `read` modifier | No corpus template task currently owns this; out of scope per this node's own *Boundary* above |
| Resolving conflicting evidence found via two different navigation paths | `#643` (`agents/conflicting-evidence.md`), unbuilt at this node's authoring time |

**Expected but not verified when this node was written:**

- **Whether the RepoQL `explore`/`query` failures observed above were transient host-resource
  exhaustion or a reproducible limitation** was not established -- no `host restart` was issued
  from this task, and the failure was recorded as an observed condition at a timestamp, not
  diagnosed further.
- **Whether sibling `#644`'s eventual merged text draws the corpus-usage/repository-navigation
  boundary identically to how this node draws it from its own side** was checked against `#644`'s
  current local-commit content, not against a merged, possibly-revised version -- neither node
  had merged as of this writing.
- **No reader has yet followed Task 1 or Task 2 end-to-end against a real, previously unseen
  navigation question** to confirm the steps above are sufficient in practice rather than merely
  internally consistent against the one worked example (`descendant_count` /
  `thread.rs`) used throughout this node.
