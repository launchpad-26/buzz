Issue #889 — generate `launchpad/docs/corpus/generated/concept-index.md` (parent PRD #621)
Stated size: not stated on #889; the #621 generated-document family brief caps every task  ->  cap: 5 steps

ALREADY TRUE on branch feature/621-generated-traceability (worktree base a7b215bb25):
- The #633 generator framework exists at launchpad/project-intelligence/corpus/indexes.py:
  builder discovery from index_defs/, schema-derived enums, input digest, derived
  inverse edges (implemented-by among them), front-matter + body-skeleton rendering,
  CLI `--list | --all | --only | --check`, `--root`/`--defs-dir` for tests.
- Five builders already merged on the branch (glossary, index, decisions_index,
  api_index, capability_index) with per-builder tests; test baseline is 225 OK.
- templates/concept.md (id `corpus-template-concept`) exists on origin/launchpad,
  as do corpus-agents and corpus-template-generated-index — all three are safe
  relationship targets.
- No canonical node currently declares `implements -> corpus-template-concept`
  (grep over launchpad/docs/corpus front matter finds zero `target:
  corpus-template-concept` relationship lines), and node.schema.json's type enum
  has no `concept` value — so the deterministic inclusion rule matches zero nodes
  today and the honest output is an empty listing, exactly the state glossary.py
  shipped in for glossary terms.

STEP 1 [independent]  <- RUNS HERE
Write launchpad/project-intelligence/corpus/index_defs/concept_index.py exposing
SPEC: name `concept-index`, output_path `generated/concept-index.md`, node_id
`generated-concept-index`, node_type `governance` (enum has no concept/index
value; follows the recorded meta-document precedent glossary.py cites), audiences
agent/developer/reviewer. Inclusion rule mirrors glossary.py: a valid canonical
node qualifies iff it declares a forward `implements` relationship targeting
`corpus-template-concept`, read from ctx.inverse_edges["implemented-by"] — never
prose judgement. Zero matches renders an honest empty listing that says so.
The module docstring must note honestly that templates/concept.md does not itself
prescribe the implements edge (unlike glossary-term.md); the rule rests on
relationships.schema.json's `implements` directionality ("source is the concrete
realization of target (e.g. a template instance of a standard)") and the
corpus-wide template-instance convention the merged builders already use.
Relationships: implements -> corpus-template-generated-index, references ->
corpus-template-concept, references -> corpus-agents.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list`
includes `concept-index	generated/concept-index.md` and exits 0.

STEP 2 [needs 1]
Generate the document and prove determinism: run `--only concept-index` (writes
the target), run it a second time, confirm `git status --porcelain` shows the
file unchanged between runs, and run `--check --only concept-index`.
done when: second run leaves no diff and `--check --only concept-index` exits 0.

STEP 3 [needs 1]
Add launchpad/project-intelligence/corpus/tests/test_index_concept_index.py
following test_index_glossary.py's conventions: builder discovered with declared
identity; fixture-corpus inclusion tests (implementing node listed and sorted by
id, template itself and non-implementing nodes excluded, node implementing a
different template excluded, empty match renders the honest empty sentence);
byte-stable double render; committed-file check limited to SPEC-fixed properties
(id, type, do-not-edit marker).
done when: `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_index_concept_index.py"`
reports OK.

STEP 4 [needs 2, 3]
Full gates: the whole corpus test suite (baseline 225 + this task's additions)
and `python3 launchpad/project-intelligence/corpus/validate.py` exit 0 (hard
errors only; pre-existing UNVERIFIED notices are non-fatal). Then one signed
commit of exactly: the builder module, the generated target, the test file, and
this plan.
done when: suite OK, validate.py exit 0, `git log --oneline -1` shows the signed
commit `docs(corpus): generate generated/concept-index.md (#889)`.

PARALLEL: Steps 2 and 3 are independent of each other once Step 1 exists.

GATES:
- indexes.py --check --only concept-index exit 0 (regenerable, no-change rerun clean)
- python3 -m unittest discover ... exit 0, count > 225
- validate.py exit 0 with no new hard errors
- generated file is never hand-edited; any content fix goes through the builder

BUDGET: 1 new builder module, 1 generated document, 1 test file, 1 plan file —
no edits to indexes.py, validate.py or any shared/existing file.

OPEN:
- Whether templates/concept.md should gain an explicit "Relationships an
  instance node should consider" section prescribing the implements edge (as
  glossary-term.md has) is a template-content decision for a separate task, not
  this builder's to make.

LEFT OUT:
- Widening the inclusion rule (keyword, path or type matching) to make the
  listing look fuller — zero matches is the honest current state.
- Authoring any concept instance node so the index has content — out of scope
  per the issue ("exactly one generated corpus document").
- Any edit to shared framework files — the builder contract is add-a-file-only.
