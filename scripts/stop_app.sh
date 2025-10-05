#!/bin/bash
# Stop running services, but ignore errors if they aren't running
if docker-compose -f /opt/production/docker-compose.yml ps; then
    docker-compose -f /opt/production/docker-compose.yml down --remove-orphans
fi
