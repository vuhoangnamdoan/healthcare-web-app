# Healthcare Appointment Booking System

A modern healthcare appointment booking system built with Django REST API and React.

## Architecture
- **Backend**: Django REST Framework with JWT authentication
- **Frontend**: React with Bootstrap UI
- **Database**: PostgreSQL
- **Deployment**: Kubernetes with Docker containers

## Git Workflow

This project follows the GitFlow branching model:

- `master`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches (e.g., feature/user-authentication)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- Kubernetes cluster (for production)

### Development
```bash
# Backend
pip install -r requirements.txt
python manage.py migrate
python manage.py create_doctors
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
npm start
```

### Local Testing with Docker
```bash
# Test full stack locally
docker-compose up --build
```

### Production (Kubernetes)
```bash
# Build and push images
docker build -t your-registry/healthcare-backend:latest .
cd frontend && docker build -t your-registry/healthcare-frontend:latest .
docker push your-registry/healthcare-backend:latest
docker push your-registry/healthcare-frontend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/postgres-secrets.yaml
kubectl apply -f k8s/django-secrets.yaml
kubectl apply -f k8s/django_config.yaml
kubectl apply -f k8s/persistent-volumes.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

## Features
- Patient registration and appointment booking
- Doctor appointment slot management
- JWT authentication with role-based access
- Responsive web interface
- Kubernetes-ready deployment
- Auto-created initial doctors for demo

## Default Credentials
- **Admin**: admin@hospital.com / admin123pass!
- **Doctor 1**: dr.smith@hospital.com / test123pass!
- **Doctor 2**: dr.johnson@hospital.com / test123pass!

## Access After Deployment
- Frontend: http://healthcare.local (or your domain)
- Admin: http://healthcare.local/admin
- API: http://healthcare.local/api