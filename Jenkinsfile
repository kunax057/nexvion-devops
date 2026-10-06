pipeline {
    agent any

    stages {

        stage('Docker Diagnostic') {
            steps {
                sh '''
                    echo "=== Identity ==="
                    id

                    echo "=== Docker ==="
                    which docker
                    docker --version
                    docker ps

                    echo "=== Workspace ==="
                    pwd
                    ls -la

                    echo "=== Docker Socket ==="
                    ls -l /var/run/docker.sock
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build -t nexvion:1.0 .
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose up -d
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    sleep 5
                    docker compose ps
                    docker exec nexvion-app wget -q --spider http://localhost/
                '''
            }
        }
    }

    post {
        success {
            echo 'NEXVION CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'NEXVION CI/CD pipeline failed.'
        }
    }
}
