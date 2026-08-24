"""Controls for assemble.py -- issue #211.

Hermetic. Findings are constructed directly, and the one live read that
verify.verified_fact performs targets a real repo file (deterministic, no `rql`,
no `cargo`) -- the same boundary test_verify.py works within.

Run:  python3 -m unittest test_assemble
  or: python3 test_assemble.py
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from assemble import APPEARS_UNUSED_CONFIDENCE, COMMIT_INTENT_CONFIDENCE, assemble
from investigation import Findings
from memory import MemoryEntry, ProjectMemory
from question import decompose
from trace import Trace

REAL_FILE = "crates/buzz-core/src/kind.rs"
REAL_LINE = 219
REAL_SIGNATURE = "pub fn is_shared_gated_kind(kind: u32) -> bool"
TARGET = "is_shared_gated_kind"


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
class _Commit:
    hash: str
    date: str
    author: str
    message: str


def _findings(**overrides: object) -> Findings:
    findings = Findings(target=TARGET)
    findings.match = _Match(TARGET, "function", REAL_FILE, REAL_SIGNATURE)
    findings.definition_line = REAL_LINE
    for key, value in overrides.items():
        setattr(findings, key, value)
    return findings


class ProvenanceTest(unittest.TestCase):
    """STEP 8's done-when."""

    def test_every_claim_carries_a_provenance_class(self) -> None:
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), ProjectMemory()
        )
        self.assertTrue(answer.claims)
        for claim in answer.claims:
            with self.subTest(claim=claim.statement):
                self.assertIn(claim.entry_class, ("FACT", "INFERENCE", "TEAM_KNOWLEDGE"))

    def test_an_inference_names_the_real_artefact_it_came_from(self) -> None:
        answer = assemble(
            decompose(f"how did `{TARGET}` evolve?"),
            _findings(history=[_Commit("f4e1c9", "2026-01-01", "alice", "add idempotency key check")]),
            Trace(),
            ProjectMemory(),
        )
        inferences = answer.claims_of_class("INFERENCE")
        self.assertTrue(inferences)
        from_commit = [c for c in inferences if "f4e1c9" in " ".join(c.evidence)]
        self.assertTrue(from_commit, "no inference cites the commit it was drawn from")
        self.assertEqual(from_commit[0].confidence, COMMIT_INTENT_CONFIDENCE)

    def test_a_commit_message_inference_is_never_a_fact(self) -> None:
        """A message states intent, never a measured outcome -- the design
        doc's own worked example draws exactly this line."""
        answer = assemble(
            decompose(f"how did `{TARGET}` evolve?"),
            _findings(history=[_Commit("abc123", "2026-01-01", "alice", "add cache for perf")]),
            Trace(),
            ProjectMemory(),
        )
        for claim in answer.claims:
            if "abc123" in " ".join(claim.evidence):
                self.assertEqual(claim.entry_class, "INFERENCE")


class VerificationIsNotSkippedTest(unittest.TestCase):
    def test_the_definition_fact_is_re_confirmed_by_a_live_read(self) -> None:
        """Stage 3 read the file to LOCATE. Stage 2 re-reads the exact range to
        CONFIRM. Different questions, and only the second catches a citation
        that resolves without supporting its claim."""
        trace = Trace()
        answer = assemble(decompose(f"how does `{TARGET}` work?"), _findings(), trace, ProjectMemory())
        self.assertIn("read_file", trace.tools)
        definition = answer.claims[0]
        self.assertEqual(definition.entry_class, "FACT")
        self.assertEqual(definition.evidence, (f"{REAL_FILE}:{REAL_LINE}-{REAL_LINE}",))

    def test_a_wrong_definition_line_downgrades_rather_than_asserting(self) -> None:
        """The citation still resolves -- line 1 of kind.rs is a real line. It
        just does not contain the signature, so the claim must not be a FACT."""
        trace = Trace()
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"), _findings(definition_line=1), trace, ProjectMemory()
        )
        self.assertEqual(answer.claims[0].entry_class, "INFERENCE")
        self.assertIn("unconfirmed", answer.claims[0].evidence[0])


class TeamKnowledgeTest(unittest.TestCase):
    def test_team_knowledge_passes_through_verbatim_with_its_author(self) -> None:
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="tk1",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"we are not adding kinds near {TARGET} this milestone",
                provided_by="serina",
            )
        )
        answer = assemble(decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), memory)
        team = answer.claims_of_class("TEAM_KNOWLEDGE")
        self.assertEqual(len(team), 1)
        self.assertEqual(team[0].provided_by, "serina")
        self.assertIn("not adding kinds", team[0].statement)

    def test_team_knowledge_is_not_downgraded_for_lack_of_corroboration(self) -> None:
        """The design doc forbids the mere absence of corroborating code from
        overriding it -- it is the class that exists for exactly that case."""
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="tk2",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"{TARGET} is being replaced next quarter",
                provided_by="serina",
            )
        )
        answer = assemble(decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), memory)
        self.assertEqual(len(answer.claims_of_class("TEAM_KNOWLEDGE")), 1)

    def test_a_superseded_entry_is_not_surfaced_as_current(self) -> None:
        """Cross-model review reproduced Alice's "do not use" and Bob's
        superseding "approved for use" BOTH appearing as current TEAM_KNOWLEDGE,
        contradicting each other with no sign of which won. #209 built
        `superseded_by` for exactly this and nothing consumed it. A retracted
        statement presented as current is worse than one omitted -- the reader
        acts on guidance the team already withdrew."""
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="old",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"{TARGET}: do not use",
                provided_by="alice",
                superseded_by="new",
            )
        )
        memory.add(
            MemoryEntry(
                id="new",
                entry_class="TEAM_KNOWLEDGE",
                statement=f"{TARGET}: approved for use",
                provided_by="bob",
            )
        )
        answer = assemble(decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), memory)
        team = answer.claims_of_class("TEAM_KNOWLEDGE")
        self.assertEqual(len(team), 1)
        self.assertEqual(team[0].provided_by, "bob")
        self.assertNotIn("do not use", team[0].statement)

    def test_unrelated_team_knowledge_is_not_attached(self) -> None:
        memory = ProjectMemory()
        memory.add(
            MemoryEntry(
                id="tk3",
                entry_class="TEAM_KNOWLEDGE",
                statement="the desktop app is frozen this sprint",
                provided_by="serina",
            )
        )
        answer = assemble(decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), memory)
        self.assertEqual(answer.claims_of_class("TEAM_KNOWLEDGE"), ())


class UncorroboratedTest(unittest.TestCase):
    def test_appears_unused_is_an_inference_citing_both_failed_lookups(self) -> None:
        trace = Trace()
        trace.record("find_references", "x", found=False, detail="no callers in this crate")
        trace.record("search_text", "y", found=False, detail="no mention below a test-module marker")
        answer = assemble(decompose(f"how does `{TARGET}` work?"), _findings(), trace, ProjectMemory())
        unused = [c for c in answer.claims_of_class("INFERENCE") if "appears unused" in c.statement]
        self.assertEqual(len(unused), 1)
        self.assertEqual(unused[0].confidence, APPEARS_UNUSED_CONFIDENCE)
        self.assertEqual(len(unused[0].evidence), 2)

    def test_no_lookup_in_the_trace_makes_no_unused_claim_at_all(self) -> None:
        """If nothing looked, "appears unused" would be asserting absence of
        evidence as evidence of absence. Caught by running this step's tests:
        an empty trace built an INFERENCE with an empty evidence tuple, which
        Claim refused -- correctly."""
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), ProjectMemory()
        )
        self.assertEqual(
            [c for c in answer.claims_of_class("INFERENCE") if "appears unused" in c.statement], []
        )

    def test_corroborated_symbols_make_no_unused_claim(self) -> None:
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"),
            _findings(callers=[_Ref("is_unshared_gated_event", REAL_FILE, 240)]),
            Trace(),
            ProjectMemory(),
        )
        self.assertEqual(
            [c for c in answer.claims_of_class("INFERENCE") if "appears unused" in c.statement], []
        )


class CallerCountingTest(unittest.TestCase):
    """Four call sites in one test plus one real caller -- the exact shape the
    live run against kind.rs produced."""

    def _four_sites_two_callers(self) -> list:
        return [
            _Ref("tests::membership", REAL_FILE, 1077),
            _Ref("tests::membership", REAL_FILE, 1078),
            _Ref("tests::membership", REAL_FILE, 1082),
            _Ref("is_unshared_gated_event", REAL_FILE, 234),
        ]

    def test_callers_and_call_sites_are_counted_separately(self) -> None:
        """Reporting "4 caller(s)" and then naming two reads as two names having
        gone missing."""
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"),
            _findings(callers=self._four_sites_two_callers()),
            Trace(),
            ProjectMemory(),
        )
        caller_claim = next(c for c in answer.claims if "call site" in c.statement)
        self.assertIn("2 caller(s) across 4 call site(s)", caller_claim.statement)
        self.assertEqual(len(caller_claim.evidence), 4)

    def test_the_flow_is_deduped_by_caller(self) -> None:
        """The live run emitted the same arrow four times, which reads as four
        distinct callers."""
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"),
            _findings(callers=self._four_sites_two_callers()),
            Trace(),
            ProjectMemory(),
        )
        self.assertEqual(answer.relevant_flow.count(f"tests::membership -> {TARGET}"), 1)
        self.assertEqual(answer.relevant_flow.count(" | "), 1)


class CaveatsTest(unittest.TestCase):
    def test_the_caveats_section_restates_the_inferences(self) -> None:
        """Not an authored paragraph: an authored caveat can say something the
        claims do not support, and then Sources and Things-to-be-aware-of
        disagree about the same answer."""
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"),
            _findings(callers=[_Ref("is_unshared_gated_event", REAL_FILE, 234)]),
            Trace(),
            ProjectMemory(),
        )
        inferences = answer.claims_of_class("INFERENCE")
        self.assertTrue(inferences)
        for claim in inferences:
            self.assertIn(claim.statement, answer.things_to_be_aware_of)

    def test_the_caveats_section_is_populated_in_the_ordinary_case(self) -> None:
        """An earlier version emitted it only when history existed or nothing
        corroborated, so the common case rendered five of six sections."""
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"),
            _findings(callers=[_Ref("is_unshared_gated_event", REAL_FILE, 234)]),
            Trace(),
            ProjectMemory(),
        )
        self.assertTrue(answer.things_to_be_aware_of.strip())

    def test_every_caveat_line_carries_its_evidence(self) -> None:
        answer = assemble(
            decompose(f"how did `{TARGET}` evolve?"),
            _findings(history=[_Commit("f4e1c9", "2026-01-01", "alice", "widen the allowlist")]),
            Trace(),
            ProjectMemory(),
        )
        self.assertIn("f4e1c9", answer.things_to_be_aware_of)
        self.assertIn("INFERENCE", answer.things_to_be_aware_of)


class TemporalStateTest(unittest.TestCase):
    def test_a_base_question_says_it_was_answered_from_working(self) -> None:
        """BASE was classified by question.py and then ignored by everything
        downstream -- the third dead-classified-value defect in this branch. BASE
        reads are still not implemented (filed separately); what is fixed is the
        silence. The design doc: "don't silently answer from one state while the
        question implied the other"."""
        question = decompose(f"how did `{TARGET}` behave before my changes?")
        self.assertEqual(question.temporal_state, "BASE")
        answer = assemble(question, _findings(), Trace(), ProjectMemory())
        self.assertIn("asked about the repository BEFORE", answer.things_to_be_aware_of)
        self.assertIn("read from the WORKING tree", answer.things_to_be_aware_of)

    def test_a_working_question_carries_no_base_caveat(self) -> None:
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), ProjectMemory()
        )
        self.assertNotIn("asked about the repository BEFORE", answer.things_to_be_aware_of)


class InjectedReaderTest(unittest.TestCase):
    def test_verification_reads_through_the_injected_reader(self) -> None:
        """The seam was split: investigation used agent.tools while verification
        called the process-global investigator, so a test driving an injected
        repository had its claim confirmed against the real worktree instead --
        silently downgrading a claim the injected data supported."""
        seen: list[str] = []

        def reader(path, start=None, end=None):
            seen.append(path)
            return REAL_SIGNATURE

        answer = assemble(
            decompose(f"how does `{TARGET}` work?"),
            _findings(),
            Trace(),
            ProjectMemory(),
            read_file=reader,
        )
        self.assertEqual(seen, [REAL_FILE])
        self.assertEqual(answer.claims[0].entry_class, "FACT")

    def test_omitting_the_reader_still_uses_the_real_investigator(self) -> None:
        """Production callers must keep working without passing one."""
        answer = assemble(
            decompose(f"how does `{TARGET}` work?"), _findings(), Trace(), ProjectMemory()
        )
        self.assertEqual(answer.claims[0].entry_class, "FACT")


class NotLocatedTest(unittest.TestCase):
    def test_an_unlocatable_symbol_says_so_about_the_index_not_the_codebase(self) -> None:
        """"Not in the index" and "not in the codebase" are different claims,
        and only the first was established."""
        trace = Trace()
        trace.record("search_symbols", "'nope', crate='buzz-core'", found=False, detail="no symbol")
        findings = Findings(target="nope")
        answer = assemble(decompose("how does `nope` work?"), findings, trace, ProjectMemory())
        self.assertIn("could not be located in the index", answer.short_answer)
        self.assertIn("statement about the index", answer.things_to_be_aware_of)
        self.assertEqual(len(answer.claims), 1)
        self.assertEqual(answer.claims[0].entry_class, "FACT")


if __name__ == "__main__":
    unittest.main()
