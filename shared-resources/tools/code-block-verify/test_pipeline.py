"""Exercise the same explicit bash -e -o pipefail semantics used by Actions."""
import subprocess
import unittest

class PipelineTests(unittest.TestCase):
    def test_tee_preserves_python_failure(self):
        result = subprocess.run(
            ['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail', '-c',
             "python3 -c 'import sys; print(\"intentional regression failure\"); sys.exit(23)' | tee /dev/null"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
        self.assertIn('intentional regression failure', result.stdout)

    def test_successful_pipeline_passes(self):
        result = subprocess.run(
            ['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail', '-c',
             "python3 -c 'print(\"intentional regression success\")' | tee /dev/null"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == '__main__':
    unittest.main()
