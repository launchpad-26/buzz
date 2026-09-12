#!/usr/bin/env python3
"""The shared write discipline and the five write edges — `code/P-09-github-adapter.md`
§3 preamble, §3.1, §3.2, §6, §8 rows T1, T2, T3, T7, T8, T11, T12.

Every test runs against a fake transport, a fake `MutationStore`, and a fake
`RecordWriter` — fixture responses, no network (§8's preamble; U-DOCS-24's
`NON_TOKEN_CREDENTIAL` is the only credential-shaped string in this file).
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Entry,
    GithubUnavailable,
    Grant,
    Job,
    JobStatus,
    LeaseTaken,
    Mutation,
    Stale,
)
from rqa.github import AdapterError, GithubAdapter, MutationKind  # noqa: E402
from rqa.github import transport as transport_module  # noqa: E402
from rqa.github import writes  # noqa: E402
from rqa.github.testing import NON_TOKEN_CREDENTIAL  # noqa: E402

FIXED_NOW = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)


def make_job(**over) -> Job:
    fields = dict(
        id="job-1",
        repo="octo/repo",
        number=7,
        head_sha="H1",
        base_sha="B1",
        head_repo="octo/repo",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.QUEUED,
    )
    fields.update(over)
    return Job(**fields)


def make_grant(activity: Activity, **over) -> Grant:
    fields = dict(
        activity=activity,
        repo="octo/repo",
        job_id="job-1",
        snapshot_hash="snap-1",
        capability_proof_id=1,
        categories=None,
        entry_seq=1,
    )
    fields.update(over)
    return Grant(**fields)


def node_payload(*, viewer="operator", assignees=(), state="OPEN", head="H1", pr_id="PR_1"):
    return {
        "viewer": {"login": viewer, "id": "U_operator"},
        "repository": {
            "pullRequest": {
                "id": pr_id,
                "state": state,
                "headRefOid": head,
                "assignees": {
                    "nodes": [{"login": login, "id": f"U_{login}"} for login in assignees]
                },
            }
        },
    }


class FakeTransport:
    """Duck-typed transport: a queue of GraphQL node payloads, one mutate
    result, one reviews fixture. Records every call."""

    def __init__(self, *, nodes, mutate=None, mutate_error=None, reviews=None, reviews_error=None):
        self.nodes = list(nodes)
        self._mutate = {"accepted": True} if mutate is None else mutate
        self._mutate_error = mutate_error
        self._reviews = [] if reviews is None else reviews
        self._reviews_error = reviews_error
        self.graphql_calls = []
        self.mutate_calls = []
        self.rest_calls = []

    def call_count(self) -> int:
        return len(self.graphql_calls) + len(self.mutate_calls) + len(self.rest_calls)

    def graphql(self, document, variables, *, operation, credential=None):
        self.graphql_calls.append((document, dict(variables), operation))
        payload = self.nodes.pop(0) if len(self.nodes) > 1 else self.nodes[0]
        if isinstance(payload, Exception):
            raise payload
        return payload

    def mutate(self, document, variables, *, operation, credential=None):
        self.mutate_calls.append((document, dict(variables), operation))
        if self._mutate_error is not None:
            raise self._mutate_error
        return self._mutate

    def rest_paginated(self, path, *, operation, page_cap, item_key=None, credential=None):
        self.rest_calls.append(path)
        if self._reviews_error is not None:
            raise self._reviews_error
        return list(self._reviews)

    def rest_json(self, *args, **kwargs):
        raise AssertionError("write path made an unexpected rest_json call")

    def rest_text(self, *args, **kwargs):
        raise AssertionError("write path made an unexpected rest_text call")


class PoisonTransport:
    """Every method is a defect: proves a code path made zero GitHub calls."""

    def _refuse(self, *args, **kwargs):
        raise AssertionError("unexpected GitHub call")

    graphql = mutate = rest_paginated = rest_json = rest_text = _refuse


class FakeMutations:
    def __init__(self):
        self.rows = {}
        self.puts = []

    def find(self, client_mutation_id):
        return self.rows.get(client_mutation_id)

    def put(self, row):
        self.rows[row.client_mutation_id] = row
        self.puts.append(row)


class FakeRecord:
    def __init__(self):
        self.entries = []

    def append(self, job_id, kind, payload):
        self.entries.append((job_id, kind, dict(payload)))
        return Entry(seq=len(self.entries), hash=f"hash-{len(self.entries)}")


class RaisingRecord:
    def append(self, job_id, kind, payload):
        raise AppendFailed("record store refused the append")


def adapter_with(transport, mutations=None):
    return GithubAdapter(
        transport=transport,
        mutations=FakeMutations() if mutations is None else mutations,
        clock=lambda: FIXED_NOW,
    )


def expected_cmid(job: Job, kind: MutationKind, payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256("\x1f".join((job.id, kind.value, canonical)).encode()).hexdigest()


def _write_calls(adapter, job, record, grant_for=None):
    """The five §6 write edges as (name, closure(grant)) pairs."""
    return [
        ("claim_lease", lambda grant: adapter.claim_lease(job=job, grant=grant, record=record)),
        ("release_lease", lambda grant: adapter.release_lease(job=job, grant=grant, record=record)),
        ("submit_review", lambda grant: adapter.submit_review(
            job=job, state="APPROVE", body="lgtm", grant=grant, record=record)),
        ("comment", lambda grant: adapter.comment(job=job, body="hi", grant=grant, record=record)),
        ("merge", lambda grant: adapter.merge(job=job, grant=grant, record=record)),
    ]


# -- T1: no Grant → AdapterError, zero GitHub calls, zero appends ----------------


def test_t1_every_write_with_grant_none_raises_before_any_call_or_append() -> None:
    job = make_job()
    transport = PoisonTransport()
    record = FakeRecord()
    mutations = FakeMutations()
    adapter = GithubAdapter(transport=transport, mutations=mutations, clock=lambda: FIXED_NOW)
    for name, call in _write_calls(adapter, job, record):
        try:
            call(None)
        except AdapterError:
            pass
        else:
            raise AssertionError(f"{name}: expected AdapterError for grant=None")
    assert record.entries == []
    assert mutations.puts == []


# -- T2: wrong activity, repo, or job id → AdapterError, zero calls/appends ------


def test_t2_wrong_activity_repo_or_job_raises_before_any_call_or_append() -> None:
    job = make_job()
    record = FakeRecord()
    mutations = FakeMutations()
    adapter = GithubAdapter(transport=PoisonTransport(), mutations=mutations, clock=lambda: FIXED_NOW)
    right = {
        "claim_lease": Activity.REVIEW,
        "release_lease": Activity.REVIEW,
        "submit_review": Activity.APPROVE,
        "comment": Activity.COMMENT,
        "merge": Activity.MERGE,
    }
    wrong_activity = {
        "claim_lease": Activity.MERGE,
        "release_lease": Activity.APPROVE,
        "submit_review": Activity.MERGE,   # MERGE is never accepted for APPROVE
        "comment": Activity.REVIEW,
        "merge": Activity.APPROVE,         # APPROVE never implies MERGE
    }
    for name, call in _write_calls(adapter, job, record):
        bad_grants = (
            make_grant(wrong_activity[name]),
            make_grant(right[name], repo="octo/other"),
            make_grant(right[name], job_id="job-2"),
        )
        for grant in bad_grants:
            try:
                call(grant)
            except AdapterError:
                pass
            else:
                raise AssertionError(f"{name}: expected AdapterError for {grant}")
    assert record.entries == []
    assert mutations.puts == []


# -- T3: an already-terminal mutation dedupes byte-identically -------------------


def test_t3_second_identical_submit_review_returns_terminal_without_calls() -> None:
    job = make_job()
    grant = make_grant(Activity.REQUEST_CHANGES)
    record = FakeRecord()
    mutations = FakeMutations()
    first_transport = FakeTransport(nodes=[node_payload()])
    adapter = GithubAdapter(transport=first_transport, mutations=mutations, clock=lambda: FIXED_NOW)
    first = adapter.submit_review(job=job, state="REQUEST_CHANGES", body="fix", grant=grant, record=record)
    assert isinstance(first, Mutation) and first.accepted
    assert len(record.entries) == 1
    assert mutations.rows[first.id].state == "completed"

    # Second call: identical (job, state, body); the transport would fail the
    # test on any GitHub call, and the record on any new `action` entry.
    poisoned = GithubAdapter(transport=PoisonTransport(), mutations=mutations, clock=lambda: FIXED_NOW)
    second = poisoned.submit_review(job=job, state="REQUEST_CHANGES", body="fix", grant=grant, record=record)
    assert second == first
    assert len(record.entries) == 1


def test_client_mutation_id_is_the_fixed_stable_hash_formula() -> None:
    """§3 preamble / §1: `stable_hash(job.id, kind.value, canonical_json(payload))`,
    with P-01's fixed definition `sha256("\\x1f".join(parts)).hexdigest()`. The
    formula and its determinism are asserted — both resolution paths are
    byte-identical, so this holds before and after `rqa.intake` lands."""
    job = make_job()
    grant = make_grant(Activity.COMMENT)
    record = FakeRecord()
    adapter = adapter_with(FakeTransport(nodes=[node_payload()]))
    result = adapter.comment(job=job, body="hello", grant=grant, record=record)
    assert isinstance(result, Mutation)
    payload = {"repo": job.repo, "number": job.number, "body": "hello"}
    assert result.id == expected_cmid(job, MutationKind.COMMENT, payload)
    assert writes._stable_hash("a", "b") == hashlib.sha256(b"a\x1fb").hexdigest()


# -- T7: APPROVE's fresh read sees a different head ------------------------------


def test_t7_approve_with_changed_head_is_stale_with_zero_mutations() -> None:
    job = make_job()
    grant = make_grant(Activity.APPROVE)
    record = FakeRecord()
    transport = FakeTransport(nodes=[node_payload(head="H2")])
    adapter = adapter_with(transport)
    result = adapter.submit_review(job=job, state="APPROVE", body="lgtm", grant=grant, record=record)
    assert result == Stale(reason="head_changed", observed_head_sha="H2")
    assert transport.mutate_calls == []
    assert [entry[2]["outcome"] for entry in record.entries] == ["stale"]
    assert record.entries[0][2]["response"] is None  # no mutation was ever sent


def test_approve_on_a_closed_pr_is_stale_pr_closed() -> None:
    job = make_job()
    grant = make_grant(Activity.APPROVE)
    transport = FakeTransport(nodes=[node_payload(state="CLOSED")])
    adapter = adapter_with(transport)
    result = adapter.submit_review(job=job, state="APPROVE", body="lgtm", grant=grant, record=FakeRecord())
    assert result == Stale(reason="pr_closed", observed_head_sha="H1")
    assert transport.mutate_calls == []


# -- T8: APPROVE's post-check is unreadable or lacks the matching review ---------


def test_t8_unreadable_post_check_returns_unavailable_not_an_ambiguous_result() -> None:
    job = make_job()
    grant = make_grant(Activity.APPROVE)
    transport = FakeTransport(
        nodes=[node_payload()],
        reviews_error=transport_module.Unavailable(reason="unreachable", retriable=True),
    )
    adapter = adapter_with(transport)
    result = adapter.submit_review(job=job, state="APPROVE", body="lgtm", grant=grant, record=FakeRecord())
    assert result == GithubUnavailable(op="submit_review", reason="incomplete", retriable=True)


def test_t8_post_check_without_a_matching_visible_review_is_unavailable() -> None:
    job = make_job()
    grant = make_grant(Activity.APPROVE)
    # A review is visible but for a different commit: not the matching one.
    transport = FakeTransport(
        nodes=[node_payload()],
        reviews=[{"state": "APPROVED", "user": {"login": "operator"}, "commit_id": "H0"}],
    )
    adapter = adapter_with(transport)
    result = adapter.submit_review(job=job, state="APPROVE", body="lgtm", grant=grant, record=FakeRecord())
    assert result == GithubUnavailable(op="submit_review", reason="incomplete", retriable=True)


def test_approve_with_matching_visible_review_is_verified_and_accepted() -> None:
    job = make_job()
    grant = make_grant(Activity.APPROVE)
    mutations = FakeMutations()
    transport = FakeTransport(
        nodes=[node_payload()],
        reviews=[{"state": "APPROVED", "user": {"login": "operator"}, "commit_id": "H1"}],
    )
    adapter = GithubAdapter(transport=transport, mutations=mutations, clock=lambda: FIXED_NOW)
    result = adapter.submit_review(job=job, state="APPROVE", body="lgtm", grant=grant, record=FakeRecord())
    assert isinstance(result, Mutation) and result.accepted
    assert mutations.rows[result.id].state == "verified"
    # U-DOCS-45: the submitted document carries the fixed literal event.
    assert "event:APPROVE" in transport.mutate_calls[0][0]


# -- T11: merge sees GitHub's expected-head mismatch -----------------------------


def test_t11_merge_head_mismatch_is_stale_with_no_separate_pre_check() -> None:
    job = make_job()
    grant = make_grant(Activity.MERGE)
    mismatch = transport_module.Unavailable(
        reason="graphql_error",
        retriable=False,
        errors=({"message": "Head branch was modified. Review and try the merge again."},),
    )
    transport = FakeTransport(nodes=[node_payload(head="H9")], mutate_error=mismatch)
    adapter = adapter_with(transport)
    result = adapter.merge(job=job, grant=grant, record=FakeRecord())
    assert result == Stale(reason="head_changed", observed_head_sha="H9")
    # No separate pre-check REST call: GitHub's expectedHeadOid decided.
    assert transport.rest_calls == []
    assert len(transport.mutate_calls) == 1
    assert transport.mutate_calls[0][1]["expectedHeadOid"] == "H1"


def test_merge_success_is_an_accepted_mutation_with_expected_head_oid() -> None:
    job = make_job()
    grant = make_grant(Activity.MERGE)
    transport = FakeTransport(nodes=[node_payload()], mutate={"pullRequest": {"merged": True}})
    adapter = adapter_with(transport)
    result = adapter.merge(job=job, grant=grant, record=FakeRecord())
    assert isinstance(result, Mutation) and result.accepted
    document, variables, _ = transport.mutate_calls[0]
    assert "mergePullRequest" in document
    assert "expectedHeadOid" in document
    assert variables == {"pullRequestId": "PR_1", "expectedHeadOid": "H1"}


# -- T12: claim_lease finds another login ----------------------------------------


def test_t12_claim_lease_with_another_assignee_is_lease_taken_zero_mutations() -> None:
    job = make_job()
    grant = make_grant(Activity.REVIEW)
    transport = FakeTransport(nodes=[node_payload(assignees=("alice",))])
    adapter = adapter_with(transport)
    result = adapter.claim_lease(job=job, grant=grant, record=FakeRecord())
    assert result == LeaseTaken(login="alice")
    assert transport.mutate_calls == []


def test_claim_lease_existing_operator_assignment_is_the_completed_no_op() -> None:
    job = make_job()
    grant = make_grant(Activity.REVIEW)
    record = FakeRecord()
    transport = FakeTransport(nodes=[node_payload(assignees=("operator",))])
    adapter = adapter_with(transport)
    result = adapter.claim_lease(job=job, grant=grant, record=record)
    assert isinstance(result, Mutation) and result.accepted
    assert transport.mutate_calls == []
    assert len(record.entries) == 1  # a no-op write is not a terminal-cache no-op


def test_claim_lease_reread_without_operator_is_incomplete_and_retriable() -> None:
    job = make_job()
    grant = make_grant(Activity.REVIEW)
    transport = FakeTransport(nodes=[node_payload(), node_payload()])  # re-read still empty
    adapter = adapter_with(transport)
    result = adapter.claim_lease(job=job, grant=grant, record=FakeRecord())
    assert result == GithubUnavailable(op="claim_lease", reason="incomplete", retriable=True)


def test_claim_lease_verified_by_the_mandatory_reread() -> None:
    job = make_job()
    grant = make_grant(Activity.REVIEW)
    mutations = FakeMutations()
    transport = FakeTransport(
        nodes=[node_payload(), node_payload(assignees=("operator",))]
    )
    adapter = GithubAdapter(transport=transport, mutations=mutations, clock=lambda: FIXED_NOW)
    result = adapter.claim_lease(job=job, grant=grant, record=FakeRecord())
    assert isinstance(result, Mutation) and result.accepted
    assert mutations.rows[result.id].state == "verified"
    assert len(transport.graphql_calls) == 2  # read + mandatory re-read


def test_release_lease_operator_absent_is_the_completed_success_no_op() -> None:
    job = make_job()
    grant = make_grant(Activity.REVIEW)
    transport = FakeTransport(nodes=[node_payload(assignees=("alice",))])
    adapter = adapter_with(transport)
    result = adapter.release_lease(job=job, grant=grant, record=FakeRecord())
    assert isinstance(result, Mutation) and result.accepted
    assert transport.mutate_calls == []


def test_release_lease_still_present_after_remove_is_unavailable() -> None:
    job = make_job()
    grant = make_grant(Activity.REVIEW)
    transport = FakeTransport(
        nodes=[node_payload(assignees=("operator",)), node_payload(assignees=("operator",))]
    )
    adapter = adapter_with(transport)
    result = adapter.release_lease(job=job, grant=grant, record=FakeRecord())
    assert result == GithubUnavailable(op="release_lease", reason="incomplete", retriable=True)


# -- §6: exactly one action entry; AppendFailed propagates -----------------------


def test_every_non_noop_write_appends_exactly_one_action_entry() -> None:
    job = make_job()
    grant = make_grant(Activity.COMMENT)
    record = FakeRecord()
    adapter = adapter_with(FakeTransport(nodes=[node_payload()]))
    result = adapter.comment(job=job, body="hello", grant=grant, record=record)
    assert isinstance(result, Mutation)
    assert len(record.entries) == 1
    job_id, kind, payload = record.entries[0]
    assert job_id == job.id and kind == "action"
    assert payload["kind"] == "comment" and payload["outcome"] == "submitted"
    assert payload["client_mutation_id"] == result.id
    assert payload["response"] == {"accepted": True}


def test_append_failed_propagates_and_the_mutation_row_stays_non_terminal() -> None:
    job = make_job()
    grant = make_grant(Activity.COMMENT)
    mutations = FakeMutations()
    adapter = GithubAdapter(
        transport=FakeTransport(nodes=[node_payload()]),
        mutations=mutations,
        clock=lambda: FIXED_NOW,
    )
    try:
        adapter.comment(job=job, body="hello", grant=grant, record=RaisingRecord())
    except AppendFailed:
        pass
    else:
        raise AssertionError("expected AppendFailed to propagate")
    # The write did not return a value and its row never turned terminal (§6).
    states = {row.state for row in mutations.puts}
    assert states == {"pending"}


def test_the_review_events_are_fixed_literals_never_interpolated() -> None:
    """U-DOCS-45's kept, load-bearing assertion: the event is inside the
    GraphQL text itself, so a caller cannot select a more-authoritative
    review event (RQA-NFR-032)."""
    assert "event:APPROVE" in writes._APPROVE_MUTATION
    assert "event:CHANGES_REQUESTED" in writes._REQUEST_CHANGES_MUTATION
    assert "event:COMMENT" in writes._COMMENT_MUTATION
    for document in (
        writes._APPROVE_MUTATION,
        writes._REQUEST_CHANGES_MUTATION,
        writes._COMMENT_MUTATION,
        writes._MERGE_MUTATION,
    ):
        assert "$event" not in document and "%(event)" not in document


def test_non_token_credential_is_never_sent_by_these_fakes() -> None:
    """The write paths resolve no credential of their own here: the fake
    transport takes none, and the sentinel exists only to be visibly not a
    token."""
    assert not NON_TOKEN_CREDENTIAL.startswith(("ghp_", "gho_", "ghu_", "github_pat_"))
