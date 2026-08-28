#!/usr/bin/env python3
"""Ingest real closed pull requests into historical calibration samples.

Shadow calibration needs past revisions plus an outcome label that was NOT
produced by the thing being calibrated. This module builds those samples from the
repository's own closed PRs using only allowlisted REST reads.

Outcome labelling is deliberately independent of the evaluator:

    contested  a human requested changes before the PR was merged
    adverse    the PR was reverted afterwards, or closed unmerged after review
    clean      merged with review activity and no changes ever requested
    unknown    merged with no review signal at all, so it proves nothing

`clean` is asserted only when there is positive review evidence. A PR that nobody
reviewed is `unknown`, never `clean`: absence of objection is not approval, and
treating it as approval would inflate the measured would-approve accuracy.

Read-only: no mutations, no lease, no model calls.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

CONTESTED = "contested"
ADVERSE = "adverse"
CLEAN = "clean"
UNKNOWN = "unknown"

#: A later PR whose title reverts an earlier one, e.g. 'Revert "fix: thing" (#123)'
_REVERT = re.compile(r"^\s*revert\b", re.IGNORECASE)
_REVERT_NUMBER = re.compile(r"#(\d+)")


def _reverted_numbers(closed: list[dict[str, Any]]) -> set[int]:
    """PR numbers that a later revert PR names in its title."""
    reverted: set[int] = set()
    for pr in closed:
        title = pr.get("title") or ""
        if not _REVERT.match(title):
            continue
        for match in _REVERT_NUMBER.findall(title):
            try:
                reverted.add(int(match))
            except ValueError:
                continue
    return reverted


def classify_outcome(
    pr: dict[str, Any],
    reviews: list[dict[str, Any]],
    *,
    reverted: set[int],
    self_login: str = "",
) -> tuple[str, str]:
    """Return (outcome, evidence_source), independent of any evaluator decision."""
    number = pr.get("number")
    merged = bool(pr.get("merged_at"))

    if number in reverted:
        return ADVERSE, "later revert PR names this number"

    human_reviews = [
        r for r in reviews
        if (r.get("user") or {}).get("login") and (r.get("user") or {}).get("login") != self_login
    ]
    states = {(r.get("state") or "").upper() for r in human_reviews}

    if "CHANGES_REQUESTED" in states:
        return CONTESTED, "a human requested changes before merge"

    if not merged:
        if human_reviews:
            return ADVERSE, "closed unmerged after human review"
        return UNKNOWN, "closed unmerged with no review signal"

    if "APPROVED" in states:
        return CLEAN, "merged after human approval with no changes requested"
    if human_reviews:
        return CLEAN, "merged after human review comments with no changes requested"

    # Merged with nobody reviewing proves nothing about correctness.
    return UNKNOWN, "merged with no human review signal"


def _timestamps(
    pr: dict[str, Any],
    reviews: list[dict[str, Any]],
    checks_ok_at: str | None = None,
) -> dict[str, Any]:
    """Evidence timestamps, all strictly at-or-before the merge cutoff.

    The cutoff is the merge (or close) time. Evidence only counts when it
    demonstrably existed by then, so a backtest cannot use hindsight.

    `pr.updated_at` is deliberately NOT used as evidence: merging the PR updates
    it, so it usually lands AFTER the cutoff and would make every sample look
    stale. Instead we take the latest timestamp that provably predates the cutoff
    among the PR's creation, its reviews, and its green-check completion.
    """
    cutoff = pr.get("merged_at") or pr.get("closed_at") or ""
    at_or_before = lambda ts: bool(ts) and bool(cutoff) and ts <= cutoff  # noqa: E731

    review_times = sorted(r.get("submitted_at") for r in reviews if r.get("submitted_at"))
    first_review = review_times[0] if review_times else None

    candidates = [ts for ts in (
        pr.get("created_at"),
        review_times[-1] if review_times else None,
        checks_ok_at,
    ) if at_or_before(ts)]

    return {
        "cutoff": cutoff,
        # Adjudication evidence: the first human review at-or-before the cutoff.
        "adjudication_at": first_review if at_or_before(first_review) else None,
        # Evidence freshness: the most recent thing we can PROVE existed pre-merge.
        "evidence_at": max(candidates) if candidates else None,
    }


def build_entry(
    repo: str,
    pr: dict[str, Any],
    reviews: list[dict[str, Any]],
    files: list[str],
    *,
    reverted: set[int],
    self_login: str = "",
    checks_ok_at: str | None = None,
) -> dict[str, Any]:
    """One `shadow.build_sample`-compatible entry for a single closed PR."""
    outcome, source = classify_outcome(pr, reviews, reverted=reverted, self_login=self_login)
    stamps = _timestamps(pr, reviews, checks_ok_at)
    head = (pr.get("head") or {}).get("sha", "")
    return {
        "repo": repo,
        "number": pr.get("number"),
        "head_sha": head,
        "merged_at": pr.get("merged_at") or "",
        "outcome": outcome,
        "evidence_source": source,
        "cutoff": stamps["cutoff"],
        # Checks evidence is not available from the PR list endpoint; left None
        # (fail-closed) unless a caller supplies it from a check-runs read.
        "checks_ok_at": checks_ok_at,
        "adjudication_at": stamps["adjudication_at"],
        "evidence_at": stamps["evidence_at"],
        # A CLOSED pull request's head SHA cannot advance, so the close/merge
        # time is the moment the head became final. `shadow.historical_evidence`
        # uses this in place of the live pre-mutation REST revalidation the
        # backtest cannot replay; an entry without it fails that gate closed.
        "head_frozen_at": stamps["cutoff"] or None,
        "files": files,
        "additions": int(pr.get("additions") or 0),
        "pr_facts": {
            "author_login": (pr.get("user") or {}).get("login", ""),
            "complexity": 0,
            "title": (pr.get("title") or "")[:200],
        },
    }


def checks_ok_timestamp(checks: list[dict[str, Any]]) -> str | None:
    """When every completed check had succeeded, or None.

    Returns the LATEST completion time among successful checks, so the backtest
    can require that check evidence existed at-or-before the cutoff. Any check that
    did not succeed, or has no completion time, makes this None (fail-closed):
    partial green is not green.
    """
    if not checks:
        return None
    latest = ""
    for check in checks:
        if not isinstance(check, dict):
            return None
        status = (check.get("status") or "").lower()
        conclusion = (check.get("conclusion") or "").upper()
        # A still-running check means we cannot assert the suite was green.
        if status and status != "completed":
            return None
        if conclusion not in ("SUCCESS", "NEUTRAL", "SKIPPED"):
            return None
        completed = check.get("completed_at") or ""
        if not completed:
            return None
        latest = max(latest, completed)
    return latest or None


def ingest(
    config: dict[str, Any],
    state,
    repo: str,
    *,
    limit: int = 50,
    with_files: bool = False,
    with_checks: bool = False,
    self_login: str = "",
) -> dict[str, Any]:
    """Fetch closed PRs and build calibration entries.

    `with_files` and `with_checks` each cost one extra REST call per PR. Without
    them the corresponding gates stay fail-closed, which is reported rather than
    silently assumed: a backtest with no check evidence can only ever produce a 0%
    would-approve rate, and that must not be mistaken for a safety result.
    """
    from github_rest import RestReader

    reader = RestReader(config, state)
    closed = reader.closed_prs(repo)
    reverted = _reverted_numbers(closed)

    entries: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for pr in closed[:limit]:
        number = pr.get("number")
        head = (pr.get("head") or {}).get("sha", "")
        if not number or not head:
            skipped.append({"number": number, "reason": "missing number or head sha"})
            continue
        try:
            reviews = reader.pr_reviews(repo, number)
        except Exception as exc:
            skipped.append({"number": number, "reason": f"reviews unreadable: {exc}"})
            continue
        files: list[str] = []
        if with_files:
            try:
                files = [
                    f.get("filename", "") for f in reader.changed_files(repo, number)
                    if isinstance(f, dict)
                ]
            except Exception as exc:
                skipped.append({"number": number, "reason": f"files unreadable: {exc}"})
        checks_at: str | None = None
        if with_checks:
            try:
                checks_at = checks_ok_timestamp(reader.checks(repo, number))
            except Exception as exc:
                skipped.append({"number": number, "reason": f"checks unreadable: {exc}"})
        entries.append(build_entry(
            repo, pr, reviews, files, reverted=reverted, self_login=self_login,
            checks_ok_at=checks_at,
        ))

    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["outcome"]] = counts.get(entry["outcome"], 0) + 1

    return {
        "repo": repo,
        "closed_seen": len(closed),
        "ingested": len(entries),
        "skipped": skipped,
        "outcome_counts": counts,
        "files_included": with_files,
        "checks_included": with_checks,
        "entries": entries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest closed PRs as calibration samples")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--repo", help="OWNER/REPO (defaults to the configured slug)")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--with-files", action="store_true",
                        help="also read changed files (one extra REST call per PR). "
                             "Without it no protected-trigger or file-limit "
                             "evidence exists for any sample")
    parser.add_argument("--with-checks", action="store_true",
                        help="also read check runs (one extra REST call per PR). "
                             "WITHOUT this flag no check evidence is ingested and "
                             "the checks_complete_ok gate stays fail-closed for "
                             "every sample, so the backtest can only ever report a "
                             "0%% would-approve rate")
    parser.add_argument("--out", help="write entries here instead of stdout")
    args = parser.parse_args(argv)

    from cli import make_state, resolve_or_onboarding

    config, _ = resolve_or_onboarding(args.repo_root)
    if config is None:
        return 1
    repo = args.repo or (config.get("repository") or {}).get("slug", "")
    if not repo:
        print(json.dumps({"error": "no repository slug configured; pass --repo"}))
        return 1

    state = make_state(config)
    try:
        report = ingest(
            config, state, repo,
            limit=args.limit, with_files=args.with_files,
            with_checks=args.with_checks,
            self_login=config.get("login", ""),
        )
    finally:
        state.close()

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(report["entries"], handle, indent=2, sort_keys=True)
        summary = {k: v for k, v in report.items() if k != "entries"}
        summary["out"] = args.out
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
