#!/usr/bin/env python3
"""Disposition-precedence and policy-attribution coverage beyond `code/P-07-judgement.md`
§8's 18 rows — the two extra DoD rows the issue names.

AC11 / RQA-FR-039 (bound_reached escalation) is §8's own T7c and lives in
`test_rqa_judgement_judge.py`; the two-snapshots-differing-only-in-blocking-policy
row (AC02, RQA-FR-003) is new and lives here.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import replace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_judgement_fixtures as fx  # noqa: E402
from rqa.contracts import Category, EvidenceState, Location  # noqa: E402
from rqa.judgement.judge import judge  # noqa: E402


def test_ac02_two_snapshots_differing_only_in_blocking_policy_give_two_blocking_outcomes() -> None:
    """RQA-FR-003 / AC02: identical job, facts, panel result and carry-over; only
    `policy.blocking.categories` differs between the two snapshots. The disposition
    difference is attributable to that one field alone.
    """
    job = fx.make_job()
    facts = fx.make_facts()
    plan = fx.make_plan(obligations=("O1",))
    carry = fx.make_carry()

    location = Location(path="src/widget.py", line=3)
    categories = frozenset({Category.SECURITY})
    finding_a = fx.make_finding(
        finding_id="FA", categories=categories, location=location, source_attempt="att-1"
    )
    finding_b = fx.make_finding(
        finding_id="FB", categories=categories, location=location, source_attempt="att-2"
    )
    attempt_a = fx.make_attempt(
        attempt_id="att-1", route=fx.make_route(family="fam-a"),
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding_a,)),
    )
    attempt_b = fx.make_attempt(
        attempt_id="att-2", route=fx.make_route(family="fam-b"),
        outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding_b,)),
    )
    panel = fx.make_panel(attempts=(attempt_a, attempt_b))

    lenient_policy = fx.make_policy(blocking_categories=frozenset())
    strict_policy = replace(lenient_policy, blocking=replace(lenient_policy.blocking, categories=frozenset({Category.SECURITY})))
    assert lenient_policy == replace(strict_policy, blocking=lenient_policy.blocking), (
        "the two policies must differ only in blocking.categories"
    )

    lenient_snapshot = replace(fx.make_snapshot(policy=lenient_policy), hash="snap-lenient")
    strict_snapshot = replace(fx.make_snapshot(policy=strict_policy), hash="snap-strict")

    lenient_record = fx.FakeRecord()
    strict_record = fx.FakeRecord()
    lenient_result = judge(
        job=job, plan=plan, panel=panel, carry=carry, facts=facts,
        snapshot=lenient_snapshot, decision=None, record=lenient_record,
    )
    strict_result = judge(
        job=job, plan=plan, panel=panel, carry=carry, facts=facts,
        snapshot=strict_snapshot, decision=None, record=strict_record,
    )

    assert lenient_result.disposition == "approve"
    assert lenient_result.blocking == frozenset()
    assert strict_result.disposition == "request_changes"
    assert {"FA", "FB"} <= strict_result.blocking
    # both runs corroborated the identical finding pair identically; only the
    # blocking classification (policy-derived) differs.
    assert lenient_result.corroborated == strict_result.corroborated
    assert lenient_result.obligations == strict_result.obligations

    # The persisted record — not just the returned Judgement — attributes the
    # difference to policy alone: the two snapshots carry distinct hashes
    # (reflecting their differing policy content) and the corresponding
    # `judgement` payloads differ in exactly `disposition`/`blocking`, never
    # in the corroboration or obligation-state fields.
    lenient_payload = lenient_record.of_kind("judgement")[0]
    strict_payload = strict_record.of_kind("judgement")[0]
    assert lenient_payload["snapshot_hash"] == "snap-lenient"
    assert strict_payload["snapshot_hash"] == "snap-strict"
    assert lenient_payload["disposition"] == "approve"
    assert strict_payload["disposition"] == "request_changes"
    assert lenient_payload["blocking"] == []
    assert set(strict_payload["blocking"]) >= {"FA", "FB"}
    assert lenient_payload["corroborated"] == strict_payload["corroborated"]
    assert lenient_payload["obligations"] == strict_payload["obligations"]
