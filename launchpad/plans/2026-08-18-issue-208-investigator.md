Issue #208 — task: build the Investigator tool surface (search, read, git, run, test, logs, build-system)
Stated size: no Size line on this repo's Task template (same gap as #206/#207)  →  cap: 12 steps

ALREADY TRUE  (verified against git and the live repo, not notes)
  launchpad/project-intelligence/ exists (#206/#207, PRs #213/#214, not yet merged into
    `launchpad`): symbol.py, indexer.py, graph.py, plus their test files.
  No Investigator, tool registry, or any of the twelve named tool functions exist yet --
    `grep -rln "class Investigator\|def search_text\|TOOL_REGISTRY"` across
    launchpad/project-intelligence/ returns nothing.
  RepoQL's `rql read <uri> => history` / `=> blame` already proved out real git history/blame
    extraction in #206 (enrich_git_ownership()) -- the same primitive this task's
    inspect_git_history/git_blame tools need, not a new mechanism to discover.
  crates/buzz-core/Cargo.toml has real dependencies to ground inspect_dependency's worked
    example against (e.g. `nostr = { workspace = true }`).
  #208 has no stated dependency on #206 or #207 in its own issue body -- its Impacted
    components field does not name a location or a prerequisite task, confirmed before
    planning, not assumed.

STEP 1  [independent] Define the tool registry convention: each tool is a plain function, with a
        side-effect marker (READ_ONLY or EXECUTE) recorded per tool name in one place, matching
        the design doc's table exactly (only run_command and run_test are EXECUTE). Implement
        the three trivial file/dir wrappers as the first real tools: read_file, list_directory,
        inspect_logs (a log file is just a file to read; no separate mechanism).
        done when: a unit test asserts exactly {run_command, run_test} are marked EXECUTE and
        every other named tool is READ_ONLY.

STEP 2  [needs 1] Implement search_text (literal/regex search across the repo) and
        search_symbols (via RepoQL's Functions/Types views, same query shape #206 already
        proved). ← RUNS HERE
        done when: search_text for a known literal string and search_symbols for a known
        function name both return real matches from this repo, verified by cross-checking one
        result against a plain `grep`.

STEP 3  [needs 1] Implement find_references: real callers of a chosen symbol, not just text
        matches on its name -- reuse the resolved-qualified-name approach #206's
        with_called_by() already proved (a name match against indexed symbols, not a raw grep
        alone).
        done when: find_references for a real, already-known-to-have-callers symbol (e.g.
        is_shared_gated_kind, per #206/#207's own worked examples) returns its real callers,
        cross-checked against #207's own graph output for the same symbol.

STEP 4  [needs 1] Implement inspect_git_history and git_blame as thin wrappers over
        `rql read <uri> => history` / `=> blame`, the same primitive #206 already used.
        done when: for a chosen real symbol or file range, both tools' output matches raw
        `git log -L` / `git blame` output, checked by hand -- same verification shape #206
        already used for git_ownership.

STEP 5  [independent] Implement inspect_dependency: parse a crate's Cargo.toml and report a
        named dependency's declared version/source.
        done when: inspect_dependency("buzz-core", "nostr") returns the real entry from
        crates/buzz-core/Cargo.toml, cross-checked by reading that file directly.

STEP 6  [independent] Implement query_build_system: read-only introspection of what the build
        system would do, without building or running anything (e.g. `cargo metadata --no-deps`
        or `just --list` output, parsed rather than executed for effect).
        done when: query_build_system("buzz-core") returns real target/manifest information for
        that crate without having compiled or run anything (no build artifacts produced),
        verified by checking no new files appear under target/ from this call alone.

STEP 7  [needs 1] Implement run_command and run_test as the two EXECUTE-marked tools. Calling
        either surfaces the EXECUTE flag to the caller (e.g. printed or returned before the
        subprocess actually runs), not silently, per #208's own Definition of done.
        done when: calling run_command with a trivial real command (e.g. `echo`) and run_test
        with a fast real test target both print/return the EXECUTE flag before their output,
        and this is shown running, not just asserted.

STEP 8  [needs 2, 3, 4, 5, 6, 7] Document the design doc's investigation decision logic (check
        confidence first -> verify important claims even when confident -> investigate when not
        confident -> construct explanation) as the tools' calling convention, and wire a
        CLI/harness printing every tool's name, side-effect marker, and one real result.
        done when: running it prints all twelve tools with correct EXECUTE/READ_ONLY markers and
        a real result for each, matching the UserRepository-style investigation trace shape from
        the design doc.

PARALLEL  Step 1 and step 5 and step 6 touch no file another step needs first and could run as
          parallel subagents. Steps 2, 3, 4, 7 all extend the same growing investigator module
          and its registry, so -- same note as #206/#207 -- they are sequential in practice
          unless split into separate files up front.

GATES     Same as #206/#207: serina:review-code and serina:review-tests as scoped re-reviews
          after step 8, the only integration point. No SDD ledger applies (issue-driven,
          `--issue` flag) -- expected, not a defect.

BUDGET    Step 3 (find_references) is most likely to eat the budget -- the design doc's own
          done-when explicitly distinguishes "real callers" from "just text matches on its
          name", and getting that distinction right (not just wrapping a plain grep) is the
          same kind of work #206's with_called_by() needed, not a trivial wrapper like most of
          the other read-only tools.

OPEN      Whether run_command/run_test should have any allowlist or sandboxing beyond "print the
          EXECUTE flag before running" -- #208's own Definition of done only requires the flag
          to surface, not a containment mechanism, but a builder should not assume no further
          safety review is needed before these are used by an actual orchestrating agent (#211).
          Location: continuing launchpad/project-intelligence/ (Python), matching #206/#207's
          already-settled decision -- not re-opening that question here.
          This repo's Task template has no Size line at all (confirmed against #67 when planning
          #206) -- sizing above is this plan's own judgment call, not read from the issue.

LEFT OUT  Any actual orchestration deciding *when* to call which tool -- #208's own "Out of
          scope" explicitly assigns that to #211 (KnowledgeAgent).
          Any UI or chat surface for invoking these tools directly -- also explicitly out of
          scope per #208 itself.
          Sandboxing or resource limits on run_command/run_test beyond surfacing the EXECUTE
          flag -- see OPEN above.
