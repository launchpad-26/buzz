---
description: What the six launchpad/project-intelligence suites actually cover — 80% of logic, with coverage stopping precisely where the external rql dependency starts, leaving indexer.py's main entry point untested.
tags: [testing, coverage, project-intelligence, rql, research, issue-330]
---

# What do the six `project-intelligence` suites actually cover?

## Finding

**80% of logic, and the gap is not random — coverage stops exactly where the external `rql`
dependency starts.**

Five of the six modules are well covered (93–100%). One, `indexer.py`, sits at **38%**, and the
reason is structural rather than careless: `test_indexer.py` tests **2 of the module's 13
functions**, and the two it tests are the only ones that are pure in-memory transforms. Everything
that shells out to `rql`, `git`, or the filesystem is untested — including `index_crate`, the
indexer's primary public entry point.

So the honest summary for #290's criterion 2 is: **the cohort tests its pure logic well and its
integration points not at all.**

## Measured coverage

Tool: `coverage` 7.15.4, installed in a throwaway venv outside the repository (the directory has no
declared dependencies and none was added). Branch coverage on, 114 tests, all passing.

Raw, as measured:

```
$ python -m coverage run --branch --source=. -m unittest discover -s . -p "test_*.py"
Ran 114 tests in 117.229s
OK

$ python -m coverage report --omit="test_*"
Name                Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------
graph.py               98     32     32      2    69%
indexer.py            130     85     36      1    35%
investigator.py       193     41     42      7    74%
memory.py             102     25     40      2    80%
semantic_index.py     173     31     54      4    81%
symbol.py              31      0      0      0   100%
-----------------------------------------------------
TOTAL                 727    214    204     16    70%
```

That 70% understates it, because five of the six modules end in an `if __name__ == "__main__":`
demonstration block — worked examples from the design document, not shipped logic:

```
$ grep -n "__main__" *.py | grep -v test_
semantic_index.py:336:if __name__ == "__main__":
graph.py:183:if __name__ == "__main__":
indexer.py:311:if __name__ == "__main__":
investigator.py:483:if __name__ == "__main__":
memory.py:200:if __name__ == "__main__":
```

Excluding those blocks and the `_demo_*` helpers gives the figure worth quoting:

```
$ python -m coverage report --rcfile=<exclude __main__ and _demo_*> --omit="test_*"
Name                Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------
graph.py               65      1     24      1    98%
indexer.py            119     75     28      0    38%
investigator.py       184     34     38      6    77%
memory.py              81      5     38      1    93%
semantic_index.py     143      2     44      3    97%
symbol.py              31      0      0      0   100%
-----------------------------------------------------
TOTAL                 623    117    172     11    80%
```

**80% of logic, and one clear outlier.**

## Per module

**`symbol.py` — 100%.** 31 statements, 2 tests, nothing uncovered. It is a dataclass module.

**`graph.py` — 98%.** 14 tests. The graph construction and `reachable` traversal are covered; one
line of `reachable` is not.

**`semantic_index.py` — 97%.** 27 tests. Two statements uncovered (`embed_symbol` line 103,
`summarize_symbol` line 322), both single lines inside otherwise-covered functions.

**`memory.py` — 93%.** 33 tests, the largest suite. Uncovered: `_print_entry` (a stdout helper)
and single lines in `MemoryEntry` and `__post_init__`. The provenance and supersession rules that
make this module interesting are covered.

**`investigator.py` — 77%.** 31 tests. This is the security-relevant module and its
*rejection* paths are well covered — the injection tests assert that malformed arguments are
refused before any subprocess runs. What is uncovered is the *success* paths of the tools that
need `rql`: `find_references` (21 lines, 47% of its body), `search_symbols` (7 lines),
`_rql_read_json`, `inspect_logs`, and parts of `inspect_git_history` and `git_blame`.

**`indexer.py` — 38%.** The outlier, and worth stating precisely.

## The `indexer.py` gap, precisely

The module defines 13 functions:

```
run_rql_query          _read_body            _best_effort_calls    _best_effort_config_deps
index_crate            with_called_by        with_tests            _repo_markdown_files
with_documentation_links   _rql_read_json    enrich_git_ownership  build_index
_print_symbol
```

`test_indexer.py`'s 7 tests cover **two** of them:

```
class WithCalledByTest        5 tests   -> with_called_by
class WithTestsTest           2 tests   -> with_tests
```

**Eleven functions have no test.** Ranked by uncovered lines:

| Function | Uncovered | Share of body | Needs |
|---|---|---|---|
| `index_crate` | 31 | **94%** | `rql` |
| `_print_symbol` | 18 | 82% | stdout |
| `enrich_git_ownership` | 17 | 68% | `git` |
| `with_documentation_links` | 15 | 52% | filesystem |
| `_best_effort_calls` | 9 | 53% | nothing — pure |
| `run_rql_query` | 8 | **89%** | `rql` |
| `_rql_read_json` | 8 | **89%** | `rql` |
| `_read_body` | 6 | 86% | filesystem |
| `build_index` | 5 | 31% | composition of the above |
| `_repo_markdown_files` | 4 | 80% | filesystem |
| `_best_effort_config_deps` | 2 | 20% | nothing — pure |

The pattern is almost perfectly clean: **the two tested functions are the two that take a
`list[Symbol]` and return a `list[Symbol]`.** Every function that reaches outside the process is
untested. The two exceptions are `_best_effort_calls` and `_best_effort_config_deps`, which are
pure string helpers that simply have no direct tests.

`index_crate` is the module's principal entry point and is 94% uncovered. `build_index`, the
top-level composition, is exercised only incidentally.

This is consistent with #329's finding that `rql` is absent from the environment and the suites
still pass: they pass *because* nothing tests the code paths that need it.

## What this changes for #290

**Criterion 2 now has a real answer for this directory,** and it is more precise than a file
count: 114 tests covering 80% of logic, concentrated on pure transforms, with integration points
uncovered by construction.

**Criterion 8 gains a specific entry.** "The `project-intelligence` indexer's `rql`-dependent
paths are untested, including `index_crate`" is a nameable piece of non-coverage. Whether it is a
*choice* is not established — see below — and that distinction is exactly what criterion 8 asks
for.

**The `investigator.py` shape is worth noticing on its own.** Its rejection paths are tested and
its success paths are not. For a module whose job includes refusing injected arguments, that is
arguably the right priority — the security-relevant assertion is that bad input is refused, and
that is covered. Worth recording as a deliberate-looking emphasis rather than a gap.

**A caution against a coverage target.** #290 already rules out a percentage goal as a non-goal,
and this data supports that: raising `indexer.py` from 38% would mean testing functions that
require `rql` and a live repository, which pulls the whole suite away from the hermetic,
100-millisecond character that five of the six modules currently have. The interesting question is
not "what number" but "should the integration boundary be tested at all, and with what".

## Confidence and what was not checked

**High confidence:** the coverage numbers (raw output pasted, twice, with and without demo-block
exclusion), the function inventory and test-to-function mapping for `indexer.py` (read from
source), and the `__main__` block locations.

**Not checked:**

- **Whether the uncovered code is deliberately untested or simply untested.** I mapped what is
  covered; I did not ask the authors, and no comment in `test_indexer.py` states an intent. The
  `rql`-shaped pattern is strong evidence of a *reason* but not of a *decision*. Criterion 8 needs
  the decision, and that requires a human who was there.
- **Coverage quality.** Line and branch coverage say a line executed, not that anything was
  asserted about it. A module at 97% can still assert weakly. I did not audit assertion strength.
- **`coverage` measured on Python 3.14.6 only.** The 3.11 run in #329 passed but was not measured
  for coverage; the numbers could differ slightly on a different interpreter.
- **The other cohort suites.** `launchpad/scripts/`, `launchpad/agents/` and
  `launchpad/review-agent/` were not measured. This document is only about
  `launchpad/project-intelligence/`.
- **Mutation testing.** The stronger question — would these tests fail if the logic broke — is not
  answered by coverage. The cohort already owns a tool for this
  (`launchpad/scripts/mutation_harness.py`); pointing it at this directory would be a better
  measure than any percentage here.
