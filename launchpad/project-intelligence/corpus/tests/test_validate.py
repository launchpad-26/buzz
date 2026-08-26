"""Unit tests for the deterministic corpus validator -- issue #623.

Run:  python3 -m unittest launchpad.project_intelligence.corpus.tests.test_validate
  or: python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"

These tests only ever point --root at fixtures under this directory, never at the
real launchpad/docs/corpus/ -- that root's own content (or lack of it) must never
change what this suite asserts.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"

# validate.py lives in a directory (project-intelligence/corpus/) that isn't a
# package (no __init__.py, matching this repo's existing project-intelligence/
# convention), so it's loaded by path rather than imported by dotted name.
_VALIDATE_PATH = Path(__file__).resolve().parent.parent / "validate.py"
_spec = importlib.util.spec_from_file_location("corpus_validate", _VALIDATE_PATH)
validate = importlib.util.module_from_spec(_spec)
sys.modules["corpus_validate"] = validate
_spec.loader.exec_module(validate)


class ValidFixtureTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        report = validate.validate_corpus(VALID_DIR)
        self.assertEqual(report.errors, [])

    def test_valid_fixture_actually_discovers_its_nodes(self) -> None:
        # errors == [] alone can't distinguish "genuinely clean" from "discovery
        # silently found nothing" -- assert the positive too. Five nodes as of
        # this test: node-a, node-b (auth citation), node-c (pinned url citation),
        # node-d (.env.example citation), node-e (all six citation forms).
        # generated/index.json is not .md and doesn't count.
        nodes = validate.load_nodes(VALID_DIR)
        self.assertEqual(len(nodes), 5)


class SchemaViolationTest(unittest.TestCase):
    def test_bad_schema_fixture_named_and_rejected(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "bad-schema")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("validator-fixture-bad-schema", report.errors[0])

    def test_schema_error_does_not_echo_the_offending_value(self) -> None:
        # The DoD's "without leaking private source content" applied to the one
        # path that bypasses the citation checks entirely: a node with a schema
        # error is skipped by find_citation_problems, so jsonschema's own rendered
        # message -- which quotes the instance verbatim -- was the only thing
        # printed about it. A cross-model review panel found this by supplying a
        # credential-shaped path where the schema required an array.
        report = validate.validate_corpus(INVALID_DIR / "leaky-schema-error")
        self.assertEqual(len(report.errors), 1)
        self.assertNotIn("id_rsa", report.errors[0])
        self.assertNotIn("some/private/path", report.errors[0])
        # Still actionable: it says where, and what the schema demanded instead.
        self.assertIn("evidence", report.errors[0])
        self.assertIn("array", report.errors[0])

    def test_unsafe_node_id_is_not_echoed_as_a_label(self) -> None:
        # The sibling leak: a schema-invalid node's `id` is unvalidated input, so
        # naming the node with it would reintroduce exactly what the test above
        # closes. Messages fall back to the file path when the id isn't kebab-case.
        report = validate.validate_corpus(INVALID_DIR / "unsafe-id")
        self.assertEqual(len(report.errors), 1)
        self.assertNotIn("id_rsa", report.errors[0])
        self.assertIn("unsafe-id", report.errors[0])  # named by path instead

    def test_label_helper_accepts_schema_shaped_ids(self) -> None:
        # The fallback must not swallow every id -- a valid kebab-case id is still
        # the label, otherwise every message would degrade to a path.
        self.assertEqual(validate._label("some-node-id", Path("x.md")), "some-node-id")
        self.assertEqual(validate._label("Not Kebab", Path("x.md")), "x.md")
        self.assertEqual(validate._label(None, Path("x.md")), "x.md")
        self.assertEqual(validate._label(12345, Path("x.md")), "x.md")


class DuplicateIdTest(unittest.TestCase):
    def test_duplicate_id_rejected_and_named(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "duplicate-id")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("validator-fixture-duplicate", report.errors[0])
        self.assertIn("duplicate id", report.errors[0])


class UnresolvedRelationshipTargetTest(unittest.TestCase):
    def test_unresolved_target_rejected_and_named(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "unresolved-target")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("validator-fixture-unresolved-target", report.errors[0])
        self.assertIn("no-such-node-anywhere", report.errors[0])


class MissingCitationTest(unittest.TestCase):
    def test_missing_citation_rejected_and_named(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "missing-citation")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("validator-fixture-missing-citation", report.errors[0])
        # Citations are located by position rather than quoted, so an author can
        # find the offender without the validator printing any citation value.
        self.assertIn("evidence entry 1, citation 1", report.errors[0])


class ProhibitedCitationTest(unittest.TestCase):
    def test_prohibited_citation_rejected_without_leaking_the_value(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "prohibited-citation")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("validator-fixture-prohibited-citation", report.errors[0])
        # The DoD's "without leaking private source content", taken literally: the
        # rejected value itself must never appear in the error output.
        self.assertNotIn("id_rsa", report.errors[0])

    def test_ordinary_auth_path_is_not_prohibited(self) -> None:
        # crates/buzz-auth is a real, ordinary, non-secret crate this repo ships.
        # An earlier draft of this plan's credential blocklist (*auth* as a bare
        # substring) would have rejected it; serina:review-plan caught this before
        # any code was written. node-b-auth-citation.md in the valid fixtures cites
        # exactly this path -- this test asserts it passes, not merely that the
        # whole valid directory happens to pass for unrelated reasons.
        self.assertFalse(validate._is_prohibited_citation("crates/buzz-auth/src/lib.rs"))

    def test_env_example_is_not_prohibited(self) -> None:
        # .env.example is this repo's own real, tracked, non-secret config
        # template (AGENTS.md: `cp .env.example .env`). An independent
        # review-code pass found the .env.* blocklist rejected it -- the same
        # class of over-broad match already caught once for buzz-auth, recurring
        # here until that pass found it. node-d-env-example-citation.md in the
        # valid fixtures cites exactly this path.
        self.assertFalse(validate._is_prohibited_citation(".env.example"))

    def test_env_local_is_still_prohibited(self) -> None:
        # The exemption is for conventional non-secret suffixes only -- a real
        # .env.local (or bare .env) must still be rejected.
        self.assertTrue(validate._is_prohibited_citation(".env.local"))
        self.assertTrue(validate._is_prohibited_citation(".env"))


class NonMappingFrontmatterTest(unittest.TestCase):
    """Frontmatter that is valid YAML but not a mapping (a bare list, string,
    number, or bool) must be reported as a parse error naming the file, never
    crash with an unhandled AttributeError -- the sibling case, at the top
    level, of MalformedEntryDoesNotCrashTest below. An independent review-final
    pass found this by trying the one adversarial shape the earlier review-code/
    review-tests round hadn't: a malformed top-level document rather than a
    malformed entry nested inside an already-parsed dict."""

    def test_non_mapping_frontmatter_reported_not_crashed(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "non-mapping-frontmatter")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("not a mapping", report.errors[0])


class MalformedEntryDoesNotCrashTest(unittest.TestCase):
    """A non-dict item in `evidence` or `relationships` must never crash the
    validator -- it must be reported (via node.error from schema validation,
    since node.schema.json already requires object-typed entries) rather than
    raising an unhandled AttributeError, per the DoD's "names the failing node,"
    which a stack trace does not. An independent review-code pass found this by
    constructing exactly this input against the shipped code."""

    def test_non_dict_evidence_item_does_not_crash(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"),
            data={"evidence": ["just a bare string, not an object"]},
            error="already reported by schema validation",
        )
        errors, unverified = validate.find_citation_problems(
            [node], validate.repo_root()
        )
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_non_dict_relationship_item_does_not_crash(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"),
            data={"relationships": ["just a bare string, not an object"]},
            error="already reported by schema validation",
        )
        errors = validate.find_unresolved_relationship_targets([node])
        self.assertEqual(errors, [])


class AbsolutePathCitationTest(unittest.TestCase):
    """An absolute-path citation must be rejected explicitly, not silently
    "validated" against the host filesystem -- pathlib's `/` operator discards
    the left operand when the right is absolute, so `repo_root / "/etc/passwd"`
    would otherwise evaluate to `/etc/passwd` itself. An independent review-code
    pass found this by citing a path that genuinely exists on the host."""

    def test_absolute_path_citation_rejected(self) -> None:
        errors, _ = _classify_one("/etc/passwd")
        self.assertEqual(len(errors), 1)
        self.assertIn("citation-check", errors[0])
        self.assertIn("repo-relative", errors[0])


def _classify_one(citation: str) -> tuple[list[str], list[str]]:
    """Run one citation through the real find_citation_problems path.

    Deliberately not calling _classify_citation directly: the message-building,
    node-labelling and redaction all live in find_citation_problems, and a test
    that skipped them would assert the classifier is right while proving nothing
    about what actually gets printed.
    """
    node = validate.LoadedNode(
        path=Path("synthetic"),
        id="citation-check",
        data={
            "evidence": [
                {"statement": "x", "entry_class": "FACT", "evidence": [citation]}
            ]
        },
    )
    return validate.find_citation_problems([node], validate.repo_root())


class UrlCitationTest(unittest.TestCase):
    """A repository file link must be pinned to a full commit SHA (ADR-0003); any
    other URL is unpinnable and uncheckable offline, so it is reported unverified.

    An earlier revision waved every `http`-prefixed string through untouched. A
    cross-model review panel found it, pointing at this repo's own passing fixture,
    which cited a mutable `blob/main` URL while ADR-0003 forbids exactly that.
    """

    def test_url_accepted_even_when_path_looks_credential_like(self) -> None:
        # The credential blocklist must still run AFTER the URL check -- an
        # independent review-code pass found it running first, silently rejecting
        # public URLs whose path merely resembled a credential filename.
        errors, unverified = _classify_one(
            "https://example.com/posts/id_rsa-security-best-practices"
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(unverified), 1)
        self.assertIn("external URL", unverified[0])

    def test_commit_pinned_github_url_accepted(self) -> None:
        errors, unverified = _classify_one(
            "https://github.com/launchpad-26/buzz/blob/"
            "69baedd197e5d35c9ae4736115789da59929e288/.env.example"
        )
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_commit_pinned_raw_github_url_accepted(self) -> None:
        errors, unverified = _classify_one(
            "https://raw.githubusercontent.com/launchpad-26/buzz/"
            "69baedd197e5d35c9ae4736115789da59929e288/Justfile"
        )
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_blob_main_url_rejected(self) -> None:
        errors, _ = _classify_one(
            "https://github.com/launchpad-26/buzz/blob/main/.env.example"
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("mutable ref", errors[0])

    def test_tag_pinned_url_rejected(self) -> None:
        # A tag is movable, and a short SHA is ambiguous. ADR-0003 says full SHA.
        for ref in ("v1.2.3", "69baedd"):
            with self.subTest(ref=ref):
                errors, _ = _classify_one(
                    f"https://github.com/launchpad-26/buzz/blob/{ref}/Justfile"
                )
                self.assertEqual(len(errors), 1)
                self.assertIn("mutable ref", errors[0])

    def test_markdown_link_is_unwrapped_before_pinning_is_judged(self) -> None:
        # ADR-0003's prescribed format is a markdown link, so `[label](url)` must
        # be judged by its target. An earlier revision compared the whole string
        # against `http`, so the prescribed format failed as a nonexistent file.
        pinned = (
            "[.env.example](https://github.com/launchpad-26/buzz/blob/"
            "69baedd197e5d35c9ae4736115789da59929e288/.env.example)"
        )
        errors, unverified = _classify_one(pinned)
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

        mutable = "[.env.example](https://github.com/launchpad-26/buzz/blob/main/.env.example)"
        errors, _ = _classify_one(mutable)
        self.assertEqual(len(errors), 1)
        self.assertIn("mutable ref", errors[0])


class CitationFormTest(unittest.TestCase):
    """CONTRACT.md section 3's six shapes, each routed to the right rule.

    An earlier revision passed every non-URL citation straight to Path.exists(),
    so five of the six were reported as missing files -- including the two
    positional forms CONTRACT.md uses as its own worked examples. A cross-model
    review panel found it.
    """

    def test_file_range_citation_accepted(self) -> None:
        errors, unverified = _classify_one(
            "launchpad/project-intelligence/corpus/validate.py:1-5"
        )
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_file_line_citation_accepted(self) -> None:
        errors, unverified = _classify_one(
            "launchpad/project-intelligence/corpus/validate.py:1077"
        )
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_bare_path_citation_accepted(self) -> None:
        errors, unverified = _classify_one("Justfile")
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_graph_edge_reported_unverified_not_missing(self) -> None:
        errors, unverified = _classify_one(
            "is_shared_gated_kind -> is_unshared_gated_event (1 hop)"
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(unverified), 1)
        self.assertIn("names no openable file", unverified[0])

    def test_tool_result_reported_unverified_not_missing(self) -> None:
        errors, unverified = _classify_one(
            "find_references('x', crate='buzz-core') -> no callers in this crate"
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(unverified), 1)

    def test_commit_reference_reported_unverified_not_missing(self) -> None:
        errors, unverified = _classify_one(
            "commit 69baedd197e5d35c9ae4736115789da59929e288 (2026-08-25) by Serina"
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(unverified), 1)
        self.assertIn("commit reference", unverified[0])

    def test_unrecognised_form_is_an_error_not_a_pass(self) -> None:
        # The unverified channel is for RECOGNISED-but-uncheckable forms only.
        # Free prose matching no form at all must fail, or the channel becomes a
        # way to launder anything past validation.
        errors, unverified = _classify_one("I read this somewhere once, honest")
        self.assertEqual(len(errors), 1)
        self.assertEqual(unverified, [])
        self.assertIn("six supported citation forms", errors[0])

    def test_malformed_line_position_rejected(self) -> None:
        errors, _ = _classify_one(
            "launchpad/project-intelligence/corpus/validate.py:9-2"
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("malformed line position", errors[0])

    def test_positional_citation_still_runs_the_credential_blocklist(self) -> None:
        # Parsing the position off must not become a way to smuggle a prohibited
        # path past the blocklist -- the extracted path is what gets checked.
        errors, _ = _classify_one("some/path/id_rsa:12")
        self.assertEqual(len(errors), 1)
        self.assertIn("prohibited", errors[0])
        self.assertNotIn("id_rsa", errors[0])


class CitationContainmentTest(unittest.TestCase):
    """A repo-relative citation must resolve to a real file INSIDE the repository.

    An earlier revision checked only `(repo_root / citation).exists()`, so a `..`
    chain resolved out onto the host filesystem and a bare directory name passed
    as though it were a file. A cross-model review panel found both.
    """

    def test_traversal_and_directory_citations_rejected(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "escaping-citation")
        self.assertEqual(len(report.errors), 2)
        joined = " ".join(report.errors)
        self.assertIn("resolves outside the repository", joined)
        self.assertIn("does not resolve to a real file", joined)

    def test_traversal_is_rejected_even_when_the_target_exists(self) -> None:
        # /etc/passwd genuinely exists on this host, so an existence check alone
        # would have called this citation valid.
        errors, _ = _classify_one("../../../../../../../../etc/passwd")
        self.assertEqual(len(errors), 1)
        self.assertIn("resolves outside the repository", errors[0])

    def test_directory_citation_rejected(self) -> None:
        errors, _ = _classify_one("launchpad")
        self.assertEqual(len(errors), 1)
        self.assertIn("does not resolve to a real file", errors[0])


class MutableUrlFixtureTest(unittest.TestCase):
    def test_mutable_url_fixture_rejected_and_named(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "mutable-url-citation")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("validator-fixture-mutable-url-citation", report.errors[0])
        self.assertIn("mutable ref", report.errors[0])


class OwnershipViolationTest(unittest.TestCase):
    def test_stray_non_md_file_rejected_and_named(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "misplaced-generated")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("index.json", report.errors[0])

    def test_non_md_file_under_generated_is_not_a_placement_error(self) -> None:
        # Only the reject-outside-generated/ direction was tested before -- this
        # proves the exemption itself has a passing-case fixture, not just that
        # the whole valid/ directory happens to pass for unrelated reasons.
        errors, _ = validate.find_ownership_violations(VALID_DIR)
        self.assertEqual(errors, [])

    def test_generated_artifact_is_reported_unverified_not_silently_passed(self) -> None:
        # Correct placement is only half of ADR-0028: derived views must also be
        # "never hand-authored, always reproducible from canonical Markdown", and
        # placement proves neither. No corpus generator exists yet to reproduce
        # them against, so the artifact is reported rather than passed in silence
        # -- a check that cannot run must not read as a check that was satisfied.
        # A cross-model review panel found the silent pass.
        errors, unverified = validate.find_ownership_violations(VALID_DIR)
        self.assertEqual(errors, [])
        self.assertEqual(len(unverified), 1)
        self.assertIn("index.json", unverified[0])
        self.assertIn("reproducibility", unverified[0])


class MissingInputTest(unittest.TestCase):
    """A nonexistent root is a missing input (fail closed). An existing root with
    zero nodes is a true, honest state -- launchpad/docs/corpus/ today, before
    #636/#639 land content -- and must pass, not fail. These are deliberately
    different outcomes; see this plan's own OPEN section for why."""

    def test_nonexistent_root_raises_corpus_root_missing(self) -> None:
        missing_path = FIXTURES_DIR / "does-not-exist-anywhere"
        self.assertFalse(missing_path.exists())
        with self.assertRaises(validate.CorpusRootMissing):
            validate.validate_corpus(missing_path)

    def test_main_reports_failure_for_nonexistent_root(self) -> None:
        missing_path = FIXTURES_DIR / "does-not-exist-anywhere"
        exit_code = validate.main(["--root", str(missing_path)])
        self.assertEqual(exit_code, 1)

    def test_existing_but_empty_root_passes_cleanly(self) -> None:
        empty_dir = FIXTURES_DIR / "empty-on-purpose"
        empty_dir.mkdir(exist_ok=True)
        try:
            self.assertEqual(validate.validate_corpus(empty_dir).errors, [])
            # errors == [] alone can't distinguish "genuinely empty" from
            # "discovery broke" -- assert zero nodes were found, not merely zero
            # errors, since both would look identical from errors alone.
            self.assertEqual(validate.load_nodes(empty_dir), [])
        finally:
            empty_dir.rmdir()


class UnverifiedChannelTest(unittest.TestCase):
    """The unverified channel must be visible and must not decide the exit code.

    Two failure modes it sits between. Failing on an unverifiable-by-nature
    citation would make CONTRACT.md's own commit/graph-edge/tool-result forms
    unusable in the corpus. Hiding them would let a green run claim it checked
    things it never opened. So: always printed, never fatal, and the summary line
    says how many there were rather than the bare word "clean".
    """

    def _run_main(self, root: Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            exit_code = validate.main(["--root", str(root)])
        return exit_code, out.getvalue(), err.getvalue()

    def test_unverified_items_print_but_do_not_fail_the_run(self) -> None:
        exit_code, stdout, stderr = self._run_main(VALID_DIR)
        self.assertEqual(exit_code, 0)
        self.assertIn("UNVERIFIED", stderr)
        self.assertIn("PASS", stdout)
        # The summary must not read as an unqualified all-clear when items were
        # reported but not checked.
        self.assertNotIn("corpus validation clean", stdout)
        self.assertIn("unverified", stdout)

    def test_errors_still_fail_even_alongside_unverified_items(self) -> None:
        exit_code, stdout, stderr = self._run_main(INVALID_DIR / "escaping-citation")
        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL", stderr)
        self.assertNotIn("PASS", stdout)

    def test_fully_clean_root_says_clean(self) -> None:
        # The unqualified wording must still be reachable, or the distinction the
        # test above relies on is meaningless.
        empty_dir = FIXTURES_DIR / "empty-for-clean-summary"
        empty_dir.mkdir(exist_ok=True)
        try:
            exit_code, stdout, _ = self._run_main(empty_dir)
            self.assertEqual(exit_code, 0)
            self.assertIn("corpus validation clean", stdout)
        finally:
            empty_dir.rmdir()


class SchemaDirExclusionTest(unittest.TestCase):
    """schema/ is #622's own infrastructure, never scanned as corpus content.

    Proven against a purpose-built fixture tree containing BOTH a schema/ file
    and a real sibling, not merely against today's real launchpad/docs/corpus/
    root -- that root currently has zero non-schema content, so a test asserting
    only "no file under schema/ leaked" against it would pass vacuously even if
    exclusion were broadened to reject everything. An independent review-tests
    pass found this.
    """

    def test_sibling_discovered_schema_dir_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "schema").mkdir()
            real_sibling = root / "real-sibling.md"
            inside_schema = root / "schema" / "inside-schema.md"
            real_sibling.write_text("not real frontmatter, only proving discovery\n")
            inside_schema.write_text("not real frontmatter, only proving exclusion\n")

            files = validate.discover_markdown_files(root)

            self.assertIn(real_sibling, files)
            self.assertNotIn(inside_schema, files)

    def test_real_corpus_root_currently_has_no_content_outside_schema(self) -> None:
        # A documentation-style sanity check on today's real state, not the
        # primary proof of exclusion (see test_sibling_discovered_schema_dir_
        # excluded above, which is the one that can actually fail on regression).
        root = validate.repo_root() / validate.DEFAULT_ROOT
        files = validate.discover_markdown_files(root)
        self.assertEqual(files, [])


if __name__ == "__main__":
    unittest.main()
