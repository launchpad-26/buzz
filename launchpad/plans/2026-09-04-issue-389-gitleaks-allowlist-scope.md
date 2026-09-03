Issue #389 — bug: two global gitleaks allowlist entries are broader than their stated reason
Stated size: no Size line on the issue → cap: 5 steps (assumed ≤30-minute size: a two-entry
config edit in one file, already fully diagnosed by the issue's own reproduction; see OPEN)

ALREADY TRUE  (verified against git and a live gitleaks run, not notes)
  .gitleaks.toml's global [allowlist] (lines 104-125 on origin/launchpad HEAD) has:
    - paths = ['''launchpad/scripts/security_audit_fixtures/secrets/.*''', '''(^|/)Cargo\.lock$''']
    - regexes = ['''<[A-Za-z0-9 ]+>''', '''38980a43aba04331ba61b5e7b64b90e250cd411d042050eaf102a408acc6c379''']
  gitleaks 8.30.1 (the version pinned in .github/workflows/launchpad-security-audit.yml,
    SHA256 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb) is available in
    this environment: downloaded, checksum-verified, and run directly for this investigation.
  Reproduced against the real repo, not a synthetic fixture: with the global [allowlist]
    stripped, gitleaks detect against launchpad/deploy/archived/runbooks/dev-deployment-SOP.md
    (current path and content) produces exactly 1 finding (generic-api-key at line 1080, the
    "Public key:" line) and 0 findings on the "Secret key: <64 hex characters>" placeholder
    line alone. The literal-value regexes entry already covers the one real finding.
  Reproduced against full git history (9998 commits, `gitleaks detect` with no --log-opts,
    matching launchpad/scripts/security_audit_secrets_check.py's full-history invocation):
    baseline (current config) reports 281 findings. Three other Cargo.lock paths exist
    somewhere in this repo's history (buzz-agent-core/Cargo.lock,
    crates/buzz-push-gateway/tests/fixtures/app-attest-generator/Cargo.lock,
    goose-acp/Cargo.lock) but none of them trip any rule — confirmed by running the full
    scan with the Cargo.lock paths entry narrowed to the two literal paths named in the
    comment, which reports the same 281 findings, identical file:line:rule set, as baseline.
  Removing the bracket-placeholder regexes entry entirely and narrowing the Cargo.lock paths
    entry together still reproduces exactly 281 findings, identical set, against full history.
  launchpad/scripts/test_security_audit*.py (88 tests, including
    test_security_audit_gitleaks_ruleset.py under REQUIRE_GITLEAKS_RULESET=1) passes
    unchanged against the narrowed config.
  Work is happening in an isolated worktree at
    /home/serina/Launchpad/buzz/__worktrees/fix-issue-389-gitleaks-allowlist-scope on branch
    fix/issue-389-gitleaks-allowlist-scope (from origin/launchpad, current HEAD aef93f2c2a).
  .gitleaks.toml already carries an uncommitted working-tree edit in that worktree, made
    during the investigation above, that implements both changes described in STEP 1 below.

STEP 1  Edit .gitleaks.toml: remove the bracket-placeholder regexes entry               [independent]
        '''<[A-Za-z0-9 ]+>''' and its comment (it is not needed for the stated reason —
        the SOP's `<64 hex characters>` placeholder alone produces 0 findings); narrow the
        Cargo.lock paths entry from '''(^|/)Cargo\.lock$''' to the two literal paths it was
        verified against, '''^Cargo\.lock$''' and '''^desktop/src-tauri/Cargo\.lock$'''.
        Keep the existing literal public-key regexes entry unchanged. Update the comments so
        they describe what the entry now does and cite #389, matching the style of the
        adjacent public-key and postgres entries (state the verified case, not just the fix).
        done when: `git diff .gitleaks.toml` shows only the removed regexes entry, the
        narrowed paths entry, and their comments — no rule blocks, no unrelated formatting
        changes — and `toml` parses cleanly (`python3 -c "import tomllib,sys; tomllib.load(open('.gitleaks.toml','rb'))"` exits 0, or an equivalent TOML parser if tomllib is unavailable).

STEP 2  Re-run the harness's own gitleaks ruleset tests                                 [needs 1]  ← RUNS HERE
        `REQUIRE_GITLEAKS_RULESET=1 python3 -m unittest discover -s launchpad/scripts -p
        "test_security_audit*.py"` from the worktree root, with the pinned gitleaks 8.30.1 on
        PATH.
        done when: all tests pass (0 failures, 0 errors) — this is the one existing suite that
        proves .gitleaks.toml's rules still match anything, per the workflow's own comment on
        REQUIRE_GITLEAKS_RULESET.

STEP 3  Full-history verification scan: confirm zero new and zero removed findings      [needs 1]
        Run `gitleaks detect --config .gitleaks.toml --report-format json --report-path <out>
        --redact --no-banner` from the worktree root (matching
        launchpad/scripts/security_audit_secrets_check.py's exact invocation for the
        full-history/reporting path) and diff the resulting {File, StartLine, RuleID} set
        against the pre-change baseline captured during investigation (281 findings).
        Separately run `python3 launchpad/scripts/security_audit_secrets_check.py .` and
        confirm its one-line summary count and rule-id sample are unchanged from the
        pre-change run.
        done when: the finding set is byte-for-byte identical to the pre-change baseline
        (same count, same file:line:rule-id set) — proving the narrower allowlist neither
        suppresses less than before (no new findings surfaced) nor suppresses more (no
        scope creep introduced).

STEP 4  Commit and open the PR                                                          [needs 2, 3]
        `git commit -s` (DCO required) with a message describing the two scope narrowings
        and citing #389. Push the branch. Run `gh pr create` as a standalone command (no `cd`
        prefix — this repo's pr-gate hook rejects `cd <dir> && gh pr create` as one call),
        based on `launchpad`, with "Closes #389" in the body. Check 2-3 recent merged
        agent-authored PRs (`gh pr list --repo launchpad-26/buzz --search "is:merged
        label:by:agent" --limit 3 --json number,labels`) for label convention and match it.
        The repo's pr-gate hook is expected to require a `review-final` ledger verdict this
        plan doesn't produce, and fall back to opening a draft PR via its own documented
        escape valve — that is expected, not a failure to fix.
        done when: a PR exists on GitHub targeting `launchpad`, its body contains "Closes
        #389", and its label matches the convention found in the 2-3 PRs checked above.

PARALLEL  None of these steps can run in parallel: 1 must land before the tests/scans in 2
          and 3 can validate anything, and 2 and 3 both read the same worktree state that 1
          produces (though 2 and 3 themselves don't conflict with each other and could run
          concurrently as two subagents if desired — both are read-only against the same
          committed edit). Step 4 needs both 2 and 3 green before it commits.
GATES     No review-* skill applies to the substance of a two-entry TOML config narrowing —
          there is no application code, UI, or test suite being authored for this change to
          route through review-code/review-tests/review-a11y. serina:build-change's own
          handoff to a review gate (pr-gate.sh's review-final ledger requirement) still
          applies per this repo's normal process; it is expected to fall back to a draft PR
          per STEP 4's note, not to block. qa explore mode does not apply: there is no runtime
          interface to exercise beyond the two verification scans in STEP 2 and STEP 3, which
          already are the full mechanical treatment.
BUDGET    STEP 3's full-history gitleaks scan is the step most likely to eat time — it scans
          9998 commits and took ~20s per run in investigation, but re-running it plus the
          88-test suite plus a second confirmation pass could approach several minutes total
          if repeated for any reason (e.g. STEP 1's edit needing a second pass).
OPEN      The issue has no Size line, so the 5-step cap above is an assumption, not a read
          value — flagged per the skill's instruction to say so rather than silently pick one.
          Given the fix is a two-entry, single-file TOML edit with the reproduction already
          done by the issue itself, ≤30 minutes reads as the right size, but this is this
          plan's call, not the issue's.
LEFT OUT  Re-litigating whether gitleaks is the right secret-scanning engine, or whether
          ADR-0006's decision should change — out of scope, this issue only narrows two
          existing allowlist entries. Auditing every other rule/allowlist pair in
          .gitleaks.toml for the same over-broad-scope pattern — not asked for by #389, which
          names exactly two entries; a broader audit would be its own issue. Adding a fixture
          under launchpad/scripts/security_audit_fixtures/ that pins the placeholder-produces-
          zero-findings behavior as a regression test — the existing
          test_security_audit_gitleaks_ruleset.py suite already asserts the ruleset fires on
          its fixtures, and this change removes an allowlist entry rather than a rule, so
          there is no rule behavior for a new fixture to pin; STEP 2's re-run of the existing
          suite plus STEP 3's full-history diff already cover regression risk for an allowlist
          change without inventing a new fixture whose only job would be re-proving what the
          issue itself already measured.
