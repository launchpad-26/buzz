#!/usr/bin/env python3
"""Claim, verify, and release the assignee review lease via GraphQL, verified on REST.

Safety rules (enforced here):

- The mutation uses the PR node ID as `assignableId` and the configured USER
  node ID as `assigneeIds`. The USER node ID always comes from the REST `user`
  endpoint for the configured login — never a hardcoded fallback.
- `claim` only records the local lease AFTER the REST read confirms the login is
  an assignee (and does not claim a PR that has other assignees).
- `release` only deletes the local lease AFTER the REST read confirms the login
  is no longer an assignee. A failed/uncertain mutation leaves the lease intact.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from common import State, load_config, utcnow
from github_rest import RestReader


def login_from_config(config: dict[str, Any]) -> str:
    """The configured login; never a hardcoded fallback."""
    return str(config.get("login") or "").strip()


def _pr_node_id(config: dict[str, Any], state: State, repo: str, number: int) -> str:
    row = state.db.execute(
        "SELECT payload FROM prs WHERE repo=? AND number=?", (repo, number)
    ).fetchone()
    if row:
        node = json.loads(row["payload"]).get("node_id")
        if node:
            return node
    raise RuntimeError(f"no cached PR node_id for {repo}#{number}; run queue.py first")


def user_node_id_from_rest(config: dict[str, Any], state: State, login: str) -> str:
    """Read the USER node ID from the REST `user` endpoint (no GraphQL resolve)."""
    row = state.db.execute("SELECT body FROM etags WHERE url=?", (user_url(login),)).fetchone()
    if row:
        node = json.loads(row["body"]).get("node_id")
        if node:
            return node
    reader = RestReader(config, state)
    payload = reader.rest.get(f"/users/{login}", "user_node_id")
    node = payload.get("node_id")
    if not node:
        raise RuntimeError(f"user {login} has no node_id in REST response")
    return node


def user_url(login: str) -> str:
    return f"https://api.github.com/users/{login}"


def current_logins(config: dict[str, Any], state: State, repo: str, number: int) -> list[str]:
    return sorted(a.get("login", "") for a in RestReader(config, state).pr_meta(repo, number).get("assignees", []))


def claim(config: dict[str, Any], state: State, repo: str, number: int, job: str, login: str) -> bool:
    from github_mutate import post

    if not login:
        raise RuntimeError("a nonempty login is required to claim a lease")

    current = current_logins(config, state, repo, number)
    # A PR that already has another assignee is not claimable.
    if any(lg != login for lg in current):
        return False
    if login not in current:
        pr_node = _pr_node_id(config, state, repo, number)
        user_node = user_node_id_from_rest(config, state, login)
        post(
            state, "add_assignee",
            {"assignableId": pr_node, "assigneeIds": [user_node]},
            job,
        )
    # REST-verify the assignment before recording local lease state.
    verified = current_logins(config, state, repo, number)
    if login not in verified:
        return False
    if login != min(verified):
        return False
    state.db.execute(
        "INSERT INTO leases(repo, number, job_id, claimed_at) VALUES(?,?,?,?) "
        "ON CONFLICT(repo, number) DO UPDATE SET job_id=excluded.job_id,claimed_at=excluded.claimed_at",
        (repo, number, job, utcnow()),
    )
    state.db.commit()
    return True


def release(config: dict[str, Any], state: State, repo: str, number: int, job: str, login: str) -> None:
    from github_mutate import post

    current = current_logins(config, state, repo, number)
    if login in current:
        pr_node = _pr_node_id(config, state, repo, number)
        user_node = user_node_id_from_rest(config, state, login)
        post(
            state, "remove_assignee",
            {"assignableId": pr_node, "assigneeIds": [user_node]},
            job,
        )
    # REST-verify the login is no longer an assignee before dropping the lease.
    remaining = current_logins(config, state, repo, number)
    if login in remaining:
        raise RuntimeError(f"REST still lists {login} as assignee; refusing to drop the local lease")
    state.db.execute("DELETE FROM leases WHERE repo=? AND number=?", (repo, number))
    state.db.commit()


def verify(config: dict[str, Any], state: State, repo: str, number: int, login: str) -> bool:
    return login in current_logins(config, state, repo, number)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage the assignee review lease")
    parser.add_argument("--config", default=None)
    parser.add_argument("action", choices=["claim", "release", "verify"])
    parser.add_argument("repo")
    parser.add_argument("number", type=int)
    parser.add_argument("--job", required=True)
    parser.add_argument("--login", default="")
    args = parser.parse_args(argv)

    config, _ = load_config(args.config)
    state = State(config)
    login = args.login or login_from_config(config)
    try:
        if args.action == "claim":
            ok = claim(config, state, args.repo, args.number, args.job, login)
            json.dump({"claimed": ok, "lease_verified": verify(config, state, args.repo, args.number, login)}, sys.stdout)
        elif args.action == "release":
            release(config, state, args.repo, args.number, args.job, login)
            json.dump({"released": True, "remaining_logins": current_logins(config, state, args.repo, args.number)}, sys.stdout)
        else:
            json.dump({"assigned": verify(config, state, args.repo, args.number, login)}, sys.stdout)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
