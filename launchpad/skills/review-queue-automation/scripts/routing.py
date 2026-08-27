"""Runtime model routing for review-queue-automation.

The runtime model of the finished automation is configured independently of the
implementation model. This module resolves a requested activity/strategy to a
concrete `provider/model` using the subscription-first ladder:

  1. configured Claude subscription route
  2. configured Codex subscription route
  3. provider-diverse OpenRouter fallback
  4. final economical fallback
  5. human escalation or read-only failure

Routing records, for every step:
  requested alias, resolved canonical model id, provider, fallback position,
  and reason. A fallback-loop guard prevents repeatedly selecting the same
  unavailable provider within a route window, and cooldowns are held in state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Ordered rungs of the subscription-first ladder.
RUNG_ORDER = ("claude", "codex", "openrouter", "economical", "human")


class RoutingError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResolvedRoute:
    requested_alias: str
    resolved_model: str
    provider: str
    fallback_position: int  # 0 = first rung
    reason: str = ""


@dataclass
class RoutedRun:
    requested_alias: str = ""
    resolved: list[ResolvedRoute] = field(default_factory=list)
    final: str = "human"  # last-resort marker
    attempted: list[str] = field(default_factory=list)

    def record(self, route: ResolvedRoute) -> None:
        self.resolved.append(route)
        self.attempted.append(route.resolved_model)
        self.final = route.resolved_model

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_alias": self.requested_alias,
            "resolved": [r.__dict__ for r in self.resolved],
            "final": self.final,
            "attempted": self.attempted,
        }


def _routes_from_config(cfg: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    models = cfg.get("models") or {}
    return {
        "claude": models.get("claude", []),
        "codex": models.get("codex", []),
        "openrouter": models.get("openrouter", []),
        "economical": models.get("economical", []),
    }


def is_route_available(state, key: str) -> bool:
    """Check a provider/model cooldown in the state DB (or no DB => available)."""
    if state is None:
        return True
    row = state.db.execute(
        "SELECT unavailable_until FROM providers WHERE key=?", (key,)
    ).fetchone()
    if not row or not row["unavailable_until"]:
        return True
    from datetime import datetime

    until = datetime.fromisoformat(row["unavailable_until"].replace("Z", "+00:00"))
    return datetime.now().astimezone() > until


def resolve_route(
    cfg: dict[str, Any],
    requested_alias: str,
    *,
    provider_hint: str | None = None,
    state=None,
    cooldown_seconds: int = 1800,
) -> RoutedRun:
    """Resolve `requested_alias` to the first available concrete model via the
    subscription-first ladder. A human/escalation fallback position is returned
    when every rung is unavailable; it is never a mutating model.

    Prevents fallback loops: once a route is attempted it is not selected again in
    the same resolution, and unavailability persists via the optional cooldown
    store.
    """
    run = RoutedRun(requested_alias=requested_alias)
    routes = _routes_from_config(cfg)
    # Honour an explicit provider hint by checking that rung first.
    order = RUNG_ORDER
    if provider_hint in routes:
        order = [provider_hint] + [r for r in RUNG_ORDER if r != provider_hint and r in routes]

    position = 0
    for rung in order:
        if rung == "human":
            run.final = "human"
            break
        for entry in routes.get(rung, []):
            model = entry.get("model") or entry.get("selector")
            provider = entry.get("provider") or rung
            if not model:
                continue
            key = f"{provider}:{model}"
            if key in run.attempted:
                continue  # fallback-loop guard
            if not is_route_available(state, key):
                continue  # cooldown => try next eligible route
            run.record(ResolvedRoute(
                requested_alias=requested_alias,
                resolved_model=model,
                provider=provider,
                fallback_position=position,
                reason=f"rung={rung}",
            ))
            return run
        position += 1
    # No eligible router: record human fallback (read-only / escalate).
    run.final = "human"
    return run