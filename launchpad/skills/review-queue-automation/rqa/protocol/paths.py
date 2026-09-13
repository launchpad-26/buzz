"""`matches()` — the sole PathGlob matcher in RQA (`CONTRACTS.md` §2, `P-04-protocol.md` §2).

`PathGlob` grammar: `*` matches any run of non-`/` characters; `**` matches zero or
more complete segments; `?` matches exactly one non-`/` character. Patterns are
anchored at the repository root, matching is case-sensitive, and a leading `.` is an
ordinary character — this is not gitignore semantics.

Both `path` and `pattern` must already be normalized repository-relative strings:
non-empty, relative, `/`-separated, free of `\\`, empty segments, `.`/`..` segments,
and free of `**` except as a complete segment. Invalid input always raises
`PathGlobError`; no invalid-input branch ever returns a plausible Boolean.

`matches` is deliberately positional — `CONTRACTS.md` §2 fixes it as
`def matches(path: str, pattern: str) -> bool: ...`, the one documented exception to
every other function in this package being keyword-only.

P-03, P-06, P-10 and P-13 import and call `rqa.protocol.paths.matches` directly; they
must not use `fnmatch`, `PurePath.match`, a regex matcher, or their own glob
implementation, and neither does this module — matching is a plain iterative
wildcard match within one segment, and an iterative indexed DP across segments;
neither is a translation to a regular expression, and neither recurses.
"""

from __future__ import annotations


class PathGlobError(Exception):
    """A path or pattern is outside the normalized PathGlob grammar."""


def _segments(value: str, *, what: str) -> tuple[str, ...]:
    if not value:
        raise PathGlobError(f"{what} must not be empty")
    if value.startswith("/"):
        raise PathGlobError(f"{what} {value!r} is absolute")
    if value.startswith("./"):
        raise PathGlobError(f"{what} {value!r} begins with './'")
    if "\\" in value:
        raise PathGlobError(f"{what} {value!r} contains a backslash")
    segments = tuple(value.split("/"))
    for segment in segments:
        if segment == "":
            raise PathGlobError(f"{what} {value!r} has an empty segment")
        if segment in (".", ".."):
            raise PathGlobError(f"{what} {value!r} has a {segment!r} segment")
        if segment != "**" and "**" in segment:
            raise PathGlobError(f"{what} {value!r} has '**' outside a complete segment")
    return segments


def _match_segment(text: str, pattern: str) -> bool:
    """Plain iterative wildcard match: `*` any run, `?` exactly one character."""
    ti = pi = 0
    star_pi = -1
    star_ti = 0
    while ti < len(text):
        if pi < len(pattern) and (pattern[pi] == "?" or pattern[pi] == text[ti]):
            ti += 1
            pi += 1
        elif pi < len(pattern) and pattern[pi] == "*":
            star_pi = pi
            star_ti = ti
            pi += 1
        elif star_pi != -1:
            pi = star_pi + 1
            star_ti += 1
            ti = star_ti
        else:
            return False
    while pi < len(pattern) and pattern[pi] == "*":
        pi += 1
    return pi == len(pattern)


def _match_segments(path_segments: tuple[str, ...], pattern_segments: tuple[str, ...]) -> bool:
    """Iterative indexed DP over (path index, pattern index) — never recursive.

    A naive recursive walk over consecutive `**` groups re-explores the same
    (path index, pattern index) state exponentially many times, and Python's own
    recursion depth caps out on a long segment chain even without any `**` at all.
    `dp[i][j]` is `True` exactly when `path_segments[i:]` matches
    `pattern_segments[j:]`; every cell is computed once, bottom-up, so both the time
    and the call-stack depth are bounded by `len(path_segments) * len(pattern_segments)`.
    """
    path_count = len(path_segments)
    pattern_count = len(pattern_segments)
    dp = [[False] * (pattern_count + 1) for _ in range(path_count + 1)]
    dp[path_count][pattern_count] = True
    for j in range(pattern_count - 1, -1, -1):
        dp[path_count][j] = pattern_segments[j] == "**" and dp[path_count][j + 1]
    for i in range(path_count - 1, -1, -1):
        for j in range(pattern_count - 1, -1, -1):
            head = pattern_segments[j]
            if head == "**":
                dp[i][j] = dp[i][j + 1] or dp[i + 1][j]
            else:
                dp[i][j] = _match_segment(path_segments[i], head) and dp[i + 1][j + 1]
    return dp[0][0]


def matches(path: str, pattern: str) -> bool:
    """`True` when the normalized repository-relative `path` matches `pattern`.

    Raises `PathGlobError` for any input outside the normalized PathGlob grammar —
    never returns a Boolean for invalid input.
    """
    path_segments = _segments(path, what="path")
    pattern_segments = _segments(pattern, what="pattern")
    return _match_segments(path_segments, pattern_segments)
