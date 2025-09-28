pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "travel-backend"
        FRONTEND_IMAGE = "travel-frontend"
        AWS_REGION = "eu-north-1"
        AWS_ECR_REPO_BACKEND = "886011807844.dkr.ecr.eu-north-1.amazonaws.com/travel-backend"
        AWS_ECR_REPO_FRONTEND = "886011807844.dkr.ecr.eu-north-1.amazonaws.com/travel-frontend"
        // AWS credentials from Jenkins Credentials (add in Jenkins > Credentials)
        AWS_CREDS = credentials('aws-creds')
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
                    # Login to ECR
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REPO_BACKEND
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REPO_FRONTEND

                    # Tag and push backend image
                    docker tag $BACKEND_IMAGE:latest $AWS_ECR_REPO_BACKEND:latest
                    docker push $AWS_ECR_REPO_BACKEND:latest

                    # Tag and push frontend image
                    docker tag $FRONTEND_IMAGE:latest $AWS_ECR_REPO_FRONTEND:latest
                    docker push $AWS_ECR_REPO_FRONTEND:latest
                '''
            }
        }

        stage('Deploy to AWS ECS') {
            steps {
                echo "Deploying to ECS..."
                sh '''
                    # Replace <cluster_name> and <service_name> with your ECS values
                    aws ecs update-service --cluster <cluster_name> --service <service_name> --force-new-deployment --region $AWS_REGION
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}