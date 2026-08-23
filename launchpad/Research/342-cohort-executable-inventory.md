---
description: The inventory of cohort-owned executables under launchpad/ and which have tests that run in CI — 32 test artifacts exist, 6 run, and the 14 shell test scripts and review-agent's 5 unittest suites are invisible to automation.
tags: [testing, ci, inventory, criterion-3, coverage, research, issue-342]
---

# What is the complete inventory of cohort-owned executables, and which have tests in CI?

## Finding

**32 test artifacts exist under `launchpad/`. Six of them run in CI.**

Criterion 3 of #290 quantifies over "every cohort-owned executable", and this is the denominator
it was missing: **44 production Python modules, 12 production shell scripts, and 34 `.yml` files**,
guarded by **18 Python test files and 14 `test-*.sh` scripts**. CI invokes exactly two things — a
`unittest discover` over `launchpad/scripts` and `review-agent/run_controls.py` — which between
them cover 6 of the 32.

The two findings worth acting on are both things nobody has named:

1. **13 `test-*.sh` scripts in `launchpad/scripts/` are run by no workflow at all.** This is an
   entire class of cohort-owned tests that is invisible to automation, and it is larger than the
   `project-intelligence` gap #290 does name.
2. **`launchpad/review-agent/`'s five `test_*.py` suites do not run in CI either.** Its *containment
   controls* do, via a hardcoded list, and the two are easy to confuse — I confused them myself in
   an earlier sweep of this PRD.

## Inventory

Tracked files only, from `git ls-files`:

```
$ git ls-files launchpad | ... | awk '{print $1}' | sort | uniq -c
  62 py
  26 sh
  34 yaml
```

Split into production and test, per directory:

| Directory | Production `.py` | Test `.py` | Shell |
|---|---|---|---|
| `launchpad/scripts` | 11 | 6 | 16 (of which **13** are `test-*.sh`) |
| `launchpad/review-agent` | 24 | 5 | — |
| `launchpad/project-intelligence` | 6 | 6 | — |
| `launchpad/agents` | 3 | 1 | — |
| `launchpad/deploy` | — | — | 9 (1 is `test-run-guard.sh`) |
| `launchpad/sync-labels.sh` | — | — | 1 |

**Totals: 44 production Python modules, 18 Python test files, 26 shell scripts of which 13 are
tests.**

## What CI actually invokes

Every `run:` line across all five `launchpad-*.yml` workflows:

```
--- launchpad-adr-check.yml
python3 -m unittest discover -s launchpad/scripts
python3 launchpad/scripts/adr_boundary_check.py .
--- launchpad-issue-check.yml
(inline python heredoc only - no test invocation)
--- launchpad-pr-check.yml
python3 launchpad/scripts/pr_body_check.py
python3 -m unittest discover -s launchpad/scripts -t launchpad/scripts -v
python3 launchpad/scripts/mutation_harness.py
--- launchpad-review-agent-controls.yml
pip install pyyaml
python3 run_controls.py
--- launchpad-security-audit.yml
python3 -m unittest discover -s launchpad/scripts -p "test_security_audit*.py"
python3 launchpad/scripts/security_audit.py .
```

That is the whole of it. Note the three `discover` invocations differ — `adr-check` has no `-t`,
`security-audit` narrows to `-p "test_security_audit*.py"`, and only `pr-check` runs the full set
with `-t launchpad/scripts -v`. So the complete `launchpad/scripts` suite runs on pull requests via
one workflow, and narrower subsets run via the other two.

## The coverage table

| Test artifact | Count | Runs in CI? | Evidence |
|---|---|---|---|
| `launchpad/scripts/test_*.py` | 6 | **yes** | `unittest discover -s launchpad/scripts` in `launchpad-pr-check.yml` |
| `launchpad/scripts/test-*.sh` | **13** | **no** | no workflow references any of them |
| `launchpad/review-agent/test_*.py` | 5 | **no** | see below |
| `launchpad/project-intelligence/test_*.py` | 6 | **no** | no workflow mentions the directory (#329 — they pass) |
| `launchpad/agents/test_*.py` | 1 | **no** | no workflow mentions the directory (#270) |
| `launchpad/deploy/test-run-guard.sh` | 1 | **no** | only `docker.yml:142` mentions `launchpad/deploy`, in a comment |

**6 of 32.**

### Why review-agent's suites do not run, though something of its does

`launchpad-review-agent-controls.yml` runs `python3 run_controls.py`, whose docstring says *"One
entry point, so CI has one thing to invoke."* But its target list is hardcoded and contains no test
module:

```python
CONTROLS = [
    ("check_contract.py", False),
    ("check_step2.py", False),
    ("check_step3.py", True),
    ("check_step45.py", False),
    ("check_step6.py", True),
    ("suite.py", False),
    ("check_step8.py", False),
    ("check_step9.py", False),
    ("check_step11.py", False),
    ("check_invariants.py", False),
    ("check_mutations.py", False),
    ("check_flag_guard.py", False),
    ("check_fetch_states.py", False),
]
```

Thirteen entries, none of them `test_findings.py`, `test_fixtures.py`, `test_injection_clause.py`,
`test_recordings.py` or `test_run_dimensions.py`. The one entry that might have covered them —
`suite.py` — is its own thing: a 35-case containment control suite whose docstring describes
enumerating payloads through entry points, and which references none of the five test modules.

So the review agent has **strong CI coverage of its containment contract and none of its unit
tests**. Both are real; they are not substitutes, and the naming makes them easy to conflate.

## What this changes for #290

**Criterion 3's scope is roughly four times what the PRD describes.** #290 names
`launchpad/project-intelligence/` (six suites) and `launchpad/agents/` (#270) as the gap. The real
set is 26 unrun test artifacts, and the largest single block is the **14 shell test scripts**, which
the PRD does not mention at all.

**The PRD's evidence needs two corrections.** It says CI "invokes the cohort's *checkers* ... but
never runs their test suites". For `launchpad/scripts` that is false — the full Python suite runs on
every pull request, plus `mutation_harness.py`. And my own earlier sweep comment on #290 said the
review agent's controls run, in a context that implied its suites do; that was imprecise, and this
document is the correction.

**A cheap sequencing observation.** The 14 shell tests and the 6 project-intelligence suites are
probably the two cheapest wins, for different reasons: the shell tests need no interpreter beyond
bash, and #329 established the project-intelligence suites already pass with no dependencies. The
`agents` suite is the expensive one (#270 documents a missing package and a `PATH`-dependent test).

**Criterion 8 gains an entry with a number.** "13 cohort shell test scripts and 12 cohort Python
test suites exist and are not run by automation" is a nameable piece of non-coverage, and it is
checkable against this table.

## Confidence and what was not checked

**High confidence:** the file counts (`git ls-files`, all local), the complete list of `run:` lines
across the five cohort workflows, the `CONTROLS` list, and that `suite.py` references none of the
five test modules.

**Not checked:**

- **Whether the 13 `test-*.sh` scripts pass.** I inventoried them; I did not run one. They may be
  green, stale, or broken, and that changes the cost of wiring them in considerably. Named as the
  obvious next question rather than assumed either way.
- **Whether `unittest discover -s launchpad/scripts` actually collects all six** Python test files.
  It should by naming convention, but I did not run it and read the count — and #270 records that an
  empty discovery can read as a pass, which is exactly this hazard.
- **Whether the 13 review-agent `check_*.py` controls subsume what the five `test_*.py` suites
  assert.** They might overlap substantially. I established they are different invocations, not
  that the coverage is disjoint.
- **The 34 `.yml` files** were counted but not classified. Some are deploy configuration rather than
  executables, and "cohort-owned executable" is genuinely arguable at that boundary — as it is for
  `bin/lefthook` (a cohort divergence under ADR-0017, executable, outside `launchpad/`) and for the
  five ADR-0005 deployment files (cohort-owned, not executable). This document counts what is under
  `launchpad/`; it does not settle the category.
- **Upstream's `scripts/` directory** is excluded. The fork depends on several of those scripts, and
  whether they count as cohort-owned when the fork's CI relies on them is not addressed here.
