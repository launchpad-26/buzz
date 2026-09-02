Issue #633 — implement deterministic corpus graph and index generation
Stated size: no Size line on the issue; batch orchestrator fixes the bound  ->  cap: 5 steps

ALREADY TRUE
- validate.py already owns the "what counts as a node" contract: discover_markdown_files
  (sorted rglob, schema/ excluded, symlink-resolved) and load_nodes (frontmatter parse +
  node.schema.json validation). The generator reuses these, never reimplements them.
- relationships.schema.json already marks which inverse types are generated
  (depended-on-by, superseded-by, implemented-by, has-part) and which is authored
  (referenced-by). Nothing derives them yet.
- templates/generated-index.md already prescribes the generated body shape: do-not-edit
  blockquote, Generator, Inclusion and exclusion rules, listing, Relationships,
  Scope and omissions.
- standards/generated-content.md MUST 6 already bars hand-authored inverse edges;
  node.schema.json's closed relationship enum enforces it structurally.
- The test suite convention (path-loaded module, fixture corpora under tests/fixtures/,
  --root pointing at fixtures) already exists in test_validate.py. Baseline: 170 tests.
- launchpad/project-intelligence/corpus/indexes.py does not exist (generated-content.md
  records this as FACT); no corpus document exists under generated/.

STEP 1 [independent] Framework core in launchpad/project-intelligence/corpus/indexes.py  <- RUNS HERE
  Load validate.py by path (same pattern test_validate.py uses) and build on its
  contract: canonical inputs = discover_markdown_files/load_nodes output MINUS every
  registered builder's output_path (outputs never feed themselves). Define IndexSpec
  (name, output_path, node_id, title, node_type, audiences, subject, generate,
  optional extra_evidence, optional relationships) and GeneratedBody (includes,
  excludes, sections, optional not_covered/unverified bullets). Builder discovery:
  sorted module files in new package index_defs/ (ships with only __init__.py),
  loaded by path; each exposes SPEC (IndexSpec or duck-typed equivalent). Validate
  each SPEC against node.schema.json's type/audiences enums at load time. Compute
  input digest: sha256 over sorted (posix rel path, b"\0", bytes) of canonical inputs.
  done when: python3 -c importing indexes.py by path succeeds; discovery of an empty
  index_defs/ returns []; digest of a fixture corpus is stable across two calls.

STEP 2 [needs 1] Graph helpers + rendering
  GenerationContext carries: corpus_root, canonical nodes (sorted), forward edges,
  derived inverse-edge maps for the four generated-inverse types, broken-edge report
  (targets resolving to no node id — reported, never a crash), orphan report (nodes
  with no in- or out-edges), input digest. Framework renders the whole document:
  schema-valid YAML front matter (id, type, status: draft, origin: launchpad,
  audiences, evidence with machine-produced FACT entries citing indexes.py and the
  builder module per CONTRACT.md's citation forms, plus extra_evidence; relationships
  only when non-empty) and the template body skeleton (H1, do-not-edit blockquote
  naming script + inputs, ## Generator with script/inputs/ordering/source-revision
  digest, ## Inclusion and exclusion rules, builder sections, ## Relationships,
  ## Scope and omissions). LF, single trailing newline, no timestamps, no git SHAs.
  done when: rendering a fixture builder twice yields byte-identical text containing
  the do-not-edit marker and the sha256 digest.

STEP 3 [needs 2] CLI
  argparse following validate.py's conventions: --list, --only NAME (repeatable),
  --all, --check, --root PATH, --defs-dir PATH (tests only, mirrors --root's role).
  --check regenerates in memory and diffs against disk: nonzero exit + per-file
  report on any difference or missing file; with no builders installed it exits 0.
  Writing (--all/--only) creates parent dirs and writes LF bytes.
  done when: --check on an empty index_defs exits 0; --list prints nothing extra;
  exit codes observable from a subprocess-free main(argv) call.

STEP 4 [needs 3] Tests in launchpad/project-intelligence/corpus/tests/test_indexes.py
  Fixture corpora under tests/fixtures/indexes/ (clean/ with resolvable edges across
  all five forward types; broken/ with a dangling target and an orphan node) plus a
  committed fixture builder module under tests/fixtures/indexes/defs/. Cover: stable
  no-change regeneration (generate twice byte-identical; --check 0 after generate,
  1 after tampering); orphan + broken-edge reports (no crash); do-not-edit marker and
  digest present; outputs excluded from canonical inputs; deterministic ordering of
  builders and context nodes; a fixture-generated node's front matter passes
  validate.validate_corpus with zero errors.
  done when: python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py" is OK with >170 tests.

STEP 5 [needs 4] Validate + commit
  Run validate.py against the real corpus (must exit 0 — this change adds no corpus
  document), re-run the full suite as the sole command to earn the verify-gate stamp,
  then one signed commit: feat(corpus): deterministic index/graph generator framework (#633).
  done when: validate.py exits 0 and git log shows exactly one signed commit on
  task/633-corpus-index-generator.

PARALLEL
- None within this plan; steps are a strict chain. The 29 follow-up builder tasks run
  in parallel AFTER this lands, which is why extension is add-a-file-only: a new
  builder is one new module in index_defs/, never an edit to indexes.py.

GATES
- python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" (OK, >170 tests)
- python3 launchpad/project-intelligence/corpus/validate.py (exit 0)
- pre-commit verify-gate stamp earned by the real suite run as a sole command

BUDGET
- 2 new source files (indexes.py, index_defs/__init__.py), 1 test file, fixture
  corpora + 1 fixture builder module, this plan. No edits to validate.py, no files
  under launchpad/docs/corpus/.

OPEN
- Which concrete indexes/graphs to generate: each is its own follow-up issue
  (#891-#906 family); this framework ships zero real builders on purpose.
- Whether generated Markdown outputs live under generated/ or a subject directory:
  standards/generated-content.md says placement is per-subject; each builder's
  output_path decides, not this framework.

LEFT OUT
- Any real builder module — creating one here would swallow a follow-up issue's scope.
- Embedding git HEAD SHAs or timestamps in outputs — either would break byte-identical
  no-change reruns; the input digest is the source revision instead.
- Changes to validate.py (its ownership check for non-.md files stays untouched;
  generated .md nodes are validated like any node, which is the standard's rule).
- Wiring into just/CI — no issue bullet asks for it; follow-ups own their outputs.
