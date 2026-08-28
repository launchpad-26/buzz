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
  reading this specific pull request (not rate-limited -- that is ``2``); ``5``
  zero dimensions ran (``dimensions/`` was empty -- STEP 4 has not landed yet, or
  a caller passed an empty explicit list). ``5`` exists because ``all(...)`` over
  an empty ``reports`` array is vacuously ``True`` in Python, and printing an
  empty-``reports`` document while exiting ``0`` is exactly the "reads as clean
  when nothing ran" ambiguity FINDINGS.md's own "must not be empty" rule (and
  ``findings.validate()``) exists to forbid one level up.
* **``--payload`` commit pair.** A captured payload has no live commit pair to
  resolve (CONTAINMENT.md's compare-API call needs a real PR). ``merge_base_sha``/
  ``head_sha`` are read from the payload JSON's own ``merge_base_sha``/``head_sha``
  keys when present (harmless extra keys -- ``fetch.from_payload`` ignores
  anything outside ``contain.ENTRY_POINTS``), else default to ``"0" * 40``. The
  positional ``pr`` argument is optional with ``--payload`` and defaults to ``0``.
* **Per-dimension timeout default:** 120 seconds -- generous for a real model
  call once STEP 4 lands; every test in ``test_run_dimensions.py`` overrides it
  with a short value.
* **Concurrency uses one daemon ``threading.Thread`` per dimension, not
  ``ThreadPoolExecutor``.** ``ThreadPoolExecutor`` worker threads are
  non-daemon and CPython registers an ``atexit`` hook
  (``concurrent.futures.thread._python_exit``) that joins every live worker at
  interpreter shutdown -- regardless of ``shutdown(wait=False)``. A reviewer
  that never returns (a stalled network read, not merely a slow-but-finite
  call) would leave that worker thread alive forever, and the atexit hook would
  then block the whole *process* from exiting even after every dimension has
  been individually timed out and the merged document already printed. Plain
  ``daemon=True`` threads are not tracked by that hook and are simply abandoned
  at interpreter shutdown, so a genuinely-hung reviewer no longer prevents the
  process itself from exiting. See ``_run_dimensions_concurrently``.
* **``resolve_commit_pair`` compares against the PR's ``head.sha``, not its
  ``head.ref`` branch name.** An earlier version of this module used
  ``{base_ref}...{head_ref}``, which GitHub's compare API resolves against
  ``repo`` (the base repository) -- for a fork-based PR, an unqualified head
  branch name is either not found there at all (404) or, worse, silently
  resolves to an unrelated same-named branch in the base repo. A commit SHA has
  no such ambiguity: it identifies one commit regardless of which repository's
  branch pointed at it, as long as it is reachable from ``repo``'s history,
  which a PR's head commit always is via GitHub's internal ``pull/N/head`` ref.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
import threading
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
EXIT_NO_DIMENSIONS = 5

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


#: What ``build_document`` records under the document's ``reviewer`` key so a
#: downstream stage can tell a real review from this stub's unconditional
#: ``{"outcome": "clean"}``.
REVIEWER_STUB = "stub"
REVIEWER_INJECTED = "injected"


def reviewer_identity(reviewer: Reviewer) -> dict:
    """Name the reviewer that produced a document, for the published body's sake.

    Without this the two cases are indistinguishable downstream: a real review
    that found nothing, and this module's stub, which returns
    ``{"outcome": "clean", "findings": []}`` for every dimension without reading
    anything. An independent review panel found the publish workflow doing
    exactly that -- invoking ``main()``, which binds ``default_reviewer``, and
    publishing "No confirmed findings" as though a review had happened.

    ``main()`` still exposes no flag for choosing a reviewer -- #117 puts model
    choice out of scope and that stays true. This records which one ran; it does
    not select one. Wiring a real dimension reviewer is #116's work, and until it
    lands, ``publish_render`` turns this marker into a named INCOMPLETE reason
    rather than letting a stub run render as a clean pass.
    """
    kind = REVIEWER_STUB if reviewer is default_reviewer else REVIEWER_INJECTED
    return {"kind": kind, "name": getattr(reviewer, "__name__", type(reviewer).__name__)}


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


class _DaemonFuture:
    """A minimal, ``concurrent.futures.Future``-compatible-enough result box.

    Exists only so ``_collect_report`` can keep calling ``future.result(timeout=...)``
    and catching ``concurrent.futures.TimeoutError`` unchanged, while the thread
    that produces the value is a plain daemon thread rather than one owned by a
    ``ThreadPoolExecutor``. See ``_run_dimensions_concurrently`` for why that
    distinction is load-bearing.
    """

    def __init__(self) -> None:
        self._event = threading.Event()
        self._result: object = None
        self._exception: BaseException | None = None

    def set_result(self, value: object) -> None:
        self._result = value
        self._event.set()

    def set_exception(self, exc: BaseException) -> None:
        self._exception = exc
        self._event.set()

    def result(self, timeout: float | None = None) -> object:
        if not self._event.wait(timeout):
            raise concurrent.futures.TimeoutError(
                f"reviewer did not finish within {timeout}s"
            )
        if self._exception is not None:
            raise self._exception
        return self._result


def _run_reviewer_into(reviewer: Reviewer, document: str, future: _DaemonFuture) -> None:
    """The daemon thread's target: always resolves ``future``, one way or another.

    Catches ``BaseException``, not just ``Exception`` -- if the reviewer call
    itself raised something narrower this function did not anticipate, the
    future must still be resolved, or ``future.result(timeout=...)`` would wait
    the FULL timeout for a thread that had, in fact, already finished (crashed).
    """
    try:
        result = reviewer(document)
    except BaseException as exc:  # noqa: BLE001 - always resolve the future
        future.set_exception(exc)
    else:
        future.set_result(result)


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

    Each call runs in its own ``daemon=True`` thread, deliberately not a
    ``ThreadPoolExecutor``: ``ThreadPoolExecutor`` worker threads are
    non-daemon, and CPython registers an ``atexit`` hook
    (``concurrent.futures.thread._python_exit``) that joins every live worker
    thread at interpreter shutdown -- unconditionally, regardless of
    ``shutdown(wait=False)``. A reviewer that genuinely never returns (a
    stalled network read, not merely a slow-but-finite call) would leave that
    worker alive forever, and the atexit hook would then block the *process*
    itself from exiting even after every dimension has already been
    individually timed out here and the merged document printed. A plain
    ``daemon=True`` thread carries none of that bookkeeping: it is simply
    abandoned when the interpreter shuts down, so a genuinely-hung reviewer
    can no longer prevent the process from exiting. The thread is not
    cancelled -- Python cannot forcibly stop a running thread either way -- it
    is abandoned either way; the difference is entirely in whether abandoning
    it also blocks process exit.
    """
    if not dimensions:
        return []
    futures = []
    for _ in dimensions:
        future = _DaemonFuture()
        thread = threading.Thread(
            target=_run_reviewer_into, args=(reviewer, document, future), daemon=True
        )
        thread.start()
        futures.append(future)
    return [
        _collect_report(dim, fut, timeout, pr, merge_base_sha, head_sha, nonce)
        for dim, fut in zip(dimensions, futures)
    ]


# ---------------------------------------------------------------------------
# The stages manifest -- launchpad-26/buzz#565
# ---------------------------------------------------------------------------


def build_stages(dimensions: list[str], reports: list[dict]) -> list[dict]:
    """The ``stages`` manifest entries for #117's dimensions, one per DISPATCHED slug.

    Sourced from ``dimensions`` -- the list this run actually dispatched -- and
    ``dimensions`` alone. ``reports`` is indexed by ``dimension`` and looked up,
    never enumerated to produce the name list: a report cannot testify to its own
    absence, so the manifest is built from what was dispatched, not from what came
    back. A dimension that was dispatched and produced no report is still named
    here, with ``status: "no_report"`` -- it does not silently vanish from the
    manifest just because nothing came back for it. A report for a dimension this
    run did not dispatch contributes no entry (it cannot -- ``dimensions`` is the
    only source of names).

    Status/reason per dispatched dimension:

    * report arrived with ``status: "complete"`` -> ``{"status": "complete",
      "reason": None}``.
    * no report arrived at all -> ``{"status": "no_report", "reason": <fixed
      reason naming the absence>}``.
    * any other status -- ``"failed"`` today, and whatever #117 adds later --
      passes through verbatim, with ``reason`` taken from the report's own
      ``error["reason"]`` when it has one. A status that is not a string at all
      becomes ``"malformed_report"``: named, and not complete.

    Reports are matched to dimensions BY NAME, never by position. The two coincide
    today -- ``_run_dimensions_concurrently`` zips its results against the same
    ``dimensions`` list -- so a positional implementation would pass every test
    that supplies reports in dispatch order. It would also silently attach each
    status to the wrong dimension the moment anything resolves reports by
    completion order instead (an ``as_completed()`` refactor, a replayed
    recording), which is why the tests hand it reports deliberately out of order.

    Duplicate reports for one dimension resolve fail-closed: a ``"complete"``
    report never displaces a non-complete one. Precisely, it is
    first-non-complete-wins, so where SEVERAL non-complete reports name one
    dimension, which of them surfaces depends on arrival order. That order
    dependence is deliberate and harmless: every one of those outcomes is
    non-complete, so each downstream ``status != "complete"`` test fires either
    way and only the reason string differs. The direction that would matter --
    a complete masking a failure -- cannot happen.

    Only ``"complete"`` is treated as complete, and every other status is carried
    through rather than matched against a list. Written the other way round -- an
    ``elif`` for ``"failed"`` and an ``else`` producing ``"complete"`` -- a status
    this function had never heard of would render as a clean stage, which is the
    partial-review-reading-as-complete failure #119's condition (1) exists to
    catch and the reason #565 was filed. #117's own definition of done already
    reserves a third case ("a report without a completion marker is treated as
    truncated rather than clean"), so the unknown status is a matter of time, not
    a hypothetical. ``main()``'s own completion check reads the same way --
    ``all(report["status"] == "complete" for report in document["reports"])`` --
    and this keeps the two consistent.
    """
    by_name: dict[str, dict] = {}
    for report in reports:
        # Never raises on a malformed report, matching the idiom findings.py and
        # verdicts.py state explicitly for this directory: a document build that
        # dies on a bad report takes the whole review with it, and this function
        # sits on the path every run takes. A report too malformed to name its own
        # dimension cannot be matched to a dispatched slug by any means, so it
        # contributes nothing -- and the dimension it was FOR still gets named
        # below, as "no_report", because the names come from `dimensions`.
        if not isinstance(report, dict):
            continue
        name = report.get("dimension")
        if not isinstance(name, str):
            continue
        kept = by_name.get(name)
        # Duplicate reports for one dimension: a "complete" one must never
        # displace a non-complete one. Last-wins would let a partially-failed
        # dimension publish as clean while `reports` still carried the failure --
        # a stages/reports split-brain, and the same fail-open shape this
        # function's status handling exists to refuse. A dimension is complete
        # only if every report for it is, which is how main()'s own completion
        # check reads.
        if kept is None or (
            kept.get("status") == "complete" and report.get("status") != "complete"
        ):
            by_name[name] = report

    stages = []
    for dimension in dimensions:
        # Coerced to str once, and everything below uses the coerced value.
        # `list_dimensions()` yields `Path.stem`, so this is identity for every
        # real caller. It matters for any other one: `_input_stages` in
        # run_adjudication.py raises StagesShapeError on a non-string ``name``,
        # so writing the raw value through would have #117 emit a document #118
        # refuses wholesale -- one stage tolerating what the next rejects, with
        # the error surfacing in the wrong stage. Naming it in a shape #118
        # accepts keeps the dispatched dimension visible, which is the property
        # this function exists for; dropping it would not.
        name = dimension if isinstance(dimension, str) else str(dimension)
        report = by_name.get(name)
        if report is None:
            stages.append(
                {
                    "name": name,
                    "status": "no_report",
                    "reason": "dimension was dispatched but produced no report",
                }
            )
            continue
        status = report.get("status")
        if status == "complete":
            stages.append({"name": name, "status": "complete", "reason": None})
            continue
        error = report.get("error")
        stages.append(
            {
                "name": name,
                # A report whose status is not even a string is not a report this
                # function can vouch for. It is named, and it is not complete.
                "status": status if isinstance(status, str) else "malformed_report",
                "reason": error.get("reason") if isinstance(error, dict) else None,
            }
        )
    return stages


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
        "stages": build_stages(dimensions, reports),
        "reviewer": reviewer_identity(reviewer),
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


def _http_probe(path: str) -> tuple[int | None, str, int | None, str]:
    """One GET via ``gh api --include``, decoded to
    ``(status, message, rate_limit_remaining, body)``.

    Never raises: a missing ``gh``, a timeout, or any other subprocess-level
    failure all fold into ``status=None`` so ``classify_user_probe``/
    ``classify_pr_probe`` stay pure functions of already-decoded values, and this
    is the only place a real network/subprocess call happens for the identity
    probe. ``body`` is the raw response body text (whether or not it decoded as
    JSON) -- ``probe_credential_and_pr`` reuses it for the pull-request probe so
    ``resolve_commit_pair`` does not have to re-fetch the same PR JSON a second
    time.
    """
    try:
        proc = subprocess.run(["gh", "api", path, "--include"], capture_output=True, timeout=30)
    except FileNotFoundError:
        return None, "gh is not installed", None, ""
    except subprocess.TimeoutExpired:
        return None, "gh timed out after 30s", None, ""

    output = proc.stdout.decode("utf-8", "replace")
    status = _parse_status_line(output)
    if status is None:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        return None, detail or "gh produced no parseable HTTP status line", None, ""

    header_block, body = _split_header_block(output)
    rate_limit_match = _RATE_LIMIT_HEADER.search(header_block)
    rate_limit_remaining = int(rate_limit_match.group(1)) if rate_limit_match else None

    message = ""
    if status >= 400:
        try:
            message = json.loads(body).get("message", "") if body.strip() else ""
        except (json.JSONDecodeError, AttributeError):
            message = body.strip()
    return status, message, rate_limit_remaining, body


def probe_credential_and_pr(repo: str, pr: int) -> tuple[str, str, dict | None]:
    """The full two-call identity probe. Returns ``(outcome, reason, pr_json)``.

    ``"live"`` is the only outcome that means proceed; every other value is
    terminal. See ``classify_user_probe``/``classify_pr_probe`` for the per-call
    classification and ``main()`` for how each outcome maps to an exit code.

    ``pr_json`` is the already-parsed body of the ``GET /repos/{repo}/pulls/{pr}``
    call this function had to make anyway to classify the PR-existence outcome --
    non-``None`` only when ``outcome == "live"`` and the body parsed as JSON.
    ``main()`` threads it into ``resolve_commit_pair`` so a live run fetches the
    PR JSON once, not twice.
    """
    status, message, _rate_limit, _body = _http_probe("user")
    outcome, reason = classify_user_probe(status, message)
    if outcome != "live":
        return outcome, reason, None

    status, message, rate_limit_remaining, body = _http_probe(f"repos/{repo}/pulls/{pr}")
    outcome, reason = classify_pr_probe(status, message, rate_limit_remaining)
    pr_json = None
    if outcome == "live":
        try:
            pr_json = json.loads(body)
        except json.JSONDecodeError:
            pr_json = None
    return outcome, reason, pr_json


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


def resolve_commit_pair(repo: str, pr: int, pr_json: dict | None = None) -> tuple[str, str]:
    """``(merge_base_sha, head_sha)`` for a live PR. Two REST calls, never GraphQL.

    ``fetch.fetch_all``/the PR JSON ``fetch.py`` narrows down never carry a
    merge-base SHA. The PR JSON's own ``base.sha`` is the base branch's CURRENT
    tip, not the commit the head forked from -- diffing against it would
    attribute every commit landed on the base branch since the fork point to this
    PR's own diff. ``compare``'s ``merge_base_commit.sha`` is the actual fork
    point, so that is what is read here.

    Compares against the PR's ``head.sha``, never its ``head.ref`` branch name:
    GitHub's compare API resolves an unqualified branch name against ``repo``
    (the base repository), so for a fork-based PR that name either does not
    exist there (404) or, worse, silently resolves to an unrelated same-named
    branch. A SHA has no such ambiguity.

    ``pr_json`` lets a caller that already fetched ``GET /repos/{repo}/pulls/{pr}``
    (``probe_credential_and_pr`` does, to classify the PR-existence outcome) pass
    it straight through instead of this function re-fetching it -- one call
    instead of two per live run. ``None`` (the default) fetches it here, so this
    function is still correct and self-contained when called on its own.
    """
    if pr_json is None:
        pr_json = _gh_api_json(f"repos/{repo}/pulls/{pr}")
    base_ref = pr_json["base"]["ref"]
    head_sha = pr_json["head"]["sha"]
    compare_json = _gh_api_json(f"repos/{repo}/compare/{base_ref}...{head_sha}")
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


def main(argv: list[str] | None = None, *, reviewer: Reviewer = default_reviewer) -> int:
    """``reviewer`` is a testability seam only, never exposed via ``argv`` --

    #117 puts choosing the model out of scope, and this keeps that true of the CLI
    surface: there is no flag that lets a caller select one. Without this seam,
    ``main()``'s own exit-code wiring (the ``all(...)`` check below, and its
    connection to the process's actual exit status) has no way to be exercised
    end-to-end -- ``build_document``'s ``reviewer`` parameter is bound to
    ``default_reviewer`` at function-definition time, so patching the module-level
    ``default_reviewer`` name after the fact does not reach a call that already
    defaulted to the original object -- Python binds a default argument value once,
    at function-definition time, not on each call (the same rule behind the classic
    mutable-default-argument pitfall). STEP 6 (launchpad-26/buzz#117) needs a real
    test of "the process exits non-zero when a dimension fails", not only of
    ``build_document``'s return value, and this is the minimal way to give it one.
    """
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
        outcome, reason, pr_json = probe_credential_and_pr(args.repo, args.pr)
        if outcome == "no_such_pr":
            print(f"NO SUCH PR: {reason}", file=sys.stderr)
            return EXIT_NO_SUCH_PR
        if outcome == "blocked":
            print(f"BLOCKED: {reason}", file=sys.stderr)
            return EXIT_BLOCKED
        if outcome != "live":
            print(f"INFRASTRUCTURE: {reason}", file=sys.stderr)
            return EXIT_INFRASTRUCTURE

        # pr_json is the body probe_credential_and_pr already fetched from
        # GET /repos/{repo}/pulls/{pr} to classify the PR-existence outcome --
        # threaded through so a live run fetches that JSON once, not twice.
        merge_base_sha, head_sha = resolve_commit_pair(args.repo, args.pr, pr_json=pr_json)
        surfaces = fetch.fetch_all(args.pr, args.repo)
        pr_number = args.pr

    for spec in args.degrade:
        surfaces = fetch.degrade(surfaces, spec)

    if not dimensions:
        # Zero dimension files exist (STEP 4 has not landed, or a caller wired
        # this to an explicitly empty list). all(...) over an empty "reports"
        # array is vacuously True, so without this check the run below would
        # print an empty-reports document and exit 0 -- a document
        # findings.validate() itself rejects ("reports must not be empty"),
        # and exactly the "reads as clean when nothing ran" ambiguity
        # FINDINGS.md's own rule for this exists to forbid one level up.
        print(
            "NO DIMENSIONS: dimensions/ contains no *.py files -- nothing to run",
            file=sys.stderr,
        )
        return EXIT_NO_DIMENSIONS

    document = build_document(
        pr_number, merge_base_sha, head_sha, surfaces, dimensions, nonce,
        reviewer=reviewer, timeout=args.timeout
    )

    print(json.dumps(document, indent=2))

    if all(report["status"] == "complete" for report in document["reports"]):
        return EXIT_OK
    return EXIT_DIMENSION_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
