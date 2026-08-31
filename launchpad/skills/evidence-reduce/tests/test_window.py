import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'window')


def _load_script(name):
    path = os.path.join(SCRIPTS_DIR, name)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


window = _load_script('window')


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
        code = window.main(argv)
        return RunResult(code, sys.stdout.getvalue(), sys.stderr.getvalue())
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


class TimestampFormatTests(unittest.TestCase):
    def test_iso8601_format(self):
        result = run([fixture('iso8601.log')])
        self.assertEqual(result.code, 0)
        self.assertIn('app started', result.stdout)
        self.assertIn('shutdown', result.stdout)

    def test_syslog_format_and_year_wrap(self):
        result = run([fixture('syslog.log'), '--json'])
        self.assertEqual(result.code, 0)
        records = json.loads(result.stdout)
        timestamps = [r['timestamp'] for r in records]
        self.assertTrue(timestamps[0].startswith('1970-12-31'))
        self.assertTrue(timestamps[-1].startswith('1971-01-01'))

    def test_apache_format(self):
        result = run([fixture('apache.log')])
        self.assertEqual(result.code, 0)
        self.assertIn('/login', result.stdout)

    def test_epoch_seconds_and_millis(self):
        result = run([fixture('epoch.log'), '--json'])
        self.assertEqual(result.code, 0)
        records = json.loads(result.stdout)
        self.assertEqual(len(records), 5)
        self.assertTrue(records[0]['timestamp'].startswith('2023-10-11'))
        self.assertTrue(records[-1]['timestamp'].startswith('2023-10-11'))


class MultiLineRecordTests(unittest.TestCase):
    def test_traceback_stays_attached_to_leading_timestamp(self):
        result = run([fixture('iso8601.log'), '--from', '2026-08-18T10:10:00Z',
                      '--to', '2026-08-18T10:10:00Z'])
        self.assertEqual(result.code, 0)
        self.assertIn('request failed', result.stdout)
        self.assertIn('Traceback', result.stdout)
        self.assertIn('ValueError: boom', result.stdout)
        # the next record must not have been pulled in
        self.assertNotIn('retry succeeded', result.stdout)


class WindowFilterTests(unittest.TestCase):
    def test_from_and_to_bounds(self):
        result = run([fixture('iso8601.log'), '--from', '2026-08-18T10:05:00Z',
                      '--to', '2026-08-18T10:15:00Z', '--json'])
        records = json.loads(result.stdout)
        texts = [r['text'] for r in records]
        self.assertEqual(len(records), 3)
        self.assertTrue(any('healthcheck ok' in t for t in texts))
        self.assertTrue(any('retry succeeded' in t for t in texts))
        self.assertFalse(any('app started' in t for t in texts))
        self.assertFalse(any('shutdown' in t for t in texts))

    def test_no_matches_exits_1(self):
        result = run([fixture('iso8601.log'), '--from', '2099-01-01T00:00:00Z'])
        self.assertEqual(result.code, 1)

    def test_bad_from_value_exits_2(self):
        result = run([fixture('iso8601.log'), '--from', 'not-a-date'])
        self.assertEqual(result.code, 2)

    def test_missing_file_exits_2(self):
        result = run(['/no/such/file.log'])
        self.assertEqual(result.code, 2)


class ReceiptAndJsonTests(unittest.TestCase):
    def test_reduction_receipt_on_stderr(self):
        result = run([fixture('iso8601.log'), '--from', '2026-08-18T10:15:00Z'])
        self.assertRegex(
            result.stderr,
            r'read [\d,]+ lines -> [\d,]+ lines \([\d.]+% reduction\)',
        )

    def test_json_flag_produces_valid_json(self):
        result = run([fixture('apache.log'), '--json'])
        records = json.loads(result.stdout)
        self.assertIsInstance(records, list)
        for r in records:
            self.assertIn('timestamp', r)
            self.assertIn('source', r)
            self.assertIn('text', r)

    def test_output_file_written_and_input_untouched(self):
        src = fixture('epoch.log')
        with open(src) as f:
            before = f.read()
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, 'out.txt')
            result = run([src, '-o', out_path])
            self.assertEqual(result.code, 0)
            self.assertEqual(result.stdout, '')
            with open(out_path) as f:
                content = f.read()
            self.assertIn('metric cpu=12', content)
        with open(src) as f:
            after = f.read()
        self.assertEqual(before, after)


class ScaleTests(unittest.TestCase):
    def test_100000_line_fixture_streams_without_full_load(self):
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.log', delete=False) as f:
            path = f.name
            for i in range(100_000):
                minute = i % 60
                hour = (i // 60) % 24
                day = 18 + (i // 1440)
                f.write(
                    f"2026-08-{day:02d}T{hour:02d}:{minute:02d}:00Z "
                    f"line {i}\n"
                )
        try:
            result = run([path, '--from', '2026-08-18T00:00:00Z'])
        finally:
            os.remove(path)
        self.assertEqual(result.code, 0)
        self.assertRegex(result.stderr, r'read 100,000 lines')
        # Streaming reads line-by-line rather than materialising the whole
        # file; iter_records is a generator, so nothing forces a full read.
        self.assertTrue(hasattr(window.iter_records(['/dev/null'], 1970),
                                 '__next__'))


if __name__ == '__main__':
    unittest.main()
