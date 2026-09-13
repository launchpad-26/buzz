#!/usr/bin/env python3
"""E-01 `inventory`, E-14 `checks`, E-23 `facts` — `code/P-09-github-adapter.md`
§3.1, §3.3, §3.5, §8 rows T13, T14, T15.

Every test runs against a duck-typed fake transport with fixture responses —
no network, no credential (§8's preamble).
"""

from __future__ import annotations

import base64
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import (  # noqa: E402
    CheckConclusion,
    Facts,
    GithubUnavailable,
    Job,
    JobStatus,
)
from rqa.github import GithubAdapter  # noqa: E402
from rqa.github import transport as transport_module  # noqa: E402

FIXED_NOW = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

RULE_NULL = {"repository": {"ref": {"branchProtectionRule": None}}}
RULE_PRESENT = {"repository": {"ref": {"branchProtectionRule": {"id": "BPR_1"}}}}
REF_MISSING = {"repository": {"ref": None}}
SHAPE_MALFORMED = {"repository": {}}


class FakeTransport:
    """Fixtures keyed by exact path; GraphQL serves the protection payload and
    logs every variables dict."""

    def __init__(self, *, json_by_path=None, pages_by_path=None, text_by_path=None,
                 protection=RULE_NULL, protection_error=None):
        self.json_by_path = dict(json_by_path or {})
        self.pages_by_path = dict(pages_by_path or {})
        self.text_by_path = dict(text_by_path or {})
        self.protection = protection
        self.protection_error = protection_error
        self.graphql_calls = []

    def rest_json(self, path, *, operation, credential=None):
        value = self.json_by_path[path]
        if isinstance(value, Exception):
            raise value
        return value

    def rest_paginated(self, path, *, operation, page_cap, item_key=None, credential=None):
        value = self.pages_by_path[path]
        if isinstance(value, Exception):
            raise value
        return list(value)

    def rest_text(self, path, *, operation, accept, credential=None):
        return self.text_by_path[path]

    def graphql(self, document, variables, *, operation, credential=None):
        self.graphql_calls.append(dict(variables))
        if self.protection_error is not None:
            raise self.protection_error
        return self.protection

    def mutate(self, *args, **kwargs):
        raise AssertionError("a read path attempted a mutation")


def adapter_with(transport) -> GithubAdapter:
    class _NoMutations:
        def find(self, cmid):
            raise AssertionError("a read path touched the mutations store")

        def put(self, row):
            raise AssertionError("a read path wrote the mutations store")

    return GithubAdapter(transport=transport, mutations=_NoMutations(), clock=lambda: FIXED_NOW)


def make_job(**over) -> Job:
    fields = dict(
        id="job-1",
        repo="octo/repo",
        number=7,
        head_sha="H1",
        base_sha="B1",
        head_repo="alice/fork",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.QUEUED,
    )
    fields.update(over)
    return Job(**fields)


def pr_payload(**over):
    payload = {
        "number": 7,
        "state": "open",
        "title": "Add feature",
        "body": "Adds the feature.",
        "user": {"login": "alice"},
        "labels": [{"name": "enhancement"}],
        "changed_files": 2,
        "head": {
            "sha": "H1",
            "ref": "feature",
            "repo": {"full_name": "alice/fork"},
        },
        "base": {"sha": "B1", "repo": {"full_name": "octo/repo"}},
    }
    payload.update(over)
    return payload


def compare_payload(*, merge_base="M1", files=("src/app.py", "docs/guide.md")):
    return {
        "merge_base_commit": {"sha": merge_base},
        "files": [{"filename": name, "status": "modified"} for name in files],
    }


def contents_payload(text: str):
    return {"content": base64.b64encode(text.encode()).decode(), "encoding": "base64"}


_PULLS_PATH = "/repos/octo/repo/pulls?state=open&per_page=50"


def inventory_fixture(*, protection=RULE_NULL, protection_error=None, pr=None):
    return FakeTransport(
        pages_by_path={_PULLS_PATH: [pr_payload() if pr is None else pr]},
        json_by_path={"/repos/octo/repo/compare/B1...H1": compare_payload()},
        protection=protection,
        protection_error=protection_error,
    )


def facts_fixture(*, job, protection=RULE_NULL, reviews=None, head_checks=None,
                  head_statuses=None, base_checks=None, pr=None, revision_files=("src/app.py",)):
    prp = pr_payload() if pr is None else pr
    json_by_path = {
        "/repos/octo/repo/pulls/7": prp,
        "/repos/octo/repo/compare/B1...H1": compare_payload(),
        "/repos/octo/repo/contents/src/app.py?ref=H1": contents_payload("print('app')\n"),
        "/repos/octo/repo/contents/docs/guide.md?ref=H1": contents_payload("# guide\n"),
    }
    if job.predecessor_head_sha is not None:
        json_by_path[f"/repos/octo/repo/compare/{job.predecessor_head_sha}...H1"] = (
            compare_payload(files=revision_files)
        )
    pages_by_path = {
        "/repos/octo/repo/commits/H1/check-runs?per_page=100": head_checks or [],
        "/repos/octo/repo/commits/H1/statuses?per_page=100": head_statuses or [],
        "/repos/octo/repo/commits/M1/check-runs?per_page=100": base_checks or [],
        "/repos/octo/repo/commits/M1/statuses?per_page=100": [],
        "/repos/octo/repo/pulls/7/reviews?per_page=100": reviews or [],
    }
    return FakeTransport(
        json_by_path=json_by_path,
        pages_by_path=pages_by_path,
        text_by_path={"/repos/octo/repo/pulls/7": "diff --git a/src/app.py b/src/app.py\n"},
        protection=protection,
    )


# -- inventory (§3.1) ------------------------------------------------------------


def test_inventory_returns_empty_tuple_when_there_are_no_open_prs() -> None:
    transport = FakeTransport(pages_by_path={_PULLS_PATH: []})
    assert adapter_with(transport).inventory(repo="octo/repo") == ()


def test_inventory_null_repository_is_not_found_and_not_retriable() -> None:
    transport = FakeTransport(
        pages_by_path={
            _PULLS_PATH: transport_module.Unavailable(
                reason="not_found", retriable=False, status=404
            )
        }
    )
    result = adapter_with(transport).inventory(repo="octo/repo")
    assert result == GithubUnavailable(op="inventory", reason="not_found", retriable=False)


def test_inventory_page_cap_overrun_is_a_non_retriable_refusal() -> None:
    transport = FakeTransport(
        pages_by_path={
            _PULLS_PATH: transport_module.Unavailable(reason="page_cap_exceeded", retriable=False)
        }
    )
    result = adapter_with(transport).inventory(repo="octo/repo")
    assert result == GithubUnavailable(op="inventory", reason="page_cap_exceeded", retriable=False)


def test_inventory_malformed_required_pr_field_is_malformed() -> None:
    # A deleted fork: head.repo is null, so the PR-head destination cannot be
    # identified (§3.1's malformed required field).
    broken = pr_payload()
    broken["head"] = {"sha": "H1", "ref": "feature", "repo": None}
    transport = inventory_fixture(pr=broken)
    result = adapter_with(transport).inventory(repo="octo/repo")
    assert result == GithubUnavailable(op="inventory", reason="malformed", retriable=False)


def test_inventory_captures_the_actual_head_destination_and_merge_base() -> None:
    transport = inventory_fixture()
    result = adapter_with(transport).inventory(repo="octo/repo")
    assert isinstance(result, tuple) and len(result) == 1
    facts = result[0]
    assert facts.repo == "octo/repo" and facts.number == 7
    assert facts.head_repo == "alice/fork" and facts.head_ref == "feature"
    assert facts.merge_base_sha == "M1"
    assert facts.labels == frozenset({"enhancement"})


# -- T13: the protection query targets the exact fork destination ----------------


def test_t13_fork_head_protection_query_targets_that_exact_repository_and_ref() -> None:
    transport = inventory_fixture(protection=RULE_NULL)
    result = adapter_with(transport).inventory(repo="octo/repo")
    assert isinstance(result, tuple)
    assert transport.graphql_calls == [
        {"owner": "alice", "name": "fork", "ref": "refs/heads/feature"}
    ]
    # The returned facts retain both fork values.
    assert result[0].head_repo == "alice/fork"
    assert result[0].head_ref == "feature"


# -- T14: readable null rule is False; every unknown case is True ----------------


def test_t14_readable_exact_ref_with_null_rule_is_definitively_unprotected() -> None:
    transport = inventory_fixture(protection=RULE_NULL)
    result = adapter_with(transport).inventory(repo="octo/repo")
    assert result[0].head_protected is False


def test_t14_every_unknown_case_reads_as_protected() -> None:
    unknown_cases = (
        dict(protection=RULE_PRESENT),  # a real rule: protected, not unknown
        dict(protection=REF_MISSING),
        dict(protection=SHAPE_MALFORMED),
        dict(protection_error=transport_module.Unavailable(reason="graphql_error", retriable=False)),
        dict(protection_error=transport_module.Unavailable(reason="rate_limited", retriable=True)),
        dict(protection_error=transport_module.Unavailable(reason="unreachable", retriable=True)),
        dict(protection_error=transport_module.Unavailable(reason="unauthenticated", retriable=False)),
    )
    for case in unknown_cases:
        transport = inventory_fixture(**case)
        result = adapter_with(transport).inventory(repo="octo/repo")
        assert isinstance(result, tuple), case
        assert result[0].head_protected is True, case


# -- checks (§3.3) ----------------------------------------------------------------


def _check_run(name, conclusion, completed_at="2026-09-12T10:00:00Z"):
    return {"name": name, "conclusion": conclusion, "completed_at": completed_at}


def test_checks_normalises_both_sources_and_check_run_wins_collisions() -> None:
    transport = FakeTransport(
        pages_by_path={
            "/repos/octo/repo/commits/H1/check-runs?per_page=100": [
                _check_run("ci", "success"),
                {"name": "build", "conclusion": None},  # unsettled: capture time
            ],
            "/repos/octo/repo/commits/H1/statuses?per_page=100": [
                {"context": "ci", "state": "failure", "updated_at": "2026-09-12T09:00:00Z"},
                {"context": "lint", "state": "error", "updated_at": "2026-09-12T09:00:00Z"},
            ],
        }
    )
    result = adapter_with(transport).checks(repo="octo/repo", sha="H1")
    assert isinstance(result, tuple)
    by_name = {check.name: check for check in result}
    assert set(by_name) == {"ci", "build", "lint"}
    # The check-run wins the same-name legacy collision.
    assert by_name["ci"].conclusion is CheckConclusion.SUCCESS
    assert by_name["build"].conclusion is CheckConclusion.PENDING
    assert by_name["build"].observed_at == FIXED_NOW
    assert by_name["lint"].conclusion is CheckConclusion.ACTION_REQUIRED
    assert by_name["ci"].observed_at == datetime(2026, 9, 12, 10, 0, tzinfo=timezone.utc)
    assert all(check.sha == "H1" for check in result)


def test_checks_with_no_checks_from_either_source_is_empty() -> None:
    transport = FakeTransport(
        pages_by_path={
            "/repos/octo/repo/commits/H1/check-runs?per_page=100": [],
            "/repos/octo/repo/commits/H1/statuses?per_page=100": [],
        }
    )
    assert adapter_with(transport).checks(repo="octo/repo", sha="H1") == ()


def test_checks_unreadable_source_is_unavailable() -> None:
    transport = FakeTransport(
        pages_by_path={
            "/repos/octo/repo/commits/H1/check-runs?per_page=100": [],
            "/repos/octo/repo/commits/H1/statuses?per_page=100": transport_module.Unavailable(
                reason="unreachable", retriable=True
            ),
        }
    )
    result = adapter_with(transport).checks(repo="octo/repo", sha="H1")
    assert result == GithubUnavailable(op="checks", reason="unreachable", retriable=True)


# -- T15 / facts (§3.5) ------------------------------------------------------------


def test_t15_successor_capture_carries_both_path_sets_and_every_fact() -> None:
    job = make_job(predecessor_job="job-0", predecessor_head_sha="A1")
    transport = facts_fixture(
        job=job,
        reviews=[
            {
                "id": 55,
                "state": "APPROVED",
                "user": {"login": "carol"},
                "commit_id": "A1",
                "submitted_at": "2026-09-11T08:30:00Z",
            },
            {"id": 56, "state": "COMMENTED", "user": {"login": "dave"}, "commit_id": "H1"},
        ],
        head_checks=[_check_run("ci", "success")],
        base_checks=[_check_run("ci", "failure", "2026-09-10T10:00:00Z")],
        revision_files=("src/app.py",),
    )
    result = adapter_with(transport).facts(job=job, record=None)
    assert isinstance(result, Facts)
    # PR-wide and A→B revision path sets are both present and distinct (E-05
    # alone uses the revision set).
    assert result.changed_paths == frozenset({"src/app.py", "docs/guide.md"})
    assert result.revision_changed_paths == frozenset({"src/app.py"})
    # Check observation times: head at GitHub's immutable completed_at.
    assert result.checks[0].observed_at == datetime(2026, 9, 12, 10, 0, tzinfo=timezone.utc)
    assert result.base_checks[0].conclusion is CheckConclusion.FAILURE
    # Submitted reviews carry id, actor, reviewed commit and immutable time.
    assert len(result.reviews) == 1
    review = result.reviews[0]
    assert (review.id, review.actor, review.outcome, review.head_sha) == (
        "55", "carol", "approved", "A1"
    )
    assert review.submitted_at == datetime(2026, 9, 11, 8, 30, tzinfo=timezone.utc)
    # Files, labels, diff, and the UTC capture time.
    assert result.files["src/app.py"] == b"print('app')\n"
    assert result.pr.labels == frozenset({"enhancement"})
    assert result.diff.startswith("diff --git")
    assert result.fetched_at == FIXED_NOW and result.fetched_at.tzinfo is not None
    assert result.pr.merge_base_sha == "M1"


def test_t15_without_a_predecessor_the_revision_set_equals_the_pr_wide_set() -> None:
    job = make_job()
    transport = facts_fixture(job=job)
    result = adapter_with(transport).facts(job=job, record=None)
    assert isinstance(result, Facts)
    assert result.revision_changed_paths == result.changed_paths


def test_t15_malformed_review_timestamp_fails_the_whole_capture() -> None:
    job = make_job()
    transport = facts_fixture(
        job=job,
        reviews=[{
            "id": 55, "state": "APPROVED", "user": {"login": "carol"},
            "commit_id": "H1", "submitted_at": "not-a-time",
        }],
    )
    result = adapter_with(transport).facts(job=job, record=None)
    assert result == GithubUnavailable(op="facts", reason="malformed", retriable=False)


def test_t15_compare_count_inconsistency_fails_atomically() -> None:
    job = make_job()
    transport = facts_fixture(job=job, pr=pr_payload(changed_files=5))
    result = adapter_with(transport).facts(job=job, record=None)
    assert result == GithubUnavailable(op="facts", reason="malformed", retriable=False)


def test_facts_identity_mismatch_returns_unavailable_not_partial_facts() -> None:
    job = make_job(head_sha="H2")  # the PR fixture's head is H1
    transport = facts_fixture(job=make_job())
    result = adapter_with(transport).facts(job=job, record=None)
    assert result == GithubUnavailable(op="facts", reason="malformed", retriable=False)


def test_facts_vanished_blob_fails_the_whole_capture() -> None:
    job = make_job()
    transport = facts_fixture(job=job)
    transport.json_by_path["/repos/octo/repo/contents/src/app.py?ref=H1"] = (
        transport_module.Unavailable(reason="not_found", retriable=False, status=404)
    )
    result = adapter_with(transport).facts(job=job, record=None)
    assert result == GithubUnavailable(op="facts", reason="malformed", retriable=False)


def test_facts_transport_failure_returns_the_matching_unavailable() -> None:
    job = make_job()
    transport = facts_fixture(job=job)
    transport.json_by_path["/repos/octo/repo/pulls/7"] = transport_module.Unavailable(
        reason="rate_limited", retriable=True, status=429
    )
    result = adapter_with(transport).facts(job=job, record=None)
    assert result == GithubUnavailable(op="facts", reason="rate_limited", retriable=True)
