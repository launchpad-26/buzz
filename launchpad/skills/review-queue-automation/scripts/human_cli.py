#!/usr/bin/env python3
"""Deterministic human request CLI (no interactive stdin).

Commands:
  list                      list pending human approval requests
  show <request_id>         inspect one request
  decide <request_id> <approve|decline|request_changes> --actor <name> [--reason ...]
  resume <job_id>           resume a job whose human approval was granted
  supersede <repo> <pr> <head_sha>

Resumption: deciding 'approve' marks the request approved; `resume` then moves
the bound job `human_approval_pending -> approval_revalidation` and NEVER at the
mutation stage. `decide decline|request_changes` is terminal: the bound job
moves to `completed_human_declined`. Expired / stale-SHA / stale-policy
decisions cannot approve or resume.
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


def _cmd_resume(
    state,
    job_id: str,
    policy: dict[str, Any],
    *,
    current_head_sha: str | None = None,
) -> dict[str, Any]:
    """Resume a job whose human approval was granted.

    `current_head_sha`, when supplied, is the LIVE PR head read at resume time;
    approval is revalidated against it so a stale-SHA decision can never resume.
    """
    row = state.db.execute(
        "SELECT repo, number, head_sha, status FROM jobs WHERE id=?", (job_id,)
    ).fetchone()
    if not row:
        raise SystemExit(json.dumps({"error": f"job not found: {job_id}"}))
    if row["status"] != "human_approval_pending":
        raise SystemExit(
            json.dumps({"error": f"job {job_id} is not awaiting human approval (status={row['status']})"})
        )
    repo, number, head_sha = row["repo"], int(row["number"]), row["head_sha"]
    # Revalidate against the live head when the caller supplies it; otherwise the
    # job's recorded head (legacy behavior).
    approved = find_approved(state, job_id, repo, number, current_head_sha or head_sha, policy)
    if approved is None:
        raise SystemExit(
            json.dumps(
                {
                    "error": (
                        "no usable approved human request for job; "
                        "expired, stale-SHA, or stale-policy decisions cannot resume"
                    )
                }
            )
        )
    from states import can_transition
    if not can_transition("human_approval_pending", "approval_revalidation"):
        raise SystemExit(json.dumps({"error": "illegal resume transition"}))
    state.db.execute(
        "UPDATE jobs SET status='approval_revalidation', reason=?, updated_at=? WHERE id=?",
        ("human approved; resuming through approval revalidation", utcnow(), job_id),
    )
    state.db.commit()
    return {
        "job": job_id,
        "status": "approval_revalidation",
        "request_id": approved["request_id"],
        "requested_state": approved["state"],
        "actor": approved.get("decision_actor", ""),
    }


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
    res.add_argument("--head", default=None, help="live PR head SHA for stale-SHA revalidation")

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
            json.dump(
                _cmd_resume(state, args.job_id, config, current_head_sha=args.head),
                sys.stdout, indent=2, sort_keys=True,
            )
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