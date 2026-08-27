#!/usr/bin/env python3
"""Deterministic human request CLI (no interactive stdin).

Commands:
  list                      list pending human approval requests
  show <request_id>         inspect one request
  decide <request_id> <approve|decline|request_changes> --actor <name> [--reason ...]
  resume <job_id>           resume a job whose human approval was granted
  supersede <repo> <pr> <head_sha>

Resumption: deciding 'approve' marks the request approved; `resume` then reads the
LIVE PR head, revalidates the decision against it and the current policy, and runs
the same guarded approval executor as the automatic path (mandatory REST
revalidation before the mutation, REST verification after). A human decision
authorizes an approval; it never bypasses those checks.

`decide decline|request_changes` is terminal: the bound job moves to
`completed_human_declined`. Expired / stale-SHA / stale-policy decisions cannot
approve or resume, and an unreadable live head is a refusal rather than a pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from approval import (
    find_approved,
    get,
    is_expired,
    list_pending,
    supersede_for_head,
    supersede_for_policy,
    policy_hash,
    decide,
)
from cli import resolve_or_onboarding, make_state
from common import utcnow


def live_head_sha(config: dict[str, Any], state, repo: str, number: int) -> tuple[str, str]:
    """Read the PR's CURRENT head via REST. Returns (head_sha, error).

    Resume must revalidate against the live head, not the head the decision was
    made for — comparing a decision's head against itself always matches and would
    make the staleness check meaningless.
    """
    try:
        from github_rest import RestReader

        meta = RestReader(config, state).pr_meta(repo, number) or {}
    except Exception as exc:
        return "", f"could not read the live PR head: {str(exc)[:200]}"
    head = (meta.get("head") or {}).get("sha", "")
    if not head:
        return "", "the live PR payload carried no head sha"
    return head, ""


def _cmd_resume(
    state,
    job_id: str,
    policy: dict[str, Any],
    *,
    current_head_sha: str | None = None,
    allow_recorded_head: bool = False,
    execute: bool = True,
) -> dict[str, Any]:
    """Resume a job whose human approval was granted.

    Safety properties:
      - the live PR head is read and used for revalidation by default; an
        unreadable head is a refusal, never a pass. `allow_recorded_head` is an
        explicit offline escape hatch and is recorded in the result.
      - the human decision is revalidated against that live head AND the current
        policy hash, so an expired, stale-SHA or stale-policy decision cannot act.
      - the approval itself runs through the SAME guarded executor as the
        automatic path (mandatory REST revalidation, then REST verification), so a
        human decision authorizes an approval rather than bypassing its checks.
    """
    row = state.db.execute(
        "SELECT repo, number, head_sha, status FROM jobs WHERE id=?", (job_id,)
    ).fetchone()
    if not row:
        return {"error": f"job not found: {job_id}"}
    if row["status"] != "human_approval_pending":
        return {"error": f"job {job_id} is not awaiting human approval (status={row['status']})"}

    repo, number, recorded_head = row["repo"], int(row["number"]), row["head_sha"]

    head_for_check = current_head_sha or ""
    head_source = "caller"
    if not head_for_check:
        head_for_check, err = live_head_sha(policy, state, repo, number)
        head_source = "live"
        if not head_for_check:
            if not allow_recorded_head:
                return {
                    "error": f"refusing to resume: {err}",
                    "hint": "pass --head <sha>, or --allow-recorded-head to accept "
                            "the recorded head (unsafe if the PR has advanced)",
                }
            head_for_check, head_source = recorded_head, "recorded (unverified)"

    if head_for_check != recorded_head:
        return {
            "error": "the PR advanced since review; the human decision is stale",
            "reviewed_head": recorded_head,
            "current_head": head_for_check,
        }

    approved = find_approved(state, job_id, repo, number, head_for_check, policy)
    if approved is None:
        return {
            "error": ("no usable approved human request for job; "
                      "expired, stale-SHA, or stale-policy decisions cannot resume")
        }

    from states import can_transition

    if not can_transition("human_approval_pending", "approval_revalidation"):
        return {"error": "illegal resume transition"}
    state.db.execute(
        "UPDATE jobs SET status='approval_revalidation', reason=?, updated_at=? WHERE id=?",
        ("human approved; resuming through approval revalidation", utcnow(), job_id),
    )
    state.db.commit()

    result = {
        "job": job_id,
        "status": "approval_revalidation",
        "request_id": approved["request_id"],
        "requested_state": approved["state"],
        "actor": approved.get("decision_actor", ""),
        "head_sha": head_for_check,
        "head_source": head_source,
    }
    if not execute:
        return result
    result.update(_apply_human_approval(state, job_id, repo, number, head_for_check,
                                        policy, approved))
    return result


def _apply_human_approval(
    state, job_id: str, repo: str, number: int, head_sha: str,
    policy: dict[str, Any], approved: dict[str, Any],
) -> dict[str, Any]:
    """Run the guarded approval mutation under a human authorization."""
    from approval import policy_hash as compute_policy_hash
    from approval_action import APPROVED, approve
    from approval_evaluate import persist_human_approval

    payload_row = state.db.execute(
        "SELECT payload FROM prs WHERE repo=? AND number=?", (repo, number)
    ).fetchone()
    pr_node_id = ""
    if payload_row:
        try:
            pr_node_id = (json.loads(payload_row["payload"]) or {}).get("node_id", "")
        except (ValueError, TypeError):
            pr_node_id = ""
    if not pr_node_id:
        state.db.execute(
            "UPDATE jobs SET status='safe_stop', reason=?, updated_at=? WHERE id=?",
            (f"no cached PR node_id for {repo}#{number}", utcnow(), job_id),
        )
        state.db.commit()
        return {"status": "safe_stop", "approval_outcome": "missing_node_id"}

    decision_id = persist_human_approval(
        state, repo=repo, number=number, head_sha=head_sha,
        policy_hash=compute_policy_hash(policy), cfg=policy,
        actor=approved.get("decision_actor", ""),
    )
    ok, outcome, message = approve(
        state, decision_id=decision_id, repo=repo, number=number,
        head_sha=head_sha, policy_hash=compute_policy_hash(policy),
        pr_node_id=pr_node_id, login=policy.get("login", ""),
        body=(f"Approved by review-queue-automation under human authorization "
              f"({approved.get('decision_actor', 'unknown actor')})."),
        config=policy,
    )
    if ok and outcome == APPROVED:
        for target, reason in (
            ("approval_action", "human-authorized approve mutation verified"),
            ("completed_auto_approved", "approved under human authorization"),
        ):
            state.db.execute(
                "UPDATE jobs SET status=?, reason=?, updated_at=? WHERE id=?",
                (target, reason, utcnow(), job_id),
            )
        state.db.commit()
        return {"status": "completed_auto_approved", "approval_outcome": outcome,
                "decision_id": decision_id}

    state.db.execute(
        "UPDATE jobs SET status='safe_stop', reason=?, updated_at=? WHERE id=?",
        (f"{outcome}: {message}"[:200], utcnow(), job_id),
    )
    state.db.commit()
    return {"status": "safe_stop", "approval_outcome": outcome, "reason": message}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Human approval queue CLI")
    parser.add_argument("--repo-root", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("request_id")

    dec = sub.add_parser("decide")
    dec.add_argument("request_id")
    dec.add_argument("decision", choices=["approve", "decline", "request_changes"])
    dec.add_argument("--actor", required=True)
    dec.add_argument("--reason", default="")

    res = sub.add_parser("resume")
    res.add_argument("job_id")
    res.add_argument("--head", default=None,
                     help="override the live PR head used for stale-SHA revalidation")
    res.add_argument("--allow-recorded-head", action="store_true",
                     help="accept the recorded head when the live head cannot be read "
                          "(unsafe if the PR has advanced)")
    res.add_argument("--no-execute", action="store_true",
                     help="revalidate and transition only; do not post the approval")

    sup = sub.add_parser("supersede")
    sup.add_argument("repo")
    sup.add_argument("number", type=int)
    sup.add_argument("head_sha")
    args = parser.parse_args(argv)

    repo_root = args.repo_root or "."
    resolved = resolve_or_onboarding(repo_root)
    if resolved is None:
        return 1
    config, _ = resolved
    state = make_state(config)
    try:
        if args.command == "list":
            items = [
                {k: r[k] for k in (
                    "request_id", "job_id", "repo", "number", "head_sha", "state",
                    "risk_score", "risk_band", "recommendation", "created_at", "expires_at",
                ) if k in r}
                for r in list_pending(state)
            ]
            json.dump(items, sys.stdout, indent=2, sort_keys=True)
        elif args.command == "show":
            row = get(state, args.request_id)
            if row is None:
                print(json.dumps({"error": "unknown request"}, indent=2))
                return 1
            row["expired"] = is_expired(row)
            json.dump(dict(row), sys.stdout, indent=2, sort_keys=True)
        elif args.command == "decide":
            updated = decide(state, args.request_id, args.decision, args.actor, args.reason)
            json.dump(dict(updated), sys.stdout, indent=2, sort_keys=True)
        elif args.command == "resume":
            outcome = _cmd_resume(
                state, args.job_id, config,
                current_head_sha=args.head,
                allow_recorded_head=args.allow_recorded_head,
                execute=not args.no_execute,
            )
            json.dump(outcome, sys.stdout, indent=2, sort_keys=True)
            if "error" in outcome:
                sys.stdout.write("\n")
                return 1
        else:
            count = supersede_for_head(state, args.repo, args.number, args.head_sha)
            pc = supersede_for_policy(state, args.repo, args.number, config)
            json.dump({"superseded_by_head": count, "superseded_by_policy": pc}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())