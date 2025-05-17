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
                // Using local repo and update it
                sh '''
                    cd /home/jenkins/BenBox
                    git pull origin v0.2.0
                '''
            }
        }

        stage('Build & Deploy') {
            steps {
                // Using local repo and building docker image and deploying
                sh '''
                    cd /home/jenkins/BenBox
                    docker-compose -f docker-compose.yml down --remove-orphans
                    docker image prune -fa
                    docker system prune -af
                    docker volume prune -f
                    docker-compose -f docker-compose.yml build --no-cache
                    docker-compose -f docker-compose.yml --project-name benbox up -d
                '''
            }
        }
    }
}