#!/usr/bin/env python3
"""`rqa.authority`'s public surface, its seam and its exclusions —
`code/P-08-authority-gate.md` §1, §7, §8's closing property.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Two things these tests deliberately do NOT do:

* They never assert that another package under `rqa/` is absent or unimportable.
  `rqa.github` (#2193) lands in this same wave and `rqa.remediation` (#2194) in a later
  batch; a test pinned to today's tree would have to be deleted then.
* They never pin a tree-wide module, package or test count for the same reason. The
  module set and `__all__` pinned below are P-08's own, which no other lane appends to,
  and they are pinned to §1's finished list rather than to what happens to exist.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.authority  # noqa: E402
import rqa.contracts as contracts  # noqa: E402
from rqa import edges  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
AUTHORITY = RQA / "authority"

#: §1's module list, in full. This package is one lane's work, so this is the finished
#: set, not a stage of it.
MODULES = frozenset({"__init__", "activities", "gate", "capability", "store"})

#: §1's re-export list, in order.
EXPORTS = ["grant", "Activity", "Grant", "Deny", "GateError"]

#: §6: the only two entry kinds P-08 writes.
ENTRY_KINDS_WRITTEN = frozenset({"grant", "attestation"})


def _sources() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8") for path in sorted(AUTHORITY.glob("*.py"))
    }


def _imported(source: str, *, top_level_only: bool = False) -> set[str]:
    """Every module and name this source imports, as dotted strings."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            if not top_level_only:
                for alias in node.names:
                    names.add(f"{node.module}.{alias.name}")
    return names


def _identifiers(source: str) -> set[str]:
    """Every name the source references, including string-indirected ones.

    `ast.Constant` strings are collected too (gate G-2192 F3): a forbidden name reached
    through `getattr(os, "environ")`, `vars(os)["environ"]` or `__import__("os")` appears
    only as a string literal, and a check over `Name`/`Attribute` nodes alone would not
    see it. Membership is exact, so prose in a docstring that merely contains the word
    is not a match.
    """
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
    return names


def _string_literals(source: str) -> list[str]:
    return [
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


# -- §1: modules and re-exports -----------------------------------------------


def test_the_module_set_is_exactly_the_one_section_one_lists() -> None:
    found = frozenset(path.stem for path in AUTHORITY.glob("*.py"))
    assert found == MODULES, f"§1 lists {sorted(MODULES)}; the package has {sorted(found)}"


def test_all_is_exactly_section_ones_re_export_list() -> None:
    assert list(rqa.authority.__all__) == EXPORTS


def test_every_re_exported_name_actually_resolves() -> None:
    missing = [name for name in rqa.authority.__all__ if not hasattr(rqa.authority, name)]
    assert missing == [], f"__all__ names that do not resolve: {missing}"


def test_the_seam_types_are_the_ones_contracts_declares() -> None:
    for name in ("Activity", "Grant", "Deny"):
        assert getattr(rqa.authority, name) is getattr(contracts, name), name


def test_the_package_declares_nothing_it_only_re_exports() -> None:
    """§1: the shared vocabulary has exactly one definition, in `rqa.contracts`."""
    tree = ast.parse((AUTHORITY / "__init__.py").read_text(encoding="utf-8"))
    declarations = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert declarations == []


def test_the_gate_the_proof_and_the_two_collaborators_are_not_package_surface() -> None:
    """They stay submodule names, the way `rqa.policy` keeps `SnapshotStore` out of its
    package surface even though E-03's signature mentions the Protocol."""
    for name in (
        "Gate",
        "CapabilityProof",
        "CapabilityStore",
        "GithubProbe",
        "SqliteCapabilityStore",
        "CredentialGithubUnavailable",
        "REQUIRED_CAPABILITY",
    ):
        assert name not in rqa.authority.__all__, name


def test_no_module_here_is_a_stub() -> None:
    for name, source in _sources().items():
        assert "NotImplementedError" not in source, name
        assert "TODO" not in source, name


# -- the seam: E-04 -----------------------------------------------------------


def test_grant_matches_the_contracts_md_edge_signature_exactly() -> None:
    assert inspect.signature(rqa.authority.grant) == inspect.signature(edges.grant)


def test_the_gate_method_is_the_same_signature_p02_declares_as_authority_client() -> None:
    """`code/P-02-lifecycle.md` §4's `AuthorityClient.grant` is E-04 as a method; the
    object a caller injects and the free function must not drift."""
    from rqa.authority.gate import Gate

    method = inspect.signature(Gate.grant)
    free = inspect.signature(edges.grant)
    assert list(method.parameters)[0] == "self"
    assert [
        (name, parameter.annotation, parameter.kind)
        for name, parameter in list(method.parameters.items())[1:]
    ] == [(name, parameter.annotation, parameter.kind) for name, parameter in free.parameters.items()]
    assert method.return_annotation == free.return_annotation


def test_the_two_collaborator_protocols_stay_empty_in_the_edge_module() -> None:
    """§9 keeps `GithubProbe` and `CapabilityStore` empty placeholders naming P-08 as
    their owner; this package states their shapes, and does not edit the placeholders."""
    for name in ("GithubProbe", "CapabilityStore"):
        placeholder = getattr(edges, name)
        assert [
            attribute for attribute in vars(placeholder) if not attribute.startswith("_")
        ] == [], name


def test_required_capability_covers_every_activity_and_never_implies_another() -> None:
    from rqa.authority.activities import REQUIRED_CAPABILITY

    assert set(REQUIRED_CAPABILITY) == set(contracts.Activity)
    assert REQUIRED_CAPABILITY[contracts.Activity.MERGE] > REQUIRED_CAPABILITY[
        contracts.Activity.APPROVE
    ]


# -- §1: what this package may import -----------------------------------------


def test_no_module_here_imports_a_part_section_one_forbids() -> None:
    """§1: "it never imports `rqa.policy` or `rqa.lifecycle`: the snapshot arrives as an
    argument"."""
    for name, source in _sources().items():
        imported = _imported(source)
        for forbidden in ("rqa.policy", "rqa.lifecycle"):
            assert not any(
                module == forbidden or module.startswith(f"{forbidden}.") for module in imported
            ), f"{name} imports {forbidden}"


def test_the_mechanical_tool_registry_is_resolved_at_call_time_not_at_import() -> None:
    """P-10 need not be present for this gate to be correct, and an unimportable
    registry is an empty one — every configured tool then fails `TOOL_NOT_IN_SET`, which
    is the fail-closed answer rather than an import error."""
    source = (AUTHORITY / "gate.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {node.module for node in tree.body if isinstance(node, ast.ImportFrom) and node.module}
    assert not any(
        module and module.startswith("rqa.remediation") for module in top_level
    ), "P-10 is imported at module level"
    assert "_mechanical_tool_set" in source


# -- §7: what P-08 does not do ------------------------------------------------


def test_no_module_here_reads_a_file_the_environment_or_a_configuration() -> None:
    """§7: "Does not read `.rqa/config.json`, the environment, or any file." The
    snapshot is the only policy source."""
    for name, source in _sources().items():
        identifiers = _identifiers(source)
        for forbidden in ("environ", "getenv", "read_text", "read_bytes", "open"):
            assert forbidden not in identifiers, f"{name} uses {forbidden}"
        assert "config.json" not in source, name


def test_the_only_process_this_package_launches_is_the_credential_read() -> None:
    """E-22 is `gh auth token` and nothing else; no tool runs, no git, no GitHub CLI
    mutation."""
    launchers = sorted(
        name for name, source in _sources().items() if "subprocess" in _imported(source)
    )
    assert launchers == ["capability.py"], launchers
    assert "(\"gh\", \"auth\", \"token\")" in (AUTHORITY / "capability.py").read_text(
        encoding="utf-8"
    )


def test_no_module_here_imports_an_http_client() -> None:
    """§7: P-08 performs no GitHub call at all, including the probe — E-18 makes P-09
    the only HTTP client import in RQA."""
    for name, source in _sources().items():
        imported = _imported(source, top_level_only=True)
        for client in ("urllib", "urllib.request", "http", "http.client", "requests", "httpx"):
            assert client not in imported, f"{name} imports {client}"


def test_no_module_here_escalates_or_transitions_a_job() -> None:
    """§7: it returns a `Deny`; P-02 decides that a `Deny` becomes an escalation. It
    writes no `transition` and never touches `jobs.status`."""
    for name, source in _sources().items():
        identifiers = _identifiers(source)
        for forbidden in ("Escalation", "EscalationCause", "raise_", "JobStatus"):
            assert forbidden not in identifiers, f"{name} references {forbidden}"
        assert "jobs" not in _string_literals(source), name


def test_no_module_here_knows_a_finding() -> None:
    """§7: remediation receives its complete category set and P-08 verifies every
    member; it never sees the finding those categories came from."""
    for name, source in _sources().items():
        assert "Finding" not in _identifiers(source), name
        assert "Remedy" not in _identifiers(source), name


def test_the_only_entry_kinds_written_are_grant_and_attestation() -> None:
    """§6, and `ENTRY_KINDS` is the closed set both belong to."""
    written = set()
    for source in _sources().values():
        for node in ast.walk(ast.parse(source)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
            ):
                written.add(node.args[1].value)
    assert written == ENTRY_KINDS_WRITTEN, written
    assert ENTRY_KINDS_WRITTEN <= contracts.ENTRY_KINDS


# -- §8's closing property and §5's single writer ------------------------------

_AUTHORITY_READ = re.compile(r"authority\[")
_CAPABILITIES_WRITE = re.compile(
    r"INSERT INTO capabilities|UPDATE capabilities|DELETE FROM capabilities"
)


def test_only_the_authority_gate_and_policy_validation_read_an_authority_setting() -> None:
    """§8: `grep -rn "authority\\[" rqa/ --include=*.py` returns hits only under
    `rqa/authority/` and `rqa/policy/` (validation).

    Written over the whole `rqa/` tree as §8 states it, not scoped to this package:
    the property is that no *other* part reads an authority setting, and a scan of one
    package could not see that.
    """
    readers = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if _AUTHORITY_READ.search(path.read_text(encoding="utf-8"))
    )
    strays = [
        path
        for path in readers
        if not (path.startswith("rqa/authority/") or path.startswith("rqa/policy/"))
    ]
    assert strays == [], f"parts other than P-08 and P-03 read an authority setting: {strays}"


def test_only_this_packages_store_writes_the_capabilities_table() -> None:
    """§5: written only by P-08. P-02 reads it through `current()` and nothing else
    touches the rows."""
    writers = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if _CAPABILITIES_WRITE.search(path.read_text(encoding="utf-8"))
    )
    assert writers == ["rqa/authority/store.py"], writers


def test_this_package_writes_no_table_other_than_capabilities() -> None:
    # `UPDATE` requires its trailing `SET` so the `ON CONFLICT ... DO UPDATE SET` of an
    # upsert is not read as a table named `SET`.
    statement = re.compile(
        r"\b(?:INSERT INTO|DELETE FROM|CREATE TABLE(?: IF NOT EXISTS)?)\s+(\w+)"
        r"|\bUPDATE\s+(\w+)\s+SET\b"
    )
    for name, source in _sources().items():
        for literal in _string_literals(source):
            for groups in statement.findall(literal):
                table = next(group for group in groups if group)
                assert table == "capabilities", f"{name} writes {table}"
