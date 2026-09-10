---
id: verification-strategy-quality-model
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The root CLAUDE.md's Quality Gates section names seven distinct checks a change passes through: repository-wide formatting, lint, and static checks (`just ci`), pre-commit hooks that auto-fix formatting via `stage_fixed` and block on unfixable lint issues, pre-push hooks running the differential file-size gate, clippy, desktop TypeScript typechecking (`tsc --noEmit`), and fast unit tests, builds being CI-only, and a required DCO `Signed-off-by` trailer enforced by a commit-msg hook plus a stated 'DCO Check'."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "`Justfile`'s `check` recipe (line 96) chains `fmt-check`, `clippy`, `desktop-check`, `desktop-tauri-fmt-check`, `desktop-tauri-clippy`, `web-check`, `mobile-check`, `security-review-check`, and `file-size-check`; the `ci` recipe (line 307) chains `check` plus `test-unit`, `desktop-test`, `desktop-build`, `desktop-tauri-check`, `desktop-tauri-test`, `web-build`, and `mobile-test`."
    entry_class: FACT
    evidence:
      - "Justfile:96"
      - "Justfile:307"
  - statement: "`fmt-check` runs `cargo fmt --all -- --check` (Rust formatting) and `desktop-tauri-fmt-check` runs the same against the Tauri crate; `fix-all` (line 164) runs `fmt`, `desktop-tauri-fmt`, `desktop-fix`, `web-fix`, and `mobile-fix` to auto-fix formatting and lint issues in one shot."
    entry_class: FACT
    evidence:
      - "Justfile:117"
      - "Justfile:118"
      - "Justfile:157"
      - "Justfile:158"
      - "Justfile:164"
  - statement: "`clippy` runs `cargo clippy --workspace --all-targets -- -D warnings`, turning every clippy warning into a build failure."
    entry_class: FACT
    evidence:
      - "Justfile:121"
      - "Justfile:122"
  - statement: "`desktop-check` runs `pnpm check`, which desktop/package.json defines as `biome check . && pnpm check:px-text && pnpm check:pubkey-truncation` — Biome lint/format plus two custom guard scripts — and does not itself run TypeScript type-checking."
    entry_class: FACT
    evidence:
      - "Justfile:133"
      - "Justfile:134"
      - "desktop/package.json"
  - statement: "desktop/package.json's `build` script is `tsc && vite build`, so `just desktop-build` fails on a TypeScript type error even though `just desktop-check` does not check types; type-checking is therefore gated through the build step, not through the lint step."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
  - statement: "A separate `desktop-typecheck` recipe (`pnpm typecheck`, i.e. `tsc --noEmit`) exists and is wired into the pre-push hook's `desktop-typecheck` lane, but is not a member of either the `check` or `ci` Justfile recipes."
    entry_class: FACT
    evidence:
      - "Justfile:145"
      - "Justfile:146"
      - "lefthook.yml"
  - statement: "`file-size-check` (Justfile line 106) runs `node --test scripts/check-file-sizes-core.test.mjs` plus the desktop, web, and mobile `check-file-sizes.mjs` scripts, and its own comment states the ratchet inspects only files changed from the merge base so it can run unconditionally without duplicating path filters."
    entry_class: FACT
    evidence:
      - "Justfile:106"
      - "Justfile:107"
      - "Justfile:108"
      - "Justfile:109"
      - "Justfile:110"
  - statement: "`Justfile`'s `hooks` recipe (line 54) installs lefthook by setting `core.hooksPath` to the absolute `.git`-common-dir hooks path and running `lefthook install --force`, using the Hermit-pinned `bin/lefthook` regardless of PATH."
    entry_class: FACT
    evidence:
      - "Justfile:54"
  - statement: "`lefthook.yml`'s `pre-commit` block runs `rust-fmt`, `desktop-tauri-fmt`, `desktop-fix`, `web-fix`, and `mobile-fmt` in parallel, each scoped by glob to its own subtree and each with `stage_fixed: true`, so a pre-commit failure on these lanes means an unfixable issue rather than a formatting diff."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "`lefthook.yml`'s `commit-msg` block appends a `Signed-off-by` trailer via `git interpret-trailers --if-exists doNothing`, so a local commit always carries a trailer once hooks are installed, independent of whether the author passed `-s`."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "`lefthook.yml`'s `pre-push` block runs `file-size-check` unconditionally, plus path-scoped lanes for `rust-tests` (`just test-unit`), `desktop-check`, `desktop-typecheck`, `desktop-test`, `desktop-tauri-checks` (`just desktop-tauri-clippy && just desktop-tauri-test`), and `mobile-checks` (`just mobile-check && just mobile-test`), each gated on `git diff --name-only origin/main...HEAD` matching its glob."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "CONTRIBUTING.md states plainly: 'Every commit needs a Developer Certificate of Origin (DCO) sign-off. The `-s` flag appends a `Signed-off-by` trailer that certifies you wrote the change and can contribute it under the project license. The DCO Check will block your PR without it.'"
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md:56"
  - statement: "Neither the legacy branch-protection endpoint nor the rulesets endpoint returns any configuration for the `launchpad` branch of `launchpad-26/buzz`, and no check named 'DCO' (or containing 'DCO') appears among the check-runs on three recent merged PRs (#1941, #1970, #1978) in this fork — so, as configured today, no CI check including the documented 'DCO Check' is wired as a required status check that blocks a PR's merge button on this fork's `launchpad` branch."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> 404 Not Found, run 2026-09-01"
      - "gh_api('repos/launchpad-26/buzz/rulesets') -> [], run 2026-09-01"
      - "gh_api('repos/launchpad-26/buzz/rules/branches/launchpad') -> [], run 2026-09-01"
      - "gh_pr_checks(1941, 1970, 1978, repo='launchpad-26/buzz') -> no check named or containing 'DCO' in any of the three check-run lists, run 2026-09-01"
  - statement: "ADR-0020 records the identical finding at an earlier revision: `required_status_checks` on `launchpad` returns 404 (not configured), so upstream's own 'PRs that fail `just ci` will not be merged' is an honour system on this fork, not an enforced gate, and ADR-0019 already ruled on what may gate and deferred enforcement to the CI/CD pipeline programme rather than reopening it here."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "The direct GitHub API check performed for this node (branch protection and rulesets both empty for `launchpad`, no PR carrying a required 'DCO' check) confirms ADR-0020's enforcement-gap finding still holds at this node's recorded revision, roughly eleven days after ADR-0020's own measurement."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "gh_api('repos/launchpad-26/buzz/rulesets') -> [], run 2026-09-01"
    confidence: 0.85
  - statement: "`.github/workflows/ci.yml`'s `changes` job (which has no `if:` condition and therefore always runs) includes a 'File size policy' step running `just file-size-check` as one of its own steps, alongside unit-test contracts for the path filter and the file-size ratchet itself — so the file-size gate runs on every PR and push regardless of which paths changed, even though every other CI job is path-filtered by the `changes` job's own outputs."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:91"
      - ".github/workflows/ci.yml:92"
      - ".github/workflows/ci.yml:101"
      - ".github/workflows/ci.yml:102"
  - statement: "`.github/workflows/ci.yml`'s `rust-lint` job runs `just fmt-check`, `just desktop-tauri-fmt-check`, and `just clippy`; its `desktop-core` job runs `just desktop-check`, `just desktop-test`, `just desktop-build`, `just desktop-tauri-clippy`, `just desktop-tauri-check`, and `just desktop-tauri-test`; its `web` job runs `just web-check` and `just web-build`; its `mobile` job runs `dart format --set-exit-if-changed`, `flutter analyze`, `flutter test`, and an Android debug APK build — each job path-filtered by the `changes` job's outputs, so a PR touching only one surface does not run every job."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "desktop/playwright.config.ts sets `retries: process.env.CI ? 2 : 0`, and desktop/scripts/summarize-flaky-tests.mjs's own header comment states this lets a test 'fail then pass on retry with no durable signal beyond a one-line \"N flaky\" in the console log,' which hid a real membership race (issue #1798) for months; the script appends any Playwright spec whose `status === \"flaky\"` to the job's GitHub Actions summary so a retried failure stays visible even when the shard ultimately goes green."
    entry_class: FACT
    evidence:
      - "desktop/playwright.config.ts:6"
      - "desktop/scripts/summarize-flaky-tests.mjs"
  - statement: "ADR-0020 states as a bad consequence that 'quarantine becomes necessary the moment checks are required' because upstream gates nothing while this fork inherits 146 Playwright specs and 19 relay E2E suites, and that with no required check today a flaky test cannot yet block a merge — so no formal quarantine (skip-and-track) mechanism exists yet, only the flaky-test summarizer's visibility step, which surfaces flakiness after the fact rather than removing it from the merge path."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "At this node's recorded revision, `origin/launchpad`'s corpus tree has no `launchpad/docs/corpus/verification/` subtree at all, so no `verification-strategy-test-levels` or `verification-strategy-coverage-model` node (or any other verification-surface node) exists yet as a valid `relationships[].target`."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no path under launchpad/docs/corpus/verification/, checked 2026-09-01 against commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "Issue #1389's Definition of Done requires this node to name known non-coverage and flakiness/quarantine policy 'where applicable'; per the two entries above, this fork has a flakiness-visibility mechanism (the summarizer) but no quarantine policy, which this node states as an honest gap rather than inventing a policy that does not exist."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1389 definition of done"
---

# Buzz (launchpad-26 fork) — quality model

## Scope

This node names, for the whole `launchpad-26/buzz` repository, **the dimensions of
code quality this repository actually gates a change on** — formatting, lint,
type-checking, automated tests, build success, DCO sign-off, and the file-size
ratchet — as distinct surfaces from *which test levels exist* and *how much of the
product those tests cover*. Those two narrower questions belong to
`verification-strategy-test-levels` and `verification-strategy-coverage-model`
respectively (see *Relationships* — neither exists as a corpus node yet). This
node's strategy applies to that scope only: the mechanical, tool-enforced quality
gates a change passes through from local edit to CI, not the testing methodology's
own internal structure (unit/integration/E2E) and not product-behavior coverage.

This node adapts the `test-strategy` template's shape (a levels table, per-level
infrastructure and command, honest enforcement status) to a broader unit than one
test level: **a quality dimension**, of which "run the test suite" is only one of
seven. The template's own worked skeleton is a levels table with one row per test
level; this node's table has one row per quality dimension for the same reason the
template's boundary section gives — the two questions ("what tiers exist within
testing" and "what dimensions gate a change at all") are related but not the same,
and this node is scoped to the second.

## Dimensions

| Dimension | Purpose | Infrastructure | Command | Local gating |
|---|---|---|---|---|
| Formatting (Rust) | Consistent style, zero bikeshedding in review | None | `just fmt-check` (`cargo fmt --all -- --check`) | Pre-commit auto-fixes and re-stages (`stage_fixed`); nothing left to block locally |
| Formatting (Tauri Rust) | Same, for the `desktop/src-tauri` crate | None | `just desktop-tauri-fmt-check` | Pre-commit auto-fixes and re-stages |
| Formatting (desktop/web/mobile) | Consistent style in TS and Dart | None | `pnpm exec biome check --write .` (desktop/web `*-fix`), `dart format` (mobile `mobile-fmt`) | Pre-commit auto-fixes and re-stages |
| Lint (Rust) | Catch bug-shaped patterns before review | None | `just clippy` (`cargo clippy --workspace --all-targets -- -D warnings`) | Pre-push `desktop-tauri-checks` lane (Rust-touching paths only); no plain-crate pre-push lane runs bare `clippy` outside the Tauri-scoped one |
| Lint (desktop) | Biome lint plus two custom guards (px-text literal ban, pubkey-truncation) | None | `just desktop-check` (`pnpm check`) | Pre-push `desktop-check` lane, path-scoped to `desktop/**` |
| Lint (web/mobile) | Biome (web), `flutter analyze` (mobile) | None | `just web-check`, `just mobile-check` | Pre-push `mobile-checks` lane for mobile; no path-scoped pre-push lane exists for `web-check` in `lefthook.yml` |
| Type-checking (desktop) | Catch TS type errors | None | `just desktop-typecheck` (`tsc --noEmit`); also gated indirectly because `desktop-build` runs `tsc && vite build` | Pre-push `desktop-typecheck` lane, path-scoped to `desktop/**` |
| Tests — unit (Rust) | Fast, infrastructure-free correctness checks | None | `just test-unit` | Pre-push `rust-tests` lane, path-scoped to Rust-touching paths |
| Tests — desktop unit | TS helper unit tests | None | `just desktop-test` (`node --test`) | Pre-push `desktop-test` lane, path-scoped to `desktop/**` |
| Tests — Tauri | Tauri Rust crate tests | None | `just desktop-tauri-test` | Pre-push `desktop-tauri-checks` lane |
| Tests — mobile | Flutter widget/unit tests | None | `just mobile-test` (`flutter test`) | Pre-push `mobile-checks` lane |
| Build (desktop) | Frontend compiles and type-checks cleanly | None | `just desktop-build` (`tsc && vite build`) | Not a pre-push lane; CI-only per root CLAUDE.md |
| Build (web) | Web client compiles | None | `just web-build` | Not a pre-push lane; CI-only |
| File-size ratchet | Cap file growth; force splitting large files | None (pure diff against merge base) | `just file-size-check` | Pre-push, unconditional (not path-filtered) |
| DCO sign-off | Every commit legally attributable | None | `git commit -s`; `commit-msg` hook auto-appends `Signed-off-by` | `commit-msg` hook runs on every local commit and merge (not on `rebase`/`cherry-pick` without `--signoff`) |

## Current enforcement

**Honestly: no dimension in this table is a required GitHub status check on the
`launchpad` branch today.** A direct check of both the branch-protection and
rulesets APIs for `launchpad-26/buzz` returned nothing configured (empty rulesets,
404 legacy protection), and no PR's check-run list carried a check named or
containing "DCO" across three recently merged PRs sampled for this node. This
matches, and independently reconfirms roughly eleven days later, ADR-0020's own
finding that `required_status_checks` on `launchpad` returns 404 — the "PRs that
fail `just ci` will not be merged" language in this repo's contributor
documentation (including the documented "DCO Check will block your PR") describes
an **honour system enforced by CI running and being visible**, not a merge-button
gate. Nothing here should be read as "these checks don't matter" — CI runs every
dimension above on every relevant push and PR, and a red run is a strong social
signal — but a reviewer citing this node must not claim a dimension "gates merges"
in the schema sense, because none currently does.

**What actually happens locally, and it is real enforcement even without a
required check:**

- **Pre-commit** (formatting dimensions) auto-fixes and re-stages; an unfixable
  lint issue blocks the commit outright, and this is a hard local block with no
  bypass short of `--no-verify` (which this repository's own AGENTS.md instructs
  agents never to use).
- **Pre-push** (lint, type-checking, tests, file-size) blocks the push locally,
  scoped by `git diff --name-only origin/main...HEAD` against each lane's glob —
  the file-size lane alone is unconditional. A non-`HEAD` push (an explicit
  refspec, `--all`) only gets a non-fatal warning from the `push-head-scope` lane
  and relies on CI for path-scoped coverage.
- **CI** re-runs every dimension (plus dimensions with no local lane at all —
  builds, `web-check`) on every PR and push to `main`/`release`, path-filtered by
  the `changes` job's `dorny/paths-filter` outputs, except the file-size policy
  step, which runs unconditionally inside the always-on `changes` job itself.

So the honest layering is: **local hooks are the actual gate** for whichever
dimensions have a matching lane and whichever paths a branch touches; **CI is
comprehensive but not merge-blocking** for any dimension.

## Deliberately out of scope

- **Security and dependency-policy checks** (`cargo-deny`, the "Dead Token
  Reference Guard", `Server Cross-Compile`) are real CI jobs but are not code-
  quality dimensions in the sense this node covers — they check licensing/
  dependency posture and platform buildability, not formatting, correctness, or
  size. A security-focused corpus node, if one is written, owns these.
- **Which test levels exist and what each needs to run** (unit/integration/relay
  E2E/desktop E2E, per ADR-0020) is `verification-strategy-test-levels`'s subject,
  not this node's. This node names *that* `just test-unit`, `just desktop-test`,
  `just desktop-tauri-test`, and `just mobile-test` exist as quality-gate
  dimensions; it does not restate their infrastructure needs or gating semantics
  level by level.
- **How much of the product's behavior those tests actually cover** is
  `verification-strategy-coverage-model`'s subject. This node does not measure or
  claim any coverage percentage.
- **Traceability from a product claim or specification to the specific test that
  verifies it** is a test-contract-level concern (`templates/test-contract.md`),
  narrower than any dimension in this table. This node's dimensions are pass/fail
  gates on the codebase as a whole, not obligation-by-obligation traceability.
- **Environments and fixtures for the test dimensions' own content** (what data a
  given unit or integration test seeds) are owned by the tests themselves and by
  `verification-strategy-test-levels` once it exists; this node names only the
  infrastructure footprint of *running* a dimension's command (none for every
  dimension in this table — none of the seven quality dimensions require
  Postgres/Redis/a live relay, unlike the integration and E2E test levels ADR-0020
  describes), not the data those commands exercise.
- **A quarantine (skip-and-track) mechanism for flaky tests does not exist.** The
  desktop E2E suite retries twice in CI and a summarizer surfaces any test that
  passed only on retry to the job summary, but nothing removes a chronically flaky
  test from the merge path — ADR-0020 names this as a consequence that becomes
  necessary "the moment checks are required," which, per *Current enforcement*
  above, has not happened yet. This is a known gap, not a policy this node
  invents.

## Relationships

**Checked, not assumed absent.** At this node's recorded revision,
`origin/launchpad`'s corpus tree carries no `launchpad/docs/corpus/verification/`
subtree at all — `verification-strategy-test-levels` and
`verification-strategy-coverage-model` do not exist as corpus nodes yet, so
neither is a valid `relationships[].target` today. This node declares no
relationships for that reason.

**The two edges this node expects to declare once their targets exist:**
`references` toward `verification-strategy-test-levels` (this node's "Tests — *"
rows name that dimension exists as a quality gate; that node would own the tiered
structure within it) and `references` toward
`verification-strategy-coverage-model` (this node makes no coverage claim; that
node would own coverage measurement). Both are the first sibling nodes to revisit
this section against, per `AGENTS.md`'s standing instruction to check the merge
target rather than assume "nothing to point at" stays true.

## Scope and omissions

**This node covers** the seven mechanical quality dimensions this repository runs
on a change (Rust/Tauri/desktop/web/mobile formatting, Rust/desktop/web/mobile
lint, desktop type-checking, the four test-running dimensions, the two build
dimensions, the file-size ratchet, and DCO sign-off), the exact command and local
hook coverage for each, and — stated honestly — that none of them is a required
GitHub status check on `launchpad` today, cross-checked directly against the
GitHub API rather than assumed from ADR-0020's earlier finding alone.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Which test levels exist, their infrastructure needs, and their own gating status | `verification-strategy-test-levels` (does not exist yet) |
| How much of the product's behavior is covered by tests | `verification-strategy-coverage-model` (does not exist yet) |
| One testable obligation traced to the specific test that verifies it | `templates/test-contract.md`-shaped nodes, none of which exist yet for Buzz |
| Why this fork's testing methodology looks the way it does, and the enforcement gap this node reconfirms | `launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md` |
| What may gate a merge at all, as a matter of policy | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md`, deferred further by ADR-0020 to the CI/CD pipeline programme |
| Security and dependency-policy CI checks (`cargo-deny`, dead-token guard, cross-compile) | No corpus node yet |
| Creating, updating, and retiring any corpus node, including this one | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether `web-check` has any pre-push local lane at all was read from
  `lefthook.yml`'s literal contents, not exercised by actually running a push
  against a web-only change.** The file names no `web-check` pre-push command;
  that reading was not behaviorally confirmed.
- **Whether the "DCO Check" name in CONTRIBUTING.md refers to a GitHub App that
  is simply not installed on this fork, versus a check that exists but was not
  triggered by any of the three sampled PRs, was not distinguished.** Either
  explanation is consistent with the evidence gathered; this node states only
  that no such check was observed and that no ruleset or branch protection
  requires one, not which of those two explanations is true.
- **Whether the `check`/`ci` Justfile recipes or `lefthook.yml`'s lanes have
  changed between this node's recorded revision and whenever it is read** was not
  re-verified beyond the recorded commit; per `AGENTS.md`, a claim here is a
  snapshot, not a timeless fact.
