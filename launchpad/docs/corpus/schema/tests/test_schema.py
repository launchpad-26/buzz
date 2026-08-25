"""Unit tests for the corpus node/relationship schemas -- issue #622.

Run:  python3 -m unittest launchpad.docs.corpus.schema.tests.test_schema
  or: python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py"
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml

SCHEMA_DIR = Path(__file__).resolve().parent.parent
NODE_SCHEMA_PATH = SCHEMA_DIR / "node.schema.json"
RELATIONSHIPS_SCHEMA_PATH = SCHEMA_DIR / "relationships.schema.json"
VALID_FIXTURES_DIR = SCHEMA_DIR / "fixtures" / "valid"
INVALID_FIXTURES_DIR = SCHEMA_DIR / "fixtures" / "invalid"


def _load_frontmatter(path: Path) -> dict:
    """Parse a Markdown-with-YAML-frontmatter fixture (ADR-0028's representation)."""
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path} has no leading frontmatter delimiter")
    _, frontmatter, _body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter)


def _node_validator() -> jsonschema.Draft202012Validator:
    """A validator for node.schema.json that can resolve its relationships.schema.json $ref."""
    node_schema = json.loads(NODE_SCHEMA_PATH.read_text())
    relationships_schema = json.loads(RELATIONSHIPS_SCHEMA_PATH.read_text())
    store = {relationships_schema["$id"]: relationships_schema}
    resolver = jsonschema.RefResolver.from_schema(node_schema, store=store)
    return jsonschema.Draft202012Validator(node_schema, resolver=resolver)


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


class ValidFixtureTest(unittest.TestCase):
    """A minimal, fully-conforming node passes validation."""

    def test_valid_fixture_passes(self) -> None:
        frontmatter = _load_frontmatter(VALID_FIXTURES_DIR / "node-minimal.md")
        _node_validator().validate(frontmatter)


class InvalidFixtureTest(unittest.TestCase):
    """Each fixture violates exactly one failure class, and fails only for that reason.

    Every assertion pins the single reported error's JSON path and validator keyword, not
    merely "raises" -- a fixture that fails for a different, accidental reason must fail
    this test, not pass it.
    """

    def _one_error(self, filename: str):
        frontmatter = _load_frontmatter(INVALID_FIXTURES_DIR / filename)
        errors = list(_node_validator().iter_errors(frontmatter))
        self.assertEqual(
            len(errors), 1, f"{filename}: expected exactly one error, got {errors}"
        )
        return errors[0]

    def test_missing_identity_rejected(self) -> None:
        error = self._one_error("missing-identity.md")
        self.assertEqual(error.validator, "required")
        self.assertIn("id", error.message)

    def test_unknown_type_rejected(self) -> None:
        error = self._one_error("unknown-type.md")
        self.assertEqual(list(error.absolute_path), ["type"])
        self.assertEqual(error.validator, "enum")

    def test_unknown_status_rejected(self) -> None:
        error = self._one_error("unknown-status.md")
        self.assertEqual(list(error.absolute_path), ["status"])
        self.assertEqual(error.validator, "enum")

    def test_unknown_origin_rejected(self) -> None:
        error = self._one_error("unknown-origin.md")
        self.assertEqual(list(error.absolute_path), ["origin"])
        self.assertEqual(error.validator, "enum")

    def test_missing_audiences_rejected(self) -> None:
        error = self._one_error("missing-audiences.md")
        self.assertEqual(error.validator, "required")
        self.assertIn("audiences", error.message)

    def test_missing_evidence_for_fact_rejected(self) -> None:
        error = self._one_error("missing-evidence-fact.md")
        self.assertEqual(list(error.absolute_path), ["evidence", 0])
        self.assertEqual(error.validator, "required")
        self.assertIn("evidence", error.message)

    def test_missing_evidence_for_inference_rejected(self) -> None:
        error = self._one_error("missing-evidence-inference.md")
        self.assertEqual(list(error.absolute_path), ["evidence", 0])
        self.assertEqual(error.validator, "required")
        self.assertIn("evidence", error.message)

    def test_unknown_relationship_type_rejected(self) -> None:
        error = self._one_error("unknown-relationship-type.md")
        self.assertEqual(list(error.absolute_path), ["relationships", 0, "type"])
        self.assertEqual(error.validator, "enum")

    def test_wrong_direction_relationship_rejected(self) -> None:
        # depended-on-by is depends-on's *generated* inverse (relationshipMeta) -- never
        # an authored `type` value. Same enum mechanism as unknown-relationship-type, but
        # a distinct, meaningful authoring mistake: hand-writing the inverse edge rather
        # than an arbitrary typo.
        error = self._one_error("wrong-direction-relationship.md")
        self.assertEqual(list(error.absolute_path), ["relationships", 0, "type"])
        self.assertEqual(error.validator, "enum")
        self.assertIn("depended-on-by", error.message)


if __name__ == "__main__":
    unittest.main()
