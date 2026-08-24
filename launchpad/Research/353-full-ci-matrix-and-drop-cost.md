# The full CI matrix on a vendor drop: has it passed, and what does it cost

**Title:** Whether this fork's full CI matrix has ever run green, and the cost of one run
**Summary:** Establishes that the full 23-job matrix has passed green twice, both times on an upstream sync branch — including PR #216, a 113-commit / 981-file drop. Cost is zero billable minutes (public repository, GitHub-hosted runners) and roughly 53 minutes wall-clock. Also records that this fork has already taken two upstream drops, which corrects the impression left by #273's Evidence section, and that PR #216's body is a complete worked example of the drop report #306 is trying to specify.
**Tags:** `upstream-sync` `vendor-drop` `ci` `cost` `actions` `prd-273`
**Established:** 2026-08-22 · **Answers:** [#353](https://github.com/launchpad-26/buzz/issues/353) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**Yes — twice, and both times on a full upstream sync.** Run `32095795174` (branch `sync-upstream-2026-08-18`, PR #216, **113 commits across 981 files**) completed with **23 of 23 jobs succeeding and none skipped**. Run `31358601797` (PR #12, 64 commits, 299 files) did the same.

**Cost is not a constraint.** Zero billable minutes — the repository is public, so GitHub-hosted `ubuntu-latest`, `windows-latest` and `macos-latest` runners are free. The real cost is ~53 minutes wall-clock and ~198 job-minutes of fan-out.

The consequential part is not the cost figure. It is that **success criterion 6 is largely already satisfied and success criterion 2's mechanism has been exercised twice**, on real drops, by hand. What is missing is only that no check is *required* — a branch-protection gap, not a build problem.

---

## Evidence

### The repository is public, so runners are free

```
$ gh api repos/launchpad-26/buzz --jq '{visibility,private,fork,parent:.parent.full_name}'
{"fork":true,"parent":"block/buzz","private":false,"visibility":"public"}
```

### Both sync runs: 23 jobs, all green, none skipped

```
$ gh api "repos/launchpad-26/buzz/actions/runs/32095795174/jobs?per_page=100" \
    --jq '.jobs[] | [.conclusion,.name] | @tsv' \
  | awk -F'\t' '{c[$1]++} END {for(k in c) print k, c[k]}'
success 23

$ gh api "repos/launchpad-26/buzz/actions/runs/31358601797/jobs?per_page=100" ...
success 23
```

For contrast, PR #308 — two markdown files — ran 6 checks and skipped 16. `ci.yml` gates on a changed-paths filter, so only a broad change exercises the whole matrix. A drop is the broadest change the fork ever makes.

### Per-job wall-clock and runner class, run 32095795174

```
  23.4m  success  ubuntu-latest    Desktop Core
  28.2m  success  windows-latest   Windows Rust (x86_64-pc-windows-msvc)
  18.7m  success  ubuntu-latest    Desktop E2E Relay
  17.2m  success  macos-latest     Desktop Build (macOS)
  16.7m  success  ubuntu-latest    Mobile
  14.8m  success  ubuntu-latest    Desktop Smoke E2E (3)
  14.0m  success  ubuntu-latest    Desktop Smoke E2E (1)
  13.8m  success  ubuntu-latest    Desktop Smoke E2E (4)
  12.4m  success  ubuntu-latest    Desktop Smoke E2E (2)
   8.7m  success  ubuntu-latest    Desktop E2E Integration (2/2)
   7.6m  success  ubuntu-latest    Desktop E2E Integration (1/2)
   5.1m  success  ubuntu-latest    Unit Tests
   4.4m  success  ubuntu-latest    Rust Lint
   3.6m  success  ubuntu-latest    Server Cross-Compile (aarch64-unknown-linux-musl)
   3.6m  success  ubuntu-latest    Server Cross-Compile (x86_64-unknown-linux-musl)
   2.7m  success  ubuntu-latest    Relay E2E
   0.9m  success  ubuntu-latest    Backend Integration (relay e2e)
   0.7m  success  ubuntu-latest    Security
   0.5m  success  ubuntu-latest    Web
   0.4m  success  ubuntu-latest    Detect Changed Paths
   0.1m  success  ubuntu-latest    Dead Token Reference Guard
   0.1m  success  ubuntu-latest    Desktop                  (aggregator gate)
   0.1m  success  ubuntu-latest    Desktop E2E Integration  (aggregator gate)
--- sum of job minutes: 197.8
```

### Billable time is zero on every runner class

```
$ gh api "repos/launchpad-26/buzz/actions/runs/32095795174/timing"
{"billable":{"UBUNTU":{"total_ms":0,"jobs":42,...},
             "WINDOWS":{"total_ms":0,"jobs":2,...},
             "MACOS":{"total_ms":0,"jobs":2,...}},
 "run_duration_ms":1416000}
```

`run_duration_ms` is 23.6 minutes; the run's `created_at`→`updated_at` span was 53.5 minutes, the difference being queueing across a 23-job fan-out. Both figures matter: 24 minutes is the critical path, 53 minutes is what a person waits.

### Lanes that do not reliably pass

Failed job names across the 22 failing `ci.yml` runs in the last 166:

```
  15 Desktop                       (aggregator — fails when any desktop lane fails)
   8 Desktop Core
   6 Security
   5 Desktop Smoke E2E (2)
   5 Desktop E2E Integration
   3 Desktop Smoke E2E (4)
   2 Desktop Smoke E2E (3) / (1) / E2E Integration (1/2) / (2/2)
   1 Desktop E2E Relay
   1 Desktop Build (macOS)
```

Failure is concentrated in desktop and E2E, not in Rust or relay. Overall: 129 success, 22 failure, 15 cancelled out of 166 runs.

`Mobile` has never failed in CI in this window — but PR #216's own body records `mobile-test` failing **locally** with four timestamp-layout tests at large accessible text sizes, confirmed pre-existing against `origin/launchpad`'s tip and tracked at **#215**. So the local gate and the CI gate disagree about mobile, and CI is the more forgiving of the two. Anyone treating a green CI run as equivalent to a clean local `just ci` is wrong in that one respect.

### The fork has already taken two drops

```
$ gh pr list --repo launchpad-26/buzz --state all --search "sync-upstream" --json number,title,headRefName,changedFiles,mergedAt,author
#216  sync-upstream-2026-08-18  113 commits, 981 files  MERGED 2026-08-19  serina-mcfall
#12   sync-upstream-2026-08-10   64 commits, 299 files  MERGED 2026-08-11  tucktuck101
```

Merge-base `f8692fa9b` (2026-08-17) **is the result of PR #216**. The 67-commit backlog is five days of upstream activity, not five weeks of neglect.

---

## What this means for #273

**Success criterion 6 is closer to met than the PRD assumes.** `just ci`'s CI equivalent already runs, green, on a 981-file upstream merge. What remains is making a check *required*, which is a branch-protection question ([#358](https://github.com/launchpad-26/buzz/issues/358), [#154](https://github.com/launchpad-26/buzz/issues/154)), not an engineering one.

**Success criterion 2's mechanism has been exercised twice.** "A clean upstream merge reaches a reviewable PR" is not unproven; it has happened, by hand, and passed the full gate. What is unproven is the *unattended* version, and under the corrected premise the drop is deliberate anyway — so the part still worth building is the report, not the merge.

**#273's Evidence section leaves a false impression.** It states *"No upstream commit has been merged into `launchpad` in that window"* and that the only sync automation "runs on a contributor's personal fork". Both are true as worded; together they read as a fork that has never synced. It has synced twice, and the second sync is where merge-base `f8692fa9b` came from. Worth correcting, because "nothing owns this job" and "two people have done this job by hand twice" call for different work.

**ADR-0022's affordability argument does not need to account for CI cost.** Free runners plus a 24-minute critical path means the constraint on drop frequency is human attention, exactly as that record already says — now with a number behind it rather than an assumption.

**#306 should start from PR #216's body, not from a blank page.** That PR body already contains, unprompted, the artifact #306 is trying to specify: a notable-upstream-changes summary with upstream PR numbers and why each matters to this fork; a per-file risk table naming each fork change and whether it survived the merge; a gate table with raw results; and an explicit pre-existing-failure carve-out with evidence that it is pre-existing. It is a worked precedent produced by someone doing the job, which is better input than a design discussion.

---

## Confidence and limits

**High confidence** on job counts, durations, runner classes and zero-billing — all pasted API output from completed runs, not inference.

**Not established: the Actions minute allowance and consumption.** The org billing endpoint is closed to this token:

```
$ gh api "orgs/launchpad-26/settings/billing/actions"
{"message":"Not Found",...,"status":"404"}
gh: This API operation needs the "admin:org" scope.
```

I judge this moot rather than unanswered — with `total_ms: 0` on every runner class there is no consumption to check against an allowance. It stops being moot the moment the repository is made private, at which point the `macos-latest` lane's 10× multiplier would dominate.

**Not checked.** Whether the Windows and macOS lanes use standard or larger runners — I read only `labels[0]`. Whether the 39 active caches totalling 8.7 GB are near the 10 GB per-repository limit, which would slow future runs; `Desktop Core` at 23 minutes leans on the pnpm store cache and is the lane that would notice. I did not dispatch any workflow myself; every figure comes from runs that already happened. I did not read the failure logs of the 22 failing runs to establish whether the desktop and E2E failures are flakes or real, only counted them by job name.
