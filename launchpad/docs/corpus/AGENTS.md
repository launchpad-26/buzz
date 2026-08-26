---
id: corpus-agents
type: agent
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 0052f5a7820ca4ca261efa233feb8bb53858ade6."
    entry_class: FACT
    evidence:
      - "commit 0052f5a7820ca4ca261efa233feb8bb53858ade6"
  - statement: "Markdown with YAML front matter is the one canonical authored representation of a corpus node; every other serialization is a generated derived view."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "A node's front matter is validated against node.schema.json, which requires id, type, status, origin, audiences and evidence, and permits no field outside that set."
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
  - statement: "Every change under launchpad/docs/corpus is gated in CI by the corpus validate workflow."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
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
file and in `schema/README.md`; they are not repeated here, because a second copy
drifts silently — the checker never reads this document's prose, so a stale copy
would stay green forever.

**`id` is permanent.** Kebab-case, assigned once, never renamed. Generated views
derive from it reproducibly, so renaming an id is a migration, not an edit.

**Relationships are optional and must resolve.** A `relationships[].target` naming an
id no node in the corpus carries is a hard error. A node with no sibling to point at
correctly declares none.

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
in `node.schema.json` and `schema/README.md`, and are not restated here.

What the classes are *for* is the part that is easy to get wrong:

- **`FACT`** — you opened the cited source and it says so. Not "a source exists that
  probably says so."
- **`INFERENCE`** — you reasoned to it from evidence. Reasoning is not fact, however
  good it is.
- **`TEAM_KNOWLEDGE`** — a person told you, and nothing corroborates it. This is the
  class that exists for uncorroborated statements; using it honestly is better than
  promoting a recollection to `FACT`.

When two sources disagree, do not average them and do not pick the newer one. For how
the system **currently behaves**, executable evidence — code, config, schema, passing
tests — outranks documentation and history. For **intended or authorized** behaviour,
accepted decisions outrank code that has drifted from them. When two sources of the
*same* claim type conflict, stop: record the conflict and leave the node flagged for a
human rather than resolving it yourself. `ADR-0029` is the full rule.

### What the checker does with each citation shape

`CONTRACT.md` §3 defines the six shapes. What `validate.py` does with them is not
documented anywhere else, so it is here:

| Shape | Checker's verdict |
|---|---|
| Bare repository path | Resolved; must be a real **file** inside the repo. A directory fails. |
| Path with a line or line range | Resolved as a path. **The line number is not checked** — see below. |
| GitHub file link | Must be pinned to a full 40-character commit SHA, and must name a file. |
| Commit reference | Reported `UNVERIFIED`. Nothing on disk to open. |
| Graph edge | Reported `UNVERIFIED`. |
| Tool result | Reported `UNVERIFIED`. |

Anything matching **no** known shape is a hard error, not an `UNVERIFIED` notice.

### Three things a passing run does not mean

**1. It does not mean a citation supports its claim.** Checking is *structural*. The
checker confirms a path resolves to a real file; it never opens that file and compares
it against your `statement`. A `FACT` citing a real file that says nothing on the
subject passes cleanly. Only a human reading the source establishes a `FACT`.

**2. `UNVERIFIED` is not a pass.** Those notices are printed, never fatal, and they
mean the checker recognised the shape and could not open it. A `FACT` resting only on
`UNVERIFIED` citations has not been checked by anything — open the source and keep the
class, or change the class.

**3. A line number is not verified.** `Justfile:999999` is accepted against a
1005-line file (#1459). Prefer a bare path until that is fixed; a position that has
silently drifted is worse than no position, because it looks precise.

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
   expected to verify and could not.
4. **Choose the `id`.** Kebab-case, and permanent from this moment. Pick something that
   describes the idea, not where the file currently sits.
5. **Create the file** anywhere under `launchpad/docs/corpus/` except `schema/`.
6. **Write the front matter** against `node.schema.json`. Include a commit citation for
   the revision from step 3 — the ledger is the only schema-legal place for it.
7. **Write one `evidence` entry per substantive claim** you intend to make. Classify
   honestly; open every source you call a `FACT`.
8. **Write the body**, structured for lookup. State what the node does not cover.
9. **Add relationships only to nodes that exist.** A target no node carries is a hard
   error. None is a valid answer.
10. **Run the check.** Fix what it names, and re-run until it exits 0.

## Updating a node

1. **Confirm the change belongs in this node.** New idea, not new detail about the
   existing one? That is a new node.
2. **Re-record the revision you are checking against.** `git rev-parse HEAD` now, not
   the one already in the ledger.
3. **Re-verify the claims you are touching** against sources at that revision. A claim
   whose source moved is not still a `FACT` because it used to be.
4. **Update the ledger in the same edit as the body.** A new claim without an entry, or
   an entry left behind by a deleted claim, are the two ways these drift apart.
5. **Update the recorded revision** to the one from step 2.
6. **Leave the `id` alone.** Always.
7. **Run the check.**

## Retiring a node

1. **Find what points at it.** Search the corpus for the node's `id`; any node with a
   relationship targeting it needs handling first, or the corpus is left with a
   relationship that no longer resolves.
2. **Decide what replaces it.** If another node takes over the subject, say so in that
   node — a reader arriving at a retired node needs somewhere to go.
3. **Set `status` to the retired value** defined in `node.schema.json`. Do not delete
   the file: generated views and inbound links resolve through the id, and deleting it
   breaks them silently.
4. **Never reuse or rename the `id`.** A retired id stays spent.
5. **Record why**, in the body and in the ledger, at the revision you checked.
6. **Run the check.**

## Scope and omissions
