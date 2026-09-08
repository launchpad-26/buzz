---
id: verification-unit-desktop
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "desktop/package.json's `test` script is `node --import ./test-loader.mjs --experimental-strip-types --test \"src/**/*.test.mjs\"` -- Node's own built-in test runner, invoked directly, with no Vitest, Jest, or other third-party test framework in the invocation."
    entry_class: FACT
    evidence:
      - "desktop/package.json:17"
  - statement: "`test-loader.mjs` registers a single ESM loader hook, `test-loader-hooks.mjs`, whose job is to resolve extensionless `@/...` and relative specifiers to their `.ts`/`.tsx`/`.js`/`.jsx`/`.mjs` files on disk and to strip TypeScript via Node's `--experimental-strip-types` flag, plus stub a small, explicit list of CJS-only packages (e.g. `emoji-mart`) that Node's ESM loader cannot otherwise resolve; the loader does not construct a browser, a DOM, or a Tauri IPC bridge for any test."
    entry_class: FACT
    evidence:
      - "desktop/test-loader.mjs"
      - "desktop/test-loader-hooks.mjs"
  - statement: "Individual desktop unit test files that need a Tauri global construct it themselves inline rather than receiving one from the loader -- `desktop/src/shared/deep-link.test.mjs` builds its own `tauriInternals` object and assigns it to `globalThis.window.__TAURI_INTERNALS__` and `globalThis.__TAURI_INTERNALS__` before importing the module under test, with no such assignment present in `test-loader-hooks.mjs` itself."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/deep-link.test.mjs:1-27"
      - "desktop/test-loader-hooks.mjs"
  - statement: "42 desktop unit test files import the `jsdom` package directly (an in-process, library-constructed DOM), which is a devDependency of `desktop/package.json`; this is a Node-process-local emulation, not a real browser, a Tauri webview, or Playwright."
    entry_class: FACT
    evidence:
      - "count_files_matching('desktop/src/**/*.test.mjs', grep='jsdom') -> 42"
      - "desktop/package.json"
  - statement: "At the recorded revision, 610 files under `desktop/src/` match `*.test.mjs`."
    entry_class: FACT
    evidence:
      - "count_files('desktop/src/**/*.test.mjs') -> 610"
  - statement: "The Justfile's `desktop-test` recipe is `cd desktop && pnpm test`, and CI's `Desktop Core` job (`.github/workflows/ci.yml`) runs a step named 'Desktop unit tests' whose command is `just desktop-test`, immediately after a 'Desktop lint and format' step and before the desktop build and Tauri steps -- the same job, not a separate one from Tauri/build/e2e work."
    entry_class: FACT
    evidence:
      - "Justfile:140-142"
      - ".github/workflows/ci.yml:204-205"
  - statement: "The `desktop-core` job runs unconditionally when the workflow is triggered by a push, and on a pull request only when the `changes` job's `desktop`, `desktop-rust`, or `rust` output is `true`; there is no further gate inside the job itself on the 'Desktop unit tests' step -- once the job runs, that step always runs."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:148-153"
  - statement: "lefthook.yml's pre-push `desktop-test` command runs `just desktop-test`, scoped by `files: git diff --name-only origin/main...HEAD` and `glob: [\"desktop/**\", \"pnpm-lock.yaml\"]` excluding `desktop/src-tauri/**`, so it fires locally only on a push whose merge-base diff against `origin/main` touches non-Tauri desktop source or the lockfile -- a narrower trigger than CI's `desktop-core` job, which also runs on every plain push regardless of changed paths."
    entry_class: FACT
    evidence:
      - "lefthook.yml:112-116"
  - statement: "lefthook.yml's own header comment states that `desktop-test` (along with `desktop-check`/`desktop-typecheck`) deliberately does not trigger on Rust-only changes locally, because the command is 'pure TS (biome + tsc + node:test) with no Rust dependency,' even though CI's Desktop Core job also triggers on the `rust` change filter."
    entry_class: FACT
    evidence:
      - "lefthook.yml:18-21"
  - statement: "Running `pnpm test` from `desktop/` at the recorded revision reported 5780 tests across 84 suites: 5779 passing, 0 failing, 1 cancelled, over a duration of approximately 598 seconds; the sole cancelled test was `src/features/terminal/terminalBannerWave.test.mjs`, which Node's test runner reported with the diagnostic 'Promise resolution is still pending but the event loop has already resolved.'"
    entry_class: FACT
    evidence:
      - "run_command('pnpm test', cwd='desktop') -> tests 5780; suites 84; pass 5779; fail 0; cancelled 1; duration_ms 597745; failing tests: none; cancelled: src/features/terminal/terminalBannerWave.test.mjs (dangling-promise diagnostic)"
  - statement: "CLAUDE.md's E2E-specs guidance states that the desktop app's mock Tauri bridge is compiled in only under `pnpm build:e2e` (`--mode e2e`), that a plain `pnpm run build` strips it so `window.__TAURI_INTERNALS__` is undefined, and that desktop E2E specs are Playwright specs under `desktop/tests/e2e/` driven by `pnpm test:e2e:smoke` / `pnpm test:e2e:integration`, which is a distinct build, distinct runner, and distinct directory from the `pnpm test` / `desktop/src/**/*.test.mjs` unit-test surface this node documents."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "desktop/package.json:17"
      - "desktop/package.json:9"
      - "desktop/package.json:21-22"
  - statement: "At the recorded revision, `origin/launchpad`'s corpus tree contains no `launchpad/docs/corpus/verification/` subtree and no node anywhere in the corpus declares an id resembling `verification-e2e-desktop`, so no `references` edge to a desktop end-to-end verification node can resolve; this node declares no `relationships` for that reason, to be revisited once such a node merges."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no verification/ path present; no id matching verification-e2e-desktop found in any loaded node"
  - statement: "Issue #1393's parent PRD (#617) and its own task body ask for exactly one hand-authored canonical document at this path, documenting a testable obligation with named verifying test(s), an honestly stated enforcement status, and a limits section -- the same required-sections shape `launchpad/docs/corpus/templates/test-contract.md` describes for a `type: verification` node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1393 definition of done, read against launchpad/docs/corpus/templates/test-contract.md"
  - statement: "This node's own obligation is stated at the level of the unit-test harness's operating contract (isolation from Tauri/browser, the invocation command, and unconditional CI enforcement) rather than at the level of any one test file's specific business assertion. That is a scoping decision the author made, not a finding either source compelled: #1393's task body names no single business-behavior obligation for desktop unit tests to describe, and `test-contract.md`'s own Boundary section explicitly excludes 'a whole test suite's structure or how to write tests generally' from a test-contract node's proper subject -- the two facts together leave the choice open, and the author made it, so it is recorded here rather than dressed up as an inference from either document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1393 definition of done, compared against launchpad/docs/corpus/templates/test-contract.md's Boundary against neighboring corpus content section"
---

# Desktop unit tests — test contract

## Purpose and boundary

This node documents one obligation: that the desktop app's TypeScript/React unit-test
surface — every file matching `desktop/src/**/*.test.mjs` — runs under Node's own
built-in test runner, independent of any Tauri IPC bridge, real browser, or Playwright
harness, and that this surface is exercised unconditionally by CI whenever the
`Desktop Core` job runs. It covers that harness-level obligation only. It does not
cover, and makes no claim about, whether any individual test's own business-logic
assertion is correct — that is each test file's own concern, not this node's. It also
does not cover the desktop end-to-end (Playwright, Tauri-mock-bridge) surface, which is
a distinct build, a distinct runner, and a distinct obligation — see *Scope and
omissions*.

## Obligation

> Every file matching `desktop/src/**/*.test.mjs` runs to completion under Node's
> built-in test runner via `pnpm test` (invoked as `just desktop-test`), without
> requiring a Tauri IPC bridge, a real browser, or a Playwright harness to be present,
> and CI's `Desktop Core` job (`.github/workflows/ci.yml`) executes this suite
> unconditionally as one of its own steps whenever that job itself runs.

## Verifying test(s)

- **The suite itself**: `desktop/src/**/*.test.mjs` (610 files at the recorded
  revision), collectively invoked by the single command below. There is no per-file
  enumeration in this node — the obligation is about the harness all 610 files share,
  not about any one file's assertions.
- **`desktop/src/shared/deep-link.test.mjs`** — representative evidence for the
  "no Tauri bridge required by the harness itself" half of the obligation: this file
  constructs its own `globalThis.__TAURI_INTERNALS__` stub before importing the module
  under test (lines 1-27), rather than relying on any ambient Tauri global the loader
  or runner would otherwise supply. No such global is set anywhere in
  `desktop/test-loader-hooks.mjs`.
- **`desktop/test-loader.mjs`** / **`desktop/test-loader-hooks.mjs`** — the loader
  actually passed to `node --import`; covers the "runs under Node's built-in test
  runner, with TypeScript stripped and `@/...` specifiers resolved, and nothing else
  injected" half of the obligation.

## How to run it

```bash
cd desktop && pnpm test
```

Equivalently, from the repository root: `just desktop-test`. Neither command requires
Docker, a running relay, Postgres, Redis, or a built Tauri binary. No flag or
environment variable gates this command — unlike the desktop E2E suites, there is no
`#[ignore]`-equivalent skip here; every matched `*.test.mjs` file runs on every
invocation.

## Current enforcement status

**Verified**, as of the recorded revision, with one caveat stated plainly rather than
smoothed over:

- CI's `Desktop Core` job runs `just desktop-test` unconditionally once the job itself
  runs (`.github/workflows/ci.yml:204-205`), and the job runs on every `push` and on
  every pull request that changes `desktop`, `desktop-rust`, or `rust` paths
  (`.github/workflows/ci.yml:148-153`).
- `lefthook.yml`'s pre-push `desktop-test` lane (`lefthook.yml:112-116`) also runs
  `just desktop-test` locally, scoped to a branch's merge-base diff against
  `origin/main` touching non-Tauri desktop source or the lockfile — narrower than CI's
  trigger, so CI remains the authoritative gate for a push that lefthook's scoping
  does not catch (e.g. a non-HEAD ref push, per `scripts/check-push-head-scope.sh`'s own
  warn-only lane).
- Actually running `pnpm test` at the recorded revision produced **5779 passing, 0
  failing, 1 cancelled**, out of 5780 tests in 84 suites (~598s wall time). The one
  cancellation, `src/features/terminal/terminalBannerWave.test.mjs`, is not a business-
  logic failure — Node's test runner reported a dangling-promise diagnostic
  ("Promise resolution is still pending but the event loop has already resolved")
  rather than an assertion failure — but it means the harness's most recently observed
  run at this revision is not a clean 5780/5780, and this node does not round that up.

## Limits

- **A pass proves the harness ran the files, not that every file's assertions are
  individually correct or exhaustive.** This node's obligation is about the harness
  (isolation, invocation, CI wiring), not about any one test's coverage of its own
  subject; a `*.test.mjs` file with weak or missing assertions inside it is invisible
  to the claim this node makes.
- **The observed run (5779/5780, 1 cancelled) is one invocation at one revision.**
  Per `launchpad/docs/corpus/standards/test-references.md`, a single observed pass (or
  near-pass) is a single observation; this repository's own tooling provides no
  retry/flaky signal for `node --test` runs comparable to
  `desktop/scripts/summarize-flaky-tests.mjs`'s Playwright-specific `flaky` label, so
  whether `terminalBannerWave.test.mjs`'s cancellation reproduces on a second run was
  not checked, and no claim is made either way.
- **42 of 610 files construct an in-process DOM via `jsdom`.** "No browser required"
  means no real browser process and no Tauri webview — it does not mean every test is
  free of DOM emulation; `jsdom` is a Node-process-local library, not a browser.
- **This node does not verify that `desktop/src/**/*.test.mjs` is an exhaustive or
  sufficient set of unit tests for the desktop app.** It verifies only that the files
  which do exist under that glob run the way described above.

## Scope and omissions

**This node covers** the desktop unit-test harness's operating contract: which runner
executes `desktop/src/**/*.test.mjs`, what that runner does and does not provide
(TypeScript stripping and specifier resolution, but no Tauri bridge or real browser),
how the suite is invoked, and its current CI/pre-push enforcement and most recently
observed pass state.

**It does not cover:**

- **Any individual test file's own business-logic obligation.** Each of the 610 files
  asserts something specific about its own subject; those obligations belong to future,
  narrower test-contract nodes (or elsewhere), not to this one.
- **Desktop end-to-end tests.** `pnpm test:e2e:smoke` / `pnpm test:e2e:integration`
  are Playwright specs under `desktop/tests/e2e/`, driven by a build
  (`pnpm build:e2e`) that compiles in a mock Tauri bridge unavailable to the plain
  `pnpm test` unit-test build. That is a different obligation, a different command,
  and a different verifying-test set from this node's. **No `references` (or other)
  relationship is declared to a desktop end-to-end verification node**: at the recorded
  revision, `origin/launchpad`'s corpus tree carries no `launchpad/docs/corpus/verification/`
  subtree at all, and no node anywhere in the corpus declares an id resembling
  `verification-e2e-desktop` — checked directly via `git ls-tree`, not assumed. The
  first such node to merge is the moment to add the edge.
- **Desktop Tauri (Rust) unit tests.** `just desktop-tauri-test` (`cargo test` inside
  `desktop/src-tauri`) is a separate command, a separate language runtime, and a
  separate CI step from the one this node documents.
- **Whether the harness's exclusion of a Tauri bridge and real browser is the *right*
  design choice for desktop unit tests.** That is a decision, not an obligation this
  node verifies; it is out of scope here.

**Expected but not verified when this node was written:**

- **Whether `terminalBannerWave.test.mjs`'s cancellation is a known, previously
  reported issue or a new observation.** No issue search was performed for it; this
  node records the observed run honestly and leaves the question open rather than
  guessing.
- **Whether the observed run's ~598 second duration is typical or was inflated by this
  worktree's cold `pnpm install` / uncached state.** Only one run was performed; no
  second run was taken to compare timing.
