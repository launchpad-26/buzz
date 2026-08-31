#!/usr/bin/env python3
"""Panel review runner: assurance router, fallback pools, error classification,
cooldown persistence, trusted metadata, and per-attempt structured log artifacts.

For one trusted profile it fills each reviewer slot from an ordered fallback
chain and returns only the freshly-written, schema-valid verdicts for that
profile, each accompanied by a trusted metadata sidecar that records the exact
runner/model/provider identity that produced it. A slot is "filled" only when a
fresh, schema-valid verdict file was written this run and its trust metadata was
attached; anything less is a partial/degraded panel and is never reported
complete.

Trust boundaries:
- Verdict content (signal, recommendation, findings) is model-controlled and
  validated strictly against schemas/reviewer-verdict.json before it may fill a
  slot. Malformed JSON, missing/contradictory fields, or a signal token embedded
  in prose NEVER fill a slot — they are classed candidate_terminal, cooled down,
  and the next fallback is tried.
- Runner/model/provider identity is trusted machinery state, attached by this
  code OUTSIDE the model-controlled verdict JSON (a meta sidecar per slot), never
  parsed from model prose.

Selection rules:
- Only candidates whose declared capability meets the profile minimum and whose
  declared efforts include the profile effort are ever invoked.
- Each slot requires a distinct concrete selector and -- where declared -- a
  distinct provider family.
- A lane with no qualifying candidate stays empty; we never resurrect an
  unfiltered fallback lane at lower assurance.

Error policy (see errors.py):
  transient          -> retry the same candidate once, then cooldown + fallback
  candidate_terminal -> cooldown + fallback immediately
  job_blocking       -> raise; the dispatcher moves the job to human_required
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

from assurance import Profile, minimum_profile
from checks import is_failing as _check_is_failing
from common import State, atomic_write, load_config, utcnow
from errors import (
    AuditLoggingError,
    CANDIDATE_TERMINAL,
    JOB_BLOCKING,
    JobBlockingError,
    PROVIDER_TERMINAL,
    TRANSIENT,
)
from fallback import order_candidates, recipe_for
from modes import Participant, aggregate, for_profile as mode_for_profile
from logging_otel import MAX_STDERR_BYTES
from runners import (
    EffortUnsupportedError,
    UnknownRunnerError,
    build_invocation,
)
from strategies import STRATEGY_BY_NAME
from verdict import signal_from_verdict, validate_verdict

SENSITIVE = re.compile(
    r"(^|/)(security|migrations?|provisioning)(/|$)|^\.github/workflows/|(^|/)deploy/"
)
CAPABILITY_RANK = {"economy": 0, "workhorse": 1, "frontier": 2}

SIGNAL_TOKENS = (
    "SUPPORTED",
    "MISSING_EVIDENCE",
    "INSUFFICIENT_CAPABILITY",
    "MATERIAL_DISAGREEMENT",
    "HUMAN_RESERVED",
)
SLOT_FILES = ("review-A.txt", "review-B.txt")

#: The one verdict schema this panel validates against (schemas/<name>.json).
#: A strategy declaring a different `output_schema` is refused, fail-closed.
VERDICT_SCHEMA = "reviewer-verdict"

# OMP invocation flags, verified against `omp --help` on this machine (v18.0.4):
#   --cwd=<value>     Directory to start in (overrides the launch cwd)
#   --no-tools        Disable ALL built-in tools -> demonstrably read-only.
#   --no-session      Ephemeral: never persists the session.
#   -p, --print       Non-interactive: process prompt and exit.
#   --thinking=<...>  Thinking level: off, minimal, low, medium, high, xhigh, max, auto
#   --model=<value>   Model to use.
# `--no-tools` is the strictest supported read-only profile (stronger than a tool
# allowlist), so it is preserved for the review invocation.
OMP_READ_ONLY_FLAGS = ("--no-tools",)


def _record_diagnostic(
    logger, entry: dict[str, Any], attempt: int, text: str
) -> list[str]:
    """Persist a bounded (<=8KB) redacted stderr diagnostic artifact, if a logger
    is present, and return its relative path(s).

    Failure to record must not mask the candidate failure, so logging exceptions
    are converted into a typed AuditLoggingError (disposition capable of blocking
    approval).
    """
    if logger is None:
        return []
    try:
        relative = logger.diagnostic(
            "stderr",
            text,
            attempt=attempt,
            candidate=entry.get("selector", "candidate"),
        )
        return [relative]
    except AuditLoggingError:
        raise
    except Exception as exc:  # logging must be typed, never swallowed
        raise AuditLoggingError(str(exc)) from exc


def _files_for(state: State, repo: str, number: int) -> list[str]:
    row = state.db.execute(
        "SELECT payload FROM prs WHERE repo=? AND number=?", (repo, number)
    ).fetchone()
    if not row:
        return []
    payload = json.loads(row["payload"])
    files = payload.get("files") or []
    if isinstance(files, list):
        return [str(f.get("filename", "")) for f in files][:200]
    return []


def decide_assurance(
    config: dict[str, Any], state: State, repo: str, number: int, lane: str
) -> Profile:
    """Deterministic minimum profile from PR facts. Sensitive or large -> frontier/high."""
    files = _files_for(state, repo, number)
    assurance = config.get("assurance", {})
    sensitive = any(SENSITIVE.search(f) for f in files)
    row = state.db.execute(
        "SELECT payload FROM prs WHERE repo=? AND number=?", (repo, number)
    ).fetchone()
    additions = deletions = 0
    if row:
        payload = json.loads(row["payload"])
        additions = payload.get("additions", 0) or 0
        deletions = payload.get("deletions", 0) or 0
    large = (additions + deletions) >= int(assurance.get("large_diff_lines", 700))
    if sensitive or large:
        return Profile(capability="frontier", effort="high", independence="challenger")
    return minimum_profile(lane, sensitive=False, large=False)


def resolve_repo_path(config: dict[str, Any], repo: str) -> str:
    """Repo path from either the legacy config shape (repos.<repo>.path) or the
    repo-local shape (repository.root)."""
    if "repos" in config:
        entry = config["repos"].get(repo)
        if entry and entry.get("path"):
            return entry["path"]
    repo_cfg = config.get("repository", {}) or {}
    return repo_cfg.get("root", "")


def _independence_count(independence: str) -> int:
    return 1 if independence == "single" else 2


def _signal_for_file(path: pathlib.Path) -> str:
    """Return the signal ONLY from a schema-valid verdict.

    A prose-embedded signal token, malformed JSON, or a verdict missing/contradicting
    required schema fields is not a completed review: returns MISSING_EVIDENCE so
    the slot is treated as incomplete (never a forged SUPPORTED)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return "MISSING_EVIDENCE"
    ok, _ = validate_verdict(text)
    if not ok:
        return "MISSING_EVIDENCE"
    return signal_from_verdict(text)


def _parse_signals(artifact_dir: pathlib.Path, expected: int) -> list[str]:
    signals: list[str] = []
    for idx in range(min(expected, len(SLOT_FILES))):
        vf = artifact_dir / SLOT_FILES[idx]
        if vf.is_file():
            signals.append(_signal_for_file(vf))
    return signals


def _slot_role(roles: tuple[str, ...], idx: int, expected: int) -> str:
    """The role this slot plays, taken from the STRATEGY's declared roles.

    The strategy is the record of how participants compose, so the role labels
    come from it rather than being re-invented here. A strategy that declares
    fewer roles than the panel fills falls back to the generic reviewer labels,
    so a short `roles` tuple degrades the label, never the panel.
    """
    if idx < len(roles) and roles[idx]:
        return str(roles[idx])
    if expected <= 1:
        return "reviewer"
    return f"reviewer_{'ab'[idx] if idx < 2 else idx}"


def _mode_participants(
    artifact_dir: pathlib.Path, expected: int, roles: tuple[str, ...] = ()
) -> list[Participant]:
    """Build mode participants for the filled slots.

    `provider_family` is read from the trusted sidecar the machinery wrote, never
    from model-controlled verdict content, so a model cannot claim independence it
    does not have. A slot with no verdict file contributes an invalid participant
    rather than being silently omitted, so the discount reason is recorded.
    """
    participants: list[Participant] = []
    for idx in range(min(expected, len(SLOT_FILES))):
        slot_file = artifact_dir / SLOT_FILES[idx]
        role = _slot_role(roles, idx, expected)
        if not slot_file.is_file():
            participants.append(Participant(role=role, model=f"<{SLOT_FILES[idx]}>", valid=False))
            continue
        meta: dict[str, Any] = {}
        sidecar = slot_file.with_suffix(".meta.json")
        if sidecar.is_file():
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                meta = {}
        participants.append(Participant(
            role=role,
            model=str(meta.get("model") or SLOT_FILES[idx]),
            provider_family=str(meta.get("provider_family") or ""),
            valid=True,
            signal=_signal_for_file(slot_file),
        ))
    return participants


def _trust_meta(slot: str, entry: dict[str, Any], effort: str) -> dict[str, Any]:
    """Trusted (machinery-written) metadata for one filled slot. This lives in a
    sidecar file OUTSIDE the model-controlled verdict JSON; the model never shapes
    it, so downstream approval can rely on the recorded identity."""
    meta = {
        "slot": slot,
        "runner": entry.get("runner"),
        "model": entry.get("selector"),
        "provider_family": entry.get("provider_family"),
        "capability": entry.get("capability"),
        "effort": effort,
        "trusted": True,
        "written_at": utcnow(),
    }
    return {k: v for k, v in meta.items() if v is not None}


def _available(state: State, key: str) -> bool:
    row = state.db.execute("SELECT unavailable_until FROM providers WHERE key=?", (key,)).fetchone()
    if not row or not row["unavailable_until"]:
        return True
    until = dt.datetime.fromisoformat(row["unavailable_until"].replace("Z", "+00:00"))
    return dt.datetime.now(dt.timezone.utc) > until


def mark_unavailable(state: State, key: str, error: str, cooldown: int) -> None:
    until = (
        dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=cooldown)
    ).isoformat().replace("+00:00", "Z")
    state.db.execute(
        "INSERT INTO providers(key,unavailable_until,last_error,updated_at) VALUES(?,?,?,?) "
        "ON CONFLICT(key) DO UPDATE SET unavailable_until=excluded.unavailable_until,"
        "last_error=excluded.last_error,updated_at=excluded.updated_at",
        (key, until, error[:300], utcnow()),
    )
    state.db.commit()


def select_candidate_pools(config: dict[str, Any], state: State) -> list[list[dict[str, Any]]]:
    pools = config.get("models", {})
    lanes: list[list[dict[str, Any]]] = []
    for pool_name in ("primary", "secondary"):
        lane: list[dict[str, Any]] = []
        for entry in pools.get(pool_name, []):
            key = f"{entry['runner']}:{entry['selector']}"
            if _available(state, key):
                lane.append(dict(entry, _key=key))
        if lane:
            lanes.append(lane)
    return lanes


def _run_reviewer(entry, prompt, out_path, effort, repo_path, timeout, logger=None) -> None:
    """Invoke one candidate runner and write its raw stdout to `out_path`.

    Command construction is delegated to `runners.build_invocation`, which owns the
    read-only invocation for each supported transport (omp / claude / codex). A
    runner with no adapter is a hard job_blocking configuration error that must
    reach the operator, not a candidate failure that silently falls through to the
    next model. A non-zero exit raises ReviewerError carrying the bounded stderr
    for the diagnostic artifact (never for our own schema-validation rejections).
    """
    try:
        invocation = build_invocation(entry, prompt, effort, repo_path)
    except (UnknownRunnerError, EffortUnsupportedError) as exc:
        raise JobBlockingError(str(exc)) from exc
    # Record what actually enforced read-only, and whether the requested effort
    # was enforceable, so a route cannot later claim an axis it did not apply.
    entry["_invocation"] = invocation.as_meta()
    cmd = list(invocation.cmd)
    result = subprocess.run(
        cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL
    )
    stdout = result.stdout or b""
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if result.returncode != 0:
        stderr = result.stderr or b""
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        raise ReviewerError(
            f"{entry['selector']} exit {result.returncode}", stderr=stderr or ""
        )
    out_path.write_text(stdout)


class ReviewerError(RuntimeError):
    """A candidate runner exited non-zero; carries its bounded stderr for the
    diagnostic artifact (never raised for our own validation rejections)."""

    def __init__(self, message: str, *, stderr: str = ""):
        super().__init__(message)
        self.stderr = stderr


class VerdictRejectedError(RuntimeError):
    """The candidate returned, but its output is not a schema-valid verdict.

    Raised inside `_attempt_candidate` after a successful runner is complete, so
    malformed / missing-field / contradictory / prose-embedded-signal output is
    classified candidate_terminal, given a cooldown, and falls through to the
    next candidate. The slot file is removed so nothing is filled by it.
    """

    def __init__(self, issues: list[str]):
        super().__init__("verdict rejected: " + "; ".join(issues))
        self.issues = issues


def _attempt_candidate(
    entry,
    prompt,
    out,
    effort,
    repo_path,
    state,
    timeout=1800,
    cooldown=1800,
    logger=None,
) -> tuple[bool, str, str]:
    """Run one candidate under fallback policy.

    Returns (success, classification, failure summary). Only a real runner timeout
    (subprocess.TimeoutExpired) is transient and retried exactly once (a total of
    two tries on the SAME candidate); every other failure -- including a
    returned-but-invalid verdict, a non-zero exit, or an OSError -- is terminal for
    this candidate, persisted as a cooldown, and falls through to the next
    candidate. job_blocking propagates to the caller.
    """
    run_count = 0
    while True:
        run_count += 1
        try:
            _run_reviewer(entry, prompt, out, effort, repo_path, timeout)
        except (JobBlockingError, AuditLoggingError):
            raise
        except subprocess.TimeoutExpired as exc:
            summary = f"timeout after {timeout}s: {entry.get('_key', '')}"
            _record_diagnostic(logger, entry, run_count, f"timeout: {exc}")
            mark_unavailable(state, entry["_key"], summary, cooldown)
            if run_count == 1:
                continue  # retry the SAME candidate exactly once on genuine timeout
            # A transport that never answered twice is a provider problem, not a
            # quirk of this model: its siblings are not worth a second timeout.
            return False, TRANSIENT, summary
        except Exception as exc:
            # Only a genuine runner timeout is transient; everything else is a
            # deterministic terminal failure (never blanket-labeled transient).
            # A non-zero exit or OSError is attributable to the PROVIDER (auth,
            # quota, missing binary), so it is provider-scoped rather than
            # candidate-scoped.
            summary = str(exc)[:200]
            stderr = getattr(exc, "stderr", "") or ""
            _record_diagnostic(logger, entry, run_count, stderr or summary)
            mark_unavailable(state, entry["_key"], summary, cooldown)
            return False, PROVIDER_TERMINAL, summary

        # Runner returned cleanly: the output must be a schema-valid verdict.
        try:
            text = out.read_text(encoding="utf-8")
        except OSError as exc:
            summary = f"could not read candidate output: {exc}"
            _record_diagnostic(logger, entry, run_count, summary)
            mark_unavailable(state, entry["_key"], summary, cooldown)
            return False, CANDIDATE_TERMINAL, summary
        ok, issues = validate_verdict(text)
        if ok:
            return True, "ok", ""
        # Invalid output (malformed JSON, missing schema fields, contradictory
        # fields, or a prose-embedded signal token) never fills the slot.
        if out.is_file():
            out.unlink()
        summary = f"invalid verdict: {'; '.join(issues)[:200]}"
        _record_diagnostic(logger, entry, run_count, text[:MAX_STDERR_BYTES] if text else summary)
        mark_unavailable(state, entry["_key"], summary, cooldown)
        return False, CANDIDATE_TERMINAL, summary


def _selection_context(config, repo, number, lane, profile):
    """Best-effort strategy + route selection for logging. Never raises; returns
    (strategy_name, routed_log). Unknown/failed participants never count as
    agreement regardless of strategy."""
    strategy_name = "direct_analysis"
    routed_log: dict = {}
    try:
        from routing import resolve_route
        from strategies import strategy_for_profile

        # The SHARED selector, so the orchestrator's pre-spend budget reservation
        # and the panel's execution can never pick two different strategies.
        strategy, reason = strategy_for_profile(profile)
        strategy_name = strategy.name
        routed_log["strategy"] = strategy.name
        routed_log["strategy_reason"] = reason
        run = resolve_route(config, "review")
        routed_log["resolved_model"] = run.as_dict()
    except Exception as exc:
        # Selection is advisory metadata, so a failure must not fail the panel.
        # It is recorded rather than swallowed: a silent `pass` here previously
        # hid real configuration errors (e.g. a routing ladder that resolves to
        # no model at all) from the attempt artifact.
        routed_log["selection_error"] = f"{type(exc).__name__}: {exc}"[:200]
    return strategy_name, routed_log



def _plan_for_job(config, state, repo, number, job):
    """Build the review plan from PERSISTED facts. Returns None when unavailable.

    Never raises: an unavailable plan means the reviewer falls back to the generic
    prompt, which is weaker but not wrong. The plan is recorded in the ledger so an
    omitted question is visible rather than silently absent.
    """
    try:
        import json as _json

        from planner import plan_review

        row = state.db.execute(
            "SELECT payload FROM prs WHERE repo=? AND number=?", (repo, number)
        ).fetchone()
        payload = _json.loads(row["payload"]) if row else {}
        if not isinstance(payload, dict):
            payload = {}

        raw_files = payload.get("files") or []
        files = [f.get("filename", "") if isinstance(f, dict) else str(f) for f in raw_files]

        evidence_path = state.job_dir(job) / "evidence.json"
        checks: list = []
        if evidence_path.is_file():
            evidence = _json.loads(evidence_path.read_text(encoding="utf-8"))
            checks = (evidence or {}).get("checks") or []
        # `is_failing` is the same predicate this expression spelled inline: not
        # green and not pending. Vocabulary lives in `checks.py`.
        checks_failing = any(_check_is_failing(c) for c in checks)

        head_row = state.db.execute(
            "SELECT head_sha FROM jobs WHERE id=?", (job,)
        ).fetchone()
        head_sha = head_row["head_sha"] if head_row else ""

        # A prior reviewed revision of the same PR makes this a re-review.
        prior = state.db.execute(
            "SELECT COUNT(*) AS c FROM jobs WHERE repo=? AND number=? AND head_sha<>?",
            (repo, number, head_sha),
        ).fetchone()
        is_rereview = bool(prior and int(prior["c"]) > 0)

        plan = plan_review(
            files=files,
            additions=int(payload.get("additions", 0) or 0),
            deletions=int(payload.get("deletions", 0) or 0),
            large_diff_lines=int((config.get("assurance") or {}).get("large_diff_lines", 700) or 700),
            checks_failing=checks_failing,
            is_rereview=is_rereview,
            head_sha=head_sha,
        )
        try:
            from ledger import record as _record

            _record(state, job_id=job, repo=repo, number=number, head_sha=head_sha,
                    kind="strategy", entry_key="review_plan",
                    payload={"name": "review_plan", **plan.as_dict()})
        except Exception:
            pass
        return plan
    except Exception:
        return None


def run_panel(
    config,
    state,
    repo,
    number,
    lane,
    job,
    profile=None,
    logger=None,
) -> dict[str, Any]:
    """Run exactly one trusted profile once, with fallback + cooldown + logging.

    Returns `complete` only when every required slot produced a fresh, schema-valid
    verdict this run AND had its trusted metadata sidecar attached. Attempt
    artifacts and events are written when `logger` (a JobLogger) is given;
    otherwise attempt writing is skipped but the panel still runs.
    """
    artifact_dir = state.job_dir(job)
    evidence_text = artifact_dir / "evidence.txt"
    if not evidence_text.is_file():
        raise JobBlockingError("evidence.txt missing; run evidence.py before panel")

    profile = profile or decide_assurance(config, state, repo, number, lane)
    required = _independence_count(profile.independence)
    repo_path = resolve_repo_path(config, repo)

    candidate_lanes = select_candidate_pools(config, state)
    required_rank = CAPABILITY_RANK[profile.capability]

    def _qualifying(pool: dict[str, Any]) -> bool:
        # Never run a model below the required capability.
        if CAPABILITY_RANK.get(pool.get("capability"), 1) < required_rank:
            return False
        # Skip models that do not declare support for the requested effort.
        efforts = pool.get("efforts") or []
        if efforts and profile.effort not in efforts:
            return False
        return True

    # The strategy is resolved BEFORE candidate ordering, because which tier leads
    # is a property of the review strategy, not of config file order. It is also
    # reused for the attempt log below, so it is computed exactly once.
    strategy_name, route_log = _selection_context(config, repo, number, lane, profile)
    recipe = recipe_for(strategy_name)
    strategy = STRATEGY_BY_NAME.get(strategy_name)

    # The strategy declares the schema its participants must satisfy. This panel
    # validates against exactly one schema, so a strategy asking for a different
    # one is a configuration error that must stop the run rather than be silently
    # validated against the wrong contract.
    if strategy is not None and strategy.output_schema != VERDICT_SCHEMA:
        raise JobBlockingError(
            f"strategy {strategy_name!r} declares output_schema "
            f"{strategy.output_schema!r} but the panel validates {VERDICT_SCHEMA!r}"
        )

    lanes = [
        order_candidates([c for c in lane_entries if _qualifying(c)], recipe)
        for lane_entries in candidate_lanes
    ]
    # Deliberately DO NOT fall back to unfiltered lanes: a lane with no qualifying
    # candidate stays empty -> the panel is degraded rather than lowered in quality.
    lanes = [lane_entries for lane_entries in lanes if lane_entries]

    # The deterministic plan decides WHICH questions this change requires, so a
    # security or compatibility question is asked when the paths warrant it rather
    # than left to the reviewer's discretion.
    review_plan = _plan_for_job(config, state, repo, number, job)
    activities = ""
    if review_plan is not None:
        from planner import render_activities

        activities = render_activities(review_plan)

    # The full verdict contract is stated explicitly. Leaving `recommendation` or
    # the finding fields unspecified caused schema rejections, and each rejection
    # cools that candidate down for the configured cooldown — so an under-specified
    # prompt silently burns reviewers.
    prompt = (
        f"Independently review {repo} PR #{number} (lane {lane}, job {job}). "
        f"Read the evidence envelope at {evidence_text}. "
        + (f"{activities} " if activities else "")
        + "Return ONLY a strict JSON object with exactly these keys: "
        "signal, recommendation, summary, findings, good, missing_evidence. "
        f"signal must be exactly one of: {', '.join(SIGNAL_TOKENS)}. "
        "recommendation must be exactly one of: clean, findings, human. "
        "summary is a non-empty string. findings is an array; each finding needs "
        "severity (one of blocker, high, medium, low), title, location formatted "
        "as path:line, evidence, and primary_source. good and missing_evidence are "
        "arrays of non-empty strings. "
        "Use signal SUPPORTED only with recommendation clean and no findings; use "
        "DEFECTS_FOUND when you have located a real defect, with at least one "
        "finding. "
        "Emit raw JSON only: no markdown code fence, no backticks, and no "
        "commentary before or after the object. "
        "Do not call GitHub or modify files."
    )

    # The runtime ceiling is the TIGHTER of the operator's transport timeout and
    # the strategy's declared budget. A strategy can only ever shorten a run, so
    # this cannot lengthen an operator-configured timeout.
    timeout = int(config["models"].get("timeout_seconds", 1800))
    if strategy is not None and strategy.timeout_seconds > 0:
        timeout = min(timeout, int(strategy.timeout_seconds))
    cooldown = int(config["models"].get("cooldown_seconds", 1800))

    # A fresh attempt clears every prior slot file so a stale (lower-profile) verdict
    # is never consumed on an escalated run.
    for sf in SLOT_FILES:
        prior = artifact_dir / sf
        if prior.is_file():
            prior.unlink()

    completed: list[str] = []
    selected: list[str] = []
    considered: list[str] = []
    attempted: list[str] = []
    failed: list[str] = []
    skipped: list[str] = []
    used_selectors: set[str] = set()
    used_families: set[str] = set()
    #: Families whose PROVIDER failed this run (auth/quota/transport). Their
    #: sibling models are not retried: provider-level failures are correlated, so
    #: a sibling costs another full timeout for the same outcome.
    failed_families: set[str] = set()
    filled = 0
    diag_paths: list[str] = []

    # `lane_index` selects the candidate lane; the SLOT is allocated by fill
    # order. Indexing slot files by lane meant a lane-0 wipeout followed by a
    # lane-1 success wrote review-B.txt while `_parse_signals` (which reads the
    # first `required` slot files) only looked at review-A.txt: real model spend,
    # a valid verdict on disk, and a panel reported degraded.
    for lane_index, lane_list in enumerate(lanes):
        if filled >= required:
            break
        for pos, pool in enumerate(lane_list):
            family = pool.get("provider_family")
            if family and family in failed_families:
                skipped.append(pool["_key"])
                continue
            if pool["selector"] in used_selectors or (family and family in used_families):
                skipped.append(pool["_key"])
                continue
            considered.append(pool["_key"])
            slot = filled
            out = artifact_dir / SLOT_FILES[slot]
            attempted.append(pool["_key"])
            ok, classification, failure = _attempt_candidate(
                pool,
                prompt,
                out,
                profile.effort,
                repo_path,
                state,
                timeout=timeout,
                cooldown=cooldown,
                logger=logger,
            )
            if ok:
                selected.append(pool["_key"])
                completed.append(pool["selector"])
                # Record the route that ACTUALLY executed, including whether the
                # requested effort was enforceable by that transport.
                try:
                    from ledger import record as _ledger_record
                    from model_registry import qualified_route

                    route = qualified_route(
                        pool,
                        effort=profile.effort,
                        policy_version=str((config.get("policy") or {}).get("version") or "unversioned"),
                        default_prompt_version=str((config.get("models") or {}).get("prompt_version") or "v1"),
                    )
                    _ledger_record(
                        state, job_id=job, repo=repo, number=number,
                        head_sha=state.db.execute(
                            "SELECT head_sha FROM jobs WHERE id=?", (job,)
                        ).fetchone()["head_sha"],
                        kind="route", entry_key=pool["_key"],
                        payload=dict(pool.get("_invocation") or {},
                                     slot=SLOT_FILES[slot],
                                     capability=pool.get("capability", ""),
                                     provider_family=pool.get("provider_family", ""),
                                     qualified_route=route),
                    )
                except Exception:
                    pass  # the ledger explains runs; it must not break one
                used_selectors.add(pool["selector"])
                if family:
                    used_families.add(family)
                # Trusted metadata sidecar, OUTSIDE the model-controlled verdict JSON.
                atomic_write(
                    out.with_suffix(".meta.json"),
                    json.dumps(_trust_meta(SLOT_FILES[slot], pool, profile.effort), indent=2, sort_keys=True),
                )
                filled += 1
                break
            failed.append(pool["_key"])
            # A provider-scoped failure retires the whole family for this run; a
            # model emitting invalid output retires only that model.
            if family and classification in (TRANSIENT, PROVIDER_TERMINAL):
                failed_families.add(family)
        if filled >= required:
            break

    signals = _parse_signals(artifact_dir, required)

    # Counting slot files cannot see that a slot produced no valid verdict, or
    # that two slots came from one provider family. The mode contract discounts
    # both, so completeness reflects participants that actually count. It can
    # only ever be stricter than the slot count, never looser.
    mode_spec = mode_for_profile(profile.independence, required)
    strategy_roles = strategy.roles if strategy is not None else ()
    mode_result = aggregate(
        mode_spec, _mode_participants(artifact_dir, required, strategy_roles)
    )
    # A split among the participants that DID count is handled the way the
    # strategy declares. It is reported rather than resolved here: `assurance`
    # owns what a disagreement means, this only records which handling applies.
    counted_signals = {s for s in mode_result.signals if s}
    disagreement = len(counted_signals) > 1
    disagreement_handling = (
        (strategy.disagreement_handling if strategy is not None else "escalate")
        if disagreement else ""
    )
    complete = (
        len(signals) >= required
        and filled >= required
        and len(mode_result.counted) >= required
    )
    outcome = "complete" if complete else ("degraded" if completed else "retryable")

    attempt = {
        "phase": "assurance",
        "profile": profile.as_dict(),
        "strategy": strategy_name,
        "recipe": recipe.name,
        "recipe_tiers": list(recipe.tiers),
        "considered": considered,
        "skipped": skipped,
        "attempted": attempted,
        "failed": failed,
        "failed_families": sorted(failed_families),
        "selected": selected,
        "cooldowns": ["cooldown:" + c for c in failed],
        "signals": signals,
        "required": required,
        "completed": len(completed),
        "outcome": outcome,
        "timeout_seconds": timeout,
        "budget_tokens": int(strategy.budget_tokens) if strategy is not None else 0,
        "roles": [_slot_role(strategy_roles, i, required) for i in range(required)],
        "disagreement": disagreement,
        "disagreement_handling": disagreement_handling,
    }
    if logger is not None:
        try:
            # Strategy/route selection was already resolved before ordering.
            logger.attempt(attempt)
            logger.info(
                body=f"panel attempt {repo}#{number} -> {outcome}",
                phase="assurance",
                outcome=outcome,
                attributes={
                    "review.required": required,
                    "review.completed": len(completed),
                    "review.attempt": 1,
                    "ai.models": completed,
                    "reasoning.strategy": strategy_name,
                    "reasoning.recipe": recipe.name,
                    "reasoning.resolved_model": route_log.get("resolved_model"),
                },
                event_name="panel_attempt",
            )
        except Exception as exc:  # logged/audit failure must be typed + block
            raise AuditLoggingError(str(exc)) from exc

    state.db.commit()
    return {
        "profile": profile.as_dict(),
        "required_reviewers": required,
        "completed_reviewers": completed,
        "selected_candidates": selected,
        "consider": considered,
        "skip": skipped,
        "attempted_candidates": attempted,
        "failed_candidates": failed,
        "complete": complete,
        "signals": signals,
        "outcome": outcome,
        "failed_families": sorted(failed_families),
        "strategy": strategy_name,
        "recipe": recipe.name,
        "budget_tokens": int(strategy.budget_tokens) if strategy is not None else 0,
        "timeout_seconds": timeout,
        "roles": [_slot_role(strategy_roles, i, required) for i in range(required)],
        "disagreement": disagreement,
        "disagreement_handling": disagreement_handling,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Panel and assurance runner")
    parser.add_argument("--config", default=None)
    parser.add_argument("repo")
    parser.add_argument("number", type=int)
    parser.add_argument("--lane", default="incoming_review")
    parser.add_argument("--job", required=True)
    parser.add_argument("--capability", choices=["economy", "workhorse", "frontier"], default=None)
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh"], default=None)
    parser.add_argument("--independence", choices=["single", "challenger", "panel"], default=None)
    args = parser.parse_args(argv)

    explicit = None
    if args.capability or args.effort or args.independence:
        explicit = Profile(
            capability=args.capability or "workhorse",
            effort=args.effort or "medium",
            independence=args.independence or "challenger",
        )

    config, _ = load_config(args.config)
    state = State(config)
    try:
        result = run_panel(config, state, args.repo, args.number, args.lane, args.job, explicit)
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    finally:
        state.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())