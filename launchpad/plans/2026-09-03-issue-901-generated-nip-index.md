Issue #901 — generate corpus document generated/nip-index.md
Stated size: no Size line on the issue; family task under parent PRD #621 -> cap: 5 steps

ALREADY TRUE
- The #633 generator framework (launchpad/project-intelligence/corpus/indexes.py) is
  merged on this base: builder discovery from index_defs/*.py, IndexSpec/GeneratedBody
  contracts, GenerationContext (valid_nodes, node.path, input_digest, rel_path), and
  full front-matter/body-skeleton rendering per templates/generated-index.md.
- 15 builders are already registered (glossary, index, decisions-index, api-index,
  capability-index, code-to-doc-map, concept-index, configuration-index, corpus-index,
  coverage, crate-index, database-index, decision-index, dependency-graph,
  doc-to-code-map); nip-index is not among them.
- AGENTS.md references "https://github.com/nostr-protocol/nips" and names several NIPs
  Buzz implements directly (NIP-29 groups, NIP-42 auth, NIP-50 search, NIP-10 threads,
  NIP-17 gift wraps). A literal-token scan of the corpus (verified this run, before any
  code was written) found 34 distinct `NIP-<digits>` tokens across 103 canonical nodes,
  418 occurrences in front matter and 513 in body text -- both channels carry the
  signal, and 11 files mention a NIP only in body text, so restricting to front matter
  alone would silently under-count.
- No canonical node's `evidence[].evidence` citation list contains a NIP token (NIPs
  are not file paths), so crate-index's "citation is a resolvable file path" classifier
  does not transfer as-is; the matching signal here is the literal `NIP-<digits>` token
  appearing anywhere in a canonical node's own file (front matter statement text or
  body prose), not a citation shape.
- Source-code identifiers that collide lexically (`nip11.rs`, `nip42.rs`, `nip29_group_id`,
  `nip44.dart`) are lowercase and/or unhyphenated and are excluded by construction from
  a case-sensitive `\bNIP-\d+\b` match -- verified against the corpus's own
  generated/doc-to-code-map.md rows, none of which match that pattern.
- Every literal token found this run is either already 2-digit zero-padded (NIP-01,
  NIP-05, NIP-07, NIP-09) or naturally 2+ digits (NIP-10 upward) plus one outlier,
  NIP-24242 (a Blossom media-auth event kind the corpus text itself calls "NIP-24242"
  rather than "kind 24242") -- no unpadded single-digit form (e.g. `NIP-1`) coexists
  with a padded one, so no padding-normalization ambiguity exists to resolve today.

STEP 1 [independent] Builder module index_defs/nip_index.py  <- RUNS HERE
  Determinism source: read each valid canonical node's own file
  (`node.path.read_text(encoding="utf-8")` -- the exact bytes already covered by
  ctx.input_digest, no working-tree read outside the canonical inputs, unlike
  crate-index's crates/*/Cargo.toml) and regex-scan the WHOLE file (front matter +
  body) with `re.compile(r"\bNIP-\d+\b")`, case-sensitive, no normalization of
  zero-padding. This is a cross-reference (NIP token -> mentioning nodes), the
  crate-index/code-to-doc-map shape, not a type-enum filter -- no single node.schema.json
  type fits "documents that mention a NIP". Known-NIP set is self-derived from the
  corpus's own mentions (no external nostr-protocol/nips fetch, no hardcoded list),
  keeping the generator fully offline and reproducible.
  SPEC: name nip-index, output_path generated/nip-index.md, node_id
  generated-nip-index, node_type governance (same reasoning crate-index.py and
  code_to_doc_map.py give: rows are NIP tokens, not canonical nodes of one
  front-matter type), audiences [agent, developer], relationships
  references->corpus-agents and implements->corpus-template-generated-index.
  Table: one row per distinct NIP token, sorted by (int(digits), token), columns
  NIP token / mentioning-node count / sorted mentioning node ids. Zero-match case
  renders an honest empty table, not a widened rule.
  done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list` shows
  nip-index, and `--only nip-index` writes generated/nip-index.md without error.

STEP 2 [needs 1] Generate and confirm stability
  Run the generator to write TARGET, then rerun and diff (git status --porcelain must
  be empty) and run `--check --only nip-index` (must exit 0).
  done when: two consecutive generations are byte-identical and --check exits 0.

STEP 3 [needs 1] Test file
  tests/test_index_nip_index.py, following test_index_crate_index.py's conventions
  (indexes.py loaded by path as corpus_indexes; generation into a tempdir corpus --
  this builder's determinism source is ctx.valid_nodes/node.path, entirely fixture-
  local, unlike crate-index's real-repo crates/ read). Cover: builder discovered with
  declared identity; two runs byte-identical; a fixture node whose body text (not
  front matter) contains a NIP token is still picked up (proves body-text scanning is
  real, not accidental); a fixture node whose only NIP-shaped text is lowercase/
  unhyphenated (e.g. `nip42.rs`) is excluded; two fixture nodes citing the same NIP
  token both appear, sorted, under one row; zero-NIP fixture corpus renders an honest
  empty table; front matter carries the declared node_id and type.
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
  done when: `git log` on task/901-generated-nip-index shows exactly one commit ahead
  of feature/621-generated-traceability, containing exactly those four files.

PARALLEL
- None within this plan; steps are a short chain (module -> generate -> test/validate
  -> commit). This task itself runs in parallel with the other #621 family builders,
  each isolated to its own worktree and its own new index_defs/ module.

GATES
- python3 launchpad/project-intelligence/corpus/indexes.py --check --only nip-index (exit 0)
- python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" (OK, >225 tests)
- python3 launchpad/project-intelligence/corpus/validate.py (exit 0)
- pre-commit verify-gate stamp earned by the real suite run as a sole command

BUDGET
- 1 new builder module (index_defs/nip_index.py), 1 generated file
  (generated/nip-index.md), 1 test file, this plan. No edits to indexes.py,
  validate.py, or any other builder module.

OPEN
- Whether a future NIP appears in exactly one of two spellings (padded vs. unpadded,
  e.g. `NIP-1` alongside `NIP-01`) that this generator would then list as two separate
  rows rather than merging -- not present in the corpus today (verified this run), so
  left as literal-token behavior rather than speculative normalization.

LEFT OUT
- Fetching or embedding the official nostr-protocol/nips list/titles -- would require
  network access at generation time, breaking offline reproducibility; the index only
  reports which NIP tokens the corpus itself already mentions, and where.
- Any hand-authored second document -- Definition of done bars folding a second
  concept into this task.
