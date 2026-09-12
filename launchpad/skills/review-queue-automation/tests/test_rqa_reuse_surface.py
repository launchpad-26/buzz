#!/usr/bin/env python3
"""P-13 §1/§3/§5/§7 — exact package surface, seam signature, and exclusions."""

from __future__ import annotations

import ast
import inspect
import pathlib
import sys
from typing import get_type_hints

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.reuse  # noqa: E402
from rqa.contracts import (  # noqa: E402
    CarryOver,
    Facts,
    Job,
    RecordReader,
    RecordWriter,
    Snapshot,
)
from rqa.reuse import Reason, ReuseError, carry_over  # noqa: E402

REUSE = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "reuse"
MODULES = frozenset({"__init__", "obligations", "pin", "reuse"})
EXPORTS = ["carry_over", "Reason", "ReuseError"]


def _sources() -> dict[str, str]:
    return {
        path.stem: path.read_text(encoding="utf-8")
        for path in sorted(REUSE.glob("*.py"))
    }


def _imports(*, source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _qualified_match_call(*, node: ast.Call) -> bool:
    function = node.func
    return (
        isinstance(function, ast.Attribute)
        and function.attr == "matches"
        and isinstance(function.value, ast.Attribute)
        and function.value.attr == "paths"
        and isinstance(function.value.value, ast.Attribute)
        and function.value.value.attr == "protocol"
        and isinstance(function.value.value.value, ast.Name)
        and function.value.value.value.id == "rqa"
    )


def test_section_one_module_set_is_exactly_the_four_owned_files() -> None:
    assert frozenset(path.stem for path in REUSE.glob("*.py")) == MODULES


def test_section_one_package_exports_are_exact_and_resolve() -> None:
    assert rqa.reuse.__all__ == EXPORTS
    assert rqa.reuse.carry_over is carry_over
    assert rqa.reuse.Reason is Reason
    assert rqa.reuse.ReuseError is ReuseError


def test_section_two_reason_vocabulary_and_error_role_are_exact() -> None:
    assert {member.name: member.value for member in Reason} == {
        "PATH_TOUCHED": "path_touched",
        "PIN_CHANGED": "pin_changed",
        "NOT_VERIFIED": "not_verified",
        "NEW_OBLIGATION": "new_obligation",
        "NO_PRIOR_JUDGEMENT": "no_prior_judgement",
        "NO_PREDECESSOR": "no_predecessor",
        "UNTRUSTED_PREDECESSOR": "untrusted_predecessor",
        "UNCHANGED_VERIFIED": "unchanged_verified",
    }
    assert issubclass(ReuseError, Exception)


def test_e05_signature_is_keyword_only_and_uses_the_shared_types() -> None:
    signature = inspect.signature(carry_over)
    assert list(signature.parameters) == ["job", "prior", "facts", "snapshot", "record"]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    hints = get_type_hints(carry_over)
    assert hints == {
        "job": Job,
        "prior": RecordReader,
        "facts": Facts,
        "snapshot": Snapshot,
        "record": RecordWriter,
        "return": CarryOver,
    }


def test_only_the_qualified_protocol_matcher_is_called_for_paths() -> None:
    sources = _sources()
    calls = [
        node
        for node in ast.walk(ast.parse(sources["obligations"]))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"matches", "match", "fnmatch", "fnmatchcase"}
    ]
    assert len(calls) == 1
    assert _qualified_match_call(node=calls[0])
    for name, source in sources.items():
        imports = _imports(source=source)
        assert not imports & {"fnmatch", "glob", "re", "pathlib"}, name


def test_package_has_no_store_io_network_model_or_process_dependency() -> None:
    forbidden_imports = {
        "asyncio",
        "http",
        "requests",
        "socket",
        "sqlite3",
        "subprocess",
        "urllib",
    }
    for name, source in _sources().items():
        assert not _imports(source=source) & forbidden_imports, name
        tree = ast.parse(source)
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not called & {"open", "exec", "eval", "compile"}, name


def test_package_never_uses_unauthenticated_reader_methods_or_catches_append_failed() -> None:
    for name, source in _sources().items():
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "prior":
                    assert node.func.attr == "trusted_prefix", f"{name}: prior.{node.func.attr}"
            if isinstance(node, ast.ExceptHandler):
                assert node.type is not None, f"{name}: bare except"
                if isinstance(node.type, ast.Name):
                    assert node.type.id not in {"AppendFailed", "Exception", "BaseException"}, name
