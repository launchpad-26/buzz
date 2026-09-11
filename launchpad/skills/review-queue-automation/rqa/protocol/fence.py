"""`strip_fence()` — markdown-fence normalisation (U-VERDICT-01, kept).

Several harnesses reliably emit an otherwise-correct verdict inside a ```json fence.
Removing that wrapper is a formatting normalisation, not a relaxation: the entire
stripped text must be one fence — an opening ``` (with an optional language tag)
immediately followed by a newline, content, a newline, and a closing ``` with
nothing else before or after — or it is left exactly as it was. Prose around a
fence, two consecutive fences, or an unclosed fence are never partially repaired;
they fall through unstripped to a JSON-decode failure downstream, so a verdict can
never be extracted out of surrounding prose.
"""

from __future__ import annotations

import re

#: Matches ONE markdown fence that wraps the ENTIRE payload. Anchored at both ends
#: on purpose: if any prose sits outside the fence the match fails and the payload
#: is returned unstripped.
_FULL_PAYLOAD_FENCE = re.compile(
    r"\A```[ \t]*[A-Za-z0-9_+.-]*[ \t]*\r?\n(?P<body>.*?)\r?\n?[ \t]*```\Z",
    re.DOTALL,
)


def strip_fence(*, text: str) -> str:
    """Strip one markdown fence when it wraps the whole payload, else return as-is.

    "Wraps the whole payload" means exactly one fence boundary: the anchored
    `\\A...\\Z` match alone is not sufficient proof, since it spans from the first
    opening ``` to the *last* closing ``` in the text — for two adjacent (or
    prose-separated) fences that still matches, splicing both bodies together with
    the fences in between left in as literal text.

    A fence marker is a structural token only when it begins a physical line — that
    is exactly what the opening/closing grammar this same pattern requires means.
    JSON forbids a literal newline inside a string, so a backtick sequence embedded
    in valid JSON content (for example a `Finding.evidence` string quoting a fenced
    code excerpt) is always mid-line in the serialized text, never line-initial,
    and must still be stripped normally. A body containing a *line-initial* ```
    sequence, by contrast, is a genuine second fence boundary, so the payload is
    not a single fence and is left exactly as it was.
    """
    if not text:
        return ""
    stripped = text.strip()
    match = _FULL_PAYLOAD_FENCE.match(stripped)
    if match is None:
        return stripped
    body = match.group("body")
    if body.startswith("```") or "\n```" in body:
        return stripped
    return body.strip()
