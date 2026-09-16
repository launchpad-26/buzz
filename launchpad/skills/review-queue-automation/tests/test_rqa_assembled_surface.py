#!/usr/bin/env python3
"""Final assembled RQA package module inventories.

These guards deliberately inspect the filesystem without importing the package under
test. A missing module must fail its invariant assertion, not turn mutation evidence
into an import or collection error.
"""

from __future__ import annotations

import pathlib


RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
FINAL_MODULES = {
    "supply": frozenset(
        {"__init__", "aliases", "ladder", "breakers", "budget", "spend", "probe"}
    ),
    "intake": frozenset(
        {
            "__init__", "identity", "lock", "store", "types", "admission",
            "inventory", "lease", "batch", "tick",
        }
    ),
    "policy": frozenset(
        {"__init__", "schema", "validate", "types", "snapshot", "store", "onboard"}
    ),
    "record": frozenset(
        {
            "__init__", "kinds", "hashing", "store", "writer", "verify", "reader",
            "trace", "anchor", "explain", "migrate",
        }
    ),
    "lifecycle": frozenset(
        {
            "__init__", "states", "errors", "deps", "transition", "status", "admit",
            "steps", "rest", "resume",
        }
    ),
}


def _assert_final_modules(package: str) -> None:
    found = frozenset(path.stem for path in (RQA / package).glob("*.py"))
    expected = FINAL_MODULES[package]
    assert found == expected, (
        f"rqa/{package} module set is not final: expected {sorted(expected)}, "
        f"found {sorted(found)}"
    )


def test_supply_has_exact_final_module_set() -> None:
    _assert_final_modules("supply")


def test_intake_has_exact_final_module_set() -> None:
    _assert_final_modules("intake")


def test_policy_has_exact_final_module_set() -> None:
    _assert_final_modules("policy")


def test_record_has_exact_final_module_set() -> None:
    _assert_final_modules("record")


def test_lifecycle_has_exact_final_module_set() -> None:
    _assert_final_modules("lifecycle")
