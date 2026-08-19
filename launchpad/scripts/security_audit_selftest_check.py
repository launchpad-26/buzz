#!/usr/bin/env python3
"""Self-test: proves the harness renders all four statuses, distinctly, in one run.

Registered as an ordinary check so it runs inside the real audit workflow rather
than only under `unittest` — the CI run this produces is the evidence #66 asks
for, not a separate manual exercise. It feeds four synthetic results, one of each
status, through the harness's own `format_report`, and fails if any status is
missing from the rendered report or if any two statuses render identically —
checked pairwise, not just each against `pass`, so a fix that made e.g. `fail`
and `warn` collide would be caught too, not only a collision with `pass`.
"""

from security_audit_core import CheckResult, Status, format_report

NAME = "harness-self-test"

_SYNTHETIC = [
    CheckResult("synthetic-pass", Status.PASS, "example pass"),
    CheckResult("synthetic-fail", Status.FAIL, "example fail"),
    CheckResult("synthetic-warn", Status.WARN, "example warn"),
    CheckResult("synthetic-indeterminate", Status.INDETERMINATE, "example indeterminate"),
]


def _bracket(line: str) -> str:
    return line.split("]", 1)[0]


def run(repo_root) -> CheckResult:  # noqa: ARG001 — signature matches CheckFunc
    report = format_report(_SYNTHETIC)
    report_lines = report.splitlines()

    problems = []
    lines = {}
    for r in _SYNTHETIC:
        matches = [l for l in report_lines if r.name in l]
        if not matches:
            problems.append(f"{r.name} is missing from the report entirely")
            continue
        lines[r.name] = matches[0]

    # Pairwise, not just each-against-pass: a fix that makes FAIL and WARN
    # render identically would pass the old vs-pass-only check silently.
    brackets = {r.name: _bracket(lines[r.name]) for r in _SYNTHETIC if r.name in lines}
    names = list(brackets)
    for i, name_a in enumerate(names):
        for name_b in names[i + 1 :]:
            if brackets[name_a] == brackets[name_b]:
                problems.append(
                    f"{name_a} and {name_b} render identically ({brackets[name_a]})"
                )

    if problems:
        return CheckResult(NAME, Status.FAIL, "; ".join(problems))
    return CheckResult(NAME, Status.PASS, "pass/fail/warn/indeterminate all render distinctly")
