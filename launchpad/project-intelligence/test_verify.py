"""Controls for verify.py and trace.py -- issue #211.

Reads real repo files through investigator.read_file, which is deterministic and
needs no `rql` and no `cargo` -- the same boundary test_investigator.py already
works within. Nothing here shells out.

Run:  python3 -m unittest test_verify
  or: python3 test_verify.py
"""

from __future__ import annotations

import unittest

import investigator
from memory import MemoryEntry, ProjectMemory
from trace import Trace
from verify import UNCONFIRMED_CONFIDENCE, confirm_text_at, verified_fact

# The real symbol this task's live demo uses, and its real location.
REAL_PATH = "crates/buzz-core/src/kind.rs"
REAL_START, REAL_END = 219, 221
REAL_SIGNATURE = "pub fn is_shared_gated_kind(kind: u32) -> bool"


class FixtureDriftTest(unittest.TestCase):
    """Several suites here hardcode this real symbol's current line numbers.

    review-tests flagged that as an undeclared coupling to a file outside this
    change's control. It fails loudly rather than silently, and this test names
    the cause.

    It does NOT run first, and an earlier version of this docstring claimed it
    did. Adjudication measured the real discovery order: `unittest discover`
    sorts modules alphabetically, so test_assemble's dependent test runs at
    position 62 of 269 while this guard runs at 308. Fixing that properly means
    hoisting the shared fixture constants into one module with a setUpModule
    hook -- worth doing, not done here, and recorded rather than implied.

    The affected modules, measured by simulating a 5-line drift rather than
    assumed: test_verify.py, test_assemble.py and test_worked_trace.py fail.
    test_knowledge_agent.py does NOT -- it hardcodes the range only in a
    synthetic DefinedAt that no test reads from disk. The earlier message named
    that file and omitted test_worked_trace.py, pointing a maintainer at the one
    module that was fine and away from one that was broken.
    """

    def test_the_hardcoded_range_still_holds_the_symbol_the_fixtures_assume(self) -> None:
        text = investigator.read_file(REAL_PATH, REAL_START, REAL_END)
        self.assertIn(
            REAL_SIGNATURE,
            text,
            f"{REAL_PATH}:{REAL_START}-{REAL_END} no longer contains {REAL_SIGNATURE!r}. "
            "The fixtures in test_verify.py, test_assemble.py and test_worked_trace.py "
            "read this range from disk; update them together rather than one at a time. "
            "(test_knowledge_agent.py hardcodes the same numbers but never reads the file, "
            "so it will not fail here.)",
        )


class TraceTest(unittest.TestCase):
    def test_side_effect_class_comes_from_the_registry_not_the_caller(self) -> None:
        """A caller that could label its own call READ_ONLY could run a test
        suite and record it as a read."""
        trace = Trace()
        trace.record("read_file", "x", found=True, detail="")
        trace.record("run_test", "buzz-core", found=True, detail="")
        self.assertEqual(trace.calls[0].side_effect, "READ_ONLY")
        self.assertEqual(trace.calls[1].side_effect, "EXECUTE")

    def test_an_unknown_tool_is_rejected(self) -> None:
        """The trace must not be able to claim a tool the Investigator has no
        such thing as -- that would be evidence of a call nobody could make."""
        with self.assertRaises(ValueError):
            Trace().record("summon_answer", "x", found=True, detail="")

    def test_tool_order_is_preserved_including_repeats(self) -> None:
        trace = Trace()
        for tool in ("search_symbols", "read_file", "read_file", "find_references"):
            trace.record(tool, "x", found=True, detail="")
        self.assertEqual(
            trace.tools, ("search_symbols", "read_file", "read_file", "find_references")
        )

    def test_side_effecting_calls_are_separately_reportable(self) -> None:
        trace = Trace()
        trace.record("read_file", "x", found=True, detail="")
        self.assertEqual(trace.side_effecting, ())
        trace.record("run_command", "echo hi", found=True, detail="")
        self.assertEqual(len(trace.side_effecting), 1)

    def test_an_empty_trace_renders_as_no_investigation(self) -> None:
        self.assertEqual(Trace().render(), "(no investigation performed)")


class ConfirmTextAtTest(unittest.TestCase):
    def test_a_real_citation_that_supports_its_claim_confirms(self) -> None:
        trace = Trace()
        self.assertTrue(
            confirm_text_at(REAL_PATH, REAL_START, REAL_END, REAL_SIGNATURE, trace)
        )
        self.assertEqual(trace.tools, ("read_file",))
        self.assertTrue(trace.calls[0].found)

    def test_a_citation_that_resolves_but_does_not_support_its_claim_fails(self) -> None:
        """The STEP 3 defect, as a permanent control: kind.rs:219-221 exists and
        reads fine, but it does not contain the test that a claim about tests
        would need. A check that only asked "does the path exist" passes this."""
        trace = Trace()
        self.assertFalse(
            confirm_text_at(REAL_PATH, REAL_START, REAL_END, "fn shared_gated_kinds_membership", trace)
        )
        self.assertIn("does not contain", trace.calls[0].detail)

    def test_an_unreadable_path_records_a_failure_rather_than_raising(self) -> None:
        trace = Trace()
        self.assertFalse(confirm_text_at("no/such/file.rs", 1, 2, "anything", trace))
        self.assertEqual(len(trace.calls), 1)
        self.assertFalse(trace.calls[0].found)


class VerifiedFactTest(unittest.TestCase):
    def test_a_confirmed_claim_is_a_fact_citing_the_range_it_read(self) -> None:
        trace = Trace()
        claim = verified_fact(
            "is_shared_gated_kind returns a bool",
            REAL_SIGNATURE,
            REAL_PATH,
            REAL_START,
            REAL_END,
            trace,
        )
        self.assertEqual(claim.entry_class, "FACT")
        self.assertEqual(claim.evidence, (f"{REAL_PATH}:{REAL_START}-{REAL_END}",))

    def test_an_unconfirmed_claim_is_never_a_fact(self) -> None:
        """STEP 6's second done-when, asserted on entry_class."""
        trace = Trace()
        claim = verified_fact(
            "is_shared_gated_kind writes to the database",
            "db.execute",
            REAL_PATH,
            REAL_START,
            REAL_END,
            trace,
        )
        self.assertEqual(claim.entry_class, "INFERENCE")
        self.assertEqual(claim.confidence, UNCONFIRMED_CONFIDENCE)
        self.assertIn("unconfirmed", claim.evidence[0])

    def test_cached_agreement_does_not_skip_the_live_call(self) -> None:
        """STEP 6's first done-when. ProjectMemory already agreeing changes
        nothing: memory records what was true when it was written, so the
        read_file must still appear in the trace."""
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="m1",
                entry_class="FACT",
                statement="is_shared_gated_kind returns a bool",
                evidence=(f"{REAL_PATH}:{REAL_START}-{REAL_END}",),
            )
        )
        self.assertEqual(len(memory.query_by_class("FACT")), 1)

        trace = Trace()
        claim = verified_fact(
            "is_shared_gated_kind returns a bool",
            REAL_SIGNATURE,
            REAL_PATH,
            REAL_START,
            REAL_END,
            trace,
        )
        self.assertEqual(claim.entry_class, "FACT")
        self.assertEqual(trace.tools, ("read_file",))

    def test_verification_never_reaches_a_side_effecting_tool(self) -> None:
        trace = Trace()
        verified_fact("x is y", REAL_SIGNATURE, REAL_PATH, REAL_START, REAL_END, trace)
        self.assertEqual(trace.side_effecting, ())

    def test_a_claim_is_downgraded_never_dropped(self) -> None:
        """A dropped claim leaves the answer quietly shorter, and a reader
        cannot tell "nothing to say" from "could not confirm what I was going
        to say"."""
        trace = Trace()
        claim = verified_fact("unsupportable", "not-in-that-range", REAL_PATH, REAL_START, REAL_END, trace)
        self.assertIsNotNone(claim)
        self.assertEqual(claim.statement, "unsupportable")


if __name__ == "__main__":
    unittest.main()
