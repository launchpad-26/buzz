---
description: Which ci.yml jobs actually run on a pull request targeting launchpad — change detection works, but every cache-save step on this fork is dead code, so the pipeline is permanently cold.
tags: [testing, ci, github-actions, paths-filter, caching, cost, research, issue-328]
---

# Which CI jobs actually run on a pull request targeting `launchpad`?

## Finding

**Change detection works. Caching does not.**

Two answers, and the second is the one that matters:

1. **`ci.yml` has never run on a `push` event in this fork**, so all 23 of its
   `github.event_name == 'push'` conditions are dead. Six of those guard **cache-save** steps,
   and a further eight `rust-cache` steps are gated `save-if: github.event_name != 'pull_request'`,
   which is also always false here. **This fork never writes a CI cache.** Every pull request
   builds cold, and always will, because the only event that would warm the cache never fires.
2. **The `rust` filter is a master switch.** It gates 14 of the 18 jobs. Only `web` and `mobile`
   are independent of it, and `Cargo.lock` is in the `rust` filter's path list — so almost any
   dependency change runs almost the whole pipeline.

Change detection itself is sound: a docs-only pull request runs 2 jobs in under a minute. The
~28–32 minute figure #290 quotes is real but it is a **permanently cold-cache** number, not a
steady state that will improve.

## 1. No `push` event has ever run this workflow here

`ci.yml` triggers on `push` only for two branches (`.github/workflows/ci.yml:2-5`):

```yaml
on:
  push:
    branches: [main, release]
  pull_request:
```

This fork's integration branch is `launchpad`, which is in neither list.

```
$ gh run list --workflow ci.yml --event push --limit 10
(no output)

$ gh run list --workflow ci.yml --limit 100 --json event --jq '[.[].event]|group_by(.)|map({event:.[0],count:length})'
[{"count":100,"event":"pull_request"}]
```

100 of the last 100 runs are `pull_request`; a filtered query for `push` returns nothing.

### What that kills

Six step-level conditions, every one of them a cache write:

| Line | Step |
|---|---|
| 228 | Save pnpm store cache |
| 275 | Save Playwright browser cache (smoke, shard 1) |
| 385 | Save relay artifacts cache |
| 458 | Save Playwright browser cache (integration, shard 1) |
| 574 | Save pnpm store cache |
| 844 | Save pnpm store cache |

Plus eight `Swatinem/rust-cache` steps (lines 112, 134, 159, 355, 774, 966, 1010, 1084), each:

```yaml
          save-if: ${{ github.event_name != 'pull_request' }}
```

false on every run this fork performs. And sccache is read-only except for one hardcoded
upstream pull request number that will never match here (line 331):

```yaml
      SCCACHE_GHA_RW_MODE: ${{ (github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.pull_request.number == 5224)) && 'READ_WRITE' || 'READ_ONLY' }}
```

The restore steps still run, but nothing ever populated what they restore from, so they miss.
This is upstream's design working as intended *upstream* — where `push` to `main` warms the cache
and pull requests read it. Fork the repository without `main`, and only the reading half survives.

## 2. What actually gates each job

Extracted from `ci.yml`. There are **18** jobs, not the 19 quoted in #290 and ADR-0020 — a naive
grep counts `push:` under `on:`.

| Job | Gate |
|---|---|
| `changes` | always |
| `dead-token-guard` | always |
| `rust-lint` | `rust` or `desktop-rust` |
| `unit-tests` | `rust` |
| `backend-integration` | `rust` |
| `relay-e2e` | `rust` |
| `security` | `rust` |
| `server-cross-compile` | `rust` |
| `windows-rust` | `rust` or `desktop-rust` |
| `desktop-core` | `desktop` or `desktop-rust` or **`rust`** |
| `desktop-smoke-e2e` | `desktop` or `desktop-rust` or **`rust`** |
| `desktop` (gate) | `desktop` or `desktop-rust` or **`rust`** |
| `desktop-e2e-relay` | `desktop` or `desktop-rust` or **`rust`** |
| `desktop-e2e-integration-shard` | `desktop` or `desktop-rust` or **`rust`** |
| `desktop-e2e-integration` (gate) | `desktop` or `desktop-rust` or **`rust`** |
| `desktop-build-macos` | `desktop` or `desktop-rust` or **`rust`** |
| `web` | `web` only |
| `mobile` | `mobile` only |

Every one also has `github.event_name == 'push' ||` in front, which is permanently false here.

**`rust` alone triggers 14 of 18.** The `desktop` filter never independently decides anything —
every job that consults it also accepts `rust`. And the `rust` filter matches more than crates:

```yaml
            rust:
              - 'crates/**'
              - 'migrations/**'
              - 'schema/**'
              - 'Cargo.toml'
              - 'Cargo.lock'
              - 'rust-toolchain.toml'
              - 'deny.toml'
              - '.github/workflows/ci.yml'
              - 'scripts/run-tests.sh'
              - 'scripts/model-capabilities.json'
              - 'scripts/normative-corpus.json'
              - 'justfile'
```

Touch `Cargo.lock`, the `justfile`, or `ci.yml` itself, and the desktop E2E shards, the macOS
build and the Windows Rust job all run.

## 3. Observed behaviour

**Docs-only pull request** — 2 jobs, under a minute:

```
branch: research/319-desktop-distribution-path
elapsed: 0 min
ran: Dead Token Reference Guard, Detect Changed Paths
skipped: 16 jobs
```

Reproduced on a second docs branch (`research/358-required-checks`) with an identical result.
Change detection is doing its job.

**Code-touching pull request** — run `32473521557`, 32m 35s (10:38:03Z → 11:10:38Z), 21 of 23
job instances ran, only `Web` and `Mobile` skipped. A second code-touching run measured 24 min.
So the working range on this fork is **~24–32 minutes cold**, and under a minute for docs.

## 4. A trap worth knowing: the filter's "changed files" is not GitHub's

Run `32473521557` is on branch `docs/adr-0018-relay-vps-specification`, and its pull request
(#268) shows **one changed file**:

```
$ gh pr view 268 --json files
101+ 0- launchpad/decisions/ADR-0018-cohort-relay-vps-specification.md
```

Yet the whole Rust and desktop pipeline ran. The `changes` job log says why:

```
GitHub token is not available - changes will be detected using git diff
Change detection f36d10f9c..e619f8fd8
[command] git diff --no-renames --name-status -z f36d10f9c..e619f8fd8
M Cargo.lock
A launchpad/agents/project-pack.py
A launchpad/agents/test_project_pack.py
A launchpad/decisions/ADR-0018-cohort-relay-vps-specification.md
Detected 4 changed files
Filter rust = true
  Matching files:
  Cargo.lock [modified]
Filter desktop = false
Filter desktop-rust = false
Filter web = false
Filter mobile = false
Changes output set to ["rust"]
```

Four files, not one. `Cargo.lock` matched `rust`, and 14 jobs followed.

The action is configured with `token: ''` (`ci.yml:37`), so it diffs with git rather than asking
the API. The base it used, `f36d10f9c`, is an *older* `launchpad` tip — `launchpad` advanced
(`dba2e66a0`, #239 STEP 2, landed in between) and the extra three files are that advance, not the
pull request's own work.

The consequence is that a pull request's job set depends on **how far the base branch moved since
the pull request was opened**, not only on what the pull request changed. It fails safe — the
error is running too much, never too little — but it means "why did my docs PR run the E2E
shards?" has a real answer, and cost attribution per pull request is noisier than it looks.

## What this changes for #290

**Criterion 1** should describe change detection as it behaves *here*: a five-filter
`dorny/paths-filter` gate where `rust` is effectively a master switch, `desktop` is redundant
against it, and only `web` and `mobile` narrow anything on their own. And the document should not
carry the "19 CI jobs" figure — it is 18.

**Criterion 5** gains a concrete constraint. A required check must name a status context that is
actually published, and on this fork the publishing set depends on the paths-filter. A check
required on, say, `Mobile` would sit pending forever on every pull request that does not touch
`mobile/`, which is the trap `launchpad-adr-check.yml`'s own header comment (line 6) records the
cohort stepping in once already. The safe contexts to require are the two unconditional jobs,
`changes` and `dead-token-guard`.

**A cost finding nobody was looking for.** The fork pays full cold-build cost on every pull
request and cannot stop, because caches are only written on `push` to `main`/`release` and this
fork has neither branch. Making `push` to `launchpad` a trigger would fix it, but that is a change
to an upstream file and therefore an ADR under `launchpad/AGENTS.md` §3, not a patch.

## Confidence and what was not checked

**High confidence:** the absence of `push` runs (queried directly), the gate table (extracted
from `ci.yml`), the dead cache-save steps (each read at its line), the docs-only and
code-touching job sets and durations (read from real runs), and the paths-filter log quoted above.

**Not checked:**

- **Whether the cache restores actually miss.** It follows from nothing ever saving, but I did not
  open a restore step's log to observe a miss. That is the one measurement that would turn "the
  pipeline is cold" from inference into observation.
- **The stale-base mechanism was diagnosed from one run.** The log for `32473521557` is
  unambiguous about what happened *there*; the general rule is inferred from it plus how
  `pull_request.base.sha` behaves, not from a second reproduction.
- **Duration sampling is thin** — two code-touching runs (32 min, 24 min). Neither was
  cache-warm, so there is no comparison point.
- **Whether any status check is currently required** — not re-checked here; ADR-0019 records
  zero, and #358 is looking at it separately.
- I did not audit the other 22 workflow files. Everything here is about `ci.yml`.
