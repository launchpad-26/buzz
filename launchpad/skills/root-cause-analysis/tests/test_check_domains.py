#!/usr/bin/env python3
"""Unit tests for check-domains validator."""

import unittest
import tempfile
import shutil
import os
import sys
import subprocess
from pathlib import Path


class CheckDomainsTest(unittest.TestCase):
    """Test the check-domains validator."""

    @classmethod
    def setUpClass(cls):
        """Set up paths."""
        cls.script_path = Path(__file__).parent.parent / 'scripts' / 'check-domains'
        cls.fixtures_dir = Path(__file__).parent / 'fixtures'

    def run_check_domains(self, domains_dir):
        """Run check-domains on a directory. Returns (returncode, stderr_output)."""
        result = subprocess.run(
            [sys.executable, str(self.script_path)],
            cwd=str(domains_dir.parent),
            capture_output=True,
            text=True,
            env={**os.environ, 'PYTHONPATH': str(self.script_path.parent)}
        )
        return result.returncode, result.stderr

    def test_passes_on_template(self):
        """Test that check-domains passes on _TEMPLATE.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            # Copy the actual _TEMPLATE.md from the project
            template_src = Path(__file__).parent.parent.parent / 'domains' / '_TEMPLATE.md'
            if template_src.exists():
                shutil.copy(template_src, domains_dir / '_TEMPLATE.md')
            else:
                # Create a valid template for testing
                (domains_dir / '_TEMPLATE.md').write_text(
                    """---
name: _TEMPLATE
summary: Template for domain files
layer: Template
---

# Template

## First five checks
1. First check
2. Second check
3. Third check
4. Fourth check
5. Fifth check

## Evidence sources
Evidence sources here.

## Common root causes in this layer
Root causes here.

## Diagnostic commands and queries
Commands here.

## Escalation signals
Escalation info.
"""
                )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertEqual(returncode, 0, f"Expected success but got: {stderr}")

    def test_fails_on_four_checks(self):
        """Test that check-domains fails when First five checks has only 4 items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            shutil.copy(
                self.fixtures_dir / 'four_checks.md',
                domains_dir / 'four_checks.md'
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on 4 checks")
            self.assertIn('exactly 5 numbered items', stderr,
                         f"Expected '5 numbered items' error, got: {stderr}")
            self.assertIn('found 4', stderr,
                         f"Expected 'found 4' in error, got: {stderr}")

    def test_fails_on_six_checks(self):
        """Test that check-domains fails when First five checks has 6 items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            shutil.copy(
                self.fixtures_dir / 'six_checks.md',
                domains_dir / 'six_checks.md'
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on 6 checks")
            self.assertIn('exactly 5 numbered items', stderr,
                         f"Expected '5 numbered items' error, got: {stderr}")
            self.assertIn('found 6', stderr,
                         f"Expected 'found 6' in error, got: {stderr}")

    def test_fails_on_unnumbered_list(self):
        """Test that check-domains fails when First five checks uses bullet list instead of numbered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            shutil.copy(
                self.fixtures_dir / 'unnumbered_list.md',
                domains_dir / 'unnumbered_list.md'
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on unnumbered list")
            self.assertIn('exactly 5 numbered items', stderr,
                         f"Expected '5 numbered items' error, got: {stderr}")
            self.assertIn('found 0', stderr,
                         f"Expected 'found 0' in error, got: {stderr}")

    def test_reports_all_failing_files(self):
        """Test that check-domains reports every failing file, not just the first."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            # Create two failing files
            shutil.copy(
                self.fixtures_dir / 'four_checks.md',
                domains_dir / 'four_checks.md'
            )
            shutil.copy(
                self.fixtures_dir / 'six_checks.md',
                domains_dir / 'six_checks.md'
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure")
            # Both files should be mentioned
            self.assertIn('four_checks.md', stderr,
                         f"Expected 'four_checks.md' in output, got: {stderr}")
            self.assertIn('six_checks.md', stderr,
                         f"Expected 'six_checks.md' in output, got: {stderr}")

    def test_exits_nonzero_on_bad_frontmatter(self):
        """Test that check-domains exits non-zero on malformed frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            (domains_dir / 'bad_frontmatter.md').write_text(
                """no-starting-dashes
name: bad
---

# Test
"""
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected non-zero exit on bad frontmatter")
            self.assertIn('Frontmatter not parseable', stderr,
                         f"Expected 'Frontmatter not parseable' error, got: {stderr}")

    def test_missing_required_keys(self):
        """Test that check-domains reports missing required frontmatter keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            (domains_dir / 'missing_keys.md').write_text(
                """---
name: missing_keys
summary: Missing layer key
---

# Test

## First five checks
1. A
2. B
3. C
4. D
5. E

## Evidence sources
Info.

## Common root causes in this layer
Info.

## Diagnostic commands and queries
Info.

## Escalation signals
Info.
"""
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on missing key")
            self.assertIn("Missing frontmatter key 'layer'", stderr,
                         f"Expected missing key error, got: {stderr}")

    def test_name_mismatch(self):
        """Test that check-domains fails when name doesn't match filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            (domains_dir / 'actual_name.md').write_text(
                """---
name: wrong_name
summary: Name mismatch
layer: Test
---

# Test

## First five checks
1. A
2. B
3. C
4. D
5. E

## Evidence sources
Info.

## Common root causes in this layer
Info.

## Diagnostic commands and queries
Info.

## Escalation signals
Info.
"""
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on name mismatch")
            self.assertIn("does not match filename", stderr,
                         f"Expected name mismatch error, got: {stderr}")

    def test_missing_sections(self):
        """Test that check-domains fails when required sections are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            (domains_dir / 'missing_section.md').write_text(
                """---
name: missing_section
summary: Missing a section
layer: Test
---

# Test

## First five checks
1. A
2. B
3. C
4. D
5. E

## Evidence sources
Info.

## Escalation signals
Info.
"""
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on missing section")
            self.assertIn("Missing section", stderr,
                         f"Expected missing section error, got: {stderr}")

    def test_empty_section(self):
        """Test that check-domains fails when a required section is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            (domains_dir / 'empty_section.md').write_text(
                """---
name: empty_section
summary: Empty section
layer: Test
---

# Test

## First five checks
1. A
2. B
3. C
4. D
5. E

## Evidence sources

## Common root causes in this layer
Info.

## Diagnostic commands and queries
Info.

## Escalation signals
Info.
"""
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on empty section")
            self.assertIn("is empty", stderr,
                         f"Expected empty section error, got: {stderr}")

    def test_wrong_section_order(self):
        """Test that check-domains fails when sections are out of order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            (domains_dir / 'wrong_order.md').write_text(
                """---
name: wrong_order
summary: Wrong section order
layer: Test
---

# Test

## Evidence sources
Info.

## First five checks
1. A
2. B
3. C
4. D
5. E

## Common root causes in this layer
Info.

## Diagnostic commands and queries
Info.

## Escalation signals
Info.
"""
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertNotEqual(returncode, 0, "Expected failure on wrong order")
            self.assertIn("not in required order", stderr,
                         f"Expected wrong order error, got: {stderr}")

    def test_valid_file_passes(self):
        """Test that a valid domain file passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domains_dir = tmpdir_path / 'domains'
            domains_dir.mkdir()

            shutil.copy(
                self.fixtures_dir / 'valid.md',
                domains_dir / 'valid.md'
            )

            returncode, stderr = self.run_check_domains(domains_dir)
            self.assertEqual(returncode, 0, f"Expected success but got: {stderr}")


if __name__ == '__main__':
    unittest.main()
