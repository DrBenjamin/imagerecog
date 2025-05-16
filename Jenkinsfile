pipeline {

    agent any

    environment {
        PATH = "$PATH:/usr/local/bin:/opt/homebrew/Caskroom/miniconda/base/bin/"

        // Setting environment variables for MinIO (can be set in Jenkins or .env file)
        MINIO_ENDPOINT = credentials('MINIO_ENDPOINT')
        MINIO_ACCESS_KEY = credentials('MINIO_ACCESS_KEY')
        MINIO_SECRET_KEY = credentials('MINIO_SECRET_KEY')
        MINIO_SECURE = credentials('MINIO_SECURE')
        MINIO_BUCKET = credentials('MINIO_BUCKET')
    }

    stages {
        stage('Checkout') {
            steps {
                // Checking out the v0.2.0 branch from the GitHub repository
                git branch: 'v0.2.0', url: 'https://github.com/DrBenjamin/BenBox.git'
            }
        }

        stage('Build & Deploy') {
            steps {
                // Updating to use relative path for docker-compose
                sh 'docker-compose -f ../BenBox/docker-compose.yml build --no-cache'
                sh 'docker-compose -f ../BenBox/docker-compose.yml --project-name benbox up -d'

                // Pruning unused images to save space
                sh 'docker image prune -fa'
            }
        }
    }
}