#!/usr/bin/env python3
"""P-06 §3.1 — deterministic planning. §8 rows T1, T2 and T3, plus the strategy rule.

T1  identical facts/snapshot/carry -> identical plans and identical recorded payloads
T2  a reused obligation is absent from `Plan.obligations` and `omitted[id] == "carried"`
T3  risk-excluded and path-excluded obligations carry their deterministic reasons, and
    path selection calls P-04 `matches()`
"""

from __future__ import annotations

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_harness_fixtures as fx  # noqa: E402
from rqa.contracts import Obligation  # noqa: E402
from rqa.harness import plan as plan_entry  # noqa: E402
from rqa.harness.risk import (  # noqa: E402
    CARRIED_REASON,
    PATH_REASON,
    RISK_REASON_PREFIX,
    STRATEGIES,
    matched_classes,
    selection,
)
from rqa.protocol import paths as protocol_paths  # noqa: E402

STANDARD = Obligation(id="O-std", paths=(), required_for=frozenset({"standard"}), evidence="e")
SECURITY = Obligation(id="O-sec", paths=(), required_for=frozenset({"security"}), evidence="e")
SCOPED = Obligation(
    id="O-scoped",
    paths=("src/*.py",),
    required_for=frozenset({"standard"}),
    evidence="e",
)


def _plan(*, changed_paths, obligations, reused=(), assurance=None):
    snapshot = fx.make_snapshot(
        policy=fx.make_policy(obligations=obligations, assurance=assurance or {"standard": 1})
    )
    record = fx.FakeRecord()
    planned = plan_entry(
        job=fx.make_job(),
        facts=fx.make_facts(changed_paths=changed_paths),
        snapshot=snapshot,
        carry=fx.make_carry(reused=reused),
        record=record,
    )
    return planned, record


# -- T1 -------------------------------------------------------------------------


def test_t1_identical_inputs_produce_identical_plans_and_identical_payloads() -> None:
    paths = frozenset({"src/a.py", "migrations/0001.sql"})
    obligations = (STANDARD, SECURITY, SCOPED)
    first, first_record = _plan(changed_paths=paths, obligations=obligations)
    second, second_record = _plan(changed_paths=paths, obligations=obligations)
    assert first == second
    assert first_record.of_kind("plan") == second_record.of_kind("plan")


def test_t1_the_recorded_payload_is_every_plan_field() -> None:
    planned, record = _plan(changed_paths=frozenset({"src/a.py"}), obligations=(STANDARD,))
    payload = record.of_kind("plan")[0]
    assert set(payload) == {
        "obligations",
        "omitted",
        "strategy",
        "participants",
        "risk_class",
        "head_sha",
        "snapshot_hash",
        "protocol_hash",
        "policy_version",
    }
    assert tuple(payload["obligations"]) == planned.obligations
    assert payload["head_sha"] == planned.head_sha
    assert payload["snapshot_hash"] == planned.snapshot_hash
    assert payload["protocol_hash"] == planned.protocol_hash
    assert payload["policy_version"] == planned.policy_version


def _imported_modules(module: pathlib.Path) -> set[str]:
    """Every module name this file imports, from the AST — not a text search.

    A grep over the source cannot tell an import from the word appearing in a docstring,
    and these modules document the matchers they refuse by name.
    """
    tree = ast.parse(module.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def test_t1_planning_reads_no_clock_and_no_environment() -> None:
    imported = _imported_modules(
        pathlib.Path(__file__).resolve().parent.parent / "rqa" / "harness" / "risk.py"
    )
    for forbidden in ("random", "uuid", "time", "os", "datetime", "secrets", "subprocess"):
        assert forbidden not in imported, forbidden


# -- T2 -------------------------------------------------------------------------


def test_t2_a_reused_obligation_is_never_planned_and_is_recorded_carried() -> None:
    planned, _ = _plan(
        changed_paths=frozenset({"src/a.py"}),
        obligations=(STANDARD, SCOPED),
        reused=("O-std",),
    )
    assert "O-std" not in planned.obligations
    assert planned.omitted["O-std"] == CARRIED_REASON
    assert "O-scoped" in planned.obligations


def test_t2_carried_wins_over_every_other_omission_cause() -> None:
    """Step 1 is first and mutually exclusive: an obligation that is *also* risk-excluded
    is still recorded `carried`, never with a risk reason."""
    planned, _ = _plan(
        changed_paths=frozenset({"docs/readme.md"}),
        obligations=(SECURITY,),
        reused=("O-sec",),
    )
    assert planned.omitted["O-sec"] == CARRIED_REASON


def test_t2_every_non_carried_obligation_appears_exactly_once() -> None:
    obligations = (STANDARD, SECURITY, SCOPED)
    planned, _ = _plan(
        changed_paths=frozenset({"docs/readme.md"}), obligations=obligations, reused=()
    )
    seen = set(planned.obligations) | set(planned.omitted)
    assert seen == {obligation.id for obligation in obligations}
    assert not set(planned.obligations) & set(planned.omitted)


# -- T3 -------------------------------------------------------------------------


def test_t3_a_risk_excluded_obligation_carries_the_risk_reason() -> None:
    planned, _ = _plan(changed_paths=frozenset({"docs/readme.md"}), obligations=(SECURITY,))
    assert planned.omitted["O-sec"].startswith(RISK_REASON_PREFIX)
    assert "standard" in planned.omitted["O-sec"]


def test_t3_a_path_excluded_obligation_carries_the_path_reason() -> None:
    planned, _ = _plan(changed_paths=frozenset({"docs/readme.md"}), obligations=(SCOPED,))
    assert planned.omitted["O-scoped"] == PATH_REASON


def test_t3_the_two_reasons_are_distinct_and_deterministic() -> None:
    planned, _ = _plan(
        changed_paths=frozenset({"docs/readme.md"}), obligations=(SECURITY, SCOPED)
    )
    assert planned.omitted["O-sec"] != planned.omitted["O-scoped"]
    again, _ = _plan(changed_paths=frozenset({"docs/readme.md"}), obligations=(SECURITY, SCOPED))
    assert planned.omitted == again.omitted


def test_t3_path_selection_calls_the_p04_matcher() -> None:
    """Direct evidence, not a source grep: the module's `matches` is replaced by a
    counting wrapper around P-04's own, and the count has to move."""
    from rqa.harness import risk

    calls: list[tuple[str, str]] = []
    original = risk.matches

    def counting(path: str, pattern: str) -> bool:
        calls.append((path, pattern))
        return original(path, pattern)

    risk.matches = counting  # type: ignore[assignment]
    try:
        _plan(changed_paths=frozenset({"src/a.py"}), obligations=(SCOPED,))
    finally:
        risk.matches = original  # type: ignore[assignment]
    assert original is protocol_paths.matches
    assert ("src/a.py", "src/*.py") in calls


def test_t3_path_matching_is_pathglob_not_fnmatch() -> None:
    """`src/*.py` must not match `src/a/b.py`: `*` never crosses a `/` in PathGlob, and
    that is precisely where `fnmatch` differs. A package that reached for `fnmatch` would
    plan this obligation instead of omitting it."""
    planned, _ = _plan(changed_paths=frozenset({"src/a/b.py"}), obligations=(SCOPED,))
    assert planned.omitted["O-scoped"] == PATH_REASON
    matched, _ = _plan(changed_paths=frozenset({"src/b.py"}), obligations=(SCOPED,))
    assert "O-scoped" in matched.obligations


def test_no_other_path_matcher_is_used_anywhere_in_the_package() -> None:
    """§7: no `fnmatch`, no `PurePath.match`, no other matcher, for any comparison.

    Both halves are checked: nothing imports an alternative matcher, and no call in the
    package is `.match(`/`.fnmatch(` on anything.
    """
    harness = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "harness"
    for module in sorted(harness.glob("*.py")):
        imported = _imported_modules(module)
        for forbidden in ("fnmatch", "glob", "re", "pathlib.PurePath"):
            assert forbidden not in imported, f"{module.name} imports {forbidden}"
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"match", "fnmatch", "fnmatchcase"}, (
                    f"{module.name} calls .{node.func.attr}()"
                )


# -- risk classification and strategy (§2, §3.1) ---------------------------------


def test_the_baseline_class_always_matches() -> None:
    assert matched_classes(changed_paths=frozenset()) == ("standard",)
    assert matched_classes(changed_paths=frozenset({"docs/x.md"})) == ("standard",)


def test_the_first_matching_class_is_the_recorded_class() -> None:
    matched = matched_classes(changed_paths=frozenset({"src/auth/login.py", "migrations/1.sql"}))
    assert matched[0] == "security"
    risk_class, _, _ = selection(changed_paths=frozenset({"migrations/1.sql"}), assurance={"standard": 1})
    assert risk_class == "migration"


def test_strategy_is_decided_only_by_the_policys_stated_assurance() -> None:
    paths = frozenset({"src/auth/login.py"})
    assert selection(changed_paths=paths, assurance={"standard": 1, "security": 1})[1] == "single_pass"
    assert selection(changed_paths=paths, assurance={"standard": 1, "security": 2})[1] == "independent_panel"
    assert selection(changed_paths=paths, assurance={"standard": 1, "security": 3})[1] == "challenge_and_verify"


def test_a_non_adversarial_class_never_reaches_challenge_and_verify() -> None:
    paths = frozenset({".github/workflows/ci.yml"})
    risk_class, strategy, participants = selection(
        changed_paths=paths, assurance={"standard": 1, "infrastructure": 4}
    )
    assert risk_class == "infrastructure"
    assert strategy == "independent_panel"
    assert participants == 4


def test_a_missing_assurance_entry_falls_back_to_standard_then_to_one() -> None:
    paths = frozenset({"src/auth/login.py"})
    assert selection(changed_paths=paths, assurance={"standard": 3})[2] == 3
    assert selection(changed_paths=paths, assurance={})[2] == 1


def test_the_maximum_across_matched_classes_is_used() -> None:
    paths = frozenset({"src/auth/login.py", "migrations/1.sql"})
    _, _, participants = selection(
        changed_paths=paths, assurance={"standard": 1, "security": 2, "migration": 5}
    )
    assert participants == 5


def test_every_strategy_meets_its_own_minimum_participant_count() -> None:
    for assurance in ({"standard": 1}, {"standard": 2}, {"standard": 4}):
        for changed in (frozenset({"src/auth/a.py"}), frozenset({"docs/a.md"})):
            _, strategy, participants = selection(changed_paths=changed, assurance=assurance)
            assert participants >= STRATEGIES[strategy].minimum_participants


def test_append_failure_for_the_plan_entry_propagates() -> None:
    """T17's plan half: a plan whose durable record does not hold it is not a plan."""
    record = fx.FakeRecord(fail_kind="plan")
    try:
        plan_entry(
            job=fx.make_job(),
            facts=fx.make_facts(),
            snapshot=fx.make_snapshot(policy=fx.make_policy(obligations=(STANDARD,))),
            carry=fx.make_carry(),
            record=record,
        )
    except Exception as exc:  # noqa: BLE001 - the type is the assertion
        assert type(exc).__name__ == "AppendFailed"
    else:  # pragma: no cover - a swallowed AppendFailed is the defect under test
        raise AssertionError("AppendFailed did not propagate out of plan()")
