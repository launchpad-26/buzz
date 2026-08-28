#!/usr/bin/env python3
"""Guarded approval mutation executor.

Runs the APPROVE mutation ONLY when every pre-mutation check passes:

- A persisted, eligible, NON-EXPIRED approval decision record is loaded from
  SQLite by decision ID — caller JSON is never an acceptable source.
- The decision is validated independently against the caller-supplied current
  repo, PR number, current head SHA and current full-config/policy hash.
- `github_mutate.execute_approval` performs a mandatory REST final revalidation
  immediately before the mutation and a mandatory REST review verification after
  it. All transport/read functions are injectable for fake tests; when absent
  they are wired to the real REST allowlist so production never approves without
  live revalidation + verification.

Every gate defaults to false (fail-closed). The event is fixed to APPROVE inside
the mutation executor; no caller can inject an arbitrary review event, and a
protected trigger always prevents live approval.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from cli import resolve_or_onboarding, make_state
from github_mutate import (
    ApprovalRecordRequiredError,
    DecisionStaleError,
    MutationUncertainError,
    PermissionAuthorityError,
    execute_approval,
)
from risk import protected_triggered


def load_eligible_decision(state, decision_id: str) -> dict[str, Any] | None:
    """Load the persisted approval decision by ID (SQLite-only; never caller JSON)."""
    row = state.db.execute(
        "SELECT id, repo, number, head_sha, policy_hash, status, mode, risk_score, created_at, expires_at "
        "FROM approval_decisions WHERE id=?",
        (decision_id,),
    ).fetchone()
    return dict(row) if row else None


def build_revalidation(
    config: dict[str, Any],
    *,
    current_head_sha: str,
    login: str,
    rest_provider: Callable[[], dict[str, Any]],
) -> Callable[[], dict[str, bool]]:
    """Return the injectable REST final-revalidation `rest_before` for approval.

    `rest_provider()` must return the current REST PR meta (a dict) with at least
    `head.sha`, `draft`, `user.login` and `files`. Every check fails closed; a
    protected trigger always prevents live approval.
    """
    patterns = (config.get("risk", {}) or {}).get("protected_triggers") or []

    def revalidate() -> dict[str, bool]:
        meta = rest_provider() or {}
        files = [str(f) for f in (meta.get("files") or [])]
        protected_hit = any(protected_triggered([f], patterns)[0] for f in files)
        return {
            "pr_found": bool(meta),
            "head_matches": (meta.get("head", {}) or {}).get("sha") == current_head_sha,
            "pr_open_not_draft": bool(meta.get("draft")) is False,
            "no_protected_trigger": not protected_hit,
            "author_not_identity": (meta.get("user", {}) or {}).get("login") != login,
        }

    return revalidate


def build_verification(
    reviews_provider: Callable[[], list[dict[str, Any]]],
    login: str,
    head_sha: str,
) -> Callable[[], str]:
    """Return the injectable REST post-mutation verification `rest_after`.

    Confirms an APPROVED review by the expected login on the exact head SHA.
    Returns 'verified' when confirmed, else 'uncertain' (never a blind retry)."""

    def verify() -> str:
        reviews = reviews_provider() or []
        for review in reviews:
            user = review.get("user", {}) or {}
            if (user.get("login") == login
                    and review.get("state") == "APPROVED"
                    and review.get("commit_id") == head_sha):
                return "verified"
        return "uncertain"

    return verify


def _real_rest_wiring(config, state, repo, number, head_sha, login):
    """Wire the mandatory REST revalidation + verification to the REST allowlist."""
    from github_rest import RestReader

    reader = RestReader(config or {}, state)
    revalidate = build_revalidation(
        config or {}, current_head_sha=head_sha, login=login,
        rest_provider=lambda: reader.pr_meta(repo, number),
    )
    verify = build_verification(lambda: reader.pr_reviews(repo, number), login, head_sha)
    return revalidate, verify


#: Outcome classifications returned by `approve`. The dispatcher maps these to
#: distinct job states, so a denial (human can still decide) is never confused
#: with an uncertain mutation (must stop, never blindly retry).
APPROVED = "approved"
NO_DECISION = "no_decision"
DENIED = "denied"
STALE = "stale"
UNCERTAIN = "uncertain"
FAILED = "failed"


def approve(
    state,
    *,
    decision_id: str,
    repo: str,
    number: int,
    head_sha: str,
    policy_hash: str,
    pr_node_id: str,
    login: str,
    body: str = "Approved by review-queue-automation (live).",
    config: dict[str, Any] | None = None,
    http_post: Callable[..., tuple[int, dict[str, Any]]] | None = None,
    rest_before: Callable[[], Any] | None = None,
    rest_after: Callable[[], Any] | None = None,
) -> tuple[bool, str, str]:
    """Execute the APPROVE mutation under an eligible, non-expired decision.

    Returns `(ok, status, message)` where `status` is one of the module-level
    classifications. The decision is loaded from SQLite by ID; current
    repo/PR/head/policy are compared independently against the stored record,
    then `execute_approval` enforces mandatory REST revalidation (before) and
    review verification (after). Transport/read callables are injectable for fake
    tests; when absent they are wired to the real REST allowlist so production
    never approves without live revalidation + verification.
    """
    decision = load_eligible_decision(state, decision_id)
    if decision is None:
        return False, NO_DECISION, f"no eligible decision record for id {decision_id}"

    if rest_before is None or rest_after is None:
        rest_before, rest_after = _real_rest_wiring(
            config, state, repo, number, head_sha, login
        )

    try:
        execute_approval(
            state,
            decision,
            {"pullRequestId": pr_node_id, "body": body},
            f"approve-{decision_id}",
            decision_id=decision_id,
            repo=repo, number=number,
            current_head_sha=head_sha, current_policy_hash=policy_hash,
            login=login,
            http_post=http_post,
            rest_before=rest_before,
            rest_after=rest_after,
        )
    except (ApprovalRecordRequiredError, PermissionAuthorityError) as exc:
        return False, DENIED, str(exc)
    except DecisionStaleError as exc:
        return False, STALE, str(exc)
    except MutationUncertainError as exc:
        return False, UNCERTAIN, str(exc)
    except RuntimeError as exc:
        return False, FAILED, str(exc)
    return True, APPROVED, "approved"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Approval mutation executor")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--number", required=True, type=int)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--policy-hash", required=True)
    parser.add_argument("--pr-node-id", required=True)
    parser.add_argument("--login", required=True)
    parser.add_argument("--body", default="Approved by review-queue-automation (live).")
    args = parser.parse_args(argv)

    cfg, _ = resolve_or_onboarding(args.repo_root)
    if cfg is None:
        return 1
    state = make_state(cfg)
    try:
        ok, status, msg = approve(
            state,
            decision_id=args.decision_id,
            repo=args.repo, number=args.number,
            head_sha=args.head_sha, policy_hash=args.policy_hash,
            pr_node_id=args.pr_node_id, login=args.login,
            body=args.body, config=cfg,
        )
        print(json.dumps({"ok": ok, "status": status, "message": msg}, indent=2))
        return 0 if ok else 1
    finally:
        state.close()


if __name__ == "__main__":
    sys.exit(main())
