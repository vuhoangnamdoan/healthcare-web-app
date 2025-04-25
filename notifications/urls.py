from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('notifications', views.NotificationViewSet, basename='notifications')
router.register('templates', views.NotificationTemplateViewSet, basename='notification-templates')
router.register('reminders', views.AppointmentReminderViewSet, basename='appointment-reminders')

urlpatterns = [
    path('', include(router.urls)),
]