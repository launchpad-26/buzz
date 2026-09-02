---
id: development-change-impact
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "CI's first job is `changes` (display name 'Detect Changed Paths'), which runs dorny/paths-filter and exposes exactly five boolean outputs -- rust, desktop, desktop-rust, web, mobile -- that every path-gated downstream job reads."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The `rust` filter matches crates/**, migrations/**, schema/**, Cargo.toml, Cargo.lock, rust-toolchain.toml, deny.toml, .github/workflows/ci.yml, scripts/run-tests.sh, scripts/model-capabilities.json, scripts/normative-corpus.json and justfile; `desktop` matches scripts/model-capabilities.json, scripts/normative-corpus.json, desktop/** and pnpm-lock.yaml; `desktop-rust` matches desktop/src-tauri/** alone; `web` matches web/** and pnpm-lock.yaml; `mobile` matches mobile/**, seven named scripts/ files, .github/workflows/mobile-release-candidate.yml and .github/workflows/ci.yml."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Every path-gated CI job guards on `github.event_name == 'push' || <one or more changes outputs>`: Rust Lint on rust or desktop-rust; Unit Tests, Backend Integration, Relay E2E, Security and Server Cross-Compile on rust alone; Desktop Core, Desktop Smoke E2E, Desktop, Desktop E2E Relay, Desktop E2E Integration (and its shards) and Desktop Build (macOS) on desktop or desktop-rust or rust; Web on web; Mobile on mobile; Windows Rust on rust or desktop-rust."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "Two CI jobs are not gated the same way as the rest: `dead-token-guard` ('Dead Token Reference Guard') declares no `needs` and no `if`, so it runs on every event CI fires on; and `mobile-swift` guards on `needs.changes.outputs.mobile == 'true'` only, omitting the `github.event_name == 'push'` escape hatch every other path-gated job carries."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "CI's `on:` block is `push` restricted to branches [main, release] plus an unrestricted `pull_request`, so on this fork -- whose integration branch is `launchpad` -- the `github.event_name == 'push'` disjunct in every job condition is never satisfied by a push to `launchpad`, and CI is reached through pull requests."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "launchpad/AGENTS.md"
  - statement: "Before any filter output is consumed, the `changes` job itself runs eleven unconditional contract steps in-line -- release workflow source contract, relay image eligibility contract, desktop release candidate contract, OSS desktop promotion contract (two scripts), mobile release contract (two scripts), mobile worktree identity contract, file size ratchet unit tests, changed-paths filter contract, Codex security review contract, Rust cache contract (two scripts) -- and finally `just file-size-check` as the 'File size policy' step."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "lefthook's pre-commit stage runs five parallel auto-fix lanes, each scoped by a glob and each with `stage_fixed: true`: rust-fmt on crates/** and examples/countdown-bot/**, desktop-tauri-fmt on desktop/src-tauri/**, desktop-fix on desktop/** excluding desktop/src-tauri/**, web-fix on web/**, and mobile-fmt on mobile/**."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "lefthook's commit-msg stage carries a single unglobbed `signoff` lane that appends the DCO Signed-off-by trailer with `git interpret-trailers --if-exists doNothing`, and lefthook.yml records that Git runs commit-msg only for `git commit` and `git merge`, so `git rebase --signoff` and `git cherry-pick -s` need their own flag."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "lefthook's pre-push stage runs three unfiltered lanes -- branch-skew (launchpad/scripts/check-branch-skew.sh), push-head-scope (scripts/check-push-head-scope.sh, warn-only, reads pushed refs from stdin) and file-size-check (just file-size-check) -- alongside five globbed lanes: rust-tests, desktop-check, desktop-typecheck, desktop-test, desktop-tauri-checks and mobile-checks."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "Each globbed pre-push lane sets `files: git diff --name-only origin/main...HEAD`, so its file set is the branch's merge-base diff rather than lefthook's stock `git diff HEAD @{push}` discovery; lefthook.yml states that without it a rebase or a merge from main would fire mobile/desktop/rust lanes on unrelated pushes and a brand-new branch would fall back to a stale remote tip."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "lefthook.yml documents five deliberate deviations from CI's filter groups: the .github/workflows/ci.yml path is omitted from the local rust and mobile globs; desktop-check/desktop-typecheck/desktop-test do not trigger on rust changes although CI's Desktop Core job does; file-size-check is deliberately unfiltered because its own merge-base diff is the path filter; deletion-only surface changes do not trigger local hooks because lefthook 2.1.x drops deleted paths from push-file discovery, with CI's paths-filter catching deletions; and commit-msg has no glob because it rewrites the message, not files."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "`just file-size-check` runs the ratchet's own unit tests (node --test scripts/check-file-sizes-core.test.mjs) and then three per-surface wrappers -- desktop/scripts/check-file-sizes.mjs, web/scripts/check-file-sizes.mjs and mobile/scripts/check-file-sizes.mjs -- and the Justfile records that the ratchet inspects only files changed from the merge base, which is why it runs unconditionally."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "All three ratchet wrappers set MAX_LINES to 1000. Desktop governs src-tauri/src and src-tauri/crates (.rs) plus src/app, src/features, src/shared/api, src/shared/context, src/shared/lib, src/shared/ui (.ts/.tsx) and src/shared/styles (.css); Web governs src/app, src/features and src/shared/api (.ts/.tsx); Mobile governs lib (.dart). A path outside every listed root is ungoverned and the check still exits 0."
    entry_class: FACT
    evidence:
      - "desktop/scripts/check-file-sizes.mjs"
      - "web/scripts/check-file-sizes.mjs"
      - "mobile/scripts/check-file-sizes.mjs"
  - statement: "resolveBaseRef picks the ratchet's comparison point in a fixed precedence: CHECK_FILE_SIZES_BASE when set, else the literal HEAD^1 when GITHUB_ACTIONS is 'true', else `git merge-base origin/main HEAD` (collapsing to HEAD when the merge base is HEAD), and it throws rather than passing when origin/main cannot be resolved."
    entry_class: FACT
    evidence:
      - "scripts/check-file-sizes-core.mjs"
  - statement: "The ratchet is differential, not absolute: allowedLineCount returns maxLines when the base file is absent or already within the limit and otherwise returns the base line count, so an already-oversized file is pinned at its current size; deletions (status D) are skipped, and a rename's base content is read from the old path."
    entry_class: FACT
    evidence:
      - "scripts/check-file-sizes-core.mjs"
  - statement: "scripts/test-ci-changed-paths-filter.sh parses ci.yml's `filters:` block and fails any filter that mixes a negated pattern with positive patterns, because dorny/paths-filter evaluates each pattern as an independent OR clause -- so a standalone '!desktop/src-tauri/**' would make the whole filter true for nearly any change; the script names launchpad-26/buzz#181 as the bug it guards, and states the fix is to split the excluded path into its own filter and OR the outputs at the job `if:` condition."
    entry_class: FACT
    evidence:
      - "scripts/test-ci-changed-paths-filter.sh"
  - statement: "The tracked file at the repository root is `Justfile` with a capital J, CI's `rust` filter lists the pattern as lowercase `justfile`, and lefthook's rust-tests lane lists it as `Justfile`."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
      - "lefthook.yml"
      - "git_ls_tree(ref='origin/launchpad') -> Justfile (capital J; no lowercase 'justfile' path exists)"
  - statement: "A change touching only the root Justfile therefore fires the local pre-push rust-tests lane but does not set CI's `rust` filter output, so the CI jobs that entry is meant to gate do not run for it."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - "lefthook.yml"
      - "picomatch_isMatch('Justfile', 'justfile') -> false (picomatch 2.3.2, run outside this repository)"
    confidence: 0.85
  - statement: "Issue #442 reports the lowercase 'justfile' pattern as a CI defect, states that dorny/paths-filter matches case-sensitively so the entry has never fired, and names the desktop E2E shards, the macOS build and the Windows Rust job as the jobs it fails to gate; the issue is open and unfixed at the recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#442"
  - statement: "The cohort's own workflows are individually path-gated: launchpad-agents-tests on launchpad/agents/**; launchpad-corpus-schema-tests on launchpad/docs/corpus/schema/**; launchpad-corpus-validate on launchpad/project-intelligence/corpus/**, launchpad/project-intelligence/requirements.txt and launchpad/docs/corpus/**; launchpad-rqa-tests on launchpad/skills/review-queue-automation/**; launchpad-review-agent-controls on launchpad/review-agent/** and, deliberately, on launchpad-review-agent-publish.yml as well -- each also listing its own workflow file, and each mirroring the same paths on `push` to branch launchpad."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-agents-tests.yml"
      - ".github/workflows/launchpad-corpus-schema-tests.yml"
      - ".github/workflows/launchpad-corpus-validate.yml"
      - ".github/workflows/launchpad-rqa-tests.yml"
      - ".github/workflows/launchpad-review-agent-controls.yml"
  - statement: "Three cohort checks carry no paths filter at all and therefore evaluate every pull request regardless of what changed: launchpad-adr-check (pull_request types opened/reopened/synchronize/ready_for_review), launchpad-pr-check (pull_request types including edited/labeled/unlabeled) and launchpad-security-audit (a bare `pull_request: {}` alongside a nightly schedule and workflow_dispatch)."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-adr-check.yml"
      - ".github/workflows/launchpad-pr-check.yml"
      - ".github/workflows/launchpad-security-audit.yml"
  - statement: "Several upstream workflows restrict their pull_request trigger to `branches: [main]` -- codex-security-review.yml (pull_request_target), desktop-release-candidate.yml and auto-tag-on-release-pr-merge.yml -- so they do not evaluate a pull request whose base is this fork's `launchpad` branch."
    entry_class: FACT
    evidence:
      - ".github/workflows/codex-security-review.yml"
      - ".github/workflows/desktop-release-candidate.yml"
      - ".github/workflows/auto-tag-on-release-pr-merge.yml"
  - statement: "docker.yml is the fork-adjusted image workflow: its `push` trigger is branch `launchpad` plus relay-v* tags, and its pull_request paths list Dockerfile, Dockerfile.push-gateway, .dockerignore, its own workflow file, deploy/charts/buzz/Chart.yaml, three scripts/ helpers, Cargo.toml, Cargo.lock, rust-toolchain.toml, crates/**, web/**, package.json, pnpm-lock.yaml, pnpm-workspace.yaml and patches/**."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "CONTRIBUTING.md's 'How to Add a New Event Kind' enumerates nine companion sites for one new kind: the constant and ALL_KINDS collision check in buzz-core/src/kind.rs, an optional payload type in buzz-core/src, required_scope_for_kind() in crates/buzz-relay/src/handlers/ingest.rs, handle_side_effects() in crates/buzz-relay/src/handlers/side_effects.rs (plus crates/buzz-relay/src/api and router.rs if an HTTP bridge is needed), persistence in buzz-db/src, the search_tsv exclusion CASE in the initial schema migration for a privacy-sensitive kind, automatic audit capture, tests in buzz-core and buzz-test-client, and documentation with kind.rs as the authoritative registry."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's 'How to Add a New API Endpoint' states the preference for a signed Nostr event over a new endpoint, and when an endpoint is unavoidable names six companion sites: a handler under crates/buzz-relay/src/api, route registration in crates/buzz-relay/src/router.rs, buzz-db queries only when the existing event query paths cannot express it, the api_error()/internal_error()/not_found() helpers in buzz-relay/src/api/mod.rs, tests in crates/buzz-test-client/tests, and documentation of any public endpoint in ARCHITECTURE.md."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "AGENTS.md states four cross-file coupling contracts that no path filter expresses: reply inserts must update the materialized reply_count and descendant_count on thread root events; every new community-scoped module-level singleton needs a reset wired into resetCommunityState() in desktop/src/features/communities/useCommunityInit.ts; mobile's lib/shared/relay/nostr_models.dart event kinds must stay in sync with desktop/src/shared/constants/kinds.ts; and every pgschema apply caller must also run scripts/reconcile-schema-after-pgschema.sql because pgschema omits seed DML and some storage parameters."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "No script, workflow or Justfile recipe in this repository references both desktop/src/shared/constants/kinds.ts and mobile/lib/shared/relay/nostr_models.dart, so the kind-sync contract AGENTS.md states is held by review rather than by a check."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "lefthook.yml"
      - ".github/workflows/ci.yml"
      - "grep_repository(pattern='nostr_models|kinds.ts', paths='scripts/, .github/, Justfile') -> no matching file"
  - statement: "The desktop lint lane is a chain rather than a single tool: desktop/package.json's `check` script runs `biome check . && pnpm check:px-text && pnpm check:pubkey-truncation`, `just desktop-check` invokes that script, and CI's Desktop Core job runs `just desktop-check` as its 'Desktop lint and format' step -- so the arbitrary-text-size guard fires from both the pre-push desktop-check lane and CI."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "Justfile"
      - ".github/workflows/ci.yml"
  - statement: "`just check` aggregates fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check and file-size-check, and `just ci` is `check` plus test-unit, desktop-test, desktop-build, desktop-tauri-check, desktop-tauri-test, web-build and mobile-test -- neither applies any path filter."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "launchpad/AGENTS.md section 3 makes editing an upstream file a fork-level impact rather than a local one: cohort files live under launchpad/, upstream files must never be moved or renamed because the fork merges from an approximately 3,800-file upstream regularly, the list of permitted divergences is closed and each entry names its own ADR, a permitted divergence should take the form of a fork-owned override rather than an in-place edit (ADR-0043), and any new workflow must be named launchpad-*.yml so it never collides with upstream's."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "At the recorded revision origin/launchpad's corpus tree contains four nodes under development/ -- build.md, debugging.md, hermit.md and prerequisites.md -- and no node under a verification/, operations/ or release/ directory, so no merged node covers CI gating or hook lanes as its own subject."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> development/build.md, development/debugging.md, development/hermit.md, development/prerequisites.md and no verification/, operations/ or release/ directory"
  - statement: "At the recorded revision .github/workflows/ contains thirty .yml files, ten of them named launchpad-*; the two cohort workflows this node's trigger table omits are launchpad-issue-check.yml, which fires on `issues` events rather than on a change to any path, and launchpad-review-agent-publish.yml, which fires on `pull_request_target` with no paths filter."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-issue-check.yml"
      - ".github/workflows/launchpad-review-agent-publish.yml"
      - "list_directory('.github/workflows/*.yml') -> 30 files, 10 matching launchpad-*"
  - statement: "Issue #847's definition of done requires that this node be structured for lookup rather than narrative teaching, contain only facts supported by current source while labelling generated versus authored values, define its scope and omissions, and link authoritative source/schema/config."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#847 definition of done"
  - statement: "Sibling tasks under Feature #619 own the per-domain change procedures this node deliberately excludes: #848 configuration-changes, #855 database-changes, #858 event-kind-changes, #861 protocol-changes, #862 public-api-changes, and #846 build."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#619 child issue list"
---

# Change impact: which gates a changed path triggers

A lookup table from **a path you changed** to **the automated gates that will
evaluate it** and **the companion files that must change with it**. It catalogues
the repository's path-to-gate wiring as it stands at the recorded revision; it
does not walk you through making any particular change. For the procedure for a
specific kind of change, see the sibling nodes named under *Boundary*.

Read the three tables in order: *CI path-filter groups* says which filter your
path sets, *CI jobs* says what that filter switches on, and *Local hook lanes*
says what runs before the push that would trigger any of it.

## Authoritative sources

This node duplicates none of them. If it and any of these disagree, **they win**.

| For | Read |
|---|---|
| CI's filter groups, job conditions and unconditional contract steps | `.github/workflows/ci.yml` |
| Local pre-commit / commit-msg / pre-push lanes and their globs | `lefthook.yml` |
| The differential file-size ratchet's base resolution and rules | `scripts/check-file-sizes-core.mjs` |
| Which paths each surface's ratchet governs, and the line ceiling | `desktop/scripts/check-file-sizes.mjs`, `web/scripts/check-file-sizes.mjs`, `mobile/scripts/check-file-sizes.mjs` |
| Aggregate local gates (`just check`, `just ci`, `just file-size-check`) | `Justfile` |
| The guard on the filter configuration itself | `scripts/test-ci-changed-paths-filter.sh` |
| Companion sites for a new event kind or HTTP endpoint | `CONTRIBUTING.md` |
| Cross-file coupling contracts no filter expresses | `AGENTS.md` |
| The fork's upstream-file boundary and workflow naming rule | `launchpad/AGENTS.md` §3 |

## CI path-filter groups

CI's first job, `changes` ("Detect Changed Paths"), runs `dorny/paths-filter` and
publishes five boolean outputs. Patterns are listed here in the order they are
authored in `ci.yml`.

| Output | Patterns that set it |
|---|---|
| `rust` | `crates/**`, `migrations/**`, `schema/**`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `deny.toml`, `.github/workflows/ci.yml`, `scripts/run-tests.sh`, `scripts/model-capabilities.json`, `scripts/normative-corpus.json`, `justfile` (see *Known asymmetries*) |
| `desktop` | `scripts/model-capabilities.json`, `scripts/normative-corpus.json`, `desktop/**`, `pnpm-lock.yaml` |
| `desktop-rust` | `desktop/src-tauri/**` |
| `web` | `web/**`, `pnpm-lock.yaml` |
| `mobile` | `mobile/**`, `scripts/mobile-release.sh`, `scripts/mobile-worktree-overrides.sh`, `scripts/mobile-worktree-clean.sh`, `scripts/publish-mobile-release-candidate.sh`, `scripts/release-rulesets.sh`, `scripts/test-mobile-release-contract.sh`, `scripts/test-mobile-release-candidate-publisher.sh`, `scripts/test-mobile-worktree-overrides.sh`, `.github/workflows/mobile-release-candidate.yml`, `.github/workflows/ci.yml` |

`desktop-rust` exists as its own filter rather than as a negated pattern inside
`desktop` on purpose — see *Guards on the wiring itself*.

## CI jobs and what switches them on

Every condition below is authored as `github.event_name == 'push' || <outputs>`,
except where the third column says otherwise. On this fork the `push` disjunct is
inert for the integration branch: `ci.yml`'s `push` trigger is restricted to
`branches: [main, release]`, so a push to `launchpad` does not start CI at all and
every job is reached through `pull_request`, path-gated.

| Job (display name) | Runs when | Note |
|---|---|---|
| Detect Changed Paths | always | Also runs eleven unconditional contract steps — see below |
| Rust Lint | `rust` or `desktop-rust` | |
| Unit Tests | `rust` | |
| Desktop Core | `desktop` or `desktop-rust` or `rust` | |
| Desktop Smoke E2E (sharded) | `desktop` or `desktop-rust` or `rust` | |
| Desktop | `desktop` or `desktop-rust` or `rust` | `always()`-wrapped aggregator over Desktop Core + Smoke E2E |
| Desktop E2E Relay | `desktop` or `desktop-rust` or `rust` | |
| Desktop E2E Integration (+ shards) | `desktop` or `desktop-rust` or `rust` | Aggregator is `always()`-wrapped |
| Backend Integration (relay e2e) | `rust` | |
| Relay E2E | `rust` | |
| Web | `web` | |
| Mobile | `mobile` | |
| Mobile Swift | `mobile` | **No `push` disjunct** — the only path-gated job without one |
| Security | `rust` | |
| Dead Token Reference Guard | always | **No `needs`, no `if`** — greps `desktop/src/`, `desktop/tests/`, `mobile/test/`, `mobile/lib/` and the env template for dead token patterns |
| Server Cross-Compile | `rust` | |
| Windows Rust | `rust` or `desktop-rust` | |
| Desktop Build (macOS) | `desktop` or `desktop-rust` or `rust` | |

### Unconditional steps inside the `changes` job

These run before any filter output is consumed, so they evaluate every pull
request whatever it touched: the release workflow source contract, relay image
eligibility contract, desktop release candidate contract, OSS desktop promotion
contract (two scripts), mobile release contract (two scripts), mobile worktree
identity contract, the file-size ratchet's own unit tests, the changed-paths
filter contract, the Codex security review contract, the Rust cache contract (two
scripts), and finally `just file-size-check` as the "File size policy" step.

## Local hook lanes

`lefthook.yml` mirrors CI's groups deliberately and deviates from them
deliberately; both are recorded in its header comment.

### pre-commit — parallel, auto-fixing, `stage_fixed: true`

| Lane | Glob | Runs |
|---|---|---|
| `rust-fmt` | `crates/**`, `examples/countdown-bot/**` | `just fmt` |
| `desktop-tauri-fmt` | `desktop/src-tauri/**` | `just desktop-tauri-fmt` |
| `desktop-fix` | `desktop/**` minus `desktop/src-tauri/**` | `just desktop-fix` |
| `web-fix` | `web/**` | `just web-fix` |
| `mobile-fmt` | `mobile/**` | `just mobile-fmt` |

### commit-msg

One ungated `signoff` lane appends the DCO `Signed-off-by` trailer with
`git interpret-trailers --if-exists doNothing`. Git runs `commit-msg` only for
`git commit` and `git merge`; `git rebase --signoff` and `git cherry-pick -s`
carry their own flag.

### pre-push — parallel

| Lane | Scope | Runs |
|---|---|---|
| `branch-skew` | unfiltered | `./launchpad/scripts/check-branch-skew.sh` |
| `push-head-scope` | unfiltered, warn-only, reads pushed refs from stdin | `./scripts/check-push-head-scope.sh` |
| `file-size-check` | unfiltered by design | `just file-size-check` |
| `rust-tests` | `crates/**`, `migrations/**`, `schema/**`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `deny.toml`, `scripts/run-tests.sh`, `Justfile` | `just test-unit` |
| `desktop-check` | `desktop/**`, `pnpm-lock.yaml`, minus `desktop/src-tauri/**` | `just desktop-check` |
| `desktop-typecheck` | same as above | `just desktop-typecheck` |
| `desktop-test` | same as above | `just desktop-test` |
| `desktop-tauri-checks` | `desktop/src-tauri/**` plus the whole `rust-tests` glob list | `just desktop-tauri-clippy && just desktop-tauri-test` |
| `mobile-checks` | `mobile/**` | `just mobile-check && just mobile-test` |

Every globbed lane above sets `files: git diff --name-only origin/main...HEAD`, so
its file set is the branch's merge-base diff. Without that, lefthook's stock
`git diff HEAD @{push}` discovery would include everything the base branch moved
since the last push, firing unrelated lanes after a rebase or a merge, and would
fall back to a stale remote tip on a brand-new branch.

### Deliberate deviations from CI

Recorded in `lefthook.yml` itself, not inferred:

- `.github/workflows/ci.yml` is omitted from the local `rust` and `mobile` globs —
  a CI-workflow-only edit does not need a local test run.
- `desktop-check` / `desktop-typecheck` / `desktop-test` do not trigger on `rust`
  changes although CI's Desktop Core job does; those commands are pure TypeScript
  with no Rust dependency.
- `file-size-check` is unfiltered because its own merge-base diff *is* its path
  filter; duplicating the governed roots in the hook is the coverage drift the
  gate exists to prevent.
- Deletion-only surface changes do not trigger local hooks: lefthook 2.1.x drops
  deleted paths from push-file discovery. CI's paths-filter catches deletions.
  Accepted, not worked around.
- `commit-msg` has no glob because it rewrites the message, not files.

## The file-size ratchet

Unfiltered, and differential rather than absolute. `just file-size-check` runs the
ratchet's unit tests plus one wrapper per surface.

| Surface | Governed roots (extensions) | Ceiling |
|---|---|---|
| Desktop | `src-tauri/src`, `src-tauri/crates` (`.rs`); `src/app`, `src/features`, `src/shared/api`, `src/shared/context`, `src/shared/lib`, `src/shared/ui` (`.ts`, `.tsx`); `src/shared/styles` (`.css`) | 1000 lines |
| Web | `src/app`, `src/features`, `src/shared/api` (`.ts`, `.tsx`) | 1000 lines |
| Mobile | `lib` (`.dart`) | 1000 lines |

A path outside every listed root is **ungoverned**, and the check still exits 0 —
absence of a violation is not evidence of coverage.

Base-ref resolution, in precedence order:

1. `CHECK_FILE_SIZES_BASE`, when set.
2. The literal `HEAD^1`, when `GITHUB_ACTIONS` is `"true"`.
3. `git merge-base origin/main HEAD`, collapsing to `HEAD` when the merge base is
   `HEAD`. If `origin/main` cannot be resolved, the check throws rather than
   passing.

Ratchet semantics: a file already over the ceiling is pinned at its current line
count rather than failed outright, a new file is held to the ceiling, deletions
are skipped, and a rename reads its base content from the old path.

## Companion changes no path filter expresses

These are contracts held by review, not by a gate. Each row names the source that
states it.

| When you change | You must also change | Stated in |
|---|---|---|
| A new event kind | `buzz-core/src/kind.rs` constant + `ALL_KINDS` collision check, `required_scope_for_kind()` in `crates/buzz-relay/src/handlers/ingest.rs`, `handle_side_effects()` in `crates/buzz-relay/src/handlers/side_effects.rs`, persistence in `buzz-db/src`, the `search_tsv` exclusion for a privacy-sensitive kind, tests in `buzz-core` and `buzz-test-client` | `CONTRIBUTING.md` |
| A new HTTP endpoint (only when an event will not do) | handler under `crates/buzz-relay/src/api`, route in `crates/buzz-relay/src/router.rs`, the `api_error()`/`internal_error()`/`not_found()` helpers, tests in `crates/buzz-test-client/tests`, `ARCHITECTURE.md` for any public endpoint | `CONTRIBUTING.md` |
| Code that inserts replies | the materialized `reply_count` and `descendant_count` on thread root events | `AGENTS.md` |
| A new community-scoped module-level singleton in desktop | a reset wired into `resetCommunityState()` in `desktop/src/features/communities/useCommunityInit.ts` | `AGENTS.md` |
| Event kinds on any client | keep `mobile/lib/shared/relay/nostr_models.dart` in sync with `desktop/src/shared/constants/kinds.ts` | `AGENTS.md` |
| Anything applied with `pgschema apply` | run `scripts/reconcile-schema-after-pgschema.sql`; pgschema omits seed DML and some storage parameters | `AGENTS.md` |

The kind-sync row has **no** automated backstop: no script, workflow or `Justfile`
recipe in this repository names both `kinds.ts` and `nostr_models.dart`.

Also note that `just desktop-check` is a chain, not one tool —
`desktop/package.json`'s `check` script is `biome check . && pnpm check:px-text &&
pnpm check:pubkey-truncation`, and CI's Desktop Core job runs `just desktop-check`
as its lint step. A desktop change that introduces an arbitrary text-size literal
fails locally and in CI through that chain, not through a separate job.

## Cohort workflows and the fork boundary

| Workflow | Fires on |
|---|---|
| `launchpad-agents-tests.yml` | `launchpad/agents/**` (+ its own file) |
| `launchpad-corpus-schema-tests.yml` | `launchpad/docs/corpus/schema/**` (+ its own file) |
| `launchpad-corpus-validate.yml` | `launchpad/project-intelligence/corpus/**`, `launchpad/project-intelligence/requirements.txt`, `launchpad/docs/corpus/**` (+ its own file) |
| `launchpad-rqa-tests.yml` | `launchpad/skills/review-queue-automation/**` (+ its own file) |
| `launchpad-review-agent-controls.yml` | `launchpad/review-agent/**`, `launchpad-review-agent-publish.yml` (+ its own file) |
| `launchpad-adr-check.yml` | **every** pull request |
| `launchpad-pr-check.yml` | **every** pull request, including on label and body edits |
| `launchpad-security-audit.yml` | **every** pull request, plus a nightly schedule and manual dispatch |

Each path-gated cohort workflow mirrors the same paths on `push` to branch
`launchpad`.

Three upstream workflows never evaluate a pull request based on `launchpad`,
because their trigger is restricted to `branches: [main]`:
`codex-security-review.yml`, `desktop-release-candidate.yml` and
`auto-tag-on-release-pr-merge.yml`. `docker.yml` is the fork-adjusted one — its
`push` trigger is branch `launchpad` plus `relay-v*` tags.

**Editing an upstream file has fork-level impact, not just CI impact.**
`launchpad/AGENTS.md` §3 states that cohort files live under `launchpad/`, that
upstream files are never moved or renamed because the fork merges regularly from
an approximately 3,800-file upstream, that the list of permitted divergences is
closed with each entry naming its own ADR, that a permitted divergence should take
the form of a fork-owned override rather than an in-place edit, and that any new
workflow must be named `launchpad-*.yml`.

## Guards on the wiring itself

`scripts/test-ci-changed-paths-filter.sh` runs in the `changes` job and fails any
filter that mixes a negated pattern with positive patterns. `dorny/paths-filter`
evaluates each pattern as an independent **OR** clause, so a standalone
`'!desktop/src-tauri/**'` inside a filter that also has positive patterns matches
every file outside that directory and silently makes the whole filter true for
nearly any change — the defect recorded as launchpad-26/buzz#181. The prescribed
fix is to split the excluded path into its own filter and OR the outputs at the
job's `if:` condition, which is exactly why `desktop` and `desktop-rust` are two
filters rather than one.

## Known asymmetries

- **`justfile` versus `Justfile`.** The tracked file is `Justfile`; CI's `rust`
  filter lists `justfile` in lowercase, while lefthook's `rust-tests` lane lists
  `Justfile`. The consequence — a `Justfile`-only change fires the local rust lane
  but not CI's `rust` filter — is recorded in this node's provenance ledger as an
  inference, because `dorny/paths-filter`'s pinned picomatch version was not
  executed here. Issue **#442** reports it as a CI defect and names the desktop
  E2E shards, the macOS build and the Windows Rust job as the jobs left ungated.
  It is open at the recorded revision; this node documents it and does not fix it.
- **`Mobile Swift` has no `push` disjunct** while every other path-gated job does.
- **Deletion-only changes** reach CI's filters but not the local hooks.
- **`ci.yml` triggers itself**: the path appears in both the `rust` and `mobile`
  filter lists, so editing CI runs the Rust and Mobile lanes; the local hooks
  deliberately omit it.

## Authored versus generated values

Everything in the tables above is an **authored** literal read out of a checked-in
file — the glob lists, the `if:` expressions, the lane globs, `MAX_LINES = 1000`,
the ratchet's governed roots, the workflow triggers. None of it is produced by a
generator, and this node is not a generated projection.

The values that are **generated at run time**, and therefore appear nowhere in the
repository as text, are: the five `changes` job outputs (computed per event by
`dorny/paths-filter` from the pull request's diff), each hook lane's file set
(computed by `git diff --name-only origin/main...HEAD` at push time), and the
ratchet's base ref and per-file limit (resolved by `resolveBaseRef` and
`allowedLineCount` at run time). Reading a filter's pattern list tells you what
*can* set an output; only a run tells you what did.

## Boundary

This node does not describe:

- **How to make any particular kind of change.** Configuration changes (#848),
  database changes (#855), event kind changes (#858), protocol changes (#861) and
  public API changes (#862) each own their own procedure, as does building (#846).
  This node stops at *which gates will look at it*.
- **Why the gates are shaped this way.** The rationale for the fork's upstream
  boundary lives in its ADRs; the rationale for the ratchet's differential design
  lives in its own source comments.
- **How to run the toolchain.** `development/hermit.md` covers Hermit activation
  and `development/prerequisites.md` covers version floors.
- **What any individual check asserts.** This node names the lane; the lane's own
  script or recipe defines its verdict.

## Relationships

**Declared: none** — this node's front matter carries no `relationships` key.
Checked against `origin/launchpad` at the recorded revision,
not against this worktree. The corpus's four merged `development/` nodes are
`build.md`, `debugging.md`, `hermit.md` and `prerequisites.md`; there is no merged
node under a `verification/`, `operations/` or `release/` directory, so nothing in
the merged corpus takes CI gating or hook lanes as its subject. The obvious
`references` targets — the per-domain change nodes listed under *Boundary* — do
not exist yet, and a `relationships[].target` naming an id no merged node carries
is a hard validation error. The first of those nodes to merge is the moment to add
the edges.

**See also**, as prose rather than typed edges:
`launchpad/docs/corpus/development/hermit.md`,
`launchpad/docs/corpus/development/prerequisites.md`,
`launchpad/docs/corpus/development/build.md`,
`launchpad/docs/corpus/development/debugging.md`.

## Scope and omissions

**This node covers** the mapping from a changed path to the automated gates that
evaluate it — CI's five filter groups and every job condition that reads them, the
unconditional steps inside the `changes` job, lefthook's pre-commit, commit-msg
and pre-push lanes with their globs and merge-base scoping, the unfiltered
file-size ratchet and the roots it governs, the cohort workflows' path triggers,
the upstream workflows that a `launchpad`-based pull request never reaches — plus
the companion-change contracts that no path filter expresses, and the known
asymmetries between the CI and local wiring.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Configuration change procedure | #848 |
| Database / migration change procedure | #855 |
| Event kind change procedure | #858 |
| Protocol change procedure | #861 |
| Public API change procedure | #862 |
| Building and the build gate's own semantics | #846 |
| Toolchain activation and version floors | `development/hermit.md`, `development/prerequisites.md` |
| The `'justfile'` casing defect's fix | launchpad-26/buzz#442, open |
| The mixed-quantifier filter defect's history | launchpad-26/buzz#181 |

**Expected but not verified when this node was written:**

- **`dorny/paths-filter`'s pinned picomatch version was not executed.** Case
  sensitivity was confirmed against picomatch 2.3.2 in an unrelated checkout, not
  against the version the pinned action bundles. The `Justfile` consequence is
  therefore carried as an inference, not a fact.
- **No pull request was opened to observe the filter outputs.** Every job
  condition above is read from `ci.yml`'s text; none was watched evaluating on a
  live run, so a discrepancy between the authored condition and GitHub's
  evaluation would not have been caught here.
- **The absence of a kind-sync check is a negative search result, not a proof.**
  A repository-wide search of `scripts/`, `.github/` and the `Justfile` found no
  file naming both `kinds.ts` and `nostr_models.dart`; a check enforcing the
  contract by some other means would not have been found by that search.
- **`.github/workflows/` holds thirty workflow files and this node reads the
  triggers of a subset** — `ci.yml`, eight of the ten `launchpad-*` workflows
  (`launchpad-issue-check.yml` fires on issues rather than on a change, and
  `launchpad-review-agent-publish.yml` is triggered by `pull_request_target` with
  no path filter), `docker.yml`, and the three `branches: [main]`-restricted ones.
  Release, canary, benchmark,
  helm-chart, mesh-lifecycle and sprig workflows were not catalogued, so their
  path triggers are outside what this node establishes.
- **Required-check configuration was not inspected.** Which of these jobs a
  branch ruleset actually requires before merge is a repository setting, not a
  file in the tree, and no claim about it is made here.
