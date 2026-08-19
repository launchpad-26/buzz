"""Controls for indexer.py's pure data transforms -- issue #206.

Scoped to the functions that need no `rql` CLI (with_called_by, with_tests):
constructed Symbol fixtures in, transformed Symbols out. index_crate(),
enrich_git_ownership(), and with_documentation_links() shell out to `rql` or
read real repo files and are verified against the live repo instead (see the
PR body and commit messages for #206) -- a fixture-based unit test for those
would either mock `rql` (testing the mock, not the behaviour) or require a
live index, neither of which belongs in a fast, hermetic suite.

Run:  python3 -m unittest test_indexer    (from launchpad/project-intelligence/)
  or: python3 test_indexer.py
"""

from __future__ import annotations

import unittest

from indexer import with_called_by, with_tests
from symbol import DefinedAt, Symbol


def _sym(qualified_name: str, calls: tuple[str, ...] = ()) -> Symbol:
    return Symbol(
        symbol_id=f"file:///f.rs#symbol={qualified_name}",
        kind="function",
        qualified_name=qualified_name,
        defined_at=DefinedAt("f.rs", 1, 2, "WORKING"),
        signature=f"fn {qualified_name}()",
        calls=calls,
    )


class WithCalledByTest(unittest.TestCase):
    def test_resolves_calls_to_qualified_names_when_indexed(self) -> None:
        caller = _sym("caller", calls=("callee",))
        callee = _sym("callee")
        result = {s.qualified_name: s for s in with_called_by([caller, callee])}

        self.assertEqual(result["caller"].calls, ("callee",))
        self.assertEqual(result["callee"].called_by, ("caller",))

    def test_unresolved_call_keeps_bare_short_name(self) -> None:
        # "contains" is not itself an indexed symbol (e.g. a std-lib method) --
        # nothing to resolve it to, so it is kept as-is rather than dropped.
        caller = _sym("caller", calls=("contains",))
        result = {s.qualified_name: s for s in with_called_by([caller])}

        self.assertEqual(result["caller"].calls, ("contains",))

    def test_short_name_collision_attaches_caller_to_every_candidate(self) -> None:
        # Documented, accepted limitation (see with_called_by's docstring):
        # two symbols sharing a short name both receive the same caller.
        caller = _sym("mod_a::run", calls=("run",))
        target_1 = _sym("mod_b::run")
        target_2 = _sym("mod_c::run")
        result = {s.qualified_name: s for s in with_called_by([caller, target_1, target_2])}

        self.assertIn("mod_a::run", result["mod_b::run"].called_by)
        self.assertIn("mod_a::run", result["mod_c::run"].called_by)

    def test_called_by_is_deduplicated(self) -> None:
        # Two distinct call sites to the same target must not double-count.
        caller = _sym("caller", calls=("callee", "callee"))
        callee = _sym("callee")
        result = {s.qualified_name: s for s in with_called_by([caller, callee])}

        self.assertEqual(result["callee"].called_by, ("caller",))

    def test_a_symbol_never_calls_itself(self) -> None:
        recursive = _sym("recursive", calls=("recursive",))
        result = {s.qualified_name: s for s in with_called_by([recursive])}

        self.assertEqual(result["recursive"].called_by, ())


class WithTestsTest(unittest.TestCase):
    def test_test_like_caller_is_classified_as_a_test(self) -> None:
        target = _sym("is_shared_gated_kind")
        test_caller = _sym("tests::shared_gated_kinds_membership", calls=("is_shared_gated_kind",))
        result = {s.qualified_name: s for s in with_tests(with_called_by([test_caller, target]))}

        self.assertEqual(result["is_shared_gated_kind"].tests, ("tests::shared_gated_kinds_membership",))

    def test_non_test_caller_is_not_classified_as_a_test(self) -> None:
        target = _sym("is_shared_gated_kind")
        real_caller = _sym("is_unshared_gated_event", calls=("is_shared_gated_kind",))
        result = {s.qualified_name: s for s in with_tests(with_called_by([real_caller, target]))}

        self.assertEqual(result["is_shared_gated_kind"].tests, ())
        self.assertIn("is_unshared_gated_event", result["is_shared_gated_kind"].called_by)


if __name__ == "__main__":
    unittest.main()
