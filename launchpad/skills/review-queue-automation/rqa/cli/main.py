"""`rqa` — the E-17 command surface and the E-21 `tick` entry point.

Parses arguments, builds the real collaborators (`rqa/cli/composition.py`),
calls exactly one provider per subcommand, renders the result
(`rqa/cli/render.py`) and picks an exit code (`rqa/cli/exitcodes.py`). It
never decides a disposition, reconstructs a record, validates a config or
resolves an escalation itself, and it writes no file of its own — `onboard`'s
write is `rqa.policy.onboard`'s, not this module's.

Providers called, one per subcommand, character-for-character as their own
lane states them:

* `tick`    -> `rqa.intake.tick` (imported through `rqa.intake`'s `__init__`,
              its one sanctioned form — see the module docstring on
              `tests/test_rqa_intake_surface.py`'s corrected premise).
* `status`  -> `rqa.lifecycle.status.status`
* `explain` -> `rqa.record.explain.explain` / `.explain_job`
* `decide`  -> `rqa.escalation.decide.decide`
* `pending` -> `rqa.escalation.escalate.pending` (E-17's `pending` IS E-11's)
* `onboard` -> `rqa.policy.onboard.onboard`
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, NoReturn

from rqa.cli import exitcodes
from rqa.cli.composition import anchor_job_for, build_composition
from rqa.cli.render import emit
from rqa.authority import GateError
from rqa.contracts import EscalationRefused, ExplanationUnavailable
from rqa.escalation import EscalationError, decide as escalation_decide, pending as escalation_pending
from rqa.intake import tick as intake_tick
from rqa.lifecycle import LifecycleError, NotFound, status as lifecycle_status
from rqa.policy import OnboardRefusal, onboard as policy_onboard
from rqa.record import AppendFailed, ReuseResolutionError, explain as record_explain, explain_job

__all__ = ["main"]

_DEFAULT_STATE_DIR = "RQA_STATE_DIR"
_REPOS_FILENAME = "repos.json"


class _UsageError(Exception):
    """A bad `rqa` invocation itself — an argparse failure, or an argument
    this module rejects before any provider is called. Always exit 1."""


class _ArgumentParser(argparse.ArgumentParser):
    """`argparse.ArgumentParser` with its default `SystemExit(2)` on a parse
    failure replaced by `_UsageError`, so every input mistake — missing
    argument, bad `type=int`, unknown subcommand — maps to this CLI's own
    `1` (input error), never argparse's unrelated `2`."""

    def error(self, message: str) -> NoReturn:  # pragma: no cover - argparse's own call shape
        raise _UsageError(message)


def _default_state_dir() -> Path:
    configured = os.environ.get(_DEFAULT_STATE_DIR)
    if configured is not None:
        if not configured.strip():
            raise _UsageError("RQA_STATE_DIR must not be empty")
        return Path(configured)
    return Path.home() / ".local" / "state" / "rqa"


def _configured_repos(state_dir: Path) -> tuple[str, ...]:
    """The repositories `rqa tick` sweeps when the operator names none on the
    command line — E-21's scheduler launches bare `rqa tick`, "no payload",
    so the swept set must already be durable. `<state_dir>/repos.json` (a
    JSON array of repo strings) is that durable set; an absent file is an
    empty sweep, not an error — the same "legitimately do very little"
    the task names for an unreachable GitHub.
    """
    import json

    path = state_dir / _REPOS_FILENAME
    if not path.exists():
        return ()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise _UsageError(f"{path}: not a readable JSON array of repos: {exc}") from exc
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise _UsageError(f"{path}: must be a JSON array of repo strings")
    return tuple(_repo_slug(item) for item in raw)


def _repo_slug(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", value):
        raise _UsageError("repository must be an owner/repo slug")
    if value.split("/")[1] in {".", ".."}:
        raise _UsageError("repository name cannot be . or ..")
    return value


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise _UsageError("expected a positive integer") from exc
    if number <= 0:
        raise _UsageError("expected a positive integer")
    return number


def _build_parser() -> _ArgumentParser:
    parser = _ArgumentParser(prog="rqa", description="Review Queue Automation operator CLI")
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help="state directory (default: $RQA_STATE_DIR or ~/.local/state/rqa)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    tick_parser = sub.add_parser("tick", help="one sweep over every configured repository")
    tick_parser.add_argument(
        "--repo",
        action="append",
        dest="repos",
        type=_repo_slug,
        default=None,
        help="repository to sweep (repeatable); default: <state-dir>/repos.json",
    )
    tick_parser.add_argument("--batch-size", type=_positive_int, default=None)

    onboard_parser = sub.add_parser("onboard", help="write a starter .rqa/config.json")
    onboard_parser.add_argument("repo", help="existing local repository directory; never created by this command")
    onboard_parser.add_argument("--migrate", action="store_true")

    status_parser = sub.add_parser("status", help="the current disposition and its reason")
    status_parser.add_argument("repo", type=_repo_slug)
    status_parser.add_argument("number", type=_positive_int)

    sub.add_parser("pending", help="open escalations, each naming its cause and question")

    decide_parser = sub.add_parser("decide", help="record a human decision")
    decide_parser.add_argument("escalation_id", type=_positive_int)
    decide_parser.add_argument("--actor", required=True)
    decide_parser.add_argument("--basis", required=True)
    decide_parser.add_argument(
        "--outcome", choices=("approved", "changes_requested"), default=None
    )

    anchor_parser = sub.add_parser(
        "anchor",
        help="publish a job's record chain head so a removed tail becomes detectable",
    )
    anchor_parser.add_argument(
        "anchor_target",
        metavar="job-id|recover",
        help="job id to publish, or 'recover' for external-anchor recovery",
    )
    anchor_parser.add_argument(
        "recovery_job_id",
        metavar="job-id",
        nargs="?",
        help="job id to recover after the literal 'recover'",
    )
    anchor_parser.add_argument(
        "--publisher",
        help="accepted GitHub login for anchor recovery; defaults to the job's stored capability proof",
    )

    explain_parser = sub.add_parser(
        "explain", help="reconstruct an outcome from the record alone, offline"
    )
    explain_parser.add_argument("first", metavar="repo|job", help="owner/repo, or literal 'job' to select a job id")
    explain_parser.add_argument("second", metavar="number|job-id", help="positive PR number, or job id after 'job'")

    return parser


def _cmd_tick(args: argparse.Namespace, state_dir: Path) -> tuple[int, dict[str, Any]]:
    repos = tuple(args.repos) if args.repos else _configured_repos(state_dir)
    comp = build_composition(state_dir, repos=repos)
    kwargs: dict[str, Any] = {}
    if args.batch_size is not None:
        kwargs["batch_size"] = args.batch_size
    try:
        result = intake_tick(
            repos=repos,
            github=comp.github,
            policy=comp.policy,
            authority=comp.authority,
            supply=comp.supply,
            harness=comp.harness,
            judgement=comp.judgement,
            remediation=comp.remediation,
            escalation=comp.escalation,
            reuse=comp.reuse,
            jobs=comp.jobs,
            pr_facts=comp.pr_facts,
            leases=comp.leases,
            record=comp.record,
            connection=comp.connection,
            state_dir=state_dir,
            runner=comp.runner,
            **kwargs,
        )
    except Exception:
        # `tick()` documents `IntakeError`/`AppendFailed` as always propagating
        # (P-01 §3): whatever partial per-repo/per-job commit it already made
        # stands (tick.py commits per iteration itself), but nothing this call
        # left uncommitted on this connection may become durable.
        comp.connection.rollback()
        raise
    comp.connection.commit()
    if result.repos_failed:
        reasons = {failure.reason for failure in result.repos_failed}
        code = (exitcodes.AUTH if "unauthenticated" in reasons else
                exitcodes.OTHER if "internal_error" in reasons else exitcodes.NETWORK)
        return code, {"outcome": "incomplete", "result": result}
    if result.jobs_failed:
        return exitcodes.OTHER, {"outcome": "incomplete", "result": result}
    if result.repos_refused:
        return exitcodes.INPUT_ERROR, {"outcome": "refused", "result": result}
    return exitcodes.OK, {"outcome": result.outcome, "result": result}


def _cmd_onboard(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if not args.repo.strip() or not Path(args.repo).is_dir():
        raise _UsageError("onboard requires an existing local repository directory")
    result = policy_onboard(repo=args.repo, migrate=args.migrate)
    if isinstance(result, OnboardRefusal):
        return exitcodes.INPUT_ERROR, {"outcome": "refused", "result": result}
    return exitcodes.OK, {"outcome": "written", "result": result}


def _cmd_status(args: argparse.Namespace, state_dir: Path) -> tuple[int, dict[str, Any]]:
    comp = build_composition(state_dir)
    result = lifecycle_status(args.repo, args.number, connection=comp.connection)
    if isinstance(result, NotFound):
        return exitcodes.INPUT_ERROR, {"outcome": "not_found", "result": result}
    return exitcodes.OK, {"outcome": "ok", "result": result}


def _cmd_pending(state_dir: Path) -> tuple[int, dict[str, Any]]:
    comp = build_composition(state_dir)
    escalations = escalation_pending(store=comp.escalation_store)
    return exitcodes.OK, {"outcome": "ok", "result": escalations}


def _cmd_decide(args: argparse.Namespace, state_dir: Path) -> tuple[int, dict[str, Any]]:
    comp = build_composition(state_dir, repos=_configured_repos(state_dir))
    try:
        result = escalation_decide(
            args.escalation_id,
            args.actor,
            args.basis,
            args.outcome,
            store=comp.escalation_store,
            record=comp.record,
            jobs=comp.job_reader(),
            lifecycle=comp.lifecycle_resume(),
            deps=comp.lifecycle_deps(),
        )
    except EscalationError as exc:
        comp.connection.rollback()
        return exitcodes.INPUT_ERROR, {"outcome": "rejected", "detail": str(exc)}
    except Exception:
        # Deliberate, not accidental: `decide()` opens `record.append`,
        # `store.close` and `lifecycle.resume` on this one connection with no
        # commit between them (E-13's "one atomic fact"). Any exception here
        # — `AppendFailed`, `LifecycleError`, or anything else — means that
        # sequence did not complete, so nothing it touched may become durable.
        comp.connection.rollback()
        raise
    comp.connection.commit()
    if isinstance(result, EscalationRefused):
        return exitcodes.INPUT_ERROR, {"outcome": "refused", "result": result}
    return exitcodes.OK, {"outcome": "decided", "escalation_id": args.escalation_id, "result": result}


def _cmd_anchor(args: argparse.Namespace, state_dir: Path) -> tuple[int, dict[str, Any]]:
    """ADR-0066's anchored chain head (#2300).

    Always exits 0 when it ran: an anchor that could not be published is a reported
    state, not an error. The local anchor row is written either way, and that is what
    detects a crash-truncated log with no network at all. Anchoring must never be able
    to fail a review.
    """
    job_id, recovery = _anchor_request(args)
    comp = build_composition(state_dir, repos=_configured_repos(state_dir))
    try:
        outcome = anchor_job_for(
            comp, job_id, publisher=args.publisher, recover=recovery
        )
    except Exception:
        # A gate or record failure is not an anchor outcome.  Preserve the CLI's
        # atomic boundary rather than leaving an in-process caller with a partial
        # grant/attestation transaction after the error has been rendered.
        comp.connection.rollback()
        raise
    if not recovery:
        comp.connection.commit()
        return exitcodes.OK, {"outcome": "ok", "result": outcome}

    # Recovery is allowed to commit only the authenticated evidence imported for a
    # FOUND result. Every other result is explicitly rolled back so a failed recovery
    # cannot mutate the local state it is supposed to repair.
    recovery_outcome = outcome.outcome
    if recovery_outcome == "recovered":
        comp.connection.commit()
        return exitcodes.OK, {"outcome": recovery_outcome, "result": outcome}
    comp.connection.rollback()
    code = {
        "none": exitcodes.INPUT_ERROR,
        "unavailable": exitcodes.NETWORK,
        "unauthenticated": exitcodes.AUTH,
        "malformed": exitcodes.OTHER,
        "conflict": exitcodes.OTHER,
        "no_job": exitcodes.INPUT_ERROR,
        "publisher_unavailable": exitcodes.INPUT_ERROR,
    }.get(recovery_outcome, exitcodes.OTHER)
    return code, {"outcome": recovery_outcome, "result": outcome}


def _anchor_request(args: argparse.Namespace) -> tuple[str, bool]:
    """Normalise the legacy publish form and explicit ``anchor recover`` form."""
    if args.anchor_target == "recover":
        if args.recovery_job_id is None:
            raise _UsageError("anchor recover requires a job-id")
        return args.recovery_job_id, True
    if args.recovery_job_id is not None:
        raise _UsageError("anchor accepts one job-id, or 'anchor recover <job-id>'")
    return args.anchor_target, False


def _cmd_explain(args: argparse.Namespace, state_dir: Path) -> tuple[int, dict[str, Any]]:
    comp = build_composition(state_dir)
    if args.first == "job":
        result = explain_job(comp.connection, args.second)
    else:
        try:
            number = _positive_int(args.second)
        except _UsageError as exc:
            raise _UsageError(
                f"explain: PR number must be an integer, got {args.second!r}"
            ) from exc
        result = record_explain(comp.connection, _repo_slug(args.first), number)
    if isinstance(result, ExplanationUnavailable):
        return exitcodes.INPUT_ERROR, {"outcome": "unavailable", "subject": {"job_id": args.second} if args.first == "job" else {"repo": args.first, "number": number}, "result": result}
    return exitcodes.OK, {"outcome": "ok", "result": result}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except _UsageError as exc:
        emit({"outcome": "usage_error", "detail": str(exc)})
        return exitcodes.INPUT_ERROR

    try:
        state_dir = args.state_dir if args.state_dir is not None else _default_state_dir()
        recovery = args.command == "anchor" and _anchor_request(args)[1]
        if args.command in {"status", "pending", "decide", "explain"} or recovery:
            if not (state_dir / "state.db").exists():
                raise _UsageError(f"no RQA state database at {state_dir}; check --state-dir or run tick to initialise it")
        if args.command == "onboard":
            code, payload = _cmd_onboard(args)
        elif args.command == "tick":
            code, payload = _cmd_tick(args, state_dir)
        elif args.command == "status":
            code, payload = _cmd_status(args, state_dir)
        elif args.command == "pending":
            code, payload = _cmd_pending(state_dir)
        elif args.command == "decide":
            code, payload = _cmd_decide(args, state_dir)
        elif args.command == "anchor":
            code, payload = _cmd_anchor(args, state_dir)
        elif args.command == "explain":
            code, payload = _cmd_explain(args, state_dir)
        else:  # pragma: no cover - argparse's `required=True` makes this unreachable
            raise _UsageError(f"unknown command {args.command!r}")
    except _UsageError as exc:
        emit({"outcome": "usage_error", "detail": str(exc)})
        return exitcodes.INPUT_ERROR
    except (LifecycleError, GateError, AppendFailed, ReuseResolutionError) as exc:
        # A part's own programming-error exception, never suppressed and never
        # retried here: `LifecycleError` (a corrupted or illegally-transitioned
        # job), `GateError` (wrong-shaped authority call), `AppendFailed` (the
        # record itself could not be written), and `ReuseResolutionError` (a
        # broken `reused_from` chain) are genuine defects this CLI did not
        # anticipate, not values any provider licenses it to interpret.
        emit({"outcome": "error", "error_type": type(exc).__name__, "detail": str(exc)})
        return exitcodes.OTHER
    except Exception as exc:
        # `main()` is the process boundary. Provider and infrastructure
        # exceptions not assigned a narrower meaning above still need the
        # command surface's one-JSON-object guarantee and exit code 4.
        emit({"outcome": "error", "error_type": type(exc).__name__, "detail": str(exc)})
        return exitcodes.OTHER

    payload["command"] = args.command
    emit(payload)
    return code


if __name__ == "__main__":
    sys.exit(main())
