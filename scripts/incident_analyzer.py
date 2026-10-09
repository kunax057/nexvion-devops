#!/usr/bin/env python3
"""Rule-based incident analyzer for NEXVION DevOps diagnostics."""

import re
import sys
from pathlib import Path

RULES = [
    (
        "HTTP health check failed",
        re.compile(r"FAIL: NEXVION did not return a successful HTTP response", re.I),
        "Check the nexvion-app container, Nginx logs, and port 8081 mapping.",
    ),
    (
        "Kubernetes pod failure",
        re.compile(
            r"\bCrashLoopBackOff\b|\bImagePullBackOff\b|\bErrImagePull\b|"
            r"\bOOMKilled\b|\bCreateContainerConfigError\b",
            re.I,
        ),
        "Run kubectl get pods -o wide and kubectl describe pod <pod-name>.",
    ),
    (
        "Application or proxy error",
        re.compile(
            r"\bHTTP/[0-9.]+\s+(?:5\d\d)\b|\b(?:502|503|504)\b|"
            r"\bupstream timed out\b|\bconnection refused\b",
            re.I,
        ),
        "Inspect application and Nginx logs, service endpoints, and port mappings.",
    ),
    (
        "Container exited or unhealthy",
        re.compile(r"status=(?:exited|dead)|health=unhealthy", re.I),
        "Run docker ps -a and docker logs <container-name> to identify the cause.",
    ),
    (
        "Kubernetes warning event",
        re.compile(
            r"\bWarning\s+(?:Failed|Unhealthy|BackOff|FailedScheduling|"
            r"FailedMount|Evicted)\b",
            re.I,
        ),
        "Inspect kubectl describe pod <pod-name> and kubectl get events.",
    ),
    (
        "Application error in logs",
        re.compile(r"\b(?:ERROR|FATAL|Traceback \(most recent call last\))\b", re.I),
        "Review the surrounding log lines and identify the first underlying error.",
    ),
]


def analyze(path: Path) -> int:
    if not path.is_file():
        print(f"ERROR: Diagnostic report not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text(encoding="utf-8", errors="replace")
    incidents = []

    for title, pattern, recommendation in RULES:
        matches = list(pattern.finditer(content))
        if matches:
            incidents.append((title, len(matches), recommendation))

    print("NEXVION INCIDENT ANALYSIS")
    print(f"Report: {path}")
    print(f"Lines analyzed: {len(content.splitlines())}")
    print()

    if not incidents:
        print("No configured incident patterns detected.")
        print("This does not prove that every component is healthy.")
        print("Review the diagnostic report and monitoring dashboards.")
        return 0

    print(f"Incident categories detected: {len(incidents)}")
    for number, (title, count, recommendation) in enumerate(incidents, 1):
        print(f"\n{number}. {title} (matches: {count})")
        print(f"   Recommended action: {recommendation}")

    print("\nAnalysis complete. Verify each finding against the original logs.")
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python3 scripts/incident_analyzer.py <diagnostic-report.log>",
            file=sys.stderr,
        )
        return 2
    return analyze(Path(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
