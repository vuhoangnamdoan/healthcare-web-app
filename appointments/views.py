from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .models import Appointment, AvailabilitySlot
from .serializers import AppointmentSerializer, AppointmentDetailSerializer, AvailabilitySlotSerializer
from users.permissions import IsAdmin, IsDoctor, IsPatient, IsAppointmentParticipant
from users.models import User, DoctorProfile


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments.
    Permissions are based on user role:
    - Patients can create appointments and see/update their own appointments
    - Doctors can see and update their own appointments
    - Admins can see and manage all appointments
    """
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentSerializer
    
    def get_permissions(self):
        """
        Define custom permissions based on action:
        - List/retrieve: Must be a participant in the appointment or admin
        - Create: Patient or admin only
        - Update/partial update: Participant or admin
        - Delete: Admin only
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsPatient | IsAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAppointmentParticipant]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter appointments based on user role:
        - Patients see their own appointments
        - Doctors see appointments where they are the doctor
        - Admins see all appointments
        """
        user = self.request.user
        
        # Admin sees all
        if user.role == 'admin' or user.is_superuser:
            return Appointment.objects.all()
        
        # Patients see their appointments
        if user.role == 'patient':
            return Appointment.objects.filter(patient=user)
        
        # Doctors see appointments where they are the doctor
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor=user)
        
        # Default to empty queryset
        return Appointment.objects.none()
    
    def perform_create(self, serializer):
        # If patient creates appointment, set patient as current user
        if self.request.user.role == 'patient':
            serializer.save(patient=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAppointmentParticipant])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        
        if appointment.status == 'completed':
            return Response(
                {'detail': 'Cannot cancel a completed appointment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'cancelled'
        appointment.cancellation_reason = request.data.get('reason', '')
        appointment.save()
        
        return Response({'detail': 'Appointment cancelled successfully.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor | IsAdmin])
    def complete(self, request, pk=None):
        """Mark an appointment as completed (doctors & admins only)"""
        appointment = self.get_object()
        
        if appointment.status != 'confirmed':
            return Response(
                {'detail': 'Only confirmed appointments can be completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'completed'
        appointment.save()
        
        return Response({'detail': 'Appointment marked as completed.'})


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor availability slots.
    - Doctors can manage their own availability slots
    - Admin can manage all availability slots
    - Patients can only view availability slots
    """
    model = AvailabilitySlot
    serializer_class = AvailabilitySlotSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsDoctor | IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter availability slots based on user role:
        - Doctors see their own availability slots
        - Others see all available slots
        """
        user = self.request.user
        
        # If doctor, show only their slots
        if user.role == 'doctor':
            try:
                doctor_profile = DoctorProfile.objects.get(user=user)
                return AvailabilitySlot.objects.filter(doctor_id=doctor_profile.doctor_id)
            except DoctorProfile.DoesNotExist:
                return AvailabilitySlot.objects.none()
        
        # For patients and admins, show all available slots
        return AvailabilitySlot.objects.filter(is_available=True)
    
    def perform_create(self, serializer):
        """Set the doctor ID automatically if the user is a doctor"""
        if self.request.user.role == 'doctor':
            doctor_profile = DoctorProfile.objects.get(user=self.request.user)
            serializer.save(doctor_id=doctor_profile.doctor_id)
        else:
            serializer.save()
            
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get all available slots for scheduling appointments
        Filtering options: date, doctor_id
        """
        queryset = AvailabilitySlot.objects.filter(is_available=True)
        
        # Filter by date
        date = request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)
        
        # Filter by doctor_id
        doctor_id = request.query_params.get('doctor_id', None)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
