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


class SchemaMetaValidityTest(unittest.TestCase):
    """The schema documents themselves are valid JSON Schema (draft 2020-12)."""

    def test_node_schema_is_valid_json_schema(self) -> None:
        schema = json.loads(NODE_SCHEMA_PATH.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
