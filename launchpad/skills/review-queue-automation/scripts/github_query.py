#!/usr/bin/env python3
"""Allowlisted GraphQL bulk reads. The queue-inventory read chokepoint.

WHY THIS MODULE EXISTS. The queue reconciler needs the same handful of facts for
every open pull request: head SHA, author, draft state, assignees, requested
reviewers, reviews, changed files and check conclusions. Assembling that over
REST costs one list call plus five per-PR calls (`pr_meta`, changed files,
`checks`, `requested_reviewers`, `pr_reviews`) — about 151 calls for thirty open
pull requests, repeated on every sweep. One GraphQL query returns all of it for
up to fifty pull requests at a time.

TRANSPORT SPLIT. `github_rest.py` remains the chokepoint for per-PR reads and for
the mandatory revalidation before an approval mutation; `github_mutate.py`
remains the sole mutation chokepoint. This module is a third, narrow chokepoint:
bulk read-only inventory, allowlisted by name, no mutation vocabulary. It shares
no code with `github_mutate.py` on purpose — a read path must not be able to
reach mutation machinery, idempotency keys or the decision ledger.
See `references/contracts.md`, "GitHub transport".

FAIL CLOSED ON TRUNCATION. Every GraphQL connection is capped. A truncated file
list would understate the change and could make `no_protected_trigger` or
`limits_pass` pass on facts that were merely missing, which is exactly the
failure `queue.py` already refuses for changed files. Each capped connection is
therefore followed to completion with a cursor, and the outer pull-request walk
refuses to exceed its page cap rather than return a partial queue.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Callable

from checks import canonical as _upper, conclusion_from_status as _rollup_state_to_conclusion
from common import State, github_token, load_config

_BASE = "https://api.github.com/graphql"

#: Pull requests per page of the outer walk.
_PR_PAGE_SIZE = 50
#: Refuse to walk more than this many pages rather than report a partial queue.
_PR_PAGE_CAP = 5
#: Items per page of every nested connection.
_CONNECTION_PAGE_SIZE = 100
#: Refuse to follow a nested connection further than this.
_CONNECTION_PAGE_CAP = 20

_CHECK_FIELDS = """
        __typename
        ... on CheckRun {
          name
          status
          conclusion
          startedAt
          completedAt
        }
        ... on StatusContext {
          context
          state
          createdAt
        }
"""

QUEUE_INVENTORY = """
query QueueInventory($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: %(prs)d, states: OPEN, after: $cursor,
                 orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id
        number
        title
        url
        isDraft
        updatedAt
        additions
        deletions
        changedFiles
        reviewDecision
        baseRefName
        headRefName
        headRefOid
        author { login }
        assignees(first: 100) { pageInfo { hasNextPage endCursor } nodes { login } }
        reviewRequests(first: 100) {
          pageInfo { hasNextPage endCursor }
          nodes { requestedReviewer { ... on User { login } } }
        }
        reviews(first: %(conn)d) {
          pageInfo { hasNextPage endCursor }
          nodes { id state submittedAt author { login } commit { oid } }
        }
        files(first: %(conn)d) {
          pageInfo { hasNextPage endCursor }
          nodes { path additions deletions }
        }
        commits(last: 1) {
          nodes {
            commit {
              statusCheckRollup {
                state
                contexts(first: %(conn)d) {
                  pageInfo { hasNextPage endCursor }
                  nodes {
%(checks)s
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
""" % {"prs": _PR_PAGE_SIZE, "conn": _CONNECTION_PAGE_SIZE, "checks": _CHECK_FIELDS}

_FILES_PAGE = """
query FilesPage($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      files(first: %(conn)d, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { path additions deletions }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
""" % {"conn": _CONNECTION_PAGE_SIZE}

_REVIEWS_PAGE = """
query ReviewsPage($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: %(conn)d, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id state submittedAt author { login } commit { oid } }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
""" % {"conn": _CONNECTION_PAGE_SIZE}

_CONTEXTS_PAGE = """
query ContextsPage($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      commits(last: 1) {
        nodes {
          commit {
            statusCheckRollup {
              contexts(first: %(conn)d, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
%(checks)s
                }
              }
            }
          }
        }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
""" % {"conn": _CONNECTION_PAGE_SIZE, "checks": _CHECK_FIELDS}

_ASSIGNEES_PAGE = """
query AssigneesPage($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      assignees(first: %(conn)d, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { login }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
""" % {"conn": _CONNECTION_PAGE_SIZE}

_REVIEW_REQUESTS_PAGE = """
query ReviewRequestsPage($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewRequests(first: %(conn)d, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { requestedReviewer { ... on User { login } } }
      }
    }
  }
  rateLimit { cost remaining resetAt }
}
""" % {"conn": _CONNECTION_PAGE_SIZE}

#: Named, read-only queries. Nothing outside this table may be sent.
QUERIES: dict[str, str] = {
    "queue_inventory": QUEUE_INVENTORY,
    "files_page": _FILES_PAGE,
    "reviews_page": _REVIEWS_PAGE,
    "contexts_page": _CONTEXTS_PAGE,
    "assignees_page": _ASSIGNEES_PAGE,
    "review_requests_page": _REVIEW_REQUESTS_PAGE,
}

_FORBIDDEN = ("mutation", "subscription")


class InventoryError(RuntimeError):
    """A bulk read could not be completed with complete facts."""


def handle_http_post(
    token: str,
    payload: str,
    *,
    timeout: int = 60,
) -> tuple[int, dict[str, Any]]:
    """POST one GraphQL read body. Returns (status, parsed_json). Injectable.

    Deliberately separate from `github_mutate.handle_http_post`: the read path
    must not import the mutation module.
    """
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
        body = response.read().decode("utf-8")
        return response.status, json.loads(body) if body else {}


# The conclusion vocabulary lives in `checks.py` and nowhere else. This module
# is the transport that PRODUCES conclusions, which makes it the worst possible
# place to keep a second copy: drift here feeds every consumer wrong data.
# Aliased rather than re-wrapped so there is one implementation, not two names
# for two functions that happen to agree today.


class InventoryReader:
    """Bulk, read-only queue inventory over GraphQL."""

    def __init__(
        self,
        config: dict[str, Any],
        state: State,
        *,
        http_post: Callable[..., tuple[int, dict[str, Any]]] | None = None,
        token: str | None = None,
    ):
        self.config = config
        self.state = state
        self._post = http_post or handle_http_post
        self._token = token
        self.timeout = int((config.get("github") or {}).get("timeout_seconds", 30))

    def _token_value(self) -> str:
        if self._token is None:
            self._token = github_token()
        return self._token

    def query(self, operation: str, variables: dict[str, Any]) -> dict[str, Any]:
        if operation not in QUERIES:
            raise InventoryError(f"unsupported read operation: {operation}")
        document = QUERIES[operation]
        lowered = document.lower()
        for word in _FORBIDDEN:
            if word in lowered:
                raise InventoryError(f"read query {operation} contains {word!r}")
        payload = json.dumps({"query": document, "variables": variables})
        try:
            status, result = self._post(self._token_value(), payload, timeout=self.timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            self.state.record_api_call("graphql", operation, exc.code, {})
            raise InventoryError(f"GraphQL {operation} failed ({exc.code}): {detail[:800]}") from exc
        rate = ((result.get("data") or {}).get("rateLimit") or {})
        self.state.record_api_call(
            "graphql",
            operation,
            status,
            {"x-ratelimit-used": rate.get("cost"), "x-ratelimit-remaining": rate.get("remaining")},
        )
        if result.get("errors"):
            raise InventoryError(
                f"GraphQL {operation} errors: {json.dumps(result['errors'])[:800]}"
            )
        return result.get("data") or {}

    # -- connection completion -------------------------------------------------

    def _complete(
        self,
        operation: str,
        repo: str,
        number: int,
        connection: dict[str, Any],
        extract: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Follow a capped connection to completion. Never returns partial facts."""
        owner, name = repo.split("/", 1)
        nodes = list(connection.get("nodes") or [])
        page_info = connection.get("pageInfo") or {}
        pages = 0
        while page_info.get("hasNextPage"):
            pages += 1
            if pages > _CONNECTION_PAGE_CAP:
                raise InventoryError(
                    f"{operation} for {repo}#{number} exceeded {_CONNECTION_PAGE_CAP} pages; "
                    "refusing to enrich with a truncated list"
                )
            data = self.query(
                operation,
                {"owner": owner, "name": name, "number": number,
                 "cursor": page_info.get("endCursor")},
            )
            nxt = extract(data)
            nodes.extend(nxt.get("nodes") or [])
            page_info = nxt.get("pageInfo") or {}
        return nodes

    @staticmethod
    def _pr_connection(data: dict[str, Any], field: str) -> dict[str, Any]:
        pr = ((data.get("repository") or {}).get("pullRequest") or {})
        return pr.get(field) or {}

    @staticmethod
    def _contexts_connection(data: dict[str, Any]) -> dict[str, Any]:
        pr = ((data.get("repository") or {}).get("pullRequest") or {})
        commits = ((pr.get("commits") or {}).get("nodes") or [])
        if not commits:
            return {}
        rollup = ((commits[0].get("commit") or {}).get("statusCheckRollup") or {})
        return rollup.get("contexts") or {}

    # -- shaping ---------------------------------------------------------------

    def _checks(self, repo: str, number: int, node: dict[str, Any]) -> list[dict[str, Any]]:
        commits = ((node.get("commits") or {}).get("nodes") or [])
        if not commits:
            return []
        rollup = ((commits[0].get("commit") or {}).get("statusCheckRollup") or {})
        if not rollup:
            return []
        raw = self._complete(
            "contexts_page", repo, number, rollup.get("contexts") or {}, self._contexts_connection
        )
        checks: list[dict[str, Any]] = []
        for item in raw:
            if item.get("__typename") == "CheckRun":
                checks.append(
                    {
                        "name": item.get("name") or "",
                        "status": _upper(item.get("status")),
                        "conclusion": _upper(item.get("conclusion")),
                        "started_at": item.get("startedAt"),
                        "completed_at": item.get("completedAt"),
                    }
                )
            else:
                checks.append(
                    {
                        "name": item.get("context") or "",
                        "context": item.get("context") or "",
                        "status": "COMPLETED",
                        "conclusion": _rollup_state_to_conclusion(item.get("state")),
                        "submitted_at": item.get("createdAt"),
                    }
                )
        return checks

    def _packet(self, repo: str, node: dict[str, Any]) -> dict[str, Any]:
        """One pull request, shaped exactly as the REST enrichment shaped it.

        Downstream consumers read the persisted payload, so the key names and
        nesting here are a compatibility contract, not a free choice.
        """
        number = int(node["number"])
        head = node.get("headRefOid") or ""
        if not head:
            raise InventoryError(f"PR #{number} in {repo} has no head SHA")
        author = (node.get("author") or {}).get("login") or ""

        files_nodes = self._complete(
            "files_page", repo, number, node.get("files") or {},
            lambda data: self._pr_connection(data, "files"),
        )
        reviews_nodes = self._complete(
            "reviews_page", repo, number, node.get("reviews") or {},
            lambda data: self._pr_connection(data, "reviews"),
        )
        assignee_nodes = self._complete(
            "assignees_page", repo, number, node.get("assignees") or {},
            lambda data: self._pr_connection(data, "assignees"),
        )
        request_nodes = self._complete(
            "review_requests_page", repo, number, node.get("reviewRequests") or {},
            lambda data: self._pr_connection(data, "reviewRequests"),
        )

        # `changedFiles` is GitHub's own count. If the completed file list does not
        # match it, the inventory is incomplete and must not be used to decide
        # whether a change is bounded or touches a protected path.
        declared = node.get("changedFiles")
        if isinstance(declared, int) and declared != len(files_nodes):
            raise InventoryError(
                f"file list for {repo}#{number} is incomplete: GitHub reports "
                f"{declared} changed files, inventory assembled {len(files_nodes)}"
            )

        assignees = [{"login": a.get("login")} for a in assignee_nodes if a.get("login")]
        requested_reviewers = [
            {"login": (r.get("requestedReviewer") or {}).get("login")}
            for r in request_nodes
            if (r.get("requestedReviewer") or {}).get("login")
        ]
        reviews = [
            {
                "id": r.get("id"),
                "state": _upper(r.get("state")),
                "submitted_at": r.get("submittedAt"),
                "commit_id": (r.get("commit") or {}).get("oid") or "",
                "user": {"login": (r.get("author") or {}).get("login") or ""},
            }
            for r in reviews_nodes
        ]
        checks = self._checks(repo, number, node)

        detail = {
            "number": number,
            "node_id": node.get("id"),
            "title": node.get("title") or "",
            "html_url": node.get("url") or "",
            "state": "open",
            "draft": bool(node.get("isDraft")),
            "updated_at": node.get("updatedAt"),
            "user": {"login": author},
            "assignees": assignees,
            "requested_reviewers": requested_reviewers,
            "base": {"ref": node.get("baseRefName") or ""},
            "head": {"ref": node.get("headRefName") or "", "sha": head},
            # PR-level totals, not a sum over a page of files: authoritative even
            # when a pull request touches more files than one page returns.
            "additions": int(node.get("additions") or 0),
            "deletions": int(node.get("deletions") or 0),
            "changed_files": declared if isinstance(declared, int) else len(files_nodes),
            "review_decision": node.get("reviewDecision") or "",
        }

        packet = dict(detail)
        packet["head"] = {"ref": node.get("headRefName") or "", "sha": head}
        packet["pr_detail"] = detail
        packet["files"] = [f.get("path") for f in files_nodes if f.get("path")]
        packet["additions"] = detail["additions"]
        packet["deletions"] = detail["deletions"]
        packet["reviews_meta"] = reviews
        packet["checks"] = checks
        packet["checks_updated_at"] = _checks_timestamp(checks)
        packet["requested_reviewers"] = requested_reviewers
        return packet

    # -- public API ------------------------------------------------------------

    def queue_inventory(self, repo: str) -> list[dict[str, Any]]:
        """Every open pull request in `repo`, enriched, in one query per page."""
        owner, name = repo.split("/", 1)
        packets: list[dict[str, Any]] = []
        cursor: str | None = None
        pages = 0
        while True:
            pages += 1
            if pages > _PR_PAGE_CAP:
                raise InventoryError(
                    f"more than {_PR_PAGE_CAP * _PR_PAGE_SIZE} open pull requests in {repo}; "
                    "refusing to reconcile an incomplete queue"
                )
            data = self.query(
                "queue_inventory", {"owner": owner, "name": name, "cursor": cursor}
            )
            repository = data.get("repository")
            if not repository:
                raise InventoryError(f"repository {repo} not visible to this token")
            connection = repository.get("pullRequests") or {}
            for node in connection.get("nodes") or []:
                packets.append(self._packet(repo, node))
            page_info = connection.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                return packets
            cursor = page_info.get("endCursor")


def _checks_timestamp(checks: list[dict[str, Any]]) -> str | None:
    """Latest check timestamp across the rollup, or None."""
    stamps = [
        c.get("completed_at") or c.get("submitted_at") or c.get("started_at")
        for c in checks
        if (c.get("completed_at") or c.get("submitted_at") or c.get("started_at"))
    ]
    return max(stamps) if stamps else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Allowlisted GraphQL bulk reads")
    parser.add_argument("--config", default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    p_inventory = sub.add_parser("queue_inventory")
    p_inventory.add_argument("repo")
    args = parser.parse_args(argv)

    config, _ = load_config(args.config)
    state = State(config)
    reader = InventoryReader(config, state)
    try:
        result = reader.queue_inventory(args.repo)
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
