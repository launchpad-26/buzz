"""Human notification transports for review-queue-automation.

When a job needs a person, the durable record always lives in the SQLite human
queue. This module is only the *delivery* of that fact, so a delivery failure is
never allowed to imply the request was handled.

Transports (chosen by `notifications.transport` in the repo-local config):

    none      no delivery. Explicit opt-out; the queue is the only surface.
    file      append one JSON line to `notifications.path` (durable, greppable).
    command   run `notifications.command` with the packet JSON on stdin, so an
              operator can bridge to Slack/webhook/etc. without this skill
              embedding any vendor.

Rules:
- The packet is built from the durable request row only, so what a human reads
  matches what is queued.
- Values are bounded and redacted: no tokens, no PR body, no enveloped evidence.
- Delivery failure raises; callers must catch it and preserve the queued request.
- A transport never mutates GitHub, never touches the repository, and never
  decides anything.
"""

from __future__ import annotations

import json
import pathlib
import re
import shlex
import subprocess

NONE = "none"
FILE = "file"
COMMAND = "command"
TRANSPORTS = (NONE, FILE, COMMAND)

#: Hard ceiling on any single rendered field, so a packet stays readable and a
#: malformed upstream value cannot produce an unbounded notification.
MAX_FIELD = 400

#: Markers that indicate credential-shaped content inside a field VALUE. The
#: packet itself is built from a strict allowlist, so a smuggled *key* can never
#: reach a channel; the live risk is a token pasted into a legitimate field such
#: as `rationale`, which is why this scans values and redacts them.
_SECRET_VALUE_MARKERS = ("bearer ", "api_key", "apikey", "password", "secret",
                         "authorization:", "token=", "access_token", "private_key")

#: A JWT header followed by two dot-delimited segments.
_JWT = re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")

REDACTED = "<redacted>"


class NotifyError(RuntimeError):
    """Raised when delivery fails. The queued request must be left intact."""


class NotifyConfigError(ValueError):
    """Raised when the notification config is unusable."""


def _redact(text: str) -> str:
    """Redact a field value that looks like it carries credential material."""
    lowered = text.lower()
    if any(marker in lowered for marker in _SECRET_VALUE_MARKERS):
        return REDACTED
    if _JWT.search(text):
        return REDACTED
    return text


def _clip(value: Any) -> Any:
    if isinstance(value, str):
        text = _redact(value.strip())
        return text if len(text) <= MAX_FIELD else text[:MAX_FIELD] + "…"
    if isinstance(value, (list, tuple)):
        return [_clip(v) for v in list(value)[:20]]
    return value


def _as_list(value: Any) -> list[Any]:
    """Human-queue rows store JSON strings; accept either shape."""
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]
        return parsed if isinstance(parsed, list) else [parsed]
    return []


def build_packet(request: dict[str, Any], *, repo_slug: str = "") -> dict[str, Any]:
    """Render the operator-facing packet from a durable human-queue row.

    Everything here answers one question: what must a human decide, and on what
    evidence. It deliberately carries identifiers and paths rather than content,
    so no PR body or enveloped evidence can leak into a notification channel.
    """
    repo = request.get("repo") or repo_slug
    number = request.get("number")
    assurance = request.get("assurance")
    if isinstance(assurance, str) and assurance:
        try:
            assurance = json.loads(assurance)
        except json.JSONDecodeError:
            assurance = {"raw": assurance}

    packet = {
        "kind": "review_queue_human_request",
        "request_id": request.get("request_id"),
        "job_id": request.get("job_id"),
        "repo": repo,
        "pull_request": number,
        "url": f"https://github.com/{repo}/pull/{number}" if repo and number else "",
        "head_sha": request.get("head_sha"),
        "action_required": request.get("action"),
        "summary": _clip(request.get("summary")),
        "recommendation": _clip(request.get("recommendation")),
        "rationale": _clip(request.get("rationale")),
        "risk_score": request.get("risk_score"),
        "risk_band": request.get("risk_band"),
        "assurance": assurance,
        "reviewers": _clip(_as_list(request.get("reviewers"))),
        "failed_gates": _clip(_as_list(request.get("failed_gates"))),
        "protected_paths": _clip(_as_list(request.get("protected"))),
        "findings": _clip(_as_list(request.get("findings"))),
        "expires_at": request.get("expires_at"),
        "decide_with": (
            f"human_cli.py decide {request.get('request_id')} --approve|--decline"
            if request.get("request_id") else ""
        ),
    }
    return {k: v for k, v in packet.items() if v not in (None, "", [], {})}



def render_text(packet: dict[str, Any]) -> str:
    """One compact, self-explanatory block for a human channel."""
    lines = [
        f"{packet.get('repo', '?')}#{packet.get('pull_request', '?')} "
        f"needs your decision: {packet.get('action_required', 'review')}",
    ]
    if packet.get("url"):
        lines.append(packet["url"])
    if packet.get("summary"):
        lines.append(f"Summary: {packet['summary']}")
    if packet.get("rationale"):
        lines.append(f"Reason: {packet['rationale']}")
    if packet.get("failed_gates"):
        lines.append(f"Failed gates: {', '.join(str(g) for g in packet['failed_gates'])}")
    if packet.get("protected_paths"):
        lines.append(f"Protected paths: {', '.join(str(p) for p in packet['protected_paths'])}")
    if packet.get("risk_band"):
        lines.append(f"Risk: {packet.get('risk_score')} ({packet['risk_band']})")
    if packet.get("assurance"):
        lines.append(f"Assurance reached: {json.dumps(packet['assurance'], sort_keys=True)}")
    if packet.get("reviewers"):
        lines.append(f"Reviewers: {', '.join(str(r) for r in packet['reviewers'] if r)}")
    if packet.get("head_sha"):
        lines.append(f"Head: {packet['head_sha']}")
    if packet.get("expires_at"):
        lines.append(f"Expires: {packet['expires_at']}")
    if packet.get("decide_with"):
        lines.append(f"Decide: {packet['decide_with']}")
    return "\n".join(lines)


def transport_of(config: dict[str, Any]) -> str:
    section = config.get("notifications") or {}
    transport = (section.get("transport") or NONE).strip().lower()
    if transport not in TRANSPORTS:
        raise NotifyConfigError(
            f"notifications.transport must be one of {', '.join(TRANSPORTS)}, got {transport!r}"
        )
    return transport


def deliver(
    config: dict[str, Any],
    request: dict[str, Any],
    *,
    _runner=subprocess.run,
) -> dict[str, Any]:
    """Deliver one human request. Raises NotifyError on delivery failure.

    Returns a small delivery record describing what was attempted, so the caller
    can log it without re-deriving the transport.
    """
    transport = transport_of(config)
    packet = build_packet(request, repo_slug=(config.get("repository") or {}).get("slug", ""))

    if transport == NONE:
        return {"transport": NONE, "delivered": False,
                "detail": "no transport configured; request is queued only"}

    section = config.get("notifications") or {}

    if transport == FILE:
        target = section.get("path")
        if not target:
            raise NotifyConfigError("notifications.path is required for the file transport")
        path = pathlib.Path(target).expanduser()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(packet, sort_keys=True) + "\n")
        except OSError as exc:
            raise NotifyError(f"could not append notification to {path}: {exc}") from exc
        return {"transport": FILE, "delivered": True, "path": str(path)}

    # COMMAND
    raw = section.get("command")
    if not raw:
        raise NotifyConfigError("notifications.command is required for the command transport")
    argv = raw if isinstance(raw, list) else shlex.split(raw)
    if not argv:
        raise NotifyConfigError("notifications.command is empty")
    timeout = int(section.get("timeout_seconds", 30))
    payload = json.dumps({"packet": packet, "text": render_text(packet)}, sort_keys=True)
    try:
        proc = _runner(argv, input=payload.encode("utf-8"), capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise NotifyError(f"notification command timed out after {timeout}s") from exc
    except OSError as exc:
        raise NotifyError(f"notification command could not run: {exc}") from exc
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        raise NotifyError(f"notification command exit {proc.returncode}: {stderr[:300]}")
    return {"transport": COMMAND, "delivered": True, "command": argv[0]}
