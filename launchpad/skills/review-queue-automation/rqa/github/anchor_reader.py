"""E-27's GitHub external-anchor reader.

Anchors are published as COMMENT pull-request reviews, rather than issue comments.
This reader deliberately asks GitHub for that exact review connection and authenticates
the repository, PR number, marker grammar, and expected publisher before producing
``AnchorEvidence``.  Recovery is evidence acquisition, not record reconstruction:
the review body is parsed into only an ``Anchor`` and the immutable review node id is
kept as its locator.  Record payloads never cross this boundary.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
import re

from rqa.contracts import Anchor, AnchorEvidence, AnchorRead, AnchorReadOutcome
from rqa.github import transport as transport_module
from rqa.github.anchor_publisher import ANCHOR_MARKER, anchor_body, review_locator

__all__ = ["GithubAnchorReader"]

_REVIEWS_PAGE_SIZE = 100
_REVIEWS_PAGE_CAP = 20
_REVIEWS_QUERY = (
    "query($owner:String!,$name:String!,$number:Int!,$cursor:String){"
    "repository(owner:$owner,name:$name){nameWithOwner"
    " pullRequest(number:$number){number reviews(first:100,after:$cursor){"
    "nodes{id body author{login} submittedAt} pageInfo{hasNextPage endCursor}}}}}"
)
_BODY_PATTERN = re.compile(
    rf"\A{re.escape(ANCHOR_MARKER)}\n"
    r"RQA record anchor\n\n"
    r"- job: `(?P<job>[^`\n]+)`\n"
    r"- seq: `(?P<seq>[1-9][0-9]*)`\n"
    r"- chain head: `(?P<hash>[0-9a-f]{64})`\n"
    r"- anchored at: `(?P<at>[^`\n]+)`\n\n"
    r"This attests that the review record for this job held (?P=seq) "
    r"entries ending in that hash\. Entries appended after it are not covered\.\Z"
)


@dataclass(frozen=True)
class _Candidate:
    evidence: AnchorEvidence
    submitted_at: datetime


def _parse_timestamp(value: object) -> datetime | None:
    """Parse one RFC 3339-ish timestamp, refusing naive values.

    GitHub uses ``Z`` for ``submittedAt``; the publisher's local anchor stamp uses
    ``+00:00``.  Both spellings are timezone-aware and therefore accepted.
    """
    if not isinstance(value, str) or not value or "T" not in value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _parse_body(body: object) -> Anchor | None:
    """Accept precisely ``anchor_body()``'s grammar, with an aware timestamp."""
    if not isinstance(body, str):
        return None
    matched = _BODY_PATTERN.fullmatch(body)
    if matched is None:
        return None
    anchor = Anchor(
        job=matched.group("job"),
        seq=int(matched.group("seq")),
        hash=matched.group("hash"),
        at=matched.group("at"),
    )
    if _parse_timestamp(anchor.at) is None:
        return None
    # Keep parser and publisher coupled: regex extracts the fields, while this catches
    # any future prose/whitespace drift rather than accepting a lookalike body.
    return anchor if anchor_body(anchor=anchor) == body else None


def _result(outcome: AnchorReadOutcome, detail: str, evidence: tuple[AnchorEvidence, ...] = ()) -> AnchorRead:
    return AnchorRead(outcome=outcome, evidence=evidence, detail=detail)


class GithubAnchorReader:
    """``AnchorSource`` over the exact PR-review output of ``GithubAnchorPublisher``."""

    def __init__(self, *, adapter):
        self._adapter = adapter

    def read(self, *, repo: str, number: int, job_id: str, publisher: str) -> AnchorRead:
        """Read every review page, then return the newest evidence at the highest seq.

        A malformed anchor by the accepted publisher is fail-closed: saying there is
        no external evidence in the face of a malformed one could bless a truncated
        local chain.  Lookalikes from other authors and valid anchors for other jobs
        are simply not evidence for this recovery request.
        """
        if "/" not in repo or not repo or isinstance(number, bool) or not isinstance(number, int) or number <= 0:
            return _result(AnchorReadOutcome.MALFORMED, "invalid repository or pull request")
        if not isinstance(job_id, str) or not job_id or not isinstance(publisher, str) or not publisher:
            return _result(AnchorReadOutcome.MALFORMED, "invalid job or publisher")
        owner, name = repo.split("/", 1)
        if not owner or not name or "/" in name:
            return _result(AnchorReadOutcome.MALFORMED, "invalid repository")

        cursor: str | None = None
        seen_cursors: set[str] = set()
        seen_review_ids: set[str] = set()
        candidates: list[_Candidate] = []

        for _ in range(_REVIEWS_PAGE_CAP):
            try:
                data = self._adapter.transport.graphql(
                    _REVIEWS_QUERY,
                    {"owner": owner, "name": name, "number": number, "cursor": cursor},
                    operation="anchor_read",
                )
            except transport_module.Unavailable as failure:
                outcome = (
                    AnchorReadOutcome.UNAUTHENTICATED
                    if failure.reason == "unauthenticated"
                    else AnchorReadOutcome.UNAVAILABLE
                )
                return _result(outcome, failure.reason)

            page = self._page(data=data, repo=repo, number=number)
            if page is None:
                return _result(AnchorReadOutcome.MALFORMED, "malformed or incomplete review pagination")
            nodes, has_next, end_cursor = page

            for node in nodes:
                parsed = self._candidate(
                    node=node,
                    repo=repo,
                    number=number,
                    job_id=job_id,
                    publisher=publisher,
                )
                if parsed == "malformed":
                    return _result(AnchorReadOutcome.MALFORMED, "malformed anchor from accepted publisher")
                if parsed is None:
                    continue
                if parsed.evidence.locator in seen_review_ids:
                    return _result(AnchorReadOutcome.MALFORMED, "duplicate review id in pagination")
                seen_review_ids.add(parsed.evidence.locator)
                candidates.append(parsed)

            if not has_next:
                return self._select(candidates)
            if end_cursor is None or end_cursor in seen_cursors:
                return _result(AnchorReadOutcome.MALFORMED, "incomplete review pagination")
            seen_cursors.add(end_cursor)
            cursor = end_cursor

        return _result(AnchorReadOutcome.MALFORMED, "review pagination exceeded its cap")

    @staticmethod
    def _page(*, data: object, repo: str, number: int) -> tuple[list, bool, str | None] | None:
        if not isinstance(data, Mapping):
            return None
        repository = data.get("repository")
        if not isinstance(repository, Mapping) or repository.get("nameWithOwner") != repo:
            return None
        pull_request = repository.get("pullRequest")
        if not isinstance(pull_request, Mapping) or pull_request.get("number") != number:
            return None
        reviews = pull_request.get("reviews")
        if not isinstance(reviews, Mapping):
            return None
        nodes = reviews.get("nodes")
        page_info = reviews.get("pageInfo")
        if not isinstance(nodes, list) or not isinstance(page_info, Mapping):
            return None
        has_next = page_info.get("hasNextPage")
        end_cursor = page_info.get("endCursor")
        if not isinstance(has_next, bool):
            return None
        if has_next and (not isinstance(end_cursor, str) or not end_cursor):
            return None
        if not has_next and end_cursor is not None and not isinstance(end_cursor, str):
            return None
        return nodes, has_next, end_cursor if isinstance(end_cursor, str) else None

    @staticmethod
    def _candidate(*, node: object, repo: str, number: int, job_id: str, publisher: str) -> _Candidate | str | None:
        if not isinstance(node, Mapping):
            return "malformed"
        review_id = node.get("id")
        body = node.get("body")
        author = node.get("author")
        author_login = author.get("login") if isinstance(author, Mapping) else None

        # A non-anchor review and an untrusted author's lookalike are not evidence.
        if not isinstance(body, str) or ANCHOR_MARKER not in body:
            return None
        if author_login != publisher:
            return None

        anchor = _parse_body(body)
        if anchor is None:
            return "malformed"
        if anchor.job != job_id:
            return None
        submitted_at = _parse_timestamp(node.get("submittedAt"))
        if not isinstance(review_id, str) or not review_id or submitted_at is None:
            return "malformed"
        return _Candidate(
            evidence=AnchorEvidence(
                anchor=anchor,
                repo=repo,
                number=number,
                publisher=publisher,
                locator=review_locator(review_id),
            ),
            submitted_at=submitted_at,
        )

    @staticmethod
    def _select(candidates: list[_Candidate]) -> AnchorRead:
        if not candidates:
            return _result(AnchorReadOutcome.NONE, "no trusted anchor found")
        by_seq: dict[int, list[_Candidate]] = {}
        for candidate in candidates:
            by_seq.setdefault(candidate.evidence.anchor.seq, []).append(candidate)
        for seq, same_seq in by_seq.items():
            if len({candidate.evidence.anchor.hash for candidate in same_seq}) > 1:
                evidence = tuple(candidate.evidence for candidate in same_seq)
                return _result(AnchorReadOutcome.CONFLICT, f"conflicting trusted anchors at seq {seq}", evidence)
        highest = max(by_seq)
        # Replay can create two reviews carrying one anchor.  Preserve only the most
        # recently submitted immutable review; locator breaks an otherwise exact tie.
        chosen = max(
            by_seq[highest],
            key=lambda candidate: (candidate.submitted_at, candidate.evidence.locator),
        )
        return _result(AnchorReadOutcome.FOUND, "trusted anchor found", (chosen.evidence,))
