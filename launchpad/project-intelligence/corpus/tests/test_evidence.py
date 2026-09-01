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
import unittest.mock
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


class CitationParserTest(unittest.TestCase):
    def test_parses_local_file_range(self) -> None:
        parsed = evidence.parse_citation("crates/buzz-core/src/kind.rs:219-221")
        self.assertEqual(parsed.kind, evidence.EvidenceKind.LOCAL_FILE_RANGE)
        self.assertEqual(parsed.path, "crates/buzz-core/src/kind.rs")
        self.assertEqual(parsed.start_line, 219)
        self.assertEqual(parsed.end_line, 221)

    def test_parses_commit_reference_without_echoing_raw_value_in_detail(self) -> None:
        parsed = evidence.parse_citation(
            "commit 69baedd197e5d35c9ae4736115789da59929e288 (2026-08-25)"
        )
        self.assertEqual(parsed.kind, evidence.EvidenceKind.COMMIT)
        self.assertEqual(parsed.commit, "69baedd197e5d35c9ae4736115789da59929e288")

    def test_parses_external_url_and_discards_trailing_metadata(self) -> None:
        parsed = evidence.parse_citation(
            "https://example.com/spec, ms.date 2026-01-01"
        )
        self.assertEqual(parsed.kind, evidence.EvidenceKind.EXTERNAL_URL)
        self.assertEqual(parsed.url, "https://example.com/spec")

    def test_parses_graph_and_tool_results_as_distinct_unopenable_kinds(self) -> None:
        graph = evidence.parse_citation("source_symbol -> target_symbol (1 hop)")
        tool = evidence.parse_citation("grep_repo('needle') -> no matches")
        self.assertEqual(graph.kind, evidence.EvidenceKind.GRAPH_EDGE)
        self.assertEqual(tool.kind, evidence.EvidenceKind.TOOL_RESULT)

    def test_unknown_citation_is_explicitly_unknown(self) -> None:
        parsed = evidence.parse_citation("free prose is not a citation")
        self.assertEqual(parsed.kind, evidence.EvidenceKind.UNKNOWN)


class EvidenceVerifierTest(unittest.TestCase):
    def test_verifies_existing_local_file_and_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "source.py"
            path.write_text("one\ntwo\n")
            parsed = evidence.parse_citation("source.py:2")
            result = evidence.verify_citation(parsed, root)
        self.assertEqual(result.status, "ok")

    def test_rejects_local_line_past_end_of_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.py").write_text("one\n")
            parsed = evidence.parse_citation("source.py:2")
            result = evidence.verify_citation(parsed, root)
        self.assertEqual(result.status, "error")
        self.assertIn("line position exceeds", result.detail)

    def test_verifies_existing_commit(self) -> None:
        root = Path(__file__).resolve().parents[4]
        parsed = evidence.parse_citation(
            "commit 69baedd197e5d35c9ae4736115789da59929e288"
        )
        result = evidence.verify_citation(parsed, root)
        self.assertEqual(result.status, "ok")

    def test_unsupported_tool_result_is_unverified(self) -> None:
        root = Path(__file__).resolve().parents[4]
        parsed = evidence.parse_citation("grep_repo('needle') -> no matches")
        result = evidence.verify_citation(parsed, root)
        self.assertEqual(result.status, "unverified")
        self.assertEqual(result.detail, evidence.UNVERIFIABLE_KIND_DETAIL)


class GitToolCitationParseTest(unittest.TestCase):
    """The argument half of a tool-result citation is tractable; the asserted
    half is prose. Parsing must expose the first without pretending about the
    second."""

    def test_captures_tool_name_arguments_and_assertion(self) -> None:
        parsed = evidence.parse_citation(
            "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') "
            "-> AGENTS.md, README.md"
        )
        self.assertEqual(parsed.kind, evidence.EvidenceKind.TOOL_RESULT)
        self.assertEqual(parsed.tool, "git_ls_tree")
        self.assertEqual(parsed.tool_assertion, "AGENTS.md, README.md")

    def test_parses_keyword_argument_form(self) -> None:
        args = evidence._parse_git_tool_arguments(
            "ref='origin/launchpad', path='launchpad/docs/corpus'"
        )
        self.assertEqual(args, ("origin/launchpad", "launchpad/docs/corpus"))

    def test_parses_unquoted_keyword_argument_form(self) -> None:
        args = evidence._parse_git_tool_arguments(
            "ref=origin/launchpad, path=launchpad/docs/corpus"
        )
        self.assertEqual(args, ("origin/launchpad", "launchpad/docs/corpus"))

    def test_parses_positional_form(self) -> None:
        args = evidence._parse_git_tool_arguments(
            "origin/launchpad, launchpad/docs/corpus"
        )
        self.assertEqual(args, ("origin/launchpad", "launchpad/docs/corpus"))

    def test_parses_git_show_combined_ref_colon_path_form(self) -> None:
        args = evidence._parse_git_tool_arguments(
            "'68cbb95295d1c76809b5f1595411bbe87d5deede:launchpad/docs/corpus/x.md'"
        )
        self.assertEqual(
            args,
            (
                "68cbb95295d1c76809b5f1595411bbe87d5deede",
                "launchpad/docs/corpus/x.md",
            ),
        )

    def test_ignores_a_trailing_annotation_argument(self) -> None:
        args = evidence._parse_git_tool_arguments(
            "origin/launchpad, 'launchpad/docs/corpus', run 2026-08-27"
        )
        self.assertEqual(args, ("origin/launchpad", "launchpad/docs/corpus"))

    def test_unparseable_arguments_return_none(self) -> None:
        self.assertIsNone(evidence._parse_git_tool_arguments(""))


class GitToolCitationVerifierTest(unittest.TestCase):
    """DECISION-1: this verifier is fail-only. It may report `error` when a
    cited source is gone, and otherwise leaves the citation blocking. It never
    returns `ok`, because the asserted result is prose nothing compared."""

    REPO_ROOT = Path(__file__).resolve().parents[4]

    def _verify(self, citation: str) -> evidence.VerificationResult:
        return evidence.verify_citation(
            evidence.parse_citation(citation), self.REPO_ROOT
        )

    def test_missing_ref_is_an_error(self) -> None:
        result = self._verify(
            "git_ls_tree(ref='origin/task/0000-branch-deleted-long-ago', "
            "path='launchpad/docs/corpus') -> AGENTS.md"
        )
        self.assertEqual(result.status, "error")
        self.assertIn("no longer exists", result.detail)

    def test_missing_path_at_a_live_ref_is_an_error(self) -> None:
        result = self._verify(
            "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus/no-such-dir') "
            "-> something"
        )
        self.assertEqual(result.status, "error")
        self.assertIn("does not exist at the cited ref", result.detail)

    def test_reachable_source_stays_blocking_with_a_specific_detail(self) -> None:
        result = self._verify(
            "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> AGENTS.md"
        )
        self.assertEqual(result.status, "unverified")
        self.assertIn("was not compared", result.detail)
        self.assertNotIn("no verifier exists", result.detail)

    def test_shell_metacharacters_are_refused_without_spawning_a_process(self) -> None:
        for hostile in (
            "git_ls_tree(ref='HEAD; rm -rf /', path='x') -> y",
            "git_ls_tree(ref='$(whoami)', path='x') -> y",
            "git_ls_tree(ref='`id`', path='x') -> y",
            "git_ls_tree(ref='HEAD | cat', path='x') -> y",
        ):
            with self.subTest(citation=hostile):
                with unittest.mock.patch.object(
                    evidence.subprocess, "run", side_effect=AssertionError("spawned")
                ):
                    result = self._verify(hostile)
                self.assertEqual(result.status, "unverified")
                self.assertIn("shell metacharacter", result.detail)

    def test_option_shaped_argument_is_refused_without_spawning_a_process(self) -> None:
        with unittest.mock.patch.object(
            evidence.subprocess, "run", side_effect=AssertionError("spawned")
        ):
            result = self._verify(
                "git_ls_tree(ref='--upload-pack=payload', path='x') -> y"
            )
        self.assertEqual(result.status, "unverified")
        self.assertIn("option", result.detail)

    def test_unparseable_arguments_stay_blocking_without_spawning_a_process(self) -> None:
        with unittest.mock.patch.object(
            evidence.subprocess, "run", side_effect=AssertionError("spawned")
        ):
            result = self._verify("git_ls_tree() -> nothing in particular")
        self.assertEqual(result.status, "unverified")
        self.assertIn("could not be parsed", result.detail)

    def test_no_input_ever_verifies_ok(self) -> None:
        """The load-bearing guarantee of DECISION-1."""
        for citation in (
            "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> AGENTS.md",
            "git_ls_tree(ref='HEAD', path='nope') -> AGENTS.md",
            "git_ls_tree(ref='origin/task/0000-gone', path='x') -> y",
            "git_show(ref='HEAD', path='launchpad/docs/corpus/AGENTS.md') -> heading",
            "git_ls_tree(HEAD, launchpad/docs/corpus) -> AGENTS.md",
            "git_ls_tree() -> nothing",
            "git_ls_tree(ref='$(id)', path='x') -> y",
        ):
            with self.subTest(citation=citation):
                self.assertNotEqual(self._verify(citation).status, "ok")

    def test_a_true_assertion_and_a_false_one_are_indistinguishable(self) -> None:
        """Not a gap — the documented consequence of not comparing prose. If
        this ever starts failing, the verifier began judging assertions and
        DECISION-1 needs revisiting."""
        truthful = self._verify(
            "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> AGENTS.md"
        )
        false = self._verify(
            "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') "
            "-> nothing whatsoever is present here"
        )
        self.assertEqual(truthful.status, false.status)
        self.assertEqual(truthful.detail, false.detail)


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

    def test_refuses_an_absolute_path(self) -> None:
        # An earlier revision checked only `(root / path).exists()`. pathlib's
        # `/` operator silently discards the left operand when the right is
        # absolute, so `root / "/etc/hosts"` evaluated to `/etc/hosts` itself
        # and "validated" against the host filesystem.
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                evidence.collect_code_evidence(Path(tmp), "/etc/hosts", "claim", "value")

    def test_refuses_a_path_that_escapes_the_repository_via_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                evidence.collect_code_evidence(
                    Path(tmp), "../../../../etc/passwd", "claim", "value"
                )

    def test_refuses_a_bare_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "launchpad").mkdir()
            with self.assertRaises(FileNotFoundError):
                evidence.collect_code_evidence(root, "launchpad", "claim", "value")


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

    def test_refuses_an_adr_path_that_escapes_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                evidence.collect_adr_evidence(
                    Path(tmp), "../../../../etc/passwd", "claim", "value"
                )


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
