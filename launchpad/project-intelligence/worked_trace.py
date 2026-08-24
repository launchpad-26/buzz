"""The UserRepository-shaped investigation trace -- issue #211, STEP 10.

The design doc's § Decision logic worked example, reproduced against real code
in this repo rather than its fictional TypeScript subject:

  search_symbols -> read_file -> find_references -> tests -> git history
    -> an answer separating FACT from INFERENCE

Subject: `event_kind_i32` in crates/buzz-core/src/kind.rs. Chosen because it
makes every stage fire honestly rather than because it flatters the output --
it is a public function with no in-crate callers, so the tests stage runs (the
stop rule skips it when callers already corroborate), and the question is
historical, so the history stage runs. Picking a well-connected symbol would
have produced a shorter trace and a demo that quietly skipped two stages.

The citation audit below is the point of this module as much as the trace is. It
re-opens every file:line an answer cites and checks the line supports the claim.
That check is why STEP 3's two defects were caught, and running it here makes it
repeatable rather than a thing someone did once by hand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import investigator
from answer import Answer, Claim, render
from knowledge_agent import KnowledgeAgent

WORKED_CRATE = "buzz-core"
WORKED_SYMBOL = "event_kind_i32"
WORKED_QUESTION = f"why does `{WORKED_SYMBOL}` exist?"

# "path:12" or "path:12-34". Deliberately strict: a citation this cannot parse
# is REPORTED as unparsed, never counted as checked. A checker that silently
# skips what it does not understand reports a clean audit over nothing.
_CITATION = re.compile(r"^(?P<path>[\w./-]+\.\w+):(?P<start>\d+)(?:-(?P<end>\d+))?$")


@dataclass(frozen=True)
class CitationCheck:
    citation: str
    claim: str
    supported: bool
    note: str


def _words(statement: str) -> list[str]:
    """Identifier-ish tokens worth looking for in the cited range. Prose words
    are skipped: "is a decision point rather than a transformation" will never
    appear in source, and demanding it would fail every honest inference."""
    return [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_:]{3,}", statement) if "_" in w or "::" in w]


def audit_citations(answer: Answer) -> tuple[list[CitationCheck], list[str]]:
    """Re-open every parseable file:line citation and check it supports its claim.

    Returns (checks, unparsed). A claim may legitimately cite something that is
    not a file range -- a graph edge, a commit hash -- and those go in
    `unparsed` so the count of what was actually verified stays honest.
    """
    checks: list[CitationCheck] = []
    unparsed: list[str] = []

    for claim in answer.claims:
        for citation in claim.evidence:
            match = _CITATION.match(citation)
            if match is None:
                unparsed.append(citation)
                continue
            path = match.group("path")
            start = int(match.group("start"))
            end = int(match.group("end") or start)
            try:
                text = investigator.read_file(path, start, end)
            except (OSError, ValueError) as exc:
                checks.append(CitationCheck(citation, claim.statement, False, f"unreadable: {exc}"))
                continue
            wanted = _words(claim.statement)
            hits = [w for w in wanted if w in text]
            checks.append(
                CitationCheck(
                    citation,
                    claim.statement,
                    supported=bool(hits) or not wanted,
                    note=(
                        f"found {', '.join(hits)}"
                        if hits
                        else ("no identifier to check" if not wanted else f"none of {wanted} present")
                    ),
                )
            )
    return checks, unparsed


def _split_by_class(answer: Answer) -> tuple[tuple[Claim, ...], tuple[Claim, ...], tuple[Claim, ...]]:
    return (
        answer.claims_of_class("FACT"),
        answer.claims_of_class("INFERENCE"),
        answer.claims_of_class("TEAM_KNOWLEDGE"),
    )


def main(agent: KnowledgeAgent | None = None) -> None:
    """Takes an already-built agent when one exists: indexing the crate is the
    expensive part, and knowledge.py's CLI runs both worked examples."""
    agent = agent if agent is not None else KnowledgeAgent.build(WORKED_CRATE)
    outcome = agent.run(WORKED_QUESTION)

    print(f"Question: {WORKED_QUESTION}\n")
    print("=== stage 1 -- check confidence first ===")
    for hit in outcome.assessment.hits:  # type: ignore[union-attr]
        print(f"  {hit.component}: {'found' if hit.found else 'empty'} -- {hit.detail}")
    print(f"  confident: {outcome.assessment.confident}\n")  # type: ignore[union-attr]

    print("=== stage 3 -- investigation, in the design doc's order ===")
    print(outcome.trace.render())
    print(f"  stages recorded: {' -> '.join(outcome.trace.tools)}")
    print(f"  side-effecting calls: {len(outcome.trace.side_effecting)}\n")

    print("=== stage 4 -- the labeled answer ===")
    print(render(outcome.answer))

    facts, inferences, team = _split_by_class(outcome.answer)
    print(f"\n  FACT: {len(facts)}  INFERENCE: {len(inferences)}  TEAM KNOWLEDGE: {len(team)}")

    print("\n=== citation audit -- every file:line re-opened ===")
    checks, unparsed = audit_citations(outcome.answer)
    for check in checks:
        print(f"  {'OK  ' if check.supported else 'FAIL'} {check.citation} -- {check.note}")
    for citation in unparsed:
        print(f"  n/a  {citation} (not a file range -- not counted as verified)")
    print(f"  verified {sum(c.supported for c in checks)}/{len(checks)}, {len(unparsed)} not a file range")


if __name__ == "__main__":
    main()
