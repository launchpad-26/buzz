# Issue #183 — Security CI job fails on pre-existing yanked spin crate advisory (dormant, unrelated to any specific PR)

Stated size: no `Size` line on the issue → treated as ≤30 minutes (cap: 5 steps),
given the issue's own three "Possible directions" already scope the work to a
single-file/lockfile dependency bump or a `deny.toml` ignore-list addition. This
assumption is called out again in OPEN below rather than blocking on it, per the
parent task's explicit direction to proceed.

ALREADY TRUE (verified against git and a live `cargo-deny` run, not the issue's
original evidence snippet)

  - Worktree exists at
    `/home/serina/Launchpad/buzz/__worktrees/fix-issue-183-yanked-spin-advisory`,
    branch `fix/issue-183-yanked-spin-advisory`, tracking `origin/launchpad`,
    HEAD at `aef93f2c2` (`Merge pull request #1954 ...`). Working tree clean.
  - `Cargo.lock` and `deny.toml` on this HEAD are byte-identical to
    `origin/launchpad` (`git diff --stat origin/launchpad HEAD -- Cargo.lock
    deny.toml` is empty) — the reproduction below is against the real current
    state of the target branch, not a stale local copy.
  - `deny.toml`'s `[advisories].ignore` list has four existing entries
    (`RUSTSEC-2024-0384`, `RUSTSEC-2024-0436`, `RUSTSEC-2026-0194`,
    `RUSTSEC-2026-0195`) but **no** `spin` or `async-utility` entries, and no
    explicit `[advisories].yanked` key at all.
  - Root cause, established via `agentic-debugging`'s
    Observation/Hypothesis/Test/Result/Conclusion loop:
    - **Observation**: running `cargo-deny check advisories` (hermit-pinned
      `cargo-deny 0.19.0`, the same binary/version CI uses) on this exact HEAD
      prints three `warning[yanked]` blocks — `spin 0.9.8` (via
      `flume → mdns-sd → mesh-llm-host-runtime`), `spin 0.10.0` (via
      `futures-buffered → n0-future → iroh`, and `iroh` is a *direct* dependency
      of `buzz-relay-mesh` in this repo), and `async-utility 0.3.1` (via
      `nostr-sdk → mesh-llm-client`/`mesh-llm-host-runtime`) — but still exits
      `0` with `advisories ok`. This contradicts the issue's premise that the
      check currently fails.
    - **Hypothesis**: `cargo-deny`'s `yanked` lint defaults to non-fatal
      (`warn`) without an explicit `[advisories].yanked = "deny"` override, so
      the historical CI failure (job log linked in the issue,
      `advisories FAILED`, exit 1) needed that override present at the time,
      or a `cargo-deny` version where the default was stricter.
    - **Test**: temporarily added `yanked = "deny"` to `deny.toml` and reran
      `cargo-deny check advisories`.
    - **Result**: reproduced the issue's exact failure signature —
      `advisories FAILED`, exit code 1 — then removed the override and
      confirmed `advisories ok` / exit 0 returns.
    - **Conclusion**: the check is not *currently* hard-failing under default
      config, but the three yanked crates are still resolved in `Cargo.lock`
      and remain one config change (or one `cargo-deny` default-policy change
      upstream) away from failing again — consistent with the issue's own
      framing ("dormant ... unrelated to any specific PR"). Fixing the
      underlying yanked resolutions removes the latent risk rather than
      leaving it to luck.
  - `cargo update -p spin@0.9.8 --dry-run` resolves to `spin 0.9.9`;
    `cargo update -p spin@0.10.0 --dry-run` resolves to `spin 0.10.1`;
    `cargo update -p async-utility --dry-run` resolves to `async-utility
    0.3.2`. All three are dry-run-clean, each touches exactly 1 locked
    package (240–241 other packages reported unchanged), and none requires
    any change to this repo's own `Cargo.toml` direct dependencies or to the
    pinned `mesh-llm` git tag.
  - Issues #71 (open, dependency-alerting-path task), #64 (closed ADR,
    Dependabot/Renovate decision), #46 (closed ADR, CI security-check gating),
    and #62 (open PRD, general security-hygiene sequence) are all broader
    dependency-policy work items — none of them names or claims ownership of
    this specific yanked-`spin`/`async-utility` resolution. Proceeding here as
    a one-off fix per the issue's option 3 guidance ("if unrelated/inactive,
    proceed").

STEP 1  Update the three yanked crates in Cargo.lock            [independent]
        Run `cargo update -p spin@0.9.8 -p spin@0.10.0 -p async-utility`
        for real (no `--dry-run`), from repo root inside the worktree.
        done when: `git diff --stat Cargo.lock` shows changes to exactly
        `Cargo.lock` (no other file), and inspection shows `spin` locked at
        `0.9.9` and `0.10.1` (no `0.9.8` or `0.10.0` entries remain), and
        `async-utility` locked at `0.3.2`.

STEP 2  Confirm cargo-deny is clean                                [needs 1]
        Run `cargo-deny check advisories`, then `cargo-deny check` for the
        full gate, and confirm zero `warning[yanked]` blocks.
        done when: `cargo-deny check advisories` output contains no
        `warning[yanked]` lines and exits 0; `cargo-deny check` overall exits
        0 with `advisories ok, bans ok, licenses ok, sources ok`.

STEP 3  Build buzz-relay against the updated lockfile   [needs 1]  ← RUNS HERE
        Run `cargo build -p buzz-relay` — it dev-depends on
        `mesh-llm-sdk`/`mesh-llm-embedded-runtime`, the path that pulls
        `spin` and `async-utility`, so this exercises the changed tree.
        done when: `cargo build -p buzz-relay` exits 0.

STEP 4  Commit the Cargo.lock change                            [needs 2, 3]
        `git commit -s` (DCO required), message explaining the
        yanked-crate resolution and citing #183.
        done when: `git log -1 --format='%H %s'` shows the new commit, and
        `git log -1 --format='%B' | grep -q '^Signed-off-by:'` is true.

STEP 5  Push and open the PR                                       [needs 4]
        `gh pr create` as a standalone command (no `cd` chained in front —
        the `pr-gate.sh` hook rejects that shape), base `launchpad`, body
        includes "Closes #183". Check 2-3 recent agent-authored merged PRs'
        labels (`gh pr list --repo launchpad-26/buzz --search "is:merged
        label:by:agent" --limit 3 --json number,labels`) to decide whether to
        add a `by:agent` label to match convention.
        done when: `gh pr view <n> --repo launchpad-26/buzz --json url,body`
        shows the PR exists, targets `launchpad`, and its body contains
        "Closes #183".

PARALLEL  Step 1 is the only step with no prerequisite. Steps 2 and 3 both
          need only step 1 and touch no shared file (deny check reads
          `Cargo.lock`/`deny.toml`; the build reads `Cargo.lock`/source), so
          they could run as parallel subagents, but both are near-instant
          local commands here and running them sequentially in one session is
          simpler than coordinating two subagents for a task this small.
          Steps 4 and 5 are strictly sequential (commit must exist before
          push/PR) and touch git state directly, so no parallelism there.

GATES     No `review-*` skill applies to a lockfile-only dependency bump with
          no source or test changes — there is no diff for `review-code`,
          `review-tests`, or `review-a11y` to examine, and no plan for
          `review-plan` beyond this one (already covered by `plan-issue`
          itself). `qa` explore mode does not apply: there is no new runtime
          interface (CLI flag, API, UI) to exercise — `cargo-deny check` and
          `cargo build` in steps 2–3 already are the verification surface for
          this change. Per the parent task, this skill hands off to
          `serina:build-change`, which runs its own review-gate step at
          handover; no additional gate is named here beyond that.

BUDGET    Step 1 (`cargo update`) is the step most likely to eat the budget,
          not because the command is slow but because a network hiccup
          against the sparse crates.io index, or a surprise transitive
          resolution shift beyond the three targeted packages, would need
          re-diagnosis before continuing — mitigated by scoping the update to
          exactly the three named packages via `-p`, already dry-run-verified
          to touch only those three.

OPEN      The issue has no `Size` line — this plan assumed ≤30 minutes given
          the issue's own scoping. The issue's evidence snippet only shows
          `spin` failing; this plan additionally resolves `async-utility
          0.3.1`, which is also yanked and present in the same `cargo-deny`
          output today — leaving it unresolved would still print a
          `warning[yanked]` and defeat the point of doing this fix at all, so
          it is folded in rather than filed separately.

LEFT OUT  `deny.toml` `[advisories].ignore` entries (issue's option 1) — not
          needed, since option 2 (`cargo update`) resolves cleanly with zero
          risk to this repo's direct dependencies, which the issue and the
          parent task both call the strictly-better outcome when available.
          No `[advisories].yanked = "deny"` hardening is added either: making
          the lint fatal is a policy decision belonging to the broader
          dependency-hygiene work already tracked in #62/#71, not this
          one-off fix, and turning it on here would require also covering the
          two `RUSTSEC` ignore-list entries' interaction with a stricter
          default — out of scope.
