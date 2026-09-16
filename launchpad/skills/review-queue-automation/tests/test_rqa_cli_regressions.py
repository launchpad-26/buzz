"""Regression coverage through the real CLI composition and real SQLite stores."""

import contextlib
import importlib
import io
import json
import pathlib
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_authority_gate as authority_fx
from test_rqa_cli_main import _run
from rqa.cli.composition import build_composition
from rqa.contracts import Activity, Deny, DenyReason, GithubUnavailable, Grant
from rqa.github import GithubAdapter
from rqa.github.transport import Response, Transport

main_module = importlib.import_module("rqa.cli.main")


def test_bad_inputs_leave_no_state_or_phantom_checkout():
    with tempfile.TemporaryDirectory() as directory:
        state = pathlib.Path(directory) / "absent"
        for args in (("status", "o/r", "1"), ("pending",), ("explain", "job", "missing"),
                     ("tick", "--batch-size", "0"), ("tick", "--repo", "../repo"),
                     ("tick", "--repo", "o/.."), ("status", "o/r", "-1"),
                     ("onboard", ""), ("onboard", str(state / "phantom"))):
            code, payload = _run(state, *args)
            assert code == 1, (args, payload)
            assert not state.exists(), args
        with patch.dict("os.environ", {"RQA_STATE_DIR": ""}), contextlib.redirect_stdout(io.StringIO()):
            assert main_module.main(["tick"]) == 1
        assert not state.exists()


def test_tick_reports_inventory_outage_and_authentication_failure():
    tick_module = importlib.import_module("rqa.intake.tick")
    for reason, expected in (("unreachable", 2), ("unauthenticated", 3)):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            tick_module, "_check_admission", return_value=None
        ), patch.object(GithubAdapter, "inventory", return_value=GithubUnavailable(
            op="inventory", reason=reason, retriable=reason == "unreachable"
        )):
            code, payload = _run(pathlib.Path(directory), "tick", "--repo", "o/r")
            assert code == expected, payload
            assert payload["outcome"] == "incomplete"
            assert payload["result"]["repos_failed"][0]["reason"] == reason


def test_real_composition_grants_only_configured_repository_with_scoped_attestation():
    with tempfile.TemporaryDirectory() as directory:
        comp = build_composition(pathlib.Path(directory), repos=(authority_fx.REPO,))
        calls = []

        def exchange(self, request, **kwargs):
            calls.append((request.method, request.url))
            assert request.method == "GET"
            value = ({"login": "fixture-operator"} if request.url.endswith("/user") else
                     {"private": True, "permissions": {"pull": True, "push": True}})
            return Response(200, {"X-OAuth-Scopes": "repo"}, json.dumps(value))

        # Replace the network exchange only: composition, probe, gate, cache,
        # record writer and database are the production implementations.
        with patch.object(Transport, "_exchange", exchange), patch(
            "rqa.authority.capability.credential", return_value="fixture-only"
        ):
            kwargs = dict(activity=Activity.APPROVE, snapshot=authority_fx.snapshot(
                enabled=frozenset({Activity.APPROVE})), job_id="job", categories=None,
                github=comp.github, store=comp.authority.store, record=comp.record)
            answer = comp.authority.grant(repo=authority_fx.REPO, **kwargs)
            assert isinstance(answer, Grant), answer
            before = len(calls)
            denied = comp.authority.grant(repo="unmanaged/repo", **kwargs)
            assert isinstance(denied, Deny) and denied.reason is DenyReason.REPO_NOT_MANAGED
            assert len(calls) == before
        comp.connection.commit()
        rows = comp.connection.execute("SELECT payload FROM record_entries WHERE kind='attestation'").fetchall()
        assert rows
        proof = json.loads(rows[0][0])
        assert "pulls:write" in proof["attested_not_proven"]
        assert "pulls:write" not in proof["capabilities"]
        comp.connection.close()


def test_explain_unknown_job_echoes_requested_subject():
    with tempfile.TemporaryDirectory() as directory:
        state = pathlib.Path(directory)
        build_composition(state).connection.close()
        code, payload = _run(state, "explain", "job", "requested-job")
        assert code == 1 and payload["subject"] == {"job_id": "requested-job"}


def test_decision_controls_are_escaped_in_the_record_and_explanation():
    from test_rqa_cli_main import _seed_escalated_job, _offline_composition
    from rqa.contracts import EscalationCause
    from rqa.cli.render import sanitize_text
    import sqlite3
    with tempfile.TemporaryDirectory() as directory:
        state = pathlib.Path(directory)
        eid = _seed_escalated_job(state, job_id="text-job", repo="o/r", number=1,
            cause=EscalationCause.EVIDENCE_GAP, question="first\nsecond\u202e",
            context={"obligation": "ob-1"})
        code, pending = _run(state, "pending")
        assert code == 0 and pending["result"][0]["question"] == sanitize_text("first\nsecond\u202e")
        actor, basis = "human\x1b[31m", "observed\nsecond line\u2028"
        with _offline_composition():
            code, payload = _run(state, "decide", str(eid), "--actor", actor, "--basis", basis)
        assert code == 0, payload
        with sqlite3.connect(state / "state.db") as connection:
            saved = json.loads(connection.execute("SELECT payload FROM record_entries WHERE kind='decision'").fetchone()[0])
        assert saved["actor"] == sanitize_text(actor)
        assert saved["basis"] == sanitize_text(basis.strip())
        code, explained = _run(state, "explain", "job", "text-job")
        assert code == 0, explained
        assert explained["result"]["reviewer_identity"] == [saved["actor"]]
        assert explained["result"]["decision_basis"] == saved["basis"]
