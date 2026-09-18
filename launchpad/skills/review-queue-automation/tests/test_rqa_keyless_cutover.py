"""#2299's end-to-end keyless-cutover guard.

The focused record tests prove individual behaviours. This test owns the cross-surface
claim that ADR-0066 removed the credential-store seam rather than merely making one
code path skip it: the public APIs expose no keystore, old keyed rows remain readable,
new rows are unkeyed, and the record package stays stdlib-only.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.cli.composition import anchor_job_for, build_composition  # noqa: E402
from rqa.record import SQLiteRecordReader, SQLiteRecordWriter, verify  # noqa: E402
from rqa.record.explain import explain, explain_job  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECORD = ROOT / "rqa" / "record"
_FORBIDDEN_SEAM_NAMES = frozenset(
    {"KEY_NAME", "OSKeyStore", "KeyStoreExplanationUnavailable", "KeyStore"}
)
_FORBIDDEN_COMMANDS = frozenset({"security", "secret-tool"})


def _executable_strings(source: str) -> set[str]:
    """String literals excluding docstrings, which may honestly describe history."""
    tree = ast.parse(source)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                docstrings.add(id(first.value))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    }


def _imports(source: str) -> set[str]:
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    return imported


def test_the_keychain_module_and_credential_store_seam_are_absent() -> None:
    assert not (RECORD / "keychain.py").exists()

    for path in RECORD.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        identifiers = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        } | {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        assert not (identifiers & _FORBIDDEN_SEAM_NAMES), path
        assert not (_executable_strings(source) & _FORBIDDEN_COMMANDS), path


def test_record_and_composition_apis_take_no_keystore() -> None:
    surfaces = (
        SQLiteRecordWriter.__init__,
        SQLiteRecordWriter.append,
        SQLiteRecordReader.__init__,
        SQLiteRecordReader.entries,
        SQLiteRecordReader.latest,
        SQLiteRecordReader.trusted_prefix,
        verify,
        explain,
        explain_job,
        build_composition,
        anchor_job_for,
    )
    for surface in surfaces:
        parameters = inspect.signature(surface).parameters
        forbidden = [name for name in parameters if "key" in name.lower()]
        assert forbidden == [], f"{surface.__qualname__} still takes {forbidden}"


def test_historical_keyed_rows_stay_chain_valid_and_new_rows_are_unkeyed() -> None:
    connection = sqlite3.connect(":memory:")
    clock = lambda: datetime(2026, 9, 18, tzinfo=timezone.utc)
    writer = SQLiteRecordWriter(connection, clock=clock)

    old = writer.append("job-1", "transition", {"to_state": "queued"})
    connection.execute(
        "UPDATE record_entries SET keyed = 1, hmac = 'legacy-hmac' WHERE job = ? AND seq = ?",
        ("job-1", old.seq),
    )
    connection.execute(
        "UPDATE record_heads SET keyed = 1, hmac = 'legacy-hmac' WHERE job = ?",
        ("job-1",),
    )

    assert verify(connection, "job-1").ok is True

    new = writer.append("job-1", "plan", {"obligations": []})
    keyed, hmac = connection.execute(
        "SELECT keyed, hmac FROM record_entries WHERE job = ? AND seq = ?",
        ("job-1", new.seq),
    ).fetchone()
    assert (keyed, hmac) == (0, None)
    assert verify(connection, "job-1").ok is True


def test_record_package_imports_only_stdlib_or_rqa_modules() -> None:
    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    for path in RECORD.glob("*.py"):
        for imported in _imports(path.read_text(encoding="utf-8")):
            root = imported.split(".", 1)[0]
            assert root in stdlib or root == "rqa", f"{path.name}: {imported}"
