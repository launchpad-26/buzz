"""Decision logic stage 3 -- issue #211, STEP 7.

"Investigate when not confident": the design doc's § Decision logic progression,
run in order, stopping as soon as the evidence is sufficient.

  locate (search_symbols) -> read (read_file) -> callers (find_references)
    -> tests (search_text) -> history (inspect_git_history)

**The stop rule, stated because it is the one real judgement in this task and
the design doc does not specify it mechanically:**

  * Locate and read ALWAYS run. Without them there is nothing to answer from,
    so "sufficient" cannot be true before them.
  * Callers runs whenever there is a symbol target.
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

# The canonical order. The trace must be a subsequence of this.
PROGRESSION = ("search_symbols", "read_file", "find_references", "search_text", "inspect_git_history")

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

    @property
    def located(self) -> bool:
        return self.match is not None and self.definition_line is not None

    @property
    def corroborated(self) -> bool:
        """Something other than the definition itself points at this symbol."""
        return bool(self.callers) or bool(self.test_sites)

    @property
    def sufficient(self) -> bool:
        return self.located and self.corroborated

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
    for i, line in enumerate(lines, start=1):
        if signature and signature in line:
            findings.definition_line = i
            break
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
    text = tools.read_file(file)  # type: ignore[union-attr]
    marker_line = next(
        (i for i, line in enumerate(text.splitlines(), start=1) if TEST_MODULE_MARKER in line), None
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


# The history stage queries a window, not the single definition line.
#
# Measured, not assumed: investigator.inspect_git_history on
# crates/buzz-core/src/kind.rs returns 0 commits for the range (850, 850) and 4
# commits for (840, 860), while `git log -L 850,850:...` names a real commit for
# that exact line. A degenerate start == end range comes back empty from #208's
# tool. That is #208's defect and is filed rather than patched here -- the plan's
# LEFT OUT reserves #206-#210's own logic to their own issues.
#
# What IS this task's to fix is the call site: asking with start == end meant the
# history stage was silently returning nothing every time. The citation reports
# the window actually queried, never the single line, because a claim must cite
# what was really asked.
HISTORY_LINE_WINDOW = 10


def _history(findings: Findings, trace: Trace, tools: Tools) -> None:
    match = findings.match
    line = findings.definition_line or 1
    start, end = line, line + HISTORY_LINE_WINDOW
    commits = tools.inspect_git_history(match.file, start, end)  # type: ignore[union-attr]
    findings.history = list(commits)
    trace.record(
        "inspect_git_history",
        f"{match.file}:{start}-{end}",  # type: ignore[union-attr]
        found=bool(commits),
        detail=(
            f"{len(commits)} commit(s)" if commits else "no commits touching that range"
        ),
    )


def investigate(
    question: Question,
    crate: str,
    trace: Trace,
    tools: Tools = REAL_TOOLS,
) -> Findings:
    if question.target is None:
        raise ValueError("investigate() needs a named target; a nameless question is FIND's case")

    findings = Findings(target=question.target)
    _locate(question.target, crate, findings, trace, tools)
    if findings.match is None:
        return findings

    _read(findings, trace, tools)
    _callers(question.target, crate, findings, trace, tools)

    if not findings.corroborated:
        _tests(question.target, findings, trace, tools)

    wants_history = question.temporal_state == "HISTORY" or question.depth == "RATIONALE"
    if wants_history and findings.located:
        _history(findings, trace, tools)

    return findings
