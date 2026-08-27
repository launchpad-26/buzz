"""Canonical reviewer-model aliases and qualified route identity.

A route is not a marketing model name. It is the exact transport/model/version and
all execution inputs that can change a review result.  The registry is pure data:
operators select from it in repo-local config; it never probes or invokes a model.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelAlias:
    name: str
    runner: str
    selector: str
    provider_family: str


# The selector is intentionally exact and versioned. Operators may use a different
# approved model, but then it is a different qualified route, not a silent alias.
ALIASES: dict[str, ModelAlias] = {
    "CLAUDE_FAST": ModelAlias("CLAUDE_FAST", "claude", "claude-sonnet-4-5", "anthropic"),
    "CLAUDE_STRONG": ModelAlias("CLAUDE_STRONG", "claude", "claude-opus-4-5", "anthropic"),
    "CLAUDE_MAX": ModelAlias("CLAUDE_MAX", "claude", "claude-fable-1", "anthropic"),
    "CODEX_ECONOMY": ModelAlias("CODEX_ECONOMY", "codex", "gpt-5.6-luna", "openai"),
    "CODEX_BALANCED": ModelAlias("CODEX_BALANCED", "codex", "gpt-5.6-terra", "openai"),
    "CODEX_STRONG": ModelAlias("CODEX_STRONG", "codex", "gpt-5.6-sol", "openai"),
}


def normalize_alias(value: str) -> str:
    """Normalize human spellings without allowing a fuzzy model selection."""
    key = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()
    # Historical shorthand appears in operator notes; normalize it before lookup.
    return {"COD_EXE_STRONG": "CODEX_STRONG", "COD_EXE_BALANCED": "CODEX_BALANCED",
            "COD_EXE_ECONOMY": "CODEX_ECONOMY"}.get(key, key)


def resolve(value: str) -> ModelAlias:
    """Resolve one supported alias or reject it; there is no implicit latest route."""
    key = normalize_alias(value)
    try:
        return ALIASES[key]
    except KeyError as exc:
        raise ValueError(f"unknown model alias {value!r}; supported: {', '.join(sorted(ALIASES))}") from exc


def qualified_route(
    entry: dict[str, Any],
    *,
    effort: str,
    policy_version: str,
    default_prompt_version: str = "v1",
) -> dict[str, Any]:
    """Build the complete immutable identity of an executable reviewer route."""
    alias = str(entry.get("alias") or entry.get("selector") or entry.get("model") or "").strip()
    selector = str(entry.get("selector") or entry.get("model") or "").strip()
    if not selector:
        raise ValueError("qualified route requires selector")
    route = {
        "alias": normalize_alias(alias),
        "runner": str(entry.get("runner") or "").strip(),
        "provider": str(entry.get("provider") or entry.get("provider_family") or "").strip(),
        "model": selector,
        "model_version": str(entry.get("model_version") or selector).strip(),
        "effort": effort,
        "execution_mode": str(entry.get("execution_mode") or "read_only").strip(),
        "tools": list(entry.get("tools") or []),
        "prompt_version": str(entry.get("prompt_version") or default_prompt_version).strip(),
        "policy_version": str(policy_version or "unversioned"),
    }
    if not route["runner"] or not route["provider"]:
        raise ValueError("qualified route requires runner and provider")
    encoded = json.dumps(route, sort_keys=True, separators=(",", ":")).encode("utf-8")
    route["fingerprint"] = hashlib.sha256(encoded).hexdigest()
    return route


def runtime_route_material(config: dict[str, Any]) -> dict[str, Any]:
    """Return only model/prompt/tool inputs whose change must return to shadow."""
    models = config.get("models") or {}
    policy = config.get("policy") or {}
    entries: list[dict[str, Any]] = []
    for pool in ("primary", "secondary"):
        for entry in models.get(pool) or []:
            if not isinstance(entry, dict):
                continue
            for effort in entry.get("efforts") or ["medium"]:
                entries.append(qualified_route(
                    entry, effort=str(effort), policy_version=str(policy.get("version") or "unversioned"),
                    default_prompt_version=str(models.get("prompt_version") or "v1"),
                ))
    return {"routes": sorted(entries, key=lambda item: item["fingerprint"])}


def route_material_fingerprint(config: dict[str, Any]) -> str:
    material = runtime_route_material(config)
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def observe_runtime_routes(state, config: dict[str, Any], *, scope: str) -> dict[str, Any]:
    """Persist model/prompt/tool identity and lock changed routes to shadow.

    The first observed runtime establishes a baseline while approval is already
    fail-closed by default. A later changed fingerprint is never silently trusted:
    it remains `shadow_locked` until qualification explicitly replaces it.
    """
    from common import utcnow

    fingerprint = route_material_fingerprint(config)
    row = state.db.execute(
        "SELECT fingerprint, status FROM route_qualifications WHERE scope=?", (scope,)
    ).fetchone()
    if row is None:
        state.db.execute(
            "INSERT INTO route_qualifications(scope,fingerprint,status,updated_at) VALUES(?,?,?,?)",
            (scope, fingerprint, "observed", utcnow()),
        )
        state.db.commit()
        return {"fingerprint": fingerprint, "status": "observed", "shadow_locked": False}
    if row["fingerprint"] == fingerprint:
        return {
            "fingerprint": fingerprint,
            "status": row["status"],
            "shadow_locked": row["status"] == "shadow_locked",
        }
    state.db.execute(
        "UPDATE route_qualifications SET fingerprint=?,status='shadow_locked',updated_at=? WHERE scope=?",
        (fingerprint, utcnow(), scope),
    )
    state.db.commit()
    return {"fingerprint": fingerprint, "status": "shadow_locked", "shadow_locked": True}
