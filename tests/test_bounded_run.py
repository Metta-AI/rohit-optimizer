import json
from pathlib import Path
import subprocess
import sys
import signal
import time
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'skills/softmax-demo/scripts/bounded_run.py'


class BoundedRunTests(unittest.TestCase):
    def run_operation(self, directory, code, *options):
        return subprocess.run([sys.executable, str(RUNNER), '--state-dir', directory, '--key', 'test',
                               '--reserve-mib', '1', *options, '--', sys.executable, '-c', code],
                              capture_output=True, text=True, timeout=10)

    def test_output_flood_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_operation(directory, 'while True: print("x" * 10000)', '--output-mib', '1')
            record = json.loads(result.stdout)
            self.assertEqual(record['status'], 'output_limit')
            self.assertLessEqual(Path(record['output']).stat().st_size, 1024 * 1024)

    def test_timeout_and_retry_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            for _ in range(2):
                result = self.run_operation(directory, 'import time; time.sleep(30)', '--seconds', '1', '--retry-safe')
                self.assertEqual(json.loads(result.stdout)['status'], 'timeout')
            result = self.run_operation(directory, 'import time; time.sleep(30)', '--seconds', '1', '--retry-safe')
            self.assertEqual(json.loads(result.stdout)['status'], 'reconciliation_required')

    def test_completed_operation_not_repeated(self):
        with tempfile.TemporaryDirectory() as directory:
            code = f'from pathlib import Path; p=Path({directory!r}) / "writes"; p.open("a").write("x")'
            self.assertEqual(self.run_operation(directory, code).returncode, 0)
            self.assertEqual(self.run_operation(directory, code).returncode, 0)
            self.assertEqual((Path(directory) / 'writes').read_text(), 'x')

    def test_uncertain_external_write_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as directory:
            code = 'raise SystemExit(1)'
            self.run_operation(directory, code)
            result = self.run_operation(directory, code)
            self.assertEqual(json.loads(result.stdout)['status'], 'reconciliation_required')

    def test_interrupted_operation_records_and_releases_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(RUNNER), '--state-dir', directory, '--key', 'test',
                       '--reserve-mib', '1', '--', sys.executable, '-c', 'import time; time.sleep(30)']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            deadline = time.monotonic() + 5
            while not (Path(directory) / 'test.1.log').exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            process.send_signal(signal.SIGTERM)
            output, errors = process.communicate(timeout=5)
            self.assertEqual(json.loads(output)['status'], 'interrupted', errors)
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(json.loads(result.stdout)['status'], 'reconciliation_required')

    def test_low_disk_blocks_before_command_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_operation(directory, 'raise SystemExit("must not run")', '--reserve-mib', '1000000000')
            self.assertEqual(json.loads(result.stdout)['status'], 'disk_reserve')
            self.assertFalse((Path(directory) / 'test.1.log').exists())

    def test_file_output_is_limited(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dump'
            result = self.run_operation(directory, f'open({str(output)!r}, "wb").write(b"x" * 2000000)', '--file-mib', '1')
            self.assertNotEqual(result.returncode, 0)
            self.assertLessEqual(output.stat().st_size, 1024 * 1024)


if __name__ == '__main__':
    unittest.main()
