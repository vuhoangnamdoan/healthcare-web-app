from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create separate routers for each viewset to avoid routing conflicts
appointment_router = DefaultRouter()
availability_router = DefaultRouter()

# Register viewsets with their respective routers
appointment_router.register('', views.AppointmentViewSet, basename='appointments')
availability_router.register('', views.AvailabilitySlotViewSet, basename='availability')

urlpatterns = [
    path('', include(appointment_router.urls)),
    path('availability/', include(availability_router.urls)),
]