"""Unit tests for the Git/GitHub evidence bundle collector -- issue #625.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

No test calls the real `gh` CLI or network -- `FakeGitHubClient` below returns
canned dicts shaped like the real GitHub REST responses `GitHubClient` parses,
the same "fixtures/mocked GitHub responses" approach issue #627's own
definition of done calls for. `collect_code_evidence`/`collect_adr_evidence`
read real files, so those tests build a throwaway repo tree under
`tempfile.TemporaryDirectory`, mirroring `test_inventory.py`'s rule.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_EVIDENCE_PATH = Path(__file__).resolve().parent.parent / "evidence.py"
_spec = importlib.util.spec_from_file_location("corpus_evidence", _EVIDENCE_PATH)
evidence = importlib.util.module_from_spec(_spec)
sys.modules["corpus_evidence"] = evidence
_spec.loader.exec_module(evidence)


class FakeGitHubClient(evidence.GitHubClient):
    """Returns canned data instead of shelling out to `gh api`."""

    def __init__(self, *, commit=None, pr_reviews=None, issue=None, issue_comments=None) -> None:
        self._commit = commit or {}
        self._pr_reviews = pr_reviews or []
        self._issue = issue or {}
        self._issue_comments = issue_comments or []

    def get_commit(self, repo: str, sha: str) -> dict:
        return self._commit

    def get_pull_request(self, repo: str, number: int) -> dict:
        raise NotImplementedError("not used by these tests")

    def get_pull_request_reviews(self, repo: str, number: int) -> list:
        return self._pr_reviews

    def get_issue(self, repo: str, number: int) -> dict:
        return self._issue

    def get_issue_comments(self, repo: str, number: int) -> list:
        return self._issue_comments


class CredentialLikePathTest(unittest.TestCase):
    def test_env_local_is_prohibited(self) -> None:
        self.assertTrue(evidence._is_credential_like_path(".env.local"))

    def test_bare_env_is_prohibited(self) -> None:
        self.assertTrue(evidence._is_credential_like_path(".env"))

    def test_env_example_is_not_prohibited(self) -> None:
        self.assertFalse(evidence._is_credential_like_path(".env.example"))

    def test_id_ed25519_is_prohibited(self) -> None:
        self.assertTrue(evidence._is_credential_like_path("id_ed25519"))

    def test_pem_extension_is_prohibited(self) -> None:
        self.assertTrue(evidence._is_credential_like_path("certs/server.pem"))

    def test_ordinary_auth_crate_path_is_not_prohibited(self) -> None:
        # The exact regression validate.py's own review caught: *auth* as a
        # substring must never reject a real, non-secret path.
        self.assertFalse(evidence._is_credential_like_path("crates/buzz-auth/src/lib.rs"))


class CollectCodeEvidenceTest(unittest.TestCase):
    def test_bundles_a_real_path_with_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "crates" / "buzz-core" / "src").mkdir(parents=True)
            (root / "crates" / "buzz-core" / "src" / "kind.rs").write_text("pub const KIND_TEXT_NOTE: u32 = 1;\n")

            entry = evidence.collect_code_evidence(
                root, "crates/buzz-core/src/kind.rs", "text-note-kind-value", "1", line=1
            )

        self.assertEqual(entry.evidence_class, "code")
        self.assertEqual(entry.source_id, "crates/buzz-core/src/kind.rs:1")
        self.assertTrue(entry.fact_eligible)

    def test_refuses_a_credential_shaped_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.local").write_text("SECRET=x\n")

            with self.assertRaises(evidence.ProhibitedPathError):
                evidence.collect_code_evidence(root, ".env.local", "some-claim", "value")

    def test_refuses_a_path_that_does_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                evidence.collect_code_evidence(Path(tmp), "does/not/exist.rs", "claim", "value")

    def test_rejects_an_evidence_class_outside_code_test_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "f.rs").write_text("x")
            with self.assertRaises(ValueError):
                evidence.collect_code_evidence(root, "f.rs", "claim", "value", evidence_class="commit")


class CollectAdrEvidenceTest(unittest.TestCase):
    def test_bundles_an_accepted_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "launchpad" / "decisions").mkdir(parents=True)
            (root / "launchpad" / "decisions" / "ADR-0029-corpus-evidence-precedence.md").write_text("# ADR\n")

            entry = evidence.collect_adr_evidence(
                root,
                "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md",
                "evidence-precedence-rule",
                "record conflicts, never auto-resolve",
            )

        self.assertEqual(entry.evidence_class, "adr")
        self.assertTrue(entry.fact_eligible)


class CollectCommitEvidenceTest(unittest.TestCase):
    def test_records_the_resolved_sha_and_url(self) -> None:
        client = FakeGitHubClient(commit={"sha": "abc123", "html_url": "https://github.com/o/r/commit/abc123"})

        entry = evidence.collect_commit_evidence("o/r", "abc123", "claim", "value", client)

        self.assertEqual(entry.evidence_class, "commit")
        self.assertEqual(entry.source_id, "sha:abc123")
        self.assertEqual(entry.url, "https://github.com/o/r/commit/abc123")
        self.assertTrue(entry.fact_eligible)


class CollectPrReviewEvidenceTest(unittest.TestCase):
    def test_one_entry_per_review_never_fact_eligible(self) -> None:
        client = FakeGitHubClient(
            pr_reviews=[
                {"id": 1, "html_url": "https://github.com/o/r/pull/9#pullrequestreview-1"},
                {"id": 2, "html_url": "https://github.com/o/r/pull/9#pullrequestreview-2"},
            ]
        )

        entries = evidence.collect_pr_review_evidence("o/r", 9, "claim", "value", client)

        self.assertEqual(len(entries), 2)
        self.assertTrue(all(e.evidence_class == "pr_review" for e in entries))
        self.assertTrue(all(e.fact_eligible is False for e in entries))
        self.assertEqual({e.source_id for e in entries}, {"pr:9#review:1", "pr:9#review:2"})


class CollectIssueDiscussionEvidenceTest(unittest.TestCase):
    def test_issue_body_and_every_comment_are_separate_entries(self) -> None:
        client = FakeGitHubClient(
            issue={"html_url": "https://github.com/o/r/issues/42"},
            issue_comments=[
                {"id": 100, "html_url": "https://github.com/o/r/issues/42#comment-100"},
                {"id": 101, "html_url": "https://github.com/o/r/issues/42#comment-101"},
            ],
        )

        entries = evidence.collect_issue_discussion_evidence("o/r", 42, "claim", "value", client)

        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].source_id, "issue:42")
        self.assertEqual({e.source_id for e in entries[1:]}, {"issue:42#comment:100", "issue:42#comment:101"})
        self.assertTrue(all(e.fact_eligible is False for e in entries))


class FactEligibilityConsistencyTest(unittest.TestCase):
    def test_discussion_class_cannot_be_constructed_as_fact_eligible(self) -> None:
        with self.assertRaises(ValueError):
            evidence.EvidenceEntry(
                evidence_class="issue_discussion",
                claim_key="k",
                value="v",
                source_id="issue:1",
                url=None,
                fact_eligible=True,
            )

    def test_code_class_cannot_be_constructed_as_non_fact_eligible(self) -> None:
        with self.assertRaises(ValueError):
            evidence.EvidenceEntry(
                evidence_class="code",
                claim_key="k",
                value="v",
                source_id="some/path.rs",
                url=None,
                fact_eligible=False,
            )

    def test_unknown_evidence_class_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evidence.EvidenceEntry(
                evidence_class="rumor",
                claim_key="k",
                value="v",
                source_id="x",
                url=None,
                fact_eligible=True,
            )


class ConflictDetectionTest(unittest.TestCase):
    def _entry(self, claim_key: str, value: str, source_id: str) -> "evidence.EvidenceEntry":
        return evidence.EvidenceEntry(
            evidence_class="code",
            claim_key=claim_key,
            value=value,
            source_id=source_id,
            url=None,
            fact_eligible=True,
        )

    def test_differing_values_under_the_same_claim_key_are_flagged(self) -> None:
        entries = [self._entry("timeout-seconds", "30", "a.rs"), self._entry("timeout-seconds", "60", "b.rs")]

        conflicts = evidence.find_conflicts(entries)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["claim_key"], "timeout-seconds")
        self.assertEqual(conflicts[0]["values"], ["30", "60"])

    def test_matching_values_under_the_same_claim_key_are_not_flagged(self) -> None:
        entries = [self._entry("timeout-seconds", "30", "a.rs"), self._entry("timeout-seconds", "30", "b.rs")]

        self.assertEqual(evidence.find_conflicts(entries), [])

    def test_conflict_is_reported_even_when_one_side_outranks_the_other(self) -> None:
        # ADR-0029 as AGENTS.md cites it: even a same-type conflict is recorded,
        # never silently resolved by picking the nominally higher-precedence side.
        entries = [
            evidence.EvidenceEntry(
                evidence_class="adr",
                claim_key="retention-days",
                value="30",
                source_id="launchpad/decisions/ADR-x.md",
                url=None,
                fact_eligible=True,
            ),
            self._entry("retention-days", "14", "crates/buzz-relay/src/config.rs"),
        ]

        conflicts = evidence.find_conflicts(entries)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["values"], ["14", "30"])


class FullBundleFixtureTest(unittest.TestCase):
    """One fixture demonstrating code + test + commit + PR + issue evidence -- issue #625 DoD."""

    def test_bundle_contains_all_five_evidence_classes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "crates" / "buzz-core" / "src").mkdir(parents=True)
            (root / "crates" / "buzz-core" / "src" / "kind.rs").write_text("pub const KIND_REACTION: u32 = 7;\n")
            (root / "crates" / "buzz-test-client" / "tests").mkdir(parents=True)
            (root / "crates" / "buzz-test-client" / "tests" / "e2e_relay.rs").write_text("// test\n")

            client = FakeGitHubClient(
                commit={"sha": "deadbeef", "html_url": "https://github.com/o/r/commit/deadbeef"},
                pr_reviews=[{"id": 1, "html_url": "https://github.com/o/r/pull/5#pullrequestreview-1"}],
                issue={"html_url": "https://github.com/o/r/issues/7"},
                issue_comments=[],
            )

            entries = [
                evidence.collect_code_evidence(
                    root, "crates/buzz-core/src/kind.rs", "reaction-kind-value", "7", evidence_class="code"
                ),
                evidence.collect_code_evidence(
                    root,
                    "crates/buzz-test-client/tests/e2e_relay.rs",
                    "reaction-kind-covered-by-e2e",
                    "yes",
                    evidence_class="test",
                ),
                evidence.collect_commit_evidence("o/r", "deadbeef", "reaction-kind-introduced", "deadbeef", client),
                *evidence.collect_pr_review_evidence("o/r", 5, "reaction-kind-reviewed", "approved", client),
                *evidence.collect_issue_discussion_evidence("o/r", 7, "reaction-kind-requested", "requested", client),
            ]

            bundle = evidence.build_bundle(entries)

        classes_present = {e.evidence_class for e in bundle.entries}
        self.assertEqual(classes_present, {"code", "test", "commit", "pr_review", "issue_discussion"})
        self.assertEqual(bundle.conflicts, [])
        # Every entry carries a stable identifier, never bare unattributed prose.
        self.assertTrue(all(e.source_id for e in bundle.entries))

    def test_bundle_json_is_sorted_and_round_trips(self) -> None:
        import json

        entries = [
            evidence.EvidenceEntry("code", "z-claim", "v", "z.rs", None, True),
            evidence.EvidenceEntry("code", "a-claim", "v", "a.rs", None, True),
        ]
        bundle = evidence.build_bundle(entries)

        payload = json.loads(bundle.to_json())

        self.assertEqual([e["claim_key"] for e in payload["entries"]], ["a-claim", "z-claim"])


if __name__ == "__main__":
    unittest.main()
