pipeline {

    agent any

    environment {
        PATH = "$PATH:/usr/local/bin:/opt/homebrew/Caskroom/miniconda/base/bin/"

        # Setting environment variables for MinIO (can be set in Jenkins or .env file)
        MINIO_ENDPOINT = credentials('minio-endpoint')
        MINIO_ACCESS_KEY = credentials('minio-access-key')
        MINIO_SECRET_KEY = credentials('minio-secret-key')
        MINIO_SECURE = credentials('minio-secure')
        MINIO_BUCKET = credentials('minio-bucket')
    }

    stages {
        stage('Checkout') {
            steps {
                # Checking out the v0.2.0 branch from the GitHub repository
                git branch: 'v0.2.0', url: 'https://github.com/DrBenjamin/BenBox.git'
            }
        }

        stage('Test') {
            steps {
                # Running pytest for all Python code (assumes tests are present)
                sh 'python -m pytest --junitxml results.xml -W ignore::DeprecationWarning'
            }
        }

        stage('Build & Deploy') {
            steps {
                # Updating to use relative path for docker-compose
                sh 'docker-compose -f ../BenBox/docker-compose.yml build --no-cache'
                sh 'docker-compose -f ../BenBox/docker-compose.yml --project-name benbox up -d'
                # Pruning unused images to save space
                sh 'docker image prune -fa'
            }
        }
    }
    post {
        always {
            # Publishing test results
            junit testResults: 'results.xml', skipPublishingChecks: true
        }
    }
}