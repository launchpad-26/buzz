#!/usr/bin/env python3
"""Prove the named RQA invariant guards with bounded source mutations.

The source under test is always exported from one Git commit into a temporary
directory.  Neither tests nor mutations run in the operator checkout.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence


SKILL_REL = Path("launchpad/skills/review-queue-automation")
DEFAULT_INVENTORY_REL = Path("integrity/invariants.json")
DEFAULT_TIMEOUT = 60.0


class RunnerError(RuntimeError):
    """An invalid inventory or inconclusive mutation run."""


@dataclass(frozen=True)
class TestResult:
    returncode: int
    output: str
    timed_out: bool = False


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    outcome: str
    detail: str


def _clean_env(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Drop inherited Git repository context before every Git/test subprocess."""
    clean = {
        key: value
        for key, value in (source or os.environ).items()
        if not key.startswith("GIT_")
    }
    clean.pop("PYTEST_ADDOPTS", None)
    clean.pop("PYTEST_PLUGINS", None)
    return clean


def _run(
    argv: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
    timeout: float,
    binary: bool = False,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        tuple(argv),
        cwd=cwd,
        env=dict(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=not binary,
        timeout=timeout,
        check=False,
    )


def _git_text(repo: Path, *args: str) -> str:
    try:
        completed = _run(
            ("git", *args), cwd=repo, env=_clean_env(), timeout=DEFAULT_TIMEOUT
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunnerError(f"git {' '.join(args)} could not run: {exc}") from exc
    if completed.returncode != 0:
        raise RunnerError(
            f"git {' '.join(args)} failed ({completed.returncode}):\n{completed.stdout}"
        )
    return completed.stdout.strip()


def _repository_root(start: Path) -> Path:
    return Path(_git_text(start, "rev-parse", "--show-toplevel")).resolve()


def _safe_archive_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise RunnerError(f"git archive contains an unsafe path: {member.name!r}")
    return members


def _export_skill(repo: Path, commit: str, destination: Path) -> Path:
    try:
        completed = _run(
            ("git", "archive", "--format=tar", commit, SKILL_REL.as_posix()),
            cwd=repo,
            env=_clean_env(),
            timeout=DEFAULT_TIMEOUT,
            binary=True,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunnerError(f"git archive could not run: {exc}") from exc
    if completed.returncode != 0:
        output = completed.stdout.decode(errors="replace")
        raise RunnerError(f"git archive failed ({completed.returncode}):\n{output}")
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        archive.extractall(destination, members=_safe_archive_members(archive))
    skill = destination / SKILL_REL
    if not skill.is_dir():
        raise RunnerError(f"archive did not contain {SKILL_REL}")
    return skill


def _relative_path(value: object, *, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise RunnerError(f"{field} must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise RunnerError(f"{field} must stay inside the archived skill: {value!r}")
    return Path(*path.parts)


def _load_inventory(path: Path) -> list[dict]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunnerError(f"cannot load inventory {path}: {exc}") from exc
    if not isinstance(document, dict) or document.get("version") != 1:
        raise RunnerError("inventory must be an object with version 1")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RunnerError("inventory must contain a non-empty cases list")
    seen: set[str] = set()
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            raise RunnerError(f"{label} must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise RunnerError(f"{label}.id must be a non-empty string")
        if case_id in seen:
            raise RunnerError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        for field in ("invariant", "test", "expected_assertion"):
            if not isinstance(case.get(field), str) or not case[field]:
                raise RunnerError(f"{case_id}.{field} must be a non-empty string")
        if "::" not in case["test"]:
            raise RunnerError(f"{case_id}.test must be one exact pytest node id")
        source = case.get("source")
        if not isinstance(source, dict) or not isinstance(source.get("line"), int):
            raise RunnerError(f"{case_id}.source must name path and integer line")
        _relative_path(source.get("path"), field=f"{case_id}.source.path")
        mutation = case.get("mutation")
        if not isinstance(mutation, dict):
            raise RunnerError(f"{case_id}.mutation must be an object")
        _relative_path(mutation.get("path"), field=f"{case_id}.mutation.path")
        delete = mutation.get("delete", False)
        if not isinstance(delete, bool):
            raise RunnerError(f"{case_id}.mutation.delete must be a boolean")
        if delete:
            if "before" in mutation or "after" in mutation:
                raise RunnerError(
                    f"{case_id}.mutation must choose either delete or before/after"
                )
        else:
            for field in ("before", "after"):
                if not isinstance(mutation.get(field), str) or not mutation[field]:
                    raise RunnerError(
                        f"{case_id}.mutation.{field} must be a non-empty string"
                    )
    return cases


def _apply_mutation(skill: Path, case: Mapping[str, object]) -> None:
    case_id = str(case["id"])
    mutation = case["mutation"]
    if not isinstance(mutation, Mapping):
        raise RunnerError(f"{case_id}.mutation is invalid")
    relative = _relative_path(mutation["path"], field=f"{case_id}.mutation.path")
    target = skill / relative
    if mutation.get("delete") is True:
        if not target.is_file():
            raise RunnerError(f"{case_id}: deletion target is not a file: {relative}")
        target.unlink()
        return
    try:
        original = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise RunnerError(f"{case_id}: cannot read mutation target {relative}: {exc}") from exc
    before = str(mutation["before"])
    after = str(mutation["after"])
    matches = original.count(before)
    if matches != 1:
        raise RunnerError(
            f"{case_id}: stale mutation anchor in {relative}: expected 1 match, found {matches}"
        )
    mutated = original.replace(before, after, 1)
    if target.suffix == ".py":
        try:
            ast.parse(mutated, filename=str(relative))
        except SyntaxError as exc:
            raise RunnerError(f"{case_id}: mutation does not preserve valid Python: {exc}") from exc
    target.write_text(mutated, encoding="utf-8")


def _pytest(skill: Path, node: str, timeout: float) -> TestResult:
    env = _clean_env()
    env["PYTHONPATH"] = str(skill)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = _run(
            (sys.executable, "-m", "pytest", "-q", node),
            cwd=skill,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return TestResult(returncode=-1, output=output, timed_out=True)
    except OSError as exc:
        return TestResult(returncode=-1, output=str(exc), timed_out=False)
    return TestResult(returncode=completed.returncode, output=completed.stdout)


def _classify_mutant(result: TestResult, expected_assertion: str) -> tuple[str, str]:
    if result.timed_out:
        return "ERROR", "mutated test timed out"
    if result.returncode == 0:
        return "SURVIVED", "named guard test stayed green"
    if result.returncode != 1:
        return "ERROR", f"pytest exited {result.returncode}, not an assertion-failure exit"
    if "AssertionError" not in result.output:
        return "ERROR", "pytest failed without an AssertionError"
    if expected_assertion not in result.output:
        return "ERROR", f"expected invariant assertion {expected_assertion!r} was absent"
    return "KILLED", "named guard failed with the expected invariant assertion"


def _print_test(label: str, node: str, result: TestResult) -> None:
    print(f"  {label}: {sys.executable} -m pytest -q {node}")
    print(f"  returncode: {result.returncode}{' (timeout)' if result.timed_out else ''}")
    if result.output:
        for line in result.output.rstrip().splitlines():
            print(f"    {line}")
    else:
        print("    <no output>")


def _run_case(
    archive_skill: Path,
    scratch: Path,
    case: Mapping[str, object],
    timeout: float,
) -> CaseResult:
    case_id = str(case["id"])
    isolated_skill = scratch / case_id / "skill"
    shutil.copytree(archive_skill, isolated_skill)
    node = str(case["test"])
    baseline = _pytest(isolated_skill, node, timeout)
    print(f"\n[{case_id}] {case['invariant']}")
    _print_test("baseline", node, baseline)
    if baseline.timed_out:
        return CaseResult(case_id, "ERROR", "unmutated named test timed out")
    if baseline.returncode != 0:
        return CaseResult(
            case_id,
            "ERROR",
            f"unmutated named test exited {baseline.returncode}; baseline must pass",
        )
    try:
        _apply_mutation(isolated_skill, case)
    except RunnerError as exc:
        return CaseResult(case_id, "ERROR", str(exc))
    mutant = _pytest(isolated_skill, node, timeout)
    _print_test("mutant", node, mutant)
    outcome, detail = _classify_mutant(mutant, str(case["expected_assertion"]))
    return CaseResult(case_id, outcome, detail)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", default=[], help="run only this inventory id")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.timeout <= 0:
        print("ERROR: --timeout must be positive", file=sys.stderr)
        return 2
    try:
        repo = _repository_root(Path(__file__).resolve().parent)
        commit = _git_text(repo, "rev-parse", "HEAD")
        with tempfile.TemporaryDirectory(prefix="rqa-invariant-mutations-") as directory:
            scratch = Path(directory)
            archived_skill = _export_skill(repo, commit, scratch / "archive")
            cases = _load_inventory(archived_skill / DEFAULT_INVENTORY_REL)
            requested = set(args.case)
            known = {str(case["id"]) for case in cases}
            missing = sorted(requested - known)
            if missing:
                raise RunnerError(f"unknown case id(s): {', '.join(missing)}")
            selected = [case for case in cases if not requested or case["id"] in requested]
            print(f"source_commit: {commit}")
            print(f"source_scope: {SKILL_REL.as_posix()}")
            print(f"isolation: git archive -> {scratch} (deleted on exit)")
            print(f"cases: {len(selected)}")
            results = [
                _run_case(archived_skill, scratch / "runs", case, args.timeout)
                for case in selected
            ]
    except RunnerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("\nsummary:")
    for result in results:
        print(f"  {result.case_id}: {result.outcome} - {result.detail}")
    killed = sum(result.outcome == "KILLED" for result in results)
    survived = sum(result.outcome == "SURVIVED" for result in results)
    errors = sum(result.outcome == "ERROR" for result in results)
    print(f"totals: killed={killed} survived={survived} errors={errors}")
    if errors:
        return 2
    if survived:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
