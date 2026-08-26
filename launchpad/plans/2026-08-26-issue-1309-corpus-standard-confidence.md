Issue #1309 — task: document corpus standard for confidence
Stated size: no `Size` line  →  cap: 5 steps (set by the feature #605 task brief, not asked per-issue)

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-1309-corpus-standard-confidence` is on branch
    `task/1309-corpus-standard-confidence`, based on `origin/task/636-corpus-agents-md`,
    HEAD `60d4947b7145a6ef25f185b9c25d43e43d99de3c`, working tree clean.
  `launchpad/docs/corpus/AGENTS.md` exists on this base (the instruction node, #636, unmerged as PR #1462).
  `launchpad/docs/corpus/standards/` does NOT exist — no sibling standard has landed.
  The only authored corpus node today is `AGENTS.md`; everything else under
    `launchpad/docs/corpus/` is `schema/`, which `validate.py` deliberately skips.
  `node.schema.json` already encodes the confidence rule in three `allOf` branches:
    INFERENCE requires `evidence` + `confidence`; FACT forbids `confidence` and `provided_by`;
    TEAM_KNOWLEDGE requires `provided_by` and forbids `confidence`.
  `launchpad/project-intelligence/memory.py` `__post_init__` enforces the same rule at runtime,
    plus two checks the schema does not have (bool rejection, NaN rejection).
  `validate.py` imports `jsonschema` and `yaml` only — it never imports `memory.py`.
    The corpus path is enforced by the schema, not by `memory.py`.
  Measured by running `Draft202012Validator` over synthesised nodes (recorded in STEP 1):
    `0.0` and `1.0` both pass (bounds inclusive); integer `1` passes; `1.1` and `-0.1` fail;
    `true` and `"0.8"` fail on type; **`.nan` PASSES the schema** but `memory.py` rejects it.
  ADR-0029 is accepted and states inference is "never treated as fact on their own".
  No open or closed issue on `launchpad-26/buzz` matches "confidence NaN schema".

STEP 1  [independent]  Record the measured constraint set as a reproducible probe script
        under the session scratchpad, covering: the three `allOf` branches, both inclusive
        bounds, integer acceptance, bool/string rejection, and the NaN divergence between
        `node.schema.json` and `memory.py`. This is evidence-gathering, not a
        deliverable — nothing under `launchpad/` changes in this step.
        done when: the probe script runs and prints one PASS/FAIL line per case, and its
        output shows `INFERENCE conf nan -> PASS` against the schema while
        `memory.py` raises `confidence must be within [0.0, 1.0]` for the same value.

STEP 2  [needs 1]  Create `launchpad/docs/corpus/standards/confidence.md` with schema-valid
        front matter only (`id: corpus-standard-confidence`, `type: governance`,
        `status: active`, `origin: launchpad`, `audiences`, an `evidence` ledger whose
        first entry is the `commit 60d4947b…` provenance citation, and **no**
        `relationships` key).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with
        the new file present, and a YAML parse of the front matter (not a grep — a grep
        confuses "prints 0" with "exits 1") reports `relationships` absent from the
        top-level keys and `id == corpus-standard-confidence`.

STEP 3  [needs 2]  ← RUNS HERE  Write the body: scope and authority, what the number
        means, MUST vs SHOULD split, how an author picks one, what a reader may and may
        not conclude, the reasoning-from-evidence versus dressing-up-a-decision
        distinction, enforcement and its gaps, and the exception/escalation route to
        `status: flagged` per ADR-0029. Link the schema and ADR-0029 rather than
        restating enum lists or the field-combination matrix.
        done when: `validate.py` exits 0; every `##` section named in this step is present
        in the file; and the body links `launchpad/docs/corpus/schema/node.schema.json`
        and `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` at least once each.
        NOTE: "does not restate the field-combination matrix" is deliberately NOT a
        done-when here. A one-line grep cannot detect a matrix restated as a table or a
        bulleted list — review-plan proved that by constructing one that slipped through.
        It is a reading judgement, so it belongs to STEP 4's audit, not to a regex.

STEP 4  [needs 3]  Audit the finished node against its own ledger: every `##`-level
        substantive claim has an `evidence` entry, every `FACT` cites a source that was
        actually opened, exactly one commit-only FACT exists, every INFERENCE carries a
        confidence the document's own rules would justify, and the body nowhere restates
        the schema's field-combination matrix or an enum member list (the judgement STEP 3
        deliberately did not delegate to a regex).
        done when: `validate.py` exits 0; a YAML parse of the ledger — not a grep, so
        indentation and quote style cannot skew the count — reports exactly one entry
        whose every citation matches `^commit [0-9a-f]{40}$`; every INFERENCE entry has a
        `confidence` key; and a written audit note maps each ledger entry to the body claim
        it supports, naming any entry that supports none.

STEP 5  [needs 4]  Run the full corpus test suite and the validator as the last command of
        their own invocations (verify-gate stamp), file the NaN-divergence finding as a
        GitHub issue on `launchpad-26/buzz` linked to parent #605, then commit with `-s`
        via an `-F` message file.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK; `validate.py` exits 0; `gh issue view <the new number> --repo launchpad-26/buzz`
        resolves and its body references #605; and `git log --format=%B -1` shows a
        `Signed-off-by:` trailer.

PARALLEL  None. Steps 2, 3 and 4 all edit the same single file
          (`launchpad/docs/corpus/standards/confidence.md`), so they are strictly
          sequential regardless of how separable the content looks. STEP 1 touches no
          repository file but produces the measurements STEP 2's ledger cites, so it
          still precedes them. No step may be dispatched as a parallel subagent.

GATES     `review-plan` on this plan before STEP 1 (self-review, not independent).
          `review-code` after STEP 5. `review-tests` does NOT apply — the diff adds no
          test file and changes none; if that stops being true, it applies.
          `review-adjudicate` over every finding both raise. A mandatory Codex
          cross-model final pass after adjudication.
          `qa` explore mode does **not** apply: the deliverable is a Markdown document
          with no runtime interface to exercise. The only executable surface touched is
          `validate.py`, which this change calls but does not modify.

BUDGET    STEP 3. The hard part is not length, it is saying what a confidence number
          licenses a reader to conclude without either overclaiming calibration the
          repository cannot support or hedging into uselessness. Expect the
          reasoning-versus-decision distinction to need more than one pass.

OPEN      Whether `developer` belongs in `audiences`. #636 carries `agent` and
          `reviewer`, and the brief calls the question deliberately unsettled. Planned
          choice: `agent`, `reviewer` — an author picking a number is acting as agent,
          a person checking it is acting as reviewer, and a developer reading corpus
          prose is not addressed by this document in any way the other two do not
          already cover. Stated so a reviewer can overturn it cheaply.
          Whether the NaN divergence is a schema defect or an accepted limit of
          structural validation. Planned handling: report it, do not fix it here —
          `schema/` is out of this issue's scope and its DoD forbids a second authored
          node. It becomes a filed issue, not a silent edit.

LEFT OUT  Any `relationships` edge. Every sibling standard (#1307–#1351) is unmerged,
          and a `relationships[].target` naming an id no loaded node carries is a hard
          validation error. The absence is stated in the body with its reason, as
          `AGENTS.md` does for itself.
          Editing `launchpad/docs/corpus/AGENTS.md`, even where this work suggests it
          could be clearer — the brief forbids it and the DoD scopes this task to one
          authored document.
          Restating the enum members or the field-combination matrix in body prose.
          `validate.py` never reads body prose, so a second copy would stay green
          forever after it went stale.
          Fixing `#1459` (line numbers unverified) or the NaN gap. Both are pre-existing
          and owned elsewhere.
