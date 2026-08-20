#!/usr/bin/env python3
"""Controls for STEP 5 (#117): the cross-cutting injection clause.

Covers the half of STEP 5's done-when checkable without a real model run: the
clause is byte-identical across all three dimension definitions, and neither
the clause nor a full assembled PROMPT trips the deterministic detector (the
same use-mention trap CONTAINMENT.md and detect.py's own docstrings name).

The other half of STEP 5's done-when -- that the paraphrase fixture yields a
Blocker finding with the right entry_point from each of the three dimensions,
and the description-of-an-attack fixture yields none from any of them -- is a
property of REAL reviewer output, not of this clause's text. That is exactly
what STEP 8's recordings exist to prove; this file does not simulate it.

Run:  python3 -m unittest test_injection_clause    (from launchpad/review-agent/)
  or: python3 test_injection_clause.py
"""

from __future__ import annotations

import importlib.util
import os
import unittest

from detect import detect

HERE = os.path.dirname(os.path.abspath(__file__))
DIMENSION_SLUGS = ("secrets-and-access", "claim-vs-evidence", "correctness-and-failure-modes")


def _load_dimension(slug: str):
    path = os.path.join(HERE, "dimensions", f"{slug}.py")
    spec = importlib.util.spec_from_file_location(f"dim_{slug.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InjectionClauseByteIdentityTests(unittest.TestCase):
    def test_clause_is_byte_identical_across_all_three_dimension_files(self):
        clauses = {slug: _load_dimension(slug).INJECTION_CLAUSE for slug in DIMENSION_SLUGS}
        values = list(clauses.values())
        self.assertTrue(
            all(v == values[0] for v in values),
            f"clause text differs across dimensions: {clauses}",
        )

    def test_each_dimension_actually_embeds_the_clause_in_its_assembled_prompt(self):
        # Byte-identity of the standalone constant proves nothing if PROMPT never
        # includes it -- assembly is a separate failure mode from wording drift.
        for slug in DIMENSION_SLUGS:
            with self.subTest(slug=slug):
                module = _load_dimension(slug)
                self.assertIn(module.INJECTION_CLAUSE.strip(), module.PROMPT)


class InjectionClauseAvoidsTheUseMentionTrapTests(unittest.TestCase):
    """Sanity precondition, per STEP 5's own done-when reasoning: a clause that
    itself trips the deterministic detector would be indistinguishable from the
    attack it describes -- the exact failure mode CONTAINMENT.md's Detection
    section and detect.py's docstring both warn against.
    """

    def test_the_clause_text_alone_produces_no_deterministic_finding(self):
        for slug in DIMENSION_SLUGS:
            with self.subTest(slug=slug):
                clause = _load_dimension(slug).INJECTION_CLAUSE
                self.assertEqual(detect(clause, "pr_body"), [])

    def test_the_full_assembled_prompt_produces_no_deterministic_finding(self):
        # The clause could be individually clean yet combine with surrounding
        # prompt text to form a matching sentence once concatenated -- checked
        # against the real, fully-assembled PROMPT string, not just the isolated
        # constant.
        for slug in DIMENSION_SLUGS:
            with self.subTest(slug=slug):
                prompt = _load_dimension(slug).PROMPT
                self.assertEqual(detect(prompt, "pr_body"), [])


if __name__ == "__main__":
    unittest.main()
