#!/usr/bin/env python3
"""
Unit tests for build-routing script.

Tests routing table generation from technique frontmatter.

Every test runs against a throwaway copy of the skill directory, never against
the real techniques/ or ROUTING.md. build-routing resolves both paths relative
to its own __file__, so isolating it means copying the script into a temp tree
rather than changing the working directory.
"""

import unittest
import subprocess
import sys
from pathlib import Path
import shutil
import tempfile

class TestBuildRouting(unittest.TestCase):
    """Test build-routing script."""

    @classmethod
    def setUpClass(cls):
        """Locate the real script, template and fixtures. All read-only sources."""
        skill_dir = Path(__file__).parent.parent
        cls.real_script = skill_dir / 'scripts' / 'build-routing'
        cls.real_techniques = skill_dir / 'techniques'
        cls.real_template = cls.real_techniques / '_TEMPLATE.md'
        cls.real_routing = skill_dir / 'ROUTING.md'
        cls.fixtures_dir = Path(__file__).parent / 'fixtures'

        # Snapshot the real library so test_real_library_untouched can prove
        # this suite left it alone.
        cls.real_listing_before = sorted(p.name for p in cls.real_techniques.glob('*.md'))
        cls.real_routing_existed = cls.real_routing.exists()

    def setUp(self):
        """Build a throwaway skill directory containing a copy of the script."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)

        self.skill_dir = Path(tmp.name) / 'analysis-technique'
        self.techniques_dir = self.skill_dir / 'techniques'
        self.techniques_dir.mkdir(parents=True)
        (self.skill_dir / 'scripts').mkdir()

        self.script_path = self.skill_dir / 'scripts' / 'build-routing'
        shutil.copy(self.real_script, self.script_path)
        shutil.copy(self.real_template, self.techniques_dir / '_TEMPLATE.md')

        self.routing_path = self.skill_dir / 'ROUTING.md'

    def install(self, *fixture_names):
        """Copy fixtures into the temp techniques directory."""
        for name in fixture_names:
            src = self.fixtures_dir / name
            if not src.exists():
                self.skipTest(f"Fixture not found: {name}")
            shutil.copy(src, self.techniques_dir / name)

    def run_build_routing(self, args=None, cwd=None):
        """Run the temp copy of build-routing."""
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

    def test_build_routing_stdout(self):
        """Test that build-routing prints to stdout by default."""
        self.install('valid-technique-1.md', 'valid-technique-2.md')

        result = self.run_build_routing()
        self.assertEqual(result.returncode, 0, f"Should succeed: {result.stderr}")
        self.assertIn("Service responds but data is wrong", result.stdout)
        self.assertIn("valid-technique-1", result.stdout)
        self.assertIn("valid-technique-2", result.stdout)
        self.assertIn("Symptom shape", result.stdout)
        self.assertIn("Reach for", result.stdout)

    def test_build_routing_to_file(self):
        """Test that build-routing -o writes to ROUTING.md."""
        self.install('valid-technique-1.md', 'valid-technique-2.md')

        self.assertFalse(self.routing_path.exists(), "ROUTING.md should not exist before -o")

        result = self.run_build_routing(['-o'])
        self.assertEqual(result.returncode, 0, f"Should succeed: {result.stderr}")
        self.assertTrue(self.routing_path.exists(), "ROUTING.md should be created with -o")

        content = self.routing_path.read_text()
        self.assertIn("valid-technique-1", content)
        self.assertIn("valid-technique-2", content)

    def test_build_routing_idempotent(self):
        """Test that running twice produces byte-identical output."""
        self.install('valid-technique-1.md', 'valid-technique-2.md')

        # Run twice to stdout
        result1 = self.run_build_routing()
        result2 = self.run_build_routing()

        self.assertEqual(result1.returncode, 0)
        self.assertEqual(result2.returncode, 0)
        self.assertEqual(result1.stdout, result2.stdout, "Output should be byte-identical on second run")

    def test_build_routing_file_idempotent(self):
        """Test that writing to file twice produces byte-identical output."""
        self.install('valid-technique-1.md', 'valid-technique-2.md')

        # Run twice with -o
        result1 = self.run_build_routing(['-o'])
        content1 = self.routing_path.read_text()

        # Sleep briefly to ensure file timestamps would differ
        import time
        time.sleep(0.01)

        result2 = self.run_build_routing(['-o'])
        content2 = self.routing_path.read_text()

        self.assertEqual(result1.returncode, 0)
        self.assertEqual(result2.returncode, 0)
        self.assertEqual(content1, content2, "File content should be byte-identical on second run")

    def test_build_routing_sorted(self):
        """Test that routing table entries are sorted."""
        self.install('valid-technique-1.md', 'valid-technique-2.md')

        result = self.run_build_routing()
        self.assertEqual(result.returncode, 0)

        # Extract table rows and check they're sorted
        lines = result.stdout.split('\n')
        table_start = next(i for i, line in enumerate(lines) if 'Symptom shape' in line)
        table_lines = [line for line in lines[table_start+2:] if line.strip() and '|' in line]

        # Extract symptom shapes from table
        symptoms = [line.split('|')[1].strip() for line in table_lines]
        symptoms_lower = [s.lower() for s in symptoms]

        # Check they're sorted
        self.assertEqual(symptoms_lower, sorted(symptoms_lower), "Symptoms should be sorted")

    def test_build_routing_malformed_input(self):
        """Test that malformed input causes non-zero exit."""
        self.install('malformed-yaml.md')

        result = self.run_build_routing()
        self.assertNotEqual(result.returncode, 0, "Should fail on malformed input")

    def test_build_routing_no_files(self):
        """Test that no technique files produces empty table."""
        # Only _TEMPLATE.md is present, and build-routing skips it

        result = self.run_build_routing()
        self.assertEqual(result.returncode, 0)
        self.assertIn("Symptom shape", result.stdout)
        self.assertIn("Reach for", result.stdout)

    def test_build_routing_banner(self):
        """Test that output contains 'generated' banner."""
        self.install('valid-technique-1.md')

        result = self.run_build_routing()
        self.assertIn("Generated", result.stdout, "Should have generation banner")
        self.assertIn("build-routing", result.stdout, "Banner should name the script")

    def test_build_routing_bad_usage(self):
        """Test that bad usage exits with code 2."""
        result = self.run_build_routing(['--invalid-flag'])
        self.assertEqual(result.returncode, 2)

    def test_build_routing_from_different_cwd(self):
        """Test that build-routing works from any working directory."""
        self.install('valid-technique-1.md')

        # Run from a working directory unrelated to the skill tree
        with tempfile.TemporaryDirectory() as elsewhere:
            result = self.run_build_routing(cwd=elsewhere)
            # Should still work because script finds techniques dir relative to itself
            self.assertEqual(result.returncode, 0)
            self.assertIn("valid-technique-1", result.stdout)

    def test_real_library_untouched(self):
        """The suite must not add to, delete from, or empty the real library."""
        listing_now = sorted(p.name for p in self.real_techniques.glob('*.md'))
        self.assertEqual(
            listing_now, self.real_listing_before,
            "Tests changed the real techniques/ directory"
        )
        self.assertEqual(
            self.real_routing.exists(), self.real_routing_existed,
            "Tests created or deleted the real ROUTING.md"
        )


if __name__ == '__main__':
    unittest.main()
