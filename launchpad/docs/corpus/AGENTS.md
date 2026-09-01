---
id: corpus-agents
type: agent
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 0052f5a7820ca4ca261efa233feb8bb53858ade6."
    entry_class: FACT
    evidence:
      - "commit 0052f5a7820ca4ca261efa233feb8bb53858ade6"
  - statement: "Markdown with YAML front matter is the one canonical authored representation of a corpus node; every other serialization is a generated derived view."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "A node's front matter is validated against node.schema.json, which requires id, type, status, origin, audiences and evidence, additionally permits relationships, and rejects any field beyond those seven."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The corpus root is launchpad/docs/corpus, and validate.py is the deterministic check that governs it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "Justfile"
  - statement: "The schema/ subtree is excluded from validation because it is the schema's own testing infrastructure rather than corpus content."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Evidence precedence is contextual by claim type, and two authoritative sources of the same claim type in conflict leave the node flagged for a human rather than silently resolved."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Citations take six shapes and only three of them name a file that can be opened."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "Citation checking is structural: the validator confirms a cited path resolves to a real file inside the repository, never that the file supports the statement it sits under."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A relationship whose target matches no loaded node's id is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "This file is also resolved as the nearest AGENTS.md for every change under launchpad/docs/corpus, so it is read as governing instructions and not only as a corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/preflight_core.py"
  - statement: "Changes under launchpad/docs/corpus are validated in CI on pull requests and on pushes to the launchpad branch."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "Evidence entries are classified FACT, INFERENCE or TEAM_KNOWLEDGE, and the class chosen decides which further fields the schema requires or forbids."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "supersedes is a typed relationship whose declared directionality is that the source replaces the target and the target becomes historical."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "A non-GitHub external URL is reported UNVERIFIED on a default run, which blocks validation rather than passing as a notice; under --check-links it is fetched, verifying ok when it resolves and error when it does not."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A GitHub file link must be pinned to a full 40-character commit SHA, use a file-content verb, and name a path within the repository; under --check-links it is additionally fetched, so a well-formed link naming a file that does not exist is reported error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Deleting a node breaks every relationship targeting it, while retiring it by status change leaves those relationships resolving."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Retirement is therefore a status change that keeps the file and spends the id permanently, rather than a deletion."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
    confidence: 0.8
  - statement: "Issue #636 requires that the draft is checked against the repository revision recorded in provenance."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#636 definition of done"
  - statement: "Issue #636 requires that a node represent one independently maintainable idea, and that a newly discovered second concept, contract or procedure be filed as its own task rather than folded in."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#636 definition of done"
  - statement: "A git pathspec carrying a citation's :line or :start-end suffix matches nothing and reports empty output with exit status 0, so an unnormalized file citation makes a changed file indistinguishable from an unchanged one."
    entry_class: FACT
    evidence:
      - "git_diff_name_only(0052f5a7820ca4ca261efa233feb8bb53858ade6, pathspec='launchpad/docs/corpus/AGENTS.md:127') -> empty output, exit status 0, while the same pathspec without the ':127' suffix reports that file as changed"
  - statement: "Every non-.md file under the corpus root is rejected today, including one placed under generated/, because no generator exists to reproduce it from canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A commit citation is resolved against this repository's object store: a commit that exists verifies ok and one that does not is a hard error, so a FACT resting only on a commit citation is no longer reported UNVERIFIED at all."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation naming a line or line range is checked for both the path and the position: a line or range extending past the cited file's length is a hard error (#1459)."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
---

# Working with the documentation corpus

Instructions for creating, updating and retiring one node in
`launchpad/docs/corpus/`. Look up the section you need; this is a reference, not a
tutorial.

**Authoritative sources — this file duplicates none of them:**

| For | Read |
|---|---|
| The front-matter contract (fields, enums, conditional rules) | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose explanation of those fields | `launchpad/docs/corpus/schema/README.md` |
| Adding a value to a closed enum | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Why Markdown + front matter is canonical | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| How to rank conflicting evidence | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The six citation shapes | `launchpad/project-intelligence/CONTRACT.md` §3 |
| What the checker actually enforces | `launchpad/project-intelligence/corpus/validate.py` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

## What a corpus node is

**One file is one node.** A node is a Markdown file with YAML front matter, and that
is the single canonical authored representation; anything else — JSON, an index, a
graph serialization — is a generated derived view, never hand-authored.

**One node is one independently maintainable idea.** If a second concept, contract or
procedure turns up while you are writing, it does not get folded in. File it as its
own task and link to it.

**Where it goes.** Anywhere under `launchpad/docs/corpus/`, except `schema/` — that
subtree is the schema's own testing infrastructure and is deliberately skipped by the
checker, so a node placed there is never validated at all.

**Front matter.** Validated against `node.schema.json`. Field names, which fields are
required, the closed enums and the conditional rules between fields all live in that
file and in `launchpad/docs/corpus/schema/README.md`; they are not repeated here,
because a second copy drifts silently — the checker never reads this document's
prose, so a stale copy would stay green forever.

**`id` is permanent.** Kebab-case, assigned once, never renamed. Generated views
derive from it reproducibly, so renaming an id is a migration, not an edit.

**Relationships are optional and must resolve.** A `relationships[].target` naming an
id no node in the corpus carries is a hard error, so an edge may only name a node that
is already merged. Declaring none is always valid — but **check before you justify it**.
"There was nothing to point at" was true when this was the corpus's only node and stops
being true the moment a second one merges. Enumerate what exists
(`ls launchpad/docs/corpus/**/*.md`) and give the real reason, which may simply be that
the edges are being added in one pass later. Two independent agents authoring sibling
nodes copied an earlier version of this paragraph and produced a **false** justification
from it, because it read as a general rule rather than a fact about one moment.

**Authored versus generated.** Every non-`.md` file under the corpus root must live
in a `generated/` directory. Today the checker rejects such files even there, because
no generator exists yet to reproduce them from canonical Markdown, and a hand-written
file in `generated/` is indistinguishable from a real projection. That contract is
owned by #1316; until it lands, a corpus change adds Markdown only.

## Evidence, citations, and what validation proves

Every substantive claim in a node's body needs an entry in its front-matter
`evidence` array. That array is also the node's **provenance ledger** — there is no
separate provenance field, so the revision a node was written against belongs in
there too, as a commit citation.

### Choosing a class

Three classes exist: `FACT`, `INFERENCE`, `TEAM_KNOWLEDGE`. Which one you choose
decides which additional fields the schema then requires or forbids — those rules are
in `node.schema.json` and `launchpad/docs/corpus/schema/README.md`, and are not
restated here.

What the classes are *for* is the part that is easy to get wrong:

- **`FACT`** — you opened the cited source and it says so. Not "a source exists that
  probably says so."
- **`INFERENCE`** — you reasoned to it from evidence. Reasoning is not fact, however
  good it is.
- **`TEAM_KNOWLEDGE`** — something told to the corpus that no source corroborates, with
  `provided_by` naming who or what said it: a person, an issue, a decision record. It
  is the class for uncorroborated statements, and using it honestly beats promoting a
  recollection to `FACT`. It is **not** a place to park a decision you made yourself —
  attributing an extrapolation to the thing it started from does not make it something
  you were told.

When two sources disagree, do not average them and do not pick the newer one. For how
the system **currently behaves**, executable evidence — code, config, schema, passing
tests — outranks documentation and history. For **intended or authorized** behaviour,
accepted decisions outrank code that has drifted from them. When two sources of the
*same* claim type conflict, stop: record the conflict and leave the node flagged for a
human rather than resolving it yourself. `ADR-0029` is the full rule.

### What the checker does with each citation shape

`CONTRACT.md` §3 enumerates six shapes — file range, file line, bare path, graph edge,
tool result, commit. It contains **no URL form at all** (grep it for `http`: zero hits).
The two URL rows below are forms `validate.py` recognises and §3 does not enumerate, so
this table is **seven** rows and is not a summary of §3. An earlier version of this
sentence claimed it was, and an agent authoring a sibling node built a scope argument on
the miscount before their plan review caught it. What `validate.py` does with any of them
is not
documented anywhere else, so it is here — provisionally. This table is reference
material rather than instruction, and belongs in the evidence standard once that
lands (#1314); when it moves, this section links to it instead.

Read the middle column carefully: only two rows involve opening anything.

| Shape | Checker's verdict | Does it prove the target exists? |
|---|---|---|
| Bare repository path | Opened on disk; must be a real **file** inside the repo. A directory fails. | **Yes** |
| Path with a line or line range | The path is opened. The line number is **not** checked at all. | File yes, line **no** |
| GitHub file link | **Syntax only.** Must be pinned to a full 40-character SHA and have a non-empty path segment after it. | **No** |
| External (non-GitHub) URL | Reported `UNVERIFIED`. Nothing to pin, nothing to open. | No |
| Commit reference | Reported `UNVERIFIED`. Nothing on disk to open. | No |
| Graph edge | Reported `UNVERIFIED`. | No |
| Tool result | Reported `UNVERIFIED`. | No |

Anything matching **no** known shape is a hard error, not an `UNVERIFIED` notice.

**The GitHub row is the trap.** The checker never contacts GitHub. It reads the URL as
a string, and a link pinned to a real commit but naming a file that has never existed
passes as cleanly as a correct one:

```
https://github.com/launchpad-26/buzz/blob/<full-sha>/does-not-exist.md   ->  ok
```

So a typo in a remote path ships silently. A repo-relative path is checked against the
filesystem and a GitHub link is not — prefer the former for anything in this
repository, and treat a GitHub link as a *pin*, not as evidence the target is there.

### Three things a passing run does not mean

**1. It does not mean a citation supports its claim.** Checking is *structural*. The
checker confirms a path resolves to a real file; it never opens that file and compares
it against your `statement`. A `FACT` citing a real file that says nothing on the
subject passes cleanly. Only a human reading the source establishes a `FACT`.

**2. `UNVERIFIED` is not a pass.** Those notices are printed, never fatal, and they
mean the checker recognised the shape and could not open it. A `FACT` resting only on
`UNVERIFIED` citations has not been checked by anything — open the source and keep the
class, or change the class.

One conventional exception: the **provenance entry recording the revision** cites a
commit id, which no file can corroborate because the citation *is* the claim. It is
still checkable, just not by this checker:

```bash
git cat-file -e <sha>   # exit 0 means that revision exists in this repository
```

Run that, and the entry is a `FACT`. Every other claim needs a source you opened. A
commit citation attached to a claim *about repository content* is not covered — that
claim needs the file, at that revision.

**When the only source is an issue, a PR or a discussion**, you have no openable file and
no way to pin one: the validator's repository-link check matches only file and tree views,
so an issue URL is an external URL and lands on `UNVERIFIED`. Do not force it into a
`FACT` on a tool-result or URL citation. Use `TEAM_KNOWLEDGE` with `provided_by` naming
the issue — that is what the class is for, and ADR-0029 requires GitHub history to stay
attributed rather than be promoted to fact. An earlier draft of this section left that
case with no honest class at all, which an agent authoring a sibling node hit directly.

**Nothing enforces the convention, though the citation itself is now checked.** A
commit citation resolves against this repository's object store: one that exists
verifies `ok`, one that does not is a hard error. What stays unenforced is the *count*
— a second, third or tenth `FACT` resting only on `commit <sha>` is a reviewer's
signal, not a rule the tooling holds. If a node's ledger shows more than one
commit-only `FACT`, no check will raise it for you.

**3. A line number is checked for bounds, not for meaning.** `Justfile:999999` against
a 1005-line file is now a hard error, closing #1459. But bounds are all a line number
exposes: a position that has drifted to a *different line that still exists* passes
the check while naming the wrong code, and nothing detects that. So the preference
stands — prefer a bare path, because a position that has silently drifted is worse
than no position, because it looks precise.

This is not hypothetical. `agents/invariants.md` cited this validator's own source at
seven line positions; reshaping `validate.py` moved all seven, and only the one that
fell past the end of the file was caught. The other six passed while pointing at
unrelated code. All seven are now bare paths. The missing symbol-anchored citation
form — a position that would survive edits — is #2012.

**4. Two forms exist for cases a bare path cannot express.**

- `path/to/file.py#symbol=NAME` — a position that survives edits. Prefer it over
  `path:line` for any claim about code. Verified by a word-boundary search of the
  cited file, so a renamed or deleted symbol fails instead of drifting (#2012).
- `absent:path/to/thing@<40-hex>` — evidence that something is **not** there,
  pinned to a commit. Verified by resolving that path in that tree: present means
  the claim is wrong and the citation is a hard error. Use it for "no such node
  exists yet" claims instead of describing a `git ls-tree` run in prose (#2013).

**5. Several hundred existing citations are carried in a baseline.** Fail-closed
validation could not be applied retroactively to a corpus written under the old
rule, so the citations that block are enumerated by name in
`launchpad/project-intelligence/corpus/known-unverified.txt`. That list may only
shrink — an entry that no longer names a blocking citation is a hard error, and a
new blocking citation cannot join it without editing that file in a reviewed
commit. **If your new node's citation blocks, migrate the citation; do not add a
line to the baseline.**

### Pinning

A GitHub link to a repository file must use the full 40-character commit SHA.
`blob/main` is rejected, and correctly: evidence that can change underneath a green
validation run is the exact staleness provenance exists to catch. A link pinned but
naming no file is also rejected — it cites a repository at a commit, not the source
of the claim.

## Running the check

All three procedures below end with the same command, run from the repository root:

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

Exit status 0 is a pass; 1 means at least one error, and every error names the node it
came from. `just corpus-validate` runs exactly this, but needs the Hermit environment
activated first (`. ./bin/activate-hermit`) — the direct form above does not. The same
command runs in CI on every change under `launchpad/docs/corpus/`, so a local failure
is a CI failure.

To check a corpus tree somewhere other than the real one, pass `--root <path>`. Without
it the command always validates `launchpad/docs/corpus/`, whatever directory you are
standing in.

## Creating a node

1. **Confirm it is one idea.** If you are describing two contracts, or a concept and
   the procedure that uses it, that is two nodes. File the second as its own task now.
2. **Check nothing already covers it.** Read the existing nodes under
   `launchpad/docs/corpus/`. If one is close, you are updating, not creating.
3. **Record what you inspected, before drafting.** The repository revision
   (`git rev-parse HEAD`), the source paths and symbols you read, the tests,
   specifications and configuration you consulted, and — explicitly — anything you
   expected to verify and could not. Working notes need not be committed, but every
   category has a destination in the finished node, and they are not the same one:

   | What you recorded | Where it ends up |
   |---|---|
   | The revision | A commit citation in the `evidence` ledger (step 6) |
   | Paths, symbols, tests, specs, configuration you read | Citations on the `evidence` entries whose claims they support (step 7) |
   | Expected but could not verify | The body's scope-and-omissions section (step 8), named as a gap |

   Anything that reaches none of those three was not needed. If you inspected a source
   that backs no claim, you have either a missing claim or a stale note — decide which
   rather than leaving it in a file nobody reads.
4. **Choose the `id`.** Kebab-case, and permanent from this moment. Pick something that
   describes the idea, not where the file currently sits.
5. **Create the file** anywhere under `launchpad/docs/corpus/` except `schema/`.
6. **Write the front matter** against `node.schema.json`. Include a commit citation for
   the revision from step 3 — the ledger is the only schema-legal place for it.
7. **Write one `evidence` entry per substantive claim** you intend to make. Classify
   honestly; open every source you call a `FACT`.
8. **Write the body**, structured for lookup, with a scope section carrying **two
   distinct things**: what the node does not cover and who owns it, and — separately —
   what you expected to verify from step 3 and could not. A boundary and a confidence
   disclosure are different, and an earlier version of this step named only the first,
   leaving step 3's third category with nowhere to go.
9. **Add relationships only to nodes that exist on the branch you are merging INTO.**
   Not the branch you are working on — that distinction is the whole trap. The checker
   loads whatever is present where it runs, so a target that resolves in your worktree
   can be a hard error in CI: an agent branched off an unmerged node targeted it,
   validated clean locally, and would have broken the run on `launchpad` where that node
   does not exist yet. Check against the merge base
   (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), not your own
   tree. None is a valid answer, and while the corpus is being built out it is usually
   the right one.
10. **Run the check.** Fix what it names, and re-run until it exits 0.

## Updating a node

**What the recorded revision means — working practice, not settled policy.** #636's
definition of done requires that "the draft is checked against the repository revision
recorded in provenance", so the revision is at minimum the one the claims were checked
against. Everything beyond that — whether it may stay put across edits, what to do when
only some claims are re-verified — is **#1321's** to settle and is not established here.
Until it does, this document works to the rule below, and says so rather than dressing
it up as a corpus-wide standard.

1. **Confirm the change belongs in this node.** New idea, not new detail about the
   existing one? That is a new node.
2. **Re-verify the claims you are touching**, against those sources at current `HEAD`
   (`git rev-parse HEAD`). A claim whose source moved is not still a `FACT` because it
   used to be.
3. **Update the ledger in the same edit as the body.** A new claim without an entry, or
   an entry left behind by a deleted claim, are the two ways these drift apart.
4. **Decide whether the recorded revision moves.** A node carries one snapshot, so
   moving it makes a statement about the whole ledger, not just the claims you touched.
   - Re-verified every claim at `HEAD` → move it.
   - Re-verified some → move it only if the rest still hold at `HEAD` too. Check, do
     not assume.
   - Re-verified nothing → leave it.
   - **Every cited source byte-identical between the recorded revision and `HEAD`** →
     leave it. Checking a claim at either point was the same act, so moving the
     revision would assert a re-check that added nothing. This case is why the rule is
     stated as four branches and not as "bump on every edit": that shorter rule was in
     an earlier draft and contradicted what this very node does.

     **Establishing that requires re-verification, not a diff.** A `git diff` can tell
     you that some *files* did not move; it cannot tell you a claim still holds, and it
     cannot speak to a citation that names no file at all. See *Checking whether cited
     files moved* below for what the command does and does not establish. Only the
     file-naming citations in the ledger are in its reach. The **provenance entry
     recording the revision** is itself a mandatory commit citation on every node — it
     is not one of the substantive claims this branch is deciding whether to re-verify,
     so it does not count against the check below. If any *other* citation is a graph
     edge, tool result, commit or URL, this branch is not available to you — re-verify
     those claims or leave the revision alone.
5. **Leave the `id` alone.** Always.
6. **Run the check.**

## Retiring a node

Retiring is a **status change, not a deletion**. The file stays, so the checker keeps
loading the node and inbound relationships keep resolving. Nothing here is enforced by
tooling — a retired node with stale inbound edges validates exactly like a healthy one.

1. **Set `status` to the retired value** defined in `node.schema.json`. Do not delete
   the file. Deleting it is what breaks inbound relationships: a
   `relationships[].target` naming an id nothing carries is a hard error, and every
   node pointing at the deleted one starts failing.
2. **Find what points at it.** Search the corpus for the node's `id`. Those edges will
   still resolve — that is the problem, not the safety net. Readers and generated
   views will keep being sent to a node that has stopped being current, and no check
   will ever mention it.
3. **Decide what replaces it, and say so in the vocabulary.** If another node takes
   over the subject, that node declares `supersedes` targeting the retired id — the
   type exists in `relationships.schema.json` for exactly this. Repointing the inbound
   edges from step 2 at the replacement is a judgement call: repoint the ones that
   wanted the subject, leave the ones that genuinely meant the retired node.
4. **If nothing replaces it**, say that in the retired node's body. A reader arriving
   from an old link needs to be told the subject is gone, not left guessing.
5. **Never reuse or rename the `id`.** A retired id stays spent — renaming breaks
   generated views that resolve through it, and reuse silently points old references
   at new content.
6. **Record why**, in the body and in the ledger, at the revision you checked.
7. **Run the check.** It will pass whether or not you did steps 2-4 correctly. That is
   the point of doing them deliberately.

## Scope and omissions

**This document covers** how to create, update and retire one corpus node, what the
front-matter contract is and where it lives, how to classify and cite evidence, and
what the deterministic check does and does not establish.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-type standards — naming, identifiers, linking, provenance, status, taxonomy, diagrams, evidence | somewhere in #1307–#1351 |
| Templates for each node type — concept, component, capability, interface, flow, policy, procedure, runbook, reference, specification, and the rest | somewhere in #1307–#1351 |

**That range is a range, not a mapping.** It is 45 issues across those subjects, and this
table does **not** say which number owns which subject. Look the subject up
(`gh issue list --repo launchpad-26/buzz --search "corpus standard for <subject>"`) rather
than citing this table for a subject-to-issue pairing — an agent authoring a sibling node
did exactly that and produced nine invented mappings, which is the "FACT cited to a file
that does not discuss the claim" failure this document warns about two sections up.
| How generated artifacts prove their provenance, and the exception process for them | #1316 |
| Encoding ADR-0029's claim-type classification and the flagged state in the schema and checker | #1410 |
| The human-facing entry point to the corpus | #639 |
| Line numbers in citations not being verified against file length | #1459 |

Until the standards land there is no per-type template to follow: write the node
against `node.schema.json` and the rules above, and expect a later task to reshape it.

**No `relationships` in this node's own front matter.** There is no other node to point
at, and a `relationships[].target` naming an id no node carries is a hard error. The
absence is deliberate; the first sibling node is the moment to revisit it.

**Checking whether cited files moved — and what that does not establish.** Run

```
git diff --name-only <recorded-sha> -- <the normalized file paths in the ledger>
```

Empty output means **those files** are unchanged between the recorded revision and
`HEAD`. That is all it means. It is a narrowing step, not a certification: only
re-verifying a claim against its source establishes that the claim still holds.

Two limits decide which citations the command can even be pointed at, and both come
from `CONTRACT.md` §3's six shapes:

- **Normalize first.** A file citation may carry a position — `path:1077` or
  `path:219-221`. Those are not pathspecs. Strip the trailing `:<line>` or
  `:<start>-<end>` before passing the path to `git diff`, or git resolves nothing and
  reports empty output for a file it never looked at. **An empty result from a
  malformed pathspec is indistinguishable from an empty result from an unchanged
  file**, which is what makes this the dangerous one.
- **Only three of the six shapes name a file.** Bare path, file line and file range are
  in reach. **Graph edge, tool result and commit are not**, and neither are the two URL
  forms the validator recognises beyond §3. Exclude them explicitly rather than
  silently — a claim resting on a tool result or an external URL is untouched by any
  `git diff`, so its status after the command is exactly what it was before: unknown.

So the honest reading is one sentence: *the file-naming citations I normalized and
passed are unchanged; every other claim in this ledger is unverified by this command.*
Do not take the narrowing on this document's word either — run it, and read what it
covered.

**What the corpus has NOT settled about revisions.** Whether a recorded revision may
stay put while a node is edited, and what an author must do when only some claims are
re-verified, is **#1321's** to decide (`document corpus standard for provenance`,
unlanded). Until it lands, *Updating a node* above states this document's working
practice, not a corpus-wide rule — three independent review passes rejected earlier
attempts to present it as one, on the grounds that no authorized source establishes it.
When #1321 lands, that section defers to it.

**Expected but not verified when this node was written**, per the rule in *Creating a
node* step 3:

- **No agent harness was tested reading this file as its resolved `AGENTS.md`.** The
  front matter is harmless to the checker, and to `preflight_core.py`, which resolves
  the path without parsing content. Whether it degrades the file for a harness that
  *reads* it as instructions is unknown.
- **The relationship enums in `node.schema.json` and `relationships.schema.json` were
  not checked against each other.** `relationships.schema.json` was read for the
  `supersedes` directionality this node cites. `node.schema.json` states that a test
  guards the two enum lists against drifting apart; that test was not run, so a reader
  relying on the two agreeing is relying on that guard rather than on a check made here.

**This file is read twice.** It is a corpus node, validated like any other; it is also
resolved as the nearest `AGENTS.md` for every change under `launchpad/docs/corpus/`,
so an agent working anywhere in this subtree is handed it as governing instructions.
Write it to be followed, not merely to be accurate.
