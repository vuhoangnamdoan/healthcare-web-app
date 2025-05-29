from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PatientRegisterView, LoginView, MyProfileView, UpdateProfileView,
    ChangePasswordView, LogoutView, DoctorListView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', PatientRegisterView.as_view(), name='patient-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management endpoints
    path('profile/', MyProfileView.as_view(), name='my-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    
    # Doctor discovery for patients
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),

    # path('doctors/specialities/', DoctorSpecialitiesView.as_view(), name='doctor-specialities'),
]