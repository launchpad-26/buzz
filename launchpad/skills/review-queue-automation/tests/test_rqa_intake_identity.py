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


def test_github_writes_uses_this_modules_canonical_stable_hash() -> None:
    """The assembled tree has one stable-hash owner and no compatibility fallback.

    `rqa.github.writes` resolves the owner at call time because `rqa.intake`
    imports `rqa.github`, so a module-level import there would close a cycle.
    Redirecting this module's `stable_hash` must therefore change what
    `writes._stable_hash` returns: a private copy of the formula would not
    follow, and that is the defect this asserts against.
    """
    import unittest.mock

    from rqa.github import writes

    assert writes._stable_hash("a", "b") == stable_hash("a", "b")
    assert not hasattr(writes, "hashlib"), "writes must hold no hashing implementation"
    with unittest.mock.patch(
        "rqa.intake.identity.stable_hash", return_value="redirected"
    ):
        assert writes._stable_hash("a", "b") == "redirected"
