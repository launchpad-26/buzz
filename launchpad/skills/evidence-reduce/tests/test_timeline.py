import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'timeline')


def _load_script(name):
    path = os.path.join(SCRIPTS_DIR, name)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


timeline = _load_script('timeline')


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
        code = timeline.main(argv)
        return RunResult(code, sys.stdout.getvalue(), sys.stderr.getvalue())
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


class TimestampFormatTests(unittest.TestCase):
    def test_iso8601_source(self):
        result = run([f"app={fixture('app.log')}", '--json'])
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['source'], 'app')

    def test_syslog_source(self):
        result = run([f"sys={fixture('syslog.log')}", '--json'])
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 2)
        self.assertTrue(data[0]['timestamp'].startswith('1970-08-18'))

    def test_apache_source(self):
        result = run([f"net={fixture('net.log')}", '--json'])
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 3)
        self.assertTrue(data[0]['timestamp'].startswith('2023-10-10'))

    def test_epoch_source(self):
        result = run([f"chg={fixture('change.log')}", '--json'])
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 3)
        self.assertTrue(data[0]['timestamp'].startswith('2023-10-10'))


class MergeTests(unittest.TestCase):
    def test_three_sources_merge_in_chronological_order_with_tags(self):
        result = run([
            f"app={fixture('app.log')}",
            f"net={fixture('net.log')}",
            f"chg={fixture('change.log')}",
            '--json',
        ])
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 9)

        sources_in_order = [row['source'] for row in data]
        self.assertEqual(
            sources_in_order,
            ['app', 'net', 'chg', 'net', 'app', 'net', 'chg', 'app', 'chg'],
        )

        timestamps = [row['timestamp'] for row in data]
        self.assertEqual(timestamps, sorted(timestamps))

        texts = [row['text'] for row in data]
        self.assertIn('deploy started', texts[2])
        self.assertIn('rollback triggered', texts[-1])

    def test_default_label_is_basename_when_unlabelled(self):
        result = run([fixture('app.log'), '--json'])
        data = json.loads(result.stdout)
        self.assertEqual(data[0]['source'], 'app.log')


class BucketTests(unittest.TestCase):
    def test_bucket_collapses_resolution(self):
        result = run([
            f"app={fixture('app.log')}",
            f"net={fixture('net.log')}",
            f"chg={fixture('change.log')}",
            '--bucket', '5m', '--json',
        ])
        data = json.loads(result.stdout)
        # 9 rows across a couple of minutes collapse to fewer bucket rows
        self.assertLess(len(data), 9)
        total_count = sum(row['count'] for row in data)
        self.assertEqual(total_count, 9)

    def test_bad_bucket_value_is_bad_usage(self):
        result = run([f"app={fixture('app.log')}", '--bucket', 'nonsense'])
        self.assertEqual(result.code, 2)


class TimezoneTests(unittest.TestCase):
    def test_default_tz_is_utc(self):
        result = run([f"app={fixture('app.log')}", '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['timestamp'].endswith('+00:00'))

    def test_fixed_offset_tz(self):
        result = run([f"app={fixture('app.log')}", '--tz', '-07:00', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['timestamp'].endswith('-07:00'))

    def test_negative_offset_with_equals_form(self):
        result = run([f"app={fixture('app.log')}", '--tz=-07:00', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['timestamp'].endswith('-07:00'))

    def test_positive_offset_tz(self):
        result = run([f"app={fixture('app.log')}", '--tz', '+05:30', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['timestamp'].endswith('+05:30'))

    def test_compact_negative_offset_tz(self):
        result = run([f"app={fixture('app.log')}", '--tz', '-0700', '--json'])
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['timestamp'].endswith('-07:00'))

    def test_unknown_tz_is_bad_usage(self):
        result = run([f"app={fixture('app.log')}", '--tz', 'Not/AZone'])
        self.assertEqual(result.code, 2)


class OffsetArgumentFusionTests(unittest.TestCase):
    """fuse_offset_values only rewrites a --tz flag followed by an offset."""

    def test_rewrites_negative_offset_after_tz(self):
        self.assertEqual(
            timeline.fuse_offset_values(['a.log', '--tz', '-07:00', '--json']),
            ['a.log', '--tz=-07:00', '--json'],
        )

    def test_leaves_iana_name_alone(self):
        self.assertEqual(
            timeline.fuse_offset_values(['--tz', 'Pacific/Auckland']),
            ['--tz', 'Pacific/Auckland'],
        )

    def test_leaves_other_flags_alone(self):
        self.assertEqual(
            timeline.fuse_offset_values(['--bucket', '5m', '-o', 'out.txt']),
            ['--bucket', '5m', '-o', 'out.txt'],
        )

    def test_trailing_tz_without_value_is_untouched(self):
        self.assertEqual(timeline.fuse_offset_values(['--tz']), ['--tz'])

    def test_bare_double_dash_is_untouched(self):
        self.assertEqual(
            timeline.fuse_offset_values(['--', '-07:00']),
            ['--', '-07:00'],
        )


class UsageAndReceiptTests(unittest.TestCase):
    def test_missing_file_is_bad_usage(self):
        result = run(['x=/no/such/file.log'])
        self.assertEqual(result.code, 2)

    def test_no_timestamped_lines_exits_1(self):
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.log', delete=False) as f:
            f.write('no timestamp here\nnor here\n')
            path = f.name
        try:
            result = run([path])
        finally:
            os.remove(path)
        self.assertEqual(result.code, 1)

    def test_reduction_receipt_on_stderr(self):
        result = run([f"app={fixture('app.log')}"])
        self.assertRegex(
            result.stderr,
            r'read [\d,]+ lines -> [\d,]+ rows \([\d.]+% reduction\)',
        )

    def test_output_file_written_and_input_untouched(self):
        src = fixture('app.log')
        with open(src) as f:
            before = f.read()
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, 'out.txt')
            result = run([f"app={src}", '-o', out_path])
            self.assertEqual(result.code, 0)
            self.assertEqual(result.stdout, '')
            with open(out_path) as f:
                content = f.read()
            self.assertIn('startup', content)
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
                f.write(
                    f"2026-08-{day:02d}T{hour:02d}:{minute:02d}:00Z "
                    f"line {i}\n"
                )
        try:
            result = run([f"big={path}", '--bucket', '1h'])
        finally:
            os.remove(path)
        self.assertEqual(result.code, 0)
        self.assertRegex(result.stderr, r'read 100,000 lines')


if __name__ == '__main__':
    unittest.main()
