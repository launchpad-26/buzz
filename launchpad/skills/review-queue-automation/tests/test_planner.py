#!/usr/bin/env python3
"""Tests for planner.py — deterministic review-activity selection.

The planner decides WHICH questions a change requires. Properties under test:
selection is derived only from observable facts, it is reproducible, omissions are
recorded as explicitly as inclusions, and the prompt hint stays terse (a verbose
hint was measured to break verdict compliance).
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from planner import (  # noqa: E402
    ACTIVITY_BY_NAME,
    BASELINE,
    CHECK_COMPATIBILITY,
    DEBATE_ARCHITECTURE,
    DECOMPOSE,
    FALSIFY_CORRECTNESS,
    INVESTIGATE_HYPOTHESIS,
    PREMORTEM_RELIABILITY,
    RED_TEAM_SECURITY,
    REFINE_REMEDIATION,
    REGRESSION_REREVIEW,
    classify_changes,
    plan_review,
    render_activities,
)


# -- classification ------------------------------------------------------
def test_change_classes_recognise_their_surfaces() -> None:
    grouped = classify_changes([
        "src/auth/session.ts",
        "migrations/001_init.sql",
        "package.json",
        "deploy/chart.yaml",
        ".github/workflows/release.yml",
        "src/worker/queue.rs",
        "docs/guide.md",
        "tests/test_thing.py",
    ])
    assert "src/auth/session.ts" in grouped["security"]
    assert "migrations/001_init.sql" in grouped["contract"]
    assert "package.json" in grouped["dependency"]
    assert "deploy/chart.yaml" in grouped["infrastructure"]
    assert ".github/workflows/release.yml" in grouped["ci"]
    assert "src/worker/queue.rs" in grouped["concurrency"]
    assert "docs/guide.md" in grouped["docs"]
    assert "tests/test_thing.py" in grouped["tests"]


def test_unmatched_paths_are_not_classified() -> None:
    assert classify_changes(["src/util.ts"]) == {}


# -- baseline ------------------------------------------------------------
def test_code_change_gets_every_baseline_activity() -> None:
    plan = plan_review(files=["src/session.ts"], additions=12)
    for name in BASELINE:
        assert name in plan.activities, name


def test_docs_only_change_drops_the_deep_code_questions() -> None:
    plan = plan_review(files=["docs/a.md", "README.md"], additions=10)
    assert DECOMPOSE not in plan.activities
    assert FALSIFY_CORRECTNESS not in plan.activities
    assert "only documentation and tests" in plan.omitted[DECOMPOSE]
    # intent and evidence checks still apply
    assert "validate_intent" in plan.activities
    assert "verify_evidence" in plan.activities


def test_tests_only_change_is_also_narrow() -> None:
    plan = plan_review(files=["tests/test_a.py"], additions=30)
    assert FALSIFY_CORRECTNESS not in plan.activities


def test_code_alongside_docs_still_gets_code_questions() -> None:
    plan = plan_review(files=["docs/a.md", "src/session.ts"], additions=12)
    assert FALSIFY_CORRECTNESS in plan.activities


# -- conditional activation ---------------------------------------------
def test_security_paths_activate_the_security_question() -> None:
    plan = plan_review(files=["src/auth/login.ts"], additions=20)
    assert RED_TEAM_SECURITY in plan.activities
    assert "security-sensitive" in plan.reasons[RED_TEAM_SECURITY][0]


def test_absent_security_paths_record_the_omission() -> None:
    plan = plan_review(files=["src/ui/button.tsx"], additions=5)
    assert RED_TEAM_SECURITY not in plan.activities
    assert plan.omitted[RED_TEAM_SECURITY] == "no security-sensitive path changed"


def test_migrations_and_dependencies_activate_compatibility() -> None:
    for path in ("migrations/002.sql", "package.json", "Cargo.toml", "go.mod"):
        plan = plan_review(files=[path], additions=5)
        assert CHECK_COMPATIBILITY in plan.activities, path


def test_operational_surfaces_activate_reliability() -> None:
    for path in ("deploy/chart.yaml", ".github/workflows/ci.yml", "src/queue/worker.go"):
        plan = plan_review(files=[path], additions=5)
        assert PREMORTEM_RELIABILITY in plan.activities, path


def test_large_change_activates_architecture_debate() -> None:
    plan = plan_review(files=["src/a.ts"], additions=800, large_diff_lines=700)
    assert DEBATE_ARCHITECTURE in plan.activities
    assert "exceeds" in plan.reasons[DEBATE_ARCHITECTURE][0]


def test_broad_change_activates_architecture_debate() -> None:
    plan = plan_review(files=[f"src/m{i}.ts" for i in range(20)], additions=50)
    assert DEBATE_ARCHITECTURE in plan.activities
    assert "broad" in plan.reasons[DEBATE_ARCHITECTURE][0]


def test_small_narrow_change_omits_architecture_debate() -> None:
    plan = plan_review(files=["src/a.ts"], additions=10)
    assert DEBATE_ARCHITECTURE not in plan.activities


def test_failing_check_activates_investigation() -> None:
    plan = plan_review(files=["src/a.ts"], additions=5, checks_failing=True)
    assert INVESTIGATE_HYPOTHESIS in plan.activities


def test_rereview_activates_regression_question() -> None:
    plan = plan_review(files=["src/a.ts"], additions=5, is_rereview=True)
    assert REGRESSION_REREVIEW in plan.activities
    plan2 = plan_review(files=["src/a.ts"], additions=5, is_rereview=False)
    assert REGRESSION_REREVIEW not in plan2.activities
    assert plan2.omitted[REGRESSION_REREVIEW] == "first reviewed revision"


def test_verified_blocker_activates_remediation() -> None:
    plan = plan_review(files=["src/a.ts"], additions=5, verified_blocker=True)
    assert REFINE_REMEDIATION in plan.activities


def test_prior_disagreement_adds_architecture_debate() -> None:
    plan = plan_review(files=["src/a.ts"], additions=5, prior_disagreement=True)
    assert DEBATE_ARCHITECTURE in plan.activities
    assert any("disagreed" in r for r in plan.reasons[DEBATE_ARCHITECTURE])


# -- auditability --------------------------------------------------------
def test_every_activity_is_either_selected_or_omitted_with_a_reason() -> None:
    """A silently skipped question is indistinguishable from one that found nothing."""
    plan = plan_review(files=["src/a.ts"], additions=5)
    for name in plan.activities:
        assert plan.reasons.get(name), f"{name} selected without a reason"
    for name, why in plan.omitted.items():
        assert why, f"{name} omitted without a reason"
    accounted = set(plan.activities) | set(plan.omitted)
    assert accounted == set(ACTIVITY_BY_NAME), "every activity must be accounted for"


def test_plan_is_deterministic() -> None:
    kwargs = dict(files=["src/auth/x.ts", "migrations/1.sql"], additions=900)
    assert plan_review(**kwargs).as_dict() == plan_review(**kwargs).as_dict()


def test_plan_records_the_head_it_applies_to() -> None:
    plan = plan_review(files=["src/a.ts"], additions=5, head_sha="abc123")
    assert plan.as_dict()["head_sha"] == "abc123"


def test_no_duplicate_activities() -> None:
    """Two triggers for one activity must not list it twice."""
    plan = plan_review(files=[f"src/m{i}.ts" for i in range(20)],
                       additions=5000, prior_disagreement=True)
    assert len(plan.activities) == len(set(plan.activities))
    assert len(plan.reasons[DEBATE_ARCHITECTURE]) >= 2, "each trigger is still recorded"


# -- prompt hint ---------------------------------------------------------
def test_prompt_hint_is_terse() -> None:
    """A verbose hint was measured to break verdict compliance; keep it short."""
    plan = plan_review(files=["src/auth/x.ts"], additions=20)
    hint = render_activities(plan)
    assert len(hint) < 400, f"prompt hint too long ({len(hint)} chars)"
    # names present, full questions absent
    assert RED_TEAM_SECURITY in hint
    assert ACTIVITY_BY_NAME[RED_TEAM_SECURITY].question not in hint


def test_prompt_hint_suppresses_narration() -> None:
    hint = render_activities(plan_review(files=["src/a.ts"], additions=5))
    assert "Do NOT write out" in hint
    assert "only output" in hint


def test_empty_plan_renders_nothing() -> None:
    plan = plan_review(files=[], additions=0)
    plan.activities = []
    assert render_activities(plan) == ""


def test_full_questions_remain_available_for_audit() -> None:
    plan = plan_review(files=["src/auth/x.ts"], additions=20)
    questions = dict(plan.questions())
    assert questions[RED_TEAM_SECURITY].startswith("Attack this change")
