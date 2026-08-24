"""Question decomposition -- issue #211, STEP 4.

Maps a natural-language question to (intent, target, temporal_state, depth):
the four things the decision logic needs before it can choose a component.

Deterministic and rule-based -- no model call, decided 2026-08-24 (see the
plan's APPROACH NOTE). The consequence is honest and worth stating: this
classifies the phrasings below and nothing else. A question outside them falls
back to EXPLAIN rather than guessing, and a caller that needs a specific intent
can name it directly through knowledge.py's own methods (STEP 9) instead of
phrasing a sentence and hoping.

Intents are the seven the design doc's § Data Model item 8 names -- the
programmatic interface and the intents are deliberately the same list, so a
question and a direct call route to identical logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from memory import TemporalState

Intent = Literal[
    "FIND",
    "EXPLAIN",
    "DEPENDENCIES",
    "IMPACT",
    "SETUP",
    "CONVENTIONS",
    "HISTORY",
]

# The design doc's § Data Model item 6 levels, verbatim in meaning.
Depth = Literal[
    "SUMMARY",
    "ONBOARDING",
    "IMPLEMENTATION",
    "TRACE",
    "RATIONALE",
    "IMPACT",
]

# § Reasoning Rules, "Development-environment operational answers" names these
# eight tasks; knowledge.setup(task) takes one of them.
SETUP_TASKS = ("install", "run", "seed", "migrate", "test", "lint", "build", "deploy")

# Matched in this order, not SETUP_TASKS's, and "run" is last on purpose.
# "how do I run the tests" names two tasks, and the one the caller wants is
# `test` -- "run" is the verb, not the subject. Checking `run` first answered
# "how do I start the app" to a question about the test suite. The design doc's
# own worked example is exactly this phrasing ("How do I run integration
# tests?" -> Makefile:34's test-integration target).
_TASK_MATCH_ORDER = ("install", "seed", "migrate", "test", "lint", "build", "deploy", "run")

# An identifier the caller already knows the name of: snake_case, CamelCase, a
# path-ish or ::-qualified name, or anything they backticked. A question with no
# such token is the case § Concept Retrieval exists for -- the caller cannot
# name the thing yet.
_BACKTICKED = re.compile(r"`([^`]+)`")
_IDENTIFIER = re.compile(
    r"\b(?:"
    r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+"     # snake_case
    r"|[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+"  # CamelCase
    r"|[A-Za-z_][A-Za-z0-9_]*::[A-Za-z0-9_:]+"  # a::b
    r")\b"
)


@dataclass(frozen=True)
class Question:
    raw: str
    intent: Intent
    target: str | None
    temporal_state: TemporalState
    depth: Depth
    setup_task: str | None = None


def extract_target(text: str) -> str | None:
    """A backticked span wins over a bare identifier: the caller marked it up
    on purpose, and a marked-up target may legitimately not look like an
    identifier at all (a file path, a config key)."""
    backticked = _BACKTICKED.search(text)
    if backticked:
        return backticked.group(1).strip() or None
    match = _IDENTIFIER.search(text)
    return match.group(0) if match else None


def classify_temporal_state(text: str) -> TemporalState:
    """WORKING unless the question is explicitly historical or comparative --
    the default the design doc's § Data Model item 5 states."""
    lowered = text.lower()
    if any(
        w in lowered
        for w in ("evolve", "evolved", "over time", "used to", "history", "originally", "when was", "why does")
    ):
        return "HISTORY"
    if any(w in lowered for w in ("at head", "before my changes", "before this change", "as committed", "on the branch")):
        return "BASE"
    return "WORKING"


def classify_depth(text: str, intent: Intent) -> Depth:
    lowered = text.lower()
    if intent == "IMPACT":
        return "IMPACT"
    if intent == "HISTORY":
        return "RATIONALE"
    if any(w in lowered for w in ("briefly", "quickly", "in a sentence", "one line", "tl;dr")):
        return "SUMMARY"
    if any(w in lowered for w in ("exactly", "line by line", "precisely", "which line")):
        return "IMPLEMENTATION"
    if any(w in lowered for w in ("trace", "end to end", "all the way", "call to database")):
        return "TRACE"
    if any(w in lowered for w in ("why", "rationale", "design", "decision")):
        return "RATIONALE"
    return "ONBOARDING"


def _setup_task(text: str) -> str | None:
    """A setup question needs BOTH an operational verb phrase and a named task.
    "how do I run the tests" is SETUP; "how does the test runner work" is not,
    even though both contain "test" -- the second asks about mechanism, and
    routing it to SETUP would answer a different question than the one asked.
    """
    lowered = text.lower()
    asks_how_to = any(
        p in lowered for p in ("how do i", "how do we", "how to", "what command", "steps to")
    )
    if not asks_how_to:
        return None
    for task in _TASK_MATCH_ORDER:
        if re.search(rf"\b{task}(?:s|ing|ed)?\b", lowered):
            return task
    return None


def classify_intent(text: str) -> tuple[Intent, str | None]:
    """First match wins, and the order below is the whole design.

    Specific phrasings are tested before general ones because the general ones
    subsume them: "what happens if I change X" is also a "what ... X" question,
    and "how do I run the tests" is also a "how ..." question. Reordering these
    silently reroutes questions, so the order is asserted by the tests rather
    than left to reading.
    """
    lowered = text.lower()

    task = _setup_task(text)
    if task:
        return "SETUP", task

    if any(p in lowered for p in ("what happens if", "what breaks", "safe to change", "impact of", "if i change")):
        return "IMPACT", None

    if any(p in lowered for p in ("depend on", "depends on", "what does it call", "what does it use", "dependencies of")):
        return "DEPENDENCIES", None

    if any(p in lowered for p in ("evolve", "evolved", "over time", "why does", "why do", "when was", "used to")):
        return "HISTORY", None

    if any(p in lowered for p in ("convention", "conventions", "do we usually", "our pattern", "house style", "are we allowed")):
        return "CONVENTIONS", None

    # FIND is the no-name case, so it is decided by the absence of a target
    # rather than by phrasing alone -- "where is `AuthMiddleware`" is a caller
    # who already has the name and wants the symbol, not a concept search.
    if any(p in lowered for p in ("where is", "where's", "what handles", "something that", "find the code", "which file")):
        if extract_target(text) is None:
            return "FIND", None

    return "EXPLAIN", None


def decompose(text: str) -> Question:
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"question must be a non-empty string, got {text!r}")
    intent, task = classify_intent(text)
    return Question(
        raw=text,
        intent=intent,
        target=extract_target(text),
        temporal_state=classify_temporal_state(text),
        depth=classify_depth(text, intent),
        setup_task=task,
    )
