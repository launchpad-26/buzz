#!/usr/bin/env python3
"""Probe configured reviewer routes with a canonical smoke review.

A route is only usable if it can (a) be invoked read-only through its adapter and
(b) return a schema-valid reviewer verdict. This script proves both against the
real transport, so onboarding can refuse a route that looks fine in config but
cannot actually produce a verdict.

It is READ-ONLY with respect to GitHub and the repository: it never touches a PR,
never claims a lease, never writes state, and runs each candidate through the same
read-only adapter the panel uses.

Usage:
    route_probe.py --repo-root <path>                  # probe every configured pool
    route_probe.py --runner omp --selector m --effort high
    route_probe.py --repo-root <path> --json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from runners import (  # noqa: E402
    EffortUnsupportedError,
    UnknownRunnerError,
    build_invocation,
)
from verdict import validate_verdict  # noqa: E402

#: A deterministic, self-contained review task. It deliberately carries no repo
#: evidence so the probe measures transport + verdict compliance, nothing else.
SMOKE_PROMPT = (
    "You are reviewing a trivial patch that only fixes a typo in a code comment. "
    "It has no defects. Return ONLY a strict JSON object with exactly these keys: "
    '"signal" (use "SUPPORTED"), "recommendation" (use "clean"), '
    '"summary" (a short non-empty string), "findings" (empty array), '
    '"good" (array with at least one non-empty string), '
    '"missing_evidence" (empty array). '
    "Emit raw JSON only: no markdown code fence, no backticks, and no commentary "
    "before or after the object."
)

OK = "ok"
TRANSPORT_FAILED = "transport_failed"
VERDICT_REJECTED = "verdict_rejected"
TIMEOUT = "timeout"
CONFIG_ERROR = "config_error"


def probe_route(
    entry: dict[str, Any],
    effort: str,
    *,
    repo_path: str,
    timeout: int = 300,
) -> dict[str, Any]:
    """Run one candidate and classify the outcome. Never raises."""
    label = f"{entry.get('runner')}:{entry.get('selector')}"
    try:
        invocation = build_invocation(entry, SMOKE_PROMPT, effort, repo_path)
    except (UnknownRunnerError, EffortUnsupportedError) as exc:
        return {"route": label, "status": CONFIG_ERROR, "detail": str(exc)}

    started = time.time()
    try:
        proc = subprocess.run(
            list(invocation.cmd), capture_output=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {
            "route": label, "status": TIMEOUT,
            "detail": f"no response within {timeout}s",
            "effort_enforced": invocation.effort_enforced,
        }
    except OSError as exc:  # binary missing / not executable
        return {"route": label, "status": TRANSPORT_FAILED, "detail": str(exc)}

    elapsed = round(time.time() - started, 1)
    result: dict[str, Any] = {
        "route": label,
        "effort": effort,
        "effort_enforced": invocation.effort_enforced,
        "read_only_proof": list(invocation.read_only_proof),
        "elapsed_seconds": elapsed,
    }

    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        result.update({"status": TRANSPORT_FAILED,
                       "detail": f"exit {proc.returncode}: {stderr[:300]}"})
        return result

    stdout = (proc.stdout or b"").decode("utf-8", errors="replace")
    ok, issues = validate_verdict(stdout)
    if not ok:
        result.update({"status": VERDICT_REJECTED, "detail": "; ".join(issues)[:300]})
        return result

    result["status"] = OK
    return result


def _entries_from_config(config: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
    """Flatten configured pools into (entry, effort) probe targets."""
    targets: list[tuple[dict[str, Any], str]] = []
    models = config.get("models") or {}
    for pool in ("primary", "secondary"):
        for entry in models.get(pool) or []:
            efforts = entry.get("efforts") or ["medium"]
            # Probe the cheapest declared effort: it proves the route, not the ceiling.
            targets.append((entry, efforts[0]))
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe reviewer routes with a smoke review")
    parser.add_argument("--repo-root", help="probe every route configured for this repo")
    parser.add_argument("--runner", help="probe a single explicit runner")
    parser.add_argument("--selector", help="model selector for --runner")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    repo_path = args.repo_root or "/tmp"
    targets: list[tuple[dict[str, Any], str]] = []

    if args.runner:
        if not args.selector:
            parser.error("--runner requires --selector")
        targets = [({"runner": args.runner, "selector": args.selector}, args.effort)]
    elif args.repo_root:
        from config import load_repo_config

        config, cfg_path, issues = load_repo_config(args.repo_root)
        if config is None:
            print(json.dumps({"status": "config_unusable", "config": str(cfg_path),
                              "issues": issues}, indent=2))
            return 1
        targets = _entries_from_config(config)
        if not targets:
            print(json.dumps({
                "status": "no_routes_configured",
                "detail": "models.primary and models.secondary are both empty; "
                          "the repo is not runtime-ready",
            }, indent=2))
            return 1
    else:
        parser.error("pass --repo-root or --runner/--selector")

    results = [probe_route(entry, effort, repo_path=repo_path, timeout=args.timeout)
               for entry, effort in targets]
    usable = [r for r in results if r["status"] == OK]

    report = {
        "probed": len(results),
        "usable": len(usable),
        "all_usable": len(usable) == len(results),
        "results": results,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for r in results:
            mark = "PASS" if r["status"] == OK else "FAIL"
            extra = "" if r["status"] == OK else f" — {r.get('detail', '')}"
            enforced = r.get("effort_enforced")
            note = "" if enforced in (None, True) else " [effort not enforced by transport]"
            print(f"{mark}  {r['route']}  ({r['status']}){note}{extra}")
        print(f"\n{len(usable)}/{len(results)} route(s) usable")

    return 0 if report["all_usable"] and usable else 1


if __name__ == "__main__":
    sys.exit(main())
