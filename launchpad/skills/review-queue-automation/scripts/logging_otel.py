"""Structured, append-only job logging for review-queue-automation.

Writes OTel Collector `filelog`-ingestible JSON Lines under the configured log
directory:

    <logging.directory>/
      jobs/<job-id>/
        events.jsonl            append-only, one JSON object per event
        attempts/
          attempt-001.json      immutable per panel invocation
          attempt-002.json
        diagnostics/
          attempt-001-claude.stderr.txt   (stderr excerpt, capped at 8 KB)

Design rules enforced here:
- Append-only JSONL; every line is a complete, parseable JSON object. Appends
  take an advisory `fcntl` lock so concurrent processes/threads cannot interleave
  partial lines.
- Fields (service version, head sha, phase, outcome, error disposition, decision,
  request id, risk) are carried on the event/attempt payload when supplied.
- Never log secrets, tokens, bearer/JWT credentials, full PR bodies, nonce-enveloped
  evidence, or unbounded stderr. Values are recursively sanitized; keys that look
  sensitive are redacted.
- Stderr is only ever written as a capped (UTF-8 byte-aware) redacted diagnostic
  file; events carry just the error class and a short safe summary.
- No SDKs, no exporters, no network: it is a deterministic local writer.
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any

from common import utcnow

try:  # UNIX: JWT/attempt caps and file locking rely on fcntl.
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None

SERVICE_NAME = "review-queue-automation"
MAX_STDERR_BYTES = 8192
FORMAT = "otel-jsonl"
LOG_SCHEMA_VERSION = 1

#: The canonical event names the ORCHESTRATOR must emit for one job. They are
#: named here, not in the dispatcher, so a trace consumer (and
#: `tests/test_dispatch_observability.py`) has one authority for what a complete
#: job trace looks like. `JobLogger` was previously constructed by the dispatcher
#: and never called on: a job left no orchestrator-emitted trace at all, only
#: whatever `common.State.transition` happened to log.
JOB_EVENTS: tuple[str, ...] = (
    "queueing",         # the job was selected for dispatch
    "preflight",        # config/snapshot/capability/canary checks concluded
    "lease_acquired",   # the review lease was claimed, before any model spend
    "lease_released",   # the review lease was released, on every exit path
    "evidence",         # the evidence bundle backing this job
    "budget",           # the pre-spend cost reservation and its headroom
    "planner",          # the deterministic review plan
    "strategy",         # which reasoning strategy and fallback recipe ran
    "route_selection",  # which model route actually executed
    "rereview",         # this head supersedes a previously reviewed one
    "decision",         # the disposition the job reached, and why
    "human_queue",      # a durable human request was enqueued
    "mutation",         # an external (GitHub) action was attempted
    "verify",           # a revalidation of the reviewed head
    "safe_stop",        # the job stopped safely without completing
)

#: Events that MUST appear in any job that reaches a terminal decision. A job may
#: legitimately skip `mutation`/`human_queue`/`safe_stop`/`rereview` depending on
#: the branch it takes; everything else is unconditional.
REQUIRED_JOB_EVENTS: frozenset[str] = frozenset(
    {"queueing", "preflight", "evidence", "budget", "planner", "strategy",
     "route_selection", "decision", "verify"}
)

#: Attribute magnitude cap. Cost/token/latency numbers are diagnostic, so an
#: absurd value is clamped rather than logged verbatim or dropped.
MAX_METRIC_VALUE = 1_000_000_000

#: Metric attribute names containing the substring "token". `_is_sensitive_key`
#: matches "token" anywhere in a key, so a legitimate TOKEN COUNT was being
#: written to the log as "<redacted>" — an observability control silently eaten
#: by a security control. These exact names are allowed through, and only these:
#: the allowlist is closed, and `metric_attributes` is their only producer.
METRIC_TOKENS = "cost.tokens"
METRIC_TOKENS_RESERVED = "cost.tokens_reserved"
SAFE_METRIC_KEYS: frozenset[str] = frozenset({METRIC_TOKENS, METRIC_TOKENS_RESERVED})

SENSITIVE_KEY_MARKERS = (
    "token", "api_key", "apikey", "password", "secret", "authorization",
    "bearer", "credential",
)


def metric_attributes(
    *,
    tokens: int | None = None,
    tokens_reserved: int | None = None,
    latency_ms: int | None = None,
    attempts: int | None = None,
) -> dict[str, Any]:
    """Bounded cost/token/latency attributes for an event.

    Every value is coerced to a non-negative integer and clamped, so a runaway
    counter or a negative clock delta cannot land in the log as-is. Absent values
    are omitted rather than logged as zero, because "not measured" and "zero" are
    different facts.
    """
    pairs = (
        (METRIC_TOKENS, tokens),
        (METRIC_TOKENS_RESERVED, tokens_reserved),
        ("latency.ms", latency_ms),
        ("review.attempts", attempts),
    )
    out: dict[str, Any] = {}
    for key, value in pairs:
        if value is None:
            continue
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        out[key] = max(0, min(MAX_METRIC_VALUE, number))
    return out


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(m in lowered for m in SENSITIVE_KEY_MARKERS)


def _safe_artifact_rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def sanitize_value(value: Any) -> Any:
    """Return a log-safe scalar; anything not trivially safe is coerced to a summary.
    Recurses through lists and dicts so nested sensitive values are also scrubbed."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        # Skip anything that looks like credential material or evidence envelope/body.
        if any(marker in lowered for marker in ("token", "api_key", "password", "secret", "bearer ", "authorization")):
            return "<redacted>"
        if "<<<" in value or "END:pr_" in value or "nonce" in lowered:
            return "<redacted-evidence>"
        # JWT-shaped strings must never leak even when the key is innocuous.
        if _looks_like_jwt(value):
            return "<redacted-jwt>"
        # A long string is likely a body/artifact; summarize rather than leaking it.
        if len(value) > 400:
            return f"<{len(value)} chars redacted>"
        value = value.strip()
        return value if len(value) <= 200 else value[:200] + "…"
    if isinstance(value, (list, tuple)):
        return [sanitize_value(x) for x in value[:20]]
    if isinstance(value, dict):
        return {str(k)[:60]: sanitize_value(v) for k, v in list(value.items())[:20]}
    return str(value)[:120]


def _looks_like_jwt(value: str) -> bool:
    """Cheap scan: a JWT header `eyJ...` followed by two dot-delimited segments."""
    import re as _re

    return bool(_re.search(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", value))


class JobLogger:
    """Append-only structured logger for one job under a configured log directory."""

    def __init__(
        self,
        log_root: pathlib.Path | str,
        job_id: str,
        *,
        repo: str = "",
        number: int = 0,
        lane: str = "",
        max_stderr: int = MAX_STDERR_BYTES,
        service_version: str = "",
        head: str = "",
    ):
        self.log_root = pathlib.Path(log_root)
        self.job_id = job_id
        self.repo = repo
        self.number = number
        self.lane = lane
        self.max_stderr = max_stderr
        self.service_version = sanitize_value(service_version) or ""
        self.head = sanitize_value(head) or ""
        self.job_dir = self.log_root / "jobs" / job_id
        self.attempts_dir = self.job_dir / "attempts"
        self.diag_dir = self.job_dir / "diagnostics"
        self.events_path = self.job_dir / "events.jsonl"
        for d in (self.job_dir, self.attempts_dir, self.diag_dir):
            d.mkdir(parents=True, exist_ok=True)

    # -- low-level ------------------------------------------------
    def _append_event(self, event: dict[str, Any]) -> None:
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self.events_path.open("a", encoding="utf-8") as handle:
            # Advisory interprocess/thread lock so a line is never written in halves.
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                handle.write(line + "\n")
                handle.flush()
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _base_attributes(self, phase: str, outcome: str) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "job.id": self.job_id,
            "github.repository": sanitize_value(self.repo),
            "github.pull_request.number": self.number,
            "review.lane": sanitize_value(self.lane),
            "review.phase": sanitize_value(phase),
            "review.outcome": sanitize_value(outcome),
        }
        if self.head:
            attrs["github.head.sha"] = sanitize_value(self.head)
        if self.service_version:
            attrs["service.version"] = self.service_version
        return attrs

    def _event(
        self,
        *,
        severity_text: str,
        body: str,
        phase: str,
        outcome: str,
        attributes: dict[str, Any] | None = None,
        event_name: str = "review_automation",
    ) -> None:
        event: dict[str, Any] = {
            "timestamp": utcnow(),
            "severity_text": severity_text,
            "body": sanitize_value(body),
            "schema_version": LOG_SCHEMA_VERSION,
            "event_name": event_name,
            "resource": {"service.name": SERVICE_NAME},
            "attributes": self._base_attributes(phase, outcome),
        }
        if self.service_version:
            event["resource"]["service.version"] = self.service_version
        if attributes:
            for key, value in attributes.items():
                skey = str(key)
                if _is_sensitive_key(skey) and skey not in SAFE_METRIC_KEYS:
                    event["attributes"][skey] = "<redacted>"
                else:
                    event["attributes"][skey] = sanitize_value(value)
        self._append_event(event)

    # -- public API -------------------------------------------------
    def info(self, *, body: str, phase: str, outcome: str = "", attributes: dict[str, Any] | None = None, event_name: str = "info") -> None:
        self._event(severity_text="INFO", body=body, phase=phase, outcome=outcome or phase, attributes=attributes, event_name=event_name)

    def warning(self, *, body: str, phase: str, outcome: str = "", attributes: dict[str, Any] | None = None, event_name: str = "warning") -> None:
        self._event(severity_text="WARN", body=body, phase=phase, outcome=outcome or phase, attributes=attributes, event_name=event_name)

    def error(self, *, body: str, phase: str, outcome: str = "error", attributes: dict[str, Any] | None = None, event_name: str = "error") -> None:
        self._event(severity_text="ERROR", body=body, phase=phase, outcome=outcome, attributes=attributes, event_name=event_name)

    def transition(
        self,
        prior: str | None,
        next_: str,
        *,
        phase: str,
        reason: str = "",
        attributes: dict[str, Any] | None = None,
    ) -> None:
        attrs = dict(attributes or {})
        if prior is None:
            attrs["job.status"] = next_
        else:
            attrs["job.prior_status"] = prior
            attrs["job.status"] = next_
        if reason:
            attrs["job.reason"] = sanitize_value(reason)
        self._event(
            severity_text="INFO",
            body=f"state transition: {prior or '<new>'} -> {next_}",
            phase=phase,
            outcome="transition",
            attributes=attrs,
        )

    # -- artifacts ---------------------------------------------------
    def attempt(self, attempt: dict[str, Any]) -> int:
        """Write an immutable attempt-###.json atomically and race-free.

        Allocation reserves the next free number with O_CREAT|O_EXCL; two
        concurrent callers cannot choose the same number. Content is then written
        atomically via rename (no lock needed for the immutable file itself).
        """
        number = 0
        while True:
            number += 1
            path = self.attempts_dir / f"attempt-{number:03d}.json"
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
                os.close(fd)
            except FileExistsError:
                continue
            break
        payload = {
            "attempt": number,
            "job.id": self.job_id,
            "github.repository": sanitize_value(self.repo),
            "github.pull_request.number": self.number,
            "review.lane": sanitize_value(self.lane),
        }
        if self.head:
            payload["github.head.sha"] = sanitize_value(self.head)
        if self.service_version:
            payload["service.version"] = self.service_version
        for key, value in attempt.items():
            skey = str(key)
            if _is_sensitive_key(skey) and skey not in SAFE_METRIC_KEYS:
                payload[skey] = "<redacted>"
            else:
                payload[skey] = sanitize_value(value)
        content = json.dumps(payload, indent=2, sort_keys=True)
        _atomic_replace(path, content)
        return number

    def diagnostic(self, name: str, stderr: str, *, attempt: int, candidate: str = "") -> str:
        """Persist a bounded stderr excerpt. Returns the relative artifact path."""
        safe_name = "".join(c for c in name if c.isalnum() or c in "._-")
        candidate_tag = "".join(c for c in candidate if c.isalnum() or c in "._-") or "candidate"
        file_name = f"attempt-{attempt:03d}-{candidate_tag}-{safe_name}.txt"
        path = self.diag_dir / file_name
        # Redact then cap on UTF-8 BYTES without splitting a multi-byte character.
        redacted = _redact_text(str(stderr))
        encoded = redacted.encode("utf-8")[: self.max_stderr]
        while True:
            try:
                capped = encoded.decode("utf-8")
                break
            except UnicodeDecodeError:
                encoded = encoded[:-1]
        _atomic_replace(path, capped)
        return _safe_relative(self.log_root, path)

    def event_path(self) -> pathlib.Path:
        return self.events_path


def _safe_relative(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_events(event_path: pathlib.Path) -> list[dict[str, Any]]:
    """Read back every event as parsed JSON (test/tooling helper)."""
    if not event_path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in event_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _atomic_replace(path: pathlib.Path, content: str) -> None:
    """Atomically write `content` to `path` (temp file + os.replace)."""
    import tempfile as _tf

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = _tf.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# Correct, anchored JWT pattern: `eyJ...` header, then two dot-delimited payload and
# signature segments. Uses a word-boundary start and a trailing boundary so a longer
# base-64 token is matched without splitting it. Multi-byte-safe (operates on str).
_JWT_PATTERN = (r"(?i)\b(eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)")


def _redact_text(text: str) -> str:
    """Recursively scrub secret-like values from diagnostic text (best-effort).

    Handles key=value pairs, `gh*_...` token prefixes, and JWT-shaped strings. The
    JWT regex is anchored on a JWT header so a bare base-64 payload isn't over-matched.
    """
    import re as _re

    out = text
    patterns = (
        (r"(?i)(token|api[_-]?key|secret|password|authorization|bearer)[=: ]+([A-Za-z0-9._\-]+)", r"\1=<redacted>"),
        (r"(?i)(gh[pousr]_[A-Za-z0-9_]{20,})", "<redacted-token>"),
        (_JWT_PATTERN, "<redacted-jwt>"),
    )
    for pattern, repl in patterns:
        out = _re.sub(pattern, repl, out)
    return out