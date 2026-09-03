Issue #903 -- generate corpus document generated/provenance-index.md

Stated size: batch corpus-doc task, one generated document + minimal generator/test change -> cap: 5 steps

ALREADY TRUE

- Feature #621's generator framework (`launchpad/project-intelligence/corpus/indexes.py`,
  issue #633) is merged on the local integration branch `feature/621-generated-traceability`
  and this worktree is branched from its tip. It owns discovery of `index_defs/` builder
  modules, canonical-input digesting, and rendering of front matter + the
  `templates/generated-index.md` body skeleton. A builder is add-a-file-only.
- `node.schema.json`'s `evidence` field requires `minItems: 1` and each entry's
  `entry_class` is one of `FACT` / `INFERENCE` / `TEAM_KNOWLEDGE`
  (`launchpad/docs/corpus/schema/node.schema.json`, read directly). `validate.py` rejects
  any node whose front matter fails this schema (`node.error` gets set and the node is
  excluded from `ctx.valid_nodes`), so an accepted node can never carry zero evidence
  entries -- read directly in `validate.py`.
- `templates/generated-index.md` (node id `corpus-template-generated-index`) explicitly
  names `provenance-index.md` in its own list of index-shaped documents this template
  governs, alongside `corpus-index.md`, `crate-index.md`, `database-index.md`,
  `decision-index.md`, `event-kind-index.md`, `layer-index.md`, `nip-index.md` and
  `test-index.md` -- read directly this session.
- `index_defs/decision_index.py` (issue #895, merged) is the closest precedent: a
  generated stats/coverage view (not a node listing) that counts and buckets a
  deterministic per-item signal across canonical nodes, states a corpus-wide total, and
  renders a "gap" table of items missing a property (there: zero-citation decision
  records). Read directly this session; this task's builder follows the same shape
  (per-node entry_class distribution, corpus-wide totals, a zero-evidence-node gap table)
  but over `ctx.valid_nodes`' own `evidence` arrays -- fully covered by `ctx.input_digest`,
  unlike `decision_index.py`'s digest-uncovered `launchpad/decisions/` read, since
  evidence lives inside the canonical nodes themselves.
- EXTRA (dispatch brief): this document's scope is explicitly distinct from #892's
  `coverage.md` (source-item disposition: does some canonical node account for each
  in-scope repository source item) and #634's `coverage.py` -- this document is about
  each canonical node's *own* evidence citations (how many FACT/INFERENCE/TEAM_KNOWLEDGE
  entries it carries), not source-inventory coverage. The rendered body states this
  distinction in its own prose, per `decision_index.py`'s "Distinction from ..." section
  precedent.
- `SLUG`/`NODE_ID` are pre-reserved: node id `generated-provenance-index`, builder module
  a new file `index_defs/provenance_index.py`, output path `generated/provenance-index.md`.

STEP 1 -- Author the builder module [independent]

Write `launchpad/project-intelligence/corpus/index_defs/provenance_index.py` exposing
`SPEC`:
- `name: "provenance-index"`, `output_path: "generated/provenance-index.md"`,
  `node_id: "generated-provenance-index"`, `node_type: "governance"` (no `provenance`/
  `evidence`/`index` enum member exists; the subject -- the corpus's own evidence-ledger
  bookkeeping -- is a governance concern about the corpus itself, the same reasoning
  `decision_index.py` and `coverage.py` both give for their own `governance` choice).
- `generate(ctx)` renders, over `ctx.valid_nodes` only (schema-valid nodes; an invalid
  node's `data` is not trustworthy and it is excluded from `ctx.valid_nodes` already):
  (a) a leading section stating this document's scope and its explicit non-overlap with
  #892's `coverage.md`; (b) a per-node table -- id, path (`ctx.rel_path(node)`), FACT
  count, INFERENCE count, TEAM_KNOWLEDGE count, total entries -- sorted by node id; (c) a
  corpus-wide totals section: node count, total evidence entries, and the sum of each
  `entry_class` across the whole corpus; (d) a "zero-evidence nodes" section listing any
  valid node whose `evidence` array is empty or missing, stated as **expected to be
  empty** with the schema reason given in ALREADY TRUE, rendered as an honest "None" when
  (as expected) the list is empty rather than silently omitting the section.
- No `extra_evidence` needed: the framework's own two standard evidence entries (generator
  + builder module) already cover "how this table was produced," and every number in it
  derives from `ctx.valid_nodes[*].data['evidence']`, already inside `ctx.input_digest`.
- `relationships`: `implements -> corpus-template-generated-index` (index-shaped, and the
  template explicitly names this document), `references -> corpus-agents` (the evidence
  classification rules this table renders a view of).
done when: the module exists, `python3 launchpad/project-intelligence/corpus/indexes.py
--list` shows a `provenance-index` builder with no discovery error, and `--only
provenance-index` writes `launchpad/docs/corpus/generated/provenance-index.md`.

STEP 2 -- Generate and confirm determinism [needs 1] <- RUNS HERE

Run `python3 launchpad/project-intelligence/corpus/indexes.py --only provenance-index` to
produce the target file. Re-run it a second time and confirm `git status --porcelain`
shows no diff on the generated file. Run
`python3 launchpad/project-intelligence/corpus/indexes.py --check --only provenance-index`
and confirm exit 0. Visually confirm the rendered zero-evidence-nodes section reads "None"
against the real corpus at this revision.
done when: two consecutive generations are byte-identical, `--check` exits 0, and the
zero-evidence section is confirmed empty against the real corpus.

STEP 3 -- Focused builder test [needs 1]

Write `launchpad/project-intelligence/corpus/tests/test_index_provenance_index.py`
following `test_index_decision_index.py` and `test_index_coverage.py`'s conventions:
builder discovered with the expected identity (output path, node id, node type,
relationships); a small fixture corpus (temp directory, no repo-root derivation needed
since evidence lives in `ctx.valid_nodes` directly) with 2-3 nodes carrying a mix of
FACT/INFERENCE/TEAM_KNOWLEDGE entries, asserting the per-node counts, the corpus-wide
totals, and that the zero-evidence-nodes section renders "None" (schema `minItems: 1`
makes a nonzero case unconstructable through a schema-valid fixture node, so the
always-empty case is what is tested, plus a direct assertion that the section names why);
two renders byte-identical; front matter carries `id: "generated-provenance-index"` and
`type: "governance"`.
done when: `python3 -m unittest` on this file alone passes.

STEP 4 -- Full verification [needs 2, 3]

Run the full corpus test suite (`python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`) and `python3
launchpad/project-intelligence/corpus/validate.py`, both from this worktree. Self-review
the full diff against issue #903's Definition of Done line by line (exactly one generated
document; generator-produced, not hand-authored; schema-valid front matter;
do-not-edit marker; generator/inputs/inclusion-exclusion/ordering named; regenerable;
no-change rerun produces no diff) and against the EXTRA non-overlap requirement (the
document's own body text states, explicitly, how it differs from #892's `coverage.md` and
#634's `coverage.py`).
done when: the full suite passes (374 baseline + this task's new tests), `validate.py`
exits 0, and the self-review notes are ready to fold into the commit body.

STEP 5 -- Commit [needs 4]

Run the commit-gate recipe exactly as specified (test suite as the sole command in one
Bash call, then `git add` the builder module, generated file, test file and this plan in
a separate call, then `git commit -s`).
done when: one signed local commit exists on `task/903-generated-provenance-index`
containing exactly those four files, and `git status --porcelain` is clean afterward.

PARALLEL

Steps 1 and 3 both depend only on the (already-true) framework and precedent reading, so
a second agent could draft the test file (step 3) from `decision_index.py`'s and
`coverage.py`'s test conventions while step 1 is being written, then wire it to the real
`SPEC` once step 1 lands -- not exercised in this single-agent run, but the dependency
graph allows it.

GATES

- `python3 launchpad/project-intelligence/corpus/indexes.py --check --only
  provenance-index` must exit 0 before commit.
- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit
  (pre-existing UNVERIFIED notices are non-fatal; a new hard error is this task's to fix).
- The full test suite (step 4) must pass before commit; no `--no-verify`, no touching a
  stamp file, no widening the inclusion rule to force a nonzero zero-evidence count.

BUDGET

One builder module, one generated Markdown file, one focused test file, this plan file.
No edits to `indexes.py`, any other builder, or `validate.py`.

OPEN

- Whether a future confidence-weighted or per-audience breakdown of evidence entries is
  wanted is not this task's to decide; the per-`entry_class` count is the deterministic,
  schema-grounded signal available today.
- Whether the zero-evidence-nodes section should ever fire is intentionally a standing
  tripwire, not a dead code path: if `validate.py`'s schema enforcement ever regresses,
  this document is the place a reader would see it first.

LEFT OUT

- Any statement about whether a citation *supports* its claim -- AGENTS.md is explicit
  that checking is structural only (a `FACT` citing a real file that says nothing on the
  subject still passes); this document counts classification labels, it does not audit
  citation quality.
- Source-inventory coverage (which repository source items are accounted for by some
  node) -- that is #892's `coverage.md` and #634's `coverage.py`, not restated or
  duplicated here.
- Per-node listing of decision-record citations -- that is `decisions/INDEX.md`
  (`decisions_index.py`, issue #845) and #895's `decision-index.md`; this document's
  per-node table is keyed by `entry_class`, not by cited target.
