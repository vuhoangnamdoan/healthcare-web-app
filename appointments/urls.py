from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'appointments'

router = DefaultRouter()
# These will be added when we implement the views
# router.register(r'appointments', views.AppointmentViewSet)
# router.register(r'availability', views.AvailabilityViewSet)
# router.register(r'medical-records', views.MedicalRecordViewSet)

urlpatterns = [
    path('book/', views.BookAppointmentView.as_view(), name='book'),
    path('cancel/<int:pk>/', views.CancelAppointmentView.as_view(), name='cancel'),
    path('confirm/<int:pk>/', views.ConfirmAppointmentView.as_view(), name='confirm'),
    path('complete/<int:pk>/', views.CompleteAppointmentView.as_view(), name='complete'),
    path('availability/doctor/<int:doctor_id>/', views.DoctorAvailabilityView.as_view(), name='doctor-availability'),
    path('medical-record/<int:appointment_id>/', views.MedicalRecordView.as_view(), name='medical-record'),
]

urlpatterns += router.urls