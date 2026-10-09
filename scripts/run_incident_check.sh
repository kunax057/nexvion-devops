#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== NEXVION INCIDENT CHECK ==="

if ! "$ROOT_DIR/scripts/collect_diagnostics.sh"; then
    echo "ERROR: Diagnostic collection failed." >&2
    exit 2
fi

LATEST_REPORT="$(
    find "$ROOT_DIR/logs/incident-reports" \
        -maxdepth 1 -type f -name 'diagnostics_*.log' \
        -printf '%T@ %p\n' |
    sort -nr |
    head -n 1 |
    cut -d ' ' -f 2-
)"

if [[ -z "$LATEST_REPORT" ]]; then
    echo "ERROR: No diagnostic report found." >&2
    exit 2
fi

echo
echo "Analyzing: $LATEST_REPORT"
python3 "$ROOT_DIR/scripts/incident_analyzer.py" "$LATEST_REPORT"
exit $?
