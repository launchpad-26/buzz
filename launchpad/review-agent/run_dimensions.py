"""The concurrent dimension runner. Implements launchpad-26/buzz#117 STEP 3.

Given a pull request (live, or a captured ``--payload``), this module:

1. Resolves the commit pair the review reads (``merge_base_sha``, ``head_sha``) --
   this module's own job; neither ``fetch.py`` nor ``contain.py`` does it.
2. Fetches the seven author-controlled surfaces (``fetch.fetch_all`` or
   ``fetch.from_payload``), applying any ``--degrade`` overrides.
3. Mints a run nonce (``contain.make_nonce``, random unless ``--seed`` is given).
4. Calls ``contain.render(surfaces, nonce)`` -- the single, mandatory containment
   step CONTAINMENT.md's "Contract for later stages" table binds this stage to.
5. Runs one reviewer call per dimension **concurrently**
   (``concurrent.futures.ThreadPoolExecutor``), each given the rendered, contained
   document as its input, under a per-dimension timeout.
6. Prints one merged JSON document to stdout, per FINDINGS.md's "The merged
   document" section.

The three dimension prompt files (STEP 4) do not exist yet. This module is
demonstrable without them: the reviewer is an **injected callable**, defaulting to
a clean stub, and ``--list``/dimension discovery reads ``dimensions/*.py`` off
disk rather than a hardcoded name list -- so STEP 4 only has to add files there,
never touch this module.

Design decisions this task made where FINDINGS.md/the plan left room (see the
STEP 3 task report for the full reasoning):

* **Reviewer signature: ``Callable[[str], dict | str]``, called as
  ``reviewer(document)``.** It returns (or, if a JSON string, decodes to) a
  partial report -- at minimum ``{"outcome": ..., "findings": [...]}`` -- never
  the full envelope. This runner is the sole authority for every structural
  envelope field (``schema_version``, ``dimension``, ``pr``, ``merge_base_sha``,
  ``head_sha``, ``completion_marker``): a reviewer's output is untrusted content,
  and letting it also dictate its own identity/marker fields would let a broken or
  malicious reviewer forge them. The runner always assembles those itself from the
  run's own known-good values.
* **Failure classification (point 6 of the task brief) is implemented by wrapping
  the assembled single-dimension report in a minimal one-report merged document
  and running it through ``findings.validate()`` unmodified** -- the same
  validator every other stage trusts, rather than a second, parallel notion of
  "well-formed".
* **Exit codes** (none of these are pinned by FINDINGS.md, so they are this
  module's own contract, documented here): ``0`` clean run, every report
  ``status: "complete"``; ``1`` at least one dimension ``status: "failed"``
  (the merged document is still printed); ``2`` infrastructure error (bad/expired
  credential, network failure, unexpected probe response) -- no document is
  printed; ``3`` no such pull request; ``4`` credential is live but blocked from
  reading this specific pull request (not rate-limited -- that is ``2``).
* **``--payload`` commit pair.** A captured payload has no live commit pair to
  resolve (CONTAINMENT.md's compare-API call needs a real PR). ``merge_base_sha``/
  ``head_sha`` are read from the payload JSON's own ``merge_base_sha``/``head_sha``
  keys when present (harmless extra keys -- ``fetch.from_payload`` ignores
  anything outside ``contain.ENTRY_POINTS``), else default to ``"0" * 40``. The
  positional ``pr`` argument is optional with ``--payload`` and defaults to ``0``.
* **Per-dimension timeout default:** 120 seconds -- generous for a real model
  call once STEP 4 lands; every test in ``test_run_dimensions.py`` overrides it
  with a short value.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

import contain
import fetch
import findings

#: Where STEP 4 will add one .py file per dimension. --list and dimension
#: discovery both read this directory; nothing in this module hardcodes the
#: three slugs that will eventually live here.
DIMENSIONS_DIR = Path(__file__).parent / "dimensions"

#: Seconds. See the module docstring's "Design decisions" for why this value.
DEFAULT_TIMEOUT = 120.0

#: Exit codes. See the module docstring's "Design decisions" for the rationale.
EXIT_OK = 0
EXIT_DIMENSION_FAILED = 1
EXIT_INFRASTRUCTURE = 2
EXIT_NO_SUCH_PR = 3
EXIT_BLOCKED = 4

Reviewer = Callable[[str], object]

_DUMMY_SHA = "0" * 40


# ---------------------------------------------------------------------------
# Dimension discovery
# ---------------------------------------------------------------------------


def list_dimensions(dimensions_dir: Path | None = None) -> list[str]:
    """Dimension slugs on disk, sorted for deterministic ``--list`` output.

    A missing directory (true today -- STEP 4 has not run yet) is an empty list,
    not an error: ``--list`` must work before a single dimension file exists.
    """
    directory = dimensions_dir if dimensions_dir is not None else DIMENSIONS_DIR
    if not directory.is_dir():
        return []
    return sorted(p.stem for p in directory.glob("*.py"))


# ---------------------------------------------------------------------------
# Default (stub) reviewer
# ---------------------------------------------------------------------------


def default_reviewer(document: str) -> dict:
    """The clean stub: every dimension reports no findings. See module docstring."""
    return {"outcome": "clean", "findings": []}


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def _completion_marker(dimension: str, nonce: str) -> str:
    return f"BUZZ-DIMENSION-COMPLETE:{dimension}:{nonce}"


def _failed_report(
    dimension: str, pr: int, merge_base_sha: str, head_sha: str, nonce: str, reason: str
) -> dict:
    """A ``status: failed`` report. Still carries a valid, last-key completion
    marker: ``findings.validate()`` checks the marker on every report regardless
    of status, and a marker-less failed report would itself be a validation
    violation on top of the failure it is meant to report cleanly.
    """
    return {
        "schema_version": 1,
        "dimension": dimension,
        "pr": pr,
        "merge_base_sha": merge_base_sha,
        "head_sha": head_sha,
        "status": "failed",
        "outcome": None,
        "error": {"reason": reason},
        "findings": [],
        "findings_count": 0,
        "completion_marker": _completion_marker(dimension, nonce),
    }


def _validate_single_report(report: dict, nonce: str) -> list[str]:
    """Run one assembled report through the real ``findings.validate()``.

    Wraps it as the sole entry of a minimal, otherwise-correct merged document --
    correct ``containment`` (all seven entry points marked "ok", no findings) and
    a matching top-level ``nonce`` -- so every violation ``validate()`` returns is
    about the report itself, never about the wrapper's own shape.
    """
    wrapper = {
        "pr": report["pr"],
        "merge_base_sha": report["merge_base_sha"],
        "head_sha": report["head_sha"],
        "reports": [report],
        "containment": {
            "findings": [],
            "states": {ep: "ok" for ep in contain.ENTRY_POINTS},
        },
        "nonce": nonce,
    }
    return findings.validate(wrapper)


def _collect_report(
    dimension: str,
    future: concurrent.futures.Future,
    timeout: float,
    pr: int,
    merge_base_sha: str,
    head_sha: str,
    nonce: str,
) -> dict:
    """Turn one reviewer call's outcome into a spec-compliant report.

    Three failure triggers, per the task brief: the call raises, it times out, or
    its (parsed) output fails ``findings.validate()`` on the assembled report.
    None of them crash this function or the run as a whole.
    """
    try:
        raw = future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        return _failed_report(
            dimension, pr, merge_base_sha, head_sha, nonce,
            f"reviewer timed out after {timeout}s",
        )
    except Exception as exc:  # noqa: BLE001 - the reviewer's own call raised
        return _failed_report(
            dimension, pr, merge_base_sha, head_sha, nonce,
            f"reviewer raised {type(exc).__name__}: {exc}",
        )

    content = raw
    if isinstance(raw, str):
        try:
            content = json.loads(raw)
        except json.JSONDecodeError as exc:
            return _failed_report(
                dimension, pr, merge_base_sha, head_sha, nonce,
                f"reviewer output is not valid JSON: {exc}",
            )

    if not isinstance(content, dict):
        return _failed_report(
            dimension, pr, merge_base_sha, head_sha, nonce,
            f"reviewer output must be an object, got {type(content).__name__}",
        )

    findings_list = content.get("findings", [])
    if not isinstance(findings_list, list):
        return _failed_report(
            dimension, pr, merge_base_sha, head_sha, nonce,
            f"reviewer 'findings' must be an array, got {type(findings_list).__name__}",
        )

    report = {
        "schema_version": 1,
        "dimension": dimension,
        "pr": pr,
        "merge_base_sha": merge_base_sha,
        "head_sha": head_sha,
        "status": "complete",
        "outcome": content.get("outcome"),
        "error": None,
        "findings": findings_list,
        "findings_count": len(findings_list),
        "completion_marker": _completion_marker(dimension, nonce),
    }

    violations = _validate_single_report(report, nonce)
    if violations:
        return _failed_report(
            dimension, pr, merge_base_sha, head_sha, nonce,
            "reviewer output failed findings.validate(): " + "; ".join(violations),
        )
    return report


def _run_dimensions_concurrently(
    dimensions: list[str],
    document: str,
    reviewer: Reviewer,
    timeout: float,
    pr: int,
    merge_base_sha: str,
    head_sha: str,
    nonce: str,
) -> list[dict]:
    """One reviewer call per dimension, all started before any is awaited.

    ``executor.shutdown(wait=False)`` on the way out, deliberately, not the
    context-manager form: ``ThreadPoolExecutor.__exit__`` calls
    ``shutdown(wait=True)``, which blocks until every submitted call returns --
    including one this function has already given up on via
    ``future.result(timeout=...)``. That would make a single hung reviewer block
    the whole run for as long as it takes that call to finish (or forever), which
    is exactly the "not hanging" property a per-dimension timeout exists to give.
    A thread that outlives its timeout is abandoned, not cancelled -- Python
    cannot forcibly stop a running thread -- but abandoning it costs this
    function nothing further.
    """
    if not dimensions:
        return []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(dimensions))
    try:
        futures = [executor.submit(reviewer, document) for _ in dimensions]
        return [
            _collect_report(dim, fut, timeout, pr, merge_base_sha, head_sha, nonce)
            for dim, fut in zip(dimensions, futures)
        ]
    finally:
        executor.shutdown(wait=False)


# ---------------------------------------------------------------------------
# The core, testable entry point
# ---------------------------------------------------------------------------


def build_document(
    pr: int,
    merge_base_sha: str,
    head_sha: str,
    surfaces: dict,
    dimensions: list[str],
    nonce: str,
    reviewer: Reviewer = default_reviewer,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """Build the merged document for one run. No subprocess, no network.

    ``dimensions`` is an explicit parameter precisely so this function is
    testable without ``dimensions/`` existing on disk yet -- ``main()`` below is
    the only caller that populates it from ``list_dimensions()``.
    """
    document, containment_findings, _all_readable, states = contain.render(surfaces, nonce)

    reports = _run_dimensions_concurrently(
        dimensions, document, reviewer, timeout, pr, merge_base_sha, head_sha, nonce
    )

    return {
        "pr": pr,
        "merge_base_sha": merge_base_sha,
        "head_sha": head_sha,
        "reports": reports,
        "containment": {
            "findings": [f.as_dict() for f in containment_findings],
            "states": states,
        },
        "nonce": nonce,
    }


# ---------------------------------------------------------------------------
# Credential / PR-existence identity probe -- pure classification functions
# ---------------------------------------------------------------------------


def classify_user_probe(status: int | None, message: str) -> tuple[str, str]:
    """Classify a ``GET /user`` response. Returns ``(outcome, reason)``.

    ``outcome`` is ``"live"`` (proceed) or ``"infrastructure"`` (terminal). Pure:
    takes an HTTP-response-like ``(status, message)`` pair, no subprocess, so it
    is directly unit-testable against every case the task brief's classification
    table names. ``status=None`` is the network-error/timeout case.
    """
    if status is None:
        return "infrastructure", f"network error probing /user: {message}"
    if status == 200:
        return "live", ""
    if status == 403 and message == "Resource not accessible by integration":
        # The installation/Actions-token credential's normal 403 shape on /user
        # (ADR #110) -- this IS the expected live CI credential, not a failure.
        return "live", "installation-token 403 on /user (ADR #110); treated as live"
    if status == 403:
        return "infrastructure", f"/user returned 403 with an unexpected message: {message!r}"
    if status == 401:
        return "infrastructure", "/user returned 401 (bad credentials)"
    return "infrastructure", f"/user returned unexpected status {status}: {message!r}"


def classify_pr_probe(
    status: int | None, message: str, rate_limit_remaining: int | None = None
) -> tuple[str, str]:
    """Classify a ``GET /repos/{owner}/{repo}/pulls/{n}`` response.

    ``outcome`` is one of ``"live"`` (proceed), ``"no_such_pr"``, ``"blocked"``, or
    ``"infrastructure"`` -- four distinct terminal-or-proceed outcomes, each with
    its own reason string, per the task brief's requirement that a 401 is never
    classifiable as anything but infrastructure and a rate-limited 403 is never
    folded into "blocked".
    """
    if status is None:
        return "infrastructure", f"network error probing the pull request: {message}"
    if status == 200:
        return "live", ""
    if status == 404:
        # This repo (launchpad-26/buzz) is public: a live credential can read any
        # PR of a public repo, so a 404 here genuinely means "no such PR" and is
        # never generalised to a private repo.
        return "no_such_pr", f"pull request not found: {message!r}"
    if status == 403:
        if rate_limit_remaining == 0:
            return "infrastructure", "rate-limited (x-ratelimit-remaining: 0) fetching the pull request"
        return "blocked", f"credential is live but blocked from this pull request: {message!r}"
    if status == 401:
        return "infrastructure", "credential died between the /user and pull-request probes (401)"
    return "infrastructure", f"pull request probe returned unexpected status {status}: {message!r}"


# ---------------------------------------------------------------------------
# gh-backed HTTP calls -- the only place this module shells out
# ---------------------------------------------------------------------------

_STATUS_LINE = re.compile(r"^HTTP/[\d.]+\s+(\d{3})")
_RATE_LIMIT_HEADER = re.compile(r"^x-ratelimit-remaining:\s*(\d+)", re.IGNORECASE | re.MULTILINE)


def _parse_status_line(output: str) -> int | None:
    first_line = output.split("\n", 1)[0]
    match = _STATUS_LINE.match(first_line.strip())
    return int(match.group(1)) if match else None


def _split_header_block(output: str) -> tuple[str, str]:
    for sep in ("\r\n\r\n", "\n\n"):
        if sep in output:
            head, _, body = output.partition(sep)
            return head, body
    return output, ""


def _http_probe(path: str) -> tuple[int | None, str, int | None]:
    """One GET via ``gh api --include``, decoded to ``(status, message, rate_limit_remaining)``.

    Never raises: a missing ``gh``, a timeout, or any other subprocess-level
    failure all fold into ``status=None`` so ``classify_user_probe``/
    ``classify_pr_probe`` stay pure functions of already-decoded values, and this
    is the only place a real network/subprocess call happens for the identity
    probe.
    """
    try:
        proc = subprocess.run(["gh", "api", path, "--include"], capture_output=True, timeout=30)
    except FileNotFoundError:
        return None, "gh is not installed", None
    except subprocess.TimeoutExpired:
        return None, "gh timed out after 30s", None

    output = proc.stdout.decode("utf-8", "replace")
    status = _parse_status_line(output)
    if status is None:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        return None, detail or "gh produced no parseable HTTP status line", None

    header_block, body = _split_header_block(output)
    rate_limit_match = _RATE_LIMIT_HEADER.search(header_block)
    rate_limit_remaining = int(rate_limit_match.group(1)) if rate_limit_match else None

    message = ""
    if status >= 400:
        try:
            message = json.loads(body).get("message", "") if body.strip() else ""
        except (json.JSONDecodeError, AttributeError):
            message = body.strip()
    return status, message, rate_limit_remaining


def probe_credential_and_pr(repo: str, pr: int) -> tuple[str, str]:
    """The full two-call identity probe. Returns ``(outcome, reason)``.

    ``"live"`` is the only outcome that means proceed; every other value is
    terminal. See ``classify_user_probe``/``classify_pr_probe`` for the per-call
    classification and ``main()`` for how each outcome maps to an exit code.
    """
    status, message, _ = _http_probe("user")
    outcome, reason = classify_user_probe(status, message)
    if outcome != "live":
        return outcome, reason

    status, message, rate_limit_remaining = _http_probe(f"repos/{repo}/pulls/{pr}")
    return classify_pr_probe(status, message, rate_limit_remaining)


def _gh_api_json(path: str) -> dict:
    """A ``gh api`` call expected to succeed -- raises ``RuntimeError`` on failure.

    Only called after ``probe_credential_and_pr`` has already established a live,
    permitted credential and an existing PR, so a failure here is a fresh,
    unclassified fault (not one this module tries to re-slot into the identity
    probe's outcome table a second time).
    """
    try:
        proc = subprocess.run(["gh", "api", path], capture_output=True, timeout=30)
    except FileNotFoundError as exc:
        raise RuntimeError("gh is not installed") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"gh timed out after 30s calling {path}") from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"gh api {path} failed: {detail}")
    return json.loads(proc.stdout.decode("utf-8"))


def resolve_commit_pair(repo: str, pr: int) -> tuple[str, str]:
    """``(merge_base_sha, head_sha)`` for a live PR. Two REST calls, never GraphQL.

    ``fetch.fetch_all``/the PR JSON ``fetch.py`` narrows down never carry a
    merge-base SHA. The PR JSON's own ``base.sha`` is the base branch's CURRENT
    tip, not the commit the head forked from -- diffing against it would
    attribute every commit landed on the base branch since the fork point to this
    PR's own diff. ``compare``'s ``merge_base_commit.sha`` is the actual fork
    point, so that is what is read here.
    """
    pr_json = _gh_api_json(f"repos/{repo}/pulls/{pr}")
    base_ref = pr_json["base"]["ref"]
    head_ref = pr_json["head"]["ref"]
    head_sha = pr_json["head"]["sha"]
    compare_json = _gh_api_json(f"repos/{repo}/compare/{base_ref}...{head_ref}")
    merge_base_sha = compare_json["merge_base_commit"]["sha"]
    return merge_base_sha, head_sha


# ---------------------------------------------------------------------------
# --payload mode's own (network-free) commit pair
# ---------------------------------------------------------------------------


def _payload_commit_pair(path: str) -> tuple[str, str]:
    """A captured payload has no live commit pair. Read it from the payload's own
    ``merge_base_sha``/``head_sha`` keys when present, else a fixed dummy value.

    ``fetch.from_payload`` only reads ``contain.ENTRY_POINTS`` keys and silently
    ignores the rest, so these two extra keys cost it nothing.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return _DUMMY_SHA, _DUMMY_SHA
    return raw.get("merge_base_sha", _DUMMY_SHA), raw.get("head_sha", _DUMMY_SHA)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_dimensions.py",
        description=(
            "Run the review agent's dimension reviewers concurrently over a "
            "contained pull request document. See FINDINGS.md for the merged "
            "JSON document this prints on stdout."
        ),
    )
    parser.add_argument(
        "pr", nargs="?", type=int, default=None,
        help="pull request number (omit only when --payload is given)",
    )
    parser.add_argument("--repo", default=fetch.DEFAULT_REPO, help="owner/repo (default: %(default)s)")
    parser.add_argument(
        "--payload",
        help="path to a captured PR payload (offline -- skips the live identity/PR probes and gh entirely)",
    )
    parser.add_argument(
        "--degrade", action="append", default=[], metavar="ENTRY_POINT=STATE",
        help="force a surface into a degenerate state, e.g. pr_diff=oversized (repeatable)",
    )
    parser.add_argument(
        "--seed",
        help=(
            "derive a deterministic nonce from this string instead of a random one. "
            "Controls/tests only -- a real run must never pin its nonce."
        ),
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help=f"per-dimension reviewer timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="list dimension slugs discovered in dimensions/*.py (sorted, one per line) and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.list:
        for slug in list_dimensions():
            print(slug)
        return EXIT_OK

    if args.payload is None and args.pr is None:
        parser.error("pr is required unless --payload is given")
    if args.payload is not None and args.pr is not None:
        parser.error("pr and --payload are mutually exclusive")

    nonce = contain.make_nonce(args.seed)
    dimensions = list_dimensions()

    if args.payload is not None:
        # No live PR to check: the identity probe and commit-pair resolution are
        # both skipped entirely, and fetch.from_payload never touches gh/network.
        surfaces = fetch.from_payload(args.payload)
        pr_number = args.pr if args.pr is not None else 0
        merge_base_sha, head_sha = _payload_commit_pair(args.payload)
    else:
        outcome, reason = probe_credential_and_pr(args.repo, args.pr)
        if outcome == "no_such_pr":
            print(f"NO SUCH PR: {reason}", file=sys.stderr)
            return EXIT_NO_SUCH_PR
        if outcome == "blocked":
            print(f"BLOCKED: {reason}", file=sys.stderr)
            return EXIT_BLOCKED
        if outcome != "live":
            print(f"INFRASTRUCTURE: {reason}", file=sys.stderr)
            return EXIT_INFRASTRUCTURE

        merge_base_sha, head_sha = resolve_commit_pair(args.repo, args.pr)
        surfaces = fetch.fetch_all(args.pr, args.repo)
        pr_number = args.pr

    for spec in args.degrade:
        surfaces = fetch.degrade(surfaces, spec)

    document = build_document(
        pr_number, merge_base_sha, head_sha, surfaces, dimensions, nonce, timeout=args.timeout
    )

    print(json.dumps(document, indent=2))

    if all(report["status"] == "complete" for report in document["reports"]):
        return EXIT_OK
    return EXIT_DIMENSION_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
