"""Task #2215 — mutation verification for the lifecycle conformance checks.

A guard that a demonstrated mutation survives is not a guard. Every criterion
`test_rqa_conformance_lifecycle.py` reports as met is checked by a pure
`_..._violations` helper; this file hands each of those helpers a system that does
*not* meet the criterion and asserts it says so. Without this file, a helper that had
silently degraded to `return []` would keep the suite green while proving nothing.

The mutations perturb **the proof harness's view of the world** — a wrong expected
value, a cached read, a drifted table, a deliberately broken config. None of them
edits `rqa/`. The product is never modified to make a proof pass or fail; that would
be proving a fiction in the opposite direction.

Each test names, in its assertion message, what the mutation represents: the real
regression that would produce that shape. A mutation nobody could plausibly ship is
not evidence that the check is load-bearing.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import Assurance, EvidenceState  # noqa: E402
from rqa.lifecycle.states import DISPOSITION  # noqa: E402
from rqa.policy import SqliteSnapshotStore, snapshot_for  # noqa: E402
from rqa.policy.snapshot import config_path  # noqa: E402
from rqa.policy.types import ValidationFailure  # noqa: E402
from rqa.policy.validate import starter_config  # noqa: E402
from rqa.record.explain import DISPOSITION_TABLE  # noqa: E402
from tests.test_rqa_conformance_lifecycle import (  # noqa: E402
    AC05_EVIDENCE_STATES,
    AC06_RECONSTRUCTION_ELEMENTS,
    FR016_DISPOSITIONS,
    TRUST_DISCLOSURE_FIELDS,
    _disposition_drift,
    _disposition_vocabulary_violations,
    _evidence_vocabulary_violations,
    _fail_closed_violations,
    _missing_reconstruction_elements,
    _missing_trust_disclosure,
    _policy_reread_violations,
    _protocol_invariance_violations,
    _semantic_divergence,
)

_CANONICAL = {status.value: answer.value for status, answer in DISPOSITION.items()}


def test_mutation_ac08_an_invented_disposition_is_caught() -> None:
    """Regression shape: a new internal state is added and its operator-facing answer
    is invented at the render site rather than mapped into FR-016's six."""
    mutated = dict(_CANONICAL)
    mutated["reviewing"] = "in progress"
    violations = _disposition_vocabulary_violations(declared=FR016_DISPOSITIONS, mapping=mutated)
    assert violations, "an answer outside FR-016's six was not reported"
    assert any("in progress" in violation for violation in violations), violations


def test_mutation_ac08_a_shrunken_vocabulary_is_caught() -> None:
    """Regression shape: a disposition is quietly dropped from the enum, so a state
    that used to have an answer silently loses one."""
    violations = _disposition_vocabulary_violations(
        declared=FR016_DISPOSITIONS - {"unable to progress"}, mapping=_CANONICAL
    )
    assert violations, "a vocabulary missing one of FR-016's six was not reported"


def test_mutation_ac08_table_drift_between_status_and_explain_is_caught() -> None:
    """Regression shape: `explain`'s table is updated for a renamed state and
    `status`'s is not, so one job reports two different dispositions."""
    drifted = dict(DISPOSITION_TABLE)
    drifted["escalated"] = "blocked"
    divergence = _disposition_drift(canonical=_CANONICAL, reconstructed=drifted)
    assert divergence, "two tables answering differently for one state was not reported"
    assert any("escalated" in item for item in divergence), divergence


def test_mutation_ac08_a_state_missing_from_the_reconstruction_table_is_caught() -> None:
    """Regression shape: a state `status` can return has no row in `explain`'s table,
    so the reconstruction renders a raw internal name to an operator."""
    incomplete = {k: v for k, v in DISPOSITION_TABLE.items() if k != "merged"}
    divergence = _disposition_drift(canonical=_CANONICAL, reconstructed=incomplete)
    assert divergence, "a state absent from the reconstruction table was not reported"


def test_mutation_ac06_a_dropped_reconstruction_element_is_caught() -> None:
    """Regression shape: a refactor removes `provider` from the reconstruction type,
    so an outcome can no longer name which provider produced it."""
    for element in AC06_RECONSTRUCTION_ELEMENTS:
        fields = frozenset(AC06_RECONSTRUCTION_ELEMENTS) - {element}
        missing = _missing_reconstruction_elements(fields=fields)
        assert missing == [element], (element, missing)


def test_mutation_ac06_a_dropped_trust_disclosure_is_caught() -> None:
    """Regression shape: `unverifiable` is dropped, so a reconstruction over an
    unauthenticated record reads exactly like one over an authenticated record."""
    for name in TRUST_DISCLOSURE_FIELDS:
        fields = frozenset(TRUST_DISCLOSURE_FIELDS) - {name}
        assert _missing_trust_disclosure(fields=fields) == [name], name


def test_mutation_ac05_a_widened_evidence_vocabulary_is_caught() -> None:
    """Regression shape: a permissive state such as `assumed` is added, giving a
    reviewer a way to record evidence it never examined."""
    violations = _evidence_vocabulary_violations(declared=AC05_EVIDENCE_STATES | {"assumed"})
    assert violations, "an extra evidence state was not reported"
    assert any("assumed" in violation for violation in violations), violations


def test_mutation_ac05_a_system_that_approves_on_unsatisfied_evidence_is_caught() -> None:
    """The mutation this whole batch exists to catch: an assurance calculation that
    always reports the bar met, so `judge` never raises an evidence gap and a
    successful disposition becomes producible with nothing verified."""

    def always_satisfied(*, states, required: int) -> Assurance:
        return Assurance(required=required, achieved=required)

    violations = _fail_closed_violations(assurance_of=always_satisfied)
    assert violations, "a system that approves on unsatisfied evidence was not reported"
    unsatisfied = [member.value for member in EvidenceState if member is not EvidenceState.VERIFIED]
    for state in unsatisfied:
        assert any(state in violation for violation in violations), (state, violations)


def test_mutation_ac05_a_system_that_can_never_succeed_is_also_caught() -> None:
    """The opposite failure, and the reason the check carries a `verified` control: a
    calculation that always falls short would satisfy a naive "never approves"
    reading while making every review impossible. Fail-closed is not fail-always."""

    def never_satisfied(*, states, required: int) -> Assurance:
        return Assurance(required=required, achieved=0)

    violations = _fail_closed_violations(assurance_of=never_satisfied)
    assert violations, "a system that can never reach assurance was not reported"
    assert any("fully satisfied" in violation for violation in violations), violations


def test_mutation_ac02_a_cached_policy_read_is_caught() -> None:
    """Regression shape: `config_path` or the validated config is memoised, so an
    operator's policy edit needs a process restart — precisely what AC02 forbids."""
    violations = _policy_reread_violations(first="a" * 64, second="a" * 64, third="a" * 64)
    assert violations, "a policy pin unchanged across an edit was not reported"
    assert any("did not observe the edit" in violation for violation in violations), violations


def test_mutation_ac02_an_impure_policy_pin_is_caught() -> None:
    """Regression shape: the pin folds in activation time or a sequence number, so
    two identical configurations no longer reproduce one identity and "reproduce what
    this job ran under" stops working."""
    violations = _policy_reread_violations(first="a" * 64, second="b" * 64, third="c" * 64)
    assert violations, "a pin that did not return to its original value was not reported"
    assert any("pure function" in violation for violation in violations), violations


def test_mutation_ac02_a_broken_config_is_refused_not_served_from_cache() -> None:
    """A live mutation against the real read path rather than the helper: after one
    good read, the configuration on disk is truncated mid-object. The next read must
    refuse. Serving the last-known-good snapshot instead would make every AC02
    demonstration meaningless — the system would be answering from memory, not from
    the operator's file."""
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        repo = str(root / "owner" / "name")
        path = config_path(repo)
        path.parent.mkdir(parents=True)
        store = SqliteSnapshotStore(root / "state")
        path.write_text(json.dumps(starter_config()), encoding="utf-8")

        good = snapshot_for(repo=repo, job=None, store=store, record=None)
        assert hasattr(good, "hash"), good

        text = path.read_text(encoding="utf-8")
        path.write_text(text[: len(text) // 2], encoding="utf-8")
        after = snapshot_for(repo=repo, job=None, store=store, record=None)
        assert isinstance(after, ValidationFailure), (
            "a truncated configuration was not refused; the read was served from a cache "
            f"or a last-known-good snapshot: {after!r}"
        )


def test_mutation_ac17_a_route_dependent_protocol_is_caught() -> None:
    """Regression shape: the protocol pin starts folding in the configured routes, so
    the definition a verdict validates against depends on who produced it."""
    violations = _protocol_invariance_violations(
        pins={"provider-enabled": "a" * 64, "provider-removed": "b" * 64}
    )
    assert violations, "a protocol pin that moved with the provider was not reported"


def test_mutation_ac01_divergent_route_semantics_are_caught() -> None:
    """Regression shape: one route's obligation states are mapped through a different
    vocabulary, so two reviews of one PR no longer carry the same concepts."""
    left = ("1", (("O-1", "verified"),), ())
    right = ("1", (("O-1", "passed"),), ())
    assert _semantic_divergence(left=left, right=right), "divergent semantics were not reported"
    assert _semantic_divergence(left=left, right=left) == []
