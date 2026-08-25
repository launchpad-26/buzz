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
    """A validator for node.schema.json.

    Plain construction, no custom resolver -- node.schema.json's `relationships` field
    inlines its own $defs.relationship rather than $ref-ing relationships.schema.json
    across files. An earlier revision used a cross-file $ref keyed to node.schema.json's
    $id, which is a fake `https://buzz.launchpad-26.internal/...` domain: any standards-
    conformant validator that doesn't hand-build the same resolver/store this file used
    to (jsonschema.validate(), ajv, an IDE's JSON Schema support) would attempt a live
    DNS lookup and fail with RefResolutionError on any node using `relationships` --
    found by review-code, reproduced directly. See
    test_relationship_enum_matches_node_schemas_inlined_copy below for what keeps the
    inlined copy from silently drifting.
    """
    node_schema = json.loads(NODE_SCHEMA_PATH.read_text())
    return jsonschema.Draft202012Validator(node_schema)


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

    def test_relationship_enum_matches_node_schemas_inlined_copy(self) -> None:
        # node.schema.json inlines its own $defs.relationship (see _node_validator's
        # docstring) rather than $ref-ing this file across a schema boundary, so the two
        # enum lists are two literal copies. This is what stops them from silently
        # drifting apart -- a relationship type added to one and not the other fails here.
        node_schema = json.loads(NODE_SCHEMA_PATH.read_text())
        node_enum = node_schema["$defs"]["relationship"]["properties"]["type"]["enum"]
        self.assertEqual(node_enum, self.enum_members)


class ValidFixtureTest(unittest.TestCase):
    """Fully-conforming nodes pass validation."""

    def test_minimal_fixture_passes(self) -> None:
        frontmatter = _load_frontmatter(VALID_FIXTURES_DIR / "node-minimal.md")
        _node_validator().validate(frontmatter)

    def test_full_fixture_passes(self) -> None:
        # Exercises every optional path node-minimal.md doesn't: multiple audiences,
        # INFERENCE and TEAM_KNOWLEDGE on their own happy path (not just FACT), and a
        # relationship. Closes a real gap: without this, nothing in the suite confirmed
        # a *correct* INFERENCE/TEAM_KNOWLEDGE entry actually validates -- only that an
        # incomplete one is rejected. A schema that rejected every INFERENCE entry
        # outright would have passed every other test in this file.
        frontmatter = _load_frontmatter(VALID_FIXTURES_DIR / "node-full.md")
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

    # The tests below close gaps an independent review-tests pass found by mutation:
    # every field the schema declares `required` at :8 previously had a fixture only for
    # a *wrong value*, never plain absence -- so removing a field from `required`
    # entirely left the whole suite green. Each test here fails if the corresponding
    # field is ever silently dropped from `required` again.

    def test_missing_type_rejected(self) -> None:
        error = self._one_error("missing-type.md")
        self.assertEqual(error.validator, "required")
        self.assertIn("type", error.message)

    def test_missing_status_rejected(self) -> None:
        error = self._one_error("missing-status.md")
        self.assertEqual(error.validator, "required")
        self.assertIn("status", error.message)

    def test_missing_origin_rejected(self) -> None:
        error = self._one_error("missing-origin.md")
        self.assertEqual(error.validator, "required")
        self.assertIn("origin", error.message)

    def test_missing_evidence_field_rejected(self) -> None:
        # Distinct from test_missing_evidence_for_{fact,inference}_rejected, which cover
        # an evidence *entry* missing its own citations -- this covers the top-level
        # `evidence` array being absent entirely.
        error = self._one_error("missing-evidence-field.md")
        self.assertEqual(error.validator, "required")
        self.assertIn("evidence", error.message)

    def test_inference_missing_confidence_rejected(self) -> None:
        error = self._one_error("inference-missing-confidence.md")
        self.assertEqual(list(error.absolute_path), ["evidence", 0])
        self.assertEqual(error.validator, "required")
        self.assertIn("confidence", error.message)

    def test_team_knowledge_missing_provided_by_rejected(self) -> None:
        error = self._one_error("team-knowledge-missing-provided-by.md")
        self.assertEqual(list(error.absolute_path), ["evidence", 0])
        self.assertEqual(error.validator, "required")
        self.assertIn("provided_by", error.message)

    def test_fact_with_forbidden_fields_rejected(self) -> None:
        # Confirms the fix for review-code's finding: a FACT entry carrying confidence
        # or provided_by (fields that belong to INFERENCE/TEAM_KNOWLEDGE) must be
        # rejected, mirroring memory.py's bidirectional __post_init__ check -- not just
        # required-field checks in the "this class needs these fields" direction.
        error = self._one_error("fact-with-forbidden-fields.md")
        self.assertEqual(list(error.absolute_path), ["evidence", 0])
        self.assertEqual(error.validator, "not")

    def test_malformed_id_rejected(self) -> None:
        error = self._one_error("malformed-id.md")
        self.assertEqual(list(error.absolute_path), ["id"])
        self.assertEqual(error.validator, "pattern")

    def test_unrecognized_field_rejected(self) -> None:
        error = self._one_error("unrecognized-field.md")
        self.assertEqual(error.validator, "additionalProperties")
        self.assertIn("internal_note", error.message)

    def test_unknown_audience_value_rejected(self) -> None:
        error = self._one_error("unknown-audience-value.md")
        self.assertEqual(list(error.absolute_path), ["audiences", 0])
        self.assertEqual(error.validator, "enum")

    def test_duplicate_audiences_rejected(self) -> None:
        error = self._one_error("duplicate-audiences.md")
        self.assertEqual(list(error.absolute_path), ["audiences"])
        self.assertEqual(error.validator, "uniqueItems")


if __name__ == "__main__":
    unittest.main()
