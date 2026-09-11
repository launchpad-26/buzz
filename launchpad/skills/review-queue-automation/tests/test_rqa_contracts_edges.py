#!/usr/bin/env python3
"""Conformance tests for the `CONTRACTS.md` §9 edge signatures (#2210).

The expectation tables below are transcribed independently from
`architecture/code/CONTRACTS.md` §9 — they are never read from `rqa/edges.py`
or `rqa/contracts.py`, so a drifted declaration fails here instead of a test
comparing the module to itself. Assertions cover parameter names, their kinds
(keyword-only vs positional), their order, their annotation strings and the
return annotation strings. Annotation strings are compared directly (the
modules use `from __future__ import annotations`); `typing.get_type_hints()`
is deliberately never called — it would try to resolve `rqa.protocol`, which
another lane may not have landed yet.

The 26-edge coverage test parses `components.md` §6's own table, so an edge
row added to the architecture fails here rather than passing unnoticed.
"""

from __future__ import annotations

import inspect
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa import contracts, edges  # noqa: E402

COMPONENTS = (
    pathlib.Path(__file__).resolve().parent.parent / "architecture" / "components.md"
)

KW = inspect.Parameter.KEYWORD_ONLY
POS = inspect.Parameter.POSITIONAL_OR_KEYWORD
VAR_KW = inspect.Parameter.VAR_KEYWORD
EMPTY = inspect.Parameter.empty

# --------------------------------------------------------------------------
# CONTRACTS.md §9, transcribed: every free edge function, its keyword-only
# parameters in order with their annotation strings, and its return annotation.
# --------------------------------------------------------------------------

EDGE_FUNCTIONS: dict[str, tuple[tuple[tuple[str, str], ...], str]] = {
    # E-01  P-09 provides, P-01 consumes
    "inventory": (
        (("repo", "str"),),
        "tuple[PrFacts, ...] | GithubUnavailable",
    ),
    "claim_lease": (
        (("job", "Job"), ("grant", "Grant"), ("record", "RecordWriter")),
        "Mutation | LeaseTaken | GithubUnavailable",
    ),
    "release_lease": (
        (("job", "Job"), ("grant", "Grant"), ("record", "RecordWriter")),
        "Mutation | GithubUnavailable",
    ),
    # E-02  P-02 provides, P-01 consumes
    "admit": (
        (("job", "Job"), ("deps", "LifecycleDeps")),
        "JobStatus",
    ),
    # E-03  P-03 provides, P-02 consumes
    "snapshot_for": (
        (
            ("repo", "str"),
            ("job", "Job | None"),
            ("store", "SnapshotStore"),
            ("record", "RecordWriter | None"),
        ),
        "Snapshot | ValidationFailure",
    ),
    # E-04  P-08 provides, P-02 consumes
    "grant": (
        (
            ("repo", "str"),
            ("activity", "Activity"),
            ("snapshot", "Snapshot | None"),
            ("job_id", "str"),
            ("categories", "frozenset[Category] | None"),
            ("record", "RecordWriter"),
            ("github", "GithubProbe"),
            ("store", "CapabilityStore"),
        ),
        "Grant | Deny",
    ),
    # E-05  P-13 provides, P-02 consumes
    "carry_over": (
        (
            ("job", "Job"),
            ("prior", "RecordReader"),
            ("facts", "Facts"),
            ("snapshot", "Snapshot"),
            ("record", "RecordWriter"),
        ),
        "CarryOver",
    ),
    # E-06  P-05 provides, P-06 consumes
    "route": (
        (
            ("job", "Job"),
            ("obligation", "str"),
            ("snapshot", "Snapshot"),
            ("facts", "Facts"),
            ("cursor", "RouteCursor"),
            ("prober", "HarnessProber"),
            ("breakers", "BreakerStore"),
        ),
        "tuple[Route, RouteCursor] | RouteUnavailable",
    ),
    "reserve": (
        (
            ("job", "Job"),
            ("plan", "Plan"),
            ("route", "Route"),
            ("snapshot", "Snapshot"),
            ("spend", "SpendStore"),
        ),
        "Reservation | Refusal",
    ),
    # E-07  P-06 provides, P-02 consumes
    "plan": (
        (
            ("job", "Job"),
            ("facts", "Facts"),
            ("snapshot", "Snapshot"),
            ("carry", "CarryOver"),
            ("record", "RecordWriter"),
        ),
        "Plan",
    ),
    "run": (
        (
            ("job", "Job"),
            ("plan", "Plan"),
            ("facts", "Facts"),
            ("snapshot", "Snapshot"),
            ("supply", "SupplyPort"),
            ("state_dir", "Path"),
            ("record", "RecordWriter"),
        ),
        "PanelResult | BundleFailure",
    ),
    # E-08  P-04 provides, P-06 consumes
    "validate": (
        (("path", "Path"), ("attempt_id", "str")),
        "Valid | Invalid",
    ),
    # E-09  P-07 provides, P-02 consumes
    "judge": (
        (
            ("job", "Job"),
            ("plan", "Plan"),
            ("panel", "PanelResult"),
            ("carry", "CarryOver"),
            ("facts", "Facts"),
            ("snapshot", "Snapshot"),
            ("decision", "Decision | None"),
            ("record", "RecordWriter"),
        ),
        "Judgement",
    ),
    # E-10  P-10 provides, P-02 consumes
    "remediate": (
        (
            ("job", "Job"),
            ("finding", "Finding"),
            ("grant", "Grant"),
            ("facts", "Facts"),
            ("snapshot", "Snapshot"),
            ("state_dir", "Path"),
            ("runner", "ProcessRunner"),
            ("record", "RecordWriter"),
        ),
        "RemediationPushed | RemediationRefused",
    ),
    # E-11  P-11 provides, P-02 consumes (resume: P-02 provides)
    "raise_": (
        (
            ("job", "Job"),
            ("cause", "EscalationCause"),
            ("question", "str"),
            ("context", "Mapping"),
            ("record", "RecordWriter"),
            ("store", "EscalationStore"),
        ),
        "Escalation",
    ),
    "pending": (
        (("store", "EscalationStore"),),
        "tuple[Escalation, ...]",
    ),
    "resume": (
        (("job_id", "str"), ("decision", "Decision"), ("deps", "LifecycleDeps")),
        "JobStatus",
    ),
    # E-12  P-09 provides, P-02 consumes
    "submit_review": (
        (
            ("job", "Job"),
            ("state", "Literal['APPROVE', 'REQUEST_CHANGES']"),
            ("body", "str"),
            ("grant", "Grant"),
            ("record", "RecordWriter"),
        ),
        "Mutation | Stale | GithubUnavailable",
    ),
    "comment": (
        (
            ("job", "Job"),
            ("body", "str"),
            ("grant", "Grant"),
            ("record", "RecordWriter"),
        ),
        "Mutation | GithubUnavailable",
    ),
    "merge": (
        (("job", "Job"), ("grant", "Grant"), ("record", "RecordWriter")),
        "Mutation | Stale | GithubUnavailable",
    ),
    # E-14  P-09 provides internally to its E-23 fact capture
    "checks": (
        (("repo", "str"), ("sha", "str")),
        "tuple[CheckRun, ...] | GithubUnavailable",
    ),
    # E-15  P-05 provides, P-06 consumes through SupplyPort
    "consumed": (
        (
            ("job", "Job"),
            ("attempt", "Attempt"),
            ("reading", "int | None"),
            ("reservation", "Reservation"),
            ("record", "RecordWriter"),
            ("spend", "SpendStore"),
            ("breakers", "BreakerStore"),
        ),
        "Spend",
    ),
    # E-16  P-09 provides, P-08 consumes
    "probe": (
        (("repo", "str"), ("credential", "str")),
        "CapabilityReading | GithubUnavailable",
    ),
    # E-23  P-09 provides, P-02 consumes
    "facts": (
        (("job", "Job"), ("record", "RecordWriter")),
        "Facts | GithubUnavailable",
    ),
}

# CONTRACTS.md §9 Protocol methods: (name, kind, annotation) per parameter,
# `self` included, plus the return annotation.
PROTOCOL_METHODS: dict[str, tuple[tuple[tuple[str, object, object], ...], str]] = {
    # E-24  class HarnessProber(Protocol)
    "HarnessProber.probe": (
        (("self", POS, EMPTY), ("route", POS, "Route"), ("timeout", KW, "float")),
        "bool",
    ),
    # E-25  class KeyStore(Protocol)
    "KeyStore.read": (
        (("self", POS, EMPTY), ("name", POS, "str")),
        "bytes | None",
    ),
    # E-26  class ProcessRunner(Protocol)
    "ProcessRunner.run": (
        (
            ("self", POS, EMPTY),
            ("cwd", KW, "Path"),
            ("argv", KW, "tuple[str, ...]"),
            ("timeout", KW, "float"),
        ),
        "ProcessResult",
    ),
    # E-13  RecordWriter.append(job_id, kind, payload) -> Entry (§7 Protocol)
    "RecordWriter.append": (
        (
            ("self", POS, EMPTY),
            ("job_id", POS, "str"),
            ("kind", POS, "EntryKind"),
            ("payload", POS, "Mapping"),
        ),
        "Entry",
    ),
    # E-07 comment: SupplyPort is P-06's view of E-06 + E-15
    #   route(obligation, cursor) -> tuple[Route, RouteCursor] | RouteUnavailable
    #   reserve(plan, route) -> Reservation | Refusal
    #   consumed(attempt, reading, reservation) -> Spend
    "SupplyPort.route": (
        (
            ("self", POS, EMPTY),
            ("obligation", POS, "str"),
            ("cursor", POS, "RouteCursor"),
        ),
        "tuple[Route, RouteCursor] | RouteUnavailable",
    ),
    "SupplyPort.reserve": (
        (("self", POS, EMPTY), ("plan", POS, "Plan"), ("route", POS, "Route")),
        "Reservation | Refusal",
    ),
    "SupplyPort.consumed": (
        (
            ("self", POS, EMPTY),
            ("attempt", POS, "Attempt"),
            ("reading", POS, "int | None"),
            ("reservation", POS, "Reservation"),
        ),
        "Spend",
    ),
}

# §9 names a collaborator type in a signature's annotation without stating any
# method for it: each is an empty Protocol whose docstring names the part that
# owns its shape. `Explanation` is named only by E-17's arrow and defined
# nowhere in CONTRACTS.md; its shape is P-12's.
EMPTY_PROTOCOL_OWNERS: dict[str, str] = {
    "LifecycleDeps": "P-02",
    "SnapshotStore": "P-03",
    "GithubProbe": "P-08",
    "CapabilityStore": "P-08",
    "SpendStore": "P-05",
    "BreakerStore": "P-05",
    "EscalationStore": "P-11",
    "Explanation": "P-12",
}

# CONTRACTS.md §9's E-17 prose line: the concrete provider callables of the
# command surface, in the order the line names them.
E17_CALLABLES = ("status", "explain", "decide", "pending", "onboard", "tick")

# components.md §6: the edges that are prose-only and external — no Python
# signature exists for them anywhere in §9.
PROSE_ONLY_EDGES = frozenset({"E-18", "E-19", "E-20", "E-21", "E-22"})

SECTION_NINE_NAMES = (
    tuple(EDGE_FUNCTIONS)
    + tuple(EMPTY_PROTOCOL_OWNERS)
    + ("SupplyPort", "HarnessProber", "KeyStore", "ProcessRunner")
    + ("status", "explain", "decide", "onboard", "tick")
)


def _is_protocol(cls: object) -> bool:
    return isinstance(cls, type) and getattr(cls, "_is_protocol", False)


def _assert_signature(qualified: str, fn, expected_params, expected_return) -> None:
    signature = inspect.signature(fn)
    actual = tuple(
        (p.name, p.kind, p.annotation) for p in signature.parameters.values()
    )
    assert actual == tuple(expected_params), (
        f"{qualified}: parameters differ from CONTRACTS.md §9:\n"
        f"  declared:   {actual!r}\n  documented: {expected_params!r}"
    )
    for parameter in signature.parameters.values():
        assert parameter.default is EMPTY, (
            f"{qualified}: parameter {parameter.name!r} has a default; §9 states none"
        )
    assert signature.return_annotation == expected_return, (
        f"{qualified}: returns {signature.return_annotation!r}, "
        f"documented {expected_return!r}"
    )


def _section_six_edge_ids() -> list[str]:
    """First cell of every row of components.md §6's edge table, from the
    document itself — never from the module under test."""
    ids: list[str] = []
    in_table = False
    for line in COMPONENTS.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not in_table:
            if cells[:2] == ["edge", "from"]:
                in_table = True
            continue
        if re.fullmatch(r"E-\d\d", cells[0]):
            ids.append(cells[0])
        elif set(cells[0]) <= set("-: "):
            continue  # header separator row
        else:
            break
    return ids


# --------------------------------------------------------------------------
# §9 free functions
# --------------------------------------------------------------------------


def test_every_edge_function_matches_contracts_md_exactly() -> None:
    for name, (params, returns) in EDGE_FUNCTIONS.items():
        fn = getattr(edges, name)
        expected = tuple((p, KW, annotation) for p, annotation in params)
        _assert_signature(name, fn, expected, returns)


def test_edge_functions_are_declarations_not_implementations() -> None:
    for name in EDGE_FUNCTIONS:
        fn = getattr(edges, name)
        assert callable(fn), f"{name} is not callable"
        assert fn.__module__ == "rqa.edges", f"{name} declared in {fn.__module__}"


# --------------------------------------------------------------------------
# §9 Protocols
# --------------------------------------------------------------------------


def test_edge_protocol_methods_match_contracts_md_exactly() -> None:
    for qualified, (params, returns) in PROTOCOL_METHODS.items():
        cls_name, method_name = qualified.split(".")
        cls = getattr(contracts, cls_name)
        assert _is_protocol(cls), f"{cls_name} is not a Protocol"
        _assert_signature(qualified, getattr(cls, method_name), params, returns)


def test_protocols_declare_no_method_beyond_the_documented_ones() -> None:
    documented: dict[str, set[str]] = {}
    for qualified in PROTOCOL_METHODS:
        cls_name, method_name = qualified.split(".")
        documented.setdefault(cls_name, set()).add(method_name)
    del documented["RecordWriter"]  # §7's, owned and tested by #2209
    for cls_name, methods in documented.items():
        cls = getattr(edges, cls_name)
        public = {n for n in vars(cls) if not n.startswith("_")}
        assert public == methods, (
            f"{cls_name}: declares {sorted(public)}, §9 states {sorted(methods)}"
        )


def test_collaborator_protocols_are_empty_and_name_their_owner() -> None:
    for name, owner in EMPTY_PROTOCOL_OWNERS.items():
        cls = getattr(edges, name)
        assert _is_protocol(cls), f"{name} is not a Protocol"
        public = [n for n in vars(cls) if not n.startswith("_")]
        assert public == [], (
            f"{name}: §9 states no method, but it declares {public} — "
            "the shape is the owning part's to fill in its own lane"
        )
        doc = cls.__doc__ or ""
        assert owner in doc, f"{name}: docstring does not name its owner {owner}"


# --------------------------------------------------------------------------
# E-17 — a command surface, not one signature
# --------------------------------------------------------------------------


def test_e17_enumerates_the_concrete_provider_callables() -> None:
    surface = contracts.EDGES["E-17"]
    assert isinstance(surface, tuple), "E-17 must map to its provider callables"
    assert tuple(fn.__name__ for fn in surface) == E17_CALLABLES, (
        f"E-17 callables differ from §9's prose line: "
        f"{tuple(fn.__name__ for fn in surface)}"
    )
    for fn in surface:
        assert callable(fn), f"E-17 member {fn!r} is not callable"


def test_e17_pending_is_p11s_e11_pending() -> None:
    # components.md §6 row E-17: "`pending` (P-11 `pending()`)" — the same
    # callable as E-11's, never a second declaration.
    surface = contracts.EDGES["E-17"]
    by_name = {fn.__name__: fn for fn in surface}
    assert by_name["pending"] is edges.pending
    assert by_name["pending"] is contracts.pending


def test_e17_explain_returns_the_documented_union() -> None:
    signature = inspect.signature(edges.explain)
    assert signature.return_annotation == "Explanation | ExplanationUnavailable"


def test_e17_surface_callables_constrain_nothing_beyond_their_names() -> None:
    # §9 states the callables' names and providers only (plus explain's return
    # union); the full parameter lists belong to the provider parts' own
    # contracts. The declarations must therefore be open keyword-only surfaces:
    # nothing required, nothing narrowed, and no positional acceptance — the
    # CONTRACTS.md preamble's "every function keyword-only" rule binds free
    # functions, with rqa.protocol.paths.matches its single named exception.
    for name in ("status", "explain", "decide", "onboard", "tick"):
        fn = getattr(edges, name)
        kinds = {p.kind for p in inspect.signature(fn).parameters.values()}
        assert kinds <= {VAR_KW}, (
            f"{name}: accepts positional or concrete parameters, but CONTRACTS.md "
            f"§9 states none and its preamble makes every free function "
            f"keyword-only — the parameter list is the provider part's to state"
        )


# --------------------------------------------------------------------------
# The 26-row account, driven by components.md §6's own table
# --------------------------------------------------------------------------


def test_every_section_six_edge_row_is_accounted_for() -> None:
    ids = _section_six_edge_ids()
    assert len(ids) == 26, f"components.md §6 has {len(ids)} edge rows, expected 26"
    assert len(set(ids)) == len(ids), "duplicate edge id in components.md §6"
    assert set(contracts.EDGES) == set(ids), (
        f"EDGES and components.md §6 disagree: "
        f"missing {sorted(set(ids) - set(contracts.EDGES))}, "
        f"extra {sorted(set(contracts.EDGES) - set(ids))}"
    )


def test_prose_only_edges_are_exactly_the_five_external_ones() -> None:
    prose = {edge for edge, realised in contracts.EDGES.items() if isinstance(realised, str)}
    assert prose == PROSE_ONLY_EDGES, f"prose-only set differs: {sorted(prose)}"
    for edge in sorted(prose):
        reason = contracts.EDGES[edge]
        assert reason.startswith("prose-only external edge"), (
            f"{edge}: reason does not say why no signature exists: {reason!r}"
        )


def test_realised_edges_map_to_callables_or_protocols() -> None:
    for edge, realised in contracts.EDGES.items():
        if isinstance(realised, str):
            continue
        assert isinstance(realised, tuple) and realised, f"{edge}: empty realisation"
        for member in realised:
            assert callable(member) or _is_protocol(member), (
                f"{edge}: {member!r} is neither a callable nor a Protocol"
            )


def test_e13_is_record_writers_append_method() -> None:
    assert contracts.EDGES["E-13"] == (contracts.RecordWriter.append,)


# --------------------------------------------------------------------------
# The seam import point: rqa.contracts re-exports every §9 name
# --------------------------------------------------------------------------


def test_every_section_nine_name_is_importable_from_contracts() -> None:
    for name in SECTION_NINE_NAMES:
        assert getattr(contracts, name) is getattr(edges, name), (
            f"{name}: rqa.contracts does not re-export the edge-lane object"
        )
        assert name in contracts.__all__, f"{name} missing from contracts.__all__"


def test_contracts_dunder_all_resolves_completely() -> None:
    for name in contracts.__all__:
        assert hasattr(contracts, name), f"__all__ names missing attribute {name}"
    assert "EDGES" in contracts.__all__
