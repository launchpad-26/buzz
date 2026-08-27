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
    qualified: dict[str, Any] = field(default_factory=dict)

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


#: How a canonical pool entry's runner maps onto a ladder rung.
_RUNNER_RUNG = {"claude": "claude", "codex": "codex", "omp": "openrouter"}


def _routes_from_config(cfg: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group the configured reviewer candidates into ladder rungs.

    There is ONE source of executable candidates: `models.primary` and
    `models.secondary`, the same pools `panel.py` runs. Rungs are derived from each
    entry's `runner` so routing can never disagree with what actually executes.

    Explicit per-rung lists (`models.claude`, `models.codex`, ...) are still
    honoured when present, so an operator can pin an exact ladder.
    """
    models = cfg.get("models") or {}
    explicit = {rung: list(models.get(rung) or []) for rung in
                ("claude", "codex", "openrouter", "economical")}
    if any(explicit.values()):
        return explicit

    derived: dict[str, list[dict[str, Any]]] = {
        "claude": [], "codex": [], "openrouter": [], "economical": []
    }
    for pool in ("primary", "secondary"):
        for entry in models.get(pool) or []:
            if not isinstance(entry, dict):
                continue
            runner = (entry.get("runner") or "").strip()
            rung = _RUNNER_RUNG.get(runner)
            if rung is None:
                continue
            # An explicitly economical candidate is a last-resort rung, not a peer
            # of the provider-diverse fallbacks.
            if rung == "openrouter" and (entry.get("capability") or "") == "economy":
                rung = "economical"
            derived[rung].append(entry)
    return derived


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
    effort: str = "medium",
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
            # Canonical pools carry `provider_family`; explicit rungs carry `provider`.
            provider = entry.get("provider") or entry.get("provider_family") or rung
            if not model:
                continue
            key = f"{provider}:{model}"
            if key in run.attempted:
                continue  # fallback-loop guard
            if not is_route_available(state, key):
                continue  # cooldown => try next eligible route
            from model_registry import qualified_route

            # Explicit ladder entries predate the canonical pools and may omit
            # runner/provider fields. The rung that selected them supplies those
            # identities; qualification must not discard an otherwise executable
            # legacy route.
            qualified_entry = {
                **entry,
                "runner": entry.get("runner") or {"claude": "claude", "codex": "codex", "openrouter": "omp", "economical": "omp"}.get(rung, ""),
                "provider": entry.get("provider") or entry.get("provider_family") or provider,
                "selector": entry.get("selector") or model,
            }
            qualified = qualified_route(
                qualified_entry,
                effort=effort,
                policy_version=str((cfg.get("policy") or {}).get("version") or "unversioned"),
                default_prompt_version=str((cfg.get("models") or {}).get("prompt_version") or "v1"),
            )
            run.record(ResolvedRoute(
                requested_alias=requested_alias,
                resolved_model=model,
                provider=provider,
                fallback_position=position,
                reason=f"rung={rung}",
                qualified=qualified,
            ))
            return run
        position += 1
    # No eligible router: record human fallback (read-only / escalate).
    run.final = "human"
    return run