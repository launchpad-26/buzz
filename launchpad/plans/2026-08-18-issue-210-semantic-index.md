Issue #210 — task: build SemanticIndex and the concept-retrieval pipeline
Stated size: no Size line on this repo's Task template (same gap as #206/#207/#208/#209)  →  cap: 10 steps

ALREADY TRUE  (verified against git and the live repo, not notes)
  This branch (task/210-semantic-index) is cut from origin/task/207-project-graph, which already
    contains #206's symbol.py/indexer.py (Symbol, build_index()) and #207's graph.py
    (ProjectGraph, edges_from(), reachable()) -- confirmed via `ls launchpad/project-intelligence/`
    showing symbol.py, indexer.py, graph.py, test_*.py present on this branch (they are absent on
    plain `launchpad`, since #213/#214 are not yet merged).
  #210's own issue body states a REAL dependency, unlike #208/#209: "Depends on #206
    (ProjectIndexer) for the content to embed and summarize" -- this is why this branch stacks on
    task/207-project-graph rather than branching off `launchpad` directly, matching #207's own
    precedent for a real (not assumed) dependency.
  No ConceptEntry, SemanticIndex, or embedding/summarization code exists anywhere in the repo --
    `grep -rln "class ConceptEntry\|class SemanticIndex"` returns nothing.
  The design doc (launchpad/Research/project-intelligence-layer-design.md § Data Model item 3,
    lines 167-181, and § Reasoning Rules "Concept retrieval", lines 374-398) gives the exact
    ConceptEntry schema, the pipeline shape (concept -> subsystem -> candidate symbols ->
    confirmed references), and three worked examples this task's own positive example should
    match the *shape* of (not the literal content -- those are fictional, this task's must be
    real against buzz-core).
  #207's graph.py already demonstrates the negative-case boundary from the OTHER side (STEP 5:
    a vague description has no symbol_id for reachable() to start from) -- this task's own
    negative case is the mirror: a flow-tracing question has no verified multi-hop answer from
    this pipeline, confirming the same documented boundary from #210's side.

STEP 1  [independent] Define ConceptEntry (scope, embedding, summary) matching the design doc's
        schema, and a SemanticIndex store skeleton (add(entry), get(scope)) keyed by scope.
        `embedding` is an immutable tuple of (token, weight) pairs, not a dict -- same reasoning
        as #209's MemoryEntry.evidence being a tuple: keeps the frozen dataclass genuinely
        hashable/immutable rather than holding a mutable reference a caller could edit in place.
        done when: constructing a ConceptEntry and round-tripping it through
        add()/get() returns all three fields unchanged.

STEP 2  [independent] Implement summarize_symbol(): a deterministic natural-language gloss built
        ONLY from #206's Symbol structural facts (qualified_name, kind, signature, calls, tests,
        config_dependencies, documentation_links) -- generated once, not guessed fresh per query,
        matching the design doc's own stated constraint on ConceptEntry.summary.
        done when: summarize_symbol() on a real Symbol from buzz-core (is_shared_gated_kind)
        produces a string containing its qualified_name and at least one real structural fact
        (e.g. a real entry from its tests[]), cross-checked against that Symbol's actual fields.

STEP 3  [independent] Implement tokenization (word-boundary plus camelCase/snake_case splitting,
        so `is_shared_gated_kind` decomposes into ["is","shared","gated","kind"]) and a
        bag-of-words frequency embedding, plus cosine_similarity() between two such embeddings.
        done when: cosine_similarity() of a vector against itself is 1.0 (within floating-point
        tolerance) and between two vectors sharing no tokens is 0.0 -- both checked with
        hand-computed inputs, not real symbols, so the math itself is verified independent of
        any indexing behavior.

STEP 4  [needs 1, 2, 3] SemanticIndex.from_symbols() builds TWO levels of ConceptEntry from real
        buzz-core Symbol records: one per symbol (scope=qualified_name), and one per FILE
        (scope=file path, aggregating that file's symbols' summaries/embeddings) -- the design
        doc's schema explicitly allows scope to be symbol_id OR file OR doc_section, and this is
        the "subsystem" level the pipeline names, not invented machinery. ← RUNS HERE
        done when: building from real buzz-core Symbol records produces at least one file-scoped
        ConceptEntry whose summary/embedding aggregates more than one real symbol's content,
        verified by inspecting it directly against the real symbols in that file.

STEP 5  [needs 4] Implement the two-stage search(): rank file-level ("subsystem") entries first,
        then rank symbol-level entries scoped to the top file(s) -- concept -> candidate
        subsystem(s) -> candidate symbols, as two literal ranking stages, not collapsed into one.
        done when: searching a real vague concept question against the buzz-core index first
        returns kind.rs as the top-ranked subsystem, then returns is_shared_gated_kind as the
        top-ranked symbol within it -- both stages shown in the test/output, not just a final
        flat rank.

STEP 6  [needs 5] Implement confirm_via_graph(): the pipeline's final confirmation step, calling
        directly into #207's ProjectGraph.edges_from() for tested_by/called_by edges on a
        candidate symbol -- real structural confirmation, not semantic similarity alone.
        done when: confirm_via_graph() on the STEP 5 candidate returns real tested_by/called_by
        edges matching #207's own already-proven edges for the same symbol (cross-checked
        against graph.py's own STEP 6 demo output for is_shared_gated_kind).

STEP 7  [needs 6] Wire find_it_for_me(): the full pipeline function tying concept -> subsystem ->
        candidate -> confirmation together into one call, returning both the ranked candidate and
        its structural confirmation.
        done when: find_it_for_me() on the STEP 5 concept question returns a result whose
        candidate matches STEP 5's top symbol and whose confirmation matches STEP 6's real edges,
        in one call.

STEP 8  [needs 7] Reproduce one design-doc-style worked concept-search example end to end against
        THIS repo's own code (not the doc's fictional OnboardingMailer example) -- a genuinely
        vague question that resolves to is_shared_gated_kind via subsystem -> candidate ->
        confirmed-reference, not a plain keyword match.
        done when: the chosen concept sentence contains no contiguous substring match of the
        actual function name (is_shared_gated_kind), yet find_it_for_me() still resolves to it as
        the top candidate with a real confirmation -- proving genuine token/concept overlap, not
        an accidental literal substring hit.

STEP 9  [needs 7] Demonstrate the negative case: pose the SAME 2-hop flow-tracing relationship
        #207's own reachable() demo already proves (tests::is_unshared_gated_event_author_always_allowed
        -> is_unshared_gated_event -> is_shared_gated_kind) through THIS pipeline instead, and show
        it cannot express or verify a multi-hop path the way ProjectGraph.reachable() does.
        done when: running the flow-tracing question through find_it_for_me() is shown NOT to
        produce a verified 2-hop path (no hop count, no path -- at best an unconfirmed single-
        symbol guess), contrasted directly against reachable()'s own verified path output for the
        identical relationship, printed side by side.

STEP 10 [needs 8, 9] Wire a final CLI printing both worked examples (positive concept resolution,
        negative flow-tracing boundary) end to end, matching #206/#207/#208/#209's demo style.
        done when: running it prints the positive example's full pipeline trace (concept ->
        subsystem -> candidate -> confirmation) and the negative example's contrast, using only
        real data from this repo -- no stubs.

PARALLEL  Steps 1, 2, and 3 touch no file another pending step needs first (2 only needs Symbol,
          3 is pure string/math) and could run as parallel subagents. Steps 4 through 10 all
          extend the same growing semantic_index.py module and its store, so -- same note as
          #206/#207/#208/#209 -- they are sequential in practice unless split into separate files
          up front.

GATES     Same as #206/#207/#208/#209: serina:review-code and serina:review-tests as scoped
          re-reviews after step 10, the only integration point. No SDD ledger applies (issue-
          driven, `--issue` flag) -- expected, not a defect.

BUDGET    Step 5 (two-stage search) is most likely to eat the budget -- getting a real worked
          example to correctly rank kind.rs as top subsystem AND is_shared_gated_kind as top
          symbol requires the bag-of-words scoring to behave sensibly on real summary text, which
          needs empirical checking against actual numbers (same kind of work #206/#207's worked
          examples needed), not just structural correctness like #209's reconciliation rule.

OPEN      Embedding representation is a bag-of-words frequency vector over a custom identifier-
          aware tokenizer, not a trained ML embedding model -- matches #210's own "out of scope:
          any embedding-model selection process beyond what's needed to demonstrate the pipeline
          once," but a human should confirm this lightweight stand-in is acceptable for now, not
          read this PR as having picked a production embedding strategy.
          top_k / how many candidates count as "the subsystem(s)" or "candidate symbols" isn't
          specified by the design doc -- this plan's own default is top_k=3 at each stage.
          Whether summary generation should ever call an LLM for real natural-language phrasing,
          rather than a deterministic structural template -- not specified; this plan uses a
          deterministic template only, consistent with every other module in this session having
          no LLM/API dependency.

LEFT OUT  Any subsystem grouping finer than "by file" (e.g. by module, by directory, by feature
          area) -- #206's Symbol schema doesn't currently carry that grouping, so file is the
          coarsest real structural unit available without inventing new extraction #206 doesn't
          do.
          Building ProjectGraph traversal itself -- #207's responsibility; this task only calls
          into it for the confirmation step, per #210's own issue text.
          Any embedding-model selection beyond the lightweight bag-of-words implementation --
          explicit in #210's own issue text.
          Incremental re-indexing when a file changes (design doc's "Incremental Knowledge
          Maintenance" item 4, recomputing embeddings for changed chunks only) -- not requested by
          #210's Definition of done.
