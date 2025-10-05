#!/bin/bash
# Navigate to the deployment directory
cd /opt/production/

# Pull the image and start the services using the production environment file
# Note: CodeDeploy copies the production.env from the artifact
docker-compose -f docker-compose.yml --env-file production.env pull
docker-compose -f docker-compose.yml --env-file production.env up -d --remove-orphans
