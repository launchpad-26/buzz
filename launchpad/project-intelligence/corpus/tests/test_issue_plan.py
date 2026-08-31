"""Unit tests for the idempotent GitHub issue-plan helper -- issue #627.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

No test calls the real `gh` CLI -- `FakePort` below is an in-memory
GitHubPort that behaves like a real issue tracker (title lookups return
what was actually "created" through it) without any network access, the
"fixtures/mocked GitHub responses" approach issue #627's own definition of
done calls for.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_CORPUS_DIR = Path(__file__).resolve().parent.parent

_manifest_spec = importlib.util.spec_from_file_location("corpus_manifest", _CORPUS_DIR / "manifest.py")
manifest = importlib.util.module_from_spec(_manifest_spec)
sys.modules["corpus_manifest"] = manifest
_manifest_spec.loader.exec_module(manifest)

_issue_plan_spec = importlib.util.spec_from_file_location("corpus_issue_plan", _CORPUS_DIR / "issue_plan.py")
issue_plan = importlib.util.module_from_spec(_issue_plan_spec)
sys.modules["corpus_issue_plan"] = issue_plan
_issue_plan_spec.loader.exec_module(issue_plan)


def _row(**overrides) -> "manifest.ManifestRow":
    base = dict(
        path="launchpad/docs/corpus/capabilities/chat.md",
        filename="chat.md",
        issue_title="task: document capabilities/chat.md",
        parent_feature="#608",
        priority="P2",
        start_date=None,
        target_date=None,
        effort="M",
        blockers=(),
        template="capability",
        purpose="Describe the chat capability's contract.",
        audiences=("agent",),
        source_start_points=("desktop_feature:chat",),
    )
    base.update(overrides)
    return manifest.ManifestRow(**base)


class FakePort(issue_plan.GitHubPort):
    """An in-memory GitHub: issues really get created and can really be found by title."""

    def __init__(self, *, project_field_writable=True, blockers_supported=True) -> None:
        self._next_number = 1000
        self._issues: dict[int, dict] = {}  # number -> {"title": ..., "labels": ...}
        self._sub_issues: dict[int, list[int]] = {}
        self.project_field_writes: list[tuple] = []
        self.blocked_by_calls: list[tuple] = []
        self._project_field_writable = project_field_writable
        self._blockers_supported = blockers_supported

    def find_issue_by_title(self, repo: str, title: str) -> int | None:
        for number, data in self._issues.items():
            if data["title"] == title:
                return number
        return None

    def create_issue(self, repo: str, title: str, body: str, labels: tuple) -> int:
        number = self._next_number
        self._next_number += 1
        self._issues[number] = {"title": title, "labels": labels, "body": body}
        return number

    def add_sub_issue(self, repo: str, parent_number: int, child_number: int) -> None:
        self._sub_issues.setdefault(parent_number, []).append(child_number)

    def get_sub_issue_numbers(self, repo: str, parent_number: int) -> list[int]:
        return list(self._sub_issues.get(parent_number, []))

    def set_project_field(self, repo: str, issue_number: int, field_name: str, value) -> bool:
        self.project_field_writes.append((issue_number, field_name, value))
        return self._project_field_writable

    def set_blocked_by(self, repo: str, issue_number: int, blocker_issue_number: int) -> bool:
        self.blocked_by_calls.append((issue_number, blocker_issue_number))
        return self._blockers_supported


class DryRunTest(unittest.TestCase):
    def test_dry_run_emits_the_plan_without_a_port_at_all(self) -> None:
        result = issue_plan.dry_run([_row()])

        self.assertEqual(len(result.planned), 1)
        self.assertEqual(result.planned[0].title, "task: document capabilities/chat.md")
        self.assertEqual(result.planned[0].alias, "launchpad/docs/corpus/capabilities/chat.md")

    def test_dry_run_is_deterministic_json(self) -> None:
        first = issue_plan.dry_run([_row()]).to_json()
        second = issue_plan.dry_run([_row()]).to_json()

        self.assertEqual(first, second)


class ApplyCreatesTest(unittest.TestCase):
    def test_a_fresh_apply_creates_one_issue_per_row(self) -> None:
        port = FakePort()

        result = issue_plan.apply([_row()], port, "o/r")

        self.assertEqual(len(result.created), 1)
        self.assertEqual(result.already_existed, {})


class IdempotentResumeTest(unittest.TestCase):
    def test_reapplying_the_same_rows_creates_no_duplicates(self) -> None:
        port = FakePort()
        row = _row()

        first = issue_plan.apply([row], port, "o/r")
        second = issue_plan.apply([row], port, "o/r", alias_ledger={**first.created, **first.already_existed})

        self.assertEqual(len(second.created), 0)
        self.assertEqual(len(second.already_existed), 1)
        # Only one real issue exists in the fake tracker -- the guard worked, not just the ledger.
        self.assertEqual(len(port._issues), 1)

    def test_an_interruption_without_a_ledger_still_avoids_duplicates_via_title_search(self) -> None:
        # Simulates: first run created the issue then crashed before returning
        # the ledger. A second run with NO ledger still must not duplicate --
        # find_issue_by_title is the fallback that makes this safe.
        port = FakePort()
        row = _row()
        port.create_issue("o/r", row.issue_title, "some body", ("by:agent",))

        result = issue_plan.apply([row], port, "o/r", alias_ledger=None)

        self.assertEqual(result.created, {})
        self.assertEqual(len(result.already_existed), 1)
        self.assertEqual(len(port._issues), 1)


class ProjectFieldTest(unittest.TestCase):
    def test_writable_fields_produce_no_manual_actions(self) -> None:
        port = FakePort(project_field_writable=True)
        row = _row(priority="P1", start_date="2026-09-01", target_date="2026-09-15", effort="S")

        result = issue_plan.apply([row], port, "o/r")

        self.assertEqual(result.manual_actions, [])
        self.assertEqual(len(port.project_field_writes), 4)

    def test_unwritable_fields_produce_one_manual_action_each(self) -> None:
        port = FakePort(project_field_writable=False)
        row = _row(priority="P1", start_date="2026-09-01", target_date="2026-09-15", effort="S")

        result = issue_plan.apply([row], port, "o/r")

        self.assertEqual(len(result.manual_actions), 4)
        self.assertTrue(all("Manually set" in a for a in result.manual_actions))

    def test_none_valued_fields_are_skipped_not_reported_as_manual_actions(self) -> None:
        port = FakePort(project_field_writable=False)
        row = _row(start_date=None, target_date=None)

        result = issue_plan.apply([row], port, "o/r")

        # Only priority and effort are non-None in the default fixture row.
        self.assertEqual(len(result.manual_actions), 2)


class BlockerTest(unittest.TestCase):
    def test_a_blocker_already_created_in_this_run_is_applied(self) -> None:
        port = FakePort(blockers_supported=True)
        blocker_row = _row(
            path="launchpad/docs/corpus/capabilities/base.md",
            filename="base.md",
            issue_title="task: document capabilities/base.md",
        )
        dependent_row = _row(
            path="launchpad/docs/corpus/capabilities/chat.md",
            filename="chat.md",
            issue_title="task: document capabilities/chat.md",
            blockers=("launchpad/docs/corpus/capabilities/base.md",),
        )

        result = issue_plan.apply([blocker_row, dependent_row], port, "o/r")

        self.assertEqual(result.unresolved_blockers, [])
        self.assertEqual(len(port.blocked_by_calls), 1)

    def test_a_blocker_the_port_cannot_apply_is_reported_unresolved(self) -> None:
        port = FakePort(blockers_supported=False)
        blocker_row = _row(
            path="launchpad/docs/corpus/capabilities/base.md",
            filename="base.md",
            issue_title="task: document capabilities/base.md",
        )
        dependent_row = _row(blockers=("launchpad/docs/corpus/capabilities/base.md",))

        result = issue_plan.apply([blocker_row, dependent_row], port, "o/r")

        self.assertEqual(len(result.unresolved_blockers), 1)
        self.assertEqual(result.unresolved_blockers[0]["reason"], "port could not apply a blocked-by relationship")

    def test_a_blocker_that_was_never_created_is_reported_unresolved_not_crashed(self) -> None:
        port = FakePort(blockers_supported=True)
        dependent_row = _row(blockers=("launchpad/docs/corpus/capabilities/nonexistent.md",))

        result = issue_plan.apply([dependent_row], port, "o/r")

        self.assertEqual(len(result.unresolved_blockers), 1)
        self.assertEqual(result.unresolved_blockers[0]["reason"], "blocker not yet created")
        self.assertEqual(port.blocked_by_calls, [])


class SubIssueLinkTest(unittest.TestCase):
    def test_link_verified_by_reading_the_parent_back(self) -> None:
        port = FakePort()

        linked = issue_plan.link_sub_issue(port, "o/r", parent_number=1, child_number=2)

        self.assertTrue(linked)
        self.assertEqual(port.get_sub_issue_numbers("o/r", 1), [2])

    def test_link_call_succeeding_without_the_child_appearing_is_reported_as_not_linked(self) -> None:
        class LiesAboutLinkingPort(FakePort):
            def add_sub_issue(self, repo, parent_number, child_number) -> None:
                pass  # deliberately does not record it, simulating a silent no-op API

        port = LiesAboutLinkingPort()

        linked = issue_plan.link_sub_issue(port, "o/r", parent_number=1, child_number=2)

        self.assertFalse(linked)


class RealPortSafeFallbackTest(unittest.TestCase):
    """The real GitHubPort makes real `gh` calls for creates/reads/sub-issues/
    project fields (untested here, same as evidence.py's GitHubClient --
    see that module's own test file), but the two paths that need no network
    access at all are exercised for real: no project configured always
    degrades to a manual action, and set_blocked_by is unconditional."""

    def test_set_project_field_without_a_configured_project_returns_false(self) -> None:
        port = issue_plan.GitHubPort()  # project_owner/project_number default to None

        self.assertFalse(port.set_project_field("o/r", 1, "Priority", "P1"))

    def test_set_blocked_by_is_always_false_by_design(self) -> None:
        port = issue_plan.GitHubPort()

        self.assertFalse(port.set_blocked_by("o/r", 1, 2))


if __name__ == "__main__":
    unittest.main()
