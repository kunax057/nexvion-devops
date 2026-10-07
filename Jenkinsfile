pipeline {
    agent any

    stages {
        stage('Identity Test') {
            steps {
                sh '''
                    echo "=== PIPELINE IDENTITY ==="
                    id

                    echo "=== PROCESS ==="
                    ps -ef

                    echo "=== DOCKER SOCKET ==="
                    ls -ln /var/run/docker.sock

                    echo "=== WAITING 60 SECONDS ==="
                    sleep 60
                '''
            }
        }
    }
}
