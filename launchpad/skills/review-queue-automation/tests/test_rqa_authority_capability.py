#!/usr/bin/env python3
"""`rqa.authority.capability` — `code/P-08-authority-gate.md` §4 and §8 row T14.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

`credential()` is E-22, the one process launch in P-08. These tests exercise the real
function against a *substituted* process — `capability._run` — so every branch is
covered without a real `gh` on the machine and without a network call, in this suite or
in CI. The substitution point is a module-level function precisely so this is possible.
"""

from __future__ import annotations

import contextlib
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.authority.capability as capability  # noqa: E402
from rqa.authority.capability import (  # noqa: E402
    CapabilityProof,
    CredentialGithubUnavailable,
    credential,
    probe_capability,
)
from rqa.authority.gate import GateError  # noqa: E402
from rqa.contracts import CapabilityReading, GithubUnavailable  # noqa: E402

REPO = "launchpad-26/buzz"
JOB = "job-1"
TOKEN = "gho_thetokenvalue"  # nosec - a sentinel, never a real credential
PROBED_AT = datetime(2026, 9, 12, 8, 30, 15, tzinfo=timezone.utc)


class FakeProbe:
    def __init__(self, reading=None):
        self.reading = reading or CapabilityReading(
            capabilities=frozenset({"pulls:write"}),
            attested_not_proven=frozenset({"admin:org"}),
            login="rqa-operator",
        )
        self.credentials: list[str] = []

    def probe(self, *, repo: str, credential: str):
        self.credentials.append(credential)
        return self.reading


class FakeStore:
    def __init__(self):
        self.puts: list[CapabilityProof] = []

    def current(self, repo: str, job_id: str):
        return None

    def put(self, proof: CapabilityProof) -> int:
        self.puts.append(proof)
        return 7


class ExplodingStore(FakeStore):
    def put(self, proof: CapabilityProof) -> int:
        raise AssertionError("nothing may be persisted when the credential is unavailable")


@contextlib.contextmanager
def process(result=None, error: Exception | None = None):
    """Substitute E-22's process launch for the duration of one test."""

    def run(argv):
        assert argv == capability.GH_TOKEN_ARGV, argv
        if error is not None:
            raise error
        return result

    original = capability._run
    capability._run = run
    try:
        yield
    finally:
        capability._run = original


@contextlib.contextmanager
def clock(moment: datetime = PROBED_AT):
    original = capability._now
    capability._now = lambda: moment
    try:
        yield
    finally:
        capability._now = original


def completed(returncode: int, stdout: bytes = b"", stderr: bytes = b""):
    return subprocess.CompletedProcess(
        list(capability.GH_TOKEN_ARGV), returncode, stdout, stderr
    )


# -- E-22: credential() -------------------------------------------------------


def test_a_successful_gh_auth_token_is_returned_stripped() -> None:
    with process(completed(0, TOKEN.encode() + b"\n")):
        assert credential() == TOKEN


def test_t14_a_non_zero_exit_raises_credential_github_unavailable() -> None:
    with process(completed(1, b"", b"not logged in")):
        try:
            credential()
        except CredentialGithubUnavailable:
            return
    raise AssertionError("a non-zero `gh auth token` did not raise")


def test_t14_the_error_is_a_gate_error_subclass() -> None:
    """§4: no credential is not a policy answer about a repository, it is RQA being
    unable to ask the question at all."""
    assert issubclass(CredentialGithubUnavailable, GateError)


def test_t14_nothing_is_persisted_and_nothing_is_probed_when_the_credential_fails() -> None:
    probe = FakeProbe()
    with process(completed(1, b"", b"not logged in")):
        try:
            probe_capability(REPO, probe, ExplodingStore(), JOB)
        except CredentialGithubUnavailable:
            assert probe.credentials == []
            return
    raise AssertionError("a failed credential read did not stop the probe")


def test_an_absent_gh_binary_raises_credential_github_unavailable() -> None:
    with process(error=FileNotFoundError("gh")):
        try:
            credential()
        except CredentialGithubUnavailable:
            return
    raise AssertionError("an absent `gh` did not raise")


def _chain_text(error: BaseException) -> str:
    """Everything programmatically reachable from a raised exception, not just its text.

    `raise ... from None` sets `__cause__` and `__suppress_context__`, which suppress the
    *display* of a chain; Python still attaches the exception being handled to
    `__context__`, fully intact. On this path that object is a real
    `subprocess.TimeoutExpired` whose `.output` is the credential. A search that stops at
    `str()` cannot see it, which is precisely how it survived round 1.
    """
    seen: list[BaseException] = []
    pending: list[BaseException | None] = [error]
    while pending:
        current = pending.pop()
        if current is None or any(current is item for item in seen):
            continue
        seen.append(current)
        pending.extend([current.__context__, current.__cause__])
    parts: list[str] = []
    for item in seen:
        parts.extend([str(item), repr(item), repr(getattr(item, "args", ()))])
        parts.extend(repr(value) for value in vars(item).values())
        for attribute in ("output", "stdout", "stderr"):
            parts.append(repr(getattr(item, attribute, None)))
        frame = item.__traceback__
        while frame is not None:
            if "rqa/authority/" in frame.tb_frame.f_code.co_filename:
                parts.append(repr(frame.tb_frame.f_locals))
            frame = frame.tb_next
    return "".join(parts)


def test_t14_a_timed_out_credential_read_raises_rather_than_hanging_the_gate() -> None:
    timeout = subprocess.TimeoutExpired(
        list(capability.GH_TOKEN_ARGV), 30.0, output=TOKEN.encode(), stderr=TOKEN.encode()
    )
    with process(error=timeout):
        try:
            credential()
        except CredentialGithubUnavailable as error:
            assert TOKEN not in str(error)
            assert error.__cause__ is None
            # The whole point: the caught timeout must not be reachable from the
            # exception that replaced it.
            assert error.__context__ is None, "the timeout survives on __context__"
            assert TOKEN not in _chain_text(error)
            return
    raise AssertionError("a timed-out `gh auth token` did not raise")


def test_t14_an_absent_gh_binary_severs_its_os_error_too() -> None:
    """Every `OSError` the credential read can raise takes the same path, so every one
    of them is severed — not only the timeout that happens to carry `output`."""
    with process(error=PermissionError(13, "permission denied", "gh")):
        try:
            credential()
        except CredentialGithubUnavailable as error:
            assert error.__context__ is None
            assert error.__cause__ is None
            return
    raise AssertionError("an unrunnable `gh` did not raise")


def test_t14_a_non_zero_exit_leaves_no_token_bearing_frame_on_the_traceback() -> None:
    """The other credential-bearing raise site: `completed.stdout` *is* the token on the
    success path, so the process result must not still be a local when the failure
    branch raises."""
    with process(completed(1, TOKEN.encode(), TOKEN.encode())):
        try:
            credential()
        except CredentialGithubUnavailable as error:
            assert TOKEN not in _chain_text(error)
            return
    raise AssertionError("a non-zero `gh auth token` did not raise")


def test_empty_output_is_no_credential_at_all() -> None:
    with process(completed(0, b"   \n")):
        try:
            credential()
        except CredentialGithubUnavailable:
            return
    raise AssertionError("empty `gh auth token` output was accepted as a credential")


def test_no_failure_message_quotes_the_process_output() -> None:
    """On the success path that output *is* the credential (RQA-NFR-025)."""
    with process(completed(1, TOKEN.encode(), TOKEN.encode())):
        try:
            credential()
        except CredentialGithubUnavailable as error:
            assert TOKEN not in str(error)
            return
    raise AssertionError("a non-zero `gh auth token` did not raise")


# -- E-16: probe_capability() -------------------------------------------------


def test_a_reading_becomes_a_persisted_proof_carrying_its_store_assigned_id() -> None:
    probe = FakeProbe()
    store = FakeStore()
    with process(completed(0, TOKEN.encode())), clock():
        proof = probe_capability(REPO, probe, store, JOB)
    assert proof.id == 7
    assert proof.repo == REPO
    assert proof.job_id == JOB
    assert proof.capabilities == frozenset({"pulls:write"})
    assert proof.attested_not_proven == frozenset({"admin:org"})
    assert proof.login == "rqa-operator"
    assert proof.probed_at == PROBED_AT
    assert len(store.puts) == 1


def test_the_credential_reaches_the_probe_and_nothing_else() -> None:
    probe = FakeProbe()
    store = FakeStore()
    with process(completed(0, TOKEN.encode())), clock():
        proof = probe_capability(REPO, probe, store, JOB)
    assert probe.credentials == [TOKEN]
    assert TOKEN not in repr(proof)
    assert TOKEN not in repr(store.puts)


def test_an_unavailable_adapter_is_persisted_as_an_empty_capability_set() -> None:
    probe = FakeProbe(GithubUnavailable(op="probe", reason="unreachable", retriable=True))
    store = FakeStore()
    with process(completed(0, TOKEN.encode())), clock():
        proof = probe_capability(REPO, probe, store, JOB)
    assert proof.capabilities == frozenset()
    assert proof.attested_not_proven == frozenset()
    assert proof.login == ""
    assert len(store.puts) == 1


def test_a_probe_returning_something_outside_the_e16_union_is_a_programming_error() -> None:
    probe = FakeProbe({"capabilities": ["pulls:write"]})
    with process(completed(0, TOKEN.encode())):
        try:
            probe_capability(REPO, probe, FakeStore(), JOB)
        except GateError:
            return
    raise AssertionError("a probe result outside CapabilityReading | GithubUnavailable was accepted")


def test_probe_capability_keeps_the_positional_signature_section_four_states() -> None:
    import inspect

    signature = inspect.signature(probe_capability)
    assert [
        (name, parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for name, parameter in signature.parameters.items()
    ] == [("repo", True), ("github", True), ("store", True), ("job_id", True)]
    assert signature.return_annotation == "CapabilityProof"


def test_the_e16_reference_declaration_matches_the_edge_signature() -> None:
    """§4 states E-16's shape beside the call that consumes it; `rqa.edges` is where it
    is declared, and the two must not drift."""
    import inspect

    from rqa import edges

    assert inspect.signature(capability._probe_signature_for_reference) == inspect.signature(
        edges.probe
    )


def test_the_github_probe_protocol_repeats_the_edge_signature_as_a_method() -> None:
    import inspect

    from rqa import edges

    method = inspect.signature(capability.GithubProbe.probe)
    free = inspect.signature(edges.probe)
    assert list(method.parameters)[0] == "self"
    assert [
        (name, parameter.annotation) for name, parameter in list(method.parameters.items())[1:]
    ] == [(name, parameter.annotation) for name, parameter in free.parameters.items()]
    assert method.return_annotation == free.return_annotation
