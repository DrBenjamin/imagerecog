pipeline {

    agent any

    environment {
        PATH = "$PATH:/usr/local/bin:/opt/homebrew/Caskroom/miniconda/base/bin/"

        // Setting environment variables for MinIO (set in Jenkins credentials)
        MINIO_ENDPOINT = credentials('MINIO_ENDPOINT')
        MINIO_ACCESS_KEY = credentials('MINIO_ACCESS_KEY')
        MINIO_SECRET_KEY = credentials('MINIO_SECRET_KEY')
        MINIO_SECURE = credentials('MINIO_SECURE')
        MINIO_BUCKET = credentials('MINIO_BUCKET')

        // Setting environment variables for Snowflake (set in Jenkins credentials)
        SNOWFLAKE_USER = credentials('SNOWFLAKE_USER')
        SNOWFLAKE_ACCOUNT = credentials('SNOWFLAKE_ACCOUNT')
        SNOWFLAKE_WAREHOUSE = credentials('SNOWFLAKE_WAREHOUSE')
        SNOWFLAKE_DATABASE = credentials('SNOWFLAKE_DATABASE')
        SNOWFLAKE_SCHEMA = credentials('SNOWFLAKE_SCHEMA')
        SNOWFLAKE_ROLE = credentials('SNOWFLAKE_ROLE')
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

        stage('Test (Pytest)') {
            steps {
                sh '''
                    cd /home/jenkins/BenBox
                    $HOME/miniforge3/condabin/conda run -n BenBox python -m pytest --maxfail=1 --disable-warnings --junitxml=test.xml
                    cp /home/jenkins/BenBox/test.xml $WORKSPACE/test.xml
                '''
            }
            post {
                always {
                    // Publishing PyTest JUnit XML results from workspace
                    junit 'test.xml'
                }
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