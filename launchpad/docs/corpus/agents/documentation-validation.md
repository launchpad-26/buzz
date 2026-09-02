---
id: agents-documentation-validation
type: agent
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "validate.py's main() prints a run's UNVERIFIED notices to stderr first, then, if report.errors is non-empty, prints one FAIL line per error plus a trailing 'FAIL  N corpus validation error(s)' line and returns 1; otherwise it prints a PASS line -- 'PASS  corpus validation clean' when unverified is empty, or 'PASS  corpus validation found no errors; N item(s) reported unverified' when it is not -- and returns 0."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Running python3 launchpad/project-intelligence/corpus/validate.py from this repository's root at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90 exits 0 and prints 'PASS  corpus validation found no errors; 593 item(s) reported unverified' as its final line, with 593 preceding UNVERIFIED lines and zero FAIL lines."
    entry_class: FACT
    evidence:
      - "shell(python3 launchpad/project-intelligence/corpus/validate.py) -> exit 0, final line 'PASS  corpus validation found no errors; 593 item(s) reported unverified', 0 FAIL lines, 593 UNVERIFIED lines, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "validate_corpus() runs, in order: schema validation via load_nodes (one error per node, first schema violation only), find_duplicate_ids, find_unresolved_relationship_targets, find_non_finite_confidence, find_citation_problems (splitting into errors and unverified), find_non_canonical_nodes, and find_ownership_violations -- and every one of their returned strings names the offending node's id (or file path, for a node whose id itself failed validation) as its first token."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A schema violation is reported as '<label>: schema violation at <json-path-or-<root>>: failed <keyword> constraint (schema requires: <value>)', built only from node.schema.json's own keyword and required value -- never from the node's own instance data -- specifically so a credential-shaped citation that fails schema validation is not echoed into the error message or CI logs."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A relationship target that matches no loaded node's id is reported as '<id-or-path>: relationship target <target> does not match any known node id' by find_unresolved_relationship_targets, which builds its known-id set only from nodes that loaded without a schema error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A duplicate id across two or more nodes is reported as '<id>: duplicate id used by N nodes: <path1>, <path2>, ...' by find_duplicate_ids, which lists every path sharing that id string."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation is classified into exactly one of three verdicts -- ok, error, or unverified -- by _classify_citation, which routes a citation to _classify_url for anything starting with http:// or https://, to an unverified commit/graph-edge/tool-result branch for CONTRACT.md's three unopenable forms, and otherwise to _classify_repo_path for a bare path or a path:line/path:start-end position; only ok citations are silent, and only error citations, printed as '<label>: evidence entry N, citation M: <detail>', fail the run."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "_classify_repo_path rejects, in order, a credential-shaped filename ('matches a prohibited credential-like pattern'), an absolute path ('must be a repo-relative path, not absolute'), a path that resolves outside the repository once symlinks are followed ('resolves outside the repository'), and a path that resolves inside the repository but is not an existing file ('does not resolve to a real file in the repository') -- the last of these being the message a typo'd file citation produces."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "_classify_url rejects a GitHub repository link pinned to a mutable ref rather than a full 40-character commit SHA ('is a repository link pinned to a mutable ref rather than a full commit SHA (ADR-0003)'), a link whose verb is not blob or raw ('is a repository <verb> view rather than a link to the cited file itself'), and a pinned link naming no file after the ref ('is pinned but names no file within the repository') -- and reports any other http(s) URL as unverified ('is an external URL this validator can neither pin nor open'), never as an error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "find_non_finite_confidence rejects a NaN or Infinity confidence value with '<label>: evidence entry N: confidence must be a finite number within [0.0, 1.0] -- NaN and Infinity pass node.schema.json's minimum/maximum check but are rejected here', a check node.schema.json's own minimum/maximum keywords cannot perform because every numeric comparison against NaN is false."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "find_ownership_violations rejects every non-.md file under the corpus root (schema/ excluded): one under a generated/ directory as '<path>: generated artifact whose provenance and reproducibility cannot be established -- no corpus generator exists yet to reproduce it from canonical Markdown (ADR-0028); see #1316', and one anywhere else as '<path>: non-.md file outside generated/ -- misplaced generated artifact, or hand-authored content in the wrong format'."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md's 'Running the check' section states the same command runs in CI on every change under launchpad/docs/corpus/, so a local failure is a CI failure, and that --root <path> validates a corpus tree other than the real one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "The Justfile's corpus-validate recipe runs exactly python3 launchpad/project-intelligence/corpus/validate.py, with a comment stating citations that name nothing openable print as UNVERIFIED without failing the run."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: ".github/workflows/launchpad-corpus-validate.yml runs on pull_request and on push to the launchpad branch, both scoped to paths under launchpad/project-intelligence/corpus/**, launchpad/project-intelligence/requirements.txt, launchpad/docs/corpus/** and the workflow file itself, and its final step runs python3 launchpad/project-intelligence/corpus/validate.py against the real corpus tree after the validator's own unit test suite."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "AGENTS.md's 'Three things a passing run does not mean' section states that citation checking is structural (a resolving citation is never proof it supports its statement), that UNVERIFIED is not a pass (a FACT resting only on UNVERIFIED citations has not been checked by anything), and that a line-numbered citation's line number is never verified against the file's length."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "agents-invariants.md's Enforcement section states that I4 (duplicate ids), I5 (unresolved relationship targets), I6 (schema shape), I7's field-shape half (which fields an entry_class requires or forbids), I8 (GitHub link pinning) and I9 (non-.md placement) are mechanically enforced by validate.py and its CI workflow, while I1 (no second authored representation of one idea), I2 (one idea per node), I3 (id permanence), I7's honesty half (whether a FACT label was actually earned) and I10 (no reuse/rename of a retired id) are enforced by review only, because validate.py discards a node's Markdown body before any check runs."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
  - statement: "The corpus-review skill (.claude/skills/corpus-review/SKILL.md) documents a four-report review procedure for one drafted node -- structural validation (validate.py's own result, quoted not paraphrased), factual/evidence findings (opening every cited source and checking each entry_class against what its citation actually is), duplication/atomicity findings (one idea per node; the same claim restated in a neighboring node), and security/public-boundary findings (private-source content, credential-shaped citations, forged provenance) -- and states that only validate.py's own exit code is a hard contract failure, the other three are advisory for a human to weigh."
    entry_class: FACT
    evidence:
      - ".claude/skills/corpus-review/SKILL.md"
  - statement: "At commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, launchpad/docs/corpus/templates/procedure.md (id corpus-template-procedure) and launchpad/docs/corpus/agents/invariants.md (id agents-invariants) both exist on origin/launchpad, so both are valid relationship targets for a node merging into that branch."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> includes templates/procedure.md and agents/invariants.md, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "Every merged corpus node's id observed at this revision follows '<path-below-corpus-root-with-slashes-as-hyphens>-<filename-stem>', e.g. architecture-containers-mobile for architecture/containers/mobile.md and agents-invariants for agents/invariants.md -- the pattern this node's own id (agents-documentation-validation) follows."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/agents/invariants.md"
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "Parent Feature #620 lists #645 (agents/documentation-creation.md) and #646 (agents/documentation-update.md) among its 32 child document tasks, neither merged at this node's authoring time; this node's own issue #647 is a sibling task in the same family, none of the three able to read the others' actual drafted content."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body, batch dispatch brief for issues #645-#647"
  - statement: "Issue #647's own Definition of Done requires this node to state goal, prerequisites and allowed environment/scope; provide ordered, executable, project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands/config rather than give generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#647 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: agents-invariants
  - type: implements
    target: corpus-template-procedure
---

# Validating a corpus node: how-to

How to check a drafted or updated `launchpad/docs/corpus/` node before it merges: run
the deterministic validator, read what its PASS/FAIL and per-node output actually
establish, and then run the review-only checks nothing mechanical performs. Perform
this after drafting a new node (`#645`'s scope) or editing an existing one (`#646`'s
scope) -- it is their shared final gate, not a third stage in either lifecycle.

## Before you start

- A drafted or edited node's front matter and body are complete enough to check --
  this procedure does not itself draft content (`#645`, `#646`).
- A working checkout with Python 3.11+, `jsonschema` and `PyYAML` installed
  (`pip install -r launchpad/project-intelligence/requirements.txt`), and repository
  root as the working directory.
- Read `launchpad/docs/corpus/AGENTS.md` first if you have not: this node checks
  compliance with it and does not restate its evidence-classification or
  authoring/updating/retiring rules.

## Run and interpret the deterministic validator

1. From the repository root, run:

   ```bash
   python3 launchpad/project-intelligence/corpus/validate.py
   ```

   `--root <path>` validates a corpus tree other than the real one; without it the
   command always validates `launchpad/docs/corpus/`, regardless of the working
   directory. `just corpus-validate` runs the identical command but needs the Hermit
   environment activated first (`. ./bin/activate-hermit`); the direct form does not.

2. Read every `UNVERIFIED` line printed to stderr, but do not stop there -- these are
   non-fatal notices, printed for a citation form the validator recognises but cannot
   open (a commit reference, a graph edge, a tool result, an external non-GitHub URL),
   never for something the tool merely failed to check. A confirmed-clean run at this
   node's recorded revision still printed 593 of them.

3. Read the exit status and final line:
   - **Exit 0, `PASS  corpus validation clean`** -- no errors, no unverified notices.
   - **Exit 0, `PASS  corpus validation found no errors; N item(s) reported
     unverified`** -- no errors, but N citations could not be opened. Still a pass;
     re-read step 2 for what that does and does not mean.
   - **Exit 1, one or more `FAIL` lines followed by `FAIL  N corpus validation
     error(s)`** -- fix every named node before proceeding. Each `FAIL` line names
     its offending node (by `id`, or by file path if the `id` itself is what failed)
     as its first token, so the fastest path is to search this node's own id or path
     rather than re-reading the whole file.

4. Match the FAIL message's shape to its cause and fix it. This table is scoped to
   what an author drafting or updating one node most often hits -- not a full
   catalogue of every check; read `validate.py` itself for anything not listed here.

   | Message contains | Likely cause | Fix |
   |---|---|---|
   | `schema violation at <path>: failed '<keyword>' constraint` | Front matter fails `node.schema.json` -- a missing required field, wrong enum value, or a field an `entry_class` forbids | Compare the named JSON path and keyword against `node.schema.json` directly |
   | `relationship target '<target>' does not match any known node id` | A `relationships[].target` names an id that does not exist on the tree being validated | Re-check the target against `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`), not your own worktree |
   | `duplicate id used by N nodes` | Two files share the same `id` | Rename one -- but never rename an already-merged node's `id` (I3) |
   | `does not resolve to a real file in the repository` | A bare-path or `path:line` citation is misspelled, moved, or was never a real file | Open the path yourself and correct the citation |
   | `is pinned but names no file within the repository` / `pinned to a mutable ref rather than a full commit SHA` | A GitHub link citation is malformed or uses `blob/main` instead of a full SHA | Re-pin to the full 40-character commit SHA and a real file path |
   | `confidence must be a finite number within [0.0, 1.0]` | An `INFERENCE` entry's `confidence` is `NaN` or `Infinity` -- passes the schema's own range check but not this one | Set a real number in range |
   | `non-.md file outside generated/` / `generated artifact whose provenance ... cannot be established` | A non-Markdown file was added under the corpus root | Remove it, or see `#1316` if it is a genuine generated-content case (unimplemented as of this writing) |

5. Re-run the command after each fix. Repeat until exit status is 0.

## Run the review-only checks

Passing `validate.py` establishes none of what `agents-invariants.md`'s Enforcement
section calls I1, I2, I3, I7's honesty half, or I10 -- `validate.py` discards a
node's Markdown body before any check runs, so one authored idea versus two, an
honestly-earned `FACT` label, and `id` permanence are never inspected mechanically.
Use the `corpus-review` skill for this half instead of re-deriving it:

6. Invoke it (for example, `Skill(corpus-review)` in an agent session, or read
   `.claude/skills/corpus-review/SKILL.md` directly for a human reviewer) against the
   node under check. It produces four separate reports -- structural validation
   (`validate.py`'s own result, quoted), factual/evidence findings (every cited
   source opened and every `entry_class` checked against what it actually cites),
   duplication/atomicity findings (one idea per node; the same claim restated
   elsewhere in the corpus), and security/public-boundary findings (private-source
   content, credential-shaped citations, forged provenance).

7. Treat only `validate.py`'s own exit code, inside that report, as a hard blocker.
   The other three reports are advisory -- a human weighs them, per the skill's own
   stated discipline; do not let an advisory finding block a merge on its own
   authority, and do not let a clean `validate.py` run substitute for having read
   them.

8. Fix any finding that is a genuine defect, then return to step 1 and re-run
   `validate.py` -- a body edit made to satisfy a review-only finding can itself
   introduce a structural error (e.g. a citation added to back a newly-honest `FACT`
   that does not resolve).

## See also

- `launchpad/docs/corpus/AGENTS.md` -- creating, updating, and retiring a node;
  evidence classification; what a passing run does and does not establish, stated at
  greater length than this node repeats.
- `launchpad/docs/corpus/agents/invariants.md` -- the full I1-I10 invariant list and
  its Enforcement section's mechanical-versus-review-only split this node's second
  task sequence is built on top of.
- `.claude/skills/corpus-review/SKILL.md` -- the review procedure this node's second
  task sequence invokes rather than restates.
- `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/schema/README.md`
  -- the front-matter contract `validate.py`'s schema step enforces.

## Boundary

This node does not describe:
- How to draft a new node's content, choose its `id`, or write its evidence ledger --
  that is `#645`'s scope (`agents/documentation-creation.md`).
- How to re-verify claims and decide whether a recorded revision moves when updating
  an existing node -- that is `#646`'s scope (`agents/documentation-update.md`).
  Both `#645` and `#646` end at this node: it is their shared final gate, applied
  after either lifecycle produces a candidate node, not a third parallel stage
  alongside them. Neither is merged at this node's authoring time, so neither is
  named as a relationship target here (see *Relationships* below).
- How to acquire the underlying skill of writing corpus documentation from scratch,
  for a newcomer -- a tutorial, which has no corpus template as of this writing
  (`templates/procedure.md`'s own Boundary section).
- Why the corpus's evidence-classification or schema design exists, or how its
  pieces relate conceptually -- see `AGENTS.md` and the ADRs it links for that.
- The full catalogue of every message `validate.py` can print. The interpretation
  table above is scoped to what an author most often hits; `validate.py`'s own
  source is authoritative for anything else.

## Relationships

- `depends-on: corpus-agents` -- this node's own authority over what a passing
  `validate.py` run means is derived from `AGENTS.md`, not original to itself, the
  same relationship `agents-invariants.md` declares toward the same target for the
  same reason.
- `references: agents-invariants` -- this node's second task sequence is built
  directly on that node's Enforcement section, cited rather than restated.
- `implements: corpus-template-procedure` -- per `relationships.schema.json`'s own
  worked example for `implements`, "a template instance of a standard," and this
  node is exactly that: a how-to-shaped instance of `templates/procedure.md`.
- No edge to `#645` or `#646`: neither `agents/documentation-creation.md` nor
  `agents/documentation-update.md` is merged at this node's authoring time, so
  neither is a valid relationship target; named by title only in *Boundary* above,
  per the batch brief for this task family.

## Scope and omissions

**This node covers** running `validate.py` against a drafted or updated corpus node,
interpreting its exit status and per-node PASS/FAIL/UNVERIFIED output against what
each check actually establishes, a table mapping the most common `FAIL` message
shapes to their cause and fix, and invoking the `corpus-review` skill for the
invariants `validate.py` cannot check because it never reads a node's body.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Drafting a new node's content and evidence ledger | `#645` (`agents/documentation-creation.md`), unmerged |
| Re-verifying claims and moving a recorded revision when updating a node | `#646` (`agents/documentation-update.md`), unmerged |
| The full I1-I10 invariant list this node's second task sequence assumes | `launchpad/docs/corpus/agents/invariants.md` |
| The `corpus-review` skill's own four-report content, in full | `.claude/skills/corpus-review/SKILL.md` |
| Whether a recorded revision may stay put across a partial re-verification | `#1321`, unsettled corpus-wide |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |

**Expected but not verified when this node was written:**

- **No node has yet been authored from this exact template for this exact subject
  before this one.** Whether the interpretation table above covers the FAIL shapes
  an author actually hits most often, versus an exhaustive list, was not tested
  against a real defective node deliberately introduced and then fixed -- only
  against `validate.py`'s own source and a clean run.
- **Whether `#645` and `#646`, once merged, will each declare a relationship toward
  this node** (e.g. `references` or `part-of`) is their own edit to make, not decided
  here.
- **Whether the `corpus-review` skill will itself be run against this node before it
  merges**, and with what findings, is this node's own build loop's step to perform,
  not something this node's content can attest to about itself.
