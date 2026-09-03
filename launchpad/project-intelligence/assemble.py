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

from answer import Answer, Claim, format_confidence
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

# Emitted when the question implied BASE (the repository at HEAD) but every
# claim was gathered from WORKING (the live tree).
#
# The design doc is explicit: "If WORKING diverges from BASE in a way that
# changes the answer, say so -- don't silently answer from one state while the
# question implied the other." Reading BASE properly needs `git show HEAD:<path>`
# and is NOT implemented; that is filed rather than faked. What is fixed here is
# the silence. Cross-model review found BASE being classified by question.py and
# then ignored by everything downstream -- the third dead-classified-value defect
# in this branch, after the confidence predicate and Findings.sufficient.
# Wording matters here and the first version got it wrong. It said "every claim
# below was read from the WORKING tree", which is false: an answer can carry a
# HISTORY claim (drawn from git history) or TEAM_KNOWLEDGE with its own temporal
# state, and both sit beneath this sentence. A caveat that overstates what it
# covers is the same defect class the caveat exists to fix -- caught by the
# second cross-model pass, in prose written by the first fix round.
#
# It now says only what is true of every case: BASE was never read, and each
# claim carries its own temporal_state for a reader who needs the detail.
BASE_NOT_HONOURED = (
    "This question asked about the repository BEFORE the current changes (BASE). BASE reads are "
    "not implemented, so nothing here was read from BASE -- code claims come from the WORKING "
    "tree, and each claim carries its own temporal_state. If WORKING and BASE differ, this "
    "answer describes WORKING."
)


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
        # `superseded_by` is why #209 built the reconciliation rule, and this
        # never consumed it. Cross-model review reproduced Alice's "do not use"
        # and Bob's superseding "approved for use" BOTH surfacing as current
        # TEAM_KNOWLEDGE, contradicting each other with no sign of which won.
        # Presenting a retracted statement as current is worse than omitting it:
        # the reader acts on guidance the team has already withdrawn.
        if entry.superseded_by is None and target in entry.statement
    ]


def assemble(
    question: Question,
    findings: Findings,
    trace: Trace,
    memory: ProjectMemory,
    read_file=None,
) -> Answer:
    target = findings.target

    if not findings.located:
        # An answer that could not find its subject says so, with the trace as
        # its evidence. Returning an empty Answer would read as "nothing to
        # report about a symbol that exists".
        #
        # The BASE caveat belongs here too, and its absence was the sharpest
        # form of the defect: a symbol DELETED in WORKING but present at BASE
        # would report "not in the index" to a question asked specifically about
        # BASE -- an answer that is not merely incomplete but points the reader
        # away from the state they asked about. Found by the second cross-model
        # pass; the first fix round wired the caveat into the located path only.
        not_located_caveats = [
            "This is a statement about the index, not about the codebase -- the symbol may "
            "exist under a different qualified name, or in a crate that was not searched."
        ]
        if question.temporal_state == "BASE":
            not_located_caveats.insert(0, BASE_NOT_HONOURED)
        return Answer(
            question=question.raw,
            short_answer=f"{target} could not be located in the index.",
            things_to_be_aware_of="\n".join(not_located_caveats),
            claims=(
                Claim(
                    statement=f"the index has no locatable definition for {target}",
                    entry_class="FACT",
                    # A FACT needs evidence, and an empty trace supplies none --
                    # which raised ValueError out of a public function. Not
                    # reachable through run() (locate always records a call), but
                    # assemble() is public and the review panel reached it. The
                    # fallback names the real absence rather than inventing a
                    # citation.
                    evidence=tuple(f"{c.tool}({c.args}) -> {c.detail}" for c in trace.calls)
                    or ("no investigation was recorded for this target",),
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
            **({} if read_file is None else {"read_file": read_file}),
        )
    ]

    if findings.callers:
        # Call SITES and CALLERS are different counts, and the live run made the
        # difference matter: five sites in kind.rs belong to two callers, four of
        # them inside one test. Reporting "5 caller(s)" and then naming two read
        # as three names having gone missing.
        caller_names = sorted({c.caller_qualified_name for c in findings.callers})
        claims.append(
            Claim(
                statement=(
                    f"{len(caller_names)} caller(s) across {len(findings.callers)} call site(s): "
                    + ", ".join(caller_names)
                ),
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

    # Deduped by caller name. The live run produced the same caller-to-target
    # arrow four times over, which reads as four distinct callers rather than
    # four call sites in one test.
    flow = " | ".join(
        f"{name} -> {target}"
        for name in sorted({c.caller_qualified_name for c in findings.callers})
    )

    return Answer(
        question=question.raw,
        short_answer=f"A {match.kind} at {citation_file}:{citation_line}.",  # type: ignore[union-attr]
        how_it_works=f"{match.signature}".strip(),  # type: ignore[union-attr]
        relevant_flow=flow,
        important_files=tuple(dict.fromkeys(files)),
        things_to_be_aware_of=_caveats(findings, claims, trace, question),
        claims=tuple(claims),
    )


def _caveats(findings: Findings, claims: list[Claim], trace: Trace, question: Question | None = None) -> str:
    """The caveats section IS the inferences, restated where a reader meets them.

    Not a separate authored paragraph: an authored caveat can say something the
    claims do not support, and then `## Sources` and `## Things to be aware of`
    disagree about the same answer. Building it from the INFERENCE claims makes
    that impossible by construction -- the same reason Answer has no authored
    `sources` field.

    An earlier version emitted this section only when history existed or nothing
    corroborated, so the common case rendered five of six sections with the
    inferences visible only under Sources.
    """
    lines: list[str] = []
    # First, because it changes how everything under it should be read.
    if question is not None and question.temporal_state == "BASE":
        lines.append(BASE_NOT_HONOURED)
    lines += [
        f"{c.statement} (INFERENCE, confidence {format_confidence(c.confidence)}; "
        f"{'; '.join(c.evidence)})"
        for c in claims
        if c.entry_class == "INFERENCE"
    ]
    if findings.history:
        # #569: the history stage used to ask over a HISTORY_LINE_WINDOW-wide
        # range, so this said "the range queried around it" to avoid claiming
        # a narrower query than the one that actually produced these commits.
        # Now that inspect_git_history() handles a single line correctly, the
        # history stage asks about the definition line itself (see
        # investigation._history()), so the citation says exactly that.
        lines.append(f"{len(findings.history)} commit(s) touch that line.")
    if not findings.corroborated and _looked_for_corroboration(trace):
        # Gated on having actually looked. Since stage 1's confidence can now
        # skip the corroboration stages entirely, `not corroborated` alone no
        # longer means "searched and found nothing" -- it can equally mean
        # "never searched, because cached knowledge already agreed". Saying
        # "no caller was found" in the second case reports an absence nobody
        # established, which is the same defect as the "appears unused" claim
        # guarded in assemble() above.
        lines.append("No caller and no test-side mention were found in this crate.")
    return "\n".join(lines)


def _looked_for_corroboration(trace: Trace) -> bool:
    return any(c.tool in ("find_references", "search_text") for c in trace.calls)
