---
description: What the cohort's unrun Python suites print on failure — five suites appear safe, investigator remains unverified, and project-pack.py echoes a closed set of operator model/provider configuration values.
tags: [testing, ci, security, disclosure, public-logs, criterion-3, research, issue-345]
---

# What do the unrun Python suites print on failure?

All source references below are pinned to `5d76799d6e44f2f76aa7bd78c5343d339af98f63`.

## Finding

**Five suites appear safe to print. The subprocess-driven investigator suite remains unverified,
and one tool echoes operator configuration values.**

Failure output from the five inspected `launchpad/project-intelligence/` suites discloses nothing that is not already public,
and `launchpad/agents/test_project_pack.py` is deliberately hermetic with respect to the
environment. The sixth, `test_investigator.py`, runs real subprocesses and captures machine-derived
output, so this research does not clear it for public CI logs.

But the tool under test in `launchpad/agents/` — `project-pack.py`, the #239 projector — **writes
the operator's real environment values into its rendered output**, and writes that output to stdout
by default. The tests never trigger it because they inject fake dictionaries. Anything that runs the
projector itself in CI would.

## What a real failure prints

Failures were induced by mutating each production module and running its suite. Four of five
mutations were not caught; the `semantic_index` one was, and this is its complete output:

```
.....F.....................
======================================================================
FAIL: test_a_zero_vector_has_zero_similarity_not_a_division_error (test_semantic_index.EmbedAndCosineSimilarityTest.test_a_zero_vector_has_zero_similarity_not_a_division_error)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<local-worktree>/launchpad/project-intelligence/test_semantic_index.py", line 171, in test_a_zero_vector_has_zero_similarity_not_a_division_error
    self.assertEqual(cosine_similarity(empty, non_empty), 0.0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1.0 != 0.0

----------------------------------------------------------------------
Ran 27 tests in 0.007s

FAILED (failures=1)
```

Three kinds of content appear, and each is worth classifying separately:

1. **An absolute filesystem path.** Here it exposes a developer's home directory name. On
   `ubuntu-latest` the same line reads `/home/runner/work/buzz/buzz/…`, which discloses nothing.
   This is a local-only concern and would matter on a self-hosted runner.
2. **The assertion's source line**, quoted from the test file. That file is already world-readable in
   a public repository, so this adds no disclosure.
3. **The repr of the compared values** — `1.0 != 0.0`. This is the variable part, and it is where a
   leak would come from if the asserted values held anything sensitive.

## Why the asserted values are safe here

**No suite or module under `launchpad/project-intelligence/` reads the environment.** Searching all
twelve files for `os.environ`, `getenv`, `TOKEN`, `SECRET` and `KEY` returns only three comments
in [`graph.py`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/project-intelligence/graph.py) describing a `"config:KEY"` node-id
convention, and one Rust function signature used as a test fixture in
[`test_semantic_index.py:51`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/project-intelligence/test_semantic_index.py#L51). There
is no environment access to leak from.

Everything in the five inspected suites is derived from the repository — graph edges, symbols, memory
entries, similarity scores — and the repository is public. A failure printing repo-derived content
discloses nothing new.

`launchpad/agents/test_project_pack.py` is environment-hermetic because its call sites pass literal
dictionaries — `{"BUZZ_CLI_BIN": str(override)}`, `{}` — never `os.environ`. Its docstring says it
does not exercise the functions against a real `buzz` binary so the tests run without a cargo
build; that is a portability statement, not the evidence for environment hermeticity.

## The one real disclosure surface, and it is not in a test

[`project-pack.py`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/agents/project-pack.py) reads the live environment
([lines 231 and 235](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/agents/project-pack.py#L231-L235)):

```python
        buzz_bin = find_buzz_binary(REPO_ROOT, os.environ)
        kept, skipped = apply_operator_precedence(pairs, os.environ)
```

`apply_operator_precedence` records the operator's value alongside the pack's
([line 181](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/agents/project-pack.py#L181)):

```python
            skipped.append((key, value, environ[key]))
```

and `render_env_file` writes that operator value into the generated file
([lines 199-204](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/agents/project-pack.py#L199-L204)):

```python
    for key, resolved_value, operator_value in skipped:
        lines.append(
            f"# skipped {key}: operator env already sets it to "
            f"{shlex.quote(operator_value)} (pack would have projected "
            f"{shlex.quote(resolved_value)})"
        )
```

The rendered result goes to stdout unless `--out` is given
([line 244](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/agents/project-pack.py#L244)):

```python
        sys.stdout.write(rendered)
```

So for any variable the pack projects *and* the operator has already set, the real operator value is
written verbatim into the output. The projected runtime key set is closed: model, provider,
temperature and context-limit settings plus the ACP command/arguments and optional MCP command.
It does **not** include `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, or provider API credentials. The earlier
credential characterisation inferred projector scope from unrelated Agent CLI documentation and
was wrong.

This still has the output-boundary shape #279 records—a live operator value can reach stdout—but
the values reachable here are configuration, not credentials. Whether publishing model/provider
choices and limits is acceptable is a narrower policy question than the original threat model.

**No leak is claimed here.** The tests do not reach this path, no CI job runs the projector today,
and nothing in a tracked file contains a secret. What exists is a code path whose output is unsafe
to print in a public log.

## A smaller instance of the same shape

[`investigator.py:137`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/project-intelligence/investigator.py#L137) embeds subprocess
stderr into an exception message:

```python
        raise RuntimeError(f"search_text: grep exited {result.returncode}: {result.stderr!r}")
```

If that propagates through a test failure, grep's stderr reaches the log. In practice grep's stderr
is a path and an errno, so severity is low — but it is the same pattern as #279 and worth naming
while the file is open.

## An incidental observation about mutation strength

Four of the five crude mutations I applied were not detected — `graph.py`, `memory.py`,
`symbol.py` and `indexer.py` all stayed green with a production line altered. That is consistent
with #330's finding that coverage concentrates on pure transforms. **It is weak evidence**: my
mutations were mechanical (inverting the first comparison found) and several probably landed on
lines no test reaches, which is a statement about where I mutated, not about test quality.

## Recommendations

**Opinion, mine (Claude Opus 5, drafting for @tucktuck101). Not established by any source above.**

1. **I would wire the five repository-derived `project-intelligence` suites into CI without
   redaction work.** I would assess `test_investigator.py` separately before including it because
   it captures real subprocess output from `rql`, `grep`, and `cargo`.
2. **I would treat `project-pack.py`'s operator-value echo as a separate issue from this one.** My
   reading is that it needs a decision about whether the skip
   comment should carry the value at all — the comment's stated purpose is to explain why a variable
   was skipped, which arguably needs only the variable's name.
3. **I would not run the projector in CI** until that is settled, which also means keeping it out of
   whatever criterion 3 adds for `launchpad/agents/`.
4. **I would fold `investigator.py:137` into #279's thread** rather than filing it separately, since
   it is the same defect class and #279 already owns the policy question.

None of these is a decision I am entitled to take, and item 2 in particular should be looked at by
someone who knows whether that comment's value is load-bearing for operators.

## Confidence and what was not checked

**High confidence:** the redacted failure output above, the absence of environment access in the
five repository-derived suites, the hermetic construction of `test_project_pack.py`, the closed
projector key set, and the `project-pack.py` code path (read at the pinned lines).

**Not checked:**

- **Only one induced failure produced output.** Four mutations were not caught, so I have one real
  failure sample, not five. Other failure modes — an exception inside a module rather than a failed
  assertion, or a failure in `test_investigator` — would print differently and were not observed.
- **`test_investigator` was excluded from the mutation run.** It is the suite that spawns real
  subprocesses including `cargo test` (#329), so it is the most likely of the six to print something
  unexpected, and it is the one I did not induce a failure in.
- **I did not run the projector**, with real or fake environment. The disclosure path is read from
  source, not observed. Running it with a synthetic variable set would confirm it in seconds and I
  did not do so.
- **The suites that already run in CI were not audited** — `launchpad/scripts/` and
  `launchpad/review-agent/`. #279 covers one instance in the former; this document does not extend
  to either.
- **No judgement about whether the projector's behaviour is wrong.** Writing an operator's own value
  back to that operator's own terminal may be entirely intended. What I establish is that the output
  is unsafe to route into a public log, not that the feature is a defect.
