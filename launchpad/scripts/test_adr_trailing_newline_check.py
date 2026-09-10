#!/usr/bin/env python3
"""Controls for adr_trailing_newline_check.

Each case writes into a temporary decisions directory rather than touching
launchpad/decisions/ itself, so the suite never depends on -- or risks
mutating -- the real ADR tree.

Run:  python3 -m unittest discover -s launchpad/scripts
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import adr_trailing_newline_check as m


class FindViolationsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.decisions_dir = Path(self._tmp.name)

    def write(self, name: str, data: bytes):
        (self.decisions_dir / name).write_bytes(data)

    def test_well_formed_file_passes(self):
        self.write("ADR-0001-example.md", b"# ADR-0001\n\nBody.\n")
        self.assertEqual(m.find_violations(self.decisions_dir), [])

    def test_no_trailing_newline_fails(self):
        self.write("ADR-0002-example.md", b"# ADR-0002\n\nBody.")
        failures = m.find_violations(self.decisions_dir)
        self.assertEqual(len(failures), 1)
        self.assertIn("ADR-0002-example.md", failures[0])
        self.assertIn("no trailing newline", failures[0])

    def test_two_trailing_newlines_fails(self):
        self.write("ADR-0003-example.md", b"# ADR-0003\n\nBody.\n\n")
        failures = m.find_violations(self.decisions_dir)
        self.assertEqual(len(failures), 1)
        self.assertIn("ADR-0003-example.md", failures[0])
        self.assertIn("more than one trailing newline", failures[0])

    def test_empty_file_is_skipped(self):
        self.write("ADR-0004-example.md", b"")
        self.assertEqual(m.find_violations(self.decisions_dir), [])

    def test_non_adr_file_is_ignored(self):
        # README.md is a real file in launchpad/decisions/ today and is not
        # an ADR -- #1453 is scoped to ADR files, so a non-ADR file with no
        # trailing newline must not be reported.
        self.write("README.md", b"No trailing newline here.")
        self.assertEqual(m.find_violations(self.decisions_dir), [])

    def test_multiple_files_report_only_the_offenders(self):
        self.write("ADR-0005-good.md", b"# ADR-0005\n")
        self.write("ADR-0006-bad.md", b"# ADR-0006")
        failures = m.find_violations(self.decisions_dir)
        self.assertEqual(len(failures), 1)
        self.assertIn("ADR-0006-bad.md", failures[0])


class MainTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.decisions_dir = self.root / m.DECISIONS_REL
        self.decisions_dir.mkdir(parents=True)

    def test_exits_zero_when_clean(self):
        (self.decisions_dir / "ADR-0001-example.md").write_bytes(b"content\n")
        self.assertEqual(m.main(["prog", str(self.root)]), 0)

    def test_exits_one_when_violations_present(self):
        (self.decisions_dir / "ADR-0001-example.md").write_bytes(b"content")
        self.assertEqual(m.main(["prog", str(self.root)]), 1)

    def test_exits_one_when_decisions_dir_missing(self):
        empty_root = self.root / "no-such-tree"
        self.assertEqual(m.main(["prog", str(empty_root)]), 1)


if __name__ == "__main__":
    unittest.main()
