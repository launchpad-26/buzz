"""Untrusted-text neutralisation and normalised JSON rendering for every `rqa`
subcommand.

**The threat.** `status` and `explain` render content that reached RQA from an
attacker-controlled pull request — titles, labels, branch names, finding
text, verdict/decision prose, escalation questions and their free-form
context — and `pending` renders an escalation's `question`/`context`, which
`P-11-escalation.md` §3 guards only for non-blankness (RQA-FR-026 is unmet
work, tracked at #2260, and left alone here per this lane's instructions). A
terminal is not a safe sink: a raw ANSI escape, a carriage return or a
backspace embedded in that text can repaint what the operator believes they
are reading.

**The neutralisation.** `sanitize_text` replaces C0/C1 controls, Unicode line
separators and bidi directives with visible Unicode escapes. Text remains legible
and distinct instead of losing line boundaries. It runs recursively on every
string leaf; it is not a general defence against visual impersonation or Unicode
confusables. JSON encoding adds the transport escaping around those visible
sequences, so decoding JSON never activates a terminal control.

Output is one JSON object per invocation, `sort_keys=True` for a stable diff,
written to stdout. Nothing here decides an exit code; that mapping is
`rqa/cli/main.py`'s own, and it is the only place except `sanitize` itself
that reads a provider's return value at all.
"""

from __future__ import annotations

import dataclasses
import json
import re
import sys
from collections.abc import Mapping
from enum import Enum
from typing import Any

__all__ = ["sanitize_text", "to_jsonable", "emit"]

#: Every C0 control character (`\x00`-`\x1f`), DEL (`\x7f`) and every C1
#: control character (`\x80`-`\x9f`) — the whole class of bytes that can carry
#: an ANSI/CSI escape sequence (`\x1b[...`), a carriage return, a line feed
#: mid-field, a backspace or a bell. Printable text keeps every other
#: codepoint untouched, including non-ASCII letters.
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f\u061c\u200e\u200f\u2028-\u202e\u2066-\u2069]")


def sanitize_text(value: str) -> str:
    """`value` with controls rendered as visible Unicode escapes. Idempotent, and a no-op
    on text that never carried one."""
    return _CONTROL_CHARACTERS.sub(lambda match: f"\\u{ord(match.group()):04x}", value)


def to_jsonable(value: Any) -> Any:
    """`value` as plain JSON-safe data, with every string leaf sanitised.

    Handles the shapes every provider result is built from: frozen
    dataclasses (`StatusReport`, `Explanation`, `Escalation`, `Decision`,
    `TickResult`, `Written`, `OnboardRefusal`, ...), `Enum` members (rendered
    as their `.value`), mappings, sequences, `bytes` (never emitted — no
    provider result carries one to the CLI boundary; a defensive `repr` marks
    it rather than raising if one ever did), and primitives.
    """
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, Enum):
        return to_jsonable(value.value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, Mapping):
        return {sanitize_text(str(key)): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, bytes):
        return sanitize_text(repr(value))
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    # A value with no shape rule above (a rendered timestamp, a Path, ...):
    # its str() may still carry PR-derived bytes, so it is sanitised too.
    return sanitize_text(str(value))


def emit(payload: dict[str, Any]) -> None:
    """The one write to stdout every subcommand makes: recursively normalise
    and sanitise the whole `payload`, then write one sorted-key JSON object."""
    json.dump(to_jsonable(payload), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
