from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('appointments', views.AppointmentViewSet, basename='appointments')
router.register('availability', views.AvailabilitySlotViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
]