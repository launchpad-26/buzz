Issue #891 — generate corpus document generated/corpus-index.md
Stated size: none given in the issue  →  batch brief for Feature #621 caps every generated-document task  →  cap: 5 steps

ALREADY TRUE  (verified against the worktree at a7b215bb2, not notes)
  - Worktree __worktrees/task-891-generated-corpus-index exists on branch
    task/891-generated-corpus-index, based on feature/621-generated-traceability
    (carries #633's framework plus five merged builders: api-index,
    capability-index, decisions-index, glossary, index).
  - #638's builder (index_defs/index.py) already owns node id `corpus-index`
    and output INDEX.md — the full per-node table of contents (every valid
    node's id, type and path, grouped by top-level directory). This task's
    node id is `generated-corpus-index` and its output is
    generated/corpus-index.md; neither collides with any registered builder
    name or output path (checked via discover_builders()).
  - Because INDEX.md already lists every node per-row, this document must be a
    genuinely distinct view: an aggregate stats summary (counts by type,
    status, audience and top-level directory), naming no individual node.
  - On this base build_context finds 205 valid nodes, 0 invalid; types
    {agent 2, architecture 48, capabilities 69, development 4, governance 46,
    layers 36}; statuses {active 47, draft 158}; audiences are multi-valued
    per node (agent 193, developer 187, operator 86, reviewer 154).
  - Relationship targets corpus-agents and corpus-template-generated-index
    both resolve on this base (checked in ctx.node_ids);
    `generated-corpus-index` is not yet taken. The INDEX.md node
    (`corpus-index`) is NOT targeted by a relationship because it is not on
    origin/launchpad — the distinction is stated in prose instead.
  - tests/test_indexes.py already tolerates any number of shipped builders
    (five exist and the base suite passes), so no shared-file edit is needed.

STEP 1  [independent]  <- RUNS HERE
        Write the builder module
        launchpad/project-intelligence/corpus/index_defs/corpus_index.py
        exposing SPEC: name corpus-index, output_path
        generated/corpus-index.md, node_id generated-corpus-index, node_type
        governance (corpus-infrastructure precedent set by README, standards/
        and index.py — justified in the module docstring), audiences
        agent+developer+reviewer, relationships references→corpus-agents and
        implements→corpus-template-generated-index. generate(ctx) renders
        count tables only: by type, by status, by audience (noting the
        multi-valued sum), by top-level directory (corpus root first, then
        sorted directory names), plus the invalid-file count — and an explicit
        paragraph distinguishing this summary from INDEX.md's per-node
        listing, so a reader knows which to consult. No individual node id or
        path is ever emitted. extra_evidence records the counts at the input
        digest.
        done when: python3 launchpad/project-intelligence/corpus/indexes.py
        --list prints "corpus-index  generated/corpus-index.md".

STEP 2  [needs 1]
        Generate the document: indexes.py --only corpus-index writes
        launchpad/docs/corpus/generated/corpus-index.md. Never hand-edit it;
        wrong content means fixing the builder and regenerating.
        done when: a second --only corpus-index run leaves git status
        --porcelain unchanged for the file, and --check --only corpus-index
        exits 0.

STEP 3  [needs 1]
        Focused test launchpad/project-intelligence/corpus/tests/
        test_index_corpus_index.py following test_index_index.py conventions
        (path-load indexes.py as corpus_indexes, real corpus root read-only):
        builder discovered with the contracted name/output/node_id/type; two
        independent renders byte-identical; front matter starts with id
        generated-corpus-index + type governance; every type/status count in
        the rendered tables equals a recount over ctx.valid_nodes; no valid
        node's rel_path appears in the body (the no-per-node-rows rule); the
        INDEX.md distinction sentence is present.
        done when: python3 -m unittest that file passes.

STEP 4  [needs 2, 3]
        Full gate: python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py" all OK
        (baseline 225 + new), python3
        launchpad/project-intelligence/corpus/validate.py exits 0, then git
        add builder+generated+test+plan and git commit -s with the inclusion
        rule named in the body.
        done when: the signed commit exists and the suite output says OK.

PARALLEL
  Steps 2 and 3 both depend only on STEP 1 and touch disjoint files, so they
  could run in parallel. Sibling batch tasks add their own index_defs/
  modules; discovery's duplicate-name/output check fails loudly on collision,
  and this task's identifiers collide with none of the five shipped builders.

GATES
  - Commit gate: the full unittest discover run as the sole command in its
    own call, then a separate git add/commit -s call. If the gate refuses
    with no stamp found: stop and report, never touch the stamp, never
    --no-verify.
  - validate.py exit 0 (pre-existing UNVERIFIED notices are non-fatal).
  - No-change rerun produces no diff (issue DoD, checked in STEP 2).

BUDGET
  One builder module (~110 lines), one generated document, one focused test
  (~110 lines), this plan. No edits to indexes.py, validate.py,
  test_indexes.py, any shared file, or any hand-authored corpus node.

OPEN
  - Whether the integrator wants the summary regenerated once at integration
    time — every sibling merge changes the canonical inputs, so this
    document's counts and digest go stale with each merge until the branch's
    final regeneration pass (the base already carries one such
    regeneration-stability commit; the same pass covers this builder).

LEFT OUT
  - Any per-node listing rows — INDEX.md (node `corpus-index`, builder
    index.py) already owns the complete id/type/path table; duplicating it
    would make two near-identical documents, which the dispatch explicitly
    forbids.
  - Graph-shape statistics (edge counts, orphans, broken edges) — plausibly
    a sibling generated document's subject in this batch; keeping this node
    to front-matter and path aggregates avoids a cross-task duplication.
  - A relationship targeting `corpus-index` (INDEX.md) — that node exists
    only on the integration branch, not origin/launchpad; the brief limits
    relationships to targets resolvable there.
