#!/usr/bin/env python3
"""`onboard()` — `code/P-03-policy.md` §3 E-17 and §8 rows T22–T26.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.
These tests drive the real `onboard()` over a temporary repository directory,
because the properties under test — never-overwrite, validate-before-write, and
byte-identical refusal — are exactly the ones a fake filesystem cannot prove.
"""

from __future__ import annotations

import contextlib
import importlib
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.policy.validate as policy_validate  # noqa: E402

# `rqa/policy/__init__.py` re-exports the `onboard` function under the same
# name as this submodule, which shadows the submodule as a package attribute.
# `sys.modules` lookup sidesteps that shadowing and gets the real module.
policy_onboard = importlib.import_module("rqa.policy.onboard")
from rqa.contracts import ValidationError, ValidationErrorCode, ValidationFailure  # noqa: E402
from rqa.policy import (  # noqa: E402
    OnboardRefusal,
    OnboardRefusalReason,
    PolicyError,
    Written,
    onboard,
)
from rqa.policy.onboard import migrate_config  # noqa: E402


@contextlib.contextmanager
def empty_repo():
    with tempfile.TemporaryDirectory() as directory:
        yield pathlib.Path(directory) / "repo"


def config_path(repo: pathlib.Path) -> pathlib.Path:
    return repo / ".rqa" / "config.json"


@contextlib.contextmanager
def forced_validate(result):
    """Substitute `onboard.py`'s bound `validate` for the duration of one test."""
    original = policy_onboard.validate
    policy_onboard.validate = lambda *args, **kwargs: result
    try:
        yield
    finally:
        policy_onboard.validate = original


# -- T22: plain onboarding writes a valid starter config ----------------------


def test_t22_onboard_writes_a_valid_starter_config_with_documented_defaults() -> None:
    with empty_repo() as repo:
        result = onboard(repo=str(repo))
        assert isinstance(result, Written)
        assert result.path == str(config_path(repo))

        document = json.loads(config_path(repo).read_text(encoding="utf-8"))
        validated = policy_validate.validate(document)
        assert not isinstance(validated, ValidationFailure), validated

        assert document["authority"] == {
            "review": False,
            "comment": False,
            "approve": False,
            "request_changes": False,
            "remediate": False,
            "merge": False,
        }
        assert document["routes"] == []
        assert document["policy"]["remediation"]["allow_forks"] is False
        assert validated.routes == ()
        assert validated.policy.remediation.allow_forks is False


# -- T23: plain onboarding never overwrites an existing config ----------------


def test_t23_onboard_refuses_to_overwrite_an_existing_config() -> None:
    with empty_repo() as repo:
        path = config_path(repo)
        path.parent.mkdir(parents=True)
        original_bytes = b'{"not": "a real config, deliberately"}'
        path.write_bytes(original_bytes)

        result = onboard(repo=str(repo))

        assert result == OnboardRefusal(OnboardRefusalReason.ALREADY_EXISTS, detail=str(path))
        assert path.read_bytes() == original_bytes
        assert not (path.parent / "config.json.tmp").exists()


def test_onboard_leaves_no_temp_file_behind_after_a_successful_write() -> None:
    with empty_repo() as repo:
        onboard(repo=str(repo))
        leftovers = list((repo / ".rqa").glob("*.tmp"))
        assert leftovers == []


def test_onboard_raises_policy_error_when_the_starter_its_own_validator_rejects() -> None:
    """§3 step 1.3: a starter config validate() rejects is this module's own bug."""
    failure = ValidationFailure(
        "", (ValidationError(code=ValidationErrorCode.UNKNOWN_KEY, path="x", detail="x"),)
    )
    with empty_repo() as repo:
        raised = None
        with forced_validate(failure):
            try:
                onboard(repo=str(repo))
            except PolicyError as exc:
                raised = exc
        assert isinstance(raised, PolicyError)
        assert not config_path(repo).exists()


# -- T24: migration converts authority and drops notification/retention -------


def _old_shape_document() -> dict:
    return {
        "authority": {"review": True, "fix": True, "triage": True},
        "notifications": {"transport": "file", "path": "/tmp/n.jsonl"},
        "retention": {"artifact_days": 30},
        "routes": [],
        "external": {"allowed": False, "deny_label": ""},
        "policy": {
            "version": "1",
            "obligations": [],
            "blocking": {"categories": [], "severities": [], "corroboration": 1},
            "mechanical": {"categories": [], "tools": []},
            "assurance": {},
        },
        "budget": {
            "per_pr_tokens": None,
            "per_repo_daily_tokens": None,
            "per_model_daily_tokens": 500,
        },
    }


def test_t24_migrate_converts_authority_drops_removed_keys_and_keeps_the_budget_axis() -> None:
    with empty_repo() as repo:
        path = config_path(repo)
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(_old_shape_document()), encoding="utf-8")

        result = onboard(repo=str(repo), migrate=True)

        assert isinstance(result, Written)
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["authority"] == {
            "review": True,
            "comment": False,
            "approve": False,
            "request_changes": False,
            "remediate": True,
            "merge": False,
        }
        assert "notifications" not in document
        assert "retention" not in document
        assert document["budget"]["per_model_daily_tokens"] == 500

        validated = policy_validate.validate(document)
        assert not isinstance(validated, ValidationFailure), validated


# -- T25: migrate with nothing to convert --------------------------------------


def test_t25_migrate_refuses_when_no_config_exists_and_writes_nothing() -> None:
    with empty_repo() as repo:
        result = onboard(repo=str(repo), migrate=True)
        assert result == OnboardRefusal(
            OnboardRefusalReason.NO_CONFIG_TO_MIGRATE, detail=str(config_path(repo))
        )
        assert not config_path(repo).exists()


# -- T26: migrate refuses when the converted result is still invalid ----------


def test_t26_migrate_refuses_and_leaves_the_original_file_untouched() -> None:
    with empty_repo() as repo:
        path = config_path(repo)
        path.parent.mkdir(parents=True)
        old = _old_shape_document()
        old["a-fifth-unknown-top-level-key"] = "wat"  # migrate_config copies it through
        original_bytes = json.dumps(old).encode("utf-8")
        path.write_bytes(original_bytes)

        result = onboard(repo=str(repo), migrate=True)

        assert isinstance(result, OnboardRefusal)
        assert result.reason == OnboardRefusalReason.MIGRATED_CONFIG_INVALID
        assert any(
            error.code == ValidationErrorCode.UNKNOWN_KEY for error in result.errors
        ), result.errors
        assert path.read_bytes() == original_bytes


def test_unreadable_existing_config_is_refused_without_writing() -> None:
    with empty_repo() as repo:
        path = config_path(repo)
        path.parent.mkdir(parents=True)
        original_bytes = b"{not valid json at all"
        path.write_bytes(original_bytes)

        result = onboard(repo=str(repo), migrate=True)

        assert isinstance(result, OnboardRefusal)
        assert result.reason == OnboardRefusalReason.UNREADABLE_EXISTING
        assert path.read_bytes() == original_bytes


# -- migrate_config: pure, no side effects -------------------------------------


def test_migrate_config_discards_the_old_triage_key_by_any_name() -> None:
    old = _old_shape_document()
    migrated = migrate_config(old)
    assert "triage" not in migrated["authority"]
    assert set(migrated["authority"]) == {
        "review",
        "comment",
        "approve",
        "request_changes",
        "remediate",
        "merge",
    }
    # Pure: the input is untouched.
    assert old["authority"] == {"review": True, "fix": True, "triage": True}


def test_migrate_config_drops_notification_and_retention_keys_wherever_nested() -> None:
    old = _old_shape_document()
    old["policy"]["nested_notifications_block"] = {"notifications": {"transport": "file"}}
    old["policy"]["nested_retention_block"] = {"retention": {"artifact_days": 1}}
    migrated = migrate_config(old)
    assert "notifications" not in migrated["policy"]["nested_notifications_block"]
    assert "retention" not in migrated["policy"]["nested_retention_block"]


def test_migrate_config_carries_every_other_key_through_unchanged() -> None:
    old = _old_shape_document()
    migrated = migrate_config(old)
    assert migrated["routes"] == old["routes"]
    assert migrated["external"] == old["external"]
    assert migrated["policy"] == old["policy"]
    assert migrated["budget"] == old["budget"]
