Issue #1771 — bug: an agent PR with no by:agent label and no provenance table is checked as a human PR
Stated size: no `Size` line in the issue → assumed ≤30 minutes (a scoped bug fix with a suggested shape already given) → cap: 5 steps. Flagged in OPEN below rather than blocking.

ALREADY TRUE  (verified against git and code, not notes)
  `launchpad/scripts/pr_body_check.py` `looks_agent_authored()` only inspects PROVENANCE_FIELDS
    table rows and a non-N/A `### Authority` section (lines 346-366 on `origin/launchpad`).
  `check()`'s signature has no `author` parameter at all — confirmed by
    `inspect.signature(m.check)` against current code, not just the issue's stale repro.
  `is_agent = labelled_agent or body_says_agent` (check(), line ~508) — two signals only.
  `main()`'s final `kind = "agent" if "by:agent" in labels else "human"` (line ~595) uses the
    label alone, independently of `is_agent` — a second, narrower instance of the same gap.
  `.github/workflows/launchpad-pr-check.yml`'s "Validate PR body" step (lines 113-121) passes
    BODY, LABELS, CLOSING_REFS, FEATURE_CHILDREN, PR_ADDITIONS, PR_CHANGED_FILES — no author
    login is piped in today.
  Reproduced live: `m.check(body_with_no_markers, [], [148])` returns `errors == []` even
    though the body is agent-shaped content with no self-declaration — confirms the gap
    exists in current code, independent of PR #1768's now-edited live body.
  `gh pr list --repo launchpad-26/buzz --state all --limit 100` shows exactly three PR-author
    logins in this fork: `serina-mcfall`, `tucktuck101`, `benmitchell11`. Spot-checked PRs from
    each (#1907, #1906 for benmitchell11; #2066, #1998 for serina-mcfall) that carry no
    `by:agent` label are still clearly agent-produced work (corpus docs, a CODEOWNERS fix) —
    consistent with this fork's own convention that agents author every PR under a human
    cohort member's account (see `give-approval-command-when-opening-a-pr` memory: "she
    authors every PR I open"). No separate bot/service account exists in this fork.
  No existing agent-identity registry file was found anywhere in the repo (`grep` across
    `launchpad/`, `.github/` for "agent identit*", "AGENT_IDENTIT*" etc. returns nothing
    resembling a login list) — the configured list must be introduced fresh, not reused.
  `launchpad-26/buzz-infrastructure`'s `.github/scripts/pr_body_check.py` carries the identical
    `looks_agent_authored` gap (per the issue's own Environment section) — explicitly OUT OF
    SCOPE for this PR (different repo).

STEP 1  Add the author-identity signal to `pr_body_check.py`                    [independent]
        - Add `parse_agent_identities(raw: str | None) -> frozenset[str]`: comma-separated
          `AGENT_AUTHOR_LOGINS` env value → frozenset of trimmed, `.casefold()`-normalised,
          non-empty logins; unset/blank → empty frozenset (no author is ever treated as a
          signal when unconfigured — same behaviour as today). Casefolding here means the
          membership check in `agent_signals` only needs to casefold the incoming `author`,
          not re-normalise the whole set on every call.
        - Add `agent_signals(visible, labels, author, agent_identities) -> tuple[bool, bool, bool]`
          returning `(labelled_agent, body_says_agent, author_says_agent)` as one shared
          helper, so `check()` and `main()`'s final "(agent)"/"(human)" print cannot compute
          `is_agent` two different ways and disagree (the exact class of bug this file's own
          docstring warns about for markdown parsing). `author_says_agent` compares with
          `.casefold()` on both `author` and every entry in `agent_identities` (normalised once,
          in `parse_agent_identities`, not re-normalised per call) — a differently-cased login
          typo'd into the workflow's configured list must not silently and permanently disable
          the signal for that account with no error and no failing test (review-plan finding,
          2026-09-04: exact-match membership was reviewed and rejected for this reason).
        - `check()` gains two new trailing keyword-defaultable params:
          `author: str | None = None, agent_identities: frozenset[str] | None = None` — placed
          after the existing `changed_files` param so every existing positional call in
          `test_pr_body_check.py` keeps working unchanged.
        - `check()` computes `is_agent` from all three signals via `agent_signals(...)`.
        - Generalise the existing "no by:agent label" error (currently gated on
          `body_says_agent and not labelled_agent`) to also fire on `author_says_agent and not
          labelled_agent`, with the message naming which signal(s) fired (body content vs.
          author identity) rather than unconditionally claiming "This body carries agent
          provenance" when it was actually the author signal.
        - `main()` reads `PR_AUTHOR` and `AGENT_AUTHOR_LOGINS` from the environment, passes
          them into `check()`, and recomputes the final `kind` label via the same
          `agent_signals()` helper instead of `"by:agent" in labels` alone.
        done when: `python3 -c "import pr_body_check as m; print(m.check.__doc__)"` run from
          `launchpad/scripts/` shows the new params in `inspect.signature(m.check)`, and a
          manual call `m.check("### Issue type\nTask\n\n### Feature\nN/A\n\nCloses #1\n", [],
          [1], author="serina-mcfall", agent_identities=frozenset({"serina-mcfall"}))` returns
          at least one error naming the missing provenance/Authority/Deferred-blockers/fence
          sections (proving the agent-only rules now fire from author identity alone).

STEP 2  Regression tests reproducing the exact gap                              [needs 1]  ← RUNS HERE
        - New test class in `test_pr_body_check.py` (matching existing class-per-concern
          style, e.g. `AuthorIdentityIsAThirdSignal`) covering:
          (a) a body with no label, no provenance table, no Authority section, authored by a
              configured agent identity → `check()` raises the agent-only errors (provenance,
              Not verified, fence, Authority, Deferred blockers) — this is the exact issue
              repro and MUST fail against the pre-fix code and pass after.
          (b) the same body with an unconfigured/unknown author → still `(human)`, zero agent
              errors raised — proves the signal is scoped to the configured list, not "any
              author triggers agent mode".
          (c) author-signal-without-label triggers the same "no by:agent label" rule-3 error
              as body-signal-without-label does today (generalisation didn't regress the
              existing rule).
          (d) `main()`-level test (via `run_main`, extended to accept `author=` /
              `agent_identities=` kwargs) asserting the printed `(agent)`/`(human)` kind
              reflects all three signals, not the label alone — this is the second instance
              of the bug (the `kind` line) and needs its own assertion since `check()`'s
              return value doesn't carry `kind`.
          (e) `parse_agent_identities` unit tests: unset/blank → empty frozenset; comma list
              with surrounding whitespace → trimmed set; one blank entry among commas ignored.
        - Run tests (a), (c) and (d) — the ones that actually exercise the fixed code path —
          against the pre-fix `pr_body_check.py` (stash the Step-1 diff or check out `HEAD` for
          the file) to confirm each fails there, then re-apply and confirm all pass. (b) and (e)
          are boundary/negative-control tests with no reason to fail pre-fix — (b) trivially
          holds pre-fix since there is no author signal at all yet, and (e) tests a function
          that does not exist before Step 1 — so do not read a pass from either of those as
          evidence of anything; the falsification proof rests on (a), (c), (d) alone.
        done when: `python3 -m unittest discover -s launchpad/scripts -t launchpad/scripts -v`
          run from the worktree root is all green, and tests (a), (c), (d) were observed
          failing against the pre-Step-1 file (paste both outputs in the PR body's fenced
          block).

STEP 3  Wire the workflow to supply the author and the configured identity list  [needs 1]
        - `.github/workflows/launchpad-pr-check.yml`, "Validate PR body" step: add
          `PR_AUTHOR: ${{ github.event.pull_request.user.login }}` to the step's `env:` block.
        - Add `AGENT_AUTHOR_LOGINS: serina-mcfall,tucktuck101,benmitchell11` to the same `env:`
          block, with a short comment above it explaining WHY human-looking logins are treated
          as agent identities in this fork (agents run under the cohort member's own GitHub
          account here — there is no separate bot account — per the evidence gathered in
          ALREADY TRUE), and a note that adding a new cohort member's login to this list is a
          one-line workflow edit. The comparison in `pr_body_check.py` is case-insensitive
          (`.casefold()`, Step 1), so this list does not need to match GitHub's exact stored
          casing byte-for-byte — a reasonable-effort casing is enough.
        - No other workflow step needs a change: `PR_AUTHOR` needs no GitHub API call (it's a
          field already on the `pull_request` event payload), unlike `CLOSING_REFS`/
          `FEATURE_CHILDREN` which need the two existing `gh api` steps.
        done when: `git diff .github/workflows/launchpad-pr-check.yml` shows only the two new
          `env:` lines (plus the explanatory comment) inside the existing "Validate PR body"
          step — no new step, no change to the `closing`/`feature` steps or the `scripts` job.

STEP 4  Run the full local gate                                                 [needs 2, 3]
        - `python3 -m unittest discover -s launchpad/scripts -t launchpad/scripts -v`
        - `python3 launchpad/scripts/mutation_harness.py` — read `TARGETS` and `OWN_TESTS` in
          `launchpad/scripts/mutation_harness.py` before relying on this: it mutates only
          `preflight_core.py`/`no_model` functions and runs only `test_preflight_core.py` +
          `test_no_model.py` (review-plan finding, 2026-09-04, confirmed by reading the file —
          it never touches `pr_body_check.py`). Run it here only as a REGRESSION check — proof
          that this change hasn't broken the unrelated preflight controls it shares a directory
          with. It proves nothing about the new `agent_signals`/`parse_agent_identities` logic;
          that proof is Step 2's pre-fix/post-fix test diff, already captured there. Do not
          describe this run in the PR body as verifying the new controls.
        - `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/launchpad-pr-check.yml'))"`
          (or `actionlint` if available) to confirm the workflow YAML still parses.
        done when: all three commands exit 0, with their real output captured for the PR's
          required fenced code block (not paraphrased), and the mutation-harness output is
          captioned as a regression check, not as coverage evidence for this fix.

PARALLEL  Step 1 has no prerequisite and is the only file-owning step until it lands; Steps 2
  and 3 both depend on Step 1's function/param shapes existing (2 reads `check()`'s new
  signature and `agent_signals`; 3 just needs the env var names Step 1 reads) but touch
  disjoint files (`test_pr_body_check.py` vs. the workflow YAML) so 2 and 3 may run as parallel
  subagents once 1 lands. Step 4 needs both 2 and 3 finished since it runs the suite the tests
  extend and validates the YAML the workflow step changed.

GATES     `review-code` after Step 1 (the detection-logic change: three-signal `is_agent`,
  the generalised rule-3 message, the `main()` kind fix). `review-tests` after Step 2 (are the
  new tests actually falsifiable — do they fail pre-fix, and does (b) really prove the signal
  is scoped rather than accidentally always-true). `review-final` once Steps 1-4 are all in
  before opening the PR, per this repo's standard flow. `qa` explore mode does not apply — this
  is a CI script with no runtime UI/API surface beyond the two entry points already exercised
  by direct `python3` invocation and the unit-test suite; there is nothing an explore session
  would reach that STEP 2/4's commands don't already cover.

BUDGET    Step 1 is the step most likely to eat the budget: `agent_signals()` has to stay a
  single source of truth for both `check()`'s rule-3 message and `main()`'s kind print without
  quietly duplicating the boolean logic in two places (the exact class of drift this file's own
  docstring warns about for markdown parsing) — getting the shared-helper shape right the first
  time avoids a second pass.

OPEN      The issue gives no `Size` line — this plan assumed ≤30 minutes / 5-step cap based on
  the issue's own "suggested shape, not prescribed" framing and its narrow, single-file-plus-
  workflow blast radius; flagging rather than blocking per Auto Mode.
  Whether `benmitchell11` belongs in `AGENT_AUTHOR_LOGINS` alongside the two logins the issue's
  own reproduction touches (`serina-mcfall` via #1768) is this plan's one judgment call — the
  evidence (his unlabeled-but-clearly-agent PRs #1906/#1907) supports it, but the issue itself
  never names a login list, only "a configured list of agent identities" as a suggestion. Left
  in because the workflow env var is a one-line, low-cost edit to correct if wrong.
  Whether the generalised rule-3 message text is good enough for a human reader is a wording
  judgment call for `review-code`, not something this plan can pre-verify.

LEFT OUT  `launchpad-26/buzz-infrastructure`'s port of the same file/gap — explicitly out of
  scope per the task brief (different repo, needs its own PR and access). Noted for the final
  report, not filed as a new issue by this plan (the parent issue #1771 already names it).
  No change to `ISSUE_TYPES`, `PROVENANCE_FIELDS`, `DEFERRED_CEILING`, or any of the
  reference/batch/delegated-authority logic — none of it is implicated by this defect.
