Issue #571 — task: make knowledge.explain(depth) actually render at the requested depth
Stated size: none given (asked Serina 2026-09-03: "more than an hour")  →  cap: 12 steps

ALREADY TRUE  (verified against the repository, not notes)
  classify_depth() (question.py:124) already produces all six Depth values (SUMMARY,
    ONBOARDING, IMPLEMENTATION, TRACE, RATIONALE, IMPACT) correctly, with its own test
    coverage in test_question.py -- untouched, explicitly out of scope for #571.
  investigate() (investigation.py) already gates the history stage on
    `depth == "RATIONALE"` (temporal_state == "HISTORY" or depth == "RATIONALE") -- the
    ONE existing depth-conditional behaviour in the pipeline, pre-dating #571. Not to be
    duplicated or touched.
  impact(agent, symbol) (knowledge.py:203) already computes direct/secondary dependents
    via `reachable(agent.graph, symbol, ("called_by",), max_hops=IMPACT_SECONDARY_HOPS)`,
    split into two FACT claims that are "never merged" -- exactly the shape #571's IMPACT
    depth needs, reusable as-is.
  render(answer) (answer.py:165) takes one argument today and ignores depth entirely.
    Every test in test_answer.py (320 lines, RenderTest class especially) calls it with
    exactly one argument and must keep passing unmodified -- this plan does not touch any
    existing test_answer.py assertion.
  Answer (answer.py:71, frozen dataclass) has no `depth` field today.
  knowledge_agent.py's run() (line 117) already threads an explicit `depth` override into
    a rebuilt Question (lines 130-138) before calling assemble() -- but assemble() never
    reads question.depth onto the Answer it returns.
  explain(agent, symbol, depth) (knowledge.py:175) forwards depth to agent.answer() and
    nothing else; CONTRACT.md:127-129 documents the exact defect #571 exists to fix,
    naming #571 by number.
  CONTRACT.md §7 (Reconciliation table, row 1) and §4's explain() entry both state the
    current defect as "Open -- #571."

DECIDED WITH SERINA (2026-09-03, both her calls, both taken as given below)
  IMPACT depth: explain(agent, symbol, "IMPACT") delegates to impact()'s existing
    graph-based direct/secondary computation, rather than approximating with only
    findings.callers (which has no secondary/2-hop data and would under-deliver the DoD's
    "direct and secondary dependents, stated separately").
  Plan size: capped at 12 steps ("more than an hour" bucket).

STEP 1  Add `depth: Depth | None = None` to Answer (answer.py)                     [independent]
        Import Depth from question.py (no cycle: question.py imports only from
        memory.py today).
        done when: `Answer(question="q", depth="TRACE").depth == "TRACE"` and
        `Answer(question="q").depth is None`; full test_answer.py suite still 100% green
        unmodified.

STEP 2  assemble() (assemble.py) stamps `depth=question.depth` onto its Answer    [needs 1]
        Applies to both the not-located branch and the located branch.
        done when: a hermetic assemble()-level test, given a Question built with
        depth="TRACE", asserts `assemble(...).depth == "TRACE"`.

STEP 3  render() (answer.py) branches on `answer.depth`                [needs 1] ← RUNS HERE
        `None` and `"IMPACT"` keep today's exact unrestricted, omit-if-empty
        behaviour (zero change for both). The other five depths get their own
        section selection:
          SUMMARY       -- ONE paragraph, no other section. Content is the first claim
                           whose entry_class == "FACT" (its `statement` text never
                           contains a citation -- verified_fact() puts the path only in
                           `evidence`, per verify.py:95-97); falls back to short_answer
                           if there is no FACT claim.
          ONBOARDING     -- Short answer + How it works + Important files +
                           Things to be aware of. Omits Relevant flow and Sources
                           ("no deep internals").
          IMPLEMENTATION -- Short answer + How it works + Important files + Sources
                           (full citations = "line references"). Omits Relevant flow
                           and Things to be aware of.
          TRACE          -- Short answer + Relevant flow + Sources (the full traversal,
                           already built in Flow format by assemble()). Omits How it
                           works, Important files, Things to be aware of.
          RATIONALE      -- Short answer + Things to be aware of + Sources, where
                           Sources is filtered to claims with temporal_state == "HISTORY"
                           or entry_class == "TEAM_KNOWLEDGE" only -- the generic
                           "X is defined as Y" WORKING/FACT claim is excluded.
        done when: `render(Answer(question="q", depth="SUMMARY", short_answer="x",
        important_files=("a.rs",), claims=(Claim(statement="sym is defined as fn foo()",
        entry_class="FACT", evidence=("a.rs:1",)),)))` contains no match for
        `re.search(r"\S+\.\w+:\d+", rendered)` and has exactly one `## ` heading; each of
        the other four depths renders its stated section set against a hand-built
        multi-field Answer fixture, verified by heading-list equality (same pattern as
        the existing `test_sections_render_in_the_design_doc_order`).

STEP 4  explain() (knowledge.py) special-cases `depth == "IMPACT"`                 [needs 1]
        Returns `dataclasses.replace(impact(agent, symbol), depth="IMPACT")`
        instead of calling `agent.answer(...)`.
        done when: `explain(agent, symbol, "IMPACT").short_answer ==
        impact(agent, symbol).short_answer` and `explain(agent, symbol,
        "IMPACT").depth == "IMPACT"`, asserted against test_knowledge.py's existing
        built-agent fixture.

STEP 5  Regression test: four depths share one identical claim set             [needs 2]
        SUMMARY/ONBOARDING/IMPLEMENTATION/TRACE explain() answers for the same
        symbol share one identical `.claims` tuple, differing only in `.depth`
        and which fields render. RATIONALE and IMPACT are excluded from this
        comparison -- RATIONALE legitimately gains history claims via the
        pre-existing stage gate, IMPACT is a legitimate different method via
        STEP 4's delegation; both are pre-existing, documented exceptions, not
        new ones.
        done when: the test passes, and fails if temporarily run against a version of
        assemble() that does not stamp depth (i.e. it is actually pinned to STEP 2's
        change, not vacuously true).

STEP 6  Six DoD tests, one per depth, each pinning its one unique property   [needs 3, 4]
        SUMMARY -- no path-like regex match anywhere in the rendered output;
        ONBOARDING -- "## Important files" present, "## Sources" absent;
        IMPLEMENTATION -- "## Sources" present with a `path:line`-shaped
        citation, "## Relevant flow" absent; TRACE -- "## Relevant flow"
        present, "## How it works" absent; RATIONALE -- "## Sources" present
        but the generic "is defined as" FACT line absent, a HISTORY- or
        TEAM_KNOWLEDGE-derived line present; IMPACT -- short_answer matches
        `\d+ direct and \d+ secondary`.
        done when: all six pass, and each fails individually if run against the
        pre-STEP-3/pre-STEP-4 code (confirm by temporarily reverting one change at a
        time, not by inspection alone).

STEP 7  A hermetic RATIONALE-filter boundary test in test_answer.py            [needs 3]
        An Answer with one WORKING-state FACT claim, one HISTORY-state
        INFERENCE claim, and one TEAM_KNOWLEDGE claim, asserting render() at
        RATIONALE depth includes the HISTORY and TEAM_KNOWLEDGE lines under
        Sources and excludes the WORKING FACT line.
        done when: test passes. This is the step most likely to catch an off-by-one in
        the filter condition (e.g. `==` vs `!=`, or filtering on entry_class alone and
        dropping a HISTORY-state FACT that isn't TEAM_KNOWLEDGE) that STEP 6's coarser
        assertions could miss.

STEP 8  Full-suite regression                                             [needs 2, 3, 4]
        `python3 -m unittest discover -s launchpad/project-intelligence -p
        "test_*.py"` (the whole existing suite, not just the new files) green
        -- confirms nothing in worked_answer.py, worked_trace.py, or
        knowledge.py's own `__main__` demo block (all three call
        `render(answer)` with one argument) broke now that Answer carries an
        extra defaulted field.
        done when: the discover run reports 0 failures, 0 errors.

STEP 9  Update CONTRACT.md's explain() entry and reconciliation table            [needs 8]
        §4's explain() entry and §7's reconciliation-table row 1 currently
        document the SUMMARY/TRACE-identical defect and cite #571 as the open
        issue describing it -- update both once the fix is verified so the
        next reader (this contract is already cited by #553 and by
        benmitchell11's PR #2001 reviews) isn't told about a defect that no
        longer exists.
        done when: `grep -n "#571" CONTRACT.md` no longer returns a line describing the
        defect as open (a closing/historical note, if kept, is fine).

PARALLEL  After STEP 1 lands, STEPs 2 (assemble.py), 3 (answer.py), and 4 (knowledge.py)
          touch three disjoint files and only depend on STEP 1 -- these three can run as
          parallel subagents. STEPs 5, 6, and 7 add tests that plausibly land in the same
          two test files (test_answer.py, test_knowledge.py per the issue's own Impacted
          Components list) -- treat them as sequential to each other unless whoever
          implements them explicitly splits into non-overlapping test classes/files
          first, since two steps editing the same file are sequential regardless of how
          unrelated they look. STEP 8 and STEP 9 are each single-owner integration/doc
          steps, not parallelizable.
GATES     review-code after STEP 8 (real behavioural branching across three files,
          worth an adversarial pass before calling it done). review-tests after STEP 8
          too, given STEPs 5-7 add a meaningful amount of new test logic (claim
          filtering, regex-based property assertions) that could itself contain bugs.
          qa explore mode does NOT apply -- this is a pure library-level Python interface
          (render()/explain() callables consumed by other code and tests), with no
          runtime UI or CLI surface a human would interactively exercise beyond what the
          unit tests in STEPs 5-7 already cover.
BUDGET    STEP 3 is the step most likely to eat the budget: five distinct depth-rendering
          behaviours in one function, including one non-trivial claim-filter (RATIONALE)
          and one content-derivation rule (SUMMARY's path-free paragraph), all while
          keeping every existing RenderTest assertion in test_answer.py passing
          unmodified.
OPEN      Whether render()'s "IMPACT behaves exactly like None" choice (STEP 3) is
          correct long-term, or whether IMPACT should someday get its own explicit
          branch -- flagged rather than silently assumed; it works today only because
          impact()'s Answer happens to leave every field STEP 3's "None" path would
          print empty except short_answer/things_to_be_aware_of/claims.
          What "documented alternatives if any exist" means for RATIONALE beyond
          "whatever TEAM_KNOWLEDGE claims exist" -- the current data model has no
          separate "alternatives" concept; a symbol with zero HISTORY/TEAM_KNOWLEDGE
          claims renders RATIONALE with only a Short answer, which is correct but
          degenerate, and not specifically tested here.
          knowledge_agent.py's run()/Outcome does NOT get STEP 4's IMPACT delegation --
          only explain() does. Calling `agent.run(text, depth="IMPACT")` directly (as
          opposed to `knowledge.explain(agent, symbol, "IMPACT")`) still runs the plain
          four-stage pipeline and reports only findings.callers, with no secondary-hop
          data. The issue's own Impacted Components list does not name knowledge_agent.py
          as needing this change, so it is left as a real, named gap rather than silently
          extended past what #571 asked for.
LEFT OUT  A live rql-backed CLI demo run (`python3 launchpad/project-intelligence/knowledge.py`)
          -- not exercised by this plan. Per #211's own precedent (its CLI needs a real
          RepoQL index and cannot run from an arbitrary cwd), the hermetic test suite is
          the verification surface, not the CLI.
          classify_depth() and investigation.py's RATIONALE-triggers-history gate --
          both explicitly out of scope per the issue itself, and this plan does not touch
          either.
