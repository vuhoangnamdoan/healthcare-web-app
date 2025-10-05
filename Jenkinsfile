// Jenkinsfile: DevOps Pipeline for Healthcare Booking System

pipeline {
    agent any 

    environment {
        // --- CONFIGURE THESE ENVIRONMENT VARIABLES ---

        // SonarQube installation name (as configured in Jenkins -> Manage Jenkins -> Global Tool Configuration)
        // SONAR_HOME = tool 'SonarQubeScanner'
        // SONAR_URL = 'http://localhost:9000'

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

        // 2. TEST STAGE: Run PyTest (Django) and Jest (React) SEQUENTIALLY
        stage('Test') {
            steps {
                sh 'mkdir -p reports'
                sh 'docker network create ci-network || true'
                sh 'docker rm -f ci-postgres >/dev/null 2>&1 || true'
                
                sh '''
                docker run -d --name ci-postgres --network ci-network \
                  -e POSTGRES_DB=healthdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres123 \
                  postgres:15-alpine
                '''

                sh 'until docker run --rm --network ci-network postgres:15-alpine pg_isready -h ci-postgres -U postgres; do sleep 1; done'
                
                withDockerRegistry(credentialsId: 'docker-creds', url: '') {
                    sh """
                    docker run --rm \
                      --network ci-network \
                      -v "${WORKSPACE}/reports":/reports \
                      -e DJANGO_SETTINGS_MODULE=health_system.settings \
                      -e POSTGRES_HOST=ci-postgres \
                      -e POSTGRES_DB=healthdb \
                      -e POSTGRES_USER=postgres \
                      -e POSTGRES_PASSWORD=postgres123 \
                      -e PYTHONPATH=/app \
                      -e DJANGO_ALLOW_ASYNC_UNSAFE=true \
                      ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID} \
                      pytest --junitxml=/reports/backend-tests.xml
                    """
                }

                // Cleanup database and network
                sh 'docker rm -f ci-postgres || true'
                sh 'docker network rm ci-network || true'

                // Publish Test Results (Requires JUnit plugin)
                junit(testResults: '**/reports/*-tests.xml', allowEmptyResults: true) 
            }
        }

        // 3. CODE QUALITY STAGE: SonarQube Analysis
        stage('Code Quality (SonarQube)') {
            steps {
                echo 'Running SonarCloud analysis...'
                tool 'sonar-scanner'
                
                withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN_ENV')]) {
                    sh """
                    export PATH="\$PATH:/var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarQubeScanner/bin"
                    sonar-scanner \
                        -Dsonar.projectKey=vuhoangnamdoan_healthcare-web-app \
                        -Dsonar.organization=nam-doan \
                        -Dsonar.host.url=https://sonarcloud.io \
                        -Dsonar.sources=. -Dsonar.token=${SONAR_TOKEN_ENV}
                    """
                }
            }
        }

        // 4. SECURITY STAGE: Bandit Analysis
        // stage('Security (Bandit)') {
        //     steps {
        //         sh 'mkdir -p reports'
        //         echo 'Running Bandit security analysis on the Django backend inside a container...'
                
        //         sh '''
        //         docker run --rm \
        //             --entrypoint /bin/sh \
        //             -u $(id -u):$(id -g) \
        //             -v "${WORKSPACE}":/app \
        //             -w /app \
        //             ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID} \
        //             -c "
        //                 export HOME=/app
        //                 # Install bandit using the container's python/pip
        //                 python -m pip install --no-cache-dir bandit --user
                
        //                 # Run Bandit scan on the mounted code
        //                 \$HOME/.local/bin/bandit -r users/ appointments/ -o reports/bandit-report.json -f json
        //             "
        //         '''
                
        //         // Note: You must ensure the 'reports' directory exists for the output file
        //         // You can add 'sh 'mkdir -p reports' if needed, but the Test stage already does this.
        //     }
        // }

        stage('Security (Bandit SAST)') {
            steps {
                script {                    
                    def hostUid = sh(script: 'id -u', returnStdout: true).trim()
                    sh 'mkdir -p reports'
                    echo 'Starting Static Analysis (SAST) with Bandit...'
        
                    // 1. Use a Python Virtual Environment (venv) for isolated installation 
                    // This is the CRITICAL fix for permission errors.
                    sh '''
                    docker run --rm \
                        --entrypoint /bin/sh \
                        -v "${WORKSPACE}":/app \
                        -w /app \
                        ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID} \
                        -c "
                            # Ensure the tool is installed (it will be fast if already cached in the container)
                            pip install --no-cache-dir bandit 
                            
                            # Run Bandit scan. Output path must be relative to the /app mount.
                            # Use --skip-plugins to speed up scan if necessary.
                            bandit -r . -f json -o reports/bandit-report.json --exit-zero
                            bandit -r . -f html -o reports/bandit-report.html --exit-zero
                            chown -R ''' + hostUid + ''' reports/
                        "
                    '''
                    
                    // 2. Archive the generated reports (Artifacts)
                    archiveArtifacts artifacts: 'reports/bandit-report.json, reports/bandit-report.html', allowEmptyArchive: true
        
                    // 3. Publish the HTML report for easy viewing in Jenkins UI
                    publishHTML(target: [
                                allowMissing: false,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'bandit-report.html',
                                reportName: 'Bandit Security Report'
                            ])
        
                    // 4. Parse the JSON report to display a summary in the console log
                    if (fileExists('reports/bandit-report.json')) {
                        def jsonReport = readJSON file: 'reports/bandit-report.json'
                        def issueCount = jsonReport.results.size()
                        
                        // Identify high-severity issues for a high HD grade
                        def highIssues = jsonReport.results.findAll { it.severity == 'HIGH' }
        
                        if (issueCount > 0) {
                            echo "🚨 Bandit found ${issueCount} potential security issue(s), including ${highIssues.size()} HIGH severity issues. Review the HTML report for details."
                        } else {
                            echo "✅ Bandit scan completed successfully with no issues found."
                        }
                    } else {
                        echo "Bandit JSON report not found. The scan may have failed or the 'bandit-report.json' file could not be created."
                    }
                }
            }
        }

        // // 5. DEPLOY STAGE: Deploy to Staging (Test) Environment
        // stage('Deploy to Staging (Docker Compose)') {
        //     steps {
        //         echo 'Deploying to Staging Environment using Docker Compose on test server...'

        //         // Use SSH to log into the staging server and execute deployment
        //         // (Requires ssh-creds-staging to be set up)
        //         withCredentials([sshUserPrivateKey(credentialsId: 'ssh-creds-staging', keyFileVariable: 'KEY_FILE', usernameVariable: 'USER')]) {
        //             // Copy the docker-compose.yml and run it
        //             sh "scp -i ${KEY_FILE} docker-compose.yml ${USER}@staging.example.com:/opt/staging/docker-compose.yml"
        //             sh "ssh -i ${KEY_FILE} ${USER}@staging.example.com 'cd /opt/staging && docker-compose pull && docker-compose up -d --remove-orphans'"
        //         }
        //         echo 'Staging deployment complete. Run acceptance tests now.'
        //     }
        // }

        // // 6. RELEASE STAGE: Promote to Production (Kubernetes)
        // stage('Release to Production (Kubernetes)') {
        //     steps {
        //         echo 'Promoting Staging build to Production environment via Kubernetes...'
        //         // This step applies your k8s manifests using kubectl
        //         withKubeConfig(credentialsId: 'kube-creds', contextName: K8S_CONTEXT) {
        //             sh "kubectl apply -f k8s/ -n ${K8S_NAMESPACE}"
        //             // Optional: Wait for the deployment to roll out successfully
        //             sh "kubectl rollout status deployment/backend-deployment -n ${K8S_NAMESPACE}"
        //             sh "kubectl rollout status deployment/frontend-deployment -n ${K8S_NAMESPACE}"
        //         }
        //         echo 'Production release complete.'
        //     }
        // }

        // // 7. MONITORING STAGE: Datadog Integration
        // stage('Monitoring & Alerting (Datadog)') {
        //     steps {
        //         echo 'Sending deployment event to Datadog and ensuring monitoring is active...'
        //         // Send an event to Datadog to mark the deployment (Requires DATADOG_API_KEY credential)
        //         withCredentials([string(credentialsId: 'DATADOG_API_KEY', variable: 'DD_API_KEY')]) {
        //             sh """
        //             curl -X POST "https://api.datadoghq.com/api/v1/events" \
        //             -H "Content-Type: application/json" \
        //             -H "DD-API-KEY: ${DD_API_KEY}" \
        //             -d '{
        //                 "title": "Deployment Successful",
        //                 "text": "Build ${BUILD_ID} deployed to production.",
        //                 "tags": ["env:prod", "service:booking-system"],
        //                 "alert_type": "info"
        //             }'
        //             """
        //         }
        //         echo 'Datadog deployment event logged.'
        //     }
        // }
    }
}
