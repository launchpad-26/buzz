"""The knowledge.* programmatic interface -- issue #211, STEP 9.

The seven methods from the design doc's § Data Model item 8. Every one returns
an Answer, which is the point: "every return value carries the same provenance
labeling as a chat answer -- a calling agent must never have to guess whether a
field is a FACT or a guess dressed as one." One return type, one renderer, one
provenance vocabulary, whether a human or an agent asked.

  find(query)              -> concept -> subsystem -> candidate, via SemanticIndex
  explain(symbol, depth)   -> the full four-stage pipeline
  dependencies(symbol)     -> outward calls slice, direct and transitive
  impact(symbol)           -> inward dependents, direct and secondary SEPARATELY
  setup(task)              -> cited operational steps from real manifests
  conventions(area)        -> TEAM_KNOWLEDGE + INFERENCE from ProjectMemory
  history(symbol)          -> HISTORY-state narrative with commit evidence

No model is called by any of them.
"""

from __future__ import annotations

import investigator
from answer import Answer, Claim
from graph import reachable
from knowledge_agent import KnowledgeAgent
from question import Depth

# Where an operational answer for each task is looked for, in order. Cited by
# path, never generically: "run npm install" is wrong the moment the project
# uses pnpm or cargo, and citing the source is what prevents drifting into
# generic advice (§ Development-environment operational answers).
SETUP_SOURCES = ("Justfile", "CONTRIBUTING.md", "README.md", "Cargo.toml", ".env.example")

IMPACT_DIRECT_HOPS = 1
IMPACT_SECONDARY_HOPS = 2
DEPENDENCY_HOPS = 2


# A cosine score of zero means no token overlap at all: the concept and every
# indexed summary share not one word. #210's pipeline still returns its
# top-ranked candidate in that case -- verified, not assumed: the concept
# "zzzz nothing like this exists zzzz" returns is_shared_gated_kind at score
# 0.0, WITH real tested_by and called_by edges attached. Reporting that as a
# confirmed find would be true evidence about the wrong subject, so a score at
# the floor resolves to nothing rather than to whatever ranked first.
MINIMUM_CANDIDATE_SCORE = 1e-9


def find(agent: KnowledgeAgent, query: str) -> Answer:
    """The no-name case: the caller cannot name the symbol yet."""
    result = agent.find_concept(query)
    if result is not None and result.candidate_score <= MINIMUM_CANDIDATE_SCORE:
        result = None
    if result is None:
        return Answer(
            question=query,
            short_answer="No candidate resolved for that concept.",
            things_to_be_aware_of=(
                "A statement about this index, not about the codebase -- the concept may be "
                "phrased in words the indexed summaries do not use."
            ),
            claims=(
                Claim(
                    statement=f"the SemanticIndex returned no candidate for {query!r}",
                    entry_class="FACT",
                    evidence=(f"SemanticIndex.search({query!r}) over {agent.symbol_count} symbols",),
                ),
            ),
        )
    return Answer(
        question=query,
        short_answer=f"Most likely {result.qualified_name}.",
        how_it_works=f"Resolved via subsystem {result.subsystem.scope}.",
        important_files=(result.subsystem.scope,),
        claims=_find_claims(result),
    )


def _find_claims(result) -> tuple[Claim, ...]:
    """Three claims, deliberately split by what was actually established.

    The scores are measured, so they are a FACT. That the top-ranked candidate
    ANSWERS THE QUESTION is never a FACT -- a similarity rank is not a
    confirmation, and the whole § Concept Retrieval boundary exists because
    ranking first and being right are different properties. The graph edges are
    a FACT about the candidate symbol, phrased so it cannot be read as
    confirming the match: those edges would exist no matter what was asked.
    """
    claims: list[Claim] = [
        Claim(
            statement=(
                f"{result.qualified_name} ranks highest for this concept "
                f"(subsystem {result.subsystem_score:.4f}, candidate {result.candidate_score:.4f})"
            ),
            entry_class="FACT",
            evidence=(
                f"SemanticIndex two-stage ranking over subsystem {result.subsystem.scope}",
            ),
        ),
        Claim(
            statement=f"{result.qualified_name} is the implementation this concept refers to",
            entry_class="INFERENCE",
            evidence=(f"top-ranked at candidate score {result.candidate_score:.4f}",),
            # The score IS the confidence -- there is nothing more honest to
            # put here, and inventing a separate number would hide the one real
            # measurement behind a guess about it.
            confidence=min(max(result.candidate_score, 0.0), 1.0),
        ),
    ]

    confirmation = getattr(result, "confirmation", None)
    edges = list(getattr(confirmation, "callers", []) or []) + list(
        getattr(confirmation, "tests", []) or []
    )
    if edges:
        claims.append(
            Claim(
                statement=(
                    f"{result.qualified_name} has {len(edges)} real graph edge(s) "
                    "-- a fact about that symbol, not a confirmation of the match"
                ),
                entry_class="FACT",
                evidence=tuple(f"{e.edge_type}: {e.target}" for e in edges),
            )
        )
    return tuple(claims)


def explain(agent: KnowledgeAgent, symbol: str, depth: Depth | None = None) -> Answer:
    return agent.answer(f"how does `{symbol}` work?", depth=depth)


def dependencies(agent: KnowledgeAgent, symbol: str) -> Answer:
    """What this symbol reaches outward to."""
    hits = reachable(agent.graph, symbol, ("calls",), max_hops=DEPENDENCY_HOPS)
    direct = [h for h in hits if h.hop == 1]
    transitive = [h for h in hits if h.hop > 1]
    return Answer(
        question=f"what does {symbol} depend on?",
        short_answer=f"{len(direct)} direct, {len(transitive)} transitive.",
        relevant_flow=" ; ".join(" -> ".join(h.path) for h in hits) or "",
        claims=(
            _slice_claim(symbol, "direct dependency", "direct dependencies", direct),
            _slice_claim(symbol, "transitive dependency", "transitive dependencies", transitive),
        ),
    )


def impact(agent: KnowledgeAgent, symbol: str) -> Answer:
    """What reaches inward to this symbol.

    Direct and secondary are separate claims, never merged: "conflating them
    hides which consequences are certain and which are worth double-checking
    before the change" (§ Impact analysis).
    """
    hits = reachable(agent.graph, symbol, ("called_by",), max_hops=IMPACT_SECONDARY_HOPS)
    direct = [h for h in hits if h.hop <= IMPACT_DIRECT_HOPS]
    secondary = [h for h in hits if h.hop > IMPACT_DIRECT_HOPS]
    return Answer(
        question=f"what happens if I change {symbol}?",
        short_answer=f"{len(direct)} direct dependent(s), {len(secondary)} secondary.",
        things_to_be_aware_of=(
            "Secondary dependents are reached through another symbol, so a change here affects "
            "them only if the direct dependent's own behaviour changes."
        ),
        claims=(
            _slice_claim(symbol, "direct dependent", "direct dependents", direct),
            _slice_claim(symbol, "secondary dependent", "secondary dependents", secondary),
        ),
    )


def _slice_claim(symbol: str, singular: str, plural: str, hits: list) -> Claim:
    """A graph slice is a FACT when it found something and a FACT when it did
    not: both are observations of the same materialized edge set. The wording
    scopes it to the graph rather than to the world -- "the graph holds no
    dependent" is an observation, while "nothing depends on this" is a claim
    about the world that was never established.

    Takes both word forms rather than appending "(s)": the live CLI printed
    "1 direct(s)", which reads as unfinished output in an answer whose whole
    point is being trustworthy.
    """
    if hits:
        return Claim(
            statement=(
                f"{len(hits)} {singular if len(hits) == 1 else plural} of {symbol}: "
                + ", ".join(sorted(h.node for h in hits))
            ),
            entry_class="FACT",
            evidence=tuple(f"{' -> '.join(h.path)} ({h.hop} hop)" for h in hits),
        )
    return Claim(
        statement=f"the graph holds no {singular} of {symbol}",
        entry_class="FACT",
        evidence=(f"ProjectGraph traversal from {symbol!r} returned no node at that depth",),
    )


def setup(agent: KnowledgeAgent, task: str) -> Answer:
    """Cited operational steps. Every claim names the file and line it came
    from -- a generic recipe is wrong the moment the project's tooling differs
    from the guess."""
    claims: list[Claim] = []
    files: list[str] = []
    for source in SETUP_SOURCES:
        try:
            text = investigator.read_file(source)
        except (OSError, ValueError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.startswith(f"{task}:") or line.startswith(f"{task} "):
                claims.append(
                    Claim(
                        statement=f"{source} defines {task!r}: {line.strip()}",
                        entry_class="FACT",
                        evidence=(f"{source}:{lineno}",),
                    )
                )
                files.append(source)
                break
    if not claims:
        claims.append(
            Claim(
                statement=f"no {task!r} entry point was found in the files searched",
                entry_class="FACT",
                evidence=tuple(SETUP_SOURCES),
            )
        )
    return Answer(
        question=f"how do I {task} this project?",
        short_answer=(f"Defined in {files[0]}." if files else f"Not found in {len(SETUP_SOURCES)} manifests."),
        important_files=tuple(dict.fromkeys(files)),
        claims=tuple(claims),
    )


def conventions(agent: KnowledgeAgent, area: str | None = None) -> Answer:
    """TEAM_KNOWLEDGE and INFERENCE from ProjectMemory, scoped to an area.

    FACT entries are deliberately excluded: a convention is what the team
    decided, not what the code currently happens to do. Reading conventions off
    the code is how an accident becomes a rule.
    """
    entries = [
        entry
        for entry_class in ("TEAM_KNOWLEDGE", "INFERENCE")
        for entry in agent.memory.query_by_class(entry_class)
        if area is None or area in entry.statement
    ]
    claims = tuple(
        Claim(
            statement=entry.statement,
            entry_class=entry.entry_class,
            evidence=entry.evidence,
            confidence=entry.confidence,
            provided_by=entry.provided_by,
            temporal_state=entry.temporal_state,
        )
        for entry in entries
    )
    if not claims:
        claims = (
            Claim(
                statement=f"ProjectMemory holds no convention for {area or 'any area'}",
                entry_class="FACT",
                evidence=("ProjectMemory.query_by_class(TEAM_KNOWLEDGE, INFERENCE) returned nothing",),
            ),
        )
    return Answer(
        question=f"what are our conventions for {area or 'this project'}?",
        short_answer=f"{len(entries)} recorded convention(s).",
        things_to_be_aware_of=(
            "ProjectMemory does not persist between runs (#209 has no load or save), so this is "
            "empty on a fresh process rather than authoritative."
        ),
        claims=claims,
    )


def history(agent: KnowledgeAgent, symbol: str) -> Answer:
    return agent.answer(f"how did `{symbol}` evolve?")


def all_methods() -> tuple[str, ...]:
    """The seven, so a test can assert the surface is complete rather than
    checking whichever ones someone remembered to call."""
    return ("find", "explain", "dependencies", "impact", "setup", "conventions", "history")


if __name__ == "__main__":
    import worked_answer
    import worked_trace
    from answer import render

    # One index build, shared by both worked examples and the seven-method
    # surface below -- indexing the crate is the expensive part of this CLI.
    agent = KnowledgeAgent.build("buzz-core")

    print("#" * 70)
    print("# Worked example 1 -- the investigation trace (STEP 10)")
    print("#" * 70 + "\n")
    worked_trace.main(agent)

    print("\n" + "#" * 70)
    print("# Worked example 2 -- the six-section answer format (STEP 11)")
    print("#" * 70 + "\n")
    worked_answer.main(agent)

    print("\n" + "#" * 70)
    print("# The seven knowledge.* methods, live (STEP 9)")
    print("#" * 70)
    for name, call in (
        ("find", lambda: find(agent, "the check that decides whether a kind is gated for sharing")),
        ("explain", lambda: explain(agent, "is_shared_gated_kind")),
        ("dependencies", lambda: dependencies(agent, "is_shared_gated_kind")),
        ("impact", lambda: impact(agent, "is_shared_gated_kind")),
        ("setup", lambda: setup(agent, "test")),
        ("conventions", lambda: conventions(agent, "kind")),
        ("history", lambda: history(agent, "is_shared_gated_kind")),
    ):
        print(f"\n{'=' * 70}\nknowledge.{name}\n{'=' * 70}")
        print(render(call()))
