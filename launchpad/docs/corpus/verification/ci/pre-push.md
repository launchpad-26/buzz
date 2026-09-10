---
id: verification-ci-pre-push
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
  - statement: "lefthook.yml's pre-push: block runs commands in parallel and defines exactly nine named commands: branch-skew, push-head-scope, file-size-check, rust-tests, desktop-check, desktop-typecheck, desktop-test, desktop-tauri-checks and mobile-checks."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "The generated .git/hooks/* dispatchers source bin/.lefthookrc (via lefthook.yml's rc: bin/.lefthookrc) before their own $LEFTHOOK_BIN-first lookup; .lefthookrc prepends the repository's Hermit bin/ to PATH and pins LEFTHOOK_BIN to the Hermit-managed lefthook binary, so every lane subprocess resolves the pinned toolchain regardless of what the invoking shell had first on PATH."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "bin/.lefthookrc"
  - statement: "Three of the nine pre-push commands (branch-skew, push-head-scope, file-size-check) carry no glob or files filter and so run on every push; the other six (rust-tests, desktop-check, desktop-typecheck, desktop-test, desktop-tauri-checks, mobile-checks) each set files: git diff --name-only origin/main...HEAD together with a glob:, so their underlying command only runs when that three-dot diff touches a matching path."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "lefthook.yml's own top-of-file comment states the globbed lanes mirror .github/workflows/ci.yml's changes job's dorny/paths-filter groups and instructs keeping the two in sync; ci.yml's changes job does define filter groups named rust, desktop, desktop-rust, web and mobile via dorny/paths-filter, matching that description."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - ".github/workflows/ci.yml"
  - statement: "file-size-check is deliberately excluded from the glob-scoping pattern used by the other six lanes; lefthook.yml's own comment states this is because the ratchet computes its own merge-base diff internally, so duplicating its governed roots in a lefthook glob would only create a second, driftable place to keep in sync."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "The file-size-check command runs four commands in sequence: node --test scripts/check-file-sizes-core.test.mjs, then node desktop/scripts/check-file-sizes.mjs, node web/scripts/check-file-sizes.mjs and node mobile/scripts/check-file-sizes.mjs, each wrapping the shared scripts/check-file-sizes-core.mjs ratchet for its own project root."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "scripts/check-file-sizes-core.mjs's resolveBaseRef() returns the CHECK_FILE_SIZES_BASE environment variable first if set, then HEAD^1 when GITHUB_ACTIONS is \"true\", and only falls back to git merge-base origin/main HEAD when neither of those applies."
    entry_class: FACT
    evidence:
      - "scripts/check-file-sizes-core.mjs"
  - statement: "At the recorded revision, origin/launchpad's own lefthook-local.yml sets CHECK_FILE_SIZES_BASE: origin/launchpad for the pre-push file-size-check command, so a local pre-push run of the ratchet is scoped to this fork's own base branch rather than falling through to resolveBaseRef()'s origin/main default."
    entry_class: FACT
    evidence:
      - "lefthook-local.yml"
  - statement: "That override was added by PR #1997 ('fix(lefthook): resolve file-size-check base from origin/launchpad, not origin/main'), merged into launchpad, closing issue #1996, which had reproduced the ratchet failing on a file identical to origin/launchpad's own tip because resolveBaseRef()'s unconditional origin/main fallback measured growth against upstream's divergent history instead of this fork's."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/1996"
      - "https://github.com/launchpad-26/buzz/pull/1997"
      - "lefthook-local.yml"
  - statement: "branch-skew's run: target is launchpad/scripts/check-branch-skew.sh, a cohort-specific rewrite documented as living under launchpad/ rather than editing the (nonexistent, upstream-referenced) scripts/check-branch-skew.sh directly; it searches every configured remote for a ref literally named launchpad, exits 0 with no output when the branch's own changed files don't overlap files changed on that ref since the branch's merge-base, and otherwise prints the overlapping files and exits 1."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "launchpad/scripts/check-branch-skew.sh"
  - statement: "push-head-scope's run: target, scripts/check-push-head-scope.sh, reads the pre-push stdin refspecs, prints a non-fatal warning to stderr naming any pushed ref whose local SHA differs from the checked-out HEAD, and always exits 0 -- lefthook.yml's own comment on this command states explicitly that it 'never fails the push', naming it as the one exception to how the other lanes behave."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "scripts/check-push-head-scope.sh"
  - statement: "just test-unit runs a fixed, explicitly enumerated sequence of infra-free cargo nextest / cargo test invocations scoped to specific crates and, in one case, a specific #[cfg(test)] filter expression (buzz-core, buzz-auth --lib and --doc, buzz-voice, buzz-cli, buzz-db --lib, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes, buzz-agent --lib, and a filtered buzz-relay --lib admin-API subset); its own comments state repeatedly that this explicit enumeration exists because nothing in CI runs cargo test --workspace, so an un-enumerated crate's tests run in no lane."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "just test-unit never invokes cargo clippy, and lefthook.yml's pre-push block contains exactly one clippy invocation across all nine commands -- desktop-tauri-clippy, Tauri-scoped, inside desktop-tauri-checks -- with no cargo clippy --workspace command anywhere in the pre-push block."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "lefthook.yml"
  - statement: "Root CLAUDE.md's Quality Gates section states 'Pre-push hooks run the repository-wide differential file-size gate, clippy (workspace + Tauri) ...', which is contradicted by the previous claim; this exact discrepancy is independently recorded as finding H13 in launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md ('Pre-push hooks don't run workspace clippy, contradicting CLAUDE.md's Quality Gates claim'), still unresolved in either direction (no workspace-clippy pre-push command added, and the CLAUDE.md wording not corrected) at the recorded revision."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "lefthook.yml"
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md"
  - statement: "Workspace-wide cargo clippy --workspace --all-targets -- -D warnings is the just clippy recipe, which is a dependency of just check (line 96) and, transitively through just ci, but just check/just ci are commands a developer runs by choice -- neither is invoked by any pre-push lane. .github/workflows/ci.yml separately runs just clippy in its own Rust CI job."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".github/workflows/ci.yml"
  - statement: "desktop-check, desktop-typecheck and desktop-test are each glob-scoped to desktop/** and pnpm-lock.yaml, excluding desktop/src-tauri/**, and run just desktop-check (pnpm exec biome check), just desktop-typecheck (pnpm typecheck, i.e. tsc --noEmit) and just desktop-test (pnpm test) respectively."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "Justfile"
  - statement: "desktop-tauri-checks is glob-scoped to desktop/src-tauri/** plus the same Rust-affecting paths as rust-tests (crates/**, migrations/**, schema/**, Cargo.toml, Cargo.lock, rust-toolchain.toml, deny.toml, scripts/run-tests.sh, Justfile), and runs just desktop-tauri-clippy && just desktop-tauri-test serially rather than in lefthook's own parallel pool, per its own comment, 'so parallel pre-push hooks do not contend for Cargo's lock'."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "Justfile"
  - statement: "mobile-checks is glob-scoped to mobile/** and runs just mobile-check && just mobile-test serially (dart format --set-exit-if-changed, flutter analyze, then flutter test), per its own comment, to avoid contending for shared Flutter build state (.dart_tool, shader bundle) with other parallel lanes."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "Justfile"
  - statement: "just hooks points git's core.hooksPath at the absolute path of the shared .git-common-dir's hooks directory (so every linked worktree dispatches the same installed hooks) and then runs lefthook install --force to generate the dispatcher scripts; just setup does not call just hooks itself, so hook installation is a separate, one-time step per clone."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Git's own pre-push hook contract, documented in the local githooks(5) manual page, states: 'If this hook exits with a non-zero status, git push will abort without pushing anything.' launchpad/scripts/check-branch-skew.sh's own failure branch ends in an explicit exit 1, so an actual skew failure aborts the push under that documented contract, not merely by convention."
    entry_class: FACT
    evidence:
      - "read_man_page('githooks(5), pre-push section') -> \"If this hook exits with a non-zero status, git push will abort without pushing anything.\""
      - "launchpad/scripts/check-branch-skew.sh"
  - statement: "Because a glob-scoped lane's command is skipped entirely (not run-and-passed) when the three-dot diff touches nothing under its glob, a branch that touches no crates/desktop/mobile paths pushes successfully having exercised only the three unconditional lanes (branch-skew, push-head-scope, file-size-check) -- the obligation this node states never claims every lane always runs, only that a triggered lane's failure blocks the push."
    entry_class: INFERENCE
    evidence:
      - "lefthook.yml"
    confidence: 0.8
relationships:
  - type: references
    target: development-hermit
  - type: references
    target: development-prerequisites
  - type: references
    target: corpus-standard-test-references
---

# Pre-push gate — test contract

## Purpose and boundary

This node documents one obligation: **that this repository's local pre-push git hook
blocks a push whose triggered checks do not pass.** It covers the pre-push hook
mechanism itself — what lanes exist, when each one is triggered, what each one
actually runs, and how failure of a triggered lane relates to the outcome of `git
push` — as configured in `lefthook.yml` (plus its `lefthook-local.yml` override) at
the recorded revision. It does not cover pre-commit hooks, CI's own workflow jobs as
a separate enforcement surface, or the correctness of any individual lane's
underlying logic (e.g. whether `check-branch-skew.sh`'s overlap detection is itself
bug-free) beyond what is needed to state honestly what each lane checks and when.

## Obligation

> A `git push` from a local clone of this repository, with hooks installed via `just
> hooks`, is rejected before any commit reaches the remote if any pre-push lane
> configured in `lefthook.yml` that is triggered for the pushed branch's current diff
> exits non-zero.

## Verifying check(s)

Nine `lefthook.yml` `pre-push:` commands jointly implement this obligation. Three run
unconditionally on every push; six run only when the branch's `git diff --name-only
origin/main...HEAD` touches a path under the listed `glob:`.

| Command (`lefthook.yml`) | Trigger | What it runs | Covers |
|---|---|---|---|
| `branch-skew` | always | `launchpad/scripts/check-branch-skew.sh` | Fails if the branch is behind this fork's `launchpad` ref *and* a file the branch changed was also changed on `launchpad` since the branch's merge-base — a stale-base check specific to this cohort fork, replacing upstream's `origin/main`-assuming script. |
| `push-head-scope` | always | `scripts/check-push-head-scope.sh` | Warns (never fails) when a pushed ref's commit differs from the checked-out `HEAD`, naming the scoped lanes below as not having validated that ref. |
| `file-size-check` | always | `just file-size-check` (`node --test scripts/check-file-sizes-core.test.mjs`, then `check-file-sizes.mjs` for `desktop/`, `web/`, `mobile/`) | The differential file-size ratchet: no governed file may grow past its allowed line count, measured against a base resolved by `scripts/check-file-sizes-core.mjs`'s `resolveBaseRef()`. |
| `rust-tests` | `crates/**`, `migrations/**`, `schema/**`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `deny.toml`, `scripts/run-tests.sh`, `Justfile` | `just test-unit` | A fixed, explicitly enumerated set of infra-free `cargo nextest`/`cargo test` runs across specific crates — not `cargo test --workspace` and not `cargo clippy`. |
| `desktop-check` | `desktop/**` (excl. `desktop/src-tauri/**`), `pnpm-lock.yaml` | `just desktop-check` | Desktop Biome lint/format check. |
| `desktop-typecheck` | same as above | `just desktop-typecheck` | `pnpm typecheck` (`tsc --noEmit`). |
| `desktop-test` | same as above | `just desktop-test` | `pnpm test` (desktop unit tests). |
| `desktop-tauri-checks` | `desktop/src-tauri/**` plus the `rust-tests` path set | `just desktop-tauri-clippy && just desktop-tauri-test` (serial) | Tauri-crate `cargo clippy -D warnings` and its tests. |
| `mobile-checks` | `mobile/**` | `just mobile-check && just mobile-test` (serial) | `dart format --set-exit-if-changed`, `flutter analyze`, `flutter test`. |

## How to run it

- **Precondition:** hooks must be installed once per clone/worktree —
  `just hooks` (wraps `git config --local core.hooksPath <shared .git/hooks>` and
  `lefthook install --force`). `just setup` does not do this on its own.
- **Normal path:** `git push` — the installed `.git/hooks/pre-push` dispatcher sources
  `bin/.lefthookrc`, pins the Hermit toolchain onto `PATH`, and runs the triggered
  commands above in parallel (serially within `desktop-tauri-checks` and
  `mobile-checks`).
- **Without pushing:** `lefthook run pre-push` from the repository root runs the same
  commands against the checked-out `HEAD` — the verification method named directly in
  `launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md`'s own finding H13
  (`lefthook run pre-push on a clippy-triggering branch fails locally before push`).
  Add `--command <name>` to run one lane in isolation, or `--all-files` to force a
  glob-scoped lane to run regardless of the current diff.
- Activating Hermit first (`. ./bin/activate-hermit`) is recommended per root
  `CLAUDE.md`, though `bin/.lefthookrc` self-pins `PATH`/`LEFTHOOK_BIN` for the hook's
  own subprocesses even in an unactivated shell.

## Current enforcement status

**Verified** for all nine lanes as configured — each is a real, currently-runnable
command, not a stub — with two named qualifications:

- **`push-head-scope` never fails.** It is a warn-only lane by design (see its own
  code comment); it is "triggered" on every push but can never itself cause the
  rejection this obligation describes.
- **The glob-scoped lanes (`rust-tests` through `mobile-checks`) are conditionally
  triggered, not conditionally passing.** A branch that touches nothing under a
  lane's `glob:` does not run that lane's command at all; this is by design (mirroring
  CI's own `dorny/paths-filter` groups), not a gap in what the obligation claims.

**A previously real gap in `file-size-check`'s base resolution is already closed at
this revision.** `scripts/check-file-sizes-core.mjs`'s `resolveBaseRef()` still falls
back to `git merge-base origin/main HEAD` in its own source, which would be wrong for
this fork (`origin/main` is upstream's branch, not this fork's `launchpad` base — see
closed issue #1996). But `origin/launchpad`'s own `lefthook-local.yml` sets
`CHECK_FILE_SIZES_BASE: origin/launchpad` for the pre-push `file-size-check` command
specifically, which `resolveBaseRef()` checks first and prefers over the `origin/main`
fallback. So the pre-push ratchet, as actually invoked by this hook, is already scoped
correctly; only a bare direct invocation of the underlying script outside `lefthook`
(or outside `lefthook-local.yml`'s override) would hit the stale fallback.

## Limits

- **This node does not claim workspace-wide `clippy` runs at pre-push, because it
  does not.** `rust-tests` runs `just test-unit`, which never invokes `cargo clippy`;
  the only `clippy` command anywhere in `lefthook.yml`'s `pre-push:` block is
  Tauri-scoped. Root `CLAUDE.md`'s "Quality Gates" section currently states pre-push
  runs "clippy (workspace + Tauri)" — that half of the claim does not hold at this
  revision. This is not a new finding of this node; it restates already-recorded
  audit finding H13, unresolved as of the recorded revision. Workspace `clippy` is
  enforced by `.github/workflows/ci.yml`'s own Rust CI job and by `just check`/`just
  ci` when a developer runs them manually — neither is a pre-push lane.
- **A pushed ref that is not the checked-out `HEAD` is not validated by the
  glob-scoped lanes.** Both the three-dot diff those lanes use and lefthook's own
  stock file discovery inspect `HEAD`; pushing a different ref (an explicit refspec,
  `git push --all`) only produces a non-fatal `push-head-scope` warning, and CI is the
  only path-scoped gate that actually ran against that ref's real content.
- **`just test-unit`'s coverage is a fixed, hand-enumerated crate list, not
  `cargo test --workspace`.** A new crate, or a new test module inside an existing
  crate that nobody adds to the enumeration, runs in no local pre-push lane; its own
  comments name this explicitly as a recurring risk, not a hypothetical one.
- **Hooks must be installed to exist at all.** A clone that has run `just setup` but
  never `just hooks` has no local pre-push enforcement whatsoever; every claim in this
  node describes what happens once the hook is installed, not a property of the
  repository on its own.
- **No lane in this list re-verifies that the branch actually builds** — `just
  test-unit` and the desktop/mobile test commands compile what they need to run their
  own tests, but a full `cargo build --workspace` or equivalent is not itself a
  pre-push obligation.

## Scope and omissions

**Covered:** the nine `lefthook.yml` pre-push commands, their trigger conditions,
what each one runs, the git-level contract that a non-zero exit blocks the push, how
to run the gate manually, and the two currently-known gaps between what this gate
enforces and what `CLAUDE.md`/the file-size ratchet's own source code might suggest in
isolation.

**Not covered here, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Pre-commit hooks (formatting auto-fix lanes) | A separate `verification`/`ci` node, not yet written |
| CI's own workflow jobs as an independent enforcement surface | `.github/workflows/ci.yml`, not yet a corpus node |
| Whether `check-branch-skew.sh`'s overlap-detection logic is itself correct in every case | Not verified here beyond reading its source once |
| Fixing the workspace-clippy / `CLAUDE.md` discrepancy (H13) | `launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md`; no linked implementation issue exists yet at this revision |
| Hermit toolchain pinning mechanics in general | `launchpad/docs/corpus/development/hermit.md` |
| `lefthook` as a Hermit-pinned prerequisite and its version | `launchpad/docs/corpus/development/prerequisites.md` |
| How any corpus node should cite a test/check as evidence, generally | `launchpad/docs/corpus/standards/test-references.md` |

**Expected but not verified when this node was written:**

- **No lane was actually exercised end-to-end for this node** (no real `git push`,
  no `lefthook run pre-push` invocation was executed) — every command in the table
  above is confirmed to exist and be wired to the stated trigger by reading
  `lefthook.yml` and the scripts/recipes it calls, not by observing a live pass or
  failure.
- **Whether `just setup` is expected to also install hooks, and simply does not, or
  whether the separation is deliberate**, was not resolved from any decision record —
  only the current script behavior (`hooks` is its own recipe, not a dependency of
  `setup`) is recorded as fact.
- **Whether resolving H13 should add a workspace-clippy pre-push lane or correct
  `CLAUDE.md`'s wording** is explicitly left to a human, per the audit's own framing
  of that finding; this node does not decide it.
