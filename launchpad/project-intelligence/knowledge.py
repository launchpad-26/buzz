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

from dataclasses import replace

import investigator
from answer import Answer, Claim
from graph import reachable
from knowledge_agent import KnowledgeAgent
from question import Depth, decompose

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

    # Two DIFFERENT no-answer states, which an earlier version conflated into
    # one claim that was simply false.
    #
    # `candidate_score is None` means index.search() came back empty -- nothing
    # was returned at all. It is reachable: find_it_for_me returns a
    # PipelineResult with EVERY field None (not None itself) for an index built
    # from zero symbols, and the first version of this guard tested only
    # `result is not None`, so that raised TypeError instead of answering.
    #
    # A score at or below the floor is the opposite: the index DID return a
    # candidate, and this code rejected it. Saying "the SemanticIndex returned
    # no candidate" there is a FACT that is untrue -- caught by the cross-model
    # review, which reproduced `find()` reporting exactly that while
    # find_concept() had returned is_shared_gated_kind at score 0.0. A false
    # FACT is the worst output this layer can produce, and it was produced by
    # the fix for another defect of the same class.
    rejected_candidate = None
    if result is not None:
        if result.candidate_score is None:
            result = None
        elif result.candidate_score <= MINIMUM_CANDIDATE_SCORE:
            rejected_candidate = result
            result = None

    if result is None:
        if rejected_candidate is not None:
            return Answer(
                question=query,
                short_answer="No candidate resolved for that concept.",
                things_to_be_aware_of=(
                    "The index did return a top-ranked symbol, and it was rejected here for "
                    "sharing no token at all with the concept -- not withheld because the index "
                    "was silent."
                ),
                claims=(
                    Claim(
                        statement=(
                            f"the top-ranked candidate {rejected_candidate.qualified_name} scored "
                            f"{rejected_candidate.candidate_score}, at or below the floor of "
                            f"{MINIMUM_CANDIDATE_SCORE}"
                        ),
                        entry_class="FACT",
                        evidence=(
                            f"SemanticIndex.search({query!r}) over {agent.symbol_count} symbols",
                        ),
                    ),
                ),
            )
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
    """The full four-stage pipeline, at the requested depth -- #571.

    IMPACT is the one depth the pipeline itself cannot answer: locate/read/
    callers/tests/history has no notion of a SECONDARY (2-hop) dependent, and
    #571 is explicit that depth must not change what gets investigated -- so
    rather than approximate with direct-only data, IMPACT delegates whole to
    impact(), which already reads the graph for exactly this (direct and
    secondary, "never merged" -- see impact()'s own docstring). Every other
    depth still runs the one investigation and only renders differently.
    """
    if depth == "IMPACT":
        return replace(impact(agent, symbol), depth="IMPACT")
    return agent.answer(f"how does `{symbol}` work?", depth=depth)


def dependencies(agent: KnowledgeAgent, symbol: str) -> Answer:
    """What this symbol reaches outward to."""
    hits = reachable(agent.graph, symbol, ("calls",), max_hops=DEPENDENCY_HOPS)
    direct = [h for h in hits if h.hop == 1]
    transitive = [h for h in hits if h.hop > 1]
    return Answer(
        question=f"what does {symbol} depend on?",
        # Phrased without "(s)" for the same reason the claims were: the
        # pluralisation fix landed on claims only, and its regression test
        # iterated result.claims -- so the defect its own narrative described
        # survived one field over, invisibly. Caught by the review panel.
        short_answer=(
            f"{len(direct)} direct and {len(transitive)} transitive "
            f"{'dependency' if len(direct) + len(transitive) == 1 else 'dependencies'}."
        ),
        relevant_flow=" ; ".join(" -> ".join(h.path) for h in hits) or "",
        things_to_be_aware_of=SNAPSHOT_CAVEAT,
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
        short_answer=(
            f"{len(direct)} direct and {len(secondary)} secondary "
            f"{'dependent' if len(direct) + len(secondary) == 1 else 'dependents'}."
        ),
        things_to_be_aware_of=(
            "Secondary dependents are reached through another symbol, so a change here affects "
            "them only if the direct dependent's own behaviour changes.\n" + SNAPSHOT_CAVEAT
        ),
        claims=(
            _slice_claim(symbol, "direct dependent", "direct dependents", direct),
            _slice_claim(symbol, "secondary dependent", "secondary dependents", secondary),
        ),
    )


def _slice_claim(symbol: str, singular: str, plural: str, hits: list) -> Claim:
    """A graph slice, scoped in its wording to THE INDEX rather than the world.

    Both branches are FACT, and the wording is what earns that: every statement
    says what the indexed graph holds, never what the codebase contains. "The
    indexed graph holds no dependent" is an observation of a snapshot; "nothing
    depends on this" is a claim about the world that was never established.

    Cross-model review pushed on this: dependencies() and impact() return FACT
    claims while every live Investigator tool is disabled, so nothing was
    re-verified against the tree. That is true, and the answer is scoping rather
    than verifying -- re-confirming every edge in a traversal would mean a live
    read per node, which turns a graph query into an investigation. The claim is
    honest as long as it never says more than "the index says so", which is why
    "indexed" appears in every statement here and the caller adds the snapshot
    caveat.

    Takes both word forms rather than appending "(s)": the live CLI printed
    "1 direct(s)", which reads as unfinished output in an answer whose whole
    point is being trustworthy.
    """
    if hits:
        return Claim(
            statement=(
                f"the indexed graph holds {len(hits)} "
                f"{singular if len(hits) == 1 else plural} of {symbol}: "
                + ", ".join(sorted(h.node for h in hits))
            ),
            entry_class="FACT",
            evidence=tuple(f"{' -> '.join(h.path)} ({h.hop} hop)" for h in hits),
        )
    return Claim(
        statement=f"the indexed graph holds no {singular} of {symbol}",
        entry_class="FACT",
        evidence=(f"ProjectGraph traversal from {symbol!r} returned no node at that depth",),
    )


# Appended to any answer built purely from the in-memory graph, with no live
# read. The graph is built once by KnowledgeAgent.build(); an edit to the tree
# after that point is invisible to it.
SNAPSHOT_CAVEAT = (
    "Derived from the graph indexed at agent build time, with no live re-read -- an edit to the "
    "working tree since then is not reflected here."
)


def setup(agent: KnowledgeAgent, task: str) -> Answer:
    """Cited operational steps. Every claim names the file and line it came
    from -- a generic recipe is wrong the moment the project's tooling differs
    from the guess."""
    claims: list[Claim] = []
    files: list[str] = []
    # Reads through the agent's injected seam, not the process-global
    # investigator. Cross-model review found the seam was split: investigation
    # used agent.tools while verification and this function bypassed it, so a
    # test driving an injected repository still had these two functions reading
    # the real worktree.
    for source in SETUP_SOURCES:
        try:
            text = agent.tools.read_file(source)
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
        # Superseded entries are excluded here for the same reason as in
        # assemble._team_knowledge: a retracted convention presented as current
        # is worse than one omitted. This consumer had the same gap.
        if entry.superseded_by is None and (area is None or area in entry.statement)
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


def ask(agent: KnowledgeAgent, text: str) -> Answer:
    """Route a natural-language question to the method that answers it.

    This is the piece `question.py` always claimed existed. Its docstring said
    "a question and a direct call route to identical logic" while nothing
    dispatched on intent at all: `KnowledgeAgent.run()` ran the EXPLAIN pipeline
    for every question, so "how do I run the tests?" classified SETUP with
    setup_task="test", discarded both, and answered "no symbol named in the
    question" -- while setup() sat right here and would have answered it.

    Five of seven intents were dead values. The review panel named it as the
    FOURTH instance of the dead-classified-value defect on a branch that had
    already fixed that class three times (the confidence predicate,
    Findings.sufficient, and BASE). Fixing each instance as it surfaced and never
    sweeping for the rest is the actual mistake; this time every intent is
    dispatched and a test asserts each one reaches its own method.

    It lives here rather than in KnowledgeAgent.run() because knowledge.py
    imports knowledge_agent -- routing from inside run() would be a cycle. So
    run() stays what it honestly is: the explain pipeline.
    """
    question = decompose(text)

    if question.intent == "SETUP":
        # setup_task is guaranteed non-None for SETUP by classify_intent, which
        # returns the intent and the task together.
        return setup(agent, question.setup_task or "")
    if question.intent == "FIND":
        return find(agent, text)
    if question.intent == "CONVENTIONS":
        return conventions(agent, question.target)

    if question.target is None:
        # Every remaining intent needs a subject. Saying so beats answering a
        # different question, and beats crashing on a None target.
        return Answer(
            question=text,
            short_answer="No symbol named in the question.",
            things_to_be_aware_of=(
                f"This reads as a {question.intent} question, which needs a named symbol. "
                "Use knowledge.find() for a concept whose name you do not know yet."
            ),
            depth=question.depth,
        )

    if question.intent == "DEPENDENCIES":
        return dependencies(agent, question.target)
    if question.intent == "IMPACT":
        # Stamped explicitly, matching explain()'s own IMPACT delegation
        # (line ~189 above): impact() never sets depth itself, and
        # classify_depth() always classifies an IMPACT-intent question's
        # depth as "IMPACT", so this is never overwriting a different value.
        return replace(impact(agent, question.target), depth=question.depth)
    if question.intent == "HISTORY":
        return history(agent, question.target)
    return explain(agent, question.target, question.depth)


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
