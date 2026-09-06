"""Unit tests for canonical-corpus staleness detection -- issue #556.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test below builds its own throwaway fixture -- either a plain temp
directory (no git needed, for the pure recorded-revision-ladder logic) or a
hermetic throwaway git repository under `tempfile.TemporaryDirectory`, per
`test_inventory.py`'s stated rule. Fixture git repos never read this
repository's history or any global gitconfig: `GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_SYSTEM` are pointed at `/dev/null`, `HOME` is pointed at the
fixture directory itself (so no `~/.gitconfig` is even reachable), and every
invocation pins `user.name`/`user.email`/`commit.gpgsign=false` with `-c`
rather than writing to any config file. `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`
are fixed per commit so the same fixture yields the same SHAs -- and the same
report -- on every run. CI's depth-1 checkout is the reason this matters: a
test pinned to a real corpus SHA would pass locally and fail in CI for a
reason that looks nothing like its cause.

ONE test is deliberately outside the fixture-only rule, the same carve-out
`test_validate.py` documents for itself: `RealCorpusSmokeTest` reads the real
`launchpad/docs/corpus/` tree and the real git history of this repository. It
exists to catch a regression against real committed content no fixture can
stand in for, and its own docstring says what it can and cannot prove.

The plan this module implements measured "94 nodes, distribution {1: 93, 2:
1}" against a corpus snapshot from earlier the same day. Corpus batches have
merged into `origin/launchpad` since, and the real count as measured directly
against this checkout on 2026-09-03 is 205 nodes, distribution {1: 204, 2: 1}
by statement-match count, {1: 202, 2: 1, 3: 2} by distinct commit-citation
count -- `standards/linking.md` remains the only node whose statement count
is not exactly 1. `RealCorpusSmokeTest` no longer hardcodes that count: it
compares `discover_nodes()`'s result against a fresh, independently-computed
walk of the same corpus root, the same precedent `test_validate.py`'s own
real-corpus test already set, so growth in the corpus strengthens rather than
breaks the test.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

_CORPUS_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=_CORPUS_DIR,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validate = _load("corpus_validate_for_stale_tests", _CORPUS_DIR / "validate.py")
stale = _load("corpus_stale", _CORPUS_DIR / "stale.py")


# ---------------------------------------------------------------------------
# Hermetic git fixture harness -- STEP 6. Lives only in this test file, never
# in stale.py itself.
# ---------------------------------------------------------------------------

_GIT_IDENTITY = [
    "-c", "user.name=Corpus Stale Test",
    "-c", "user.email=corpus-stale-test@example.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "init.defaultBranch=main",
]


def _git(args: list[str], cwd: Path, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    # Isolation, belt-and-braces: GIT_CONFIG_GLOBAL/SYSTEM point nowhere, and
    # HOME points at the fixture itself, so there is no ~/.gitconfig to find
    # even if some git build ignores the GIT_CONFIG_* overrides.
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    env["HOME"] = str(cwd)
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        ["git", *_GIT_IDENTITY, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {args} failed in {cwd}: {result.stderr}")
    return result


def init_repo(root: Path) -> None:
    _git(["init", "-q"], root)


def commit_all(root: Path, message: str, when: str) -> str:
    """Stage everything and commit with fixed author/committer dates -- the
    same fixture yields the same SHA on every run.

    `--allow-empty`: several "base" commits in this file exist only to give a
    later commit something to record a revision against and stage no file of
    their own -- an ordinary `git commit` refuses those with nothing to
    commit. Any real staged changes still commit normally; this only removes
    the requirement that there be one.
    """
    _git(["add", "-A"], root)
    _git(
        ["commit", "-q", "--allow-empty", "-m", message],
        root,
        extra_env={"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when},
    )
    return _git(["rev-parse", "HEAD"], root).stdout.strip()


def write_node(root: Path, rel_path: str, node_id: str, evidence_entries: list[dict]) -> None:
    """Write a schema-valid corpus node -- id/type/status/origin/audiences are
    fixed to values `node.schema.json` accepts; only `id` and `evidence` vary
    per fixture."""
    lines = [
        "---",
        f"id: {node_id}",
        "type: governance",
        "status: active",
        "origin: launchpad",
        "audiences:",
        "  - agent",
        "evidence:",
    ]
    for entry in evidence_entries:
        statement = entry["statement"].replace('"', '\\"')
        lines.append(f'  - statement: "{statement}"')
        lines.append(f'    entry_class: {entry.get("entry_class", "FACT")}')
        citations = entry.get("evidence") or []
        if citations:
            lines.append("    evidence:")
            for citation in citations:
                escaped = citation.replace('"', '\\"')
                lines.append(f'      - "{escaped}"')
    lines.append("---")
    lines.append("")
    lines.append(f"# {node_id}")
    lines.append("")
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def provenance_entry(sha: str) -> dict:
    return {
        "statement": f"This node was authored and checked against repository revision {sha}.",
        "entry_class": "FACT",
        "evidence": [f"commit {sha}"],
    }


def _single_node(root: Path):
    nodes = stale.discover_nodes(root)
    assert len(nodes) == 1, f"expected exactly one node, found {len(nodes)}"
    return nodes[0]


# ---------------------------------------------------------------------------
# STEP 6 -- harness smoke test
# ---------------------------------------------------------------------------


class GitFixtureHarnessTest(unittest.TestCase):
    def test_two_commit_repo_with_a_cited_file_parses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "cited.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-two-commit",
                [
                    provenance_entry(sha_a),
                    {
                        "statement": "Cites a fixture file.",
                        "entry_class": "FACT",
                        "evidence": ["cited.txt"],
                    },
                ],
            )
            commit_all(root, "commit B", "2020-01-02T00:00:00")

            log = _git(["log", "--oneline"], root).stdout.strip().splitlines()
            self.assertEqual(len(log), 2)

            node = _single_node(root)
            self.assertEqual(node.id, "fixture-two-commit")


# ---------------------------------------------------------------------------
# STEP 2 -- recorded-revision ladder. No git needed: this logic runs purely
# over parsed front matter.
# ---------------------------------------------------------------------------


class RecordedRevisionLadderTest(unittest.TestCase):
    def test_rung3_fires_on_two_distinct_shas_with_no_single_statement_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha_one = "a" * 40
            sha_two = "b" * 40
            write_node(
                root,
                "ambiguous.md",
                "fixture-ambiguous",
                [
                    {
                        "statement": "Checked against one possible revision, never resolved to a single one.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha_one}"],
                    },
                    {
                        "statement": "A second, different revision was also recorded here.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha_two}"],
                    },
                ],
            )
            node = _single_node(root)
            result = stale.extract_recorded_revision(node)
            self.assertIsNone(result.sha)
            self.assertEqual(result.reason, "ambiguous or absent recorded revision")

    def test_rung2_resolves_the_real_linking_md_shape(self) -> None:
        # Reproduces standards/linking.md's real structure: two evidence
        # entries whose `statement` BOTH match the rung-1 pattern (so rung 1's
        # "exactly one ENTRY" check fails and falls through), citing the SAME
        # sha, but only one entry's citation is a structured `commit <sha>` --
        # the other's citation is a bare path, which does not count toward
        # rung 2's tally. Must resolve via rung 2 to that single sha, never
        # rung 3 `unestablished`.
        sha = "919886b4192df6251de50c547548ecae5d85afce"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_node(
                root,
                "linking-shape.md",
                "fixture-linking-shape",
                [
                    provenance_entry(sha),
                    {
                        "statement": (
                            "AGENTS.md's own front matter states this node was "
                            f"authored and checked against repository revision {sha}, "
                            "the same revision this node records."
                        ),
                        "entry_class": "FACT",
                        "evidence": ["AGENTS.md"],
                    },
                ],
            )
            node = _single_node(root)
            result = stale.extract_recorded_revision(node)
            self.assertEqual(result.sha, sha)
            self.assertIsNone(result.reason)

    def test_rung2_abbreviated_and_full_citation_of_same_commit_is_not_ambiguous(
        self,
    ) -> None:
        # The same commit cited once abbreviated and once in full must count
        # as ONE distinct SHA toward rung 2's tally, never two -- otherwise
        # this falls through to rung 3 `unestablished` for a commit that was
        # never actually ambiguous. Neither entry's statement matches the
        # rung-1 pattern, so this can only resolve via rung 2.
        sha = "d" * 40
        abbreviated = sha[:7]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_node(
                root,
                "abbreviated-and-full.md",
                "fixture-abbreviated-and-full",
                [
                    {
                        "statement": "Cites the commit in full.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha}"],
                    },
                    {
                        "statement": "Cites the identical commit, abbreviated.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {abbreviated}"],
                    },
                ],
            )
            node = _single_node(root)
            result = stale.extract_recorded_revision(node)
            self.assertEqual(result.sha, sha)
            self.assertIsNone(result.reason)

    def test_rung1_exactly_one_matching_statement_resolves_directly(self) -> None:
        sha = "c" * 40
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_node(root, "ordinary.md", "fixture-ordinary", [provenance_entry(sha)])
            node = _single_node(root)
            result = stale.extract_recorded_revision(node)
            self.assertEqual(result.sha, sha)
            self.assertIsNone(result.reason)


# ---------------------------------------------------------------------------
# `normalize_file_citation` -- STEP 2's own function, public and stable-
# signature for #635's benefit (see its docstring), but previously exercised
# only indirectly through `evaluate_citation`. No git/fixture needed: it is a
# pure string decision over CONTRACT.md's citation shapes.
# ---------------------------------------------------------------------------


class NormalizeFileCitationTest(unittest.TestCase):
    def test_bare_path_returns_itself(self) -> None:
        self.assertEqual(
            stale.normalize_file_citation("launchpad/AGENTS.md"),
            "launchpad/AGENTS.md",
        )

    def test_single_line_position_strips_to_the_path(self) -> None:
        self.assertEqual(stale.normalize_file_citation("path/to/file.py:12"), "path/to/file.py")

    def test_line_range_position_strips_to_the_path(self) -> None:
        self.assertEqual(
            stale.normalize_file_citation("path/to/file.py:12-20"), "path/to/file.py"
        )

    def test_commit_citation_is_not_a_file_shape(self) -> None:
        self.assertIsNone(stale.normalize_file_citation("commit " + "a" * 40))

    def test_url_citation_is_not_a_file_shape(self) -> None:
        self.assertIsNone(stale.normalize_file_citation("https://example.invalid/x"))

    def test_graph_edge_citation_is_not_a_file_shape(self) -> None:
        self.assertIsNone(
            stale.normalize_file_citation("some_symbol -> other_symbol (1 hop)")
        )

    def test_empty_citation_returns_none(self) -> None:
        self.assertIsNone(stale.normalize_file_citation("   "))


# ---------------------------------------------------------------------------
# STEP 4 -- the four fail-closed gates, plus the verdict-precedence check.
# ---------------------------------------------------------------------------


class GateTest(unittest.TestCase):
    def test_gate1_recorded_sha_absent_from_repo_is_unestablished(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            never_committed_sha = "f" * 40
            write_node(root, "node.md", "fixture-gate1", [provenance_entry(never_committed_sha)])
            head_sha = commit_all(root, "only commit", "2020-01-01T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            self.assertEqual(recorded.sha, never_committed_sha)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            self.assertIn("absent from this repository", verdict.findings[0].reason)

    def test_gate2_divergent_branch_is_unestablished(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "base.txt").write_text("base\n")
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            _git(["checkout", "-q", "-b", "branch-a"], root)
            (root / "a.txt").write_text("a\n")
            sha_a = commit_all(root, "branch a commit", "2020-01-02T00:00:00")
            _git(["checkout", "-q", "-b", "branch-b", base_sha], root)
            write_node(root, "node.md", "fixture-gate2", [provenance_entry(sha_a)])
            head_sha = commit_all(root, "branch b commit", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            self.assertEqual(recorded.sha, sha_a)
            self.assertFalse(stale.is_ancestor(sha_a, head_sha, root))
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            self.assertIn("not an ancestor", verdict.findings[0].reason)

    def test_gate3_path_never_existed_at_recorded_revision_is_unestablished(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-gate3",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a file that never existed at the recorded revision.",
                        "entry_class": "FACT",
                        "evidence": ["never-existed.txt"],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            for finding in verdict.findings:
                self.assertNotIn("never-existed.txt", finding.citation)
                self.assertIn("does not resolve to a real file", finding.reason)

    def test_gate4_prohibited_citation_is_unestablished_and_not_echoed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-gate4-credential",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a credential-shaped path.",
                        "entry_class": "FACT",
                        "evidence": ["id_rsa"],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            for finding in verdict.findings:
                self.assertNotIn("id_rsa", finding.citation)
                self.assertTrue(finding.citation.startswith("evidence entry"))
                self.assertIn("prohibited credential-like pattern", finding.reason)

    def test_gate4_escaping_path_is_unestablished_and_not_echoed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-gate4-escaping",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a path that escapes the repository.",
                        "entry_class": "FACT",
                        "evidence": ["../../../../etc/passwd"],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            for finding in verdict.findings:
                self.assertNotIn("passwd", finding.citation)
                self.assertIn("resolves outside the repository", finding.reason)

    def test_one_unestablished_citation_prevents_fresh_even_with_clean_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "clean.txt").write_text("v1\n")
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-mixed",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a clean, unchanged file.",
                        "entry_class": "FACT",
                        "evidence": ["clean.txt"],
                    },
                    {
                        "statement": "Also cites something this checker cannot open.",
                        "entry_class": "FACT",
                        "evidence": ["commit " + "c" * 40],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            self.assertNotEqual(verdict.status, "fresh")
            self.assertEqual(len(verdict.findings), 1)
            self.assertIn("commit reference", verdict.findings[0].reason)


# ---------------------------------------------------------------------------
# STEP 5 -- finding shape and the redaction-timing fix.
# ---------------------------------------------------------------------------


class FindingShapeTest(unittest.TestCase):
    def test_stale_finding_names_node_path_and_two_shas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "moved.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-stale-shape",
                [
                    provenance_entry(sha_a),
                    {
                        "statement": "Cites a file that will move.",
                        "entry_class": "FACT",
                        "evidence": ["moved.txt"],
                    },
                ],
            )
            commit_all(root, "add node", "2020-01-02T00:00:00")
            (root / "moved.txt").write_text("v2\n")
            sha_b = commit_all(root, "commit B", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, sha_b, root)
            self.assertEqual(verdict.status, "stale")
            stale_findings = [f for f in verdict.findings if f.status == "stale"]
            self.assertEqual(len(stale_findings), 1)
            finding = stale_findings[0]
            self.assertEqual(finding.node_id, "fixture-stale-shape")
            self.assertEqual(finding.citation, "moved.txt")
            self.assertEqual(finding.recorded_revision, sha_a)
            self.assertEqual(finding.current_revision, sha_b)
            self.assertNotEqual(finding.recorded_revision, finding.current_revision)

    def test_credential_shaped_citation_names_position_never_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-redacted",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a credential-shaped path.",
                        "entry_class": "FACT",
                        "evidence": ["secrets/id_ed25519"],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(len(verdict.findings), 1)
            finding = verdict.findings[0]
            self.assertEqual(finding.status, "unestablished")
            self.assertNotIn("id_ed25519", finding.citation)
            self.assertEqual(finding.citation, "evidence entry 2, citation 1")

    def test_deleted_file_after_recorded_revision_is_stale_and_names_the_path(self) -> None:
        # The redaction fix this step exists for: a citation resolved to a
        # real file AT THE RECORDED REVISION, then deleted before `head`, must
        # still be named -- checking CURRENT-tree existence would silently
        # redact exactly this case.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "doomed.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-deleted",
                [
                    provenance_entry(sha_a),
                    {
                        "statement": "Cites a file that will be deleted.",
                        "entry_class": "FACT",
                        "evidence": ["doomed.txt"],
                    },
                ],
            )
            commit_all(root, "add node", "2020-01-02T00:00:00")
            (root / "doomed.txt").unlink()
            sha_b = commit_all(root, "delete doomed.txt", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            self.assertFalse((root / "doomed.txt").exists())  # gone from the CURRENT tree
            verdict = stale.evaluate_node(node, recorded, sha_b, root)
            self.assertEqual(verdict.status, "stale")
            stale_findings = [f for f in verdict.findings if f.status == "stale"]
            self.assertEqual(len(stale_findings), 1)
            self.assertEqual(stale_findings[0].citation, "doomed.txt")


# ---------------------------------------------------------------------------
# STEP 7 -- the two DoD fixtures, plus the six named traps. The plan's own
# done-when says "seven bullets above"; the plan's own enumerated list under
# "Then the traps" is six items, plus the two DoD fixtures named just above
# it, which is eight distinguishable behaviors, not seven. Rather than drop
# one to force the count to match, every one of the eight is given its own
# test method below -- flagged in the build report as a discrepancy in the
# plan's own bullet count, not resolved silently.
# ---------------------------------------------------------------------------


class DodFixturesAndTrapsTest(unittest.TestCase):
    def test_known_stale_fixture_proves_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "watched.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-known-stale",
                [
                    provenance_entry(sha_a),
                    {
                        "statement": "Cites a file that will be modified.",
                        "entry_class": "FACT",
                        "evidence": ["watched.txt"],
                    },
                ],
            )
            commit_all(root, "add node", "2020-01-02T00:00:00")
            (root / "watched.txt").write_text("v2\n")
            sha_b = commit_all(root, "modify watched.txt", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, sha_b, root)
            self.assertEqual(verdict.status, "stale")
            finding = [f for f in verdict.findings if f.status == "stale"][0]
            self.assertEqual(finding.citation, "watched.txt")
            self.assertEqual(finding.recorded_revision, sha_a)
            self.assertEqual(finding.current_revision, sha_b)

    def test_same_revision_fixture_is_fresh_with_zero_findings(self) -> None:
        # Assert the positive too -- "no errors" alone can't distinguish a
        # genuinely clean run from a run that discovered nothing, which
        # test_validate.py documents learning the hard way.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "steady.txt").write_text("v1\n")
            head_sha = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-same-revision",
                [
                    provenance_entry(head_sha),
                    {
                        "statement": "Cites a file that has not changed.",
                        "entry_class": "FACT",
                        "evidence": ["steady.txt"],
                    },
                ],
            )
            # `head_sha` is the commit BEFORE the node file itself was added,
            # deliberately: the node's own file must not be part of what it
            # cites, or adding it would itself look like a change against the
            # recorded revision. Re-commit so the node exists at `head`, but
            # keep the recorded revision equal to the commit that already
            # contains `steady.txt` unchanged going forward.
            final_head = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            self.assertEqual(recorded.sha, head_sha)
            verdict = stale.evaluate_node(node, recorded, final_head, root)
            self.assertEqual(verdict.status, "fresh")
            self.assertEqual(len(verdict.findings), 0)

    def test_trap_unnormalized_position_citation_does_not_come_back_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "changed.py").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-unnormalized-trap",
                [
                    provenance_entry(sha_a),
                    {
                        "statement": "Cites a specific line of a file that will change.",
                        "entry_class": "FACT",
                        "evidence": ["changed.py:127"],
                    },
                ],
            )
            commit_all(root, "add node", "2020-01-02T00:00:00")
            (root / "changed.py").write_text("v2\n")
            sha_b = commit_all(root, "modify changed.py", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, sha_b, root)
            # If the trailing ":127" were passed straight to `git diff` un-
            # normalized, the pathspec would resolve nothing, print empty
            # output, and this would come back "fresh" despite the real
            # change -- AGENTS.md's documented dangerous case.
            self.assertNotEqual(verdict.status, "fresh")
            self.assertEqual(verdict.status, "stale")
            self.assertEqual(verdict.findings[0].citation, "changed.py")

    def test_trap_recorded_sha_absent_is_unestablished_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            absent_sha = "e" * 40
            write_node(root, "node.md", "fixture-absent-trap", [provenance_entry(absent_sha)])
            head_sha = commit_all(root, "only commit", "2020-01-01T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertNotEqual(verdict.status, "fresh")
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            self.assertIn("absent from this repository", verdict.findings[0].reason)

    def test_trap_divergent_branch_is_unestablished_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "base.txt").write_text("base\n")
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            _git(["checkout", "-q", "-b", "branch-a"], root)
            (root / "a.txt").write_text("a\n")
            sha_a = commit_all(root, "branch a commit", "2020-01-02T00:00:00")
            _git(["checkout", "-q", "-b", "branch-b", base_sha], root)
            write_node(root, "node.md", "fixture-divergent-trap", [provenance_entry(sha_a)])
            head_sha = commit_all(root, "branch b commit", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertNotEqual(verdict.status, "fresh")
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            self.assertIn("not an ancestor", verdict.findings[0].reason)

    def test_trap_path_never_existed_is_unestablished_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-never-existed-trap",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a file that never existed at the recorded revision.",
                        "entry_class": "FACT",
                        "evidence": ["ghost.txt"],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertNotEqual(verdict.status, "fresh")
            self.assertEqual(verdict.status, "unestablished")
            self.assertEqual(len(verdict.findings), 1)
            self.assertIn("does not resolve to a real file", verdict.findings[0].reason)

    def test_trap_deleted_or_renamed_file_is_stale_with_path_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "renamed_from.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "node.md",
                "fixture-renamed-trap",
                [
                    provenance_entry(sha_a),
                    {
                        "statement": "Cites a file that will be renamed away.",
                        "entry_class": "FACT",
                        "evidence": ["renamed_from.txt"],
                    },
                ],
            )
            commit_all(root, "add node", "2020-01-02T00:00:00")
            _git(["mv", "renamed_from.txt", "renamed_to.txt"], root)
            sha_b = commit_all(root, "rename the cited file", "2020-01-03T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            verdict = stale.evaluate_node(node, recorded, sha_b, root)
            self.assertEqual(verdict.status, "stale")
            stale_findings = [f for f in verdict.findings if f.status == "stale"]
            self.assertEqual(len(stale_findings), 1)
            self.assertEqual(stale_findings[0].citation, "renamed_from.txt")

    def test_trap_unopenable_shapes_are_unestablished_and_own_entry_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            base_sha = commit_all(root, "base", "2020-01-01T00:00:00")
            other_commit_sha = "d" * 40
            write_node(
                root,
                "node.md",
                "fixture-unopenable-shapes",
                [
                    provenance_entry(base_sha),
                    {
                        "statement": "Cites a different commit entirely, not this node's own provenance.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {other_commit_sha}"],
                    },
                    {
                        "statement": "Cites a graph edge.",
                        "entry_class": "FACT",
                        "evidence": ["is_shared_gated_kind -> is_unshared_gated_event (1 hop)"],
                    },
                    {
                        "statement": "Cites a tool result.",
                        "entry_class": "FACT",
                        "evidence": ["find_references('x', crate='buzz-core') -> no callers here"],
                    },
                ],
            )
            head_sha = commit_all(root, "add node", "2020-01-02T00:00:00")

            node = _single_node(root)
            recorded = stale.extract_recorded_revision(node)
            self.assertEqual(recorded.sha, base_sha)
            verdict = stale.evaluate_node(node, recorded, head_sha, root)
            self.assertEqual(verdict.status, "unestablished")
            # Three unopenable citations reported -- the node's OWN
            # recorded-revision `commit <base_sha>` entry produces no finding
            # at all, so exactly three findings exist, not four.
            self.assertEqual(len(verdict.findings), 3)
            for finding in verdict.findings:
                self.assertEqual(finding.status, "unestablished")
                self.assertNotIn(base_sha, finding.citation)


# ---------------------------------------------------------------------------
# STEP 8 -- determinism.
# ---------------------------------------------------------------------------


class DeterminismTest(unittest.TestCase):
    def test_rerun_against_unchanged_tree_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "a.txt").write_text("v1\n")
            (root / "b.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            write_node(
                root,
                "one.md",
                "fixture-determinism-one",
                [
                    provenance_entry(sha_a),
                    {"statement": "Cites a.txt.", "entry_class": "FACT", "evidence": ["a.txt"]},
                ],
            )
            write_node(
                root,
                "two.md",
                "fixture-determinism-two",
                [
                    provenance_entry(sha_a),
                    {"statement": "Cites b.txt.", "entry_class": "FACT", "evidence": ["b.txt"]},
                ],
            )
            head_sha = commit_all(root, "add nodes", "2020-01-02T00:00:00")

            first = stale.run(root, head_sha, root).render()
            second = stale.run(root, head_sha, root).render()
            self.assertEqual(first, second)


# ---------------------------------------------------------------------------
# main() -- up-front `--head` validation, fail closed on an unresolvable ref
# ---------------------------------------------------------------------------


class MainHeadValidationTest(unittest.TestCase):
    """`main()` must refuse a `--head` that cannot be resolved to a commit,
    rather than running every node against an invisible ref and printing a
    full report where every verdict happens to be `unestablished` --
    indistinguishable from the legitimate shallow-checkout case this module's
    own docstring, and `corpus-maintain`'s SKILL.md, both say not to treat as
    failure. Mirrors `regenerate.py`'s existing up-front `--base`/`--head`
    validation in its own `main()`.

    `main()` resolves `repo_dir` from `validate.repo_root()` unconditionally
    -- unlike `regenerate.py`, it takes no `--repo-dir` override -- so this
    is the one test in this file that patches that single call, to point it
    at a hermetic fixture repo rather than reading this repository's own
    history. Everything about the fixture itself still follows this file's
    hermetic-git-repo rule; only the module-level `repo_root()` lookup is
    substituted, so `main()` is driven end-to-end rather than `run()` called
    directly.
    """

    def test_unresolvable_head_exits_non_zero_and_prints_no_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            commit_all(root, "commit A", "2020-01-01T00:00:00")

            bogus_head = "0" * 40  # well-formed SHA shape, resolves to nothing
            out, err = io.StringIO(), io.StringIO()
            with unittest.mock.patch.object(stale.validate, "repo_root", return_value=root):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    exit_code = stale.main(["--head", bogus_head])

            self.assertNotEqual(exit_code, 0)
            self.assertIn(bogus_head, err.getvalue())
            self.assertIn("does not resolve to a commit", err.getvalue())
            self.assertEqual(out.getvalue(), "")


# ---------------------------------------------------------------------------
# Real-corpus smoke test -- the one deliberate exception to "never read the
# real tree", per test_validate.py's own documented carve-out.
# ---------------------------------------------------------------------------


class RealCorpusSmokeTest(unittest.TestCase):
    def test_real_corpus_recorded_revisions_all_resolve(self) -> None:
        """Every real node's recorded revision resolves to a SHA, none
        ambiguous.

        Replaces a hardcoded `self.assertEqual(len(nodes), 205)`, the same
        fragile-assertion-on-changing-real-state pattern
        `test_validate.py`'s `test_real_corpus_root_discovery_matches_an_
        independent_walk` documents replacing for exactly the reason given
        there: a bare count says nothing about *which* nodes were found and
        breaks on the exact growth it should tolerate. This follows that
        fix's precedent -- `discover_nodes()`'s result set is compared
        against a fresh, independently-computed walk of the same corpus
        root, so the test strengthens as the corpus grows rather than merely
        breaking on it."""
        root = validate.repo_root() / "launchpad" / "docs" / "corpus"
        resolved_root = root.resolve()
        expected_paths = sorted(
            path
            for path in root.rglob("*.md")
            if path.relative_to(root).parts[0] != "schema"
            and path.resolve().is_relative_to(resolved_root)
        )
        self.assertNotEqual(expected_paths, [])  # corpus must not be empty

        nodes = stale.discover_nodes(root)
        self.assertEqual(sorted(node.path for node in nodes), expected_paths)

        results = [stale.extract_recorded_revision(node) for node in nodes]
        unresolved = [r for r in results if r.sha is None]
        self.assertEqual(unresolved, [])

    def test_real_corpus_run_is_well_formed_and_reproducible(self) -> None:
        """Runs the actual checker over the real corpus at real `HEAD`. Not a
        fixture -- this repository's real git history is what produces a real
        report, which no hermetic fixture can substitute for. Also proves
        STEP 3's reproducibility requirement: the same run against the same
        `HEAD` is byte-for-byte identical.

        Deliberately does NOT assert `assertIn("STALE  ", first)`. CI's
        `actions/checkout@v4` runs at depth 1 (no `fetch-depth` set in
        `.github/workflows/launchpad-corpus-validate.yml`), so `commit_exists()`
        (gate 1) fails closed for every real node's recorded SHA there -- none
        of that history is fetched -- and the report has zero `STALE` lines in
        CI, exactly the depth-1 caveat this module's own docstring warns about.
        Asserting a specific verdict distribution here would make this test
        fail deterministically in CI, for a reason that has nothing to do with
        a regression. What IS depth-independent -- and what this asserts
        instead -- is that the report is well-formed and reproducible.
        Hermetic-fixture tests elsewhere in this file
        (`test_known_stale_fixture_proves_detection`) already prove
        stale-detection itself works, with no CI-checkout dependency."""
        repo_root = validate.repo_root()
        root = repo_root / "launchpad" / "docs" / "corpus"
        first = stale.run(root, "HEAD", repo_root).render()
        second = stale.run(root, "HEAD", repo_root).render()
        self.assertEqual(first, second)

        lines = first.rstrip("\n").split("\n")
        self.assertTrue(lines)
        summary_line = lines[-1]
        self.assertTrue(summary_line.startswith("SUMMARY  "))
        for line in lines[:-1]:
            self.assertTrue(
                line.startswith("STALE  ") or line.startswith("UNESTABLISHED  "),
                f"unexpected report line shape: {line!r}",
            )

        nodes = stale.discover_nodes(root)
        self.assertIn(f"{len(nodes)} node(s)", summary_line)


if __name__ == "__main__":
    unittest.main()
