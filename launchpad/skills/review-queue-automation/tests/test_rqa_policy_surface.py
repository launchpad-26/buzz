#!/usr/bin/env python3
"""`rqa.policy`'s public surface and its exclusions — `code/P-03-policy.md` §1, §7.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

**Why the module and export assertions name two states.** §1 specifies seven modules
and eighteen re-exports for the finished package. The `onboard` half (`onboard.py`
and its five names) is a sibling lane's, landing separately. A test frozen to the
six-module / thirteen-name state this lane produces would have to be edited when that
lane merges, and a test frozen to the finished state would fail until it does.
Asserting membership of exactly those two real states catches both a lane adding
surface §1 does not specify and a botched merge that lands half a package — while
never asserting that a sibling's contract-required work is absent
(`plan-rqa.md` §7, D-B1-3).
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.policy  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
POLICY = RQA / "policy"

#: §1's module list, split by the lane that builds each module.
VALIDATION_MODULES = frozenset({"__init__", "schema", "validate", "types", "snapshot", "store"})
ONBOARD_MODULES = frozenset({"onboard"})
ALL_MODULES = VALIDATION_MODULES | ONBOARD_MODULES

#: §1's re-export list, split the same way.
VALIDATION_EXPORTS = frozenset(
    {
        "Snapshot",
        "Route",
        "External",
        "Policy",
        "Blocking",
        "Mechanical",
        "Budget",
        "snapshot_for",
        "ValidationError",
        "ValidationErrorCode",
        "ValidationFailure",
        "PolicyError",
        "SnapshotStoreCorrupted",
    }
)
ONBOARD_EXPORTS = frozenset(
    {"onboard", "OnboardResult", "Written", "OnboardRefusal", "OnboardRefusalReason"}
)
ALL_EXPORTS = VALIDATION_EXPORTS | ONBOARD_EXPORTS


def _sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(POLICY.glob("*.py"))
    }


def _imported(source: str, *, top_level_only: bool = False) -> set[str]:
    """Every module and name this source imports, as dotted strings.

    The exclusion tests below check what this part *uses*, and its docstrings quote
    several of the names it must not use — "uses neither `fnmatch` nor
    `PurePath.match`" is exactly the promise being checked. A raw text scan would
    report the documentation of a rule as a breach of it, so the imports and
    identifiers come from the syntax tree instead.
    """
    tree = ast.parse(source)
    nodes = tree.body if top_level_only else list(ast.walk(tree))
    names: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.add(module)
            names.update(f"{module}.{alias.name}" for alias in node.names)
    return names


def _identifiers(source: str) -> set[str]:
    """Every bare name and attribute name the source actually references."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def test_the_module_set_is_one_of_the_two_states_section_one_specifies() -> None:
    found = frozenset(path.stem for path in POLICY.glob("*.py"))
    assert found in (VALIDATION_MODULES, ALL_MODULES), (
        f"rqa/policy holds {sorted(found)}; §1 specifies {sorted(ALL_MODULES)}, of which "
        f"{sorted(VALIDATION_MODULES)} is the pre-onboard state"
    )


def test_all_is_one_of_the_two_states_section_one_specifies() -> None:
    exported = list(rqa.policy.__all__)
    assert len(exported) == len(set(exported)), f"duplicate re-export: {exported}"
    assert frozenset(exported) in (VALIDATION_EXPORTS, ALL_EXPORTS), (
        f"__all__ is {sorted(exported)}; §1 specifies {sorted(ALL_EXPORTS)}"
    )


def test_every_re_exported_name_actually_resolves() -> None:
    missing = [name for name in rqa.policy.__all__ if not hasattr(rqa.policy, name)]
    assert missing == [], f"__all__ names that do not resolve: {missing}"


def test_the_store_protocol_and_its_row_type_are_not_public_package_surface() -> None:
    """`SnapshotStore` and `StoredSnapshot` stay `rqa.policy.store` names even though
    E-03's signature mentions the Protocol: they are not in §1's re-export list."""
    assert "SnapshotStore" not in rqa.policy.__all__
    assert "StoredSnapshot" not in rqa.policy.__all__


def test_the_package_declares_nothing_it_only_re_exports() -> None:
    """§1: the shared vocabulary has exactly one definition, in `rqa.contracts`."""
    import ast

    tree = ast.parse((POLICY / "__init__.py").read_text(encoding="utf-8"))
    declarations = [
        node
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert declarations == []


def test_the_seam_types_are_the_ones_contracts_declares() -> None:
    import rqa.contracts as contracts

    for name in ("Snapshot", "Route", "External", "Policy", "Blocking", "Mechanical", "Budget"):
        assert getattr(rqa.policy, name) is getattr(contracts, name), name


# -- §7: what this part does not do -------------------------------------------

_SNAPSHOT_WRITE = re.compile(
    r"(INSERT\s+(OR\s+\w+\s+)?INTO|UPDATE|DELETE\s+FROM|CREATE\s+TABLE[^;]*?)\s+(IF\s+NOT\s+EXISTS\s+)?snapshots",
    re.IGNORECASE | re.DOTALL,
)


def test_only_the_policy_store_writes_the_snapshots_store() -> None:
    """`container.md` §5: `snapshots` is written by P-03 and by nothing else.

    Scoped to the `rqa/` tree, which is the new estate. The legacy `scripts/`
    snapshot store is superseded, not imported by anything here, and is handed to
    `CUTOVER.md` for deletion.
    """
    writers = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if _SNAPSHOT_WRITE.search(path.read_text(encoding="utf-8"))
    )
    assert writers == ["rqa/policy/store.py"], writers


def test_the_store_never_deletes_or_updates_a_snapshot_row_or_file() -> None:
    source = (POLICY / "store.py").read_text(encoding="utf-8")
    assert not re.search(r"\bDELETE\s+FROM\b", source, re.IGNORECASE)
    assert not re.search(r"\bUPDATE\s+snapshots\b", source, re.IGNORECASE)
    # `unlink` appears once, on the temp file of a failed write, never on an archive.
    assert source.count("unlink") == 1
    assert "temporary.unlink" in source


def test_no_module_here_writes_the_jobs_table() -> None:
    """§7: `jobs.status` and `jobs.snapshot_hash` belong to P-01/P-02."""
    for name, source in _sources().items():
        assert not re.search(
            r"(INSERT|UPDATE|DELETE)[^;]{0,40}\bjobs\b", source, re.IGNORECASE
        ), name


def test_no_module_here_defines_its_own_path_matching() -> None:
    """§4, §7: `rqa.protocol.paths.matches` is the only matcher in RQA — P-03 uses
    neither `fnmatch` nor `PurePath.match` nor a regex over patterns."""
    for name, source in _sources().items():
        imported = _imported(source)
        assert not {"fnmatch", "re", "glob"} & imported, name
        identifiers = _identifiers(source)
        for forbidden in ("PurePath", "fnmatch", "match", "fullmatch", "compile"):
            assert forbidden not in identifiers, f"{name} uses {forbidden}"
    # The one sanctioned matcher call, made through the qualified module P-04 §2
    # mandates, with the pattern validated by the matcher's own grammar.
    validator = (POLICY / "validate.py").read_text(encoding="utf-8")
    assert "matches" in _identifiers(validator)
    assert "rqa.protocol.paths" in _imported(validator)


def test_no_module_here_reaches_a_credential_a_process_or_the_network() -> None:
    """§7: no credential probe, no GitHub call, no notification, no tool run."""
    forbidden = {
        "subprocess",
        "socket",
        "urllib",
        "urllib.request",
        "http",
        "http.client",
        "requests",
        "ssl",
        "smtplib",
    }
    for name, source in _sources().items():
        assert not forbidden & _imported(source), name
        assert "GITHUB_TOKEN" not in _identifiers(source), name
        assert "environ" not in _identifiers(source), name


def test_no_module_here_imports_a_part_section_one_forbids() -> None:
    """§1: never `rqa.lifecycle`, `rqa.github` or `rqa.judgement` — nothing here
    decides an authority question or interprets a finding. `rqa.record` is not
    imported either: E-13 is reached through `CONTRACTS.md` §7's `RecordWriter`
    Protocol, which the caller supplies. `rqa.remediation` is reached only through
    the call-time membership lookup inside `validate.py`, never at import."""
    for name, source in _sources().items():
        imported = _imported(source)
        for forbidden in ("rqa.lifecycle", "rqa.github", "rqa.judgement", "rqa.record"):
            offences = {item for item in imported if item.startswith(forbidden)}
            assert offences == set(), f"{name} imports {sorted(offences)}"
        # P-10's registry is resolved inside `validate()`, so no module here imports
        # `rqa.remediation` at import time — which is what keeps `rqa.policy`
        # importable before P-10 exists, with an empty (fail-closed) registry.
        assert "rqa.remediation" not in _imported(source, top_level_only=True), name


def test_the_onboard_module_is_not_stubbed_by_this_lane() -> None:
    """A stub would satisfy §1's module list while hiding an unbuilt entry point.
    Either `onboard.py` is the sibling lane's real module or it is not here yet."""
    onboard = POLICY / "onboard.py"
    if not onboard.is_file():
        return
    source = onboard.read_text(encoding="utf-8")
    assert "def onboard(" in source
    assert "NotImplementedError" not in source
