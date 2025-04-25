from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, UserProfileView, ChangePasswordView,
    DoctorRegistrationView, PatientProfileViewSet, DoctorProfileViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'patients', PatientProfileViewSet, basename='patient')
router.register(r'doctors', DoctorProfileViewSet, basename='doctor')

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Admin-only doctor registration
    path('register-doctor/', DoctorRegistrationView.as_view(), name='register-doctor'),
    
    # Include router URLs
    path('', include(router.urls)),
]