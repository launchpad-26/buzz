#!/usr/bin/env python3
"""`rqa.supply`'s public surface, its seam and its exclusions —
`code/P-05-reviewer-supply.md` §1, §5, §6, §7 and §8's closing property.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

**This package lands in two waves and this file is the record of the split.** The routing
and liveness-probing half (§3.1 `route()`, §4's probe, §5's breaker store) lands first; the
budget and spend half (§3.2 `reserve()`, §3.3 `consumed()`, `budget.py`, `spend.py`) lands
next. Every assertion below therefore pins a state the *contract* fixes forever, never the
state of the tree on the afternoon the first half landed:

* the module set is **exactly one of** the pre-sibling five or §1's full seven — not a
  subset test, not a superset test, and never "the five I wrote";
* `__all__` is **exactly one of** the pre-sibling four or §1's full nine re-exports;
* nothing here asserts that `rqa.supply.budget`/`rqa.supply.spend` cannot be imported or
  that `reserve`/`consumed`/`Spend` are absent — a sibling's contract-required work is not
  an invariant to pin as missing;
* §8's closing `kind="spend"` property is written so that zero hits (this wave) and hits
  confined to `rqa/supply/spend.py` (after the sibling lands) both pass, while a hit in any
  other file fails.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.supply  # noqa: E402
from rqa import edges  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
SUPPLY = RQA / "supply"

#: §1's module list, in full. This package is two lanes' work, so both states are legal —
#: and nothing in between is.
MODULES_FULL = frozenset({"__init__", "aliases", "ladder", "breakers", "budget", "spend", "probe"})
#: The routing/probing half alone: §1's list minus the budget half's two modules.
MODULES_ROUTING = MODULES_FULL - {"budget", "spend"}

#: §1's re-export list, in full.
EXPORTS_FULL = frozenset(
    {"route", "reserve", "consumed", "Route", "RouteCursor", "Reservation", "Refusal",
     "RouteUnavailable", "Spend"}
)
#: The routing half's share of it.
EXPORTS_ROUTING = frozenset({"route", "Route", "RouteCursor", "RouteUnavailable"})

#: §6: the only entry kind P-05 writes, from `consumed()` alone.
ENTRY_KINDS_WRITTEN = frozenset({"spend"})

#: §5 and container.md §5: the tables this part owns. `spend` is the sibling half's.
TABLES = frozenset({"providers", "circuit_breakers", "spend"})

#: Every other part's package. §1: a module here imports none of them; `rqa.record` is the
#: one exception the contract names (`consumed()` appends through it), and `rqa.contracts`
#: / `rqa.edges` are the seam, not a part.
OTHER_PARTS = (
    "rqa.policy", "rqa.protocol", "rqa.lifecycle", "rqa.queue", "rqa.github", "rqa.harness",
    "rqa.judgement", "rqa.authority", "rqa.remediation", "rqa.escalation", "rqa.reuse",
)


def _sources() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(SUPPLY.glob("*.py"))}


def _imported(source: str) -> set[str]:
    """Every module and name this source imports, as dotted strings."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def _declared(source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.parse(source).body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.Assign):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
    return {name for name in names if not name.startswith("__")}


# -- §1: modules and re-exports -------------------------------------------------


def test_the_module_set_is_exactly_one_of_the_two_legitimate_states() -> None:
    found = frozenset(path.stem for path in SUPPLY.glob("*.py"))
    assert found in (MODULES_ROUTING, MODULES_FULL), (
        "§1 lists "
        f"{sorted(MODULES_FULL)}; the routing half alone is {sorted(MODULES_ROUTING)}; "
        f"the package has {sorted(found)}"
    )


def test_all_is_exactly_one_of_the_two_legitimate_re_export_sets() -> None:
    found = frozenset(rqa.supply.__all__)
    assert found in (EXPORTS_ROUTING, EXPORTS_FULL), (
        f"§1 re-exports {sorted(EXPORTS_FULL)}; the routing half re-exports "
        f"{sorted(EXPORTS_ROUTING)}; the package re-exports {sorted(found)}"
    )


def test_the_two_halves_of_the_re_export_list_partition_it() -> None:
    """The split is a partition, not an overlap: neither lane may claim the other's names,
    and together they are exactly §1's list."""
    assert EXPORTS_ROUTING < EXPORTS_FULL
    assert EXPORTS_FULL - EXPORTS_ROUTING == frozenset(
        {"reserve", "consumed", "Reservation", "Refusal", "Spend"}
    )


def test_the_module_set_and_the_re_export_set_describe_the_same_wave() -> None:
    """A package with the sibling's modules but not its exports — or the reverse — is a
    partial state, which is exactly what this file exists to fail."""
    modules = frozenset(path.stem for path in SUPPLY.glob("*.py"))
    exports = frozenset(rqa.supply.__all__)
    assert (modules == MODULES_FULL) == (exports == EXPORTS_FULL)


def test_every_re_exported_name_actually_resolves() -> None:
    missing = [name for name in rqa.supply.__all__ if not hasattr(rqa.supply, name)]
    assert missing == [], f"__all__ names that do not resolve: {missing}"


def test_the_seam_types_are_the_ones_contracts_declares() -> None:
    for name in rqa.supply.__all__:
        if name[0].isupper():
            assert getattr(rqa.supply, name) is getattr(contracts, name), name


def test_the_package_declares_nothing_it_only_re_exports() -> None:
    """§1: the shared vocabulary has exactly one definition, in `rqa.contracts`."""
    assert _declared((SUPPLY / "__init__.py").read_text(encoding="utf-8")) == set()


def test_the_stores_the_registry_and_the_probe_are_not_package_surface() -> None:
    """They stay submodule names, the way `rqa.policy` keeps `SnapshotStore` out of its
    package surface even though E-03's signature mentions the Protocol. `SupplyError` is
    §2's, and §1's re-export list does not carry it either."""
    for name in ("BreakerStore", "BreakerState", "SupplyError", "ALIASES", "HarnessProber",
                 "SubprocessHarnessProber", "route_key", "eligible", "subscription_first"):
        assert name not in rqa.supply.__all__, name


def test_no_module_here_is_a_stub() -> None:
    for name, source in _sources().items():
        assert "NotImplementedError" not in source, name
        assert "TODO" not in source, name


# -- the seam: E-06's `route()` and E-24 ----------------------------------------


def test_route_matches_the_contracts_md_edge_signature_exactly() -> None:
    assert inspect.signature(rqa.supply.route) == inspect.signature(edges.route)


def test_the_store_protocols_stay_empty_placeholders_in_the_edge_module() -> None:
    """§9 keeps `BreakerStore` and `SpendStore` empty Protocols naming P-05 as the part
    that states their shape; this package is where that statement lives."""
    for name in ("BreakerStore", "SpendStore"):
        assert [
            member for member in vars(getattr(edges, name)) if not member.startswith("_")
        ] == [], name


def test_the_breaker_store_shape_is_stated_in_this_package() -> None:
    from rqa.supply.breakers import BreakerStore

    assert BreakerStore is not edges.BreakerStore
    assert set(vars(BreakerStore)) >= {
        "cooldown", "set_cooldown", "breaker", "record_failure", "record_success"
    }


def test_the_harness_prober_protocol_is_consumed_verbatim_not_restated() -> None:
    """§4: `HarnessProber` is defined only in `CONTRACTS.md` §9 and consumed here."""
    assert list(inspect.signature(edges.HarnessProber.probe).parameters) == ["self", "route", "timeout"]
    for name, source in _sources().items():
        assert "class HarnessProber" not in source, name


def test_the_probe_constants_live_where_section_four_puts_them() -> None:
    from rqa.supply.probe import PROBE_COOLDOWN, PROBE_TIMEOUT_SECONDS

    assert PROBE_TIMEOUT_SECONDS == 300
    assert PROBE_COOLDOWN.total_seconds() == 300


# -- §1: what this package may import -------------------------------------------


def test_no_module_here_imports_another_parts_package() -> None:
    """§1: "No module in `rqa.supply` imports from any other part except `rqa.record` (to
    append)". `rqa.contracts` and `rqa.edges` are the seam, not a part."""
    for name, source in _sources().items():
        imported = _imported(source)
        for part in OTHER_PARTS:
            assert not any(entry.startswith(part) for entry in imported), f"{name}: {part}"


def test_only_the_probe_adapter_spawns_a_process() -> None:
    """§1: the process primitive that spawns a harness is permitted "inside `probe.py`
    only"."""
    for name, source in _sources().items():
        if name == "probe.py":
            assert "subprocess" in _imported(source)
            continue
        assert "subprocess" not in _imported(source), name


def test_no_module_here_imports_an_http_client_or_opens_a_socket() -> None:
    """§4: the probe touches no GitHub API and sends no repository content."""
    for name, source in _sources().items():
        imported = _imported(source)
        for client in ("http", "http.client", "urllib", "urllib.request", "requests", "socket"):
            assert client not in imported, f"{name} imports {client}"


def test_the_alias_registry_is_pure_data() -> None:
    """§1: `aliases.py` is the closed registry. It never probes and never invokes."""
    source = (SUPPLY / "aliases.py").read_text(encoding="utf-8")
    imported = _imported(source)
    assert not any(entry.startswith("rqa.supply.probe") for entry in imported)
    assert "subprocess" not in imported


# -- §6: what is written down ---------------------------------------------------


def test_route_is_handed_no_record_writer() -> None:
    """§6: "`route()` never calls `record.append`" — no record kind exists for "a route was
    resolved", and E-06's signature gives it no writer to call."""
    assert "record" not in inspect.signature(rqa.supply.route).parameters


def test_the_routing_modules_neither_import_nor_call_the_record() -> None:
    for name in ("ladder.py", "aliases.py", "breakers.py", "probe.py"):
        source = (SUPPLY / name).read_text(encoding="utf-8")
        assert not any(entry.startswith("rqa.record") for entry in _imported(source)), name
        assert "record.append" not in source, name


def test_the_only_entry_kind_this_package_writes_is_spend() -> None:
    """§6, and `ENTRY_KINDS` is the closed set it belongs to."""
    written = set()
    for source in _sources().values():
        written.update(re.findall(r'kind="([a-z_]+)"', source))
    assert written <= ENTRY_KINDS_WRITTEN, f"P-05 writes only {sorted(ENTRY_KINDS_WRITTEN)}"
    assert ENTRY_KINDS_WRITTEN <= contracts.ENTRY_KINDS


_SPEND_KIND = re.compile(r'kind="spend"')

#: `rqa/record/migrate.py` is the one ruled exception to §8's closing property, and it was
#: already landed when this package was written. P-12's one-time legacy migration replays
#: the incumbent `cost_ledger` into the record as `spend` entries whose `source` is
#: `"migrated"` — a historical import, not a review-time spend, and the record payload is
#: deliberately not a serialised `Spend` (it carries `axis` and `attempt_id`, which `Spend`
#: has not). P-05 remains the only part that writes a `spend` entry *for a review*.
MIGRATION_WRITER = "rqa/record/migrate.py"
RUNTIME_WRITER = "rqa/supply/spend.py"


def test_only_the_supply_spend_module_writes_a_spend_entry_for_a_review() -> None:
    """§8's closing property: `grep -rn 'kind="spend"' rqa/ --include=*.py` returns hits
    only inside `rqa/supply/spend.py`, plus P-12's landed legacy migration. The state
    before the budget half lands (migration alone) and the state after it (both) are each
    legal; a hit in any other file is not."""
    writers = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if _SPEND_KIND.search(path.read_text(encoding="utf-8"))
    )
    assert writers in ([MIGRATION_WRITER], [MIGRATION_WRITER, RUNTIME_WRITER]), (
        f"a `spend` entry is written outside `{RUNTIME_WRITER}`: {writers}"
    )


# -- §5: the tables, and who writes them ----------------------------------------

#: `UPDATE` requires its trailing `SET` so the `ON CONFLICT ... DO UPDATE SET` of an upsert
#: is not read as a table named `SET`.
_WRITE = re.compile(
    r"(?:INSERT INTO|DELETE FROM)\s+([a-z_]+)|UPDATE\s+([a-z_]+)\s+SET", re.IGNORECASE
)


def _written_tables(source: str) -> set[str]:
    return {name.lower() for match in _WRITE.findall(source) for name in match if name}


def test_this_package_writes_no_table_outside_its_own_two_stores() -> None:
    for name, source in _sources().items():
        for table in _written_tables(source):
            assert table in TABLES, f"{name} writes {table}"


def test_only_this_package_writes_the_breaker_tables() -> None:
    """§5: "Both stores are written only by P-05 and read only by P-05"
    (container.md §5: readers `-` for both `spend` and `breakers`)."""
    strays = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if not str(path).startswith(str(SUPPLY))
        and _written_tables(path.read_text(encoding="utf-8")) & {"providers", "circuit_breakers"}
    )
    assert strays == [], f"a part other than P-05 writes a breaker table: {strays}"


def test_only_this_package_reads_the_breaker_tables() -> None:
    strays = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if not str(path).startswith(str(SUPPLY))
        and re.search(r"FROM\s+(providers|circuit_breakers)\b", path.read_text(encoding="utf-8"))
    )
    assert strays == [], f"a part other than P-05 reads a breaker table: {strays}"


# -- §7: what P-05 does not do ---------------------------------------------------


def test_nothing_here_offers_a_manual_breaker_or_cooldown_reset() -> None:
    """§7, U-DISPATCH-05 (`bin`): the only ways back are a passing probe, a `consumed()`
    outcome, or the stored deadline passing."""
    for name, source in _sources().items():
        for declaration in _declared(source):
            assert "reset" not in declaration.lower(), f"{name}: {declaration}"


def test_nothing_here_reads_a_file_the_environment_or_a_configuration() -> None:
    """§1: `job`, `plan`, `facts` and `snapshot` all arrive as arguments. The one
    environment read is the probe's allowlist, which exists to *withhold* variables from a
    child, not to configure this part."""
    for name, source in _sources().items():
        assert "config.json" not in source, name
        if name == "probe.py":
            continue
        assert "os.environ" not in source, name


def test_nothing_here_transitions_a_job_or_knows_a_finding() -> None:
    """§7: P-05 does not touch `jobs.status`, writes no `transition` entry, and does not
    know what a finding or a disposition is."""
    for name, source in _sources().items():
        assert "jobs.status" not in source, name
        assert 'kind="transition"' not in source, name
        for foreign in ("Finding", "Remedy", "EvidenceState", "Judgement"):
            assert foreign not in _declared(source), f"{name}: {foreign}"


def test_route_retries_nothing_and_walks_the_ladder_once() -> None:
    """§7: "Does not retry inside `route()`: one call inspects the ladder once"."""
    source = (SUPPLY / "ladder.py").read_text(encoding="utf-8")
    loops = [node for node in ast.walk(ast.parse(source))
             if isinstance(node, (ast.For, ast.While)) and not isinstance(
                 getattr(node, "parent", None), ast.GeneratorExp)]
    functions = {node.name: node for node in ast.parse(source).body
                 if isinstance(node, ast.FunctionDef)}
    in_route = [node for node in ast.walk(functions["route"]) if isinstance(node, (ast.For, ast.While))]
    assert len(in_route) == 1, "route() walks the configured ladder exactly once"
    assert loops, "the ladder walk is a loop, not an unrolled special case"
