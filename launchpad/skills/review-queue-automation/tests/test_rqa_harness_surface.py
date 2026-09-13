#!/usr/bin/env python3
"""`rqa.harness`'s public surface, its seam and its exclusions — P-06 §1, §2, §6, §7.

§1 fixes seven modules and six re-exports, and "no extra public surface" is a
definition-of-done clause rather than a preference. §7 is the authoritative exclusion
list. Everything here is a structural assertion over the package as shipped, so a later
change that quietly widens the surface, adds a second path matcher, mints a `Verdict` or
a `Spend`, or writes a record kind P-06 does not own fails a test instead of a review.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.harness  # noqa: E402
from rqa import edges  # noqa: E402
from rqa.harness import adapters, bundle, errors, invoke, panel, risk  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
HARNESS = RQA / "harness"

#: §1's module list, verbatim.
MODULES = frozenset({"__init__", "risk", "bundle", "adapters", "invoke", "panel", "errors"})

#: §1's re-export list, verbatim.
EXPORTS = frozenset({"plan", "run", "SupplyPort", "HarnessAdapter", "BundleFailure", "HarnessError"})

#: §6's four rows: the only record kinds this part writes.
ENTRY_KINDS_WRITTEN = frozenset({"plan", "bundle", "attestation", "panel"})

#: Every other part's package. §1 lets this one import the shared seam (`rqa.contracts`,
#: `rqa.edges`) and exactly two neighbours' *published* surfaces: `rqa.protocol` (E-08 and
#: the path matcher) and, for its payload rule, nothing else.
OTHER_PARTS = ("rqa.supply", "rqa.policy", "rqa.authority", "rqa.github", "rqa.record")


def _sources() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(HARNESS.glob("*.py"))}


def _trees() -> dict[str, ast.Module]:
    return {name: ast.parse(source) for name, source in _sources().items()}


# -- §1: modules and re-exports -------------------------------------------------


def test_the_module_set_is_exactly_the_seven_section_one_lists() -> None:
    assert frozenset(path.stem for path in HARNESS.glob("*.py")) == MODULES


def test_all_is_exactly_the_six_names_section_one_re_exports() -> None:
    assert frozenset(rqa.harness.__all__) == EXPORTS
    assert len(rqa.harness.__all__) == len(EXPORTS)


def test_every_re_exported_name_resolves() -> None:
    missing = [name for name in rqa.harness.__all__ if not hasattr(rqa.harness, name)]
    assert missing == []


def test_there_is_no_extra_public_surface_on_the_package() -> None:
    """Anything the package needs beyond §1's six is a submodule name, not a package one."""
    public = {
        name
        for name in vars(rqa.harness)
        # `annotations` is the `__future__` feature flag every module in this repository
        # imports; it is a language directive, not part of anyone's surface.
        if not name.startswith("_")
        and name != "annotations"
        and not inspect.ismodule(getattr(rqa.harness, name))
    }
    assert public == EXPORTS


def test_the_package_declares_nothing_it_only_re_exports() -> None:
    tree = ast.parse((HARNESS / "__init__.py").read_text(encoding="utf-8"))
    declared = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    assert declared == []


def test_the_shared_types_are_imported_not_restated() -> None:
    """The seam rule: `SupplyPort` and `BundleFailure` have one definition each, and it is
    not in this package. `rqa/edges.py` landed §9's E-07 Protocol; restating §2's printed
    form here would be a second definition of a shared name."""
    assert rqa.harness.SupplyPort is contracts.SupplyPort is edges.SupplyPort
    assert rqa.harness.BundleFailure is contracts.BundleFailure
    for name, source in _sources().items():
        assert "class SupplyPort" not in source, name
        assert "class BundleFailure" not in source, name


def test_the_adapter_protocol_is_this_parts_own() -> None:
    """§2: "P-06 defines only its private adapter and programming-error types"."""
    assert not hasattr(contracts, "HarnessAdapter")
    assert rqa.harness.HarnessAdapter is adapters.HarnessAdapter


def test_errors_declares_exactly_the_three_section_two_names() -> None:
    tree = ast.parse((HARNESS / "errors.py").read_text(encoding="utf-8"))
    declared = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    assert declared == ["HarnessError", "EmptyPlanError", "ProtocolVersionUnknown"]
    assert issubclass(errors.EmptyPlanError, errors.HarnessError)
    assert issubclass(errors.ProtocolVersionUnknown, errors.HarnessError)


def test_no_module_here_is_a_stub() -> None:
    for name, source in _sources().items():
        assert "NotImplementedError" not in source, name
        assert "TODO" not in source, name
        assert "pragma: no cover" not in source, name


# -- the seam: E-07 and E-08 ----------------------------------------------------


def test_plan_and_run_match_the_contracts_md_edge_signatures_exactly() -> None:
    assert inspect.signature(rqa.harness.plan) == inspect.signature(edges.plan)
    assert inspect.signature(rqa.harness.run) == inspect.signature(edges.run)


def test_the_supply_port_protocol_is_the_narrow_positional_view_the_contract_states() -> None:
    """§2 prints `SupplyPort`'s three methods in positional form on purpose: it is P-06's
    *view* of E-06 and E-15, not their full keyword-only signatures, which stay P-05's."""
    for name, expected in (
        ("route", ["self", "obligation", "cursor"]),
        ("reserve", ["self", "plan", "route"]),
        ("consumed", ["self", "attempt", "reading", "reservation"]),
    ):
        signature = inspect.signature(getattr(contracts.SupplyPort, name))
        assert list(signature.parameters) == expected
        for parameter in list(signature.parameters.values())[1:]:
            assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD, f"{name}.{parameter.name}"


def test_the_adapter_protocol_methods_are_positional_as_the_contract_fixes_them() -> None:
    for name, expected in (("argv", ["self", "route", "effort"]), ("resolved_effort", ["self", "requested"])):
        assert list(inspect.signature(getattr(adapters.HarnessAdapter, name)).parameters) == expected


def test_e08_is_the_only_validator_and_this_part_never_mints_a_verdict() -> None:
    """§4 and §7: P-06 consumes `validate` exactly as declared and never parses
    `verdict.json` itself to decide validity."""
    from rqa.protocol import validate

    assert inspect.signature(validate) == inspect.signature(edges.validate)
    assert panel.validate is validate
    for name, tree in _trees().items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"Verdict", "Valid", "Invalid", "Spend"}, (
                    f"{name} constructs {node.func.id}"
                )


def test_this_part_never_mints_a_spend_it_only_reports_a_reading() -> None:
    """§7 and the settled Batch 2b reading: P-06 hands P-05 a reading; the `Spend` that
    comes back is P-05's answer, not P-06's construction."""
    for name, source in _sources().items():
        assert "Spend(" not in source, name
    assert "reading" in inspect.getsource(panel.run)
    signature = inspect.signature(contracts.SupplyPort.consumed)
    assert signature.parameters["reading"].annotation == "int | None"


def test_the_attempt_timeout_is_the_number_section_three_three_states() -> None:
    assert invoke.ATTEMPT_TIMEOUT_SECONDS == 1800


def test_the_risk_classes_and_strategies_are_the_ones_section_two_names() -> None:
    assert risk.RISK_CLASSES == ("security", "migration", "infrastructure", "standard")
    assert set(risk.STRATEGIES) == {"single_pass", "independent_panel", "challenge_and_verify"}
    for name, strategy in risk.STRATEGIES.items():
        assert strategy.name == name
        assert strategy.minimum_participants >= 1
        assert strategy.effort


# -- §1: what this package may import -------------------------------------------


def test_no_module_here_imports_another_parts_implementation() -> None:
    for name, tree in _trees().items():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for part in OTHER_PARTS:
                    assert not node.module.startswith(part), f"{name}: {node.module}"


def test_the_path_matcher_is_imported_the_one_qualified_way_p04_mandates() -> None:
    source = _sources()["risk.py"]
    assert "from rqa.protocol.paths import matches" in source
    assert risk.matches.__module__ == "rqa.protocol.paths"


def test_no_module_here_imports_an_http_client_or_opens_a_socket() -> None:
    for name, tree in _trees().items():
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        for client in ("socket", "http", "urllib", "requests", "httpx"):
            assert client not in imported, f"{name} imports {client}"


# -- §6: what is written down ---------------------------------------------------


def _appended_kinds() -> set[str]:
    kinds: set[str] = set()
    for tree in _trees().values():
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append"
                and len(node.args) == 3
                and isinstance(node.args[1], ast.Constant)
            ):
                kinds.add(node.args[1].value)
    return kinds


def test_the_only_entry_kinds_this_package_writes_are_section_sixs_four() -> None:
    assert _appended_kinds() == ENTRY_KINDS_WRITTEN
    assert ENTRY_KINDS_WRITTEN <= contracts.ENTRY_KINDS


def test_this_part_writes_no_lifecycle_transition_and_no_judgement() -> None:
    """§7 and §6's closing line: "P-06 writes no lifecycle transition and does not mutate
    job status"."""
    forbidden = {"transition", "judgement", "spend", "grant", "action", "escalation", "decision", "carry_over", "snapshot"}
    assert not (_appended_kinds() & forbidden)
    for name, source in _sources().items():
        for symbol in ("Judgement", "JobStatus", "Grant", "Deny", "Mutation", "Escalation"):
            assert symbol not in source, f"{name} mentions {symbol}"


# -- §5: the two trees, and who writes them --------------------------------------


def test_only_this_package_writes_the_two_trees_section_five_names() -> None:
    """A tree-wide check: no module outside `rqa/harness` composes
    `jobs/<job>/bundle` or `jobs/<job>/harness/`. P-12's trace writes
    `jobs/<job>/trace.jsonl`, a different record it owns."""
    strays: list[str] = []
    for path in sorted(RQA.rglob("*.py")):
        if path.is_relative_to(HARNESS):
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        if "jobs" in literals and ({"bundle", "harness"} & literals):
            strays.append(str(path.relative_to(RQA.parent)))
    assert strays == [], f"a module outside P-06 composes P-06's trees: {strays}"


def test_the_bundle_tree_name_and_the_harness_tree_name_are_the_published_ones() -> None:
    assert bundle.BUNDLE_DIRNAME == "bundle"
    assert panel.HARNESS_DIRNAME == "harness"
    assert panel.VERDICT_FILENAME == "verdict.json"


# -- §7: what P-06 does not do ---------------------------------------------------


def test_nothing_here_probes_a_route_or_manufactures_a_fallback() -> None:
    """§7: "It does not call a provider itself, probe routes, or manufacture fallback
    routes." E-24's `HarnessProber` is consumed by P-05 and its concrete adapter landed
    there (`rqa/supply/probe.py`); this package adds no second one."""
    for name, source in _sources().items():
        assert "class HarnessProber" not in source, name
        assert "PROBE_MARKER" not in source, name
    for name, tree in _trees().items():
        declared = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "probe" not in declared, name
        assert not any(item.startswith("fallback") for item in declared), name


def test_nothing_here_implements_p05_budgeting() -> None:
    """§7: "It does not implement P-05 budgeting: it requests reservations and reports
    observed consumption through `SupplyPort`"."""
    for name, tree in _trees().items():
        declared = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert not declared & {"route", "reserve", "consumed"}, name


def test_nothing_here_reads_a_file_the_environment_or_a_configuration_for_a_decision() -> None:
    """Every input arrives as an argument. The one environment read is `invoke`'s
    allow-list, which builds the child's environment rather than deciding anything."""
    for name, source in _sources().items():
        if name == "invoke.py":
            continue
        assert "os.environ" not in source, name
        assert "os.getenv" not in source, name
