#!/usr/bin/env python3
"""E-27's GitHub anchor reader: fixture-only, never a live GitHub call."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import Activity, Anchor, AnchorReadOutcome, Grant, Job, JobStatus  # noqa: E402
from rqa.github.anchor_publisher import GithubAnchorPublisher, anchor_body, review_locator  # noqa: E402
from rqa.github.anchor_reader import GithubAnchorReader  # noqa: E402
from rqa.github import transport as transport_module  # noqa: E402

REPO = "octo/repo"
NUMBER = 7
JOB = "job-1"
PUBLISHER = "rqa-bot"


class FakeTransport:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def graphql(self, document, variables, *, operation, credential=None):
        assert operation == "anchor_read"
        self.calls.append(dict(variables))
        page = self.pages.pop(0)
        if isinstance(page, Exception):
            raise page
        return page

    def mutate(self, *args, **kwargs):  # pragma: no cover - reader must remain read-only
        raise AssertionError("anchor reader attempted a GitHub mutation")


class Adapter:
    def __init__(self, pages):
        self.transport = FakeTransport(pages)


def anchor(*, seq=3, digest="a" * 64, at="2026-09-18T10:11:12.123456+00:00"):
    return Anchor(job=JOB, seq=seq, hash=digest, at=at)


def review(*, review_id="PRR_1", body=None, author=PUBLISHER, submitted_at="2026-09-18T10:12:00Z"):
    return {
        "id": review_id,
        "body": anchor_body(anchor=anchor()) if body is None else body,
        "author": {"login": author},
        "submittedAt": submitted_at,
    }


def page(nodes, *, has_next=False, end_cursor=None, repo=REPO, number=NUMBER):
    return {
        "repository": {
            "nameWithOwner": repo,
            "pullRequest": {
                "number": number,
                "reviews": {
                    "nodes": nodes,
                    "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
                },
            },
        }
    }


def read(pages):
    return GithubAnchorReader(adapter=Adapter(pages)).read(
        repo=REPO, number=NUMBER, job_id=JOB, publisher=PUBLISHER
    )


def test_reads_the_exact_published_body_into_immutable_evidence_only() -> None:
    result = read([page([review(review_id="PRR_exact")])])

    assert result.outcome is AnchorReadOutcome.FOUND
    assert result.evidence == (
        result.evidence[0],
    )
    evidence = result.evidence[0]
    assert evidence.anchor == anchor()
    assert evidence.repo == REPO and evidence.number == NUMBER
    assert evidence.publisher == PUBLISHER
    assert evidence.locator == review_locator("PRR_exact")
    assert set(vars(evidence.anchor)) == {"job", "seq", "hash", "at"}


def test_paginates_completely_then_chooses_newest_replay_at_highest_sequence() -> None:
    old = review(review_id="PRR_old", submitted_at="2026-09-18T09:00:00Z")
    replay = review(review_id="PRR_replay", submitted_at="2026-09-18T11:00:00+00:00")
    stale = review(
        review_id="PRR_stale",
        body=anchor_body(anchor=anchor(seq=2, digest="b" * 64)),
        submitted_at="2026-09-18T12:00:00Z",
    )
    adapter = Adapter([page([old, stale], has_next=True, end_cursor="cursor-1"), page([replay])])

    result = GithubAnchorReader(adapter=adapter).read(
        repo=REPO, number=NUMBER, job_id=JOB, publisher=PUBLISHER
    )

    assert result.outcome is AnchorReadOutcome.FOUND
    assert result.evidence[0].locator == review_locator("PRR_replay")
    assert result.evidence[0].anchor.seq == 3
    assert adapter.transport.calls == [
        {"owner": "octo", "name": "repo", "number": NUMBER, "cursor": None},
        {"owner": "octo", "name": "repo", "number": NUMBER, "cursor": "cursor-1"},
    ]


def test_same_sequence_with_distinct_hashes_is_conflict_never_timestamp_selection() -> None:
    first = review(review_id="PRR_one")
    second = review(
        review_id="PRR_two",
        body=anchor_body(anchor=anchor(digest="b" * 64)),
        submitted_at="2026-09-18T13:00:00Z",
    )

    result = read([page([first, second])])

    assert result.outcome is AnchorReadOutcome.CONFLICT
    assert {item.anchor.hash for item in result.evidence} == {"a" * 64, "b" * 64}


def test_wrong_author_or_job_and_non_anchor_reviews_are_not_evidence() -> None:
    foreign = review(review_id="PRR_foreign", author="untrusted")
    other_job = review(
        review_id="PRR_other",
        body=anchor_body(anchor=Anchor(job="other-job", seq=3, hash="a" * 64, at=anchor().at)),
    )
    prose = review(review_id="PRR_prose", body="ordinary review prose")

    result = read([page([foreign, other_job, prose])])

    assert result.outcome is AnchorReadOutcome.NONE
    assert result.evidence == ()


def test_malformed_accepted_anchor_and_naive_timestamps_are_rejected() -> None:
    malformed = review(body=anchor_body(anchor=anchor()).replace("- seq: `3`", "- seq: `0`"))
    result = read([page([malformed])])
    assert result.outcome is AnchorReadOutcome.MALFORMED

    naive = review(body=anchor_body(anchor=anchor(at="2026-09-18T10:11:12")))
    result = read([page([naive])])
    assert result.outcome is AnchorReadOutcome.MALFORMED

    untrusted_naive = review(author="untrusted", body=anchor_body(anchor=anchor(at="2026-09-18T10:11:12")))
    result = read([page([untrusted_naive])])
    assert result.outcome is AnchorReadOutcome.NONE


def test_malformed_or_repeated_pagination_is_not_silently_truncated() -> None:
    missing_cursor = read([page([], has_next=True, end_cursor=None)])
    assert missing_cursor.outcome is AnchorReadOutcome.MALFORMED

    repeated_cursor = read([
        page([], has_next=True, end_cursor="again"),
        page([], has_next=True, end_cursor="again"),
    ])
    assert repeated_cursor.outcome is AnchorReadOutcome.MALFORMED

    wrong_pr = read([page([], number=8)])
    assert wrong_pr.outcome is AnchorReadOutcome.MALFORMED


def test_transport_auth_and_availability_are_explicit_closed_outcomes() -> None:
    unauthenticated = read([
        transport_module.Unavailable(reason="unauthenticated", retriable=False),
    ])
    assert unauthenticated.outcome is AnchorReadOutcome.UNAUTHENTICATED

    unavailable = read([
        transport_module.Unavailable(reason="rate_limited", retriable=True),
    ])
    assert unavailable.outcome is AnchorReadOutcome.UNAVAILABLE


def test_review_timestamp_must_also_be_timezone_aware() -> None:
    result = read([page([review(submitted_at="2026-09-18T10:12:00")])])
    assert result.outcome is AnchorReadOutcome.MALFORMED


def test_reader_never_copies_a_review_body_into_evidence() -> None:
    body = anchor_body(anchor=anchor())
    result = read([page([review(body=body)])])
    rendered = repr(result.evidence[0])
    assert body not in rendered
    assert "RQA record anchor" not in rendered


def test_publisher_returns_the_same_immutable_review_locator_the_reader_preserves() -> None:
    job = Job(
        id=JOB,
        repo=REPO,
        number=NUMBER,
        head_sha="head",
        base_sha="base",
        head_repo=REPO,
        head_ref="branch",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snapshot",
        status=JobStatus.QUEUED,
    )
    grant = Grant(
        activity=Activity.COMMENT,
        repo=REPO,
        job_id=JOB,
        snapshot_hash="snapshot",
        capability_proof_id=1,
        categories=None,
        entry_seq=1,
    )

    class PublishingTransport:
        def graphql(self, *args, **kwargs):
            return {
                "viewer": {"login": PUBLISHER, "id": "U_1"},
                "repository": {
                    "pullRequest": {
                        "id": "PR_1", "state": "OPEN", "headRefOid": "head", "assignees": {"nodes": []}
                    }
                },
            }

        def mutate(self, *args, **kwargs):
            return {"addPullRequestReview": {"pullRequestReview": {"id": "PRR_published"}}}

    class PublishingAdapter:
        transport = PublishingTransport()

    locator = GithubAnchorPublisher(adapter=PublishingAdapter(), job=job, grant=grant).publish(
        anchor=anchor()
    )
    assert locator == review_locator("PRR_published")
