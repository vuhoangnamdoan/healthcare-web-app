from django.db import models
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Appointment(models.Model):
    """Model for medical appointments between patients and doctors."""
    
    # Status choices for appointment
    PENDING = 'pending'
    SCHEDULED = 'scheduled'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'
    RESCHEDULED = 'rescheduled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (SCHEDULED, _('Scheduled')),
        (CONFIRMED, _('Confirmed')),
        (CANCELLED, _('Cancelled')),
        (COMPLETED, _('Completed')),
        (NO_SHOW, _('No Show')),
        (RESCHEDULED, _('Rescheduled')),
    ]
    
    # Foreign keys will be imported at runtime to avoid circular imports
    patient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_id = models.CharField(max_length=50, unique=True, editable=False)
    
    # Appointment schedule details
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    
    # Appointment details with encryption for sensitive information
    reason = encrypt(models.TextField())
    notes = encrypt(models.TextField(blank=True))
    
    # Appointment status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=SCHEDULED)
    
    # Appointment metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_reason = models.TextField(blank=True)
    confirmation_timestamp = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['date', 'doctor']),
            models.Index(fields=['date', 'patient']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        # Check if this is a new appointment or status is changed
        is_new = not self.pk
        
        if is_new:
            self.appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        else:
            # Get the previous state from the database
            try:
                old_instance = Appointment.objects.get(pk=self.pk)
                old_status = old_instance.status
                status_changed = old_status != self.status
                date_changed = old_instance.date != self.date
            except Appointment.DoesNotExist:
                status_changed = False
                date_changed = False
                
        # Save the appointment first
        super().save(*args, **kwargs)
        
        # Handle automated actions after save
        if is_new or (status_changed or date_changed):
            self._handle_reminders()
    
    def _handle_reminders(self):
        """
        Handle reminder creation or cancellation based on appointment status
        """
        try:
            from notifications.utils import cancel_reminder
            from notifications.models import AppointmentReminder, NotificationTemplate, Notification
            from datetime import datetime, timedelta
            
            # If appointment is cancelled, remove any pending reminders
            if self.status == self.CANCELLED:
                cancel_reminder(self.appointment_id)
                return
                
            # For scheduled and confirmed appointments, create reminders if needed
            if self.status in [self.SCHEDULED, self.CONFIRMED]:
                # Check if the appointment date is within the reminder window (e.g., next 7 days)
                today = timezone.now().date()
                days_until_appointment = (self.date - today).days
                
                if 0 <= days_until_appointment <= 7:
                    # Check if a reminder already exists
                    existing_reminder = AppointmentReminder.objects.filter(
                        appointment_id=self.appointment_id,
                        status='pending'
                    ).exists()
                    
                    if not existing_reminder:
                        # Create reminder messages
                        try:
                            template = NotificationTemplate.objects.get(template_type='appointment_reminder')
                            patient_message = template.content.format(
                                patient_name=f"{self.patient.first_name} {self.patient.last_name}",
                                doctor_name=f"{self.doctor.first_name} {self.doctor.last_name}",
                                date=self.date.strftime("%B %d, %Y"),
                                time=self.start_time.strftime("%I:%M %p"),
                                location="Online",
                                duration=f"{self.duration_minutes} minutes"
                            )
                        except (NotificationTemplate.DoesNotExist, KeyError):
                            patient_message = (
                                f"Reminder: You have an appointment with Dr. {self.doctor.last_name} "
                                f"on {self.date.strftime('%B %d, %Y')} at {self.start_time.strftime('%I:%M %p')}. "
                                f"Please be on time."
                            )
                            
                        # Create reminder time for 8 AM on appointment day
                        reminder_time = datetime.combine(
                            self.date, 
                            datetime.strptime("08:00", "%H:%M").time()
                        )
                        reminder_time = timezone.make_aware(reminder_time)
                        
                        # Create reminder for patient
                        AppointmentReminder.objects.create(
                            appointment_id=self.appointment_id,
                            recipient=self.patient,
                            scheduled_time=reminder_time,
                            message=patient_message,
                            status='pending'
                        )
                        
                        # Create reminder for doctor
                        doctor_message = (
                            f"Reminder: You have an appointment with {self.patient.first_name} "
                            f"{self.patient.last_name} scheduled for {self.date.strftime('%B %d, %Y')} "
                            f"at {self.start_time.strftime('%I:%M %p')}."
                        )
                        
                        AppointmentReminder.objects.create(
                            appointment_id=self.appointment_id,
                            recipient=self.doctor,
                            scheduled_time=reminder_time,
                            message=doctor_message,
                            status='pending'
                        )
                        
        except ImportError:
            # If notifications app isn't available, just continue
            pass
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.date} {self.start_time}"
    
    def clean(self):
        """Validate appointment time range and availability."""
        if self.start_time >= self.end_time:
            raise ValidationError(_("End time must be after start time"))
        
        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            status__in=[self.SCHEDULED, self.CONFIRMED],
        ).exclude(pk=self.pk)
        
        for appointment in overlapping_appointments:
            if (
                (self.start_time <= appointment.start_time < self.end_time) or
                (appointment.start_time <= self.start_time < appointment.end_time)
            ):
                raise ValidationError(_("This time slot conflicts with another appointment"))
    
    def is_pending(self):
        return self.status == self.PENDING
        
    def is_scheduled(self):
        return self.status == self.SCHEDULED
    
    def is_confirmed(self):
        return self.status == self.CONFIRMED
    
    def is_cancelled(self):
        return self.status == self.CANCELLED
    
    def is_completed(self):
        return self.status == self.COMPLETED
    
    def is_no_show(self):
        return self.status == self.NO_SHOW
    
    def is_rescheduled(self):
        return self.status == self.RESCHEDULED


class AvailabilitySlot(models.Model):
    """Model to track doctor availability for appointments."""
    
    doctor_id = models.CharField(max_length=50)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    week_day = models.PositiveSmallIntegerField(choices=[
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ], null=True, blank=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor_id', 'date', 'start_time', 'end_time']
        indexes = [
            models.Index(fields=['doctor_id', 'date']),
            models.Index(fields=['is_available']),
            models.Index(fields=['week_day']),
        ]
    
    def __str__(self):
        return f"Doctor {self.doctor_id} - {self.date} {self.start_time}-{self.end_time}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("End time must be after start time"))
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
