---
description: What it takes to run the six launchpad/project-intelligence test suites green — they pass with no third-party packages, but one of them is not hermetic and shells out to a real cargo test.
tags: [testing, ci, python, project-intelligence, hermeticity, research, issue-329]
---

# What does it take to run the six `project-intelligence` suites green?

## Finding

**They already pass. 114 tests, no third-party packages, on both Python 3.11 and 3.14.**

The obstacle to wiring them into CI is not that they are broken — it is that **one of them is not
hermetic**. `test_investigator.py` deliberately shells out to real commands against the real
repository, including a real **`cargo test -p buzz-core`**. That single test is why the suite takes
~100 seconds locally, and it means a CI job running these suites needs the **Rust toolchain**, not
just Python.

Read together with #328 — this fork never writes a CI cache — that test would face a cold cargo
build on every pull request.

## The runs

Both invocations are from a clean checkout at `launchpad` tip with no packages installed.

**Python 3.11**, the version CI already pins in `launchpad-review-agent-controls.yml:36`:

```
$ python3.11 -m unittest discover -s . -p "test_*.py"
...........................................[EXECUTE] run_command: echo hi
.[EXECUTE] run_test: cargo test -p buzz-core kind::tests::
......................................................................
----------------------------------------------------------------------
Ran 114 tests in 105.038s

OK
```

**Python 3.14.6**, this machine's default:

```
$ python3 -m unittest discover -s . -p "test_*.py"
----------------------------------------------------------------------
Ran 114 tests in 143.097s

OK
```

Per suite, run individually:

| Suite | Tests | Time |
|---|---|---|
| `test_symbol` | 2 | 0.000s |
| `test_graph` | 14 | 0.001s |
| `test_indexer` | 7 | 0.001s |
| `test_memory` | 33 | 0.002s |
| `test_semantic_index` | 27 | 0.006s |
| `test_investigator` | **31** | **96.794s** |

Five of the six suites are effectively instantaneous — 83 tests in under 10 milliseconds combined.
**All the cost, and all the risk, is in `test_investigator`.**

## What they require

**Nothing installed.** Every import across the six modules and their suites resolves to the
standard library or a sibling module:

```
__future__ collections dataclasses json math pathlib re subprocess sys time typing unittest uuid
```

plus `graph`, `indexer`, `investigator`, `memory`, `semantic_index`, `symbol`. There is no
`requirements.txt` or `pyproject.toml` under `launchpad/project-intelligence/`, and none is needed.
This is a real difference from `launchpad/agents/`, where #270 records `test_goose_config.py`
failing at import on a missing `ruamel.yaml`.

**No network.** No `urllib`, `requests` or `http` import appears anywhere in the directory.

**An intact repository checkout.** `investigator.py:34` resolves its root by walking up the tree:

```python
REPO_ROOT = Path(__file__).resolve().parents[2]
```

so the suites must run from inside a real checkout, not a copied-out directory.

**Real `git` and `grep`.** `test_investigator.py` contains **zero** mocks or patches:

```
$ grep -cn "mock\|patch" test_investigator.py
0
```

It calls `subprocess.run` and `subprocess.Popen` directly and lets them execute.

**The Rust toolchain.** This is the one that matters:

```python
# test_investigator.py:238-239
def test_run_test_surfaces_execute_flag_and_runs_a_real_fast_test(self) -> None:
    result = investigator.run_test("buzz-core", "kind::tests::")
```

The test's own name says it runs a real test, and the `[EXECUTE] run_test: cargo test -p buzz-core
kind::tests::` line in the output above confirms it does. It is "fast" here only because this
worktree has a warm `target/` directory of 6.7 GB.

**`rql` is *not* required.** `investigator.py` invokes `rql query` in several places
(lines 171, 222), but `rql` is absent from this machine and all 31 tests still pass:

```
$ command -v rql
rql NOT on PATH
```

The suite's own comment explains why (`test_investigator.py:153`): *"Validation runs before any
subprocess call, so these are hermetic"* — the injection-rejection tests assert that a malformed
argument is refused before anything is executed, so they never reach `rql`.

## One inconsistency worth recording

`test_investigator.py:252` hardcodes the interpreter for a subprocess:

```python
["python3", "-c", "import investigator; investigator.run_command(['sleep', '2'])"]
```

So running the suite under `python3.11` still spawns whatever `python3` resolves to — 3.14.6 on
this machine. The suite passed both ways, so nothing is broken, but the interpreter under test and
the interpreter in the subprocess are not necessarily the same one. A CI job that pins a Python
version should be aware it is only pinning half of it.

## What this changes for #290

**Criterion 3 is cheaper than #290 implies for this directory, with one caveat.** The PRD groups
`project-intelligence` with `agents` as "the cohort's Python suites do not run in CI". For
`agents` that is a real obstacle (#270 documents a missing package and a `PATH`-dependent test).
For `project-intelligence` there is no obstacle at all at the Python level: a job that runs
`python3 -m unittest discover` would be green today.

**The caveat is the cargo dependency, and it is not small.** A workflow running these suites needs
Rust available, and on this fork it would build cold every time — nothing warms the cache (#328).
For scale: a cold `just clippy` on this workspace took 593 seconds. `cargo test -p buzz-core
kind::tests::` is narrower than that, but it is a cold dependency build, not a no-op.

Three options exist and this document does not choose between them: install Rust in the workflow
and accept the cost; split `test_investigator`'s executing tests out so the hermetic 83 can run in
a fast Python-only job; or mark the cargo test as opt-in the way upstream marks E2E with
`#[ignore]`. The third would sit closest to the methodology ADR-0020 adopts.

**A note for criterion 8.** `test_investigator` is a deliberate non-hermetic test — its comments
show the choice was made knowingly, to prove that an EXECUTE-flagged tool really executes. That is
worth recording as a choice rather than being discovered later as an oversight.

## Confidence and what was not checked

**High confidence:** the pass results and timings (both runs pasted above), the absence of
third-party dependencies (import scan plus a clean run with nothing installed), the cargo
invocation (visible in the output and in the source at line 239), and `rql` being unnecessary.

**Not checked:**

- **Whether they pass on Linux.** Both runs were on Intel macOS. Nothing here is obviously
  platform-specific, but `subprocess` behaviour and path handling were not exercised on the
  `ubuntu-latest` runner CI would actually use.
- **Whether they pass with a cold `target/`.** The cargo test was fast because this worktree has a
  warm 6.7 GB `target/`. I did not measure it cold, so the CI cost is unquantified — I can say it
  is a cold build, not how long it takes.
- **What the suites cover.** This document is only about whether they run. Coverage is #330.
- **Repeat runs.** Each suite ran once per interpreter; nothing here speaks to flakiness, and
  `test_investigator` spawning real processes and a `sleep 2` is the kind of test that can be
  timing-sensitive.
- **The host was at 99% disk (4.3 GiB free)** throughout, and a cargo test in a parallel lane died
  with "No space left on device". These suites passed regardless, but the environment was not clean.
