"""Controls for investigation.py -- issue #211.

Hermetic: the stop rule and the call order, driven through the Tools seam with
recorded stand-ins. The live run against real buzz-core data is STEP 10's
worked trace, evidenced in the PR body -- three of these five tools shell out to
`rql`, which the fast suite must not need.

Run:  python3 -m unittest test_investigation
  or: python3 test_investigation.py
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from investigation import HISTORY_LINE_WINDOW, PROGRESSION, Tools, investigate
from question import decompose
from trace import Trace


@dataclass(frozen=True)
class _Match:
    qualified_name: str
    kind: str
    file: str
    signature: str


@dataclass(frozen=True)
class _Ref:
    caller_qualified_name: str
    file: str
    line: int


@dataclass(frozen=True)
class _TextMatch:
    file: str
    line: int
    text: str


FILE = "crates/buzz-core/src/kind.rs"
SIGNATURE = "pub fn is_shared_gated_kind(kind: u32) -> bool"
FILE_TEXT = "\n".join(
    ["// header"] * 5
    + [SIGNATURE, "    SHARED_GATED_KINDS.contains(&kind)", "}"]
    + ["// filler"] * 3
    + ["mod tests {", "    fn membership() { is_shared_gated_kind(1); }", "}"]
)
MATCH = _Match("is_shared_gated_kind", "function", FILE, SIGNATURE)


def _tools(
    matches: list | None = None,
    refs: list | None = None,
    text_hits: list | None = None,
    commits: list | None = None,
    file_text: str = FILE_TEXT,
) -> Tools:
    return Tools(
        search_symbols=lambda name, crate: list(matches if matches is not None else [MATCH]),
        read_file=lambda path, *a, **k: file_text,
        find_references=lambda qn, crate: list(refs if refs is not None else []),
        search_text=lambda pattern, **k: list(text_hits if text_hits is not None else []),
        inspect_git_history=lambda f, s, e: list(commits if commits is not None else []),
    )


def _is_subsequence(candidate: tuple[str, ...], of: tuple[str, ...]) -> bool:
    it = iter(of)
    return all(item in it for item in candidate)


class CallOrderTest(unittest.TestCase):
    """STEP 7's done-when. The trace is a subsequence of PROGRESSION, in order.

    Asserted as a subsequence rather than a fixed list on purpose: the stop rule
    skips stages, and a fixed-list assertion cannot tell a legitimate skip from
    an out-of-order regression. Subsequence catches the second and permits the
    first, which is exactly the distinction that matters.
    """

    def test_recorded_calls_are_an_ordered_subsequence_of_the_progression(self) -> None:
        trace = Trace()
        investigate(decompose("how does `is_shared_gated_kind` work?"), "buzz-core", trace, _tools())
        # The non-emptiness check is not padding. review-tests demonstrated that
        # the subsequence assertion ALONE passes on a total no-op: () is a
        # subsequence of anything, so an investigate() that returned immediately
        # with zero tool calls satisfied it. Its siblings in this class caught
        # that mutation, but this test read in isolation was a tautology.
        self.assertTrue(trace.tools, "investigate() recorded no tool calls at all")
        self.assertTrue(
            _is_subsequence(trace.tools, PROGRESSION),
            f"{trace.tools} is not an ordered subsequence of {PROGRESSION}",
        )

    def test_all_five_stages_fire_in_order_when_every_one_is_warranted(self) -> None:
        """An uncorroborated historical question reaches every stage, so the
        full progression is provably reachable and not just permitted."""
        trace = Trace()
        investigate(
            decompose("why does `is_shared_gated_kind` exist?"),
            "buzz-core",
            trace,
            _tools(text_hits=[_TextMatch(FILE, 12, "is_shared_gated_kind(1)")]),
        )
        self.assertEqual(trace.tools, PROGRESSION)

    def test_a_side_effecting_tool_is_never_reached(self) -> None:
        trace = Trace()
        investigate(decompose("why does `is_shared_gated_kind` exist?"), "buzz-core", trace, _tools())
        self.assertEqual(trace.side_effecting, ())


class StopRuleTest(unittest.TestCase):
    def test_corroborated_callers_skip_the_tests_stage(self) -> None:
        """Tests is the second attempt at corroboration. Once callers
        corroborate, repeating it is a slower answer and a longer trace."""
        trace = Trace()
        investigate(
            decompose("how does `is_shared_gated_kind` work?"),
            "buzz-core",
            trace,
            _tools(refs=[_Ref("is_unshared_gated_event", FILE, 240)]),
        )
        self.assertNotIn("search_text", trace.tools)

    def test_no_callers_reaches_the_tests_stage(self) -> None:
        trace = Trace()
        investigate(decompose("how does `is_shared_gated_kind` work?"), "buzz-core", trace, _tools())
        self.assertIn("search_text", trace.tools)

    def test_history_runs_only_for_a_historical_question(self) -> None:
        present = Trace()
        investigate(decompose("how does `is_shared_gated_kind` work?"), "buzz-core", present, _tools())
        self.assertNotIn("inspect_git_history", present.tools)

        historical = Trace()
        investigate(decompose("how did `is_shared_gated_kind` evolve?"), "buzz-core", historical, _tools())
        self.assertIn("inspect_git_history", historical.tools)

    def test_history_runs_even_when_the_evidence_is_already_sufficient(self) -> None:
        """History answers a different question rather than corroborating this
        one, so sufficiency must not suppress it."""
        trace = Trace()
        findings = investigate(
            decompose("how did `is_shared_gated_kind` evolve?"),
            "buzz-core",
            trace,
            _tools(refs=[_Ref("is_unshared_gated_event", FILE, 240)]),
        )
        self.assertTrue(findings.sufficient)
        self.assertIn("inspect_git_history", trace.tools)

    def test_history_is_queried_over_a_window_never_a_single_line(self) -> None:
        """Measured against the real tool: inspect_git_history returns 0 commits
        for (850, 850) and 4 for (840, 860) on kind.rs, while `git log -L
        850,850` names a real commit. A degenerate range comes back empty, so a
        single-line query made this stage silently useless."""
        seen: list[tuple[int, int]] = []
        tools = _tools()
        tools = Tools(
            search_symbols=tools.search_symbols,
            read_file=tools.read_file,
            find_references=tools.find_references,
            search_text=tools.search_text,
            inspect_git_history=lambda f, s, e: seen.append((s, e)) or [],
        )
        trace = Trace()
        investigate(decompose("how did `is_shared_gated_kind` evolve?"), "buzz-core", trace, tools)
        self.assertEqual(len(seen), 1)
        start, end = seen[0]
        self.assertGreater(end, start, "a degenerate start == end range returns nothing")
        self.assertEqual(end - start, HISTORY_LINE_WINDOW)

    def test_the_history_citation_reports_the_range_actually_queried(self) -> None:
        """A claim must cite what was really asked, not the line it was about."""
        trace = Trace()
        investigate(decompose("how did `is_shared_gated_kind` evolve?"), "buzz-core", trace, _tools())
        call = next(c for c in trace.calls if c.tool == "inspect_git_history")
        self.assertIn(f"{6}-{6 + HISTORY_LINE_WINDOW}", call.args)

    def test_a_symbol_that_does_not_exist_stops_after_locating(self) -> None:
        """Nothing downstream has a subject, so continuing would query for a
        symbol the index says is not there."""
        trace = Trace()
        findings = investigate(
            decompose("how does `no_such_symbol` work?"), "buzz-core", trace, _tools(matches=[])
        )
        self.assertEqual(trace.tools, ("search_symbols",))
        self.assertFalse(findings.located)
        self.assertFalse(findings.sufficient)


class FindingsTest(unittest.TestCase):
    def test_the_definition_line_is_found_by_reading_not_assumed(self) -> None:
        trace = Trace()
        findings = investigate(
            decompose("how does `is_shared_gated_kind` work?"), "buzz-core", trace, _tools()
        )
        self.assertEqual(findings.definition_line, 6)
        self.assertEqual(findings.citation(), f"{FILE}:6")

    def test_a_signature_absent_from_the_file_reports_not_located(self) -> None:
        trace = Trace()
        findings = investigate(
            decompose("how does `is_shared_gated_kind` work?"),
            "buzz-core",
            trace,
            _tools(file_text="nothing relevant here"),
        )
        self.assertIsNone(findings.definition_line)
        self.assertFalse(findings.located)
        self.assertIsNone(findings.citation())

    def test_mentions_above_the_test_marker_are_not_counted_as_tests(self) -> None:
        """A mention in the definition itself, or in a doc comment above it, is
        not a test corroborating anything."""
        trace = Trace()
        findings = investigate(
            decompose("how does `is_shared_gated_kind` work?"),
            "buzz-core",
            trace,
            _tools(text_hits=[_TextMatch(FILE, 6, SIGNATURE)]),
        )
        self.assertEqual(findings.test_sites, [])
        self.assertFalse(findings.corroborated)

    def test_a_file_with_no_test_module_claims_no_test_sites(self) -> None:
        trace = Trace()
        findings = investigate(
            decompose("how does `is_shared_gated_kind` work?"),
            "buzz-core",
            trace,
            _tools(
                file_text="\n".join(["// header"] * 5 + [SIGNATURE]),
                text_hits=[_TextMatch(FILE, 6, SIGNATURE)],
            ),
        )
        self.assertEqual(findings.test_sites, [])

    def test_a_nameless_question_is_rejected_rather_than_guessed_at(self) -> None:
        with self.assertRaises(ValueError):
            investigate(
                decompose("where is the code that checks kind gating?"), "buzz-core", Trace(), _tools()
            )


if __name__ == "__main__":
    unittest.main()
