#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ANALYZER = Path(__file__).with_name("incident_analyzer.py")


class IncidentAnalyzerTests(unittest.TestCase):
    def run_analyzer(self, content, json_output=False):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "diagnostics.log"
            report.write_text(content, encoding="utf-8")

            command = [sys.executable, str(ANALYZER), str(report)]
            output_file = Path(directory) / "incident-report.json"

            if json_output:
                command.append(str(output_file))

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

            structured = None
            if json_output and output_file.exists():
                structured = json.loads(
                    output_file.read_text(encoding="utf-8")
                )

            return result, structured

    def test_healthy_report(self):
        result, _ = self.run_analyzer(
            "NEXVION DIAGNOSTIC REPORT\n"
            "PASS: NEXVION returned a successful HTTP response.\n"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "No configured incident patterns detected", result.stdout
        )

    def test_http_failure(self):
        result, _ = self.run_analyzer(
            "FAIL: NEXVION did not return a successful HTTP response.\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("HTTP health check failed", result.stdout)

    def test_kubernetes_failure(self):
        result, _ = self.run_analyzer(
            "nexvion-test 0/1 CrashLoopBackOff\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Kubernetes pod failure", result.stdout)

    def test_http_503(self):
        result, _ = self.run_analyzer(
            "HTTP/1.1 503 Service Unavailable\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Application or proxy error", result.stdout)

    def test_http_failure_is_critical(self):
        result, structured = self.run_analyzer(
            "FAIL: NEXVION did not return a successful HTTP response.\n",
            json_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(structured["status"], "INCIDENTS_DETECTED")
        self.assertEqual(structured["incidents"][0]["severity"], "CRITICAL")
        self.assertTrue(structured["incidents"][0]["evidence"])

    def test_json_report_contains_remediation(self):
        _, structured = self.run_analyzer(
            "nexvion-test 0/1 CrashLoopBackOff\n",
            json_output=True,
        )
        incident = structured["incidents"][0]
        self.assertEqual(incident["id"], "NEX-002")
        self.assertTrue(incident["recommendation"])
        self.assertEqual(incident["match_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
