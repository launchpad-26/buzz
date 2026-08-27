"""Locate and parse fenced ```verdict blocks inside one PR comment's raw text.

Implements launchpad-26/buzz#287 STEPs 2 and 3. See ADJUDICATION.md's
"PR comment verdict blocks: refusing more than one (#287)" section for the
Option-B rule this module is a building block of, and `verdict_resolution.py`
for the rule itself (STEP 5).

STEP 2 — ``locate_verdict_blocks``. This module reuses
``launchpad/scripts/pr_body_check.py``'s ``FENCE_OPEN``/``FENCE_CLOSE``
run-length-matching regexes for the fence boundary itself (CommonMark's rule
that a closing fence must be at least as long as the one that opened it, and
must close with the same character) — that matching logic is correct here
unchanged. What is NOT reused is `_strip_fences`'s blockquote disposition:
`_strip_fences` strips a `> ` prefix *before* matching, on purpose, so a fence
someone quoted is recognised as real (its docstring: "Without that, quoting
someone else's fenced output left its contents standing as prose"). This
module's job is the opposite — a PR comment quoting someone else's
` ```verdict ` block must NOT have that block treated as this commenter's
own verdict — so a fence line matching `BLOCKQUOTE` disqualifies that fence
from the returned list, without changing anything about how the underlying
run-length matching works. `_strip_fences` also only captures the backtick or
tilde run, never what follows it on the same line, so it cannot tell a
` ```verdict ` fence from a ` ```python ` one; this module captures that info
string and only ever returns blocks whose info string is the exact word
``verdict``.

STEP 3 — ``parse_rows``. Mirrors `review-gate.sh`'s `cmd_verdict`: a row
needs 4 or more tab-separated fields, with everything from field 4 onward
rejoined as the description (a description containing a literal tab is legal
on the emitter side, per that script's own `cut -f4-`). ``verdict`` is
checked against ``verdicts.VERDICTS`` and ``severity`` against
``review.SEVERITY_ORDER`` — both imported, never redeclared, for the same
reason `verdicts.py` itself gives for importing `SEVERITY_ORDER` rather than
re-declaring it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from review import SEVERITY_ORDER
from verdicts import VERDICTS

#: Same pattern as `pr_body_check.BLOCKQUOTE` — a run of one or more `>` markers,
#: each optionally preceded by up to 3 spaces, with one optional trailing space.
BLOCKQUOTE = re.compile(r"^(?: {0,3}>)+ ?")

#: Unlike `pr_body_check.FENCE_OPEN`, this captures group 2: everything after the
#: backtick/tilde run on the opening line, so the info string (`verdict`, `python`,
#: or nothing) can be told apart. CommonMark's own indentation limit (0-3 leading
#: spaces) is unchanged, so a 4-space-indented fence still never matches.
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

#: Identical to `pr_body_check.FENCE_CLOSE` — a closing fence carries nothing but
#: its run and trailing whitespace.
FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")

#: The one info string this locator returns blocks for. Case-sensitive and exact:
#: `` ```verdicts `` or `` ```verdict-old `` are unrelated fences, not this one.
_VERDICT_INFO = "verdict"


@dataclass
class LocatedBlock:
    """One ` ```verdict ` fence found in a comment body, 1-indexed line numbers."""

    start_line: int
    end_line: int | None  # None when the fence never closes (runs to EOF)
    closed: bool
    info: str
    raw_rows: str  # the raw text between the fence lines; "" if none


def locate_verdict_blocks(text: str) -> list[LocatedBlock]:
    """Every top-level ` ```verdict ` fence in ``text``, closed or not.

    A fence opened inside a blockquote is tracked (so its extent is understood
    correctly, the same way `pr_body_check._strip_fences` tracks it) but is
    NEVER returned, regardless of its info string or closed state — that is
    the "disqualify" disposition STEP 2 requires, the mirror image of
    `_strip_fences` recognising it. A fence opened outside a blockquote whose
    info string is not exactly ``verdict`` is tracked the same way and also
    never returned — it is a real fence, just not this one.
    """
    blocks: list[LocatedBlock] = []
    lines = text.splitlines()

    fence_char: str | None = None
    fence_len = 0
    fence_in_quote = False
    start_line = 0
    info = ""
    row_lines: list[str] = []

    def flush(end_line: int | None, closed: bool) -> None:
        if fence_in_quote:
            return
        if info.strip() != _VERDICT_INFO:
            return
        blocks.append(
            LocatedBlock(start_line, end_line, closed, info.strip(), "\n".join(row_lines))
        )

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        lineno = i + 1

        if fence_char is not None:
            if fence_in_quote and not BLOCKQUOTE.match(line):
                # CommonMark ends a block quote lazily: a line with no `>` marker
                # closes it, and a fence opened inside keeps no memory of the
                # container it opened in — it closes with the quote, unclosed.
                flush(None, False)
                fence_char = None
                fence_in_quote = False
                continue  # re-evaluate this same line fresh, below
            probe = BLOCKQUOTE.sub("", line) if fence_in_quote else line
            closer = FENCE_CLOSE.match(probe)
            if closer and closer.group(1)[0] == fence_char and len(closer.group(1)) >= fence_len:
                flush(lineno, True)
                fence_char = None
                fence_in_quote = False
                i += 1
                continue
            row_lines.append(line)
            i += 1
            continue

        quoted = bool(BLOCKQUOTE.match(line))
        probe = BLOCKQUOTE.sub("", line) if quoted else line
        m = FENCE_OPEN.match(probe)
        if m:
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            info = m.group(2)
            fence_in_quote = quoted
            start_line = lineno
            row_lines = []
        i += 1

    if fence_char is not None:
        flush(None, False)

    return blocks


@dataclass
class ParsedRow:
    verdict: str
    severity: str
    location: str
    description: str


@dataclass
class MalformedRow:
    raw: str
    reason: str


def parse_rows(raw_rows: str) -> list[ParsedRow | MalformedRow]:
    """Parse a located block's raw row text into ``ParsedRow``/``MalformedRow``.

    A blank line between rows is skipped, not flagged malformed — the same
    disposition `review-gate.sh`'s `cmd_verdict` gives it (`[ -z "$row" ] &&
    continue`).
    """
    results: list[ParsedRow | MalformedRow] = []
    for line in raw_rows.split("\n"):
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < 4:
            results.append(
                MalformedRow(
                    raw=line,
                    reason=f"{len(fields)} tab-separated field(s), need 4 or more: {line}",
                )
            )
            continue
        verdict, severity, location = fields[0], fields[1], fields[2]
        description = "\t".join(fields[3:])
        if verdict not in VERDICTS:
            results.append(
                MalformedRow(
                    raw=line,
                    reason=f"verdict {verdict!r} not in {sorted(VERDICTS)}: {line}",
                )
            )
            continue
        if severity not in SEVERITY_ORDER:
            results.append(
                MalformedRow(
                    raw=line,
                    reason=f"severity {severity!r} not in {sorted(SEVERITY_ORDER)}: {line}",
                )
            )
            continue
        results.append(ParsedRow(verdict, severity, location, description))
    return results
