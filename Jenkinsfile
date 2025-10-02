// Jenkinsfile: DevOps Pipeline for Healthcare Booking System

pipeline {
    agent any 
    
    environment {
        // --- CONFIGURE THESE ENVIRONMENT VARIABLES ---
        
        // SonarQube installation name (as configured in Jenkins -> Manage Jenkins -> Global Tool Configuration)
        SONAR_SCANNER_HOME = tool 'SonarQubeScanner' 
        SONAR_URL = 'http://localhost:9000'
        
        // Docker registry (e.g., your Docker Hub username)
        DOCKER_REGISTRY = 'vuhoangnamdoan' 
        
        // Staging/Test Server SSH details
        STAGING_SERVER = 'namdoan@172.26.108.190' 
        
        // --- KUBERNETES/RELEASE VARIABLES ---
        K8S_CONTEXT = 'docker-desktop' // e.g., 'microk8s'
        K8S_NAMESPACE = 'production'
        
        // --- CREDENTIALS (Must be configured in Jenkins) ---
        // 'docker-creds': DockerHub username/password credential ID
        // 'ssh-creds-staging': SSH private key credential ID for staging server
        // 'kube-creds': Kubernetes service account or kubeconfig credential ID
    }
    
    stages {
        
        // 1. BUILD STAGE: Containerize Django and React
        stage('Build Artifacts (Docker)') {
            steps {
                echo 'Building frontend and backend Docker images...'
                
                // Build the React Frontend assets first
                // sh 'cd frontend && npm install && npm run build'
                nodejs('Node_20') { 
                    // FRONTEND BUILD STEPS
                    sh 'cd frontend && npm install'
                    sh 'cd frontend && npm run build'
                }

                
                script {
                    // Build backend image (from root-level Dockerfile)
                    docker.build("${DOCKER_REGISTRY}/booking-backend:${BUILD_ID}", '.')
                    // Build frontend image (assuming a simple Dockerfile in frontend/ or serving the build output)
                    docker.build("${DOCKER_REGISTRY}/booking-frontend:${BUILD_ID}", './frontend')
                    
                    // Push images to DockerHub
                    withCredentials([usernamePassword(credentialsId: 'docker-creds', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}"
                        sh "docker push ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID}"
                        sh "docker push ${DOCKER_REGISTRY}/booking-frontend:${BUILD_ID}"
                    }
                }
            }
        }
        
        // 2. TEST STAGE: Run PyTest (Django) and Jest (React)
        stage('Test') {
            steps {
                echo 'Running automated tests: PyTest (Backend) and Jest (Frontend)...'
                // Run Tests inside a temporary container to ensure consistent environment
                withDockerRegistry(credentialsId: 'docker-creds', url: '') {
                    // Backend (PyTest)
                    // sh "docker run --rm ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID} sh -c 'pytest --junitxml=reports/backend-tests.xml'"
                    sh "docker run --rm \
                    -e DJANGO_SETTINGS_MODULE=health_system.settings \
                    -e PYTHONPATH=/app \
                    -e DJANGO_ALLOW_ASYNC_UNSAFE=true \
                    ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID} \
                    pytest --junitxml=reports/backend-tests.xml"

                    // Frontend (Jest) - assuming Jest is configured in package.json
                    // sh 'cd frontend && npm test -- --ci --json --outputFile=../reports/frontend-tests.json'
                    sh 'cd frontend && npm test -- --ci --reporters=default --reporters=jest-junit --outputFile=../reports/frontend-tests.xml'
                }
                
                // Publish Test Results (Requires JUnit plugin)
                junit '**/reports/*-tests.xml' 
            }
        }
        
        // 3. CODE QUALITY STAGE: SonarQube Analysis
        stage('Code Quality (SonarQube)') {
            steps {
                echo 'Running SonarQube analysis...'
                // The sonar-project.properties file should be in your project root
                withSonarQubeEnv(installationName: SONAR_SCANNER_HOME) {
                    sh "${SONAR_SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectKey=health-system -Dsonar.sources=."
                }
                // Gate the pipeline based on SonarQube Quality Gate result
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        // 4. SECURITY STAGE: Bandit Analysis
        stage('Security (Bandit)') {
            steps {
                echo 'Running Bandit security analysis on the Django backend...'
                // Run Bandit on the Python code (recursive scan on backend apps)
                sh 'bandit -r users/ appointments/ -o reports/bandit-report.json -f json'
                
                // Optional: Check the exit code of Bandit to fail the stage on HIGH severity issues
                // Example: sh('bandit -r . || exit 1') 
            }
        }

        // 5. DEPLOY STAGE: Deploy to Staging (Test) Environment
        stage('Deploy to Staging (Docker Compose)') {
            steps {
                echo 'Deploying to Staging Environment using Docker Compose on test server...'
                
                // Use SSH to log into the staging server and execute deployment
                // (Requires ssh-creds-staging to be set up)
                withCredentials([sshUserPrivateKey(credentialsId: 'ssh-creds-staging', keyFileVariable: 'KEY_FILE', usernameVariable: 'USER')]) {
                    // Copy the docker-compose.yml and run it
                    sh "scp -i ${KEY_FILE} docker-compose.yml ${USER}@staging.example.com:/opt/staging/docker-compose.yml"
                    sh "ssh -i ${KEY_FILE} ${USER}@staging.example.com 'cd /opt/staging && docker-compose pull && docker-compose up -d --remove-orphans'"
                }
                echo 'Staging deployment complete. Run acceptance tests now.'
            }
        }
        
        // 6. RELEASE STAGE: Promote to Production (Kubernetes)
        stage('Release to Production (Kubernetes)') {
            steps {
                echo 'Promoting Staging build to Production environment via Kubernetes...'
                // This step applies your k8s manifests using kubectl
                withKubeConfig(credentialsId: 'kube-creds', contextName: K8S_CONTEXT) {
                    sh "kubectl apply -f k8s/ -n ${K8S_NAMESPACE}"
                    // Optional: Wait for the deployment to roll out successfully
                    sh "kubectl rollout status deployment/backend-deployment -n ${K8S_NAMESPACE}"
                    sh "kubectl rollout status deployment/frontend-deployment -n ${K8S_NAMESPACE}"
                }
                echo 'Production release complete.'
            }
        }
        
        // 7. MONITORING STAGE: Datadog Integration
        stage('Monitoring & Alerting (Datadog)') {
            steps {
                echo 'Sending deployment event to Datadog and ensuring monitoring is active...'
                // Send an event to Datadog to mark the deployment (Requires DATADOG_API_KEY credential)
                withCredentials([string(credentialsId: 'DATADOG_API_KEY', variable: 'DD_API_KEY')]) {
                    sh """
                    curl -X POST "https://api.datadoghq.com/api/v1/events" \
                    -H "Content-Type: application/json" \
                    -H "DD-API-KEY: ${DD_API_KEY}" \
                    -d '{
                        "title": "Deployment Successful",
                        "text": "Build ${BUILD_ID} deployed to production.",
                        "tags": ["env:prod", "service:booking-system"],
                        "alert_type": "info"
                    }'
                    """
                }
                echo 'Datadog deployment event logged.'
            }
        }
    }
}
