#!/usr/bin/env python3
"""Deterministic assurance ladder and escalation driver.

Turns reviewer signals into a minimum-cost escalation path. Pure logic, no GitHub
and no model calls, so it is unit-testable in isolation.

Axes and order (a value later in the list is "above" an earlier one):

  capability:    economy < workhorse < frontier
  effort:        low < medium < high < xhigh
  independence:  single < challenger < panel < human

Ladder invariant: the router may raise an axis, never lower below a recorded
deterministic minimum, and never drive past the cap on each axis. Past the cap,
or on material disagreement the panel cannot settle, control moves to a human.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

CAPABILITY = ("economy", "workhorse", "frontier")
EFFORT = ("low", "medium", "high", "xhigh")
INDEPENDENCE = ("single", "challenger", "panel", "human")

SIGNALS = {
    "SUPPORTED",
    "DEFECTS_FOUND",
    "MISSING_EVIDENCE",
    "INSUFFICIENT_CAPABILITY",
    "MATERIAL_DISAGREEMENT",
    "HUMAN_RESERVED",
}

DECISIONS = {
    "SUCCESS",
    "REQUEST_CHANGES",
    "GATHER_EVIDENCE",
    "RAISE_EFFORT",
    "RAISE_CAPABILITY",
    "CONVENE_PANEL",
    "HUMAN",
}


@dataclass(frozen=True)
class Profile:
    capability: str = "workhorse"
    effort: str = "medium"
    independence: str = "challenger"

    def __post_init__(self) -> None:
        if self.capability not in CAPABILITY:
            raise ValueError(f"invalid capability {self.capability!r}")
        if self.effort not in EFFORT:
            raise ValueError(f"invalid effort {self.effort!r}")
        if self.independence not in INDEPENDENCE:
            raise ValueError(f"invalid independence {self.independence!r}")

    def as_dict(self) -> dict[str, str]:
        return {"capability": self.capability, "effort": self.effort, "independence": self.independence}


def ordered(axis: tuple[str, ...], value: str) -> int:
    return axis.index(value)


def raised(profile: Profile, axis: str) -> Profile | None:
    """Return the profile one step up on `axis`, or None if it is at the cap."""
    if axis == "capability":
        idx = ordered(CAPABILITY, profile.capability)
        if idx + 1 >= len(CAPABILITY):
            return None
        return Profile(CAPABILITY[idx + 1], profile.effort, profile.independence)
    if axis == "effort":
        idx = ordered(EFFORT, profile.effort)
        if idx + 1 >= len(EFFORT):
            return None
        return Profile(profile.capability, EFFORT[idx + 1], profile.independence)
    if axis == "independence":
        idx = ordered(INDEPENDENCE, profile.independence)
        if idx + 1 >= len(INDEPENDENCE):
            return None
        return Profile(profile.capability, profile.effort, INDEPENDENCE[idx + 1])
    raise ValueError(f"unknown axis {axis!r}")


def convene_panel(profile: Profile) -> Profile:
    """Force the strongest machine configuration for a panel: frontier + xhigh."""
    return Profile("frontier", "xhigh", "panel")


def classify(profile: Profile, signals: list[str]) -> str:
    """Decide the next action for one assessment attempt."""
    if not signals:
        return "GATHER_EVIDENCE"

    if any(s == "HUMAN_RESERVED" for s in signals):
        return "HUMAN"

    # One reviewer says the change is clean while another located defects. That is
    # a disagreement about the core question, so it escalates rather than acting:
    # neither "approve" nor "request changes" is supported by the panel.
    if "DEFECTS_FOUND" in signals and "SUPPORTED" in signals:
        if profile.independence in ("single", "challenger"):
            return "CONVENE_PANEL"
        return "HUMAN"

    if "MATERIAL_DISAGREEMENT" in signals:
        if profile.independence in ("single", "challenger"):
            return "CONVENE_PANEL"
        return "HUMAN"

    if "INSUFFICIENT_CAPABILITY" in signals:
        if profile.effort != EFFORT[-1]:
            return "RAISE_EFFORT"
        if profile.capability != CAPABILITY[-1]:
            return "RAISE_CAPABILITY"
        return "HUMAN"

    if "MISSING_EVIDENCE" in signals:
        return "GATHER_EVIDENCE"

    if all(s == "SUPPORTED" for s in signals):
        return "SUCCESS"

    # Every reviewer that completed agrees defects are present. Whether that may
    # become a formal change request is decided downstream by the corroboration
    # rule and the request-changes authority gate, never here.
    if all(s == "DEFECTS_FOUND" for s in signals):
        return "REQUEST_CHANGES"

    return "HUMAN"


@dataclass(frozen=True)
class Step:
    profile: Profile
    decision: str
    order: int


def drive(
    minimum: Profile,
    assess: Callable[[Profile], list[str]],
    gather: Callable[[Profile], Profile] | None = None,
    max_steps: int = 6,
) -> tuple[Profile, str, list[Step]]:
    """Run the escalation loop.

    `assess(profile) -> list[str]` returns the reviewer signals for a profile.
    `gather(profile) -> Profile` is an optional callback that returns the profile
    to run after gathering missing evidence; None means re-run the same profile.
    """
    profile = minimum
    steps: list[Step] = []
    for step_index in range(max_steps):
        signals = list(assess(profile))
        decision = classify(profile, signals)
        steps.append(Step(profile=profile, decision=decision, order=step_index))
        if decision == "SUCCESS":
            return profile, "SUCCESS", steps
        # A corroborated defect finding is a terminal assessment outcome: raising
        # effort or capability cannot make a located defect go away.
        if decision == "REQUEST_CHANGES":
            return profile, "REQUEST_CHANGES", steps
        if decision == "HUMAN":
            return profile, "HUMAN", steps
        if decision == "GATHER_EVIDENCE":
            if gather is not None:
                profile = gather(profile)
            continue
        if decision == "RAISE_EFFORT":
            profile = raised(profile, "effort") or profile
            continue
        if decision == "RAISE_CAPABILITY":
            profile = raised(profile, "capability") or profile
            continue
        if decision == "CONVENE_PANEL":
            profile = convene_panel(profile)
            continue
        return profile, "HUMAN", steps
    return profile, "HUMAN", steps


def minimum_profile(lane: str, sensitive: bool = False, large: bool = False) -> Profile:
    """Deterministic minimum profile for a PR and lane."""
    if lane == "author_triage":
        capability = "frontier" if (sensitive or large) else "workhorse"
        return Profile(capability=capability, effort="high", independence="challenger")
    if sensitive or large:
        return Profile(capability="frontier", effort="high", independence="challenger")
    return Profile(capability="workhorse", effort="medium", independence="challenger")