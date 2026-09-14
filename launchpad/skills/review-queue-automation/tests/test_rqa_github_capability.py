#!/usr/bin/env python3
"""E-16 `probe` — `code/P-09-github-adapter.md` §3.4, §8 row T9; ADR-0062.

The probe is read-only and needs no grant: T9's fake transport raises on any
mutation helper invocation, so a successful probe is the proof that zero write
calls happened.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import CapabilityReading, GithubUnavailable  # noqa: E402
from rqa.github import GithubAdapter  # noqa: E402
from rqa.github import transport as transport_module  # noqa: E402
from rqa.github.testing import NON_TOKEN_CREDENTIAL  # noqa: E402

FIXED_NOW = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)


class ProbeTransport:
    """rest_json fixtures only. Every write-capable helper raises: a probe
    performs no write to establish a write capability (§3.4)."""

    def __init__(self, json_by_path):
        self.json_by_path = dict(json_by_path)
        self.credentials_seen = []

    def rest_json(self, path, *, operation, credential=None):
        self.credentials_seen.append(credential)
        value = self.json_by_path[path]
        if isinstance(value, Exception):
            raise value
        return value

    def mutate(self, *args, **kwargs):
        raise AssertionError("probe attempted a mutation")

    def graphql(self, *args, **kwargs):
        raise AssertionError("probe attempted a GraphQL call")

    def rest_paginated(self, *args, **kwargs):
        raise AssertionError("probe attempted a paginated read")

    def rest_text(self, *args, **kwargs):
        raise AssertionError("probe attempted a text read")


def adapter_with(transport) -> GithubAdapter:
    class _NoMutations:
        def find(self, cmid):
            raise AssertionError("probe touched the mutations store")

        def put(self, row):
            raise AssertionError("probe wrote the mutations store")

    return GithubAdapter(transport=transport, mutations=_NoMutations(), clock=lambda: FIXED_NOW)


def repo_meta(**permissions):
    merged = {"pull": False, "triage": False, "push": False, "maintain": False, "admin": False}
    merged.update(permissions)
    return {"full_name": "octo/repo", "permissions": merged}


def test_t9_probe_returns_a_reading_with_zero_write_calls() -> None:
    transport = ProbeTransport(
        {
            "/user": {"login": "operator"},
            "/repos/octo/repo": repo_meta(pull=True, push=True),
        }
    )
    result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
    assert isinstance(result, CapabilityReading)
    assert result.login == "operator"
    # Proven reads: the probe itself exercised them with this credential.
    assert result.capabilities == frozenset({"pulls:read", "contents:read", "checks:read"})
    # Writes are only ever attested, never proven (ADR-E residual).
    assert result.attested_not_proven == frozenset(
        {"pulls:write", "contents:write", "issues:write"}
    )
    # The caller-supplied credential was used on every read (§4's exception).
    assert transport.credentials_seen == [NON_TOKEN_CREDENTIAL, NON_TOKEN_CREDENTIAL]


def test_probe_read_only_permission_attests_no_write() -> None:
    transport = ProbeTransport(
        {"/user": {"login": "operator"}, "/repos/octo/repo": repo_meta(pull=True)}
    )
    result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
    assert result.capabilities == frozenset({"pulls:read", "contents:read", "checks:read"})
    assert result.attested_not_proven == frozenset()


def test_probe_triage_attests_assignee_writes_only() -> None:
    transport = ProbeTransport(
        {"/user": {"login": "operator"}, "/repos/octo/repo": repo_meta(pull=True, triage=True)}
    )
    result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
    assert result.attested_not_proven == frozenset({"issues:write"})


def test_probe_unauthenticated_user_endpoint_is_unauthenticated() -> None:
    transport = ProbeTransport(
        {
            "/user": transport_module.Unavailable(
                reason="unauthenticated", retriable=False, status=401
            )
        }
    )
    result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
    assert result == GithubUnavailable(op="probe", reason="unauthenticated", retriable=False)


def test_probe_unreadable_user_endpoint_is_unauthenticated_too() -> None:
    transport = ProbeTransport(
        {"/user": transport_module.Unavailable(reason="unreachable", retriable=True)}
    )
    result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
    assert result == GithubUnavailable(op="probe", reason="unauthenticated", retriable=False)


def test_probe_403_or_404_repository_is_the_empty_capability_reading() -> None:
    for status in (403, 404):
        transport = ProbeTransport(
            {
                "/user": {"login": "operator"},
                "/repos/octo/repo": transport_module.Unavailable(
                    reason="not_found", retriable=False, status=status
                ),
            }
        )
        result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
        assert result == CapabilityReading(
            capabilities=frozenset(), attested_not_proven=frozenset(), login="operator"
        ), status


def test_probe_rate_limited_or_unreachable_repository_is_retriable() -> None:
    for reason in ("rate_limited", "unreachable"):
        transport = ProbeTransport(
            {
                "/user": {"login": "operator"},
                "/repos/octo/repo": transport_module.Unavailable(
                    reason=reason, retriable=True, status=None
                ),
            }
        )
        result = adapter_with(transport).probe(repo="octo/repo", credential=NON_TOKEN_CREDENTIAL)
        assert result == GithubUnavailable(op="probe", reason=reason, retriable=True), reason
