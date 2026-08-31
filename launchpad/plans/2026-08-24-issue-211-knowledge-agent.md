Issue #211 — task: build KnowledgeAgent orchestration and the knowledge.* programmatic interface
Stated size: no Size line on this repo's Task template (same gap as #206-#210)  →  cap: 12 steps
              (12, not #206-#210's 10, confirmed with Serina 2026-08-24: this is the integration
              task and carries seven interface methods, four decision stages, an answer format and
              two end-to-end worked examples)

ALREADY TRUE  (verified against git and the live repo, not notes)
  Branch task/211-knowledge-agent is cut from origin/launchpad at 132f921ac, which already
    contains all five of #206-#210's implementations -- `ls launchpad/project-intelligence/`
    shows symbol.py, indexer.py, graph.py, semantic_index.py, memory.py, investigator.py and a
    test_*.py beside each. Unlike #210, nothing here needs to stack on an unmerged branch.
  All five suites pass on this branch: `python3 -m unittest discover -p "test_*.py"` from
    launchpad/project-intelligence/ reports **Ran 114 tests ... OK** in 49s. Two investigator
    tests shell out to `cargo`, so hermit must be activated first (`. ./bin/activate-hermit`) --
    without it the same run reports FAILED (errors=2) with FileNotFoundError: 'cargo'.
  No orchestration exists: `grep -rn "KnowledgeAgent\|knowledge\.\(find\|explain\|impact\)"`
    across launchpad/project-intelligence/ returns exactly one hit, and it is a comment, not an
    implementation -- investigator.py:9. There is no knowledge.py, no answer-format renderer, no
    Claim type, and no __init__.py; the modules are flat and import each other by bare module
    name (`from graph import ProjectGraph`).
  That one hit is a requirement this task inherits. investigator.py:8-20 documents the four-stage
    calling convention "documented here rather than enforced by any code -- the caller that
    applies it is #211's KnowledgeAgent, which does not exist yet", and states that every tool in
    its TOOL_REGISTRY is READ_ONLY except run_command and run_test, which are EXECUTE and print
    that flag before the subprocess runs. So #208 already wrote down what #211 owes it, and
    TOOL_REGISTRY's own flags are the mechanism step 7's done-when can assert against.
  The five components' public surface is settled and callable as of this branch:
    indexer.build_index(crate) -> list[Symbol]; ProjectGraph.from_symbols(symbols),
    .edges_from(node, edge_types), graph.reachable(graph, start, edge_types, max_hops);
    SemanticIndex.from_symbols(symbols), .search(concept, top_k),
    semantic_index.find_it_for_me(index, graph, concept); ProjectMemory.add/get/query_by_class/
    record_code_contradiction/record_team_statement; investigator's twelve module-level tool
    functions (read_file, list_directory, inspect_logs, search_text, search_symbols,
    find_references, inspect_git_history, git_blame, inspect_dependency, query_build_system,
    run_command, run_test).
  memory.py already owns the provenance vocabulary this task must label answers with:
    MemoryEntry(entry_class ∈ FACT|INFERENCE|TEAM_KNOWLEDGE, statement, evidence, confidence,
    provided_by, temporal_state ∈ BASE|WORKING|HISTORY, superseded_by), and it already enforces
    the doc's constraints in __post_init__ -- confidence required for INFERENCE only, provided_by
    for TEAM_KNOWLEDGE only, evidence for FACT and INFERENCE. This task reuses that vocabulary
    rather than inventing a second one.
  The series' testing pattern is established and documented in test_indexer.py's own docstring:
    fast hermetic suites use constructed Symbol fixtures carrying values copied from the real
    repo; anything that shells out to `rql` or reads real files is verified live and evidenced in
    the PR body instead. semantic_index.py:336 shows the matching live-demo pattern -- an
    `if __name__ == "__main__":` block calling build_index("buzz-core") for real.
  Operational fact for the live demo: indexer.run_rql_query shells out to `rql`, so the demo
    needs a RepoQL index of *this worktree*. A fresh worktree has none -- the first `rql query`
    here returned "Host did not become healthy within 120000ms" while the initial index built.
    Budget for that build before running any live demo; the hermetic suite must not need it.
  Monday's rescope (buzz-infrastructure/project-management/2026-08-24-rescope.md) makes #4 the
    anchor PRD for M3 "Knowledge crate", which is a Rust crate surfaced in Buzz Settings.
    Confirmed with Serina 2026-08-24: **this issue finishes the Python prototype as its DoD is
    written**; the crate is separate M3 issues that do not exist yet. Do not start Rust here.

APPROACH NOTE (read before step 1)
  Orchestration here is **deterministic** -- rule-based question decomposition and templated
  prose, no model call. **Confirmed with Serina 2026-08-24, before step 1.** Three reasons, all
  checkable: every sibling module in this series has no LLM/API dependency; ADR-0012's
  inference-provider boundary was amended on 2026-08-20 for #74 specifically, and names no other
  consumer, so a model call from #211 sits outside the recorded credential boundary; and all six
  of #211's DoD items are structurally checkable without one.

  A builder must therefore not introduce an API client, a model client, or a network call. If one
  looks necessary to satisfy a step, that is a signal the step was misread -- stop and say so.

  Tests are written **per step**, as each step's own done-when, not gathered at the end.
  Step 12 proves the suite is hermetic and wires the CLI; it does not author the suite.

STEP 1  [independent] Add answer.py: the Claim and Answer data model. Claim carries
        (statement, entry_class, evidence, confidence, provided_by) and reuses memory.py's
        EntryClass literal rather than declaring a parallel vocabulary. Answer holds the six
        named sections from the design doc's § Data Model item 7 plus its claims. Validation
        mirrors MemoryEntry.__post_init__ field-for-field.
        done when: Claim(entry_class="INFERENCE") with confidence=None raises ValueError, and
        Claim(entry_class="FACT", evidence=()) raises ValueError -- both asserted directly, and
        both mirroring an error memory.py already raises for the same shape.

STEP 2  [needs 1] Render the answer format: a function producing exactly `## Short answer`,
        `## How it works`, `## Relevant flow`, `## Important files`, `## Things to be aware of`,
        `## Sources` in that order, omitting any section the question did not fill, and listing
        every claim under `## Sources` with its provenance label.
        done when: rendering an Answer holding one FACT and one INFERENCE emits both under
        `## Sources` with the literal labels FACT and INFERENCE, and an Answer with no flow
        content emits no `## Relevant flow` heading at all -- both asserted on the rendered
        string, not on the object.

STEP 3  [needs 1, 2] One real answer, end to end, single hardcoded question, no decision logic
        yet: build the index for buzz-core, resolve one real symbol through ProjectGraph, and
        print a rendered six-section answer from real data.                     ← RUNS HERE
        done when: running it prints all six section headings for a real buzz-core symbol and
        every `file:line` under `## Sources` resolves -- each one opened and confirmed to contain
        what the claim says it contains, not merely to exist.

STEP 4  [needs 3] Question decomposition: map a natural-language question to
        (intent, target, temporal_state, depth), where intent is one of the seven knowledge.*
        intents, temporal_state ∈ BASE|WORKING|HISTORY defaulting to WORKING, and depth is one of
        the design doc's six § Data Model item 6 levels.
        done when: seven questions, one per intent, each classify to their own intent with no
        two colliding; and "how did X change over time" classifies HISTORY while "how does X
        work" classifies WORKING.

STEP 5  [needs 4] Decision logic stage 1 -- check confidence first: query ProjectGraph,
        SemanticIndex and ProjectMemory for what is already known about the target, returning an
        assessment that names which components answered and which were empty.
        done when: a target with both a real graph node and a real ProjectMemory FACT reports
        confident and names both sources; a target absent from all three reports no confidence
        and names all three as empty -- never reports confidence from an empty component.

STEP 6  [needs 5] Decision logic stage 2 -- verify important claims even when confident: a claim
        that will be asserted as settled fact gets at least one live Investigator confirmation
        before assertion, and a claim whose confirmation comes back empty is downgraded rather
        than asserted.
        done when: a FACT claim that a cached ProjectMemory entry already agrees with is shown
        making a real investigator call before assertion (the call appears in the recorded
        trace), and a claim whose confirmation returns empty is emitted as INFERENCE or dropped
        -- asserted by checking the emitted claim's entry_class, never FACT.

STEP 7  [needs 5] Decision logic stage 3 -- investigate when not confident: run the design doc's
        progression (search_symbols → read_file → find_references → tests → git history),
        stopping as soon as the evidence is sufficient, recording an ordered trace of every tool
        call made.
        done when: a question about a real buzz-core symbol against an empty ProjectMemory
        produces a trace whose recorded calls appear in that order, and neither run_command nor
        run_test appears in it -- a read-only question must not reach a side-effecting tool.

STEP 8  [needs 6, 7] Decision logic stage 4 -- assemble the explanation from the gathered
        evidence only, after stages 1-3, with every claim carrying its provenance class and every
        INFERENCE carrying both its evidence and its confidence.
        done when: the assembled answer for step 7's question contains at least one INFERENCE
        whose evidence names the real artefact the inference was drawn from, and iterating every
        claim in the answer finds none without a provenance class.

STEP 9  [needs 8] Add knowledge.py: find, explain, dependencies, impact, setup, conventions,
        history as seven callable functions over the agent, each returning a provenance-labeled
        result. find routes to semantic_index.find_it_for_me; dependencies and impact route to
        graph.reachable; conventions routes to ProjectMemory.query_by_class; history routes to
        investigator.inspect_git_history; setup reads the real manifests the design doc's
        § Development-environment operational answers names.
        done when: all seven are called once each and every claim in every returned result
        carries a provenance class -- checked by iterating the returned claims programmatically,
        not by reading the printed output.

STEP 10 [needs 9] DoD item 6 -- reproduce the UserRepository-shaped investigation trace end to
        end against a real symbol in this repo: search → read → find_references → tests → git
        history → labeled answer, following the design doc's § Decision logic worked example
        shape against real buzz code rather than its fictional TypeScript subject.
        done when: the trace prints all five investigation stages against one real symbol and
        ends in an answer separating at least one FACT from at least one INFERENCE, with every
        cited file:line opened and confirmed to contain what is claimed.

STEP 11 [needs 9] DoD item 3 -- the JWT/Auth0-shaped worked example against this codebase's own
        equivalent flow (buzz-core's kind gating is the nearest real analogue already proven by
        #207's and #210's own demos; pick the strongest real candidate at build time rather than
        forcing that one).
        done when: the produced answer carries the same six-section shape as the design doc's
        example; its `## Relevant flow` is a real graph.reachable() path with its hop count, not
        prose; and its `## Things to be aware of` carries an INFERENCE whose evidence is stated.

STEP 12 [needs 10, 11] Prove the suite is hermetic and wire the live CLI: the new tests must run
        with no `rql` and no network, matching test_indexer.py's stated boundary, while the live
        worked examples run from an `if __name__ == "__main__":` block as in semantic_index.py.
        done when: `python3 -m unittest discover -p "test_*.py"` passes from
        launchpad/project-intelligence/ with the new tests included and with `rql` made
        unavailable on PATH; and separately, with hermit active and the index built,
        `python3 knowledge.py` prints both worked examples from real data. Both runs pasted into
        the PR body -- the count must exceed 114.

PARALLEL  Step 1 is independent. Steps 6 and 7 are both `[needs 5]` and are the one genuine
          fan-out opportunity: stage 2 (verification) and stage 3 (investigation) are separate
          decision stages, and if each lands in its own module they touch no shared file. If both
          are written into one knowledge_agent.py they are sequential regardless -- the file is
          the constraint, not the logic. Steps 10 and 11 are both `[needs 9]` and genuinely
          independent (two different worked examples, two different output paths) provided each
          gets its own test file. Everything else is sequential: steps 2-5, 8, 9 and 12 each
          extend a file an earlier step created.

GATES     serina:review-code and serina:review-tests after step 12, the integration point.
          serina:review-adjudicate then serina:review-final before the PR, per this repo's
          gate order. **qa explore mode applies** -- knowledge.py ships seven callable methods
          and a CLI, so there is a real runtime surface to attack: a symbol that does not exist,
          an empty ProjectMemory, a target with no graph edges, a question matching no intent, a
          HISTORY question about a file with one commit, and `rql` absent mid-run.
          Reviewers run before the push, not after it.

BUDGET    Step 7 (the investigation loop) is most likely to overrun. "Stopping as soon as the
          evidence is sufficient" is the one piece of real judgement in this task, it is the
          stage the design doc specifies least precisely, and it has to produce a *deterministic*
          stop condition to be testable at all. Step 11 is the runner-up for a different reason:
          finding a real flow in buzz-core with enough depth to fill all six sections honestly
          may take several candidate symbols before one holds up.

OPEN      ~~**Does the KnowledgeAgent call a model?**~~ **Decided 2026-08-24 by Serina: no.**
          Deterministic templated prose -- see APPROACH NOTE. Kept here rather than deleted
          because the design doc's "the only component allowed to produce prose" still reads as
          an LLM to anyone arriving at that sentence cold, and the reason it isn't one is the
          ADR-0012 boundary, not the doc. If a later consumer wants real synthesis, that is an
          ADR-0012 amendment naming it, before code.
          **What "significant enough to re-verify" means** in decision-logic stage 2. The doc
          says "it will drive a code change, or will be stated to the user as settled fact",
          which is not mechanically decidable. Default: every FACT claim is verified, since the
          cost is one Investigator call and the failure mode of guessing wrong is asserting an
          unverified fact -- exactly what this layer exists to prevent.
          **Where the knowledge.* interface is called from.** #211 says "callable methods" and
          nothing about a transport. Default: Python functions plus the CLI, no server, no MCP.
          **Whether ProjectMemory persists between runs.** It does not: grepping memory.py for
          save, load, json, open( and Path returns nothing, so the store is in-memory only.
          conventions() and the stage-1 confidence check therefore start empty on every run, and
          TEAM_KNOWLEDGE cannot survive a process exit -- which is most of the point of the class.
          Not this issue's to fix, but it caps what stage 1 can ever report, and it is worth its
          own issue against #209.

LEFT OUT  Anything Rust, and anything touching Buzz Settings -- confirmed out of scope for #211
          on 2026-08-24; those are M3's unfiled crate issues.
          Incremental/symbol-scoped index maintenance on file change -- named as out of scope in
          #211's own body, which also asks whether it should be its own issue. It should; file it
          rather than absorbing it here.
          Any change to #206-#210's own logic -- #211 only calls into them. A defect found in one
          of them becomes its own issue, per this repo's non-blocker rule.
          Wiring these suites into CI. The Python suites run in no CI job at all, which the
          rescope names as M5's biggest single blind spot and tracks as #270. Fixing it for one
          directory here would fix it in the wrong place.
          Packaging the directory as an importable module (__init__.py, a console entry point).
          The whole series imports by bare module name from inside the directory; changing that
          convention in the integration task would touch all five existing modules.
