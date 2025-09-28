pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "travel-backend"
        FRONTEND_IMAGE = "travel-frontend"
        AWS_REGION = "eu-north-1"
        AWS_ECR_REPO_BACKEND = "886011807844.dkr.ecr.eu-north-1.amazonaws.com/travel-backend"
        AWS_ECR_REPO_FRONTEND = "886011807844.dkr.ecr.eu-north-1.amazonaws.com/travel-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                git branch: 'main', url: 'https://github.com/SarveshKumar7/Travel-Recommendation-System'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "Building Docker images..."
                sh '''
                docker build -t $BACKEND_IMAGE ./backend
                docker build -t $FRONTEND_IMAGE ./frontend
                '''
            }
        }

        stage('Push Docker Images to AWS ECR') {
            steps {
                echo "Pushing Docker images to AWS ECR..."
                sh '''
                aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REPO_BACKEND
                aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REPO_FRONTEND

                docker tag $BACKEND_IMAGE:latest $AWS_ECR_REPO_BACKEND:latest
                docker push $AWS_ECR_REPO_BACKEND:latest

                docker tag $FRONTEND_IMAGE:latest $AWS_ECR_REPO_FRONTEND:latest
                docker push $AWS_ECR_REPO_FRONTEND:latest
                '''
            }
        }

        stage('Deploy to AWS ECS') {
            steps {
                echo "Deploy stage: Replace this with your ECS service update commands"
            }
        }
    }

    post {
        success { echo "✅ Pipeline completed successfully!" }
        failure { echo "❌ Pipeline failed!" }
    }
}