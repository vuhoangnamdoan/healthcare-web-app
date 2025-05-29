from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import Appointment, Booking
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    BookingSerializer, BookingCreateSerializer, BookingCancelSerializer,
    AvailableAppointmentSerializer, DoctorAvailabilitySerializer
)
from users.permissions import IsPatient, IsDoctor, IsSelf
from users.models import Patient


# Doctor appointment slot management
class AppointmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsDoctor]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        return Appointment.objects.filter(doctor__user=self.request.user)

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsDoctor]
    serializer_class = AppointmentSerializer
    lookup_field = 'appointment_id'
    
    def get_queryset(self):
        return Appointment.objects.filter(doctor__user=self.request.user)

# Patient appointment discovery  
class AvailableAppointmentListView(generics.ListAPIView):
    permission_classes = [IsPatient]
    serializer_class = AvailableAppointmentSerializer
    
    def get_queryset(self):
        queryset = Appointment.objects.filter(is_available=True).select_related('doctor__user').order_by('week_day', 'start_time')

        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            try:
                # Filter appointments for the specific doctor
                queryset = queryset.filter(doctor__user__user_id=doctor_id)
            except Exception as e:
                return Appointment.objects.none()

        return queryset
    
class AvailableAppointmentDetailView(generics.RetrieveAPIView):
    """View for patients to see details of available appointment slots."""
    permission_classes = [IsPatient]
    serializer_class = AvailableAppointmentSerializer
    lookup_field = 'appointment_id'
    
    def get_queryset(self):
        return Appointment.objects.filter(is_available=True)

# Booking management
class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsPatient]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            # Get the patient from the current user
            patient = Patient.objects.get(user=request.user)
            
            # Add patient to the data
            data = request.data.copy()
            data['patient'] = patient.user.user_id  # ✅ Use the Patient's User ID
            
            print(f"🔍 DEBUG: Creating booking with data: {data}")  # Debug log
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            booking = serializer.save()
            
            print(f"✅ DEBUG: Booking created: {booking.booking_id}")  # Debug log
            
            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
        except Patient.DoesNotExist:
            print(f"❌ DEBUG: Patient not found for user: {request.user.user_id}")  # Debug log
            return Response(
                {'error': 'Patient profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"❌ DEBUG: Booking creation error: {str(e)}")  # Debug log
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        return Booking.objects.filter(patient__user=self.request.user)

class BookingDetailView(generics.RetrieveAPIView):
    permission_classes = [IsPatient]
    serializer_class = BookingSerializer
    lookup_field = 'booking_id'
    
    def get_queryset(self):
        return Booking.objects.filter(patient__user=self.request.user)

class BookingCancelView(APIView):
    permission_classes = [IsPatient]
    
    def post(self, request, booking_id):
        booking = get_object_or_404(
            Booking, 
            booking_id=booking_id, 
            patient__user=request.user,
            is_canceled=False
        )
        
        serializer = BookingCancelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(booking, serializer.validated_data)
            return Response(BookingSerializer(booking).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Role-based views
class MyAppointmentsView(generics.ListAPIView):
    permission_classes = [IsDoctor]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        queryset = Appointment.objects.filter(
            doctor__user=self.request.user
        ).select_related(
            'doctor__user'
        ).order_by('week_day', 'start_time')
        
        return queryset


class MyBookingsView(generics.ListAPIView):
    permission_classes = [IsPatient]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        return Booking.objects.filter(patient__user=self.request.user)

# Doctor availability management
class DoctorScheduleView(APIView):
    permission_classes = [IsDoctor]
    
    def get(self, request):
        appointments = Appointment.objects.filter(doctor__user=request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

class DoctorAvailabilityView(APIView):
    permission_classes = [IsDoctor]
    
    def post(self, request):
        serializer = DoctorAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            # Get the doctor
            try:
                doctor = request.user.doctor
            except Exception as e:
                return Response(
                    {"detail": "Doctor profile not found."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract validated data
            week_day = serializer.validated_data['week_day']
            start_time = serializer.validated_data['start_time']
            duration = serializer.validated_data.get('duration', 60)
            
            try:
                appointment = Appointment.objects.create(
                    doctor=doctor,
                    week_day=week_day,
                    start_time=start_time,
                    duration=duration,
                    is_available=True
                )
                # Return created appointment
                response_data = AppointmentSerializer(appointment).data
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {"detail": f"Failed to create appointment: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)