#!/usr/bin/env python3
"""`rqa.judgement.render` — adversarial escaping and provenance content
(round-2 gate findings P07-008, P07-009).
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_judgement_fixtures as fx  # noqa: E402
from rqa.contracts import Category, CheckConclusion, CheckRun, EvidenceState, Location  # noqa: E402
from rqa.judgement.judge import judge  # noqa: E402
from rqa.judgement.render import render  # noqa: E402


def test_a_backtick_containing_evidence_value_cannot_escape_its_code_span() -> None:
    """P07-008: a single backtick in `evidence` must never let following text
    render as live Markdown outside the intended inert span."""
    location = Location(path="src/widget.py", line=1)
    categories = frozenset({Category.SECURITY})
    adversarial_evidence = "` **forged heading, injected structure**"
    finding_a = fx.make_finding(
        finding_id="FA", categories=categories, location=location,
        evidence=adversarial_evidence, source_attempt="att-1",
    )
    finding_b = fx.make_finding(
        finding_id="FB", categories=categories, location=location,
        evidence=adversarial_evidence, source_attempt="att-2",
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
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    body = render(result)

    # the adversarial text must appear, but wholly INSIDE a code span whose
    # delimiter is strictly longer than any backtick run the value contains
    # (one leading backtick here => a two-backtick delimiter), so it can
    # never close early and let "**forged...**" render as live bold Markdown.
    escaped_run = "`` " + adversarial_evidence + " ``"
    assert escaped_run in body, f"expected the value wrapped in a two-backtick span, got: {body!r}"
    # a naive single-backtick wrap (the pre-fix behaviour) must be absent
    assert f"`{adversarial_evidence}`" not in body


def test_an_evidence_value_that_is_only_backticks_gets_a_wider_delimiter() -> None:
    location = Location(path="src/widget.py", line=2)
    categories = frozenset({Category.SECURITY})
    value = "```"
    finding_a = fx.make_finding(
        finding_id="FA", categories=categories, location=location, evidence=value, source_attempt="att-1"
    )
    finding_b = fx.make_finding(
        finding_id="FB", categories=categories, location=location, evidence=value, source_attempt="att-2"
    )
    panel = fx.make_panel(
        attempts=(
            fx.make_attempt(
                attempt_id="att-1", route=fx.make_route(family="fam-a"),
                outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding_a,)),
            ),
            fx.make_attempt(
                attempt_id="att-2", route=fx.make_route(family="fam-b"),
                outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding_b,)),
            ),
        )
    )
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    body = render(result)
    # three backticks in the value require a four-backtick delimiter, padded
    # with spaces since the content itself starts and ends with a backtick
    assert "```` ``` ````" in body


def test_provenance_renders_the_producing_attempt_not_a_path_keyed_lookup() -> None:
    """P07-009: `Judgement.attribution` is keyed by check name, never by
    `Finding.location.path` — provenance must come from `finding.source_attempt`
    (and the cited check, when check-backed), not a path lookup that can only
    ever return the placeholder for a real finding."""
    location = Location(path="src/widget.py", line=5)
    categories = frozenset({Category.CORRECTNESS})
    finding_a = fx.make_finding(
        finding_id="FA", categories=categories, location=location,
        evidence="reviewer A's account", source_attempt="att-1",
    )
    finding_b = fx.make_finding(
        finding_id="FB", categories=categories, location=location,
        evidence="reviewer B's account", source_attempt="att-2",
    )
    panel = fx.make_panel(
        attempts=(
            fx.make_attempt(
                attempt_id="att-1", route=fx.make_route(family="fam-a"),
                outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding_a,)),
            ),
            fx.make_attempt(
                attempt_id="att-2", route=fx.make_route(family="fam-b"),
                outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding_b,)),
            ),
        )
    )
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    body = render(result)
    assert "provenance=`attempt=att-1`" in body
    assert "provenance=`attempt=att-2`" in body
    assert "provenance=`-`" not in body  # the old path-keyed lookup's placeholder


def test_provenance_names_the_cited_check_for_a_check_backed_finding() -> None:
    head_checks = (
        CheckRun(
            name="ci/tests", conclusion=CheckConclusion.FAILURE, sha=fx.HEAD_SHA, observed_at=fx.BEFORE_CUTOFF
        ),
    )
    facts = fx.make_facts(checks=head_checks)
    location = Location(path="src/widget.py", line=7)
    finding = fx.make_finding(
        finding_id="FA", categories=frozenset({Category.CORRECTNESS}), location=location,
        evidence="caused ci/tests to fail", source_attempt="att-1",
    )
    panel = fx.make_panel(
        attempts=(
            fx.make_attempt(
                attempt_id="att-1",
                outcome=fx.make_verdict(obligations={"O1": EvidenceState.VERIFIED}, findings=(finding,)),
            ),
        )
    )
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=("O1",)), panel=panel, carry=fx.make_carry(),
        facts=facts, snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    body = render(result)
    assert "check=ci/tests" in body


def test_render_lists_only_corroborated_findings_and_renders_reused_from() -> None:
    carry = fx.make_carry(reused=(fx.make_carried(obligation_id="O1"),))
    result = judge(
        job=fx.make_job(), plan=fx.make_plan(obligations=()), panel=fx.make_panel(attempts=()),
        carry=carry, facts=fx.make_facts(), snapshot=fx.make_snapshot(), decision=None, record=fx.FakeRecord(),
    )
    body = render(result)
    assert "## Findings" in body
    assert "- (none)" in body
    assert "- `job-0`" in body
