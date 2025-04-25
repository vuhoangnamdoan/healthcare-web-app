from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import views as needed when we implement them
# from .views import NotificationViewSet

# Create a router and register our viewsets
router = DefaultRouter()
# router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]