#!/bin/bash
# deploy-to-microk8s.sh
set -e

echo "🚀 Healthcare System - MicroK8s Deployment"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check MicroK8s is ready
echo "Checking MicroK8s status..."
microk8s status --wait-ready || {
    print_error "MicroK8s is not ready. Please check installation."
    exit 1
}

# Enable required add-ons
echo "Enabling required add-ons..."
microk8s enable dns storage registry ingress

echo "Waiting for add-ons to be ready..."
sleep 15

# Get registry details
echo "Setting up container registry..."
REGISTRY_PORT=$(microk8s kubectl get svc -n container-registry -o jsonpath='{.items[0].spec.ports[0].nodePort}' 2>/dev/null || echo "32000")
REGISTRY_URL="localhost:$REGISTRY_PORT"
echo "Registry URL: $REGISTRY_URL"

sleep 10
until curl -s http://$REGISTRY_URL/v2/_catalog >/dev/null 2>&1; do
    echo "Waiting for registry..."
    sleep 5
done
print_status "Registry is ready"

echo "Building Docker images..."
# Build backend image
echo "Building backend image..."
docker build -t ${REGISTRY_URL}/healthcare-backend:latest . || {
    print_error "Failed to build backend image"
    exit 1
}
# Build frontend image
echo "Building frontend image..."
cd frontend
docker build -t ${REGISTRY_URL}/healthcare-frontend:latest . || {
    print_error "Failed to build frontend image"
    exit 1
}
cd ..

# Push images to registry
echo "Pushing images to registry..."
docker push ${REGISTRY_URL}/healthcare-backend:latest || {
    print_error "Failed to push backend image"
    exit 1
}
docker push ${REGISTRY_URL}/healthcare-frontend:latest || {
    print_error "Failed to push frontend image"
    exit 1
}

# Verify images in registry
echo "Verifying images in registry..."
curl -s http://$REGISTRY_URL/v2/_catalog
print_status "Images built and pushed successfully"

# Update deployment files with correct image references
echo "Updating Kubernetes manifests..."
sed -i "s|localhost:32000/healthcare-backend:latest|${REGISTRY_URL}/healthcare-backend:latest|g" k8s/backend-deployment.yaml
sed -i "s|localhost:32000/healthcare-frontend:latest|${REGISTRY_URL}/healthcare-frontend:latest|g" k8s/frontend-deployment.yaml
echo "Updated image references:"
grep "image:" k8s/backend-deployment.yaml
grep "image:" k8s/frontend-deployment.yaml
print_status "Deployment files updated"

# Deploy secrets and configs
echo "Creating secrets and configurations..."
microk8s kubectl apply -f k8s/postgres-secrets.yaml
microk8s kubectl apply -f k8s/django-secrets.yaml
print_status "Secrets created"

# Setup storage
echo "Setting up persistent storage..."
microk8s kubectl apply -f k8s/persistent-volumes.yaml
print_status "Storage configured"

# Deploy PostgreSQL
echo "Deploying PostgreSQL database..."
microk8s kubectl apply -f k8s/postgres-deployment.yaml
echo "Waiting for PostgreSQL to be ready..."
microk8s kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s || {
    print_error "PostgreSQL failed to start"
    echo "Checking PostgreSQL logs:"
    microk8s kubectl logs -l app=postgres --tail=50
    exit 1
}
print_status "PostgreSQL is ready"

# Deploy Django Backend
echo "Deploying Django backend..."
microk8s kubectl apply -f k8s/backend-deployment.yaml
echo "Waiting for Django backend to be ready..."
microk8s kubectl wait --for=condition=ready pod -l app=django-backend --timeout=300s || {
    print_error "Django backend failed to start"
    echo "Checking Django logs:"
    microk8s kubectl logs -l app=django-backend --tail=50
    exit 1
}
print_status "Django backend is ready"

# Deploy React Frontend
echo "Deploying React frontend..."
microk8s kubectl apply -f k8s/frontend-deployment.yaml
echo "Waiting for frontend to be ready..."
microk8s kubectl wait --for=condition=ready pod -l app=react-frontend --timeout=180s || {
    print_error "React frontend failed to start"
    echo "Checking frontend logs:"
    microk8s kubectl logs -l app=react-frontend --tail=50
    exit 1
}
print_status "React frontend is ready"

# Setup Ingress
echo "Setting up ingress routing..."
microk8s kubectl apply -f k8s/ingress.yaml

echo "Configuring ingress for host network access..." # From what I faced and fix
microk8s kubectl patch daemonset nginx-ingress-microk8s-controller -n ingress -p '{"spec":{"template":{"spec":{"hostNetwork":true}}}}'
print_status "Ingress host network enabled"

# Wait for ingress to be ready
echo "Waiting for ingress to restart..."
sleep 15

# Show deployment status
echo ""
echo "Deployment Complete!"
echo "======================"
echo ""
echo "Pod Status:"
microk8s kubectl get pods
echo ""
echo "Services:"
microk8s kubectl get services
echo ""
echo "Ingress:"
microk8s kubectl get ingress
echo ""
echo "Application URLs:"
echo "Frontend: http://localhost"
echo "Admin: http://localhost/admin"
echo "API: http://localhost/api"
echo ""
echo "Default Credentials:"
echo "Admin: admin@hospital.com / admin123pass!"
echo ""
print_status "Healthcare System deployed successfully!"