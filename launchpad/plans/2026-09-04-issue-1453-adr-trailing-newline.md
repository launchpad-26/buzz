Issue #1453 — bug: generated ADR files have no trailing newline
Stated size: no Size line in the issue body  ->  cap: 5 steps (smallest tier;
scope is one guard script + CI wiring, well under the 30-minute band)

ALREADY TRUE  (verified against git, not notes)
  All 29 pre-existing ADRs on `launchpad` end with a trailing newline
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/decisions/`, spot-
  checked with `git show <rev>:<path> | tail -c 1`).
  `launchpad/scripts/adr_boundary_check.py` exists and is a *validator* for
  ADR-0005's sanctioned-file list — unrelated in purpose, but its docstring/
  usage/exit-code shape is the pattern this fix should match.
  `launchpad/scripts/test_adr_boundary_check.py` is its companion unittest,
  discovered by `python3 -m unittest discover -s launchpad/scripts` — the same
  command `.github/workflows/launchpad-adr-check.yml` already runs in its
  "Run the checker's controls" step.
  `.github/workflows/launchpad-adr-check.yml` already runs unconditionally on
  every `pull_request` (its own header comment: "DELIBERATELY UNFILTERED BY
  PATH") — no `paths:` filter to fight, and it already fails closed on a
  missing checker file.
  No script or template that writes ADR file *content* exists anywhere in this
  repo, `.claude/skills/`, `launchpad/agents/the-professor/`, or the imported
  `serina-skills` marketplace (`documentation-and-adrs`, `plan-issue`,
  `build-change`, `corpus-author`, `corpus-batch-author` all checked) — see
  root-cause note below.

ROOT CAUSE (already investigated via agentic-debugging + root-cause-analysis;
not re-investigated here)
  All 14 new ADR files (#1433-#1446) were authored directly by a Claude Code
  agent session's file-write tool, one PR at a time, under one human's account,
  following the prose convention in `launchpad/decisions/README.md` — not by
  any committed script or template. PR #1433's own Agent-provenance table
  states "Harness / provider: Claude Code, Model: claude-opus-5". Byte-level
  check on PR #1433's first commit (334feaaf4b) confirms the file was written
  without a trailing `\n` at that point. There is no code-level "generator"
  artifact in this repository to patch — this plan does not include a step to
  "fix the generator" for that reason, and says so here rather than dropping
  that half of the issue's Objective silently. The actionable, locatable half
  of the Objective — a check that catches recurrence — does not depend on
  finding that artifact, and is what this plan builds.

STEP 1  Write the trailing-newline checker script            [independent]
        `launchpad/scripts/adr_trailing_newline_check.py`: walks
        `launchpad/decisions/*.md`, fails any file that is non-empty and does
        not end in exactly one `\n` (0 or 2+ trailing newlines both fail; an
        empty file is skipped). Follows `adr_boundary_check.py`'s shape: a
        module docstring stating what/why, a `main()` returning an exit
        code, `Usage: python3 adr_trailing_newline_check.py [repo-root]`,
        one `FAIL: <path>` line per offender, a final `failed: N`, exit 0
        when N=0.
        done when: `python3 launchpad/scripts/adr_trailing_newline_check.py .`
        run from the worktree root exits 0 and prints `failed: 0` against the
        current tree (which already satisfies the invariant, per ALREADY TRUE
        above).

STEP 2  Write the companion unit tests                       [needs 1]
        `launchpad/scripts/test_adr_trailing_newline_check.py`: a
        `unittest` suite using a `tempfile` decisions directory (never the
        real one), covering: a well-formed file (passes), no trailing
        newline (fails, path reported), two trailing newlines (fails), an
        empty `.md` file (skipped), a non-`.md` file (ignored).
        done when: `python3 -m unittest discover -s launchpad/scripts`
        passes with 0 failures, and the no-trailing-newline case was
        manually confirmed to fail without the fix (temporarily revert the
        check's core condition, re-run, observe the failure, then restore
        before committing).

STEP 3  Wire the check into CI                          [needs 1, 2]  ← RUNS HERE
        In `.github/workflows/launchpad-adr-check.yml`: add a step after
        "Check the ADR boundary" running `python3
        launchpad/scripts/adr_trailing_newline_check.py .`, and add the new
        script's path to the "Confirm the checker and the documents exist"
        step's file list so a missing checker fails closed like the
        existing one does.
        done when: the workflow YAML parses (`python3 -c "import yaml;
        yaml.safe_load(open('.github/workflows/launchpad-adr-check.yml'))"`
        raises nothing), and running both scripts locally exactly as the
        new steps invoke them (`python3 -m unittest discover -s
        launchpad/scripts` then `python3
        launchpad/scripts/adr_trailing_newline_check.py .`) exits 0.

STEP 4  Regression proof                                     [needs 1]
        Create a throwaway file under `launchpad/decisions/` with no
        trailing newline (`printf 'x' >
        launchpad/decisions/ADR-9999-scratch-regression-check.md`), run the
        checker against it, confirm it fails and names the file, then
        delete the scratch file before anything is committed.
        done when: the checker's exit code is non-zero and its output names
        `ADR-9999-scratch-regression-check.md`; `git status` shows the
        scratch file gone before the commit in STEP 5.

STEP 5  Commit, push, open the PR                       [needs 1, 2, 3, 4]
        `git commit -s`, push the branch, open the PR against `launchpad`
        with `Closes #1453` in the body, per `launchpad/AGENTS.md` "Opening
        a PR" (`gh pr create -F <body-file> --base launchpad --label
        by:agent`) and the Agent PR template.
        done when: `gh pr view <n> --repo launchpad-26/buzz --json url,state`
        returns the PR, and its body (`-q .body`) contains `Closes #1453`.

PARALLEL  Step 1 has no dependency and could start immediately. Step 2 needs
          1 (imports the module under test). Step 3 needs both 1 and 2 (the
          workflow step assumes both scripts already pass locally). Step 4
          only needs 1. In practice these are small enough and file-disjoint
          enough (1/2 touch new files, 3 touches the workflow YAML, 4 touches
          nothing persistent) that steps 1, 2, and 4's checker-only part could
          run as parallel subagents; step 3 should wait for 1 and 2 to land
          since it references both scripts by name in the workflow file.

GATES     `review-code` after step 3 (the new script + workflow change is the
          entire diff). `review-tests` after step 2 (the new unittest file).
          `qa` explore mode does not apply — this is a CI script with no
          runtime/UI surface to exercise interactively; local execution in
          steps 1, 2, and 4 already covers its only interface (CLI exit code
          + stdout). `review-final` runs at branch level per the repo's
          standard build-change handoff.

BUDGET    Step 1 (the checker script) is the step most likely to eat the
          budget — getting the "exactly one trailing newline, 0 or 2+ both
          fail, empty file skipped" edge cases right the first time is the
          fiddly part; steps 2-5 are comparatively mechanical once it exists.

OPEN      Whether a Claude Code session or skill-level guard (outside this
          repo, e.g. a serina-skills change to plan-issue/build-change or to
          documentation-and-adrs) should also be taught to end markdown files
          with a trailing newline. That is a cross-repo, process-level change
          affecting every future document this workflow writes, not a
          launchpad/buzz code fix, and is left for a human to decide whether
          to raise separately.

LEFT OUT  Retroactively rewriting any of the 14 already-merged ADR files
          (#1433-#1446) to add their trailing newline — explicitly out of
          scope per the task brief: that history belongs to other people's
          merged PRs. A generic "every markdown file in the repo must end in
          a newline" policy — the issue is scoped to ADRs specifically, and a
          repo-wide policy is a larger, separate decision. Enforcing "no
          trailing whitespace" or other markdown-lint concerns beyond the
          newline the issue names.
