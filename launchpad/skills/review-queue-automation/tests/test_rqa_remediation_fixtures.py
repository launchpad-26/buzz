#!/usr/bin/env python3
"""Fakes and fixtures shared by the `rqa.remediation` (P-10) tests.

Self-contained: no dependency on another part's test fixtures, so this package's tests
never break because a sibling's fixtures changed shape. Every builder has a sane default
so a test only names the field it is exercising.

Nothing here reaches a network, a real git remote or a real formatter. `FakeRunner` is the
whole of E-26 and E-20 for these tests: it records every `(cwd, argv, timeout)`, plays a
scripted outcome, can raise `FileNotFoundError` for a missing binary, and — by default —
answers `git diff --name-only -z` from the bytes actually on disk, so a test that wants a
file to look changed changes the file.
"""

from __future__ import annotations

import contextlib
import hashlib
import pathlib
import sys
import tempfile
from collections.abc import Callable, Mapping
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Blocking,
    Budget,
    Category,
    Entry,
    External,
    Facts,
    Finding,
    Grant,
    Job,
    JobStatus,
    Location,
    Mechanical,
    Policy,
    PrFacts,
    ProcessResult,
    Remedy,
    RemediationPolicy,
    Snapshot,
)
from rqa.remediation import MECHANICAL_TOOL_SET  # noqa: E402

REPO = "acme/widgets"
FORK = "contributor/widgets"
NUMBER = 7
JOB_ID = "job-2194"
HEAD_SHA = "a" * 40
BASE_SHA = "b" * 40
NEW_HEAD_SHA = "c" * 40
SNAPSHOT_HASH = "s" * 64
HEAD_REF = "feature/tidy"
FETCHED_AT = datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)

TARGET = "src/widget.py"

#: Unformatted source and its formatted twin: same AST, same comments, different bytes.
PY_BEFORE = b"# keep me\nVALUES = [1,   2]\ndef go( x ):\n  return VALUES[ x ]\n"
PY_AFTER = b'# keep me\nVALUES = [1, 2]\n\n\ndef go(x):\n    return VALUES[x]\n'
#: The same formatting change plus one literal edit — behavior-changing, and the oracle
#: must say so.
PY_ADVERSARIAL = b'# keep me\nVALUES = [1, 3]\n\n\ndef go(x):\n    return VALUES[x]\n'


# -- builders ------------------------------------------------------------------


def make_job(**overrides) -> Job:
    fields = {
        "id": JOB_ID,
        "repo": REPO,
        "number": NUMBER,
        "head_sha": HEAD_SHA,
        "base_sha": BASE_SHA,
        "head_repo": REPO,
        "head_ref": HEAD_REF,
        "predecessor_job": None,
        "predecessor_head_sha": None,
        "snapshot_hash": SNAPSHOT_HASH,
        "status": JobStatus.REMEDIATING,
    }
    fields.update(overrides)
    return Job(**fields)


def make_pr_facts(*, job: Job | None = None, **overrides) -> PrFacts:
    job = job if job is not None else make_job()
    fields = {
        "repo": job.repo,
        "number": job.number,
        "head_sha": job.head_sha,
        "base_sha": job.base_sha,
        "merge_base_sha": job.base_sha,
        "head_repo": job.head_repo,
        "head_ref": job.head_ref,
        "head_protected": False,
        "author": "contributor",
        "labels": frozenset(),
        "title": "Tidy the widget",
        "body": "",
    }
    fields.update(overrides)
    return PrFacts(**fields)


def make_facts(
    *,
    job: Job | None = None,
    files: Mapping[str, bytes] | None = None,
    changed_paths: frozenset[str] | None = None,
    pr: PrFacts | None = None,
) -> Facts:
    job = job if job is not None else make_job()
    files = {TARGET: PY_BEFORE} if files is None else dict(files)
    return Facts(
        pr=pr if pr is not None else make_pr_facts(job=job),
        diff="",
        changed_paths=frozenset(files) if changed_paths is None else changed_paths,
        revision_changed_paths=frozenset(),
        files=files,
        checks=(),
        base_checks=(),
        reviews=(),
        fetched_at=FETCHED_AT,
    )


def make_remedy(**overrides) -> Remedy:
    fields = {"tool": "ruff-format", "paths": (TARGET,), "check": "ruff-format-check"}
    fields.update(overrides)
    return Remedy(**fields)


def make_finding(*, remedy: Remedy | None = ..., **overrides) -> Finding:
    fields = {
        "id": "F-1",
        "categories": frozenset({Category.MECHANICAL}),
        "extra_tags": frozenset(),
        "location": Location(path=TARGET, line=2),
        "evidence": "the file is not formatted",
        "severity": "low",
        "remedy": make_remedy() if remedy is ... else remedy,
        "behaviour_changing": False,
        "source_attempt": "A-1",
    }
    fields.update(overrides)
    return Finding(**fields)


def make_policy(*, allow_forks: bool = True, tools: frozenset[str] | None = None) -> Policy:
    return Policy(
        version="1",
        obligations=(),
        blocking=Blocking(
            categories=frozenset({Category.CORRECTNESS}),
            severities=frozenset({"high"}),
            corroboration=1,
        ),
        mechanical=Mechanical(
            categories=frozenset({Category.MECHANICAL}),
            tools=frozenset({"ruff-format"}) if tools is None else tools,
        ),
        assurance={},
        remediation=RemediationPolicy(allow_forks=allow_forks),
    )


def make_snapshot(*, policy: Policy | None = None, **overrides) -> Snapshot:
    fields = {
        "hash": SNAPSHOT_HASH,
        "repo": REPO,
        "protocol_hash": "p" * 64,
        "authority": {Activity.REMEDIATE: True},
        "routes": (),
        "external": External(allowed=False, deny_label="rqa:external"),
        "policy": policy if policy is not None else make_policy(),
        "budget": Budget(
            per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None
        ),
    }
    fields.update(overrides)
    return Snapshot(**fields)


def make_grant(*, finding: Finding | None = None, **overrides) -> Grant:
    finding = finding if finding is not None else make_finding()
    fields = {
        "activity": Activity.REMEDIATE,
        "repo": REPO,
        "job_id": JOB_ID,
        "snapshot_hash": SNAPSHOT_HASH,
        "capability_proof_id": 1,
        "categories": finding.categories,
        "entry_seq": 3,
    }
    fields.update(overrides)
    return Grant(**fields)


# -- fakes ---------------------------------------------------------------------


class FakeRecord:
    """`RecordWriter`. Keeps every append; can fail the terminal one (T16)."""

    def __init__(self, *, fail: bool = False) -> None:
        self.appended: list[tuple[str, str, Mapping]] = []
        self.fail = fail

    def append(self, job_id: str, kind: str, payload: Mapping) -> Entry:
        if self.fail:
            raise AppendFailed("the record is unwritable")
        self.appended.append((job_id, kind, dict(payload)))
        return Entry(seq=len(self.appended), hash="h" * 64)

    def of_kind(self, kind: str) -> list[Mapping]:
        return [payload for _, entry_kind, payload in self.appended if entry_kind == kind]


class FakeRunner:
    """`ProcessRunner`. Records every `(cwd, argv, timeout)` and plays a scripted outcome.

    The git surface is simulated, not run: `checkout` materialises `seed` in the worktree,
    `diff --name-only -z` reports whichever seeded files now hold different bytes, and
    `push` succeeds unless a test says otherwise. `missing` makes a binary raise
    `FileNotFoundError`, which is how E-26 reports an uninstalled tool.
    """

    def __init__(
        self,
        *,
        seed: Mapping[str, bytes] | None = None,
        on_fix: Callable[[pathlib.Path], None] | None = None,
        on_check: Callable[[pathlib.Path], None] | None = None,
        fetched_sha: str = HEAD_SHA,
        new_head_sha: str = NEW_HEAD_SHA,
        missing: frozenset[str] = frozenset(),
        returncodes: Mapping[str, int] | None = None,
        diff_stdout: bytes | None = None,
        diff_answers: tuple[bytes, ...] | None = None,
        changed: tuple[str, ...] | None = None,
        check_stdout: bytes = b"",
    ) -> None:
        self.seed = {TARGET: PY_BEFORE} if seed is None else dict(seed)
        self.on_fix = on_fix
        self.on_check = on_check
        self.fetched_sha = fetched_sha
        self.new_head_sha = new_head_sha
        self.missing = missing
        self.returncodes = dict(returncodes or {})
        self.diff_stdout = diff_stdout
        # Scripted per `git diff` call, in order, falling back to the computed answer once
        # exhausted. A single static override answers every call the same way, which makes
        # the first diff decide every later one too (G2194-P10-NEW1).
        self.diff_answers = list(diff_answers or ())
        self.changed = changed
        self.check_stdout = check_stdout
        self.calls: list[tuple[pathlib.Path, tuple[str, ...], float]] = []
        self.fix_runs = 0

    # -- introspection used by the tests ---------------------------------------

    @property
    def argvs(self) -> list[tuple[str, ...]]:
        return [argv for _, argv, _ in self.calls]

    def ran(self, *prefix: str) -> list[tuple[str, ...]]:
        return [argv for argv in self.argvs if argv[: len(prefix)] == prefix]

    def flat(self) -> list[str]:
        return [token for argv in self.argvs for token in argv]

    # -- E-26 ------------------------------------------------------------------

    def run(self, *, cwd: pathlib.Path, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        self.calls.append((cwd, argv, timeout))
        if argv[0] in self.missing:
            raise FileNotFoundError(argv[0])
        if argv[0] != "git":
            return self._tool(cwd=cwd, argv=argv)
        return self._git(cwd=cwd, argv=argv)

    # -- internals -------------------------------------------------------------

    def _result(self, key: str, *, stdout: bytes = b"") -> ProcessResult:
        return ProcessResult(returncode=self.returncodes.get(key, 0), stdout=stdout, stderr=b"")

    def _tool(self, *, cwd: pathlib.Path, argv: tuple[str, ...]) -> ProcessResult:
        """A registered formatter. Which invocation this is comes from the registry's own
        argv prefixes, never from guessing at option spelling."""
        spec = next(
            (spec for spec in MECHANICAL_TOOL_SET.values() if argv[: len(spec.fix_argv)] == spec.fix_argv
             or argv[: len(spec.check_argv)] == spec.check_argv),
            None,
        )
        if spec is None:
            raise AssertionError(f"unregistered tool invocation: {argv}")
        if argv[: len(spec.check_argv)] == spec.check_argv:
            # A check that writes is not a registered tool's behaviour; it is the shape of
            # a compromised or misregistered binary, and G2194-P10-F4 is about what the
            # package does when one appears.
            if self.on_check is not None:
                self.on_check(cwd)
            return self._result("check", stdout=self.check_stdout)
        self.fix_runs += 1
        key = "fix" if self.fix_runs == 1 else "fix2"
        if self.on_fix is not None and self.returncodes.get(key, 0) == 0:
            self.on_fix(cwd)
        return self._result(key)

    def _git(self, *, cwd: pathlib.Path, argv: tuple[str, ...]) -> ProcessResult:
        command = argv[1]
        if command == "-c":  # the fixed-identity commit
            command = "commit"
        if command == "init":
            return self._result("init")
        if command == "fetch":
            return self._result("fetch")
        if command == "rev-parse":
            if argv[-1] == "FETCH_HEAD":
                return self._result("rev-parse", stdout=f"{self.fetched_sha}\n".encode())
            return self._result("rev-parse-head", stdout=f"{self.new_head_sha}\n".encode())
        if command == "checkout":
            if self.returncodes.get("checkout", 0) == 0:
                for name, content in self.seed.items():
                    target = cwd / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
            return self._result("checkout")
        if command == "diff":
            return self._result("diff", stdout=self._diff(cwd))
        if command == "add":
            return self._result("add")
        if command == "commit":
            return self._result("commit")
        if command == "check-ref-format":
            return self._result("check-ref-format")
        if command == "push":
            return self._result("push")
        raise AssertionError(f"unscripted git command: {argv}")

    def _diff(self, cwd: pathlib.Path) -> bytes:
        if self.diff_answers:
            return self.diff_answers.pop(0)
        if self.diff_stdout is not None:
            return self.diff_stdout
        if self.changed is not None:
            return b"".join(name.encode("utf-8") + b"\x00" for name in self.changed)
        names = []
        for name, content in sorted(self.seed.items()):
            path = cwd / name
            now = path.read_bytes() if path.is_file() else b""
            if hashlib.sha256(now).digest() != hashlib.sha256(content).digest():
                names.append(name)
        return b"".join(name.encode("utf-8") + b"\x00" for name in names)


# -- helpers -------------------------------------------------------------------


@contextlib.contextmanager
def sandbox():
    """A state directory that exists only for one test."""
    with tempfile.TemporaryDirectory(prefix="rqa-remediation-") as directory:
        yield pathlib.Path(directory)


def writes(content: bytes, *, path: str = TARGET) -> Callable[[pathlib.Path], None]:
    """An `on_fix` that makes the formatter produce exactly `content`."""

    def apply(cwd: pathlib.Path) -> None:
        target = cwd / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    return apply


def call(**overrides) -> dict:
    """The keyword arguments of one successful E-10 call, ready to be overridden."""
    job = overrides.pop("job", None) or make_job()
    finding = overrides.pop("finding", None) or make_finding()
    arguments = {
        "job": job,
        "finding": finding,
        "grant": make_grant(finding=finding),
        "facts": make_facts(job=job),
        "snapshot": make_snapshot(),
        "runner": FakeRunner(on_fix=writes(PY_AFTER)),
        "record": FakeRecord(),
    }
    arguments.update(overrides)
    return arguments
