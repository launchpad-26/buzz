import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')


def _load_script(name):
    path = os.path.join(SCRIPTS_DIR, name)
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


intervals = _load_script('intervals')


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
        code = intervals.main(argv)
        return RunResult(code, sys.stdout.getvalue(), sys.stderr.getvalue())
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


class TimestampParsingTests(unittest.TestCase):
    """Test parsing of all four supported timestamp formats."""

    def test_parse_iso8601_utc(self):
        """ISO 8601 with Z suffix."""
        dt = intervals.parse_timestamp('2026-08-18T14:30:00Z')
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 8)
        self.assertEqual(dt.day, 18)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)

    def test_parse_iso8601_with_offset(self):
        """ISO 8601 with timezone offset."""
        dt = intervals.parse_timestamp('2026-08-18T14:30:00+02:00')
        self.assertIsNotNone(dt)
        # Should be converted to UTC
        self.assertEqual(dt.hour, 12)  # 14 - 2 = 12
        self.assertEqual(dt.tzinfo.utcoffset(None).total_seconds(), 0)

    def test_parse_iso8601_with_space(self):
        """ISO 8601 with space instead of T."""
        dt = intervals.parse_timestamp('2026-08-18 14:30:00Z')
        self.assertIsNotNone(dt)
        self.assertEqual(dt.hour, 14)

    def test_parse_apache_format(self):
        """Apache/nginx common log format."""
        dt = intervals.parse_timestamp('[18/Aug/2026:14:30:00 +0200]')
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 8)
        self.assertEqual(dt.day, 18)
        # Converted to UTC
        self.assertEqual(dt.hour, 12)  # 14 - 2 = 12

    def test_parse_epoch_seconds(self):
        """Unix epoch in seconds."""
        # 2026-08-18T14:30:00Z = 1787146200
        dt = intervals.parse_timestamp('1787146200')
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 8)

    def test_parse_epoch_millis(self):
        """Unix epoch in milliseconds."""
        # 2026-08-18T14:30:00Z = 1787146200000
        dt = intervals.parse_timestamp('1787146200000')
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 8)

    def test_parse_syslog_format(self):
        """Syslog format (year-less)."""
        dt = intervals.parse_timestamp('Aug 18 14:30:00', syslog_year=2026)
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 8)
        self.assertEqual(dt.day, 18)
        self.assertEqual(dt.hour, 14)

    def test_invalid_timestamp_returns_none(self):
        """Invalid timestamps return None."""
        self.assertIsNone(intervals.parse_timestamp('not a timestamp'))
        self.assertIsNone(intervals.parse_timestamp(''))
        self.assertIsNone(intervals.parse_timestamp(None))


class DurationFormattingTests(unittest.TestCase):
    """Test human-readable duration formatting."""

    def test_format_seconds_only(self):
        from datetime import timedelta
        td = timedelta(seconds=45)
        self.assertEqual(intervals.format_duration(td), '45s')

    def test_format_minutes_and_seconds(self):
        from datetime import timedelta
        td = timedelta(minutes=5, seconds=30)
        self.assertEqual(intervals.format_duration(td), '5m 30s')

    def test_format_hours_minutes_seconds(self):
        from datetime import timedelta
        td = timedelta(hours=2, minutes=15, seconds=30)
        self.assertEqual(intervals.format_duration(td), '2h 15m 30s')

    def test_format_none_returns_unknown(self):
        self.assertEqual(intervals.format_duration(None), 'unknown')

    def test_format_zero_duration(self):
        from datetime import timedelta
        td = timedelta(seconds=0)
        self.assertEqual(intervals.format_duration(td), '0s')


class IntervalComputationTests(unittest.TestCase):
    """Test TTD, TTM, TTR computation."""

    def test_compute_all_intervals(self):
        from datetime import datetime, timezone
        start = datetime(2026, 8, 18, 10, 0, 0, tzinfo=timezone.utc)
        detection = datetime(2026, 8, 18, 10, 5, 0, tzinfo=timezone.utc)
        mitigation = datetime(2026, 8, 18, 10, 15, 0, tzinfo=timezone.utc)
        resolution = datetime(2026, 8, 18, 10, 25, 0, tzinfo=timezone.utc)

        result = intervals.compute_intervals(start, detection, mitigation, resolution)

        self.assertIsNotNone(result['ttd'])
        self.assertEqual(result['ttd'].total_seconds(), 300)  # 5 minutes
        self.assertIsNotNone(result['ttm'])
        self.assertEqual(result['ttm'].total_seconds(), 600)  # 10 minutes
        self.assertIsNotNone(result['ttr'])
        self.assertEqual(result['ttr'].total_seconds(), 1500)  # 25 minutes

    def test_compute_with_missing_detection(self):
        from datetime import datetime, timezone
        start = datetime(2026, 8, 18, 10, 0, 0, tzinfo=timezone.utc)
        mitigation = datetime(2026, 8, 18, 10, 15, 0, tzinfo=timezone.utc)
        resolution = datetime(2026, 8, 18, 10, 25, 0, tzinfo=timezone.utc)

        result = intervals.compute_intervals(start, None, mitigation, resolution)

        self.assertIsNone(result['ttd'])
        self.assertIsNone(result['ttm'])
        self.assertIsNotNone(result['ttr'])

    def test_compute_with_missing_resolution(self):
        from datetime import datetime, timezone
        start = datetime(2026, 8, 18, 10, 0, 0, tzinfo=timezone.utc)
        detection = datetime(2026, 8, 18, 10, 5, 0, tzinfo=timezone.utc)
        mitigation = datetime(2026, 8, 18, 10, 15, 0, tzinfo=timezone.utc)

        result = intervals.compute_intervals(start, detection, mitigation, None)

        self.assertIsNotNone(result['ttd'])
        self.assertIsNotNone(result['ttm'])
        self.assertIsNone(result['ttr'])


class EndToEndTests(unittest.TestCase):
    """End-to-end tests of the intervals script."""

    def test_basic_run_with_all_times(self):
        result = run([
            '--start', '2026-08-18T10:00:00Z',
            '--detection', '2026-08-18T10:05:00Z',
            '--mitigation', '2026-08-18T10:15:00Z',
            '--resolution', '2026-08-18T10:25:00Z'
        ])
        self.assertEqual(result.code, 0)
        self.assertIn('Time to Detect', result.stdout)
        self.assertIn('5m', result.stdout)
        self.assertIn('10m', result.stdout)
        self.assertIn('25m', result.stdout)

    def test_run_with_missing_detection(self):
        result = run([
            '--start', '2026-08-18T10:00:00Z',
            '--mitigation', '2026-08-18T10:15:00Z',
            '--resolution', '2026-08-18T10:25:00Z'
        ])
        self.assertEqual(result.code, 0)
        self.assertIn('unknown', result.stdout)

    def test_json_output(self):
        result = run([
            '--start', '2026-08-18T10:00:00Z',
            '--detection', '2026-08-18T10:05:00Z',
            '--mitigation', '2026-08-18T10:15:00Z',
            '--resolution', '2026-08-18T10:25:00Z',
            '--json'
        ])
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data['ttd'], 300)
        self.assertEqual(data['ttm'], 600)
        self.assertEqual(data['ttr'], 1500)

    def test_json_with_missing_values(self):
        result = run([
            '--start', '2026-08-18T10:00:00Z',
            '--detection', '2026-08-18T10:05:00Z',
            '--json'
        ])
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data['ttd'], 300)
        self.assertIsNone(data['ttm'])
        self.assertIsNone(data['ttr'])

    def test_missing_required_start(self):
        result = run([
            '--detection', '2026-08-18T10:05:00Z'
        ])
        self.assertEqual(result.code, 2)

    def test_invalid_start_time(self):
        result = run([
            '--start', 'not-a-time'
        ])
        self.assertEqual(result.code, 2)
        self.assertIn('invalid start time', result.stderr)

    def test_mixed_formats(self):
        """Use different timestamp formats in one run."""
        result = run([
            '--start', '2026-08-18T10:00:00Z',
            '--detection', '18/Aug/2026:10:05:00 +0000',
            '--mitigation', '1787119500',  # epoch
            '--resolution', 'Aug 18 10:25:00'  # syslog
        ])
        self.assertEqual(result.code, 0)
        self.assertIn('Time to Detect', result.stdout)

    def test_dst_boundary_handling(self):
        """Test computation across a DST boundary."""
        # Times around DST transition (spring forward in US)
        # 2026-03-08 at 02:00 EDT becomes 03:00 EDT
        result = run([
            '--start', '2026-03-08T06:55:00Z',  # 01:55 EST
            '--detection', '2026-03-08T07:05:00Z',  # 03:05 EDT (after transition)
            '--json'
        ])
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)
        # Should still be exactly 10 minutes apart in UTC
        self.assertEqual(data['ttd'], 600)

    def test_timezone_change_handling(self):
        """Test computation across a timezone change."""
        result = run([
            '--start', '2026-08-18T12:30:00+02:00',
            '--detection', '2026-08-18T08:35:00-05:00',
            '--json'
        ])
        self.assertEqual(result.code, 0)
        data = json.loads(result.stdout)
        # Both should normalize to UTC and compute correctly
        # 12:30+02:00 = 10:30 UTC, 08:35-05:00 = 13:35 UTC = 5 min difference
        self.assertIsNotNone(data['ttd'])
        self.assertGreater(data['ttd'], 0)


if __name__ == '__main__':
    unittest.main()
