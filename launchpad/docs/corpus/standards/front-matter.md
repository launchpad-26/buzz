---
id: corpus-standard-front-matter
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109."
    entry_class: FACT
    evidence:
      - "commit ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109"
  - statement: "Front matter is the machine-checkable half of a corpus node and the Markdown body is the prose half, because Markdown with YAML front matter is the one canonical authored representation."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "node.schema.json is the contract for which fields exist, which are required, what each accepts, and which combinations are legal; schema/README.md is its prose explanation."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "The field set is closed: node.schema.json sets additionalProperties to false, so a key the schema does not define is a hard error rather than an ignored extra."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "There is no provenance field, so the revision a node was checked against belongs in the evidence ledger as a commit citation."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A schema violation is reported using the schema's own constraint and never the offending value, so the message says what was demanded without naming which key broke the closed field set."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The checker splits a node into front matter and body and binds the body to a name it never reads again, so nothing in body prose is ever checked against anything."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Front matter must begin on the file's first line, because the checker requires the text to start with the opening delimiter rather than searching for it, which rejects both a leading blank line and a byte-order mark."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "An unquoted scalar is exposed to two YAML behaviours that are not alike: implicit typing is caught by the schema's type and enum constraints and exits non-zero, while comment stripping is silent and passes, so quoting free text guards against the second rather than the first."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "validate.py('id: 2026-08-26' unquoted) -> exit 1, schema violation at id; same value quoted -> exit 0"
  - statement: "Each rule this node states as enforced was confirmed by a node that breaks it and exits non-zero, and each rule it states as unenforced by a node that violates it and exits zero; the sole partial case is quoting, which is called out where it is stated."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "validate.py(--root <one fixture per rule, both directions>) -> exits as this node states"
  - statement: "Nothing requires a commit citation to be present: a node whose ledger contains no commit citation anywhere validates clean, so recording the revision is a convention a reviewer holds rather than a rule the checker holds."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The checker resolves a relationship target only against the nodes loaded by the run that is executing, so it cannot establish that a target exists on the branch being merged into."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The split takes at most two delimiters, so the second delimiter line in the file closes the front matter and every key after it is body text that is parsed by nothing and reported by nothing."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A node whose front matter has no closing delimiter is rejected, but the message is a Python unpacking error rather than a description of the missing delimiter."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Front matter that parses as valid YAML but is not a mapping is caught before schema validation and named as such."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A repeated key is a hard error that the checker detects deliberately, because YAML itself resolves a repeated key to the last one silently."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A repeated-key message names the key only when that key is a property node.schema.json defines, and otherwise gives position alone."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Front matter is handed to PyYAML's safe loader, so every YAML scalar rule -- comment stripping, implicit typing of unquoted scalars -- applies to a node's field values before the schema ever sees them."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "An unquoted value whose text contains a space followed by a number sign loses everything from that point as a YAML comment, and the truncated remainder still satisfies the schema, so the run passes."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "yaml.safe_load('provided_by: launchpad-26/buzz #1315 note') -> {'provided_by': 'launchpad-26/buzz'}"
  - statement: "Field order carries no meaning, because front matter is loaded into a mapping and validated as one."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A relationship target that matches no loaded node's id is a hard error, and the set of loaded nodes is whatever exists where the checker runs rather than where the author works."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The merge target now carries loadable corpus nodes, so the original reason this node declared no relationships -- that no edge could resolve there -- has expired; the edges are deferred to launchpad-26/buzz#1489, the batch-wide backfill pass that owns them, rather than declared here."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "git.ls_tree('origin/launchpad', 'launchpad/docs/corpus') -> AGENTS.md, README.md, standards/confidence.md, standards/decision-references.md, plus the excluded schema/ subtree"
  - statement: "A bare-path citation carries the same merge-order hazard as a relationship target: it is resolved against the tree the run sees, so a citation to a file that exists only on the authoring branch passes locally and becomes a hard error once merged."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "validate.py(clean origin/launchpad tree + this node citing the unmerged AGENTS.md) -> exit 1, 5 citations do not resolve"
  - statement: "Nothing in the repository reads the audiences field: the schema declares it, the schema's own tests exercise it, and the checker never looks at it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.9
  - statement: "The same command enforces this contract locally and in CI, running on pull requests and on pushes to the launchpad branch whenever anything under the corpus root changes."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "Widening a closed field -- adding a value to an enum -- is an additive change, while removing a field or a value or narrowing a type is breaking and requires a dated compatibility entry plus a re-validation pass in the same pull request."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "A citation naming a line is checked for its path only, so a position that has silently moved is never caught."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Edge kinds and each kind's directionality are defined in relationships.schema.json, which node.schema.json inlines a copy of rather than referencing across files."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Evidence precedence is contextual by claim type, and two authoritative sources of the same claim type in conflict leave the node marked for a human rather than resolved by its author."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Issue #1315 requires this node to state the scope and authority of the policy, to separate requirements from guidance, and to define enforcement and an exception process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1315 definition of done"
  - statement: "The per-field subjects this node defers are owned by issues #1317 identifiers, #1323 status, #1311 deprecation, #1324 taxonomy, #1309 confidence, #1314 evidence, #1308 code references and #1316 generated content, each read from the issue's own title."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz issues #1308, #1309, #1311, #1314, #1316, #1317, #1323, #1324 (titles read 2026-08-26)"
  - statement: "The corpus create procedure covers the merge-order hazard for relationship targets but not for bare-path citations, and that omission has already produced a defect in a sibling node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1488 defect B, and #1473 which records it occurring (titles read 2026-08-27)"
---

# Front matter

What a corpus node's front matter is for, what it must satisfy, and how it fails.
Look up the section you need.

**This node does not list the fields, their accepted values, or the rules between
them.** Those live in the schema, and a second copy in prose would drift without
anything noticing — the checker reads front matter and discards the body, so a stale
list here would stay green forever. Every lookup below points at the file that holds
the answer.

| For | Read |
|---|---|
| Which fields exist, which are required, what each accepts, which combinations are legal, and what each field is *for* | `launchpad/docs/corpus/schema/node.schema.json` |
| The same contract in prose | `launchpad/docs/corpus/schema/README.md` |
| Widening or narrowing a closed field | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| Edge kinds and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node, step by step | `launchpad/docs/corpus/AGENTS.md` |
| What the checker actually does | `launchpad/project-intelligence/corpus/validate.py` |

If this node and any of those disagree, **they win**. This one has drifted.

## Scope and authority

This node is policy for the **front matter block** of a corpus node: the delimiters
that bound it, the YAML inside them, and what a passing run does and does not
establish about it.

Its authority is derived, not original. ADR-0028 decided that a node is Markdown with
YAML front matter; `node.schema.json` is the contract that front matter satisfies; and
`validate.py` is the one command that enforces it. This node adds only what none of
those can say about themselves — what the fields are *for*, and how the block fails in
practice.

**It does not own the fields' meanings.** Each of those is a separate node's subject:

| Subject | Owner |
|---|---|
| How an `id` is named | #1317 — *corpus standard for identifiers* |
| What each `status` value means | #1323 — *for status* |
| Retiring a node, and what that does to its status | #1311 — *for deprecation* |
| Which `type` a node should carry | #1324 — *for taxonomy* |
| What a `confidence` number means | #1309 — *for confidence* |
| The evidence ledger's own contract | #1314 — *for evidence* |
| Citation shapes | #1308 — *for code references* |
| Provenance for generated artifacts | #1316 — *for generated content* |

Each row names the issue's own title, checked against the issue rather than guessed
from a numbering range — inventing a subject-to-issue mapping is a failure `AGENTS.md`
records having already happened once, nine times over.

Where this node touches one of those — the ledger holds the revision, a citation's
line number is unchecked — it states the mechanical consequence for the front-matter
block and points at the owner for the meaning.

## What front matter is for

A node has two halves and they are not checked alike.

**Front matter is the checked half.** It is parsed, validated against the schema, and
cross-checked against every other node — duplicate ids, unresolved edges, citations
that name no real file. Anything a tool must be able to rely on belongs here.

**The body is the unchecked half.** The checker splits the file, keeps the front
matter, and binds the body to a name it never reads again. No claim in prose is
compared against anything.

That asymmetry is the reason for the rule at the top of this node. Prose that
*duplicates* front matter is prose that can contradict it silently. Prose that
*explains* it cannot.

### What each field is for

**Read it from the schema.** Every property in `node.schema.json` carries a
`description`, and those descriptions are what each field is for — not a summary of
them kept here. A field's purpose is the one thing about front matter that already
lives in the checked half, beside the field it describes, where it cannot drift away
from what is enforced. Restating them here would produce exactly the silent
contradiction the rule at the top of this node exists to prevent.

The one fact about a field that this node does state, because no schema `description`
can, is the mechanical consequence of the checked/unchecked split for the field this
node itself leaves out: see *No `relationships` in this node's own front matter* under
*Scope and omissions*.

## Requirements

These are MUST, and **each was confirmed by building a node that breaks it and watching
the checker exit non-zero.** A violation fails CI and blocks the change.

Three rules that read like requirements are deliberately *not* here, because the checker
does not hold them. They are in *Guidance*, and why that line is drawn so sharply is in
*Where the line actually falls*.

1. **The file MUST begin with the opening delimiter on line 1.** The checker tests that
   the text *starts with* it; it does not search for it. A blank line or a byte-order
   mark before it is rejected as having no front matter at all — both cases were run,
   both rejected with `no leading '---' frontmatter delimiter`.
2. **The block MUST be closed.** An unterminated block is rejected, though the message
   is a Python unpacking error rather than a description of the problem — see
   *Delimiters*.
3. **Front matter MUST be a YAML mapping.** A sequence or a bare scalar is valid YAML
   and is rejected before schema validation.
4. **No key MUST appear twice.** YAML would resolve a repeat to the last value
   silently; the checker looks for repeats on purpose and fails the run.
5. **Every field MUST be one the schema defines, and every required field MUST be
   present.** The field set is closed. A key the schema does not know is an error, not
   an ignored extra.
6. **A declared `relationships` target MUST resolve to a node the checker loaded.** An
   unresolvable target is a hard error. Note the scope — *loaded where the run happens*;
   guidance item 5 is the half of this the checker cannot hold. Declaring no
   relationships at all is always valid.

## Guidance

These are SHOULD. **No check holds any of them completely**, which is precisely why they
are written down: they are the conventions a reviewer has to hold. For items 2 to 8 the
checker holds nothing at all — each was confirmed by building a node that violates it and
watching the run pass clean. **Item 1 is a partial exception and says so.**

1. **Quote values that carry free text** — a `statement`, a `provided_by`, a citation.
   An unquoted scalar is exposed to two YAML behaviours, and they are *not* alike:

   - **Implicit typing is usually caught, loudly.** An unquoted value that looks like a
     date or a boolean stops being a string, and the schema's `type` and `enum`
     constraints reject it. This is the half a check does hold — an unquoted
     date-shaped `id` exits non-zero — so quoting is protection against a confusing
     message rather than against a silent pass. The message is confusing: a coerced
     `id` is no longer a string, so the error falls back to naming the file path
     instead of the node.
   - **Comment stripping is silent, and nothing catches it.** A space followed by a
     number sign begins a comment; the remainder of the value is discarded, the
     truncated string still satisfies the schema, and the run passes. This half is why
     the item is here.

   **Enum keywords are exempt and should stay bare.** `type`, `status` and `origin`
   values, and the members of `audiences`, cannot be coerced into another type or
   truncated by a number sign. Every node in the corpus leaves them unquoted, including
   this one — quoting them would be harmless but would diverge from every existing node
   for no gain. See *YAML hazards*.
2. **Do not put a delimiter line inside the front-matter block.** This reads like a
   requirement and is not one. A stray delimiter ends the block, and every field after
   it becomes body text that nothing parses and nothing reports — including a
   `relationships` block whose target resolves nowhere, which is otherwise requirement 6
   and a hard error. A node like that **exits 0**. See *Delimiters*; filed as #1482.
3. **Record the revision the node was checked at as a commit citation in the `evidence`
   ledger.** There is no `provenance` field, so the ledger is the only place the schema
   permits it — but nothing requires the citation to be present. A node carrying no
   commit citation anywhere validates clean; only a reader will notice it missing.
4. **State in the body why `relationships` is absent**, when it is. "Nothing to point
   at" stops being true the moment a second node merges, and a justification copied
   from a node written earlier is how two sibling nodes have already shipped a false
   one. Give the reason that is true today — usually merge order.
5. **Check every reference against the branch you are merging into**, not the one you
   are working on. This applies to *two* kinds of reference, and the second is the one
   that gets missed:
   - **Relationship targets.** Requirement 6 is enforced only against the nodes present
     where the checker runs, and it cannot see another branch.
   - **Bare-path citations in the ledger.** Identical hazard, same cause. A citation is
     resolved against the tree the run sees, so one naming a file that exists only on
     your branch resolves for you and becomes a hard error for whoever merges.

   Both pass locally and fail after merge, which is the worst time to find out. If your
   branch is stacked on another unmerged branch, everything that branch adds is invisible
   to the merge target — test it, do not reason about it:

   ```bash
   git archive origin/<merge-target> | tar -x -C <tmp> && git -C <tmp> init -q .
   cp <your node> <tmp>/launchpad/docs/corpus/<dir>/ \
     && (cd <tmp> && python3 launchpad/project-intelligence/corpus/validate.py)
   ```

   This node cited a file from its own unmerged base and passed every local check; the
   command above exited 1 with five unresolvable citations. `AGENTS.md`'s create
   procedure covers the relationship half of this hazard and not the citation half —
   the gap is #1488, and #1473 is it happening.
6. **Prefer a bare path to a path with a line number** in citations. The path is opened
   and checked; the line number is not compared against the file at all, so a position
   that has drifted looks precise and is wrong (#1459).
7. **Keep the ledger to one commit-only entry** — the revision. A second claim resting
   on nothing but a commit id has been checked by nothing, and produces only a
   non-fatal notice. No check will raise it.
8. **Order fields for a reader.** Order carries no meaning to the parser; it is
   entirely for the human reading the PR diff, which ADR-0028 makes the corpus's actual
   audit mechanism.

### Where the line actually falls

The split above is not stylistic, and it was got wrong twice while writing this node —
in both directions. Both errors are recorded here because the second one is the more
instructive.

**Rules asserted as enforced that are not.** Items 2, 3 and 5 are ones an author would
reasonably assume CI holds. An earlier revision listed all three as requirements. Each
moved here only after a reviewer built the violating node and watched it pass.

**A rule asserted as unenforced that partly is.** The correction above then over-swung:
this section claimed *nothing* in Guidance was enforced, which made item 1 false, because
an unquoted date-shaped `id` does fail. One fix opened its neighbour — which is the
failure this repository sees most often, and it survived two review rounds before a
third caught it.

The lesson is not "check harder". It is that **enforcement is a property of the checker,
never of how important a rule sounds** — and that intuition is wrong in both directions,
so a claim that something *is* enforced needs a failing run behind it exactly as much as
a claim that something is not. Write the node that breaks the rule and run the checker.
The wider point stands underneath: **a green run is evidence about structure, not about
correctness.**

## Delimiters

The checker splits the file on the delimiter, taking **at most two**. The first opens
the block, the second closes it, and everything after is body.

That has a consequence worth stating on its own, because it is silent and it passes:

> **A delimiter line inside the front matter ends it.** Every key after that line
> becomes body text. It is parsed by nothing, validated by nothing, and reported by
> nothing.

Placing a `relationships` block after such a line — with a target no node carries,
which is otherwise a hard error — produces a **clean run**. The fields are simply
gone. Nothing distinguishes this from a node that never declared them.

Two related failures are noisy rather than silent, and one of them is confusing:

| What you wrote | What happens |
|---|---|
| Anything before the opening delimiter | Rejected: no front matter delimiter found |
| No closing delimiter at all | Rejected, but the message is a Python unpacking error about expecting three values and getting two. It names the file, so it is actionable; it does not mention the delimiter (#1483). |

## YAML hazards

Front matter is handed to PyYAML's safe loader. Every YAML rule applies to a node's
values before the schema sees them, and the schema then judges whatever YAML produced
— not what you typed.

**Implicit typing.** An unquoted scalar may not stay a string. A value that looks like
a date becomes a date; a value that looks like a boolean becomes a boolean. The schema
catches both, but it reports them oddly: a coerced value fails a `type` or `enum`
constraint, and because a coerced `id` is no longer a string, the error falls back to
naming the **file path** instead of the node.

**Comment stripping — the silent one.** A space followed by a number sign begins a
comment. In an unquoted value, everything from there is discarded:

```
provided_by: launchpad-26/buzz #1315 definition of done
```

parses to `launchpad-26/buzz`. The remainder is gone, the truncated string is still a
non-empty string, the schema is satisfied, and **the run passes clean**. Quoting the
value is the whole fix.

**What the error message will and will not tell you.** A schema violation is reported
using the schema's own constraint and never the value that broke it, so that a
malformed node cannot print sensitive content into CI logs. The practical cost: when
the closed field set rejects a key, the message says the constraint failed and does
**not** name the key. Compare your front matter against the schema's field list to
find it. A repeated key is the exception — it is named, but only when it is a field
the schema defines; otherwise you get position alone.

## What nothing consumes yet

`audiences` is required, and no code reads it. The schema declares it and the schema's
own tests exercise it; the checker never looks at it, and no generated view exists yet
to route by it.

This is stated because it is genuinely undecided rather than merely undocumented — two
reviewers reached opposite conclusions about whether the field mattered. It is
required, so fill it honestly; but a node's `audiences` value changes nothing today
beyond what a human reads.

**This node claims `agent` and `reviewer`.** Agents author corpus nodes, and reviewers
hold every convention in *Guidance*, none of which any check enforces. It claims no
other role the schema offers, because nothing here addresses building or running Buzz
itself — only authoring a node.

## Enforcement

One command, from the repository root:

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

Exit 0 passes; 1 means at least one error, and every error names the node it came
from. The same command runs in CI on pull requests and on pushes to `launchpad`,
triggered by any change under the corpus root — so a local failure is a CI failure,
and there is no second, laxer gate.

**`UNVERIFIED` notices are not failures and are not passes.** They mean the checker
recognised a citation's shape and had nothing it could open. A run printing them still
exits 0.

**What a passing run establishes about front matter:** that the block is well-formed and
closed, that its fields are ones the schema defines with values the schema accepts, that
its id is unique, that the edges *it can see* resolve, and that its cited paths name
real files.

**What it does not:** that any statement in the ledger is true, that a cited file backs
the claim it sits under, that a cited line number is still the right line, or that
anything at all in the body is accurate.

Three of those gaps are sharp enough to name individually, because a passing run looks
like proof of each and is not:

| A green run does not establish | Because |
|---|---|
| That the block contains everything you wrote in it | A stray delimiter ends it, and the rest is discarded unread — including a `relationships` block that would otherwise be a hard error |
| That the node records the revision it was checked at | Nothing requires a commit citation; a ledger with none passes clean |
| That a relationship target will still resolve after merge | Targets are checked against the nodes loaded *here*, and the checker cannot see the branch you are merging into |

Checking is structural. Only a reader establishes the rest, which is what makes the PR
diff the real gate.

## Exceptions and escalation

**A field or value the schema does not allow is not an exception you may take.** The
field set is closed on purpose, and the checker fails closed. Widening it is a change
to the schema, not a local override, and there is no per-node opt-out.

- **Adding a value to a closed field** is additive and not breaking. It needs no
  compatibility entry, though noting it is welcome.
- **Removing a field or a value, or narrowing a type,** is breaking. It requires, in
  the same pull request, a dated entry in `COMPATIBILITY.md` and a re-validation pass
  of every existing node against the new schema. A note describing the change without
  checking it against real nodes is a claim, not a check.
- **A field you need that does not exist** is a schema change proposed against #605's
  contract, not a key added to one node.

**When two authoritative sources conflict**, do not average them and do not take the
newer one. ADR-0029 is the rule: executable evidence governs claims about current
behaviour, accepted decisions govern claims about intended behaviour, and two sources
of the *same* claim type in conflict leave the node marked for a human rather than
resolved by its author.

## Scope and omissions

**This node covers** the front-matter block: its delimiters, the YAML inside them,
what each field is for, what the checker enforces, and what a passing run leaves
unestablished.

**It does not cover, and these are gaps rather than silence:**

| Not covered | Owner |
|---|---|
| The meaning of any individual field's values | the nodes listed under *Scope and authority* |
| The evidence ledger's contract, and citation shapes | #1314, #1308 |
| Body structure, or any per-type template | unlanded, somewhere in #1307–#1351 — a range, not a mapping; look the subject up rather than reading a number off it |
| Provenance for generated artifacts | #1316 |
| A line number in a citation not being checked against the file | #1459 |

**No `relationships` in this node's own front matter, and the original reason has
expired.** It was written when `launchpad` carried no loadable corpus node at all, so
any edge would have resolved in the authoring worktree and been a hard error in CI.
That is no longer true: `launchpad` now carries `corpus-agents`, `corpus-readme` and
two standards nodes, and an edge to any of them would resolve. The block stays empty
here only because declaring edges is a batch-wide pass with its own owner — **#1489** —
and not because there is nothing to point at. Stating the expired reason as though it
still held would be the exact drift this node's own Guidance 4 warns about.

**Expected but not checked when this node was written:**

- **No behaviour here was checked against any consumer of the corpus.** Everything
  stated is the checker's behaviour and the schema's contract. Whether a generated view
  or the knowledge crate imposes further front-matter expectations was not established,
  because no such consumer exists yet to test against.
- **The claim that nothing reads `audiences` is an inference from an exhaustive search,
  not a proof.** A consumer reading the field dynamically, or one outside this
  repository, would not appear in it. It is recorded at 0.9 confidence for that reason.
- **Every MUST in *Requirements* and every SHOULD in *Guidance* was run, in both
  directions** — each requirement has a node that breaks it and exits non-zero, and each
  guidance item bar one has a node that violates it and exits zero. The exception is
  guidance item 1, which is partly enforced; that is stated at the item rather than
  hidden here. What was *not* done is the converse sweep — enumerating every path through
  the checker and asking which rule catches it — so a rule this node never thought to
  state could be enforced without being written down here.
- **The claim that a green run says nothing about body prose rests on reading the code,
  not on a fixture.** The checker binds the body to a name it never reads again, which
  is plain in the source; no test was built that puts a false claim in a body and
  confirms the run stays clean, because there is nothing that could report it.
