# Healthcare Appointment Booking System

A comprehensive healthcare appointment booking system built with Django REST Framework and React. The system provides role-based access for patients, doctors, and administrators with a modern web interface and cloud-ready deployment.

## 🏗️ Architecture Overview

- **Backend**: Django REST Framework with JWT authentication
- **Frontend**: React with Bootstrap UI components  
- **Database**: PostgreSQL with optimized indexes and constraints
- **Authentication**: JWT-based with role-based permissions
- **Deployment**: Kubernetes-ready with Docker containers
- **Admin Interface**: Django Admin with custom interfaces

## 📋 Core Features

### For Patients
- **User Registration & Login**: Secure account creation with role-based access
- **Profile Management**: Complete patient profiles with medical information
- **Doctor Discovery**: Browse doctors by specialty and availability
- **Appointment Booking**: Book available appointment slots with doctors
- **Appointment Management**: View, track, and cancel appointments
- **Search & Filter**: Find doctors by name, specialty, and working hours

### For Doctors  
- **Professional Profiles**: Detailed doctor profiles with specialties and experience
- **Schedule Management**: Configure working days and hours
- **Appointment Slots**: Create and manage available time slots
- **Patient Bookings**: View and manage patient appointments
- **Availability Control**: Enable/disable availability and slot management

### For Administrators
- **User Management**: Complete CRUD operations for all user types
- **Appointment Oversight**: Monitor all appointments and bookings
- **System Analytics**: Track usage patterns and system health
- **Role-based Access**: Granular permission control
- **Bulk Operations**: Batch operations on appointments and users

## 🛠️ Technology Stack

### Backend Technologies
- **Django 5.0+**: Web framework with ORM
- **Django REST Framework**: API development
- **PostgreSQL 15+**: Primary database with advanced features
- **JWT Authentication**: Stateless authentication
- **Django Admin**: Administrative interface
- **Python 3.11+**: Runtime environment

### Frontend Technologies
- **React 18+**: Modern UI library
- **Bootstrap 5**: Responsive CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Context API**: State management
- **React Hooks**: Modern React patterns

### DevOps & Deployment
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Nginx**: Reverse proxy and static file serving
- **MicroK8s**: Local Kubernetes development
- **Docker Compose**: Local development environment

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15+
- Docker & Docker Compose
- Kubernetes cluster (for production deployment)

### Development Setup

#### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd health-appointment-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

#### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

### Docker Development
```bash
# Start complete stack with Docker Compose
docker-compose up --build

# Access points remain the same
```

### Production Deployment (Kubernetes)

#### Manual Deployment
```bash
# Build and tag Docker images
docker build -t your-registry/healthcare-backend:latest .
cd frontend && docker build -t your-registry/healthcare-frontend:latest .

# Push to container registry
docker push your-registry/healthcare-backend:latest
docker push your-registry/healthcare-frontend:latest

# Deploy to Kubernetes (in order)
kubectl apply -f k8s/postgres-secrets.yaml
kubectl apply -f k8s/django-secrets.yaml
kubectl apply -f k8s/persistent-volumes.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

#### Automated Deployment (MicroK8s)
```bash
# Use the provided deployment script
chmod +x deploy-to-microk8s.sh
./deploy-to-microk8s.sh
```

## 📊 Database Schema

### User Management
- **Users**: Custom user model with role-based access (Patient/Doctor/Admin)
- **Patients**: Extended patient profiles with medical information
- **Doctors**: Professional profiles with specialties and schedules

### Appointment System
- **Appointments**: Doctor-created time slots with availability management
- **Bookings**: Patient reservations of appointment slots
- **Constraints**: Unique constraints preventing double-booking

### Key Model Features
- **UUID Primary Keys**: Enhanced security and scalability
- **Soft Deletion**: Appointment cancellation with history preservation
- **Audit Trails**: Created/updated timestamps on all models
- **Data Validation**: Comprehensive validation rules and constraints

## 🔐 Authentication & Security

### JWT Authentication
- **Stateless**: No server-side session storage
- **Role-based**: Different access levels for users
- **Secure**: Token-based authentication with expiration

### Permission System
- **IsPatient**: Patient-only endpoints
- **IsDoctor**: Doctor-only endpoints  
- **IsSelf**: User can only access own data
- **Django Admin**: Full administrative access

### Security Features
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: ORM-based database access
- **XSS Protection**: Sanitized user inputs

## 🎨 User Interface

### Design System
- **Bootstrap 5**: Modern, responsive design
- **Consistent Styling**: Unified color scheme and typography
- **Mobile-First**: Responsive design for all devices
- **Accessibility**: WCAG compliant interface elements

### User Experience
- **Intuitive Navigation**: Clear menu structure and routing
- **Real-time Feedback**: Loading states and error handling
- **Form Validation**: Client and server-side validation
- **Progressive Enhancement**: Works without JavaScript

## 📁 Project Structure

```
health-appointment-system/
├── health_system/              # Django project settings
│   ├── settings.py            # Configuration settings
│   ├── urls.py               # Main URL routing
│   └── wsgi.py               # WSGI application
├── users/                     # User management app
│   ├── models.py             # User, Patient, Doctor models
│   ├── views.py              # Authentication views
│   ├── serializers.py        # DRF serializers
│   ├── admin.py              # Admin interfaces
│   └── permissions.py        # Custom permissions
├── appointments/              # Appointment management app
│   ├── models.py             # Appointment, Booking models
│   ├── views.py              # Appointment API views
│   ├── serializers.py        # Appointment serializers
│   ├── admin.py              # Appointment admin
│   └── urls.py               # Appointment URLs
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   │   ├── auth/         # Authentication pages
│   │   │   ├── patient/      # Patient-specific pages
│   │   │   ├── doctor/       # Doctor-specific pages
│   │   │   └── common/       # Shared pages
│   │   ├── context/          # React Context providers
│   │   └── services/         # API service layer
│   ├── public/               # Static assets
│   └── package.json          # Frontend dependencies
├── k8s/                      # Kubernetes manifests
│   ├── postgres-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   └── secrets.yaml
├── docker-compose.yml        # Local development
├── Dockerfile               # Backend container
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 API Documentation

### Authentication Endpoints
```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/logout/         # User logout
GET  /api/auth/profile/        # Get user profile
PUT  /api/auth/profile/        # Update user profile
```

### User Management
```
GET  /api/users/doctors/       # List doctors
GET  /api/users/doctors/{id}/  # Doctor details
GET  /api/users/patients/      # List patients  
GET  /api/users/patients/{id}/ # Patient details
```

### Appointment Management
```
# Doctor endpoints
GET  /api/appointments/my-appointments/     # Doctor's appointment slots
POST /api/appointments/availability/       # Create appointment slot
PUT  /api/appointments/slots/{id}/         # Update appointment slot
DELETE /api/appointments/slots/{id}/       # Delete appointment slot

# Patient endpoints  
GET  /api/appointments/available/          # Browse available slots
GET  /api/appointments/my-bookings/        # Patient's bookings
POST /api/appointments/bookings/           # Create booking
POST /api/appointments/bookings/{id}/cancel/ # Cancel booking
```

### Response Formats
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

## 🏥 Business Logic

### Appointment Slot Management
- **Doctor Schedule**: Doctors define working days and hours
- **Slot Creation**: Time slots created within working schedule
- **Availability Rules**: Slots marked available/unavailable
- **Conflict Prevention**: Unique constraints prevent scheduling conflicts

### Booking Process
- **Slot Discovery**: Patients browse available appointments
- **Booking Creation**: Reserve specific time slots
- **Validation**: Ensure slot availability and patient eligibility
- **Confirmation**: Automatic booking confirmation and updates

### Cancellation System
- **Patient Cancellation**: Patients can cancel their bookings
- **Slot Release**: Cancelled slots become available again
- **Audit Trail**: Cancellation reasons and timestamps tracked
- **Admin Override**: Administrators can manage all bookings

## 🎯 Specialties Supported

The system supports multiple medical specialties:
- **Mental Health**: Psychiatry and psychology services
- **General Medicine**: Primary care and family medicine
- **Dentistry**: Dental care and oral health
- **Physiotherapy**: Physical therapy and rehabilitation
- **Chiropractic**: Chiropractic care and treatment
- **Audiology**: Hearing and balance disorders
- **Optometry**: Eye care and vision services

## 📱 Frontend Features

### Patient Interface
- **Dashboard**: Overview of upcoming appointments
- **Doctor Browser**: Search and filter doctors
- **Appointment Booking**: Interactive slot selection
- **My Appointments**: Booking history and management
- **Profile Management**: Personal and medical information

### Doctor Interface  
- **Dashboard**: Professional overview and quick actions
- **Appointment Slots**: Manage available time slots
- **Schedule Management**: Configure working hours and days
- **Patient Bookings**: View and manage patient appointments
- **Profile Management**: Professional information and settings

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Tablet Support**: Enhanced tablet experience
- **Desktop**: Full-featured desktop interface
- **Cross-Browser**: Compatible with modern browsers

## 🔒 Admin Interface

### User Management
- **User CRUD**: Complete user lifecycle management
- **Role Assignment**: Assign and modify user roles
- **Profile Management**: Manage patient and doctor profiles
- **Bulk Operations**: Efficient batch operations

### Appointment Administration
- **Appointment Overview**: System-wide appointment monitoring
- **Booking Management**: Handle booking conflicts and issues
- **Schedule Oversight**: Monitor doctor schedules and availability
- **Analytics**: Appointment patterns and system usage

### System Configuration
- **Site Settings**: Configure system-wide settings
- **Permission Management**: Fine-grained access control
- **Data Export**: Export system data for analysis
- **Audit Logs**: Track administrative actions

## 🚀 Deployment Options

### Local Development
- **Docker Compose**: Complete local stack
- **Manual Setup**: Individual component setup
- **Hot Reload**: Development with live reloading

### Production Deployment
- **Kubernetes**: Scalable container orchestration
- **Load Balancing**: High availability configuration
- **SSL/TLS**: Secure HTTPS communication
- **Database Clustering**: PostgreSQL high availability

### Cloud Platforms
- **AWS EKS**: Amazon Kubernetes Service
- **Google GKE**: Google Kubernetes Engine  
- **Azure AKS**: Azure Kubernetes Service
- **DigitalOcean**: Managed Kubernetes

## 🔍 Monitoring & Logging

### Application Monitoring
- **Health Checks**: Kubernetes readiness/liveness probes
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Exception monitoring and alerting
- **User Analytics**: Usage patterns and behavior

### Logging Strategy
- **Structured Logging**: JSON-formatted log entries
- **Log Levels**: Debug, info, warning, error levels
- **Centralized Logs**: Aggregated logging solution
- **Log Retention**: Configurable retention policies

## 🧪 Testing Strategy

### Backend Testing
- **Unit Tests**: Model and view testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Migration and constraint testing
- **Permission Tests**: Role-based access validation

### Frontend Testing  
- **Component Tests**: React component testing
- **Integration Tests**: User flow testing
- **E2E Tests**: Complete user journey validation
- **Accessibility Tests**: WCAG compliance testing

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Strategic database indexes
- **Query Optimization**: Efficient ORM queries
- **Connection Pooling**: Database connection management
- **Caching**: Redis-based caching strategy

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Webpack optimization
- **Image Optimization**: Compressed and responsive images
- **CDN Integration**: Static asset delivery

## 🔄 Git Workflow

This project follows GitFlow branching model:

- **`master`**: Production-ready code
- **`develop`**: Integration branch for features  
- **`feature/*`**: Individual feature branches
- **`hotfix/*`**: Critical production fixes
- **`release/*`**: Release preparation branches

## 🎛️ Configuration

### Environment Variables
```bash
# Database
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend
REACT_APP_API_URL=http://localhost:8000/api
```

### Production Settings
- **Debug Mode**: Disabled in production
- **Static Files**: Served via Nginx
- **Media Files**: S3 or similar storage
- **Database**: Managed PostgreSQL service

## 🆘 Troubleshooting

### Common Issues
1. **Database Connection**: Check PostgreSQL service status
2. **JWT Token Errors**: Verify secret key configuration
3. **CORS Issues**: Configure allowed origins
4. **Migration Errors**: Run migrations in correct order

### Debug Mode
```bash
# Enable debug logging
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver

# Frontend debug mode
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- **Documentation**: Refer to this README
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

## 🚀 Access Information

### Local Development
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api  
- **Admin Panel**: http://localhost:8000/admin

### Production Deployment
- **Frontend**: http://healthcare.local (or your domain)
- **Admin**: http://healthcare.local/admin
- **API**: http://healthcare.local/api

### Default Test Credentials
- **Admin**: admin@hospital.com / admin123pass!
- **Doctor 1**: dr.smith@hospital.com / test123pass!
- **Doctor 2**: dr.johnson@hospital.com / test123pass!

---

*Built with ❤️ using Django REST Framework and React*
