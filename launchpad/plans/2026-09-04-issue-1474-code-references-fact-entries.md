Issue #1474 — bug: two FACT entries in the code-references node misdescribe measured validator behaviour
Stated size: none  ->  cap: 5 steps (no `Size` line in the issue; proceeding without asking per
auto-mode, since the investigation below already narrows the fix to a single line and stopping to
ask would burn a round-trip on a decision the evidence already answers — flagged in OPEN below for
visibility).

ALREADY TRUE  (verified against git and the live file, not the issue's quoted text)
  - Working tree is clean on branch fix/issue-1474-code-references-fact-entries, tracking
    origin/launchpad at aef93f2c2a.
  - `python3 -c "...v._classify_citation('https://github.com/launchpad-26/buzz/issues/1459', root)"`
    prints `CitationVerdict(status='unverified', detail='is an external URL this validator can
    neither pin nor open')` — confirms a github.com URL that isn't a blob/raw link is `unverified`.
  - `_classify_repo_path` (launchpad/project-intelligence/corpus/validate.py:653-698) ends at
    `candidate.is_file()` — a stat — and reads no file contents anywhere in that path.
  - Commit 9a9ebfc22a ("docs(corpus): reconcile three ledger self-contradictions (#1308)",
    2026-08-27) ALREADY rewrote evidence entry 3 (line 19) to "...resolved on disk and must name a
    real file... Resolution establishes only that the file is there; the file's contents are never
    read." and evidence entry 9 (line 43) to "...external URLs that are not pinned repository links
    -- including GitHub issue and pull-request URLs -- are routed to a non-fatal UNVERIFIED
    channel...". Both now match measured behaviour and no longer contradict entry 12
    ("...is never opened..."). **Issue #1474's quoted text for entries 3 and 9 is stale — those two
    ledger entries need no further change.**
  - Section 2's table row 1 (line 139) was NOT touched by that commit and still reads: "The path was
    resolved and opened." — this is the one surviving defect from the issue, and it contradicts
    entry 3 and entry 12.
  - PR #2087 (open, unmerged, branch fix/issue-1479-code-references-column-explanation) touches the
    same file's Enforcement section for a different issue (#1479). Diff must stay scoped to line 139
    to minimise merge friction.
  - Grep of the rest of the corpus found two more instances of the same misdescription pattern,
    outside this file's scope: `launchpad/docs/corpus/AGENTS.md:64,221` (stale "non-GitHub" framing
    — code-references.md's own scope note says it may not edit AGENTS.md) and
    `launchpad/docs/corpus/standards/diagrams.md:47` ("is opened on disk", the same wording entry 3
    used to have). Both are out of scope for this issue; report only.

STEP 1  Edit line 139 of launchpad/docs/corpus/standards/code-references.md: change              [independent]
        "The path was resolved and opened." to "The path was resolved and confirmed to be a file."
        (matches the issue's own suggested wording, and now agrees with entry 3 and entry 12).
        No other line in the file changes.
        done when: `git diff` for the file shows exactly one changed line, at line 139, and no
        change touches the Enforcement section PR #2087 owns.

STEP 2  Run the corpus validator and confirm it still exits 0 with the same unverified count as       [needs 1]  ← RUNS HERE
        before the edit (this is a body-prose change; the validator does not read body prose, so the
        count must be unchanged).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, and its
        reported unverified count matches a pre-edit run (diff the two outputs).

STEP 3  Commit with `git commit -s` (DCO required); do not amend, do not force-push, do not skip      [needs 2]
        hooks.
        done when: `git log -1 --format=%B` shows a `Signed-off-by:` trailer and the commit touches
        only code-references.md.

STEP 4  Push the branch and open the PR as a standalone `gh pr create` call (no `cd` prefix — the     [needs 3]
        repo's pr-gate hook rejects `cd <dir> && gh pr create` as one call), based on `launchpad`,
        body includes "Closes #1474" and a note that PR #2087 touches the same file's Enforcement
        section so merge order is worth checking. Check 2-3 recent `is:merged label:by:agent` PRs to
        decide whether to add a `by:agent` label, matching convention.
        done when: `gh pr view <num> --repo launchpad-26/buzz --json url,body` shows the PR open
        against `launchpad`, body contains "Closes #1474", and its label set matches the sampled
        convention.

STEP 5  Report to Serina: what was confirmed, what was already fixed and needed no change, the        [needs 4]
        out-of-scope AGENTS.md/diagrams.md findings, the PR URL, and the exact
        `gh pr edit <num> --repo launchpad-26/buzz --add-reviewer <username>` command for her to run
        herself (she authors this session and cannot self-approve). Do not close #1474 — it closes
        on merge.
        done when: the report names all of the above explicitly; issue #1474 remains open.

PARALLEL  None of these can run as parallel subagents — each step's file/branch state depends on the
          prior step completing (edit → validate → commit → push/PR → report is a strict chain on
          one file and one branch).
GATES     `serina:build-change` runs this plan and hands off to its own review gate at the end
          (per the task's process). `review-code` / `review-tests` do not apply — no source code or
          tests are touched, only a documentation line. `qa` explore mode does not apply — there is
          no runtime interface to exercise; the only executable surface is the validator, and its
          exit code plus unverified count is the check in STEP 2.
BUDGET    STEP 4 (PR creation) is the step most likely to eat time — it depends on an external `gh`
          call, a label-convention lookup, and the pr-gate hook's exact invocation shape.
OPEN      No `Size` line on the issue — proceeded without asking because the evidence above already
          caps this at a one-line fix; flagged here rather than silently assumed. Whether entries 3
          and 9's *current* wording is the best possible phrasing (vs. merely "no longer
          contradictory") is not re-litigated — they satisfy the issue's underlying concern already
          and further wordsmithing risks unrelated churn against PR #2087's in-flight diff.
LEFT OUT  Editing AGENTS.md's stale "non-GitHub" rows (out of scope — code-references.md's own text
          says it may not edit AGENTS.md; report as a follow-up candidate instead). Editing
          diagrams.md's "is opened on disk" line (a different corpus node/standard; out of scope for
          this issue, report as a follow-up candidate instead). Re-wording entries 3 and 9 to match
          the issue's suggested phrasing verbatim, since they are no longer defective.
