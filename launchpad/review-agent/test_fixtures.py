#!/usr/bin/env python3
"""Controls for STEP 7 (#117): the five fixtures under fixtures/dimensions/.

A permanent, committed witness for the verification STEP 7's own done-when
requires, following the same convention test_findings.py adopted after an
earlier round of "verified with a throwaway script, deleted before commit" left
nobody able to reproduce what "verified" meant.

Not wired into run_controls.py -- that list is #120's own containment-control
suite; this file is scoped to the STEP 7 fixtures alone, the same reasoning
test_findings.py's own docstring gives for staying off that list.

Run:  python3 -m unittest test_fixtures    (from launchpad/review-agent/)
  or: python3 test_fixtures.py
"""

from __future__ import annotations

import glob
import json
import os
import re
import unittest

import contain
import fetch
import findings
import run_dimensions
from detect import detect

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(HERE, "fixtures", "dimensions")

DEFECT_FIXTURES = ("secrets-and-access", "claim-vs-evidence", "correctness-and-failure-modes")
LOCATION_BEARING_FIXTURES = DEFECT_FIXTURES + ("paraphrase",)
ALL_FIXTURE_SLUGS = LOCATION_BEARING_FIXTURES + ("description-of-an-attack",)
ALL_DIMENSION_SLUGS = frozenset(DEFECT_FIXTURES)


def _load(slug: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, f"{slug}.json"), encoding="utf-8") as handle:
        return json.load(handle)


def _new_side_line_of(diff_text: str, marker: str) -> int | None:
    """The new-side line number of the first line in ``diff_text`` containing
    ``marker``, parsing hunk headers exactly (no library, mirroring what a
    reviewer reading this diff by eye would count). Returns None if never found.
    """
    new_ln = None
    for line in diff_text.split("\n"):
        m = re.match(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@", line)
        if m:
            new_ln = int(m.group(3))
            continue
        if new_ln is None:
            continue
        if line.startswith("+"):
            if marker in line:
                return new_ln
            new_ln += 1
        elif line.startswith(" "):
            if marker in line:
                return new_ln
            new_ln += 1
        # a "-" (removed) line consumes no new-side line number
    return None


def _hunk_declared_counts_match_body(diff_text: str) -> list[str]:
    """Every ``@@ -M,N +M,N @@`` header's declared old/new line counts checked
    against what the hunk body actually contains. Returns a list of mismatch
    descriptions (empty if every hunk is internally consistent).

    Catches the exact defect a prior review found in one fixture's own diff:
    a header declaring more lines than its body carries is not a valid unified
    diff, and nothing else in this pipeline (fetch.from_payload, a future
    diff-structure-aware stage) currently rejects that on its own.
    """
    mismatches: list[str] = []
    old_declared = new_declared = None
    old_seen = new_seen = 0

    def _flush(hunk_index: int) -> None:
        if old_declared is None:
            return
        if old_seen != old_declared or new_seen != new_declared:
            mismatches.append(
                f"hunk {hunk_index}: declared -{old_declared}/+{new_declared}, "
                f"actual -{old_seen}/+{new_seen}"
            )

    hunk_index = 0
    for line in diff_text.split("\n"):
        m = re.match(r"^@@ -\d+,(\d+) \+\d+,(\d+) @@", line)
        if m:
            _flush(hunk_index)
            hunk_index += 1
            old_declared, new_declared = int(m.group(1)), int(m.group(2))
            old_seen = new_seen = 0
            continue
        if old_declared is None:
            continue
        if line.startswith("+"):
            new_seen += 1
        elif line.startswith("-"):
            old_seen += 1
        elif line.startswith(" "):
            old_seen += 1
            new_seen += 1
    _flush(hunk_index)
    return mismatches


class FixtureFilesExistTests(unittest.TestCase):
    def test_exactly_five_fixtures_exist(self):
        on_disk = sorted(
            os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(FIXTURES_DIR, "*.json"))
        )
        self.assertEqual(on_disk, sorted(ALL_FIXTURE_SLUGS))


class FixtureLoadsAsValidPayloadTests(unittest.TestCase):
    def test_every_fixture_loads_with_all_seven_surfaces_ok(self):
        for slug in ALL_FIXTURE_SLUGS:
            with self.subTest(slug=slug):
                surfaces = fetch.from_payload(os.path.join(FIXTURES_DIR, f"{slug}.json"))
                for entry_point in contain.ENTRY_POINTS:
                    self.assertEqual(
                        surfaces[entry_point].state,
                        "ok",
                        f"{slug}: {entry_point} did not load as ok",
                    )

    def test_four_location_bearing_fixtures_are_valid_run_dimensions_input(self):
        # "valid input to run_dimensions.py" per STEP 7's done-when: build_document
        # accepts it, the stub reviewer runs, and the merged document validates.
        for slug in LOCATION_BEARING_FIXTURES:
            with self.subTest(slug=slug):
                surfaces = fetch.from_payload(os.path.join(FIXTURES_DIR, f"{slug}.json"))
                nonce = contain.make_nonce(seed=f"step7-{slug}")
                doc = run_dimensions.build_document(
                    0, "a" * 40, "b" * 40, surfaces, list(ALL_DIMENSION_SLUGS), nonce,
                )
                self.assertEqual(findings.validate(doc), [])


class FixtureMetadataShapeTests(unittest.TestCase):
    def test_each_fixture_declares_a_valid_entry_point(self):
        for slug in ALL_FIXTURE_SLUGS:
            with self.subTest(slug=slug):
                meta = _load(slug)["_fixture"]
                self.assertIn(meta["planted_entry_point"], contain.ENTRY_POINTS)

    def test_each_fixture_declares_must_find_and_must_not_find(self):
        for slug in ALL_FIXTURE_SLUGS:
            with self.subTest(slug=slug):
                meta = _load(slug)["_fixture"]
                self.assertIn("must_find", meta)
                self.assertIn("must_not_find", meta)
                # every named dimension is one of the three real slugs
                for d in meta["must_find"] + meta["must_not_find"]:
                    self.assertIn(d, ALL_DIMENSION_SLUGS)
                # must_find and must_not_find never overlap
                self.assertEqual(set(meta["must_find"]) & set(meta["must_not_find"]), set())

    def test_four_location_bearing_fixtures_declare_file_and_line(self):
        for slug in LOCATION_BEARING_FIXTURES:
            with self.subTest(slug=slug):
                meta = _load(slug)["_fixture"]
                self.assertIsNotNone(meta["planted_file"])
                self.assertIsInstance(meta["planted_line"], int)

    def test_description_of_an_attack_declares_no_location(self):
        meta = _load("description-of-an-attack")["_fixture"]
        self.assertIsNone(meta["planted_file"])
        self.assertIsNone(meta["planted_line"])
        self.assertIn("location_note", meta)
        self.assertTrue(meta["location_note"])

    def test_three_defect_fixtures_name_exactly_one_must_find_dimension(self):
        # each defect fixture tests exclusions: the OTHER two dimensions must
        # explicitly be named as must-not-find, not merely absent from must_find.
        for slug in DEFECT_FIXTURES:
            with self.subTest(slug=slug):
                meta = _load(slug)["_fixture"]
                self.assertEqual(meta["must_find"], [slug])
                self.assertEqual(set(meta["must_not_find"]), ALL_DIMENSION_SLUGS - {slug})

    def test_paraphrase_fixture_must_be_found_by_all_three_dimensions(self):
        # per STEP 5 (not yet built): the injection clause is identical across
        # all three definitions, so this fixture is everyone's responsibility.
        meta = _load("paraphrase")["_fixture"]
        self.assertEqual(set(meta["must_find"]), ALL_DIMENSION_SLUGS)
        self.assertEqual(meta["must_not_find"], [])


class HunkHeaderIntegrityTests(unittest.TestCase):
    """Every fixture's pr_diff must be a structurally valid unified diff --
    checked on all FIVE fixtures, not only the four with a planted location.
    A hunk header's declared counts must match its own body; this is a
    prerequisite for the line-number checks below, not a substitute for them.
    """

    def test_every_fixtures_hunk_header_counts_match_its_body(self):
        for slug in ALL_FIXTURE_SLUGS:
            with self.subTest(slug=slug):
                data = _load(slug)
                mismatches = _hunk_declared_counts_match_body(data["pr_diff"])
                self.assertEqual(mismatches, [], f"{slug}: {mismatches}")


class PlantedLocationIsRealTests(unittest.TestCase):
    """The declared planted_file/planted_line must be independently derivable
    from the fixture's own pr_diff text -- not just asserted in its metadata.
    """

    _MARKERS = {
        "secrets-and-access": "DEPLOY_DB_PASSWORD",
        "claim-vs-evidence": '"--verbose"',
        "correctness-and-failure-modes": "return True",
        "paraphrase": "walked this patch",
    }

    def test_declared_line_matches_the_diffs_own_new_side_numbering(self):
        for slug, marker in self._MARKERS.items():
            with self.subTest(slug=slug):
                data = _load(slug)
                actual_line = _new_side_line_of(data["pr_diff"], marker)
                self.assertIsNotNone(actual_line, f"{slug}: marker not found in pr_diff")
                self.assertEqual(actual_line, data["_fixture"]["planted_line"])

    def test_declared_file_appears_as_the_diffs_own_plus_plus_plus_header(self):
        for slug in LOCATION_BEARING_FIXTURES:
            with self.subTest(slug=slug):
                data = _load(slug)
                declared_file = data["_fixture"]["planted_file"]
                self.assertIn(f"+++ b/{declared_file}", data["pr_diff"])


class DetectorBehaviourTests(unittest.TestCase):
    """Confirms STEP 7's own detect.py-facing done-when criteria."""

    def test_paraphrase_fixture_text_evades_the_deterministic_detector(self):
        data = _load("paraphrase")
        self.assertEqual(detect(data["pr_diff"], "pr_diff"), [])

    def test_description_of_an_attack_produces_no_finding_on_any_surface(self):
        data = _load("description-of-an-attack")
        for entry_point in contain.ENTRY_POINTS:
            with self.subTest(entry_point=entry_point):
                self.assertEqual(detect(data[entry_point], entry_point), [])

    def test_three_defect_fixtures_produce_no_accidental_containment_findings(self):
        # sanity: these are not injection fixtures, and should not be mistaken
        # for one by the deterministic layer either.
        for slug in DEFECT_FIXTURES:
            data = _load(slug)
            for entry_point in contain.ENTRY_POINTS:
                with self.subTest(slug=slug, entry_point=entry_point):
                    self.assertEqual(detect(data[entry_point], entry_point), [])


if __name__ == "__main__":
    unittest.main()
