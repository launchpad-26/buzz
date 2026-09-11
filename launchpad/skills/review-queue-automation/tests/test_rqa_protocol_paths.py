#!/usr/bin/env python3
"""Tests for `rqa.protocol.paths.matches` (`P-04-protocol.md` §2) — T26, T27.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.
`matches` is the one deliberately positional signature in this package; every call
below uses positional arguments to prove that form works.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.protocol import paths  # noqa: E402

# -- T26: every valid row of §2's path conformance table -----------------------
CONFORMANCE_TABLE = (
    ("README.md", "README.md", True),  # root
    ("src/a/main.py", "src/*/main.py", True),  # nested
    ("src/a/main.py", "src/*.py", False),  # '*' does not cross a separator
    ("src/main.py", "src/**/main.py", True),  # zero-segment '**'
    ("src/a/b/main.py", "src/**/main.py", True),  # nested '**'
    (".github/workflows/ci.yml", ".github/**/*.yml", True),  # dotfile
    ("src/a.py", "src/?.py", True),  # question mark
    ("src/a/b.py", "src/?.py", False),  # question mark does not cross a separator
    ("src/main.py", "SRC/main.py", False),  # separator and case
)


def test_conformance_table_root() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[0]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_nested() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[1]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_star_does_not_cross_separator() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[2]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_zero_segment_double_star() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[3]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_nested_double_star() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[4]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_dotfile() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[5]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_question_mark() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[6]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_question_mark_does_not_cross_separator() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[7]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_separator_and_case() -> None:
    path, pattern, expected = CONFORMANCE_TABLE[8]
    assert paths.matches(path, pattern) is expected


def test_conformance_table_every_row_matches_stated_boolean() -> None:
    for path, pattern, expected in CONFORMANCE_TABLE:
        assert paths.matches(path, pattern) is expected, (path, pattern, expected)


def test_triple_star_across_three_segments() -> None:
    assert paths.matches("a/b/c/leaf.py", "a/**/leaf.py") is True


def test_double_star_matches_deeply_nested_segments() -> None:
    assert paths.matches("a/b/c/d/e/leaf.py", "**/leaf.py") is True


def test_bare_double_star_matches_everything() -> None:
    assert paths.matches("a/b/c.py", "**") is True
    assert paths.matches("a.py", "**") is True


# -- Regressions: F-PATHS-BACKTRACKING, F-PATHS-RECURSION-LIMIT ----------------
# A naive recursive walk over consecutive '**' groups re-explores the same
# (path index, pattern index) state exponentially many times, and a non-tail
# recursive segment walk blows Python's own recursion limit on a long chain even
# with zero wildcards. `matches()` must return a plain Boolean, in time and stack
# depth bounded by len(path) * len(pattern), for any grammar-valid input — never
# take unbounded time and never raise `RecursionError`.
def test_many_consecutive_double_stars_resolve_quickly_on_a_non_matching_path() -> None:
    import time

    pattern = "a/" + "**/" * 6 + "b"
    path = "a/" + "/".join(f"seg{i}" for i in range(40)) + "/not-b"
    started = time.perf_counter()
    result = paths.matches(path, pattern)
    elapsed = time.perf_counter() - started
    assert result is False
    assert elapsed < 5.0, f"multi-'**' matching took {elapsed:.3f}s — expected sub-second"


def test_a_very_deep_literal_path_does_not_raise_recursion_error() -> None:
    segments = [f"seg{i}" for i in range(1500)]
    path = "/".join(segments) + "/leaf.py"
    pattern = path  # exact literal match, no wildcards at all
    assert paths.matches(path, pattern) is True


def test_a_very_deep_path_with_a_double_star_does_not_raise_recursion_error() -> None:
    segments = [f"seg{i}" for i in range(1500)]
    path = "root/" + "/".join(segments) + "/leaf.py"
    assert paths.matches(path, "root/**/leaf.py") is True


def test_a_very_deep_non_matching_path_does_not_raise_recursion_error() -> None:
    segments = [f"seg{i}" for i in range(1500)]
    path = "/".join(segments) + "/leaf.py"
    pattern = "/".join(segments) + "/other.py"
    assert paths.matches(path, pattern) is False


# -- T27: each invalid PathGlob input raises PathGlobError, never a Boolean ----
def _assert_raises_path_glob_error(path: str, pattern: str) -> None:
    try:
        paths.matches(path, pattern)
    except paths.PathGlobError:
        return
    raise AssertionError(f"expected PathGlobError for matches({path!r}, {pattern!r})")


def test_empty_path_raises() -> None:
    _assert_raises_path_glob_error("", "a.py")


def test_empty_pattern_raises() -> None:
    _assert_raises_path_glob_error("a.py", "")


def test_absolute_path_raises() -> None:
    _assert_raises_path_glob_error("/a.py", "a.py")


def test_absolute_pattern_raises() -> None:
    _assert_raises_path_glob_error("a.py", "/a.py")


def test_leading_dot_slash_raises() -> None:
    _assert_raises_path_glob_error("./a.py", "a.py")


def test_backslash_raises() -> None:
    _assert_raises_path_glob_error("a\\b.py", "a\\b.py")


def test_empty_segment_raises() -> None:
    _assert_raises_path_glob_error("a//b.py", "a/b.py")


def test_dot_segment_raises() -> None:
    _assert_raises_path_glob_error("a/./b.py", "a/b.py")


def test_dot_dot_segment_raises() -> None:
    _assert_raises_path_glob_error("a/../b.py", "a/b.py")


def test_bare_dot_raises() -> None:
    _assert_raises_path_glob_error(".", "a.py")


def test_bare_dot_dot_raises() -> None:
    _assert_raises_path_glob_error("..", "a.py")


def test_double_star_not_a_complete_segment_raises() -> None:
    _assert_raises_path_glob_error("a.py", "a**b/c.py")
    _assert_raises_path_glob_error("a.py", "**b/c.py")
    _assert_raises_path_glob_error("a.py", "a**/c.py")


def test_no_invalid_branch_returns_a_boolean() -> None:
    invalid_pairs = (
        ("", "a"),
        ("a", ""),
        ("/a", "a"),
        ("a", "/a"),
        ("./a", "a"),
        ("a\\b", "a"),
        ("a//b", "a/b"),
        ("a/.", "a"),
        ("a/..", "a"),
        (".", "a"),
        ("..", "a"),
        ("a", "a**b"),
    )
    for path, pattern in invalid_pairs:
        try:
            result = paths.matches(path, pattern)
        except paths.PathGlobError:
            continue
        raise AssertionError(
            f"matches({path!r}, {pattern!r}) returned {result!r} instead of raising"
        )


def test_path_glob_error_is_a_real_exception_type() -> None:
    assert issubclass(paths.PathGlobError, Exception)
