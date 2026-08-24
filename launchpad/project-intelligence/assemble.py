"""Decision logic stage 4 -- issue #211, STEP 8.

"Construct the explanation only after 1-3, labeling every non-FACT claim."

Assembly reads only what the earlier stages found. It never reaches for a tool
of its own, and it never states anything the Findings, the Trace or
ProjectMemory did not supply -- that separation is what makes an answer
auditable: every line of prose here traces to a stage that recorded its own
evidence.

Each FACT goes back through verify.verified_fact rather than being asserted
from the Findings directly. Stage 3 read the file to locate the definition;
stage 2 re-reads the exact range to confirm the claim it is about to make. That
is deliberate duplication -- locating a symbol and confirming a statement about
it are different questions, and the second is the one that catches a citation
which resolves without supporting its claim.
"""

from __future__ import annotations

from answer import Answer, Claim
from investigation import Findings
from memory import ProjectMemory
from question import Question
from trace import Trace
from verify import verified_fact

# Confidence for an inference drawn from a commit message. A message states
# intent, never a measured outcome -- the design doc's own worked example makes
# exactly this distinction ("gives a rationale, but the commit message states
# intent, not a measured result").
COMMIT_INTENT_CONFIDENCE = 0.5

# Confidence for "appears unused". Two tools looked and found nothing, which is
# real evidence, but absence within one crate is not absence in the workspace.
APPEARS_UNUSED_CONFIDENCE = 0.4

PREDICATE_CONFIDENCE = 0.7


def _team_knowledge(memory: ProjectMemory, target: str) -> list[Claim]:
    """TEAM_KNOWLEDGE passes through verbatim, with its author.

    Never re-verified and never downgraded for lack of corroborating code: the
    design doc requires it not be "overridden by the mere absence of
    corroborating code", and it is the one class that exists for statements no
    file can confirm.
    """
    return [
        Claim(
            statement=entry.statement,
            entry_class="TEAM_KNOWLEDGE",
            provided_by=entry.provided_by,
            temporal_state=entry.temporal_state,
        )
        for entry in memory.query_by_class("TEAM_KNOWLEDGE")
        if target in entry.statement
    ]


def assemble(
    question: Question,
    findings: Findings,
    trace: Trace,
    memory: ProjectMemory,
) -> Answer:
    target = findings.target

    if not findings.located:
        # An answer that could not find its subject says so, with the trace as
        # its evidence. Returning an empty Answer would read as "nothing to
        # report about a symbol that exists".
        return Answer(
            question=question.raw,
            short_answer=f"{target} could not be located in the index.",
            things_to_be_aware_of=(
                "This is a statement about the index, not about the codebase -- the symbol may "
                "exist under a different qualified name, or in a crate that was not searched."
            ),
            claims=(
                Claim(
                    statement=f"the index has no locatable definition for {target}",
                    entry_class="FACT",
                    evidence=tuple(f"{c.tool}({c.args}) -> {c.detail}" for c in trace.calls),
                ),
            ),
        )

    match = findings.match
    citation_file, citation_line = match.file, findings.definition_line  # type: ignore[union-attr]
    claims: list[Claim] = [
        verified_fact(
            f"{target} is defined as {match.signature}",  # type: ignore[union-attr]
            match.signature.strip(),  # type: ignore[union-attr]
            citation_file,
            citation_line,  # type: ignore[arg-type]
            citation_line,  # type: ignore[arg-type]
            trace,
        )
    ]

    if findings.callers:
        claims.append(
            Claim(
                statement=f"{len(findings.callers)} caller(s) in this crate: "
                + ", ".join(sorted({c.caller_qualified_name for c in findings.callers})),
                entry_class="FACT",
                evidence=tuple(f"{c.file}:{c.line}" for c in findings.callers),
            )
        )

    if findings.test_sites:
        claims.append(
            Claim(
                statement=f"{len(findings.test_sites)} test-side mention(s)",
                entry_class="FACT",
                evidence=tuple(f"{m.file}:{m.line}" for m in findings.test_sites),
            )
        )

    if not findings.corroborated:
        # The claim rests on lookups having actually happened. If no
        # find_references or search_text call is in the trace, nothing looked,
        # and "appears unused" would be asserting absence of evidence as
        # evidence of absence -- so no claim is made at all.
        #
        # Found by running this step's own tests: an empty trace produced an
        # INFERENCE with an empty evidence tuple, which Claim rightly refused.
        # The fix is not to invent a fallback evidence string; it is to notice
        # that an unfounded claim should not exist.
        looked = tuple(
            f"{c.tool}({c.args}) -> {c.detail}"
            for c in trace.calls
            if c.tool in ("find_references", "search_text")
        )
        if looked:
            claims.append(
                Claim(
                    statement=f"{target} appears unused within this crate",
                    entry_class="INFERENCE",
                    evidence=looked,
                    confidence=APPEARS_UNUSED_CONFIDENCE,
                )
            )

    if findings.history:
        newest = findings.history[0]
        claims.append(
            Claim(
                statement=f"the stated reason for its most recent change is {newest.message.strip()!r}",
                entry_class="INFERENCE",
                evidence=(f"commit {newest.hash} ({newest.date}) by {newest.author}",),
                confidence=COMMIT_INTENT_CONFIDENCE,
                temporal_state="HISTORY",
            )
        )

    if match.signature.rstrip().endswith("bool"):  # type: ignore[union-attr]
        claims.append(
            Claim(
                statement=f"{target} is a decision point rather than a transformation",
                entry_class="INFERENCE",
                evidence=(f"returns bool -- {citation_file}:{citation_line}",),
                confidence=PREDICATE_CONFIDENCE,
            )
        )

    claims.extend(_team_knowledge(memory, target))

    files = [citation_file]
    files += sorted({c.file for c in findings.callers} | {m.file for m in findings.test_sites})

    return Answer(
        question=question.raw,
        short_answer=f"A {match.kind} at {citation_file}:{citation_line}.",  # type: ignore[union-attr]
        how_it_works=f"{match.signature}".strip(),  # type: ignore[union-attr]
        relevant_flow=(
            " | ".join(
                f"{c.caller_qualified_name} -> {target}"
                for c in sorted(findings.callers, key=lambda c: c.caller_qualified_name)
            )
            if findings.callers
            else ""
        ),
        important_files=tuple(dict.fromkeys(files)),
        things_to_be_aware_of=(
            f"{len(findings.history)} commit(s) touch its definition line."
            if findings.history
            else (
                "No caller and no test-side mention were found in this crate."
                if not findings.corroborated
                else ""
            )
        ),
        claims=tuple(claims),
    )
