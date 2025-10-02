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
                script {
                    sh 'mkdir -p ${WORKSPACE}/reports'
                    sh 'mkdir -p ${WORKSPACE}/postman' // Ensure the postman folder exists

                    parallel(
                        // 1. BACKEND PYTEST (CRITICAL: Added PYTHONPATH and DJANGO_ALLOW_ASYNC_UNSAFE)
                        backend_tests: {
                            sh '''
                            # Create network and start a disposable Postgres for tests
                            docker network create ci-network || true
                            docker rm -f ci-postgres >/dev/null 2>&1 || true
                            docker run -d --name ci-postgres --network ci-network \
                              -e POSTGRES_DB=healthdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres123 \
                              postgres:15-alpine
                            
                            # Wait for Postgres to accept connections
                            echo "Waiting for Postgres..."
                            until docker run --rm --network ci-network postgres:15-alpine pg_isready -h ci-postgres -U postgres >/dev/null 2>&1; do sleep 1; done
                            
                            # Run backend tests in an ephemeral Python container using workspace sources
                            docker run --rm \
                              --network ci-network \
                              -v "${WORKSPACE}":/app -w /app \
                              -v "${WORKSPACE}/reports":/reports \
                              -e DJANGO_SETTINGS_MODULE=health_system.settings \
                              -e POSTGRES_HOST=ci-postgres \
                              -e POSTGRES_DB=healthdb \
                              -e POSTGRES_USER=postgres \
                              -e POSTGRES_PASSWORD=postgres123 \
                              -e PYTHONPATH=/app \
                              -e DJANGO_ALLOW_ASYNC_UNSAFE=true \
                              python:3.11-slim \
                              bash -lc "\
                                pip install --no-cache-dir -r requirements.txt pytest pytest-django >/dev/null && \
                                pytest -q --junitxml=/reports/backend-tests.xml || test_exit_code=\$? ; exit \${test_exit_code:-0}\
                              "
                            
                            # Cleanup Postgres and network
                            docker rm -f ci-postgres || true
                            docker network rm ci-network || true
                            '''
                        },
                        
                        // 2. FRONTEND TESTS (Junit XML generation)
                        frontend_tests: {
                            sh '''
                            # Frontend tests (runs in Node container). Expect frontend tests to emit JUnit XML to /reports/frontend-tests.xml.
                            docker run --rm -v "${WORKSPACE}/frontend":/app -w /app node:18-alpine sh -lc "\
                              if [ -f package.json ]; then \
                                npm ci --silent && \
                                # Example: run tests and write JUnit with jest-junit if configured
                                (npm test -- --ci --reporters=default --reporters=jest-junit 2>/dev/null || true); \
                              else echo 'No frontend package.json, skipping frontend tests'; fi"
                            # Copy any generated report into workspace (jest-junit default: junit.xml)
                            if [ -f frontend/junit.xml ]; then mv frontend/junit.xml reports/frontend-tests.xml; fi
                            '''
                        },
                        
                        // 3. API INTEGRATION (Postman/Newman)
                        api_integration_tests: {
                            sh '''
                            # API integration tests using Newman (Postman) example.
                            # We assume the collection file is named 'collection.json' and environment 'env.json'.
                            if [ -d "${WORKSPACE}/postman" ]; then
                              docker run --rm -v "${WORKSPACE}/postman":/etc/newman postman/newman:alpine \
                                run "collection.json" --environment "env.json" \
                                --reporters junit --reporter-junit-export /etc/newman/api-integration-tests.xml || true
                              
                              # Newman saves the output inside the mounted volume /etc/newman. We move it to the reports folder.
                              if [ -f "${WORKSPACE}/postman/api-integration-tests.xml" ]; then
                                  mv "${WORKSPACE}/postman/api-integration-tests.xml" "${WORKSPACE}/reports/api-integration-tests.xml"
                              fi
                            else
                              echo "No postman collection found; skipping API integration tests."
                            fi
                            '''
                        }
                    ) // end parallel
                }
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
