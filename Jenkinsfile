
pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    echo "=== BUILDING SECURED NEXVION IMAGE ==="
                    docker build -t nexvion:1.1 .
                    docker images nexvion:1.1
                '''
            }
        }

        stage('Deploy NEXVION') {
            steps {
                sh '''
                    set -e
                    echo "=== DEPLOYING NEXVION 1.1 ==="
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
                    echo "=== NEXVION DEPLOYMENT SUCCESSFUL ==="
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
