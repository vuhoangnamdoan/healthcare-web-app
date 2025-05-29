from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Doctor appointment slot management
    path('slots/', views.AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('slots/<uuid:appointment_id>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('my-schedule/', views.DoctorScheduleView.as_view(), name='doctor-schedule'),
    
    # Patient appointment view
    path('available/', views.AvailableAppointmentListView.as_view(), name='available-appointments'),
    path('available/<uuid:appointment_id>/', views.AvailableAppointmentDetailView.as_view(), name='available-appointment-detail'),
    
    # Booking management
    path('bookings/', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<uuid:booking_id>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<uuid:booking_id>/cancel/', views.BookingCancelView.as_view(), name='booking-cancel'),
    
    # Role-based views
    path('my-appointments/', views.MyAppointmentsView.as_view(), name='my-appointments'),
    path('my-bookings/', views.MyBookingsView.as_view(), name='my-bookings'),
    
    # Doctor availability management
    path('availability/', views.DoctorAvailabilityView.as_view(), name='doctor-availability'),
]