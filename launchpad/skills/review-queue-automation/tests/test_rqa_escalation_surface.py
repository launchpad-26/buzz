#!/usr/bin/env python3
"""`rqa.escalation`'s public surface, its seam and its exclusions —
`code/P-11-escalation.md` §1, §2, §5, §6, §7.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

These are structural guards, and each is here because the property it holds is one a
reviewer would otherwise have to re-derive by reading the whole package:

* the package exports exactly §1's list, so a later change cannot widen the surface;
* `human_requests` is written by this package alone, so §5's "written only by P-11"
  claim is tree-wide, not package-local;
* the boundary types (`EscalationCause`, `EscalationSubjectKind`, `EscalationSubject`, `Decision`, `Escalation`,
  `EscalationRefusalReason`, `EscalationRefused`) are imported, never redeclared —
  `test_rqa_contracts_guard.py` checks the CONTRACTS.md-owned half of this tree-wide;
  this file checks the identity match from this package's own side;
* nothing here imports another part's package, `jobs.status` is never read or written,
  and every public function is keyword-only except `decide`'s first four parameters,
  which §3 states are positional-or-keyword.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.escalation  # noqa: E402
from rqa import edges  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
ESCALATION = RQA / "escalation"

#: §1's module list, in full.
MODULES = frozenset({"__init__", "escalate", "decide", "store"})

#: §1's re-export list, verbatim order, then the one concrete store this package publishes
#: so a composition root can construct it through the front door. #2211 (the operator CLI)
#: is the module that falsified §1's "except through `__init__`" sentence: `raise_()`,
#: `pending()` and `decide()` all take their store as a parameter and nothing in
#: `rqa/escalation/` ever builds one, so something outside P-11 always must.
EXPORTS = [
    "raise_",
    "pending",
    "decide",
    "EscalationCause",
    "EscalationSubjectKind",
    "EscalationSubject",
    "Escalation",
    "Decision",
    "EscalationRefused",
    "EscalationRefusalReason",
    "EscalationError",
    "SqliteEscalationStore",
]

#: The names published beyond §1's own list. Asserted positively below, not merely
#: tolerated by the exact-list check.
PUBLISHED = {"SqliteEscalationStore"}

#: §6: the only two entry kinds P-11 writes.
ENTRY_KINDS_WRITTEN = frozenset({"escalation", "decision"})

#: The boundary types §2 says P-11 "imports and uses unchanged".
BOUNDARY_TYPES = (
    "EscalationCause",
    "EscalationSubjectKind",
    "EscalationSubject",
    "Decision",
    "Escalation",
    "EscalationRefusalReason",
    "EscalationRefused",
)


def _sources() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(ESCALATION.glob("*.py"))}


def _imported(source: str) -> set[str]:
    names: set[str] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _appended_kinds(source: str) -> set[str]:
    """The literal `kind=` of every `record.append(...)` call in `source`."""
    tree = ast.parse(source)
    kinds: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append":
            for keyword in node.keywords:
                if keyword.arg == "kind" and isinstance(keyword.value, ast.Constant):
                    kinds.add(keyword.value.value)
            for index, arg in enumerate(node.args):
                if index == 1 and isinstance(arg, ast.Constant):
                    kinds.add(arg.value)
    return kinds


# -- §1: modules and re-exports ---------------------------------------------------


def test_the_module_set_is_exactly_the_one_section_one_lists() -> None:
    found = frozenset(path.stem for path in ESCALATION.glob("*.py"))
    assert found == MODULES, f"§1 lists {sorted(MODULES)}; the package has {sorted(found)}"


def test_all_is_exactly_section_ones_re_export_list() -> None:
    assert list(rqa.escalation.__all__) == EXPORTS


def test_every_re_exported_name_resolves_and_nothing_else_is_surface() -> None:
    missing = [name for name in rqa.escalation.__all__ if not hasattr(rqa.escalation, name)]
    assert missing == []
    # Internal names — never §1 surface. Submodules (`escalate`, `store`) are excluded
    # from this check: Python's import machinery binds an imported submodule as an
    # attribute of its parent package regardless of `__all__`, so `rqa.escalation.store`
    # is always reachable this way — that is a language mechanic, not this package
    # choosing to export its store module. `SqliteEscalationStore` is no longer on this
    # list: it is published surface, asserted positively in the next test.
    for internal in (
        "EscalationRow", "ensure_schema",
        "JobReader", "LifecycleDeps", "LifecycleResume", "utcnow",
    ):
        assert internal not in rqa.escalation.__all__, internal
        assert not hasattr(rqa.escalation, internal), internal


def test_the_concrete_store_a_composition_root_needs_is_package_surface() -> None:
    """§1's "no other module imports from `rqa.escalation` except through `__init__`" and
    `raise_(store=...)` are only jointly satisfiable if the store is reachable through
    `__init__`. The package must publish the store module's own class, not a second copy."""
    from rqa.escalation.store import SqliteEscalationStore

    assert PUBLISHED <= set(rqa.escalation.__all__)
    assert rqa.escalation.SqliteEscalationStore is SqliteEscalationStore


def test_the_package_init_declares_nothing_it_only_re_exports() -> None:
    tree = ast.parse((ESCALATION / "__init__.py").read_text(encoding="utf-8"))
    declarations = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert declarations == []


def test_the_boundary_types_are_the_ones_contracts_declares() -> None:
    for name in BOUNDARY_TYPES:
        assert getattr(rqa.escalation, name) is getattr(contracts, name), name


def test_no_module_here_is_a_stub() -> None:
    for name, source in _sources().items():
        assert "NotImplementedError" not in source, name
        assert "TODO" not in source, name


# -- §3: the two contract-fixed signatures ----------------------------------------


def test_raise_and_pending_match_the_contracts_md_edge_signatures_exactly() -> None:
    assert inspect.signature(rqa.escalation.raise_) == inspect.signature(edges.raise_)
    assert inspect.signature(rqa.escalation.pending) == inspect.signature(edges.pending)


def test_decides_first_four_parameters_are_positional_or_keyword_the_rest_keyword_only() -> None:
    parameters = list(inspect.signature(rqa.escalation.decide).parameters.values())
    positional_or_keyword = [p.name for p in parameters if p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD]
    keyword_only = [p.name for p in parameters if p.kind is inspect.Parameter.KEYWORD_ONLY]
    assert positional_or_keyword == ["escalation_id", "actor", "basis", "outcome"]
    assert keyword_only == ["store", "record", "jobs", "lifecycle", "deps", "clock"]


def test_every_other_public_function_here_is_keyword_only() -> None:
    """CONTRACTS.md preamble: every function keyword-only, unconditionally — except
    `decide`'s first four, which §3 states positional-or-keyword."""
    for name in ("raise_", "pending"):
        function = getattr(rqa.escalation, name)
        positional = [
            p.name
            for p in inspect.signature(function).parameters.values()
            if p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        ]
        assert positional == [], f"{name} takes {positional}"


# -- §5/§6: the store and the record entries --------------------------------------


def test_this_package_is_the_only_writer_of_human_requests_in_the_tree() -> None:
    """§5: "written only by P-11" — checked tree-wide, not package-locally."""
    writers = []
    for path in sorted(RQA.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "human_requests" in source and ("INSERT INTO human_requests" in source or "UPDATE human_requests" in source):
            writers.append(str(path.relative_to(RQA.parent)))
    assert writers == ["rqa/escalation/store.py"], writers


def test_no_module_here_writes_any_entry_kind_but_escalation_and_decision() -> None:
    kinds: set[str] = set()
    for source in _sources().values():
        kinds |= _appended_kinds(source)
    assert kinds == ENTRY_KINDS_WRITTEN, kinds


# -- §1/§7: the import graph and the exclusions -----------------------------------


def test_no_module_here_imports_another_parts_package() -> None:
    """§1: "no module in rqa.escalation imports from any other part except
    rqa.contracts... and rqa.record" — and this package, in fact, needs neither
    `rqa.record` (append arrives through the injected `RecordWriter`) nor anything
    beyond `rqa.contracts` and its own submodules."""
    allowed_roots = {"rqa.contracts", "rqa.escalation", "collections", "dataclasses", "datetime",
                      "types", "typing", "json", "sqlite3", "__future__"}
    for name, source in _sources().items():
        for module in _imported(source):
            root = module.split(".")[0] if not module.startswith("rqa.") else ".".join(module.split(".")[:2])
            assert root in allowed_roots or module in allowed_roots, f"{name} imports {module}"


def test_no_module_here_reads_or_writes_jobs_status() -> None:
    """§1/§7: P-11 never reads or writes `jobs.status`; only P-02 changes a job's
    state."""
    for name, source in _sources().items():
        assert "jobs.status" not in source, name
        assert "UPDATE jobs" not in source, name
        assert "FROM jobs" not in source, name


def test_no_module_here_imports_rqa_intake_or_rqa_lifecycle() -> None:
    for name, source in _sources().items():
        imported = _imported(source)
        for forbidden in ("rqa.intake", "rqa.lifecycle"):
            assert not any(entry.startswith(forbidden) for entry in imported), f"{name}: {forbidden}"


def test_no_module_here_does_not_verify_expire_or_re_run_judgement() -> None:
    """§7's exclusions that are checkable as absent identifiers: no expiry timer, no
    harness invocation, no re-judgement call."""
    for name, source in _sources().items():
        for forbidden in ("timedelta(days", "harness.run", "judge(", "plan("):
            assert forbidden not in source, f"{name} contains {forbidden!r}"


def test_the_package_ships_no_pep_695_type_alias() -> None:
    """CI gates on Python 3.11, where `type X = A | B` is a parse-time `SyntaxError`."""
    alias_node = getattr(ast, "TypeAlias", None)
    for name, source in _sources().items():
        tree = ast.parse(source)
        if alias_node is not None:
            assert not any(isinstance(node, alias_node) for node in ast.walk(tree)), name
