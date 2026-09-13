#!/usr/bin/env python3
"""`rqa.remediation.remediate` — `code/P-10-remediation.md` §8 rows T1-T14 and T16.

The registry and its oracles (T15) live in `test_rqa_remediation_tools.py`; the package
surface and §7's exclusions live in `test_rqa_remediation_surface.py`.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`. No test
reaches a network, a real git remote or a real formatter: `FakeRunner` is the whole of E-20
and E-26, and every filesystem effect happens inside a per-test temporary directory.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_remediation_fixtures as fx  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Category,
    Deny,
    DenyReason,
    Location,
    ProcessResult,
    RemediationPushed,
    RemediationRefused,
    RemediationRefusalReason,
)
from rqa.remediation import RemediationError, remediate  # noqa: E402

REASON = RemediationRefusalReason


class Outcome:
    """One E-10 call, plus what the filesystem looked like before the sandbox went away."""

    def __init__(self, *, result, runner, record, state_dir: pathlib.Path) -> None:
        self.result = result
        self.runner = runner
        self.record = record
        self.worktree_exists = (state_dir / "worktrees" / fx.JOB_ID).exists()

    @property
    def reason(self) -> RemediationRefusalReason:
        assert isinstance(self.result, RemediationRefused), self.result
        return self.result.reason

    @property
    def actions(self) -> list:
        return self.record.of_kind("action")


def outcome(**overrides) -> Outcome:
    with fx.sandbox() as state_dir:
        arguments = fx.call(**overrides)
        result = remediate(state_dir=state_dir, **arguments)
        return Outcome(
            result=result,
            runner=arguments["runner"],
            record=arguments["record"],
            state_dir=state_dir,
        )


def refusal(expected: RemediationRefusalReason, **overrides) -> Outcome:
    answer = outcome(**overrides)
    assert isinstance(answer.result, RemediationRefused), answer.result
    assert answer.reason is expected, f"expected {expected}, got {answer.result}"
    assert len(answer.actions) == 1, answer.actions
    assert answer.actions[0]["decision"] == "refused"
    assert answer.actions[0]["reason"] == expected.value
    assert not answer.worktree_exists, "the worktree outlived the call"
    return answer


def raised(**overrides):
    """§3 step 1 raises. Returns the runner and the record so a test can prove neither moved."""
    with fx.sandbox() as state_dir:
        arguments = fx.call(**overrides)
        try:
            remediate(state_dir=state_dir, **arguments)
        except RemediationError as error:
            return error, arguments["runner"], arguments["record"], (state_dir / "worktrees").exists()
    raise AssertionError("expected RemediationError")


def with_remedy(**remedy_overrides):
    """A finding whose remedy is overridden, with the grant and facts kept consistent."""
    remedy = fx.make_remedy(**remedy_overrides)
    location = Location(path=remedy.paths[0] if remedy.paths else fx.TARGET, line=1)
    return fx.make_finding(remedy=remedy, location=location)


# -- T1: the grant gate raises, before any record or worktree action ------------


def test_t1_a_grant_for_another_activity_raises_and_touches_nothing() -> None:
    for activity in Activity:
        if activity is Activity.REMEDIATE:
            continue
        error, runner, record, worktrees = raised(grant=fx.make_grant(activity=activity))
        assert "authorises" in str(error), activity
        assert runner.calls == [], activity
        assert record.appended == [], activity
        assert not worktrees, activity


def test_t1_a_deny_is_indistinguishable_from_an_absent_grant() -> None:
    """RQA-NFR-019: the grant is verified here, never assumed. A `Deny` carries three of
    `Grant`'s field names, so anything short of a type check would read part of it."""
    deny = Deny(
        activity=Activity.REMEDIATE,
        repo=fx.REPO,
        job_id=fx.JOB_ID,
        reason=DenyReason.NOT_ENABLED,
        detail="remediation is disabled",
        entry_seq=2,
    )
    for absent in (deny, None):
        error, runner, record, worktrees = raised(grant=absent)
        assert "verified Grant" in str(error)
        assert runner.calls == []
        assert record.appended == []
        assert not worktrees


def test_t1_a_grant_for_another_repo_job_or_snapshot_raises() -> None:
    for override, needle in (
        ({"repo": "acme/other"}, "repo"),
        ({"job_id": "job-other"}, "job"),
        ({"snapshot_hash": "z" * 64}, "snapshot"),
    ):
        error, runner, record, worktrees = raised(grant=fx.make_grant(**override))
        assert needle in str(error), override
        assert runner.calls == [] and record.appended == [] and not worktrees


def test_t1_the_grant_must_cover_the_findings_complete_category_set() -> None:
    """Set equality, never a subset test: a grant for `{MECHANICAL}` cannot authorise a
    finding that is also `PROCEDURAL` (ADR-0064, RQA-NFR-019)."""
    finding = fx.make_finding(categories=frozenset({Category.MECHANICAL, Category.PROCEDURAL}))
    for categories in (
        frozenset({Category.MECHANICAL}),
        frozenset({Category.MECHANICAL, Category.PROCEDURAL, Category.CREATION_TIME}),
        frozenset({Category.PROCEDURAL}),
        None,
    ):
        error, runner, record, worktrees = raised(
            finding=finding, grant=fx.make_grant(categories=categories)
        )
        assert "complete category set" in str(error), categories
        assert runner.calls == [] and record.appended == [] and not worktrees


def test_t1_the_grants_exact_category_set_is_accepted() -> None:
    finding = fx.make_finding(categories=frozenset({Category.MECHANICAL, Category.PROCEDURAL}))
    answer = outcome(finding=finding, grant=fx.make_grant(categories=finding.categories))
    assert isinstance(answer.result, RemediationPushed), answer.result


def test_t1_facts_that_describe_another_pr_raise() -> None:
    job = fx.make_job()
    for override in (
        {"repo": "acme/other"},
        {"number": 8},
        {"head_sha": "d" * 40},
        {"base_sha": "e" * 40},
        {"head_repo": fx.FORK},
        {"head_ref": "other-branch"},
    ):
        facts = fx.make_facts(job=job, pr=fx.make_pr_facts(job=job, **override))
        error, runner, record, worktrees = raised(facts=facts)
        assert "does not match job" in str(error), override
        assert runner.calls == [] and record.appended == [] and not worktrees


# -- T2: remedy, tool and check, all before a worktree exists -------------------


def test_t2_a_finding_without_a_remedy_is_remedy_missing() -> None:
    answer = refusal(REASON.REMEDY_MISSING, finding=fx.make_finding(remedy=None))
    assert answer.runner.calls == []
    assert "tool_id" not in answer.actions[0], "§6 records tool_id only when a remedy exists"


def test_t2_a_tool_outside_the_registry_is_tool_not_in_set() -> None:
    for tool in ("ruff", "black", "isort", "sh", ""):
        answer = refusal(REASON.TOOL_NOT_IN_SET, finding=with_remedy(tool=tool))
        assert answer.runner.calls == [], tool
        assert answer.actions[0]["tool_id"] == tool


def test_t2_a_check_that_is_not_the_tools_registered_one_is_check_not_in_set() -> None:
    for check in ("ruff-check", "rustfmt-check", "", "ruff-format-check "):
        answer = refusal(REASON.CHECK_NOT_IN_SET, finding=with_remedy(check=check))
        assert answer.runner.calls == [], check


# -- T3/T4: fork policy and protected heads, before a worktree exists -----------


def test_t3_a_fork_head_the_pinned_snapshot_disallows_is_fork_not_allowed() -> None:
    job = fx.make_job(head_repo=fx.FORK)
    answer = refusal(
        REASON.FORK_NOT_ALLOWED,
        job=job,
        facts=fx.make_facts(job=job),
        snapshot=fx.make_snapshot(policy=fx.make_policy(allow_forks=False)),
    )
    assert answer.runner.calls == []


def test_t3_a_same_repo_head_is_never_refused_for_fork_policy() -> None:
    answer = outcome(snapshot=fx.make_snapshot(policy=fx.make_policy(allow_forks=False)))
    assert isinstance(answer.result, RemediationPushed), answer.result


def test_t4_a_protected_head_is_head_protected_for_a_fork_and_for_the_base_repo() -> None:
    for job in (fx.make_job(), fx.make_job(head_repo=fx.FORK)):
        facts = fx.make_facts(job=job, pr=fx.make_pr_facts(job=job, head_protected=True))
        answer = refusal(REASON.HEAD_PROTECTED, job=job, facts=facts)
        assert answer.runner.calls == [], job.head_repo


# -- T5: exact path validation, before a worktree exists ------------------------


def test_t5_a_path_that_is_not_an_exact_captured_target_is_invalid_path() -> None:
    cases = {
        "traversal": ("../../etc/passwd",),
        "absolute": ("/etc/passwd",),
        "dot segment": ("src/./widget.py",),
        "glob": ("src/*.py",),
        "brace": ("src/{widget,other}.py",),
        "backslash": ("src\\widget.py",),
        "option": ("--force",),
        "pathspec magic": (":(glob)src/**.py",),
        "empty": ("",),
        "directory": ("src/",),
        "duplicate": (fx.TARGET, fx.TARGET),
        "unknown file": ("src/never-captured.py",),
        "unsupported suffix": ("src/widget.go",),
    }
    files = {
        fx.TARGET: fx.PY_BEFORE,
        "src/widget.go": b"package main\n",
        "src/*.py": fx.PY_BEFORE,
        "src/./widget.py": fx.PY_BEFORE,
        "src/": b"",
        "": b"",
        "--force": b"",
        "src\\widget.py": fx.PY_BEFORE,
        "../../etc/passwd": b"",
        "/etc/passwd": b"",
        ":(glob)src/**.py": b"",
        "src/{widget,other}.py": fx.PY_BEFORE,
    }
    facts = fx.make_facts(files=files)
    for name, paths in cases.items():
        answer = refusal(REASON.INVALID_PATH, finding=with_remedy(paths=paths), facts=facts)
        assert answer.runner.calls == [], name


def test_t5_a_captured_but_unchanged_file_is_invalid_path() -> None:
    """`facts.changed_paths` is the PR's own file set; a remedy may not reach outside it."""
    facts = fx.make_facts(files={fx.TARGET: fx.PY_BEFORE}, changed_paths=frozenset({"other.py"}))
    answer = refusal(REASON.INVALID_PATH, facts=facts)
    assert answer.runner.calls == []


def test_t5_a_remedy_that_omits_the_findings_own_location_is_invalid_path() -> None:
    finding = fx.make_finding(
        remedy=fx.make_remedy(paths=("src/other.py",)),
        location=Location(path=fx.TARGET, line=2),
    )
    facts = fx.make_facts(files={fx.TARGET: fx.PY_BEFORE, "src/other.py": fx.PY_BEFORE})
    answer = refusal(REASON.INVALID_PATH, finding=finding, facts=facts)
    assert answer.runner.calls == []


# -- T6: the exact head, or nothing --------------------------------------------


def test_t6_a_fetch_that_produced_another_commit_is_no_head() -> None:
    answer = refusal(REASON.NO_HEAD, runner=fx.FakeRunner(fetched_sha="d" * 40))
    assert answer.runner.ran("git", "checkout") == [], "checked out an unverified commit"


def test_t6_a_failed_checkout_is_no_head() -> None:
    refusal(REASON.NO_HEAD, runner=fx.FakeRunner(returncodes={"checkout": 1}))


def test_t6_a_head_sha_that_is_not_an_object_name_never_reaches_git() -> None:
    job = fx.make_job(head_sha="HEAD; rm -rf /")
    answer = refusal(REASON.NO_HEAD, job=job, facts=fx.make_facts(job=job))
    assert answer.runner.calls == []


def test_t6_the_fetch_targets_the_head_repo_and_the_exact_sha_never_the_ref() -> None:
    job = fx.make_job(head_repo=fx.FORK)
    answer = outcome(job=job, facts=fx.make_facts(job=job))
    assert isinstance(answer.result, RemediationPushed), answer.result
    fetches = answer.runner.ran("git", "fetch")
    assert len(fetches) == 1, fetches
    assert fetches[0] == ("git", "fetch", "--no-tags", f"https://github.com/{fx.FORK}.git", fx.HEAD_SHA)
    assert fx.HEAD_REF not in fetches[0], "the head ref is never a fetch fallback"


# -- T7: target confinement, before any formatter runs --------------------------


class _CheckoutRunner(fx.FakeRunner):
    """A checkout that materialises something other than a plain regular file."""

    def __init__(self, *, materialise, **kwargs) -> None:
        super().__init__(**kwargs)
        self.materialise = materialise

    def _git(self, *, cwd: pathlib.Path, argv: tuple[str, ...]) -> ProcessResult:
        if argv[1] == "checkout":
            self.materialise(cwd)
            return ProcessResult(returncode=0, stdout=b"", stderr=b"")
        return super()._git(cwd=cwd, argv=argv)


def _symlinked_file(cwd: pathlib.Path) -> None:
    outside = cwd.parent / "outside.py"
    outside.write_bytes(fx.PY_BEFORE)
    (cwd / "src").mkdir(parents=True, exist_ok=True)
    (cwd / fx.TARGET).symlink_to(outside)


def _symlinked_parent(cwd: pathlib.Path) -> None:
    outside = cwd.parent / "elsewhere"
    outside.mkdir(parents=True, exist_ok=True)
    (outside / "widget.py").write_bytes(fx.PY_BEFORE)
    (cwd / "src").symlink_to(outside, target_is_directory=True)


def _directory(cwd: pathlib.Path) -> None:
    (cwd / fx.TARGET).mkdir(parents=True, exist_ok=True)


def test_t7_a_symlinked_target_or_a_symlinked_parent_is_invalid_path() -> None:
    for materialise in (_symlinked_file, _symlinked_parent):
        answer = refusal(REASON.INVALID_PATH, runner=_CheckoutRunner(materialise=materialise))
        assert answer.runner.ran("ruff") == [], "a formatter ran on an escaped target"


def test_t7_a_missing_or_non_regular_target_is_invalid_path() -> None:
    for runner in (
        fx.FakeRunner(seed={}),
        _CheckoutRunner(materialise=_directory),
    ):
        answer = refusal(REASON.INVALID_PATH, runner=runner)
        assert answer.runner.ran("ruff") == []


def test_t7_a_target_that_cannot_be_fingerprinted_is_invalid_path() -> None:
    for content in (b"def (:\n", b"\xff\xfe not utf-8\n"):
        answer = refusal(REASON.INVALID_PATH, runner=fx.FakeRunner(seed={fx.TARGET: content}))
        assert answer.runner.ran("ruff") == [], "a formatter ran on an unfingerprintable file"


# -- T8: the tool itself --------------------------------------------------------


def test_t8_a_missing_formatter_is_tool_unavailable() -> None:
    answer = refusal(
        REASON.TOOL_UNAVAILABLE,
        runner=fx.FakeRunner(missing=frozenset({"ruff"}), on_fix=fx.writes(fx.PY_AFTER)),
    )
    assert answer.runner.ran("git", "push") == []


def test_t8_a_failed_fix_is_tool_failed() -> None:
    answer = refusal(
        REASON.TOOL_FAILED,
        runner=fx.FakeRunner(returncodes={"fix": 2}, on_fix=fx.writes(fx.PY_AFTER)),
    )
    assert answer.runner.ran("git", "commit") == []
    assert answer.runner.ran("git", "push") == []


# -- T9: exact set membership over NUL-delimited output -------------------------


def test_t9_a_changed_file_outside_the_exact_remedy_set_is_scope_exceeded() -> None:
    for changed in (
        (fx.TARGET, "other/file.py"),
        ("src/widget.pyi",),
        ("src/sibling.py",),
        ("src/widget.py.orig",),
    ):
        answer = refusal(
            REASON.SCOPE_EXCEEDED,
            runner=fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), changed=changed),
        )
        assert answer.runner.ran("git", "commit") == [], changed
        assert answer.runner.ran("git", "push") == [], changed


def test_t9_malformed_or_failed_diff_output_is_scope_exceeded_not_a_crash() -> None:
    for runner in (
        fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), diff_stdout=b"src/widget.py"),
        fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), diff_stdout=b"src/widget.py\x00\x00"),
        fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), diff_stdout=b"\xff\xfe\x00"),
        fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), returncodes={"diff": 1}),
    ):
        answer = refusal(REASON.SCOPE_EXCEEDED, runner=runner)
        assert answer.runner.ran("git", "push") == []


def test_t9_an_empty_diff_is_in_scope() -> None:
    """A formatter that changed nothing is not out of scope; it proceeds to the check."""
    answer = outcome(runner=fx.FakeRunner(on_fix=None))
    assert isinstance(answer.result, RemediationPushed), answer.result


# -- T10: behavior equivalence --------------------------------------------------


def test_t10_a_semantic_change_is_behaviour_changed_and_never_reaches_a_commit() -> None:
    answer = refusal(
        REASON.BEHAVIOUR_CHANGED, runner=fx.FakeRunner(on_fix=fx.writes(fx.PY_ADVERSARIAL))
    )
    assert answer.runner.ran("git", "commit") == []
    assert answer.runner.ran("git", "push") == []


def test_t10_a_fingerprint_that_cannot_be_produced_after_the_fix_is_behaviour_changed() -> None:
    for produced in (b"def (:\n", b"\xff\xfe\n", b""):
        answer = refusal(
            REASON.BEHAVIOUR_CHANGED, runner=fx.FakeRunner(on_fix=fx.writes(produced))
        )
        assert answer.runner.ran("git", "push") == []


def test_t10_a_dropped_comment_is_behaviour_changed() -> None:
    """A directive is a comment (`# fmt: off`, `# type: ignore`), so the oracle keeps
    comments in the digest and a formatter that removed one does not pass."""
    without_comment = fx.PY_AFTER.replace(b"# keep me\n", b"")
    refusal(REASON.BEHAVIOUR_CHANGED, runner=fx.FakeRunner(on_fix=fx.writes(without_comment)))


# -- T11: the registered check, and the fixpoint --------------------------------


def test_t11_a_check_that_still_fails_is_check_still_failing() -> None:
    answer = refusal(
        REASON.CHECK_STILL_FAILING,
        runner=fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), returncodes={"check": 1}),
    )
    assert answer.runner.ran("git", "commit") == []


def _twice(first: bytes, second: bytes):
    outputs = [first, second]

    def apply(cwd: pathlib.Path) -> None:
        content = outputs.pop(0) if outputs else second
        (cwd / fx.TARGET).write_bytes(content)

    return apply


def test_t11_a_second_fix_that_changes_the_tree_again_is_not_fixpoint() -> None:
    answer = refusal(
        REASON.NOT_FIXPOINT,
        runner=fx.FakeRunner(on_fix=_twice(fx.PY_AFTER, fx.PY_AFTER + b"\n")),
    )
    assert answer.runner.ran("git", "push") == []


def test_t11_a_second_fix_that_changes_behaviour_refuses_with_the_stronger_reason() -> None:
    """§3 step 11: fingerprint and scope are re-checked over the observed change *before*
    the weaker `NOT_FIXPOINT` is reported."""
    answer = refusal(
        REASON.BEHAVIOUR_CHANGED,
        runner=fx.FakeRunner(on_fix=_twice(fx.PY_AFTER, fx.PY_ADVERSARIAL)),
    )
    assert answer.runner.ran("git", "push") == []


# -- T12/T13/T14: the push --------------------------------------------------------


def test_t12_a_permitted_fork_pushes_to_the_fork_and_only_to_the_pr_head_ref() -> None:
    job = fx.make_job(head_repo=fx.FORK)
    answer = outcome(
        job=job,
        facts=fx.make_facts(job=job),
        snapshot=fx.make_snapshot(policy=fx.make_policy(allow_forks=True)),
    )
    assert isinstance(answer.result, RemediationPushed), answer.result
    pushes = answer.runner.ran("git", "push")
    assert pushes == [
        ("git", "push", f"https://github.com/{fx.FORK}.git", f"HEAD:refs/heads/{fx.HEAD_REF}")
    ], pushes


def test_t13_an_invalid_or_rqa_prefixed_head_ref_is_push_rejected_before_any_push() -> None:
    for head_ref in ("rqa/job-2194", "rqa", "", "--force", "-f", "feat ure", "a..b", "x:y", "+x",
                     "@{-1}", "head\nref", "/leading", ".hidden", "back\\slash"):
        job = fx.make_job(head_ref=head_ref)
        answer = refusal(REASON.PUSH_REJECTED, job=job, facts=fx.make_facts(job=job))
        assert answer.runner.ran("git", "push") == [], head_ref


def test_t13_a_ref_git_itself_rejects_is_push_rejected_before_any_push() -> None:
    answer = refusal(
        REASON.PUSH_REJECTED,
        runner=fx.FakeRunner(
            on_fix=fx.writes(fx.PY_AFTER), returncodes={"check-ref-format": 1}
        ),
    )
    assert answer.runner.ran("git", "check-ref-format") != []
    assert answer.runner.ran("git", "push") == []


def test_t13_a_rejected_push_is_push_rejected() -> None:
    answer = refusal(
        REASON.PUSH_REJECTED,
        runner=fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), returncodes={"push": 1}),
    )
    assert len(answer.runner.ran("git", "push")) == 1, "a rejected push was retried"


def test_t14_success_pushes_once_records_once_and_leaves_no_worktree() -> None:
    answer = outcome()
    assert isinstance(answer.result, RemediationPushed), answer.result
    assert answer.result == RemediationPushed(
        new_head_sha=fx.NEW_HEAD_SHA, tool_id="ruff-format", entry_seq=1
    )
    assert not answer.worktree_exists
    assert len(answer.record.appended) == 1
    job_id, kind, payload = answer.record.appended[0]
    assert (job_id, kind) == (fx.JOB_ID, "action")
    assert payload["decision"] == "pushed"
    assert payload["finding_id"] == "F-1"
    assert payload["tool_id"] == "ruff-format"
    assert payload["new_head_sha"] == fx.NEW_HEAD_SHA
    assert "reason" not in payload, "§6 records a reason only for a refusal"


def test_t14_the_tool_argv_is_the_exact_files_and_never_a_directory_or_a_force() -> None:
    answer = outcome()
    assert answer.runner.ran("ruff", "format") == [
        ("ruff", "format", fx.TARGET),
        ("ruff", "format", "--check", fx.TARGET),
        ("ruff", "format", fx.TARGET),
    ]
    tokens = answer.runner.flat()
    assert "." not in tokens, "a formatter was pointed at the whole tree"
    for forbidden in ("--force", "-f", "--force-with-lease", "--no-verify", "--merge", "--mirror"):
        assert forbidden not in tokens, forbidden
    assert [argv for argv in answer.runner.argvs if "push" in argv] == [
        ("git", "push", f"https://github.com/{fx.REPO}.git", f"HEAD:refs/heads/{fx.HEAD_REF}")
    ]


def test_t14_the_commit_carries_a_fixed_rqa_identity_and_names_the_finding_and_tool() -> None:
    answer = outcome()
    commits = [argv for argv in answer.runner.argvs if "commit" in argv]
    assert len(commits) == 1, commits
    commit = commits[0]
    assert "user.name=RQA Remediation" in commit
    assert any(token.startswith("user.email=") for token in commit)
    message = commit[commit.index("-m") + 1]
    assert "F-1" in message and "ruff-format" in message


def test_t14_only_the_remedys_exact_files_are_staged() -> None:
    answer = outcome()
    assert answer.runner.ran("git", "add") == [("git", "add", "--", fx.TARGET)]


def test_no_recorded_entry_is_a_transition_or_a_status_change() -> None:
    """§6: P-10 writes one `action` per value outcome, and nothing else."""
    for answer in (outcome(), refusal(REASON.REMEDY_MISSING, finding=fx.make_finding(remedy=None))):
        kinds = {kind for _, kind, _ in answer.record.appended}
        assert kinds == {"action"}, kinds


def test_no_detail_or_payload_ever_carries_process_output() -> None:
    """A tool's stderr can quote a credential a credential helper printed; none of it is
    copied into a refusal or into the record (RQA-NFR-025)."""
    secret = b"ghp_0123456789abcdefghijklmnopqrstuvwx"

    class Leaky(fx.FakeRunner):
        def run(self, *, cwd, argv, timeout):
            result = super().run(cwd=cwd, argv=argv, timeout=timeout)
            return ProcessResult(returncode=result.returncode, stdout=result.stdout, stderr=secret)

    answer = refusal(
        REASON.TOOL_FAILED, runner=Leaky(returncodes={"fix": 1}, on_fix=fx.writes(fx.PY_AFTER))
    )
    assert secret.decode() not in repr(answer.actions)
    assert secret.decode() not in answer.result.detail


# -- T16: the terminal append ---------------------------------------------------


def test_t16_append_failed_propagates_after_cleanup() -> None:
    for overrides in (
        {},  # the pushed outcome
        {"finding": fx.make_finding(remedy=None)},  # a refusal
        {"runner": fx.FakeRunner(on_fix=fx.writes(fx.PY_ADVERSARIAL))},  # a refusal after checkout
    ):
        with fx.sandbox() as state_dir:
            arguments = fx.call(record=fx.FakeRecord(fail=True), **overrides)
            try:
                remediate(state_dir=state_dir, **arguments)
            except AppendFailed:
                assert not (state_dir / "worktrees" / fx.JOB_ID).exists(), overrides
            else:
                raise AssertionError("AppendFailed did not propagate")


def test_every_call_leaves_the_state_directory_as_it_found_it() -> None:
    """§5: the worktree exists for one call. Nothing else under `state_dir` is P-10's."""
    with fx.sandbox() as state_dir:
        arguments = fx.call()
        remediate(state_dir=state_dir, **arguments)
        remaining = sorted(path.relative_to(state_dir).as_posix() for path in state_dir.rglob("*"))
        assert remaining in ([], ["worktrees"]), remaining

# -- Round 2 ---------------------------------------------------------------------
#
# G2194-P10-M1: no process output and no credential may be reachable from a propagated
# exception — its attributes, its `__context__`/`__cause__` chain, or any traceback
# frame's locals. G2194-P10-F4: the bytes about to be committed are re-verified against
# step 6's fingerprints unconditionally, whatever the check step did to the tree.


SECRET = "ghp_0123456789abcdefghijklmnopqrstuvwx"
SECRET_BYTES = SECRET.encode("utf-8")


def timed_out() -> BaseException:
    """The shape a real `subprocess` timeout has: the child's own output on the exception."""
    return subprocess.TimeoutExpired(
        cmd=("git", "push"), timeout=1.0, output=SECRET_BYTES, stderr=SECRET_BYTES
    )


def runtime_error() -> BaseException:
    return RuntimeError(SECRET)


def os_error() -> BaseException:
    return OSError(SECRET)


ERRORS = (timed_out, runtime_error, os_error)


class _LeakyRunner(fx.FakeRunner):
    """Every result carries a credential-shaped `stderr`, and one chosen call raises."""

    def __init__(self, *, raise_at: int = -1, error=timed_out, **kwargs) -> None:
        super().__init__(**kwargs)
        self.raise_at = raise_at
        self.error = error
        self.index = -1

    def run(self, *, cwd, argv, timeout) -> ProcessResult:
        self.index += 1
        if self.index == self.raise_at:
            self.calls.append((cwd, argv, timeout))
            raise self.error()
        result = super().run(cwd=cwd, argv=argv, timeout=timeout)
        return ProcessResult(returncode=result.returncode, stdout=result.stdout, stderr=SECRET_BYTES)


def _leaks(value, depth: int = 0, seen: set | None = None) -> bool:
    """Is the secret reachable from `value` by any ordinary attribute/container walk?"""
    seen = set() if seen is None else seen
    if depth > 6 or id(value) in seen:
        return False
    seen.add(id(value))
    if isinstance(value, str):
        return SECRET in value
    if isinstance(value, (bytes, bytearray)):
        return SECRET_BYTES in bytes(value)
    if isinstance(value, (types.ModuleType, type)):
        return False
    if isinstance(value, dict):
        return any(
            _leaks(key, depth + 1, seen) or _leaks(item, depth + 1, seen)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_leaks(item, depth + 1, seen) for item in value)
    state = getattr(value, "__dict__", None)
    if isinstance(state, dict):
        return _leaks(dict(state), depth + 1, seen)
    return False


def _exception_leaks(error: BaseException, *, ignore: tuple = ()) -> str | None:
    """The first place the secret is reachable from `error`, or `None`.

    `ignore` holds the injected collaborators — the fake runner and the fake record. A
    test that plants a secret *in the runner itself* would otherwise find it there through
    `remediate`'s own `runner` parameter, which says nothing about this package: a real
    `ProcessRunner` retains no child output. Everything else in every frame is scanned,
    which is where `fixed`, `checked`, `again`, `committed`, `resolved`, `push` and the
    decoded diff names would be.
    """
    ignored = {id(item) for item in ignore}
    chain: list[BaseException] = []
    pending = [error]
    while pending:
        current = pending.pop()
        if current is None or any(current is seen for seen in chain):
            continue
        chain.append(current)
        pending.extend([current.__context__, current.__cause__])
    for exception in chain:
        if _leaks(exception.args, seen=set(ignored)) or _leaks(
            getattr(exception, "__dict__", {}), seen=set(ignored)
        ):
            return f"attributes of {type(exception).__name__}"
        traceback = exception.__traceback__
        while traceback is not None:
            frame = traceback.tb_frame
            if _leaks(dict(frame.f_locals), seen=set(ignored)):
                return f"{frame.f_code.co_name}() locals in {type(exception).__name__}"
            traceback = traceback.tb_next
    return None


def _call_count() -> int:
    """How many processes one successful remediation runs."""
    with fx.sandbox() as state_dir:
        arguments = fx.call()
        remediate(state_dir=state_dir, **arguments)
        return len(arguments["runner"].calls)


def test_m1_the_secret_leaks_from_the_probe_itself() -> None:
    """The scanner is not vacuous: the untouched exception does carry the secret, so a
    test that finds nothing later is finding a real absence."""
    try:
        raise timed_out()
    except subprocess.TimeoutExpired as error:
        assert _exception_leaks(error) is not None
    for factory in ERRORS:
        assert _leaks(factory().args) or _leaks(getattr(factory(), "__dict__", {})), factory


def test_m1_a_process_failure_at_any_call_site_is_a_named_refusal_not_an_exception() -> None:
    total = _call_count()
    assert total >= 12, total
    for index in range(total):
        for factory in ERRORS:
            with fx.sandbox() as state_dir:
                arguments = fx.call(
                    runner=_LeakyRunner(
                        raise_at=index, error=factory, on_fix=fx.writes(fx.PY_AFTER)
                    )
                )
                result = remediate(state_dir=state_dir, **arguments)
                assert not (state_dir / "worktrees" / fx.JOB_ID).exists(), (index, factory)
            assert isinstance(result, RemediationRefused), (index, factory, result)
            assert SECRET not in result.detail, (index, factory)
            assert not _leaks(arguments["record"].appended), (index, factory)


def test_m1_no_secret_is_reachable_from_a_propagating_append_failed() -> None:
    """`AppendFailed` still propagates — but with nothing of the child processes on it."""
    total = _call_count()
    for index in range(total):
        for factory in ERRORS:
            with fx.sandbox() as state_dir:
                arguments = fx.call(
                    record=fx.FakeRecord(fail=True),
                    runner=_LeakyRunner(
                        raise_at=index, error=factory, on_fix=fx.writes(fx.PY_AFTER)
                    ),
                )
                try:
                    remediate(state_dir=state_dir, **arguments)
                except AppendFailed as error:
                    where = _exception_leaks(
                        error, ignore=(arguments["runner"], arguments["record"])
                    )
                    assert where is None, (index, factory.__name__, where)
                else:
                    raise AssertionError("AppendFailed did not propagate")
                assert not (state_dir / "worktrees" / fx.JOB_ID).exists()


def test_m1_no_secret_is_reachable_when_every_process_succeeds_and_the_record_fails() -> None:
    """The pushed path: every `ProcessResult` in play carried a credential-shaped stderr."""
    with fx.sandbox() as state_dir:
        arguments = fx.call(
            record=fx.FakeRecord(fail=True),
            runner=_LeakyRunner(on_fix=fx.writes(fx.PY_AFTER)),
        )
        try:
            remediate(state_dir=state_dir, **arguments)
        except AppendFailed as error:
            ignore = (arguments["runner"], arguments["record"])
            assert _exception_leaks(error, ignore=ignore) is None, _exception_leaks(
                error, ignore=ignore
            )
        else:
            raise AssertionError("AppendFailed did not propagate")


def _secret_diff() -> bytes:
    """A `git diff -z` answer naming an out-of-scope, credential-shaped path.

    Built here rather than in the test body on purpose: a local holding these bytes would
    put them in the test's own frame, and the test frame is on the traceback the scan
    walks.
    """
    return b"".join(
        name.encode("utf-8") + b"\x00" for name in (fx.TARGET, "x/" + SECRET + ".py")
    )


def test_m1_a_secret_shaped_path_in_the_diff_never_reaches_the_refusal_or_the_record() -> None:
    """Out-of-scope names are process output too: they are dropped before the append."""
    answer = refusal(
        REASON.SCOPE_EXCEEDED,
        runner=_LeakyRunner(on_fix=fx.writes(fx.PY_AFTER), diff_stdout=_secret_diff()),
    )
    assert SECRET not in answer.result.detail
    assert not _leaks(answer.actions)


def test_m1_a_secret_shaped_path_in_the_diff_never_reaches_a_propagating_exception() -> None:
    with fx.sandbox() as state_dir:
        arguments = fx.call(
            record=fx.FakeRecord(fail=True),
            runner=_LeakyRunner(on_fix=fx.writes(fx.PY_AFTER), diff_stdout=_secret_diff()),
        )
        try:
            remediate(state_dir=state_dir, **arguments)
        except AppendFailed as error:
            ignore = (arguments["runner"], arguments["record"])
            assert _exception_leaks(error, ignore=ignore) is None, _exception_leaks(
                error, ignore=ignore
            )
        else:
            raise AssertionError("AppendFailed did not propagate")


def _first_fix_only(content: bytes):
    """A formatter that writes once and is a no-op on every later run."""
    state = {"runs": 0}

    def apply(cwd: pathlib.Path) -> None:
        state["runs"] += 1
        if state["runs"] == 1:
            (cwd / fx.TARGET).write_bytes(content)

    return apply


def test_f4_bytes_the_check_step_altered_are_re_verified_against_step_six() -> None:
    """A check that mutates the tree, followed by a no-op second fix: `settled` is taken
    after the check, so only the unconditional final pass can catch this."""
    answer = refusal(
        REASON.BEHAVIOUR_CHANGED,
        runner=fx.FakeRunner(
            on_fix=_first_fix_only(fx.PY_AFTER), on_check=fx.writes(fx.PY_ADVERSARIAL)
        ),
    )
    assert answer.runner.ran("git", "add") == []
    assert answer.runner.ran("git", "commit") == []
    assert answer.runner.ran("git", "push") == []


def test_f4_a_check_step_that_escapes_scope_is_re_verified_too() -> None:
    answer = refusal(
        REASON.SCOPE_EXCEEDED,
        runner=fx.FakeRunner(
            on_fix=_first_fix_only(fx.PY_AFTER),
            on_check=fx.writes(fx.PY_AFTER, path="src/elsewhere.py"),
            seed={fx.TARGET: fx.PY_BEFORE, "src/elsewhere.py": fx.PY_BEFORE},
        ),
    )
    assert answer.runner.ran("git", "commit") == []


def test_f4_the_final_pass_does_not_disturb_the_ordinary_pushed_path() -> None:
    answer = outcome()
    assert isinstance(answer.result, RemediationPushed), answer.result
    assert len(answer.runner.ran("git", "diff")) == 2, answer.runner.argvs


# -- Round 3 ---------------------------------------------------------------------
#
# G2194-P10-NEW1: each of the three defensive nullings has its own named guard, and each
# is reached *independently* — the diff answer is scripted per call, so step 8 no longer
# decides what step 11's second diff and the final pass see.
# G2194-P10-NEW2: "could not be run" is `None`, not an integer, because every integer
# including `-1` is a status a real process can report.


def _in_scope_diff() -> bytes:
    """A `git diff -z` answer naming exactly the remedy's own file."""
    return fx.TARGET.encode("utf-8") + b"\x00"


def _leaky_scripted(*answers: bytes, on_fix=None) -> "_LeakyRunner":
    """A runner whose `git diff` answers are scripted in order."""
    return _LeakyRunner(on_fix=on_fix, diff_answers=answers)


def test_new1_the_second_diff_branch_is_reached_and_refuses_out_of_scope() -> None:
    """Step 11's second-diff branch, not step 8: the first diff is clean and in scope, and
    the second fix changes the tree so the branch runs at all."""
    answer = refusal(
        REASON.SCOPE_EXCEEDED,
        runner=_leaky_scripted(
            _in_scope_diff(),
            _secret_diff(),
            on_fix=_twice(fx.PY_AFTER, fx.PY_AFTER + b"\n"),
        ),
    )
    assert SECRET not in answer.result.detail
    assert not _leaks(answer.actions)
    assert answer.runner.ran("git", "commit") == []
    assert len(answer.runner.ran("git", "diff")) == 2, answer.runner.argvs


def test_new1_the_second_diff_names_never_reach_a_propagating_exception() -> None:
    with fx.sandbox() as state_dir:
        arguments = fx.call(
            record=fx.FakeRecord(fail=True),
            runner=_leaky_scripted(
                _in_scope_diff(),
                _secret_diff(),
                on_fix=_twice(fx.PY_AFTER, fx.PY_AFTER + b"\n"),
            ),
        )
        try:
            remediate(state_dir=state_dir, **arguments)
        except AppendFailed as error:
            ignore = (arguments["runner"], arguments["record"])
            assert _exception_leaks(error, ignore=ignore) is None, _exception_leaks(
                error, ignore=ignore
            )
        else:
            raise AssertionError("AppendFailed did not propagate")


def test_new1_the_final_pass_is_reached_and_refuses_out_of_scope() -> None:
    """The F4 final pass, not step 8 and not the second-diff branch: the fix is a fixpoint,
    so the only remaining diff is the unconditional one before `git add`."""
    answer = refusal(
        REASON.SCOPE_EXCEEDED,
        runner=_leaky_scripted(
            _in_scope_diff(), _secret_diff(), on_fix=_first_fix_only(fx.PY_AFTER)
        ),
    )
    assert SECRET not in answer.result.detail
    assert not _leaks(answer.actions)
    assert answer.runner.ran("git", "add") == []
    assert len(answer.runner.ran("git", "diff")) == 2, answer.runner.argvs


def test_new1_the_final_pass_names_never_reach_a_propagating_exception() -> None:
    with fx.sandbox() as state_dir:
        arguments = fx.call(
            record=fx.FakeRecord(fail=True),
            runner=_leaky_scripted(
                _in_scope_diff(), _secret_diff(), on_fix=_first_fix_only(fx.PY_AFTER)
            ),
        )
        try:
            remediate(state_dir=state_dir, **arguments)
        except AppendFailed as error:
            ignore = (arguments["runner"], arguments["record"])
            assert _exception_leaks(error, ignore=ignore) is None, _exception_leaks(
                error, ignore=ignore
            )
        else:
            raise AssertionError("AppendFailed did not propagate")


def test_new1_the_scripted_probe_is_not_vacuous() -> None:
    """The two branches above really are reached — and the scanner really would see the
    names if they were left bound. Both halves are checked inside a function, never at
    module scope, where `f_locals` *is* `globals()` and any probe finds its own constants."""
    assert _leaks({"changed": frozenset({"x/" + SECRET + ".py"})})
    assert not _leaks({"changed": None})
    for on_fix, expected in (
        (_twice(fx.PY_AFTER, fx.PY_AFTER + b"\n"), "second diff"),
        (_first_fix_only(fx.PY_AFTER), "final pass"),
    ):
        with fx.sandbox() as state_dir:
            arguments = fx.call(
                runner=_leaky_scripted(_in_scope_diff(), _in_scope_diff(), on_fix=on_fix)
            )
            result = remediate(state_dir=state_dir, **arguments)
        # In scope both times: the branch was reached and did *not* refuse for scope.
        assert not isinstance(result, RemediationRefused) or result.reason is not (
            REASON.SCOPE_EXCEEDED
        ), (expected, result)
        assert len(arguments["runner"].ran("git", "diff")) == 2, expected


def test_new2_a_signal_killed_formatter_is_tool_failed_not_tool_unavailable() -> None:
    """POSIX reports a signal-killed child as `-N`, so `-1` is a legal status. §3 step 7:
    a tool that ran and failed is `TOOL_FAILED`; only a tool that could not be run at all
    is `TOOL_UNAVAILABLE`."""
    for returncode in (-1, -9, -15, 1, 2, 127):
        answer = refusal(
            REASON.TOOL_FAILED,
            runner=fx.FakeRunner(
                on_fix=fx.writes(fx.PY_AFTER), returncodes={"fix": returncode}
            ),
        )
        assert str(returncode) in answer.result.detail, returncode
        assert answer.runner.ran("git", "push") == []


def test_new2_a_signal_killed_second_fix_is_also_tool_failed() -> None:
    for returncode in (-1, -9, 3):
        refusal(
            REASON.TOOL_FAILED,
            runner=fx.FakeRunner(
                on_fix=fx.writes(fx.PY_AFTER), returncodes={"fix2": returncode}
            ),
        )


def test_new2_only_a_binary_that_could_not_run_is_tool_unavailable() -> None:
    """The control: the missing-binary and the raising-runner paths keep their reason."""
    refusal(
        REASON.TOOL_UNAVAILABLE,
        runner=fx.FakeRunner(missing=frozenset({"ruff"}), on_fix=fx.writes(fx.PY_AFTER)),
    )
    refusal(
        REASON.TOOL_UNAVAILABLE,
        runner=_LeakyRunner(raise_at=4, error=timed_out, on_fix=fx.writes(fx.PY_AFTER)),
    )


def test_new2_a_signal_killed_git_keeps_its_own_named_refusal() -> None:
    """No integer is reserved anywhere: `-1` from git is still that step's own reason."""
    for key, reason in (
        ("checkout", REASON.NO_HEAD),
        ("commit", REASON.COMMIT_FAILED),
        ("push", REASON.PUSH_REJECTED),
    ):
        refusal(
            reason,
            runner=fx.FakeRunner(on_fix=fx.writes(fx.PY_AFTER), returncodes={key: -1}),
        )


def test_new2_the_process_helpers_reserve_no_integer_at_all() -> None:
    """Directly, at the helpers: a status a process really reported comes back unchanged —
    `-1` included — and only an execution failure is `None`.

    `_push_status`'s own reversion is invisible through `remediate()`, because a failed
    push and an unrunnable one are both `PUSH_REJECTED`. That makes a test at the call
    site useless as a guard, so the helper is exercised here instead."""
    from rqa.remediation.remediate import _push_status, _status

    class _NotAProcessRunner:
        """Answers with something that has no `returncode`, so `push_head` raises."""

        def run(self, *, cwd, argv, timeout):
            return object()

    for returncode in (-1, -9, 0, 1):
        runner = fx.FakeRunner(returncodes={"fix": returncode, "push": returncode})
        assert (
            _status(
                runner=runner, cwd=pathlib.Path("/tmp"), argv=("ruff", "format", "a.py"), timeout=1.0
            )
            == returncode
        ), returncode
        assert (
            _push_status(
                runner=runner,
                worktree=pathlib.Path("/tmp"),
                head_repo=fx.REPO,
                head_ref="feature/tidy",
            )
            == returncode
        ), returncode

    raising = _LeakyRunner(raise_at=0)
    assert (
        _status(
            runner=raising, cwd=pathlib.Path("/tmp"), argv=("ruff", "format", "a.py"), timeout=1.0
        )
        is None
    )
    assert (
        _push_status(
            runner=_NotAProcessRunner(),
            worktree=pathlib.Path("/tmp"),
            head_repo=fx.REPO,
            head_ref="feature/tidy",
        )
        is None
    )
