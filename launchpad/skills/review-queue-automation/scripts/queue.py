#!/usr/bin/env python3
"""Deterministic REST queue reconciler: persist open PRs, create jobs, and
supersede older nonterminal jobs when a PR's head changes.

- PR facts are enriched from full REST detail (pr_meta), changed-files, requested
  reviewers, and check-runs: complete file list, summed additions/deletions,
  draft/open state, author, base/head branches, node ID, requested reviewers,
  head SHA, and checks/evidence timestamps. A changed-files read failure is never
  folded into empty safe-looking data: it fails closed.
- Author-triage derives current change-request state from the LATEST substantive
  REST review PER REVIEWER. A dismissed review (state DISMISSED) and a change
  request superseded by the reviewer's newer review do not queue.
- A changed head SHA supersedes every older nonterminal job of the same PR AND
  every related pending human approval request whose head no longer matches.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import approval as approval_mod
from common import State, job_id, load_config, utcnow
from github_rest import RestReader

NONTERMINAL = ("detected", "preflight", "evidence", "assurance", "degraded_draft",
               "adjudication", "approval_evaluation", "would_auto_approve",
               "approval_revalidation", "human_approval_pending", "advisory_action",
               "action", "retryable", "held")


def _latest_substantive_states(pr_reviews: list[dict[str, Any]]) -> list[str]:
    """The latest substantive review state PER REVIEWER.

    GitHub's REST `reviews` list is in submission order (oldest first). For each
    distinct reviewer key keep the newest review; a reviewer's dismissing
    (state DISMISSED) or a later, differing verdict supersedes their earlier
    change request. Returns the surviving states, oldest-reviewer-first.
    """
    latest: dict[str, str] = {}
    for review in pr_reviews:
        author = (review.get("user") or {}).get("login")
        if not author:
            continue
        state = review.get("state") or ""
        if not state:
            continue
        latest[author] = state  # list is chronological; later wins
    return list(latest.values())


def review_requires_changes(pr_reviews: list[dict[str, Any]], _login: str) -> bool:
    """True if any reviewer's latest substantive review is CHANGES_REQUESTED.

    Deliberately independent of any `review_decision` field shipped by the REST
    list payload. DISMISSED and superseded reviews carry no surviving weight.
    """
    return "CHANGES_REQUESTED" in _latest_substantive_states(pr_reviews)


def _own_change_required(pr: dict[str, Any]) -> bool:
    reviews = pr.get("reviews_meta") or []
    return "CHANGES_REQUESTED" in _latest_substantive_states(reviews)


def _checks_timestamps(checks: list[dict[str, Any]]) -> str | None:
    """Latest check/evidence timestamp found across check runs."""
    stamps = [
        r.get("completed_at") or r.get("submitted_at") or r.get("started_at")
        for r in checks
        if (r.get("completed_at") or r.get("submitted_at") or r.get("started_at"))
    ]
    return max(stamps) if stamps else None


def reconcile(config: dict[str, Any], state: State, repo: str) -> dict[str, Any]:
    login = config["login"]
    reader = RestReader(config, state)
    now = utcnow()
    transitions: list[dict[str, Any]] = []
    current_keys: set[tuple[int, str]] = set()
    problems: list[str] = []

    for pr in reader.open_prs(repo):
        number = int(pr["number"])

        # Enrich from the full PR detail (author, branches, draft/open, node_id,
        # base/head refs) so downstream consumers have authoritative facts, not
        # just the truncated list-view entry.
        try:
            detail = reader.pr_meta(repo, number)
        except Exception as exc:
            raise RuntimeError(f"could not enrich PR #{number} meta for {repo}: {exc}") from exc
        head = (detail.get("head") or {}).get("sha") or (pr.get("head") or {}).get("sha")
        if not head:
            raise RuntimeError(f"PR #{number} in {repo} has no head SHA")
        current_keys.add((number, head))

        # Changed files + summed additions/deletions. A read failure is NOT coerced
        # into an empty file list: that would make a later assurance decision look
        # safe when the facts are simply missing. Fail closed instead.
        try:
            changed = reader.changed_files(repo, number)
        except Exception as exc:
            raise RuntimeError(
                f"changed-files read failed for {repo}#{number}; refusing to enrich "
                f"with empty safe-looking facts: {exc}"
            ) from exc
        files = [f.get("filename") for f in changed]
        additions = sum(int(f.get("additions") or 0) for f in changed)
        deletions = sum(int(f.get("deletions") or 0) for f in changed)

        # Requested reviewers + checks (with timestamps for evidence freshness).
        try:
            checks = reader.checks(repo, number)
            requested_reviewers = reader.requested_reviewers(repo, number)
        except Exception as exc:
            raise RuntimeError(f"could not enrich checks/reviewers for {repo}#{number}: {exc}") from exc
        pr["checks"] = checks
        pr["checks_updated_at"] = _checks_timestamps(checks)
        pr["requested_reviewers"] = requested_reviewers

        pr["pr_detail"] = detail
        pr["files"] = files
        pr["additions"] = additions
        pr["deletions"] = deletions
        pr["reviews_meta"] = reader.pr_reviews(repo, number)

        state.execute(
            "INSERT INTO prs(repo,number,head_sha,updated_at,payload,open,last_seen) VALUES(?,?,?,?,?,1,?) "
            "ON CONFLICT(repo,number) DO UPDATE SET head_sha=excluded.head_sha,"
            "updated_at=excluded.updated_at,payload=excluded.payload,open=1,last_seen=excluded.last_seen",
            (repo, number, head, detail.get("updated_at", now), json.dumps(pr), now),
        )
        state._commit()

        author_login = ((detail.get("user")) or {}).get("login") or ((pr.get("user")) or {}).get("login")
        is_own = author_login == login
        lane = "author_triage" if is_own else "incoming_review"
        job = job_id(repo, number, head, lane)
        existing = state.execute("SELECT 1 FROM jobs WHERE id=?", (job,)).fetchone()
        if not existing:
            if is_own:
                if not _own_change_required(pr):
                    continue
                reason = "author PR carries an outstanding change request"
            elif any((a.get("login") if isinstance(a, dict) else a) != login for a in detail.get("assignees", [])):
                continue
            else:
                reason = "unclaimed incoming review"
            state.execute(
                "INSERT INTO jobs(id,repo,number,head_sha,lane,status,reason,artifact_dir,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)",
                (job, repo, number, head, lane, "detected", reason, str(state.job_dir(job)), now, now),
            )
            state._commit()

        # Supersede older nonterminal jobs for the same PR plus any pending review
        # request whose head is stale, when the head changed.
        jobs_superseded = _supersede_old(state, repo, number, head)
        requests_superseded = approval_mod.supersede_for_head(state, repo, number, head)
        if jobs_superseded or requests_superseded:
            transitions.append(
                {"repo": repo, "number": number, "lane": lane, "head_sha": head,
                 "superseded_jobs": jobs_superseded, "superseded_requests": requests_superseded}
            )
        else:
            transitions.append(
                {"repo": repo, "number": number, "lane": lane, "head_sha": head, "status": "detected", "job_id": job}
            )

    state.execute("UPDATE prs SET open=0 WHERE repo=? AND open=1", (repo,))
    for number, head in current_keys:
        state.execute("UPDATE prs SET open=1 WHERE repo=? AND number=?", (repo, number))
    state._commit()

    open_count = state.execute(
        "SELECT COUNT(*) AS n FROM prs WHERE repo=? AND open=1", (repo,)
    ).fetchone()["n"]
    return {"repo": repo, "now": now, "transitions": transitions, "open_count": open_count, "problems": problems}


def _supersede_old(state: State, repo: str, number: int, current_head: str) -> int:
    rows = state.execute(
        "SELECT id, status, head_sha FROM jobs WHERE repo=? AND number=? AND head_sha<>?",
        (repo, number, current_head),
    ).fetchall()
    superseded = 0
    for row in rows:
        if row["status"] not in NONTERMINAL:
            continue
        state.execute(
            "UPDATE jobs SET status='superseded', reason='head changed', updated_at=? WHERE id=?",
            (utcnow(), row["id"]),
        )
        superseded += 1
    state._commit()
    return superseded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REST queue reconciler")
    parser.add_argument("--config", default=None)
    parser.add_argument("repo")
    args = parser.parse_args(argv)

    config, _ = load_config(args.config)
    state = State(config)
    try:
        result = reconcile(config, state, args.repo)
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())