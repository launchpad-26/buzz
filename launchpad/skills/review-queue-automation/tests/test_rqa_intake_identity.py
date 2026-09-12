#!/usr/bin/env python3
"""`rqa.intake.identity` — `code/P-01-intake.md` §1 (U-RESILIENCE-13).

`stable_hash`/`job_id` are the one hashing mechanism this part owns; P-09's
`rqa.github.writes` resolves them at call time and falls back to the same
formula while this package was unlanded (§1). Now that it is landed, both
paths must be byte-identical — that fallback is dead code from this point on,
never a second definition.
"""

from __future__ import annotations

import hashlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.intake.identity import job_id, stable_hash  # noqa: E402


def test_stable_hash_matches_the_fixed_formula() -> None:
    parts = ("alice/repo", "42", "deadbeef")
    expected = hashlib.sha256("\x1f".join(parts).encode()).hexdigest()
    assert stable_hash(*parts) == expected


def test_stable_hash_is_deterministic() -> None:
    assert stable_hash("a", "b", "c") == stable_hash("a", "b", "c")


def test_stable_hash_distinguishes_different_splits_of_the_same_joined_text() -> None:
    """The unit-separator join means `("ab", "c")` and `("a", "bc")` hash
    differently even though a naive `"".join()` would collide them."""
    assert stable_hash("ab", "c") != stable_hash("a", "bc")


def test_stable_hash_accepts_variadic_positional_parts() -> None:
    assert stable_hash("only-one-part") == hashlib.sha256("only-one-part".encode()).hexdigest()
    assert stable_hash() == hashlib.sha256(b"").hexdigest()


def test_job_id_is_stable_hash_of_repo_str_number_and_head_sha() -> None:
    """`CONTRACTS.md` §1: `Job.id  # stable_hash(repo, number, head_sha)`."""
    assert job_id("alice/repo", 42, "deadbeef") == stable_hash("alice/repo", "42", "deadbeef")


def test_job_id_accepts_the_exact_positional_call_site_p01_section3_uses() -> None:
    """§3 step 2c calls it as `job_id(repo, pf.number, pf.head_sha)` —
    positional, never by keyword."""
    assert job_id("alice/repo", 42, "deadbeef") == job_id(*("alice/repo", 42, "deadbeef"))


def test_job_id_is_sensitive_to_every_argument() -> None:
    base = job_id("alice/repo", 1, "sha-a")
    assert job_id("bob/repo", 1, "sha-a") != base
    assert job_id("alice/repo", 2, "sha-a") != base
    assert job_id("alice/repo", 1, "sha-b") != base


def test_github_writes_fallback_is_now_byte_identical_with_this_module() -> None:
    """`rqa.github.writes._stable_hash` resolves `rqa.intake.identity` at call
    time (never at import) and falls back only while this package is
    unlanded. Now that it exists, every call must take this path and produce
    the identical digest its dead fallback would also have produced."""
    from rqa.github.writes import _stable_hash

    assert _stable_hash("job-1", "approve", "{}") == stable_hash("job-1", "approve", "{}")
