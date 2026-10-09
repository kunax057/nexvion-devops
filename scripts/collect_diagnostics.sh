#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${ROOT_DIR}/logs/incident-reports"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="${REPORT_DIR}/diagnostics_${TIMESTAMP}.log"

mkdir -p "$REPORT_DIR"

section() {
    printf '\n\n========== %s ==========\n' "$1" >> "$REPORT"
}

run_check() {
    local title="$1"
    shift
    section "$title"
    if "$@" >> "$REPORT" 2>&1; then
        :
    else
        echo "[WARN] Command failed: $*" >> "$REPORT"
    fi
}

{
    echo "NEXVION DIAGNOSTIC REPORT"
    echo "Generated: $(date --iso-8601=seconds)"
    echo "Host: $(hostname)"
} > "$REPORT"

run_check "DOCKER CONTAINER STATUS" \
    docker ps -a --no-trunc

run_check "NEXVION APPLICATION LOGS" \
    docker logs --tail 300 nexvion-app

run_check "JENKINS CONTAINER STATUS" \
    docker inspect --format '{{.Name}} status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}not-configured{{end}}' jenkins

if command -v kubectl >/dev/null 2>&1; then
    run_check "KUBERNETES DEPLOYMENTS" \
        kubectl get deployments -o wide

    run_check "KUBERNETES PODS" \
        kubectl get pods -o wide

    run_check "KUBERNETES EVENTS" \
        kubectl get events --sort-by=.lastTimestamp

    run_check "NEXVION KUBERNETES LOGS" \
        kubectl logs deployment/nexvion --all-pods=true --prefix=true --tail=150
fi

section "HTTP HEALTH CHECK"
if curl -fsS --max-time 10 http://localhost:8081/ -o /dev/null; then
    echo "PASS: NEXVION returned a successful HTTP response." >> "$REPORT"
else
    echo "FAIL: NEXVION did not return a successful HTTP response." >> "$REPORT"
fi

echo "Diagnostic report saved to: $REPORT"
