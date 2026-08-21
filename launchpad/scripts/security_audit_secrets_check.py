#!/usr/bin/env python3
"""Secret-material detection for #62, using the engine and allowlist location
ADR-0006 decided: gitleaks, driven by .gitleaks.toml at the repo root.

Two modes, selected by GITHUB_EVENT_NAME rather than two registered checks,
so the registry still carries one line for this whole feature:

  pull_request       Scans only the commits this PR adds — fetches the PR's
                      base ref at run time and scopes gitleaks to
                      FETCH_HEAD..HEAD, so history predating the PR is never
                      re-scanned on every push. Reports FAIL on any finding:
                      this is the gate.
  schedule / anything Full git history, no range restriction. Reports WARN on
  else (workflow_     any finding, never FAIL — #67's definition of done
  dispatch, local)    calls this path "reports findings", distinct from the
                      PR path's "fails the run". A repository with pre-
                      existing findings must not be permanently red on this
                      path; it must be visibly, honestly not-clean.

Neither path prints a matched secret value anywhere: gitleaks runs with
--redact, which cleans both stdout and the JSON report gitleaks itself
produces, and this check's own CheckResult.detail is built only from file
paths, line numbers and rule ids — never the report's "Secret"/"Match" fields.

Local run: python3 security_audit_secrets_check.py [repo-root] runs the
full-history (reporting) path directly, without the harness, for a quick
manual check outside CI.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

from security_audit_core import CheckResult, Status

NAME = "gitleaks-secret-scan"
GITLEAKS_CONFIG = ".gitleaks.toml"

# Generous but bounded: the PR path must stay inside #66's 3-minute overall
# budget for the harness; the full-history path is explicitly allowed to
# exceed it, so it gets a much longer allowance rather than none at all —
# an unbounded subprocess is its own failure mode.
_PR_TIMEOUT_SECONDS = 120
_FULL_HISTORY_TIMEOUT_SECONDS = 1200


def _run_gitleaks(
    repo_root: Path, log_opts: Optional[str], timeout: int
) -> Tuple[Optional[List[dict]], Optional[str]]:
    """Run gitleaks; (findings, None) on success, (None, reason) if it could not run.

    Deliberately does NOT pass --exit-code 0: gitleaks' real exit code (0 clean,
    1 leaks found) is how a genuine engine failure (bad config, crash — any
    other code) is told apart from "it ran and found something", which
    --exit-code 0 would erase.
    """
    config_path = repo_root / GITLEAKS_CONFIG
    if not config_path.is_file():
        return None, f"{GITLEAKS_CONFIG} not found at {config_path}"

    cmd = [
        "gitleaks",
        "detect",
        "--config",
        str(config_path),
        "--report-format",
        "json",
        "--report-path",
        "-",
        "--redact",
        "--no-banner",
    ]
    if log_opts:
        cmd.append(f"--log-opts={log_opts}")

    try:
        # encoding/errors explicit, not text=True's platform default: gitleaks
        # emits UTF-8 (file paths, findings) and Windows' default subprocess
        # text decoding is the system locale (cp1252 on this machine), which
        # crashes decoding it. Reproduced locally before this fix landed.
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return None, "gitleaks is not installed or not on PATH"
    except subprocess.TimeoutExpired:
        return None, f"gitleaks did not finish within {timeout}s"
    except OSError as exc:
        return None, f"could not run gitleaks: {exc}"

    if result.returncode not in (0, 1):
        stderr = (result.stderr or "").strip()[-1000:]
        return None, f"gitleaks exited {result.returncode}: {stderr}"

    try:
        findings = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError as exc:
        return None, f"could not parse gitleaks report: {exc}"

    return findings, None


def _summarize(findings: List[dict], limit: int = 8) -> str:
    """file:line (rule-id), never the matched value — see module docstring."""
    locations = sorted(
        {f"{f.get('File', '?')}:{f.get('StartLine', '?')} ({f.get('RuleID', '?')})" for f in findings}
    )
    shown = ", ".join(locations[:limit])
    if len(locations) > limit:
        shown += f", and {len(locations) - limit} more"
    return shown


def _scan_pr_diff(repo_root: Path) -> CheckResult:
    # This path is the gate (module docstring): security_audit_core.exit_code()
    # only fails the run on Status.FAIL, treating INDETERMINATE the same as
    # PASS. So every "couldn't actually run the scan" case here must be FAIL,
    # never INDETERMINATE — an unscanned PR going green would silently violate
    # ADR-0008's rule that indeterminate must never render as pass. This is
    # deliberately asymmetric with _scan_full_history below, whose own
    # INDETERMINATE is correct: that path already reports pre-existing findings
    # as WARN rather than FAIL by design, so a same-shaped infra failure there
    # isn't gating anything a merge depends on.
    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    if not base_ref:
        return CheckResult(
            NAME, Status.FAIL, "GITHUB_BASE_REF is unset; cannot scope a diff scan"
        )

    try:
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", base_ref],
            cwd=repo_root,
            check=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        return CheckResult(NAME, Status.FAIL, f"could not fetch base ref {base_ref!r}: {exc}")

    findings, error = _run_gitleaks(repo_root, log_opts="FETCH_HEAD..HEAD", timeout=_PR_TIMEOUT_SECONDS)
    if error is not None:
        return CheckResult(NAME, Status.FAIL, error)
    if findings:
        return CheckResult(
            NAME,
            Status.FAIL,
            f"{len(findings)} finding(s) in this PR: {_summarize(findings)}",
        )
    return CheckResult(NAME, Status.PASS, "no secret material found in this PR's commits")


def _scan_full_history(repo_root: Path) -> CheckResult:
    start = time.monotonic()
    findings, error = _run_gitleaks(repo_root, log_opts=None, timeout=_FULL_HISTORY_TIMEOUT_SECONDS)
    elapsed = time.monotonic() - start
    if error is not None:
        return CheckResult(NAME, Status.INDETERMINATE, error)
    if findings:
        # WARN, not FAIL: a pre-existing finding is reported, per #67's
        # definition of done, not treated as this run's fault. See D-13-style
        # reasoning in the module docstring — no baseline snapshot exists to
        # silently swallow these; they are visible every run until someone
        # allowlists or remediates each one.
        return CheckResult(
            NAME,
            Status.WARN,
            f"{len(findings)} finding(s) across full history in {elapsed:.0f}s: {_summarize(findings)}",
        )
    return CheckResult(NAME, Status.PASS, f"full history clean in {elapsed:.0f}s")


def run(repo_root: Path) -> CheckResult:
    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
        return _scan_pr_diff(repo_root)
    return _scan_full_history(repo_root)


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    outcome = _scan_full_history(root)
    print(f"[{outcome.status.value}] {outcome.name} - {outcome.detail}")
    sys.exit(1 if outcome.status is Status.FAIL else 0)
