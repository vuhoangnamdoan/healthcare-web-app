from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, datetime, date

from .models import Appointment, AvailabilitySlot
from .serializers import AppointmentSerializer, AppointmentDetailSerializer, AvailabilitySlotSerializer
from users.permissions import IsAdmin, IsDoctor, IsPatient, IsAppointmentParticipant
from users.models import User, DoctorProfile, PatientProfile
from notifications.models import Notification
from notifications.utils import create_appointment_notification, schedule_appointment_reminders


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments.
    
    Implements complete CRUD operations with role-based permissions:
    - Patients can create appointments and see/update their own appointments
    - Doctors can see and update their own appointments
    - Admins can see and manage all appointments
    
    Additional actions:
    - cancel: Cancel an appointment
    - confirm: Confirm a scheduled appointment
    - complete: Mark an appointment as completed
    - reschedule: Reschedule an existing appointment
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reason', 'notes', 'doctor__first_name', 'doctor__last_name', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['date', 'start_time', 'status', 'created_at']
    ordering = ['date', 'start_time']
    
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
        queryset = Appointment.objects.all()
        
        # Apply filters if provided
        status_filter = self.request.query_params.get('status', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
                
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        # Role-based filtering
        if user.role == 'admin' or user.is_superuser:
            return queryset
        
        if user.role == 'patient':
            return queryset.filter(patient=user)
        
        if user.role == 'doctor':
            return queryset.filter(doctor=user)
        
        # Default to empty queryset
        return Appointment.objects.none()
    
    def perform_create(self, serializer):
        # If patient creates appointment, set patient as current user
        instance = None
        
        if self.request.user.role == 'patient':
            instance = serializer.save(patient=self.request.user)
        else:
            instance = serializer.save()
            
        # Create notification for new appointment
        if instance:
            # Create notification
            create_appointment_notification(instance, 'created')
            
            # Schedule reminder if appointment is in the future
            schedule_appointment_reminders(instance)
    
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
        
        # Create cancellation notification
        create_appointment_notification(appointment, 'cancelled')
        
        return Response({'detail': 'Appointment cancelled successfully.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor | IsAdmin])
    def confirm(self, request, pk=None):
        """Confirm an appointment (doctors & admins only)"""
        appointment = self.get_object()
        
        if appointment.status != 'scheduled':
            return Response(
                {'detail': 'Only scheduled appointments can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        appointment.status = 'confirmed'
        appointment.confirmation_timestamp = timezone.now()
        appointment.save()
        
        # Create confirmation notification
        create_appointment_notification(appointment, 'confirmed')
        
        return Response({'detail': 'Appointment confirmed.'})
    
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
        
        # Create completion notification
        create_appointment_notification(appointment, 'completed')
        
        return Response({'detail': 'Appointment marked as completed.'})
        
    @action(detail=True, methods=['post'], permission_classes=[IsAppointmentParticipant])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment to a new time"""
        appointment = self.get_object()
        
        if appointment.status in ['completed', 'cancelled']:
            return Response(
                {'detail': f'Cannot reschedule a {appointment.status} appointment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate new time slot
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update appointment
        for key, value in serializer.validated_data.items():
            setattr(appointment, key, value)
            
        appointment.save()
        
        # Create reschedule notification
        create_appointment_notification(appointment, 'rescheduled')
        
        # Update reminder if the appointment date changed
        if 'date' in serializer.validated_data:
            # Schedule new reminder
            schedule_appointment_reminders(appointment)
        
        return Response({'detail': 'Appointment rescheduled successfully.'})
        
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments for the authenticated user"""
        user = request.user
        today = date.today()
        
        if user.role == 'patient':
            appointments = Appointment.objects.filter(
                patient=user,
                date__gte=today,
                status__in=['scheduled', 'confirmed']
            ).order_by('date', 'start_time')
        elif user.role == 'doctor':
            appointments = Appointment.objects.filter(
                doctor=user,
                date__gte=today,
                status__in=['scheduled', 'confirmed']
            ).order_by('date', 'start_time')
        else:
            # For admins, show all upcoming appointments
            appointments = Appointment.objects.filter(
                date__gte=today,
                status__in=['scheduled', 'confirmed']
            ).order_by('date', 'start_time')
        
        page = self.paginate_queryset(appointments)
        if page is not None:
            serializer = AppointmentDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = AppointmentDetailSerializer(appointments, many=True)
        return Response(serializer.data)

# Keep the rest of the AvailabilitySlotViewSet unchanged
class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor availability slots.
    - Doctors can manage their own availability slots
    - Admin can manage all availability slots
    - Patients can only view availability slots
    """
    serializer_class = AvailabilitySlotSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
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
        
        # Get query parameters
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        doctor_id = self.request.query_params.get('doctor_id', None)
        
        queryset = AvailabilitySlot.objects.all()
        
        # Apply date range filters if provided
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
                
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        # Filter by doctor_id if provided
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # If doctor, show only their slots
        if user.role == 'doctor':
            try:
                doctor_profile = DoctorProfile.objects.get(user=user)
                return queryset.filter(doctor_id=doctor_profile.doctor_id)
            except DoctorProfile.DoesNotExist:
                return AvailabilitySlot.objects.none()
        
        # For patients and admins, show all available slots
        if user.role == 'patient':
            return queryset.filter(is_available=True)
        
        # For admins, show all slots
        return queryset
    
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
        date_param = request.query_params.get('date', None)
        if date_param:
            queryset = queryset.filter(date=date_param)
        
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
        
    @action(detail=False, methods=['post'], permission_classes=[IsDoctor])
    def bulk_create(self, request):
        """
        Create multiple availability slots at once.
        Useful for setting up recurring availability.
        """
        # Get the doctor ID
        doctor_profile = DoctorProfile.objects.get(user=request.user)
        doctor_id = doctor_profile.doctor_id
        
        # Get the recurring pattern data
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        days = request.data.get('days', [])  # List of weekdays (0=Monday, 6=Sunday)
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        # Validate required data
        if not all([start_date, end_date, days, start_time, end_time]):
            return Response(
                {'detail': 'Missing required fields for recurring availability.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convert string dates to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Create slots for each day in the date range
            created_slots = []
            current_date = start_date
            
            while current_date <= end_date:
                # Check if the current weekday is in the selected days
                if current_date.weekday() in days:
                    slot = AvailabilitySlot(
                        doctor_id=doctor_id,
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True,
                        week_day=current_date.weekday()
                    )
                    created_slots.append(slot)
                
                # Move to the next day
                current_date += timedelta(days=1)
            
            # Bulk create the availability slots
            AvailabilitySlot.objects.bulk_create(created_slots)
            
            return Response({
                'detail': f'Successfully created {len(created_slots)} availability slots.',
                'count': len(created_slots)
            })
            
        except ValueError as e:
            return Response(
                {'detail': f'Invalid date or time format: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
