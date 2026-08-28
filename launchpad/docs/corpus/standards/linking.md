---
id: corpus-standard-linking
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
  - statement: "validate.py's frontmatter loader splits a node's file on the first '---\\n' boundary into frontmatter and body, parses only the frontmatter as YAML, and never inspects the body again -- no function in validate.py opens, greps, or otherwise reads a node's Markdown body after this split."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "node.schema.json permits exactly seven top-level frontmatter properties (id, type, status, origin, audiences, evidence, relationships) and sets additionalProperties to false, so no eighth field -- a 'see also' or 'links' array -- can hold a pointer to related material without a schema change."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A relationships[].target is a bare kebab-case id resolved by exact string match against loaded nodes' id values, carries one of five fixed types (depends-on, supersedes, implements, references, part-of), and validate.py raises a hard error when no loaded node carries the named id; nothing in relationships.schema.json or validate.py associates a target with prose, a heading, or a location inside the target node's body."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "corpus-standard-decision-references governs which claims a decision record may be cited for as evidence, how to cite one in the evidence ledger, and what to do when a cited decision is superseded or two accepted decisions conflict; its own Scope and authority section states this boundary explicitly."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "AGENTS.md's Scope and omissions table lists 'naming, identifiers, linking, provenance, status, taxonomy, diagrams, evidence' together as per-type standards owned by 'somewhere in #1307-#1351', and separately warns that this range is a range and not a mapping -- it does not say which number owns which subject -- after an agent authoring a sibling node invented nine false issue-to-subject mappings from that same table."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "In the four nodes merged into origin/launchpad's corpus at the recorded revision, AGENTS.md, standards/confidence.md, and standards/decision-references.md each refer to a sibling file or a decision record in body prose as a bare repository-relative path or bare filename inside backticks -- for example 'launchpad/decisions/ADR-0029-corpus-evidence-precedence.md' and 'AGENTS.md' -- and none of the three contains a single Markdown hyperlink of the form [text](target) anywhere in its body prose."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "README.md, the fourth node merged into origin/launchpad's corpus at the recorded revision, refers to the same kind of target -- AGENTS.md, node.schema.json, individual ADRs -- using full Markdown hyperlinks throughout, for example '[launchpad/docs/corpus/AGENTS.md](AGENTS.md)' and '[ADR-0028-corpus-canonical-representation.md](../../decisions/ADR-0028-corpus-canonical-representation.md)', for the identical kind of pointer the other three merged nodes write as a bare path."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
  - statement: "decision-references.md is the only one of the four merged nodes that references a GitHub issue using a Markdown reference-style link ([#1410][i1410]) backed by a footer block of link targets; AGENTS.md, README.md, and confidence.md each mention issue numbers in body prose as a bare '#NNNN' with no surrounding link syntax."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
  - statement: "GitHub's own documentation states that autolinked references to issues and pull requests are 'automatically converted to shortened links' within conversations on GitHub, but that 'Autolinked references are not created in wikis or files in a repository' -- so a bare '#1410' inside a Markdown file stored in this repository does not render as a clickable link on GitHub, unlike the same text typed into an issue or pull request comment."
    entry_class: FACT
    evidence:
      - "https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/autolinked-references-and-urls"
  - statement: "No workflow under .github/workflows whose name starts with 'launchpad-' mentions Markdown, and neither of the two corpus-specific workflows (launchpad-corpus-validate.yml, launchpad-corpus-schema-tests.yml) runs anything beyond validate.py or the schema test suite; no markdownlint configuration file exists anywhere in the repository."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
      - ".github/workflows/launchpad-corpus-schema-tests.yml"
  - statement: "Zero occurrences of a Markdown anchor link (the pattern '](#') exist across AGENTS.md, README.md, confidence.md, and decision-references.md; every intra-document section pointer in those four files instead names the target heading in prose, typically italicized, as in 'See *Enforcement, and where it stops*' and 'under *Three things a passing run does not mean*'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "README.md points a reader at a specific section of a different node by combining a Markdown link to the file with an italicized heading name in the same sentence -- 'owned by launchpad/docs/corpus/AGENTS.md under *Three things a passing run does not mean* -- read it there before reviewing a corpus change' -- rather than an anchor URL fragment."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
  - statement: "AGENTS.md's own citation-shape table was, in an earlier revision, miscounted as a summary of CONTRACT.md section 3's six shapes; an agent authoring a sibling node built a scope argument on that miscount before their plan review caught it, and the corrected text now states 'this table is seven rows and is not a summary of section 3' as a standing warning against restating an enumerated set that another document owns."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "confidence.md restates one row of the schema's field-combination matrix (the confidence row) because its own Requirement 1 cannot be stated without it, and carries a table titled 'If the schema's rules change, these are the places in this document that must change with them' naming exactly which of its own sections restate schema content and which schema element each one tracks."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/confidence.md"
  - statement: "AGENTS.md's Retiring a node procedure narrates a relationships edge in prose rather than only declaring it: step 3 reads 'that node declares supersedes targeting the retired id -- the type exists in relationships.schema.json for exactly this', pairing a plain-language explanation of what the edge means with the schema element that encodes it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's own front matter states this node was authored and checked against repository revision 919886b4192df6251de50c547548ecae5d85afce, the same revision this node records, so the four-node merge-target inventory this node cites from AGENTS.md, README.md, confidence.md, and decision-references.md was read at the identical revision as this node's own provenance."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Checked by running 'git fetch origin launchpad' and 'git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus' immediately before finalizing this node's front matter: the merge target carries exactly four loaded nodes outside schema/, with ids corpus-agents (AGENTS.md), corpus-readme (README.md), corpus-standard-confidence (standards/confidence.md), and corpus-standard-decision-references (standards/decision-references.md); none of the other four documents in this same five-way batch (provenance, review-requirements, taxonomy, test-references) are present."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md(id=corpus-agents), README.md(id=corpus-readme), schema/** (excluded), standards/confidence.md(id=corpus-standard-confidence), standards/decision-references.md(id=corpus-standard-decision-references)"
  - statement: "Because nothing in validate.py inspects a node's body, a link inside that body carries no mechanical consequence for whether the node validates: a body pointing at a node, section, or file that has never existed passes exactly as cleanly as a correct one, for the same reason AGENTS.md documents for a GitHub evidence citation pinned to a real commit but naming a nonexistent file."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.8
  - statement: "A body-prose mention of another node and a relationships[] edge to that same node serve different readers and neither substitutes for the other: the edge is what a generated graph view or a future relationship-aware tool resolves, while a reader of the rendered body -- human or agent -- sees only the prose unless they separately open the front matter, so a connection that matters to a body's argument but is never mentioned in the body is invisible to that reader even when a relationships edge for it exists."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
    confidence: 0.7
  - statement: "Issue #1318 requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1318 definition of done"
  - statement: "Issue #1318's dispatch note draws the boundary for this node explicitly: it governs when and how a node's body prose links to another corpus node, a decision record, code, or a test, as distinct from the relationships[] field's contract (#1317), how to cite a decision as evidence (#1310, merged), and how to cite code as evidence (#1308, unmerged at the recorded revision)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1318 dispatch note"
  - statement: "Issue #1308 (the code-references standard) was open and unmerged at the recorded revision, with its own Scope and authority section stating it governs citations of code in a node's evidence ledger, not body prose; this node's description of that boundary is therefore based on a PR diff read for context, not on a merged, settled document, and may need reconciling once #1308 lands."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1308, PR #1480 (open, unmerged at the recorded revision)"
relationships:
  - type: references
    target: corpus-agents
  - type: references
    target: corpus-readme
  - type: references
    target: corpus-standard-decision-references
---

# Standard: linking a node's body to something else

How a corpus node's Markdown **body** — the prose a reader actually reads, as
opposed to its machine-checked front matter — points at another corpus node, a
decision record, code or a test, a GitHub issue or pull request, an external
resource, or a section of a document. This is a policy node about one thing:
connective tissue in prose. Look up the section you need.

## Scope and authority

**This node governs** how body prose points a reader at something else, in four
parts: which target types exist and which document owns citing each one as
*evidence*; the syntax a body-prose pointer should use for each target type;
when a body pointer needs a `relationships[]` edge alongside it, and when it does
not; and what counts as restating another source's canonical content rather than
linking to it.

**It does not govern three surfaces that look adjacent and are not:**

| Surface | What it is | Owned by |
|---|---|---|
| `relationships[].target` | A bare id, resolved by exact string match, one of five fixed types, checked by `validate.py` | `node.schema.json` / `relationships.schema.json` for the contract; the identifiers standard (#1317, unmerged at the recorded revision) for the `id` half of it |
| A decision cited as **evidence** for an intent claim | An `evidence[].evidence` citation naming an ADR, judged by claim type and record status | `corpus-standard-decision-references` |
| Code or a test cited as **evidence** | An `evidence[].evidence` citation naming a repository path, pinned and positioned | The code-references standard (#1308, unmerged at the recorded revision — treat its content as informative, not settled, until it lands) |

The distinction that actually separates this node from those three: an
`evidence[]` entry and a `relationships[]` entry are both *fields* — the schema
shapes them, and `validate.py` checks what it can reach. A pointer inside the
**body** is not a field. It is a sentence, and nothing anywhere checks it. That
is this node's whole subject.

**Its authority is derived, not original**, the way `corpus-standard-confidence`
and `corpus-standard-decision-references` state theirs. `node.schema.json` and
`validate.py` already govern the two field-shaped surfaces above; this document
does not touch either. What it adds is the half no schema can hold: how to write
a sentence that points a reader somewhere real, and how to tell whether a body
has quietly become a second copy of a rule that already lives elsewhere.

| For | Read |
|---|---|
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The `relationships[]` contract and its five types | `launchpad/docs/corpus/schema/relationships.schema.json` |
| The `id` field's permanence and uniqueness contract | `launchpad/docs/corpus/schema/node.schema.json` today; the identifiers standard, #1317, once it lands |
| Citing a decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Citing code or a test as evidence | The code-references standard, #1308, once it lands |
| The six citation shapes `evidence[].evidence` may take | `launchpad/project-intelligence/CONTRACT.md` §3, and `launchpad/docs/corpus/AGENTS.md`'s extended table |

Where this document and any of those disagree, **they win** — this one has
drifted and should be fixed.

## Why a body-linking standard is needed at all

Two structural facts make this a real gap rather than a stylistic nicety.

**Nothing checks the body.** `validate.py` splits a node's file at the first
`---` boundary, parses only the piece before it as YAML, and never opens the
body again. A `relationships[]` edge that resolves to nothing is a hard error;
a body sentence that points at a node, section, or file that has never existed
passes exactly as cleanly as a correct one — the same failure mode AGENTS.md
already documents for a GitHub evidence link pinned to a real commit but naming
a file that was never there.

**There is nowhere else for a "see also" to live.** `node.schema.json` permits
exactly seven top-level fields and forbids an eighth. There is no `links` array,
no `see_also` field. A pointer that is not a typed relationship and not a
citation backing a specific claim has exactly one home: a sentence in the body.

Put together: the one surface this document governs is also the one surface no
tooling ever reaches. Every rule below is therefore review-enforced, and the
corpus's four merged nodes already show what happens without one — the same
kind of pointer is written two different ways by two different authors, both
schema-valid, both silently uncheckable:

- AGENTS.md, `confidence.md`, and `decision-references.md` each name a sibling
  file or a decision record as a bare repository-relative path or filename in
  backticks — `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`,
  `AGENTS.md` — with zero Markdown hyperlinks in any of the three.
- `README.md` names the identical kind of target with a full Markdown
  hyperlink throughout — `` [`launchpad/docs/corpus/AGENTS.md`](AGENTS.md) ``.
- `decision-references.md` alone links a GitHub issue with a reference-style
  link and a footer target (`[#1410][i1410]`); the other three merged nodes
  write the same kind of reference as a bare `#1410`.

None of this is a defect in those four nodes — nothing told any of their
authors which form to use, because nothing existed yet. It is exactly the gap
this standard closes.

## Which kind of pointer are you writing?

Answer this before choosing syntax. The target decides who owns the rule; this
node only owns the "body prose" column.

| You want to point at | As an evidence citation (backs a specific claim) | In body prose (this node) |
|---|---|---|
| Another corpus node | Not applicable — a citation backs a claim, a node isn't one | Name it; add a `relationships[]` edge only if the connection is one of the five typed kinds and resolves against the merge branch (see *Prose and `relationships[]`*) |
| An accepted decision | `corpus-standard-decision-references` — MUST rules on claim type, record status, superseded records | This node — a narrative mention that backs no `FACT`/`INFERENCE` on its own |
| Code or a test | The code-references standard, #1308 (unmerged) | This node — naming a file or symbol in passing |
| A GitHub issue or pull request | `TEAM_KNOWLEDGE`'s `provided_by`, or a citation shape from `CONTRACT.md` §3 | This node — no other standard names this target type |
| A section of this document | Not applicable | This node — see *Anchors and section pointers* |
| A section of a different document | Not applicable | This node — see *Anchors and section pointers* |

A single sentence can do both left and right columns at once — "Cite
`ADR-0029-corpus-evidence-precedence.md` for X" is simultaneously a citation
(governed by decision-references.md) and a body-prose mention of a decision
(governed by this node's syntax rules below). The two obligations stack; they
do not compete.

## MUST

These are enforced by review. Nothing mechanical reaches any of them — see
*Enforcement, and where it stops*.

1. **A body-prose pointer to a specific corpus node, decision record, code
   path, or GitHub issue/PR MUST name a target that currently exists**, checked
   by the author actually opening it, not assumed from memory or from an
   earlier draft. This is the load-bearing MUST: it is the one thing every rule
   below exists in service of, and it is the one thing that can go silently
   wrong forever, because nothing else will ever check it.
2. **A GitHub issue or pull request reference MUST use a Markdown link (inline
   `[#NNNN](url)` or reference-style `[#NNNN][iNNNN]`) if the sentence needs it
   to be clickable when the file is read on GitHub.** A bare `#NNNN` does not
   autolink inside a repository file — GitHub's own documentation states that
   autolinking "is not created in wikis or files in a repository," only within
   conversations. Writing `#1318` in a node's body is a valid reference; it is
   not a working link, and a sentence that depends on the reader being able to
   click it needs the Markdown form instead.
3. **A pointer to a section within the same document, or within a different
   one, MUST name the target heading in prose** — quote or closely paraphrase
   the heading text, conventionally italicized ("under *Enforcement, and where
   it stops*") — **and MUST NOT rely on a Markdown anchor URL fragment**
   (`[text](#some-heading)` or `[text](file.md#some-heading)`). See *Anchors
   and section pointers* for why.
4. **A body-prose pointer to another corpus node's file MUST resolve to a real
   path** if written as a path or a Markdown link — the same discipline as an
   evidence citation, even though nothing enforces it here. A relative link
   that resolves from one directory but not another (`AGENTS.md` versus
   `../AGENTS.md`) is a real, silent failure mode with nothing to catch it;
   check it resolves from the file it is written in.
5. **Restating another source's enumerated or precisely-bounded rule set —
   an enum's members, a table of fixed shapes, a list of required fields — in
   place of linking to it is a defect, not a convenience**, whether or not
   the restatement is currently accurate. See *Linking without duplicating*.
   The corpus already has one incident of exactly this going wrong: an earlier
   restatement of a citation-shape table was miscounted, and a sibling node's
   author built a scope argument on the miscount before review caught it.
6. **A `relationships[]` edge MUST NOT stand in for a body-prose mention when
   the connection matters to a reader following the argument**, and a
   body-prose mention MUST NOT stand in for a `relationships[]` edge when the
   connection is one of the five typed kinds and resolves against the branch
   this change will merge into. See *Prose and `relationships[]`* — this MUST
   is the operational form of "do both, for different readers," not a
   preference between them.

## SHOULD

Enforced by review. Depart from these with a stated reason.

- **Cite the node or file by the same string a reader would grep for.** For a
  corpus node this is usually the filename or path, because that is what is
  openable and clickable; the `id` matters most where it is machine-resolved
  (a `relationships[].target`), not in a sentence a human is reading. Naming
  both — "`AGENTS.md` (`corpus-agents`)" — costs one clause and removes the
  ambiguity entirely; reach for it when the sentence is itself about ids or
  about a relationship.
- **Use a Markdown hyperlink for a file pointer when the node's primary
  purpose is navigation** — an entry point like `README.md`, or any node
  whose `audiences` includes `developer` reading it directly on GitHub — and a
  bare backtick path when the node's primary purpose is being followed as
  instructions or cited as a source. This is not a rule the corpus has
  written down before this node; it generalizes the split already observed
  between `README.md` (links) and `AGENTS.md`/`confidence.md`/
  `decision-references.md` (bare paths), and is offered as the reason for
  continuing that split deliberately rather than by accident.
- **Prefer a reference-style link (`[#NNNN][iNNNN]` with a footer block) over
  an inline link when a document cites the same issue more than once**, the
  way `decision-references.md` does — one footer entry instead of repeating
  the full URL at every mention, and a single place to fix if the URL ever
  needs to change.
- **On a second mention of the same issue in the same paragraph, a bare
  `#NNNN` is enough** — link once, per the surrounding prose, not every time
  the number appears. `decision-references.md`'s own body already does this
  (`[#1314][i1314]` once, then a bare `#1314` two sentences later in the same
  thought).
- **When narrating a `relationships[]` edge in prose, name the relationship
  type and the reason, not just the target** — "declares `supersedes`
  targeting the retired id" reads very differently from "see the old node."
  AGENTS.md's own *Retiring a node* step 3 is the worked example.
- **Quote a decision's operative sentence rather than pointing only at its
  filename**, when the body's own argument depends on what the decision
  actually says — decision-references.md's MUST 3 already forbids a line
  position on a decision citation for this exact reason: a quotation survives
  the file being reflowed, a position does not.

## Anchors and section pointers

Across the four nodes merged at the recorded revision, the pattern is
unanimous and worth stating as a rule rather than leaving it to keep
happening by coincidence: **zero** occurrences of a Markdown anchor link
(`](#`) exist anywhere in AGENTS.md, README.md, confidence.md, or
decision-references.md. Every section pointer, inside a document or across
documents, is a heading name in prose.

**Why, not just what.** A GitHub-rendered anchor is generated from the
heading's text at render time. Nothing in this corpus's tooling, or in this
repository's CI, checks that an anchor link's fragment still matches a real
heading — there is no markdown-link checker configured anywhere in the
repository, and neither corpus-specific workflow does anything beyond running
`validate.py` or the schema test suite. Rename a heading and every anchor
pointing at it goes quietly nowhere, with no error at the point of the rename
and no error at the point of the broken link. A heading name written in prose
degrades more gracefully: it goes stale-looking rather than silently dead — a
reviewer rereading "*Enforcement, and where it stops*" notices when that
heading no longer exists, because the words are sitting right there to
compare against the document's actual headings.

**For a section in the same document**, name it in prose: "See *Section
Name*." Italics are the observed convention; follow it.

**For a section in a different document**, combine a file pointer with the
heading name in the same sentence — README.md's own pattern: "owned by
`launchpad/docs/corpus/AGENTS.md` under *Three things a passing run does not
mean*." The file pointer gets the reader to the document; the heading name
gets them to the paragraph, and neither piece depends on a fragment matching
anything.

## Prose and `relationships[]`

These are not substitutes for each other, because they reach different
readers.

A `relationships[]` edge is what a generated graph view, or a future
relationship-aware tool, resolves. It is invisible to a reader of the
rendered body — human or agent — unless that reader separately opens the
front matter. A body-prose mention is the reverse: it is exactly what that
reader sees, and it resolves to nothing a machine can traverse.

**When the connection is one of the five typed kinds** — `depends-on`,
`supersedes`, `implements`, `references`, `part-of` — **and it resolves
against the branch the change will merge into**, declare the edge. Do not
let a well-written sentence substitute for it: a reader is not the only
consumer of this corpus, and an edge that exists only in prose is invisible
to everything else.

**When the connection matters to the argument the body is making**, say so
in prose, even when the edge is also declared. AGENTS.md's *Retiring a node*
step 3 is the pattern to follow: "that node declares `supersedes` targeting
the retired id — the type exists in `relationships.schema.json` for exactly
this." The sentence explains what the edge means and why it exists; the edge
is what a tool can walk. Declaring the edge with no sentence explaining it
answers a question only a tool will ever ask.

**When the connection is real but the target does not yet resolve on the
merge branch** — the exact situation identifiers.md and this node's own
front matter are both in at the recorded revision — prose is still available
even though the edge is not. Say so plainly rather than silently dropping the
mention: name the target, and say that the edge is deferred and why, the way
this node's own *Scope and omissions* does below for its own case.

## Linking without duplicating

Every standard in this batch carries a DoD line requiring it to "link...
without duplicating... canonical content." This is the operational answer.

**Duplication is restating a bounded set — an enum's members, a table of
fixed shapes, a list of required fields — that another source owns**, in a
way that goes stale the moment that source changes and nothing here notices.
The corpus has one documented incident of exactly this: an earlier version of
AGENTS.md's citation-shape table was miscounted relative to what it claimed
to summarize, and a sibling node's author built a scope argument on the
miscount before their own plan review caught it. The failure was not that the
table was wrong when written — it was that a bounded set had been copied
instead of linked, so nothing forced the copy to be checked against its
source again.

**A citation-backed claim about that source's behavior is not duplication.**
"The checker resolves a `relationships[].target` by exact string match" is a
sentence *about* `validate.py`'s behavior, cited to it, needed to explain why
a rule in this document exists. It is not a second copy of the matching
logic. The difference is whether a future change to the source would make
this document's *sentence* wrong (duplication — the sentence has become an
independent claim standing in for the source) or would make this document's
*citation* stale while the claim above it still needs re-checking (a normal,
expected citation, exactly like any other `FACT`).

**The working test:** could someone read only this document's restated
version and be wrong about the source without ever noticing? If restating an
enum, a table, or a rule's exact boundary would let that happen, link to the
source instead of restating it. If a single sentence is needed to make this
document's own MUST self-contained — the way `confidence.md`'s Requirement 1
cannot omit the `confidence` field's own rule — restate only that sentence,
say explicitly that it is restated and from where, and accept that a reviewer
re-checks it against the source when the source changes, the same way any
other `FACT` gets re-verified.

## Enforcement, and where it stops

**Enforced mechanically: nothing.** This is the one standard in the batch
where that row is not a gap in an otherwise-enforced table — it is the whole
table. `validate.py` never reads a node's body past the frontmatter
delimiter, so no MUST above has any mechanical backing. A body containing a
link to a node that has never existed, an anchor fragment that matches no
heading, or a bare issue number that never renders as a link validates
exactly as cleanly as a body with none of those problems.

**Enforced by review, entirely:**

| Gap | Consequence |
|---|---|
| MUST 1 — the target actually exists | A stale or invented pointer is discoverable only by a reviewer opening it |
| MUST 2 — issue links are clickable where needed | A bare `#NNNN` reads as a link to an author who has not checked GitHub's own behavior, and stays wrong until someone does |
| MUST 3 — no anchor fragments | Nothing rejects one if an author writes it; it simply breaks silently on the next heading rename |
| MUST 4 — relative paths resolve from where they are written | A link that resolves in one context and not another is invisible until a reader in the failing context tries it |
| MUST 5 — no duplicated enumerations | A stale restatement looks exactly as authoritative as a current one, and stays that way until compared against its source |
| MUST 6 — prose and `relationships[]` used for what each reaches | `validate.py` accepts a node with an edge and no explanatory prose, or prose and no edge, without complaint either way |

The same pattern the sibling standards for `confidence` and decision
references name for their own fields applies here with nothing left over:
everything a schema can hold is held elsewhere, and this whole subject is
outside what a schema can hold.

## Exceptions and escalation

**There is no exception process, because there is no mechanical rule to
except.** Every MUST above is a review judgment, not a gate. A reviewer who
disagrees with how a pointer is written raises it as ordinary review feedback,
the same as any other prose issue.

**When a target genuinely cannot be linked yet** — a corpus node that does
not exist on the merge branch, a standard still in an open PR, a decision not
yet accepted — say so in the body rather than omitting the mention or forcing
a premature link. This node's own body does exactly that for the
code-references standard, #1308, throughout: named, described as unmerged,
and not treated as settled.

**When the question is whether something should be a corpus node, a
`relationships[]` edge, or an evidence citation at all** — rather than how to
write the pointer once that is decided — that is not this node's call. It is
the same one-idea, one-task discipline AGENTS.md states for content: file it
separately rather than deciding it here.

## Scope and omissions

**This node covers** the four target-type/mechanism split above; syntax MUSTs
and SHOULDs for corpus-node, decision, code, and issue/PR pointers written in
body prose; anchor and section-pointer conventions; when a body mention and a
`relationships[]` edge are both required versus when either alone suffices;
and what distinguishes linking from duplicating another source's canonical
content.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `relationships[].target` field's own contract — type, uniqueness, permanence | `node.schema.json` today; the identifiers standard, #1317, once it lands |
| Citing a decision as evidence for a claim | `corpus-standard-decision-references` |
| Citing code or a test as evidence for a claim | The code-references standard, #1308, unmerged at the recorded revision |
| The evidence-entry contract generally — classes, required fields, the six citation shapes | `launchpad/docs/corpus/AGENTS.md` today; the evidence standard, #1314, once it lands |
| Filename shape, the filename-to-id correspondence, and document titles | The naming standard, #1319, unmerged at the recorded revision — its own Scope and omissions table names this node as the owner of "link syntax and anchor conventions between corpus documents," which is the boundary this node draws from its side too |
| Whether a recorded provenance revision may stay put across an edit | #1321 |
| Corpus-wide review process and checklist beyond the linking-specific checks this document names | #1322 |

**This node declares three relationships, each checked against
`origin/launchpad` immediately before finalizing front matter** (`git fetch
origin launchpad && git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`, run at the revision this node's provenance entry
records): the merge target carries `corpus-agents`, `corpus-readme`,
`corpus-standard-confidence`, and `corpus-standard-decision-references`, and
none of the other four documents dispatched alongside this one.

- **`references corpus-agents`.** This node's *Why a body-linking standard is
  needed at all* and *Anchors and section pointers* sections both draw
  directly on AGENTS.md's text — its citation-shape-table miscount incident,
  its *Retiring a node* step 3 — as worked evidence, not decoration.
- **`references corpus-readme`.** README.md is this node's positive example
  throughout: the Markdown-hyperlink convention, and the file-plus-heading
  pattern for cross-document section pointers, are both drawn from its actual
  text, cited and quoted above.
- **`references corpus-standard-decision-references`.** This node's own
  *Scope and authority* table names it as the owner of citing a decision as
  evidence, and its MUST 3 (no line position on a decision citation) and its
  worked pattern for narrating a `relationships` edge in prose are both used
  above as precedent this node continues rather than reinvents.

`corpus-standard-confidence` is not targeted: this node does not draw on its
content anywhere in the body above, and a `references` edge with nothing in
the prose backing it would be exactly the "edge with no sentence" failure
mode this node's own MUST 6 and *Prose and `relationships[]`* section argue
against.

**Expected but not verified when this node was written**, per the rule in
*Creating a node* step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No generated view or tooling was tested reading a body-prose link.**
  Whether a future generator that walks corpus content expects any particular
  link shape is unknown; this node's rules are written for a human or agent
  reader, because that is the only consumer that exists today.
- **The claim that GitHub does not autolink a bare `#NNNN` inside a
  repository file was checked against GitHub's own current documentation,
  not against a live rendered page in this repository.** The documentation
  page was read and quoted directly; whether GitHub's actual rendering
  behavior still matches what its documentation states, at the moment a
  reader opens one of these files, was not independently confirmed by
  rendering one.
- **Whether the `README.md`-versus-the-rest split (links for navigation
  entry points, bare paths elsewhere) was a deliberate choice by either
  document's author, or an incidental difference in each author's own
  style**, was not established from any source — this node's SHOULD guidance
  offers the split as a reason to keep, not as a decision it found on record.
- **No author has yet applied this standard to a node written after it.**
  Whether its MUST list is followable in practice, and not merely internally
  consistent, is untested.
