from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
# These will be added when we implement the views
# router.register(r'patients', views.PatientViewSet)
# router.register(r'doctors', views.DoctorViewSet)

urlpatterns = [
    # Basic auth endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Admin-only endpoints
    path('admin/doctors/register/', views.DoctorRegistrationView.as_view(), name='doctor-register'),
]

urlpatterns += router.urls