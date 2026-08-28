#!/usr/bin/env python3
"""The sole GitHub mutation executor. Named GraphQL templates, REST-verified.

Authority is fixed inside the module:

- `add_comment_review` -> event is always COMMENT. The caller cannot supply an event.
- `approve_review`     -> event is always APPROVE AND requires a persisted, eligible
                          decision record matching repo + PR + head SHA + policy hash.
                          Approval is reached ONLY through `execute_approval`, which
                          loads the decision by ID from SQLite (caller JSON is never
                          trusted) and demands a mandatory REST final revalidation
                          before the mutation and a mandatory REST review
                          verification after it. The generic `post` entry point
                          refuses every approval-required operation.

Every mutation is verified against REST after completion. On ambiguity the executor
re-raises as `uncertain` rather than blindly retrying; the double-send is never
repeated without a fresh, revalidated decision.

The curl transport (`_http_post`), pre-mutation REST revalidation (`rest_before`)
and post-mutation REST verification (`rest_after`) are injectable so the module is
fully unit-testable with fakes and no GitHub access.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Callable

from common import State, github_token, mutation_id, utcnow
from errors import DecisionStaleError, MutationUncertainError, PermissionAuthorityError

_BASE = "https://api.github.com/graphql"

_COMMENT_QUERY = (
    "mutation($pullRequestId:ID!$body:String!){"
    "addPullRequestReview(input:{pullRequestId:$pullRequestId,body:$body,event:COMMENT}){"
    "pullRequestReview{id}}}"
)
_APPROVE_QUERY = (
    "mutation($pullRequestId:ID!$body:String!){"
    "addPullRequestReview(input:{pullRequestId:$pullRequestId,body:$body,event:APPROVE}){"
    "pullRequestReview{id}}}"
)
_REQUEST_CHANGES_QUERY = (
    "mutation($pullRequestId:ID!$body:String!){"
    "addPullRequestReview(input:{pullRequestId:$pullRequestId,body:$body,event:CHANGES_REQUESTED}){"
    "pullRequestReview{id}}}"
)
_CREATE_ISSUE_QUERY = (
    "mutation($repositoryId:ID!$title:String!$body:String!){"
    "createIssue(input:{repositoryId:$repositoryId,title:$title,body:$body}){"
    "issue{number}}}"
)
_ADD_LABELS_QUERY = (
    "mutation($labelableId:ID!$labelIds:[ID!]!){"
    "addLabelsToLabelable(input:{labelableId:$labelableId,labelIds:$labelIds}){"
    "labelable{id}}}"
)
_REQUEST_REVIEW_QUERY = (
    "mutation($pullRequestId:ID!$userIds:[ID!]!){"
    "requestReviews(input:{pullRequestId:$pullRequestId,userIds:$userIds}){"
    "pullRequest{id}}}"
)
_THREAD_REPLY_QUERY = (
    "mutation($pullRequestReviewThreadId:ID!$body:String!){"
    "addPullRequestReviewThreadReply(input:{"
    "pullRequestReviewThreadId:$pullRequestReviewThreadId,body:$body}){"
    "comment{id}}}"
)
_ASSIGNEE_QUERY = (
    "mutation($assignableId:ID!$assigneeIds:[ID!]!){"
    "addAssigneesToAssignable(input:{assignableId:$assignableId,assigneeIds:$assigneeIds}){"
    "assignable{... on PullRequest{id}}}}"
)
_REMOVE_ASSIGNEE_QUERY = (
    "mutation($assignableId:ID!$assigneeIds:[ID!]!){"
    "removeAssigneesFromAssignable(input:{"
    "assignableId:$assignableId,assigneeIds:$assigneeIds}){"
    "assignable{... on PullRequest{id}}}}"
)


class ApprovalRecordRequiredError(Exception):
    """A caller tried to approve without a persisted, eligible decision record."""


#: Lifecycle states persisted for the APPROVE mutation. Only `verified` is
#: persisted after REST confirms the effect; `pending`/`failed`/`uncertain` are
#: never blindly retried with another mutation.
LIFECYCLE_STATES = ("verified", "failed", "uncertain")


MUTATIONS: dict[str, dict[str, Any]] = {
    "add_comment_review": {"query": _COMMENT_QUERY, "event": "COMMENT", "approval_required": False},
    "approve_review": {"query": _APPROVE_QUERY, "event": "APPROVE", "approval_required": True},
    "request_changes_review": {"query": _REQUEST_CHANGES_QUERY, "event": "CHANGES_REQUESTED", "approval_required": False},
    "create_issue": {"query": _CREATE_ISSUE_QUERY, "event": None, "approval_required": False},
    "add_labels": {"query": _ADD_LABELS_QUERY, "event": None, "approval_required": False},
    "request_review": {"query": _REQUEST_REVIEW_QUERY, "event": None, "approval_required": False},
    "thread_reply": {"query": _THREAD_REPLY_QUERY, "event": None, "approval_required": False},
    "add_assignee": {"query": _ASSIGNEE_QUERY, "event": None, "approval_required": False},
    "remove_assignee": {"query": _REMOVE_ASSIGNEE_QUERY, "event": None, "approval_required": False},
}


def fixed_event_of(name: str) -> str | None:
    return MUTATIONS.get(name, {}).get("event")


def requires_approval_record(name: str) -> bool:
    return bool(MUTATIONS.get(name, {}).get("approval_required"))


def handle_http_post(
    token: str,
    payload: str,
    *,
    timeout: int = 60,
) -> tuple[int, dict[str, Any]]:
    """POST one GraphQL body. Returns (status, parsed_json). Injectable for tests."""
    request = urllib.request.Request(
        _BASE,
        data=payload.encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "review-queue-automation",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _record(state: State, client_mutation_id: str, operation: str, status: str, data: dict[str, Any] | None = None) -> None:
    now = utcnow()
    response = json.dumps(data) if data is not None else None
    state.db.execute(
        "INSERT INTO mutations(client_mutation_id,operation,status,response,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?) ON CONFLICT(client_mutation_id) DO UPDATE SET "
        "status=excluded.status,response=excluded.response,updated_at=excluded.updated_at",
        (client_mutation_id, operation, status, response, now, now),
    )
    state.db.commit()


def _existing_mutation(state: State, client_mutation_id: str) -> tuple[str | None, str | None]:
    row = state.db.execute(
        "SELECT status,response FROM mutations WHERE client_mutation_id=?", (client_mutation_id,)
    ).fetchone()
    if not row:
        return None, None
    return row["status"], row["response"]


def _iso_expired(expires_at: str, now: str) -> bool:
    try:
        expiry = dt.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        current = dt.datetime.fromisoformat(now.replace("Z", "+00:00"))
        return current >= expiry
    except ValueError:
        # Unparseable expiry fails closed (treated as expired).
        return True


def require_eligible_decision(
    decision: dict[str, Any] | None,
    *,
    job: str, repo: str, number: int, head_sha: str, policy_hash: str,
    now: str | None = None,
) -> None:
    """Refuse approval unless a persisted, matching, NON-EXPIRED decision exists.

    The decision is validated INDEPENDENTLY against the caller-supplied current
    repo, PR number, current head SHA and current full-config/policy hash — it
    is never compared against values read back out of the decision itself.
    """
    if not decision:
        raise ApprovalRecordRequiredError(f"no approval decision record for job {job}")
    if (decision.get("repo"), int(decision.get("number", 0))) != (repo, int(number)):
        raise ApprovalRecordRequiredError("approval decision repo/PR mismatch")
    if decision.get("head_sha") != head_sha:
        raise DecisionStaleError("approval decision head is stale")
    if decision.get("policy_hash") != policy_hash:
        raise DecisionStaleError("approval decision policy hash is stale")
    if decision.get("status") != "eligible":
        raise ApprovalRecordRequiredError("approval decision is not eligible")
    expires_at = decision.get("expires_at")
    if not expires_at:
        raise DecisionStaleError("approval decision has no expiry")
    if _iso_expired(expires_at, now or utcnow()):
        raise DecisionStaleError("approval decision is expired")


def _load_decision_by_id(state: State, decision_id: str) -> dict[str, Any] | None:
    row = state.db.execute(
        "SELECT * FROM approval_decisions WHERE id=?", (decision_id,)
    ).fetchone()
    return dict(row) if row else None


def post(
    state: State,
    operation: str,
    variables: dict[str, Any],
    job: str,
    *,
    token: str | None = None,
    http_post: Callable[..., tuple[int, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Execute a NON-approval mutation, recording it idempotently.

    The generic entry point NEVER exposes APPROVE: any operation flagged
    `approval_required` is refused here and must go through `execute_approval`,
    which enforces the eligible-decision record + mandatory REST revalidation.
    """
    if operation not in MUTATIONS:
        raise RuntimeError(f"unsupported mutation operation: {operation}")
    if requires_approval_record(operation):
        raise ApprovalRecordRequiredError(
            f"{operation} requires an eligible decision record; use execute_approval"
        )
    query = MUTATIONS[operation]["query"]
    client_mutation_id = mutation_id(job, operation)
    existing, cached = _existing_mutation(state, client_mutation_id)
    if existing == "completed":
        return json.loads(cached) if cached else {}

    clean = {key: value for key, value in variables.items() if value not in (None, "")}
    clean.setdefault("clientMutationId", client_mutation_id)
    payload = json.dumps({"query": query, "variables": clean, "operationName": None})
    sender = http_post or handle_http_post
    token_resolved = token or github_token()
    try:
        status, result = sender(token_resolved, payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        state.record_api_call("graphql", operation, exc.code, {"remaining": None})
        raise RuntimeError(f"GraphQL {operation} failed ({exc.code}): {detail[:800]}") from exc
    state.record_api_call("graphql", operation, status, {"remaining": None})
    if result.get("errors"):
        raise RuntimeError(f"GraphQL {operation} errors: {json.dumps(result['errors'])[:800]}")
    data = result.get("data", {}) or {}
    _record(state, client_mutation_id, operation, "completed", data)
    return data


def _revalidate_before(rest_before: Callable[[], Any] | None) -> None:
    """Mandatory REST final revalidation immediately before the approval mutation.

    Refuses (raises, no mutation) whenever revalidation is missing or reports any
    failing condition. This is the hard backstop that a forged or stale decision
    cannot pass through."""
    if rest_before is None:
        raise PermissionAuthorityError("approval requires REST final revalidation before mutation")
    result = rest_before()
    if result is None:
        raise PermissionAuthorityError("approval final revalidation returned no result")
    if isinstance(result, dict):
        bad = [k for k, v in result.items() if not v]
        if bad:
            raise PermissionAuthorityError(f"approval final revalidation failed: {', '.join(bad)}")
        return
    if not result:
        raise PermissionAuthorityError("approval final revalidation failed")


def _confirm_review(reviews: list[dict[str, Any]], login: str, state_expected: str, head_sha: str) -> bool:
    # GitHub returns "APPROVED"/"CHANGES_REQUESTED"/"COMMENTED" review states via REST.
    for review in reviews:
        if (review.get("user", {}).get("login") == login
                and review.get("state") == state_expected
                and review.get("commit_id") == head_sha):
            return True
    return False


def _normalize_verification(result: Any, login: str | None, head_sha: str | None) -> str:
    """Interpret a post-mutation REST verification result into a lifecycle state.

    A string is taken verbatim from {verified, failed, uncertain}. A list of
    reviews is confirmed against the expected reviewer/head; a failure to confirm
    is `uncertain` (the mutation may or may not have landed) — never a blind
    retry on our side."""
    if isinstance(result, str):
        status = result.lower()
        if status in LIFECYCLE_STATES:
            return status
        return "uncertain"
    if isinstance(result, list):
        if login and head_sha and _confirm_review(result, login, "APPROVED", head_sha):
            return "verified"
        return "uncertain"
    return "uncertain"


def execute_approval(
    state: State,
    decision: dict[str, Any],
    variables: dict[str, Any],
    job: str,
    *,
    decision_id: str | None = None,
    repo: str = "",
    number: int = 0,
    current_head_sha: str = "",
    current_policy_hash: str = "",
    now: str | None = None,
    login: str | None = None,
    token: str | None = None,
    http_post: Callable[..., tuple[int, dict[str, Any]]] | None = None,
    rest_before: Callable[[], Any] | None = None,
    rest_after: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    """Approve a PR ONLY with a persisted, eligible, unexpired decision record.

    The decision is loaded by `decision_id` from SQLite when given (the
    authoritative path); otherwise the caller-supplied `decision` dict is treated
    as the record but still validated independently against the caller-supplied
    current repo/PR/head/policy. Caller JSON alone can never satisfy approval.

    Order of operations:
      1. resolve + validate the eligible decision (head/policy/status/expiry)
      2. mandatory REST final revalidation (no mutation on failure)
      3. GraphQL APPROVE (persist `pending`)
      4. mandatory REST review verification -> persist `verified` | `failed` |
         `uncertain`. `verified` is persisted only on REST confirmation; `uncertain`
         raises without a blind retry.

    Raises:
      - ApprovalRecordRequiredError  if decision missing / not eligible / mismatched.
      - DecisionStaleError           if decision head, policy, or expiry is stale.
      - PermissionAuthorityError     if mandatory revalidation fails or is absent.
      - MutationUncertainError       if the effect can't be confirmed.
    """
    record = decision
    if decision_id:
        loaded = _load_decision_by_id(state, decision_id)
        if not loaded:
            raise ApprovalRecordRequiredError(f"no approval decision record for id {decision_id}")
        record = loaded

    require_eligible_decision(
        record,
        job=job,
        repo=repo or record.get("repo", ""),
        number=number if number else int(record.get("number", 0)),
        head_sha=current_head_sha,
        policy_hash=current_policy_hash,
        now=now,
    )

    body = variables.get("body", "Approved by review automation (shadow/live per policy).")
    head_sha = current_head_sha or record.get("head_sha", "")
    client_mutation_id = mutation_id(job, "approve_review")

    existing, cached = _existing_mutation(state, client_mutation_id)
    if existing == "verified":
        return json.loads(cached) if cached else {}

    # Mandatory REST final revalidation BEFORE any mutation.
    _revalidate_before(rest_before)

    def send() -> dict[str, Any]:
        clean = {key: value for key, value in variables.items() if value not in (None, "")}
        clean.pop("body", None)
        clean["body"] = body
        clean.setdefault("clientMutationId", client_mutation_id)
        payload = json.dumps({"query": _APPROVE_QUERY, "variables": clean, "operationName": None})
        sender = http_post or handle_http_post
        token_resolved = token or github_token()
        try:
            status, result = sender(token_resolved, payload)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            state.record_api_call("graphql", "approve_review", exc.code, {"remaining": None})
            raise RuntimeError(f"GraphQL approve_review failed ({exc.code}): {detail[:800]}") from exc
        state.record_api_call("graphql", "approve_review", status, {"remaining": None})
        if result.get("errors"):
            raise RuntimeError(f"GraphQL approve_review errors: {json.dumps(result['errors'])[:800]}")
        data = result.get("data", {}) or {}
        _record(state, client_mutation_id, "approve_review", "pending", data)
        return data

    if existing is not None and existing in ("pending", "uncertain", "failed"):
        # Never blindly re-send. Re-verify only; escalate without a second mutation.
        remaining = json.loads(cached) if cached else {}
        status = _normalize_verification(rest_after() if rest_after is not None else None, login, head_sha)
        data = remaining
    else:
        data = send()
        status = _normalize_verification(rest_after() if rest_after is not None else None, login, head_sha)

    if status == "uncertain":
        _record(state, client_mutation_id, "approve_review", "uncertain", data)
        raise MutationUncertainError("cannot confirm approval review landed after mutation")
    if status == "failed":
        _record(state, client_mutation_id, "approve_review", "failed", data)
        raise RuntimeError("approval review was not applied (REST verification failed)")
    # verified
    _record(state, client_mutation_id, "approve_review", "verified", data)
    return data


def execute_request_changes(
    state: State,
    variables: dict[str, Any],
    job: str,
    *,
    token: str | None = None,
    http_post: Callable[..., tuple[int, dict[str, Any]]] | None = None,
    rest_probe: Callable[[], list[dict[str, Any]]] | None = None,
    login: str | None = None,
    head_sha: str | None = None,
) -> dict[str, Any]:
    """Post a CHANGES_REQUESTED review. Event is fixed internally to CHANGES_REQUESTED.

    This is only reachable through the verified-blocker request-changes gate (the
    caller must pass `execute_request_changes_for`); the event cannot be overridden
    and the mutation is REST-verified after posting.
    """
    data = post(
        state, "request_changes_review",
        {"pullRequestId": variables.get("pullRequestId"), "body": variables.get("body", "")},
        job, token=token, http_post=http_post,
    )
    if rest_probe is not None and login and head_sha:
        if not _confirm_review(rest_probe(), login, "CHANGES_REQUESTED", head_sha):
            raise MutationUncertainError("cannot confirm request-changes review landed")
    return data


def execute_comment_review(
    state: State,
    variables: dict[str, Any],
    job: str,
    *,
    token: str | None = None,
    http_post: Callable[..., tuple[int, dict[str, Any]]] | None = None,
    rest_probe: Callable[[], list[dict[str, Any]]] | None = None,
    login: str | None = None,
    head_sha: str | None = None,
) -> dict[str, Any]:
    """Post an advisory COMMENT review. Event is always COMMENT (cannot be overridden)."""
    data = post(
        state, "add_comment_review",
        {"pullRequestId": variables.get("pullRequestId"), "body": variables.get("body", "")},
        job, token=token, http_post=http_post,
    )
    if rest_probe is not None and login and head_sha:
        if not _confirm_review(rest_probe(), login, "COMMENTED", head_sha):
            raise MutationUncertainError("cannot confirm advisory comment review landed")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GraphQL-only GitHub mutation executor")
    parser.add_argument("--state-dir", default="~/.config/review-queue-automation")
    parser.add_argument("operation", choices=sorted(MUTATIONS))
    parser.add_argument("--job", required=True)
    parser.add_argument("--variables", default="{}")
    # Approval is reached ONLY by an eligible SQLite decision id — caller JSON is
    # forbidden. The current repo/number/head/policy are supplied for independent
    # comparison against the stored decision.
    parser.add_argument("--decision-id", default="")
    parser.add_argument("--repo", default="")
    parser.add_argument("--number", type=int, default=0)
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--policy-hash", default="")
    parser.add_argument("--login", default="")
    args = parser.parse_args(argv)

    from common import State as _State

    state = _State({"state_dir": args.state_dir or "~/.config/review-queue-automation"})
    try:
        variables = json.loads(args.variables)
        if args.operation == "approve_review":
            data = execute_approval(
                state, {}, variables, args.job,
                decision_id=args.decision_id or None,
                repo=args.repo, number=args.number,
                current_head_sha=args.head_sha, current_policy_hash=args.policy_hash,
                login=args.login or None,
            )
        else:
            data = post(state, args.operation, variables, args.job)
        json.dump(data, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
