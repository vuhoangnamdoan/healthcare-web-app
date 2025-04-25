from django.db import models
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt
from django.core.exceptions import ValidationError
import uuid


class Appointment(models.Model):
    """Model for medical appointments between patients and doctors."""
    
    # Status choices for appointment
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'
    RESCHEDULED = 'rescheduled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
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
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    
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
        if not self.appointment_id:
            self.appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
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
            status__in=[self.PENDING, self.CONFIRMED],
        ).exclude(pk=self.pk)
        
        for appointment in overlapping_appointments:
            if (
                (self.start_time <= appointment.start_time < self.end_time) or
                (appointment.start_time <= self.start_time < appointment.end_time)
            ):
                raise ValidationError(_("This time slot conflicts with another appointment"))
    
    def is_pending(self):
        return self.status == self.PENDING
    
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
