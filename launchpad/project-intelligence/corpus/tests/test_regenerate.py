"""Unit tests for deterministic regeneration reporting -- issue #559.

Run:  python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

Every test builds its own throwaway, hermetic git repository under
`tempfile.TemporaryDirectory`, using the SAME isolation `test_stale.py` and
`test_impact.py` already established for this package -- copied here
verbatim, per this issue's own plan ("Copy that pattern; do not invent
another"): `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` point at `/dev/null`,
`HOME` points at the fixture directory itself, `user.name`/`user.email`/
`commit.gpgsign=false` are pinned with `-c` rather than written to any
config file, and commit dates are fixed so the same fixture yields the same
SHAs on every run.

NOTHING in this file references a real SHA, a real corpus node id, a real
source path, or `origin/launchpad` -- CI checks out at depth 1 and both
`test_impact.py` and `test_stale.py` were bitten by precisely this before.
Every SHA below is either a fixture-generated commit hash (returned by
`commit_all`, a real object in the fixture's own throwaway `.git`) or an
obviously-synthetic placeholder (`"a" * 40`) used only where no real commit
is needed.
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
from pathlib import Path

_CORPUS_DIR = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


regenerate = _load("corpus_regenerate", _CORPUS_DIR / "regenerate.py")
impact = regenerate.impact
stale = regenerate.stale
validate = regenerate.validate


# ---------------------------------------------------------------------------
# Hermetic git fixture harness -- identical isolation to test_stale.py and
# test_impact.py, copied rather than reinvented.
# ---------------------------------------------------------------------------

_GIT_IDENTITY = [
    "-c", "user.name=Corpus Regenerate Test",
    "-c", "user.email=corpus-regenerate-test@example.invalid",
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


def init_repo(root: Path, initial_branch: str = "main") -> None:
    _git(["init", "-q", "-b", initial_branch], root)


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
) -> None:
    """Write a schema-valid corpus node -- the same fixed shape (id/type/
    status/origin/audiences) `test_stale.py`'s and `test_impact.py`'s own
    `write_node` helpers use; only `id` and `evidence` vary per fixture.
    """
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
    path = corpus_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def provenance_entry(sha: str) -> dict:
    return {
        "statement": f"This node was authored and checked against repository revision {sha}.",
        "entry_class": "FACT",
        "evidence": [f"commit {sha}"],
    }


def _single_node(root: Path) -> "validate.LoadedNode":
    nodes = stale.discover_nodes(root)
    assert len(nodes) == 1, f"expected exactly one node, found {len(nodes)}"
    return nodes[0]


@contextlib.contextmanager
def _captured_stdio():
    """Both streams -- `main()` writes its report to real stdout when no
    `--out` is given, which would otherwise leak into the suite's console
    output for a passing test with nothing wrong to show."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out, err


# ---------------------------------------------------------------------------
# classify_claim -- route-2 shape and diff classification
# ---------------------------------------------------------------------------


class ClassifyClaimTest(unittest.TestCase):
    def test_all_file_citations_unchanged_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "unchanged.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            commit_all(root, "commit B (no changes)", "2020-01-02T00:00:00")
            head = _git(["rev-parse", "HEAD"], root).stdout.strip()

            result = regenerate.classify_claim(2, ["unchanged.txt"], sha_a, head, root)
            self.assertEqual(result.status, "clean")

    def test_a_changed_file_citation_is_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "changed.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "changed.txt").write_text("v2\n")
            sha_b = commit_all(root, "commit B: edit changed.txt", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(2, ["changed.txt"], sha_a, sha_b, root)
            self.assertEqual(result.status, "dirty")
            self.assertIn("changed.txt", result.reason)

    def test_a_single_non_file_citation_closes_the_whole_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "cited.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            fake_sha = "d" * 40
            result = regenerate.classify_claim(
                2, ["cited.txt", f"commit {fake_sha}"], sha_a, sha_b, root
            )
            self.assertEqual(result.status, "closed")

    def test_a_graph_edge_citation_closes_the_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(
                2, ["node_alpha -> node_beta (1 hop)"], sha_a, sha_b, root
            )
            self.assertEqual(result.status, "closed")

    def test_a_tool_result_citation_closes_the_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(
                2, ["find_thing(x='y') -> no matches"], sha_a, sha_b, root
            )
            self.assertEqual(result.status, "closed")

    def test_a_url_citation_closes_the_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(
                2, ["https://example.invalid/spec"], sha_a, sha_b, root
            )
            self.assertEqual(result.status, "closed")

    def test_a_citation_absent_at_the_recorded_revision_is_treated_as_dirty(self) -> None:
        """A path that never existed at the recorded revision cannot be
        trusted as unchanged -- `git diff` for it is empty for a reason
        unrelated to "nothing changed", so `classify_claim` refuses to call
        that clean."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            sha_a = commit_all(root, "commit A (no files yet)", "2020-01-01T00:00:00")
            (root / "new.txt").write_text("v1\n")
            sha_b = commit_all(root, "commit B: add new.txt", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(2, ["new.txt"], sha_a, sha_b, root)
            self.assertEqual(result.status, "dirty")

    def test_no_citations_is_vacuously_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(2, [], sha_a, sha_b, root)
            self.assertEqual(result.status, "clean")


# ---------------------------------------------------------------------------
# The normalization trap -- proved by a test that FAILS if the `:line`/
# `:start-end` suffix is passed through to git unstripped.
# ---------------------------------------------------------------------------


class SuffixNormalizationTrapTest(unittest.TestCase):
    def test_position_suffixed_citation_of_a_changed_file_is_correctly_dirty(self) -> None:
        """`classify_claim` must strip `:2-2` before the path reaches git,
        and the REASON it gives must show the strip actually happened, not
        merely land on "dirty" by coincidence.

        `classify_claim` has two independent checks in front of git, in
        order: `stale.path_exists_at_revision` first, then
        `stale.diff_touched`. Both take a colon in the pathspec badly --
        `git cat-file -e <sha>:changed.txt:2-2` is a malformed object name
        (exit 128, verified directly against a throwaway fixture), so
        `path_exists_at_revision` ALSO reports "not found" for an unstripped
        suffixed path, independently of whether the strip ran. That means
        asserting `status == "dirty"` alone does not prove the strip
        happened -- the existence-check's own conservative "not found ->
        dirty" fallback produces the identical status even with the strip
        removed (verified empirically while writing this test). What DOES
        differ is the REASON: stripped, the citation resolves and
        `diff_touched` reports the real content change ("changed between the
        recorded revision and head"); unstripped, it never reaches
        `diff_touched` at all and reports "does not resolve at the recorded
        revision" instead -- a materially different, less accurate reason,
        because the file undeniably existed at the recorded revision. THIS
        assertion is the one that fails if the strip is removed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "changed.txt").write_text("line1\nline2\nline3\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "changed.txt").write_text("line1\nEDITED\nline3\n")
            sha_b = commit_all(root, "commit B: edit changed.txt", "2020-01-02T00:00:00")

            result = regenerate.classify_claim(2, ["changed.txt:2-2"], sha_a, sha_b, root)
            self.assertEqual(result.status, "dirty")
            self.assertEqual(
                result.reason,
                "changed.txt changed between the recorded revision and head",
                "the reason must name the STRIPPED path and the real diff -- "
                "an unstripped suffix instead reports 'does not resolve at "
                "the recorded revision', which is the observable symptom of "
                "the strip being skipped",
            )

    def test_unstripped_pathspec_would_have_hidden_the_same_change(self) -> None:
        """Companion assertion: passing the RAW, un-normalized citation
        straight to `stale.diff_touched` (bypassing `classify_claim`
        entirely) DOES report `False` (no change) for the identical fixture
        -- demonstrating the trap this module's normalization avoids, not
        merely asserting the fix works in isolation.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "changed.txt").write_text("line1\nline2\nline3\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "changed.txt").write_text("line1\nEDITED\nline3\n")
            sha_b = commit_all(root, "commit B: edit changed.txt", "2020-01-02T00:00:00")

            unstripped_touched = stale.diff_touched(sha_a, sha_b, "changed.txt:2-2", root)
            self.assertFalse(
                unstripped_touched,
                "an unstripped position suffix should indeed fool diff_touched "
                "-- this is the trap classify_claim's normalization avoids",
            )


# ---------------------------------------------------------------------------
# locate_recorded_revision_entry -- position, never guessed
# ---------------------------------------------------------------------------


class LocateRecordedRevisionEntryTest(unittest.TestCase):
    def test_rung1_statement_match_locates_entry_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha_a = "a" * 40
            write_node(
                root,
                "node.md",
                "fixture-locate-rung1",
                [
                    provenance_entry(sha_a),
                    {"statement": "Something else.", "entry_class": "FACT", "evidence": ["x.txt"]},
                ],
            )
            node = _single_node(root)
            index = regenerate.locate_recorded_revision_entry(node, sha_a)
            self.assertEqual(index, 1)

    def test_rung2_commit_citation_locates_the_actual_non_first_position(self) -> None:
        """Regression (verified via mutation testing: returning the wrong
        index left all 23 pre-existing tests passing). Every other fixture in
        this file places the recorded-revision entry at position 1, so rung
        1's statement match always succeeds first and rung 2's own `return
        rung2[0]` line (STEP 2, around lines 242-243) is never exercised with
        a real single match. This fixture's entry 1 defeats rung 1 (no
        recorded-revision sentence anywhere) and only entry 2 carries the
        `commit <sha>` citation, so the returned position must be exactly 2
        -- not merely non-crashing.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha_a = "9" * 40
            write_node(
                root,
                "node.md",
                "fixture-locate-rung2",
                [
                    {
                        "statement": "An unrelated claim citing a stable file.",
                        "entry_class": "FACT",
                        "evidence": ["stable.txt"],
                    },
                    {
                        "statement": "Not the fixed recorded-revision sentence at all.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha_a}"],
                    },
                    {
                        "statement": "Another unrelated claim.",
                        "entry_class": "FACT",
                        "evidence": ["other.txt"],
                    },
                ],
            )
            node = _single_node(root)
            index = regenerate.locate_recorded_revision_entry(node, sha_a)
            self.assertEqual(index, 2)

    def test_ambiguous_position_refuses_rather_than_guesses(self) -> None:
        """Two entries both citing `commit <sha>` in `commit <sha>` shape,
        with no unique statement match, is a position `locate_recorded_
        revision_entry` must refuse to pick between -- this is the exact
        corruption-risk shape STEP 2's plan names (a SHA cited again
        elsewhere), constructed here as the position-lookup boundary case.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha_a = "b" * 40
            write_node(
                root,
                "node.md",
                "fixture-locate-ambiguous",
                [
                    {
                        "statement": "Not the recorded-revision sentence at all.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha_a}"],
                    },
                    {
                        "statement": "Also not the recorded-revision sentence.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {sha_a}"],
                    },
                ],
            )
            node = _single_node(root)
            with self.assertRaises(ValueError):
                regenerate.locate_recorded_revision_entry(node, sha_a)


# ---------------------------------------------------------------------------
# apply_revision_move -- line-scoped rewrite, byte-identical everywhere else
# ---------------------------------------------------------------------------


class ApplyRevisionMoveTest(unittest.TestCase):
    def test_only_the_recorded_revision_entrys_two_lines_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha_old = "a" * 40
            sha_new = "b" * 40
            write_node(
                root,
                "node.md",
                "fixture-apply-scope",
                [
                    provenance_entry(sha_old),
                    {
                        "statement": "An unrelated claim citing a file.",
                        "entry_class": "FACT",
                        "evidence": ["some/file.rs"],
                    },
                ],
            )
            path = root / "node.md"
            before = path.read_text()
            node = _single_node(root)

            entry_index = regenerate.locate_recorded_revision_entry(node, sha_old)
            regenerate.apply_revision_move(path, entry_index, sha_old, sha_new)

            after = path.read_text()
            self.assertNotEqual(before, after)
            self.assertNotIn(sha_old, after)
            self.assertIn(sha_new, after)

            before_lines = before.splitlines()
            after_lines = after.splitlines()
            self.assertEqual(len(before_lines), len(after_lines))
            changed_lines = [
                i for i in range(len(before_lines)) if before_lines[i] != after_lines[i]
            ]
            self.assertEqual(
                len(changed_lines),
                2,
                f"expected exactly 2 changed lines, got {len(changed_lines)}: {changed_lines}",
            )

            # id is untouched (MUST 5).
            after_node = _single_node(root)
            self.assertEqual(after_node.id, "fixture-apply-scope")

    def test_a_shared_sha_in_an_unrelated_entry_is_left_byte_for_byte_unchanged(self) -> None:
        """REQUIRED (review-plan finding): a node whose recorded-revision SHA
        is ALSO cited verbatim in a separate, unrelated evidence entry (a
        `tool_result` genuinely about that historical commit) must have that
        unrelated entry's citation text untouched after `--apply`'s
        line-scoped rewrite. This is the regression test for the corruption
        risk STEP 2 names: a global string/regex replace of the old SHA
        would pass every other test in this file while still corrupting this
        exact shape -- measured at 88 of 226 real corpus nodes today.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha_old = "c" * 40
            sha_new = "d" * 40
            unrelated_citation = f"git_ls_tree(ref='some-ref') -> state as of commit {sha_old}"
            write_node(
                root,
                "node.md",
                "fixture-shared-sha",
                [
                    provenance_entry(sha_old),
                    {
                        "statement": "A clean claim citing a file that never changes.",
                        "entry_class": "FACT",
                        "evidence": ["stable.txt"],
                    },
                    {
                        "statement": f"As of commit {sha_old}, some historical fact held.",
                        "entry_class": "FACT",
                        "evidence": [unrelated_citation],
                    },
                ],
            )
            path = root / "node.md"
            node = _single_node(root)

            entry_index = regenerate.locate_recorded_revision_entry(node, sha_old)
            self.assertEqual(entry_index, 1, "recorded-revision entry must be entry 1")

            regenerate.apply_revision_move(path, entry_index, sha_old, sha_new)

            after_text = path.read_text()
            self.assertIn(
                unrelated_citation,
                after_text,
                "the unrelated tool_result citation of the same SHA must survive "
                "--apply byte-for-byte -- only the recorded-revision entry's own "
                "two lines may change",
            )
            # And the historical statement sentence naming the old SHA must
            # also survive untouched -- it is entry 3's statement, not
            # entry 1's.
            self.assertIn(f"As of commit {sha_old}, some historical fact held.", after_text)

    def test_apply_refuses_when_the_entry_position_has_no_statement_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_node(
                root,
                "node.md",
                "fixture-apply-refuse",
                [
                    {
                        "statement": "Not a recorded-revision sentence.",
                        "entry_class": "FACT",
                        "evidence": ["x.txt"],
                    }
                ],
            )
            path = root / "node.md"
            with self.assertRaises(ValueError):
                regenerate.apply_revision_move(path, 1, "e" * 40, "f" * 40)

    def test_apply_refuses_when_entry_index_is_out_of_range(self) -> None:
        """The other refusal branch on the same line (`entry_index >
        len(starts) or entry_index < 1`) -- only the "no statement match"
        branch above was previously covered.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_node(
                root,
                "node.md",
                "fixture-apply-out-of-range",
                [
                    {
                        "statement": "Only one evidence entry exists in this node.",
                        "entry_class": "FACT",
                        "evidence": ["x.txt"],
                    }
                ],
            )
            path = root / "node.md"
            with self.assertRaises(ValueError):
                regenerate.apply_revision_move(path, 2, "a" * 40, "b" * 40)


# ---------------------------------------------------------------------------
# evaluate_node / build_report -- end-to-end disposition, may-move vs MUST 4
# ---------------------------------------------------------------------------


class NodeDispositionTest(unittest.TestCase):
    def _fixture_with_trigger_and_stable_claim(self, second_claim_dirty: bool):
        """Shared fixture shape: commit A creates `trigger.txt` and
        `stable.txt`; commit B (the RECORDED revision) edits `trigger.txt`;
        commit C adds the node, citing both files. `--base`/`--head` for
        `impact.compute_impact` span A..C (so `trigger.txt`'s edit is what
        makes the node "impacted"); route-2 diffs the RECORDED revision (B)
        against C, where `trigger.txt` is unchanged since B by construction
        -- isolating whether `stable.txt` changing after B is what flips the
        disposition.
        """
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        init_repo(root)
        (root / "trigger.txt").write_text("v1\n")
        (root / "stable.txt").write_text("v1\n")
        sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")

        (root / "trigger.txt").write_text("v2\n")
        sha_b = commit_all(root, "commit B: edit trigger.txt (recorded revision)", "2020-01-02T00:00:00")

        if second_claim_dirty:
            (root / "stable.txt").write_text("v2\n")
            commit_all(root, "commit B2: edit stable.txt after recorded revision", "2020-01-02T12:00:00")

        write_node(
            root,
            "node.md",
            "fixture-disposition",
            [
                provenance_entry(sha_b),
                {
                    "statement": "Cites the triggering file.",
                    "entry_class": "FACT",
                    "evidence": ["trigger.txt"],
                },
                {
                    "statement": "Cites a second, stable file.",
                    "entry_class": "FACT",
                    "evidence": ["stable.txt"],
                },
            ],
        )
        sha_c = commit_all(root, "commit C: add node", "2020-01-03T00:00:00")
        return tmp, root, sha_a, sha_b, sha_c

    def test_every_claim_route2_clean_yields_may_move(self) -> None:
        tmp, root, sha_a, sha_b, sha_c = self._fixture_with_trigger_and_stable_claim(
            second_claim_dirty=False
        )
        with tmp:
            report = regenerate.build_report(root, sha_a, sha_c, root)
            self.assertEqual(len(report.nodes), 1)
            node_report = report.nodes[0]
            self.assertEqual(node_report.disposition, "may-move")
            self.assertEqual(node_report.blocking, [])
            self.assertEqual(node_report.recorded_revision, sha_b)

    def test_one_dirty_claim_forces_must_not_move(self) -> None:
        tmp, root, sha_a, sha_b, sha_c = self._fixture_with_trigger_and_stable_claim(
            second_claim_dirty=True
        )
        with tmp:
            report = regenerate.build_report(root, sha_a, sha_c, root)
            self.assertEqual(len(report.nodes), 1)
            node_report = report.nodes[0]
            self.assertEqual(node_report.disposition, "must-not-move (MUST 4)")
            self.assertIn(3, node_report.blocking)  # entry 3 cites stable.txt

    def test_apply_end_to_end_moves_only_the_may_move_node(self) -> None:
        tmp, root, sha_a, sha_b, sha_c = self._fixture_with_trigger_and_stable_claim(
            second_claim_dirty=False
        )
        with tmp:
            report = regenerate.build_report(root, sha_a, sha_c, root)
            regenerate.apply_report(report, root, sha_c, root)

            self.assertTrue(report.nodes[0].applied)
            self.assertEqual(report.nodes[0].new_revision, sha_c)

            after_node = _single_node(root)
            recorded_after = stale.extract_recorded_revision(after_node)
            self.assertEqual(recorded_after.sha, sha_c.lower())
            self.assertEqual(after_node.id, "fixture-disposition")

    def test_a_node_with_no_recorded_revision_is_must_not_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "trigger.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "trigger.txt").write_text("v2\n")
            write_node(
                root,
                "node.md",
                "fixture-no-recorded-revision",
                [
                    {
                        "statement": "No recorded-revision sentence and no commit citation anywhere.",
                        "entry_class": "FACT",
                        "evidence": ["trigger.txt"],
                    }
                ],
            )
            sha_c = commit_all(root, "commit C: edit + add node", "2020-01-02T00:00:00")

            report = regenerate.build_report(root, sha_a, sha_c, root)
            self.assertEqual(len(report.nodes), 1)
            node_report = report.nodes[0]
            self.assertEqual(node_report.disposition, "must-not-move (MUST 4)")
            self.assertIsNone(node_report.recorded_revision)

    def test_a_recorded_revision_absent_from_the_repo_is_must_not_move(self) -> None:
        """Regression for `evaluate_node`'s `commit_exists` gate (around
        lines 481-489) -- verified via mutation testing: removing that gate
        left all 23 pre-existing tests passing. This is the exact regression
        the module's own docstring says was previously caught: a recorded
        revision this repository never fetched/committed must resolve to
        MUST 4, not silently read as clean because `classify_claim`'s
        `diff_touched` call would otherwise see only a failed `git diff`'s
        empty stdout -- indistinguishable from a genuinely unchanged file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            commit_all(root, "commit A", "2020-01-01T00:00:00")
            head = _git(["rev-parse", "HEAD"], root).stdout.strip()

            missing_sha = "f" * 40
            write_node(
                root,
                "node.md",
                "fixture-missing-recorded-revision",
                [provenance_entry(missing_sha)],
            )

            node = _single_node(root)
            node_report = regenerate.evaluate_node(node, head, root, [])
            self.assertEqual(node_report.disposition, "must-not-move (MUST 4)")
            self.assertEqual(node_report.blocking, [])
            self.assertEqual(node_report.recorded_revision, missing_sha)

    def test_a_closed_claim_forces_must_not_move(self) -> None:
        """Regression: `ClassifyClaimTest` already covers `classify_claim`
        itself returning "closed" in isolation, but no `NodeDispositionTest`
        case previously drove a CLOSED (not merely dirty) claim all the way
        through `build_report`'s node-level disposition -- the integration
        path.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "trigger.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")

            (root / "trigger.txt").write_text("v2\n")
            sha_b = commit_all(
                root, "commit B: edit trigger.txt (recorded revision)", "2020-01-02T00:00:00"
            )

            write_node(
                root,
                "node.md",
                "fixture-closed-claim",
                [
                    provenance_entry(sha_b),
                    {
                        "statement": "Cites the triggering file.",
                        "entry_class": "FACT",
                        "evidence": ["trigger.txt"],
                    },
                    {
                        "statement": "Cites a non-file, commit-shaped reference -- closes route 2.",
                        "entry_class": "FACT",
                        "evidence": [f"commit {'a' * 40}"],
                    },
                ],
            )
            sha_c = commit_all(root, "commit C: add node", "2020-01-03T00:00:00")

            report = regenerate.build_report(root, sha_a, sha_c, root)
            self.assertEqual(len(report.nodes), 1)
            node_report = report.nodes[0]
            closed_claims = [claim for claim in node_report.claims if claim.status == "closed"]
            self.assertEqual(len(closed_claims), 1)
            self.assertEqual(closed_claims[0].entry_index, 3)
            self.assertEqual(node_report.disposition, "must-not-move (MUST 4)")
            self.assertIn(3, node_report.blocking)

    def test_main_apply_actually_rewrites_the_may_move_node_on_disk(self) -> None:
        """Regression for `main()`'s own `--apply` wiring (`if args.apply:
        apply_report(...)`, around lines 616-621) -- verified via mutation
        testing: no-opping that call left all 23 pre-existing tests passing.
        The only test previously proving an actual file move
        (`test_apply_end_to_end_moves_only_the_may_move_node`) calls
        `build_report`/`apply_report` directly, bypassing `main()` entirely.
        This drives `main()` itself, end-to-end, and asserts the file on
        disk actually changed.
        """
        tmp, root, sha_a, sha_b, sha_c = self._fixture_with_trigger_and_stable_claim(
            second_claim_dirty=False
        )
        with tmp:
            node = _single_node(root)
            before_recorded = stale.extract_recorded_revision(node)
            self.assertEqual(before_recorded.sha, sha_b.lower())
            before_text = node.path.read_text()

            with _captured_stdio():
                exit_code = regenerate.main(
                    [
                        "--base", sha_a,
                        "--head", sha_c,
                        "--root", str(root),
                        "--repo-dir", str(root),
                        "--apply",
                    ]
                )
            self.assertEqual(exit_code, 0)

            after_text = node.path.read_text()
            self.assertNotEqual(before_text, after_text)

            after_node = _single_node(root)
            after_recorded = stale.extract_recorded_revision(after_node)
            self.assertEqual(after_recorded.sha, sha_c.lower())


# ---------------------------------------------------------------------------
# Coverage gaps -- credential-shaped path redacted, never echoed
# ---------------------------------------------------------------------------


class CoverageGapRedactionTest(unittest.TestCase):
    def test_a_credential_shaped_changed_path_is_redacted_not_echoed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")

            secret_dir = root / "config"
            secret_dir.mkdir()
            (secret_dir / ".env").write_text("SECRET=1\n")
            sha_b = commit_all(root, "commit B: add .env", "2020-01-02T00:00:00")

            report = regenerate.build_report(root, sha_a, sha_b, root)
            self.assertEqual(report.coverage_gaps.redacted_count, 1)
            self.assertNotIn("config/.env", report.coverage_gaps.paths)
            for path in report.coverage_gaps.paths:
                self.assertNotIn(".env", path)

            rendered_json = report.to_json()
            self.assertNotIn(".env", rendered_json)
            rendered_text = report.to_text()
            self.assertNotIn(".env", rendered_text)


# ---------------------------------------------------------------------------
# Branch guard -- refuses on the default branch, permits any other
# ---------------------------------------------------------------------------


class BranchGuardTest(unittest.TestCase):
    def test_apply_refuses_on_the_default_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root, initial_branch="launchpad")
            (root / "trigger.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "trigger.txt").write_text("v2\n")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            self.assertEqual(regenerate.current_branch(root), "launchpad")

            with _captured_stdio() as (_stdout, stderr):
                exit_code = regenerate.main(
                    ["--base", sha_a, "--head", sha_b, "--root", str(root), "--repo-dir", str(root), "--apply"]
                )
            self.assertNotEqual(exit_code, 0)
            self.assertIn("launchpad", stderr.getvalue())
            self.assertIn("default branch", stderr.getvalue())

    def test_apply_permits_a_non_default_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root, initial_branch="feature-branch")
            (root / "trigger.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "trigger.txt").write_text("v2\n")
            sha_b = commit_all(root, "commit B", "2020-01-02T00:00:00")

            self.assertEqual(regenerate.current_branch(root), "feature-branch")

            with _captured_stdio() as (_stdout, stderr):
                exit_code = regenerate.main(
                    ["--base", sha_a, "--head", sha_b, "--root", str(root), "--repo-dir", str(root), "--apply"]
                )
            # No nodes exist in this fixture, so there is nothing to move --
            # the point of this test is that the branch guard itself does
            # NOT fire, not that a move happened.
            self.assertEqual(exit_code, 0)
            self.assertNotIn("default branch", stderr.getvalue())


# ---------------------------------------------------------------------------
# Determinism -- byte-identical report across two runs, cross-process
# ---------------------------------------------------------------------------

_SUBPROCESS_DRIVER = """
import sys
from pathlib import Path

sys.path.insert(0, {corpus_dir!r})
import regenerate

report = regenerate.build_report(Path({corpus_root!r}), {base!r}, {head!r}, Path({repo_dir!r}))
sys.stdout.write(report.to_json())
"""


def _run_build_report_in_subprocess(
    corpus_root: Path, base: str, head: str, repo_dir: Path, pythonhashseed: str
) -> str:
    script = _SUBPROCESS_DRIVER.format(
        corpus_dir=str(_CORPUS_DIR),
        corpus_root=str(corpus_root),
        base=base,
        head=head,
        repo_dir=str(repo_dir),
    )
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = pythonhashseed
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"build_report subprocess failed: {result.stderr}")
    return result.stdout


class DeterminismTest(unittest.TestCase):
    def test_report_is_byte_identical_across_two_subprocesses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            (root / "trigger.txt").write_text("v1\n")
            (root / "other.txt").write_text("v1\n")
            sha_a = commit_all(root, "commit A", "2020-01-01T00:00:00")
            (root / "trigger.txt").write_text("v2\n")
            sha_b = commit_all(root, "commit B: recorded revision", "2020-01-02T00:00:00")

            write_node(
                root,
                "node-one.md",
                "fixture-determinism-one",
                [
                    provenance_entry(sha_b),
                    {"statement": "Cites trigger.", "entry_class": "FACT", "evidence": ["trigger.txt"]},
                ],
            )
            write_node(
                root,
                "node-two.md",
                "fixture-determinism-two",
                [
                    provenance_entry(sha_b),
                    {"statement": "Also cites trigger.", "entry_class": "FACT", "evidence": ["trigger.txt"]},
                ],
            )
            sha_c = commit_all(root, "commit C: add nodes", "2020-01-03T00:00:00")

            first = _run_build_report_in_subprocess(root, sha_a, sha_c, root, "1")
            second = _run_build_report_in_subprocess(root, sha_a, sha_c, root, "2")
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
