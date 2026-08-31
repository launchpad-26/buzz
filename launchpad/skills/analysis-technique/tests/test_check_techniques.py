#!/usr/bin/env python3
"""
Unit tests for check-techniques script.

Tests validation of technique files against the RCA contract.

Every test runs against a throwaway copy of the skill directory. check-techniques
resolves techniques/ relative to its own __file__, so isolating it means copying
the script into a temp tree rather than changing the working directory. Validating
fixtures inside the real library would also mean each result depended on whether
the eleven shipped techniques happened to be valid.
"""

import unittest
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil

class TestCheckTechniques(unittest.TestCase):
    """Test check-techniques script."""

    @classmethod
    def setUpClass(cls):
        """Locate the real script, template and fixtures. All read-only sources."""
        skill_dir = Path(__file__).parent.parent
        cls.real_script = skill_dir / 'scripts' / 'check-techniques'
        cls.real_techniques = skill_dir / 'techniques'
        cls.real_template = cls.real_techniques / '_TEMPLATE.md'
        cls.fixtures_dir = Path(__file__).parent / 'fixtures'

        # Snapshot the real library so test_real_library_untouched can prove
        # this suite left it alone.
        cls.real_listing_before = sorted(p.name for p in cls.real_techniques.glob('*.md'))

    def setUp(self):
        """Build a throwaway skill directory containing a copy of the script."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)

        self.skill_dir = Path(tmp.name) / 'analysis-technique'
        self.techniques_dir = self.skill_dir / 'techniques'
        self.techniques_dir.mkdir(parents=True)
        (self.skill_dir / 'scripts').mkdir()

        self.script_path = self.skill_dir / 'scripts' / 'check-techniques'
        shutil.copy(self.real_script, self.script_path)
        shutil.copy(self.real_template, self.techniques_dir / '_TEMPLATE.md')

    def install(self, *fixture_names):
        """Copy fixtures into the temp techniques directory."""
        for name in fixture_names:
            src = self.fixtures_dir / name
            if not src.exists():
                self.skipTest(f"Fixture not found: {name}")
            shutil.copy(src, self.techniques_dir / name)

    def run_check(self, args=None, cwd=None):
        """Run the temp copy of check-techniques."""
        if cwd is None:
            cwd = self.skill_dir
        cmd = [sys.executable, str(self.script_path)]
        if args:
            cmd.extend(args)
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result

    def test_template_passes(self):
        """Test that _TEMPLATE.md passes validation."""
        result = self.run_check()
        self.assertEqual(result.returncode, 0, f"Template should pass: {result.stderr}")

    def test_shipped_library_passes(self):
        """The eleven shipped technique files validate against the contract."""
        for src in self.real_techniques.glob('*.md'):
            shutil.copy(src, self.techniques_dir / src.name)

        result = self.run_check()
        self.assertEqual(result.returncode, 0, f"Shipped library should pass: {result.stderr}")

    def test_valid_technique_files(self):
        """Test that valid technique files pass."""
        self.install('valid-technique-1.md', 'valid-technique-2.md')

        result = self.run_check()
        self.assertEqual(result.returncode, 0, f"Valid files should pass: {result.stderr}")

    def test_missing_key(self):
        """Test that missing required key is caught."""
        self.install('missing-key.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on missing key")
        self.assertIn("missing-key.md", result.stderr, "Should report the filename")

    def test_bad_cost(self):
        """Test that invalid cost value is caught."""
        self.install('bad-cost.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on bad cost")
        self.assertIn("bad-cost.md", result.stderr)
        self.assertIn("cost", result.stderr.lower())

    def test_bad_reduces_with(self):
        """Test that invalid reduces-with value is caught."""
        self.install('bad-reduces-with.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on bad reduces-with")
        self.assertIn("bad-reduces-with.md", result.stderr)
        self.assertIn("reduces-with", result.stderr.lower())

    def test_name_filename_mismatch(self):
        """Test that name/filename mismatch is caught."""
        self.install('name-mismatch.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on name/filename mismatch")
        self.assertIn("name-mismatch.md", result.stderr)

    def test_missing_heading(self):
        """Test that missing required heading is caught."""
        self.install('missing-heading.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on missing heading")
        self.assertIn("missing-heading.md", result.stderr)
        self.assertIn("Done when", result.stderr)

    def test_empty_heading(self):
        """Test that empty heading content is caught."""
        self.install('empty-heading.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on empty heading")
        self.assertIn("empty-heading.md", result.stderr)
        self.assertIn("empty", result.stderr.lower())

    def test_malformed_yaml(self):
        """Test that malformed YAML is caught."""
        self.install('malformed-yaml.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on malformed YAML")
        self.assertIn("malformed-yaml.md", result.stderr)

    def test_no_frontmatter(self):
        """Test that missing frontmatter is caught."""
        self.install('no-frontmatter.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail on missing frontmatter")
        self.assertIn("no-frontmatter.md", result.stderr)

    def test_multiple_errors_reported(self):
        """Test that all errors are reported, not just the first."""
        self.install('bad-cost.md', 'missing-heading.md')

        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, "Should fail")
        # Should report both files
        self.assertIn("bad-cost.md", result.stderr)
        self.assertIn("missing-heading.md", result.stderr)

    def test_bad_usage(self):
        """Test that bad command line usage exits with code 2."""
        result = self.run_check(['--invalid-flag'])
        self.assertEqual(result.returncode, 2)

    def test_real_library_untouched(self):
        """The suite must not add fixtures to, or remove files from, the real library."""
        listing_now = sorted(p.name for p in self.real_techniques.glob('*.md'))
        self.assertEqual(
            listing_now, self.real_listing_before,
            "Tests changed the real techniques/ directory"
        )


if __name__ == '__main__':
    unittest.main()
