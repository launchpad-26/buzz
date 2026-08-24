"""Agent-configuration-surface check for #68.

Scans the agent-surface directories and config-file shapes defined in
`security_audit_agent_surface.py` for credential-shaped strings — reusing
#67's gitleaks ruleset (`.gitleaks.toml`) rather than a second pattern set,
per this task's own definition of done. This is a present-tense content
check (what does the surface carry *today*), not a history scan — #67 already
owns history; this check exists because the agent-surface directories are a
distinct, growing part of the tree a contributor or an agent itself might
populate with a real credential (a live API key dropped into an MCP config
for local testing, for instance) that #67's PR-diff scan would only catch if
the addition happened inside a PR gitleaks actually ran on.

Never prints a matched value — same discipline as #67's check, and the same
`--redact` flag on every gitleaks invocation.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from security_audit_agent_surface import AGENT_CONFIG_FILE_GLOBS, AGENT_SURFACE_DIRS
from security_audit_core import CheckResult, Status

NAME = "agent-surface-secret-scan"
GITLEAKS_CONFIG = ".gitleaks.toml"
_TIMEOUT_SECONDS = 60


def _collect_surface_paths(repo_root: Path) -> List[Path]:
    """Every file under an AGENT_SURFACE_DIRS directory, plus every file
    matching an AGENT_CONFIG_FILE_GLOBS shape anywhere in the repo. A set,
    not a list, so a file matched both ways (a persona.md inside .claude/,
    say) is scanned once.
    """
    paths: set[Path] = set()
    for dir_name in AGENT_SURFACE_DIRS:
        directory = repo_root / dir_name
        if directory.is_dir():
            paths.update(p for p in directory.rglob("*") if p.is_file())
    for glob_pattern in AGENT_CONFIG_FILE_GLOBS:
        paths.update(p for p in repo_root.glob(glob_pattern) if p.is_file())
    return sorted(paths)


def _summarize(findings: List[dict], repo_root: Path, limit: int = 8) -> str:
    """file:line (rule-id), repo-relative, never the matched value."""
    locations = set()
    for f in findings:
        try:
            rel = Path(f.get("File", "?")).relative_to(repo_root)
        except ValueError:
            rel = f.get("File", "?")
        locations.add(f"{rel}:{f.get('StartLine', '?')} ({f.get('RuleID', '?')})")
    shown = sorted(locations)
    text = ", ".join(shown[:limit])
    if len(shown) > limit:
        text += f", and {len(shown) - limit} more"
    return text


def _run_gitleaks_no_git(
    repo_root: Path, source_paths: List[Path]
) -> Tuple[Optional[List[dict]], Optional[str]]:
    config_path = repo_root / GITLEAKS_CONFIG
    if not config_path.is_file():
        return None, f"{GITLEAKS_CONFIG} not found at {config_path}"
    if not source_paths:
        return [], None

    findings: List[dict] = []
    for path in source_paths:
        cmd = [
            "gitleaks",
            "detect",
            "--no-git",
            "--source",
            str(path),
            "--config",
            str(config_path),
            "--report-format",
            "json",
            "--report-path",
            "-",
            "--redact",
            "--no-banner",
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=_TIMEOUT_SECONDS,
            )
        except FileNotFoundError:
            return None, "gitleaks is not installed or not on PATH"
        except subprocess.TimeoutExpired:
            return None, f"gitleaks did not finish within {_TIMEOUT_SECONDS}s scanning {path}"
        except OSError as exc:
            return None, f"could not run gitleaks on {path}: {exc}"

        if result.returncode not in (0, 1):
            stderr = (result.stderr or "").strip()[-500:]
            return None, f"gitleaks exited {result.returncode} on {path}: {stderr}"

        try:
            file_findings = json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError as exc:
            return None, f"could not parse gitleaks report for {path}: {exc}"
        findings.extend(file_findings)

    return findings, None


def run(repo_root: Path) -> CheckResult:
    surface_paths = _collect_surface_paths(repo_root)
    if not surface_paths:
        # Nothing to scan is not a clean scan. Without this, a sparse checkout,
        # a refactor that moves the agent-config directories, or any environment
        # where AGENT_SURFACE_DIRS and AGENT_CONFIG_FILE_GLOBS resolve to nothing
        # produces "no credential-shaped strings found across 0 agent-surface
        # file(s)" — indistinguishable in the summary from a real clean scan of
        # the full surface, and green because exit_code() only fails on FAIL. A
        # security check that reports clean when it did not run is worse than no
        # check. Same fail-closed shape as security_audit_ignore_coverage_check's
        # unreadable-file case.
        return CheckResult(
            NAME,
            Status.INDETERMINATE,
            "no agent-surface files were found to scan, so this control asserts "
            "nothing — this is not the same as scanning the surface and finding it "
            f"clean. Looked for {list(AGENT_CONFIG_FILE_GLOBS)} under "
            f"{list(AGENT_SURFACE_DIRS)} in {repo_root}",
        )
    findings, error = _run_gitleaks_no_git(repo_root, surface_paths)
    if error is not None:
        return CheckResult(NAME, Status.INDETERMINATE, error)
    if findings:
        return CheckResult(
            NAME,
            Status.FAIL,
            f"{len(findings)} finding(s) on the agent-config surface: "
            + _summarize(findings, repo_root),
        )
    return CheckResult(
        NAME,
        Status.PASS,
        f"no credential-shaped strings found across {len(surface_paths)} agent-surface file(s)",
    )
