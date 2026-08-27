"""Deterministic error taxonomy and disposition matrix for review-queue-automation.

Two surfaces:

- `classify_error(text)` — legacy coarse classifier returning one of the three
  historical codes (TRANSIENT / CANDIDATE_TERMINAL / JOB_BLOCKING). Kept for
  backward compatibility with existing tests and simple callers.

- `classify_disposition(text)` — fine-grained disposition driving the approval
  policy (see DISPOSITIONS). This is what the dispatcher and panel use.

Typed RQAError subclasses carry a `disposition` used for policy decisions.
"""

from __future__ import annotations

from typing import Any

# ---- legacy coarse codes (kept for compatibility) --------------------------
TRANSIENT = "transient"
CANDIDATE_TERMINAL = "candidate_terminal"
JOB_BLOCKING = "job_blocking"

# ---- detailed dispositions (spec) -------------------------------------------
TRANSIENT_INFRA = "transient_infrastructure"
EVIDENCE_INCOMPLETE = "evidence_incomplete"
INVALID_CONFIG = "invalid_config"
POLICY_PROTECTED = "policy_protected"
DECISION_STALE = "decision_stale"
STATE_PERSISTENCE = "state_persistence"
AUDIT_LOGGING_FAILURE = "audit_logging_failure"
NOTIFICATION_FAILURE = "notification_failure"
MUTATION_UNCERTAIN = "mutation_uncertain"
PERMISSION_AUTHORITY = "permission_authority"
EXTERNAL_VERIFICATION = "external_verification"

_DISPOSITIONS = frozenset(
    {
        TRANSIENT_INFRA, CANDIDATE_TERMINAL, EVIDENCE_INCOMPLETE, INVALID_CONFIG,
        POLICY_PROTECTED, JOB_BLOCKING, DECISION_STALE, STATE_PERSISTENCE,
        AUDIT_LOGGING_FAILURE, NOTIFICATION_FAILURE, MUTATION_UNCERTAIN,
        PERMISSION_AUTHORITY, EXTERNAL_VERIFICATION,
    }
)

# ---- token tables ------------------------------------------------------------
TRANSIENT_TOKENS = (
    "timeout", "timed out", "network", "connection", "reset", "5xx", "502", "503",
    "504", "temporarily", "econnreset", "econnrefused", "dns", "tls", "http error 5",
)
CANDIDATE_TERMINAL_TOKENS = (
    "quota", "rate limit", "rate-limit", "insufficient_quota", "model_not_found",
    "not found", "unavailable model", "model does not exist", "auth", "unauthorized",
    "401", "403", "invalid_api_key", "malformed", "invalid schema", "schema error",
    "does not match schema", "signal",
)
JOB_BLOCKING_TOKENS = (
    "invalid config", "configuration missing", "config not", "config missing",
    "config is missing", "config is required", "unknown runner", "missing evidence",
    "evidence.txt missing", "illegal transition", "invalid state transition",
    "not ignored", "tracked", "config.json", "config is tracked", "config not ignored",
    "nonexistent job", "no such job",
)


def _hit(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(t in lowered for t in tokens)


def classify_error(text: str) -> str:
    """Legacy coarse classification (see module docstring). Unknown -> CANDIDATE_TERMINAL."""
    source = text or ""
    if not source.strip():
        return CANDIDATE_TERMINAL
    if _hit(source, JOB_BLOCKING_TOKENS):
        return JOB_BLOCKING
    if _hit(source, TRANSIENT_TOKENS):
        return TRANSIENT
    if _hit(source, CANDIDATE_TERMINAL_TOKENS):
        return CANDIDATE_TERMINAL
    return CANDIDATE_TERMINAL


# ---- detailed disposition classifier -----------------------------------------
_DISPOSITION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (INVALID_CONFIG, ("invalid config", "config missing", "config is missing", "config is required", "config is tracked", "config not ignored", "onboarding_required")),
    (EVIDENCE_INCOMPLETE, ("missing evidence", "evidence incomplete", "gather evidence", "evidence.txt missing")),
    (JOB_BLOCKING, ("illegal transition", "invalid state transition", "unknown runner", "nonexistent job", "no such job")),
    (DECISION_STALE, ("expired", "stale decision", "stale sha", "stale policy", "decision expired", "superseded")),
    (POLICY_PROTECTED, ("protected trigger", "policy protected", "forbidden surface", "high-consequence")),
    (MUTATION_UNCERTAIN, ("mutation uncertain", "unable to verify", "uncertain mutation", "cannot confirm")),
    (PERMISSION_AUTHORITY, ("permission", "unauthorized", "not authorized", "forbidden", "approval denied by authority")),
    (TRANSIENT_INFRA, TRANSIENT_TOKENS),
    (CANDIDATE_TERMINAL, CANDIDATE_TERMINAL_TOKENS),
)


def classify_disposition(text: str) -> str:
    """Detailed disposition from a message. Unknown -> CANDIDATE_TERMINAL."""
    source = text or ""
    if not source.strip():
        return CANDIDATE_TERMINAL
    for disposition, tokens in _DISPOSITION_RULES:
        if _hit(source, tokens):
            return disposition
    return CANDIDATE_TERMINAL


class RQAError(Exception):
    """Base error; carries a machine-readable disposition."""

    disposition = CANDIDATE_TERMINAL

    def __init__(self, message: str, *, disposition: str | None = None):
        super().__init__(message)
        if disposition is not None:
            self.disposition = disposition

    def as_event(self) -> dict[str, Any]:
        return {
            "error.class": self.__class__.__name__,
            "error.disposition": self.disposition,
            "error.message": str(self)[:300],
        }


class TransientError(RQAError):
    disposition = TRANSIENT_INFRA


class CandidateTerminalError(RQAError):
    disposition = CANDIDATE_TERMINAL


class EvidenceIncompleteError(RQAError):
    disposition = EVIDENCE_INCOMPLETE


class InvalidConfigError(RQAError):
    disposition = INVALID_CONFIG


class PolicyProtectedError(RQAError):
    disposition = POLICY_PROTECTED


class JobBlockingError(RQAError):
    disposition = JOB_BLOCKING

    def __init__(self, message: str):
        super().__init__(message, disposition=JOB_BLOCKING)


class DecisionStaleError(RQAError):
    disposition = DECISION_STALE


class StatePersistenceError(RQAError):
    disposition = STATE_PERSISTENCE


class AuditLoggingError(RQAError):
    disposition = AUDIT_LOGGING_FAILURE


class NotificationFailureError(RQAError):
    disposition = NOTIFICATION_FAILURE


class MutationUncertainError(RQAError):
    disposition = MUTATION_UNCERTAIN


class PermissionAuthorityError(RQAError):
    disposition = PERMISSION_AUTHORITY


class ExternalVerificationError(RQAError):
    disposition = EXTERNAL_VERIFICATION


def wrap_error(exc: BaseException) -> RQAError:
    """Wrap an arbitrary exception as a typed RQAError (idempotent for RQAError)."""
    if isinstance(exc, RQAError):
        return exc
    disposition = classify_disposition(str(exc))
    return RQAError(str(exc), disposition=disposition)

# ---------------------------------------------------------------------------
# Error category registry: retryability + authority + severity + escalation
# ---------------------------------------------------------------------------
# Disposition metadata drives safe degradation. `authority_impact` expresses how
# the category constrains autonomy:
#   none       -> no change to authority
#   no_mutate  -> block mutating actions for this job/cycle
#   escalate   -> route to human escalation
#   safe_stop  -> stop the affected job (never widen authority)
CATEGORY_META: dict[str, dict[str, Any]] = {
    TRANSIENT_INFRA: {"retryable": True, "behavior": "retry_same_once_then_next", "authority_impact": "none", "severity": "WARN", "escalate": False},
    CANDIDATE_TERMINAL: {"retryable": True, "behavior": "cooldown_then_fallback", "authority_impact": "none", "severity": "WARN", "escalate": False},
    EVIDENCE_INCOMPLETE: {"retryable": True, "behavior": "one_bounded_gather", "authority_impact": "no_mutate", "severity": "WARN", "escalate": True},
    INVALID_CONFIG: {"retryable": False, "behavior": "onboarding_required", "authority_impact": "safe_stop", "severity": "ERROR", "escalate": True},
    POLICY_PROTECTED: {"retryable": False, "behavior": "human_required", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    JOB_BLOCKING: {"retryable": False, "behavior": "human_required", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    DECISION_STALE: {"retryable": False, "behavior": "supersede", "authority_impact": "no_mutate", "severity": "WARN", "escalate": False},
    STATE_PERSISTENCE: {"retryable": False, "behavior": "safe_stop_job", "authority_impact": "safe_stop", "severity": "ERROR", "escalate": True},
    AUDIT_LOGGING_FAILURE: {"retryable": True, "behavior": "retry_log_then_safe", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    NOTIFICATION_FAILURE: {"retryable": True, "behavior": "preserve_and_retry", "authority_impact": "none", "severity": "WARN", "escalate": False},
    MUTATION_UNCERTAIN: {"retryable": True, "behavior": "reconcile_then_retry", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    PERMISSION_AUTHORITY: {"retryable": False, "behavior": "no_approval", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    EXTERNAL_VERIFICATION: {"retryable": True, "behavior": "retry_verify", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    # spec categories that map onto dispositions / markers
    "rate_limit": {"retryable": True, "behavior": "backoff_then_next", "authority_impact": "none", "severity": "WARN", "escalate": False},
    "provider_unavailable": {"retryable": True, "behavior": "cooldown_then_next", "authority_impact": "none", "severity": "WARN", "escalate": False},
    "model_unavailable": {"retryable": True, "behavior": "cooldown_then_next", "authority_impact": "none", "severity": "WARN", "escalate": False},
    "invalid_model_output": {"retryable": False, "behavior": "discard_participant", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": False},
    "state_conflict": {"retryable": True, "behavior": "reconcile_state", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    "invariant_violation": {"retryable": False, "behavior": "safe_stop", "authority_impact": "safe_stop", "severity": "CRITICAL", "escalate": True},
    "authentication": {"retryable": False, "behavior": "no_approval", "authority_impact": "no_mutate", "severity": "ERROR", "escalate": True},
    "policy_validation": {"retryable": False, "behavior": "retain_last_known_good", "authority_impact": "safe_stop", "severity": "ERROR", "escalate": True},
    "invalid_transition": {"retryable": False, "behavior": "reject_no_change", "authority_impact": "no_mutate", "severity": "WARN", "escalate": False},
}

# Every disposition referenced above must resolve.
for _k in list(CATEGORY_META):
    if _k not in _DISPOSITIONS and _k not in ("rate_limit", "provider_unavailable",
                                               "model_unavailable", "invalid_model_output",
                                               "state_conflict", "invariant_violation",
                                               "authentication", "policy_validation",
                                               "invalid_transition"):
        # these are additional named categories, not dispositions
        pass


def category_meta(disposition: str) -> dict[str, Any]:
    """Return the safety metadata for a disposition/category (fail-safe unknown)."""
    return CATEGORY_META.get(disposition, {
        "retryable": False,
        "behavior": "safe_stop",
        "authority_impact": "no_mutate",
        "severity": "ERROR",
        "escalate": True,
    })
