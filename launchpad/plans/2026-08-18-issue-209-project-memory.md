Issue #209 — task: build ProjectMemory with FACT/INFERENCE/TEAM_KNOWLEDGE provenance
Stated size: no Size line on this repo's Task template (same gap as #206/#207/#208)  →  cap: 8 steps

ALREADY TRUE  (verified against git and the live repo, not notes)
  launchpad/project-intelligence/ exists on disk from earlier branch work (#206/#207/#208, PRs
    #213/#214/#217, none merged into `launchpad` yet) but this branch (task/209-project-memory,
    cut fresh off launchpad at d4d08b76f, which already includes merged #192/#195) has no
    tracked files there -- only a stray __pycache__/, confirmed via `git status`/`ls`.
  No MemoryEntry, ProjectMemory, or reconciliation code exists anywhere in the repo --
    `grep -rn "class MemoryEntry\|class ProjectMemory"` returns nothing.
  #209 has no stated dependency on #206/#207/#208 in its own issue body -- its Impacted
    components field names no fixed location, only "likely alongside #206/#207" as a hint,
    not a blocking prerequisite, confirmed before planning (same check made for #208).
  The design doc (launchpad/Research/project-intelligence-layer-design.md § Data Model item 4,
    lines 183-225) gives the exact MemoryEntry field list, the three-class semantics, the
    reconciliation rule, and the legacyExport worked example this task must reproduce.

STEP 1  [independent] Define MemoryEntry (id, class, statement, evidence[], confidence,
        provided_by, temporal_state, superseded_by) with field-combination validation matching
        the design doc exactly: confidence required for INFERENCE only, provided_by required for
        TEAM_KNOWLEDGE only, evidence required for FACT and INFERENCE.
        done when: constructing each invalid combination (confidence on a FACT, missing evidence
        on an INFERENCE, missing provided_by on a TEAM_KNOWLEDGE) raises, and one valid entry per
        class constructs successfully -- a unit test proves each of the six cases.

STEP 2  [needs 1] Implement ProjectMemory: add(entry), get(id), query_by_class(cls) -- the class
        stored as a real structural field, not a free-text note.
        done when: query_by_class("TEAM_KNOWLEDGE") against a store holding one entry of each
        class returns exactly the TEAM_KNOWLEDGE entry, distinct from what query_by_class("FACT")
        and query_by_class("INFERENCE") return.

STEP 3  [needs 2] Implement record_code_contradiction(): the reconciliation rule for FACT/
        INFERENCE. When live evidence contradicts a stored entry, create a NEW entry from the new
        evidence and set the OLD entry's superseded_by to the new entry's id -- never delete or
        silently overwrite the old statement. ← RUNS HERE
        done when: calling it against a FACT entry returns a new entry, the old entry's
        superseded_by now points to it, and get(old_id) still returns the ORIGINAL statement
        unchanged (proving nothing was silently overwritten).

STEP 4  [needs 3] Implement the TEAM_KNOWLEDGE exception inside record_code_contradiction(): a
        code-only contradiction attempt against a TEAM_KNOWLEDGE entry is a no-op.
        done when: the same call that supersedes a FACT entry in STEP 3 leaves a TEAM_KNOWLEDGE
        entry's superseded_by at None when called against it -- one test exercises both, so the
        exception is shown to be about the class, not about the function doing nothing for
        everyone.

STEP 5  [needs 2] Implement record_team_statement(): the one thing that CAN supersede a
        TEAM_KNOWLEDGE entry -- an explicit new statement from a person, distinct from a code
        observation.
        done when: calling it against a TEAM_KNOWLEDGE entry sets that entry's superseded_by to a
        new TEAM_KNOWLEDGE entry carrying the new statement and provided_by.

STEP 6  [needs 4, 5] Reproduce the design doc's own worked example end to end: the
        `OrderRepository.legacyExport` TEAM_KNOWLEDGE entry, verbatim.
        done when: the entry is added, surfaces via query_by_class("TEAM_KNOWLEDGE") with no
        corroborating code anywhere, survives a record_code_contradiction() attempt against it
        unchanged (STEP 4's exception exercised on the doc's own example, not a synthetic one),
        and IS correctly superseded once record_team_statement() supplies an explicit new
        statement (e.g. "migration #482 complete, legacyExport removed").

STEP 7  [independent] Validate temporal_state as one of BASE | WORKING | HISTORY on construction.
        Storing/passing the value through is this task's job; resolving which state a given
        question implies is design-doc item 5's job for #211 (KnowledgeAgent), not this store.
        done when: constructing a MemoryEntry with an invalid temporal_state raises, and all
        three valid values construct successfully.

STEP 8  [needs 3, 4, 5, 6, 7] Wire a CLI/demo reproducing the legacyExport trace end to end plus
        one FACT reconciliation example, printed in the same worked-example style #206/#207/#208
        used.
        done when: running it prints the legacyExport TEAM_KNOWLEDGE entry surviving a code
        contradiction attempt, then being superseded by an explicit statement, and a separate
        FACT entry being correctly superseded by new code evidence -- all real calls, not stubs.

PARALLEL  Step 1 and step 7 touch no file another pending step needs first and could run as
          parallel subagents. Steps 2 through 6 all extend the same growing memory.py module and
          its store, so -- same note as #206/#207/#208 -- they are sequential in practice unless
          split into separate files up front.

GATES     Same as #206/#207/#208: serina:review-code and serina:review-tests as scoped
          re-reviews after step 8, the only integration point. No SDD ledger applies (issue-
          driven, `--issue` flag) -- expected, not a defect.

BUDGET    Step 3 (record_code_contradiction) is most likely to eat the budget -- it is the first
          place the "flag stale, never silently overwrite or silently keep" rule has to be
          expressed as actual code rather than restated as prose, and getting the
          create-new-entry-plus-supersede shape right (not a field-mutation shortcut that would
          silently overwrite) is the same kind of work #206's with_called_by() and #207's
          reachable() needed.

OPEN      The design doc's MemoryEntry schema names `confidence` for INFERENCE with no stated
          type or range -- this plan's own judgment call is a float in [0.0, 1.0], not read from
          the issue or the doc; a maintainer may want a different scale.
          Id generation strategy (uuid4 hex vs sequential vs caller-supplied) is not specified by
          the issue or the doc -- this plan's own call is uuid4 hex, generated by the store on
          add() unless the caller supplies one.
          Whether record_team_statement() should be allowed to supersede FACT/INFERENCE entries
          too, not just TEAM_KNOWLEDGE -- the doc only states TEAM_KNOWLEDGE's exception
          explicitly; this plan allows it universally since an explicit human statement is at
          least as strong evidence as a code observation, but that is a judgment call for a human
          to confirm, not something to treat as settled by building it.

LEFT OUT  Persistence to disk or a database -- the issue's Definition of done describes store
          behavior (structural field, reconciliation, exception), not a storage backend; this
          task builds an in-process store, matching #207's ProjectGraph precedent.
          Auto-populating memory from #206/#207's ProjectIndexer/ProjectGraph output --
          explicitly out of scope per #209's own issue text.
          Any UI for browsing or editing memory entries -- also explicitly out of scope per #209.
          Full temporal_state resolution logic (deciding WORKING vs BASE vs HISTORY for a given
          question) -- design doc item 5 assigns that to #211 (KnowledgeAgent); STEP 7 here only
          validates the field's own three allowed values.
