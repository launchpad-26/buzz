Issue #207 — task: build a ProjectGraph with typed edges and traversal over ProjectIndexer output
Stated size: no Size line on this repo's Task template (see OPEN, same gap as #206)  →  cap: 12 steps

ALREADY TRUE  (verified against git and the live repo, not notes)
  #206 is implemented (PR #213, not yet merged into `launchpad` -- this plan's branch stacks on
    task/206-project-indexer). launchpad/project-intelligence/indexer.py's build_index(crate)
    returns Symbol records for buzz-core (453 symbols) with calls[]/called_by[] already resolved
    to qualified names, tests[], config_dependencies[], and documentation_links[] populated.
  No ProjectGraph, Edge type, or traversal query exists yet -- `grep -rln "class ProjectGraph\|
    def reachable\|Edge("` across launchpad/project-intelligence/ returns nothing.
  A real, verified 2-hop call chain exists in the already-indexed buzz-core data:
    tests::is_unshared_gated_event_author_always_allowed -> is_unshared_gated_event ->
    is_shared_gated_kind (kind.rs:1006-1010, :234, :219-221) -- confirmed by reading the source
    directly, not assumed.

STEP 1  [independent] Define a typed Edge record (source, target, edge_type, evidence) and the
        set of edge-type names the design doc names (imports, calls, called_by, configured_by,
        tested_by, documented_by, deployed_by, owns, depends_on).
        done when: a unit test constructs edges of at least 4 distinct types and asserts every
        field.

STEP 2  [needs 1] Build a ProjectGraph that ingests a list of Symbol records (from #206's
        build_index) and materializes the 4 edge types directly derivable from what #206 already
        produces: calls/called_by (already present on each Symbol), tested_by (inverse of
        tests[]), configured_by (inverse of config_dependencies[]), documented_by (inverse of
        documentation_links[]). ← RUNS HERE
        done when: running against buzz-core's indexed symbols produces a graph whose edges for
        the worked-example symbol (is_shared_gated_kind) match that symbol's own Symbol record
        fields exactly (calls[], called_by[], tests[], etc.), verified by comparing the two
        directly.

STEP 3  [needs 2] Implement reachable(from_symbol, edge_types, max_hops) -> list of
        (symbol, hop_distance, path), via BFS over the materialized edges.
        done when: querying reachable() from
        tests::is_unshared_gated_event_author_always_allowed with edge_types=["calls"],
        max_hops=2 returns is_unshared_gated_event at hop 1 and is_shared_gated_kind at hop 2,
        matching the real chain confirmed in ALREADY TRUE.

STEP 4  [needs 3] Demonstrate the graph answers something the flat Symbol record alone could
        not: is_shared_gated_kind's own record does not list
        tests::is_unshared_gated_event_author_always_allowed anywhere (it is two hops away, not
        one) -- only graph traversal finds it.
        done when: this is shown explicitly -- printing is_shared_gated_kind's own called_by[]
        (which does not include the 2-hop test) alongside the reachable() result that does.

STEP 5  [needs 2] Demonstrate the negative case: a vague, terminology-free query (no starting
        symbol name given, e.g. "what checks whether an event is gated") against the graph
        returns nothing useful or requires a symbol name up front -- confirming the documented
        boundary with #210 (SemanticIndex), which #207 explicitly excludes.
        done when: this limitation is shown running, not just asserted in prose -- e.g.
        reachable() called with no valid starting symbol_id raises or returns empty, and the
        output states plainly that finding a starting point from a vague description is out of
        this graph's job.

STEP 6  [needs 2] Wire a CLI/harness entry point printing every edge for one chosen real
        symbol, each labelled with its type (e.g. "is_shared_gated_kind --called_by-->
        is_unshared_gated_event"), matching the design doc's checkout-flow trace shape -- not a
        single untyped list.
        done when: running it against is_shared_gated_kind in buzz-core prints every edge with
        an explicit, correct type label.

PARALLEL  Step 1 is independent of everything. Steps 2-6 all read or write the same growing
          graph module and the same materialized edge set, so they are sequential in practice
          regardless of their logical ordering -- state clearly if the implementer splits them
          into separate files to parallelize, matching #206's own PARALLEL note.

GATES     Same as #206: serina:review-code and serina:review-tests as scoped re-reviews after
          step 6, the only integration point. No SDD ledger applies to this plan format (issue-
          driven, `--issue` flag) -- expected, not a defect.

BUDGET    Step 3 (the BFS traversal) is most likely to eat the budget -- not because BFS itself
          is hard, but because verifying it against a REAL multi-hop chain (not a synthetic
          fixture) requires finding one in the actual indexed data first, the way ALREADY TRUE
          already did once for this plan.

OPEN      Which subset of the design doc's 8 edge types this task actually implements. This plan
          implements 4 (calls/called_by, tested_by, configured_by, documented_by) -- the ones
          #206's Symbol schema already produces. The other 4 (imports, deployed_by, owns,
          depends_on) need extraction #206 does not currently do (Rust `use` statements,
          deployment units, Cargo.toml dependencies) and are not "ingesting a ProjectIndexer's
          Symbol records" as #207's own Objective states it -- a builder must not silently treat
          4-of-8 as either sufficient or insufficient; it is a real scope question for whoever
          reviews this.
          Whether graph storage should be anything beyond in-memory for this task -- #207's own
          "Out of scope" already defers persistent storage, so in-memory is assumed, not decided
          here.
          This repo's Task template has no Size line at all (confirmed against #67 when planning
          #206) -- sizing above is this plan's own judgment call, not read from the issue.

LEFT OUT  imports, deployed_by, owns, depends_on edge types -- see OPEN above; these need new
          extraction beyond #206's current output, which is a larger task than "ingest #206's
          Symbol records."
          Persistent/database-backed graph storage -- explicitly out of scope per #207 itself.
          Cross-crate traversal -- matches #206's own single-crate (buzz-core) scope; a call
          crossing into buzz-relay (like the real is_shared_gated_kind caller found while
          building #206) is not reachable from a buzz-core-only graph, and this task does not
          index a second crate to fix that.
