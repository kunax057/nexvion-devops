
#!/usr/bin/env python3
"""Rule-based incident analyzer for NEXVION DevOps diagnostics."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RULES = [
    {
        "id": "NEX-001",
        "title": "HTTP health check failed",
        "severity": "CRITICAL",
        "pattern": re.compile(
            r"FAIL: NEXVION did not return a successful HTTP response", re.I
        ),
        "recommendation": (
            "Check docker ps, docker logs nexvion-app, "
            "and the host port 8081 mapping."
        ),
    },
    {
        "id": "NEX-002",
        "title": "Kubernetes pod failure",
        "severity": "CRITICAL",
        "pattern": re.compile(
            r"\bCrashLoopBackOff\b|\bImagePullBackOff\b|\bErrImagePull\b|"
            r"\bOOMKilled\b|\bCreateContainerConfigError\b",
            re.I,
        ),
        "recommendation": (
            "Run kubectl get pods -o wide and "
            "kubectl describe pod <pod-name>."
        ),
    },
    {
        "id": "NEX-003",
        "title": "Application or proxy error",
        "severity": "HIGH",
        "pattern": re.compile(
            r"\bHTTP/[0-9.]+\s+5\d\d\b|\b(?:502|503|504)\b|"
            r"\bupstream timed out\b|\bconnection refused\b",
            re.I,
        ),
        "recommendation": (
            "Inspect application logs, Nginx logs, service endpoints, "
            "and port mappings."
        ),
    },
    {
        "id": "NEX-004",
        "title": "Container exited or unhealthy",
        "severity": "HIGH",
        "pattern": re.compile(r"status=(?:exited|dead)|health=unhealthy", re.I),
        "recommendation": (
            "Run docker ps -a and docker logs <container-name> "
            "to investigate the cause."
        ),
    },
    {
        "id": "NEX-005",
        "title": "Kubernetes warning event",
        "severity": "HIGH",
        "pattern": re.compile(
            r"\bWarning\s+(?:Failed|Unhealthy|BackOff|FailedScheduling|"
            r"FailedMount|Evicted)\b",
            re.I,
        ),
        "recommendation": (
            "Inspect kubectl describe pod <pod-name> "
            "and kubectl get events."
        ),
    },
    {
        "id": "NEX-006",
        "title": "Application error in logs",
        "severity": "MEDIUM",
        "pattern": re.compile(
            r"\b(?:ERROR|FATAL|Traceback \(most recent call last\))\b", re.I
        ),
        "recommendation": (
            "Review the surrounding log lines and identify the first "
            "underlying error."
        ),
    },
]


def analyze(path: Path) -> tuple[int, dict]:
    if not path.is_file():
        print(f"ERROR: Diagnostic report not found: {path}", file=sys.stderr)
        return 2, {}

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    incidents = []

    for rule in RULES:
        evidence = []
        for line_number, line in enumerate(lines, start=1):
            if rule["pattern"].search(line):
                evidence.append({
                    "line": line_number,
                    "text": line.strip()[:500],
                })

        if evidence:
            incidents.append({
                "id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "match_count": len(evidence),
                "evidence": evidence[:20],
                "recommendation": rule["recommendation"],
            })

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
    incidents.sort(key=lambda item: severity_order[item["severity"]])

    result = {
        "application": "NEXVION",
        "analyzer_type": "rule-based",
        "source_report": str(path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lines_analyzed": len(lines),
        "incident_count": len(incidents),
        "incidents": incidents,
        "status": "INCIDENTS_DETECTED" if incidents else "NO_MATCHING_PATTERNS",
        "limitations": (
            "No matching rules do not guarantee system health. "
            "Findings require human verification."
        ),
    }

    print("NEXVION INCIDENT ANALYSIS")
    print(f"Report: {path}")
    print(f"Lines analyzed: {len(lines)}")
    print(f"Incident categories detected: {len(incidents)}")

    if not incidents:
        print("No configured incident patterns detected.")
        print(result["limitations"])
        return 0, result

    for number, incident in enumerate(incidents, start=1):
        print(
            f"\n{number}. [{incident['severity']}] "
            f"{incident['id']} - {incident['title']}"
        )
        print(f"   Matches: {incident['match_count']}")
        print(f"   Evidence: {incident['evidence'][0]['text']}")
        print(f"   Recommended action: {incident['recommendation']}")

    print("\nAnalysis complete. Verify findings against the original logs.")
    return 1, result


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(
            "Usage: python3 scripts/incident_analyzer.py "
            "<diagnostic-report.log> [incident-report.json]",
            file=sys.stderr,
        )
        return 2

    source = Path(sys.argv[1])
    exit_code, result = analyze(source)

    if result and len(sys.argv) == 3:
        output = Path(sys.argv[2])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Structured incident report saved to: {output}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
