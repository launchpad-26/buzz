"""Repo-local configuration for review-queue-automation.

The authoritative per-repository runtime config lives at:

    <repo>/.review-queue-automation/config.json

Rules (enforced here):
- The config is local and must be git-ignored.
- `.review-queue-automation/` must be in the repository's `.gitignore`.
- No secrets/tokens in the config; auth stays in environment/keychain.
- A populated config is never placed under version control.
- Main automation refuses dispatch on missing/unreadable/invalid/tracked/not
  ignored config and directs the operator to onboarding.

A tracked example template lives in the skill library (`config.example.json`)
but is never a populated config.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from typing import Any

RQA_CONFIG_DIR = ".review-queue-automation"
CONFIG_FILENAME = "config.json"
DEFAULT_LOG_DIR_NAME = "pr review logs"
REQUIRED_KEYS = {
    "version",
    "login",
    "state_dir",
    "repository",
    "logging",
    "models",
    "assurance",
    "dispatch",
    "github",
    "approval",
    "risk",
    "human_queue",
    "shadow",
}
REPOSITORY_KEYS = {"slug", "root", "base"}
LOGGING_KEYS = {"directory", "format"}

#: The two repo-relative paths (dir form) that must be git-ignored + untracked.
IGNORED_REL_PATHS = (RQA_CONFIG_DIR + "/", DEFAULT_LOG_DIR_NAME)


class ConfigError(Exception):
    """Raised when a repo-local config is unusable; carries a safe reason."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def repo_config_path(repo_root) -> pathlib.Path:
    return pathlib.Path(repo_root) / RQA_CONFIG_DIR / CONFIG_FILENAME


def _git(repo_root: pathlib.Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=str(repo_root), timeout=15, stdin=subprocess.DEVNULL
    )
    return result.stdout.strip()


def is_git_repo(repo_root: pathlib.Path) -> bool:
    return bool(_git(repo_root, ["rev-parse", "--is-inside-work-tree"]))


def is_ignored(repo_root: pathlib.Path, rel_path: str) -> bool:
    if not is_git_repo(repo_root):
        return False
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", rel_path],
        capture_output=True, text=True, cwd=str(repo_root), timeout=15, stdin=subprocess.DEVNULL,
    )
    return result.returncode == 0


def is_tracked(repo_root: pathlib.Path, rel_path: str) -> bool:
    if not is_git_repo(repo_root):
        return False
    return bool(_git(repo_root, ["ls-files", "--error-unmatch", "--", rel_path]))


def ensure_ignored(repo_root: pathlib.Path, rel_path: str) -> bool:
    """Append `rel_path` to `.gitignore` if not already ignored. No-op if ignored."""
    if is_ignored(repo_root, rel_path):
        return False
    gitignore = repo_root / ".gitignore"
    entry = rel_path if rel_path.endswith("/") else rel_path
    with gitignore.open("a", encoding="utf-8") as handle:
        if gitignore.stat().st_size > 0:
            handle.write("\n")
        handle.write(f"# review-queue-automation (local, optional)\n{entry}\n")
    return True


def check_writable(path: pathlib.Path) -> bool:
    if path.exists():
        return os.access(path, os.W_OK)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return os.access(path, os.W_OK)
    except OSError:
        return False


def validate_config(config: dict[str, Any], repo_root: pathlib.Path) -> list[str]:
    """Deterministic list of issues; empty list == valid."""
    issues: list[str] = []
    missing = sorted(REQUIRED_KEYS - set(config))
    if missing:
        return [f"config missing keys: {', '.join(missing)}"]

    if not isinstance(config.get("version"), int) or config["version"] < 1:
        issues.append("version must be an integer >= 1")

    repo = config.get("repository") or {}
    for key in REPOSITORY_KEYS:
        if not repo.get(key):
            issues.append(f"repository.{key} is required")
    root = pathlib.Path(repo.get("root", ""))
    if not root.exists() or not root.is_dir():
        issues.append(f"repository.root does not exist or is not a directory: {root}")

    logging_ = config.get("logging", {})
    for key in LOGGING_KEYS:
        if not logging_.get(key):
            issues.append(f"logging.{key} is required")
    if logging_.get("format", "otel-jsonl") != "otel-jsonl":
        issues.append("logging.format must be 'otel-jsonl'")
    log_dir = pathlib.Path(logging_.get("directory", ""))
    if log_dir and not check_writable(log_dir):
        issues.append(f"logging.directory is not writable: {log_dir}")

    # ---- GitHub transport -------------------------------------------------
    github = config.get("github", {}) or {}
    if not isinstance(github, dict) or not github:
        issues.append("github must be a non-empty object")
    else:
        if not github.get("api_version"):
            issues.append("github.api_version is required")
        if not isinstance(github.get("timeout_seconds"), int) or github.get("timeout_seconds", 0) <= 0:
            issues.append("github.timeout_seconds must be a positive integer")
        if "read_only" in github and not isinstance(github.get("read_only"), bool):
            issues.append("github.read_only must be a boolean")

    # ---- Model pools ------------------------------------------------------
    # Each pool entry must declare a non-empty efforts list (the reviewer
    # capability/effort gate reads `efforts`). Empty pools are structurally
    # valid but leave the config non-runtime-ready (checked in onboarding).
    models = config.get("models", {}) or {}
    for pool in ("primary", "secondary"):
        entries = models.get(pool)
        if entries is not None and not isinstance(entries, list):
            issues.append(f"models.{pool} must be a list")
            continue
        for i, entry in enumerate(entries or []):
            if not isinstance(entry, dict):
                issues.append(f"models.{pool}[{i}] must be an object")
                continue
            for field in ("runner", "selector", "provider_family", "capability"):
                if not (entry.get(field) or "").strip():
                    issues.append(f"models.{pool}[{i}].{field} is required")
            efforts = entry.get("efforts")
            if not isinstance(efforts, list) or not efforts:
                issues.append(f"models.{pool}[{i}].efforts must be a non-empty list")

    # ---- Assurance --------------------------------------------------------
    assurance = config.get("assurance", {}) or {}
    for key in ("sensitive_paths", "large_diff_lines", "full_rereview_ratio"):
        if key not in assurance:
            issues.append(f"assurance.{key} is required")
    if not isinstance(assurance.get("sensitive_paths", []), list):
        issues.append("assurance.sensitive_paths must be a list")
    if not isinstance(assurance.get("large_diff_lines", 0), int) or assurance.get("large_diff_lines", 0) <= 0:
        issues.append("assurance.large_diff_lines must be a positive integer")
    ratio = assurance.get("full_rereview_ratio")
    if not (isinstance(ratio, (int, float)) and 0 <= ratio <= 1):
        issues.append("assurance.full_rereview_ratio must be a number in [0,1]")

    # ---- Managed worker ownership ----------------------------------------
    # One State directory has one exclusive runtime lock. Parallel workers need
    # separate state directories and explicit operator isolation; accepting a
    # larger per-state setting would advertise concurrency the dispatcher refuses.
    dispatch = config.get("dispatch", {}) or {}
    for key in ("incoming_concurrency", "author_concurrency_per_repo"):
        value = dispatch.get(key, 1)
        if not isinstance(value, int) or isinstance(value, bool) or value != 1:
            issues.append(f"dispatch.{key} must be 1: a state directory has one worker")

    # ---- Logging / retention ---------------------------------------------
    if not isinstance(logging_.get("max_stderr_bytes", 0), int) or logging_.get("max_stderr_bytes", 0) <= 0:
        issues.append("logging.max_stderr_bytes must be a positive integer")

    # Recursively reject secret-like keys anywhere in the config.
    secret_hits = find_secret_keys(config)
    if secret_hits:
        issues.append("config contains forbidden secret-like keys: " + ", ".join(sorted(secret_hits)[:10]))

    # Per-activity authority must be structurally valid (fail-closed).
    if "authority" in config:
        from authority import validate_authority

        issues.extend(validate_authority(config.get("authority")))

    # A `policy` inline section, when present, must validate; malformed policy never
    # widens authority. This is the same validator the runtime snapshot uses.
    if "policy" in config:
        from policy import validate_policy

        issues_p = validate_policy(dict(config["policy"]))
        issues.extend("policy." + i for i in issues_p)

    # ---- Cost / rate-limit controls (optional; fail-closed when malformed)
    # Absent means the built-in defaults apply, which are finite. A PRESENT but
    # malformed section is an error rather than a silent fallback, so a typo can
    # never quietly remove a spend ceiling.
    from budget import validate_budget

    issues.extend(validate_budget(config))

    # ---- Retention (optional) --------------------------------------------
    if "retention" in config:
        retention = config.get("retention")
        if not isinstance(retention, dict):
            issues.append("retention must be an object")
        else:
            days = retention.get("artifact_days", 0)
            if isinstance(days, bool) or not isinstance(days, int) or days < 0:
                issues.append("retention.artifact_days must be a non-negative integer")

    # ---- Approval: modes / thresholds / canary / rates -------------------
    # Defaults disabled, so live is never enabled by omission.
    approval = config.get("approval", {}) or {}
    mode = approval.get("mode", "disabled")
    if mode not in {"disabled", "shadow", "human_escalation", "live"}:
        issues.append(f"approval.mode must be one of disabled|shadow|human_escalation|live, got {mode!r}")
    if mode == "live" and not approval.get("live_canary_approved", False):
        issues.append("approval.mode is live but approval.live_canary_approved is false")
    for intkey in ("effective_risk_max", "complexity_max", "file_limit", "line_limit"):
        value = approval.get(intkey, 0)
        if not isinstance(value, int) or value < 0:
            issues.append(f"approval.{intkey} must be a non-negative integer")
    rate = approval.get("approval_rate_max")
    if not (isinstance(rate, (int, float)) and 0 <= rate <= 1):
        issues.append("approval.approval_rate_max must be a number in [0,1]")

    # ---- Risk bands (fail-closed: malformed bands are issues, not crashes)
    risk_cfg = config.get("risk", {}) or {}
    if not isinstance(risk_cfg, dict):
        issues.append("risk must be an object")
    else:
        bands = risk_cfg.get("bands")
        if not isinstance(bands, dict) or not {"low", "medium", "high"} <= set(bands):
            issues.append("risk.bands must be present with low, medium and high")
        else:
            for key in ("low", "medium", "high"):
                if not isinstance(bands.get(key), int) or isinstance(bands.get(key), bool):
                    issues.append(f"risk.bands.{key} must be an integer")
            if not any("risk.bands" in i for i in issues):
                from risk import validate_bands, ConfigBandError

                try:
                    validate_bands(bands)
                except (ConfigBandError, ValueError, TypeError) as exc:
                    issues.append(f"risk.bands invalid: {exc}")

        # Protected triggers: each pattern must be valid regex AND, when
        # approval is live, non-empty. Invalid patterns fail closed at config
        # load so a typo can never silently widen the approval surface.
        triggers = risk_cfg.get("protected_triggers")
        if triggers is not None and not isinstance(triggers, list):
            issues.append("risk.protected_triggers must be a list")
        elif triggers:
            import re as _re

            for i, pattern in enumerate(triggers):
                if not isinstance(pattern, str):
                    issues.append(f"risk.protected_triggers[{i}] must be a string")
                    continue
                try:
                    _re.compile(pattern)
                except _re.error as exc:
                    issues.append(f"risk.protected_triggers[{i}] is not a valid regex: {exc}")
        if mode == "live" and not triggers:
            issues.append("approval.mode live requires non-empty risk.protected_triggers")

    # ---- Human expiry -----------------------------------------------------
    human = config.get("human_queue", {}) or {}
    if not isinstance(human, dict) or not human:
        issues.append("human_queue must be a non-empty object")
    elif not isinstance(human.get("expiry_minutes", 0), int) or human.get("expiry_minutes", 0) <= 0:
        issues.append("human_queue.expiry_minutes must be a positive integer")

    # ---- Shadow / history -------------------------------------------------
    shadow = config.get("shadow", {}) or {}
    if not isinstance(shadow, dict) or not shadow:
        issues.append("shadow must be a non-empty object")
    else:
        if not isinstance(shadow.get("history_window_months", 0), int) or shadow.get("history_window_months", 0) <= 0:
            issues.append("shadow.history_window_months must be a positive integer")
        if "evaluated_sha_only" in shadow and not isinstance(shadow.get("evaluated_sha_only"), bool):
            issues.append("shadow.evaluated_sha_only must be a boolean")

    # ---- Notifications (optional; fail-closed when malformed) -------------
    # Absent section == no delivery, which is safe: the human queue is still the
    # durable record. A PRESENT but malformed section is an error, so a typo can
    # never silently disable the operator's only notification path.
    if "notifications" in config:
        notifications = config.get("notifications")
        if not isinstance(notifications, dict):
            issues.append("notifications must be an object")
        else:
            transport = (notifications.get("transport") or "none").strip().lower()
            if transport not in ("none", "file", "command"):
                issues.append(
                    "notifications.transport must be one of none|file|command, "
                    f"got {transport!r}"
                )
            if transport == "file" and not (notifications.get("path") or "").strip():
                issues.append("notifications.path is required when transport is file")
            if transport == "command":
                command = notifications.get("command")
                if isinstance(command, list):
                    if not command or not all(isinstance(c, str) and c for c in command):
                        issues.append("notifications.command list must be non-empty strings")
                elif not (command or "").strip():
                    issues.append("notifications.command is required when transport is command")
            timeout = notifications.get("timeout_seconds", 30)
            if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
                issues.append("notifications.timeout_seconds must be a positive integer")

    return issues


SECRET_KEY_HINTS = ("token", "api_key", "apikey", "password", "secret", "private_key", "client_secret")

#: Exact config paths whose NAME trips `SECRET_KEY_HINTS` but whose VALUE is a
#: count, never a credential. The hint list matches "token" as a substring, so
#: token-BUDGET keys were rejected as secrets and a config carrying a budget
#: section could not load at all. The allowlist is exact-path and closed; a key
#: is only added here when its value is provably a number.
SECRET_KEY_ALLOWLIST = frozenset({
    "budget.per_pr_tokens",
    "budget.per_repo_daily_tokens",
    "budget.per_model_daily_tokens",
})


def _budget_defaults() -> dict[str, Any]:
    """The budget ceilings, taken from `budget.DEFAULTS` so the two cannot drift."""
    from budget import DEFAULTS

    resolved = {k: v for k, v in DEFAULTS.items() if k != "circuit_breaker"}
    resolved["circuit_breaker"] = dict(DEFAULTS["circuit_breaker"])
    return resolved


def policy_defaults(config: dict[str, Any]) -> dict[str, Any]:
    """Derive the inline `policy` section from a config, mirroring it verbatim.

    The policy is the immutable decision surface a job is pinned to. It is
    DERIVED, never invented: every value here is copied from the config it is
    built from, so seeding a policy cannot widen authority or move a threshold.

    It exists because `snapshot.build_snapshot` is fail-closed on a missing
    policy: without this section every job runs UNPINNED and `policy_version`
    stays blank in the ledger, which silently disables the pinning guarantee.
    """
    approval = dict(config.get("approval") or {})
    risk = dict(config.get("risk") or {})
    # Every key `policy.validate_policy` requires is present, falling back to the
    # SAME defaults `onboarding_defaults` uses. A derived policy that fails
    # validation would leave the job unpinned and `policy_version` blank, which is
    # the exact silent failure this section exists to prevent, so the fallbacks
    # are structural, not new thresholds.
    required_approval = {
        "mode": "disabled",
        "live_canary_approved": False,
        "effective_risk_max": 24,
        "complexity_max": 2,
        "file_limit": 50,
        "line_limit": 1000,
        "approval_rate_max": 0.5,
    }
    return {
        "version": "v1",
        "authority": dict(config.get("authority") or {}),
        "approval": {
            key: approval.get(key, fallback)
            for key, fallback in required_approval.items()
        },
        "risk": {
            "bands": dict(risk.get("bands") or {}),
            "protected_triggers": list(risk.get("protected_triggers") or []),
        },
        "human_queue": dict(config.get("human_queue") or {}),
        "assurance": dict(config.get("assurance") or {}),
    }


def find_secret_keys(config: dict[str, Any], prefix: str = "") -> list[str]:
    """Recursively find keys that look secret-like (e.g. api_key, secret, token)."""
    hits: list[str] = []
    for key, value in (config or {}).items():
        k = str(key).lower()
        path = f"{prefix}.{key}" if prefix else str(key)
        if any(h in k for h in SECRET_KEY_HINTS) and path not in SECRET_KEY_ALLOWLIST:
            hits.append(path)
        if isinstance(value, dict):
            hits.extend(find_secret_keys(value, path))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    hits.extend(find_secret_keys(item, f"{path}[{i}]"))
    return hits


def _repo_relative_log(config: dict[str, Any]) -> str | None:
    log_dir = config.get("logging", {}).get("directory", "")
    if not log_dir:
        return None
    root = pathlib.Path(config.get("repository", {}).get("root", ""))
    if not root:
        return None
    try:
        rel = pathlib.Path(log_dir).resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return rel.as_posix() + "/"


def load_repo_config(repo_root) -> tuple[dict[str, Any] | None, pathlib.Path, list[str]]:
    """Load and validate the repo-local config.

    Returns `(config | None, config_path, issues)`. Non-empty issues means dispatch
    must refuse and direct the operator to onboarding.
    """
    root = pathlib.Path(repo_root)
    cfg_path = repo_config_path(root)
    if not cfg_path.is_file():
        return None, cfg_path, [f"config not found: {cfg_path} (run onboarding)"]
    try:
        config = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, cfg_path, [f"config is not valid JSON: {exc.msg} at line {exc.lineno}"]
    except OSError as exc:
        return None, cfg_path, [f"config unreadable: {exc}"]

    issues = validate_config(config, root)
    if is_tracked(root, RQA_CONFIG_DIR) or is_tracked(root, f"{RQA_CONFIG_DIR}/{CONFIG_FILENAME}"):
        issues.append("config is tracked; it must be git-ignored and untracked (run onboarding)")
    if not is_ignored(root, RQA_CONFIG_DIR + "/"):
        issues.append(f"{RQA_CONFIG_DIR}/ is not git-ignored")
    log_rel = _repo_relative_log(config)
    if log_rel:
        if is_tracked(root, log_rel):
            issues.append(f"logging.directory is tracked: {log_rel}")
        if not is_ignored(root, log_rel):
            issues.append(f"logging.directory is not git-ignored: {log_rel}")
    return (config if not issues else None), cfg_path, issues


def onboarding_defaults(repo_root) -> dict[str, Any]:
    """A valid starter config for onboarding. Never written until validated."""
    root = pathlib.Path(repo_root).resolve()
    log_dir = root / DEFAULT_LOG_DIR_NAME
    defaults: dict[str, Any] = {
        "version": 1,
        "login": "",
        "state_dir": "~/.config/review-queue-automation",
        "repository": {"slug": "", "root": str(root), "base": "launchpad", "preflight": ""},
        "logging": {"directory": str(log_dir), "format": "otel-jsonl", "max_stderr_bytes": 8192},
        "poll": {"active_seconds": 300, "idle_seconds": [600, 1200, 1800], "rest_remaining_floor": 200},
        "models": {"cooldown_seconds": 1800, "timeout_seconds": 1800, "primary": [], "secondary": []},
        "assurance": {
            "sensitive_paths": [
                "(^|/)(security|migrations?|provisioning)(/|$)",
                "^\\.github/workflows/",
                "(^|/)deploy/",
            ],
            "large_diff_lines": 700,
            "full_rereview_ratio": 0.5,
        },
        "dispatch": {
            "incoming_concurrency": 1,
            "author_concurrency_per_repo": 1,
            "incoming_canary_approved": False,
            "author_canary_approved": False,
        },
        "authority": {act: "disabled" for act in ("review", "comment", "approve", "request_changes", "triage", "fix")},
        "approval": {
            "mode": "disabled",
            "live_canary_approved": False,
            "effective_risk_max": 24,
            "complexity_max": 2,
            "file_limit": 50,
            "line_limit": 1000,
            "approval_rate_max": 0.5,
        },
        "risk": {
            "bands": {"low": 24, "medium": 99, "high": 100},
            "protected_triggers": [
                "(^|/)(security|auth|authentication|authorization|credentials?)(/|$)",
                "(^|/)migrations?/",
                r"\.(sql|prisma|graphql)$",
                "(^|/)deploy/",
                r"(^|/)\.github/workflows/",
                "schema/",
                "policy",
            ],
        },
        "human_queue": {"expiry_minutes": 1440},
        "shadow": {"history_window_months": 12, "evaluated_sha_only": True},
        "github": {"api_version": "2022-11-28", "timeout_seconds": 30, "read_only": True},
        # Written out explicitly rather than left implicit: an operator can see
        # and change the ceilings, and `budget.limits` would apply these same
        # values anyway if the section were absent.
        "budget": _budget_defaults(),
        "retention": {"artifact_days": 30},
    }
    defaults["policy"] = policy_defaults(defaults)
    return defaults