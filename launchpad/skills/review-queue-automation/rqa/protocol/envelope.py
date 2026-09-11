"""The nonce-envelope grammar: `envelope()`, `extract()` (U-RESILIENCE-15's format).

Stateless string functions defining the grammar only. P-04 does not enforce
nonce-envelope use at runtime and never touches PR content (§7): applying this
grammar to every PR-derived byte in a bundle is P-06's mechanism, under
RQA-NFR-015, not something this module calls or checks.

`envelope()` wraps `content` between an opening `<<<label:nonce>>>` marker and a
matching closing `<<<END:label:nonce>>>` marker. `extract()` recovers the exact
original bytes only when given the same `label` and `nonce` the envelope was built
with; a wrong nonce (or label) never recovers them — it returns `None`, a value, not
an exception, since failing to find a matching envelope is not a programming error.
"""

from __future__ import annotations


def envelope(*, label: str, nonce: str, content: str) -> str:
    """Wrap `content` in a per-run nonce-bound envelope keyed by `label`/`nonce`."""
    return f"<<<{label}:{nonce}>>>\n{content}\n<<<END:{label}:{nonce}>>>"


def extract(*, text: str, label: str, nonce: str) -> str | None:
    """Recover the exact content of the `label`/`nonce` envelope in `text`, or `None`.

    Returns `None` when no envelope keyed by exactly this `label` and `nonce` is
    present — including when `text` was built with a different nonce. The closing
    marker is located from the *end* of `text` backwards: if `content` itself
    happens to contain a substring that looks like this exact closing marker, the
    genuine closing tag `envelope()` appended is still the last such occurrence in
    the text, so the full original content is recovered rather than truncated at
    the embedded look-alike.
    """
    open_marker = f"<<<{label}:{nonce}>>>\n"
    close_marker = f"\n<<<END:{label}:{nonce}>>>"
    start = text.find(open_marker)
    if start == -1:
        return None
    start += len(open_marker)
    end = text.rfind(close_marker)
    if end == -1 or end < start:
        return None
    return text[start:end]
