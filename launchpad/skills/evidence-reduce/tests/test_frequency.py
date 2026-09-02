import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'frequency')
FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'frequency', 'sample.log')
REQUEST_ID_FIXTURE = os.path.join(
    os.path.dirname(__file__), 'fixtures', 'frequency', 'request-id.log'
)


def run_frequency(args, stdin_text=None):
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        input=stdin_text,
        capture_output=True,
        text=True,
    )


class TestFrequency(unittest.TestCase):
    def test_collapses_to_known_signature_count(self):
        result = run_frequency(['--json', FIXTURE])
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 3)
        counts = sorted(entry['count'] for entry in payload)
        self.assertEqual(counts, [3, 5, 7])

    def test_receipt_on_stderr_reports_exact_reduction(self):
        result = run_frequency(['--json', FIXTURE])
        self.assertIn('read 15 lines -> 3 signatures', result.stderr)

    def test_keeps_a_representative_raw_line_per_signature(self):
        result = run_frequency(['--json', FIXTURE])
        payload = json.loads(result.stdout)
        db_entry = next(e for e in payload if e['count'] == 7)
        self.assertIn('ERROR db connection failed', db_entry['example'])
        self.assertIn('request_id=', db_entry['example'])

    def test_normalizes_timestamp_uuid_ip_port(self):
        result = run_frequency(['--json', FIXTURE])
        payload = json.loads(result.stdout)
        db_entry = next(e for e in payload if e['count'] == 7)
        self.assertNotIn('2026-08-18', db_entry['signature'])
        self.assertNotIn('550e8400', db_entry['signature'])
        self.assertNotIn('10.0.0.5', db_entry['signature'])
        self.assertNotIn(':5432', db_entry['signature'])
        self.assertIn('<TS>', db_entry['signature'])
        self.assertIn('<UUID>', db_entry['signature'])
        self.assertIn('<IP>', db_entry['signature'])
        self.assertIn('<PORT>', db_entry['signature'])

    def test_collapses_hyphenated_request_id_tokens(self):
        # Merge-gate regression: 'req-abc123' and 'req-def456' differ only in
        # a prefix-hyphen-alnum request ID and must collapse to one signature.
        result = run_frequency(['--json', REQUEST_ID_FIXTURE])
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['count'], 2)
        self.assertIn('<ID>', payload[0]['signature'])
        self.assertNotIn('abc123', payload[0]['signature'])
        self.assertNotIn('def456', payload[0]['signature'])

    def test_top_n_caps_output(self):
        result = run_frequency(['--json', '--top', '1', FIXTURE])
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['count'], 7)

    def test_table_output_is_default(self):
        result = run_frequency([FIXTURE])
        self.assertEqual(result.returncode, 0)
        self.assertIn('COUNT', result.stdout)
        self.assertIn('SIGNATURE', result.stdout)

    def test_reads_from_stdin_when_no_files_given(self):
        with open(FIXTURE) as f:
            text = f.read()
        result = run_frequency(['--json'], stdin_text=text)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 3)

    def test_never_mutates_input_file(self):
        with open(FIXTURE) as f:
            before = f.read()
        run_frequency(['--json', FIXTURE])
        with open(FIXTURE) as f:
            after = f.read()
        self.assertEqual(before, after)

    def test_exit_1_on_no_input(self):
        result = run_frequency([], stdin_text='')
        self.assertEqual(result.returncode, 1)

    def test_exit_2_on_bad_usage(self):
        result = run_frequency(['/nonexistent/path/does-not-exist.log'])
        self.assertEqual(result.returncode, 2)

    def test_writes_output_file_only_when_dash_o_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, 'out.json')
            result = run_frequency(['--json', '-o', out_path, FIXTURE])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            with open(out_path) as f:
                payload = json.load(f)
            self.assertEqual(len(payload), 3)

    def test_100k_line_input_processed_and_streamed(self):
        # Generated deterministically at test time rather than committed as a
        # multi-megabyte fixture; the property under test (streaming, not
        # bulk-loading) does not depend on the bytes being checked in.
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.log', delete=False
        ) as f:
            path = f.name
            for i in range(100_000):
                octet = (i % 250) + 1
                f.write(
                    f"2026-08-18T10:00:{i % 60:02d}Z host app: "
                    f"INFO request completed client=10.0.0.{octet}:{5000 + (i % 500)} "
                    f"duration_us={100000 + i}\n"
                )
        try:
            result = run_frequency(['--json', path])
        finally:
            os.unlink(path)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['count'], 100_000)
        self.assertIn('read 100,000 lines -> 1 signatures', result.stderr)


if __name__ == '__main__':
    unittest.main()
