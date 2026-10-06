pipeline {
    agent any

    stages {

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

                    docker exec nexvion-app \
                      wget -q --spider http://localhost/

                    docker inspect --format='{{.State.Status}}' nexvion-app \
                      | grep -q running
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
