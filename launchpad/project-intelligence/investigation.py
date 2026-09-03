"""Decision logic stage 3 -- issue #211, STEP 7.

"Investigate when not confident": the design doc's § Decision logic progression,
run in order, stopping as soon as the evidence is sufficient.

  locate (search_symbols) -> read (read_file) -> callers (find_references)
    -> tests (search_text) -> history (inspect_git_history)

**The stop rule, stated because it is the one real judgement in this task and
the design doc does not specify it mechanically:**

  * Locate and read ALWAYS run. Without them there is nothing to answer from,
    so no amount of cached confidence can skip them.
  * Callers runs whenever there is a symbol target AND stage 1 found no prior
    stored answer -- see `confident` in investigate()'s own docstring below.
    (This line said "whenever there is a symbol target" until 2026-08-24, which
    contradicted investigate() two hundred lines below it once the confidence
    gate landed. Adjudication caught it: a module header denying a gate that
    exists is the same defect as the docstring that claimed a gate that didn't.)
  * Tests runs only if callers found no corroboration. It is the second attempt
    at the same thing, so corroborated evidence makes it redundant -- and a
    redundant call is not free, it is a slower answer and a longer trace for a
    reader to audit.
  * History runs only when the question is historical (temporal_state HISTORY,
    or depth RATIONALE). It answers a different question rather than
    corroborating this one, so sufficiency does not govern it either way.

A consequence to be honest about: because stages can be skipped, the trace is a
SUBSEQUENCE of the progression above, not always all five calls. That is the
intended behaviour of a stop rule, and the test asserts subsequence-and-order
rather than a fixed list -- which also catches an out-of-order regression that a
fixed-list assertion would not distinguish from a skip.

`run_command` and `run_test` are never reached. Nothing here needs runtime
confirmation, and the design doc gates those on "genuinely needed".

The Tools seam exists so the stop rule is testable without a RepoQL index:
every stage but read_file and search_text shells out to `rql`. STEP 12 requires
a hermetic suite and a live demo, so the seam serves both rather than being
speculative generality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import investigator
from question import Question
from trace import Trace

# The canonical TOOL-CALL order. The trace must be a subsequence of this.
#
# Note the second `read_file`: the tests stage makes two calls, one to locate the
# `mod tests` boundary and one to search below it. That read used to be absent
# from both this constant and the trace, which made the trace under-report. It is
# listed here rather than hidden because this constant's whole job is to be the
# truth the trace is checked against -- a canonical order that omits a call the
# code makes is the same class of lie as the trace that omitted it.
PROGRESSION = (
    "search_symbols",
    "read_file",
    "find_references",
    "read_file",
    "search_text",
    "inspect_git_history",
)

TEST_MODULE_MARKER = "mod tests"


@dataclass(frozen=True)
class Tools:
    search_symbols: Callable
    read_file: Callable
    find_references: Callable
    search_text: Callable
    inspect_git_history: Callable


REAL_TOOLS = Tools(
    search_symbols=investigator.search_symbols,
    read_file=investigator.read_file,
    find_references=investigator.find_references,
    search_text=investigator.search_text,
    inspect_git_history=investigator.inspect_git_history,
)


@dataclass
class Findings:
    target: str
    match: object | None = None
    definition_line: int | None = None
    callers: list = field(default_factory=list)
    test_sites: list = field(default_factory=list)
    history: list = field(default_factory=list)
    # Files of every candidate when a name resolved to more than one symbol.
    # Empty is the normal case; non-empty means an answer describes ONE of
    # several same-named symbols and must say so.
    ambiguous: tuple = ()

    @property
    def located(self) -> bool:
        return self.match is not None and self.definition_line is not None

    @property
    def corroborated(self) -> bool:
        """Something other than the definition itself points at this symbol.

        Read directly by the stop rule below and by assemble(). Note what it
        does NOT mean since the confidence gate landed: False can mean "looked
        and found nothing" OR "never looked, because a prior answer existed".
        Any caller inferring an absence from it must first check the trace for a
        find_references/search_text call -- assemble() does exactly that.
        """
        return bool(self.callers) or bool(self.test_sites)

    # `sufficient` (located and corroborated) was removed on 2026-08-24.
    # Adjudication found it had no production reader at all -- the stop rule
    # reads `corroborated` directly -- and that it had become actively
    # misleading: it reported False for is_unshared_gated_event, a symbol with
    # eight real callers, because the confidence gate had SKIPPED corroboration
    # rather than failed to find it. Dead code that misreports is worse than no
    # code, so it is gone rather than documented.

    def citation(self) -> str | None:
        if not self.located:
            return None
        return f"{self.match.file}:{self.definition_line}"  # type: ignore[union-attr]


def _locate(target: str, crate: str, findings: Findings, trace: Trace, tools: Tools) -> None:
    matches = tools.search_symbols(target, crate)
    trace.record(
        "search_symbols",
        f"{target!r}, crate={crate!r}",
        found=bool(matches),
        detail=f"{len(matches)} match(es)" if matches else "no symbol of that name in the crate",
    )
    if matches:
        findings.match = matches[0]
        # A collision is DISCLOSED, not silently resolved. Taking matches[0]
        # when several symbols share a name produces the worst citation shape
        # this layer can emit: a real file:line for the wrong subject. The code
        # guards against that shape elsewhere (exact qualified_name matching in
        # find_symbol, the "not a prefix match" test), and this path quietly
        # did the opposite. Found by the review panel.
        #
        # Still resolved to the first match rather than refusing -- refusing
        # would answer nothing for a legitimately overloaded name. But the trace
        # now records that a choice was made, so an auditor sees it.
        if len(matches) > 1:
            findings.ambiguous = tuple(
                getattr(m, "file", "?") for m in matches
            )
            trace.record(
                "search_symbols",
                f"{target!r} resolved to {getattr(matches[0], 'file', '?')} of "
                f"{len(matches)} candidates",
                found=True,
                detail="AMBIGUOUS: several symbols share this name; the first was used",
            )


def _read(findings: Findings, trace: Trace, tools: Tools) -> None:
    """Reads the whole defining file and locates the signature's line.

    search_symbols returns no line range (SymbolMatch carries file and
    signature only), so the line is found by reading rather than assumed. That
    is also why the line is reported at all: a claim needs a citation a reader
    can open, and file-without-line is not one.
    """
    match = findings.match
    text = tools.read_file(match.file)  # type: ignore[union-attr]
    lines = text.splitlines()
    signature = match.signature.strip()  # type: ignore[union-attr]
    # Prefer a line that STARTS with the signature (after indentation) over one
    # that merely contains it. A signature quoted inside a doc comment --
    # `/// calls pub fn foo(...)` -- would otherwise be pinned as the
    # definition, and then verification would confirm the claim against the
    # comment. That is the wrong-subject failure the verify stage exists to
    # catch, defeated by the locate stage handing it the wrong line. Found by
    # the review panel.
    #
    # Falls back to a containment match so a formatting the strict rule does not
    # anticipate still locates something, rather than reporting the symbol
    # missing.
    contained_at = None
    for i, line in enumerate(lines, start=1):
        if not signature:
            break
        stripped = line.strip()
        if stripped.startswith(signature):
            findings.definition_line = i
            break
        if contained_at is None and signature in line:
            contained_at = i
    if findings.definition_line is None and contained_at is not None:
        findings.definition_line = contained_at
    trace.record(
        "read_file",
        match.file,  # type: ignore[union-attr]
        found=findings.definition_line is not None,
        detail=(
            f"signature found at line {findings.definition_line}"
            if findings.definition_line is not None
            else f"signature {signature!r} not present in the file"
        ),
    )


def _callers(target: str, crate: str, findings: Findings, trace: Trace, tools: Tools) -> None:
    refs = tools.find_references(target, crate)
    findings.callers = list(refs)
    trace.record(
        "find_references",
        f"{target!r}, crate={crate!r}",
        found=bool(refs),
        detail=f"{len(refs)} caller(s)" if refs else "no callers in this crate",
    )


def _tests(target: str, findings: Findings, trace: Trace, tools: Tools) -> None:
    """Mentions of the symbol below the file's own `mod tests` marker.

    Rust keeps unit tests in the same file, so a test reference is a textual
    mention positioned after that marker -- and it yields a real file:line a
    reader can open, which a graph edge naming a test symbol does not.
    """
    match = findings.match
    file = match.file  # type: ignore[union-attr]
    # This read is RECORDED. It was not until 2026-08-24: the trace claimed to
    # hold every Investigator call and quietly omitted this one, so injected
    # tools counted two reads while the trace showed one. A trace that
    # under-reports is worse than no trace -- it is an audit log that lies by
    # omission, in the one artefact built to make the reasoning inspectable.
    text = tools.read_file(file)  # type: ignore[union-attr]
    marker_line = next(
        (i for i, line in enumerate(text.splitlines(), start=1) if TEST_MODULE_MARKER in line), None
    )
    trace.record(
        "read_file",
        f"{file} (locating the {TEST_MODULE_MARKER!r} boundary)",
        found=marker_line is not None,
        detail=(
            f"test module starts at line {marker_line}"
            if marker_line is not None
            else f"no {TEST_MODULE_MARKER!r} in the file"
        ),
    )
    matches = [m for m in tools.search_text(target, glob=file.rsplit("/", 1)[-1]) if m.file == file]
    if marker_line is not None:
        matches = [m for m in matches if m.line > marker_line]
    else:
        # No test module in the file: a mention cannot be classified as a test
        # site, so none is claimed. Reporting zero is honest; guessing is not.
        matches = []
    findings.test_sites = matches
    trace.record(
        "search_text",
        f"{target!r} below {TEST_MODULE_MARKER!r} in {file}",
        found=bool(matches),
        detail=(
            f"{len(matches)} test-side mention(s), first at line {matches[0].line}"
            if matches
            else "no mention below a test-module marker"
        ),
    )


# The history stage queries the exact definition line.
#
# Was a 10-line window instead, worked around here rather than fixed here: #569
# measured investigator.inspect_git_history on crates/buzz-core/src/kind.rs
# returning 0 commits for the degenerate range (850, 850) and 4 for (840, 860),
# while `git log -L 850,850:...` names a real commit for that exact line. #208's
# tool has since been fixed to call `git log -L` directly instead of RepoQL's
# `=> history` modifier, and a single-line range now returns the same commits
# `git log -L N,N:file` reports -- see investigator.py's inspect_git_history()
# and its InspectGitHistoryTest coverage. The workaround is removed rather than
# widened, per #569's own instruction: querying a window wider than the claim it
# supports made every history citation broader than what was actually asked.
def _history(findings: Findings, trace: Trace, tools: Tools) -> None:
    match = findings.match
    line = findings.definition_line or 1
    commits = tools.inspect_git_history(match.file, line, line)  # type: ignore[union-attr]
    findings.history = list(commits)
    trace.record(
        "inspect_git_history",
        f"{match.file}:{line}-{line}",  # type: ignore[union-attr]
        found=bool(commits),
        detail=(
            f"{len(commits)} commit(s)" if commits else "no commits touching that line"
        ),
    )


def investigate(
    question: Question,
    crate: str,
    trace: Trace,
    tools: Tools = REAL_TOOLS,
    confident: bool = False,
) -> Findings:
    """`confident` is stage 1's verdict -- specifically, whether ProjectMemory
    holds a PRIOR ANSWER about the target (see confidence.Assessment.confident,
    which is not "some component has heard of it"). It gates the CORROBORATION
    stages only -- find_references and search_text.

    Decided 2026-08-24 after two independent reviewers found that stage 1's
    assessment was computed and then ignored, while this module's caller claimed
    in its own docstring that stage 3 was "skipped when already confident". The
    gate now exists, and its shape follows the design doc rather than that
    sentence:

      * locate and read are NEVER skipped. Nothing in ProjectGraph,
        SemanticIndex or ProjectMemory supplies a citable file:line, so skipping
        them would produce an answer with no citation -- which is the one thing
        this layer must never do. This is also § Reasoning Rules point 2: "at
        least one live Investigator call before answering, even if cached
        knowledge already agrees."
      * find_references and search_text ARE skipped when confident. They exist
        to corroborate, and a stored FACT or a graph edge is the cached
        corroboration that made stage 1 confident in the first place.
      * history is NOT gated by confidence, despite the first draft of this
        decision saying it would be. History is the CONTENT of a historical
        question, not corroboration of a present-tense one -- gating it would
        make knowledge.history() return no commits for any target stage 1
        happened to feel confident about. It stays governed by the question.
    """
    if question.target is None:
        raise ValueError("investigate() needs a named target; a nameless question is FIND's case")

    findings = Findings(target=question.target)
    _locate(question.target, crate, findings, trace, tools)
    if findings.match is None:
        return findings

    _read(findings, trace, tools)

    if not confident:
        _callers(question.target, crate, findings, trace, tools)
        if not findings.corroborated:
            _tests(question.target, findings, trace, tools)

    wants_history = question.temporal_state == "HISTORY" or question.depth == "RATIONALE"
    if wants_history and findings.located:
        _history(findings, trace, tools)

    return findings
