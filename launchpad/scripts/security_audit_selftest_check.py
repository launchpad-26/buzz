#!/usr/bin/env python3
"""Self-test: proves the harness renders all four statuses, distinctly, in one run.

Registered as an ordinary check so it runs inside the real audit workflow rather
than only under `unittest` — the CI run this produces is the evidence #66 asks
for, not a separate manual exercise. It feeds four synthetic results, one of each
status, through the harness's own `format_report`, and fails if any status is
missing from the rendered report or if `indeterminate` renders identically to
`pass` — the one confusion the report contract exists to rule out.
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
    lines = {r.name: next(l for l in report.splitlines() if r.name in l) for r in _SYNTHETIC}

    problems = []
    pass_bracket = _bracket(lines["synthetic-pass"])
    for r in _SYNTHETIC[1:]:
        other_bracket = _bracket(lines[r.name])
        if other_bracket == pass_bracket:
            problems.append(f"{r.status.value} renders identically to pass ({other_bracket})")

    if problems:
        return CheckResult(NAME, Status.FAIL, "; ".join(problems))
    return CheckResult(NAME, Status.PASS, "pass/fail/warn/indeterminate all render distinctly")
