#!/usr/bin/env python3
"""Collect an immutable evidence bundle for one PR: PR meta, reviews, comments, files,
linked issue, checks, and a local repository context manifest. REST reads only."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from common import State, atomic_write, load_config, nonce_envelope, utcnow
from errors import EvidenceIncompleteError
from github_rest import RestReader

LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.IGNORECASE)

#: Canonical evidence artifact names. The panel and dispatcher read exactly these
#: names, so every writer in this module must use the same contract:
EVIDENCE_JSON = "evidence.json"
EVIDENCE_TXT = "evidence.txt"
CONTEXT_JSON = "context.json"


def collect(
    config: dict[str, Any],
    state: State,
    repo: str,
    number: int,
    lane: str,
    job: str,
) -> dict[str, Any]:
    reader = RestReader(config, state)
    artifact_dir = state.job_dir(job)

    pr = reader.pr_meta(repo, number)
    if not isinstance(pr, dict) or not pr:
        raise EvidenceIncompleteError(f"evidence for {repo}/#{number}: empty PR meta; failing closed")
    head = (pr.get("head") or {}).get("sha") or ""
    if not head:
        raise EvidenceIncompleteError(f"evidence for {repo}/{number} missing head SHA; failing closed")

    reviews = reader.pr_reviews(repo, number)
    review_comments = reader.review_comments(repo, number)
    issue_comments = reader.issue_comments(repo, number)
    files = reader.changed_files(repo, number)
    checks = reader.checks(repo, number)
    if checks is None:
        raise EvidenceIncompleteError(f"evidence for {repo}/{number} has no check-runs; failing closed")

    linked_number = None
    match = LINK_RE.search(pr.get("body") or "")
    if match:
        linked_number = int(match.group(1))

    linked: dict[str, Any] = {}
    if linked_number:
        try:
            linked["issue"] = reader.issue(repo, linked_number)
            linked["comments"] = reader.issue_comments(repo, linked_number)
        except RuntimeError as exc:
            linked["error"] = str(exc)

    context = {
        "repo": repo,
        "number": number,
        "head": head,
        "base": (pr.get("base") or {}).get("ref", ""),
        "head_ref": (pr.get("head") or {}).get("ref", ""),
        "author": (pr.get("user") or {}).get("login", ""),
        "draft": pr.get("draft", False),
        "review_decision": pr.get("review_decision"),
        "linked_issue": linked_number,
        "repo_path": config["repos"].get(repo, {}).get("path"),
        "dco": config["repos"].get(repo, {}).get("dco", True),
    }

    artifact = {
        "pr": pr,
        "reviews": reviews,
        "review_comments": review_comments,
        "issue_comments": issue_comments,
        "files": files,
        "checks": checks,
        "linked": linked,
        "context": context,
        "collected_at": utcnow(),
    }
    artifact_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(artifact_dir / EVIDENCE_JSON, json.dumps(artifact, indent=2, sort_keys=True))

    nonce = job
    envelope = "\n".join(
        [
            f"Repository {repo} PR #{number} (head {head}); lane {lane}; job {job}",
            "",
            nonce_envelope("pr_meta", pr, nonce),
            "",
            nonce_envelope("reviews", reviews, nonce),
            "",
            nonce_envelope("review_comments", review_comments, nonce),
            "",
            nonce_envelope("issue_comments", issue_comments, nonce),
            "",
            nonce_envelope("changed_files", [f.get("filename") for f in files], nonce),
        ]
        + (
            [
                "",
                nonce_envelope("linked_issue", linked.get("issue", {}), nonce),
                "",
                nonce_envelope("linked_issue_comments", linked.get("comments", []), nonce),
            ]
            if linked
            else []
        )
        + [
            "",
            nonce_envelope("checks_context", checks, nonce),
            "",
            f"Repo path for local verification: {context['repo_path']}",
        ]
    )
    atomic_write(artifact_dir / EVIDENCE_TXT, envelope)
    atomic_write(artifact_dir / CONTEXT_JSON, json.dumps(context, indent=2, sort_keys=True))

    return {"job": job, "repo": repo, "number": number, "lane": lane, "head": head, "artifact_dir": str(artifact_dir)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect evidence for one PR")
    parser.add_argument("--config", default=None)
    parser.add_argument("repo")
    parser.add_argument("number", type=int)
    parser.add_argument("--lane", default="incoming_review")
    parser.add_argument("--job", required=True)
    args = parser.parse_args(argv)

    config, _ = load_config(args.config)
    state = State(config)
    try:
        result = collect(config, state, args.repo, args.number, args.lane, args.job)
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())