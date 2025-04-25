from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

router = DefaultRouter()
# These will be added when we implement the views
# router.register(r'notifications', views.NotificationViewSet)
# router.register(r'templates', views.NotificationTemplateViewSet)

urlpatterns = [
    path('user/', views.UserNotificationsView.as_view(), name='user-notifications'),
    path('mark-read/<int:pk>/', views.MarkNotificationReadView.as_view(), name='mark-read'),
    path('templates/', views.NotificationTemplatesView.as_view(), name='templates'),
    path('send-test/', views.SendTestNotificationView.as_view(), name='send-test'),
]

urlpatterns += router.urls