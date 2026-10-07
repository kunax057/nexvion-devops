pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "=== BUILDING NEXVION IMAGE ==="
                    docker build -t nexvion:1.0 .
                    docker images nexvion:1.0
                '''
            }
        }

        stage('Deploy NEXVION') {
            steps {
                sh '''
                    echo "=== DEPLOYING NEXVION ==="

                    docker rm -f nexvion-app 2>/dev/null || true

                    docker run -d \
                        --name nexvion-app \
                        --restart unless-stopped \
                        -p 8081:80 \
                        nexvion:1.0

                    echo "=== CONTAINER STATUS ==="
                    docker ps --filter name=nexvion-app
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "=== WAITING FOR NEXVION ==="
                    sleep 5

                    echo "=== HEALTH CHECK ==="
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
