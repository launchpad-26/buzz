#!/usr/bin/env python3
"""Tests for github_auth.py — auth resolution and capability probing.

Properties under test:
  - the token value is never recorded anywhere, only its presence and source;
  - capability is derived from PROVEN permissions; anything unstated is absent;
  - capability can only REDUCE configured authority, never grant it;
  - a missing token or unreadable repo degrades the run instead of raising
    SystemExit and killing a sweep.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from github_auth import (  # noqa: E402
    FULL,
    RECOMMENDATION_ONLY,
    UNUSABLE,
    capabilities_from_permissions,
    downgrade_config_for_mode,
    probe,
    resolve_token_source,
)


class _Reader:
    """Fake REST reader; raises when a payload is set to an exception."""

    def __init__(self, viewer=None, repo=None):
        self._viewer = viewer if viewer is not None else {"login": "alice"}
        self._repo = repo if repo is not None else {
            "permissions": {"pull": True, "triage": True, "push": True},
            "has_issues": True,
        }

    def viewer(self):
        if isinstance(self._viewer, Exception):
            raise self._viewer
        return self._viewer

    def repo_meta(self, repo):
        if isinstance(self._repo, Exception):
            raise self._repo
        return self._repo


def _runner_ok(argv, capture_output=False, timeout=None, stdin=None):
    return subprocess.CompletedProcess(argv, 0, b"ghp_secretvalue\n", b"")


def _runner_fail(argv, capture_output=False, timeout=None, stdin=None):
    return subprocess.CompletedProcess(argv, 1, b"", b"not logged in")


# -- token handling ------------------------------------------------------
def test_token_presence_is_recorded_without_the_value(monkeypatch=None) -> None:
    source = resolve_token_source(_runner=_runner_ok)
    assert source.present is True
    assert source.source == "gh"
    blob = json.dumps(source.as_dict())
    assert "ghp_secretvalue" not in blob, "the token value must never be recorded"


def test_missing_token_degrades_instead_of_exiting() -> None:
    source = resolve_token_source(_runner=_runner_fail)
    assert source.present is False
    assert "not logged in" in source.reason


def test_absent_gh_binary_degrades() -> None:
    def missing(argv, **kwargs):
        raise FileNotFoundError("gh not found")

    source = resolve_token_source(_runner=missing)
    assert source.present is False
    assert "unavailable" in source.reason


def test_empty_token_output_is_not_present() -> None:
    def empty(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, b"   \n", b"")

    assert resolve_token_source(_runner=empty).present is False


# -- capability derivation ----------------------------------------------
def test_push_permission_yields_full_mode() -> None:
    caps = capabilities_from_permissions("alice", {"pull": True, "push": True, "triage": True})
    assert caps.mode == FULL
    assert caps.can_submit_review is True
    assert caps.can_add_labels is True


def test_read_only_permission_yields_recommendation_only_for_labels() -> None:
    """Read access can still submit a review, but not manage labels."""
    caps = capabilities_from_permissions("alice", {"pull": True})
    assert caps.repo_readable is True
    assert caps.can_submit_review is True
    assert caps.can_add_labels is False
    assert any("triage/push" in r for r in caps.reasons)


def test_no_permissions_is_unusable() -> None:
    caps = capabilities_from_permissions("alice", {"pull": False})
    assert caps.mode == UNUSABLE
    assert caps.repo_readable is False


def test_absent_permissions_object_is_unknown_and_absent() -> None:
    """Anything we cannot prove must be treated as missing, not assumed."""
    for payload in (None, {}, "nope"):
        caps = capabilities_from_permissions("alice", payload)  # type: ignore[arg-type]
        assert caps.mode == UNUSABLE
        assert "permissions" in caps.unknown


def test_issues_disabled_blocks_issue_creation() -> None:
    caps = capabilities_from_permissions(
        "alice", {"pull": True, "push": True}, has_issues=False
    )
    assert caps.can_create_issue is False
    assert any("issues unavailable" in r for r in caps.reasons)


def test_non_boolean_permission_values_are_ignored() -> None:
    caps = capabilities_from_permissions("alice", {"pull": "yes", "push": True})
    assert "pull" not in caps.permissions
    assert caps.permissions.get("push") is True


# -- probe ---------------------------------------------------------------
def test_probe_reports_full_mode_and_hides_the_token() -> None:
    report = probe({}, None, "o/r", _reader=_Reader(), _runner=_runner_ok)
    assert report["mode"] == FULL
    assert report["token"]["present"] is True
    assert "ghp_secretvalue" not in json.dumps(report)
    assert report["capabilities"]["login"] == "alice"


def test_probe_without_a_token_is_unusable_and_does_not_read() -> None:
    class Exploding:
        def viewer(self):
            raise AssertionError("must not read GitHub without a token")

        def repo_meta(self, repo):
            raise AssertionError("must not read GitHub without a token")

    report = probe({}, None, "o/r", _reader=Exploding(), _runner=_runner_fail)
    assert report["mode"] == UNUSABLE


def test_probe_survives_an_unreadable_repository() -> None:
    report = probe({}, None, "o/r",
                   _reader=_Reader(repo=RuntimeError("404 Not Found")),
                   _runner=_runner_ok)
    assert report["mode"] == UNUSABLE
    assert any("unreadable" in r for r in report["capabilities"]["reasons"])


def test_probe_survives_a_failing_viewer_read() -> None:
    """A viewer failure must not lose the capability signal from the repo read."""
    report = probe({}, None, "o/r",
                   _reader=_Reader(viewer=RuntimeError("boom")),
                   _runner=_runner_ok)
    assert report["mode"] == FULL
    assert "viewer_error" in report


# -- authority clamping -------------------------------------------------
def _live_config() -> dict:
    return {
        "authority": {"approve": "live", "request_changes": "live",
                       "comment": "live", "fix": "live", "triage": "disabled"},
        "approval": {"mode": "live", "approval_enabled": True,
                      "live_canary_approved": True},
    }


def test_full_mode_leaves_authority_untouched() -> None:
    reduced = downgrade_config_for_mode(_live_config(), FULL)
    assert reduced["authority"]["approve"] == "live"
    assert reduced["approval"]["mode"] == "live"


def test_recommendation_only_downgrades_every_mutating_authority() -> None:
    reduced = downgrade_config_for_mode(_live_config(), RECOMMENDATION_ONLY)
    for activity in ("approve", "request_changes", "comment", "fix"):
        assert reduced["authority"][activity] == "human_escalation"
    assert reduced["approval"]["mode"] == "human_escalation"
    assert reduced["approval"]["approval_enabled"] is False


def test_clamping_never_grants_authority() -> None:
    """A disabled activity must not be raised by any capability mode."""
    disabled = {"authority": {"approve": "disabled", "request_changes": "disabled"},
                "approval": {"mode": "disabled"}}
    for mode in (FULL, RECOMMENDATION_ONLY, UNUSABLE):
        reduced = downgrade_config_for_mode(disabled, mode)
        assert reduced["authority"]["approve"] == "disabled"
        assert reduced["approval"]["mode"] == "disabled"


def test_clamping_does_not_mutate_the_caller_config() -> None:
    original = _live_config()
    downgrade_config_for_mode(original, UNUSABLE)
    assert original["authority"]["approve"] == "live"
    assert original["approval"]["approval_enabled"] is True
