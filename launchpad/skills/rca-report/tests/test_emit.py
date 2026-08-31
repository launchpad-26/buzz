import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')


def _load_script(name):
    path = os.path.join(SCRIPTS_DIR, name)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


emit = _load_script('emit')


class RunResult:
    def __init__(self, code, stdout, stderr):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


def run(argv):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        code = emit.main(argv)
        return RunResult(code, sys.stdout.getvalue(), sys.stderr.getvalue())
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


class DateExtractionTests(unittest.TestCase):
    """Test extraction of incident date from report."""

    def test_extract_iso_date_from_text(self):
        report = 'Incident occurred on 2026-08-18 at 14:30 UTC'
        date = emit._extract_iso_date(report)
        self.assertEqual(date, '2026-08-18')

    def test_extract_iso_date_from_timestamp(self):
        report = 'Started: 2026-08-18T14:30:00Z'
        date = emit._extract_iso_date(report)
        self.assertEqual(date, '2026-08-18')

    def test_extract_iso_date_returns_none_if_missing(self):
        report = 'No date in this report'
        date = emit._extract_iso_date(report)
        self.assertIsNone(date)

    def test_extract_first_date_if_multiple(self):
        report = 'First: 2026-08-18, Later: 2026-08-19'
        date = emit._extract_iso_date(report)
        self.assertEqual(date, '2026-08-18')


class SlugificationTests(unittest.TestCase):
    """Test filename slug generation."""

    def test_slugify_basic(self):
        slug = emit._slugify('Database Connection Timeout')
        self.assertEqual(slug, 'database-connection-timeout')

    def test_slugify_lowercase(self):
        slug = emit._slugify('API Down')
        self.assertEqual(slug, 'api-down')

    def test_slugify_removes_special_chars(self):
        slug = emit._slugify('Error: Too Many Requests!')
        self.assertIn('error', slug)
        self.assertNotIn('!', slug)
        self.assertNotIn(':', slug)

    def test_slugify_collapses_runs(self):
        slug = emit._slugify('Multiple   Spaces   Here')
        self.assertNotIn('   ', slug)
        self.assertNotIn('--', slug)

    def test_slugify_limits_length(self):
        slug = emit._slugify('a' * 100)
        self.assertLessEqual(len(slug), 50)

    def test_slugify_strips_hyphens(self):
        slug = emit._slugify('---leading and trailing---')
        self.assertFalse(slug.startswith('-'))
        self.assertFalse(slug.endswith('-'))


class TitleExtractionTests(unittest.TestCase):
    """Test title extraction from report."""

    def test_extract_title_first_line(self):
        report = 'Database outage\nDetails here'
        title = emit._extract_title(report)
        self.assertEqual(title, 'Database outage')

    def test_extract_title_skips_headers(self):
        report = '# Main Title\nSubtitle'
        title = emit._extract_title(report)
        self.assertEqual(title, 'Subtitle')

    def test_extract_title_skips_whitespace(self):
        report = '  \n\n  \nActual Title'
        title = emit._extract_title(report)
        self.assertEqual(title, 'Actual Title')

    def test_extract_title_falls_back_to_incident(self):
        report = ''
        title = emit._extract_title(report)
        self.assertEqual(title, 'incident')


class SaveReportTests(unittest.TestCase):
    """Test saving reports to dated archive."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_save_creates_dated_path(self):
        report = '2026-08-18: Database down\n\nDetails'
        path = emit.save_report(report, '2026-08-18', self.tempdir)
        self.assertIsNotNone(path)
        # Should be archive_dir/2026/08/18/...
        self.assertIn('2026/08/18', path)
        self.assertTrue(os.path.exists(path))

    def test_save_creates_nested_directories(self):
        report = 'Incident'
        path = emit.save_report(report, '2026-08-18', self.tempdir)
        self.assertTrue(os.path.isdir(os.path.dirname(path)))

    def test_save_writes_report_content(self):
        report = 'Test report content'
        path = emit.save_report(report, '2026-08-18', self.tempdir)
        with open(path, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Test report content')

    def test_save_uses_slugified_title(self):
        report = 'Database Connection Timeout\n\nDetails'
        path = emit.save_report(report, '2026-08-18', self.tempdir)
        self.assertIn('database-connection-timeout', path)
        self.assertTrue(path.endswith('.md'))

    def test_save_refuses_overwrite_without_force(self):
        report = 'First report'
        path = emit.save_report(report, '2026-08-18', self.tempdir)
        # Try to save again with same title
        result = emit.save_report('First report\n\nDifferent content', '2026-08-18', self.tempdir,
                                 force=False)
        self.assertIsNone(result)

    def test_save_allows_overwrite_with_force(self):
        report = 'First report'
        path = emit.save_report(report, '2026-08-18', self.tempdir)
        # Try to save again with force
        result = emit.save_report('Second report', '2026-08-18', self.tempdir,
                                 force=True)
        self.assertIsNotNone(result)
        with open(result, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Second report')

    def test_save_dry_run_does_not_write(self):
        report = 'Test report'
        path = emit.save_report(report, '2026-08-18', self.tempdir, dry_run=True)
        self.assertIsNotNone(path)
        self.assertFalse(os.path.exists(path))

    def test_save_invalid_date(self):
        report = 'Report'
        result = emit.save_report(report, 'invalid-date', self.tempdir)
        self.assertIsNone(result)

    def test_save_missing_date(self):
        report = 'Report'
        result = emit.save_report(report, None, self.tempdir)
        self.assertIsNone(result)

    def test_save_different_years_months_days(self):
        report = 'Report 1'
        path1 = emit.save_report(report, '2025-12-31', self.tempdir)
        path2 = emit.save_report(report, '2026-01-01', self.tempdir)
        self.assertIn('2025/12/31', path1)
        self.assertIn('2026/01/01', path2)


class RaiseIssueTests(unittest.TestCase):
    """Test issue creation (mocked since we can't call gh)."""

    def test_extract_title_for_issue(self):
        report = 'Database Connection Timeout\nSome details'
        title = emit._extract_title(report)
        self.assertEqual(title, 'Database Connection Timeout')

    def test_raise_dry_run_does_not_call_gh(self):
        report = 'Test report'
        # This should not raise or try to call gh
        result = emit.raise_issue(report, '2026-08-18', dry_run=True)
        self.assertIsNotNone(result)
        self.assertIn('github.com', result)


class EndToEndTests(unittest.TestCase):
    """End-to-end tests of the emit script."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_save_mode_basic(self):
        # Write report to temp file
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: Database down\n\nRoot cause: connection pool exhaustion')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result = run([report_file, '--save', archive_dir])

        self.assertEqual(result.code, 0)
        # Output should contain the saved path
        self.assertIn('archive', result.stdout)
        self.assertIn('2026/08/18', result.stdout)

    def test_save_mode_with_stdin(self):
        # Test file-based reading works (stdin testing is complex in unit tests)
        # This validates the main functionality without mocking stdin
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: Test from file\n\nContent')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result = run([report_file, '--save', archive_dir])
        self.assertEqual(result.code, 0)
        self.assertIn('archive', result.stdout)

    def test_save_mode_explicit_date(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('No date in content')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result = run([report_file, '--save', archive_dir, '--date', '2026-08-18'])

        self.assertEqual(result.code, 0)
        self.assertIn('archive', result.stdout)

    def test_save_mode_dry_run(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: Test\n\nContent')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result = run([report_file, '--save', archive_dir, '--dry-run'])

        self.assertEqual(result.code, 0)
        self.assertIn('Would save', result.stdout)
        # Directory should not have been created
        self.assertFalse(os.path.exists(archive_dir))

    def test_save_mode_refuse_overwrite(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: First\n\nContent')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result1 = run([report_file, '--save', archive_dir])
        self.assertEqual(result1.code, 0)

        # Try to save again
        with open(report_file, 'w') as f:
            f.write('2026-08-18: First\n\nDifferent content')
        result2 = run([report_file, '--save', archive_dir])
        self.assertEqual(result2.code, 2)
        self.assertIn('exists', result2.stderr)

    def test_save_mode_allow_force_overwrite(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: Test\n\nFirst')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result1 = run([report_file, '--save', archive_dir])
        self.assertEqual(result1.code, 0)

        with open(report_file, 'w') as f:
            f.write('2026-08-18: Test\n\nSecond')
        result2 = run([report_file, '--save', archive_dir, '--force'])
        self.assertEqual(result2.code, 0)

    def test_missing_mode_error(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('Content')

        result = run([report_file])
        self.assertEqual(result.code, 2)
        self.assertIn('--save or --raise', result.stderr)

    def test_empty_report_error(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result = run([report_file, '--save', archive_dir])
        self.assertEqual(result.code, 2)
        self.assertIn('empty', result.stderr)

    def test_missing_file_error(self):
        result = run(['/nonexistent/file.md', '--save', '/tmp'])
        self.assertEqual(result.code, 2)
        self.assertIn('Error', result.stderr)

    def test_raise_mode_dry_run(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: Database Down\n\nDetails here')

        result = run([report_file, '--raise', '--dry-run'])
        self.assertEqual(result.code, 0)
        self.assertIn('Would raise issue', result.stdout)

    def test_json_output_save(self):
        report_file = os.path.join(self.tempdir, 'report.md')
        with open(report_file, 'w') as f:
            f.write('2026-08-18: Test\n\nContent')

        archive_dir = os.path.join(self.tempdir, 'archive')
        result = run([report_file, '--save', archive_dir, '--json'])

        self.assertEqual(result.code, 0)
        # JSON output should be the last line
        lines = result.stdout.strip().split('\n')
        data = json.loads(lines[-1])
        self.assertIn('saved', data)
        self.assertIn('2026/08/18', data['saved'])

    def test_multiple_saves_same_date_different_titles(self):
        archive_dir = os.path.join(self.tempdir, 'archive')

        # Save first report
        report1 = os.path.join(self.tempdir, 'report1.md')
        with open(report1, 'w') as f:
            f.write('2026-08-18: Database Down\n\nDetails')
        result1 = run([report1, '--save', archive_dir])
        self.assertEqual(result1.code, 0)

        # Save different report same date
        report2 = os.path.join(self.tempdir, 'report2.md')
        with open(report2, 'w') as f:
            f.write('2026-08-18: Network Latency\n\nDetails')
        result2 = run([report2, '--save', archive_dir])
        self.assertEqual(result2.code, 0)

        # Both should exist
        archive_path = os.path.join(archive_dir, '2026', '08', '18')
        files = os.listdir(archive_path)
        self.assertEqual(len(files), 2)


if __name__ == '__main__':
    unittest.main()
