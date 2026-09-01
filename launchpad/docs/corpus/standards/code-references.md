---
id: corpus-standard-code-references
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 60d4947b7145a6ef25f185b9c25d43e43d99de3c."
    entry_class: FACT
    evidence:
      - "commit 60d4947b7145a6ef25f185b9c25d43e43d99de3c"
  - statement: "A code reference lives in a node's frontmatter evidence array, because the schema requires that array, defines no other field for citations, and rejects any field beyond the seven it names."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A bare repository path is resolved on disk and must name a real file: a directory, a path that does not exist, and a path naming no file all fail. Resolution establishes only that the file is there; the file's contents are never read."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A repository path is resolved against the repository root rather than the citing document or the current working directory, and after resolution it must still lie inside the repository, so an absolute path and a path that escapes the tree are both rejected."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "In a path:line or path:start-end citation the path is checked exactly as a bare path is, and the line number is compared both against itself -- start at least 1, end not before start -- and against the length of the file, a position past the end being a hard error since #1459."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A GitHub repository file link is judged on syntax alone: the validator requires a full forty-character lowercase commit SHA and a non-empty path after it, and never contacts GitHub to establish that the named file exists."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A repository link is rejected when it is pinned to a mutable ref, when it names no file after the ref, and when its verb is tree, blame, commits or edit rather than blob or raw."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The requirement to pin a repository link to the full SHA and never to blob/main originates in ADR-0003's reference format."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0003-handbook-page-provenance-contract.md"
  - statement: "Graph edges, tool results no verifier covers, and external URLs on a default run are routed to an UNVERIFIED channel that prints and, under fail-closed validation, blocks the run. Commit references are no longer among them: a commit is resolved against the object store, verifying ok or failing hard. Tool results naming git or grep are routed to verifiers that may also fail hard."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation matching no recognised form is a hard error rather than an UNVERIFIED notice."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation that contains no whitespace and matches no other form falls through to the repository-path rule, so it is reported as a path that does not resolve rather than as an unrecognised form."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Citation checking is structural: a citation that resolves to a real file is never opened, so nothing compares that file against the statement the citation sits under."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The validator resolves a relationship target only against the ids carried by the Markdown files it discovers beneath the corpus root outside schema/, and an unmatched target is a hard error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "CONTRACT.md section 3 enumerates seven citation shapes -- symbol anchor, file range, file line, bare path, graph edge, tool result and commit -- and none of them is a URL."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "AGENTS.md presents a seven-row citation table and states explicitly that it is not a summary of CONTRACT.md section 3, because the two URL rows are forms validate.py recognises and section 3 does not enumerate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "AGENTS.md states that its citation-shape table is provisional and belongs in the evidence standard once that standard lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The same validator command that runs locally runs in CI on every pull request and on every push to launchpad that touches the corpus, and the just recipe wrapping it needs the Hermit environment activated first while the direct interpreter form does not."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
      - "Justfile"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Declaring an edge to corpus-agents would validate on this branch and become a hard error if this node merged ahead of the branch that introduces corpus-agents, so this node declares no relationships."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.9
  - statement: "A line number that is not checked against the length of the cited file is a known defect rather than intended behaviour."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1459 'bug: corpus validator accepts path:line citations whose line does not exist'"
  - statement: "This standard addresses developers as well as agents and reviewers, because a developer is one of the two authors the parent feature names."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 outcome: 'A developer or agent can create one atomic corpus node and deterministic validation accepts or rejects it against one documented contract.'"
  - statement: "Per Serina's decision on launchpad-26/buzz#1486, this node reconciles to #1313's documentation-standard: top-level sections are no longer numbered (G4), and internal cross-references that pointed at a section by its number now name the section instead."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1486, decided 2026-08-27"
---

# Standard: code references

How a corpus node points at code, what each reference form actually proves, and how a
reference stays honest once the code moves underneath it. Look up the rule you need;
this is reference material, not a tutorial.

## Scope and authority

**This node governs** every citation, in any node's `evidence` ledger, that names code
in a repository: which forms are permitted, which are forbidden, how they are pinned and
positioned, and what a passing validation run does and does not establish about them.

**Its authority is executable.** The rules below are not house style — each one is the
behaviour of `launchpad/project-intelligence/corpus/validate.py`, measured by running it,
and each MUST corresponds to a verdict that command returns today. Where this document
and that program disagree, **the program wins and this document has drifted.**
`launchpad/project-intelligence/CONTRACT.md` §3 supplies the vocabulary of shapes;
`launchpad/docs/corpus/schema/node.schema.json` supplies the field the citations live in.

**This node does not govern the ledger itself.** Which class a claim carries, how
conflicting evidence is ranked, and the forms that name tool output rather than code —
graph edges and tool results — belong to the evidence standard (#1314). `AGENTS.md` says
its own citation table is provisional and belongs there once it lands; this node claims
only the code-naming half of that table, and the two will need reconciling when #1314
arrives. That overlap is named here rather than silently resolved.

**Nothing here is a decision about ADR-0003's markdown-link format.** `_classify_url`
accepts a bare pinned URL and documents in its own docstring that requiring the markdown
wrapper on corpus evidence is #605's call, not the validator's. This node describes that
state and leaves it open.

## The forms, and what a pass proves

Seven shapes are enumerated in `CONTRACT.md` §3. Five of them can name code in this
repository; the validator additionally accepts a URL form that §3 does not enumerate at
all. Every verdict below was measured against `_classify_citation` at the revision this
node records.

Verdicts marked `deferred` are decided by the `--check-links` stage, which CI always runs;
they are reported and do not block the offline stage.

| Form | Example | Verdict | What the verdict establishes |
|---|---|---|---|
| Symbol anchor | `…kind.rs#symbol=is_shared_gated_kind` | `ok` | **The file exists and names that symbol**, matched on word boundaries. Not that it supports the claim. |
| Symbol anchor, symbol absent | `…kind.rs#symbol=renamed_away` | `error` | — the symbol does not appear in the cited file |
| Bare repository path | `Justfile` | `ok` | **The file exists.** The path was resolved and opened. |
| Bare path, directory | `launchpad` | `error` | — a directory is not a file |
| Bare path, absolute | `/etc/passwd` | `error` | — must be repo-relative |
| Bare path, escaping | `../buzz/Justfile` | `error` | — resolves outside the repository |
| Path with a line | `Justfile:1` | `ok` | **The file exists and is at least that long.** Not that the line says anything relevant. |
| Path with a line, out of range | `Justfile:999999` | `error` | — the position exceeds the file's length (#1459) |
| Path with a range, out of range | `Justfile:1-99999999` | `error` | — same bounds check applies to the range |
| Path with a malformed position | `Justfile:0`, `Justfile:5-1` | `error` | — the position is inconsistent with itself |
| Path with a column | `…kind.rs:219:5` | `error` | — not a supported form; see *Enforcement* for the misleading message |
| GitHub file link, pinned | `…/blob/<40-hex>/Justfile` | `deferred` → `ok` | Syntax offline; the link stage fetches it. |
| GitHub file link, pinned, target never existed | `…/blob/<40-hex>/does-not-exist.md` | `deferred` → `error` | The link stage does contact GitHub, and this fails there. |
| GitHub file link, mutable ref | `…/blob/main/Justfile` | `error` | — not pinned to a full SHA |
| GitHub file link, abbreviated or uppercase SHA | `…/blob/60d4947/…`, `…/blob/<40-HEX>/…` | `error` | — the SHA must be forty lowercase hex characters |
| GitHub link, no file after the ref | `…/blob/<40-hex>` | `error` | — names a repository at a commit, not a file |
| GitHub link, non-file verb | `…/tree/…`, `…/blame/…`, `…/commits/…`, `…/edit/…` | `error` | — a view of a file is not a citation of it |
| `raw.githubusercontent.com`, pinned | `…/<40-hex>/Justfile` | `deferred` → `ok`/`error` | As above. |
| GitHub issue or pull-request URL | `…/issues/1459` | `deferred` → `ok`/`error` | That the URL resolves. Never what it says. |
| Other external URL | `https://example.com/spec` | `deferred` → `ok`/`error` | That the URL resolves. |
| Commit reference | `commit <7-40 hex>` | `ok` | **The commit exists in this repository.** A commit that does not is an `error`. |
| Graph edge | `a -> b (1 hop)` | `unverified` | Nothing. Owned by #1314. |
| Tool result, git or grep | `git_ls_tree(ref=…, path=…) -> …` | `unverified` / `error` | That the cited ref and path still resolve. Never the asserted result, which is prose. |
| Tool result, other families | `shell('…') -> …` | `unverified` | Nothing, and the message names why that family has no verifier. |
| Anything else | `#1459`, `issue #1459`, free text | `error` | — hard error, never a notice |

A markdown wrapper — `[label](target)` — is unwrapped before any of this, so it is
accepted wherever its bare target would be, and rejected wherever its target would be.

**Read the right-hand column, not the middle one.** An `ok` still establishes less than an
author would assume: no citation form opens a file and compares it against the statement it
sits under. What changed is that fewer forms now return `ok` for nothing — a line past the
end of a file fails, a missing commit fails, a renamed symbol fails, and a dead ref fails.

**Prefer the symbol anchor for a claim about code.** A line number names a place in the file
as it was; a symbol names the thing the claim is about. When code above it moves, the line
citation keeps passing while naming unrelated code, and the symbol citation still resolves.
When the symbol's name disappears from the file, the citation fails — which is the point. The
match is lexical, so a name still mentioned in a comment or a string literal keeps passing; this
detects a name vanishing, not a definition being removed.

## MUST

1. **A code reference MUST be a citation in the node's frontmatter `evidence` array.**
   The schema defines no other field for one, and rejects any field beyond the seven it
   names.
2. **A reference to a file in this repository MUST be a repository-relative path,
   resolved from the repository root, naming a file that exists.** Not a path relative to
   the citing document: `launchpad/project-intelligence/corpus/validate.py` is a real
   file, and the citation `validate.py` names nothing, because the root is the only
   anchor. That verdict does not depend on the directory you run the check from — the
   root is resolved from the validator's own location, so the citation fails identically
   from anywhere. **Whether the path also carries a position is not this rule's
   business:** MUST 6 sets the permitted position syntax and SHOULD 1 sets the
   preference between them. This rule governs the anchor only.
3. **A reference MUST NOT be an absolute path and MUST NOT resolve outside the
   repository**, before or after `..` segments and symlinks are followed.
4. **A file in this repository MUST NOT be cited as a GitHub link when a repository path
   would name the same file.** The path form is checked against the filesystem; the link
   form is checked against a regular expression. Choosing the link discards the only
   guarantee available.
5. **A GitHub repository link MUST be pinned to the full forty-character lowercase commit
   SHA, MUST use the `blob` or `raw` view, and MUST name a file after the ref.** ADR-0003
   is the source of the pinning rule; the other two are the validator's.
6. **A citation MUST NOT carry a column, a symbol fragment, or any suffix beyond `:line`
   or `:start-end`.** Editor and compiler output (`file:219:5`) and index fragments
   (`file#symbol=Name`) are hard errors, reported confusingly — see *Enforcement*.
7. **An issue or pull request MUST NOT be cited as `#1459` or `owner/repo#1459`.** Both
   are hard errors. Cite the full URL, which is recorded `unverified`, or attribute the
   claim through `provided_by` — see *Exceptions and escalation*.
8. **A claim classified `FACT` MUST rest on at least one citation the validator can
   open**, with exactly one exception, in *Exceptions and escalation*. A `FACT` supported
   only by `unverified` citations has been checked by nothing.
9. **A node MUST carry at most one commit-only `FACT`** — the entry recording the
   revision the node was checked against. Nothing enforces this; a second one produces
   another non-fatal notice and still exits 0. It is a rule a reviewer holds.

## SHOULD

1. **Prefer a bare path to `path:line`.** The line is not verified against the file, so a
   position that has silently drifted is worse than no position: it looks precise. This
   preference is provisional and lapses when #1459 is fixed.
2. **When a position genuinely earns its place, cite a range that brackets a named
   symbol, and name that symbol in the `statement`.** A range that has drifted is still
   wrong, but a reader comparing the statement's symbol name against the file can detect
   it. A bare line number gives them nothing to compare.
3. **Cite the narrowest source that actually supports the claim, and only that.** A
   second citation added "for context" is a second thing that can rot, and the checker
   will not tell you which one did.
4. **Use the markdown-link form when a human will read the citation.** It is accepted for
   both repository paths and URLs, and it costs nothing.
5. **For code in another repository, use a pinned `blob` link** — and record, in the
   `statement` itself, what you actually opened, because nothing downstream will.

## Enforcement

Run it locally, from the repository root:

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

Exit 0 passes; 1 means at least one error, each naming the node it came from.
`just corpus-validate` is the same command but needs Hermit activated first. CI runs it
on every pull request and every push to `launchpad` that touches
`launchpad/docs/corpus/**`, so a local failure is a CI failure.

**Four things a green run does not establish.** The first three are stated in
`AGENTS.md`; the fourth is not stated anywhere else.

1. **That a citation supports its claim.** Checking is structural. A `FACT` citing a real
   file that says nothing on the subject passes cleanly. Only a person reading the source
   makes it a `FACT`.
2. **That an `UNVERIFIED` item is fine.** Those notices mean the form was recognised and
   could not be opened. They print on passing runs precisely so a PASS does not claim
   them.
3. **That a line number is real.** `Justfile:999999` passes against a 1005-line file
   (#1459).
4. **That a rejection means what its message says.** A citation containing no whitespace
   that matches no other form falls through to the repository-path rule, so `#1459` and
   `launchpad-26/buzz#1459` are reported as paths that "do not resolve to a real file in
   the repository". They are not paths and were never intended as paths. An author
   debugging that message will look for a missing file that was never meant to exist.

**What a reviewer has to hold, because no check will.** MUST 4 (path over link),
MUST 8 (a `FACT` rests on something openable), MUST 9 (one commit-only `FACT`), and every
SHOULD. All four pass validation whether honoured or not.

## Exceptions and escalation

**The one permitted commit-only `FACT`** is the entry recording the revision the node's
claims were checked against. It is exempt from MUST 8 because the citation *is* the
claim, and it is checkable, just not by this checker:

```bash
git cat-file -e <sha>   # exit 0 means that revision exists in this repository
```

Run that and the entry is a `FACT`. A commit citation attached to any claim *about
repository content* is not covered by this exception — that claim needs the file, at that
revision.

**When the only available source is unopenable** — an issue, a pull request, an upstream
specification, a tool's output — do not promote it. Cite the URL and accept the
`unverified` notice, or, where a person or an issue is the source rather than a document,
classify the claim `TEAM_KNOWLEDGE` and name that source in `provided_by`. A policy choice
attributed to a file that does not discuss it is not an `INFERENCE`; it is a
misclassification.

**When a rule here cannot be met**, do not relax it locally. A standard one node
quietly widens has stopped being a standard, and the validator will not notice. Raise an
issue against #605 describing the reference you needed and could not write. The `flagged`
status is not the escape hatch: it names an unresolved conflict between two authoritative
sources, not an inconvenient rule.

**When this document and the validator disagree**, the validator is right and this
document is the defect. Fix it here, with a new measured verdict, rather than working
around it in a node.

## Read these instead of trusting a copy here

| For | Read |
|---|---|
| The frontmatter contract, and which field a citation lives in | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose explanation of those fields | `launchpad/docs/corpus/schema/README.md` |
| The six citation shapes as vocabulary | `launchpad/project-intelligence/CONTRACT.md` §3 |
| What the checker actually does — the authority for every verdict above | `launchpad/project-intelligence/corpus/validate.py` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Why a link must be pinned to the full SHA | `launchpad/decisions/ADR-0003-handbook-page-provenance-contract.md` |
| Why Markdown with frontmatter is canonical | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| How to rank conflicting evidence | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |

Enum member lists and the schema's field-combination rules are **not** repeated in this
document. The validator never reads body prose, so a copy of them here would stay green
forever after going stale.

## Scope and omissions

**Not covered here, and these are gaps rather than silence:**

| Not covered | Owned by |
|---|---|
| Classifying a claim, evidence precedence, and the graph-edge and tool-result forms | #1314 |
| Line numbers not being checked against file length | #1459 |
| Provenance for generated artifacts | #1316 |
| Naming, identifiers, taxonomy, status, diagrams, and the per-type templates | #1307 and #1309–#1351 |
| Whether ADR-0003's markdown-link wrapper is required on corpus evidence | #605 |

**A divergence found while writing this node, reported rather than fixed.** `CONTRACT.md`
§3 enumerates six shapes and none of them is a URL — the section contains no occurrence of
"url", "http" or "github". `validate.py` nevertheless implements a whole URL branch.
`AGENTS.md` presents a seven-row table and says explicitly that it **is not** a summary of
§3: its two URL rows are forms the validator recognises and §3 does not enumerate. This
node describes the forms the validator accepts and says plainly which of them §3
enumerates. Reconciling `CONTRACT.md` with what the validator implements is still open —
filed as #1478 — but it is not this node's to do: it may not edit `AGENTS.md`, and it does
not own `CONTRACT.md`.

An earlier draft of this node asserted the opposite — that `AGENTS.md` introduced the table
*as* §3's six shapes and then listed seven. That was true of an earlier `AGENTS.md`,
corrected in `ebe2daf72`, and the miscount had already been used here to build a scope
argument before review caught it. `AGENTS.md` records the same incident from its own side.
The lesson is the one this standard exists to teach: a claim recorded against one revision
of a moving document is not a claim about the document that finally ships beside it.

**No `relationships` in this node's frontmatter.** The reason is merge order, not an empty
corpus. At the recorded revision `corpus-agents` is loadable, so an edge to it would
validate here — and would become a hard error the moment this node reached `launchpad`
ahead of the branch that introduces `corpus-agents`, because an unmatched target fails.
Every sibling standard is likewise unmerged. Edges get declared once the set has landed,
which is a follow-up, not an oversight.

**What the recorded revision means is not settled here.** #636's definition of done
requires that a draft is "checked against the repository revision recorded in provenance",
so the revision is at minimum the one this node's claims were checked against. Whether it
may stay put across later edits, and what to do when only some claims are re-verified, is
**#1321's** to decide (`document corpus standard for provenance`, unlanded). An earlier
draft of this section asserted the wider rule as settled — it was copied from a version of
`AGENTS.md` that has since removed it, after three cross-model passes refused it as a
corpus-wide policy no authorized source establishes.

**Expected but not verified when this node was written:**

- **No pinned GitHub link in this node's ledger was fetched from GitHub**, because there
  are none — every citation here is a repository path. The claim that a pinned link to a
  nonexistent file passes was established against the validator, not against GitHub, which
  is exactly the point being made.
- **The validator was not exercised against a corpus containing two nodes that cite each
  other's paths.** Nothing in `find_citation_problems` treats a corpus path differently
  from any other, so no difference is expected; it was not confirmed.
- **`git cat-file -e` was run for this node's own recorded revision and no other.** The
  *Exceptions and escalation* procedure is stated from that one use.
