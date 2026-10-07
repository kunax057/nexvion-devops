pipeline {
    agent any

    stages {
        stage('Identity Test') {
            steps {
                sh '''
                    echo "=== PIPELINE IDENTITY ==="
                    id

                    echo "=== DOCKER SOCKET ==="
                    ls -ln /var/run/docker.sock

                    echo "=== DOCKER VERSION ==="
                    docker --version

                    echo "=== DOCKER TEST ==="
                    docker ps
                '''
            }
        }
    }
}
