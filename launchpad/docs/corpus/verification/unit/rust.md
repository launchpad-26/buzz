---
id: verification-unit-rust
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
  - statement: "Justfile's `test-unit` recipe (Justfile:315-388) is introduced by its own comment as 'Run unit tests only (no infra needed)', runs `./scripts/test-ensure-local-relay-key.sh` first, and then, when `cargo-nextest` is on PATH, runs a fixed sequence of `cargo nextest run -p <crate>` / `cargo test -p <crate>` invocations naming nine crates by explicit `-p` flag plus one name-filtered subset of a tenth."
    entry_class: FACT
    evidence:
      - "Justfile:315-388"
  - statement: "The nine crates `test-unit` names outright are buzz-core, buzz-auth (both `--lib` and, separately, `cargo test -p buzz-auth --doc` for its NIP-FI verifier doctests), buzz-voice, buzz-cli, buzz-db (`--lib` only), buzz-conformance (all targets), buzz-push-gateway, buzz-backend-kubernetes, and buzz-agent (`--lib`); the tenth, buzz-relay, is not run in full -- it is scoped to `cargo nextest run -p buzz-relay --lib -E 'test(/^api::admin::/) - test(=...disabled_mode_allows_unauthenticated_requests_on_the_admin_host) - test(=...nip98_mode_unrostered_signer_does_not_consume_a_replay_slot)'`, i.e. only the api::admin module's tests, minus two named exclusions the recipe's own comment says are excluded because they pass without a database only by waiting out a ~30s sqlx acquire timeout."
    entry_class: FACT
    evidence:
      - "Justfile:321-385"
  - statement: "The recipe's own comments state three separate times, verbatim, that 'nothing in CI runs `cargo test --workspace`' (for buzz-backend-kubernetes, buzz-agent, and buzz-relay respectively), and that workspace membership alone buys clippy/check, not a single executed unit test -- so a crate not named by one of the `-p` flags above has no unit-test lane in this recipe at all, regardless of whether it defines `#[test]` functions."
    entry_class: FACT
    evidence:
      - "Justfile:347-351"
      - "Justfile:356-359"
      - "Justfile:365-368"
  - statement: "The root Cargo.toml workspace (Cargo.toml:1-36) lists 31 `members` under `crates/*`, `launchpad/crates/knowledge` and `examples/countdown-bot`, and separately `exclude`s `desktop/src-tauri`; only 9 of those 31 members are named by an explicit `-p` flag anywhere in `test-unit`."
    entry_class: FACT
    evidence:
      - "Cargo.toml:1-36"
      - "Justfile:315-388"
  - statement: "CLAUDE.md's 'Common Gotchas' section states plainly, as gotcha 5, that 'Desktop crate excluded from root workspace -- `cargo test` at repo root does NOT run desktop tests. Use `cargo test --manifest-path desktop/src-tauri/Cargo.toml` explicitly.'"
    entry_class: FACT
    evidence:
      - "CLAUDE.md:472"
  - statement: "crates/buzz-core/src/kind.rs declares `#[cfg(test)] mod tests` at lines 898-899 and, inside it, a `#[test] fn no_duplicate_kind_values()` at lines 902-903 that asserts every value in `ALL_KINDS` is unique via `HashSet::insert`; this test carries no `#[ignore]` attribute and is exercised, without any external infrastructure, by `test-unit`'s `cargo nextest run -p buzz-core --lib` step."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:898-908"
      - "Justfile:321"
  - statement: "scripts/run-tests.sh's `run_unit_tests` function (scripts/run-tests.sh:78-119) is the fallback `test-unit` takes when `cargo-nextest` is not on PATH, and it names buzz-core, buzz-auth (`--lib` only, no separate doctest step), buzz-voice, buzz-cli, buzz-db, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes and buzz-agent -- but, unlike the nextest path, names no buzz-relay invocation at all, so the fallback path does not exercise the api::admin auth-boundary regression tests the nextest path runs; two of its own comments (scripts/run-tests.sh:107-108, 117-118) say the two lists 'must stay in step', which the buzz-relay omission shows they are not."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:78-119"
      - "Justfile:384-385"
  - statement: "`.github/workflows/ci.yml`'s `unit-tests` job (named 'Unit Tests') runs `just test-unit` as its only test step, gated `if: github.event_name == 'push' || needs.changes.outputs.rust == 'true'`, where the `changes` job's `dorny/paths-filter` `rust` filter matches `crates/**`, `migrations/**`, `schema/**`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `deny.toml`, `.github/workflows/ci.yml`, `scripts/run-tests.sh`, `scripts/model-capabilities.json`, `scripts/normative-corpus.json` and `justfile`; the job installs `cargo-nextest@0.9.136` explicitly beforehand, so CI always takes the nextest path documented above, never the scripts/run-tests.sh fallback."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:95-150"
  - statement: "lefthook.yml's pre-push `rust-tests` lane runs `just test-unit`, scoped by `files: git diff --name-only origin/main...HEAD` against the glob `[\"crates/**\", \"migrations/**\", \"schema/**\", \"Cargo.toml\", \"Cargo.lock\", \"rust-toolchain.toml\", \"deny.toml\", \"scripts/run-tests.sh\", \"Justfile\"]`, so it fires only when the branch's own diff against `origin/main` touches one of those paths, independent of whether `cargo-nextest` happens to be installed in the developer's shell."
    entry_class: FACT
    evidence:
      - "lefthook.yml:98-101"
  - statement: "ADR-0020 records that this repository's testing methodology has five levels separated by infrastructure need -- unit (`just test-unit`, no infrastructure), integration (`just test`, Postgres and Redis), relay E2E, desktop E2E smoke, and desktop E2E integration -- and that every test needing a live relay is marked `#[ignore]`, so a plain `cargo test` invocation never executes E2E tests and is safe everywhere."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "Root TESTING.md states that `just test-unit` and `just test` both skip the E2E suites in `buzz-test-client`, which are marked `#[ignore]` and require a running relay, and gives `cargo test -p buzz-test-client -- --ignored` (after starting a relay) as the separate command to run them."
    entry_class: FACT
    evidence:
      - "TESTING.md:1-17"
  - statement: "Issue #1393 ('task: document verification/unit/desktop.md') is the separate, open task for the desktop unit-test level; at the recorded revision no `launchpad/docs/corpus/verification/` file of any kind exists on `origin/launchpad`, so this node is the first, and desktop's own unit-test contract is deliberately out of scope here rather than folded in."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1393 title, compared against git ls-tree of origin/launchpad's launchpad/docs/corpus tree at the recorded revision"
  - statement: "Because `test-unit`'s own comments name the absence of a `cargo test --workspace` lane as the specific failure this recipe's explicit enumeration exists to prevent, and because three of those comments give a concrete historical instance (a broken admin test that 'slipped past every gate once'), a crate's presence in the Cargo workspace is not evidence that this obligation covers its tests -- only appearing in one of `test-unit`'s own `-p` flags is."
    entry_class: INFERENCE
    evidence:
      - "Justfile:347-351"
      - "Justfile:365-370"
    confidence: 0.8
relationships:
  - type: implements
    target: corpus-template-test-contract
  - type: references
    target: corpus-standard-test-references
---

# Rust unit tests — test contract

## Purpose and boundary

This node documents one obligation: that `just test-unit` runs, without any external
infrastructure, the unit tests of a fixed and explicitly named subset of the crates in
this repository's root Cargo workspace, and that this recipe is actually wired into both
CI and the pre-push hook rather than existing only as a document. It covers **the Rust
unit-test level of this repository's root Cargo workspace only** — not the Tauri/desktop
Rust crate (`desktop/src-tauri`), which the workspace's own `Cargo.toml` excludes and
which is issue #1393's separate, not-yet-landed node; not Postgres/Redis-backed
integration tests (`just test`); and not the `#[ignore]`-gated relay or desktop E2E
suites. Those are named here only to say what this obligation is not.

## Obligation

> `just test-unit` runs, without starting any external infrastructure, the unit tests of
> a fixed set of Cargo workspace crates that the recipe names explicitly by `-p` flag —
> and only those crates — and this recipe is invoked unconditionally by CI's `unit-tests`
> job and by the pre-push `rust-tests` lefthook lane whenever a change touches a
> Rust-relevant path.

## Verifying test(s)

`test-unit` (`Justfile:316-388`) is the command-level obligation; it is not itself a test.
The concrete, currently-enumerated unit-test lanes it runs are, in the order the recipe
invokes them:

- `cargo nextest run -p buzz-core -p buzz-auth --lib` (`Justfile:321`) — every `#[test]`
  in `buzz-core`'s and `buzz-auth`'s library targets. One concrete example: `crates/buzz-core/src/kind.rs:898-899` (`mod tests`), `crates/buzz-core/src/kind.rs:902-903`
  (`fn no_duplicate_kind_values`) — asserts every value in `ALL_KINDS` is unique.
- `cargo test -p buzz-auth --doc` (`Justfile:328`) — buzz-auth's NIP-FI verifier
  `compile_fail` doctests, which `nextest` does not run.
- `cargo nextest run -p buzz-voice --lib` (`Justfile:329`).
- `cargo nextest run -p buzz-cli` (`Justfile:330`).
- `cargo nextest run -p buzz-db --lib` (`Justfile:338`) — the infra-free migrator/lint
  tests only; buzz-db's Postgres-backed tests are `#[ignore]`d and excluded by `--lib`.
- `cargo nextest run -p buzz-conformance` (`Justfile:343`) — all targets, including the
  `tests/replay_fixtures.rs` integration test, described in the recipe's own comment as
  pure in-process trace replay with no infrastructure dependency.
- `cargo nextest run -p buzz-push-gateway` (`Justfile:346`).
- `cargo nextest run -p buzz-backend-kubernetes` (`Justfile:352`).
- `cargo nextest run -p buzz-agent --lib` (`Justfile:360`).
- `cargo nextest run -p buzz-relay --lib -E 'test(/^api::admin::/) - test(=...) - test(=...)'`
  (`Justfile:384-385`) — only the `api::admin` module's tests, minus two named exclusions.
  This is the **only** buzz-relay lane in `test-unit`; `buzz-relay`'s other library tests
  (e.g. `api::media`, which needs Postgres) are not run here.

## How to run it

```bash
just test-unit
```

or, to run one lane directly (requires `cargo-nextest`, e.g. via
`. ./bin/activate-hermit`):

```bash
cargo nextest run -p buzz-core --lib
```

If `cargo-nextest` is not on `PATH`, `test-unit` falls back to
`scripts/run-tests.sh unit` (`Justfile:386-387`), whose `run_unit_tests` function
(`scripts/run-tests.sh:78-119`) covers the same nine crates named above by `cargo test`
instead of `cargo nextest run` — **except it names no `buzz-relay` invocation at all**, so
the fallback path does not exercise the `api::admin` auth-boundary tests the nextest path
runs. CI always installs `cargo-nextest@0.9.136` before this step, so this gap is only
live for a developer running `just test-unit` locally without the Hermit-pinned toolchain
active.

## Current enforcement status

**Verified**, for the crates and test lanes named above. `.github/workflows/ci.yml`'s
`unit-tests` job runs `just test-unit` unconditionally on every push and on every pull
request whose diff matches the `changes` job's `rust` path filter
(`crates/**`, `migrations/**`, `schema/**`, `Cargo.toml`, `Cargo.lock`,
`rust-toolchain.toml`, `deny.toml`, `.github/workflows/ci.yml`, `scripts/run-tests.sh`,
`scripts/model-capabilities.json`, `scripts/normative-corpus.json`, `justfile`) — this is
a real, non-`#[ignore]`d CI job, not a stub. `lefthook.yml`'s pre-push `rust-tests` lane
runs the identical command, scoped to the same class of paths, diffed against
`origin/main`, before a push leaves the developer's machine.

This status is **level-scoped, not crate-scoped**: it means the nine-and-a-partial-tenth
crates named in *Verifying test(s)* are exercised on every applicable push and pre-push.
It does **not** mean every crate in the 31-member workspace has a unit-test lane — see
*Limits*.

## Limits

- **`test-unit` is an explicit allowlist, not `cargo test --workspace`.** The recipe's own
  comments say so three times, and name a past incident (a broken admin test that
  "slipped past every gate once") as the reason the enumeration is explicit rather than
  implicit. A crate added to the workspace `members` list gains clippy/check coverage
  from CI's `rust-lint` job, but gains **no** unit-test lane at all until someone adds a
  `-p` flag for it here. This node does not audit whether every workspace crate that
  defines `#[test]` functions currently has such a flag — only that the nine named above
  do.
- **The `buzz-relay` lane is a name-filtered subset, not the crate's full `--lib` suite.**
  Only `api::admin::*` tests run here, minus two explicitly excluded ones; `buzz-relay`'s
  other non-`#[ignore]`d library tests (for example under `api::media`, which needs
  Postgres) are covered by neither this recipe nor, per its own comment trail, any other
  enumerated CI lane this node's authors traced.
- **The nextest and fallback paths diverge.** `scripts/run-tests.sh`'s `run_unit_tests`
  claims (in its own comments) to mirror `test-unit`'s crate list, but it omits
  `buzz-relay` entirely — a real gap between the two paths, not merely a difference in
  test runner.
- **A green run of `test-unit` says nothing about `desktop/src-tauri`, integration tests,
  or `#[ignore]`d E2E tests.** Those are excluded by design (see *Purpose and boundary*)
  and are not partially covered by this obligation.
- **This node does not verify that the enumerated crates' tests currently pass.** It
  documents which lanes exist, how they are invoked, and where they run, per
  `corpus-standard-test-references`'s distinction between a test's existence and a test's
  observed result. Confirming today's pass/fail state would require actually running
  `just test-unit` at the recorded revision, which was not done as part of authoring this
  node.

## Scope and omissions

**This node covers** the `test-unit` recipe as the definition of this repository's Rust
unit-test level for the root Cargo workspace: which crates and test subsets it currently
names, how to invoke it, and how CI and the pre-push hook enforce it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The Tauri/desktop Rust crate's own unit-test contract | Issue #1393 (`verification/unit/desktop.md`, not yet landed) |
| Postgres/Redis-backed integration tests (`just test`) | Not yet documented as a corpus node at the recorded revision |
| Relay and desktop E2E suites (`#[ignore]`-gated) | `TESTING.md`; not yet a corpus node at the recorded revision |
| General guidance on writing Rust tests in this repository | `TESTING.md`, `crates/buzz-cli/TESTING.md` |
| How any corpus node should cite a test as evidence, generally | `corpus-standard-test-references` |
| Whether each of the nine enumerated crates' tests currently passes | Not verified by this node — see *Limits* |

**Expected but not verified when this node was written:**

- **Whether every crate under `crates/*` that defines `#[test]` functions is named by a
  `-p` flag in `test-unit` was not exhaustively audited.** This node verified the nine (plus
  the `buzz-relay` subset) that the recipe names today, and verified — from the recipe's
  own comments and from `scripts/run-tests.sh`'s parallel list — that the enumeration is
  known to be partial by design. It did not enumerate every crate under `crates/**` and
  check each one's own test files for a matching, missing `-p` flag.
- **Whether `test-unit`'s nine-plus-one lanes currently pass** was not established by
  running them; only their existence, non-`#[ignore]`d status (for the one example test
  read in full) and wiring into CI/pre-push were checked, per
  `corpus-standard-test-references`'s existence-versus-result distinction.
