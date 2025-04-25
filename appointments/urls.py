from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, AvailabilitySlotViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'availability', AvailabilitySlotViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
]