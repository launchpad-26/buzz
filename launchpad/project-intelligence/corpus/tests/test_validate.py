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

    def test_plain_http_scheme_does_not_bypass_the_pin_check(self) -> None:
        # An earlier revision anchored the GitHub patterns to `https://` while
        # routing on a prefix tuple that also contained `http://`, so the same
        # mutable blob link reopened the whole finding under one changed character
        # -- it fell past both patterns and came back a non-fatal external URL. An
        # independent review-code pass found it.
        errors, unverified = _classify_one(
            "http://github.com/launchpad-26/buzz/blob/main/.env.example"
        )
        self.assertEqual(len(errors), 1)
        self.assertEqual(unverified, [])
        self.assertIn("mutable ref", errors[0])

    def test_non_file_github_views_are_not_accepted_as_file_citations(self) -> None:
        # ADR-0003 cites "the cited file". `tree` is a directory listing; `blame`,
        # `commits` and `edit` are views of a file rather than citations of it. A
        # review-final pass found `tree/<sha>/<dir>` accepted as a verified file
        # citation, and `blame/main/...` slipping past the pin check entirely by
        # not matching the file-only pattern.
        sha = "69baedd197e5d35c9ae4736115789da59929e288"
        for verb in ("tree", "blame", "commits", "edit"):
            with self.subTest(verb=verb):
                errors, unverified = _classify_one(
                    f"https://github.com/launchpad-26/buzz/{verb}/{sha}/Justfile"
                )
                self.assertEqual(len(errors), 1)
                self.assertEqual(unverified, [])
                self.assertIn(verb, errors[0])

    def test_truncated_repository_url_still_faces_the_pin_check(self) -> None:
        # `.../blob/main` with no file after it matched neither pattern in an
        # earlier revision and fell through to the non-fatal external-URL branch,
        # so a truncated mutable link evaded the check a complete one fails. A
        # second cross-model review-final pass found this variant.
        for url in (
            "https://github.com/launchpad-26/buzz/blob/main",
            "https://github.com/launchpad-26/buzz/blob/main/",
            "https://raw.githubusercontent.com/launchpad-26/buzz/main",
        ):
            with self.subTest(url=url):
                errors, unverified = _classify_one(url)
                self.assertEqual(len(errors), 1)
                self.assertEqual(unverified, [])
                self.assertIn("mutable ref", errors[0])

    def test_pinned_url_naming_no_file_is_rejected(self) -> None:
        # Making the trailing path optional closed one hole and opened another: a
        # pinned link with nothing after the ref names a repository at a commit,
        # not the cited file, and came back "ok". A third cross-model review-final
        # pass found it. The path is optional to MATCH (so the pin check reaches
        # truncated links) and required to PASS.
        sha = "69baedd197e5d35c9ae4736115789da59929e288"
        for url in (
            f"https://github.com/launchpad-26/buzz/blob/{sha}",
            f"https://raw.githubusercontent.com/launchpad-26/buzz/{sha}",
        ):
            with self.subTest(url=url):
                errors, unverified = _classify_one(url)
                self.assertEqual(len(errors), 1)
                self.assertEqual(unverified, [])
                self.assertIn("names no file", errors[0])

    def test_mutable_non_file_view_fails_on_the_pin_first(self) -> None:
        # `blame/main` is wrong twice over; it must not escape by being wrong in a
        # way the file-verb check alone would not catch.
        errors, unverified = _classify_one(
            "https://github.com/launchpad-26/buzz/blame/main/Justfile"
        )
        self.assertEqual(len(errors), 1)
        self.assertEqual(unverified, [])

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
        # The line number is deliberately past the end of the file. Positional
        # citations are checked for their internal consistency and for the file
        # they name, NOT against the file's length -- bounds-checking a cited line
        # is staleness detection, which belongs with the staleness work rather than
        # here (see _classify_citation). Do not "fix" this to an in-range number:
        # that would silently drop the only coverage of that documented boundary.
        # A cross-model review-final pass raised the out-of-range line as a
        # separate, deferred finding; it is tracked, not forgotten.
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

    def test_arrow_alone_does_not_make_a_citation_recognised(self) -> None:
        # An earlier revision treated ANY string containing " -> " as a recognised
        # graph/tool citation and downgraded it to the non-fatal channel, so
        # arbitrary text -- including a prohibited path -- laundered past every
        # check and exited 0. A cross-model review-final pass found this fail-open.
        # Both forms are now matched by shape.
        for citation in (
            "private/path/id_rsa -> not a real citation",
            "something -> something else",
            "a -> b (not a hop count)",
            "not_a_call -> result",
        ):
            with self.subTest(citation=citation):
                errors, unverified = _classify_one(citation)
                self.assertEqual(len(errors), 1)
                self.assertEqual(unverified, [])
                self.assertIn("six supported citation forms", errors[0])
                self.assertNotIn("id_rsa", errors[0])

    def test_a_path_cannot_wear_a_graph_edge_suffix(self) -> None:
        # Matching the graph-edge shape with `\S+` endpoints still accepted
        # `private/path/id_rsa -> target (1 hop)`: adding a syntactically valid
        # suffix to a path re-opened the laundering the shape check was added to
        # close. A second cross-model review-final pass found it. Endpoints are
        # symbol names, and a symbol cannot contain a path separator.
        for citation in (
            "private/path/id_rsa -> target (1 hop)",
            "some/path -> other/path (2 hops)",
        ):
            with self.subTest(citation=citation):
                errors, unverified = _classify_one(citation)
                self.assertEqual(len(errors), 1)
                self.assertEqual(unverified, [])
                self.assertNotIn("id_rsa", errors[0])

    def test_prohibited_paths_embedded_in_expressions_are_caught(self) -> None:
        # Testing the whole string got this wrong in both directions at once, which
        # a third cross-model review-final pass demonstrated: it MISSED a path
        # buried in a tool result's arguments, because the string's basename is the
        # trailing prose. The blocklist runs per token now.
        errors, unverified = _classify_one(
            "find_references('private/path/.env', crate='buzz-core') -> no callers"
        )
        self.assertEqual(len(errors), 1)
        self.assertEqual(unverified, [])
        self.assertIn("prohibited", errors[0])
        self.assertNotIn(".env", errors[0])

    def test_safe_env_form_inside_an_expression_is_not_a_false_positive(self) -> None:
        # The other direction of the same defect: `.env.example` is expressly
        # exempt, and testing the whole string rejected a legitimate tool result
        # that merely mentioned it, because the exemption depends on reading the
        # token as a filename rather than as the suffix of a sentence.
        errors, unverified = _classify_one(
            "find_references('.env.example', crate='buzz-core') -> no callers"
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(unverified), 1)

    def test_prohibited_names_are_blocked_in_the_unopenable_forms_too(self) -> None:
        # Defence in depth. Two rounds have now found a way to satisfy one of these
        # shapes with hostile content, so the blocklist runs as a second,
        # independent reason the same laundering fails -- `id_rsa` alone is a valid
        # identifier, so the shape check cannot catch this one.
        errors, unverified = _classify_one("id_rsa -> target (1 hop)")
        self.assertEqual(len(errors), 1)
        self.assertEqual(unverified, [])
        self.assertIn("prohibited", errors[0])
        self.assertNotIn("id_rsa", errors[0])

    def test_malformed_line_position_rejected(self) -> None:
        errors, _ = _classify_one(
            "launchpad/project-intelligence/corpus/validate.py:9-2"
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("malformed line position", errors[0])

    def test_line_numbers_are_one_based(self) -> None:
        # The `start < 1` half of the same guard, which an independent
        # review-tests pass found untested: dropping it, or weakening it to
        # `start < 0`, would have left every other test passing. Both sides of the
        # boundary are pinned so neither direction can drift.
        errors, _ = _classify_one("Justfile:0")
        self.assertEqual(len(errors), 1)
        self.assertIn("malformed line position", errors[0])

        errors, unverified = _classify_one("Justfile:1")
        self.assertEqual(errors, [])
        self.assertEqual(unverified, [])

    def test_empty_citation_rejected(self) -> None:
        errors, unverified = _classify_one("   ")
        self.assertEqual(len(errors), 1)
        self.assertEqual(unverified, [])

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

    def test_traversal_is_rejected_before_the_target_is_ever_examined(self) -> None:
        # /etc/passwd genuinely exists on this host, so an existence check alone
        # would have called this citation valid. The containment check runs before
        # the existence check, so this test's outcome does not depend on that file
        # being present -- an independent review-tests pass flagged the earlier
        # wording here as overstating a host dependency the code does not have.
        errors, _ = _classify_one("../../../../../../../../etc/passwd")
        self.assertEqual(len(errors), 1)
        self.assertIn("resolves outside the repository", errors[0])

    def test_directory_citation_rejected(self) -> None:
        errors, _ = _classify_one("launchpad")
        self.assertEqual(len(errors), 1)
        self.assertIn("does not resolve to a real file", errors[0])

    def test_containment_errors_do_not_echo_the_citation(self) -> None:
        # CitationVerdict.detail is documented as never carrying the citation
        # value, and that holds for these branches today -- but nothing pinned it,
        # so a regression adding the resolved path "for debuggability" would leak a
        # host-filesystem location and pass every other test. An independent
        # review-tests pass found the gap.
        errors, _ = _classify_one("../../../../../../../../etc/passwd")
        self.assertNotIn("passwd", errors[0])
        self.assertNotIn("..", errors[0])

        errors, _ = _classify_one("launchpad")
        self.assertNotIn("launchpad/", errors[0])

    def test_citation_naming_an_unresolvable_symlink_reports_not_crashes(self) -> None:
        # The sibling of the discovery-side loop crash: a citation naming a
        # self-referential symlink inside the repository made .resolve() raise, and
        # it escaped as a traceback. A third cross-model review-final pass found
        # this second, unguarded site.
        link = validate.repo_root() / "citation-loop-probe.md"
        self.assertFalse(link.exists(), "probe path must not already exist")
        link.symlink_to(link)
        try:
            errors, _ = _classify_one("citation-loop-probe.md")
            self.assertEqual(len(errors), 1)
            self.assertIn("cannot be resolved", errors[0])
        finally:
            link.unlink()

    def test_citation_symlink_out_of_the_repo_is_rejected(self) -> None:
        # The symlink half of containment, which the docstring claims and no test
        # pinned: `.resolve()` dereferences before the containment check, so a link
        # inside the repo pointing outside is caught rather than followed. Written
        # into the repo tree because the citation must be repo-relative, and
        # removed again whatever happens.
        link = validate.repo_root() / "citation-symlink-probe.md"
        self.assertFalse(link.exists(), "probe path must not already exist")
        link.symlink_to("/etc/passwd")
        try:
            errors, _ = _classify_one("citation-symlink-probe.md")
            self.assertEqual(len(errors), 1)
            self.assertIn("resolves outside the repository", errors[0])
        finally:
            link.unlink()


class YamlParseFailureTest(unittest.TestCase):
    """A document that fails to PARSE never reaches schema validation, so the
    schema-error redaction cannot protect it -- PyYAML's exception text quotes the
    source line it choked on. A cross-model review-final pass found this leak after
    the schema-error one had already been closed: same defect, different door."""

    def test_yaml_error_does_not_echo_the_frontmatter(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "leaky-yaml-error")
        self.assertEqual(len(report.errors), 1)
        self.assertNotIn("id_rsa", report.errors[0])
        self.assertNotIn("some/private/path", report.errors[0])

    def test_yaml_error_still_locates_the_fault(self) -> None:
        # Redaction must not cost the author the ability to find it: line and
        # column are positions, not content, and PyYAML's `problem` text names YAML
        # tokens rather than the document's values.
        report = validate.validate_corpus(INVALID_DIR / "leaky-yaml-error")
        self.assertIn("leaky-yaml-error", report.errors[0])
        self.assertIn("frontmatter line", report.errors[0])

    def test_yaml_problem_text_cannot_leak_through_tags_or_aliases(self) -> None:
        # `problem` looks content-free -- "expected <block end>, but found ':'" --
        # and an earlier revision of this fix printed it for that reason. For an
        # undefined alias or an unknown tag, PyYAML interpolates the document's own
        # identifier into it: `found undefined alias 'PRIVATE_SOURCE_ID_RSA'`. A
        # second cross-model review-final pass found the residual leak with exactly
        # these two shapes, after every ordinary malformation came back clean.
        shapes = {
            "alias": "---\nid: x\nevidence: *PRIVATE_SOURCE_ID_RSA\n---\n\nbody\n",
            "tag": "---\nid: x\nevidence: !PRIVATE_SOURCE_ID_RSA v\n---\n\nbody\n",
        }
        for name, text in shapes.items():
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "node.md").write_text(text)
                report = validate.validate_corpus(root)
                self.assertEqual(len(report.errors), 1)
                self.assertNotIn("PRIVATE_SOURCE_ID_RSA", report.errors[0])
                self.assertNotIn("ID_RSA", report.errors[0].upper())

    def test_duplicate_frontmatter_key_rejected(self) -> None:
        # PyYAML resolves `id: first` / `id: second` silently to the last one, so a
        # node could carry two values for one field and pass validation with the
        # reader and the parser disagreeing about which is canonical. A second
        # cross-model review-final pass found this.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "node.md").write_text(
                "---\nid: first-value\nid: second-value\n---\n\nbody\n"
            )
            report = validate.validate_corpus(root)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("duplicate frontmatter key 'id'", report.errors[0])

    def test_duplicate_key_error_names_only_keys_the_schema_defines(self) -> None:
        # An earlier revision matched the key's SHAPE (`^[a-z][a-z0-9_]*$`), which a
        # third cross-model review-final pass defeated at once: `id_rsa` and
        # `private_source_id_rsa` are both perfectly good-looking field names, so
        # the shape test let exactly the content it existed to withhold through.
        # Membership of the committed schema is a fact; shape is a guess.
        for key in ("id_rsa", "private_source_id_rsa", "some/private/path/id_rsa"):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "node.md").write_text(
                    f'---\n"{key}": a\n"{key}": b\n---\n\nbody\n'
                )
                report = validate.validate_corpus(root)
                self.assertEqual(len(report.errors), 1)
                self.assertIn("duplicate frontmatter key", report.errors[0])
                self.assertNotIn("id_rsa", report.errors[0])

    def test_schema_property_names_covers_nested_definitions(self) -> None:
        # The allowlist must reach into $defs, or a duplicate `statement` inside an
        # evidence entry would be reported without naming the field and the error
        # would be needlessly hard to act on.
        names = validate._schema_property_names(
            validate.load_node_schema(validate.repo_root())
        )
        self.assertIn("id", names)          # top level
        self.assertIn("statement", names)   # $defs.evidenceEntry
        self.assertIn("target", names)      # $defs.relationship
        self.assertNotIn("id_rsa", names)

    def test_recursive_anchor_does_not_exhaust_the_stack(self) -> None:
        # `loop: &loop {self: *loop}` is legal YAML and composes to a cyclic node
        # graph, not a tree, so the duplicate-key walk descended forever and died
        # with an uncaught RecursionError. A third cross-model review-final pass
        # found it. The document is still rejected -- on its schema, not by crash.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "node.md").write_text(
                "---\nloop: &loop {self: *loop}\n---\n\nbody\n"
            )
            report = validate.validate_corpus(root)
            self.assertEqual(len(report.errors), 1)

    def test_unreadable_node_reported_not_crashed(self) -> None:
        # A dangling symlink whose target name resolves lexically inside the root
        # passes the canonical-location check and then fails to open. A third
        # cross-model review-final pass found the uncaught FileNotFoundError; the
        # exception's own text names the target, so it is not echoed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "broken.md").symlink_to("nowhere.md")
            report = validate.validate_corpus(root)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("could not be read", report.errors[0])
            self.assertNotIn("nowhere.md", report.errors[0])

    def test_nested_duplicate_key_rejected(self) -> None:
        # Detection recurses; a duplicate inside an evidence entry is the same
        # ambiguity one level down.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "node.md").write_text(
                "---\nid: x\nevidence:\n  - statement: a\n    statement: b\n"
                "---\n\nbody\n"
            )
            report = validate.validate_corpus(root)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("duplicate frontmatter key 'statement'", report.errors[0])

    def test_missing_delimiter_still_reported(self) -> None:
        # The non-YAMLError branch of the same handler: our own structural
        # ValueError, whose message is a fixed string with no document content.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "no-frontmatter.md").write_text("no delimiter here\n")
            report = validate.validate_corpus(root)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("frontmatter delimiter", report.errors[0])


class UnhashableIdTest(unittest.TestCase):
    """An unvalidated `id` can be a YAML list or dict, which is unhashable.

    Duplicate detection deliberately includes schema-invalid nodes -- two nodes can
    collide on an id neither of which validates -- so a non-str id reaches a dict
    key and a set member. Both crashed with an unhandled TypeError instead of the
    controlled, node-naming failure the DoD requires; a stack trace names no node.
    A cross-model review-final pass found the first site, and running its fixture
    against the whole validator surfaced the second.
    """

    def test_list_id_reported_not_crashed(self) -> None:
        report = validate.validate_corpus(INVALID_DIR / "unhashable-id")
        self.assertEqual(len(report.errors), 1)
        self.assertIn("unhashable-id", report.errors[0])  # named by path
        self.assertNotIn("id_rsa", report.errors[0])

    def test_both_id_consuming_checks_survive_a_non_str_id(self) -> None:
        # Exercised directly, because validate_corpus stops reporting past the
        # schema error and would mask a crash in either function below.
        node = validate.LoadedNode(
            path=Path("synthetic"),
            id=["some/private/path/id_rsa"],
            data={"relationships": [{"type": "references", "target": "elsewhere"}]},
            error="already reported by schema validation",
        )
        self.assertEqual(validate.find_duplicate_ids([node]), [])
        self.assertEqual(validate.find_unresolved_relationship_targets([node]), [])

    def test_dict_id_also_survives(self) -> None:
        node = validate.LoadedNode(
            path=Path("synthetic"), id={"nested": "mapping"}, error="reported"
        )
        self.assertEqual(validate.find_duplicate_ids([node]), [])
        self.assertEqual(validate.find_unresolved_relationship_targets([node]), [])


class SymlinkedNodeTest(unittest.TestCase):
    """A `.md` symlink pointing out of the corpus was walked and validated as
    canonical corpus content. ADR-0028 makes the corpus tree itself the canonical
    source; validating content that only appears to live there lends it authority
    it does not have. A cross-model review-final pass found this by symlinking a
    valid node in from outside and watching the run print PASS.

    Distinct from the citation-target containment in CitationContainmentTest: this
    governs which files are corpus content in the first place.
    """

    def test_symlink_out_of_the_corpus_is_not_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside"
            outside.mkdir()
            smuggled = outside / "smuggled.md"
            smuggled.write_text("---\nid: smuggled-node\n---\n\nnot corpus content\n")

            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            real = corpus / "real.md"
            real.write_text("---\nid: real-node\n---\n\ncorpus content\n")
            (corpus / "link.md").symlink_to(smuggled)

            files = validate.discover_markdown_files(corpus)

            # The real sibling proves discovery still works -- without it, a
            # regression that discovered nothing at all would pass this test.
            self.assertIn(real, files)
            self.assertNotIn(corpus / "link.md", files)

    def test_symlink_within_the_corpus_is_still_discovered(self) -> None:
        # The check must reject escapes, not symlinks as such.
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            (corpus / "nested").mkdir(parents=True)
            target = corpus / "nested" / "target.md"
            target.write_text("---\nid: target-node\n---\n\ncorpus content\n")
            (corpus / "link.md").symlink_to(target)

            files = validate.discover_markdown_files(corpus)
            self.assertIn(corpus / "link.md", files)

    def test_escaping_symlink_is_reported_not_merely_skipped(self) -> None:
        # Excluding it from validation is not the same as ignoring it. An earlier
        # revision only dropped it from discovery, so the run still printed PASS
        # with an unchecked file sitting in the tree -- a quieter version of the
        # problem the exclusion was added to fix. A second cross-model
        # review-final pass drew that distinction.
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside"
            outside.mkdir()
            smuggled = outside / "smuggled.md"
            smuggled.write_text("---\nid: smuggled-node\n---\n\nnot corpus\n")

            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "link.md").symlink_to(smuggled)

            report = validate.validate_corpus(corpus)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("link.md", report.errors[0])
            self.assertIn("not canonical corpus content", report.errors[0])

    def test_symlink_loop_reports_rather_than_crashing(self) -> None:
        # `.resolve()` raises RuntimeError on a self-referential link, and an
        # earlier revision let it escape as a traceback. A traceback names no node,
        # which the DoD forbids. A second cross-model review-final pass found this
        # by committing a self-referential link.
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "loop.md").symlink_to(corpus / "loop.md")

            report = validate.validate_corpus(corpus)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("loop.md", report.errors[0])
            self.assertIn("cannot be resolved", report.errors[0])


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
        self.assertIn("outside generated/", report.errors[0])

    def test_correctly_placed_generated_artifact_still_fails(self) -> None:
        # Correct placement is only half of ADR-0028: derived views must also be
        # "never hand-authored, always reproducible from canonical Markdown", and a
        # directory name proves neither. No corpus generator exists yet to
        # reproduce them against, so the artifact fails rather than passing.
        #
        # An earlier revision of this fix reported it as a non-fatal notice, which
        # a cross-model review-final pass rejected: a hand-authored artifact would
        # print one line and still exit 0, permitting exactly the state ADR-0028
        # forbids. The fixture is correctly PLACED on purpose -- if it were
        # misplaced it would fail for the other reason and prove nothing here.
        report = validate.validate_corpus(INVALID_DIR / "unestablished-generated")
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.unverified, [])
        self.assertIn("index.json", report.errors[0])
        self.assertIn("reproducibility", report.errors[0])
        # Distinguishable from the misplacement error above, or the two messages
        # would send an author to fix the wrong thing.
        self.assertNotIn("outside generated/", report.errors[0])

    def test_valid_fixtures_contain_no_ownership_violations(self) -> None:
        self.assertEqual(validate.find_ownership_violations(VALID_DIR), [])


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
    and a real sibling, rather than against the real launchpad/docs/corpus/ root
    alone. When this suite was written that root held zero non-schema content, so
    a test asserting only "no file under schema/ leaked" against it would have
    passed vacuously even if exclusion were broadened to reject everything. An
    independent review-tests pass found that. The fixture test below stays the
    primary proof for the same reason: it controls both sides of the comparison,
    where the real root only ever shows whatever happens to be committed.
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

    def test_real_corpus_root_discovery_matches_an_independent_walk(self) -> None:
        """Discovery over the real root returns EXACTLY the nodes that are there.

        This replaces `test_real_corpus_root_currently_has_no_content_outside_
        schema`, which asserted the root was EMPTY. That assertion was true when
        #623 wrote it and had a shelf life ending at the first authored node --
        #636's launchpad/docs/corpus/AGENTS.md, which is what broke it. A test
        encoding a temporary state as a permanent assertion fails on the change
        it was supposed to permit, and says nothing about the behaviour under
        test when it does.

        The first replacement asserted only "non-empty AND nothing from schema/",
        which an independent review-tests pass defeated immediately: replacing
        discover_markdown_files with a hardcoded `return [root / "AGENTS.md"]`
        -- a constant that never touches the filesystem -- satisfied both halves
        while proving neither discovery nor exclusion. Asserting that a check CAN
        fail is not the same as asserting it can only pass for the right reason.

        So the expectation is now derived from the filesystem independently of
        the function under test, and compared for equality. Measured against
        mutants of discover_markdown_files, this test catches:

            returns nothing          -> FAIL (caught)
            exclusion disabled       -> FAIL (caught)
            hardcoded constant       -> PASS (NOT caught today)

        The constant is not caught, and cannot be by any assertion made here
        while the real corpus holds exactly ONE node: `[root / "AGENTS.md"]` is
        the correct answer today, so a constant and a real walk are
        indistinguishable from outside. That is a property of the real tree, not
        of this assertion -- and it resolves itself the moment a second node
        lands, at which point the equality form catches constants and partial
        walks for free. `test_sibling_discovered_schema_dir_excluded` catches the
        constant NOW, because its fixture tree holds names no constant predicts.
        That test, not this one, is the proof of discovery behaviour.

        `assertNotEqual(expected, [])` is the guard against inheriting the
        original sin: with an empty corpus both sides would be [] and equality
        would pass vacuously. If that ever fires, the corpus is empty and this
        test should be read as reporting that, not as a discovery bug.

        The walk mirrors the canonical-location rule as well as the schema/
        exclusion, because discover_markdown_files drops symlinks resolving
        outside the root. A node symlinked in from elsewhere therefore fails
        here loudly rather than silently widening what counts as corpus content.
        """
        root = validate.repo_root() / validate.DEFAULT_ROOT
        resolved_root = root.resolve()

        expected = sorted(
            path
            for path in root.rglob("*.md")
            if path.relative_to(root).parts[0] != "schema"
            and path.resolve().is_relative_to(resolved_root)
        )

        self.assertNotEqual(expected, [])
        self.assertEqual(validate.discover_markdown_files(root), expected)


if __name__ == "__main__":
    unittest.main()
