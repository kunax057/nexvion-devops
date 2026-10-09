#!/usr/bin/env python3

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ANALYZER = Path(__file__).with_name("incident_analyzer.py")


class IncidentAnalyzerTests(unittest.TestCase):
    def run_analyzer(self, content):
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".log", delete=False
        ) as report:
            report.write(content)
            report_path = Path(report.name)

        try:
            return subprocess.run(
                [sys.executable, str(ANALYZER), str(report_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            report_path.unlink(missing_ok=True)

    def test_healthy_report(self):
        result = self.run_analyzer(
            "NEXVION DIAGNOSTIC REPORT\n"
            "PASS: NEXVION returned a successful HTTP response.\n"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("No configured incident patterns detected", result.stdout)

    def test_http_failure(self):
        result = self.run_analyzer(
            "FAIL: NEXVION did not return a successful HTTP response.\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("HTTP health check failed", result.stdout)

    def test_kubernetes_failure(self):
        result = self.run_analyzer("nexvion-test 0/1 CrashLoopBackOff\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Kubernetes pod failure", result.stdout)

    def test_http_503(self):
        result = self.run_analyzer("HTTP/1.1 503 Service Unavailable\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Application or proxy error", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
