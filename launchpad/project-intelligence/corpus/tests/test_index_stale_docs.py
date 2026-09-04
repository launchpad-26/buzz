"""Focused tests for the stale-docs builder -- issue #904.

Follows test_index_orphaned_docs.py's fixture-node pattern and
test_index_coverage.py's fixture-repo-root pattern (a temp root whose corpus
lives under `<root>/launchpad/docs/corpus/`, so the builder's repo-root
derivation for git commands resolves the fixture, never the real
repository). Extended with a real, hermetic `git init` repository inside the
same temp root, so the commit-freshness comparison's "possibly stale" and "no
signal of staleness" buckets are exercised deterministically against real git
history rather than only smoke-tested against the live buzz repository. Every
behavioral test builds its own throwaway fixture tree; one read-only smoke
test touches the real committed document.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_INDEXES_PATH = Path(__file__).resolve().parent.parent / "indexes.py"
indexes = sys.modules.get("corpus_indexes")
if indexes is None:
    _spec = importlib.util.spec_from_file_location("corpus_indexes", _INDEXES_PATH)
    indexes = importlib.util.module_from_spec(_spec)
    sys.modules["corpus_indexes"] = indexes
    _spec.loader.exec_module(indexes)

BUILDER_NAME = "stale-docs"
OUTPUT_REL = "generated/stale-docs.md"
NODE_ID = "generated-stale-docs"
REAL_CORPUS = indexes.validate.repo_root() / indexes.validate.DEFAULT_ROOT

_UNRESOLVABLE_SHA = "0123456789abcdef0123456789abcdef01234567"


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git(args: list[str], cwd: Path) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"git {' '.join(args)} failed in {cwd}: {result.stderr}"
    )


def _node_text(node_id: str, node_type: str, entries: list[list[str]]) -> str:
    """`entries` is a list of evidence entries, each a list of citation
    strings -- one FACT entry per inner list, mirroring how a real node can
    carry more than one commit citation or file citation."""
    blocks = []
    for citations in entries:
        cite_lines = "\n".join(f'      - "{c}"' for c in citations)
        blocks.append(
            f'  - statement: "Fixture entry for test_index_stale_docs.py."\n'
            f"    entry_class: FACT\n"
            f"    evidence:\n"
            f"{cite_lines}"
        )
    evidence_block = "\n".join(blocks)
    return (
        "---\n"
        f"id: {node_id}\n"
        f"type: {node_type}\n"
        "status: active\n"
        "origin: launchpad\n"
        "audiences:\n"
        "  - agent\n"
        "evidence:\n"
        f"{evidence_block}\n"
        "---\n\n"
        f"# {node_id}\n"
    )


def _spec_for_builder():
    specs = indexes.discover_builders()
    by_name = {s.name: s for s in specs}
    return by_name.get(BUILDER_NAME), specs


def _render_fixture(corpus_root: Path) -> str:
    spec, specs = _spec_for_builder()
    ctx = indexes.build_context(corpus_root, specs)
    return indexes.render_document(spec, ctx)


class DiscoveryTest(unittest.TestCase):
    def test_builder_discovered_with_expected_identity(self) -> None:
        spec, _ = _spec_for_builder()
        self.assertIsNotNone(spec, "stale-docs builder not discovered")
        self.assertEqual(spec.output_path, OUTPUT_REL)
        self.assertEqual(spec.node_id, NODE_ID)
        self.assertEqual(spec.node_type, "governance")
        self.assertEqual(
            spec.relationships, ({"type": "references", "target": "corpus-agents"},)
        )
        # Not index-shaped -- the template names this document an audit
        # report, same as orphaned-docs.md, so it must not declare implements
        # toward the generated-index template.
        self.assertNotIn(
            {"type": "implements", "target": "corpus-template-generated-index"},
            list(spec.relationships),
        )


class HermeticGitFixtureTest(unittest.TestCase):
    """A fixture repo, `git init`'d at the temp root, with:
    - fixture-fresh: cites commit SHA1 + src/stable.txt, untouched since
      SHA1 -> no signal of staleness.
    - fixture-stale: cites commit SHA1 + src/mutate.txt, edited (uncommitted)
      after SHA1 -> possibly stale.
    - fixture-no-revision: cites only a file, no commit citation at all ->
      no revision-pinning FACT.
    - fixture-ambiguous: cites two distinct commit shas -> ambiguous
      revision.
    - fixture-unresolvable: cites a well-formed but nonexistent sha -> cannot
      verify locally.
    - fixture-no-files: cites only commit SHA1, no other file citation ->
      nothing to compare.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.root = root
        self.corpus = root / "launchpad" / "docs" / "corpus"

        _git(["init", "-q"], root)
        _git(["config", "user.email", "fixture@example.invalid"], root)
        _git(["config", "user.name", "Fixture"], root)
        _git(["config", "commit.gpgsign", "false"], root)

        _write(root, "src/stable.txt", "v1\n")
        _write(root, "src/mutate.txt", "v1\n")
        _git(["add", "src/stable.txt", "src/mutate.txt"], root)
        _git(["commit", "-q", "-m", "initial fixture commit"], root)
        sha1 = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.sha1 = sha1

        # Uncommitted edit -- git diff <sha1> -- src/mutate.txt sees this
        # against the working tree without needing a second commit.
        _write(root, "src/mutate.txt", "v2\n")

        _write(
            root,
            "launchpad/docs/corpus/fixture-fresh.md",
            _node_text(
                "fixture-fresh",
                "governance",
                [[f"commit {sha1}"], ["src/stable.txt"]],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-stale.md",
            _node_text(
                "fixture-stale",
                "governance",
                [[f"commit {sha1}"], ["src/mutate.txt"]],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-no-revision.md",
            _node_text(
                "fixture-no-revision",
                "governance",
                [["src/stable.txt"]],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-ambiguous.md",
            _node_text(
                "fixture-ambiguous",
                "governance",
                [[f"commit {sha1}", f"commit {_UNRESOLVABLE_SHA}"]],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-unresolvable.md",
            _node_text(
                "fixture-unresolvable",
                "governance",
                [[f"commit {_UNRESOLVABLE_SHA}"], ["src/stable.txt"]],
            ),
        )
        _write(
            root,
            "launchpad/docs/corpus/fixture-no-files.md",
            _node_text(
                "fixture-no-files",
                "governance",
                [[f"commit {sha1}"]],
            ),
        )

    def test_no_revision_bucket(self) -> None:
        text = _render_fixture(self.corpus)
        section = text.split("### No revision-pinning FACT", 1)[1].split(
            "### Ambiguous revision"
        )[0]
        self.assertIn("fixture-no-revision", section)
        self.assertNotIn("fixture-fresh", section)
        self.assertNotIn("fixture-stale", section)

    def test_ambiguous_revision_bucket(self) -> None:
        text = _render_fixture(self.corpus)
        section = text.split("### Ambiguous revision", 1)[1].split(
            "### Commit-freshness comparison"
        )[0]
        self.assertIn("fixture-ambiguous", section)
        self.assertIn(self.sha1, section)
        self.assertIn(_UNRESOLVABLE_SHA, section)
        self.assertNotIn("fixture-fresh", section)

    def test_fresh_bucket(self) -> None:
        text = _render_fixture(self.corpus)
        fresh_section = text.split(
            "#### No signal of staleness", 1
        )[1].split("#### Cannot verify locally", 1)[0]
        self.assertIn("fixture-fresh", fresh_section)
        self.assertNotIn("fixture-stale", fresh_section)

    def test_possibly_stale_bucket_names_changed_path(self) -> None:
        text = _render_fixture(self.corpus)
        stale_section = text.split(
            "#### Possibly stale", 1
        )[1].split("#### No signal of staleness", 1)[0]
        self.assertIn("fixture-stale", stale_section)
        self.assertIn("src/mutate.txt", stale_section)
        self.assertNotIn("fixture-fresh", stale_section)

    def test_unresolvable_bucket(self) -> None:
        text = _render_fixture(self.corpus)
        section = text.split(
            "#### Cannot verify locally", 1
        )[1].split("#### No other file citation", 1)[0]
        self.assertIn("fixture-unresolvable", section)
        self.assertIn(_UNRESOLVABLE_SHA, section)
        self.assertNotIn("fixture-fresh", section)

    def test_no_file_citations_bucket(self) -> None:
        text = _render_fixture(self.corpus)
        section = text.split("#### No other file citation", 1)[1].split(
            "## Relationships"
        )[0]
        self.assertIn("fixture-no-files", section)
        self.assertNotIn("fixture-fresh", section)

    def test_output_stable_across_two_renders(self) -> None:
        self.assertEqual(_render_fixture(self.corpus), _render_fixture(self.corpus))

    def test_front_matter_carries_node_id_and_type(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertTrue(text.startswith(f'---\nid: "{NODE_ID}"\ntype: "governance"\n'))
        self.assertIn("do not edit by hand", text)

    def test_narrowing_not_certification_language_present(self) -> None:
        text = _render_fixture(self.corpus)
        self.assertIn("narrowing step, not a certification", text)

    def test_shallow_disclosure_reflects_live_non_shallow_fixture(self) -> None:
        # Issue #2060: this fixture is a real, freshly `git init`'d, single-
        # commit checkout -- not shallow -- so a live check must say "full
        # clone", never the old hardcoded "shallow clone" claim regardless
        # of the actual repository state.
        text = _render_fixture(self.corpus)
        self.assertIn("This worktree's repository is a full clone", text)
        self.assertNotIn("This worktree's repository is a shallow clone", text)

    def test_unresolvable_explanation_reflects_live_non_shallow_fixture(self) -> None:
        text = _render_fixture(self.corpus)
        section = text.split(
            "#### Cannot verify locally", 1
        )[1].split("#### No other file citation", 1)[0]
        self.assertIn("this worktree's repository is a full clone", section)
        self.assertNotIn(
            "this worktree's repository is a shallow clone, so an older",
            section,
        )

    def test_extra_evidence_statement_describes_checkout_as_non_shallow(self) -> None:
        text = _render_fixture(self.corpus)
        front_matter = text.split("---\n")[1]
        self.assertIn("(non-shallow) checkout", front_matter)
        self.assertNotIn("(shallow) checkout", front_matter)


class NonGitFixtureTest(unittest.TestCase):
    """A fixture corpus with NO `.git` at all (or one outside any repo),
    exercising the graceful-degradation path: every commit citation present
    still lands somewhere sensible (never crashes generation) even when git
    itself cannot answer."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.corpus = root / "launchpad" / "docs" / "corpus"
        _write(
            root,
            "launchpad/docs/corpus/fixture-plain.md",
            _node_text(
                "fixture-plain",
                "governance",
                [[f"commit {_UNRESOLVABLE_SHA}"], ["src/whatever.txt"]],
            ),
        )

    def test_generation_does_not_crash_without_a_git_repository(self) -> None:
        # No assertion beyond "this does not raise" -- a temp dir outside any
        # git worktree is the one environment this builder must degrade out
        # of gracefully rather than crash generation for the whole document.
        text = _render_fixture(self.corpus)
        self.assertIn("fixture-plain", text)

    def test_shallow_disclosure_says_could_not_determine(self) -> None:
        # Issue #2060: outside any git repository, `git rev-parse
        # --is-shallow-repository` cannot resolve -- the disclosure must say
        # so plainly, never fall back to asserting either shallow or full.
        text = _render_fixture(self.corpus)
        self.assertIn(
            "Whether this worktree's repository is a shallow clone could "
            "not be determined",
            text,
        )
        self.assertNotIn("This worktree's repository is a shallow clone", text)
        self.assertNotIn("This worktree's repository is a full clone", text)


class RealCorpusSmokeTest(unittest.TestCase):
    """Read-only checks against the committed generated document."""

    def test_committed_document_identity_and_marker(self) -> None:
        target = REAL_CORPUS / OUTPUT_REL
        self.assertTrue(target.is_file(), f"{OUTPUT_REL} missing on disk")
        text = target.read_text(encoding="utf-8")
        front_matter = text.split("---\n")[1]
        self.assertIn(f'id: "{NODE_ID}"', front_matter)
        self.assertIn('type: "governance"', front_matter)
        self.assertIn("**Generated -- do not edit by hand.**", text)
        self.assertIn("### No revision-pinning FACT", text)
        self.assertIn("### Ambiguous revision", text)
        self.assertIn("### Commit-freshness comparison (best-effort)", text)


if __name__ == "__main__":
    unittest.main()
