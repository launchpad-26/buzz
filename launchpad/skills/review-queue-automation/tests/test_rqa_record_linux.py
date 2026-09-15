"""Secret Service queries must distinguish missing items from unreadable keyrings."""

import pathlib
import sqlite3
import sys
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import AppendFailed
from rqa.record.keychain import KEY_NAME, KeyStoreExplanationUnavailable, OSKeyStore
from rqa.record.writer import SQLiteRecordWriter


class Responses:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []

    def __call__(self, argv):
        self.calls.append(tuple(argv))
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return result


def test_linux_present_key_is_returned_without_a_write_or_whitespace_loss():
    runner = Responses((0, b" fixture key ", False))
    with patch("rqa.record.keychain.sys.platform", "linux"):
        assert OSKeyStore(linux_runner=runner).read(KEY_NAME) == b" fixture key "
    assert runner.calls == [("secret-tool", "lookup", "service", KEY_NAME)]


def test_linux_absence_requires_both_empty_lookup_and_empty_search():
    runner = Responses((1, b"", False), (0, b"", False))
    with patch("rqa.record.keychain.sys.platform", "linux"):
        assert OSKeyStore(linux_runner=runner).read(KEY_NAME) is None
    assert runner.calls[-1] == ("secret-tool", "search", "--all", "service", KEY_NAME)


def test_linux_locked_broken_missing_and_empty_keys_never_downgrade_to_unkeyed():
    cases = [
        ((1, b"", True),),
        ((1, b"", False), (0, b"[/locked/item]", False)),
        ((1, b"", False), (1, b"", True)),
        ((0, b"", False),),
        (FileNotFoundError("secret-tool"),),
        (TimeoutError("keyring did not answer"),),
    ]
    for responses in cases:
        connection = sqlite3.connect(":memory:")
        runner = Responses(*responses)
        with patch("rqa.record.keychain.sys.platform", "linux"):
            writer = SQLiteRecordWriter(connection, keystore=OSKeyStore(linux_runner=runner))
            try:
                writer.append("fixture-job", "transition", {})
            except AppendFailed:
                pass
            else:
                raise AssertionError("an unavailable keychain was treated as absent")
        assert connection.execute("SELECT count(*) FROM record_entries").fetchone()[0] == 0
        connection.close()


def test_linux_default_store_invokes_secret_tool_and_does_not_expose_diagnostics():
    from subprocess import CompletedProcess
    with patch("rqa.record.keychain.sys.platform", "linux"), patch(
        "rqa.record.keychain.subprocess.run",
        return_value=CompletedProcess([], 1, stdout=b"", stderr=b"private diagnostic"),
    ) as command:
        try:
            OSKeyStore().read(KEY_NAME)
        except KeyStoreExplanationUnavailable as error:
            assert "private diagnostic" not in str(error)
        else:
            raise AssertionError("default Linux store ignored the failed query")
        assert command.call_args.args[0] == ["secret-tool", "lookup", "service", KEY_NAME]
