"""P-09-private result/implementation types — `code/P-09-github-adapter.md` §2.

`PrFacts`, `Facts`, `CheckRun`, `Mutation`, `Stale`, `LeaseTaken`,
`GithubUnavailable` and `CapabilityReading` are boundary values defined only in
`CONTRACTS.md` §4 and imported unchanged; `Grant`, `Activity`, `Job`,
`RecordWriter` and `Entry` only in §§1, 7 and 8 (§4 here). This module declares
what is genuinely P-09's: the mutation discriminator, the programming error,
and the one neighbour-facing object, `GithubAdapter`.

`GithubAdapter` is how a neighbour holds this adapter: P-01 receives one for
E-01 (`github.inventory(repo=...)`, `github.claim_lease(job=..., grant=...,
record=...)`), P-02 for E-12/E-23, P-08 for E-16. Every public method has
exactly its `CONTRACTS.md` §9 signature after `self` — keyword-only, same
names, same annotations, same return union — and there is no second shape for
an E-NN anywhere in this package (§3). The bodies live in `reads.py`,
`writes.py` and `capability.py`; the method-level imports below are what keeps
this module importable before those (they import this one for the types).

`AdapterError` is raised before any GitHub call or record append, every time
(§3 preamble, §7, T1/T2): a write without its matching `Grant` for that exact
activity, repository and job is a programming error, never a partial write.
There is no default-allow path.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from rqa.contracts import (
    CapabilityReading,
    CheckRun,
    Facts,
    GithubUnavailable,
    Grant,
    Job,
    LeaseTaken,
    Mutation,
    PrFacts,
    RecordWriter,
    Stale,
)
from rqa.github.store import MutationStore

__all__ = ["AdapterError", "GithubAdapter", "MutationKind"]


class MutationKind(str, Enum):
    ASSIGNEE_ADD = "assignee_add"
    ASSIGNEE_REMOVE = "assignee_remove"
    COMMENT = "comment"
    REVIEW_SUBMIT = "review_submit"
    MERGE = "merge"


class AdapterError(Exception):
    """Programming error: a handle is bound to the wrong job, or a write lacks its matching Grant."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class GithubAdapter:
    """Every byte RQA sends to or reads from GitHub crosses this one adapter
    and no other (§ responsibility). `transport` owns the HTTP seam, the ETag
    cache and `api_calls`; `mutations` is the §5 dedupe boundary; `clock`
    supplies capture time (UTC) and is injectable for tests."""

    transport: object
    mutations: MutationStore
    clock: Callable[[], datetime] = field(default=_utcnow)

    # -- E-01 -------------------------------------------------------------------

    def inventory(self, *, repo: str) -> tuple[PrFacts, ...] | GithubUnavailable:
        from rqa.github import reads

        return reads.inventory(adapter=self, repo=repo)

    def claim_lease(self, *, job: Job, grant: Grant, record: RecordWriter) -> Mutation | LeaseTaken | GithubUnavailable:
        from rqa.github import writes

        return writes.claim_lease(adapter=self, job=job, grant=grant, record=record)

    def release_lease(self, *, job: Job, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable:
        from rqa.github import writes

        return writes.release_lease(adapter=self, job=job, grant=grant, record=record)

    # -- E-12 -------------------------------------------------------------------

    def submit_review(self, *, job: Job, state: Literal["APPROVE", "REQUEST_CHANGES"], body: str, grant: Grant,
                      record: RecordWriter) -> Mutation | Stale | GithubUnavailable:
        from rqa.github import writes

        return writes.submit_review(
            adapter=self, job=job, state=state, body=body, grant=grant, record=record
        )

    def comment(self, *, job: Job, body: str, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable:
        from rqa.github import writes

        return writes.comment(adapter=self, job=job, body=body, grant=grant, record=record)

    def merge(self, *, job: Job, grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable:
        from rqa.github import writes

        return writes.merge(adapter=self, job=job, grant=grant, record=record)

    # -- E-14 -------------------------------------------------------------------

    def checks(self, *, repo: str, sha: str) -> tuple[CheckRun, ...] | GithubUnavailable:
        from rqa.github import reads

        return reads.checks(adapter=self, repo=repo, sha=sha)

    # -- E-16 -------------------------------------------------------------------

    def probe(self, *, repo: str, credential: str) -> CapabilityReading | GithubUnavailable:
        from rqa.github import capability

        return capability.probe(adapter=self, repo=repo, credential=credential)

    # -- E-23 -------------------------------------------------------------------

    def facts(self, *, job: Job, record: RecordWriter) -> Facts | GithubUnavailable:
        from rqa.github import reads

        return reads.facts(adapter=self, job=job, record=record)
