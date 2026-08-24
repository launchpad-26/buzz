"""The "how does auth work?" worked example -- issue #211, STEP 11.

The design doc's § Data Model item 7 example, reproduced against this codebase's
own equivalent flow. Buzz has no JWT/Auth0 middleware; its nearest real analogue
is the shared-kind gating decision in crates/buzz-core/src/kind.rs -- a
predicate every gated event passes through, exactly the shape the doc's
AuthMiddleware example has.

Two things this adds over the ordinary assembled answer:

  * `## Relevant flow` is a real ProjectGraph traversal with its hop count, not
    prose and not a caller list. graph.reachable() returns the path, so the flow
    line is a fact about materialized edges that a reader can re-derive.
  * All six sections are filled from real data, which is what makes this a
    reproduction of the doc's example rather than a partial one.

The doc's own example is fictional -- AuthMiddleware.ts, Auth0, a JWKS cache
TTL. Nothing here copies its content; only its shape.
"""

from __future__ import annotations

from dataclasses import replace

from answer import Answer, render
from graph import Reachable, reachable
from knowledge_agent import KnowledgeAgent

WORKED_CRATE = "buzz-core"
WORKED_SYMBOL = "is_unshared_gated_event"
WORKED_QUESTION = f"how does `{WORKED_SYMBOL}` work?"

MAX_FLOW_HOPS = 3


def deepest_path(agent: KnowledgeAgent, symbol: str, max_hops: int = MAX_FLOW_HOPS) -> Reachable | None:
    """The longest call path out of a symbol, as the design doc's Flow format.

    Deepest rather than first: a one-hop neighbour is a dependency, and a flow
    is what the request actually travels through. Ties break on the path itself
    so the output is stable across runs -- an unstable demo cannot be diffed.
    """
    hits = reachable(agent.graph, symbol, ("calls",), max_hops=max_hops)
    if not hits:
        return None
    return max(hits, key=lambda r: (r.hop, r.path))


def render_flow(hit: Reachable) -> str:
    return f"{' -> '.join(hit.path)}  ({hit.hop} hop{'s' if hit.hop != 1 else ''})"


def build(agent: KnowledgeAgent) -> Answer:
    """The assembled answer, with its flow replaced by a real traversal.

    Composed rather than special-cased inside assemble(): explain()'s
    caller-based flow is right for "what reaches this", and a graph traversal is
    right for "what does this reach". Both are real; they answer different
    questions, so this picks one instead of changing the other.
    """
    answer = agent.answer(WORKED_QUESTION)
    hit = deepest_path(agent, WORKED_SYMBOL)
    if hit is None:
        return answer
    return replace(answer, relevant_flow=render_flow(hit))


def section_names(rendered: str) -> list[str]:
    return [line[3:] for line in rendered.splitlines() if line.startswith("## ")]


def main() -> None:
    agent = KnowledgeAgent.build(WORKED_CRATE)
    answer = build(agent)
    rendered = render(answer)
    print(f"Question: {WORKED_QUESTION}\n")
    print(rendered)

    print("\n=== checks on this output ===")
    names = section_names(rendered)
    print(f"  sections present ({len(names)}/6): {', '.join(names)}")
    hit = deepest_path(agent, WORKED_SYMBOL)
    print(f"  flow is a real traversal: {hit is not None}, hops={hit.hop if hit else 0}")
    inferences = answer.claims_of_class("INFERENCE")
    print(f"  inferences in caveats: {len(inferences)}")
    for claim in inferences:
        print(f"    - {claim.statement} :: evidence {claim.evidence}")


if __name__ == "__main__":
    main()
