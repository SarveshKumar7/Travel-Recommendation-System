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
                // Using AWS credentials stored in Jenkins
                withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
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
        }

        stage('Run Docker Containers (Optional)') {
            steps {
                echo "Running Docker containers locally..."
                sh '''
                    # Stop existing containers if running
                    docker rm -f backend || true
                    docker rm -f frontend || true

                    # Run backend container
                    docker run -d --name backend -p 5000:5000 $BACKEND_IMAGE:latest

                    # Run frontend container
                    docker run -d --name frontend -p 3000:3000 $FRONTEND_IMAGE:latest
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