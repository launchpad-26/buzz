"""Controls for memory.py -- issue #209.

Run:  python3 -m unittest test_memory    (from launchpad/project-intelligence/)
  or: python3 test_memory.py
"""

from __future__ import annotations

import unittest

from memory import MemoryEntry, ProjectMemory


class MemoryEntryValidationTest(unittest.TestCase):
    def test_valid_fact_entry_constructs(self) -> None:
        entry = MemoryEntry(
            id="1", entry_class="FACT", statement="is_shared_gated_kind exists", evidence=("crates/buzz-core/src/kind.rs:219",)
        )
        self.assertEqual(entry.entry_class, "FACT")

    def test_valid_inference_entry_constructs(self) -> None:
        entry = MemoryEntry(
            id="2",
            entry_class="INFERENCE",
            statement="kind gating likely applies to all team-scoped kinds",
            evidence=("crates/buzz-core/src/kind.rs:219", "crates/buzz-core/src/kind.rs:234"),
            confidence=0.7,
        )
        self.assertEqual(entry.confidence, 0.7)

    def test_valid_team_knowledge_entry_constructs(self) -> None:
        entry = MemoryEntry(
            id="3",
            entry_class="TEAM_KNOWLEDGE",
            statement="OrderRepository.legacyExport is being migrated off; do not add new callers.",
            provided_by="developer, migration issue #482",
        )
        self.assertEqual(entry.provided_by, "developer, migration issue #482")

    def test_confidence_on_a_fact_entry_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(id="4", entry_class="FACT", statement="x", evidence=("e",), confidence=0.9)

    def test_missing_evidence_on_an_inference_entry_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(id="5", entry_class="INFERENCE", statement="x", confidence=0.5)

    def test_missing_provided_by_on_a_team_knowledge_entry_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(id="6", entry_class="TEAM_KNOWLEDGE", statement="x")

    def test_missing_evidence_on_a_fact_entry_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(id="7", entry_class="FACT", statement="x")

    def test_provided_by_on_a_fact_entry_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(id="8", entry_class="FACT", statement="x", evidence=("e",), provided_by="someone")

    def test_invalid_entry_class_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(id="9", entry_class="OPINION", statement="x")

    def test_invalid_temporal_state_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryEntry(
                id="10",
                entry_class="TEAM_KNOWLEDGE",
                statement="x",
                provided_by="someone",
                temporal_state="FUTURE",
            )


class ProjectMemoryStoreTest(unittest.TestCase):
    def _store_with_one_of_each_class(self) -> ProjectMemory:
        store = ProjectMemory()
        store.add(MemoryEntry(id="f1", entry_class="FACT", statement="fact", evidence=("e1",)))
        store.add(
            MemoryEntry(id="i1", entry_class="INFERENCE", statement="inference", evidence=("e1", "e2"), confidence=0.6)
        )
        store.add(
            MemoryEntry(id="t1", entry_class="TEAM_KNOWLEDGE", statement="team knowledge", provided_by="someone")
        )
        return store

    def test_query_by_class_returns_only_that_class(self) -> None:
        store = self._store_with_one_of_each_class()

        team_knowledge = store.query_by_class("TEAM_KNOWLEDGE")
        self.assertEqual([e.id for e in team_knowledge], ["t1"])

        facts = store.query_by_class("FACT")
        self.assertEqual([e.id for e in facts], ["f1"])

        inferences = store.query_by_class("INFERENCE")
        self.assertEqual([e.id for e in inferences], ["i1"])

    def test_get_returns_the_stored_entry(self) -> None:
        store = self._store_with_one_of_each_class()
        self.assertEqual(store.get("f1").statement, "fact")

    def test_get_returns_none_for_an_unknown_id(self) -> None:
        store = ProjectMemory()
        self.assertIsNone(store.get("no-such-id"))

    def test_add_rejects_a_duplicate_id(self) -> None:
        store = self._store_with_one_of_each_class()
        with self.assertRaises(ValueError):
            store.add(MemoryEntry(id="f1", entry_class="FACT", statement="different", evidence=("e",)))


class RecordCodeContradictionTest(unittest.TestCase):
    def test_supersedes_a_fact_entry_without_overwriting_it(self) -> None:
        store = ProjectMemory()
        original = MemoryEntry(
            id="f1", entry_class="FACT", statement="is_shared_gated_kind gates only KIND_PERSONA", evidence=("e1",)
        )
        store.add(original)

        new_entry = store.record_code_contradiction(
            "f1", "is_shared_gated_kind gates KIND_PERSONA and KIND_TEAM_CATALOG", ("crates/buzz-core/src/kind.rs:219",)
        )

        self.assertEqual(new_entry.entry_class, "FACT")
        self.assertEqual(new_entry.statement, "is_shared_gated_kind gates KIND_PERSONA and KIND_TEAM_CATALOG")

        old_still_in_store = store.get("f1")
        self.assertEqual(old_still_in_store.statement, original.statement)  # never silently overwritten
        self.assertEqual(old_still_in_store.evidence, original.evidence)
        self.assertEqual(old_still_in_store.superseded_by, new_entry.id)  # but flagged stale

    def test_new_entry_is_queryable_alongside_the_old_one(self) -> None:
        store = ProjectMemory()
        store.add(MemoryEntry(id="f1", entry_class="FACT", statement="old", evidence=("e1",)))
        new_entry = store.record_code_contradiction("f1", "new", ("e2",))

        facts = {e.id for e in store.query_by_class("FACT")}
        self.assertEqual(facts, {"f1", new_entry.id})

    def test_unknown_entry_id_raises(self) -> None:
        store = ProjectMemory()
        with self.assertRaises(KeyError):
            store.record_code_contradiction("no-such-id", "new", ("e",))

    def test_team_knowledge_entry_is_not_superseded_by_a_code_contradiction(self) -> None:
        # One test exercising BOTH: the same function supersedes a FACT entry
        # (STEP 3) but is a no-op against a TEAM_KNOWLEDGE entry -- proving
        # the exception is about the class, not the function doing nothing.
        store = ProjectMemory()
        store.add(MemoryEntry(id="f1", entry_class="FACT", statement="fact", evidence=("e1",)))
        store.add(
            MemoryEntry(
                id="t1",
                entry_class="TEAM_KNOWLEDGE",
                statement="OrderRepository.legacyExport is being migrated off; do not add new callers.",
                provided_by="developer, migration issue #482",
            )
        )

        fact_result = store.record_code_contradiction("f1", "new fact", ("e2",))
        team_knowledge_result = store.record_code_contradiction(
            "t1", "code shows legacyExport is unused", ("crates/whatever/src/lib.rs:1",)
        )

        self.assertIsNotNone(fact_result)  # the FACT case still supersedes
        self.assertIsNone(team_knowledge_result)  # the TEAM_KNOWLEDGE case does not

        team_knowledge_entry = store.get("t1")
        self.assertIsNone(team_knowledge_entry.superseded_by)
        self.assertEqual(
            team_knowledge_entry.statement,
            "OrderRepository.legacyExport is being migrated off; do not add new callers.",
        )


class RecordTeamStatementTest(unittest.TestCase):
    def test_supersedes_a_team_knowledge_entry(self) -> None:
        store = ProjectMemory()
        store.add(
            MemoryEntry(
                id="t1",
                entry_class="TEAM_KNOWLEDGE",
                statement="OrderRepository.legacyExport is being migrated off; do not add new callers.",
                provided_by="developer, migration issue #482",
            )
        )

        new_entry = store.record_team_statement(
            "t1", "migration #482 complete, legacyExport removed", "developer, migration issue #482"
        )

        self.assertEqual(new_entry.entry_class, "TEAM_KNOWLEDGE")
        self.assertEqual(new_entry.statement, "migration #482 complete, legacyExport removed")

        old_entry = store.get("t1")
        self.assertEqual(old_entry.superseded_by, new_entry.id)
        # the original wording is preserved, not rewritten
        self.assertEqual(old_entry.statement, "OrderRepository.legacyExport is being migrated off; do not add new callers.")

    def test_unknown_entry_id_raises(self) -> None:
        store = ProjectMemory()
        with self.assertRaises(KeyError):
            store.record_team_statement("no-such-id", "new", "someone")


if __name__ == "__main__":
    unittest.main()
