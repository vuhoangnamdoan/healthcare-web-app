from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import Notification, NotificationTemplate, AppointmentReminder
from .serializers import NotificationSerializer, NotificationTemplateSerializer, AppointmentReminderSerializer
from users.permissions import IsAdmin, IsDoctor, IsPatient
from appointments.models import Appointment


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications
    """
    serializer_class = NotificationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter notifications to only show notifications for the current user.
        Admin users can see all notifications with special query parameters.
        """
        user = self.request.user
        
        # Retrieve query parameters
        notification_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        user_id = self.request.query_params.get('user_id')  # For admin use
        
        # Default query filters to user's own notifications
        queryset = Notification.objects.filter(recipient=user)
        
        # Apply filters based on query parameters
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
            
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Admin can filter by user_id
        if user.role == 'admin' and user_id:
            queryset = Notification.objects.filter(recipient_id=user_id)
        
        return queryset
    
    def get_permissions(self):
        """Define custom permissions"""
        if self.action in ['destroy', 'create']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        
        # Ensure the user is the recipient of the notification
        if notification.recipient != request.user and not request.user.role == 'admin':
            return Response(
                {"detail": "You do not have permission to mark this notification as read."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for the current user"""
        notifications = Notification.objects.filter(
            recipient=request.user, 
            status='unread'
        )
        
        now = timezone.now()
        count = notifications.count()
        
        # Update all notifications with a single query
        notifications.update(status='read', read_at=now)
        
        return Response({
            "detail": f"Marked {count} notifications as read.",
            "count": count
        })


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification templates
    Only accessible to admin users
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['template_type', 'title', 'content']


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointment reminders
    """
    serializer_class = AppointmentReminderSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['scheduled_time']
    ordering = ['scheduled_time']
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all reminders
        if user.role == 'admin':
            queryset = AppointmentReminder.objects.all()
        else:
            # Other users can only see their own reminders
            queryset = AppointmentReminder.objects.filter(recipient=user)
        
        # Filter by appointment ID if provided
        appointment_id = self.request.query_params.get('appointment_id')
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)
            
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_permissions(self):
        """Define custom permissions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsDoctor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def create_appointment_reminders(self, request):
        """
        Create appointment reminders automatically based on appointment dates
        This can be called by a scheduled task or manually by admins
        """
        if not (request.user.role == 'admin' or request.user.role == 'doctor'):
            return Response(
                {"detail": "Only admins and doctors can create appointment reminders."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days_ahead = int(request.data.get('days_ahead', 1))
        reminder_date = timezone.now().date() + timedelta(days=days_ahead)
        
        # Get appointments scheduled for the target date
        appointments = Appointment.objects.filter(
            date=reminder_date,
            status__in=['scheduled', 'confirmed']
        )
        
        reminders_created = 0
        
        # Create reminders for each appointment
        for appointment in appointments:
            # Check if reminder already exists
            existing_reminder = AppointmentReminder.objects.filter(
                appointment_id=appointment.appointment_id,
                recipient=appointment.patient,
                status='pending'
            ).exists()
            
            if not existing_reminder:
                # Create reminder for patient
                try:
                    # Get the reminder template
                    template = NotificationTemplate.objects.get(template_type='appointment_reminder')
                    message = template.content.format(
                        patient_name=f"{appointment.patient.first_name} {appointment.patient.last_name}",
                        doctor_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                        date=appointment.date.strftime("%B %d, %Y"),
                        time=appointment.start_time.strftime("%I:%M %p")
                    )
                except (NotificationTemplate.DoesNotExist, KeyError):
                    # Fallback message if template doesn't exist
                    message = (
                        f"Reminder: You have an appointment with Dr. {appointment.doctor.last_name} "
                        f"on {appointment.date} at {appointment.start_time.strftime('%I:%M %p')}."
                    )
                
                # Calculate the reminder time (typically morning of the appointment)
                reminder_time = datetime.combine(
                    appointment.date, 
                    datetime.strptime("08:00", "%H:%M").time()
                )
                
                # Create the reminder
                AppointmentReminder.objects.create(
                    appointment_id=appointment.appointment_id,
                    recipient=appointment.patient,
                    scheduled_time=reminder_time,
                    message=message
                )
                
                reminders_created += 1
        
        return Response({
            "detail": f"Created {reminders_created} appointment reminders for {reminder_date}.",
            "count": reminders_created
        })
    
    @action(detail=False, methods=['post'])
    def send_due_reminders(self, request):
        """
        Send reminders that are due to be sent.
        This would typically be called by a scheduled task,
        but can be manually triggered by admins.
        """
        if not request.user.role == 'admin':
            return Response(
                {"detail": "Only admins can manually trigger sending reminders."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get pending reminders that are due to be sent
        now = timezone.now()
        due_reminders = AppointmentReminder.objects.filter(
            status='pending',
            scheduled_time__lte=now
        )
        
        reminders_sent = 0
        
        # Process each reminder
        for reminder in due_reminders:
            # Create a notification for the reminder
            Notification.objects.create(
                recipient=reminder.recipient,
                title="Appointment Reminder",
                message=reminder.message,
                notification_type="reminder",
                appointment_id=reminder.appointment_id
            )
            
            # Mark the reminder as sent
            reminder.mark_as_sent()
            reminders_sent += 1
        
        return Response({
            "detail": f"Sent {reminders_sent} appointment reminders.",
            "count": reminders_sent
        })
