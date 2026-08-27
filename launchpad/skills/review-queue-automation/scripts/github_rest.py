#!/usr/bin/env python3
"""Allowlisted REST-only GitHub reads. Direct GitHub calls are prohibited elsewhere."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from common import GithubRest, State, load_config


class RestReader:
    def __init__(self, config: dict[str, Any], state: State):
        self.rest = GithubRest(config, state)

    def open_prs(self, repo: str) -> list[dict[str, Any]]:
        owner, name = repo.split("/", 1)
        pages: list[dict[str, Any]] = []
        page = 1
        while True:
            batch = self.rest.get(
                f"/repos/{owner}/{name}/pulls",
                "list_prs",
                {"state": "open", "sort": "updated", "direction": "desc", "per_page": 100, "page": page},
            )
            pages.extend(batch)
            if len(batch) < 100:
                break
            page += 1
            if page > 5:
                raise RuntimeError("refusing to walk more than 5 PR pages")
        return pages

    def pr_meta(self, repo: str, number: int) -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        return self.rest.get(f"/repos/{owner}/{name}/pulls/{number}", "pr_meta")

    def pr_reviews(self, repo: str, number: int) -> list[dict[str, Any]]:
        owner, name = repo.split("/", 1)
        return self.rest.get(
            f"/repos/{owner}/{name}/pulls/{number}/reviews", "pr_reviews", {}, paginate=True
        )

    def review_comments(self, repo: str, number: int) -> list[dict[str, Any]]:
        owner, name = repo.split("/", 1)
        return self.rest.get(
            f"/repos/{owner}/{name}/pulls/{number}/comments", "review_comments", {}, paginate=True
        )

    def issue_comments(self, repo: str, number: int) -> list[dict[str, Any]]:
        owner, name = repo.split("/", 1)
        return self.rest.get(
            f"/repos/{owner}/{name}/issues/{number}/comments", "issue_comments", {}, paginate=True
        )

    def issue(self, repo: str, number: int) -> dict[str, Any]:
        owner, name = repo.split("/", 1)
        return self.rest.get(f"/repos/{owner}/{name}/issues/{number}", "issue_read")

    def requested_reviewers(self, repo: str, number: int) -> list[dict[str, Any]]:
        owner, name = repo.split("/", 1)
        return self.rest.get(
            f"/repos/{owner}/{name}/pulls/{number}/requested_reviewers", "requested_reviewers"
        ).get("users", [])

    def checks(self, repo: str, number: int) -> list[dict[str, Any]]:
        owner, name = repo.split("/", 1)
        return self.rest.get(
            f"/repos/{owner}/{name}/commits/refs/pull/{number}/head/check-runs",
            "check_runs",
            {"per_page": 100},
        ).get("check_runs", [])


OPERATIONS = {
    "open_prs": lambda reader, args: reader.open_prs(args.repo),
    "pr": lambda reader, args: reader.pr_meta(args.repo, args.number),
    "pr_reviews": lambda reader, args: reader.pr_reviews(args.repo, args.number),
    "review_comments": lambda reader, args: reader.review_comments(args.repo, args.number),
    "issue_comments": lambda reader, args: reader.issue_comments(args.repo, args.number),
    "requested_reviewers": lambda reader, args: reader.requested_reviewers(args.repo, args.number),
    "checks": lambda reader, args: reader.checks(args.repo, args.number),
    "checks": lambda reader, args: reader.checks(args.repo, args.number),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REST-only GitHub read allowlist")
    parser.add_argument("--config", default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in OPERATIONS:
        p_ = sub.add_parser(command)
        p_.add_argument("repo")
        if command != "open_prs":
            p_.add_argument("number", type=int)
    args = parser.parse_args(argv)

    config, _ = load_config(args.config)
    state = State(config)
    reader = RestReader(config, state)
    try:
        result = OPERATIONS[args.command](reader, args)
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())