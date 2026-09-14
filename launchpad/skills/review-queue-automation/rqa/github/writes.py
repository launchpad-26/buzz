"""E-01 `claim_lease`/`release_lease`, E-12 `submit_review`/`comment`/`merge` —
`code/P-09-github-adapter.md` §3 preamble, §3.1, §3.2, §6.

**Shared write discipline (U-AUTHORITY-09).** Every write first calls
`_require_grant(grant, activity, job)` and raises `AdapterError` before any
GitHub call or record append when the grant is missing or bound to a different
activity, repository or job (T1/T2). It then derives
`client_mutation_id = stable_hash(job.id, kind.value, canonical_json(payload))`,
returns an existing terminal mutation without an HTTP call or append (T3), or
performs the fixed mutation and appends exactly one `action` entry through its
supplied `record`. `AppendFailed` propagates: a write whose `action` entry
could not be written does not return a value (§6).

**Fixed events (U-AUTHORITY-09's retained registry, U-DOCS-45,
RQA-NFR-032).** The GraphQL documents below are module literals with their
review event spelled inside the text — `event:APPROVE`,
`event:CHANGES_REQUESTED`, `event:COMMENT` — never an interpolated event, so a
caller provably cannot select a more-authoritative review event.

**No escalation, ever (§7, launchpad/AGENTS.md §5, ADR-0052).** There is no
force-push, no admin override, no protection-rule edit and no merge method
that skips required checks: `merge` sends `mergePullRequest` with
`expectedHeadOid=job.head_sha` and reports GitHub's refusal as a value. A call
that would need elevated permission fails and reports; it does not escalate.

**`stable_hash` is P-01's (U-RESILIENCE-13).** `rqa.intake.identity` owns
job/mutation identity and is not yet landed; `_stable_hash` resolves it at
call time, never at import, exactly the way `rqa.policy.validate` resolves
P-10's `MECHANICAL_TOOL_SET`. The fallback is the definition §1 records P-01
as having already fixed — `sha256("\\x1f".join(parts).encode()).hexdigest()` —
so both paths produce byte-identical digests and no `client_mutation_id`
changes when P-01 lands. `canonical_json` here is this package's private
rendering by the formula P-12 §5 fixes; `rqa.record`'s public surface is
closed and is imported only to append (§1).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import timezone
from typing import Literal

from rqa.contracts import (
    Activity,
    GithubUnavailable,
    Grant,
    Job,
    LeaseTaken,
    Mutation,
    RecordWriter,
    Stale,
)
from rqa.github import transport as transport_module
from rqa.github.store import TERMINAL_STATES, MutationRow, response_text
from rqa.github.types import AdapterError, MutationKind

__all__ = ["claim_lease", "comment", "merge", "release_lease", "submit_review"]

# -- the fixed mutation documents (U-DOCS-45: the event lives in the literal) --

_APPROVE_MUTATION = (
    "mutation($pullRequestId:ID!,$body:String!){"
    "addPullRequestReview(input:{pullRequestId:$pullRequestId,body:$body,event:APPROVE}){"
    "pullRequestReview{id state}}}"
)
_REQUEST_CHANGES_MUTATION = (
    "mutation($pullRequestId:ID!,$body:String!){"
    "addPullRequestReview(input:{pullRequestId:$pullRequestId,body:$body,event:CHANGES_REQUESTED}){"
    "pullRequestReview{id state}}}"
)
_COMMENT_MUTATION = (
    "mutation($pullRequestId:ID!,$body:String!){"
    "addPullRequestReview(input:{pullRequestId:$pullRequestId,body:$body,event:COMMENT}){"
    "pullRequestReview{id state}}}"
)
_MERGE_MUTATION = (
    "mutation($pullRequestId:ID!,$expectedHeadOid:GitObjectID!){"
    "mergePullRequest(input:{pullRequestId:$pullRequestId,expectedHeadOid:$expectedHeadOid}){"
    "pullRequest{merged}}}"
)
_ADD_ASSIGNEE_MUTATION = (
    "mutation($assignableId:ID!,$assigneeIds:[ID!]!){"
    "addAssigneesToAssignable(input:{assignableId:$assignableId,assigneeIds:$assigneeIds}){"
    "assignable{... on PullRequest{id}}}}"
)
_REMOVE_ASSIGNEE_MUTATION = (
    "mutation($assignableId:ID!,$assigneeIds:[ID!]!){"
    "removeAssigneesFromAssignable(input:{assignableId:$assignableId,assigneeIds:$assigneeIds}){"
    "assignable{... on PullRequest{id}}}}"
)

#: One addressing read per write: the PR node id, its live state and head, the
#: viewer, and the current assignees. An observation, never a caller-visible
#: second fact edge.
_PR_NODE_QUERY = (
    "query($owner:String!,$name:String!,$number:Int!){"
    "viewer{login id}"
    "repository(owner:$owner,name:$name){"
    "pullRequest(number:$number){id state headRefOid"
    " assignees(first:20){nodes{login id}}}}}"
)

_REVIEWS_PAGE_SIZE = 100
_REVIEWS_PAGE_CAP = 20


def _require_grant(grant: Grant | None, activity: Activity, job: Job) -> None:
    """The shared discipline's gate (§3 preamble): checked, never inferred.
    `MERGE` is never implied by `APPROVE`; the six activities are independent,
    and a `Grant` for a different repo or job never passes."""
    if grant is None:
        raise AdapterError("write refused: no Grant supplied")
    if grant.activity is not activity:
        raise AdapterError(
            f"write refused: Grant is for activity {grant.activity.value!r},"
            f" this write needs {activity.value!r}"
        )
    if grant.repo != job.repo:
        raise AdapterError("write refused: Grant is for a different repository")
    if grant.job_id != job.id:
        raise AdapterError("write refused: Grant is for a different job")


def _canonical_json(payload: Mapping) -> str:
    """This package's private canonical rendering, by the formula P-12 §5
    fixes. Deliberately not imported from `rqa.record`: its public surface is
    closed (§1 permits importing it only to append)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_hash(*parts: str) -> str:
    """P-01's deterministic hash (U-RESILIENCE-13), resolved at call time —
    never at import — with §1's fixed definition as the fallback while
    `rqa.intake` has not landed. Both paths are byte-identical."""
    try:
        from rqa.intake.identity import stable_hash
    except ImportError:
        return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()
    return stable_hash(*parts)


def _client_mutation_id(*, job: Job, kind: MutationKind, payload: Mapping) -> str:
    return _stable_hash(job.id, kind.value, _canonical_json(payload))


@dataclass(frozen=True)
class _Outcome:
    """What one perform step concluded: the §6 `outcome` word, the value the
    edge returns, the `mutations.state` to persist, and GitHub's payload
    (None when no mutation was ever sent)."""

    outcome: str
    value: Mutation | Stale | LeaseTaken | GithubUnavailable
    state: str
    response: Mapping | None


@dataclass(frozen=True)
class _PrNode:
    viewer_login: str
    viewer_id: str
    pr_id: str
    state: str
    head_ref_oid: str
    assignees: tuple[tuple[str, str], ...]  # (login, node id)


def _read_pr_node(adapter, *, job: Job, operation: str) -> _PrNode:
    owner, name = job.repo.split("/", 1)
    data = adapter.transport.graphql(
        _PR_NODE_QUERY,
        {"owner": owner, "name": name, "number": job.number},
        operation=operation,
    )
    viewer = data.get("viewer") if isinstance(data, Mapping) else None
    repository = data.get("repository") if isinstance(data, Mapping) else None
    pull = repository.get("pullRequest") if isinstance(repository, Mapping) else None
    if not isinstance(viewer, Mapping) or not isinstance(pull, Mapping):
        raise transport_module.Unavailable(
            reason="malformed", retriable=False, detail=f"{operation}: node read shape"
        )
    assignees_field = pull.get("assignees")
    nodes = assignees_field.get("nodes", []) if isinstance(assignees_field, Mapping) else []
    assignees = []
    for node in nodes or []:
        if isinstance(node, Mapping) and node.get("login") and node.get("id"):
            assignees.append((str(node["login"]), str(node["id"])))
    for field_name in ("login", "id"):
        if not viewer.get(field_name):
            raise transport_module.Unavailable(
                reason="malformed", retriable=False, detail=f"{operation}: viewer shape"
            )
    for field_name in ("id", "state", "headRefOid"):
        if not pull.get(field_name):
            raise transport_module.Unavailable(
                reason="malformed", retriable=False, detail=f"{operation}: pull shape"
            )
    return _PrNode(
        viewer_login=str(viewer["login"]),
        viewer_id=str(viewer["id"]),
        pr_id=str(pull["id"]),
        state=str(pull["state"]),
        head_ref_oid=str(pull["headRefOid"]),
        assignees=tuple(assignees),
    )


def _unavailable(op: str, failure: transport_module.Unavailable) -> GithubUnavailable:
    return GithubUnavailable(op=op, reason=failure.reason, retriable=failure.retriable)


def _now_text(adapter) -> str:
    return adapter.clock().astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _mark_pending(adapter, *, cmid: str, job: Job, kind: MutationKind, created_at: str | None) -> None:
    now = _now_text(adapter)
    adapter.mutations.put(
        MutationRow(
            client_mutation_id=cmid,
            job_id=job.id,
            kind=kind.value,
            state="pending",
            response=None,
            created_at=created_at or now,
            updated_at=now,
        )
    )


def _dispatch(
    adapter,
    *,
    job: Job,
    grant: Grant,
    activity: Activity,
    kind: MutationKind,
    payload: Mapping,
    record: RecordWriter,
    perform: Callable[[str], _Outcome],
):
    """§3's preamble, in order: grant check, deterministic id, terminal-cache
    no-op, perform, exactly one `action` entry, then the final `mutations` row.
    The append happens before the row turns terminal, so a terminal row always
    has its `action` entry even when `AppendFailed` propagates."""
    _require_grant(grant, activity, job)
    cmid = _client_mutation_id(job=job, kind=kind, payload=payload)
    row = adapter.mutations.find(cmid)
    if row is not None and row.state in TERMINAL_STATES:
        # T3: byte-identical to the first accepted Mutation; zero GitHub
        # calls, zero new `action` entries (§6's deduplicated no-op).
        return Mutation(id=cmid, kind=row.kind, accepted=True)
    result = perform(cmid)
    record.append(
        job.id,
        "action",
        {
            "client_mutation_id": cmid,
            "kind": kind.value,
            "outcome": result.outcome,
            "response": dict(result.response) if result.response is not None else None,
        },
    )
    now = _now_text(adapter)
    adapter.mutations.put(
        MutationRow(
            client_mutation_id=cmid,
            job_id=job.id,
            kind=kind.value,
            state=result.state,
            response=response_text(
                dict(result.response) if result.response is not None else None
            ),
            created_at=row.created_at if row is not None else now,
            updated_at=now,
        )
    )
    return result.value


# -- E-01 lease writes (§3.1) — both require Activity.REVIEW -------------------


def claim_lease(*, adapter, job: Job, grant: Grant, record: RecordWriter) -> Mutation | LeaseTaken | GithubUnavailable:
    kind = MutationKind.ASSIGNEE_ADD
    payload = {"repo": job.repo, "number": job.number}

    def perform(cmid: str) -> _Outcome:
        try:
            node = _read_pr_node(adapter, job=job, operation="claim_lease")
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("claim_lease", failure), "uncertain", None)
        other = next(
            (login for login, _ in node.assignees if login != node.viewer_login), None
        )
        if other is not None:
            return _Outcome("lease_taken", LeaseTaken(login=other), "uncertain", None)
        if any(login == node.viewer_login for login, _ in node.assignees):
            # Existing operator assignment: the completed no-op Mutation.
            return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "completed", None)
        _mark_pending(adapter, cmid=cmid, job=job, kind=kind, created_at=None)
        try:
            data = adapter.transport.mutate(
                _ADD_ASSIGNEE_MUTATION,
                {"assignableId": node.pr_id, "assigneeIds": [node.viewer_id]},
                operation="claim_lease",
            )
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("claim_lease", failure), "uncertain", None)
        # §3.1: the mandatory re-read. Accepted only when the operator is present.
        try:
            confirmed = _read_pr_node(adapter, job=job, operation="claim_lease")
        except transport_module.Unavailable:
            confirmed = None
        if confirmed is not None and any(
            login == node.viewer_login for login, _ in confirmed.assignees
        ):
            return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "verified", data)
        return _Outcome(
            "unavailable",
            GithubUnavailable(op="claim_lease", reason="incomplete", retriable=True),
            "pending",
            data,
        )

    return _dispatch(
        adapter,
        job=job,
        grant=grant,
        activity=Activity.REVIEW,
        kind=kind,
        payload=payload,
        record=record,
        perform=perform,
    )


def release_lease(*, adapter, job: Job, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable:
    kind = MutationKind.ASSIGNEE_REMOVE
    payload = {"repo": job.repo, "number": job.number}

    def perform(cmid: str) -> _Outcome:
        try:
            node = _read_pr_node(adapter, job=job, operation="release_lease")
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("release_lease", failure), "uncertain", None)
        operator_ids = [node_id for login, node_id in node.assignees if login == node.viewer_login]
        if not operator_ids:
            # §3.1: operator absent is the completed no-op/success condition.
            return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "completed", None)
        _mark_pending(adapter, cmid=cmid, job=job, kind=kind, created_at=None)
        try:
            data = adapter.transport.mutate(
                _REMOVE_ASSIGNEE_MUTATION,
                {"assignableId": node.pr_id, "assigneeIds": operator_ids},
                operation="release_lease",
            )
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("release_lease", failure), "uncertain", None)
        try:
            confirmed = _read_pr_node(adapter, job=job, operation="release_lease")
        except transport_module.Unavailable:
            confirmed = None
        if confirmed is not None and not any(
            login == node.viewer_login for login, _ in confirmed.assignees
        ):
            return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "verified", data)
        return _Outcome(
            "unavailable",
            GithubUnavailable(op="release_lease", reason="incomplete", retriable=True),
            "pending",
            data,
        )

    return _dispatch(
        adapter,
        job=job,
        grant=grant,
        activity=Activity.REVIEW,
        kind=kind,
        payload=payload,
        record=record,
        perform=perform,
    )


# -- E-12 review, comment and merge writes (§3.2) ------------------------------


def _visible_matching_approval(adapter, *, job: Job, viewer_login: str) -> bool | None:
    """APPROVE's mandatory post-check: a visible APPROVED review by the viewer
    at the job's exact head. None when the read itself failed."""
    try:
        rows = adapter.transport.rest_paginated(
            f"/repos/{job.repo}/pulls/{job.number}/reviews?per_page={_REVIEWS_PAGE_SIZE}",
            operation="submit_review",
            page_cap=_REVIEWS_PAGE_CAP,
        )
    except transport_module.Unavailable:
        return None
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        user = row.get("user")
        login = user.get("login") if isinstance(user, Mapping) else None
        if (
            row.get("state") == "APPROVED"
            and login == viewer_login
            and row.get("commit_id") == job.head_sha
        ):
            return True
    return False


def submit_review(*, adapter, job: Job, state: Literal["APPROVE", "REQUEST_CHANGES"], body: str,
                  grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable:
    if state == "APPROVE":
        activity = Activity.APPROVE
        document = _APPROVE_MUTATION
    elif state == "REQUEST_CHANGES":
        activity = Activity.REQUEST_CHANGES
        document = _REQUEST_CHANGES_MUTATION
    else:
        raise AdapterError(f"submit_review: unknown state {state!r}")
    kind = MutationKind.REVIEW_SUBMIT
    payload = {"repo": job.repo, "number": job.number, "state": state, "body": body}

    def perform(cmid: str) -> _Outcome:
        try:
            node = _read_pr_node(adapter, job=job, operation="submit_review")
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("submit_review", failure), "uncertain", None)
        if state == "APPROVE":
            # §3.2: the fresh read is APPROVE's mandatory pre-check (U-AUTHORITY-08).
            if node.state != "OPEN":
                return _Outcome(
                    "stale", Stale(reason="pr_closed", observed_head_sha=node.head_ref_oid), "uncertain", None
                )
            if node.head_ref_oid != job.head_sha:
                return _Outcome(
                    "stale", Stale(reason="head_changed", observed_head_sha=node.head_ref_oid), "uncertain", None
                )
        _mark_pending(adapter, cmid=cmid, job=job, kind=kind, created_at=None)
        try:
            data = adapter.transport.mutate(
                document, {"pullRequestId": node.pr_id, "body": body}, operation="submit_review"
            )
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("submit_review", failure), "uncertain", None)
        if state == "REQUEST_CHANGES":
            return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "completed", data)
        # §3.2: APPROVE's mandatory review-visibility post-check (U-AUTHORITY-08).
        visible = _visible_matching_approval(adapter, job=job, viewer_login=node.viewer_login)
        if visible:
            return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "verified", data)
        return _Outcome(
            "unavailable",
            GithubUnavailable(op="submit_review", reason="incomplete", retriable=True),
            "pending",
            data,
        )

    return _dispatch(
        adapter,
        job=job,
        grant=grant,
        activity=activity,
        kind=kind,
        payload=payload,
        record=record,
        perform=perform,
    )


def comment(*, adapter, job: Job, body: str, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable:
    kind = MutationKind.COMMENT
    payload = {"repo": job.repo, "number": job.number, "body": body}

    def perform(cmid: str) -> _Outcome:
        try:
            node = _read_pr_node(adapter, job=job, operation="comment")
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("comment", failure), "uncertain", None)
        _mark_pending(adapter, cmid=cmid, job=job, kind=kind, created_at=None)
        try:
            data = adapter.transport.mutate(
                _COMMENT_MUTATION, {"pullRequestId": node.pr_id, "body": body}, operation="comment"
            )
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("comment", failure), "uncertain", None)
        return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "completed", data)

    return _dispatch(
        adapter,
        job=job,
        grant=grant,
        activity=Activity.COMMENT,
        kind=kind,
        payload=payload,
        record=record,
        perform=perform,
    )


def _is_head_mismatch(errors: tuple[Mapping, ...]) -> bool:
    """GitHub's expected-head refusal, recognised from the GraphQL error text
    (`expectedHeadOid` produces "Head branch was modified...")."""
    for error in errors:
        message = str(error.get("message", "")).lower() if isinstance(error, Mapping) else ""
        if "head branch was modified" in message or "expected head" in message:
            return True
    return False


def merge(*, adapter, job: Job, grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable:
    kind = MutationKind.MERGE
    payload = {"repo": job.repo, "number": job.number, "expected_head_oid": job.head_sha}

    def perform(cmid: str) -> _Outcome:
        # One addressing read for the PR node id. Its head is retained as the
        # observation for a Stale value but is NOT a pre-check gate (T11: no
        # separate pre-check call; GitHub's expectedHeadOid decides).
        try:
            node = _read_pr_node(adapter, job=job, operation="merge")
        except transport_module.Unavailable as failure:
            return _Outcome("unavailable", _unavailable("merge", failure), "uncertain", None)
        _mark_pending(adapter, cmid=cmid, job=job, kind=kind, created_at=None)
        try:
            data = adapter.transport.mutate(
                _MERGE_MUTATION,
                {"pullRequestId": node.pr_id, "expectedHeadOid": job.head_sha},
                operation="merge",
            )
        except transport_module.Unavailable as failure:
            if failure.reason == "graphql_error" and _is_head_mismatch(failure.errors):
                return _Outcome(
                    "stale", Stale(reason="head_changed", observed_head_sha=node.head_ref_oid), "uncertain", None
                )
            return _Outcome("unavailable", _unavailable("merge", failure), "uncertain", None)
        return _Outcome("submitted", Mutation(id=cmid, kind=kind.value, accepted=True), "completed", data)

    return _dispatch(
        adapter,
        job=job,
        grant=grant,
        activity=Activity.MERGE,
        kind=kind,
        payload=payload,
        record=record,
        perform=perform,
    )
