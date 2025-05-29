from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


class Appointment(models.Model):
    """Model for medical appointment slots created by doctors."""
    
    # Days of the week choices
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]
    
    appointment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey('users.Doctor', on_delete=models.CASCADE, related_name='appointments')
    week_day = models.IntegerField(choices=DAYS_OF_WEEK, help_text="Day of the week (1=Monday, 7=Sunday)")
    start_time = models.TimeField(help_text="Start time of the appointment slot")
    duration = models.IntegerField(default=60, help_text="Duration in minutes")
    is_available = models.BooleanField(default=True, help_text="Whether this slot is available for booking")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(week_day__gte=1) & models.Q(week_day__lte=7),
                name='valid_week_day'
            ),
            models.UniqueConstraint(
                fields=['doctor', 'week_day', 'start_time'],
                name='unique_doctor_time_slot'
            )
        ]
        ordering = ['week_day', 'start_time']
    
    def __str__(self):
        return f"Dr. {self.doctor.user.first_name} {self.doctor.user.last_name} - {self.get_week_day_display()} at {self.start_time}"
    
    def get_end_time(self):
        """Calculate end time based on start time and duration."""
        if not self.start_time:
            return None 
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = start_datetime + timedelta(minutes=self.duration)
        return end_datetime.time()
    
    def is_slot_available(self):
        """Check if this appointment slot is available for booking."""
        return self.is_available and not self.bookings.filter(is_canceled=False).exists()
    
    def mark_as_booked(self):
        """Mark this appointment slot as unavailable."""
        self.is_available = False
        self.save(update_fields=['is_available', 'updated_at'])
    
    def mark_as_available(self):
        """Mark this appointment slot as available."""
        self.is_available = True
        self.save(update_fields=['is_available', 'updated_at'])
    
    def clean(self):
        """Validate appointment data."""
        super().clean()
        
        # Validate that appointment is within doctor's working hours
        if hasattr(self, 'doctor') and self.doctor:
            working_days = [int(day.strip()) for day in self.doctor.working_day.split(',') if day.strip()]
            if self.week_day not in working_days:
                raise ValidationError(
                    f"Doctor is not available on {self.get_week_day_display()}. "
                    f"Working days: {self.doctor.get_working_days_display()}"
                )
            
            if not (self.doctor.from_time <= self.start_time < self.doctor.to_time):
                raise ValidationError(
                    f"Appointment time must be within doctor's working hours "
                    f"({self.doctor.from_time} - {self.doctor.to_time})"
                )


class Booking(models.Model):
    """Model for patient bookings of appointment slots."""
    
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='bookings')
    patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE, related_name='bookings')
    reason = models.TextField(blank=True, null=True, help_text="Reason for the appointment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_canceled = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['appointment'],
                condition=models.Q(is_canceled=False),
                name='unique_active_booking_per_appointment'
            ),
            models.UniqueConstraint(
                fields=['appointment', 'patient'],
                condition=models.Q(is_canceled=False),
                name='unique_patient_appointment'
            )
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Canceled" if self.is_canceled else "Active"
        return (f"Booking {self.booking_id} - "
                f"Dr. {self.appointment.doctor.user.first_name} {self.appointment.doctor.user.last_name} - "
                f"{self.appointment.get_week_day_display()} at {self.appointment.start_time} - "
                f"Patient: {self.patient.user.first_name} {self.patient.user.last_name} - "
                f"Status: {status}")
    
    def clean(self):
        super().clean()
        if not self.appointment.is_slot_available() and not self.pk:
            raise ValidationError("This appointment slot is no longer available.")
        
        if not self.pk:
            existing_booking = Booking.objects.filter(
                appointment=self.appointment,
                appointment__week_day=self.appointment.week_day,
                appointment__start_time=self.appointment.start_time,
                is_canceled=False
            ).first()
            
            if existing_booking:
                raise ValidationError(
                    f"This appointment slot is already booked by {existing_booking.patient.user.get_full_name()}."
                )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        was_canceled = False
        if not is_new and self.pk:
            try:
                old_booking = Booking.objects.get(pk=self.pk)
                was_canceled = not old_booking.is_canceled and self.is_canceled
            except Booking.DoesNotExist:
                was_canceled = False
        if self.is_canceled and not self.canceled_at:
            self.canceled_at = timezone.now()
        elif not self.is_canceled:
            self.canceled_at = None
        
        super().save(*args, **kwargs)

        self.update_appointment_availability()
    
    def update_appointment_availability(self):
        active_bookings = self.appointment.bookings.filter(is_canceled=False).count()

        if active_bookings > 0:
            if self.appointment.is_available:
                self.appointment.mark_as_booked()
        else:
            if not self.appointment.is_available:
                self.appointment.mark_as_available()
    
    def cancel_booking(self, reason=None):
        self.is_canceled = True
        self.canceled_at = timezone.now()
        if reason:
            self.cancellation_reason = reason
        self.save()
