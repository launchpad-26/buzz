---
description: The inventory of cohort-owned executables under launchpad/ and which have tests that run in CI — 36 test artifacts exist, 9 run, and the 14 shell test scripts and review-agent's 7 unittest suites are invisible to automation.
tags: [testing, ci, inventory, criterion-3, coverage, research, issue-342]
---

# What is the complete inventory of cohort-owned executables, and which have tests in CI?

**All counts in this document are as of commit
`132f921ace6be6d391c03e134b304ddea3ecccf0`** (the `launchpad` branch tip merged into this
PR on 2026-08-24). Earlier revisions of this note counted 31, then 32 artifacts at
`f75085d5c`; the base has since gained a sixth workflow
(`.github/workflows/launchpad-agents-tests.yml`), one `launchpad/scripts` suite
(`test_pr_review_batch.py`), two `launchpad/review-agent` suites
(`test_run_adjudication.py`, `test_verdicts.py`) and one `launchpad/agents` suite
(`test_project_pack.py`), which changes both the denominator and the numerator. Every
figure below was re-derived at the pinned commit with the commands shown.

## Finding

**36 test artifacts exist under `launchpad/`. Nine of them run in CI.**

Criterion 3 of #290 quantifies over "every cohort-owned executable", and this is the denominator
it was missing: **48 production Python modules, 12 production shell scripts, one extensionless
Bash entry point (`deploy/archived/deploy`), and 34 `.yml` files** (6 of them Ansible playbooks —
classified in the appendix), guarded by **22 Python test files and 14 `test-*.sh` scripts**. CI
invokes exactly three things — a `unittest discover` over `launchpad/scripts`, a `unittest
discover` over `launchpad/agents` (new since `8f4293543`), and
`review-agent/run_controls.py` — which between them cover 9 of the 36.

The two findings worth acting on are both things nobody has named:

1. **All 14 `test-*.sh` scripts (13 in `launchpad/scripts/`, 1 in `launchpad/deploy/`) are run by
   no workflow at all.** This is an entire class of cohort-owned tests that is invisible to
   automation, and it is larger than the `project-intelligence` gap #290 does name.
2. **`launchpad/review-agent/`'s seven `test_*.py` suites do not run in CI either.** Its *containment
   controls* do, via a hardcoded list, and the two are easy to confuse — I confused them myself in
   an earlier sweep of this PRD.

## Inventory

Tracked files only, from `git ls-files` at `132f921ac`:

```
$ git ls-files launchpad | grep -E '\.(py|sh|yml|yaml)$' | sed 's/.*\.//' | sort | uniq -c
  70 py
  26 sh
  34 yml
```

(All 34 are `.yml`; the repository contains no `.yaml` file under `launchpad/`.) Extension
counting alone misses executables with no extension, so the appendix below re-derives the
inventory from git file mode and shebang as well — that is what surfaces
`deploy/archived/deploy`.

Split into production and test, per directory:

| Directory | Production `.py` | Test `.py` | Shell |
|---|---|---|---|
| `launchpad/scripts` | 12 | 7 | 16 (of which **13** are `test-*.sh`, plus 2 fixtures in `testdata/`) |
| `launchpad/review-agent` | 26 | 7 | — |
| `launchpad/project-intelligence` | 6 | 6 | — |
| `launchpad/agents` | 4 | 2 | — |
| `launchpad/deploy` | — | — | 9 (1 is `test-run-guard.sh`) + 1 extensionless (`archived/deploy`) |
| `launchpad/sync-labels.sh` | — | — | 1 |

**Totals: 48 production Python modules, 22 Python test files, 26 shell scripts of which 14 are
tests, and one extensionless Bash entry point.**

## What CI actually invokes

Every test-relevant `run:` line across all six `launchpad-*.yml` workflows:

```
--- launchpad-adr-check.yml
python3 -m unittest discover -s launchpad/scripts
python3 launchpad/scripts/adr_boundary_check.py .
--- launchpad-agents-tests.yml
pip install -r launchpad/agents/requirements.txt
python3 - <<'PY'   # guard: fails if discover collects zero test CASES
python3 -m unittest discover -s launchpad/agents -p "test_*.py" -v
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

That is the whole of it. Note the four `discover` invocations differ — `adr-check` has no `-t`,
`security-audit` narrows to `-p "test_security_audit*.py"`, `pr-check` runs the full
`launchpad/scripts` set with `-t launchpad/scripts -v`, and `agents-tests` runs
`launchpad/agents` behind an explicit case-count guard that fails the job if discovery collects
zero test cases (the empty-discovery hazard this note's first revision flagged, closed for that
directory only).

## The coverage table

| Test artifact | Count | Runs in CI? | Evidence |
|---|---|---|---|
| `launchpad/scripts/test_*.py` | 7 | **yes** | `unittest discover -s launchpad/scripts` in `launchpad-pr-check.yml` |
| `launchpad/scripts/test-*.sh` | **13** | **no** | no workflow references any of them |
| `launchpad/review-agent/test_*.py` | 7 | **no** | see below |
| `launchpad/project-intelligence/test_*.py` | 6 | **no** | no workflow mentions the directory (#329 — they pass) |
| `launchpad/agents/test_*.py` | 2 | **yes** | `unittest discover -s launchpad/agents` in `launchpad-agents-tests.yml` (closed #270's gap) |
| `launchpad/deploy/test-run-guard.sh` | 1 | **no** | only `docker.yml:142` mentions `launchpad/deploy`, in a comment |

**9 of 36.**

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
`test_recordings.py`, `test_run_adjudication.py`, `test_run_dimensions.py` or `test_verdicts.py`.
The one entry that might have covered them — `suite.py` — is its own thing: a 35-case containment
control suite whose docstring describes enumerating payloads through entry points, and which
references none of the seven test modules.

So the review agent has **strong CI coverage of its containment contract and none of its unit
tests**. Both are real; they are not substitutes, and the naming makes them easy to conflate.

## What this changes for #290

**Criterion 3's scope is roughly four times what the PRD describes.** #290 names
`launchpad/project-intelligence/` (six suites) and `launchpad/agents/` (#270) as the gap. The real
set is 27 unrun test artifacts, and the largest single block is the **14 shell test scripts**, which
the PRD does not mention at all. The `launchpad/agents` half of the PRD's named gap has meanwhile
been closed by `launchpad-agents-tests.yml` — so the PRD's named gap and the actual gap now
barely overlap.

**The PRD's evidence needs two corrections.** It says CI "invokes the cohort's *checkers* ... but
never runs their test suites". For `launchpad/scripts` and `launchpad/agents` that is false — both
full suites run on every pull request (plus `mutation_harness.py` for scripts). And my own earlier
sweep comment on #290 said the review agent's controls run, in a context that implied its suites
do; that was imprecise, and this document is the correction.

**A cheap sequencing observation.** The 14 shell tests and the 6 project-intelligence suites are
probably the two cheapest wins, for different reasons: the shell tests need no interpreter beyond
bash, and #329 established the project-intelligence suites already pass with no dependencies. The
`agents` wiring that #270 documented as expensive has since landed, with a case-count guard worth
copying for any future discover-based job.

**Criterion 8 gains an entry with a number.** "14 cohort shell test scripts and 13 cohort Python
test suites (review-agent's 7 and project-intelligence's 6) exist and are not run by automation"
is a nameable piece of non-coverage — 27 unrun artifacts — and it is checkable against this table.

## Appendix: per-executable inventory

Issue #342 asks for every executable enumerated mechanically. Method, reproducible at
`132f921ac`: a row for every tracked file under `launchpad/` that has extension `.py` or `.sh`,
**or** git mode `100755`, **or** is an Ansible playbook (`.yml` under `ansible/playbooks/`).
Derivation: `git ls-files -s launchpad` for modes and paths; `head -c2` for shebangs. "Test
(name-match)" pairs `x.py` with `test_x.py` and `x.sh` with `test-x.sh` in the same directory
(plus `deploy/run.sh` ↔ `test-run-guard.sh`, which the guard's own header states as its target);
a "none" there means no *dedicated named* test — directory-level suites and controls are recorded
in the CI column, not silently credited.

¹ review-agent production modules are exercised by the containment controls and (for some) by
directory-level suites, but have no name-matched unit test; the seven `test_*.py` suites that do
exist cover `findings.py`, `run_adjudication.py`, `run_dimensions.py`, `verdicts.py` plus three
fixture/injection/recording concerns without a same-named production file.
² `run_controls.py` is itself the CI entry point for the controls; nothing tests it.

| Path | Enumerated by | Role | Test (name-match) | CI workflow running that test |
|---|---|---|---|---|
| `agents/goose_config.py` | .py+shebang | production | yes — `test_goose_config.py` | agents-tests (discover) |
| `agents/project-pack.py` | .py+shebang | production | none found by name-match | none |
| `agents/test_goose_config.py` | .py+shebang | test artifact | — (is itself a test) | agents-tests (discover) |
| `agents/test_project_pack.py` | .py+shebang | test artifact | — (is itself a test) | agents-tests (discover) |
| `agents/the-professor/tools/check_server.py` | .py+mode 755 | production | none found by name-match | none |
| `agents/the-professor/tools/server.py` | .py+mode 755 | production | none found by name-match | none |
| `deploy/archived/ansible/playbooks/04-docker.yml` | playbook | production | none found by name-match | none |
| `deploy/archived/ansible/playbooks/05-bundle.yml` | playbook | production | none found by name-match | none |
| `deploy/archived/ansible/playbooks/06-config.yml` | playbook | production | none found by name-match | none |
| `deploy/archived/ansible/playbooks/07-up.yml` | playbook | production | none found by name-match | none |
| `deploy/archived/ansible/playbooks/09-members.yml` | playbook | production | none found by name-match | none |
| `deploy/archived/ansible/playbooks/10-harden.yml` | playbook | production | none found by name-match | none |
| `deploy/archived/deploy` | mode 755 | production | none found by name-match | none |
| `deploy/archived/scripts/resolve-image-tag.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/archived/scripts/verify.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/archived/virtual-box/build-vps-clone.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/archived/virtual-box/fetch-image.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/archived/virtual-box/host-dns.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/archived/virtual-box/preflight.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/archived/virtual-box/resize-vps-clone.sh` | .sh+mode 755 | production | none found by name-match | none |
| `deploy/run.sh` | .sh+mode 755 | production | yes — `test-run-guard.sh` | none |
| `deploy/test-run-guard.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `project-intelligence/graph.py` | .py | production | yes — `test_graph.py` | none |
| `project-intelligence/indexer.py` | .py | production | yes — `test_indexer.py` | none |
| `project-intelligence/investigator.py` | .py | production | yes — `test_investigator.py` | none |
| `project-intelligence/memory.py` | .py | production | yes — `test_memory.py` | none |
| `project-intelligence/semantic_index.py` | .py | production | yes — `test_semantic_index.py` | none |
| `project-intelligence/symbol.py` | .py | production | yes — `test_symbol.py` | none |
| `project-intelligence/test_graph.py` | .py | test artifact | — (is itself a test) | none |
| `project-intelligence/test_indexer.py` | .py | test artifact | — (is itself a test) | none |
| `project-intelligence/test_investigator.py` | .py | test artifact | — (is itself a test) | none |
| `project-intelligence/test_memory.py` | .py | test artifact | — (is itself a test) | none |
| `project-intelligence/test_semantic_index.py` | .py | test artifact | — (is itself a test) | none |
| `project-intelligence/test_symbol.py` | .py | test artifact | — (is itself a test) | none |
| `review-agent/check_contract.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_fetch_states.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_flag_guard.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_invariants.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_mutations.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step11.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step2.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step3.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step45.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step6.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step8.py` | .py | production | none by name-match ¹ | none |
| `review-agent/check_step9.py` | .py | production | none by name-match ¹ | none |
| `review-agent/contain.py` | .py | production | none by name-match ¹ | none |
| `review-agent/corpus.py` | .py | production | none by name-match ¹ | none |
| `review-agent/detect.py` | .py | production | none by name-match ¹ | none |
| `review-agent/dimensions/claim-vs-evidence.py` | .py | production | none found by name-match | none |
| `review-agent/dimensions/correctness-and-failure-modes.py` | .py | production | none found by name-match | none |
| `review-agent/dimensions/secrets-and-access.py` | .py | production | none found by name-match | none |
| `review-agent/fetch.py` | .py | production | none by name-match ¹ | none |
| `review-agent/findings.py` | .py | production | yes — `test_findings.py` | none |
| `review-agent/review.py` | .py | production | none by name-match ¹ | none |
| `review-agent/run_adjudication.py` | .py | production | yes — `test_run_adjudication.py` | none |
| `review-agent/run_controls.py` | .py | production | none by name-match ¹ | review-agent-controls runs this file itself ² |
| `review-agent/run_dimensions.py` | .py | production | yes — `test_run_dimensions.py` | none |
| `review-agent/suite.py` | .py | production | none by name-match ¹ | none |
| `review-agent/test_findings.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/test_fixtures.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/test_injection_clause.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/test_recordings.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/test_run_adjudication.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/test_run_dimensions.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/test_verdicts.py` | .py+shebang | test artifact | — (is itself a test) | none |
| `review-agent/verdicts.py` | .py | production | yes — `test_verdicts.py` | none |
| `scripts/adr_boundary_check.py` | .py+shebang | production | yes — `test_adr_boundary_check.py` | pr-check, adr-check (discover) |
| `scripts/check-branch-skew.sh` | .sh+mode 755 | production | yes — `test-check-branch-skew.sh` | none |
| `scripts/mutation_harness.py` | .py+shebang | production | none found by name-match | none |
| `scripts/pr-preflight.py` | .py+mode 755 | production | none found by name-match | none |
| `scripts/pr_body_check.py` | .py+shebang | production | yes — `test_pr_body_check.py` | pr-check, adr-check (discover) |
| `scripts/pr_review_batch.py` | .py+shebang | production | yes — `test_pr_review_batch.py` | pr-check, adr-check (discover) |
| `scripts/preflight_core.py` | .py | production | yes — `test_preflight_core.py` | pr-check, adr-check (discover) |
| `scripts/preflight_fetch.py` | .py | production | none found by name-match | none |
| `scripts/security_audit.py` | .py+shebang | production | yes — `test_security_audit.py` | pr-check, adr-check, security-audit (discover) |
| `scripts/security_audit_classifier.py` | .py+shebang | production | yes — `test_security_audit_classifier.py` | pr-check, adr-check, security-audit (discover) |
| `scripts/security_audit_core.py` | .py+shebang | production | none found by name-match | none |
| `scripts/security_audit_registry.py` | .py+shebang | production | none found by name-match | none |
| `scripts/security_audit_selftest_check.py` | .py+shebang | production | none found by name-match | none |
| `scripts/test-adr-0006-0007-renumbering.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0008-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0009-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0010-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0011-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0012-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0013-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0014-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-adr-0015-frontmatter.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-agents-md-parent-fix.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-check-branch-skew.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-gh-set-default-guidance.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test-readme-review-count.sh` | .sh+mode 755 | test artifact | — (is itself a test) | none |
| `scripts/test_adr_boundary_check.py` | .py+shebang | test artifact | — (is itself a test) | pr-check, adr-check (discover) |
| `scripts/test_no_model.py` | .py | test artifact | — (is itself a test) | pr-check, adr-check (discover) |
| `scripts/test_pr_body_check.py` | .py+shebang | test artifact | — (is itself a test) | pr-check, adr-check (discover) |
| `scripts/test_pr_review_batch.py` | .py+shebang | test artifact | — (is itself a test) | pr-check, adr-check (discover) |
| `scripts/test_preflight_core.py` | .py | test artifact | — (is itself a test) | pr-check, adr-check (discover) |
| `scripts/test_security_audit.py` | .py+shebang | test artifact | — (is itself a test) | pr-check, adr-check, security-audit (discover) |
| `scripts/test_security_audit_classifier.py` | .py+shebang | test artifact | — (is itself a test) | pr-check, adr-check, security-audit (discover) |
| `scripts/testdata/record-delete-fixture.sh` | .sh+mode 755 | test fixture | — | none |
| `scripts/testdata/record.sh` | .sh+mode 755 | test fixture | — | none |
| `sync-labels.sh` | .sh+mode 755 | production | none found by name-match | none |

### The 28 `.yml` files that are not playbooks

Per #342's out-of-scope rule, boundary cases are recorded as arguable rather than ruled on:

- **11 role task files + 2 handler files** (`ansible/roles/*/{tasks,handlers}/main.yml`) —
  executed, but only by inclusion when a playbook runs; arguably executables, arguably playbook
  internals. Counted here as *executed-by-inclusion*, not as independent entry points. No tests,
  no CI, all under `deploy/archived/`.
- **11 role defaults + 3 inventory files** (`defaults/main.yml`, `inventory/`) — configuration
  data, not executables.
- **`launchpad/labels.yml`** — data consumed by `sync-labels.sh`, not an executable.

All Ansible content sits under `launchpad/deploy/archived/`; no workflow runs any of it (the
single `launchpad/deploy` mention in any workflow is a comment at `docker.yml:142`), and the same
is true of `deploy/archived/deploy`, the one extensionless production entry point — an archived
bash deploy driver with no test and no CI.

## Confidence and what was not checked

**High confidence:** the file counts (`git ls-files` at the pinned commit, commands shown
verbatim), the complete list of test-relevant `run:` lines across the six cohort workflows, the
`CONTROLS` list, and that `suite.py` references none of the seven test modules.

**Not checked:**

- **Whether the 14 `test-*.sh` scripts pass.** I inventoried them; I did not run one. They may be
  green, stale, or broken, and that changes the cost of wiring them in considerably. Named as the
  obvious next question rather than assumed either way.
- **Whether `unittest discover -s launchpad/scripts` actually collects all seven** Python test
  files. It should by naming convention, but I did not run it and read the count. #270 recorded
  that an empty discovery can read as a pass; `launchpad-agents-tests.yml` now guards against
  exactly this for `launchpad/agents` (it counts collected *cases*, not files), but the three
  `launchpad/scripts` discover invocations have no such guard.
- **Whether the 13 review-agent `check_*.py` controls subsume what the seven `test_*.py` suites
  assert.** They might overlap substantially. I established they are different invocations, not
  that the coverage is disjoint.
- **The executable-boundary edge cases** stay recorded rather than settled: `bin/lefthook` (a
  cohort divergence under ADR-0017, executable, outside `launchpad/`), the five ADR-0005
  deployment files (cohort-owned, not executable), and the executed-by-inclusion status of
  Ansible role tasks above.
- **Upstream's `scripts/` directory** is excluded. The fork depends on several of those scripts, and
  whether they count as cohort-owned when the fork's CI relies on them is not addressed here.
