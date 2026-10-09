pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
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
    }

    post {
        success {
            echo 'NEXVION CI/CD, Ansible validation, and security scan completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the stage logs.'
        }
    }
}
