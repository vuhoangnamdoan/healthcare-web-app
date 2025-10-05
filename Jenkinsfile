// Jenkinsfile: DevOps Pipeline for Healthcare Booking System

pipeline {
    agent any 

    environment {
        // --- CONFIGURE THESE ENVIRONMENT VARIABLES ---

        // Docker registry (e.g., your Docker Hub username)
        DOCKER_REGISTRY = 'vuhoangnamdoan' 

        // Staging/Test Server SSH details
        STAGING_SERVER = '172.26.108.190' 

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

        stage('Security (Bandit SAST)') {
            steps {
                script {
                    def containerName = "bandit-scan-${env.BUILD_NUMBER}"
                    sh 'mkdir -p reports'
                    echo 'Starting Static Analysis (SAST) with Bandit...'
        
                    sh """ 
                    # 1. Run container in detached mode (-d)
                    docker run -d --name ${containerName} \
                        --entrypoint /bin/sh \
                        -v "${WORKSPACE}":/app \
                        -w /app \\
                        ${DOCKER_REGISTRY}/booking-backend:${BUILD_ID} \
                        -c "
                            # Install Bandit 
                            pip install --no-cache-dir bandit 
                            
                            # Run Bandit scan and output to /tmp/reports inside container
                            mkdir -p /tmp/reports
                            bandit -r . -f json -o /tmp/reports/bandit-report.json --exit-zero
                            bandit -r . -f html -o /tmp/reports/bandit-report.html --exit-zero
                        "
                    
                    # 2. Wait for the container process to complete
                    docker wait ${containerName}
                    
                    # 3. Copy reports back to the host workspace
                    docker cp ${containerName}:/tmp/reports/bandit-report.json ./reports/
                    docker cp ${containerName}:/tmp/reports/bandit-report.html ./reports/
                    
                    # 4. Remove the container
                    docker rm ${containerName}
                    """
                    
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
                    
                    // 4. Parse the JSON report
                    if (fileExists('reports/bandit-report.json')) {
                        def jsonReport = readJSON file: 'reports/bandit-report.json'
                        def issueCount = jsonReport.results.size()
                        def highIssues = jsonReport.results.findAll { it.severity == 'HIGH' }
        
                        if (issueCount > 0) {
                            echo "Bandit found ${issueCount} potential security issue(s), including ${highIssues.size()} HIGH severity issues. Review the HTML report for details."
                        } else {
                            echo "Bandit scan completed successfully with no issues found."
                        }
                    } else {
                        echo "Bandit JSON report not found. The scan may have failed or the 'bandit-report.json' file could not be created."
                    }
                }
            }
        }

        // 5. DEPLOY STAGE: Deploy to Staging (Test) Environment
        stage('Deploy to Staging (Docker Compose)') {
            steps {
                echo 'Deploying to Staging Environment using Docker Compose on test server...'
                
                withCredentials([sshUserPrivateKey(credentialsId: 'ssh-creds-staging', keyFileVariable: 'KEY_FILE', usernameVariable: 'USER')]) {
                    
                    // 1. Copy required files
                    // 🚨 CHANGED: Copy 'staging.env' which you created.
                    sh "scp -i ${KEY_FILE} docker-compose.yml staging.env ${USER}@${STAGING_SERVER}:/opt/staging/"
                    
                    // 2. SSH into the server and perform the deployment
                    sh """
                    ssh -i ${KEY_FILE} ${USER}@${STAGING_SERVER} '
                        cd /opt/staging
                        
                        # Use the -f flag to point docker-compose to the environment file
                        docker-compose -f docker-compose.yml --env-file staging.env pull
                        
                        docker-compose -f docker-compose.yml --env-file staging.env up -d --remove-orphans
                    '
                    """
                }
                echo 'Staging deployment complete. Run acceptance tests now.'
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
    }
}
