#!/usr/bin/env python3
"""Run every registered #62 security check and print one structured report.

This is the harness, not a check. It owns three things: the result contract every
check must return, running the registry and catching a check that raises instead
of reporting, and turning the results into one printed report plus a process exit
code. Detection logic — secret material, ignore coverage, Actions hygiene,
settings attestation — lives in separate checks registered in
security_audit_registry.py and is deliberately absent here, so those checks land
independently without editing this file or the workflow YAML.

Four statuses exist, not two, because a question this can't answer is not the
same as a question it answered "no" to:

  pass           the check ran and the condition held
  fail           the check ran and the condition did not hold
  warn           the check ran, found something worth a human's attention, but
                 the condition is not itself a failure
  indeterminate  the check could not be evaluated (e.g. a network dependency was
                 unreachable) — this must never render or count as `pass`. A
                 silently-unanswerable check that looks green is worse than one
                 that visibly failed.

A check that raises is caught here and recorded as `fail` with the exception
message as its detail, rather than crashing the run or being silently dropped —
a broken check is a finding, not an outage.

Detail strings must never contain raw file contents or matched substrings; the
harness only ever prints what a check chooses to summarize.

This module holds the contract and the runner. `security_audit.py` is the thin
CLI entrypoint that calls `main()` here — kept separate so that nothing which
imports this module by name also runs it as `__main__`, which would otherwise
load it twice under two different module identities and make its own `Status`
enum fail to match itself (`Status.PASS != Status.PASS` across the two copies).

Exit code is 1 if any check reports `fail`, 0 otherwise — `warn` and
`indeterminate` are visible in the report but do not fail the run themselves,
since neither asserts the condition is wrong, only that it is unresolved or
worth noting.
"""

import dataclasses
import enum
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, List


class Status(enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    INDETERMINATE = "indeterminate"


# Fixed width so the report's brackets line up regardless of which statuses are
# present in a given run — a ragged column is what makes a skim miss a FAIL.
_MARKERS = {
    Status.PASS: "PASS",
    Status.FAIL: "FAIL",
    Status.WARN: "WARN",
    Status.INDETERMINATE: "INDETERMINATE",
}
_MARKER_WIDTH = max(len(m) for m in _MARKERS.values())


@dataclasses.dataclass(frozen=True)
class CheckResult:
    """What one check reports. `name` identifies the check, not the file it looked at."""

    name: str
    status: Status
    detail: str = ""


CheckFunc = Callable[[Path], CheckResult]


def run_all(repo_root: Path, checks: Iterable[CheckFunc]) -> List[CheckResult]:
    results: List[CheckResult] = []
    for check in checks:
        try:
            results.append(check(repo_root))
        except Exception as exc:  # noqa: BLE001 — a broken check is a finding, see module docstring
            identifier = getattr(check, "__module__", repr(check))
            results.append(
                CheckResult(
                    name=identifier,
                    status=Status.FAIL,
                    detail=f"check raised {type(exc).__name__}: {exc}",
                )
            )
    return results


def format_report(results: List[CheckResult]) -> str:
    lines = ["Launchpad security audit", "=" * 25, ""]
    name_width = max((len(r.name) for r in results), default=0)
    for r in results:
        marker = _MARKERS[r.status]
        line = f"[{marker.rjust(_MARKER_WIDTH)}] {r.name.ljust(name_width)}"
        if r.detail:
            line += f"  - {r.detail}"
        lines.append(line.rstrip())
    counts = Counter(r.status for r in results)
    lines.append("")
    lines.append(
        f"{counts.get(Status.PASS, 0)} pass, "
        f"{counts.get(Status.FAIL, 0)} fail, "
        f"{counts.get(Status.WARN, 0)} warn, "
        f"{counts.get(Status.INDETERMINATE, 0)} indeterminate"
    )
    return "\n".join(lines)


def exit_code(results: List[CheckResult]) -> int:
    return 1 if any(r.status is Status.FAIL for r in results) else 0


def main(argv: List[str]) -> int:
    repo_root = Path(argv[1]) if len(argv) > 1 else Path.cwd()

    # Imported here, not at module load, so a broken registry import surfaces as
    # this script's own failure rather than an ImportError before the report
    # machinery above is even available to describe it.
    from security_audit_registry import CHECKS

    results = run_all(repo_root, CHECKS)
    print(format_report(results))
    return exit_code(results)
