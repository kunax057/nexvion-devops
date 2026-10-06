pipeline {
    agent any

    stages {

        stage('Build') {
            steps {
                sh '''
                    docker compose build
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
