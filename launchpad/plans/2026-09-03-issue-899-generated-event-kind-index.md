Issue #899 — generate corpus document generated/event-kind-index.md
Stated size: no Size line on the issue; family task under parent PRD #621 -> cap: 5 steps

ALREADY TRUE
- The #633 generator framework (launchpad/project-intelligence/corpus/indexes.py) is
  merged on this base: builder discovery from index_defs/*.py, IndexSpec/GeneratedBody
  contracts, GenerationContext (valid_nodes, inverse_edges, input_digest, rel_path),
  and full front-matter/body-skeleton rendering per templates/generated-index.md.
- Fifteen builders are already registered (glossary, index, decisions-index,
  api-index, capability-index, code-to-doc-map, concept-index, configuration-index,
  corpus-index, coverage, crate-index, database-index, decision-index,
  dependency-graph, doc-to-code-map); event-kind-index is not among them.
- templates/generated-index.md's own "Boundary against the rest of the generated/*.md
  family" table names event-kind-index as one of the nine literally `*-index.md`
  documents its shape governs -- a direct textual anchor for using this template.
- templates/event-kind.md exists and states, in its own Required section 1, that a
  real event-kind instance node "would most plausibly take
  node.schema.json's ... interfaces-events type" (an INFERENCE, confidence 0.6, since
  no instance existed when that template was written) and, in its Boundary section,
  that no relationships exist yet from that template because zero canonical nodes on
  its base described a Nostr kind.
- Verified fresh on this base (not assumed from the template's now-stale count): zero
  canonical nodes (excluding generated/, templates/, schema/) carry front-matter
  `type: interfaces-events`, and zero carry `relationships: implements ->
  corpus-template-event-kind` -- both signals stay empty, so neither can drive this
  index's inclusion rule.
- A third signal does populate non-trivially: 67 canonical nodes across
  architecture/, capabilities/ and standards/ cite `crates/buzz-core/src/kind.rs` in
  their front-matter `evidence[].evidence` arrays -- some as a bare file citation,
  some with a `:N` or `:N-M` line-range suffix that lands on one specific `pub const
  KIND_<NAME>: u32 = <value>;` declaration line (e.g.
  capabilities/presence/user-status.md cites `crates/buzz-core/src/kind.rs:67-70`,
  which contains line 70, `KIND_USER_STATUS`'s own declaration line).
- `crates/buzz-core/src/kind.rs` itself is the deterministic, working-tree-inspectable
  registry of kinds: 129 `pub const KIND_<NAME>: u32 = <value>;` declarations at this
  revision, parseable by a plain regex (mirrors crate_index.py's tomllib parse of
  Cargo.toml -- a real, mechanical source, never AGENTS.md's or kind.rs's own prose
  commentary), with zero duplicate values (kind.rs's own `no_duplicate_kind_values`
  test already enforces this invariant on the constants this builder reads).
- index_defs/crate_index.py and index_defs/code_to_doc_map.py already ship the
  mechanical, schema-grounded citation classifier (path-shaped, line-suffix stripped,
  resolves to a real working-tree file) this task's classifier mirrors and extends
  one level deeper (line number -> containing constant), rather than reinventing it.

STEP 1 [independent] Builder module index_defs/event_kind_index.py  <- RUNS HERE
  Determinism source for "known kinds": a regex walk of
  `crates/buzz-core/src/kind.rs` in the working tree (via validate.repo_root(), same
  resolution code_to_doc_map.py/crate_index.py use) matching
  `^pub const (KIND_[A-Z0-9_]+): u32 = (\d+);` per line, recording each constant's
  name, value and 1-based declaration line number -- never a hand-copied kind list.
  Cross-reference rule: a kind is "documented by" every valid canonical node whose
  evidence citation resolves (via the shared classifier: no whitespace/parens/`->`,
  no `://`, optional trailing `:N`/`:N-M` line-suffix, must resolve to a real file)
  to `crates/buzz-core/src/kind.rs`, where the citation carries a line-suffix AND that
  suffix's line range includes the constant's own declaration line. A bare
  (no-line-suffix) citation of kind.rs cites the file generally, not one kind, and is
  named explicitly in "excludes" rather than silently dropped or force-attributed to
  every kind. SPEC: name event-kind-index, output_path
  generated/event-kind-index.md, node_id generated-event-kind-index, node_type
  governance (rows are kind.rs constants, not canonical nodes of one front-matter
  type -- same reasoning crate_index.py and code_to_doc_map.py give; the
  interfaces-events value the event-kind template names is for a future per-kind
  instance node, not for this cross-reference), audiences [agent, developer],
  relationships references->corpus-agents and implements->corpus-template-
  generated-index (the template's own family-boundary table names event-kind-index
  as one of the nine index-shaped documents). Zero-match branches (no kind.rs found,
  no citing node) both render an honest empty/partial state, never a widened rule.
  done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list` shows
  event-kind-index, and `--only event-kind-index` writes generated/event-kind-index.md
  without error.

STEP 2 [needs 1] Generate and confirm stability
  Run the generator to write TARGET, then rerun and diff (git status --porcelain must
  be empty) and run `--check --only event-kind-index` (must exit 0).
  done when: two consecutive generations are byte-identical and --check exits 0.

STEP 3 [needs 1] Test file
  tests/test_index_event_kind_index.py, following test_index_crate_index.py's
  conventions (indexes.py loaded by path as corpus_indexes; generation into a
  tempdir corpus; the builder still resolves kind.rs against the real repo root).
  Cover: builder discovered with declared identity; two runs byte-identical; a real
  kind constant (KIND_USER_STATUS, value 30315) appears in the listing even with zero
  fixture nodes; a fixture node citing kind.rs with a line-suffix landing on that
  constant's declaration line attributes documentation to it; a bare (no-suffix)
  citation of kind.rs attributes to no kind; a line-suffix landing on a different
  constant's line does not attribute to KIND_USER_STATUS; non-path-shaped/URL/prose
  citations and citations to a different file are excluded; front matter carries the
  declared node_id and type.
  done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` is OK with more tests than the 225-test baseline.

STEP 4 [needs 2] Validate
  Run validate.py against the real corpus; UNVERIFIED notices are pre-existing and
  non-fatal, any hard error is this task's to fix.
  done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 5 [needs 4] Commit gate
  Run the full unittest suite as the sole Bash command in the worktree to earn the
  verify-gate stamp, then stage builder module + generated file + test + this plan
  and create one signed commit.
  done when: `git log` on task/899-generated-event-kind-index shows exactly one
  commit ahead of feature/621-generated-traceability, containing exactly those four
  files.

PARALLEL
- None within this plan; steps are a short chain (module -> generate -> test/validate
  -> commit). This task itself runs in parallel with the other #621 family builders,
  each isolated to its own worktree and its own new index_defs/ module.

GATES
- python3 launchpad/project-intelligence/corpus/indexes.py --check --only event-kind-index (exit 0)
- python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" (OK, >225 tests)
- python3 launchpad/project-intelligence/corpus/validate.py (exit 0)
- pre-commit verify-gate stamp earned by the real suite run as a sole command

BUDGET
- 1 new builder module (index_defs/event_kind_index.py), 1 generated file
  (generated/event-kind-index.md), 1 test file, this plan. No edits to indexes.py,
  validate.py, or any other builder module.

OPEN
- Whether every one of the 129 `pub const KIND_*` constants in kind.rs is "live"
  (some doc comments mark a kind superseded by a renumbering, e.g. V1 kinds replaced
  by V2) -- this index lists every declared constant as found; it does not attempt
  to classify liveness, which kind.rs's own comments do inconsistently and which is
  out of scope for a mechanical cross-reference.
- Whether a future real event-kind instance node (type: interfaces-events,
  implements -> corpus-template-event-kind) should also gain a generated
  `implemented-by` edge on this index or on kind.rs's row -- no such instance exists
  on this base, so there is nothing to wire yet.

LEFT OUT
- Per-kind wire-shape detail (tags, content semantics, access-control gating) --
  that is templates/event-kind.md's per-instance job, not this cross-reference's.
- Any hand-authored second document -- Definition of done bars folding a second
  concept into this task.
