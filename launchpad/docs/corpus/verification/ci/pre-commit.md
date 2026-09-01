---
id: verification-ci-pre-commit
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
  - statement: "lefthook.yml declares a pre-commit block with parallel: true and five commands -- rust-fmt, desktop-tauri-fmt, desktop-fix, web-fix, mobile-fmt -- each scoped by its own glob (crates/** plus examples/countdown-bot/**; desktop/src-tauri/**; desktop/** excluding desktop/src-tauri/**; web/**; mobile/**) and each declaring stage_fixed: true."
    entry_class: FACT
    evidence:
      - "lefthook.yml:43-68"
  - statement: "Each pre-commit command's run string is a Justfile recipe: rust-fmt runs `just fmt` (`cargo fmt --all`); desktop-tauri-fmt runs `just desktop-tauri-fmt` (`cargo fmt --manifest-path desktop/src-tauri/Cargo.toml --all`); desktop-fix and web-fix run `just desktop-fix` / `just web-fix` (`pnpm exec biome check --write .`, run inside desktop/ and web/ respectively); mobile-fmt runs `just mobile-fmt` (`dart format .`, run inside mobile/ after unsetting GIT_DIR and GIT_WORK_TREE)."
    entry_class: FACT
    evidence:
      - "lefthook.yml:43-68"
      - "Justfile:113-114"
      - "Justfile:153-154"
      - "Justfile:137-138"
      - "Justfile:718-719"
      - "Justfile:742-743"
  - statement: "Root CLAUDE.md's Quality Gates section states that pre-commit hooks are installed automatically by `just setup`, run fix variants in parallel (Rust fmt, Tauri Rust fmt, desktop biome fix, web biome fix, mobile dart format), that auto-fixable issues are fixed and re-staged, and that unfixable lint issues block the commit."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "mobile-fmt's run command, `dart format .`, carries no `--set-exit-if-changed` flag, unlike the pre-push mobile-checks lane's `dart format --output=none --set-exit-if-changed .` (via `just mobile-check`) and CI's own mobile job step, both of which do; a bare `dart format .` rewrites files in place and exits 0 regardless of how many it rewrites, so mobile-fmt is fix-only and cannot itself block a commit -- only desktop-fix and web-fix's `biome check --write` retain a lint pass that can still exit non-zero after applying its safe fixes."
    entry_class: FACT
    evidence:
      - "Justfile:742-743"
      - "Justfile:750-751"
      - ".github/workflows/ci.yml:1005"
  - statement: "scripts/dev-setup.sh, which `just setup` runs, sets core.hooksPath to the shared, worktree-independent `.git` common directory's hooks folder and then runs `lefthook install --force`, so a contributor who completes the documented setup path has the pre-commit hook installed without a separate manual step; `just hooks` performs the equivalent two actions directly for a contributor re-installing hooks after an environment change."
    entry_class: FACT
    evidence:
      - "scripts/dev-setup.sh:176-186"
      - "Justfile:54-65"
  - statement: "bin/.lefthookrc, sourced by the generated .git/hooks/* dispatchers before their own $LEFTHOOK_BIN-first lookup, pins LEFTHOOK_BIN to the repository's Hermit-managed bin/lefthook and prepends that bin/ directory to PATH, so every pre-commit command (and its subprocesses, e.g. pnpm, dart) resolves the repository's pinned toolchain versions rather than whatever the invoking shell had first on PATH."
    entry_class: FACT
    evidence:
      - "bin/.lefthookrc"
  - statement: "lefthook.yml's own top-of-file comment describes bin/.lefthookrc as pinning 'the Hermit-pinned bin/lefthook (2.1.3)', but at the revision this node records the actual pinned marker file is bin/.lefthook-2.1.10.pkg, so that comment's version number is stale against the toolchain it describes."
    entry_class: FACT
    evidence:
      - "lefthook.yml:34-40"
      - "bin/.lefthook-2.1.10.pkg"
  - statement: "CI's ci.yml runs each formatting/lint check independently of lefthook: the Rust Lint job's 'Format check' and 'Desktop Tauri format check' steps run `just fmt-check` (`cargo fmt --all -- --check`) and `just desktop-tauri-fmt-check`, the desktop job runs `just desktop-check` (`pnpm check`), the web job runs `just web-check` (`pnpm check`), and the mobile job runs `dart format --output=none --set-exit-if-changed .` directly -- none of these steps installs or invokes lefthook."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:117-121"
      - ".github/workflows/ci.yml:203"
      - ".github/workflows/ci.yml:944"
      - ".github/workflows/ci.yml:1005"
  - statement: "No automated test or CI step exercises lefthook.yml's pre-commit block itself -- there is no test that stages a deliberately misformatted file, runs the hook, and asserts the file was reformatted and re-staged, or that an unfixable lint issue aborted the commit; the pre-commit gate's only executable form is the hook configuration running live against a contributor's real `git commit`."
    entry_class: INFERENCE
    evidence:
      - "lefthook.yml"
      - ".github/workflows/ci.yml"
    confidence: 0.6
  - statement: "A git hook run through core.hooksPath is a local, opt-out mechanism: launchpad/Research/369-enforcing-the-upstream-boundary.md states plainly that a hook is bypassable via `git commit --no-verify`, giving PR #216 as an example where that bypass was actually used against this repository's lefthook pre-push hook; separately, a checkout where `just setup` or `just hooks` was never run has no hooksPath configured at all, so the pre-commit gate is not a barrier CI or the remote repository enforces on its own."
    entry_class: FACT
    evidence:
      - "launchpad/Research/369-enforcing-the-upstream-boundary.md"
      - "Justfile:52-65"
      - "scripts/dev-setup.sh:176-186"
relationships:
  - type: references
    target: development-hermit
---

# Pre-commit gate — test contract

## Purpose and boundary

This node documents one obligation: Buzz's `lefthook.yml` **pre-commit** hooks
auto-fix formatting for the file types a commit touches and re-stage what they
fix, without silently discarding an issue they cannot fix. It covers only the
`pre-commit` block of `lefthook.yml` — the five glob-triggered fix lanes
(`rust-fmt`, `desktop-tauri-fmt`, `desktop-fix`, `web-fix`, `mobile-fmt`) and
the installation path that wires them into `git commit`. It does not cover
`lefthook.yml`'s separate `commit-msg` block (the DCO `Signed-off-by` trailer)
or its `pre-push` block (branch-skew, file-size, and test/lint lanes) — both
are distinct obligations with their own trigger points and enforcement
posture, named as gaps below rather than folded in here.

## Obligation

> When `git commit` runs with the repository's `core.hooksPath` pointed at
> lefthook (installed by `just setup` or `just hooks`), each pre-commit
> command whose glob matches a file in the commit runs before the commit is
> created; any file that command rewrites is re-staged into the same commit
> via `stage_fixed: true`; and a command that exits non-zero after attempting
> its fixes aborts the commit instead of completing it silently.

## Verifying check(s) / hook(s)

- `lefthook.yml`, `pre-commit:` block — the five named commands: `rust-fmt`,
  `desktop-tauri-fmt`, `desktop-fix`, `web-fix`, `mobile-fmt`. This
  configuration file **is** the obligation's enforcement mechanism; there is
  no separate automated test asserting its behavior (see *Current enforcement
  status* below).
- Each command's `run:` value resolves to a Justfile recipe: `just fmt`,
  `just desktop-tauri-fmt`, `just desktop-fix`, `just web-fix`, `just
  mobile-fmt` — the exact commands are quoted in the evidence ledger above.
- `bin/.lefthookrc` — the `rc:` file lefthook sources before every hook run,
  which pins the Hermit-managed `bin/lefthook` binary and prepends the
  repository's Hermit `bin/` to `PATH` for every lane's subprocesses.

## How to run / trigger it

**Automatically, via a real commit** (the normal path): after `just setup` or
`just hooks` has run once, stage a change under one of the five globs and run
`git commit`. The matching lane(s) run in parallel before the commit object is
created; a file a lane rewrites is re-staged automatically, and the commit
proceeds unless a lane exits non-zero.

**Directly, without committing**, using the Hermit-pinned binary the
repository ships:

```bash
./bin/lefthook run pre-commit
```

This runs every configured `pre-commit` command against the files lefthook
determines are staged, independent of whether `core.hooksPath` has been
configured — useful for inspecting a lane's behavior without creating a
commit.

**Installing the hooks**, if they are not already installed for a checkout or
worktree:

```bash
just hooks     # equivalent to: git config --local core.hooksPath <shared .git/hooks>; lefthook install --force
```

`just setup` performs the same two steps as part of `scripts/dev-setup.sh`,
so a contributor who completed the documented setup path already has this
installed.

## Current enforcement status

**This obligation does not fit the verified/gated/pending taxonomy cleanly,
and the honest answer says so rather than forcing one label.** The mechanism
is real and unconditional: every `git commit` made with `core.hooksPath`
configured runs the matching lane(s), with no `#[ignore]`-style skip and no
stub. But unlike this repository's CI-run test contracts, nothing automated
asserts that behavior — there is no test that stages a misformatted file,
invokes the hook, and checks the result. The closest accurate statement,
broken into its parts:

- **Configured and live**, for any contributor whose checkout has run `just
  setup` or `just hooks`: FACT, from `lefthook.yml`'s `pre-commit:` block and
  the installation path in `scripts/dev-setup.sh`.
- **Not exercised by any automated test or CI step**: FACT, from reading
  `lefthook.yml` and `.github/workflows/ci.yml` — CI's own format/lint jobs
  (`just fmt-check`, `just desktop-tauri-fmt-check`, `just desktop-check`,
  `just web-check`, the mobile job's direct `dart format
  --set-exit-if-changed`) re-check the same five surfaces independently of
  lefthook, rather than testing lefthook's own hook-triggering behavior.
- **Not enforceable on anyone by itself**: a local git hook is opt-out
  (`git commit --no-verify`) and opt-in in the first place (a checkout that
  never ran `just setup`/`just hooks` has no hooksPath configured at all).
  CI's independent format/lint jobs above are what actually stops
  unformatted code from merging regardless of whether pre-commit ran, was
  skipped, or was never installed.

If this is scored against the template's three-state scale, **pending** is
the least inaccurate label for "no automated test exists" — but read the
paragraph above rather than the single word: the gate is not stubbed or
unimplemented, it simply has no test of its own, and CI is the layer that
actually cannot be skipped.

## Limits

- **Only two of the five lanes carry a lint gate that can fail.**
  `desktop-fix` and `web-fix` run `biome check --write`, which can still exit
  non-zero after applying its safe fixes if an unfixable lint violation
  remains. `rust-fmt`, `desktop-tauri-fmt`, and `mobile-fmt` run pure
  formatters (`cargo fmt --all`, `dart format .` with no
  `--set-exit-if-changed`) that reformat and exit 0 regardless of content, so
  those three lanes cannot themselves block a commit.
- **Whether `biome check --write` actually exits non-zero on a genuine
  unfixable violation in this repository was not independently executed**
  while authoring this node — the claim rests on root CLAUDE.md's own
  description of the gate (cited above as a FACT about what that document
  says), not on a reproduced failing run.
- **Nothing here proves the hook is installed for any given contributor.**
  `just setup`/`just hooks` install it; a checkout that skips both, or a
  `.git/hooks` directory a contributor otherwise rewires, runs with no
  pre-commit enforcement at all, and nothing in this repository detects that
  case.
- **`--no-verify` is not examined here beyond naming it.** How often it is
  used, and whether any process catches it after the fact beyond CI's
  independent checks, is out of scope for this node.
- **This node does not prove any of the five underlying tools (`cargo fmt`,
  `biome`, `dart format`) behave correctly** — only that lefthook invokes
  them, on the globs and with the flags shown above. Correctness of those
  tools themselves is out of scope.
- **CI's independent format/lint jobs are named as the real backstop, but
  their own pass/fail behavior is not this node's obligation** — a future
  test-contract node for `just fmt-check`, `just desktop-check`, `just
  web-check`, or the mobile CI format step would document each on its own
  terms.

## Scope and omissions

**This node covers** the `pre-commit` block of `lefthook.yml`: its five
glob-triggered fix lanes, their exact underlying commands, the
`stage_fixed`/auto-fix-and-block behavior root CLAUDE.md describes, the
installation path that wires the hook into `git commit`, and the honest
enforcement-status gap between "runs live" and "has an automated test."

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `commit-msg` DCO `Signed-off-by` trailer hook | A separate corpus node, not yet authored |
| The `pre-push` block (`branch-skew`, `push-head-scope`, `file-size-check`, `rust-tests`, `desktop-check`/`desktop-typecheck`/`desktop-test`, `desktop-tauri-checks`, `mobile-checks`) | A separate corpus node, not yet authored |
| CI's own independent format/lint jobs (`just fmt-check`, `just desktop-tauri-fmt-check`, `just desktop-check`, `just web-check`, the mobile job's `dart format --set-exit-if-changed`) as obligations in their own right | A separate corpus node, not yet authored |
| Correctness of `cargo fmt`, `biome`, and `dart format` themselves | Their own upstream projects, not this repository |
| How Hermit pins and resolves `bin/lefthook` and the other pinned tools generally | `development-hermit` |

**Expected but not verified when this node was written:**

- **Whether `biome check --write` exits non-zero on a genuine unfixable
  violation was not reproduced in this repository** — `desktop/node_modules`
  was not installed while authoring this node, so the claim that
  `desktop-fix`/`web-fix` can block a commit rests on root CLAUDE.md's
  description rather than an observed failing run.
- **The pre-commit hook itself was not triggered end-to-end while authoring
  this node** (no test commit was made and `./bin/lefthook run pre-commit`
  was not executed), specifically to avoid reformatting unrelated files in a
  worktree that must contain exactly one new hand-authored corpus document.
  The commands quoted above are read directly from `lefthook.yml` and
  `Justfile`, not from an observed run.
