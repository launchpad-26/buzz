Issue #1304 -- generate specifications/implemented-documents.md (parent PRD #621, sibling family #1302-#1306)
Stated size: no `Size` line on the issue -> single generated-document task -> cap: 5 steps (self-imposed, matching sibling #1302's plan).

ALREADY TRUE  (verified against the worktree, not notes)
  Base branch `feature/621-generated-traceability` carries the merged #633 generator
    framework (`launchpad/project-intelligence/corpus/indexes.py`) with 25 registered
    builders, including `index_defs/specifications_index.py` (#1302) -- the closest
    precedent for scoping to the `specifications/` path prefix.
  `launchpad/docs/corpus/specifications/INDEX.md` is the only file under `specifications/`
    on this base; it is itself a generated builder output (`specifications-index`),
    excluded from canonical inputs. No specification-shaped canonical node exists yet
    (`indexes.py --list` plus a filesystem check confirm this), so any inclusion rule
    scoped to that prefix matches zero nodes today.
  `node.schema.json`'s `status` enum is `[draft, active, deprecated, retired, flagged]`
    -- no `implemented` literal exists anywhere in the schema.
  `relationships.schema.json` defines `implements` as "source is the concrete realization
    of target" with generated inverse `implemented-by`, already computed by `indexes.py`'s
    `build_context` into `ctx.inverse_edges['implemented-by']` (target id -> sorted source
    ids) -- no new graph derivation needed.
  `corpus-template-specification` (`launchpad/docs/corpus/templates/specification.md`)
    exists and is merged; #1302's builder already cites it in its own empty-listing
    message, giving precedent for citing it here too.

STEP 1  [independent]  Decide and record, in the new builder module's own docstring, the
        "implemented" interpretation the issue's ambiguity note raises: (a) a specification
        node's `ctx.inverse_edges['implemented-by']` entry is non-empty (something in the
        corpus declares `implements` targeting it) -- grounded in
        `relationships.schema.json`'s own directionality text; (b) `status: active` read as
        a loose synonym for "implemented" -- weaker, inferential, no schema grounding for
        the word itself. Choose (a), name (b) as the rejected alternative, and scope the
        specification population to the `specifications/` path prefix (matching #1302's
        precedent, since #1303 does not exist yet to compare against).
        done when: the docstring states both candidates, names the chosen one and why, and
        matches what STEP 2 actually implements.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/project-intelligence/corpus/index_defs/implemented_documents.py`
        exposing `SPEC` (dict form): `name="implemented-documents"`,
        `output_path="specifications/implemented-documents.md"`,
        `node_id="specifications-implemented-documents"`, `node_type="governance"`
        (corpus-about-corpus meta-document, same reasoning as #1302's
        `specifications_index.py`), `audiences=("agent","developer","reviewer")`,
        `relationships=({"type":"references","target":"corpus-agents"},
        {"type":"implements","target":"corpus-template-generated-index"},
        {"type":"references","target":"corpus-template-specification"})`.
        `generate(ctx)` selects nodes where `ctx.rel_path(n).startswith("specifications/")`
        AND `ctx.inverse_edges.get("implemented-by", {}).get(n.id)` is non-empty, sorted by
        path, rendered as a table (id, path, status, implementing source ids). Body
        includes an explicit `## Interpreting "implemented"` subsection stating the chosen
        interpretation and the rejected alternative in the document's own prose (not only
        the module docstring), an honest empty-listing branch pointing at
        `corpus-template-specification`, and `includes`/`excludes`/`not_covered` bullets
        naming the path scope, the `implemented-by` inverse-edge test, and the excluded
        `status: active` reading. Then run
        `python3 launchpad/project-intelligence/corpus/indexes.py --only implemented-documents`.
        done when: the command exits 0 and writes
        `launchpad/docs/corpus/specifications/implemented-documents.md`.

STEP 3  [needs 2]  Regenerate a second time and confirm `git status --porcelain` shows no
        diff on the output file; run
        `python3 launchpad/project-intelligence/corpus/indexes.py --check --only implemented-documents`.
        done when: both checks show no diff and the `--check` run exits 0.

STEP 4  [needs 2]  Add
        `launchpad/project-intelligence/corpus/tests/test_index_implemented_documents.py`
        following `test_index_specifications_index.py`'s conventions (throwaway temp-dir
        corpus, `indexes.py` loaded by path as `corpus_indexes`). Cases: builder discovered
        with declared identity; two runs byte-identical; a fixture node under
        `specifications/` with an inbound `implements` edge appears in the listing while one
        without an inbound edge and one outside the `specifications/` prefix do not; the
        real no-fixture-corpus case renders the honest empty-listing text naming
        `corpus-template-specification`; front matter carries
        `id: "specifications-implemented-documents"` and `type: "governance"`.
        done when: the new test module passes standalone
        (`python3 -m unittest launchpad/project-intelligence/corpus/tests/test_index_implemented_documents.py`
        run via its discover-compatible path).

STEP 5  [needs 3, 4]  Run `python3 launchpad/project-intelligence/corpus/validate.py`
        (must exit 0; pre-existing UNVERIFIED notices are non-fatal). Run the full
        `unittest discover` command from the task brief's commit gate as the sole prior
        command. Self-review the diff line by line against the issue's DoD. Commit the
        builder module, generated output, test module, and this plan file as one signed
        commit.
        done when: `validate.py` exits 0, the full discover run reports OK, and one signed
        commit exists on `task/1304-specifications-implemented-documents` containing
        exactly those four files.

PARALLEL  STEPs 3 and 4 both depend only on STEP 2 (the builder existing) and touch
          disjoint files (generated output vs. new test module) -- no ordering dependency
          between them; both must be satisfied before STEP 5 begins.

GATES     `python3 launchpad/project-intelligence/corpus/indexes.py --check --only
          implemented-documents` must exit 0. `python3
          launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m
          unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
          must report OK before commit. `review-adjudicate` and the cross-model final-review
          pass are explicitly deferred (batch mode, self-review only per the task brief).

BUDGET    One new builder module (~120-160 lines, in line with `specifications_index.py`'s
          152 and `dependency_graph.py`'s 281), one generated Markdown file, one test module
          (~130-160 lines, in line with `test_index_specifications_index.py`'s 162), this
          plan file. No edits to `indexes.py` or any other shared framework file -- the
          add-a-file-only contract.

OPEN      Whether a future specification-shaped node's `implements` edge targeting
          `corpus-template-specification` itself should also count toward "implemented" (a
          template-wide reading) is deliberately NOT decided here: this builder's
          `implemented-by` check is per-specification-node (something implemented THIS
          specific spec), not a check against the template edge. Left explicit rather than
          silently resolved, since the issue's own ambiguity note only addresses the
          per-node reading.

LEFT OUT  Interpretation (b) (`status: active` as "implemented") is documented and
          explicitly rejected, not implemented as a fallback or secondary listing -- adding
          it as an alternate view would blur the one definition this node commits to.
          No edit to `index_defs/specifications_index.py` or any other existing builder --
          this task adds exactly one new file, per the framework's add-a-file-only
          contract.
          No attempt to backfill a real specification-shaped node or an `implements` edge
          into the corpus to make the listing non-empty -- widening the rule or fabricating
          content to look fuller is explicitly barred by the issue brief and
          `standards/generated-content.md`.
