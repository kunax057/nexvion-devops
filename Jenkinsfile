pipeline {
    agent any

    stages {
        stage('Incident Analyzer Tests') {
            steps {
                sh '''
                    set -e
                    echo "=== TESTING INCIDENT ANALYZER ==="
                    python3 scripts/test_incident_analyzer.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -eu
                    echo "=== PIPELINE DOCKER DIAGNOSTICS ==="
                    id
                    id -G
                    ls -ln /var/run/docker.sock
                    docker context show
                    docker info
                    echo "=== BUILDING NEXVION IMAGE ==="
                    docker build -t nexvion:1.1 .
                    docker images nexvion:1.1
                '''
            }
        }

        stage('Ansible Playbook Validation') {
            steps {
                sh '''
                    set -e
                    echo "=== VALIDATING ANSIBLE PLAYBOOK ==="
                    ansible-playbook --syntax-check \
                        -i ansible/inventory/hosts.ini \
                        ansible/site.yml
                    echo "Ansible playbook syntax validation successful."
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                    set -e
                    echo "=== SCANNING NEXVION IMAGE ==="
                    trivy image \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        --ignore-unfixed \
                        nexvion:1.1
                '''
            }
        }

        stage('Deploy NEXVION') {
            steps {
                sh '''
                    set -e
                    docker rm -f nexvion-app 2>/dev/null || true
                    docker run -d \
                        --name nexvion-app \
                        --restart unless-stopped \
                        -p 8081:80 \
                        nexvion:1.1
                    docker ps --filter name=nexvion-app
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    set -e
                    sleep 5
                    docker exec nexvion-app \
                        wget --no-verbose --tries=1 --spider \
                        http://localhost/
                    echo "NEXVION deployment and health check successful."
                '''
            }
        }

        stage('Incident Diagnostics and Analysis') {
            steps {
                sh '''
                    set -eu

                    REPORT="logs/incident-reports/jenkins-diagnostics.log"
                    JSON_REPORT="logs/incident-reports/jenkins-diagnostics.analysis.json"

                    mkdir -p logs/incident-reports

                    {
                        echo "NEXVION Jenkins Diagnostic Report"
                        echo "Generated at: $(date -Is)"
                        echo "=== CONTAINER STATUS ==="
                        docker ps -a --filter name=nexvion-app
                        echo "=== RECENT CONTAINER LOGS ==="
                        docker logs --tail 100 nexvion-app 2>&1 || \
                            echo "WARN: Could not read container logs."

                        echo "=== HTTP HEALTH CHECK ==="
                        HTTP_STATUS=$(curl -sS -o /dev/null \
                            -w '%{http_code}' \
                            --max-time 10 \
                            http://host.docker.internal:8081/ || true)

                        if [ "$HTTP_STATUS" = "200" ]; then
                            echo "PASS: NEXVION HTTP status 200"
                        else
                            echo "FAIL: NEXVION did not return a successful HTTP response (status: $HTTP_STATUS)"
                        fi
                    } > "$REPORT"

                    cat "$REPORT"

                    set +e
                    python3 scripts/incident_analyzer.py \
                        "$REPORT" "$JSON_REPORT"
                    ANALYSIS_STATUS=$?
                    set -e

                    if [ "$ANALYSIS_STATUS" -eq 2 ]; then
                        echo "ERROR: Incident analyzer could not process the report."
                        exit 2
                    elif [ "$ANALYSIS_STATUS" -eq 1 ]; then
                        echo "WARNING: Incident patterns detected. Reports will be archived."
                    elif [ "$ANALYSIS_STATUS" -eq 0 ]; then
                        echo "Incident analysis completed without matching patterns."
                    else
                        echo "ERROR: Unexpected analyzer exit code: $ANALYSIS_STATUS"
                        exit 2
                    fi

                    test -s "$JSON_REPORT"
                    echo "Incident analysis JSON report generated."
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'logs/incident-reports/*',
                             allowEmptyArchive: true
        }
        success {
            echo 'NEXVION CI/CD, incident tests, Ansible validation, security scan, deployment, health check, and diagnostics completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the stage logs and any archived diagnostic reports.'
        }
    }
}
