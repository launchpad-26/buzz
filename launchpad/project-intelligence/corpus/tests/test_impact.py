"""Unit tests for change-set to impacted-node mapping -- issue #635.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test builds its own throwaway fixture -- either a plain temp directory
(no git needed, for the pure citation-indexing and coverage-gap logic) or a
hermetic throwaway git repository under `tempfile.TemporaryDirectory`, using
the same isolation `test_stale.py` documents for itself: `GIT_CONFIG_GLOBAL`
and `GIT_CONFIG_SYSTEM` point at `/dev/null`, `HOME` points at the fixture
directory itself, `user.name`/`user.email`/`commit.gpgsign=false` are pinned
with `-c` rather than written to any config file, and commit dates are fixed
so the same fixture yields the same SHAs on every run.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_CORPUS_DIR = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


impact = _load("corpus_impact", _CORPUS_DIR / "impact.py")
stale = impact.stale
validate = impact.validate


# ---------------------------------------------------------------------------
# Hermetic git fixture harness -- same isolation `test_stale.py` uses.
# ---------------------------------------------------------------------------

_GIT_IDENTITY = [
    "-c", "user.name=Corpus Impact Test",
    "-c", "user.email=corpus-impact-test@example.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "init.defaultBranch=main",
]


def _git(args: list[str], cwd: Path, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    env["HOME"] = str(cwd)
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        ["git", *_GIT_IDENTITY, *args], cwd=cwd, capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {args} failed in {cwd}: {result.stderr}")
    return result


def init_repo(root: Path) -> None:
    _git(["init", "-q"], root)


def commit_all(root: Path, message: str, when: str) -> str:
    _git(["add", "-A"], root)
    _git(
        ["commit", "-q", "--allow-empty", "-m", message],
        root,
        extra_env={"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when},
    )
    return _git(["rev-parse", "HEAD"], root).stdout.strip()


def write_node(
    corpus_root: Path,
    rel_path: str,
    node_id: str,
    evidence_entries: list[dict],
    relationships: list[dict] | None = None,
) -> None:
    """Write a schema-valid corpus node. `id`, `evidence` and (optionally)
    `relationships` vary per fixture; the rest are fixed to values
    `node.schema.json` accepts, the same convention `test_stale.py` uses."""
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
    if relationships:
        lines.append("relationships:")
        for rel in relationships:
            lines.append(f'  - type: {rel["type"]}')
            lines.append(f'    target: {rel["target"]}')
    lines.append("---")
    lines.append("")
    lines.append(f"# {node_id}")
    lines.append("")
    path = corpus_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def write_invalid_node(corpus_root: Path, rel_path: str) -> None:
    """Write a schema-invalid node with no `id` at all, so `validate._label`
    cannot fall back to an id and must use the file path instead -- the shape
    STEP 7's done-when checks for."""
    text = "\n".join(
        [
            "---",
            "type: governance",
            "status: active",
            "origin: launchpad",
            "audiences:",
            "  - agent",
            "evidence:",
            '  - statement: "Missing id."',
            "    entry_class: FACT",
            '    evidence: ["some/path.rs"]',
            "---",
            "",
            "# invalid",
            "",
        ]
    )
    path = corpus_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def provenance_entry(sha: str) -> dict:
    return {
        "statement": f"This node was authored and checked against repository revision {sha}.",
        "entry_class": "FACT",
        "evidence": [f"commit {sha}"],
    }


# ---------------------------------------------------------------------------
# STEP 1 -- citation-to-node index
# ---------------------------------------------------------------------------


class CitationIndexTest(unittest.TestCase):
    def test_position_and_bare_citations_of_the_same_file_index_to_the_same_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_node(
                root,
                "node.md",
                "fixture-both-shapes",
                [
                    {
                        "statement": "Cites a ranged position.",
                        "entry_class": "FACT",
                        "evidence": ["foo/bar.rs:12-20"],
                    },
                    {
                        "statement": "Cites the same file bare.",
                        "entry_class": "FACT",
                        "evidence": ["foo/bar.rs"],
                    },
                ],
            )
            nodes = stale.discover_nodes(root)
            index = impact.build_citation_index(nodes)

            self.assertIn("foo/bar.rs", index)
            node_ids = {ref.node_id for ref in index["foo/bar.rs"]}
            self.assertEqual(node_ids, {"fixture-both-shapes"})
            self.assertEqual(len(index["foo/bar.rs"]), 2)

    def test_unopenable_citation_shapes_index_to_no_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha = "a" * 40
            write_node(
                root,
                "node.md",
                "fixture-unopenable",
                [
                    {
                        "statement": "Cites a commit.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha}"],
                    },
                    {
                        "statement": "Cites a graph edge.",
                        "entry_class": "FACT",
                        "evidence": ["a -> b (1 hop)"],
                    },
                    {
                        "statement": "Cites a tool result.",
                        "entry_class": "FACT",
                        "evidence": ["f(x) -> y"],
                    },
                    {
                        "statement": "Cites a URL.",
                        "entry_class": "FACT",
                        "evidence": ["https://example.com/thing"],
                    },
                ],
            )
            nodes = stale.discover_nodes(root)
            index = impact.build_citation_index(nodes)

            self.assertEqual(index, {})


# ---------------------------------------------------------------------------
# STEP 2 -- change-set reader
# ---------------------------------------------------------------------------


class ChangedPathsTest(unittest.TestCase):
    def test_rename_carries_both_names_and_delete_is_not_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "old.txt").write_text("content\n" * 5)
            (root / "gone.txt").write_text("bye\n")
            base = commit_all(root, "base", "2020-01-01T00:00:00")

            _git(["mv", "old.txt", "new.txt"], root)
            (root / "gone.txt").unlink()
            head = commit_all(root, "rename and delete", "2020-01-02T00:00:00")

            changes = impact.changed_paths(base, head, root)

            rename = next(c for c in changes if c.status == "R")
            self.assertEqual(rename.path, "new.txt")
            self.assertEqual(rename.old_path, "old.txt")

            delete = next(c for c in changes if c.path == "gone.txt")
            self.assertEqual(delete.status, "D")


# ---------------------------------------------------------------------------
# STEP 3 -- wiring: compute_impact end to end, and determinism
# ---------------------------------------------------------------------------


class ComputeImpactWiringTest(unittest.TestCase):
    def test_a_changed_cited_file_produces_an_impacted_node_and_reruns_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            corpus_root = root / "corpus"
            (root / "src.rs").write_text("v1\n")
            base = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                corpus_root,
                "node.md",
                "fixture-wiring",
                [{"statement": "Cites src.rs.", "entry_class": "FACT", "evidence": ["src.rs"]}],
            )
            (root / "src.rs").write_text("v2\n")
            head = commit_all(root, "change src.rs and add node", "2020-01-02T00:00:00")

            first = impact.compute_impact(corpus_root, base, head, root).to_json()
            second = impact.compute_impact(corpus_root, base, head, root).to_json()

            self.assertEqual(first, second)
            self.assertIn('"node_id": "fixture-wiring"', first)
            self.assertIn('"changed_path": "src.rs"', first)


# ---------------------------------------------------------------------------
# STEP 4 -- relationship-type propagation
# ---------------------------------------------------------------------------


class PropagationTest(unittest.TestCase):
    def test_depends_on_part_of_and_supersedes_propagate_but_references_and_implements_do_not(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            corpus_root = root / "corpus"
            (root / "src.rs").write_text("v1\n")
            base = commit_all(root, "base", "2020-01-01T00:00:00")

            # The directly-impacted node cites the changed file, and declares
            # the propagating-by-forward-or-both edges itself (part-of,
            # supersedes). depends-on must instead be declared BY the
            # dependent neighbour, per relationshipMeta's directionality
            # ("source requires target to be true/current") -- see
            # _PROPAGATION_DIRECTION's comment in impact.py.
            write_node(
                corpus_root,
                "d.md",
                "d",
                [{"statement": "Cites src.rs.", "entry_class": "FACT", "evidence": ["src.rs"]}],
                relationships=[
                    {"type": "part-of", "target": "n-part-of"},
                    {"type": "supersedes", "target": "n-supersedes"},
                    {"type": "references", "target": "n-references"},
                    {"type": "implements", "target": "n-implements"},
                ],
            )
            for neighbour_id in ("n-part-of", "n-supersedes", "n-references", "n-implements"):
                write_node(
                    corpus_root,
                    f"{neighbour_id}.md",
                    neighbour_id,
                    [{"statement": "Unrelated claim.", "entry_class": "FACT", "evidence": ["other.rs"]}],
                )
            write_node(
                corpus_root,
                "n-depends-on.md",
                "n-depends-on",
                [{"statement": "Unrelated claim.", "entry_class": "FACT", "evidence": ["other.rs"]}],
                relationships=[{"type": "depends-on", "target": "d"}],
            )

            (root / "src.rs").write_text("v2\n")
            head = commit_all(root, "change src.rs and add nodes", "2020-01-02T00:00:00")

            report = impact.compute_impact(corpus_root, base, head, root)
            impacted_ids = {row.node_id for row in report.impacted_nodes}

            self.assertIn("d", impacted_ids)
            self.assertIn("n-part-of", impacted_ids)
            self.assertIn("n-supersedes", impacted_ids)
            self.assertIn("n-depends-on", impacted_ids)
            self.assertNotIn("n-references", impacted_ids)
            self.assertNotIn("n-implements", impacted_ids)

            by_id = {row.node_id: row for row in report.impacted_nodes}
            self.assertIn("part-of", by_id["n-part-of"].reason)
            self.assertIn("supersedes", by_id["n-supersedes"].reason)
            self.assertIn("depends-on", by_id["n-depends-on"].reason)


# ---------------------------------------------------------------------------
# STEP 5 -- coverage gaps
# ---------------------------------------------------------------------------


class CoverageGapsTest(unittest.TestCase):
    def test_a_credential_shaped_changed_path_is_counted_but_never_echoed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            corpus_root = root / "corpus"
            base = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                corpus_root,
                "node.md",
                "fixture-gaps",
                [{"statement": "Cites nothing relevant.", "entry_class": "FACT", "evidence": ["other.rs"]}],
            )
            (root / ".env").write_text("SECRET=x\n")
            head = commit_all(root, "add .env and a node", "2020-01-02T00:00:00")

            report = impact.compute_impact(corpus_root, base, head, root)

            self.assertNotIn(".env", report.to_json())
            self.assertGreater(report.coverage_gaps.redacted_count, 0)

    def test_a_cited_changed_path_is_impacted_not_a_coverage_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            corpus_root = root / "corpus"
            (root / "cited.rs").write_text("v1\n")
            base = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                corpus_root,
                "node.md",
                "fixture-covered",
                [{"statement": "Cites cited.rs.", "entry_class": "FACT", "evidence": ["cited.rs"]}],
            )
            (root / "cited.rs").write_text("v2\n")
            head = commit_all(root, "change cited.rs and add node", "2020-01-02T00:00:00")

            report = impact.compute_impact(corpus_root, base, head, root)

            self.assertIn("fixture-covered", {row.node_id for row in report.impacted_nodes})
            self.assertNotIn("cited.rs", report.coverage_gaps.paths)


# ---------------------------------------------------------------------------
# STEP 6 -- category fixtures (inventory.py's own vocabulary)
# ---------------------------------------------------------------------------


class CategoryFixturesTest(unittest.TestCase):
    def _run_one_file_change(self, changed_path: str) -> "impact.ImpactReport":
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            corpus_root = root / "corpus"
            (root / changed_path).parent.mkdir(parents=True, exist_ok=True)
            (root / changed_path).write_text("v1\n")
            base = commit_all(root, "base", "2020-01-01T00:00:00")
            write_node(
                corpus_root,
                "node.md",
                "fixture-category",
                [
                    {
                        "statement": f"Cites {changed_path}.",
                        "entry_class": "FACT",
                        "evidence": [changed_path],
                    }
                ],
            )
            (root / changed_path).write_text("v2\n")
            head = commit_all(root, "change file and add node", "2020-01-02T00:00:00")
            return impact.compute_impact(corpus_root, base, head, root)

    def _assert_single_node_with_reason_naming_citation(
        self, report: "impact.ImpactReport", changed_path: str
    ) -> None:
        self.assertEqual({row.node_id for row in report.impacted_nodes}, {"fixture-category"})
        row = report.impacted_nodes[0]
        self.assertIn(changed_path, row.reason)

    def test_migration_change(self) -> None:
        report = self._run_one_file_change("migrations/0001_test.sql")
        self._assert_single_node_with_reason_naming_citation(report, "migrations/0001_test.sql")

    def test_event_kind_change(self) -> None:
        report = self._run_one_file_change("crates/buzz-core/src/kind.rs")
        self._assert_single_node_with_reason_naming_citation(report, "crates/buzz-core/src/kind.rs")

    def test_relay_route_change(self) -> None:
        report = self._run_one_file_change("crates/buzz-relay/src/router.rs")
        self._assert_single_node_with_reason_naming_citation(report, "crates/buzz-relay/src/router.rs")

    def test_plain_crate_source_change(self) -> None:
        report = self._run_one_file_change("crates/buzz-core/src/lib.rs")
        self._assert_single_node_with_reason_naming_citation(report, "crates/buzz-core/src/lib.rs")


# ---------------------------------------------------------------------------
# STEP 7 -- unreadable nodes
# ---------------------------------------------------------------------------


class UnreadableNodesTest(unittest.TestCase):
    def test_a_schema_invalid_node_with_no_id_is_labelled_by_path_not_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            corpus_root = root / "corpus"
            base = commit_all(root, "base", "2020-01-01T00:00:00")
            write_invalid_node(corpus_root, "broken.md")
            head = commit_all(root, "add invalid node", "2020-01-02T00:00:00")

            report = impact.compute_impact(corpus_root, base, head, root)

            labels = [u.label for u in report.unreadable_nodes]
            self.assertIn(str(corpus_root / "broken.md"), labels)


if __name__ == "__main__":
    unittest.main()
