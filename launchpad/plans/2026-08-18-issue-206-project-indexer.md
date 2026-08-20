Issue #206 — task: build a ProjectIndexer producing Symbol records for one target
Stated size: no Size line on this repo's Task template (see OPEN)  →  cap: 12 steps

ALREADY TRUE  (verified against git and the live repo, not notes)
  launchpad/Research/project-intelligence-layer-design.md exists (merged via PR #191) and
    defines the exact Symbol record schema this task must produce.
  No Symbol record type, ProjectIndexer implementation, or CLI exists yet anywhere in this
    repo — `grep -rln "ProjectIndexer\|struct Symbol\b"` across *.rs/*.ts/*.py returns nothing.
  RepoQL is available in this environment and already provides a `Functions` view with
    `uri, file, name, qualified_name, function_kind, declaring_type, signature, return_type,
    parameters, start_line, end_line` (confirmed via `DESCRIBE SELECT * FROM Functions LIMIT 0`),
    plus `read(<uri>#symbol=X => history)` and `=> blame` modifiers for git history/ownership.
    This is most of what a from-scratch AST parser would otherwise need to build.

STEP 1  [independent] Define the Symbol record type/schema in code, matching the design
        doc's fields exactly (symbol_id, kind, qualified_name, defined_at, signature, calls[],
        called_by[], tests[], config_dependencies[], documentation_links[], git_ownership).
        done when: a unit test constructs one Symbol value by hand and asserts on every field.

STEP 2  [needs 1] Adapter: query RepoQL's Functions view for ONE target crate (recommend
        buzz-core — small, foundational, well-defined) and map each row into a Symbol record
        populating kind, qualified_name, defined_at, signature, and calls[] (a best-effort scan
        of the symbol's own body/structure for outbound call sites — precision can improve
        later). ← RUNS HERE
        done when: running the adapter against buzz-core prints a real, populated Symbol
        record for a specific known function, and the populated fields visibly match RepoQL's
        own `read()` output for that same symbol.

STEP 3  [needs 2] Populate called_by[] as a real inverse index, materialized at index time —
        for each symbol produced in step 2, find its callers (RepoQL's exact mechanism for
        this is not yet confirmed; a plain text/regex search for the symbol's qualified name
        across the target is an acceptable fallback for this task's scope) and build the
        inverse mapping once, not per query.
        done when: a symbol known to have at least one caller in buzz-core lists that caller
        in called_by[], cross-checked by hand against a manual search for the call site.

STEP 4  [needs 2] Populate git_ownership (primary_authors, history) using RepoQL's
        `=> history` and `=> blame` modifiers for each symbol's line range.
        done when: for one chosen symbol, the indexer's git_ownership.history list matches
        `git log -L <range>` output for that same range, checked by hand.

STEP 5  [needs 2] Populate tests[] — search for test symbols/files referencing each symbol's
        qualified name and attach matches.
        done when: a symbol with an obvious existing test shows that test in tests[].

STEP 6  [needs 2] Populate config_dependencies[] — scan each symbol's body for env-var/
        config-key reads (e.g. `std::env::var(...)`) and attach the names found.
        done when: a symbol known to read an env var shows that variable's name in
        config_dependencies[].

STEP 7  [needs 2] Populate documentation_links[] — search this repo's own markdown (README,
        CONTRIBUTING, launchpad/) for mentions of each symbol's qualified name or file, and
        attach matches.
        done when: a symbol documented somewhere in this repo's markdown shows that doc's
        path in documentation_links[].

STEP 8  [needs 3, 4, 5, 6, 7] Wire a CLI or test-harness entry point that prints one full
        Symbol record end to end, matching the design doc's PaymentService.processPayment
        worked-example shape.
        done when: running it against a real buzz-core symbol prints all seven enrichment
        fields, populated or explicitly empty (e.g. "no tests found"), legibly formatted.

PARALLEL  Step 1 is independent of everything. Steps 4, 5, 6, and 7 are logically independent
          enrichments of the same symbol set step 2 produced, and COULD run as parallel
          subagents if the implementer splits them into separate files/modules from the start.
          If they instead land in one growing indexer module (the likely default), they are
          sequential regardless of their logical independence, per this skill's own rule that
          two steps touching the same file are sequential. State which shape was chosen before
          parallelizing.

GATES     This repo's actual review methodology (per launchpad/AGENTS.md and prior plans in
          this directory) runs serina:review-code and serina:review-tests as scoped
          re-reviews rather than named "verify-*" skills — apply both after step 8, the only
          integration point. No SDD ledger exists for this plan format (STEP N headings, not
          `### Task N:`), so `check-ledger.sh` correctly reports it inapplicable rather than
          passing — treat that as expected, not a defect, per this skill's own guidance for
          the serina:plan-issue methodology.

BUDGET    Step 3 (called_by[] as a real inverse index) is most likely to eat the budget — the
          exact RepoQL mechanism for "who calls this symbol" was not confirmed while writing
          this plan (a `related()`-style table function did not exist under that name), so the
          implementer needs to explore RepoQL's actual capability first or commit to the
          text-search fallback named above.

OPEN      Which crate/language to target first — buzz-core is a recommendation, not a mandate.
          The exact RepoQL mechanism (or fallback) for finding callers (step 3).
          Where this code lives — a new Rust crate, a script, something else — neither the
          design doc nor task #206 commits to an implementation location.
          This repo's Task template has no Size line at all (confirmed against #67) — sizing
          above is this plan's own judgment call, not read from the issue.

LEFT OUT  calls[] precision beyond a best-effort body scan (step 2) — full call-graph accuracy
          is really #207's (ProjectGraph) concern once symbols exist to build edges from;
          revisit if #207 needs stronger guarantees than this task provides.
          Any language/crate beyond the first target — proving the schema and pipeline once is
          the point of this task, not covering the whole repo.
          Incremental/symbol-scoped re-indexing on file change (design doc's own item 9) — not
          filed as its own task yet in this decomposition; flag for the PRD if it should be.
