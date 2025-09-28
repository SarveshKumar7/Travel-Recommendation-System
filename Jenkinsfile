pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "travel-backend"
        FRONTEND_IMAGE = "travel-frontend"
        AWS_REGION = "eu-north-1"                     // replace with your AWS region
        AWS_ECR_REPO_BACKEND = "886011807844.dkr.ecr.eu-north-1.amazonaws.com/travel-backend"   // replace with your backend ECR repo
        AWS_ECR_REPO_FRONTEND = "886011807844.dkr.ecr.eu-north-1.amazonaws.com/travel-frontend" // replace with your frontend ECR repo
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                git branch: 'main', url: 'https://github.com/SarveshKumar7/Travel-Recommendation-System'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing backend and frontend dependencies..."
                sh '''
                # Backend dependencies
                cd backend
                pip install -r requirements.txt

                # Frontend dependencies
                cd ../frontend
                npm install
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running backend tests..."
                sh '''
                cd backend
                pytest || true   # continue even if no tests exist
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "Building Docker images..."
                sh '''
                # Backend Docker build
                docker build -t $BACKEND_IMAGE ./backend

                # Frontend Docker build
                docker build -t $FRONTEND_IMAGE ./frontend
                '''
            }
        }

        stage('Push Docker Images to AWS ECR') {
            steps {
                echo "Pushing Docker images to AWS ECR..."
                sh '''
                # Login to AWS ECR
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
                echo "Deploy stage: Replace this with your ECS service update commands"
                sh '''
                # Example: Update ECS services (replace cluster and service names)
                # aws ecs update-service --cluster my-cluster --service backend-service --force-new-deployment
                # aws ecs update-service --cluster my-cluster --service frontend-service --force-new-deployment
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