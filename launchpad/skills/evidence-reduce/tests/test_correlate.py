import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'correlate')
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'correlate')
SERIES1 = os.path.join(FIXTURE_DIR, 'series1.log')
SERIES2 = os.path.join(FIXTURE_DIR, 'series2.log')

CAUSAL_WORDS = ('causes', 'caused', 'leads to', 'triggers', 'because', 'drives', 'due to')


def run_correlate(args):
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True,
        text=True,
    )


class TestCorrelate(unittest.TestCase):
    def test_buckets_two_series_by_time(self):
        result = run_correlate(['--json', '--bucket', '60', SERIES1, SERIES2])
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload['buckets']), 5)
        counts1 = [b['counts']['series1'] for b in payload['buckets']]
        counts2 = [b['counts']['series2'] for b in payload['buckets']]
        self.assertEqual(counts1, [5, 1, 5, 1, 5])
        self.assertEqual(counts2, [4, 1, 4, 2, 5])

    def test_reports_correlation_coefficient(self):
        result = run_correlate(['--json', '--bucket', '60', SERIES1, SERIES2])
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload['alignment']), 1)
        r = payload['alignment'][0]['correlation']
        self.assertAlmostEqual(r, 0.9444, places=3)

    def test_output_makes_no_causal_claim(self):
        result = run_correlate([SERIES1, SERIES2])
        table = result.stdout.lower()
        for word in CAUSAL_WORDS:
            self.assertNotIn(word, table)

    def test_json_output_makes_no_causal_claim(self):
        result = run_correlate(['--json', SERIES1, SERIES2])
        text = result.stdout.lower()
        for word in CAUSAL_WORDS:
            self.assertNotIn(word, text)

    def test_table_output_is_default(self):
        result = run_correlate([SERIES1, SERIES2])
        self.assertEqual(result.returncode, 0)
        self.assertIn('BUCKET', result.stdout)
        self.assertIn('ALIGNMENT', result.stdout)

    def test_receipt_on_stderr(self):
        result = run_correlate(['--json', SERIES1, SERIES2])
        self.assertIn('read 33 events -> 5 buckets', result.stderr)

    def test_configurable_bucket_size_changes_bucket_count(self):
        result = run_correlate(['--json', '--bucket', '300', SERIES1, SERIES2])
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload['buckets']), 1)

    def test_never_mutates_input(self):
        with open(SERIES1) as f:
            before1 = f.read()
        with open(SERIES2) as f:
            before2 = f.read()
        run_correlate(['--json', SERIES1, SERIES2])
        with open(SERIES1) as f:
            self.assertEqual(before1, f.read())
        with open(SERIES2) as f:
            self.assertEqual(before2, f.read())

    def test_exit_1_when_neither_series_has_timestamps(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f2:
            path1, path2 = f1.name, f2.name
            f1.write('no timestamp here\n')
            f2.write('also none here\n')
        try:
            result = run_correlate([path1, path2])
        finally:
            os.unlink(path1)
            os.unlink(path2)
        self.assertEqual(result.returncode, 1)

    def test_exit_2_when_fewer_than_two_series(self):
        result = run_correlate([SERIES1])
        self.assertEqual(result.returncode, 2)

    def test_exit_2_on_bad_usage(self):
        result = run_correlate(['/nonexistent/series.log', SERIES2])
        self.assertEqual(result.returncode, 2)

    def test_exit_2_on_nonpositive_bucket(self):
        result = run_correlate(['--bucket', '0', SERIES1, SERIES2])
        self.assertEqual(result.returncode, 2)

    def test_writes_output_only_when_dash_o_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, 'out.json')
            result = run_correlate(['--json', '-o', out_path, SERIES1, SERIES2])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            with open(out_path) as f:
                payload = json.load(f)
            self.assertEqual(len(payload['buckets']), 5)

    def test_large_series_processed_and_streamed(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f1:
            path1 = f1.name
            for i in range(50_000):
                minute = (i // 100) % 60
                second = i % 60
                f1.write(f"2026-08-18T10:{minute:02d}:{second:02d}Z series one event {i}\n")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f2:
            path2 = f2.name
            for i in range(50_000):
                minute = (i // 100) % 60
                second = i % 60
                f2.write(f"2026-08-18T10:{minute:02d}:{second:02d}Z series two event {i}\n")
        try:
            result = run_correlate(['--json', '--bucket', '3600', path1, path2])
        finally:
            os.unlink(path1)
            os.unlink(path2)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        total_events = sum(b['counts']['series1'] for b in payload['buckets'])
        self.assertEqual(total_events, 50_000)


if __name__ == '__main__':
    unittest.main()
