import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), 'fixtures', 'first_occurrence')


def _load_script(name):
    path = os.path.join(SCRIPTS_DIR, name)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


first_occurrence = _load_script('first-occurrence')


def fixture(name):
    return os.path.join(FIXTURES_DIR, name)


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
        code = first_occurrence.main(argv)
        return RunResult(code, sys.stdout.getvalue(), sys.stderr.getvalue())
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


class TimestampFormatTests(unittest.TestCase):
    def test_iso8601_format(self):
        result = run([fixture('mixed.log'), '--pattern', 'error', '--json'])
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['found'])
        self.assertEqual(data[0]['timestamp'], '2026-08-18T09:10:00+00:00')

    def test_syslog_format(self):
        result = run([fixture('syslog.log'), '--pattern', 'error', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['found'])
        self.assertTrue(data[0]['timestamp'].startswith('1970-08-18'))

    def test_apache_format(self):
        result = run([fixture('apache.log'), '--pattern', '/login', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['found'])
        self.assertTrue(data[0]['timestamp'].startswith('2023-10-10'))
        self.assertIn('/login', data[0]['match'])

    def test_epoch_format(self):
        result = run([fixture('epoch.log'), '--pattern', 'spike', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['found'])
        self.assertTrue(data[0]['timestamp'].startswith('2023-10-11'))
        self.assertIn('cpu=97', data[0]['match'])


class MultiplePatternTests(unittest.TestCase):
    def test_reports_first_occurrence_of_each_pattern(self):
        result = run([
            fixture('mixed.log'),
            '--pattern', 'error',
            '--pattern', 'warn',
            '--json',
        ])
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['pattern'], 'error')
        self.assertEqual(data[1]['pattern'], 'warn')
        self.assertEqual(data[0]['timestamp'], '2026-08-18T09:10:00+00:00')
        self.assertEqual(data[1]['timestamp'], '2026-08-18T09:25:00+00:00')

    def test_unmatched_pattern_reported_not_found(self):
        result = run([
            fixture('mixed.log'), '--pattern', 'does-not-exist', '--json',
        ])
        data = json.loads(result.stdout)
        self.assertFalse(data[0]['found'])
        self.assertEqual(result.code, 1)

    def test_partial_match_across_patterns_exits_0(self):
        result = run([
            fixture('mixed.log'),
            '--pattern', 'error',
            '--pattern', 'does-not-exist',
        ])
        self.assertEqual(result.code, 0)


class ContextTests(unittest.TestCase):
    def test_before_and_after_context(self):
        result = run([
            fixture('mixed.log'), '--pattern', 'error',
            '--before', '1', '--after', '1', '--json',
        ])
        data = json.loads(result.stdout)[0]
        self.assertEqual(data['before'], ['2026-08-18T09:05:00Z info: healthcheck ok'])
        self.assertEqual(data['after'], ['2026-08-18T09:15:00Z info: retry ok'])

    def test_negative_context_is_bad_usage(self):
        result = run([fixture('mixed.log'), '--pattern', 'error', '--before', '-1'])
        self.assertEqual(result.code, 2)


class CrossSourceTests(unittest.TestCase):
    def test_earliest_chosen_across_multiple_sources_by_timestamp(self):
        result = run([
            fixture('source_a.log'), fixture('source_b.log'),
            '--pattern', 'disk full', '--json',
        ])
        data = json.loads(result.stdout)[0]
        self.assertTrue(data['found'])
        self.assertEqual(data['timestamp'], '2026-08-18T09:10:00+00:00')
        self.assertTrue(data['source'].endswith('source_b.log'))


class UsageAndReceiptTests(unittest.TestCase):
    def test_no_pattern_is_bad_usage(self):
        result = run([fixture('mixed.log')])
        self.assertEqual(result.code, 2)

    def test_bad_regex_is_bad_usage(self):
        result = run([fixture('mixed.log'), '--pattern', '('])
        self.assertEqual(result.code, 2)

    def test_missing_file_is_bad_usage(self):
        result = run(['/no/such/file.log', '--pattern', 'error'])
        self.assertEqual(result.code, 2)

    def test_reduction_receipt_on_stderr(self):
        result = run([fixture('mixed.log'), '--pattern', 'error'])
        self.assertRegex(
            result.stderr,
            r'read [\d,]+ lines -> [\d,]+ lines \([\d.]+% reduction\)',
        )

    def test_output_file_written_and_input_untouched(self):
        src = fixture('mixed.log')
        with open(src) as f:
            before = f.read()
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, 'out.txt')
            result = run([src, '--pattern', 'error', '-o', out_path])
            self.assertEqual(result.code, 0)
            self.assertEqual(result.stdout, '')
            with open(out_path) as f:
                content = f.read()
            self.assertIn('connection refused', content)
        with open(src) as f:
            after = f.read()
        self.assertEqual(before, after)


class ScaleTests(unittest.TestCase):
    def test_100000_line_fixture(self):
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.log', delete=False) as f:
            path = f.name
            for i in range(100_000):
                minute = i % 60
                hour = (i // 60) % 24
                day = 18 + (i // 1440)
                marker = 'RARE-MARKER' if i == 99_999 else 'noise'
                f.write(
                    f"2026-08-{day:02d}T{hour:02d}:{minute:02d}:00Z "
                    f"line {i} {marker}\n"
                )
        try:
            result = run([path, '--pattern', 'RARE-MARKER', '--json'])
        finally:
            os.remove(path)
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)[0]
        self.assertTrue(data['found'])
        self.assertIn('99999', data['match'])
        self.assertRegex(result.stderr, r'read 100,000 lines')


if __name__ == '__main__':
    unittest.main()
