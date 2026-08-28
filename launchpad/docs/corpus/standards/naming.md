---
id: corpus-standard-naming
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
  - statement: "At the recorded revision, every document under launchpad/docs/corpus/ (schema/ excluded) has a lowercase kebab-case filename with a .md extension, except AGENTS.md and README.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "The agent harness's governing-instructions resolution matches an ancestor rules file by exact, case-sensitive string membership against RULES_FILENAMES = (\"AGENTS.md\", \"CLAUDE.md\"), so a differently-cased filename would not resolve as the nearest AGENTS.md."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/preflight_core.py"
  - statement: "AGENTS.md's own front matter states that this file is also resolved as the nearest AGENTS.md for every change under launchpad/docs/corpus, so it is read as governing instructions and not only as a corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Every node's id observed at the recorded revision is 'corpus-' followed by the lowercased filename stem, with a singular category word inserted for a document living one level below the corpus root in a purpose-named subdirectory: corpus-agents for AGENTS.md, corpus-readme for README.md, corpus-standard-confidence for standards/confidence.md, and corpus-standard-decision-references for standards/decision-references.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "Neither document under standards/ repeats the word 'standard' in its filename, even though each one's id inserts 'standard-' before the filename stem."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "validate.py never compares a node's id field to its filename or file stem anywhere in load_nodes, find_duplicate_ids, or find_unresolved_relationship_targets."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's node discovery matches files with the literal, case-sensitive glob *.md, and its ownership check compares a path's suffix to the exact string '.md'; neither inspects whether the filename stem is kebab-case, so a schema-valid node saved under any other filename shape validates identically to a kebab-case one."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py never reads a node's Markdown body past the front-matter block: _load_frontmatter splits the document at the second '---' delimiter and only the region before it is parsed, so no check exists for a body's heading, its position, or its count."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Each of the four documents at the recorded revision -- AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md -- opens its body with exactly one level-1 Markdown heading as the first line after the front matter's closing delimiter."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "AGENTS.md's front matter defines the node's evidence array in prose as 'the node's provenance ledger', with no separate provenance field, and every later mention in that document shortens it to 'the ledger'; confidence.md's Scope and authority section instead names the identical array 'a corpus node's evidence ledger'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/standards/confidence.md"
  - statement: "Corpus prose spells the YAML front-matter block 'front matter' (two words) in the majority of its occurrences across AGENTS.md, README.md and both standards documents, uses the hyphenated 'front-matter' in those same documents only as a compound adjective directly before a noun, and the schema/ subtree -- which validate.py excludes from corpus content -- instead spells it 'frontmatter', one word, throughout node.schema.json and schema/README.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "A title read on its own, without its sibling documents for context, names its subject more reliably when it states the reader's task or question -- as standards/decision-references.md's 'Citing a decision' does -- than when it mechanically restates the node's id or filename, as standards/confidence.md's 'Standard: `confidence`' does."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
    confidence: 0.6
  - statement: "Issue #1319 requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1319 definition of done"
  - statement: "Issue #1319 scopes 'naming' to how corpus documents are named -- filenames under launchpad/docs/corpus/, document titles, and cross-document terminology -- and explicitly excludes the id field's own contract (#1317) and code-level naming conventions elsewhere in the repository."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1319 issue body, dispatch-time note on subject matter and overlap risk"
relationships:
  - type: references
    target: corpus-agents
---

# Naming a corpus document

How to name a corpus document itself: its file location and filename, how its `id`
should read against that filename, its title, and the terms it uses for concepts the
corpus already has a name for. Not the `id` field's own contract, and not code-level
naming elsewhere in this repository.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| The `id` field's own contract -- pattern, permanence, uniqueness | `launchpad/docs/corpus/schema/node.schema.json`, and the identifiers standard (#1317, unlanded at the recorded revision) |
| Creating, updating and retiring a node, and the id-choice step this document does not restate | `launchpad/docs/corpus/AGENTS.md` |
| The front-matter contract in full | `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/schema/README.md` |
| Why Markdown with front matter is canonical, and why the corpus is reviewed as a PR diff | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |

If this file and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Scope and authority

**This standard governs** three things about a corpus document, and nothing about
what the document says:

1. Where its file lives and what its filename is.
2. How its `id` reads against that filename, and how its title reads on its own.
3. Which spelling or phrasing a corpus document uses for a concept the corpus
   already has a name for.

**It does not govern the `id` field's own contract.** The kebab-case pattern, the
rule that an `id` is permanent once assigned, and how uniqueness is enforced belong
to `node.schema.json` today and to the identifiers standard once it lands (#1319's
own issue body names this boundary explicitly, because a past batch already
produced overlapping documents that argued over which one owned a rule -- see
issues #1476 and #1481). What this standard adds is narrower: given a filename, what
`id` a reader should expect, and given an `id`, what filename a reader should expect
-- the correspondence, not the shape.

**It does not govern naming in the rest of this repository.** Tailwind token names,
Nostr event-kind names, Rust module names and every other product-code convention
are out of scope; this node is about how corpus *documents* -- the things under
`launchpad/docs/corpus/` -- name themselves.

**Its authority is derived, not original**, in the same way `corpus-standard-confidence`
and `corpus-standard-decision-references` state theirs: `node.schema.json` already
enforces the `id` pattern and `validate.py` already enforces the `.md`-only,
`schema/`-excluded corpus boundary. This document does not create or relax either.
What it adds -- filename shape, filename-to-id correspondence, title convention, and
term reuse -- is enforced by review, because nothing in the current tooling reaches
it (see *Enforcement, and where it stops*).

## MUST

These bind every corpus document created or substantially retitled from this
standard's merge onward. They do not require rewriting an existing document to
comply; see *Scope and omissions* for what that would mean and why it is
deliberately not asked for here.

1. **A filename MUST be lowercase kebab-case with a `.md` extension**
   (`^[a-z0-9]+(-[a-z0-9]+)*\.md$`), with exactly two standing exceptions:
   `AGENTS.md` and `README.md`. `AGENTS.md`'s exact casing is load-bearing, not
   stylistic -- the agent harness resolves an ancestor rules file by exact,
   case-sensitive string membership against a fixed filename tuple, so a
   lowercase `agents.md` would silently stop being read as governing instructions
   for every change under this directory. `README.md` is named for the corpus's
   paired human-facing entry point, alongside `AGENTS.md`, per `AGENTS.md`'s own
   gap table. A third exception is not ruled out, but it needs the same kind of
   external constraint and MUST be justified in the new node's own evidence
   ledger, not asserted by convention.
2. **A filename MUST NOT re-encode its own directory as a prefix or suffix.**
   Both documents under `standards/` omit the word "standard" from their
   filenames even though it appears in their `id`s -- the directory already says
   what kind of document this is; repeating that in the filename is redundant
   with the path a reader is already standing in.
3. **A document's `id` MUST be recognizable, on sight, as the filename.**
   Concretely, at the recorded revision this means: strip `.md`, lowercase the
   stem, prefix with `corpus-`, and -- for a document one level below the corpus
   root inside a purpose-named subdirectory -- insert that subdirectory's
   singular form before the stem. `standards/naming.md` therefore takes
   `corpus-standard-naming`, matching the two precedents this document was
   written against. This MUST constrains the *correspondence* only. It does not
   restate or extend the `id` field's character-level contract (that pattern is
   `node.schema.json`'s, and its full standard is #1317's); a document that
   picked an unrecognizable `id` still fails this MUST even if the string
   happens to satisfy the schema's regex.
4. **A document's body MUST open with exactly one level-1 (`#`) heading**, as the
   first line after the front matter's closing `---`, and MUST NOT contain a
   second level-1 heading anywhere else in the body. `validate.py` never reads a
   node's body at all -- it discards everything after the front matter's second
   delimiter -- so nothing but review holds this today.
5. **New or edited corpus prose MUST spell the YAML block "front matter"** (two
   words) as a noun, and **MUST NOT** use "frontmatter" (one word). The
   hyphenated "front-matter" is permitted only as a compound adjective directly
   before a noun ("front-matter contract", "front-matter key"), matching how
   `AGENTS.md`, `README.md` and both `standards/` documents already use it. This
   binds writing under `launchpad/docs/corpus/`; it does not require editing
   `schema/node.schema.json` or `schema/README.md`, which spell it "frontmatter"
   throughout and sit outside `validate.py`'s corpus-content boundary -- see
   *Scope and omissions* for that gap.
6. **New or edited corpus prose MUST call the node's `evidence` array its
   "provenance ledger"**, matching the term `AGENTS.md` defines it under ("the
   node's provenance ledger -- there is no separate provenance field"), and MUST
   NOT introduce a new synonym for it. `corpus-standard-confidence` already uses
   "evidence ledger" for the same array; that is a pre-existing document this
   task does not edit (see *Scope and omissions*), and this MUST governs writing
   from here forward, not a retroactive rename.

## SHOULD

Depart from these with a stated reason; nothing enforces them but review.

- **Title the document by what a reader is trying to do or find, not by
  mechanically restating its `id` or filename.** `standards/decision-references.md`'s
  "Citing a decision" reads on its own; `standards/confidence.md`'s
  "Standard: `confidence`" reads only once you already know the corpus calls
  every policy node a "standard." Both are already merged and both are
  legitimate precedent -- this is guidance for the next title, not a verdict on
  either existing one.
- **Choose a filename stem a reader would grep for the concept**, not a phrase
  that only parses next to its neighbors. "naming.md" inside `standards/`, not
  "corpus-document-naming.md" -- the directory already supplies "corpus" and
  "standard" the way MUST 2 above holds it should.
- **When the subject already has a short name elsewhere in this repository** --
  an ADR's title, a PRD's title, a schema field's own name -- reuse it rather
  than inventing a new one. This is the same discipline `node.schema.json`
  itself follows when it reuses PRD #602's surface list and ADR-0003's origin
  vocabulary rather than inventing parallel ones.
- **When you notice two corpus documents already using different words for the
  same thing, name both in your new document's evidence rather than silently
  picking one.** Read the two "front matter" and "provenance ledger" evidence
  entries above for the shape this takes: state what each document says, cite
  both, and let a reviewer decide whether reconciling them belongs in your diff
  or in a separate one. Folding a rename of someone else's already-merged node
  into an unrelated change is exactly the "second hand-authored canonical
  document" this task's own out-of-scope list forbids.

## Enforcement, and where it stops

**Enforced mechanically, but only adjacently to naming:** `node.schema.json`
enforces the `id` field's kebab-case pattern through `validate.py`, and
`validate.py` separately enforces that every corpus file is `.md` (via case-sensitive
glob matching in `discover_markdown_files`) and that `schema/` is excluded from
corpus content. Neither of those checks is *about* naming as this document defines
it -- one constrains the `id` string in isolation, the other constrains the
extension and the directory boundary. Both stay true regardless of anything in this
document.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| Filename shape (kebab-case, no re-encoded directory) | A node saved as `NAMING.md`, `Naming_Doc.md`, or `standard-naming.md` inside `standards/` validates identically to one that follows MUST 1 and MUST 2. |
| Filename-to-`id` correspondence | `validate.py` never reads a node's path to compare it against its `id`; an `id` with no visible relationship to its filename passes cleanly, and duplicate-id detection (`find_duplicate_ids`) would not even notice two files converging on unrelated ids. |
| A single, first-line, singular H1 | `validate.py` discards the entire body after the front matter's closing delimiter; a missing heading, a second heading, or a heading buried mid-document is invisible to it. |
| Term reuse (MUST 5, MUST 6, and the SHOULD guidance) | Nothing in this repository lints corpus prose. Two documents can disagree about a term indefinitely, and a passing validation run says nothing about it -- this document's own evidence ledger shows two live examples that already do. |

The pattern is the same one `corpus-standard-confidence` names for its own field:
everything a schema can hold is held, and everything that requires reading prose is
not. A reviewer checking a new corpus document against this standard has to
actually open it next to the documents it should read like, the same way a
reviewer checking a decision citation has to open the decision.

## Exceptions and escalation

**There is no exception process for the two mechanically enforced rules** (the `id`
pattern, the `.md`/`schema/` boundary) -- they are `node.schema.json`'s and
`validate.py`'s to relax, not this document's, and doing so is a schema or validator
change under `launchpad/docs/corpus/schema/COMPATIBILITY.md`, not an exception here.

**A third filename exception beyond `AGENTS.md` and `README.md`** is not
categorically refused, but MUST 1 requires it to be justified the same way this
document justified the two it names: an external constraint, stated as a citation
in the new node's own evidence ledger, not asserted by convention or by analogy to
these two.

**A term or phrasing disagreement between two already-merged documents** is not
this document's to resolve by editing the other document -- that is a second
hand-authored canonical document, out of this task's scope, and out of scope for
whatever future change invokes this standard too, unless that change's own task is
specifically to fix the drift. Record the disagreement (per the SHOULD above) and
either file it or fix it in a change scoped to that purpose.

**Anything this document does not answer** escalates the way the rest of the corpus
does: an open question becomes a `type:task` (or `type:adr`, if it is genuinely a
decision) issue, argued and resolved by a human, not settled by precedent inside a
node's body.

## Scope and omissions

**This document covers** filename shape, the filename-to-`id` correspondence,
document titles, and reuse of existing corpus terminology, for documents under
`launchpad/docs/corpus/`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `id` field's own pattern, permanence and uniqueness contract | `launchpad/docs/corpus/schema/node.schema.json` today; the identifiers standard, #1317, unlanded at the recorded revision |
| The vocabulary and phrasing of MUST/SHOULD and other normative language itself | The normative-language standard, #1320, unlanded at the recorded revision |
| Naming and provenance for files under `generated/` | The generated-content standard, #1316, unlanded at the recorded revision |
| The front-matter field contract field-by-field | The front-matter standard, #1315, unlanded at the recorded revision |
| Link syntax and anchor conventions between corpus documents | The linking standard, #1318, unlanded at the recorded revision |
| The `type` enum's vocabulary and what surface each value names | The taxonomy standard, #1324, unlanded at the recorded revision |
| The overall shape every standards document should follow | The documentation standard, #1313 (see also the related decision, #1486), unlanded at the recorded revision |
| Retroactively reconciling "front matter"/"frontmatter" across `schema/` and the corpus proper, and "provenance ledger"/"evidence ledger" between `AGENTS.md` and `standards/confidence.md` | Not this task -- both are pre-existing documents this task does not edit; filed as [#1510](https://github.com/launchpad-26/buzz/issues/1510) |

**Why this document declares one relationship and not more.** At the recorded
revision, `origin/launchpad` carries exactly four corpus documents:
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`, and
`corpus-standard-decision-references` -- confirmed by
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` run
immediately before this front matter was finalized, not assumed from an earlier
check or from this worktree's own branch (which additionally carries an unmerged
`AGENTS.md` fix from `task/636-corpus-agents-md` that `origin/launchpad` does not
yet have). `corpus-agents` is the node this document cites most heavily and depends
on for its own procedural grounding, so a `references` edge to it resolves today and
is added. The other three siblings dispatched in this same batch --
generated-content, identifiers, normative-language, and status -- are not targeted:
none of them will exist on `launchpad` by the time this document merges, regardless
of what any of those branches' own worktrees show, per this task's own dispatch
instructions.

**Expected but not verified when this node was written**, per the rule in
*Creating a node* step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **Why `README.md`'s exact casing matters was not independently established here**,
  beyond it being the corpus's second observed non-kebab-case filename and the
  paired human-facing entry point `AGENTS.md` names. `corpus-readme`'s own ledger
  flags the identical gap about GitHub's directory-rendering behavior; this document
  does not close it either.
- **No corpus document was actually renamed or retitled against MUST 1 through 4**
  to confirm the rules are followable in practice rather than merely
  self-consistent with the four documents they were read from.
- **Whether a lint or CI check should eventually enforce any part of this standard**
  was not evaluated. Today every MUST here is review-only, and this document takes
  no position on whether that should change.
