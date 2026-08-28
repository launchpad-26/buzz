"""Unit tests for the one-document one-task corpus manifest -- issue #626.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test constructs its own plan list in-memory -- there is no real
"the corpus's actual plan" fixture to read, because curating that plan is
explicitly out of scope for this task (see manifest.py's module docstring).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.py"
_spec = importlib.util.spec_from_file_location("corpus_manifest", _MANIFEST_PATH)
manifest = importlib.util.module_from_spec(_spec)
sys.modules["corpus_manifest"] = manifest
_spec.loader.exec_module(manifest)


def _entry(**overrides) -> dict:
    base = {
        "path": "launchpad/docs/corpus/capabilities/chat.md",
        "filename": "chat.md",
        "issue_title": "task: document capabilities/chat.md",
        "parent_feature": "#608",
        "priority": "P2",
        "start_date": None,
        "target_date": None,
        "effort": "M",
        "blockers": [],
        "template": "capability",
        "purpose": "Describe the chat capability's contract.",
        "audiences": ["agent", "contributor"],
        "source_start_points": ["desktop_feature:chat"],
    }
    base.update(overrides)
    return base


class RequiredFieldsTest(unittest.TestCase):
    def test_every_required_field_is_carried_through(self) -> None:
        result = manifest.build_manifest([_entry()])

        row = result.rows[0].to_dict()
        self.assertEqual(
            set(row.keys()),
            {
                "path",
                "filename",
                "issue_title",
                "parent_feature",
                "priority",
                "start_date",
                "target_date",
                "effort",
                "blockers",
                "template",
                "purpose",
                "audiences",
                "source_start_points",
            },
        )

    def test_missing_field_is_rejected_not_defaulted(self) -> None:
        entry = _entry()
        del entry["template"]

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest([entry])
        self.assertIn("template", str(ctx.exception))


class ScalarSequenceFieldTest(unittest.TestCase):
    def test_a_scalar_blockers_value_is_rejected_not_exploded_into_characters(self) -> None:
        entry = _entry(blockers="#607")

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest([entry])
        self.assertIn("blockers", str(ctx.exception))
        self.assertIn("not a list", str(ctx.exception))

    def test_a_scalar_audiences_value_is_rejected_not_exploded_into_characters(self) -> None:
        entry = _entry(audiences="agent")

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest([entry])
        self.assertIn("audiences", str(ctx.exception))

    def test_a_scalar_source_start_points_value_is_rejected_not_exploded_into_characters(self) -> None:
        entry = _entry(source_start_points="desktop_feature:chat")

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest([entry])
        self.assertIn("source_start_points", str(ctx.exception))


class DuplicatePathTest(unittest.TestCase):
    def test_the_same_document_assigned_to_two_tasks_is_rejected(self) -> None:
        first = _entry(issue_title="task: document capabilities/chat.md")
        second = _entry(issue_title="task: document capabilities/chat.md (duplicate)")

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest([first, second])
        self.assertIn("assigned to two tasks", str(ctx.exception))


class DuplicateIssueTitleTest(unittest.TestCase):
    def test_one_task_owning_two_documents_is_rejected(self) -> None:
        first = _entry(path="launchpad/docs/corpus/capabilities/chat.md", filename="chat.md")
        second = _entry(path="launchpad/docs/corpus/capabilities/forum.md", filename="forum.md")
        # Both entries share the same issue_title -- one task, two documents.

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest([first, second])
        self.assertIn("own two hand-authored canonical documents", str(ctx.exception))


class FeatureChildLimitTest(unittest.TestCase):
    def test_a_feature_at_exactly_the_limit_is_accepted(self) -> None:
        plan = [
            _entry(
                path=f"launchpad/docs/corpus/capabilities/cap-{i}.md",
                filename=f"cap-{i}.md",
                issue_title=f"task: document capabilities/cap-{i}.md",
            )
            for i in range(100)
        ]

        result = manifest.build_manifest(plan)

        self.assertEqual(len(result.rows), 100)

    def test_a_feature_over_the_limit_is_rejected(self) -> None:
        plan = [
            _entry(
                path=f"launchpad/docs/corpus/capabilities/cap-{i}.md",
                filename=f"cap-{i}.md",
                issue_title=f"task: document capabilities/cap-{i}.md",
            )
            for i in range(101)
        ]

        with self.assertRaises(manifest.ManifestValidationError) as ctx:
            manifest.build_manifest(plan)
        self.assertIn("101 document tasks", str(ctx.exception))

    def test_different_features_are_counted_independently(self) -> None:
        plan = [_entry(parent_feature="#608"), _entry(path="x2.md", filename="x2.md", issue_title="t2", parent_feature="#609")]

        result = manifest.build_manifest(plan)

        self.assertEqual(len(result.rows), 2)


class DeterminismTest(unittest.TestCase):
    def test_rerunning_against_the_same_plan_produces_no_diff(self) -> None:
        plan = [
            _entry(path="b.md", filename="b.md", issue_title="t-b"),
            _entry(path="a.md", filename="a.md", issue_title="t-a"),
        ]

        first = manifest.build_manifest(plan).to_json()
        second = manifest.build_manifest(plan).to_json()

        self.assertEqual(first, second)

    def test_rows_are_sorted_by_path_regardless_of_input_order(self) -> None:
        plan = [
            _entry(path="z.md", filename="z.md", issue_title="t-z"),
            _entry(path="a.md", filename="a.md", issue_title="t-a"),
        ]

        result = manifest.build_manifest(plan)

        self.assertEqual([row.path for row in result.rows], ["a.md", "z.md"])


class EmptyPlanTest(unittest.TestCase):
    def test_an_empty_plan_produces_an_empty_manifest_not_an_error(self) -> None:
        result = manifest.build_manifest([])

        self.assertEqual(result.rows, [])
        self.assertEqual(result.to_json(), '{\n  "rows": []\n}\n')


if __name__ == "__main__":
    unittest.main()
