import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'delta')
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'delta')
A = os.path.join(FIXTURE_DIR, 'a.log')
B = os.path.join(FIXTURE_DIR, 'b.log')


def run_delta(args):
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True,
        text=True,
    )


class TestDelta(unittest.TestCase):
    def test_reports_only_in_a_only_in_b_and_changed(self):
        result = run_delta(['--json', A, B])
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)

        self.assertEqual(len(payload['only_in_a']), 1)
        self.assertIn('WARN cache miss', payload['only_in_a'][0]['signature'])
        self.assertEqual(payload['only_in_a'][0]['count'], 2)

        self.assertEqual(len(payload['only_in_b']), 1)
        self.assertIn('ERROR disk full', payload['only_in_b'][0]['signature'])
        self.assertEqual(payload['only_in_b'][0]['count'], 6)

        self.assertEqual(len(payload['changed']), 1)
        changed = payload['changed'][0]
        self.assertIn('ERROR db connection failed', changed['signature'])
        self.assertEqual(changed['count_a'], 5)
        self.assertEqual(changed['count_b'], 1)
        self.assertLess(changed['rate_change_pct'], 0)

    def test_stable_rate_signature_is_not_reported_as_changed(self):
        result = run_delta(['--json', A, B])
        payload = json.loads(result.stdout)
        signatures_changed = [c['signature'] for c in payload['changed']]
        self.assertFalse(any('INFO request completed' in s for s in signatures_changed))

    def test_keyed_on_signature_not_raw_line(self):
        result = run_delta(['--json', A, B])
        payload = json.loads(result.stdout)
        for bucket in ('only_in_a', 'only_in_b'):
            for entry in payload[bucket]:
                self.assertNotIn('2026-08-18', entry['signature'])

    def test_receipt_on_stderr(self):
        result = run_delta(['--json', A, B])
        self.assertIn('read 20 lines -> 3 differences', result.stderr)

    def test_threshold_flag_changes_sensitivity(self):
        # At a very high threshold, the db-connection-failed rate swing no
        # longer clears the bar.
        result = run_delta(['--json', '--threshold', '95', A, B])
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload['changed']), 0)

    def test_never_mutates_input(self):
        with open(A) as f:
            before_a = f.read()
        with open(B) as f:
            before_b = f.read()
        run_delta(['--json', A, B])
        with open(A) as f:
            self.assertEqual(before_a, f.read())
        with open(B) as f:
            self.assertEqual(before_b, f.read())

    def test_exit_1_when_no_differences(self):
        result = run_delta(['--json', A, A])
        self.assertEqual(result.returncode, 1)

    def test_exit_2_on_bad_usage(self):
        result = run_delta(['/nonexistent/a.log', B])
        self.assertEqual(result.returncode, 2)

    def test_writes_output_only_when_dash_o_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, 'out.json')
            result = run_delta(['--json', '-o', out_path, A, B])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            with open(out_path) as f:
                payload = json.load(f)
            self.assertEqual(len(payload['only_in_a']), 1)

    def test_100k_line_inputs_processed_and_streamed(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as fa:
            path_a = fa.name
            for i in range(50_000):
                fa.write(f"2026-08-18T10:00:{i % 60:02d}Z host app: INFO steady state ok id={100000 + i}\n")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as fb:
            path_b = fb.name
            for i in range(50_000):
                fb.write(f"2026-08-18T11:00:{i % 60:02d}Z host app: ERROR steady state broke id={200000 + i}\n")
        try:
            result = run_delta(['--json', path_a, path_b])
        finally:
            os.unlink(path_a)
            os.unlink(path_b)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload['only_in_a']), 1)
        self.assertEqual(payload['only_in_a'][0]['count'], 50_000)
        self.assertEqual(len(payload['only_in_b']), 1)
        self.assertEqual(payload['only_in_b'][0]['count'], 50_000)


if __name__ == '__main__':
    unittest.main()
