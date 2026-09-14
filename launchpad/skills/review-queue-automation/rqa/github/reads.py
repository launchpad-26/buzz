"""E-01 `inventory`, E-14 `checks`, and one assembled E-23 `facts` —
`code/P-09-github-adapter.md` §3.1, §3.3, §3.5.

Reads append nothing: `inventory`, `checks` and `facts` have no record kind of
their own (§6). Every availability or shape failure is a `GithubUnavailable`
value, never a partial result (U-AUTHORITY-10, U-AUTHORITY-11: refuse rather
than truncate; a page-cap overrun and a malformed required field are refusals).

**Fail-closed protection reading (§3.1, §3.5 step 2, T13/T14).** The head
protection query targets the actual PR-head destination — including a fork —
by exact ref. A readable exact ref with a null `branchProtectionRule` is
definitively unprotected; a missing ref, GraphQL error, authorization,
rate-limit or transport failure, or malformed shape reads as protected. A
failed read never becomes writable, while a real unprotected branch stays
representable (RQA-NFR-021: P-10 refuses on these fields before constructing a
wrong, fork or protected destination).

**Attribution stays downstream (§7, U-VERDICT-06).** `checks()` returns the
same canonical vocabulary for a head read and a base read; comparing them by
name is P-07's, through E-14. Nothing here classifies a failure as the PR's or
the base's.
"""

from __future__ import annotations

import base64
import binascii
import urllib.parse
from collections.abc import Mapping
from datetime import datetime, timezone

from rqa.contracts import (
    UNSETTLED,
    CheckRun,
    Facts,
    GithubUnavailable,
    Job,
    PrFacts,
    RecordWriter,
    SubmittedReview,
)
from rqa.github import transport as transport_module
from rqa.github.conclusions import normalise_conclusion, normalise_status

__all__ = ["checks", "facts", "inventory"]

#: Open PRs per page and the page cap §3.1 fixes.
_INVENTORY_PAGE_SIZE = 50
_INVENTORY_PAGE_CAP = 5
#: Nested reads use a generous fixed cap; overrun is a refusal, not truncation.
_CONNECTION_PAGE_SIZE = 100
_CONNECTION_PAGE_CAP = 20

_PROTECTION_QUERY = (
    "query($owner:String!,$name:String!,$ref:String!){"
    "repository(owner:$owner,name:$name){"
    "ref(qualifiedName:$ref){branchProtectionRule{id}}}}"
)


class _Malformed(Exception):
    """Private: a required field is missing or has the wrong shape. Converted
    to `GithubUnavailable(reason="malformed", retriable=False)` at the edge."""


def _unavailable(op: str, failure: transport_module.Unavailable) -> GithubUnavailable:
    return GithubUnavailable(op=op, reason=failure.reason, retriable=failure.retriable)


def _malformed(op: str) -> GithubUnavailable:
    return GithubUnavailable(op=op, reason="malformed", retriable=False)


def _required(mapping: object, key: str) -> object:
    if not isinstance(mapping, Mapping) or mapping.get(key) is None:
        raise _Malformed(key)
    return mapping[key]


def _required_str(mapping: object, key: str) -> str:
    value = _required(mapping, key)
    if not isinstance(value, str):
        raise _Malformed(key)
    return value


def _required_int(mapping: object, key: str) -> int:
    value = _required(mapping, key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise _Malformed(key)
    return value


def _parse_utc(value: object) -> datetime:
    """One ISO-8601 UTC timestamp, GitHub's `Z` spelling included. Malformed
    or missing is a `_Malformed`, never a guessed time (§3.5 step 4)."""
    if not isinstance(value, str) or not value:
        raise _Malformed("timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise _Malformed("timestamp") from error
    if parsed.tzinfo is None:
        raise _Malformed("timestamp")
    return parsed.astimezone(timezone.utc)


def _head_protected(adapter, *, head_repo: str, head_ref: str, operation: str) -> bool:
    """§3.1/§3.5's fail-closed protection read, against the exact PR-head
    repository and ref (T13). Total: every unknown case is True (T14)."""
    if "/" not in head_repo:
        return True
    owner, name = head_repo.split("/", 1)
    try:
        data = adapter.transport.graphql(
            _PROTECTION_QUERY,
            {"owner": owner, "name": name, "ref": f"refs/heads/{head_ref}"},
            operation=operation,
        )
    except transport_module.Unavailable:
        return True
    repository = data.get("repository") if isinstance(data, Mapping) else None
    if not isinstance(repository, Mapping):
        return True
    ref = repository.get("ref")
    if not isinstance(ref, Mapping) or "branchProtectionRule" not in ref:
        return True
    return ref["branchProtectionRule"] is not None


def _merge_base_sha(adapter, *, repo: str, base_sha: str, head_sha: str, operation: str) -> str:
    compare = adapter.transport.rest_json(
        f"/repos/{repo}/compare/{base_sha}...{head_sha}", operation=operation
    )
    merge_base_commit = _required(compare, "merge_base_commit")
    return _required_str(merge_base_commit, "sha")


def _pr_facts(adapter, *, repo: str, pr: object, operation: str) -> PrFacts:
    """One PR listing/read into `PrFacts`, fail-closed on every required field
    (§3.1). A null `head.repo` (deleted fork) cannot identify the PR-head
    destination and is malformed; a null `body` is GitHub's spelling of an
    empty body and normalises to ""."""
    number = _required_int(pr, "number")
    head = _required(pr, "head")
    base = _required(pr, "base")
    head_sha = _required_str(head, "sha")
    base_sha = _required_str(base, "sha")
    head_repo = _required_str(_required(head, "repo"), "full_name")
    head_ref = _required_str(head, "ref")
    author = _required_str(_required(pr, "user"), "login")
    labels_field = pr.get("labels", []) if isinstance(pr, Mapping) else []
    if not isinstance(labels_field, list):
        raise _Malformed("labels")
    labels = frozenset(_required_str(label, "name") for label in labels_field)
    title = _required_str(pr, "title")
    body = pr.get("body") or ""
    if not isinstance(body, str):
        raise _Malformed("body")
    return PrFacts(
        repo=repo,
        number=number,
        head_sha=head_sha,
        base_sha=base_sha,
        merge_base_sha=_merge_base_sha(
            adapter, repo=repo, base_sha=base_sha, head_sha=head_sha, operation=operation
        ),
        head_repo=head_repo,
        head_ref=head_ref,
        head_protected=_head_protected(
            adapter, head_repo=head_repo, head_ref=head_ref, operation=operation
        ),
        author=author,
        labels=labels,
        title=title,
        body=body,
    )


def inventory(*, adapter, repo: str) -> tuple[PrFacts, ...] | GithubUnavailable:
    """E-01 — §3.1: open PRs, 50 per page, cap five; `()` when there are none.
    Null repository → `not_found`; transport/rate-limit/GraphQL error → the
    corresponding value; page-cap overrun or a malformed required field →
    a non-retriable refusal. Total branches."""
    try:
        pulls = adapter.transport.rest_paginated(
            f"/repos/{repo}/pulls?state=open&per_page={_INVENTORY_PAGE_SIZE}",
            operation="inventory",
            page_cap=_INVENTORY_PAGE_CAP,
        )
    except transport_module.Unavailable as failure:
        return _unavailable("inventory", failure)
    collected = []
    try:
        for pr in pulls:
            collected.append(_pr_facts(adapter, repo=repo, pr=pr, operation="inventory"))
    except transport_module.Unavailable as failure:
        return _unavailable("inventory", failure)
    except _Malformed:
        return _malformed("inventory")
    return tuple(collected)


def _check_runs(adapter, *, repo: str, sha: str, operation: str) -> list:
    return adapter.transport.rest_paginated(
        f"/repos/{repo}/commits/{sha}/check-runs?per_page={_CONNECTION_PAGE_SIZE}",
        operation=operation,
        page_cap=_CONNECTION_PAGE_CAP,
        item_key="check_runs",
    )


def _legacy_statuses(adapter, *, repo: str, sha: str, operation: str) -> list:
    return adapter.transport.rest_paginated(
        f"/repos/{repo}/commits/{sha}/statuses?per_page={_CONNECTION_PAGE_SIZE}",
        operation=operation,
        page_cap=_CONNECTION_PAGE_CAP,
    )


def _normalised_checks(adapter, *, repo: str, sha: str, operation: str) -> tuple[CheckRun, ...]:
    """§3.3's assembly: check-runs plus legacy statuses, every source value
    normalised to exactly one `CheckConclusion`, a check-run winning a
    same-name legacy collision. Raises to the caller on any failure."""
    runs = _check_runs(adapter, repo=repo, sha=sha, operation=operation)
    statuses = _legacy_statuses(adapter, repo=repo, sha=sha, operation=operation)

    legacy: dict[str, CheckRun] = {}
    for status in statuses:
        name = _required_str(status, "context")
        if name in legacy:  # /statuses is newest-first; the first row per context wins
            continue
        conclusion = normalise_status(status.get("state") if isinstance(status, Mapping) else None)
        if conclusion in UNSETTLED:
            observed_at = adapter.clock()
        else:
            observed_at = _parse_utc(status.get("updated_at"))
        legacy[name] = CheckRun(name=name, conclusion=conclusion, sha=sha, observed_at=observed_at)

    by_name: dict[str, CheckRun] = dict(legacy)
    for run in runs:
        name = _required_str(run, "name")
        conclusion = normalise_conclusion(run.get("conclusion") if isinstance(run, Mapping) else None)
        if conclusion in UNSETTLED:
            observed_at = adapter.clock()  # capture time; never corroborates or blocks
        else:
            observed_at = _parse_utc(run.get("completed_at"))  # GitHub's immutable completed_at
        by_name[name] = CheckRun(name=name, conclusion=conclusion, sha=sha, observed_at=observed_at)

    return tuple(by_name[name] for name in sorted(by_name))


def checks(*, adapter, repo: str, sha: str) -> tuple[CheckRun, ...] | GithubUnavailable:
    """E-14 — §3.3. Either unreadable source is a `GithubUnavailable`; no check from
    either source is `()`; otherwise the deduplicated tuple."""
    try:
        return _normalised_checks(adapter, repo=repo, sha=sha, operation="checks")
    except transport_module.Unavailable as failure:
        return _unavailable("checks", failure)
    except _Malformed:
        return _malformed("checks")


def _changed_paths(compare: object) -> tuple[frozenset[str], list]:
    files = _required(compare, "files")
    if not isinstance(files, list):
        raise _Malformed("files")
    paths = frozenset(_required_str(entry, "filename") for entry in files)
    if len(paths) != len(files):
        raise _Malformed("files")  # duplicate paths: count/path inconsistency
    return paths, files


def _blob(adapter, *, job: Job, path: str) -> bytes:
    """One changed file's content at the job's exact head. A vanished blob
    fails the whole capture (§3.5 step 1)."""
    quoted = urllib.parse.quote(path)
    try:
        payload = adapter.transport.rest_json(
            f"/repos/{job.repo}/contents/{quoted}?ref={job.head_sha}", operation="facts"
        )
    except transport_module.Unavailable as failure:
        if failure.reason == "not_found":
            raise _Malformed("vanished blob") from failure
        raise
    encoded = _required_str(payload, "content")
    try:
        return base64.b64decode(encoded, validate=False)
    except (binascii.Error, ValueError) as error:
        raise _Malformed("content") from error


def _submitted_reviews(adapter, *, job: Job) -> tuple[SubmittedReview, ...]:
    rows = adapter.transport.rest_paginated(
        f"/repos/{job.repo}/pulls/{job.number}/reviews?per_page={_CONNECTION_PAGE_SIZE}",
        operation="facts",
        page_cap=_CONNECTION_PAGE_CAP,
    )
    outcomes = {"APPROVED": "approved", "CHANGES_REQUESTED": "changes_requested"}
    collected = []
    for row in rows:
        state = row.get("state") if isinstance(row, Mapping) else None
        if state not in outcomes:
            continue
        collected.append(
            SubmittedReview(
                id=str(_required(row, "id")),
                actor=_required_str(_required(row, "user"), "login"),
                outcome=outcomes[state],
                head_sha=_required_str(row, "commit_id"),
                submitted_at=_parse_utc(row.get("submitted_at")),
            )
        )
    return tuple(collected)


def _assemble_facts(adapter, *, job: Job) -> Facts:
    pr = adapter.transport.rest_json(f"/repos/{job.repo}/pulls/{job.number}", operation="facts")

    # Job/PR identity (§3.5 step 1): the capture is for this job's exact revision.
    if _required_int(pr, "number") != job.number:
        raise _Malformed("number")
    head = _required(pr, "head")
    if _required_str(head, "sha") != job.head_sha:
        raise _Malformed("head_sha")
    base = _required(pr, "base")
    if _required_str(_required(base, "repo"), "full_name") != job.repo:
        raise _Malformed("base repo")

    pr_facts = _pr_facts(adapter, repo=job.repo, pr=pr, operation="facts")

    compare = adapter.transport.rest_json(
        f"/repos/{job.repo}/compare/{pr_facts.base_sha}...{job.head_sha}", operation="facts"
    )
    changed_paths, files = _changed_paths(compare)
    if _required_int(pr, "changed_files") != len(files):
        raise _Malformed("changed_files")  # compare count/path inconsistency

    # §3.5 step 3: the revision set is the exact predecessor→head compare;
    # without a predecessor it equals the PR-wide set. E-05 alone uses it.
    if job.predecessor_head_sha is not None:
        revision_compare = adapter.transport.rest_json(
            f"/repos/{job.repo}/compare/{job.predecessor_head_sha}...{job.head_sha}",
            operation="facts",
        )
        revision_changed_paths, _ = _changed_paths(revision_compare)
    else:
        revision_changed_paths = changed_paths

    diff = adapter.transport.rest_text(
        f"/repos/{job.repo}/pulls/{job.number}",
        operation="facts",
        accept=transport_module.ACCEPT_DIFF,
    )

    contents = {}
    for entry in files:
        if entry.get("status") == "removed":
            continue
        path = _required_str(entry, "filename")
        contents[path] = _blob(adapter, job=job, path=path)

    # §3.3: facts() calls the E-14 assembly internally exactly twice.
    head_checks = _normalised_checks(adapter, repo=job.repo, sha=job.head_sha, operation="facts")
    base_checks = _normalised_checks(
        adapter, repo=job.repo, sha=pr_facts.merge_base_sha, operation="facts"
    )

    reviews = _submitted_reviews(adapter, job=job)

    # §3.5 step 5: after all reads complete, set UTC fetched_at.
    fetched_at = adapter.clock()
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)

    return Facts(
        pr=pr_facts,
        diff=diff,
        changed_paths=changed_paths,
        revision_changed_paths=revision_changed_paths,
        files=contents,
        checks=head_checks,
        base_checks=base_checks,
        reviews=reviews,
        fetched_at=fetched_at.astimezone(timezone.utc),
    )


def facts(*, adapter, job: Job, record: RecordWriter) -> Facts | GithubUnavailable:
    """E-23 — §3.5: the only P-02-facing fact read, one coherent capture.
    Nothing partial is returned, and nothing is appended: reads have no record
    kind of their own (§6). `record` is E-23's signature; the append it exists
    for belongs to the write edges."""
    del record  # reads append nothing (§6)
    try:
        return _assemble_facts(adapter, job=job)
    except transport_module.Unavailable as failure:
        return _unavailable("facts", failure)
    except _Malformed:
        return _malformed("facts")
