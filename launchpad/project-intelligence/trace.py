"""The investigation trace -- issue #211, STEP 6.

Every Investigator call the agent makes, in the order it made them, with the
side-effect class it carried. Shared by decision-logic stage 2 (verification,
STEP 6) and stage 3 (investigation, STEP 7).

Why a record at all: the design doc's constraint is that "every claim in an
answer must resolve to a component that can be inspected independently of the
model's output". A trace is how that is inspected. Without one, "I verified
this" is exactly the unfalsifiable assertion the whole layer exists to replace.

The side-effect class is read from investigator.TOOL_REGISTRY rather than passed
in by the caller. A caller who could label its own call READ_ONLY could run a
test suite and record it as a read.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from investigator import TOOL_REGISTRY, SideEffect


@dataclass(frozen=True)
class ToolCall:
    tool: str
    args: str
    side_effect: SideEffect
    found: bool
    detail: str


@dataclass
class Trace:
    """Append-only, ordered. Mutable by design -- it accumulates across a
    single question's investigation, unlike every other type here."""

    calls: list[ToolCall] = field(default_factory=list)

    def record(self, tool: str, args: str, found: bool, detail: str) -> ToolCall:
        if tool not in TOOL_REGISTRY:
            raise ValueError(f"{tool!r} is not a tool in investigator.TOOL_REGISTRY")
        call = ToolCall(
            tool=tool,
            args=args,
            side_effect=TOOL_REGISTRY[tool][1],
            found=found,
            detail=detail,
        )
        self.calls.append(call)
        return call

    @property
    def tools(self) -> tuple[str, ...]:
        """Tool names in call order, with repeats -- the order is the evidence
        that the design doc's progression was followed, so collapsing repeats
        would hide a loop that never advanced."""
        return tuple(c.tool for c in self.calls)

    @property
    def side_effecting(self) -> tuple[ToolCall, ...]:
        return tuple(c for c in self.calls if c.side_effect == "EXECUTE")

    def render(self) -> str:
        if not self.calls:
            return "(no investigation performed)"
        return "\n".join(
            f"  {i}. {c.tool}({c.args}) [{c.side_effect}] -> {'found' if c.found else 'nothing'}: {c.detail}"
            for i, c in enumerate(self.calls, start=1)
        )
