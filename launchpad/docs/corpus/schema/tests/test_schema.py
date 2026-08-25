"""Unit tests for the corpus node/relationship schemas -- issue #622.

Run:  python3 -m unittest launchpad.docs.corpus.schema.tests.test_schema
  or: python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py"
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema

SCHEMA_DIR = Path(__file__).resolve().parent.parent
NODE_SCHEMA_PATH = SCHEMA_DIR / "node.schema.json"
RELATIONSHIPS_SCHEMA_PATH = SCHEMA_DIR / "relationships.schema.json"


class SchemaMetaValidityTest(unittest.TestCase):
    """The schema documents themselves are valid JSON Schema (draft 2020-12)."""

    def test_node_schema_is_valid_json_schema(self) -> None:
        schema = json.loads(NODE_SCHEMA_PATH.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)

    def test_relationships_schema_is_valid_json_schema(self) -> None:
        schema = json.loads(RELATIONSHIPS_SCHEMA_PATH.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)


class RelationshipEnumMetadataTest(unittest.TestCase):
    """Every relationship type states its directionality and inverse authorship."""

    def setUp(self) -> None:
        self.schema = json.loads(RELATIONSHIPS_SCHEMA_PATH.read_text())
        self.enum_members = self.schema["$defs"]["relationship"]["properties"]["type"]["enum"]
        self.meta = self.schema["relationshipMeta"]

    def test_every_enum_member_has_metadata(self) -> None:
        for member in self.enum_members:
            self.assertIn(member, self.meta, f"{member} has no relationshipMeta entry")

    def test_every_metadata_entry_has_directionality_and_inverse(self) -> None:
        for member in self.enum_members:
            entry = self.meta[member]
            self.assertIn("directionality", entry)
            self.assertTrue(entry["directionality"])
            self.assertIn("inverse", entry)
            self.assertIn(entry["inverse"], ("authored", "generated"))


if __name__ == "__main__":
    unittest.main()
