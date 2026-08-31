#!/usr/bin/env python3
"""Answer "why did this PR get this outcome?" from the ledger.

Read-only: reads the local ledger and prints the reconstruction. It never touches
GitHub, never invokes a model, and never changes a job.

Usage:
    explain.py --repo-root <path> job <job-id>
    explain.py --repo-root <path> pr <number> [--repo OWNER/REPO]
    explain.py --repo-root <path> pr <number> --json
"""

from __future__ import annotations

import argparse
import json
import sys

from cli import make_state, resolve_or_onboarding
from ledger import explain, render_explanation, revisions


def _latest_job_for_pr(state, repo: str, number: int) -> str:
    history = revisions(state, repo, number)
    return history[-1]["job_id"] if history else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explain a review outcome from the ledger")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--repo", default="", help="OWNER/REPO (defaults to the configured slug)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="command", required=True)

    job = sub.add_parser("job", help="explain one job")
    job.add_argument("job_id")

    pr = sub.add_parser("pr", help="explain a pull request's latest reviewed revision")
    pr.add_argument("number", type=int)
    pr.add_argument("--all-revisions", action="store_true",
                    help="explain every reviewed revision, oldest first")

    args = parser.parse_args(argv)

    # `resolve_or_onboarding` always returns a 2-tuple; unpack, then test the
    # config (testing the tuple for None never fires).
    config, _ = resolve_or_onboarding(args.repo_root)
    if config is None:
        return 1
    repo = args.repo or (config.get("repository") or {}).get("slug", "")

    state = make_state(config)
    try:
        if args.command == "job":
            job_ids = [args.job_id]
        else:
            if not repo:
                print(json.dumps({"error": "no repository slug configured; pass --repo"}))
                return 1
            history = revisions(state, repo, args.number)
            if not history:
                print(json.dumps({
                    "error": f"no ledger entries for {repo}#{args.number}",
                    "hint": "the PR has not been reviewed by this automation yet",
                }, indent=2))
                return 1
            job_ids = ([h["job_id"] for h in history] if args.all_revisions
                       else [history[-1]["job_id"]])

        reports = [explain(state, job_id) for job_id in job_ids]
        if args.json:
            print(json.dumps(reports if len(reports) > 1 else reports[0],
                             indent=2, sort_keys=True))
        else:
            for report in reports:
                sys.stdout.write(render_explanation(report))
                if len(reports) > 1:
                    sys.stdout.write("\n")
        return 0 if all(r.get("explained") for r in reports) else 1
    finally:
        state.close()


if __name__ == "__main__":
    sys.exit(main())
