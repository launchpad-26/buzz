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
        """Resolves a commit at run time. The previous hardcoded SHA was an
        unpushed local commit, so this passed on one machine and failed in CI
        once commit citations became verifiable."""
        import subprocess

        root = Path(__file__).resolve().parents[4]
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        result = evidence.verify_citation(
            evidence.parse_citation(f"commit {head}"), root
        )
        self.assertEqual(result.status, "ok")

    def test_unrecognised_tool_result_is_unverified(self) -> None:
        root = Path(__file__).resolve().parents[4]
        parsed = evidence.parse_citation("some_novel_tool('needle') -> no matches")
        result = evidence.verify_citation(parsed, root)
        self.assertEqual(result.status, "unverified")
        self.assertEqual(result.detail, evidence.UNVERIFIABLE_KIND_DETAIL)

    def test_graph_edge_keeps_the_shared_unverifiable_detail(self) -> None:
        root = Path(__file__).resolve().parents[4]
        parsed = evidence.parse_citation("source_symbol -> target_symbol (1 hop)")
        result = evidence.verify_citation(parsed, root)
        self.assertEqual(result.status, "unverified")
        self.assertEqual(result.detail, evidence.UNVERIFIABLE_KIND_DETAIL)


class SymbolAnchoredCitationTest(unittest.TestCase):
    """#2012: a position that survives edits.

    The corpus had only `path` (durable, no position) and `path:line` (precise,
    rots). This form is both, and it is the first precise code citation that can
    genuinely fail rather than have a bounds check stand in for a meaning check.
    """

    def test_parses_path_and_symbol(self) -> None:
        parsed = evidence.parse_citation(
            "launchpad/project-intelligence/corpus/validate.py#symbol=find_duplicate_ids"
        )
        self.assertEqual(parsed.kind, evidence.EvidenceKind.LOCAL_FILE_SYMBOL)
        self.assertEqual(
            parsed.path, "launchpad/project-intelligence/corpus/validate.py"
        )
        self.assertEqual(parsed.symbol, "find_duplicate_ids")

    def test_parses_dotted_member_symbol(self) -> None:
        parsed = evidence.parse_citation("a/b.py#symbol=ClassName.method_name")
        self.assertEqual(parsed.symbol, "ClassName.method_name")

    def test_present_symbol_verifies_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.py").write_text("def find_me():\n    return 1\n")
            result = evidence.verify_citation(
                evidence.parse_citation("source.py#symbol=find_me"), root
            )
        self.assertEqual(result.status, "ok")

    def test_absent_symbol_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.py").write_text("def something_else():\n    return 1\n")
            result = evidence.verify_citation(
                evidence.parse_citation("source.py#symbol=find_me"), root
            )
        self.assertEqual(result.status, "error")
        self.assertIn("does not appear in the cited file", result.detail)

    def test_survives_edits_above_it_where_a_line_number_would_not(self) -> None:
        """The property the form exists for. Both citations are correct before
        the edit; after 20 lines are inserted above, only the symbol anchor is
        still right -- and the line citation does not fail, it silently points
        at the wrong code."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.py"
            source.write_text("def target():\n    return 1\n" + "# tail\n" * 30)
            before_symbol = evidence.verify_citation(
                evidence.parse_citation("source.py#symbol=target"), root
            )
            before_line = evidence.verify_citation(
                evidence.parse_citation("source.py:1"), root
            )
            self.assertEqual(before_symbol.status, "ok")
            self.assertEqual(before_line.status, "ok")

            source.write_text("# inserted\n" * 20 + source.read_text())
            after_symbol = evidence.verify_citation(
                evidence.parse_citation("source.py#symbol=target"), root
            )
            after_line = evidence.verify_citation(
                evidence.parse_citation("source.py:1"), root
            )
        self.assertEqual(after_symbol.status, "ok")
        # Still "ok", now naming an inserted comment. Nothing detects it.
        self.assertEqual(after_line.status, "ok")

    def test_partial_word_does_not_count_as_the_symbol(self) -> None:
        """Without a word boundary, `#symbol=Foo` would be satisfied by
        `FooBarBaz`, and a renamed symbol would keep verifying."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.py").write_text("class FooBarBaz:\n    pass\n")
            result = evidence.verify_citation(
                evidence.parse_citation("source.py#symbol=Foo"), root
            )
        self.assertEqual(result.status, "error")

    def test_missing_file_is_an_error_before_the_symbol_is_considered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = evidence.verify_citation(
                evidence.parse_citation("no/such/file.py#symbol=whatever"), Path(tmp)
            )
        self.assertEqual(result.status, "error")
        self.assertIn("does not resolve to a real file", result.detail)

    def test_credential_guard_is_not_bypassed_by_the_new_form(self) -> None:
        """A new citation shape must not become a way around the blocklist."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.local").write_text("TOKEN=xyz\n")
            result = evidence.verify_citation(
                evidence.parse_citation(".env.local#symbol=TOKEN"), root
            )
        self.assertEqual(result.status, "error")
        self.assertIn("prohibited credential-like pattern", result.detail)

    def test_escaping_the_repository_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = evidence.verify_citation(
                evidence.parse_citation("../../etc/passwd#symbol=root"), Path(tmp)
            )
        self.assertEqual(result.status, "error")


class UrlReachabilityTriStateTest(unittest.TestCase):
    """A dead link and an unreachable network are different facts.

    Conflating them made the link stage nondeterministic — the same commit
    produced one failure and two passes within minutes. A required check that
    flaps teaches people to ignore it.
    """

    def test_http_error_status_is_a_definitive_dead_link(self) -> None:
        import urllib.error

        def fail(*_a, **_k):
            raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)

        with unittest.mock.patch.object(evidence.urllib.request, "urlopen", fail):
            self.assertIs(evidence._url_resolves("https://example.com/gone"), False)

    def test_transport_failure_is_indeterminate_not_dead(self) -> None:
        with unittest.mock.patch.object(
            evidence.urllib.request, "urlopen", side_effect=TimeoutError()
        ), unittest.mock.patch.object(evidence.time, "sleep", lambda _s: None):
            self.assertIsNone(evidence._url_resolves("https://example.com/slow"))

    def test_transport_failure_is_retried_before_giving_up(self) -> None:
        with unittest.mock.patch.object(
            evidence.urllib.request, "urlopen", side_effect=TimeoutError()
        ) as opener, unittest.mock.patch.object(
            evidence.time, "sleep", lambda _s: None
        ):
            evidence._url_resolves("https://example.com/slow")
        self.assertEqual(opener.call_count, evidence._URL_CHECK_ATTEMPTS)

    def test_unreachable_url_does_not_become_a_hard_error(self) -> None:
        with unittest.mock.patch.object(
            evidence, "_url_resolves", return_value=None
        ):
            result = evidence.verify_citation(
                evidence.parse_citation("https://example.com/spec"),
                Path("."),
                check_links=True,
            )
        self.assertEqual(result.status, "unverified")
        self.assertIn("network failure", result.detail)

    def test_a_genuinely_dead_link_still_fails_hard(self) -> None:
        """The retry must not have turned the check into a no-op."""
        with unittest.mock.patch.object(
            evidence, "_url_resolves", return_value=False
        ):
            result = evidence.verify_citation(
                evidence.parse_citation("https://example.com/gone"),
                Path("."),
                check_links=True,
            )
        self.assertEqual(result.status, "error")


class AbsentPathCitationTest(unittest.TestCase):
    """#2013: evidence that something is NOT there.

    Absence claims were the single largest class of unverifiable corpus FACTs
    (94 of 213) and had no citable form at all. Absence is verifiable — a path
    either is or is not in a tree — so this form can genuinely fail.
    """

    REPO_ROOT = Path(__file__).resolve().parents[4]

    @classmethod
    def setUpClass(cls) -> None:
        import subprocess

        cls.HEAD = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cls.REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()

    def _verify(self, citation: str) -> evidence.VerificationResult:
        return evidence.verify_citation(
            evidence.parse_citation(citation), self.REPO_ROOT
        )

    def test_parses_path_and_commit(self) -> None:
        parsed = evidence.parse_citation(f"absent:some/where@{self.HEAD}")
        self.assertEqual(parsed.kind, evidence.EvidenceKind.ABSENT_PATH)
        self.assertEqual(parsed.path, "some/where")
        self.assertEqual(parsed.commit, self.HEAD)

    def test_genuinely_absent_path_verifies_ok(self) -> None:
        result = self._verify(
            f"absent:launchpad/docs/corpus/no-such-subtree@{self.HEAD}"
        )
        self.assertEqual(result.status, "ok")

    def test_present_path_makes_the_claim_an_error(self) -> None:
        """The failure mode that makes this form worth having: a claim that
        something is absent, when it is right there."""
        result = self._verify(f"absent:launchpad/docs/corpus/AGENTS.md@{self.HEAD}")
        self.assertEqual(result.status, "error")
        self.assertIn("exists at the pinned commit", result.detail)

    def test_unavailable_commit_is_not_treated_as_absence(self) -> None:
        """The vacuity guard. A path is missing from a tree this checkout does
        not have for reasons that have nothing to do with the claim, so absence
        must not confirm itself against a tree nobody looked at."""
        result = self._verify(
            "absent:launchpad/docs/corpus/AGENTS.md"
            "@0123456789abcdef0123456789abcdef01234567"
        )
        self.assertEqual(result.status, "unverified")
        self.assertIn("does not have", result.detail)

    def test_requires_a_full_sha_pin(self) -> None:
        """Absence is only meaningful relative to a specific tree, so an
        unpinned or branch-pinned form is not this citation at all."""
        for unpinned in (
            "absent:some/where@origin/launchpad",
            "absent:some/where@338b4d0",
            "absent:some/where",
        ):
            with self.subTest(citation=unpinned):
                parsed = evidence.parse_citation(unpinned)
                self.assertNotEqual(parsed.kind, evidence.EvidenceKind.ABSENT_PATH)

    def test_credential_guard_applies(self) -> None:
        result = self._verify(f"absent:.env.local@{self.HEAD}")
        self.assertEqual(result.status, "error")
        self.assertIn("prohibited credential-like pattern", result.detail)

    def test_escaping_the_repository_is_refused(self) -> None:
        result = self._verify(f"absent:../../etc/passwd@{self.HEAD}")
        self.assertEqual(result.status, "error")

    def test_absolute_path_is_refused(self) -> None:
        result = self._verify(f"absent:/etc/passwd@{self.HEAD}")
        self.assertEqual(result.status, "error")


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

    def test_missing_bare_sha_is_not_an_error_in_a_shallow_clone(self) -> None:
        """A shortened history is exactly what makes an old commit unreachable
        here but real upstream, so absence proves nothing about the citation."""
        with unittest.mock.patch.object(
            evidence, "_is_shallow_repository", return_value=True
        ):
            result = self._verify(
                "git_show('0123456789abcdef0123456789abcdef01234567"
                ":launchpad/docs/corpus/AGENTS.md') -> a heading"
            )
        self.assertEqual(result.status, "unverified")
        self.assertIn("shallow", result.detail)

    def test_missing_branch_name_is_conclusive_even_in_a_shallow_clone(self) -> None:
        """Shallowness truncates history depth, not the ref list. If this
        checkout holds refs for the remote, the branch list was fetched and a
        name absent from it is genuinely gone -- confirmed against the remote
        for the refs this branch reports."""
        with unittest.mock.patch.object(
            evidence, "_is_shallow_repository", return_value=True
        ):
            result = self._verify(
                "git_ls_tree(ref='origin/task/0000-branch-deleted-long-ago', "
                "path='launchpad/docs/corpus') -> AGENTS.md"
            )
        self.assertEqual(result.status, "error")

    def test_this_checkout_holds_remote_refs_so_the_error_path_is_live(self) -> None:
        """Guards the error-path tests from passing vacuously: without remote
        refs every one of them would exercise the shallow downgrade instead of
        the behaviour it names."""
        self.assertTrue(
            evidence._remote_tracking_refs_present(self.REPO_ROOT, "origin")
        )

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


class GrepReplayVerifierTest(unittest.TestCase):
    """DECISION-1: replay only what is pinned, and only ever to fail.

    A grep citation is replayed only when it pins `ref=` to a full 40-hex SHA
    present locally. Everything else stays blocking without spawning anything.
    A matching replay confirms the match count -- not the claim the count was
    cited to support -- so it still returns `unverified`, never `ok`.
    """

    REPO_ROOT = Path(__file__).resolve().parents[4]

    # Assembled at runtime so the literal never appears contiguously in this
    # file. Written out, it would be committed into the very tree these tests
    # grep, and every "absent pattern" case would start finding itself -- the
    # same self-reference trap that made invariants.md cite a line that moved.
    ABSENT = "nx" + "9f4c2" + "_absent_marker"

    @classmethod
    def setUpClass(cls) -> None:
        import subprocess

        cls.HEAD = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cls.REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def _verify(self, citation: str) -> evidence.VerificationResult:
        return evidence.verify_citation(
            evidence.parse_citation(citation), self.REPO_ROOT
        )

    def test_absence_claim_contradicted_by_replay_is_an_error(self) -> None:
        result = self._verify(
            f"grep_recursive('EvidenceKind', "
            f"path='launchpad/project-intelligence/corpus', ref='{self.HEAD}') "
            f"-> zero matches"
        )
        self.assertEqual(result.status, "error")
        self.assertIn("finds matches", result.detail)

    def test_presence_claim_contradicted_by_replay_is_an_error(self) -> None:
        result = self._verify(
            f"grep_recursive('{self.ABSENT}', "
            f"path='launchpad/project-intelligence/corpus', ref='{self.HEAD}') "
            f"-> 3 matches"
        )
        self.assertEqual(result.status, "error")
        self.assertIn("finds none", result.detail)

    def test_agreeing_replay_still_blocks_and_never_passes(self) -> None:
        result = self._verify(
            f"grep_recursive('{self.ABSENT}', "
            f"path='launchpad/project-intelligence/corpus', ref='{self.HEAD}') "
            f"-> zero matches"
        )
        self.assertEqual(result.status, "unverified")
        self.assertIn("was not compared", result.detail)

    def test_missing_path_at_pinned_commit_is_not_replayed(self) -> None:
        """The vacuous-pass guard. Without it, a mistyped path makes every
        absence claim trivially true -- git grep finds nothing in a directory
        that is not there, and the citation would look confirmed."""
        result = self._verify(
            f"grep_recursive('anything', path='no/such/directory/at/all', "
            f"ref='{self.HEAD}') -> zero matches"
        )
        self.assertEqual(result.status, "unverified")
        self.assertIn("does not exist at the pinned commit", result.detail)

    def test_regex_alternation_in_the_pattern_is_replayed_not_refused(self) -> None:
        """`|` is legitimate in a grep pattern and must not trip the shell
        guard -- the pattern reaches git as an argument, never a shell string.
        If this starts failing, the guard has become over-broad and the
        pinned citations silently stop being checked."""
        result = self._verify(
            f"grep_case_insensitive('EvidenceKind|ParsedCitation', "
            f"path='launchpad/project-intelligence/corpus', ref='{self.HEAD}') "
            f"-> zero matches"
        )
        self.assertEqual(result.status, "error")

    def test_pattern_beginning_with_a_dash_is_not_read_as_an_option(self) -> None:
        result = self._verify(
            f"grep_recursive('--count', path='launchpad/project-intelligence', "
            f"ref='{self.HEAD}') -> zero matches"
        )
        self.assertIn(result.status, {"error", "unverified"})

    def test_unpinned_citation_is_not_replayed(self) -> None:
        for unpinned in (
            "grep_recursive('needle', path='launchpad', ref='origin/launchpad') -> zero matches",
            "grep_recursive('needle', path='launchpad') -> zero matches",
            "grep_recursive('needle', path='launchpad', ref='338b4d0') -> zero matches",
        ):
            with self.subTest(citation=unpinned):
                with unittest.mock.patch.object(
                    evidence.subprocess, "run", side_effect=AssertionError("spawned")
                ):
                    result = self._verify(unpinned)
                self.assertEqual(result.status, "unverified")
                self.assertIn("not pinned", result.detail)

    def test_uncheckable_assertion_is_not_replayed(self) -> None:
        with unittest.mock.patch.object(
            evidence.subprocess, "run", side_effect=AssertionError("spawned")
        ):
            result = self._verify(
                f"grep_recursive('needle', path='launchpad', ref='{self.HEAD}') "
                f"-> see the discussion in the linked issue"
            )
        self.assertEqual(result.status, "unverified")
        self.assertIn("no checkable match verdict", result.detail)

    def test_shell_metacharacter_in_path_is_refused_without_spawning(self) -> None:
        with unittest.mock.patch.object(
            evidence.subprocess, "run", side_effect=AssertionError("spawned")
        ):
            result = self._verify(
                f"grep_recursive('needle', path='launchpad; rm -rf /', "
                f"ref='{self.HEAD}') -> zero matches"
            )
        self.assertEqual(result.status, "unverified")
        self.assertIn("shell metacharacter", result.detail)

    def test_bracketed_path_list_keeps_every_path(self) -> None:
        """Regression: `[^,]+` stopped at the first comma inside `paths=[...]`,
        so only the first path was searched. Searching less than was cited
        makes an absence claim look true -- the one direction this verifier
        must never fail in."""
        parsed = evidence.parse_citation(
            "grep_recursive(pattern='reply_count', "
            "paths=['crates/buzz-db/src', 'crates/buzz-relay/src'], "
            "ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> 2 matches"
        )
        citation = evidence._parse_grep_citation(parsed)
        self.assertEqual(
            citation["paths"], ["crates/buzz-db/src", "crates/buzz-relay/src"]
        )

    def test_space_separated_path_value_keeps_every_path(self) -> None:
        parsed = evidence.parse_citation(
            "grep_recursive_case_insensitive('30350|push_lease', "
            "paths='mobile/lib desktop/src', ref='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') "
            "-> no matches"
        )
        citation = evidence._parse_grep_citation(parsed)
        self.assertEqual(citation["paths"], ["mobile/lib", "desktop/src"])

    def test_glob_scoped_grep_is_reported_as_such_and_not_replayed(self) -> None:
        with unittest.mock.patch.object(
            evidence.subprocess, "run", side_effect=AssertionError("spawned")
        ):
            result = self._verify(
                f"grep_recursive('ContentActioned', glob='**/*.rs', "
                f"ref='{self.HEAD}') -> zero matches"
            )
        self.assertEqual(result.status, "unverified")
        self.assertIn("scoped by a glob", result.detail)

    def test_no_input_ever_verifies_ok(self) -> None:
        """The load-bearing guarantee of DECISION-1."""
        for citation in (
            f"grep_recursive('EvidenceKind', path='launchpad', ref='{self.HEAD}') -> zero matches",
            f"grep_recursive('{self.ABSENT}', path='launchpad', ref='{self.HEAD}') -> zero matches",
            f"grep_recursive('x', path='no/such/dir', ref='{self.HEAD}') -> zero matches",
            "grep_recursive('x', path='launchpad') -> zero matches",
            "grep_repo('needle') -> no matches",
        ):
            with self.subTest(citation=citation):
                self.assertNotEqual(self._verify(citation).status, "ok")


class UnsupportedToolFamilyDetailTest(unittest.TestCase):
    """Step 5: an unsupported family says which family it is and why, instead
    of every tool result sharing one generic string."""

    REPO_ROOT = Path(__file__).resolve().parents[4]

    def _detail(self, citation: str) -> str:
        return evidence.verify_citation(
            evidence.parse_citation(citation), self.REPO_ROOT
        ).detail

    def test_families_are_named_distinctly(self) -> None:
        details = {
            self._detail("shell('ls -la') -> three entries"),
            self._detail("webfetch('https://example.com/spec') -> 200 OK"),
            self._detail("gh_pr_list('--state open') -> 4 open"),
            self._detail("git_log_oneline('-n 5') -> five commits"),
        }
        self.assertEqual(len(details), 4, "each family needs its own reason")

    def test_shell_refusal_says_why_it_is_permanent(self) -> None:
        detail = self._detail("shell('cat /etc/passwd') -> some output")
        self.assertIn("execute text", detail)
        self.assertIn("none is planned", detail)

    def test_a_detail_never_echoes_the_citation(self) -> None:
        """Details print on passing runs. Citation text is untrusted document
        prose, so a detail that interpolated it would put arbitrary content --
        including anything credential-shaped -- into validator output."""
        for citation, secret in (
            ("shell('export TOKEN=hunter2seekrit') -> exported", "hunter2seekrit"),
            ("webfetch('https://example.com/?key=abcd1234xyz') -> 200", "abcd1234xyz"),
            ("gh_api('/repos/o/r?token=zzsecretzz') -> 200", "zzsecretzz"),
            ("git_log('--author=nobody@example.com') -> none", "nobody@example.com"),
            ("unknown_tool('payload_marker_9987') -> whatever", "payload_marker_9987"),
        ):
            with self.subTest(citation=citation):
                self.assertNotIn(secret, self._detail(citation))

    def test_every_detail_comes_from_the_fixed_constant_set(self) -> None:
        known = {detail for _, detail in evidence._UNSUPPORTED_TOOL_FAMILIES}
        known.add(evidence.UNVERIFIABLE_KIND_DETAIL)
        for citation in (
            "shell('x') -> y",
            "webfetch('https://example.com') -> y",
            "gh_issue_view('12') -> open",
            "git_diff_name_only('a..b') -> two files",
            "yaml.safe_load('config.yml') -> a mapping",
            "path_exists('somewhere') -> true",
        ):
            with self.subTest(citation=citation):
                self.assertIn(self._detail(citation), known)

    def test_unrecognised_tool_keeps_the_shared_detail(self) -> None:
        self.assertEqual(
            self._detail("some_novel_tool('x') -> y"),
            evidence.UNVERIFIABLE_KIND_DETAIL,
        )

    def test_naming_a_family_never_turns_it_into_a_pass(self) -> None:
        """Step 5 improves reporting only. A better message must not become a
        weaker verdict -- every one of these still blocks."""
        for citation in (
            "shell('x') -> y",
            "webfetch('https://example.com') -> y",
            "gh_pr_list('') -> y",
            "git_log('') -> y",
            "some_novel_tool('x') -> y",
            "source_symbol -> target_symbol (1 hop)",
        ):
            with self.subTest(citation=citation):
                result = evidence.verify_citation(
                    evidence.parse_citation(citation), self.REPO_ROOT
                )
                self.assertEqual(result.status, "unverified")


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
