"""Controls for symbol.py -- issue #206, STEP 1's done-when.

Constructs one Symbol by hand and asserts every field the design doc's schema
names, so a future change to the dataclass shape fails a real test rather than
being noticed later by a caller.

Run:  python3 -m unittest test_symbol    (from launchpad/project-intelligence/)
  or: python3 test_symbol.py
"""

from __future__ import annotations

import unittest

from symbol import DefinedAt, GitOwnership, Symbol


class SymbolFieldsTest(unittest.TestCase):
    def test_every_schema_field_is_settable_and_readable(self) -> None:
        sym = Symbol(
            symbol_id="file:///crates/buzz-core/src/kind.rs#symbol=is_shared_gated_kind",
            kind="function",
            qualified_name="is_shared_gated_kind",
            defined_at=DefinedAt(
                file="crates/buzz-core/src/kind.rs",
                start_line=219,
                end_line=221,
                temporal_state="WORKING",
            ),
            signature="pub fn is_shared_gated_kind(kind: u32) -> bool",
            calls=("SOME_CONST_CHECK",),
            called_by=("event_is_shared",),
            tests=("tests::is_shared_gated_kind_true_for_39000",),
            config_dependencies=(),
            documentation_links=("launchpad/AGENTS.md#kind-registry",),
            git_ownership=GitOwnership(
                primary_authors=("alice",),
                history=("f4e1c9 add moderation-kind gating",),
            ),
        )

        self.assertEqual(sym.kind, "function")
        self.assertEqual(sym.qualified_name, "is_shared_gated_kind")
        self.assertEqual(sym.defined_at.file, "crates/buzz-core/src/kind.rs")
        self.assertEqual(sym.defined_at.start_line, 219)
        self.assertEqual(sym.defined_at.end_line, 221)
        self.assertEqual(sym.defined_at.temporal_state, "WORKING")
        self.assertEqual(sym.signature, "pub fn is_shared_gated_kind(kind: u32) -> bool")
        self.assertEqual(sym.calls, ("SOME_CONST_CHECK",))
        self.assertEqual(sym.called_by, ("event_is_shared",))
        self.assertEqual(sym.tests, ("tests::is_shared_gated_kind_true_for_39000",))
        self.assertEqual(sym.config_dependencies, ())
        self.assertEqual(sym.documentation_links, ("launchpad/AGENTS.md#kind-registry",))
        self.assertEqual(sym.git_ownership.primary_authors, ("alice",))
        self.assertEqual(sym.git_ownership.history, ("f4e1c9 add moderation-kind gating",))

    def test_defaults_are_empty_not_none(self) -> None:
        sym = Symbol(
            symbol_id="x",
            kind="function",
            qualified_name="x",
            defined_at=DefinedAt("f.rs", 1, 2, "WORKING"),
            signature="fn x()",
        )
        self.assertEqual(sym.calls, ())
        self.assertEqual(sym.called_by, ())
        self.assertEqual(sym.tests, ())
        self.assertEqual(sym.config_dependencies, ())
        self.assertEqual(sym.documentation_links, ())
        self.assertEqual(sym.git_ownership, GitOwnership())


if __name__ == "__main__":
    unittest.main()
