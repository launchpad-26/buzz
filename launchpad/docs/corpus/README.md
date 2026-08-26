---
id: corpus-readme
type: governance
status: active
origin: launchpad
audiences:
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a1e8bbcd0846321c6f6684acfe551096da4d974a."
    entry_class: FACT
    evidence:
      - "commit a1e8bbcd0846321c6f6684acfe551096da4d974a"
  - statement: "Markdown with YAML front matter is the one canonical authored representation of a corpus node; every other serialization is a generated derived view."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "Front matter carries the machine-checkable fields and the Markdown body carries the human-readable prose."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "One node is one independently maintainable idea, so a second concept, contract or procedure discovered while writing becomes its own node rather than another section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The corpus root is launchpad/docs/corpus, and validate.py is the deterministic check that governs it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "Justfile"
  - statement: "Exit status 0 is a pass and exit status 1 means at least one error, with every error naming the node it came from; just corpus-validate runs the same command but needs the Hermit environment activated first."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The schema/ subtree is excluded from validation because it is the schema's own testing infrastructure rather than corpus content, so a node placed there is never checked."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A node's front matter is validated against node.schema.json, which requires id, type, status, origin, audiences and evidence, additionally permits relationships, and rejects any field beyond those seven."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "AGENTS.md is the corpus's agent-facing instruction node, carrying the create, update and retire procedures, and it is also resolved as the nearest AGENTS.md for every change under launchpad/docs/corpus."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/scripts/preflight_core.py"
  - statement: "The checker's own discovery function enumerates the corpus's authored nodes, so the current set can be listed on demand rather than read from a count written here."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The corpus schema was authored under issue #622, whose parent feature is #605 and whose parent PRD is #602."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "AGENTS.md records the per-type standards and templates as owned by issues #1307-#1351 with none of them merged yet, and names #1316, #1410 and #1459 as the owners of three further named gaps."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Changes under launchpad/docs/corpus are validated in CI on pull requests and on pushes to the launchpad branch, running the same validator command as a local run."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "UNVERIFIED notices are printed on every run and are never fatal; a run that reports them still exits 0."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Citation checking is structural: the validator confirms a cited path resolves to a real file inside the repository, never that the file supports the statement it sits under."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A line number in a citation is checked only for internal consistency, never against the cited file's actual length."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The corpus's audit mechanism is the human-read pull-request diff, and preserving that is why ADR-0028 chose Markdown over a machine-readable record format."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "A relationship whose target matches no loaded node's id is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The schema defines audiences as who the node is written for, and constrains it to a closed enum of agent, developer, operator and reviewer."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node therefore omits agent from its audiences, because the node authored for agents is AGENTS.md and this one only redirects there."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.75
  - statement: "The type enum contains no reference or index member, so governance is the closest true fit for a node whose subject is the corpus's own rules and boundaries."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
---

# The Buzz documentation corpus

The canonical, evidence-backed documentation of the Buzz system, written as one
node per idea. This page is the door: it says what the corpus is, what is in it
today, where each rule actually lives, and how the whole thing is checked.

It is a map, not a manual. **No rule is *owned* here.** A door has to orient the
person standing in it, so a few rules are summarised below in one or two lines —
but every one of them names the file that owns it, and that file wins on any
disagreement. The checker never reads this page's prose, so a summary here can go
stale without anything turning red; treat what you read on this page as a pointer,
never as the authority.

**If you are an agent, you want
[`launchpad/docs/corpus/AGENTS.md`](AGENTS.md), not this page.** That node carries
the create, update and retire procedures, and it is what an agent harness resolves
as the nearest `AGENTS.md` for any change under this directory.

## What a node is

One file is one node: a Markdown file with YAML front matter. That is the single
canonical authored representation of everything in the corpus — JSON, indexes and
graph serializations are generated derived views, never hand-authored. The front
matter carries the machine-checkable fields and the body carries the prose.

One node is one independently maintainable idea. A second concept, contract or
procedure discovered while writing becomes its own node, not another section.

## What is in the corpus today

Ask the checker rather than trusting a count written on this page — it is the same
discovery the validator itself runs, and it cannot go stale:

```bash
python3 -c "import sys; sys.path.insert(0, 'launchpad/project-intelligence/corpus'); \
import validate as v; \
print(*(p.name for p in v.discover_markdown_files(v.repo_root() / 'launchpad/docs/corpus')), sep='\n')"
```

Two kinds of thing live under the corpus root, and the difference matters:

| Path | What it is | A validated node? |
|---|---|---|
| [`launchpad/docs/corpus/AGENTS.md`](AGENTS.md) | The agent-facing instruction node — how to create, update and retire a node | Yes |
| [`launchpad/docs/corpus/README.md`](README.md) | This page — the human-facing entry point | Yes |
| [`launchpad/docs/corpus/schema/`](schema/README.md) | The front-matter contract, its fixtures and its tests | **No** — deliberately excluded from the scan |

**This is a corpus under construction, and the sparseness is the current state
rather than an omission.** The per-type standards and templates are owned by issues
#1307–#1351, none of which had merged when this page was written, and #1316, #1410
and #1459 own three further named gaps. Expect the list above to grow, and expect
the shape of a node to be tightened by standards that do not exist yet.

## Where each rule lives

Every row is the authoritative source for its subject. This page owns none of
them — go to the file, not to a summary of it.

| If you want | Read |
|---|---|
| To create, update or retire a node | [`launchpad/docs/corpus/AGENTS.md`](AGENTS.md) |
| The front-matter contract — fields, enums, conditional rules | [`launchpad/docs/corpus/schema/node.schema.json`](schema/node.schema.json) |
| Those fields explained in prose | [`launchpad/docs/corpus/schema/README.md`](schema/README.md) |
| The relationship types and their directionality | [`launchpad/docs/corpus/schema/relationships.schema.json`](schema/relationships.schema.json) |
| To add a value to a closed enum | [`launchpad/docs/corpus/schema/COMPATIBILITY.md`](schema/COMPATIBILITY.md) |
| Why Markdown with front matter is the canonical form | [`launchpad/decisions/ADR-0028-corpus-canonical-representation.md`](../../decisions/ADR-0028-corpus-canonical-representation.md) |
| How to rank evidence when two sources disagree | [`launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`](../../decisions/ADR-0029-corpus-evidence-precedence.md) |
| The six shapes a citation may take | [`launchpad/project-intelligence/CONTRACT.md`](../../project-intelligence/CONTRACT.md) §3 |
| What the checker actually enforces | [`launchpad/project-intelligence/corpus/validate.py`](../../project-intelligence/corpus/validate.py) |
| Where the check runs in CI | [`.github/workflows/launchpad-corpus-validate.yml`](../../../.github/workflows/launchpad-corpus-validate.yml) |

If this page and any of those disagree, **they win** — this one has drifted and
should be fixed.

## How the corpus is checked

One command, run from the repository root:

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

Exit status 0 is a pass. Exit status 1 means at least one error, and every error
names the node it came from. `just corpus-validate` runs exactly that command, but
needs the Hermit environment activated first (`. ./bin/activate-hermit`); the
interpreter form above does not.

The same command runs in CI on every pull request touching
`launchpad/docs/corpus/**` and on every push of such a change to the `launchpad`
branch, so a local failure is a CI failure.

`UNVERIFIED` notices are printed on every run and are **never fatal** — the run can
report them and still exit 0. They mean the checker recognised a citation's shape
and had nothing on disk to open, which is not the same as having checked it.

### What a passing run does not establish

A pass is a structural result, not an editorial one. It does not mean a citation
supports the claim it sits under; it does not mean an `UNVERIFIED` citation was
checked; and it does not mean a line number in a citation points anywhere real.
That is the summary. What each limit means, and what a reviewer has to hold in
place of the check, is owned by
[`launchpad/docs/corpus/AGENTS.md`](AGENTS.md) under *Three things a passing run
does not mean* — read it there before reviewing a corpus change.

**This matters most at review time.** The corpus is audited in the pull-request
diff a human reads, not after the fact — that is the enforcement mechanism
[ADR-0028](../../decisions/ADR-0028-corpus-canonical-representation.md) chose this
file format to preserve. A green check is the floor, not the verdict.

## Scope and omissions

**This node covers** what the corpus is, what it contains today, which file owns
each rule, and how the corpus is checked.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How to create, update or retire a node | [`launchpad/docs/corpus/AGENTS.md`](AGENTS.md) |
| Per-type standards and the template for each node type | #1307–#1351, none merged yet |
| How generated artifacts prove their provenance | #1316 |
| Encoding ADR-0029's claim-type classification in the schema and checker | #1410 |
| Line numbers in citations not being verified against file length | #1459 |

**This node declares no `relationships`.** A `relationships[].target` naming an id
no loaded node carries is a hard validation error, and almost every node this page
will eventually point at does not exist yet. An edge to `corpus-agents` would
resolve, so the absence is a choice rather than a constraint: this node waits and
takes its edges in one pass once the standards have landed, instead of accumulating
them one at a time against a set that is still changing shape.

**That is this node's own decision, not a rule for the corpus.** Whether nodes
authored before the standard set lands should declare edges as they go is not
settled anywhere, and this page has no authority to settle it — the per-type
standards owned by #1307–#1351 do.

**`agent` is deliberately absent from `audiences`.** The schema defines that field
as who the node is written *for*, and this node is written for the humans arriving at
the corpus — a developer looking for the rules and a reviewer judging a corpus pull
request. What it does for an agent is hand it to
[`AGENTS.md`](AGENTS.md), which is the node authored for agents. Listing `agent`
here would make an audience-filtered view return two nodes to a cold-start agent, one
of which only redirects to the other. This is the corpus's first `developer` audience
and its first deliberate audience *exclusion*; a reader who thinks `audiences` should
name everyone who might read a node rather than everyone it addresses would add it.

**`type: governance` is the closest true fit, not an exact one.** The enum carries no
`reference` or `index` member, and this node's subject is the corpus's own rules and
boundaries, which is what makes `governance` the nearest. If a later standard
introduces a taxonomy that fits an entry point better, this node's `type` is a
candidate for revision. Its `id` is not — ids are permanent.

**Expected but not verified when this node was written:**

- **How this file renders on GitHub.** It is a `README.md`, so GitHub displays it
  automatically when someone opens the corpus directory — with YAML front matter at
  the top that a plain reader did not ask for. Whether that renders as a table, as
  raw text, or is hidden was not checked, and it is a real question for a
  human-facing entry point specifically. The front matter is not optional: this path
  is scanned by the checker and an unvalidated node here would be worse.
- **No agent harness was tested to confirm it prefers `AGENTS.md` over this file.**
  The redirect at the top of this page is written for a human reader. Whether a
  harness that globs the directory reads both is unknown.
