"""Real transport -> capability probe -> authority gate, with offline HTTP responses."""

import json
import pathlib
import sqlite3
import sys
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_authority_gate as fx
from rqa.authority.gate import Gate
from rqa.authority.store import SqliteCapabilityStore
from rqa.contracts import Activity, Deny, DenyReason, Grant
from rqa.github import GithubAdapter
from rqa.github.store import SqliteApiCallStore, SqliteEtagStore, SqliteMutationStore, ensure_schema
from rqa.github.transport import Response, Transport


def _ask(*, scopes="repo", private=True, push=True, managed=True, enabled=True):
    connection = sqlite3.connect(":memory:")
    ensure_schema(connection)
    calls = []

    def send(request):
        calls.append(request)
        assert request.method == "GET"
        headers = {} if scopes is None else {"X-OAuth-Scopes": scopes}
        if request.url.endswith("/user"):
            value = {"login": "fixture-operator"}
        else:
            value = {"private": private, "permissions": {"pull": True, "push": push}}
        return Response(200, headers, json.dumps(value))

    transport = Transport(etags=SqliteEtagStore(connection), api_calls=SqliteApiCallStore(connection), send=send)
    github = GithubAdapter(transport=transport, mutations=SqliteMutationStore(connection))
    store = SqliteCapabilityStore(connection)
    record = fx.FakeRecord()
    snapshot = fx.snapshot(enabled=frozenset({Activity.APPROVE}))
    if enabled is not True:
        from dataclasses import replace
        snapshot = replace(snapshot, authority={Activity.APPROVE: enabled})
    with patch("rqa.authority.capability.credential", return_value="fixture-only"):
        answer = Gate(repos={fx.REPO} if managed else set()).grant(
            repo=fx.REPO, activity=Activity.APPROVE, snapshot=snapshot,
            job_id=fx.JOB, categories=None, record=record, github=github, store=store,
        )
    connection.close()
    return answer, record, calls


def test_scoped_repository_write_attestation_grants_and_remains_distinct_in_record():
    answer, record, calls = _ask()
    assert isinstance(answer, Grant)
    attestation = record.kinds("attestation")[0]
    assert "pulls:write" in attestation["attested_not_proven"]
    assert "pulls:write" not in attestation["capabilities"]
    assert len(calls) == 3


def test_missing_scopes_read_only_access_and_unknown_visibility_deny():
    for kwargs in ({"scopes": None}, {"scopes": ""}, {"scopes": "read:user"},
                   {"scopes": "public_repo"}, {"push": False}, {"push": "true"},
                   {"scopes": "public_repo", "private": None}):
        answer, _, _ = _ask(**kwargs)
        assert isinstance(answer, Deny) and answer.reason is DenyReason.CAPABILITY_MISSING, kwargs


def test_public_repo_scope_is_sufficient_only_for_explicitly_public_repository():
    assert isinstance(_ask(scopes="public_repo", private=False)[0], Grant)


def test_unmanaged_and_non_boolean_authority_never_probe():
    answer, _, calls = _ask(managed=False)
    assert isinstance(answer, Deny) and answer.reason is DenyReason.REPO_NOT_MANAGED
    assert calls == []
    for enabled in (False, 1, "true"):
        answer, _, calls = _ask(enabled=enabled)
        assert isinstance(answer, Deny) and answer.reason is DenyReason.NOT_ENABLED
        assert calls == []


def test_legacy_unscoped_attestations_are_not_reused_after_upgrade():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE capabilities (id INTEGER PRIMARY KEY, repo TEXT, job_id TEXT, capabilities TEXT, attested TEXT, login TEXT, probed_at TEXT, UNIQUE(repo, job_id))")
    connection.execute("INSERT INTO capabilities VALUES (1, ?, ?, '[]', '[\"pulls:write\"]', 'operator', '2026-09-15T00:00:00+00:00')", (fx.REPO, fx.JOB))
    store = SqliteCapabilityStore(connection)
    assert store.current(fx.REPO, fx.JOB) is None
    assert connection.execute("SELECT count(*) FROM capabilities").fetchone()[0] == 1
    connection.close()
