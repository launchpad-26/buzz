#!/usr/bin/env python3
"""E-25's key store, and the no-network property — `code/P-12-record.md` §2, §4, §7,
and §8's T7 technique applied to this lane's half.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

**No test here touches a real keychain.** `OSKeyStore`'s one subprocess is injected, so
every branch — key present, item absent, command unaskable — is exercised without a key
existing on the machine running the suite, and without `security` ever being executed.
"""

from __future__ import annotations

import pathlib
import socket
import sqlite3
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.record.keychain as keychain  # noqa: E402
from rqa.contracts import KeyStore  # noqa: E402
from rqa.record import KeyStoreExplanationUnavailable, verify  # noqa: E402
from rqa.record.keychain import KEY_NAME, OSKeyStore  # noqa: E402
from rqa.record.reader import SQLiteRecordReader  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

SECRET = b"a-test-key-that-never-leaves-this-process"


class RecordingRunner:
    """Stands in for the local keychain command."""

    def __init__(self, *, returncode: int = 0, stdout: bytes = SECRET + b"\n", error=None):
        self.returncode = returncode
        self.stdout = stdout
        self.error = error
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, argv):
        self.calls.append(tuple(argv))
        if self.error is not None:
            raise self.error
        return self.returncode, self.stdout


def darwin(monkeypatched: str = "darwin"):
    """`OSKeyStore` refuses to guess at a platform command; pin the platform for the
    branches that are about the command's answer rather than about its absence."""
    original = keychain.sys.platform
    keychain.sys.platform = monkeypatched
    return original


class FakeKeyStore:
    def __init__(self, *, key: bytes | None = SECRET):
        self.key = key

    def read(self, name: str) -> bytes | None:
        return self.key


# -- the shape E-25 fixes ------------------------------------------------------


def test_os_key_store_implements_the_key_store_protocol_signature() -> None:
    """`CONTRACTS.md` §9: `def read(self, name: str) -> bytes | None`, positional."""
    import inspect

    declared = inspect.signature(KeyStore.read)
    implemented = inspect.signature(OSKeyStore.read)
    assert [(p.name, p.kind) for p in implemented.parameters.values()] == [
        (p.name, p.kind) for p in declared.parameters.values()
    ]
    assert implemented.return_annotation == declared.return_annotation


def test_the_one_item_this_part_reads_is_named_by_the_contract() -> None:
    """§3.1 step 5 and §3.2 step 3 both name `rqa-record-hmac`."""
    assert KEY_NAME == "rqa-record-hmac"


# -- the three answers ---------------------------------------------------------


def test_a_present_item_returns_its_bytes_from_a_local_command() -> None:
    runner = RecordingRunner()
    original = darwin()
    try:
        assert OSKeyStore(runner=runner).read(KEY_NAME) == SECRET
    finally:
        keychain.sys.platform = original
    assert runner.calls == [("security", "find-generic-password", "-w", "-s", KEY_NAME)]


def test_an_absent_item_is_none_rather_than_an_error() -> None:
    """ADR-0063: absent is a specified outcome — `append` proceeds unkeyed and says so."""
    runner = RecordingRunner(returncode=44, stdout=b"")
    original = darwin()
    try:
        assert OSKeyStore(runner=runner).read(KEY_NAME) is None
    finally:
        keychain.sys.platform = original


def test_a_command_that_fails_is_unavailable_rather_than_absent() -> None:
    """§2: "This differs from an absent item, for which `KeyStore.read()` returns None"."""
    original = darwin()
    try:
        for runner in (
            RecordingRunner(returncode=1, stdout=b"keychain internals"),
            RecordingRunner(error=OSError("security: not found")),
            RecordingRunner(error=subprocess.TimeoutExpired("security", 10.0)),
            RecordingRunner(returncode=0, stdout=b"   \n"),
        ):
            raised = False
            try:
                OSKeyStore(runner=runner).read(KEY_NAME)
            except KeyStoreExplanationUnavailable:
                raised = True
            assert raised, f"{runner.__dict__} should be unavailable, not absent"
    finally:
        keychain.sys.platform = original


def test_a_failure_message_never_carries_the_commands_own_output() -> None:
    """§6 of this part's boundary: the keychain's output can carry item contents, and
    this message reaches logs and `AppendFailed`."""
    runner = RecordingRunner(returncode=1, stdout=b"password: " + SECRET)
    original = darwin()
    try:
        OSKeyStore(runner=runner).read(KEY_NAME)
    except KeyStoreExplanationUnavailable as exc:
        assert SECRET.decode() not in str(exc)
        assert "password" not in str(exc)
    finally:
        keychain.sys.platform = original


def test_it_reads_only_its_own_item_and_never_another_name() -> None:
    """§2: "Reads only `rqa-record-hmac`". A caller asking for something else gets an
    unavailable answer, not a general-purpose keychain reader."""
    runner = RecordingRunner()
    raised = False
    try:
        OSKeyStore(runner=runner).read("some-other-credential")
    except KeyStoreExplanationUnavailable:
        raised = True
    assert raised
    assert runner.calls == [], "nothing was executed"


def test_a_platform_without_the_command_is_unavailable_not_a_guess() -> None:
    runner = RecordingRunner()
    original = darwin("linux")
    try:
        raised = False
        try:
            OSKeyStore(runner=runner).read(KEY_NAME)
        except KeyStoreExplanationUnavailable:
            raised = True
        assert raised
        assert runner.calls == []
    finally:
        keychain.sys.platform = original


def test_this_part_never_writes_generates_or_rotates_a_key() -> None:
    """§7: "Does not generate, rotate, or write the operator's HMAC key into the OS
    keychain — only reads it". The command this module can build is a read."""
    source = pathlib.Path(keychain.__file__).read_text(encoding="utf-8")
    for verb in ("add-generic-password", "delete-generic-password", "set-generic-password"):
        assert verb not in source
    assert "find-generic-password" in source
    assert not hasattr(OSKeyStore, "write")
    assert not hasattr(OSKeyStore, "rotate")


# -- T7's technique: this half of the package touches no network ---------------


def test_t7_appending_verifying_and_reading_work_with_every_socket_poisoned() -> None:
    """T7's technique applied to this lane's entry points: with `socket.socket` and
    `subprocess.run` replaced by raisers, a full append/verify/read cycle completes.

    §1: "Nothing in this package opens a socket, spawns `gh` or `git`, or invokes a
    model", proved behaviourally rather than by reading the source.
    """

    def no_sockets(*args, **kwargs):
        raise AssertionError("rqa.record opened a socket")

    def no_subprocesses(*args, **kwargs):
        raise AssertionError("rqa.record spawned a process")

    original_socket = socket.socket
    original_run = subprocess.run
    socket.socket = no_sockets  # type: ignore[assignment]
    subprocess.run = no_subprocesses  # type: ignore[assignment]
    try:
        keystore = FakeKeyStore()
        connection = sqlite3.connect(":memory:")
        writer = SQLiteRecordWriter(connection, keystore=keystore)
        writer.append("job-1", "transition", {"to_state": "queued", "repo": "o/r", "number": 7})
        writer.append("job-1", "judgement", {"disposition": "approve"})
        assert verify(connection, "job-1", keystore=keystore).ok is True
        reader = SQLiteRecordReader(connection, keystore=keystore)
        assert len(reader.entries("job-1")) == 2
        assert reader.latest("job-1", "judgement") is not None
        assert reader.trusted_prefix("job-1").checked_through_seq == 2
    finally:
        socket.socket = original_socket  # type: ignore[assignment]
        subprocess.run = original_run  # type: ignore[assignment]
