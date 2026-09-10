Issue #637 — generate corpus document GLOSSARY.md (parent PRD #621)
Stated size: not stated on issue #637; the #621 batch brief caps every task in this family  ->  cap: 5 steps

Plan: add one builder module to the #633 generator framework that emits
`launchpad/docs/corpus/GLOSSARY.md` — a generated index of glossary-term
nodes — plus a focused test. Base is the local integration branch
`feature/621-generated-traceability` (framework #633 and coverage #634 merged).

ALREADY TRUE
- The generator framework exists and ships zero builders: `launchpad/project-intelligence/corpus/indexes.py` discovers `index_defs/*.py` modules exposing `SPEC`, renders all front matter and the generated-index body skeleton, and provides `--only/--check`. Verified by reading indexes.py and running its test suite baseline (225 tests OK on this base).
- `launchpad/docs/corpus/templates/glossary-term.md` (id `corpus-template-glossary-term`) is merged on origin/launchpad; its "Relationships an instance node should consider" section names `implements -> corpus-template-glossary-term` as the edge a real glossary-term instance declares.
- Zero canonical nodes currently declare that edge: `grep -rl corpus-template-glossary-term launchpad/docs/corpus --include='*.md'` matches only the template itself. The glossary is therefore honestly empty at this revision.
- `corpus-template-generated-index` and `corpus-agents` are merged on origin/launchpad (git ls-tree checked), so `implements -> corpus-template-generated-index` and `references -> corpus-agents` / `references -> corpus-template-glossary-term` are resolvable relationship targets.
- standards/generated-content.md MUST 2 constrains only non-Markdown artifacts to `generated/`; a generated Markdown node may live at the corpus root, so `GLOSSARY.md` placement is legal.

STEP 1 [independent]  <- RUNS HERE
Write `launchpad/project-intelligence/corpus/index_defs/glossary.py` exposing
module-level `SPEC` (name `glossary`, output_path `GLOSSARY.md`, node_id
`corpus-glossary`, node_type `governance` — justified in the module docstring by
the README/standards precedent for corpus meta-documents; the glossary indexes
terms across all thirteen surfaces so no subject type fits better).
Inclusion rule, deterministic and schema-grounded: a valid canonical node
qualifies iff it declares a forward `implements` relationship targeting
`corpus-template-glossary-term` — read from
`ctx.inverse_edges["implemented-by"]` (the framework's generated inverse), never
from prose. Empty match renders an honest "no entries" listing, not a widened
rule. Rows (when any) sorted by node id: id, path, type, status.
Relationships: `implements -> corpus-template-generated-index`,
`references -> corpus-template-glossary-term`, `references -> corpus-agents`.
One `extra_evidence` entry stating the qualifying-node count at the input digest.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list` prints `glossary	GLOSSARY.md`.

STEP 2 [needs 1]
Generate and prove determinism: run `--only glossary` (writes
launchpad/docs/corpus/GLOSSARY.md), rerun it, and run `--check --only glossary`.
done when: second run leaves `git status --porcelain -- launchpad/docs/corpus/GLOSSARY.md` unchanged and `--check --only glossary` exits 0.

STEP 3 [needs 1]
Write `launchpad/project-intelligence/corpus/tests/test_index_glossary.py`
following test_indexes.py conventions (fixture corpus copied to a temp dir,
`--root`/`--defs-dir` pointed away from the real corpus where mutation happens):
builder discovered with the right name/output/node_id/type; output byte-stable
across two runs; inclusion rule behaves — a fixture node with
`implements -> corpus-template-glossary-term` is listed, a node without it is
not, and an empty corpus yields the explicit empty-listing sentence; front
matter of the real generated file carries `id: "corpus-glossary"` and
`type: "governance"` (real corpus read-only).
done when: `python3 -m unittest launchpad.project-intelligence...` equivalent discovery run shows the new tests passing alongside the existing 225.

STEP 4 [needs 2, 3]
Full gates: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
(new UNVERIFIED notices acceptable, hard errors not), full unittest discovery
over corpus/tests passes, then one signed commit of builder + GLOSSARY.md +
test + this plan.
done when: unittest discovery reports OK and `git log --format=%G? -1` shows a signed commit containing exactly those four files.

PARALLEL
Steps 2 and 3 are independent of each other once step 1 exists; run in either
order. Nothing else in this worktree runs in parallel — sibling #621 tasks build
their own builders in their own worktrees, and duplicate names/output paths fail
discovery loudly at integration.

GATES
- `indexes.py --check --only glossary` exit 0 (no-change rerun, DoD).
- `validate.py` exit 0 (schema-valid front matter, resolvable relationships).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` OK — the commit gate from the batch brief.

BUDGET
One new builder module (~80 lines), one generated document, one test file
(~120 lines), this plan. No shared file is edited; indexes.py, validate.py and
existing tests are untouched.

OPEN
- Whether GLOSSARY.md should eventually list the term statement text (body line)
  rather than just id/path/type/status — deliberately not decided here; the term
  statement lives in instance bodies that do not exist yet, and extracting body
  prose is not schema-grounded. First real glossary-term instance should force
  the question.
- Whether glossary-term instances should also declare `part-of -> corpus-glossary`
  once this node merges (the template names that mechanism) — an instance-author
  decision, not this generator's.

LEFT OUT
- Any hand-authored glossary term: the issue's out-of-scope bars a second
  canonical document, and the honest state is zero terms.
- Widening the inclusion rule to path prefixes or keyword matches to make the
  glossary look fuller — the brief explicitly forbids prose-judgement inclusion
  and blesses an honest near-empty glossary.
- Edits to indexes.py or any shared file — the framework's add-a-file-only
  contract.
